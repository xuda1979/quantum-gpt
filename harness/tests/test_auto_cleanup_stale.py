"""TDD test: auto_cleanup_stale_running requeues running cards with dead PIDs."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import qgh


class AutoCleanupStaleRunningTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="qgh-test-clean-")
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

    def test_dead_pid_running_card_is_cleaned(self):
        """A running card with a dead PID should be requeued as bounced."""
        queue = self._make_queue(
            [
                {
                    "id": "C-9801",
                    "title": "stale running",
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
        cleaned = qgh.auto_cleanup_stale_running(self.tmpdir)
        self.assertEqual(cleaned, 1)
        queue2 = qgh.load_queue(self.tmpdir)
        card = qgh.find_card(queue2, "C-9801")
        self.assertEqual(card["status"], "bounced")
        self.assertEqual(card["bounce_count"], 1)

    def test_alive_pid_running_card_is_not_cleaned(self):
        """A running card with a live PID should NOT be cleaned."""
        my_pid = str(os.getpid())
        queue = self._make_queue(
            [
                {
                    "id": "C-9802",
                    "title": "live running",
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
        cleaned = qgh.auto_cleanup_stale_running(self.tmpdir)
        self.assertEqual(cleaned, 0)

    def test_no_claim_pid_running_card_is_cleaned(self):
        """A running card with no claimed_by is corrupt and should be cleaned."""
        queue = self._make_queue(
            [
                {
                    "id": "C-9803",
                    "title": "no claim",
                    "lane": "trainer-ops",
                    "status": "running",
                    "claimed_by": None,
                    "priority": 0,
                    "bounce_count": 0,
                    "acceptance": ["test acceptance criterion"],
                    "deps": [],
                    "gates": [],
                },
            ]
        )
        qgh.save_queue(self.tmpdir, queue)
        cleaned = qgh.auto_cleanup_stale_running(self.tmpdir)
        self.assertEqual(cleaned, 1)


if __name__ == "__main__":
    unittest.main()
