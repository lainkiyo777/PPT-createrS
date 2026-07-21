"""Bounded Producer-Reviewer revision control with versioned artifacts."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


class RevisionCycleError(RuntimeError):
    pass


class RevisionController:
    def __init__(self, output_dir: Path, state_machine: Any, *, max_rounds: int = 2):
        if max_rounds < 1:
            raise ValueError("max_rounds must be positive")
        self.output_dir = Path(output_dir)
        self.machine = state_machine
        self.max_rounds = max_rounds

    def record_failure(
        self,
        *,
        round_number: int,
        issues: Iterable[dict[str, Any]],
        review_phase: str = "preview",
    ):
        if not 1 <= round_number <= self.max_rounds:
            raise RevisionCycleError(f"review round must be within 1..{self.max_rounds}")
        if review_phase not in {"preview", "final"}:
            raise RevisionCycleError(f"unknown review phase: {review_phase}")
        artifact_dir = self.output_dir / "artifacts" / f"round-{round_number:02d}"
        if artifact_dir.exists():
            raise RevisionCycleError(f"artifact round is immutable and already exists: {artifact_dir}")
        artifact_dir.mkdir(parents=True)
        issue_payload = {
            "round": round_number,
            "artifact_version": f"round-{round_number:02d}",
            "review_phase": review_phase,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "issues": list(issues),
        }
        issue_path = artifact_dir / "structured-issues.json"
        issue_path.write_text(json.dumps(issue_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        if round_number < self.max_rounds:
            state = self.machine.transition(
                "revising",
                stage=f"{review_phase}-revision",
                actor="orchestrator",
                evidence_files=[issue_path],
                message=f"review round {round_number} failed; structured issues sent to Producer",
            )
        else:
            state = self.machine.transition(
                "awaiting_human_review",
                stage="human-review",
                actor="orchestrator",
                evidence_files=[issue_path],
                message=f"{self.max_rounds} automatic revision rounds failed",
            )
        state.revision_round = round_number
        state.artifact_version = f"round-{round_number:02d}"
        return self.machine.save(state)
