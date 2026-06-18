#!/usr/bin/env python3
"""Inspect or summarize an existing onebullex-web-qa evidence directory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description="Summarize OneBullEx Web QA report artifacts.")
    p.add_argument("--evidence-dir", required=True)
    args = p.parse_args()
    evidence = Path(args.evidence_dir).expanduser()
    report = evidence / "onebullex-web-qa-report.json"
    if not report.exists():
        raise SystemExit(f"Missing report JSON: {report}")
    data = json.loads(report.read_text(encoding="utf-8"))
    print(json.dumps({"evidence_dir": str(evidence), "summary": data.get("summary"), "report": str(evidence / "onebullex-web-qa-report.md"), "bug_template": str(evidence / "confirmed-bugs.template.json")}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
