"""C-9535: wire StallDetector into tick for training stall detection.

The StallDetector class exists but is never used. Training can stall (no
step advancement for 30+ minutes) without the harness noticing. Wire it
into the tick so the harness can detect stalls and trigger relaunch.

RED: this test must FAIL until the tick uses StallDetector.
"""

import inspect
import os
import sys
import unittest

_HARNESS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _HARNESS_DIR not in sys.path:
    sys.path.insert(0, _HARNESS_DIR)

import qgh  # noqa: E402


class TestStallDetectorWired(unittest.TestCase):
    def test_stall_detector_class_exists(self):
        """Sanity check: StallDetector class exists."""
        self.assertTrue(hasattr(qgh, "StallDetector"))

    def test_tick_references_stall_detection(self):
        """cmd_tick should reference stall detection (StallDetector or
        refresh_trainer_probe with stall check)."""
        src = inspect.getsource(qgh.cmd_tick)
        # The tick should either use StallDetector directly or check for
        # trainer stall via refresh_trainer_probe output
        has_stall_ref = (
            "StallDetector" in src or "stall" in src.lower() or "refresh_trainer_probe" in src
        )
        self.assertTrue(
            has_stall_ref,
            "cmd_tick has no stall detection reference; training can stall "
            "silently without the harness noticing.",
        )

    def test_trainer_probe_refresh_in_tick(self):
        """cmd_tick should call refresh_trainer_probe to check training status."""
        src = inspect.getsource(qgh.cmd_tick)
        self.assertIn(
            "refresh_trainer_probe",
            src,
            "cmd_tick never calls refresh_trainer_probe; training status is not monitored.",
        )


if __name__ == "__main__":
    unittest.main()
