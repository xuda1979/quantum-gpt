from __future__ import annotations

import json
import random
import subprocess
import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "validate_agentic_grpo_run_artifacts.py"


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def run_validator(output_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(output_dir)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def build_valid_run(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_dir = output_dir / "checkpoints" / "step-00008"
    adapter_dir = checkpoint_dir / "adapter"
    adapter_dir.mkdir(parents=True, exist_ok=True)

    runtime_state_path = checkpoint_dir / "runtime_state.pt"
    torch.save(
        {
            "step": 8,
            "optimizer_state": {"param_groups": []},
            "python_random_state": random.getstate(),
            "torch_rng_state": torch.random.get_rng_state(),
            "adaptive_temp_state": {"base_temp": 0.8, "current_temp": 0.8},
            "curriculum_state": {"quantum_demo": 0.5},
        },
        runtime_state_path,
    )

    checkpoint_state = {
        "timestamp_utc": "2026-05-14T00:00:00+00:00",
        "step": 8,
        "checkpoint_interval_seconds": 3600,
        "latest_record": {"step": 8, "mean_reward": 0.75},
        "adapter_dir": str(adapter_dir),
        "runtime_state_path": str(runtime_state_path),
    }
    write_json(checkpoint_dir / "checkpoint_state.json", checkpoint_state)

    latest_checkpoint = {
        "timestamp_utc": "2026-05-14T00:00:00+00:00",
        "step": 8,
        "checkpoint_dir": str(checkpoint_dir),
        "saved_count": 1,
        "checkpoint_interval_seconds": 3600,
        "latest_record": {"step": 8, "mean_reward": 0.75},
    }
    online_eval_latest = {
        "timestamp_utc": "2026-05-14T00:00:05+00:00",
        "step": 8,
        "benchmark_file": "evals/benchmarks/quantum_generalization_holdout_v1.txt",
        "task_count": 2,
        "pass_rate": 0.5,
        "mean_total_reward": 0.625,
        "mean_syntax_reward": 1.0,
        "mean_interface_reward": 0.5,
        "mean_verifier_reward": 0.25,
        "termination_counts": {"final_answer": 2},
        "failure_categories": {"assertion_failure": 1},
        "sample_failures": ["AssertionError: expected 4 got 3"],
        "tasks": [
            {
                "task_id": "quantum_demo_a",
                "domain": "quantum",
                "passed": True,
                "total_reward": 1.0,
                "pass_reward": 1.0,
                "syntax_reward": 1.0,
                "interface_reward": 1.0,
                "verifier_reward": 0.0,
                "termination": "final_answer",
                "test_runs": 1,
                "details": [],
            },
            {
                "task_id": "quantum_demo_b",
                "domain": "quantum",
                "passed": False,
                "total_reward": 0.25,
                "pass_reward": 0.0,
                "syntax_reward": 1.0,
                "interface_reward": 0.0,
                "verifier_reward": 0.5,
                "termination": "final_answer",
                "test_runs": 1,
                "details": ["AssertionError: expected 4 got 3"],
            },
        ],
    }
    live_status = {
        "timestamp_utc": "2026-05-14T00:00:06+00:00",
        "status": "running",
        "elapsed_seconds": 120.0,
        "planned_steps": 64,
        "world_size": 4,
        "summary": {
            "recorded_steps": 8,
            "updated_steps": 8,
            "skipped_steps": 0,
            "skip_reasons": {},
        },
        "recent": {
            "window": 8,
            "recorded_steps": 8,
            "updated_steps": 8,
            "mean_reward": 0.75,
            "mean_pass_rate": 0.5,
            "mean_loss": 0.2,
            "termination_counts": {"final_answer": 8},
        },
        "alerts": [],
        "last_record": {"step": 8, "mean_reward": 0.75},
        "latest_checkpoint": latest_checkpoint,
        "online_eval_latest": online_eval_latest,
        "wallclock_checkpoints_saved": 1,
    }

    write_json(output_dir / "latest_checkpoint.json", latest_checkpoint)
    write_jsonl(output_dir / "checkpoint_history.jsonl", [latest_checkpoint])
    write_json(output_dir / "online_eval_latest.json", online_eval_latest)
    write_jsonl(output_dir / "online_eval_history.jsonl", [online_eval_latest])
    write_json(output_dir / "live_status.json", live_status)


def test_validator_passes_for_consistent_run_artifacts(tmp_path: Path) -> None:
    output_dir = tmp_path / "outputs" / "run-001"
    build_valid_run(output_dir)

    result = run_validator(output_dir)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["checks"]["runtime_state_valid"] is True
    assert payload["checks"]["latest_checkpoint_matches_checkpoint_history"] is True
    assert payload["checks"]["online_eval_latest_matches_live_status"] is True


def test_validator_fails_when_runtime_state_is_missing(tmp_path: Path) -> None:
    output_dir = tmp_path / "outputs" / "run-001"
    build_valid_run(output_dir)
    (output_dir / "checkpoints" / "step-00008" / "runtime_state.pt").unlink()

    result = run_validator(output_dir)
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["checks"]["runtime_state_valid"] is False
    assert any("runtime_state.pt" in error for error in payload["errors"])


def test_validator_fails_when_online_eval_history_drifts_from_latest(tmp_path: Path) -> None:
    output_dir = tmp_path / "outputs" / "run-001"
    build_valid_run(output_dir)

    drifted_online_eval = {
        "timestamp_utc": "2026-05-14T00:00:05+00:00",
        "step": 7,
        "benchmark_file": "evals/benchmarks/quantum_generalization_holdout_v1.txt",
        "task_count": 2,
        "pass_rate": 0.0,
        "mean_total_reward": 0.25,
        "mean_syntax_reward": 0.5,
        "mean_interface_reward": 0.0,
        "mean_verifier_reward": 0.0,
        "termination_counts": {"turn_budget": 2},
        "failure_categories": {"assertion_failure": 2},
        "sample_failures": ["AssertionError: drifted"],
        "tasks": [
            {
                "task_id": "quantum_demo_a",
                "domain": "quantum",
                "passed": False,
                "total_reward": 0.25,
                "pass_reward": 0.0,
                "syntax_reward": 0.5,
                "interface_reward": 0.0,
                "verifier_reward": 0.0,
                "termination": "turn_budget",
                "test_runs": 1,
                "details": ["AssertionError: drifted"],
            },
            {
                "task_id": "quantum_demo_b",
                "domain": "quantum",
                "passed": False,
                "total_reward": 0.25,
                "pass_reward": 0.0,
                "syntax_reward": 0.5,
                "interface_reward": 0.0,
                "verifier_reward": 0.0,
                "termination": "turn_budget",
                "test_runs": 1,
                "details": ["AssertionError: drifted"],
            },
        ],
    }
    write_jsonl(output_dir / "online_eval_history.jsonl", [drifted_online_eval])

    result = run_validator(output_dir)
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["checks"]["online_eval_latest_matches_online_eval_history"] is False
    assert any("online_eval_history" in error for error in payload["errors"])
