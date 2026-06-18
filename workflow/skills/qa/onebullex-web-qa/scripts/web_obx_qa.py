#!/usr/bin/env python3
"""Compatibility CLI for OneBullEx Web QA."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
FLOW_RUNNER = SCRIPT_DIR / "flow_runner.py"

if __name__ == "__main__":
    raise SystemExit(subprocess.run([sys.executable, str(FLOW_RUNNER), *sys.argv[1:]]).returncode)
