# Zentao Bug Filing Flow

Use this reference after the QA report is generated and the user confirms which issues should be filed.

## Destination

Open the create page in Chrome:

`https://zentao.1bullex.com/index.php?m=bug&f=create&productID=1&branch=0&extra=moduleID=0`

Use existing Chrome login state. Preferred account: `Henrly linjinhong16@gmail.com`.

## Form Fields From Screenshot

The simplified `提Bug` page includes:

- Required `所属产品`: default/select `OneBullEx`.
- `所属模块`: default `/` unless the confirmed issue names a more precise module.
- Required `影响版本`: choose the confirmed build/dev version if known. If unknown, pause and ask.
- `当前指派`: leave blank/default unless the user specifies an assignee.
- `截止日期`: leave blank unless the user specifies a deadline.
- Required `Bug标题`: use the confirmed draft title.
- `Bug类型`: default `代码错误` unless the symptom is clearly UI/体验/需求类 and the user agrees.
- `严重程度`: default the draft value, commonly `3`.
- `优先级`: default the draft value, commonly `3`.
- `重现步骤`: paste the draft body with `[步骤]`, `[结果]`, `[期望]`.
- `附件`: upload screenshots/logs/XML only when the user approves those files.
- `保存`: final side-effect button; never click before explicit user confirmation.

## Chrome Operation Rules

- Use the Chrome plugin/skill because Zentao depends on logged-in browser state.
- Do not read or inspect cookies, passwords, local storage, or profile internals.
- If login, account selection, CAPTCHA, or permission prompts appear, stop and let the user handle them.
- Prefer DOM/Playwright interactions for stable fields; use visual interaction only when DOM labels are insufficient.
- After filling each draft, summarize the exact title, body, severity/priority, and attachments, then ask for explicit approval before clicking `保存`.

## Draft Mapping

`zentao-bug-drafts.json` fields map as follows:

- `product` -> `所属产品`
- `module` -> `所属模块`
- `affected_version` -> `影响版本`
- `title` -> `Bug标题`
- `bug_type` -> `Bug类型`
- `severity` -> `严重程度`
- `priority` -> `优先级`
- `repro_steps` -> `重现步骤`
- `attachments` -> `附件`

If `affected_version` is empty and Zentao requires it, pause and ask the user which version to choose.
