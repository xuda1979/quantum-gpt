"""C-9109: RED-first tests for the checkpoint inventory refresh loop.

Card acceptance: the refresh consumes the C-9068 inventory scan and
(a) excludes any checkpoint lacking config.json + adapter_config.json + sha256,
(b) fails closed BLOCKED when the prior inventory is missing/malformed;
rewrites the inventory artifact + c9063_target_checkpoint.json only from
sha-verified entries carrying selected_at_utc + prior pin, is idempotent
(no-change refresh updates refreshed_at only), never selects an unstaged or
box-only entry Mac-side, and on absent box transport leaves the inventory
as-is with a named BLOCKED note.
"""

import hashlib
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import c9109_inventory_refresh as c9109  # noqa: E402

NOW_T1 = "2026-09-18T11:00:00Z"
NOW_T2 = "2026-09-18T11:30:00Z"
SHA_A = "a" * 64
SHA_B = "b" * 64


def _entry(
    sha=SHA_A,
    mtime="2026-09-18T01:00:00Z",
    files=None,
    staged=True,
    path="/root/work/outputs/run1/step_000111_adapter",
):
    e = {"path": path, "bytes": 1024, "mtime_utc": mtime, "sha256": sha, "sha": "MEASURED"}
    if files is not None:
        e["files"] = files
    if staged is not None:
        e["staged"] = staged
    return e


def _complete_entry(**kw):
    return _entry(files=["config.json", "adapter_config.json", "adapter_model.safetensors"], **kw)


def _write_inventory(path, checkpoints):
    inv = {"card": "C-9068", "kind": "lora_checkpoint_inventory", "checkpoints": checkpoints}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(inv, f)
    return inv


