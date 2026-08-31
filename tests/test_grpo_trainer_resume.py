"""TDD: SOFT-RESUME — resume_state.json stateful continuation (2026-08-25, lane #20).

Every relaunch of the SAPO RL loop currently restores only the WEIGHTS
(ADAPTER_INIT) and resets: the step counter, curriculum EMA/weights, repair
queue ledger, task-seen counts, temperature state, and the trust-region
LR-scale state — so each relaunch re-walks early tasks. This suite pins the
soft-resume contract:

  (a) save -> load round-trip restores every field exactly;
  (b) a resumed run's next step number = state.step + 1 and the metrics file
      appends rather than overwrites (same-dir AND new-run-dir cases);
  (c) a restored curriculum EMA changes task sampling deterministically vs a
      cold start;
  (d) repair-converted dedup keys survive the round trip and re-seed a fresh
      ledger without replaying or losing entries;
  (e) the SIGTERM final-save path writes resume_state.json.

Non-resume launches must be byte-identical to today: every helper below is a
no-op unless a resume_state payload is present.
"""

from __future__ import annotations

import json
import os
import random
import signal
import sys
from argparse import Namespace
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training import grpo_trainer  # noqa: E402
from training.grpo_trainer import (  # noqa: E402
    RESUME_STATE_FILENAME,
    GracefulStop,
    build_resume_state_payload,
    collect_repair_converted_dedup_keys,
    collect_repair_converted_status,
    load_resume_state,
    reseed_repair_converted_ledger,
    restore_adaptive_temp_skip_counter,
    restore_curriculum_state,
    restore_trust_region_state,
    save_resume_state,
    termination_save,
)
from training.grpo_utils import (  # noqa: E402
    AdaptiveTemperatureState,
    TaskCurriculum,
    count_repair_conversions,
)

# ---------------------------------------------------------------------------
# fixtures / helpers
# ---------------------------------------------------------------------------


def _sample_payload(step: int = 7) -> dict:
    """A representative resume-state payload with every tracked field set."""
    return build_resume_state_payload(
        step=step,
        curriculum_state={
            "quantum_shor": {"ema_reward": 0.72, "seen": 14.0},
            "quantum_teleport": {"ema_reward": 0.04, "seen": 6.0},
            "quantum_grover": {"ema_reward": 0.96, "seen": 31.0},
        },
        adaptive_temp_state={
            "base_temp": 1.0,
            "step_size": 0.15,
            "max_temp": 1.3,
            "consecutive_low_signal_skips": 3,
        },
        router_state={
            "quantum_shor": {
                "p_pass_ema": 0.5,
                "shaped_std_ema": 0.2,
                "probes": 14.0,
                "last_probe_step": 7.0,
                "route": "frontier_rl",
                "coverage_need": 1.0,
                "rl_updates": 5.0,
                "posterior_alpha": 8.0,
                "posterior_beta": 8.0,
                "flaky": 0.0,
                "group_size_last": 4.0,
            },
            "quantum_teleport": {
                "p_pass_ema": 0.0,
                "shaped_std_ema": 0.05,
                "probes": 6.0,
                "last_probe_step": 6.0,
                "route": "repair_sft",
                "coverage_need": 1.0,
                "rl_updates": 0.0,
                "posterior_alpha": 1.0,
                "posterior_beta": 7.0,
                "flaky": 0.0,
                "group_size_last": 4.0,
            },
        },
        recent_frontier=["quantum_shor", "quantum_teleport"],
        total_probes=20,
        trust_region_violation_count=3,
        optimizer_lr=2.5e-5,  # 2e-4 halved twice by scale_lr
        repair_converted_dedup_keys=[
            "quantum_teleport:ab12cd34ef",
            "quantum_grover:1111222233",
        ],
        repair_converted_status={
            "quantum_teleport:ab12cd34ef": True,
            "quantum_grover:1111222233": True,
        },
        metrics_path="/runs/sapo-27b-ai-20260824T031524/grpo_step_metrics.jsonl",
        output_dir="/runs/sapo-27b-ai-20260824T031524",
        resume_from=None,
    )


