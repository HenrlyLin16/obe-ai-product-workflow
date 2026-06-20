# Android ADB Stability Gate

`adb devices -l` stable recognition is the first hard gate for every non-dry-run.

## Pass Conditions

- The target device appears in `adb devices -l`.
- The state is `device`.
- When `--serial` is provided, the serial must match exactly.
- When `--serial` is omitted, there must be exactly one ready device.
- The same ready device must be observed in consecutive samples before the run continues.

## Fail Conditions

- State is `offline`, `unauthorized`, `recovery`, or any non-`device` state.
- The device appears and disappears across retries.
- More than one ready device exists and no serial was provided.
- USB/Wi-Fi reconnect causes identity ambiguity.

## Recommended Defaults

- `--adb-stability-retries 3`
- `--adb-stability-interval-ms 800`
- Record the final snapshot, selected serial, model, and transport id in the report.

## Classification

- Stable-recognition failure is always an `environment_blocker`.
- Do not proceed to APK gate, VPN, or app-flow execution until this gate passes.
