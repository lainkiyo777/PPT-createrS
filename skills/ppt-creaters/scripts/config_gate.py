#!/usr/bin/env python3
"""Interactive configuration and style-selection gates for PPT production.

This module is intentionally independent from PPT rendering.  It must run before
outline, slide-spec, preview, final-image, or PPTX generation.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping


CONFIRM_FIELDS = (
    "presentation_type",
    "visual_style",
    "presentation_effect",
    "workflow_mode",
    "selection_mode",
    "output_mode",
    "notes_mode",
    "target_duration_minutes",
    "content_density",
)

OPTIONS: dict[str, tuple[Any, ...]] = {
    "presentation_type": (
        "research-report", "technical-report", "introductory", "academic-defense",
        "product-solution", "executive-summary", "training-course",
    ),
    "visual_style": (
        "academic-clean", "university-formal", "technology-dark", "industrial-technical",
        "business-data", "light-modern", "institutional-red",
    ),
    "presentation_effect": (
        "keynote", "formal-report", "academic", "storytelling", "dashboard",
        "documentary", "minimal",
    ),
    "workflow_mode": ("auto", "manual"),
    "selection_mode": ("direct", "guided"),
    "output_mode": ("production-image", "hybrid-editable", "background-only"),
    "notes_mode": ("none", "summary", "full"),
    "target_duration_minutes": (10, 15, 20, 30, 45),
    "content_density": ("low", "medium", "high"),
}

CANDIDATE_ASSETS = ("cover.png", "section.png", "content.png", "result.png", "style-profile.yaml")


class GateBlocked(RuntimeError):
    """Raised when a generation stage is attempted before a gate is ready."""

    def __init__(self, status: str, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


class GateResult:
    def __init__(self, status: str, message: str, confirmed_config_path: Path | None = None, selected_style_path: Path | None = None):
        self.status = status
        self.message = message
        self.confirmed_config_path = confirmed_config_path
        self.selected_style_path = selected_style_path

    @property
    def can_generate(self) -> bool:
        return self.status == "ready"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_yaml_scalars(path: Path, payload: Mapping[str, Any]) -> None:
    """Write a small scalar YAML file without requiring PyYAML.

    JSON is valid YAML, but scalar YAML is easier for users to inspect. Nested
    metadata is represented by flat fields in the gate artifacts.
    """
    lines: list[str] = []
    for key, value in payload.items():
        if isinstance(value, bool):
            rendered = "true" if value else "false"
        elif isinstance(value, (int, float)):
            rendered = str(value)
        elif value is None:
            rendered = "null"
        else:
            rendered = json.dumps(str(value), ensure_ascii=False)
        lines.append(f"{key}: {rendered}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _read_mapping(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8")
    try:
        payload = json.loads(text)
        return dict(payload) if isinstance(payload, dict) else {}
    except json.JSONDecodeError:
        result: dict[str, Any] = {}
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            key, raw_value = line.split(":", 1)
            value = raw_value.strip()
            if not value:
                continue
            if " #" in value:
                value = value.split(" #", 1)[0].rstrip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
                value = value[1:-1]
            if value.lower() in {"true", "false"}:
                result[key.strip()] = value.lower() == "true"
            else:
                try:
                    result[key.strip()] = float(value) if "." in value else int(value)
                except ValueError:
                    result[key.strip()] = value
        return result


def _write_state(output_dir: Path, status: str, message: str, **extra: Any) -> None:
    payload = {"build_status": status, "message": message, "updated_at": _now(), **extra}
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "build-status.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _write_report(output_dir: Path, status: str, message: str, **extra: Any) -> None:
    lines = [
        "# Configuration selection report",
        "",
        f"- build_status: `{status}`",
        f"- message: {message}",
        f"- updated_at: `{_now()}`",
    ]
    for key, value in extra.items():
        lines.append(f"- {key}: `{value}`")
    (output_dir / "config-selection-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _safe_input(input_fn: Callable[[str], str], prompt: str) -> str:
    try:
        value = input_fn(prompt)
    except TypeError:
        try:
            value = input_fn()  # test doubles such as iterator.__next__
        except (EOFError, StopIteration):
            return ""
    except (EOFError, StopIteration):
        return ""
    return "" if value is None else str(value).strip()


def _show_options(field: str, current: Any, output_fn: Callable[[str], None]) -> None:
    output_fn(f"{field} (recommended: {current!r})")
    for index, option in enumerate(OPTIONS[field], start=1):
        output_fn(f"  {index}) {option}")


def _collect_guided_config(
    config: Mapping[str, Any],
    input_fn: Callable[[str], str],
    output_fn: Callable[[str], None],
) -> dict[str, Any] | None:
    output_fn("Configuration choices are required before outline or page generation.")
    output_fn("The uploaded template is a reference only; it is not a user confirmation.")
    resolved = dict(config)
    for field in CONFIRM_FIELDS:
        _show_options(field, config.get(field), output_fn)
        raw = _safe_input(input_fn, f"Select {field} by number (blank = wait): ")
        if not raw:
            return None
        try:
            index = int(raw)
            options = OPTIONS[field]
            if not 1 <= index <= len(options):
                return None
            resolved[field] = options[index - 1]
        except (TypeError, ValueError):
            return None
    output_fn("Selected configuration:")
    for field in CONFIRM_FIELDS:
        output_fn(f"  {field}: {resolved.get(field)}")
    confirmed = _safe_input(input_fn, "Confirm configuration? type yes to continue (blank = wait): ")
    if confirmed.lower() not in {"y", "yes"}:
        return None
    return resolved


def _validate_required_config(config: Mapping[str, Any]) -> list[str]:
    missing = [field for field in CONFIRM_FIELDS if config.get(field) in (None, "")]
    if missing:
        return [f"missing configuration fields: {', '.join(missing)}"]
    invalid: list[str] = []
    for field, options in OPTIONS.items():
        if field in config and config[field] not in options:
            invalid.append(f"invalid {field}: {config[field]}")
    return invalid


def _write_confirmed_config(output_dir: Path, config: Mapping[str, Any], method: str) -> Path:
    payload = dict(config)
    payload["confirmation_method"] = method
    payload["confirmation_timestamp"] = _now()
    path = output_dir / "deck-config.confirmed.yaml"
    _write_yaml_scalars(path, payload)
    return path


def _candidate_dirs(output_dir: Path) -> tuple[list[Path], list[str]]:
    root = output_dir / "style-candidates"
    candidates = sorted(path for path in root.glob("candidate-*") if path.is_dir())
    errors: list[str] = []
    if not 2 <= len(candidates) <= 4:
        errors.append("manual mode requires 2-4 style-candidates/candidate-* directories")
    for candidate in candidates:
        for asset in CANDIDATE_ASSETS:
            if not (candidate / asset).is_file():
                errors.append(f"{candidate.name} is missing {asset}")
    return candidates, errors


def _manual_style_gate(
    output_dir: Path,
    input_fn: Callable[[str], str],
    output_fn: Callable[[str], None],
) -> GateResult:
    candidates, errors = _candidate_dirs(output_dir)
    if errors:
        message = "; ".join(errors)
        _write_state(output_dir, "failed", message)
        _write_report(output_dir, "failed", message)
        return GateResult("failed", message)
    selected_path = output_dir / "selected-style.yaml"
    if selected_path.is_file():
        selected = _read_mapping(selected_path)
        if selected.get("selected_by") != "user":
            message = "manual mode requires selected-style.yaml selected_by: user"
            _write_state(output_dir, "failed", message)
            _write_report(output_dir, "failed", message)
            return GateResult("failed", message)
        names = {candidate.name for candidate in candidates}
        if selected.get("selected_candidate") not in names:
            message = "selected-style.yaml names a candidate that does not exist"
            _write_state(output_dir, "failed", message)
            _write_report(output_dir, "failed", message)
            return GateResult("failed", message)
        return GateResult("ready", "user-confirmed candidate", selected_style_path=selected_path)

    output_fn("Candidate styles are ready. Select one; no candidate is selected automatically.")
    for index, candidate in enumerate(candidates, start=1):
        output_fn(f"  {index}) {candidate.name} (cover, section, content, result, profile)")
    raw = _safe_input(input_fn, "Select candidate by number (blank = wait): ")
    if not raw:
        message = "waiting for user style selection"
        _write_state(output_dir, "awaiting_style_selection", message)
        _write_report(output_dir, "awaiting_style_selection", message)
        return GateResult("awaiting_style_selection", message)
    try:
        index = int(raw)
        if not 1 <= index <= len(candidates):
            raise ValueError
    except (TypeError, ValueError):
        message = "invalid candidate selection; no candidate was confirmed"
        _write_state(output_dir, "failed", message)
        _write_report(output_dir, "failed", message)
        return GateResult("failed", message)
    candidate = candidates[index - 1]
    selected = {
        "selected_candidate": candidate.name,
        "selected_by": "user",
        "confirmation_timestamp": _now(),
        "candidate_profile_path": (candidate / "style-profile.yaml").relative_to(output_dir).as_posix(),
    }
    _write_yaml_scalars(selected_path, selected)
    message = f"user selected {candidate.name}"
    _write_state(output_dir, "ready", message, selected_candidate=candidate.name)
    _write_report(output_dir, "ready", message, selected_by="user", candidate_profile_path=selected["candidate_profile_path"])
    return GateResult("ready", message, selected_style_path=selected_path)


def run_gate(
    output_dir: Path,
    config: Mapping[str, Any] | None = None,
    *,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
    explicit_fields: Iterable[str] | None = None,
) -> GateResult:
    """Resolve configuration and, for manual mode, a user-confirmed candidate.

    This function is the only supported entry point before generation.  It never
    creates outline, slide specs, images, or PPTX files.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    config = dict(config) if config is not None else _read_mapping(output_dir / "deck-config.yaml")
    workflow_mode = config.get("workflow_mode")
    selection_mode = config.get("selection_mode")
    if workflow_mode not in {"auto", "manual"} or selection_mode not in {"direct", "guided"}:
        message = "workflow_mode and selection_mode must be explicit auto/manual and direct/guided values"
        _write_state(output_dir, "failed", message)
        _write_report(output_dir, "failed", message)
        return GateResult("failed", message)

    confirmed_path = output_dir / "deck-config.confirmed.yaml"
    if workflow_mode == "auto":
        errors = _validate_required_config(config)
        if errors:
            message = "; ".join(errors)
            _write_state(output_dir, "failed", message)
            _write_report(output_dir, "failed", message)
            return GateResult("failed", message)
        confirmed = _write_confirmed_config(output_dir, config, "auto_inference")
        message = "configuration auto-inferred; no user prompt was required"
        _write_state(output_dir, "ready", message, auto_inference=True)
        _write_report(output_dir, "ready", message, auto_inference="recorded in confirmed config")
        return GateResult("ready", message, confirmed_config_path=confirmed)

    if not confirmed_path.is_file():
        if selection_mode == "guided":
            resolved = _collect_guided_config(config, input_fn, output_fn)
            if resolved is None:
                message = "waiting for user configuration confirmation"
                _write_state(output_dir, "awaiting_configuration", message)
                _write_report(output_dir, "awaiting_configuration", message)
                return GateResult("awaiting_configuration", message)
            config = resolved
        else:
            required = set(CONFIRM_FIELDS)
            provided = set(explicit_fields or ())
            missing = sorted(required - provided)
            if missing:
                message = "direct mode requires explicit user fields: " + ", ".join(missing)
                _write_state(output_dir, "failed", message)
                _write_report(output_dir, "failed", message)
                return GateResult("failed", message)
            errors = _validate_required_config(config)
            if errors:
                message = "; ".join(errors)
                _write_state(output_dir, "failed", message)
                _write_report(output_dir, "failed", message)
                return GateResult("failed", message)
            config = dict(config)
            config["user_provided_fields"] = ",".join(sorted(set(explicit_fields or ())))
        confirmed_path = _write_confirmed_config(output_dir, config, "user_confirmed")

    if workflow_mode == "manual":
        result = _manual_style_gate(output_dir, input_fn, output_fn)
        return GateResult(result.status, result.message, confirmed_config_path=confirmed_path, selected_style_path=result.selected_style_path)

    message = "configuration confirmed"
    _write_state(output_dir, "ready", message)
    _write_report(output_dir, "ready", message)
    return GateResult("ready", message, confirmed_config_path=confirmed_path)


