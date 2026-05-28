# Public Git 分发与本地配置指南

目标：把 OBE AI 协作产品自动化工作流包作为公开模板仓库发布，让使用者可以通过 GitHub 拉取后，在自己的 Codex / Cursor 环境中完成配置和自定义。

## 1. 推荐仓库形态

本包按 Public GitHub 仓库处理：

- 仓库名：`obe-ai-product-workflow`
- 公开地址：`https://github.com/HenrlyLin16/obe-ai-product-workflow`
- 仓库内容只包含可分发的工作流文档、模板、产品 Skill 与同步脚本。
- 不依赖完整业务工作区，不提交私有文档、个人路径、私有知识源链接或真实密钥。

## 2. 建议提交内容

必须提交：

```text
README.md
START_HERE.md
workflow/docs/ai-product-workflow-sharing/
workflow/skills/product/web3-cex-product-team.md
workflow/skills/product/pipelines.yaml
workflow/skills/product/engineering-plan-review.md
workflow/skills/product/web3-prd-figma-prompt.md
workflow/skills/product/product-test-qa.md
scripts/sync-workflow-skills-to-cursor.sh
scripts/sync-workflow-skills-to-codex.sh
```

按需提交：

```text
workflow/docs/FIGMA-MCP-CAPABILITIES.md
workflow/CODEX-LOCAL-MCP-SKILL-INTEGRATION.md
tools/lark-mcp-server/docs/
```

不要提交：

```text
.DS_Store
.env
.env.local
.cursor/skills/
~/.codex/skills/
真实 Token / API Key / Secret
个人本机路径
内部 Lark / Notion / NotebookLM URL 或页面 ID
未经脱敏的历史 demo / scripts 文件
```

## 3. 上传前检查

```bash
cd <repo-root>

find workflow/docs/ai-product-workflow-sharing -name ".DS_Store" -print

rg -n "ntn_[A-Za-z0-9]|figd_[A-Za-z0-9]|AIza[0-9A-Za-z_-]|prj_[A-Za-z0-9]" \
  workflow/docs/ai-product-workflow-sharing \
  workflow/skills/product/web3-cex-product-team.md \
  workflow/skills/product/pipelines.yaml \
  workflow/skills/product/engineering-plan-review.md \
  workflow/skills/product/web3-prd-figma-prompt.md \
  workflow/skills/product/product-test-qa.md \
  scripts/sync-workflow-skills-to-cursor.sh \
  scripts/sync-workflow-skills-to-codex.sh

rg -n "^(GEMINI_API_KEY|FIGMA_API_KEY|NOTION_TOKEN|LARK_APP_SECRET|LARK_APP_ID)\\s*=\\s*[^\\s#]+" \
  --glob '!*.example' \
  --glob '!*.example.toml' \
  workflow/docs/ai-product-workflow-sharing \
  workflow/skills/product \
  scripts/sync-workflow-skills-to-cursor.sh \
  scripts/sync-workflow-skills-to-codex.sh
```

扫描结果只能出现示例命令或 `${ENV_VAR}` 占位，不能出现真实值。

继续执行公开发布检查：

```bash
git ls-files -z | xargs -0 rg -n \
  "[l]injinhong|[g]mail|/[U]sers/|[l]arksuite\\.com/docx|[n]otebooklm\\.google\\.com/notebook|[0-9a-f]{32}|私有仓[库]|内[部] Git|部门内[部]|项目内[部]知识|内[部]知识库"
```

期望没有输出。若有输出，先改成通用占位或配置说明，再重新提交。

## 4. Git 命令模板

如果当前目录已经是 Git 仓库：

```bash
git status --short
git add \
  README.md \
  START_HERE.md \
  workflow/docs/ai-product-workflow-sharing \
  workflow/skills/product/web3-cex-product-team.md \
  workflow/skills/product/pipelines.yaml \
  workflow/skills/product/engineering-plan-review.md \
  workflow/skills/product/web3-prd-figma-prompt.md \
  workflow/skills/product/product-test-qa.md \
  scripts/sync-workflow-skills-to-cursor.sh \
  scripts/sync-workflow-skills-to-codex.sh
git commit -m "docs: prepare public OBE AI workflow package"
git remote add origin https://github.com/HenrlyLin16/obe-ai-product-workflow.git
git push -u origin main
```

如果当前目录不是 Git 仓库：

```bash
git init
git add \
  README.md \
  START_HERE.md \
  workflow/docs/ai-product-workflow-sharing \
  workflow/skills/product/web3-cex-product-team.md \
  workflow/skills/product/pipelines.yaml \
  workflow/skills/product/engineering-plan-review.md \
  workflow/skills/product/web3-prd-figma-prompt.md \
  workflow/skills/product/product-test-qa.md \
  scripts/sync-workflow-skills-to-cursor.sh \
  scripts/sync-workflow-skills-to-codex.sh
git commit -m "docs: prepare public OBE AI workflow package"
git remote add origin https://github.com/HenrlyLin16/obe-ai-product-workflow.git
git push -u origin main
```

## 5. 使用者拉取后的本地配置

```bash
git clone https://github.com/HenrlyLin16/obe-ai-product-workflow.git
cd obe-ai-product-workflow
bash workflow/docs/ai-product-workflow-sharing/scripts/install-local-workflow.sh
```

配置个人 AI API：

```bash
cp workflow/docs/ai-product-workflow-sharing/config/ai-api.env.example .env.local
```

先只填写 `ANTHROPIC_BASE_URL` 和 `ANTHROPIC_AUTH_TOKEN`。Lark、Figma、Vercel 是进阶能力，建议先手动复制结果，熟悉后再复制 `config/lark.env.example` 中对应参数到 `.env.local`。真实值只放本地，不提交到 Git。

## 6. 使用者验证方式

```bash
rg -n "feature-discovery|plan-review-gauntlet|engineering-plan-review" workflow/skills/product
test -d ~/.codex/skills/onebullex && echo "Codex skills installed"
test -d .cursor/skills && echo "Cursor skills installed"
```

然后在 Codex 中输入：

```text
召唤产品专家团队，对“合约交易页价格提醒提醒方式优化”走 feature-discovery。
```
