"""Card C-0057: goal-done FIRE DRILL on a synthetic 18/18 fixture.

C-0012 (composer), C-0020 (done-check) and C-0013 (beats_base) were each
proven in isolation, but until now nothing exercised the full
done_criteria chain on a synthetic 18/18 input:

    real composer -> verdict file -> scan_verdicts -> goal_done
    (+ beats_base verdict fields + the C-0050 standup annotation)

This file is the end-to-end proof. The positive fixture drives the REAL
composer (scripts/holdout_verdict.py) over two synthetic leg envelopes
and then asks the REAL done-check whether the goal retires. Negative
controls each produce NO verdict or NO goal-done: 17/18, a missing
probe-differs marker, disagreeing legs, a budget-UNKNOWN leg (C-9046,
added 2026-09-17 by C-9055), and a legacy sha-unpinned verdict (the
C-0050 class).

Sha-pin note: goal_done compares a verdict pins against the CANONICAL
COMMITTED manifest. Concurrent sessions legitimately drift the working
tree mid-edit, so the positive legs pin the manifest READ to the
on-disk scorer files (fz.compute_manifest) -- that simulates a
freeze-consistent tree WITHOUT weakening anything: the composer still
hashes the real frozen files, and the drift guard itself is exercised
separately (the legacy test keeps the REAL named-violation path and
proves an unpinned verdict fails closed).
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_HARNESS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_REPO_ROOT = os.path.dirname(_HARNESS_DIR)
for p in (_HARNESS_DIR, _REPO_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

import harness_lib as H  # noqa: E402

from evals.runner import holdout_freeze as fz  # noqa: E402
from scripts import holdout_verdict as hv  # noqa: E402

FROZEN_BENCH = os.path.join(_REPO_ROOT, fz.BENCH_RELPATH)
VALID_LOG = (
    "stage: adapter_applied, adapter: adapters/x\n"
    "summary: adapter-applied adapter-probe-differs tasks=18\n"
)


def _frozen_ids():
    ids = [
        line.strip().split()[0]
        for line in Path(FROZEN_BENCH).read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]
    assert len(ids) == 18, "frozen holdout drifted: %d tasks" % len(ids)
    return ids


def _write_scores(tmp, name, passes):
    records = []
    for tid, (ap, bp) in passes.items():
        # scores.overall present (C-0033: the composer refuses empty legs)
        records.append(
            dict(model="adapter", task_id=tid, passed=ap, scores=dict(overall=1.0 if ap else 0.0))
        )
        records.append(
            dict(model="base", task_id=tid, passed=bp, scores=dict(overall=1.0 if bp else 0.0))
        )
    p = tmp / (name + "_scores.json")
    p.write_text(json.dumps(dict(task_ids=list(passes), records=records)))
    return p


def _write_leg(tmp, leg, passes, runner, markers=(True, True)):
    scores = _write_scores(tmp, leg, passes)
    log = tmp / (leg + ".log")
    log.write_text(VALID_LOG)
    env = dict(
        leg=leg,
        runner_mechanism=runner,
        box="ASI2",
        adapter=str(tmp / "adapter"),
        base_model=str(tmp / "base"),
        # C-9055 reconciliation (2026-09-17): C-9046 budget parity --
        # every leg envelope MUST carry a usable max_new_tokens or the
        # composer refuses fail-closed (verdict_composer_refused_budget
        # _unknown). 384 = the canonical runner default under debate.
        max_new_tokens=384,
        benchmark=FROZEN_BENCH,
        adapter_applied_marker=markers[0],
        adapter_probe_differs_marker=markers[1],
        leg_log=str(log),
        scores=str(scores),
    )
    p = tmp / (leg + ".json")
    p.write_text(json.dumps(env))
    return p


def _legs_all_pass(tmp):
    passes = dict((tid, (True, False)) for tid in _frozen_ids())
    leg1 = _write_leg(tmp, "leg1", passes, "parallel-3-slice")
    leg2 = _write_leg(tmp, "leg2", passes, "sequential-single-slice")
    return leg1, leg2


def _manifest_from_disk():
    """Freeze-consistent manifest: the ACTUAL on-disk frozen files."""
    return dict(fz.compute_manifest(_REPO_ROOT))


def _compose_goal_done(tmp, out_name="verdict_fire_drill.json", extra_files=None):
    """Full chain: compose -> write -> scan -> goal_done. Returns
    (done, file, verdict, scan_len)."""
    leg1, leg2 = _legs_all_pass(tmp)
    out = tmp / "outputs" / out_name
    verdict = hv.compose_verdict(leg1, leg2, out)
    for name, blob in (extra_files or dict()).items():
        (tmp / "outputs" / name).write_text(json.dumps(blob))
    vs = H.scan_verdicts(tmp)
    with mock.patch.object(H, "_canonical_sha_manifest", _manifest_from_disk):
        done, src = H.goal_done(dict(target_pass="18/18"), vs)
    return done, src, verdict, len(vs)


class TestC0057FireDrill(unittest.TestCase):
    def test_positive_fixture_composes_and_retires_goal(self):
        """ACCEPTANCE 1: fake dual-leg 18/18 verdicts, markers present ->
        composer emits a verdict file with every done_criteria field, and
        the REAL done-check retires the goal on it."""
        tmp = Path(tempfile.mkdtemp(prefix="c0057-"))
        done, src, v, _ = _compose_goal_done(tmp)
        # every done_criteria field on the emitted file
        self.assertEqual(v["pass_adapter"], "18/18")
        self.assertIs(v["beats_base"], True)
        self.assertIs(v["meets_goal"], True)
        self.assertIs(v["adapter_applied_marker"], True)
        self.assertIs(v["adapter_probe_differs_marker"], True)
        self.assertIs(v["independent_second_leg"], True)
        self.assertEqual(len(v["per_task"]), 18)
        self.assertTrue(v["leg1"]["markers"]["adapter_probe_differs"])
        self.assertTrue(v["leg2"]["markers"]["adapter_probe_differs"])
        self.assertNotEqual(v["leg1"]["runner_mechanism"], v["leg2"]["runner_mechanism"])
        # the verdict FILE exists on disk and the done-check fires on it
        self.assertTrue((tmp / "outputs" / "verdict_fire_drill.json").is_file())
        self.assertTrue(done, "done-check refused a perfect composed 18/18 verdict")
        self.assertEqual(src, "verdict_fire_drill.json")

    def test_goal_done_fires_exactly_once_on_mixed_outputs(self):
        """ACCEPTANCE 3 (first half): with qualifying AND non-qualifying
        verdicts in outputs/, goal-done fires exactly once, on the
        qualifying file."""
        tmp = Path(tempfile.mkdtemp(prefix="c0057-"))
        legacy = dict(
            pass_adapter="18/18",
            pass_base="1/18",
            beats_base=True,
            scorer_version="holdout-scorer-1.2.0",
            _file="verdict_legacy.json",
        )  # C-0050 class: banked pre-pin verdict, no sha pins, no legs
        seventeen = dict(
            pass_adapter="17/18",
            pass_base="0/18",
            beats_base=True,
            _file="verdict_17.json",
        )
        extra = dict()
        extra["verdict_legacy.json"] = legacy
        extra["verdict_17.json"] = seventeen
        done, src, _, n = _compose_goal_done(tmp, extra_files=extra)
        self.assertEqual(n, 3)
        self.assertTrue(done)
        self.assertEqual(src, "verdict_fire_drill.json")
        # remove the qualifying verdict -> NO other verdict substitutes
        (tmp / "outputs" / "verdict_fire_drill.json").unlink()
        vs = H.scan_verdicts(tmp)
        with mock.patch.object(H, "_canonical_sha_manifest", _manifest_from_disk):
            done2, _ = H.goal_done(dict(target_pass="18/18"), vs)
        self.assertFalse(done2)

    def test_17_of_18_composes_but_never_retires_goal(self):
        """NEGATIVE 1: honest 17/18 still composes (meets_goal false) but
        produces NO goal-done."""
        tmp = Path(tempfile.mkdtemp(prefix="c0057-"))
        ids = _frozen_ids()
        passes = dict((tid, (True, False)) for tid in ids)
        passes[ids[0]] = (False, False)  # adapter fails task 0 on BOTH legs
        leg1 = _write_leg(tmp, "leg1", passes, "parallel-3-slice")
        leg2 = _write_leg(tmp, "leg2", passes, "sequential-single-slice")
        out = tmp / "outputs" / "verdict_17.json"
        v = hv.compose_verdict(leg1, leg2, out)
        self.assertEqual(v["pass_adapter"], "17/18")
        self.assertIs(v["meets_goal"], False)
        self.assertTrue(out.is_file())  # honest count still composes
        vs = H.scan_verdicts(tmp)
        with mock.patch.object(H, "_canonical_sha_manifest", _manifest_from_disk):
            done, _ = H.goal_done(dict(target_pass="18/18"), vs)
        self.assertFalse(done, "17/18 must never retire the goal")

    def test_missing_probe_differs_marker_rejected_no_verdict(self):
        """NEGATIVE 2: a leg without the probe-differs marker -> composer
        rejects, NO verdict file; and a verdict stripped of the top-level
        marker -> no goal-done."""
        tmp = Path(tempfile.mkdtemp(prefix="c0057-"))
        leg1, leg2 = _legs_all_pass(tmp)
        env = json.loads(Path(leg2).read_text())
        env["adapter_probe_differs_marker"] = None
        Path(leg2).write_text(json.dumps(env))
        out = tmp / "outputs" / "verdict_x.json"
        with self.assertRaises(hv.VerdictRejected):
            hv.compose_verdict(leg1, leg2, out)
        self.assertFalse(out.exists())
        # done-check side: a marker-less verdict fails closed even if
        # something else wrote the file
        leg1b, leg2b = _legs_all_pass(tmp)
        v = hv.compose_verdict(leg1b, leg2b, tmp / "outputs" / "verdict_ok.json")
        v["adapter_probe_differs_marker"] = None
        with mock.patch.object(H, "_canonical_sha_manifest", _manifest_from_disk):
            done, _ = H.goal_done(dict(target_pass="18/18"), [v])
        self.assertFalse(done)

    def test_budget_unknown_leg_refused_fail_closed(self):
        """NEGATIVE 5 (C-9046, C-9055 reconciliation witness): an
        envelope stripped of max_new_tokens is a budget-UNKNOWN leg ->
        composer refuses with the NAMED token, NO verdict file. This is
        the exact orphan-drift class measured 2026-09-17: fixtures that
        predated the budget guard failed all five compose paths."""
        tmp = Path(tempfile.mkdtemp(prefix="c0057-"))
        leg1, leg2 = _legs_all_pass(tmp)
        env = json.loads(Path(leg2).read_text())
        del env["max_new_tokens"]
        Path(leg2).write_text(json.dumps(env))
        out = tmp / "outputs" / "verdict_x.json"
        with self.assertRaises(hv.VerdictRejected) as cm:
            hv.compose_verdict(leg1, leg2, out)
        self.assertIn("refused_budget_unknown", str(cm.exception))
        self.assertFalse(out.exists())

    def test_disagreeing_legs_rejected_no_verdict(self):
        """NEGATIVE 3: legs disagreeing on a per-task pass -> composer
        rejects, NO verdict file."""
        tmp = Path(tempfile.mkdtemp(prefix="c0057-"))
        ids = _frozen_ids()
        p1 = dict((tid, (True, False)) for tid in ids)
        p2 = dict((tid, (True, False)) for tid in ids)
        p2[ids[3]] = (False, False)  # leg2 disagrees on task 3
        leg1 = _write_leg(tmp, "leg1", p1, "parallel-3-slice")
        leg2 = _write_leg(tmp, "leg2", p2, "sequential-single-slice")
        out = tmp / "outputs" / "verdict_x.json"
        with self.assertRaises(hv.VerdictRejected):
            hv.compose_verdict(leg1, leg2, out)
        self.assertFalse(out.exists())

    def test_legacy_sha_unpinned_verdict_never_retires_goal(self):
        """NEGATIVE 4 (C-0050 class): a verdict stripped of its sha pins
        fails the done-check with a NAMED violation; the C-0050 standup
        annotation flags eligibility correctly (exactly one YES, the
        legacy row named as ineligible)."""
        tmp = Path(tempfile.mkdtemp(prefix="c0057-"))
        leg1, leg2 = _legs_all_pass(tmp)
        v = hv.compose_verdict(leg1, leg2, tmp / "outputs" / "verdict_ok.json")
        legacy = dict(v)
        legacy["_file"] = "verdict_legacy.json"
        del legacy["holdout_sha256"]
        del legacy["scorer_shas"]
        with mock.patch.object(H, "_canonical_sha_manifest", _manifest_from_disk):
            done_pos, _ = H.goal_done(dict(target_pass="18/18"), [dict(v, _file="verdict_ok.json")])
            done_leg, _ = H.goal_done(dict(target_pass="18/18"), [legacy])
            vio = H.sha_pin_violation(legacy)
        self.assertTrue(done_pos)  # control: the pinned twin DOES retire
        self.assertFalse(done_leg, "sha-unpinned legacy verdict must never retire the goal")
        self.assertEqual(vio, "scorer_sha_pins_missing")
        # C-0050 standup annotation: exactly one goal_done=YES, the legacy
        # row explicitly ineligible with the named violation
        with mock.patch.object(H, "_canonical_sha_manifest", _manifest_from_disk):
            out = H.render_standup(
                dict(target_pass="18/18"),
                dict(cards=[]),
                dict(agents=[]),
                1,
                verdicts=[legacy, dict(v, _file="verdict_ok.json")],
            )
        self.assertEqual(out.count("goal_done=YES"), 1)
        self.assertIn("verdict_legacy.json", out)
        self.assertIn("goal_done=NO (sha_pin_violation: scorer_sha_pins_missing)", out)


if __name__ == "__main__":
    unittest.main()
