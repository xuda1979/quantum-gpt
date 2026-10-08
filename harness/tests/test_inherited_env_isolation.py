"""C-9001 RED: an INHERITED QGH_STATE_DIR pointing at the live state dir
must not defeat the pytest isolation seam.

Incident 2026-09-17 (second hole, distinct from the conftest docstring
first incident): qgh dispatches workers with env QGH_STATE_DIR=<live>
(qgh.py env.setdefault("QGH_STATE_DIR", STATE)), and worker gate steps
run pytest. conftest.py trusted any inherited value (if not
os.environ.get -- set means trusted), so a worker-side pytest run
re-bound qgh.STATE to the LIVE dir and test writes polluted the real
queue: fixture card C-9001 (title "t", why "w", acceptance ["a"],
fixture deadline "2026-09-16T10:00:00Z") landed in live QUEUE.json and
live EVENTS.jsonl gained the suite reaped/gate_bounced/auto_plan events.

The existing canary (test_live_state_isolation.py) only pins the
unset-env path; under the hole it fails AFTER earlier files already
wrote live. This test pins the fix end-to-end: rerun the canary in a
subprocess whose env carries QGH_STATE_DIR=<live> -- it must PASS
(conftest isolates), not fail. Read-only: the canary never writes, so
the RED phase cannot pollute live.
"""

import os
import subprocess
import sys
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TEST_DIR))
LIVE_STATE = os.path.join(REPO, "harness", "state")


class TestInheritedLiveEnvIsolation(unittest.TestCase):
    def test_canary_passes_even_when_env_inherits_live_state_dir(self):
        env = dict(os.environ)
        env["QGH_STATE_DIR"] = LIVE_STATE  # exactly what worker shells carry
        r = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                os.path.join(TEST_DIR, "test_live_state_isolation.py"),
            ],
            cwd=REPO,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )
        msg = (
            "canary failed under inherited QGH_STATE_DIR=<live>: conftest "
            "trusted the inherited value and bound qgh.STATE to live. "
            "stdout tail: " + r.stdout[-1500:] + " stderr tail: " + r.stderr[-800:]
        )
        self.assertEqual(r.returncode, 0, msg)


if __name__ == "__main__":
    unittest.main()
