# OBE AI 协作产品自动化工作流包

本目录用于公开分发一套可自定义的 AI 产品协作工作流模板，覆盖 PRD、设计衔接、工程计划评审、测试验收、Lark/Figma/Codex/Cursor 协作等场景。


## 新手最快路径

如果你第一次使用，不要先配置所有 MCP。先按以下顺序拿到第一个可用产出：

1. 读根目录 `START_HERE.md`，复制第一个 Demo 提示词。
2. 克隆仓库并运行安装脚本。
3. 复制 `config/ai-api.env.example` 为 `.env.local`，只改 `ANTHROPIC_BASE_URL` 与 `ANTHROPIC_AUTH_TOKEN`。
4. 在 Codex 或 Cursor 中先跑 `feature-discovery`，确认能得到需求澄清结论。
5. 把结果手动复制到 Lark；熟悉后再配置 Lark/Figma/Vercel 的 MCP 或 CLI 自动同步。

推荐学习顺序：

- 15 分钟：跑通 `feature-discovery`。
- 30 分钟：跑通 `prd-and-qa`，得到 PRD + 验收标准。
- 60 分钟：学习 `plan-review-gauntlet`，让多 Agent 做联合评审。
- 进阶：再配置 Lark、Figma、Vercel 自动化。

## 初学者可以改哪些文件

| 目的 | 修改文件 | 只改这些参数 |
|------|----------|--------------|
| 接入 OBE AI API | `.env.local`，来源 `config/ai-api.env.example` | `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN` |
| 手动填需求信息 | `templates/需求澄清模板.md`、`templates/PRD交付模板.md` | 功能名、用户场景、目标端、非目标、验收标准 |
| Lark 自动同步（进阶） | `.env.local`，来源 `config/lark.env.example` | `LARK_APP_ID`, `LARK_APP_SECRET`, `LARK_WRITE_DRY_RUN` |
| Figma MCP（进阶） | `.env.local` + `config/codex-local-integrations.example.toml` | `FIGMA_OAUTH_TOKEN` 或 `FIGMA_API_KEY` |
| Codex MCP（进阶） | `~/.codex/config.toml` | 复制所需 `[mcp_servers.*]` 段落 |

初学者不要直接修改：`.codebuddy/skills/product/pipelines.yaml`、Skill 文件、`.cursor/skills`、`~/.codex/skills`。

## GitHub 文件地图

| 文件 | 什么时候看 |
|------|------------|
| `START_HERE.md` | 第一次使用，先看这个 |
| `docs/beginner-recipes.md` | 不知道该复制哪条提示词时 |
| `docs/command-cheatsheet.md` | 需要命令或配置参数时 |
| `OBE-AI协作产品自动化工作流-Lark主文档.md` | 要复制到 Lark 作为团队主文档时 |
| `OBE-AI协作工作流-操作手册.md` | 已经跑通过 Demo，想系统使用时 |
| `templates/` | 要把输出整理成正式交付物时 |
| `.codebuddy/skills/product/` | 进阶维护 Skill 或工作流时 |

## 最快使用方式

适用场景：从 GitHub 拉取本仓库后，在自己的本地 Codex / Cursor 中启用同一套产品工作流。

```bash
git clone https://github.com/HenrlyLin16/obe-ai-product-workflow.git
cd obe-ai-product-workflow
bash .codebuddy/docs/ai-product-workflow-sharing/scripts/install-local-workflow.sh
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

- `OBE-AI协作产品自动化工作流-Lark主文档.md`：可复制到 Lark 的主文档模板
- `OBE-AI协作产品自动化工作流-分享稿.md`：分享正文
- `OBE-AI协作工作流-操作手册.md`：给 PM/设计师的操作手册
- `OBE-AI协作工作流-Demo脚本.md`：10-15 分钟现场 Demo 脚本
- `templates/`：可复制复用的模板
- `demo-outputs/`：现场失败时可展示的预置结果
- `config/ai-api.env.example`：OBE 第三方 AI API 环境变量示例
- `config/codex-local-integrations.example.toml`：Codex MCP 脱敏配置示例
- `config/lark.env.example`：Lark / Figma 进阶环境变量示例
- `docs/beginner-recipes.md`：初学者任务食谱
- `docs/command-cheatsheet.md`：常用命令与参数速查
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
- 个人本机路径
- 内部 Lark / Notion / NotebookLM URL 或页面 ID
- 未经脱敏的历史 demo / scripts 文件

## 同步到 Lark

本仓库不包含任何私有 Lark 文档链接。使用者可以把主文档模板创建到自己的 Lark 空间：

```bash
lark-cli docs +create \
  --title "OBE AI 协作产品自动化工作流" \
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

公开发布前执行：

```bash
rg -n "ntn_[A-Za-z0-9]|figd_[A-Za-z0-9]|AIza[0-9A-Za-z_-]|prj_[A-Za-z0-9]" .codebuddy/docs/ai-product-workflow-sharing
git ls-files -z | xargs -0 rg -n "[l]injinhong|[g]mail|/[U]sers/|[l]arksuite\\.com/docx|[n]otebooklm\\.google\\.com/notebook|[0-9a-f]{32}|私有仓[库]|内[部] Git|部门内[部]|项目内[部]知识|内[部]知识库"
```

若有结果，先脱敏再同步。

完整 Git 分发范围的扫描命令见 `GIT_DISTRIBUTION.md`。只提交本仓库明确放行的文件，不提交完整业务工作区。

## 本地配置

使用者拉取 Git 后，初学者只需要先配置 AI API：

```bash
cp .codebuddy/docs/ai-product-workflow-sharing/config/ai-api.env.example .env.local
```

先改：

- `ANTHROPIC_BASE_URL`
- `ANTHROPIC_AUTH_TOKEN`

Lark、Figma、Vercel 属于进阶能力，建议手动复制结果验证流程后再配置：

- Lark：`LARK_APP_ID`、`LARK_APP_SECRET`、`LARK_WRITE_DRY_RUN`
- Figma：`FIGMA_OAUTH_TOKEN` 或 `FIGMA_API_KEY`
- Vercel：先用 `vercel login`，仅在本地流程需要时配置 `VERCEL_TOKEN`

真实值只放在本地 shell、系统 keychain、`.env.local` 或个人 Codex/Cursor 配置里，不写回 Git。Notion、Lark、NotebookLM 等知识源请接入自己的 workspace / document / notebook。
