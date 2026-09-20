import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import QFT
from qiskit.quantum_info import Statevector
from fractions import Fraction

def main():
    n_count = 3
    # Target is a single qubit on which we apply the S gate (phase = i = exp(i*pi/2))
    # The eigenvalue of S|1> = i*|1> = exp(2*pi*i*(1/4))*|1>, so phase = 1/4.
    creg = ClassicalRegister(n_count, "c")
    qcount = QuantumRegister(n_count, "count")
    qtgt = QuantumRegister(1, "tgt")
    qc = QuantumCircuit(qcount, qtgt, creg)
    # Prepare target in |1> (eigenstate of S)
    qc.x(qtgt[0])
    # Hadamards on counting register
    qc.h(qcount)
    # Apply controlled-S^(2^q) for q=0..n_count-1
    for q in range(n_count):
        # S^(2^q) = phase gate repeated 2^q times
        for _ in range(2 ** q):
            qc.cp(np.pi / 2, qcount[q], qtgt[0])
    # Inverse QFT
    qc.compose(QFT(n_count, inverse=True), qcount[:], inplace=True)
    qc.measure(qcount, creg)
    # Simulate
    sv = Statevector.from_instruction(qc.remove_final_measurements(inplace=False))
    probs = sv.probabilities_dict()
    best = max(probs.items(), key=lambda kv: kv[1])[0]
    phase_int = int(best, 2)
    phase = phase_int / (2 ** n_count)
    frac = Fraction(phase).limit_denominator(2 ** n_count)
    print(f"Counting qubits = {n_count}")
    print(f"Top bitstring = {best}")
    print(f"Phase estimate = {phase:.4f}")
    print(f"Fraction = {frac.numerator}/{frac.denominator}")
    print(f"Exact phase = 0.2500")
    print(f"Correct: {frac == Fraction(1, 4)}")

if __name__ == "__main__":
    main()
