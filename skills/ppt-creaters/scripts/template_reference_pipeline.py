"""Validation helpers for the v2.1 template-referenced image-first route.

This module deliberately does not call an image model or invent a provider API. The
Codex host injects the configured ``image_gen``/``image2`` adapter; this module only
checks the artifacts that the adapter and PPT assembler leave behind.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import struct
import sys
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence
from xml.etree import ElementTree as ET


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
SLIDE_RE = re.compile(r"^slide-(\d{2,})\.png$")
SOURCE_SLIDE_RE = re.compile(r"^source-slide-(\d{2,})\.png$")
PPT_SLIDE_RE = re.compile(r"^ppt/slides/slide(\d+)\.xml$")
NOTES_RE = re.compile(r"^ppt/notesSlides/notesSlide(\d+)\.xml$")


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def merge(self, other: "ValidationResult") -> "ValidationResult":
        return ValidationResult(
            self.ok and other.ok,
            self.errors + other.errors,
            self.warnings + other.warnings,
        )


def _numbered_pngs(directory: Path, pattern: re.Pattern[str]) -> dict[int, Path]:
    if not directory.is_dir():
        return {}
    files: dict[int, Path] = {}
    for path in directory.iterdir():
        match = pattern.match(path.name)
        if match and path.is_file():
            files[int(match.group(1))] = path
    return files


def _png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if not data.startswith(PNG_SIGNATURE) or len(data) < 24 or data[12:16] != b"IHDR":
        raise ValueError(f"not a readable PNG: {path}")
    width, height = struct.unpack(">II", data[16:24])
    if width <= 0 or height <= 0:
        raise ValueError(f"PNG has invalid dimensions: {path}")
    return width, height


def _check_16_9(paths: Iterable[Path], label: str) -> list[str]:
    errors: list[str] = []
    for path in paths:
        try:
            width, height = _png_size(path)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        ratio = width / height
        if abs(ratio - (16 / 9)) > 0.02:
            errors.append(f"{label} {path.name} is not 16:9: {width}x{height}")
    return errors


def _contiguous(numbers: Sequence[int], expected: int | None) -> bool:
    if not numbers:
        return False
    target = expected if expected is not None else len(numbers)
    return list(numbers) == list(range(1, target + 1))


def validate_asset_stages(root: Path | str, expected_slide_count: int | None = None) -> ValidationResult:
    """Validate reference, preview, and final image stages for a production run."""
    root = Path(root)
    errors: list[str] = []
    warnings: list[str] = []
    references = _numbered_pngs(root / "reference-slides", SOURCE_SLIDE_RE)
    previews = _numbered_pngs(root / "preview-images", SLIDE_RE)
    finals = _numbered_pngs(root / "final-images", SLIDE_RE)
    stages = (("reference", references), ("preview", previews), ("final", finals))

    if expected_slide_count is None:
        counts = {len(items) for _, items in stages}
        if len(counts) != 1 or not counts or 0 in counts:
            errors.append("reference, preview, and final image counts must match and be non-zero")
        expected_slide_count = len(references)

    for label, items in stages:
        if len(items) != expected_slide_count:
            errors.append(f"{label} image count {len(items)} != expected {expected_slide_count}")
        if items and not _contiguous(sorted(items), expected_slide_count):
            errors.append(f"{label} image numbering must be contiguous from 01 to {expected_slide_count:02d}")
        errors.extend(_check_16_9(items.values(), label))

    if references and previews and len(references) == len(previews):
        for number in sorted(references):
            if number not in previews:
                errors.append(f"preview is missing slide {number:02d} reference")
    if previews and finals:
        for number in sorted(previews):
            if number in finals and hashlib.sha256(previews[number].read_bytes()).digest() == hashlib.sha256(finals[number].read_bytes()).digest():
                errors.append(f"final image slide {number:02d} reuses the preview bytes; generate/approve a final asset")

    return ValidationResult(not errors, errors, warnings)


def _pptx_slide_numbers(pptx_path: Path) -> tuple[list[int], list[int], list[str]]:
    errors: list[str] = []
    try:
        archive = zipfile.ZipFile(pptx_path)
    except (OSError, zipfile.BadZipFile) as exc:
        return [], [], [f"cannot open PPTX {pptx_path}: {exc}"]
    with archive:
        slide_numbers = sorted(int(match.group(1)) for name in archive.namelist() if (match := PPT_SLIDE_RE.match(name)))
        note_numbers = sorted(int(match.group(1)) for name in archive.namelist() if (match := NOTES_RE.match(name)))
        pic_tag = "{http://schemas.openxmlformats.org/presentationml/2006/main}pic"
        shape_tag = "{http://schemas.openxmlformats.org/presentationml/2006/main}sp"
        for number in slide_numbers:
            name = f"ppt/slides/slide{number}.xml"
            try:
                root = ET.fromstring(archive.read(name))
            except (KeyError, ET.ParseError) as exc:
                errors.append(f"cannot parse {name}: {exc}")
                continue
            pictures = root.findall(f".//{pic_tag}")
            shapes = root.findall(f".//{shape_tag}")
            if len(pictures) != 1:
                errors.append(f"slide {number:02d} must contain exactly one full-slide picture; found {len(pictures)}")
            if shapes:
                errors.append(f"slide {number:02d} contains native text/shape objects; image-first assembly forbids them")
    return slide_numbers, note_numbers, errors


def validate_image_deck(pptx_path: Path | str, expected_slide_count: int) -> ValidationResult:
    pptx_path = Path(pptx_path)
    slide_numbers, note_numbers, errors = _pptx_slide_numbers(pptx_path)
    if slide_numbers != list(range(1, expected_slide_count + 1)):
        errors.append(f"PPTX slide numbering/count {slide_numbers} does not match 01..{expected_slide_count:02d}")
    if note_numbers and note_numbers != slide_numbers:
        errors.append("speaker notes count/numbering does not match the slide deck")
    return ValidationResult(not errors, errors, [])


def validate_output(output_dir: Path | str, expected_slide_count: int | None = None) -> ValidationResult:
    """Validate the canonical output/ directory plus its image-only PPTX."""
    output_dir = Path(output_dir)
    result = validate_asset_stages(output_dir, expected_slide_count)
    count = expected_slide_count or len(_numbered_pngs(output_dir / "final-images", SLIDE_RE))
    required = ("outline.md", "presentation.pptx", "qa-report.md", "generation-report.md")
    errors = list(result.errors)
    for filename in required:
        if not (output_dir / filename).is_file():
            errors.append(f"missing required output file: {filename}")
    if count:
        errors.extend(validate_image_deck(output_dir / "presentation.pptx", count).errors)
    return ValidationResult(not errors, errors, result.warnings)


def validate_demo(project_dir: Path | str) -> ValidationResult:
    """Validate the checked-in v2.1 template-reference demo artifact.

    The demo intentionally keeps the approved preview files as the image source for
    the example deck. Production runs must use ``validate_output`` and provide a
    separate ``final-images`` directory.
    """
    project_dir = Path(project_dir)
    references = _numbered_pngs(project_dir / "reference-slides", SOURCE_SLIDE_RE)
    previews = _numbered_pngs(project_dir / "generated-previews", re.compile(r"^slide-(\d{2,})-preview\.png$"))
    errors: list[str] = []
    if len(references) == 0:
        errors.append("demo has no reference slide images")
    if len(references) != len(previews):
        errors.append(f"demo reference/preview count mismatch: {len(references)} vs {len(previews)}")
    if references and not _contiguous(sorted(references), len(references)):
        errors.append("demo reference numbering is not contiguous")
    if previews and not _contiguous(sorted(previews), len(previews)):
        errors.append("demo preview numbering is not contiguous")
    errors.extend(_check_16_9(references.values(), "reference"))
    errors.extend(_check_16_9(previews.values(), "preview"))
    pptx_path = project_dir / "presentation.pptx"
    if not pptx_path.is_file():
        errors.append("demo is missing presentation.pptx")
    elif references:
        errors.extend(validate_image_deck(pptx_path, len(references)).errors)
    warnings = ["demo deck uses approved preview assets as its final image source; production must regenerate final-images"]
    return ValidationResult(not errors, errors, warnings)


def _main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate the v2.1 template-reference image-first pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)
    output_parser = subparsers.add_parser("validate-output")
    output_parser.add_argument("output_dir", type=Path)
    output_parser.add_argument("--slide-count", type=int)
    demo_parser = subparsers.add_parser("validate-demo")
    demo_parser.add_argument("project_dir", type=Path)
    args = parser.parse_args(argv)
    result = validate_output(args.output_dir, args.slide_count) if args.command == "validate-output" else validate_demo(args.project_dir)
    for warning in result.warnings:
        print(f"WARNING: {warning}")
    for error in result.errors:
        print(f"ERROR: {error}")
    if result.ok:
        print("PASS")
        return 0
    print("FAIL")
    return 1


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
