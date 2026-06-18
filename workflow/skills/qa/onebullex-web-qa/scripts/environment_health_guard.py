#!/usr/bin/env python3
"""Emit a conservative OneBullEx Web environment health-gate JSON."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import urllib.request
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description="Check OneBullEx Web testnet environment health.")
    p.add_argument("--base-url", default="https://testnet.1bullex.com/")
    p.add_argument("--output")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    checks = []
    if args.dry_run:
        checks.append({"name": "site_http_reachable", "status": "not_run", "classification": "dry_run", "error": "dry-run skipped network"})
        status = "not_run"
    else:
        try:
            with urllib.request.urlopen(args.base_url, timeout=15) as resp:
                ok = 200 <= resp.status < 500
                checks.append({"name": "site_http_reachable", "status": "pass" if ok else "fail", "classification": "environment_blocker" if not ok else "", "http_status": resp.status})
                status = "healthy" if ok else "environment_blocker"
        except Exception as exc:
            checks.append({"name": "site_http_reachable", "status": "fail", "classification": "environment_blocker", "error": str(exc)})
            status = "environment_blocker"
    payload = {"generated": dt.datetime.now().isoformat(timespec="seconds"), "base_url": args.base_url, "status": status, "checks": checks}
    out = Path(args.output) if args.output else Path("environment-health-check.json")
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(out)
    return 0 if status in {"healthy", "not_run"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
