from qiskit import QuantumCircuit


def main():
    # Create a 5-qubit circuit (3 data + 2 syndrome)
    qc = QuantumCircuit(5, 5)

    # Step 1: Encode |1> into |111> by applying X on q0, q1, q2
    qc.x(0)
    qc.x(1)
    qc.x(2)

    # Step 2: Apply X error on middle qubit (q1)
    qc.x(1)

    # Step 3: Syndrome measurement
    # c0 = q0 XOR q1
    qc.cx(0, 3)
    qc.cx(1, 3)
    # c1 = q1 XOR q2
    qc.cx(1, 4)
    qc.cx(2, 4)

    # Step 4: Measure all 5 qubits
    qc.measure_all()

    # Wait, measure_all() adds classical bits. Let me use measure instead.
    # Actually, I already created the circuit with 5 classical bits.
    # Let me use qc.measure(range(5), range(5)) instead.
