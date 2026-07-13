from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "huanxin_download_and_start_distillation.sh"


def test_huanxin_distillation_bootstrap_dry_run_uses_all_requested_npus() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run", "--nproc-per-node", "8"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={**os.environ, "ASCEND_RT_VISIBLE_DEVICES": ""},
    )

    assert result.returncode == 0, result.stderr
    assert "remote_root=/vllm-workspace/quantum-gpt" in result.stdout
    assert "qwen36-35b-a3b-distill-uniform-lora-asi2-allnpu" in result.stdout
    assert "nproc_per_node=8" in result.stdout
    assert "num_epochs=3" in result.stdout
    assert "max_trainable_parameters=1000000000" in result.stdout
    assert "min_trainable_parameters=200000000" in result.stdout
    assert "ascend_rt_visible_devices=0\\,1\\,2\\,3\\,4\\,5\\,6\\,7" in result.stdout
    assert "rclone copy" in result.stdout
    assert "torchrun --nproc_per_node=8" in result.stdout
    assert "--num-epochs 3" in result.stdout
    assert "--model-name /root/work/filestorage/Qwen3.6-35B-A3B" in result.stdout
    assert "Qwen3.6-27B" not in result.stdout
    assert "--lora-rank 64" in result.stdout
    assert "--lora-alpha 128" in result.stdout
    assert (
        "--target-modules q_proj k_proj v_proj o_proj gate_proj up_proj down_proj" in result.stdout
    )
    assert "training/qwen_sft_peft.py" in result.stdout
    assert "--train-on-completions-only" in result.stdout
    assert "--gradient-checkpointing" in result.stdout
    assert "--train-layernorm" in result.stdout
    assert "--max-trainable-parameters 1000000000" in result.stdout
    assert "--min-trainable-parameters 200000000" in result.stdout
    assert "--load-in-8bit" not in result.stdout
