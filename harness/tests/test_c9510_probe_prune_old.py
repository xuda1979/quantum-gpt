"""C-9510 RED: old probe files must be pruned to prevent disk bloat."""

import os
import sys
import time
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
sys.path.insert(0, HARNESS_DIR)
import harness_lib as H  # noqa: E402
import qgh  # noqa: E402


class TestProbePruneOld(unittest.TestCase):
    def setUp(self):
        self._orig_state = qgh.STATE
        qgh.STATE = os.path.join(
            os.environ.get("QGH_STATE_DIR", "/tmp/qgh-test"), "probe_prune_test"
        )
        os.makedirs(os.path.join(qgh.STATE, "agents"), exist_ok=True)
        os.makedirs(os.path.join(qgh.STATE, "locks"), exist_ok=True)
        os.makedirs(os.path.join(qgh.STATE, "probes"), exist_ok=True)
        os.makedirs(os.path.join(qgh.STATE, "standups"), exist_ok=True)

    def tearDown(self):
        qgh.STATE = self._orig_state

    def test_old_probes_pruned(self):
        """Probe files older than 7 days should be pruned during tick."""
        probes_dir = os.path.join(qgh.STATE, "probes")
        # Create old probe files (8 days old)
        old_time = time.time() - (8 * 24 * 3600)
        for i in range(10):
            p = os.path.join(probes_dir, f"old-probe-{i}.json")
            with open(p, "w") as f:
                f.write("{}")
            os.utime(p, (old_time, old_time))
        # Create recent probe files (1 hour old)
        recent_time = time.time() - 3600
        for i in range(3):
            p = os.path.join(probes_dir, f"recent-probe-{i}.json")
            with open(p, "w") as f:
                f.write("{}")
            os.utime(p, (recent_time, recent_time))

        # Run prune
        pruned = H.prune_old_probes(qgh.STATE, max_age_days=7)

        self.assertEqual(pruned, 10, "10 old probes should be pruned")
        remaining = os.listdir(probes_dir)
        self.assertEqual(len(remaining), 3, "3 recent probes should remain")


if __name__ == "__main__":
    unittest.main()
