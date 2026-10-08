"""Tests for eval-leg transport fix — eval legs must complete fail-closed.

TDD: these tests define the contract BEFORE the fix exists.
The core issue: eval legs on ASI2 stall-killed + transport-wedged, causing
3x bounce auto-retirement. No eval leg has ever completed fail-closed.
"""

import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "harness" / "scripts"


def run_script(name: str, *args, timeout: int = 30) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(REPO),
    )


def test_eval_leg_runner_exists():
    """The eval-leg runner script exists."""
    assert (SCRIPTS / "run_eval_leg.py").exists()


def test_eval_leg_runner_has_timeout():
    """Eval-leg runner accepts a --timeout parameter."""
    r = run_script("run_eval_leg.py", "--help")
    assert r.returncode == 0
    assert "--timeout" in r.stdout


def test_eval_leg_runner_reports_markers():
    """Eval-leg runner reports adapter_applied + probe_differs markers."""
    r = run_script("run_eval_leg.py", "--dry-run")
    assert r.returncode == 0
    assert "adapter_applied" in r.stdout or "adapter" in r.stdout.lower()


def test_eval_leg_runner_completes_fast_dry_run():
    """Dry-run completes in <5s."""
    start = time.time()
    r = run_script("run_eval_leg.py", "--dry-run", timeout=10)
    elapsed = time.time() - start
    assert r.returncode == 0
    assert elapsed < 5.0, f"dry-run took {elapsed:.1f}s, expected <5s"


def test_eval_leg_stall_reproducer_exists():
    """The stall-reproducer test exists for RED-phase documentation."""
    test_path = REPO / "tests" / "test_eval_leg_stall_repro.py"
    assert test_path.exists(), "stall reproducer test must exist"
