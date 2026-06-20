# Mac Clash VPN Gate

Use this reference before Web QA flows that require VPN or when testnet reachability is suspect.

## Client

- App: `/Applications/ClashX Pro.app`
- Do not read Clash config files, proxy credentials, node names, or logs.
- Do not switch nodes automatically in the first implementation.

## Available Criteria

VPN is considered available only when all applicable criteria pass:

1. ClashX Pro app exists.
2. ClashX Pro process is running, or the app can be opened.
3. Clash UI has `设置为系统代理` enabled.
4. macOS system proxy state can be cross-checked with `scutil --proxy`.
5. The QA precheck actively probes testnet HTTP / REST / WS to generate traffic.
6. Clash menu bar traffic is confirmed as `>0kb`.
7. testnet HTTP / REST / WS probes are reachable under the current network state.

## Traffic Confirmation

If menu-bar traffic cannot be read programmatically, pause for manual confirmation. The report must record whether traffic `>0kb` was manually confirmed. A historical nonzero value is not enough; the probe should generate current traffic.

## Classification

- Clash missing, not running, system proxy disabled, traffic not confirmed, or HTTP unreachable -> `environment_blocker`.
- REST or WS partial failure while HTTP works -> `service_degradation`.
- Never classify VPN or proxy failure as a product bug.

## CLI Defaults

- `--vpn-mode off`: do not run this gate.
- `--vpn-mode auto`: run this gate when the flow declares `requires_clash_vpn: true` or health checks suggest network problems.
- `--vpn-mode required`: run this gate before target flows and block on failure unless the user explicitly skips it.
