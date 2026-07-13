from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "launch_qwen36_35b_a3b_agentic_grpo_asi1.sh"


def test_asi1_launcher_defaults_to_8_npus_and_checkpointing() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run", "--hours", "24"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={"HUANXIN_TRAINING_ENV": "ASI1"},
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    command = payload["remote_command"]

    assert "ASCEND_RT_VISIBLE_DEVICES=0,1,2,3,4,5,6,7" in command
    assert "torchrun --nproc_per_node=8" in command
    assert "__ASI1_GRPO_BEFORE_TORCHRUN__" in command
    assert "__ASI1_GRPO_AFTER_TORCHRUN__" in command
    assert "test -s " in command
    assert "/grpo_step_metrics.jsonl" in command
    assert "/final_adapter" in command
    assert "__ASI1_GRPO_METRICS_AND_ARTIFACTS_OK__" in command
    assert "--group-size 8" in command
    assert "--grpo-steps 64" in command
    assert "--max-new-tokens 2048" in command
    assert "--max-seq-length 16384" in command
    assert "--checkpoint-interval-seconds 3600" in command
    assert "--checkpoint-every-steps 0" in command
    assert (
        "--online-eval-benchmark-file evals/benchmarks/quantum_generalization_holdout_v2_hard.txt"
        in command
    )
    assert "--online-eval-every-steps 8" in command
    assert "--online-eval-max-tasks 4" in command


def test_asi1_launcher_passes_quantum_domain_filter() -> None:
    result = subprocess.run(
        [
            "bash",
            str(SCRIPT),
            "--dry-run",
            "--domain-filter",
            "quantum",
            "--benchmark-file",
            "evals/benchmarks/quantum_grpo_training_v5_failure_shape_disjoint.txt",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={"HUANXIN_TRAINING_ENV": "ASI1"},
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    command = payload["remote_command"]
    assert (
        "--benchmark-file evals/benchmarks/quantum_grpo_training_v5_failure_shape_disjoint.txt"
        in command
    )
    assert "--domain-filter quantum" in command


def test_asi1_launcher_allows_overridden_model() -> None:
    result = subprocess.run(
        [
            "bash",
            str(SCRIPT),
            "--dry-run",
            "--model-name",
            "/tmp/custom-model",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={"HUANXIN_TRAINING_ENV": "ASI1"},
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert "test -d /tmp/custom-model" in payload["remote_command"]
