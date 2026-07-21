import importlib.util
import json
import shutil
import unittest
import uuid
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = SKILL_ROOT / "scripts" / "workflow_runner.py"
TEST_TMP_ROOT = SKILL_ROOT / ".test-tmp-workflow"


def load_runner():
    if not RUNNER_PATH.is_file():
        return None
    spec = importlib.util.spec_from_file_location("workflow_runner", RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def blank_input(_prompt: str = "") -> str:
    return ""


class PersistentWorkflowStateTests(unittest.TestCase):
    def setUp(self):
        self.case_root = TEST_TMP_ROOT / f"{self._testMethodName}-{uuid.uuid4().hex}"
        self.output = self.case_root / "output"
        self.output.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.case_root, ignore_errors=True)

    def test_missing_modes_default_to_manual_guided_and_wait_for_configuration(self):
        runner = load_runner()
        self.assertIsNotNone(runner, "workflow_runner.py must provide the persistent runtime")
        result = runner.run_once(
            self.output,
            config={"template_source": "blue.pptx"},
            input_fn=blank_input,
            output_fn=lambda _line: None,
        )
        self.assertEqual("awaiting_configuration", result.status)
        state = runner._read_mapping(self.output / "build-state.yaml")
        self.assertEqual("manual", state["workflow_mode"])
        self.assertEqual("guided", state["selection_mode"])

    def test_uploaded_template_does_not_create_configuration_confirmation(self):
        runner = load_runner()
        self.assertIsNotNone(runner, "workflow_runner.py must provide the persistent runtime")
        runner.run_once(
            self.output,
            config={"template_source": "blue.pptx"},
            input_fn=blank_input,
            output_fn=lambda _line: None,
        )
        self.assertFalse((self.output / "deck-config.confirmed.yaml").exists())

    def test_one_execution_cannot_cross_two_awaiting_states(self):
        runner = load_runner()
        self.assertIsNotNone(runner, "workflow_runner.py must provide the persistent runtime")
        machine = runner.WorkflowStateMachine(self.output, workflow_mode="manual", selection_mode="guided")
        evidence = self.output / "evidence.json"
        evidence.write_text("{}", encoding="utf-8")
        machine.load()
        machine.transition("awaiting_configuration", stage="configuration", actor="orchestrator", evidence_files=[evidence])
        with self.assertRaises(runner.MultiAwaitTransitionError):
            machine.run_once(lambda _state: [
                {"status": "generating_style_candidates", "stage": "candidates", "evidence_files": [evidence]},
                {"status": "awaiting_style_selection", "stage": "style-selection", "evidence_files": [evidence]},
                {"status": "generating_slide_specs", "stage": "specs", "evidence_files": [evidence]},
                {"status": "generating_previews", "stage": "previews", "evidence_files": [evidence]},
                {"status": "reviewing", "stage": "review", "evidence_files": [evidence]},
                {"status": "awaiting_preview_approval", "stage": "preview-approval", "evidence_files": [evidence]},
            ])

    def test_unselected_candidate_blocks_full_preview(self):
        runner = load_runner()
        self.assertIsNotNone(runner, "workflow_runner.py must provide the persistent runtime")
        config = {
            "presentation_type": "technical-report",
            "visual_style": "academic-clean",
            "presentation_effect": "formal-report",
            "template_application_mode": "style-reference",
            "output_mode": "production-image",
            "notes_mode": "full",
            "target_duration_minutes": 20,
            "content_density": "medium",
            "template_source": "blue.pptx",
        }
        result = runner.run_once(
            self.output,
            config=config,
            input_fn=blank_input,
            output_fn=lambda _line: None,
        )
        self.assertEqual("awaiting_configuration", result.status)
        self.assertFalse((self.output / "preview-images").exists())
        self.assertFalse((self.output / "presentation.pptx").exists())


if __name__ == "__main__":
    unittest.main()
