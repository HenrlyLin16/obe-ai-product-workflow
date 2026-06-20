#!/usr/bin/env python3
"""Build a conservative release-readiness checklist for Web QA Skill changes."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


def run(cmd: list[str], cwd: Path) -> dict[str, Any]:
    proc = subprocess.run(cmd, cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False)
    return {"cmd": cmd, "exit_code": proc.returncode, "output": proc.stdout.strip()[:4000]}


def main() -> int:
    p = argparse.ArgumentParser(description="Check release readiness for onebullex-web-qa source changes.")
    p.add_argument("--repo", default="/Users/jingxing/Desktop/Onebullex")
    p.add_argument("--skill-dir", default="workflow/skills/qa/onebullex-web-qa")
    p.add_argument("--output", default="release-readiness.json")
    p.add_argument("--skip-sync-check", action="store_true")
    args = p.parse_args()
    repo = Path(args.repo).expanduser().resolve()
    skill = repo / args.skill_dir

    checks: list[dict[str, Any]] = []
    status = run(["git", "status", "--short"], repo)
    changed = [line for line in status["output"].splitlines() if line.strip()]
    unrelated = [line for line in changed if args.skill_dir not in line and "scripts/sync-onebullex-web-qa-skill.sh" not in line]
    checks.append({"name": "git_diff_scope", "status": "pass" if not unrelated else "fail", "changed": changed, "unrelated": unrelated})

    py_files = sorted(str(p.relative_to(repo)) for p in (skill / "scripts").glob("*.py"))
    if py_files:
        checks.append({"name": "py_compile", **run(["python3", "-m", "py_compile", *py_files], repo)})
        checks[-1]["status"] = "pass" if checks[-1]["exit_code"] == 0 else "fail"

    flow_files = sorted(str(p.relative_to(repo)) for p in (skill / "flows").glob("*.yaml"))
    if flow_files:
        checks.append({"name": "flow_lint", **run(["python3", str(skill / "scripts" / "flow_lint.py"), *flow_files], repo)})
        checks[-1]["status"] = "pass" if checks[-1]["exit_code"] == 0 else "fail"

    if not args.skip_sync_check:
        checks.append({"name": "sync_check", **run(["scripts/sync-onebullex-web-qa-skill.sh", "--check"], repo)})
        checks[-1]["status"] = "pass" if checks[-1]["exit_code"] == 0 else "fail"

    overall = "ready" if all(c.get("status") == "pass" for c in checks) else "not_ready"
    payload = {"overall": overall, "branch_prefix": "codex/onebullex-web-qa-*", "checks": checks, "pr_description_requires": ["change summary", "validation", "not validated", "Clash VPN requirements", "high-risk flow impact"]}
    out = Path(args.output).expanduser()
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(out)
    return 0 if overall == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
