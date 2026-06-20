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
SIDE_EFFECT_LEVELS = {"none", "login", "dry_run", "submit", "withdraw"}
TEST_LEVELS = {"L0", "L1", "L2", "L3", "L4"}
RISK_LEVELS = {"low", "medium", "high", "critical"}
RUNTIMES = {"playwright", "codex"}
ORACLE_TYPES = {"dom", "api", "ws", "state", "visual", "negative"}
ACTIONS = {"goto", "click", "type", "wait_for", "assert_text", "assert_url", "assert_visible", "assert_not_visible", "assert_table_sort", "assert_balance_block", "assert_order_state", "assert_position_state", "assert_history_row", "assert_toast", "assert_ws_freshness", "assert_numeric_delta", "assert_api_response", "snapshot", "ux_snapshot", "ensure_locale", "safety_gate", "sleep", "assert_account_profile", "ensure_clash_vpn"}


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



def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def infer_expected_oracles(data: dict[str, Any]) -> set[str]:
    actions = {step.get("action") for step in data.get("steps", []) if isinstance(step, dict)}
    expected: set[str] = set()
    if actions & {"assert_visible", "assert_text", "assert_url", "assert_table_sort"}:
        expected.add("dom")
    if "assert_api_response" in actions:
        expected.add("api")
    if "assert_ws_freshness" in actions:
        expected.add("ws")
    if actions & {"assert_order_state", "assert_position_state", "assert_history_row", "assert_balance_block", "assert_numeric_delta"}:
        expected.add("state")
    if "ux_snapshot" in actions:
        expected.add("visual")
    if actions & {"assert_toast", "assert_not_visible"}:
        expected.add("negative")
    return expected

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
    if data.get("test_level") not in TEST_LEVELS:
        errors.append(f"{path}: missing or invalid test_level {data.get('test_level')}")
    if data.get("risk_level") not in RISK_LEVELS:
        errors.append(f"{path}: missing or invalid risk_level {data.get('risk_level')}")
    if data.get("required_runtime") not in RUNTIMES:
        errors.append(f"{path}: missing or invalid required_runtime {data.get('required_runtime')}")
    if data.get("side_effect_level") not in SIDE_EFFECT_LEVELS:
        errors.append(f"{path}: missing or invalid side_effect_level {data.get('side_effect_level')}")
    oracle = as_list(data.get("oracle_type"))
    if not oracle:
        errors.append(f"{path}: missing oracle_type")
    invalid_oracle = [item for item in oracle if item not in ORACLE_TYPES]
    if invalid_oracle:
        errors.append(f"{path}: invalid oracle_type {invalid_oracle}")
    inferred = infer_expected_oracles(data)
    missing_inferred = sorted(inferred - set(oracle))
    if missing_inferred:
        errors.append(f"{path}: oracle_type missing expected coverage {missing_inferred}")
    if data.get("browser_mode") == "chrome" and data.get("public_only") is True:
        errors.append(f"{path}: public_only flow should not require browser_mode=chrome")
    if data.get("test_level") in {"L2", "L3"} and data.get("required_account_profile") == "guest":
        errors.append(f"{path}: {data.get('test_level')} flow must not use guest account profile")
    if data.get("test_level") == "L3" and data.get("side_effect_level") not in {"dry_run", "submit", "withdraw"}:
        errors.append(f"{path}: L3 flow must declare transaction side_effect_level")
    if data.get("test_level") == "L4" and "visual" not in as_list(data.get("oracle_type")):
        errors.append(f"{path}: L4 flow must include visual oracle_type")
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
        if action == "sleep" and not step.get("allow_fixed_wait"):
            errors.append(f"{path}: step {idx} uses sleep without allow_fixed_wait=true per anti-flaky policy")
        if action == "ensure_clash_vpn" and not data.get("requires_clash_vpn"):
            errors.append(f"{path}: step {idx} uses ensure_clash_vpn but flow does not declare requires_clash_vpn=true")
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
