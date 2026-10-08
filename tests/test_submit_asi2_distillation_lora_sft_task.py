from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "submit_asi2_distillation_lora_sft_task.sh"


def _launch_spec(*args: str) -> dict:
    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run", "__launch-spec", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_asi2_distillation_lora_launch_spec_uses_compact_verified_sft_by_default() -> None:
    spec = _launch_spec()
    command = spec["execution_command"]
    remote_command = spec["remote_command"]
    remote_script_body = spec["remote_script_body"]

    assert spec["remote_root"] == "/vllm-workspace/quantum-gpt"
    assert (
        spec["output_dir"]
        == "outputs/qwen36-35b-a3b-distill-uniform-lora-asi2-allnpu-r64-broad-ln-l512-s40-100hq"
    )
    assert spec["nproc_per_node"] == "8"
    assert spec["num_epochs"] == "3"
    assert spec["train_layernorm"] is True
    assert spec["min_trainable_parameters"] == 200_000_000
    assert spec["max_trainable_parameters"] == 1_000_000_000
    assert (
        spec["uniform_lora_policy"]
        == "all matching transformer layers, shared rank, attention plus mlp projection targets"
    )
    assert spec["embed_patches"] is False
    assert spec["single_line_execution"] is True
    assert spec["remote_script_path"] is None
    assert spec["remote_b64_path"] is None
    assert len(command) > 200
    assert "\n" not in command
    assert "p.write_bytes(b.b64decode(" in command
    assert "/tmp/asi2_distill_lora_run_full.sh" in command
    assert "subprocess" in command
    assert remote_command == command

    assert "echo __ASI2_DISTILL_LORA_TASK_START__" in remote_script_body
    assert "NAS copy detected - syncing offline..." in remote_script_body
    assert "torchrun --nproc_per_node=8 training/qwen_sft_peft.py" in remote_script_body
    assert "--model-name /root/work/filestorage/Qwen3.6-35B-A3B" in remote_script_body
    assert "--max-steps 40" in remote_script_body
    assert "--num-epochs 3" in remote_script_body


def test_asi2_distillation_lora_launch_spec_can_embed_patches_when_requested() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run", "__launch-spec"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={**os.environ, "ASI2_DISTILL_EMBED_PATCHES": "1"},
    )
    assert result.returncode == 0, result.stderr
    spec = json.loads(result.stdout)
    command = spec["execution_command"]
    remote_script_body = spec["remote_script_body"]

    assert spec["embed_patches"] is False
    assert "echo __ASI2_DISTILL_LORA_TASK_START__" in remote_script_body
    assert "torchrun --nproc_per_node=8 training/qwen_sft_peft.py" in remote_script_body
    assert "/tmp/asi2_distill_lora_run_full.sh" in command


def test_asi2_distillation_lora_wrapper_defaults_to_dry_run_without_submit() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run", "--task-name", "asi2-dlora-test"],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )

    stdout = result.stdout.decode("utf-8", errors="replace")
    stderr = result.stderr.decode("utf-8", errors="replace")
    assert result.returncode == 0, stderr
    assert "--task-name asi2-dlora-test" in stdout
    assert "--accelerator-cards 8" in stdout
    assert "--cpu-cores 160" in stdout
    assert "--memory-gb 1920" in stdout
    assert "--submit" not in stdout


def test_asi2_distillation_lora_launch_spec_allows_nproc_override() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run", "__launch-spec"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={**os.environ, "ASI2_DISTILL_NPROC_PER_NODE": "4", "ASI2_DISTILL_NUM_EPOCHS": "2"},
    )
    assert result.returncode == 0, result.stderr
    spec = json.loads(result.stdout)
    assert spec["nproc_per_node"] == "4"
    assert spec["num_epochs"] == "2"
    assert "torchrun --nproc_per_node=4 training/qwen_sft_peft.py" in spec["remote_script_body"]
    assert "--num-epochs 2" in spec["remote_script_body"]
