from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import scripts.render_agentic_training_dashboard as dashboard

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "render_agentic_training_dashboard.py"
SERVE_SCRIPT = ROOT / "scripts" / "serve_agentic_training_dashboard.py"

EXPECTED_OBSERVABILITY_SECTIONS = {
    "infrastructure": ["基础设施", "任务心跳新鲜", "指标年龄"],
    "evals": ["评测", "评测通过率", "已经记录在线评测"],
    "artifacts": ["工件", "工件完整性", "已抓取文件", "指标指纹"],
    "safety": ["安全", "不安全工具", "没有不安全工具事件"],
    "alerts": ["告警", "实时告警", "NPU 内存"],
    "structured_logs": ["结构化日志事件", "训练步摘要", "检查点已保存"],
}


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def build_run(run_dir: Path) -> None:
    metrics = [
        {
            "step": 1,
            "timestamp_utc": "2026-05-26T00:00:00+00:00",
            "task": "docstring_contract",
            "domain": "software",
            "mean_reward": 0.04,
            "reward_signal_std": 0.0,
            "pass_rate": 0.0,
            "skipped": True,
            "reason": "low_reward_signal",
            "termination_counts": {"context_overflow": 2},
            "trajectory_tool_counts": {"read_file": 2},
        },
        {
            "step": 2,
            "timestamp_utc": "2026-05-26T00:01:00+00:00",
            "task": "patch_contract",
            "domain": "software",
            "mean_reward": 0.31,
            "reward_signal_std": 0.08,
            "pass_rate": 0.5,
            "loss": 0.2,
            "kl_coeff": 0.03,
            "termination_counts": {"final_answer": 2},
            "trajectory_tool_counts": {"read_file": 2, "write_file": 1, "final_answer": 1},
        },
    ]
    write_jsonl(run_dir / "grpo_step_metrics.jsonl", metrics)
    latest_checkpoint = {
        "timestamp_utc": "2026-05-26T00:01:30+00:00",
        "step": 2,
        "checkpoint_dir": str(run_dir / "checkpoints" / "step-00002"),
        "saved_count": 1,
        "checkpoint_interval_seconds": 600,
        "latest_record": metrics[-1],
    }
    write_json(run_dir / "latest_checkpoint.json", latest_checkpoint)
    write_jsonl(run_dir / "checkpoint_history.jsonl", [latest_checkpoint])
    write_json(
        run_dir / "live_status.json",
        {
            "status": "running",
            "planned_steps": 4,
            "summary": {"recorded_steps": 2, "updated_steps": 1, "skipped_steps": 1},
            "recent": {"mean_reward": 0.175, "mean_pass_rate": 0.25, "mean_loss": 0.2},
            "last_record": metrics[-1],
            "alerts": [],
            "latest_checkpoint": latest_checkpoint,
            "online_eval_latest": {
                "step": 2,
                "task_count": 2,
                "pass_rate": 0.5,
                "mean_total_reward": 0.7,
                "termination_counts": {"final_answer": 2},
                "failure_categories": {"assertion_failure": 1},
            },
        },
    )


