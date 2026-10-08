"""C-9532: the tick must call auto_queue_training so training auto-relaunches.

The auto_queue_training function (C-9531) exists and is tested, but the tick
never calls it. This means if training stops (crash, OOM, wedge), the harness
will NOT automatically relaunch it -- a critical gap on the path to 18/18.

RED: this test must FAIL until cmd_tick calls auto_queue_training.
"""

import inspect
import os
import sys
import unittest

_HARNESS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _HARNESS_DIR not in sys.path:
    sys.path.insert(0, _HARNESS_DIR)

import qgh  # noqa: E402


class TestTickCallsAutoTraining(unittest.TestCase):
    def test_tick_source_contains_auto_queue_training(self):
        """cmd_tick source must contain a call to auto_queue_training."""
        src = inspect.getsource(qgh.cmd_tick)
        self.assertIn(
            "auto_queue_training(",
            src,
            "cmd_tick never calls auto_queue_training; training will not "
            "auto-relaunch when it stops.",
        )

    def test_tick_source_contains_auto_eval_scan(self):
        """Sanity check: cmd_tick already calls auto_eval_scan."""
        src = inspect.getsource(qgh.cmd_tick)
        self.assertIn("auto_eval_scan(", src)


if __name__ == "__main__":
    unittest.main()
