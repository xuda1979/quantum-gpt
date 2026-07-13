import numpy as np
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp


def main():
    dt = 0.25
    steps = 4
    total_time = 1.0

    # Build circuit for 4 Trotter steps
    qc = QuantumCircuit(2)
    # Initial state |01>
    qc.x(1)

    for _ in range(steps):
        # e^{-i dt XX}
        qc.h(0)
        qc.h(1)
        qc.cx(0, 1)
        qc.rz(2 * dt, 1)
        qc.cx(0, 1)
        qc.h(0)
        qc.h(1)

        # e^{-i dt YY}
        qc.rx(np.pi / 2, 0)
        qc.rx(np.pi / 2, 1)
        qc.cx(0, 1)
        qc.rz(2 * dt, 1)
        qc.cx(0, 1)
        qc.rx(-np.pi / 2, 0)
        qc.rx(-np.pi / 2, 1)

        # e^{-i dt * 0.5 ZZ}
        qc.cx(0, 1)
        qc.rz(2 * 0.5 * dt, 1)
        qc.cx(0, 1)

    # Observable ZI
    obs = SparsePauliOp.from_list([("ZI", 1.0)])

    estimator = StatevectorEstimator()
    job = estimator.run([(qc, obs)])
    result = job.result()
    value = result[0].data.evs

    print(f"<Z on q0> = {value:.4f}")

if __name__ == "__main__":
    main()
