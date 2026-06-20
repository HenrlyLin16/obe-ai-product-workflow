---
name: onebullex-web-qa
description: Run OneBullEx Web testnet QA with plan-first new-requirement workflow, CEX environment health gate, account profile matrix, dual-browser (iab/chrome) Playwright strategy, YAML Flow DSL with DOM/API/WS assertions, evidence/report generation, UI/UX screenshot walkthroughs, dry-run trade flow safety gates with granular side-effect controls, and human-confirmed Zentao bug drafts. Use for OneBullEx Web testnet testing, 中文站回归, 行情/现货/合约/资产/订单/奖励/Spartans/Referral 流程验证, 交易提交流程演练 (dry-run + 细粒度放行), UX/UI 截图走查, and preparing confirmed QA findings for Zentao.
---

# OneBullEx Web QA

Use this skill to run deterministic Web QA for OneBullEx testnet (`https://testnet.1bullex.com/`). Prefer DOM selectors and Flow DSL over screenshots or raw coordinates. Screenshots are evidence, not the primary reasoning surface. All flows default to `locale=zh-cn`.

Two execution modes are supported:

- `runtime=codex`: preferred. Use Codex Browser/Chrome plugins as the live execution surface. This is the default for interactive QA and any flow that depends on existing login state.
- `runtime=playwright`: local runner. Use it for stateless/public-page regression and CLI validation outside Codex plugin execution.


## Professional QA Platform Upgrade

This Skill now uses a layered QA model. Read these references before changing flows or execution behavior:

- `references/test-levels.md` — L0/L1/L2/L3/L4 execution boundaries and required metadata.
- `references/clash-vpn-gate.md` — Mac ClashX Pro VPN gate. VPN is usable only when ClashX Pro is running, `设置为系统代理` is enabled, QA probes generate traffic, and menu-bar traffic is confirmed `>0kb`.
- `references/test-data-policy.md` — account profile, masking, state residue, and high-risk data rules.
- `references/oracle-policy.md` — required DOM/API/WS/state/visual/negative oracle coverage.
- `references/record-replay-policy.md` — Record & Replay quality gate and candidate-only promotion rules.
- `references/anti-flaky-policy.md` — waiting, retry, failure classification, and minimum evidence rules.
- `references/github-release-flow.md` — release-readiness and PR checklist for confirmed source changes.

Test levels:

| Level | Scope | Default execution |
|-------|-------|-------------------|
| `L0` | Environment health gate | Playwright/iab or dry-run |
| `L1` | Public smoke and market data | Playwright/iab |
| `L2` | Login/account/assets/orders state | Codex Chrome |
| `L3` | Transaction or withdraw dry-run to `safety_gate` | Codex Chrome |
| `L4` | UX/UI screenshot walkthrough | split by page/viewport |

`all-public` must stay L0+L1. `all-auth` must stay L0+L2+L3 dry-run. UX/UI flows are explicit, not default functional regression.

Record & Replay can be used to capture an expert-demonstrated browser path, but recordings only generate candidates (`flow_seed`, `route_candidate`, `selector_candidate`, `assertion_candidate`, `test_id_request`, or `do_not_promote`). Formal regression still requires route-backed selectors, Flow DSL, oracle metadata, and human-confirmed promotion.

## Source And Mirrors

- Repo source of truth: `/Users/jingxing/Desktop/Onebullex/workflow/skills/qa/onebullex-web-qa`.
- Codex runtime mirror: `/Users/jingxing/.codex/skills/onebullex-web-qa`.
- Cursor runtime mirror: `/Users/jingxing/Desktop/Onebullex/.cursor/skills/onebullex-web-qa`.
- Edit the repo source, then sync mirrors with `scripts/sync-onebullex-web-qa-skill.sh` from `/Users/jingxing/Desktop/Onebullex`.
- After syncing into `~/.codex/skills/onebullex-web-qa`, Codex can discover it as a selectable Skill via `agents/openai.yaml`.

## Quick Start

Run all public-page stable flows through the local Playwright runner (`iab`, no login):

```bash
python3 /Users/jingxing/Desktop/Onebullex/workflow/skills/qa/onebullex-web-qa/scripts/web_obx_qa.py \
  --flow all-public \
  --runtime playwright \
  --browser-mode iab \
  --viewport desktop \
  --locale zh-cn \
  --evidence-level normal
```

