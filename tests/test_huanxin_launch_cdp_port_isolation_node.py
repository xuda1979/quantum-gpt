"""Venv-visible canary for the per-env CDP port isolation fix (2026-09-18).

huanxin_browser_launch.js hardcoded `--remote-debugging-port=9224`, so every
env's Chrome (ASI1/ASI2/ASI3) tried to bind ASI1's CDP port -> the 2nd/3rd env
crashed with "Target page, context or browser has been closed" and the envs
could not stay up simultaneously. The launch must honor HUANXIN_CDP_PORT.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST_JS = ROOT / "tests" / "test_huanxin_launch_cdp_port_isolation.js"


def test_node_cdp_port_isolation_suite_passes() -> None:
    result = subprocess.run(
        ["node", str(TEST_JS)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert (
        result.returncode == 0
    ), f"node CDP port isolation suite failed ({result.returncode}):\n{result.stdout}\n{result.stderr}"
    assert "All CDP port isolation tests passed" in result.stdout
