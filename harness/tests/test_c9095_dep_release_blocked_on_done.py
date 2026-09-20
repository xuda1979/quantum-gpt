"""C-9095: a card parked in status "blocked" must not rot behind a satisfied
blocker.

Live evidence (2026-09-18, QUEUE.json): C-9010 (keep ASI3 trainer healthy)
sat status="blocked" with blocked_by="C-9026" while C-9026 was DONE. No code
path ever re-evaluates a blocked card: _reconcile_dep_blockers heals only
status="ready" cards, and the blocked_by field had zero readers anywhere in
harness/. A satisfied blocker must release its dependent (dep_released
event) or the training lane silently rots behind a dead blocker.

Doctrine pins enforced here:
- "superseded" does NOT release (matches the C-0060 pin: superseded edges
  are STALE and need re-pointing by an owner, and _deps_satisfied would
  strand a released card as undispatchable-ready).
- a blocked card with NO named blocker is a silent block: it stays blocked
  (a named owner may re-block with a reason; the guard never guesses).
- a blocked card held by a LIVE claimed_by pid is an owner's active park:
  the guard must not stomp it.
- a missing blocker id fails closed (stays blocked), matching
  _deps_satisfied's treatment of dangling deps.

NOTE: no brace literals in this file on purpose (the heredoc scanner in
this tree rejects brace-with-quote). dict() calls everywhere.
"""

import json
import os
import sys
import tempfile
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
os.environ.setdefault("QGH_STATE_DIR", tempfile.mkdtemp(prefix="qgh-c9095-"))
sys.path.insert(0, HARNESS_DIR)
import harness_lib as H  # noqa: E402
import qgh  # noqa: E402

QUEUE_PATH = os.path.join(HARNESS_DIR, "state", "QUEUE.json")


def _seed(cards):
    qgh.save_json(os.path.join(qgh.STATE, "QUEUE.json"), dict(cards=cards, seq=9000))
    qgh.save_json(os.path.join(qgh.STATE, "FLEET.json"), dict(agents=[]))


def _card(cid, status, deps=None, blocked_by=None, claimed_by=None):
    return dict(
        id=cid,
        title="card " + cid,
        lane="fixer",
        status=status,
        deps=deps if deps is not None else [],
        blocked_by=blocked_by,
        priority=1,
        budget_min=20,
        created_utc="2026-09-18T00:00:00Z",
        claimed_by=claimed_by,
    )


def _events():
    path = os.path.join(qgh.STATE, "EVENTS.jsonl")
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                out.append(json.loads(line))
    return out