def _read(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def test_excludes_entries_missing_required_files_or_sha(tmp_path):
    inv_path = str(tmp_path / "inv.json")
    pin_path = str(tmp_path / "pin.json")
    good = _complete_entry()
    no_config = _entry(sha=SHA_B, files=["adapter_config.json"], path="/root/step_000112_adapter")
    no_sha = _entry(
        sha=None, files=["config.json", "adapter_config.json"], path="/root/step_000113_adapter"
    )
    not_a_dict = "garbage-non-dict-checkpoint-entry"
    _write_inventory(inv_path, [no_config, good, no_sha, not_a_dict])
    rec = c9109.refresh_inventory(inv_path, pin_path, now_utc=NOW_T1)
    assert rec["status"] == "PINNED", rec
    inv = _read(inv_path)
    kept = [e["path"] for e in inv["checkpoints"]]
    assert kept == [good["path"]], kept  # incomplete entries excluded
    assert inv["refreshed_by"] == "C-9109"
    pin = _read(pin_path)
    assert pin["status"] == "PINNED"
    assert pin["target"]["sha256"] == SHA_A
    assert pin["target"]["step"] == "step_000111_adapter"
    assert pin["selected_at_utc"] == NOW_T1
    assert pin["prior_pin"] is None
    excluded = set(pin["excluded_incomplete_paths"])
    assert {no_config["path"], no_sha["path"]} <= excluded, excluded


def _foreign_pin():
    """Schema of the LIVE banked C-9089 pin: status PINNED, no 'target' key,
    checkpoint identity at top level (checkpoint_id/box_path/sha256)."""
    return {
        "card": "C-9089",
        "status": "PINNED",
        "checkpoint_id": "sapo-27b-ai-20260907T085136Z/step_000097_adapter",
        "box_path": "/root/work/outputs/sapo-27b-ai-20260907T085136Z/step_000097_adapter",
        "sha256": SHA_A,
        "staged_dir": "harness/state/probes/c9068/staged_s97_0907/",
        "consumer_cards": ["C-9009", "C-9016"],
        "selected_at_utc": "2026-09-18T10:26:03Z",
    }


def test_blocks_when_prior_inventory_missing(tmp_path):
    inv_path = str(tmp_path / "absent.json")
    pin_path = str(tmp_path / "pin.json")
    rec = c9109.refresh_inventory(inv_path, pin_path, now_utc=NOW_T1)
    assert rec["status"] == "BLOCKED"
    assert "missing" in rec["blocked_reason"]
    assert not os.path.exists(inv_path)  # inventory stays as-is
    assert not os.path.exists(pin_path)  # BLOCKED never fabricates a pin
    note = _read(str(tmp_path / c9109.STATUS_NAME))
    assert note["status"] == "BLOCKED"
    assert "missing" in note["blocked_reason"]


def test_blocks_when_prior_inventory_malformed(tmp_path):
    inv_path = str(tmp_path / "inv.json")
    raw = "{not json at all"
    with open(inv_path, "w", encoding="utf-8") as f:
        f.write(raw)
    pin_path = str(tmp_path / "pin.json")
    rec = c9109.refresh_inventory(inv_path, pin_path, now_utc=NOW_T1)
    assert rec["status"] == "BLOCKED"
    assert "malformed" in rec["blocked_reason"]
    with open(inv_path, encoding="utf-8") as f:
        assert f.read() == raw  # inventory untouched
    note = _read(str(tmp_path / c9109.STATUS_NAME))
    assert note["status"] == "BLOCKED"


def test_blocked_never_clobbers_existing_foreign_pin(tmp_path):
    """RED defect: _blocked() save_json'd the pin outright. The live pin is
    C-9089-schema (status PINNED, no 'target' key), so the clobber both
    destroyed banked s97 evidence AND recorded prior_pin=None. BLOCKED must
    leave an existing pin byte-identical and carry the full prior pin in the
    named note artifact."""
    inv_path = str(tmp_path / "inv.json")
    pin_path = str(tmp_path / "pin.json")
    with open(pin_path, "w", encoding="utf-8") as f:
        json.dump(_foreign_pin(), f)
    pin_before = open(pin_path, "rb").read()
    rec = c9109.refresh_inventory(inv_path, pin_path, now_utc=NOW_T1)
    assert rec["status"] == "BLOCKED"
    assert open(pin_path, "rb").read() == pin_before  # pin byte-identical
    note = _read(str(tmp_path / c9109.STATUS_NAME))
    assert note["status"] == "BLOCKED"
    full = note["prior_pin_full"]
    assert full["card"] == "C-9089"
    assert full["checkpoint_id"].endswith("step_000097_adapter")
    assert full["sha256"] == SHA_A


def test_blocks_on_box_only_candidates_without_transport(tmp_path):
    inv_path = str(tmp_path / "inv.json")
    pin_path = str(tmp_path / "pin.json")
    box_only = _complete_entry(staged=False)
    _write_inventory(inv_path, [box_only])
    with open(pin_path, "w", encoding="utf-8") as f:
        json.dump(_foreign_pin(), f)
    pin_before = open(pin_path, "rb").read()
    rec = c9109.refresh_inventory(inv_path, pin_path, now_utc=NOW_T1, box_transport_available=False)
    assert rec["status"] == "BLOCKED"
    assert box_only["path"] in rec["blocked_reason"]  # named, not silent
    with open(inv_path, encoding="utf-8") as f:
        raw_before = f.read()
    _write_inventory(inv_path, [box_only])
    with open(inv_path, encoding="utf-8") as f:
        assert f.read() == raw_before  # inventory stays as-is
    assert open(pin_path, "rb").read() == pin_before  # pin stays as-is
    note = _read(str(tmp_path / c9109.STATUS_NAME))
    assert note["status"] == "BLOCKED"
    assert box_only["path"] in note["blocked_reason"]


def test_no_change_refresh_updates_refreshed_at_only(tmp_path):
    inv_path = str(tmp_path / "inv.json")
    pin_path = str(tmp_path / "pin.json")
    _write_inventory(inv_path, [_complete_entry()])
    c9109.refresh_inventory(inv_path, pin_path, now_utc=NOW_T1)
    inv_after_first = open(inv_path, "rb").read()
    pin1 = _read(pin_path)
    rec2 = c9109.refresh_inventory(inv_path, pin_path, now_utc=NOW_T2)
    assert rec2["status"] == "UNCHANGED"
    assert open(inv_path, "rb").read() == inv_after_first  # not rewritten
    pin2 = _read(pin_path)
    assert pin2["refreshed_at"] == NOW_T2
    assert pin2["selected_at_utc"] == pin1["selected_at_utc"] == NOW_T1
    assert pin2["target"] == pin1["target"]


def test_change_carries_selected_at_utc_and_prior_pin(tmp_path):
    inv_path = str(tmp_path / "inv.json")
    pin_path = str(tmp_path / "pin.json")
    old = _complete_entry(
        sha=SHA_A, mtime="2026-09-17T00:00:00Z", path="/root/run0/step_000100_adapter"
    )
    _write_inventory(inv_path, [old])
    c9109.refresh_inventory(inv_path, pin_path, now_utc=NOW_T1)
    new = _complete_entry(
        sha=SHA_B, mtime="2026-09-18T02:00:00Z", path="/root/run1/step_000150_adapter"
    )
    _write_inventory(inv_path, [old, new])
    rec = c9109.refresh_inventory(inv_path, pin_path, now_utc=NOW_T2)
    assert rec["status"] == "PINNED"
    pin = _read(pin_path)
    assert pin["target"]["sha256"] == SHA_B  # newest sha-verified selected
    assert pin["selected_at_utc"] == NOW_T2
    assert pin["prior_pin"]["sha256"] == SHA_A  # prior carried for diff
    assert pin["prior_pin"]["selected_at_utc"] == NOW_T1
    assert pin["prior_pin_full"]["target"]["sha256"] == SHA_A


def test_gate_staged_s97_manifest_shas_recompute():
    """Mechanical sha-verified gate: the live staged s97 files must still
    recompute to the manifest sha256 values the pin would be built from."""
    probes = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "state", "probes"
    )
    manifest_path = os.path.join(probes, "c9068", "c9068_s97_manifest.json")
    if not os.path.exists(manifest_path):
        pytest.skip("s97 manifest missing: " + manifest_path)
    manifest = _read(manifest_path)
    staged = os.path.join(probes, "c9068", "staged_s97_0907")
    assert manifest["staged_dir"] == "harness/state/probes/c9068/staged_s97_0907/"
    for row in manifest["staged_verified"]:
        with open(os.path.join(staged, row["name"]), "rb") as f:
            digest = hashlib.sha256(f.read()).hexdigest()
        assert digest == row["sha256"], row["name"]
        assert os.path.getsize(os.path.join(staged, row["name"])) == row["size"]
