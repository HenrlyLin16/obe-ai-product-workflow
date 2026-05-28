# Start Here: OBE AI Product Workflow For Beginners

This guide is for teammates who want useful output quickly without understanding MCP, YAML, or Skill internals first.

## 1. Pick Your Role

| I am... | Start with | Goal |
|---------|------------|------|
| Product manager | `feature-discovery` -> `prd-and-qa` | Turn an idea into PRD and acceptance criteria |
| Designer | `web3-prd-figma-prompt` | Turn PRD into Figma-ready design input |
| Product lead | `plan-review-gauntlet` | Review product, UX, engineering, and QA risks |
| New teammate | Demo prompt below | Prove the workflow works in 15 minutes |

## 2. First-Time Setup

```bash
git clone https://github.com/HenrlyLin16/obe-ai-product-workflow.git
cd obe-ai-product-workflow
cp .codebuddy/docs/ai-product-workflow-sharing/config/ai-api.env.example .env.local
bash .codebuddy/docs/ai-product-workflow-sharing/scripts/install-local-workflow.sh
```

Open `.env.local` and replace only these values:

```bash
ANTHROPIC_BASE_URL="https://ai.1bullex.com/api"
ANTHROPIC_AUTH_TOKEN="示例 Token"
```

Keep real tokens local. Do not commit `.env.local`.

## 3. Your First 15-Minute Demo

Copy this into Codex or Cursor:

```text
召唤产品专家团队，对以下想法走 feature-discovery：
用户在合约交易页设置价格提醒时，希望能选择站内通知、邮件、Push 三种提醒方式，并能在触发前确认风险提示，避免错过关键价格或误以为系统会自动下单。

请输出：做/不做/延后/缩小范围判断、目标用户、成功指标、非目标、关键风险、下一步入口。
```

Expected output:

- A clear decision such as `narrow_scope`.
- Target users and scenarios.
- Success metrics and non-goals.
- Risks and next workflow recommendation.

## 4. The Three Beginner Workflows

| Workflow | Use when | Copy prompt |
|----------|----------|-------------|
| `feature-discovery` | The idea is still vague | `召唤产品专家团队，对以下想法走 feature-discovery：...` |
| `prd-and-qa` | You need PRD and test cases | `基于上一步结论，走 prd-and-qa：...` |
| `plan-review-gauntlet` | You need cross-role review | `对该 PRD/方案走 plan-review-gauntlet：...` |

Learn these three first. They already cover most PM work.

## 5. Advanced Integrations Come Later

Lark, Figma, and Vercel are advanced capabilities. Use this order:

1. Manual first: copy AI output into Lark, Figma Make, or a prototype issue manually.
2. Configure local parameters only after the manual flow feels useful.
3. Turn on MCP/CLI automation one integration at a time.

Where to edit parameters:

| Integration | File to copy/edit | Parameters |
|-------------|-------------------|------------|
| AI API | `.env.local` from `config/ai-api.env.example` | `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN` |
| Lark | `.env.local` from `config/lark.env.example` | `LARK_APP_ID`, `LARK_APP_SECRET`, `LARK_WRITE_DRY_RUN` |
| Figma | `.env.local` from `config/lark.env.example` | `FIGMA_OAUTH_TOKEN` or `FIGMA_API_KEY` |
| Codex MCP | `~/.codex/config.toml` using `config/codex-local-integrations.example.toml` | MCP server sections and env var names |
| Vercel | local shell or Vercel CLI login | `VERCEL_TOKEN` only if your local Vercel workflow requires it |

## 6. Next Reading

- Beginner recipes: `.codebuddy/docs/ai-product-workflow-sharing/docs/beginner-recipes.md`
- Command cheatsheet: `.codebuddy/docs/ai-product-workflow-sharing/docs/command-cheatsheet.md`
- Lark-ready master doc: `.codebuddy/docs/ai-product-workflow-sharing/OBE-AI协作产品自动化工作流-Lark主文档.md`
