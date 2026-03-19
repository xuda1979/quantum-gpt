#!/usr/bin/env python3
"""Minimal PEFT SFT runner for chat-style JSONL corpora."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import torch
from peft import LoraConfig, TaskType, get_peft_model
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

try:
    import torch_npu  # noqa: F401
except ImportError:
    torch_npu = None  # type: ignore[assignment]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-name", required=True)
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
    parser.add_argument(
        "--target-modules",
        nargs="*",
        default=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    )
    return parser.parse_args()


def resolve_device(choice: str) -> torch.device:
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


def render_messages(tokenizer: AutoTokenizer, record: dict) -> str:
    messages = record.get("messages")
    if not isinstance(messages, list) or not messages:
        raise ValueError(f"Record {record.get('example_id')} has no messages")
    if hasattr(tokenizer, "apply_chat_template"):
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)

    parts = []
    for message in messages:
        role = str(message.get("role", "user")).upper()
        content = str(message.get("content", ""))
        parts.append(f"{role}: {content}")
    return "\n\n".join(parts)


class ChatSftDataset(Dataset):
    def __init__(self, path: Path, tokenizer: AutoTokenizer, max_length: int) -> None:
        rows = load_jsonl(path)
        self.examples = []
        for record in rows:
            text = render_messages(tokenizer, record)
            encoded = tokenizer(
                text,
                truncation=True,
                max_length=max_length,
                padding=False,
                return_attention_mask=True,
            )
            self.examples.append(
                {
                    "input_ids": encoded["input_ids"],
                    "attention_mask": encoded["attention_mask"],
                    "example_id": record.get("example_id"),
                }
            )

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(self, index: int) -> dict:
        return self.examples[index]


class PaddingCollator:
    def __init__(self, tokenizer: AutoTokenizer) -> None:
        self.tokenizer = tokenizer

    def __call__(self, batch: list[dict]) -> dict[str, torch.Tensor]:
        padded = self.tokenizer.pad(
            [{"input_ids": item["input_ids"], "attention_mask": item["attention_mask"]} for item in batch],
            padding=True,
            return_tensors="pt",
        )
        labels = padded["input_ids"].clone()
        labels[padded["attention_mask"] == 0] = -100
        padded["labels"] = labels
        return padded


def evaluate(model: torch.nn.Module, loader: DataLoader, device: torch.device) -> dict[str, float]:
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


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    device = resolve_device(args.device)
    if device.type == "npu":
        torch.npu.set_device(0)

    tokenizer = AutoTokenizer.from_pretrained(args.model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    train_dataset = ChatSftDataset(args.train_file, tokenizer, args.max_length)
    eval_dataset = ChatSftDataset(args.eval_file, tokenizer, args.max_length) if args.eval_file else None

    collator = PaddingCollator(tokenizer)
    train_loader = DataLoader(train_dataset, batch_size=args.per_device_batch_size, shuffle=True, collate_fn=collator)
    eval_loader = None
    if eval_dataset is not None:
        eval_loader = DataLoader(eval_dataset, batch_size=args.per_device_batch_size, shuffle=False, collate_fn=collator)

    model = AutoModelForCausalLM.from_pretrained(args.model_name, trust_remote_code=True)
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=args.lora_rank,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        target_modules=args.target_modules,
        bias="none",
    )
    model = get_peft_model(model, lora_config)
    model.to(device)
    model.train()

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate)
    total_train_steps = max(args.max_steps, 1)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=total_train_steps)

    metrics: list[dict[str, float | int]] = []
    global_step = 0
    optimizer.zero_grad(set_to_none=True)

    for epoch in range(args.num_epochs):
        for batch_index, batch in enumerate(train_loader, start=1):
            batch = {name: tensor.to(device) for name, tensor in batch.items()}
            outputs = model(**batch)
            loss = outputs.loss / args.gradient_accumulation_steps
            loss.backward()

            if batch_index % args.gradient_accumulation_steps == 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad(set_to_none=True)
                global_step += 1

                if global_step % args.log_steps == 0:
                    record: dict[str, float | int] = {
                        "step": global_step,
                        "epoch": epoch + 1,
                        "train_loss": float(loss.item() * args.gradient_accumulation_steps),
                        "lr": float(scheduler.get_last_lr()[0]),
                    }
                    if eval_loader is not None and global_step % args.eval_steps == 0:
                        record.update({f"eval_{k}": v for k, v in evaluate(model, eval_loader, device).items()})
                        model.train()
                    metrics.append(record)
                    print(json.dumps(record, ensure_ascii=False))

                if global_step >= args.max_steps:
                    break
        if global_step >= args.max_steps:
            break

    final_eval = evaluate(model, eval_loader, device) if eval_loader is not None else None
    adapter_dir = args.output_dir / "adapter"
    model.save_pretrained(adapter_dir)
    tokenizer.save_pretrained(adapter_dir)

    summary = {
        "model_name": args.model_name,
        "device": str(device),
        "train_examples": len(train_dataset),
        "eval_examples": len(eval_dataset) if eval_dataset is not None else 0,
        "max_steps": global_step,
        "final_eval": final_eval,
        "metrics": metrics,
    }
    (args.output_dir / "metrics.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