Validate authenticated flow definitions locally without live browser actions:

```bash
python3 /Users/jingxing/Desktop/Onebullex/workflow/skills/qa/onebullex-web-qa/scripts/web_obx_qa.py \
  --dry-run \
  --flow account-state.yaml \
  --browser-mode chrome \
  --account-profile basic-login \
  --environment-profile testnet
```

Run live interactive Codex execution for account/trade flows:

Use `$onebullex-web-qa` in Codex and choose `browser_mode=chrome` for login/account/trade flows. The Browser/Chrome plugins perform the live actions; the Skill conventions, routes, reports, and learning loop define how to execute and record them.

Health check flow dry-run / precheck only (live checks use Browser plugin + helper scripts):

```bash
python3 /Users/jingxing/Desktop/Onebullex/workflow/skills/qa/onebullex-web-qa/scripts/web_obx_qa.py \
  --health-check-only \
  --browser-mode iab
```

Dry-run without a browser:

```bash
python3 /Users/jingxing/Desktop/Onebullex/workflow/skills/qa/onebullex-web-qa/scripts/web_obx_qa.py \
  --dry-run --flow smoke-public
```

Evidence levels:

```bash
--evidence-level minimal   # DOM summary + snapshots only on failure
--evidence-level normal    # key snapshots + failures; default
--evidence-level full      # every step snapshot + DOM + network log
```

## Workflow

1. For any new feature, new requirement, new page, new assertion, or new flow automation task, first read `references/test-task-planning-policy.md`, produce a test plan, and wait for explicit human confirmation before executing.
2. Before any non-public-page flow, run the CEX environment health gate (`flows/env-health-check.yaml` or `--health-check-only`). Continue only when status is `healthy` or the user explicitly requests `--skip-health-check`.
3. Validate `--account-profile` against flow `required_account_profile` declaration. Mismatch → `environment_blocker`.
4. Execute YAML flows with `scripts/flow_runner.py` via the CLI entry `scripts/web_obx_qa.py`.
5. Prefer `runtime=codex` for live interactive execution and `runtime=playwright` for local stateless regression. Do not use local Playwright as the default path for Chrome login-state flows.
6. Review Markdown and JSON reports. Treat `automation_issue`, `environment_blocker`, `service_degradation`, and `requirement_unclear` as Skill/QA follow-up, not product bugs by default.
7. Review `qa-experience-summary.md` and `qa-skill-optimization-confirm.template.json`; only confirmed learning items may be used to optimize this Skill.
8. After confirmed Skill changes, sync Codex and Cursor mirrors with `scripts/sync-onebullex-web-qa-skill.sh`.
9. Only after human confirmation, generate Zentao drafts with `scripts/zentao_bug_draft.py`.
10. If filing bugs in Chrome, fill Zentao but stop before `保存` until the user explicitly confirms the destination, account, title, body, and attachments.

## Boundary with Other QA Skills

| Skill | Responsibility | Web QA Relationship |
|-------|---------------|---------------------|
| `cex-contract-testing-expert` | PRD rule test-case design (margin/liquidation/funding formula assertions) | Web QA does not design test cases; executes testnet automation only |
| `product-test-qa` | UAT acceptance criteria and checklist | Web QA flows can serve as UAT automation carrier |
| `web3-product-expert` | Product design / PRD | Web QA references PRD but does not produce one |
| `onebullex-android-qa` | Android APK automation | Shares Zentao/learning-loop/report conventions; Web QA adds DOM+API+WS dual verification |

## CEX Environment Health Gate

Non-dry-run and non-public-only flows are blocked unless the health gate passes or the user explicitly requests `--skip-health-check`.

Check items (executed by `scripts/environment_health_guard.py` + `scripts/ws_probe.py`):

1. Site HTTP reachable: testnet homepage loads
2. `ensure_locale` → Chinese UI signals (e.g., "登录", "市场", "合约")
3. Login entry reachable (login not required for check)
4. Market REST available: public ticker/market API returns data or page embeds market data
5. WebSocket alive: receives tick within `freshness_window_ms` (default `5000`) via `ws_probe.py`
6. Spot/futures trading page routes load (DOM skeleton / key controls visible)
7. Asset page route loads
8. No global maintenance / risk-control banner detected (hit → `service_degradation`)

