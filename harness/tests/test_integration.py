"""Integration tests: the full card -> worker -> harvest lifecycle with REAL
process semantics (fake workers, no model API). Runs against an isolated
QGH_STATE_DIR — the live harness state is never touched."""

import json
import os
import subprocess
import sys
import tempfile
import time
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
os.environ["QGH_STATE_DIR"] = tempfile.mkdtemp(prefix="qgh-int-")
sys.path.insert(0, HARNESS_DIR)
import harness_lib as H  # noqa: E402
import qgh  # noqa: E402

qgh.STATE = os.environ["QGH_STATE_DIR"]  # rebind in case conftest already imported qgh


def make_card(**kw):
    base = dict(title="test card", lane="fixer", why="test why", acceptance=["test acceptance"])
    base.update(kw)
    return H.new_card(**base)


def seed_card(**kw):
    # ids must never collide with leftover per-card artifacts (progress/log/lock)
    # from earlier tests: keep the seq high and unique for the whole run.
    q = qgh.load_queue(qgh.STATE)
    if q.get("seq", 0) < 9000:
        q["seq"] = 9000
        qgh.save_queue(qgh.STATE, q)
    c = H.add_card(
        q,
        H.new_card(
            title=kw.pop("title", "test card"),
            lane=kw.pop("lane", "fixer"),
            why=kw.pop("why", "test why"),
            acceptance=["test acceptance"],
            **kw,
        ),
    )
    qgh.save_queue(qgh.STATE, q)
    return c


