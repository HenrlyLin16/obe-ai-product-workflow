# Cursor 执行计划：创建 Public GitHub 仓库并上传工作流包

## 目标

在 GitHub 账号 `HenrlyLin16` 下创建一个公开仓库，把当前本地 OBE AI 协作产品自动化工作流包作为 Public 模板包上传到 Git，供使用者通过 Codex / Cursor 拉取后在本地安装和自定义。

推荐仓库名：

```text
obe-ai-product-workflow
```

最终公开访问地址：

```text
https://github.com/HenrlyLin16/obe-ai-product-workflow
```

## 当前本地状态

执行目录：

```bash
cd <repo-root>
```

当前 Git 状态以执行时为准：

```bash
git status --short
git branch --show-current
git log --oneline -1
git ls-files | wc -l
```

当前仓库通过 `.gitignore` 只放行可分发文件，避免上传完整业务工作区。Public 发布前必须清理私有链接、个人路径、邮箱、私有知识源 / NotebookLM URL 与真实密钥。

## 上传内容范围

本次只上传已跟踪且通过 Public 检查的文件：

```bash
git ls-files
```

核心内容包括：

```text
workflow/docs/ai-product-workflow-sharing/
workflow/skills/product/
scripts/sync-workflow-skills-to-cursor.sh
scripts/sync-workflow-skills-to-codex.sh
```

本执行计划文件可作为发布检查说明提交到仓库。如果只希望保留为本地执行记录，执行 `git add` 时不要包含本文件。

不要执行：

```bash
git add .
```

也不要解除 `.gitignore` 后上传整个工作区。

## 执行前安全检查

在 Cursor 终端执行：

```bash
cd <repo-root>

git status --short
git branch --show-current
git log --oneline -1
git ls-files | wc -l
```

期望结果：

```text
branch 为 main
git status --short 只包含本次 Public 清理相关改动，或没有输出
latest commit 为最新 Public 准备提交
```

执行密钥扫描：

```bash
git ls-files -z | xargs -0 awk '
BEGIN { bad=0 }
/^[[:space:]]*#/ { next }
/ntn_[A-Za-z0-9]|figd_[A-Za-z0-9]|AIza[0-9A-Za-z_-]|prj_[A-Za-z0-9]/ {
  print FILENAME ":" FNR ":" $0
  bad=1
}
/^(GEMINI_API_KEY|FIGMA_API_KEY|NOTION_TOKEN|LARK_APP_SECRET|LARK_APP_ID)[[:space:]]*=[[:space:]]*[^[:space:]#]+/ {
  print FILENAME ":" FNR ":" $0
  bad=1
}
END { exit bad }
'
```

期望结果：

```text
没有输出，退出码为 0
```

如果扫描发现真实 Token / API Key / Secret，停止上传，先脱敏并重新提交。

执行公开信息扫描：

```bash
git ls-files -z | xargs -0 rg -n \
  "[l]injinhong|[g]mail|/[U]sers/|[l]arksuite\\.com/docx|[n]otebooklm\\.google\\.com/notebook|[0-9a-f]{32}|私有仓[库]|内[部] Git|部门内[部]|项目内[部]知识|内[部]知识库"
```

期望结果：

```text
没有输出，退出码为 1
```

如果扫描发现私有链接、个人路径、邮箱、私有页面 ID、私有知识源或 NotebookLM URL，停止上传，改成通用占位、环境变量或本地 MCP 配置说明后重新提交。

## 创建公开 GitHub 仓库

用本地 GitHub App 或浏览器打开：

```text
https://github.com/new
```

填写：

```text
Owner: HenrlyLin16
Repository name: obe-ai-product-workflow
Description: OBE AI product workflow package for PM, design, Lark, Figma, Codex and Cursor collaboration
Visibility: Public
Initialize repository: 不勾选 README / .gitignore / LICENSE
```

创建后确认仓库页面是空仓库，并显示类似：

```text
Quick setup
https://github.com/HenrlyLin16/obe-ai-product-workflow.git
```

如果仓库名已存在，改用：

```text
obe-ai-product-workflow-20260527
```

