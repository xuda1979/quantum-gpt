#!/usr/bin/env python3
"""Convert chat-sft-v1 style JSONL rows into dataset-v0 JSONL rows.

Input rows (observed in this workspace) look like:
{
  "example_id": "...",
  "format": "chat-sft-v1",
  "source_schema": "template-large-v1" ,
  "messages": [ {"role":"system","content":"..."}, {"role":"user","content":"..."}, {"role":"assistant","content":"..."} ],
  "metadata": { ... , "domain": "quantum|software", "category", "task_type", "task_id", "prompt_family", ... }
}

Output rows follow research/dataset-schema-v0.md minimal contract:
- schema_version = dataset-v0
- example_id preserved
- instruction from user message content
- response from assistant message content
- artifacts default to {}
- metadata retains original metadata plus provenance
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def find_message_content(messages: list[dict[str, Any]], wanted_role: str) -> str | None:
    for m in messages:
        role = m.get("role")
        if role == wanted_role:
            content = m.get("content")
            if isinstance(content, str) and content.strip():
                return content
    return None


def convert_row(row: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(row, dict):
        raise ValueError("Row is not a JSON object")

    example_id = row.get("example_id")
    if not isinstance(example_id, str) or not example_id.strip():
        raise ValueError("Row missing non-empty example_id")

    messages = row.get("messages")
    if not isinstance(messages, list):
        raise ValueError("Row missing messages list")

    instruction = find_message_content(messages, "user")
    response = find_message_content(messages, "assistant")
    if instruction is None:
        raise ValueError("Row missing non-empty user message content")
    if response is None:
        raise ValueError("Row missing non-empty assistant message content")

    md_in = row.get("metadata")
    if not isinstance(md_in, dict):
        raise ValueError("Row missing metadata object")

    # Map dataset-v0 required fields
    out_md = dict(md_in)  # shallow copy

    # Preserve chat-specific provenance
    out_md["_source_format"] = row.get("format")
    out_md["_source_schema"] = row.get("source_schema")

    # dataset-v0 contract requires artifacts to be a JSON object
    artifacts: dict[str, Any] = {}

    out: dict[str, Any] = {
        "schema_version": "dataset-v0",
        "example_id": example_id,
        "domain": md_in.get("domain"),
        "category": md_in.get("category"),
        "task_type": md_in.get("task_type"),
        "source": md_in.get("source"),
        "difficulty": md_in.get("difficulty"),
        "language": md_in.get("language"),
        "framework": md_in.get("framework"),
        "tags": md_in.get("tags", []),
        "instruction": instruction,
        "response": response,
        "artifacts": artifacts,
        "metadata": out_md,
    }

    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Convert chat-sft-v1 JSONL to dataset-v0 JSONL")
    ap.add_argument("--input-jsonl", type=Path, required=True)
    ap.add_argument("--output-jsonl", type=Path, required=True)
    ap.add_argument("--require-format", type=str, default="chat-sft-v1")
    ap.add_argument("--skip-bad-rows", action="store_true")
    args = ap.parse_args()

    in_path: Path = args.input_jsonl
    out_path: Path = args.output_jsonl

    if not in_path.exists():
        raise SystemExit(f"Input not found: {in_path}")

    out_path.parent.mkdir(parents=True, exist_ok=True)

    total = 0
    kept = 0
    skipped = 0

    with in_path.open("r", encoding="utf-8") as fin, out_path.open("w", encoding="utf-8") as fout:
        for line_no, line in enumerate(fin, start=1):
            if not line.strip():
                continue
            total += 1
            row = json.loads(line)
            if args.require_format is not None:
                fmt = row.get("format")
                if fmt != args.require_format:
                    msg = f"{in_path}:{line_no} format={fmt!r} != {args.require_format!r}"
                    if args.skip_bad_rows:
                        skipped += 1
                        continue
                    raise ValueError(msg)
            try:
                out_row = convert_row(row)
            except Exception as e:  # noqa: BLE001
                if args.skip_bad_rows:
                    skipped += 1
                    continue
                raise ValueError(f"{in_path}:{line_no} conversion failed: {e}") from e

            fout.write(json.dumps(out_row, ensure_ascii=False) + "\n")
            kept += 1

    print(
        json.dumps(
            {
                "input": str(in_path.resolve()),
                "output": str(out_path.resolve()),
                "total_rows": total,
                "kept_rows": kept,
                "skipped_rows": skipped,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
