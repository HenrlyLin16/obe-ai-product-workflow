# Account Profiles

Use these profiles as flow preconditions and report environment facts. Account mismatch is an `environment_blocker`.

| Profile | Purpose | Required visible signal |
| --- | --- | --- |
| `guest` | Public pages | Login/register entry visible, no UID/user menu |
| `basic-login` | Logged-in baseline | UID/avatar/account menu visible |
| `funded-spot` | Spot trade/assets | Spot asset balance or USDT amount visible |
| `funded-futures` | Futures trade/assets | Futures available margin or guarantee asset visible |
| `open-orders` | Order management | Current order table non-empty |
| `open-position` | Position management | Position table non-empty and size visible |
| `withdraw-capable` | Withdrawal entry only | Withdraw entry enabled; do not submit withdrawal |

Never store credentials, cookies, localStorage, tokens, screenshots containing secrets, or profile internals in this Skill.