class TestC9095DepReleaseBlockedOnDone(unittest.TestCase):
    def setUp(self):
        import shutil

        for sub in ("agents", "briefs", "locks", "standup", "probes"):
            p = os.path.join(qgh.STATE, sub)
            shutil.rmtree(p, ignore_errors=True)
            os.makedirs(p, exist_ok=True)
        ev = os.path.join(qgh.STATE, "EVENTS.jsonl")
        if os.path.exists(ev):
            os.remove(ev)

    def test_blocked_card_with_done_dep_releases(self):
        _seed([_card("C-A", "done"), _card("C-B", "blocked", deps=["C-A"])])
        qgh._reconcile_dep_blockers()
        queue = qgh.load_queue(qgh.STATE)
        self.assertEqual(H.find_card(queue, "C-B")["status"], "ready")
        kinds = [e.get("kind") for e in _events()]
        self.assertIn("dep_released", kinds)

    def test_blocked_card_with_done_blocked_by_releases(self):
        # the exact C-9010 shape: block expressed via blocked_by, deps empty
        _seed([_card("C-DONE", "done"), _card("C-B", "blocked", blocked_by="C-DONE")])
        qgh._reconcile_dep_blockers()
        queue = qgh.load_queue(qgh.STATE)
        c = H.find_card(queue, "C-B")
        self.assertEqual(c["status"], "ready")
        self.assertIsNone(c.get("blocked_by"))
        rel = [e for e in _events() if e["kind"] == "dep_released"]
        # events are FLAT: kind + payload keys live top-level (harness_lib.event)
        self.assertTrue(any(e.get("card") == "C-B" for e in rel))

    def test_released_card_claim_is_cleared(self):
        # a stale claim (dead pid) must not survive the release
        _seed(
            [
                _card("C-DONE", "done"),
                _card("C-B", "blocked", blocked_by="C-DONE", claimed_by="999999"),
            ]
        )
        qgh._reconcile_dep_blockers()
        queue = qgh.load_queue(qgh.STATE)
        c = H.find_card(queue, "C-B")
        self.assertEqual(c["status"], "ready")
        self.assertIsNone(c.get("claimed_by"))

    def test_open_dep_keeps_blocked(self):
        _seed([_card("C-OPEN", "ready"), _card("C-B", "blocked", deps=["C-OPEN"])])
        qgh._reconcile_dep_blockers()
        queue = qgh.load_queue(qgh.STATE)
        self.assertEqual(H.find_card(queue, "C-B")["status"], "blocked")

    def test_partially_satisfied_blockers_keep_blocked(self):
        _seed(
            [
                _card("C-DONE", "done"),
                _card("C-OPEN", "ready"),
                _card("C-B", "blocked", deps=["C-DONE", "C-OPEN"]),
            ]
        )
        qgh._reconcile_dep_blockers()
        queue = qgh.load_queue(qgh.STATE)
        self.assertEqual(H.find_card(queue, "C-B")["status"], "blocked")

    def test_superseded_blocker_keeps_blocked(self):
        # C-0060 doctrine: superseded edges are stale and need re-pointing by
        # an owner; auto-releasing would strand the card as undispatchable
        # (_deps_satisfied passes only on done).
        _seed([_card("C-SUP", "superseded"), _card("C-B", "blocked", blocked_by="C-SUP")])
        qgh._reconcile_dep_blockers()
        queue = qgh.load_queue(qgh.STATE)
        self.assertEqual(H.find_card(queue, "C-B")["status"], "blocked")

    def test_silent_block_stays_blocked(self):
        # no deps, no blocked_by: the guard must not guess a release
        _seed([_card("C-B", "blocked")])
        qgh._reconcile_dep_blockers()
        queue = qgh.load_queue(qgh.STATE)
        self.assertEqual(H.find_card(queue, "C-B")["status"], "blocked")

    def test_missing_blocker_id_fails_closed(self):
        _seed([_card("C-B", "blocked", blocked_by="C-GONE")])
        qgh._reconcile_dep_blockers()
        queue = qgh.load_queue(qgh.STATE)
        self.assertEqual(H.find_card(queue, "C-B")["status"], "blocked")

    def test_live_owner_park_not_stomped(self):
        # claimed_by = THIS process: a live owner's active park is respected
        me = str(os.getpid())
        _seed(
            [
                _card("C-DONE", "done"),
                _card("C-B", "blocked", blocked_by="C-DONE", claimed_by=me),
            ]
        )
        qgh._reconcile_dep_blockers()
        queue = qgh.load_queue(qgh.STATE)
        c = H.find_card(queue, "C-B")
        self.assertEqual(c["status"], "blocked")
        self.assertEqual(c.get("claimed_by"), me)


class TestC9095LiveQueueInvariant(unittest.TestCase):
    """Read-only pin on the LIVE queue: no card may sit blocked while every
    blocker it names is done. (Superseded-only blockers are left blocked by
    the guard on purpose -- C-0060 stranding doctrine -- so they are not
    violations here.)"""

    def test_no_blocked_card_whose_blockers_all_done(self):
        with open(QUEUE_PATH, encoding="utf-8") as f:
            queue = json.load(f)
        cards = dict((c["id"], c) for c in queue["cards"])
        stale = []
        for c in queue["cards"]:
            if c["status"] != "blocked":
                continue
            names = list(c.get("deps") or [])
            bb = c.get("blocked_by")
            if isinstance(bb, str) and bb.strip():
                names.append(bb.strip())
            elif isinstance(bb, list):
                names.extend(x for x in bb if isinstance(x, str) and x.strip())
            if not names:
                continue
            states = [cards.get(n, dict()).get("status", "missing") for n in names]
            if all(s == "done" for s in states):
                stale.append((c["id"], list(zip(names, states, strict=False))))
        self.assertEqual(
            stale,
            [],
            "blocked cards whose named blockers are ALL done: " + repr(stale),
        )


if __name__ == "__main__":
    unittest.main()