Result classification:
- `healthy`: all checks pass
- `environment_blocker`: site unreachable, login entry broken, or other hard failures
- `service_degradation`: maintenance banner, WS silent, or partial API issues — blocks trading flows only

Output artifact: `environment-health-check.json`.

## Account State Matrix

Defined in `references/account-profiles.md`. Every flow must declare required profile; `scripts/account_state_probe.py` validates actual state.

| Profile | Purpose | Probe Signals (examples) |
|---------|---------|--------------------------|
| `guest` | Public pages | No user menu / shows login |
| `basic-login` | Logged-in, no positions | Avatar/UID visible + no position rows |
| `funded-spot` | Spot balance > 0 | Asset page USDT/BTC balance > 0 |
| `funded-futures` | Futures margin available | Futures asset area shows available margin |
| `open-orders` | Active pending orders | Current orders count > 0 |
| `open-position` | Active positions | Position list non-empty |
| `withdraw-capable` | Withdrawal enabled | Withdraw entry available and not disabled (probe only, no action) |

Account state mismatch → `environment_blocker` (prevents misclassifying profile issues as product bugs).

## Dual-Browser Strategy

Defined in `references/web-qa-config.md`. Browser/Chrome plugins are the preferred live execution surfaces; local Playwright runtime is the fallback for stateless/public-page flows. Python scripts provide flow linting, report assembly, route resolution, and non-sensitive precheck helpers. Route selection:

| Flow Category | Browser Mode | Strategy |
|---------------|-------------|----------|
| Public pages (smoke, market, locale) | `iab` | Playwright fresh Chromium context, `locale=zh-CN`, no persistent storage |
| Auth flows (login, asset, trade) | `chrome` | `launch_persistent_context(user_data_dir=...)` or `chromium.connect_over_cdp(url)` for pre-logged-in testnet sessions |

- `iab`: fast, stateless, suitable for stable regression and no-session-dependency flows. It can run through Codex Browser plugin or the local Playwright runtime.
- `chrome`: use the user Chrome plugin/session for login-dependent flows; do not inspect cookies, local storage, profiles, passwords, or session stores.
- Local Playwright runtime is intentionally limited to stateless/public-page flows first. Treat login/account/trade flows as Codex interactive execution unless expanded later.
- Current local Playwright smoke runs show the homepage rendering English on `2026-06-17`; `ensure_locale` should fail in that case and surface a real locale/default-language finding instead of being treated as runner noise.
- Current local Playwright runtime is reliable for short public flows such as `smoke-public`, `market-data`, and split desktop/mobile checks. Long screenshot-heavy walkthroughs should be split into smaller public flows or moved back to Codex interactive Browser execution.
- Flow-level `browser_mode` mismatch → `environment_blocker`.

## Flow System

- Stable flows live in `flows/*.yaml`.
- `scripts/browser_driver.py` provides:
  - `runtime=codex`: report-oriented bridge for interactive Browser/Chrome plugin execution.
  - `runtime=playwright`: local runner for public/stateless flows through the bundled Playwright CLI wrapper.
- `scripts/flow_runner.py` executes Flow DSL and writes:
  - `onebullex-web-qa-report.md`
  - `onebullex-web-qa-report.json`
  - `confirmed-bugs.template.json`
  - `qa-experience-summary.md`
  - `qa-skill-optimization-candidates.json`
  - `qa-skill-optimization-confirm.template.json`
  - `flows-used/`
  - per-step `dom-summary.txt`, optional screenshots, network log (full evidence)

Read `references/flow-format.md` before adding or changing flows.

### Web Flow DSL Actions

**Navigation & Interaction**: `goto`, `click`, `type`, `wait_for`, `sleep`, `ensure_locale`

**Assertions**:
- `assert_text`, `assert_url`, `assert_visible`
- `assert_table_sort` — DOM order assertion with `tolerance` / `max_inversions`
- `assert_balance_block` — asset block field + numeric tolerance
- `assert_order_state` / `assert_position_state` / `assert_history_row` — page table + optional API cross-check
- `assert_toast` — negative/error toast verification
- `assert_ws_freshness` — WebSocket time window check
- `assert_numeric_delta` — pre/post balance/margin delta with `delta_tolerance` and `max_wait_ms`
- `assert_api_response` — intercept XHR/fetch and assert JSON path structure

