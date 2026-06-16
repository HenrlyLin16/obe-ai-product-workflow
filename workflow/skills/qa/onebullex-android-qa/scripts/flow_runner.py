#!/usr/bin/env python3
"""Run OneBullEx Android QA YAML flows."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - fallback tested through JSON-compatible YAML.
    yaml = None

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from ui_driver import AdbDevice, DriverError, UIDriver, choose_serial, require_adb, summarize_xml, text_values, label_values, parse_nodes

DEFAULT_PACKAGE = "com.onemore.onebullex.dev"
CHANNEL_TO_PACKAGE = {
    "dev": "com.onemore.onebullex.dev",
    "prod": "com.onemore.onebullex",
}
DEFAULT_ACTIVITY = "com.icy.neptune.MainActivity"
REPORT_NAME = "onebullex-android-qa-report.md"
REPORT_JSON_NAME = "onebullex-android-qa-report.json"
BUG_TEMPLATE_NAME = "confirmed-bugs.template.json"
EXPERIENCE_SUMMARY_NAME = "qa-experience-summary.md"
OPTIMIZATION_CANDIDATES_NAME = "qa-skill-optimization-candidates.json"
OPTIMIZATION_CONFIRM_NAME = "qa-skill-optimization-confirm.template.json"
FLOWS_USED_DIR_NAME = "flows-used"
SKILL_DIR = SCRIPT_DIR.parent
FLOWS_DIR = SKILL_DIR / "flows"
APK_VERSION_GUARD = SCRIPT_DIR / "apk_version_guard.py"


@dataclass
class StepResult:
    flow: str
    step: str
    action: str
    status: str
    category: str = ""
    bug_candidate: bool = False
    notes: list[str] = field(default_factory=list)
    selector: dict[str, Any] | None = None
    evidence: dict[str, str] = field(default_factory=dict)
    fallback: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "flow": self.flow,
            "step": self.step,
            "action": self.action,
            "status": self.status,
            "category": self.category,
            "bug_candidate": self.bug_candidate,
            "notes": self.notes,
            "selector": self.selector,
            "evidence": self.evidence,
            "fallback": self.fallback,
        }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run OneBullEx Android QA flows.")
    p.add_argument("flow", nargs="?", default="all", help="Flow path/name or all.")
    p.add_argument("--serial", default=os.environ.get("ADB_SERIAL"))
    p.add_argument("--wireless")
    p.add_argument("--channel", choices=["dev", "prod"], default="dev")
    p.add_argument("--package")
    p.add_argument("--activity", default=DEFAULT_ACTIVITY)
    p.add_argument("--out-dir", default="/tmp/onebullex-android-qa")
    p.add_argument("--run-name")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--allow-side-effects", action="store_true")
    p.add_argument("--skip-version-check", action="store_true")
    p.add_argument("--version-check-only", action="store_true")
    p.add_argument("--allow-install-latest", action="store_true")
    p.add_argument("--accept-version-gate-risk", action="store_true")
    p.add_argument("--requirement-doc")
    p.add_argument("--device-start-state")
    p.add_argument("--force-stop-before-launch", action="store_true")
    p.add_argument("--evidence-level", choices=["minimal", "normal", "full"], default="normal")
    p.add_argument("--no-launch", action="store_true")
    return p.parse_args()


def package_for_channel(channel: str, package_override: str | None) -> str:
    return package_override or CHANNEL_TO_PACKAGE.get(channel, DEFAULT_PACKAGE)


def load_yaml(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if yaml:
        data = yaml.safe_load(text)
    else:
        data = json.loads(text)
    if not isinstance(data, dict):
        raise DriverError(f"Flow must be a mapping: {path}")
    return data


def resolve_flows(flow_arg: str) -> list[Path]:
    if flow_arg == "all":
        names = ["smoke.yaml", "market-sort.yaml", "asset-sort.yaml"]
        return [FLOWS_DIR / name for name in names]
    path = Path(flow_arg).expanduser()
    if path.exists():
        return [path]
    if not flow_arg.endswith(".yaml"):
        flow_arg += ".yaml"
    path = FLOWS_DIR / flow_arg
    if not path.exists():
        raise DriverError(f"Flow not found: {flow_arg}")
    return [path]


def prepare_device(device: AdbDevice, package: str, activity: str, no_launch: bool, force_stop_before_launch: bool = False) -> list[str]:
    if device.dry_run:
        return ["Dry-run mode: skipped adb device mutation and launch."]
    notes: list[str] = []
    device.shell("svc", "power", "stayon", "true", check=False)
    device.shell("cmd", "statusbar", "collapse", check=False)
    lock_state = str(device.shell("dumpsys", "window", "policy", check=False))
    if "mInputRestricted=true" in lock_state or "isStatusBarKeyguard=true" in lock_state:
        raise DriverError("Device appears locked. Unlock the phone before running QA.")
    resolved = str(device.shell("cmd", "package", "resolve-activity", "--brief", package, check=False)).strip()
    notes.append(f"Resolved activity: {resolved or 'not reported'}")
    if not no_launch:
        if force_stop_before_launch:
            device.shell("am", "force-stop", package, check=False)
            time.sleep(0.5)
            notes.append(f"Force-stopped {package} before launch")
        component = f"{package}/{activity}"
        device.shell("am", "start", "-n", component, check=True)
        time.sleep(1.2)
        notes.append(f"Launched {component}")
    return notes


def run_version_gate(args: argparse.Namespace, serial: str, package: str, out_dir: Path) -> tuple[dict[str, Any] | None, list[str]]:
    output_path = out_dir / "apk-version-check.json"
    if args.dry_run:
        result = {
            "status": "not_run",
            "channel": args.channel,
            "package": package,
            "serial": serial,
            "recommended_action": "Dry-run skipped device and remote package freshness checks.",
        }
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return result, ["Dry-run mode: skipped APK latest-package gate.", f"APK version check JSON: {output_path}"]
    if args.skip_version_check:
        return {
            "status": "skipped",
            "channel": args.channel,
            "package": package,
            "serial": serial,
            "recommended_action": "Version check was explicitly skipped by the user.",
        }, ["WARNING: APK latest-package gate was skipped by explicit user request."]
    cmd = [
        sys.executable,
        str(APK_VERSION_GUARD),
        "--channel",
        args.channel,
        "--serial",
        serial,
        "--package",
        package,
        "--output",
        str(output_path),
    ]
    if args.allow_install_latest:
        cmd.append("--allow-install-latest")
        cmd.append("--inspect-apk")
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False)
    raw = output_path.read_text(encoding="utf-8") if output_path.exists() else proc.stdout
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise DriverError(f"APK version gate failed to produce JSON. Output:\n{proc.stdout}") from exc
    notes = [
        f"APK latest-package gate: {result.get('status')} for {args.channel}/{package}.",
        f"APK version check JSON: {output_path}",
    ]
    if result.get("reason"):
        notes.append(str(result["reason"]))
    if result.get("recommended_action"):
        notes.append(str(result["recommended_action"]))
    allowed_with_risk = args.accept_version_gate_risk and result.get("status") in {"unknown", "outdated", "not_installed"}
    if allowed_with_risk:
        result["accepted_risk"] = True
        notes.append("APK gate risk explicitly accepted for this run; continuing with lower confidence.")
    if result.get("status") != "latest" and not args.version_check_only and not allowed_with_risk:
        raise DriverError(
            "APK latest-package gate blocked QA execution. "
            f"status={result.get('status')}; reason={result.get('reason')}; "
            f"details={output_path}"
        )
    if proc.returncode not in (0,):
        if allowed_with_risk:
            notes.append(f"APK guard command exited {proc.returncode}, but this run continued because risk was explicitly accepted.")
        elif args.version_check_only:
            notes.append(f"APK guard command exited {proc.returncode} during version-check-only mode.")
    return result, notes


def collect_environment(device: AdbDevice, channel: str, package: str, activity: str, side_effects: str, version_gate: dict[str, Any] | None = None, requirement_doc: str | None = None, device_start_state: str | None = None) -> dict[str, Any]:
    version_summary = version_gate or {"status": "not_run"}
    if device.dry_run:
        return {
            "serial": device.serial,
            "channel": channel,
            "package": package,
            "activity": activity,
            "device": "dry-run Solana Seeker sample",
            "wm_size": "Physical size: 1200x2670",
            "wm_density": "Physical density: 480",
            "side_effects": side_effects,
            "apk_version_gate": version_summary,
            "requirement_doc": requirement_doc or "",
            "device_start_state": device_start_state or "",
            "package_gate_exception_accepted": bool(version_summary.get("accepted_risk")),
        }
    return {
        "serial": device.serial,
        "channel": channel,
        "package": package,
        "activity": activity,
        "device": str(device.shell("getprop", "ro.product.manufacturer", check=False)).strip() + " " + str(device.shell("getprop", "ro.product.model", check=False)).strip(),
        "android": str(device.shell("getprop", "ro.build.version.release", check=False)).strip(),
        "wm_size": str(device.shell("wm", "size", check=False)).strip(),
        "wm_density": str(device.shell("wm", "density", check=False)).strip(),
        "foreground": str(device.shell("dumpsys", "window", "|", "grep", "mCurrentFocus", check=False)).strip(),
        "side_effects": side_effects,
        "apk_version_gate": version_summary,
        "requirement_doc": requirement_doc or "",
        "device_start_state": device_start_state or "",
        "package_gate_exception_accepted": bool(version_summary.get("accepted_risk")),
    }


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_") or "step"


def snapshot(driver: UIDriver, step_dir: Path, level: str, force: bool = False, failed: bool = False) -> dict[str, str]:
    step_dir.mkdir(parents=True, exist_ok=True)
    xml = driver.dump_xml()
    xml_path = step_dir / "ui.xml"
    summary_path = step_dir / "ui-summary.txt"
    xml_path.write_text(xml, encoding="utf-8")
    summary_path.write_text(summarize_xml(xml), encoding="utf-8")
    evidence = {"xml": str(xml_path), "summary": str(summary_path)}
    should_screenshot = level == "full" or force or failed or (level == "normal" and force)
    if should_screenshot:
        screenshot_path = step_dir / "screenshot.png"
        driver.screenshot(screenshot_path)
        evidence["screenshot"] = str(screenshot_path)
    if level == "full" or failed:
        logcat_path = step_dir / "logcat.txt"
        driver.logcat(logcat_path)
        evidence["logcat"] = str(logcat_path)
    return evidence


def decimal(value: str) -> float | None:
    m = re.search(r"-?\d+(?:\.\d+)?", value.replace(",", ""))
    return float(m.group(0)) if m else None


def market_rows(xml_text: str) -> list[dict[str, Any]]:
    nodes = parse_nodes(xml_text)
    rows: list[dict[str, Any]] = []
    for node in nodes:
        y = node.y1
        if not (550 <= y <= 2360):
            continue
        if re.search(r"([A-Z0-9]+\s*/\s*USDT|[A-Z0-9]+USDT)$", node.text):
            band = [n for n in nodes if y <= n.y1 <= y + 155 and n.text]
            vals = [n.text for n in band]
            numeric = [decimal(v) for v in vals if decimal(v) is not None]
            rows.append({"symbol": node.text.replace(" / ", "/"), "texts": vals, "numeric": numeric})
    return rows


def assert_sorted(xml_text: str, spec: dict[str, Any]) -> tuple[bool, str]:
    rows = market_rows(xml_text)
    if len(rows) < int(spec.get("min_rows", 3)):
        return False, f"Only parsed {len(rows)} market rows."
    key = spec.get("key", "symbol")
    order = spec.get("order", "asc")
    if key == "symbol":
        values = [row["symbol"] for row in rows[: int(spec.get("sample", 8))]]
        expected = sorted(values, reverse=(order == "desc"))
        ok = values == expected
        return ok, f"{key} values: {values[:8]} ({'ok' if ok else 'not ' + order})."
    index = {"volume": -3, "price": -2, "change": -1}.get(str(key), -1)
    values = []
    for row in rows[: int(spec.get("sample", 8))]:
        nums = row.get("numeric") or []
        if not nums:
            continue
        values.append(nums[index] if abs(index) <= len(nums) else nums[-1])
    if len(values) < int(spec.get("min_values", 3)):
        return False, f"Parsed too few values for {key}: {values}."
    tolerance = float(spec.get("tolerance", 0.0))
    inversions = []
    for left, right in zip(values, values[1:]):
        if order == "desc":
            bad = left + tolerance < right
        else:
            bad = left > right + tolerance
        if bad:
            inversions.append((left, right))
    max_inversions = int(spec.get("max_inversions", 0))
    ok = len(inversions) <= max_inversions
    detail = "ok" if ok else f"not {order}; inversions={inversions[:3]}"
    if tolerance:
        detail += f"; tolerance={tolerance}"
    return ok, f"{key} values: {values[:8]} ({detail})."


def assert_assets(xml_text: str, mode: str) -> tuple[bool, str]:
    vals = text_values(xml_text)
    if mode == "spot":
        symbols: list[str] = []
        for val in vals:
            if re.fullmatch(r"[A-Z0-9]{1,12}", val) and val not in {"USDT"} and val not in symbols:
                symbols.append(val)
        ok = len(symbols) >= 3 and "隐藏小额资产" in vals
        return ok, f"spot symbols: {symbols[:8]}; hide-small-assets={'隐藏小额资产' in vals}."
    required = ["总资产价值", "账户余额", "持仓保证金", "委托保证金", "未实现盈亏"]
    present = [r for r in required if r in vals]
    ok = len(present) >= 3
    return ok, f"asset metrics present: {present}."


def run_step(driver: UIDriver, flow_name: str, step: dict[str, Any], out_dir: Path, evidence_level: str, allow_side_effects: bool) -> StepResult:
    name = str(step.get("name") or step.get("action") or "step")
    action = str(step.get("action"))
    step_dir = out_dir / safe_name(flow_name) / safe_name(name)
    selector = step.get("selector") if isinstance(step.get("selector"), dict) else None
    try:
        notes: list[str] = []
        fallback = ""
        if action == "tap":
            if not selector:
                raise DriverError("tap requires selector")
            info = driver.tap_selector(selector, wait=float(step.get("wait", 1.0)))
            fallback = str(info.get("method", ""))
            notes.append(f"Tapped via {fallback}.")
        elif action == "input":
            value = str(step.get("value", ""))
            env_name = step.get("env")
            if env_name:
                value = os.environ.get(str(env_name), "")
                if not value:
                    raise DriverError(f"Missing required environment variable: {env_name}")
            driver.input_text(value, selector=selector)
            notes.append(f"Input text into selector; length={len(value)}.")
        elif action == "wait_text":
            driver.wait_until({"text": str(step["text"])}, timeout=float(step.get("timeout", 8)))
            notes.append(f"Text present: {step['text']}.")
        elif action == "assert_text":
            expected = step.get("any") or step.get("all") or []
            timeout = 0.02 if driver.device.dry_run else float(step.get("timeout", 3.0))
            deadline = time.time() + timeout
            last_vals: list[str] = []
            while True:
                xml = driver.dump_xml()
                vals = label_values(xml)
                last_vals = vals
                if step.get("all"):
                    missing = [v for v in expected if v not in vals]
                    if not missing:
                        break
                else:
                    if any(v in vals for v in expected):
                        break
                    missing = expected
                if time.time() >= deadline:
                    if step.get("all"):
                        raise DriverError(f"Missing expected text: {missing}; observed sample={last_vals[:20]}")
                    raise DriverError(f"None of expected texts found: {expected}; observed sample={last_vals[:20]}")
                time.sleep(0.02 if driver.device.dry_run else 0.4)
            notes.append(f"Text assertion passed: {expected}.")
        elif action == "assert_sorted":
            if driver.device.dry_run:
                notes.append(f"Dry-run: skipped strict {step.get('key', 'symbol')} sorting assertion.")
            else:
                ok, note = assert_sorted(driver.dump_xml(), step)
                if not ok and not step.get("non_blocking"):
                    raise DriverError(note)
                notes.append(note)
        elif action == "assert_assets":
            if driver.device.dry_run:
                notes.append(f"Dry-run: skipped strict asset assertion for {step.get('mode', 'overview')}.")
            else:
                ok, note = assert_assets(driver.dump_xml(), str(step.get("mode", "overview")))
                if not ok:
                    raise DriverError(note)
                notes.append(note)
        elif action == "snapshot":
            notes.append("Snapshot captured.")
        elif action == "ux_snapshot":
            notes.append(f"UX/UI screenshot checkpoint: {step.get('label', name)}.")
        elif action == "sleep":
            time.sleep(0.02 if driver.device.dry_run else float(step.get("seconds", 1)))
            notes.append(f"Slept {step.get('seconds', 1)}s.")
        elif action == "tap_xy":
            target = step.get("coordinate") or step.get("xy")
            if not isinstance(target, list) or len(target) != 2:
                raise DriverError("tap_xy requires coordinate: [x, y]")
            driver.tap_xy(int(target[0]), int(target[1]), wait=float(step.get("wait", 1.0)))
            fallback = "coordinate"
            notes.append(f"Tapped coordinate {target}.")
        elif action == "swipe":
            start = step.get("start")
            end = step.get("end")
            if not isinstance(start, list) or len(start) != 2 or not isinstance(end, list) or len(end) != 2:
                raise DriverError("swipe requires start: [x, y] and end: [x, y]")
            driver.swipe_xy(int(start[0]), int(start[1]), int(end[0]), int(end[1]), duration_ms=int(step.get("duration_ms", 300)), wait=float(step.get("wait", 1.0)))
            fallback = "gesture"
            notes.append(f"Swiped from {start} to {end}.")
        elif action == "keyevent":
            keycode = step.get("keycode")
            if keycode is None:
                raise DriverError("keyevent requires keycode")
            driver.keyevent(keycode, wait=float(step.get("wait", 1.0)))
            notes.append(f"Sent keyevent {keycode}.")
        elif action == "safety_gate":
            if step.get("requires_side_effect") and not allow_side_effects:
                raise DriverError("Safety gate blocked side-effect step. Pass --allow-side-effects only after explicit user confirmation.")
            notes.append("Safety gate passed without side effects." if not step.get("requires_side_effect") else "Safety gate requires final human confirmation before execution.")
        else:
            raise DriverError(f"Unsupported action: {action}")
        evidence = snapshot(driver, step_dir, evidence_level, force=bool(step.get("snapshot")))
        return StepResult(flow_name, name, action, "pass", notes=notes, selector=selector, evidence=evidence, fallback=fallback)
    except Exception as exc:
        evidence = snapshot(driver, step_dir, evidence_level, failed=True)
        category = str(step.get("failure_category", "automation_issue"))
        bug_candidate = bool(step.get("bug_candidate", False)) and category == "product_bug"
        return StepResult(flow_name, name, action, "fail", category=category, bug_candidate=bug_candidate, notes=[str(exc)], selector=selector, evidence=evidence)


def run_flow(driver: UIDriver, flow_path: Path, out_dir: Path, evidence_level: str, allow_side_effects: bool) -> list[StepResult]:
    flow = load_yaml(flow_path)
    flow_name = str(flow.get("name") or flow_path.stem)
    results: list[StepResult] = []
    for step in flow.get("steps", []):
        if not isinstance(step, dict):
            continue
        result = run_step(driver, flow_name, step, out_dir, evidence_level, allow_side_effects)
        results.append(result)
        if result.status != "pass" and not step.get("continue_on_failure", False):
            break
    return results


def bug_template(results: list[StepResult], out_dir: Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for r in results:
        if not r.bug_candidate:
            continue
        attachments = [v for k, v in r.evidence.items() if k in {"screenshot", "xml", "logcat", "summary"}]
        items.append({
            "confirmed": False,
            "bug_candidate": True,
            "category": r.category,
            "title": f"[Android][OneBullEx dev] {r.flow}/{r.step} failed",
            "module": "/",
            "affected_version": "",
            "bug_type": "代码错误",
            "severity": 3,
            "priority": 3,
            "steps": [f"Run flow {r.flow}", f"Step {r.step}: {r.action}"],
            "actual": "; ".join(r.notes),
            "expected": "Step should match the documented OneBullEx requirement.",
            "attachments": attachments,
            "source_report": str(out_dir / REPORT_NAME),
        })
    if not items:
        items.append({
            "confirmed": False,
            "bug_candidate": False,
            "category": "manual_placeholder",
            "title": "[Android][OneBullEx dev] Replace with confirmed product bug title",
            "module": "/",
            "affected_version": "",
            "bug_type": "代码错误",
            "severity": 3,
            "priority": 3,
            "steps": ["1. Replace with reproduction step"],
            "actual": "Replace with actual result.",
            "expected": "Replace with expected result.",
            "attachments": [],
            "source_report": str(out_dir / REPORT_NAME),
        })
    return items


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def snapshot_flows_used(out_dir: Path, flow_paths: list[Path]) -> list[dict[str, Any]]:
    flows_dir = out_dir / FLOWS_USED_DIR_NAME
    flows_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    for index, path in enumerate(flow_paths, start=1):
        flow = load_yaml(path)
        flow_name = str(flow.get("name") or path.stem)
        target = flows_dir / f"{index:02d}-{safe_name(flow_name)}.yaml"
        shutil.copy2(path, target)
        steps = flow.get("steps", [])
        records.append({
            "flow": flow_name,
            "source_path": str(path),
            "snapshot_path": str(target),
            "sha256": sha256_file(path),
            "step_count": len(steps) if isinstance(steps, list) else 0,
        })
    return records


def build_learning_candidates(env: dict[str, Any], results: list[StepResult], flow_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()

    def add(kind: str, title: str, recommendation: str, result: StepResult | None = None, target: str = "") -> None:
        key = (kind, result.flow if result else target, result.step if result else title)
        if key in seen:
            return
        seen.add(key)
        evidence = result.evidence if result else {}
        candidates.append({
            "id": f"learn-{len(candidates) + 1:03d}",
            "type": kind,
            "confirmed": False,
            "title": title,
            "flow": result.flow if result else "",
            "step": result.step if result else "",
            "status": result.status if result else "",
            "category": result.category if result else "",
            "recommendation": recommendation,
            "target": target,
            "evidence": evidence,
            "human_notes": "",
        })

    for record in flow_records:
        add(
            "flow_update",
            f"Review flow snapshot for {record['flow']}",
            "If this run produced a stable path, compare the snapshot with the source flow before promoting changes.",
            target=str(record.get("snapshot_path", "")),
        )

    for result in results:
        if result.fallback == "coordinate" or result.action in {"tap_xy", "swipe"}:
            add(
                "selector_update",
                f"Replace coordinate fallback in {result.flow}/{result.step}",
                "Ask Android to expose a stable resource-id/content-desc, then update the flow selector and keep coordinates only as fallback.",
                result,
                target=f"flows/{result.flow}.yaml",
            )
        if result.status == "fail" and result.category in {"automation_issue", "environment_blocker", "requirement_unclear"}:
            add(
                result.category,
                f"Classify non-product failure in {result.flow}/{result.step}",
                "Confirm whether this is repeatable. If yes, improve the flow, driver, requirement note, or environment checklist instead of filing a product bug.",
                result,
                target="references/qa-learning-loop.md",
            )

    gate = env.get("apk_version_gate")
    if isinstance(gate, dict) and gate.get("status") in {"unknown", "outdated", "not_installed", "skipped"}:
        add(
            "environment_note",
            f"Record APK gate status: {gate.get('status')}",
            "Keep this as an execution-confidence note unless the package source or install flow itself needs improvement.",
            target="references/package-version-gate.md",
        )

    add(
        "cursor_sync_note",
        "Sync confirmed QA Skill changes to Cursor mirror",
        "After confirmed source changes are written, run scripts/sync-onebullex-android-qa-skill.sh so Cursor and Codex use the same Skill.",
        target="/Users/jingxing/Desktop/Onebullex/.cursor/skills/onebullex-android-qa",
    )
    return candidates


def write_learning_artifacts(out_dir: Path, report_json: dict[str, Any], results: list[StepResult], flow_records: list[dict[str, Any]]) -> dict[str, str]:
    candidates = build_learning_candidates(report_json.get("environment", {}), results, flow_records)
    candidates_path = out_dir / OPTIMIZATION_CANDIDATES_NAME
    confirm_path = out_dir / OPTIMIZATION_CONFIRM_NAME
    summary_path = out_dir / EXPERIENCE_SUMMARY_NAME

    payload = {
        "generated": report_json["generated"],
        "evidence_dir": str(out_dir),
        "source_report": str(out_dir / REPORT_JSON_NAME),
        "flows_used": flow_records,
        "candidates": candidates,
    }
    candidates_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    confirm_payload = {
        "instructions": "Set confirmed=true only for learning items that should be used to update the QA Skill. Leave product bugs for Zentao review.",
        "source_candidates": str(candidates_path),
        "candidates": candidates,
    }
    confirm_path.write_text(json.dumps(confirm_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    counts = report_json.get("summary", {})
    fallback_steps = [f"{r.flow}/{r.step}" for r in results if r.fallback == "coordinate" or r.action in {"tap_xy", "swipe"}]
    failed = [r for r in results if r.status == "fail"]
    lines = [
        "# QA Skill Experience Summary\n",
        f"- Generated: {report_json['generated']}\n",
        f"- Evidence directory: `{out_dir}`\n",
        f"- Source report: `{out_dir / REPORT_JSON_NAME}`\n",
        f"- Result: {counts.get('pass', 0)} pass, {counts.get('fail', 0)} fail\n",
        "\n## Flows Used\n",
    ]
    for record in flow_records:
        lines.append(f"- `{record['flow']}`: {record['step_count']} steps, sha256 `{record['sha256'][:12]}`, snapshot `{record['snapshot_path']}`\n")
    lines.append("\n## Reusable Experience\n")
    if fallback_steps:
        lines.append(f"- Coordinate or gesture fallback steps need selector hardening: `{', '.join(fallback_steps[:12])}`.\n")
    else:
        lines.append("- No coordinate fallback was recorded in this run.\n")
    if failed:
        for result in failed[:10]:
            lines.append(f"- `{result.flow}/{result.step}` failed as `{result.category or 'unknown'}`: {'; '.join(result.notes[:2])}\n")
    else:
        lines.append("- No failed steps were recorded.\n")
    lines.append("\n## Human Confirmation\n")
    lines.append(f"- Review candidates in `{confirm_path}`.\n")
    lines.append("- Confirm only stable flow, selector, documentation, or environment learnings.\n")
    lines.append("- Product bugs stay in `confirmed-bugs.template.json` and follow the Zentao confirmation flow.\n")
    summary_path.write_text("".join(lines), encoding="utf-8")

    return {
        "experience_summary": str(summary_path),
        "optimization_candidates": str(candidates_path),
        "optimization_confirm_template": str(confirm_path),
        "flows_used_dir": str(out_dir / FLOWS_USED_DIR_NAME),
    }


def write_reports(out_dir: Path, env: dict[str, Any], setup_notes: list[str], results: list[StepResult], flow_paths: list[Path]) -> tuple[Path, Path]:
    counts = {s: sum(1 for r in results if r.status == s) for s in ["pass", "fail"]}
    flow_records = snapshot_flows_used(out_dir, flow_paths)
    report_json = {
        "generated": dt.datetime.now().isoformat(timespec="seconds"),
        "environment": env,
        "setup_notes": setup_notes,
        "summary": counts,
        "flows_used": flow_records,
        "results": [r.to_dict() for r in results],
    }
    learning_paths = write_learning_artifacts(out_dir, report_json, results, flow_records)
    report_json["learning_artifacts"] = learning_paths
    json_path = out_dir / REPORT_JSON_NAME
    json_path.write_text(json.dumps(report_json, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# OneBullEx Android QA Report\n", f"- Generated: {report_json['generated']}\n", f"- Evidence directory: `{out_dir}`\n", f"- Summary: {counts.get('pass', 0)} pass, {counts.get('fail', 0)} fail\n", f"- Report JSON: `{json_path}`\n"]
    lines.append("\n## Environment\n")
    for k, v in env.items():
        if k == "apk_version_gate" and isinstance(v, dict):
            continue
        lines.append(f"- {k}: `{v}`\n")
    gate = env.get("apk_version_gate")
    if isinstance(gate, dict):
        lines.append("\n## APK Version Gate\n")
        for key in ["status", "channel", "package", "serial", "device_version_name", "device_version_code", "remote_version_name", "remote_version_code", "apk_url", "recommended_action", "accepted_risk"]:
            if key in gate:
                lines.append(f"- {key}: `{gate.get(key)}`\n")
    lines.append("\n## Setup Notes\n")
    for note in setup_notes:
        lines.append(f"- {note}\n")
    watch_monitor_results = [r for r in results if r.flow.startswith("watch-monitor-")]
    if watch_monitor_results:
        fallback_steps = [f"{r.flow}/{r.step}" for r in watch_monitor_results if r.fallback == "coordinate"]
        lines.append("\n## Watch Monitor Summary\n")
        if env.get("requirement_doc"):
            lines.append(f"- Requirement source: `{env['requirement_doc']}`\n")
        lines.append(f"- Executed watch-monitor steps: `{len(watch_monitor_results)}`\n")
        lines.append(f"- Package gate exception accepted: `{env.get('package_gate_exception_accepted', False)}`\n")
        lines.append(f"- Overlay finding: `SYSTEM_ALERT_WINDOW was required for this run; cross-app evidence is screenshot-based.`\n")
        lines.append(f"- Selector fallback risks: `{', '.join(fallback_steps[:8]) if fallback_steps else 'none recorded'}`\n")
    lines.append("\n## Test Matrix\n")
    lines.append("| Flow | Step | Action | Status | Category | Notes | Evidence |\n")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |\n")
    for r in results:
        ev = " ".join(f"[{k}]({Path(v).as_posix()})" for k, v in r.evidence.items() if k in {"screenshot", "summary", "xml"})
        notes = "<br>".join(n.replace("|", "\\|") for n in r.notes[:3])
        lines.append(f"| {r.flow} | {r.step} | {r.action} | {r.status} | {r.category or '-'} | {notes} | {ev} |\n")
    lines.append("\n## Bug Review\n")
    lines.append(f"- Product bug candidates only are written to `{out_dir / BUG_TEMPLATE_NAME}`.\n")
    lines.append("- Automation/environment/requirement issues are evidence for Skill improvement, not default Zentao bugs.\n")
    lines.append("\n## Skill Learning Review\n")
    lines.append(f"- Experience summary: `{learning_paths['experience_summary']}`.\n")
    lines.append(f"- Optimization candidates: `{learning_paths['optimization_candidates']}`.\n")
    lines.append(f"- Human confirmation template: `{learning_paths['optimization_confirm_template']}`.\n")
    lines.append(f"- Flow snapshots: `{learning_paths['flows_used_dir']}`.\n")
    md_path = out_dir / REPORT_NAME
    md_path.write_text("".join(lines), encoding="utf-8")
    (out_dir / BUG_TEMPLATE_NAME).write_text(json.dumps(bug_template(results, out_dir), ensure_ascii=False, indent=2), encoding="utf-8")
    return md_path, json_path


def main() -> int:
    args = parse_args()
    require_adb(args.dry_run)
    serial = choose_serial(args.serial, args.wireless, args.dry_run)
    package = package_for_channel(args.channel, args.package)
    run_name = args.run_name or dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = Path(args.out_dir).expanduser() / run_name
    out_dir.mkdir(parents=True, exist_ok=True)
    version_gate, gate_notes = run_version_gate(args, serial, package, out_dir)
    if args.version_check_only:
        print(f"APK version check: {out_dir / 'apk-version-check.json'}")
        return 0 if args.dry_run or (version_gate or {}).get("status") == "latest" else 10
    device = AdbDevice(serial, dry_run=args.dry_run)
    setup_notes = gate_notes + prepare_device(device, package, args.activity, args.no_launch, args.force_stop_before_launch)
    env = collect_environment(
        device,
        args.channel,
        package,
        args.activity,
        "allowed-with-gate" if args.allow_side_effects else "none",
        version_gate,
        args.requirement_doc,
        args.device_start_state,
    )
    driver = UIDriver(device, out_dir)
    all_results: list[StepResult] = []
    flow_paths = resolve_flows(args.flow)
    for flow_path in flow_paths:
        all_results.extend(run_flow(driver, flow_path, out_dir, args.evidence_level, args.allow_side_effects))
    md_path, _ = write_reports(out_dir, env, setup_notes, all_results, flow_paths)
    print(f"Report: {md_path}")
    print(f"Bug template: {out_dir / BUG_TEMPLATE_NAME}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except DriverError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
