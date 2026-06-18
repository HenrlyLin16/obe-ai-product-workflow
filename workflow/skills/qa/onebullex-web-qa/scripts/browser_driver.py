#!/usr/bin/env python3
"""Browser driver for onebullex-web-qa.

Supports two execution modes:
- `runtime=codex`: Skill-driven interactive execution through Codex Browser/Chrome
  plugins. This runtime is report-oriented and intentionally does not inspect
  browser storage.
- `runtime=playwright`: local execution through the bundled Playwright CLI
  wrapper. This runtime is intended for public/stateless flows first.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class BrowserDriverError(RuntimeError):
    pass


@dataclass
class DriverObservation:
    ok: bool
    note: str
    dom: str = ""
    screenshot: str = ""
    data: dict[str, Any] | None = None


class BrowserDriver:
    def __init__(
        self,
        browser_mode: str = "iab",
        viewport: str = "desktop",
        locale: str = "zh-cn",
        runtime: str = "codex",
        dry_run: bool = False,
        out_dir: Path | None = None,
        session_name: str | None = None,
    ) -> None:
        self.browser_mode = browser_mode
        self.viewport = viewport
        self.locale = locale
        self.runtime = runtime
        self.dry_run = dry_run
        self.out_dir = out_dir
        self.current_url = "https://testnet.1bullex.com/"
        self.last_dom = self._dry_dom()
        self.session_name = session_name or f"obx-web-{browser_mode}-{viewport}"
        self._pwcli = Path(os.environ.get("PWCLI", str(Path.home() / ".codex/skills/playwright/scripts/playwright_cli.sh")))
        self._playwright_ready = False
        self._allow_live_playwright = runtime == "playwright" and not dry_run

    def _require_codex_plugin_runtime(self) -> None:
        raise BrowserDriverError(
            "This flow is configured for Codex interactive execution. "
            "Use the Browser/Chrome plugin through the Skill prompt, or run with "
            "`--runtime playwright` for supported stateless flows."
        )

    def _ensure_playwright_ready(self) -> None:
        if self.dry_run or self.runtime != "playwright":
            return
        if self.browser_mode != "iab":
            raise BrowserDriverError(
                "Local Playwright runtime currently supports only `browser_mode=iab`. "
                "Use Codex Chrome plugin for login-state/account flows."
            )
        if not self._pwcli.exists():
            raise BrowserDriverError(f"Playwright CLI wrapper not found: {self._pwcli}")
        if not self._playwright_ready:
            args = ["open", self.current_url or "https://testnet.1bullex.com/"]
            if self.viewport == "desktop":
                self._run_pwcli(["open", self.current_url])
                self._run_pwcli(["resize", "1280", "720"])
            elif self.viewport == "mobile":
                self._run_pwcli(["open", self.current_url])
                self._run_pwcli(["resize", "390", "844"])
            else:
                self._run_pwcli(args)
            self._playwright_ready = True

    def _run_pwcli(self, args: list[str], timeout: int | float | None = None) -> dict[str, Any]:
        cmd = [str(self._pwcli), "--session", self.session_name, *args, "--json"]
        try:
            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise BrowserDriverError(f"playwright-cli timed out after {timeout}s: {' '.join(cmd)}") from exc
        if proc.returncode != 0:
            raise BrowserDriverError(proc.stdout.strip() or f"playwright-cli failed: {' '.join(cmd)}")
        text = proc.stdout.strip()
        if not text:
            return {}
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"raw": text}

    def goto(self, url: str) -> DriverObservation:
        self.current_url = url
        if self.dry_run:
            self.last_dom = self._dry_dom(url)
            return DriverObservation(True, f"Dry-run goto {url}", self.last_dom)
        if self.runtime == "codex":
            self._require_codex_plugin_runtime()
        self._ensure_playwright_ready()
        self._run_pwcli(["goto", url])
        self.last_dom = self._snapshot_text()
        return DriverObservation(True, f"Playwright goto {url}", self.last_dom)

    def click(self, selector: dict[str, Any]) -> DriverObservation:
        if self.dry_run:
            ok = self._selector_present(selector)
            return DriverObservation(ok, f"Dry-run click {'matched' if ok else 'did not match'} selector {selector}", self.last_dom)
        if self.runtime == "codex":
            self._require_codex_plugin_runtime()
        self._ensure_playwright_ready()
        target = self._first_working_target(selector, command="click")
        self.last_dom = self._snapshot_text()
        return DriverObservation(True, f"Playwright click {target}", self.last_dom)

    def type_text(self, selector: dict[str, Any], value: str) -> DriverObservation:
        if self.dry_run:
            ok = self._selector_present(selector)
            scrubbed = "***" if value else ""
            return DriverObservation(ok, f"Dry-run type {scrubbed} into selector {selector}", self.last_dom)
        if self.runtime == "codex":
            self._require_codex_plugin_runtime()
        self._ensure_playwright_ready()
        target = self._first_working_target(selector, command="fill", value=value)
        self.last_dom = self._snapshot_text()
        return DriverObservation(True, f"Playwright fill {target}", self.last_dom)

    def wait_for(self, selector: dict[str, Any] | None = None, ms: int | None = None) -> DriverObservation:
        if self.dry_run:
            if ms:
                time.sleep(min(ms / 1000.0, 0.02))
                return DriverObservation(True, f"Dry-run waited {ms}ms", self.last_dom)
            ok = self._selector_present(selector or {})
            return DriverObservation(ok, f"Dry-run wait_for {'matched' if ok else 'missing'} selector {selector}", self.last_dom)
        if self.runtime == "codex":
            self._require_codex_plugin_runtime()
        self._ensure_playwright_ready()
        if ms:
            time.sleep(max(int(ms), 0) / 1000.0)
        elif selector:
            deadline = time.time() + 10.0
            while time.time() < deadline:
                text = self._snapshot_text()
                if self._selector_matches_text(selector, text):
                    self.last_dom = text
                    return DriverObservation(True, "Playwright wait_for matched selector", self.last_dom)
                time.sleep(0.5)
            return DriverObservation(False, f"Playwright wait_for timed out for selector {selector}", self.last_dom)
        self.last_dom = self._snapshot_text()
        return DriverObservation(True, "Playwright wait_for completed", self.last_dom)

    def assert_visible(self, selector: dict[str, Any]) -> DriverObservation:
        if self.dry_run:
            ok = self._selector_present(selector)
            return DriverObservation(ok, f"Selector {'visible' if ok else 'not visible'}: {selector}", self.last_dom)
        if self.runtime == "codex":
            self._require_codex_plugin_runtime()
        self._ensure_playwright_ready()
        text = self._snapshot_text()
        ok = self._selector_matches_text(selector, text)
        self.last_dom = text
        return DriverObservation(ok, f"Selector {'visible' if ok else 'not visible'}: {selector}", self.last_dom, data={"match_source": "snapshot-text"})

    def assert_not_visible(self, selector: dict[str, Any]) -> DriverObservation:
        obs = self.assert_visible(selector)
        return DriverObservation(not obs.ok, f"Selector {'not visible' if not obs.ok else 'unexpectedly visible'}: {selector}", obs.dom, data=obs.data)

    def assert_text(self, expected_any: list[str] | None = None, expected_all: list[str] | None = None) -> DriverObservation:
        text = self._current_text()
        if expected_all:
            missing = [v for v in expected_all if v not in text]
            return DriverObservation(not missing, f"Text all check missing={missing}", text)
        if expected_any:
            found = [v for v in expected_any if v in text]
            return DriverObservation(bool(found), f"Text any check found={found}", text)
        return DriverObservation(True, "No text expectations provided", text)

    def assert_url(self, pattern: str) -> DriverObservation:
        current = self._current_url()
        ok = bool(re.search(pattern, current)) or pattern in current
        return DriverObservation(ok, f"URL {current} matches {pattern}: {ok}", self.last_dom)

    def snapshot(self, step_dir: Path, label: str = "snapshot", force_screenshot: bool = False) -> dict[str, str]:
        step_dir.mkdir(parents=True, exist_ok=True)
        dom_path = step_dir / "dom-summary.txt"
        dom_path.write_text(self.summarize_dom(), encoding="utf-8")
        html_path = step_dir / "dom.txt"
        html_path.write_text(self.last_dom, encoding="utf-8")
        evidence = {"dom_summary": str(dom_path), "dom": str(html_path)}
        if force_screenshot:
            shot = step_dir / "screenshot.png"
            if self.dry_run or self.runtime == "codex":
                shot.write_bytes(b"")
            else:
                try:
                    data = self._run_pwcli(["screenshot"], timeout=20)
                    raw = str(data.get("result", ""))
                    match = re.search(r"\(([^)]+\\.png)\)", raw) or re.search(r'"file":"([^"]+)"', raw)
                    if match and Path(match.group(1)).exists():
                        Path(match.group(1)).replace(shot)
                    else:
                        shot.write_bytes(b"")
                except BrowserDriverError:
                    shot.write_bytes(b"")
            evidence["screenshot"] = str(shot)
        return evidence

    def summarize_dom(self, max_chars: int = 4000) -> str:
        text = re.sub(r"<[^>]+>", " ", self.last_dom)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:max_chars] + ("\n" if text else "")

    def _current_text(self) -> str:
        if self.dry_run or self.runtime == "codex":
            return self.last_dom
        payload = self._run_pwcli(["eval", "document.body.innerText"])
        raw = payload.get("result", "")
        text = raw if isinstance(raw, str) else json.dumps(raw, ensure_ascii=False)
        self.last_dom = text
        return text

    def _current_url(self) -> str:
        if self.dry_run or self.runtime == "codex":
            return self.current_url
        payload = self._run_pwcli(["eval", "location.href"])
        raw = payload.get("result", "")
        if isinstance(raw, str):
            current = raw.strip('"')
        else:
            current = str(raw)
        self.current_url = current
        return current

    def _snapshot_text(self) -> str:
        if self.dry_run or self.runtime == "codex":
            return self.last_dom
        payload = self._run_pwcli(["snapshot"])
        snapshot = payload.get("snapshot", "")
        if isinstance(snapshot, str) and snapshot:
            self.last_dom = snapshot
        return self.last_dom

    def _selector_matches_text(self, selector: dict[str, Any], text: str) -> bool:
        if not selector:
            return True
        candidates = self._selector_text_candidates(selector)
        if any(token and token in text for token in candidates):
            return True
        regex = selector.get("text_regex")
        if regex and re.search(str(regex), text, flags=re.IGNORECASE):
            return True
        return False

    def _selector_text_candidates(self, selector: dict[str, Any]) -> list[str]:
        values: list[str] = []
        for key in ("text", "name", "testid", "css"):
            raw = selector.get(key)
            if not raw:
                continue
            token = str(raw).strip()
            if token:
                values.append(token)
        regex = selector.get("text_regex")
        if regex:
            parts = [part.strip() for part in str(regex).split("|")]
            values.extend([part for part in parts if part])
        return values

    def _selector_present(self, selector: dict[str, Any]) -> bool:
        dom = self.last_dom
        if not selector:
            return True
        if selector.get("testid") and f'data-testid="{selector["testid"]}"' in dom:
            return True
        if selector.get("text") and str(selector["text"]) in dom:
            return True
        if selector.get("text_regex") and re.search(str(selector["text_regex"]), dom):
            return True
        if selector.get("css"):
            css = str(selector["css"])
            if "table" in css and "table" in dom.lower():
                return True
            if "toast" in css and "toast" in dom.lower():
                return True
            if "order" in css and "order" in dom.lower():
                return True
            if "position" in css and "position" in dom.lower():
                return True
            if "history" in css and "history" in dom.lower():
                return True
            if "market" in css and "market" in dom.lower():
                return True
            if "price" in css and "price" in dom.lower():
                return True
            if "qty" in css and "qty" in dom.lower():
                return True
        if selector.get("role") and selector.get("name") and str(selector["name"]) in dom:
            return True
        return False

    def _pw_targets(self, selector: dict[str, Any]) -> list[str]:
        targets: list[str] = []
        if selector.get("text"):
            targets.append(f'text={selector["text"]}')
        if selector.get("role") and selector.get("name"):
            targets.append(f'text={selector["name"]}')
        if selector.get("css"):
            targets.append(str(selector["css"]))
        if selector.get("testid"):
            targets.append(f'data-testid={selector["testid"]}')
        if selector.get("text_regex"):
            for part in [part.strip() for part in str(selector["text_regex"]).split("|") if part.strip()]:
                targets.append(f"text={part}")
        deduped: list[str] = []
        seen: set[str] = set()
        for target in targets:
            if target not in seen:
                deduped.append(target)
                seen.add(target)
        if not deduped:
            raise BrowserDriverError(f"Unsupported selector for Playwright target: {selector}")
        return deduped

    def _first_working_target(self, selector: dict[str, Any], command: str, value: str | None = None) -> str:
        errors: list[str] = []
        for target in self._pw_targets(selector):
            args = [command, target] if value is None else [command, target, value]
            try:
                self._run_pwcli(args)
                return target
            except BrowserDriverError as exc:
                errors.append(f"{target}: {exc}")
        raise BrowserDriverError("; ".join(errors) or f"No working target for selector {selector}")

    def _dry_dom(self, url: str = "/") -> str:
        payload = {
            "mode": self.browser_mode,
            "viewport": self.viewport,
            "locale": self.locale,
            "runtime": self.runtime,
            "url": url,
        }
        return f"""<!doctype html><html lang="zh-CN"><body data-testid="dry-run-root">
