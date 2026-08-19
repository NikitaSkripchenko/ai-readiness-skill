#!/usr/bin/env python3
"""Regression tests for the deterministic maturity scorer."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("score_assessment.py")
SPEC = importlib.util.spec_from_file_location("score_assessment", SCRIPT)
assert SPEC and SPEC.loader
SCORER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCORER)
RUBRIC = SCORER.load_rubric(SCORER.DEFAULT_RUBRIC)


def repository(score: int = 2) -> dict[str, int]:
    return {criterion: score for criterion in SCORER.REPOSITORY_CRITERIA}


def dimensions(
    reached_stage: int,
    evidence: str = "observed",
    overrides: dict[str, int] | None = None,
) -> dict[str, dict[str, dict[str, object]]]:
    overrides = overrides or {}
    values: dict[str, dict[str, dict[str, object]]] = {}
    for dimension in RUBRIC["dimensions"]:
        dimension_stage = overrides.get(dimension["id"], reached_stage)
        values[dimension["id"]] = {}
        for control in dimension["controls"]:
            met = control["stage"] <= dimension_stage
            values[dimension["id"]][control["id"]] = {
                "status": "met" if met else "not_met",
                "evidence": [evidence] if met else ["observed"],
            }
    return values


def interview(
    question_turns: int = 4,
    omit_dimensions: set[str] | None = None,
    unknown_dimensions: set[str] | None = None,
    confirmed_by_user: bool = True,
) -> dict[str, object]:
    omit_dimensions = omit_dimensions or set()
    unknown_dimensions = unknown_dimensions or set()
    records: dict[str, dict[str, object]] = {}
    for dimension in RUBRIC["dimensions"]:
        dimension_id = dimension["id"]
        if dimension_id in omit_dimensions:
            continue
        if dimension_id in unknown_dimensions:
            records[dimension_id] = {
                "state": "explicit_unknown",
                "answer_quality": "unknown",
                "challenge_count": 1,
                "user_evidence": [],
            }
        else:
            records[dimension_id] = {
                "state": "resolved",
                "answer_quality": "specific",
                "challenge_count": 0,
                "user_evidence": [
                    {
                        "summary": f"User supplied recent evidence for {dimension_id}.",
                        "source": "declared",
                        "recency": "recent",
                    }
                ],
            }
    return {
        "question_turns": question_turns,
        "confirmed_by_user": confirmed_by_user,
        "terminal_state": "ready_to_score",
        "dimensions": records,
    }


def full_assessment(
    reached_stage: int,
    repository_scores: dict[str, int] | None = None,
    evidence: str = "observed",
    overrides: dict[str, int] | None = None,
) -> dict[str, object]:
    return {
        "mode": "full",
        "repository": repository_scores or repository(),
        "interview": interview(),
        "dimensions": dimensions(reached_stage, evidence=evidence, overrides=overrides),
    }


class ScoreAssessmentTests(unittest.TestCase):
    def test_fully_evidenced_s4_is_advanced(self) -> None:
        result = SCORER.score(full_assessment(4), RUBRIC)
        self.assertEqual(result["verdict"], "Advanced")
        self.assertEqual(result["overall_stage"], 4)
        self.assertEqual(result["confidence"]["label"], "high")
        self.assertEqual(result["skill_version"], "3.0.0")
        self.assertEqual(result["assessment_revision"], "2026-08-19.3")
        self.assertEqual(result["interview"]["question_turns"], 4)

    def test_s3_with_strong_evidence_is_ai_native(self) -> None:
        result = SCORER.score(full_assessment(3), RUBRIC)
        self.assertEqual(result["verdict"], "AI-native")
        self.assertEqual(result["overall_stage"], 3)

    def test_s2_is_emerging(self) -> None:
        result = SCORER.score(full_assessment(2), RUBRIC)
        self.assertEqual(result["verdict"], "Emerging")
        self.assertEqual(result["overall_stage"], 2)

    def test_critical_safety_gap_caps_verdict(self) -> None:
        result = SCORER.score(
            full_assessment(3, overrides={"safety-governance": 1}), RUBRIC
        )
        self.assertEqual(result["verdict"], "Not AI-native")
        self.assertEqual(
            [item["dimension"] for item in result["critical_blockers"]],
            ["safety-governance"],
        )

    def test_declared_only_evidence_lowers_confidence_and_verdict(self) -> None:
        result = SCORER.score(full_assessment(3, evidence="declared"), RUBRIC)
        self.assertEqual(result["confidence"]["label"], "low")
        self.assertEqual(result["verdict"], "Emerging")

    def test_repository_not_ready_caps_verdict(self) -> None:
        low_repository = repository(0)
        low_repository["agent-entry-instructions"] = 2
        low_repository["feedback-loop"] = 1
        result = SCORER.score(full_assessment(3, low_repository), RUBRIC)
        self.assertEqual(result["repository"]["score"], 3)
        self.assertEqual(result["verdict"], "Not AI-native")

    def test_met_control_requires_evidence(self) -> None:
        assessment = full_assessment(1)
        assessment["dimensions"]["intent-specification"]["intent-s1"]["evidence"] = []
        with self.assertRaises(SCORER.AssessmentError):
            SCORER.score(assessment, RUBRIC)

    def test_unknown_control_is_rejected(self) -> None:
        assessment = full_assessment(1)
        assessment["dimensions"]["intent-specification"]["invented-control"] = {
            "status": "met",
            "evidence": ["observed"],
        }
        with self.assertRaises(SCORER.AssessmentError):
            SCORER.score(assessment, RUBRIC)

    def test_markdown_output_carries_version(self) -> None:
        result = SCORER.score(full_assessment(3), RUBRIC)
        output = SCORER.as_markdown(result)
        self.assertIn("skill_version: 3.0.0", output)
        self.assertIn("assessment_revision: 2026-08-19.3", output)
        self.assertIn("Interview: 4 user-answered questions", output)

    def test_met_control_rejects_contradictory_evidence(self) -> None:
        assessment = full_assessment(1)
        assessment["dimensions"]["intent-specification"]["intent-s1"]["evidence"] = [
            "observed",
            "not found",
        ]
        with self.assertRaises(SCORER.AssessmentError):
            SCORER.score(assessment, RUBRIC)

    def test_full_assessment_without_interview_is_rejected(self) -> None:
        assessment = full_assessment(2)
        del assessment["interview"]
        with self.assertRaisesRegex(SCORER.AssessmentError, "requires an interview"):
            SCORER.score(assessment, RUBRIC)

    def test_single_interview_round_is_rejected(self) -> None:
        assessment = full_assessment(2)
        assessment["interview"] = interview(question_turns=3)
        with self.assertRaisesRegex(SCORER.AssessmentError, "at least 4"):
            SCORER.score(assessment, RUBRIC)

    def test_incomplete_dimension_coverage_is_rejected(self) -> None:
        assessment = full_assessment(2)
        assessment["interview"] = interview(
            omit_dimensions={"measurement-compounding"}
        )
        with self.assertRaisesRegex(SCORER.AssessmentError, "records missing"):
            SCORER.score(assessment, RUBRIC)

    def test_repository_only_mode_has_no_team_verdict(self) -> None:
        result = SCORER.score(
            {"mode": "repository-only", "repository": repository()}, RUBRIC
        )
        self.assertEqual(result["verdict"], "Not assessable")
        self.assertIsNone(result["overall_stage"])
        self.assertEqual(result["dimensions"], [])
        output = SCORER.as_markdown(result)
        self.assertIn("Team AI-native verdict: not assessable", output)

    def test_missing_mode_is_rejected(self) -> None:
        with self.assertRaisesRegex(SCORER.AssessmentError, "mode must be"):
            SCORER.score({"repository": repository()}, RUBRIC)

    def test_resolved_dimension_requires_user_evidence(self) -> None:
        assessment = full_assessment(2)
        assessment["interview"]["dimensions"]["intent-specification"][
            "user_evidence"
        ] = []
        with self.assertRaisesRegex(SCORER.AssessmentError, "needs user evidence"):
            SCORER.score(assessment, RUBRIC)

    def test_vague_answer_cannot_resolve_dimension(self) -> None:
        assessment = full_assessment(2)
        assessment["interview"]["dimensions"]["intent-specification"][
            "answer_quality"
        ] = "vague"
        with self.assertRaisesRegex(SCORER.AssessmentError, "needs specific"):
            SCORER.score(assessment, RUBRIC)

    def test_critical_dimension_cannot_remain_unknown(self) -> None:
        assessment = full_assessment(2)
        assessment["interview"] = interview(
            unknown_dimensions={"safety-governance"}
        )
        with self.assertRaisesRegex(SCORER.AssessmentError, "Critical.*unknown"):
            SCORER.score(assessment, RUBRIC)

    def test_noncritical_unknown_prevents_team_verdict(self) -> None:
        assessment = full_assessment(2)
        assessment["interview"] = interview(
            unknown_dimensions={"measurement-compounding"}
        )
        result = SCORER.score(assessment, RUBRIC)
        self.assertEqual(result["verdict"], "Not assessable")
        self.assertIsNone(result["overall_stage"])
        output = SCORER.as_markdown(result)
        self.assertIn("measurement-compounding", output)

    def test_corroborated_quality_requires_corroborated_source(self) -> None:
        assessment = full_assessment(2)
        record = assessment["interview"]["dimensions"]["intent-specification"]
        record["answer_quality"] = "corroborated"
        with self.assertRaisesRegex(SCORER.AssessmentError, "needs corroborated"):
            SCORER.score(assessment, RUBRIC)


if __name__ == "__main__":
    unittest.main()
