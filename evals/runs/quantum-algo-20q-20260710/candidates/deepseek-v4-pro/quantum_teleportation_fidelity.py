from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator


def main():
    # Create circuit with 3 qubits and 0 classical bits
    qc = QuantumCircuit(3, 0)

    # Step 1: Prepare |+> on q0
    qc.h(0)

    # Step 2: Create Bell pair on (q1, q2)
    qc.h(1)
    qc.cx(1, 2)

    # Step 3: Apply CX q0->q1 then H q0
    qc.cx(0, 1)
    qc.h(0)

    # Step 4: Coherent corrections: CX q1->q2 and CZ q0->q2
    qc.cx(1, 2)
    qc.cz(0, 2)

    # Compute expectation value <X> on qubit q2
    estimator = StatevectorEstimator()
    job = estimator.run([(qc, [('X', [2])])])
    result = job.result()
    exp_val = result[0].data.evs[0]

    print(f"<X> on Bob = {exp_val:.6f}")

if __name__ == "__main__":
    main()
