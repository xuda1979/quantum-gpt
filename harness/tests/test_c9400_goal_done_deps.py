"""C-9400: C-9393 (goal-done composite verification) is a terminal card
that must NOT run before its eval verdicts exist. Its deps must include
C-9394 (canonical eval producing the 18/18 verdict) and C-9391 (second-leg
reconfirmation). Without the canonical-eval dep edge, C-9393 could be
dispatched before any eval verdict exists and pass goal_done with a
fabricated/empty composite.

Asserted against the LIVE harness/state/QUEUE.json (same idiom as the v1-v5
dep-graph family): the queue is the source of truth, not a fixture.

RED witness (measured live): C-9393 deps == C-9390,C-9391 -- C-9394
(canonical eval) missing. Fix: add C-9394 to C-9393 deps.
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


class TestC9400GoalDoneDeps(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(QUEUE_PATH):
            self.skipTest("QUEUE.json missing at " + QUEUE_PATH)
        self.q = load_live_queue()
        self.cards = by_id(self.q)

    def test_C9393_in_queue(self):
        if "C-9393" not in self.cards:
            self.skipTest("C-9393" + " not in QUEUE.json (purged or not yet created)")
        self.assertIn("C-9393", self.cards, "C-9393 must exist in QUEUE.json")

    def test_C9393_deps_include_canonical_eval_and_second_leg(self):
        if "C-9393" not in self.cards:
            self.skipTest("C-9393 not in QUEUE.json (purged or rebuilt)")
        # ACCEPTANCE: C-9393 depends_on includes C-9394 (canonical eval) and
        # C-9391 (second-leg reconfirmation) in QUEUE.json.
        c = self.cards["C-9393"]
        deps = c.get("deps") or []
        self.assertIn("C-9394", deps, "C-9393 must dep on C-9394 (canonical eval)")
        self.assertIn("C-9391", deps, "C-9393 must dep on C-9391 (second-leg reconfirm)")

    def test_C9393_dep_targets_exist(self):
        if "C-9393" not in self.cards:
            self.skipTest("C-9393 not in QUEUE.json (purged or rebuilt)")
        # Every C-9393 dep edge must resolve to a real card (no dangling).
        c = self.cards["C-9393"]
        for d in c.get("deps") or []:
            self.assertIn(d, self.cards, "C-9393 dep " + d + " must exist in QUEUE.json")


if __name__ == "__main__":
    unittest.main()
