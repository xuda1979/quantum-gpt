import importlib.util

from qiskit.quantum_info import Statevector

EDGES = [(0, 1), (0, 2), (0, 3), (1, 2), (2, 3)]


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _cut_ref(bits, edges=EDGES):
    n = 0
    for u, v in edges:
        if ((bits >> u) & 1) != ((bits >> v) & 1):
            n += 1
    return n


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures: list[str] = []

    # --- single declared bit-order function: exact cut values ---
    try:
        c5 = int(module.bitstring_cut(5, EDGES))
        c3 = int(module.bitstring_cut(3, EDGES))
        c0 = int(module.bitstring_cut(0, EDGES))
        c15 = int(module.bitstring_cut(15, EDGES))
    except Exception as e:  # noqa: BLE001
        failures.append(f"bitstring_cut raised: {e}")
        c5 = c3 = c0 = c15 = None
    if c5 is not None:
        if c5 != 4:
            failures.append(f"cut_0101={c5}, expected 4")
        if c3 != 3:
            failures.append(f"cut_0011={c3}, expected 3")
        if c0 != 0 or c15 != 0:
            failures.append("cut_all0_or_all1=nonzero, expected 0/0")
        ok_all = all(int(module.bitstring_cut(b, EDGES)) == _cut_ref(b) for b in range(16))
        if not ok_all:
            failures.append("bitorder_consistency=0, expected 1")

    # --- classical optimum: max cut = 4, achieved by {0101, 1010} ---
    opt = None
    try:
        opt = module.classical_optimum(EDGES)
    except Exception as e:  # noqa: BLE001
        failures.append(f"classical_optimum raised: {e}")
    if opt is not None:
        value, bits = opt
        if value != 4:
            failures.append(f"classical_optimum={value}, expected 4")
        if not (5 in bits and 10 in bits):
            failures.append(f"optimal_bitstrings_present=0, expected {5, 10}")

    # --- probabilities from the circuit sum to one ---
    try:
        qc = module.qaoa_circuit([0.5, 1.0], [0.3, 0.7], EDGES)
        probs = Statevector(qc).probabilities_dict(decimals=15)
    except Exception as e:  # noqa: BLE001
        failures.append(f"qaoa_circuit raised: {e}")
        probs = None
    if probs is not None:
        s = sum(probs.values())
        if abs(s - 1.0) > 1e-9:
            failures.append(f"prob_sum={s:.12f}, expected 1.000000000000")
        # circuit with no parameters = uniform superposition -> expected cut 2.5
        try:
            e0 = float(module.expected_cut([0.0, 0.0], [0.0, 0.0], EDGES))
        except Exception as e:  # noqa: BLE001
            failures.append(f"expected_cut raised: {e}")
            e0 = None
        if e0 is not None and abs(e0 - 2.5) > 1e-6:
            failures.append(f"expected_cut_zero={e0:.9f}, expected 2.500000000")

    # --- expected cut uses the declared bit-order function consistently ---
    if probs is not None:
        try:
            e1 = float(module.expected_cut([0.4, 0.9], [0.2, 0.6], EDGES))
        except Exception as e:  # noqa: BLE001
            failures.append(f"expected_cut(params) raised: {e}")
            e1 = None
        if e1 is not None:
            # harness-side recomputation with the same bit-order convention
            qc1 = module.qaoa_circuit([0.4, 0.9], [0.2, 0.6], EDGES)
            p1 = Statevector(qc1).probabilities_dict(decimals=15)
            ref1 = sum(v * _cut_ref(int(b, 2)) for b, v in p1.items())
            if abs(e1 - ref1) > 1e-6:
                failures.append(f"expected_cut_consistency={e1:.9f}, expected {ref1:.9f}")

    # --- optimization quality: expected cut >= 3.5 of the 4 max cut ---
    # (reference reaches ~3.85; p=1 or truncated-edge landscapes stay < 3.4)
    gamma = beta = None
    try:
        gamma, beta, value, ratio = module.optimize_parameters(EDGES, n_starts=12, seed=0)
    except Exception as e:  # noqa: BLE001
        failures.append(f"optimize_parameters raised: {e}")
        value = None
    if value is not None:
        if value < 3.5:
            failures.append(f"optimized_cut={value:.6f}, expected >= 3.500000")
        if not (0.0 <= float(ratio) <= 1.0 + 1e-9):
            failures.append(f"approximation_ratio={float(ratio):.6f}, expected in [0, 1]")

    # --- seeded sampling of the optimized circuit ---
    if gamma is not None and beta is not None:
        try:
            counts = module.sample_optimized(gamma, beta, shots=4096, seed=42, edges=EDGES)
        except Exception as e:  # noqa: BLE001
            failures.append(f"sample_optimized raised: {e}")
            counts = None
        if counts:
            total = sum(counts.values())
            if total != 4096:
                failures.append(f"sampled_shots={total}, expected 4096")
            mean = sum(_cut_ref(int(b, 2)) * c for b, c in counts.items()) / float(total)
            if abs(mean - float(value)) > 0.05:
                failures.append(
                    f"sampled_mean_cut={mean:.6f}, expected within 0.05 of {float(value):.6f}"
                )

    return {
        "passed": not failures,
        "details": failures
        or [
            "p=2 QAOA on 4-vertex 5-edge MaxCut: exact expected cut from "
            "Statevector probabilities, single bit-order function, "
            "classical optimum 4, optimized expected cut >= 3.5, "
            "probabilities sum to 1, seeded sampling consistent",
        ],
    }
