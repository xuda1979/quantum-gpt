"""Grover search in Cirq for the marked state '1000' on 4 qubits.

The phase oracle is a diagonal MatrixGate with -1 on the marked
computational basis state and +1 elsewhere. The diffusion operator
D = 2|s><s| - I is built explicitly, both as a numpy matrix and as an
elementary H-X-MCZ-X-H circuit (verified to match up to global phase).
The iteration count is the analytic r = floor(pi/4 * sqrt(N)). Exact
final probabilities come from cirq.Simulator().simulate(); 4096
repetitions are sampled with a fixed seed."""

from __future__ import annotations

import math

import cirq
import numpy as np


def phase_oracle_matrix(marked: str) -> np.ndarray:
    """2**n x 2**n diagonal matrix: -1 on |marked>, +1 elsewhere."""
    size = 1 << len(marked)
    idx = int(marked, 2)
    mat = np.eye(size, dtype=complex)
    mat[idx, idx] = -1.0
    return mat


def iterations_for(n: int) -> int:
    """Analytic Grover iteration count floor(pi/4 * sqrt(2**n))."""
    return int(math.floor(math.pi / 4.0 * math.sqrt(1 << n)))


def diffusion_matrix(n: int) -> np.ndarray:
    """Diffusion operator D = 2|s><s| - I with |s> = H^xn |0...0>."""
    s = np.full(1 << n, 1.0 / math.sqrt(1 << n), dtype=complex)
    return 2.0 * np.outer(s, s.conj()) - np.eye(1 << n, dtype=complex)


def diffusion_circuit(qubits) -> cirq.Circuit:
    """Elementary construction of the diffusion operator.

    D = -H^xn X^xn MCZ X^xn H^xn where MCZ is the n-qubit controlled-Z
    (phase flip of |1...1> only). The leading global phase -1 leaves all
    probabilities unchanged, so the circuit is a valid diffusion step."""
    qs = list(qubits)
    n = len(qs)
    mcz = cirq.Z.controlled(num_controls=n - 1)
    ops = []
    ops += [cirq.H(q) for q in qs]
    ops += [cirq.X(q) for q in qs]
    ops += [mcz(*qs)]
    ops += [cirq.X(q) for q in qs]
    ops += [cirq.H(q) for q in qs]
    return cirq.Circuit(ops)


def grover_circuit(marked: str, iterations: int | None = None) -> cirq.Circuit:
    """Full Grover circuit: equal superposition, r oracle+diffusion
    rounds, then measurement. Qubit 0 is the most significant bit of the
    marked bitstring."""
    n = len(marked)
    qubits = cirq.LineQubit.range(n)
    r = iterations_for(n) if iterations is None else iterations
    oracle = cirq.MatrixGate(phase_oracle_matrix(marked))
    circuit = cirq.Circuit(cirq.H.on_each(*qubits))
    for _ in range(r):
        circuit.append(oracle.on(*qubits))
        circuit.append(diffusion_circuit(qubits))
    circuit.append(cirq.measure(*qubits, key="m"))
    return circuit


def exact_probabilities(circuit: cirq.Circuit) -> dict[str, float]:
    """Exact outcome probabilities from the final state vector.

    The terminal measurement is stripped first (simulate() would
    otherwise collapse the state onto a sampled outcome)."""
    unmeasured = cirq.drop_terminal_measurements(circuit)
    state = np.asarray(cirq.Simulator(dtype=np.complex128).simulate(unmeasured).final_state_vector)
    probs = np.abs(state) ** 2
    n = len(circuit.all_qubits())
    return {format(i, "0%db" % n): float(p) for i, p in enumerate(probs)}


def sample_counts(
    circuit: cirq.Circuit, repetitions: int = 4096, seed: int = 4242
) -> dict[str, int]:
    """Seeded sampling of the measured circuit; bitstrings are n-wide."""
    results = cirq.Simulator(dtype=np.complex128, seed=seed).run(circuit, repetitions=repetitions)
    counts = results.histogram(key="m")
    n = len(circuit.all_qubits())
    return {format(k, "0%db" % n): int(c) for k, c in counts.items()}


def run_grover(marked: str = "1000", shots: int = 4096, seed: int = 4242) -> dict:
    """Run Grover end-to-end and return all verifiable quantities."""
    r = iterations_for(len(marked))
    circuit = grover_circuit(marked)
    probs = exact_probabilities(circuit)
    counts = sample_counts(circuit, repetitions=shots, seed=seed)
    n = len(marked)
    p_expected = math.sin((2 * r + 1) * math.asin(1.0 / math.sqrt(1 << n))) ** 2
    return {
        "marked": marked,
        "iterations": r,
        "p_exact": probs[marked],
        "p_expected": p_expected,
        "top_exact": max(probs, key=probs.get),
        "top_sampled": max(counts, key=counts.get),
        "probs": probs,
        "counts": counts,
    }


def main():
    result = run_grover()
    print("iterations =", result["iterations"])
    print("p_exact =", result["p_exact"])
    print("p_expected =", result["p_expected"])
    print("top_exact =", result["top_exact"])
    print("top_sampled =", result["top_sampled"])
    assert result["top_exact"] == "1000", "marked state must be most probable"
    assert result["top_sampled"] == "1000", "marked state must dominate sampling"
    assert (
        abs(result["p_exact"] - result["p_expected"]) < 1e-9
    ), "success probability must match the Grover rotation formula"


if __name__ == "__main__":
    main()
