"""C-0068: dep re-baseline v2 -- re-point C-0052/C-0056/C-0061 from the
twice-refuted C-0047 onto C-0063 (ready P0 Mac-local eval path).

RED (measured 2026-09-17 against the live QUEUE.json): C-0047 closed
REFUTED-REVERIFIED twice (harness/state/probes/C-0047-r2-reprobe.json:
zero of five endpoint classes provide the POST /exec transport) yet
C-0052 (beats_base anchor, done-criterion 1), C-0056 (independent
second leg, criterion 3) and C-0061 (deadlock USER package) still dep
on it. _deps_satisfied passes ONLY on dep status=="done", and C-0047 is
bounced/terminal, so each dependent idles undispatchable forever. The
fix re-points those edges onto C-0063, whose acceptance hands the
planner the re-point. C-0047 itself is NEVER deleted: ids stay
addressable in the ledger.

Same binding idiom as test_dep_graph_rebaseline.py (C-0060/C-0065):
these tests assert the graph invariant against the LIVE
harness/state/QUEUE.json -- the queue is the source of truth, not a
fixture. Event assertions bind to the live EVENTS.jsonl, which is
append-only (rotate_log only ever touches tick.log).
"""

import json
import os
import sys
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
sys.path.insert(0, HARNESS_DIR)

QUEUE_PATH = os.path.join(HARNESS_DIR, "state", "QUEUE.json")
EVENTS_PATH = os.path.join(HARNESS_DIR, "state", "EVENTS.jsonl")

# The twice-refuted endpoint-driven transport. Never a re-point target;
# no dispatchable card may dep on it.
REFUTED_TRANSPORT = "C-0047"
NEW_TARGET = "C-0063"
REPOINTED = ("C-0052", "C-0056", "C-0061")
PROBE_REF = "C-0047-r2-reprobe.json"


def load_live_queue():
    with open(QUEUE_PATH, encoding="utf-8") as f:
        return json.load(f)


def by_id(queue):
    out = dict()
    for c in queue["cards"]:
        out[c["id"]] = c
    return out


class TestDepGraphRebaselineV2(unittest.TestCase):
    def setUp(self):
        _existing = set(c["id"] for c in load_live_queue().get("cards", []))
        _required = {'C-0047', 'C-0052', 'C-0053', 'C-0056', 'C-0060', 'C-0061', 'C-0063', 'C-0065', 'C-0068'}
        _missing = _required - _existing
        if _missing:
            self.skipTest("historical cards purged: " + str(sorted(_missing)[:5]))
        self.assertTrue(os.path.exists(QUEUE_PATH), "QUEUE.json missing at " + QUEUE_PATH)
        self.q = load_live_queue()
        self.cards = by_id(self.q)

    def test_all_touched_ids_still_exist(self):
        # never delete: C-0047 stays addressable in the ledger
        for cid in ("C-0047", "C-0052", "C-0053", "C-0056", "C-0061", "C-0063"):
            self.assertIn(cid, self.cards, f"card {cid} vanished from QUEUE.json")

    def test_repoint_target_is_not_a_refuted_card(self):
        # never re-point onto a refuted path: C-0063 must exist and not
        # be closed refuted at execution time
        status = self.cards[NEW_TARGET]["status"]
        self.assertNotEqual(
            status, "refuted", "C-0063 closed refuted: cards must be BLOCKED, not re-pointed"
        )

    def test_C0052_dep_C0063_not_C0047(self):
        c = self.cards["C-0052"]
        self.assertNotIn(REFUTED_TRANSPORT, c["deps"])
        self.assertEqual(c["deps"], [NEW_TARGET])

    def test_C0056_dep_C0063_not_C0047(self):
        c = self.cards["C-0056"]
        self.assertNotIn(REFUTED_TRANSPORT, c["deps"])
        self.assertEqual(c["deps"], [NEW_TARGET])

    def test_C0061_repoints_C0047_keeps_C0053(self):
        # C-0053 was still running at execution time: that edge stays;
        # only the refuted C-0047 edge re-points.
        c = self.cards["C-0061"]
        self.assertNotIn(REFUTED_TRANSPORT, c["deps"])
        self.assertEqual(c["deps"], [NEW_TARGET, "C-0053"])

    def test_no_dispatchable_card_deps_on_refuted_transport(self):
        # live-graph invariant: a dispatchable card (ready/running) must
        # never dep on the bounced C-0047 -- _deps_satisfied only passes
        # on done, so such an edge parks the card undispatchable forever.
        for c in self.q["cards"]:
            if c.get("status") not in ("ready", "running"):
                continue
            self.assertNotIn(
                REFUTED_TRANSPORT,
                c.get("deps") or [],
                "dispatchable card {} deps on twice-refuted {}".format(c["id"], REFUTED_TRANSPORT),
            )

    def test_one_line_note_cites_refutation_probe(self):
        # card text untouched beyond the dep pointer + a one-line note
        # citing the measured refutation
        for cid in REPOINTED:
            note = self.cards[cid].get("note") or ""
            self.assertIn(PROBE_REF, note, f"card {cid} note must cite {PROBE_REF}")


class TestDepRepointedEvents(unittest.TestCase):
    def setUp(self):
        _existing = set(c["id"] for c in load_live_queue().get("cards", []))
        _required = {"C-0047", "C-0052", "C-0056", "C-0061", "C-0063"}
        _missing = _required - _existing
        if _missing:
            self.skipTest("historical cards purged: " + str(sorted(_missing)[:5]))
        self.assertTrue(os.path.exists(EVENTS_PATH), "EVENTS.jsonl missing at " + EVENTS_PATH)

    def test_dep_repointed_events_landed_for_all_three(self):
        got = dict()
        with open(EVENTS_PATH, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                if (
                    e.get("kind") == "dep_repointed"
                    and e.get("dep_from") == REFUTED_TRANSPORT
                    and e.get("dep_to") == NEW_TARGET
                ):
                    got[e.get("card")] = e
        for cid in REPOINTED:
            self.assertIn(
                cid, got, f"no dep_repointed event for {cid} ({REFUTED_TRANSPORT}->{NEW_TARGET})"
            )
            self.assertEqual(
                got[cid].get("by"), "C-0068", f"re-point event for {cid} must name C-0068"
            )


if __name__ == "__main__":
    unittest.main()
