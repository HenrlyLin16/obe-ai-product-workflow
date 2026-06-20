# OneBullEx Android QA Test Task Planning Policy

Use this reference before starting any new feature, new requirement, new page, or new flow automation task.

## When Planning Is Mandatory

Start in planning mode and wait for explicit human confirmation when the request involves:

- New feature or new requirement validation from PRD, Lark, Feishu, screenshots, or product discussion.
- New Android page, new navigation path, new selector discovery, or new Flow DSL file.
- New assertion rules, especially sorting, funds, login, trading, permissions, or error states.
- UX/UI walkthroughs that require subjective screenshot review or design/product judgment.
- Any flow that may affect account state, orders, positions, assets, or production data.

## Allowed Without A New Plan

Existing stable regression flows may run directly only when all are true:

- The user explicitly asks to run an existing flow such as `smoke`, `market-sort`, `asset-sort`, `ux-ui-walkthrough`, or `all`.
- The APK version gate passes or the user explicitly requests `--skip-version-check`.
- The flow does not require new exploration, new selectors, new assertions, or side effects.
- The account/environment is already suitable for the requested flow.

## Required Plan Contents

A plan for a new test task must include:

- Test objective and requirement source, including Lark/PRD URL or pasted scope when available.
- Target channel: `dev` by default, `prod` only after explicit user selection.
- Package gate strategy: version check command, expected package name, and install confirmation policy.
- Device assumptions: serial, lock state, network, login state, whether USB or Wi-Fi adb is used, and how `adb devices -l` stability will be checked.
- Device control assumptions: whether the task needs home-screen reset, external app switching, overlay permission handling, notification shade, or Android system dialog handling.
- Record & Replay usage: whether the task needs a demonstration recording, how recording outputs will be converted into seeds, and which parts still require manual selector hardening.
- VPN strategy: whether the flow requires VPN, which package will be used, whether the last-used node/config is acceptable, and what to do if automatic connection fails.
- Flows to run or create, with rough step list and selector discovery strategy.
- Evidence and reports: evidence directory, Markdown report, JSON report, UX report if needed.
- Release target: whether confirmed improvements should remain local, sync only to mirrors, or be prepared for a GitHub branch + PR.
- Risk controls: side effects, login credentials, trading confirmation, production restrictions.
- Acceptance criteria and known blockers.

## Confirmation Rule

Do not execute the planned automation until the user explicitly confirms with wording such as `继续`, `执行`, `确认执行`, `PLEASE IMPLEMENT THIS PLAN`, or an equivalent direct approval. If the user only asks for opinions or refinements, keep iterating on the plan.
