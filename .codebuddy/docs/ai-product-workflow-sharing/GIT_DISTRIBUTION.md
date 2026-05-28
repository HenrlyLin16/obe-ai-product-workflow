# Git 分发与同事本地配置指南

目标：把 OBE AI 协作产品自动化工作流包上传到 Git，让其他产品同事可以拉取后在本地 Codex / Cursor 中完成配置和复用。

## 1. 推荐仓库形态

优先级从高到低：

1. **放入现有 Onebullex 内部 Git 仓库**：最适合和 `.codebuddy/skills`、产品文档、同步脚本保持一致。
2. **创建独立私有仓库**：适合把工作流包抽象成部门工具包，减少对完整 Onebullex 工作区的依赖。
3. **只上传 Lark 附件**：不推荐，无法版本化，也不方便 Codex/Cursor 拉取。

## 2. 建议提交内容

必须提交：

```text
.codebuddy/docs/ai-product-workflow-sharing/
.codebuddy/skills/product/web3-cex-product-team.md
.codebuddy/skills/product/pipelines.yaml
.codebuddy/skills/product/engineering-plan-review.md
.codebuddy/skills/product/web3-prd-figma-prompt.md
.codebuddy/skills/product/product-test-qa.md
scripts/sync-codebuddy-skills-to-cursor.sh
scripts/sync-codebuddy-skills-to-codex.sh
```

按需提交：

```text
.codebuddy/docs/FIGMA-MCP-CAPABILITIES.md
.codebuddy/CODEX-LOCAL-MCP-SKILL-INTEGRATION.md
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
旧 demo 脚本或历史工具脚本，除非已完成密钥扫描和脱敏
```

## 3. 上传前检查

```bash
cd <repo-root>

find .codebuddy/docs/ai-product-workflow-sharing -name ".DS_Store" -print

rg -n "ntn_[A-Za-z0-9]|figd_[A-Za-z0-9]|AIza[0-9A-Za-z_-]|prj_[A-Za-z0-9]" \
  .codebuddy/docs/ai-product-workflow-sharing \
  .codebuddy/skills/product/web3-cex-product-team.md \
  .codebuddy/skills/product/pipelines.yaml \
  .codebuddy/skills/product/engineering-plan-review.md \
  .codebuddy/skills/product/web3-prd-figma-prompt.md \
  .codebuddy/skills/product/product-test-qa.md \
  scripts/sync-codebuddy-skills-to-cursor.sh \
  scripts/sync-codebuddy-skills-to-codex.sh

rg -n "^(GEMINI_API_KEY|FIGMA_API_KEY|NOTION_TOKEN|LARK_APP_SECRET|LARK_APP_ID)\\s*=\\s*[^\\s#]+" \
  --glob '!*.example' \
  --glob '!*.example.toml' \
  .codebuddy/docs/ai-product-workflow-sharing \
  .codebuddy/skills/product \
  scripts/sync-codebuddy-skills-to-cursor.sh \
  scripts/sync-codebuddy-skills-to-codex.sh
```

扫描结果只能出现示例命令或 `${ENV_VAR}` 占位，不能出现真实值。

注意：当前 Onebullex 工作区历史 `scripts/` 下存在旧 demo 文件和硬编码示例密钥，不应把整个 `scripts/` 目录作为部门分发包上传。

## 4. Git 命令模板

如果当前目录已经是 Git 仓库：

```bash
git status --short
git add \
  .codebuddy/docs/ai-product-workflow-sharing \
  .codebuddy/skills/product/web3-cex-product-team.md \
  .codebuddy/skills/product/pipelines.yaml \
  .codebuddy/skills/product/engineering-plan-review.md \
  .codebuddy/skills/product/web3-prd-figma-prompt.md \
  .codebuddy/skills/product/product-test-qa.md \
  scripts/sync-codebuddy-skills-to-cursor.sh \
  scripts/sync-codebuddy-skills-to-codex.sh
git commit -m "docs: add OBE AI product workflow package"
git push
```

如果当前目录不是 Git 仓库：

```bash
git init
git add \
  .codebuddy/docs/ai-product-workflow-sharing \
  .codebuddy/skills/product/web3-cex-product-team.md \
  .codebuddy/skills/product/pipelines.yaml \
  .codebuddy/skills/product/engineering-plan-review.md \
  .codebuddy/skills/product/web3-prd-figma-prompt.md \
  .codebuddy/skills/product/product-test-qa.md \
  scripts/sync-codebuddy-skills-to-cursor.sh \
  scripts/sync-codebuddy-skills-to-codex.sh
git commit -m "docs: add OBE AI product workflow package"
git remote add origin <private-git-remote-url>
git push -u origin main
```

## 5. 同事拉取后的本地配置

```bash
git clone <private-git-remote-url>
cd <repo>
bash .codebuddy/docs/ai-product-workflow-sharing/scripts/install-local-workflow.sh
```

配置个人密钥：

```bash
cp .codebuddy/docs/ai-product-workflow-sharing/config/lark.env.example .env.local
```

把真实值填入个人本地环境，不提交到 Git。

## 6. 同事验证方式

```bash
rg -n "feature-discovery|plan-review-gauntlet|engineering-plan-review" .codebuddy/skills/product
test -d ~/.codex/skills/onebullex && echo "Codex skills installed"
test -d .cursor/skills && echo "Cursor skills installed"
```

然后在 Codex 中输入：

```text
召唤产品专家团队，对“合约交易页价格提醒提醒方式优化”走 feature-discovery。
```
