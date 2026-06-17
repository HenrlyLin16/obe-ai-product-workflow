#!/usr/bin/env python3
"""Small adb + uiautomator driver for OneBullEx Android QA flows."""

from __future__ import annotations

import html
import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class DriverError(RuntimeError):
    pass


@dataclass
class Node:
    text: str = ""
    content_desc: str = ""
    resource_id: str = ""
    bounds: str = ""
    class_name: str = ""
    clickable: str = ""
    selected: str = ""
    x1: int = 0
    y1: int = 0
    x2: int = 0
    y2: int = 0

    @property
    def cx(self) -> int:
        return (self.x1 + self.x2) // 2

    @property
    def cy(self) -> int:
        return (self.y1 + self.y2) // 2

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "content-desc": self.content_desc,
            "resource-id": self.resource_id,
            "bounds": self.bounds,
            "class": self.class_name,
            "clickable": self.clickable,
            "selected": self.selected,
            "center": [self.cx, self.cy],
        }


class AdbDevice:
    def __init__(self, serial: str, dry_run: bool = False) -> None:
        self.serial = serial
        self.dry_run = dry_run

    def run(self, *args: str, check: bool = True, text: bool = False) -> bytes | str:
        cmd = ["adb", "-s", self.serial, *args]
        if self.dry_run:
            line = " ".join(cmd)
            return line if text else line.encode()
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        if check and proc.returncode != 0:
            raise DriverError(proc.stdout.decode(errors="replace").strip() or f"adb failed: {' '.join(cmd)}")
        return proc.stdout.decode(errors="replace") if text else proc.stdout

    def shell(self, *args: str, check: bool = True, text: bool = True) -> bytes | str:
        return self.run("shell", *args, check=check, text=text)


def require_adb(dry_run: bool = False) -> None:
    if dry_run:
        return
    if not shutil.which("adb"):
        raise DriverError("adb not found on PATH. Install Android platform-tools or add adb to PATH.")


