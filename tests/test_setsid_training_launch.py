"""Tests for setsid-based training launch — training survives daemon restarts.

TDD: these tests define the contract BEFORE the implementation exists.
"""

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "harness" / "scripts"


def test_launch_script_exists():
    """The setsid training launch script exists."""
    assert (SCRIPTS / "launch_training.py").exists()


def test_launch_script_uses_setsid():
    """Launch script uses setsid to create a new session."""
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "launch_training.py"), "--dry-run"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"exit {r.returncode}: {r.stderr}"
    assert "setsid" in r.stdout, "launch command must use setsid"


def test_launch_script_writes_probe():
    """Launch script writes probe to harness/state/probes/train.json."""
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "launch_training.py"), "--dry-run"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(REPO),
    )
    assert r.returncode == 0
    assert "train.json" in r.stdout or "probe" in r.stdout.lower()


def test_boot_verify_script_exists():
    """The boot-verify script exists."""
    assert (SCRIPTS / "boot_verify_training.py").exists()


def test_boot_verify_completes_fast():
    """Boot-verify completes in <30s even with no training running."""
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "boot_verify_training.py"), "--box", "ASI3"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(REPO),
    )
    # Should complete quickly, report NOT_RUNNING if no training
    assert r.returncode == 0
    assert "STATUS:" in r.stdout


def test_launch_command_has_no_nohup_only():
    """Launch must use setsid, not just nohup (nohup alone doesn't survive daemon restart)."""
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "launch_training.py"), "--dry-run"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(REPO),
    )
    assert r.returncode == 0
    output = r.stdout
    assert "setsid" in output
    # nohup is OK as a supplement but setsid must be present
