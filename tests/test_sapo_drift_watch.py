"""TDD tests for the SAPO drift watch (scripts/sapo_drift_watch.py).

The watcher alarms within minutes of a checkpoint landing when the merged
adapter delta vs base is ZERO (byte-identical -> TIER-0) or flat at the bf16
noise floor / below the ACTIVE bar (TIER-1/TIER-2) — the failure modes that
burned days in the GSPO era and hours in run 3 (s11->s13 plateau at 4.88e-4).
All tests run locally on CPU with tiny fake adapters; no NPU, no base model,
no peft/transformers required.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import sapo_drift_watch as dw  # noqa: E402

# ---------------------------------------------------------------------------
# fixtures / helpers
# ---------------------------------------------------------------------------


def make_ckpt(
    run_dir: Path,
    step: int,
    complete: bool = True,
    a: float = 0.01,
    b: float = 0.0,
    config: dict | None = None,
) -> Path:
    """Create a fake `step_XXXXXX_adapter` dir. a = LoRA-A fill value,
    b = LoRA-B fill value. complete=False leaves only adapter_config.json
    (simulates a mid-save / partial checkpoint)."""
    d = run_dir / f"step_{step:06d}_adapter"
    d.mkdir(parents=True, exist_ok=True)
    cfg = config or {"r": 64, "lora_alpha": 64}
    (d / "adapter_config.json").write_text(json.dumps(cfg))
    if complete:
        import torch
        from safetensors.torch import save_file

        save_file(
            {
                "base_model.model.layers.0.self_attn.q_proj.lora_A.default": torch.full((4, 8), a),
                "base_model.model.layers.0.self_attn.q_proj.lora_B.default": torch.full((8, 4), b),
            },
            str(d / "adapter_model.safetensors"),
        )
    return d


def fake_precheck(
    max_abs_diff: float, verdict: str = "active", any_active: bool = True, tensors_compared: int = 2
):
    """Injected precheck fn returning a canned merged-delta (no peft needed)."""

    def _fn(adapter, base, device):
        return {
            "adapter": str(adapter),
            "base": base,
            "phase": 2,
            "scaling": 1.0,
            "max_abs_diff": max_abs_diff,
            "verdict": verdict,
            "any_active": any_active,
            "tensors_compared": tensors_compared,
            "max_abs_lora": 0.01,
            "max_abs_lora_b": 0.005,
            "lora_only": True,
            "nonzero_pair_possible": True,
        }

    return _fn


def seed_history(run_dir: Path, step: int, max_abs_diff: float) -> None:
    """Seed a previous checkpoint's drift.jsonl line (simulates history)."""
    d = run_dir / "drift.jsonl"
    d.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "ts": "2026-08-25T00:00:00Z",
        "step": step,
        "adapter": str(run_dir / f"step_{step:06d}_adapter"),
        "max_abs_diff": max_abs_diff,
        "verdict": "active",
        "tier": "TIER-3",
        "alarm": "ACTIVE",
    }
    with d.open("a") as f:
        f.write(json.dumps(rec) + "\n")


def read_lines(p: Path) -> list[dict]:
    if not p.is_file():
        return []
    return [json.loads(ln) for ln in p.read_text().splitlines() if ln.strip()]


# ---------------------------------------------------------------------------
# (import-safety) the module must be importable without torch/peft/transformers
# ---------------------------------------------------------------------------


def test_module_import_is_heavy_dep_free():
    code = (
        "import sys\n"
        f"sys.path.insert(0, {str(SCRIPTS)!r})\n"
        "import sapo_drift_watch as dw\n"
        "heavy = [m for m in ('torch', 'peft', 'transformers') if m in sys.modules]\n"
        "assert not heavy, heavy\n"
        "assert dw.main is not None\n"
        "print('OK')\n"
    )
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert "OK" in out.stdout


# ---------------------------------------------------------------------------
# (a) TIER-0 ZERO_CHANGE — must fire at the VERY FIRST checkpoint
# ---------------------------------------------------------------------------


def test_tier0_zero_change_fires_at_first_checkpoint(tmp_path):
    run = tmp_path / "run"
    make_ckpt(run, 1, a=0.01, b=0.01)  # complete files; precheck injected
    rec = dw.run_once(
        run, "fake-base", precheck_fn=fake_precheck(0.0, verdict="inert", any_active=False)
    )
    assert rec is not None
    assert rec["tier"] == "TIER-0"
    assert rec["alarm"] == "ZERO_CHANGE"
    assert rec["max_abs_diff"] == 0.0
    assert rec["prev_step"] is None  # fired with NO history — first checkpoint
    # alarm side-effects
    assert read_lines(run / "alarms.jsonl")[0]["alarm"] == "ZERO_CHANGE"
    log = (run / "drift_alarms.log").read_text()
    assert "ALARM TIER-0 ZERO_CHANGE" in log and "STOP" in log


