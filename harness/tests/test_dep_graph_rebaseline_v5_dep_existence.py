"""C-9028: dep-existence guard -- every QUEUE.json card dep must resolve
to an existing card id.

RED (measured 2026-09-17 against the live QUEUE.json): the 2026-09-17
event-log queue recovery rebuilt cards from card_added events only, so
cards that never left a card_added record were silently dropped while
their inbound dep edges survived. Two dangling edges result (full-queue
sweep, 88 cards): C-0016(ready)->C-0002 and C-0029(ready)->C-0042.
harness_lib._deps_satisfied returns False on a missing dep, so a
dangling edge is a SILENT permanent dispatch-block with no signal --
C-0016 sat "ready" while undispatchable.

Fixes, on evidence (smallest change per card):
- C-0016: C-0002 -> C-0051. C-0002 left no card_added record to rebuild
  from; C-0051 (P0 running) owns the C-0002 fire-on-ready mission per
  its own title ("Own C-0002 fire-on-ready: armed watcher fires the
  fail-closed 18-task leg when ASI2 turns ready"), box path per C-0063.
- C-0029: C-0042 bounce, fail-closed, NOT a guess. C-0042 was the
  "user-gated ASI2 console-cure card" (per C-0076 restored acceptance
  citing test_dep_graph_rebaseline.py); it left no durable queue/EVENTS
  record, and neither standup-42 nor EVENTS.jsonl names a live owner --
  C-0076 is explicitly the ASI3 training-container SIBLING, a different
  container. Re-pointing there would satisfy the gate on the wrong
  container cure. So: dep edge removed (it can never resolve), status
  bounced with the evidence in bounce_reason; re-fire is a user
  decision (recreate the ASI2 cure card and re-point, or name the owner).
  bounced is deliberately NOT dead/superseded (v4 live-shell contract)
  and the tdd gate is untouched (v4 training-leg contract).

Same binding idiom as the v1-v4 family: asserted against the LIVE
harness/state/QUEUE.json -- the queue is the source of truth, not a
fixture. The generic invariant is universal (every card, terminal or
not): the v1 "historical deps are a record" allowance governs whether a
terminal dep GATES dispatch, not whether the id exists.
"""

import json
import os
import sys
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
sys.path.insert(0, HARNESS_DIR)

QUEUE_PATH = os.path.join(HARNESS_DIR, "state", "QUEUE.json")

# The two dangling pairs this card was opened for (RED witness).
KNOWN_DANGLING = {("C-0016", "C-0002"), ("C-0029", "C-0042")}


def load_live_queue():
    with open(QUEUE_PATH, encoding="utf-8") as f:
        return json.load(f)


def by_id(queue):
    return {c["id"]: c for c in queue["cards"]}


class TestDepGraphRebaselineV5DepExistence(unittest.TestCase):
    def setUp(self):
        self.assertTrue(os.path.exists(QUEUE_PATH), "QUEUE.json missing at " + QUEUE_PATH)
        self.q = load_live_queue()
        self.cards = by_id(self.q)

    # ------------------------------------------------- generic invariant
    def test_every_card_dep_resolves_to_existing_card(self):
        # THE guard: a dep edge to a card id that does not exist in
        # QUEUE.json can never satisfy _deps_satisfied and can never be
        # repaired by the normal done-transition -- it is a silent
        # permanent block. Universal scope: all cards, all statuses.
        dangling = []
        for c in self.q["cards"]:
            for d in c.get("deps") or []:
                if d not in self.cards:
                    dangling.append((c["id"], c.get("status"), d))
        self.assertEqual(
            dangling,
            [],
            "dangling dep edges (card, status, missing dep): " + repr(dangling),
        )

    def test_known_dangling_pairs_are_gone(self):
        # Names the two measured RED pairs explicitly so a regression
        # that re-introduces either edge is diagnosed, not just counted.
        for cid, dep in KNOWN_DANGLING:
            self.assertNotIn(
                dep,
                self.cards[cid].get("deps") or [],
                cid + " re-acquired dangling dep " + dep,
            )

    # ------------------------------------------------------------- C-0016
    def test_C0016_dep_repointed_to_C9011_canonical_mining(self):
        # C-9028 re-pointed C-0002 -> C-0051 (owner of the C-0002
        # fire-on-ready mission). C-9056 AMENDMENT (2026-09-17,
        # RED-first): C-0051 is itself bounced terminal now ("no RESULT
        # verdict", non-env), so the edge can never reach done and
        # fired dead_dep_escalated every tick (55x thru
        # 2026-09-16T22:03Z). Re-pointed onto C-9011, the canonical
        # failure-mining card feeding C-9052; C-9016 (second leg,
        # different id) untouched. Guard: v7.
        c = self.cards["C-0016"]
        self.assertIn("C-9011", self.cards, "re-point target C-9011 must exist")
        self.assertEqual(
            c.get("deps"),
            ["C-9011"],
            "C-0016 must dep on C-9011 (canonical failure mining)",
        )
        self.assertEqual(c.get("status"), "ready", "C-0016 stays dispatchable")

    # ------------------------------------------------------------- C-0029
    def test_C0029_bounced_failclosed_no_live_owner_for_C0042(self):
        c = self.cards["C-0029"]
        self.assertEqual(
            c.get("status"),
            "bounced",
            "C-0029 must sit bounced fail-closed: no live owner for the C-0042 mission",
        )
        self.assertNotIn("C-0042", c.get("deps") or [], "dangling C-0042 edge must be gone")
        self.assertNotIn(
            c.get("status"),
            ("dead", "superseded"),
            "bounce is recoverable, not terminal (v4 live-shell contract)",
        )
        reason = c.get("bounce_reason") or ""
        self.assertIn("C-0042", reason, "bounce_reason must cite the unresolvable dep")
        self.assertIn("fail-closed", reason.lower(), "bounce_reason must cite the fail-closed call")
        self.assertIn(
            "INFEASIBLE",
            c.get("reason") or "",
            "historical C-0065 un-retire reason must survive the bounce",
        )


if __name__ == "__main__":
    unittest.main()
