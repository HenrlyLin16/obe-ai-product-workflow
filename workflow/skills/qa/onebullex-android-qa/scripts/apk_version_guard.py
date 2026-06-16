#!/usr/bin/env python3
"""Check OneBullEx Android package freshness before QA runs.

The guard is intentionally conservative: if the remote app-space page cannot be
parsed into a reliable version signal, it returns status=unknown and blocks test
execution until a human confirms how to proceed.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

CHANNELS: dict[str, dict[str, str]] = {
    "dev": {
        "page_url": "https://app-space.1bullex.com/android-dev-onebullex",
        "package": "com.onemore.onebullex.dev",
    },
    "prod": {
        "page_url": "https://app-space.1bullex.com/android-onebullex",
        "package": "com.onemore.onebullex",
    },
}

DEFAULT_SERIAL = "SM02G4061923909"
CACHE_ROOT = Path(os.environ.get("OBX_APK_CACHE", "/tmp/onebullex-android-qa/apk-cache"))


class VersionGuardError(RuntimeError):
    pass


def run_cmd(cmd: list[str], check: bool = False) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False)
    if check and proc.returncode != 0:
        raise VersionGuardError(proc.stdout.strip() or f"Command failed: {' '.join(cmd)}")
    return proc


def adb_shell(serial: str, *args: str, check: bool = False) -> str:
    return run_cmd(["adb", "-s", serial, "shell", *args], check=check).stdout


def require_serial_ready(serial: str) -> None:
    if not shutil.which("adb"):
        raise VersionGuardError("adb not found on PATH. Install Android platform-tools or add adb to PATH.")
    proc = run_cmd(["adb", "devices"], check=False)
    devices: dict[str, str] = {}
    for line in proc.stdout.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2:
            devices[parts[0]] = parts[1]
    if serial not in devices:
        raise VersionGuardError(f"Requested serial {serial} is not in adb devices: {sorted(devices.items())}")
    if devices[serial] != "device":
        raise VersionGuardError(f"Device {serial} is {devices[serial]}; authorize USB debugging or reconnect.")


def parse_package_dump(text: str) -> dict[str, Any]:
    if "Unable to find package" in text or "Unknown package" in text:
        return {"installed": False}
    version_code = first_match(text, [r"versionCode=(\d+)", r"longVersionCode=(\d+)"])
    version_name = first_match(text, [r"versionName=([^\s]+)"])
    first_install = first_match(text, [r"firstInstallTime=([^\n]+)"])
    last_update = first_match(text, [r"lastUpdateTime=([^\n]+)"])
    return {
        "installed": bool(version_code or version_name or "Packages:" in text),
        "version_code": int(version_code) if version_code and version_code.isdigit() else None,
        "version_name": version_name,
        "first_install_time": first_install,
        "last_update_time": last_update,
    }


def get_device_package(serial: str, package: str, dry_run: bool = False) -> dict[str, Any]:
    if dry_run:
        return {
            "installed": True,
            "version_code": 100,
            "version_name": "0.0.100-dry-run",
            "first_install_time": "dry-run",
            "last_update_time": "dry-run",
        }
    require_serial_ready(serial)
    text = adb_shell(serial, "dumpsys", "package", package, check=False)
    return parse_package_dump(text)


def first_match(text: str, patterns: list[str], flags: int = re.IGNORECASE) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, flags)
        if match:
            return match.group(1).strip().strip('"\'')
    return None


def fetch_text(url: str, timeout: float = 20.0) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "onebullex-android-qa/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec: controlled URL from CLI/channel defaults.
        data = resp.read()
    return data.decode("utf-8", errors="replace")


def parse_remote_page(page_url: str, dry_run: bool = False) -> dict[str, Any]:
    if dry_run:
        return {
            "page_url": page_url,
            "http_status": "dry-run",
            "apk_url": "https://example.invalid/onebullex-dry-run.apk",
            "version_code": 100,
            "version_name": "0.0.100-dry-run",
            "metadata_source": "dry-run",
        }
    html = fetch_text(page_url)
    apk_url = find_apk_url(html, page_url)
    version_name = first_match(html, [
        r"versionName[\"']?\s*[:=]\s*[\"']([^\"'<>\s]+)",
        r"version_name[\"']?\s*[:=]\s*[\"']([^\"'<>\s]+)",
        r"版本(?:名称|号)?\s*[:：]?\s*([0-9]+(?:\.[0-9A-Za-z_-]+)+)",
        r"Version\s*[:：]?\s*([0-9]+(?:\.[0-9A-Za-z_-]+)+)",
        r"v([0-9]+(?:\.[0-9A-Za-z_-]+)+)",
    ])
    version_code = first_match(html, [
        r"versionCode[\"']?\s*[:=]\s*[\"']?(\d+)",
        r"version_code[\"']?\s*[:=]\s*[\"']?(\d+)",
        r"build(?:No|Number|Code)?[\"']?\s*[:=]\s*[\"']?(\d+)",
        r"构建(?:号|编号)?\s*[:：]?\s*(\d+)",
    ])
    return {
        "page_url": page_url,
        "http_status": "ok",
        "apk_url": apk_url,
        "version_code": int(version_code) if version_code and version_code.isdigit() else None,
        "version_name": version_name,
        "metadata_source": "page-html" if version_code or version_name or apk_url else "none",
    }


def find_apk_url(html: str, page_url: str) -> str | None:
    candidates: list[str] = []
    for pattern in [
        r"href=[\"']([^\"']+\.apk(?:\?[^\"']*)?)[\"']",
        r"src=[\"']([^\"']+\.apk(?:\?[^\"']*)?)[\"']",
        r"[\"'](https?://[^\"']+\.apk(?:\?[^\"']*)?)[\"']",
        r"(https?://[^\s\"'<>]+\.apk(?:\?[^\s\"'<>]*)?)",
    ]:
        candidates.extend(re.findall(pattern, html, flags=re.IGNORECASE))
    if not candidates:
        return None
    return urllib.parse.urljoin(page_url, candidates[0].replace("\\/", "/"))


def download_apk(apk_url: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(urllib.parse.urlparse(apk_url).path).name or "onebullex.apk"
    if not suffix.endswith(".apk"):
        suffix += ".apk"
    target = out_dir / suffix
    req = urllib.request.Request(apk_url, headers={"User-Agent": "onebullex-android-qa/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:  # nosec: user/channel controlled APK URL.
        target.write_bytes(resp.read())
    return target


def inspect_apk(apk_path: Path) -> dict[str, Any]:
    aapt = shutil.which("aapt")
    if aapt:
        proc = run_cmd([aapt, "dump", "badging", str(apk_path)], check=False)
        if proc.returncode == 0:
            line = proc.stdout.splitlines()[0] if proc.stdout.splitlines() else ""
            pkg = first_match(line, [r"name='([^']+)'"])
            code = first_match(line, [r"versionCode='(\d+)'"])
            name = first_match(line, [r"versionName='([^']*)'"])
            return {
                "inspector": "aapt",
                "package": pkg,
                "version_code": int(code) if code and code.isdigit() else None,
                "version_name": name,
            }
    apkanalyzer = shutil.which("apkanalyzer")
    if apkanalyzer:
        proc = run_cmd([apkanalyzer, "manifest", "print", str(apk_path)], check=False)
        if proc.returncode == 0:
            return {
                "inspector": "apkanalyzer",
                "package": first_match(proc.stdout, [r"package=\"([^\"]+)\""]),
                "version_code": maybe_int(first_match(proc.stdout, [r"android:versionCode=\"?(\d+)\"?"])),
                "version_name": first_match(proc.stdout, [r"android:versionName=\"([^\"]+)\""]),
            }
    return {"inspector": None, "package": None, "version_code": None, "version_name": None}


def maybe_int(value: str | None) -> int | None:
    return int(value) if value and value.isdigit() else None


def version_tuple(value: str | None) -> tuple[Any, ...] | None:
    if not value:
        return None
    parts: list[Any] = []
    for part in re.split(r"[._+\-]", value):
        if part == "":
            continue
        parts.append(int(part) if part.isdigit() else part.lower())
    return tuple(parts) if parts else None


def decide_status(device: dict[str, Any], remote: dict[str, Any]) -> tuple[str, str]:
    if not device.get("installed"):
        return "not_installed", "Package is not installed on the selected device."
    device_code = device.get("version_code")
    remote_code = remote.get("version_code")
    if device_code is not None and remote_code is not None:
        if int(device_code) < int(remote_code):
            return "outdated", f"Device versionCode {device_code} is older than remote {remote_code}."
        if int(device_code) > int(remote_code):
            return "latest", f"Device versionCode {device_code} is newer than remote {remote_code}; treating as acceptable."
        return "latest", f"Device versionCode {device_code} matches remote {remote_code}."
    device_name = version_tuple(device.get("version_name"))
    remote_name = version_tuple(remote.get("version_name"))
    if device_name is not None and remote_name is not None:
        if device_name < remote_name:
            return "outdated", f"Device versionName {device.get('version_name')} is older than remote {remote.get('version_name')}."
        if device_name > remote_name:
            return "latest", f"Device versionName {device.get('version_name')} is newer than remote {remote.get('version_name')}; treating as acceptable."
        return "latest", f"Device versionName {device.get('version_name')} matches remote {remote.get('version_name')}."
    return "unknown", "Remote version metadata could not be reliably compared with the installed package."


def recommended_action(status: str, remote: dict[str, Any]) -> str:
    if status == "latest":
        return "Continue QA with the currently installed package."
    if status in {"outdated", "not_installed"} and remote.get("apk_url"):
        return "Stop before QA. Ask the user to confirm installing the latest APK, then run with --allow-install-latest."
    if status in {"outdated", "not_installed"}:
        return "Stop before QA. Ask the user to confirm phone-driven download/install from the app-space page."
    return "Stop before QA. Ask the user to confirm whether the current package is acceptable or provide/install the latest APK."


def run_guard(args: argparse.Namespace) -> dict[str, Any]:
    channel = CHANNELS[args.channel]
    package = args.package or channel["package"]
    page_url = args.download_page or channel["page_url"]
    serial = args.serial or DEFAULT_SERIAL
    device = get_device_package(serial, package, dry_run=args.dry_run)
    remote = parse_remote_page(page_url, dry_run=args.dry_run)
    apk_inspection: dict[str, Any] | None = None
    downloaded_apk: str | None = None
    if args.inspect_apk and remote.get("apk_url") and not args.dry_run:
        apk_path = download_apk(str(remote["apk_url"]), Path(args.out_dir) / "downloads")
        downloaded_apk = str(apk_path)
        apk_inspection = inspect_apk(apk_path)
        if apk_inspection.get("version_code") is not None or apk_inspection.get("version_name"):
            remote["version_code"] = apk_inspection.get("version_code")
            remote["version_name"] = apk_inspection.get("version_name")
            remote["metadata_source"] = f"apk-{apk_inspection.get('inspector') or 'download'}"
    status, reason = decide_status(device, remote)
    result = {
        "generated": dt.datetime.now().isoformat(timespec="seconds"),
        "channel": args.channel,
        "page_url": page_url,
        "package": package,
        "serial": serial,
        "device_installed": device.get("installed", False),
        "device_version_name": device.get("version_name"),
        "device_version_code": device.get("version_code"),
        "device_first_install_time": device.get("first_install_time"),
        "device_last_update_time": device.get("last_update_time"),
        "remote_version_name": remote.get("version_name"),
        "remote_version_code": remote.get("version_code"),
        "remote_metadata_source": remote.get("metadata_source"),
        "apk_url": remote.get("apk_url"),
        "downloaded_apk": downloaded_apk,
        "apk_inspection": apk_inspection,
        "status": status,
        "reason": reason,
        "recommended_action": recommended_action(status, remote),
        "install_attempted": False,
        "install_result": None,
    }
    if args.allow_install_latest and status in {"outdated", "not_installed"}:
        install_result = install_latest(args, package, page_url, remote, downloaded_apk, apk_inspection)
        result.update(install_result)
        if install_result.get("install_exit_code") == 0:
            refreshed_device = get_device_package(serial, package, dry_run=args.dry_run)
            refreshed_status, refreshed_reason = decide_status(refreshed_device, remote)
            result.update({
                "device_installed": refreshed_device.get("installed", False),
                "device_version_name": refreshed_device.get("version_name"),
                "device_version_code": refreshed_device.get("version_code"),
                "device_first_install_time": refreshed_device.get("first_install_time"),
                "device_last_update_time": refreshed_device.get("last_update_time"),
                "status": refreshed_status,
                "reason": refreshed_reason,
                "recommended_action": recommended_action(refreshed_status, remote),
            })
    return result


def install_latest(args: argparse.Namespace, package: str, page_url: str, remote: dict[str, Any], downloaded_apk: str | None, apk_inspection: dict[str, Any] | None) -> dict[str, Any]:
    if args.dry_run:
        return {"install_attempted": True, "install_result": "dry-run: would install latest APK after human confirmation"}
    if not shutil.which("adb"):
        raise VersionGuardError("adb not found on PATH; cannot install APK.")
    apk_url = remote.get("apk_url")
    if not apk_url:
        run_cmd(["adb", "-s", args.serial or DEFAULT_SERIAL, "shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", page_url], check=False)
        return {
            "install_attempted": True,
            "install_result": "opened download page on phone; manual download/install confirmation required",
        }
    apk_path = Path(downloaded_apk) if downloaded_apk else download_apk(str(apk_url), Path(args.out_dir) / "downloads")
    inspection = apk_inspection or inspect_apk(apk_path)
    inspected_package = inspection.get("package")
    if not inspected_package:
        raise VersionGuardError("Downloaded APK could not be inspected; refusing to install silently.")
    if inspected_package != package:
        raise VersionGuardError(f"Downloaded APK package {inspected_package} does not match expected {package}; refusing to install.")
    proc = run_cmd(["adb", "-s", args.serial or DEFAULT_SERIAL, "install", "-r", str(apk_path)], check=False)
    return {
        "install_attempted": True,
        "install_result": proc.stdout.strip() or f"adb install exit={proc.returncode}",
        "install_exit_code": proc.returncode,
        "downloaded_apk": str(apk_path),
        "apk_inspection": inspection,
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Check whether the device has the latest OneBullEx Android package before QA.")
    p.add_argument("--channel", choices=sorted(CHANNELS), default="dev")
    p.add_argument("--serial", default=os.environ.get("ADB_SERIAL"))
    p.add_argument("--package", help="Override package name. Defaults by channel.")
    p.add_argument("--download-page", help="Override app-space download page URL.")
    p.add_argument("--out-dir", default=str(CACHE_ROOT))
    p.add_argument("--output", help="Write JSON result to this path.")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--version-check-only", action="store_true", help="Alias/documentation flag; the guard never installs unless --allow-install-latest is passed.")
    p.add_argument("--inspect-apk", action="store_true", help="Download a direct APK URL and inspect version metadata if tooling is available.")
    p.add_argument("--allow-install-latest", action="store_true", help="Install only after explicit human confirmation. Refuses uninspectable APKs.")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    result = run_guard(args)
    output = json.dumps(result, ensure_ascii=False, indent=2)
    print(output)
    if args.output:
        path = Path(args.output).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(output + "\n", encoding="utf-8")
    if result.get("status") == "latest":
        return 0
    return 10


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except VersionGuardError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
