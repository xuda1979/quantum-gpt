"""C-9035: dep re-baseline v6 -- un-deadlock the adapter-verdict spine.

RED (measured 2026-09-17 ~21:15Z against the live QUEUE.json, 98 cards):
C-9009 -- the goal's object (fail-closed re-eval of the newest adapter
checkpoint; GOAL.json done_criteria #1/#2) -- sits blocked with
deps ['C-9008', 'C-9003'], and BOTH deps are bounced with no owner:
- C-9008 (box assessment): bounce_count=3, bounce_reason 'no RESULT
  verdict (dead)'; its re-measure heir C-9018 is ALSO bounced (dep
  C-0037). harness_lib._deps_satisfied passes only on status=='done',
  so the edge can never resolve.
- C-9003 (canonical base leg): bounced, launch/collect-superseded by
  C-9029/C-9030 (live: C-9024 done, C-9029 running, C-9030 ready);
  C-9003's own result points the verdict phase at C-9030 via the
  c9003_base_leg_handoff contract.
After the base leg lands, the queue deadlocks one round short of the
objective (the C-0070 no-progress class). v5's dep-existence guard
cannot see this: C-9008/C-9003 both EXIST as ids -- they just can
never reach done.

Fixes, on evidence (smallest change per card):
- C-9009.deps: ['C-9008','C-9003'] -> ['C-9030'] (C-9003's named
  supersessor; live dep chain C-9024 done + C-9029 running). The
  newest-checkpoint question C-9008 was to answer is UNMEASURABLE
  while the box /exec wedge persists (C-9018: 4 consecutive failing
  windows, B-324 console-gated) and C-9009's own fail-closed leg
  protocol resolves the newest checkpoint at eval time -- the dep is
  removed, not re-pointed. C-9009 stays blocked: re-ready is C-9020's
  two-probe same-pid gate, not this card's call.
- C-9008: deadded (status=dead, C-9012 precedent), reason in result:
  3-bounce terminal, mission unmeasurable under the B-324 wedge,
  residual decision owned by C-9009 at leg time.
- C-9005 (duplicate-mission canonical re-score of step_000097):
  reconciled into the C-9009 lineage -- status=superseded with the
  supersession note in result (C-9012 precedent via C-0010, the prior
  duplicate re-score retire). C-9009 re-evals the newest checkpoint,
  covering the s97 re-score mission when s97 is newest; the note
  names that lineage. Gates preserved.

Same binding idiom as the v1-v5 family: asserted against the LIVE
harness/state/QUEUE.json -- the queue is the source of truth, not a
fixture. Older family members asserting the deadlocked edges (v3
C-9009 deps, v4 C-9005 live-shell) are amended in place with dated
comments -- the v1/C-9028 precedent. Out-of-scope bounced-dep edges
(C-0015->C-0029, C-0016->C-0051, C-9004->C-9008) are NOT this card's
scope; the live-dep invariant here is scoped to the C-9009 spine.

RED-witness addendum (C-9035 re-claim, 2026-09-17 ~21:35Z): the first
attempt re-baselined the live queue BEFORE landing durable evidence in
the card result -- its bounce_reason is exactly that -- so the live RED
state is consumed, and regressing a shared live queue to re-measure it
is off-limits (concurrent sessions read this tree).
TestDepGraphRebaselineV6RedWitness therefore rebuilds the RECORDED
pre-fix shape from durable evidence (C-9035 card title/why;
EVENTS.jsonl dep_blocker_requeued blocker=C-9008 @19:30:00Z and
blocker=C-9003 @19:42:55Z, both unblocks=C-9009; C-9008 at
bounce_count=3, status bounced) and asserts every guard FIRES there.
Witness-RED + live-GREEN is the honest RED->GREEN pair still
available. In the same edit the four invariants were refactored into
module-level guard functions so the witness cannot drift from the
live asserts (one source of truth).

Re-baseline addendum (C-9055, 2026-09-17): the exact-shape pin moved
['C-9030'] -> ['C-9030', 'C-9038']. C-9042 added the C-9038 dep
deliberately at 21:36:14Z (EVENTS.jsonl, "serialize adapter legs
behind truncation fix") minutes after this file pinned the singleton
shape -- concurrent-session drift; C-9038 is live (ready, deps
[C-9029]), so the dep is WANTED and the stale pin, not the queue, was
wrong. guard_spine still refuses any dead/missing id on either edge.
"""

import json
import os
import sys
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
sys.path.insert(0, HARNESS_DIR)

QUEUE_PATH = os.path.join(HARNESS_DIR, "state", "QUEUE.json")

LIVE_STATUSES = ("ready", "running", "done", "blocked")


def load_live_queue():
    with open(QUEUE_PATH, encoding="utf-8") as f:
        return json.load(f)


def by_id(queue):
    return dict((c["id"], c) for c in queue["cards"])


