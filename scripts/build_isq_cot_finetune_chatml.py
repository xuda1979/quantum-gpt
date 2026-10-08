#!/usr/bin/env python3
"""Build a clean ChatML finetuning file from isq_train_cot.json."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

DEFAULT_INPUT = Path("isq_train_cot.json")
DEFAULT_OUTPUT = Path("data/generated/isq_train_cot_finetune_chatml.jsonl")
DEFAULT_MANIFEST = Path("data/generated/isq_train_cot_finetune_chatml.manifest.json")
SYSTEM_PROMPT = (
    "You are an expert isQ quantum software engineering assistant. "
    "Write complete standalone runnable code, keep prompts clean, and return practical code-first answers."
)
QUESTION_SUFFIX = ". Write the code using isQ language."
CODE_TASK_TYPES = {"code_generation", "bug_fix"}
PREFIX_RE = re.compile(
    r"^\s*(?:" r"question|q|prompt|task|problem|题目|问题|题目描述|问题描述" r")\s*[:：\-]?\s*",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-json", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-jsonl", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    return parser.parse_args()


def clean_prompt(prompt: str) -> str:
    text = str(prompt or "").strip()
    if not text:
        return text
    text = PREFIX_RE.sub("", text, count=1).strip()
    if not text:
        return text
    text = text.rstrip("。.?？!！").rstrip()
    if not text.endswith(QUESTION_SUFFIX):
        text = f"{text}{QUESTION_SUFFIX}"
    return text


def source_answer(row: dict[str, Any]) -> str:
    answer = str(row.get("reference_solution") or "").strip()
    return answer


def is_code_task(row: dict[str, Any]) -> bool:
    return str(row.get("task_type") or "") in CODE_TASK_TYPES


def convert_row(row: dict[str, Any]) -> dict[str, Any]:
    example_id = str(row.get("task_id") or f"isq_cot_{row.get('dataset_index', 0):06d}").strip()
    prompt = clean_prompt(row.get("prompt") or "")
    answer = source_answer(row)
    if not prompt:
        raise ValueError(f"{example_id}: empty prompt after cleaning")
    if not answer:
        raise ValueError(f"{example_id}: empty answer")
    metadata = {
        "task_id": row.get("task_id"),
        "dataset_index": row.get("dataset_index"),
        "task_type": row.get("task_type"),
        "difficulty": row.get("difficulty"),
        "category": row.get("category"),
        "concept_tags": row.get("concept_tags")
        if isinstance(row.get("concept_tags"), list)
        else [],
        "source": row.get("source"),
        "source_file": "isq_train_cot.json",
        "answer_field": "reference_solution",
        "prompt_cleaned": True,
        "answer_type": "code_only",
    }
    return {
        "format": "chat-sft-v1",
        "source_schema": "isq-train-cot-json",
        "example_id": f"isq_cot_{hashlib.sha256(example_id.encode('utf-8')).hexdigest()[:16]}",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": answer},
        ],
        "metadata": metadata,
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True, sort_keys=True) + "\n")


def main() -> int:
    args = parse_args()
    payload = json.loads(args.input_json.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"{args.input_json} must contain a JSON list")

    source_rows = [row for row in payload if isinstance(row, dict) and is_code_task(row)]
    rows = [convert_row(row) for row in source_rows]
    write_jsonl(args.output_jsonl, rows)
    manifest = {
        "ok": True,
        "input": str(args.input_json),
        "output": str(args.output_jsonl),
        "manifest_version": "isq-train-cot-finetune-v2",
        "source_rows": len(source_rows),
        "rows": len(rows),
        "prompt_suffix": QUESTION_SUFFIX,
        "all_prompts_cleaned": all(row["metadata"]["prompt_cleaned"] for row in rows),
        "no_prompt_starts_with_question": not any(
            str(row["messages"][1]["content"]).lstrip().lower().startswith("question")
            for row in rows
        ),
        "all_answers_full_code": all(
            str(row["messages"][2]["content"]).lstrip().startswith("import std;")
            or "procedure main()" in str(row["messages"][2]["content"]).lower()
            for row in rows
        ),
        "answer_field_counts": {
            "reference_solution": sum(
                1 for row in rows if row["metadata"]["answer_field"] == "reference_solution"
            ),
        },
        "answer_type_counts": {
            "code_only": sum(
                1 for row in rows if row["metadata"].get("answer_type") == "code_only"
            ),
        },
    }
    args.manifest.write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
