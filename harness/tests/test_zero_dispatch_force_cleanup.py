"""TDD test: zero-dispatch streak tracking and force cleanup."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import qgh


class ZeroDispatchForceCleanupTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="qgh-test-zdfc-")
        qgh.STATE = self.tmpdir
        qgh.save_json(
            os.path.join(self.tmpdir, "GOAL.json"),
            {
                "objective": "test",
                "status": "OPEN",
                "target_pass": "18/18",
            },
        )
        qgh.save_json(
            os.path.join(self.tmpdir, "OPS.json"),
            {
                "consecutive_spawn_failures": 0,
                "backoff_until_utc": None,
            },
        )

    def test_zero_dispatch_streak_persists_in_ops(self):
        """zero_dispatch_streak should be loadable from OPS.json."""
        ops = qgh.load_ops(self.tmpdir)
        ops["zero_dispatch_streak"] = 3
        qgh.save_ops(self.tmpdir, ops)
        ops2 = qgh.load_ops(self.tmpdir)
        self.assertEqual(ops2.get("zero_dispatch_streak"), 3)

    def test_auto_cleanup_stale_running_returns_zero_on_empty_queue(self):
        """auto_cleanup_stale_running should return 0 when no stale cards exist."""
        queue = {"seq": 9600, "cards": []}
        qgh.save_queue(self.tmpdir, queue)
        fleet = {"agents": []}
        qgh.save_fleet(self.tmpdir, fleet)
        cleaned = qgh.auto_cleanup_stale_running(self.tmpdir)
        self.assertEqual(cleaned, 0)


if __name__ == "__main__":
    unittest.main()
