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
        self.cards = {c["id"]: c for c in json.load(open(QUEUE_PATH))["cards"]}

    def test_c9403_is_dep(self):
        self.assertIn("C-9403", self.cards["C-9394"].get("deps") or [])


if __name__ == "__main__":
    unittest.main()
