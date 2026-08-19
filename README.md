# AI-Native Maturity Audit

Version `1.0.1` · assessment revision `2026-08-19`

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

The skill audits read-only by default. It inspects repository evidence first, then asks only the organizational questions that cannot be answered from the repository.

## Verify the package

```sh
python3 /path/to/skill-creator/scripts/quick_validate.py .
python3 scripts/test_score_assessment.py
```

See the official OpenAI documentation for [building and installing Codex skills](https://learn.chatgpt.com/docs/build-skills).
