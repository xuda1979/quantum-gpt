"""C-9447: C-9394 (s97 re-eval) must depend on C-9442 (leg script deploy).

Asserted against LIVE harness/state/QUEUE.json (same idiom as C-9446).
"""

import json
import os
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
QUEUE_PATH = os.path.join(HARNESS_DIR, "state", "QUEUE.json")


class TestC9447Dep9442(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(QUEUE_PATH):
            self.skipTest("QUEUE.json missing at " + QUEUE_PATH)
        with open(QUEUE_PATH, encoding="utf-8") as f:
            self.q = json.load(f)

    def test_c9394_depends_on_c9442(self):
        cards = [c for c in self.q["cards"] if c["id"] == "C-9394"]
        if not cards:
            self.skipTest("C-9394 not in QUEUE.json (purged or not yet created)")
        card = cards[0]
        self.assertIn("C-9442", card["deps"], "C-9394 missing dep C-9442")
