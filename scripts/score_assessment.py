#!/usr/bin/env python3
"""Deterministically score an AI-native maturity assessment.

The input is JSON. Repository criteria are integers from 0 to 2. Dimension
controls contain a status and zero or more evidence labels. Missing controls
are treated as unverified.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUBRIC = ROOT / "references" / "rubric.json"

REPOSITORY_CRITERIA = (
    "agent-entry-instructions",
    "project-map-memory",
    "architecture",
    "quality-rules",
    "feedback-loop",
)
STATUSES = {"met", "partial", "not_met", "unverified"}
EVIDENCE_LABELS = {
    "observed",
    "declared",
    "corroborated",
    "inferred",
    "not found",
    "unverified",
}
STRONG_EVIDENCE = {"observed", "corroborated"}
SUPPORTING_EVIDENCE = {"declared", "inferred"}


class AssessmentError(ValueError):
    """Raised for invalid assessment input."""


def load_json(path: Path | None) -> dict[str, Any]:
    try:
        if path is None:
            value = json.load(sys.stdin)
        else:
            with path.open(encoding="utf-8") as handle:
                value = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        raise AssessmentError(f"Could not read assessment JSON: {error}") from error
    if not isinstance(value, dict):
        raise AssessmentError("Assessment input must be a JSON object")
    return value


def load_rubric(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as handle:
            rubric = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        raise AssessmentError(f"Could not read rubric JSON: {error}") from error
    if not isinstance(rubric, dict) or not isinstance(rubric.get("dimensions"), list):
        raise AssessmentError("Rubric must define a dimensions array")
    return rubric


def normalize_control(value: Any, control_id: str) -> dict[str, Any]:
    if value is None:
        return {"status": "unverified", "evidence": []}
    if isinstance(value, str):
        value = {"status": value, "evidence": []}
    if not isinstance(value, dict):
        raise AssessmentError(f"Control {control_id!r} must be an object or status string")

    status = value.get("status")
    if status not in STATUSES:
        raise AssessmentError(
            f"Control {control_id!r} has invalid status {status!r}; "
            f"expected one of {sorted(STATUSES)}"
        )
    evidence = value.get("evidence", [])
    if not isinstance(evidence, list) or not all(isinstance(item, str) for item in evidence):
        raise AssessmentError(f"Control {control_id!r} evidence must be a list of labels")
    unknown = set(evidence) - EVIDENCE_LABELS
    if unknown:
        raise AssessmentError(
            f"Control {control_id!r} has invalid evidence labels: {sorted(unknown)}"
        )
    useful = set(evidence) & (STRONG_EVIDENCE | SUPPORTING_EVIDENCE)
    if status == "met" and not useful:
        raise AssessmentError(
            f"Control {control_id!r} is met but has no observed, corroborated, "
            "declared, or inferred evidence"
        )
    if status == "met" and set(evidence) & {"not found", "unverified"}:
        raise AssessmentError(
            f"Control {control_id!r} cannot be met with not found or unverified evidence"
        )
    return {"status": status, "evidence": evidence}


def repository_result(assessment: dict[str, Any]) -> dict[str, Any]:
    raw = assessment.get("repository", {})
    if not isinstance(raw, dict):
        raise AssessmentError("repository must be a JSON object")
    unknown = set(raw) - set(REPOSITORY_CRITERIA)
    if unknown:
        raise AssessmentError(f"Unknown repository criteria: {sorted(unknown)}")
    scores: dict[str, int] = {}
    for criterion in REPOSITORY_CRITERIA:
        score = raw.get(criterion)
        if isinstance(score, bool) or not isinstance(score, int) or not 0 <= score <= 2:
            raise AssessmentError(f"Repository criterion {criterion!r} must be 0, 1, or 2")
        scores[criterion] = score
    total = sum(scores.values())
    if total <= 3:
        label = "not ready"
    elif total <= 6:
        label = "partially ready"
    elif total <= 8:
        label = "mostly ready"
    else:
        label = "AI-coding ready"
    return {"score": total, "label": label, "criteria": scores}


def dimension_results(
    rubric: dict[str, Any], assessment: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    raw_dimensions = assessment.get("dimensions", {})
    if not isinstance(raw_dimensions, dict):
        raise AssessmentError("dimensions must be a JSON object")

    expected_dimensions = {dimension["id"] for dimension in rubric["dimensions"]}
    unknown_dimensions = set(raw_dimensions) - expected_dimensions
    if unknown_dimensions:
        raise AssessmentError(f"Unknown dimensions: {sorted(unknown_dimensions)}")

    results: list[dict[str, Any]] = []
    assessed_controls: list[dict[str, Any]] = []
    for dimension in rubric["dimensions"]:
        dimension_id = dimension["id"]
        raw_controls = raw_dimensions.get(dimension_id, {})
        if not isinstance(raw_controls, dict):
            raise AssessmentError(f"Dimension {dimension_id!r} must be a JSON object")
        expected_controls = {control["id"] for control in dimension["controls"]}
        unknown_controls = set(raw_controls) - expected_controls
        if unknown_controls:
            raise AssessmentError(
                f"Dimension {dimension_id!r} has unknown controls: {sorted(unknown_controls)}"
            )

        controls: list[dict[str, Any]] = []
        stage = 0
        first_blocker: dict[str, Any] | None = None
        for control in sorted(dimension["controls"], key=lambda item: item["stage"]):
            result = normalize_control(raw_controls.get(control["id"]), control["id"])
            combined = {**control, **result}
            controls.append(combined)
            if first_blocker is None and result["status"] == "met":
                stage = control["stage"]
            elif first_blocker is None:
                first_blocker = combined

        assessment_ceiling = min(stage + 1, 4)
        assessed_controls.extend(item for item in controls if item["stage"] <= assessment_ceiling)
        results.append(
            {
                "id": dimension_id,
                "name": dimension["name"],
                "critical": bool(dimension.get("critical")),
                "stage": stage,
                "stage_label": rubric["stages"][str(stage)],
                "next_control": first_blocker,
                "controls": controls,
            }
        )
    return results, assessed_controls


def confidence_result(controls: list[dict[str, Any]]) -> dict[str, Any]:
    met = [control for control in controls if control["status"] == "met"]
    strong = [control for control in met if set(control["evidence"]) & STRONG_EVIDENCE]
    unverified = [control for control in controls if control["status"] == "unverified"]
    strong_ratio = len(strong) / len(met) if met else 0.0
    unverified_ratio = len(unverified) / len(controls) if controls else 1.0

    if strong_ratio >= 0.70 and unverified_ratio <= 0.10:
        label = "high"
    elif strong_ratio >= 0.40 and unverified_ratio <= 0.30:
        label = "medium"
    else:
        label = "low"
    return {
        "label": label,
        "strong_met_controls": len(strong),
        "met_controls": len(met),
        "assessed_controls": len(controls),
        "unverified_controls": len(unverified),
        "strong_evidence_ratio": round(strong_ratio, 3),
        "unverified_ratio": round(unverified_ratio, 3),
    }


def verdict_result(
    repository: dict[str, Any],
    dimensions: list[dict[str, Any]],
    confidence: dict[str, Any],
) -> dict[str, Any]:
    overall_stage = min(item["stage"] for item in dimensions)
    critical = [item for item in dimensions if item["critical"]]
    blockers = [item for item in critical if item["stage"] < 2]

    if overall_stage <= 1 or repository["score"] <= 3 or blockers:
        verdict = "Not AI-native"
    elif (
        overall_stage == 4
        and repository["score"] >= 9
        and confidence["label"] == "high"
    ):
        verdict = "Advanced"
    elif (
        overall_stage >= 3
        and repository["score"] >= 8
        and all(item["stage"] >= 3 for item in critical)
        and confidence["label"] in {"medium", "high"}
    ):
        verdict = "AI-native"
    else:
        verdict = "Emerging"

    return {
        "verdict": verdict,
        "overall_stage": overall_stage,
        "critical_blockers": [
            {
                "dimension": item["id"],
                "stage": item["stage"],
                "next_control": item["next_control"]["id"] if item["next_control"] else None,
            }
            for item in blockers
        ],
    }


def score(assessment: dict[str, Any], rubric: dict[str, Any]) -> dict[str, Any]:
    repository = repository_result(assessment)
    dimensions, assessed_controls = dimension_results(rubric, assessment)
    confidence = confidence_result(assessed_controls)
    verdict = verdict_result(repository, dimensions, confidence)
    return {
        "skill": rubric["skill"],
        "skill_version": rubric["skill_version"],
        "assessment_revision": rubric["assessment_revision"],
        **verdict,
        "stage_label": rubric["stages"][str(verdict["overall_stage"])],
        "repository": repository,
        "confidence": confidence,
        "dimensions": [
            {
                "id": item["id"],
                "name": item["name"],
                "stage": item["stage"],
                "stage_label": item["stage_label"],
                "critical": item["critical"],
                "next_control": item["next_control"],
            }
            for item in dimensions
        ],
    }


def as_markdown(result: dict[str, Any]) -> str:
    lines = [
        "---",
        f"skill: {result['skill']}",
        f"skill_version: {result['skill_version']}",
        f"assessment_revision: {result['assessment_revision']}",
        f"confidence: {result['confidence']['label']}",
        "---",
        "",
        "# AI-Native Maturity Score",
        "",
        f"**{result['verdict']}** — S{result['overall_stage']} "
        f"{result['stage_label']}; repository {result['repository']['score']}/10 "
        f"({result['repository']['label']}); confidence {result['confidence']['label']}.",
        "",
        "| Dimension | Stage | Next unmet control |",
        "|---|---:|---|",
    ]
    for dimension in result["dimensions"]:
        next_control = dimension["next_control"]
        next_id = next_control["id"] if next_control else "none"
        lines.append(
            f"| {dimension['name']} | S{dimension['stage']} | {next_id} |"
        )
    if result["critical_blockers"]:
        lines.extend(["", "## Critical blockers", ""])
        for blocker in result["critical_blockers"]:
            lines.append(
                f"- {blocker['dimension']} is S{blocker['stage']} "
                f"(next: {blocker['next_control']})."
            )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path, help="Assessment JSON; defaults to stdin")
    parser.add_argument("--rubric", type=Path, default=DEFAULT_RUBRIC)
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        assessment = load_json(args.input)
        rubric = load_rubric(args.rubric)
        result = score(assessment, rubric)
    except AssessmentError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if args.format == "markdown":
        print(as_markdown(result), end="")
    else:
        json.dump(result, sys.stdout, indent=2)
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
