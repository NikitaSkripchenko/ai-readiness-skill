---
name: ai-native-maturity-audit
description: Assess whether a repository and the team operating it are AI-native through read-only repository inspection, an adaptive evidence-seeking interview, deterministic maturity scoring, and a prioritized improvement report. Use when asked to audit AI coding readiness, agentic engineering maturity, AI-native development practices, or organizational readiness for coding agents. Do not use for a security-only audit or to modify the repository.
metadata:
  version: "1.0.1"
  assessment-revision: "2026-08-19"
---

# AI-Native Maturity Audit

Answer this question with evidence:

> Is this repository, and the team operating it, AI-native in a repeatable, safe, and measurable way?

Treat repository readiness and team maturity as related but distinct. Files can prove technical foundations; they cannot by themselves prove how people work.

## Operating constraints

- Audit read-only. Do not create, edit, install, build, deploy, or contact third parties unless the user separately authorizes it.
- Inspect the actual repository before interviewing the user. Do not ask questions whose answers are already observable.
- Cite a file, command, approved external artifact, or explicit user statement for every material conclusion.
- Label evidence as `observed`, `declared`, `corroborated`, `inferred`, `not found`, or `unverified`.
- Never convert inaccessible evidence into `not found`. Never convert a user claim into observed fact.
- Assess consistent recent practice, normally the last 90 days or the last 5–10 relevant changes. A one-off success is not a mature practice.
- Keep the assessment independent of any particular AI vendor or coding tool.

## Workflow

### 1. Establish scope

Determine the repository or repository sample, team shape, assessment timeframe, and whether production, regulated, privacy-sensitive, or safety-critical systems are involved. If the current repository and a single team are obvious, proceed without asking.

For multiple repositories, ask the user to choose a representative sample or explicitly limit the conclusion. Do not extrapolate one repository to the whole organization without corroboration.

### 2. Inspect repository evidence

Read root and nested agent instructions, README and documentation indexes, architecture and decision records, manifests and task runners, test and lint configuration, CI policies, review templates, security configuration, AI-tool configuration, and relevant recent history.

Use the five repository criteria in [references/maturity-model.md](references/maturity-model.md). Score each `0`, `1`, or `2`. Record concrete paths and commands, including `not found` when appropriate. Do not run builds or dependency-installing commands without permission.

### 3. Run the adaptive team interview

Read [references/interview-guide.md](references/interview-guide.md). Ask one to three focused questions per round. Prefer a recent example, artifact, owner, frequency, or exception path over a yes/no opinion.

Start at the lowest uncertain maturity rung in each dimension. Stop asking advanced questions when a lower prerequisite is not met, unless the user explicitly wants a future-state gap analysis. Reinterpret team controls for a solo operator; do not simply waive them.

### 4. Resolve contradictions

When repository evidence and a user answer conflict, show the specific conflict and ask for clarification. Keep both pieces of evidence in the ledger. Downgrade stale, isolated, or policy-only evidence that is not reflected in recent work.

### 5. Score deterministically

Read [references/scoring-and-verdicts.md](references/scoring-and-verdicts.md). Build the scorer input using [references/assessment-schema.md](references/assessment-schema.md). Use [scripts/score_assessment.py](scripts/score_assessment.py) when executable tools are available. Otherwise apply the same rules manually.

Do not use a simple average for the overall verdict. The team stage is the lowest load-bearing dimension, and missing safety, deterministic verification, or human review can cap the verdict.

### 6. Report and discuss

Use [references/report-template.md](references/report-template.md). Lead with a qualified answer, scope, and confidence. Separate evidence-backed findings from user-reported practices. Include the smallest changes that unlock the next stage.

If evidence is insufficient, say what remains unverified and continue the interview rather than forcing a verdict. Offer remediation only after completing the audit; do not edit the assessed repository unless the user makes a separate request.

## Version discipline

Include these values in every report:

```yaml
skill: ai-native-maturity-audit
skill_version: 1.0.1
assessment_revision: 2026-08-19
```

- Patch: wording or implementation fixes that do not change outcomes.
- Minor: compatible questions, evidence checks, or report capabilities.
- Major: changed dimensions, maturity semantics, score thresholds, or verdict gates.
- Change `assessment-revision` whenever the rubric or verdict logic changes. Warn before comparing reports from different revisions.
