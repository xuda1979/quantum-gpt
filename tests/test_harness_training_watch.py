"""TDD for training_watch: full-training-process monitoring alarms.

The harness must monitor the FULL training process: metrics growth,
reward signal health, pass-rate progress, log freshness, step advancement.
fail-closed: missing metrics => TRAINING-UNMEASURABLE alarm, not silence.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness.harness_lib import training_watch_alarms


def _row(step, mean_reward, pass_rate, entropy=None, seq_kl=None):
    d = {"step": step, "mean_reward": mean_reward, "pass_rate": pass_rate}
    if entropy is not None:
        d["entropy_mean"] = entropy
    if seq_kl is not None:
        d["seq_kl_after"] = seq_kl
    return d


class TestTrainingWatchAlarms(unittest.TestCase):
    def test_no_metrics_is_unmeasurable_not_silent(self):
        alarms = training_watch_alarms([], now_s=1000, last_mtime=900)
        self.assertTrue(any(a["kind"] == "TRAINING-UNMEASURABLE" for a in alarms))

    def test_stale_log_raises_LOG_STALE(self):
        rows = [_row(28, 0.2, 0.0)]
        alarms = training_watch_alarms(rows, now_s=1_000_000, last_mtime=900_000)
        self.assertTrue(any(a["kind"] == "LOG-STALE" for a in alarms))

    def test_fresh_log_no_stale_alarm(self):
        rows = [_row(28, 0.2, 0.0)]
        alarms = training_watch_alarms(rows, now_s=1_000_030, last_mtime=1_000_000)
        self.assertFalse(any(a["kind"] == "LOG-STALE" for a in alarms))

    def test_dead_signal_three_zero_reward_steps(self):
        rows = [_row(i, 0.0, 0.0) for i in (25, 26, 27)]
        alarms = training_watch_alarms(rows, now_s=1000, last_mtime=990)
        self.assertTrue(any(a["kind"] == "DEAD-SIGNAL" for a in alarms))

    def test_nonzero_reward_no_dead_signal(self):
        rows = [_row(i, 0.19, 0.0) for i in (25, 26, 27)]
        alarms = training_watch_alarms(rows, now_s=1000, last_mtime=990)
        self.assertFalse(any(a["kind"] == "DEAD-SIGNAL" for a in alarms))

    def test_noop_flat_reward_two_steps(self):
        rows = [_row(26, 0.193, 0.0), _row(27, 0.193, 0.0)]
        alarms = training_watch_alarms(rows, now_s=1000, last_mtime=990)
        self.assertTrue(any(a["kind"] == "NO-OP" for a in alarms))

    def test_pass_rate_stuck_zero_many_steps(self):
        rows = [_row(i, 0.1 + i * 0.01, 0.0) for i in range(20, 31)]
        alarms = training_watch_alarms(rows, now_s=1000, last_mtime=990)
        self.assertTrue(any(a["kind"] == "PASS-RATE-ZERO" for a in alarms))

    def test_entropy_collapse_alarm(self):
        rows = [_row(27, 0.2, 0.0, entropy=0.05)]
        alarms = training_watch_alarms(rows, now_s=1000, last_mtime=990)
        self.assertTrue(any(a["kind"] == "ENTROPY-LOW" for a in alarms))

    def test_seq_kl_blowup_alarm(self):
        rows = [_row(27, 0.2, 0.1, seq_kl=0.40)]
        alarms = training_watch_alarms(rows, now_s=1000, last_mtime=990)
        self.assertTrue(any(a["kind"] == "SEQ-KL-HIGH" for a in alarms))

    def test_healthy_training_no_alarms(self):
        rows = [
            _row(26, 0.20, 0.0, entropy=0.20, seq_kl=0.05),
            _row(27, 0.25, 0.25, entropy=0.22, seq_kl=0.04),
        ]
        alarms = training_watch_alarms(rows, now_s=1_000_030, last_mtime=1_000_000)
        self.assertEqual(alarms, [])


if __name__ == "__main__":
    unittest.main()


from harness.harness_lib import eval_truth_summary


class TestEvalTruthSummary(unittest.TestCase):
    def test_counts_passes_not_candidates(self):
        rows = [{"step": 31, "passed": False}, {"step": 31, "passed": False},
                {"step": 31, "passed": True}]
        t = eval_truth_summary(rows)
        self.assertEqual(t["n_passes"], 1)
        self.assertEqual(t["n_candidates"], 3)

    def test_all_fail_is_zero_not_candidates(self):
        rows = [{"step": 32, "passed": False} for _ in range(4)]
        t = eval_truth_summary(rows)
        self.assertEqual(t["n_passes"], 0)  # NOT 4 — the C-9590 lesson
        self.assertEqual(t["n_candidates"], 4)

    def test_empty_is_none(self):
        self.assertIsNone(eval_truth_summary([]))


from harness.harness_lib import best_checkpoint_update, best_checkpoint_warm_start


class TestBestCheckpointRegistry(unittest.TestCase):
    def test_first_verdict_becomes_best(self):
        best = best_checkpoint_update(None, {"checkpoint": "ck31", "n_passes": 4,
                                             "n_tasks": 18, "beats_base": True})
        self.assertEqual(best["checkpoint"], "ck31")
        self.assertEqual(best["n_passes"], 4)

    def test_higher_pass_count_promotes(self):
        cur = {"checkpoint": "ck31", "n_passes": 4, "n_tasks": 18}
        new = best_checkpoint_update(cur, {"checkpoint": "ck45", "n_passes": 6,
                                           "n_tasks": 18, "beats_base": True})
        self.assertEqual(new["checkpoint"], "ck45")

    def test_lower_or_equal_does_not_promote(self):
        cur = {"checkpoint": "ck45", "n_passes": 6, "n_tasks": 18}
        for n in (6, 3):
            new = best_checkpoint_update(cur, {"checkpoint": "ckX", "n_passes": n,
                                               "n_tasks": 18})
            self.assertEqual(new["checkpoint"], "ck45")

    def test_fail_closed_requires_full_tasks(self):
        with self.assertRaises(ValueError):
            best_checkpoint_update(None, {"checkpoint": "ck", "n_passes": 18,
                                          "n_tasks": None})

    def test_warm_start_prefers_registry_over_stale(self):
        best = {"checkpoint": "/outputs/run/step_000045_adapter",
                "n_passes": 6, "n_tasks": 18}
        picked = best_checkpoint_warm_start(best, "/outputs/old/step_000027_adapter")
        self.assertEqual(picked, "/outputs/run/step_000045_adapter")

    def test_warm_start_falls_back_when_no_best(self):
        picked = best_checkpoint_warm_start(None, "/outputs/old/step_000027_adapter")
        self.assertEqual(picked, "/outputs/old/step_000027_adapter")
