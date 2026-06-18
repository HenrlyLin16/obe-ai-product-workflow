# Web Test ID Guidelines

Use this reference when requesting stable automation IDs from Web developers.

## Why Test IDs Matter

Web QA relies on DOM selectors. Without stable test IDs, flows fall back to fragile CSS/text/coordinate selectors, increasing false-positive automation failures.

## Request Format

When requesting test IDs from Web developers, provide:

```markdown
### Page: [page name]
- Element: [description]
- Suggested data-testid: [kebab-case identifier]
- Reason: [which flow/assertion depends on this]
```

## Naming Convention

- Use `kebab-case` for `data-testid` attributes.
- Prefix with page/feature scope: `trade-`, `asset-`, `market-`, `login-`, `order-`.
- Include element type when ambiguous: `trade-submit-btn`, `trade-price-input`.

## Priority Elements

These elements provide the highest leverage for automation stability:

### Trading Pages
- Order form inputs: `trade-price-input`, `trade-qty-input`, `trade-leverage-slider`
- Submit buttons: `trade-open-long-btn`, `trade-open-short-btn`, `trade-close-btn`
- Mode toggles: `trade-margin-mode-toggle`, `trade-order-type-toggle`
- Position list: `position-table`, `position-row-{symbol}`
- Order list: `order-table`, `order-row-{id}`

### Asset Pages
- Balance blocks: `asset-spot-balance`, `asset-futures-margin`
- Transfer controls: `asset-transfer-amount`, `asset-transfer-submit`

### Navigation
- Main nav items: `nav-market`, `nav-trade`, `nav-assets`
- Sub nav / tabs: `tab-spot`, `tab-futures`, `tab-orders`

### Authentication
- Login form: `login-email-input`, `login-password-input`, `login-submit-btn`
- User menu: `user-menu-trigger`, `user-uid`

### General
- Toast container: `toast-container`
- Loading indicators: `loading-spinner`
- Error states: `error-message`, `error-retry-btn`
- Empty states: `empty-state-message`

## CSS Selector Fallback (When Test IDs Are Missing)

When test IDs are not available, prefer these CSS patterns:

- Form inputs: `input[placeholder*="价格"]`, `input[name="price"]`
- Buttons: `button:has-text("开多")`, `button.submit-btn`
- Tables: `table.ant-table`, `[class*="position-table"]`
- Navigation: `nav a[href*="/trade"]`, `[class*="nav-item"]`

These patterns are more fragile than `data-testid` and should be flagged in reports as needing developer collaboration.

## Coordination with Android QA

Test ID names should align with Android `resource-id` / `content-desc` conventions where the same logical element exists on both platforms, so cross-platform regression reports are readable.
