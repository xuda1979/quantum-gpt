"""C-0036 RED tests: the eval-leg launcher must TAKE the asi2-eval lease.

C-0035 measured ZERO callers of harness/state/locks/asi2-eval.lock in every
eval-launching path: scripts/asi2_loop_eval.sh dispatches 18-task holdout
legs with only per-ts pid checks (/tmp/asi2_loop_precheck_<TS>.pid,
/tmp/reeval_<TS>.pid), so two launchers carrying different checkpoints
double-fire NPU legs at ASI2. The helper (harness_lib.acquire_lock) is
green but unwired -- a landed lock nobody takes serializes nothing.

These tests pin the WIRING (the helper itself is already pinned by
test_eval_box_lock.py):
  - the launcher exposes a real acquisition path that takes the lease via
    harness_lib.acquire_lock and REFUSES while another live holder has it
    (a holder whose lease pid is alive -- this also pins that the lease
    names the long-lived launcher shell, not the short-lived helper
    process, else dead-pid takeover would let the next launcher steal it
    mid-dispatch)
  - the release path removes the lease so the next dispatcher can proceed
  - the main flow actually CALLS acquire before the eval dispatch and
    releases after it (ordering pinned by line numbers, so deleting the
    acquisition turns this RED)
"""

import json
import os
import subprocess
import tempfile
import time
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LAUNCHER = os.path.join(ROOT, "scripts", "asi2_loop_eval.sh")


def _bash(body, lock_path, timeout=60):
    """Run BODY in bash with the launcher sourced via its test seam."""
    script = (
        "set -euo pipefail\n"
        "export SAPO_EVAL_LIB_ONLY=1\n"
        f'source "{LAUNCHER}"\n'
        f'export EVAL_LOCK_FILE="{lock_path}"\n'
        f"{body}\n"
    )
    return subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=timeout)


class TestLauncherTakesEvalBoxLease(unittest.TestCase):
    """Behavior tests: source the launcher via its SAPO_EVAL_LIB_ONLY=1 seam
    (helpers defined, main flow stops before the first box probe) and drive
    the lease functions against a temp lock path."""

    def test_acquire_creates_lease_and_release_removes_it(self):
        with tempfile.TemporaryDirectory(prefix="qgh-c0036-") as d:
            lock = os.path.join(d, "asi2-eval.lock")
            p = _bash(
                "asi2_eval_lock_acquire || { echo ACQUIRE_REFUSED; exit 3; }\n"
                'test -f "$EVAL_LOCK_FILE" || { echo NO_LOCK_FILE; exit 4; }\n'
                'cat "$EVAL_LOCK_FILE"; echo\n'
                'echo "---RELEASE---"\n'
                "asi2_eval_lock_release\n"
                'if [ -e "$EVAL_LOCK_FILE" ]; then echo LOCK_NOT_RELEASED; exit 5; fi\n',
                lock,
            )
            self.assertEqual(p.returncode, 0, f"stderr={p.stderr} stdout={p.stdout}")
            before, _after = p.stdout.split("---RELEASE---")
            tok = json.loads(before.strip())
            self.assertIn("pid", tok, "lease token must carry a holder pid")
            self.assertIn("ts", tok, "lease token must carry a timestamp")

    def test_second_dispatcher_refused_while_lease_live(self):
        """A live holder must make the second dispatcher REFUSE. This fails if
        the lease names a dead helper pid: dead-pid takeover would steal it."""
        with tempfile.TemporaryDirectory(prefix="qgh-c0036-") as d:
            lock = os.path.join(d, "asi2-eval.lock")
            ready = os.path.join(d, "holder_ready")
            holder_body = (
                "asi2_eval_lock_acquire || { echo HOLDER_ACQUIRE_FAILED; exit 9; }\n"
                f'touch "{ready}"\n' + "sleep 6\n" + "asi2_eval_lock_release\n"
            )
            script = (
                "set -euo pipefail\n"
                "export SAPO_EVAL_LIB_ONLY=1\n"
                f'source "{LAUNCHER}"\n' + f'export EVAL_LOCK_FILE="{lock}"\n' + holder_body
            )
            holder = subprocess.Popen(
                ["bash", "-c", script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            try:
                deadline = time.time() + 10
                while not os.path.exists(ready) and time.time() < deadline:
                    if holder.poll() is not None:
                        break
                    time.sleep(0.2)
                self.assertTrue(os.path.exists(ready), "holder never acquired its lease")
                second = _bash(
                    "if asi2_eval_lock_acquire; then "
                    "echo UNEXPECTED_SECOND_ACQUIRE; exit 6; fi\n"
                    'echo "REFUSED_AS_EXPECTED"\n',
                    lock,
                )
                self.assertIn(
                    "REFUSED_AS_EXPECTED",
                    second.stdout,
                    "second dispatcher must be refused while a live holder has the "
                    f"lease (stdout={second.stdout} stderr={second.stderr})",
                )
            finally:
                out, _err = holder.communicate(timeout=30)
            self.assertEqual(holder.returncode, 0, f"holder must release cleanly: {out}")
            third = _bash(
                "asi2_eval_lock_acquire || { echo REACQUIRE_FAILED; exit 7; }\n"
                "asi2_eval_lock_release\n",
                lock,
            )
            self.assertEqual(
                third.returncode,
                0,
                f"after release the lease is free: {third.stderr}",
            )


class TestMainFlowWiring(unittest.TestCase):
    """The lease must be taken in the MAIN FLOW (after the lib-only test
    seam), before the eval dispatch, and released after it."""

    def test_main_flow_orders_lock_around_eval_dispatch(self):
        with open(LAUNCHER, encoding="utf-8") as f:
            lines = f.read().splitlines()
        seam = next(i for i, ln in enumerate(lines) if "SAPO_EVAL_LIB_ONLY" in ln and ":-0" in ln)
        dispatch = next(
            i
            for i, ln in enumerate(lines)
            if i > seam and "run_asi2_base_adapter_rubric_eval.py" in ln
        )
        acquire = [
            i
            for i, ln in enumerate(lines)
            if i > seam and "asi2_eval_lock_acquire" in ln and not ln.strip().startswith("#")
        ]
        release = [
            i
            for i, ln in enumerate(lines)
            if i > seam and "asi2_eval_lock_release" in ln and not ln.strip().startswith("#")
        ]
        self.assertTrue(
            any(seam < a < dispatch for a in acquire),
            "main flow must acquire the asi2-eval lease BEFORE dispatching the "
            f"eval leg (seam L{seam + 1}, dispatch L{dispatch + 1}, "
            f"acquire calls {[a + 1 for a in acquire]})",
        )
        self.assertTrue(
            any(r > dispatch for r in release),
            "main flow must release the lease AFTER the dispatch completes "
            f"(dispatch L{dispatch + 1}, release calls {[r + 1 for r in release]})",
        )
        self.assertTrue(
            any("harness_lib" in ln for ln in lines),
            "acquisition must go through harness_lib",
        )


if __name__ == "__main__":
    unittest.main()
