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
    steps = 3

    # --- shift permutation: valid permutation, correct +1/-1 mapping ---
    perm = None
    try:
        perm = np.asarray(module.shift_permutation(), dtype=complex)
    except Exception as e:  # noqa: BLE001
        failures.append(f"shift_permutation raised: {e}")
    if perm is not None:
        if perm.shape != (8, 8):
            failures.append(f"permutation_shape={perm.shape}, expected 8x8")
        else:
            rows = np.sum(np.abs(perm), axis=1)
            cols = np.sum(np.abs(perm), axis=0)
            bad_rows = int(np.sum(np.abs(rows - 1.0) > 1e-9))
            bad_cols = int(np.sum(np.abs(cols - 1.0) > 1e-9))
            if bad_rows != 0 or bad_cols != 0:
                failures.append(
                    f"permutation_bad_rows={bad_rows} bad_cols={bad_cols}, " "expected 0 0"
                )
            for coin in (0, 1):
                for pos in (0, 2, 3):
                    src = coin * 4 + pos
                    dst = coin * 4 + ((pos + 1) % 4 if coin == 0 else (pos - 1) % 4)
                    if abs(complex(perm[dst, src]) - 1.0) > 1e-9:
                        failures.append(
                            f"shift_mapping[coin={coin},pos={pos}]="
                            f"{complex(perm[dst, src])}, expected 1.000000"
                        )
            dev = float(np.max(np.abs(perm @ perm.conj().T - np.eye(8, dtype=complex))))
            if dev > 1e-12:
                failures.append(f"permutation_unitarity={dev:.3e}, expected <= 1.0e-12")

    # --- walk circuit exists and has 3 qubits ---
    circuit = None
    try:
        circuit = module.walk_circuit(steps)
        if len(circuit.qubits) != 3:
            failures.append(f"circuit_qubits={len(circuit.qubits)}, expected 3")
    except Exception as e:  # noqa: BLE001
        failures.append(f"walk_circuit raised: {e}")

    # --- exact marginal: nonnegative, normalized ---
    marginal = None
    try:
        marginal = np.asarray(module.position_marginal(steps), dtype=float)
    except Exception as e:  # noqa: BLE001
        failures.append(f"position_marginal raised: {e}")
    if marginal is not None:
        if marginal.shape != (4,):
            failures.append(f"marginal_shape={marginal.shape}, expected 4")
        else:
            if np.any(marginal < -1e-9):
                failures.append(f"negative_mass={float(np.min(marginal)):.9f}, expected >= 0.0")
            total = float(np.sum(marginal))
            if abs(total - 1.0) > 1e-9:
                failures.append(f"marginal_total={total:.9f}, expected 1.000000000")

    # --- independent numpy simulation agrees within 1e-12 ---
    numpy_ref = None
    try:
        numpy_ref = np.asarray(module.numpy_marginal(steps), dtype=float)
    except Exception as e:  # noqa: BLE001
        failures.append(f"numpy_marginal raised: {e}")
    if marginal is not None and numpy_ref is not None:
        if numpy_ref.shape == (4,):
            max_diff = float(np.max(np.abs(marginal - numpy_ref)))
            if max_diff > 1e-12:
                failures.append(f"crosscheck_max_diff={max_diff:.3e}, expected <= 1.0e-12")
        else:
            failures.append(f"numpy_marginal_shape={numpy_ref.shape}, expected 4")

    # --- end-to-end run object ---
    try:
        result = module.run_walk(steps=steps)
        if result.get("max_diff", 1.0) > 1e-12:
            failures.append(f"run_max_diff={result.get('max_diff')}, expected <= 1.0e-12")
        if abs(float(result.get("marginal_normalized", 0.0)) - 1.0) > 1e-9:
            failures.append(
                f"run_normalized={result.get('marginal_normalized')}, " "expected 1.000000000"
            )
    except Exception as e:  # noqa: BLE001
        failures.append(f"run_walk raised: {e}")

    return {
        "passed": not failures,
        "details": failures
        or [
            "3-step coined walk on cycle 4: explicit unitary permutation "
            "validated, qiskit marginal matches independent numpy simulation "
            "within 1e-12",
        ],
    }
