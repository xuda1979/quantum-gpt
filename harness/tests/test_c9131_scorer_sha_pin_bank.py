"""Card C-9131: bank the frozen scorer sha pins under harness/state.

C-0031 made goal_done refuse sha-unpinned verdicts (fail-closed, correct),
but nobody banked the pins the gate demands, so every banked verdict died
goal_done=NO (scorer_sha_pins_missing) and done_criteria #1 was unreachable
even at a perfect 18/18. This file pins the C-9131 contract:

  - fail-closed preserved: a full 18/18 verdict with NO scorer pins still
    composes goal_done NO with the named scorer_sha_pins_missing violation
  - bank_scorer_sha_pins banks the EXACT frozen pins (bench + the 4-file
    scorer chain) under harness/state, refusing any drift vs the manifest
  - a verdict stamped from the bank fires goal_done YES
  - a tampered bank is not a bypass: its verdict still fails closed

Manifest note (same discipline as test_c0057): concurrent sessions
legitimately drift the working tree mid-edit, so every read of the
canonical manifest is pinned to fz.compute_manifest(root) -- the on-disk
frozen files -- and the SAME read is handed to the bank and the bank
checks. Nothing here weakens sha_pin_violation.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from evals.runner import holdout_freeze as fz  # noqa: E402
from harness import harness_lib as H  # noqa: E402


def _manifest_from_disk(_fz=None):
    return dict(fz.compute_manifest(ROOT))


def _full_verdict(holdout_sha, scorer_shas):
    """A verdict that satisfies every non-sha goal_done gate (C-9044 bank
    shape: two distinct legs, probe-differs both, 18-task per_task map,
    proven Qwen3.8-27B identity)."""
    per_task = {
        ("quantum_task_%02d" % i): {"adapter_pass": True, "base_pass": (i == 0)} for i in range(18)
    }
    return {
        "pass_adapter": "18/18",
        "pass_base": "1/18",
        "beats_base": True,
        "scorer_version": "holdout-freeze-c9131",
        "adapter_applied_marker": True,
        "adapter_probe_differs_marker": True,
        "leg1": {
            "box": "box-a",
            "runner_mechanism": "mech-1",
            "adapter_applied_marker": True,
            "adapter_probe_differs_marker": True,
        },
        "leg2": {
            "box": "box-b",
            "runner_mechanism": "mech-2",
            "adapter_applied_marker": True,
            "adapter_probe_differs_marker": True,
        },
        "per_task": per_task,
        "model_identity": {
            "status": "PASS",
            "base_model": "Qwen/Qwen3.8-27B",
            "sha256": "a" * 64,
        },
        "holdout_sha256": holdout_sha,
        "scorer_shas": scorer_shas,
    }


def test_goal_done_stays_no_when_scorer_pins_missing():
    """Fail-closed preserved: an 18/18 verdict with no scorer pins still
    composes goal_done NO, with the exact named violation."""
    v = _full_verdict("b" * 64, {})
    v.pop("scorer_shas")
    v.pop("holdout_sha256")
    with mock.patch.object(H, "_canonical_sha_manifest", _manifest_from_disk):
        assert H.sha_pin_violation(v) == "scorer_sha_pins_missing"
        done, _src = H.goal_done(dict(target_pass="18/18"), [dict(v, _file="v.json")])
    assert done is False


def test_bank_scorer_sha_pins_banks_exact_frozen_pins(tmp_path):
    """The bank holds the sha256 of every pinned scorer file + the 18-task
    holdout, byte-identical to the canonical manifest entries."""
    manifest = _manifest_from_disk()
    bank = H.bank_scorer_sha_pins(state_dir=str(tmp_path), manifest=manifest)
    on_disk = json.loads((tmp_path / "scorer_sha_pins.json").read_text(encoding="utf-8"))
    assert on_disk == bank
    assert bank["holdout_sha256"] == manifest[fz.BENCH_RELPATH]
    for rel in fz.SCORER_CHAIN:
        assert bank["scorer_shas"][rel] == manifest[rel]
    assert len(bank["scorer_shas"]) == len(fz.SCORER_CHAIN)
    assert bank["n_tasks"] == 18
    # load-back returns the same pins
    assert H.load_banked_scorer_sha_pins(state_dir=str(tmp_path)) == bank


def test_goal_done_fires_yes_when_pins_banked():
    """THE C-9131 fix: a verdict stamped from the banked pins composes
    goal_done YES -- done_criteria #1 is reachable again."""
    manifest = _manifest_from_disk()
    with mock.patch.object(H, "_canonical_sha_manifest", _manifest_from_disk):
        bank = H.bank_scorer_sha_pins(manifest=manifest)
        loaded = H.load_banked_scorer_sha_pins()
        assert loaded == bank
        v = _full_verdict(loaded["holdout_sha256"], loaded["scorer_shas"])
        assert H.sha_pin_violation(v) is None
        done, _src = H.goal_done(dict(target_pass="18/18"), [dict(v, _file="v.json")])
    assert done is True


def test_tampered_bank_is_not_a_bypass(tmp_path):
    """A corrupted bank cannot mint a passing verdict: the gate compares
    verdict pins against the canonical manifest, not the bank alone."""
    manifest = _manifest_from_disk()
    bank = H.bank_scorer_sha_pins(state_dir=str(tmp_path), manifest=manifest)
    rel = sorted(bank["scorer_shas"])[0]
    bank["scorer_shas"][rel] = "c" * 64
    (tmp_path / "scorer_sha_pins.json").write_text(json.dumps(bank), encoding="utf-8")
    loaded = H.load_banked_scorer_sha_pins(state_dir=str(tmp_path))
    v = _full_verdict(loaded["holdout_sha256"], loaded["scorer_shas"])
    with mock.patch.object(H, "_canonical_sha_manifest", _manifest_from_disk):
        assert H.sha_pin_violation(v) == "scorer_sha_mismatch:" + rel
        done, _src = H.goal_done(dict(target_pass="18/18"), [dict(v, _file="v.json")])
    assert done is False


def test_load_bank_missing_returns_none(tmp_path):
    assert H.load_banked_scorer_sha_pins(state_dir=str(tmp_path)) is None


def test_load_bank_malformed_fails_closed(tmp_path):
    (tmp_path / "scorer_sha_pins.json").write_text("{not json", encoding="utf-8")
    with pytest.raises(ValueError):
        H.load_banked_scorer_sha_pins(state_dir=str(tmp_path))
