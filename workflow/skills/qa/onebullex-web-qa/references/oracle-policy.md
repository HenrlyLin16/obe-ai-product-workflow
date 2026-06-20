# OneBullEx Web QA Oracle Policy

Every flow declares one or more `oracle_type` values. Use the smallest oracle set that can support a product conclusion.

| Oracle | Use for | Evidence |
|---|---|---|
| `dom` | Page controls, tables, URL, text, Toasts. | DOM summary and screenshot when useful. |
| `api` | XHR/fetch result structure and business status. | Network/API observation or plugin notes. |
| `ws` | Market/order push freshness. | `ws_probe.py` or Browser/Chrome observation. |
| `state` | Orders, assets, positions, history, balances. | Page state plus result-state evidence. |
| `visual` | UX/UI consistency and cross-viewport issues. | Screenshot + checklist/core-rule. |
| `negative` | Error handling, blocking, not-created results. | Toast/error state plus absence of success state. |

## Required Pairings

- Market data: `dom` + `ws`.
- Account/assets: `dom` + `api` or `state`.
- Trading dry-run: `dom` + `negative` or `state`, plus `safety_gate`.
- UX/UI: `visual` plus screenshot evidence and checklist/core-rule basis.

A product bug requires enough oracle evidence to rule out environment, account profile, network, and automation issues.
