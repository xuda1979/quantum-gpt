"""C-9056: dep re-baseline v7 -- re-point the v2-era shells C-0015 and
C-0016 onto the canonical spine.

RED (measured 2026-09-17 ~06:05Z against the live QUEUE.json + EVENTS
grep): C-0015(ready)->C-0029(bounced) and C-0016(ready)->C-0051
(bounced) are non-environmental terminal deps -- the exact precondition
of harness/qgh.py _reconcile_dep_blockers (:813-843): a bounced dep
whose bounce_reason+result match none of ENV_BOUNCE_SIGNATURES (:756)
can never be re-armed and can never reach done (_deps_satisfied passes
only on status=="done"), so dead_dep_escalated fires EVERY tick.
Measured: 55 dead_dep_escalated events in harness/state/EVENTS.jsonl,
every one blockers=["C-0029","C-0051"], latest 2026-09-16T22:03:09Z --
and each fire also spends an _auto_plan mint. Full-queue sweep: these
are the ONLY two live violations (C-9038 is ready, so C-9016 is clean).

Why re-point and not retire: v4 (test_dep_graph_rebaseline_v4_p1_shells)
pins C-0015 and C-0016 as LIVE shells -- not dead/superseded -- so the
fail-closed retire arm of the C-9056 acceptance is closed for these two
cards; the edges re-point instead, with the named reason recorded on
the card (no silent edit).

- C-0015 -> C-9009: the canonical sha-pinned adapter re-eval (the goal
  object, C-9035 spine). C-0029 is twice-refuted: the Mac v2 path is
  INFEASIBLE (C-0065, probes/mac_lora_feasibility.md verdict v2) and
  its C-0042 console-cure dep has no live owner (C-9028 bounce) -- the
  edge can never resolve. The v1 pin test_C0015_dep_repointed_to_C0029
  (C-0065) is amended in place with a dated comment, family precedent.
- C-0016 -> C-9011: the canonical failure-mining card (feeds C-9052
  distillation slice v3). C-0051 -- C-9028 re-point target -- is itself
  bounced terminal ("no RESULT verdict (dead)"), so the v5 pin
  test_C0016_dep_repointed_to_C0051_owner_of_C0002_mission is amended
  in place with a dated comment.
- C-9016 (independent second-leg card, DIFFERENT id) is NOT this card
  target: its spine deps stay untouched; the guard pins non-mutation.

Same binding idiom as the v1-v6 family: asserted against the LIVE
harness/state/QUEUE.json -- the queue is the source of truth, not a
fixture. The pre-fix shape is durably recorded (v1 C-0065 pin; v5
C-9028 pin; C-0029/C-0051 bounce_reasons still live on the queue; the
55 EVENTS lines), so TestDepGraphRebaselineV7RedWitness rebuilds the
fixture pair -- two shells whose deps point at bounced cards -- from
the live cards and asserts every guard FIRES there: witness stays RED
forever, live goes GREEN.
"""

import json
import os
import sys
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
sys.path.insert(0, HARNESS_DIR)

QUEUE_PATH = os.path.join(HARNESS_DIR, "state", "QUEUE.json")

# A dep target that can still reach done (or is already there).
# "blocked" is live: a blocked card is owned/ownable and may resolve.
LIVE_STATUSES = ("ready", "running", "done", "blocked")

# Mirrors harness/qgh.py ENV_BOUNCE_SIGNATURES (:756) -- the set that
# makes _reconcile_dep_blockers RE-ARM a bounced dep instead of
# escalating it as dead. Do not diverge silently: if the qgh tuple
# grows, mirror it here (no import: qgh binds STATE dirs at import).
ENV_BOUNCE_SIGNATURES = (
    "api error",
    "not logged in",
    "transport",
    "exec",
    "connection",
    "rate limit",
    "no exec path",
    "daemon",
    "booting",
    "backoff",
    "timeout",
)


def load_live_queue():
    with open(QUEUE_PATH, encoding="utf-8") as f:
        return json.load(f)


def by_id(queue):
    return dict((c["id"], c) for c in queue["cards"])


def bounce_was_environmental(dep):
    # Mirrors harness/qgh.py _bounce_was_environmental (:771).
    blob = ((dep.get("bounce_reason") or "") + " " + (dep.get("result") or "")).lower()
    return any(sig in blob for sig in ENV_BOUNCE_SIGNATURES)


