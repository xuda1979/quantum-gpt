#!/usr/bin/env python3
"""Prepare deterministic train/eval ChatML splits for verified finetuning data."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

DEFAULT_INPUT = Path(
    "data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_chatml.jsonl"
)
DEFAULT_OUTPUT_DIR = Path("data/generated/quantum_distillation_teacher_responses_asi2_v1_sft")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-jsonl", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--eval-ratio", type=float, default=0.1)
    parser.add_argument("--min-eval", type=int, default=10)
    parser.add_argument("--train-count", type=int, default=None)
    return parser.parse_args()


def to_chatml_row(row: dict[str, Any]) -> dict[str, Any]:
    instruction = str(row.get("instruction", "")).strip()
    output = str(row.get("output", "")).rstrip()
    example_id = str(row.get("id") or row.get("example_id") or "").strip()
    if not instruction:
        raise ValueError("row missing instruction")
    if not output:
        raise ValueError("row missing output")
    if not example_id:
        raise ValueError("row missing id")
    return {
        "example_id": example_id,
        "format": "chat-sft-v1",
        "messages": [
            {
                "role": "system",
                "content": "You are a careful quantum software engineering assistant. Use the user's task and any supplied context to produce correct, testable Python or precise repair guidance.",
            },
            {"role": "user", "content": instruction},
            {"role": "assistant", "content": output},
        ],
        "metadata": {
            "domain": row.get("domain"),
            "framework": row.get("framework"),
            "language": row.get("language"),
            "difficulty": row.get("difficulty"),
            "family": row.get("family"),
            "source_id": example_id,
        },
    }


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_no}: row must be object")
            if "instruction" in row and "output" in row:
                rows.append(to_chatml_row(row))
            elif row.get("format") == "chat-sft-v1":
                rows.append(row)
            else:
                raise ValueError(
                    f"{path}:{line_no}: expected instruction/output or format=chat-sft-v1"
                )
    if not rows:
        raise ValueError(f"No rows found in {path}")
    return rows


def stable_key(row: dict[str, Any]) -> str:
    example_id = str(row.get("example_id", ""))
    seed_id = str(row.get("metadata", {}).get("seed_example_id", ""))
    return hashlib.sha256(f"{example_id}\n{seed_id}".encode()).hexdigest()


def split_rows(
    rows: list[dict[str, Any]], *, eval_ratio: float, min_eval: int, train_count: int | None
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    ordered = sorted(rows, key=stable_key)
    if train_count is not None:
        if not 0 < train_count < len(ordered):
            raise ValueError("--train-count must be between 1 and len(rows)-1")
        train_rows = ordered[:train_count]
        eval_rows = ordered[train_count:]
        return train_rows, eval_rows
    if not 0.0 < eval_ratio < 0.5:
        raise ValueError("--eval-ratio must be between 0 and 0.5")
    eval_count = max(min_eval, round(len(rows) * eval_ratio))
    eval_count = min(max(eval_count, 1), len(rows) - 1)
    eval_rows = ordered[:eval_count]
    eval_ids = {row["example_id"] for row in eval_rows}
    train_rows = [row for row in rows if row["example_id"] not in eval_ids]
    return train_rows, eval_rows


def summarize_metadata(rows: list[dict[str, Any]]) -> dict[str, Any]:
    from collections import Counter

    metadata_rows = [
        row.get("metadata") if isinstance(row.get("metadata"), dict) else {} for row in rows
    ]
    return {
        "categories": dict(
            sorted(Counter(str(row.get("category")) for row in metadata_rows).items())
        ),
        "task_types": dict(
            sorted(Counter(str(row.get("task_type")) for row in metadata_rows).items())
        ),
        "frameworks": dict(
            sorted(Counter(str(row.get("framework")) for row in metadata_rows).items())
        ),
        "source_doc_count": len(
            {row.get("source_doc_sha256") for row in metadata_rows if row.get("source_doc_sha256")}
        ),
        "seed_count": len(
            {row.get("seed_example_id") for row in metadata_rows if row.get("seed_example_id")}
        ),
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True, sort_keys=True) + "\n")


def main() -> int:
    args = parse_args()
    rows = load_rows(args.input_jsonl)
    train_rows, eval_rows = split_rows(
        rows, eval_ratio=args.eval_ratio, min_eval=args.min_eval, train_count=args.train_count
    )
    train_path = args.output_dir / "train_chatml.jsonl"
    eval_path = args.output_dir / "eval_chatml.jsonl"
    manifest_path = args.output_dir / "manifest.json"
    write_jsonl(train_path, train_rows)
    write_jsonl(eval_path, eval_rows)
    manifest = {
        "ok": True,
        "source": str(args.input_jsonl),
        "train_file": str(train_path),
        "eval_file": str(eval_path),
        "total_rows": len(rows),
        "train_rows": len(train_rows),
        "eval_rows": len(eval_rows),
        "eval_ratio": args.eval_ratio,
        "split_policy": "stable_sha256_example_id_seed_id",
        "no_overlap": not (
            {row["example_id"] for row in train_rows} & {row["example_id"] for row in eval_rows}
        ),
        "total_summary": summarize_metadata(rows),
        "train_summary": summarize_metadata(train_rows),
        "eval_summary": summarize_metadata(eval_rows),
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
