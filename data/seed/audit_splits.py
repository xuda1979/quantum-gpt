#!/usr/bin/env python3
"""Audit train/val/test split manifests for tiny-corpus quality issues."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "data" / "seed" / "splits" / "manifest.json"
SPLIT_NAMES = ("train", "val", "test")
SUMMARY_GROUP_KEYS = ("domains", "task_types", "categories", "difficulties")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help="Split manifest to audit")
    parser.add_argument(
        "--warn-ratio-drift",
        type=float,
        default=0.20,
        help="Warn when absolute split-share drift exceeds this threshold",
    )
    parser.add_argument(
        "--warn-group-skew",
        type=float,
        default=0.60,
        help="Warn when a domain/task_type/category/difficulty share inside a split exceeds this threshold",
    )
    parser.add_argument(
        "--warn-missing-coverage",
        action="store_true",
        help="Warn when a split is missing a group value that exists elsewhere in the corpus",
    )
    return parser.parse_args()



def load_manifest(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)



def validate_manifest(manifest: dict) -> None:
    if "splits" not in manifest or not isinstance(manifest["splits"], dict):
        raise ValueError("Manifest must contain a 'splits' object")
    missing = [name for name in SPLIT_NAMES if name not in manifest["splits"]]
    if missing:
        raise ValueError(f"Manifest missing splits: {missing}")



def summarize_total_counts(manifest: dict) -> tuple[int, dict[str, int]]:
    split_counts = {}
    total = 0
    for split_name in SPLIT_NAMES:
        count = int(manifest["splits"][split_name].get("summary", {}).get("count", 0))
        split_counts[split_name] = count
        total += count
    return total, split_counts



def compute_ratio_drift(manifest: dict, split_counts: dict[str, int], total: int) -> list[str]:
    ratios = manifest.get("ratios", {})
    warnings = []
    if total == 0:
        return ["dataset has zero total examples"]
    for split_name in SPLIT_NAMES:
        target = float(ratios.get(split_name, 0.0))
        actual = split_counts[split_name] / total
        drift = abs(actual - target)
        warnings.append(
            f"ratio[{split_name}] target={target:.2f} actual={actual:.2f} drift={drift:.2f}"
        )
    return warnings



def collect_ids(manifest: dict) -> tuple[set[str], list[str]]:
    seen = set()
    problems = []
    for split_name in SPLIT_NAMES:
        ids = manifest["splits"][split_name].get("example_ids", [])
        local_seen = set()
        for example_id in ids:
            if example_id in local_seen:
                problems.append(f"duplicate id within {split_name}: {example_id}")
            local_seen.add(example_id)
            if example_id in seen:
                problems.append(f"duplicate id across splits: {example_id}")
            seen.add(example_id)
    return seen, problems



def check_empty_splits(split_counts: dict[str, int]) -> list[str]:
    return [f"split '{split_name}' is empty" for split_name, count in split_counts.items() if count == 0]



def group_label(group_key: str) -> str:
    return group_key[:-1] if group_key.endswith("s") else group_key



def collect_group_universe(manifest: dict) -> dict[str, set[str]]:
    universe = {group_key: set() for group_key in SUMMARY_GROUP_KEYS}
    for split_name in SPLIT_NAMES:
        summary = manifest["splits"][split_name].get("summary", {})
        for group_key in SUMMARY_GROUP_KEYS:
            group_counts = summary.get(group_key, {})
            if isinstance(group_counts, dict):
                universe[group_key].update(str(name) for name in group_counts)
    return universe



def check_group_skew(manifest: dict, threshold: float) -> list[str]:
    warnings = []
    for split_name in SPLIT_NAMES:
        summary = manifest["splits"][split_name].get("summary", {})
        count = int(summary.get("count", 0))
        if count <= 0:
            continue
        for group_key in SUMMARY_GROUP_KEYS:
            group_counts = summary.get(group_key, {})
            for name, value in sorted(group_counts.items()):
                share = value / count
                if share > threshold:
                    warnings.append(
                        f"{split_name} {group_label(group_key)} '{name}' share={share:.2f} ({value}/{count}) exceeds {threshold:.2f}"
                    )
    return warnings



def check_missing_coverage(manifest: dict) -> list[str]:
    warnings = []
    universe = collect_group_universe(manifest)
    for split_name in SPLIT_NAMES:
        summary = manifest["splits"][split_name].get("summary", {})
        count = int(summary.get("count", 0))
        if count <= 0:
            continue
        for group_key in SUMMARY_GROUP_KEYS:
            present = set(str(name) for name in summary.get(group_key, {}))
            missing = sorted(universe[group_key] - present)
            for name in missing:
                warnings.append(
                    f"{split_name} missing {group_label(group_key)} '{name}' present elsewhere in corpus"
                )
    return warnings



def check_ratio_drift(manifest: dict, split_counts: dict[str, int], total: int, threshold: float) -> list[str]:
    warnings = []
    ratios = manifest.get("ratios", {})
    if total == 0:
        return ["dataset has zero total examples"]
    for split_name in SPLIT_NAMES:
        target = float(ratios.get(split_name, 0.0))
        actual = split_counts[split_name] / total
        drift = abs(actual - target)
        if drift > threshold:
            warnings.append(
                f"{split_name} ratio drift {drift:.2f} exceeds {threshold:.2f} (target={target:.2f}, actual={actual:.2f})"
            )
    return warnings



def build_report(manifest: dict, warn_ratio_drift: float, warn_group_skew: float, warn_missing_coverage: bool) -> dict:
    total, split_counts = summarize_total_counts(manifest)
    ids_seen, id_problems = collect_ids(manifest)
    warnings = []
    warnings.extend(check_empty_splits(split_counts))
    warnings.extend(id_problems)
    warnings.extend(check_group_skew(manifest, warn_group_skew))
    if warn_missing_coverage:
        warnings.extend(check_missing_coverage(manifest))
    warnings.extend(check_ratio_drift(manifest, split_counts, total, warn_ratio_drift))

    return {
        "manifest_version": manifest.get("manifest_version"),
        "input_path": manifest.get("input_path"),
        "source_schema": manifest.get("source_schema"),
        "balance_key": manifest.get("balance_key"),
        "min_per_balance_group": manifest.get("min_per_balance_group"),
        "auto_policy": manifest.get("auto_policy"),
        "total_examples": total,
        "unique_example_ids": len(ids_seen),
        "split_counts": split_counts,
        "group_universe": {key: sorted(values) for key, values in collect_group_universe(manifest).items()},
        "ratio_observations": compute_ratio_drift(manifest, split_counts, total),
        "warnings": warnings,
        "status": "ok" if not warnings else "warn",
    }



def main() -> None:
    args = parse_args()
    manifest = load_manifest(args.manifest)
    validate_manifest(manifest)
    report = build_report(manifest, args.warn_ratio_drift, args.warn_group_skew, args.warn_missing_coverage)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
