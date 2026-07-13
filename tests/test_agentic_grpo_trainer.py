from __future__ import annotations

import json
from pathlib import Path

from training.agentic_grpo_trainer import (
    WallClockCheckpointState,
    build_job_health_payload,
    build_live_status_payload,
    build_run_started_log_event_payload,
    build_step_log_event_payload,
    build_task_inventory_log_event_payload,
    checkpoint_due,
    classify_failure_detail,
    clear_device_cache,
    emit_training_log_event,
    run_online_eval,
    trajectory_behavior_reward,
)

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_PATH = ROOT / "evals" / "benchmarks" / "agentic_coding_trajectory_training_v1.txt"
HOLDOUT_PATH = ROOT / "evals" / "benchmarks" / "quantum_generalization_holdout_v1.txt"


def _load_ids(path: Path) -> list[str]:
    ids: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            ids.append(line)
    return ids


def test_checkpoint_due_is_time_based() -> None:
    assert checkpoint_due(interval_seconds=3600, last_saved_at=100.0, now=3699.0) is False
    assert checkpoint_due(interval_seconds=3600, last_saved_at=100.0, now=3700.0) is True
    assert checkpoint_due(interval_seconds=0, last_saved_at=100.0, now=99999.0) is False


def test_wallclock_checkpoint_state_can_also_save_by_step() -> None:
    state = WallClockCheckpointState(
        interval_seconds=3600,
        last_saved_at=100.0,
        every_steps=4,
        last_saved_step=8,
    )

    assert state.due(now=101.0, step=11) is False
    assert state.due(now=101.0, step=12) is True
    state.mark_saved(now=101.0, step=12)
    assert state.last_saved_step == 12
    assert state.saved_count == 1
    assert state.due(now=3701.1, step=13) is True


def test_classify_failure_detail_maps_common_bug_shapes() -> None:
    assert classify_failure_detail("SyntaxError: invalid syntax") == "syntax_error"
    assert classify_failure_detail("ModuleNotFoundError: No module named 'foo'") == "import_error"
    assert classify_failure_detail("AssertionError: expected 4 got 3") == "assertion_failure"
    assert classify_failure_detail("TypeError: unsupported operand type(s)") == "type_error"
    assert classify_failure_detail("mystery failure") == "other_failure"


def test_trajectory_behavior_reward_prefers_candidate_writing() -> None:
    class Args:
        trajectory_write_bonus = 0.04
        trajectory_final_bonus = 0.02
        trajectory_timeout_penalty = 0.02
        trajectory_prewrite_test_penalty = 0.02
        trajectory_repeated_read_penalty = 0.01

    read_only = trajectory_behavior_reward(
        {
            "tool_counts": {"read_file": 2, "run_tests": 2},
            "run_tests_before_write_calls": 2,
            "repeated_read_calls": 1,
        },
        terminated="turn_budget",
        args=Args(),
    )
    wrote = trajectory_behavior_reward(
        {"tool_counts": {"read_file": 1, "write_file": 1, "run_tests": 1}},
        terminated="turn_budget",
        args=Args(),
    )
    finalized = trajectory_behavior_reward(
        {"tool_counts": {"read_file": 1, "final_answer": 1}},
        terminated="final_answer",
        args=Args(),
    )

    assert read_only == -0.07
    assert wrote == 0.04
    assert finalized == 0.06


def test_clear_device_cache_uses_npu_empty_cache() -> None:
    class Npu:
        called = False

        def empty_cache(self) -> None:
            self.called = True

    class TorchModule:
        npu = Npu()

    class Device:
        type = "npu"

    clear_device_cache(TorchModule, Device())

    assert TorchModule.npu.called is True


def test_build_live_status_payload_exposes_recent_summary() -> None:
    checkpoint_state = WallClockCheckpointState(
        interval_seconds=3600, last_saved_at=10.0, saved_count=2
    )
    records = [
        {
            "step": 1,
            "mean_reward": 0.25,
            "pass_rate": 0.0,
            "termination_counts": {"final_answer": 1, "turn_budget": 1},
            "skipped": True,
            "reason": "low_reward_signal",
        },
        {
            "step": 2,
            "mean_reward": 0.75,
            "pass_rate": 0.5,
            "loss": 0.2,
            "termination_counts": {"final_answer": 2},
        },
    ]
    payload = build_live_status_payload(
        records=records,
        planned_steps=64,
        checkpoint_state=checkpoint_state,
        latest_checkpoint={"step": 2, "checkpoint_dir": "/tmp/ckpt"},
        latest_online_eval={"step": 2, "pass_rate": 0.5},
        world_size=4,
        status="running",
        started_at=0.0,
        recent_window=10,
        min_read_before_write_rate=0.5,
        min_tests_before_final_rate=0.4,
        max_no_tool_rate=0.2,
    )

    assert payload["status"] == "running"
    assert payload["schema_version"] == 1
    assert payload["summary"]["recorded_steps"] == 2
    assert payload["summary"]["updated_steps"] == 1
    assert payload["summary"]["skip_reasons"] == {"low_reward_signal": 1}
    assert payload["recent"]["termination_counts"] == {"final_answer": 3, "turn_budget": 1}
    assert payload["alerts"] == []
    assert payload["latest_checkpoint"]["step"] == 2
    assert payload["online_eval_latest"]["pass_rate"] == 0.5
    assert payload["checkpoint_every_steps"] == 0
    assert payload["last_checkpoint_step"] == 0


