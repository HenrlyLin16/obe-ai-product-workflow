# OneBullEx Web QA GitHub Release Flow

Use this reference only after confirmed Skill changes are written to the repo source.

## Source Scope

The source of truth is `/Users/jingxing/Desktop/Onebullex/workflow/skills/qa/onebullex-web-qa`.

Do not commit generated mirrors, evidence, raw recordings, caches, credentials, or screenshots unless explicitly requested and reviewed.

## Branching

- Default branch prefix: `codex/onebullex-web-qa-*`.
- Do not push directly to `main` by default.
- Use PR review for Skill changes.

## Release Readiness Gate

Before PR:

- Python compile passes.
- Flow lint passes.
- At least one dry-run passes.
- Public flow changes have public flow evidence.
- Auth/trade changes have dry-run plus interactive evidence or clearly documented gaps.
- `scripts/sync-onebullex-web-qa-skill.sh --check` passes or mirror drift is documented before syncing.
- Git diff contains only intended source files.

## PR Description

Include:

- Change summary.
- Validation performed.
- Not validated / known gaps.
- Clash VPN requirements or limitations.
- High-risk flow impact.
- Evidence paths or report summary.
