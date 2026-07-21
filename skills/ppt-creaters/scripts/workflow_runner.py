"""One-run-at-a-time orchestrator for the human-gated PPT workflow."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping


def _load_sibling(name: str):
    module_name = f"ppt_creaters_{name}"
    if module_name in sys.modules:
        return sys.modules[module_name]
    path = Path(__file__).with_name(f"{name}.py")
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


try:
    from .state_machine import MultiAwaitTransitionError, WorkflowState, WorkflowStateMachine
except ImportError:
    _state = _load_sibling("state_machine")
    MultiAwaitTransitionError = _state.MultiAwaitTransitionError
    WorkflowState = _state.WorkflowState
    WorkflowStateMachine = _state.WorkflowStateMachine


CONFIG_FIELDS = (
    "presentation_type",
    "visual_style",
    "presentation_effect",
    "template_application_mode",
    "output_mode",
    "notes_mode",
    "target_duration_minutes",
    "content_density",
)
OPTIONS: dict[str, tuple[Any, ...]] = {
    "presentation_type": ("research-report", "technical-report", "introductory", "academic-defense", "product-solution", "executive-summary", "training-course"),
    "visual_style": ("academic-clean", "university-formal", "technology-dark", "industrial-technical", "business-data", "light-modern", "institutional-red"),
    "presentation_effect": ("keynote", "formal-report", "academic", "storytelling", "dashboard", "documentary", "minimal"),
    "template_application_mode": ("style-reference", "adaptive-layout", "strict-template"),
    "output_mode": ("production-image", "hybrid-editable", "background-only"),
    "notes_mode": ("none", "summary", "full"),
    "target_duration_minutes": (10, 15, 20, 30, 45),
    "content_density": ("low", "medium", "high"),
}
DEFAULT_CONFIG = {
    "presentation_type": "technical-report",
    "visual_style": "academic-clean",
    "presentation_effect": "formal-report",
    "template_application_mode": "style-reference",
    "output_mode": "production-image",
    "notes_mode": "full",
    "target_duration_minutes": 20,
    "content_density": "medium",
}
CANDIDATE_STYLES = {
    "candidate-a": "高校科研简洁风，白底、蓝色结构、克制、正式。",
    "candidate-b": "技术发布会风，深蓝或高对比、强主视觉、更具冲击力。",
    "candidate-c": "数据技术报告风，图表优先、信息结构清晰、适合科研结果汇报。",
}
CANDIDATE_PROFILES = {
    "candidate-a": {
        "color_palette": "white canvas; university blue structure; restrained cyan accent; dark neutral text",
        "typography": "formal Chinese sans-serif; generous title hierarchy; low decorative emphasis",
        "spacing": "wide margins; disciplined alignment; generous whitespace",
        "composition_language": "clear academic grid; one restrained dominant visual; formal balance",
        "image_treatment": "bright, clean, documentary technical imagery with low visual noise",
        "chart_style": "blue primary series; thin gridlines; direct labels; no decorative 3D",
        "icon_style": "simple line icons with consistent stroke weight",
        "page_rhythm": "quiet cover, clear section breaks, concise evidence pages, formal conclusion",
    },
    "candidate-b": {
        "color_palette": "deep blue field; white text; high-contrast cyan highlights; limited bright accent",
        "typography": "bold launch-event hierarchy; short copy; large numeric emphasis",
        "spacing": "strong focal zones; controlled asymmetry; generous negative space around hero visuals",
        "composition_language": "cinematic technical keynote; strong dominant visual; high contrast",
        "image_treatment": "dramatic but inspectable technology imagery; crisp edges; no atmospheric blur",
        "chart_style": "high-contrast series; luminous accent only for the key comparison; direct labels",
        "icon_style": "precise geometric icons with strong silhouette",
        "page_rhythm": "impactful cover, decisive chapter shifts, alternating hero and evidence pages",
    },
    "candidate-c": {
        "color_palette": "white or light neutral canvas; blue data structure; cyan and green semantic accents",
        "typography": "compact technical-report hierarchy; legible labels; stable data density",
        "spacing": "modular grid; aligned chart regions; consistent evidence gutters",
        "composition_language": "chart-first research reporting; explicit comparison and result hierarchy",
        "image_treatment": "use imagery only when it explains the domain; charts and diagrams take priority",
        "chart_style": "code-rendered analytical charts; clear axes, units, legends, and source line",
        "icon_style": "small functional line icons used only for navigation and semantics",
        "page_rhythm": "overview, method, evidence, comparison, conclusion with repeatable data families",
    },
}
CANDIDATE_PAGES = ("cover", "section", "content", "result")


class RunResult:
    def __init__(self, status: str, message: str, state: WorkflowState):
        self.status = status
        self.message = message
        self.state = state


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _atomic_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, path)


def _write_yaml_scalars(path: Path, payload: Mapping[str, Any]) -> None:
    lines = []
    for key, value in payload.items():
        if isinstance(value, bool):
            rendered = "true" if value else "false"
        elif isinstance(value, (int, float)):
            rendered = str(value)
        elif value is None:
            rendered = "null"
        else:
            rendered = json.dumps(value, ensure_ascii=False)
        lines.append(f"{key}: {rendered}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _read_mapping(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8")
    try:
        value = json.loads(text)
        return dict(value) if isinstance(value, dict) else {}
    except json.JSONDecodeError:
        result: dict[str, Any] = {}
        for raw in text.splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            key, value = line.split(":", 1)
            value = value.strip()
            try:
                result[key.strip()] = json.loads(value)
            except json.JSONDecodeError:
                result[key.strip()] = value.strip("\"'")
        return result


def _safe_input(input_fn: Callable[[str], str], prompt: str) -> str:
    try:
        value = input_fn(prompt)
    except TypeError:
        try:
            value = input_fn()
        except (EOFError, StopIteration):
            return ""
    except (EOFError, StopIteration):
        return ""
    return "" if value is None else str(value).strip()


def resolve_modes(config: Mapping[str, Any] | None, explicit_fields: Iterable[str] | None = None) -> tuple[str, str]:
    config = dict(config or {})
    explicit = set(explicit_fields or ())
    if (
        config.get("workflow_mode") == "auto"
        and config.get("selection_mode") == "direct"
        and {"workflow_mode", "selection_mode"}.issubset(explicit)
    ):
        return "auto", "direct"
    return "manual", "guided"


def _show_configuration(config: Mapping[str, Any], output_fn: Callable[[str], None]) -> None:
    output_fn("必须先确认配置；上传模板只提供 template_source，不代表确认任何选项。")
    output_fn("workflow_mode: manual; selection_mode: guided（默认）")
    for field in CONFIG_FIELDS:
        output_fn(f"{field} (recommended: {config.get(field)!r})")
        for index, option in enumerate(OPTIONS[field], start=1):
            output_fn(f"  {index}) {option}")


def _write_configuration_report(output_dir: Path, config: Mapping[str, Any]) -> None:
    lines = [
        "# Configuration selection report",
        "",
        "- build_status: `awaiting_configuration`",
        "- workflow_mode: `manual`",
        "- selection_mode: `guided`",
        "- template_upload_is_confirmation: `false`",
        "",
        "## Required user choices",
        "",
    ]
    for field in CONFIG_FIELDS:
        options = ", ".join(str(option) for option in OPTIONS[field])
        lines.append(f"- `{field}`: recommended `{config.get(field)}`; options: {options}")
    lines.extend(["", "No selection has been applied. Re-run the workflow and confirm all eight fields.", ""])
    (output_dir / "config-selection-report.md").write_text("\n".join(lines), encoding="utf-8")


def _write_pending_config(output_dir: Path, config: Mapping[str, Any]) -> Path:
    pending = dict(DEFAULT_CONFIG)
    pending.update(dict(config))
    pending["workflow_mode"] = str(config.get("workflow_mode", "manual"))
    pending["selection_mode"] = str(config.get("selection_mode", "guided"))
    pending["confirmed"] = False
    pending["configuration_source"] = {
        field: "default" if field not in config else "inferred" for field in CONFIG_FIELDS
    }
    path = output_dir / "deck-config.pending.yaml"
    _write_yaml_scalars(path, pending)
    return path


def _collect_configuration(config: Mapping[str, Any], input_fn: Callable[[str], str], output_fn: Callable[[str], None]) -> dict[str, Any] | None:
    _show_configuration(config, output_fn)
    resolved = dict(config)
    for field in CONFIG_FIELDS:
        raw = _safe_input(input_fn, f"Select {field} by number (blank = wait): ")
        if not raw:
            return None
        try:
            index = int(raw)
            if not 1 <= index <= len(OPTIONS[field]):
                return None
            resolved[field] = OPTIONS[field][index - 1]
        except (TypeError, ValueError):
            return None
    output_fn("Selected configuration:")
    for field in CONFIG_FIELDS:
        output_fn(f"  {field}: {resolved[field]}")
    if _safe_input(input_fn, "Confirm configuration? type yes to continue: ").lower() not in {"yes", "y"}:
        return None
    resolved["workflow_mode"] = "manual"
    resolved["selection_mode"] = "guided"
    resolved["confirmation_method"] = "user_confirmed"
    resolved["confirmed_by"] = "user"
    resolved["confirmation_timestamp"] = _now()
    resolved["configuration_source"] = {field: "user" for field in CONFIG_FIELDS}
    return resolved


def _references(config: Mapping[str, Any]) -> list[str]:
    refs = config.get("reference_images", [])
    if isinstance(refs, str):
        refs = [refs]
    return [str(item) for item in refs if str(item).strip()]


def _load_manifest(output_dir: Path) -> dict[str, Any]:
    path = output_dir / "image-generation-manifest.json"
    if not path.is_file():
        return {"schema_version": 1, "required_tool": "image2", "calls": []}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {"schema_version": 1, "required_tool": "image2", "calls": []}
    except json.JSONDecodeError:
        return {"schema_version": 1, "required_tool": "image2", "calls": []}


def _record_image_call(output_dir: Path, call: dict[str, Any]) -> None:
    manifest = _load_manifest(output_dir)
    manifest.setdefault("calls", []).append(call)
    manifest["updated_at"] = _now()
    _atomic_json(output_dir / "image-generation-manifest.json", manifest)


def _call_image2(adapter: Any, *, output_dir: Path, prompt_path: Path, reference_images: list[str], output_path: Path) -> None:
    relative_prompt = prompt_path.relative_to(output_dir).as_posix()
    relative_output = output_path.relative_to(output_dir).as_posix()
    call = {
        "tool_name": getattr(adapter, "tool_name", None),
        "model_or_tool_version": getattr(adapter, "model_or_tool_version", getattr(adapter, "version", "unknown")),
        "prompt_path": relative_prompt,
        "reference_images": reference_images,
        "output_path": relative_output,
        "timestamp": _now(),
        "success": False,
        "error": None,
        "status": "failure",
    }
    if adapter is None or getattr(adapter, "tool_name", None) != "image2":
        call["error"] = "image2 adapter is unavailable or misidentified"
        _record_image_call(output_dir, call)
        raise RuntimeError(call["error"])
    try:
        success = adapter.generate(prompt_path=prompt_path, reference_images=reference_images, output_path=output_path)
        if success is False or not output_path.is_file():
            raise RuntimeError("image2 did not create the requested output")
        call["success"] = True
        call["status"] = "success"
    except Exception as exc:
        call["error"] = str(exc)
        raise
    finally:
        _record_image_call(output_dir, call)


def _candidate_prompt(style: str, page_type: str) -> str:
    return (
        "Use image2. Learn the supplied blue template's color, typography language, whitespace, "
        "graphic vocabulary, photography treatment, and page rhythm. Do not copy source text, "
        "source slides, or exact textbox coordinates. Recompose a 16:9 {page_type} page. "
        "Interpretation: {style} Image2 owns background, scene, composition, and decoration. "
        "Leave clean regions for deterministic Chinese text, numbers, charts, and footnotes; "
        "do not render exact Chinese copy or data."
    ).format(page_type=page_type, style=style)


def _generate_candidates(output_dir: Path, config: Mapping[str, Any], image2_adapter: Any) -> None:
    references = _references(config)
    if not references:
        raise RuntimeError("style candidates require reference_images from the supplied template")
    for candidate, style in CANDIDATE_STYLES.items():
        candidate_dir = output_dir / "style-candidates" / candidate
        prompt_dir = candidate_dir / "prompts"
        candidate_dir.mkdir(parents=True, exist_ok=True)
        profile = {
            "candidate": candidate,
            "interpretation": style,
            "template_application_mode": "style-reference",
            "reference_images": references,
            "image_tool": "image2",
            "deterministic_overlays": "Chinese text, numbers, charts, labels, and footnotes",
            **CANDIDATE_PROFILES[candidate],
            "layout_principles": "recompose for current content; preserve semantic hierarchy; keep deterministic overlay regions clear",
            "prohibited_behaviors": "copy source slides; copy source text; lock source textbox coordinates; ask image2 to render exact Chinese or data",
        }
        _write_yaml_scalars(candidate_dir / "style-profile.yaml", profile)
        for page_type in CANDIDATE_PAGES:
            prompt_path = prompt_dir / f"{page_type}.txt"
            prompt_path.parent.mkdir(parents=True, exist_ok=True)
            prompt_path.write_text(_candidate_prompt(style, page_type) + "\n", encoding="utf-8")
            _call_image2(
                image2_adapter,
                output_dir=output_dir,
                prompt_path=prompt_path,
                reference_images=references,
                output_path=candidate_dir / f"{page_type}.png",
            )
    guards = _load_sibling("artifact_guards")
    errors = guards.validate_style_candidates(output_dir)
    if errors:
        raise RuntimeError("; ".join(errors))


def _write_selected_style(output_dir: Path, candidate: str) -> None:
    confirmed = _read_mapping(output_dir / "deck-config.confirmed.yaml")
    _write_yaml_scalars(output_dir / "selected-style.yaml", {
        "selected_candidate": candidate,
        "selected_by": "user",
        "confirmation_timestamp": _now(),
        "candidate_profile_path": f"style-candidates/{candidate}/style-profile.yaml",
        "template_profile": confirmed.get("template_profile", ""),
    })


def _failure_evidence(output_dir: Path, *, stage: str, error: Exception) -> Path:
    path = output_dir / "failures" / f"{stage}-{__import__('uuid').uuid4().hex[:8]}.json"
    _atomic_json(path, {"stage": stage, "error": str(error), "timestamp": _now()})
    return path


def _source_material_paths(output_dir: Path, config: Mapping[str, Any]) -> list[Path]:
    raw = config.get("source_materials", config.get("source_material", []))
    if isinstance(raw, str):
        raw = [raw]
    result = []
    for item in raw if isinstance(raw, list) else []:
        path = Path(str(item))
        candidate = path if path.is_absolute() else output_dir / path
        if candidate.is_file():
            result.append(candidate.resolve())
    return result


def _prepare_review_pack(
    output_dir: Path,
    *,
    rubric_name: str,
    reviewer_role: str,
    reviewer_model: str,
    phase: str,
    slide_count: int,
) -> tuple[Path, Path, Path]:
    existing = sorted((output_dir / "reviews").glob("round-*")) if (output_dir / "reviews").is_dir() else []
    round_number = len(existing) + 1
    round_name = f"round-{round_number:02d}"
    rubric_path = Path(__file__).resolve().parents[1] / "rubrics" / rubric_name
    isolation = _load_sibling("review_isolation")
    config = _read_mapping(output_dir / "deck-config.confirmed.yaml")
    pack_path = output_dir / "review-pack" / round_name
    isolation.ReviewPackBuilder(output_dir).build(
        pack_path,
        rubric_path=rubric_path,
        source_materials=_source_material_paths(output_dir, config),
    )
    review_dir = output_dir / "reviews" / round_name
    review_dir.mkdir(parents=True, exist_ok=False)
    request_path = review_dir / "review-request.json"
    _atomic_json(request_path, {
        "review_id": round_name,
        "artifact_version": round_name,
        "review_pack": pack_path.relative_to(output_dir).as_posix(),
        "rubric": rubric_path.relative_to(Path(__file__).resolve().parents[1]).as_posix(),
        "reviewer_role": reviewer_role,
        "reviewer_model": reviewer_model,
        "isolated_context": True,
        "read_only": True,
        "producer_private_context_included": False,
        "timestamp": _now(),
    })
    checks_path = review_dir / "deterministic-checks.json"
    _load_sibling("deterministic_checks").DeterministicCheckRunner(output_dir).run(
        phase=phase,
        slide_count=slide_count,
        report_path=checks_path,
    )
    return pack_path / "review-pack-manifest.json", request_path, checks_path


def _select_candidate(output_dir: Path, input_fn: Callable[[str], str], output_fn: Callable[[str], None]) -> str | None:
    guards = _load_sibling("artifact_guards")
    errors = guards.validate_style_candidates(output_dir)
    if errors:
        raise RuntimeError("; ".join(errors))
    output_fn("三套 image2 风格候选已生成，请由用户选择；系统不会默认选择 Candidate A。")
    for index, (candidate, style) in enumerate(CANDIDATE_STYLES.items(), start=1):
        output_fn(f"  {index}) {candidate}: {style}")
    raw = _safe_input(input_fn, "Select candidate by number (blank = wait): ")
    if not raw:
        return None
    try:
        index = int(raw)
        candidate = tuple(CANDIDATE_STYLES)[index - 1]
    except (ValueError, IndexError):
        raise RuntimeError("invalid candidate selection")
    _write_selected_style(output_dir, candidate)
    return candidate


def _spec_references(payload: Mapping[str, Any]) -> list[str]:
    refs = payload.get("reference_images", [])
    if isinstance(refs, list):
        return [str(item) for item in refs]
    if isinstance(refs, str):
        try:
            decoded = json.loads(refs)
            if isinstance(decoded, list):
                return [str(item) for item in decoded]
        except json.JSONDecodeError:
            pass
        return [refs]
    return []


def _generate_slide_images(output_dir: Path, *, image2_adapter: Any, final: bool) -> int:
    guards = _load_sibling("artifact_guards")
    if not final:
        guards.assert_preview_generation_allowed(output_dir)
    specs, errors = guards.validate_slide_specs(output_dir)
    if errors:
        raise RuntimeError("; ".join(errors))
    destination = output_dir / ("final-images" if final else "preview-images")
    destination.mkdir(parents=True, exist_ok=True)
    for index, spec in enumerate(specs, start=1):
        payload = guards.read_mapping(spec)
        prompt_path = spec.with_suffix(".image-prompt.txt")
        prompt = "\n\n".join([
            str(payload["style_reference_prompt"]),
            str(payload["image_prompt"]),
            f"Dominant visual: {payload['dominant_visual']}",
            "Do not render exact Chinese, numbers, charts, labels, or footnotes. Deterministic code overlays those elements.",
        ])
        prompt_path.write_text(prompt + "\n", encoding="utf-8")
        _call_image2(
            image2_adapter,
            output_dir=output_dir,
            prompt_path=prompt_path,
            reference_images=_spec_references(payload),
            output_path=destination / f"slide-{index:02d}.png",
        )
    if final:
        _atomic_json(output_dir / "final-images-qa.json", {"status": "pass", "image_count": len(specs), "checked_at": _now()})
    return len(specs)


def _assemble_and_prepare_final_review(
    output_dir: Path,
    *,
    router: Any,
    presentation_adapter: Any,
    available_models: Iterable[str] | None,
    slide_count: int,
) -> tuple[Path, Path, Path]:
    presentation = _load_sibling("presentation_guard")
    presentation.assert_assembly_ready(output_dir, slide_count=slide_count)
    if presentation_adapter is None or getattr(presentation_adapter, "tool_name", None) != "presentation":
        raise RuntimeError("presentation adapter is unavailable")
    presentation_adapter.assemble(
        output_pptx=output_dir / "presentation.pptx",
        final_images=[output_dir / "final-images" / f"slide-{i:02d}.png" for i in range(1, slide_count + 1)],
        speaker_notes=[output_dir / "speaker-notes" / f"slide-{i:02d}.md" for i in range(1, slide_count + 1)],
        slide_size="16:9",
        allowed_operations=("create_blank_deck", "insert_full_slide_image", "write_speaker_note", "save", "reopen_and_verify_notes"),
    )
    errors = presentation.validate_presentation(
        output_dir / "presentation.pptx",
        output_dir / "speaker-notes",
        slide_count=slide_count,
    )
    if errors:
        raise RuntimeError("; ".join(errors))
    final_reviewer_decision = router.route(
        "final_reviewer",
        complexity="critical",
        available_models=available_models,
    )
    return _prepare_review_pack(
        output_dir,
        rubric_name="final-delivery-rubric.yaml",
        reviewer_role="final_reviewer",
        reviewer_model=final_reviewer_decision.model,
        phase="final",
        slide_count=slide_count,
    )


def run_once(
    output_dir: Path,
    *,
    config: Mapping[str, Any] | None = None,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
    image2_adapter: Any = None,
    presentation_adapter: Any = None,
    available_models: Iterable[str] | None = None,
) -> RunResult:
    """Advance from the current persisted state to at most the next human Gate."""
    output_dir = Path(output_dir).resolve()
    supplied = dict(config) if config is not None else _read_mapping(output_dir / "deck-config.yaml")
    explicit = set(config.keys()) if config is not None else set()
    workflow_mode, selection_mode = resolve_modes(supplied, explicit)
    supplied["workflow_mode"] = workflow_mode
    supplied["selection_mode"] = selection_mode
    for field, value in DEFAULT_CONFIG.items():
        supplied.setdefault(field, value)
    machine = WorkflowStateMachine(output_dir, workflow_mode=workflow_mode, selection_mode=selection_mode)
    state = machine.load()

    try:
        router_module = _load_sibling("model_router")
        router = router_module.ModelRouter(
            Path(__file__).resolve().parents[1] / "agents" / "model-routing.json",
            audit_manifest=output_dir / "model-routing-manifest.json",
        )
        router.route("orchestrator", available_models=available_models)
        if state.build_status == "initialized":
            router.route("low_cost_worker", available_models=available_models)
            pending_path = _write_pending_config(output_dir, supplied)
            _show_configuration(supplied, output_fn)
            _write_configuration_report(output_dir, supplied)
            report_path = output_dir / "config-selection-report.md"
            state = machine.transition(
                "awaiting_configuration",
                stage="configuration",
                actor="orchestrator",
                evidence_files=[pending_path, report_path, output_dir / "model-routing-manifest.json"],
                message="waiting for user configuration confirmation",
            )
            return RunResult(state.build_status, state.message, state)

        if state.build_status == "awaiting_configuration":
            if workflow_mode == "auto" and selection_mode == "direct":
                missing = [field for field in CONFIG_FIELDS if supplied.get(field) in (None, "")]
                if missing:
                    raise RuntimeError("auto/direct is missing explicit fields: " + ", ".join(missing))
                supplied["confirmation_method"] = "auto_inference"
                supplied["confirmation_timestamp"] = _now()
                confirmed_path = output_dir / "deck-config.confirmed.yaml"
                _write_yaml_scalars(confirmed_path, supplied)
                state = machine.transition(
                    "generating_slide_specs",
                    stage="configuration",
                    actor="orchestrator",
                    evidence_files=[confirmed_path],
                    message="auto/direct configuration recorded",
                )
                return RunResult(state.build_status, state.message, state)

            resolved = _collect_configuration(supplied, input_fn, output_fn)
            if resolved is None:
                _write_configuration_report(output_dir, supplied)
                state = machine.touch(message="waiting for user configuration confirmation")
                return RunResult(state.build_status, state.message, state)
            confirmed_path = output_dir / "deck-config.confirmed.yaml"
            _write_yaml_scalars(confirmed_path, resolved)
            router.route("producer", complexity="high", available_models=available_models)
            state = machine.transition(
                "generating_style_candidates",
                stage="style-candidates",
                actor="orchestrator",
                evidence_files=[confirmed_path],
                message="configuration confirmed by user",
            )
            _generate_candidates(output_dir, resolved, image2_adapter)
            manifest_path = output_dir / "image-generation-manifest.json"
            state = machine.transition(
                "awaiting_style_selection",
                stage="style-selection",
                actor="orchestrator",
                evidence_files=[manifest_path],
                message="three image2 candidates are ready for user selection",
            )
            return RunResult(state.build_status, state.message, state)

        if state.build_status == "generating_style_candidates":
            router.route("producer", complexity="high", available_models=available_models)
            confirmed = _read_mapping(output_dir / "deck-config.confirmed.yaml")
            _generate_candidates(output_dir, confirmed, image2_adapter)
            state = machine.transition(
                "awaiting_style_selection",
                stage="style-selection",
                actor="orchestrator",
                evidence_files=[output_dir / "image-generation-manifest.json"],
                message="three image2 candidates are ready for user selection",
            )
            return RunResult(state.build_status, state.message, state)

        if state.build_status == "awaiting_style_selection":
            if _select_candidate(output_dir, input_fn, output_fn) is None:
                state = machine.touch(message="waiting for user style selection")
                return RunResult(state.build_status, state.message, state)
            selected_path = output_dir / "selected-style.yaml"
            router.route("producer", complexity="high", available_models=available_models)
            router.route("slide_worker", available_models=available_models)
            state = machine.transition(
                "generating_slide_specs",
                stage="slide-specs",
                actor="orchestrator",
                evidence_files=[selected_path],
                message="user selected style; slide specs are authorized",
            )
            guards = _load_sibling("artifact_guards")
            specs, errors = guards.validate_slide_specs(output_dir)
            if errors:
                raise RuntimeError("; ".join(errors))
            state = machine.transition(
                "generating_previews",
                stage="previews",
                actor="orchestrator",
                evidence_files=specs,
                message="slide specs validated",
            )
            _generate_slide_images(output_dir, image2_adapter=image2_adapter, final=False)
            preview_files = sorted((output_dir / "preview-images").glob("slide-*.png"))
            reviewer_decision = router.route("reviewer", available_models=available_models)
            pack_manifest, review_request, checks_path = _prepare_review_pack(
                output_dir,
                rubric_name="preview-rubric.yaml",
                reviewer_role="reviewer",
                reviewer_model=reviewer_decision.model,
                phase="preview",
                slide_count=len(preview_files),
            )
            state = machine.transition(
                "reviewing",
                stage="preview-review",
                actor="orchestrator",
                evidence_files=[*preview_files, pack_manifest, review_request, checks_path],
                message="previews generated; isolated Reviewer evaluation required",
            )
            return RunResult(state.build_status, state.message, state)

        if state.build_status == "generating_slide_specs":
            guards = _load_sibling("artifact_guards")
            specs, errors = guards.validate_slide_specs(output_dir)
            if errors:
                raise RuntimeError("; ".join(errors))
            state = machine.transition(
                "generating_previews",
                stage="previews",
                actor="orchestrator",
                evidence_files=specs,
                message="slide specs validated",
            )
            return RunResult(state.build_status, state.message, state)

        if state.build_status == "generating_previews":
            slide_count = _generate_slide_images(output_dir, image2_adapter=image2_adapter, final=False)
            preview_files = sorted((output_dir / "preview-images").glob("slide-*.png"))
            reviewer_decision = router.route("reviewer", available_models=available_models)
            pack_manifest, review_request, checks_path = _prepare_review_pack(
                output_dir,
                rubric_name="preview-rubric.yaml",
                reviewer_role="reviewer",
                reviewer_model=reviewer_decision.model,
                phase="preview",
                slide_count=slide_count,
            )
            state = machine.transition(
                "reviewing",
                stage="preview-review",
                actor="orchestrator",
                evidence_files=[*preview_files, pack_manifest, review_request, checks_path],
                message="previews generated; isolated Reviewer evaluation required",
            )
            return RunResult(state.build_status, state.message, state)

        if state.build_status == "reviewing":
            review_dirs = sorted((output_dir / "reviews").glob("round-*")) if (output_dir / "reviews").is_dir() else []
            pending = next(
                (
                    directory for directory in review_dirs
                    if (directory / "evaluation.json").is_file() and not (directory / "gate-decision.json").exists()
                ),
                None,
            )
            if pending is None:
                state = machine.touch(message="waiting for an isolated read-only Reviewer evaluation")
                return RunResult(state.build_status, state.message, state)
            evaluation_path = pending / "evaluation.json"
            checks_path = pending / "deterministic-checks.json"
            checks = _read_mapping(checks_path)
            deterministic_pass = checks.get("status") == "pass"
            rubric_name = "final-delivery-rubric.yaml" if state.last_stage == "final-review" else "preview-rubric.yaml"
            rubric_path = Path(__file__).resolve().parents[1] / "rubrics" / rubric_name
            review_gate = _load_sibling("review_gate").DeterministicReviewGate(rubric_path)
            decision_path = pending / "gate-decision.json"
            decision = review_gate.evaluate_file(
                evaluation_path,
                deterministic_checks_passed=deterministic_pass,
                decision_path=decision_path,
            )
            if decision.passed:
                next_status = "final_qa" if state.last_stage == "final-review" else "awaiting_preview_approval"
                next_stage = "final-qa" if next_status == "final_qa" else "preview-approval"
                state = machine.transition(
                    next_status,
                    stage=next_stage,
                    actor="orchestrator",
                    evidence_files=[evaluation_path, checks_path, decision_path],
                    message="deterministic review Gate passed",
                )
                return RunResult(state.build_status, state.message, state)
            cycle = _load_sibling("review_cycle").RevisionController(output_dir, machine, max_rounds=2)
            issues = decision.valid_issues or [
                {"id": f"CRITICAL-{index:02d}", "critical_failure": failure}
                for index, failure in enumerate(decision.critical_failures, start=1)
            ] or [{"id": "REVIEW-GATE", "validation_errors": decision.validation_errors}]
            review_phase = "final" if state.last_stage == "final-review" else "preview"
            state = cycle.record_failure(
                round_number=state.revision_round + 1,
                issues=issues,
                review_phase=review_phase,
            )
            return RunResult(state.build_status, state.message, state)

        if state.build_status == "revising":
            issue_path = output_dir / "artifacts" / f"round-{state.revision_round:02d}" / "structured-issues.json"
            issue_payload = _read_mapping(issue_path)
            if not issue_payload:
                raise RuntimeError("revising requires immutable structured issues")
            router.route("producer", complexity="high", available_models=available_models)
            ready_path = issue_path.with_name("revision-ready.json")
            if not ready_path.is_file():
                state = machine.touch(message="waiting for Producer revision evidence")
                return RunResult(state.build_status, state.message, state)
            ready = _read_mapping(ready_path)
            if ready.get("revised_by") != "producer":
                raise RuntimeError("revision-ready.json must record revised_by: producer")
            review_phase = str(issue_payload.get("review_phase", "preview"))
            next_status = "generating_final_images" if review_phase == "final" else "generating_previews"
            state = machine.transition(
                next_status,
                stage=f"{review_phase}-regeneration",
                actor="orchestrator",
                evidence_files=[issue_path, ready_path],
                message="Producer revision accepted; regeneration authorized",
            )
            return RunResult(state.build_status, state.message, state)

        if state.build_status == "awaiting_preview_approval":
            approval = _safe_input(input_fn, "Approve previews? type yes to continue: ").lower()
            if approval not in {"yes", "y"}:
                state = machine.touch(message="waiting for user preview approval")
                return RunResult(state.build_status, state.message, state)
            approval_path = output_dir / "preview-approval.json"
            _atomic_json(approval_path, {"approved_by": "user", "timestamp": _now()})
            state = machine.transition(
                "generating_final_images",
                stage="final-images",
                actor="orchestrator",
                evidence_files=[approval_path],
                message="previews approved by user",
            )
            slide_count = _generate_slide_images(output_dir, image2_adapter=image2_adapter, final=True)
            state = machine.transition(
                "assembling_ppt",
                stage="ppt-assembly",
                actor="orchestrator",
                evidence_files=[output_dir / "final-images-qa.json"],
                message="final images passed QA",
            )
            pack_manifest, review_request, checks_path = _assemble_and_prepare_final_review(
                output_dir,
                router=router,
                presentation_adapter=presentation_adapter,
                available_models=available_models,
                slide_count=slide_count,
            )
            state = machine.transition(
                "reviewing",
                stage="final-review",
                actor="orchestrator",
                evidence_files=[output_dir / "presentation.pptx", pack_manifest, review_request, checks_path],
                message="presentation assembled; isolated final Reviewer evaluation required",
            )
            return RunResult(state.build_status, state.message, state)

        if state.build_status == "generating_final_images":
            slide_count = _generate_slide_images(output_dir, image2_adapter=image2_adapter, final=True)
            state = machine.transition(
                "assembling_ppt",
                stage="ppt-assembly",
                actor="orchestrator",
                evidence_files=[output_dir / "final-images-qa.json"],
                message="final images passed QA",
            )
            return RunResult(state.build_status, state.message, state)

        if state.build_status == "assembling_ppt":
            slide_count = len(sorted((output_dir / "slide-specs").glob("slide-*.yaml")))
            pack_manifest, review_request, checks_path = _assemble_and_prepare_final_review(
                output_dir,
                router=router,
                presentation_adapter=presentation_adapter,
                available_models=available_models,
                slide_count=slide_count,
            )
            state = machine.transition(
                "reviewing",
                stage="final-review",
                actor="orchestrator",
                evidence_files=[output_dir / "presentation.pptx", pack_manifest, review_request, checks_path],
                message="presentation assembled; isolated final Reviewer evaluation required",
            )
            return RunResult(state.build_status, state.message, state)

        if state.build_status == "final_qa":
            decisions = sorted((output_dir / "reviews").glob("round-*/gate-decision.json"))
            if not decisions:
                raise RuntimeError("final_qa requires a deterministic gate-decision.json")
            latest = json.loads(decisions[-1].read_text(encoding="utf-8"))
            if latest.get("passed") is not True or latest.get("deterministic_checks_passed") is not True:
                raise RuntimeError("final deterministic review Gate did not pass")
            state = machine.transition(
                "completed",
                stage="completed",
                actor="orchestrator",
                evidence_files=[decisions[-1], output_dir / "presentation.pptx"],
                message="all human, reviewer, and deterministic Gates passed",
            )
            return RunResult(state.build_status, state.message, state)

        return RunResult(state.build_status, state.message, state)
    except Exception as exc:
        evidence = _failure_evidence(output_dir, stage=state.last_stage, error=exc)
        state = machine.fail(
            stage=state.last_stage,
            actor="orchestrator",
            evidence_files=[evidence],
            message=str(exc),
        )
        return RunResult(state.build_status, state.message, state)


__all__ = ["MultiAwaitTransitionError", "RunResult", "WorkflowStateMachine", "resolve_modes", "run_once"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="Task output directory containing deck-config.yaml")
    args = parser.parse_args(argv)
    result = run_once(args.output)
    print(f"build_status: {result.status}")
    print(result.message)
    return 0 if result.status in {"completed"} or result.status.startswith("awaiting_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
