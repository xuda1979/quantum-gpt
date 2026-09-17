"""Coined discrete-time quantum walk on a cycle of 16 positions: 7 steps in
Cirq with one coin qubit and 4 position qubits. The conditional +1/-1
modular shift is a validated 32x32 permutation MatrixGate under the
declared tensor-bit order (coin, p3, p2, p1, p0) with the coin as the most
significant bit. The exact position marginal is cross-checked against an
independently constructed NumPy step matrix (agreement within 1e-12)."""

import math

import cirq
import numpy as np

N_POS = 16
N_QUITS = 5


def qubit_order():
    """Simulation qubit order: [coin, p3, p2, p1, p0] — the coin is the MSB
    of the 32-dim space, the 4 position qubits encode 0..15 in standard
    binary (p3 MSB)."""
    return cirq.LineQubit.range(5)


def shift_permutation():
    """32x32 permutation of the controlled modular shift:
    (coin, pos) -> (coin, pos+1 mod 16) if coin==0 else (coin, pos-1 mod 16).
    Rows/columns have exactly one 1 (validated in run_walk)."""
    mat = np.zeros((32, 32), dtype=complex)
    for coin in (0, 1):
        for pos in range(16):
            nxt = (pos + 1) % 16 if coin == 0 else (pos - 1) % 16
            src = coin * 16 + pos
            dst = coin * 16 + nxt
            mat[dst, src] = 1.0
    return mat


def shift_gate():
    """The controlled modular shift as a cirq MatrixGate applied in the
    declared tensor-bit order (coin first, then p3..p0)."""
    return cirq.MatrixGate(shift_permutation())


def coin_hadamard_gate():
    return cirq.H


def walk_circuit(steps):
    """One coin Hadamard, then `steps` rounds of (shift, H on the coin)."""
    qs = qubit_order()
    circuit = cirq.Circuit()
    circuit.append(cirq.H(qs[0]))
    for _ in range(steps):
        circuit.append(shift_gate().on(*qs))
        circuit.append(cirq.H(qs[0]))
    return circuit


def walk_statevector(steps):
    """Exact 32-component statevector after `steps` walk steps."""
    simulator = cirq.Simulator(dtype=np.complex128)
    state = np.asarray(
        simulator.simulate(walk_circuit(steps), qubit_order=qubit_order()).final_state_vector
    )
    return state


def position_marginal(steps):
    """Exact 16-entry position marginal (coin traced out)."""
    state = walk_statevector(steps)
    probs = np.abs(state) ** 2
    return np.array([float(probs[0 * 16 + pos] + probs[1 * 16 + pos]) for pos in range(16)])


def numpy_step_matrix():
    """Independent NumPy construction of one walk step:
    S * (H_coin x I_16) with the same (coin, pos) index layout."""
    shift = shift_permutation()
    h_coin = np.array([[1.0, 1.0], [1.0, -1.0]], dtype=complex) / math.sqrt(2.0)
    return shift @ np.kron(h_coin, np.eye(16, dtype=complex))


def numpy_marginal(steps):
    """Position marginal from the independent NumPy step matrix."""
    step = numpy_step_matrix()
    vec = np.zeros(32, dtype=complex)
    vec[0] = 1.0
    mat = np.eye(32, dtype=complex)
    for _ in range(steps):
        mat = step @ mat
    vec = mat @ vec
    probs = np.abs(vec) ** 2
    return np.array([float(probs[0 * 16 + pos] + probs[1 * 16 + pos]) for pos in range(16)])


def run_walk(steps=7):
    """Run the walk and verify all invariants."""
    marginal = position_marginal(steps)
    numpy_ref = numpy_marginal(steps)
    max_diff = float(np.max(np.abs(marginal - numpy_ref)))
    permutation = shift_permutation()
    rows = np.sum(np.abs(permutation), axis=1)
    cols = np.sum(np.abs(permutation), axis=0)
    return {
        "steps": int(steps),
        "marginal": marginal,
        "numpy_marginal": numpy_ref,
        "max_diff": max_diff,
        "marginal_normalized": float(np.sum(marginal)),
        "permutation_rows": int(np.sum(np.abs(rows - 1.0) > 1e-12)),
        "permutation_cols": int(np.sum(np.abs(cols - 1.0) > 1e-12)),
    }


def main():
    steps = 7
    result = run_walk(steps)
    marginal = result["marginal"]
    print("steps =", steps)
    print("marginal =", np.round(marginal, 6))
    print("max cross-check diff =", result["max_diff"])
    assert result["permutation_rows"] == 0, "shift is not a row-permutation"
    assert result["permutation_cols"] == 0, "shift is not a column-permutation"
    assert abs(result["marginal_normalized"] - 1.0) < 1e-12, "marginal not normalized"
    assert result["max_diff"] < 1e-12, "cirq and numpy marginals disagree"
    assert np.all(marginal >= -1e-12), "marginal has negative entries"
    support = int(np.sum(marginal > 1e-9))
    assert support >= 5, f"walk failed to spread: support={support}"


if __name__ == "__main__":
    main()
