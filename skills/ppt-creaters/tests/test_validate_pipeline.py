import hashlib
import importlib.util
import shutil
import struct
import unittest
import uuid
import zipfile
import zlib
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = SKILL_ROOT / "scripts" / "validate_pipeline.py"
TEST_TMP_ROOT = SKILL_ROOT / ".test-tmp"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_pipeline", VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + chunk_type
        + data
        + struct.pack(">I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)
    )


def write_png(path: Path, width: int, height: int, color: tuple[int, int, int]) -> None:
    raw = b"".join(b"\x00" + bytes(color) * width for _ in range(height))
    payload = (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + png_chunk(b"IDAT", zlib.compress(raw))
        + png_chunk(b"IEND", b"")
    )
    path.write_bytes(payload)


def write_image_only_pptx(path: Path, slide_count: int, native_text_slide: int | None = None) -> None:
    presentation_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
        '<p:sldSz cx="12192000" cy="6858000"/>'
        "</p:presentation>"
    )
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("ppt/presentation.xml", presentation_xml)
        for slide_number in range(1, slide_count + 1):
            native_text = "<p:sp><p:txBody/></p:sp>" if slide_number == native_text_slide else ""
            slide_xml = (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
                'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
                "<p:cSld><p:spTree>"
                '<p:nvGrpSpPr/><p:grpSpPr/>'
                '<p:pic><p:nvPicPr/><p:blipFill/><p:spPr><a:xfrm>'
                '<a:off x="0" y="0"/><a:ext cx="12192000" cy="6858000"/>'
                "</a:xfrm></p:spPr></p:pic>"
                f"{native_text}</p:spTree></p:cSld></p:sld>"
            )
            archive.writestr(f"ppt/slides/slide{slide_number}.xml", slide_xml)


def write_slide_spec(path: Path, slide_number: int) -> None:
    path.write_text(
        "\n".join(
            [
                f'page_type: "content"',
                f'title: "Slide {slide_number}"',
                f'key_message: "Message {slide_number}"',
                'layout: "16:9 full-slide composition"',
                'visual_style: "editorial-v01"',
                'image_prompt: "Complete image prompt with exact hierarchy and content"',
                "source_assets: []",
                "dependencies: []",
                "qa_checklist:",
                '  - "Key message is legible"',
            ]
        ),
        encoding="utf-8",
    )


def write_report(path: Path, values: dict[str, str | int]) -> None:
    lines = ["---"] + [f"{key}: {value}" for key, value in values.items()] + ["---", "# Report"]
    path.write_text("\n".join(lines), encoding="utf-8")


def build_valid_output(root: Path, slide_count: int = 2) -> None:
    (root / "slide-specs").mkdir(parents=True)
    (root / "preview-images").mkdir()
    (root / "final-images").mkdir()
    (root / "outline.md").write_text(f"# Outline\n\nslide_count: {slide_count}\n", encoding="utf-8")
    for slide_number in range(1, slide_count + 1):
        stem = f"slide-{slide_number:02d}"
        write_slide_spec(root / "slide-specs" / f"{stem}.md", slide_number)
        write_png(root / "preview-images" / f"{stem}.png", 640, 360, (slide_number, 20, 30))
        write_png(root / "final-images" / f"{stem}.png", 1920, 1080, (slide_number, 40, 60))
    write_image_only_pptx(root / "presentation.pptx", slide_count)
    write_report(
        root / "qa-report.md",
        {
            "status": "pass",
            "page_count": slide_count,
            "preview_image_count": slide_count,
            "final_image_count": slide_count,
            "aspect_ratio_check": "pass",
            "missing_files_check": "pass",
            "font_size_risk_check": "pass",
            "overflow_check": "pass",
        },
    )
    write_report(
        root / "generation-report.md",
        {
            "status": "completed",
            "page_count": slide_count,
            "image_tool": "test-image-adapter",
            "image_tool_status": "available",
            "ppt_assembly_mode": "full-slide-images-only",
        },
    )


class PipelineValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.case_root = TEST_TMP_ROOT / f"{self._testMethodName}-{uuid.uuid4().hex}"
        self.output = self.case_root / "output"
        self.output.mkdir(parents=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.case_root, ignore_errors=True)

    def test_valid_image_first_pipeline_passes(self) -> None:
        build_valid_output(self.output)
        validator = load_validator()
        self.assertEqual([], validator.validate_output(self.output))

    def test_rejects_monolithic_slide_specs(self) -> None:
        build_valid_output(self.output)
        for path in (self.output / "slide-specs").glob("*.md"):
            path.unlink()
        (self.output / "slide-specs.txt").write_text("all slides", encoding="utf-8")
        validator = load_validator()
        errors = validator.validate_output(self.output)
        self.assertTrue(any("slide-specs/slide-XX.md" in error for error in errors))

    def test_rejects_missing_required_slide_spec_field(self) -> None:
        build_valid_output(self.output)
        spec_path = self.output / "slide-specs" / "slide-01.md"
        spec_path.write_text(spec_path.read_text(encoding="utf-8").replace("image_prompt:", "prompt:"), encoding="utf-8")
        validator = load_validator()
        errors = validator.validate_output(self.output)
        self.assertTrue(any("image_prompt" in error for error in errors))

    def test_rejects_missing_preview_or_final_image(self) -> None:
        build_valid_output(self.output)
        (self.output / "final-images" / "slide-02.png").unlink()
        validator = load_validator()
        errors = validator.validate_output(self.output)
        self.assertTrue(any("final-images" in error for error in errors))

    def test_rejects_preview_reused_as_final(self) -> None:
        build_valid_output(self.output)
        preview = self.output / "preview-images" / "slide-01.png"
        final = self.output / "final-images" / "slide-01.png"
        final.write_bytes(preview.read_bytes())
        self.assertEqual(hashlib.sha256(preview.read_bytes()).digest(), hashlib.sha256(final.read_bytes()).digest())
        validator = load_validator()
        errors = validator.validate_output(self.output)
        self.assertTrue(any("reuses the preview" in error for error in errors))

    def test_rejects_unavailable_image_tool(self) -> None:
        build_valid_output(self.output)
        report = self.output / "generation-report.md"
        report.write_text(report.read_text(encoding="utf-8").replace("image_tool_status: available", "image_tool_status: unavailable"), encoding="utf-8")
        validator = load_validator()
        errors = validator.validate_output(self.output)
        self.assertTrue(any("image tool" in error.lower() for error in errors))

    def test_rejects_native_text_or_chart_objects_in_pptx(self) -> None:
        build_valid_output(self.output)
        write_image_only_pptx(self.output / "presentation.pptx", 2, native_text_slide=2)
        validator = load_validator()
        errors = validator.validate_output(self.output)
        self.assertTrue(any("native layout object" in error for error in errors))

    def test_rejects_non_full_slide_image_placement(self) -> None:
        build_valid_output(self.output)
        pptx_path = self.output / "presentation.pptx"
        with zipfile.ZipFile(pptx_path, "r") as source:
            entries = {name: source.read(name) for name in source.namelist()}
        entries["ppt/slides/slide1.xml"] = entries["ppt/slides/slide1.xml"].replace(b'cx="12192000"', b'cx="10000000"')
        with zipfile.ZipFile(pptx_path, "w") as target:
            for name, content in entries.items():
                target.writestr(name, content)
        validator = load_validator()
        errors = validator.validate_output(self.output)
        self.assertTrue(any("does not cover the full slide" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
