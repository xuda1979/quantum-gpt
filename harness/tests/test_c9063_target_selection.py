"""C-9089 (re-file of bounce-dead C-9063): RED-first tests for the fail-closed
selector that pins the C-9009/C-9016 adapter target checkpoint from the C-9068
inventory artifacts.

Card acceptance under test:
- selection consumes the C-9068 inventory JSON artifact and fails closed with a
  named BLOCKED when it is missing, malformed, or contains zero sha-verified
  staged checkpoints;
- selects newest-mtime sha-verified staged checkpoint by a stated deterministic
  rule; rejects unstaged or unhashed entries;
- banks checkpoint_id + sha256 + inventory_path + selected_at_utc.
"""

import json
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import target_checkpoint as tc  # noqa: E402

SHA_A = "1b9ba88778b82bd8aa9f862052f3da2ed64c4ca848e71aaf5e2c1d2d497a3248"
SHA_B = "2313123df9d5753c8064aa9069ca1a7d42526eb2a451f8a22258e957be60febd"


def _manifest(weights_sha=SHA_A, staged_verified=None, checkpoint_mtime=None):
    return {
        "card": "C-9068",
        "checkpoint": {
            "run_dir": "sapo-27b-ai-20260907T085136Z",
            "step_dir": "step_000097_adapter",
            "box_path": "/root/work/software/quantum-gpt/outputs/"
            "sapo-27b-ai-20260907T085136Z/step_000097_adapter",
            "mtime_utc": checkpoint_mtime or "2026-09-07T19:41:00Z",
        },
        "staged_dir": "harness/state/probes/c9068/staged_s97_0907/",
        "staged_verified": staged_verified
        if staged_verified is not None
        else [{"name": "adapter_config.json", "sha256": "a" * 64}],
        "blocked": [
            {
                "name": "adapter_model.safetensors",
                "sha256": weights_sha,
                "reason": "312MB over budget transport",
            }
        ],
    }


def _inventory():
    return {
        "card": "C-9068",
        "alt_s97": {
            "path": "sapo-27b-ai-20260908T094427Z/step_000097_adapter",
            "adapter_model_sha": SHA_B,
            "mtime": 1788899306,
            "note": "different weights from banked s97; NOT staged",
        },
    }


def _write(tmp_path, name, obj_or_str):
    p = tmp_path / name
    text = obj_or_str if isinstance(obj_or_str, str) else json.dumps(obj_or_str)
    p.write_text(text, encoding="utf-8")
    return str(p)


def _both(tmp_path, inv=None, man=None):
    return (
        _write(tmp_path, "inv.json", inv if inv is not None else _inventory()),
        _write(tmp_path, "man.json", man if man is not None else _manifest()),
    )


# --- acceptance 1: fail closed with a named BLOCKED -------------------------


def test_missing_inventory_blocked(tmp_path):
    man = _write(tmp_path, "man.json", _manifest())
    with pytest.raises(tc.TargetCheckpointError, match="BLOCKED.*missing.*inv.json"):
        tc.select_target_from_c9068(str(tmp_path / "inv.json"), man)


def test_missing_manifest_blocked(tmp_path):
    inv = _write(tmp_path, "inv.json", _inventory())
    with pytest.raises(tc.TargetCheckpointError, match="BLOCKED.*missing.*man.json"):
        tc.select_target_from_c9068(inv, str(tmp_path / "man.json"))


def test_malformed_inventory_blocked(tmp_path):
    inv, man = _both(tmp_path, inv="{not json")
    with pytest.raises(tc.TargetCheckpointError, match="BLOCKED.*malformed"):
        tc.select_target_from_c9068(inv, man)


def test_malformed_manifest_blocked(tmp_path):
    inv, man = _both(tmp_path, man="[{broken")
    with pytest.raises(tc.TargetCheckpointError, match="BLOCKED.*malformed"):
        tc.select_target_from_c9068(inv, man)


def test_zero_sha_verified_staged_checkpoints_blocked(tmp_path):
    inv, man = _both(tmp_path, man=_manifest(weights_sha=None))
    with pytest.raises(tc.TargetCheckpointError, match="BLOCKED.*zero sha-verified staged"):
        tc.select_target_from_c9068(inv, man)


def test_no_staged_verified_files_blocked(tmp_path):
    inv, man = _both(tmp_path, man=_manifest(staged_verified=[]))
    with pytest.raises(tc.TargetCheckpointError, match="BLOCKED.*zero sha-verified staged"):
        tc.select_target_from_c9068(inv, man)


# --- acceptance 2: deterministic newest-mtime rule, reject unstaged/unhashed -


def test_unstaged_newer_alt_is_rejected():
    sel = tc.select_target_from_c9068_artifacts(_inventory(), _manifest())
    assert sel["checkpoint_id"].endswith("step_000097_adapter")
    assert sel["checkpoint_id"].startswith("sapo-27b-ai-20260907T085136Z")
    assert sel["sha256"] == SHA_A
    assert any("alt" in r and "unstaged" in r for r in sel["rejected"])


def test_unhashed_staged_entry_rejected_from_selection():
    man = _manifest(staged_verified=[{"name": "adapter_config.json"}])  # no sha256
    with pytest.raises(tc.TargetCheckpointError, match="BLOCKED.*zero sha-verified staged"):
        tc.select_target_from_c9068_artifacts(_inventory(), man)


def test_newest_mtime_wins_among_staged_candidates():
    man = _manifest()
    man["other_staged"] = [
        {
            "checkpoint_id": "runX/step_000050_adapter",
            "box_path": "/root/work/outputs/runX/step_000050_adapter",
            "mtime_utc": "2026-09-09T00:00:00Z",
            "sha256": "c" * 64,
            "staged_verified": [{"name": "adapter_config.json", "sha256": "c" * 64}],
        }
    ]
    sel = tc.select_target_from_c9068_artifacts(_inventory(), man)
    assert sel["checkpoint_id"] == "runX/step_000050_adapter"  # newer mtime wins
    assert sel["sha256"] == "c" * 64


# --- acceptance 3: banked artifact shape ------------------------------------


def test_banked_artifact_required_keys(tmp_path):
    inv, man = _both(tmp_path)
    sel = tc.select_target_from_c9068(inv, man)
    out = str(tmp_path / "c9063_target_checkpoint.json")
    tc.bank_target_checkpoint(sel, out)
    with open(out, encoding="utf-8") as f:
        art = json.load(f)
    for key in ("checkpoint_id", "sha256", "inventory_path", "selected_at_utc", "selection_rule"):
        assert key in art, key
    assert re.match(r"^[0-9a-f]{64}$", art["sha256"])
    assert art["status"] == "PINNED"
    assert set(art["consumer_cards"]) == {"C-9009", "C-9016"}
    # weights are transport-blocked Mac-side; the artifact must say so, not guess
    assert art["weights_staged_mac_side"] is False
