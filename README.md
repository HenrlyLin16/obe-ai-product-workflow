# OBE AI Product Workflow

This repository is a reusable workflow package for product managers, designers, and product leads. It helps teams turn a rough product idea into PRD, acceptance criteria, design handoff, review notes, and Lark-ready documentation with Codex or Cursor.

Start here if you are new:

- Read `START_HERE.md` first.
- Then run the installer and copy one beginner prompt.
- Treat Lark, Figma, and Vercel as advanced integrations: copy results manually first, then configure MCP/CLI when the workflow is familiar.

## Fast Path

```bash
git clone https://github.com/HenrlyLin16/obe-ai-product-workflow.git
cd obe-ai-product-workflow
cp .codebuddy/docs/ai-product-workflow-sharing/config/ai-api.env.example .env.local
bash .codebuddy/docs/ai-product-workflow-sharing/scripts/install-local-workflow.sh
```

Set your AI API token locally before launching Codex or Cursor:

```bash
export ANTHROPIC_BASE_URL="https://ai.1bullex.com/api"
export ANTHROPIC_AUTH_TOKEN="示例 Token"
```

## What To Read

- `START_HERE.md` - beginner path and first prompts.
- `.codebuddy/docs/ai-product-workflow-sharing/README.md` - package details and file map.
- `.codebuddy/docs/ai-product-workflow-sharing/docs/beginner-recipes.md` - copyable task recipes.
- `.codebuddy/docs/ai-product-workflow-sharing/docs/command-cheatsheet.md` - commands and parameters to edit.
- `.codebuddy/docs/ai-product-workflow-sharing/OBE-AI协作产品自动化工作流-Lark主文档.md` - content to copy into Lark.

## Safe Editing Rule

Beginners should only edit:

- `.env.local` for local tokens and integration parameters.
- Files under `.codebuddy/docs/ai-product-workflow-sharing/templates/` for their own task content.
- Prompt text copied into Codex or Cursor.

Do not edit `.codebuddy/skills/product/pipelines.yaml` or Skill files until you understand how triggers and quality gates work.