**Safety & Evidence**: `safety_gate`, `snapshot`, `ux_snapshot`

### Selector Priority

```
data-testid > css(.class#id) > text > role+name > fallback_xy
```

- Prefer stable `data-testid` selectors. Ask Web developers to add them per `references/web-test-id-guidelines.md`.
- `css` selector has higher priority than `text` and `role+name` in Web context.
- `text` selectors work for Chinese-only but may break if locale changes.
- `fallback_xy` coordinates are temporary compatibility only; reports must flag them as lower stability.

### Dynamic Data Strategy

- **Price / change%**: assert structure, sort order, non-empty, WS freshness only — never assert absolute values.
- **Balance / margin**: `assert_numeric_delta` enabled only with `--allow-side-effects` + user-confirmed symbol/qty.
- **Negative cases**: insufficient balance, precision error, leverage over-limit → `assert_toast` + order-not-created (URL/list dual verification).
- **Tolerance windows**: all numeric assertions include configurable tolerance to avoid flagging normal market fluctuation.

### Transaction Dual Verification

For all key trading conclusions, enforce paired verification:
- **Page state**: button state, form values, toast messages, list row content
- **Result state**: order list / position list / trade history / asset value delta (optionally via `assert_api_response` for XHR/fetch interception)

## Side-Effect Control Granularity

| Level | CLI Flag | Default | Behavior |
|-------|----------|---------|----------|
| Login only | `--allow-login` | allowed | Test credentials from env, no asset impact |
| Navigate to confirm | `--allow-side-effects` | blocked | Fills forms up to final confirmation; stops at `safety_gate` |
| Final submit | `--confirm-submit` | blocked | Clicks final confirmation; requires user to confirm symbol, direction, quantity, leverage per flow |
| Withdrawal | `--allow-withdraw` | blocked-by-default | Highest risk; requires explicit per-operation approval |

`safety_gate` at the last step of trade flows blocks execution unless the matching flag is set and the user has confirmed in the plan.

## High-Risk Flows

- `login-dev.yaml` reads `OBX_TEST_USERNAME` and `OBX_TEST_PASSWORD` from environment; never store credentials in the Skill.
- `spot-trade-dry-run.yaml` and `futures-trade-dry-run.yaml` are blocked by default before final order confirmation.
- Do not pass `--confirm-submit` unless the user has explicitly approved the account, environment, symbol, direction, quantity, and leverage.
- Production / real-asset trading side effects are out of scope by default.

## Planning Policy

For new feature / new requirement automation, read `references/test-task-planning-policy.md` and produce a plan first. Existing stable regression flows may run directly only after the environment health gate passes and only when no new selectors/assertions/pages are being introduced.

## Learning Loop

Every automated QA run must leave a Skill learning review in the evidence directory. Read `references/qa-learning-loop.md` before applying those learnings.

Default review flow:

```bash
python3 /Users/jingxing/Desktop/Onebullex/workflow/skills/qa/onebullex-web-qa/scripts/skill_learning_review.py \
  --apply-confirmed /tmp/onebullex-web-qa/<run>
```

Only after human confirmation, write confirmed learnings back to the repo source:

```bash
python3 /Users/jingxing/Desktop/Onebullex/workflow/skills/qa/onebullex-web-qa/scripts/skill_learning_review.py \
  --apply-confirmed \
  --write-skill \
  /tmp/onebullex-web-qa/<run>
```

Then sync runtime mirrors:

```bash
cd /Users/jingxing/Desktop/Onebullex
scripts/sync-onebullex-web-qa-skill.sh
```

Do not promote unconfirmed product bugs, environment blockers, credentials, or one-off network/session behavior into this Skill.

## AI Explore Once, Then Solidify

For a new page or operation:

1. Use Browser/Chrome plugin DOM summaries and, only when necessary, screenshots to discover the path.
2. Prefer stable `data-testid` selectors; use `css` selectors next.
3. Add fallback coordinates only as temporary compatibility.
4. Write the confirmed path into `routes/*.yaml` and `flows/*.yaml`.
5. Re-run `runtime=playwright` for public-page validation when possible; keep login/account/trade verification in Codex interactive mode unless a dedicated local runner path has been added.
5. Re-run dry-run/lint first, then live plugin execution when appropriate.
5. Re-run the flow. Do not rely on fresh AI exploration for repeated regression runs.

