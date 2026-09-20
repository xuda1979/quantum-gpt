"""TDD evidence for the harness itself. RED first: run before lib existed.
These tests ARE the harness's own correctness register — every behavior the
manager relies on mechanically is pinned here."""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import harness_lib as H  # noqa: E402


def tmp_state():
    d = tempfile.mkdtemp(prefix="qgh-test-")
    return d


def make_card(**kw):
    base = dict(
        title="test card", lane="fixer", why="test why", acceptance=["acceptance criterion"]
    )
    base.update(kw)
    return H.new_card(**base)


class TestQueue(unittest.TestCase):
    def test_priority_order_and_lane_filter(self):
        q = {"cards": [], "seq": 0}
        c_low = H.add_card(q, make_card(priority=2))
        c_p0 = H.add_card(q, make_card(priority=0))
        H.add_card(q, make_card(priority=0, lane="planner"))
        ready = H.ready_cards(q, "fixer")
        self.assertEqual([c["id"] for c in ready], [c_p0["id"], c_low["id"]])

    def test_deps_gate_readiness(self):
        q = {"cards": [], "seq": 0}
        dep = H.add_card(q, make_card())
        child = H.add_card(q, make_card(deps=[dep["id"]]))
        self.assertEqual(H.ready_cards(q), [dep])
        dep["status"] = "done"
        self.assertEqual([c["id"] for c in H.ready_cards(q)], [child["id"]])

    def test_bounce_rearms_max_two_then_dies(self):
        c = make_card()
        H.release_card(c, "bounced", "no evidence", "gate fail")
        self.assertEqual(c["status"], "ready")
        self.assertEqual(c["bounce_count"], 1)
        H.release_card(c, "bounced", "x", "gate fail")
        self.assertEqual(c["status"], "ready")
        H.release_card(c, "bounced", "x", "gate fail")
        self.assertEqual(c["status"], "bounced")  # 3rd strike stays terminal
        self.assertEqual(c["bounce_count"], 3)


class TestFleetHarvest(unittest.TestCase):
    def test_harvest_parses_result_contract(self):
        d = tempfile.mkdtemp()
        log = os.path.join(d, "x.log")
        with open(log, "w") as f:
            f.write("did stuff\nRESULT: DONE all acceptance met\nEVIDENCE: 3/3 green\n")
        verdict, tail = H.harvest_log(log)
        self.assertEqual(verdict, "DONE")
        self.assertLessEqual(len(tail), 10)

    def test_harvest_fails_closed_on_missing_result(self):
        d = tempfile.mkdtemp()
        log = os.path.join(d, "x.log")
        with open(log, "w") as f:
            f.write("I think it is done\n")
        verdict, _ = H.harvest_log(log)
        self.assertIsNone(verdict)

    def test_pid_alive(self):
        self.assertTrue(H.pid_alive(os.getpid()))
        self.assertFalse(H.pid_alive(999999999))


class TestGates(unittest.TestCase):
    def test_tdd_gate_fails_closed_without_evidence(self):
        ok, _ = H.check_gate("tdd", "I fixed it, tests pass")
        self.assertFalse(ok)
        ok, _ = H.check_gate("tdd", "RED test added first; GREEN 5/5 pass")
        self.assertTrue(ok)

    def test_review_gate(self):
        ok, _ = H.check_gate("review", "notes REVIEW: APPROVED by reviewer")
        self.assertTrue(ok)
        ok, _ = H.check_gate("review", "looks good to me")
        self.assertFalse(ok)

    def test_eval_failclosed_gate(self):
        ok, _ = H.check_gate(
            "eval-failclosed", "log markers: adapter-applied, adapter-probe-differs"
        )
        self.assertTrue(ok)
        ok, _ = H.check_gate("eval-failclosed", "adapter-applied only")
        self.assertFalse(ok)
        ok, _ = H.check_gate("eval-failclosed", "")
        self.assertFalse(ok)

    def test_unknown_gate_fails_closed(self):
        ok, _ = H.check_gate("made-up-gate", "anything")
        self.assertFalse(ok)


class TestBrief(unittest.TestCase):
    def test_brief_small_and_has_contract(self):
        goal = "test goal"
        c = make_card(acceptance=["criterion one", "criterion two"], gates=["tdd"], budget_min=25)
        b = H.compose_brief(goal, c, dep_results=[])
        n = len(b.splitlines())
        self.assertLessEqual(n, H.BRIEF_MAX_LINES)
        self.assertIn("RESULT:", b)
        self.assertIn("ACCEPTANCE", b)
        self.assertIn("RED test first", b)
        self.assertIn("25 min", b)


_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)


