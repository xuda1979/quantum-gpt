import numpy as np
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.quantum_info import Statevector


def ghz_circuit(n: int) -> QuantumCircuit:
    """Prepare the GHZ state (|0...0> + |1...1>)/sqrt(2) on n qubits."""
    qr = QuantumRegister(n)
    qc = QuantumCircuit(qr, name="ghz")
    qc.h(qr[0])
    for i in range(1, n):
        qc.cx(qr[0], qr[i])
    return qc


def qft_circuit(n: int) -> QuantumCircuit:
    """Implement the forward n-qubit QFT without final swaps."""
    qr = QuantumRegister(n)
    qc = QuantumCircuit(qr, name="qft")
    for i in range(n):
        qc.h(qr[i])
        for j in range(i + 1, n):
            qc.cp(2 * np.pi / (2 ** (j - i + 1)), qr[j], qr[i])
    return qc


def ghz_then_qft_circuit(n: int) -> QuantumCircuit:
    """Compose ghz_circuit and qft_circuit."""
    qr = QuantumRegister(n)
    qc = QuantumCircuit(qr, name="ghz_then_qft")
    ghz = ghz_circuit(n)
    qft = qft_circuit(n)
    qc.compose(ghz, inplace=True)
    qc.compose(qft, inplace=True)
    return qc


def ghz_then_qft_statevector(n: int) -> np.ndarray:
    """Return the statevector of ghz_then_qft_circuit(n)."""
    qc = ghz_then_qft_circuit(n)
    sv = Statevector.from_instruction(qc)
    return sv.data


def amplitude_histogram(n: int, tol: float = 1e-10) -> dict:
    """
    Return a dictionary mapping zero-padded n-bit binary strings to their
    amplitudes, including only those with |amplitude| > tol.
    """
    sv = ghz_then_qft_statevector(n)
    result = {}
    for k in range(2**n):
        amp = sv[k]
        if abs(amp) > tol:
            key = format(k, f"0{n}b")
            result[key] = amp
    return result