# ----------------------------------------------------------- the guards
# One source of truth for the four v6 invariants. Each guard raises
# AssertionError on violation: the live-queue tests below assert the
# guards PASS on the live queue; the RED-witness class asserts the
# SAME functions FIRE on the recorded pre-fix reconstruction.


def guard_spine(cards):
    # THE v6 guard, scoped to the goal's object card: a dep edge from
    # C-9009 to a bounced/dead card can never satisfy _deps_satisfied
    # (needs status=="done") and, with no owner, deadlocks the verdict
    # spine one round short of the objective.
    c = cards["C-9009"]
    bad = []
    for d in c.get("deps") or []:
        t = cards.get(d)
        if t is None:
            bad.append((d, "MISSING"))
        elif t.get("status") not in LIVE_STATUSES:
            bad.append((d, t.get("status")))
    assert not bad, "C-9009 deps on non-live cards (dep, status): " + repr(bad)


def guard_repoint(cards):
    # C-9003 -> C-9030 (its named supersessor, live chain C-9024 done
    # + C-9029 running); C-9008 removed (no live owner). Shape pinned
    # exactly so no dead id can quietly creep back in. C-9035 must NOT
    # flip C-9009's status: re-ready is C-9020's two-probe same-pid
    # gate (boot-restart loop), not this card's.
    # C-9055 reconciliation (2026-09-17): C-9042 deliberately appended
    # C-9038 AFTER this pin landed (EVENTS.jsonl 21:36:14Z, "serialize
    # adapter legs behind truncation fix"); C-9038 is live (status
    # ready, deps [C-9029], bounce_count 0) so the exact shape moves to
    # the pair below. Liveness of BOTH deps stays enforced by
    # guard_spine. The stale ['C-9030'] pin was the wrong side.
    c = cards["C-9009"]
    assert c.get("deps") == ["C-9030", "C-9038"], (
        "C-9009 must dep exactly on C-9030 (C-9003 supersessor) + "
        "C-9038 (truncation-ceiling serialize, C-9042), got " + repr(c.get("deps"))
    )
    t = cards["C-9030"]
    assert t.get("status") in ("ready", "running", "done"), (
        "C-9030 must be a live re-point target, got " + repr(t.get("status"))
    )
    assert c.get("status") == "blocked", (
        "C-9009 re-ready belongs to the C-9020 sweep gate, got " + repr(c.get("status"))
    )


def guard_deadd(cards):
    # No named live owner exists (heir C-9018 bounced too); 3-bounce
    # terminal. C-9012 precedent: dead + reason in result.
    c = cards["C-9008"]
    assert c.get("status") == "dead", (
        "C-9008 must be deadded (ownerless, 3-bounce terminal), got " + repr(c.get("status"))
    )
    result = c.get("result") or ""
    assert "C-9035" in result, "deadd reason must cite this card"
    assert "C-9009" in result, "deadd reason must name the dep owner"
    assert "B-324" in result, "deadd reason must cite the wedge evidence"


def guard_reconcile(cards):
    # Duplicate-mission canonical re-score of step_000097 reconciled
    # into C-9009 (newest-checkpoint re-eval covers s97 when s97 is
    # newest). C-9012 precedent via C-0010: superseded + note naming
    # the lineage. Gates survive (the mission, not the contract,
    # moved).
    c = cards["C-9005"]
    assert c.get("status") == "superseded", (
        "C-9005 must sit superseded into the C-9009 lineage, got " + repr(c.get("status"))
    )
    result = c.get("result") or ""
    assert "C-9009" in result, "supersession note must name the lineage"
    assert "C-9035" in result, "supersession note must cite this card"
    gates = c.get("gates") or []
    assert "eval-failclosed" in gates, "C-9005 gates must survive"
    assert "sha-verified" in gates, "C-9005 gates must survive"


GUARDS = (
    ("spine", guard_spine),
    ("repoint", guard_repoint),
    ("deadd", guard_deadd),
    ("reconcile", guard_reconcile),
)


class TestDepGraphRebaselineV6UndeadlockSpine(unittest.TestCase):
    def setUp(self):
        _existing = set(c["id"] for c in load_live_queue().get("cards", []))
        _required = {"C-0010", "C-0015", "C-0016", "C-0029", "C-0037", "C-0051", "C-0070"}
        _missing = _required - _existing
        if _missing:
            self.skipTest("historical cards purged: " + str(sorted(_missing)[:5]))
        self.assertTrue(os.path.exists(QUEUE_PATH), "QUEUE.json missing at " + QUEUE_PATH)
        self.q = load_live_queue()
        self.cards = by_id(self.q)

    def test_C9009_every_dep_is_live_or_done(self):
        guard_spine(self.cards)

    def test_C9009_deps_repointed_to_C9030_exactly(self):
        guard_repoint(self.cards)

    def test_C9008_deadded_with_reason_string(self):
        guard_deadd(self.cards)

    def test_C9005_superseded_into_C9009_lineage(self):
        guard_reconcile(self.cards)