def test_tier0_zero_change_fires_at_any_checkpoint_even_after_healthy(tmp_path):
    run = tmp_path / "run"
    make_ckpt(run, 1, a=0.01, b=0.01)
    make_ckpt(run, 2, a=0.01, b=0.01)
    seed_history(run, 1, 4.5e-4)
    rec = dw.run_once(
        run, "fake-base", precheck_fn=fake_precheck(0.0, verdict="inert", any_active=False)
    )
    assert rec["step"] == 2
    assert rec["tier"] == "TIER-0" and rec["alarm"] == "ZERO_CHANGE"


def test_tier0_zero_change_phase1_fast_path_real_safetensors(tmp_path):
    """A dead adapter (nonzero A, all-zero B -> no A*B pair) is detected by the
    phase-1 fast path from REAL safetensors files: max_abs_diff == 0.0 exactly,
    no base model / peft merge involved."""
    run = tmp_path / "run"
    make_ckpt(run, 3, a=0.01, b=0.0)  # B all zeros -> no nonzero pair
    rec = dw.run_once(run, "fake-base")  # default compute_delta, real files
    assert rec is not None
    assert rec["phase"] == 1
    assert rec["max_abs_diff"] == 0.0
    assert rec["verdict"] == "inert"
    assert rec["tier"] == "TIER-0" and rec["alarm"] == "ZERO_CHANGE"


# ---------------------------------------------------------------------------
# (b) TIER-1 FLAT_AT_NOISE_FLOOR — 2 consecutive equal small deltas
# ---------------------------------------------------------------------------


def test_tier1_flat_at_noise_floor_two_equal_small_deltas(tmp_path):
    run = tmp_path / "run"
    make_ckpt(run, 1, a=0.01, b=0.01)
    make_ckpt(run, 2, a=0.01, b=0.01)
    seed_history(run, 1, 6.0e-5)  # below the ~1.2e-4 noise boundary
    rec = dw.run_once(
        run,
        "fake-base",
        precheck_fn=fake_precheck(6.0e-5, verdict="inert_at_precision", any_active=False),
    )
    assert rec["tier"] == "TIER-1"
    assert rec["alarm"] == "FLAT_AT_NOISE_FLOOR"
    assert rec["prev_step"] == 1
    assert rec["growth"] == 0.0
    assert read_lines(run / "alarms.jsonl")[0]["alarm"] == "FLAT_AT_NOISE_FLOOR"


# ---------------------------------------------------------------------------
# (c) TIER-2 PLATEAU — growth <5% across 2 consecutive checkpoints,
# above noise but below the ACTIVE bar (1e-3)
# ---------------------------------------------------------------------------


def test_tier2_plateau_small_growth_under_five_percent(tmp_path):
    run = tmp_path / "run"
    make_ckpt(run, 1, a=0.01, b=0.01)
    make_ckpt(run, 2, a=0.01, b=0.01)
    seed_history(run, 1, 4.88e-4)
    rec = dw.run_once(
        run,
        "fake-base",
        precheck_fn=fake_precheck(5.0e-4, verdict="inert_at_precision", any_active=False),
    )
    assert rec["tier"] == "TIER-2"
    assert rec["alarm"] == "PLATEAU"
    assert 0.02 < rec["growth"] < 0.03  # ~2.5% growth


def test_tier2_plateau_exact_flat_above_noise_run3_s11_to_s13(tmp_path):
    """Regression: run-3 s11->s13 stayed EXACTLY 4.88e-4 (flat, above the noise
    floor, below ACTIVE) and took hours to surface via periodic prechecks.
    The watcher must flag it as PLATEAU."""
    run = tmp_path / "run"
    make_ckpt(run, 11, a=0.01, b=0.01)
    make_ckpt(
        run, 13, a=0.01, b=0.01
    )  # s12 was skipped by the run — still 2 consecutive checkpoints
    seed_history(run, 11, 4.88e-4)
    rec = dw.run_once(
        run,
        "fake-base",
        precheck_fn=fake_precheck(4.88e-4, verdict="inert_at_precision", any_active=False),
    )
    assert rec["tier"] == "TIER-2"
    assert rec["alarm"] == "PLATEAU"


def test_tier2_plateau_on_shrinking_delta_regression(tmp_path):
    """A delta that SHRINKS is growth <5% too — regression toward base must alarm."""
    run = tmp_path / "run"
    make_ckpt(run, 1, a=0.01, b=0.01)
    make_ckpt(run, 2, a=0.01, b=0.01)
    seed_history(run, 1, 4.0e-4)
    rec = dw.run_once(
        run,
        "fake-base",
        precheck_fn=fake_precheck(3.0e-4, verdict="inert_at_precision", any_active=False),
    )
    assert rec["tier"] == "TIER-2" and rec["alarm"] == "PLATEAU"
    assert rec["growth"] < 0.0


