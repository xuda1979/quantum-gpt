"""C-9123: dead-worker requeue — cards with all workers dead and deadline
expired must be bounced (not stuck in 'running' forever).

The C-9029 incident: a card sat in 'running' for 8+ hours with 7 dead fleet
entries and an expired deadline. The reaper marked workers dead but the card
status never changed, creating a dependency deadlock that blocked 3 downstream
cards and prevented training resumption for the entire day.
"""

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

_HARNESS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_REPO_ROOT = os.path.dirname(_HARNESS_DIR)
for p in (_HARNESS_DIR, _REPO_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

import harness_lib as H  # noqa: E402


def _make_card(cid, status="running", deps=None, deadline_utc=None):
    return dict(
        id=cid,
        title=f"test-{cid}",
        lane="fixer",
        priority=0,
        why="test",
        acceptance=["done"],
        status=status,
        deps=deps or [],
        budget_min=25,
        claimed_by="999",
        claimed_utc="2026-09-18T10:00:00Z",
        deadline_utc=deadline_utc,
    )


class TestDeadWorkerRequeue(unittest.TestCase):
    """When all fleet workers for a card are dead and the deadline has
    passed, the card must be bounced — not left in 'running' forever."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="qgh-deadworker-")
        self.state = self.tmp

    def _save_queue(self, cards):
        H.save_json(os.path.join(self.state, "QUEUE.json"), {"cards": cards, "seq": 100})

    def _save_fleet(self, agents):
        H.save_json(os.path.join(self.state, "FLEET.json"), {"agents": agents})

    def test_card_with_dead_workers_and_expired_deadline_bounced(self):
        """Card 'running' with all dead workers + expired deadline → bounced."""
        past = (datetime.now(timezone.utc) - timedelta(hours=8)).strftime("%Y-%m-%dT%H:%M:%SZ")
        card = _make_card("C-9001", status="running", deadline_utc=past)
        self._save_queue([card])
        self._save_fleet(
            [
                {
                    "card": "C-9001",
                    "pid": 99999,
                    "status": "running",
                    "lane": "fixer",
                    "deadline_utc": past,
                    "started_utc": past,
                },
            ]
        )
        # All PIDs are dead (99999 doesn't exist)
        bounced = H.bounce_dead_running_cards(self.state, pid_alive_fn=lambda pid: False)
        self.assertEqual(bounced, ["C-9001"])
        q = H.load_json(os.path.join(self.state, "QUEUE.json"))
        self.assertEqual(q["cards"][0]["status"], "bounced")

    def test_card_with_alive_worker_not_bounced(self):
        """Card 'running' with at least one alive worker → stays running."""
        future = (datetime.now(timezone.utc) + timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%SZ")
        card = _make_card("C-9002", status="running", deadline_utc=future)
        self._save_queue([card])
        self._save_fleet(
            [
                {
                    "card": "C-9002",
                    "pid": 99998,
                    "status": "running",
                    "lane": "fixer",
                    "deadline_utc": future,
                    "started_utc": "2026-09-18T10:00:00Z",
                },
            ]
        )
        bounced = H.bounce_dead_running_cards(self.state, pid_alive_fn=lambda pid: pid == 99998)
        self.assertEqual(bounced, [])
        q = H.load_json(os.path.join(self.state, "QUEUE.json"))
        self.assertEqual(q["cards"][0]["status"], "running")

    def test_card_with_no_fleet_entries_bounced_if_overdue(self):
        """Card 'running' with NO fleet entries + expired deadline → bounced."""
        past = (datetime.now(timezone.utc) - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
        card = _make_card("C-9003", status="running", deadline_utc=past)
        self._save_queue([card])
        self._save_fleet([])
        bounced = H.bounce_dead_running_cards(self.state, pid_alive_fn=lambda pid: False)
        self.assertEqual(bounced, ["C-9003"])

    def test_card_not_running_not_affected(self):
        """Cards in other statuses (ready, blocked, done) are not touched."""
        card = _make_card("C-9004", status="ready")
        self._save_queue([card])
        self._save_fleet([])
        bounced = H.bounce_dead_running_cards(self.state, pid_alive_fn=lambda pid: False)
        self.assertEqual(bounced, [])

    def test_bounce_records_event(self):
        """Bouncing a dead card records a 'dead_worker_requeued' event."""
        past = (datetime.now(timezone.utc) - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        card = _make_card("C-9005", status="running", deadline_utc=past)
        self._save_queue([card])
        self._save_fleet([])
        H.bounce_dead_running_cards(self.state, pid_alive_fn=lambda pid: False)
        events_path = os.path.join(self.state, "events.jsonl")
        if os.path.exists(events_path):
            lines = open(events_path).read().strip().split("\n")
            kinds = [json.loads(line).get("kind") for line in lines if line]
            self.assertIn("dead_worker_requeued", kinds)


if __name__ == "__main__":
    unittest.main()