## Developer Collaboration

Ask Web developers to add stable test IDs listed in `references/web-test-id-guidelines.md`. This is the highest leverage improvement for speed and reliability.

## UX/UI Screenshot Walkthrough

Run the final screenshot-backed UX/UI review after functional flows:

```bash
python3 /Users/jingxing/Desktop/Onebullex/workflow/skills/qa/onebullex-web-qa/scripts/web_obx_qa.py \
  --flow ux-ui-walkthrough.yaml \
  --browser-mode chrome \
  --viewport both \
  --evidence-level normal
```

Then build the UX/UI review pack:

```bash
python3 /Users/jingxing/Desktop/Onebullex/workflow/skills/qa/onebullex-web-qa/scripts/ux_ui_review_pack.py /tmp/onebullex-web-qa/<run>
```

Use `references/ux-ui-checklist.md` and `references/onebullex-core-ui-review.md` as the review criteria. UX findings must cite screenshot evidence and a checklist/core-rule basis. P0/P1 issues that block use, mislead users, create funds risk, or break core component consistency may become bug candidates after human confirmation. `visual_polish` and `needs_design_confirmation` stay as design debt by default.

When `--viewport both`, the report includes a `## Cross-Viewport Consistency` section comparing desktop and mobile rendering differences.

## Zentao Drafts

Generate drafts only from confirmed product bug candidates:

```bash
python3 /Users/jingxing/Desktop/Onebullex/workflow/skills/qa/onebullex-web-qa/scripts/zentao_bug_draft.py \
  /tmp/onebullex-web-qa/<run>/confirmed-bugs.template.json
```

Chrome/Zentao safety rules:
- Use existing Chrome login state and prefer `Henrly linjinhong16@gmail.com`.
- Do not inspect cookies, passwords, local storage, or profile internals.
- Stop on login, CAPTCHA, account mismatch, or permission prompts.
- Stop before clicking `保存`; submit only after explicit user confirmation.

## Unified CLI Parameters (`web_obx_qa.py`)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--flow` | - | Flow name/path or `all-public` / `all-auth` |
| `--browser-mode` | `iab` | `iab` or `chrome` |
| `--viewport` | `desktop` | `desktop` / `mobile` / `both` (serial runs with diff section) |
| `--locale` | `zh-cn` | Force Chinese site |
| `--evidence-level` | `normal` | `minimal` / `normal` / `full` |
| `--allow-side-effects` | false | Allow testnet side effects (up to safety_gate) |
| `--confirm-submit` | false | Allow clicking final submit/confirm |
| `--allow-withdraw` | false | Allow withdrawal flows (highest restriction) |
| `--account-profile` | `guest` | See account-profiles matrix |
| `--environment-profile` | `testnet` | Currently testnet only |
| `--dry-run` | false | Validate flow/params without browser |
| `--health-check-only` | false | Run health gate only |
| `--skip-health-check` | false | Explicit skip (requires user confirmation) |
| `--chrome-user-data-dir` | env | `OBX_CHROME_USER_DATA_DIR` |
| `--chrome-cdp-url` | env | `OBX_CHROME_CDP_URL`, mutually exclusive with userDataDir |
| `--test-level` | flow | Override/validate flow level `L0`-`L4` |
| `--risk-level` | flow | Override/report flow risk level |
| `--vpn-mode` | `off` | `off` / `auto` / `required` Clash VPN gate |
| `--vpn-app` | `/Applications/ClashX Pro.app` | Clash client path |
| `--vpn-require-system-proxy` | false | Require macOS system proxy to be enabled |
| `--vpn-require-traffic` | false | Require current Clash traffic confirmation `>0kb` |
| `--vpn-failure-policy` | `block` | `block` or `pause_for_manual` |
| `--record-replay-session` | - | Path to Record & Replay session/events for candidate generation |
| `--generate-flow-seed-from-recording` | false | Generate recording candidate artifacts without formal promotion |
| `--recording-label` | - | Human-readable recording label |
| `--release-readiness-check` | false | Add release-readiness checklist to report |

Credentials: `OBX_TEST_USERNAME` / `OBX_TEST_PASSWORD` (shared with Android QA, never stored in Skill).

## Dependencies

```bash
pip install playwright pyyaml
playwright install chromium
```

## Report Format Extensions (vs Android QA)

In addition to Android QA report sections, Web QA reports include:

