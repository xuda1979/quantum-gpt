"""C-9106: Base-leg mid-leg slice-progress watch.

Re-files bounce-dead C-9057. The eval leg (C-9030 chain) fails closed only
at collect time, so a mid-leg death silently burns a scarce ASI2 window.
This pins the watch: a durable per-slice status artifact built from the
eval_results.jsonl step ladder (stage "step_begin" then "backward_done"),
mtime-liveness checked, and a NAMED alarm artifact on mid-leg death/stall
that names the run dir. The watch must NEVER re-launch (C-9032 single-launch
guard): there is no launch path in the module.
"""

import json
import os
import subprocess  # noqa: F401  (referenced by relaunch-guard patches)
import sys
import tempfile
import unittest
from unittest import mock

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
sys.path.insert(0, HARNESS_DIR)
import slice_watch  # noqa: E402

NOW = 1758200000.0
STALE_S = 900


def _write_log(run_dir, events):
    os.makedirs(run_dir, exist_ok=True)
    path = os.path.join(run_dir, "eval_results.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for ev in events:
            f.write(json.dumps(ev) + "\n")
    return path


def _ladder(open_step=1):
    """Slices 0 fully done; slice `open_step` begun, not finished."""
    return [
        {"ts": "2026-09-18T08:00:00Z", "stage": "step_begin", "step": 0},
        {"ts": "2026-09-18T08:01:00Z", "stage": "backward_done", "step": 0},
        {"ts": "2026-09-18T08:02:00Z", "stage": "step_begin", "step": open_step},
    ]


class TestC9106SliceWatch(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="c9106-")
        self.run_dir = os.path.join(self.tmp, "run_eval_base")
        self.state_dir = os.path.join(self.tmp, "state", "slice_watch")

    def _watch(self, run_dir=None):
        return slice_watch.watch(
            run_dir or self.run_dir,
            self.state_dir,
            stale_s=STALE_S,
            now=NOW,
        )

    def test_fresh_open_slice_status_artifact_no_alarm(self):
        log = _write_log(self.run_dir, _ladder())
        os.utime(log, (NOW - 60, NOW - 60))  # fresh mtime

        summary = self._watch()

        self.assertEqual(summary["verdict"], "LIVE")
        status_path = summary["status_artifact"]
        self.assertTrue(os.path.exists(status_path), "durable status artifact must exist")
        with open(status_path, encoding="utf-8") as f:
            status = json.load(f)
        self.assertEqual(status["run_dir"], self.run_dir)
        self.assertEqual(status["liveness"], "LIVE")
        self.assertEqual(
            status["slices"].get("1", {}).get("backward_done", None),
            False,
            "open slice must be recorded as begun, not done",
        )
        self.assertEqual(status["slices"].get("0", {}).get("backward_done"), True)
        alarms = [p for p in os.listdir(self.state_dir) if p.startswith("ALARM_")]
        self.assertEqual(alarms, [], "fresh leg must not raise an alarm")

    def test_stale_open_slice_raises_named_alarm(self):
        log = _write_log(self.run_dir, _ladder())
        os.utime(log, (NOW - 3600, NOW - 3600))  # silent for 1h > stale_s

        summary = self._watch()

        self.assertEqual(summary["verdict"], "ALARM")
        alarms = [p for p in os.listdir(self.state_dir) if p.startswith("ALARM_")]
        self.assertEqual(len(alarms), 1, "exactly one named alarm artifact")
        with open(os.path.join(self.state_dir, alarms[0]), encoding="utf-8") as f:
            alarm = json.load(f)
        self.assertEqual(alarm["run_dir"], self.run_dir, "alarm must name the run dir")
        self.assertIn("stall", alarm["kind"])

    def test_missing_log_fails_closed_with_alarm(self):
        os.makedirs(self.run_dir, exist_ok=True)
        summary = self._watch()
        self.assertEqual(summary["verdict"], "ALARM", "missing log must fail closed")
        alarms = [p for p in os.listdir(self.state_dir) if p.startswith("ALARM_")]
        self.assertEqual(len(alarms), 1)
        with open(os.path.join(self.state_dir, alarms[0]), encoding="utf-8") as f:
            alarm = json.load(f)
        self.assertIn("unknown", alarm["kind"])
        self.assertEqual(alarm["run_dir"], self.run_dir)

    def test_done_leg_no_alarm(self):
        events = [
            {"ts": "2026-09-18T08:00:00Z", "stage": "step_begin", "step": 0},
            {"ts": "2026-09-18T08:01:00Z", "stage": "backward_done", "step": 0},
        ]
        log = _write_log(self.run_dir, events)
        os.utime(log, (NOW - 3600, NOW - 3600))  # old mtime, but no open slice

        summary = self._watch()
        self.assertEqual(summary["verdict"], "LIVE", "fully-paired ladder is not a stall")
        alarms = [p for p in os.listdir(self.state_dir) if p.startswith("ALARM_")]
        self.assertEqual(alarms, [])

    def test_never_relaunches(self):
        # C-9032 single-launch guard: the watch contains no launch path.
        log = _write_log(self.run_dir, _ladder())
        os.utime(log, (NOW - 3600, NOW - 3600))
        boom = AssertionError("watch must never spawn/launch anything")
        with (
            mock.patch.object(subprocess, "Popen", side_effect=boom),
            mock.patch.object(subprocess, "run", side_effect=boom),
            mock.patch.object(os, "system", side_effect=boom),
            mock.patch.object(os, "execv", side_effect=boom),
        ):
            summary = self._watch()
        self.assertEqual(summary["verdict"], "ALARM", "alarm path must work launch-free")

    def test_status_artifact_is_durable_atomic(self):
        # Durable = tmp-file + os.replace, never a torn partial write.
        log = _write_log(self.run_dir, _ladder())
        os.utime(log, (NOW - 60, NOW - 60))
        summary = self._watch()
        self.assertFalse(
            [p for p in os.listdir(self.state_dir) if p.endswith(".tmp")],
            "no temp files may survive an atomic write",
        )
        self.assertTrue(os.path.exists(summary["status_artifact"]))


if __name__ == "__main__":
    unittest.main()
