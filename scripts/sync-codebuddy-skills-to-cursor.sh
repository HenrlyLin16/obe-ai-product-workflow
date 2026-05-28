#!/usr/bin/env bash
# 将 .codebuddy/skills 同步到 .cursor/skills（SSOT = .codebuddy/skills）
# 用法：从项目根执行 ./scripts/sync-codebuddy-skills-to-cursor.sh
# 修改技能时请在 .codebuddy/skills 侧进行，改后执行本脚本同步到 .cursor/skills。

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CODEBUDDY="${ROOT}/.codebuddy/skills"
CURSOR="${ROOT}/.cursor/skills"
DOMAINS="general product investment virtual-world"

# 根目录下不视为「可加载技能」的 .md，不同步
EXCLUDE_MD="README.md product-skills-analysis-report.md product-team-skill-implementation-summary.md SKILL-COLLABORATION-GUIDE.md investment-advisor-core-capabilities.md"

echo "[sync] CodeBuddy skills -> Cursor skills (SSOT: .codebuddy/skills)"
echo ""

for domain in $DOMAINS; do
  src="${CODEBUDDY}/${domain}"
  [ ! -d "$src" ] && continue
  echo "[sync] domain: $domain"

  # 1) 根目录单文件 .md -> .cursor/skills/<name>/SKILL.md
  for f in "$src"/*.md; do
    [ ! -f "$f" ] && continue
    base=$(basename "$f")
    skip=
    for ex in $EXCLUDE_MD; do
      [ "$base" = "$ex" ] && skip=1 && break
    done
    [ -n "$skip" ] && continue
    name="${base%.md}"
    dest_dir="${CURSOR}/${name}"
    mkdir -p "$dest_dir"
    cp "$f" "${dest_dir}/SKILL.md"
    echo "  + ${name}/SKILL.md (from ${domain}/${base})"
  done

  # 2) 子目录且内含 SKILL.md -> .cursor/skills/<subdir>/
  for subdir in "$src"/*/; do
    [ ! -d "$subdir" ] && continue
    [ ! -f "${subdir}SKILL.md" ] && continue
    name=$(basename "$subdir")
    dest_dir="${CURSOR}/${name}"
    mkdir -p "$dest_dir"
    rsync -a --delete \
      --exclude='.git' \
      --exclude='.venv' \
      --exclude='__pycache__' \
      --exclude='node_modules' \
      "$subdir" "$dest_dir/"
    echo "  + ${name}/ (dir from ${domain}/${name})"
  done
  echo ""
done

echo "[sync] done. Modify skills in .codebuddy/skills, then re-run this script to update .cursor/skills."
