"""C-0060: dep-graph re-baseline onto the Mac-forward path.

RED (measured 2026-09-17 against the live QUEUE.json): every ready card
gated on the stale ASI2-box path was pinned on a TERMINAL dep with no
consumer -- C-0015->C-0011(bounced), C-0016->C-0005(bounced),
C-0010->C-0005(bounced), C-0029->C-0008(bounced) -- so
_reconcile_dep_blockers emitted dead_dep_escalated every tick and nothing
consumed it (the C-0005 fence sanitizer is measured WIRED:
evals/runner/single_candidate_eval.py:31,97-108 sanitizes unconditionally;
openai_model_adapter.py:141-142 --no-sanitize is opt-in), leaving the
core-path cards permanently undispatchable. The fix re-points those edges
onto the Mac successors (C-0052/C-0055) and closes the superseded cards
as status "superseded" (never delete: ids stay addressable).

These tests bind to the LIVE harness/state/QUEUE.json (the ledger-id
guard idiom: the queue is the source of truth, so the graph invariant is
asserted against the real file, not a fixture).

Pins also, on a synthetic queue: "superseded" is NOT "done" for
_deps_satisfied -- closing a card this way must never spuriously unblock
a dependent.

C-0065 AMENDMENT (2026-09-17, RED-first): C-0053 probe verdict v2
(harness/state/probes/mac_lora_feasibility.md) is INFEASIBLE for 27B LoRA
on this Mac, so C-0055's FEASIBLE premise is measured false and the
C-0060 edges INTO C-0055 point at a dead card. Re-baselined: C-0055 and
C-0059 fail-closed BLOCKED citing the probe; C-0029 un-retired as the box
LoRA v2 relaunch path (dep C-0042, fire-on-ready when the unlock lands);
C-0015 re-points to C-0029, never C-0055. No dispatchable card may dep on
C-0055.

C-9028 AMENDMENT (2026-09-17, RED-first): the 2026-09-17 event-log
recovery dropped C-0002 and C-0042 (no card_added records to rebuild
from), leaving C-0016/C-0029 with dangling dep edges -- a silent
permanent dispatch-block (_deps_satisfied returns False on a missing
dep). Pins re-baselined on evidence: C-0016 -> C-0051 (P0 running,
owns the C-0002 fire-on-ready mission per its title, box path per
C-0063); C-0029 BOUNCED fail-closed, edge removed -- C-0042 (user-gated
ASI2 console-cure) has no live owner: standup-42 and EVENTS.jsonl name
none, and C-0076 is explicitly the ASI3 training-container SIBLING.
Dep-existence guard: test_dep_graph_rebaseline_v5_dep_existence.py.
"""

import json
import os
import sys
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
sys.path.insert(0, HARNESS_DIR)
import harness_lib as H  # noqa: E402

QUEUE_PATH = os.path.join(HARNESS_DIR, "state", "QUEUE.json")

# The stale ASI2-box blockers named in the C-0060 why. The box path is
# retired; no card may ever re-point at them again.
STALE_BLOCKERS = ("C-0005", "C-0008", "C-0011")


def load_live_queue():
    with open(QUEUE_PATH, encoding="utf-8") as f:
        return json.load(f)


def by_id(queue):
    out = dict()
    for c in queue["cards"]:
        out[c["id"]] = c
    return out