def test_build_job_health_payload_exposes_dashboard_fields() -> None:
    class Args:
        model_name = "/models/qwen"
        benchmark_file = "train.txt"
        online_eval_benchmark_file = "eval.txt"
        training_mode = "lora"
        grpo_steps = 24

    payload = build_job_health_payload(
        args=Args(),
        output_dir=Path("outputs/run"),
        world_size=8,
        status="running",
        started_at=0.0,
        records=[{"step": 3, "timestamp_utc": "2026-06-03T00:00:00Z"}],
        latest_checkpoint={"step": 2, "checkpoint_dir": "outputs/run/checkpoints/step-00002"},
    )

    assert payload["environment"] == "ASI1"
    assert payload["huanxin_task_status"] == "running"
    assert payload["world_size"] == 8
    assert payload["recorded_steps"] == 1
    assert payload["last_record_step"] == 3
    assert payload["latest_checkpoint_step"] == 2
    assert payload["pid_alive"] is True


def test_build_live_status_payload_flags_regressions_and_train_eval_gap() -> None:
    checkpoint_state = WallClockCheckpointState(
        interval_seconds=3600, last_saved_at=10.0, saved_count=1
    )
    records = [
        {
            "step": 1,
            "mean_reward": 1.0,
            "pass_rate": 1.0,
            "termination_counts": {"final_answer": 1},
        },
        {
            "step": 2,
            "mean_reward": 0.95,
            "pass_rate": 1.0,
            "termination_counts": {"final_answer": 1},
        },
        {"step": 3, "mean_reward": 0.2, "pass_rate": 0.0, "termination_counts": {"turn_budget": 1}},
        {"step": 4, "mean_reward": 0.1, "pass_rate": 0.0, "termination_counts": {"turn_budget": 1}},
    ]
    payload = build_live_status_payload(
        records=records,
        planned_steps=64,
        checkpoint_state=checkpoint_state,
        latest_checkpoint={"step": 4, "checkpoint_dir": "/tmp/ckpt"},
        latest_online_eval={"step": 4, "pass_rate": 0.0},
        world_size=4,
        status="running",
        started_at=0.0,
        recent_window=2,
        min_read_before_write_rate=0.5,
        min_tests_before_final_rate=0.4,
        max_no_tool_rate=0.2,
    )

    alert_kinds = {str(item.get("kind")) for item in payload["alerts"]}
    assert "pass_rate_drop" in alert_kinds
    assert "reward_drop" in alert_kinds

    payload_with_gap = build_live_status_payload(
        records=records[:2],
        planned_steps=64,
        checkpoint_state=checkpoint_state,
        latest_checkpoint={"step": 2, "checkpoint_dir": "/tmp/ckpt"},
        latest_online_eval={"step": 2, "pass_rate": 0.5},
        world_size=4,
        status="running",
        started_at=0.0,
        recent_window=2,
        min_read_before_write_rate=0.5,
        min_tests_before_final_rate=0.4,
        max_no_tool_rate=0.2,
    )
    gap_alert_kinds = {str(item.get("kind")) for item in payload_with_gap["alerts"]}
    assert "train_eval_gap" in gap_alert_kinds


