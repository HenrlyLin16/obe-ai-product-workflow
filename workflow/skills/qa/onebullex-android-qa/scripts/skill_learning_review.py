#!/usr/bin/env python3
"""Review confirmed QA learning candidates and prepare Skill updates."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
CONFIRM_NAME = "qa-skill-optimization-confirm.template.json"
CANDIDATES_NAME = "qa-skill-optimization-candidates.json"
PATCH_NAME = "qa-skill-optimization-confirmed.patch.md"
AUDIT_REL = Path("references") / "qa-learning-audit.md"
RELEASE_SUMMARY_NAME = "qa-github-release-summary.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Review and apply confirmed onebullex-android-qa learning candidates.")
    parser.add_argument("evidence_dir", help="Evidence directory from a onebullex-android-qa run.")
    parser.add_argument("--apply-confirmed", action="store_true", help="Read confirmed candidates and create a patch review file.")
    parser.add_argument("--write-skill", action="store_true", help="Append confirmed learnings to the repo Skill audit file.")
    parser.add_argument("--source-skill-dir", default=str(SKILL_DIR), help="Repo source Skill directory to update.")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_confirmed(evidence_dir: Path) -> tuple[Path, list[dict[str, Any]]]:
    confirm_path = evidence_dir / CONFIRM_NAME
    source_path = confirm_path if confirm_path.exists() else evidence_dir / CANDIDATES_NAME
    if not source_path.exists():
        raise SystemExit(f"Missing learning candidate file: {confirm_path} or {evidence_dir / CANDIDATES_NAME}")
    payload = load_json(source_path)
    candidates = payload.get("candidates", [])
    if not isinstance(candidates, list):
        raise SystemExit(f"Invalid candidates payload: {source_path}")
    confirmed = [item for item in candidates if isinstance(item, dict) and item.get("confirmed") is True]
    return source_path, confirmed


def render_patch(evidence_dir: Path, source_path: Path, confirmed: list[dict[str, Any]]) -> str:
    lines = [
        "# QA Skill Confirmed Learning Patch\n",
        f"- Generated: {dt.datetime.now().isoformat(timespec='seconds')}\n",
        f"- Evidence directory: `{evidence_dir}`\n",
        f"- Source confirmation file: `{source_path}`\n",
        f"- Confirmed candidates: {len(confirmed)}\n",
        "\n## Confirmed Items\n",
    ]
    if not confirmed:
        lines.append("- No confirmed learning candidates. Nothing should be applied.\n")
        return "".join(lines)
    for item in confirmed:
        lines.extend([
            f"\n### {item.get('id', 'unknown')} {item.get('title', '')}\n",
            f"- Type: `{item.get('type', '')}`\n",
            f"- Flow: `{item.get('flow', '')}`\n",
            f"- Step: `{item.get('step', '')}`\n",
            f"- Target: `{item.get('target', '')}`\n",
            f"- Recommendation: {item.get('recommendation', '')}\n",
            f"- Human notes: {item.get('human_notes', '')}\n",
        ])
    lines.append("\n## Apply Policy\n")
    lines.append("- Apply only these confirmed items to the repo source Skill.\n")
    lines.append("- Keep Codex and Cursor mirrors generated through `scripts/sync-onebullex-android-qa-skill.sh`.\n")
    return "".join(lines)


def append_audit(source_skill_dir: Path, evidence_dir: Path, source_path: Path, confirmed: list[dict[str, Any]]) -> Path:
    audit_path = source_skill_dir / AUDIT_REL
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    if not audit_path.exists():
        audit_path.write_text("# QA Learning Audit\n\nConfirmed Skill learnings applied from QA evidence.\n", encoding="utf-8")
    lines = [
        f"\n## {dt.datetime.now().isoformat(timespec='seconds')}\n",
        f"- Evidence directory: `{evidence_dir}`\n",
        f"- Confirmation file: `{source_path}`\n",
        f"- Confirmed candidates: {len(confirmed)}\n",
    ]
    for item in confirmed:
        lines.append(f"- `{item.get('type', '')}` {item.get('id', '')}: {item.get('title', '')} -> {item.get('target', '')}\n")
    with audit_path.open("a", encoding="utf-8") as fh:
        fh.write("".join(lines))
    return audit_path


def write_release_summary(evidence_dir: Path, confirmed: list[dict[str, Any]]) -> Path:
    summary_path = evidence_dir / RELEASE_SUMMARY_NAME
    lines = [
        "# QA GitHub Release Summary\n",
        f"- Evidence directory: `{evidence_dir}`\n",
        f"- Confirmed learning items: {len(confirmed)}\n",
        "\n## Proposed Branch\n",
        "- `codex/onebullex-android-qa-learning-loop`\n",
        "\n## Suggested Commit Scope\n",
        "- `workflow/skills/qa/onebullex-android-qa/**`\n",
        "- `scripts/sync-onebullex-android-qa-skill.sh`\n",
        "\n## PR Notes\n",
        "- Summarize ADB stability gate updates.\n",
        "- Summarize Android device control and VPN behavior.\n",
        "- Summarize Record & Replay seed workflow additions.\n",
        "- Link the local QA report and learning summary.\n",
        "\n## Confirmed Learning Items\n",
    ]
    if not confirmed:
        lines.append("- No confirmed learning items yet.\n")
    else:
        for item in confirmed:
            lines.append(f"- `{item.get('type', '')}` {item.get('title', '')} -> {item.get('target', '')}\n")
    summary_path.write_text("".join(lines), encoding="utf-8")
    return summary_path


def main() -> int:
    args = parse_args()
    evidence_dir = Path(args.evidence_dir).expanduser().resolve()
    source_path, confirmed = load_confirmed(evidence_dir)
    patch_text = render_patch(evidence_dir, source_path, confirmed)
    patch_path = evidence_dir / PATCH_NAME
    patch_path.write_text(patch_text, encoding="utf-8")
    print(f"Patch review: {patch_path}")
    print(f"Confirmed candidates: {len(confirmed)}")

    if args.write_skill:
        audit_path = append_audit(Path(args.source_skill_dir).expanduser().resolve(), evidence_dir, source_path, confirmed)
        release_summary = write_release_summary(evidence_dir, confirmed)
        print(f"Skill audit updated: {audit_path}")
        print(f"GitHub release summary: {release_summary}")
        print("Next: run scripts/sync-onebullex-android-qa-skill.sh from the repo root.")
    elif args.apply_confirmed:
        print("No Skill files were modified. Review the patch file before passing --write-skill.")
    else:
        print("Use --apply-confirmed to review confirmed candidates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
