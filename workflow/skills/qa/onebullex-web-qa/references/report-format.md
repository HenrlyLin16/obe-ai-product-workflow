# OneBullEx Web QA Report Format

Use this reference when editing or extending `onebullex-web-qa-report.md`.

## Required Sections

1. `# OneBullEx Web QA Report`
2. Generated time, evidence directory, and pass/fail/blocked summary.
3. `## Environment`: site URL, locale, browser mode, viewport, CDP/userDataDir info, Playwright version.
4. `## Environment Health Gate`: health check items with pass/fail/blocked status, `environment-health-check.json` link.
5. `## Browser & Viewport`: mode (`iab`/`chrome`), viewport (`desktop`/`mobile`/`both`), locale, CDP endpoint or userDataDir path.
6. `## Account State`: expected profile vs actual profile, probe results, match status.
7. `## Setup Notes`: health gate result, login result, `--skip-health-check` if used, requirement source if any.
8. `## Test Matrix`: one row per step with status, notes, DOM summary, screenshot link.
9. `## Cross-Viewport Consistency`: present when `--viewport both`; compares desktop vs mobile rendering.
10. `## Page vs Result Verification`: dual verification summary per trading assertion.
11. `## Suspected Bugs For Human Review`: tells the user to mark `confirmed: true` in `confirmed-bugs.template.json`.
12. `## Skill Learning Review`: links to `qa-experience-summary.md`, `qa-skill-optimization-candidates.json`, `qa-skill-optimization-confirm.template.json`, and `flows-used/`.

## Status Meaning

- `pass`: the step ran and available evidence supports expected behavior.
- `fail`: the step ran and evidence contradicts expected behavior.
- `blocked`: setup, auth, selector ambiguity, DOM instability, missing requirement, or parser ambiguity prevents a product judgment.
- `environment_blocker`: health gate failure, site unreachable, account profile mismatch, or setup prevents a reliable product judgment.
- `service_degradation`: maintenance banner, WS silent, or partial API issues — blocks trading flows but not public-page flows.

## Writing Rules

- Keep evidence paths exact and local; do not copy large logs into the report.
- Separate product defects from setup blockers and service degradation.
- For sort checks, include the observed first N rows and detected order when available.
- For suspected bugs, use the structure `[步骤] / [结果] / [期望]` so it can be copied into Zentao.
- Avoid filing a bug solely because a DOM parser could not interpret the page; include screenshots/DOM summaries for manual review instead.
- Do not file product bugs from health gate failures or account profile mismatches. Record those as environment blockers.
- Do not silently optimize the Skill from a run. Generate learning artifacts first, then require human confirmation.
- For `--viewport both` runs, document viewport-specific differences and classify by impact.

## Human Confirmation Checklist

Before drafting Zentao bugs, confirm for each issue:

- Is this expected behavior according to PRD requirements?
- Is the reproduction stable with a clean browser session?
- Which evidence files should be attached?
- What severity and priority should be used?
- Should similar findings be grouped into one bug or filed separately?

## Skill Learning Checklist

Before updating the QA Skill from a run:

- Is the learning repeatable and supported by DOM, screenshot, or report evidence?
- Is it a flow/selector/documentation/environment improvement rather than a product bug?
- Has the candidate been marked `confirmed: true` in `qa-skill-optimization-confirm.template.json`?
- Will the change be written to the repo source under `workflow/skills/qa/onebullex-web-qa`?
- After writing, has `scripts/sync-onebullex-web-qa-skill.sh` been run to update Codex and Cursor mirrors?

## UX/UI Finding Format

UX/UI screenshot findings must include:

- `id`: stable finding id.
- `category`: one of `ux_blocker`, `ui_inconsistency`, `copy_issue`, `accessibility_issue`, `visual_polish`, `needs_design_confirmation`.
- `severity`: `P0`, `P1`, or `P2`.
- `bug_candidate`: true only for P0/P1 issues that should be considered for Zentao after human confirmation.
- `page`: page or flow checkpoint.
- `viewport`: `desktop`, `mobile`, or `both`.
- `screenshot`: local screenshot evidence path.
- `check_item`: UX checklist/core UI rule used for judgment.
- `phenomenon`: what is visible or what happened.
- `impact`: user impact.
- `suggestion`: expected behavior or repair direction.

Default policy:

- P0/P1 `ux_blocker`, `ui_inconsistency`, `copy_issue`, and `accessibility_issue` can become bug candidates.
- `visual_polish` and `needs_design_confirmation` are design debt by default, not Zentao bugs.
- Every UX/UI bug candidate must cite screenshot evidence.
- Cross-viewport findings (desktop vs mobile inconsistency) are tagged `both` and may be treated as `ui_inconsistency`.

## Professional QA Extensions

Reports also include:

- `## Test Level & Risk`: L0-L4 level, risk, side-effect level.
- `## Clash VPN Gate`: app path, app running, system proxy, traffic `>0kb`, HTTP/REST/WS probes, manual confirmation.
- `## Preconditions`: account, health, VPN, data, and safety preconditions.
- `## Oracle Coverage`: DOM/API/WS/state/visual/negative coverage.
- `## Route & Selector Stability`: route-backed selectors and fallback notes.
- `## Flakiness Notes`: fixed sleeps, retry policy, inconclusive evidence.
- `## Evidence Index`: local evidence files grouped by flow.
- `## Release Readiness`: PR readiness checks when requested.

A product bug should not be drafted unless oracle evidence rules in `references/oracle-policy.md` are satisfied.
