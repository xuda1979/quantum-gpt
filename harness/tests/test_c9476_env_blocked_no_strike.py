"""C-9476 RED: BLOCKED with environmental text should not burn bounce."""
import json
import os
import sys
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
sys.path.insert(0, HARNESS_DIR)
import harness_lib as H
import qgh


class TestEnvBlockedNoStrike(unittest.TestCase):
    def setUp(self):
        for sub in ("agents", "briefs", "locks", "standup", "probes"):
            os.makedirs(os.path.join(qgh.STATE, sub), exist_ok=True)
        ev = os.path.join(qgh.STATE, "EVENTS.jsonl")
        if os.path.exists(ev):
            os.remove(ev)
        qgh.save_json(os.path.join(qgh.STATE, "QUEUE.json"), {"cards": [], "seq": 0})
        qgh.save_json(os.path.join(qgh.STATE, "FLEET.json"), {"agents": []})
        qgh.save_json(
            os.path.join(qgh.STATE, "OPS.json"),
            {"consecutive_spawn_failures": 0, "backoff_until_utc": None},
        )

    def test_blocked_with_transport_error_does_not_bounce(self):
        q = qgh.load_queue(qgh.STATE)
        card = H.add_card(q, H.new_card(
            title="test env blocked card here",
            lane="evaluator",
            why="test why",
            acceptance=["test acceptance"],
        ))
        card["status"] = "running"
        card["claimed_by"] = "1"
        card["claimed_utc"] = H.now_iso()
        card["deadline_utc"] = H.now_iso()
        qgh.save_queue(qgh.STATE, q)
        qgh.save_json(
            os.path.join(qgh.STATE, "FLEET.json"),
            {"agents": [dict(pid=99999, card=card["id"], lane="evaluator", status="running", log=os.path.join(qgh.STATE, "agents", card["id"] + ".log"))]},
        )
        log = os.path.join(qgh.STATE, "agents", card["id"] + ".log")
        with open(log, "w") as f:
            f.write("RESULT: BLOCKED ASI2 transport error: connection refused\n")
        qgh._reap()
        q = qgh.load_queue(qgh.STATE)
        c = H.find_card(q, card["id"])
        self.assertEqual(c["status"], "ready")
        self.assertEqual(c.get("bounce_count", 0), 0)

    def test_blocked_without_env_text_does_bounce(self):
        q = qgh.load_queue(qgh.STATE)
        card = H.add_card(q, H.new_card(
            title="test normal blocked card here",
            lane="fixer",
            why="test why",
            acceptance=["test acceptance"],
        ))
        card["status"] = "running"
        card["claimed_by"] = "1"
        card["claimed_utc"] = H.now_iso()
        card["deadline_utc"] = H.now_iso()
        qgh.save_queue(qgh.STATE, q)
        qgh.save_json(
            os.path.join(qgh.STATE, "FLEET.json"),
            {"agents": [dict(pid=99999, card=card["id"], lane="fixer", status="running", log=os.path.join(qgh.STATE, "agents", card["id"] + ".log"))]},
        )
        log = os.path.join(qgh.STATE, "agents", card["id"] + ".log")
        with open(log, "w") as f:
            f.write("RESULT: BLOCKED waiting on dependency\n")
        qgh._reap()
        q = qgh.load_queue(qgh.STATE)
        c = H.find_card(q, card["id"])
        self.assertEqual(c.get("bounce_count", 0), 1)


if __name__ == "__main__":
    unittest.main()