def canonical_sha_pins():
    """C-0031: the composer verdict shape pins the frozen holdout bench +
    scorer chain to the canonical committed manifest (5c36b1d)."""
    from evals.runner import holdout_freeze as fz

    manifest = dict(fz.load_manifest(os.path.join(_REPO_ROOT, fz.MANIFEST_RELPATH)))
    return manifest[fz.BENCH_RELPATH], dict((rel, manifest[rel]) for rel in fz.SCORER_CHAIN)


def compliant_verdict(**over):
    # Composer-shaped two-leg verdict (scripts/holdout_verdict.py output):
    # both legs embedded with markers + identity, agreed per_task map, and
    # a scorer_version tag. Same box, distinct runner mechanisms (matches
    # the composer: leg1 parallel-3-slice, leg2 sequential-single-slice).
    hold_sha, scorer_shas = canonical_sha_pins()
    per_task = dict(
        ("task_" + str(i).zfill(2), dict(adapter_pass=True, base_pass=False)) for i in range(18)
    )
    v = dict(
        pass_adapter="18/18",
        pass_base="1/18",
        beats_base=True,
        goal_target="18/18",
        adapter_applied_marker=True,
        adapter_probe_differs_marker=True,
        independent_second_leg=True,
        scorer_version="holdout-scorer-1.2.0",
        holdout_sha256=hold_sha,
        scorer_shas=scorer_shas,
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
        candidates_vs_base_gate={
            "leg1": dict(status="PASS", n_checked=18, n_byte_match=0),
            "leg2": dict(status="PASS", n_checked=18, n_byte_match=0),
        },
        model_identity=dict(
            status="PASS",
            base_model="Qwen/Qwen3.8-27B",
            sha256="a" * 64,
        ),
        _file="verdict_step000100.json",
    )
    v.update(over)
    return v


class TestDoneCheck(unittest.TestCase):
    def test_done_requires_18_of_18_and_beats_base(self):
        goal = dict(target_pass="18/18")
        v = [dict(pass_adapter="3/18", beats_base=True, _file="a.json")]
        done, _ = H.goal_done(goal, v)
        self.assertFalse(done)
        v3 = [dict(pass_adapter="18/18", beats_base=False, _file="c.json")]
        done, _ = H.goal_done(goal, v3)
        self.assertFalse(done)

    def test_done_fails_closed_on_empty(self):
        done, _ = H.goal_done(dict(target_pass="18/18"), [])
        self.assertFalse(done)


