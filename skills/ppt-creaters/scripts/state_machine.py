"""Persistent audited workflow state controlled only by the Orchestrator."""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable


WORKFLOW_STATES = (
    "initialized",
    "awaiting_configuration",
    "generating_style_candidates",
    "awaiting_style_selection",
    "generating_slide_specs",
    "generating_previews",
    "awaiting_preview_approval",
    "generating_final_images",
    "assembling_ppt",
    "reviewing",
    "revising",
    "awaiting_human_review",
    "final_qa",
    "completed",
    "failed",
)
AWAITING_STATES = {state for state in WORKFLOW_STATES if state.startswith("awaiting_")}
EDGES = {
    "initialized": {"awaiting_configuration", "generating_slide_specs", "failed"},
    "awaiting_configuration": {"generating_style_candidates", "generating_slide_specs", "failed"},
    "generating_style_candidates": {"awaiting_style_selection", "failed"},
    "awaiting_style_selection": {"generating_slide_specs", "failed"},
    "generating_slide_specs": {"generating_previews", "failed"},
    "generating_previews": {"reviewing", "awaiting_preview_approval", "failed"},
    "awaiting_preview_approval": {"generating_final_images", "failed"},
    "generating_final_images": {"assembling_ppt", "failed"},
    "assembling_ppt": {"reviewing", "final_qa", "failed"},
    "reviewing": {"awaiting_preview_approval", "revising", "awaiting_human_review", "final_qa", "failed"},
    "revising": {"generating_previews", "generating_final_images", "reviewing", "awaiting_human_review", "failed"},
    "awaiting_human_review": {"revising", "final_qa", "failed"},
    "final_qa": {"completed", "failed"},
    "completed": set(),
    "failed": set(),
}


class StateMachineError(RuntimeError):
    pass


class InvalidTransitionError(StateMachineError):
    pass


class MultiAwaitTransitionError(StateMachineError):
    pass


class ActorPermissionError(StateMachineError):
    pass


class MissingEvidenceError(StateMachineError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, path)


def _atomic_yaml(path: Path, payload: dict[str, Any]) -> None:
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
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    os.replace(temp, path)


def _read_yaml_mapping(path: Path) -> dict[str, Any]:
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


class WorkflowState:
    def __init__(
        self,
        *,
        build_status: str,
        workflow_mode: str,
        selection_mode: str,
        last_stage: str,
        run_id: str,
        updated_at: str,
        transition_history: list[dict[str, Any]] | None = None,
        message: str = "",
        revision_round: int = 0,
        artifact_version: str = "round-00",
    ):
        self.build_status = build_status
        self.workflow_mode = workflow_mode
        self.selection_mode = selection_mode
        self.last_stage = last_stage
        self.run_id = run_id
        self.updated_at = updated_at
        self.transition_history = list(transition_history or [])
        self.message = message
        self.revision_round = revision_round
        self.artifact_version = artifact_version

    def as_dict(self) -> dict[str, Any]:
        return {
            "build_status": self.build_status,
            "workflow_mode": self.workflow_mode,
            "selection_mode": self.selection_mode,
            "last_stage": self.last_stage,
            "run_id": self.run_id,
            "updated_at": self.updated_at,
            "transition_history": self.transition_history,
            "message": self.message,
            "revision_round": self.revision_round,
            "artifact_version": self.artifact_version,
        }


