import importlib.util


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures = []

    # Single-qubit snapshot for outcome 0:
    # rho_hat = 3 * |0><0| - I = [[2, 0], [0, -1]]
    snap = module.clifford_shadow_snapshot(0, 1, 0)
    expected = [[2.0 + 0j, 0j], [0j, -1.0 + 0j]]
    ok = (
        len(snap) == 2
        and abs(snap[0][0] - 2.0) < 1e-12
        and abs(snap[1][1] - (-1.0)) < 1e-12
        and abs(snap[0][1]) < 1e-12
        and abs(snap[1][0]) < 1e-12
    )
    if not ok:
        failures.append(f"snapshot(0, n=1) incorrect: {snap}")

    # Snapshot for outcome 1:
    # rho_hat = 3 * |1><1| - I = [[-1, 0], [0, 2]]
    snap1 = module.clifford_shadow_snapshot(1, 1, 0)
    if not (abs(snap1[0][0] - (-1.0)) < 1e-12 and abs(snap1[1][1] - 2.0) < 1e-12):
        failures.append(f"snapshot(1, n=1) incorrect: {snap1}")

    # 2-qubit snapshot dimension
    snap2 = module.clifford_shadow_snapshot(0, 2, 0)
    if len(snap2) != 4 or any(len(r) != 4 for r in snap2):
        failures.append("2-qubit snapshot should be 4x4")
    # diagonal entry for outcome 0: (d+1)*1 - 1 = 5 - 1 = 4 (d = 2^2 = 4)
    if abs(snap2[0][0] - 4.0) > 1e-12:
        failures.append("snapshot(0, n=2)[0][0] should be 4")
    # other diagonal entries: -1
    for i in (1, 2, 3):
        if abs(snap2[i][i] - (-1.0)) > 1e-12:
            failures.append(f"snapshot(0, n=2)[{i}][{i}] should be -1")
            break

    # Expectation estimator: observable = Z = [[1,0],[0,-1]]
    # For snapshot 0: Tr(Z * snap) = 1*2 + (-1)*(-1) = 3
    Z = [[1.0 + 0j, 0j], [0j, -1.0 + 0j]]
    val = module.shadow_estimate_expectation([snap], Z)
    if abs(val - 3.0) > 1e-9:
        failures.append(f"Tr(Z * snap0) should be 3, got {val}")

    # Average of two opposite snapshots
    avg = module.shadow_estimate_expectation([snap, snap1], Z)
    # snap0 gives 3, snap1 gives Tr(Z * [[-1,0],[0,2]]) = -1 - 2 = -3
    if abs(avg - 0.0) > 1e-9:
        failures.append(f"average of opposite snapshots should be 0, got {avg}")

    # Sample snapshots deterministically
    snaps = module.sample_shadow_snapshots(5, 1, seed=42)
    if len(snaps) != 5:
        failures.append("sample_shadow_snapshots should return requested count")
    if any(len(s) != 2 or len(s[0]) != 2 for s in snaps):
        failures.append("each sampled snapshot should be 2x2")

    # Invalid inputs
    try:
        module.clifford_shadow_snapshot(2, 1, 0)
        failures.append("should raise on outcome >= 2^n")
    except ValueError:
        pass
    try:
        module.shadow_estimate_expectation([], Z)
        failures.append("should raise on empty snapshots")
    except ValueError:
        pass

    return {
        "passed": not failures,
        "details": failures or ["Classical shadow tomography estimator correct"],
    }
