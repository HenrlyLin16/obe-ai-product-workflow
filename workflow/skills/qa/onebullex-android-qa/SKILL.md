---
name: onebullex-android-qa
description: Run OneBullEx Android QA with plan-first new-requirement workflow, APK latest-package gates, USB/Wi-Fi adb, selector-driven uiautomator flows, YAML Flow DSL, evidence/report generation, screenshot-backed UX/UI walkthroughs, dev-login and dry-run trade flow safety gates, and human-confirmed Zentao bug drafts. Use when testing OneBullEx Android packages, checking dev/prod APK freshness, solidifying AI-discovered mobile flows, validating market/asset/login/futures flows, reading Lark QA requirements, or preparing confirmed Android QA findings for Zentao through Chrome.
---

# OneBullEx Android QA

Use this skill to run deterministic Android QA for OneBullEx dev builds. Prefer uiautomator XML selectors and Flow DSL over screenshots or raw coordinates. Screenshots are evidence, not the primary reasoning surface.

## Source And Mirrors

- Repo source of truth: `/Users/jingxing/Desktop/Onebullex/workflow/skills/qa/onebullex-android-qa`.
- Codex runtime mirror: `/Users/jingxing/.codex/skills/onebullex-android-qa`.
- Cursor runtime mirror: `/Users/jingxing/Desktop/Onebullex/.cursor/skills/onebullex-android-qa`.
- Edit the repo source, then sync mirrors with `scripts/sync-onebullex-android-qa-skill.sh` from `/Users/jingxing/Desktop/Onebullex`.

## Quick Start

Run all stable flows after the APK version gate passes:

```bash
python3 /Users/jingxing/.codex/skills/onebullex-android-qa/scripts/adb_obx_qa.py --serial SM02G4061923909 --flow all --channel dev
```

Run one flow:

```bash
python3 /Users/jingxing/.codex/skills/onebullex-android-qa/scripts/adb_obx_qa.py --serial SM02G4061923909 --flow market-sort.yaml
```

Check package freshness only:

```bash
python3 /Users/jingxing/.codex/skills/onebullex-android-qa/scripts/adb_obx_qa.py --version-check-only --channel dev --serial SM02G4061923909
```

Dry-run without a device:

```bash
python3 /Users/jingxing/.codex/skills/onebullex-android-qa/scripts/adb_obx_qa.py --dry-run --flow all --channel dev
```

Evidence levels:

```bash
--evidence-level minimal   # XML + summary, screenshots only on failure
--evidence-level normal    # key snapshots + failures; default
--evidence-level full      # every step screenshot/XML/logcat
```

## Workflow

1. For any new feature, new requirement, new page, or new flow automation task, first read `references/test-task-planning-policy.md`, produce a test plan, and wait for explicit human confirmation before executing.
2. Read Lark/Feishu requirements when available; if auth is unavailable, ask for pasted/exported requirements.
3. Discover/connect the Android device with adb. Defaults: `SM02G4061923909`, channel `dev`, package `com.onemore.onebullex.dev`, activity `com.icy.neptune.MainActivity`.
4. Before every non-dry-run execution, run the APK version gate from `references/package-version-gate.md`; continue only when status is `latest` or the user explicitly accepts `--skip-version-check`.
5. Execute YAML flows with `scripts/flow_runner.py` or the compatibility wrapper `scripts/adb_obx_qa.py`.
6. Review Markdown and JSON reports. Treat `automation_issue`, `environment_blocker`, and `requirement_unclear` as Skill/QA follow-up, not product bugs by default.
7. Review `qa-experience-summary.md` and `qa-skill-optimization-confirm.template.json`; only confirmed learning items may be used to optimize this Skill.
8. After confirmed Skill changes, sync Codex and Cursor mirrors with `scripts/sync-onebullex-android-qa-skill.sh`.
9. Only after human confirmation, generate Zentao drafts with `scripts/zentao_bug_draft.py`.
10. If filing bugs in Chrome, fill Zentao but stop before `保存` until the user explicitly confirms the destination, account, title, body, and attachments.


## APK Version Gate

- Default channel is `dev`: `https://app-space.1bullex.com/android-dev-onebullex`, package `com.onemore.onebullex.dev`.
- Production channel uses `https://app-space.1bullex.com/android-onebullex`, package `com.onemore.onebullex`, and requires explicit user selection.
- Non-dry-run QA is blocked unless `scripts/apk_version_guard.py` reports `latest` or the user explicitly requests `--skip-version-check`.
- `outdated`, `not_installed`, or `unknown` are environment blockers. Ask the user before downloading/installing or accepting the risk.
- `--allow-install-latest` means the user already confirmed install; prefer direct APK download plus `adb install -r`, otherwise open the app-space page on the phone and require manual/visible install confirmation.

Read `references/package-version-gate.md` before changing package freshness or install behavior.

## Planning Policy

For new feature/new requirement automation, read `references/test-task-planning-policy.md` and produce a plan first. Existing stable regression flows may run directly only after the APK version gate passes and only when no new selectors/assertions/pages are being introduced.

## Flow System

