from __future__ import annotations

import argparse

import scripts.render_timeboxed_scaleup_commands as render_timeboxed_scaleup_commands


def _args(**overrides: str | None) -> argparse.Namespace:
    defaults = {
        "target": render_timeboxed_scaleup_commands.DEFAULT_TARGET,
        "iteration_profile": "fast",
        "model_name": None,
        "train_file": None,
        "eval_file": None,
        "benchmark_file": None,
        "paper_inputs": None,
        "paper_output_dir": None,
        "paper_dataset_name": None,
        "paper_train_file": None,
        "paper_eval_file": None,
        "paper_router_output_dir": None,
        "paper_router_target_module_regex": None,
        "paper_router_trainable_param_regex": None,
        "paper_router_freeze_param_regex": None,
        "sft_adapter_init": None,
        "grpo_adapter_init": None,
        "sft_output_dir": None,
        "grpo_output_dir": None,
        "output": render_timeboxed_scaleup_commands.OUTPUT,
    }
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def test_default_qwen36_render_uses_next_round_base_model() -> None:
    config = render_timeboxed_scaleup_commands.resolve_target_config(_args())
    bootstrap = render_timeboxed_scaleup_commands.build_bootstrap_command(config)
    paper_router = render_timeboxed_scaleup_commands.build_paper_router_warmup_command(config)
    sft = render_timeboxed_scaleup_commands.build_sft_command(config)
    grpo = render_timeboxed_scaleup_commands.build_grpo_command(config)
    assert "training/requirements-huanxin-cpu.txt" in bootstrap
    assert config["iteration_profile"] == "fast"
    assert config["model_name"] == "models/Qwen3.6-27B"
    assert "models/Qwen3.6-27B" in paper_router
    assert "models/Qwen3.6-27B" in sft
    assert "models/Qwen3.6-27B" in grpo
    assert "--output-dir outputs/qwen36-27b-quantum-generalization-sft-8npu-true40-fastiter" in sft
    assert "--adapter-init" not in sft
    assert "outputs/qwen36-27b-quantum-generalization-sft-8npu-true40/adapter" in grpo
    assert "--output-dir outputs/qwen36-27b-quantum-generalization-grpo-8npu-true8-fastiter" in grpo
    assert "--max-steps 12" in sft
    assert "--eval-steps 6" in sft
    assert "--log-steps 1" in sft
    assert "--group-size 2" in grpo
    assert "--grpo-steps 2" in grpo
    assert "--max-new-tokens 96" in grpo


def test_omnicoder_render_preserves_current_paths() -> None:
    config = render_timeboxed_scaleup_commands.resolve_target_config(_args(target="omnicoder9b"))
    bootstrap = render_timeboxed_scaleup_commands.build_bootstrap_command(config)
    sft = render_timeboxed_scaleup_commands.build_sft_command(config)
    grpo = render_timeboxed_scaleup_commands.build_grpo_command(config)
    assert "training/requirements-huanxin-cpu.txt" in bootstrap
    assert config["iteration_profile"] == "fast"
    assert "models/OmniCoder-9B" in sft
    assert "--output-dir outputs/omnicoder9b-quantum-generalization-sft-8npu-true40-fastiter" in sft
    assert (
        "outputs/interface-prefix-omnicoder9b-semantic-v4-2npu-true20-20260329T2219CST/adapter"
        in sft
    )
    assert (
        "outputs/interface-prefix-omnicoder9b-semantic-v4-2npu-true20-20260329T2219CST/adapter"
        in grpo
    )
    assert (
        "--output-dir outputs/omnicoder9b-quantum-generalization-grpo-8npu-true8-fastiter" in grpo
    )
    assert "--max-steps 12" in sft
    assert "--eval-steps 6" in sft
    assert "--log-steps 1" in sft
    assert "--group-size 2" in grpo
    assert "--grpo-steps 2" in grpo
    assert "--max-new-tokens 96" in grpo


def test_standard_profile_preserves_longer_omnicoder_paths() -> None:
    config = render_timeboxed_scaleup_commands.resolve_target_config(
        _args(target="omnicoder9b", iteration_profile="standard")
    )
    sft = render_timeboxed_scaleup_commands.build_sft_command(config)
    grpo = render_timeboxed_scaleup_commands.build_grpo_command(config)
    assert config["iteration_profile"] == "standard"
    assert "outputs/omnicoder9b-quantum-generalization-sft-8npu-true40" in sft
    assert "outputs/omnicoder9b-quantum-generalization-sft-8npu-true40-fastiter" not in sft
    assert "outputs/omnicoder9b-quantum-generalization-grpo-8npu-true8" in grpo
    assert "--max-steps 40" in sft
    assert "--group-size 4" in grpo


