import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, DensityMatrix, partial_trace

def build_bitflip_encode():
    """Encode |psi> = a|0> + b|1> into (a|000> + b|111>)/sqrt(2)."""
    qc = QuantumCircuit(3)
    qc.cx(0, 1); qc.cx(0, 2)
    return qc

def build_bitflip_syndrome():
    """Measure Z0Z1 and Z1Z2 stabilizers into 2 ancilla qubits."""
    qc = QuantumCircuit(5)
    # ancilla qubits 3 and 4
    qc.cx(0, 3); qc.cx(1, 3)  # ancilla 3 measures Z0Z1 parity
    qc.cx(1, 4); qc.cx(2, 4)  # ancilla 4 measures Z1Z2 parity
    return qc

def apply_correction(syndrome):
    """Return (qc, flipped_qubit) for the given 2-bit syndrome."""
    qc = QuantumCircuit(3)
    # syndrome bits (s0, s1) where s0 = Z0Z1 parity, s1 = Z1Z2 parity
    s0, s1 = syndrome
    if s0 == 1 and s1 == 0:
        qc.x(0)  # bit flip on qubit 0
        return qc, 0
    elif s0 == 1 and s1 == 1:
        qc.x(1)
        return qc, 1
    elif s0 == 0 and s1 == 1:
        qc.x(2)
        return qc, 2
    return qc, -1  # no error

def main():
    # Encode a known state |psi> = sqrt(0.7)|0> + sqrt(0.3)|1>
    alpha, beta = np.sqrt(0.7), np.sqrt(0.3)
    psi = np.array([alpha, beta], dtype=complex)
    # Build full encode circuit
    enc = QuantumCircuit(3)
    enc.initialize(psi, 0)
    enc.compose(build_bitflip_encode(), inplace=True)
    sv_enc = Statevector.from_instruction(enc)
    # Apply a bit-flip error on qubit 1
    err = QuantumCircuit(3); err.x(1)
    sv_err = sv_enc.evolve(err)
    # Syndrome measurement
    syn_circ = build_bitflip_syndrome()
    full = QuantumCircuit(5)
    full.initialize(psi, 0)
    full.compose(build_bitflip_encode(), inplace=True)
    full.x(1)  # error
    full.compose(syn_circ, inplace=True)
    sv_full = Statevector.from_instruction(full)
    probs = sv_full.probabilities_dict()
    # Determine syndrome from the most likely outcome
    best = max(probs.items(), key=lambda kv: kv[1])[0]
    # Qubit ordering: q0,q1,q2,q3(ancilla),q4(ancilla) -> bitstring is q4q3q2q1q0
    # So ancilla bits are the leftmost two
    anc_bits = best[:2]
    s1 = int(anc_bits[0]); s0 = int(anc_bits[1])
    syndrome = (s0, s1)
    # Apply correction
    corr, flipped = apply_correction(syndrome)
    # Rebuild: encode -> error -> correct, then check fidelity with original
    final = QuantumCircuit(3)
    final.initialize(psi, 0)
    final.compose(build_bitflip_encode(), inplace=True)
    final.x(1)
    final.compose(corr, inplace=True)
    sv_final = Statevector.from_instruction(final)
    # Compare to the encoded (no-error) state
    fid = float(np.abs(np.vdot(sv_enc.data, sv_final.data)) ** 2)
    print(f"Encoded (a,b) = ({alpha:.4f}, {beta:.4f})")
    print(f"Error applied: X on qubit 1")
    print(f"Syndrome (Z0Z1, Z1Z2) = {syndrome}")
    print(f"Corrected qubit = {flipped}")
    print(f"Recovery fidelity = {fid:.6f}")
    print(f"Correct: {abs(fid - 1.0) < 1e-9}")

if __name__ == "__main__":
    main()
