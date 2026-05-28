# OBE 产品部门 AI 协作产品自动化工作流

> 本文档是 OBE 产品部门 AI 协作工作流的主入口。适用对象：产品经理、设计师、产品负责人。  
> 本地源文件：`workflow/docs/ai-product-workflow-sharing/`  
> Demo 沙盒功能：合约交易页价格提醒提醒方式优化。


## 0. 新手先看这 5 步

第一次使用不要先配置 Lark、Figma、Vercel 自动化。先手动复制结果，确认这套工作流能节省你的 PRD、评审和验收时间。

1. 打开 GitHub 仓库，先读 `START_HERE.md`。
2. 按 README 安装本地 Skill，并在 `.env.local` 配置 `ANTHROPIC_BASE_URL` 与 `ANTHROPIC_AUTH_TOKEN`。
3. 在 Codex 或 Cursor 复制“第一次使用推荐输入”，先跑 `feature-discovery`。
4. 将输出结果手动复制到 Lark，作为团队协作初稿。
5. 熟悉后再按需配置 Lark/Figma/Vercel 的 MCP 或 CLI 自动同步。

### 第一次使用推荐输入

```text
召唤产品专家团队，对以下想法走 feature-discovery：
用户在合约交易页设置价格提醒时，希望能选择站内通知、邮件、Push 三种提醒方式，并能在触发前确认风险提示，避免错过关键价格或误以为系统会自动下单。

请输出做/不做/延后/缩小范围判断、目标用户、成功指标、非目标、关键风险、下一步入口。
```

预期结果：先得到一个可讨论的需求澄清结论，而不是一次性追求完整自动化。

### 从 GitHub 文件到 Lark 协作

- GitHub 存放：模板、Skill、工作流、示例配置和操作说明。
- Codex/Cursor 执行：读取 Skill 与提示词，生成 PRD、验收、设计提示词和评审结论。
- Lark 沉淀：把确认后的输出复制或同步到团队文档，作为项目协作入口。
- Figma/Vercel 进阶：先手动使用设计提示词和本地原型，熟悉后再自动上传或发布。

### 指定文件参数怎么改

| 场景 | 修改文件 | 参数 | 建议 |
|------|----------|------|------|
| 接入 OBE AI API | `.env.local`，从 `config/ai-api.env.example` 复制 | `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN` | 必配；真实 Token 不进 Git |
| Lark 自动同步 | `.env.local`，从 `config/lark.env.example` 复制 | `LARK_APP_ID`, `LARK_APP_SECRET`, `LARK_WRITE_DRY_RUN` | 进阶；先保持 dry-run |
| Figma MCP | `.env.local` + Codex/Cursor MCP 配置 | `FIGMA_OAUTH_TOKEN` 或 `FIGMA_API_KEY` | 进阶；先手动复制提示词到 Figma Make |
| Codex MCP | `~/.codex/config.toml` | `[mcp_servers.*]` | 只复制自己要用的 server 段 |
| 自定义工作流 | `workflow/skills/product/pipelines.yaml` | `trigger_keywords`, `steps`, `quality_gates` | 产品负责人维护，初学者不要先改 |

## 1. 这套工作流解决什么问题

产品与设计、开发协作中常见问题：

- 需求从聊天开始，最后也散落在聊天里。
- PRD、设计稿、测试用例、评审结论之间没有统一入口。
- 不同 PM 的 AI 使用方式不可复用，质量不稳定。
- 设计师拿到的是“功能描述”，不是清晰的状态、组件和风险边界。
- 开发拿到的是“需求 + 设计”，但缺少验收标准和工程风险前置评审。

这套工作流的目标：

- 产品经理：更快完成需求澄清、PRD、验收标准。
- 设计师：更早拿到设计提示词、状态清单、风险提示和 Figma 衔接方式。
- 开发：接收 PRD + Figma/设计稿链接 + 验收标准/测试用例 + 联合评审结论。
- 团队：把 Lark 作为主入口，把 Codex/Cursor/Figma 作为执行与协作工具。

## 2. 工作流全景

```text
一句产品想法
  ↓
feature-discovery：需求澄清与立项判断
  ↓
prd-full / prd-and-qa：PRD + 验收标准/测试用例
  ↓
web3-prd-figma-prompt：设计提示词 / Figma Make 输入
  ↓
plan-review-gauntlet：产品 + 设计 + 工程 + 测试联合评审
  ↓
prototype-full：原型 / Vercel / Figma Capture（需要时）
  ↓
Lark 归档：主文档、设计链接、验收证据、任务跟进
```

## 3. 三类角色如何使用

### 产品经理

1. 用 `feature-discovery` 判断想法是否值得做。
2. 用 `prd-full` 或 `prd-and-qa` 输出 PRD 与验收标准。
3. 用 `web3-prd-figma-prompt` 给设计师生成设计输入。
4. 用 `plan-review-gauntlet` 做进入设计/开发前的联合评审。
5. 把最终交付归档到 Lark。

### 设计师

