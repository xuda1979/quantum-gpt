"""C-9534: auto-retire high-bounce cards to keep the queue clean.

Bounced cards with bounce_count >= 4 are stuck -- they keep failing the same
way. Auto-retire them (mark dead) so the queue stays clean and the dispatcher
can focus on new, more targeted cards. The bounce reasons are preserved for
future mining.

RED: this test must FAIL until auto_retire_high_bounce exists and is called
from the tick.
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


class TestAutoRetireHighBounce(unittest.TestCase):
    def setUp(self):
        self.state_dir = tempfile.mkdtemp(prefix="qgh-9534-")
        cards = [
            {"id": "C-3001", "status": "done", "title": "done", "bounce_count": 0, "lane": "fixer"},
            {
                "id": "C-3002",
                "status": "bounced",
                "title": "bounce3",
                "bounce_count": 3,
                "lane": "fixer",
            },
            {
                "id": "C-3003",
                "status": "bounced",
                "title": "bounce4",
                "bounce_count": 4,
                "lane": "fixer",
            },
            {
                "id": "C-3004",
                "status": "bounced",
                "title": "bounce5",
                "bounce_count": 5,
                "lane": "evaluator",
            },
            {
                "id": "C-3005",
                "status": "bounced",
                "title": "bounce2",
                "bounce_count": 2,
                "lane": "fixer",
            },
        ]
        qgh.save_json(
            os.path.join(self.state_dir, "QUEUE.json"),
            {"cards": cards, "seq": 100},
        )

    def test_retire_high_bounce_cards(self):
        """Cards with bounce_count >= 4 should be retired to dead."""
        result = qgh.auto_retire_high_bounce(self.state_dir)
        self.assertEqual(result, 2, "should retire 2 cards (bounce_count 4 and 5)")

    def test_does_not_retire_low_bounce(self):
        """Cards with bounce_count < 4 should NOT be retired."""
        qgh.auto_retire_high_bounce(self.state_dir)
        queue = qgh.load_queue(self.state_dir)
        by_id = {c["id"]: c for c in queue["cards"]}
        self.assertEqual(by_id["C-3002"]["status"], "bounced", "bounce_count=3 should stay bounced")
        self.assertEqual(by_id["C-3005"]["status"], "bounced", "bounce_count=2 should stay bounced")

    def test_tick_calls_auto_retire(self):
        """cmd_tick should call auto_retire_high_bounce."""
        src = inspect.getsource(qgh.cmd_tick)
        self.assertIn(
            "auto_retire_high_bounce(",
            src,
            "cmd_tick never calls auto_retire_high_bounce; high-bounce cards "
            "accumulate forever and clog the queue.",
        )


if __name__ == "__main__":
    unittest.main()
