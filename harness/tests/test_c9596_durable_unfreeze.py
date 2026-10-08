"""C-9596 durable unfreeze RED test."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import harness_lib as H


class T(unittest.TestCase):
    def test_advancing_midstep_not_stalled(self):
        h = H.DurableTrainerHealth()
        h.observe(28, "2026-09-20T17:37:00Z")
        self.assertTrue(h.observe(29, "2026-09-20T18:11:00Z"))
        self.assertFalse(h.is_stalled(current_time="2026-09-20T18:44:20Z"))

    def test_frozen_stalled(self):
        h = H.DurableTrainerHealth()
        h.observe(28, "2026-09-20T17:37:00Z")
        self.assertTrue(h.is_stalled(current_time="2026-09-20T20:37:00Z"))

    def test_cadence_aware(self):
        h = H.DurableTrainerHealth(cadence_s=2040)
        h.observe(28, "2026-09-20T17:37:00Z")
        self.assertFalse(h.is_stalled(current_time="2026-09-20T18:14:24Z"))
        self.assertTrue(h.is_stalled(current_time="2026-09-20T18:45:24Z"))


if __name__ == "__main__":
    unittest.main()


class TestDurableUnfreezeLogStale(unittest.TestCase):
    """Durable unfreeze must guard training_watch LOG-STALE against
    false positives on a healthy advancing ~34min/step trainer."""

    def _row(self, step):
        return {
            "step": step,
            "mean_reward": 1.0,
            "pass_rate": 0.5,
            "entropy_mean": 1.0,
            "seq_kl_after": 0.1,
        }

    def test_advancing_34min_trainer_not_log_stale_at_20min(self):
        rows = [self._row(28), self._row(29)]
        alarms = H.training_watch_alarms(rows, now_s=100000, last_mtime=998800)
        kinds = {a["kind"] for a in alarms}
        self.assertNotIn("LOG-STALE", kinds)

    def test_advancing_34min_trainer_not_log_stale_mid_cadence(self):
        rows = [self._row(28), self._row(29)]
        alarms = H.training_watch_alarms(rows, now_s=100000, last_mtime=100000 - 33 * 60)
        kinds = {a["kind"] for a in alarms}
        self.assertNotIn("LOG-STALE", kinds)

    def test_frozen_trainer_log_stale_after_real_freeze(self):
        rows = [self._row(29)]
        now = 100000
        alarms = H.training_watch_alarms(rows, now_s=now, last_mtime=now - 68 * 60)
        kinds = {a["kind"] for a in alarms}
        self.assertIn("LOG-STALE", kinds)