# ----------------------------------------------------------- the guards
# One source of truth for the three v7 invariants (v6 idiom): live
# tests assert the guards PASS on the live queue; the witness asserts
# they FIRE on the reconstructed pre-fix fixture pair.


def guard_no_ready_card_deps_on_terminal(cards):
    # THE v7 guard: the live precondition of the every-tick
    # dead_dep_escalated loop (qgh.py _reconcile_dep_blockers :813-843).
    # A ready/running card must never dep on a card that can never
    # reach done: dead, or bounced with a non-environmental bounce
    # (env bounces are re-armed by the reconciler -- those are fine).
    bad = []
    for c in cards.values():
        if c.get("status") not in ("ready", "running"):
            continue
        for d in c.get("deps") or []:
            t = cards.get(d)
            if t is None:
                continue  # existence is v5 guard territory, not this one
            if t.get("status") == "dead":
                bad.append((c["id"], d, "dead"))
            elif t.get("status") == "bounced" and not bounce_was_environmental(t):
                bad.append((c["id"], d, "bounced-nonenv"))
    assert not bad, "ready/running cards dep on never-done cards (card, dep, why): " + repr(bad)


def guard_C0015_repoint(cards):
    # C-0015 eval handoff resolves into C-9009, the canonical sha-pinned
    # adapter re-eval. Never C-0029 (twice-refuted v2 path), never the
    # dead C-0011/C-0055 of the earlier re-baselines.
    c = cards["C-0015"]
    assert c.get("deps") == ["C-9009"], (
        "C-0015 must dep exactly on C-9009 (canonical adapter-eval outcome), got "
        + repr(c.get("deps"))
    )
    t = cards.get("C-9009")
    assert t is not None and t.get("status") in LIVE_STATUSES, (
        "C-9009 must exist and be live, got " + repr(t and t.get("status"))
    )
    reason = c.get("reason") or ""
    assert "C-9056" in reason, "re-point must cite this card in reason"
    assert "C-0029" in reason, "re-point must name the retired edge"


def guard_C0016_repoint(cards):
    # C-0016 mining resolves into C-9011, the canonical failure-mining
    # card (feeds C-9052). Never C-0051 (itself bounced terminal), never
    # the lost C-0002/C-0005 of the earlier re-baselines.
    c = cards["C-0016"]
    assert c.get("deps") == ["C-9011"], (
        "C-0016 must dep exactly on C-9011 (canonical failure mining), got " + repr(c.get("deps"))
    )
    t = cards.get("C-9011")
    assert t is not None and t.get("status") in LIVE_STATUSES, (
        "C-9011 must exist and be live, got " + repr(t and t.get("status"))
    )
    reason = c.get("reason") or ""
    assert "C-9056" in reason, "re-point must cite this card in reason"
    assert "C-0051" in reason, "re-point must name the retired edge"


def guard_C9016_untouched(cards):
    # C-9016 is the independent SECOND-LEG card -- a different id from
    # C-0016. This re-baseline must not mutate it: it keeps its live
    # spine and carries no C-9056 annotation.
    c = cards["C-9016"]
    assert c.get("status") == "ready", "C-9016 must stay ready, got " + repr(c.get("status"))
    assert "C-9056" not in (
        c.get("reason") or ""
    ), "C-9016 must carry no C-9056 re-baseline note (different card)"
    for d in c.get("deps") or []:
        t = cards.get(d)
        assert t is not None and t.get("status") in LIVE_STATUSES, (
            "C-9016 dep must stay live, got " + d + "=" + repr(t and t.get("status"))
        )


GUARDS = (
    ("no-terminal-dep", guard_no_ready_card_deps_on_terminal),
    ("C-0015-repoint", guard_C0015_repoint),
    ("C-0016-repoint", guard_C0016_repoint),
    ("C-9016-untouched", guard_C9016_untouched),
)


