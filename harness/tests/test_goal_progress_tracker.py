"""TDD test: GoalProgressTracker detects goal-level stalls."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import qgh


class GoalProgressTrackerTest(unittest.TestCase):
    def test_records_improvement(self):
        tracker = qgh.GoalProgressTracker(stall_threshold_ticks=5)
        tracker.record_tick(1, 3)
        tracker.record_tick(2, 5)
        self.assertEqual(tracker.best_pass(), 5)
        self.assertEqual(tracker.ticks_since_improvement(), 0)
        self.assertFalse(tracker.is_stalled())

    def test_detects_stall(self):
        tracker = qgh.GoalProgressTracker(stall_threshold_ticks=3)
        tracker.record_tick(1, 3)
        tracker.record_tick(2, 3)
        tracker.record_tick(3, 3)
        tracker.record_tick(4, 3)
        self.assertTrue(tracker.is_stalled())
        self.assertEqual(tracker.ticks_since_improvement(), 3)

    def test_no_stall_with_recent_improvement(self):
        tracker = qgh.GoalProgressTracker(stall_threshold_ticks=3)
        tracker.record_tick(1, 3)
        tracker.record_tick(2, 3)
        tracker.record_tick(3, 5)
        self.assertFalse(tracker.is_stalled())
        self.assertEqual(tracker.ticks_since_improvement(), 0)

    def test_status_string(self):
        tracker = qgh.GoalProgressTracker(stall_threshold_ticks=2)
        tracker.record_tick(1, 3)
        tracker.record_tick(2, 3)
        tracker.record_tick(3, 3)
        status = tracker.status()
        self.assertIn("stalled", status)
        self.assertIn("3/18", status)


if __name__ == "__main__":
    unittest.main()