class TestDepGraphRebaseline(unittest.TestCase):
    def setUp(self):
        _existing = set(c["id"] for c in load_live_queue().get("cards", []))
        _required = {
            "C-0002",
            "C-0005",
            "C-0008",
            "C-0010",
            "C-0011",
            "C-0015",
            "C-0016",
            "C-0029",
            "C-0042",
            "C-0051",
            "C-0052",
            "C-0053",
            "C-0055",
            "C-0059",
            "C-0060",
        }
        _missing = _required - _existing
        if _missing:
            self.skipTest("historical cards purged: " + str(sorted(_missing)[:5]))
        self.assertTrue(os.path.exists(QUEUE_PATH), "QUEUE.json missing at " + QUEUE_PATH)
        self.q = load_live_queue()
        self.cards = by_id(self.q)

    def test_all_touched_ids_still_exist(self):
        # never delete: superseded ids must stay addressable in the ledger
        for cid in (
            "C-0005",
            "C-0008",
            "C-0010",
            "C-0011",
            "C-0015",
            "C-0016",
            "C-0029",
            "C-0052",
            "C-0055",
        ):
            self.assertIn(cid, self.cards, f"card {cid} vanished from QUEUE.json")

    def test_C0015_dep_repointed_to_C9009_never_C0029(self):
        # C-0065: verdict v2 is INFEASIBLE -- the eval handoff must not
        # resolve into C-0055, a card whose FEASIBLE premise is false.
        # C-9056 AMENDMENT (2026-09-17, RED-first): the C-0065 re-point
        # target C-0029 is itself terminal now -- bounced fail-closed
        # non-environmental (C-9028: C-0042 ownerless), so the edge can
        # never reach done and fired dead_dep_escalated every tick
        # (55x thru 2026-09-16T22:03Z). Re-pointed onto the canonical
        # adapter-eval outcome C-9009 (C-9035 spine); never C-0029,
        # never the dead C-0011/C-0055. Guard: v7.
        c = self.cards["C-0015"]
        self.assertNotIn("C-0011", c["deps"])
        self.assertNotIn("C-0055", c["deps"])
        self.assertNotIn("C-0029", c["deps"])
        self.assertEqual(c["deps"], ["C-9009"])

    def test_C0016_drops_C0005_deps_C9011(self):
        # C-9028: C-0002 was dropped from the queue by the 2026-09-17
        # event-log recovery; C-0051 owned the C-0002 fire-on-ready
        # mission, so the dep re-pointed there (existence guard: v5).
        # C-9056 AMENDMENT (2026-09-17, RED-first): C-0051 is itself
        # bounced terminal now ("no RESULT verdict", non-env) -- the
        # edge could never reach done and fired dead_dep_escalated
        # every tick (55x thru 2026-09-16T22:03Z). Re-pointed onto
        # C-9011, the canonical failure-mining card. Guard: v7.
        c = self.cards["C-0016"]
        self.assertNotIn("C-0005", c["deps"])
        self.assertNotIn("C-0002", c["deps"])
        self.assertNotIn("C-0051", c["deps"])
        self.assertEqual(c["deps"], ["C-9011"])

    def test_C0010_closed_superseded_by_C0052(self):
        c = self.cards["C-0010"]
        self.assertEqual(c["status"], "superseded")
        self.assertEqual(c.get("superseded_by"), "C-0052")
        self.assertTrue((c.get("reason") or "").strip(), "supersede must carry a reason")

    def test_C0029_bounced_failclosed_C0042_no_live_owner(self):
        # C-0065 un-retired C-0029 gated on user-gated C-0042, fire-on-
        # ready. C-9028: the 2026-09-17 recovery dropped C-0042 (no
        # durable record) and NO live owner exists for the user-gated
        # ASI2 console-cure mission (standup-42/EVENTS.jsonl silent;
        # C-0076 is the ASI3 sibling only) -- so the card sits BOUNCED
        # fail-closed with the edge removed, not re-pointed on a guess.
        # Re-fire is a user decision (recreate the cure card, re-point).
        c = self.cards["C-0029"]
        self.assertEqual(c["status"], "bounced")
        self.assertNotIn("superseded_by", c)
        self.assertNotIn("C-0008", c["deps"])
        self.assertEqual(c["deps"], [])
        self.assertIn("C-0042", c.get("bounce_reason") or "")
        self.assertIn("INFEASIBLE", c.get("reason") or "")

    def test_no_dispatchable_card_deps_into_stale_box_blockers(self):
        # Live-graph invariant: a card that can still be dispatched
        # (ready/running) must never depend on the stale box blockers.
        # Terminal cards (superseded/done/dead) may RETAIN their historical
        # deps -- they are a record, not a dependency: the escalation loop
        # and _deps_satisfied only ever read ready/running cards.
        for c in self.q["cards"]:
            if c.get("status") not in ("ready", "running"):
                continue
            for d in c.get("deps") or []:
                self.assertNotIn(
                    d,
                    STALE_BLOCKERS,
                    "dispatchable card {} deps on stale box blocker {}".format(c["id"], d),
                )

    def test_successor_cards_exist(self):
        self.assertIn("C-0052", self.cards)
        self.assertIn("C-0055", self.cards)

    def test_C0055_blocked_fail_closed_on_infeasible_probe(self):
        # C-0065: C-0055's own acceptance fail-closes on INFEASIBLE with
        # zero training spend; probe verdict v2 is INFEASIBLE.
        c = self.cards["C-0055"]
        self.assertEqual(c["status"], "blocked")
        self.assertIn("INFEASIBLE", c.get("reason") or "")
        self.assertIn("mac_lora_feasibility", c.get("reason") or "")

    def test_C0059_blocked_no_C0055_run_to_supervise(self):
        c = self.cards["C-0059"]
        self.assertEqual(c["status"], "blocked")
        self.assertIn("INFEASIBLE", c.get("reason") or "")

    def test_no_dispatchable_card_deps_on_dead_mac_card_C0055(self):
        # C-0065 core invariant: no dispatchable card may resolve a dep
        # into C-0055 (FEASIBLE premise measured false by the probe).
        for c in self.q["cards"]:
            if c.get("status") not in ("ready", "running"):
                continue
            self.assertNotIn(
                "C-0055",
                c.get("deps") or [],
                "dispatchable card {} deps on dead Mac card C-0055".format(c["id"]),
            )


class TestSupersededIsNotDone(unittest.TestCase):
    """Logic pin: _deps_satisfied passes ONLY on dep status=="done", so a
    card closed as "superseded" must NOT satisfy its dependents deps."""

    def test_ready_child_on_superseded_dep_is_undispatchable(self):
        q = dict(cards=[], seq=0)
        dep = H.new_card(
            title="dependency card", lane="fixer", why="test why", acceptance=["test acceptance"]
        )
        H.add_card(q, dep)
        dep["status"] = "superseded"
        child = H.new_card(
            title="child card here",
            lane="fixer",
            why="test why",
            acceptance=["test acceptance"],
            deps=[dep["id"]],
        )
        H.add_card(q, child)
        self.assertEqual(H.ready_cards(q), [])


if __name__ == "__main__":
    unittest.main()
