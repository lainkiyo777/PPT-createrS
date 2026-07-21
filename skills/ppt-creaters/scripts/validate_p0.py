#!/usr/bin/env python3
"""Dependency-free validator for the PPT Creaters P0 contract."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path


CONFIG_ENUMS = {
    "presentation_type": {"research-report", "technical-report", "introductory", "academic-defense", "product-solution", "executive-summary", "training-course"},
    "visual_style": {"academic-clean", "university-formal", "technology-dark", "industrial-technical", "business-data", "light-modern", "institutional-red"},
    "presentation_effect": {"keynote", "formal-report", "academic", "storytelling", "dashboard", "documentary", "minimal"},
    "workflow_mode": {"auto", "manual"},
    "selection_mode": {"direct", "guided"},
    "template_application_mode": {"style-reference", "adaptive-layout", "strict-template"},
    "output_mode": {"production-image", "hybrid-editable", "background-only"},
    "notes_mode": {"none", "summary", "full"},
    "content_density": {"low", "medium", "high"},
}
CONFIG_REQUIRED = tuple(CONFIG_ENUMS) + (
    "language", "aspect_ratio", "audience", "target_duration_minutes", "style_confidence", "classification_reason",
)
SPEC_REQUIRED = (
    "slide_number", "page_type", "title", "key_message", "font_roles", "layout", "visual",
    "template_application_mode", "dominant_visual", "layout_flexibility", "visual_inheritance", "prohibited_inheritance",
    "source_assets", "referenced_metrics", "image_prompt", "style_reference_prompt", "reference_images",
    "deterministic_text_overlay", "deterministic_chart_overlay", "speaker_notes_path", "speaker_notes", "qa_checklist",
)
TYPOGRAPHY_MINIMUMS = {"body": 28, "chart_label": 24, "footnote": 18}
TEMPLATE_PROFILE_REQUIRED = (
    "color_palette", "typography", "spacing", "composition_language",
    "image_treatment", "chart_style", "icon_style", "page_rhythm",
    "layout_principles", "prohibited_behaviors",
)


def _load_sibling(name: str):
    path = Path(__file__).with_name(f"{name}.py")
    spec = importlib.util.spec_from_file_location(f"ppt_creaters_{name}_validator", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _read(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"Cannot read {path}: {exc}.")
        return ""


def _scalar(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^\s*{re.escape(key)}:\s*(.*?)\s*$", text)
    if not match:
        return None
    return match.group(1).strip().strip("\"'")


def _number(text: str, key: str) -> float | None:
    value = _scalar(text, key)
    try:
        return float(value) if value is not None else None
    except ValueError:
        return None


def _has_key(text: str, key: str) -> bool:
    return re.search(rf"(?m)^{re.escape(key)}:\s*", text) is not None


def _block_items(text: str, key: str) -> list[str]:
    lines = text.splitlines()
    items: list[str] = []
    active = False
    base_indent = 0
    for line in lines:
        if not active:
            match = re.match(rf"^(\s*){re.escape(key)}:\s*", line)
            if match:
                active = True
                base_indent = len(match.group(1))
            continue
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()
        if indent <= base_indent and not stripped.startswith("-"):
            break
        if stripped.startswith("-"):
            items.append(stripped[1:].strip().strip("\"'"))
    return items


def _status_report(root: Path, filename: str, errors: list[str]) -> None:
    path = root / filename
    text = _read(path, errors) if path.is_file() else ""
    if not path.is_file():
        errors.append(f"Missing {filename}.")
    elif _scalar(text, "status") != "pass":
        errors.append(f"{filename} must declare status: pass.")


def _check_config(root: Path, errors: list[str]) -> tuple[dict[str, str], int]:
    config_path = root / "deck-config.yaml"
    brief_path = root / "deck-brief.yaml"
    config = _read(config_path, errors) if config_path.is_file() else ""
    brief = _read(brief_path, errors) if brief_path.is_file() else ""
    if not config_path.is_file():
        errors.append("Missing deck-config.yaml.")
    if not brief_path.is_file():
        errors.append("Missing deck-brief.yaml.")
    values: dict[str, str] = {}
    for key in CONFIG_REQUIRED:
        value = _scalar(config, key)
        if value is None:
            errors.append(f"deck-config.yaml is missing {key}.")
        else:
            values[key] = value
    for key, allowed in CONFIG_ENUMS.items():
        if key in values and values[key] not in allowed:
            errors.append(f"Invalid {key}: {values[key]}; allowed={sorted(allowed)}.")
    if values.get("language") and values["language"] != "zh-CN":
        errors.append("P0 currently requires language: zh-CN for the deterministic Chinese text contract.")
    if values.get("aspect_ratio") != "16:9":
        errors.append("deck-config.yaml requires aspect_ratio: 16:9.")
    duration = _number(config, "target_duration_minutes")
    if duration is None or duration <= 0:
        errors.append("target_duration_minutes must be a positive number.")
    confidence = _number(config, "style_confidence")
    if confidence is None or not 0 <= confidence <= 1:
        errors.append("style_confidence must be between 0 and 1.")
    slide_count_value = _scalar(brief, "target_slide_count")
    try:
        slide_count = int(slide_count_value) if slide_count_value is not None else 0
    except ValueError:
        slide_count = 0
    if slide_count <= 0:
        errors.append("deck-brief.yaml requires a positive target_slide_count.")
    if not _has_key(brief, "presentation_goal"):
        errors.append("deck-brief.yaml is missing presentation_goal.")
    if values.get("workflow_mode") == "manual" and values.get("selection_mode") == "guided":
        if not (root / "selected-style.yaml").is_file():
            errors.append("Manual + guided mode requires selected-style.yaml before page generation.")
        candidates = sorted(path for path in (root / "style-candidates").glob("candidate-*") if path.is_dir())
        if not 2 <= len(candidates) <= 4:
            errors.append("Manual mode requires 2-4 style-candidates/candidate-* directories.")
        for candidate in candidates:
            for required in ("style-profile.yaml", "cover.png", "section.png", "content.png", "result.png"):
                if not (candidate / required).is_file():
                    errors.append(f"{candidate.name} is missing {required}.")
    return values, slide_count


def _mapping_file(path: Path, errors: list[str]) -> dict[str, object]:
    if not path.is_file():
        return {}
    text = _read(path, errors)
    try:
        payload = json.loads(text)
        return dict(payload) if isinstance(payload, dict) else {}
    except json.JSONDecodeError:
        result: dict[str, object] = {}
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or ":" not in stripped:
                continue
            key, value = stripped.split(":", 1)
            value = value.strip().strip("\"'")
            try:
                result[key.strip()] = json.loads(value)
            except json.JSONDecodeError:
                result[key.strip()] = value
        return result


def _check_selection_gate(root: Path, values: dict[str, str], errors: list[str]) -> None:
    """Validate the P0-A configuration and user-confirmed style gates."""
    confirmed_path = root / "deck-config.confirmed.yaml"
    if not confirmed_path.is_file():
        errors.append("Missing deck-config.confirmed.yaml; configuration confirmation gate has not completed.")
    else:
        confirmed = _mapping_file(confirmed_path, errors)
        method = str(confirmed.get("confirmation_method", ""))
        mode = values.get("template_application_mode", "style-reference")
        if mode == "strict-template":
            selected_by = str(confirmed.get("template_application_mode_selected_by", ""))
            provided = {item.strip() for item in str(confirmed.get("user_provided_fields", "")).split(",") if item.strip()}
            if method == "auto_inference" or not (selected_by == "user" or "template_application_mode" in provided):
                errors.append("strict-template requires explicit user selection; upload or AI inference is not enough.")
        workflow = values.get("workflow_mode")
        selection = values.get("selection_mode")
        if workflow == "auto":
            if method != "auto_inference":
                errors.append("auto mode requires confirmation_method: auto_inference in deck-config.confirmed.yaml.")
            report = root / "config-selection-report.md"
            report_text = _read(report, errors) if report.is_file() else ""
            if "auto_inference" not in report_text:
                errors.append("auto mode must record auto_inference in config-selection-report.md.")
        else:
            if method != "user_confirmed":
                errors.append("manual/direct mode requires confirmation_method: user_confirmed.")
            if confirmed.get("confirmed_by") != "user":
                errors.append("manual mode requires deck-config.confirmed.yaml confirmed_by: user.")
            sources = confirmed.get("configuration_source")
            required_source_fields = {
                "presentation_type", "visual_style", "presentation_effect", "template_application_mode",
                "output_mode", "notes_mode", "target_duration_minutes", "content_density",
            }
            if not isinstance(sources, dict) or set(sources) < required_source_fields:
                errors.append("manual mode requires configuration_source for all eight confirmed fields.")
            for field in ("presentation_type", "visual_style", "presentation_effect", "workflow_mode", "template_application_mode", "output_mode", "notes_mode", "target_duration_minutes", "content_density"):
                if field not in confirmed:
                    errors.append(f"deck-config.confirmed.yaml is missing confirmed field {field}.")
            if selection == "direct":
                provided = {item.strip() for item in str(confirmed.get("user_provided_fields", "")).split(",") if item.strip()}
                required = {"presentation_type", "visual_style", "presentation_effect", "workflow_mode", "selection_mode", "template_application_mode", "output_mode", "notes_mode", "target_duration_minutes", "content_density"}
                missing = sorted(required - provided)
                if missing:
                    errors.append("direct mode confirmation is missing explicit user fields: " + ", ".join(missing) + ".")

    state_path = root / "build-state.yaml"
    if not state_path.is_file():
        errors.append("Missing build-state.yaml; final publication requires persistent workflow state.")
    else:
        state = _mapping_file(state_path, errors)
        status = state.get("build_status")
        if status != "completed":
            errors.append(f"build-state.yaml blocks publication with build_status: {status}; require completed.")
        history = state.get("transition_history")
        if not isinstance(history, list) or not history:
            errors.append("build-state.yaml requires non-empty audited transition_history.")
        else:
            last = history[-1]
            if not isinstance(last, dict) or last.get("to") != "completed" or last.get("actor") != "orchestrator":
                errors.append("completed transition must be recorded by orchestrator.")
            if not isinstance(last.get("evidence_files"), list) or not last.get("evidence_files"):
                errors.append("completed transition requires evidence_files.")

    if values.get("workflow_mode") != "manual":
        return
    candidates = sorted(path for path in (root / "style-candidates").glob("candidate-*") if path.is_dir())
    if not 2 <= len(candidates) <= 4:
        errors.append("manual mode requires 2-4 style-candidates/candidate-* directories.")
    for candidate in candidates:
        for required in ("cover.png", "section.png", "content.png", "result.png", "style-profile.yaml"):
            if not (candidate / required).is_file():
                errors.append(f"{candidate.name} is missing {required}.")
    selected_path = root / "selected-style.yaml"
    if not selected_path.is_file():
        errors.append("manual mode requires selected-style.yaml after user style selection.")
        return
    selected = _mapping_file(selected_path, errors)
    for field in ("selected_candidate", "selected_by", "confirmation_timestamp", "candidate_profile_path", "template_profile"):
        if field not in selected:
            errors.append(f"selected-style.yaml is missing required field {field}.")
    if selected.get("selected_by") != "user":
        errors.append("selected-style.yaml selected_by must be user; AI selection is not valid.")
    names = {candidate.name for candidate in candidates}
    if selected.get("selected_candidate") not in names:
        errors.append("selected-style.yaml selected_candidate does not match a candidate directory.")
    candidate_errors = _load_sibling("artifact_guards").validate_style_candidates(root)
    errors.extend(candidate_errors)


def _check_template_profile(root: Path, errors: list[str]) -> None:
    """Require a semantic profile whenever a build imports a PPTX template."""
    config_path = root / "deck-config.yaml"
    config = _read(config_path, errors) if config_path.is_file() else ""
    template_source = _scalar(config, "template_source")
    if not template_source:
        return
    source_path = (root / template_source).resolve()
    if not source_path.is_file():
        errors.append(f"template_source does not resolve to a file: {template_source}.")
        return
    profile_ref = _scalar(config, "template_profile")
    if not profile_ref:
        errors.append("Imported templates require deck-config.yaml template_profile before page generation.")
        return
    profile_path = (root / profile_ref).resolve()
    expected = (source_path.parent.parent / "profiles" / source_path.stem / "style-profile.yaml").resolve()
    if profile_path != expected:
        errors.append(f"template_profile must be {expected}, not {profile_path}.")
    if not profile_path.is_file():
        errors.append(f"Missing imported-template style profile: {profile_path}.")
        return
    profile = _read(profile_path, errors)
    for field in TEMPLATE_PROFILE_REQUIRED:
        if not _has_key(profile, field):
            errors.append(f"style-profile.yaml is missing required section {field}.")


def _role_block(text: str, role: str) -> str:
    match = re.search(rf"(?ms)^  {re.escape(role)}:\s*\n(.*?)(?=^  [A-Za-z0-9_-]+:\s*$|\Z)", text)
    return match.group(1) if match else ""


def _check_typography(root: Path, errors: list[str]) -> None:
    path = root / "typography-scale.yaml"
    text = _read(path, errors) if path.is_file() else ""
    if not path.is_file():
        errors.append("Missing typography-scale.yaml.")
        return
    for key, expected in (("width", 1920), ("height", 1080)):
        value = _number(text, key)
        if value != expected:
            errors.append(f"typography-scale.yaml canvas {key} must be {expected}.")
    for role, minimum in TYPOGRAPHY_MINIMUMS.items():
        block = _role_block(text, role)
        values = {key: _number(block, key) for key in ("min_px", "preferred_px", "max_px")}
        if any(value is None for value in values.values()):
            errors.append(f"typography-scale.yaml is missing complete {role} role.")
            continue
        if values["min_px"] < minimum:
            errors.append(f"{role} min_px {values['min_px']} is below P0 minimum {minimum}.")
        if not values["min_px"] <= values["preferred_px"] <= values["max_px"]:
            errors.append(f"{role} typography values must satisfy min <= preferred <= max.")
    _status_report(root, "typography-qa-report.md", errors)


def _json_object(path: Path, errors: list[str]):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(f"Invalid JSON in {path}: {exc}.")
        return {}


def _check_specs_and_data(root: Path, slide_count: int, errors: list[str]) -> tuple[set[str], set[str]]:
    metrics_path = root / "data" / "metrics.json"
    tables_path = root / "data" / "tables.json"
    chart_dir = root / "data" / "chart-data"
    if not metrics_path.is_file():
        errors.append("Missing data/metrics.json.")
        metrics: dict[str, object] = {}
    else:
        metrics = _json_object(metrics_path, errors)
        if not isinstance(metrics, dict):
            errors.append("data/metrics.json must contain an object keyed by unique metric IDs.")
    if not tables_path.is_file():
        errors.append("Missing data/tables.json.")
    else:
        _json_object(tables_path, errors)
    if not chart_dir.is_dir() or not list(chart_dir.glob("*.json")):
        errors.append("data/chart-data/ must contain at least one structured JSON chart dataset.")
    else:
        for path in chart_dir.glob("*.json"):
            _json_object(path, errors)
    specs_dir = root / "slide-specs"
    specs = sorted(specs_dir.glob("slide-*.yaml")) if specs_dir.is_dir() else []
    expected = [f"slide-{index:02d}.yaml" for index in range(1, slide_count + 1)]
    if [path.name for path in specs] != expected:
        errors.append(f"slide-specs must contain exactly YAML files {expected}.")
    known_metrics = set(metrics) if isinstance(metrics, dict) else set()
    referenced: set[str] = set()
    for path in specs:
        text = _read(path, errors)
        for field in SPEC_REQUIRED:
            if not _has_key(text, field):
                errors.append(f"{path.name} is missing required field {field}.")
        mode = _scalar(text, "template_application_mode") or "style-reference"
        flexibility = (_scalar(text, "layout_flexibility") or "").lower()
        reuse_mode = (_scalar(text, "reuse_mode") or "").lower()
        if mode == "style-reference" and reuse_mode == "duplicate-slide":
            errors.append(f"{path.name} style-reference cannot use duplicate-slide.")
        if mode == "style-reference" and ("fixed-source-textbox" in flexibility or flexibility.strip() == "fixed"):
            errors.append(f"{path.name} source textboxes cannot fix layout flexibility.")
        if mode == "style-reference" and (_scalar(text, "content_density") or "").lower() == "over-capacity" and not any(token in flexibility for token in ("recompose", "split", "add", "resize")):
            errors.append(f"{path.name} over-capacity content requires recompose or split.")
        for metric in _block_items(text, "referenced_metrics"):
            referenced.add(metric)
            if metric not in known_metrics:
                errors.append(f"{path.name} references unknown metric {metric}.")
        notes_file = _scalar(text, "speaker_notes_path") or _scalar(text, "file")
        if not notes_file:
            errors.append(f"{path.name} must point speaker_notes.file to a note file.")
    _status_report(root, "data-qa-report.md", errors)
    return known_metrics, referenced


def _check_notes(root: Path, values: dict[str, str], slide_count: int, known_metrics: set[str], errors: list[str]) -> None:
    mode = values.get("notes_mode")
    if mode == "none":
        return
    notes_dir = root / "speaker-notes"
    expected = [f"slide-{index:02d}.md" for index in range(1, slide_count + 1)]
    notes = sorted(path.name for path in notes_dir.glob("slide-*.md")) if notes_dir.is_dir() else []
    if notes != expected:
        errors.append(f"speaker-notes must contain exactly {expected} when notes_mode is {mode}.")
    total_seconds = 0
    for name in notes:
        text = _read(notes_dir / name, errors)
        for field in ("slide_number", "purpose"):
            if not _has_key(text, field):
                errors.append(f"{name} is missing {field}.")
        seconds = _number(text, "estimated_duration_seconds")
        if seconds is None or seconds <= 0:
            errors.append(f"{name} requires positive estimated_duration_seconds.")
        else:
            total_seconds += seconds
        for metric in _block_items(text, "referenced_metrics"):
            if metric not in known_metrics:
                errors.append(f"{name} references unknown metric {metric}.")
    target = _number(_read(root / "deck-config.yaml", errors), "target_duration_minutes") or 0
    if target and notes and not target * 60 * 0.5 <= total_seconds <= target * 60 * 1.5:
        errors.append(f"Speaker-note duration {total_seconds}s is not close to target {target * 60}s.")
    _status_report(root, "speaker-notes-report.md", errors)


def _check_output(root: Path, values: dict[str, str], slide_count: int, errors: list[str]) -> None:
    mode = values.get("output_mode")
    if mode == "production-image":
        finals = sorted((root / "final-images").glob("slide-*.png")) if (root / "final-images").is_dir() else []
        expected = [f"slide-{index:02d}.png" for index in range(1, slide_count + 1)]
        if [path.name for path in finals] != expected:
            errors.append("production-image requires one final-images/slide-XX.png for every slide.")
        if not (root / "presentation.pptx").is_file():
            errors.append("production-image requires presentation.pptx.")
        else:
            qa = _mapping_file(root / "final-images-qa.json", errors)
            if qa.get("status") != "pass" or str(qa.get("image_count")) != str(slide_count):
                errors.append("final-images-qa.json must pass with image_count equal to slide count.")
            note_errors = _load_sibling("presentation_guard").validate_presentation(
                root / "presentation.pptx", root / "speaker-notes", slide_count=slide_count
            )
            errors.extend(note_errors)
    elif mode == "hybrid-editable":
        if not (root / "presentation.pptx").is_file():
            errors.append("hybrid-editable requires presentation.pptx as the editable output contract.")
    elif mode == "background-only":
        backgrounds = sorted((root / "backgrounds").glob("slide-*-bg.png")) if (root / "backgrounds").is_dir() else []
        guides = sorted((root / "layout-guides").glob("slide-*-layout.json")) if (root / "layout-guides").is_dir() else []
        expected_bg = [f"slide-{index:02d}-bg.png" for index in range(1, slide_count + 1)]
        expected_guides = [f"slide-{index:02d}-layout.json" for index in range(1, slide_count + 1)]
        if [path.name for path in backgrounds] != expected_bg:
            errors.append("background-only requires one backgrounds/slide-XX-bg.png per slide.")
        if [path.name for path in guides] != expected_guides:
            errors.append("background-only requires one layout-guides/slide-XX-layout.json per slide.")
        for path in guides:
            payload = _json_object(path, errors)
            for field in ("slide_number", "page_type", "title_area", "subtitle_area"):
                if field not in payload:
                    errors.append(f"{path.name} is missing layout field {field}.")
        if not (root / "presentation-backgrounds.pptx").is_file():
            errors.append("background-only requires presentation-backgrounds.pptx.")


def validate_p0(root: Path) -> list[str]:
    root = Path(root)
    errors: list[str] = []
    if not root.is_dir():
        return [f"Output directory does not exist: {root}."]
    values, slide_count = _check_config(root, errors)
    _check_selection_gate(root, values, errors)
    _check_template_profile(root, errors)
    _check_typography(root, errors)
    known_metrics, _ = _check_specs_and_data(root, slide_count, errors)
    _check_notes(root, values, slide_count, known_metrics, errors)
    _check_output(root, values, slide_count, errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    errors = validate_p0(args.output)
    if errors:
        print("FAIL: P0 contract validation failed")
        print("build_status: failed")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS: P0 contract validation succeeded")
    print("build_status: passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
