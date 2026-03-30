#!/usr/bin/env python3
"""Build a deterministic chat-SFT train/eval split from a task-id subset."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/generated/template-v2.jsonl"),
        help="Source chat-SFT JSONL corpus.",
    )
    parser.add_argument(
        "--task-id-file",
        type=Path,
        required=True,
        help="Text file with one task id per line; '#' comments are ignored.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        required=True,
        help="Destination directory for train/eval splits and manifest.",
    )
    parser.add_argument(
        "--train-ratio",
        type=float,
        default=0.85,
        help="Deterministic train split ratio.",
    )
    parser.add_argument(
        "--seed-tag",
        default="task-subset-v1",
        help="Stable tag mixed into hashes for deterministic splitting.",
    )
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_task_ids(path: Path) -> list[str]:
    task_ids = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        task_ids.append(line)
    if not task_ids:
        raise SystemExit(f"No task ids found in {path}")
    return task_ids


def stable_bucket(example_id: str, seed_tag: str) -> float:
    digest = hashlib.sha256(f"{seed_tag}:{example_id}".encode("utf-8")).hexdigest()
    return int(digest[:16], 16) / float(16**16 - 1)


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_domain = Counter()
    by_task = Counter()
    for row in rows:
        metadata = row.get("metadata", {})
        by_domain[metadata.get("domain", "unknown")] += 1
        by_task[metadata.get("task_id", "unknown")] += 1
    return {
        "count": len(rows),
        "domains": dict(sorted(by_domain.items())),
        "tasks": dict(sorted(by_task.items())),
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    args = parse_args()
    if not 0.0 < args.train_ratio < 1.0:
        raise SystemExit("--train-ratio must be between 0 and 1")

    task_ids = set(load_task_ids(args.task_id_file))
    rows = [row for row in load_jsonl(args.input) if row.get("metadata", {}).get("task_id") in task_ids]
    if not rows:
        raise SystemExit("No rows matched the requested task subset")

    train_rows: list[dict[str, Any]] = []
    eval_rows: list[dict[str, Any]] = []
    for row in rows:
        bucket = stable_bucket(row["example_id"], f"{args.seed_tag}:split")
        target = train_rows if bucket < args.train_ratio else eval_rows
        target.append(row)

    if not train_rows or not eval_rows:
        raise SystemExit("Deterministic split produced an empty train or eval split; adjust seed or train ratio")

    write_jsonl(args.out_dir / "train.jsonl", train_rows)
    write_jsonl(args.out_dir / "eval.jsonl", eval_rows)

    manifest = {
        "manifest_version": "task-subset-v1",
        "input": str(args.input),
        "task_id_file": str(args.task_id_file),
        "out_dir": str(args.out_dir),
        "train_ratio": args.train_ratio,
        "seed_tag": args.seed_tag,
        "selected_summary": summarize(rows),
        "train_summary": summarize(train_rows),
        "eval_summary": summarize(eval_rows),
    }
    (args.out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
