# OneBullEx Web QA Test Task Planning Policy

Use this reference before starting any new feature, new requirement, new page, or new flow automation task.

## When Planning Is Mandatory

Start in planning mode and wait for explicit human confirmation when the request involves:

- New feature or new requirement validation from PRD, Lark, Feishu, screenshots, or product discussion.
- New Web page, new navigation path, new selector discovery, or new Flow DSL file.
- New assertion rules, especially market data, funds, login, trading, order/position consistency, or error states.
- UX/UI walkthroughs that require subjective screenshot review or design/product judgment.
- Any flow that may affect account state, orders, positions, assets, or production data.
- New environment health check items or account profile rules.

## Allowed Without A New Plan

Existing stable regression flows may run directly only when all are true:

- The user explicitly asks to run an existing flow such as `smoke-public`, `market-data`, `asset-overview`, `ux-ui-walkthrough`, `all-public`, or `all-auth`.
- The CEX environment health gate passes or the user explicitly requests `--skip-health-check`.
- The flow does not require new exploration, new selectors, new assertions, or side effects.
- The account/environment is already suitable for the requested flow.

## Required Plan Contents

A plan for a new test task must include:

- Test objective and requirement source, including PRD URL or pasted scope when available.
- Target environment: `testnet` (default), `prod` only after explicit user selection.
- Browser strategy: `iab` or `chrome`, viewport (`desktop` / `mobile` / `both`), locale (`zh-cn`).
- Account profile assumptions: which profile is needed and whether login is required.
- Flows to run or create, with rough step list and selector discovery strategy.
- Evidence and reports: evidence directory, Markdown report, JSON report, UX report if needed.
- Risk controls: side effects, login credentials, trading confirmation, withdrawal restrictions.
- Acceptance criteria and known blockers.
- Any new WebSocket or API endpoint probes needed.

## Confirmation Rule

Do not execute the planned automation until the user explicitly confirms with wording such as `继续`, `执行`, `确认执行`, `PLEASE IMPLEMENT THIS PLAN`, or an equivalent direct approval. If the user only asks for opinions or refinements, keep iterating on the plan.
