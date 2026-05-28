# OBE 设计参考与品味训练 — 工作流 Playbook

**用途**：把「外部参考」变成 **可检索、可对照、可验收** 的输入，提升自动化产品工作流（PRD / UX 评审 / 原型）的 **判断质量**，而非堆砌效果图。

**版本**：v1.0  
**最后更新**：2026-05-02  

**配套**：与 [OBE-product-ux-self-check.md](OBE-product-ux-self-check.md) **§11** 联动；体验产出由 `web3-product-experience-expert` 优先加载本文。

---

## 1. 误区与真相（校准自动化 Agent 与人类评审）

| 误区 | 真相 |
|------|------|
| 「品味是天生的」 | 品味是 **大量样本训练后的模式识别**；工作流里要把「样本 → 对比维度 → 结论」结构化 |
| 「要多看 Dribbble / Behance」 | 多为 **展示型作品**；真产品的约束（性能、合规、数据延迟、错误态）不同；可作 **局部视觉灵感**，不可当作交互规格 |
| 「要学会 Sketch / Figma 才有品味」 | 工具是表达手段；品味是 **判断力与取舍**，可在 PRD / 表格 / 标注里体现 |
| 「我是产品/后端，不用懂设计」 | 品味决定 **反馈质量** 与 **能否推动团队做正确取舍**；应写入评审门禁 |

---

## 2. 参考源分层（自动化时按优先级取用）

**原则**：先 **上线产品 / 真实截图库**，再 **设计系统与思维类**，最后才是 **概念稿社区**。

| 层级 | 类型 | 你提供的精选 | 自动化中的用法 |
|------|------|----------------|------------------|
| A | 真实上线产品 | Binance / OKX / dYdX 改版对比；Linear / Raycast / Vercel Dashboard | **竞品与领域基准**：`ux-audit`、`market-researcher`、PRD「竞品对照」节；需浏览器 MCP 时遵守仓库 **browser 三选一** 流程 |
| B | 真实界面样本库 | [Mobbin](https://mobbin.com/discover)（按行业/功能分类的 App 截图） | **流程与组件范式**：快速找「同类屏」；适合作为「对照样本索引」中的一条 |
| C | 社区与文件模板 | [Figma Community](https://www.figma.com/community/) | **组件/布局启发**；须标注「非业务约束来源」，避免把模板当业务规则 |
| D | 展示型社区 | [Dribbble](https://dribbble.com/) | **仅提取图案层灵感**（色彩节奏、插画风格）；必须在文档中标注 **非交互真理来源** |
| E | 设计思维与系统写法 | 《The Design of Everyday Things》（Don Norman）、《Refactoring UI》（Adam Wathan & Steve Schoger）；[Stripe 设计相关写作](https://stripe.com/blog/design) | **评审词汇与取舍框架**：写「体验验收」理由、密度与层级取舍 |

> **Stripe**：官方内容多在 [stripe.com/blog](https://stripe.com/blog)（可按 **design** 主题筛选）；与产品叙事、表单密度、渐进披露相关的文章尤其适合 B2B / 金融科技语境。

---

## 3. 写入工作流的四种「硬挂钩」（推荐）

### 3.1 PRD / 交互文档附录：`参考样本索引`（强制结构）

每张需求至少一行（可作为 **P2** 门禁，见自查清单 §11）：

| 字段 | 说明 |
|------|------|
| 样本来源 | Mobbin / 竞品构建 / Figma Community / Dribbble / 书籍章节 |
| URL 或标识 | 可点击或可检索 |
| 对照对象 | 与本需求对应的屏或流程 |
| 借鉴点 | 具体（如「空状态结构」「二级信息折叠」） |
| **不采纳点** | **约束差异**（展示稿无加载失败；我们有 WS 延迟等） |

自动化：`doc-writer` 输出 PRD 时若有界面章节，应预留该表或由 Agent 生成草稿。

### 3.2 UX 评审 / 自查时的固定问句（Agent 可执行）

在完成 [OBE-product-ux-self-check.md](OBE-product-ux-self-check.md) P0 之余，追加：

1. **上线对照**：同类 **已上线** 流程至少 1 例；结论是否写入「参考样本索引」？
2. **展示型边界**：若引用 Dribbble 等，是否写明 **仅视觉 / 不采纳的交互假设**？
3. **领域天花板**：B2B 密度与层级是否可对齐 Linear / Vercel Dashboard 一类「高密度可读」基准（不要求抄袭视觉）？

### 3.3 研究增强层（Parallel / 浏览器）

- **Parallel MCP**：适合「Stripe empty state best practices」「Mobbin checkout pattern summary」类 **事实快扫**，产出仍须经 PRD 附录索引落地。
- **浏览器 MCP**：竞品 **实时界面与文案**；触发前须完成 **browser-mcp-choice-workflow** 用户确认。

### 3.4 与流水线对齐（你已配置的 YAML）

凡含 PRD / UX / 原型的流水线已引用 `OBE-product-ux-self-check`：**§11（参考源）** 作为 **P2**，建议在 `ux-audit`、`prd-full` 人工抽检或 Agent 说明中显式勾选，避免只有规则无样本。

---

## 4. 给 Agent 的一键指令（可选粘贴）

```text
请读取 workflow/skills/product/OBE-design-reference-playbook.md，
针对「{功能/页面}」：
1) 按 Playbook §2 优先级给出 2～3 个应对照的来源类型（含至少 1 个「上线产品」或 Mobbin 同类屏）；
2) 生成 PRD 可用的「参考样本索引」表草稿（含「不采纳点」列）；
3) 指出若只用 Dribbble 类来源会漏掉哪些真实约束（加载、权限、数值精度等）。
```

---

## 修订记录

| 版本 | 日期 | 摘要 |
|------|------|------|
| v1.0 | 2026-05-02 | 首版：误区表、分层资源、与工作流 / OBE §11 挂钩 |
