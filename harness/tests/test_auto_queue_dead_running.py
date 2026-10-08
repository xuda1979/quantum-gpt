"""TDD test: auto_queue_training must not be blocked by a dead running card."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import qgh


class AutoQueueDeadRunningTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="qgh-test-aq-")
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

    def test_dead_running_trainer_does_not_block_new_queue(self):
        queue = self._make_queue(
            [
                {
                    "id": "C-9601",
                    "title": "dead training",
                    "lane": "trainer-ops",
                    "status": "running",
                    "claimed_by": "99999",
                    "priority": 0,
                    "bounce_count": 0,
                    "acceptance": ["test acceptance criterion"],
                    "deps": [],
                    "gates": [],
                },
            ]
        )
        qgh.save_queue(self.tmpdir, queue)
        try:
            os.kill(99999, 0)
            self.skipTest("PID 99999 unexpectedly alive")
        except (ProcessLookupError, PermissionError):
            pass

        card = qgh.auto_queue_training(self.tmpdir)
        self.assertIsNotNone(card, "should queue new card when running trainer has dead PID")
        self.assertEqual(card["lane"], "trainer-ops")

    def test_alive_running_trainer_blocks_new_queue(self):
        my_pid = str(os.getpid())
        queue = self._make_queue(
            [
                {
                    "id": "C-9602",
                    "title": "live training",
                    "lane": "trainer-ops",
                    "status": "running",
                    "claimed_by": my_pid,
                    "priority": 0,
                    "bounce_count": 0,
                    "acceptance": ["test acceptance criterion"],
                    "deps": [],
                    "gates": [],
                },
            ]
        )
        qgh.save_queue(self.tmpdir, queue)
        card = qgh.auto_queue_training(self.tmpdir)
        self.assertIsNone(card, "should NOT queue when live trainer-ops is running")

    def test_bounced_trainer_does_not_block_new_queue(self):
        queue = self._make_queue(
            [
                {
                    "id": "C-9603",
                    "title": "bounced training",
                    "lane": "trainer-ops",
                    "status": "bounced",
                    "claimed_by": None,
                    "priority": 0,
                    "bounce_count": 3,
                    "acceptance": ["test acceptance criterion"],
                    "deps": [],
                    "gates": [],
                },
            ]
        )
        qgh.save_queue(self.tmpdir, queue)
        card = qgh.auto_queue_training(self.tmpdir)
        self.assertIsNotNone(card, "should queue new card when existing trainer cards are bounced")


if __name__ == "__main__":
    unittest.main()
