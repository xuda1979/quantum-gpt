#!/usr/bin/env python3
"""Minimal PEFT SFT runner for chat-style JSONL corpora."""

from __future__ import annotations

import argparse
import copy
from dataclasses import dataclass
import hashlib
import json
import math
import os
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

import torch
from torch.utils.data import DataLoader, Dataset

if TYPE_CHECKING:
    from transformers import AutoProcessor, AutoTokenizer

try:
    from torch.distributed.elastic.multiprocessing.errors import record as elastic_record
except Exception:  # noqa: BLE001
    def elastic_record(function: Any) -> Any:
        return function

from training.research_plugins import load_research_methods, summarize_methods


@dataclass
class TextPreprocessorBackend:
    render_backend: Any
    text_backend: Any
    save_backend: Any
    backend_kind: str


def load_model_config_metadata(model_name: str) -> dict[str, Any]:
    from transformers import PretrainedConfig

    config_dict, _unused_kwargs = PretrainedConfig.get_config_dict(model_name, trust_remote_code=True)
    return config_dict


def load_tokenizer_config_metadata(model_name: str) -> dict[str, Any]:
    tokenizer_config_path = Path(model_name) / "tokenizer_config.json"
    if not tokenizer_config_path.exists():
        return {}
    return json.loads(tokenizer_config_path.read_text(encoding="utf-8"))


