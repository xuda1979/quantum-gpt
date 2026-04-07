from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class ConflictRecord:
    patch_id: str
    key: str
    reason: str
    expected_version: int
    actual_version: Optional[int]
    attempted_new_version: int


@dataclass(frozen=True)
class ApplyResult:
    state: dict[str, dict[str, Any]]
    applied_patch_ids: list[str]
    conflicts: list[ConflictRecord]


def apply_patch_plan(base_state, patches):
    state = {key: value.copy() for key, value in base_state.items()}
    applied_patch_ids = []
    conflicts = []
    seen_patch_ids = set()

    for patch in patches:
        patch_id = patch["patch_id"]
        if patch_id in seen_patch_ids:
            continue
        seen_patch_ids.add(patch_id)

        key = patch["key"]
        current = state.get(key)

        if current is None:
            conflicts.append(
                ConflictRecord(
                    patch_id=patch_id,
                    key=key,
                    reason="missing_key",
                    expected_version=patch["expected_version"],
                    actual_version=None,
                    attempted_new_version=patch["new_version"],
                )
            )
            continue

        current_version = current["version"]

        if current_version != patch["expected_version"]:
            conflicts.append(
                ConflictRecord(
                    patch_id=patch_id,
                    key=key,
                    reason="version_mismatch",
                    expected_version=patch["expected_version"],
                    actual_version=current_version,
                    attempted_new_version=patch["new_version"],
                )
            )
            continue

        if patch["new_version"] <= current_version:
            conflicts.append(
                ConflictRecord(
                    patch_id=patch_id,
                    key=key,
                    reason="non_monotonic_version",
                    expected_version=patch["expected_version"],
                    actual_version=current_version,
                    attempted_new_version=patch["new_version"],
                )
            )
            continue

        state[key] = {"value": patch["value"], "version": patch["new_version"]}
        applied_patch_ids.append(patch_id)

    return ApplyResult(
        state=state,
        applied_patch_ids=applied_patch_ids,
        conflicts=conflicts,
    )


def apply_patches(base_state, patches):
    result = apply_patch_plan(base_state, patches)
    return {
        "state": result.state,
        "applied_patch_ids": list(result.applied_patch_ids),
        "conflicts": [
            {
                "patch_id": conflict.patch_id,
                "key": conflict.key,
                "reason": conflict.reason,
                "expected_version": conflict.expected_version,
                "actual_version": conflict.actual_version,
                "attempted_new_version": conflict.attempted_new_version,
            }
            for conflict in result.conflicts
        ],
    }


def render_conflict_report(result):
    conflicts = result["conflicts"]
    return {
        "applied_count": len(result["applied_patch_ids"]),
        "applied_patch_ids": list(result["applied_patch_ids"]),
        "conflict_count": len(conflicts),
        "conflict_keys": [conflict["key"] for conflict in conflicts],
        "conflict_reasons": [conflict["reason"] for conflict in conflicts],
    }
