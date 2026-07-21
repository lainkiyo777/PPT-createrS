"""Auditable role-to-model routing for the PPT production system."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


class RoutingError(RuntimeError):
    pass


class UnknownRoleError(RoutingError):
    pass


class ModelUnavailableError(RoutingError):
    pass


class RoutingDecision:
    def __init__(self, *, role: str, model: str, requested_model: str, reason: str, fallback_used: bool):
        self.role = role
        self.model = model
        self.requested_model = requested_model
        self.reason = reason
        self.fallback_used = fallback_used

    def as_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "model": self.model,
            "requested_model": self.requested_model,
            "reason": self.reason,
            "fallback_used": self.fallback_used,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


class ModelRouter:
    def __init__(self, config_path: Path, *, audit_manifest: Path | None = None):
        self.config_path = Path(config_path)
        self.audit_manifest = Path(audit_manifest) if audit_manifest else None
        try:
            self.config = json.loads(self.config_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise RoutingError(f"invalid model routing config: {self.config_path}: {exc}") from exc
        if not isinstance(self.config.get("agents"), dict):
            raise RoutingError("model routing config must contain an agents object")

    def role_config(self, role: str) -> dict[str, Any]:
        config = self.config["agents"].get(role)
        if not isinstance(config, dict):
            raise UnknownRoleError(f"unknown model role: {role}")
        return config

    def route(
        self,
        role: str,
        *,
        complexity: str = "normal",
        available_models: Iterable[str] | None = None,
    ) -> RoutingDecision:
        config = self.role_config(role)
        requested = str(config["model"])
        reason = "configured primary model"
        selected = requested
        fallback_used = False
        if role == "slide_worker" and complexity in {"high", "critical"}:
            selected = str(config.get("escalation_model", requested))
            reason = f"{complexity} complexity requires escalation_model"
            fallback_used = selected != requested

        available = set(available_models) if available_models is not None else None
        if available is not None and selected not in available:
            fallback = config.get("fallback_model")
            if fallback and str(fallback) in available:
                selected = str(fallback)
                reason = f"configured model unavailable; used explicit fallback_model {selected}"
                fallback_used = True
            else:
                raise ModelUnavailableError(
                    f"role {role} requires {selected}; no declared available fallback exists"
                )

        decision = RoutingDecision(
            role=role,
            model=selected,
            requested_model=requested,
            reason=reason,
            fallback_used=fallback_used,
        )
        if self.audit_manifest:
            self._append_audit(decision)
        return decision

    def _append_audit(self, decision: RoutingDecision) -> None:
        path = self.audit_manifest
        payload = {"schema_version": 1, "routing_decisions": []}
        if path.is_file():
            try:
                existing = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(existing, dict):
                    payload = existing
            except (OSError, UnicodeError, json.JSONDecodeError):
                pass
        payload.setdefault("routing_decisions", []).append(decision.as_dict())
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_suffix(path.suffix + ".tmp")
        temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(temp, path)
