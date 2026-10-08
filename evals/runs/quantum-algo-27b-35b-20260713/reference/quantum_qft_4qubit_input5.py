import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT
from qiskit.quantum_info import Statevector

def main():
    n = 4
    # Prepare the state |5> = |0101>
    qc = QuantumCircuit(n)
    bits = format(5, f"0{n}b")
    for q, b in enumerate(bits):
        if b == '1':
            qc.x(q)
    # Apply QFT
    qc.compose(QFT(n, inverse=False), inplace=True)
    sv = Statevector.from_instruction(qc)
    # The QFT of |x> on n qubits is (1/sqrt(N)) sum_k exp(2 pi i k x / N) |k>
    N = 2 ** n
    expected = np.zeros(N, dtype=complex)
    for k in range(N):
        expected[k] = np.exp(2j * np.pi * k * 5 / N) / np.sqrt(N)
    actual = sv.data
    # Pick the top-2 most probable basis states (by magnitude)
    mags = np.abs(actual) ** 2
    top2 = np.argsort(mags)[::-1][:2]
    # Compare to analytic
    overlap = float(np.abs(np.vdot(expected, actual)) ** 2)
    print(f"N = {N}")
    print(f"Input state = |5>")
    print(f"QFT output overlap = {overlap:.6f}")
    print(f"Top amplitude index = {top2[0]}")
    print(f"Max prob = {mags[top2[0]]:.4f}")
    print(f"All probs equal: {np.allclose(mags, 1.0 / N)}")
    print(f"Correct: {overlap > 0.9999 and np.allclose(mags, 1.0 / N)}")

if __name__ == "__main__":
    main()
