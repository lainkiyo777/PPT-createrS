"""Freeze reviewer inputs and enforce Producer/Reviewer capability boundaries."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


class ReviewIsolationError(RuntimeError):
    pass


class PermissionDenied(ReviewIsolationError):
    pass


class ContaminatedContextError(ReviewIsolationError):
    pass


class ReviewPackError(ReviewIsolationError):
    pass


FORBIDDEN_CONTEXT_TOKENS = (
    "producer.log",
    "producer-logs",
    "producer-conversation",
    "producer-self-assessment",
    "producer-model",
    "producer-summary",
)
MUTATING_REVIEWER_TOOLS = {"image2", "presentation", "pptx", "filesystem_write", "apply_patch"}


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_reviewer_context(review_pack: Path, context_paths: Iterable[Path]) -> list[Path]:
    root = Path(review_pack).resolve()
    validated: list[Path] = []
    for candidate in context_paths:
        resolved = Path(candidate).resolve()
        lowered = resolved.as_posix().lower()
        if not _is_relative_to(resolved, root) or any(token in lowered for token in FORBIDDEN_CONTEXT_TOKENS):
            raise ContaminatedContextError(
                f"reviewer context must contain review-pack artifacts only: {resolved}"
            )
        validated.append(resolved)
    return validated


class ReviewerSession:
    """Read-only capability facade exposed to reviewer models."""

    def __init__(self, review_pack: Path):
        self.review_pack = Path(review_pack).resolve()

    def read(self, relative_path: str) -> bytes:
        target = (self.review_pack / relative_path).resolve()
        validate_reviewer_context(self.review_pack, [target])
        return target.read_bytes()

    def list_files(self) -> list[str]:
        return sorted(
            path.relative_to(self.review_pack).as_posix()
            for path in self.review_pack.rglob("*")
            if path.is_file()
        )

    def write(self, relative_path: str, content: bytes | str) -> None:
        raise PermissionDenied("reviewer sessions are read-only")

    def call_tool(self, tool_name: str, **_: Any) -> None:
        if tool_name in MUTATING_REVIEWER_TOOLS:
            raise PermissionDenied(f"reviewer cannot call mutating tool {tool_name}")
        raise PermissionDenied(f"reviewer tool capability is not declared: {tool_name}")


class ArtifactAccessController:
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir).resolve()

    def assert_write_allowed(self, actor: str, target: Path) -> None:
        resolved = Path(target).resolve()
        relative = resolved.relative_to(self.output_dir).as_posix() if _is_relative_to(resolved, self.output_dir) else ""
        if actor in {"reviewer", "final_reviewer"}:
            raise PermissionDenied(f"{actor} is read-only")
        if actor in {"producer", "slide_worker", "low_cost_worker"} and relative.startswith("reviews/") and relative.endswith("/evaluation.json"):
            raise PermissionDenied(f"{actor} cannot modify reviewer evaluation files")
        if actor != "orchestrator" and relative == "build-state.yaml":
            raise PermissionDenied(f"{actor} cannot modify persistent workflow state")


class ReviewPackBuilder:
    """Create a versioned, hash-manifested pack with no Producer-private context."""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)

    def build(
        self,
        review_pack: Path,
        *,
        rubric_path: Path,
        source_materials: Iterable[Path] = (),
    ) -> Path:
        destination = Path(review_pack)
        if destination.exists():
            raise ReviewPackError(f"review pack already exists and is immutable: {destination}")
        destination.mkdir(parents=True)

        file_map = {
            "user-brief.md": self.output_dir / "user-brief.md",
            "deck-config.confirmed.yaml": self.output_dir / "deck-config.confirmed.yaml",
            "selected-style.yaml": self.output_dir / "selected-style.yaml",
            "overview.png": self.output_dir / "overview" / "overview.png",
            "metrics.json": self.output_dir / "data" / "metrics.json",
            "presentation.pptx": self.output_dir / "presentation.pptx",
        }
        for relative, source in file_map.items():
            if source.is_file():
                target = destination / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
        shutil.copy2(rubric_path, destination / "rubric.yaml")

        for directory_name in ("slide-specs", "preview-images", "speaker-notes"):
            source_dir = self.output_dir / directory_name
            if source_dir.is_dir():
                shutil.copytree(source_dir, destination / directory_name)
        source_root = destination / "source-materials"
        for source in source_materials:
            source_path = Path(source)
            if source_path.is_file():
                source_root.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, source_root / source_path.name)

        manifest_entries = []
        for path in sorted(destination.rglob("*")):
            if path.is_file():
                manifest_entries.append({
                    "path": path.relative_to(destination).as_posix(),
                    "sha256": _sha256(path),
                    "size": path.stat().st_size,
                })
        manifest = {
            "schema_version": 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "isolated_context": True,
            "producer_private_context_included": False,
            "files": manifest_entries,
        }
        (destination / "review-pack-manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        for path in destination.rglob("*"):
            if path.is_file():
                try:
                    path.chmod(stat.S_IREAD)
                except OSError:
                    pass
        return destination


class ReviewSubmissionStore:
    """Host-side writer; reviewer returns JSON but never receives filesystem write access."""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.access = ArtifactAccessController(output_dir)

    def submit(self, payload: dict[str, Any], *, round_number: int, actor: str = "orchestrator") -> Path:
        if actor != "orchestrator":
            raise PermissionDenied("only orchestrator may persist a reviewer response")
        path = self.output_dir / "reviews" / f"round-{round_number:02d}" / "evaluation.json"
        self.access.assert_write_allowed(actor, path)
        if path.exists():
            raise PermissionDenied(f"evaluation is append-only and already exists: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path
