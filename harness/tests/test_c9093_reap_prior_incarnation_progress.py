"""C-9093: the reaper's stall check must not read a progress file left by a
PRIOR incarnation of the same card as a stall by the current worker.

Live evidence: C-9029 was dispatch-killed twice at ~1m50s (EVENTS 04:48:12
dispatched pid 18053 -> 04:50:02 stalled-killed; 04:58:28 pid 4241 ->
05:00:01 stalled-killed) because agents/C-9029.progress retained the mtime of
a previous dispatch. hb_age must key off max(mtime, started_utc): the file
cannot be older than the current incarnation. A genuinely stale worker
(started_utc AND mtime both past STALL_MIN) must still be killed."""

import os
import sys
import tempfile
import time
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
os.environ.setdefault("QGH_STATE_DIR", tempfile.mkdtemp(prefix="qgh-c9093-"))
sys.path.insert(0, HARNESS_DIR)
import harness_lib as H  # noqa: E402
import qgh  # noqa: E402
from test_integration import running_agent, seed_card  # noqa: E402


class TestC9093PriorIncarnationProgress(unittest.TestCase):
    def setUp(self):
        import shutil

        for sub in ("agents", "briefs", "locks", "standup", "probes"):
            p = os.path.join(qgh.STATE, sub)
            shutil.rmtree(p, ignore_errors=True)
            os.makedirs(p, exist_ok=True)
        qgh.save_json(os.path.join(qgh.STATE, "QUEUE.json"), {"cards": [], "seq": 0})
        qgh.save_json(os.path.join(qgh.STATE, "FLEET.json"), {"agents": []})
        qgh.save_json(
            os.path.join(qgh.STATE, "OPS.json"),
            {"consecutive_spawn_failures": 0, "backoff_until_utc": None},
        )

    def _backdate_started(self, entry, minutes_ago):
        fleet = qgh.load_fleet(qgh.STATE)
        for a in fleet["agents"]:
            if a["pid"] == entry["pid"]:
                a["started_utc"] = (
                    H.datetime.utcnow() - H.timedelta(minutes=minutes_ago)
                ).strftime("%Y-%m-%dT%H:%M:%SZ")
        qgh.save_fleet(qgh.STATE, fleet)

    def test_fresh_agent_with_prior_incarnation_progress_not_stall_killed(self):
        c = seed_card()
        entry, log, proc = running_agent(c, "sleep 120\n")  # fresh dispatch, hung on work
        self.addCleanup(proc.wait)
        self.addCleanup(proc.kill)
        hb = os.path.join(qgh.STATE, "agents", "{}.progress".format(c["id"]))
        with open(hb, "w") as f:
            f.write("left by a prior incarnation of this card\n")
        old = time.time() - 3 * 3600
        os.utime(hb, (old, old))  # progress mtime 3h old, started_utc = now
        qgh._reap()
        time.sleep(2.5)  # TERM(1s) + KILL grace: prove no kill was issued
        self.assertTrue(
            H.pid_alive(proc.pid),
            "fresh dispatch must not be stall-killed for a progress file "
            "left by a prior incarnation",
        )
        fleet = qgh.load_fleet(qgh.STATE)
        self.assertEqual(fleet["agents"][0]["status"], "running")

    def test_genuinely_stale_live_agent_still_killed(self):
        c = seed_card()
        entry, log, proc = running_agent(c, "sleep 120\n")
        self.addCleanup(proc.wait)
        self.addCleanup(proc.kill)
        self._backdate_started(entry, minutes_ago=H.STALL_MIN + 10)
        hb = os.path.join(qgh.STATE, "agents", "{}.progress".format(c["id"]))
        with open(hb, "w") as f:
            f.write("started once, then the worker hung\n")
        old = time.time() - (H.STALL_MIN + 5) * 60
        os.utime(hb, (old, old))  # started_utc AND mtime both past STALL_MIN
        qgh._reap()
        time.sleep(2.5)
        self.assertFalse(
            H.pid_alive(proc.pid),
            "real hang (both ages past STALL_MIN) must still be killed",
        )
        q = qgh.load_queue(qgh.STATE)
        card = H.find_card(q, c["id"])
        self.assertEqual(card["status"], "ready")
        self.assertIn("stalled", card["bounce_reason"])


if __name__ == "__main__":
    unittest.main()
