#!/usr/bin/env python3
"""C-9630: cmd_heal must ensure the self-resume guardian is STANDING.

Measured gap 2026-09-22 12:04Z: the guardian resumed training once and was
gone; the 507015 NPU fault killed the trainer 11 min later and nothing
re-resumed for 40+ min. The heal daemon (launchd, every 30 min) is the
durable supervisor for this: _ensure_standing_guardian() must restart the
guardian detached when no guardian process is alive, do nothing when one is,
and never raise (a failed restart logs an event and lets the next heal
retry).
"""

import os
import subprocess
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import harness.qgh as q  # noqa: E402


class TestEnsureStandingGuardian(unittest.TestCase):
    def _guardian_pids(self):
        p = subprocess.run(
            ["pgrep", "-f", "self_resume_guardian.py"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return [ln for ln in p.stdout.split() if ln.strip()]

    def test_no_guardian_means_spawn(self):
        """pgrep finds nothing -> a detached guardian is spawned."""
        spawned = []
        fake_probe = mock.Mock(returncode=1, stdout="")
        with (
            mock.patch.object(subprocess, "run", return_value=fake_probe),
            mock.patch.object(
                subprocess, "Popen", side_effect=lambda *a, **k: spawned.append(k) or mock.Mock()
            ),
            mock.patch.object(q, "event") as ev,
        ):
            q._ensure_standing_guardian()
        self.assertEqual(len(spawned), 1, "exactly one guardian spawn")
        kwargs = spawned[0]
        self.assertTrue(kwargs.get("start_new_session"), "guardian must detach")
        # a clean spawn logs a restart event (telemetry), never a failure event
        if ev.call_count:
            self.assertNotEqual(
                ev.call_args[0][1],
                "guardian_restart_failed",
                "a clean spawn must not be logged as a failure",
            )

    def test_live_guardian_means_no_spawn(self):
        """pgrep finds a pid -> nothing is spawned (no double guardians)."""
        fake_probe = mock.Mock(returncode=0, stdout="4242\n")
        with (
            mock.patch.object(subprocess, "run", return_value=fake_probe),
            mock.patch.object(subprocess, "Popen") as pop,
        ):
            q._ensure_standing_guardian()
        pop.assert_not_called()

    def test_spawn_failure_never_raises(self):
        """Popen raising -> the failure is logged as an event, never raised."""
        fake_probe = mock.Mock(returncode=1, stdout="")
        with (
            mock.patch.object(subprocess, "run", return_value=fake_probe),
            mock.patch.object(subprocess, "Popen", side_effect=OSError("no fds")),
            mock.patch.object(q, "event") as ev,
        ):
            try:
                q._ensure_standing_guardian()
            except Exception as exc:  # pragma: no cover
                self.fail(f"guardian restart must never raise, raised {exc}")
        ev.assert_called_once()
        self.assertEqual(ev.call_args[0][1], "guardian_restart_failed")

    def test_heal_calls_ensure(self):
        """cmd_heal wires the guardian check into the 30-min heal cadence."""
        src = open(q.__file__, encoding="utf-8").read()
        self.assertIn("_ensure_standing_guardian()", src.split("def cmd_heal")[1][:2500])


if __name__ == "__main__":
    unittest.main()
