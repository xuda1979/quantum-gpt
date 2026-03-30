#!/usr/bin/env python3
"""Build a larger quantum-skewed chat-SFT dataset from an existing JSONL corpus."""

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
        "--out-dir",
        type=Path,
        default=Path("data/generated/omnicoder-quantum-focus-v1"),
        help="Destination directory for train/eval splits and manifest.",
    )
    parser.add_argument(
        "--software-fraction",
        type=float,
        default=0.25,
        help="Relative software count vs kept quantum count. 0.25 means keep software up to 25%% of quantum rows.",
    )
    parser.add_argument(
        "--train-ratio",
        type=float,
        default=0.85,
        help="Deterministic train split ratio.",
    )
    parser.add_argument(
        "--seed-tag",
        default="omnicoder-quantum-focus-v1",
        help="Stable tag mixed into hashes for deterministic selection and splitting.",
    )
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def stable_hex(example_id: str, seed_tag: str) -> str:
    return hashlib.sha256(f"{seed_tag}:{example_id}".encode("utf-8")).hexdigest()


def stable_bucket(example_id: str, seed_tag: str) -> float:
    digest = stable_hex(example_id, seed_tag)
    return int(digest[:16], 16) / float(16**16 - 1)


def pick_rows(rows: list[dict[str, Any]], software_fraction: float, seed_tag: str) -> list[dict[str, Any]]:
    quantum_rows = [row for row in rows if row.get("metadata", {}).get("domain") == "quantum"]
    software_rows = [row for row in rows if row.get("metadata", {}).get("domain") == "software"]
    target_software = min(len(software_rows), int(len(quantum_rows) * software_fraction))

    software_rows = sorted(
        software_rows,
        key=lambda row: (stable_hex(row["example_id"], f"{seed_tag}:software"), row["example_id"]),
    )[:target_software]

    selected = quantum_rows + software_rows
    selected.sort(key=lambda row: (stable_hex(row["example_id"], f"{seed_tag}:all"), row["example_id"]))
    return selected


def split_rows(rows: list[dict[str, Any]], train_ratio: float, seed_tag: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    train_rows: list[dict[str, Any]] = []
    eval_rows: list[dict[str, Any]] = []
    for row in rows:
        bucket = stable_bucket(row["example_id"], f"{seed_tag}:split")
        target = train_rows if bucket < train_ratio else eval_rows
        target.append(row)
    return train_rows, eval_rows


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
        "top_tasks": by_task.most_common(12),
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    args = parse_args()
    if not 0.0 <= args.software_fraction <= 1.0:
        raise SystemExit("--software-fraction must be between 0 and 1")
    if not 0.0 < args.train_ratio < 1.0:
        raise SystemExit("--train-ratio must be between 0 and 1")

    rows = load_jsonl(args.input)
    selected = pick_rows(rows, software_fraction=args.software_fraction, seed_tag=args.seed_tag)
    train_rows, eval_rows = split_rows(selected, train_ratio=args.train_ratio, seed_tag=args.seed_tag)

    train_path = args.out_dir / "train.jsonl"
    eval_path = args.out_dir / "eval.jsonl"
    write_jsonl(train_path, train_rows)
    write_jsonl(eval_path, eval_rows)

    manifest = {
        "manifest_version": "omnicoder-quantum-focus-v1",
        "input": str(args.input),
        "out_dir": str(args.out_dir),
        "software_fraction": args.software_fraction,
        "train_ratio": args.train_ratio,
        "seed_tag": args.seed_tag,
        "selected_summary": summarize(selected),
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