def build_observability_run(run_dir: Path) -> None:
    metrics = [
        {
            "step": 1,
            "timestamp_utc": "2026-05-26T00:00:00+00:00",
            "task": "agentic_patch_smoke",
            "domain": "software",
            "mean_reward": 0.2,
            "reward_signal_std": 0.05,
            "pass_rate": 0.25,
            "loss": 0.4,
            "termination_counts": {"final_answer": 1},
            "trajectory_tool_counts": {"read_file": 2, "write_file": 1, "final_answer": 1},
        },
        {
            "step": 2,
            "timestamp_utc": "2026-05-26T00:01:00+00:00",
            "task": "agentic_patch_smoke",
            "domain": "software",
            "mean_reward": 0.55,
            "reward_signal_std": 0.12,
            "pass_rate": 0.5,
            "loss": 0.25,
            "kl_coeff": 0.02,
            "termination_counts": {"final_answer": 2},
            "trajectory_tool_counts": {
                "read_file": 2,
                "write_file": 2,
                "run_tests": 1,
                "final_answer": 1,
            },
        },
    ]
    online_eval_latest = {
        "timestamp_utc": "2026-05-26T00:01:05+00:00",
        "step": 2,
        "benchmark_file": "evals/benchmarks/agentic_software_engineering_holdout_v1.txt",
        "task_count": 4,
        "pass_rate": 0.5,
        "quantum_pass_rate": 0.25,
        "quantum_task_count": 2,
        "software_pass_rate": 0.75,
        "software_task_count": 2,
        "domain_metrics": {
            "quantum": {"task_count": 2, "pass_rate": 0.25, "mean_total_reward": 0.35},
            "software": {"task_count": 2, "pass_rate": 0.75, "mean_total_reward": 0.81},
        },
        "mean_total_reward": 0.58,
        "termination_counts": {"final_answer": 4},
        "failure_categories": {"assertion_failure": 1, "timeout": 1},
        "sample_failures": ["AssertionError: expected patched config"],
    }
    latest_checkpoint = {
        "timestamp_utc": "2026-05-26T00:01:10+00:00",
        "step": 2,
        "checkpoint_dir": str(run_dir / "checkpoints" / "step-00002"),
        "saved_count": 1,
        "checkpoint_interval_seconds": 600,
        "latest_record": metrics[-1],
    }
    write_jsonl(run_dir / "grpo_step_metrics.jsonl", metrics)
    write_jsonl(run_dir / "online_eval_history.jsonl", [online_eval_latest])
    write_json(run_dir / "online_eval_latest.json", online_eval_latest)
    write_json(run_dir / "latest_checkpoint.json", latest_checkpoint)
    write_jsonl(run_dir / "checkpoint_history.jsonl", [latest_checkpoint])
    write_json(
        run_dir / "run_config.json",
        {
            "model_name": "models/Qwen3.6-27B",
            "benchmark_file": "evals/benchmarks/agentic_coding_trajectory_training_v1.txt",
            "online_eval_benchmark_file": "evals/benchmarks/agentic_software_engineering_holdout_v1.txt",
            "grpo_steps": 8,
        },
    )
    write_json(
        run_dir / "asi1_fetch_manifest.json",
        {
            "schema_version": 1,
            "env": "ASI1",
            "remote_dir": "/workspace/quantum-gpt/outputs/observability-run",
            "log_path": "/tmp/observability-run.log",
            "files": {
                "live_status.json": {"fetched": True, "bytes": 128},
                "训练步指标": {"fetched": True, "bytes": 256},
                "train_log_tail.txt": {"fetched": True, "bytes": 72},
            },
        },
    )
    (run_dir / "train_log_tail.txt").write_text(
        "\n".join(
            [
                "[agentic-grpo] step=2 reward=0.55 pass_rate=0.50",
                "__ASI1_INLINE_RL_BOOT__ Python 3.11.13",
                "__ASI1_INLINE_RL_START__ rank=0 device=npu:0 world_size=4",
                "__ASI1_INLINE_RL_DONE__ rank=0",
                json.dumps(
                    {
                        "stage": "训练步摘要",
                        "timestamp_utc": "2026-05-26T00:01:00+00:00",
                        "step": 2,
                        "reward": {"mean_reward": 0.55, "pass_rate": 0.5},
                        "loss": 0.25,
                        "task": {"task_id": "agentic_patch_smoke", "domain": "software"},
                    }
                ),
                json.dumps(
                    {
                        "stage": "checkpoint_saved",
                        "timestamp_utc": "2026-05-26T00:01:10+00:00",
                        "step": 2,
                        "checkpoint_dir": str(run_dir / "checkpoints" / "step-00002"),
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    write_json(
        run_dir / "live_status.json",
        {
            "status": "running",
            "planned_steps": 8,
            "world_size": 4,
            "summary": {"recorded_steps": 2, "updated_steps": 2, "skipped_steps": 0},
            "recent": {"mean_reward": 0.375, "mean_pass_rate": 0.375, "mean_loss": 0.325},
            "last_record": metrics[-1],
            "alerts": [
                {
                    "kind": "gpu_memory",
                    "severity": "warning",
                    "message": "NPU 内存余量低于金丝雀门槛",
                }
            ],
            "job_health": {"last_metric_age_sec": 45.0, "worker_count": 4},
            "safety": {"unsafe_tool_events": 1, "sandbox_escape_attempts": 0},
            "latest_checkpoint": latest_checkpoint,
            "online_eval_latest": online_eval_latest,
        },
    )


def build_huanxin_status(path: Path) -> None:
    write_json(
        path,
        {
            "schema_version": 1,
            "generated_at_utc": "2026-05-26T00:02:00+00:00",
            "manual_mode": {"manual_mode": False, "automation_enabled": True},
            "environments": [
                {
                    "env_name": "ASI1",
                    "summary": "safari_keepalive_and_browser_daemon_healthy",
                    "train_dev_url": "https://example.invalid/train-dev/environment?name=ASI1",
                    "browser_daemon_operational": True,
                    "browser_daemon_state": "healthy",
                    "startup_state": "ready",
                    "auth_state": "已认证",
                    "current_url": "https://example.invalid/train-dev/environment?name=ASI1",
                    "shell_endpoint_failure": False,
                    "command_channel_recent_success": True,
                    "command_channel_transport": "独立通道",
                    "command_channel_age_seconds": 10.0,
                    "keepalive_operational": True,
                    "keepalive_loaded": True,
                    "job_count": 3,
                    "recent_job_ids": ["job-a", "job-b", "job-c"],
                    "latest_job": {"job_id": "job-c"},
                }
            ],
        },
    )


def build_domain_expert_manifest(data_dir: Path) -> None:
    manifest_path = data_dir / "generated" / "qwen36-domain-expert-mix" / "manifest.json"
    write_json(
        manifest_path,
        {
            "manifest_version": "curriculum-mix-v1",
            "domain_expert_contract": {
                "contract_version": "domain-expert-curriculum-v1",
                "purpose": "Specialize toward quantum coding while preserving software replay.",
                "reference_notes": [
                    "PDF reference: domain expert SFT should keep replay coverage."
                ],
                "requirements": {
                    "train_domain_min": {"quantum": 500, "software": 100},
                    "eval_domain_min": {"quantum": 50},
                    "require_task_disjoint": True,
                },
                "checks": {
                    "train_domain_min_quantum": True,
                    "train_domain_min_software": True,
                    "task_id_disjoint": True,
                },
                "details": {
                    "train_domain_counts": {"quantum": 1024, "software": 256},
                    "eval_domain_counts": {"quantum": 128, "software": 64},
                    "task_id_overlap": [],
                },
                "ok": True,
            },
        },
    )


def build_asi1_failed_status_run(run_dir: Path) -> None:
    task_id = "dt-asi1failed0001"
    task_name = "asi1-grpo-status-test"
    write_json(
        run_dir / "live_status.json",
        {
            "status": "failed",
            "planned_steps": 1,
            "summary": {"recorded_steps": 0, "updated_steps": 0, "skipped_steps": 0},
            "recent": {"recorded_steps": 0, "updated_steps": 0, "mean_reward": None},
            "last_record": None,
            "online_eval_latest": None,
            "alerts": [
                {
                    "kind": "asi1_task_failed_before_metrics",
                    "severity": "error",
                    "message": "ASI1 task failed before metrics.",
                    "task_id": task_id,
                }
            ],
        },
    )
    write_json(
        run_dir / "failure_report.json",
        {
            "status": "failed",
            "summary": "ASI1 task failed before GRPO metrics were emitted.",
            "failure_stage": "训练脚本启动前",
            "startup_diagnosis": "Huanxin emitted the platform sshd startup warning before user-code markers.",
            "huanxin_status": 6,
            "huanxin_use_time": "00:00:11",
            "task_id": task_id,
            "task_name": task_name,
        },
    )
    write_json(
        run_dir / "job_health.json",
        {
            "environment": "ASI1",
            "huanxin_task_id": task_id,
            "huanxin_task_name": task_name,
            "huanxin_task_status": "failed",
            "huanxin_task_status_code": 6,
            "huanxin_use_time": "00:00:11",
            "last_metric_age_sec": None,
            "remote_path": "outputs/asi1-failed-status-run",
        },
    )
    write_json(
        run_dir / "run_config.json",
        {
            "environment": "ASI1",
            "grpo_steps": 1,
            "huanxin_task_id": task_id,
            "huanxin_task_name": task_name,
            "model_name": "/root/work/filestorage/Qwen3.6-27B",
        },
    )


def build_asi1_live_metric_run(run_dir: Path) -> None:
    task_id = "dt-asi1live0001"
    task_name = "asi1-grpo-live-status-test"
    write_jsonl(
        run_dir / "grpo_step_metrics.jsonl",
        [
            {
                "step": 1,
                "timestamp_utc": "2026-05-29T00:00:00+00:00",
                "task": "agentic_patch_smoke",
                "domain": "software",
                "mean_reward": 0.42,
                "reward_signal_std": 0.11,
                "pass_rate": 0.5,
                "loss": 0.3,
                "kl_coeff": 0.02,
                "termination_counts": {"final_answer": 1},
                "trajectory_tool_counts": {"read_file": 1, "write_file": 1, "run_tests": 1},
            },
            {
                "step": 2,
                "timestamp_utc": "2026-05-29T00:01:00+00:00",
                "task": "agentic_patch_smoke",
                "domain": "software",
                "mean_reward": 0.5,
                "reward_signal_std": 0.13,
                "pass_rate": 0.75,
                "loss": 0.2,
                "kl_coeff": 0.03,
                "termination_counts": {"final_answer": 1},
                "trajectory_tool_counts": {"read_file": 1, "write_file": 1, "run_tests": 1},
            },
        ],
    )
    write_json(
        run_dir / "live_status.json",
        {
            "status": "running",
            "planned_steps": 4,
            "summary": {"recorded_steps": 1, "updated_steps": 1, "skipped_steps": 0},
            "recent": {"recorded_steps": 1, "updated_steps": 1, "mean_reward": 0.42},
            "last_record": {
                "step": 1,
                "mean_reward": 0.42,
                "reward_signal_std": 0.11,
                "pass_rate": 0.5,
                "loss": 0.3,
                "kl_coeff": 0.02,
            },
            "online_eval_latest": None,
            "alerts": [],
        },
    )
    write_json(
        run_dir / "job_health.json",
        {
            "environment": "ASI1",
            "huanxin_task_id": task_id,
            "huanxin_task_name": task_name,
            "huanxin_task_status": "running",
            "huanxin_task_status_code": 3,
            "last_metric_age_sec": 30,
            "remote_path": "outputs/asi1-live-metric-run",
        },
    )
    write_jsonl(
        run_dir / "online_eval_history.jsonl",
        [
            {
                "step": 1,
                "task_count": 4,
                "pass_rate": 0.25,
                "quantum_pass_rate": 0.5,
                "quantum_task_count": 2,
                "software_pass_rate": 0.0,
                "software_task_count": 2,
                "mean_total_reward": 0.33,
            },
            {
                "step": 2,
                "task_count": 4,
                "pass_rate": 0.5,
                "domain_metrics": {
                    "quantum": {"task_count": 2, "pass_rate": 1.0, "mean_total_reward": 0.82},
                    "software": {"task_count": 2, "pass_rate": 0.0, "mean_total_reward": 0.28},
                },
                "mean_total_reward": 0.62,
            },
        ],
    )


def build_tiny_asi1_metrics_smoke_run(run_dir: Path) -> None:
    write_jsonl(
        run_dir / "grpo_step_metrics.jsonl",
        [
            {
                "step": 1,
                "mean_reward": 0.18,
                "reward_signal_std": 0.03,
                "pass_rate": 0.25,
                "termination_counts": {"final_answer": 1},
                "trajectory_tool_counts": {"final_answer": 1},
            }
        ],
    )
    write_jsonl(
        run_dir / "online_eval_history.jsonl",
        [
            {
                "step": 1,
                "task_count": 2,
                "pass_rate": 0.5,
                "quantum_pass_rate": 0.5,
                "mean_total_reward": 0.41,
            }
        ],
    )
    write_json(run_dir / "live_status.json", {"status": "training", "planned_steps": 2})
    write_json(
        run_dir / "run_config.json",
        {
            "environment": "ASI1",
            "model_name": "models/Qwen3.6-27B",
            "grpo_steps": 2,
        },
    )


def build_asi1_live_status_only_eval_and_checkpoint_run(run_dir: Path) -> None:
    write_jsonl(
        run_dir / "grpo_step_metrics.jsonl",
        [
            {
                "step": 64,
                "mean_reward": 1.0,
                "reward_signal_std": None,
                "pass_rate": 1.0,
                "loss": None,
                "kl_coeff": 0.02,
                "skipped": False,
                "termination_counts": {"final_answer": 3},
                "trajectory_tool_counts": {
                    "read_file": 6,
                    "write_file": 189,
                    "run_tests": 3,
                    "final_answer": 3,
                },
            }
        ],
    )
    write_json(
        run_dir / "live_status.json",
        {
            "status": "completed",
            "planned_steps": 64,
            "summary": {
                "planned_steps": 64,
                "recorded_steps": 1,
                "updated_steps": 1,
                "skipped_steps": 0,
            },
            "recent": {
                "mean_reward": 1.0,
                "mean_pass_rate": 1.0,
                "recorded_steps": 1,
                "updated_steps": 1,
            },
            "last_record": {
                "step": 64,
                "mean_reward": 1.0,
                "pass_rate": 1.0,
                "kl_coeff": 0.02,
                "trajectory_tool_counts": {"write_file": 189, "final_answer": 3},
            },
            "job_health": {
                "environment": "ASI1",
                "huanxin_task_id": "dt-liveonly0001",
                "huanxin_task_name": "asi1-rl-liveonly",
                "huanxin_task_status": "ended",
                "huanxin_task_status_code": 0,
                "huanxin_use_time": "00:00:18",
                "last_metric_age_sec": None,
            },
            "latest_checkpoint": {
                "checkpoint_dir": "/tmp/qg-asi1-inline-rl-liveonly",
                "saved_count": 1,
                "step": 64,
            },
            "online_eval_latest": {
                "step": 64,
                "task_count": 3,
                "pass_rate": 1.0,
                "mean_total_reward": 1.0,
                "domain_metrics": {
                    "agentic": {"task_count": 1, "pass_rate": 1.0},
                    "quantum": {"task_count": 1, "pass_rate": 1.0},
                    "software": {"task_count": 1, "pass_rate": 1.0},
                },
                "model_load": {
                    "attempted": True,
                    "ok": True,
                    "mode": "config",
                    "model_class": "qwen3_5",
                    "architectures": ["Qwen3_5ForConditionalGeneration"],
                },
            },
        },
    )


def build_live_status_only_grpo_evidence_run(run_dir: Path) -> None:
    write_json(
        run_dir / "live_status.json",
        {
            "status": "running",
            "planned_steps": 16,
            "summary": {"recorded_steps": 1, "updated_steps": 1, "skipped_steps": 0},
            "last_record": {
                "step": 8,
                "mean_reward": 0.72,
                "reward_signal_std": 0.09,
                "pass_rate": 0.75,
                "loss": 0.18,
                "kl_coeff": 0.04,
                "termination_counts": {"final_answer": 2},
                "trajectory_tool_counts": {
                    "read_file": 4,
                    "write_file": 2,
                    "run_tests": 2,
                    "final_answer": 2,
                },
            },
            "latest_checkpoint": {
                "step": 8,
                "checkpoint_dir": "/tmp/qg-live-status-only/checkpoint-8",
                "saved_count": 2,
                "checkpoint_interval_seconds": 300,
            },
            "online_eval_latest": {
                "step": 8,
                "task_count": 4,
                "pass_rate": 0.5,
                "domain_metrics": {
                    "quantum": {"task_count": 2, "pass_rate": 0.5, "mean_total_reward": 0.6},
                    "software": {"task_count": 2, "pass_rate": 0.5, "mean_total_reward": 0.55},
                    "agentic": {"task_count": 1, "pass_rate": 1.0, "mean_total_reward": 0.9},
                },
                "mean_total_reward": 0.58,
                "rank_markers": {"started_count": 8, "completed_count": 8, "world_size": 8},
            },
            "job_health": {
                "environment": "ASI1",
                "huanxin_task_id": "dt-live-evidence",
                "huanxin_task_name": "q36-live-evidence",
                "huanxin_task_status": "running",
                "huanxin_task_status_code": 3,
                "huanxin_use_time": "00:12:34",
                "remote_root": "/workspace/quantum-gpt",
                "remote_path": "/tmp/qg-live-status-only",
            },
        },
    )
    write_json(
        run_dir / "run_manifest.json",
        {
            "environment": "ASI1",
            "model_name": "/root/work/filestorage/Qwen3.6-27B",
            "grpo_steps": 16,
            "benchmark_file": "evals/benchmarks/agentic_coding_trajectory_training_v5_quantum.txt",
            "online_eval_benchmark_file": "evals/benchmarks/quantum_generalization_holdout_v2_hard.txt",
            "remote_root": "/workspace/quantum-gpt",
            "remote_output_dir": "/tmp/qg-live-status-only",
        },
    )
    write_json(
        run_dir / "asi1_fetch_manifest.json",
        {
            "env": "ASI1",
            "remote_dir": "/workspace/quantum-gpt//tmp/qg-live-status-only",
            "files": {
                "live_status.json": {"fetched": True, "bytes": 1024},
                "train_log_tail.txt": {"fetched": True, "bytes": 2048},
            },
        },
    )
    (run_dir / "train_log_tail.txt").write_text(
        "\n".join(
            [
                "__ASI1_INLINE_RL_BOOT__ Python 3.11.13",
                "__ASI1_INLINE_RL_START__ rank=0 device=npu:0 world_size=8",
                "__ASI1_INLINE_RL_DONE__ rank=0",
                "训练日志只在测试里保留标记，不渲染原始命令。",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    write_json(
        run_dir / "run_config.json",
        {
            "environment": "ASI1",
            "model_name": "/root/work/filestorage/Qwen3.6-27B",
            "grpo_steps": 64,
            "benchmark_file": "inline_quantum_software_agentic_rl",
            "online_eval_benchmark_file": "inline_quantum_software_agentic_eval",
        },
    )


def build_asi1_queued_status_only_run(run_dir: Path) -> None:
    task_id = "dt-asi1queued0001"
    task_name = "q36-27b-qgrpo-queued-status"
    write_json(
        run_dir / "live_status.json",
        {
            "status": "queued",
            "planned_steps": 300,
            "summary": {"recorded_steps": 0, "updated_steps": 0, "skipped_steps": 0},
            "recent": {"recorded_steps": 0, "updated_steps": 0},
            "last_record": None,
            "online_eval_latest": None,
            "latest_checkpoint": {
                "checkpoint_interval_seconds": 180,
                "saved_count": 0,
            },
            "job_health": {
                "environment": "ASI1",
                "huanxin_task_id": task_id,
                "huanxin_task_name": task_name,
                "huanxin_task_status": "queued",
                "huanxin_task_status_code": 2,
                "huanxin_use_time": "00:00:00",
                "remote_path": "outputs/q36-27b-qgrpo-queued-status",
            },
        },
    )
    write_json(
        run_dir / "run_config.json",
        {
            "environment": "ASI1",
            "model_name": "/root/work/filestorage/Qwen3.6-27B",
            "grpo_steps": 300,
            "benchmark_file": "evals/benchmarks/agentic_coding_trajectory_training_v5_quantum.txt",
            "online_eval_benchmark_file": "evals/benchmarks/agentic_software_engineering_holdout_v1.txt",
        },
    )


def build_blocked_noisy_placeholder_run(run_dir: Path) -> None:
    write_json(
        run_dir / "live_status.json",
        {
            "status": "failed",
            "planned_steps": 8,
            "summary": {"recorded_steps": 0, "updated_steps": 0, "skipped_steps": 0},
            "recent": {"mean_reward": None, "mean_pass_rate": None},
            "last_record": None,
            "online_eval_latest": None,
            "alerts": [
                {
                    "kind": "pre_python_task_failure",
                    "severity": "error",
                    "message": "N/A",
                }
            ],
            "job_health": {
                "environment": "ASI1",
                "huanxin_task_id": "dt-blocked0001",
                "huanxin_task_name": "q36-blocked-noisy",
                "huanxin_task_status": "failed",
                "huanxin_task_status_code": 6,
                "last_metric_age_sec": None,
                "last_log_age_sec": None,
                "npu_visible": None,
            },
        },
    )
    write_json(
        run_dir / "failure_report.json",
        {
            "status": "failed",
            "summary": "N/A",
            "exact_blocker": "训练 Pod 启动后没有写出 GRPO 指标；最新日志显示入口脚本在加载模型前退出。",
            "failure_stage": "pre_python_task_startup",
            "startup_diagnosis": "None",
            "task_id": "dt-blocked0001",
            "task_name": "q36-blocked-noisy",
        },
    )
    write_json(
        run_dir / "asi1_fetch_manifest.json",
        {
            "env": "ASI1",
            "remote_dir": None,
            "files": {
                "live_status.json": {"fetched": True, "bytes": 128},
            },
        },
    )


def build_structured_log_only_run(run_dir: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    step_event = {
        "stage": "训练步摘要",
        "timestamp_utc": "2026-06-01T09:00:00+00:00",
        "step": 7,
        "rank": 0,
        "world_size": 8,
        "training_mode": "lora",
        "skipped": False,
        "loss": 0.17,
        "task": {
            "task_id": "quantum_phase_estimation_repair",
            "name": "quantum_phase_estimation_repair",
            "domain": "quantum",
            "category": "algorithm",
            "candidate_file": "candidate.py",
        },
        "curriculum": {
            "selection_probability": 0.25,
            "task_ema_reward": 0.48,
            "task_seen": 3,
        },
        "sampling": {"group_size": 4, "temperature": 0.7},
        "reward": {
            "mean_reward": 0.63,
            "reward_std": 0.13,
            "reward_signal_std": 0.11,
            "pass_rate": 0.75,
            "syntax_rate": 1.0,
            "interface_rate": 1.0,
            "verifier_rate": 0.75,
            "advantage_scale": 0.9,
            "components": {"mean_pass_reward": 0.75, "mean_verifier_reward": 0.75},
        },
        "trajectory_health": {
            "mean_turns": 3.5,
            "mean_test_runs": 1.0,
            "termination_counts": {"final_answer": 3, "turn_budget": 1},
            "tool_counts": {"read_file": 4, "write_file": 3, "run_tests": 3, "final_answer": 3},
            "read_before_write_rate": 1.0,
            "tests_before_final_rate": 0.75,
            "no_tool_call_rate": 0.0,
            "think_call_rate": 0.25,
        },
        "checkpoint": {
            "interval_seconds": 180,
            "every_steps": 7,
            "saved_count": 0,
            "last_saved_step": 0,
        },
    }
    checkpoint_event = {
        "stage": "checkpoint_saved",
        "timestamp_utc": "2026-06-01T09:00:10+00:00",
        "step": 7,
        "checkpoint_dir": "/remote/outputs/structured-log-only/checkpoints/step-00007",
        "adapter_dir": "/remote/outputs/structured-log-only/checkpoints/step-00007/adapter",
        "runtime_state_path": "/remote/outputs/structured-log-only/checkpoints/step-00007/runtime_state.pt",
        "saved_count": 1,
        "checkpoint_interval_seconds": 180,
        "checkpoint_every_steps": 7,
    }
    eval_event = {
        "stage": "online_eval_complete",
        "timestamp_utc": "2026-06-01T09:00:20+00:00",
        "step": 7,
        "task_count": 4,
        "pass_rate": 0.5,
        "quantum_pass_rate": 0.5,
        "software_pass_rate": 0.5,
        "mean_total_reward": 0.58,
        "domain_metrics": {
            "quantum": {"task_count": 2, "pass_rate": 0.5, "mean_total_reward": 0.6},
            "software": {"task_count": 2, "pass_rate": 0.5, "mean_total_reward": 0.56},
        },
        "termination_counts": {"final_answer": 4},
        "failure_categories": {"assertion_failure": 2},
        "sample_failures": ["AssertionError: phase estimate drifted"],
    }
    completed_event = {
        "stage": "训练完成",
        "timestamp_utc": "2026-06-01T09:01:00+00:00",
        "adapter_dir": "/remote/outputs/structured-log-only/final_adapter",
        "output_dir": "/remote/outputs/structured-log-only",
        "planned_steps": 7,
        "recorded_steps": 1,
        "updated_steps": 1,
        "wallclock_checkpoints_saved": 1,
        "latest_checkpoint_step": 7,
        "latest_online_eval_step": 7,
    }
    (run_dir / "train_log_tail.txt").write_text(
        "\n".join(
            [
                "[agentic-grpo] remote stdout replay",
                json.dumps(step_event),
                json.dumps(checkpoint_event),
                json.dumps(eval_event),
                json.dumps(completed_event),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    write_json(
        run_dir / "run_config.json",
        {
            "environment": "ASI1",
            "model_name": "models/Qwen3.6-27B",
            "grpo_steps": 7,
            "benchmark_file": "evals/benchmarks/agentic_coding_trajectory_training_v5_quantum.txt",
            "online_eval_benchmark_file": "evals/benchmarks/agentic_software_engineering_holdout_v1.txt",
        },
    )


def test_huanxin_tab_distinguishes_daemon_endpoint_from_command_channel() -> None:
    html_text = dashboard.render_huanxin_environment_card(
        {
            "env_name": "ASI1",
            "summary": "command_channel_connected_daemon_shell_endpoint_failed",
            "auth_state": "已认证",
            "browser_daemon_operational": False,
            "keepalive_operational": False,
            "shell_endpoint_failure": True,
            "command_channel_recent_success": True,
            "command_channel_transport": "独立通道",
            "command_channel_age_seconds": 7.0,
        }
    )

    assert "终端入口" in html_text
    assert "降级" in html_text
    assert "命令通道" in html_text
    assert "独立通道" in html_text


def test_dashboard_chinese_helpers_preserve_zero_values() -> None:
    html_text = dashboard.compact_dict_items(
        {
            "task_status": "completed",
            "fetched_files": 0,
            "rank_started": 0,
            "rank_completed": 1,
        },
        ["task_status", "fetched_files", "rank_started", "rank_completed"],
    )

    assert "<strong>任务状态</strong>：已完成" in html_text
    assert "<strong>已抓取文件数</strong>：0" in html_text
    assert "<strong>已启动 rank 数</strong>：0" in html_text
    assert "<strong>已完成 rank 数</strong>：1" in html_text


def test_dashboard_reconstructs_run_from_structured_training_log_only(tmp_path: Path) -> None:
    run_dir = tmp_path / "outputs" / "structured-log-only"
    build_structured_log_only_run(run_dir)
    output = tmp_path / "dashboard.html"
    registry_output = tmp_path / "registry.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--outputs-dir",
            str(tmp_path / "outputs"),
            "--output",
            str(output),
            "--registry-output",
            str(registry_output),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    html_text = output.read_text(encoding="utf-8")
    assert "structured-log-only" in html_text
    assert "量子评测</span><strong>50.0%" in html_text
    assert "检查点进度</span><strong>7/7" in html_text
    assert "训练完成" in html_text

    registry = json.loads(registry_output.read_text(encoding="utf-8"))
    run = registry["runs"][0]
    assert run["recorded_steps"] == 1
    assert run["updated_steps"] == 1
    assert run["last_record"]["source"] == "structured_training_log"
    assert run["last_record"]["mean_reward"] == 0.63
    assert run["tool_counts"]["write_file"] == 3
    assert run["terminations"]["final_answer"] == 3
    assert run["eval_history_summary"]["records"] == 1
    assert run["eval_history_summary"]["latest"]["source"] == "structured_training_log"
    assert run["eval_history_summary"]["latest"]["domain_metrics"]["quantum"]["pass_rate"] == 0.5
    assert run["checkpoint_summary"]["checkpoint_step"] == 7
    assert run["checkpoint_summary"]["checkpoint_progress_text"] == "7/7"
    assert run["train_log_summary"]["stage_counts"]["训练完成"] == 1
    assert run["train_log_summary"]["latest_training_completed"]["latest_checkpoint_step"] == 7
    assert run["artifact_status"]["metrics"] is True
    assert run["artifact_status"]["online_eval_history"] is True
    assert run["artifact_status"]["structured_training_log"] is True


def build_legacy_run(run_dir: Path) -> None:
    write_json(
        run_dir / "metrics.json",
        {
            "model_name": "models/Qwen2.5-1.5B-Instruct",
            "device": "cpu",
            "world_size": 1,
            "train_examples": 160,
            "eval_examples": 32,
            "max_steps": 5,
            "final_eval": {"loss": 0.8788, "perplexity": 2.4079},
            "metrics": [
                {"step": 1, "epoch": 1, "train_loss": 0.78, "lr": 0.00018},
                {
                    "step": 2,
                    "epoch": 1,
                    "train_loss": 0.66,
                    "lr": 0.0,
                    "eval_loss": 0.8788,
                    "eval_perplexity": 2.4079,
                },
            ],
        },
    )


def assert_observability_section_is_represented(html_text: str, section: str) -> None:
    needles = EXPECTED_OBSERVABILITY_SECTIONS[section]
    assert any(
        needle in html_text for needle in needles
    ), f"missing {section} dashboard cues: {needles}"


def test_dashboard_renders_training_signals(tmp_path: Path) -> None:
    run_dir = tmp_path / "outputs" / "run-001"
    build_run(run_dir)
    output = tmp_path / "dashboard.html"
    registry_output = tmp_path / "registry.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--outputs-dir",
            str(tmp_path / "outputs"),
            "--output",
            str(output),
            "--registry-output",
            str(registry_output),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["runs"] == ["run-001"]

    html_text = output.read_text(encoding="utf-8")
    assert "智能体训练状态" in html_text
    assert "run-001" in html_text
    assert "怎么看" in html_text
    assert "总览" in html_text
    assert "训练" in html_text
    assert "门槛" in html_text
    assert "曲线" in html_text
    assert "来源" in html_text
    assert "诊断" in html_text
    assert "奖励波动" in html_text
    assert "评测通过率" in html_text
    assert "检查点进度" in html_text
    assert "检查点与评测状态" in html_text
    assert "焕新运行证据" in html_text
    assert "KL 系数" in html_text
    assert "2/4" in html_text
    assert "运行编号" in html_text
    assert "优先级门槛" in html_text
    assert "下一步" in html_text
    assert "失败类型" in html_text
    assert "P0 保护" in html_text
    assert "奖励和通过率应该一起改善" in html_text
    assert "P0" in html_text
    assert "上下文溢出" in html_text
    assert "完成回答" in html_text

    registry = json.loads(registry_output.read_text(encoding="utf-8"))
    assert registry["runs"][0]["name"] == "run-001"
    assert registry["runs"][0]["updated_steps"] == 1
    assert registry["runs"][0]["lineage"]["metrics_sha256"]
    assert registry["runs"][0]["practices"]["P0"]["passed"] is False
    assert registry["runs"][0]["practices"]["P1"]["passed"] is True
    gate_names = {gate["name"] for gate in registry["runs"][0]["gates"]}
    assert "optimizer_updated" in gate_names
    assert "no_context_overflow" in gate_names
    assert any(gate["priority"] == "P0" for gate in registry["runs"][0]["gates"])


def test_dashboard_fixture_covers_observability_tab_needs(tmp_path: Path) -> None:
    run_dir = tmp_path / "outputs" / "observability-run"
    build_observability_run(run_dir)
    output = tmp_path / "dashboard.html"
    registry_output = tmp_path / "registry.json"
    huanxin_status = tmp_path / "huanxin_environment_status.json"
    build_huanxin_status(huanxin_status)
    build_domain_expert_manifest(tmp_path / "data")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--outputs-dir",
            str(tmp_path / "outputs"),
            "--output",
            str(output),
            "--registry-output",
            str(registry_output),
            "--huanxin-status",
            str(huanxin_status),
            "--data-dir",
            str(tmp_path / "data"),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    html_text = output.read_text(encoding="utf-8")
    for section in EXPECTED_OBSERVABILITY_SECTIONS:
        assert_observability_section_is_represented(html_text, section)
    assert "用指纹、模型名和配置" in html_text
    assert "今日结论" in html_text
    assert "训练是否在进行" in html_text
    assert "是否有检查点" in html_text
    assert "量子评测是否变好" in html_text
    assert "当前最大阻塞" in html_text
    assert "下一步动作" in html_text
    assert "本页展示底层计数" in html_text
    assert "evals/benchmarks/agentic_software_engineering_holdout_v1.txt" in html_text
    assert "焕新" in html_text
    assert "焕新环境" in html_text
    assert "研发系统" in html_text
    assert "领域专家课程" in html_text
    assert "qwen36-domain-expert-mix" in html_text
    assert "日志来源" in html_text
    assert "远程工件契约" in html_text
    assert "训练步指标" in html_text
    assert "智能体轨迹" in html_text
    assert "工件抓取摘要" in html_text
    assert "训练日志摘要" in html_text
    assert "结构化日志事件" in html_text
    assert "训练步摘要" in html_text
    assert "最新训练奖励" in html_text
    assert "检查点进度" in html_text
    assert "2/8" in html_text
    assert "ASI1" in html_text
    assert "已认证" in html_text

    registry = json.loads(registry_output.read_text(encoding="utf-8"))
    run = registry["runs"][0]
    gate_names = {gate["name"] for gate in run["gates"]}
    assert {
        "job_heartbeat_fresh",
        "no_unsafe_tool_events",
        "no_live_alerts",
        "online_eval_recorded",
    } <= gate_names
    assert run["failure_signals"]["alert_gpu_memory"] == 1
    assert (
        run["lineage"]["online_eval_benchmark_file"]
        == "evals/benchmarks/agentic_software_engineering_holdout_v1.txt"
    )
    assert run["practices"]["P0"]["passed"] is False
    assert run["practices"]["P1"]["passed"] is False
    assert registry["huanxin_environment_status"]["environments"][0]["env_name"] == "ASI1"
    assert registry["research_system_status"]["outputs"]["run_count"] == 1
    contracts = registry["research_system_status"]["domain_expert_contracts"]
    assert contracts[0]["正常"] is True
    assert contracts[0]["checks"]["train_domain_min_quantum"] is True
    assert registry["source_contract"]["huanxin_environment_status_present"] is True
    assert registry["decision_summary"]["active_runs"] == 1
    assert registry["decision_summary"]["checkpoint_run"] == "observability-run"
    assert registry["decision_summary"]["eval_run"] == "observability-run"
    assert "metrics" in registry["source_contract"]["present_counts"]
    assert run["fetch_manifest"]["env"] == "ASI1"
    assert "step=2 reward=0.55" in run["train_log_tail"]
    assert run["train_log_summary"]["stage_counts"]["训练步摘要"] == 1
    assert run["artifact_status"]["structured_training_log"] is True


def test_dashboard_surfaces_asi1_failed_status_artifacts(tmp_path: Path) -> None:
    run_dir = tmp_path / "outputs" / "asi1-failed-status-run"
    build_asi1_failed_status_run(run_dir)
    output = tmp_path / "dashboard.html"
    registry_output = tmp_path / "registry.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--outputs-dir",
            str(tmp_path / "outputs"),
            "--output",
            str(output),
            "--registry-output",
            str(registry_output),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    html_text = output.read_text(encoding="utf-8")
    assert "ASI1 任务 asi1-grpo-status-test dt-asi1failed0001 在产生指标前失败" in html_text
    assert "训练脚本启动前" in html_text
    assert "焕新状态码=6" in html_text
    assert "焕新在用户训练代码标记出现前产生平台启动告警" in html_text

    registry = json.loads(registry_output.read_text(encoding="utf-8"))
    run = registry["runs"][0]
    assert run["status"] == "失败"
    assert run["status_text"].startswith(
        "ASI1 任务 asi1-grpo-status-test dt-asi1failed0001 在产生指标前失败"
    )
    assert "训练脚本启动前" in run["status_detail"]
    assert "焕新状态码=6" in run["status_detail"]


def test_dashboard_marks_metric_bearing_asi1_run_active(tmp_path: Path) -> None:
    run_dir = tmp_path / "outputs" / "asi1-live-metric-run"
    build_asi1_live_metric_run(run_dir)
    output = tmp_path / "dashboard.html"
    registry_output = tmp_path / "registry.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--outputs-dir",
            str(tmp_path / "outputs"),
            "--output",
            str(output),
            "--registry-output",
            str(registry_output),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    html_text = output.read_text(encoding="utf-8")
    assert (
        "ASI1 任务 asi1-grpo-live-status-test dt-asi1live0001 正在训练，GRPO 指标已实时产生"
        in html_text
    )
    assert "<span>训练中</span><strong>1</strong>" in html_text
    assert "量子评测曲线" in html_text
    assert 'aria-label="量子通过率 曲线"' in html_text
    assert 'aria-label="软件工程通过率 曲线"' in html_text
    assert 'aria-label="KL 系数 曲线"' in html_text
    assert "未记录奖励波动" not in html_text

    registry = json.loads(registry_output.read_text(encoding="utf-8"))
    run = registry["runs"][0]
    assert run["status"] == "active"
    assert run["recorded_steps"] == 1
    assert run["eval_history_summary"]["records"] == 2
    assert run["eval_history_summary"]["latest"]["domain_metrics"]["quantum"]["pass_rate"] == 1.0
    assert run["status_text"].endswith("正在训练，GRPO 指标已实时产生")


def test_dashboard_marks_tiny_asi1_metrics_smoke_training_active(tmp_path: Path) -> None:
    run_dir = tmp_path / "outputs" / "asi1-tiny-metrics-smoke"
    build_tiny_asi1_metrics_smoke_run(run_dir)
    output = tmp_path / "dashboard.html"
    registry_output = tmp_path / "registry.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--outputs-dir",
            str(tmp_path / "outputs"),
            "--output",
            str(output),
            "--registry-output",
            str(registry_output),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    html_text = output.read_text(encoding="utf-8")
    assert "<span>训练中</span><strong>1</strong>" in html_text
    assert "ASI1 正在训练，GRPO 指标已实时产生" in html_text
    assert "已捕获第一个数值：0.18；等待下一个点" in html_text
    assert "已捕获第一个数值：0.5；等待下一个点" in html_text
    assert "等待第一步 GRPO" not in html_text
    assert "等待留出评测" not in html_text

    registry = json.loads(registry_output.read_text(encoding="utf-8"))
    run = registry["runs"][0]
    assert run["status"] == "active"
    assert run["recorded_steps"] == 1
    assert run["updated_steps"] == 1
    assert run["eval_history_summary"]["records"] == 1
    assert run["eval_history_summary"]["latest"]["pass_rate"] == 0.5


def test_dashboard_uses_live_status_eval_and_checkpoint_when_history_files_absent(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "outputs" / "asi1-live-status-only"
    build_asi1_live_status_only_eval_and_checkpoint_run(run_dir)
    output = tmp_path / "dashboard.html"
    registry_output = tmp_path / "registry.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--outputs-dir",
            str(tmp_path / "outputs"),
            "--output",
            str(output),
            "--registry-output",
            str(registry_output),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    html_text = output.read_text(encoding="utf-8")
    assert "ASI1 任务 asi1-rl-liveonly dt-liveonly0001 状态为 已完成" in html_text
    assert "量子评测</span><strong>100.0%" in html_text
    assert "软件工程评测</span><strong>100.0%" in html_text
    assert "检查点进度</span><strong>64/64" in html_text
    assert "KL 系数</span><strong>0.0200" in html_text
    assert "指标新鲜度" in html_text
    assert "未记录奖励波动; 最新奖励=1.0000 通过率=100.0%" in html_text
    assert "等待量子评测" not in html_text
    assert "等待软件工程评测" not in html_text
    assert "等待检查点进度" not in html_text

    registry = json.loads(registry_output.read_text(encoding="utf-8"))
    run = registry["runs"][0]
    assert run["status"] == "completed"
    assert run["recorded_steps"] == 1
    assert run["updated_steps"] == 1
    assert run["eval_history_summary"]["records"] == 1
    assert run["eval_history_summary"]["latest"]["domain_metrics"]["quantum"]["pass_rate"] == 1.0
    assert run["checkpoint_summary"]["checkpoint_progress_text"] == "64/64"
    assert run["checkpoint_summary"]["checkpoint_saved_count"] == 1
    assert (
        next(gate for gate in run["gates"] if gate["name"] == "reward_signal_nonzero")["passed"]
        is True
    )
    assert (
        next(gate for gate in run["gates"] if gate["name"] == "job_heartbeat_fresh")["detail"]
        == "已捕获最终指标"
    )


def test_dashboard_surfaces_queued_huanxin_task_without_na_placeholders(tmp_path: Path) -> None:
    run_dir = tmp_path / "outputs" / "asi1-queued-status-only"
    build_asi1_queued_status_only_run(run_dir)
    output = tmp_path / "dashboard.html"
    registry_output = tmp_path / "registry.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--outputs-dir",
            str(tmp_path / "outputs"),
            "--output",
            str(output),
            "--registry-output",
            str(registry_output),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    html_text = output.read_text(encoding="utf-8")
    assert "ASI1 任务 q36-27b-qgrpo-queued-status dt-asi1queued0001 状态为 排队中" in html_text
    assert "正在等待 GRPO 或评测工件" in html_text
    assert "检查点间隔（秒）" in html_text
    assert "180" in html_text
    assert "等待第一步 GRPO" in html_text
    assert "等待留出评测" in html_text
    assert "N/A" not in html_text

    registry = json.loads(registry_output.read_text(encoding="utf-8"))
    run = registry["runs"][0]
    assert run["status"] == "queued"
    assert run["status_text"].endswith("正在等待 GRPO 或评测工件")
    assert run["job_health"]["huanxin_task_status"] == "queued"
    assert run["job_health"]["huanxin_task_status_code"] == 2
    assert run["checkpoint_summary"]["checkpoint_interval_seconds"] == 180
    assert run["checkpoint_summary"]["checkpoint_saved_count"] == 0
    assert run["eval_history_summary"]["records"] == 0


def test_default_dashboard_selection_keeps_grpo_evidence_after_many_status_only_runs(
    tmp_path: Path,
) -> None:
    outputs_dir = tmp_path / "outputs"
    for index in range(16):
        run_dir = outputs_dir / f"fresh-status-only-{index:02d}"
        build_asi1_queued_status_only_run(run_dir)
        (run_dir / "live_status.json").write_text(
            (run_dir / "live_status.json")
            .read_text(encoding="utf-8")
            .replace(
                "q36-27b-qgrpo-queued-status",
                f"q36-27b-qgrpo-queued-status-{index:02d}",
            ),
            encoding="utf-8",
        )
        for path in run_dir.iterdir():
            path.touch()
        run_dir.touch()

    evidence_run = outputs_dir / "older-grpo-evidence"
    build_asi1_live_status_only_eval_and_checkpoint_run(evidence_run)
    for path in evidence_run.iterdir():
        path.touch()
    evidence_run.touch()

    output = tmp_path / "dashboard.html"
    registry_output = tmp_path / "registry.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--outputs-dir",
            str(outputs_dir),
            "--output",
            str(output),
            "--registry-output",
            str(registry_output),
            "--limit",
            "12",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    html_text = output.read_text(encoding="utf-8")
    assert "older-grpo-evidence" in html_text
    assert "量子评测</span><strong>100.0%" in html_text
    assert "检查点进度</span><strong>64/64" in html_text
    assert "N/A" not in html_text

    registry = json.loads(registry_output.read_text(encoding="utf-8"))
    names = [run["name"] for run in registry["runs"]]
    assert "older-grpo-evidence" in names
    evidence_payload = next(run for run in registry["runs"] if run["name"] == "older-grpo-evidence")
    assert evidence_payload["recorded_steps"] == 1
    assert evidence_payload["eval_history_summary"]["records"] == 1
    assert evidence_payload["checkpoint_summary"]["checkpoint_progress_text"] == "64/64"


def test_dashboard_uses_live_status_for_grpo_checkpoint_eval_and_huanxin_evidence(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "outputs" / "live-status-only-grpo"
    build_live_status_only_grpo_evidence_run(run_dir)
    output = tmp_path / "dashboard.html"
    registry_output = tmp_path / "registry.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--outputs-dir",
            str(tmp_path / "outputs"),
            "--output",
            str(output),
            "--registry-output",
            str(registry_output),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    html_text = output.read_text(encoding="utf-8")
    assert "live-status-only-grpo" in html_text
    assert "平均奖励</span><strong>0.7200" in html_text
    assert "训练通过率</span><strong>75.0%" in html_text
    assert "KL 系数</span><strong>0.0400" in html_text
    assert "检查点进度</span><strong>8/16" in html_text
    assert "总评测通过率</span><strong>50.0%" in html_text
    assert "量子通过率</span><strong>50.0%" in html_text
    assert "智能体通过率</span><strong>100.0%" in html_text
    assert "智能体任务" in html_text
    assert "焕新运行证据" in html_text
    assert "q36-live-evidence" in html_text
    assert "dt-live-evidence" in html_text
    assert "world size" not in html_text.lower()
    assert "N/A" not in html_text
    assert "<pre" not in html_text
    assert "```" not in html_text

    registry = json.loads(registry_output.read_text(encoding="utf-8"))
    run = registry["runs"][0]
    assert run["recorded_steps"] == 1
    assert run["last_record"]["source"] == "live_status_last_record"
    assert run["checkpoint_summary"]["checkpoint_progress_text"] == "8/16"
    assert run["eval_history_summary"]["records"] == 1
    assert run["eval_history_summary"]["latest"]["domain_metrics"]["agentic"]["pass_rate"] == 1.0
    assert run["huanxin_evidence"]["environment"] == "ASI1"
    assert run["huanxin_evidence"]["task_id"] == "dt-live-evidence"
    assert run["huanxin_evidence"]["world_size"] == 8
    assert run["huanxin_evidence"]["launcher_markers"]["boot"] == 1


def test_dashboard_replaces_empty_placeholders_and_surfaces_exact_blocker(tmp_path: Path) -> None:
    run_dir = tmp_path / "outputs" / "blocked-noisy-placeholders"
    build_blocked_noisy_placeholder_run(run_dir)
    output = tmp_path / "dashboard.html"
    registry_output = tmp_path / "registry.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--outputs-dir",
            str(tmp_path / "outputs"),
            "--output",
            str(output),
            "--registry-output",
            str(registry_output),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    html_text = output.read_text(encoding="utf-8")
    assert "精确阻塞" in html_text
    assert "训练 Pod 启动后没有写出 GRPO 指标；最新日志显示入口脚本在加载模型前退出。" in html_text
    assert "暂无数据" in html_text
    assert "等待日志抓取" in html_text
    assert "等待第一步 GRPO" in html_text
    assert "等待留出评测" in html_text
    assert "N/A" not in html_text
    assert ">None<" not in html_text
    assert "&gt;None&lt;" not in html_text

    registry = json.loads(registry_output.read_text(encoding="utf-8"))
    run = registry["runs"][0]
    assert (
        run["failure_report"]["exact_blocker"]
        == "训练 Pod 启动后没有写出 GRPO 指标；最新日志显示入口脚本在加载模型前退出。"
    )


def test_dashboard_visible_content_is_chinese_and_not_raw_code(tmp_path: Path) -> None:
    run_dir = tmp_path / "outputs" / "observability-run"
    build_observability_run(run_dir)
    output = tmp_path / "dashboard.html"
    registry_output = tmp_path / "registry.json"
    huanxin_status = tmp_path / "huanxin_environment_status.json"
    build_huanxin_status(huanxin_status)

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--outputs-dir",
            str(tmp_path / "outputs"),
            "--output",
            str(output),
            "--registry-output",
            str(registry_output),
            "--huanxin-status",
            str(huanxin_status),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    html_text = output.read_text(encoding="utf-8")
    forbidden_visible_fragments = [
        "<pre",
        "Raw Data",
        "Auto-refreshes",
        "Mean Reward",
        "Train Pass",
        "Eval Pass",
        "Shell Endpoint",
        "Command Channel",
        "NPU memory",
        "N/A",
        "code=",
        "session_state=",
        "```",
    ]
    for fragment in forbidden_visible_fragments:
        assert fragment not in html_text
    assert "每 60 秒自动刷新" in html_text
    assert "诊断摘要" in html_text
    assert "NPU 内存余量低于金丝雀门槛" in html_text


def test_dashboard_handles_empty_outputs_dir(tmp_path: Path) -> None:
    output = tmp_path / "dashboard.html"
    registry_output = tmp_path / "registry.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--outputs-dir",
            str(tmp_path / "missing"),
            "--output",
            str(output),
            "--registry-output",
            str(registry_output),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    html_text = output.read_text(encoding="utf-8")
    assert "还没有训练运行" in html_text


def test_dashboard_compatibility_with_legacy_metrics_json(tmp_path: Path) -> None:
    run_dir = tmp_path / "outputs" / "legacy-run"
    build_legacy_run(run_dir)
    output = tmp_path / "dashboard.html"
    registry_output = tmp_path / "registry.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--outputs-dir",
            str(tmp_path / "outputs"),
            "--output",
            str(output),
            "--registry-output",
            str(registry_output),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    html_text = output.read_text(encoding="utf-8")
    assert "legacy-run" in html_text
    assert "优先级门槛" in html_text.lower()
    assert "总览" in html_text
    assert "诊断" in html_text
    assert "评测通过率" in html_text
    registry = json.loads(registry_output.read_text(encoding="utf-8"))
    assert registry["runs"][0]["name"] == "legacy-run"
    assert registry["runs"][0]["status"] == "completed"


def test_dashboard_server_serves_status_json(tmp_path: Path) -> None:
    run_dir = tmp_path / "outputs" / "run-001"
    build_run(run_dir)
    output = tmp_path / "dashboard.html"
    registry_output = tmp_path / "registry.json"
    huanxin_status = tmp_path / "huanxin_environment_status.json"
    build_huanxin_status(huanxin_status)
    port = 18881

    proc = subprocess.Popen(
        [
            sys.executable,
            str(SERVE_SCRIPT),
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--outputs-dir",
            str(tmp_path / "outputs"),
            "--output",
            str(output),
            "--registry-output",
            str(registry_output),
            "--huanxin-status",
            str(huanxin_status),
            "--poll-seconds",
            "1",
        ],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        url = f"http://127.0.0.1:{port}/status.json"
        for _ in range(30):
            try:
                with urllib.request.urlopen(url, timeout=1) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                break
            except Exception:
                time.sleep(0.2)
        else:
            raise AssertionError("dashboard server did not become ready")

        assert payload["ok"] is True
        assert payload["runs"][0]["name"] == "run-001"
        assert payload["runs"][0]["status_text"].endswith("正在训练，GRPO 指标已实时产生")
        assert payload["runs"][0]["eval_history_summary"]["latest"]["pass_rate"] == 0.5
        assert payload["runs"][0]["checkpoint_summary"]["checkpoint_progress_text"] == "2/4"
        assert payload["runs"][0]["job_health"] == {}
        assert payload["huanxin_environment_status"]["environments"][0]["env_name"] == "ASI1"
        assert payload["research_system_status"]["outputs"]["run_count"] == 1
        assert "source_contract" in payload
        assert payload["decision_summary"]["active_runs"] == 1
        assert output.exists()
        assert registry_output.exists()

        request = urllib.request.Request(f"http://127.0.0.1:{port}/", method="HEAD")
        with urllib.request.urlopen(request, timeout=1) as response:
            assert response.status == 200
            assert response.headers["Content-Type"].startswith("text/html")

        request = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(request, timeout=1) as response:
            assert response.status == 200
            assert response.headers["Content-Type"].startswith("application/json")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