def probe_model_runtime_compat(model_name: str, auto_config_cls: Any) -> dict[str, Any] | None:
    try:
        config_dict = load_model_config_metadata(model_name)
    except Exception:
        return None

    model_type = str(config_dict.get("model_type") or "")
    architectures = [str(item) for item in (config_dict.get("architectures") or [])]
    summary: dict[str, Any] = {
        "config_model_type": model_type,
        "config_architectures": architectures,
        "runtime_autoconfig_ok": False,
    }
    try:
        runtime_config = auto_config_cls.from_pretrained(model_name, trust_remote_code=True)
        summary["runtime_autoconfig_ok"] = True
        summary["runtime_config_class"] = runtime_config.__class__.__name__
    except Exception as exc:  # noqa: BLE001
        summary["runtime_autoconfig_error_type"] = type(exc).__name__
        summary["runtime_autoconfig_error"] = str(exc)
        if model_type == "qwen3_5":
            raise SystemExit(
                f"Transformers runtime is too old for '{model_name}' "
                f"(model_type='{model_type}', architectures={architectures}). "
                "This path now supports processor-aware text preprocessing, but the active "
                "runtime still cannot resolve Qwen3.5 configs. Upgrade the bootstrap stack "
                "to a Qwen3.5-capable Transformers build before launching this fine-tune."
            ) from exc
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-name", required=True)
    parser.add_argument(
        "--adapter-init",
        type=Path,
        default=None,
        help="Optional existing PEFT adapter directory to continue training from.",
    )
    parser.add_argument("--train-file", type=Path, required=True)
    parser.add_argument("--eval-file", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda", "npu"], default="auto")
    parser.add_argument("--max-length", type=int, default=2048)
    parser.add_argument("--per-device-batch-size", type=int, default=1)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument("--num-epochs", type=int, default=1)
    parser.add_argument("--max-steps", type=int, default=10)
    parser.add_argument("--eval-steps", type=int, default=5)
    parser.add_argument("--log-steps", type=int, default=1)
    parser.add_argument("--lora-rank", type=int, default=16)
    parser.add_argument("--lora-alpha", type=int, default=32)
    parser.add_argument("--lora-dropout", type=float, default=0.05)
    parser.add_argument("--load-in-8bit", action="store_true")
    parser.add_argument("--train-on-completions-only", action="store_true")
    parser.add_argument("--research-methods", nargs="*", default=[])
    parser.add_argument("--overwrite-output-dir", action="store_true")
    parser.add_argument("--allow-output-dir-reuse", action="store_true")
    parser.add_argument(
        "--target-modules",
        nargs="*",
        default=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    )
    return parser.parse_args()


def require_training_dependencies() -> tuple[Any, Any, Any, Any, Any, Any, Any, Any, Any, Any, Any]:
    try:
        import torch
        from peft import LoraConfig, PeftModel, TaskType, get_peft_model
        from torch.utils.data import DataLoader, Dataset
        from transformers import AutoConfig, AutoModelForCausalLM, AutoProcessor, AutoTokenizer, PreTrainedTokenizerFast
    except ImportError as exc:
        raise SystemExit(
            "Missing training dependencies. Install the bootstrap stack first, for example: "
            "python3 -m pip install -r training/requirements-huanxin-cpu.txt"
        ) from exc

    try:
        import torch_npu  # noqa: F401
    except ImportError:
        pass

    return (
        torch,
        LoraConfig,
        PeftModel,
        TaskType,
        get_peft_model,
        DataLoader,
        Dataset,
        AutoConfig,
        AutoModelForCausalLM,
        AutoTokenizer,
        AutoProcessor,
        PreTrainedTokenizerFast,
    )


def supports_text_backend(candidate: Any) -> bool:
    return candidate is not None and hasattr(candidate, "__call__") and hasattr(candidate, "pad")


def load_tokenizers_backend_fallback(model_name: str, pretrained_tokenizer_fast_cls: Any) -> TextPreprocessorBackend | None:
    tokenizer_config = load_tokenizer_config_metadata(model_name)
    if tokenizer_config.get("tokenizer_class") != "TokenizersBackend":
        return None

    tokenizer_path = Path(model_name) / "tokenizer.json"
    if not tokenizer_path.exists():
        return None

    additional_special_tokens = []
    for key in (
        "image_token",
        "video_token",
        "vision_bos_token",
        "vision_eos_token",
        "audio_bos_token",
        "audio_eos_token",
        "audio_token",
    ):
        value = tokenizer_config.get(key)
        if value and value not in additional_special_tokens:
            additional_special_tokens.append(value)

    tokenizer = pretrained_tokenizer_fast_cls(
        tokenizer_file=str(tokenizer_path),
        pad_token=tokenizer_config.get("pad_token"),
        eos_token=tokenizer_config.get("eos_token"),
        additional_special_tokens=additional_special_tokens or None,
        clean_up_tokenization_spaces=bool(tokenizer_config.get("clean_up_tokenization_spaces", False)),
        model_max_length=int(tokenizer_config.get("model_max_length", 262144)),
    )
    return TextPreprocessorBackend(
        render_backend=tokenizer,
        text_backend=tokenizer,
        save_backend=tokenizer,
        backend_kind="pretrained_tokenizer_fast_fallback",
    )


def load_text_preprocessor_backend(model_name: str, auto_tokenizer_cls: Any, auto_processor_cls: Any, pretrained_tokenizer_fast_cls: Any) -> TextPreprocessorBackend:
    processor_error: Exception | None = None
    try:
        processor = auto_processor_cls.from_pretrained(model_name, trust_remote_code=True)
        processor_tokenizer = getattr(processor, "tokenizer", None)
        if supports_text_backend(processor_tokenizer):
            render_backend = processor if hasattr(processor, "apply_chat_template") else processor_tokenizer
            return TextPreprocessorBackend(
                render_backend=render_backend,
                text_backend=processor_tokenizer,
                save_backend=processor,
                backend_kind="processor.tokenizer",
            )
    except Exception as exc:  # noqa: BLE001
        processor_error = exc

    try:
        tokenizer = auto_tokenizer_cls.from_pretrained(model_name, trust_remote_code=True)
        return TextPreprocessorBackend(
            render_backend=tokenizer,
            text_backend=tokenizer,
            save_backend=tokenizer,
            backend_kind="tokenizer",
        )
    except Exception as exc:  # noqa: BLE001
        fallback = load_tokenizers_backend_fallback(model_name, pretrained_tokenizer_fast_cls)
        if fallback is not None:
            return fallback
        error_parts = [f"AutoTokenizer load failed: {type(exc).__name__}: {exc}"]
        if processor_error is not None:
            error_parts.append(f"AutoProcessor fallback also failed: {type(processor_error).__name__}: {processor_error}")
        raise SystemExit("Unable to load a text preprocessing backend. " + " | ".join(error_parts)) from exc


def resolve_device(torch: Any, choice: str) -> Any:
    if choice == "cpu":
        return torch.device("cpu")
    if choice == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA requested but not available")
        return torch.device("cuda")
    if choice == "npu":
        if not hasattr(torch, "npu") or not torch.npu.is_available():
            raise RuntimeError("NPU requested but not available")
        return torch.device("npu")
    if hasattr(torch, "npu") and torch.npu.is_available():
        return torch.device("npu")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number} of {path}: {exc}") from exc
    if not rows:
        raise ValueError(f"No rows found in {path}")
    return rows


