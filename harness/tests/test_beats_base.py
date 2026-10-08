# C-0013 RED spec: pin the beats_base comparison metric BEFORE the C-0012
# composer consumes it (18/18-tie deadlock guard).
#
# Decision under test (recorded in harness/state/beats_base_metric.md):
#   1. PRIMARY: pass-count. beats_base True iff pass_adapter > pass_base.
#   2. TIEBREAK: on equal pass-counts, composite score decides.
#   3. FAIL-CLOSED: a tie with no composite inputs raises BeatsBaseError --
#      the composer must NOT emit a beats_base bool it cannot support.
#      This is the pass_base==18/18 deadlock guard.
#   4. FULL TIE (pass + composite equal): measured False with rule
#      "full-tie-deadlock" -- named, never silent; unblocking it needs a
#      GOAL amendment (GOAL.json is frozen; harness-auto-gated).
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import beats_base as BB  # noqa: E402

HARNESS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestPassCountPrimary(unittest.TestCase):
    def test_adapter_above_base_true_on_pass_count(self):
        # PRIMARY pinned: composite is NOT consulted when pass-counts differ,
        # even if the adapter composite is WORSE.
        verdict, rule = BB.beats_base("10/18", "3/18", composite_adapter=0.5, composite_base=0.9)
        self.assertTrue(verdict)
        self.assertEqual(rule, "pass-count")

    def test_adapter_below_base_false_on_pass_count(self):
        verdict, rule = BB.beats_base("2/18", "3/18", composite_adapter=0.9, composite_base=0.1)
        self.assertFalse(verdict)
        self.assertEqual(rule, "pass-count")


class TestCompositeTiebreak(unittest.TestCase):
    def test_tie_broken_by_higher_composite_true(self):
        # The 18/18-tie case: base lifted to perfect by sanitization; only
        # composite decides. This test existing = the deadlock guard exists.
        verdict, rule = BB.beats_base("18/18", "18/18", composite_adapter=17.9, composite_base=17.1)
        self.assertTrue(verdict)
        self.assertEqual(rule, "composite-tiebreak")

    def test_tie_broken_by_lower_composite_false(self):
        verdict, rule = BB.beats_base("18/18", "18/18", composite_adapter=17.0, composite_base=17.5)
        self.assertFalse(verdict)
        self.assertEqual(rule, "composite-tiebreak")

    def test_full_tie_is_named_not_silent(self):
        verdict, rule = BB.beats_base("18/18", "18/18", composite_adapter=17.5, composite_base=17.5)
        self.assertFalse(verdict)
        self.assertEqual(rule, "full-tie-deadlock")


class TestFailClosedGuard(unittest.TestCase):
    def test_tie_without_tiebreak_inputs_raises(self):
        # THE GUARD: pass_base==18/18 and no tiebreak rule applied must fail
        # closed (raise), never default to True or False silently.
        with self.assertRaises(BB.BeatsBaseError):
            BB.beats_base("18/18", "18/18")

    def test_partial_tie_without_composite_also_raises(self):
        with self.assertRaises(BB.BeatsBaseError):
            BB.beats_base("5/18", "5/18")

    def test_malformed_score_raises(self):
        with self.assertRaises(BB.BeatsBaseError):
            BB.beats_base("x/18", "3/18", composite_adapter=1.0, composite_base=0.5)

    def test_mismatched_denominators_raise(self):
        with self.assertRaises(BB.BeatsBaseError):
            BB.beats_base("18/18", "3/9", composite_adapter=1.0, composite_base=0.5)

    def test_out_of_range_raises(self):
        with self.assertRaises(BB.BeatsBaseError):
            BB.beats_base("19/18", "3/18", composite_adapter=1.0, composite_base=0.5)
        with self.assertRaises(BB.BeatsBaseError):
            BB.beats_base("18/18", "3/18", composite_adapter=-1.0, composite_base=0.5)

    def test_int_inputs_accepted(self):
        verdict, rule = BB.beats_base(10, 3, composite_adapter=None, composite_base=None)
        self.assertTrue(verdict)
        self.assertEqual(rule, "pass-count")


class TestDecisionRecorded(unittest.TestCase):
    def test_spec_file_exists_and_pins_rules(self):
        path = os.path.join(HARNESS_DIR, "state", "beats_base_metric.md")
        with open(path, encoding="utf-8") as f:
            text = f.read()
        for token in (
            "pass-count",
            "composite-tiebreak",
            "full-tie-deadlock",
            "BeatsBaseError",
            "C-0012",
        ):
            self.assertIn(token, text)


if __name__ == "__main__":
    unittest.main()
