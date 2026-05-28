#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
cd "$ROOT"

echo "[obe-ai-workflow] root: $ROOT"

required=(
  ".codebuddy/docs/ai-product-workflow-sharing/OBE-AI协作产品自动化工作流-Lark主文档.md"
  ".codebuddy/docs/ai-product-workflow-sharing/OBE-AI协作工作流-操作手册.md"
  ".codebuddy/skills/product/pipelines.yaml"
  ".codebuddy/skills/product/web3-cex-product-team.md"
  "scripts/sync-codebuddy-skills-to-cursor.sh"
  "scripts/sync-codebuddy-skills-to-codex.sh"
)

for path in "${required[@]}"; do
  if [[ ! -e "$path" ]]; then
    echo "[obe-ai-workflow] missing required file: $path" >&2
    exit 1
  fi
done

echo "[obe-ai-workflow] required files ok"

if command -v rg >/dev/null 2>&1; then
  echo "[obe-ai-workflow] running secret scan"
  scan_paths=(
    ".codebuddy/docs/ai-product-workflow-sharing"
    ".codebuddy/skills/product/web3-cex-product-team.md"
    ".codebuddy/skills/product/pipelines.yaml"
    ".codebuddy/skills/product/engineering-plan-review.md"
    ".codebuddy/skills/product/web3-prd-figma-prompt.md"
    ".codebuddy/skills/product/product-test-qa.md"
    "scripts/sync-codebuddy-skills-to-cursor.sh"
    "scripts/sync-codebuddy-skills-to-codex.sh"
  )
  if rg -n "ntn_[A-Za-z0-9]|figd_[A-Za-z0-9]|AIza[0-9A-Za-z_-]|prj_[A-Za-z0-9]" "${scan_paths[@]}"; then
    echo "[obe-ai-workflow] token-like values found. Review output before sharing." >&2
    exit 1
  fi
  if rg -n "^(GEMINI_API_KEY|FIGMA_API_KEY|NOTION_TOKEN|LARK_APP_SECRET|LARK_APP_ID)\\s*=\\s*[^\\s#]+" \
    --glob '!*.example' \
    --glob '!*.example.toml' \
    .codebuddy/docs/ai-product-workflow-sharing \
    .codebuddy/skills/product \
    scripts/sync-codebuddy-skills-to-cursor.sh \
    scripts/sync-codebuddy-skills-to-codex.sh; then
    echo "[obe-ai-workflow] non-empty env assignments found. Review output before sharing." >&2
    exit 1
  fi
else
  echo "[obe-ai-workflow] rg not found; skipping secret scan"
fi

echo "[obe-ai-workflow] syncing Cursor skills"
bash scripts/sync-codebuddy-skills-to-cursor.sh

echo "[obe-ai-workflow] syncing Codex skills"
bash scripts/sync-codebuddy-skills-to-codex.sh

echo "[obe-ai-workflow] done"
echo "[obe-ai-workflow] next: restart Codex/Cursor if new skills do not appear"
