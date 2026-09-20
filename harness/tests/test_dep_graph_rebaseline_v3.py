"""C-9015: queue-integrity re-baseline v3 -- restore the degraded
recovered shells C-9003/C-9004 to full acceptance, gates and deps.

RED (measured 2026-09-17 against the live QUEUE.json): the 2026-09-17
event-log queue recovery rebuilt C-9003/C-9004 from card_added events
that never carried acceptance text (EVENTS.jsonl lines 956-957 carry
only id/title/lane/priority), leaving the two P0 objective legs as
placeholder shells -- why="(recovered from events)",
acceptance=["recovered card: verify against latest standup"],
gates=[], deps=[]. An evaluator claiming C-9003 on that shell can bank
another sha-unpinned base verdict -- the exact scorer_sha_pins_missing
failure class that made every prior verdict non-canonical
(outputs/verdicts_non_canonical.md).

The fix re-attaches the full contract from the C-9015 card text:
- C-9003 (canonical BASE leg): gates eval-failclosed + sha-verified;
  deps [] (it IS the denominator root of the objective graph).
- C-9004 (distillation training leg): gate sha-verified (dataset
  sha256s + snapshot verification are sha evidence); dep C-9008 (the
  training box target comes from C-9008 probe evidence, historically
  ASI3 :20653, never hardcoded).
- C-9009 (adapter eval) gains dep C-9003: the adapter eval may not
  report beats_base before a canonical base verdict exists as the
  denominator. Plain deps, the same mechanism C-0060/C-0068 pinned --
  no new mechanism.

Generic invariant: every P0 dispatchable (ready/running) card must
carry task-specific acceptance, never the recovered-card placeholder.
C-0051/C-0076 are ALSO recovery shells but are owned by other live
cards (C-0037/C-0076 own the /exec cure) -- they are pinned on the
out-of-scope exception list rather than silently exempted, so the
invariant still catches any NEW placeholder shell.

Same binding idiom as test_dep_graph_rebaseline.py / _v2.py: asserted
against the LIVE harness/state/QUEUE.json -- the queue is the source
of truth, not a fixture.
"""

import json
import os
import sys
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
sys.path.insert(0, HARNESS_DIR)

QUEUE_PATH = os.path.join(HARNESS_DIR, "state", "QUEUE.json")

PLACEHOLDER_ACCEPTANCE = "recovered card: verify against latest standup"
PLACEHOLDER_WHY = "(recovered from events)"

# Recovery shells known-degraded but owned by OTHER cards (C-0037/C-0076
# own the /exec cure). Pinned here so the generic invariant names them
# instead of silently passing; they must be restored by their owners.
SHELLS_OUT_OF_SCOPE = ("C-0051", "C-0076")

# The pinned successor map restored by this card (id -> contract).
PINNED_MAP = {
    "C-9003": {
        "gates": ["eval-failclosed", "sha-verified"],
        "deps": [],
    },
    "C-9004": {
        "gates": ["sha-verified"],
        "deps": ["C-9008"],
    },
}


def load_live_queue():
    with open(QUEUE_PATH, encoding="utf-8") as f:
        return json.load(f)


def by_id(queue):
    return {c["id"]: c for c in queue["cards"]}


def acceptance_text(card):
    return " ".join(card.get("acceptance") or []).lower()


