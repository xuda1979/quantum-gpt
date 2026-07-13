from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector


def build_direct():
    qc = QuantumCircuit(3)
    qc.x(0); qc.x(1)
    qc.ccx(0, 1, 2)
    return qc

def build_decomposed():
    qc = QuantumCircuit(3)
    qc.x(0); qc.x(1)
    qc.cx(1, 2); qc.tdg(2); qc.cx(0, 2); qc.t(2)
    qc.cx(1, 2); qc.tdg(2); qc.cx(0, 2); qc.t(1); qc.t(2)
    qc.cx(0, 1); qc.t(0); qc.tdg(1); qc.cx(0, 1)
    return qc

def main():
    psi_a = Statevector.from_instruction(build_direct())
    psi_b = Statevector.from_instruction(build_decomposed())
    fidelity = abs(psi_a.inner(psi_b)) ** 2
    print(f"fidelity = {fidelity:.3f}")
    print(f"match: {'True' if fidelity >= 0.999 else 'False'}")

if __name__ == "__main__":
    main()
