# Assessment JSON schema

The scorer accepts one JSON object. A full assessment requires a completed team interview. Supply every repository criterion. Omitted dimension controls are `unverified`.

```json
{
  "mode": "full",
  "repository": {
    "agent-entry-instructions": 2,
    "project-map-memory": 1,
    "architecture": 1,
    "quality-rules": 2,
    "feedback-loop": 2
  },
  "interview": {
    "question_turns": 6,
    "confirmed_by_user": true,
    "terminal_state": "ready_to_score",
    "dimensions": {
      "intent-specification": {
        "state": "resolved",
        "answer_quality": "specific",
        "challenge_count": 1,
        "user_evidence": [
          {
            "summary": "The user described a recent feature whose approved spec predated implementation.",
            "source": "declared",
            "recency": "recent"
          }
        ]
      }
    }
  },
  "dimensions": {
    "intent-specification": {
      "intent-s1": {
        "status": "met",
        "evidence": ["observed", "declared"]
      },
      "intent-s2": {
        "status": "partial",
        "evidence": ["observed"]
      }
    }
  }
}
```

`mode` is required:

- `full` requires at least four user-answered question turns, explicit user confirmation, terminal state `ready_to_score`, and one record for every dimension;
- `repository-only` requires only repository scores and returns `Team AI-native verdict: not assessable`.

Do not set `confirmed_by_user` based on repository inference. It means a person actually answered the interview. The example abbreviates `interview.dimensions`; a real full input must contain all nine IDs from `rubric.json`.

Dimension interview records:

- `state`: `resolved` or `explicit_unknown`;
- `answer_quality` for resolved records: `specific`, `corroborated`, or `explicit_absence`;
- `answer_quality` for unknown records: `unknown`;
- `challenge_count`: non-negative integer;
- `user_evidence`: one or more records for resolved dimensions, empty for unknown dimensions;
- evidence `source`: `declared` or `corroborated`;
- evidence `recency`: `recent`, `stale`, or `unknown`.

Critical dimensions cannot remain `explicit_unknown`. If any non-critical dimension is unknown, the scorer returns `Not assessable` instead of inventing a team stage.

Repository values must be `0`, `1`, or `2`.

Control statuses:

- `met`
- `partial`
- `not_met`
- `unverified`

Evidence labels:

- `observed`
- `declared`
- `corroborated`
- `inferred`
- `not found`
- `unverified`

A `met` control must include `observed`, `corroborated`, `declared`, or `inferred` evidence. Put detailed citations and interview notes in the report's evidence ledger; the scorer needs only the labels.

Run:

```sh
python3 scripts/score_assessment.py assessment.json
python3 scripts/score_assessment.py assessment.json --format markdown
```
