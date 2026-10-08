"""Coined discrete-time quantum walk on a cycle of 4 positions: 3 steps in
Qiskit with one coin qubit (q0) and two position qubits (q1=p1, q2=p0).
The conditional +1/-1 modulo-4 shift is an explicit 8x8 unitary
permutation under the declared basis order [coin, p1, p0] with the coin as
the most significant bit (index = coin*4 + position). The exact final
position marginal is asserted against an independent NumPy matrix
simulation."""

import math

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector


def qubit_order():
    """Basis order: q0 = coin (MSB), q1 = p1, q2 = p0 (LSB)."""
    return [0, 1, 2]


def shift_permutation():
    """8x8 permutation: (coin, pos) -> (coin, pos+1 mod 4) if coin==0 else
    (coin, pos-1 mod 4)."""
    mat = np.zeros((8, 8), dtype=complex)
    for coin in (0, 1):
        for pos in range(4):
            nxt = (pos + 1) % 4 if coin == 0 else (pos - 1) % 4
            src = coin * 4 + pos
            dst = coin * 4 + nxt
            mat[dst, src] = 1.0
    return mat


def coin_hadamard():
    """Coin flip matrix H x I_4 on the 8-dim space."""
    h = np.array([[1.0, 1.0], [1.0, -1.0]], dtype=complex) / math.sqrt(2.0)
    return np.kron(h, np.eye(4, dtype=complex))


def step_unitary():
    """One walk step: S * (H x I_4)."""
    return shift_permutation() @ coin_hadamard()


def walk_circuit(steps):
    """Qiskit circuit: H on the coin, then `steps` rounds of the shift
    unitary and an H coin flip."""
    qc = QuantumCircuit(3)
    qc.h(0)
    for _ in range(steps):
        qc.unitary(shift_permutation(), qubit_order(), label="shift")
        qc.h(0)
    return qc


def position_marginal(steps):
    """Exact position marginal after `steps` steps (coin traced out)."""
    sv = np.asarray(Statevector(walk_circuit(steps)))
    probs = np.abs(sv) ** 2
    return np.array([float(probs[0 * 4 + pos] + probs[1 * 4 + pos]) for pos in range(4)])


def numpy_marginal(steps):
    """Independent NumPy simulation of the same walk."""
    step = step_unitary()
    vec = np.zeros(8, dtype=complex)
    vec[0] = 1.0
    mat = np.eye(8, dtype=complex)
    for _ in range(steps):
        mat = step @ mat
    vec = mat @ vec
    probs = np.abs(vec) ** 2
    return np.array([float(probs[0 * 4 + pos] + probs[1 * 4 + pos]) for pos in range(4)])


def run_walk(steps=3):
    """Run the walk and verify the invariants."""
    marginal = position_marginal(steps)
    numpy_ref = numpy_marginal(steps)
    max_diff = float(np.max(np.abs(marginal - numpy_ref)))
    perm = shift_permutation()
    rows = np.sum(np.abs(perm), axis=1)
    cols = np.sum(np.abs(perm), axis=0)
    unitary_check = float(np.max(np.abs(perm @ perm.conj().T - np.eye(8, dtype=complex))))
    return {
        "steps": int(steps),
        "marginal": marginal,
        "numpy_marginal": numpy_ref,
        "max_diff": max_diff,
        "marginal_normalized": float(np.sum(marginal)),
        "permutation_rows": int(np.sum(np.abs(rows - 1.0) > 1e-12)),
        "permutation_cols": int(np.sum(np.abs(cols - 1.0) > 1e-12)),
        "unitary_deviation": unitary_check,
    }


def main():
    result = run_walk(3)
    marginal = result["marginal"]
    print("steps =", result["steps"])
    print("marginal =", np.round(marginal, 6))
    print("max cross-check diff =", result["max_diff"])
    assert result["permutation_rows"] == 0, "shift is not a row-permutation"
    assert result["permutation_cols"] == 0, "shift is not a column-permutation"
    assert result["unitary_deviation"] < 1e-12, "shift is not unitary"
    assert abs(result["marginal_normalized"] - 1.0) < 1e-12, "marginal not normalized"
    assert np.all(marginal >= -1e-12), "marginal has negative entries"
    assert result["max_diff"] < 1e-12, "qiskit and numpy marginals disagree"


if __name__ == "__main__":
    main()
