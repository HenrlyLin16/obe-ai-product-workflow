#!/usr/bin/env python3
"""Classify OneBullEx Web account profile from visible-page observations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

PROFILES = {"guest", "basic-login", "funded-spot", "funded-futures", "open-orders", "open-position", "withdraw-capable"}


def classify(text: str) -> str:
    if "登录" in text and "UID" not in text:
        return "guest"
    if "持仓" in text and "暂无" not in text:
        return "open-position"
    if "订单" in text and "暂无" not in text:
        return "open-orders"
    if "保证金" in text:
        return "funded-futures"
    if "USDT" in text or "资产" in text:
        return "funded-spot"
    if "UID" in text or "账户" in text:
        return "basic-login"
    return "guest"


def main() -> int:
    p = argparse.ArgumentParser(description="Probe account profile from DOM summary text.")
    p.add_argument("--dom-summary")
    p.add_argument("--expected", choices=sorted(PROFILES))
    p.add_argument("--output")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    text = "UID 123456 资产 USDT 保证金" if args.dry_run else (Path(args.dom_summary).read_text(encoding="utf-8") if args.dom_summary else "")
    actual = classify(text)
    payload = {"expected": args.expected or "", "actual": actual, "match": not args.expected or args.expected == actual, "dry_run": args.dry_run}
    out = Path(args.output) if args.output else Path("account-state-probe.json")
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(out)
    return 0 if payload["match"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
