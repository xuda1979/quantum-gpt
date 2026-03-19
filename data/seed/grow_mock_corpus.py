#!/usr/bin/env python3
"""Expand the tiny seed corpus into a larger deterministic mock dataset for split/audit stress tests."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "data" / "seed" / "train-chat.jsonl"
DEFAULT_OUTPUT = ROOT / "data" / "seed" / "mock-train-chat.jsonl"
SUPPORTED_SCHEMAS = {"dataset-v0", "chat-sft-v1"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Source JSONL corpus to expand")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Destination JSONL corpus")
    parser.add_argument(
        "--copies-per-example",
        type=int,
        default=4,
        help="Number of deterministic variants to emit per source example (must be >= 1)",
    )
    parser.add_argument(
        "--variant-tag",
        default="mock-expanded-v1",
        help="Metadata tag recorded on generated variants for provenance",
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



def record_metadata(record: dict[str, Any]) -> dict[str, Any]:
    metadata = record.get("metadata")
    return metadata if isinstance(metadata, dict) else {}



def validate_input(records: list[dict[str, Any]]) -> str:
    example_ids = set()
    schema = None
    for record in records:
        example_id = record.get("example_id")
        if not isinstance(example_id, str) or not example_id.strip():
            raise ValueError("Each record must have a non-empty example_id")
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



def clone_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cloned = []
    for message in messages:
        if not isinstance(message, dict):
            raise ValueError("Each message must be an object")
        cloned.append(dict(message))
    return cloned



def append_variant_note(text: str, variant_index: int) -> str:
    note = f"\n\n# Variant note\nThis deterministic mock example is variant {variant_index}."
    return text.rstrip() + note + "\n"



def make_variant(record: dict[str, Any], variant_index: int, variant_tag: str, schema: str) -> dict[str, Any]:
    original_id = record["example_id"]
    variant_id = f"{original_id}__variant_{variant_index:02d}"
    metadata = dict(record_metadata(record))
    metadata.update(
        {
            "source_example_id": original_id,
            "mock_variant_index": variant_index,
            "mock_variant_tag": variant_tag,
        }
    )

    variant = dict(record)
    variant["example_id"] = variant_id
    variant["metadata"] = metadata

    if schema == "dataset-v0":
        artifacts = record.get("artifacts")
        if not isinstance(artifacts, dict):
            raise ValueError(f"dataset-v0 record {original_id} must contain object-shaped artifacts")
        variant["artifacts"] = dict(artifacts)
        variant["instruction"] = append_variant_note(str(record["instruction"]), variant_index)
        variant["response"] = append_variant_note(str(record["response"]), variant_index)
        return variant

    if schema == "chat-sft-v1":
        messages = record.get("messages")
        if not isinstance(messages, list) or not messages:
            raise ValueError(f"chat-sft-v1 record {original_id} must contain a non-empty messages list")
        cloned_messages = clone_messages(messages)
        assistant_seen = False
        for message in cloned_messages:
            role = message.get("role")
            if role == "user":
                message["content"] = append_variant_note(str(message.get("content", "")), variant_index)
            elif role == "assistant":
                message["content"] = append_variant_note(str(message.get("content", "")), variant_index)
                assistant_seen = True
        if not assistant_seen:
            raise ValueError(f"chat-sft-v1 record {original_id} must include an assistant message")
        variant["messages"] = cloned_messages
        return variant

    raise ValueError(f"Unsupported schema: {schema}")



def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    domains = Counter()
    task_types = Counter()
    source_examples = defaultdict(int)
    for record in records:
        metadata = record_metadata(record)
        domains[str(metadata.get("domain", record.get("domain", "unknown")))] += 1
        task_types[str(metadata.get("task_type", record.get("task_type", "unknown")))] += 1
        source_examples[str(metadata.get("source_example_id", record["example_id"]))] += 1
    return {
        "count": len(records),
        "domains": dict(sorted(domains.items())),
        "task_types": dict(sorted(task_types.items())),
        "source_example_variant_counts": dict(sorted(source_examples.items())),
    }



def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")



def main() -> None:
    args = parse_args()
    if args.copies_per_example < 1:
        raise ValueError("--copies-per-example must be >= 1")

    records = load_jsonl(args.input)
    schema = validate_input(records)

    expanded = []
    for record in sorted(records, key=lambda item: item["example_id"]):
        for variant_index in range(1, args.copies_per_example + 1):
            expanded.append(make_variant(record, variant_index, args.variant_tag, schema))

    example_ids = [record["example_id"] for record in expanded]
    if len(example_ids) != len(set(example_ids)):
        raise ValueError("Expanded corpus contains duplicate example_id values")

    write_jsonl(args.output, expanded)
    print(
        json.dumps(
            {
                "status": "ok",
                "source_schema": schema,
                "input_path": str(args.input.relative_to(ROOT) if args.input.is_relative_to(ROOT) else args.input),
                "output_path": str(args.output.relative_to(ROOT) if args.output.is_relative_to(ROOT) else args.output),
                "copies_per_example": args.copies_per_example,
                "variant_tag": args.variant_tag,
                "summary": summarize(expanded),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
