"""C-9533: auto_requeue_zero_bounce must use bounce_count field, not bounces.

The function checks c.get("bounces", 0) but real cards use "bounce_count"
(see new_card at line 219). This means the function requeues ALL bounced
cards (bounces always defaults to 0), including ones with bounce_count=4
that should NOT be requeued. The tick also never calls this function.

RED: this test must FAIL until the field name is fixed and the tick calls it.
"""

import inspect
import os
import sys
import tempfile
import unittest

_HARNESS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _HARNESS_DIR not in sys.path:
    sys.path.insert(0, _HARNESS_DIR)

import qgh  # noqa: E402


class TestAutoRequeueBounceCountField(unittest.TestCase):
    def setUp(self):
        self.state_dir = tempfile.mkdtemp(prefix="qgh-9533-")
        self.queue_path = os.path.join(self.state_dir, "QUEUE.json")
        cards = [
            {"id": "C-2001", "status": "done", "title": "done", "bounce_count": 0, "lane": "fixer"},
            {
                "id": "C-2002",
                "status": "bounced",
                "title": "bounce0",
                "bounce_count": 0,
                "lane": "fixer",
            },
            {
                "id": "C-2003",
                "status": "bounced",
                "title": "bounce3",
                "bounce_count": 3,
                "lane": "fixer",
            },
            {
                "id": "C-2004",
                "status": "running",
                "title": "running",
                "bounce_count": 0,
                "lane": "fixer",
            },
            {
                "id": "C-2005",
                "status": "bounced",
                "title": "bounce0b",
                "bounce_count": 0,
                "lane": "evaluator",
            },
        ]
        qgh.save_json(self.queue_path, {"cards": cards, "seq": 100})

    def test_requeues_zero_bounce_count_cards(self):
        """Cards with bounce_count=0 should be requeued."""
        result = qgh.auto_requeue_zero_bounce(self.state_dir)
        self.assertEqual(result, 2, "should requeue exactly 2 zero-bounce cards")

    def test_does_not_requeue_high_bounce_count(self):
        """Cards with bounce_count > 0 should NOT be requeued."""
        qgh.auto_requeue_zero_bounce(self.state_dir)
        queue = qgh.load_queue(self.state_dir)
        by_id = {c["id"]: c for c in queue["cards"]}
        self.assertEqual(
            by_id["C-2003"]["status"], "bounced", "card with bounce_count=3 should NOT be requeued"
        )

    def test_tick_calls_auto_requeue(self):
        """cmd_tick should call auto_requeue_zero_bounce."""
        src = inspect.getsource(qgh.cmd_tick)
        self.assertIn(
            "auto_requeue_zero_bounce(",
            src,
            "cmd_tick never calls auto_requeue_zero_bounce; bounced cards "
            "with 0 bounces sit idle forever.",
        )


if __name__ == "__main__":
    unittest.main()
