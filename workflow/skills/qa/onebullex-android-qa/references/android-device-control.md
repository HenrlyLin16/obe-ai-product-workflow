# Android Device Control

Use this reference when a OneBullEx Android QA flow needs phone-level control rather than only in-app selectors.

## Responsibilities

- Verify `adb devices -l` can stably identify the target device before any real run.
- Keep the device awake and interactive.
- Check for lock-screen blockers before app automation starts.
- Return to home, back out of pages, open recent apps, or switch to an external app when the flow requires it.
- Handle narrow Android system dialogs only when their purpose is already known, such as a VPN permission confirmation.

## Boundaries

- Do not assume a locked device can be safely unlocked by automation; ask the user to unlock first.
- Do not silently dismiss unknown security prompts, payment prompts, or destructive confirmations.
- Do not treat unstable USB/Wi-Fi recognition as a product bug. Classify it as `environment_blocker`.
- Prefer package/activity launch or system commands first, then fall back to UI automation when Android does not expose a stable entry point.

## Common Controls

- `launch_app`
- `open_external_app`
- `ensure_foreground`
- `home`
- `back`
- `recent_apps`
- `open_notification_shade`
- `open_quick_settings`
- `handle_system_dialog`

## Reporting

Every run that uses device control should record:

- adb connection mode and stability result
- target serial/model/transport id
- whether the device was already unlocked
- which external apps were opened
- whether any system dialog needed manual help