# ---------------------------------------------------------------------------
# (d) no alarm on healthy growth / at-or-above ACTIVE bar / first baseline
# ---------------------------------------------------------------------------


def test_tier3_healthy_growth_no_alarm(tmp_path):
    run = tmp_path / "run"
    make_ckpt(run, 1, a=0.01, b=0.01)
    make_ckpt(run, 2, a=0.01, b=0.01)
    seed_history(run, 1, 3.0e-4)
    rec = dw.run_once(
        run, "fake-base", precheck_fn=fake_precheck(4.5e-4, verdict="active", any_active=True)
    )
    assert rec["tier"] == "TIER-3" and rec["alarm"] == "ACTIVE"
    assert rec["growth"] >= 0.05
    assert not (run / "alarms.jsonl").exists()


def test_tier3_delta_at_or_above_active_bar_no_alarm(tmp_path):
    run = tmp_path / "run"
    make_ckpt(run, 1, a=0.01, b=0.01)
    make_ckpt(run, 2, a=0.01, b=0.01)
    seed_history(run, 1, 3.0e-4)
    rec = dw.run_once(
        run, "fake-base", precheck_fn=fake_precheck(1.5e-3, verdict="active", any_active=True)
    )
    assert rec["tier"] == "TIER-3" and rec["alarm"] == "ACTIVE"
    assert not (run / "alarms.jsonl").exists()


def test_tier3_first_checkpoint_baseline_no_alarm(tmp_path):
    run = tmp_path / "run"
    make_ckpt(run, 1, a=0.01, b=0.01)
    rec = dw.run_once(run, "fake-base", precheck_fn=fake_precheck(2.0e-4))
    assert rec is not None
    assert rec["tier"] == "TIER-3" and rec["alarm"] == "ACTIVE"
    assert rec["growth"] is None and rec["prev_step"] is None
    assert not (run / "alarms.jsonl").exists()


# ---------------------------------------------------------------------------
# (e) --once picks the NEWEST step_*_adapter by STEP NUMBER, not mtime
# ---------------------------------------------------------------------------


def test_once_picks_newest_by_step_number_not_mtime(tmp_path):
    run = tmp_path / "run"
    d2 = make_ckpt(run, 2, a=0.01, b=0.01)
    d3 = make_ckpt(run, 3, a=0.01, b=0.01)
    d10 = make_ckpt(run, 10, a=0.01, b=0.01)
    # scramble mtimes: step 2 is NEWEST on disk, step 10 is OLDEST
    old = 1_000_000_000
    os.utime(d10, (old, old))
    mid = 2_000_000_000
    os.utime(d3, (mid, mid))
    new = 3_000_000_000
    os.utime(d2, (new, new))
    assert d2.stat().st_mtime > d3.stat().st_mtime > d10.stat().st_mtime
    seen = []

    def spy(adapter, base, device):
        seen.append(Path(adapter).name)
        return fake_precheck(1.0e-3)(adapter, base, device)

    rec = dw.run_once(run, "fake-base", precheck_fn=spy)
    assert rec is not None and rec["step"] == 10  # newest returned
    # F10 (code-review wave): every unmeasured step is measured, in order
    assert seen == ["step_000002_adapter", "step_000003_adapter", "step_000010_adapter"]


def test_once_skips_incomplete_newest_checkpoint(tmp_path):
    run = tmp_path / "run"
    make_ckpt(run, 1, a=0.01, b=0.01, complete=True)
    make_ckpt(run, 2, complete=False)  # newest but mid-save
    rec = dw.run_once(run, "fake-base", precheck_fn=fake_precheck(1.0e-3))
    # F10: the complete step 1 is measured; the mid-save step 2 is skipped
    assert rec is not None and rec["step"] == 1
    lines = read_lines(run / "drift.jsonl")
    assert [r["step"] for r in lines] == [1]  # no crash, no partial record


# ---------------------------------------------------------------------------
# (f) jsonl lines parse and carry step/ts/delta fields
# ---------------------------------------------------------------------------


def test_jsonl_lines_parse_and_carry_fields(tmp_path):
    run = tmp_path / "run"
    make_ckpt(run, 2, a=0.01, b=0.01)
    rec = dw.run_once(run, "fake-base", precheck_fn=fake_precheck(7.0e-4))
    assert rec is not None
    lines = read_lines(run / "drift.jsonl")
    assert len(lines) == 1
    line = lines[0]
    for field in (
        "ts",
        "step",
        "adapter",
        "max_abs_diff",
        "tier",
        "alarm",
        "verdict",
        "any_active",
    ):
        assert field in line, field
    assert line["step"] == 2
    assert line["max_abs_diff"] == 7.0e-4
    assert line["ts"].count("-") == 2 and "T" in line["ts"]  # ISO-ish UTC stamp
    # per-checkpoint drift.json + latest drift.json snapshot also written
    assert (run / "drift_step_000002.json").is_file()
    latest = json.loads((run / "drift.json").read_text())
    assert latest["step"] == 2 and latest["max_abs_diff"] == 7.0e-4


