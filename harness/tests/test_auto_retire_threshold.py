"""TDD test: auto_retire_high_bounce retires cards at bounce_count >= 3.

Cards with 3 bounces have failed 3 times and should be retired
so fresh cards can be queued. The old threshold of 4 left 3-bounce
cards stuck forever.
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import qgh


class AutoRetireThresholdTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="qgh-test-retire-")
        qgh.STATE = self.tmpdir
        qgh.save_json(
            os.path.join(self.tmpdir, "GOAL.json"),
            {
                "objective": "test",
                "status": "OPEN",
                "target_pass": "18/18",
            },
        )

    def _make_queue(self, cards):
        return {"seq": 9600, "cards": cards}

    def test_bounce_3_is_retired(self):
        """A card with bounce_count=3 should be retired."""
        queue = self._make_queue(
            [
                {
                    "id": "C-9701",
                    "title": "triple bounced",
                    "lane": "trainer-ops",
                    "status": "bounced",
                    "priority": 0,
                    "bounce_count": 3,
                    "acceptance": ["test acceptance criterion"],
                    "deps": [],
                    "gates": [],
                },
            ]
        )
        qgh.save_queue(self.tmpdir, queue)
        retired = qgh.auto_retire_high_bounce(self.tmpdir)
        self.assertEqual(retired, 1, "card with bounce_count=3 should be retired")
        queue2 = qgh.load_queue(self.tmpdir)
        card = qgh.find_card(queue2, "C-9701")
        self.assertEqual(card["status"], "dead")

    def test_bounce_2_is_not_retired(self):
        """A card with bounce_count=2 should NOT be retired."""
        queue = self._make_queue(
            [
                {
                    "id": "C-9702",
                    "title": "double bounced",
                    "lane": "trainer-ops",
                    "status": "bounced",
                    "priority": 0,
                    "bounce_count": 2,
                    "acceptance": ["test acceptance criterion"],
                    "deps": [],
                    "gates": [],
                },
            ]
        )
        qgh.save_queue(self.tmpdir, queue)
        retired = qgh.auto_retire_high_bounce(self.tmpdir)
        self.assertEqual(retired, 0, "card with bounce_count=2 should not be retired")


if __name__ == "__main__":
    unittest.main()
