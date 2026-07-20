#!/usr/bin/env python3
"""Validate the mandatory image-first output contract for ppt-creaters."""

from __future__ import annotations

import argparse
import hashlib
import re
import struct
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


REQUIRED_ROOT_ENTRIES = {
    "outline.md",
    "slide-specs",
    "preview-images",
    "final-images",
    "presentation.pptx",
    "qa-report.md",
    "generation-report.md",
}
REQUIRED_SPEC_FIELDS = (
    "page_type",
    "title",
    "key_message",
    "layout",
    "visual_style",
    "image_prompt",
    "source_assets",
    "dependencies",
    "qa_checklist",
)
QA_REQUIRED = {
    "status": "pass",
    "aspect_ratio_check": "pass",
    "missing_files_check": "pass",
    "font_size_risk_check": "pass",
    "overflow_check": "pass",
}
GENERATION_REQUIRED = {
    "status": "completed",
    "image_tool_status": "available",
    "ppt_assembly_mode": "full-slide-images-only",
}
SLIDE_SIZE = (12192000, 6858000)


def _frontmatter(path: Path) -> dict[str, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return {}
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    values: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return values
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*?)\s*$", line)
        if match:
            values[match.group(1)] = match.group(2).strip("\"'")
    return {}


def _number(value: str | None) -> int | None:
    try:
        return int(value) if value is not None else None
    except ValueError:
        return None


def _png_size(path: Path) -> tuple[int, int] | None:
    try:
        header = path.read_bytes()[:24]
    except OSError:
        return None
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", header[16:24])


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _validate_specs(root: Path, errors: list[str]) -> tuple[int, list[str]]:
    specs_dir = root / "slide-specs"
    if not specs_dir.is_dir():
        errors.append("Missing slide-specs/ directory; require individual slide-specs/slide-XX.md files.")
        return 0, []
    specs = sorted(path.name for path in specs_dir.glob("*.md"))
    if not specs:
        errors.append("No individual slide-specs/slide-XX.md files found; a monolithic slide-specs.txt is forbidden.")
        return 0, []
    expected = [f"slide-{index:02d}.md" for index in range(1, len(specs) + 1)]
    if specs != expected:
        errors.append(f"slide-specs filenames must be contiguous slide-01.md..slide-{len(specs):02d}.md; found {specs}.")
    for name in specs:
        path = specs_dir / name
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"Cannot read slide-specs/{name}: {exc}.")
            continue
        for field in REQUIRED_SPEC_FIELDS:
            if not re.search(rf"(?m)^{re.escape(field)}:\s*", text):
                errors.append(f"slide-specs/{name} is missing required field: {field}.")
    return len(specs), [name[:-3] for name in specs]


def _validate_images(root: Path, stems: list[str], errors: list[str]) -> None:
    expected = {f"{stem}.png" for stem in stems}
    for directory_name in ("preview-images", "final-images"):
        directory = root / directory_name
        if not directory.is_dir():
            errors.append(f"Missing {directory_name}/ directory.")
            continue
        actual = {path.name for path in directory.glob("*.png")}
        if actual != expected:
            missing = sorted(expected - actual)
            extra = sorted(actual - expected)
            errors.append(f"{directory_name}/ must exactly match slide specs; missing={missing}, extra={extra}.")
        for filename in sorted(actual & expected):
            size = _png_size(directory / filename)
            if size is None:
                errors.append(f"{directory_name}/{filename} is not a readable PNG.")
                continue
            width, height = size
            if height == 0 or abs(width / height - 16 / 9) > 0.01:
                errors.append(f"{directory_name}/{filename} has ratio {width}:{height}; require 16:9.")
            if directory_name == "final-images" and (width < 1920 or height < 1080):
                errors.append(f"final-images/{filename} is {width}x{height}; final images require at least 1920x1080.")
    for stem in stems:
        preview = root / "preview-images" / f"{stem}.png"
        final = root / "final-images" / f"{stem}.png"
        if preview.is_file() and final.is_file() and _sha256(preview) == _sha256(final):
            errors.append(f"final-images/{stem}.png reuses the preview image; regenerate a distinct final image.")


def _validate_report_counts(root: Path, page_count: int, errors: list[str]) -> None:
    outline = root / "outline.md"
    if outline.is_file():
        match = re.search(r"(?m)^slide_count:\s*(\d+)\s*$", outline.read_text(encoding="utf-8"))
        if not match:
            errors.append("outline.md must contain slide_count: N.")
        elif int(match.group(1)) != page_count:
            errors.append(f"outline.md slide_count is {match.group(1)}, but {page_count} slide specs exist.")

    qa_path = root / "qa-report.md"
    qa = _frontmatter(qa_path) if qa_path.is_file() else {}
    if not qa:
        errors.append("qa-report.md must contain valid YAML frontmatter.")
    else:
        for key, expected in QA_REQUIRED.items():
            if qa.get(key) != expected:
                errors.append(f"qa-report.md requires {key}: {expected}.")
        for key in ("page_count", "preview_image_count", "final_image_count"):
            if _number(qa.get(key)) != page_count:
                errors.append(f"qa-report.md {key} must equal {page_count}.")

    report_path = root / "generation-report.md"
    report = _frontmatter(report_path) if report_path.is_file() else {}
    if not report:
        errors.append("generation-report.md must contain valid YAML frontmatter.")
    else:
        for key, expected in GENERATION_REQUIRED.items():
            if report.get(key) != expected:
                if key == "image_tool_status":
                    errors.append("The image tool is unavailable or unverified; the pipeline cannot be marked complete.")
                else:
                    errors.append(f"generation-report.md requires {key}: {expected}.")
        if not report.get("image_tool"):
            errors.append("generation-report.md must name the actual image tool or adapter used.")
        if _number(report.get("page_count")) != page_count:
            errors.append(f"generation-report.md page_count must equal {page_count}.")