- `## Environment Health Gate` — health check summary with pass/fail/blocked items
- `## Browser & Viewport` — mode, viewport, locale, CDP/userDataDir info
- `## Account State` — expected vs actual profile match
- `## Cross-Viewport Consistency` — when `--viewport both`
- `## Page vs Result Verification` — dual verification summary per trading assertion


Additional professional QA report sections:

- `## Test Level & Risk` — L0/L1/L2/L3/L4 scope, risk level, side-effect level, oracle types.
- `## Clash VPN Gate` — Clash app, running state, system proxy, traffic confirmation, HTTP/REST/WS probe status.
- `## Preconditions` — health, account, VPN, data, and safety gate status.
- `## Oracle Coverage` — DOM/API/WS/state/visual/negative coverage per flow.
- `## Route & Selector Stability` — route-backed selectors and fallback/stability notes.
- `## Flakiness Notes` — sleeps, retries, fallback selectors, inconclusive evidence.
- `## Evidence Index` — local evidence files grouped by flow and step.
- `## Release Readiness` — validation and GitHub PR readiness checklist.

## MVP Flow Catalog (Phase 1)

```text
flows/
├── env-health-check.yaml          # Environment gate (prerequisite)
├── smoke-public.yaml              # Public page smoke
├── locale-zh-cn.yaml              # Chinese locale default
├── locale-zh-cn-mobile.yaml       # Mobile Chinese layout/rendering
├── market-data.yaml               # Market data + WS freshness
├── login-dev.yaml                 # Auth-only login flow
├── asset-overview.yaml            # Asset page overview
├── spot-trade-dry-run.yaml        # Spot: up to confirm with safety_gate
├── futures-trade-dry-run.yaml     # Futures: up to confirm with safety_gate
├── order-position-consistency.yaml # Order/position cross-verification
└── ux-ui-walkthrough.yaml         # UX/UI screenshot review
```

Flow dependency graph:

```
env-health-check
 ├── smoke-public ──→ ux-ui-walkthrough
 ├── locale-zh-cn
 ├── locale-zh-cn-mobile
 ├── market-data
 └── login-dev
       ├── asset-overview
       ├── spot-trade-dry-run
       ├── futures-trade-dry-run
       └── order-position-consistency
```

- `all-public` = `env-health-check` + `smoke-public` + `locale-zh-cn` + `locale-zh-cn-mobile` + `market-data`
- `all-auth` = health + login + asset + dry-runs + consistency (no real submit)

Phase 2 (not MVP): Spartans, Referral, rewards flows (requires product routing and testid spec).

## Directory Structure (Phase 1)

```text
workflow/skills/qa/onebullex-web-qa/
├── SKILL.md
├── agents/openai.yaml
├── flows/
│   ├── env-health-check.yaml
│   ├── smoke-public.yaml
│   ├── locale-zh-cn.yaml
│   ├── locale-zh-cn-mobile.yaml
│   ├── market-data.yaml
│   ├── login-dev.yaml
│   ├── asset-overview.yaml
│   ├── spot-trade-dry-run.yaml
│   ├── futures-trade-dry-run.yaml
│   ├── order-position-consistency.yaml
│   └── ux-ui-walkthrough.yaml
├── scripts/
│   ├── web_obx_qa.py              # CLI entry
│   ├── flow_runner.py             # Flow executor
│   ├── browser_driver.py          # Playwright abstraction
│   ├── environment_health_guard.py
│   ├── account_state_probe.py
│   ├── ws_probe.py                # WebSocket push probe
│   ├── ux_ui_review_pack.py       # Adapted from android
│   ├── zentao_bug_draft.py        # Reuse android logic
│   └── skill_learning_review.py   # Reuse android logic
└── references/
    ├── test-task-planning-policy.md
    ├── flow-format.md
    ├── report-format.md
    ├── web-qa-config.md            # Merged: browser-strategy + account-profiles + health-gate
    ├── web-test-id-guidelines.md
    ├── qa-learning-loop.md
    ├── ux-ui-checklist.md          # → symlink to android-qa/references/ux-ui-checklist.md
    ├── onebullex-core-ui-review.md  # → symlink to android-qa/references/onebullex-core-ui-review.md
    └── zentao-bug-flow.md           # → symlink to android-qa/references/zentao-bug-flow.md
```
