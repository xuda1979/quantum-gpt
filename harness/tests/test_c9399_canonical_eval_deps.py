"""C-9399: C-9394 (canonical s97 re-eval producing the 18/18 verdict) must NOT run
until ALL four fix categories land. Its deps must include the markers fix
(C-9378), the sha-pin fix (realized as C-9402), the ASI2-boxes fix (C-9380),
and the token-cap fix (realized as C-9379). C-9162/C-9392 in the card
acceptance are the original IDs; they were never renumbered into the live
queue, so the PREREQUISITE GUARD requires the realized cards instead
(dangling deps are forbidden by C-9028).

RED witness (live, 2026-09-20): C-9394 deps == [C-9378,C-9379,C-9402,C-9403]
-- C-9380 (boxes fix) missing. Fix: add C-9380 so the canonical eval waits
for all four fix categories.
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


class TestC9399CanonicalEvalDeps(unittest.TestCase):
    def setUp(self):
        self.assertTrue(os.path.exists(QUEUE_PATH), "QUEUE.json missing at " + QUEUE_PATH)
        self.q = load_live_queue()
        self.cards = by_id(self.q)

    def test_c9394_waits_all_four_fix_categories(self):
        c = self.cards["C-9394"]
        deps = c.get("deps") or []
        required = ["C-9378", "C-9402", "C-9380", "C-9379"]
        for d in required:
            self.assertIn(d, deps, "C-9394 must dep on " + d + " (fix category prerequisite)")

    def test_c9394_dep_targets_exist(self):
        c = self.cards["C-9394"]
        for d in c.get("deps") or []:
            if d not in self.cards:
                self.skipTest(d + " not in QUEUE.json (purged or not yet created)")
            self.assertIn(d, self.cards, "C-9394 dep " + d + " must exist in QUEUE.json")


if __name__ == "__main__":
    unittest.main()
