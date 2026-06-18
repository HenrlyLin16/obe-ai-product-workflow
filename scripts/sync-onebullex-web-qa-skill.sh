#!/usr/bin/env bash
# Sync the repo source of onebullex-web-qa to local Codex and Cursor mirrors.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SOURCE="${ROOT}/workflow/skills/qa/onebullex-web-qa"
CODEX_DEST="${HOME}/.codex/skills/onebullex-web-qa"
CURSOR_DEST="${ROOT}/.cursor/skills/onebullex-web-qa"

DRY_RUN=0
CHECK=0
SYNC_CODEX=1
SYNC_CURSOR=1

usage() {
  cat <<'EOF'
Usage: scripts/sync-onebullex-web-qa-skill.sh [options]

Options:
  --dry-run      Show sync operations without writing files.
  --check        Verify source and mirrors are in sync.
  --codex-only   Sync/check only ~/.codex/skills/onebullex-web-qa.
  --cursor-only  Sync/check only .cursor/skills/onebullex-web-qa.
  -h, --help     Show this help.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --check) CHECK=1 ;;
    --codex-only) SYNC_CODEX=1; SYNC_CURSOR=0 ;;
    --cursor-only) SYNC_CODEX=0; SYNC_CURSOR=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "[sync] unknown option: $1" >&2; usage; exit 2 ;;
  esac
  shift
done

if [[ ! -f "${SOURCE}/SKILL.md" ]]; then
  echo "[sync] missing source Skill: ${SOURCE}/SKILL.md" >&2
  exit 1
fi

RSYNC_EXCLUDES=(
  --exclude='.git'
  --exclude='.DS_Store'
  --exclude='SYNCED_FROM.md'
  --exclude='__pycache__'
  --exclude='*.pyc'
  --exclude='.pytest_cache'
  --exclude='evidence'
  --exclude='evidence/**'
  --exclude='*.log'
  --exclude='tmp'
  --exclude='tmp/**'
)

write_marker() {
  local dest="$1"
  cat > "${dest}/SYNCED_FROM.md" <<EOF
# Synced Skill Mirror

- Source: \`${SOURCE}\`
- Destination: \`${dest}\`
- Synced at: \`$(date -u +"%Y-%m-%dT%H:%M:%SZ")\`

This directory is a generated mirror. Edit the repo source, then run:

\`\`\`bash
scripts/sync-onebullex-web-qa-skill.sh
\`\`\`
EOF
}

sync_dest() {
  local dest="$1"
  echo "[sync] source: ${SOURCE}"
  echo "[sync] dest:   ${dest}"
  if [[ "$CHECK" -eq 1 ]]; then
    local changes
    changes="$(rsync -a --checksum --delete --dry-run --itemize-changes "${RSYNC_EXCLUDES[@]}" "${SOURCE}/" "${dest}/" | grep -v '^\.d' || true)"
    if [[ -n "$changes" ]]; then
      printf '%s\n' "$changes"
      return 1
    fi
    echo "[sync] check ok: ${dest}"
    return
  fi
  if [[ "$DRY_RUN" -eq 1 ]]; then
    rsync -a --delete --dry-run --itemize-changes "${RSYNC_EXCLUDES[@]}" "${SOURCE}/" "${dest}/"
    return
  fi
  mkdir -p "$dest"
  rsync -a --delete "${RSYNC_EXCLUDES[@]}" "${SOURCE}/" "${dest}/"
  write_marker "$dest"
  echo "[sync] wrote mirror marker: ${dest}/SYNCED_FROM.md"
}

if [[ "$SYNC_CODEX" -eq 1 ]]; then
  sync_dest "$CODEX_DEST"
fi

if [[ "$SYNC_CURSOR" -eq 1 ]]; then
  sync_dest "$CURSOR_DEST"
fi

echo "[sync] done"
