"""Steane 7-qubit code: encode the logical |1> state.

The Steane code is a [[7,1,3]] CSS code. The 8 codewords of the
Hamming [7,4,3] code are:
  0000000, 1010101, 0110011, 1100110,
  0001111, 1011010, 0111100, 1101001
|0_L> = (1/sqrt(8)) sum_i |c_i>. |1_L> = X^{⊗7} |0_L>.
We use qubits 6,5,3 as 'control' qubits (in |+>), then CNOTs to
set the dependent bits, then X^{⊗7} for logical |1>.
We verify the X-stabilizer eigenvalues are all +1 and Z_L = -1.
"""
from qiskit import QuantumCircuit
from qiskit.quantum_info import Pauli, Statevector


def steane_encode_logical_one() -> QuantumCircuit:
    qc = QuantumCircuit(7)
    # Control qubits 6, 5, 3 in |+>
    qc.h(6)
    qc.h(5)
    qc.h(3)
    # q4 = q6 ^ q5
    qc.cx(6, 4)
    qc.cx(5, 4)
    # q2 = q6 ^ q3
    qc.cx(6, 2)
    qc.cx(3, 2)
    # q1 = q5 ^ q3
    qc.cx(5, 1)
    qc.cx(3, 1)
    # q0 = q6 ^ q5 ^ q3
    qc.cx(6, 0)
    qc.cx(5, 0)
    qc.cx(3, 0)
    # Apply X^{⊗7} for logical |1>
    for i in range(7):
        qc.x(i)
    return qc


def make_pauli_x(qubits, n=7):
    labels = ["I"] * n
    for q in qubits:
        labels[q] = "X"
    return Pauli("".join(labels))


def main():
    enc = steane_encode_logical_one()
    sv = Statevector.from_instruction(enc)
    x_stabs = [
        make_pauli_x([0, 2, 4, 6]),
        make_pauli_x([1, 2, 5, 6]),
        make_pauli_x([3, 4, 5, 6]),
    ]
    x_eigenvalues = [sv.expectation_value(p).real for p in x_stabs]
    zL = Pauli("Z" * 7)
    zL_ev = sv.expectation_value(zL).real
    print(f"X-stabilizer eigenvalues: {[f'{v:.3f}' for v in x_eigenvalues]}")
    print(f"Z_L eigenvalue: {zL_ev:.3f}")
    all_x_plus1 = all(abs(v - 1.0) < 0.01 for v in x_eigenvalues)
    is_logical_1 = abs(zL_ev - (-1.0)) < 0.01
    print(f"encoded: {all_x_plus1 and is_logical_1}")


if __name__ == "__main__":
    main()
