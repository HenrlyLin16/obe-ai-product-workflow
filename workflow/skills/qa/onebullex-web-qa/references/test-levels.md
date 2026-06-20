# OneBullEx Web QA Test Levels

Use this reference when classifying Web QA flows and deciding which suites can run together.

## Levels

| Level | Name | Purpose | Default runtime | Account | Side effects |
|---|---|---|---|---|---|
| `L0` | Environment health | Decide whether testnet is testable. | `playwright` or dry-run | `guest` | none |
| `L1` | Public smoke | Homepage, locale, public market pages, public routes. | `playwright`/`iab` | `guest` | none |
| `L2` | Auth/account | Login state, account profile, assets, orders, positions. | `codex`/`chrome` | logged-in profile | no trading submit |
| `L3` | Transaction dry-run | Spot/Futures/withdraw paths up to `safety_gate`. | `codex`/`chrome` | funded or withdraw-capable | blocked by default |
| `L4` | UX/UI walkthrough | Screenshot-backed review and cross-viewport consistency. | split by page | depends on page | none by default |

## Suite Mapping

- `all-public` = `L0` + `L1` only.
- `all-auth` = `L0` + `L2` + `L3` dry-run only.
- UX/UI flows are not part of default functional regression unless explicitly requested.

## Required Flow Metadata

Every flow should declare:

```yaml
test_level: L0|L1|L2|L3|L4
risk_level: low|medium|high|critical
required_runtime: playwright|codex
browser_mode: iab|chrome|any
required_account_profile: guest|basic-login|funded-spot|funded-futures|open-orders|open-position|withdraw-capable
side_effect_level: none|login|dry_run|submit|withdraw
```

## New Requirement Testability Review

Before new feature automation, confirm:

- Requirement source and target route are clear.
- Expected success, empty, loading, error, and permission states are described.
- Required account profile and test data are available.
- Oracle types are known: DOM, API, WS, state, visual, or negative.
- Any funds, order, position, withdraw, or Futures rule risk is identified.
- Futures formulas or risk rules are handed to `cex-contract-testing-expert` before Web execution.
