# Maturity model

## Evidence vocabulary

Use exactly these labels:

| Label | Meaning |
|---|---|
| `observed` | Directly inspected in the repository or an approved connected system. |
| `declared` | Reported by the user but not independently verified. |
| `corroborated` | A user statement supported by inspected artifacts or multiple independent examples. |
| `inferred` | A cautious conclusion from indirect evidence; state the inference. |
| `not found` | Searched for in the agreed scope and absent. |
| `unverified` | May exist, but the assessor could not access or validate it. |

Evidence also has freshness and consistency. Prefer recent repeated examples over policy documents, isolated experiments, or aspirational plans.

## Repository readiness: 0–10

Score each criterion from 0 to 2:

- `0` — absent, contradicted, unusable, or materially stale;
- `1` — partial, informal, difficult to discover, or not reliably runnable;
- `2` — explicit, current, discoverable, and usable by a cold-start agent.

### R1. Agent entry instructions

Look for root and nested `AGENTS.md`, `CLAUDE.md`, or equivalents. They should name key paths, commands, constraints, review expectations, and where deeper context lives.

### R2. Project map and durable memory

Look for indexed documentation, module maps, specifications, decisions, glossaries, handoffs, or progress-state conventions. Documentation should preserve intent rather than merely restate code.

### R3. Architecture described top-down

Look for system boundaries, dependency direction, data flows, external integrations, schemas, and architectural invariants that match the implementation.

### R4. Explicit quality rules

Look for stack-specific conventions covering errors, logging, tests, APIs, UI or domain behavior, security, accessibility, performance, and forbidden approaches.

### R5. Working feedback loop

Look for documented and runnable lint, typecheck, test, build, security, smoke, UI, or end-to-end checks. Required CI gates matter more than optional local commands.

Interpretation:

- `0–3`: not ready;
- `4–6`: partially ready;
- `7–8`: mostly ready;
- `9–10`: AI-coding ready.

## Team maturity: S0–S4

Team maturity requires a completed interview. Repository evidence may corroborate team practices but cannot establish a team stage by itself.

- `S0 Improvised` — AI use is absent or accidental; outcomes depend on individuals.
- `S1 Assisted` — people use AI for suggestions under close supervision, without a shared operating system.
- `S2 Delegated` — bounded work is delegated through repeatable context, review, and verification practices.
- `S3 Orchestrated` — the team owns reusable workflows, risk tiers, gates, handoffs, and operational visibility.
- `S4 Autonomous` — guarded agent loops execute meaningful work independently and demonstrably improve the engineering system.

Use [rubric.json](rubric.json) as the canonical set of stage controls. A dimension reaches a stage only when its control for that stage and every lower stage is `met`. `partial`, `not_met`, and `unverified` stop progression.

## Nine load-bearing dimensions

1. **Intent and specification** — durable goals, constraints, non-goals, acceptance criteria, and decision rationale precede implementation.
2. **Context, memory, and harness** — agents receive maintained project context, reusable task guidance, and resumable state.
3. **Autonomy and orchestration** — delegation tiers, stop conditions, isolation, maker/checker separation, and autonomous loops are deliberate.
4. **Verification and review** — review depth follows risk; humans retain accountability; AI-specific failure modes are checked.
5. **Tests and deterministic gates** — executable tests and immovable CI gates carry more weight than plausible generated output.
6. **Safety, security, and governance** — permissions, secrets, destructive actions, untrusted input, privacy, provenance, and production boundaries are controlled.
7. **Comprehension and judgment** — engineers understand what ships, preserve system rationale, and resist rubber-stamping.
8. **Reusable capability and learning** — prompts, skills, rules, hooks, and recurring lessons become maintained shared capability.
9. **Measurement, cost, and compounding** — the team measures quality, rework, incidents, cost, traceability, and improvement over time.

## Source note

This model combines and substantially restructures two user-provided inputs: the `ai-coding-readiness-audit` repository checklist and the public [Agentic Engineering Maturity — Factory Edition](https://claude.ai/public/artifacts/20941cc9-6721-45df-9f86-7fdd6a40cf44), version 2026.06.0. The controls and wording here are purpose-built for an interactive evidence-based audit.
