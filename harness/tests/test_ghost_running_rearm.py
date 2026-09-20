"""C-9014: ghost running-card re-arm reconcile.

RED (measured 2026-09-17): the event-log recovery flipped cards whose last
event was `dispatched` (no matching `reaped`) to status "running" with
claimed_by=None. The qgh harvest loop only reaps cards that HAVE a fleet
agent row, so a running card with no fleet entry is never cleaned:
running_count() counts it against its lane cap and the lane is blocked
forever. Measured on the live board 2026-09-16T20:40Z: C-0051/C-0074/
C-0076/C-0078 all running, claimed_by=None, no fleet entry.

This pins the reconcile: requeue_card() refuses non-bounced cards (fail-
closed by design), so the ghost path needs its own transition -- the same
environmental re-arm qgh already uses for workers that died without a
verdict (ready, claims cleared, bounce_count untouched, requeued_utc set
so the reaper exhausted-retries tripwire cannot eat it). Never touches a
card that HAS a live fleet entry; a fleet entry whose pid is dead or whose
lstart identity no longer matches is NOT live (pid reuse), so its card is
a ghost too.
"""

import os
import sys
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
sys.path.insert(0, HARNESS_DIR)
import harness_lib as H  # noqa: E402

NEW_CARD_KW = ("budget_min", "gates", "deps", "priority")


def make_card(**kw):
    cid = kw.pop("id", None)
    base = dict(
        title="test card", lane="fixer", why="test why", acceptance=["acceptance criterion"]
    )
    for k in NEW_CARD_KW:
        if k in kw:
            base[k] = kw.pop(k)
    c = H.new_card(card_id=cid, **base)
    c.update(kw)
    return c


def q(*cards):
    return dict(cards=list(cards))


def fl(*agents):
    return dict(agents=list(agents))


def agent(card, pid=123, status="running", lstart="Mon Jan  1 00:00:00 2024"):
    return dict(
        pid=pid,
        card=card,
        lane="fixer",
        status=status,
        lstart=lstart,
        started_utc="2026-09-16T20:00:00Z",
    )


class TestGhostRunningRearm(unittest.TestCase):
    def test_running_card_without_fleet_entry_is_rearmed(self):
        queue = q(
            make_card(
                id="C-9001",
                status="running",
                claimed_by="9",
                claimed_utc="2026-09-16T20:00:00Z",
                deadline_utc="2026-09-16T20:25:00Z",
                bounce_count=1,
            )
        )
        fleet = fl(agent("C-9999"))  # some other card live worker
        rearmed = H.rearm_ghost_running_cards(queue, fleet, live_fn=lambda a: True)
        self.assertEqual(rearmed, ["C-9001"])
        c = H.find_card(queue, "C-9001")
        self.assertEqual(c["status"], "ready")
        self.assertIsNone(c["claimed_by"])
        self.assertIsNone(c["claimed_utc"])
        self.assertIsNone(c["deadline_utc"])
        self.assertTrue(c.get("requeued_utc"))
        self.assertEqual(c["bounce_count"], 1)  # environmental: no strike

    def test_running_card_with_live_entry_is_untouched(self):
        queue = q(make_card(id="C-9001", status="running", claimed_by="9"))
        fleet = fl(agent("C-9001", pid=4242))
        rearmed = H.rearm_ghost_running_cards(queue, fleet, live_fn=lambda a: True)
        self.assertEqual(rearmed, [])
        self.assertEqual(H.find_card(queue, "C-9001")["status"], "running")

    def test_dead_or_lstart_mismatched_entry_is_not_live(self):
        queue = q(
            make_card(id="C-9001", status="running", claimed_by="9"),
            make_card(id="C-9002", status="running", claimed_by="9"),
        )
        fleet = fl(
            agent("C-9001", pid=111, lstart="old identity"),
            agent("C-9002", pid=222, lstart="old identity"),
        )

        def live(a):
            if a["pid"] == 111:
                return False  # process gone
            return a["lstart"] == "new identity"  # pid reused by someone else

        rearmed = H.rearm_ghost_running_cards(queue, fleet, live_fn=live)
        self.assertEqual(sorted(rearmed), ["C-9001", "C-9002"])
        for cid in ("C-9001", "C-9002"):
            self.assertEqual(H.find_card(queue, cid)["status"], "ready")

    def test_stopped_entries_and_terminal_cards_never_touched(self):
        queue = q(
            make_card(id="C-9001", status="running", claimed_by="9"),
            make_card(id="C-9002", status="done"),
            make_card(id="C-9003", status="bounced", bounce_count=3),
        )
        # only a STOPPED entry for C-9001 -> ghost; terminal cards ignored
        fleet = fl(agent("C-9001", status="stopped"))
        rearmed = H.rearm_ghost_running_cards(queue, fleet, live_fn=lambda a: True)
        self.assertEqual(rearmed, ["C-9001"])
        self.assertEqual(H.find_card(queue, "C-9001")["status"], "ready")
        self.assertEqual(H.find_card(queue, "C-9002")["status"], "done")
        self.assertEqual(H.find_card(queue, "C-9003")["status"], "bounced")

    def test_idempotent_and_noop(self):
        queue = q(make_card(id="C-9001", status="ready"))
        fleet = fl()
        fn = H.rearm_ghost_running_cards
        self.assertEqual(fn(queue, fleet, live_fn=lambda a: True), [])
        self.assertEqual(queue["cards"][0]["status"], "ready")


if __name__ == "__main__":
    unittest.main()
