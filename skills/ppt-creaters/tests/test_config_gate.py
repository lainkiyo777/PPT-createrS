import importlib.util
import json
import shutil
import unittest
import uuid
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
GATE_PATH = SKILL_ROOT / "scripts" / "config_gate.py"
TEST_TMP_ROOT = SKILL_ROOT / ".test-tmp-config-gate"


CONFIG_FIELDS = (
    "presentation_type", "visual_style", "presentation_effect", "workflow_mode",
    "output_mode", "notes_mode", "target_duration_minutes", "content_density",
)


def load_gate():
    spec = importlib.util.spec_from_file_location("config_gate", GATE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def base_config(workflow_mode="manual", selection_mode="guided"):
    return {
        "presentation_type": "technical-report",
        "visual_style": "technology-dark",
        "presentation_effect": "formal-report",
        "workflow_mode": workflow_mode,
        "selection_mode": selection_mode,
        "template_application_mode": "style-reference",
        "output_mode": "production-image",
        "notes_mode": "full",
        "target_duration_minutes": 20,
        "content_density": "medium",
        "template_profile": "references/deck-library/profiles/blue-template/style-profile.yaml",
    }


def make_candidates(output: Path) -> None:
    calls = []
    for candidate in ("candidate-a", "candidate-b", "candidate-c"):
        for name in ("cover.png", "section.png", "content.png", "result.png", "style-profile.yaml"):
            write(output / "style-candidates" / candidate / name, "candidate")
        for name in ("cover.png", "section.png", "content.png", "result.png"):
            prompt = output / "style-candidates" / candidate / "prompts" / name.replace(".png", ".txt")
            write(prompt, "prompt")
            calls.append({
                "tool_name": "image2",
                "model_or_tool_version": "test-image2-v1",
                "prompt_path": prompt.relative_to(output).as_posix(),
                "reference_images": ["blue-template.png"],
                "output_path": (output / "style-candidates" / candidate / name).relative_to(output).as_posix(),
                "timestamp": "2026-07-21T00:00:00+00:00",
                "success": True,
                "error": None,
                "status": "success",
            })
    write(output / "image-generation-manifest.json", json.dumps({"calls": calls}))


def write_confirmed(output: Path, config: dict) -> None:
    write(output / "deck-config.confirmed.yaml", json.dumps(config, ensure_ascii=False))


def write_selected(output: Path, selected_by="user") -> None:
    write(output / "selected-style.yaml", json.dumps({
        "selected_candidate": "candidate-a",
        "selected_by": selected_by,
        "confirmation_timestamp": "2026-07-21T00:00:00+00:00",
        "candidate_profile_path": "style-candidates/candidate-a/style-profile.yaml",
        "template_profile": "references/deck-library/profiles/blue-template/style-profile.yaml",
    }))


class ConfigGateTests(unittest.TestCase):
    def setUp(self):
        self.case_root = TEST_TMP_ROOT / f"{self._testMethodName}-{uuid.uuid4().hex}"
        self.output = self.case_root / "output"
        self.output.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.case_root, ignore_errors=True)

    def test_guided_without_configuration_confirmation_blocks_outline(self):
        gate = load_gate()
        result = gate.run_gate(self.output, base_config(), input_fn=iter([""]).__next__, output_fn=lambda _: None)
        self.assertEqual("awaiting_configuration", result.status)
        self.assertFalse((self.output / "outline.md").exists())
        with self.assertRaises(gate.GateBlocked):
            gate.assert_generation_allowed(self.output, "outline")

    def test_guided_without_configuration_confirmation_blocks_pptx(self):
        gate = load_gate()
        result = gate.run_gate(self.output, base_config(), input_fn=iter([""]).__next__, output_fn=lambda _: None)
        self.assertEqual("awaiting_configuration", result.status)
        self.assertFalse((self.output / "presentation.pptx").exists())
        with self.assertRaises(gate.GateBlocked):
            gate.assert_generation_allowed(self.output, "pptx")

    def test_manual_without_candidate_selection_blocks_full_deck(self):
        gate = load_gate()
        config = base_config()
        write_confirmed(self.output, config)
        make_candidates(self.output)
        result = gate.run_gate(self.output, config, input_fn=iter([""]).__next__, output_fn=lambda _: None)
        self.assertEqual("awaiting_style_selection", result.status)
        self.assertFalse((self.output / "selected-style.yaml").exists())
        with self.assertRaises(gate.GateBlocked):
            gate.assert_generation_allowed(self.output, "final-image")

    def test_missing_selected_style_cannot_continue(self):
        gate = load_gate()
        config = base_config()
        write_confirmed(self.output, config)
        make_candidates(self.output)
        with self.assertRaises(gate.GateBlocked):
            gate.assert_generation_allowed(self.output, "publish")

    def test_selected_by_ai_fails(self):
        gate = load_gate()
        config = base_config()
        write_confirmed(self.output, config)
        make_candidates(self.output)
        write_selected(self.output, selected_by="ai")
        with self.assertRaises(gate.GateBlocked):
            gate.assert_generation_allowed(self.output, "publish")

    def test_uploaded_template_does_not_skip_configuration(self):
        gate = load_gate()
        config = base_config()
        config["template_source"] = "template.pptx"
        result = gate.run_gate(self.output, config, input_fn=iter([""]).__next__, output_fn=lambda _: None)
        self.assertEqual("awaiting_configuration", result.status)
        self.assertFalse((self.output / "deck-config.confirmed.yaml").exists())

    def test_auto_mode_cannot_infer_strict_template(self):
        gate = load_gate()
        config = base_config(workflow_mode="auto", selection_mode="direct")
        config["template_application_mode"] = "strict-template"
        result = gate.run_gate(self.output, config, input_fn=lambda _: self.fail("auto must not prompt"), output_fn=lambda _: None)
        self.assertEqual("failed", result.status)
        self.assertIn("strict-template", result.message)

    def test_auto_mode_records_inference_without_prompt(self):
        gate = load_gate()
        config = base_config(workflow_mode="auto", selection_mode="direct")
        result = gate.run_gate(self.output, config, input_fn=lambda _: self.fail("auto must not prompt"), output_fn=lambda _: None)
        self.assertEqual("ready", result.status)
        self.assertTrue((self.output / "deck-config.confirmed.yaml").exists())
        report = (self.output / "config-selection-report.md").read_text(encoding="utf-8")
        self.assertIn("auto_inference", report)

    def test_direct_mode_requires_explicit_user_fields(self):
        gate = load_gate()
        config = base_config(workflow_mode="manual", selection_mode="direct")
        result = gate.run_gate(self.output, config, explicit_fields={"presentation_type"}, output_fn=lambda _: None)
        self.assertEqual("failed", result.status)
        self.assertIn("explicit", result.message)

    def test_guided_falls_back_to_numbered_text_options(self):
        gate = load_gate()
        seen = []
        result = gate.run_gate(self.output, base_config(), input_fn=iter([""]).__next__, output_fn=seen.append)
        self.assertEqual("awaiting_configuration", result.status)
        self.assertTrue(any("1)" in line for line in seen))

    def test_guided_confirmation_writes_confirmed_config(self):
        gate = load_gate()
        values = ["2", "3", "2", "2", "2", "1", "1", "3", "3", "2", "yes"]
        make_candidates(self.output)
        result = gate.run_gate(self.output, base_config(), input_fn=iter(values).__next__, output_fn=lambda _: None)
        self.assertEqual("awaiting_style_selection", result.status)
        self.assertTrue((self.output / "deck-config.confirmed.yaml").exists())
        self.assertFalse((self.output / "selected-style.yaml").exists())

    def test_manual_user_selection_writes_confirmation_metadata(self):
        gate = load_gate()
        config = base_config()
        write_confirmed(self.output, config)
        make_candidates(self.output)
        result = gate.run_gate(self.output, config, input_fn=iter(["1"]).__next__, output_fn=lambda _: None)
        self.assertEqual("ready", result.status)
        selected = (self.output / "selected-style.yaml").read_text(encoding="utf-8")
        self.assertIn("selected_by: \"user\"", selected)
        self.assertIn("candidate_profile_path", selected)

    def test_gate_bypass_makes_publish_fail(self):
        gate = load_gate()
        config = base_config(workflow_mode="manual", selection_mode="direct")
        write_confirmed(self.output, config)
        write_selected(self.output, selected_by="ai")
        with self.assertRaises(gate.GateBlocked):
            gate.assert_generation_allowed(self.output, "publish")


if __name__ == "__main__":
    unittest.main()
