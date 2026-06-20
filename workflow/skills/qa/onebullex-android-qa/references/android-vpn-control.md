# Android VPN Control

This Skill can optionally prepare VPN before a flow runs.

## Current Defaults

- Package: `com.follow.clash`
- Mode: `auto`
- Target mode: `reuse_last`
- Failure policy: `pause_for_manual`

## Behavior

- If the flow does not require VPN and the user did not force it, do not open FIClash.
- If VPN is required, first check whether it is already connected.
- Prefer launcher/intent-style app entry first.
- If Android shows the standard VPN confirmation dialog, the Skill may accept that narrow prompt.
- If the app cannot be opened or VPN does not connect in time, stop and wait for the user.

## Boundaries

- Do not configure a new subscription or import a first-time profile automatically.
- Do not guess a new node/profile when `reuse_last` is the agreed mode.
- Do not classify VPN connection failure as a product bug for OneBullEx.
