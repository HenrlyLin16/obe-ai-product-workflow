#!/usr/bin/env python3
"""Convert confirmed OneBullEx QA product-bug candidates into Zentao drafts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ZENTAO_CREATE_URL = "https://zentao.1bullex.com/index.php?m=bug&f=create&productID=1&branch=0&extra=moduleID=0"

SAMPLE = [
    {
        "confirmed": True,
        "bug_candidate": True,
        "category": "product_bug",
        "title": "[Android][OneBullEx dev] Change% sorting does not toggle descending",
        "module": "/",
        "affected_version": "dev",
        "bug_type": "代码错误",
        "severity": 3,
        "priority": 3,
        "steps": ["Run market-sort flow", "Tap Change% twice"],
        "actual": "List remains ascending after the second tap.",
        "expected": "List should toggle to descending order.",
        "attachments": ["/tmp/onebullex-android-qa/sample/screenshot.png"],
    }
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build Zentao bug draft payloads from confirmed bug candidates.")
    p.add_argument("template", nargs="?", help="Path to confirmed-bugs.template.json or onebullex-android-qa-report.json.")
    p.add_argument("--out", help="Output JSON path. Defaults next to input as zentao-bug-drafts.json.")
    p.add_argument("--sample-report", action="store_true", help="Emit a sample draft without reading input.")
    return p.parse_args()


def load_items(args: argparse.Namespace) -> tuple[list[dict[str, Any]], Path | None]:
    if args.sample_report:
        return SAMPLE, None
    if not args.template:
        raise SystemExit("Provide confirmed-bugs.template.json/report.json or pass --sample-report.")
    path = Path(args.template).expanduser()
    if not path.exists():
        raise SystemExit(f"Input not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data, path
    if isinstance(data, dict) and isinstance(data.get("results"), list):
        return report_results_to_items(data, path), path
    raise SystemExit("Input must be a bug template list or report JSON with results.")


def report_results_to_items(data: dict[str, Any], path: Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for result in data.get("results", []):
        if not result.get("bug_candidate") or result.get("category") != "product_bug":
            continue
        evidence = result.get("evidence") or {}
        items.append({
            "confirmed": False,
            "bug_candidate": True,
            "category": "product_bug",
            "title": f"[Android][OneBullEx dev] {result.get('flow')}/{result.get('step')} failed",
            "module": "/",
            "affected_version": "",
            "bug_type": "代码错误",
            "severity": 3,
            "priority": 3,
            "steps": [f"Run flow {result.get('flow')}", f"Step {result.get('step')}: {result.get('action')}"],
            "actual": "; ".join(str(n) for n in result.get("notes", [])),
            "expected": "Step should match the documented OneBullEx requirement.",
            "attachments": list(evidence.values()),
            "source_report": str(path),
        })
    return items


def to_draft(item: dict[str, Any]) -> dict[str, Any]:
    steps = item.get("steps") or []
    if isinstance(steps, str):
        steps = [steps]
    body = "[步骤]\n" + "\n".join(str(s) for s in steps)
    body += "\n\n[结果]\n" + str(item.get("actual", ""))
    body += "\n\n[期望]\n" + str(item.get("expected", ""))
    return {
        "zentao_url": ZENTAO_CREATE_URL,
        "account_hint": "Henrly linjinhong16@gmail.com",
        "product": "OneBullEx",
        "module": item.get("module", "/"),
        "affected_version": item.get("affected_version", ""),
        "title": item.get("title", ""),
        "bug_type": item.get("bug_type", "代码错误"),
        "severity": item.get("severity", 3),
        "priority": item.get("priority", 3),
        "repro_steps": body,
        "attachments": item.get("attachments", []),
        "safety_gate": "Open Chrome and fill this draft, but stop before clicking 保存 until the user confirms.",
    }


def main() -> int:
    args = parse_args()
    items, input_path = load_items(args)
    allowed_categories = {"product_bug", "ux_blocker", "ui_inconsistency", "copy_issue", "accessibility_issue"}
    confirmed = [i for i in items if i.get("confirmed") is True and i.get("bug_candidate") is True and i.get("category") in allowed_categories]
    if not confirmed:
        print("No confirmed product/UX bug candidates found. Set confirmed: true on P0/P1 candidates before drafting.")
        return 1
    drafts = [to_draft(i) for i in confirmed]
    if args.out:
        out = Path(args.out).expanduser()
    elif input_path:
        out = input_path.with_name("zentao-bug-drafts.json")
    else:
        out = Path("/tmp/zentao-bug-drafts.sample.json")
    out.write_text(json.dumps(drafts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
