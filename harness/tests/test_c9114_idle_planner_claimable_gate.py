# C-9114 idle-planner trigger regression:
#
# On 2026-09-18T05:50Z the idle-planner minted C-9111 while standup #342
# showed 25 ready + 6 running cards (EVENTS.jsonl: every auto_plan from
# 04:23Z to 05:50Z -- C-9083/C-9088/C-9092/C-9096/C-9100/C-9104/C-9111 --
# is paired with dead_dep_escalated blockers ["C-9029"]). The dead-dep
# escalation path called _auto_plan UNGATED: one terminally dead blocker
# re-minted a planner card every tick while the board held plenty of
# claimable ready work; three planner legs (C-9100/C-9104/C-9111) burned
# in 20 min re-inspecting the same full queue.
#
# Claimable ready = status "ready" AND no dep whose status is dead/bounced
# (a running or done dep is work in flight/complete, not idleness; only a
# TERMINAL dep means the card can never become work). The trigger must
# skip the mint while claimable ready > 0, and keep minting when the board
# is genuinely empty or every ready card is terminally blocked (the
# C-0021 doctrine pinned by tests/test_qgh_dispatch_integrity.py).

import json
import os
import sys
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
sys.path.insert(0, HARNESS_DIR)
import harness_lib as H  # noqa: E402
import qgh  # noqa: E402


def card(title, lane="fixer", deps=None, **kw):
    kw.setdefault("why", "goal edge")
    kw.setdefault("acceptance", ["acceptance criteria"])
    return H.new_card(title=title, lane=lane, deps=deps or [], **kw)


