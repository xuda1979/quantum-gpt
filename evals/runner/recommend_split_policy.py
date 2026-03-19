from __future__ import annotations

from collections import Counter
from typing import Any

SPLIT_NAMES = ("train", "val", "test")


def record_metadata(record: dict[str, Any]) -> dict[str, Any]:
    metadata = record.get("metadata")
    return metadata if isinstance(metadata, dict) else {}



def get_value(record: dict[str, Any], key: str) -> str:
    metadata = record_metadata(record)
    value = record.get(key, metadata.get(key, "unknown"))
    return str(value)



def summarize_groups(records: list[dict[str, Any]], key: str) -> dict[str, int]:
    counter = Counter(get_value(record, key) for record in records)
    return dict(sorted(counter.items()))



def recommend_policy(records: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(records)
    domains = summarize_groups(records, "domain")
    task_types = summarize_groups(records, "task_type")

    min_domain = min(domains.values()) if domains else 0
    min_task_type = min(task_types.values()) if task_types else 0

    if total <= 9 or min_domain < len(SPLIT_NAMES):
        reason = (
            "Corpus is still tiny relative to the three-way split, so explicit domain coverage matters more "
            "than preserving nominal ratios."
        )
        return {
            "policy": "domain_balanced",
            "flags": ["--balance-key", "domain", "--min-per-balance-group", "1"],
            "reason": reason,
        }

    if min_task_type >= len(SPLIT_NAMES):
        reason = (
            "Each task type has enough support to appear across train/val/test, and protecting holdouts from "
            "task-family collapse is more valuable than chasing perfect domain symmetry."
        )
        return {
            "policy": "task_type_balanced",
            "flags": ["--balance-key", "task_type", "--min-per-balance-group", "1"],
            "reason": reason,
        }

    reason = (
        "The corpus is no longer tiny, but some task types are still too sparse for forced coverage across all "
        "three splits. Plain deterministic hashing is the least distortive default until those groups grow."
    )
    return {
        "policy": "plain_hash",
        "flags": [],
        "reason": reason,
    }