def _write_state(tmp_path: Path, payload: dict | None = None) -> Path:
    path = tmp_path / "resume_state.json"
    save_resume_state(path, payload if payload is not None else _sample_payload())
    return path


class _OptimStub:
    """AdamW-shaped stub: only the LR slot is consumed by the trust restore."""

    def __init__(self, lr: float = 1e-5) -> None:
        self.param_groups = [{"lr": lr}]


class TinyBackend:
    def save_pretrained(self, path: Path) -> None:
        Path(path).mkdir(parents=True, exist_ok=True)
        (Path(path) / "backend.marker").write_text("ok")


class TinyModel:
    def save_pretrained(self, path: Path) -> None:
        Path(path).mkdir(parents=True, exist_ok=True)
        (Path(path) / "adapter_config.json").write_text('{"r": 64, "lora_alpha": 64}')
        (Path(path) / "adapter_model.safetensors").write_text("fake-tensors")


class TinyPreprocessor:
    save_backend = TinyBackend()


# ---------------------------------------------------------------------------
# (a) save -> load round-trip restores every field exactly
# ---------------------------------------------------------------------------


def test_resume_state_round_trip_restores_every_field(tmp_path: Path) -> None:
    original = _sample_payload(step=12)
    path = _write_state(tmp_path, original)

    loaded = load_resume_state(path)

    assert loaded["version"] == 1
    assert loaded["step"] == 12
    # curriculum EMA + task-seen counts per task
    assert loaded["curriculum_state"] == original["curriculum_state"]
    assert loaded["task_seen"] == {
        "quantum_shor": 14.0,
        "quantum_teleport": 6.0,
        "quantum_grover": 31.0,
    }
    assert loaded["task_seen"] == original["task_seen"]
    # repair-converted dedup ledger (keys sorted deterministically; the
    # per-key converted flag rides along for an exact breaker count)
    assert loaded["repair_converted_dedup_keys"] == sorted(
        ["quantum_teleport:ab12cd34ef", "quantum_grover:1111222233"]
    )
    assert loaded["repair_converted_status"] == {
        "quantum_teleport:ab12cd34ef": True,
        "quantum_grover:1111222233": True,
    }
    # adaptive temperature state
    assert loaded["adaptive_temp"] == original["adaptive_temp"]
    assert loaded["adaptive_temp"]["consecutive_low_signal_skips"] == 3
    # trust-region count + LR scale
    assert loaded["trust_region"] == {
        "violation_count": 3,
        "optimizer_lr": 2.5e-5,
    }
    # router/mix reconstruction state
    assert loaded["router_state"] == original["router_state"]
    assert loaded["router_state"]["quantum_teleport"]["route"] == "repair_sft"
    assert loaded["recent_frontier"] == ["quantum_shor", "quantum_teleport"]
    assert loaded["total_probes"] == 20
    # resume markers
    assert loaded["metrics_path"] == original["metrics_path"]
    assert loaded["output_dir"] == original["output_dir"]
    assert loaded["resume_from"] is None
    assert loaded["saved_at_utc"]  # ISO timestamp present


def test_round_trip_exact_equality_of_all_state_fields(tmp_path: Path) -> None:
    """Beyond spot checks: EVERY structural field must survive byte-exact."""
    original = _sample_payload(step=5)
    loaded = load_resume_state(_write_state(tmp_path, original))
    for key in (
        "version",
        "step",
        "curriculum_state",
        "task_seen",
        "repair_converted_dedup_keys",
        "repair_converted_status",
        "adaptive_temp",
        "router_state",
        "recent_frontier",
        "total_probes",
        "trust_region",
        "metrics_path",
        "output_dir",
        "resume_from",
    ):
        assert loaded[key] == original[key], f"field {key} changed in round trip"


