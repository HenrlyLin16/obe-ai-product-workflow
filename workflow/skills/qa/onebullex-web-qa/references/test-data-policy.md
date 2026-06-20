# OneBullEx Web QA Test Data Policy

Use this reference for account, balance, order, position, and withdraw-capable flows.

## Account Profiles

Profiles are defined in `references/account-profiles.md` and must be declared by every flow. If actual account state does not satisfy the required profile, classify the run as `environment_blocker`.

## Snapshot Rules

- Record only non-sensitive state needed for QA: profile match, counts, thresholds, and route visibility.
- UID, email, phone, and account identifiers must be masked.
- Balances are recorded as threshold checks, not exact private amounts, unless the user explicitly supplies test values for a testnet-only assertion.
- Do not inspect cookies, localStorage, passwords, browser profile files, or session stores.

## High-Risk State

- Default flows must not create lasting orders, positions, withdrawals, or asset movements.
- `side_effect_level: dry_run` may fill forms and stop at `safety_gate`.
- `side_effect_level: submit` or `withdraw` requires explicit user confirmation and must record pre-state, post-state, and cleanup requirements.

## Dynamic Market Data

Never assert absolute market prices. Assert structure, non-empty values, ordering, freshness, and state transitions within tolerance windows.
