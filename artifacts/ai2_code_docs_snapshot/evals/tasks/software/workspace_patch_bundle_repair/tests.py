import copy
import importlib
import sys


BASE_STATE = {
    "alpha": {"value": "A0", "version": 1},
    "beta": {"value": "B0", "version": 5},
}

PATCHES = [
    {"patch_id": "p1", "key": "alpha", "expected_version": 1, "value": "A1", "new_version": 2},
    {"patch_id": "p1", "key": "alpha", "expected_version": 2, "value": "A2", "new_version": 3},
    {"patch_id": "p2", "key": "beta", "expected_version": 4, "value": "B1", "new_version": 6},
    {"patch_id": "p3", "key": "beta", "expected_version": 5, "value": "B1", "new_version": 5},
    {"patch_id": "p4", "key": "gamma", "expected_version": 0, "value": "G1", "new_version": 1},
    {"patch_id": "p5", "key": "beta", "expected_version": 5, "value": "B2", "new_version": 6},
    {"patch_id": "p6", "key": "beta", "expected_version": 6, "value": "B3", "new_version": 7},
]

EXPECTED_RESULT = {
    "state": {
        "alpha": {"value": "A1", "version": 2},
        "beta": {"value": "B3", "version": 7},
    },
    "applied_patch_ids": ["p1", "p5", "p6"],
    "conflicts": [
        {
            "patch_id": "p2",
            "key": "beta",
            "reason": "version_mismatch",
            "expected_version": 4,
            "actual_version": 5,
            "attempted_new_version": 6,
        },
        {
            "patch_id": "p3",
            "key": "beta",
            "reason": "non_monotonic_version",
            "expected_version": 5,
            "actual_version": 5,
            "attempted_new_version": 5,
        },
        {
            "patch_id": "p4",
            "key": "gamma",
            "reason": "missing_key",
            "expected_version": 0,
            "actual_version": None,
            "attempted_new_version": 1,
        },
    ],
}

EXPECTED_REPORT = {
    "applied_count": 3,
    "applied_patch_ids": ["p1", "p5", "p6"],
    "conflict_count": 3,
    "conflict_keys": ["beta", "beta", "gamma"],
    "conflict_reasons": ["version_mismatch", "non_monotonic_version", "missing_key"],
}


def run_tests(workspace_root: str) -> dict:
    failures = []
    sys.path.insert(0, workspace_root)
    try:
        patch_engine = importlib.import_module("pkg.patch_engine")
        reporting = importlib.import_module("pkg.reporting")
        models = importlib.import_module("pkg.models")

        base_state = copy.deepcopy(BASE_STATE)
        patches = copy.deepcopy(PATCHES)
        actual = patch_engine.apply_patches(base_state, patches)
        if actual != EXPECTED_RESULT:
            failures.append(f"apply_patches returned {actual!r}, expected {EXPECTED_RESULT!r}")
        if base_state != BASE_STATE:
            failures.append("apply_patches mutated input base_state")
        if patches != PATCHES:
            failures.append("apply_patches mutated input patches")

        report = reporting.render_conflict_report(actual)
        if report != EXPECTED_REPORT:
            failures.append(f"render_conflict_report returned {report!r}, expected {EXPECTED_REPORT!r}")

        duplicate_conflict = patch_engine.apply_patches(
            {"x": {"value": 1, "version": 1}},
            [
                {"patch_id": "dup", "key": "x", "expected_version": 0, "value": 2, "new_version": 2},
                {"patch_id": "dup", "key": "x", "expected_version": 1, "value": 3, "new_version": 2},
            ],
        )
        duplicate_expected = {
            "state": {"x": {"value": 1, "version": 1}},
            "applied_patch_ids": [],
            "conflicts": [
                {
                    "patch_id": "dup",
                    "key": "x",
                    "reason": "version_mismatch",
                    "expected_version": 0,
                    "actual_version": 1,
                    "attempted_new_version": 2,
                }
            ],
        }
        if duplicate_conflict != duplicate_expected:
            failures.append(
                "duplicate conflicting patch suppression incorrect: "
                f"{duplicate_conflict!r} != {duplicate_expected!r}"
            )

        empty = patch_engine.apply_patches({}, [])
        if empty != {"state": {}, "applied_patch_ids": [], "conflicts": []}:
            failures.append(f"empty input handling incorrect: {empty!r}")
        empty_report = reporting.render_conflict_report(empty)
        if empty_report != {
            "applied_count": 0,
            "applied_patch_ids": [],
            "conflict_count": 0,
            "conflict_keys": [],
            "conflict_reasons": [],
        }:
            failures.append(f"empty report handling incorrect: {empty_report!r}")

        missing_key_conflict = models.build_conflict(
            patch_id="z1",
            key="missing",
            reason="missing_key",
            expected_version=0,
            actual_version=None,
            attempted_new_version=1,
        )
        if missing_key_conflict["actual_version"] is not None:
            failures.append("models.build_conflict did not preserve None actual_version")
        if tuple(models.conflict_signature(missing_key_conflict)) != ("missing", "missing_key"):
            failures.append("models.conflict_signature contract changed")
    finally:
        if sys.path and sys.path[0] == workspace_root:
            sys.path.pop(0)
        for module_name in ["pkg", "pkg.models", "pkg.patch_engine", "pkg.reporting"]:
            sys.modules.pop(module_name, None)

    return {
        "passed": not failures,
        "details": failures or [
            "Workspace patch bundle repair preserves engine semantics and reporting contract across module boundaries"
        ],
    }