def test_build_live_status_payload_flags_trajectory_health_alerts() -> None:
    checkpoint_state = WallClockCheckpointState(
        interval_seconds=3600, last_saved_at=10.0, saved_count=1
    )
    records = [
        {
            "step": 1,
            "mean_reward": 0.6,
            "pass_rate": 0.5,
            "read_before_write_rate": 0.2,
            "tests_before_final_rate": 0.1,
            "no_tool_call_rate": 0.4,
            "think_call_rate": 1.0,
            "termination_counts": {"final_answer": 1},
        },
        {
            "step": 2,
            "mean_reward": 0.55,
            "pass_rate": 0.5,
            "read_before_write_rate": 0.25,
            "tests_before_final_rate": 0.15,
            "no_tool_call_rate": 0.35,
            "think_call_rate": 0.5,
            "termination_counts": {"final_answer": 1},
        },
    ]
    payload = build_live_status_payload(
        records=records,
        planned_steps=64,
        checkpoint_state=checkpoint_state,
        latest_checkpoint={"step": 2, "checkpoint_dir": "/tmp/ckpt"},
        latest_online_eval={"step": 2, "pass_rate": 0.5},
        world_size=4,
        status="running",
        started_at=0.0,
        recent_window=2,
        min_read_before_write_rate=0.5,
        min_tests_before_final_rate=0.4,
        max_no_tool_rate=0.2,
    )

    alert_kinds = {str(item.get("kind")) for item in payload["alerts"]}
    assert "trajectory_read_before_write_drop" in alert_kinds
    assert "trajectory_tests_before_final_drop" in alert_kinds
    assert "trajectory_no_tool_rate_high" in alert_kinds


def test_emit_training_log_event_is_machine_readable_json(capsys) -> None:
    event = emit_training_log_event("training_step_summary", {"step": 3, "mean_reward": 0.5})
    captured = capsys.readouterr().out.strip()
    payload = json.loads(captured)

    assert payload["stage"] == "training_step_summary"
    assert payload["step"] == 3
    assert payload["mean_reward"] == 0.5
    assert payload["timestamp_utc"]
    assert event == payload


def test_build_step_log_event_payload_contains_training_debug_contract() -> None:
    checkpoint_state = WallClockCheckpointState(
        interval_seconds=3600, last_saved_at=10.0, every_steps=4
    )

    class Adaptive:
        def to_dict(self):
            return {"base_temp": 0.8, "consecutive_low_signal_skips": 1}

    record = {
        "step": 2,
        "task": "quantum_gate_token_canonicalizer",
        "domain": "quantum",
        "training_mode": "lora",
        "mean_reward": 0.42,
        "reward_std": 0.1,
        "reward_signal_std": 0.12,
        "pass_rate": 0.5,
        "syntax_rate": 1.0,
        "interface_rate": 0.75,
        "verifier_rate": 0.5,
        "advantage_scale": 0.12,
        "curriculum_prob": 0.2,
        "task_ema_reward": 0.3,
        "task_seen": 2,
        "mean_turns": 5,
        "mean_test_runs": 1,
        "termination_counts": {"final_answer": 4},
        "trajectory_tool_counts": {"read_file": 4, "write_file": 4, "run_tests": 2},
        "read_before_write_rate": 1.0,
        "tests_before_final_rate": 0.5,
        "no_tool_call_rate": 0.0,
        "think_call_rate": 0.25,
    }
    payload = build_step_log_event_payload(
        record=record,
        task={
            "task_id": "quantum_gate_token_canonicalizer",
            "meta": {
                "id": "quantum_gate_token_canonicalizer",
                "domain": "quantum",
                "category": "repair",
                "candidate_file": "candidate.py",
            },
        },
        task_weight=1.5,
        weight_sum=6.0,
        group_size=8,
        world_size=8,
        rank=0,
        effective_temperature=0.8,
        adaptive_temp=Adaptive(),
        evaluations=[
            {"total_reward": 1.0, "pass_reward": 1.0, "syntax_reward": 1.0, "details": []},
            {
                "total_reward": 0.0,
                "pass_reward": 0.0,
                "syntax_reward": 1.0,
                "details": ["AssertionError: miss"],
            },
        ],
        trajectory_summaries=[{"tool_counts": {"read_file": 1}, "turn_count": 2}],
        checkpoint_state=checkpoint_state,
        latest_checkpoint={"step": 1, "checkpoint_dir": "/tmp/ckpt"},
        latest_online_eval={"step": 1, "pass_rate": 0.25, "sample_failures": ["x" * 400]},
    )

    assert payload["task"]["domain"] == "quantum"
    assert payload["curriculum"]["selection_probability"] == 0.2
    assert payload["sampling"]["group_size"] == 8
    assert payload["reward"]["components"]["mean_total_reward"] == 0.5
    assert payload["reward"]["components"]["failure_categories"] == {"assertion_failure": 1}
    assert payload["trajectory_health"]["tool_counts"]["write_file"] == 4
    assert payload["checkpoint"]["interval_seconds"] == 3600
    assert payload["checkpoint"]["latest_step"] == 1
    assert "truncated" in payload["online_eval_latest"]["sample_failures"][0]


