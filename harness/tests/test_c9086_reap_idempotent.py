"""C-9086: reap idempotency -- the reaper must never re-emit a reaped event
for an already-reaped (card, dispatched pid).

Live evidence: EVENTS.jsonl re-emitted identical reaped lines for
C-9063/9066/9071/9073/9076/9078 ~15x from 02:20-04:23Z (two emitters at
both :00 and :05), and throughput done(940) exceeded dispatched(567) --
a fleet row resurrected to "running" by a concurrent writer's lost update
gets re-harvested every tick: duplicate reaped events, double-counted DONE
throughput, re-released cards. The second reap pass over the same
(card, pid) must be a no-op. A NEW incarnation (new pid) of the same card
must still reap normally -- the key is (card, pid), never card alone."""

import json
import os
import sys
import tempfile
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
os.environ.setdefault("QGH_STATE_DIR", tempfile.mkdtemp(prefix="qgh-c9086-"))
sys.path.insert(0, HARNESS_DIR)
import harness_lib as H  # noqa: E402
import qgh  # noqa: E402
from test_integration import running_agent, seed_card, wait_exit  # noqa: E402


def reaped_events(card_id):
    out = []
    path = os.path.join(qgh.STATE, "EVENTS.jsonl")
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if e.get("kind") == "reaped" and e.get("card") == card_id:
                out.append(e)
    return out


def resurrect(agent_pid, card_id="C-9086"):
    """Simulate the live failure: a concurrent writer's stale fleet write
    puts an already-reaped row back to status "running" (same card+pid).
    C-9508: stopped agents are pruned after reap, so re-add the entry
    to simulate a concurrent writer racing the prune."""
    fleet = qgh.load_fleet(qgh.STATE)
    found = False
    for a in fleet["agents"]:
        if a["pid"] == agent_pid:
            a["status"] = "running"
            found = True
    if not found:
        # Pruned by C-9508; re-add the row as running (concurrent writer simulation)
        fleet["agents"].append({
            "pid": agent_pid,
            "card": card_id,
            "lane": "fixer",
            "status": "running",
            "log": os.path.join(qgh.STATE, "agents", card_id + ".log"),
        })
    qgh.save_fleet(qgh.STATE, fleet)


class TestC9086ReapIdempotent(unittest.TestCase):
    def setUp(self):
        import shutil

        for sub in ("agents", "briefs", "locks", "standup", "probes"):
            p = os.path.join(qgh.STATE, sub)
            shutil.rmtree(p, ignore_errors=True)
            os.makedirs(p, exist_ok=True)
        # qgh.STATE binds once per pytest process (test_integration.py:15
        # overwrites QGH_STATE_DIR), so EVENTS.jsonl is shared across every
        # module in the run -- truncate it or reaped-event counts pick up
        # events written by OTHER modules' reaps.
        open(os.path.join(qgh.STATE, "EVENTS.jsonl"), "w").close()
        qgh.save_json(os.path.join(qgh.STATE, "QUEUE.json"), dict(cards=[], seq=9000))
        qgh.save_json(os.path.join(qgh.STATE, "FLEET.json"), dict(agents=[]))
        qgh.save_json(
            os.path.join(qgh.STATE, "OPS.json"),
            dict(consecutive_spawn_failures=0, backoff_until_utc=None),
        )

    def test_resurrected_row_second_reap_is_noop(self):
        c = seed_card()
        _entry, _log, proc = running_agent(c, "echo RESULT: DONE\n")
        self.addCleanup(proc.kill)
        self.addCleanup(proc.wait)
        wait_exit(proc)
        qgh._reap()  # first pass: the legit reap
        self.assertEqual(len(reaped_events(c["id"])), 1, "first reap emits exactly one event")
        q = qgh.load_queue(qgh.STATE)
        self.assertEqual(H.find_card(q, c["id"])["status"], "done")
        # the lost-update resurrection
        resurrect(proc.pid, c["id"])
        qgh._reap()  # second pass over the same (card, pid)
        self.assertEqual(
            len(reaped_events(c["id"])),
            1,
            "reaping the same (card, pid) twice must emit exactly ONE reaped event",
        )
        fleet = qgh.load_fleet(qgh.STATE)
        rows = [a for a in fleet["agents"] if a["pid"] == proc.pid]
        # C-9508: stopped agents are pruned, so the row is gone (no stale row to linger)
        if rows:
            self.assertEqual(rows[0]["status"], "stopped", "stale row must not linger as running")
        # else: pruned -- even better, no stale row exists
        q = qgh.load_queue(qgh.STATE)
        card = H.find_card(q, c["id"])
        self.assertEqual(card["status"], "done", "second pass must not touch the card")

    def test_new_incarnation_same_card_still_reaps(self):
        c = seed_card()
        _e1, _l1, p1 = running_agent(c, "echo RESULT: DONE\n")
        self.addCleanup(p1.kill)
        self.addCleanup(p1.wait)
        wait_exit(p1)
        qgh._reap()
        # second incarnation: same card, NEW pid (re-claim + fresh dispatch)
        q = qgh.load_queue(qgh.STATE)
        H.claim_card(q, c["id"], "redispatch")
        qgh.save_queue(qgh.STATE, q)
        _e2, _l2, p2 = running_agent(c, "echo working\n")  # dies with no RESULT
        self.addCleanup(p2.kill)
        self.addCleanup(p2.wait)
        wait_exit(p2)
        qgh._reap()
        self.assertEqual(
            len(reaped_events(c["id"])),
            2,
            "a NEW incarnation (new pid) of the same card must still reap",
        )


if __name__ == "__main__":
    unittest.main()
