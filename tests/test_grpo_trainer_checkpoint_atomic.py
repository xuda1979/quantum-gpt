"""TDD (coverage lane, PASS 16): checkpoint/resume mechanics.

Before this suite: save_peft_checkpoint_atomic 16/26 (61.5%), _atomic_save_adapter_dir
14/22 (63.6%) — the recovery-dir class (incomplete dir -> renamed aside -> new
save lands complete) was untested; load_resume_state 18/19 (94.7%) — the last
error path unpinned.

Pinned mechanics:

  * save_peft_checkpoint_atomic: a PRE-EXISTING INCOMPLETE checkpoint dir is
    renamed aside to `.incomplete-*` and the new save lands complete — a KILL
    mid-save of a prior run can never block or poison the next save;
  * an already-complete checkpoint dir is a no-op (immutability — no rewrite);
  * a failing save cleans its temp dir and leaves any existing dir intact;
  * the rename-failure recovery path restores the renamed-aside dir;
  * load_resume_state raises actionable ValueErrors on every corrupt class;
  * termination_save with resume_state writes a coherent resume_state.json
    (round-trips through load_resume_state) whose step matches the checkpoint
    dir being written (SIGTERM payload coherence, code-review F2).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.grpo_trainer import (  # noqa: E402
    RESUME_STATE_FILENAME,
    _atomic_save_adapter_dir,
    build_resume_state_payload,
    load_resume_state,
    peft_checkpoint_complete,
    save_peft_checkpoint_atomic,
    termination_save,
)


class TinyBackend:
    """save_pretrained stand-in for the text-preprocessor backend."""

    def __init__(self) -> None:
        self.saved: list[Path] = []

    def save_pretrained(self, path: Path) -> None:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        (path / "backend.marker").write_text("ok")
        self.saved.append(path)


class TinyModel:
    """save_pretrained writes the PEFT files the completeness rule checks for."""

    def __init__(self, fail: bool = False) -> None:
        self.saved: list[Path] = []
        self.fail = fail

    def save_pretrained(self, path: Path) -> None:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        (path / "adapter_config.json").write_text(json.dumps({"r": 64}))
        if not self.fail:
            (path / "adapter_model.safetensors").write_text("fake-tensors")
        self.saved.append(path)


class TinyPreprocessor:
    def __init__(self) -> None:
        self.save_backend = TinyBackend()


def _harness(tmp_path: Path) -> tuple[Path, TinyModel, TinyPreprocessor]:
    out = tmp_path / "run"
    out.mkdir()
    return out, TinyModel(), TinyPreprocessor()


def _complete_at(path: Path) -> bool:
    return peft_checkpoint_complete(path)


def _incomplete_dir(path: Path) -> Path:
    """A dir that LOOKS like a checkpoint but is missing the weights — the
    KILL-mid-save artifact class."""
    path.mkdir(parents=True, exist_ok=True)
    (path / "adapter_config.json").write_text(json.dumps({"r": 64}))
    return path


# ---------------------------------------------------------------------------
# save_peft_checkpoint_atomic — the recovery-dir class
# ---------------------------------------------------------------------------


def test_atomic_save_fresh_dir_lands_complete(tmp_path: Path) -> None:
    out, model, preproc = _harness(tmp_path)
    ckpt = out / "step_000007_adapter"
    saved = save_peft_checkpoint_atomic(model, preproc, ckpt)
    assert saved == ckpt
    assert _complete_at(ckpt)
    assert (ckpt / "backend.marker").is_file()
    # no temp dirs left behind
    assert not list(out.glob(".*.tmp-*"))


def test_atomic_save_existing_complete_dir_is_noop(tmp_path: Path) -> None:
    """Immutability: a complete checkpoint is returned as-is, never rewritten."""
    out, model, preproc = _harness(tmp_path)
    ckpt = out / "step_000005_adapter"
    _incomplete_dir(ckpt)
    (ckpt / "adapter_model.safetensors").write_text("original-tensors")
    save_peft_checkpoint_atomic(model, preproc, ckpt)
    assert model.saved == []  # no rewrite happened
    assert (ckpt / "adapter_model.safetensors").read_text() == "original-tensors"


def test_atomic_save_incomplete_dir_renamed_aside_and_replaced(tmp_path: Path) -> None:
    """THE recovery class: an incomplete prior dir is renamed aside to
    `.incomplete-*` and the new save lands COMPLETE at the canonical path."""
    out, model, preproc = _harness(tmp_path)
    ckpt = out / "step_000003_adapter"
    _incomplete_dir(ckpt)  # prior KILL-mid-save artifact
    save_peft_checkpoint_atomic(model, preproc, ckpt)
    assert _complete_at(ckpt)
    assert (ckpt / "adapter_model.safetensors").read_text() == "fake-tensors"
    aside = list(out.glob(".step_000003_adapter.incomplete-*"))
    assert len(aside) == 1
    # the aside retains the old partial content (forensic value)
    assert (aside[0] / "adapter_config.json").is_file()
    assert not (aside[0] / "adapter_model.safetensors").is_file()
    # exactly one incomplete dir — the second save of a complete dir is a noop
    model2, preproc2 = TinyModel(), TinyPreprocessor()
    save_peft_checkpoint_atomic(model2, preproc2, ckpt)
    assert model2.saved == []


def test_atomic_save_bin_variant_counts_complete(tmp_path: Path) -> None:
    """adapter_model.bin is an acceptable weight file for completeness."""
    out, model, preproc = _harness(tmp_path)
    ckpt = out / "step_000002_adapter"

    class BinModel(TinyModel):
        def save_pretrained(self, path: Path) -> None:
            path = Path(path)
            path.mkdir(parents=True, exist_ok=True)
            (path / "adapter_config.json").write_text("{}")
            (path / "adapter_model.bin").write_text("bin-tensors")
            self.saved.append(path)

    bin_model = BinModel()
    save_peft_checkpoint_atomic(bin_model, preproc, ckpt)
    assert _complete_at(ckpt)


def test_atomic_save_failing_save_cleans_temp_and_keeps_prior(tmp_path: Path) -> None:
    """A failing save must clean its temp dir and leave the prior dir intact
    (the rename-aside only happens after a COMPLETE stage)."""
    out, model, preproc = _harness(tmp_path)
    ckpt = out / "step_000001_adapter"
    _incomplete_dir(ckpt)  # partial prior state
    failing = TinyModel(fail=True)  # never writes adapter_model.safetensors
    with pytest.raises(RuntimeError, match="incomplete PEFT checkpoint"):
        save_peft_checkpoint_atomic(failing, preproc, ckpt)
    assert not list(out.glob(".*.tmp-*"))  # temp cleaned in finally
    # prior dir NOT renamed aside on a failed save (only after a complete stage)
    assert (ckpt / "adapter_config.json").is_file()
    assert not _complete_at(ckpt)
    assert not list(out.glob(".step_000001_adapter.incomplete-*"))


def test_atomic_save_rename_failure_restores_recovery_dir(tmp_path: Path, monkeypatch) -> None:
    """If the final rename fails, the renamed-aside recovery dir is restored —
    no data loss, no duplicate."""

    out, model, preproc = _harness(tmp_path)
    ckpt = out / "step_000009_adapter"
    _incomplete_dir(ckpt)
    real_rename = Path.rename

    def failing_rename(self, target: Path) -> None:
        if ".tmp-" in self.name:
            raise OSError("simulated rename failure on final landing")
        return real_rename(self, target)

    monkeypatch.setattr(Path, "rename", failing_rename)
    with pytest.raises(OSError, match="rename failure"):
        save_peft_checkpoint_atomic(model, preproc, ckpt)
    # recovery: the aside came back to the canonical path
    assert ckpt.exists()
    assert (ckpt / "adapter_config.json").is_file()
    assert not list(out.glob(".step_000009_adapter.incomplete-*"))
    assert not list(out.glob(".*.tmp-*"))


# ---------------------------------------------------------------------------
# _atomic_save_adapter_dir — the live adapter dir (same class, no completeness)
# ---------------------------------------------------------------------------


def test_atomic_adapter_dir_fresh_save(tmp_path: Path) -> None:
    out, model, preproc = _harness(tmp_path)
    adapter_dir = out / "adapter"
    saved = _atomic_save_adapter_dir(model, preproc, adapter_dir)
    assert saved == adapter_dir
    assert (adapter_dir / "adapter_config.json").is_file()
    assert (adapter_dir / "adapter_model.safetensors").is_file()
    assert (adapter_dir / "backend.marker").is_file()
    assert not list(out.glob(".*.tmp-*"))


def test_atomic_adapter_dir_incomplete_prior_renamed_aside(tmp_path: Path) -> None:
    out, model, preproc = _harness(tmp_path)
    adapter_dir = out / "adapter"
    _incomplete_dir(adapter_dir)  # prior KILL-mid-save artifact
    _atomic_save_adapter_dir(model, preproc, adapter_dir)
    assert _complete_at(adapter_dir)
    aside = list(out.glob(".adapter.incomplete-*"))
    assert len(aside) == 1
    # the aside retains the old partial content (forensic value)
    assert (aside[0] / "adapter_config.json").read_text() == json.dumps({"r": 64})
    assert not (aside[0] / "adapter_model.safetensors").exists()


def test_atomic_adapter_dir_rename_failure_restores_recovery_dir(
    tmp_path: Path, monkeypatch
) -> None:
    """The adapter-dir save has the same recovery class: a failed final
    rename restores the renamed-aside dir."""
    out, model, preproc = _harness(tmp_path)
    adapter_dir = out / "adapter"
    _incomplete_dir(adapter_dir)
    real_rename = Path.rename

    def failing_rename(self, target: Path) -> None:
        if ".tmp-" in self.name:
            raise OSError("simulated rename failure on final landing")
        return real_rename(self, target)

    monkeypatch.setattr(Path, "rename", failing_rename)
    with pytest.raises(OSError, match="rename failure"):
        _atomic_save_adapter_dir(model, preproc, adapter_dir)
    assert adapter_dir.exists()
    assert (adapter_dir / "adapter_config.json").is_file()
    assert not list(out.glob(".adapter.incomplete-*"))
    assert not list(out.glob(".*.tmp-*"))


def test_atomic_adapter_dir_skips_backend_when_none(tmp_path: Path) -> None:
    out, model, _preproc = _harness(tmp_path)
    adapter_dir = _atomic_save_adapter_dir(model, None, out / "adapter")
    assert (adapter_dir / "adapter_config.json").is_file()


# ---------------------------------------------------------------------------
# load_resume_state — every corrupt class is an actionable ValueError
# ---------------------------------------------------------------------------


def test_load_resume_state_round_trip(tmp_path: Path) -> None:
    payload = build_resume_state_payload(
        step=7,
        curriculum_state={"t1": {"ema_reward": 0.5, "seen": 3.0}},
        adaptive_temp_state={"base_temp": 1.0},
        router_state={"t1": {"p_pass_ema": 0.5}},
        recent_frontier=["t1"],
        total_probes=12,
        trust_region_violation_count=1,
        optimizer_lr=1e-5,
        repair_converted_dedup_keys=["k1"],
        metrics_path="m.json",
        output_dir="out",
    )
    path = tmp_path / "resume_state.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    loaded = load_resume_state(path)
    assert loaded["step"] == 7
    assert loaded["curriculum_state"]["t1"]["ema_reward"] == 0.5
    assert loaded["task_seen"]["t1"] == 3.0
    assert loaded["trust_region"]["violation_count"] == 1
    assert loaded["sigterm_save"] is False


def test_load_resume_state_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="missing"):
        load_resume_state(tmp_path / "nope.json")


def test_load_resume_state_corrupt_json_raises(tmp_path: Path) -> None:
    path = tmp_path / "resume_state.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(ValueError, match="not valid JSON"):
        load_resume_state(path)


def test_load_resume_state_non_dict_raises(tmp_path: Path) -> None:
    path = tmp_path / "resume_state.json"
    path.write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(ValueError, match="JSON object"):
        load_resume_state(path)


def test_load_resume_state_wrong_version_raises(tmp_path: Path) -> None:
    path = tmp_path / "resume_state.json"
    path.write_text(json.dumps({"version": 99, "step": 1}), encoding="utf-8")
    with pytest.raises(ValueError, match="unsupported version"):
        load_resume_state(path)


def test_load_resume_state_bad_step_raises(tmp_path: Path) -> None:
    for bad in (None, "3", 3.5, True, -1):
        path = tmp_path / "resume_state.json"
        path.write_text(json.dumps({"version": 1, "step": bad}), encoding="utf-8")
        with pytest.raises(ValueError, match="step"):
            load_resume_state(path)


# ---------------------------------------------------------------------------
# termination_save + resume_state — SIGTERM payload coherence round-trip
# ---------------------------------------------------------------------------


def test_termination_save_writes_coherent_resume_state(tmp_path: Path) -> None:
    out, model, preproc = _harness(tmp_path)
    payload = build_resume_state_payload(
        step=5,
        curriculum_state={"t1": {"ema_reward": 0.5, "seen": 3.0}},
        adaptive_temp_state={"base_temp": 1.0},
        router_state={},
        recent_frontier=[],
        total_probes=9,
        trust_region_violation_count=0,
        optimizer_lr=1e-5,
        repair_converted_dedup_keys=[],
        metrics_path="m.json",
        output_dir=str(out),
        sigterm=True,
    )
    adapter_dir = termination_save(
        model,
        preproc,
        out,
        step=5,
        distributed=False,
        rank=0,
        metrics=[{"step": 5, "loss": -0.1}],
        planned_steps=20,
        resume_state=payload,
    )
    assert adapter_dir == out / "adapter"
    state_path = out / RESUME_STATE_FILENAME
    assert state_path.is_file()
    # round-trip: the next launch with --resume-state reads it back exactly
    loaded = load_resume_state(state_path)
    assert loaded == payload
    assert loaded["step"] == 5  # matches the checkpoint dir step_000005_adapter
    assert loaded["sigterm_save"] is True
    assert (out / "step_000005_adapter" / "adapter_config.json").is_file()
    assert (out / "adapter" / "adapter_config.json").is_file()
    assert (out / "grpo_metrics.json").is_file()


def test_termination_save_without_resume_state_writes_no_state(tmp_path: Path) -> None:
    out, model, preproc = _harness(tmp_path)
    termination_save(model, preproc, out, step=1, distributed=False, rank=0)
    assert not (out / RESUME_STATE_FILENAME).exists()
