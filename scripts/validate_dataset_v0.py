#!/usr/bin/env python3
"""Validate JSONL datasets against the local dataset-v0 schema contract.

This validator enforces the minimal required fields described in
research/dataset-schema-v0.md (treated as a hard integration contract).

It is intentionally strict and CPU-first.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REQUIRED_COMMON_FIELDS = [
    "schema_version",
    "example_id",
    "domain",
    "category",
    "task_type",
    "source",
    "difficulty",
    "language",
    "framework",
    "tags",
    "instruction",
    "response",
    "artifacts",
    "metadata",
]

ALLOWED_DOMAINS = {"quantum", "software"}


def iter_jsonl_lines(path: Path):
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except Exception as e:  # noqa: BLE001
                raise ValueError(f"{path}:{line_no} invalid JSON: {e}") from e
            yield line_no, row


def validate_row(path: Path, line_no: int, row: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if not isinstance(row, dict):
        return [f"{path}:{line_no} row is not a JSON object"]

    for field in REQUIRED_COMMON_FIELDS:
        if field not in row:
            errors.append(f"{path}:{line_no} missing required field: {field}")

    if row.get("schema_version") != "dataset-v0":
        errors.append(f"{path}:{line_no} schema_version must be 'dataset-v0'")

    domain = row.get("domain")
    if domain not in ALLOWED_DOMAINS:
        errors.append(f"{path}:{line_no} domain must be one of {sorted(ALLOWED_DOMAINS)}")

    instruction = row.get("instruction")
    if not isinstance(instruction, str) or not instruction.strip():
        errors.append(f"{path}:{line_no} instruction must be a non-empty string")

    response = row.get("response")
    if not isinstance(response, str) or not response.strip():
        errors.append(f"{path}:{line_no} response must be a non-empty string")

    artifacts = row.get("artifacts")
    if not isinstance(artifacts, dict):
        errors.append(f"{path}:{line_no} artifacts must be a JSON object (dict)")

    metadata = row.get("metadata")
    if not isinstance(metadata, dict):
        errors.append(f"{path}:{line_no} metadata must be a JSON object (dict)")

    example_id = row.get("example_id")
    if not isinstance(example_id, str) or not example_id.strip():
        errors.append(f"{path}:{line_no} example_id must be a non-empty string")

    tags = row.get("tags")
    if not isinstance(tags, list) or any(not isinstance(t, str) for t in tags):
        errors.append(f"{path}:{line_no} tags must be a list of strings")

    framework = row.get("framework")
    if framework is not None and not isinstance(framework, str):
        errors.append(f"{path}:{line_no} framework must be null or a string")

    # uniqueness within file
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Validate JSONL dataset rows against dataset-v0 schema contract."
    )
    ap.add_argument("--input-jsonl", type=Path, required=True)
    ap.add_argument("--output", type=Path, default=None)
    ap.add_argument("--min-count", type=int, default=0)
    ap.add_argument("--max-errors", type=int, default=50)
    args = ap.parse_args()

    input_path: Path = args.input_jsonl
    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")

    seen_example_ids: set[str] = set()
    duplicate_example_ids: list[str] = []

    total_rows = 0
    validation_errors: list[str] = []

    for line_no, row in iter_jsonl_lines(input_path):
        total_rows += 1

        # parse-time minimal uniqueness tracking
        if (
            isinstance(row, dict)
            and isinstance(row.get("example_id"), str)
            and row["example_id"].strip()
        ):
            eid = row["example_id"]
            if eid in seen_example_ids:
                duplicate_example_ids.append(eid)
            else:
                seen_example_ids.add(eid)

        row_errors = validate_row(input_path, line_no, row)
        if row_errors:
            validation_errors.extend(row_errors)
            if len(validation_errors) >= args.max_errors:
                break

    checks: dict[str, Any] = {
        "count_meets_min": total_rows >= args.min_count,
        "no_duplicate_example_ids": len(duplicate_example_ids) == 0,
        "no_validation_errors": len(validation_errors) == 0,
    }

    report: dict[str, Any] = {
        "input_jsonl": str(input_path.resolve()),
        "count": total_rows,
        "min_count": args.min_count,
        "ok": False,
        "checks": checks,
        "duplicate_example_ids": sorted(set(duplicate_example_ids))[:50],
        "errors": validation_errors[: args.max_errors],
    }
    report["ok"] = all(bool(v) for v in checks.values())

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    else:
        print(json.dumps(report, indent=2))

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
