#!/usr/bin/env python3
"""Build a screenshot-backed UX/UI review pack from a ux-ui-walkthrough run."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

FINDING_JSON = "ux-ui-findings.json"
FINDING_MD = "ux-ui-review-report.md"
BUG_TEMPLATE = "confirmed-bugs.template.json"

P0_CHECKS = [
    "主流程是否通畅、可退出、可返回、无死循环",
    "关键操作区是否易触达，按钮状态/反馈是否清楚",
    "排序、tab 切换、刷新、列表交互是否有可感知反馈",
    "失败/无内容/无权限/未登录是否有明确原因和解决方法",
    "交易/资产/价格数字是否可读、精度合理、正负号和颜色一致",
    "高风险或资金相关操作是否有二次确认和风险提示",
]
P1_CHECKS = [
    "页面信息层级是否清晰，重要内容是否突出",
    "同类文案、时间、符号、单位、按钮文案是否统一",
    "列表项结构是否稳定，字段之间对齐和关联是否清楚",
    "加载、刷新、网络变化是否有反馈或降级提示",
    "输入框是否有提示、限制、错误原因和恢复方式",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate UX/UI review report from OneBullEx evidence directory.")
    p.add_argument("evidence_dir", help="Directory created by ux-ui-walkthrough flow.")
    p.add_argument("--dry-run", action="store_true", help="Generate report skeleton without heuristic findings.")
    return p.parse_args()


def load_report(evidence_dir: Path) -> dict[str, Any]:
    path = evidence_dir / "onebullex-android-qa-report.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"results": [], "environment": {}, "summary": {}}


def read_summary(path: str | None) -> str:
    if not path:
        return ""
    p = Path(path)
    return p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""


def page_label(result: dict[str, Any]) -> str:
    return str(result.get("step", "")).replace("ux_", "").replace("_", " ")


def base_review_items(report: dict[str, Any]) -> list[dict[str, Any]]:
    items = []
    for result in report.get("results", []):
        if not str(result.get("step", "")).startswith("ux_"):
            continue
        evidence = result.get("evidence") or {}
        items.append({
            "page": page_label(result),
            "step": result.get("step"),
            "status": result.get("status"),
            "screenshot": evidence.get("screenshot", ""),
            "summary": evidence.get("summary", ""),
            "xml": evidence.get("xml", ""),
            "notes": result.get("notes", []),
            "checks": P0_CHECKS + P1_CHECKS,
        })
    return items


def heuristic_findings(items: list[dict[str, Any]], dry_run: bool) -> list[dict[str, Any]]:
    if dry_run:
        return []
    findings: list[dict[str, Any]] = []
    for item in items:
        summary = read_summary(item.get("summary"))
        page = item["page"]
        screenshot = item.get("screenshot", "")
        if item.get("status") != "pass":
            findings.append(finding(page, screenshot, "ux_blocker", "P0", "页面走查步骤未通过", "流程无法稳定进入或取证失败", "用户可能无法完成对应路径", "修复 flow 或页面可达性后复测", True, item))
        if "market" in page and "sort" not in page and "市场" in summary:
            if not re.search(r"涨|跌|Change|价格|Price", summary):
                findings.append(finding(page, screenshot, "ui_inconsistency", "P1", "行情列表排序/价格字段反馈不清晰", "截图摘要未识别到价格/涨跌相关表头或反馈", "用户难以理解列表当前排序和行情含义", "补充稳定表头、排序箭头或选中态", True, item))
        if "assets" in page or "资产" in page:
            if "总资产价值" in summary and not re.search(r"≈\s*\$|USDT", summary):
                findings.append(finding(page, screenshot, "copy_issue", "P1", "资产估值单位表达不完整", "资产区域缺少可识别的 USDT 或折合美元说明", "用户可能误解资产数值单位", "统一金额单位与折合展示", True, item))
            long_amount = re.search(r"\b\d{1,3}(?:,\d{3}){2,}\.\d{2,}\b", summary)
            if long_amount and "总资产价值" in summary:
                findings.append(finding(page, screenshot, "accessibility_issue", "P1", "超大资产金额与单位同排展示可读性风险", f"总资产区域出现超长金额 {long_amount.group(0)}，在移动端容易压缩单位和下拉控件", "用户在资产页快速确认余额和计价单位时认知负担增加，极端大额账户可能发生视觉拥挤", "为大额资产提供自适应字号、单位换行/右侧固定、或万/百万缩写策略，并保留完整值查看方式", True, item))
            if "隐藏小额资产" in summary and "BTC" in summary and "≈ $" not in summary:
                findings.append(finding(page, screenshot, "ui_inconsistency", "P1", "现货资产列表估值信息不完整", "资产列表存在币种但缺少折合估值文本", "影响用户判断资产价值", "保持币种数量与法币估值成组展示", True, item))
    findings = dedupe_findings(findings)
    if not findings:
        findings.append({
            "id": "UX-OBS-001",
            "category": "needs_design_confirmation",
            "severity": "P2",
            "bug_candidate": False,
            "title": "本轮自动启发式未发现明确 UX/UI Bug",
            "page": "all",
            "screenshot": "",
            "check_item": "截图取证 + P0/P1 自查项",
            "phenomenon": "已生成页面截图证据，需人工/设计继续做视觉细节判断",
            "impact": "自动规则只能覆盖结构化问题，视觉规范一致性仍需人工确认",
            "suggestion": "由产品/设计基于截图复核间距、颜色、字重、组件状态",
            "evidence": {},
        })
    return findings


def finding(page: str, screenshot: str, category: str, severity: str, title: str, phenomenon: str, impact: str, suggestion: str, bug_candidate: bool, item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": f"UX-{abs(hash((page, title))) % 100000:05d}",
        "category": category,
        "severity": severity,
        "bug_candidate": bug_candidate and severity in {"P0", "P1"},
        "title": title,
        "page": page,
        "screenshot": screenshot,
        "check_item": "; ".join(item.get("checks", [])[:3]),
        "phenomenon": phenomenon,
        "impact": impact,
        "suggestion": suggestion,
        "evidence": {"screenshot": screenshot, "summary": item.get("summary", ""), "xml": item.get("xml", "")},
    }


def dedupe_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[tuple[str, str], dict[str, Any]] = {}
    for item in findings:
        key = (str(item.get("title", "")), str(item.get("phenomenon", "")))
        if key not in seen:
            seen[key] = item
            continue
        existing = seen[key]
        if item.get("screenshot") and item.get("screenshot") != existing.get("screenshot"):
            existing.setdefault("related_screenshots", []).append(item.get("screenshot"))
            evidence = existing.setdefault("evidence", {})
            related = evidence.setdefault("related_screenshots", [])
            if isinstance(related, list):
                related.append(item.get("screenshot"))
    return list(seen.values())


def write_markdown(out: Path, report: dict[str, Any], items: list[dict[str, Any]], findings: list[dict[str, Any]]) -> None:
    lines = ["# OneBullEx UX/UI Screenshot Walkthrough Report\n\n"]
    lines.append(f"- Evidence directory: `{out}`\n")
    lines.append(f"- Device: `{report.get('environment', {}).get('device', '')}`\n")
    lines.append(f"- Findings: {len(findings)}\n\n")
    lines.append("## Coverage\n\n")
    lines.append("| Page | Status | Screenshot | Summary |\n| --- | --- | --- | --- |\n")
    for item in items:
        lines.append(f"| {item['page']} | {item['status']} | {link('screenshot', item.get('screenshot'))} | {link('summary', item.get('summary'))} |\n")
    lines.append("\n## Findings\n\n")
    lines.append("| ID | Severity | Category | Bug Candidate | Page | Title | Evidence |\n| --- | --- | --- | --- | --- | --- | --- |\n")
    for f in findings:
        lines.append(f"| {f['id']} | {f['severity']} | {f['category']} | {f['bug_candidate']} | {f['page']} | {f['title']} | {link('screenshot', f.get('screenshot'))} |\n")
    lines.append("\n## Review Criteria\n\n")
    lines.append("### P0\n")
    for c in P0_CHECKS:
        lines.append(f"- {c}\n")
    lines.append("\n### P1\n")
    for c in P1_CHECKS:
        lines.append(f"- {c}\n")
    out.joinpath(FINDING_MD).write_text("".join(lines), encoding="utf-8")


def link(label: str, path: str | None) -> str:
    return f"[{label}]({Path(path).as_posix()})" if path else "-"


def flatten_attachments(evidence: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for value in evidence.values():
        if isinstance(value, list):
            out.extend(str(v) for v in value if v)
        elif value:
            out.append(str(value))
    # Preserve order while deduping.
    return list(dict.fromkeys(out))


def write_bug_template(out: Path, findings: list[dict[str, Any]]) -> None:
    items = []
    for f in findings:
        if not f.get("bug_candidate"):
            continue
        items.append({
            "confirmed": False,
            "bug_candidate": True,
            "category": f.get("category"),
            "severity": f.get("severity"),
            "title": f"[Android][OneBullEx dev][UX] {f.get('title')}",
            "module": "/",
            "affected_version": "",
            "bug_type": "界面优化",
            "priority": 3 if f.get("severity") == "P1" else 2,
            "steps": [f"Open page: {f.get('page')}", f"Review screenshot: {f.get('screenshot')}"],
            "actual": f.get("phenomenon", ""),
            "expected": f.get("suggestion", ""),
            "attachments": flatten_attachments(f.get("evidence", {})),
            "source_report": str(out / FINDING_MD),
        })
    if not items:
        items.append({
            "confirmed": False,
            "bug_candidate": False,
            "category": "manual_placeholder",
            "severity": "P2",
            "title": "[Android][OneBullEx dev][UX] Replace with confirmed UX/UI issue",
            "module": "/",
            "bug_type": "界面优化",
            "priority": 3,
            "steps": ["1. Replace with screenshot-backed reproduction step"],
            "actual": "Replace with observed UX/UI issue.",
            "expected": "Replace with expected UI/UX behavior.",
            "attachments": [],
            "source_report": str(out / FINDING_MD),
        })
    (out / BUG_TEMPLATE).write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    args = parse_args()
    out = Path(args.evidence_dir).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    report = load_report(out)
    items = base_review_items(report)
    findings = heuristic_findings(items, args.dry_run)
    (out / FINDING_JSON).write_text(json.dumps({"coverage": items, "findings": findings}, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(out, report, items, findings)
    write_bug_template(out, findings)
    print(out / FINDING_MD)
    print(out / FINDING_JSON)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