1. 从 PRD 获取业务目标、用户场景、范围和非目标。
2. 从设计提示词获取页面结构、组件状态、风险提示和异常态。
3. 在 Figma 中产出设计稿或基于 Figma Make 快速起稿。
4. 把 Figma 文件/节点链接回写到 Lark。

### 产品负责人

1. 维护团队流水线与质量门。
2. 根据业务线定制模板、触发词和归档路径。
3. 复盘哪些环节真正节省了协作成本。

## 4. Demo：合约价格提醒提醒方式优化

一句话需求：

> 用户在合约交易页设置价格提醒时，希望能选择站内通知、邮件、Push 三种提醒方式，并能在触发前确认风险提示，避免错过关键价格或误以为系统会自动下单。

Demo 路径：

1. `feature-discovery`：输出 `narrow_scope`，本期先做站内通知 + Push。
2. `prd-and-qa`：输出 PRD 摘要、页面状态、业务规则、验收标准与测试用例。
3. `web3-prd-figma-prompt`：输出设计提示词，给设计师进入 Figma。
4. `plan-review-gauntlet`：输出产品、体验、工程、测试的评审结论。
5. Lark 归档：汇总 PRD、设计链接占位、验收用例和下一步任务。

## 5. 可复用模板

本地模板路径：

- `workflow/docs/ai-product-workflow-sharing/templates/需求澄清模板.md`
- `workflow/docs/ai-product-workflow-sharing/templates/PRD交付模板.md`
- `workflow/docs/ai-product-workflow-sharing/templates/设计衔接模板.md`
- `workflow/docs/ai-product-workflow-sharing/templates/开发交付验收模板.md`

PM 使用时最少只改 5 项：

1. 功能名
2. 目标用户和场景
3. 目标端：Web / H5 / App / Admin
4. Figma 文件或页面
5. Lark 归档空间或目标文档

## 6. 工具打通方式

> 初学者原则：Lark、Figma、Vercel 都先手动复制结果；当你确认每一步产出有用后，再开启 MCP/CLI 自动同步。


### Codex / Cursor

- `workflow/skills` 是 Skill 单一事实源。
- Cursor 同步：`./scripts/sync-workflow-skills-to-cursor.sh`
- Codex 同步：`./scripts/sync-workflow-skills-to-codex.sh`

### Figma

初学者：先用 `web3-prd-figma-prompt` 生成设计提示词，手动复制给设计师或 Figma Make。

进阶：再配置 Figma MCP。

- 参数位置：`.env.local` 中的 `FIGMA_OAUTH_TOKEN` 或 `FIGMA_API_KEY`。
- Codex 配置：复制 `config/codex-local-integrations.example.toml` 中 `[mcp_servers.figma]` 段到 `~/.codex/config.toml`。
- 本地页面导入 Figma：html-to-design capture。
- 注意：capture URL 的 hash 必须以 `#figmacapture=` 开头。

### Lark

初学者：先手动复制 Codex/Cursor 输出到 Lark 主文档。

进阶：再配置 CLI/MCP 自动同步。

参数位置：`.env.local` 中的 `LARK_APP_ID`、`LARK_APP_SECRET`、`LARK_WRITE_DRY_RUN`。首次联调建议保持 `LARK_WRITE_DRY_RUN=true`。

可用工具：

- `lark_search_docs`
- `lark_get_doc`
- `lark_create_doc`
- `lark_append_doc`
- `lark_send_message`
- `lark_create_task`

本地 CLI 示例：

```bash
lark-cli docs +search --query "OBE AI 协作"
lark-cli docs +create --title "OBE 产品部门 AI 协作产品自动化工作流" --markdown @workflow/docs/ai-product-workflow-sharing/OBE-AI协作产品自动化工作流-Lark主文档.md
```

## 7. 安全与权限

- 不在分享材料中展示真实 Token、API Key、Secret。
- 示例配置统一使用环境变量占位：`${FIGMA_OAUTH_TOKEN}`、`${NOTION_TOKEN}`、`${LARK_APP_SECRET}`。
- 若密钥曾出现在共享文件、截图或群聊中，应在分享前轮换。
- Lark 写操作建议先 dry-run，再正式写入。

## 8. 会后落地

第一周：

- 选 1-2 个低风险需求用模板跑一遍。
- 设计师补充 Figma 页面结构偏好。
- 产品负责人确认 Lark 归档路径。

第二周：

- 把有效模板固化到团队规范。
- 补充失败案例和回退策略。
- 评估是否需要新增 `requirement-intake`、`code-review-gate`、`release-manager` 等后续 Skill。

## 9. 相关本地文件

- 分享稿：`workflow/docs/ai-product-workflow-sharing/OBE-AI协作产品自动化工作流-分享稿.md`
- 操作手册：`workflow/docs/ai-product-workflow-sharing/OBE-AI协作工作流-操作手册.md`
- Demo 脚本：`workflow/docs/ai-product-workflow-sharing/OBE-AI协作工作流-Demo脚本.md`
- Demo 归档示例：`workflow/docs/ai-product-workflow-sharing/demo-outputs/沙盒功能-Lark归档示例.md`
