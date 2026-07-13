#!/usr/bin/env python3
"""Audit strict distillation ChatML data before expensive finetuning."""

from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path
from typing import Any

DEFAULT_INPUT = Path(
    "data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft_203_strict_english_runnable_v1/all_chatml.jsonl"
)
DEFAULT_REPORT = Path("reports/strict_distillation_203_dataset_audit.json")
DEFAULT_VALID_OUTPUT = Path(
    "data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft_203_strict_valid_subset_v1/all_chatml.jsonl"
)

CHINESE_RE = re.compile(r"[\u4e00-\u9fff]")
FENCE_RE = re.compile(r"```(?:[\w.+-]+)?\n(.*?)\n```", re.S)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-jsonl", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--valid-output", type=Path, default=DEFAULT_VALID_OUTPUT)
    parser.add_argument("--min-valid-rows", type=int, default=203)
    return parser.parse_args()


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_no}: row must be object")
            rows.append(row)
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def answer_code(answer: str) -> tuple[str | None, str | None]:
    match = FENCE_RE.fullmatch(answer.strip())
    if not match:
        return None, "answer must be exactly one fenced code block"
    return match.group(1), None


def audit_row(index: int, row: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    messages = row.get("messages")
    if not isinstance(messages, list) or len(messages) < 3:
        return ["missing ChatML messages"]
    user = str(messages[1].get("content") if isinstance(messages[1], dict) else "")
    answer = str(messages[2].get("content") if isinstance(messages[2], dict) else "")
    if CHINESE_RE.search(user):
        reasons.append("prompt contains Chinese")
    if re.search(r"\bquestion\b", user, re.I):
        reasons.append("prompt contains the word question")
    code, error = answer_code(answer)
    if error:
        reasons.append(error)
        return reasons
    assert code is not None
    if "Sanitized fallback" in code:
        reasons.append("answer is sanitized fallback, not real solution code")
    executable_lines = [
        ln for ln in code.splitlines() if ln.strip() and not ln.strip().startswith("#")
    ]
    if len(executable_lines) < 3:
        reasons.append("answer has fewer than three executable non-comment lines")
    if answer.strip().startswith("```python"):
        try:
            ast.parse(code)
        except SyntaxError as exc:
            reasons.append(f"python syntax error: {exc.msg} line {exc.lineno}")
    return reasons


def main() -> int:
    args = parse_args()
    rows = load_rows(args.input_jsonl)
    valid_rows: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []
    reason_counts: dict[str, int] = {}

    for index, row in enumerate(rows, start=1):
        reasons = audit_row(index, row)
        if reasons:
            invalid.append({"row": index, "example_id": row.get("example_id"), "reasons": reasons})
            for reason in reasons:
                reason_counts[reason] = reason_counts.get(reason, 0) + 1
        else:
            valid_rows.append(row)

    write_jsonl(args.valid_output, valid_rows)
    report = {
        "ok": len(valid_rows) >= args.min_valid_rows and not invalid,
        "input_jsonl": str(args.input_jsonl),
        "valid_output": str(args.valid_output),
        "rows": len(rows),
        "valid_rows": len(valid_rows),
        "invalid_rows": len(invalid),
        "min_valid_rows": args.min_valid_rows,
        "reason_counts": dict(sorted(reason_counts.items())),
        "invalid_examples": invalid[:50],
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
