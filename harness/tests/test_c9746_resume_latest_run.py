"""Card C-9746: resume must pick the LATEST-RUN's newest checkpoint, not the
global max-step across runs.

Incident 2026-09-24T03:16Z: ASI3 trainer died (NPU 507015, chip 3). Its run
(sft-27b-q38-v10-resume-20260924T085644Z) had banked its OWN step-73 — which
contains shard-166 weights + 73 further trained steps. But
find_latest_checkpoint() globs sft-27b-q38-v10*/checkpoints/step-*/adapter
and takes the GLOBAL max step-N => it picked shard-asi1 step-166 (already
consumed as the dead run's warm-start) and would DISCARD the 73 banked steps.
"""
import os
import sys
import unittest
from unittest import mock

_HARNESS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_HARNESS_DIR)
sys.path.insert(0, _HARNESS_DIR)
sys.path.insert(0, _REPO_ROOT)

from scripts import resume_training as RT  # noqa: E402


DEAD_RUN = "/root/work/quantum-gpt/outputs/sft-27b-q38-v10-resume-20260924T085644Z/checkpoints/step-73/adapter"
SHARD_166 = "/root/work/quantum-gpt/outputs/sft-27b-q38-v10-shard-asi1-20260923T124524Z/checkpoints/step-166/adapter"
OLDER_RESUME = "/root/work/quantum-gpt/outputs/sft-27b-q38-v10-resume-20260923T031239Z/checkpoints/step-40/adapter"


class TestC9746ResumePicksLatestRun(unittest.TestCase):
    def test_red_global_max_step_is_wrong(self):
        """The OLD selection (global max step) returns shard-166 — proves the
        bug the incident exposed."""
        got = RT.parse_latest_checkpoint([DEAD_RUN, SHARD_166, OLDER_RESUME])
        self.assertEqual(got, SHARD_166,
                         "global-max selection is the C-9746 bug carrier (expected shard-166 to be picked)")

    def test_latest_run_checkpoints_recede_in_priority(self):
        """NEW selector: among runs, prefer the run whose checkpoints are
        NEWEST by mtime; within it, max step. The dead run's step-73 (mtime
        03:10) is newer than shard-166 (mtime 18:05 previous day), so resume
        must pick DEAD_RUN."""
        # New LS_ALL_SH emits "<mtime> <path>" lines (see resume_training.py C-9746)
        fake_stdout = (
            "1790221852 " + DEAD_RUN + "\n"
            "1790191518 " + SHARD_166 + "\n"
            "1790100000 " + OLDER_RESUME + "\n"
        )
        with mock.patch.object(RT, "run_box", return_value={"status": "PASS", "stdout": fake_stdout}):
            got = RT.find_latest_checkpoint()
        self.assertEqual(got, DEAD_RUN)


if __name__ == "__main__":
    unittest.main()
