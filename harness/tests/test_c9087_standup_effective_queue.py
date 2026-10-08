"""Card C-9087: standup EFFECTIVE-QUEUE count + per-row DISPATCHABLE column.

C-9083 was minted on the premise "queue nearly empty" while the 04:23Z
standup showed 9 P0 rows conflating running/blocked/dead-dep-ready rows.
Both the planner top-up and the dead-dep escalator act on EFFECTIVE
dispatchability, which no human-readable artifact exposed -- the next
planner decision again needed a 200KB QUEUE.json grep. This pins the
standup renderer to MEASURE it:

    EFFECTIVE-QUEUE = cards that are ready AND deps-not-dead AND
    unclaimed (rendered as a count line in the QUEUE section), plus a
    per-row disp column: Y, or N with the dead dep NAMED on the row.

Zero queue-semantics change: this only renders what is already in
QUEUE.json; no card status transitions.
"""

from __future__ import annotations

import os
import sys
import unittest

_HARNESS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_REPO_ROOT = os.path.dirname(_HARNESS_DIR)
for p in (_HARNESS_DIR, _REPO_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

import harness_lib as H  # noqa: E402


def _card(cid, status, deps=(), claimed_by=None):
    c = H.new_card(
        title=f"card {cid}",
        lane="planner",
        why="goal edge: C-9087 fixture row",
        acceptance=["fixture row"],
        card_id=cid,
        deps=list(deps),
    )
    c["status"] = status
    c["claimed_by"] = claimed_by
    return c


def _fixture_queue():
    return {
        "cards": [
            _card("C-OK", "ready"),  # the ONLY dispatchable card
            _card("C-DP", "ready", deps=["C-DEAD"]),  # ready, dead dep
            _card("C-CLM", "ready", claimed_by="w2"),  # ready, claimed
            _card("C-RUN", "running", claimed_by="w1"),  # not ready
            _card("C-BLK", "blocked"),  # not ready
            _card("C-DEAD", "dead"),  # the dead dep itself
        ]
    }


def _render(queue):
    return H.render_standup(dict(objective="obj", status="OPEN"), queue, dict(agents=[]), 1)


def _rows(out):
    rows = dict()
    for line in out.splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) > 2 and parts[2].startswith("C-"):
            rows[parts[2]] = line
    return rows


class TestStandupEffectiveQueue(unittest.TestCase):
    def test_effective_queue_counts_only_ready_deps_not_dead_unclaimed(self):
        """6-card fixture (ready+deps-ok / ready+dead-dep / ready+claimed /
        running / blocked / dead) yields EFFECTIVE-QUEUE=1."""
        out = _render(_fixture_queue())
        self.assertIn("EFFECTIVE-QUEUE: 1 (ready+deps-not-dead+unclaimed)", out)

    def test_rows_mark_dispatchable_and_name_dead_dep(self):
        """Per-row disp column: Y on the dispatchable card; N with the dead
        dep NAMED on the blocked-dep card; N with reason elsewhere."""
        out = _render(_fixture_queue())
        rows = _rows(out)
        self.assertIn("C-OK", rows)
        self.assertIn("C-DP", rows)
        self.assertIn("| Y |", rows["C-OK"])
        self.assertIn("N (dead dep: C-DEAD)", rows["C-DP"])
        self.assertIn("N (claimed)", rows["C-CLM"])
        self.assertIn("N (not ready)", rows["C-RUN"])
        self.assertIn("N (not ready)", rows["C-BLK"])


if __name__ == "__main__":
    unittest.main()
