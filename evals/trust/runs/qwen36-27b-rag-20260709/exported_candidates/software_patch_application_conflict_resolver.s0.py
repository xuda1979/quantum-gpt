def apply_patches(base_state: dict[str, dict], patches: list[dict]) -> dict:
    """Apply ordered key/value patches with duplicate suppression and conflict reporting.

    Input:
      base_state: {key: {"value": object, "version": int}}
      patches: list of {
          "patch_id": str,
          "key": str,
          "expected_version": int,
          "value": object,
          "new_version": int,
      }

    Output:
      {
        "state": {key: {"value": object, "version": int}},
        "applied_patch_ids": [patch ids in first-application order],
        "conflicts": [
            {
              "patch_id": str,
              "key": str,
              "reason": "missing_key" | "version_mismatch" | "non_monotonic_version",
              "expected_version": int,
              "actual_version": int | None,
              "attempted_new_version": int,
            }, ...
        ],
      }

    Rules:
    - Do not mutate inputs.
    - Ignore duplicate patch_ids after their first occurrence, whether the first occurrence applied cleanly or conflicted.
    - A patch applies only if the key exists, expected_version matches the current version, and new_version > current version.
    - Conflicts must be reported in encounter order.
    - Output state keys and nested records should be ordinary dicts.
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