class TestC9114ClaimableReadyGate(unittest.TestCase):
    def setUp(self):
        for sub in ("agents", "briefs", "locks", "standup", "probes"):
            os.makedirs(os.path.join(qgh.STATE, sub), exist_ok=True)
        # per-test event isolation: _events() reads the whole jsonl
        ev = os.path.join(qgh.STATE, "EVENTS.jsonl")
        if os.path.exists(ev):
            os.remove(ev)
        qgh.save_json(os.path.join(qgh.STATE, "QUEUE.json"), {"cards": [], "seq": 0})
        qgh.save_json(os.path.join(qgh.STATE, "FLEET.json"), {"agents": []})
        qgh.save_json(
            os.path.join(qgh.STATE, "OPS.json"),
            {"consecutive_spawn_failures": 0, "backoff_until_utc": None},
        )

    def _planners(self):
        q = qgh.load_queue(qgh.STATE)
        return [c for c in q["cards"] if c["lane"] == "planner" and c["status"] == "ready"]

    def _events(self):
        path = os.path.join(qgh.STATE, "EVENTS.jsonl")
        with open(path, encoding="utf-8") as f:
            return [json.loads(ln) for ln in f if ln.strip()]

    def _dead_blocker_plus_child(self, q):
        # The live C-9029 shape: a terminally dead card whose ready child
        # re-escalates it every tick (dead_dep_escalated -> _auto_plan).
        blocker = H.add_card(q, card("hopeless blocker"))
        blocker["status"] = "dead"
        blocker["bounce_reason"] = "genuine failure 3 strikes"
        H.add_card(q, card("dead-blocked child", deps=[blocker["id"]]))
        return blocker

    def test_nonempty_board_with_claimable_ready_skips_dead_dep_mint(self):
        # THE C-9111 incident: dead blocker C-9029 escalated every tick while
        # standup #342 held 25 ready cards. A board with 1+ claimable ready
        # card is NOT idle; the escalation must not mint a planner card.
        q = qgh.load_queue(qgh.STATE)
        self._dead_blocker_plus_child(q)
        H.add_card(q, card("healthy claimable work"))  # standup #342 ready mass
        qgh.save_queue(qgh.STATE, q)

        qgh._reconcile_dep_blockers()

        self.assertEqual(
            len(self._planners()),
            0,
            "idle-planner minted while claimable ready work existed (C-9111)",
        )
        esc = [e for e in self._events() if e["kind"] == "dead_dep_escalated"]
        self.assertEqual(len(esc), 1, "escalation must stay auditable")
        self.assertFalse(esc[0].get("minted"), "skip must be recorded as minted=false")

    def test_dead_dep_with_zero_claimable_still_mints(self):
        # Positive control (C-0021 doctrine): a dead blocker with NO other
        # claimable ready work is a genuine management failure -> mint.
        # AMENDED 2026-09-18 (C-9056/v7 edge-drop self-heal): the original
        # fixture paired the dead blocker with a dep-blocked child, but the
        # reconciler now DROPS the never-done edge (audited dep_edge_dropped)
        # -- the child becomes claimable work, so that board is NOT idle and
        # must NOT mint (pinned by tests/test_dep_edge_drop.py). The zero-
        # claimable control is therefore the bare dead blocker, no dependents.
        q = qgh.load_queue(qgh.STATE)
        blocker = H.add_card(q, card("hopeless blocker"))
        blocker["status"] = "dead"
        blocker["bounce_reason"] = "genuine failure 3 strikes"
        qgh.save_queue(qgh.STATE, q)

        qgh._reconcile_dep_blockers()

        # AMENDED 2026-09-18 (continued): a bare dead blocker (no ready
        # dependent) never triggered the reconciler-internal mint even
        # before the edge-drop self-heal (measured: changed=False,
        # dead=[]); the C-0021 idle-mint duty is enforced by the tick's
        # top-up gate (cmd_tick: planner_topup_needed + no planner
        # running -> _auto_plan). Assert the doctrine through that
        # production predicate end-to-end.
        queue = qgh.load_queue(qgh.STATE)
        self.assertTrue(
            qgh.planner_topup_needed(queue),
            "dead blocker with zero claimable ready is genuinely idle -> tick must mint",
        )
        if qgh.planner_topup_needed(queue) and qgh.running_count(queue, "planner") == 0:
            qgh._auto_plan(qgh.load_goal(qgh.STATE))
        self.assertEqual(
            len(self._planners()),
            1,
            "the tick's mint path must re-decompose a genuinely idle board",
        )

    def test_claimable_ready_count_reads_queue_cards(self):
        # The count basis reads QUEUE.json cards field (dict-format cards):
        # running deps and done deps are claimable; dead/bounced deps are not.
        q = qgh.load_queue(qgh.STATE)
        running = H.add_card(q, card("running dep"))
        running["status"] = "running"
        dead = H.add_card(q, card("dead dep card"))
        dead["status"] = "dead"
        H.add_card(q, card("free work"))  # no deps: claimable
        H.add_card(q, card("waits on running", deps=[running["id"]]))  # claimable
        H.add_card(q, card("waits on dead", deps=[dead["id"]]))  # NOT claimable
        qgh.save_queue(qgh.STATE, q)

        queue = qgh.load_queue(qgh.STATE)
        self.assertEqual(qgh.claimable_ready_count(queue), 2)

    def test_topup_gate_skips_when_claimable_ready_exists(self):
        # The gated top-up path must honor the same >0 predicate: one healthy
        # ready card means the queue is not idle (old min_ready=2 minted on 1).
        q = qgh.load_queue(qgh.STATE)
        H.add_card(q, card("healthy claimable work"))
        qgh.save_queue(qgh.STATE, q)
        queue = qgh.load_queue(qgh.STATE)
        self.assertFalse(
            qgh.planner_topup_needed(queue),
            "1+ claimable ready card on the board: not idle, no top-up",
        )
        # both-states evidence: empty queue still triggers, dead-dep-only too
        self.assertTrue(qgh.planner_topup_needed({"cards": [], "seq": 0}))
        dead_q = {"cards": [], "seq": 0}  # fresh board: ONLY the dead-blocked pair
        d = H.add_card(dead_q, card("dead dep card"))
        d["status"] = "dead"
        H.add_card(dead_q, card("blocked forever", deps=[d["id"]]))
        self.assertTrue(
            qgh.planner_topup_needed(dead_q),
            "only terminally-blocked ready cards left: that IS idle, must mint",
        )


if __name__ == "__main__":
    unittest.main()