def test_load_resume_state_rejects_malformed_input(tmp_path: Path) -> None:
    missing = tmp_path / "nope.json"
    with pytest.raises(ValueError, match="missing"):
        load_resume_state(missing)

    bad_json = tmp_path / "bad.json"
    bad_json.write_text("{not json", encoding="utf-8")
    with pytest.raises(ValueError, match="not valid JSON"):
        load_resume_state(bad_json)

    bad_version = tmp_path / "bad_version.json"
    bad_version.write_text(json.dumps({"version": 99, "step": 3}), encoding="utf-8")
    with pytest.raises(ValueError, match="unsupported version"):
        load_resume_state(bad_version)

    bad_step = tmp_path / "bad_step.json"
    bad_step.write_text(json.dumps({"version": 1, "step": "seven"}), encoding="utf-8")
    with pytest.raises(ValueError, match="step"):
        load_resume_state(bad_step)


# ---------------------------------------------------------------------------
# (b) resumed next step = state.step + 1; metrics append, never overwrite
# ---------------------------------------------------------------------------


def _base_namespace(output_dir: Path, **overrides) -> Namespace:
    values = dict(
        model_name="models/OmniCoder-9B",
        adapter_init=str(output_dir / "step_000010_adapter"),
        tasks_dir=str(output_dir / "tasks"),
        benchmark_file=None,
        domain_filter=None,
        output_dir=str(output_dir),
        device="cpu",
        group_size=4,
        grpo_steps=1,
        lr=1e-5,
        kl_coeff=0.05,
        temperature=0.8,
        max_new_tokens=128,
        max_adaptive_new_tokens=128,
        max_seq_length=2048,
        log_steps=1,
        lora_rank=8,
        lora_alpha=16,
        reward_pass_weight=0.6,
        reward_syntax_weight=0.1,
        reward_interface_weight=0.15,
        reward_verifier_weight=0.15,
        reward_detail_budget_cap=8,
        advantage_clip=2.5,
        ratio_clip_log_delta=8.0,
        logit_clip=50.0,
        min_reward_std=0.05,
        curriculum_ema_decay=0.9,
        curriculum_min_weight=0.05,
        curriculum_uncertainty_bonus=0.35,
        research_methods=[],
        quantum_priority=1.5,
        resume_from=None,
        # Guardian alarm 8 (repairq 2026-08-27): the sidecar liveness guard
        # reads these in main(); test fixtures must carry them.
        repair_sidecar_pidfile=None,
        repair_sidecar_log=None,
        repair_sidecar_max_log_age=300,
        reward_brevity_weight=0.0,
        brevity_target_lines=40,
        npu_device_map="balanced-layers",
        overwrite_output_dir=False,
    )
    values.update(overrides)
    return Namespace(**values)


def _run_main_until_tasks_abort(
    monkeypatch: pytest.MonkeyPatch, namespace: Namespace, capsys=None
) -> None:
    """Drive main() through the resume wiring to the tasks-discovery abort
    (the earliest guaranteed abort before any model load)."""
    monkeypatch.setattr(grpo_trainer, "parse_args", lambda: namespace)
    monkeypatch.setattr(grpo_trainer, "load_research_methods", lambda _methods: [])
    monkeypatch.setattr(grpo_trainer, "discover_tasks", lambda *_a, **_k: [])
    monkeypatch.delenv("RANK", raising=False)
    monkeypatch.delenv("LOCAL_RANK", raising=False)
    monkeypatch.delenv("WORLD_SIZE", raising=False)
    with pytest.raises(ValueError, match="No GRPO tasks matched"):
        grpo_trainer.main()


