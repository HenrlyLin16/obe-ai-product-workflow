# OBE AI 产品工作流

这是一个面向产品经理、设计师和产品负责人的可复用 AI 产品工作流包。它帮助团队把一句粗略想法，快速整理成需求澄清、PRD、验收标准、设计衔接、联合评审结论，以及可复制到 Lark 的协作文档。

如果你是第一次使用，请按这个顺序：

- 先读 `START_HERE.md`，复制第一个 Demo 提示词。
- 再运行安装脚本，把产品 Skills 同步到 Codex / Cursor。
- Lark、Figma、Vercel 都先当作进阶能力：第一轮先手动复制结果，熟悉后再配置 MCP / CLI 自动同步。

## 最快开始

```bash
git clone https://github.com/HenrlyLin16/obe-ai-product-workflow.git
cd obe-ai-product-workflow
cp workflow/docs/ai-product-workflow-sharing/config/ai-api.env.example .env.local
bash workflow/docs/ai-product-workflow-sharing/scripts/install-local-workflow.sh
```

启动 Codex 或 Cursor 前，在本地 shell 设置 AI API：

```bash
export ANTHROPIC_BASE_URL="https://ai.1bullex.com/api"
export ANTHROPIC_AUTH_TOKEN="示例 Token"
```

真实 Token 只放在本地环境变量或 `.env.local`，不要提交到 Git。

## 先看哪些文件

- `START_HERE.md`：新手入口，包含第一次使用路径和第一条提示词。
- `workflow/docs/ai-product-workflow-sharing/README.md`：工作流包说明与文件地图。
- `workflow/docs/ai-product-workflow-sharing/docs/beginner-recipes.md`：常见任务食谱，可直接复制提示词。
- `workflow/docs/ai-product-workflow-sharing/docs/command-cheatsheet.md`：常用命令和需要修改的参数。
- `workflow/docs/ai-product-workflow-sharing/OBE-AI协作产品自动化工作流-Lark主文档.md`：可复制到 Lark 的团队主文档。

## 新手默认只改这些

- `.env.local`：配置本地 AI API、Lark、Figma 等私有参数。
- `workflow/docs/ai-product-workflow-sharing/templates/`：把模板复制成自己的需求文档。
- 复制到 Codex / Cursor 的提示词：替换功能名、用户场景、目标端和非目标。

先不要改 `workflow/skills/product/pipelines.yaml` 或 Skill 文件；等你理解触发词、质量门和多 Agent 分工后，再由产品负责人统一维护。

## 三个最常用工作流

| 工作流 | 什么时候用 | 产出 |
|--------|------------|------|
| `feature-discovery` | 想法还模糊，需要判断做不做 | 做/不做/延后/缩小范围、目标用户、风险、下一步 |
| `prd-and-qa` | 已确定要做，需要交付 PRD 和验收 | PRD 摘要、功能范围、页面状态、业务规则、测试用例 |
| `plan-review-gauntlet` | 进入设计或开发前，需要多角色评审 | 产品、体验、工程、测试评审结论和阻断项 |

## 进阶自动化

初学者先手动复制结果到 Lark、Figma 或 Vercel 发布记录。确认流程有用后，再按 `workflow/docs/ai-product-workflow-sharing/docs/command-cheatsheet.md` 配置：

- Lark：`LARK_APP_ID`、`LARK_APP_SECRET`、`LARK_WRITE_DRY_RUN`
- Figma：`FIGMA_OAUTH_TOKEN` 或 `FIGMA_API_KEY`
- Codex MCP：`~/.codex/config.toml`
- Vercel：本地 Vercel CLI 登录、项目目录、构建命令和发布环境
