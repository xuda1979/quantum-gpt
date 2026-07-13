#!/usr/bin/env python3
"""Audit ASI2 distillation seed/generated dataset diversity and packaging."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

DEFAULT_SEED = Path("data/seed/quantum_distillation_seed_questions_asi2_v1.jsonl")
DEFAULT_GENERATED = Path(
    "data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality.jsonl"
)
DEFAULT_CHATML = Path(
    "data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_chatml.jsonl"
)
DEFAULT_SPLIT_DIR = Path(
    "data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft"
)
DEFAULT_REPORT = Path("reports/quantum_distillation_teacher_responses_asi2_v1_diversity_audit.json")

REQUIRED_TASK_TYPES = {"implementation", "repair", "agentic_trajectory", "optimization"}
REQUIRED_CATEGORIES = {
    "algorithm_implementation",
    "library_api_grounding",
    "hardware_compilation",
    "noise_and_mitigation",
    "quantum_engineering",
}
REQUIRED_FRAMEWORKS = {"qiskit", "cirq", "pennylane", "braket", "cuda-quantum", "pyzx"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed-jsonl", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--generated-jsonl", type=Path, default=DEFAULT_GENERATED)
    parser.add_argument("--chatml-jsonl", type=Path, default=DEFAULT_CHATML)
    parser.add_argument("--split-dir", type=Path, default=DEFAULT_SPLIT_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--min-seed-rows", type=int, default=400)
    parser.add_argument("--min-generated-rows", type=int, default=200)
    parser.add_argument("--min-source-docs", type=int, default=100)
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
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


def metadata(row: dict[str, Any]) -> dict[str, Any]:
    value = row.get("metadata")
    return value if isinstance(value, dict) else {}


def row_value(row: dict[str, Any], key: str) -> Any:
    return row.get(key, metadata(row).get(key))


def counter(rows: list[dict[str, Any]], key: str) -> Counter[str]:
    return Counter(str(row_value(row, key)) for row in rows)


def source_docs(rows: list[dict[str, Any]]) -> set[str]:
    return {
        str(metadata(row).get("source_doc_sha256"))
        for row in rows
        if metadata(row).get("source_doc_sha256")
    }


def duplicate_ids(rows: list[dict[str, Any]]) -> list[str]:
    counts = Counter(str(row.get("example_id")) for row in rows)
    return sorted(example_id for example_id, count in counts.items() if count > 1)


def chinese_ratio(text: str) -> float:
    visible = re.findall(r"\S", text)
    if not visible:
        return 0.0
    chinese = re.findall(r"[\u4e00-\u9fff]", text)
    return len(chinese) / len(visible)


def generated_language_errors(rows: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for row in rows:
        example_id = str(row.get("example_id"))
        instruction = str(row.get("instruction", ""))
        response = str(row.get("response", ""))
        if chinese_ratio(instruction) > 0.02:
            errors.append(f"{example_id}: instruction contains non-English Chinese text")
        if chinese_ratio(response) > 0.02:
            errors.append(f"{example_id}: response contains non-English Chinese text")
    return errors


def split_ids(path: Path) -> set[str]:
    return {str(row.get("example_id")) for row in load_jsonl(path)}


def main() -> int:
    args = parse_args()
    seed_rows = load_jsonl(args.seed_jsonl)
    generated_rows = load_jsonl(args.generated_jsonl)
    chatml_rows = load_jsonl(args.chatml_jsonl)
    train_ids = split_ids(args.split_dir / "train_chatml.jsonl")
    eval_ids = split_ids(args.split_dir / "eval_chatml.jsonl")

    generated_ids = {str(row.get("example_id")) for row in generated_rows}
    chatml_ids = {str(row.get("example_id")) for row in chatml_rows}
    split_total_ids = train_ids | eval_ids

    seed_task_types = set(counter(seed_rows, "task_type"))
    generated_task_types = set(counter(generated_rows, "task_type"))
    seed_categories = set(counter(seed_rows, "category"))
    generated_categories = set(counter(generated_rows, "category"))
    seed_frameworks = set(counter(seed_rows, "framework")) - {"None"}
    generated_frameworks = set(counter(generated_rows, "framework")) - {"None"}

    errors: list[str] = []
    if len(seed_rows) < args.min_seed_rows:
        errors.append(f"seed row count too low: {len(seed_rows)} < {args.min_seed_rows}")
    if len(generated_rows) < args.min_generated_rows:
        errors.append(
            f"generated row count too low: {len(generated_rows)} < {args.min_generated_rows}"
        )
    if len(source_docs(seed_rows)) < args.min_source_docs:
        errors.append(
            f"seed source doc count too low: {len(source_docs(seed_rows))} < {args.min_source_docs}"
        )
    if duplicate_ids(seed_rows):
        errors.append(f"duplicate seed ids: {duplicate_ids(seed_rows)[:10]}")
    if duplicate_ids(generated_rows):
        errors.append(f"duplicate generated ids: {duplicate_ids(generated_rows)[:10]}")
    missing_seed_tasks = REQUIRED_TASK_TYPES - seed_task_types
    if missing_seed_tasks:
        errors.append(f"seed missing task types: {sorted(missing_seed_tasks)}")
    missing_generated_tasks = REQUIRED_TASK_TYPES - generated_task_types
    if missing_generated_tasks:
        errors.append(f"generated missing task types: {sorted(missing_generated_tasks)}")
    if REQUIRED_CATEGORIES - seed_categories:
        errors.append(f"seed missing categories: {sorted(REQUIRED_CATEGORIES - seed_categories)}")
    if REQUIRED_CATEGORIES - generated_categories:
        errors.append(
            f"generated missing categories: {sorted(REQUIRED_CATEGORIES - generated_categories)}"
        )
    if REQUIRED_FRAMEWORKS - seed_frameworks:
        errors.append(f"seed missing frameworks: {sorted(REQUIRED_FRAMEWORKS - seed_frameworks)}")
    if REQUIRED_FRAMEWORKS - generated_frameworks:
        errors.append(
            f"generated missing frameworks: {sorted(REQUIRED_FRAMEWORKS - generated_frameworks)}"
        )
    if chatml_ids != generated_ids:
        errors.append(
            "chatml ids do not match accepted generated ids: "
            f"missing={len(generated_ids - chatml_ids)} extra={len(chatml_ids - generated_ids)}"
        )
    if split_total_ids != chatml_ids:
        errors.append(
            "split ids do not match chatml ids: "
            f"missing={len(chatml_ids - split_total_ids)} extra={len(split_total_ids - chatml_ids)}"
        )
    if train_ids & eval_ids:
        errors.append(f"train/eval overlap: {len(train_ids & eval_ids)} ids")
    errors.extend(generated_language_errors(generated_rows)[:20])

    report = {
        "ok": not errors,
        "seed_rows": len(seed_rows),
        "generated_rows": len(generated_rows),
        "chatml_rows": len(chatml_rows),
        "train_rows": len(train_ids),
        "eval_rows": len(eval_ids),
        "seed_source_doc_count": len(source_docs(seed_rows)),
        "generated_source_doc_count": len(source_docs(generated_rows)),
        "seed_task_types": dict(sorted(counter(seed_rows, "task_type").items())),
        "generated_task_types": dict(sorted(counter(generated_rows, "task_type").items())),
        "seed_categories": dict(sorted(counter(seed_rows, "category").items())),
        "generated_categories": dict(sorted(counter(generated_rows, "category").items())),
        "seed_frameworks": dict(sorted(counter(seed_rows, "framework").items())),
        "generated_frameworks": dict(sorted(counter(generated_rows, "framework").items())),
        "errors": errors,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, ensure_ascii=True, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
