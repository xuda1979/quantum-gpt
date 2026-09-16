"""C-9017: queue-integrity re-baseline v4 -- extend the C-9015 v3
queue-integrity invariant from P0 dispatchable cards to ALL cards, and
force the 2026-09-17 recovery-shell fleet to a terminal classification.

RED (measured 2026-09-17 against the live QUEUE.json): the 2026-09-17
event-log recovery rebuilt the queue from card_added events that never
carried acceptance text (EVENTS.jsonl card_added lines carry only
id/title/lane/priority), leaving 61 cards as placeholder shells --
why="(recovered from events)",
acceptance=["recovered card: verify against latest standup"].
Workers claiming a live shell (ready/running/bounced/blocked) have no
acceptance to satisfy and bounce -- 24 gate_bounced / 21
spawn_failed_env events and standup #1 throughput already show it.

The invariant: a placeholder shell is only allowed on a TERMINAL card
(status dead or superseded). Every non-terminal card must carry
task-specific acceptance (never the generic recovered-card
placeholder) and a why that is not the generic recovery marker.
C-9017 triages every shell to RESTORED (acceptance re-attached from a
named durable source: brief file, standup, named card result, or the
EVENTS.jsonl ledger) or DEAD (superseded duplicate / unrecoverable,
per the C-9012 precedent).

Same binding idiom as test_dep_graph_rebaseline_v3.py: asserted
against the LIVE harness/state/QUEUE.json -- the queue is the source
of truth, not a fixture.
"""

import json
import os
import sys
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
sys.path.insert(0, HARNESS_DIR)

QUEUE_PATH = os.path.join(HARNESS_DIR, "state", "QUEUE.json")

PLACEHOLDER_ACCEPTANCE = "recovered card: verify against latest standup"
PLACEHOLDER_WHY = "(recovered from events)"
TERMINAL_STATUSES = ("dead", "superseded")


def load_live_queue():
    with open(QUEUE_PATH, encoding="utf-8") as f:
        return json.load(f)


class TestDepGraphRebaselineV4P1Shells(unittest.TestCase):
    def setUp(self):
        self.assertTrue(os.path.exists(QUEUE_PATH), "QUEUE.json missing at " + QUEUE_PATH)
        self.q = load_live_queue()
        self.cards = dict((c["id"], c) for c in self.q["cards"])

    def test_no_placeholder_shell_on_any_nonterminal_card(self):
        # v3 covered P0 ready/running only; v4 extends the invariant to
        # every card at every priority: a recovered placeholder shell
        # may only survive on a terminal (dead/superseded) card.
        offenders = []
        for c in self.q["cards"]:
            if c.get("status") in TERMINAL_STATUSES:
                continue
            acc = c.get("acceptance") or []
            if not acc:
                offenders.append(c["id"] + ":empty-acceptance")
            for item in acc:
                if item.strip().lower() == PLACEHOLDER_ACCEPTANCE:
                    offenders.append(c["id"] + ":placeholder-acceptance")
                    break
            if (c.get("why") or "").strip() == PLACEHOLDER_WHY:
                offenders.append(c["id"] + ":placeholder-why")
        self.assertEqual(
            offenders,
            [],
            "non-terminal placeholder shells (must be RESTORED or DEAD by C-9017): "
            + ", ".join(offenders),
        )

    def test_restored_live_shells_carry_task_specific_acceptance(self):
        # Every dispatchable shell named to C-9017 must now carry
        # acceptance long enough to be a contract, not a stub.
        LIVE_SHELLS = (
            "C-0015",
            "C-0016",
            "C-0022",
            "C-0023",
            "C-0029",
            "C-0051",
            "C-0052",
            "C-0055",
            "C-0059",
            "C-0064",
            "C-0069",
            # C-9035 (2026-09-17): C-9005 removed from LIVE_SHELLS --
            # duplicate re-score mission superseded into the C-9009
            # lineage (v6 test pins it); a live-shell member must not
            # sit terminal. Its fail-closed gates assert survives below.
            "C-0072",
            "C-0073",
            "C-0076",
            "C-0077",
            "C-9007",
        )
        for cid in LIVE_SHELLS:
            self.assertIn(cid, self.cards, "card " + cid + " vanished from QUEUE.json")
            c = self.cards[cid]
            self.assertNotIn(
                c.get("status"),
                ("dead", "superseded"),
                cid + ": live shell must be RESTORED, not terminal",
            )
            text = " ".join(c.get("acceptance") or []).lower()
            self.assertGreaterEqual(
                len(text),
                80,
                cid + ": restored acceptance too thin to dispatch against",
            )
            self.assertNotIn(PLACEHOLDER_ACCEPTANCE, text)

    def test_eval_leg_restores_carry_failclosed_gates(self):
        # Objective chain: eval legs = eval-failclosed + sha-verified.
        # C-0052 (v4 follow-up, measured 2026-09-17): the C-0010 dual
        # re-score re-target is an eval leg in the beats-base chain
        # (verdict consumed by C-0072 then C-0016) and must carry the
        # same fail-closed pair as C-0015/C-9005/C-0051.
        for cid in ("C-0015", "C-0052", "C-9005"):
            gates = self.cards[cid].get("gates") or []
            self.assertIn("eval-failclosed", gates, cid + " missing eval-failclosed gate")
            self.assertIn("sha-verified", gates, cid + " missing sha-verified gate")

    def test_training_leg_restores_carry_tdd_gate(self):
        # Objective chain: training legs = tdd.
        for cid in ("C-0029", "C-0055"):
            gates = self.cards[cid].get("gates") or []
            self.assertIn("tdd", gates, cid + " missing tdd gate")

    def test_dead_marks_cite_reason(self):
        # No dead-mark without a reason in the result field (C-9012
        # precedent: result carries the why).
        for c in self.q["cards"]:
            if c.get("status") == "dead":
                self.assertTrue(
                    (c.get("result") or "").strip(),
                    c["id"] + ": dead without a cited reason in result",
                )


if __name__ == "__main__":
    unittest.main()
