# Web3 CEX 产品团队

## 📌 描述与定位

顶级 Web3 CEX 产品团队（Team Skill），作为**统一入口与协同剧本**。在现有细分职能 Skill 之上提供团队身份、显式角色表（Roster）、命名流水线（Pipeline）与交付质量门，形成团队化协同作战能力。不替代 `web3-product-expert` 与各职能 Skill，而是驱动其按团队流水线或 ad-hoc 协作执行。

**适用**：用户希望「产品团队」整体承接任务（如「产品团队来做止盈止损功能」「全流程 PRD」）时启用；单点需求（如「写个 PRD」「设计强平」）仍由 web3-product-expert-trigger 直接激活主导 Skill。

---

## 🎯 触发与入口

### 何时启用团队模式

- **触发词**：产品团队、团队来做、产品团队协作、全流程 PRD、团队承接、产品团队从 0 到 1、团队全链路
- **意图**：用户明确希望由「团队」整体交付（多角色、多步骤），而非单点专家回复。

### 与单点专家模式的区分

| 用户表达示例           | 模式     | 入口                         |
|------------------------|----------|------------------------------|
| 「产品团队来做止盈止损」 | 团队模式 | 本 Skill + 选流水线/协作      |
| 「全流程 PRD 加测试」   | 团队模式 | 本 Skill → prd-and-qa 等     |
| 「写个止盈止损的 PRD」  | 单点模式 | web3-product-expert-trigger   |
| 「设计强平逻辑」       | 单点模式 | web3-product-expert-trigger   |

命中团队触发时：加载本 Skill，并视需要同时加载 [SKILL-COLLABORATION-GUIDE.md](.codebuddy/skills/product/SKILL-COLLABORATION-GUIDE.md) 与 [web3-product-expert.md](.codebuddy/skills/product/web3-product-expert.md)。

---

## 👥 团队角色与技能映射（Roster）

| 团队角色       | 对应 Skill                               | 主要产出                         |
|----------------|------------------------------------------|----------------------------------|
| 产品负责人/架构师 | web3-product-expert                      | 方案、规则、评审、调度             |
| 需求澄清/立项判断 | web3-product-expert + market-researcher / data-analyst | 背景、用户、痛点、非目标、成功指标、立项结论 |
| 永续合约专家   | perpetual-designer                       | 合约功能与风控设计                 |
| 文档工程师     | doc-writer                               | PRD、技术/用户文档                |
| 市场/竞品研究  | market-researcher                        | 竞品分析、行业实践                 |
| 数据分析       | data-analyst                             | 指标、埋点、监控                   |
| 体验设计       | web3-product-experience-expert           | 交互与 UX 方案                    |
| 工程计划评审   | engineering-plan-review                  | 架构边界、接口/数据流、状态机、权限安全、回滚、监控与测试策略 |
| 计划联合评审   | product-lens-reviewer + web3-product-experience-expert + engineering-plan-review + product-test-qa | 战略、体验、工程可行性、测试可测性评审 |
| 设计对接       | web3-prd-figma-prompt                    | Figma 设计提示词                  |
| 测试与验收     | product-test-qa / cex-contract-testing-expert | 测试用例、UAT、可测性评估          |
| AI 功能设计    | ai-function-designer                     | AI 能力边界、Fallback、复核流程   |
| 图解/白板     | excalidraw-diagram                       | `.excalidraw` 架构图、链路图、状态机（含 PNG 自检） |
| 协同发布       | Lark Sync（lark-cli 优先）                 | Lark 文档新建/更新与回链           |

测试角色按场景选择：通用 UAT/验收用 product-test-qa；合约专项测试用例与可测性评估用 cex-contract-testing-expert（与现有 trigger 一致）。

---

## 🔀 团队级工作流（流水线）定义

**单一事实源**：流水线步骤、触发词、产出路径**以 [pipelines.yaml](.codebuddy/skills/product/pipelines.yaml) 为准**；本文件仅保留总览与执行逻辑说明，不重复维护与 YAML 相同的内容。Agent 加载本 Skill 时应优先读取 pipelines.yaml（若存在）。

### 流水线总览

| 流水线 id | 适用意图 | 对应 orchestrator 模板 |
|-----------|----------|------------------------|
| feature-discovery | 需求刚出现，先判断值不值得做、做多大、下一步进哪条流水线 | 可不走 orchestrator |
| plan-review-gauntlet | PRD/方案/原型计划进入开发或设计前的联合评审 | 可不走 orchestrator |
| prd-full | 新功能从 0 到 PRD+测试+设计对接 | web3-prd-with-translation 或扩展 |
| prd-and-qa | PRD + 测试用例与验收标准 | prd-and-qa |
| futures-feature | 合约专项（强平/保证金/资金费等）设计到测试 | futures-feature |
| ai-feature | AI 功能（智能客服/推荐/风控模型等）产品设计 | ai-feature |
| ux-audit | 现有功能 UX 评审（并行协作） | 可不走 orchestrator |
| prototype-full | 产品原型全流程（设计→测试→修订→发布→Figma） | prototype-full |

