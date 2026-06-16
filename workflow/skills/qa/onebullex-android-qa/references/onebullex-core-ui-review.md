# OneBullEx Core UI Review Rules

Use these rules together with `ux-ui-checklist.md` when doing screenshot-backed UX/UI walkthroughs.

## Navigation

- Bottom navigation must have clear selected/unselected states for 首页、市场、合约、现货、资产/总览 entry points.
- Tap targets should be easy to reach on 1200x2670 devices; avoid tiny text-only hit areas.
- Top tabs must show a clear active state and preserve context when switching.

## Market List

- Symbol, price, volume, and change columns must align consistently row-to-row.
- Sorting taps must produce visible feedback: arrow direction, active column state, or row order change.
- Price/percentage precision and signs must be consistent; positive/negative colors must match CEX convention.
- Dense lists should remain readable without clipping symbol names, values, or percentage chips.

## Assets

- Total asset value and fiat conversion must have clear hierarchy.
- Asset actions such as 充值、提现、划转、历史记录 must be visually grouped and easy to tap.
- Spot and futures asset pages must clearly show which account type is active.
- Amounts, units, and approximate fiat values must align and remain readable.

## Buttons, Inputs, Dialogs

- Primary and secondary actions must be visually distinct and consistent.
- Disabled buttons must explain the reason or make the activation condition discoverable.
- Destructive/funds-related actions require second confirmation and visible risk context.
- Form errors must appear near the relevant field and explain how to recover.

## Loading, Empty, Error, Network

- Loading states should use skeletons or clear progress cues for content lists/cards.
- Empty states should explain what happened and what the user can do next.
- Network/permission/login blockers should provide recovery actions, not just fail silently.

## Finding Classification

- `ux_blocker`: blocks a user from completing a core flow or creates high-risk misunderstanding.
- `ui_inconsistency`: component state, spacing, alignment, hierarchy, or visual language conflicts with current app patterns.
- `copy_issue`: wording is inconsistent, unclear, too long, or lacks recovery guidance.
- `accessibility_issue`: readability, contrast, font size, touch target, or layout overflow issue.
- `visual_polish`: minor quality improvement, not a bug by default.
- `needs_design_confirmation`: cannot judge without product/design decision.
