"""Grover search from elementary Qiskit gates for the 3-qubit marked
computational-basis state '101': explicit phase oracle and diffusion
operator, floor(pi/4*sqrt(2**3)) iterations, exact success probability
before measurement matched against sin^2((2r+1)asin(1/sqrt(N))), and a
seeded 4096-shot sample."""

import math

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

MARKED = "101"  # |q2 q1 q0> with q2 the most significant bit
N = 8


def marked_state():
    return MARKED


def phase_oracle():
    """Phase oracle for |101>: X on q1, CCZ(0,1,2), X on q1 (flips the
    phase of exactly the marked state)."""
    qc = QuantumCircuit(3, name="oracle")
    qc.x(1)
    qc.h(2)
    qc.ccx(0, 1, 2)
    qc.h(2)
    qc.x(1)
    return qc


def diffusion():
    """Diffusion operator D = H^3 X^3 CCZ X^3 H^3 (2|s><s| - I up to the
    standard global phase)."""
    qc = QuantumCircuit(3, name="diffusion")
    qc.h(range(3))
    qc.x(range(3))
    qc.h(2)
    qc.ccx(0, 1, 2)
    qc.h(2)
    qc.x(range(3))
    qc.h(range(3))
    return qc


def optimal_iterations(n_qubits=3):
    """floor(pi/4 * sqrt(2**n_qubits))."""
    return int(math.floor(math.pi / 4.0 * math.sqrt(2**n_qubits)))


def grover_circuit(measure=True):
    """Equal superposition, then (oracle + diffusion) repeated r times,
    optionally with a terminal measurement of all qubits."""
    r = optimal_iterations()
    qc = QuantumCircuit(3, 3)
    qc.h(range(3))
    for _ in range(r):
        qc.compose(phase_oracle(), inplace=True)
        qc.compose(diffusion(), inplace=True)
    if measure:
        qc.measure(range(3), range(3))
    return qc


def exact_success_probability():
    """|amp|^2 of the marked state before measurement."""
    sv = np.asarray(Statevector(grover_circuit(measure=False)))
    return float(np.abs(sv[int(MARKED, 2)]) ** 2)


def grover_formula(r=None):
    """Analytic success probability sin^2((2r+1) asin(1/sqrt(N)))."""
    if r is None:
        r = optimal_iterations()
    return math.sin((2 * r + 1) * math.asin(1.0 / math.sqrt(N))) ** 2


def sample_counts(shots=4096, seed=1234):
    """Seeded AerSimulator sampling; counts keyed by 3-bit bitstrings."""
    backend = AerSimulator(seed_simulator=seed)
    return backend.run(grover_circuit(), shots=shots).result().get_counts()


def run_grover(shots=4096, seed=1234):
    """Full Grover verification."""
    r = optimal_iterations()
    p_exact = exact_success_probability()
    p_formula = grover_formula(r)
    counts = sample_counts(shots, seed)
    most_frequent = max(counts, key=counts.get)
    share = counts.get(MARKED, 0) / float(shots)
    return {
        "marked": MARKED,
        "iterations": r,
        "p_exact": p_exact,
        "p_formula": p_formula,
        "most_frequent": most_frequent,
        "marked_share": share,
    }


def main():
    result = run_grover()
    print("iterations =", result["iterations"])
    print("p_exact =", result["p_exact"])
    print("p_formula =", result["p_formula"])
    print("most_frequent =", result["most_frequent"])
    print("marked share =", result["marked_share"])
    assert (
        abs(result["p_exact"] - result["p_formula"]) < 1e-9
    ), "exact probability must match the Grover rotation formula"
    assert result["most_frequent"] == MARKED, "marked state must dominate"
    assert result["marked_share"] > 0.9, "sampled share must exceed 0.9"


if __name__ == "__main__":
    main()
