# OneBullEx Android QA Flow Format

Flows live in `flows/*.yaml` and are executed by `scripts/flow_runner.py`.

## Top-level fields

- `name`: stable flow id, for example `market-sort`.
- `version`: flow schema version, currently `1`.
- `side_effects`: optional marker such as `none`, `auth-only`, or `blocked-by-default`.
- `requires_vpn`: optional boolean. When true, runner ensures VPN is connected before execution unless the user explicitly disables VPN checks.
- `requires_device_unlocked`: optional boolean. Use for flows that assume the device is already unlocked and interactive.
- `required_external_apps`: optional list of packages that may be opened during the flow, for example `com.follow.clash`.
- `device_start_hints`: optional list of preconditions such as `home-screen`, `logged-in`, or `overlay-permission-enabled`.
- `recording_seeded`: optional boolean. Mark true when the flow originated from Record & Replay exploration and still needs selector/route hardening review.
- `inputs`: optional input contract. Values are passed with `--input key=value` and referenced as `{{ inputs.key }}`.
- `steps`: ordered list of actions.

## Supported actions

- `tap`: tap a selector. Selector priority is `id`, `desc`, exact `text`, regex text/desc, then `fallback` coordinates.
- `input`: input text, optionally from `env`.
- `wait_text`: wait for exact text.
- `assert_text`: require `all` or `any` texts.
- `assert_sorted`: parse market rows and assert `symbol`, `price`, `volume`, or `change` ordering.
- `assert_assets`: assert asset overview/spot/futures page content.
- `snapshot`: collect evidence only.
- `sleep`: pause.
- `tap_xy`: tap a fixed coordinate `[x, y]`.
- `swipe`: swipe from `start` to `end`.
- `keyevent`: send an Android key event such as `KEYCODE_HOME`.
- `press_back`: send Android back.
- `dismiss_if_present`: tap an optional selector only when it is visible.
- `branch`: match the first visible selector and execute nested `then` steps.
- `log`: add a note to the report.
- `safety_gate`: stop side-effectful flows unless the user explicitly allowed them.
- `launch_app`: launch a package or package/activity pair.
- `open_external_app`: open an external Android app, such as FIClash.
- `ensure_foreground`: assert that the foreground app contains the expected package name.
- `handle_system_dialog`: dismiss a narrow set of system confirmation buttons such as VPN permission prompts.
- `home`: send Android home.
- `back`: send Android back.
- `recent_apps`: open the recent-apps switcher.
- `open_notification_shade`: expand the notification shade.
- `open_quick_settings`: expand Quick Settings.
- `ensure_vpn`: require VPN connectivity inside the flow.

The runner accepts both OneBullEx action-style steps and the shorter
`ui-automation-flow` style:

```json
{"name":"open_futures","tap":"watch_monitor.bottom_tab_futures","snapshot":true}
{"name":"maybe_close_popup","dismiss_if_present":{"text":"知道了","timeout":1}}
{"name":"go_back","press_back":{"settle":0.5}}
```

Inputs example:

```json
{
  "name": "search-symbol",
  "inputs": {
    "symbol": {"required": true}
  },
  "steps": [
    {"name":"type_symbol","action":"input","selector":{"text":"搜索"},"value":"{{ inputs.symbol }}"}
  ]
}
```

Run with:

```bash
python3 scripts/adb_obx_qa.py --dry-run --flow search-symbol.yaml --input symbol=BTCUSDT
```

## Failure classification

Use `failure_category` on steps:

- `product_bug`: product behavior likely violates requirements.
- `automation_issue`: selector, timing, parser, or flow problem.
- `environment_blocker`: device, auth, credentials, lockscreen, or network issue.
- `requirement_unclear`: behavior needs PRD/QA clarification.

Only steps with `bug_candidate: true` and `failure_category: product_bug` are written as Zentao candidates.

## Selector example

```yaml
selector:
  desc: market-sort-change
  text_regex: "涨跌|Change"
  fallback: [1065, 585]
```

Fallback coordinates are allowed before stable app test IDs exist, but reports should treat them as lower stability.

## Route references

Reusable selectors and temporary coordinates live in `routes/*.yaml`. Prefer a
route reference when the same control appears in more than one flow.

```json
{"name":"open_settings_sheet","action":"tap","route":"watch_monitor.kline_settings_button","snapshot":true}
```

Rules:

- `route` resolves to the route entry's `selector` for `tap` and `input`.
- `route` resolves to the route entry's `coordinate` for `tap_xy` when a stable selector does not exist yet.
- Flow-local `selector` or `coordinate` values override the route entry.
- Coordinate fallback via a route is still fallback; the learning loop records a `route_update` candidate so the route can later be hardened with a stable Android automation ID.
- Keep route files JSON-compatible unless the local Python environment has PyYAML available.

## Record & Replay Seeded Flows

When a new path is first explored with Record & Replay:

- Generate exploratory seeds with `scripts/record_replay_flow_seed.py`.
- Mark draft flows with `recording_seeded: true`.
- Convert recorded hints into stable `route` references and selector-based steps before treating the flow as reusable regression coverage.
- Never copy passwords, OTPs, secrets, or account-private data from a recording into `flows/*.yaml`.

## Branch example

```json
{
  "name": "handle_optional_state",
  "branch": {
    "timeout": 2,
    "cases": [
      {
        "name": "watch_monitor_visible",
        "match": {"text": "实时盯盘"},
        "then": [
          {"log": "Watch monitor page is already open."},
          {"screenshot": "watch-monitor-open"}
        ]
      },
      {
        "name": "settings_visible",
        "match": {"text": "实时盯盘浮窗"},
        "then": [
          {"tap": "watch_monitor.settings_watch_monitor_entry"}
        ]
      }
    ]
  }
}
```

Use `branch` for optional state handling only. Core product assertions should
remain explicit `assert_text` or domain-specific checks so failures stay easy to
classify.

## UX/UI screenshot steps

Use `ux_snapshot` for screenshot-backed UX/UI walkthrough checkpoints.

```json
{"name":"ux_market_page","action":"ux_snapshot","label":"市场页","snapshot":true}
```

Rules:

- UX snapshots must force screenshot capture with `snapshot: true`.
- Keep `ui.xml` and `ui-summary.txt` with every screenshot so findings can cite both visual and structural evidence.
- Use `failure_category: environment_blocker` for pages that cannot be reached; do not classify unreachable optional pages as product bugs by default.
- Run `scripts/ux_ui_review_pack.py <evidence-dir>` after the flow to generate `ux-ui-review-report.md` and `ux-ui-findings.json`.
