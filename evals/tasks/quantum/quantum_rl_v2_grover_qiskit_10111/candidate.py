"""Grover search from elementary Qiskit gates for the 5-qubit marked
computational-basis state '10111'.

The phase oracle is built from X gates on the zero bits plus a
multi-controlled Z implemented as H + multi-controlled-X + H (all
elementary gates). The diffusion operator D = 2|s><s| - I is built
explicitly as H^xn X^xn MCZ X^xn H^xn. The iteration count is the
analytic r = floor(pi/4 * sqrt(2**5)) = 4. The exact success
probability is computed from the Statevector before measurement and
must match sin^2((2r+1)asin(1/sqrt(N))); 4096 shots are sampled with a
fixed seed."""

from __future__ import annotations

import math

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator


def iterations_for(n: int) -> int:
    """Analytic Grover iteration count floor(pi/4 * sqrt(2**n))."""
    return int(math.floor(math.pi / 4.0 * math.sqrt(1 << n)))


def _mcz(qc: QuantumCircuit, qubits) -> None:
    """Multi-controlled Z on all given qubits (elementary H-MCX-H)."""
    controls = list(qubits[:-1])
    target = qubits[-1]
    qc.h(target)
    qc.mcx(controls, target)
    qc.h(target)


def oracle_circuit(marked: str) -> QuantumCircuit:
    """Phase oracle: -1 on |marked>, +1 elsewhere (elementary gates)."""
    n = len(marked)
    qc = QuantumCircuit(n)
    qubits = list(range(n))
    for i, bit in enumerate(marked):
        if bit == "0":
            qc.x(i)
    _mcz(qc, qubits)
    for i, bit in enumerate(marked):
        if bit == "0":
            qc.x(i)
    return qc


def diffusion_circuit(n: int) -> QuantumCircuit:
    """Diffusion operator D = 2|s><s| - I from elementary H, X, MCZ."""
    qc = QuantumCircuit(n)
    qubits = list(range(n))
    qc.h(qubits)
    qc.x(qubits)
    _mcz(qc, qubits)
    qc.x(qubits)
    qc.h(qubits)
    return qc


def grover_circuit(marked: str, iterations: int | None = None) -> QuantumCircuit:
    """Full Grover circuit: superposition, r oracle+diffusion rounds,
    measurement of all qubits (qiskit little-endian key order)."""
    n = len(marked)
    r = iterations_for(n) if iterations is None else iterations
    qc = QuantumCircuit(n, n)
    qc.h(range(n))
    for _ in range(r):
        qc.compose(oracle_circuit(marked), inplace=True)
        qc.compose(diffusion_circuit(n), inplace=True)
    qc.measure(range(n), range(n))
    return qc


def exact_success_probability(circuit: QuantumCircuit, marked: str) -> float:
    """Exact |<marked|psi>|^2 from the pre-measurement state vector.

    Statevector indices are little-endian, so the marked MSB-first
    bitstring is reversed before indexing."""
    idx = int(marked[::-1], 2)
    unmeasured = circuit.remove_final_measurements(inplace=False)
    sv = Statevector(unmeasured)
    return abs(sv.data[idx]) ** 2


def sample_counts(circuit: QuantumCircuit, shots: int = 4096, seed: int = 12345) -> dict[str, int]:
    """Seeded Aer sampling; keys normalized to MSB-first bitstrings."""
    counts = AerSimulator(seed_simulator=seed).run(circuit, shots=shots).result().get_counts()
    return {key[::-1]: int(count) for key, count in counts.items()}


def run_grover(marked: str = "10111", shots: int = 4096, seed: int = 12345) -> dict:
    """Run Grover end-to-end; returns probabilities, counts, checks."""
    n = len(marked)
    r = iterations_for(n)
    circuit = grover_circuit(marked)
    p_exact = exact_success_probability(circuit, marked)
    counts = sample_counts(circuit, shots=shots, seed=seed)
    p_expected = math.sin((2 * r + 1) * math.asin(1.0 / math.sqrt(1 << n))) ** 2
    return {
        "marked": marked,
        "iterations": r,
        "p_exact": p_exact,
        "p_expected": p_expected,
        "top_sampled": max(counts, key=counts.get),
        "counts": counts,
    }


def main():
    result = run_grover()
    print("iterations =", result["iterations"])
    print("p_exact =", result["p_exact"])
    print("p_expected =", result["p_expected"])
    print("top_sampled =", result["top_sampled"])
    assert result["top_sampled"] == "10111", "marked state must be most frequent"
    assert (
        abs(result["p_exact"] - result["p_expected"]) < 1e-9
    ), "success probability must match the Grover rotation formula"


if __name__ == "__main__":
    main()
