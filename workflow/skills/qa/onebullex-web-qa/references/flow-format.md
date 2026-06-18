# OneBullEx Web QA Flow Format

Flows live in `flows/*.yaml` and are executed by `scripts/flow_runner.py`.

## Top-level fields

- `name`: stable flow id, for example `market-data`.
- `version`: flow schema version, currently `1`.
- `description`: human-readable flow purpose.
- `side_effects`: optional marker such as `none`, `auth-only`, or `blocked-by-default`.
- `required_account_profile`: one of `guest`, `basic-login`, `funded-spot`, `funded-futures`, `open-orders`, `open-position`, `withdraw-capable`.
- `required_browser_mode`: `iab`, `chrome`, or `any`.
- `steps`: ordered list of actions.

## Supported Actions

### Navigation & Interaction

| Action | Parameters | Description |
|--------|-----------|-------------|
| `goto` | `url` | Navigate to URL. Supports `{env}` template for testnet base URL. |
| `click` | `selector` | Click matched element. Follows selector priority chain. |
| `type` | `selector`, `value`, `clear` | Type text into input. `value` supports `env:VAR` for credentials. |
| `wait_for` | `selector` or `ms` | Wait for element visible or fixed milliseconds. |
| `sleep` | `ms` | Fixed pause. |
| `ensure_locale` | `signals` | Assert Chinese UI signals present (e.g., "登录", "市场"). |
| `scroll_to` | `selector` | Scroll element into view. |
| `select` | `selector`, `value` | Select dropdown option. |

### Assertions

| Action | Parameters | Description |
|--------|-----------|-------------|
| `assert_text` | `selector`, `text`, `mode` | Assert text presence. `mode`: `contains` (default), `exact`, `regex`. |
| `assert_url` | `pattern` | Assert current URL matches pattern (supports glob/regex). |
| `assert_visible` | `selector` | Assert element is visible. |
| `assert_table_sort` | `row_selector`, `col_key`, `order`, `tolerance`, `max_inversions` | Parse DOM table rows and assert sorting. `order`: `asc` or `desc`. |
| `assert_balance_block` | `selector`, `field`, `operator`, `value`, `tolerance` | Assert asset block field with numeric tolerance. |
| `assert_order_state` | `order_id_selector`, `expected_state` | Assert order row shows expected state (e.g., "未成交"). |
| `assert_position_state` | `symbol`, `expected_fields` | Assert position row has expected fields (e.g., size > 0). |
| `assert_history_row` | `row_selector`, `expected_fields` | Assert history table row content. |
| `assert_toast` | `text`, `timeout_ms` | Assert toast/notification appears with text. Supports negative case. |
| `assert_ws_freshness` | `freshness_window_ms` | Assert WebSocket received tick within time window. |
| `assert_numeric_delta` | `pre_selector`, `post_selector`, `expected_delta`, `delta_tolerance`, `max_wait_ms` | Assert numeric change before/after operation. |
| `assert_api_response` | `path_pattern`, `method`, `assert_json_path`, `assert_not_empty` | Intercept XHR/fetch and assert API response structure. |
| `assert_not_visible` | `selector` | Negative assertion: element must not be visible. |

### Safety & Evidence

| Action | Parameters | Description |
|--------|-----------|-------------|
| `safety_gate` | `reason` | Block execution unless matching CLI flag is set. |
| `snapshot` | `label` | Capture DOM summary + optional screenshot. |
| `ux_snapshot` | `label`, `snapshot` | Force screenshot for UX review checkpoint. |

## Selector Format

```yaml
selector:
  testid: "order-submit-btn"           # Preferred: data-testid attribute
  css: ".trade-form .submit-btn"       # CSS selector
  text: "开多"                         # Text content match
  role: "button"                       # ARIA role
  name: "Submit"                       # ARIA name / accessible name
  fallback_xy: [640, 360]              # Temporary coordinate fallback (low stability)
```

Priority: `data-testid` → `css(.class#id)` → `text` → `role+name` → `fallback_xy`

Fallback coordinates are allowed before stable test IDs exist, but reports must flag them as lower stability.

## Dynamic Data Strategy

- **Price / change%**: assert structure, sort order, non-empty, WS freshness only — never assert absolute values.
- **Balance / margin**: `assert_numeric_delta` enabled only with `--allow-side-effects` + user-confirmed symbol/qty.
- **Negative cases**: insufficient balance, precision error, leverage over-limit → `assert_toast` + `assert_not_visible` on success elements.
- **Tolerance windows**: all numeric assertions include configurable tolerance to avoid flagging normal market fluctuation.
- **Sort tolerance**: `assert_table_sort` accepts `max_inversions` for near-sorted lists (e.g., market data with rapid updates).

## Failure Classification

Use `failure_category` on steps:

- `product_bug`: product behavior likely violates requirements.
- `automation_issue`: selector, timing, parser, or flow problem.
- `environment_blocker`: site unreachable, login broken, account profile mismatch, health gate failure.
- `service_degradation`: maintenance banner, WS silent, partial API issues (blocks trading, not public flows).
- `requirement_unclear`: behavior needs PRD/QA clarification.

Only steps with `bug_candidate: true` and `failure_category: product_bug` are written as Zentao candidates.

## Double-Verification Enforcement

For all key trading assertions (`assert_order_state`, `assert_position_state`, `assert_numeric_delta`, `assert_balance_block`):

- **Page state**: button state, form values, toast messages, list row content
- **Result state**: order list / position list / trade history / asset value delta
- Optionally validated via `assert_api_response` for XHR/fetch data cross-check

## UX/UI Screenshot Steps

Use `ux_snapshot` for screenshot-backed UX/UI walkthrough checkpoints.

```yaml
step:
  name: "ux_market_page"
  action: "ux_snapshot"
  label: "市场页"
  snapshot: true
```

Rules:
- UX snapshots must force screenshot capture with `snapshot: true`.
- Keep `dom-summary.txt` with every screenshot so findings can cite both visual and structural evidence.
- Use `failure_category: environment_blocker` for pages that cannot be reached; do not classify unreachable optional pages as product bugs by default.
- Run `scripts/ux_ui_review_pack.py <evidence-dir>` after the flow to generate `ux-ui-review-report.md` and `ux-ui-findings.json`.
- When `--viewport both`, take snapshots at both desktop and mobile viewports for cross-viewport comparison.
- For local `runtime=playwright`, prefer shorter UX snapshot flows per page group. Do not assume one long screenshot-heavy flow will be the most stable execution shape.

## Route References

Reusable selectors and URLs live in `routes/*.yaml`. Prefer route references over repeating selectors in multiple flows.

```json
{"name":"open_market","action":"goto","route":"market.page","snapshot":true}
```

Rules:

- `route` may provide `url`, `selector`, and stability metadata.
- Flow-local `selector` or `url` overrides the route entry.
- Route entries marked `needs_test_id: true` should produce learning candidates until Web developers add stable `data-testid` values.
- Keep route files JSON-compatible unless PyYAML is available in the active environment.

## High-Risk Step Requirements

Any flow with `side_effects: blocked-by-default` or `side_effects: testnet-submit` must include a final `safety_gate` step. The gate must declare `requires_side_effect: true`, and final order submission must also declare `requires_confirm_submit: true`.

Default behavior is to stop before final submit. Testnet real submit requires explicit user confirmation and CLI flags.
