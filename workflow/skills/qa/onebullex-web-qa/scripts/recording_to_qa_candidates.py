#!/usr/bin/env python3
"""Convert a Record & Replay event stream into Web QA candidate artifacts.

This tool summarizes local event JSONL into candidate files only. It does not
promote recordings into formal flows or routes.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from typing import Any

SENSITIVE_PATTERNS = [
    re.compile(r"password|passwd|pwd|otp|验证码|code|token|cookie|authorization|secret|api[_-]?key", re.I),
    re.compile(r"\b\d{6}\b"),
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
]


def safe_text(value: Any, limit: int = 300) -> str:
    text = json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value
    for pat in SENSITIVE_PATTERNS:
        text = pat.sub("[REDACTED]", text)
    return text[:limit]


def classify_event(event: dict[str, Any]) -> dict[str, Any] | None:
    raw = json.dumps(event, ensure_ascii=False)
    lower = raw.lower()
    item: dict[str, Any] = {
        "event_index": event.get("index") or event.get("seq") or "",
        "app": event.get("app") or event.get("application") or event.get("appName") or "",
        "window": event.get("window") or event.get("windowTitle") or "",
        "summary": safe_text(event),
    }
    if any(k in lower for k in ["click", "press", "button", "鼠标"]):
        item["type"] = "action_candidate"
    elif any(k in lower for k in ["url", "location", "http", "testnet.1bullex.com"]):
        item["type"] = "route_candidate"
    elif any(k in lower for k in ["select", "selected", "focus", "focused", "input", "text field"]):
        item["type"] = "selector_candidate"
    elif any(k in lower for k in ["assert", "visible", "toast", "error", "success", "成功", "失败"]):
        item["type"] = "assertion_candidate"
    else:
        return None
    return item


def load_events(path: Path, max_events: int) -> tuple[list[dict[str, Any]], int, bool]:
    events: list[dict[str, Any]] = []
    sensitive = False
    total = 0
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if not line.strip():
                continue
            total += 1
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                event = {"raw": line.strip()}
            raw = json.dumps(event, ensure_ascii=False)
            if any(p.search(raw) for p in SENSITIVE_PATTERNS):
                sensitive = True
            if len(events) < max_events:
                events.append(event)
    return events, total, sensitive


def main() -> int:
    p = argparse.ArgumentParser(description="Generate onebullex-web-qa candidates from Record & Replay events.jsonl.")
    p.add_argument("--events", required=True, help="Record & Replay events.jsonl path")
    p.add_argument("--metadata", default="", help="Optional session.json path")
    p.add_argument("--out-dir", required=True)
    p.add_argument("--label", default="recorded-web-flow")
    p.add_argument("--max-events", type=int, default=200)
    args = p.parse_args()

    events_path = Path(args.events).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    events, total, sensitive = load_events(events_path, args.max_events)
    candidates = [c for e in events if (c := classify_event(e))]

    quality_gate = {
        "workflow_complete": "manual_review_required",
        "sensitive_data_detected": sensitive,
        "route_action_assertion_identified": bool(candidates),
        "selector_mapping_required": True,
        "too_many_misclicks": "manual_review_required",
        "status": "needs_manual_review" if candidates and not sensitive else "do_not_promote",
    }

    digest = hashlib.sha256(events_path.read_bytes()).hexdigest()
    summary = {
        "generated": dt.datetime.now().isoformat(timespec="seconds"),
        "label": args.label,
        "events_path": str(events_path),
        "events_sha256": digest,
        "metadata_path": str(Path(args.metadata).expanduser().resolve()) if args.metadata else "",
        "total_events": total,
        "sampled_events": len(events),
        "quality_gate": quality_gate,
        "candidate_counts": {},
        "note": "Candidates require human confirmation before updating routes/*.yaml or flows/*.yaml.",
    }
    for c in candidates:
        summary["candidate_counts"][c["type"]] = summary["candidate_counts"].get(c["type"], 0) + 1

    (out_dir / "qa-recording-summary.md").write_text(
        "# QA Recording Summary\n\n"
        f"- Generated: {summary['generated']}\n"
        f"- Label: `{args.label}`\n"
        f"- Events: `{events_path}`\n"
        f"- Total events: {total}\n"
        f"- Quality gate: `{quality_gate['status']}`\n"
        f"- Sensitive data detected: `{sensitive}`\n\n"
        "Raw recordings must not be committed. Promote only confirmed candidates.\n",
        encoding="utf-8",
    )
    payload = {"summary": summary, "candidates": candidates}
    (out_dir / "recording-candidates.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    for folder, typ in [
        ("flow-seed-candidates", "action_candidate"),
        ("route-seed-candidates", "route_candidate"),
    ]:
        d = out_dir / folder
        d.mkdir(exist_ok=True)
        selected = [c for c in candidates if c["type"] == typ]
        (d / "README.md").write_text(
            "# Candidate Review\n\n"
            "These are not formal flows/routes. Convert only human-confirmed items.\n\n"
            + "\n".join(f"- {safe_text(c.get('summary',''), 180)}" for c in selected[:50])
            + ("\n" if selected else "- No candidates.\n"),
            encoding="utf-8",
        )

    selector_candidates = [c for c in candidates if c["type"] == "selector_candidate"]
    assertion_candidates = [c for c in candidates if c["type"] == "assertion_candidate"]
    test_id_requests = [c for c in candidates if c["type"] in {"selector_candidate", "action_candidate"}]
    (out_dir / "selector-hardening-candidates.json").write_text(json.dumps(selector_candidates, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "assertion-candidates.json").write_text(json.dumps(assertion_candidates, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "test-id-requests.md").write_text(
        "# Test ID Requests From Recording\n\n"
        + "\n".join(f"- Review target for stable `data-testid`: {safe_text(c.get('summary',''), 180)}" for c in test_id_requests[:50])
        + ("\n" if test_id_requests else "- No candidates.\n"),
        encoding="utf-8",
    )
    print(out_dir / "recording-candidates.json")
    return 0 if quality_gate["status"] != "do_not_promote" else 1


if __name__ == "__main__":
    raise SystemExit(main())
