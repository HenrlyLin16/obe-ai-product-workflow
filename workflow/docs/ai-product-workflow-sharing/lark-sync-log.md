# Lark 同步记录

## OBE AI 协作产品自动化工作流

- sync_mode: template
- source_path: `workflow/docs/ai-product-workflow-sharing/OBE-AI协作产品自动化工作流-Lark主文档.md`
- doc_id: `[YOUR_LARK_DOC_ID]`
- doc_url: `[YOUR_LARK_DOC_URL]`
- synced_at: `[YOUR_SYNC_TIME]`
- sync_status: `[pending|success|failed]`
- tool: `lark-cli docs +create` 或 `lark-cli docs +update`

## 创建命令

```bash
lark-cli docs +create \
  --title "OBE AI 协作产品自动化工作流" \
  --markdown @workflow/docs/ai-product-workflow-sharing/OBE-AI协作产品自动化工作流-Lark主文档.md
```

## 更新命令

```bash
lark-cli docs +update \
  --doc "[YOUR_LARK_DOC_URL_OR_TOKEN]" \
  --mode overwrite \
  --markdown @workflow/docs/ai-product-workflow-sharing/OBE-AI协作产品自动化工作流-Lark主文档.md
```
