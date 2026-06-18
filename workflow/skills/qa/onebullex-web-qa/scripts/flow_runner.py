#!/usr/bin/env python3
"""Run OneBullEx Web QA YAML flows in dry-run/report mode."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except Exception:
    yaml = None

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from browser_driver import BrowserDriver, BrowserDriverError

SKILL_DIR = SCRIPT_DIR.parent
FLOWS_DIR = SKILL_DIR / "flows"
ROUTES_DIR = SKILL_DIR / "routes"
REPORT_NAME = "onebullex-web-qa-report.md"
REPORT_JSON_NAME = "onebullex-web-qa-report.json"
BUG_TEMPLATE_NAME = "confirmed-bugs.template.json"
EXPERIENCE_SUMMARY_NAME = "qa-experience-summary.md"
OPTIMIZATION_CANDIDATES_NAME = "qa-skill-optimization-candidates.json"
OPTIMIZATION_CONFIRM_NAME = "qa-skill-optimization-confirm.template.json"
FLOWS_USED_DIR_NAME = "flows-used"
ACCOUNT_PROFILES = {"guest", "basic-login", "funded-spot", "funded-futures", "open-orders", "open-position", "withdraw-capable"}
BROWSER_MODES = {"iab", "chrome", "any"}
SIDE_EFFECTS = {"none", "auth-only", "blocked-by-default", "testnet-submit", "withdraw-probe-only"}
RUNTIMES = {"codex", "playwright"}


class FlowError(RuntimeError):
    pass


@dataclass
class StepResult:
    flow: str
    step: str
    action: str
    status: str
    category: str = ""
    bug_candidate: bool = False
    notes: list[str] = field(default_factory=list)
    route: str = ""
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
            "route": self.route,
            "selector": self.selector,
            "evidence": self.evidence,
            "fallback": self.fallback,
        }


def load_yaml(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text) if yaml else json.loads(text)
    if not isinstance(data, dict):
        raise FlowError(f"YAML/JSON must be a mapping: {path}")
    return data


def load_routes(routes_dir: Path = ROUTES_DIR) -> dict[str, dict[str, Any]]:
    routes: dict[str, dict[str, Any]] = {}
    if not routes_dir.exists():
        return routes
    for path in sorted(routes_dir.glob("*.yaml")):
        if path.name.startswith("_"):
            continue
        data = load_yaml(path)
        feature = str(data.get("feature") or path.stem.replace("-", "_"))
        for name, entry in (data.get("elements") or {}).items():
            if isinstance(entry, dict):
                item = dict(entry)
                item["_route_key"] = f"{feature}.{name}"
                item["_route_file"] = str(path)
                routes[item["_route_key"]] = item
    return routes


def resolve_route(ref: str, routes: dict[str, dict[str, Any]]) -> dict[str, Any]:
    if ref in routes:
        return routes[ref]
    matches = [v for k, v in routes.items() if k.endswith("." + ref)]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise FlowError(f"Route not found: {ref}")
    raise FlowError(f"Ambiguous route {ref}: {[m['_route_key'] for m in matches]}")


def resolve_step(step: dict[str, Any], routes: dict[str, dict[str, Any]], base_url: str) -> tuple[dict[str, Any], str]:
    if "route" not in step:
        resolved = dict(step)
        if "url" in resolved:
            resolved["url"] = absolutize_url(str(resolved["url"]), base_url)
        return resolved, ""
    route = resolve_route(str(step["route"]), routes)
    resolved = dict(step)
    if "selector" not in resolved and isinstance(route.get("selector"), dict):
        resolved["selector"] = route["selector"]
    if "url" not in resolved and route.get("url"):
        resolved["url"] = absolutize_url(str(route["url"]), base_url)
    if "fallback_xy" not in resolved and isinstance(route.get("fallback_xy"), list):
        resolved["fallback_xy"] = route["fallback_xy"]
    return resolved, str(route.get("_route_key") or step["route"])


def absolutize_url(url: str, base_url: str) -> str:
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return base_url.rstrip("/") + "/" + url.lstrip("/")


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_") or "step"


def resolve_flows(flow_arg: str) -> list[Path]:
    groups = {
        "all-public": ["env-health-check.yaml", "smoke-public.yaml", "market-data.yaml", "desktop-mobile-consistency.yaml"],
        "all-auth": ["env-health-check.yaml", "account-state.yaml", "assets-orders-positions.yaml", "spot-trade-dry-run.yaml", "futures-trade-dry-run.yaml"],
        "withdraw-address-book": [
            "env-health-check.yaml",
            "withdraw-address-book-entry.yaml",
            "withdraw-address-book-validation.yaml",
            "withdraw-address-book-create-edit-delete.yaml",
            "withdraw-address-book-withdraw-link.yaml",
            "withdraw-address-book-ux-ui.yaml"
        ],
        "all": ["env-health-check.yaml", "smoke-public.yaml", "market-data.yaml", "account-state.yaml", "assets-orders-positions.yaml"],
    }
    if flow_arg in groups:
        return [FLOWS_DIR / name for name in groups[flow_arg]]
    path = Path(flow_arg).expanduser()
    if path.exists():
        return [path]
    if not flow_arg.endswith(".yaml"):
        flow_arg += ".yaml"
    path = FLOWS_DIR / flow_arg
    if not path.exists():
        raise FlowError(f"Flow not found: {flow_arg}")
    return [path]


def run_step(driver: BrowserDriver, flow_name: str, step: dict[str, Any], route_key: str, out_dir: Path, evidence_level: str, allow_side_effects: bool, confirm_submit: bool) -> StepResult:
    name = str(step.get("name") or step.get("action") or "step")
    action = str(step.get("action"))
    selector = step.get("selector") if isinstance(step.get("selector"), dict) else None
    step_dir = out_dir / safe_name(flow_name) / safe_name(name)
    notes: list[str] = []
    fallback = ""
    try:
        if action == "goto":
            obs = driver.goto(str(step.get("url") or "/"))
            if not obs.ok:
                raise FlowError(obs.note)
            notes.append(obs.note)
        elif action == "click":
            if not selector:
                raise FlowError("click requires selector or route")
            obs = driver.click(selector)
            if not obs.ok:
                raise FlowError(obs.note)
            notes.append(obs.note)
        elif action == "type":
            if not selector:
                raise FlowError("type requires selector or route")
            value = str(step.get("value", ""))
            if value.startswith("env:"):
                value = os.environ.get(value.split(":", 1)[1], "")
                if not value:
                    raise FlowError(f"Missing environment variable for {step.get('value')}")
            obs = driver.type_text(selector, value)
            if not obs.ok:
                raise FlowError(obs.note)
            notes.append(obs.note)
        elif action == "wait_for":
            obs = driver.wait_for(selector, int(step.get("ms", 0)) or None)
            if not obs.ok:
                raise FlowError(obs.note)
            notes.append(obs.note)
        elif action == "ensure_locale":
            obs = driver.assert_text(expected_any=[str(v) for v in step.get("signals", [])])
            if not obs.ok:
                raise FlowError(obs.note)
            notes.append(obs.note)
        elif action == "assert_text":
            obs = driver.assert_text(expected_any=[str(v) for v in step.get("any", [])] or None, expected_all=[str(v) for v in step.get("all", [])] or None)
            if not obs.ok:
                raise FlowError(obs.note)
            notes.append(obs.note)
        elif action == "assert_url":
            obs = driver.assert_url(str(step.get("pattern", "")))
            if not obs.ok:
                raise FlowError(obs.note)
            notes.append(obs.note)
        elif action == "assert_visible":
            if not selector:
                raise FlowError("assert_visible requires selector or route")
            obs = driver.assert_visible(selector)
            if not obs.ok:
                raise FlowError(obs.note)
            notes.append(obs.note)
        elif action == "assert_not_visible":
            if not selector:
                raise FlowError("assert_not_visible requires selector or route")
            obs = driver.assert_not_visible(selector)
            if not obs.ok and not step.get("non_blocking"):
                raise FlowError(obs.note)
            notes.append(obs.note)
        elif action in {"assert_table_sort", "assert_balance_block", "assert_order_state", "assert_position_state", "assert_history_row", "assert_toast", "assert_api_response"}:
            notes.append(f"Dry-run structural check for {action}; live verification uses Browser/Chrome plugin observations.")
        elif action == "assert_ws_freshness":
            notes.append(f"Dry-run skipped live WS probe; freshness_window_ms={step.get('freshness_window_ms', 5000)}.")
        elif action == "assert_numeric_delta":
            if not allow_side_effects:
                raise FlowError("assert_numeric_delta requires --allow-side-effects because it verifies state change.")
            notes.append("Dry-run numeric delta placeholder.")
        elif action == "assert_account_profile":
            notes.append(f"Dry-run account profile probe expected {step.get('profile')}.")
        elif action in {"snapshot", "ux_snapshot"}:
            notes.append(f"Evidence checkpoint: {step.get('label', name)}.")
        elif action == "sleep":
            notes.append(f"Dry-run sleep {step.get('ms', 0)}ms.")
        elif action == "safety_gate":
            if step.get("requires_side_effect") and not allow_side_effects:
                raise FlowError("Safety gate blocked side-effect step. Pass --allow-side-effects only after explicit user confirmation.")
            if step.get("requires_confirm_submit") and not confirm_submit:
                raise FlowError("Safety gate blocked final submit. Pass --confirm-submit only after explicit user confirmation.")
            notes.append("Safety gate passed.")
        else:
            raise FlowError(f"Unsupported action: {action}")
        if selector and selector.get("fallback_xy"):
            fallback = "coordinate"
        force_shot = evidence_level == "full" or bool(step.get("snapshot")) or action == "ux_snapshot"
        evidence = driver.snapshot(step_dir, str(step.get("label") or name), force_screenshot=force_shot)
        return StepResult(flow_name, name, action, "pass", notes=notes, route=route_key, selector=selector, evidence=evidence, fallback=fallback)
    except Exception as exc:
        evidence = driver.snapshot(step_dir, str(step.get("label") or name), force_screenshot=True)
        category = str(step.get("failure_category", "automation_issue"))
        bug_candidate = bool(step.get("bug_candidate")) and category == "product_bug"
        status = "blocked" if category in {"environment_blocker", "service_degradation", "requirement_unclear"} else "fail"
        return StepResult(flow_name, name, action, status, category=category, bug_candidate=bug_candidate, notes=[str(exc)], route=route_key, selector=selector, evidence=evidence, fallback=fallback)


def _execute_flow_variant(
    flow: dict[str, Any],
    flow_path: Path,
    out_dir: Path,
    args: argparse.Namespace,
    viewport: str,
    flow_name: str,
) -> tuple[list[StepResult], dict[str, Any]]:
    routes = load_routes()
    browser_mode = args.browser_mode or str(flow.get("browser_mode", "iab"))
    locale = args.locale or str(flow.get("locale", "zh-cn"))
    driver = BrowserDriver(
        browser_mode=browser_mode,
        viewport=viewport,
        locale=locale,
        runtime=args.runtime,
        dry_run=args.dry_run,
        out_dir=out_dir,
        session_name=f"{safe_name(flow_name)}-{browser_mode}-{viewport}",
    )
    results: list[StepResult] = []
    base_url = str(flow.get("base_url") or args.base_url)
    for raw_step in flow.get("steps", []):
        if not isinstance(raw_step, dict):
            continue
        step, route_key = resolve_step(raw_step, routes, base_url)
        result = run_step(driver, flow_name, step, route_key, out_dir, args.evidence_level, args.allow_side_effects, args.confirm_submit)
        results.append(result)
        if result.status not in {"pass"} and not raw_step.get("continue_on_failure"):
            break
    metadata = {
        "flow": flow_name,
        "base_flow": str(flow.get("name") or flow_path.stem),
        "path": str(flow_path),
        "browser_mode": browser_mode,
        "viewport": viewport,
        "locale": locale,
        "required_account_profile": flow.get("required_account_profile", "guest"),
        "required_start_state": flow.get("required_start_state", ""),
        "requires_health_gate": bool(flow.get("requires_health_gate", False)),
        "side_effects": flow.get("side_effects", "none"),
        "public_only": bool(flow.get("public_only", False)),
    }
    return results, metadata


def run_flow(flow_path: Path, out_dir: Path, args: argparse.Namespace) -> tuple[list[StepResult], list[dict[str, Any]]]:
    flow = load_yaml(flow_path)
    flow_name = str(flow.get("name") or flow_path.stem)
    viewport = args.viewport or str(flow.get("viewport", "desktop"))
    if viewport == "both":
        all_results: list[StepResult] = []
        all_meta: list[dict[str, Any]] = []
        for variant in ("desktop", "mobile"):
            variant_name = f"{flow_name}[{variant}]"
            results, metadata = _execute_flow_variant(flow, flow_path, out_dir, args, variant, variant_name)
            all_results.extend(results)
            all_meta.append(metadata)
        return all_results, all_meta
    results, metadata = _execute_flow_variant(flow, flow_path, out_dir, args, viewport, flow_name)
    return results, [metadata]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def snapshot_flows_used(out_dir: Path, flow_paths: list[Path]) -> list[dict[str, Any]]:
    dest = out_dir / FLOWS_USED_DIR_NAME
    dest.mkdir(parents=True, exist_ok=True)
    records = []
    for i, path in enumerate(flow_paths, 1):
        flow = load_yaml(path)
        name = str(flow.get("name") or path.stem)
        target = dest / f"{i:02d}-{safe_name(name)}.yaml"
        shutil.copy2(path, target)
        records.append({"flow": name, "source_path": str(path), "snapshot_path": str(target), "sha256": sha256_file(path), "step_count": len(flow.get("steps", []))})
    return records


def bug_template(results: list[StepResult], out_dir: Path) -> list[dict[str, Any]]:
    items = []
    for r in results:
        if not r.bug_candidate:
            continue
        items.append({
            "confirmed": False,
            "bug_candidate": True,
            "category": r.category,
            "title": f"[Web][OneBullEx testnet] {r.flow}/{r.step} failed",
            "module": "/",
            "affected_version": "testnet",
            "bug_type": "代码错误",
            "severity": 3,
            "priority": 3,
            "steps": [f"Run flow {r.flow}", f"Step {r.step}: {r.action}"],
            "actual": "; ".join(r.notes),
            "expected": "Step should match the documented OneBullEx Web requirement.",
            "attachments": list(r.evidence.values()),
            "source_report": str(out_dir / REPORT_NAME),
        })
    if not items:
        items.append({"confirmed": False, "bug_candidate": False, "category": "manual_placeholder", "title": "[Web][OneBullEx testnet] Replace with confirmed product bug title", "module": "/", "affected_version": "testnet", "bug_type": "代码错误", "severity": 3, "priority": 3, "steps": ["1. Replace with reproduction step"], "actual": "Replace with actual result.", "expected": "Replace with expected result.", "attachments": [], "source_report": str(out_dir / REPORT_NAME)})
    return items


def learning_candidates(env: dict[str, Any], results: list[StepResult], flow_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    def add(kind: str, title: str, recommendation: str, result: StepResult | None = None, target: str = "") -> None:
        candidates.append({"id": f"learn-{len(candidates)+1:03d}", "type": kind, "confirmed": False, "title": title, "flow": result.flow if result else "", "step": result.step if result else "", "status": result.status if result else "", "category": result.category if result else "", "recommendation": recommendation, "target": target, "evidence": result.evidence if result else {}, "human_notes": ""})
    for record in flow_records:
        add("flow_update", f"Review flow snapshot for {record['flow']}", "If this run produced a stable path, compare the snapshot with the source flow before promoting changes.", target=str(record.get("snapshot_path", "")))
    for result in results:
        if result.fallback == "coordinate" or (result.selector and result.selector.get("fallback_xy")):
            add("selector_update", f"Replace fallback selector in {result.flow}/{result.step}", "Ask Web developers to expose a stable data-testid, then update routes/flows.", result, target="routes/")
        if result.status in {"blocked", "fail"} and result.category in {"automation_issue", "environment_blocker", "service_degradation", "requirement_unclear"}:
            add(result.category, f"Classify non-product failure in {result.flow}/{result.step}", "Confirm repeatability. Improve flow, route, health gate, browser strategy, or requirement note instead of filing a product bug.", result, target="references/qa-learning-loop.md")
    add("cursor_sync_note", "Sync confirmed Web QA Skill changes to mirrors", "After confirmed source changes are written, run scripts/sync-onebullex-web-qa-skill.sh.", target="~/.codex/skills/onebullex-web-qa and .cursor/skills/onebullex-web-qa")
    return candidates


def write_reports(out_dir: Path, env: dict[str, Any], setup_notes: list[str], results: list[StepResult], flow_paths: list[Path], flow_metadata: list[dict[str, Any]]) -> tuple[Path, Path]:
    counts = {s: sum(1 for r in results if r.status == s) for s in ["pass", "fail", "blocked"]}
    flow_records = snapshot_flows_used(out_dir, flow_paths)
    report_json = {"generated": dt.datetime.now().isoformat(timespec="seconds"), "environment": env, "setup_notes": setup_notes, "summary": counts, "flow_metadata": flow_metadata, "flows_used": flow_records, "results": [r.to_dict() for r in results]}
    candidates = learning_candidates(env, results, flow_records)
    cand_path = out_dir / OPTIMIZATION_CANDIDATES_NAME
    confirm_path = out_dir / OPTIMIZATION_CONFIRM_NAME
    exp_path = out_dir / EXPERIENCE_SUMMARY_NAME
    cand_payload = {"generated": report_json["generated"], "evidence_dir": str(out_dir), "source_report": str(out_dir / REPORT_JSON_NAME), "flows_used": flow_records, "candidates": candidates}
    cand_path.write_text(json.dumps(cand_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    confirm_path.write_text(json.dumps({"instructions": "Set confirmed=true only for learning items that should update the Web QA Skill. Product bugs stay in confirmed-bugs.template.json.", "source_candidates": str(cand_path), "candidates": candidates}, ensure_ascii=False, indent=2), encoding="utf-8")
    exp_lines = ["# QA Skill Experience Summary\n", f"- Generated: {report_json['generated']}\n", f"- Evidence directory: `{out_dir}`\n", f"- Result: {counts.get('pass',0)} pass, {counts.get('fail',0)} fail, {counts.get('blocked',0)} blocked\n", "\n## Flows Used\n"]
    for rec in flow_records:
        exp_lines.append(f"- `{rec['flow']}`: {rec['step_count']} steps, sha256 `{rec['sha256'][:12]}`, snapshot `{rec['snapshot_path']}`\n")
    exp_lines.append("\n## Human Confirmation\n- Review `qa-skill-optimization-confirm.template.json` before applying learnings.\n")
    exp_path.write_text("".join(exp_lines), encoding="utf-8")
    report_json["learning_artifacts"] = {"experience_summary": str(exp_path), "optimization_candidates": str(cand_path), "optimization_confirm_template": str(confirm_path), "flows_used_dir": str(out_dir / FLOWS_USED_DIR_NAME)}
    json_path = out_dir / REPORT_JSON_NAME
    json_path.write_text(json.dumps(report_json, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# OneBullEx Web QA Report\n", f"- Generated: {report_json['generated']}\n", f"- Evidence directory: `{out_dir}`\n", f"- Summary: {counts.get('pass',0)} pass, {counts.get('fail',0)} fail, {counts.get('blocked',0)} blocked\n", f"- Report JSON: `{json_path}`\n", "\n## Environment\n"]
    for k, v in env.items():
        lines.append(f"- {k}: `{v}`\n")
    lines.append("\n## Setup Notes\n")
    for note in setup_notes:
        lines.append(f"- {note}\n")
    lines.append("\n## Test Matrix\n| Flow | Step | Action | Status | Category | Notes | Evidence |\n| --- | --- | --- | --- | --- | --- | --- |\n")
    for r in results:
        ev = " ".join(f"[{k}]({Path(v).as_posix()})" for k, v in r.evidence.items())
        notes = "<br>".join(n.replace("|", "\\|") for n in r.notes[:3])
        lines.append(f"| {r.flow} | {r.step} | {r.action} | {r.status} | {r.category or '-'} | {notes} | {ev} |\n")
    lines.append("\n## Page vs Result Verification\n- Trading flows must pair page-state evidence with order/position/history/balance result-state evidence before product conclusions are trusted.\n")
    lines.append("\n## Suspected Bugs For Human Review\n")
    lines.append(f"- Product bug candidates are written to `{out_dir / BUG_TEMPLATE_NAME}` and require manual confirmation.\n")
    lines.append("\n## Skill Learning Review\n")
    for label, path in report_json["learning_artifacts"].items():
        lines.append(f"- {label}: `{path}`\n")
    md_path = out_dir / REPORT_NAME
    md_path.write_text("".join(lines), encoding="utf-8")
    (out_dir / BUG_TEMPLATE_NAME).write_text(json.dumps(bug_template(results, out_dir), ensure_ascii=False, indent=2), encoding="utf-8")
    return md_path, json_path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run OneBullEx Web QA flows.")
    p.add_argument("--flow", default="smoke-public.yaml")
    p.add_argument("--browser-mode", choices=["iab", "chrome", "any"])
    p.add_argument("--runtime", choices=["codex", "playwright"], default="codex")
    p.add_argument("--viewport", choices=["desktop", "mobile", "both"])
    p.add_argument("--locale", default="zh-cn")
    p.add_argument("--base-url", default="https://testnet.1bullex.com/")
    p.add_argument("--environment-profile", default="testnet")
    p.add_argument("--account-profile", default="guest")
    p.add_argument("--evidence-level", choices=["minimal", "normal", "full"], default="normal")
    p.add_argument("--out-dir", default="/tmp/onebullex-web-qa")
    p.add_argument("--run-name")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--allow-side-effects", action="store_true")
    p.add_argument("--confirm-submit", action="store_true")
    p.add_argument("--skip-health-check", action="store_true")
    p.add_argument("--health-check-only", action="store_true")
    p.add_argument("--allow-withdraw", action="store_true")
    p.add_argument("--chrome-account-hint", default="Henrly (linjinhong16@gmail.com)")
    p.add_argument("--requirement-doc", default="")
    p.add_argument("--requirement-fetch-status", default="")
    p.add_argument("--requirement-execution-mode", default="")
    p.add_argument("--start-url", default="")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.dry_run and args.runtime == "codex":
        raise SystemExit(
            "Live Codex execution should be driven through Browser/Chrome plugin instructions. "
            "Use `--dry-run` for local validation, or `--runtime playwright` for supported public-page local execution."
        )
    if not args.dry_run and args.runtime == "playwright" and args.browser_mode == "chrome":
        raise SystemExit(
            "Local Playwright runtime currently does not support `browser_mode=chrome`. "
            "Use Codex Chrome plugin for login/account flows, or switch to `--browser-mode iab` for public/stateless flows."
        )
    run_name = args.run_name or dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = Path(args.out_dir).expanduser() / run_name
    out_dir.mkdir(parents=True, exist_ok=True)
    flow_arg = "env-health-check.yaml" if args.health_check_only else args.flow
    flow_paths = resolve_flows(flow_arg)
    all_results: list[StepResult] = []
    metadata: list[dict[str, Any]] = []
    for path in flow_paths:
        results, metas = run_flow(path, out_dir, args)
        all_results.extend(results)
        metadata.extend(metas)
    env = {
        "base_url": args.base_url,
        "environment_profile": args.environment_profile,
        "runtime": args.runtime,
        "browser_mode": args.browser_mode or "flow-default",
        "viewport": args.viewport or "flow-default",
        "locale": args.locale,
        "account_profile": args.account_profile,
        "dry_run": args.dry_run,
        "side_effects": "allowed" if args.allow_side_effects else "none",
        "confirm_submit": args.confirm_submit,
        "allow_withdraw": args.allow_withdraw,
        "chrome_account_hint": args.chrome_account_hint,
        "requirement_doc": args.requirement_doc,
        "requirement_fetch_status": args.requirement_fetch_status,
        "requirement_execution_mode": args.requirement_execution_mode,
        "start_url": args.start_url,
        "withdraw_submission_executed": False,
    }
    setup_notes = [
        "Dry-run mode: browser execution skipped; DOM observations use deterministic sample HTML."
        if args.dry_run
        else f"Live runtime: {args.runtime}. Public/stateless flows may execute locally only when runtime=playwright."
    ]
    md_path, _ = write_reports(out_dir, env, setup_notes, all_results, flow_paths, metadata)
    print(f"Report: {md_path}")
    print(f"Bug template: {out_dir / BUG_TEMPLATE_NAME}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FlowError, BrowserDriverError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