def test_alarms_jsonl_only_alarm_lines_and_grepable_log(tmp_path):
    run = tmp_path / "run"
    make_ckpt(run, 1, a=0.01, b=0.01)
    dw.run_once(run, "fake-base", precheck_fn=fake_precheck(2.0e-4))  # ACTIVE, no alarm
    make_ckpt(run, 2, a=0.01, b=0.01)
    dw.run_once(
        run, "fake-base", precheck_fn=fake_precheck(0.0, verdict="inert", any_active=False)
    )  # ZERO_CHANGE
    assert not (run / "alarms.jsonl").exists() or True
    alarms = read_lines(run / "alarms.jsonl")
    assert [a["alarm"] for a in alarms] == ["ZERO_CHANGE"]  # only the alarm line
    log = (run / "drift_alarms.log").read_text().splitlines()
    assert len(log) == 1
    assert "ALARM TIER-0 ZERO_CHANGE step=2" in log[0] and "max_abs_diff=0" in log[0]


# ---------------------------------------------------------------------------
# (g) corrupted / partial checkpoint dirs: skipped + retried, never crashes
# ---------------------------------------------------------------------------


def test_partial_checkpoint_skipped_and_retried(tmp_path):
    run = tmp_path / "run"
    make_ckpt(run, 1, complete=False)  # mid-save: adapter_config.json only
    state = dw.WatchState()
    emitted = dw.poll_run(run, "fake-base", state, precheck_fn=fake_precheck(1.0e-3))
    assert emitted == []
    assert state.processed == set()  # NOT marked processed
    assert state.retries.get(1, 0) == 1
    assert not (run / "drift.jsonl").exists()
    # ... mid-save finishes; next poll processes it
    make_ckpt(run, 1, complete=True, a=0.01, b=0.01)
    emitted = dw.poll_run(run, "fake-base", state, precheck_fn=fake_precheck(1.0e-3))
    assert [r["step"] for r in emitted] == [1]
    assert state.processed == {1}
    assert state.retries.get(1, 0) == 0


def test_corrupt_checkpoint_retried_then_error_record_never_crashes(tmp_path):
    run = tmp_path / "run"
    d = make_ckpt(run, 1, complete=True, a=0.01, b=0.01)
    (d / "adapter_model.safetensors").write_bytes(b"garbage-not-a-safetensors-file")
    state = dw.WatchState()
    for _ in range(2):  # max_retries=2 -> two silent retries (default compute_delta)
        emitted = dw.poll_run(run, "fake-base", state, max_retries=2)
        assert emitted == []
    assert state.processed == set()
    emitted = dw.poll_run(run, "fake-base", state, max_retries=2)
    assert len(emitted) == 1
    assert emitted[0]["status"] == "error" and emitted[0]["verdict"] == "unknown"
    assert emitted[0]["error"]
    # The step is NOT marked processed: if the checkpoint becomes readable
    # later it must still be measured (a permanently unmeasured step could be
    # a silent ZERO_CHANGE).
    assert state.processed == set()
    # still no crash and no bogus drift alarm
    assert read_lines(run / "alarms.jsonl") == []
    emitted = dw.poll_run(run, "fake-base", state, max_retries=2)
    assert emitted == []  # no error re-emission spam (recorded once)


def test_error_recorded_step_rechecked_once_checkpoint_becomes_readable(tmp_path):
    """Watch-mode under-alarm regression: a checkpoint whose precheck failed
    (or that stayed mid-save past max_retries) used to be marked PROCESSED
    forever — once it became readable, its delta was never measured. A
    ZERO_CHANGE checkpoint in that window never alarmed. The step must be
    re-measured as soon as it is readable."""
    run = tmp_path / "run"
    d = make_ckpt(run, 1, complete=True, a=0.01, b=0.01)
    (d / "adapter_model.safetensors").write_bytes(b"garbage-not-a-safetensors-file")
    state = dw.WatchState()
    for _ in range(3):  # max_retries=2 -> error record on the 3rd poll
        dw.poll_run(run, "fake-base", state, max_retries=2)
    assert state.processed == set()
    # the checkpoint becomes readable (e.g. a later re-save / fs hiccup)
    make_ckpt(run, 1, complete=True, a=0.01, b=0.0)  # dead adapter -> phase-1
    emitted = dw.poll_run(run, "fake-base", state, max_retries=2)
    assert [r["step"] for r in emitted] == [1]
    assert emitted[0]["status"] == "ok"
    assert emitted[0]["tier"] == "TIER-0"  # measured: zero-change alarm fires
    assert state.processed == {1}