class TestDepGraphRebaselineV7CanonicalSpineShells(unittest.TestCase):
    def setUp(self):
        _existing = set(c["id"] for c in load_live_queue().get("cards", []))
        _required = {
            "C-0002",
            "C-0005",
            "C-0011",
            "C-0015",
            "C-0016",
            "C-0029",
            "C-0042",
            "C-0051",
            "C-0055",
            "C-0065",
        }
        _missing = _required - _existing
        if _missing:
            self.skipTest("historical cards purged: " + str(sorted(_missing)[:5]))
        self.assertTrue(os.path.exists(QUEUE_PATH), "QUEUE.json missing at " + QUEUE_PATH)
        self.q = load_live_queue()
        self.cards = by_id(self.q)

    def test_no_ready_card_deps_on_never_done_card(self):
        guard_no_ready_card_deps_on_terminal(self.cards)

    def test_C0015_repointed_to_C9009_canonical_eval(self):
        guard_C0015_repoint(self.cards)

    def test_C0016_repointed_to_C9011_canonical_mining(self):
        guard_C0016_repoint(self.cards)

    def test_C9016_second_leg_untouched(self):
        guard_C9016_untouched(self.cards)

    def test_repoint_targets_still_on_their_own_spine(self):
        # The re-point must land on the C-9035 canonical spine, not on
        # another shell: C-9009 keeps C-9030 live, C-9011 -> C-9009.
        self.assertIn("C-9030", self.cards["C-9009"].get("deps") or [])
        self.assertEqual(self.cards["C-9011"].get("deps"), ["C-9009"])


# ------------------------------------------------------------ RED witness
# The pre-fix live shape is consumed by this card own fix, and
# regressing a shared live queue to re-measure it is off-limits
# (concurrent sessions read this tree -- the v6 precedent). The witness
# rebuilds the fixture pair from durable evidence and asserts every
# guard FIRES there. Sources: C-0015->C-0029 was pinned live by the v1
# C-0065 amendment; C-0016->C-0051 by the v5 C-9028 pin; C-0029 and
# C-0051 keep their bounce records on the live queue; 55
# dead_dep_escalated EVENTS lines record the every-tick loop.


class TestDepGraphRebaselineV7RedWitness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _existing = set(c["id"] for c in load_live_queue().get("cards", []))
        _required = {
            "C-0002",
            "C-0005",
            "C-0011",
            "C-0015",
            "C-0016",
            "C-0029",
            "C-0042",
            "C-0051",
            "C-0055",
            "C-0065",
        }
        _missing = _required - _existing
        if _missing:
            raise unittest.SkipTest("historical cards purged: " + str(sorted(_missing)[:5]))
        cls.live = by_id(load_live_queue())
        fx = json.loads(json.dumps(cls.live))  # deep copy; live never touched
        # rewind the two re-pointed edges to their recorded pre-fix shape
        fx["C-0015"]["deps"] = ["C-0029"]
        fx["C-0016"]["deps"] = ["C-0051"]
        cls.fx = fx

    def test_fixture_pair_mirrors_recorded_prefix_shape(self):
        self.assertEqual(self.fx["C-0015"]["deps"], ["C-0029"])
        self.assertEqual(self.fx["C-0016"]["deps"], ["C-0051"])
        self.assertEqual(self.fx["C-0029"]["status"], "bounced")
        self.assertEqual(self.fx["C-0051"]["status"], "bounced")
        # both bounces are NON-environmental -> the escalator dead path
        self.assertFalse(bounce_was_environmental(self.fx["C-0029"]))
        self.assertFalse(bounce_was_environmental(self.fx["C-0051"]))

    def test_prefix_shape_guards_fire_on_fixture_pair(self):
        # The three PRE-FIX-shape guards must fire; C-9016-untouched is
        # a non-mutation guard and legitimately held pre-fix too.
        fired = []
        for name, guard in GUARDS:
            if name == "C-9016-untouched":
                guard(self.fx)  # must NOT fire
                continue
            with self.assertRaises(
                AssertionError, msg="guard " + name + " did not fire on the fixture pair"
            ):
                guard(self.fx)
            fired.append(name)
        self.assertEqual(fired, ["no-terminal-dep", "C-0015-repoint", "C-0016-repoint"])

    def test_witness_never_touches_live_queue(self):
        self.assertIsNot(self.fx, self.live)
        self.assertEqual(self.fx["C-0015"]["deps"], ["C-0029"])
        self.assertEqual(self.fx["C-0016"]["deps"], ["C-0051"])


if __name__ == "__main__":
    unittest.main()
