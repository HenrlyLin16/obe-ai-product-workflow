#!/usr/bin/env python3
"""Mac ClashX Pro VPN gate for OneBullEx Web QA.

The gate is intentionally conservative: it checks app/process/system proxy state
and optionally probes testnet to create traffic. It does not inspect Clash config
files, node names, credentials, or logs.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_APP = "/Applications/ClashX Pro.app"
DEFAULT_BASE_URL = "https://testnet.1bullex.com/"


def run_cmd(cmd: list[str], timeout: int = 8) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=timeout, check=False)
        return proc.returncode, proc.stdout.strip()
    except Exception as exc:
        return 127, str(exc)


def process_running() -> bool:
    code, out = run_cmd(["pgrep", "-f", "ClashX Pro|ClashXPro|Clash"], timeout=5)
    return code == 0 and bool(out.strip())


def open_app(app: str) -> tuple[bool, str]:
    code, out = run_cmd(["open", "-g", app], timeout=10)
    return code == 0, out


def system_proxy_status() -> dict[str, Any]:
    code, out = run_cmd(["scutil", "--proxy"], timeout=5)
    enabled_tokens = [
        "HTTPEnable : 1",
        "HTTPSEnable : 1",
        "SOCKSEnable : 1",
        "ProxyAutoConfigEnable : 1",
    ]
    enabled = code == 0 and any(token in out for token in enabled_tokens)
    return {"status": "pass" if enabled else "fail", "enabled": enabled, "command_exit": code, "summary": "proxy enabled" if enabled else "proxy not enabled", "raw_excerpt": out[:1200]}


def http_probe(url: str, timeout: int = 15) -> dict[str, Any]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "onebullex-web-qa-clash-gate/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return {"status": "pass" if 200 <= resp.status < 500 else "fail", "http_status": resp.status, "url": url}
    except Exception as exc:
        return {"status": "fail", "url": url, "error": str(exc)}


def run_gate(args: argparse.Namespace) -> dict[str, Any]:
    app_path = Path(args.vpn_app).expanduser()
    checks: list[dict[str, Any]] = []

    app_exists = app_path.exists()
    checks.append({"name": "clash_app_exists", "status": "pass" if app_exists else "fail", "path": str(app_path), "classification": "" if app_exists else "environment_blocker"})

    running_before = process_running()
    opened = False
    open_note = ""
    if not running_before and app_exists and args.open_if_needed and not args.dry_run:
        opened, open_note = open_app(str(app_path))
    running_after = running_before or (process_running() if not args.dry_run else False)
    checks.append({
        "name": "clash_process_running",
        "status": "pass" if running_after else ("not_run" if args.dry_run else "fail"),
        "running_before": running_before,
        "opened": opened,
        "open_note": open_note,
        "classification": "" if running_after else "environment_blocker",
    })

    proxy = system_proxy_status() if not args.dry_run else {"status": "not_run", "enabled": False, "summary": "dry-run skipped scutil"}
    proxy["name"] = "system_proxy_enabled"
    proxy["classification"] = "" if proxy.get("enabled") else "environment_blocker"
    checks.append(proxy)

    if args.probe and not args.dry_run:
        checks.append({"name": "testnet_http_probe", **http_probe(args.base_url)})
        checks.append({"name": "testnet_rest_probe", **http_probe(args.rest_url)})
    else:
        checks.append({"name": "testnet_http_probe", "status": "not_run", "url": args.base_url, "classification": "dry_run" if args.dry_run else "skipped"})
        checks.append({"name": "testnet_rest_probe", "status": "not_run", "url": args.rest_url, "classification": "dry_run" if args.dry_run else "skipped"})

    traffic_status = "pass" if args.traffic_confirmed else ("manual_required" if args.require_traffic else "not_required")
    checks.append({
        "name": "clash_menu_bar_traffic_gt_0kb",
        "status": traffic_status,
        "confirmed_by": "cli" if args.traffic_confirmed else "manual_required" if args.require_traffic else "not_required",
        "classification": "" if args.traffic_confirmed or not args.require_traffic else "environment_blocker",
    })

    blocking = [c for c in checks if c.get("classification") == "environment_blocker" and c.get("status") not in {"pass", "not_required"}]
    service = [c for c in checks if c.get("name") in {"testnet_rest_probe"} and c.get("status") == "fail"]
    if blocking:
        status = "environment_blocker"
    elif service:
        status = "service_degradation"
    else:
        status = "healthy"

    return {
        "generated": dt.datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "vpn_app": str(app_path),
        "vpn_mode": args.vpn_mode,
        "requires_system_proxy": args.require_system_proxy,
        "requires_traffic_gt_0kb": args.require_traffic,
        "failure_policy": args.failure_policy,
        "checks": checks,
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Check Mac ClashX Pro VPN readiness for OneBullEx Web QA.")
    p.add_argument("--vpn-mode", choices=["off", "auto", "required"], default="required")
    p.add_argument("--vpn-app", default=DEFAULT_APP)
    p.add_argument("--base-url", default=DEFAULT_BASE_URL)
    p.add_argument("--rest-url", default="https://testnet.1bullex.com/")
    p.add_argument("--output", default="clash-vpn-gate.json")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--open-if-needed", action="store_true", default=True)
    p.add_argument("--probe", action="store_true", default=True)
    p.add_argument("--require-system-proxy", action="store_true")
    p.add_argument("--require-traffic", action="store_true")
    p.add_argument("--traffic-confirmed", action="store_true", help="User or UI automation confirmed Clash menu-bar traffic is >0kb after probes.")
    p.add_argument("--failure-policy", choices=["block", "pause_for_manual"], default="block")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.vpn_mode == "off":
        payload = {"generated": dt.datetime.now().isoformat(timespec="seconds"), "status": "skipped", "vpn_mode": "off", "checks": []}
    else:
        payload = run_gate(args)
    out = Path(args.output).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(out)
    if payload.get("status") in {"healthy", "skipped"}:
        return 0
    if payload.get("status") == "service_degradation":
        return 3
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