# ------------------------------------------------------------ RED witness
# The first C-9035 attempt re-baselined the live queue BEFORE landing
# durable evidence in the card result -- its bounce_reason is exactly
# that -- so the live RED state is consumed and regressing a shared
# live queue to re-measure it is off-limits (concurrent sessions read
# this tree). The witness rebuilds the RECORDED pre-fix shape from
# durable evidence and asserts every guard FIRES there; witness-RED +
# live-GREEN is the honest RED->GREEN pair still available.
# Pre-fix shape sources (durable): C-9035 card title/why names the
# deadlocked deps ['C-9008','C-9003'] with C-9008 'bounced, no owner'
# and C-9003 superseded by C-9029/C-9030; EVENTS.jsonl line 1080
# (19:30:00Z, dep_blocker_requeued blocker=C-9008 unblocks=C-9009) and
# line 1119 (19:42:55Z, blocker=C-9003) prove both edges existed;
# C-9008 sat at bounce_count=3, status bounced. NOT durably recorded:
# C-9005's exact pre-fix status -- only 'not superseded, no lineage
# note' is load-bearing; 'ready' is the benign default used here.

PRE_FIX_C9009_DEPS = ["C-9008", "C-9003"]


def prefix_fixture(cards):
    fx = json.loads(json.dumps(cards))  # deep copy; live never touched
    fx["C-9009"]["deps"] = list(PRE_FIX_C9009_DEPS)
    fx["C-9008"]["status"] = "bounced"
    fx["C-9008"]["result"] = (
        "NEXT: C-9020 should capture the ASI2 boot-time bar breach (pre-rebaseline note)"
    )
    fx["C-9003"]["status"] = "bounced"
    fx["C-9005"]["status"] = "ready"
    fx["C-9005"]["result"] = (
        "NEXT: Coordinator note -- duplicates the C-9029/C-9030 pattern (pre-rebaseline note)"
    )
    return fx


class TestDepGraphRebaselineV6RedWitness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _existing = set(c["id"] for c in load_live_queue().get("cards", []))
        _required = {"C-0010", "C-0015", "C-0016", "C-0029", "C-0037", "C-0051", "C-0070"}
        _missing = _required - _existing
        if _missing:
            raise unittest.SkipTest("historical cards purged: " + str(sorted(_missing)[:5]))
        cls.live = by_id(load_live_queue())
        cls.fx = prefix_fixture(cls.live)

    def test_fixture_mirrors_recorded_prefix_shape(self):
        self.assertEqual(self.fx["C-9009"]["deps"], ["C-9008", "C-9003"])
        self.assertEqual(self.fx["C-9008"]["status"], "bounced")
        self.assertEqual(self.fx["C-9003"]["status"], "bounced")
        self.assertNotEqual(self.fx["C-9005"]["status"], "superseded")
        self.assertNotIn("C-9035", self.fx["C-9005"].get("result") or "")
        self.assertNotIn("C-9035", self.fx["C-9008"].get("result") or "")
        self.assertNotIn("C-9009", self.fx["C-9005"].get("result") or "")

    def test_every_guard_fires_on_prefix_fixture(self):
        fired = []
        for name, guard in GUARDS:
            with self.assertRaises(
                AssertionError, msg="guard " + name + " did not fire on the pre-fix fixture"
            ):
                guard(self.fx)
            fired.append(name)
        self.assertEqual(fired, ["spine", "repoint", "deadd", "reconcile"])

    def test_C9055_stale_singleton_pin_fires_repoint_guard(self):
        # C-9055 (2026-09-17): the consumed RED side of the dep-drift
        # reconciliation, kept durable per the C-9035 witness doctrine.
        # EVENTS.jsonl line 1447 (2026-09-16T21:36:14Z, card_deps_updated
        # by C-9042, "serialize adapter legs behind truncation fix")
        # records deps_before ["C-9030"] -> ["C-9030","C-9038"]; the
        # stale singleton pin ran RED against the live queue until the
        # pin (not the queue) was reconciled. The fixture replays that
        # shape; the guard must keep firing on it forever.
        fx = json.loads(json.dumps(self.live))
        fx["C-9009"]["deps"] = ["C-9030"]
        with self.assertRaises(AssertionError):
            guard_repoint(fx)

    def test_witness_never_touches_live_queue(self):
        # C-9055 (2026-09-17): live shape grew C-9038 via C-9042
        # (EVENTS.jsonl 21:36:14Z); see guard_repoint.
        self.assertEqual(self.live["C-9009"]["deps"], ["C-9030", "C-9038"])
        self.assertEqual(self.live["C-9008"]["status"], "dead")
        self.assertEqual(self.live["C-9005"]["status"], "superseded")
        self.assertEqual(self.fx["C-9009"]["deps"], ["C-9008", "C-9003"])


if __name__ == "__main__":
    unittest.main()
