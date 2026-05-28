# OBE AI 协作产品自动化工作流包

本目录用于 OBE 产品部门内部分享与落地。

## 给同事的最快使用方式

适用场景：其他产品同事从 Git 拉取本仓库或本目录后，在自己的本地 Codex / Cursor 中启用同一套产品工作流。

```bash
cd <your-onebullex-workspace>
./.codebuddy/docs/ai-product-workflow-sharing/scripts/install-local-workflow.sh
```

安装脚本会做三件事：

1. 检查核心文件是否存在。
2. 执行安全扫描，避免把真实 Token 当作模板传播。
3. 同步 `.codebuddy/skills` 到 Cursor 和 Codex 的本地 Skills 目录。

如果脚本不可执行：

```bash
bash .codebuddy/docs/ai-product-workflow-sharing/scripts/install-local-workflow.sh
```

## 文件说明

- `OBE-AI协作产品自动化工作流-Lark主文档.md`：Lark 主入口内容
- `OBE-AI协作产品自动化工作流-分享稿.md`：分享正文
- `OBE-AI协作工作流-操作手册.md`：给 PM/设计师的操作手册
- `OBE-AI协作工作流-Demo脚本.md`：10-15 分钟现场 Demo 脚本
- `templates/`：可复制复用的模板
- `demo-outputs/`：现场失败时可展示的预置结果
- `config/codex-local-integrations.example.toml`：Codex MCP 脱敏配置示例
- `config/lark.env.example`：Lark 环境变量示例
- `scripts/install-local-workflow.sh`：本地初始化与同步脚本
- `GIT_DISTRIBUTION.md`：上传 Git 与同事拉取说明

## Git 分发建议

建议把以下内容一起提交到 Git：

- `.codebuddy/docs/ai-product-workflow-sharing/`
- `.codebuddy/skills/product/web3-cex-product-team.md`
- `.codebuddy/skills/product/pipelines.yaml`
- `.codebuddy/skills/product/engineering-plan-review.md`
- `.codebuddy/skills/product/web3-prd-figma-prompt.md`
- `.codebuddy/skills/product/product-test-qa.md`
- `scripts/sync-codebuddy-skills-to-cursor.sh`
- `scripts/sync-codebuddy-skills-to-codex.sh`

不要提交：

- 真实 Token / API Key / Secret
- 个人 `.env`
- `.DS_Store`
- 本机生成的 `.cursor/skills` 或 `~/.codex/skills` 副本
- 未经脱敏的历史 demo / scripts 文件

## 同步到 Lark

当前 Lark 主文档：

- https://www.larksuite.com/docx/VdOndMhkroziXzxMKkHlihaXg5e
- 同步记录：`lark-sync-log.md`

```bash
lark-cli docs +create \
  --title "OBE 产品部门 AI 协作产品自动化工作流" \
  --markdown @.codebuddy/docs/ai-product-workflow-sharing/OBE-AI协作产品自动化工作流-Lark主文档.md
```

如需更新已有文档：

```bash
lark-cli docs +update \
  --doc "<Lark 文档 URL 或 token>" \
  --mode overwrite \
  --markdown @.codebuddy/docs/ai-product-workflow-sharing/OBE-AI协作产品自动化工作流-Lark主文档.md
```

## 安全检查

同步前执行：

```bash
rg -n "ntn_[A-Za-z0-9]|figd_[A-Za-z0-9]|AIza[0-9A-Za-z_-]|prj_[A-Za-z0-9]" .codebuddy/docs/ai-product-workflow-sharing
```

若有结果，先脱敏再同步。

完整 Git 分发范围的扫描命令见 `GIT_DISTRIBUTION.md`。不要直接扫描通过后提交整个工作区；本工作区历史脚本中可能存在旧的硬编码示例密钥。

## 本地配置

同事拉取 Git 后只需要配置自己的环境变量，不需要改模板文件。

```bash
cp .codebuddy/docs/ai-product-workflow-sharing/config/lark.env.example .env.local
```

然后按需配置：

- `FIGMA_OAUTH_TOKEN` 或 `FIGMA_API_KEY`
- `NOTION_TOKEN`
- `LARK_APP_ID`
- `LARK_APP_SECRET`

真实值只放在本地 shell、系统 keychain、`.env.local` 或个人 Codex/Cursor 配置里，不写回 Git。
