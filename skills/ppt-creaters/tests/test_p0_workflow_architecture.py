import importlib.util
import json
import shutil
import unittest
import uuid
import zipfile
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
TEST_TMP_ROOT = SKILL_ROOT / ".test-tmp-p0-architecture"


def load_script(name):
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"ppt_creaters_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_mapping(path):
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        result = {}
        for line in text.splitlines():
            if ":" not in line or line.lstrip().startswith("#"):
                continue
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip("\"'")
        return result


def confirmed_manual_config():
    return {
        "presentation_type": "technical-report",
        "visual_style": "academic-clean",
        "presentation_effect": "formal-report",
        "workflow_mode": "manual",
        "selection_mode": "guided",
        "template_application_mode": "style-reference",
        "output_mode": "production-image",
        "notes_mode": "full",
        "target_duration_minutes": 20,
        "content_density": "medium",
        "template_source": "blue-template.pptx",
        "template_profile": "references/deck-library/profiles/blue-template/style-profile.yaml",
        "reference_images": ["blue-template-preview.png"],
    }


class FakeImage2:
    tool_name = "image2"
    model_or_tool_version = "test-image2-v1"

    def __init__(self, available=True, succeed=True):
        self.available = available
        self.succeed = succeed
        self.calls = []

    def generate(self, *, prompt_path, reference_images, output_path):
        self.calls.append({
            "prompt_path": str(prompt_path),
            "reference_images": list(reference_images),
            "output_path": str(output_path),
        })
        if not self.available:
            raise RuntimeError("image2 unavailable")
        if self.succeed:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            Path(output_path).write_bytes(b"image2-test-output")
        return self.succeed


def write_minimal_pptx(path, *, with_text=False, with_notes=False, note_text="note one"):
    slide = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        '<p:cSld><p:spTree><p:nvGrpSpPr/><p:grpSpPr/>'
        '<p:pic><p:spPr><a:xfrm><a:off x="0" y="0"/>'
        '<a:ext cx="12192000" cy="6858000"/></a:xfrm></p:spPr></p:pic>'
        + ('<p:sp><p:txBody><a:p><a:r><a:t>forbidden</a:t></a:r></a:p></p:txBody></p:sp>' if with_text else '')
        + '</p:spTree></p:cSld></p:sld>'
    )
    presentation = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
        '<p:sldSz cx="12192000" cy="6858000"/></p:presentation>'
    )
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("ppt/presentation.xml", presentation)
        archive.writestr("ppt/slides/slide1.xml", slide)
        if with_notes:
            archive.writestr(
                "ppt/slides/_rels/slide1.xml.rels",
                '<?xml version="1.0" encoding="UTF-8"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide" Target="../notesSlides/notesSlide1.xml"/>'
                '</Relationships>',
            )
            archive.writestr(
                "ppt/notesSlides/notesSlide1.xml",
                '<?xml version="1.0" encoding="UTF-8"?>'
                '<p:notes xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
                'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
                f'<p:cSld><p:spTree><p:sp><p:txBody><a:p><a:r><a:t>{note_text}</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld></p:notes>',
            )


