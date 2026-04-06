from __future__ import annotations

from argparse import Namespace
import json
from pathlib import Path

import pytest

from training import grpo_trainer
from training.grpo_utils import append_grpo_metric, append_grpo_metric_jsonl


def test_append_grpo_metric_persists_skipped_step_reason() -> None:
    metrics: list[dict[str, object]] = []

    record = append_grpo_metric(
        metrics,
        step=1,
        task="quantum_qaoa_maxcut",
        domain="quantum",
        mean_reward=0.054625,
        reward_std=0.01,
        reward_signal_std=0.01,
        curriculum_prob=0.25,
        task_ema_reward=0.054625,
        task_seen=1,
        skipped=True,
        reason="low_reward_signal",
    )

    assert metrics == [record]
    assert record["skipped"] is True
    assert record["reason"] == "low_reward_signal"
    assert record["domain"] == "quantum"
    assert "loss" not in record


def test_append_grpo_metric_persists_update_loss() -> None:
    metrics: list[dict[str, object]] = []

    record = append_grpo_metric(
        metrics,
        step=2,
        task="quantum_phase_estimation_circuit",
        domain="quantum",
        mean_reward=0.21,
        reward_std=0.11,
        reward_signal_std=0.12,
        curriculum_prob=0.4,
        task_ema_reward=0.21,
        task_seen=3,
        skipped=False,
        loss=0.037,
    )

    assert metrics == [record]
    assert "skipped" not in record
    assert record["loss"] == 0.037
    assert "reason" not in record


def test_append_grpo_metric_omits_skipped_key_for_update_rows() -> None:
    metrics: list[dict[str, object]] = []

    record = append_grpo_metric(
        metrics,
        step=3,
        task="quantum_phase_estimation_circuit",
        domain="quantum",
        mean_reward=0.31,
        reward_std=0.14,
        reward_signal_std=0.14,
        curriculum_prob=0.2,
        task_ema_reward=0.31,
        task_seen=2,
        skipped=False,
        loss=0.021,
    )

    assert metrics == [record]
    assert "skipped" not in record
    assert record["loss"] == 0.021
    assert "reason" not in record


def test_append_grpo_metric_jsonl_persists_multiple_records(tmp_path: Path) -> None:
    metrics_path = tmp_path / "grpo_step_metrics.jsonl"
    first = {
        "step": 1,
        "task": "quantum_qaoa_maxcut",
        "domain": "quantum",
        "skipped": True,
        "reason": "low_reward_signal",
    }
    second = {
        "step": 2,
        "task": "quantum_superdense_coding",
        "domain": "quantum",
        "loss": 0.0125,
    }

    append_grpo_metric_jsonl(metrics_path, first)
    append_grpo_metric_jsonl(metrics_path, second)

    rows = [
        json.loads(line)
        for line in metrics_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert rows == [first, second]


def test_main_removes_stale_grpo_metrics_before_early_abort(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    output_dir = tmp_path / "grpo-run"
    output_dir.mkdir(parents=True)
    stale_metrics = output_dir / "grpo_metrics.json"
    stale_metrics.write_text('{"stale": true}\n', encoding="utf-8")

    monkeypatch.setattr(
        grpo_trainer,
        "parse_args",
        lambda: Namespace(
            model_name="models/OmniCoder-9B",
            adapter_init=None,
            tasks_dir=str(tmp_path / "tasks"),
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
            reward_brevity_weight=0.0,
            brevity_target_lines=40,
        ),
    )
    monkeypatch.setattr(grpo_trainer, "load_research_methods", lambda _methods: [])
    monkeypatch.setattr(grpo_trainer, "discover_tasks", lambda *_args, **_kwargs: [])
    monkeypatch.delenv("RANK", raising=False)
    monkeypatch.delenv("LOCAL_RANK", raising=False)
    monkeypatch.delenv("WORLD_SIZE", raising=False)

    with pytest.raises(ValueError, match="No GRPO tasks matched the requested filters"):
        grpo_trainer.main()

    assert not stale_metrics.exists()


def test_main_removes_stale_run_config_before_early_abort(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    output_dir = tmp_path / "grpo-run"
    output_dir.mkdir(parents=True)
    stale_run_config = output_dir / "run_config.json"
    stale_run_config.write_text('{"stale": true}\n', encoding="utf-8")

    monkeypatch.setattr(
        grpo_trainer,
        "parse_args",
        lambda: Namespace(
            model_name="models/OmniCoder-9B",
            adapter_init=None,
            tasks_dir=str(tmp_path / "tasks"),
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
            reward_brevity_weight=0.0,
            brevity_target_lines=40,
        ),
    )
    monkeypatch.setattr(grpo_trainer, "load_research_methods", lambda _methods: [])
    monkeypatch.setattr(grpo_trainer, "discover_tasks", lambda *_args, **_kwargs: [])
    monkeypatch.delenv("RANK", raising=False)
    monkeypatch.delenv("LOCAL_RANK", raising=False)
    monkeypatch.delenv("WORLD_SIZE", raising=False)

    with pytest.raises(ValueError, match="No GRPO tasks matched the requested filters"):
        grpo_trainer.main()

    assert not stale_run_config.exists()
