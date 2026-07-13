#!/usr/bin/env python3
"""Run a tiny qualitative base-vs-adapter comparison on a fixed eval slice.

Loads prompts from reports/base_vs_adapter_eval_slice.json, generates one response with the
base model and one with a LoRA adapter, and writes a side-by-side JSON artifact for review.
This is intentionally small and CPU-friendly for local experimentation.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import torch
from peft import PeftModel
from transformers import (
    AutoConfig,
    AutoModelForCausalLM,
    AutoProcessor,
    AutoTokenizer,
    PreTrainedTokenizerFast,
)

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from training.model_backend import (
    ensure_text_backend_preflight,
    load_causal_lm_with_text_backend_preflight,
)
from training.text_preprocessor_backend import (
    TextPreprocessorBackend,
    load_text_preprocessor_backend,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--slice-json", type=Path, default=Path("reports/base_vs_adapter_eval_slice.json")
    )
    parser.add_argument("--base-model", type=Path, default=Path("models/Qwen3.6-27B"))
    parser.add_argument(
        "--adapter", type=Path, default=Path("outputs/fast-lora-qwen25-1p5b-mini/adapter")
    )
    parser.add_argument("--output", type=Path, default=Path("reports/base_vs_adapter_outputs.json"))
    parser.add_argument("--max-new-tokens", type=int, default=192)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument(
        "--limit", type=int, default=0, help="Optional max number of examples to run (0 = all)"
    )
    parser.add_argument("--device", default="cpu")
    parser.add_argument(
        "--npu-device-map",
        choices=["auto", "balanced-layers"],
        default="auto",
        help="For --device npu, shard language-model layers across visible NPUs instead of loading on one card.",
    )
    parser.add_argument(
        "--npu-max-memory-gib",
        type=int,
        default=56,
        help="Per-NPU max_memory GiB used with --device npu --npu-device-map balanced-layers.",
    )
    parser.add_argument(
        "--offload-dir",
        type=Path,
        default=Path("outputs/base_vs_adapter_offload"),
        help="Used only with --device auto to let Accelerate spill weights to disk.",
    )
    return parser.parse_args()


def load_slice(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _visible_npu_indices() -> list[int]:
    raw = os.environ.get("ASCEND_RT_VISIBLE_DEVICES") or os.environ.get("ASCEND_VISIBLE_DEVICES")
    if not raw:
        return [0]
    indices: list[int] = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        try:
            indices.append(int(item))
        except ValueError:
            indices.append(len(indices))
    return indices or [0]


def _config_get(config, key: str):
    if hasattr(config, key):
        return getattr(config, key)
    if isinstance(config, dict):
        return config.get(key)
    return None


def build_balanced_npu_layer_device_map(config, visible_npus: list[int]) -> dict[str, int]:
    text_config = _config_get(config, "text_config") or _config_get(config, "llm_config") or config
    num_layers = _config_get(text_config, "num_hidden_layers") or _config_get(
        text_config, "num_layers"
    )
    if not num_layers:
        raise SystemExit(
            "Cannot build balanced NPU device map: config does not expose num_hidden_layers."
        )
    devices = list(range(len(visible_npus)))
    last_device = devices[-1]
    device_map: dict[str, int] = {
        "model.embed_tokens": devices[0],
        "model.norm": last_device,
        "model.rotary_emb": devices[0],
        "model.language_model.embed_tokens": devices[0],
        "model.language_model.norm": last_device,
        "model.language_model.rotary_emb": devices[0],
        "lm_head": last_device,
    }
    for layer_idx in range(int(num_layers)):
        device_map[f"model.layers.{layer_idx}"] = devices[
            layer_idx * len(devices) // int(num_layers)
        ]
        device_map[f"model.language_model.layers.{layer_idx}"] = devices[
            layer_idx * len(devices) // int(num_layers)
        ]
    return device_map


def load_causal_lm(
    model_path: Path, device: str, offload_dir: Path, npu_device_map: str, npu_max_memory_gib: int
):
    model_kwargs = {
        "trust_remote_code": True,
        "low_cpu_mem_usage": True,
        "torch_dtype": "auto",
    }
    if device == "npu" and npu_device_map == "balanced-layers":
        model_config = AutoConfig.from_pretrained(str(model_path), trust_remote_code=True)
        visible_npus = _visible_npu_indices()
        model_kwargs["device_map"] = build_balanced_npu_layer_device_map(model_config, visible_npus)
        model_kwargs["max_memory"] = {
            device_idx: f"{npu_max_memory_gib}GiB" for device_idx in range(len(visible_npus))
        }
        model = load_causal_lm_with_text_backend_preflight(
            str(model_path),
            auto_config_cls=AutoConfig,
            auto_model_for_causal_lm_cls=AutoModelForCausalLM,
            model_kwargs=model_kwargs,
        )
    elif device == "auto":
        offload_dir.mkdir(parents=True, exist_ok=True)
        model_kwargs["device_map"] = "auto"
        model_kwargs["offload_folder"] = str(offload_dir)
        model = load_causal_lm_with_text_backend_preflight(
            str(model_path),
            auto_config_cls=AutoConfig,
            auto_model_for_causal_lm_cls=AutoModelForCausalLM,
            model_kwargs=model_kwargs,
        )
    else:
        model = load_causal_lm_with_text_backend_preflight(
            str(model_path),
            auto_config_cls=AutoConfig,
            auto_model_for_causal_lm_cls=AutoModelForCausalLM,
            model_kwargs=model_kwargs,
        ).to(device)
    generation_config = getattr(model, "generation_config", None)
    if generation_config is not None:
        # Keep deterministic runs quiet by neutralizing stale sampling defaults.
        generation_config.do_sample = False
        generation_config.temperature = 1.0
        generation_config.top_p = 1.0
        generation_config.top_k = 50
    model.eval()
    return model


def load_text_backend(model_path: Path) -> TextPreprocessorBackend:
    ensure_text_backend_preflight(str(model_path), AutoConfig)
    return load_text_preprocessor_backend(
        str(model_path), AutoTokenizer, AutoProcessor, PreTrainedTokenizerFast
    )


def resolve_input_device(model, device: str) -> torch.device:
    if device not in {"auto", "npu"}:
        return torch.device(device)
    try:
        return next(model.parameters()).device
    except StopIteration:
        return torch.device("cpu")


def build_inputs(backend: TextPreprocessorBackend, prompt: str, device: torch.device):
    messages = [{"role": "user", "content": prompt}]
    render_backend = backend.render_backend
    text_backend = backend.text_backend
    if hasattr(render_backend, "apply_chat_template"):
        try:
            text = render_backend.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False,
            )
        except TypeError:
            text = render_backend.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
    else:
        text = "USER: " + prompt
    tokens = text_backend(text, return_tensors="pt")
    return {k: v.to(device) for k, v in tokens.items()}, text


def generate_text(
    model,
    backend: TextPreprocessorBackend,
    prompt: str,
    max_new_tokens: int,
    temperature: float,
    device: str,
) -> str:
    input_device = resolve_input_device(model, device)
    inputs, _ = build_inputs(backend, prompt, input_device)
    prompt_len = inputs["input_ids"].shape[1]
    tokenizer = backend.text_backend
    gen_kwargs = {
        "max_new_tokens": max_new_tokens,
        "do_sample": temperature > 0,
        "temperature": temperature if temperature > 0 else None,
        "pad_token_id": tokenizer.eos_token_id,
    }
    gen_kwargs = {k: v for k, v in gen_kwargs.items() if v is not None}
    with torch.inference_mode():
        output = model.generate(**inputs, **gen_kwargs)
    new_tokens = output[0][prompt_len:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


def print_progress(phase: str, index: int, total: int, example_id: str) -> None:
    print(f"[{phase}] {index}/{total} {example_id}", flush=True)


def write_json_atomically(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f"{path.name}.tmp")
    with tmp_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    tmp_path.replace(path)


def main() -> int:
    args = parse_args()
    if not args.base_model.exists():
        raise SystemExit(f"Base model path does not exist: {args.base_model}")
    if not args.adapter.exists():
        raise SystemExit(f"Adapter path does not exist: {args.adapter}")
    payload = load_slice(args.slice_json)
    examples = (
        payload["examples"][: args.limit] if args.limit and args.limit > 0 else payload["examples"]
    )

    backend = load_text_backend(args.base_model)
    tokenizer = backend.text_backend
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    results = {
        "slice_json": str(args.slice_json),
        "base_model": str(args.base_model),
        "adapter": str(args.adapter),
        "max_new_tokens": args.max_new_tokens,
        "temperature": args.temperature,
        "examples": [
            {
                "example_id": example["example_id"],
                "task_id": example.get("task_id"),
                "task_name": example.get("task_name"),
                "domain": example.get("domain"),
                "prompt": example["prompt"],
                "reference": example.get("reference"),
                "review_checklist": example.get("review_checklist", []),
            }
            for example in examples
        ],
    }

    total_examples = len(examples)

    print(
        f"loading base model from {args.base_model} for {total_examples} examples on {args.device}",
        flush=True,
    )
    base_model = load_causal_lm(
        args.base_model,
        args.device,
        args.offload_dir / "base",
        args.npu_device_map,
        args.npu_max_memory_gib,
    )
    for index, example in enumerate(examples):
        print_progress("base", index + 1, total_examples, example["example_id"])
        results["examples"][index]["base_output"] = generate_text(
            base_model,
            backend,
            example["prompt"],
            args.max_new_tokens,
            args.temperature,
            args.device,
        )
    del base_model
    if args.device == "cpu":
        import gc

        gc.collect()

    print(f"loading adapter from {args.adapter}", flush=True)
    adapter_base = load_causal_lm(
        args.base_model,
        args.device,
        args.offload_dir / "adapter_base",
        args.npu_device_map,
        args.npu_max_memory_gib,
    )
    adapter_model = PeftModel.from_pretrained(adapter_base, str(args.adapter))
    adapter_model.eval()
    for index, example in enumerate(examples):
        print_progress("adapter", index + 1, total_examples, example["example_id"])
        results["examples"][index]["adapter_output"] = generate_text(
            adapter_model,
            backend,
            example["prompt"],
            args.max_new_tokens,
            args.temperature,
            args.device,
        )
    del adapter_model
    del adapter_base
    if args.device == "cpu":
        import gc

        gc.collect()

    write_json_atomically(args.output, results)
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
