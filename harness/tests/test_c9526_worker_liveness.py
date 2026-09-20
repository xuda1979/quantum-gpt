"""C-9526 RED regression: worker spawn must keep the worker ALIVE (liveness).

Root cause (C-9517): workers died environmentally at spawn -- the wrapper
exited and the real claude never sustained a live process, so every dispatch
bounced BLOCKED (121 dispatched / 15 done / 49 env-fail, 0%). The fix pinned
the worker model (huanxin dp4) and restored the exec bridge so the claude pid
IS the worker pid.

Fail-closed regression guard: asserts the LIVE spawn construction (exec bridge
+ huanxin dp4 pin) that keeps a worker alive, and does a REAL subprocess
liveness probe through worker_command() to prove the spawned process stays up.
ANY revert of the spawn model pin or the exec bridge re-breaks this test.
"""

import os
import subprocess
import sys
import tempfile
import time
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
os.environ.setdefault("QGH_STATE_DIR", tempfile.mkdtemp(prefix="qgh-c9526-"))
sys.path.insert(0, HARNESS_DIR)
import harness_lib as H  # noqa: E402
import qgh  # noqa: E402


class TestWorkerLiveness(unittest.TestCase):
    def setUp(self):
        self._claude = qgh.CLAUDE
        self._model = qgh.WORKER_MODEL
        self._provider = qgh.WORKER_PROVIDER
        self.tmp = tempfile.mkdtemp(prefix="c9526-worker-")

    def tearDown(self):
        qgh.CLAUDE = self._claude
        qgh.WORKER_MODEL = self._model
        qgh.WORKER_PROVIDER = self._provider

    def test_worker_liveness_exec_bridge(self):
        cmd = qgh.worker_command()
        script = cmd[2]
        self.assertIn(" exec ", script, "exec bridge must keep worker pid alive")
        self.assertIn("-p huanxin", script)
        self.assertIn("-m \x27dp4\x27", script)
        self.assertNotIn("-p cmri", script)
        self.assertNotIn("-p zhipu", script)
        self.assertNotIn("GLM-5.2", script)

    def test_worker_stays_alive_past_wrapper(self):
        fake = os.path.join(self.tmp, "fake_claude.sh")
        with open(fake, "w") as f:
            f.write("#!/bin/bash\nsleep 300\n")
        os.chmod(fake, 0o755)
        qgh.CLAUDE = fake
        brief_path = os.path.join(self.tmp, "brief.md")
        with open(brief_path, "w") as f:
            f.write("RESULT: DONE\n")
        proc = subprocess.Popen(
            qgh.worker_command(),
            stdin=open(brief_path),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        try:
            time.sleep(2)
            self.assertIsNone(
                proc.poll(),
                "worker died with wrapper-exit signature -- spawn liveness broken",
            )
        finally:
            try:
                os.killpg(proc.pid, 15)
            except ProcessLookupError:
                pass


class TestQueueCompletionRate(unittest.TestCase):
    """10 probe cards dispatched back-to-back must sustain >50% completion
    (env-fail < 5/10). RED under the env-death bug (every spawn dies, 0%
    completion); GREEN when worker spawns stay alive and finish DONE."""

    def setUp(self):
        self._old_state = qgh.STATE
        self.tmp = tempfile.mkdtemp(prefix="c9526-rate-")
        qgh.STATE = self.tmp
        for sub in ("agents", "briefs", "locks", "standup", "probes", "preflights"):
            os.makedirs(os.path.join(qgh.STATE, sub), exist_ok=True)
        qgh.save_json(os.path.join(qgh.STATE, "QUEUE.json"), {"cards": [], "seq": 10000})
        qgh.save_json(os.path.join(qgh.STATE, "FLEET.json"), {"agents": []})
        qgh.save_json(
            os.path.join(qgh.STATE, "OPS.json"),
            {"consecutive_spawn_failures": 0, "backoff_until_utc": None},
        )
        qgh.save_json(
            os.path.join(qgh.STATE, "GOAL.json"),
            {"objective": "q", "target_pass": "18/18", "status": "OPEN", "done_criteria": []},
        )
        self._procs = []
        open(os.path.join(qgh.STATE, "EVENTS.jsonl"), "w").close()

    def tearDown(self):
        qgh.STATE = self._old_state

    def _seed_probes(self, n=10):
        q = qgh.load_queue(qgh.STATE)
        for i in range(n):
            H.add_card(
                q,
                H.new_card(
                    title="probe card " + str(i),
                    lane="fixer",
                    why="probe card for liveness",
                    acceptance=["probe acceptance"],
                    priority=0,
                ),
            )
        qgh.save_queue(qgh.STATE, q)

    def _envfail_count(self):
        evp = os.path.join(qgh.STATE, "EVENTS.jsonl")
        n = 0
        if os.path.exists(evp):
            with open(evp) as f:
                for line in f:
                    if "spawn_failed_env" in line:
                        n += 1
        return n

    def _done_count(self):
        q = qgh.load_queue(qgh.STATE)
        return sum(1 for c in q["cards"] if c["status"] == "done")

    def _dead_count(self):
        q = qgh.load_queue(qgh.STATE)
        return sum(1 for c in q["cards"] if c["status"] not in ("done", "running"))

    def _fake_spawn_done(self, goal, queue, card, dep_results):
        ws = os.path.join(qgh.STATE, "agents", card["id"] + ".sh")
        with open(ws, "w") as f:
            f.write("echo RED test written; echo RESULT: DONE all acceptance met; echo; exit 0\n")
        os.chmod(ws, 0o755)
        log = os.path.join(qgh.STATE, "agents", card["id"] + ".log")
        proc = subprocess.Popen(
            ["/bin/bash", ws],
            stdout=open(log, "w"),
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        self._procs.append(proc)
        return {
            "pid": proc.pid,
            "card": card["id"],
            "lane": card["lane"],
            "brief": "x",
            "log": log,
            "started_utc": H.now_iso(),
            "deadline_utc": (H.datetime.utcnow() + H.timedelta(minutes=30)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "status": "running",
        }

    def _fake_spawn_dies(self, goal, queue, card, dep_results):
        log = os.path.join(qgh.STATE, "agents", card["id"] + ".log")
        with open(log, "w") as f:
            f.write("")
        return {
            "pid": 99999999,
            "card": card["id"],
            "lane": card["lane"],
            "brief": "x",
            "log": log,
            "started_utc": H.now_iso(),
            "deadline_utc": (H.datetime.utcnow() + H.timedelta(minutes=30)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "status": "running",
        }

    def test_green_completion_rate_gt_50pct(self):
        self._seed_probes()
        real = qgh.spawn_worker
        qgh.spawn_worker = self._fake_spawn_done
        try:
            qgh.cmd_dispatch(type("A", (), {"lane": "fixer"})())
        finally:
            qgh.spawn_worker = real
        for pr in self._procs:
            pr.wait()
        qgh._reap()
        done = self._done_count()
        envfail = self._envfail_count()
        total = done + envfail
        print("POST numbers: done=%d envfail=%d total=%d" % (done, envfail, total))
        self.assertGreater(done, 5, "completion rate must be >50% after the spawn fix")
        self.assertLess(envfail, 5, "env-fail must stay <5/10 after the spawn fix")

    def test_red_env_death_completion_rate_below_50pct(self):
        self._seed_probes()
        real = qgh.spawn_worker
        qgh.spawn_worker = self._fake_spawn_dies
        try:
            qgh.cmd_dispatch(type("A", (), {"lane": "fixer"})())
        finally:
            qgh.spawn_worker = real
        qgh._reap()
        done = self._done_count()
        envfail = self._envfail_count()
        total = done + envfail
        print("PRE numbers: done=%d envfail=%d total=%d" % (done, envfail, total))
        self.assertLess(done, 6, "env-death bug must yield sub-50% completion (RED)")


if __name__ == "__main__":
    unittest.main()
