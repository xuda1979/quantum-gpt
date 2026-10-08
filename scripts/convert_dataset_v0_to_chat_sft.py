#!/usr/bin/env python3
"""Convert dataset-v0 instruction/response rows into chat-sft-v1 JSONL."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_SYSTEM_PROMPT = (
    "You are a careful quantum software engineering assistant. "
    "Use the user's task and any supplied context to produce correct, testable Python or precise repair guidance."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-jsonl", type=Path, required=True)
    parser.add_argument("--output-jsonl", type=Path, required=True)
    parser.add_argument("--system-prompt", default=DEFAULT_SYSTEM_PROMPT)
    parser.add_argument("--source-schema", default="dataset-v0")
    return parser.parse_args()


def convert_row(row: dict[str, Any], *, system_prompt: str, source_schema: str) -> dict[str, Any]:
    example_id = row.get("example_id") or row.get("id")
    instruction = row.get("instruction")
    response = row.get("response") or row.get("output")
    metadata = row.get("metadata")
    if not isinstance(example_id, str) or not example_id.strip():
        raise ValueError("row missing example_id")
    if not isinstance(instruction, str) or not instruction.strip():
        raise ValueError(f"{example_id}: row missing instruction")
    if not isinstance(response, str) or not response.strip():
        raise ValueError(f"{example_id}: row missing response")
    if metadata is None:
        metadata = {}
    if not isinstance(metadata, dict):
        raise ValueError(f"{example_id}: row metadata must be an object when present")

    out_metadata = dict(metadata)
    for key in (
        "domain",
        "category",
        "task_type",
        "difficulty",
        "language",
        "framework",
        "tags",
        "source",
    ):
        out_metadata.setdefault(key, row.get(key))
    out_metadata["_source_schema"] = source_schema

    return {
        "format": "chat-sft-v1",
        "source_schema": source_schema,
        "example_id": example_id,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": instruction.strip()},
            {"role": "assistant", "content": response.strip()},
        ],
        "metadata": out_metadata,
    }


def main() -> int:
    args = parse_args()
    args.output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    with (
        args.input_jsonl.open("r", encoding="utf-8") as fin,
        args.output_jsonl.open("w", encoding="utf-8") as fout,
    ):
        for line_no, line in enumerate(fin, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"{args.input_jsonl}:{line_no}: row must be a JSON object")
            converted = convert_row(
                row, system_prompt=args.system_prompt, source_schema=args.source_schema
            )
            fout.write(json.dumps(converted, ensure_ascii=True, sort_keys=True) + "\n")
            total += 1
    print(
        json.dumps(
            {
                "input": str(args.input_jsonl.resolve()),
                "output": str(args.output_jsonl.resolve()),
                "rows": total,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
