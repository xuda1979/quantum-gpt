#!/usr/bin/env python3
"""Convert isq_train_cot.json into deterministic ChatML SFT train/eval splits."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

DEFAULT_INPUT = Path("isq_train_cot.json")
DEFAULT_OUTPUT_DIR = Path("data/generated/isq-cot-sft-80-20-v3")
SYSTEM_PROMPT = (
    "You are an expert quantum computing and ISQ programming assistant. "
    "Answer with rigorous reasoning, practical implementation detail, and clear caveats."
)
QUESTION_SUFFIX = "写成完整的可执行的代码。"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-json", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--train-ratio", type=float, default=0.8)
    return parser.parse_args()


def stable_key(row: dict[str, Any]) -> str:
    key = f"{row.get('task_id', '')}\n{row.get('dataset_index', '')}\n{row.get('prompt', '')}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def append_question_suffix(prompt: str) -> str:
    text = str(prompt or "").strip()
    if not text:
        return text
    if QUESTION_SUFFIX in text:
        return text
    if text.endswith(("。", ".", "?", "？", "!", "！")):
        return f"{text} {QUESTION_SUFFIX}"
    return f"{text}\n\n{QUESTION_SUFFIX}"


def load_source(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"{path} must contain a JSON list")
    rows = []
    seen_ids: set[str] = set()
    for index, row in enumerate(payload):
        if not isinstance(row, dict):
            raise ValueError(f"{path}[{index}] must be an object")
        prompt = append_question_suffix(row.get("prompt") or "")
        reference_answer = str(row.get("reference_answer") or "").strip()
        cot_reasoning = str(row.get("cot_reasoning") or "").strip()
        task_id = str(row.get("task_id") or f"isq_cot_{index:06d}").strip()
        if reference_answer and cot_reasoning:
            answer = f"{cot_reasoning}\n\n## Answer\n{reference_answer}"
        else:
            answer = reference_answer or cot_reasoning
        if not prompt or not answer.strip():
            continue
        example_key = f"{task_id}\n{index}"
        example_id = f"isq_cot_{hashlib.sha256(example_key.encode('utf-8')).hexdigest()[:16]}"
        if example_id in seen_ids:
            raise ValueError(f"duplicate generated example_id: {example_id}")
        seen_ids.add(example_id)
        metadata = {
            "task_id": task_id,
            "task_type": row.get("task_type"),
            "difficulty": row.get("difficulty"),
            "category": row.get("category"),
            "concept_tags": row.get("concept_tags")
            if isinstance(row.get("concept_tags"), list)
            else [],
            "cot_status": row.get("cot_status"),
            "source": row.get("source"),
            "dataset_index": row.get("dataset_index", index),
            "source_file": str(path),
        }
        chat_row = {
            "format": "chat-sft-v1",
            "source_schema": "isq-train-cot-json",
            "example_id": example_id,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": answer},
            ],
            "metadata": metadata,
        }
        rows.append((row, chat_row))
    if len(rows) < 2:
        raise ValueError(f"{path} did not contain enough usable prompt/answer rows")
    return [
        chat_row for _source_row, chat_row in sorted(rows, key=lambda item: stable_key(item[0]))
    ]


def split_rows(
    rows: list[dict[str, Any]], train_ratio: float
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not 0.5 < train_ratio < 1.0:
        raise ValueError("--train-ratio must be between 0.5 and 1.0")
    train_count = int(len(rows) * train_ratio)
    train_count = min(max(train_count, 1), len(rows) - 1)
    return rows[:train_count], rows[train_count:]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True, sort_keys=True) + "\n")


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    metadata = [row["metadata"] for row in rows]
    return {
        "rows": len(rows),
        "categories": dict(sorted(Counter(str(item.get("category")) for item in metadata).items())),
        "difficulties": dict(
            sorted(Counter(str(item.get("difficulty")) for item in metadata).items())
        ),
        "task_types": dict(
            sorted(Counter(str(item.get("task_type")) for item in metadata).items())
        ),
        "task_count": len({str(item.get("task_id")) for item in metadata}),
    }


def main() -> int:
    args = parse_args()
    rows = load_source(args.input_json)
    train_rows, eval_rows = split_rows(rows, args.train_ratio)
    train_path = args.output_dir / "train_chatml.jsonl"
    eval_path = args.output_dir / "eval_chatml.jsonl"
    manifest_path = args.output_dir / "manifest.json"
    write_jsonl(train_path, train_rows)
    write_jsonl(eval_path, eval_rows)
    train_ids = {row["example_id"] for row in train_rows}
    eval_ids = {row["example_id"] for row in eval_rows}
    manifest = {
        "ok": True,
        "source": str(args.input_json),
        "output_dir": str(args.output_dir),
        "train_file": str(train_path),
        "eval_file": str(eval_path),
        "total_rows": len(rows),
        "train_rows": len(train_rows),
        "eval_rows": len(eval_rows),
        "train_ratio": args.train_ratio,
        "eval_ratio": round(1.0 - args.train_ratio, 6),
        "split_policy": "stable_sha256_task_id_dataset_index_prompt_sorted_prefix",
        "no_example_id_overlap": not bool(train_ids & eval_ids),
        "total_summary": summarize(rows),
        "train_summary": summarize(train_rows),
        "eval_summary": summarize(eval_rows),
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
