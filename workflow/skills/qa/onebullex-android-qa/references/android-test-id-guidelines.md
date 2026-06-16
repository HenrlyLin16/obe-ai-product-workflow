# Android Test ID Guidelines For OneBullEx

Add stable `content-desc` or test-only `resource-id` values for QA automation. Do not rely on visual screenshots or coordinates as the primary control surface.

## Recommended IDs

Navigation:

- `tab-home`
- `tab-market`
- `tab-futures`
- `tab-spot`
- `tab-assets`

Market sorting:

- `market-sort-symbol`
- `market-sort-volume`
- `market-sort-price`
- `market-sort-change`

Assets:

- `asset-tab-overview`
- `asset-tab-spot`
- `asset-tab-futures`

Login:

- `login-entry`
- `login-email-input`
- `login-password-input`
- `login-submit-button`

Futures order flow:

- `futures-symbol-selector`
- `futures-open-long-button`
- `futures-open-short-button`
- `order-price-input`
- `order-size-input`
- `order-preview-button`
- `order-confirm-button`

## Rules

- IDs should be stable across languages and copy changes.
- IDs should not include dynamic values such as symbol names or balances unless they identify repeated row items by a documented pattern.
- Keep IDs available in dev/test builds at minimum; production can hide test-only IDs if required.
- Every destructive or side-effectful action needs a distinct confirm button ID so the QA flow can stop before it.
