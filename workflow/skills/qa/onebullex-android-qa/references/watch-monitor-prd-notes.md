# OneBullEx Watch Monitor PRD Notes

Source document:

- Title: `OBE App 实时盯盘浮窗`
- URL: `https://wsgysqudq8b5.sg.larksuite.com/docx/OiJSdNXg0ohwOOxLQJ1ldpchgEd?from=from_copylink`
- Read via: `lark-cli docs +fetch --doc '<url>'`

## P0 behavior to validate on Android

- Entry path exists in K-line settings sheet: `实时盯盘浮窗` with subtitle `开启后可实时查看币种波动趋势`.
- Watch monitor management page contains:
  - title `实时盯盘`
  - top banner about background running
  - toggle row `实时盯盘浮窗`
  - list area and `添加币对`
- Enabling watch monitor with an empty list must lead the user to add at least one pair.
- Add sheet supports `合约 | 现货` tabs.
- Selecting a contract pair such as `BTCUSDT 永续` should create a watched pair and show the floating card.
- Floating card is for watch-only behavior; no trade-side action is in scope.
- Android should support overlay visibility when leaving the trading page and when going to another app.

## Important product rules

- `spot` display name: `{base}/{quote}`.
- `usdt_perp` display name: `{symbol} 永续`.
- Displayed price uses `lastPrice` for both spot and USDT perpetual.
- `缩小` is not equal to closing the feature.
- `关闭 ×` on the floating card should be equivalent to Toggle OFF.
- If all watched pairs are removed, the feature should auto-close.

## Execution notes from device exploration

- Current device: `SM02G4061923909` / Solana Seeker / Android 16.
- Current package seen on device: `com.onemore.onebullex.dev` version `1.9.0-dev (26060810)`.
- Package gate from app-space is currently `unknown`; this run must record accepted risk.
- Current Android overlay permission had to be granted via:
  - `adb shell appops set com.onemore.onebullex.dev SYSTEM_ALERT_WINDOW allow`
- Observed live selectors and coordinates:
  - Home bottom nav `合约`: coordinate fallback around `[600,2550]`
  - Contract page `K线图`: text `K线图`, fallback `[1002,212]`
  - K-line page `设置`: desc/text `设置`, fallback `[1133,682]`
  - Settings sheet entry `实时盯盘浮窗`: row fallback `[600,2325]`
  - Watch monitor toggle: fallback `[1062,564]`
  - Add button: text `添加币对`, fallback `[600,2450]`
  - Add sheet first contract checkbox: fallback `[1128,1188]`
- The floating card appears in screenshots but is not surfaced in `uiautomator` XML, so its controls currently need screenshot evidence and coordinate-only attempts.

## Recommended classification

- `product_bug`
  - wrong entry copy or missing entry
  - no add flow after enabling feature
  - watched pair cannot be created
  - watched pair removal does not update page state
- `automation_issue`
  - floating card controls require coordinate fallback only
  - bottom button taps near the gesture bar are unstable
- `environment_blocker`
  - not logged in
  - not on a reachable K-line/contract route
  - overlay permission disabled
  - background permission page/system dialog blocks the flow
