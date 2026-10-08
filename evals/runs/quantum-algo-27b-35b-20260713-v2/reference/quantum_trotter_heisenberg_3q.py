import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp, Statevector

N = 3
J = 1.0
h = 0.5
TERMS = ["XXI", "IXX", "YYI", "IYY", "ZZI", "IZZ",
         "ZII", "IZI", "IIZ"]

def trotter_step(qc, dt):
    # Apply exp(-i * dt * term) for each term.
    # For 2-qubit Pauli strings XX, YY, ZZ: use RXX(2*dt), RYY(2*dt), RZZ(2*dt).
    # For single Z: use RZ(2*dt) on the appropriate qubit.
    # qiskit Pauli string: leftmost = qubit 0.
    for term in TERMS:
        # Identify qubits involved
        qubits = [i for i, c in enumerate(term) if c != "I"]
        pauli = [c for c in term if c != "I"]
        if len(qubits) == 2:
            if pauli == ["X", "X"]:
                qc.rxx(2 * J * dt, qubits[0], qubits[1])
            elif pauli == ["Y", "Y"]:
                qc.ryy(2 * J * dt, qubits[0], qubits[1])
            elif pauli == ["Z", "Z"]:
                qc.rzz(2 * J * dt, qubits[0], qubits[1])
        elif len(qubits) == 1:
            # Z on a single qubit
            qc.rz(2 * h * dt, qubits[0])

def main():
    n_trotter = 4
    dt = 0.1
    t_total = n_trotter * dt
    qc = QuantumCircuit(N)
    # Initial state |100>: qubit 0 in |1>
    qc.x(0)
    for _ in range(n_trotter):
        trotter_step(qc, dt)
    sv = Statevector.from_instruction(qc)
    norm = float(np.linalg.norm(sv.data))
    # <X0> and <Z0>
    X0 = SparsePauliOp.from_list([("XII", 1.0)])
    Z0 = SparsePauliOp.from_list([("ZII", 1.0)])
    x0_exp = float(sv.expectation_value(X0).real)
    z0_exp = float(sv.expectation_value(Z0).real)
    print(f"Total time = {t_total:.4f}")
    print(f"<X0>(t) = {x0_exp:.4f}")
    print(f"<Z0>(t) = {z0_exp:.4f}")
    print(f"State norm = {norm:.4f}")
    print(f"Trotter steps = {n_trotter}")

if __name__ == "__main__":
    main()
