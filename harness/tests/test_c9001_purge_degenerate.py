"""C-9001: purge the degenerate placeholder card and prevent re-mint.

C-9001 (title='t', why='w', acceptance=['a']) was minted before the
C-9147 validation gate existed. It is now status=dead with a dead pid
(22626). These tests verify:

1. purge_card() removes a dead degenerate card from the queue.
2. After purge, the card id C-9001 is never re-issued by add_card
   (history_card_ids prevents id recycling -- C-9124 regression).
3. The CLI path cmd_card_remove purges a dead card and emits a
   card_purged event.
4. purge_card refuses to purge a running card with a live pid (orphan
   guard), even if the card is degenerate.

RED first: these tests must pass before C-9001 is marked done.
"""

import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.dirname(HERE)
sys.path.insert(0, HARNESS)
import harness_lib as H  # noqa: E402
import qgh  # noqa: E402


def make_valid_card(**kw):
    base = dict(
        title="a legitimate card title",
        lane="fixer",
        why="a legitimate reason for this card",
        acceptance=["a measurable acceptance criterion"],
    )
    base.update(kw)
    return H.new_card(**base)


class TestPurgeDegenerateDeadCard(unittest.TestCase):
    """purge_card removes a dead degenerate card (status=dead, pid dead)."""

    def test_purge_removes_dead_degenerate_card(self):
        """C-9001 is status=dead with dead pid 22626; purge must succeed."""
        q = {"cards": [], "seq": 9230}
        c = H.add_card(q, make_valid_card(card_id="C-9001"))
        c["title"] = "t"
        c["why"] = "w"
        c["acceptance"] = ["a"]
        c["status"] = "dead"
        c["claimed_by"] = "22626"
        c["bounce_reason"] = "placeholder title=t why=w burned fixer slot"

        removed = H.purge_card(q, "C-9001", live_fn=lambda pid: False)
        self.assertTrue(removed)
        self.assertIsNone(H.find_card(q, "C-9001"))

    def test_purge_refuses_live_running_degenerate_card(self):
        """Even a degenerate card must not be orphaned if pid is live."""
        q = {"cards": [], "seq": 9230}
        c = H.add_card(q, make_valid_card(card_id="C-9001"))
        c["status"] = "running"
        c["claimed_by"] = str(os.getpid())

        removed = H.purge_card(q, "C-9001")
        self.assertFalse(removed)
        self.assertIsNotNone(H.find_card(q, "C-9001"))


class TestPurgedIdNeverReissued(unittest.TestCase):
    """After purging C-9001, add_card must never re-mint C-9001.

    C-9124 was re-minted 2026-09-20 for an unrelated card after its
    original was pruned. history_card_ids() reads EVENTS.jsonl to
    prevent this. The purge event written by cmd_card_remove ensures
    the purged id enters history.
    """

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="c9001-purge-")
        self.old_state = qgh.STATE
        qgh.STATE = self.tmpdir
        H.save_json(os.path.join(self.tmpdir, "QUEUE.json"), {"cards": [], "seq": 9230})
        H.save_json(os.path.join(self.tmpdir, "FLEET.json"), {"agents": []})
        open(os.path.join(self.tmpdir, "EVENTS.jsonl"), "w").close()
        goal_path = os.path.join(HARNESS, "state", "GOAL.json")
        H.save_json(os.path.join(self.tmpdir, "GOAL.json"), H.load_json(goal_path, {}))

    def tearDown(self):
        qgh.STATE = self.old_state

    def test_purged_id_not_reissued_by_add_card(self):
        """Purge C-9001, then add_card must skip to C-9231, not re-mint."""
        q = H.load_json(os.path.join(self.tmpdir, "QUEUE.json"), {"cards": [], "seq": 9230})
        c = H.add_card(q, make_valid_card(card_id="C-9001"))
        c["status"] = "dead"
        c["claimed_by"] = "999999"
        H.save_queue(self.tmpdir, q)

        import argparse

        args = argparse.Namespace(ids=["C-9001"])
        qgh.cmd_card_remove(args)

        q2 = H.load_json(os.path.join(self.tmpdir, "QUEUE.json"), {"cards": [], "seq": 9230})
        self.assertIsNone(H.find_card(q2, "C-9001"))

        c_new = H.add_card(q2, make_valid_card(), state_dir=self.tmpdir)
        self.assertNotEqual(c_new["id"], "C-9001", "add_card re-issued purged id C-9001")

    def test_card_purged_event_written(self):
        """cmd_card_remove must emit a card_purged event for audit trail."""
        q = H.load_json(os.path.join(self.tmpdir, "QUEUE.json"), {"cards": [], "seq": 9230})
        c = H.add_card(q, make_valid_card(card_id="C-9001"))
        c["status"] = "dead"
        c["claimed_by"] = None
        H.save_queue(self.tmpdir, q)

        import argparse

        args = argparse.Namespace(ids=["C-9001"])
        qgh.cmd_card_remove(args)

        events = []
        with open(os.path.join(self.tmpdir, "EVENTS.jsonl")) as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(json.loads(line))
        purged = [e for e in events if e.get("kind") == "card_purged" and e.get("id") == "C-9001"]
        self.assertEqual(len(purged), 1, "card_purged event for C-9001 must be written once")


