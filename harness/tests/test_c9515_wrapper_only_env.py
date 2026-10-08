"""C-9515 RED: agent death with only wrapper output should be environmental."""

import os
import sys
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
sys.path.insert(0, HARNESS_DIR)
import harness_lib as H  # noqa: E402
import qgh  # noqa: E402


class TestWrapperOnlyEnvNoStrike(unittest.TestCase):
    def setUp(self):
        self._orig_state = qgh.STATE
        qgh.STATE = os.path.join(
            os.environ.get("QGH_STATE_DIR", "/tmp/qgh-test"), "wrapper_env_test"
        )
        os.makedirs(os.path.join(qgh.STATE, "agents"), exist_ok=True)
        os.makedirs(os.path.join(qgh.STATE, "locks"), exist_ok=True)
        os.makedirs(os.path.join(qgh.STATE, "standups"), exist_ok=True)

    def tearDown(self):
        qgh.STATE = self._orig_state

    def _make_card(self, cid="C-9515"):
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

    def test_wrapper_only_death_no_strike(self):
        """Agent dies with only claude wrapper output (no RESULT) -> environmental."""
        card = self._make_card()
        q = {"cards": [card], "seq": 9515}
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
            f.write("claude wrapper (cmri): probing CMRI key sk-xxx model=DeepSeek\n")
            f.write("claude wrapper (cmri): using CMRI key sk-xxx model=DeepSeek\n")
        qgh._reap()
        q = qgh.load_queue(qgh.STATE)
        c = H.find_card(q, card["id"])
        self.assertEqual(
            c.get("bounce_count", 0), 0, "wrapper-only death must not burn bounce strike"
        )


if __name__ == "__main__":
    unittest.main()