各流水线的触发关键词、输入要求、步骤与角色、产出路径见 **pipelines.yaml**；执行时按该文件或 workflow-orchestrator 中同名模板执行。

### gstack 吸收策略

gstack 的 `/office-hours`、`/autoplan`、`/qa`、`/ship` 等命令不直接照搬为 Onebullex 命令。当前团队 Skill 只吸收两类高收益模式：

- **前置判断**：通过 `feature-discovery` 把产品想法先收束为做/不做/延后/缩小范围，避免直接进入 PRD 或原型。
- **联合评审**：通过 `plan-review-gauntlet` 在进入开发、设计或原型实现前，把战略、体验、工程、测试风险一次性结构化暴露。

真实工程交付、代码审查、上线、文档同步与复盘暂不新增为独立 `delivery-full`，避免与现有 `prototype-full`、Vercel/Figma 原型链路抢触发。若后续要接入，应先补齐对应 Skill 或明确由现有 Skill fallback。

---

## ⚙️ 执行逻辑

当用户以团队入口提出需求时：

1. **选择流水线或 ad-hoc**：根据触发关键词与意图匹配上表流水线；若仍处于想法阶段，优先 `feature-discovery`；若已有 PRD/方案且准备进入设计、开发或原型实现，优先 `plan-review-gauntlet`；若无匹配则按「非标协同」处理。
2. **命名流水线**：若存在对应 workflow-orchestrator 模板，则调用 orchestrator 执行该模板并传入参数（如功能名、是否多语言、是否含测试）；若暂无模板，则按本 Skill 中该流水线的步骤与角色描述，**按步骤依次加载对应职能 Skill** 执行（先 web3-product-expert，再 doc-writer / perpetual-designer / cex-contract-testing-expert 等），不重复实现步骤逻辑。
3. **非标协同**：按 [SKILL-COLLABORATION-GUIDE](.codebuddy/skills/product/SKILL-COLLABORATION-GUIDE.md) 的串行/并行/条件协作，由 web3-product-expert 主导，调用相应职能 Skill。
4. **Lark 协同发布（可选）**：若用户要求将本地 PRD/方案同步到 Lark，执行 hybrid 流程：先匹配候选文档并确认，再执行 create/update。
5. **交付前**：执行下方「质量门」检查清单。

---

## ✅ 质量门（交付前检查清单）

**交互 / 原型 / UX 方案单一事实源**：凡产出含界面、流程、控件状态或体验文案的交付，交付前须完成 [OBE-product-ux-self-check.md](.codebuddy/skills/product/OBE-product-ux-self-check.md) 中与本次范围相关的 **全部 P0** 自检（或由 `web3-product-experience-expert` 主笔并在团队中勾选）；P1/P2 缺口记入 PRD「体验债」或迭代清单。

**视觉 Token / 组件约束**：凡产出 **Figma 提示词、交互原型、PRD 内嵌线框说明** 或与设计稿对齐的验收条目，须引用 **`产品设计/设计提示词/OBE DESIGN.md`**（及 `产品设计/需求文档（PRD）/00-规范与模板/OBE-设计规范与Figma关键页面索引.md` 中的 `fileKey` / `node-id`）；与 Figma Variables 冲突时以 Variables 为准。

团队交付前必须确认：

