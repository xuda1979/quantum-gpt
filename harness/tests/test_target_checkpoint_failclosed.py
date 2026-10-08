"""C-9063: RED-first fail-closed validator for the C-9009 target_checkpoint.json
claim-time artifact.

Card acceptance: the validator rejects (a) missing sha256 on a pinned target,
(b) malformed json, (c) unknown step names; an artifact is either a sha-verified
PINNED selection or an UNRESOLVED_FAIL_CLOSED record naming the blocking edge,
never a silent default to s97.
"""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import target_checkpoint as tc  # noqa: E402

VALID_PINNED = {
    "card": "C-9063",
    "goal_card": "C-9009",
    "generated_utc": "2026-09-17T09:00:00Z",
    "status": "PINNED",
    "selection_rule": "newest registered checkpoint, sha-verified",
    "target_checkpoint": {
        "step": "step_000123_adapter",
        "path": "/root/work/outputs/run1/step_000123_adapter",
        "sha256": "a" * 64,
        "source": "C-9036-inventory",
    },
    "fallback_s97": None,
}


def test_valid_pinned_artifact_passes():
    resolved = tc.validate_target_checkpoint(dict(VALID_PINNED))
    assert resolved["target_checkpoint"]["step"] == "step_000123_adapter"


def test_rejects_missing_sha256():
    art = json.loads(json.dumps(VALID_PINNED))
    del art["target_checkpoint"]["sha256"]
    with pytest.raises(tc.TargetCheckpointError, match="sha256"):
        tc.validate_target_checkpoint(art)


def test_rejects_malformed_sha256():
    art = json.loads(json.dumps(VALID_PINNED))
    art["target_checkpoint"]["sha256"] = "deadbeef"
    with pytest.raises(tc.TargetCheckpointError, match="sha256"):
        tc.validate_target_checkpoint(art)


def test_rejects_malformed_json_file(tmp_path):
    p = tmp_path / "target_checkpoint.json"
    p.write_text("{not json at all", encoding="utf-8")
    with pytest.raises(tc.TargetCheckpointError, match="unparseable"):
        tc.validate_target_checkpoint_file(str(p))


def test_rejects_missing_file(tmp_path):
    with pytest.raises(tc.TargetCheckpointError, match="absent"):
        tc.validate_target_checkpoint_file(str(tmp_path / "nope.json"))


def test_rejects_unknown_step_names():
    for bad in ("s97", "step_97_adapter", "checkpoint-3", "step_000123"):
        art = json.loads(json.dumps(VALID_PINNED))
        art["target_checkpoint"]["step"] = bad
        with pytest.raises(tc.TargetCheckpointError, match="unknown step name"):
            tc.validate_target_checkpoint(art)


def test_rejects_unresolved_artifact_carrying_pinned_target():
    art = {
        "card": "C-9063",
        "status": "UNRESOLVED_FAIL_CLOSED",
        "blocking_edge": {"artifacts": "C-9036 inventory", "edge": "box exec down"},
        "target_checkpoint": {"step": "step_000097_adapter", "sha256": "b" * 64},
    }
    with pytest.raises(tc.TargetCheckpointError, match="pinned target"):
        tc.validate_target_checkpoint(art)


def test_valid_unresolved_artifact_names_edge():
    art = {
        "card": "C-9063",
        "goal_card": "C-9009",
        "status": "UNRESOLVED_FAIL_CLOSED",
        "target_checkpoint": None,
        "fallback_s97": None,
        "blocking_edge": {
            "artifacts": "C-9036 inventory FAIL_CLOSED_UNKNOWN; C-9050 registration absent",
            "edge": "box exec transport down on all containers",
        },
    }
    resolved = tc.validate_target_checkpoint(art)
    assert resolved["status"] == "UNRESOLVED_FAIL_CLOSED"


def test_unresolved_requires_blocking_edge():
    art = {
        "card": "C-9063",
        "status": "UNRESOLVED_FAIL_CLOSED",
        "target_checkpoint": None,
    }
    with pytest.raises(tc.TargetCheckpointError, match="blocking_edge"):
        tc.validate_target_checkpoint(art)