def wait_exit(proc, timeout=10):
    """Wait until the fake worker actually exits (tests must not race the reaper:
    a live, not-overdue worker is CORRECTLY skipped)."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if proc.poll() is not None:
            return
        time.sleep(0.05)
    raise AssertionError(f"fake worker did not exit in {timeout}s")


def running_agent(card, script_body, budget_min=25, started_min_ago=0):
    """Start a REAL fake worker process and register it in the fleet."""
    path = os.path.join(tempfile.mkdtemp(), "worker.sh")
    with open(path, "w") as f:
        f.write(script_body)
    os.chmod(path, 0o755)
    log = os.path.join(qgh.STATE, "agents", "{}.log".format(card["id"]))
    proc = subprocess.Popen(
        ["/bin/bash", path], stdout=open(log, "w"), stderr=subprocess.STDOUT, start_new_session=True
    )
    q_fleet = qgh.load_fleet(qgh.STATE)
    deadline = H.datetime.utcnow()
    from datetime import timedelta

    deadline = deadline + timedelta(minutes=budget_min)
    entry = {
        "pid": proc.pid,
        "card": card["id"],
        "lane": card["lane"],
        "brief": "x",
        "log": log,
        "started_utc": H.now_iso(),
        "deadline_utc": deadline.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "running",
    }
    if started_min_ago:
        entry["started_utc"] = (
            deadline - timedelta(minutes=budget_min + started_min_ago)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
        entry["deadline_utc"] = (deadline - timedelta(minutes=started_min_ago)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
    q_fleet["agents"].append(entry)
    qgh.save_fleet(qgh.STATE, q_fleet)
    qc = qgh.load_queue(qgh.STATE)
    H.claim_card(qc, card["id"], str(proc.pid))
    qgh.save_queue(qgh.STATE, qc)
    return entry, log, proc


WAIT_SUCCESS = (
    "echo 'RED test written'\necho 'GREEN 5/5 pass'\necho 'RESULT: DONE all acceptance met'\n"
)
WAIT_BLOCKED = "echo 'RESULT: BLOCKED missing inputs'\n"


class TestLifecycle(unittest.TestCase):
    def setUp(self):
        import shutil

        for sub in ("agents", "briefs", "locks", "standup", "probes"):
            p = os.path.join(qgh.STATE, sub)
            shutil.rmtree(p, ignore_errors=True)
            os.makedirs(p, exist_ok=True)
        # fresh queue/fleet/ops per test
        qgh.save_json(os.path.join(qgh.STATE, "QUEUE.json"), {"cards": [], "seq": 0})
        qgh.save_json(os.path.join(qgh.STATE, "FLEET.json"), {"agents": []})
        qgh.save_json(
            os.path.join(qgh.STATE, "OPS.json"),
            {"consecutive_spawn_failures": 0, "backoff_until_utc": None},
        )
        time.sleep(0.1)

    def test_success_with_tdd_gate(self):
        c = seed_card(gates=["tdd"])
        _, _, proc = running_agent(c, WAIT_SUCCESS)
        wait_exit(proc)
        reaped = qgh._reap()
        self.assertEqual(reaped, 1)
        q = qgh.load_queue(qgh.STATE)
        card = H.find_card(q, c["id"])
        self.assertEqual(card["status"], "done")

    def test_done_without_gate_evidence_bounces(self):
        c = seed_card(gates=["tdd"])
        _, _, proc = running_agent(c, "echo 'RESULT: DONE trust me'\n")
        wait_exit(proc)
        qgh._reap()
        q = qgh.load_queue(qgh.STATE)
        card = H.find_card(q, c["id"])
        self.assertEqual(card["status"], "ready")  # re-armed
        self.assertEqual(card["bounce_count"], 1)  # strike burned

    def test_blocked_verdict_bounces(self):
        c = seed_card()
        _, _, proc = running_agent(c, WAIT_BLOCKED)
        wait_exit(proc)
        qgh._reap()
        q = qgh.load_queue(qgh.STATE)
        self.assertEqual(H.find_card(q, c["id"])["status"], "ready")

    def test_environmental_death_spares_card_and_counts_failures(self):
        c = seed_card()
        entry, log, proc = running_agent(c, "exit 0\n")  # dies silently
        proc.wait()
        qgh._reap()
        q = qgh.load_queue(qgh.STATE)
        card = H.find_card(q, c["id"])
        self.assertEqual(card["status"], "ready")
        self.assertEqual(card["bounce_count"], 0)  # NO strike
        ops = H.load_ops(qgh.STATE)
        # C-9449: environmental deaths must NOT trip the global backoff
        self.assertEqual(ops["consecutive_spawn_failures"], 0)
        self.assertFalse(H.backoff_active(ops))
        # second environmental death still does not trip global backoff
        c2 = seed_card()
        _, _, p2 = running_agent(c2, "exit 0\n")
        p2.wait()
        qgh._reap()
        ops = H.load_ops(qgh.STATE)
        self.assertFalse(H.backoff_active(ops), "environmental deaths must not trip global backoff")

    def test_overrun_hung_worker_killed_and_struck(self):
        c = seed_card()
        entry, log, proc = running_agent(
            c, "sleep 60\n", budget_min=25, started_min_ago=30
        )  # deadline passed
        time.sleep(0.3)
        self.assertTrue(H.pid_alive(proc.pid))
        qgh._reap()
        time.sleep(2.5)  # TERM(1s) + KILL grace
        self.assertFalse(H.pid_alive(proc.pid), "hung worker must be killed")
        q = qgh.load_queue(qgh.STATE)
        card = H.find_card(q, c["id"])
        self.assertEqual(card["status"], "ready")  # re-armed via bounce
        self.assertEqual(card["bounce_count"], 1)  # a strike: it burned its budget
        ops = H.load_ops(qgh.STATE)
        self.assertEqual(ops["consecutive_spawn_failures"], 0)  # NOT an API outage

    def test_auto_plan_when_queue_runs_dry(self):
        c = seed_card(lane="evaluator", gates=["eval-failclosed"])
        qc = qgh.load_queue(qgh.STATE)
        H.claim_card(qc, c["id"], "x")  # the only card becomes running
        qgh.save_queue(qgh.STATE, qc)
        qgh._auto_plan(qgh.load_goal(qgh.STATE))
        q = qgh.load_queue(qgh.STATE)
        planners = [x for x in q["cards"] if x["lane"] == "planner" and x["status"] == "ready"]
        self.assertEqual(len(planners), 1)

    def test_third_bounce_kills_card(self):
        c = seed_card()
        for _ in range(3):
            q = qgh.load_queue(qgh.STATE)
            card = H.find_card(q, c["id"])
            if card["status"] == "ready":
                H.release_card(card, "bounced", "x", "no evidence")
                qgh.save_queue(qgh.STATE, q)
        q = qgh.load_queue(qgh.STATE)
        self.assertEqual(H.find_card(q, c["id"])["status"], "bounced")


def canonical_sha_pins():
    """C-0031: the composer verdict shape pins the frozen holdout bench +
    scorer chain to the canonical committed manifest (5c36b1d)."""
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    manifest = {}
    with open(os.path.join(root, "evals/benchmarks/sapo_promotion_holdout_v1_18.sha256")) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                sha, rel = line.split(None, 1)
                manifest[rel.strip()] = sha
    return manifest["evals/benchmarks/sapo_promotion_holdout_v1_18.txt"], manifest


def compliant_verdict():
    # Composer-shaped two-leg verdict (C-0020 + C-0031 sha pins): the only
    # shape that can satisfy the done-check.
    per_task = dict(
        ("task_" + str(i).zfill(2), dict(adapter_pass=True, base_pass=False)) for i in range(18)
    )
    return dict(
        pass_adapter="18/18",
        pass_base="1/18",
        beats_base=True,
        goal_target="18/18",
        adapter_applied_marker=True,
        adapter_probe_differs_marker=True,
        independent_second_leg=True,
        scorer_version="holdout-scorer-1.2.0",
        holdout_sha256=canonical_sha_pins()[0],
        scorer_shas={
            rel: sha
            for rel, sha in canonical_sha_pins()[1].items()
            if rel
            in (
                "evals/runner/single_candidate_eval.py",
                "scripts/run_asi2_base_adapter_rubric_eval.py",
                "evals/runner/candidate_sanitize.py",
                "harness/beats_base.py",
            )
        },
        leg1=dict(
            ref="outputs/leg1.json",
            runner_mechanism="parallel-3-slice",
            box="ASI2",
            markers=dict(adapter_applied=True, adapter_probe_differs=True),
        ),
        leg2=dict(
            ref="outputs/leg2.json",
            runner_mechanism="sequential-single-slice",
            box="ASI2",
            markers=dict(adapter_applied=True, adapter_probe_differs=True),
        ),
        per_task=per_task,
        model_identity=dict(
            status="PASS",
            base_model="Qwen3.8-27B",
            sha256="abc123def456abc123def456abc123def456abc123def456abc123def456abcd",
        ),
    )


class TestDoneCheckCli(unittest.TestCase):
    def test_exit_codes(self):
        tmp_repo = tempfile.mkdtemp()
        os.makedirs(os.path.join(tmp_repo, "outputs"))
        old_repo = qgh.REPO
        try:
            qgh.REPO = tmp_repo
            with self.assertRaises(SystemExit) as ctx:
                qgh.cmd_done_check(None)
            self.assertEqual(ctx.exception.code, 1)  # OPEN: not achieved
            # C-0020: leg1-only 18/18 verdict (no probe-differs, no leg2)
            # must NOT retire the goal -> exit 1.
            v = compliant_verdict()
            del v["leg2"]
            v["adapter_probe_differs_marker"] = None
            with open(os.path.join(tmp_repo, "outputs", "verdict_leg1.json"), "w") as f:
                json.dump(v, f)
            with self.assertRaises(SystemExit) as ctx:
                qgh.cmd_done_check(None)
            self.assertEqual(ctx.exception.code, 1)  # leg1-only: NOT achieved
            v = compliant_verdict()
            with open(os.path.join(tmp_repo, "outputs", "verdict_final.json"), "w") as f:
                json.dump(v, f)
            with self.assertRaises(SystemExit) as ctx:
                qgh.cmd_done_check(None)
            self.assertEqual(ctx.exception.code, 0)  # ACHIEVED
        finally:
            qgh.REPO = old_repo


class TestBackoffBlocksDispatch(unittest.TestCase):
    def test_dispatch_skips_under_backoff(self):
        qgh.save_json(os.path.join(qgh.STATE, "QUEUE.json"), {"cards": [], "seq": 0})
        qgh.save_json(os.path.join(qgh.STATE, "FLEET.json"), {"agents": []})
        seed_card(lane="fixer")
        ops = {
            "consecutive_spawn_failures": 2,
            "backoff_until_utc": (H.datetime.utcnow() + H.timedelta(minutes=10)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
        }
        qgh.save_json(os.path.join(qgh.STATE, "OPS.json"), ops)
        qgh.cmd_dispatch(type("A", (), {"lane": None})())
        fleet = qgh.load_fleet(qgh.STATE)
        self.assertEqual(len(fleet["agents"]), 0, "backoff must block dispatch")


if __name__ == "__main__":
    unittest.main()


class TestWipLimits(unittest.TestCase):
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

    def test_dispatch_never_exceeds_wip_or_global_cap(self):
        # Use real WIP_LIMITS + MAX_LIVE_AGENTS from the harness config.
        fixer_wip = H.WIP_LIMITS.get("fixer", 1)
        eval_wip = H.WIP_LIMITS.get("evaluator", 1)
        global_cap = qgh.MAX_LIVE_AGENTS
        # Seed more cards than any limit so the caps are binding.
        n_fixer = min(fixer_wip + 3, global_cap + 3)
        n_eval = min(eval_wip + 3, global_cap + 3)
        for i in range(n_fixer):
            seed_card(title=f"fixer card number {i}", lane="fixer")
        for i in range(n_eval):
            seed_card(title=f"eval card number {i}", lane="evaluator")
        spawned = {"n": 0}

        def fake_spawn(goal, queue, card, dep_results):
            spawned["n"] += 1
            return {
                "pid": os.getpid(),
                "card": card["id"],
                "lane": card["lane"],
                "brief": "x",
                "log": "x",
                "started_utc": H.now_iso(),
                "deadline_utc": (H.datetime.utcnow() + H.timedelta(minutes=5)).strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                ),
                "status": "running",
            }

        real = qgh.spawn_worker
        qgh.spawn_worker = fake_spawn
        try:
            qgh.cmd_dispatch(type("A", (), {"lane": None})())
        finally:
            qgh.spawn_worker = real
        q = qgh.load_queue(qgh.STATE)
        running = [c for c in q["cards"] if c["status"] == "running"]
        by_lane = {}
        for c in running:
            by_lane[c["lane"]] = by_lane.get(c["lane"], 0) + 1
        self.assertLessEqual(by_lane.get("fixer", 0), fixer_wip)
        self.assertLessEqual(by_lane.get("evaluator", 0), eval_wip)
        self.assertLessEqual(len(running), global_cap)  # global cap respected


class TestStaleTickLock(unittest.TestCase):
    def setUp(self):
        import shutil

        # Use an isolated state dir so real cron/launchd ticks don't interfere
        self._old_state = qgh.STATE
        self._old_repo = qgh.REPO
        qgh.STATE = os.path.join(tempfile.mkdtemp(), "state")
        qgh.TICK_LOCK = os.path.join(qgh.STATE, "locks", "tick.lock")
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
        goal = {
            "objective": "test objective",
            "model": "Qwen3.8-27B",
            "target_pass": "18/18",
            "status": "OPEN",
            "created_utc": "2026-09-20T00:00:00Z",
            "done_criteria": ["a", "b", "c"],
        }
        qgh.save_json(os.path.join(qgh.STATE, "GOAL.json"), goal)

    def tearDown(self):
        qgh.STATE = self._old_state
        qgh.TICK_LOCK = os.path.join(qgh.STATE, "locks", "tick.lock")

    def test_tick_breaks_stale_lock_and_proceeds(self):
        import time as _t

        os.makedirs(os.path.join(qgh.STATE, "locks"), exist_ok=True)
        lock = os.path.join(qgh.STATE, "locks", "tick.lock")
        os.makedirs(lock, exist_ok=True)
        with open(os.path.join(lock, "pid"), "w") as f:
            f.write("999999999")  # dead pid
        old = _t.time() - 7200  # 2h old > stale window
        os.utime(lock, (old, old))
        qgh.cmd_tick(None)  # must NOT say "skipped"; must break + run
        self.assertFalse(os.path.exists(lock), "stale lock must be broken")

    def test_tick_skips_live_young_lock(self):
        os.makedirs(os.path.join(qgh.STATE, "locks"), exist_ok=True)
        lock = os.path.join(qgh.STATE, "locks", "tick.lock")
        if os.path.exists(lock):
            import shutil

            shutil.rmtree(lock)
        os.makedirs(lock, exist_ok=True)
        with open(os.path.join(lock, "pid"), "w") as f:
            f.write(str(os.getpid()))  # ALIVE pid, fresh mtime
        # a second tick must skip (simulated concurrent tick)
        import contextlib
        import io

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            qgh.cmd_tick(None)
        self.assertIn("skipped", buf.getvalue())
        import shutil

        shutil.rmtree(lock)


class TestGlobalPriorityDispatch(unittest.TestCase):
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

    def test_p0_in_late_lane_beats_p3_in_early_lane(self):
        """LANES tuple order is planner-first; priority must dominate anyway.
        Uses non-box-bound lanes to avoid the quota probe gate."""
        low = seed_card(title="cleanup task here", lane="planner", priority=3)
        high = seed_card(title="verify deploy integrity", lane="fixer", priority=0)
        order = []

        def fake_spawn(goal, queue, card, dep_results):
            order.append(card["id"])
            return {
                "pid": os.getpid(),
                "card": card["id"],
                "lane": card["lane"],
                "brief": "x",
                "log": "x",
                "started_utc": H.now_iso(),
                "deadline_utc": (H.datetime.utcnow() + H.timedelta(minutes=5)).strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                ),
                "status": "running",
            }

        real = qgh.spawn_worker
        qgh.spawn_worker = fake_spawn
        try:
            qgh.cmd_dispatch(type("A", (), {"lane": None})())
        finally:
            qgh.spawn_worker = real
        self.assertEqual(order, [high["id"], low["id"]], "P0 fixer must dispatch before P3 planner")


class TestStallDetection(unittest.TestCase):
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

    def test_stale_heartbeat_kills_worker_and_bounces(self):
        import time as _t

        c = seed_card()
        entry, log, proc = running_agent(c, "sleep 120\n")  # hangs
        # C-9093: a GENUINE hang means this incarnation is itself old enough
        # to have heartbeated and gone silent (started_utc past STALL_MIN too);
        # a fresh start with an old mtime is a prior incarnation, not a stall.
        fleet = qgh.load_fleet(qgh.STATE)
        for a in fleet["agents"]:
            if a["pid"] == entry["pid"]:
                a["started_utc"] = (
                    H.datetime.utcnow() - H.timedelta(minutes=H.STALL_MIN + 10)
                ).strftime("%Y-%m-%dT%H:%M:%SZ")
        qgh.save_fleet(qgh.STATE, fleet)
        hb = os.path.join(qgh.STATE, "agents", "{}.progress".format(c["id"]))
        with open(hb, "w") as f:
            f.write("started\n")
        old = _t.time() - (H.STALL_MIN + 5) * 60
        os.utime(hb, (old, old))  # heartbeat stale > STALL_MIN
        qgh._reap()
        time.sleep(2.5)
        self.assertFalse(H.pid_alive(proc.pid), "stalled worker must be killed")
        q = qgh.load_queue(qgh.STATE)
        card = H.find_card(q, c["id"])
        self.assertEqual(card["status"], "ready")
        self.assertIn("stalled", card["bounce_reason"])

    def test_fresh_heartbeat_never_kills(self):
        c = seed_card()
        entry, log, proc = running_agent(c, "sleep 2\n")
        hb = os.path.join(qgh.STATE, "agents", "{}.progress".format(c["id"]))
        with open(hb, "w") as f:
            f.write("working\n")
        qgh._reap()  # heartbeat fresh; worker alive; must be left alone
        self.assertTrue(H.pid_alive(proc.pid))
        proc.wait()


class TestBriefHeartbeat(unittest.TestCase):
    def test_brief_contains_heartbeat_path_and_stall_rule(self):
        c = make_card()
        b = H.compose_brief(
            "g", c, dep_results=[], heartbeat_path="harness/state/agents/C-TEST.progress"
        )
        self.assertIn("harness/state/agents/C-TEST.progress", b)
        self.assertIn("HEARTBEAT", b)
        self.assertIn("STALLED", b)


class TestApiErrorClassification(unittest.TestCase):
    def test_api_error_output_is_environmental_never_strike(self):
        os.makedirs(os.path.join(qgh.STATE, "agents"), exist_ok=True)
        qgh.save_json(os.path.join(qgh.STATE, "QUEUE.json"), {"cards": [], "seq": 0})
        qgh.save_json(os.path.join(qgh.STATE, "FLEET.json"), {"agents": []})
        qgh.save_json(
            os.path.join(qgh.STATE, "OPS.json"),
            {"consecutive_spawn_failures": 0, "backoff_until_utc": None},
        )
        c = seed_card()
        entry, log, proc = running_agent(c, "echo 'API Error: Unable to connect to API'\n")
        wait_exit(proc)
        qgh._reap()
        q = qgh.load_queue(qgh.STATE)
        card = H.find_card(q, c["id"])
        self.assertEqual(card["status"], "ready")
        self.assertEqual(card["bounce_count"], 0, "API outage must not strike the card")
        ops = H.load_ops(qgh.STATE)
        # C-9449: environmental (API outage) must not increment global counter
        self.assertEqual(ops["consecutive_spawn_failures"], 0)


class TestDispatchDeadlineIntegrity(unittest.TestCase):
    """A fleet entry's deadline must NEVER predate its own start (live finding:
    re-dispatch under a lost-update race resurrected a stale card deadline and
    the reaper then overrun-killed healthy workers)."""

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

    def test_entry_deadline_always_after_start_even_with_stale_claim(self):
        c = seed_card(budget_min=30)
        # simulate the race: the card's deadline field is stale (lost update)
        q = qgh.load_queue(qgh.STATE)
        card = H.find_card(q, c["id"])
        card["claimed_utc"] = "2026-09-16T10:00:00Z"
        card["deadline_utc"] = "2026-09-16T10:30:00Z"  # far in the past
        qgh.save_queue(qgh.STATE, q)

        class FakeProc:
            pid = os.getpid()
            args = []
            returncode = 0

            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def communicate(self, *a, **k):
                return b"", b""

            def kill(self):
                pass

            def wait(self, *a, **k):
                return 0

            def poll(self):
                return None

        real_popen = qgh.subprocess.Popen
        qgh.subprocess.Popen = lambda *a, **k: FakeProc()
        try:
            entry = qgh.spawn_worker(qgh.load_goal(qgh.STATE), q, card, [])
        finally:
            qgh.subprocess.Popen = real_popen
            import shutil

            shutil.rmtree(
                os.path.join(qgh.STATE, "locks", "agent-{}.lock".format(c["id"])),
                ignore_errors=True,
            )
        self.assertIsNotNone(entry)
        self.assertGreater(
            entry["deadline_utc"],
            entry["started_utc"],
            "spawn_worker must derive the deadline from its own clock",
        )
        self.assertEqual(entry["budget_min"], 30)

    def test_reap_neutralizes_corrupt_deadline_entries(self):
        c = seed_card(budget_min=30)
        running_agent(c, "sleep 30\n", budget_min=30)
        fleet = qgh.load_fleet(qgh.STATE)
        for a in fleet["agents"]:
            if a["card"] == c["id"]:
                a["deadline_utc"] = "2026-09-16T10:00:00Z"  # corrupt: predates start
        qgh.save_fleet(qgh.STATE, fleet)
        qgh._reap()  # must not kill the healthy worker for a corrupt deadline
        alive_worker = H.pid_alive(fleet["agents"][0]["pid"])
        self.assertTrue(alive_worker, "corrupt deadline must not overrun-kill a live worker")
        proc_pid = fleet["agents"][0]["pid"]
        os.killpg(proc_pid, 15)  # cleanup


class TestDepBlockerSelfHeal(unittest.TestCase):
    """A ready card dep-blocked on a TERMINALLY bounced card whose bounces were
    environmental must self-heal: the blocker re-arms (strikes reset), the child
    becomes claimable. Deps on DEAD cards mint a planner card instead."""

    def setUp(self):
        for sub in ("agents", "briefs", "locks", "standup", "probes"):
            os.makedirs(os.path.join(qgh.STATE, sub), exist_ok=True)
        qgh.save_json(os.path.join(qgh.STATE, "QUEUE.json"), {"cards": [], "seq": 0})
        qgh.save_json(os.path.join(qgh.STATE, "FLEET.json"), {"agents": []})
        qgh.save_json(
            os.path.join(qgh.STATE, "OPS.json"),
            {"consecutive_spawn_failures": 0, "backoff_until_utc": None},
        )

    def test_env_bounced_blocker_requeues_and_unblocks_child(self):
        blocker = seed_card(title="box leg task", lane="evaluator")
        q = qgh.load_queue(qgh.STATE)
        b = H.find_card(q, blocker["id"])
        b["status"] = "bounced"  # terminal
        b["bounce_count"] = 3
        b["bounce_reason"] = "no RESULT verdict (dead) API Error: Unable to connect to API"
        b["result"] = "API Error: Unable to connect to API"
        child = H.add_card(
            q,
            H.new_card(
                title="child card",
                lane="evaluator",
                why="test why",
                acceptance=["test acceptance"],
                deps=[blocker["id"]],
            ),
        )
        qgh.save_queue(qgh.STATE, q)
        qgh._reconcile_dep_blockers()
        q = qgh.load_queue(qgh.STATE)
        b2 = H.find_card(q, blocker["id"])
        self.assertEqual(b2["status"], "ready", "env-bounced blocker must re-arm")
        self.assertEqual(b2["bounce_count"], 0, "environmental strikes must reset")
        # child stays blocked until the blocker COMPLETES (correct semantics):
        self.assertNotIn(child["id"], [c["id"] for c in H.ready_cards(q)])
        b2["status"] = "done"
        qgh.save_queue(qgh.STATE, q)
        q = qgh.load_queue(qgh.STATE)
        self.assertIn(
            child["id"],
            [c["id"] for c in H.ready_cards(q)],
            "child must unblock once the re-armed blocker completes",
        )

    def test_dead_blocker_mints_planner(self):
        blocker = seed_card(title="hopeless", lane="fixer")
        q = qgh.load_queue(qgh.STATE)
        b = H.find_card(q, blocker["id"])
        b["status"] = "dead"
        b["bounce_reason"] = "genuine failure 3 strikes"
        H.add_card(
            q,
            H.new_card(
                title="child card2",
                lane="fixer",
                why="test why",
                acceptance=["test acceptance"],
                deps=[blocker["id"]],
            ),
        )
        qgh.save_queue(qgh.STATE, q)
        planners_before = sum(
            1 for c in q["cards"] if c["lane"] == "planner" and c["status"] == "ready"
        )
        qgh._reconcile_dep_blockers()
        q = qgh.load_queue(qgh.STATE)
        planners_after = sum(
            1 for c in q["cards"] if c["lane"] == "planner" and c["status"] == "ready"
        )
        # The unblocked child is claimable work -- no idle mint needed.
        # The dep edge drop makes the child dispatchable, so the board
        # is NOT genuinely idle and no planner should be minted.
        self.assertEqual(
            planners_after,
            planners_before,
            "unblocked dependent is claimable work: no idle mint",
        )
        # Verify the dep edge was actually dropped
        for c in q["cards"]:
            if c["id"] != blocker["id"] and c.get("lane") == "fixer":
                self.assertNotIn(blocker["id"], c.get("deps", []), "dead dep edge must be dropped")


class TestAutoPlanIdempotent(unittest.TestCase):
    def test_no_duplicate_planner_mint(self):
        for sub in ("agents", "briefs", "locks", "standup", "probes"):
            os.makedirs(os.path.join(qgh.STATE, sub), exist_ok=True)
        qgh.save_json(os.path.join(qgh.STATE, "QUEUE.json"), {"cards": [], "seq": 0})
        qgh.save_json(os.path.join(qgh.STATE, "FLEET.json"), {"agents": []})
        qgh._auto_plan({})
        qgh._auto_plan({})
        qgh._auto_plan({})
        q = qgh.load_queue(qgh.STATE)
        n = sum(
            1
            for c in q["cards"]
            if c["lane"] == "planner" and c["title"].startswith("Queue nearly empty")
        )
        self.assertEqual(n, 1, "auto_plan must be idempotent while one is live")


class TestPidReuseSafety(unittest.TestCase):
    """pid_alive lies across macOS pid reuse: a fleet entry whose recorded
    process identity (lstart) no longer matches must be treated DEAD, and the
    reaper must NEVER kill the unrelated process that now owns the pid."""

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

    def test_reaped_pid_reuse_does_not_kill_current_owner(self):
        # an innocent LONG-LIVED process (this test itself) holds the pid
        victim = os.getpid()
        c = seed_card(budget_min=30)
        entry, log, proc = running_agent(c, "sleep 300\n")  # real worker
        real_worker_pid = proc.pid
        fleet = qgh.load_fleet(qgh.STATE)
        for a in fleet["agents"]:
            if a["card"] == c["id"]:
                a["pid"] = victim  # simulate pid reuse
                a["lstart"] = "Wed Dec 31 1999 23:59:59 1999"  # stale identity
        qgh.save_fleet(qgh.STATE, fleet)
        qgh._reap()
        self.assertTrue(H.pid_alive(victim), "reaper must not kill the pid's NEW owner")
        q = qgh.load_queue(qgh.STATE)
        card = H.find_card(q, c["id"])
        self.assertIn(
            card["status"],
            ("ready", "bounced"),
            "entry with mismatched identity must be treated dead",
        )
        try:
            os.killpg(real_worker_pid, 15)
        except ProcessLookupError:
            pass


class TestDuplicateIdAutoRepair(unittest.TestCase):
    """Concurrent card-adds can mint duplicate ids (observed live: C-9020/21).
    The tick must re-id duplicates automatically — a single duplicate refused
    by the preflight must never hold the whole dispatch hostage."""

    def setUp(self):
        for sub in ("agents", "briefs", "locks", "standup", "probes"):
            os.makedirs(os.path.join(qgh.STATE, sub), exist_ok=True)
        qgh.save_json(os.path.join(qgh.STATE, "QUEUE.json"), {"cards": [], "seq": 0})
        qgh.save_json(os.path.join(qgh.STATE, "FLEET.json"), {"agents": []})

    def test_dedup_reids_duplicates_keeps_oldest(self):
        q = qgh.load_queue(qgh.STATE)
        a = H.add_card(
            q,
            H.new_card(
                title="first card", lane="fixer", why="test why", acceptance=["test acceptance"]
            ),
        )
        b = H.add_card(
            q,
            H.new_card(
                title="dup card", lane="fixer", why="test why", acceptance=["test acceptance"]
            ),
        )
        b["id"] = a["id"]  # simulate the duplicate mint
        child = H.add_card(
            q,
            H.new_card(
                title="child card",
                lane="fixer",
                why="test why",
                acceptance=["test acceptance"],
                deps=[a["id"]],
            ),
        )
        qgh.save_queue(qgh.STATE, q)
        changed = qgh._dedup_card_ids()
        self.assertTrue(changed)
        q = qgh.load_queue(qgh.STATE)
        ids = [c["id"] for c in q["cards"]]
        self.assertEqual(len(ids), len(set(ids)), "no duplicates may remain")
        self.assertEqual(a["id"], ids[0], "oldest keeps its id")
        self.assertNotEqual(ids[1], a["id"], "duplicate gets a fresh id")
        self.assertIn(a["id"], child["deps"], "deps keep pointing at the keeper")


class TestTransportGate(unittest.TestCase):
    """Box-bound lanes (evaluator/trainer-ops/deploy-integrity) must not
    dispatch while the exec transport is PERSISTENT-wedged: every cycle
    burns a worker spawn just to rediscover the outage."""

    def setUp(self):
        # Mock the quota probe so box-bound lanes are not gated by real API calls
        import unittest.mock as _mock

        self._quota_patcher = _mock.patch.object(
            qgh.QPG, "probe_quota", return_value=dict(verdict="ok", detail="test mock")
        )
        self._quota_patcher.start()
        for sub in ("agents", "briefs", "locks", "standup", "probes"):
            os.makedirs(os.path.join(qgh.STATE, sub), exist_ok=True)
        qgh.save_json(os.path.join(qgh.STATE, "QUEUE.json"), {"cards": [], "seq": 0})
        qgh.save_json(os.path.join(qgh.STATE, "FLEET.json"), {"agents": []})
        qgh.save_json(
            os.path.join(qgh.STATE, "OPS.json"),
            {"consecutive_spawn_failures": 0, "backoff_until_utc": None},
        )

    def tearDown(self):
        self._quota_patcher.stop()

    def test_box_bound_lanes_held_while_transport_wedged(self):
        seed_card(title="eval leg", lane="evaluator")
        seed_card(title="box verify", lane="deploy-integrity")
        seed_card(title="local refactor", lane="qa-steward")  # not box-bound
        H.save_json(
            os.path.join(qgh.STATE, "probes", "asi3.json"),
            {
                "ts": H.now_iso(),
                "status": "unknown",
                "summary": "UNKNOWN (ready-but-exec_wedged: busyAgeMs=30000)",
            },
        )
        order = []

        def fake_spawn(goal, queue, card, dep_results):
            order.append(card["id"])
            return {
                "pid": os.getpid(),
                "card": card["id"],
                "lane": card["lane"],
                "brief": "x",
                "log": "x",
                "started_utc": H.now_iso(),
                "deadline_utc": (H.datetime.utcnow() + H.timedelta(minutes=5)).strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                ),
                "status": "running",
            }

        real = qgh.spawn_worker
        qgh.spawn_worker = fake_spawn
        try:
            qgh.cmd_dispatch(type("A", (), {"lane": None})())
        finally:
            qgh.spawn_worker = real
        q = qgh.load_queue(qgh.STATE)
        dispatched_lanes = {c["lane"] for c in q["cards"] if c["status"] == "running"}
        self.assertNotIn("evaluator", dispatched_lanes)
        self.assertNotIn("deploy-integrity", dispatched_lanes)
        self.assertIn("qa-steward", dispatched_lanes)

    def test_box_lanes_resume_when_transport_ready(self):
        seed_card(title="eval leg", lane="evaluator")
        H.save_json(
            os.path.join(qgh.STATE, "probes", "asi3.json"),
            {"ts": H.now_iso(), "status": "ready", "summary": "READY /health ready=true pid=999"},
        )
        # Mock quota probe to allow dispatch (no API key in test env)
        _real_probe = qgh.QPG.probe_quota
        qgh.QPG.probe_quota = lambda **kw: dict(verdict="ok", detail="test mock", utc=H.now_iso())
        order = []

        def fake_spawn(goal, queue, card, dep_results):
            order.append(card["id"])
            return {
                "pid": os.getpid(),
                "card": card["id"],
                "lane": card["lane"],
                "brief": "x",
                "log": "x",
                "started_utc": H.now_iso(),
                "deadline_utc": (H.datetime.utcnow() + H.timedelta(minutes=5)).strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                ),
                "status": "running",
            }

        real = qgh.spawn_worker
        qgh.spawn_worker = fake_spawn
        try:
            qgh.cmd_dispatch(type("A", (), {"lane": None})())
        finally:
            qgh.spawn_worker = real
            qgh.QPG.probe_quota = _real_probe
        self.assertEqual(len(order), 1, "box lanes must dispatch once transport is ready")

    def test_stale_wedged_probe_does_not_block_after_recovery(self):
        """RED regression, measured outage 2026-09-17: a probe AGENT that dies
        leaves a STALE 'exec_wedged' asi3 probe on disk. The gate read that
        stale file verbatim, so box-bound lanes were held for 5h+ even though
        asi3 had rebooted and asi1/asi2 were healthy. At dispatch-decision
        time a stale/missing probe must be re-measured live; a box that has
        recovered (fresh probe ready) must NOT remain gated.

        This test drives dispatch with a stale wedged probe on disk but a
        mocked live re-probe now reporting ready, and asserts evaluator
        (box-bound) DOES dispatch.
        """
        seed_card(title="eval leg", lane="evaluator")
        stale_ts = (H.datetime.utcnow() - H.timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
        H.save_json(
            os.path.join(qgh.STATE, "probes", "asi3.json"),
            {
                "ts": stale_ts,
                "status": "unknown",
                "summary": "UNKNOWN (ready-but-exec_wedged: busyAgeMs=30000)",
            },
        )
        order = []

        def fake_spawn(goal, queue, card, dep_results):
            order.append(card["id"])
            return {
                "pid": os.getpid(),
                "card": card["id"],
                "lane": card["lane"],
                "brief": "x",
                "log": "x",
                "started_utc": H.now_iso(),
                "deadline_utc": (H.datetime.utcnow() + H.timedelta(minutes=5)).strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                ),
                "status": "running",
            }

        real_refresh = qgh._refresh_box_probe_best_effort
        real_spawn = qgh.spawn_worker
        _real_probe = qgh.QPG.probe_quota
        qgh.QPG.probe_quota = lambda **kw: dict(verdict="ok", detail="test mock", utc=H.now_iso())

        def fake_refresh(sd):
            # live re-measure: the box has rebooted and is NOT wedged now
            H.save_json(
                os.path.join(sd, "probes", "asi3.json"),
                {
                    "ts": H.now_iso(),
                    "status": "ready",
                    "summary": "READY /health ready=true pid=999",
                },
            )

        qgh._refresh_box_probe_best_effort = fake_refresh
        qgh.spawn_worker = fake_spawn
        try:
            qgh.cmd_dispatch(type("A", (), {"lane": None})())
        finally:
            qgh._refresh_box_probe_best_effort = real_refresh
            qgh.spawn_worker = real_spawn
            qgh.QPG.probe_quota = _real_probe
        self.assertEqual(len(order), 1, "recovered box must not stay gated by a stale wedged probe")

    def test_gate_stays_failsafe_when_probe_refresh_fails(self):
        """The stale-probe refresh is best-effort and NEVER opens the gate on a
        refresh failure: if the live re-measure cannot confirm recovery (e.g.
        the boxes are unreachable), the pre-existing wedge evidence must keep
        box-bound lanes held so we never dispatch against a box we couldn't
        verify. Refresh failure => hold; only confirmed recovery clears."""
        seed_card(title="eval leg", lane="evaluator")
        stale_ts = (H.datetime.utcnow() - H.timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
        H.save_json(
            os.path.join(qgh.STATE, "probes", "asi3.json"),
            {
                "ts": stale_ts,
                "status": "unknown",
                "summary": "UNKNOWN (ready-but-exec_wedged: busyAgeMs=30000)",
            },
        )
        order = []

        def fake_spawn(goal, queue, card, dep_results):
            order.append(card["id"])
            return {
                "pid": os.getpid(),
                "card": card["id"],
                "lane": card["lane"],
                "brief": "x",
                "log": "x",
                "started_utc": H.now_iso(),
                "deadline_utc": (H.datetime.utcnow() + H.timedelta(minutes=5)).strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                ),
                "status": "running",
            }

        real_refresh = qgh._refresh_box_probe_best_effort
        real_spawn = qgh.spawn_worker

        def failing_refresh(sd):
            raise RuntimeError("boxes unreachable")

        qgh._refresh_box_probe_best_effort = failing_refresh
        qgh.spawn_worker = fake_spawn
        try:
            qgh.cmd_dispatch(type("A", (), {"lane": None})())
        finally:
            qgh._refresh_box_probe_best_effort = real_refresh
            qgh.spawn_worker = real_spawn
        q = qgh.load_queue(qgh.STATE)
        dispatched_lanes = {c["lane"] for c in q["cards"] if c["status"] == "running"}
        self.assertNotIn("evaluator", dispatched_lanes, "refresh failure must not open the gate")
        self.assertEqual(order, [])
