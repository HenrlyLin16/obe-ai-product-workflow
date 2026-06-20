# GitHub Release Flow

Use this after confirmed QA Skill learnings are written back to the repo source.

## Source Of Truth

- `workflow/skills/qa/onebullex-android-qa`

Do not prepare a PR from the local Codex/Cursor mirrors.

## Suggested Branch Pattern

- `codex/onebullex-android-qa-<topic>`

Examples:

- `codex/onebullex-android-qa-adb-vpn`
- `codex/onebullex-android-qa-record-replay`

## Pre-Push Checklist

- Confirm only QA Skill files are in scope.
- Run Python compile checks and Skill validation.
- Sync mirrors with `scripts/sync-onebullex-android-qa-skill.sh`.
- Keep evidence, caches, screenshots, logs, and local mirror files out of the commit.

## PR Content

- What changed in the Skill
- How ADB stability, device control, VPN, or Record & Replay behavior changed
- What was validated
- Remaining risks or manual steps
- Links or paths to the latest QA report and learning summary

## Stop Conditions

- Unrelated dirty files are mixed into the change set
- Confirmed learnings have not yet been reviewed by a human
- Validation is missing or failing
- Sensitive information appears in generated artifacts or commit scope
