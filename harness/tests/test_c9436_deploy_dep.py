import json
import os
import sys
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
sys.path.insert(0, HARNESS_DIR)
QUEUE_PATH = os.path.join(HARNESS_DIR, "state", "QUEUE.json")


class T(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(QUEUE_PATH):
            self.skipTest("QUEUE.json missing at " + QUEUE_PATH)
        self.cards = {c["id"]: c for c in json.load(open(QUEUE_PATH))["cards"]}

    def test_c9403_is_dep(self):
        if "C-9394" not in self.cards:
            self.skipTest("C-9394 not in QUEUE.json (purged or rebuilt)")
        self.assertIn("C-9403", self.cards["C-9394"].get("deps") or [])


if __name__ == "__main__":
    unittest.main()