- Stable flows live in `flows/*.yaml`.
- `scripts/ui_driver.py` provides `dump_xml`, `find_node`, `tap_selector`, `input_text`, `wait_until`, and evidence helpers.
- `scripts/flow_runner.py` executes Flow DSL and writes:
  - `onebullex-android-qa-report.md`
  - `onebullex-android-qa-report.json`
  - `confirmed-bugs.template.json`
  - `qa-experience-summary.md`
  - `qa-skill-optimization-candidates.json`
  - `qa-skill-optimization-confirm.template.json`
  - `flows-used/`
  - per-step `ui.xml`, `ui-summary.txt`, optional screenshots/logcat

Read `references/flow-format.md` before adding or changing flows.

## Learning Loop

Every automated QA run must leave a Skill learning review in the evidence directory. Read `references/qa-learning-loop.md` before applying those learnings.

Default review flow:

```bash
python3 /Users/jingxing/Desktop/Onebullex/workflow/skills/qa/onebullex-android-qa/scripts/skill_learning_review.py \
  --apply-confirmed /tmp/onebullex-android-qa/<run>
```

Only after human confirmation, write confirmed learnings back to the repo source:

```bash
python3 /Users/jingxing/Desktop/Onebullex/workflow/skills/qa/onebullex-android-qa/scripts/skill_learning_review.py \
  --apply-confirmed \
  --write-skill \
  /tmp/onebullex-android-qa/<run>
```

Then sync runtime mirrors:

```bash
cd /Users/jingxing/Desktop/Onebullex
scripts/sync-onebullex-android-qa-skill.sh
```

Do not promote unconfirmed product bugs, environment blockers, credentials, or one-off device/network behavior into this Skill.

For the `实时盯盘浮窗` requirement, read `references/watch-monitor-prd-notes.md` and prefer the dedicated flows:

- `watch-monitor-entry.yaml`
- `watch-monitor-enable-add.yaml`
- `watch-monitor-float-interactions.yaml`
- `watch-monitor-manage-list.yaml`
- `watch-monitor-cross-page.yaml`
- `watch-monitor-ux-ui.yaml`

When running this requirement on a device that already has an accepted-but-unverified dev build, pass:

```bash
python3 /Users/jingxing/.codex/skills/onebullex-android-qa/scripts/adb_obx_qa.py \
  --serial SM02G4061923909 \
  --channel dev \
  --accept-version-gate-risk \
  --requirement-doc 'https://wsgysqudq8b5.sg.larksuite.com/docx/OiJSdNXg0ohwOOxLQJ1ldpchgEd?from=from_copylink' \
  --device-start-state 'logged-in; reachable K-line settings required'
```

## AI Explore Once, Then Solidify

For a new screen or operation:

1. Use XML summaries and, only when necessary, screenshots to discover the path.
2. Prefer stable `content-desc/resource-id` selectors; use text selectors next.
3. Add fallback coordinates only as temporary compatibility.
4. Write the confirmed path into `flows/*.yaml`.
5. Re-run the flow. Do not rely on fresh AI exploration for repeated regression runs.

## Developer Collaboration

Ask Android developers to add stable automation IDs listed in `references/android-test-id-guidelines.md`. This is the highest leverage improvement for speed and reliability.

## High-risk Flows

- `login-dev.yaml` reads `OBX_TEST_USERNAME` and `OBX_TEST_PASSWORD`; never store credentials in the Skill.
- `futures-open-position-dry-run.yaml` is blocked by default before final order confirmation.
- Do not pass `--allow-side-effects` unless the user has explicitly approved the account, environment, symbol, direction, quantity, leverage, and final action.
- Production/real-asset trading side effects are out of scope by default.

## UX/UI Screenshot Walkthrough

Run the final screenshot-backed UX/UI review after functional flows:

```bash
python3 /Users/jingxing/.codex/skills/onebullex-android-qa/scripts/adb_obx_qa.py \
  --serial SM02G4061923909 \
  --flow ux-ui-walkthrough.yaml \
  --evidence-level normal
```

Then build the UX/UI review pack:

```bash
python3 /Users/jingxing/.codex/skills/onebullex-android-qa/scripts/ux_ui_review_pack.py /tmp/onebullex-android-qa/<run>
```

Use `references/ux-ui-checklist.md` and `references/onebullex-core-ui-review.md` as the review criteria. UX findings must cite screenshot evidence and a checklist/core-rule basis. P0/P1 issues that block use, mislead users, create funds risk, or break core component consistency may become bug candidates after human confirmation. `visual_polish` and `needs_design_confirmation` stay as design debt by default.

## Zentao Drafts

Generate drafts only from confirmed product bug candidates:

```bash
python3 /Users/jingxing/.codex/skills/onebullex-android-qa/scripts/zentao_bug_draft.py /tmp/onebullex-android-qa/<run>/confirmed-bugs.template.json
```

Chrome/Zentao safety rules:

- Use existing Chrome login state and prefer `Henrly linjinhong16@gmail.com`.
- Do not inspect cookies, passwords, local storage, or profile internals.
- Stop on login, CAPTCHA, account mismatch, or permission prompts.
- Stop before clicking `保存`; submit only after explicit user confirmation.
