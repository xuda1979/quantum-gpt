from __future__ import annotations

from scripts import render_asi1_grpo_huanxin_bootstrap_command as renderer


def test_render_bootstrap_command_targets_35b_8npu_hourly_checkpoints() -> None:
    args = renderer.parse_args([])
    command = renderer.render_command(args)

    assert "HUANXIN_GRPO_MODEL_NAME=/root/work/filestorage/Qwen3.6-35B-A3B" in command
    assert "HUANXIN_GRPO_VISIBLE_DEVICES=0,1,2,3,4,5,6,7" in command
    assert "HUANXIN_GRPO_NPROC_PER_NODE=8" in command
    assert "HUANXIN_GRPO_CHECKPOINT_INTERVAL_SECONDS=3600" in command
    assert "HUANXIN_GRPO_LORA_RANK=64" in command
    assert "HUANXIN_GRPO_LORA_ALPHA=128" in command
    assert "HUANXIN_GRPO_MIN_TRAINABLE_PARAMETERS=200000000" in command
    assert "HUANXIN_GRPO_MAX_TRAINABLE_PARAMETERS=1000000000" in command
    assert (
        "HUANXIN_GRPO_TARGET_MODULES='q_proj k_proj v_proj o_proj gate_proj up_proj down_proj'"
        in command
    )
    assert "bash scripts/huanxin_pull_and_start_asi1_grpo.sh" in command
    assert "secret_access_key =" not in command
