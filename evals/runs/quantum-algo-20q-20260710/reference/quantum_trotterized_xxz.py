import math

from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp


def main():
    t_total = 1.0
    steps = 4
    dt = t_total / steps
    qc = QuantumCircuit(2)
    qc.x(1)
    for _ in range(steps):
        # XX
        qc.h([0, 1])
        qc.cx(0, 1)
        qc.rz(2 * dt, 1)
        qc.cx(0, 1)
        qc.h([0, 1])
        # YY
        qc.rx(math.pi/2, [0, 1])
        qc.cx(0, 1)
        qc.rz(2 * dt, 1)
        qc.cx(0, 1)
        qc.rx(-math.pi/2, [0, 1])
        # ZZ (with 0.5 coefficient)
        qc.cx(0, 1)
        qc.rz(2 * 0.5 * dt, 1)
        qc.cx(0, 1)
    est = StatevectorEstimator()
    obs = SparsePauliOp.from_list([("ZI", 1.0)])
    res = est.run([(qc, obs)]).result()
    val = float(res[0].data.evs.item())
    print(f"<Z on q0> = {val:.4f}")

if __name__ == "__main__":
    main()
