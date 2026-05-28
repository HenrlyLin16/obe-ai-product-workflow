# OBE AI 协作工作流操作手册

## 1. 使用前准备

### 本地目录

从项目根目录执行：

```bash
cd /Users/jingxing/Desktop/Onebullex
```

核心文件：

- 产品团队入口：`.codebuddy/skills/product/web3-cex-product-team.md`
- 流水线配置：`.codebuddy/skills/product/pipelines.yaml`
- 协作规范：`.codebuddy/skills/product/SKILL-COLLABORATION-GUIDE.md`
- Figma MCP 说明：`.codebuddy/docs/FIGMA-MCP-CAPABILITIES.md`
- Codex 本地接入：`.codebuddy/CODEX-LOCAL-MCP-SKILL-INTEGRATION.md`
- Lark 工具说明：`tools/lark-mcp-server/README.md`

### 同步 Skill

Cursor：

```bash
./scripts/sync-codebuddy-skills-to-cursor.sh
```

Codex：

```bash
./scripts/sync-codebuddy-skills-to-codex.sh
```

同步原则：`.codebuddy/skills` 是单一事实源，不直接编辑 `.cursor/skills` 或 `~/.codex/skills/onebullex` 的生成副本。

## 2. 产品经理工作流

### Step 1：需求澄清

推荐提示词：

```text
召唤产品专家团队，对以下想法走 feature-discovery：
[一句话需求]
请输出做/不做/延后/缩小范围判断、目标用户、成功指标、非目标、关键风险、下一步入口。
```

使用模板：`templates/需求澄清模板.md`

### Step 2：PRD + 验收标准

推荐提示词：

```text
基于上一步需求澄清结论，走 prd-and-qa：
输出 PRD 摘要、功能范围、页面状态、规则说明、验收标准和测试用例。
```

使用模板：

- `templates/PRD交付模板.md`
- `templates/开发交付验收模板.md`

### Step 3：设计衔接

推荐提示词：

```text
基于 PRD，调用 web3-prd-figma-prompt 生成 Figma Make 设计提示词。
请包含页面结构、组件状态、风险提示、空态/异常态、移动端适配要求。
```

使用模板：`templates/设计衔接模板.md`

### Step 4：联合评审

推荐提示词：

```text
召唤产品专家团队，对该 PRD/设计提示词走 plan-review-gauntlet。
请分别输出产品战略、体验设计、工程计划、测试验收评审结论，并给出 pass / conditional_pass / fail。
```

## 3. 设计师工作流

设计师重点读取：

- PRD 中的目标用户、场景、范围、非目标
- 设计提示词中的页面结构、组件状态、风险提示
- 联合评审中的体验设计问题和 OBE P0 自查项

Figma 衔接方式：

- 低保真 / 高保真设计：用 Figma Make 提示词作为设计起点。
- 页面捕获：本地原型可通过 Figma html-to-design capture 导入。
- 设计稿回写：将 Figma 文件/节点链接回写到 Lark 主文档。

## 4. 开发交付工作流

开发接手前至少应具备：

- PRD：功能范围、规则说明、页面状态、异常场景
- 设计稿：Figma 文件/节点链接
- 验收：测试用例、UAT 标准、联合评审结论

工程评审使用 `engineering-plan-review`，重点检查：

- 架构边界
- API / 数据流
- 状态机
- 权限、安全、风控
- 灰度、回滚、监控、测试策略

## 5. Lark 归档

推荐 Lark 主文档结构：

```text
1. 背景与目标
2. 需求澄清结论
3. PRD 摘要
4. Figma / 设计稿链接
5. 验收标准与测试用例
6. 联合评审结论
7. 下一步任务
8. 变更记录
```

可用工具：

- `lark_search_docs`
- `lark_get_doc`
- `lark_create_doc`
- `lark_append_doc`
- `lark_send_message`
- `lark_create_task`

本地 CLI：

```bash
lark-cli docs +search --query "关键词" --page-size 5
lark-cli docs +create --title "文档标题" --markdown @path/to/file.md
lark-cli docs +update --doc "doc_url_or_token" --mode append --markdown @path/to/file.md
```

## 6. 自定义方式

PM 最少只需要替换 5 项：

1. `feature_name`
2. 目标用户 / 场景
3. 目标端：Web / H5 / App / Admin
4. Figma 文件或页面
5. Lark 归档空间或目标文档

产品负责人可以进一步自定义：

- `pipelines.yaml` 中的触发词
- 每条流水线的协作 Skill
- 输出路径
- 质量门
- Lark 归档规则

## 7. 常见失败与回退

- Lark 创建失败：先检查 `lark-cli auth status`，必要时重新登录。
- Figma MCP 不可用：用设计提示词先交给设计师手动进入 Figma Make。
- Capture pending：检查 URL hash 是否以 `#figmacapture=` 开头。
- Codex 找不到新 Skill：运行 `./scripts/sync-codebuddy-skills-to-codex.sh` 后重启 Codex。
- Cursor 找不到新 Skill：运行 `./scripts/sync-codebuddy-skills-to-cursor.sh`。
