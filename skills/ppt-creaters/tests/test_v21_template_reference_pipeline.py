import importlib.util
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "skills" / "ppt-creaters" / "scripts" / "template_reference_pipeline.py"


def _png_bytes(width: int, height: int, color: int = 0) -> bytes:
    """Create a tiny valid RGB PNG without depending on Pillow."""
    row = b"\x00" + (bytes((color, 0, 0)) * width)
    raw = row * height

    def chunk(kind: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        )

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw))
        + chunk(b"IEND", b"")
    )


class V21TemplateReferencePipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("template_reference_pipeline", MODULE_PATH)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Cannot load {MODULE_PATH}")
        cls.module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.module
        spec.loader.exec_module(cls.module)

    def _write_stage(self, root: Path, stage: str, names):
        directory = root / stage
        directory.mkdir(parents=True, exist_ok=True)
        for name in names:
            (directory / name).write_bytes(_png_bytes(160, 90, 1 if stage == "final-images" else 0))

    def test_requires_template_reference_preview_and_final_stages(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_stage(root, "reference-slides", ["source-slide-01.png"])
            self._write_stage(root, "preview-images", ["slide-01.png"])
            self._write_stage(root, "final-images", ["slide-01.png"])
            result = self.module.validate_asset_stages(root, expected_slide_count=1)
            self.assertTrue(result.ok, result.errors)

    def test_rejects_mismatched_stage_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_stage(root, "reference-slides", ["source-slide-01.png"])
            self._write_stage(root, "preview-images", ["slide-01.png", "slide-02.png"])
            self._write_stage(root, "final-images", ["slide-01.png"])
            result = self.module.validate_asset_stages(root, expected_slide_count=2)
            self.assertFalse(result.ok)
            self.assertTrue(any("count" in error.lower() for error in result.errors))

    def test_rejects_non_16_9_stage_asset(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_stage(root, "reference-slides", ["source-slide-01.png"])
            self._write_stage(root, "preview-images", ["slide-01.png"])
            self._write_stage(root, "final-images", ["slide-01.png"])
            (root / "preview-images" / "slide-01.png").write_bytes(_png_bytes(100, 100))
            result = self.module.validate_asset_stages(root, expected_slide_count=1)
            self.assertFalse(result.ok)
            self.assertTrue(any("16:9" in error for error in result.errors))

    def test_style_reference_route_is_explicitly_image_first(self):
        contract = ROOT / "skills" / "ppt-creaters" / "references" / "template-reference-image-pipeline.md"
        text = contract.read_text(encoding="utf-8")
        self.assertIn("style-reference", text)
        self.assertIn("image_gen", text)
        self.assertIn("full-slide", text)
        self.assertIn("reference-slides", text)


if __name__ == "__main__":
    unittest.main()
