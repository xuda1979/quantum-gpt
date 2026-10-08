import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import QFT
from qiskit.quantum_info import Statevector

def encode_int(x, n):
    """Encode integer x as an n-qubit basis state |x>."""
    qc = QuantumCircuit(n)
    bits = format(x, f"0{n}b")
    for q, b in enumerate(bits):
        if b == '1':
            qc.x(q)
    return qc

def draper_adder(a, b, n):
    """Build a Draper adder circuit that computes |a>|b> -> |a>|a+b> using
    the QFT-based approach. n qubits for each register."""
    n_total = 2 * n
    qc = QuantumCircuit(n_total)
    # Encode a in register 1 (qubits 0..n-1) and b in register 2 (qubits n..2n-1)
    a_bits = format(a, f"0{n}b")
    b_bits = format(b, f"0{n}b")
    for q, bit in enumerate(a_bits):
        if bit == '1':
            qc.x(q)
    for q, bit in enumerate(b_bits):
        if bit == '1':
            qc.x(n + q)
    # Apply QFT to register 2 (the target register that will hold the sum)
    qc.compose(QFT(n), range(n, 2 * n), inplace=True)
    # Apply controlled phase rotations: for each qubit q_a in register 1 and
    # q_b in register 2, apply a phase rotation of 2*pi / 2^(q_b - q_a + 1)
    # if q_b >= q_a, controlled on q_a being |1>.
    for q_a in range(n):
        for q_b in range(n):
            k = q_b - q_a
            if k < 0:
                continue
            angle = 2 * np.pi / (2 ** (k + 1))
            qc.cp(angle, q_a, n + q_b)
    # Apply inverse QFT to register 2
    qc.compose(QFT(n, inverse=True), range(n, 2 * n), inplace=True)
    return qc

def main():
    a = 3; b = 2; n = 3
    qc = draper_adder(a, b, n)
    # Simulate
    sv = Statevector.from_instruction(qc)
    probs = sv.probabilities_dict()
    # The output should be |a>|a+b> = |011>|101> (little-endian)
    # In qiskit's bit ordering, the full state is a 2n-bit string with
    # qubit 0 as the rightmost bit.
    best = max(probs.items(), key=lambda kv: kv[1])[0]
    # best is little-endian: bit 0 is rightmost
    # Register 1 is the rightmost n bits (qubits 0..n-1)
    # Register 2 is the leftmost n bits (qubits n..2n-1)
    reg1_bits = best[n:][::-1]  # qubits 0..n-1 in big-endian
    reg2_bits = best[:n][::-1]  # qubits n..2n-1 in big-endian
    a_out = int(reg1_bits, 2)
    sum_out = int(reg2_bits, 2)
    expected_sum = a + b
    print(f"a = {a}")
    print(f"b = {b}")
    print(f"n = {n}")
    print(f"Top bitstring = {best}")
    print(f"Register 1 (a) = {a_out}")
    print(f"Register 2 (a+b) = {sum_out}")
    print(f"Expected sum = {expected_sum}")
    print(f"Correct: {sum_out == expected_sum and a_out == a}")

if __name__ == "__main__":
    main()
