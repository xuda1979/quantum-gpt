"""Qiskit StatePreparation of a 2-qubit amplitude vector.

Target amplitudes (proportional): [1, 1j, -1, (-0-1j)]. The target is
normalized explicitly (norm is 2, so the normalized vector is
[0.5, 0.5j, -0.5, -0.5j]), the exact Statevector is obtained from the
StatePreparation circuit, global phase is aligned before reporting the
maximum amplitude error, and fidelity must exceed 1 - 1e-12.

Bit-order convention (declared): qiskit little-endian statevector index
i corresponds to the bitstring format(i, '02b') displayed as q1 q0
(qubit 0 is the least significant bit).
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import StatePreparation
from qiskit.quantum_info import Statevector

RAW = np.array([1.0, 1.0j, -1.0, -1.0j], dtype=complex)


def raw_amplitudes():
    """The target amplitudes before normalization."""
    return np.array(RAW, dtype=complex)


def normalized_target():
    """Target amplitudes normalized explicitly (divide by sqrt(4) = 2)."""
    raw = raw_amplitudes()
    return raw / float(np.linalg.norm(raw))


def prepared_statevector():
    """Exact Statevector from StatePreparation on 2 qubits."""
    qc = QuantumCircuit(2)
    qc.append(StatePreparation(normalized_target()), [0, 1])
    return Statevector(qc)


def align_global_phase(target, prepared):
    """prepared multiplied by the scalar that best aligns it to target."""
    target = np.asarray(target, dtype=complex).reshape(-1)
    prepared = np.asarray(prepared, dtype=complex).reshape(-1)
    phase = np.angle(np.vdot(target, prepared))
    return prepared * np.exp(-1.0j * phase)


def max_amplitude_error():
    """Maximum |aligned prepared - target| over all amplitudes."""
    target = normalized_target()
    prepared = align_global_phase(target, prepared_statevector().data)
    return float(np.max(np.abs(prepared - target)))


def fidelity():
    """|langle target | prepared rangle|^2."""
    target = normalized_target()
    prepared = prepared_statevector().data
    return float(abs(np.vdot(target, prepared)) ** 2)


def probabilities():
    """Squared amplitudes keyed by qiskit bitstrings (q1 q0 order)."""
    sv = prepared_statevector().data
    probs = {format(i, "02b"): float(abs(sv[i]) ** 2) for i in range(4)}
    return probs


def main():
    target = normalized_target()
    f = fidelity()
    err = max_amplitude_error()
    probs = probabilities()
    print("normalized target:", target)
    print("fidelity:", f)
    print("max amplitude error:", err)
    print("probabilities (q1q0):", probs)
    assert abs(float(np.linalg.norm(target)) - 1.0) < 1e-12
    assert f > 1.0 - 1e-12, f"fidelity {f} below 1 - 1e-12"
    assert err < 1e-9
    assert abs(sum(probs.values()) - 1.0) < 1e-12
    print("StatePreparation 2q OK")


if __name__ == "__main__":
    main()
