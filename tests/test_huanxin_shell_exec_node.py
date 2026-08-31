"""Venv-visible canary for the huanxin /exec wedge-fix node tests
(2026-08-27 infra mission — debug lane #21).

The wedge fixes (per-call timeouts, terminal-row bound, exec hard deadline,
withLock stuck-lock watchdog) live in browser-automation/*.js and are tested
by tests/test_huanxin_shell_exec.js with a plain-node runner (no framework).
This shim surfaces them in the canonical venv pytest run: a simulated
renderer stall must NOT wedge any path.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST_JS = ROOT / "tests" / "test_huanxin_shell_exec.js"


def test_node_wedge_fix_suite_passes() -> None:
    result = subprocess.run(
        ["node", str(TEST_JS)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert (
        result.returncode == 0
    ), f"node wedge-fix suite failed ({result.returncode}):\n{result.stdout}\n{result.stderr}"
    assert "all wedge-fix tests passed" in result.stdout