def _validate_pptx(root: Path, page_count: int, errors: list[str]) -> None:
    pptx = root / "presentation.pptx"
    if not pptx.is_file():
        errors.append("Missing presentation.pptx.")
        return
    try:
        with zipfile.ZipFile(pptx) as archive:
            names = set(archive.namelist())
            if "ppt/presentation.xml" not in names:
                errors.append("presentation.pptx is missing ppt/presentation.xml.")
                return
            try:
                presentation = ET.fromstring(archive.read("ppt/presentation.xml"))
            except ET.ParseError as exc:
                errors.append(f"presentation.pptx has invalid presentation XML: {exc}.")
                return
            size_node = next((node for node in presentation.iter() if _local(node.tag) == "sldSz"), None)
            if size_node is None:
                errors.append("presentation.pptx does not declare a slide size.")
                return
            slide_cx = _number(size_node.get("cx"))
            slide_cy = _number(size_node.get("cy"))
            if (slide_cx, slide_cy) != SLIDE_SIZE:
                errors.append(f"presentation.pptx slide ratio/size is {slide_cx}x{slide_cy}; require 16:9 ({SLIDE_SIZE[0]}x{SLIDE_SIZE[1]} EMU).")

            slide_names = []
            for name in names:
                match = re.fullmatch(r"ppt/slides/slide(\d+)\.xml", name)
                if match:
                    slide_names.append((int(match.group(1)), name))
            slide_names.sort()
            expected_numbers = list(range(1, page_count + 1))
            if [number for number, _ in slide_names] != expected_numbers:
                errors.append(f"presentation.pptx must contain exactly {page_count} contiguous slides.")
            if any(name.startswith("ppt/charts/") for name in names):
                errors.append("presentation.pptx contains native chart parts; final PPT must use full-slide images only.")

            for number, name in slide_names:
                try:
                    slide = ET.fromstring(archive.read(name))
                except ET.ParseError as exc:
                    errors.append(f"Slide {number} XML is invalid: {exc}.")
                    continue
                sp_tree = next((node for node in slide.iter() if _local(node.tag) == "spTree"), None)
                if sp_tree is None:
                    errors.append(f"Slide {number} has no slide object tree.")
                    continue
                forbidden = [
                    _local(child.tag)
                    for child in list(sp_tree)
                    if _local(child.tag) in {"sp", "graphicFrame", "grpSp", "cxnSp"}
                ]
                if forbidden:
                    errors.append(f"Slide {number} contains native layout object(s) {forbidden}; only one full-slide picture is allowed.")
                pictures = [child for child in list(sp_tree) if _local(child.tag) == "pic"]
                if len(pictures) != 1:
                    errors.append(f"Slide {number} must contain exactly one picture; found {len(pictures)}.")
                    continue
                picture = pictures[0]
                xfrm = next((node for node in picture.iter() if _local(node.tag) == "xfrm"), None)
                off = next((node for node in xfrm.iter() if _local(node.tag) == "off"), None) if xfrm is not None else None
                ext = next((node for node in xfrm.iter() if _local(node.tag) == "ext"), None) if xfrm is not None else None
                placement = (
                    _number(off.get("x")) if off is not None else None,
                    _number(off.get("y")) if off is not None else None,
                    _number(ext.get("cx")) if ext is not None else None,
                    _number(ext.get("cy")) if ext is not None else None,
                )
                if placement != (0, 0, slide_cx, slide_cy):
                    errors.append(f"Slide {number} picture does not cover the full slide; placement={placement}.")
    except (OSError, zipfile.BadZipFile) as exc:
        errors.append(f"presentation.pptx cannot be opened as a PPTX archive: {exc}.")


def validate_output(root: Path) -> list[str]:
    root = Path(root)
    errors: list[str] = []
    if not root.is_dir():
        return [f"Output directory does not exist: {root}."]

    actual_entries = {path.name for path in root.iterdir()}
    for missing in sorted(REQUIRED_ROOT_ENTRIES - actual_entries):
        errors.append(f"Missing required output entry: {missing}.")
    unexpected = sorted(actual_entries - REQUIRED_ROOT_ENTRIES)
    if unexpected:
        errors.append(f"Unexpected output entries violate the fixed contract: {unexpected}.")
    if (root / "slide-specs.txt").exists():
        errors.append("slide-specs.txt is forbidden; use slide-specs/slide-XX.md.")

    page_count, stems = _validate_specs(root, errors)
    _validate_images(root, stems, errors)
    _validate_report_counts(root, page_count, errors)
    _validate_pptx(root, page_count, errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="Path to the output directory")
    args = parser.parse_args()
    errors = validate_output(args.output)
    if errors:
        print("FAIL: image-first pipeline validation failed")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS: image-first pipeline validation succeeded")
    return 0


if __name__ == "__main__":
    sys.exit(main())