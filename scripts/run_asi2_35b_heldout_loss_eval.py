#!/usr/bin/env python3
"""Held-out CE loss / perplexity eval for the ASI2 Qwen3.6-35B-A3B LoRA run.

Compares base vs a LoRA adapter/checkpoint on a chat-SFT held-out set using the
*same* completions-only cross-entropy metric the trainer logs, so base and
adapter perplexities are directly comparable. Intended for the 495-row dedup
eval split (data/generated/quantum_finetune_verified_chat_sft_dedup_1k/eval_chatml.jsonl).
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from pathlib import Path
from typing import Any

import logging

import torch
import transformers
from peft import PeftModel
from transformers import AutoConfig, AutoModelForCausalLM, AutoProcessor, AutoTokenizer, PreTrainedTokenizerFast

# This transformers build logs ``Model config {config}`` at INFO during
# AutoConfig.from_pretrained, which triggers PretrainedConfig.__repr__ ->
# to_diff_dict -> recursive_diff_dict. With the qwen3_5_moe overlay's nested
# sub-config stored as a plain dict, recursive_diff_dict raises
# "'dict' object has no attribute 'to_dict'", crashing the whole load. We never
# need that repr, so (1) silence the config logger and (2) replace the fragile
# __repr__ with a safe one that does not walk nested diff dicts.
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("transformers.configuration_utils").setLevel(logging.ERROR)
transformers.logging.set_verbosity_error()
try:
    from transformers.configuration_utils import PretrainedConfig as _PretrainedConfig

    def _safe_config_repr(self):  # noqa: ANN001
        return f"{self.__class__.__name__}(model_type={getattr(self, 'model_type', '?')})"

    _PretrainedConfig.__repr__ = _safe_config_repr
except Exception:  # noqa: BLE001
    pass

# Same root cause (overlay keeps a nested text_config as a plain dict) breaks
# GenerationConfig.from_model_config during model __init__:
# ``decoder_config.to_dict()`` on a dict. We only need a usable generation
# config for eval (no sampling), so fall back to a default GenerationConfig
# whenever the model-config-derived construction raises.
try:
    from transformers.generation.configuration_utils import GenerationConfig as _GenerationConfig

    _orig_from_model_config = _GenerationConfig.from_model_config.__func__

    def _safe_from_model_config(cls, model_config):  # noqa: ANN001
        try:
            return _orig_from_model_config(cls, model_config)
        except Exception:  # noqa: BLE001
            gc_obj = cls()
            for attr in ("bos_token_id", "eos_token_id", "pad_token_id"):
                val = getattr(model_config, attr, None)
                if val is not None:
                    setattr(gc_obj, attr, val)
            gc_obj._from_model_config = True
            return gc_obj

    _GenerationConfig.from_model_config = classmethod(_safe_from_model_config)
except Exception:  # noqa: BLE001
    pass

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from torch.utils.data import DataLoader

from training.qwen_sft_peft import ChatSftDataset, PaddingCollator, evaluate
from training.text_preprocessor_backend import load_text_preprocessor_backend
from scripts.run_asi2_35b_pass1_eval import load_35b_model, first_parameter_device


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--base-model", type=Path, required=True)
    p.add_argument("--adapter", type=Path, required=True)
    p.add_argument("--eval-file", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--device", default="npu")
    p.add_argument("--npu-max-memory-gib", type=int, default=56)
    p.add_argument("--max-length", type=int, default=512)
    p.add_argument("--batch-size", type=int, default=1)
    p.add_argument("--models", choices=["base", "adapter", "both"], default="both")
    return p.parse_args()


def build_backend(model_path: Path):
    backend = load_text_preprocessor_backend(str(model_path), AutoTokenizer, AutoProcessor, PreTrainedTokenizerFast)
    tok = backend.text_backend
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "right"
    return backend


def main() -> int:
    args = parse_args()
    started = time.time()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    backend = build_backend(args.base_model)
    dataset = ChatSftDataset(
        args.eval_file,
        backend,
        args.max_length,
        train_on_completions_only=True,
        research_methods=[],
        stage="sft",
    )
    # Static-pad every batch to --max-length so the Ascend TBE compiler compiles
    # the forward kernel once instead of recompiling per sequence length (critical
    # on the 1-core host). Padding is masked (attention_mask=0, labels=-100), so
    # the completions-only CE loss is identical to dynamic padding.
    collator = PaddingCollator(backend.text_backend, torch, pad_to_max_length=args.max_length)
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=False, collate_fn=collator)
    print(json.dumps({"stage": "eval_dataset_ready", "examples": len(dataset)}), flush=True)

    results: dict[str, Any] = {}
    load_metadata: dict[str, Any] = {}

    if args.models in ("base", "both"):
        print(json.dumps({"stage": "load_base"}), flush=True)
        base, load_metadata = load_35b_model(args.base_model, args)
        device = first_parameter_device(base, args.device)
        results["base"] = evaluate(base, loader, device, torch)
        print(json.dumps({"stage": "base_done", **results["base"]}), flush=True)
        del base
        gc.collect()
        if args.device == "npu" and hasattr(torch, "npu"):
            torch.npu.empty_cache()

    if args.models in ("adapter", "both"):
        print(json.dumps({"stage": "load_adapter"}), flush=True)
        adapter_base, load_metadata = load_35b_model(args.base_model, args)
        adapter = PeftModel.from_pretrained(adapter_base, str(args.adapter))
        adapter.eval()
        device = first_parameter_device(adapter, args.device)
        results["adapter"] = evaluate(adapter, loader, device, torch)
        print(json.dumps({"stage": "adapter_done", **results["adapter"]}), flush=True)

    comparison = None
    if "base" in results and "adapter" in results:
        comparison = {
            "loss_delta": round(results["adapter"]["loss"] - results["base"]["loss"], 6),
            "perplexity_delta": round(results["adapter"]["perplexity"] - results["base"]["perplexity"], 6),
            "adapter_better": results["adapter"]["loss"] < results["base"]["loss"],
        }

    payload = {
        "created_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "base_model": str(args.base_model),
        "adapter": str(args.adapter),
        "eval_file": str(args.eval_file),
        "eval_examples": len(dataset),
        "metric": "completions_only_cross_entropy_loss_and_perplexity",
        "results": results,
        "comparison": comparison,
        "load_metadata": load_metadata,
        "duration_sec": round(time.time() - started, 3),
    }
    tmp = args.output.with_suffix(args.output.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(args.output)
    print(json.dumps({"stage": "done", "output": str(args.output), "results": results, "comparison": comparison}, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
