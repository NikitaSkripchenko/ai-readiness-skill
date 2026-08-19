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


class ScoreAssessmentTests(unittest.TestCase):
    def test_fully_evidenced_s4_is_advanced(self) -> None:
        result = SCORER.score(
            {"repository": repository(), "dimensions": dimensions(4)}, RUBRIC
        )
        self.assertEqual(result["verdict"], "Advanced")
        self.assertEqual(result["overall_stage"], 4)
        self.assertEqual(result["confidence"]["label"], "high")
        self.assertEqual(result["skill_version"], "1.0.1")
        self.assertEqual(result["assessment_revision"], "2026-08-19")

    def test_s3_with_strong_evidence_is_ai_native(self) -> None:
        result = SCORER.score(
            {"repository": repository(), "dimensions": dimensions(3)}, RUBRIC
        )
        self.assertEqual(result["verdict"], "AI-native")
        self.assertEqual(result["overall_stage"], 3)

    def test_s2_is_emerging(self) -> None:
        result = SCORER.score(
            {"repository": repository(), "dimensions": dimensions(2)}, RUBRIC
        )
        self.assertEqual(result["verdict"], "Emerging")
        self.assertEqual(result["overall_stage"], 2)

    def test_critical_safety_gap_caps_verdict(self) -> None:
        result = SCORER.score(
            {
                "repository": repository(),
                "dimensions": dimensions(3, overrides={"safety-governance": 1}),
            },
            RUBRIC,
        )
        self.assertEqual(result["verdict"], "Not AI-native")
        self.assertEqual(
            [item["dimension"] for item in result["critical_blockers"]],
            ["safety-governance"],
        )

    def test_declared_only_evidence_lowers_confidence_and_verdict(self) -> None:
        result = SCORER.score(
            {
                "repository": repository(),
                "dimensions": dimensions(3, evidence="declared"),
            },
            RUBRIC,
        )
        self.assertEqual(result["confidence"]["label"], "low")
        self.assertEqual(result["verdict"], "Emerging")

    def test_repository_not_ready_caps_verdict(self) -> None:
        low_repository = repository(0)
        low_repository["agent-entry-instructions"] = 2
        low_repository["feedback-loop"] = 1
        result = SCORER.score(
            {"repository": low_repository, "dimensions": dimensions(3)}, RUBRIC
        )
        self.assertEqual(result["repository"]["score"], 3)
        self.assertEqual(result["verdict"], "Not AI-native")

    def test_met_control_requires_evidence(self) -> None:
        assessment_dimensions = dimensions(1)
        assessment_dimensions["intent-specification"]["intent-s1"]["evidence"] = []
        with self.assertRaises(SCORER.AssessmentError):
            SCORER.score(
                {"repository": repository(), "dimensions": assessment_dimensions},
                RUBRIC,
            )

    def test_unknown_control_is_rejected(self) -> None:
        assessment_dimensions = dimensions(1)
        assessment_dimensions["intent-specification"]["invented-control"] = {
            "status": "met",
            "evidence": ["observed"],
        }
        with self.assertRaises(SCORER.AssessmentError):
            SCORER.score(
                {"repository": repository(), "dimensions": assessment_dimensions},
                RUBRIC,
            )

    def test_markdown_output_carries_version(self) -> None:
        result = SCORER.score(
            {"repository": repository(), "dimensions": dimensions(3)}, RUBRIC
        )
        output = SCORER.as_markdown(result)
        self.assertIn("skill_version: 1.0.1", output)
        self.assertIn("assessment_revision: 2026-08-19", output)

    def test_met_control_rejects_contradictory_evidence(self) -> None:
        assessment_dimensions = dimensions(1)
        assessment_dimensions["intent-specification"]["intent-s1"]["evidence"] = [
            "observed",
            "not found",
        ]
        with self.assertRaises(SCORER.AssessmentError):
            SCORER.score(
                {"repository": repository(), "dimensions": assessment_dimensions},
                RUBRIC,
            )


if __name__ == "__main__":
    unittest.main()
