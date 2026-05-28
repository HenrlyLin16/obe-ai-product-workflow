# Command Cheatsheet And Parameters To Edit

This page lists the commands a beginner can copy safely. Replace placeholders locally only.

## 1. Clone And Install

```bash
git clone https://github.com/HenrlyLin16/obe-ai-product-workflow.git
cd obe-ai-product-workflow
bash workflow/docs/ai-product-workflow-sharing/scripts/install-local-workflow.sh
```

## 2. Configure AI API

Copy the example:

```bash
cp workflow/docs/ai-product-workflow-sharing/config/ai-api.env.example .env.local
```

Edit `.env.local`:

```bash
ANTHROPIC_BASE_URL="https://ai.1bullex.com/api"
ANTHROPIC_AUTH_TOKEN="示例 Token"
```

Load it in your shell if needed:

```bash
set -a
source .env.local
set +a
```

## 3. Sync Skills

Cursor:

```bash
./scripts/sync-workflow-skills-to-cursor.sh
```

Codex:

```bash
./scripts/sync-workflow-skills-to-codex.sh
```

Verify:

```bash
test -d ~/.codex/skills/onebullex && echo "Codex skills installed"
test -d .cursor/skills && echo "Cursor skills installed"
```

## 4. Beginner Lark Flow

Manual first: copy AI output into a Lark document.

Advanced CLI later:

```bash
cp workflow/docs/ai-product-workflow-sharing/config/lark.env.example .env.local
# Edit LARK_APP_ID, LARK_APP_SECRET, and keep LARK_WRITE_DRY_RUN=true until tested.
lark-cli docs +create \
  --title "OBE AI 协作产品自动化工作流" \
  --markdown @workflow/docs/ai-product-workflow-sharing/OBE-AI协作产品自动化工作流-Lark主文档.md
```

Parameters to edit:

- `LARK_APP_ID`: your local app id.
- `LARK_APP_SECRET`: your local app secret.
- `LARK_WRITE_DRY_RUN`: keep `true` for testing, change only after you confirm the target space.
- `LARK_ALLOWED_SPACE_IDS`: optional allowlist for safer writes.

## 5. Beginner Figma Flow

Manual first: copy the generated `web3-prd-figma-prompt` output into Figma Make or send it to a designer.

Advanced MCP later:

- Edit `FIGMA_OAUTH_TOKEN` or `FIGMA_API_KEY` in `.env.local`.
- Copy relevant Figma sections from `config/codex-local-integrations.example.toml` into `~/.codex/config.toml`.
- For html-to-design capture, ensure URL hash starts with `#figmacapture=`.

## 6. Beginner Vercel Flow

Manual first: ask the agent for build and deploy checklist, then deploy from the correct project root.

Advanced CLI later:

```bash
vercel login
vercel --prod
```

Parameters to confirm before publishing:

- local project directory
- build command
- output directory
- environment variables
- production vs preview deployment

## 7. Find Skill And Workflow Names

```bash
rg -n "feature-discovery|prd-and-qa|plan-review-gauntlet|prototype-full" workflow/skills/product
```

## 8. Troubleshooting

- Codex cannot find Skills: rerun `./scripts/sync-workflow-skills-to-codex.sh` and restart Codex.
- Cursor cannot find Skills: rerun `./scripts/sync-workflow-skills-to-cursor.sh` and restart Cursor.
- AI API fails: confirm `ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN` are loaded in the shell that starts the client.
- Lark write fails: use manual copy first; then check `lark-cli auth status` and `LARK_WRITE_DRY_RUN`.
- Figma capture pending: check `#figmacapture=` hash order and use system Chrome.
- Vercel deploys wrong app: confirm root directory before deploy.
