#!/usr/bin/env python3
"""Remote CPU smoke test for Huanxin training bootstrap.

This script proves only training-readiness basics:
- required libraries import
- chat-style dataset rows can be read
- tokenizer can be loaded for the target checkpoint
- optional model load is attempted only when explicitly requested

It is intentionally modest. Success means the remote stack is real enough to
continue; failure should expose the exact missing package or incompatible model
load instead of pretending fine-tuning already works.
"""

from __future__ import annotations

import argparse
import importlib
import json
import platform
from pathlib import Path

REQUIRED_MODULES = [
    "torch",
    "transformers",
    "accelerate",
    "datasets",
    "peft",
]


def load_model_config_metadata(model_name: str) -> dict:
    from transformers import PretrainedConfig

    config_dict, _unused_kwargs = PretrainedConfig.get_config_dict(model_name, trust_remote_code=True)
    return config_dict


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-name", required=True, help="HF model id or local path")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("data/seed/splits-auto-seed/train.jsonl"),
        help="Chat-style JSONL dataset to inspect",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=2,
        help="How many dataset rows to inspect for schema sanity",
    )
    parser.add_argument(
        "--load-model",
        action="store_true",
        help="Attempt full AutoModelForCausalLM load in addition to tokenizer load",
    )
    return parser.parse_args()


def import_versions() -> dict[str, str]:
    versions = {}
    for module_name in REQUIRED_MODULES:
        module = importlib.import_module(module_name)
        versions[module_name] = getattr(module, "__version__", "unknown")
    return versions


def inspect_dataset(path: Path, max_samples: int) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(f"dataset not found: {path}")

    sample_ids: list[str] = []
    sample_domains: list[str | None] = []
    sample_message_counts: list[int] = []
    role_histogram: dict[str, int] = {}
    total_rows = 0
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            row = json.loads(line)
            total_rows += 1
            example_id = row.get("example_id", "<missing>")
            if len(sample_ids) < max_samples:
                sample_ids.append(example_id)
                sample_domains.append(row.get("metadata", {}).get("domain"))
            messages = row.get("messages")
            if not isinstance(messages, list) or not messages:
                raise ValueError(f"row {example_id} has invalid messages payload")
            if len(sample_message_counts) < max_samples:
                sample_message_counts.append(len(messages))
            for index, message in enumerate(messages):
                if not isinstance(message, dict):
                    raise ValueError(f"row {example_id} message {index} is not an object")
                role = message.get("role")
                content = message.get("content")
                if not isinstance(role, str) or not role.strip():
                    raise ValueError(f"row {example_id} message {index} has invalid role")
                if not isinstance(content, str) or not content.strip():
                    raise ValueError(f"row {example_id} message {index} has invalid content")
                role_histogram[role] = role_histogram.get(role, 0) + 1
    return {
        "path": str(path),
        "rows": total_rows,
        "sample_ids": sample_ids,
        "sample_domains": sample_domains,
        "sample_message_counts": sample_message_counts,
        "role_histogram": role_histogram,
    }


def main() -> int:
    args = parse_args()

    summary: dict[str, object] = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "target_model": args.model_name,
        "load_model_requested": args.load_model,
    }

    try:
        summary["modules"] = import_versions()
    except Exception as exc:
        summary["stage"] = "import_versions"
        summary["status"] = "error"
        summary["error_type"] = type(exc).__name__
        summary["error"] = str(exc)
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 1

    try:
        summary["dataset"] = inspect_dataset(args.dataset, args.max_samples)
    except Exception as exc:
        summary["stage"] = "inspect_dataset"
        summary["status"] = "error"
        summary["error_type"] = type(exc).__name__
        summary["error"] = str(exc)
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 1

    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except Exception as exc:
        summary["stage"] = "runtime_imports"
        summary["status"] = "error"
        summary["error_type"] = type(exc).__name__
        summary["error"] = str(exc)
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 1

    try:
        summary["torch_cuda_available"] = torch.cuda.is_available()
    except Exception as exc:
        summary["stage"] = "torch_cuda_check"
        summary["status"] = "error"
        summary["error_type"] = type(exc).__name__
        summary["error"] = str(exc)
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 1

    try:
        config_dict = load_model_config_metadata(args.model_name)
        summary["config_model_type"] = config_dict.get("model_type")
        summary["config_architectures"] = config_dict.get("architectures")
        if summary["config_model_type"] == "qwen3_5" or any(
            "ConditionalGeneration" in str(item) for item in (summary["config_architectures"] or [])
        ):
            summary["stage"] = "runtime_compat"
            summary["status"] = "error"
            summary["error_type"] = "UnsupportedModelArchitecture"
            summary["error"] = (
                "Current smoke path only supports text-only AutoTokenizer + AutoModelForCausalLM checkpoints. "
                "This target exposes a qwen3_5 conditional-generation architecture and needs a newer "
                "Transformers runtime plus a processor-aware path before remote fine-tuning."
            )
            print(json.dumps(summary, indent=2, ensure_ascii=False))
            return 1
    except Exception as exc:
        summary["stage"] = "config_probe"
        summary["status"] = "error"
        summary["error_type"] = type(exc).__name__
        summary["error"] = str(exc)
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 1

    try:
        tokenizer = AutoTokenizer.from_pretrained(args.model_name, trust_remote_code=True)
        summary["tokenizer_class"] = tokenizer.__class__.__name__
        summary["tokenizer_vocab_size"] = getattr(tokenizer, "vocab_size", None)
        if tokenizer.pad_token is None and tokenizer.eos_token is not None:
            tokenizer.pad_token = tokenizer.eos_token
            summary["pad_token_filled_from_eos"] = True
        else:
            summary["pad_token_filled_from_eos"] = False
    except Exception as exc:
        summary["stage"] = "tokenizer_load"
        summary["status"] = "error"
        summary["error_type"] = type(exc).__name__
        summary["error"] = str(exc)
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 1

    if args.load_model:
        try:
            model = AutoModelForCausalLM.from_pretrained(args.model_name, trust_remote_code=True)
            parameter_count = sum(param.numel() for param in model.parameters())
            summary["model_class"] = model.__class__.__name__
            summary["parameter_count"] = int(parameter_count)
            summary["dtype"] = str(next(model.parameters()).dtype)
        except Exception as exc:
            summary["stage"] = "model_load"
            summary["status"] = "error"
            summary["error_type"] = type(exc).__name__
            summary["error"] = str(exc)
            print(json.dumps(summary, indent=2, ensure_ascii=False))
            return 1
    else:
        summary["model_load_skipped"] = True

    summary["status"] = "ok"
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
