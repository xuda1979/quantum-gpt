#!/usr/bin/env python3
"""Verify train/eval holdout integrity for generated SFT datasets."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-file", type=Path, required=True)
    parser.add_argument("--eval-file", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=None)
    parser.add_argument("--min-train-count", type=int, default=0)
    parser.add_argument("--min-eval-count", type=int, default=0)
    parser.add_argument("--require-task-disjoint", action="store_true")
    parser.add_argument("--require-prompt-family-disjoint", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row.get("example_id"), str) or not row["example_id"]:
                raise ValueError(f"{path}:{line_no} missing non-empty example_id")
            metadata = row.get("metadata")
            if not isinstance(metadata, dict):
                raise ValueError(f"{path}:{line_no} missing metadata object")
            rows.append(row)
    if not rows:
        raise ValueError(f"{path} is empty")
    return rows


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    example_ids = [str(row["example_id"]) for row in rows]
    task_ids = [str(row.get("metadata", {}).get("task_id", "unknown")) for row in rows]

    # Keep the legacy "unknown" behavior for reporting, but also compute explicit
    # prompt-family coverage for gate logic.
    prompt_families_report = [
        str(row.get("metadata", {}).get("prompt_family", "unknown")) for row in rows
    ]
    prompt_families_explicit: list[str] = []
    prompt_families_missing = 0
    for row in rows:
        pf = row.get("metadata", {}).get("prompt_family", None)
        if isinstance(pf, str) and pf.strip():
            prompt_families_explicit.append(pf)
        else:
            prompt_families_missing += 1

    domains = [str(row.get("metadata", {}).get("domain", "unknown")) for row in rows]
    return {
        "count": len(rows),
        "unique_example_ids": len(set(example_ids)),
        "duplicate_example_ids": sorted(
            example_id for example_id, count in Counter(example_ids).items() if count > 1
        ),
        "unique_task_ids": sorted(set(task_ids)),
        "unique_prompt_families": sorted(set(prompt_families_report)),
        "prompt_family_missing_count": prompt_families_missing,
        "unique_prompt_families_explicit": sorted(set(prompt_families_explicit)),
        "domain_counts": dict(sorted(Counter(domains).items())),
        "task_counts": dict(sorted(Counter(task_ids).items())),
        "prompt_family_counts": dict(sorted(Counter(prompt_families_report).items())),
    }


def compare_manifest_summary(
    report: dict[str, Any],
    split_name: str,
    actual_summary: dict[str, Any],
    manifest_summary: dict[str, Any] | None,
) -> None:
    if manifest_summary is None:
        return
    report[f"{split_name}_matches_manifest_count"] = actual_summary[
        "count"
    ] == manifest_summary.get("count")
    report[f"{split_name}_matches_manifest_tasks"] = actual_summary[
        "task_counts"
    ] == manifest_summary.get("tasks")
    report[f"{split_name}_matches_manifest_prompt_families"] = actual_summary[
        "prompt_family_counts"
    ] == manifest_summary.get("prompt_families")
    report[f"{split_name}_matches_manifest_domains"] = actual_summary[
        "domain_counts"
    ] == manifest_summary.get("domains")


def main() -> int:
    args = parse_args()
    train_rows = load_jsonl(args.train_file)
    eval_rows = load_jsonl(args.eval_file)
    train_summary = summarize_rows(train_rows)
    eval_summary = summarize_rows(eval_rows)

    train_task_ids = set(train_summary["unique_task_ids"])
    eval_task_ids = set(eval_summary["unique_task_ids"])

    # For prompt-family disjointness, we want determinism and provability:
    # - exclude missing/unknown prompt_family values from the overlap set
    # - separately track missing counts; if the user explicitly requests
    #   prompt-family disjointness, we fail when either split is missing.
    train_prompt_families_explicit = set(train_summary.get("unique_prompt_families_explicit", []))
    eval_prompt_families_explicit = set(eval_summary.get("unique_prompt_families_explicit", []))

    train_prompt_families = set(train_prompt_families_explicit)
    eval_prompt_families = set(eval_prompt_families_explicit)

    train_example_ids = {str(row["example_id"]) for row in train_rows}
    eval_example_ids = {str(row["example_id"]) for row in eval_rows}

    report: dict[str, Any] = {
        "train_file": str(args.train_file.resolve()),
        "eval_file": str(args.eval_file.resolve()),
        "manifest": str(args.manifest.resolve()) if args.manifest else None,
        "requirements": {
            "min_train_count": args.min_train_count,
            "min_eval_count": args.min_eval_count,
            "require_task_disjoint": args.require_task_disjoint,
            "require_prompt_family_disjoint": args.require_prompt_family_disjoint,
        },
        "train": train_summary,
        "eval": eval_summary,
        "cross_split": {
            "example_id_overlap": sorted(train_example_ids & eval_example_ids),
            "task_id_overlap": sorted(train_task_ids & eval_task_ids),
            "prompt_family_overlap": sorted(train_prompt_families & eval_prompt_families),
        },
        "checks": {},
    }

    checks = report["checks"]
    checks["train_count_meets_min"] = train_summary["count"] >= args.min_train_count
    checks["eval_count_meets_min"] = eval_summary["count"] >= args.min_eval_count
    checks["train_example_ids_unique"] = not train_summary["duplicate_example_ids"]
    checks["eval_example_ids_unique"] = not eval_summary["duplicate_example_ids"]
    checks["example_id_disjoint"] = not report["cross_split"]["example_id_overlap"]
    checks["task_id_disjoint"] = not report["cross_split"]["task_id_overlap"]
    checks["prompt_family_disjoint"] = not report["cross_split"]["prompt_family_overlap"]

    # Provability: if prompt_family is missing in either split, we cannot
    # actually prove disjointness, even if the explicit overlap set is empty.
    train_pf_missing = int(train_summary.get("prompt_family_missing_count", 0) or 0) > 0
    eval_pf_missing = int(eval_summary.get("prompt_family_missing_count", 0) or 0) > 0
    checks["prompt_family_disjoint_provable"] = (
        checks["prompt_family_disjoint"] and (not train_pf_missing) and (not eval_pf_missing)
    )

    manifest = load_json(args.manifest) if args.manifest else None
    if manifest is not None:
        holdout_policy = manifest.get("holdout_policy", {})
        report["manifest_holdout_policy"] = holdout_policy
        compare_manifest_summary(report, "train", train_summary, manifest.get("train_summary"))
        compare_manifest_summary(report, "eval", eval_summary, manifest.get("eval_summary"))
        checks["manifest_claim_train_eval_example_id_overlap"] = holdout_policy.get(
            "train_eval_example_id_overlap"
        ) == bool(report["cross_split"]["example_id_overlap"])
        checks["manifest_claim_train_eval_task_id_overlap"] = holdout_policy.get(
            "train_eval_task_id_overlap"
        ) == bool(report["cross_split"]["task_id_overlap"])
        checks["manifest_claim_train_eval_prompt_family_overlap"] = holdout_policy.get(
            "train_eval_prompt_family_overlap"
        ) == bool(report["cross_split"]["prompt_family_overlap"])

    if args.require_task_disjoint:
        checks["required_task_disjoint_satisfied"] = checks["task_id_disjoint"]
    if args.require_prompt_family_disjoint:
        checks["required_prompt_family_disjoint_satisfied"] = checks["prompt_family_disjoint"]

    # "ok" should reflect the *requested* integrity requirements, not every optional metric.
    # Required invariants are always enforced (counts, example_id uniqueness/disjointness).
    # Optional disjointness checks are only required when the corresponding flags are set.
    required_values: list[bool] = [
        checks["train_count_meets_min"],
        checks["eval_count_meets_min"],
        checks["train_example_ids_unique"],
        checks["eval_example_ids_unique"],
        checks["example_id_disjoint"],
    ]

    if args.require_task_disjoint:
        required_values.append(checks["task_id_disjoint"])

    if args.require_prompt_family_disjoint:
        required_values.append(checks["prompt_family_disjoint"])

    # If a manifest is provided, any manifest-claim mismatches should fail the gate.
    if manifest is not None:
        required_values.extend(
            [
                checks["manifest_claim_train_eval_example_id_overlap"],
                checks["manifest_claim_train_eval_task_id_overlap"],
                checks["manifest_claim_train_eval_prompt_family_overlap"],
            ]
        )

    report["ok"] = all(bool(v) for v in required_values)

    rendered = json.dumps(report, indent=2) + "\n"
    if args.output is not None:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
