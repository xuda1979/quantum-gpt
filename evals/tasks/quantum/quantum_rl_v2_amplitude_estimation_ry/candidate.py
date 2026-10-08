"""Canonical amplitude estimation from scratch in Qiskit.

A = RY(0.6) prepares |psi> = cos(0.3)|0> + sin(0.3)|1>, so the
amplitude of the good state |1> is a = sin^2(0.3). The Grover operator
Q = -A S0 A^dagger S_chi (S0 = I - 2|0><0|, S_chi = I - 2|1><1|) has
eigenvalues e^(+-2i theta) with theta = asin(sqrt(a)); QPE on Q with
3 evaluation qubits yields two symmetric phase peaks j and 2^m - j,
both mapped to a = sin^2(pi * j / 2^m). The amplitude error is asserted
to stay below pi/2^3, the conservative bound from the phase-grid
spacing."""

from __future__ import annotations

import math

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator


def grover_operator(angle: float) -> np.ndarray:
    """Q = -A S0 A^dagger S_chi as a 2x2 matrix (A = RY(angle))."""
    a = angle / 2.0
    A = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]], dtype=complex)
    S0 = np.array([[-1.0, 0.0], [0.0, 1.0]], dtype=complex)  # I - 2|0><0|
    S_chi = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)  # I - 2|1><1|
    return -A @ S0 @ A.conj().T @ S_chi


def prepare_state_gate(angle: float) -> UnitaryGate:
    """Gate for A = RY(angle) applied to the target qubit."""
    a = angle / 2.0
    A = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]], dtype=complex)
    return UnitaryGate(A, label="A_ry")


def qpe_circuit(n_eval: int = 3, angle: float = 0.6) -> QuantumCircuit:
    """QPE on Q with n_eval counting qubits and |psi> = A|0> on the
    target qubit. Controlled-Q^(2^k) gates are appended with counting
    qubit k as control; the inverse QFT is the manual ladder + SWAP
    network (qiskit convention, q0 least significant)."""
    qc = QuantumCircuit(n_eval + 1, n_eval)
    # A = RY(angle) directly (no UnitaryGate synthesis: its decomposition
    # consumes an unseeded RNG, so transpiled structure varies across
    # processes and breaks the seed_determinism check).
    qc.ry(angle, n_eval)
    qc.h(range(n_eval))
    # Controlled-Q^(2^k): for A = RY(angle), Q = -A S0 A^dag S_chi equals the
    # plane rotation exp(-i*angle*Y), so Q^(2^k) = exp(-i*2^k*angle*Y) =
    # qiskit RY(2 * 2^k * angle) (qiskit's RY(theta) = exp(-i*theta*Y/2)).
    # A single CRY per control — a primitive that transpiles
    # deterministically (no UnitaryGate synthesis, whose decomposition
    # consumes an unseeded RNG and breaks the seed_determinism check).
    for k in range(n_eval):
        qc.cry(2.0 * (1 << k) * angle, k, n_eval)
    for i in range(n_eval - 1, -1, -1):
        for j in range(n_eval - 1, i, -1):
            qc.cp(-math.pi / 2.0 ** (j - i), j, i)
        qc.h(i)
    for i in range(n_eval // 2):
        qc.swap(i, n_eval - 1 - i)
    qc.measure(range(n_eval), range(n_eval))
    return qc


def phase_peaks(counts: dict[str, int], n_eval: int) -> list[tuple[int, float]]:
    """The dominant peak j and its symmetric partner m - j, both mapped
    to (j, a_est). Both eigenvalues of Q produce the same amplitude."""
    m = 1 << n_eval
    j1 = max(counts, key=counts.get)
    j1 = int(j1, 2)
    j2 = m - j1 if (m - j1) in {int(k, 2) for k in counts} else None
    peaks = [(j1, math.sin(math.pi * j1 / m) ** 2)]
    if j2 is not None:
        peaks.append((j2, math.sin(math.pi * j2 / m) ** 2))
    return peaks


def estimate_amplitude(j: int, n_eval: int) -> float:
    """a = sin^2(pi * j / 2^n_eval) from a phase peak."""
    return math.sin(math.pi * j / (1 << n_eval)) ** 2


def run_ae(n_eval: int = 3, angle: float = 0.6, shots: int = 4096, seed: int = 7) -> dict:
    """Run canonical amplitude estimation end-to-end."""
    a_true = math.sin(angle / 2.0) ** 2
    circuit = qpe_circuit(n_eval=n_eval, angle=angle)
    sim = AerSimulator(seed_simulator=seed)
    # seed_transpiler pins layout/synthesis randomness; without it two calls
    # with the same seed can transpile to structurally different circuits and
    # sample different counts (seed_determinism check).
    counts = (
        sim.run(transpile(circuit, backend=sim, seed_transpiler=seed), shots=shots)
        .result()
        .get_counts()
    )
    counts = {key: int(c) for key, c in counts.items()}
    peaks = phase_peaks(counts, n_eval)
    a_est = peaks[0][1] if peaks else 0.0
    return {
        "a_true": a_true,
        "a_est": a_est,
        "amplitude_error": abs(a_est - a_true),
        "bound": math.pi / (1 << n_eval),
        "peaks": peaks,
        "counts": counts,
    }


def main():
    result = run_ae()
    print("a_true =", result["a_true"])
    print("peaks =", result["peaks"])
    print("a_est =", result["a_est"])
    print("amplitude_error =", result["amplitude_error"])
    print("bound =", result["bound"])
    assert (
        result["amplitude_error"] <= result["bound"]
    ), "amplitude error must stay below the phase-grid bound pi/2^3"


if __name__ == "__main__":
    main()
