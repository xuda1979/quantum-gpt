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
    marked = "10111"
    n = 5
    r_expected = 4
    p_expected = math.sin((2 * r_expected + 1) * math.asin(1.0 / math.sqrt(1 << n))) ** 2

    # --- analytic iteration count ---
    try:
        r = int(module.iterations_for(n))
        if r != r_expected:
            failures.append(f"iterations={r}, expected {r_expected}")
    except Exception as e:  # noqa: BLE001
        failures.append(f"iterations_for raised: {e}")

    # --- oracle unitary: -1 on |10111>, +1 elsewhere ---
    oracle = None
    try:
        oracle = module.oracle_circuit(marked)
        if oracle.num_qubits != 5:
            failures.append(f"oracle_qubits={oracle.num_qubits}, expected 5")
    except Exception as e:  # noqa: BLE001
        failures.append(f"oracle_circuit raised: {e}")
    if oracle is not None:
        try:
            from qiskit.quantum_info import Operator

            mat = np.asarray(Operator(oracle).data)
            diag = np.diag(mat)
            off = mat - np.diag(diag)
            wrong_offdiag = int(np.sum(np.abs(off) > 1e-9))
            wrong_diag = int(np.sum(np.abs(diag - 1.0) > 1e-9))
            idx = int(marked[::-1], 2)
            if wrong_offdiag != 0:
                failures.append(f"oracle_wrong_entries={wrong_offdiag}, expected 0")
            if wrong_diag != 1:
                failures.append(f"oracle_negated_diag={wrong_diag}, expected 1")
            if abs(complex(diag[idx]) + 1.0) > 1e-9:
                failures.append(f"oracle_marked_sign={complex(diag[idx])}, expected -1.000000")
        except Exception as e:  # noqa: BLE001
            failures.append(f"oracle unitary check raised: {e}")

    # --- diffusion unitary: 2|s><s| - I up to global phase ---
    try:
        diff = module.diffusion_circuit(n)
        from qiskit.quantum_info import Operator

        U = np.asarray(Operator(diff).data)
        s = np.full(1 << n, 1.0 / math.sqrt(1 << n), dtype=complex)
        D = 2.0 * np.outer(s, s.conj()) - np.eye(1 << n, dtype=complex)
        phase = np.trace(U.conj().T @ D) / (1 << n)
        dev = np.max(np.abs(U - phase * D))
        if dev > 1e-9 or abs(abs(phase) - 1.0) > 1e-9:
            failures.append(f"diffusion_dev={dev:.2e}, expected < 1e-9")
    except Exception as e:  # noqa: BLE001
        failures.append(f"diffusion unitary check raised: {e}")

    # --- full circuit + exact success probability ---
    circuit = None
    try:
        circuit = module.grover_circuit(marked)
        if circuit.num_qubits != 5:
            failures.append(f"circuit_qubits={circuit.num_qubits}, expected 5")
    except Exception as e:  # noqa: BLE001
        failures.append(f"grover_circuit raised: {e}")
    p_exact = None
    if circuit is not None:
        try:
            p_exact = float(module.exact_success_probability(circuit, marked))
        except Exception as e:  # noqa: BLE001
            failures.append(f"exact_success_probability raised: {e}")
        if p_exact is not None:
            if abs(p_exact - p_expected) > 1e-6:
                failures.append(f"p_exact={p_exact:.4f}, expected {p_expected:.4f}")
            if p_exact < 0.9:
                failures.append(f"p_exact={p_exact:.4f}, expected >= 0.9000")

    # --- seeded sampling ---
    counts = None
    if circuit is not None:
        try:
            counts = module.sample_counts(circuit, shots=4096, seed=12345)
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
        if share < 0.9:
            failures.append(f"marked_share={share:.4f}, expected >= 0.9000")
        try:
            counts2 = module.sample_counts(circuit, shots=4096, seed=12345)
            if counts2 != counts:
                failures.append("seed_determinism_diff=1, expected 0")
        except Exception as e:  # noqa: BLE001
            failures.append(f"sample_counts determinism raised: {e}")

    # --- end-to-end run ---
    try:
        result = module.run_grover(marked=marked, shots=4096, seed=12345)
        if abs(result.get("p_exact", 0.0) - p_expected) > 1e-6:
            failures.append(f"run_p_exact={result.get('p_exact'):.4f}, expected {p_expected:.4f}")
        if result.get("top_sampled") != marked:
            failures.append(f"run_top_sampled={result.get('top_sampled')}, expected {marked}")
    except Exception as e:  # noqa: BLE001
        failures.append(f"run_grover raised: {e}")

    return {
        "passed": not failures,
        "details": failures
        or [
            "Grover Qiskit 5 qubits marked 10111: r=4, p_exact=0.9992 matches "
            "sin^2((2r+1)asin(1/sqrt(32))), marked state most frequent in "
            "seeded 4096-shot sampling",
        ],
    }
