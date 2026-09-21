#!/usr/bin/env python3
"""C-9595 (re-mint of C-9589): the leg RUNNER itself must survive a worker reap.

C-9589 fixed the DETACHED SLICE/PROBE (leaf) so a worker reap's kill_pid
(os.killpg on the worker's own session/pgid) cannot cascade-kill an in-flight
slice. But the leg RUNNER process (run_holdout_leg1.py / run_holdout_leg2.py)
-- the parent that MERGES slice scores and WRITES the envelope -- is still
spawned by a worker in the worker's OWN process group (a claude bash tool is
a child of the worker session). When the harness reaper reaps a stalled worker
via kill_pid (killpg on the worker's pgid), the non-setid runner is
cascade-killed BEFORE it writes the envelope, even though its detached slice
completed and wrote its score file.

That is EXACTLY the recurring ASI2 stall signature the card names:
  "the leg produced scores but stalled before writing the envelope."
  (slice score file present, envelope absent, runner dead)

This test drives the REAL kill_pid reap against a runner spawned in the
worker's pgid (the bug) proving it dies pre-envelope, and against a runner
that calls the script's detach_from_caller_setsid() helper (the fix)
proving it survives and writes its envelope.
"""

import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

RUNNER_SLICE = (
    "import time, sys\n" "open(sys.argv[1], 'w').write('slice-scores')\n" "time.sleep(1.5)\n"
)
RUNNER_BODY = (
    "import subprocess, sys, time, os\n"
    "p = subprocess.Popen(['python3', sys.argv[1], sys.argv[2]], start_new_session=True)\n"
    "p.wait()\n"
    "time.sleep(0.8)\n"
    "open(sys.argv[3], 'w').write('envelope')\n"
)


def _write_runner_script(detach):
    if detach:
        _sys_inject = f"import os,sys; sys.path.insert(0, {str(ROOT)!r}); "
        detach_src = (
            _sys_inject
            + "from scripts.run_holdout_leg1 import detach_from_caller_setsid; "
            + "detach_from_caller_setsid()\n"
        )
    else:
        detach_src = "# no detach (the bug)\n"
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, dir="/tmp") as f:
        f.write(detach_src)
        f.write(RUNNER_BODY)
        runner = f.name
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, dir="/tmp") as f:
        f.write(RUNNER_SLICE)
        slice_helper = f.name
    score_file = tempfile.mktemp(prefix="c9595-score-", suffix=".txt")
    env_file = tempfile.mktemp(prefix="c9595-env-", suffix=".txt")
    return runner, slice_helper, score_file, env_file


def _spawn_worker_with_runner(detach):
    runner, slice_helper, score_file, env_file = _write_runner_script(detach)
    runner_pid_file = Path(f"/tmp/c9595_runnerpid_{os.getpid()}")
    runner_repr = repr(runner)
    slice_repr = repr(slice_helper)
    score_repr = repr(score_file)
    env_repr = repr(env_file)
    pidf_repr = repr(str(runner_pid_file))
    worker_code = (
        "import subprocess, sys, time\n"
        f"p = subprocess.Popen(['python3', {runner_repr}, {slice_repr}, {score_repr}, {env_repr}], start_new_session=False)\n"
        f"with open({pidf_repr}, 'w') as f: f.write(str(p.pid))\n"
        "time.sleep(2)\n"
    )
    worker = subprocess.Popen(
        ["python3", "-c", worker_code],
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(100):
        if runner_pid_file.exists():
            break
        time.sleep(0.05)
    runner_pid = int(runner_pid_file.read_text().strip())
    worker_pgid = os.getpgid(worker.pid)
    return worker, runner_pid, worker_pgid, score_file, env_file, runner_pid_file


class C9595RunnerSurvivesReapTest(unittest.TestCase):
    def test_nondetached_runner_killed_before_envelope(self):
        worker, runner_pid, worker_pgid, score_file, env_file, pid_file = _spawn_worker_with_runner(
            detach=False
        )
        try:
            self.assertEqual(
                os.getpgid(runner_pid),
                worker_pgid,
                "non-setid runner shares the worker's pgid (the bug)",
            )
            import harness.harness_lib as H

            H.kill_pid(worker.pid)
            worker.wait(timeout=10)
            time.sleep(0.8)
            self.assertFalse(_pid_alive(runner_pid), "runner killed by worker reap killpg")
            self.assertFalse(
                Path(env_file).exists(),
                "envelope never written -> recurring scored-but-no-envelope stall",
            )
        finally:
            _cleanup_r(worker, runner_pid, pid_file)

    def test_setid_runner_survives_and_writes_envelope(self):
        worker, runner_pid, worker_pgid, score_file, env_file, pid_file = _spawn_worker_with_runner(
            detach=True
        )
        try:
            self.assertTrue(
                _wait_session_leader(runner_pid),
                "setid runner must become its own session leader (pgid==pid)",
            )
            self.assertEqual(
                os.getpgid(runner_pid),
                runner_pid,
                "setid runner is its own session leader (pgid==pid)",
            )
            self.assertNotEqual(
                os.getpgid(runner_pid),
                worker_pgid,
                "setid runner must NOT share the worker's pgid",
            )
            import harness.harness_lib as H

            H.kill_pid(worker.pid)
            worker.wait(timeout=10)
            self.assertFalse(_pid_alive(worker.pid), "worker must be reaped")
            self.assertTrue(_pid_alive(runner_pid), "setid runner survives the reap killpg")
            ok = _wait_for(env_file, 8.0)
            self.assertTrue(ok, "surviving runner must write its envelope")
            self.assertTrue(Path(score_file).exists(), "slice score file present too")
        finally:
            _cleanup_r(worker, runner_pid, pid_file)


def _wait_session_leader(pid, timeout=5.0):
    """Wait until pid becomes its own session/process-group leader (pgid==pid).

    The worker writes the runner pid file immediately after Popen, but a setid
    runner only calls os.setsid() once its interpreter boots -- so the test must
    wait for the detach to actually land before asserting protection.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            if os.getpgid(pid) == pid:
                return True
        except (ProcessLookupError, PermissionError):
            return False
        time.sleep(0.05)
    return False


def _pid_alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _wait_for(path, timeout=8.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if Path(path).exists():
            try:
                return Path(path).read_text().strip() == "envelope"
            except OSError:
                pass
        time.sleep(0.1)
    return False


def _cleanup_r(worker, runner_pid, pid_file):
    for p in (worker.pid, runner_pid):
        try:
            os.kill(p, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
    try:
        pid_file.unlink()
    except OSError:
        pass


if __name__ == "__main__":
    unittest.main()
