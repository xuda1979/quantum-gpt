"""C-9529 RED: bounced cards with bounces=0 must be auto-requeued.

Bounced cards sitting idle with 0 bounces are a productivity leak.
The tick should auto-requeue them (set status=ready, clear claimed_by)
so the dispatcher can pick them up on the next cycle.

TDD: this test must FAIL first (no auto_requeue_zero_bounce function exists).
"""

import os
import sys
import tempfile
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
sys.path.insert(0, HARNESS_DIR)
import harness_lib as H  # noqa: E402

TMP = tempfile.mkdtemp(prefix="qgh-test-9529-")
os.environ["QGH_STATE_DIR"] = TMP


class TestAutoRequeueZeroBounce(unittest.TestCase):
    def setUp(self):
        """Create a queue with a mix of card statuses."""
        self.state_dir = tempfile.mkdtemp(prefix="qgh-9529-")
        self.queue_path = os.path.join(self.state_dir, "queue.json")
        cards = [
            {
                "id": "C-1001",
                "status": "done",
                "title": "done card",
                "bounce_count": 0,
                "lane": "fixer",
            },
            {
                "id": "C-1002",
                "status": "bounced",
                "title": "bounce0",
                "bounce_count": 0,
                "lane": "fixer",
                "result": "blocked",
            },
            {
                "id": "C-1003",
                "status": "bounced",
                "title": "bounce3",
                "bounce_count": 3,
                "lane": "fixer",
                "result": "blocked",
            },
            {
                "id": "C-1004",
                "status": "running",
                "title": "running",
                "bounce_count": 0,
                "lane": "fixer",
            },
            {
                "id": "C-1005",
                "status": "bounced",
                "title": "bounce0b",
                "bounce_count": 0,
                "lane": "evaluator",
                "result": "env fail",
            },
        ]
        H.save_json(self.queue_path, {"cards": cards})

    def test_auto_requeue_zero_bounce_cards(self):
        """Zero-bounce bounced cards should be requeued to ready."""
        result = H.auto_requeue_zero_bounce(self.state_dir)
        self.assertTrue(result, "should have requeued at least one card")
        queue = H.load_queue(self.state_dir)
        by_id = {c["id"]: c for c in queue["cards"]}
        self.assertEqual(
            by_id["C-1002"]["status"], "ready", "zero-bounce bounced card should be requeued"
        )
        self.assertEqual(
            by_id["C-1005"]["status"], "ready", "zero-bounce bounced card should be requeued"
        )
        self.assertEqual(
            by_id["C-1003"]["status"], "bounced", "high-bounce card should not be requeued"
        )
        self.assertEqual(by_id["C-1004"]["status"], "running", "running card should not be touched")

    def test_auto_requeue_clears_claimed_by(self):
        """Requeued cards should have claimed_by cleared."""
        H.auto_requeue_zero_bounce(self.state_dir)
        queue = H.load_queue(self.state_dir)
        for c in queue["cards"]:
            if c["id"] in ("C-1002", "C-1005"):
                self.assertIsNone(c.get("claimed_by"), c["id"] + " claimed_by should be cleared")

    def test_auto_requeue_returns_count(self):
        """Should return the number of cards requeued."""
        result = H.auto_requeue_zero_bounce(self.state_dir)
        self.assertEqual(result, 2, "should requeue exactly 2 cards")

    def test_auto_requeue_idempotent(self):
        """Running twice should not requeue anything the second time."""
        H.auto_requeue_zero_bounce(self.state_dir)
        result2 = H.auto_requeue_zero_bounce(self.state_dir)
        self.assertEqual(result2, 0, "second call should find nothing to requeue")


if __name__ == "__main__":
    unittest.main()
