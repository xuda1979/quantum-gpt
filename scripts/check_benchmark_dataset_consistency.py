#!/usr/bin/env python3
"""Check benchmark/task/dataset consistency for local eval and holdout contracts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TASKS_ROOT = ROOT / "evals" / "tasks"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark-file", type=Path, required=True)
    parser.add_argument("--tasks-root", type=Path, default=DEFAULT_TASKS_ROOT)
    parser.add_argument("--manifest", type=Path, default=None)
    parser.add_argument("--require-all-benchmark-tasks-in-manifest-eval", action="store_true")
    parser.add_argument("--require-benchmark-tasks-absent-from-manifest-train", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_benchmark_task_ids(path: Path) -> list[str]:
    task_ids: list[str] = []
    seen: set[str] = set()
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line in seen:
            continue
        seen.add(line)
        task_ids.append(line)
    if not task_ids:
        raise ValueError(f"No benchmark task ids found in {path}")
    return task_ids


def discover_task_ids(tasks_root: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for task_json in sorted(tasks_root.glob("*/*/task.json")):
        payload = load_json(task_json)
        task_id = payload.get("id")
        if isinstance(task_id, str) and task_id:
            mapping[task_id] = str(task_json.parent.resolve())
    return mapping


def _task_ids_from_manifest_summary(summary: dict[str, Any] | None) -> set[str]:
    if not isinstance(summary, dict):
        return set()
    tasks = summary.get("tasks")
    if not isinstance(tasks, dict):
        return set()
    return {str(task_id) for task_id in tasks}


def _task_ids_from_dataset_contract(contract: dict[str, Any] | None, key: str) -> set[str]:
    if not isinstance(contract, dict):
        return set()
    payload = contract.get(key)
    if not isinstance(payload, list):
        return set()
    return {str(item) for item in payload if isinstance(item, str) and item}


def summarize_manifest(manifest: dict[str, Any]) -> dict[str, set[str]]:
    dataset_contract = manifest.get("dataset_contract")
    train_ids = _task_ids_from_dataset_contract(dataset_contract, "train_task_ids")
    eval_ids = _task_ids_from_dataset_contract(dataset_contract, "eval_task_ids")
    source_ids = _task_ids_from_dataset_contract(dataset_contract, "source_task_ids")

    if not train_ids:
        train_ids = _task_ids_from_manifest_summary(manifest.get("train_summary"))
    if not eval_ids:
        eval_ids = _task_ids_from_manifest_summary(manifest.get("eval_summary"))
    if not source_ids:
        source_ids = train_ids | eval_ids

    return {
        "train_task_ids": train_ids,
        "eval_task_ids": eval_ids,
        "source_task_ids": source_ids,
    }


def main() -> int:
    args = parse_args()

    benchmark_task_ids = load_benchmark_task_ids(args.benchmark_file)
    known_tasks = discover_task_ids(args.tasks_root)
    missing_task_ids = [task_id for task_id in benchmark_task_ids if task_id not in known_tasks]

    report: dict[str, Any] = {
        "benchmark_file": str(args.benchmark_file.resolve()),
        "tasks_root": str(args.tasks_root.resolve()),
        "manifest": str(args.manifest.resolve()) if args.manifest else None,
        "benchmark_task_ids": benchmark_task_ids,
        "checks": {
            "all_benchmark_tasks_resolve_to_task_dirs": not missing_task_ids,
        },
        "missing_task_ids": missing_task_ids,
        "resolved_task_dirs": {
            task_id: known_tasks[task_id]
            for task_id in benchmark_task_ids
            if task_id in known_tasks
        },
    }

    manifest_task_summary: dict[str, set[str]] | None = None
    if args.manifest is not None:
        manifest = load_json(args.manifest)
        manifest_task_summary = summarize_manifest(manifest)
        benchmark_set = set(benchmark_task_ids)
        eval_overlap = sorted(benchmark_set & manifest_task_summary["eval_task_ids"])
        train_overlap = sorted(benchmark_set & manifest_task_summary["train_task_ids"])
        report["manifest_summary"] = {
            "train_task_ids": sorted(manifest_task_summary["train_task_ids"]),
            "eval_task_ids": sorted(manifest_task_summary["eval_task_ids"]),
            "source_task_ids": sorted(manifest_task_summary["source_task_ids"]),
        }
        report["manifest_overlap"] = {
            "benchmark_vs_eval_task_ids": eval_overlap,
            "benchmark_vs_train_task_ids": train_overlap,
        }

        if args.require_all_benchmark_tasks_in_manifest_eval:
            report["checks"]["all_benchmark_tasks_present_in_manifest_eval"] = (
                set(eval_overlap) == benchmark_set
            )
        if args.require_benchmark_tasks_absent_from_manifest_train:
            report["checks"]["benchmark_tasks_absent_from_manifest_train"] = not train_overlap

    report["ok"] = all(bool(value) for value in report["checks"].values())

    rendered = json.dumps(report, indent=2) + "\n"
    if args.output is not None:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
