# Scoring and verdicts

## Interaction prerequisite

A full team assessment is invalid until the interview gate passes. The scorer requires:

- `mode: full`;
- at least four user-answered question turns;
- `confirmed_by_user: true`;
- terminal state `ready_to_score`;
- all nine dimensions represented by structured interview records;
- specific user evidence for every resolved dimension;
- all critical dimensions resolved rather than unknown.

Without that evidence, use `mode: repository-only`. Repository-only mode produces a readiness score but no team maturity stage and no AI-native verdict.

If a non-critical dimension remains explicitly unknown after a valid interview, the assessment is complete but the team verdict is `Not assessable`. Unknown evidence is not negative evidence.

## Control statuses

- `met`: consistent recent practice with relevant evidence;
- `partial`: inconsistent, incomplete, isolated, or policy-only;
- `not_met`: evidence shows the practice is absent or contradicted;
- `unverified`: evidence may exist but could not be validated.

Do not treat `unverified` as `met`. Do not use `not applicable` for core controls; reinterpret them for the assessment context instead.

## Dimension stage

Each dimension has one load-bearing control at S1, S2, S3, and S4 in `rubric.json`. Start at S0. Advance one stage only when that stage's control and all controls below it are `met`.

Examples:

- S1 met, S2 partial → dimension S1.
- S1–S3 met, S4 unverified → dimension S3.
- S2–S4 met but S1 unverified → dimension S0 until the contradiction is resolved.

The overall team stage is the minimum of the nine dimension stages. Calculate it only after the interaction prerequisite passes.

## Repository readiness

Add the five 0–2 repository criteria:

- 0–3: not ready;
- 4–6: partially ready;
- 7–8: mostly ready;
- 9–10: AI-coding ready.

## Verdict gates

Apply in order:

1. **Not AI-native** when the overall team stage is S0/S1, repository readiness is 0–3, or safety, verification, or deterministic gates are below S2.
2. **Emerging** when the team is at least S2 but any dimension remains S2, repository readiness is 4–7, or confidence is low.
3. **AI-native** when all dimensions are at least S3, repository readiness is at least 8, critical dimensions are at least S3, and confidence is medium or high.
4. **Advanced** only when all dimensions are S4, repository readiness is at least 9, and confidence is high.

These labels answer whether AI is part of the operating system, not whether individual developers use AI frequently.

## Confidence

For controls marked `met`, inspect their evidence labels:

- strong: `observed` or `corroborated`;
- supporting: `declared` or `inferred`;
- absent: no evidence or only `unverified` / `not found`.

Report:

- `high`: at least 70% of met controls have strong evidence and at most 10% of all controls are unverified;
- `medium`: at least 40% of met controls have strong evidence and at most 30% are unverified;
- `low`: otherwise.

Confidence changes how strongly the verdict is stated. It does not turn missing controls into met controls.

## Contradictions and caps

List contradictions separately. A documented policy contradicted by recent implementation is at most `partial`. A repeated practice with no written policy can be `met` at S1/S2 when corroborated, but durable S3/S4 practices normally require maintained artifacts or telemetry.

Critical dimensions are:

- `verification-review`;
- `tests-gates`;
- `safety-governance`.

Any critical dimension below S2 is a blocker. Do not average it away.
