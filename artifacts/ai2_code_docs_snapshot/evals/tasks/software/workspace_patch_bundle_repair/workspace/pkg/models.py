def clone_entry(entry: dict) -> dict:
    return {
        "value": entry["value"],
        "version": entry["version"],
    }


def clone_state(state: dict) -> dict:
    return {key: clone_entry(entry) for key, entry in state.items()}


def build_conflict(
    *,
    patch_id: str,
    key: str,
    reason: str,
    expected_version: int,
    actual_version,
    attempted_new_version: int,
) -> dict:
    return {
        "patch_id": patch_id,
        "key": key,
        "reason": reason,
        "expected_version": expected_version,
        "actual_version": actual_version,
        "attempted_new_version": attempted_new_version,
    }


def conflict_signature(conflict: dict) -> tuple[str, str]:
    return (conflict["key"], conflict["reason"])
