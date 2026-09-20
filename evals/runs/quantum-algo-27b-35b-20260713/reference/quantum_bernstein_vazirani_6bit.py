import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def build_oracle(s, n):
    """Oracle for f(x) = s.x (mod 2)."""
    qc = QuantumCircuit(n + 1)
    for i, b in enumerate(s):
        if b == '1':
            qc.cx(i, n)
    return qc

def build_bv_circuit(s, n):
    qc = QuantumCircuit(n + 1, n)
    # Initialize ancilla to |-> = (|0>-|1>)/sqrt2
    qc.x(n); qc.h(n)
    qc.h(range(n))
    qc.compose(build_oracle(s, n), inplace=True)
    qc.h(range(n))
    # Measure first n qubits
    return qc

def main():
    n = 6
    s = "101101"  # hidden string
    qc = build_bv_circuit(s, n)
    qc.measure(range(n), range(n))
    sv = Statevector.from_instruction(qc.remove_final_measurements(inplace=False))
    probs = sv.probabilities_dict()
    # In BV, the measurement of the first n qubits is deterministic: |s>
    best = max(probs.items(), key=lambda kv: kv[1])[0]
    # best is the full (n+1)-bit string; the first n bits are the answer
    recovered = best[:n][::-1]  # qiskit is little-endian
    print(f"n = {n}")
    print(f"Hidden string s = {s}")
    print(f"Top bitstring = {best}")
    print(f"Recovered s = {recovered}")
    print(f"Probability = {probs[best]:.4f}")
    print(f"Correct: {recovered == s[::-1]}")

if __name__ == "__main__":
    main()
