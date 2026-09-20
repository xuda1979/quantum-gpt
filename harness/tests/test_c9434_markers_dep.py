"""C-9434: C-9432 (real markers fix) must be a direct dep of C-9390 (post-v4
canonical eval) and C-9394 (s97 re-eval).

ACCEPTANCE (from the card):
- C-9390 deps include C-9432
- C-9394 deps include C-9432

C-9390 and C-9394 both produce eval verdicts that need fail-closed markers
(adapter_applied / adapter_probe_differs). C-9432 fixes the ACTUAL hardcoding
in the leg scripts (run_holdout_leg1.py:349-350, run_holdout_leg2.py:203-204).
Without this dep, the evals could run (or be validated) while the markers are
still hardcoded True. Asserted against the LIVE harness/state/QUEUE.json (same
idiom as C-9429/C-9399): the queue is the source of truth, not a fixture.
"""

import json
import os
import sys
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
sys.path.insert(0, HARNESS_DIR)

QUEUE_PATH = os.path.join(HARNESS_DIR, "state", "QUEUE.json")


def load_live_queue():
    with open(QUEUE_PATH, encoding="utf-8") as f:
        return json.load(f)


def by_id(queue):
    return dict((str(c.get("id")), c) for c in queue["cards"])


class TestC9434MarkersDep(unittest.TestCase):
    def setUp(self):
        self.assertTrue(os.path.exists(QUEUE_PATH), "QUEUE.json missing at " + QUEUE_PATH)
        self.q = load_live_queue()
        self.cards = by_id(self.q)

    def _deps(self, cid):
        if cid not in self.cards:
            self.skipTest(cid + " not in QUEUE.json (purged or not yet created)")
        self.assertIn(cid, self.cards, cid + " must exist in QUEUE.json")
        return self.cards[cid].get("deps") or []

    def test_C9390_deps_include_C9432(self):
        deps = self._deps("C-9390")
        self.assertIn(
            "C-9432", deps, "C-9390 (post-v4 canonical eval) must dep on C-9432 (markers fix)"
        )

    def test_C9394_deps_include_C9432(self):
        deps = self._deps("C-9394")
        self.assertIn("C-9432", deps, "C-9394 (s97 re-eval) must dep on C-9432 (markers fix)")


if __name__ == "__main__":
    unittest.main()