class TestDoneCheckTwoLeg(unittest.TestCase):
    # C-0020: a single-leg or untagged verdict can no longer retire the
    # goal. done_criteria 2 (probe-differs marker) and 3 (independent
    # second leg) are BOTH enforced by goal_done, fail-closed.

    def setUp(self):
        self.goal = dict(target_pass="18/18")

    def test_bare_single_verdict_cannot_retire_goal(self):
        v = [dict(pass_adapter="18/18", beats_base=True, _file="b.json")]
        done, _ = H.goal_done(self.goal, v)
        self.assertFalse(done)

    def test_leg1_only_verdict_cannot_retire_goal(self):
        # 18/18 + beats_base + leg1, but NO probe-differs marker, NO leg2.
        v = [compliant_verdict()]
        del v[0]["leg2"]
        v[0]["adapter_probe_differs_marker"] = None
        done, _ = H.goal_done(self.goal, v)
        self.assertFalse(done)

    def test_compliant_two_leg_verdict_satisfies_done(self):
        done, f = H.goal_done(self.goal, [compliant_verdict()])
        self.assertTrue(done)
        self.assertEqual(f, "verdict_step000100.json")

    def test_scorer_version_tag_required(self):
        # Pre-sanitize verdicts (no scorer_version) never satisfy done.
        done, _ = H.goal_done(self.goal, [compliant_verdict(scorer_version="")])
        self.assertFalse(done)
        untagged = [compliant_verdict()]
        del untagged[0]["scorer_version"]
        done, _ = H.goal_done(self.goal, untagged)
        self.assertFalse(done)

    def test_probe_differs_marker_required_on_both_legs(self):
        v = [compliant_verdict()]
        v[0]["leg2"]["markers"]["adapter_probe_differs"] = False
        done, _ = H.goal_done(self.goal, v)
        self.assertFalse(done)
        v2 = [compliant_verdict()]
        del v2[0]["leg1"]["markers"]["adapter_probe_differs"]
        done, _ = H.goal_done(self.goal, v2)
        self.assertFalse(done)

    def test_candidates_differ_gate_required_on_both_legs(self):
        # C-9456: the final goal verdict must carry fail-closed
        # candidates-differ evidence on BOTH legs. A leg with recorded
        # UNKNOWN/FAIL candidates-vs-base evidence (e.g. probe could not
        # resolve the artifact) must never retire the goal.
        v = [compliant_verdict()]
        v[0]["candidates_vs_base_gate"]["leg1"]["status"] = "UNKNOWN"
        done, _ = H.goal_done(self.goal, v)
        self.assertFalse(done)
        v2 = [compliant_verdict()]
        v2[0]["candidates_vs_base_gate"]["leg2"] = dict(
            status="FAIL", n_checked=18, n_byte_match=18
        )
        done, _ = H.goal_done(self.goal, v2)
        self.assertFalse(done)
        # A verdict that never recorded the gate fails closed too.
        v3 = [compliant_verdict()]
        del v3[0]["candidates_vs_base_gate"]["leg1"]
        done, _ = H.goal_done(self.goal, v3)
        self.assertFalse(done)

    def test_leg_identity_must_differ(self):
        # Same box AND same runner mechanism is not an independent 2nd leg.
        same = [compliant_verdict()]
        same[0]["leg2"]["runner_mechanism"] = same[0]["leg1"]["runner_mechanism"]
        done, _ = H.goal_done(self.goal, same)
        self.assertFalse(done)
        # No identity on a leg: independence unprovable -> fail closed.
        blind = [compliant_verdict()]
        del blind[0]["leg2"]["runner_mechanism"]
        del blind[0]["leg2"]["box"]
        done, _ = H.goal_done(self.goal, blind)
        self.assertFalse(done)

    def test_per_task_agreement_enforced_between_legs(self):
        disagree = [compliant_verdict()]
        disagree[0]["leg1"]["per_task"] = dict(disagree[0]["per_task"])
        pt2 = dict((k, dict(rec)) for k, rec in disagree[0]["per_task"].items())
        pt2["task_00"] = dict(adapter_pass=False, base_pass=False)
        disagree[0]["leg2"]["per_task"] = pt2
        done, _ = H.goal_done(self.goal, disagree)
        self.assertFalse(done)
        agree = [compliant_verdict()]
        agree[0]["leg1"]["per_task"] = dict(agree[0]["per_task"])
        agree[0]["leg2"]["per_task"] = dict(agree[0]["per_task"])
        done, _ = H.goal_done(self.goal, agree)
        self.assertTrue(done)

    def test_per_task_must_cover_target_and_be_wellformed(self):
        short = [compliant_verdict()]
        del short[0]["per_task"]["task_17"]
        done, _ = H.goal_done(self.goal, short)
        self.assertFalse(done)
        bad = [compliant_verdict()]
        bad[0]["per_task"]["task_00"] = dict(adapter_pass=1, base_pass=False)
        done, _ = H.goal_done(self.goal, bad)
        self.assertFalse(done)


class TestDoneCheckShaPin(unittest.TestCase):
    # C-0031: a verdict retires the goal ONLY when its embedded
    # holdout/scorer sha256 pins match the canonical freeze manifest
    # (5c36b1d). Verdicts banked under a pre-pin scorer (all three in
    # outputs/ predate the pin) fail closed with a NAMED violation.

    def setUp(self):
        self.goal = dict(target_pass="18/18")

    def test_verdict_without_sha_pins_rejected_named(self):
        v = compliant_verdict()
        del v["holdout_sha256"]
        del v["scorer_shas"]
        done, _ = H.goal_done(self.goal, [v])
        self.assertFalse(done)
        self.assertEqual(H.sha_pin_violation(v), "scorer_sha_pins_missing")

    def test_drifted_scorer_sha_rejected_named(self):
        v = compliant_verdict()
        v["scorer_shas"]["harness/beats_base.py"] = "0" * 64
        done, _ = H.goal_done(self.goal, [v])
        self.assertFalse(done)
        self.assertEqual(H.sha_pin_violation(v), "scorer_sha_mismatch:harness/beats_base.py")

    def test_missing_one_scorer_pin_rejected_named(self):
        v = compliant_verdict()
        del v["scorer_shas"]["evals/runner/single_candidate_eval.py"]
        done, _ = H.goal_done(self.goal, [v])
        self.assertFalse(done)
        self.assertEqual(
            H.sha_pin_violation(v), "scorer_sha_pin_missing:evals/runner/single_candidate_eval.py"
        )

    def test_drifted_holdout_sha_rejected_named(self):
        v = compliant_verdict()
        v["holdout_sha256"] = "1" * 64
        done, _ = H.goal_done(self.goal, [v])
        self.assertFalse(done)
        self.assertEqual(H.sha_pin_violation(v), "holdout_sha_mismatch")

    def test_missing_holdout_sha_rejected_named(self):
        v = compliant_verdict()
        del v["holdout_sha256"]
        done, _ = H.goal_done(self.goal, [v])
        self.assertFalse(done)
        self.assertEqual(H.sha_pin_violation(v), "holdout_sha_pin_missing")

    def test_manifest_pins_satisfy_done(self):
        # Control: the pinned composer shape still retires the goal.
        done, f = H.goal_done(self.goal, [compliant_verdict()])
        self.assertTrue(done)
        self.assertEqual(f, "verdict_step000100.json")


