#!/usr/bin/env python3
"""C-10435 RED: reconciler relaunch MUST NOT be silently swallowed by the
keeper's per-env 300s cooldown lock when the reconciler has already gated a
genuinely-dead box.

INCIDENT (2026-10-15, measured): box_exec_dead fired 3x in one window on ASI3
(03:25, 03:32, 03:43) and ASI1 (03:32:46). huanxin_all_keepalive.log shows the
recurrence mechanism: tick box_exec_autofix -> daemon_reconciler --box ASI3 ->
relaunch_daemon -> keeper script hits `restart cooldown (lock Ns) -> skipping`
and exits 0 (looks like success, does nothing).
FREQUENCY: 262 box_exec_dead total; 34 ten-min windows saw 2+; max 3 per window.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock  # noqa: F401 — makes unittest.mock attribute resolve

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
sys.path.insert(0, HARNESS_DIR)
sys.path.insert(0, os.path.join(HARNESS_DIR, "scripts"))

import daemon_reconciler as dr  # noqa: E402
from daemon_reconciler import relaunch_daemon  # noqa: E402


def _fresh_envkeep(root):
    d = root / "envkeep"
    d.mkdir(parents=True, exist_ok=True)
    return d


class TestRelaunchBypassesCooldown(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self._old_state = dr.STATE_DIR
        dr.STATE_DIR = self.root / "reconciler"
        self._old_keep = None

    def tearDown(self):
        dr.STATE_DIR = self._old_state
        if self._old_keep is not None:
            dr.ENVKEEP_DIR = self._old_keep
        self._tmp.cleanup()

    def _tracking_keeper(self, name):
        script = self.root / name
        script.write_text(
            '#!/bin/bash\necho "keeper-ran box=${HUANXIN_RELAUNCH_BOX:-unknown}"\nexit 0\n'
        )
        script.chmod(0o755)
        self._old_keep = dr.relaunch_daemon.__globals__.get("KEEPER_SCRIPT")
        dr.relaunch_daemon.__globals__["KEEPER_SCRIPT"] = str(script)
        return script

    def test_stale_cooldown_lock_is_cleared_before_keeper(self):
        envkeep = _fresh_envkeep(self.root)
        dr.ENVKEEP_DIR = envkeep
        box = "ASI3"
        lock = envkeep / f"{box}.lock"
        lock.write_text("1")
        tracker = self._tracking_keeper("keeper.sh")
        with unittest.mock.patch("subprocess.run") as mock_run:
            proc = subprocess.CompletedProcess(["bash", str(tracker)], 0, stdout="")
            mock_run.return_value = proc
            res = relaunch_daemon(box)
        self.assertTrue(mock_run.call_count >= 1, "keeper must be invoked")
        self.assertFalse(lock.exists(), "stale cooldown lock must be cleared before keeper")
        self.assertEqual(res.get("action"), "relaunch_daemon")
        self.assertEqual(res.get("exit"), 0)

    def test_keeper_script_is_real_and_absolute(self):
        script = dr.relaunch_daemon.__globals__["KEEPER_SCRIPT"]
        self.assertTrue(str(script).endswith("huanxin_all_keepalive.sh"))

    def test_no_cooldown_lock_relaunch_still_runs(self):
        envkeep = _fresh_envkeep(self.root)
        dr.ENVKEEP_DIR = envkeep
        box = "ASI1"
        tracker = self._tracking_keeper("keeper2.sh")
        with unittest.mock.patch("subprocess.run") as mock_run:
            proc = subprocess.CompletedProcess(["bash", str(tracker)], 0, stdout="")
            mock_run.return_value = proc
            res = relaunch_daemon(box)
        self.assertTrue(mock_run.call_count >= 1)
        self.assertFalse((envkeep / f"{box}.lock").exists())
        self.assertEqual(res.get("exit"), 0)


if __name__ == "__main__":
    unittest.main()