- [ ] **术语**：与项目/Notion 术语一致，无自造或冲突用语
- [ ] **知识源**：Notion > NotebookLM > 本地文档 > OpenViking（与现有规范一致）；引用处可追溯
- [ ] **协作说明**：产出中注明主导/协作 Skill、协作类型、输入输出（符合 SKILL-COLLABORATION-GUIDE）
- [ ] **合约相关**：若涉及强平/保证金/资金费等，公式与 Notion 或 PRD 一致，并可追溯来源
- [ ] **AI 功能**：若涉及 AI，PRD 或设计文档含能力边界、Fallback、人工复核（与 ai-function-designer 对齐）
- [ ] **体验自查（P0）**：已按 [OBE-product-ux-self-check.md](.codebuddy/skills/product/OBE-product-ux-self-check.md) 完成本节所列范围内的 P0（含 **§8 Web3 CEX 附加** 与资金路径相关交互）
- [ ] **路径与命名**：产出文件路径与命名符合 SKILL-COLLABORATION-GUIDE 第 6.3 节
- [ ] **Lark 同步（可选）**：若启用 Lark 发布，已完成 preview→确认→apply，且输出 `doc_url/doc_id/sync_mode/sync_status`
- [ ] **图解（可选）**：若交付含 Excalidraw 图解，已按 `excalidraw-diagram` Skill 完成 **Render & Validate**（PNG 自检）、文件路径在 `产品设计/需求文档（PRD）/03-原型与设计资产/diagrams/` 或协作说明中可追溯
- [ ] **图标资源（可选）**：交付含 **交互原型 / 前端示例 / PRD 线框** 时，线框默认 **[Feather Icons](https://github.com/feathericons/feather)**（**§1.1b**）；需 **中文搜图标 / 复制 SVG** 可补充 **[iconfont](https://www.iconfont.cn/)**（**§1.1c**）；详见 [web3-product-expert.md](web3-product-expert.md)

---

## 本地交互原型发布（Vercel）

当用户要求**将本地可运行的交互原型发布到线上**（供评审、同事查看）且目标为 **Vercel** 时：

1. **优先**：若当前环境已启用 **Vercel MCP**（Cursor：`plugin-vercel-vercel`，主部署工具 **`deploy_to_vercel`**），由主导 Agent（`web3-product-expert`）按 [web3-product-expert.md](web3-product-expert.md) 中「MCP 集成」约定：先读取 `mcps/plugin-vercel-vercel/tools/deploy_to_vercel.json`，再 `call_mcp_tool` 完成生产部署，并在输出中给出 **`*.vercel.app` 生产链接**（及必要时 Inspect 链接）。
2. **兜底**：无 Vercel MCP 或调用失败时，在仓库内对 **BTC 移动端原型**目录执行：
   ```bash
   cd "产品设计/需求文档（PRD）/03-原型与设计资产/用户端原型/btc-trading-mobile"
   npm run deploy:vercel
   ```
   等价 `vercel deploy --prod --yes`；需本机已 `vercel login` 且项目已 link（存在 `.vercel`，该目录已列入 `.gitignore`）。构建与输出目录由同目录下 `vercel.json` 指定（Vite / `dist`）。
3. **Monorepo**：若通过 Git 连接 Vercel 而非 CLI，在 Vercel 项目 **Root Directory** 中填写上述 **`btc-trading-mobile` 相对路径**。

详细 MCP 行为与自动触发表述见 [web3-product-expert.md](web3-product-expert.md) 中 **Vercel MCP** 小节。

---

## 本地原型页面上传到 Figma

当用户要求**将本地可运行的交互原型页面/组件截图上传到 Figma 文件**（供设计评审、留档）时：

1. **前置**：确认已启用 **Figma MCP**（`user-html.to.design`，核心工具 **`generate_figma_design`**）。若 MCP 未启用则提示用户安装后重试。
2. **标准 5 步**：
   1. **注入脚本** — 在项目 `index.html` `<body>` 末尾插入：
      ```html
      <script src="https://mcp.figma.com/mcp/html-to-design/capture.js" async></script>
      ```
   2. **锁定页面状态** — 临时修改 React `useState` 等初始值，使目标页面/弹窗在页面加载后直接渲染，**避免依赖手动导航**。
   3. **生成 captureId + 打开页面** — 调用 `generate_figma_design`（`outputMode: "existingFile"`, `fileKey`, `nodeId`）获取 `captureId`；用 Shell `open` 打开含 `figmacapture`/`figmaselector`/`figmadelay` 参数的 URL。
   4. **轮询完成** — sleep → 再次调用 `generate_figma_design({ captureId })` 检查状态；pending 则重试（最多 10 次）。
   5. **还原代码** — 恢复所有临时 state 修改、移除 capture 脚本、确认 HMR 正常。
3. **多状态捕获**：每种 UI 状态需单独的 `captureId`。如同一页面需捕获"默认态"和"弹窗展开态"，需两次走步骤 2→4。
4. **避坑**：
   - `figmaselector` 目标必须在 DOM 中存在（动态弹窗需 state 预设为 visible）
   - 不使用 `figmaselector=*`（手动选择模式）做自动化
   - capture 完成后**必须还原代码**

详细参数速查与避坑清单见 [web3-product-expert.md](web3-product-expert.md) 中 **Figma Capture** 小节。

---

## 📎 参考

- **UX / 原型自查清单（单一事实源）**：[OBE-product-ux-self-check.md](.codebuddy/skills/product/OBE-product-ux-self-check.md)
- **流水线配置**：[pipelines.yaml](.codebuddy/skills/product/pipelines.yaml)（流水线定义可在此修改，无需改本文件）
- 协作规范：[SKILL-COLLABORATION-GUIDE.md](.codebuddy/skills/product/SKILL-COLLABORATION-GUIDE.md)
- 主导 Skill：[web3-product-expert.md](.codebuddy/skills/product/web3-product-expert.md)
- 工作流编排：[workflow-orchestrator.md](.codebuddy/skills/general/workflow-orchestrator.md)（general 目录）
- 产品 Skill 分析：[product-skills-analysis-report.md](.codebuddy/skills/product/product-skills-analysis-report.md)
- **图标**：线框默认 [Feather](https://github.com/feathericons/feather) · [feathericons.com](https://feathericons.com)（**§1.1b**）；补充 [iconfont](https://www.iconfont.cn/) 中文检索与 SVG（**§1.1c**，见 web3-product-expert）

---

**版本**：v1.5  
**最后更新**：2026-05-02（质量门与参考：挂载 OBE-product-ux-self-check 体验 P0 门禁）
**维护**：Web3 产品团队