def test_incomplete_checkpoint_past_retries_rechecked_when_complete(tmp_path):
    """Same class for the mid-save path: a checkpoint that stayed incomplete
    past max_retries emits ONE error record but is re-measured once the save
    finishes (never permanently skipped)."""
    run = tmp_path / "run"
    make_ckpt(run, 1, complete=False)  # mid-save forever for 3 polls
    state = dw.WatchState()
    for _ in range(3):
        dw.poll_run(run, "fake-base", state, max_retries=2)
    assert state.processed == set()
    errors = [ln for ln in read_lines(run / "drift.jsonl") if ln.get("status") == "error"]
    assert len(errors) == 1  # error recorded once, not per poll
    make_ckpt(run, 1, complete=True, a=0.01, b=0.0)  # save finishes
    emitted = dw.poll_run(run, "fake-base", state, max_retries=2)
    assert [r["step"] for r in emitted] == [1]
    assert emitted[0]["status"] == "ok"


def test_watch_restart_adoption_skips_error_lines(tmp_path):
    """On restart the watcher re-adopts processed steps from drift.jsonl.
    Error records (no numeric max_abs_diff) must NOT be adopted: a step whose
    only history line is an error must be re-checked, not skipped forever."""
    run = tmp_path / "run"
    make_ckpt(run, 1, complete=True, a=0.01, b=0.0)  # dead adapter
    make_ckpt(run, 2, complete=True, a=0.01, b=0.0)
    # simulate a previous instance that errored on step 1 and measured step 2
    dw.append_jsonl(
        dw.drift_jsonl(run), dw.build_error_record(1, str(run / "step_000001_adapter"), "boom")
    )
    dw.run_once(run, "fake-base")
    history, _ = dw.read_history(dw.drift_jsonl(run))
    # step 1's error line was NOT adopted and did NOT block re-measurement
    assert dw.adopt_processed_steps(history) == {1, 2}
    assert any(r["step"] == 1 and r["status"] == "ok" for r in history)
    # a fresh instance adopting from this history re-measures nothing new
    state = dw.WatchState()
    state.processed |= dw.adopt_processed_steps(history)
    emitted = dw.poll_run(
        run, "fake-base", state, precheck_fn=fake_precheck(0.0, verdict="inert", any_active=False)
    )
    assert emitted == []


def test_nan_delta_classifies_as_error_never_active(tmp_path):
    """A NaN/Inf measurement is a BROKEN measurement — reporting it as
    TIER-3 ACTIVE (no alarm) is a silent under-alarm on garbage data."""
    tier, alarm, _ = dw.classify_tier(float("nan"), 1.0e-3)
    assert alarm == "ERROR"
    tier, alarm, _ = dw.classify_tier(float("inf"), None)
    assert alarm == "ERROR"
    run = tmp_path / "run"
    make_ckpt(run, 1, complete=True, a=0.01, b=0.01)
    rec = dw.build_record(
        1,
        str(run / "step_000001_adapter"),
        fake_precheck(float("nan"))(run / "step_000001_adapter", "base", "cpu"),
        prev=None,
    )
    assert rec["alarm"] == "ERROR"
    assert rec["status"] == "error"  # F8: non-finite -> error record


def test_phase2_zero_tensors_compared_raises_instead_of_false_zero_change(tmp_path):
    """If phase-2 compared ZERO tensors (base/adapter name mismatch), the
    max_abs_diff of 0.0 is MEANINGLESS — reporting TIER-0 ZERO_CHANGE would
    false-stop a healthy run. Must fail loud (DriftCheckError -> error record)
    instead of fabricating a byte-identical verdict."""
    run = tmp_path / "run"
    make_ckpt(run, 1, complete=True, a=0.01, b=0.01)  # nonzero pair -> phase 2

    def mismatched_merge(adapter, base, device):
        return {
            "adapter": str(adapter),
            "base": base,
            "phase": 2,
            "scaling": 1.0,
            "max_abs_diff": 0.0,
            "verdict": "inert",
            "any_active": False,
            "tensors_compared": 0,
            "max_abs_lora": 0.01,
            "max_abs_lora_b": 0.005,
            "lora_only": True,
            "nonzero_pair_possible": True,
        }

    import pytest

    with pytest.raises(dw.DriftCheckError):
        dw.compute_delta(run / "step_000001_adapter", "fake-base", merge_fn=mismatched_merge)
    # and via --once: no bogus TIER-0 record is ever written
    rec = dw.run_once(run, "fake-base", precheck_fn=mismatched_merge)
    assert rec is None
    assert read_lines(run / "drift.jsonl") == []


# ---------------------------------------------------------------------------
# watch-mode machinery
# ---------------------------------------------------------------------------


