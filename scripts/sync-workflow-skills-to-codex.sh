#!/usr/bin/env bash
# Sync workflow/skills into Codex local skills.
# SSOT = workflow/skills. Destination defaults to ~/.codex/skills/onebullex.
# Usage: ./scripts/sync-workflow-skills-to-codex.sh [destination]

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORKFLOW="${ROOT}/workflow/skills"
DEST="${1:-${HOME}/.codex/skills/onebullex}"
DOMAINS="general product investment virtual-world"
EXCLUDE_MD="README.md product-skills-analysis-report.md product-team-skill-implementation-summary.md SKILL-COLLABORATION-GUIDE.md investment-advisor-core-capabilities.md"

if [[ ! -d "$WORKFLOW" ]]; then
  echo "[sync] missing source: $WORKFLOW" >&2
  exit 1
fi

mkdir -p "$DEST"

echo "[sync] Workflow skills -> Codex skills"
echo "[sync] source: $WORKFLOW"
echo "[sync] dest:   $DEST"
echo ""

for domain in $DOMAINS; do
  src="${WORKFLOW}/${domain}"
  [[ ! -d "$src" ]] && continue
  echo "[sync] domain: $domain"

  for f in "$src"/*.md; do
    [[ ! -f "$f" ]] && continue
    base="$(basename "$f")"
    skip=""
    for ex in $EXCLUDE_MD; do
      [[ "$base" == "$ex" ]] && skip=1 && break
    done
    [[ -n "$skip" ]] && continue

    name="${base%.md}"
    dest_dir="${DEST}/${name}"
    mkdir -p "$dest_dir"
    cp "$f" "${dest_dir}/SKILL.md"
    echo "  + ${name}/SKILL.md (from ${domain}/${base})"
  done

  for subdir in "$src"/*/; do
    [[ ! -d "$subdir" ]] && continue
    [[ ! -f "${subdir}SKILL.md" ]] && continue
    name="$(basename "$subdir")"
    dest_dir="${DEST}/${name}"
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

echo "[sync] done. Restart Codex after syncing if new skills do not appear immediately."