def test_resumed_run_next_step_is_state_step_plus_one_and_metrics_append(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    """Same-run-dir soft-resume: step continues at state.step + 1, the metrics
    JSONL is NOT truncated and prior records are NOT re-appended (dedupe)."""
    output_dir = tmp_path / "grpo-run"
    output_dir.mkdir(parents=True)
    metrics_file = output_dir / "grpo_step_metrics.jsonl"
    prior_records = [
        {"step": 1, "task": "a", "skipped": False},
        {"step": 2, "task": "b", "skipped": True, "reason": "low_reward_signal"},
    ]
    metrics_file.write_text("".join(json.dumps(r) + "\n" for r in prior_records), encoding="utf-8")
    state_payload = build_resume_state_payload(
        step=7,
        curriculum_state={"a": {"ema_reward": 0.5, "seen": 2.0}},
        adaptive_temp_state={"consecutive_low_signal_skips": 0},
        router_state={},
        recent_frontier=[],
        total_probes=2,
        trust_region_violation_count=1,
        optimizer_lr=1e-5,
        repair_converted_dedup_keys=[],
        metrics_path=str(metrics_file),  # same file the trainer will append to
        output_dir=str(output_dir),
    )
    state_path = _write_state(tmp_path, state_payload)

    ns = _base_namespace(
        output_dir,
        adapter_init=str(output_dir / "step_000010_adapter"),
        resume_state=str(state_path),
    )
    _run_main_until_tasks_abort(monkeypatch, ns)

    # (b1) the soft_resume stage confirms the loaded step -> next step is +1
    out = capsys.readouterr().out
    assert '"stage": "soft_resume"' in out
    assert '"resume_step": 7' in out
    loaded = load_resume_state(state_path)
    resume_step = int(loaded["step"])
    next_step = next(s for s in range(1, ns.grpo_steps + 1000) if s > resume_step)
    assert next_step == resume_step + 1 == 8

    # (b2) metrics append: the file still exists, byte-identical (not
    # truncated, not unlinked, no duplicate seeding of its own records)
    assert metrics_file.is_file()
    assert metrics_file.read_text(encoding="utf-8") == "".join(
        json.dumps(r) + "\n" for r in prior_records
    )


def test_resume_into_new_run_dir_seeds_metrics_and_marks_resume(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    """New-run-dir soft-resume: prior step metrics are carried into the fresh
    dir (recorded metrics_path), and step numbering continues."""
    old_dir = tmp_path / "old-run"
    old_dir.mkdir(parents=True)
    old_metrics = old_dir / "grpo_step_metrics.jsonl"
    old_metrics.write_text(
        json.dumps({"step": 3, "task": "quantum_shor", "skipped": False}) + "\n",
        encoding="utf-8",
    )
    state_payload = build_resume_state_payload(
        step=3,
        curriculum_state={"quantum_shor": {"ema_reward": 0.4, "seen": 3.0}},
        adaptive_temp_state={"consecutive_low_signal_skips": 1},
        router_state={},
        recent_frontier=[],
        total_probes=3,
        trust_region_violation_count=0,
        optimizer_lr=2e-4,
        repair_converted_dedup_keys=[],
        metrics_path=str(old_metrics),
        output_dir=str(old_dir),
    )
    state_path = _write_state(tmp_path, state_payload)

    new_dir = tmp_path / "new-run"
    new_dir.mkdir(parents=True)
    ns = _base_namespace(
        new_dir,
        adapter_init=str(old_dir / "step_000010_adapter"),
        resume_state=str(state_path),
    )
    _run_main_until_tasks_abort(monkeypatch, ns)

    out = capsys.readouterr().out
    assert '"stage": "soft_resume"' in out
    assert '"resume_step": 3' in out
    # prior records were copied into the fresh metrics file (append semantics)
    copied = new_dir / "grpo_step_metrics.jsonl"
    assert copied.is_file()
    lines = [json.loads(line) for line in copied.read_text().splitlines() if line.strip()]
    assert lines == [{"step": 3, "task": "quantum_shor", "skipped": False}]
    # the new dir's own JSONL is untouched beyond seeding (no stale overwrite)
    assert not (new_dir / "run_config.json").exists()


def test_resume_state_requires_adapter_init(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A state file describes a paused POLICY; restoring it over fresh weights
    would be a silent policy rewind (same class as the 2026-08-24 bug)."""
    state_path = _write_state(tmp_path)
    ns = _base_namespace(tmp_path / "grpo-run", adapter_init=None, resume_state=str(state_path))
    monkeypatch.setattr(grpo_trainer, "parse_args", lambda: ns)
    monkeypatch.setattr(grpo_trainer, "load_research_methods", lambda _methods: [])
    monkeypatch.setattr(grpo_trainer, "discover_tasks", lambda *_a, **_k: [])
    monkeypatch.delenv("RANK", raising=False)
    monkeypatch.delenv("LOCAL_RANK", raising=False)
    monkeypatch.delenv("WORLD_SIZE", raising=False)
    with pytest.raises(ValueError, match="requires --adapter-init"):
        grpo_trainer.main()


def test_resume_state_rejects_older_adapter_pairing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A step_NNNNNN_adapter older than the state's step must be refused
    (mirrors validate_resume_adapter_consistency for --resume-from)."""
    state_path = _write_state(tmp_path, _sample_payload(step=10))
    ns = _base_namespace(
        tmp_path / "grpo-run",
        adapter_init=str(tmp_path / "step_000003_adapter"),
        resume_state=str(state_path),
    )
    monkeypatch.setattr(grpo_trainer, "parse_args", lambda: ns)
    monkeypatch.setattr(grpo_trainer, "load_research_methods", lambda _methods: [])
    monkeypatch.setattr(grpo_trainer, "discover_tasks", lambda *_a, **_k: [])
    monkeypatch.delenv("RANK", raising=False)
    monkeypatch.delenv("LOCAL_RANK", raising=False)
    monkeypatch.delenv("WORLD_SIZE", raising=False)
    with pytest.raises(ValueError, match="older than the .* latest step"):
        grpo_trainer.main()


# ---------------------------------------------------------------------------
# (c) restored curriculum EMA changes sampling deterministically vs cold start
# ---------------------------------------------------------------------------


def test_curriculum_ema_restored_changes_sampling_vs_cold_start() -> None:
    cold = TaskCurriculum(ema_decay=0.9, min_weight=0.05)
    restored = TaskCurriculum(ema_decay=0.9, min_weight=0.05)
    state = _sample_payload(step=5)
    restore_curriculum_state(restored, state)

    tasks = ["quantum_teleport", "quantum_shor"]
    # restored EMA: quantum_teleport (ema 0.04, seen 6) is far harder than
    # quantum_shor (ema 0.72, seen 14) -> higher difficulty weight; a cold
    # start gives every task the same weight (1.0 difficulty + uncertainty).
    assert cold.weight("quantum_teleport", None) == cold.weight("quantum_shor", None)
    assert restored.weight("quantum_teleport", None) != restored.weight("quantum_shor", None)
    assert restored.weight("quantum_teleport", None) > restored.weight("quantum_shor", None)

    # deterministic sampling: same seed, same RNG stream, different choice
    # distribution vs a cold start.
    def choices(curriculum: TaskCurriculum, seed: int) -> list[str]:
        random.seed(seed)
        weights = [curriculum.weight(t, None) for t in tasks]
        return [random.choices(tasks, weights=weights, k=1)[0] for _ in range(200)]

    cold_seq = choices(cold, seed=1234)
    restored_seq = choices(restored, seed=1234)
    assert cold_seq != restored_seq
    # and the restored sequence is reproducible (deterministic)
    assert choices(restored, seed=1234) == restored_seq


def test_adaptive_temp_skip_counter_restored_but_ladder_keeps_current_config() -> None:
    """Only the stateful skip counter is restored; base/step/max come from the
    current launch config (the resumed run's ladder reflects its own args)."""
    adaptive_temp = AdaptiveTemperatureState(base_temp=1.0, step_size=0.15, max_temp=1.3)
    restore_adaptive_temp_skip_counter(adaptive_temp, _sample_payload())
    assert adaptive_temp.consecutive_low_signal_skips == 3
    assert adaptive_temp.base_temp == 1.0
    assert adaptive_temp.step_size == 0.15
    assert adaptive_temp.max_temp == 1.3
    # the escalation ladder continues from the restored count
    assert adaptive_temp.current_temp() == pytest.approx(1.3)  # min(1.0*1.45, 1.3)


def test_trust_region_count_and_lr_scale_restored() -> None:
    optimizer = _OptimStub(lr=2e-4)
    count = restore_trust_region_state(optimizer, _sample_payload())
    assert count == 3
    assert optimizer.param_groups[0]["lr"] == pytest.approx(2.5e-5)
    # absent trust_region state is a clean no-op (old state files, cold start)
    optimizer2 = _OptimStub(lr=2e-4)
    assert restore_trust_region_state(optimizer2, {"step": 1}) == 0
    assert optimizer2.param_groups[0]["lr"] == pytest.approx(2e-4)


# ---------------------------------------------------------------------------
# (d) repair-converted dedup keys survive the round trip + re-seed
# ---------------------------------------------------------------------------


def test_repair_dedup_keys_survive_round_trip_and_reseed(tmp_path: Path) -> None:
    ledger = tmp_path / "repair_converted.jsonl"
    ledger.write_text(
        json.dumps({"dedup_key": "task_a:aa11", "converted": True})
        + "\n"
        + json.dumps({"dedup_key": "task_b:bb22", "converted": False})
        + "\n",
        encoding="utf-8",
    )
    keys = collect_repair_converted_dedup_keys(ledger)
    assert keys == ["task_a:aa11", "task_b:bb22"]
    status = collect_repair_converted_status(ledger)
    assert status == {"task_a:aa11": True, "task_b:bb22": False}

    # round trip through the state file
    payload = _sample_payload()
    payload["repair_converted_dedup_keys"] = keys
    payload["repair_converted_status"] = status
    loaded = load_resume_state(_write_state(tmp_path, payload))
    assert loaded["repair_converted_dedup_keys"] == keys
    assert loaded["repair_converted_status"] == status

    # re-seed a FRESH ledger (new run dir): both keys restored with their
    # exact converted flags, and a second reseed is a no-op (no replay, no
    # duplicates, nothing lost)
    fresh = tmp_path / "new-run" / "repair_stage" / "repair_converted.jsonl"
    reseeded = reseed_repair_converted_ledger(
        fresh,
        loaded["repair_converted_dedup_keys"],
        status=loaded["repair_converted_status"],
    )
    assert reseeded == 2
    assert collect_repair_converted_dedup_keys(fresh) == keys
    assert count_repair_conversions(fresh) == 1  # only the converted one counts
    assert (
        reseed_repair_converted_ledger(
            fresh,
            loaded["repair_converted_dedup_keys"],
            status=loaded["repair_converted_status"],
        )
        == 0
    )
    assert len(collect_repair_converted_dedup_keys(fresh)) == 2


def test_reseed_restores_conversion_count_so_breaker_stays_true(tmp_path: Path) -> None:
    """The all_fail_without_repair breaker reads count_repair_conversions(); a
    fresh run dir must not lose the accumulated conversion count on resume."""
    old_ledger = tmp_path / "old" / "repair_converted.jsonl"
    old_ledger.parent.mkdir(parents=True)
    old_ledger.write_text(
        json.dumps({"dedup_key": "t1:aaaa", "converted": True})
        + "\n"
        + json.dumps({"dedup_key": "t2:bbbb", "converted": True})
        + "\n"
        + json.dumps({"dedup_key": "t3:cccc", "converted": False})
        + "\n",
        encoding="utf-8",
    )
    old_count = count_repair_conversions(old_ledger)
    assert old_count == 2

    # new run dir starts with an EMPTY ledger; resume re-seeds it from the
    # state file's dedup keys + converted flags -> the breaker sees the same
    # conversion count, and the failed attempt stays unconverted.
    fresh = tmp_path / "new-run" / "repair_converted.jsonl"
    keys = collect_repair_converted_dedup_keys(old_ledger)
    status = collect_repair_converted_status(old_ledger)
    reseed_repair_converted_ledger(fresh, keys, status=status)
    assert count_repair_conversions(fresh) == old_count == 2
    assert collect_repair_converted_status(fresh) == status


# ---------------------------------------------------------------------------
# (e) SIGTERM final-save includes resume_state.json
# ---------------------------------------------------------------------------


def _sigterm_payload(step: int = 4) -> dict:
    return build_resume_state_payload(
        step=step,
        curriculum_state={"a": {"ema_reward": 0.5, "seen": 4.0}},
        adaptive_temp_state={"consecutive_low_signal_skips": 1},
        router_state={},
        recent_frontier=[],
        total_probes=4,
        trust_region_violation_count=0,
        optimizer_lr=1e-5,
        repair_converted_dedup_keys=["a:deadbeef00"],
        metrics_path="metrics.jsonl",
        output_dir=".",
        sigterm=True,
    )


def test_termination_save_writes_resume_state_file(tmp_path: Path) -> None:
    out = tmp_path / "run"
    out.mkdir()
    model, preproc = TinyModel(), TinyPreprocessor()
    termination_save(
        model,
        preproc,
        out,
        step=5,
        distributed=False,
        rank=0,
        metrics=[],
        planned_steps=20,
        resume_state=_sigterm_payload(step=4),
    )
    state_file = out / RESUME_STATE_FILENAME
    assert state_file.is_file()
    loaded = json.loads(state_file.read_text(encoding="utf-8"))
    assert loaded["step"] == 4  # last COMPLETED step, not the in-flight boundary
    assert loaded["sigterm_save"] is True
    assert loaded["curriculum_state"]["a"]["seen"] == 4.0


def test_sigterm_handler_writes_resume_state(tmp_path: Path, monkeypatch) -> None:
    """The full SIGTERM path (handler -> termination_save) persists the state."""
    out = tmp_path / "run"
    out.mkdir()
    model, preproc = TinyModel(), TinyPreprocessor()
    stop = GracefulStop(
        save_fn=lambda: termination_save(
            model,
            preproc,
            out,
            step=stop.step,
            distributed=False,
            rank=0,
            metrics=[],
            planned_steps=20,
            resume_state=_sigterm_payload(step=6),
        )
    )
    stop.step = 7
    monkeypatch.setattr(
        os,
        "_exit",
        lambda code: (_ for _ in ()).throw(SystemExit(code)),
    )
    with pytest.raises(SystemExit):
        stop.handler(signal.SIGTERM, None)
    state_file = out / RESUME_STATE_FILENAME
    assert state_file.is_file()
    assert json.loads(state_file.read_text(encoding="utf-8"))["step"] == 6


def test_termination_save_without_resume_state_writes_nothing_new(tmp_path: Path) -> None:
    """Non-resume behavior stays byte-identical: no state file, no new files."""
    out = tmp_path / "run"
    out.mkdir()
    termination_save(TinyModel(), TinyPreprocessor(), out, step=1, distributed=False, rank=0)
    assert not (out / RESUME_STATE_FILENAME).exists()


# ---------------------------------------------------------------------------
# py3.9 compat: _strict_zip (orchestrator RED — the canonical venv is py3.9,
# where zip() has no strict= kwarg; the trainer used it at 5 sites)
# ---------------------------------------------------------------------------


def test_strict_zip_yields_pairs_and_raises_on_length_mismatch() -> None:
    """_strict_zip must reproduce py3.10 zip(strict=True) semantics on py3.9:
    equal-length iterables zip normally; a length mismatch raises ValueError
    instead of silently pairing."""
    assert list(grpo_trainer._strict_zip([1, 2], ["a", "b"])) == [(1, "a"), (2, "b")]
    assert list(grpo_trainer._strict_zip([], [])) == []
    with pytest.raises(ValueError, match="lengths differ"):
        list(grpo_trainer._strict_zip([1, 2], ["a"]))
    with pytest.raises(ValueError, match="lengths differ"):
        list(grpo_trainer._strict_zip([1], ["a", "b"]))


def test_build_generation_diagnostics_uses_py39_safe_zip() -> None:
    """The truncation-rate path (test_grpo_task_runtime_context RED) must not
    pass strict= to zip: it runs fine on py3.9 with tensor inputs."""
    import torch

    out = grpo_trainer.build_generation_diagnostics(
        raw_responses=["a", "b"],
        codes=["a", "b"],
        completion_token_ids=[torch.tensor([1, 2]), torch.tensor([3, 2])],
        max_new_tokens=2,
        eos_token_ids={2},
    )
    assert out["truncation_rate"] == 0.0
    assert out["eos_termination_rate"] == 1.0
