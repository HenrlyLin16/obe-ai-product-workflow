#!/usr/bin/env python3
"""Helpers for controlled FIClash/VPN handling during Android QA."""

from __future__ import annotations

import time
from typing import Any

from android_device_controller import open_package
from ui_driver import AdbDevice, DriverError, UIDriver, label_values

DEFAULT_VPN_PACKAGE = "com.follow.clash"


def package_installed(device: AdbDevice, package: str) -> bool:
    out = str(device.shell("pm", "list", "packages", package, check=False))
    return f"package:{package}" in out


def vpn_status(device: AdbDevice) -> dict[str, Any]:
    if device.dry_run:
        return {
            "connected": False,
            "status_text": "dry-run simulated disconnected",
            "package": DEFAULT_VPN_PACKAGE,
        }
    dump = str(device.shell("dumpsys", "connectivity", check=False))
    connected = "VPN" in dump and "CONNECTED" in dump
    return {
        "connected": connected,
        "status_text": dump[:800],
        "package": DEFAULT_VPN_PACKAGE,
    }


def _handle_android_vpn_confirm(driver: UIDriver) -> bool:
    xml = driver.dump_xml()
    values = label_values(xml)
    targets = ["确定", "允许", "OK", "始终允许"]
    for text in targets:
        if text in values:
            driver.tap_selector({"text": text, "fallback": [900, 1760]}, wait=1.0)
            return True
    return False


def ensure_vpn(
    device: AdbDevice,
    driver: UIDriver,
    package: str = DEFAULT_VPN_PACKAGE,
    target_mode: str = "reuse_last",
    failure_policy: str = "pause_for_manual",
    timeout: float = 8.0,
) -> tuple[dict[str, Any], list[str]]:
    notes: list[str] = []
    if device.dry_run:
        return {
            "vpn_mode": "dry_run_skipped",
            "vpn_package": package,
            "vpn_target_mode": target_mode,
            "vpn_connection_result": "dry_run_skipped",
            "vpn_manual_intervention_required": False,
            "vpn_status_text": "dry-run skipped VPN connection",
        }, ["Dry-run: skipped FIClash/VPN preparation."]
    if not package_installed(device, package):
        raise DriverError(f"VPN package not installed: {package}")
    initial = vpn_status(device)
    if initial.get("connected"):
        return {
            "vpn_mode": "already_connected",
            "vpn_package": package,
            "vpn_target_mode": target_mode,
            "vpn_connection_result": "already_connected",
            "vpn_manual_intervention_required": False,
            "vpn_status_text": initial.get("status_text", ""),
        }, ["VPN already connected before flow."]

    notes.extend(open_package(device, package))
    time.sleep(1.0 if not device.dry_run else 0.02)
    confirm_tapped = _handle_android_vpn_confirm(driver)
    if confirm_tapped:
        notes.append("Handled Android VPN confirmation dialog.")

    deadline = time.time() + timeout
    last = initial
    while time.time() <= deadline:
        last = vpn_status(device)
        if last.get("connected"):
            notes.append("VPN became connected.")
            return {
                "vpn_mode": "connected",
                "vpn_package": package,
                "vpn_target_mode": target_mode,
                "vpn_connection_result": "connected",
                "vpn_manual_intervention_required": False,
                "vpn_status_text": last.get("status_text", ""),
            }, notes
        time.sleep(1.0 if not device.dry_run else 0.02)

    if failure_policy == "pause_for_manual":
        notes.append("VPN did not connect automatically; manual intervention required.")
        return {
            "vpn_mode": "failed_manual_required",
            "vpn_package": package,
            "vpn_target_mode": target_mode,
            "vpn_connection_result": "manual_required",
            "vpn_manual_intervention_required": True,
            "vpn_status_text": last.get("status_text", ""),
        }, notes
    raise DriverError("VPN did not connect automatically.")
