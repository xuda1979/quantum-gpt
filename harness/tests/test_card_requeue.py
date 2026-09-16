"""C-0032: the dep-deadlock requeue path.

RED (measured 2026-09-16): a 3rd-strike bounce is terminal in release_card
and _deps_satisfied only passes on dep status=="done", so every ready card
gated on a bounced dep is undispatchable FOREVER (measured claimable=0 on
the live board; the planner then mints an identical idle card every tick).
These tests pin the only exit: an explicit requeue (bounced->ready,
bounce_count preserved, fail-closed on non-bounced ids) that is DURABLE
against the reaper exhausted-retries tripwire -- without that, the next
tick would convert the requeue into an unrecoverable dead card.

CLI-level tests run qgh.py as a subprocess against an isolated
QGH_STATE_DIR; the live harness state is never touched and qgh.STATE is
never bound inside this process (keeps test_integration binding intact).
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
REPO = os.path.dirname(HARNESS_DIR)
sys.path.insert(0, HARNESS_DIR)
import harness_lib as H  # noqa: E402


def make_card(**kw):
    base = dict(title="t", lane="fixer", why="w", acceptance=["a"])
    base.update(kw)
    return H.new_card(**base)


def bounce_three_times(card):
    for _ in range(3):
        H.release_card(card, "bounced", "x", "no evidence")
    assert card["status"] == "bounced" and card["bounce_count"] == 3


def mkq(*cards):
    q = {"cards": [], "seq": 0}
    for c in cards:
        H.add_card(q, c)
    return q


class TestRequeuePath(unittest.TestCase):
    def test_bounced_dep_blocks_ready_child_and_requeue_is_the_exit(self):
        dep = make_card(title="dep")
        bounce_three_times(dep)
        q = mkq(dep)  # add_card assigns the id BEFORE the child references it
        child = make_card(title="child", deps=[dep["id"]])
        H.add_card(q, child)
        # TODAY (the deadlock): the ready child is undispatchable on its
        # bounced dep, and the bounced dep itself is undispatchable.
        self.assertEqual(H.ready_cards(q), [])
        # the requeue path: bounced -> ready, bounce history preserved
        ok, reason = H.requeue_card(q, dep["id"])
        self.assertTrue(ok, reason)
        self.assertEqual(dep["status"], "ready")
        self.assertEqual(dep["bounce_count"], 3)  # preserved, never laundered
        self.assertIsNone(dep["claimed_by"])
        self.assertIsNotNone(dep.get("requeued_utc"))
        # the requeued dep is now claimable...
        self.assertIn(dep, H.ready_cards(q))
        # ...and once it completes, the child unblocks (deps still mean done;
        # a requeue must never fake a dep completion)
        dep["status"] = "done"
        self.assertEqual([c["id"] for c in H.ready_cards(q)], [child["id"]])

    def test_requeue_refuses_non_bounced_and_missing(self):
        ready = make_card()
        done = make_card()
        done["status"] = "done"
        running = make_card()
        running["status"] = "running"
        dead = make_card()
        dead["status"] = "dead"
        q = mkq(ready, done, running, dead)
        for card in (ready, done, running, dead):
            ok, reason = H.requeue_card(q, card["id"])
            self.assertFalse(ok, card["status"] + " must be refused: " + reason)
        # statuses unchanged after the refusals
        self.assertEqual(ready["status"], "ready")
        self.assertEqual(done["status"], "done")
        self.assertEqual(running["status"], "running")
        self.assertEqual(dead["status"], "dead")
        ok, _ = H.requeue_card(q, "C-9999")
        self.assertFalse(ok)

    def test_requeue_refuses_ambiguous_duplicate_id(self):
        # the C-0021 incident class: a duplicated id must never be mutated
        # via find_card-first-match (the requeue could hit the wrong card)
        a = make_card()
        bounce_three_times(a)
        b = make_card()
        bounce_three_times(b)
        q = mkq(a, b)
        b["id"] = a["id"]  # collide INSIDE the queue (ids are assigned by add_card)
        ok, reason = H.requeue_card(q, a["id"])
        self.assertFalse(ok)
        self.assertIn("ambiguous", reason)
        self.assertEqual(a["status"], "bounced")
        self.assertEqual(b["status"], "bounced")


def run_cli(state, *args):
    env = dict(os.environ)
    env["QGH_STATE_DIR"] = state
    return subprocess.run(
        [sys.executable, os.path.join(HARNESS_DIR, "qgh.py")] + list(args),
        capture_output=True,
        text=True,
        env=env,
        cwd=REPO,
        timeout=120,
    )


def read_events(state):
    path = os.path.join(state, "EVENTS.jsonl")
    if not os.path.exists(path):
        return []  # a fully-refused run legitimately writes no events
    with open(path, encoding="utf-8") as f:
        return [json.loads(ln) for ln in f if ln.strip()]


class TestRequeueCli(unittest.TestCase):
    """End-to-end through the real CLI against an isolated state dir."""

    def setUp(self):
        self.state = tempfile.mkdtemp(prefix="qgh-requeue-cli-")
        q = {"cards": [], "seq": 0}
        dep = make_card(title="dep")
        bounce_three_times(dep)
        H.add_card(q, dep)
        other = make_card(title="never-bounced")
        H.add_card(q, other)
        self.bounced_id = dep["id"]
        self.ready_id = other["id"]
        H.save_queue(self.state, q)

    def test_cli_requeues_bounced_and_appends_event(self):
        r = run_cli(self.state, "card", "requeue", self.bounced_id)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        q = H.load_queue(self.state)
        card = H.find_card(q, self.bounced_id)
        self.assertEqual(card["status"], "ready")
        self.assertEqual(card["bounce_count"], 3)
        requeued = [e for e in read_events(self.state) if e.get("kind") == "card_requeued"]
        self.assertEqual(len(requeued), 1)
        self.assertEqual(requeued[0].get("card"), self.bounced_id)
        self.assertEqual(requeued[0].get("bounce_count"), 3)

    def test_cli_refuses_non_bounced_fail_closed(self):
        r = run_cli(self.state, "card", "requeue", self.ready_id)
        self.assertEqual(r.returncode, 1, r.stdout)
        q = H.load_queue(self.state)
        self.assertEqual(H.find_card(q, self.ready_id)["status"], "ready")
        self.assertEqual(
            [e for e in read_events(self.state) if e.get("kind") == "card_requeued"], []
        )


class TestRequeueSurvivesReaperTripwire(unittest.TestCase):
    """reap exhausted-retries tripwire (ready + bounce_count>2 -> dead) must
    NOT re-kill a requeued card on the next tick: ticks fire every 10 min,
    and bounced->dead would make the requeue unrecoverable (requeue refuses
    non-bounced ids). A ready bc>2 card that was NEVER requeued still dies
    -- no existing behavior is weakened."""

    def setUp(self):
        self.state = tempfile.mkdtemp(prefix="qgh-requeue-reap-")
        q = {"cards": [], "seq": 0}
        self.manual = make_card(title="bounced-then-ready, never requeued")
        bounce_three_times(self.manual)
        self.manual["status"] = "ready"  # synthetic: the tripwire input shape
        H.add_card(q, self.manual)
        self.requeued = make_card(title="bounced, then requeued")
        bounce_three_times(self.requeued)
        H.add_card(q, self.requeued)
        ok, reason = H.requeue_card(q, self.requeued["id"])
        assert ok, reason
        H.save_queue(self.state, q)
        H.save_json(os.path.join(self.state, "FLEET.json"), {"agents": []})
        H.save_json(
            os.path.join(self.state, "OPS.json"),
            {"consecutive_spawn_failures": 0, "backoff_until_utc": None},
        )

    def test_requeued_card_survives_reap_unstamped_card_dies(self):
        r = run_cli(self.state, "reap")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        q = H.load_queue(self.state)
        self.assertEqual(
            H.find_card(q, self.manual["id"])["status"],
            "dead",
            "non-requeued exhausted card must still trip the reaper",
        )
        self.assertEqual(
            H.find_card(q, self.requeued["id"])["status"],
            "ready",
            "a requeued card must survive the next reap",
        )


if __name__ == "__main__":
    unittest.main()
