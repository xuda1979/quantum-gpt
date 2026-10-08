#!/usr/bin/env python3
"""C-9589: ASI2 eval legs must SURVIVE a worker reap so a real leg can actually
dispatch and complete (emit its envelope).

Root cause (carried from C-9582 and verified here at the process-group kill
path): the worker runs its own session (start_new_session=True => pgid==pid),
and harness_lib.kill_pid does os.killpg(worker_pgid) when reaping a stalled or
overrun worker. Any child the worker spawned WITHOUT start_new_session lives
in the worker's process group, so killpg cascade-kills the in-flight ~70min leg
before it writes its envelope -> every eval-leg card died stalled-killed with no
verdict.

An eval-leg slice/probe is only protected if it is spawned DETACHED
(start_new_session=True). This test drives the real kill_pid reap against a
real detached child and a real non-detached child and proves only the detached
leg survives + writes its envelope."""

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
import harness.harness_lib as H  # noqa: E402

LEG_CHILD = "import time, sys\ntime.sleep(2)\nopen(sys.argv[1], 'w').write('envelope')\n"


def _spawn_worker_with_leg(detached_leg):
    """Spawn a fake worker (its own session, pgid==pid) that spawns a leg child
    either detached (fix) or non-detached (legacy). Returns (worker, leg_pid,
    worker_pgid, envelope, legpid_file)."""
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, dir="/tmp") as f:
        f.write(LEG_CHILD)
        leg_helper = f.name
    envelope = tempfile.mktemp(prefix="c9589-env-", suffix=".txt")
    kw = "dict(start_new_session=True)" if detached_leg else "dict()"
    worker_code = (
        "import subprocess, sys, time\n"
        "p = subprocess.Popen(['python3', "
        + repr(leg_helper)
        + ", "
        + repr(envelope)
        + "], **"
        + kw
        + ")\n"
        "with open('/tmp/c9589_legpid_" + str(os.getpid()) + "', 'w') as f: f.write(str(p.pid))\n"
        "time.sleep(2)\n"
    )
    worker = subprocess.Popen(
        ["python3", "-c", worker_code],
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    legpid_file = Path(f"/tmp/c9589_legpid_{os.getpid()}")
    for _ in range(50):
        if legpid_file.exists():
            break
        time.sleep(0.05)
    leg_pid = int(legpid_file.read_text().strip())
    worker_pgid = os.getpgid(worker.pid)
    return worker, leg_pid, worker_pgid, envelope, legpid_file


class C9589LegSurvivesReapTest(unittest.TestCase):
    def test_detached_leg_survives_worker_killpg_reap(self):
        """GREEN path: a leg spawned start_new_session=True is in its OWN
        process group, so the reaper's kill_pid (killpg on the worker group)
        cannot kill it; it lives and writes its envelope."""
        worker, leg_pid, worker_pgid, envelope, legpid_file = _spawn_worker_with_leg(
            detached_leg=True
        )
        try:
            self.assertEqual(
                os.getpgid(leg_pid),
                leg_pid,
                "detached leg must be its own process-group leader (pgid==pid)",
            )
            self.assertNotEqual(
                os.getpgid(leg_pid),
                worker_pgid,
                "detached leg must NOT share the worker's process group",
            )
            H.kill_pid(worker.pid)
            worker.wait(timeout=10)
            self.assertFalse(_pid_alive(worker.pid), "worker must be reaped")
            self.assertTrue(_pid_alive(leg_pid), "detached leg must survive the worker reap killpg")
            ok = _wait_for_envelope(envelope)
            self.assertTrue(ok, "surviving detached leg must write its envelope")
        finally:
            _cleanup(worker, leg_pid, legpid_file)

    def test_nondetached_leg_killed_by_worker_killpg_reap(self):
        """RED path (the legacy bug): a leg spawned WITHOUT start_new_session
        shares the worker's process group and is cascade-killed by the reaper's
        killpg -> no envelope. This documents the dying condition C-9589 fixes."""
        worker, leg_pid, worker_pgid, envelope, legpid_file = _spawn_worker_with_leg(
            detached_leg=False
        )
        try:
            self.assertEqual(
                os.getpgid(leg_pid),
                worker_pgid,
                "non-detached leg shares the worker's process group (the bug)",
            )
            H.kill_pid(worker.pid)
            worker.wait(timeout=10)
            self.assertFalse(_pid_alive(worker.pid), "worker must be reaped")
            self.assertFalse(
                _pid_alive(leg_pid),
                "non-detached leg is cascade-killed by worker reap killpg (root cause)",
            )
        finally:
            _cleanup(worker, leg_pid, legpid_file)


def _pid_alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _wait_for_envelope(path, timeout=10.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if Path(path).exists():
            try:
                return Path(path).read_text().strip() == "envelope"
            except OSError:
                pass
        time.sleep(0.1)
    return False


def _cleanup(worker, leg_pid, legpid_file):
    for p in (worker.pid, leg_pid):
        try:
            os.kill(p, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
    try:
        legpid_file.unlink()
    except OSError:
        pass


if __name__ == "__main__":
    unittest.main()
