#!/usr/bin/env python3
"""Create deterministic train/val/test splits for dataset-v0 or chat-SFT JSONL files."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_INPUT = ROOT / "data" / "seed" / "train-chat.jsonl"
DEFAULT_OUTPUT_DIR = ROOT / "data" / "seed" / "splits"
SUPPORTED_SOURCE_SCHEMAS = {"dataset-v0", "chat-sft-v1"}
SPLIT_NAMES = ("train", "val", "test")

from evals.runner.recommend_split_policy import recommend_policy


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Input JSONL file to split")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory for split artifacts")
    parser.add_argument("--train-ratio", type=float, default=0.67, help="Fraction assigned to train")
    parser.add_argument("--val-ratio", type=float, default=0.17, help="Fraction assigned to validation")
    parser.add_argument("--test-ratio", type=float, default=0.16, help="Fraction assigned to test")
    parser.add_argument("--seed", default="seed-splits-v1", help="Deterministic split seed")
    parser.add_argument(
        "--balance-key",
        choices=["domain", "task_type"],
        default=None,
        help="Optionally balance small-corpus placement within each domain or task_type group.",
    )
    parser.add_argument(
        "--min-per-balance-group",
        type=int,
        default=0,
        help="For balanced placement, target up to this many examples per split inside each balance group when feasible.",
    )
    parser.add_argument(
        "--auto-policy",
        action="store_true",
        help="Automatically choose a split policy from corpus composition unless explicit balancing flags are provided.",
    )
    return parser.parse_args()



def load_jsonl(path: Path) -> list[dict]:
    records = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number} of {path}: {exc}") from exc
            records.append(record)
    if not records:
        raise ValueError(f"No records found in {path}")
    return records



def detect_schema(record: dict) -> str:
    if record.get("schema_version") == "dataset-v0":
        return "dataset-v0"
    if record.get("format") == "chat-sft-v1":
        return "chat-sft-v1"
    raise ValueError(f"Unsupported record shape for example_id={record.get('example_id')!r}")



def validate_records(records: list[dict]) -> str:
    example_ids = set()
    schema = None
    for record in records:
        example_id = record.get("example_id")
        if not isinstance(example_id, str) or not example_id.strip():
            raise ValueError("Each record must contain a non-empty example_id")
        if example_id in example_ids:
            raise ValueError(f"Duplicate example_id in input: {example_id}")
        example_ids.add(example_id)

        record_schema = detect_schema(record)
        if record_schema not in SUPPORTED_SOURCE_SCHEMAS:
            raise ValueError(f"Unsupported schema: {record_schema}")
        if schema is None:
            schema = record_schema
        elif schema != record_schema:
            raise ValueError("Mixed input schemas are not supported within one split run")
    assert schema is not None
    return schema



def hash_bucket(seed: str, example_id: str) -> float:
    digest = hashlib.sha256(f"{seed}:{example_id}".encode("utf-8")).hexdigest()
    return int(digest[:16], 16) / float(0xFFFFFFFFFFFFFFFF)



def assign_split(example_id: str, seed: str, train_ratio: float, val_ratio: float) -> str:
    bucket = hash_bucket(seed, example_id)
    if bucket < train_ratio:
        return "train"
    if bucket < train_ratio + val_ratio:
        return "val"
    return "test"



def ensure_ratios(train_ratio: float, val_ratio: float, test_ratio: float) -> None:
    total = train_ratio + val_ratio + test_ratio
    if min(train_ratio, val_ratio, test_ratio) <= 0:
        raise ValueError("All split ratios must be positive")
    if abs(total - 1.0) > 1e-9:
        raise ValueError(f"Split ratios must sum to 1.0, got {total}")



def write_jsonl(path: Path, records: Iterable[dict]) -> int:
    count = 0
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
    return count



def record_metadata(record: dict) -> dict:
    metadata = record.get("metadata")
    return metadata if isinstance(metadata, dict) else {}



def get_balance_value(record: dict, balance_key: str | None) -> str:
    metadata = record_metadata(record)
    if balance_key is None:
        return "__all__"
    value = record.get(balance_key, metadata.get(balance_key, "unknown"))
    return str(value)



def summarize(records: list[dict]) -> dict:
    domains: dict[str, int] = {}
    task_types: dict[str, int] = {}
    categories: dict[str, int] = {}
    difficulties: dict[str, int] = {}
    for record in records:
        metadata = record_metadata(record)
        domain = record.get("domain", metadata.get("domain", "unknown"))
        task_type = record.get("task_type", metadata.get("task_type", "unknown"))
        category = record.get("category", metadata.get("category", "unknown"))
        difficulty = record.get("difficulty", metadata.get("difficulty", "unknown"))
        domains[domain] = domains.get(domain, 0) + 1
        task_types[task_type] = task_types.get(task_type, 0) + 1
        categories[category] = categories.get(category, 0) + 1
        difficulties[difficulty] = difficulties.get(difficulty, 0) + 1
    return {
        "count": len(records),
        "domains": domains,
        "task_types": task_types,
        "categories": categories,
        "difficulties": difficulties,
    }



def build_ratio_targets(total: int, ratios: dict[str, float]) -> dict[str, int]:
    raw = {split: ratios[split] * total for split in SPLIT_NAMES}
    base = {split: int(raw[split]) for split in SPLIT_NAMES}
    remainder = total - sum(base.values())
    ranked = sorted(SPLIT_NAMES, key=lambda split: (-(raw[split] - base[split]), split))
    for split in ranked[:remainder]:
        base[split] += 1
    return base



def pick_split(
    record: dict,
    candidate_splits: list[str],
    seed: str,
    global_targets: dict[str, int],
    global_counts: dict[str, int],
    group_targets: dict[str, int],
    group_counts: dict[str, int],
) -> str:
    def score(split: str) -> tuple[float, float, float, float, str]:
        global_overflow = global_counts[split] - global_targets[split]
        group_overflow = group_counts[split] - group_targets[split]
        global_fill = global_counts[split]
        bucket = hash_bucket(f"{seed}:{split}", record["example_id"])
        return (global_overflow, group_overflow, global_fill, bucket, split)

    return min(candidate_splits, key=score)



def assign_group_balanced(
    records: list[dict],
    seed: str,
    ratios: dict[str, float],
    min_per_group: int,
    global_targets: dict[str, int],
    global_counts: dict[str, int],
) -> dict[str, list[dict]]:
    split_map = {split: [] for split in SPLIT_NAMES}
    if not records:
        return split_map

    group_targets = build_ratio_targets(len(records), ratios)
    group_counts = {split: 0 for split in SPLIT_NAMES}
    feasible_group_min = min(min_per_group, len(records), len(SPLIT_NAMES)) if min_per_group > 0 else 0
    ordered = sorted(records, key=lambda item: (hash_bucket(seed, item["example_id"]), item["example_id"]))

    for record in ordered:
        candidate_splits = list(SPLIT_NAMES)
        if feasible_group_min > 0:
            underfilled = [split for split in SPLIT_NAMES if group_counts[split] < feasible_group_min]
            if underfilled:
                candidate_splits = underfilled

        chosen = pick_split(record, candidate_splits, seed, global_targets, global_counts, group_targets, group_counts)
        split_map[chosen].append(record)
        group_counts[chosen] += 1
        global_counts[chosen] += 1

    return split_map



def assign_records(records: list[dict], seed: str, ratios: dict[str, float], balance_key: str | None, min_per_balance_group: int) -> dict[str, list[dict]]:
    if balance_key is None:
        split_map = {split: [] for split in SPLIT_NAMES}
        for record in sorted(records, key=lambda item: item["example_id"]):
            split = assign_split(record["example_id"], seed, ratios["train"], ratios["val"])
            split_map[split].append(record)
        return split_map

    groups: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        groups[get_balance_value(record, balance_key)].append(record)

    split_map = {split: [] for split in SPLIT_NAMES}
    global_targets = build_ratio_targets(len(records), ratios)
    global_counts = {split: 0 for split in SPLIT_NAMES}

    for group_name in sorted(groups):
        group_seed = f"{seed}:{balance_key}:{group_name}"
        group_assignment = assign_group_balanced(
            groups[group_name],
            group_seed,
            ratios,
            min_per_balance_group,
            global_targets,
            global_counts,
        )
        for split in SPLIT_NAMES:
            split_map[split].extend(group_assignment[split])

    for split in SPLIT_NAMES:
        split_map[split].sort(key=lambda item: item["example_id"])
    return split_map



def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(path)



def flags_to_policy_overrides(flags: list[str], default_min: int) -> tuple[str | None, int]:
    balance_key = None
    min_per_balance_group = default_min
    index = 0
    while index < len(flags):
        flag = flags[index]
        if flag == "--balance-key" and index + 1 < len(flags):
            balance_key = flags[index + 1]
            index += 2
            continue
        if flag == "--min-per-balance-group" and index + 1 < len(flags):
            min_per_balance_group = int(flags[index + 1])
            index += 2
            continue
        index += 1
    return balance_key, min_per_balance_group



def main() -> None:
    args = parse_args()
    ensure_ratios(args.train_ratio, args.val_ratio, args.test_ratio)
    if args.min_per_balance_group < 0:
        raise ValueError("--min-per-balance-group must be >= 0")

    input_path = args.input.resolve()
    output_dir = args.output_dir.resolve()

    records = load_jsonl(input_path)
    source_schema = validate_records(records)
    ratios = {"train": args.train_ratio, "val": args.val_ratio, "test": args.test_ratio}

    balance_key = args.balance_key
    min_per_balance_group = args.min_per_balance_group
    auto_policy = None
    if args.auto_policy and balance_key is None:
        auto_policy = recommend_policy(records)
        balance_key, min_per_balance_group = flags_to_policy_overrides(
            auto_policy.get("flags", []),
            min_per_balance_group,
        )

    split_map = assign_records(
        records,
        seed=args.seed,
        ratios=ratios,
        balance_key=balance_key,
        min_per_balance_group=min_per_balance_group,
    )

    assigned_ids = set()
    for split_name, split_records in split_map.items():
        for record in split_records:
            example_id = record["example_id"]
            if example_id in assigned_ids:
                raise ValueError(f"example_id assigned to multiple splits: {example_id}")
            assigned_ids.add(example_id)
    if assigned_ids != {record["example_id"] for record in records}:
        raise ValueError("Split assignment lost or duplicated examples")

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "manifest_version": "seed-splits-v3",
        "input_path": display_path(input_path),
        "source_schema": source_schema,
        "seed": args.seed,
        "ratios": ratios,
        "balance_key": balance_key,
        "min_per_balance_group": min_per_balance_group,
        "auto_policy": auto_policy,
        "splits": {},
    }

    for split_name, split_records in split_map.items():
        output_path = output_dir / f"{split_name}.jsonl"
        count = write_jsonl(output_path, split_records)
        manifest["splits"][split_name] = {
            "path": display_path(output_path),
            "summary": summarize(split_records),
            "example_ids": [record["example_id"] for record in split_records],
            "count_written": count,
        }

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote deterministic splits for {len(records)} examples to {display_path(output_dir)}")


if __name__ == "__main__":
    main()
