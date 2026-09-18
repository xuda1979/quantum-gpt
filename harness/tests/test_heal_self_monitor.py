"""Self-monitoring heal: detect a true tick HALT and self-correct.

RED (measured 2026-09-18): the live harness halted for 19h because every tick
crashed in _reap() (AttributeError on a half-landed rearm_ghost_running_cards
call). tick.log stayed fresh (launchd redirect caught the tracebacks) but
STATUS.md -- only appended on a SUCCESSFUL tick -- went stale, and 6 zombie
fleet entries blocked all dispatch. The old cmd_heal only broke a wedged tick
lock and never noticed the loop was dead. Heal must detect the stale-success
signal (no successful tick in SUCCESS_STALE_SEC) and clear zombies so a fresh
tick can dispatch.
"""

import os
import sys
import time
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
sys.path.insert(0, HARNESS_DIR)
import harness_lib as H  # noqa: E402
import qgh  # noqa: E402


def _make_card(cid, status="ready", **extra):
    c = H.new_card(card_id=cid, title="t", lane="fixer", why="w", acceptance=["a"])
    c["status"] = status
    c.update(extra)
    return c


class TestHealSelfMonitor(unittest.TestCase):
    def setUp(self):
        import shutil

        for sub in ("agents", "briefs", "locks", "standup", "probes"):
            p = os.path.join(qgh.STATE, sub)
            shutil.rmtree(p, ignore_errors=True)
            os.makedirs(p, exist_ok=True)
        qgh.save_json(os.path.join(qgh.STATE, "QUEUE.json"), {"cards": [], "seq": 0})
        qgh.save_json(os.path.join(qgh.STATE, "FLEET.json"), {"agents": []})
        qgh.save_json(
            os.path.join(qgh.STATE, "OPS.json"),
            {"consecutive_spawn_failures": 0, "backoff_until_utc": None},
        )

    def _set_status_age(self, stale):
        p = os.path.join(qgh.STATE, "STATUS.md")
        with open(p, "w") as f:
            f.write("- stale tick#0\n")
        if stale:
            ts = time.time() - (qgh.SUCCESS_STALE_SEC + 600)
            os.utime(p, (ts, ts))

    def _seed_zombie(self):
        card = _make_card(
            "C-Z",
            status="running",
            claimed_by="9",
            claimed_utc="2026-09-17T09:00:00Z",
            deadline_utc="2026-09-17T09:25:00Z",
            bounce_count=1,
        )
        qgh.save_json(os.path.join(qgh.STATE, "QUEUE.json"), {"cards": [card], "seq": 1})
        qgh.save_json(
            os.path.join(qgh.STATE, "FLEET.json"),
            {
                "agents": [
                    dict(
                        pid=999999,
                        card="C-Z",
                        lane="fixer",
                        status="running",
                        lstart="Mon Jan  1 00:00:00 2024",
                        started_utc="2026-09-17T09:00:00Z",
                    )
                ]
            },
        )

    def test_halt_detected_and_zombies_cleared(self):
        self._set_status_age(stale=True)
        self._seed_zombie()
        # mock self_spawn so heal does not actually spawn subprocesses
        spawns = []
        real = qgh.self_spawn
        qgh.self_spawn = lambda args: spawns.append(args)
        try:
            qgh.cmd_heal(None)
        finally:
            qgh.self_spawn = real
        # zombie must be reaped: card re-armed to ready, fleet cleared
        q = qgh.load_queue(qgh.STATE)
        c = H.find_card(q, "C-Z")
        self.assertEqual(c["status"], "ready", "halt heal must re-arm zombie card")
        self.assertIsNone(c["claimed_by"])
        f = qgh.load_fleet(qgh.STATE)
        self.assertEqual(
            [a for a in f["agents"] if a["status"] == "running"],
            [],
            "halt heal must clear zombie fleet entries",
        )
        # a heal_halt_detected event was recorded
        events = [ln for ln in open(os.path.join(qgh.STATE, "EVENTS.jsonl"))]
        self.assertTrue(
            any("heal_halt_detected" in ln for ln in events), "heal must log the halt detection"
        )

    def test_no_halt_when_recent_success(self):
        self._set_status_age(stale=False)  # fresh STATUS.md
        self._seed_zombie()
        real = qgh.self_spawn
        qgh.self_spawn = lambda args: None
        try:
            qgh.cmd_heal(None)
        finally:
            qgh.self_spawn = real
        # NOT halted -> zombie left in place (heal does not reap on a healthy loop)
        q = qgh.load_queue(qgh.STATE)
        c = H.find_card(q, "C-Z")
        self.assertEqual(c["status"], "running", "no halt -> no forced reap")


if __name__ == "__main__":
    unittest.main()
