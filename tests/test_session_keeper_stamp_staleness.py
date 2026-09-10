"""B-088: the keeper's cycle-top stamp published STALE probe verdicts as fresh.

Under test (scripts/session_keeper.sh, main loop):
  B-052c moved the heartbeat stamp to the TOP of the cycle so liveness cannot
  depend on how long a probe takes. Correct for liveness -- but the two stamps
  it publishes are the PREVIOUS cycle's verdicts.

  At process start those carry-over vars were initialised HEADLESS_STAMP="ok" /
  DAEMONS_STAMP="unknown" (B-068 fixed only the STATUS var to STARTING). So when
  the very first probe FAILS:

    cycle 1 top : stamp publishes HEADLESS_STAMP="ok"  (never measured)
    cycle 1 poll: headless_ok -> false, HEADLESS_STAMP="failed"
    cycle 2 top : stamp publishes HEADLESS_STAMP="failed"   <-- correct
    cycle 3 top : stamp publishes HEADLESS_STAMP="failed"   <-- cycle 2 was fine

  ...but the mirror case is the dangerous one: any cycle whose probe SUCCEEDS
  publishes "ok" for the whole of the next cycle even while that next probe is
  failing and STATUS has already gone HEALING. Live evidence 2026-09-11
  06:39:26: /tmp/session_keeper_state.json read
      {"status": "HEALING", "headless_auth": "ok", ...}
  while scripts/session_keeper.log read
      "ERROR no live process with valid auth found; keep retrying every cycle".

  A probe that has not run THIS cycle must report "unknown", never the previous
  cycle's "ok" (three-state rule, skill 5.4.1: a resource that has measured
  nothing is UNKNOWN, never OK). Same defect class as the tick-#334 false READY.

Fix spec: the carry-over re-initialisation must happen in the window between the
cycle-top stamp and the reset of STATUS for the new cycle -- i.e. BEFORE the new
probe the stamp claims a verdict for. This test asserts the ORDER, because that
is the whole defect: the value is right, the point in the cycle is wrong.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "session_keeper.sh"

CARRYOVER = ("HEADLESS_STAMP", "DAEMONS_STAMP")


def _lines() -> list[str]:
    return SCRIPT.read_text(encoding="utf-8").splitlines()


def _cycle_top_stamp_index(lines: list[str]) -> int:
    """Index of the B-052c cycle-top stamp_state call inside the main loop."""
    for i, line in enumerate(lines):
        if "stamp_state" in line and '"$HEADLESS_STAMP"' in line and '"$DAEMONS_STAMP"' in line:
            return i
    raise AssertionError("cycle-top stamp_state call not found in session_keeper.sh")


def test_carryover_is_reset_between_cycle_top_stamp_and_next_cycle_reset() -> None:
    """The stamp claims a verdict for the new cycle; that verdict must be reset
    to unknown in the same window, or the heartbeat advertises a stale probe."""
    lines = _lines()
    stamp_at = _cycle_top_stamp_index(lines)
    status_reset = None
    for j in range(stamp_at + 1, len(lines)):
        if re.search(r'^\s*STATUS="OK"\s*$', lines[j]):
            status_reset = j
            break
    assert (
        status_reset is not None
    ), 'no STATUS="OK" reset found after the cycle-top stamp -- main loop shape changed'
    window = "\n".join(lines[stamp_at + 1 : status_reset])
    for var in CARRYOVER:
        assert re.search(rf"^\s*{var}=\"unknown\"\s*$", window, re.M), (
            f'{var} is not reset to "unknown" between the cycle-top stamp_state call '
            f'(line {stamp_at + 1}) and the STATUS="OK" reset (line {status_reset + 1}). '
            "The cycle-top stamp publishes the PREVIOUS cycle's verdict, so the durable "
            'heartbeat can read headless_auth="ok" for a whole cycle while this '
            "cycle's probe is failing and STATUS has already gone HEALING."
        )


def test_carryover_initial_values_are_not_ok() -> None:
    """Process start initialises carry-over: nothing has been measured yet, so no
    probe verdict may be published as ok (B-068's lesson, applied to both vars)."""
    text = SCRIPT.read_text(encoding="utf-8")
    for var in CARRYOVER:
        m = re.search(rf'^{var}="(\w+)"', text, re.M)
        assert m, f"{var} initialiser not found"
        assert m.group(1) != "ok", (
            f'{var} is initialised to "ok" before any probe has run -- a keeper that dies '
            "having completed zero cycles would read as healthy"
        )