def list_devices() -> list[tuple[str, str]]:
    proc = subprocess.run(["adb", "devices"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False)
    if proc.returncode != 0:
        raise DriverError(proc.stdout.strip() or "adb devices failed")
    devices: list[tuple[str, str]] = []
    for line in proc.stdout.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2:
            devices.append((parts[0], parts[1]))
    return devices


def choose_serial(serial: str | None = None, wireless: str | None = None, dry_run: bool = False, default: str = "SM02G4061923909") -> str:
    if dry_run:
        return serial or default
    if wireless:
        subprocess.run(["adb", "connect", wireless], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    devices = list_devices()
    if serial:
        matches = [d for d in devices if d[0] == serial]
        if not matches:
            raise DriverError(f"Requested serial {serial} is not in adb devices: {devices}")
        if matches[0][1] != "device":
            raise DriverError(f"Device {serial} is {matches[0][1]}; authorize USB debugging or reconnect.")
        return serial
    ready = [s for s, state in devices if state == "device"]
    if len(ready) == 1:
        return ready[0]
    if not ready:
        raise DriverError(f"No authorized adb device found. adb devices: {devices}")
    raise DriverError(f"Multiple adb devices found; pass --serial. Devices: {ready}")


def parse_nodes(xml_text: str) -> list[Node]:
    nodes: list[Node] = []
    for raw in re.findall(r"<node [^>]+>", xml_text):
        attrs: dict[str, str] = {}
        for attr in ["text", "content-desc", "resource-id", "bounds", "class", "clickable", "selected"]:
            match = re.search(attr + r'="([^"]*)"', raw)
            attrs[attr] = html.unescape(match.group(1)) if match else ""
        nums = [int(n) for n in re.findall(r"\d+", attrs.get("bounds", ""))]
        coords = nums if len(nums) == 4 else [0, 0, 0, 0]
        nodes.append(Node(
            text=attrs["text"],
            content_desc=attrs["content-desc"],
            resource_id=attrs["resource-id"],
            bounds=attrs["bounds"],
            class_name=attrs["class"],
            clickable=attrs["clickable"],
            selected=attrs["selected"],
            x1=coords[0], y1=coords[1], x2=coords[2], y2=coords[3],
        ))
    return nodes


def summarize_xml(xml_text: str, max_lines: int = 140) -> str:
    lines: list[str] = []
    for node in parse_nodes(xml_text):
        label = node.text or node.content_desc
        if not label:
            continue
        lines.append(f"{label} | {node.resource_id} | {node.content_desc} | {node.bounds}".strip())
        if len(lines) >= max_lines:
            break
    return "\n".join(lines) + ("\n" if lines else "")


class UIDriver:
    def __init__(self, device: AdbDevice, out_dir: Path | None = None) -> None:
        self.device = device
        self.out_dir = out_dir
        self.last_xml = ""

    def dump_xml(self) -> str:
        if self.device.dry_run:
            self.last_xml = dry_run_xml()
            return self.last_xml
        data = self.device.run("exec-out", "uiautomator", "dump", "/dev/tty", check=True, text=False)
        self.last_xml = data.decode(errors="ignore") if isinstance(data, bytes) else str(data)
        return self.last_xml

    def nodes(self, refresh: bool = True) -> list[Node]:
        xml = self.dump_xml() if refresh or not self.last_xml else self.last_xml
        return parse_nodes(xml)

    def find_node(self, selector: dict[str, Any], refresh: bool = True) -> Node | None:
        nodes = self.nodes(refresh=refresh)
        return find_node(nodes, selector)

    def wait_until(self, selector: dict[str, Any], timeout: float = 8.0, interval: float = 0.5) -> Node:
        deadline = time.time() + timeout
        last_summary = ""
        while time.time() <= deadline:
            xml = self.dump_xml()
            last_summary = summarize_xml(xml, max_lines=40)
            node = find_node(parse_nodes(xml), selector)
            if node:
                return node
            time.sleep(interval if not self.device.dry_run else 0.01)
        raise DriverError(f"Timed out waiting for selector {selector}. Current UI:\n{last_summary}")

    def tap_selector(self, selector: dict[str, Any], wait: float = 1.0) -> dict[str, Any]:
        fallback = selector.get("fallback") or selector.get("fallback_tap")
        try:
            node = self.wait_until(selector, timeout=float(selector.get("timeout", 6)))
            self.tap_xy(node.cx, node.cy, wait=wait)
            return {"method": "selector", "selector": selector, "node": node.to_dict()}
        except DriverError:
            if fallback and isinstance(fallback, list) and len(fallback) == 2:
                self.tap_xy(int(fallback[0]), int(fallback[1]), wait=wait)
                return {"method": "coordinate", "selector": selector, "coordinate": fallback}
            raise

    def tap_xy(self, x: int, y: int, wait: float = 1.0) -> None:
        if not self.device.dry_run:
            self.device.shell("input", "tap", str(x), str(y), check=False)
        time.sleep(0.02 if self.device.dry_run else wait)

    def swipe_xy(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300, wait: float = 1.0) -> None:
        if not self.device.dry_run:
            self.device.shell("input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration_ms), check=False)
        time.sleep(0.02 if self.device.dry_run else wait)

    def keyevent(self, keycode: str | int, wait: float = 1.0) -> None:
        if not self.device.dry_run:
            self.device.shell("input", "keyevent", str(keycode), check=False)
        time.sleep(0.02 if self.device.dry_run else wait)

    def input_text(self, value: str, selector: dict[str, Any] | None = None, wait: float = 0.5) -> None:
        if selector:
            self.tap_selector(selector, wait=0.2)
        escaped = value.replace(" ", "%s")
        if not self.device.dry_run:
            self.device.shell("input", "text", escaped, check=False)
        time.sleep(0.02 if self.device.dry_run else wait)

    def screenshot(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if self.device.dry_run:
            path.write_bytes(b"")
            return
        path.write_bytes(self.device.run("exec-out", "screencap", "-p", check=True, text=False))

    def logcat(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if self.device.dry_run:
            path.write_text("dry-run logcat\n", encoding="utf-8")
            return
        path.write_text(str(self.device.run("logcat", "-d", check=False, text=True)), encoding="utf-8")


def find_node(nodes: list[Node], selector: dict[str, Any]) -> Node | None:
    if "id" in selector:
        target = str(selector["id"])
        for node in nodes:
            if node.resource_id == target or node.resource_id.endswith("/" + target):
                return node
    if "desc" in selector:
        target = str(selector["desc"])
        for node in nodes:
            if node.content_desc == target:
                return node
    if "text" in selector:
        target = str(selector["text"])
        for node in nodes:
            if node.text == target:
                return node
    if "text_regex" in selector:
        pattern = re.compile(str(selector["text_regex"]))
        for node in nodes:
            if pattern.search(node.text):
                return node
    if "desc_regex" in selector:
        pattern = re.compile(str(selector["desc_regex"]))
        for node in nodes:
            if pattern.search(node.content_desc):
                return node
    if "any_text" in selector:
        for wanted in selector["any_text"]:
            for node in nodes:
                if node.text == wanted:
                    return node
    return None


def text_values(xml_text: str) -> list[str]:
    return [node.text for node in parse_nodes(xml_text) if node.text]


def label_values(xml_text: str) -> list[str]:
    values: list[str] = []
    for node in parse_nodes(xml_text):
        for value in [node.text, node.content_desc]:
            if value and value not in values:
                values.append(value)
    return values


def dry_run_xml() -> str:
    return """<hierarchy>
<node text="首页" bounds="[177,2523][245,2572]"/>
<node text="市场" content-desc="tab-market" bounds="[372,2523][440,2572]"/>
<node text="合约" content-desc="tab-futures" bounds="[567,2523][635,2572]"/>
<node text="现货" content-desc="tab-spot" bounds="[762,2523][830,2572]"/>
<node text="资产" content-desc="tab-assets" bounds="[957,2523][1025,2572]"/>
<node text="开仓" bounds="[54,420][174,500]"/>
<node text="平仓" bounds="[234,420][354,500]"/>
<node text="K线图" bounds="[930,170][1075,255]"/>
<node text="最新价格" bounds="[48,510][210,570]"/>
<node text="更多" bounds="[930,620][1025,690]"/>
<node text="设置" content-desc="设置" bounds="[1090,640][1176,725]"/>
<node text="实时盯盘浮窗" bounds="[52,2250][420,2315]"/>
<node text="开启后可实时查看币种波动趋势" bounds="[52,2320][620,2380]"/>
<node text="实时盯盘" bounds="[52,260][245,330]"/>
<node text="添加币对" bounds="[498,2380][702,2460]"/>
<node text="BTCUSDT 永续" bounds="[72,1120][350,1200]"/>
<node text="置顶" bounds="[870,1330][970,1390]"/>
<node text="拖动" bounds="[1010,1330][1110,1390]"/>
<node text="总览" bounds="[54,140][174,225]"/>
<node text="资金" bounds="[234,140][354,225]"/>
<node text="总资产价值" bounds="[48,309][223,369]"/>
<node text="币种" content-desc="market-sort-symbol" bounds="[10,560][145,620]"/>
<node text="价格" content-desc="market-sort-price" bounds="[720,560][850,620]"/>
<node text="涨跌" content-desc="market-sort-change" bounds="[980,560][1130,620]"/>
<node text="BCH / USDT" bounds="[10,650][250,740]"/>
<node text="430.12" bounds="[720,650][900,740]"/>
<node text="5.15%" bounds="[950,650][1130,740]"/>
<node text="BTC / USDT" bounds="[10,780][250,870]"/>
<node text="104000.12" bounds="[720,780][900,870]"/>
<node text="0.59%" bounds="[950,780][1130,870]"/>
<node text="DOGE / USDT" bounds="[10,910][250,1000]"/>
<node text="0.18" bounds="[720,910][900,1000]"/>
<node text="-1.48%" bounds="[950,910][1130,1000]"/>
<node text="账户余额" bounds="[48,1106][212,1166]"/>
<node text="持仓保证金" bounds="[600,1106][805,1166]"/>
<node text="委托保证金" bounds="[48,1268][253,1328]"/>
<node text="未实现盈亏" bounds="[600,1268][805,1328]"/>
</hierarchy>"""
