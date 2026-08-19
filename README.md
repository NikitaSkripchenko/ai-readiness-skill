# AI-Native Maturity Audit

Version `3.0.0` · assessment revision `2026-08-19.3`

This Codex skill determines whether a repository and the team operating it are AI-native. It combines read-only repository inspection, an adaptive team interview, evidence classification, deterministic scoring, and a prioritized maturity report.

## Install through a prompt

### From a Git repository

Replace the placeholder with the URL of the repository or the skill directory, then send this prompt to Codex:

```text
Use $skill-installer to install the ai-native-maturity-audit skill from:
<REPOSITORY_OR_SKILL_DIRECTORY_URL>

After installation, confirm that SKILL.md, references/, scripts/, and
agents/openai.yaml are present. Report the installed skill version and
assessment revision. If Codex does not detect the skill automatically, tell me
to restart Codex.
```

### From a local checkout

Open the checkout in Codex and send:

```text
Install the ai-native-maturity-audit folder from this checkout as a user-level
Codex skill under ~/.agents/skills. Preserve the entire folder, validate the
installed SKILL.md, and report its skill version and assessment revision.
Ask before writing outside the current workspace.
```

For a repository-scoped installation, use this prompt instead:

```text
Install the ai-native-maturity-audit folder from this checkout under
.agents/skills/ai-native-maturity-audit in the current repository. Preserve the
entire skill folder and validate the installed SKILL.md.
```

Codex loads user skills from `~/.agents/skills` and repository skills from `.agents/skills`. It normally detects new skills automatically; restart Codex if the skill does not appear.

## Run the audit

Invoke it explicitly:

```text
Use $ai-native-maturity-audit to assess whether this repository and the team
operating it are AI-native.
```

The skill audits read-only by default. A full assessment is deliberately multi-turn: it inspects repository evidence, asks one adaptive question per turn, challenges vague answers, smart-skips questions already supported by concrete evidence, and refuses to issue a team verdict until the interview reaches `ready_to_score`. A repository-only run reports readiness but marks team maturity as not assessable.

## Verify the package

```sh
python3 /path/to/skill-creator/scripts/quick_validate.py .
python3 scripts/test_score_assessment.py
```

See the official OpenAI documentation for [building and installing Codex skills](https://learn.chatgpt.com/docs/build-skills).
