from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "submit_asi1_isq_sft_task.sh"


def launch_spec(env: dict[str, str] | None = None) -> dict:
    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run", "__launch-spec"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={**os.environ, **(env or {})},
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_asi1_isq_sft_defaults_to_non_w8a8_and_strict_preflight() -> None:
    spec = launch_spec()
    remote_command = spec["remote_command"]

    assert "/root/work/filestorage/Qwen3.6-35B-A3B" in remote_command
    assert "Qwen3.6-35B-A3B-W8A8" not in remote_command
    assert "qwen36-35b-w8a8" not in remote_command
    assert "preflight_qwen36_ascend_hf_training.py" in remote_command
    assert "--allow-known-blocked" not in remote_command
    assert "ALLOW_KNOWN_QWEN36_W8A8_ASCEND_HF_BLOCKER" not in remote_command
    assert "--lora-rank 64" in remote_command
    assert "--lora-alpha 128" in remote_command
    assert (
        "--target-modules q_proj k_proj v_proj o_proj gate_proj up_proj down_proj" in remote_command
    )
    assert "--train-layernorm" in remote_command
    assert "--min-trainable-parameters 200000000" in remote_command
    assert "--max-trainable-parameters 1000000000" in remote_command
    assert "data/generated/isq_train_cot_finetune_split_80_20/train_chatml.jsonl" in remote_command
    assert "data/generated/isq_train_cot_finetune_split_80_20/test_chatml.jsonl" in remote_command


def test_asi1_isq_sft_w8a8_override_still_renders_blocking_preflight() -> None:
    spec = launch_spec({"ASI1_ISQ_SFT_MODEL_NAME": "/root/work/filestorage/Qwen3.6-35B-A3B-W8A8"})
    remote_command = spec["remote_command"]

    assert "/root/work/filestorage/Qwen3.6-35B-A3B-W8A8" in remote_command
    assert "preflight_qwen36_ascend_hf_training.py" in remote_command
    assert "--allow-known-blocked" not in remote_command
    assert "ALLOW_KNOWN_QWEN36_W8A8_ASCEND_HF_BLOCKER" not in remote_command
