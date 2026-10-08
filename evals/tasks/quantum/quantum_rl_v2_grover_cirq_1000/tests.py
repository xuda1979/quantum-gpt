import importlib.util
import math


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures: list[str] = []
    marked = "1000"
    n = 4
    r_expected = 3
    p_expected = math.sin((2 * r_expected + 1) * math.asin(1.0 / math.sqrt(1 << n))) ** 2

    # --- phase oracle matrix: -1 exactly on |1000>, +1 elsewhere ---
    try:
        mat = module.phase_oracle_matrix(marked)
        import numpy as np

        if mat is None or getattr(mat, "shape", ()) != (16, 16):
            failures.append(f"oracle_shape={getattr(mat, 'shape', None)}, expected 16x16")
        else:
            diag = np.diag(mat)
            off = mat - np.diag(diag)
            wrong_offdiag = int(np.sum(np.abs(off) != 0.0))
            wrong_diag = int(np.sum(diag != 1.0))
            idx = int(marked, 2)
            if abs(complex(mat[idx, idx]) + 1.0) > 1e-12:
                failures.append(f"oracle_marked_sign={complex(mat[idx, idx])}, expected -1.000000")
            if wrong_offdiag != 0:
                failures.append(f"oracle_wrong_entries={wrong_offdiag}, expected 0")
            if wrong_diag != 1:
                failures.append(f"oracle_negated_diag={wrong_diag}, expected 1")
    except Exception as e:  # noqa: BLE001
        failures.append(f"phase_oracle_matrix raised: {e}")

    # --- analytic iteration count ---
    try:
        r = int(module.iterations_for(n))
        if r != r_expected:
            failures.append(f"iterations={r}, expected {r_expected}")
    except Exception as e:  # noqa: BLE001
        failures.append(f"iterations_for raised: {e}")

    # --- circuit structure ---
    circuit = None
    try:
        circuit = module.grover_circuit(marked)
        if len(circuit.all_qubits()) != 4:
            failures.append(f"circuit_qubits={len(circuit.all_qubits())}, expected 4")
    except Exception as e:  # noqa: BLE001
        failures.append(f"grover_circuit raised: {e}")

    # --- exact success probability matches the Grover rotation formula ---
    probs = None
    if circuit is not None:
        try:
            probs = module.exact_probabilities(circuit)
        except Exception as e:  # noqa: BLE001
            failures.append(f"exact_probabilities raised: {e}")
    if probs:
        p = probs.get(marked, 0.0)
        if abs(p - p_expected) > 1e-6:
            failures.append(f"p_exact={p:.4f}, expected {p_expected:.4f}")
        top = max(probs, key=probs.get)
        if top != marked:
            failures.append(f"top_exact={top}, expected {marked}")
        total = sum(probs.values())
        if abs(total - 1.0) > 1e-6:
            failures.append(f"prob_total={total:.6f}, expected 1.000000")

    # --- seeded sampling: marked state most frequent, full shot count ---
    counts = None
    if circuit is not None:
        try:
            counts = module.sample_counts(circuit, repetitions=4096, seed=4242)
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

    # --- determinism: same seed reproduces the same counts ---
    if circuit is not None:
        try:
            counts2 = module.sample_counts(circuit, repetitions=4096, seed=4242)
            if counts2 != counts:
                failures.append("seed_determinism_diff=1, expected 0")
        except Exception as e:  # noqa: BLE001
            failures.append(f"sample_counts determinism raised: {e}")

    # --- end-to-end run object ---
    try:
        result = module.run_grover(marked=marked, shots=4096, seed=4242)
        if result.get("p_exact") is not None and abs(result["p_exact"] - p_expected) > 1e-6:
            failures.append(f"run_p_exact={result['p_exact']:.4f}, expected {p_expected:.4f}")
        if result.get("top_sampled") != marked:
            failures.append(f"run_top_sampled={result.get('top_sampled')}, expected {marked}")
    except Exception as e:  # noqa: BLE001
        failures.append(f"run_grover raised: {e}")

    return {
        "passed": not failures,
        "details": failures
        or [
            "Grover Cirq 4 qubits marked 1000: r=3, p_exact=0.9613 matches "
            "sin^2((2r+1)asin(1/4)), marked state most probable in exact and "
            "seeded 4096-shot sampling",
        ],
    }
