"""Restrict presentation to image-only assembly and verify speaker notes."""

from __future__ import annotations

import json
import posixpath
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


SLIDE_SIZE = (12192000, 6858000)
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


class PresentationBlocked(RuntimeError):
    pass


def _read_mapping(path: Path) -> dict[str, object]:
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8")
    try:
        value = json.loads(text)
        return dict(value) if isinstance(value, dict) else {}
    except json.JSONDecodeError:
        result = {}
        for line in text.splitlines():
            if ":" in line and not line.lstrip().startswith("#"):
                key, value = line.split(":", 1)
                result[key.strip()] = value.strip().strip("\"'")
        return result


def assert_assembly_ready(output_dir: Path, *, slide_count: int) -> None:
    output_dir = Path(output_dir)
    selected = _read_mapping(output_dir / "selected-style.yaml")
    if selected.get("selected_by") != "user":
        raise PresentationBlocked("presentation requires selected-style.yaml selected_by: user")
    finals = sorted((output_dir / "final-images").glob("slide-*.png")) if (output_dir / "final-images").is_dir() else []
    expected_final_names = [f"slide-{index:02d}.png" for index in range(1, slide_count + 1)]
    if [path.name for path in finals] != expected_final_names:
        raise PresentationBlocked(f"presentation requires final-images {expected_final_names}")
    qa = _read_mapping(output_dir / "final-images-qa.json")
    if qa.get("status") != "pass" or str(qa.get("image_count")) != str(slide_count):
        raise PresentationBlocked("final-images must pass QA before presentation is called")
    notes = sorted((output_dir / "speaker-notes").glob("slide-*.md")) if (output_dir / "speaker-notes").is_dir() else []
    expected_note_names = [f"slide-{index:02d}.md" for index in range(1, slide_count + 1)]
    if [path.name for path in notes] != expected_note_names:
        raise PresentationBlocked(f"presentation requires speaker notes {expected_note_names}")


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _int(value: str | None) -> int | None:
    try:
        return int(value) if value is not None else None
    except ValueError:
        return None


def _note_target(archive: zipfile.ZipFile, slide_number: int) -> str | None:
    rel_path = f"ppt/slides/_rels/slide{slide_number}.xml.rels"
    if rel_path not in archive.namelist():
        return None
    try:
        rels = ET.fromstring(archive.read(rel_path))
    except ET.ParseError:
        return None
    for rel in rels.findall(f"{{{REL_NS}}}Relationship"):
        if str(rel.get("Type", "")).endswith("/notesSlide"):
            target = rel.get("Target")
            if target:
                return posixpath.normpath(posixpath.join("ppt/slides", target))
    return None


def _extract_note(archive: zipfile.ZipFile, path: str) -> str:
    root = ET.fromstring(archive.read(path))
    paragraphs: list[str] = []
    for shape in (node for node in root.iter() if _local(node.tag) == "sp"):
        placeholder = next((node for node in shape.iter() if _local(node.tag) == "ph"), None)
        placeholder_type = placeholder.get("type") if placeholder is not None else None
        if placeholder_type not in {None, "body"}:
            continue
        for paragraph in (node for node in shape.iter() if _local(node.tag) == "p"):
            text = "".join(node.text or "" for node in paragraph.iter() if _local(node.tag) == "t")
            if text:
                paragraphs.append(text)
    return "\n".join(paragraphs).strip()


def validate_presentation(pptx_path: Path, notes_dir: Path, *, slide_count: int) -> list[str]:
    errors: list[str] = []
    pptx_path = Path(pptx_path)
    notes_dir = Path(notes_dir)
    try:
        with zipfile.ZipFile(pptx_path) as archive:
            names = set(archive.namelist())
            if "ppt/presentation.xml" not in names:
                errors.append("presentation is missing ppt/presentation.xml")
            else:
                try:
                    presentation = ET.fromstring(archive.read("ppt/presentation.xml"))
                    size = next((node for node in presentation.iter() if _local(node.tag) == "sldSz"), None)
                    actual_size = (_int(size.get("cx")), _int(size.get("cy"))) if size is not None else (None, None)
                    if actual_size != SLIDE_SIZE:
                        errors.append(f"presentation slide size is {actual_size}; expected 16:9 {SLIDE_SIZE}")
                except ET.ParseError as exc:
                    errors.append(f"presentation XML is invalid: {exc}")
            if any(name.startswith("ppt/charts/") for name in names):
                errors.append("presentation contains native chart parts")
            slide_names = sorted(
                (int(match.group(1)), name)
                for name in names
                if (match := re.fullmatch(r"ppt/slides/slide(\d+)\.xml", name))
            )
            if len(slide_names) != slide_count:
                errors.append(f"presentation contains {len(slide_names)} slides; expected {slide_count}")
            note_parts = {name for name in names if re.fullmatch(r"ppt/notesSlides/notesSlide\d+\.xml", name)}
            if len(note_parts) != slide_count:
                errors.append(f"notesSlides count is {len(note_parts)}; expected {slide_count}")
            for slide_number, slide_path in slide_names:
                try:
                    slide = ET.fromstring(archive.read(slide_path))
                except ET.ParseError as exc:
                    errors.append(f"slide {slide_number} XML is invalid: {exc}")
                    continue
                sp_tree = next((node for node in slide.iter() if _local(node.tag) == "spTree"), None)
                children = list(sp_tree) if sp_tree is not None else []
                forbidden = [_local(child.tag) for child in children if _local(child.tag) in {"sp", "graphicFrame", "grpSp", "cxnSp"}]
                if forbidden:
                    errors.append(f"slide {slide_number} contains native layout object(s) {forbidden}")
                pictures = [child for child in children if _local(child.tag) == "pic"]
                if len(pictures) != 1:
                    errors.append(f"slide {slide_number} must contain exactly one full-slide picture")
                elif pictures:
                    xfrm = next((node for node in pictures[0].iter() if _local(node.tag) == "xfrm"), None)
                    off = next((node for node in xfrm.iter() if _local(node.tag) == "off"), None) if xfrm is not None else None
                    ext = next((node for node in xfrm.iter() if _local(node.tag) == "ext"), None) if xfrm is not None else None
                    placement = (
                        _int(off.get("x")) if off is not None else None,
                        _int(off.get("y")) if off is not None else None,
                        _int(ext.get("cx")) if ext is not None else None,
                        _int(ext.get("cy")) if ext is not None else None,
                    )
                    if placement != (0, 0, *SLIDE_SIZE):
                        errors.append(f"slide {slide_number} picture is not full-slide: {placement}")
                expected_note_path = notes_dir / f"slide-{slide_number:02d}.md"
                if not expected_note_path.is_file():
                    errors.append(f"speaker-notes/slide-{slide_number:02d}.md is missing")
                    continue
                target = _note_target(archive, slide_number)
                if not target or target not in names:
                    errors.append(f"slide {slide_number} has no mapped notesSlides part")
                    continue
                try:
                    actual = _extract_note(archive, target)
                except ET.ParseError as exc:
                    errors.append(f"slide {slide_number} notes XML is invalid: {exc}")
                    continue
                expected = expected_note_path.read_text(encoding="utf-8").strip()
                if actual != expected:
                    errors.append(f"slide {slide_number} speaker note does not match speaker-notes/slide-{slide_number:02d}.md")
    except (OSError, zipfile.BadZipFile) as exc:
        errors.append(f"presentation.pptx cannot be reopened: {exc}")
    return errors
