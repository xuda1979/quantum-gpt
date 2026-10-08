"""Three-qubit bit-flip code in Qiskit.

Logical state RY(0.83)|0> is encoded into alpha|000> + beta|111>; an X
error is injected on a chosen data qubit; the two Z-parity syndromes
(Z0Z1 into ancilla 0, Z1Z2 into ancilla 1) are extracted, the ancillas are
measured, the correction is applied with QuantumCircuit.if_test, and the
code is coherently decoded (inverse CNOT network) before logical X/Z
estimation in separate seeded circuits.

Syndrome truth table (a0, a1) -> data qubit to flip:
  (0,0) -> none, (1,0) -> qubit 0, (1,1) -> qubit 1, (0,1) -> qubit 2.
"""

import math

from qiskit import ClassicalRegister, QuantumCircuit
from qiskit_aer import AerSimulator

DATA = [0, 1, 2]
ANCILLA = [3, 4]
SINGLE = [5]  # measurement qubit for logical-basis readout
THETA = 0.83


def syndrome_truth_table():
    """(ancilla0, ancilla1) -> data qubit to correct (-1 = no correction)."""
    return {(0, 0): -1, (1, 0): 0, (1, 1): 1, (0, 1): 2}


def encode_circuit():
    """alpha|0> + beta|1> -> alpha|000> + beta|111> on the 3 data qubits.
    Includes the classical register for the two syndrome bits and the
    logical readout bit."""
    qc = QuantumCircuit(6)
    qc.add_register(ClassicalRegister(3, "c"))
    qc.ry(THETA, 0)
    qc.cx(0, 1)
    qc.cx(0, 2)
    return qc


def syndrome_measurement(qc):
    """Append the two Z-parity syndrome extractions into ancillas and the
    ancilla measurements (classical bits s0, s1)."""
    qc.cx(DATA[0], ANCILLA[0])
    qc.cx(DATA[1], ANCILLA[0])
    qc.cx(DATA[1], ANCILLA[1])
    qc.cx(DATA[2], ANCILLA[1])
    qc.measure(ANCILLA[0], 0)
    qc.measure(ANCILLA[1], 1)
    return qc


def apply_correction(qc):
    """if_test-based correction from the measured syndrome bits.

    Each non-trivial syndrome (a0, a1) maps to exactly one data qubit;
    the correction is gated on both classical bits being equal to the
    syndrome pattern (nested if_test on bit 0 then bit 1)."""
    table = syndrome_truth_table()
    for syndrome, target in table.items():
        if target < 0:
            continue
        with qc.if_test((0, syndrome[0])):
            with qc.if_test((1, syndrome[1])):
                qc.x(target)
    return qc


def decode_circuit(qc):
    """Coherent decode: reverse CNOT network, then measure qubit 0."""
    qc.cx(0, 2)
    qc.cx(0, 1)
    return qc


def build_circuit(error_qubit, basis):
    """Full pipeline for one error qubit and one logical basis ('X'/'Z')."""
    qc = encode_circuit()
    if error_qubit >= 0:
        qc.x(error_qubit)
    syndrome_measurement(qc)
    apply_correction(qc)
    decode_circuit(qc)
    if basis == "X":
        qc.h(0)
    qc.measure(0, 2)
    return qc


def logical_expectation(error_qubit, basis, shots=20000, seed=1234):
    """Estimate <logical> (X or Z) of the decoded logical qubit.

    The logical readout lands on clbit index 2, which qiskit counts keys
    order most-significant-first (first character of the key string)."""
    qc = build_circuit(error_qubit, basis)
    sim = AerSimulator(seed_simulator=seed)
    counts = sim.run(qc, shots=shots).result().get_counts()
    n_one = sum(c for key, c in counts.items() if key[:1] == "1")
    p1 = n_one / float(shots)
    return 1.0 - 2.0 * p1  # <X> after H (or <Z>) = p(0) - p(1)


def main():
    theta = THETA
    exp_x_ideal = math.sin(theta)
    exp_z_ideal = math.cos(theta)
    exp_x = logical_expectation(1, "X")
    exp_z = logical_expectation(1, "Z")
    assert abs(exp_x - exp_x_ideal) < 0.04, f"logical X {exp_x}"
    assert abs(exp_z - exp_z_ideal) < 0.04, f"logical Z {exp_z}"
    # truth-table check for all four syndrome patterns
    table = syndrome_truth_table()
    assert table[(0, 0)] == -1 and table[(1, 0)] == 0
    assert table[(1, 1)] == 1 and table[(0, 1)] == 2
    print("logical X =", exp_x, "ideal", exp_x_ideal)
    print("logical Z =", exp_z, "ideal", exp_z_ideal)


if __name__ == "__main__":
    main()
