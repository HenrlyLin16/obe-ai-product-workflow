# OneBullEx Android QA Report Format

Use this reference when editing or extending `onebullex-android-qa-report.md`.

## Required Sections

1. `# OneBullEx Android QA Report`
2. Generated time, evidence directory, and pass/fail/blocked summary.
3. `## Environment`: device serial, model, Android version if available, channel, package, activity, screen size, density, and foreground app signal.
4. `## APK Version Gate`: status, device version, remote version, APK URL when known, and recommended action.
5. `## Setup Notes`: adb connection mode, app launch result, package gate result, and any requirement source such as Lark URL.
6. `## Test Matrix`: one row per step with status, notes, screenshot, UI summary, and log link.
7. `## Suspected Bugs For Human Review`: tells the user to mark `confirmed: true` in `confirmed-bugs.template.json`.
8. For requirement-specific runs such as `实时盯盘浮窗`, add a short summary covering requirement source, package-gate exception, executed watch-monitor flows, overlay findings, and selector fallback risks.
9. `## Skill Learning Review`: links to `qa-experience-summary.md`, `qa-skill-optimization-candidates.json`, `qa-skill-optimization-confirm.template.json`, and `flows-used/`.

## Status Meaning

- `pass`: the step ran and available evidence supports expected behavior.
- `fail`: the step ran and evidence contradicts expected behavior.
- `blocked`: setup, auth, lock screen, unstable UI, missing requirement, or parser ambiguity prevents a product judgment.
- `environment_blocker`: package is not latest, not installed, unknown, device locked, auth missing, or setup prevents a reliable product judgment.

## Writing Rules

- Keep evidence paths exact and local; do not copy large logs into the report.
- Separate product defects from setup blockers.
- For sorting checks, include the observed first rows and detected order when available.
- For suspected bugs, use the structure `[步骤] / [结果] / [期望]` so it can be copied into Zentao.
- Avoid filing a bug solely because a parser could not infer the screen; include screenshots/XML for manual review instead.
- Do not file product bugs from stale, missing, or unknown APK status. Record those as environment blockers.
- Do not silently optimize the Skill from a run. Generate learning artifacts first, then require human confirmation.

## Human Confirmation Checklist

Before drafting Zentao bugs, confirm for each issue:

- Is this expected behavior according to PRD/Lark requirements?
- Is the reproduction stable on a clean app state?
- Which evidence files should be attached?
- What severity and priority should be used?
- Should similar findings be grouped into one bug or filed separately?

## Skill Learning Checklist

Before updating the QA Skill from a run:

- Is the learning repeatable and supported by XML, screenshot, or report evidence?
- Is it a flow/selector/documentation/environment improvement rather than a product bug?
- Has the candidate been marked `confirmed: true` in `qa-skill-optimization-confirm.template.json`?
- Will the change be written to the repo source under `workflow/skills/qa/onebullex-android-qa`?
- After writing, has `scripts/sync-onebullex-android-qa-skill.sh` been run to update Codex and Cursor mirrors?

## UX/UI Finding Format

UX/UI screenshot findings must include:

- `id`: stable finding id.
- `category`: one of `ux_blocker`, `ui_inconsistency`, `copy_issue`, `accessibility_issue`, `visual_polish`, `needs_design_confirmation`.
- `severity`: `P0`, `P1`, or `P2`.
- `bug_candidate`: true only for P0/P1 issues that should be considered for Zentao after human confirmation.
- `page`: page or flow checkpoint.
- `screenshot`: local screenshot evidence path.
- `check_item`: UX checklist/core UI rule used for judgment.
- `phenomenon`: what is visible or what happened.
- `impact`: user impact.
- `suggestion`: expected behavior or repair direction.

Default policy:

- P0/P1 `ux_blocker`, `ui_inconsistency`, `copy_issue`, and `accessibility_issue` can become bug candidates.
- `visual_polish` and `needs_design_confirmation` are design debt by default, not Zentao bugs.
- Every UX/UI bug candidate must cite screenshot evidence.
