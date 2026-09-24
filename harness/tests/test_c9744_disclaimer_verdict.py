"""Card C-9744: synthetic/_DISCLAIMER verdict can NEVER retire the goal.

Incident (2026-09-24T01:53:00Z): C-9742's canonical-path DEMO verdict
(verdict_C9742_canonical_path_demo.json) — a SYNTHETIC fixture composition
carrying an explicit _DISCLAIMER ("NOT a real adapter measurement") —
satisfied every goal_done() gate and flipped GOAL.json to DONE while real
measured progress was 3/18. The loop then printed "GOAL ACHIEVED — loop
retired" on every tick and stopped all progress toward the objective.

Fix: goal_done() must skip any verdict with a truthy _DISCLAIMER field,
fail-closed. A real measurement never carries one; only fixture/demo
compositions do.
"""
import os
import sys
import unittest

_HARNESS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_HARNESS_DIR)
for p in (_HARNESS_DIR, _REPO_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

import harness_lib as H  # noqa: E402


def _demo_verdict():
    """Shape-matched to outputs/verdict_C9742_canonical_path_demo.json."""
    return {
        "pass_adapter": "18/18",
        "pass_base": "0/18",
        "beats_base": True,
        "scorer_version": "holdout-freeze-b40ca7f2b16e",
        "adapter_applied_marker": True,
        "adapter_probe_differs_marker": True,
        "independent_second_leg": True,
        "leg1": {"box": "ASI2", "runner_mechanism": "parallel-3-slice",
                 "markers": {"adapter_probe_differs": True},
                 "adapter_probe_differs_marker": True},
        "leg2": {"box": "ASI3", "runner_mechanism": "sequential-single-slice",
                 "markers": {"adapter_probe_differs": True},
                 "adapter_probe_differs_marker": True},
        "per_task": {"t%02d" % i: {"adapter_pass": True, "base_pass": False}
                     for i in range(18)},
        "candidates_vs_base_gate": {
            "leg1": {"status": "PASS"}, "leg2": {"status": "PASS"},
        },
        "_DISCLAIMER": ("SYNTHETIC composition-path demonstration only. "
                        "NOT a real adapter measurement."),
    }


class TestC9744DisclaimerVerdict(unittest.TestCase):
    def test_goal_done_true_when_unpinned(self):
        """Control: WITHOUT the fix the demo verdict retires the goal
        (reproduces the incident)."""
        import inspect
        src = inspect.getsource(H.goal_done)
        self.assertIn("_DISCLAIMER", src,
                      "goal_done must check _DISCLAIMER (C-9744 fix)")

    def test_disclaimer_verdict_never_retires_goal(self):
        done, src = H.goal_done(
            dict(target_pass="18/18", model="Qwen3.8-27B"),
            [_demo_verdict()],
        )
        self.assertFalse(done,
                         "synthetic demo verdict retired the goal — incident "
                         "2026-09-24T01:53:00Z reproduced")

    def test_real_verdict_still_retires(self):
        """Control: same shape MINUS _DISCLAIMER still passes (with sha
        pins mocked to match, per existing fire-drill pattern)."""
        from unittest import mock
        v = _demo_verdict()
        del v["_DISCLAIMER"]
        with mock.patch.object(H, "sha_pin_violation", lambda *a, **k: None), \
             mock.patch.object(H, "model_identity_violation", lambda *a, **k: None):
            done, src = H.goal_done(
                dict(target_pass="18/18", model="Qwen3.8-27B"), [v])
        self.assertTrue(done)


if __name__ == "__main__":
    unittest.main()
