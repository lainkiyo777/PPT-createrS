"""Deterministically validate reviewer JSON and calculate PASS/FAIL."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


ISSUE_FIELDS = ("id", "severity", "criterion", "slides", "finding", "evidence", "required_fix")
EVALUATION_FIELDS = (
    "review_id",
    "artifact_version",
    "total_score",
    "passed",
    "critical_failures",
    "dimension_scores",
    "issues",
    "revision_priority",
)


class RubricError(RuntimeError):
    pass


class ReviewDecision:
    def __init__(
        self,
        *,
        passed: bool,
        total_score: float,
        critical_failures: list[str],
        deterministic_checks_passed: bool,
        validation_errors: list[str],
        valid_issues: list[dict[str, Any]],
    ):
        self.passed = passed
        self.total_score = total_score
        self.critical_failures = critical_failures
        self.deterministic_checks_passed = deterministic_checks_passed
        self.validation_errors = validation_errors
        self.valid_issues = valid_issues

    def as_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "total_score": self.total_score,
            "critical_failures": self.critical_failures,
            "deterministic_checks_passed": self.deterministic_checks_passed,
            "validation_errors": self.validation_errors,
            "valid_issues": self.valid_issues,
        }


def load_rubric(path: Path) -> dict[str, Any]:
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise RubricError(f"cannot read rubric {path}: {exc}") from exc
    result: dict[str, Any] = {"dimensions": {}, "critical_failures": []}
    section = "root"
    for raw in lines:
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped == "dimensions:":
            section = "dimensions"
            continue
        if stripped == "critical_failures:":
            section = "critical_failures"
            continue
        if section == "critical_failures" and stripped.startswith("-"):
            result["critical_failures"].append(stripped[1:].strip())
            continue
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip().strip("\"'")
        if section == "dimensions" and raw.startswith("  "):
            try:
                result["dimensions"][key] = float(value)
            except ValueError as exc:
                raise RubricError(f"invalid dimension weight {key}: {value}") from exc
        elif not raw.startswith(" "):
            if key in {"minimum_score", "maximum_critical_failures", "version"}:
                result[key] = float(value)
            else:
                result[key] = value
    weights = result["dimensions"]
    if not weights or abs(sum(weights.values()) - 100) > 1e-9:
        raise RubricError(f"rubric dimension weights must total 100; got {sum(weights.values())}")
    if "minimum_score" not in result or "maximum_critical_failures" not in result:
        raise RubricError("rubric requires minimum_score and maximum_critical_failures")
    return result


class DeterministicReviewGate:
    def __init__(self, rubric_path: Path):
        self.rubric_path = Path(rubric_path)
        self.rubric = load_rubric(self.rubric_path)

    def evaluate(self, evaluation: Mapping[str, Any], *, deterministic_checks_passed: bool) -> ReviewDecision:
        payload = dict(evaluation)
        errors: list[str] = []
        for field in EVALUATION_FIELDS:
            if field not in payload:
                errors.append(f"evaluation is missing {field}")

        scores = payload.get("dimension_scores", {})
        if not isinstance(scores, dict):
            errors.append("dimension_scores must be an object")
            scores = {}
        weighted = 0.0
        for dimension, weight in self.rubric["dimensions"].items():
            value = scores.get(dimension)
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 100:
                errors.append(f"dimension_scores.{dimension} must be between 0 and 100")
                value = 0
            weighted += float(value) * float(weight) / 100.0
        total_score = round(weighted, 2)
        if total_score.is_integer():
            total_score = int(total_score)

        raw_issues = payload.get("issues", [])
        if not isinstance(raw_issues, list):
            errors.append("issues must be an array")
            raw_issues = []
        valid_issues: list[dict[str, Any]] = []
        for index, issue in enumerate(raw_issues, start=1):
            if not isinstance(issue, dict):
                errors.append(f"issue {index} must be an object")
                continue
            missing = [field for field in ISSUE_FIELDS if issue.get(field) in (None, "")]
            if missing:
                errors.append(f"issue {issue.get('id', index)} is missing non-empty {', '.join(missing)}")
                continue
            if issue.get("severity") not in {"critical", "major", "minor"}:
                errors.append(f"issue {issue.get('id', index)} has invalid severity")
                continue
            if not isinstance(issue.get("slides"), list):
                errors.append(f"issue {issue.get('id', index)} slides must be an array")
                continue
            valid_issues.append(dict(issue))

        critical = payload.get("critical_failures", [])
        if not isinstance(critical, list):
            errors.append("critical_failures must be an array")
            critical = []
        critical = [str(item) for item in critical if str(item).strip()]

        passed = (
            not errors
            and total_score >= float(self.rubric["minimum_score"])
            and len(critical) <= int(self.rubric["maximum_critical_failures"])
            and deterministic_checks_passed is True
        )
        return ReviewDecision(
            passed=passed,
            total_score=total_score,
            critical_failures=critical,
            deterministic_checks_passed=deterministic_checks_passed is True,
            validation_errors=errors,
            valid_issues=valid_issues,
        )

    def evaluate_file(self, evaluation_path: Path, *, deterministic_checks_passed: bool, decision_path: Path | None = None) -> ReviewDecision:
        try:
            payload = json.loads(Path(evaluation_path).read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise RubricError(f"invalid evaluation JSON {evaluation_path}: {exc}") from exc
        decision = self.evaluate(payload, deterministic_checks_passed=deterministic_checks_passed)
        if decision_path:
            target = Path(decision_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(decision.as_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return decision
