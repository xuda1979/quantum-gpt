#!/usr/bin/env python3
"""Split the cleaned isQ finetuning corpus into train/test JSONL files."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

DEFAULT_INPUT = Path("data/generated/isq_train_cot_finetune_chatml.jsonl")
DEFAULT_OUTPUT_DIR = Path("data/generated/isq_train_cot_finetune_split_80_20")
PROMPT_SUFFIX = ". Write the code using isQ language."
LEGACY_PROMPT_SUFFIXES = (
    "Write the code using isQ language. Return complete standalone runnable code.",
    "Write the code using isQ language.",
)
SYSTEM_PROMPT = (
    "You are an expert isQ quantum software engineering assistant. "
    "Always write complete standalone runnable code."
)
CODE_ROW_TYPES = {"code_generation", "bug_fix"}
LEADING_COMMENT_RE = re.compile(r"(?s)^(?:\s*(?://[^\n]*\n|/\*.*?\*/\s*|\n))+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-jsonl", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--train-ratio", type=float, default=0.8)
    return parser.parse_args()


def clean_prompt(prompt: str) -> str:
    text = str(prompt or "").strip()
    if not text:
        return text
    for legacy_suffix in LEGACY_PROMPT_SUFFIXES:
        if text.lower().endswith(legacy_suffix.lower()):
            text = text[: -len(legacy_suffix)].rstrip()
    text = text.rstrip("。.?？!！").rstrip()
    if not text.endswith(PROMPT_SUFFIX):
        text = f"{text}{PROMPT_SUFFIX}"
    return text


def stable_key(row: dict[str, Any]) -> str:
    prompt = (
        row.get("messages", [{}, {}])[1].get("content", "")
        if isinstance(row.get("messages"), list) and len(row.get("messages")) > 1
        else ""
    )
    seed = f"{row.get('example_id', '')}\n{prompt}"
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_no}: row must be an object")
            messages = row.get("messages")
            if not isinstance(messages, list) or len(messages) < 3:
                raise ValueError(f"{path}:{line_no}: row missing chat messages")
            user = messages[1]
            if not isinstance(user, dict) or user.get("role") != "user":
                raise ValueError(f"{path}:{line_no}: malformed user message")
            user["content"] = clean_prompt(str(user.get("content") or ""))
            if not user["content"]:
                raise ValueError(f"{path}:{line_no}: empty cleaned prompt")
            row["messages"] = messages
            row.setdefault("metadata", {})
            row["metadata"]["prompt_suffix"] = PROMPT_SUFFIX
            row["metadata"]["prompt_cleaned"] = True
            rows.append(row)
    if not rows:
        raise ValueError(f"{path} has no rows")
    return rows


def is_full_code_answer(text: str) -> bool:
    stripped = str(text or "").lstrip()
    if not stripped:
        return False
    stripped = LEADING_COMMENT_RE.sub("", stripped).lstrip()
    return (
        stripped.startswith("import std;")
        or stripped.startswith("qbit ")
        or stripped.startswith("procedure ")
        or "procedure main()" in stripped.lower()
        or stripped.startswith("ctrl ")
        or stripped.startswith("H(")
        or stripped.startswith("X(")
    )


def split_rows(
    rows: list[dict[str, Any]], train_ratio: float
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not 0.5 < train_ratio < 1.0:
        raise ValueError("--train-ratio must be between 0.5 and 1.0")
    ordered = sorted(rows, key=stable_key)
    train_count = int(len(ordered) * train_ratio)
    train_count = min(max(train_count, 1), len(ordered) - 1)
    return ordered[:train_count], ordered[train_count:]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True, sort_keys=True) + "\n")


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    metadata = [
        row.get("metadata") if isinstance(row.get("metadata"), dict) else {} for row in rows
    ]
    return {
        "rows": len(rows),
        "categories": dict(sorted(Counter(str(item.get("category")) for item in metadata).items())),
        "task_types": dict(
            sorted(Counter(str(item.get("task_type")) for item in metadata).items())
        ),
        "answer_field_counts": dict(
            sorted(Counter(str(item.get("answer_field")) for item in metadata).items())
        ),
    }


def main() -> int:
    args = parse_args()
    rows = load_rows(args.input_jsonl)
    train_rows, test_rows = split_rows(rows, args.train_ratio)
    train_path = args.output_dir / "train_chatml.jsonl"
    test_path = args.output_dir / "test_chatml.jsonl"
    manifest_path = args.output_dir / "manifest.json"
    write_jsonl(train_path, train_rows)
    write_jsonl(test_path, test_rows)
    train_ids = {row["example_id"] for row in train_rows}
    test_ids = {row["example_id"] for row in test_rows}
    manifest = {
        "ok": True,
        "input": str(args.input_jsonl),
        "output_dir": str(args.output_dir),
        "train_file": str(train_path),
        "test_file": str(test_path),
        "total_rows": len(rows),
        "train_rows": len(train_rows),
        "test_rows": len(test_rows),
        "train_ratio": args.train_ratio,
        "test_ratio": round(1.0 - args.train_ratio, 6),
        "prompt_suffix": PROMPT_SUFFIX,
        "system_prompt": SYSTEM_PROMPT,
        "no_example_id_overlap": not bool(train_ids & test_ids),
        "all_prompts_cleaned": all(
            str(row["messages"][1]["content"]).endswith(PROMPT_SUFFIX) for row in rows
        ),
        "all_answers_full_code": all(
            is_full_code_answer(row["messages"][2]["content"]) for row in rows
        ),
        "train_summary": summarize(train_rows),
        "test_summary": summarize(test_rows),
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