class WorkflowStateMachine:
    def __init__(self, output_dir: Path, *, workflow_mode: str = "manual", selection_mode: str = "guided"):
        self.output_dir = Path(output_dir).resolve()
        self.state_path = self.output_dir / "build-state.yaml"
        self.legacy_state_path = self.output_dir / "build-status.json"
        self.workflow_mode = workflow_mode
        self.selection_mode = selection_mode

    def _initial(self) -> WorkflowState:
        return WorkflowState(
            build_status="initialized",
            workflow_mode=self.workflow_mode,
            selection_mode=self.selection_mode,
            last_stage="initialization",
            run_id=uuid.uuid4().hex,
            updated_at=_now(),
        )

    def load(self) -> WorkflowState:
        if not self.state_path.is_file():
            return self.save(self._initial())
        try:
            payload = _read_yaml_mapping(self.state_path)
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise StateMachineError(f"invalid persisted build state: {self.state_path}: {exc}") from exc
        if not isinstance(payload, dict) or payload.get("build_status") not in WORKFLOW_STATES:
            raise StateMachineError(f"invalid persisted build state: {self.state_path}")
        return WorkflowState(
            build_status=str(payload["build_status"]),
            workflow_mode=str(payload.get("workflow_mode", self.workflow_mode)),
            selection_mode=str(payload.get("selection_mode", self.selection_mode)),
            last_stage=str(payload.get("last_stage", "unknown")),
            run_id=str(payload.get("run_id", uuid.uuid4().hex)),
            updated_at=str(payload.get("updated_at", _now())),
            transition_history=list(payload.get("transition_history", [])),
            message=str(payload.get("message", "")),
            revision_round=int(payload.get("revision_round", 0)),
            artifact_version=str(payload.get("artifact_version", "round-00")),
        )

    def save(self, state: WorkflowState) -> WorkflowState:
        _atomic_yaml(self.state_path, state.as_dict())
        _atomic_json(self.legacy_state_path, state.as_dict())
        return state

    def touch(self, *, message: str) -> WorkflowState:
        state = self.load()
        state.message = message
        state.updated_at = _now()
        return self.save(state)

    def _evidence_paths(self, evidence_files: Iterable[Path | str]) -> list[str]:
        values = [Path(item) for item in evidence_files]
        if not values:
            raise MissingEvidenceError("every state transition requires at least one evidence file")
        rendered: list[str] = []
        for path in values:
            resolved = path if path.is_absolute() else self.output_dir / path
            if not resolved.is_file():
                raise MissingEvidenceError(f"state transition evidence does not exist: {resolved}")
            try:
                rendered.append(resolved.resolve().relative_to(self.output_dir.resolve()).as_posix())
            except ValueError:
                rendered.append(str(resolved.resolve()))
        return rendered

    def _validate_completion_evidence(self, evidence_files: Iterable[Path | str]) -> None:
        candidates = []
        for item in evidence_files:
            path = Path(item)
            resolved = path if path.is_absolute() else self.output_dir / path
            if resolved.name == "gate-decision.json" and resolved.is_file():
                candidates.append(resolved)
        if not candidates:
            raise MissingEvidenceError("completed requires deterministic gate-decision.json evidence")
        try:
            decision = json.loads(candidates[-1].read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise MissingEvidenceError(f"invalid completion gate decision: {exc}") from exc
        if decision.get("passed") is not True or decision.get("deterministic_checks_passed") is not True:
            raise ActorPermissionError("completed requires a passed deterministic Gate decision")

    def transition(
        self,
        next_status: str,
        *,
        stage: str,
        actor: str,
        evidence_files: Iterable[Path | str],
        message: str = "",
    ) -> WorkflowState:
        state = self.load()
        if actor != "orchestrator":
            raise ActorPermissionError(f"only orchestrator may transition workflow state; actor={actor}")
        if next_status not in WORKFLOW_STATES:
            raise InvalidTransitionError(f"unknown workflow state: {next_status}")
        if next_status not in EDGES.get(state.build_status, set()):
            raise InvalidTransitionError(f"cannot transition {state.build_status} -> {next_status}")
        evidence_items = list(evidence_files)
        if next_status == "completed":
            self._validate_completion_evidence(evidence_items)
        evidence = self._evidence_paths(evidence_items)
        state.transition_history.append({
            "from": state.build_status,
            "to": next_status,
            "stage": stage,
            "timestamp": _now(),
            "actor": actor,
            "evidence_files": evidence,
            "message": message,
        })
        state.build_status = next_status
        state.last_stage = stage
        state.updated_at = _now()
        state.message = message
        return self.save(state)

    def fail(self, *, stage: str, actor: str, evidence_files: Iterable[Path | str], message: str) -> WorkflowState:
        state = self.load()
        if state.build_status == "failed":
            return self.touch(message=message)
        return self.transition(
            "failed",
            stage=stage,
            actor=actor,
            evidence_files=evidence_files,
            message=message,
        )

    def run_once(self, stage_fn: Callable[[WorkflowState], Any]) -> WorkflowState:
        """Apply a declared transition sequence and reject two human Gates in one run."""
        state = self.load()
        outcome = stage_fn(state)
        transitions = outcome if isinstance(outcome, (list, tuple)) else [outcome]
        if isinstance(outcome, tuple) and len(outcome) == 2 and isinstance(outcome[0], str):
            transitions = [outcome]
        awaiting_entered = 0
        current = state
        for item in transitions:
            if not isinstance(item, dict):
                raise StateMachineError("audited run_once transitions must be dictionaries")
            next_status = str(item["status"])
            if next_status in AWAITING_STATES:
                awaiting_entered += 1
                if awaiting_entered > 1:
                    violation = self.output_dir / "gate-violation.json"
                    violation.write_text(
                        json.dumps({"error": "one execution crossed two awaiting states", "timestamp": _now()}, indent=2) + "\n",
                        encoding="utf-8",
                    )
                    self.fail(
                        stage=str(item.get("stage", current.last_stage)),
                        actor="orchestrator",
                        evidence_files=[violation],
                        message="one execution crossed two awaiting states",
                    )
                    raise MultiAwaitTransitionError("one execution cannot enter two future awaiting states")
            current = self.transition(
                next_status,
                stage=str(item.get("stage", current.last_stage)),
                actor=str(item.get("actor", "orchestrator")),
                evidence_files=item.get("evidence_files", ()),
                message=str(item.get("message", "")),
            )
        return current