<nav>
  <a data-testid="nav-market">市场</a><a data-testid="nav-spot">现货</a><a data-testid="nav-futures">合约</a><a data-testid="nav-assets">资产</a>
  <button data-testid="login-entry">登录</button><button data-testid="user-menu-trigger">账户 UID 123456</button><span data-testid="user-uid">UID 123456</span>
</nav>
<main>
  <section data-testid="market-page">市场 行情 <table data-testid="market-ticker-table"><tr><th data-testid="market-sort-symbol">币种</th><th data-testid="market-sort-price">价格</th><th data-testid="market-sort-change">涨跌</th></tr><tr><td>BTCUSDT</td><td>100000</td><td>1.2%</td></tr></table></section>
  <section data-testid="withdraw-page">链上提币 提币地址
    <input data-testid="withdraw-address-input" placeholder="提币地址"/>
    <button data-testid="withdraw-address-book-entry">地址簿</button>
    <div data-testid="withdraw-address-dropdown">当前网络暂无常用地址 可通过地址簿添加 <button data-testid="withdraw-add-address">添加地址</button></div>
    <label><input data-testid="save-to-address-book-checkbox" type="checkbox"/>添加到地址簿</label>
    <input data-testid="withdraw-remark-input" placeholder="备注"/>
    <section data-testid="address-book-page">提币地址簿 全部 免验证 不可用 选用 编辑 删除</section>
    <div data-testid="security-verify-dialog">安全验证 邮箱验证码 谷歌验证码</div>
  </section>
  <section data-testid="spot-trade-page">现货 买入 卖出 <input data-testid="trade-price-input" placeholder="价格"/><input data-testid="trade-qty-input" placeholder="数量"/><button data-testid="trade-open-long-btn">买入</button></section>
  <section data-testid="futures-trade-page">合约 开仓 平仓 <button data-testid="trade-open-long-btn">开多</button><button data-testid="trade-open-short-btn">开空</button><input data-testid="trade-price-input"/><input data-testid="trade-qty-input"/></section>
  <section data-testid="asset-page">资产 总资产 <div data-testid="asset-spot-balance">现货 USDT 100</div><div data-testid="asset-futures-margin">合约 保证金 100</div></section>
  <table data-testid="order-table"><tr><td>暂无订单</td></tr></table><table data-testid="position-table"><tr><td>暂无持仓</td></tr></table><table data-testid="history-table"><tr><td>暂无成交</td></tr></table>
  <div data-testid="toast-container" class="toast">提示</div>
</main>
<script type="application/json" id="dry-run-meta">{json.dumps(payload, ensure_ascii=False)}</script>
</body></html>"""
