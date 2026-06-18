# Web QA Configuration

Merged reference: browser strategy, account profiles, and environment health gate details.

## Browser Strategy

## Execution Boundary

Browser automation for `iab` and `chrome` is performed by Codex Browser/Chrome plugins, not by directly reading browser profiles from Python scripts. The scripts in this Skill are responsible for:

- Flow linting and dry-run validation.
- Route resolution and selector stability reporting.
- Non-sensitive helper probes, such as HTTP reachability or configured WS checks.
- Evidence/report assembly after live plugin observations are captured.

Do not inspect cookies, local storage, Chrome profiles, passwords, or session stores. If login, CAPTCHA, account mismatch, or permission prompts appear, stop and let the user handle them.

Optional Playwright CLI fallback is allowed only for stateless public-page debugging when Browser plugin is unavailable or explicitly not desired. It is not the default path for logged-in account flows.

When the local Playwright runner observes a locale mismatch, keep that as a product/environment finding. Do not silently coerce the page into another language inside the runner unless the flow explicitly models locale switching.
When the local runner is used for long screenshot-heavy walkthroughs, prefer splitting the flow into smaller public slices. The current CLI wrapper is adequate for short public regressions, but extended multi-page evidence capture is still less stable than Codex interactive Browser execution.


### Mode Selection

| Flow Category | Browser Mode | Strategy |
|---------------|-------------|----------|
| Public pages (smoke, market, locale) | `iab` | Playwright fresh Chromium context, `locale=zh-CN`, no persistent storage |
| Auth flows (login, asset, trade) | `chrome` | Chrome plugin/session with existing login state; no cookie/localStorage/profile inspection |

### `iab` Mode

```python
# Fresh context, no cookies/storage
context = browser.new_context(
    locale="zh-CN",
    viewport={"width": 1280, "height": 720},
)
```

**Use for**: public pages, stable regression, no-session-dependency flows.
**Do not use for**: login-dependent flows (no cookie persistence).

### `chrome` Mode (Plugin Session Preferred)

Use the Chrome plugin when a flow depends on existing login/account state. Claim or open a visible testnet tab through the plugin, then interact through DOM/Playwright APIs exposed by that plugin.

**Use for**: auth-dependent flows, assets, orders, positions, testnet trading dry-runs.
**Do not do**: inspect cookies, localStorage, profile directories, passwords, or session stores.

### Optional Playwright CLI Fallback

Use only for stateless public-page debugging when explicitly selected. Do not use it as the default path for Chrome login-state flows.

### Viewport Configurations

| Viewport | Width | Height | Device Scale | Use Case |
|----------|-------|--------|-------------|----------|
| `desktop` | 1280 | 720 | 1.0 | Default; covers standard 720p |
| `mobile` | 390 | 844 | 2.0 | iPhone 14 Pro size; mobile layout validation |

When `--viewport both`: execute flow twice (desktop then mobile), produce cross-viewport diff in report.

### Flow-Level Declaration

```yaml
required_browser_mode: chrome   # or iab or any
```

Mismatch → `environment_blocker` at flow start.

---

## Account Profiles

### Standard Profiles

| Profile | Purpose | Probe Signals |
|---------|---------|---------------|
| `guest` | Public pages | No user menu / shows login button or "登录" |
| `basic-login` | Logged in, no positions | Avatar/UID visible + no position rows + no pending orders |
| `funded-spot` | Spot balance > 0 | Asset page USDT/BTC balance > 0 in spot section |
| `funded-futures` | Futures margin available | Futures asset area shows available margin > 0 |
| `open-orders` | Active pending orders | Current orders count > 0 or order list non-empty |
| `open-position` | Active positions | Position list non-empty; position size > 0 |
| `withdraw-capable` | Withdrawal enabled | Withdraw entry available and not disabled (probe only, no action) |

### Probe Rules

`scripts/account_state_probe.py` checks:

1. **For `guest`**: login button/link visible; no account menu elements.
2. **For `basic-login`**: user avatar/UID visible; position table empty or shows "暂无持仓".
3. **For `funded-*`**: navigate to asset page; extract balance values; compare to 0 with tolerance.
4. **For `open-orders` / `open-position`**: navigate to relevant page; count visible rows.
5. **For `withdraw-capable`**: check withdraw button not disabled; do not navigate beyond overview.

### Flow-Level Declaration

```yaml
required_account_profile: funded-futures
```

Mismatch → `environment_blocker` with actual profile reported.

### Credentials

- `OBX_TEST_USERNAME` / `OBX_TEST_PASSWORD`: environment variables (shared with Android QA).
- Never stored in Skill, flows, reports, or SYNCED_FROM.
- Login flows reference `env:OBX_TEST_USERNAME` in `type` action value.

---

## Environment Health Gate Details

### Check Items

Implemented by `scripts/environment_health_guard.py` + `scripts/ws_probe.py`.

| # | Check | Method | Timeout | Failure Category |
|---|-------|--------|---------|-----------------|
| 1 | Site HTTP reachable | `goto` testnet homepage | 15s | `environment_blocker` |
| 2 | Chinese locale signals | `ensure_locale` — find "登录"/"市场"/"合约" | 5s | `environment_blocker` |
| 3 | Login entry reachable | `click` login button → page loads | 10s | `environment_blocker` |
| 4 | Market REST available | Check page-embedded market data or public API | 10s | `service_degradation` |
| 5 | WebSocket alive | `ws_probe.py` connect + wait `freshness_window_ms` (default 5000) for tick | 10s | `service_degradation` |
| 6 | Spot trading page loads | Navigate to spot route; assert key DOM skeleton | 10s | `service_degradation` |
| 7 | Futures trading page loads | Navigate to futures route; assert key DOM skeleton | 10s | `service_degradation` |
| 8 | Asset page loads | Navigate to asset route; assert key DOM skeleton | 10s | `service_degradation` |
| 9 | Maintenance/risk-control banner | Scan DOM for maintenance/风控 signal keywords | 5s | `service_degradation` |

### Result Matrix

| Health Gate Result | Allowed Flows | Examples |
|-------------------|---------------|----------|
| All pass | All flows | — |
| `environment_blocker` on items 1-3 | None (site/login unreachable) | Site down, DNS failure, login page broken |
| `service_degradation` on items 4-5 | Public flows only | WS silent, market API partial outage |
| `service_degradation` on items 6-9 | Public flows only (no trading/asset) | Trading page won't load, maintenance banner |

### Output

- File: `environment-health-check.json`
- Format: JSON object with per-item `status`, `duration_ms`, `error` (if failed), `classification`.
- CLI: `--health-check-only` runs gate and exits without product flows.
- CLI: `--skip-health-check` bypasses gate entirely (requires user confirmation).

### WebSocket Probe (`ws_probe.py`)

- Connects to testnet WebSocket endpoint.
- Subscribes to a public ticker channel (e.g., BTC/USDT mark price).
- Waits up to `freshness_window_ms` (default 5000ms) for first tick.
- Times out if no tick within window → `service_degradation`.
- Does not verify tick content; only verifies push connectivity and freshness.
