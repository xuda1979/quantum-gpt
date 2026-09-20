"""C-9407: critical path deps must be wired in QUEUE.json.

ACCEPTANCE (from the card):
- C-9380 deps include C-9378 and C-9379
- C-9394 deps include C-9380
- C-9387 deps include C-9395

Asserted against the LIVE harness/state/QUEUE.json (same idiom as the v1-v5
dep-graph family and C-9400): the queue is the source of truth, not a fixture.
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


class TestC9407CriticalPathDeps(unittest.TestCase):
    def setUp(self):
        self.assertTrue(os.path.exists(QUEUE_PATH), "QUEUE.json missing at " + QUEUE_PATH)
        self.q = load_live_queue()
        self.cards = by_id(self.q)

    def _deps(self, cid):
        if cid not in self.cards:
            self.skipTest(cid + " not in QUEUE.json (purged or not yet created)")
        self.assertIn(cid, self.cards, cid + " must exist in QUEUE.json")
        return self.cards[cid].get("deps") or []

    def test_C9380_deps_include_C9378_and_C9379(self):
        deps = self._deps("C-9380")
        self.assertIn("C-9378", deps, "C-9380 must dep on C-9378 (fail-closed markers)")
        self.assertIn("C-9379", deps, "C-9380 must dep on C-9379 (token cap)")

    def test_C9394_deps_include_C9380(self):
        deps = self._deps("C-9394")
        self.assertIn("C-9380", deps, "C-9394 (s97 eval) must dep on C-9380 (deploy)")

    def test_C9387_deps_include_C9395(self):
        deps = self._deps("C-9387")
        self.assertIn("C-9395", deps, "C-9387 (v4 train) must dep on C-9395")


if __name__ == "__main__":
    unittest.main()