def render_messages(render_backend: Any, record: dict) -> str:
    messages = record.get("messages")
    if not isinstance(messages, list) or not messages:
        raise ValueError(f"Record {record.get('example_id')} has no messages")
    if hasattr(render_backend, "apply_chat_template"):
        return render_backend.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)

    parts = []
    for message in messages:
        role = str(message.get("role", "user")).upper()
        content = str(message.get("content", ""))
        parts.append(f"{role}: {content}")
    return "\n\n".join(parts)


class ChatSftDataset:
    def __init__(
        self,
        path: Path,
        backend: TextPreprocessorBackend,
        max_length: int,
        train_on_completions_only: bool = False,
        research_methods: list[Any] | None = None,
        stage: str = "sft",
    ) -> None:
        rows = load_jsonl(path)
        self.examples = []
        research_methods = research_methods or []
        for record in rows:
            working_record = copy.deepcopy(record)
            for method in research_methods:
                working_record = method.augment_sft_record(working_record, stage=stage)
            full_text = render_messages(backend.render_backend, working_record)
            encoded = backend.text_backend(
                full_text,
                truncation=True,
                max_length=max_length,
                padding=False,
                return_attention_mask=True,
            )
            example = {
                "input_ids": encoded["input_ids"],
                "attention_mask": encoded["attention_mask"],
                "example_id": working_record.get("example_id"),
            }
            if train_on_completions_only:
                messages = working_record.get("messages", [])
                if len(messages) >= 2 and messages[-1].get("role") == "assistant":
                    prompt_text = render_messages(backend.render_backend, {"messages": messages[:-1]})
                    prompt_ids = backend.text_backend(
                        prompt_text,
                        truncation=True,
                        max_length=max_length,
                        padding=False,
                        return_attention_mask=False,
                    )["input_ids"]
                    example["prompt_token_count"] = min(len(prompt_ids), len(example["input_ids"]))
            self.examples.append(example)

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(self, index: int) -> dict:
        return self.examples[index]


class PaddingCollator:
    def __init__(self, text_backend: Any) -> None:
        self.text_backend = text_backend

    def __call__(self, batch: list[dict]) -> dict[str, torch.Tensor]:
        padded = self.text_backend.pad(
            [{"input_ids": item["input_ids"], "attention_mask": item["attention_mask"]} for item in batch],
            padding=True,
            return_tensors="pt",
        )
        labels = padded["input_ids"].clone()
        labels[padded["attention_mask"] == 0] = -100
        for row_index, item in enumerate(batch):
            prompt_token_count = item.get("prompt_token_count")
            if prompt_token_count:
                labels[row_index, :prompt_token_count] = -100
        padded["labels"] = labels
        return padded


def evaluate(model: Any, loader: Any, device: Any) -> dict[str, float]:
    model.eval()
    total_loss = 0.0
    total_items = 0
    with torch.no_grad():
        for batch in loader:
            batch = {name: tensor.to(device) for name, tensor in batch.items()}
            loss = model(**batch).loss
            batch_items = batch["input_ids"].size(0)
            total_loss += float(loss.item()) * batch_items
            total_items += batch_items
    mean_loss = total_loss / max(total_items, 1)
    return {"loss": mean_loss, "perplexity": float(math.exp(min(mean_loss, 20.0)))}


