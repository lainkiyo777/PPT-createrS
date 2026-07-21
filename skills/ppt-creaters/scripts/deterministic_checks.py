"""Aggregate non-generative checks into the only review Gate input accepted by code."""

from __future__ import annotations

import importlib.util
import json
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _load_sibling(name: str):
    path = Path(__file__).with_name(f"{name}.py")
    spec = importlib.util.spec_from_file_location(f"ppt_creaters_checks_{name}", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _mapping(path: Path) -> dict[str, Any]:
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
                value = value.strip()
                try:
                    result[key.strip()] = json.loads(value)
                except json.JSONDecodeError:
                    result[key.strip()] = value.strip("\"'")
        return result


def _png_size(path: Path) -> tuple[int, int] | None:
    try:
        header = path.read_bytes()[:24]
    except OSError:
        return None
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", header[16:24])


class DeterministicCheckRunner:
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)

    def run(self, *, phase: str, slide_count: int, report_path: Path) -> dict[str, Any]:
        checks: dict[str, dict[str, Any]] = {}

        selected = _mapping(self.output_dir / "selected-style.yaml")
        checks["selected_style"] = {
            "passed": selected.get("selected_by") == "user",
            "evidence": "selected-style.yaml",
        }
        candidate_errors = _load_sibling("artifact_guards").validate_style_candidates(self.output_dir)
        checks["image2_manifest"] = {
            "passed": not candidate_errors,
            "errors": candidate_errors,
            "evidence": "image-generation-manifest.json",
        }

        specs = sorted((self.output_dir / "slide-specs").glob("slide-*.yaml"))
        checks["slide_spec_count"] = {
            "passed": len(specs) == slide_count,
            "expected": slide_count,
            "actual": len(specs),
        }
        image_dir = self.output_dir / ("final-images" if phase == "final" else "preview-images")
        images = sorted(image_dir.glob("slide-*.png"))
        checks["image_count"] = {
            "passed": len(images) == slide_count,
            "expected": slide_count,
            "actual": len(images),
        }
        expected_size = (1920, 1080) if phase == "final" else None
        image_sizes = {path.name: _png_size(path) for path in images}
        checks["image_resolution"] = {
            "passed": bool(images) and all(size is not None and (expected_size is None or size == expected_size) for size in image_sizes.values()),
            "expected": expected_size,
            "actual": image_sizes,
        }

        for report_name in ("typography-qa-report.md", "data-qa-report.md"):
            report = _mapping(self.output_dir / report_name)
            checks[report_name] = {"passed": report.get("status") == "pass", "evidence": report_name}

        metrics_path = self.output_dir / "data" / "metrics.json"
        try:
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            metrics_ok = isinstance(metrics, dict)
        except (OSError, UnicodeError, json.JSONDecodeError):
            metrics_ok = False
        checks["metrics_json"] = {"passed": metrics_ok, "evidence": "data/metrics.json"}

        if phase == "final":
            qa = _mapping(self.output_dir / "final-images-qa.json")
            checks["final_image_qa"] = {
                "passed": qa.get("status") == "pass" and str(qa.get("image_count")) == str(slide_count),
                "evidence": "final-images-qa.json",
            }
            ppt_errors = _load_sibling("presentation_guard").validate_presentation(
                self.output_dir / "presentation.pptx",
                self.output_dir / "speaker-notes",
                slide_count=slide_count,
            )
            checks["presentation_and_notes"] = {
                "passed": not ppt_errors,
                "errors": ppt_errors,
                "evidence": "presentation.pptx",
            }

        passed = all(check.get("passed") is True for check in checks.values())
        payload = {
            "phase": phase,
            "status": "pass" if passed else "failed",
            "deterministic_checks_passed": passed,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "checks": checks,
        }
        target = Path(report_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return payload