def test_run_started_log_event_payload_contains_analysis_contract() -> None:
    class Args:
        model_name = "/models/qwen"
        training_mode = "lora"
        adapter_init = None
        resume_from = None
        device = "npu:0"
        tasks_dir = "evals/tasks"
        benchmark_file = "train.txt"
        online_eval_benchmark_file = "eval.txt"
        online_eval_every_steps = 8
        online_eval_max_tasks = 4
        group_size = 8
        grpo_steps = 200000
        lr = 5e-6
        kl_coeff = 0.05
        temperature = 0.8
        max_new_tokens = 4096
        max_seq_length = 32768
        max_turns = 32
        max_test_runs = 2
        checkpoint_interval_seconds = 3600
        checkpoint_every_steps = 0
        reward_pass_weight = 0.6
        reward_syntax_weight = 0.1
        reward_interface_weight = 0.15
        reward_verifier_weight = 0.15
        reward_brevity_weight = 0.0
        reward_import_hygiene_weight = 0.05
        trajectory_write_bonus = 0.04
        trajectory_final_bonus = 0.02
        trajectory_timeout_penalty = 0.02
        trajectory_prewrite_test_penalty = 0.02
        trajectory_repeated_read_penalty = 0.01
        curriculum_ema_decay = 0.9
        curriculum_min_weight = 0.05
        curriculum_uncertainty_bonus = 0.35
        quantum_priority = 1.5
        trajectory_health_min_read_before_write_rate = 0.5
        trajectory_health_min_tests_before_final_rate = 0.4
        trajectory_health_max_no_tool_rate = 0.2
        lora_rank = 64
        lora_alpha = 128
        target_modules = ["q_proj"]
        target_module_regex = None

    payload = build_run_started_log_event_payload(
        args=Args(),
        output_dir=Path("outputs/run"),
        requested_task_ids={"a", "b"},
        online_eval_task_ids={"q"},
        allowed_domains={"quantum"},
        rank=0,
        local_rank=0,
        world_size=8,
        research_methods=[],
        resume_step=0,
    )

    assert payload["model_name"] == "/models/qwen"
    assert payload["requested_task_count"] == 2
    assert payload["online_eval_requested_task_count"] == 1
    assert payload["world_size"] == 8
    assert payload["checkpoint_interval_seconds"] == 3600
    assert payload["reward_weights"]["pass"] == 0.6
    assert payload["trajectory_health_thresholds"]["max_no_tool_call_rate"] == 0.2
    assert "training_step_summary" in payload["log_contract"]["stdout_json_stages"]
    assert "run_manifest.json" in payload["log_contract"]["artifact_files"]
    assert "job_health.json" in payload["log_contract"]["artifact_files"]
    assert "grpo_step_metrics.jsonl" in payload["log_contract"]["artifact_files"]


def test_task_inventory_log_event_payload_summarizes_domains_and_categories() -> None:
    payload = build_task_inventory_log_event_payload(
        tasks=[
            {"task_id": "q1", "meta": {"domain": "quantum", "category": "repair"}},
            {"task_id": "s1", "meta": {"domain": "software", "category": "agentic"}},
            {"task_id": "q2", "meta": {"domain": "quantum", "category": "repair"}},
        ],
        benchmark_file="train.txt",
        online_eval_benchmark_file="eval.txt",
        allowed_domains={"quantum", "software"},
        research_methods=[],
        args=type(
            "Args",
            (),
            {
                "online_eval_every_steps": 8,
                "group_size": 8,
                "grpo_steps": 200000,
                "checkpoint_interval_seconds": 3600,
                "checkpoint_every_steps": 0,
            },
        )(),
    )

    assert payload["task_count"] == 3
    assert payload["domain_counts"] == {"quantum": 2, "software": 1}
    assert payload["category_counts"] == {"agentic": 1, "repair": 2}
    assert payload["sample_task_ids"] == ["q1", "s1", "q2"]
    assert payload["checkpoint_interval_seconds"] == 3600


def test_agentic_training_benchmark_exists() -> None:
    assert BENCHMARK_PATH.exists(), f"Missing {BENCHMARK_PATH}"


def test_agentic_training_benchmark_tasks_exist_on_disk() -> None:
    task_ids = set()
    for task_json in ROOT.glob("evals/tasks/*/*/task.json"):
        meta = json.loads(task_json.read_text(encoding="utf-8"))
        task_ids.add(meta.get("id", task_json.parent.name))
    benchmark_ids = set(_load_ids(BENCHMARK_PATH))
    missing = benchmark_ids - task_ids
    assert not missing, f"Tasks missing from agentic training benchmark: {sorted(missing)}"


