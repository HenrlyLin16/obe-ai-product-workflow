#!/usr/bin/env bash
# Sync .codebuddy/skills into Codex local skills.
# SSOT = .codebuddy/skills. Destination defaults to ~/.codex/skills/onebullex.
# Usage: ./scripts/sync-codebuddy-skills-to-codex.sh [destination]

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CODEBUDDY="${ROOT}/.codebuddy/skills"
DEST="${1:-${HOME}/.codex/skills/onebullex}"
DOMAINS="general product investment virtual-world"
EXCLUDE_MD="README.md product-skills-analysis-report.md product-team-skill-implementation-summary.md SKILL-COLLABORATION-GUIDE.md investment-advisor-core-capabilities.md"

if [[ ! -d "$CODEBUDDY" ]]; then
  echo "[sync] missing source: $CODEBUDDY" >&2
  exit 1
fi

mkdir -p "$DEST"

echo "[sync] CodeBuddy skills -> Codex skills"
echo "[sync] source: $CODEBUDDY"
echo "[sync] dest:   $DEST"
echo ""

for domain in $DOMAINS; do
  src="${CODEBUDDY}/${domain}"
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
