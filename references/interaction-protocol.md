# Interaction protocol

This protocol is the execution engine for a full assessment. Treat it as a state machine, not optional guidance.

## Hard gate

- Ask exactly one semantic question per turn.
- After emitting the question, stop and wait for the user.
- Never ask and answer the question yourself.
- Never mark a dimension resolved merely because repository files suggest an answer.
- Never score while the state is `collecting`, `needs_evidence`, or `needs_clarification`.
- If no interactive user is available, stop with `BLOCKED — team interview required`; do not auto-answer.

## State machine

```text
repository_scan
  -> ask_scope
  -> awaiting_answer
  -> classify_answer
       -> needs_clarification -> awaiting_answer
       -> needs_evidence      -> awaiting_answer
       -> update_ledger       -> select_next_question
  -> awaiting_answer
  -> ...
  -> readiness_check
       -> collecting         -> select_next_question
       -> not_assessable     -> repository-only report
       -> ready_to_score     -> deterministic scoring -> final report
```

Terminal states:

- `ready_to_score`: at least four user-answered question turns, all nine dimensions resolved, all critical dimensions resolved, and contradictions resolved or disclosed.
- `not_assessable`: the user declines, critical evidence remains unknown, or the interview cannot continue. Produce no team verdict.
- `repository_only`: the user explicitly requested only repository readiness. Produce no team verdict.

## Dimension states

Track every dimension as one of:

- `unasked` — no user evidence yet;
- `asked` — a question is awaiting or has just received an answer;
- `needs_evidence` — the answer is plausible but vague, policy-only, hypothetical, or stale;
- `needs_clarification` — the answer conflicts with repository or earlier evidence;
- `resolved` — the user supplied specific evidence, explicit absence, or a corroborated practice;
- `explicit_unknown` — the user cannot establish the practice. This is addressed, but prevents a defensible team verdict when critical.

## Answer classification

Classify each answer before choosing the next question:

| Quality | Meaning | Action |
|---|---|---|
| `vague` | Opinion or generality without a concrete practice | Push on the same issue |
| `hypothetical` | Describes what should happen, not what recently happened | Ask for a recent example |
| `policy_only` | A policy exists but routine use is not established | Ask for enforcement or a recent case |
| `specific` | Names a recent workflow, owner, artifact, frequency, or exception | Resolve relevant dimensions |
| `corroborated` | Specific answer matches inspected artifacts | Resolve with stronger evidence |
| `explicit_absence` | User clearly states the practice does not exist | Resolve as a gap |
| `unknown` | User cannot determine the answer | Mark `explicit_unknown` |
| `contradicted` | Conflicts with repository or a prior answer | Clarify before proceeding |

Do not reward length. A short concrete answer is stronger than a long abstract one.

## Question sequence

### Q1 — Scope and adoption

Ask who is in scope and how consistently they have used coding agents in the last 90 days or 5–10 relevant changes. This establishes team shape, timeframe, and adoption baseline.

Stop and wait.

### Q2 — Recent real workflow

Ask the user to walk through one recent non-trivial AI-assisted change from intent to merge or deployment. A strong answer naturally identifies the specification, agent responsibility, verification, review owner, and result.

Stop and wait.

### Q3 onward — Adaptive selection

Choose one unresolved issue using this priority order:

1. contradiction requiring clarification;
2. critical dimension with no specific evidence;
3. answer currently blocking the lowest plausible maturity stage;
4. highest-uncertainty dimension;
5. non-critical remaining coverage.

Do not ask a scheduled question when an earlier answer already resolved it. Do not advance to an S3/S4 probe when the prerequisite practice is absent.

## Push rules

Push once when an answer is vague, hypothetical, policy-only, or contradicted. Use the smallest follow-up that would make it scorable:

- “What happened in the most recent real change?”
- “Who owned that decision?”
- “What artifact or required gate proves it?”
- “How often was that followed in the last five relevant changes?”
- “What happens when someone bypasses it?”

If the second answer remains vague, record `explicit_unknown` or `partial`; do not interrogate indefinitely.

## Smart skip

One answer may resolve multiple dimensions. Update all supported dimensions, then skip redundant questions. Example: a concrete change walkthrough can cover intent, autonomy, review, tests, and comprehension.

Do not smart-skip merely because a topic was mentioned. Skip only when the answer contains scorable evidence.

## Question format

Use a stable counter and one target dimension:

```text
Q<N> — <short title>
Why it matters: <one sentence tied to the verdict>
What I know so far: <one concise evidence-based sentence>
Question: <one semantic question>
A strong answer includes: <2–4 evidence cues, not additional questions>
Progress: <resolved>/9 dimensions; critical <resolved>/3
```

For simple scope questions, omit “What I know so far” when empty. Do not add a second question after the template.

If a structured user-question tool is available and suitable, use it. If it is unavailable, render the question in the final response. In either case, stop immediately afterward.

## Impatience and refusal

If the user asks to speed up, explain that the interview is the team assessment and offer a fast path: ask the four highest-value questions one at a time. The fast path still requires evidence for all critical dimensions; smart-skip can cover the others.

If the user refuses further questions, respect that choice. Produce a repository-only report with `Team AI-native verdict: not assessable`.

## Readiness check

Before scoring, verify:

- at least four questions were answered by the user;
- all nine dimensions are `resolved` or `explicit_unknown`;
- verification, tests, and safety are `resolved`, not merely unknown;
- every resolved dimension has at least one user evidence record;
- vague and policy-only answers were challenged;
- contradictions are resolved or disclosed;
- the next action is scoring, not another missing question.

If any check fails, select exactly one next question and stop.