def assert_generation_allowed(output_dir: Path, stage: str) -> None:
    """Raise GateBlocked unless the requested generation stage is authorized."""
    output_dir = Path(output_dir)
    confirmed = output_dir / "deck-config.confirmed.yaml"
    if not confirmed.is_file():
        raise GateBlocked("awaiting_configuration", f"{stage} blocked until deck-config.confirmed.yaml exists")
    config = _read_mapping(confirmed)
    if config.get("workflow_mode") == "manual":
        selected = output_dir / "selected-style.yaml"
        if not selected.is_file():
            raise GateBlocked("awaiting_style_selection", f"{stage} blocked until selected-style.yaml exists")
        selected_payload = _read_mapping(selected)
        if selected_payload.get("selected_by") != "user":
            raise GateBlocked("failed", f"{stage} blocked because selected_by is not user")
    state_path = output_dir / "build-status.json"
    if state_path.is_file():
        state = _read_mapping(state_path)
        status = state.get("build_status")
        if status in {"awaiting_configuration", "awaiting_style_selection", "failed"}:
            raise GateBlocked(str(status), f"{stage} blocked by build_status={status}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="output directory containing deck-config.yaml")
    args = parser.parse_args(argv)
    result = run_gate(args.output)
    print(f"build_status: {result.status}")
    print(result.message)
    return 0 if result.status == "ready" else 2 if result.status.startswith("awaiting_") else 1


if __name__ == "__main__":
    sys.exit(main())
