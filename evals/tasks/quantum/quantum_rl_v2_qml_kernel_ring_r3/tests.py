import importlib.util

import numpy as np


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures: list[str] = []

    # --- deterministic data ---
    try:
        X = module.generate_data(seed=42)
        if X.shape != (8, 3):
            failures.append(f"data_shape={X.shape}, expected (8, 3)")
        X2 = module.generate_data(seed=42)
        if not np.array_equal(X, X2):
            failures.append("data_determinism_diff=1, expected 0")
        if np.allclose(X[0], 0.0):
            failures.append("data_entries_zero=1, expected 0 (points must vary)")
    except Exception as e:  # noqa: BLE001
        failures.append(f"generate_data raised: {e}")

    # --- feature map: 3 qubits, one CZ per unique ring edge ---
    try:
        import pennylane as qml

        tape = qml.tape.make_qscript(module.feature_map)(X[0])
        czs = [op for op in tape.operations if op.name == "CZ"]
        edges = [tuple(op.wires.labels) for op in czs]
        if len(czs) != 3:
            failures.append(f"cz_edges={len(czs)}, expected 3")
        if sorted(edges) != [(0, 1), (1, 2), (2, 0)]:
            failures.append(f"cz_edge_set={sorted(edges)}, expected [(0,1),(1,2),(2,0)]")
        nq = max(w for op in tape.operations for w in op.wires) + 1
        if nq != 3:
            failures.append(f"map_qubits={nq}, expected 3")
    except Exception as e:  # noqa: BLE001
        failures.append(f"feature map structure check raised: {e}")

    # --- kernel matrix properties ---
    K = None
    try:
        K = np.asarray(module.kernel_matrix(X))
        if K.shape != (8, 8):
            failures.append(f"kernel_shape={K.shape}, expected (8, 8)")
    except Exception as e:  # noqa: BLE001
        failures.append(f"kernel_matrix raised: {e}")
    if K is not None:
        sym_dev = float(np.max(np.abs(K - K.T)))
        if sym_dev > 1e-12:
            failures.append(f"symmetry_dev={sym_dev:.2e}, expected < 1e-12")
        diag_dev = float(np.max(np.abs(np.diag(K) - 1.0)))
        if diag_dev > 1e-12:
            failures.append(f"diagonal_dev={diag_dev:.2e}, expected < 1e-12")
        if K.min() < -1e-12 or K.max() > 1.0 + 1e-12:
            failures.append(f"entry_range=({K.min():.4f}, {K.max():.4f}), expected within [0, 1]")
        eig = np.linalg.eigvalsh(K)
        if eig[0] < -1e-10:
            failures.append(f"min_eigval={eig[0]:.2e}, expected >= -1e-10")
        # specific numeric entries for this deterministic data
        if abs(K[0, 1] - 0.3280796195515884) > 1e-9:
            failures.append(f"kernel_01={K[0, 1]:.4f}, expected 0.3281")
        if abs(K[1, 2] - 0.3443233565564805) > 1e-9:
            failures.append(f"kernel_12={K[1, 2]:.4f}, expected 0.3443")
        if abs(K[0, 2] - 0.8814421504734086) > 1e-9:
            failures.append(f"kernel_02={K[0, 2]:.4f}, expected 0.8814")

    # --- cross-check from explicit state vectors ---
    try:
        cross = float(module.cross_check_entry(0, 1, X))
        if abs(cross - K[0, 1]) > 1e-9:
            failures.append(f"cross_dev={abs(cross - K[0, 1]):.2e}, expected < 1e-9")
    except Exception as e:  # noqa: BLE001
        failures.append(f"cross_check_entry raised: {e}")

    # --- end-to-end run ---
    try:
        result = module.run_kernel(seed=42)
        if result.get("min_eigval", -1.0) < -1e-10:
            failures.append(f"run_min_eigval={result.get('min_eigval')}, expected >= -1e-10")
        if result.get("cross_dev", 1.0) > 1e-9:
            failures.append(f"run_cross_dev={result.get('cross_dev')}, expected < 1e-9")
    except Exception as e:  # noqa: BLE001
        failures.append(f"run_kernel raised: {e}")

    return {
        "passed": not failures,
        "details": failures
        or [
            "QML kernel 8 points in R3: RY angle encoding + one CZ per ring edge, "
            "K symmetric (dev 0), unit diagonal, entries in [0,1], min eigval "
            "0.0033 >= -1e-10, cross-check dev 1e-16, K[0,1]=0.3281",
        ],
    }
