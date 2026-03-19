#!/usr/bin/env python3
"""Recommend a split policy for seed corpora based on size and composition."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "data" / "seed" / "train-chat.jsonl"
SUPPORTED_SCHEMAS = {"dataset-v0", "chat-sft-v1"}

from evals.runner.recommend_split_policy import recommend_policy, summarize_groups


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Input JSONL corpus to inspect")
    parser.add_argument(
        "--emit-flags",
        action="store_true",
        help="Print a shell-friendly suggested flag string in addition to the JSON report",
    )
    return parser.parse_args()



def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number} of {path}: {exc}") from exc
    if not records:
        raise ValueError(f"No records found in {path}")
    return records



def detect_schema(record: dict[str, Any]) -> str:
    if record.get("schema_version") == "dataset-v0":
        return "dataset-v0"
    if record.get("format") == "chat-sft-v1":
        return "chat-sft-v1"
    raise ValueError(f"Unsupported record shape for example_id={record.get('example_id')!r}")



def validate_records(records: list[dict[str, Any]]) -> str:
    schema = None
    example_ids = set()
    for record in records:
        example_id = record.get("example_id")
        if not isinstance(example_id, str) or not example_id.strip():
            raise ValueError("Each record must contain a non-empty example_id")
        if example_id in example_ids:
            raise ValueError(f"Duplicate example_id in input: {example_id}")
        example_ids.add(example_id)

        record_schema = detect_schema(record)
        if record_schema not in SUPPORTED_SCHEMAS:
            raise ValueError(f"Unsupported schema: {record_schema}")
        if schema is None:
            schema = record_schema
        elif schema != record_schema:
            raise ValueError("Mixed input schemas are not supported")
    assert schema is not None
    return schema



def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(path)



def main() -> None:
    args = parse_args()
    input_path = args.input.resolve()
    records = load_jsonl(input_path)
    schema = validate_records(records)
    recommendation = recommend_policy(records)

    report = {
        "status": "ok",
        "input_path": display_path(input_path),
        "source_schema": schema,
        "total_examples": len(records),
        "group_summary": {
            "domains": summarize_groups(records, "domain"),
            "task_types": summarize_groups(records, "task_type"),
        },
        "recommended_policy": recommendation["policy"],
        "recommended_flags": recommendation["flags"],
        "reason": recommendation["reason"],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.emit_flags:
        print("FLAGS=" + " ".join(recommendation["flags"]))


if __name__ == "__main__":
    main()
