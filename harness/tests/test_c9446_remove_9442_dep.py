"""C-9446: Remove C-9442 dep from C-9443. C-9443 is a dep-fixer card that just
edits QUEUE.json to add C-9442 as a dep of C-9394 -- it does NOT need C-9442
to be done first.

ACCEPTANCE (from the card):
- C-9443 deps set to [] in QUEUE.json
- C-9443 dispatched and adds C-9442 to C-9394 deps

Asserted against the LIVE harness/state/QUEUE.json (same idiom as C-9434):
the queue is the source of truth, not a fixture.
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


class TestC9446Remove9442Dep(unittest.TestCase):
    def setUp(self):
        self.assertTrue(os.path.exists(QUEUE_PATH), "QUEUE.json missing at " + QUEUE_PATH)
        self.q = load_live_queue()
        self.cards = by_id(self.q)

    def _deps(self, cid):
        self.assertIn(cid, self.cards, cid + " must exist in QUEUE.json")
        return self.cards[cid].get("deps") or []

    def test_C9443_deps_empty(self):
        if "C-9443" not in self.cards:
            self.skipTest("C-9443 not in QUEUE.json (purged or not yet created)")
        deps = self._deps("C-9443")
        self.assertEqual(
            deps, [], "C-9443 (dep-fixer) must have no deps -- it just edits QUEUE.json"
        )

    def test_C9394_deps_include_C9442(self):
        if "C-9394" not in self.cards:
            self.skipTest("C-9394 not in QUEUE.json (purged or not yet created)")
        deps = self._deps("C-9394")
        self.assertIn("C-9442", deps, "C-9394 (s97 re-eval) must dep on C-9442 (leg script deploy)")


if __name__ == "__main__":
    unittest.main()
