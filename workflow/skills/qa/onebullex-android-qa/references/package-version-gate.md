# OneBullEx Android APK Version Gate

Use this reference before every real-device QA run.

## Channels

- Dev: `https://app-space.1bullex.com/android-dev-onebullex`, package `com.onemore.onebullex.dev`.
- Production: `https://app-space.1bullex.com/android-onebullex`, package `com.onemore.onebullex`.

Default to dev. Use production only when the user explicitly asks for production package testing and confirms the risk.

## Required Gate

Before any non-dry-run flow, run the version guard unless the user explicitly passes `--skip-version-check`:

```bash
python3 /Users/jingxing/.codex/skills/onebullex-android-qa/scripts/apk_version_guard.py \
  --channel dev \
  --serial SM02G4061923909
```

The guard writes JSON with:

- `status`: `latest`, `outdated`, `not_installed`, or `unknown`.
- device version: `device_version_name`, `device_version_code`, install/update times.
- remote version: `remote_version_name`, `remote_version_code`, `apk_url`, metadata source.
- `recommended_action` for the agent and user.

## Decision Rules

- `latest`: continue QA and record the version-check JSON in the report.
- `outdated`: stop before QA. Ask the user whether to install the latest package.
- `not_installed`: stop before QA. Ask the user whether to install the selected channel package.
- `unknown`: stop before QA. Do not assume the package is current; ask for user confirmation or a reliable APK.
- `skipped`: allowed only by explicit user request; mark the report as lower confidence.

## Install Policy

Install only after explicit human confirmation.

Preferred path:

1. Extract direct APK URL from app-space page.
2. Download APK to `/tmp/onebullex-android-qa/apk-cache`.
3. Inspect APK package and version with `aapt` or `apkanalyzer` when available.
4. Refuse install if the APK package does not match the selected channel.
5. Install with `adb install -r`.

Fallback path when no direct APK URL is available:

```bash
adb -s <serial> shell am start -a android.intent.action.VIEW -d <app-space-url>
```

Then control or guide the phone through download/install prompts. Android package installer prompts may require manual interaction.

## Safety Rules

- Never silently install production over dev or dev over production.
- Never downgrade without a separate explicit confirmation.
- Never run product conclusions on a stale, missing, or unknown package unless the user deliberately accepts the risk.
- Treat version-gate failures as `environment_blocker`, not product bugs.
