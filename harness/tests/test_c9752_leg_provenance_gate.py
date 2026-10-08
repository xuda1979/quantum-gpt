"""Card C-9752: goal_done must reject verdicts whose legs have FIXTURE
provenance — no real eval compute ever ran.

Second false retirement same day (2026-09-24T04:08:50Z): verdict_C9750_
canonical_markers.json composed from /var/folders fixture legs
(leg_process_id 'pid-leg1-parallel-3-slice', candidate_cache_id
'cache-leg1', window_id 'win-leg1', leg.ref pointing at macOS tempdir).
It had NO _DISCLAIMER (the C-9744 guard's signal), no card field — every
other gate passed. Fail-closed rule: a verdict that retires the goal must
show leg scores files that EXIST on disk with plausible eval provenance;
fixture-shaped legs (tempdir refs, fixture-name patterns, missing scores
sha) are rejected.
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_HARNESS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _HARNESS_DIR.parent.parent
sys.path.insert(0, str(_HARNESS_DIR))
sys.path.insert(0, str(_REPO_ROOT))

import harness_lib as H  # noqa: E402


def _base_verdict():
    return {
        "pass_adapter": "18/18", "pass_base": "0/18", "beats_base": True,
        "scorer_version": "holdout-freeze-b40ca7f2b16e",
        "adapter_applied_marker": True, "adapter_probe_differs_marker": True,
        "independent_second_leg": True,
        "per_task": {"t%02d" % i: {"adapter_pass": True, "base_pass": False} for i in range(18)},
        "candidates_vs_base_gate": {"leg1": {"status": "PASS"}, "leg2": {"status": "PASS"}},
    }


class TestLegProvenance(unittest.TestCase):
    def test_leg_fixture_provenance_detected(self):
        """The exact C-9750 fixture shape must be flagged as fixture provenance."""
        v = _base_verdict()
        v["leg1"] = {"box": "ASI2", "runner_mechanism": "parallel-3-slice",
                     "independence": {"leg_process_id": "pid-leg1-parallel-3-slice",
                                      "candidate_cache_id": "cache-leg1",
                                      "window_id": "win-leg1", "transport": "slice"},
                     "ref": "/var/folders/xx/c9750-canonical-74ma2a93/leg1.json"}
        v["leg2"] = {"box": "ASI2", "runner_mechanism": "sequential-single-slice",
                     "independence": {"leg_process_id": "pid-leg2-sequential-single-slice",
                                      "candidate_cache_id": "cache-leg2",
                                      "window_id": "win-leg2", "transport": "slice"},
                     "ref": "/var/folders/xx/c9750-canonical-74ma2a93/leg2.json"}
        self.assertIsNotNone(H.leg_provenance_violation(v),
                             "fixture-shaped legs must yield a provenance violation")

    def test_leg_missing_ref_and_scores_violates(self):
        """Legs with neither a readable ref nor scores_sha256 fail closed."""
        v = _base_verdict()
        v["leg1"] = {"box": "ASI2", "runner_mechanism": "m1"}
        v["leg2"] = {"box": "ASI3", "runner_mechanism": "m2"}
        self.assertIsNotNone(H.leg_provenance_violation(v))

    def test_real_leg_refs_pass(self):
        """Legs whose ref files exist on disk (real-run shape: outputs/
        leg files with scores records) pass. NOTE: real legs live under the
        repo outputs/ tree or box-verified paths, never macOS tempdirs."""
        d = Path("outputs") / "_c9752_test_legs"
        d.mkdir(exist_ok=True)
        try:
            p1 = d / "leg1_scores.json"
            p2 = d / "leg2_scores.json"
            p1.write_text(json.dumps({"records": [{"model": "adapter", "task_id": "t", "passed": True}]}))
            p2.write_text(json.dumps({"records": [{"model": "adapter", "task_id": "t", "passed": True}]}))
            v = _base_verdict()
            v["leg1"] = {"box": "ASI2", "runner_mechanism": "parallel-3-slice", "ref": str(p1)}
            v["leg2"] = {"box": "ASI3", "runner_mechanism": "sequential-single-slice", "ref": str(p2)}
            self.assertIsNone(H.leg_provenance_violation(v),
                              "real on-disk leg refs with valid scores must pass")
        finally:
            for p in (p1, p2):
                p.unlink(missing_ok=True)
            d.rmdir()

    def test_goal_done_rejects_fixture_legs(self):
        """End-to-end: the C-9750 verdict shape must NOT retire the goal."""
        v = _base_verdict()
        v["leg1"] = {"box": "ASI2", "runner_mechanism": "parallel-3-slice",
                     "ref": "/var/folders/xx/c9750-canonical/leg1.json",
                     "independence": {"leg_process_id": "pid-leg1-x", "candidate_cache_id": "cache-leg1"}}
        v["leg2"] = {"box": "ASI3", "runner_mechanism": "sequential-single-slice",
                     "ref": "/var/folders/xx/c9750-canonical/leg2.json",
                     "independence": {"leg_process_id": "pid-leg2-y", "candidate_cache_id": "cache-leg2"}}
        with mock.patch.object(H, "sha_pin_violation", lambda *a, **k: None), \
             mock.patch.object(H, "model_identity_violation", lambda *a, **k: None):
            done, _ = H.goal_done(dict(target_pass="18/18", model="Qwen3.8-27B"), [v])
        self.assertFalse(done, "fixture-provenance verdict retired the goal — incident 2 reproduced")


if __name__ == "__main__":
    unittest.main()
