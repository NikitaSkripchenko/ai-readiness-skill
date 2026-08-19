# Adaptive interview guide

## Interview posture

The interview fills evidence gaps; it is not a survey to recite. Inspect first, then ask the smallest useful question. Ask one to three questions per turn and briefly explain why the answer affects the verdict.

Use professional prompts that request observable behavior:

- Weak: “Does your team review AI code?”
- Strong: “For the last two AI-assisted production changes, who owned approval, which checks were required, and was either change sent back?”

Accept “I don't know.” Record it as `unverified`, not as failure or success.

## Opening scope questions

Ask only what cannot be inferred:

1. What does this assessment cover: this repository, a team owning several repositories, or a broader organization?
2. How many people contribute, what roles do they play, and how consistently do they use coding agents?
3. Which recent period or set of changes is representative? Default to 90 days or 5–10 relevant changes.
4. Does the system touch production, regulated data, sensitive customer information, money movement, physical safety, or other high-impact operations?

## Branching logic

### Solo operator

Translate “team standard” into repeatability across time and future handoff. Ask whether a cold-start session or another engineer could reproduce the workflow. Ownership, review, and stopping rules still apply; self-review alone cannot establish maker/checker separation on high-risk work.

### Multiple repositories

Ask for a representative sample by criticality and workflow, not convenience. Score repositories separately when practices materially differ. Limit the organization-level verdict to corroborated shared standards.

### Low or occasional AI use

Establish S0/S1 accurately. Do not interrogate S3/S4 orchestration. Ask what prevents safe delegation and produce foundational next steps.

### Claimed S3 or S4 maturity

Require at least two recent examples or one durable control plus evidence of routine use. Ask for owners, exception paths, audit trails, trends, and a failure that changed the system. Policy-only answers cannot establish S3/S4.

### Production, regulated, or high-impact systems

Expand safety questions: data classification, model/provider approval, retention, access scope, audit logs, incident response, mandatory human approval, sandboxing, and prohibited actions. A missing critical control caps the verdict.

### Inaccessible trackers, dashboards, or private policy systems

Let the user summarize them, but label the result `declared` or `unverified`. Offer a list of artifacts that would raise confidence. Do not request secrets, personal data, or sensitive raw logs.

### Contradictory evidence

State the exact conflict neutrally: “The team reports required typechecking, but this repository's required CI workflow does not run it.” Ask whether another system enforces the rule. Preserve both facts in the report.

## Dimension question routes

Start with the lowest uncertain stage. Advance only when the previous answer is supported.

### D1. Intent and specification

- S1: How is intent communicated before an AI-assisted change begins?
- S2: Show or describe two recent non-trivial changes whose specs predated implementation.
- S3: Which decisions require durable rationale, and how does review reject incomplete intent?
- S4: How is missing or stale intent detected and repaired across workflows?

### D2. Context, memory, and harness

- S1: What context does each developer manually assemble for an agent?
- S2: Can a cold-start agent discover boundaries, commands, and architecture without oral guidance?
- S3: Who owns shared rules, skills, hooks, and long-running task handoffs?
- S4: What evidence shows the harness improves outcomes across repositories or teams?

### D3. Autonomy and orchestration

- S1: Which tasks are suggestion-only, and which may the agent execute?
- S2: What bounded workflows can agents complete, and when must they stop?
- S3: How are work isolation, maker/checker separation, parallelism, and review capacity managed?
- S4: Which autonomous loops run routinely, and what limits blast radius and duration?

### D4. Verification and review

- S1: Who reads and owns AI-assisted changes before merge?
- S2: How does review depth change with risk, and which AI-specific failures are checked?
- S3: What evidence must accompany a PR, and when is an independent reviewer required?
- S4: How does triage route low-risk work while escalating suspicious or expensive changes?

### D5. Tests and deterministic gates

- S1: Which checks are normally run after generation?
- S2: Which gates are required and cannot be bypassed to merge?
- S3: How do you catch weakened tests, dropped thresholds, or behavior rewritten to fit output?
- S4: Which critical paths use mutation, property, differential, or equivalent high-signal testing?

### D6. Safety, security, and governance

- S1: What are agents explicitly forbidden to access or change?
- S2: How are secrets, permissions, generated-code provenance, and production access controlled?
- S3: How are third-party tools vetted, destructive actions blocked, and untrusted input sandboxed?
- S4: What audit or incident evidence shows the controls work across the organization?

### D7. Comprehension and judgment

- S1: How do engineers demonstrate they understand generated changes?
- S2: Which behaviors are considered unsafe surrender, and how are they challenged?
- S3: Who retains the mental model for load-bearing systems, and how is AI literacy taught by role?
- S4: How does the organization protect time and authority for engineering judgment as output grows?

### D8. Reusable capability and learning

- S1: What useful prompts or workflows are reused today?
- S2: Where are shared agent instructions, templates, or skills versioned and reviewed?
- S3: How do repeated failures become hooks, tests, rules, or reviewer checks?
- S4: What capability is shared across repositories, evaluated, and retired when obsolete?

### D9. Measurement, cost, and compounding

- S1: What, if anything, is measured about AI-assisted work?
- S2: Can the team see adoption, cost, provenance, rework, and quality signals?
- S3: Who reviews the metrics, and how are AI-related incidents or regressions analyzed?
- S4: What trend proves quality is stable or improving as agent-driven volume increases?

## Closing questions

Before finalizing, ask only if still unclear:

1. Which answer is least representative of normal work?
2. Which missing artifact could materially change the verdict?
3. Is there an important exception for critical systems or specific teams?

