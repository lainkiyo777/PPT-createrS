"""Validation policy for imported-template application modes.

The policy keeps template use semantic: style-reference is the default, while
strict-template is an explicit user choice and never an inference from upload.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence


TEMPLATE_APPLICATION_MODES = ("style-reference", "adaptive-layout", "strict-template")
DEFAULT_TEMPLATE_APPLICATION_MODE = "style-reference"


def normalize_template_application_mode(config: Mapping[str, Any] | None) -> str:
    """Return the configured mode, defaulting an uploaded template to style-reference."""
    if not config:
        return DEFAULT_TEMPLATE_APPLICATION_MODE
    value = config.get("template_application_mode")
    return str(value).strip() if value not in (None, "") else DEFAULT_TEMPLATE_APPLICATION_MODE


def validate_config_template_mode(
    config: Mapping[str, Any],
    *,
    confirmation_method: str | None = None,
    explicit_fields: Sequence[str] | None = None,
) -> list[str]:
    errors: list[str] = []
    mode = normalize_template_application_mode(config)
    if mode not in TEMPLATE_APPLICATION_MODES:
        return [f"invalid template_application_mode: {mode}"]
    if mode == "strict-template":
        method = confirmation_method or str(config.get("confirmation_method", ""))
        fields = set(explicit_fields or ())
        selected_by = str(
            config.get("template_application_mode_selected_by", config.get("template_mode_selected_by", ""))
        )
        user_selected = selected_by == "user" or "template_application_mode" in fields
        if method == "auto_inference" or not user_selected:
            errors.append("strict-template requires an explicit user choice; upload or AI inference is not confirmation")
    return errors


def _text(value: Any) -> str:
    if isinstance(value, (list, tuple, set)):
        return "; ".join(str(item) for item in value)
    return str(value or "")


def validate_slide_spec_template_mode(spec: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    required = (
        "template_application_mode", "dominant_visual", "layout_flexibility",
        "visual_inheritance", "prohibited_inheritance",
    )
    for field in required:
        if spec.get(field) in (None, ""):
            errors.append(f"slide spec is missing {field}")
    mode = normalize_template_application_mode(spec)
    if mode not in TEMPLATE_APPLICATION_MODES:
        errors.append(f"invalid template_application_mode: {mode}")
        return errors
    if mode == "style-reference":
        layout = spec.get("layout") if isinstance(spec.get("layout"), Mapping) else {}
        if str(layout.get("reuse_mode", "")).lower() == "duplicate-slide":
            errors.append("style-reference cannot use duplicate-slide")
        flexibility = _text(spec.get("layout_flexibility")).lower()
        if "fixed-source-textbox" in flexibility or "fixed" == flexibility.strip():
            errors.append("style-reference requires layout flexibility; source textboxes cannot fix the body container")
        if str(spec.get("content_density", "")).lower() == "over-capacity" and not any(
            token in flexibility for token in ("recompose", "split", "add", "resize")
        ):
            errors.append("over-capacity content requires a new composition or split")
        if not _text(spec.get("dominant_visual")).strip():
            errors.append("style-reference requires a dominant visual")
    return errors


def validate_slide_set_template_mode(specs: Sequence[Mapping[str, Any]]) -> list[str]:
    errors: list[str] = []
    style_specs = [spec for spec in specs if normalize_template_application_mode(spec) == "style-reference"]
    errors.extend(error for spec in style_specs for error in validate_slide_spec_template_mode(spec))
    if len(style_specs) > 1:
        compositions = [str(spec.get("composition_id", "")) for spec in style_specs]
        if not all(compositions) or len(set(compositions)) == 1:
            errors.append("style-reference slide set requires distinct new slide compositions")
        if all(str((spec.get("layout") or {}).get("reuse_mode", "")).lower() == "duplicate-slide" for spec in style_specs):
            errors.append("style-reference slide set cannot be an all duplicate-slide mapping")
    return errors

