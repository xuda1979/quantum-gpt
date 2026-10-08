from qiskit import QuantumCircuit
from qiskit.circuit.library import MCXGate
from qiskit.quantum_info import Statevector


def build_direct():
    qc = QuantumCircuit(6)
    qc.x(0); qc.x(1); qc.x(2); qc.x(3)
    qc.mcx([0, 1, 2, 3], 5)
    return qc

def build_decomposed():
    qc = QuantumCircuit(6)
    qc.x(0); qc.x(1); qc.x(2); qc.x(3)
    # Use Qiskit's no-ancilla MCX decomposition (relative-phase Toffoli cascade)
    qc.append(MCXGate(4, label="mct4"), [0, 1, 2, 3, 5])
    return qc

def main():
    psi_a = Statevector.from_instruction(build_direct())
    psi_b = Statevector.from_instruction(build_decomposed())
    fidelity = abs(psi_a.inner(psi_b)) ** 2
    print(f"fidelity = {fidelity:.3f}")
    print(f"match: {'True' if fidelity >= 0.999 else 'False'}")

if __name__ == "__main__":
    main()
