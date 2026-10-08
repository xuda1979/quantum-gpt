"""TDD test: verify eval markers in verdict envelopes."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import qgh


class EvalMarkerVerificationTest(unittest.TestCase):
    def test_goal_done_rejects_missing_adapter_applied(self):
        """goal_done must reject a verdict with adapter_applied_marker=false."""
        goal = {"status": "OPEN", "target_pass": "18/18", "model": "Qwen3.8-27B"}
        verdict = {
            "_file": "test_verdict.json",
            "pass_adapter": "18/18",
            "beats_base": True,
            "scorer_version": "v2",
            "adapter_applied_marker": False,
            "adapter_probe_differs_marker": True,
            "model": "Qwen3.8-27B",
        }
        done, vfile = qgh.goal_done(goal, [verdict])
        self.assertFalse(done, "verdict with adapter_applied_marker=false must not retire goal")

    def test_goal_done_rejects_missing_probe_differs(self):
        """goal_done must reject a verdict without adapter_probe_differs_marker."""
        goal = {"status": "OPEN", "target_pass": "18/18", "model": "Qwen3.8-27B"}
        verdict = {
            "_file": "test_verdict2.json",
            "pass_adapter": "18/18",
            "beats_base": True,
            "scorer_version": "v2",
            "adapter_applied_marker": True,
            "model": "Qwen3.8-27B",
        }
        done, vfile = qgh.goal_done(goal, [verdict])
        self.assertFalse(done, "verdict without adapter_probe_differs_marker must not retire goal")

    def test_goal_done_rejects_single_leg(self):
        """goal_done must reject a verdict with only one leg (needs two)."""
        goal = {"status": "OPEN", "target_pass": "18/18", "model": "Qwen3.8-27B"}
        verdict = {
            "_file": "test_verdict3.json",
            "pass_adapter": "18/18",
            "beats_base": True,
            "scorer_version": "v2",
            "adapter_applied_marker": True,
            "adapter_probe_differs_marker": True,
            "model": "Qwen3.8-27B",
            "leg1": {"adapter_probe_differs_marker": True},
        }
        done, vfile = qgh.goal_done(goal, [verdict])
        self.assertFalse(done, "verdict with only leg1 must not retire goal")


if __name__ == "__main__":
    unittest.main()
