---
skill: ai-native-maturity-audit
skill_version: 3.0.0
assessment_revision: 2026-08-19.3
assessed_at: YYYY-MM-DD
assessment_mode: full | repository-only
scope: "repository, team, and timeframe"
confidence: low | medium | high | not assessable
interview_question_turns: 0 | integer
---

# AI-Native Maturity Assessment

## Assessment validity

- Mode: full or repository-only
- User-answered question turns: X
- Resolved dimensions: X / 9
- Critical dimensions discussed: review, tests, safety

If mode is `full` and fewer than four question turns were answered, any dimension record is missing, or a critical dimension remains unknown, stop: the assessment is invalid and this report must not be issued.

## Verdict

For a full assessment: **<Not AI-native | Emerging | AI-native | Advanced>** — one direct paragraph explaining why, the scope of the conclusion, and the single most important limiting factor.

For repository-only mode: **Team AI-native verdict: not assessable** — explain that the team interview was not completed. Do not infer a team verdict from repository readiness.

## Results

| Result | Value | Interpretation |
|---|---:|---|
| Repository readiness | X / 10 | not ready / partially ready / mostly ready / AI-coding ready |
| Team maturity | S0–S4 | lowest load-bearing dimension |
| Confidence | low / medium / high | strength and completeness of evidence |
| Interview | X answered questions | all 9 dimensions resolved/explicitly unknown or repository-only |

## Repository scorecard

| Criterion | Score | Evidence | Main gap |
|---|---:|---|---|
| Agent entry instructions | 0–2 | paths or `not found` | |
| Project map and memory | 0–2 | | |
| Architecture | 0–2 | | |
| Quality rules | 0–2 | | |
| Feedback loop | 0–2 | | |

## Team maturity

| Dimension | Stage | Evidence class | Reason stage is capped |
|---|---:|---|---|
| Intent and specification | S0–S4 | | |
| Context, memory, and harness | S0–S4 | | |
| Autonomy and orchestration | S0–S4 | | |
| Verification and review | S0–S4 | | |
| Tests and deterministic gates | S0–S4 | | |
| Safety, security, and governance | S0–S4 | | |
| Comprehension and judgment | S0–S4 | | |
| Reusable capability and learning | S0–S4 | | |
| Measurement, cost, and compounding | S0–S4 | | |

## Critical blockers

Only load-bearing deficiencies that cap the verdict. Write `none found` if there are none.

## Evidence ledger

For each material claim record:

- claim;
- evidence label;
- source or user statement;
- freshness/timeframe;
- confidence or limitation.

## Contradictions and unverified claims

Separate contradictions from unavailable evidence. Explain what would resolve each item.

## Strongest existing practices

Name two or three practices worth preserving.

## Stage-up priorities

Order by gating impact, not ease alone. For each priority include owner type, concrete deliverable, proof of completion, and the dimension or verdict gate it unlocks.

### In one day

Small changes that improve agent orientation or verification immediately.

### In 30 days

Team practices, gates, or shared harness work.

### In 90 days

Measurement, governance, cross-repository capability, or guarded autonomy.

## Reassessment

Recommend a date or trigger and warn if the next report uses a different `assessment_revision`.
