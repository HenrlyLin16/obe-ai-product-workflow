#!/usr/bin/env python3
"""Compatibility CLI for OneBullEx Android QA.

Delegates execution to flow_runner.py while preserving the original scenario CLI.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
FLOW_RUNNER = SCRIPT_DIR / "flow_runner.py"
SCENARIO_TO_FLOW = {
    "smoke": "smoke.yaml",
    "market-sort": "market-sort.yaml",
    "asset-sort": "asset-sort.yaml",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run OneBullEx Android QA via adb and Flow DSL.")
    parser.add_argument("--serial")
    parser.add_argument("--wireless")
    parser.add_argument("--channel", choices=["dev", "prod"], default="dev")
    parser.add_argument("--package")
    parser.add_argument("--activity", default="com.icy.neptune.MainActivity")
    parser.add_argument("--out-dir", default="/tmp/onebullex-android-qa")
    parser.add_argument("--run-name")
    parser.add_argument("--no-launch", action="store_true")
    parser.add_argument("--scenario", action="append", choices=sorted(SCENARIO_TO_FLOW), help="Backward-compatible scenario selector.")
    parser.add_argument("--flow", action="append", help="Flow path/name or all. Overrides --scenario when provided.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--allow-side-effects", action="store_true")
    parser.add_argument("--skip-version-check", action="store_true")
    parser.add_argument("--version-check-only", action="store_true")
    parser.add_argument("--allow-install-latest", action="store_true")
    parser.add_argument("--accept-version-gate-risk", action="store_true")
    parser.add_argument("--requirement-doc")
    parser.add_argument("--device-start-state")
    parser.add_argument("--force-stop-before-launch", action="store_true")
    parser.add_argument("--evidence-level", choices=["minimal", "normal", "full"], default="normal")
    return parser.parse_args()


def run_flow(args: argparse.Namespace, flow: str) -> int:
    cmd = [sys.executable, str(FLOW_RUNNER), flow]
    for opt in ["serial", "wireless", "channel", "package", "activity", "out_dir", "run_name", "evidence_level", "requirement_doc", "device_start_state"]:
        val = getattr(args, opt)
        if val:
            cmd.extend(["--" + opt.replace("_", "-"), str(val)])
    if args.no_launch:
        cmd.append("--no-launch")
    if args.dry_run:
        cmd.append("--dry-run")
    if args.allow_side_effects:
        cmd.append("--allow-side-effects")
    if args.skip_version_check:
        cmd.append("--skip-version-check")
    if args.version_check_only:
        cmd.append("--version-check-only")
    if args.allow_install_latest:
        cmd.append("--allow-install-latest")
    if args.accept_version_gate_risk:
        cmd.append("--accept-version-gate-risk")
    if args.force_stop_before_launch:
        cmd.append("--force-stop-before-launch")
    return subprocess.run(cmd).returncode


def main() -> int:
    args = parse_args()
    flows = args.flow
    if not flows:
        scenarios = args.scenario
        if not scenarios or set(scenarios) == {"smoke", "market-sort", "asset-sort"}:
            flows = ["all"]
        else:
            flows = [SCENARIO_TO_FLOW[s] for s in scenarios]
    if len(flows) == 1:
        return run_flow(args, flows[0])
    rc = 0
    for idx, flow in enumerate(flows, start=1):
        original_run_name = args.run_name
        if original_run_name:
            args.run_name = f"{original_run_name}-{idx}-{Path(flow).stem}"
        rc = run_flow(args, flow) or rc
        args.run_name = original_run_name
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