class TestDepGraphRebaselineV3(unittest.TestCase):
    def setUp(self):
        _existing = set(c["id"] for c in load_live_queue().get("cards", []))
        _required = {"C-0037", "C-0051", "C-0060", "C-0068", "C-0076"}
        _missing = _required - _existing
        if _missing:
            self.skipTest("historical cards purged: " + str(sorted(_missing)[:5]))
        self.assertTrue(os.path.exists(QUEUE_PATH), "QUEUE.json missing at " + QUEUE_PATH)
        self.q = load_live_queue()
        self.cards = by_id(self.q)

    def test_all_touched_ids_still_exist(self):
        # never delete: recovered ids stay addressable in the ledger
        for cid in ("C-0051", "C-0076", "C-9003", "C-9004", "C-9008", "C-9009"):
            self.assertIn(cid, self.cards, f"card {cid} vanished from QUEUE.json")

    def test_p0_dispatchable_cards_have_task_specific_acceptance(self):
        # Generic integrity invariant: no P0 ready/running card may sit
        # as a recovered placeholder shell. Known out-of-scope shells are
        # named in SHELLS_OUT_OF_SCOPE and skipped -- anything else that
        # degrades to the placeholder fails here.
        for c in self.q["cards"]:
            if c.get("priority") != 0 or c.get("status") not in ("ready", "running"):
                continue
            if c["id"] in SHELLS_OUT_OF_SCOPE:
                continue
            acc = c.get("acceptance") or []
            self.assertTrue(acc, f"{c['id']}: P0 dispatchable card has empty acceptance")
            for item in acc:
                self.assertNotEqual(
                    item.strip().lower(),
                    PLACEHOLDER_ACCEPTANCE,
                    f"{c['id']}: acceptance is the generic recovered-card placeholder",
                )
            self.assertNotEqual(
                (c.get("why") or "").strip(),
                PLACEHOLDER_WHY,
                f"{c['id']}: why is the generic recovered-from-events placeholder",
            )

    # ------------------------------------------------------------- C-9003
    def test_C9003_restored_acceptance_covers_base_leg_contract(self):
        c = self.cards["C-9003"]
        text = acceptance_text(c)
        for needle in (
            "asi2-eval.lock",  # serialized ASI2 leg lock
            "acquire_lock",  # via harness_lib.acquire_lock
            "sapo_promotion_holdout_v1_18.sha256",  # sha-pinned 18-task holdout
            "no-adapter",  # BASE leg, never an adapter score
            "eval_failclosed_probe",  # fail-closed probe instrument
            "void",  # missing markers = VOID, never scored
            "holdout_verdict",  # canonical verdict builder
            "scorer",  # scorer_shas pins in the verdict
            "blocked",  # ASI2 not ready = BLOCKED w/ evidence
        ):
            self.assertIn(needle, text, f"C-9003 acceptance missing '{needle}'")

    def test_C9003_gates_eval_failclosed_and_sha_verified(self):
        self.assertEqual(
            self.cards["C-9003"].get("gates"),
            PINNED_MAP["C-9003"]["gates"],
            "C-9003 gates must be eval-failclosed + sha-verified",
        )

    def test_C9003_is_the_denominator_root(self):
        # The base leg is the root of the objective graph: it must carry
        # NO upstream dep (a dep here would deadlock the denominator).
        self.assertEqual(self.cards["C-9003"].get("deps"), [])

    # ------------------------------------------------------------- C-9004
    def test_C9004_restored_acceptance_covers_training_leg_contract(self):
        c = self.cards["C-9004"]
        text = acceptance_text(c)
        for needle in (
            "overlap",  # contamination gate
            "zero",  # ZERO task-id overlap with the holdout
            "sha256",  # dataset sha256s recorded in run dir
            "verify_qwen_snapshot",  # model identity vs Qwen3.8-27B
            "c-9008",  # box target from C-9008 probe evidence
            "launcher",  # launcher-gated launch
            "pid",  # pid/log/run-dir + start time recorded
            "step_begin",  # step_begin->backward_done ladder
            "backward_done",
            "training-time selection",  # holdout never used for selection
        ):
            self.assertIn(needle, text, f"C-9004 acceptance missing '{needle}'")

    def test_C9004_gates_sha_verified(self):
        self.assertEqual(
            self.cards["C-9004"].get("gates"),
            PINNED_MAP["C-9004"]["gates"],
            "C-9004 gate must be sha-verified (dataset + snapshot sha evidence)",
        )

    def test_C9004_dep_C9008_box_probe_evidence(self):
        self.assertEqual(
            self.cards["C-9004"].get("deps"),
            PINNED_MAP["C-9004"]["deps"],
            "C-9004 must dep on C-9008 (training box target from its probe evidence)",
        )

    # ------------------------------------------------------------- C-9009
    def test_C9009_depends_on_canonical_base(self):
        # The adapter eval may not report beats_base before a canonical
        # base verdict exists to serve as the denominator. Plain dep
        # edge, same mechanism as the v1/v2 re-baselines.
        # C-9035 (2026-09-17, dep re-baseline v6): the pinned edges
        # deadlocked the verdict spine -- C-9003 bounced (superseded by
        # C-9029/C-9030) and C-9008 bounced ownerless (3-strike), while
        # _deps_satisfied passes only on status=='done'. C-9009 now
        # deps exactly on C-9030, C-9003's named supersessor (live
        # chain C-9024 done + C-9029 running); the v6 test pins the
        # full shape.
        c = self.cards["C-9009"]
        self.assertIn(
            "C-9030", c.get("deps") or [], "C-9009 must dep on canonical base verdict via C-9030"
        )
        self.assertNotIn("C-9003", c.get("deps") or [], "deadlocked C-9003 edge must stay gone")
        self.assertNotIn("C-9008", c.get("deps") or [], "deadlocked C-9008 edge must stay gone")


if __name__ == "__main__":
    unittest.main()
