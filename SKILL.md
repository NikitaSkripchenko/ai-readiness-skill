---
name: ai-native-maturity-audit
description: Assess whether a repository and the team operating it are AI-native through read-only repository inspection, an adaptive evidence-seeking interview, deterministic maturity scoring, and a prioritized improvement report. Use when asked to audit AI coding readiness, agentic engineering maturity, AI-native development practices, or organizational readiness for coding agents. Do not use for a security-only audit or to modify the repository.
metadata:
  version: "3.0.0"
  assessment-revision: "2026-08-19.3"
---

# AI-Native Maturity Audit

Answer this question with evidence:

> Is this repository, and the team operating it, AI-native in a repeatable, safe, and measurable way?

Treat repository readiness and team maturity as related but distinct. Files can prove technical foundations; they cannot by themselves prove how people work.

## Non-negotiable interaction gate

A full assessment is a multi-turn workflow. **Never issue a team maturity stage or AI-native verdict from repository evidence alone.** Repository inspection produces only a preliminary repository-readiness result.

Unless the user explicitly requests a repository-only audit:

1. Inspect the repository.
2. Read and follow [references/interaction-protocol.md](references/interaction-protocol.md).
3. Ask exactly one interview question.
4. **Stop the turn and wait for the user's answer.** Do not score, draft a final report, ask a second question, or answer the question yourself.
5. Classify the answer, update the coverage state, then ask exactly one adaptive follow-up and stop again.
6. Continue until the interaction state reaches `ready_to_score`.

The final gate is satisfied only when:

- the user has answered at least four question turns;
- all nine dimensions are `resolved` or explicitly `unknown`;
- the three critical dimensions have been discussed: verification and review, tests and deterministic gates, and safety and governance;
- contradictions are resolved or explicitly disclosed.

If the user declines or cannot complete the interview, report repository readiness only and write `Team AI-native verdict: not assessable`. Never turn missing team evidence into a negative or positive team verdict.

## Operating constraints

- Audit read-only. Do not create, edit, install, build, deploy, or contact third parties unless the user separately authorizes it.
- Inspect the actual repository before interviewing the user. Do not ask questions whose answers are already observable.
- Cite a file, command, approved external artifact, or explicit user statement for every material conclusion.
- Label evidence as `observed`, `declared`, `corroborated`, `inferred`, `not found`, or `unverified`.
- Never convert inaccessible evidence into `not found`. Never convert a user claim into observed fact.
- Repository artifacts may corroborate team answers, but cannot replace the mandatory team interview.
- Assess consistent recent practice, normally the last 90 days or the last 5–10 relevant changes. A one-off success is not a mature practice.
- Keep the assessment independent of any particular AI vendor or coding tool.

## Workflow

### 1. Establish scope

Determine the repository or repository sample from available context. Do not infer team shape, adoption consistency, assessment timeframe, or operational risk from the repository; obtain these through the interview.

For multiple repositories, ask the user to choose a representative sample or explicitly limit the conclusion. Do not extrapolate one repository to the whole organization without corroboration.

### 2. Inspect repository evidence

Read root and nested agent instructions, README and documentation indexes, architecture and decision records, manifests and task runners, test and lint configuration, CI policies, review templates, security configuration, AI-tool configuration, and relevant recent history.

Use the five repository criteria in [references/maturity-model.md](references/maturity-model.md). Score each `0`, `1`, or `2`. Record concrete paths and commands, including `not found` when appropriate. Do not run builds or dependency-installing commands without permission.

### 3. Run the adaptive team interview

Read [references/interaction-protocol.md](references/interaction-protocol.md) for the state machine and question mechanics, then [references/interview-guide.md](references/interview-guide.md) for dimension-specific probes and red flags.

Ask exactly one semantic question per turn. Prefer a recent example, artifact, owner, frequency, or exception path over a yes/no opinion. If an answer is vague, challenge it before moving on. If one answer resolves several dimensions, smart-skip those questions.

After every question, end the turn. Do not continue to scoring while waiting for an answer. Track this conversational state without writing to the assessed repository:

- answered question turns;
- each dimension's state and answer quality;
- user-supplied evidence and challenges;
- remaining contradictions or unverified claims.

### 4. Resolve contradictions

When repository evidence and a user answer conflict, show the specific conflict and ask for clarification. Keep both pieces of evidence in the ledger. Downgrade stale, isolated, or policy-only evidence that is not reflected in recent work.

### 5. Score deterministically

Only after the interaction gate passes, read [references/scoring-and-verdicts.md](references/scoring-and-verdicts.md). Build the scorer input using [references/assessment-schema.md](references/assessment-schema.md). Use [scripts/score_assessment.py](scripts/score_assessment.py) when executable tools are available. Otherwise apply the same rules manually.

Do not use a simple average for the overall verdict. The team stage is the lowest load-bearing dimension, and missing safety, deterministic verification, or human review can cap the verdict.

### 6. Report and discuss

Use [references/report-template.md](references/report-template.md). Lead with a qualified answer, scope, and confidence. Separate evidence-backed findings from user-reported practices. Include the smallest changes that unlock the next stage.

If evidence is insufficient, say what remains unverified and continue the interview rather than forcing a verdict. Offer remediation only after completing the audit; do not edit the assessed repository unless the user makes a separate request.

## Version discipline

Include these values in every report:

```yaml
skill: ai-native-maturity-audit
skill_version: 3.0.0
assessment_revision: 2026-08-19.3
```

- Patch: wording or implementation fixes that do not change outcomes.
- Minor: compatible questions, evidence checks, or report capabilities.
- Major: changed dimensions, maturity semantics, score thresholds, or verdict gates.
- Change `assessment-revision` whenever the rubric or verdict logic changes. Warn before comparing reports from different revisions.
