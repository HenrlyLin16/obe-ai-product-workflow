#!/usr/bin/env python3
"""Lint OneBullEx Web QA Flow DSL files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except Exception:
    yaml = None

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
ROUTES_DIR = SKILL_DIR / "routes"
REQUIRED = ["name", "version", "browser_mode", "locale", "viewport", "required_account_profile", "required_start_state", "requires_health_gate", "side_effects", "steps"]
ACCOUNT_PROFILES = {"guest", "basic-login", "funded-spot", "funded-futures", "open-orders", "open-position", "withdraw-capable"}
BROWSER_MODES = {"iab", "chrome", "any"}
VIEWPORTS = {"desktop", "mobile", "both"}
SIDE_EFFECTS = {"none", "auth-only", "blocked-by-default", "testnet-submit", "withdraw-probe-only"}
ACTIONS = {"goto", "click", "type", "wait_for", "assert_text", "assert_url", "assert_visible", "assert_not_visible", "assert_table_sort", "assert_balance_block", "assert_order_state", "assert_position_state", "assert_history_row", "assert_toast", "assert_ws_freshness", "assert_numeric_delta", "assert_api_response", "snapshot", "ux_snapshot", "ensure_locale", "safety_gate", "sleep", "assert_account_profile"}


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) if yaml else json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("top-level must be mapping")
    return data


def load_route_keys() -> set[str]:
    keys: set[str] = set()
    for path in ROUTES_DIR.glob("*.yaml"):
        if path.name.startswith("_"):
            continue
        data = load_yaml(path)
        feature = str(data.get("feature") or path.stem.replace("-", "_"))
        for name in (data.get("elements") or {}).keys():
            keys.add(f"{feature}.{name}")
    return keys


def lint_flow(path: Path, route_keys: set[str]) -> list[str]:
    errors: list[str] = []
    try:
        data = load_yaml(path)
    except Exception as exc:
        return [f"{path}: cannot parse: {exc}"]
    for key in REQUIRED:
        if key not in data:
            errors.append(f"{path}: missing top-level field {key}")
    if data.get("required_account_profile") not in ACCOUNT_PROFILES:
        errors.append(f"{path}: invalid required_account_profile {data.get('required_account_profile')}")
    if data.get("browser_mode") not in BROWSER_MODES:
        errors.append(f"{path}: invalid browser_mode {data.get('browser_mode')}")
    if data.get("viewport") not in VIEWPORTS:
        errors.append(f"{path}: invalid viewport {data.get('viewport')}")
    if data.get("side_effects") not in SIDE_EFFECTS:
        errors.append(f"{path}: invalid side_effects {data.get('side_effects')}")
    if data.get("browser_mode") == "chrome" and data.get("public_only") is True:
        errors.append(f"{path}: public_only flow should not require browser_mode=chrome")
    steps = data.get("steps")
    if not isinstance(steps, list) or not steps:
        errors.append(f"{path}: steps must be a non-empty list")
        return errors
    for idx, step in enumerate(steps, 1):
        if not isinstance(step, dict):
            errors.append(f"{path}: step {idx} must be mapping")
            continue
        action = step.get("action")
        if action not in ACTIONS:
            errors.append(f"{path}: step {idx} has unsupported action {action}")
        route = step.get("route")
        if route and route not in route_keys:
            errors.append(f"{path}: step {idx} references missing route {route}")
        if data.get("side_effects") in {"blocked-by-default", "testnet-submit"} and action == "safety_gate" and not step.get("requires_side_effect"):
            errors.append(f"{path}: safety_gate step {idx} must declare requires_side_effect=true for high-risk flow")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint onebullex-web-qa flows.")
    parser.add_argument("flows", nargs="+", help="Flow YAML/JSON files")
    args = parser.parse_args()
    route_keys = load_route_keys()
    all_errors: list[str] = []
    for item in args.flows:
        all_errors.extend(lint_flow(Path(item), route_keys))
    if all_errors:
        print("\n".join(all_errors))
        return 1
    print(f"flow_lint ok: {len(args.flows)} flow(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
