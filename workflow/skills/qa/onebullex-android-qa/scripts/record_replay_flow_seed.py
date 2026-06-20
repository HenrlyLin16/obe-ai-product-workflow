#!/usr/bin/env python3
"""Turn Record & Replay event captures into QA flow seed artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any


SENSITIVE_PATTERNS = [
    re.compile(r"password", re.I),
    re.compile(r"otp", re.I),
    re.compile(r"verification", re.I),
    re.compile(r"token", re.I),
    re.compile(r"secret", re.I),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate flow seed artifacts from a Record & Replay session.")
    parser.add_argument("events_path", help="Path to the record-and-replay events.jsonl file.")
    parser.add_argument("--out-dir", required=True, help="Evidence directory for generated artifacts.")
    parser.add_argument("--label", default="recording-seed", help="Label used for generated filenames.")
    return parser.parse_args()


def load_events(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise SystemExit(f"Missing Record & Replay events file: {path}")
    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            events.append(item)
    return events


def looks_sensitive(payload: str) -> bool:
    return any(pattern.search(payload) for pattern in SENSITIVE_PATTERNS)


def summarize_event(event: dict[str, Any]) -> dict[str, Any]:
    payload = json.dumps(event, ensure_ascii=False)
    sensitive = looks_sensitive(payload)
    app = event.get("app") or event.get("application") or ""
    window = event.get("window") or event.get("windowTitle") or ""
    event_type = event.get("type") or event.get("eventType") or "unknown"
    text_hint = ""
    for key in ["text", "selectedText", "label", "title", "value"]:
        value = event.get(key)
        if isinstance(value, str) and value.strip():
            text_hint = value.strip()
            break
    if sensitive:
        text_hint = "[REDACTED]"
    return {
        "type": event_type,
        "app": app,
        "window": window,
        "text_hint": text_hint,
        "sensitive": sensitive,
    }


def build_flow_seed(event_summaries: list[dict[str, Any]]) -> dict[str, Any]:
    steps: list[dict[str, Any]] = []
    for idx, item in enumerate(event_summaries[:30], start=1):
        name = f"recorded_step_{idx:02d}"
        notes = [f"Recorded event type={item['type']} app={item['app']} window={item['window']}"]
        if item["text_hint"]:
            notes.append(f"Hint={item['text_hint']}")
        steps.append({
            "name": name,
            "action": "log",
            "message": " | ".join(notes),
            "failure_category": "automation_issue",
            "continue_on_failure": True,
        })
    return {
        "name": "record-replay-seed",
        "version": 1,
        "recording_seeded": True,
        "side_effects": "none",
        "steps": steps,
    }


def main() -> int:
    args = parse_args()
    events_path = Path(args.events_path).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    events = load_events(events_path)
    summaries = [summarize_event(event) for event in events]
    flow_seed = build_flow_seed(summaries)
    route_candidates = []
    selector_candidates = []
    for idx, item in enumerate(summaries[:20], start=1):
        route_candidates.append({
            "id": f"route-seed-{idx:02d}",
            "description": f"Review recorded navigation event {idx}",
            "app": item["app"],
            "window": item["window"],
            "text_hint": item["text_hint"],
        })
        if item["text_hint"] and item["text_hint"] != "[REDACTED]":
            selector_candidates.append({
                "id": f"selector-seed-{idx:02d}",
                "hint": item["text_hint"],
                "recommendation": "Convert this into a stable resource-id/content-desc selector before using it in a long-lived flow.",
            })

    stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", args.label).strip("_") or "recording-seed"
    flow_path = out_dir / f"{stem}.flow-seed.json"
    route_path = out_dir / f"{stem}.route-seeds.json"
    selector_path = out_dir / f"{stem}.selector-hardening.json"
    summary_path = out_dir / "qa-recording-summary.md"

    flow_path.write_text(json.dumps(flow_seed, ensure_ascii=False, indent=2), encoding="utf-8")
    route_path.write_text(json.dumps(route_candidates, ensure_ascii=False, indent=2), encoding="utf-8")
    selector_path.write_text(json.dumps(selector_candidates, ensure_ascii=False, indent=2), encoding="utf-8")
    summary_lines = [
        "# QA Recording Summary\n",
        f"- Generated: {dt.datetime.now().isoformat(timespec='seconds')}\n",
        f"- Events source: `{events_path}`\n",
        f"- Total events parsed: {len(events)}\n",
        f"- Sensitive events redacted: {sum(1 for item in summaries if item['sensitive'])}\n",
        f"- Flow seed: `{flow_path}`\n",
        f"- Route seeds: `{route_path}`\n",
        f"- Selector hardening candidates: `{selector_path}`\n",
        "\n## Notes\n",
        "- These artifacts are exploratory seeds only.\n",
        "- Convert stable steps to real selectors/routes before adding them to `flows/*.yaml`.\n",
        "- Do not copy sensitive values from the recording into the Skill.\n",
    ]
    summary_path.write_text("".join(summary_lines), encoding="utf-8")

    print(f"Flow seed: {flow_path}")
    print(f"Route seeds: {route_path}")
    print(f"Selector hardening: {selector_path}")
    print(f"Summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
