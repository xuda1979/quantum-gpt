from __future__ import annotations

import json
from pathlib import Path

import torch
from safetensors.torch import save_file

from training.manual_lora_merge import merge_lora_adapter_into_model


class _SelfAttn(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.q_proj = torch.nn.Linear(3, 2, bias=False)


class _Layer(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.self_attn = _SelfAttn()


class _InnerModel(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.layers = torch.nn.ModuleList([_Layer()])


class _RootModel(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.model = _InnerModel()


def test_merge_lora_adapter_into_model(tmp_path: Path) -> None:
    adapter_dir = tmp_path / "adapter"
    adapter_dir.mkdir()
    (adapter_dir / "adapter_config.json").write_text(
        json.dumps(
            {
                "peft_type": "LORA",
                "modules_to_save": None,
                "lora_alpha": 8,
                "r": 2,
                "fan_in_fan_out": False,
            }
        ),
        encoding="utf-8",
    )

    lora_a = torch.tensor([[1.0, 2.0, 0.0], [0.0, 1.0, 1.0]])
    lora_b = torch.tensor([[1.0, 0.0], [0.5, 1.0]])
    save_file(
        {
            "base_model.model.model.layers.0.self_attn.q_proj.lora_A.weight": lora_a,
            "base_model.model.model.layers.0.self_attn.q_proj.lora_B.weight": lora_b,
        },
        str(adapter_dir / "adapter_model.safetensors"),
    )

    model = _RootModel()
    with torch.no_grad():
        model.model.layers[0].self_attn.q_proj.weight.zero_()

    merged_count = merge_lora_adapter_into_model(model, adapter_dir)

    expected = lora_b.matmul(lora_a) * 4.0
    assert merged_count == 1
    assert torch.allclose(model.model.layers[0].self_attn.q_proj.weight, expected)