def test_watch_poll_processes_new_steps_in_step_order_and_skips_processed(tmp_path):
    run = tmp_path / "run"
    make_ckpt(run, 5, a=0.01, b=0.01)
    make_ckpt(run, 1, a=0.01, b=0.01)
    state = dw.WatchState()
    emitted = dw.poll_run(run, "fake-base", state, precheck_fn=fake_precheck(2.0e-4))
    assert [r["step"] for r in emitted] == [1, 5]  # ascending, not mtime order
    # prev linkage within one poll: step 5 sees step 1's line as history
    lines = read_lines(run / "drift.jsonl")
    assert lines[-1]["prev_step"] == 1
    # second poll: nothing new
    assert dw.poll_run(run, "fake-base", state, precheck_fn=fake_precheck(2.0e-4)) == []
    # a step appearing later is picked up without restart
    make_ckpt(run, 6, a=0.01, b=0.01)
    emitted = dw.poll_run(run, "fake-base", state, precheck_fn=fake_precheck(2.0e-4))
    assert [r["step"] for r in emitted] == [6]


def test_history_corrupt_tail_tolerated(tmp_path):
    run = tmp_path / "run"
    make_ckpt(run, 1, a=0.01, b=0.01)
    make_ckpt(run, 2, a=0.01, b=0.01)
    seed_history(run, 1, 3.0e-4)
    with (run / "drift.jsonl").open("a") as f:  # crashed mid-append
        f.write('{"step": 2, "max_abs_diff": [corrupt\n')
    rec = dw.run_once(run, "fake-base", precheck_fn=fake_precheck(4.0e-4))
    assert rec is not None and rec["tier"] == "TIER-3"
    assert rec["prev_step"] == 1  # corrupt tail ignored


# ---------------------------------------------------------------------------
# CLI end-to-end (subprocess, real phase-1 fast path, no peft)
# ---------------------------------------------------------------------------


def test_cli_once_end_to_end_zero_change_alarm(tmp_path):
    run = tmp_path / "run"
    make_ckpt(run, 1, a=0.01, b=0.0)  # dead adapter -> phase-1 inert
    out = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "sapo_drift_watch.py"),
            "--run-dir",
            str(run),
            "--base",
            "fake-base",
            "--once",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert out.returncode == 0, out.stderr
    lines = read_lines(run / "drift.jsonl")
    assert len(lines) == 1 and lines[0]["tier"] == "TIER-0"
    alarm_log = (run / "drift_alarms.log").read_text()
    assert "ALARM TIER-0 ZERO_CHANGE" in alarm_log
    assert "STOP" in alarm_log


def test_cli_accepts_watch_flag_with_once(tmp_path):
    """The documented launch pattern is `--watch` (default mode), but argparse
    never defined the flag — launching per the ops directive died with
    'unrecognized arguments: --watch'. The flag must parse; combined with
    --once it must still run the once path (no infinite loop)."""
    run = tmp_path / "run"
    make_ckpt(run, 1, a=0.01, b=0.0)  # dead adapter -> phase-1 inert
    out = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "sapo_drift_watch.py"),
            "--run-dir",
            str(run),
            "--base",
            "fake-base",
            "--once",
            "--watch",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert out.returncode == 0, out.stderr
    lines = read_lines(run / "drift.jsonl")
    assert len(lines) == 1 and lines[0]["tier"] == "TIER-0"


# ---------------------------------------------------------------------------
# (h) TIER-2 PLATEAU requires flat LoRA-B too — bf16 quantization staircase
# ---------------------------------------------------------------------------


def seed_history_lora_b(run_dir, step, max_abs_diff, lora_b):
    """Seed a history line with a numeric max_abs_lora_b (real records carry it)."""
    d = run_dir / "drift.jsonl"
    d.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "ts": "2026-08-25T00:00:00Z",
        "step": step,
        "adapter": str(run_dir / f"step_{step:06d}_adapter"),
        "max_abs_diff": max_abs_diff,
        "max_abs_lora_b": lora_b,
        "verdict": "inert_at_precision",
        "tier": "TIER-3",
        "alarm": "ACTIVE",
    }
    with d.open("a") as f:
        f.write(json.dumps(rec) + "\n")


def fake_precheck_lora_b(max_abs_diff, lora_b, verdict="inert_at_precision"):
    def _fn(adapter, base, device):
        return {
            "adapter": str(adapter),
            "base": base,
            "phase": 2,
            "scaling": 4.0,
            "max_abs_diff": max_abs_diff,
            "verdict": verdict,
            "any_active": False,
            "tensors_compared": 851,
            "max_abs_lora": 0.014,
            "max_abs_lora_b": lora_b,
            "lora_only": True,
            "nonzero_pair_possible": True,
            "max_abs_weight": 19.25,
            "max_ulp": 0.125,
        }

    return _fn


