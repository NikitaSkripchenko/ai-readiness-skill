#!/usr/bin/env python3
"""Deterministically score an AI-native maturity assessment.

The input is JSON. Full assessments require a completed multi-turn team
interview. Repository-only assessments never produce a team maturity verdict.
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
ASSESSMENT_MODES = {"full", "repository-only"}
INTERVIEW_DIMENSION_STATES = {"resolved", "explicit_unknown"}
RESOLVED_ANSWER_QUALITIES = {"specific", "corroborated", "explicit_absence"}
INTERVIEW_EVIDENCE_SOURCES = {"declared", "corroborated"}
EVIDENCE_RECENCY = {"recent", "stale", "unknown"}


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


def interview_result(
    rubric: dict[str, Any], assessment: dict[str, Any]
) -> dict[str, Any]:
    raw = assessment.get("interview")
    if not isinstance(raw, dict):
        raise AssessmentError(
            "Full assessment requires an interview object; use repository-only "
            "mode when the team interview was not completed"
        )

    question_turns = raw.get("question_turns")
    if (
        isinstance(question_turns, bool)
        or not isinstance(question_turns, int)
        or question_turns < 4
    ):
        raise AssessmentError(
            "Full assessment requires at least 4 user-answered question turns"
        )
    if raw.get("confirmed_by_user") is not True:
        raise AssessmentError(
            "Full assessment requires confirmed_by_user: true; repository evidence "
            "cannot complete the interview"
        )

    if raw.get("terminal_state") != "ready_to_score":
        raise AssessmentError(
            "Full assessment requires interview.terminal_state: ready_to_score"
        )

    records = raw.get("dimensions")
    if not isinstance(records, dict):
        raise AssessmentError("interview.dimensions must be an object")

    expected = {dimension["id"] for dimension in rubric["dimensions"]}
    unknown = set(records) - expected
    missing = expected - set(records)
    if unknown:
        raise AssessmentError(f"Interview has unknown dimensions: {sorted(unknown)}")
    if missing:
        raise AssessmentError(
            f"Interview is incomplete; dimension records missing: {sorted(missing)}"
        )

    critical = {
        dimension["id"]
        for dimension in rubric["dimensions"]
        if dimension.get("critical")
    }
    explicit_unknown: list[str] = []
    normalized: dict[str, dict[str, Any]] = {}
    for dimension_id in sorted(expected):
        record = records[dimension_id]
        if not isinstance(record, dict):
            raise AssessmentError(
                f"Interview dimension {dimension_id!r} must be an object"
            )
        state = record.get("state")
        if state not in INTERVIEW_DIMENSION_STATES:
            raise AssessmentError(
                f"Interview dimension {dimension_id!r} must be resolved or explicit_unknown"
            )
        quality = record.get("answer_quality")
        evidence = record.get("user_evidence", [])
        if not isinstance(evidence, list):
            raise AssessmentError(
                f"Interview dimension {dimension_id!r} user_evidence must be a list"
            )
        challenge_count = record.get("challenge_count", 0)
        if (
            isinstance(challenge_count, bool)
            or not isinstance(challenge_count, int)
            or challenge_count < 0
        ):
            raise AssessmentError(
                f"Interview dimension {dimension_id!r} challenge_count must be non-negative"
            )

        normalized_evidence: list[dict[str, str]] = []
        for index, item in enumerate(evidence):
            if not isinstance(item, dict):
                raise AssessmentError(
                    f"Interview dimension {dimension_id!r} evidence #{index + 1} must be an object"
                )
            summary = item.get("summary")
            source = item.get("source")
            recency = item.get("recency")
            if not isinstance(summary, str) or not summary.strip():
                raise AssessmentError(
                    f"Interview dimension {dimension_id!r} evidence #{index + 1} needs a summary"
                )
            if source not in INTERVIEW_EVIDENCE_SOURCES:
                raise AssessmentError(
                    f"Interview dimension {dimension_id!r} evidence source must be declared or corroborated"
                )
            if recency not in EVIDENCE_RECENCY:
                raise AssessmentError(
                    f"Interview dimension {dimension_id!r} evidence recency must be recent, stale, or unknown"
                )
            normalized_evidence.append(
                {"summary": summary.strip(), "source": source, "recency": recency}
            )

        if state == "resolved":
            if quality not in RESOLVED_ANSWER_QUALITIES:
                raise AssessmentError(
                    f"Resolved interview dimension {dimension_id!r} needs specific, "
                    "corroborated, or explicit_absence answer quality"
                )
            if not normalized_evidence:
                raise AssessmentError(
                    f"Resolved interview dimension {dimension_id!r} needs user evidence"
                )
            if quality == "corroborated" and not any(
                item["source"] == "corroborated" for item in normalized_evidence
            ):
                raise AssessmentError(
                    f"Corroborated interview dimension {dimension_id!r} needs corroborated evidence"
                )
        else:
            if quality != "unknown" or normalized_evidence:
                raise AssessmentError(
                    f"explicit_unknown dimension {dimension_id!r} must use unknown quality "
                    "and no evidence"
                )
            explicit_unknown.append(dimension_id)

        normalized[dimension_id] = {
            "state": state,
            "answer_quality": quality,
            "user_evidence": normalized_evidence,
            "challenge_count": challenge_count,
        }

    critical_unknown = critical & set(explicit_unknown)
    if critical_unknown:
        raise AssessmentError(
            f"Critical interview dimensions cannot remain unknown: {sorted(critical_unknown)}"
        )

    return {
        "question_turns": question_turns,
        "confirmed_by_user": True,
        "terminal_state": "ready_to_score",
        "dimensions": normalized,
        "explicit_unknown_dimensions": explicit_unknown,
        "critical_dimensions_resolved": sorted(critical),
    }


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
    mode = assessment.get("mode")
    if mode not in ASSESSMENT_MODES:
        raise AssessmentError(
            f"mode must be one of {sorted(ASSESSMENT_MODES)}; got {mode!r}"
        )
    repository = repository_result(assessment)
    base = {
        "skill": rubric["skill"],
        "skill_version": rubric["skill_version"],
        "assessment_revision": rubric["assessment_revision"],
        "mode": mode,
        "repository": repository,
    }
    if mode == "repository-only":
        return {
            **base,
            "verdict": "Not assessable",
            "overall_stage": None,
            "stage_label": None,
            "confidence": None,
            "critical_blockers": [],
            "dimensions": [],
            "interview": None,
        }

    interview = interview_result(rubric, assessment)
    dimensions, assessed_controls = dimension_results(rubric, assessment)
    confidence = confidence_result(assessed_controls)
    if interview["explicit_unknown_dimensions"]:
        verdict = {
            "verdict": "Not assessable",
            "overall_stage": None,
            "critical_blockers": [],
        }
        stage_label = None
    else:
        verdict = verdict_result(repository, dimensions, confidence)
        stage_label = rubric["stages"][str(verdict["overall_stage"])]
    return {
        **base,
        **verdict,
        "stage_label": stage_label,
        "interview": interview,
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
    confidence = result["confidence"]["label"] if result["confidence"] else "not assessable"
    lines = [
        "---",
        f"skill: {result['skill']}",
        f"skill_version: {result['skill_version']}",
        f"assessment_revision: {result['assessment_revision']}",
        f"assessment_mode: {result['mode']}",
        f"confidence: {confidence}",
        "---",
        "",
        "# AI-Native Maturity Score",
        "",
    ]
    if result["mode"] == "repository-only":
        lines.extend(
            [
                "**Team AI-native verdict: not assessable.** The team interview was not completed.",
                "",
                f"Repository readiness: {result['repository']['score']}/10 "
                f"({result['repository']['label']}).",
            ]
        )
        return "\n".join(lines) + "\n"

    if result["verdict"] == "Not assessable":
        lines.extend(
            [
                "**Team AI-native verdict: not assessable.** One or more non-critical "
                "dimensions remain explicitly unknown.",
                "",
                f"Repository readiness: {result['repository']['score']}/10 "
                f"({result['repository']['label']}).",
                "",
                "Unknown dimensions: "
                + ", ".join(result["interview"]["explicit_unknown_dimensions"]),
            ]
        )
        return "\n".join(lines) + "\n"

    lines.extend(
        [
            f"**{result['verdict']}** — S{result['overall_stage']} "
            f"{result['stage_label']}; repository {result['repository']['score']}/10 "
            f"({result['repository']['label']}); confidence {confidence}.",
            "",
            f"Interview: {result['interview']['question_turns']} user-answered questions; "
            "9/9 dimensions resolved.",
            "",
            "| Dimension | Stage | Next unmet control |",
            "|---|---:|---|",
        ]
    )
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
