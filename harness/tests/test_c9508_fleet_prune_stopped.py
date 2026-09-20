"""C-9508 RED: stopped fleet agents must be pruned to prevent unbounded growth."""

import os
import sys
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
sys.path.insert(0, HARNESS_DIR)
import qgh  # noqa: E402


class TestFleetPruneStopped(unittest.TestCase):
    def setUp(self):
        self._orig_state = qgh.STATE
        qgh.STATE = os.path.join(
            os.environ.get("QGH_STATE_DIR", "/tmp/qgh-test"), "fleet_prune_test"
        )
        os.makedirs(os.path.join(qgh.STATE, "agents"), exist_ok=True)
        os.makedirs(os.path.join(qgh.STATE, "locks"), exist_ok=True)
        os.makedirs(os.path.join(qgh.STATE, "standups"), exist_ok=True)

    def tearDown(self):
        qgh.STATE = self._orig_state

    def test_stopped_agents_pruned_after_reap(self):
        """Stopped agents should be pruned from FLEET.json after reap."""
        # Set up fleet with 5 stopped agents and 1 running
        agents = []
        for i in range(5):
            agents.append(
                {
                    "pid": 10000 + i,
                    "card": f"C-{9200+i}",
                    "lane": "fixer",
                    "status": "stopped",
                    "log": "/dev/null",
                }
            )
        agents.append(
            {
                "pid": 99999,
                "card": "C-9500",
                "lane": "trainer-ops",
                "status": "running",
                "log": os.path.join(qgh.STATE, "agents", "C-9500.log"),
            }
        )
        qgh.save_json(os.path.join(qgh.STATE, "FLEET.json"), {"agents": agents})
        qgh.save_json(os.path.join(qgh.STATE, "QUEUE.json"), {"cards": [], "seq": 9500})
        qgh.save_json(
            os.path.join(qgh.STATE, "GOAL.json"),
            {
                "objective": "test",
                "model": "test",
                "target_pass": "18/18",
                "status": "OPEN",
                "created_utc": "2026-09-20T10:00:00Z",
                "done_criteria": [],
            },
        )

        # Run reap
        qgh._reap()

        fleet = qgh.load_fleet(qgh.STATE)
        stopped = [a for a in fleet["agents"] if a.get("status") == "stopped"]
        self.assertEqual(len(stopped), 0, "stopped agents must be pruned after reap")
        # The running agent (pid 99999) was also reaped because it is not alive,
        # but the key assertion is that NO stopped agents remain in FLEET.json.


if __name__ == "__main__":
    unittest.main()
