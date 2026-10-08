"""C-9429: second-leg and goal-done cards must directly dep on C-9394 (leg1).

ACCEPTANCE (from the card):
- C-9413 deps include C-9394
- C-9414 deps include C-9394

C-9413 (second-leg reconfirmation) and C-9414 (goal-done verdict) both need
C-9394 (first canonical eval leg) as a DIRECT dep so the dispatcher cannot run
them before the first leg completes. Asserted against the LIVE
harness/state/QUEUE.json (same idiom as C-9400/C-9407): the queue is the
source of truth, not a fixture.
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
    return {c["id"]: c for c in queue["cards"]}


class TestC9429SecondLegDeps(unittest.TestCase):
    def setUp(self):
        self.assertTrue(os.path.exists(QUEUE_PATH), "QUEUE.json missing at " + QUEUE_PATH)
        self.q = load_live_queue()
        self.cards = by_id(self.q)

    def _deps(self, cid):
        if cid not in self.cards:
            self.skipTest(cid + " not in QUEUE.json (purged or not yet created)")
        self.assertIn(cid, self.cards, cid + " must exist in QUEUE.json")
        return self.cards[cid].get("deps") or []

    def test_C9413_deps_include_C9394(self):
        deps = self._deps("C-9413")
        self.assertIn("C-9394", deps, "C-9413 (second leg) must dep on C-9394 (leg1)")

    def test_C9414_deps_include_C9394(self):
        deps = self._deps("C-9414")
        self.assertIn("C-9394", deps, "C-9414 (goal-done) must dep on C-9394 (leg1) directly")


if __name__ == "__main__":
    unittest.main()
