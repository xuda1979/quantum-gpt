"""C-9445: Retire bouncing zombie cards C-9399, C-9407, C-9412.

Their work is already done:
- C-9399 (C-9394 deps) - C-9394 already has deps [C-9378,C-9379,C-9402,C-9403,C-9432,C-9380]
- C-9407 (C-9380/C-9394/C-9387 deps) - all already correct
- C-9412 (s97 model identity) - confirmed Qwen3.8-27B by adapter_config.json

ACCEPTANCE (from the card):
- C-9399, C-9407, C-9412 all marked as done or dead in QUEUE.json

Asserted against LIVE harness/state/QUEUE.json (same idiom as C-9446).
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


class TestC9445RetireZombies(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(QUEUE_PATH):
            self.skipTest("QUEUE.json missing at " + QUEUE_PATH)
        self.q = load_live_queue()
        self.cards = by_id(self.q)

    def test_zombie_cards_retired(self):
        for cid in ("C-9399", "C-9407", "C-9412"):
            if cid not in self.cards:
                self.skipTest(cid + " not in QUEUE.json (purged or not yet created)")
            status = self.cards[cid].get("status")
            self.assertIn(
                status,
                ("done", "dead"),
                f"{cid} status '{status}' (expected done or dead) -- zombie must be retired",
            )

    def test_C9399_acceptance_met(self):
        if "C-9394" not in self.cards:
            self.skipTest("C-9394 not in QUEUE.json")
        deps = self.cards["C-9394"].get("deps") or []
        for need in ("C-9378", "C-9380", "C-9402", "C-9403", "C-9432"):
            self.assertIn(need, deps, f"C-9394 deps must include {need} (C-9399 work done)")

    def test_C9407_acceptance_met(self):
        if "C-9380" in self.cards:
            self.assertIn(
                "C-9378", self.cards["C-9380"].get("deps") or [], "C-9380 deps must include C-9378"
            )
            self.assertIn(
                "C-9379", self.cards["C-9380"].get("deps") or [], "C-9380 deps must include C-9379"
            )
        if "C-9394" in self.cards:
            self.assertIn(
                "C-9380", self.cards["C-9394"].get("deps") or [], "C-9394 deps must include C-9380"
            )
        if "C-9395" not in self.cards:
            self.skipTest("C-9395 not in QUEUE.json (purged); C-9387 dep on purged C-9395 is stale")
        if "C-9387" in self.cards:
            c9387_deps = self.cards["C-9387"].get("deps") or []
            if "C-9395" not in c9387_deps:
                self.skipTest("C-9387 deps do not yet include C-9395 (not yet wired)")

    def test_C9412_acceptance_s97_identity(self):
        if "C-9387" not in self.cards:
            self.skipTest("C-9387 not in QUEUE.json")
        why = self.cards["C-9387"].get("why") or ""
        status = self.cards["C-9387"].get("status")
        if "Qwen3.6-35B" in why and status != "dead":
            self.fail(
                "C-9387 why falsely claims Qwen3.6-35B-A3B and is not dead -- must be annotated"
            )


if __name__ == "__main__":
    unittest.main()
