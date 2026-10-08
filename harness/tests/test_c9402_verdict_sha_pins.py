"""Card C-9402: holdout_verdict compose stamps BOTH sha-pin fields into the
verdict JSON, tied to the ACTUAL frozen holdout bench + scorer-chain files
on disk.

RED contract (fail-closed): any composed verdict without holdout_sha256 or
scorer_shas (or whose pins do not match the on-disk freeze manifest) is
untrusted -- the C-0031 gate (goal_done) refuses sha-unpinned/mismatched
verdicts. This test locks the COMPOSER side: compose_verdict MUST emit both
fields and MUST pin them to the real frozen files, not placeholders.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

_HARNESS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_REPO_ROOT = os.path.dirname(_HARNESS_DIR)
for p in (_HARNESS_DIR, _REPO_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

import harness.tests.test_c0057_goal_done_fire_drill as _c0057_mod  # noqa: E402,E501
from scripts import holdout_verdict as hv  # noqa: E402

_frozen_ids = _c0057_mod._frozen_ids
_write_leg = _c0057_mod._write_leg


def _composed_verdict(tmp):
    ids = _frozen_ids()
    passes = dict((tid, (True, False)) for tid in ids)  # adapter beats base everywhere
    leg1 = _write_leg(tmp, "leg1", passes, "parallel-3-slice")
    leg2 = _write_leg(tmp, "leg2", passes, "sequential-single-slice")
    out = tmp / "outputs" / "verdict.json"
    v = hv.compose_verdict(leg1, leg2, out)
    return v, out


class C9402VerdictShaPins(unittest.TestCase):
    def test_verdict_stamps_both_sha_pin_fields(self):
        """POSITIVE: compose emits holdout_sha256 AND scorer_shas."""
        tmp = Path(tempfile.mkdtemp(prefix="c9402-"))
        v, out = _composed_verdict(tmp)
        self.assertIn("holdout_sha256", v, "compose must stamp holdout_sha256")
        self.assertIn("scorer_shas", v, "compose must stamp scorer_shas")
        self.assertTrue(out.is_file())

    def test_holdout_sha_matches_on_disk_frozen_bench(self):
        """POSITIVE: holdout_sha256 equals the actual frozen bench file hash."""
        tmp = Path(tempfile.mkdtemp(prefix="c9402-"))
        v, _ = _composed_verdict(tmp)
        hold, _sc = hv.compute_sha_pins()
        self.assertEqual(v["holdout_sha256"], hold)
        self.assertEqual(len(v["holdout_sha256"]), 64)

    def test_scorer_shas_match_scorer_chain_files(self):
        """POSITIVE: every scorer chain file is hashed; values are 64-hex."""
        tmp = Path(tempfile.mkdtemp(prefix="c9402-"))
        v, _ = _composed_verdict(tmp)
        _hold, sc = hv.compute_sha_pins()
        self.assertEqual(v["scorer_shas"], sc)
        for rel, digest in v["scorer_shas"].items():
            with self.subTest(rel=rel):
                self.assertEqual(len(digest), 64)

    def test_pins_survive_written_verdict_file(self):
        """POSITIVE: both fields persist in the verdict file on disk."""
        tmp = Path(tempfile.mkdtemp(prefix="c9402-"))
        v, out = _composed_verdict(tmp)
        on_disk = json.loads(out.read_text())
        self.assertIn("holdout_sha256", on_disk)
        self.assertIn("scorer_shas", on_disk)
        self.assertEqual(on_disk["holdout_sha256"], v["holdout_sha256"])
        self.assertEqual(on_disk["scorer_shas"], v["scorer_shas"])


if __name__ == "__main__":
    unittest.main()