def build_run_signature(args: argparse.Namespace) -> dict[str, Any]:
    signature = {
        "model_name": args.model_name,
        "adapter_init": str(args.adapter_init) if args.adapter_init else None,
        "train_file": str(args.train_file),
        "eval_file": str(args.eval_file) if args.eval_file else None,
        "device": args.device,
        "max_length": args.max_length,
        "per_device_batch_size": args.per_device_batch_size,
        "gradient_accumulation_steps": args.gradient_accumulation_steps,
        "learning_rate": args.learning_rate,
        "num_epochs": args.num_epochs,
        "max_steps": args.max_steps,
        "eval_steps": args.eval_steps,
        "log_steps": args.log_steps,
        "lora_rank": args.lora_rank,
        "lora_alpha": args.lora_alpha,
        "lora_dropout": args.lora_dropout,
        "load_in_8bit": args.load_in_8bit,
        "train_on_completions_only": args.train_on_completions_only,
        "research_methods": list(args.research_methods),
        "target_modules": list(args.target_modules),
    }
    signature_json = json.dumps(signature, sort_keys=True)
    signature["signature_sha256"] = hashlib.sha256(signature_json.encode("utf-8")).hexdigest()
    return signature


def validate_output_dir(args: argparse.Namespace, run_signature: dict[str, Any]) -> None:
    config_path = args.output_dir / "run_config.json"
    has_existing_artifacts = config_path.exists() or (args.output_dir / "adapter").exists() or (args.output_dir / "metrics.json").exists()

    if args.overwrite_output_dir:
        return

    if not has_existing_artifacts:
        return

    if config_path.exists():
        existing = json.loads(config_path.read_text(encoding="utf-8"))
        existing_signature = existing.get("signature", {})
        if existing_signature != run_signature:
            raise SystemExit(
                "Refusing to reuse an existing output directory with a different training configuration. "
                f"Use a new --output-dir or pass --overwrite-output-dir if replacement is intentional: {args.output_dir}"
            )

    if not args.allow_output_dir_reuse:
        raise SystemExit(
            f"Output directory already contains prior run artifacts: {args.output_dir}. "
            "Use a new --output-dir, or pass --allow-output-dir-reuse / --overwrite-output-dir explicitly."
        )