def test_gemma_e2b_render_uses_gemma_paths_and_no_empty_sft_adapter() -> None:
    config = render_timeboxed_scaleup_commands.resolve_target_config(_args(target="gemma4-e2b-it"))
    bootstrap = render_timeboxed_scaleup_commands.build_bootstrap_command(config)
    sft = render_timeboxed_scaleup_commands.build_sft_command(config)
    grpo = render_timeboxed_scaleup_commands.build_grpo_command(config)
    assert "training/requirements-gemma4-runtime.txt" in bootstrap
    assert "models/gemma-4-E2B-it" in sft
    assert "models/gemma-4-E2B-it" in grpo
    assert "OmniCoder-9B" not in sft
    assert "OmniCoder-9B" not in grpo
    assert "--adapter-init" not in sft
    assert "--adapter-init ''" not in sft
    assert "outputs/gemma4-e2b-it-quantum-generalization-sft-8npu-true40-fastiter" in sft
    assert "outputs/gemma4-e2b-it-quantum-generalization-grpo-8npu-true8-fastiter" in grpo


def test_gemma_e4b_render_uses_gemma_paths() -> None:
    config = render_timeboxed_scaleup_commands.resolve_target_config(_args(target="gemma4-e4b-it"))
    sft = render_timeboxed_scaleup_commands.build_sft_command(config)
    grpo = render_timeboxed_scaleup_commands.build_grpo_command(config)
    assert "models/gemma-4-E4B-it" in sft
    assert "models/gemma-4-E4B-it" in grpo
    assert "outputs/gemma4-e4b-it-quantum-generalization-sft-8npu-true40-fastiter" in sft
    assert "outputs/gemma4-e4b-it-quantum-generalization-grpo-8npu-true8-fastiter" in grpo


def test_gemma_26b_a4b_render_uses_gemma_paths() -> None:
    config = render_timeboxed_scaleup_commands.resolve_target_config(
        _args(target="gemma4-26b-a4b-it")
    )
    bootstrap = render_timeboxed_scaleup_commands.build_bootstrap_command(config)
    paper_dataset = render_timeboxed_scaleup_commands.build_paper_dataset_command(config)
    router_warmup = render_timeboxed_scaleup_commands.build_paper_router_warmup_command(config)
    sft = render_timeboxed_scaleup_commands.build_sft_command(config)
    grpo = render_timeboxed_scaleup_commands.build_grpo_command(config)
    assert "training/requirements-gemma4-runtime.txt" in bootstrap
    assert "\n" in bootstrap
    assert "scripts/build_paper_sft_dataset.py" in paper_dataset
    assert "\n  paper" in paper_dataset
    assert "data/generated/quantum-paper-router-warmup-v1" in paper_dataset
    assert "models/gemma-4-26B-A4B-it" in router_warmup
    assert "quantum_paper_router_warmup_messages_train.jsonl" in router_warmup
    assert "--target-module-regex '(?:^|\\.)(?:router|gate)(?:$|\\.)'" in router_warmup
    assert "--trainable-param-regex 'lora_'" in router_warmup
    assert "outputs/gemma4-26b-a4b-it-quantum-paper-router-warmup-fastiter" in router_warmup
    assert "models/gemma-4-26B-A4B-it" in sft
    assert "models/gemma-4-26B-A4B-it" in grpo
    assert "outputs/gemma4-26b-a4b-it-curriculum-sft-v1-fastiter" in sft
    assert "outputs/gemma4-26b-a4b-it-curriculum-grpo-v1-fastiter" in grpo
    assert "--max-steps 8" in router_warmup
    assert "--max-steps 12" in sft


def test_gemma_31b_render_uses_gemma_paths() -> None:
    config = render_timeboxed_scaleup_commands.resolve_target_config(_args(target="gemma4-31b-it"))
    sft = render_timeboxed_scaleup_commands.build_sft_command(config)
    grpo = render_timeboxed_scaleup_commands.build_grpo_command(config)
    assert "models/gemma-4-31B-it" in sft
    assert "models/gemma-4-31B-it" in grpo
    assert "outputs/gemma4-31b-it-quantum-generalization-sft-8npu-true40-fastiter" in sft
    assert "outputs/gemma4-31b-it-quantum-generalization-grpo-8npu-true8-fastiter" in grpo
