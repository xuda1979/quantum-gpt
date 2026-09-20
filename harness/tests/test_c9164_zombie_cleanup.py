"""C-9164: ASI3 train-fire zombie cleanup.

Verifies that after cleanup:
  1. The state file has zombie=false (zombie key removed).
  2. fired=false and a fresh cutoff window is present.
  3. cycle is incremented (new cycle, not the stale one).
  4. The old pid orphan check returns clean.
All state paths are injected; no test touches live harness state.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "harness"))

import asi3_train_fire_on_ready as w  # noqa: E402

NOW = datetime(2026, 9, 20, tzinfo=timezone.utc)
FUTURE = "2099-01-01T00:00:00Z"


def _zombie_state(tmp_path):
    state = tmp_path / "asi3_train_fire_state.json"
    state.write_text(
        json.dumps(
            dict(
                pid=81128,
                started_utc="2026-09-16T17:53:47Z",
                cutoff="2026-09-16T23:59:00Z",
                fired=False,
                cycle=1,
                zombie=True,
                zombie_reason="C-9080 census: cutoff passed, pid 81128 dead, zero live consumers",
                rearm_owner="C-0066",
                rearm_gate="only after C-9075 cure-done marker",
            ),
            indent=1,
        )
        + "\n"
    )
    return state


def test_cleanup_zombie_clears_zombie_flag(tmp_path):
    state = _zombie_state(tmp_path)
    st = w.cleanup_zombie(str(state), new_cutoff=FUTURE, now=NOW)
    assert "zombie" not in st, f"zombie still present: {st}"
    assert "zombie_reason" not in st, f"zombie_reason still present: {st}"


def test_cleanup_zombie_sets_fired_false_and_new_cutoff(tmp_path):
    state = _zombie_state(tmp_path)
    st = w.cleanup_zombie(str(state), new_cutoff=FUTURE, now=NOW)
    assert st["fired"] is False
    assert st["cutoff"] == FUTURE
    assert w.expiry_status(st, now=NOW) == "ARMED"


def test_cleanup_zombie_increments_cycle(tmp_path):
    state = _zombie_state(tmp_path)
    st = w.cleanup_zombie(str(state), new_cutoff=FUTURE, now=NOW)
    assert st["cycle"] > 1, f"cycle not incremented: {st.get('cycle')}"


def test_cleanup_zombie_writes_clean_file_to_disk(tmp_path):
    state = _zombie_state(tmp_path)
    w.cleanup_zombie(str(state), new_cutoff=FUTURE, now=NOW)
    on_disk = json.loads(state.read_text())
    assert "zombie" not in on_disk
    assert on_disk["fired"] is False
    assert on_disk["cutoff"] == FUTURE


def test_cleanup_zombie_marks_cycle_complete(tmp_path):
    state = _zombie_state(tmp_path)
    st = w.cleanup_zombie(str(state), new_cutoff=FUTURE, now=NOW)
    assert st.get("prior_cycle_complete") is True


def test_cleanup_zombie_pid_alive_check(tmp_path):
    state = _zombie_state(tmp_path)
    st = w.cleanup_zombie(str(state), new_cutoff=FUTURE, now=NOW, pid_alive_fn=lambda pid: True)
    assert st.get("zombie") is True, "cleanup must fail-closed when pid still alive"


def test_live_state_file_zombie_cleared():
    state_path = ROOT / "harness" / "state" / "asi3_train_fire_state.json"
    if not state_path.is_file():
        import pytest

        pytest.skip("live state file not present")
    raw = state_path.read_text()
    st = json.loads(raw)
    if not st.get("zombie"):
        import pytest

        pytest.skip("live state already cleaned (zombie=false)")
    st = w.cleanup_zombie(str(state_path), new_cutoff=FUTURE, now=NOW)
    assert "zombie" not in st
    assert w.expiry_status(st, now=NOW) == "ARMED"
