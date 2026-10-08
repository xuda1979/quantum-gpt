"""TDD test: auto_cleanup_stale_running also cleans fleet zombies."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import qgh


class FleetZombieCleanupTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="qgh-test-fz-")
        qgh.STATE = self.tmpdir
        qgh.save_json(
            os.path.join(self.tmpdir, "GOAL.json"),
            {
                "objective": "test",
                "status": "OPEN",
                "target_pass": "18/18",
            },
        )

    def test_fleet_zombie_is_cleaned(self):
        """A fleet entry with a dead PID should be marked stopped."""
        queue = {
            "seq": 9600,
            "cards": [
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
            ],
        }
        qgh.save_queue(self.tmpdir, queue)
        fleet = {
            "agents": [
                {
                    "card": "C-9801",
                    "pid": 99999,
                    "status": "running",
                    "lane": "trainer-ops",
                    "started_utc": "2026-09-20T10:00:00Z",
                },
            ]
        }
        qgh.save_fleet(self.tmpdir, fleet)

        cleaned = qgh.auto_cleanup_stale_running(self.tmpdir)
        self.assertGreaterEqual(cleaned, 1)

        fleet2 = qgh.load_fleet(self.tmpdir)
        agent = fleet2["agents"][0]
        self.assertEqual(agent["status"], "stopped")

    def test_fleet_alive_entry_not_cleaned(self):
        """A fleet entry with a live PID should NOT be marked stopped."""
        my_pid = os.getpid()
        queue = {
            "seq": 9600,
            "cards": [
                {
                    "id": "C-9802",
                    "title": "live running",
                    "lane": "trainer-ops",
                    "status": "running",
                    "claimed_by": str(my_pid),
                    "priority": 0,
                    "bounce_count": 0,
                    "acceptance": ["test acceptance criterion"],
                    "deps": [],
                    "gates": [],
                },
            ],
        }
        qgh.save_queue(self.tmpdir, queue)
        fleet = {
            "agents": [
                {
                    "card": "C-9802",
                    "pid": my_pid,
                    "status": "running",
                    "lane": "trainer-ops",
                    "started_utc": "2026-09-20T10:00:00Z",
                },
            ]
        }
        qgh.save_fleet(self.tmpdir, fleet)

        cleaned = qgh.auto_cleanup_stale_running(self.tmpdir)
        self.assertEqual(cleaned, 0)

        fleet2 = qgh.load_fleet(self.tmpdir)
        agent = fleet2["agents"][0]
        self.assertEqual(agent["status"], "running")


if __name__ == "__main__":
    unittest.main()
