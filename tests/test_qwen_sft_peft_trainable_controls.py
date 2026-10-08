from __future__ import annotations

import pytest

from training.qwen_sft_peft import (
    apply_native_lora,
    enable_layernorm_training,
    enforce_min_trainable_parameters,
    enforce_trainable_parameter_budget,
)


class DummyParameter:
    def __init__(self, count: int, requires_grad: bool = False) -> None:
        self._count = count
        self.requires_grad = requires_grad

    def numel(self) -> int:
        return self._count


class DummyModel:
    def __init__(self) -> None:
        self.params = [
            ("model.layers.0.self_attn.q_proj.lora_A.default.weight", DummyParameter(64, True)),
            ("model.layers.0.input_layernorm.weight", DummyParameter(16, False)),
            ("model.layers.0.post_attention_layernorm.weight", DummyParameter(16, False)),
            ("model.layers.0.mlp.gate_proj.weight", DummyParameter(128, False)),
        ]

    def named_parameters(self):
        return iter(self.params)


def test_enable_layernorm_training_unfreezes_only_norm_parameters() -> None:
    model = DummyModel()
    summary = enable_layernorm_training(model)

    states = {name: parameter.requires_grad for name, parameter in model.named_parameters()}
    assert summary["trainable_layernorm_count"] == 2
    assert summary["trainable_layernorm_parameter_count"] == 32
    assert states["model.layers.0.self_attn.q_proj.lora_A.default.weight"] is True
    assert states["model.layers.0.input_layernorm.weight"] is True
    assert states["model.layers.0.post_attention_layernorm.weight"] is True
    assert states["model.layers.0.mlp.gate_proj.weight"] is False


def test_enforce_trainable_parameter_budget_blocks_large_adapter() -> None:
    assert enforce_trainable_parameter_budget(49_000_000, 50_000_000)["within_budget"] is True
    with pytest.raises(SystemExit):
        enforce_trainable_parameter_budget(100_000_000, 50_000_000)


def test_enforce_min_trainable_parameters_blocks_tiny_adapter() -> None:
    assert enforce_min_trainable_parameters(250_000_000, 200_000_000)["meets_minimum"] is True
    with pytest.raises(SystemExit):
        enforce_min_trainable_parameters(99_000_000, 200_000_000)


def test_apply_native_lora_wraps_only_requested_linear_modules() -> None:
    torch = pytest.importorskip("torch")

    model = torch.nn.Module()
    model.q_proj = torch.nn.Linear(8, 8, bias=False)
    model.k_proj = torch.nn.Linear(8, 8, bias=False)
    model.v_proj = torch.nn.Linear(8, 8, bias=False)

    summary = apply_native_lora(model, torch, ["q_proj", "v_proj"], rank=2, alpha=4, dropout=0.0)

    trainable = {name for name, parameter in model.named_parameters() if parameter.requires_grad}
    assert summary["wrapped_module_count"] == 2
    assert "q_proj.lora_A.weight" in trainable
    assert "q_proj.lora_B.weight" in trainable
    assert "v_proj.lora_A.weight" in trainable
    assert "v_proj.lora_B.weight" in trainable
    assert all("k_proj" not in name for name in trainable)

    output = model.q_proj(torch.ones(1, 8)) + model.v_proj(torch.ones(1, 8))
    assert output.shape == (1, 8)