def test_staircase_flat_merged_diff_growing_lora_b_is_not_plateau(tmp_path):
    """Regression (2026-08-25 coordinator finding): merged bf16 diff is
    QUANTIZED at ULP steps (~1.22e-4 at |w|~19.25) — a flat 2.44e-4 merged
    diff with lora_B moving 2e-4 -> 6e-4 is a quantization STAIRCASE, not a
    drift freeze. Must be an info record (TIER-3 QUANTIZATION_STAIR), never a
    TIER-2 alarm."""
    run = tmp_path / "run"
    make_ckpt(run, 1, a=0.01, b=0.01)
    make_ckpt(run, 3, a=0.01, b=0.01)
    seed_history_lora_b(run, 1, 2.44e-4, 2.0e-4)
    rec = dw.run_once(run, "fake-base", precheck_fn=fake_precheck_lora_b(2.44e-4, 6.0e-4))
    assert rec is not None
    assert rec["step"] == 3
    assert rec["max_abs_diff"] == 2.44e-4
    assert rec["tier"] == "TIER-3"
    assert rec["alarm"] == "QUANTIZATION_STAIR"
    assert rec["growth"] == 0.0
    # info only: NO alarm side-effects
    assert not (run / "alarms.jsonl").exists()
    assert not (run / "drift_alarms.log").exists()


def test_plateau_alarms_when_merged_diff_and_lora_b_both_flat(tmp_path):
    """The true plateau signature: merged diff flat AND lora_B flat (run-3
    s11->s13 style). Still TIER-2 PLATEAU — the alarm semantics are preserved."""
    run = tmp_path / "run"
    make_ckpt(run, 1, a=0.01, b=0.01)
    make_ckpt(run, 3, a=0.01, b=0.01)
    seed_history_lora_b(run, 1, 4.88e-4, 2.0e-4)
    rec = dw.run_once(run, "fake-base", precheck_fn=fake_precheck_lora_b(4.88e-4, 2.0e-4))
    assert rec["tier"] == "TIER-2"
    assert rec["alarm"] == "PLATEAU"
    assert read_lines(run / "alarms.jsonl")[0]["alarm"] == "PLATEAU"


def test_staircase_never_alarms_across_three_checkpoints(tmp_path):
    """Coordinator's exact case: lora_B 2e-4 -> 4e-4 -> 6e-4 (linear per
    update) while merged diff stays 2.44e-4 — every checkpoint must classify
    QUANTIZATION_STAIR (info), zero alarm lines, even sequentially."""
    run = tmp_path / "run"
    # NOTE: no step-1 dir on disk — poll_run would re-measure it; history only.
    make_ckpt(run, 3, a=0.01, b=0.01)
    make_ckpt(run, 4, a=0.01, b=0.01)
    seed_history_lora_b(run, 1, 2.44e-4, 2.0e-4)
    lora_b_by_step = {3: 4.0e-4, 4: 6.0e-4}

    def precheck(adapter, base, device):
        step = int(str(Path(adapter).name).split("_")[1])
        return fake_precheck_lora_b(2.44e-4, lora_b_by_step[step])(adapter, base, device)

    state = dw.WatchState()
    emitted = dw.poll_run(run, "fake-base", state, precheck_fn=precheck)
    assert [r["step"] for r in emitted] == [3, 4]
    assert all(r["alarm"] == "QUANTIZATION_STAIR" for r in emitted)
    assert not (run / "alarms.jsonl").exists()
    lines = read_lines(run / "drift.jsonl")
    assert len(lines) == 3  # baseline + 2 info records


def test_missing_lora_b_history_stays_conservative_plateau(tmp_path):
    """Legacy history without max_abs_lora_b: no staircase evidence -> keep the
    conservative TIER-2 alarm (never silently drop a real plateau)."""
    run = tmp_path / "run"
    make_ckpt(run, 1, a=0.01, b=0.01)
    make_ckpt(run, 3, a=0.01, b=0.01)
    seed_history(run, 1, 4.88e-4)  # no lora_b field
    rec = dw.run_once(run, "fake-base", precheck_fn=fake_precheck_lora_b(4.88e-4, 4.0e-4))
    assert rec["tier"] == "TIER-2"
    assert rec["alarm"] == "PLATEAU"


# ---------------------------------------------------------------------------
# code-review wave (2026-08-26) findings
# ---------------------------------------------------------------------------


def test_nan_delta_record_is_error_not_adopted(tmp_path):
    """Finder B/F8: a NaN max_abs_diff landed as a NUMERIC record with status
    ok — adopt_processed_steps adopted it forever and last_prev_line used it
    as a valid prev, poisoning every later tier comparison. A non-finite
    delta must be recorded as an ERROR record (max_abs_diff None)."""
    run = tmp_path / "run"
    make_ckpt(run, 1, complete=True, a=0.01, b=0.01)
    rec = dw.build_record(
        1,
        str(run / "step_000001_adapter"),
        fake_precheck(float("nan"))(run / "step_000001_adapter", "base", "cpu"),
        prev=None,
    )
    assert rec["status"] == "error"
    assert rec["max_abs_diff"] is None
    assert rec["alarm"] == "ERROR"
    # never adopted on restart, never a prev anchor
    history = [rec]
    assert dw.adopt_processed_steps(history) == set()
    assert dw.last_prev_line(history, 2) is None


