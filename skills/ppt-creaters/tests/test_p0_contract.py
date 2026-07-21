import importlib.util
import json
import shutil
import unittest
import uuid
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = SKILL_ROOT / "scripts" / "validate_p0.py"
TEST_TMP_ROOT = SKILL_ROOT / ".test-tmp-p0"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_p0", VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_valid_deck(root: Path, output_mode: str = "production-image") -> None:
    config = "\n".join([
        "presentation_type: technical-report", "visual_style: technology-dark",
        "presentation_effect: keynote", "workflow_mode: manual",
        "selection_mode: guided", "template_application_mode: style-reference", f"output_mode: {output_mode}",
        "notes_mode: full", "content_density: medium",
        "target_duration_minutes: 2", "language: zh-CN", "aspect_ratio: 16:9",
        "audience: technical-management", "style_confidence: 0.92",
        "classification_reason: 技术报告配置", "",
    ])
    write(root / "deck-config.yaml", config)
    write(root / "deck-config.confirmed.yaml", config + "confirmation_method: user_confirmed\n")
    write(root / "deck-brief.yaml", "target_slide_count: 2\npresentation_goal: test\n")
    write(root / "selected-style.yaml", "\n".join([
        "selected_candidate: candidate-a",
        "selected_by: user",
        "confirmation_timestamp: 2026-07-21T00:00:00+00:00",
        "candidate_profile_path: style-candidates/candidate-a/style-profile.yaml",
        "",
    ]))
    for candidate in ("candidate-a", "candidate-b"):
        for filename in ("style-profile.yaml", "cover.png", "section.png", "content.png", "result.png"):
            write(root / "style-candidates" / candidate / filename, "x")
    typography = "\n".join([
        "canvas:", "  width: 1920", "  height: 1080", "font_roles:",
        "  body:", "    min_px: 28", "    preferred_px: 31", "    max_px: 34",
        "  chart_label:", "    min_px: 24", "    preferred_px: 26", "    max_px: 28",
        "  footnote:", "    min_px: 18", "    preferred_px: 20", "    max_px: 21", "",
    ])
    write(root / "typography-scale.yaml", typography)
    for report in ("typography-qa-report.md", "data-qa-report.md", "speaker-notes-report.md"):
        write(root / report, "---\nstatus: pass\n---\n")
    write(root / "data" / "metrics.json", json.dumps({"prediction_horizons": {"value": 16, "unit": "points"}}))
    write(root / "data" / "tables.json", "{}")
    write(root / "data" / "chart-data" / "chart-01.json", "{}")
    for number in (1, 2):
        spec = "\n".join([
            f"slide_number: {number}", "page_type: content", f"title: Slide {number}",
            f"key_message: Message {number}", "template_application_mode: style-reference", "dominant_visual: chart or scene", "layout_flexibility: recompose; move; resize; add chart", "visual_inheritance: blue/cyan palette and Chinese sans hierarchy", "prohibited_inheritance: source text and fixed source textbox coordinates", "font_roles:", "  title: page_title", "  body: body",
            "layout:", "  structure: content", "  reuse_mode: new-composition", "visual_style:", "  profile: style-reference", "visual:", "  style: technology-dark", "  effect: keynote",
            "source_assets: []", "image_prompt: deterministic image prompt", "referenced_metrics:", "  - prediction_horizons",
            f"speaker_notes:", f"  file: ../speaker-notes/slide-{number:02d}.md", "qa_checklist:",
            "  - title_not_overflow", "",
        ])
        write(root / "slide-specs" / f"slide-{number:02d}.yaml", spec)
        note = "\n".join([
            f"slide_number: {number}", f"purpose: Explain slide {number}",
            "estimated_duration_seconds: 60", "referenced_metrics:", "  - prediction_horizons",
            "", "## 建议讲稿", "", "说明本页结论，并承接前后页面。", "",
        ])
        write(root / "speaker-notes" / f"slide-{number:02d}.md", note)
    if output_mode == "production-image":
        write(root / "presentation.pptx", "pptx-test-bytes")
        for number in (1, 2):
            write(root / "final-images" / f"slide-{number:02d}.png", "png")
    else:
        for number in (1, 2):
            write(root / "backgrounds" / f"slide-{number:02d}-bg.png", "png")
            layout = {"slide_number": number, "page_type": "content", "title_area": {"x": 1}, "subtitle_area": {"x": 1}}
            write(root / "layout-guides" / f"slide-{number:02d}-layout.json", json.dumps(layout))
        write(root / "presentation-backgrounds.pptx", "pptx-test-bytes")


class P0ContractTests(unittest.TestCase):
    def setUp(self):
        self.case_root = TEST_TMP_ROOT / f"{self._testMethodName}-{uuid.uuid4().hex}"
        self.output = self.case_root / "output"
        self.output.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.case_root, ignore_errors=True)

    def test_valid_production_image_contract_passes(self):
        build_valid_deck(self.output)
        self.assertEqual([], load_validator().validate_p0(self.output))

    def test_rejects_invalid_configuration_enum(self):
        build_valid_deck(self.output)
        path = self.output / "deck-config.yaml"
        path.write_text(path.read_text(encoding="utf-8").replace("visual_style: technology-dark", "visual_style: unknown"), encoding="utf-8")
        errors = load_validator().validate_p0(self.output)
        self.assertTrue(any("visual_style" in error for error in errors))

    def test_manual_guided_requires_selected_style(self):
        build_valid_deck(self.output)
        (self.output / "selected-style.yaml").unlink()
        errors = load_validator().validate_p0(self.output)
        self.assertTrue(any("selected-style.yaml" in error for error in errors))

    def test_rejects_body_font_below_minimum(self):
        build_valid_deck(self.output)
        path = self.output / "typography-scale.yaml"
        path.write_text(path.read_text(encoding="utf-8").replace("min_px: 28", "min_px: 26"), encoding="utf-8")
        errors = load_validator().validate_p0(self.output)
        self.assertTrue(any("body" in error and "28" in error for error in errors))

    def test_rejects_unknown_metric_reference(self):
        build_valid_deck(self.output)
        path = self.output / "slide-specs" / "slide-01.yaml"
        path.write_text(path.read_text(encoding="utf-8").replace("prediction_horizons", "missing_metric"), encoding="utf-8")
        errors = load_validator().validate_p0(self.output)
        self.assertTrue(any("missing_metric" in error for error in errors))

    def test_rejects_missing_full_notes(self):
        build_valid_deck(self.output)
        (self.output / "speaker-notes" / "slide-02.md").unlink()
        errors = load_validator().validate_p0(self.output)
        self.assertTrue(any("speaker-notes" in error for error in errors))

    def test_background_only_requires_background_contract(self):
        build_valid_deck(self.output, output_mode="background-only")
        (self.output / "presentation-backgrounds.pptx").unlink()
        errors = load_validator().validate_p0(self.output)
        self.assertTrue(any("presentation-backgrounds.pptx" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
