# C-9090: bounced-card disposition sweep - enumeration parser contract.
#
# RED (measured 2026-09-18): the live queue holds 24 bounced cards (23 of
# them P0/P1) and no mechanism enumerates them: the standup queue looks
# healthy while core-path work sits in status=bounced, and the only
# un-bounce path was a manual one-off card (the C-9084 pattern). These
# tests pin the fail-closed parser the sweep is built on:
#
# - one row per bounced card rendered as id|priority|bounce_count|disposition
# - a missing QUEUE file is a NAMED error (QueueMissingError), never silence
# - a malformed card is a NAMED error (QueueParseError) with index+field
# - every P0/P1 disposition must be refiled|superseded-by|closed with a
#   non-empty payload; assert_complete raises naming the offender
# - P2 bounces may stay pending (listed, not fatal)
#
# The module is stdlib-only and never imports qgh, so it cannot touch the
# live harness state through the QGH_STATE_DIR seam.

import json
import os
import sys
import tempfile
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
if HARNESS_DIR not in sys.path:
    sys.path.insert(0, HARNESS_DIR)

from bounced_sweep import (
    QueueMissingError,
    QueueParseError,
    SweepIncompleteError,
    assert_complete,
    build_sweep,
    collect_bounced,
    load_queue,
    render_row,
)


def write_queue(directory, cards):
    path = os.path.join(directory, "QUEUE.json")
    with open(path, "w") as fh:
        json.dump(dict(cards=cards, seq=len(cards)), fh)
    return path


def card(cid, priority, status, bounce_count=0, title="t"):
    return dict(
        id=cid,
        priority=priority,
        status=status,
        bounce_count=bounce_count,
        title=title,
    )


class TestC9090BouncedSweep(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="c9090-")

    def test_missing_queue_is_named_error(self):
        path = os.path.join(self.tmp, "QUEUE.json")
        with self.assertRaises(QueueMissingError) as ctx:
            load_queue(path)
        self.assertIn(path, str(ctx.exception))

    def test_unparseable_queue_is_named_error(self):
        path = os.path.join(self.tmp, "QUEUE.json")
        with open(path, "w") as fh:
            fh.write("NOT-JSON")
        with self.assertRaises(QueueParseError):
            load_queue(path)

    def test_malformed_card_is_named_error_with_index_and_field(self):
        path = write_queue(self.tmp, [card("C-1", 0, "ready"), dict(id="C-2")])
        queue = load_queue(path)
        with self.assertRaises(QueueParseError) as ctx:
            collect_bounced(queue)
        self.assertIn("C-2", str(ctx.exception))
        self.assertIn("status", str(ctx.exception))

    def test_one_row_per_bounced_card_only(self):
        path = write_queue(
            self.tmp,
            [
                card("C-1", 0, "ready"),
                card("C-2", 0, "bounced", bounce_count=3),
                card("C-3", 1, "bounced", bounce_count=1),
            ],
        )
        bounced = collect_bounced(load_queue(path))
        self.assertEqual([c["id"] for c in bounced], ["C-2", "C-3"])
        rows = [render_row(c) for c in bounced]
        self.assertEqual(rows, ["C-2|P0|3|pending", "C-3|P1|1|pending"])
        self.assertEqual(
            render_row(bounced[0], "refiled:C-9999"),
            "C-2|P0|3|refiled:C-9999",
        )

    def test_p0p1_without_disposition_fails_complete_by_name(self):
        path = write_queue(
            self.tmp,
            [
                card("C-P0", 0, "bounced", bounce_count=3),
                card("C-P2", 2, "bounced", bounce_count=1),
            ],
        )
        queue = load_queue(path)
        artifact = build_sweep(queue, dict(), now_utc="2026-09-18T00:00:00Z")
        self.assertEqual(artifact["total_bounced"], 2)
        self.assertEqual(artifact["p0p1_undispositioned"], ["C-P0"])
        self.assertEqual(artifact["p2_pending"], ["C-P2"])
        self.assertFalse(artifact["all_p0p1_dispositioned"])
        with self.assertRaises(SweepIncompleteError) as ctx:
            assert_complete(artifact)
        self.assertIn("C-P0", str(ctx.exception))

    def test_invalid_disposition_verb_rejected(self):
        path = write_queue(self.tmp, [card("C-P0", 0, "bounced", bounce_count=3)])
        disp = dict()
        disp["C-P0"] = "done:somewhere"
        artifact = build_sweep(load_queue(path), disp, now_utc="2026-09-18T00:00:00Z")
        self.assertIn("C-P0", artifact["p0p1_undispositioned"])
        with self.assertRaises(SweepIncompleteError):
            assert_complete(artifact)

    def test_valid_dispositions_complete(self):
        path = write_queue(self.tmp, [card("C-P0", 0, "bounced", bounce_count=3)])
        disp = dict()
        disp["C-P0"] = "superseded-by:C-9098"
        artifact = build_sweep(load_queue(path), disp, now_utc="2026-09-18T00:00:00Z")
        self.assertEqual(artifact["rows"][0]["row"], "C-P0|P0|3|superseded-by:C-9098")
        self.assertTrue(artifact["all_p0p1_dispositioned"])
        assert_complete(artifact)  # must not raise


if __name__ == "__main__":
    unittest.main()
