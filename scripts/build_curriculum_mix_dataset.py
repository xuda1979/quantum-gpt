#!/usr/bin/env python3
"""Build a deterministic mixed chat-SFT dataset from multiple JSONL sources.

The optional domain gates encode the practical lesson from domain-expert
fine-tuning work: push the expert domain hard, but keep replay coverage for
general software-engineering behavior so specialization does not silently erase
the base coding skill.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--train-source",
        action="append",
        default=[],
        help=(
            "Train JSONL source spec. Format: path[::key=value...]. "
            "Supported keys: label, domain, include_task_file, exclude_task_file, repeat, bucket_lt, bucket_ge."
        ),
    )
    parser.add_argument(
        "--eval-source",
        action="append",
        default=[],
        help=(
            "Eval JSONL source spec. Format: path[::key=value...]. "
            "Supported keys: label, domain, include_task_file, exclude_task_file, repeat, bucket_lt, bucket_ge."
        ),
    )
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--seed-tag", default="curriculum-mix-v1")
    parser.add_argument(
        "--require-train-domain-min",
        action="append",
        default=[],
        metavar="DOMAIN=COUNT",
        help="Fail unless the train split has at least COUNT rows for DOMAIN.",
    )
    parser.add_argument(
        "--require-eval-domain-min",
        action="append",
        default=[],
        metavar="DOMAIN=COUNT",
        help="Fail unless the eval split has at least COUNT rows for DOMAIN.",
    )
    parser.add_argument(
        "--require-train-domain-ratio",
        action="append",
        default=[],
        metavar="DOMAIN=RATIO",
        help="Fail unless DOMAIN is at least RATIO of the train split.",
    )
    parser.add_argument(
        "--require-eval-domain-ratio",
        action="append",
        default=[],
        metavar="DOMAIN=RATIO",
        help="Fail unless DOMAIN is at least RATIO of the eval split.",
    )
    parser.add_argument(
        "--require-task-disjoint",
        action="store_true",
        help="Fail if train and eval task_id sets overlap.",
    )
    parser.add_argument(
        "--reference-note",
        action="append",
        default=[],
        help="Record a source/reference note in the manifest, e.g. the PDF principle behind the gates.",
    )
    return parser.parse_args()


def stable_bucket(text: str, seed_tag: str) -> float:
    digest = hashlib.sha256(f"{seed_tag}:{text}".encode()).hexdigest()
    return int(digest[:16], 16) / float(16**16 - 1)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def parse_source_spec(raw: str) -> dict[str, Any]:
    pieces = raw.split("::")
    path = Path(pieces[0])
    options: dict[str, Any] = {"path": path}
    for piece in pieces[1:]:
        if "=" not in piece:
            raise SystemExit(f"Invalid source option {piece!r} in {raw!r}")
        key, value = piece.split("=", 1)
        options[key] = value
    if "label" not in options:
        stem = path.stem
        parent = path.parent.name
        options["label"] = f"{parent}_{stem}"
    return options


def load_task_ids(path: Path) -> set[str]:
    task_ids = set()
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        task_ids.add(line)
    return task_ids


def filter_rows(
    rows: list[dict[str, Any]], spec: dict[str, Any], seed_tag: str
) -> list[dict[str, Any]]:
    domains = None
    if spec.get("domain"):
        domains = {item.strip() for item in str(spec["domain"]).split(",") if item.strip()}

    include_task_ids = None
    if spec.get("include_task_file"):
        include_task_ids = load_task_ids(Path(str(spec["include_task_file"])))

    exclude_task_ids: set[str] = set()
    if spec.get("exclude_task_file"):
        exclude_task_ids = load_task_ids(Path(str(spec["exclude_task_file"])))

    bucket_lt = float(spec["bucket_lt"]) if spec.get("bucket_lt") is not None else None
    bucket_ge = float(spec["bucket_ge"]) if spec.get("bucket_ge") is not None else None

    filtered: list[dict[str, Any]] = []
    for row in rows:
        metadata = row.get("metadata", {})
        task_id = str(metadata.get("task_id", ""))
        domain = str(metadata.get("domain", ""))
        if domains is not None and domain not in domains:
            continue
        if include_task_ids is not None and task_id not in include_task_ids:
            continue
        if task_id in exclude_task_ids:
            continue
        bucket = stable_bucket(str(row.get("example_id", "")), f"{seed_tag}:{spec['label']}:bucket")
        if bucket_lt is not None and not bucket < bucket_lt:
            continue
        if bucket_ge is not None and not bucket >= bucket_ge:
            continue
        filtered.append(row)
    return filtered


def materialize_rows(
    specs: list[str], split_name: str, seed_tag: str
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows_out: list[dict[str, Any]] = []
    source_summaries: list[dict[str, Any]] = []
    seen_example_ids: set[str] = set()

    for raw_spec in specs:
        spec = parse_source_spec(raw_spec)
        source_rows = filter_rows(load_jsonl(spec["path"]), spec, seed_tag)
        repeat = int(spec.get("repeat", "1"))
        if repeat < 1:
            raise SystemExit(f"repeat must be >= 1 for source {raw_spec!r}")

        source_summary = {
            "label": spec["label"],
            "path": str(spec["path"]),
            "repeat": repeat,
            "selected_rows": len(source_rows),
        }
        source_summaries.append(source_summary)

        for repeat_index in range(repeat):
            for row in source_rows:
                cloned = copy.deepcopy(row)
                original_example_id = str(cloned.get("example_id", "missing-example-id"))
                new_example_id = f"{spec['label']}__r{repeat_index}__{original_example_id}"
                if new_example_id in seen_example_ids:
                    raise SystemExit(
                        f"Duplicate example_id after materialization: {new_example_id}"
                    )
                seen_example_ids.add(new_example_id)
                cloned["example_id"] = new_example_id
                metadata = dict(cloned.get("metadata") or {})
                metadata["curriculum_source"] = spec["label"]
                metadata["curriculum_split"] = split_name
                metadata["curriculum_repeat_index"] = repeat_index
                cloned["metadata"] = metadata
                rows_out.append(cloned)

    return rows_out, source_summaries


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_domain = Counter()
    by_task = Counter()
    by_source = Counter()
    by_family = Counter()
    for row in rows:
        metadata = row.get("metadata", {})
        by_domain[str(metadata.get("domain", "unknown"))] += 1
        by_task[str(metadata.get("task_id", "unknown"))] += 1
        by_source[str(metadata.get("curriculum_source", "unknown"))] += 1
        by_family[str(metadata.get("prompt_family", "unknown"))] += 1
    return {
        "count": len(rows),
        "domains": dict(sorted(by_domain.items())),
        "sources": dict(sorted(by_source.items())),
        "prompt_families": dict(sorted(by_family.items())),
        "top_tasks": by_task.most_common(20),
    }


def parse_min_requirements(raw_items: list[str], *, value_type: type) -> dict[str, int | float]:
    parsed: dict[str, int | float] = {}
    for raw in raw_items:
        if "=" not in raw:
            raise SystemExit(f"Invalid domain requirement {raw!r}; expected DOMAIN=VALUE")
        domain, value = raw.split("=", 1)
        domain = domain.strip()
        if not domain:
            raise SystemExit(f"Invalid domain requirement {raw!r}; domain is empty")
        try:
            parsed[domain] = value_type(value)
        except ValueError as exc:
            raise SystemExit(f"Invalid value in domain requirement {raw!r}") from exc
    return parsed


def task_ids(rows: list[dict[str, Any]]) -> set[str]:
    return {str(row.get("metadata", {}).get("task_id", "unknown")) for row in rows}


def build_domain_expert_contract(
    *,
    train_rows: list[dict[str, Any]],
    eval_rows: list[dict[str, Any]],
    train_domain_min: dict[str, int],
    eval_domain_min: dict[str, int],
    train_domain_ratio: dict[str, float],
    eval_domain_ratio: dict[str, float],
    require_task_disjoint: bool,
    reference_notes: list[str],
) -> dict[str, Any]:
    train_summary = summarize_rows(train_rows)
    eval_summary = summarize_rows(eval_rows)
    train_domains = dict(train_summary["domains"])
    eval_domains = dict(eval_summary["domains"])
    checks: dict[str, bool] = {}
    details: dict[str, Any] = {
        "train_domain_counts": train_domains,
        "eval_domain_counts": eval_domains,
        "train_domain_ratios": {},
        "eval_domain_ratios": {},
    }

    train_count = max(int(train_summary["count"]), 1)
    eval_count = max(int(eval_summary["count"]), 1)
    for domain, minimum in train_domain_min.items():
        checks[f"train_domain_min_{domain}"] = int(train_domains.get(domain, 0)) >= int(minimum)
    for domain, minimum in eval_domain_min.items():
        checks[f"eval_domain_min_{domain}"] = int(eval_domains.get(domain, 0)) >= int(minimum)
    for domain, minimum_ratio in train_domain_ratio.items():
        ratio = int(train_domains.get(domain, 0)) / train_count
        details["train_domain_ratios"][domain] = ratio
        checks[f"train_domain_ratio_{domain}"] = ratio >= float(minimum_ratio)
    for domain, minimum_ratio in eval_domain_ratio.items():
        ratio = int(eval_domains.get(domain, 0)) / eval_count
        details["eval_domain_ratios"][domain] = ratio
        checks[f"eval_domain_ratio_{domain}"] = ratio >= float(minimum_ratio)

    train_task_ids = task_ids(train_rows)
    eval_task_ids = task_ids(eval_rows)
    task_overlap = sorted(train_task_ids & eval_task_ids)
    details["task_id_overlap"] = task_overlap
    if require_task_disjoint:
        checks["task_id_disjoint"] = not task_overlap

    return {
        "contract_version": "domain-expert-curriculum-v1",
        "purpose": "Specialize toward quantum coding while preserving agentic software-engineering replay and held-out eval integrity.",
        "reference_notes": reference_notes,
        "requirements": {
            "train_domain_min": train_domain_min,
            "eval_domain_min": eval_domain_min,
            "train_domain_ratio": train_domain_ratio,
            "eval_domain_ratio": eval_domain_ratio,
            "require_task_disjoint": require_task_disjoint,
        },
        "checks": dict(sorted(checks.items())),
        "details": details,
        "ok": all(checks.values()) if checks else True,
    }


def main() -> int:
    args = parse_args()
    if not args.train_source:
        raise SystemExit("At least one --train-source is required")
    if not args.eval_source:
        raise SystemExit("At least one --eval-source is required")

    train_rows, train_sources = materialize_rows(args.train_source, "train", args.seed_tag)
    eval_rows, eval_sources = materialize_rows(args.eval_source, "eval", args.seed_tag)
    if not train_rows or not eval_rows:
        raise SystemExit("Constructed dataset has an empty train or eval split")

    domain_expert_contract = build_domain_expert_contract(
        train_rows=train_rows,
        eval_rows=eval_rows,
        train_domain_min=parse_min_requirements(args.require_train_domain_min, value_type=int),
        eval_domain_min=parse_min_requirements(args.require_eval_domain_min, value_type=int),
        train_domain_ratio=parse_min_requirements(
            args.require_train_domain_ratio, value_type=float
        ),
        eval_domain_ratio=parse_min_requirements(args.require_eval_domain_ratio, value_type=float),
        require_task_disjoint=args.require_task_disjoint,
        reference_notes=list(args.reference_note),
    )
    if not domain_expert_contract["ok"]:
        failed = [name for name, passed in domain_expert_contract["checks"].items() if not passed]
        raise SystemExit(f"Domain-expert curriculum gates failed: {', '.join(failed)}")

    write_jsonl(args.out_dir / "train.jsonl", train_rows)
    write_jsonl(args.out_dir / "eval.jsonl", eval_rows)

    manifest = {
        "manifest_version": "curriculum-mix-v1",
        "out_dir": str(args.out_dir),
        "seed_tag": args.seed_tag,
        "dataset_contract": {
            "generation_script": str(Path(__file__).resolve().relative_to(ROOT)),
            "source_task_ids": sorted(
                {
                    str(row.get("metadata", {}).get("task_id", "unknown"))
                    for row in [*train_rows, *eval_rows]
                }
            ),
            "train_task_ids": sorted(
                {str(row.get("metadata", {}).get("task_id", "unknown")) for row in train_rows}
            ),
            "eval_task_ids": sorted(
                {str(row.get("metadata", {}).get("task_id", "unknown")) for row in eval_rows}
            ),
            "prompt_families": {
                "train": sorted(
                    {
                        str(row.get("metadata", {}).get("prompt_family", "unknown"))
                        for row in train_rows
                    }
                ),
                "eval": sorted(
                    {
                        str(row.get("metadata", {}).get("prompt_family", "unknown"))
                        for row in eval_rows
                    }
                ),
            },
        },
        "train_sources": train_sources,
        "eval_sources": eval_sources,
        "train_summary": summarize_rows(train_rows),
        "eval_summary": summarize_rows(eval_rows),
        "domain_expert_contract": domain_expert_contract,
    }
    (args.out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
