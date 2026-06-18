#!/usr/bin/env python3
"""Placeholder WebSocket freshness probe for OneBullEx Web QA.

Endpoint/channel discovery is product-specific. This script intentionally fails
closed unless --dry-run is used or a concrete endpoint is supplied later.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description="Probe public WebSocket freshness.")
    p.add_argument("--endpoint")
    p.add_argument("--freshness-window-ms", type=int, default=5000)
    p.add_argument("--output")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    status = "not_run" if args.dry_run else "unknown"
    payload = {"status": status, "endpoint": args.endpoint or "", "freshness_window_ms": args.freshness_window_ms, "reason": "dry-run skipped WS" if args.dry_run else "No stable WS endpoint configured yet"}
    out = Path(args.output) if args.output else Path("ws-probe.json")
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(out)
    return 0 if args.dry_run else 2


if __name__ == "__main__":
    raise SystemExit(main())
