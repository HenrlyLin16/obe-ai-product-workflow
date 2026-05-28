---
name: engineering-plan-review
description: 开发前工程计划评审 Skill。用于 Web3 CEX 产品方案、PRD、原型计划进入设计或研发实现前，评审架构边界、接口与数据流、状态机、权限安全、灰度回滚、监控和测试策略；在 plan-review-gauntlet 中替代 superpowers fallback。
---

# Engineering Plan Review

## 📌 描述

Web3 CEX 产品方案进入设计、原型实现或研发实现前的**工程计划评审** Skill。它不负责编码实现，而是从工程视角检查方案是否具备可实现、可集成、可测试、可回滚、可观测的条件，并输出阻断项与下一步工程待确认问题。

## 🎯 适用场景

- `plan-review-gauntlet` 中的工程计划评审环节
- PRD、方案、原型计划准备进入开发或设计实现前
- 需要评审接口契约、数据流、状态机、权限、错误码、依赖、回滚、监控、测试策略
- 用户明确说“工程评审”“开发前工程评审”“架构边界”“接口数据流评审”“上线风险评审”

## 边界

- 不直接写业务代码，不替代 `frontend-implementation` / `backend-api-contract` / 研发团队。
- 不替代 `product-test-qa`；这里只评审测试策略是否充分，具体用例由测试 Skill 输出。
- 不替代 `cex-contract-testing-expert`；涉及保证金、强平、资金费、风险档位等合约规则时，必须把规则断言交给合约测试专家。
- 若输入只有早期想法，先建议回到 `feature-discovery` 或补齐方案后再评审。

## 输入要求

至少需要以下任意一种材料：

- PRD / 产品方案路径
- 原型执行计划路径
- Figma / 交互说明 / 用户路径
- API / 数据结构 / 状态机 / 权限说明
- 目标端、影响范围、上线目标或发布环境

若材料不足，先输出“工程待补充问题”，不要假设接口、数据表、发布链路已经存在。

## 评审维度

### 1. 架构边界

- 前端、后端、客户端、风控、行情、撮合、资产、通知、运营后台等边界是否清晰
- 是否说明新增模块、复用模块、改动模块
- 是否存在跨系统强耦合或隐藏依赖
- 是否明确 owner 和协作方

### 2. 接口与数据流

- 是否列出关键 API、字段、状态、错误码、幂等规则
- 是否说明读取、写入、缓存、轮询、推送、延迟与失败重试
- 是否明确数据来源和最终一致性要求
- 是否存在前端临时推断核心业务规则的风险

### 3. 状态机与异常路径

- 是否覆盖加载、空态、错误态、部分成功、超时、重复提交、撤销/回退
- 交易或资金路径是否覆盖不可逆确认、二次确认、风险提示、延迟提示
- 是否有状态转换表或可测试的状态说明

### 4. 权限、安全与风控

- 是否说明登录态、KYC、权限、地域、风控拦截、风控降级
- 是否涉及敏感信息、密钥、日志脱敏、审计记录
- 是否存在越权、重放、重复提交、参数篡改、前端绕过等风险

### 5. 测试、灰度、回滚与监控

- 是否能被自动化测试、UAT、回归测试覆盖
- 是否需要 feature flag、灰度、白名单、回滚开关
- 是否定义关键监控指标、告警、日志、埋点
- 是否有发布后验证路径和失败处理方式

## 输出格式

```markdown
# [功能名称] 工程计划评审

## 1. 结论
- result: pass | conditional_pass | fail
- owner_skill: engineering-plan-review
- evidence_path: [输入文档或评审报告路径]
- allowed_next_pipeline: [prd-full | prototype-full | delivery-full | none]

## 2. 工程范围
- 目标端:
- 涉及系统:
- 主要改动:
- 依赖方:

## 3. 评审结果
| 维度 | 结论 | 关键发现 | 阻断项 | required_next_action |
|---|---|---|---|---|
| 架构边界 | pass/conditional/fail |  |  |  |
| 接口与数据流 | pass/conditional/fail |  |  |  |
| 状态机与异常路径 | pass/conditional/fail |  |  |  |
| 权限、安全与风控 | pass/conditional/fail |  |  |  |
| 测试、灰度、回滚与监控 | pass/conditional/fail |  |  |  |

## 4. 阻断问题
- [P0] ...

## 5. 工程待确认问题
- ...

## 6. 与其他 Skill 的交接
- product-test-qa:
- cex-contract-testing-expert:
- web3-product-experience-expert:
- web3-product-expert:
```

## 判定规则

- `pass`：关键接口/数据流/状态/权限/测试/回滚/监控均足够清晰，可进入下一阶段。
- `conditional_pass`：存在待确认问题，但不阻断限定范围内的下一阶段；必须写清允许推进的范围与不可越界项。
- `fail`：存在 P0 阻断项，例如核心接口不清、状态机缺失、资金/交易风险无回滚或验证路径、权限/风控边界不明。

## plan-review-gauntlet 使用方式

在 `plan-review-gauntlet` 中，本 Skill 负责“工程计划评审”维度，并输出结构化证据字段：

- `owner_skill: engineering-plan-review`
- `review_dimension: engineering_plan`
- `result: pass | conditional_pass | fail`
- `evidence_path`
- `blocking_issues`
- `required_next_action`
- `allowed_next_pipeline`

若涉及真实研发实现，可在结论中建议后续进入工程执行纪律或 TDD 流程；但默认不触发 `superpowers`。
