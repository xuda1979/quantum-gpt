"""C-9124: auto-detect /exec endpoint failures and report them clearly.

The harness must detect when a daemon's /exec endpoint is broken
(returns rc=None or HTTP 500) and:
1. Report it as an environmental issue (not a card fault)
2. Not increment bounce_count for /exec failures
3. Consider trying alternative boxes when the primary box's /exec is broken

The ASI2 /exec failure (2026-09-19) blocked training for hours because
the harness kept dispatching workers that would fail at the /exec precheck
without diagnosing the root cause or trying alternatives.
"""

import os
import sys
import unittest

_HARNESS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_REPO_ROOT = os.path.dirname(_HARNESS_DIR)
for p in (_HARNESS_DIR, _REPO_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

import harness_lib as H  # noqa: E402


class TestExecFailureDetection(unittest.TestCase):
    """Detect /exec endpoint failures and handle them as environmental."""

    def test_exec_rc_none_is_environmental(self):
        """A /exec response with rc=None is an environmental failure,
        not a card fault — bounce_count must not increment."""
        # Simulate a worker output where /exec returned rc=None
        worker_output = (
            "precheck: /exec returned rc=None stdout=''\n"
            "ModuleNotFoundError: No module named 'qiskit'\n"
        )
        is_exec_failure = H.is_exec_endpoint_failure(worker_output)
        self.assertTrue(is_exec_failure, "rc=None /exec output must be detected as exec failure")

    def test_exec_500_is_environmental(self):
        """HTTP 500 from /exec is an environmental failure."""
        worker_output = "HTTP Error: 500 Internal Server Error from /exec\n"
        is_exec_failure = H.is_exec_endpoint_failure(worker_output)
        self.assertTrue(is_exec_failure)

    def test_normal_output_not_exec_failure(self):
        """Normal worker output with RESULT: DONE is not an exec failure."""
        worker_output = "RESULT: DONE — all tasks completed successfully\n"
        is_exec_failure = H.is_exec_endpoint_failure(worker_output)
        self.assertFalse(is_exec_failure)

    def test_module_not_found_with_exec_failure_is_environmental(self):
        """ModuleNotFoundError combined with /exec rc=None is environmental
        (the module can't be installed because /exec is broken)."""
        worker_output = (
            "/exec rc=None\n"
            "ModuleNotFoundError: No module named 'qiskit'\n"
            "BLOCKED: box /exec not functional\n"
        )
        is_exec_failure = H.is_exec_endpoint_failure(worker_output)
        self.assertTrue(is_exec_failure)


if __name__ == "__main__":
    unittest.main()
