#!/usr/bin/env python3
"""Extract UX checklist items from the CoinStore workbook disguised as .csv."""

from __future__ import annotations

import argparse
import csv
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

DEFAULT_SOURCE = "/Users/jingxing/Desktop/项目资料/CoinStore/用户体验/用户体验自查表.csv"
NS = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
SECTION_ROWS = {
    "一、任务流程": 1,
    "二、框架布局": 17,
    "三、页面级交互": 29,
    "四、页面元素": 1,
    "五、组件&控件": 43,
    "六、运营需求检查": 102,
    "七、特殊场景再查": 114,
}


def col_idx(col: str) -> int:
    n = 0
    for ch in col:
        n = n * 26 + ord(ch) - 64
    return n - 1


def read_xlsx_like(path: Path) -> list[list[str]]:
    if not zipfile.is_zipfile(path):
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            return list(csv.reader(f))
    with zipfile.ZipFile(path) as z:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.findall("a:si", NS):
                shared.append("".join(t.text or "" for t in si.findall(".//a:t", NS)))
        sheet = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
        rows: list[list[str]] = []
        for r in sheet.findall(".//a:sheetData/a:row", NS):
            arr = [""] * 16
            for c in r.findall("a:c", NS):
                ref = c.attrib.get("r", "")
                col = "".join(re.findall("[A-Z]+", ref))
                v = c.find("a:v", NS)
                if v is None:
                    continue
                value = v.text or ""
                if c.attrib.get("t") == "s":
                    value = shared[int(value)]
                idx = col_idx(col)
                if idx < len(arr):
                    arr[idx] = value.strip()
            rows.append(arr)
        return rows


def priority(required: str, section: str) -> str:
    if required == "必要":
        if section in {"一、任务流程", "五、组件&控件", "七、特殊场景再查"}:
            return "P0"
        return "P1"
    return "P2"


def parse_items(rows: list[list[str]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    current_left = "一、任务流程"
    current_right = "四、页面元素"
    left_category = ""
    right_category = ""
    left_check = ""
    right_check = ""
    for idx, row in enumerate(rows, start=1):
        a, b, c = row[0], row[1], row[2]
        e, f, g, h = row[4], row[5], row[6], row[7]
        if a.startswith(("一、", "二、", "三、")):
            current_left = a
            left_category = ""
            left_check = ""
            continue
        if e.startswith(("四、", "五、", "六、", "七、")):
            current_right = e
            right_category = ""
            right_check = ""
            continue
        if a and a not in {"自查点", "类别"}:
            left_check = a
        if b and b != "描述":
            items.append({
                "section": current_left,
                "category": left_category,
                "check": left_check or "通用",
                "description": b,
                "required": c == "必要",
                "priority": priority(c, current_left),
                "source_row": idx,
            })
        if e and e not in {"类别", "自查点"}:
            right_category = e
        if f and f not in {"标记", "自查点"}:
            right_check = f
        if g and g != "描述":
            items.append({
                "section": current_right,
                "category": right_category,
                "check": right_check or "通用",
                "description": g,
                "required": h == "必要",
                "priority": priority(h, current_right),
                "source_row": idx,
            })
    return [item for item in items if item["description"]]


def write_markdown(items: list[dict[str, Any]], out: Path, source: Path) -> None:
    groups: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        groups.setdefault(item["section"], []).append(item)
    lines = ["# UX/UI Walkthrough Checklist\n\n", f"Source: `{source}`\n\n", "Use this checklist for screenshot-backed OneBullEx Android UX/UI review. Treat P0/P1 as required review dimensions; P2 as observation/design debt.\n\n"]
    for section, section_items in groups.items():
        lines.append(f"## {section}\n\n")
        lines.append("| Priority | Category | Check | Description | Required | Source Row |\n")
        lines.append("| --- | --- | --- | --- | --- | --- |\n")
        for item in section_items:
            desc = item["description"].replace("|", "/")
            lines.append(f"| {item['priority']} | {item['category']} | {item['check']} | {desc} | {'yes' if item['required'] else 'no'} | {item['source_row']} |\n")
        lines.append("\n")
    out.write_text("".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract UX checklist from xlsx/csv source.")
    parser.add_argument("source", nargs="?", default=DEFAULT_SOURCE)
    parser.add_argument("--md", default=str(Path(__file__).resolve().parents[1] / "references" / "ux-ui-checklist.md"))
    parser.add_argument("--json", default="")
    args = parser.parse_args()
    source = Path(args.source).expanduser()
    rows = read_xlsx_like(source)
    items = parse_items(rows)
    write_markdown(items, Path(args.md), source)
    if args.json:
        Path(args.json).write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"items={len(items)} md={args.md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
