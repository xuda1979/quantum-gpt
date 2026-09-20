import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, SparsePauliOp

def build_ghz(n):
    qc = QuantumCircuit(n)
    qc.h(0)
    for i in range(n - 1):
        qc.cx(i, i + 1)
    return qc

def main():
    n = 5
    qc = build_ghz(n)
    sv = Statevector.from_instruction(qc)
    # GHZ stabilizers: X0X1X2X3X4, Z0Z1, Z1Z2, Z2Z3, Z3Z4
    stabilizers = [
        ("X" * n, +1),
        ("Z" + "Z" + "I" * (n - 2), +1),
        ("I" + "ZZ" + "I" * (n - 3), +1),
        ("II" + "ZZ" + "I" * (n - 4), +1),
        ("III" + "ZZ" + "I" * (n - 5 if n > 4 else 0), +1),
    ]
    # Note: Pauli string is read left-to-right as qubit 0,1,2,...,n-1
    # Build them correctly:
    stabilizers = [
        ("XXXXX", +1),
        ("ZZIII", +1),
        ("IZZII", +1),
        ("IIZZI", +1),
        ("IIIZZ", +1),
    ]
    results = []
    for pauli, expected_sign in stabilizers:
        op = SparsePauliOp.from_list([(pauli, 1.0)])
        val = float(sv.expectation_value(op).real)
        results.append((pauli, val))
    all_plus = all(abs(v - expected_sign) < 1e-9 for (_, v), (pauli, expected_sign) in zip(results, stabilizers))
    # Entanglement check: trace out qubits 1..4, the reduced state of qubit 0
    # should be maximally mixed (I/2) indicating entanglement.
    from qiskit.quantum_info import DensityMatrix, partial_trace
    dm = DensityMatrix(sv)
    rho0 = partial_trace(dm, list(range(1, n)))
    purity = float(np.real(np.trace(rho0.data @ rho0.data)))
    print(f"GHZ state: 5 qubits")
    for pauli, v in results:
        print(f"  <{pauli}> = {v:+.4f}")
    print(f"All stabilizers +1: {all_plus}")
    print(f"Single-qubit purity = {purity:.4f}")
    print(f"Entangled: {abs(purity - 0.5) < 1e-6}")
    print(f"Valid GHZ: {all_plus and abs(purity - 0.5) < 1e-6}")

if __name__ == "__main__":
    main()
