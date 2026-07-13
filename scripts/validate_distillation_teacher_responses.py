#!/usr/bin/env python3
"""Quality-gate generated distillation teacher-response rows."""

from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path
from typing import Any

PYTHON_FENCE_RE = re.compile(r"```(?:python|py)\s*\n(.*?)```", re.IGNORECASE | re.DOTALL)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-jsonl", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--min-count", type=int, default=0)
    parser.add_argument("--max-errors", type=int, default=50)
    return parser.parse_args()


def iter_rows(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            yield line_no, json.loads(line)


def validate_python_fences(path: Path, line_no: int, example_id: str, response: str) -> list[str]:
    errors: list[str] = []
    for index, code in enumerate(PYTHON_FENCE_RE.findall(response), start=1):
        stripped = code.strip()
        if not stripped:
            errors.append(f"{path}:{line_no} {example_id}: empty python fence #{index}")
            continue
        try:
            ast.parse(stripped)
        except SyntaxError as exc:
            errors.append(
                f"{path}:{line_no} {example_id}: python fence #{index} syntax error: {exc.msg} line {exc.lineno}"
            )
    return errors


def validate_row(path: Path, line_no: int, row: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    example_id = row.get("example_id")
    if not isinstance(example_id, str) or not example_id:
        return [f"{path}:{line_no}: missing example_id"]

    instruction = row.get("instruction")
    response = row.get("response")
    metadata = row.get("metadata")
    if not isinstance(instruction, str) or len(instruction.strip()) < 40:
        errors.append(f"{path}:{line_no} {example_id}: instruction too short")
    if not isinstance(response, str) or len(response.strip()) < 120:
        errors.append(f"{path}:{line_no} {example_id}: response too short")
        return errors
    if "<think" in response.lower() or "reasoning_content" in response.lower():
        errors.append(f"{path}:{line_no} {example_id}: hidden-reasoning marker leaked")
    contract_leak_markers = ("must not ask for fabricated", "do not ask for fabricated")
    if any(marker in response.lower() for marker in contract_leak_markers):
        errors.append(f"{path}:{line_no} {example_id}: prompt-contract text leaked into response")
    if not isinstance(metadata, dict) or not metadata.get("seed_example_id"):
        errors.append(f"{path}:{line_no} {example_id}: missing metadata.seed_example_id")
    rationale_markers = (
        "rationale",
        "solution uses",
        "issue arises",
        "the issue",
        "bug diagnosis",
        "the bug",
        "the task requires",
        "student's code",
        "reasoning:",
        "initial failure",
        "simulation fails",
        "error occurs",
        "error arises",
        "we implement",
        "we define",
        "round-trip error",
        "root cause",
        "extraction failure",
        "implementation follows",
        "code fails",
        "supplied rag",
        "adapt-vqe algorithm",
        "ripple-carry adder",
        "gate adds",
        "initial attempt",
        "分析",
        "设计",
        "原因",
        "问题诊断",
        "由于",
        "实现",
        "通过",
        "逻辑",
        "方案",
        "原理",
        "解析",
        "说明",
        "步骤",
    )
    if not any(marker in response.lower() for marker in rationale_markers):
        errors.append(f"{path}:{line_no} {example_id}: missing concise rationale summary")
    errors.extend(validate_python_fences(path, line_no, example_id, response))
    return errors


def main() -> int:
    args = parse_args()
    total = 0
    errors: list[str] = []
    seen: set[str] = set()
    duplicates: list[str] = []

    for line_no, row in iter_rows(args.input_jsonl):
        total += 1
        if not isinstance(row, dict):
            errors.append(f"{args.input_jsonl}:{line_no}: row is not object")
            continue
        example_id = row.get("example_id")
        if isinstance(example_id, str):
            if example_id in seen:
                duplicates.append(example_id)
            seen.add(example_id)
        errors.extend(validate_row(args.input_jsonl, line_no, row))
        if len(errors) >= args.max_errors:
            break

    report = {
        "input_jsonl": str(args.input_jsonl.resolve()),
        "count": total,
        "min_count": args.min_count,
        "ok": total >= args.min_count and not duplicates and not errors,
        "checks": {
            "count_meets_min": total >= args.min_count,
            "no_duplicate_example_ids": not duplicates,
            "no_quality_errors": not errors,
        },
        "duplicate_example_ids": sorted(set(duplicates))[:50],
        "errors": errors[: args.max_errors],
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
