"""QFT applied to a 3-qubit GHZ state.

The QFT of (|000> + |111>)/sqrt(2) produces a known uniform-phase
distribution; this module constructs the circuit and exposes a statevector
inspector for testing.
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector


def ghz_circuit(n: int = 3) -> QuantumCircuit:
    """Return an n-qubit GHZ state preparation circuit."""
    c = QuantumCircuit(n)
    c.h(0)
    for i in range(n - 1):
        c.cx(i, i + 1)
    return c


def qft_circuit(n: int = 3) -> QuantumCircuit:
    """Return the n-qubit QFT circuit (without final swaps for in-place order)."""
    c = QuantumCircuit(n)
    for i in range(n):
        c.h(i)
        for j in range(i + 1, n):
            c.cp(np.pi / (2 ** (j - i)), j, i)
    return c


def ghz_then_qft_circuit(n: int = 3) -> QuantumCircuit:
    """Compose GHZ preparation + QFT."""
    c = ghz_circuit(n)
    c.compose(qft_circuit(n), inplace=True)
    return c


def ghz_then_qft_statevector(n: int = 3) -> np.ndarray:
    """Return the final statevector of GHZ followed by QFT."""
    c = ghz_then_qft_circuit(n)
    sv = Statevector.from_instruction(c)
    return np.asarray(sv.data)


def amplitude_histogram(n: int = 3, tol: float = 1e-9) -> dict[str, complex]:
    """Return a {bitstring: amplitude} dict, dropping near-zero amplitudes."""
    sv = ghz_then_qft_statevector(n)
    out: dict[str, complex] = {}
    for i, a in enumerate(sv):
        if abs(a) > tol:
            out[format(i, f"0{n}b")] = complex(a)
    return out


if __name__ == "__main__":
    hist = amplitude_histogram()
    for bs, a in sorted(hist.items()):
        print(f"  {bs}: {a:.4f}")
