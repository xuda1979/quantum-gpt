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
    base = dict(title="t", lane="fixer", why="w", acceptance=["a"])
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
        c = make_card(acceptance=["a1", "a2"], gates=["tdd"], budget_min=25)
        b = H.compose_brief(goal, c, dep_results=[])
        n = len(b.splitlines())
        self.assertLessEqual(n, H.BRIEF_MAX_LINES)
        self.assertIn("RESULT:", b)
        self.assertIn("ACCEPTANCE", b)
        self.assertIn("RED test first", b)
        self.assertIn("25 min", b)


class TestDoneCheck(unittest.TestCase):
    def test_done_requires_18_of_18_and_beats_base(self):
        goal = {"target_pass": "18/18"}
        v = [{"pass_adapter": "3/18", "beats_base": True, "_file": "a.json"}]
        done, _ = H.goal_done(goal, v)
        self.assertFalse(done)
        v2 = [{"pass_adapter": "18/18", "beats_base": True, "_file": "b.json"}]
        done, f = H.goal_done(goal, v2)
        self.assertTrue(done)
        self.assertEqual(f, "b.json")
        v3 = [{"pass_adapter": "18/18", "beats_base": False, "_file": "c.json"}]
        done, _ = H.goal_done(goal, v3)
        self.assertFalse(done)

    def test_done_fails_closed_on_empty(self):
        done, _ = H.goal_done({"target_pass": "18/18"}, [])
        self.assertFalse(done)


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


if __name__ == "__main__":
    unittest.main()


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
