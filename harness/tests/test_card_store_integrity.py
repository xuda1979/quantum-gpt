# C-9027 card-store integrity regressions:
#
# 1. Duplicate decompose mints: on 2026-09-16 20:00-20:05Z the auto-planner
#    minted TWO open decompose-class cards whose stale-seq ids collided with
#    live cards (EVENTS: auto_plan C-9020 + auto_plan C-9021, then
#    dispatch_refused churn). Minting a second open decompose-class card
#    while one is open must be refused.
# 2. Live-id content mutation: standup-27 recorded C-9021 as
#    planner/"Queue nearly empty..." while QUEUE.json ended with
#    fixer/"Split /health-ready..." under the same id. No writer may mutate
#    title/lane of an existing card id; new intent requires a new id.
# 3. Queue-empty trigger auditability: the auto_plan event must record its
#    count basis (ready count + unblocked count; ts is already stamped) so a
#    misfire is auditable from EVENTS.jsonl alone.
#
# Runs against throwaway state only; the live QUEUE.json is never touched.

import json
import os
import sys
import tempfile
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
sys.path.insert(0, HARNESS_DIR)
import harness_lib as H  # noqa: E402
import qgh  # noqa: E402

DECOMPOSE_TITLE = "Queue nearly empty: decompose next objective steps"


def mk(title=DECOMPOSE_TITLE, lane="planner", **kw):
    kw.setdefault("why", "goal edge")
    kw.setdefault("acceptance", ["acceptance criteria"])
    return H.new_card(title=title, lane=lane, **kw)


def fresh_queue():
    return dict(cards=[], seq=0)


class TestDecomposeMintDedupe(unittest.TestCase):
    def test_second_open_decompose_card_refused(self):
        q = fresh_queue()
        H.add_card(q, mk())  # first open decompose-class card
        try:
            H.add_card(q, mk())  # the C-9021/C-9023 double mint
        except ValueError:
            return
        self.fail("second open decompose-class card was minted, not refused")

    def test_refusal_is_class_scoped_not_lane_scoped(self):
        # the incident card mutated lane planner->fixer; a lane-keyed guard
        # would not have caught it. Title class is the dedupe marker.
        q = fresh_queue()
        H.add_card(q, mk(lane="planner"))
        try:
            H.add_card(q, mk(lane="fixer"))
        except ValueError:
            return
        self.fail("decompose-class mint in another lane was not refused")

    def test_mint_allowed_once_open_card_closes(self):
        q = fresh_queue()
        c1 = H.add_card(q, mk())
        c1["status"] = "done"
        H.add_card(q, mk())  # no OPEN decompose card left: allowed
        self.assertEqual(len(q["cards"]), 2)

    def test_non_decompose_titles_not_deduped(self):
        q = fresh_queue()
        H.add_card(q, mk(title="Split /health-ready from /exec-alive", lane="fixer"))
        H.add_card(q, mk(title="Split /health-ready from /exec-alive: box probes", lane="fixer"))
        self.assertEqual(len(q["cards"]), 2)

    def test_stale_seq_id_collision_bumps_to_free_id(self):
        # the 20:00:01Z incident state: on-disk seq lags the live cards (a
        # lost update left seq=9020 while C-9021 existed) and the next mint
        # collided into the live id. add_card must bump to a free id.
        q = fresh_queue()
        existing = mk(title="live card", lane="fixer")
        existing["id"] = "C-9021"
        q["cards"].append(existing)
        q["seq"] = 9020
        fresh = H.add_card(q, mk(title="late mint", lane="planner"))  # seq->9021 collides
        ids = [c["id"] for c in q["cards"]]
        self.assertEqual(len(ids), len(set(ids)), f"duplicate ids minted: {ids}")
        self.assertNotEqual(fresh["id"], "C-9021")


class TestLiveIdMutationGuard(unittest.TestCase):
    def test_save_queue_refuses_title_lane_mutation_of_existing_id(self):
        d = tempfile.mkdtemp(prefix="c9027-")
        q = fresh_queue()
        H.add_card(q, mk(title="Queue nearly empty: decompose", lane="planner"))
        H.save_queue(d, q)
        q["cards"][0]["title"] = "Split-health-ready"
        q["cards"][0]["lane"] = "fixer"
        try:
            H.save_queue(d, q)
        except ValueError:
            return
        self.fail("save_queue accepted a title/lane mutation under a live id")

    def test_save_queue_allows_status_field_updates(self):
        d = tempfile.mkdtemp(prefix="c9027-")
        q = fresh_queue()
        c = H.add_card(q, mk())
        H.save_queue(d, q)
        c["status"] = "running"
        c["claimed_by"] = "4242"
        H.save_queue(d, q)  # claim/state fields are NOT protected content
        disk = H.load_queue(d)
        self.assertEqual(disk["cards"][0]["status"], "running")

    def test_save_queue_allows_new_cards_and_reid(self):
        d = tempfile.mkdtemp(prefix="c9027-")
        q = fresh_queue()
        c = H.add_card(q, mk())
        H.save_queue(d, q)
        old_id = c["id"]
        c["id"] = "C-9999"  # _dedup_card_ids-style re-id, title intact
        # re-id removes the old-id row from the in-memory queue;
        # save_queue merge preserves the old-id card from disk (it has
        # no terminal event) to prevent lost updates from concurrent
        # writers.  The re-id'd card and the new card are both present.
        q["cards"] = [x for x in q["cards"] if x["id"] != old_id]
        q["cards"].append(c)
        H.add_card(q, mk(title="new intent"))
        H.save_queue(d, q)
        disk = H.load_queue(d)
        ids = [x["id"] for x in disk["cards"]]
        self.assertIn("C-9999", ids)  # re-id'd card present
        self.assertGreaterEqual(len(disk["cards"]), 2)  # at least 2 new cards


class TestQueueEmptyTriggerCountBasis(unittest.TestCase):
    def _events(self, state_dir):
        path = os.path.join(state_dir, "EVENTS.jsonl")
        with open(path, encoding="utf-8") as f:
            return [json.loads(ln) for ln in f if ln.strip()]

    def test_auto_plan_event_records_ready_and_unblocked_counts(self):
        d = tempfile.mkdtemp(prefix="c9027-")
        old = qgh.STATE
        qgh.STATE = d
        try:
            q = fresh_queue()
            c = H.add_card(q, mk(title="real work in flight", lane="fixer"))
            c["status"] = "running"  # deps satisfied: unblocked, not ready
            H.save_queue(d, q)
            qgh._auto_plan(dict())
        finally:
            qgh.STATE = old
        ap = [e for e in self._events(d) if e["kind"] == "auto_plan"]
        self.assertEqual(len(ap), 1)
        self.assertEqual(ap[0]["ready_count"], 0)
        self.assertEqual(ap[0]["unblocked_count"], 1)
        self.assertTrue(ap[0].get("ts"))

    def test_auto_plan_skipped_event_also_records_basis(self):
        d = tempfile.mkdtemp(prefix="c9027-")
        old = qgh.STATE
        qgh.STATE = d
        try:
            q = fresh_queue()
            H.add_card(q, mk())  # open decompose card -> guard must skip
            H.save_queue(d, q)
            qgh._auto_plan(dict())
        finally:
            qgh.STATE = old
        sk = [e for e in self._events(d) if e["kind"] == "auto_plan_skipped"]
        self.assertEqual(len(sk), 1)
        self.assertIn("ready_count", sk[0])
        self.assertIn("unblocked_count", sk[0])


if __name__ == "__main__":
    unittest.main()
