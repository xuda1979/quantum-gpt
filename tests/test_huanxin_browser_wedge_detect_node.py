"""Venv-visible canary for the C-10450 browser-wedge detection node tests.

C-10450: headless Chrome daemon flap. The browser wedges at runtime and
context.newPage() throws 'Protocol error (Target.createTarget): Failed to open
a new tab' (380 occurrences in huanxin_all_keepalive.log, 04:45-05:13Z). The
fix detects that error and relaunches ONLY the browser in-process so the daemon
never needs a full keeper restart for a browser wedge.

This shim surfaces the node suite in the canonical venv pytest run.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST_JS = ROOT / "tests" / "test_huanxin_browser_wedge_detect.js"


def test_node_browser_wedge_suite_passes() -> None:
    result = subprocess.run(
        ["node", str(TEST_JS)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert (
        result.returncode == 0
    ), f"node browser-wedge suite failed ({result.returncode}):\n{result.stdout}\n{result.stderr}"
    assert "browser-wedge-detect tests passed" in result.stdout
