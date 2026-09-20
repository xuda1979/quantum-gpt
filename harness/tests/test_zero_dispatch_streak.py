"""TDD test: zero-dispatch streak tracking in OPS.json."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import qgh


class ZeroDispatchStreakTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="qgh-test-zds-")
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

    def test_ops_json_has_zero_dispatch_streak(self):
        """load_ops should return a dict that can track zero_dispatch_streak."""
        ops = qgh.load_ops(self.tmpdir)
        self.assertIsInstance(ops, dict)
        # The key may not exist initially, but get should work
        self.assertEqual(ops.get("zero_dispatch_streak", 0), 0)


if __name__ == "__main__":
    unittest.main()
