# C-9056 lineage / v7-guard self-healing: the reconciler must RESOLVE a
# never-done dep edge, not merely re-escalate it every tick.
#
# Live precondition (measured 2026-09-18 ~08:30Z, v7 guard RED):
# C-9091->C-9069, C-9106->C-9102, C-9010->C-9099 -- ready cards depending
# on bounced non-environmental cards. _reconcile_dep_blockers re-arms env
# bounces and LISTS the rest in dead_dep_escalated (55+ events, the
# C-9056 measurement) but never resolves the edge: the dependent stays
# undispatchable forever and the v7 live guard stays red until a human
# re-baseline (v1..v7) re-points it by hand. This file pins the
# self-healing arm: drop the stale edge (audited), keep the escalation
# event, and keep the C-9114 idle-mint gate honest under the resulting
# claimability.

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


class TestDepEdgeDropSelfHeal(unittest.TestCase):
    def setUp(self):
        for sub in ("agents", "briefs", "locks", "standup", "probes"):
            os.makedirs(os.path.join(qgh.STATE, sub), exist_ok=True)
        ev = os.path.join(qgh.STATE, "EVENTS.jsonl")
        if os.path.exists(ev):
            os.remove(ev)
        qgh.save_json(os.path.join(qgh.STATE, "QUEUE.json"), {"cards": [], "seq": 0})
        qgh.save_json(os.path.join(qgh.STATE, "FLEET.json"), {"agents": []})
        qgh.save_json(
            os.path.join(qgh.STATE, "OPS.json"),
            {"consecutive_spawn_failures": 0, "backoff_until_utc": None},
        )

    def _events(self):
        path = os.path.join(qgh.STATE, "EVENTS.jsonl")
        with open(path, encoding="utf-8") as f:
            return [json.loads(ln) for ln in f if ln.strip()]

    def _queue(self):
        return qgh.load_queue(qgh.STATE)

    def test_bounced_nonenv_dep_edge_dropped_and_dependent_dispatchable(self):
        # THE live v7 violation class: ready child -> bounced non-env card.
        q = self._queue()
        blocker = H.add_card(q, card("hopeless blocker"))
        blocker["status"] = "bounced"
        blocker["bounce_reason"] = "genuine failure 3 strikes"
        child = H.add_card(q, card("decision brief", deps=[blocker["id"]]))
        qgh.save_queue(qgh.STATE, q)

        qgh._reconcile_dep_blockers()

        q = self._queue()
        child = qgh.find_card(q, child["id"])
        blocker = qgh.find_card(q, blocker["id"])
        self.assertEqual(
            child["deps"], [], "stale never-done edge must be dropped, not re-escalated forever"
        )
        self.assertEqual(
            blocker["status"], "bounced", "the bounced card itself is a record; do not dead it"
        )
        ids = [c["id"] for c in H.ready_cards(q)]
        self.assertIn(child["id"], ids, "dependent must become dispatchable after the edge drop")
        drops = [e for e in self._events() if e["kind"] == "dep_edge_dropped"]
        self.assertEqual(len(drops), 1, "the drop must be audited exactly once")
        self.assertEqual(drops[0]["blocker"], blocker["id"])
        self.assertEqual(drops[0]["unblocks"], child["id"])

    def test_env_bounced_dep_still_requeued_edge_kept(self):
        # Existing C-9056 arm preserved: an ENV bounce re-arms the blocker
        # and the edge stays (the blocker can still reach done).
        q = self._queue()
        blocker = H.add_card(q, card("flaky blocker"))
        blocker["status"] = "bounced"
        blocker["bounce_count"] = 2
        blocker["bounce_reason"] = "api error 503 transport"
        child = H.add_card(q, card("downstream card", deps=[blocker["id"]]))
        qgh.save_queue(qgh.STATE, q)

        qgh._reconcile_dep_blockers()

        q = self._queue()
        child = qgh.find_card(q, child["id"])
        blocker = qgh.find_card(q, blocker["id"])
        self.assertEqual(child["deps"], [blocker["id"]], "env-bounced edge must be kept")
        self.assertEqual(blocker["status"], "ready", "env bounce must re-arm the blocker")
        self.assertEqual(blocker["bounce_count"], 0, "re-arm resets strikes")
        self.assertFalse(
            [e for e in self._events() if e["kind"] == "dep_edge_dropped"],
            "no edge-drop event on the env arm",
        )

    def test_dead_dep_edge_dropped_and_escalation_still_audited(self):
        # Dead blockers: edge dropped AND the C-9114 escalation event kept.
        q = self._queue()
        blocker = H.add_card(q, card("hopeless blocker"))
        blocker["status"] = "dead"
        blocker["bounce_reason"] = "genuine failure 3 strikes"
        child = H.add_card(q, card("recovery owner", deps=[blocker["id"]]))
        qgh.save_queue(qgh.STATE, q)

        qgh._reconcile_dep_blockers()

        q = self._queue()
        child = qgh.find_card(q, child["id"])
        self.assertEqual(child["deps"], [])
        esc = [e for e in self._events() if e["kind"] == "dead_dep_escalated"]
        self.assertEqual(len(esc), 1, "escalation stays auditable")
        self.assertEqual(esc[0]["blockers"], [blocker["id"]])

    def test_partial_deps_drop_only_the_terminal_edge(self):
        q = self._queue()
        good = H.add_card(q, card("done dep"))
        good["status"] = "done"
        bad = H.add_card(q, card("hopeless blocker"))
        bad["status"] = "bounced"
        bad["bounce_reason"] = "genuine failure 3 strikes"
        child = H.add_card(q, card("mixed card", deps=[good["id"], bad["id"]]))
        qgh.save_queue(qgh.STATE, q)

        qgh._reconcile_dep_blockers()

        q = self._queue()
        child = qgh.find_card(q, child["id"])
        self.assertEqual(child["deps"], [good["id"]], "only the never-done edge may be dropped")

    def test_edge_drop_keeps_c9114_idle_mint_gate_honest(self):
        # After the drop the dependent is claimable, so a board holding a
        # dead-blocked pair is NOT idle (no planner mint -- the C-9111
        # class). A dead blocker with NO dependents still is (C-0021).
        q = self._queue()
        blocker = H.add_card(q, card("hopeless blocker"))
        blocker["status"] = "dead"
        blocker["bounce_reason"] = "genuine failure 3 strikes"
        H.add_card(q, card("recovery owner", deps=[blocker["id"]]))
        qgh.save_queue(qgh.STATE, q)

        qgh._reconcile_dep_blockers()

        planners = [
            c for c in self._queue()["cards"] if c["lane"] == "planner" and c["status"] == "ready"
        ]
        self.assertEqual(len(planners), 0, "unblocked dependent is claimable work: no idle mint")

        # positive control: the same dead blocker with no dependents.
        # The reconciler itself never minted on a bare dead blocker
        # (measured 2026-09-18: changed=False, dead=[]); genuinely-idle
        # minting is the TICK's top-up gate (C-0021), so assert the
        # doctrine through that production predicate: the board IS idle.
        ev = os.path.join(qgh.STATE, "EVENTS.jsonl")
        if os.path.exists(ev):
            os.remove(ev)
        # Clear the queue to ONLY the dead blocker: use save_json directly
        # to bypass the save_queue merge (which would resurrect the
        # unblocked recovery owner from disk).
        qgh.save_json(
            os.path.join(qgh.STATE, "QUEUE.json"),
            {"cards": [dict(blocker, deps=[])], "seq": 1},
        )

        qgh._reconcile_dep_blockers()

        self.assertTrue(
            qgh.planner_topup_needed(self._queue()),
            "terminal blocker with no dependents and nothing claimable is genuinely idle",
        )


if __name__ == "__main__":
    unittest.main()
