import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp, Statevector

def encode_5qubit():
    qc = QuantumCircuit(5)
    qc.h([1, 2, 3, 4])
    qc.cx(1, 0); qc.cx(2, 0); qc.cx(3, 0); qc.cx(4, 0)
    # Sequence of CZ gates
    qc.cz(1, 0); qc.cz(2, 1); qc.cz(3, 2); qc.cz(4, 3); qc.cz(0, 4)
    qc.cz(2, 0); qc.cz(3, 1); qc.cz(4, 2); qc.cz(0, 3); qc.cz(1, 4)
    qc.cz(3, 0); qc.cz(4, 1); qc.cz(0, 2); qc.cz(1, 3); qc.cz(2, 4)
    qc.cz(4, 0); qc.cz(0, 1); qc.cz(1, 2); qc.cz(2, 3); qc.cz(3, 4)
    return qc

def main():
    qc = encode_5qubit()
    sv = Statevector.from_instruction(qc)
    norm = float(np.linalg.norm(sv.data))
    # 5-qubit code stabilizers (leftmost = qubit 0 in qiskit Pauli string order)
    g1 = SparsePauliOp.from_list([("XZZXI", 1.0)])
    g2 = SparsePauliOp.from_list([("IXZZX", 1.0)])
    g3 = SparsePauliOp.from_list([("XIXZZ", 1.0)])
    g4 = SparsePauliOp.from_list([("ZXIXZ", 1.0)])
    e1 = float(sv.expectation_value(g1).real)
    e2 = float(sv.expectation_value(g2).real)
    e3 = float(sv.expectation_value(g3).real)
    e4 = float(sv.expectation_value(g4).real)
    print(f"Encoded statevector norm = {norm:.4f}")
    print(f"g1 eigenvalue = {'+1' if abs(e1 - 1) < 1e-6 else '-1'}")
    print(f"g2 eigenvalue = {'+1' if abs(e2 - 1) < 1e-6 else '-1'}")
    print(f"g3 eigenvalue = {'+1' if abs(e3 - 1) < 1e-6 else '-1'}")
    print(f"g4 eigenvalue = {'+1' if abs(e4 - 1) < 1e-6 else '-1'}")

if __name__ == "__main__":
    main()
