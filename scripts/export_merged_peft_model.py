#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.runtime_overlay import apply_transformers_peft_compat_shims, configure_runtime_overlay_from_env

configure_runtime_overlay_from_env()

import torch
import transformers
from transformers import AutoConfig, AutoModelForCausalLM

apply_transformers_peft_compat_shims(transformers)

from training.model_backend import load_causal_lm_with_text_backend_preflight
from training.manual_lora_merge import merge_lora_adapter_into_model
from training.qwen_sft_peft import resolve_device


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge a PEFT adapter into a standalone full model checkpoint.")
    parser.add_argument("--base-model", type=Path, required=True)
    parser.add_argument("--adapter", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", choices=("auto", "cpu", "cuda", "npu"), default="auto")
    parser.add_argument("--safe-serialization", action="store_true")
    return parser.parse_args()


def load_model(model_path: Path, device: Any) -> Any:
    return load_causal_lm_with_text_backend_preflight(
        str(model_path),
        auto_config_cls=AutoConfig,
        auto_model_for_causal_lm_cls=AutoModelForCausalLM,
        model_kwargs={
            "trust_remote_code": True,
            "low_cpu_mem_usage": True,
            "torch_dtype": "auto",
        },
    ).to(device)


def copy_base_auxiliary_files(base_model_dir: Path, output_dir: Path) -> None:
    weight_suffixes = (
        ".safetensors",
        ".safetensors.index.json",
        ".bin",
        ".pt",
        ".pth",
    )
    for source in base_model_dir.iterdir():
        if not source.is_file():
            continue
        if source.name.startswith("pytorch_model"):
            continue
        if source.name.startswith("model-") or source.name == "model.safetensors":
            continue
        if source.name.endswith(weight_suffixes):
            continue
        shutil.copy2(source, output_dir / source.name)


def main() -> None:
    args = parse_args()
    device = resolve_device(torch, args.device)
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    base_model = load_model(args.base_model, device)
    try:
        from peft import PeftModel

        merged = PeftModel.from_pretrained(base_model, str(args.adapter)).merge_and_unload()
    except Exception as exc:  # noqa: BLE001
        merged_count = merge_lora_adapter_into_model(base_model, args.adapter)
        print(
            f"manual_lora_merge_fallback={type(exc).__name__}:{exc}; merged_modules={merged_count}",
            file=sys.stderr,
        )
        merged = base_model
    if hasattr(merged, "save_pretrained"):
        merged.save_pretrained(str(output_dir), safe_serialization=args.safe_serialization)
    else:
        raise SystemExit("Merged model object does not support save_pretrained().")
    copy_base_auxiliary_files(args.base_model, output_dir)
    print(f"merged_model_dir={output_dir}")


if __name__ == "__main__":
    main()
