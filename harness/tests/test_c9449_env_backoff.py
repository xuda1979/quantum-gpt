"""C-9449: environmental failures (box down, API error) must NOT trigger
the global dispatch backoff. The global backoff blocks ALL lanes including
non-box-bound ones (planner, fixer, qa-steward), which is wrong — those
lanes can still make progress when boxes are down.

RED 2026-09-20: when boxes are down, box-bound workers fail environmentally,
rapidly filling the global counter (threshold=2), blocking all dispatch
for 15 minutes. Only TRUE spawn failures (worker crashes, missing brief)
should trigger the global backoff.
"""

import os
import sys
import tempfile
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
sys.path.insert(0, HARNESS_DIR)

import harness_lib as H  # noqa: E402


class TestEnvironmentalBackoff(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="c9449-")
        self.ops = H.load_ops(self.tmp)

    def test_environmental_failure_does_not_trip_global_backoff(self):
        """An environmental failure (ok=False, environmental=True) must not
        increment the global consecutive_spawn_failures counter."""
        # Simulate 3 environmental failures
        for _ in range(3):
            self.ops = H.note_spawn_result(
                self.tmp,
                self.ops,
                ok=False,
                card="C-9500",
                environmental=True,
            )
        # Global counter must NOT have tripped
        self.assertIsNone(
            self.ops.get(H.BACKOFF_PATH_KEY), "environmental failures must not trip global backoff"
        )

    def test_real_spawn_failure_trips_global_backoff(self):
        """A real spawn failure (ok=False, no environmental flag) must
        still trip the global backoff after threshold."""
        for _ in range(H.SPAWN_FAIL_THRESHOLD):
            self.ops = H.note_spawn_result(
                self.tmp,
                self.ops,
                ok=False,
                card="C-9501",
            )
        self.assertIsNotNone(
            self.ops.get(H.BACKOFF_PATH_KEY), "real failures must trip global backoff"
        )


if __name__ == "__main__":
    unittest.main()
