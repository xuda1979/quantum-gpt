"""C-9505 RED: BLOCKED with fleet-down text should not burn bounce.

When the fleet is down (all boxes not ready), agents correctly report
BLOCKED but the harness does not recognize fleet / box not ready /
boxes report ready as environmental -- so the card gets a bounce strike
and eventually dies after 3 strikes, blocking the critical path.
"""

import os
import sys
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
sys.path.insert(0, HARNESS_DIR)
import harness_lib as H  # noqa: E402
import qgh  # noqa: E402


class TestFleetDownEnvNoStrike(unittest.TestCase):
    def setUp(self):
        self._orig_state = qgh.STATE
        qgh.STATE = os.path.join(
            os.environ.get("QGH_STATE_DIR", "/tmp/qgh-test"), "fleet_down_test"
        )
        os.makedirs(os.path.join(qgh.STATE, "agents"), exist_ok=True)
        os.makedirs(os.path.join(qgh.STATE, "locks"), exist_ok=True)
        os.makedirs(os.path.join(qgh.STATE, "standups"), exist_ok=True)

    def tearDown(self):
        qgh.STATE = self._orig_state

    def _make_card(self, cid="C-9505"):
        return {
            "id": cid,
            "title": "test card",
            "lane": "trainer-ops",
            "priority": 0,
            "why": "test",
            "acceptance": ["test acceptance"],
            "gates": [],
            "deps": [],
            "budget_min": 30,
            "status": "running",
            "created_utc": "2026-09-20T10:00:00Z",
            "claimed_by": 99999,
            "claimed_utc": "2026-09-20T10:00:00Z",
            "deadline_utc": "2026-09-20T12:00:00Z",
            "result": None,
            "bounce_count": 0,
            "bounce_reason": None,
        }

    def _setup_and_reap(self, card, blocked_text):
        q = {"cards": [card], "seq": int(card["id"][2:])}
        qgh.save_queue(qgh.STATE, q)
        qgh.save_json(
            os.path.join(qgh.STATE, "FLEET.json"),
            {
                "agents": [
                    dict(
                        pid=99999,
                        card=card["id"],
                        lane="trainer-ops",
                        status="running",
                        log=os.path.join(qgh.STATE, "agents", card["id"] + ".log"),
                    )
                ]
            },
        )
        log = os.path.join(qgh.STATE, "agents", card["id"] + ".log")
        with open(log, "w") as f:
            f.write(blocked_text)
        qgh._reap()
        q = qgh.load_queue(qgh.STATE)
        return H.find_card(q, card["id"])

    def test_fleet_not_ready_no_strike(self):
        card = self._make_card("C-9505")
        c = self._setup_and_reap(
            card, "RESULT: BLOCKED fleet not ready; all 3 boxes report not ready\n"
        )
        self.assertEqual(
            c.get("bounce_count", 0), 0, "fleet-down BLOCKED must not burn bounce strike"
        )

    def test_box_not_ready_no_strike(self):
        card = self._make_card("C-9506")
        c = self._setup_and_reap(
            card, "RESULT: BLOCKED box not ready; cannot reach ASI2 for eval\n"
        )
        self.assertEqual(
            c.get("bounce_count", 0), 0, "box-not-ready BLOCKED must not burn bounce strike"
        )

    def test_fleet_down_no_strike(self):
        card = self._make_card("C-9507")
        c = self._setup_and_reap(card, "RESULT: BLOCKED fleet down; 0/3 boxes ready\n")
        self.assertEqual(
            c.get("bounce_count", 0), 0, "fleet-down BLOCKED must not burn bounce strike"
        )


if __name__ == "__main__":
    unittest.main()
