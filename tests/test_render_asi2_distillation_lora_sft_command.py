from __future__ import annotations

import argparse

from scripts import render_asi2_distillation_lora_sft_command as renderer


def args(mode: str = "lora") -> argparse.Namespace:
    return argparse.Namespace(
        remote_root="/vllm-workspace/quantum-gpt",
        model_name="models/Qwen3.6-35B-A3B",
        split_dir="data/generated/split",
        output_dir="outputs/distill",
        mode=mode,
        device="npu",
        nproc_per_node=8,
        max_length=512,
        max_steps=40,
        num_epochs=3,
        per_device_batch_size=1,
        gradient_accumulation_steps=1,
        learning_rate="5e-5",
        eval_steps=10,
        log_steps=5,
        lora_rank=64,
        lora_alpha=128,
        lora_dropout="0.0",
        train_layernorm=True,
        max_trainable_parameters=1_000_000_000,
        min_trainable_parameters=200_000_000,
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        completion_only=True,
        gradient_checkpointing=True,
        output_json=None,
    )


def test_lora_command_uses_adapter_sft_without_8bit() -> None:
    payload = renderer.build_command(args("lora"))
    command = payload["command"]
    assert payload["uses_lora"] is True
    assert payload["uses_qlora"] is False
    assert payload["model_name"] == "models/Qwen3.6-35B-A3B"
    assert "Qwen3.6-27B" not in command
    assert "--max-length 512" in command
    assert "--num-epochs 3" in command
    assert "--lora-rank 64" in command
    assert "--lora-alpha 128" in command
    assert "--lora-dropout 0.0" in command
    assert "--target-modules q_proj k_proj v_proj o_proj gate_proj up_proj down_proj" in command
    assert "--train-on-completions-only" in command
    assert "--gradient-checkpointing" in command
    assert "--train-layernorm" in command
    assert "--max-trainable-parameters 1000000000" in command
    assert "--min-trainable-parameters 200000000" in command
    assert "--load-in-8bit" not in command
    assert "training/qwen_sft_peft.py" in command
    assert "torchrun --nproc_per_node=8 training/qwen_sft_peft.py" in command
    assert "torchrun --nproc_per_node=8 python3" not in command
    assert (
        payload["uniform_lora_policy"]
        == "all matching transformer layers, shared rank, attention plus mlp projection targets"
    )
    assert payload["train_layernorm"] is True
    assert payload["max_trainable_parameters"] == 1_000_000_000
    assert payload["min_trainable_parameters"] == 200_000_000


def test_qlora_command_adds_8bit_load() -> None:
    payload = renderer.build_command(args("qlora"))
    assert payload["uses_qlora"] is True
    assert "--load-in-8bit" in payload["command"]
