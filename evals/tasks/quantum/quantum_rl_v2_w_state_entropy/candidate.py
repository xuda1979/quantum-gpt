"""Exact 3-qubit W state in Qiskit: StatePreparation from a normalized
amplitude vector, Statevector fidelity vs target (up to global phase),
reduced density matrix of qubit 0, and its von Neumann entropy. Asserts
normalization and zero probability on every non-Hamming-weight-1 basis
state."""

import math

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, entropy, partial_trace, state_fidelity


def w_state_amplitudes():
    """Normalized amplitudes of |W> = (|001>+|010>+|100>)/sqrt(3).

    Index i is the basis state whose 3 bits are the bits of i, qubit 0 =
    most significant bit (Qiskit little-endian qubit order).
    """
    amp = [0.0] * 8
    inv_s3 = 1.0 / math.sqrt(3.0)
    amp[1] = inv_s3  # |001>
    amp[2] = inv_s3  # |010>
    amp[4] = inv_s3  # |100>
    return amp


def w_state_circuit():
    """Return a QuantumCircuit preparing the 3-qubit W state."""
    qc = QuantumCircuit(3)
    qc.prepare_state(w_state_amplitudes(), range(3))
    return qc


def w_statevector():
    """Return the prepared 3-qubit Statevector."""
    return Statevector(w_state_circuit())


def target_fidelity(statevector):
    """Fidelity (up to global phase) between `statevector` and |W>."""
    target = Statevector(w_state_amplitudes())
    return float(state_fidelity(statevector, target))


def reduced_qubit0_density(statevector):
    """Reduced density matrix of qubit 0 as a 2x2 list of floats."""
    rho = partial_trace(statevector, [1, 2])
    return rho.data.tolist()


def qubit0_entropy(statevector):
    """Base-2 von Neumann entropy of qubit 0's reduced state."""
    rho0 = partial_trace(statevector, [1, 2])
    return float(entropy(rho0, base=2))


def main():
    sv = w_statevector()
    amps = sv.data
    norm = sum(abs(a) ** 2 for a in amps)
    assert abs(norm - 1.0) < 1e-12, f"not normalized: {norm}"
    for i, a in enumerate(amps):
        hw = bin(i).count("1")
        if hw != 1:
            assert abs(a) < 1e-12, f"basis state {i:03b} should have zero amplitude"
    fid = target_fidelity(sv)
    assert abs(fid - 1.0) < 1e-12, f"fidelity={fid}"
    s = qubit0_entropy(sv)
    h2_third = -(2.0 / 3.0) * math.log2(2.0 / 3.0) - (1.0 / 3.0) * math.log2(1.0 / 3.0)
    assert abs(s - h2_third) < 1e-9, f"entropy={s}, expected {h2_third}"
    print("fidelity =", fid)
    print("entropy(qubit0) =", s)
    print("rho0 =", reduced_qubit0_density(sv))


if __name__ == "__main__":
    main()
