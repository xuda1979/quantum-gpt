"""C-9415: v4 training must dep on training data (C-9411) before launch.

CONTEXT: C-9387 (the original v4 training launch) is DEAD (superseded by
C-9430).  C-9395 is gone.  The living analog of the v4-training leg is
C-9430 (RE-LAUNCH v4 LoRA training on ASI3) -- it is the current card that
actually launches v4 training, taking over C-9387's role.  Since v4
training builds quantum-task SFT data from s97 failures, it MUST NOT be
dispatchable before C-9411 (the training-data construction card) is ready.

Asserted against the LIVE harness/state/QUEUE.json (same idiom as
C-9400/C-9407/C-9429): the queue is the source of truth, not a fixture.
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


class TestC9415TrainDataDep(unittest.TestCase):
    def setUp(self):
        self.assertTrue(os.path.exists(QUEUE_PATH), "QUEUE.json missing at " + QUEUE_PATH)
        self.q = load_live_queue()
        self.cards = by_id(self.q)

    def _deps(self, cid):
        self.assertIn(cid, self.cards, cid + " must exist in QUEUE.json")
        return self.cards[cid].get("deps") or []

    def test_C9430_v4_training_deps_include_C9411_training_data(self):
        deps = self._deps("C-9430")
        self.assertIn(
            "C-9411", deps, "C-9430 (v4 training launch) must dep on C-9411 (training data)"
        )

    def test_C9430_v4_training_dep_training_data_is_ready(self):
        if "C-9411" not in self.cards:
            self.skipTest("C-9411" + " not in QUEUE.json (purged or not yet created)")
        self.assertIn("C-9411", self.cards, "C-9411 must exist in QUEUE.json")
        c9411 = self.cards["C-9411"]
        self.assertNotEqual(c9411.get("status"), "dead", "C-9411 (training data) must not be dead")


if __name__ == "__main__":
    unittest.main()