def test_agentic_training_benchmark_quantum_slice_stays_disjoint_from_holdout() -> None:
    benchmark_ids = {
        task_id for task_id in _load_ids(BENCHMARK_PATH) if task_id.startswith("quantum_")
    }
    holdout_ids = set(_load_ids(HOLDOUT_PATH))
    overlap = benchmark_ids & holdout_ids
    assert not overlap, f"Agentic training quantum slice overlaps strict holdout: {sorted(overlap)}"


def test_agentic_grpo_trainer_has_gradient_checkpointing_memory_switch() -> None:
    source = (ROOT / "training" / "agentic_grpo_trainer.py").read_text(encoding="utf-8")

    assert "--gradient-checkpointing" in source
    assert "--checkpoint-every-steps" in source
    assert "--train-layernorm" in source
    assert "--min-trainable-parameters" in source
    assert "enable_layernorm_training" in source
    assert "enforce_min_trainable_parameters" in source
    assert "trainable_parameter_floor" in source
    assert "gradient_checkpointing_enable" in source
    assert "enable_input_require_grads" in source
    assert "model.config.use_cache = False" in source
    assert '"stage": "gradient_checkpointing_enabled"' in source


def test_agentic_grpo_trainer_has_native_training_mode_for_dependency_light_smoke() -> None:
    source = (ROOT / "training" / "agentic_grpo_trainer.py").read_text(encoding="utf-8")

    assert "--training-mode" in source
    assert "native_training_mode_enabled" in source
    assert "trainable_state.pt" in source
    assert 'args.training_mode == "lora"' in source


def test_agentic_grpo_trainer_loads_qwen_from_local_files_only() -> None:
    source = (ROOT / "training" / "agentic_grpo_trainer.py").read_text(encoding="utf-8")

    assert "local_files_only=True" in source


def test_run_online_eval_reports_domain_metrics(monkeypatch) -> None:
    class Args:
        online_eval_benchmark_file = "evals/benchmarks/mixed_holdout.txt"
        online_eval_max_tasks = 3
        max_turns = 1
        max_new_tokens = 8
        max_seq_length = 128
        online_eval_temperature = 0.2
        max_test_runs = 1

    class Trajectory:
        final_candidate = "pass"
        terminated = "final_answer"
        test_runs = 1

    tasks = [
        {
            "task_id": "q1",
            "tests_py": "tests.py",
            "meta": {"domain": "quantum", "candidate_file": "candidate.py"},
        },
        {
            "task_id": "q2",
            "tests_py": "tests.py",
            "meta": {"domain": "quantum", "candidate_file": "candidate.py"},
        },
        {
            "task_id": "s1",
            "tests_py": "tests.py",
            "meta": {"domain": "software", "candidate_file": "candidate.py"},
        },
    ]

    def fake_rollout(*args, **kwargs):
        return Trajectory()

    def fake_eval(candidate, test_harness, task, args, research_methods=None):
        passed = task["task_id"] != "q2"
        return {
            "passed": passed,
            "total_reward": 1.0 if passed else 0.0,
            "pass_reward": 1.0 if passed else 0.0,
            "syntax_reward": 1.0,
            "interface_reward": 1.0,
            "verifier_reward": 1.0 if passed else 0.0,
            "details": [] if passed else ["AssertionError: quantum miss"],
        }

    monkeypatch.setattr(
        "training.agentic_grpo_trainer.build_agentic_prompt",
        lambda task, research_methods=None: "prompt",
    )
    monkeypatch.setattr("training.agentic_grpo_trainer.load_test_harness", lambda path: object())
    monkeypatch.setattr("training.agentic_grpo_trainer.rollout_trajectory", fake_rollout)
    monkeypatch.setattr("training.agentic_grpo_trainer.evaluate_candidate", fake_eval)
    monkeypatch.setattr(
        "training.agentic_grpo_trainer.summarize_trajectory_behavior",
        lambda trajectory: {
            "tool_counts": {"final_answer": 1},
            "turn_count": 1,
            "tests_before_final": True,
        },
    )

    payload = run_online_eval(
        model=object(),
        tokenizer=object(),
        eval_tasks=tasks,
        device="cpu",
        args=Args(),
        research_methods=[],
        step=7,
    )

    assert payload["pass_rate"] == 2 / 3
    assert payload["quantum_pass_rate"] == 0.5
    assert payload["quantum_task_count"] == 2
    assert payload["software_pass_rate"] == 1.0
    assert payload["software_task_count"] == 1
    assert payload["domain_metrics"]["quantum"]["mean_total_reward"] == 0.5
