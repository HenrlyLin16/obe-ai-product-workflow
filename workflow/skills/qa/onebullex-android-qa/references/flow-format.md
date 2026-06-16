# OneBullEx Android QA Flow Format

Flows live in `flows/*.yaml` and are executed by `scripts/flow_runner.py`.

## Top-level fields

- `name`: stable flow id, for example `market-sort`.
- `version`: flow schema version, currently `1`.
- `side_effects`: optional marker such as `none`, `auth-only`, or `blocked-by-default`.
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
- `safety_gate`: stop side-effectful flows unless the user explicitly allowed them.

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