class TestState(unittest.TestCase):
    def test_save_json_atomic_and_roundtrip(self):
        d = tempfile.mkdtemp()
        p = os.path.join(d, "x.json")
        H.save_json(p, {"a": 1})
        self.assertEqual(H.load_json(p), {"a": 1})
        self.assertEqual([f for f in os.listdir(d) if f.endswith(".tmp")], [])

    def test_event_append(self):
        d = tempfile.mkdtemp()
        H.event(d, "test_kind", {"x": 1})
        H.event(d, "test_kind", {"x": 2})
        lines = open(os.path.join(d, "EVENTS.jsonl")).read().strip().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertEqual(json.loads(lines[1])["x"], 2)


class TestApiBackoff(unittest.TestCase):
    def test_backoff_trips_after_consecutive_failures(self):
        d = tmp_state()
        ops = H.load_ops(d)
        self.assertFalse(H.backoff_active(ops))
        H.note_spawn_result(d, ops, ok=False)
        self.assertFalse(H.backoff_active(ops))  # 1 failure: no backoff yet
        H.note_spawn_result(d, ops, ok=False)  # 2 consecutive: backoff trips
        self.assertTrue(H.backoff_active(ops))
        self.assertIsNotNone(ops[H.BACKOFF_PATH_KEY])

    def test_success_resets_counter(self):
        d = tmp_state()
        ops = H.load_ops(d)
        H.note_spawn_result(d, ops, ok=False)
        H.note_spawn_result(d, ops, ok=False)
        H.note_spawn_result(d, ops, ok=True)
        self.assertEqual(ops[H.CONSECUTIVE_SPAWN_FAIL_KEY], 0)
        self.assertFalse(H.backoff_active(ops))

    def test_backoff_expires(self):
        ops = {H.BACKOFF_PATH_KEY: "2020-01-01T00:00:00Z", H.CONSECUTIVE_SPAWN_FAIL_KEY: 2}
        self.assertFalse(H.backoff_active(ops))  # past deadline = inactive

    def test_backoff_fails_closed_on_garbage(self):
        ops = {H.BACKOFF_PATH_KEY: "not-a-date"}
        self.assertFalse(H.backoff_active(ops))


class TestRotateLog(unittest.TestCase):
    def test_rotation_moves_oversized_log(self):
        p = os.path.join(tmp_state(), "tick.log")
        with open(p, "w") as f:
            f.write("x" * (6 * 1024 * 1024))
        H.rotate_log(p, max_bytes=5 * 1024 * 1024)
        self.assertLess(os.path.getsize(p), 100)
        self.assertTrue(os.path.exists(p + ".1"))

    def test_rotation_noop_small(self):
        p = os.path.join(tmp_state(), "tick.log")
        with open(p, "w") as f:
            f.write("small")
        H.rotate_log(p)
        self.assertEqual(os.path.getsize(p), 5)
        self.assertFalse(os.path.exists(p + ".1"))


class TestBounceDeadRunningEventsFile(unittest.TestCase):
    """C-9505: bounce_dead_running_cards must write events to EVENTS.jsonl
    (uppercase), not events.jsonl (lowercase). The lowercase path was a
    separate file on case-sensitive filesystems (Linux CI), splitting the
    event log and losing audit trail."""

    def test_bounce_writes_to_canonical_EVENTS_file(self):
        d = tempfile.mkdtemp(prefix="qgh-test-bounce-")
        q = {"cards": [], "seq": 0}
        card = make_card(card_id="C-9505", budget_min=1)
        card["status"] = "running"
        card["claimed_by"] = "99999"
        card["deadline_utc"] = "2020-01-01T00:00:00Z"
        H.add_card(q, card)
        H.save_queue(d, q)
        fleet = {"agents": [{"pid": 99999, "status": "running", "card": "C-9505"}]}
        H.save_fleet(d, fleet)
        bounced = H.bounce_dead_running_cards(d, pid_alive_fn=lambda pid: False)
        self.assertEqual(bounced, ["C-9505"])
        events_path = os.path.join(d, "EVENTS.jsonl")
        self.assertTrue(os.path.exists(events_path), "EVENTS.jsonl must exist")
        lines = open(events_path).read().strip().splitlines()
        kinds = [json.loads(line)["kind"] for line in lines]
        self.assertIn("dead_worker_requeued", kinds)


if __name__ == "__main__":
    unittest.main()
