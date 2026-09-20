"""C-0022 RED tests: eval-box lock helper (asi2-eval lease).

Four concurrent cards (C-0002 slices, C-0010 base+adapter, C-0015) launch
18-task holdout legs at ONE eval box (ASI2) with no serialization -- the
launcher (scripts/asi2_loop_eval.sh) nohups NPU evals with only a per-ts
pid check, so two legs with different ts both fire and interleave writes.

These tests pin the lock helper BEFORE it exists (RED first):
  - double-acquire refusal  (a fresh, live lock is never stolen)
  - stale-lock takeover     (a crashed holder must not wedge the box forever)
  - dead-pid takeover       (crash recovery beats waiting out stale_s)
  - release-safety          (only the owner's release removes the lock)
"""

import json
import os
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import harness_lib as H  # noqa: E402


def _write_lock(path, pid, age_s=0):
    """Simulate an existing holder lock file, optionally aged."""
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - age_s))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dict(pid=pid, ts=ts, why="simulated-holder"), f)


class TestEvalBoxLock(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="qgh-locktest-")
        self.path = os.path.join(self.dir, "asi2-eval.lock")

    def test_double_acquire_refused(self):
        """Fresh lock held by a live process -> second acquirer gets None."""
        tok = H.acquire_lock(self.path)
        self.assertIsNotNone(tok, "first acquire must succeed on a free path")
        tok2 = H.acquire_lock(self.path)
        self.assertIsNone(tok2, "double acquire must be REFUSED while fresh+live")
        self.assertTrue(os.path.exists(self.path), "refused acquire must not delete the lock")

    def test_stale_lock_takeover(self):
        """Lock older than stale_s -> takeover succeeds (crashed holder)."""
        _write_lock(self.path, pid=os.getpid(), age_s=H.LOCK_STALE_S + 60)
        tok = H.acquire_lock(self.path, stale_s=H.LOCK_STALE_S)
        self.assertIsNotNone(tok, "stale lock must be taken over")

    def test_dead_pid_takeover(self):
        """Young lock whose holder pid is DEAD -> takeover (crash recovery)."""
        dead_pid = self._spawn_and_reap()
        _write_lock(self.path, pid=dead_pid, age_s=0)
        tok = H.acquire_lock(self.path, stale_s=H.LOCK_STALE_S)
        self.assertIsNotNone(tok, "lock of a dead pid must be taken over, not awaited")

    def test_release_only_own_lock(self):
        """A foreign token must NOT remove the lock; owner release does."""
        tok = H.acquire_lock(self.path)
        foreign = dict(tok)
        foreign["pid"] = tok["pid"] + 1
        self.assertFalse(H.release_lock(self.path, foreign), "foreign release must fail")
        self.assertTrue(os.path.exists(self.path), "foreign release must not delete the lock")
        self.assertTrue(H.release_lock(self.path, tok), "owner release must succeed")
        self.assertFalse(os.path.exists(self.path), "owner release must remove the lock")

    # -- helpers ------------------------------------------------------------
    def _spawn_and_reap(self):
        """A pid that is guaranteed dead (spawned child, waited)."""
        r, w = os.pipe()
        pid = os.fork()
        if pid == 0:  # child: exit immediately
            os.close(r)
            os.write(w, b"x")
            os._exit(0)
        os.close(w)
        os.read(r, 1)
        os.close(r)
        os.waitpid(pid, 0)
        return pid


if __name__ == "__main__":
    unittest.main()


class TestBriefCarriesBoxLease(unittest.TestCase):
    """C-0022: every leg brief must carry the asi2-eval lease instruction,
    so legs launched before any launcher edit still serialize."""

    def test_brief_names_asi2_eval_lock(self):
        goal = dict(objective="18/18", target_pass="18/18")
        card = H.new_card(
            title="eval leg card", lane="evaluator", why="test why", acceptance=["test acceptance"]
        )
        brief = H.compose_brief(goal, card, dep_results=[])
        self.assertIn("asi2-eval.lock", brief, "leg brief must name the box lease")
        self.assertIn("acquire_lock", brief, "leg brief must name the helper")
