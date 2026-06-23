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

## Android Contract Special Regression Flow

When releasing Android QA Skill changes from the 2026-06-22 contract special
validation, include the new flow summary in the PR:

- Flow file: `flows/contract-special-regression.yaml`
- Source requirement: Lark Wiki `HqjKwksjVimXMSkXkDqlSLWkgGb`
- Evidence pack:
  `/tmp/onebullex-android-qa/20260622-contract-special`
- Local report:
  `output/OBE-Android-dev-合约专项验证报告-放开交易权限-20260622.md`

Functional modules covered by the flow:

- Futures trading page entry and cold-start funding-rate visibility.
- Futures order unit sheet: coin, value, and cost modes.
- Order book depth unit display and refresh observation after waiting or
  precision interaction.
- Market order confirmation copy, including quantity, cost, and value fields.
- Small dev-environment position lifecycle: open, position visible, position
  TP/SL sheet visible, and cleanup requirement.
- Position TP/SL copy: whole-position and partial-position tabs, trigger price,
  amount, PnL, and risk warning.
- Futures preference settings entry and order-confirmation discoverability.
- Leverage panel high-risk copy for loss amplification and liquidation risk.

PR validation notes should explicitly call out side-effect boundaries:

- This flow is `blocked-by-default` and needs an explicit dev-test account and
  trading side-effect approval before the test-trade segment.
- The run must use a small `test_cost_usdt` input, defaulting to `1`.
- The run must confirm the final device state is cleaned up, for example
  `持仓(0)` and `当前委托(0)`.
- Do not promote private account balance, screenshots, or evidence files into
  the repository; reference their local paths only in PR notes.

Known follow-up items from the first validation should be listed as remaining
risks until confirmed:

- TP/SL invalid input currently needs clearer oracle rules before being treated
  as a product bug.
- Partial-position TP/SL quantity-unit switching needs a hardened selector and
  product confirmation for the expected `Token/BTC/USDT` behavior.
- Current-order list bottom-safe-area validation requires creating multiple
  limit orders or seeded order data.

## Stop Conditions

- Unrelated dirty files are mixed into the change set
- Confirmed learnings have not yet been reviewed by a human
- Validation is missing or failing
- Sensitive information appears in generated artifacts or commit scope
