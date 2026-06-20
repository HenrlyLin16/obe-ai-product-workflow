# OneBullEx Web QA Anti-Flaky Policy

Use this reference when writing or reviewing flows.

## Waiting

- Prefer semantic waits: visible element, URL pattern, response, WS tick, or network idle.
- Fixed `sleep` is allowed only as a last resort and must be short.
- Do not use fixed waits as the primary proof that a page is ready.

## Retry

- Environment health and Clash/VPN checks may use light retry.
- Product assertions do not retry by default.
- Selector miss may trigger one DOM refresh/snapshot, and the report must include a stability note.

## Classification

- `environment_blocker`: network, Clash, login state, account profile, route unreachable.
- `service_degradation`: partial REST/WS/market degradation.
- `automation_issue`: selector, timing, parser, DSL, recording mapping.
- `product_bug`: requirement mismatch with sufficient DOM/API/WS/state/visual evidence.
- `inconclusive`: insufficient evidence; do not draft a product bug.

## Minimum Failure Evidence

A failure record should include URL, viewport, DOM summary, screenshot if possible, network/WS note, flow step, and failure classification.
