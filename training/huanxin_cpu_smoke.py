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
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.runtime_overlay import configure_runtime_overlay_from_env

configure_runtime_overlay_from_env()

from training.model_backend import (
    build_runtime_upgrade_message,
    probe_model_runtime_compat,
    run_text_forward_preflight,
    runtime_autoconfig_requires_upgrade,
)
from training.model_family_preflight import trainer_backend_preflight_block
from training.text_preprocessor_backend import (
    TextPreprocessorBackend,
    build_supervised_text_example,
    load_text_preprocessor_backend,
    pad_supervised_text_batch,
)

REQUIRED_MODULES = [
    "torch",
    "transformers",
    "accelerate",
    "datasets",
    "peft",
]

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
    parser.add_argument(
        "--max-length",
        type=int,
        default=2048,
        help="Maximum sequence length used for text batch preflight",
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


def load_first_record(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if line:
                return json.loads(line)
    raise ValueError(f"No rows found in {path}")


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
        from transformers import AutoConfig, AutoModelForCausalLM, AutoProcessor, AutoTokenizer, PreTrainedTokenizerFast
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
        runtime_summary = probe_model_runtime_compat(args.model_name, AutoConfig)
        if runtime_summary is None:
            raise RuntimeError(f"Unable to inspect model config metadata for {args.model_name}")
        summary.update(runtime_summary)
        runtime_error = runtime_summary.get("runtime_autoconfig_error")
        if runtime_error is not None and runtime_autoconfig_requires_upgrade(
            str(summary.get("config_model_type") or ""),
            Exception(str(runtime_error)),
        ):
            summary["stage"] = "runtime_compat"
            summary["status"] = "error"
            summary["error_type"] = str(runtime_summary.get("runtime_autoconfig_error_type") or "RuntimeError")
            summary["error"] = build_runtime_upgrade_message(args.model_name, summary)
            print(json.dumps(summary, indent=2, ensure_ascii=False))
            return 1
        backend_blocker = trainer_backend_preflight_block(
            str(summary.get("config_model_type") or ""),
            [str(item) for item in (summary.get("config_architectures") or [])],
        )
    except Exception as exc:
        summary["stage"] = "config_probe"
        summary["status"] = "error"
        summary["error_type"] = type(exc).__name__
        summary["error"] = str(exc)
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 1

    try:
        text_preprocessor = load_text_preprocessor_backend(
            args.model_name, AutoTokenizer, AutoProcessor, PreTrainedTokenizerFast
        )
        summary["text_preprocessor_backend_kind"] = text_preprocessor.backend_kind
        summary["render_backend_class"] = text_preprocessor.render_backend.__class__.__name__
        summary["text_backend_class"] = text_preprocessor.text_backend.__class__.__name__
        summary["save_backend_class"] = text_preprocessor.save_backend.__class__.__name__
        tokenizer = text_preprocessor.text_backend
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

    try:
        sample_record = load_first_record(args.dataset)
        preflight_example = build_supervised_text_example(
            sample_record,
            text_preprocessor,
            args.max_length,
            train_on_completions_only=True,
        )
        preflight_batch = pad_supervised_text_batch([preflight_example], text_preprocessor.text_backend, torch)
        summary["text_batch_preflight"] = {
            "example_id": preflight_example.get("example_id"),
            "input_token_count": len(preflight_example["input_ids"]),
            "attention_token_count": len(preflight_example["attention_mask"]),
            "prompt_token_count": int(preflight_example.get("prompt_token_count") or 0),
            "batch_input_shape": list(preflight_batch["input_ids"].shape),
            "batch_label_shape": list(preflight_batch["labels"].shape),
            "masked_label_tokens": int((preflight_batch["labels"] == -100).sum().item()),
        }
    except Exception as exc:
        summary["stage"] = "text_batch_preflight"
        summary["status"] = "error"
        summary["error_type"] = type(exc).__name__
        summary["error"] = str(exc)
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 1

    if backend_blocker is not None:
        summary["stage"] = "trainer_backend_preflight"
        summary["status"] = "error"
        summary["error"] = backend_blocker
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 1

    if args.load_model:
        try:
            model = AutoModelForCausalLM.from_pretrained(args.model_name, trust_remote_code=True)
        except Exception as exc:
            summary["stage"] = "model_load"
            summary["status"] = "error"
            summary["error_type"] = type(exc).__name__
            summary["error"] = str(exc)
            print(json.dumps(summary, indent=2, ensure_ascii=False))
            return 1
        try:
            parameter_count = sum(param.numel() for param in model.parameters())
            summary["model_class"] = model.__class__.__name__
            summary["parameter_count"] = int(parameter_count)
            summary["dtype"] = str(next(model.parameters()).dtype)
            summary["text_forward_preflight"] = run_text_forward_preflight(
                model,
                preflight_batch,
                torch_module=torch,
            )
        except Exception as exc:
            summary["stage"] = "text_forward_preflight"
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
