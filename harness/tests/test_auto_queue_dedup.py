"""TDD test: auto_queue_training deduplication prevents excessive card piling."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import qgh


class AutoQueueDedupTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="qgh-test-dedup-")
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

    def _bounced_trainer(self, cid, bounce):
        return {
            "id": cid,
            "title": "bounced training",
            "lane": "trainer-ops",
            "status": "bounced",
            "claimed_by": None,
            "priority": 0,
            "bounce_count": bounce,
            "acceptance": ["test acceptance criterion that is long enough"],
            "deps": [],
            "gates": [],
        }

    def test_three_bounced_trainers_blocks_new_queue(self):
        """When 3+ bounced trainer-ops cards exist, do not queue more."""
        queue = self._make_queue(
            [
                self._bounced_trainer("C-9901", 1),
                self._bounced_trainer("C-9902", 2),
                self._bounced_trainer("C-9903", 1),
            ]
        )
        qgh.save_queue(self.tmpdir, queue)
        card = qgh.auto_queue_training(self.tmpdir)
        self.assertIsNone(card, "should not queue when 3+ bounced trainers exist")

    def test_two_bounced_trainers_still_queues(self):
        """When only 2 bounced trainer-ops cards exist, still queue new."""
        queue = self._make_queue(
            [
                self._bounced_trainer("C-9901", 1),
                self._bounced_trainer("C-9902", 2),
            ]
        )
        qgh.save_queue(self.tmpdir, queue)
        card = qgh.auto_queue_training(self.tmpdir)
        self.assertIsNotNone(card, "should queue when only 2 bounced trainers exist")


if __name__ == "__main__":
    unittest.main()
