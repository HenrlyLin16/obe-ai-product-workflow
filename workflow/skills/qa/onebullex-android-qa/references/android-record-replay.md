# Android Record & Replay

Use Record & Replay as an exploration and learning tool, not as the final regression executor.

## Good Use Cases

- Capture a first-time path through a new Android page.
- Understand a long chain of taps, swipes, and system transitions.
- Seed route and selector discussions after a user demonstrates the intended path.
- Preserve context for complex optional popups or system permission interruptions.

## Not Good Use Cases

- Long-term regression coverage without converting the path to selector-based Flow DSL.
- Secret-bearing flows where sensitive input would be copied verbatim.
- Product assertions that should rely on XML selectors, domain checks, and explicit expected results.

## Workflow

1. Record one demonstration.
2. Generate seeds with `scripts/record_replay_flow_seed.py`.
3. Review `qa-recording-summary.md`, route seeds, and selector-hardening candidates.
4. Convert reusable pieces into `routes/*.yaml` and `flows/*.yaml`.
5. Mark draft flows with `recording_seeded: true` until hardened.
6. Re-run with normal ADB + selector execution before calling the flow stable.

## Sensitive Data

- Redact passwords, OTPs, account-private values, and other secrets.
- Replace real values with placeholders before promoting anything into the Skill source.
