def apply_patches(base_state: dict[str, dict], patches: list[dict]) -> dict:
    """
    Apply ordered patches to a versioned key/value state with duplicate suppression.

    Rules:
    - Inputs must not be mutated.
    - Only the first occurrence of a patch_id is considered, whether it applies or conflicts.
    - A patch applies only when:
      * the key exists
      * expected_version equals the current version
      * new_version is strictly greater than the current version
    - Conflicts are reported in encounter order.
    """
    state = {
        key: {"value": record["value"], "version": record["version"]}
        for key, record in base_state.items()
    }

    seen_patch_ids = set()
    applied_patch_ids = []
    conflicts = []

    for patch in patches:
        patch_id = patch["patch_id"]
        if patch_id in seen_patch_ids:
            continue
        seen_patch_ids.add(patch_id)

        key = patch["key"]
        expected_version = patch["expected_version"]
        attempted_new_version = patch["new_version"]

        if key not in state:
            conflicts.append(
                {
                    "patch_id": patch_id,
                    "key": key,
                    "reason": "missing_key",
                    "expected_version": expected_version,
                    "actual_version": None,
                    "attempted_new_version": attempted_new_version,
                }
            )
            continue

        actual_version = state[key]["version"]

        if actual_version != expected_version:
            conflicts.append(
                {
                    "patch_id": patch_id,
                    "key": key,
                    "reason": "version_mismatch",
                    "expected_version": expected_version,
                    "actual_version": actual_version,
                    "attempted_new_version": attempted_new_version,
                }
            )
            continue

        if attempted_new_version <= actual_version:
            conflicts.append(
                {
                    "patch_id": patch_id,
                    "key": key,
                    "reason": "non_monotonic_version",
                    "expected_version": expected_version,
                    "actual_version": actual_version,
                    "attempted_new_version": attempted_new_version,
                }
            )
            continue

        state[key] = {
            "value": patch["value"],
            "version": attempted_new_version,
        }
        applied_patch_ids.append(patch_id)

    return {
        "state": state,
        "applied_patch_ids": applied_patch_ids,
        "conflicts": conflicts,
    }
