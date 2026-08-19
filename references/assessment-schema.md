# Assessment JSON schema

The scorer accepts one JSON object. Supply every repository criterion. Omitted dimension controls are `unverified`.

```json
{
  "repository": {
    "agent-entry-instructions": 2,
    "project-map-memory": 1,
    "architecture": 1,
    "quality-rules": 2,
    "feedback-loop": 2
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