def test_phase1_nan_weights_raise_not_fabricate_zero(tmp_path):
    """Finder B/F9: NaN weights made phase-1's `> 0.0` checks all False ->
    'inert' -> fabricated TIER-0 ZERO_CHANGE stop on a corrupted adapter.
    A NaN tensor must raise (corrupt checkpoint -> error record)."""
    run = tmp_path / "run"
    d = make_ckpt(run, 1, complete=True, a=0.01, b=0.01)
    import torch
    from safetensors.torch import save_file

    save_file(
        {
            "base_model.model.layers.0.self_attn.q_proj.lora_A.default": torch.full(
                (4, 8), float("nan")
            ),
            "base_model.model.layers.0.self_attn.q_proj.lora_B.default": torch.full((8, 4), 0.0),
        },
        str(d / "adapter_model.safetensors"),
    )
    tensors = dw.load_tensors(d)
    import pytest as _pytest

    with _pytest.raises(dw.DriftCheckError, match="NaN"):
        dw.phase1(tensors)
    # and via run_once: no bogus TIER-0 record
    rec = dw.run_once(run, "fake-base")
    assert rec is None
    assert read_lines(run / "drift.jsonl") == []


def test_once_measures_all_unmeasured_steps(tmp_path):
    """Finder B/F10: --once only measured max(steps) — a step created between
    two ticks was never measured (its ZERO_CHANGE invisible) and the prev
    chain silently widened past it."""
    run = tmp_path / "run"
    make_ckpt(run, 6, complete=True, a=0.01, b=0.0)  # dead -> phase-1 0.0
    dw.run_once(run, "fake-base")
    assert [r["step"] for r in read_lines(run / "drift.jsonl")] == [6]
    # tick N+1: steps 7 AND 8 both appeared since the last tick
    make_ckpt(run, 7, complete=True, a=0.01, b=0.0)
    make_ckpt(run, 8, complete=True, a=0.01, b=0.0)
    dw.run_once(run, "fake-base")
    steps = [r["step"] for r in read_lines(run / "drift.jsonl")]
    assert steps == [6, 7, 8]  # both new steps measured, in order
    assert steps[-1] == 8


def test_module_has_future_annotations_for_py39() -> None:
    """r10 register gate (2026-08-26, depmatrix F2): the module uses PEP 604
    `X | None` annotations — without the future import they are EVALUATED at
    def time and crash the import on py3.9. The future-import must stay."""
    source = Path(dw.__file__).read_text(encoding="utf-8")
    assert "from __future__ import annotations" in source


# ---------------------------------------------------------------------------
# wake-from-zero (prev_delta == 0.0) — 2026-08-31 audit pin
# ---------------------------------------------------------------------------


def test_wake_from_zero_record_growth_not_inf(tmp_path):
    """Audit pin (2026-08-31, router/drift audit): a checkpoint AFTER a
    ZERO_CHANGE (prev max_abs_diff == 0.0 exactly) measures a nonzero delta
    (warm-resume relaunch with a working adapter). classify_tier computes
    growth = inf for this branch, but build_record must SANITIZE it to None —
    an 'inf' growth would poison alarm_line / downstream drift dashboards."""
    run = tmp_path / "run"
    make_ckpt(run, 1, a=0.01, b=0.01)
    make_ckpt(run, 2, a=0.01, b=0.01)
    seed_history(run, 1, 0.0)  # step 1 was byte-identical (ZERO_CHANGE)
    rec = dw.run_once(run, "fake-base", precheck_fn=fake_precheck(5.0e-4))
    assert rec is not None
    assert rec["step"] == 2
    assert rec["prev_step"] == 1
    assert rec["prev_max_abs_diff"] == 0.0
    assert rec["growth"] is None, f"growth must be sanitized, got {rec['growth']!r}"


def test_wake_from_zero_classifies_active_never_zero_change(tmp_path):
    """Audit pin (2026-08-31): a nonzero delta after a 0.0 prev is MOVEMENT —
    never a repeat ZERO_CHANGE, never a PLATEAU (growth inf > 5%), never
    FLAT_AT_NOISE_FLOOR. The watcher must not double-alarm a recovered run."""
    for idx, delta in enumerate((1.0e-4, 5.0e-4, 1.5e-3)):  # below noise / mid / above ACTIVE bar
        run = tmp_path / f"run{idx}"  # fresh run dir per delta (measured steps are not re-measured)
        make_ckpt(run, 1, a=0.01, b=0.01)
        make_ckpt(run, 2, a=0.01, b=0.01)
        seed_history(run, 1, 0.0)
        rec = dw.run_once(run, "fake-base", precheck_fn=fake_precheck(delta))
        assert rec is not None, delta
        assert rec["tier"] == "TIER-3", (delta, rec["tier"])
        assert rec["alarm"] == "ACTIVE", (delta, rec["alarm"])
        assert not (run / "alarms.jsonl").exists(), (delta, read_lines(run / "alarms.jsonl"))