后续命令中的仓库地址同步替换。

## 推送本地提交

推荐命令：

```bash
cd <repo-root>

git remote add origin https://github.com/HenrlyLin16/obe-ai-product-workflow.git
git push -u origin main
```

如果提示 `remote origin already exists`，执行：

```bash
git remote set-url origin https://github.com/HenrlyLin16/obe-ai-product-workflow.git
git push -u origin main
```

如果推送要求登录，按 GitHub App / 浏览器提示完成授权，确保 GitHub owner 为 `HenrlyLin16`。

## 上传后验证

打开：

```text
https://github.com/HenrlyLin16/obe-ai-product-workflow
```

确认页面顶部不是 `Private`，仓库可公开访问。

确认以下文件存在：

```text
workflow/docs/ai-product-workflow-sharing/GIT_DISTRIBUTION.md
workflow/docs/ai-product-workflow-sharing/README.md
workflow/docs/ai-product-workflow-sharing/OBE-AI协作产品自动化工作流-Lark主文档.md
workflow/docs/ai-product-workflow-sharing/OBE-AI协作产品自动化工作流-分享稿.md
workflow/docs/ai-product-workflow-sharing/templates/
workflow/skills/product/pipelines.yaml
workflow/skills/product/engineering-plan-review.md
workflow/skills/product/web3-prd-figma-prompt.md
scripts/sync-workflow-skills-to-cursor.sh
scripts/sync-workflow-skills-to-codex.sh
```

在终端执行：

```bash
git remote -v
git status --short --untracked-files=no
git rev-parse --abbrev-ref --symbolic-full-name @{u}
```

期望结果：

```text
origin 指向 https://github.com/HenrlyLin16/obe-ai-product-workflow.git
工作区干净
上游分支为 origin/main
```

## 给使用者的使用说明

使用者本地执行：

```bash
git clone https://github.com/HenrlyLin16/obe-ai-product-workflow.git
cd obe-ai-product-workflow
bash workflow/docs/ai-product-workflow-sharing/scripts/install-local-workflow.sh
```

配置个人本地密钥：

```bash
cp workflow/docs/ai-product-workflow-sharing/config/lark.env.example .env.local
```

真实 `LARK_APP_ID`、`LARK_APP_SECRET`、`FIGMA_API_KEY`、`NOTION_TOKEN` 等只填写在个人本地环境，不提交到 Git。

Notion、Lark、NotebookLM 等知识源使用自己的 workspace / document / notebook，通过环境变量或本地 MCP 配置接入，不在 Public 仓库中硬编码。

## 验收标准

- GitHub 上存在公开仓库 `HenrlyLin16/obe-ai-product-workflow`
- 本地 `main` 已推送到 `origin/main`
- GitHub 页面能看到工作流包、模板、产品 Skill 和同步脚本
- 仓库不包含真实 Token / API Key / Secret
- 仓库不包含私有链接、个人路径、邮箱、私有页面 ID、私有知识源或 NotebookLM URL
- 使用者可以通过 `git clone` 拉取，并运行安装脚本完成本地配置

## 失败处理

### 推送认证失败

现象：

```text
Authentication failed
Permission denied
```

处理：

1. 确认 GitHub App / 浏览器当前登录账号是 `HenrlyLin16`
2. 重新执行 `git push -u origin main`
3. 如果仍失败，在 GitHub App 中完成 Git 凭据授权后重试

### 仓库已经存在

现象：

```text
Repository creation failed
name already exists
```

处理：

使用备用仓库名：

```text
obe-ai-product-workflow-20260527
```

并替换 remote：

```bash
git remote set-url origin https://github.com/HenrlyLin16/obe-ai-product-workflow-20260527.git
git push -u origin main
```

### 密钥或公开信息扫描失败

现象：扫描命令输出疑似密钥、私有链接、个人路径、邮箱、私有页面 ID 或私有知识源地址。

处理：

1. 不要推送
2. 将真实值替换为 `${ENV_VAR}`、`[REDACTED]` 或通用配置说明
3. 重新提交
4. 重新运行密钥扫描与公开信息扫描
