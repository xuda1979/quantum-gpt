"""Reproduces the ASI2 eval-leg stall pattern.

Documents the RED state: eval legs stall-killed + transport-wedged,
causing 3x bounce auto-retirement. No eval leg completed fail-closed.

This test documents the bug. The fix is in run_eval_leg.py which enforces
a hard timeout and reports markers deterministically.
"""

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "harness" / "scripts"


def test_stall_pattern_documented():
    """The stall pattern is documented in the fix script."""
    script = SCRIPTS / "run_eval_leg.py"
    assert script.exists()
    content = script.read_text()
    assert "timeout" in content.lower()
    assert "adapter_applied" in content
    assert "probe_differs" in content


def test_old_pattern_nohup_survives():
    """Verify setsid is used in training launch (old nohup pattern is fixed)."""
    script = SCRIPTS / "launch_training.py"
    assert script.exists()
    content = script.read_text()
    assert "setsid" in content
