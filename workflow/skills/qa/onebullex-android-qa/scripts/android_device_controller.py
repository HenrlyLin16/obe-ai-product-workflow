#!/usr/bin/env python3
"""Higher-level Android device control helpers for OneBullEx QA."""

from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from typing import Any

from ui_driver import AdbDevice, DriverError


@dataclass
class DeviceSnapshot:
    serial: str
    state: str
    model: str = ""
    device_name: str = ""
    transport_id: str = ""
    raw: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "serial": self.serial,
            "state": self.state,
            "model": self.model,
            "device_name": self.device_name,
            "transport_id": self.transport_id,
            "raw": self.raw,
        }


def parse_adb_devices_long(output: str) -> list[DeviceSnapshot]:
    records: list[DeviceSnapshot] = []
    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith("List of devices attached"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        meta: dict[str, str] = {}
        for token in parts[2:]:
            if ":" in token:
                key, value = token.split(":", 1)
                meta[key] = value
        records.append(
            DeviceSnapshot(
                serial=parts[0],
                state=parts[1],
                model=meta.get("model", ""),
                device_name=meta.get("device", ""),
                transport_id=meta.get("transport_id", ""),
                raw=line,
            )
        )
    return records


def adb_devices_long() -> tuple[str, list[DeviceSnapshot]]:
    proc = subprocess.run(
        ["adb", "devices", "-l"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise DriverError(proc.stdout.strip() or "adb devices -l failed")
    return proc.stdout, parse_adb_devices_long(proc.stdout)


def ensure_adb_stable(
    requested_serial: str | None = None,
    wireless: str | None = None,
    retries: int = 3,
    interval_ms: int = 800,
    dry_run: bool = False,
    default_serial: str = "SM02G4061923909",
) -> tuple[str, dict[str, Any], list[str]]:
    if dry_run:
        snapshot = DeviceSnapshot(
            serial=requested_serial or default_serial,
            state="device",
            model="Seeker",
            device_name="Seeker",
            transport_id="1",
            raw=f"{requested_serial or default_serial}\tdevice product:seeker model:Seeker device:seeker transport_id:1",
        )
        return snapshot.serial, {
            "adb_devices_snapshot": snapshot.raw,
            "adb_target_serial": snapshot.serial,
            "adb_connection_mode": "dry-run",
            "adb_stability_check_passed": True,
            "adb_stability_attempts": 1,
            "adb_detected_model": snapshot.model,
            "adb_detected_device": snapshot.device_name,
            "adb_transport_id": snapshot.transport_id,
        }, ["Dry-run: skipped real adb stability checks."]

    if wireless:
        subprocess.run(["adb", "connect", wireless], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)

    notes: list[str] = []
    stable_target: DeviceSnapshot | None = None
    raw_snapshots: list[str] = []
    for attempt in range(1, max(retries, 1) + 1):
        raw, records = adb_devices_long()
        raw_snapshots.append(raw.strip())
        if requested_serial:
            match = next((item for item in records if item.serial == requested_serial), None)
            if not match:
                notes.append(f"Attempt {attempt}: serial {requested_serial} not found in adb devices -l.")
            elif match.state != "device":
                notes.append(f"Attempt {attempt}: serial {requested_serial} state={match.state}.")
            else:
                if stable_target and stable_target.serial == match.serial and stable_target.state == "device":
                    return match.serial, {
                        "adb_devices_snapshot": raw.strip(),
                        "adb_target_serial": match.serial,
                        "adb_connection_mode": "wifi" if wireless else "usb",
                        "adb_stability_check_passed": True,
                        "adb_stability_attempts": attempt,
                        "adb_detected_model": match.model,
                        "adb_detected_device": match.device_name,
                        "adb_transport_id": match.transport_id,
                    }, notes + [f"ADB stable recognition passed on attempt {attempt}."]
                stable_target = match
        else:
            ready = [item for item in records if item.state == "device"]
            if len(ready) != 1:
                notes.append(f"Attempt {attempt}: expected exactly one ready device, got {[item.raw for item in ready]}.")
            else:
                match = ready[0]
                if stable_target and stable_target.serial == match.serial and stable_target.state == "device":
                    return match.serial, {
                        "adb_devices_snapshot": raw.strip(),
                        "adb_target_serial": match.serial,
                        "adb_connection_mode": "wifi" if wireless else "usb",
                        "adb_stability_check_passed": True,
                        "adb_stability_attempts": attempt,
                        "adb_detected_model": match.model,
                        "adb_detected_device": match.device_name,
                        "adb_transport_id": match.transport_id,
                    }, notes + [f"ADB stable recognition passed on attempt {attempt}."]
                stable_target = match
        if attempt < max(retries, 1):
            time.sleep(max(interval_ms, 100) / 1000.0)
    raise DriverError(
        "ADB stable recognition gate failed. "
        f"requested_serial={requested_serial or '<auto>'}; snapshots={raw_snapshots}; notes={notes}"
    )


def screen_locked(device: AdbDevice) -> bool:
    policy = str(device.shell("dumpsys", "window", "policy", check=False))
    return "mInputRestricted=true" in policy or "isStatusBarKeyguard=true" in policy


def foreground_app(device: AdbDevice) -> str:
    return str(device.shell("dumpsys", "window", "windows", check=False)).strip()


def launch_app(device: AdbDevice, package: str, activity: str | None = None, force_stop: bool = False) -> list[str]:
    if device.dry_run:
        component = f"{package}/{activity}" if activity else package
        return [f"Dry-run launch {component}."]
    notes: list[str] = []
    if force_stop:
        device.shell("am", "force-stop", package, check=False)
        time.sleep(0.5)
        notes.append(f"Force-stopped {package}.")
    if activity:
        component = f"{package}/{activity}"
        device.shell("am", "start", "-n", component, check=True)
        notes.append(f"Launched {component}.")
    else:
        device.shell("monkey", "-p", package, "-c", "android.intent.category.LAUNCHER", "1", check=True)
        notes.append(f"Launched {package} via launcher.")
    time.sleep(1.0)
    return notes


def open_package(device: AdbDevice, package: str) -> list[str]:
    if device.dry_run:
        return [f"Dry-run open external app {package}."]
    out = str(device.shell("cmd", "package", "resolve-activity", "--brief", package, check=False)).strip()
    if out:
        device.shell("am", "start", "-n", out.splitlines()[-1], check=False)
        time.sleep(1.0)
        return [f"Opened {package} via resolved activity {out.splitlines()[-1]}."]
    device.shell("monkey", "-p", package, "-c", "android.intent.category.LAUNCHER", "1", check=False)
    time.sleep(1.0)
    return [f"Opened {package} via monkey launcher fallback."]


def prepare_device_state(
    device: AdbDevice,
    package: str,
    activity: str,
    no_launch: bool,
    force_stop_before_launch: bool = False,
) -> list[str]:
    if device.dry_run:
        return ["Dry-run mode: skipped adb device mutation and launch."]
    notes: list[str] = []
    device.shell("svc", "power", "stayon", "true", check=False)
    device.shell("cmd", "statusbar", "collapse", check=False)
    if screen_locked(device):
        raise DriverError("Device appears locked. Unlock the phone before running QA.")
    resolved = str(device.shell("cmd", "package", "resolve-activity", "--brief", package, check=False)).strip()
    notes.append(f"Resolved activity: {resolved or 'not reported'}")
    notes.append(f"Foreground before flow: {foreground_app(device)[:160]}")
    if not no_launch:
        notes.extend(launch_app(device, package, activity=activity, force_stop=force_stop_before_launch))
    return notes
