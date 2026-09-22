"""Tests for the single daemon reconciler — failure-class-aware remedies.

The old system had 4+ competing supervisors (keeper, heartbeat, keepalive,
asi1-keepalive) fighting each other. This test defines the ONE reconciler
contract: classify failure, apply ONE remedy, never kill during boot.
"""

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "harness" / "scripts" / "daemon_reconciler.py"


def test_reconciler_exists():
    assert SCRIPT.exists()


def test_reconciler_classifies_failures():
    """classify_health() maps health payloads to failure classes."""
    r = subprocess.run(
        [
            sys.executable,
            "-c",
            """
import sys
sys.path.insert(0, 'harness/scripts')
from daemon_reconciler import classify_health
assert classify_health(None) == 'conn_refused'
assert classify_health({'startupState': 'ready'}) == 'healthy'
assert classify_health({'startupState': 'booting'}) == 'booting'
assert classify_health({'startupState': 'error', 'startupError': 'browser closed'}) == 'browser_closed'
assert classify_health({'startupState': 'error', 'startupError': 'login_required'}) == 'auth_drift'
assert classify_health({'startupState': 'error', 'startupError': 'other'}) == 'unknown_error'
print('OK')
""",
        ],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(REPO),
    )
    assert r.returncode == 0, r.stderr
    assert "OK" in r.stdout


def test_reconciler_remedy_map():
    """Each failure class has exactly ONE remedy."""
    r = subprocess.run(
        [
            sys.executable,
            "-c",
            """
import sys
sys.path.insert(0, 'harness/scripts')
from daemon_reconciler import REMEDIES
assert REMEDIES['healthy'] == 'none'
assert REMEDIES['booting'] == 'wait'
assert REMEDIES['conn_refused'] == 'relaunch_daemon'
assert REMEDIES['browser_closed'] == 'relaunch_daemon'
assert REMEDIES['auth_drift'] == 'cookie_bridge'
assert REMEDIES['unknown_error'] == 'relaunch_after_threshold'
print('OK')
""",
        ],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(REPO),
    )
    assert r.returncode == 0, r.stderr
    assert "OK" in r.stdout


def test_reconciler_never_kills_booting():
    """The booting state NEVER triggers a kill — this was the old storm bug."""
    r = subprocess.run(
        [
            sys.executable,
            "-c",
            """
import sys
sys.path.insert(0, 'harness/scripts')
from daemon_reconciler import should_relaunch
# booting NEVER relaunches regardless of duration
assert should_relaunch('booting', bad_for_s=9999) is False
# conn_refused relaunches after short delay
assert should_relaunch('conn_refused', bad_for_s=60) is True
# browser_closed relaunches after 120s bad
assert should_relaunch('browser_closed', bad_for_s=130) is True
assert should_relaunch('browser_closed', bad_for_s=60) is False
print('OK')
""",
        ],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(REPO),
    )
    assert r.returncode == 0, r.stderr
    assert "OK" in r.stdout


def test_reconciler_dry_run_mode():
    """Reconciler supports --dry-run for safe testing."""
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--dry-run", "--box", "ASI3"],
        capture_output=True,
        text=True,
        timeout=15,
        cwd=str(REPO),
    )
    assert r.returncode == 0, r.stderr
    assert "CLASS:" in r.stdout or "REMEDY:" in r.stdout
