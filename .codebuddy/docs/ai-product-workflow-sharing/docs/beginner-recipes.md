# Beginner Recipes

Use these recipes as copy/paste starting points. Do not configure Lark, Figma, or Vercel on day one unless you already know those tools.

## Recipe 1: One Idea -> Product Decision

Use when: the request is vague and you need to decide whether to do it.

```text
召唤产品专家团队，对以下想法走 feature-discovery：
[粘贴一句话需求]

请输出做/不做/延后/缩小范围判断、目标用户、成功指标、非目标、关键风险、下一步入口。
```

Expected output: decision, target user, success metrics, non-goals, risks, next workflow.

Next step: copy the result into Lark manually, or continue with Recipe 2.

Common failure: output is too broad. Add constraints such as target platform, release scope, and known non-goals.

## Recipe 2: Product Decision -> PRD + QA

Use when: you have a decision and need delivery-ready content.

```text
基于以下需求澄清结论，走 prd-and-qa：
[粘贴 feature-discovery 结果]

请输出 PRD 摘要、功能范围、页面状态、业务规则、验收标准和测试用例。
```

Expected output: PRD outline, states, rules, acceptance criteria, test cases.

Next step: paste into `templates/PRD交付模板.md` and `templates/开发交付验收模板.md`, then copy to Lark.

Common failure: missing edge cases. Ask for empty state, error state, permission failure, retry, and rollback cases.

## Recipe 3: PRD -> Figma Design Prompt

Use when: the PM needs to hand structured input to a designer.

```text
基于以下 PRD，调用 web3-prd-figma-prompt 生成 Figma Make 设计提示词：
[粘贴 PRD]

请包含页面结构、组件状态、风险提示、空态/异常态、移动端适配要求。
```

Expected output: Figma Make-ready prompt and design state checklist.

Beginner mode: copy the prompt manually into Figma Make or send it to the designer.

Advanced mode: configure Figma MCP later using `FIGMA_OAUTH_TOKEN` or `FIGMA_API_KEY`.

Common failure: prompt is too generic. Add target device, target page, key components, and design constraints.

## Recipe 4: PRD / Prototype Plan -> Cross-Role Review

Use when: a requirement is about to enter design or engineering.

```text
召唤产品专家团队，对以下 PRD/方案走 plan-review-gauntlet：
[粘贴 PRD 或方案]

请分别输出产品战略、体验设计、工程计划、测试验收评审结论，并给出 pass / conditional_pass / fail。
```

Expected output: review conclusion, blocking issues, owners, next actions.

Next step: paste review results into Lark and assign follow-up tasks manually.

Common failure: the review asks many questions. Treat them as required clarification before engineering starts.

## Recipe 5: Local Prototype -> Online Prototype

Use when: a prototype already runs locally and teammates need a URL.

```text
产品团队把当前本地原型整理为可评审的在线原型。
请先检查当前项目运行方式和页面入口，输出发布前检查清单；确认后再走 prototype-full 的 Vercel 发布步骤。
```

Beginner mode: ask the agent for a checklist and run deployment manually.

Advanced mode: configure Vercel CLI or MCP later, then let the workflow publish and return the URL.

Common failure: wrong project root. Confirm the local prototype directory and build command first.

## Recipe 6: Local Page / Component -> Figma

Use when: a running page or component needs to be captured for design review.

```text
产品团队把当前本地原型页面整理为可上传 Figma 的设计素材。
请先输出页面 URL、目标状态、需要捕获的组件、Figma 目标文件/页面参数清单；确认后再执行 Figma 上传。
```

Beginner mode: capture screenshots or copy the generated Figma prompt manually.

Advanced mode: configure Figma MCP later and ensure capture URL hash starts with `#figmacapture=`.

Common failure: capture stays pending. Check the capture URL hash order and use real Chrome instead of an embedded preview browser.