@elastic_record
def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    run_signature = build_run_signature(args)
    validate_output_dir(args, run_signature)
    research_methods = load_research_methods(args.research_methods)
    print(json.dumps({"stage": "args_parsed", "output_dir": str(args.output_dir), "train_file": str(args.train_file), "eval_file": str(args.eval_file) if args.eval_file else None}, ensure_ascii=False), flush=True)
    print(json.dumps({"stage": "research_methods_loaded", "methods": summarize_methods(research_methods)}, ensure_ascii=False), flush=True)

    (
        torch,
        LoraConfig,
        PeftModel,
        TaskType,
        get_peft_model,
        DataLoader,
        _Dataset,
        AutoConfig,
        AutoModelForCausalLM,
        AutoTokenizer,
        AutoProcessor,
        PreTrainedTokenizerFast,
    ) = require_training_dependencies()
    print(json.dumps({"stage": "deps_loaded"}, ensure_ascii=False), flush=True)

    runtime_compat = probe_model_runtime_compat(args.model_name, AutoConfig)
    if runtime_compat is not None:
        print(
            json.dumps(
                {
                    "stage": "model_runtime_compat_checked",
                    **runtime_compat,
                },
                ensure_ascii=False,
            ),
            flush=True,
        )

    text_preprocessor = load_text_preprocessor_backend(args.model_name, AutoTokenizer, AutoProcessor, PreTrainedTokenizerFast)
    print(
        json.dumps(
            {
                "stage": "text_preprocessor_loaded",
                "backend_kind": text_preprocessor.backend_kind,
                "render_backend_class": text_preprocessor.render_backend.__class__.__name__,
                "text_backend_class": text_preprocessor.text_backend.__class__.__name__,
                "save_backend_class": text_preprocessor.save_backend.__class__.__name__,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )

    device = resolve_device(torch, args.device)
    print(json.dumps({"stage": "device_resolved", "device": str(device), "requested": args.device}, ensure_ascii=False), flush=True)

    # DDP setup
    distributed = "RANK" in os.environ and "WORLD_SIZE" in os.environ
    local_rank = int(os.environ.get("LOCAL_RANK", 0))
    rank = int(os.environ.get("RANK", 0))
    world_size = int(os.environ.get("WORLD_SIZE", 1))

    if distributed:
        if device.type == "npu":
            torch.npu.set_device(local_rank)
            device = torch.device(f"npu:{local_rank}")
        torch.distributed.init_process_group(backend="hccl" if device.type == "npu" else "nccl")
    else:
        if device.type == "npu":
            torch.npu.set_device(0)
    print(json.dumps({"stage": "ddp_ready", "distributed": distributed, "rank": rank, "world_size": world_size, "device": str(device)}, ensure_ascii=False), flush=True)

    tokenizer = text_preprocessor.text_backend
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    print(json.dumps({"stage": "tokenizer_loaded", "pad_token": tokenizer.pad_token, "padding_side": tokenizer.padding_side}, ensure_ascii=False), flush=True)

    train_dataset = ChatSftDataset(
        args.train_file,
        text_preprocessor,
        args.max_length,
        train_on_completions_only=args.train_on_completions_only,
        research_methods=research_methods,
        stage="sft_train",
    )
    eval_dataset = ChatSftDataset(
        args.eval_file,
        text_preprocessor,
        args.max_length,
        train_on_completions_only=args.train_on_completions_only,
        research_methods=research_methods,
        stage="sft_eval",
    ) if args.eval_file else None
    print(json.dumps({"stage": "datasets_ready", "train_examples": len(train_dataset), "eval_examples": len(eval_dataset) if eval_dataset is not None else 0, "max_length": args.max_length}, ensure_ascii=False), flush=True)

    collator = PaddingCollator(text_preprocessor.text_backend)
    train_sampler = torch.utils.data.distributed.DistributedSampler(train_dataset, num_replicas=world_size, rank=rank, shuffle=True) if distributed else None
    train_loader = DataLoader(train_dataset, batch_size=args.per_device_batch_size, shuffle=(train_sampler is None), collate_fn=collator, sampler=train_sampler)
    eval_loader = None
    if eval_dataset is not None:
        eval_loader = DataLoader(eval_dataset, batch_size=args.per_device_batch_size, shuffle=False, collate_fn=collator)

    optimizer_steps_per_epoch = len(train_loader) // args.gradient_accumulation_steps
    max_available_steps = optimizer_steps_per_epoch * args.num_epochs
    if optimizer_steps_per_epoch < 1:
        raise ValueError(
            "Not enough batches to produce one optimizer step. "
            "Lower --gradient-accumulation-steps or increase training data."
        )
    if args.max_steps > max_available_steps:
        raise ValueError(
            f"Requested --max-steps {args.max_steps} but current settings only allow "
            f"{max_available_steps} optimizer step(s) across {args.num_epochs} epoch(s). "
            "Increase --num-epochs, lower --gradient-accumulation-steps, or reduce --max-steps."
        )
    print(
        json.dumps(
            {
                "stage": "train_schedule_ready",
                "optimizer_steps_per_epoch": optimizer_steps_per_epoch,
                "max_available_steps": max_available_steps,
                "requested_max_steps": args.max_steps,
                "num_epochs": args.num_epochs,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )

    # Keep remote multi-rank launches from spiking host RAM while preserving the
    # checkpoint's native precision for OmniCoder/Qwen-family snapshots.
    model_kwargs = {
        "trust_remote_code": True,
        "low_cpu_mem_usage": True,
        "torch_dtype": "auto",
    }
    if args.load_in_8bit:
        model_kwargs.pop("torch_dtype", None)
        model_kwargs["load_in_8bit"] = True
        model_kwargs["device_map"] = "auto"
    print(json.dumps({"stage": "model_load_start", "model_name": args.model_name, "t": time.time()}, ensure_ascii=False), flush=True)
    model_load_started_at = time.time()
    try:
        model = AutoModelForCausalLM.from_pretrained(args.model_name, **model_kwargs)
    except Exception as exc:
        print(
            json.dumps(
                {
                    "stage": "model_load_failed",
                    "t": time.time(),
                    "dt_model_load_sec": round(time.time() - model_load_started_at, 3),
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        raise
    print(json.dumps({"stage": "model_loaded", "t": time.time(), "dt_model_load_sec": round(time.time() - model_load_started_at, 3)}, ensure_ascii=False), flush=True)
    if args.adapter_init is not None:
        model = PeftModel.from_pretrained(model, str(args.adapter_init), is_trainable=True)
        print(
            json.dumps(
                {
                    "stage": "adapter_init_loaded",
                    "adapter_init": str(args.adapter_init),
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
    else:
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=args.lora_rank,
            lora_alpha=args.lora_alpha,
            lora_dropout=args.lora_dropout,
            target_modules=args.target_modules,
            bias="none",
        )
        model = get_peft_model(model, lora_config)
        print(json.dumps({"stage": "lora_wrapped"}, ensure_ascii=False), flush=True)
    model.to(device)
    print(json.dumps({"stage": "model_on_device", "device": str(device)}, ensure_ascii=False), flush=True)
    if distributed:
        model = torch.nn.parallel.DistributedDataParallel(model, device_ids=[local_rank])
        print(json.dumps({"stage": "ddp_wrapped"}, ensure_ascii=False), flush=True)
    model.train()
    print(json.dumps({"stage": "train_mode"}, ensure_ascii=False), flush=True)

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate)
    total_train_steps = max(args.max_steps, 1)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=total_train_steps)

    metrics: list[dict[str, float | int]] = []
    global_step = 0
    optimizer.zero_grad(set_to_none=True)
    print(json.dumps({"stage": "optimizer_ready", "max_steps": args.max_steps, "gradient_accumulation_steps": args.gradient_accumulation_steps}, ensure_ascii=False), flush=True)

    for epoch in range(args.num_epochs):
        if train_sampler is not None:
            train_sampler.set_epoch(epoch)
        print(json.dumps({"stage": "epoch_start", "epoch": epoch + 1}, ensure_ascii=False), flush=True)
        for batch_index, batch in enumerate(train_loader, start=1):
            if batch_index == 1:
                first_batch_time = time.time()
                print(json.dumps({"stage": "first_batch_loaded", "batch_index": batch_index, "input_shape": list(batch["input_ids"].shape), "t": first_batch_time}, ensure_ascii=False), flush=True)
            batch = {name: tensor.to(device) for name, tensor in batch.items()}
            outputs = model(**batch)
            if batch_index == 1:
                print(json.dumps({"stage": "first_forward_done", "batch_index": batch_index, "t": time.time(), "dt_from_batch_loaded_sec": round(time.time() - first_batch_time, 3)}, ensure_ascii=False), flush=True)
            loss = outputs.loss / args.gradient_accumulation_steps
            if batch_index == 1:
                print(json.dumps({"stage": "first_loss_ready", "batch_index": batch_index, "loss": float(loss.item())}, ensure_ascii=False), flush=True)
            loss.backward()
            if batch_index == 1:
                print(json.dumps({"stage": "first_backward_done", "batch_index": batch_index}, ensure_ascii=False), flush=True)

            if batch_index % args.gradient_accumulation_steps == 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                if batch_index == 1:
                    print(json.dumps({"stage": "first_clip_done", "batch_index": batch_index}, ensure_ascii=False), flush=True)
                optimizer.step()
                if batch_index == 1:
                    print(json.dumps({"stage": "first_optimizer_step_done", "batch_index": batch_index}, ensure_ascii=False), flush=True)
                scheduler.step()
                if batch_index == 1:
                    print(json.dumps({"stage": "first_scheduler_step_done", "batch_index": batch_index}, ensure_ascii=False), flush=True)
                optimizer.zero_grad(set_to_none=True)
                if batch_index == 1:
                    print(json.dumps({"stage": "first_zero_grad_done", "batch_index": batch_index}, ensure_ascii=False), flush=True)
                global_step += 1

                if global_step % args.log_steps == 0:
                    record: dict[str, float | int] = {
                        "step": global_step,
                        "epoch": epoch + 1,
                        "train_loss": float(loss.item() * args.gradient_accumulation_steps),
                        "lr": float(scheduler.get_last_lr()[0]),
                    }
                    if batch_index == 1:
                        print(json.dumps({"stage": "first_record_ready", "batch_index": batch_index}, ensure_ascii=False), flush=True)
                    if eval_loader is not None and global_step % args.eval_steps == 0:
                        if batch_index == 1:
                            print(json.dumps({"stage": "first_eval_start", "batch_index": batch_index, "t": time.time()}, ensure_ascii=False), flush=True)
                        eval_started_at = time.time()
                        record.update({f"eval_{k}": v for k, v in evaluate(model.module if distributed else model, eval_loader, device).items()})
                        if batch_index == 1:
                            print(json.dumps({"stage": "first_eval_done", "batch_index": batch_index, "t": time.time(), "dt_eval_sec": round(time.time() - eval_started_at, 3)}, ensure_ascii=False), flush=True)
                        model.train()
                    metrics.append(record)
                    if rank == 0:
                        print(json.dumps(record, ensure_ascii=False))

                if global_step >= args.max_steps:
                    break
        if global_step >= args.max_steps:
            break

    final_eval = None
    if eval_loader is not None:
        print(json.dumps({"stage": "final_eval_start", "t": time.time()}, ensure_ascii=False), flush=True)
        final_eval_started_at = time.time()
        final_eval = evaluate(model.module if distributed else model, eval_loader, device)
        print(json.dumps({"stage": "final_eval_done", "t": time.time(), "dt_final_eval_sec": round(time.time() - final_eval_started_at, 3)}, ensure_ascii=False), flush=True)

    if rank == 0:
        save_model = model.module if distributed else model
        adapter_dir = args.output_dir / "adapter"
        print(json.dumps({"stage": "save_start", "t": time.time(), "adapter_dir": str(adapter_dir)}, ensure_ascii=False), flush=True)
        save_started_at = time.time()
        save_model.save_pretrained(adapter_dir)
        text_preprocessor.save_backend.save_pretrained(adapter_dir)
        print(json.dumps({"stage": "save_done", "t": time.time(), "dt_save_sec": round(time.time() - save_started_at, 3)}, ensure_ascii=False), flush=True)

        summary = {
            "model_name": args.model_name,
            "signature": run_signature,
            "device": str(device),
            "world_size": world_size,
            "train_examples": len(train_dataset),
            "eval_examples": len(eval_dataset) if eval_dataset is not None else 0,
            "optimizer_steps_per_epoch": optimizer_steps_per_epoch,
            "max_available_steps": max_available_steps,
            "requested_max_steps": args.max_steps,
            "completed_steps": global_step,
            "max_steps": global_step,
            "research_methods": summarize_methods(research_methods),
            "final_eval": final_eval,
            "metrics": metrics,
        }
        (args.output_dir / "run_config.json").write_text(json.dumps({"signature": run_signature}, indent=2) + "\n", encoding="utf-8")
        (args.output_dir / "metrics.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(summary, ensure_ascii=False, indent=2))


    if distributed:
        torch.distributed.destroy_process_group()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
