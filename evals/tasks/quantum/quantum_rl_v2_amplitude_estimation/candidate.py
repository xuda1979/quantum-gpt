"""Canonical amplitude estimation from scratch in Qiskit: A = RY(0.7) with 4
evaluation (counting) qubits. Q = -A S0 A^dag S_chi for the good state |1>
is built as a 1-qubit circuit, QPE is run on Q with the input state
A|0>, the two symmetric phase peaks are mapped to the amplitude
a = sin(pi * phi) = sin(0.35), and the amplitude error is bounded by the
conservative phase-grid bound pi / 2**4."""

import math

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

N_EVAL = 4
THETA = 0.35  # A=RY(0.7) gives a = sin(0.35)


def amplitude_operator():
    """The amplitude operator A = RY(0.7) on one qubit: A|0> = cos(0.35)|0> +
    sin(0.35)|1>, so the good state |1> has amplitude a = sin(0.35)."""
    qc = QuantumCircuit(1, name="A")
    qc.ry(0.7, 0)
    return qc


def zero_reflection():
    """S0 = 2|0><0| - I = Z (up to global phase)."""
    qc = QuantumCircuit(1, name="S0")
    qc.z(0)
    return qc


def chi_reflection():
    """S_chi: phase flip of the good state |1> only = Z."""
    qc = QuantumCircuit(1, name="S_chi")
    qc.z(0)
    return qc


def q_operator():
    """Q = -A S0 A^dag S_chi as a 1-qubit circuit (the global -1 phase is
    irrelevant for the phase estimation)."""
    qc = QuantumCircuit(1, name="Q")
    qc.compose(amplitude_operator(), inplace=True)
    qc.compose(zero_reflection(), inplace=True)
    qc.ry(-0.7, 0)  # A^dag = RY(-0.7)
    qc.compose(chi_reflection(), inplace=True)
    return qc


def _q_matrix():
    """Explicit 2x2 matrix of Q = Z RY(-0.7) Z RY(0.7) (global -1 ignored)."""
    ry = lambda t: np.array(  # noqa: E731
        [[math.cos(t / 2), -math.sin(t / 2)], [math.sin(t / 2), math.cos(t / 2)]]
    )
    z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
    return z @ ry(-0.7) @ z @ ry(0.7)


def inverse_qft(qc, n=N_EVAL):
    """Manual n-qubit inverse QFT on the first n qubits."""
    for i in range(n // 2):
        qc.swap(i, n - 1 - i)
    for i in range(n):
        qc.h(i)
        for j in range(i + 1, n):
            qc.cp(-np.pi / 2 ** (j - i), i, j)


def qpe_circuit(measure=True):
    """QPE on Q: 4 evaluation qubits + 1 state qubit prepared as A|0>.
    Evaluation qubit k controls Q^(2^k); the register is measured MSB-first
    (evaluation qubit 0 measured first = most significant digit)."""
    q_matrix = _q_matrix()
    qc = QuantumCircuit(N_EVAL + 1, N_EVAL)
    qc.ry(0.7, N_EVAL)  # state register = A|0>
    qc.h(range(N_EVAL))
    for k in range(N_EVAL):
        power = np.linalg.matrix_power(q_matrix, 2**k)
        gate = QuantumCircuit(1)
        gate.unitary(power, 0)
        qc.append(gate.control(1), [k, N_EVAL])
    inverse_qft(qc)
    if measure:
        qc.measure(range(N_EVAL), range(N_EVAL))
    return qc


def phase_peaks():
    """The two symmetric phase peaks (phi, 1-phi) from the exact statevector
    probabilities over the evaluation register, plus their probabilities."""
    sv = np.asarray(Statevector(qpe_circuit(measure=False)))
    probs = np.abs(sv) ** 2
    # qiskit index bits (LSB first) = (q0, q1, q2, q3, state); the state
    # qubit is the top bit, so summing along axis 0 marginalizes it out and
    # marginal[k] = prob of counting value k (q0 least significant).
    marginal = probs.reshape(2, 2**N_EVAL).sum(axis=0)
    k = int(np.argmax(marginal))
    grid = 2**N_EVAL
    return {
        "peak_k": k,
        "peak_phi": k / float(grid),
        "symmetric_k": (grid - k) % grid,
        "peak_probability": float(marginal[k]),
        "symmetric_probability": float(marginal[(grid - k) % grid]),
    }


def estimated_amplitude():
    """Map the phase peak phi to the amplitude: a = sin(pi * phi)."""
    peaks = phase_peaks()
    return math.sin(math.pi * peaks["peak_phi"])


def true_amplitude():
    """The true amplitude of the good state: a = sin(0.35)."""
    return math.sin(THETA)


def run_amplitude_estimation():
    """Run canonical amplitude estimation end-to-end."""
    peaks = phase_peaks()
    estimate = estimated_amplitude()
    true = true_amplitude()
    error = abs(estimate - true)
    bound = math.pi / (2**N_EVAL)
    return {
        "estimate": estimate,
        "true": true,
        "error": error,
        "bound": bound,
        "phase_peaks": peaks,
    }


def main():
    result = run_amplitude_estimation()
    print("amplitude estimate =", result["estimate"])
    print("true amplitude =", result["true"])
    print("error =", result["error"])
    print("bound = pi/16 =", result["bound"])
    peaks = result["phase_peaks"]
    print("peak k =", peaks["peak_k"], "phi =", peaks["peak_phi"])
    print("symmetric k =", peaks["symmetric_k"])
    assert (
        abs(result["estimate"] - result["true"]) <= result["bound"]
    ), "amplitude error exceeds pi/2**4"
    assert (
        abs(peaks["peak_probability"] - peaks["symmetric_probability"]) < 1e-6
    ), "phase peaks must be symmetric"
    assert result["error"] < 0.05, "amplitude estimate should be much tighter"


if __name__ == "__main__":
    main()