class P0WorkflowArchitectureTests(unittest.TestCase):
    def setUp(self):
        self.case_root = TEST_TMP_ROOT / f"{self._testMethodName}-{uuid.uuid4().hex}"
        self.output = self.case_root / "output"
        self.output.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.case_root, ignore_errors=True)

    def test_01_default_stops_at_awaiting_configuration(self):
        runner = load_script("workflow_runner")
        result = runner.run_once(self.output, config={}, input_fn=lambda _="": "", output_fn=lambda _: None)
        self.assertEqual("awaiting_configuration", result.status)
        self.assertEqual("awaiting_configuration", read_mapping(self.output / "build-state.yaml")["build_status"])

    def test_02_template_upload_does_not_skip_configuration(self):
        runner = load_script("workflow_runner")
        result = runner.run_once(
            self.output,
            config={"template_source": "blue-template.pptx"},
            input_fn=lambda _="": "",
            output_fn=lambda _: None,
        )
        self.assertEqual("awaiting_configuration", result.status)
        self.assertFalse((self.output / "deck-config.confirmed.yaml").exists())

    def test_03_manual_mode_generates_exactly_three_image2_candidates(self):
        runner = load_script("workflow_runner")
        adapter = FakeImage2()
        runner.run_once(self.output, config=confirmed_manual_config(), input_fn=lambda _="": "", output_fn=lambda _: None)
        values = iter(["2", "1", "2", "1", "1", "3", "3", "2", "yes"])
        result = runner.run_once(
            self.output,
            config=confirmed_manual_config(),
            input_fn=lambda _="": next(values),
            output_fn=lambda _: None,
            image2_adapter=adapter,
        )
        self.assertEqual("awaiting_style_selection", result.status)
        self.assertEqual(12, len(adapter.calls))
        self.assertEqual(
            ["candidate-a", "candidate-b", "candidate-c"],
            sorted(path.name for path in (self.output / "style-candidates").iterdir()),
        )

    def test_04_candidates_not_generated_by_image2_fail(self):
        runner = load_script("workflow_runner")
        adapter = FakeImage2()
        adapter.tool_name = "presentation"
        runner.run_once(self.output, config=confirmed_manual_config(), input_fn=lambda _="": "", output_fn=lambda _: None)
        values = iter(["2", "1", "2", "1", "1", "3", "3", "2", "yes"])
        result = runner.run_once(
            self.output,
            config=confirmed_manual_config(),
            input_fn=lambda _="": next(values),
            output_fn=lambda _: None,
            image2_adapter=adapter,
        )
        self.assertEqual("failed", result.status)
        self.assertFalse((self.output / "presentation.pptx").exists())

    def test_05_missing_image_manifest_fails_candidate_validation(self):
        guards = load_script("artifact_guards")
        for candidate in ("candidate-a", "candidate-b", "candidate-c"):
            for name in ("cover.png", "section.png", "content.png", "result.png", "style-profile.yaml"):
                target = self.output / "style-candidates" / candidate / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(b"x")
        errors = guards.validate_style_candidates(self.output)
        self.assertTrue(any("image-generation-manifest.json" in error for error in errors))

    def test_06_unselected_candidate_blocks_full_preview(self):
        guards = load_script("artifact_guards")
        with self.assertRaises(guards.BuildBlocked):
            guards.assert_preview_generation_allowed(self.output)
        self.assertFalse((self.output / "preview-images").exists())

    def test_07_selected_by_must_be_user(self):
        guards = load_script("artifact_guards")
        (self.output / "selected-style.yaml").write_text("selected_by: ai\n", encoding="utf-8")
        with self.assertRaises(guards.BuildBlocked):
            guards.assert_preview_generation_allowed(self.output)

    def test_08_presentation_before_final_images_is_blocked(self):
        guard = load_script("presentation_guard")
        with self.assertRaises(guard.PresentationBlocked):
            guard.assert_assembly_ready(self.output, slide_count=1)

    def test_09_presentation_with_textbox_or_shape_fails(self):
        guard = load_script("presentation_guard")
        pptx = self.output / "presentation.pptx"
        write_minimal_pptx(pptx, with_text=True, with_notes=True)
        note_dir = self.output / "speaker-notes"
        note_dir.mkdir()
        (note_dir / "slide-01.md").write_text("note one", encoding="utf-8")
        errors = guard.validate_presentation(pptx, note_dir, slide_count=1)
        self.assertTrue(any("native layout object" in error for error in errors))

    def test_10_presentation_without_notes_slides_fails(self):
        guard = load_script("presentation_guard")
        pptx = self.output / "presentation.pptx"
        write_minimal_pptx(pptx)
        note_dir = self.output / "speaker-notes"
        note_dir.mkdir()
        (note_dir / "slide-01.md").write_text("note one", encoding="utf-8")
        errors = guard.validate_presentation(pptx, note_dir, slide_count=1)
        self.assertTrue(any("notesSlides" in error for error in errors))

    def test_11_one_run_cannot_cross_two_future_awaiting_states(self):
        runner = load_script("workflow_runner")
        machine = runner.WorkflowStateMachine(self.output)
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

    def test_12_image2_unavailable_fails_without_presentation_fallback(self):
        runner = load_script("workflow_runner")
        adapter = FakeImage2(available=False)
        runner.run_once(self.output, config=confirmed_manual_config(), input_fn=lambda _="": "", output_fn=lambda _: None)
        values = iter(["2", "1", "2", "1", "1", "3", "3", "2", "yes"])
        result = runner.run_once(
            self.output,
            config=confirmed_manual_config(),
            input_fn=lambda _="": next(values),
            output_fn=lambda _: None,
            image2_adapter=adapter,
        )
        self.assertEqual("failed", result.status)
        self.assertFalse((self.output / "presentation.pptx").exists())


if __name__ == "__main__":
    unittest.main()