class TestEndToEndDegeneratePurge(unittest.TestCase):
    """End-to-end: a dead degenerate card matching C-9001 exact shape
    is purgeable and the queue is clean afterward."""

    def test_c9001_exact_shape_purgeable(self):
        """Reproduce C-9001 field values and verify purge succeeds."""
        q = {"cards": [], "seq": 9230}
        c = H.add_card(q, make_valid_card(card_id="C-9001"))
        c["title"] = "t"
        c["why"] = "w"
        c["acceptance"] = ["a"]
        c["status"] = "dead"
        c["claimed_by"] = "22626"
        c["bounce_reason"] = "placeholder title=t why=w burned fixer slot"
        c["result"] = "voided placeholder card C-9147"
        c["budget_min"] = 25
        c["gates"] = []
        c["deps"] = []
        c["priority"] = 1

        removed = H.purge_card(q, "C-9001", live_fn=lambda pid: False)
        self.assertTrue(removed)
        self.assertIsNone(H.find_card(q, "C-9001"))
        self.assertEqual(len(q["cards"]), 0)


class TestCardPurgedIsTerminal(unittest.TestCase):
    """C-0001/C-9001: card_purged events must be recognized as terminal
    by history_terminal_card_ids so save_queue does not resurrect purged
    cards from disk.

    RED (measured 2026-09-20): the regex in history_terminal_card_ids
    omits 'card_purged' from its alternation, so a purged card whose
    event is card_purged is NOT in the terminal set. save_queue then
    resurrects it from disk during the lost-update merge.
    """

    def test_card_purged_in_terminal_set(self):
        """card_purged must be in TERMINAL_EVENT_KINDS."""
        self.assertIn("card_purged", H.TERMINAL_EVENT_KINDS)

    def test_card_purged_detected_by_history(self):
        """history_terminal_card_ids must include a card_purged event id."""
        import tempfile

        tmpdir = tempfile.mkdtemp(prefix="c9001-purged-terminal-")
        events_path = os.path.join(tmpdir, "EVENTS.jsonl")
        with open(events_path, "w") as f:
            f.write(
                json.dumps(
                    {
                        "ts": "2026-09-20T07:00:00Z",
                        "kind": "card_purged",
                        "id": "C-9001",
                        "title": "purged placeholder",
                    }
                )
                + "\n"
            )
        terminal = H.history_terminal_card_ids(tmpdir)
        self.assertIn(
            "C-9001",
            terminal,
            (
                "card_purged event must be recognized as terminal by "
                "history_terminal_card_ids -- save_queue will resurrect "
                "purged cards from disk otherwise"
            ),
        )


if __name__ == "__main__":
    unittest.main()
