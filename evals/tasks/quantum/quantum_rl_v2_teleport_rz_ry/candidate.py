"""Quantum teleportation of RZ(0.8)RY(1.1)|0> in Qiskit with mid-circuit
measurements, if_test corrections, and a seeded AerSimulator run.

Correction mapping (standard Bell teleportation): after Alice measures her
two qubits into cr_a (qubit 0) and cr_b (qubit 1), the receiver qubit 2
needs  X if cr_b==1 and Z if cr_a==1  (X tracks the qubit that Alice
entangled with the receiver first, Z tracks the second).
"""

import math

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

TARGET_Z = math.cos(1.1)  # <Z> of RZ(0.8)RY(1.1)|0> = cos(1.1)


def prepare_state_circuit():
    """One-qubit circuit preparing RZ(0.8)RY(1.1)|0> (RY first, then RZ)."""
    qc = QuantumCircuit(1)
    qc.ry(1.1, 0)
    qc.rz(0.8, 0)
    return qc


def statevector():
    """Statevector of RZ(0.8)RY(1.1)|0> as a length-2 complex array."""
    return np.asarray(Statevector(prepare_state_circuit()))


def teleport_circuit():
    """Full teleportation circuit: q0 carries the state, q1-q2 the Bell pair,
    mid-circuit measurement into two distinct classical registers (a, b),
    if_test corrections on the receiver q2, then a Z-basis measurement of the
    receiver into its own register (rec)."""
    cr_a = ClassicalRegister(1, "a")
    cr_b = ClassicalRegister(1, "b")
    cr_rec = ClassicalRegister(1, "rec")
    qc = QuantumCircuit(3, 0)
    qc.add_register(cr_a)
    qc.add_register(cr_b)
    qc.add_register(cr_rec)
    # prepare the state on q0 (RY first, then RZ)
    qc.ry(1.1, 0)
    qc.rz(0.8, 0)
    # Bell pair on (q1, q2)
    qc.h(1)
    qc.cx(1, 2)
    # Bell measurement of q0 with the first Bell-pair qubit
    qc.cx(0, 1)
    qc.h(0)
    qc.measure(0, cr_a[0])
    qc.measure(1, cr_b[0])
    # corrections: X if cr_b==1, Z if cr_a==1
    with qc.if_test((cr_b[0], 1)):
        qc.x(2)
    with qc.if_test((cr_a[0], 1)):
        qc.z(2)
    # receiver measured in the Z basis (no basis-change gate needed for Z)
    qc.measure(2, cr_rec[0])
    return qc


def receiver_expectation(counts, receiver_bit_pos=0):
    """<Z> on the receiver from a counts dict.

    Aer counts keys order the clbits from the highest bit index (leftmost)
    to the lowest (rightmost). The receiver register is the last register
    added, so it is the highest clbit index and appears as the FIRST
    character of each key.
    """
    shots = sum(counts.values())
    if shots == 0:
        raise ValueError("empty counts")
    ones = sum(v for k, v in counts.items() if int(k[receiver_bit_pos]) == 1)
    zeros = shots - ones
    return (zeros - ones) / shots


def run_teleport(shots=12000, seed_simulator=1234, tolerance=0.04):
    """Run the teleportation circuit on AerSimulator and compare the receiver
    <Z> against cos(1.1) within a statistically justified tolerance
    (3 sigma for 12000 shots is about 0.023; 0.04 is a conservative window)."""
    qc = teleport_circuit()
    backend = AerSimulator(seed_simulator=seed_simulator)
    counts = backend.run(qc, shots=shots).result().get_counts()
    z = receiver_expectation(counts)
    passed = abs(z - TARGET_Z) <= tolerance
    return {
        "receiver_z": float(z),
        "target_z": float(TARGET_Z),
        "tolerance": float(tolerance),
        "shots": int(shots),
        "passed": bool(passed),
    }


def main():
    sv = statevector()
    c = math.cos(1.1 / 2.0)
    s = math.sin(1.1 / 2.0)
    assert abs(abs(sv[0]) - c) < 1e-12, "state preparation wrong"
    assert abs(abs(sv[1]) - s) < 1e-12, "state preparation wrong"
    result = run_teleport()
    print("receiver_z =", result["receiver_z"])
    print("target_z =", result["target_z"])
    print("tolerance =", result["tolerance"])
    assert result["passed"], (
        f"receiver expectation {result['receiver_z']} deviates from "
        f"cos(1.1) = {TARGET_Z} beyond {result['tolerance']}"
    )


if __name__ == "__main__":
    main()
