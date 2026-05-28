# Web3 CEX 产品线 Skill

本目录为 **Web3 中心化交易所产品线** 的 Skill 与团队协同配置，覆盖产品设计、永续合约、文档、竞品、数据、UX、设计对接、测试与 AI 功能设计等职能，并提供团队化协同入口与流水线。

---

## 入口二选一

| 使用场景 | 入口 | 说明 |
|----------|------|------|
| **团队整体承接**（多角色、多步骤交付） | [web3-cex-product-team.md](web3-cex-product-team.md) + [pipelines.yaml](pipelines.yaml) | 用户说「产品团队来做」「全流程 PRD 加测试」等时加载；流水线步骤、触发词、产出路径以 pipelines.yaml 为准 |
| **单点需求**（单功能/单文档） | [web3-product-expert.md](web3-product-expert.md) | 用户说「写个 PRD」「设计强平」等时由 web3-product-expert-trigger 激活主导 Skill，按需协作职能 Skill |

---

## 职能 Skill 清单

| Skill | 职责摘要 | 文件路径 |
|-------|----------|----------|
| web3-product-expert | 产品专家 + 系统架构师；整体设计、规则、评审、协作调度 | [web3-product-expert.md](web3-product-expert.md) |
| perpetual-designer | 永续合约功能与风控设计 | [perpetual-designer.md](perpetual-designer.md) |
| doc-writer | PRD、技术/用户文档 | [doc-writer.md](doc-writer.md) |
| market-researcher | 竞品分析、行业实践 | [market-researcher.md](market-researcher.md) |
| data-analyst | 指标、埋点、监控 | [data-analyst.md](data-analyst.md) |
| engineering-plan-review | 开发前工程计划评审，覆盖架构边界、接口/数据流、状态机、权限安全、灰度回滚、监控与测试策略 | [engineering-plan-review.md](engineering-plan-review.md) |
| web3-product-experience-expert | 交互与 UX 方案 | [web3-product-experience-expert/SKILL.md](web3-product-experience-expert/SKILL.md) |
| web3-prd-figma-prompt | PRD → Figma 设计提示词 | [web3-prd-figma-prompt.md](web3-prd-figma-prompt.md) |
| product-test-qa | 测试用例与 UAT 验收（通用） | [product-test-qa.md](product-test-qa.md) |
| cex-contract-testing-expert | 合约测试用例与可测性评估（公式断言） | [cex-contract-testing-expert.md](cex-contract-testing-expert.md) |
| ai-function-designer | AI 能力边界、Fallback、复核流程 | [ai-function-designer.md](ai-function-designer.md) |

---

## 关键规范与配置

- **Figma MCP 全能力 + Cursor 插件 Skills + capture.js hash 约定（跨 IDE 对齐）**：[../../docs/FIGMA-MCP-CAPABILITIES.md](../../docs/FIGMA-MCP-CAPABILITIES.md)
- **协作流程与输出规范**：[SKILL-COLLABORATION-GUIDE.md](SKILL-COLLABORATION-GUIDE.md)（协作类型、映射表、团队模式、输出命名、术语与规范）
- **交互 / 原型体验自查（单一事实源）**：[OBE-product-ux-self-check.md](OBE-product-ux-self-check.md)（团队质量门与 `web3-product-experience-expert` 对齐）
- **设计参考与品味 Playbook**：[OBE-design-reference-playbook.md](OBE-design-reference-playbook.md)（Mobbin / Figma Community / Dribbble 边界、PRD「参考样本索引」、与 §11 P2 联动）
- **流水线配置**：[pipelines.yaml](pipelines.yaml)（feature-discovery / plan-review-gauntlet / prd-full / prd-and-qa / futures-feature / ai-feature / ux-audit / prototype-full；体验相关流水线均显式要求引用 [OBE-product-ux-self-check.md](OBE-product-ux-self-check.md)，详见各流水线 `mandatory_references` / `quality_gates`）
- **团队触发规则**：`.cursor/rules/web3-cex-product-team-trigger.mdc`
- **单点触发规则**：`.cursor/rules/web3-product-expert-trigger.mdc`
- **编排与路由**：`workflow/skills/general/workflow-orchestrator.md`（产品团队相关模板）；`universal-router` 中 web3-cex-product-team 与 entry_routing.product_team

---

## 模板与产出路径

- **PRD 模板**：[_templates/OneBullEX-PRD-Template.md](_templates/OneBullEX-PRD-Template.md)
- **输出路径与命名**：见 SKILL-COLLABORATION-GUIDE 第 6.3 节（PRD、测试用例、Figma 提示词、竞品分析、AI 功能等目录与命名规范）

---

**维护**：Web3 产品团队
