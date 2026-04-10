from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from safetensors.torch import load_file


def _resolve_module(root: Any, dotted_path: str) -> Any:
    module = root
    for segment in dotted_path.split("."):
        if segment.isdigit():
            module = module[int(segment)]
        else:
            module = getattr(module, segment)
    return module


def merge_lora_adapter_into_model(model: Any, adapter_dir: str | Path) -> int:
    adapter_path = Path(adapter_dir)
    config = json.loads((adapter_path / "adapter_config.json").read_text(encoding="utf-8"))
    if config.get("peft_type") != "LORA":
        raise ValueError(f"Unsupported adapter type for manual merge: {config.get('peft_type')}")
    if config.get("modules_to_save"):
        raise ValueError("Manual LoRA merge does not support modules_to_save.")

    scaling = float(config["lora_alpha"]) / float(config["r"])
    fan_in_fan_out = bool(config.get("fan_in_fan_out", False))
    state = load_file(str(adapter_path / "adapter_model.safetensors"))

    merged_count = 0
    prefix = "base_model.model."
    suffix = ".lora_A.weight"
    for key, lora_a in state.items():
        if not key.endswith(suffix):
            continue
        if not key.startswith(prefix):
            raise ValueError(f"Unexpected adapter key prefix: {key}")

        base_path = key[len(prefix) : -len(suffix)]
        lora_b_key = f"{prefix}{base_path}.lora_B.weight"
        if lora_b_key not in state:
            raise ValueError(f"Missing LoRA B weight for {key}")

        module = _resolve_module(model, base_path)
        if not hasattr(module, "weight"):
            raise ValueError(f"Resolved module {base_path} does not expose a weight tensor")

        lora_b = state[lora_b_key]
        delta = lora_b.float().matmul(lora_a.float()) * scaling
        if fan_in_fan_out:
            delta = delta.transpose(0, 1)

        weight = module.weight.data
        module.weight.data = weight + delta.to(device=weight.device, dtype=weight.dtype)
        merged_count += 1

    if merged_count == 0:
        raise ValueError(f"No LoRA weights were merged from {adapter_path}")
    return merged_count
