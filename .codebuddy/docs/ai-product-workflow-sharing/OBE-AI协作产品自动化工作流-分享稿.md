# OBE 产品部门 AI 协作产品自动化工作流

版本：v1.0  
分享对象：OBE 产品部门（产品经理、设计师、产品负责人）  
主入口：Lark 文档；本地源文件：`.codebuddy/docs/ai-product-workflow-sharing/`  
Demo 沙盒功能：合约交易页价格提醒提醒方式优化

## 1. 为什么要做

我们这次不是分享“怎么问 AI”，而是分享一套可以被产品部门复用的协作工作流。目标有两个：

1. **提升本职能效率**：产品经理可以把从想法到 PRD、测试用例、评审结论的重复劳动标准化；设计师可以从清晰的 PRD、设计提示词和验收边界开始工作；产品负责人可以把团队经验沉淀成可复制的流水线。
2. **提升跨职能协作效率**：产品、设计、测试、开发之间不再靠零散聊天接力，而是用统一产物承接：需求文档、Figma/设计稿链接、验收标准/测试用例、联合评审结论、Lark 归档记录。

当前本地已经具备底座：`.codebuddy/skills/product/pipelines.yaml` 里有产品团队流水线，`.codebuddy/skills/product/web3-cex-product-team.md` 是团队入口，Figma/Codex/Cursor/Lark 的连接方式已有文档。我们要做的是把这些能力包装成部门能用的“工作流包”。

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

这条链路的关键不是“每一步都自动生成完美答案”，而是每一步都形成可追溯的输入、输出、负责人和下一步。

## 3. 三类角色怎么用

### 产品经理

- 用 `feature-discovery` 把模糊想法先判断清楚：做不做、为什么做、做多大、先做哪个切口。
- 用 `prd-full` 或 `prd-and-qa` 生成 PRD、验收标准和测试用例。
- 用 Lark 作为最终协作入口，把 PRD、设计链接、评审报告和任务沉淀到同一个页面。

### 设计师

- 从 PRD 和 `web3-prd-figma-prompt` 获得设计目标、页面状态、组件约束、风险提示和验收边界。
- 通过 Figma MCP / Figma Capture 把可运行原型或页面状态导入 Figma，减少手动复刻成本。
- 在 `plan-review-gauntlet` 中参与体验设计评审，提前暴露状态、空态、异常态、风险提示不足等问题。

### 产品负责人

- 维护团队流水线，不让每个 PM 都从零设计 AI 协作方式。
- 根据业务线自定义触发词、模板、质量门和归档路径。
- 用联合评审和 Lark 归档保证跨职能交付可追溯。

## 4. 现场 Demo：沙盒功能端到端跑通

Demo 功能：**合约交易页价格提醒提醒方式优化**

一句话输入：

> 用户在合约交易页设置价格提醒时，希望能选择站内通知、邮件、Push 三种提醒方式，并能在触发前确认风险提示，避免错过关键价格或误以为系统会自动下单。

Demo 链路：

1. 需求澄清：判断是否值得做、目标用户是谁、成功指标是什么。
2. PRD + 验收：产出功能范围、页面状态、规则说明、测试用例。
3. 设计衔接：生成 Figma Make 提示词，明确页面结构、组件状态、风险提示。
4. 联合评审：产品、体验、工程、测试分别给出 pass / conditional_pass / fail。
5. Lark 归档：把上述产物汇总成部门可复用文档。

## 5. 落地规范

### 文件与命名

- 本地源文件：`.codebuddy/docs/ai-product-workflow-sharing/`
- PRD：`产品设计/需求文档（PRD）/OBE-{feature_name}-产品需求文档.md`
- 测试用例：`产品设计/测试用例/OBE-{feature_name}-测试用例与验收标准.md`
- 设计提示词：`产品设计/设计提示词/OBE-{feature_name}-Figma设计提示词.md`
- 联合评审：`产品设计/需求文档（PRD）/03-原型与设计资产/workflow/reports/OBE-{feature_name}-联合评审报告.md`

### Lark 归档

每个功能至少沉淀：

- 需求背景与范围
- PRD 链接或正文
- Figma/设计稿链接
- 验收标准/测试用例
- 联合评审结论
- 下一步任务和 owner

### Figma 衔接

- PRD 完成后生成 Figma Make/设计提示词。
- 需要把运行页面导入 Figma 时，使用 html-to-design capture。
- Capture URL 的 hash 必须以 `#figmacapture=` 开头，避免捕获 pending。

### Codex / Cursor 使用

- `.codebuddy/skills` 是团队 Skill 的单一事实源。
- Cursor 同步：`./scripts/sync-codebuddy-skills-to-cursor.sh`
- Codex 同步：`./scripts/sync-codebuddy-skills-to-codex.sh`
- 新增或修改 Skill 后，先改 `.codebuddy/skills`，再同步到 Cursor/Codex。

### 安全

- 分享材料只出现脱敏配置，不展示真实 Token、API Key、Secret。
- 示例配置使用 `${FIGMA_OAUTH_TOKEN}`、`${NOTION_TOKEN}`、`${LARK_APP_SECRET}` 这类环境变量占位。
- 如果密钥曾出现在共享文件或截图里，应在分享前轮换。

## 6. 会后推广方式

1. 先让 1-2 个 PM 用沙盒模板跑一个真实但低风险的需求。
2. 设计师补充 Figma 页面结构和组件命名偏好。
3. 产品负责人固化团队模板和 Lark 归档路径。
4. 一周后复盘：节省了哪些重复劳动，哪些环节仍需要人工判断，哪些 Skill 需要优化。
