# 新手从这里开始

这份文档给第一次使用 OBE AI 产品工作流的同事。你不需要先理解 MCP、YAML 或 Skill 内部结构，先跑通一个可用结果即可。

## 1. 先选你的角色

| 你的角色 | 先用哪个工作流 | 目标 |
|----------|----------------|------|
| 产品经理 | `feature-discovery` -> `prd-and-qa` | 把想法变成 PRD 和验收标准 |
| 设计师 | `web3-prd-figma-prompt` | 把 PRD 变成 Figma 设计输入 |
| 产品负责人 | `plan-review-gauntlet` | 让产品、体验、工程、测试一起评审风险 |
| 新同事 | 下面的 Demo 提示词 | 15 分钟确认工作流能跑通 |

## 2. 第一次安装

```bash
git clone https://github.com/HenrlyLin16/obe-ai-product-workflow.git
cd obe-ai-product-workflow
cp workflow/docs/ai-product-workflow-sharing/config/ai-api.env.example .env.local
bash workflow/docs/ai-product-workflow-sharing/scripts/install-local-workflow.sh
```

打开 `.env.local`，只替换这两个值：

```bash
ANTHROPIC_BASE_URL="https://ai.1bullex.com/api"
ANTHROPIC_AUTH_TOKEN="示例 Token"
```

真实 Token 只保存在本地，不提交到 Git。

## 3. 第一个 15 分钟 Demo

把下面内容复制到 Codex 或 Cursor：

```text
召唤产品专家团队，对以下想法走 feature-discovery：
用户在合约交易页设置价格提醒时，希望能选择站内通知、邮件、Push 三种提醒方式，并能在触发前确认风险提示，避免错过关键价格或误以为系统会自动下单。

请输出：做/不做/延后/缩小范围判断、目标用户、成功指标、非目标、关键风险、下一步入口。
```

你应该得到：

- 一个清晰结论，例如 `narrow_scope`。
- 目标用户和使用场景。
- 成功指标、非目标和关键风险。
- 下一步建议，例如进入 `prd-and-qa`。

## 4. 新手先掌握这三条

| 工作流 | 适用场景 | 可复制提示词 |
|--------|----------|--------------|
| `feature-discovery` | 想法还模糊 | `召唤产品专家团队，对以下想法走 feature-discovery：...` |
| `prd-and-qa` | 需要 PRD 和测试用例 | `基于上一步结论，走 prd-and-qa：...` |
| `plan-review-gauntlet` | 需要多角色评审 | `对该 PRD/方案走 plan-review-gauntlet：...` |

这三条已经覆盖大部分产品经理日常工作。

## 5. Lark / Figma / Vercel 先不要急着自动化

建议顺序：

1. 手动复制 AI 输出到 Lark、Figma Make 或原型发布记录。
2. 确认这些输出真的能节省你的工作时间。
3. 再一次只配置一个进阶工具，避免同时排查多个权限问题。

需要改的文件和参数：

| 工具 | 修改文件 | 参数 |
|------|----------|------|
| AI API | `.env.local`，来源 `workflow/docs/ai-product-workflow-sharing/config/ai-api.env.example` | `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN` |
| Lark | `.env.local`，来源 `workflow/docs/ai-product-workflow-sharing/config/lark.env.example` | `LARK_APP_ID`, `LARK_APP_SECRET`, `LARK_WRITE_DRY_RUN` |
| Figma | `.env.local` + Codex/Cursor MCP 配置 | `FIGMA_OAUTH_TOKEN` 或 `FIGMA_API_KEY` |
| Codex MCP | `~/.codex/config.toml` | 从 `config/codex-local-integrations.example.toml` 复制需要的 server 段 |
| Vercel | 本地 shell 或 Vercel CLI | 项目目录、构建命令、preview/production |

## 6. 下一步阅读

- 任务食谱：`workflow/docs/ai-product-workflow-sharing/docs/beginner-recipes.md`
- 命令速查：`workflow/docs/ai-product-workflow-sharing/docs/command-cheatsheet.md`
- Lark 主文档：`workflow/docs/ai-product-workflow-sharing/OBE-AI协作产品自动化工作流-Lark主文档.md`
