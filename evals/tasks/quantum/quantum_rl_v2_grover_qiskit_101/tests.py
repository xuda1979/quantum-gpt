import importlib.util
import math

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
    marked = "101"
    n = 3
    r_expected = 2
    p_expected = math.sin((2 * r_expected + 1) * math.asin(1.0 / math.sqrt(1 << n))) ** 2

    # --- phase oracle: -1 exactly on |101> ---
    try:
        from qiskit.quantum_info import Operator

        oracle = np.asarray(Operator(module.phase_oracle()))
        if oracle.shape != (8, 8):
            failures.append(f"oracle_shape={oracle.shape}, expected 8x8")
        else:
            diag = np.diag(oracle)
            off = oracle - np.diag(diag)
            wrong_offdiag = int(np.sum(np.abs(off) > 1e-12))
            wrong_diag = int(np.sum(np.abs(diag - 1.0) > 1e-12))
            if abs(complex(diag[int(marked, 2)]) + 1.0) > 1e-12:
                failures.append(
                    f"oracle_marked_sign={complex(diag[int(marked, 2)])}, " "expected -1.000000"
                )
            if wrong_offdiag != 0:
                failures.append(f"oracle_wrong_entries={wrong_offdiag}, expected 0")
            if wrong_diag != 1:
                failures.append(f"oracle_negated_diag={wrong_diag}, expected 1")
    except Exception as e:  # noqa: BLE001
        failures.append(f"phase_oracle raised: {e}")

    # --- diffusion operator: D = 2|s><s| - I ---
    try:
        from qiskit.quantum_info import Operator

        d = np.asarray(Operator(module.diffusion()))
        if d.shape != (8, 8):
            failures.append(f"diffusion_shape={d.shape}, expected 8x8")
        else:
            # the elementary H-X-CCZ-X-H construction yields the diffusion up
            # to a global phase; compare entrywise absolute values
            s = np.full(8, 1.0 / math.sqrt(8))
            expected_d = 2.0 * np.outer(s, s) - np.eye(8)
            diff = float(np.max(np.abs(np.abs(d) - np.abs(expected_d))))
            if diff > 1e-9:
                failures.append(f"diffusion_matrix_diff={diff:.3e}, expected <= 1.0e-9")
    except Exception as e:  # noqa: BLE001
        failures.append(f"diffusion raised: {e}")

    # --- analytic iteration count ---
    try:
        r = int(module.optimal_iterations(n))
        if r != r_expected:
            failures.append(f"iterations={r}, expected {r_expected}")
    except Exception as e:  # noqa: BLE001
        failures.append(f"optimal_iterations raised: {e}")

    # --- exact success probability matches the rotation formula ---
    p_exact = None
    try:
        p_exact = float(module.exact_success_probability())
    except Exception as e:  # noqa: BLE001
        failures.append(f"exact_success_probability raised: {e}")
    if p_exact is None:
        failures.append("exact_marked_probability=0.000000, expected >= 0.900000")
    else:
        if abs(p_exact - p_expected) > 1e-9:
            failures.append(
                f"formula_deviation={abs(p_exact - p_expected):.9f}, " "expected <= 0.000000001"
            )
        if p_exact < 0.90:
            failures.append(f"exact_marked_probability={p_exact:.6f}, expected >= 0.900000")

    # --- seeded sampling: marked state most frequent ---
    counts = None
    try:
        counts = module.sample_counts(shots=4096, seed=1234)
    except Exception as e:  # noqa: BLE001
        failures.append(f"sample_counts raised: {e}")
    if counts:
        total = sum(counts.values())
        if total != 4096:
            failures.append(f"sampled_shots={total}, expected 4096")
        top = max(counts, key=counts.get)
        if top != marked:
            failures.append(f"top_sampled={top}, expected {marked}")
        share = counts.get(marked, 0) / float(total)
        if share < 0.90:
            failures.append(f"marked_share={share:.4f}, expected >= 0.9000")

    # --- end-to-end run object ---
    try:
        result = module.run_grover(shots=4096, seed=1234)
        if result.get("most_frequent") != marked:
            failures.append(f"run_top_sampled={result.get('most_frequent')}, expected {marked}")
        if abs(float(result.get("p_exact", 0.0)) - p_expected) > 1e-9:
            failures.append(f"run_p_exact={result.get('p_exact')}, expected {p_expected:.9f}")
    except Exception as e:  # noqa: BLE001
        failures.append(f"run_grover raised: {e}")

    return {
        "passed": not failures,
        "details": failures
        or [
            "Grover qiskit 3 qubits marked 101: r=2, p_exact=0.9453 matches "
            "sin^2((2r+1)asin(1/sqrt(8))), marked state most frequent in the "
            "seeded 4096-shot sample",
        ],
    }
