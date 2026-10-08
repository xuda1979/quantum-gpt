"""QFT applied to a periodic superposition on 3 qubits.

The periodic input (|000> + |100>)/sqrt(2) = (|0> + |4>)/sqrt(2) is the sum
of two computational basis states whose indices differ by a power of two.
Its QFT has nonzero amplitude exactly on the even indices {0, 2, 4, 6}
(amplitude 1/2 each), the Fourier-dual signature of periodicity.

The circuit includes the final swap layer so that the amplitude at index k
is the natural Fourier coefficient omega^(j k)/sqrt(N) -- no bit-reversed
output ordering.
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator

S2 = 1.0 / np.sqrt(2)


def qft_circuit(n: int = 3) -> QuantumCircuit:
    """Return the forward n-qubit QFT circuit (with the final swap layer).

    The unitary implemented is U|j> = sum_k omega^(j k)|k>/sqrt(N) with
    omega = exp(2 pi i / 2^n) and index k in the natural computational order.
    """
    c = QuantumCircuit(n)
    # Rotate the highest qubit first (textbook order), then the controlled
    # phase rotations that target it, and recurse down.
    for i in range(n - 1, -1, -1):
        c.h(i)
        for j in range(i):
            c.cp(np.pi / 2 ** (i - j), j, i)
    for i in range(n // 2):
        c.swap(i, n - 1 - i)
    return c


def periodic_state(n: int = 3) -> list[complex]:
    """Return (|0...0> + |1 0...0>)/sqrt(2) as a length-2^n amplitude list."""
    v = np.zeros(2**n, dtype=complex)
    v[0] = S2
    v[2 ** (n - 1)] = S2  # |1 0...0>: the most significant bit set
    return list(v)


def apply_qft(state: list[complex]) -> list[complex]:
    """Return QFT(state) as a list of amplitudes in natural index order."""
    n = int(round(np.log2(len(state))))
    u = np.asarray(Operator(qft_circuit(n)))
    return list(u @ np.asarray(state, dtype=complex))
