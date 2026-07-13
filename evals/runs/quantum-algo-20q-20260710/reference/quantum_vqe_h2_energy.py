from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp
from qiskit_algorithms.minimum_eigensolvers import VQE
from qiskit_algorithms.optimizers import COBYLA


def main():
    H = SparsePauliOp.from_list([
        ("II", -1.052373),
        ("ZI", 0.397937),
        ("IZ", -0.397937),
        ("ZZ", -0.011280),
        ("XX", 0.180931),
    ])
    p = ParameterVector("p", 6)
    ansatz = QuantumCircuit(2)
    ansatz.ry(p[0], 0); ansatz.ry(p[1], 1)
    ansatz.cx(0, 1)
    ansatz.ry(p[2], 0); ansatz.ry(p[3], 1)
    ansatz.cx(0, 1)
    ansatz.ry(p[4], 0); ansatz.ry(p[5], 1)
    estimator = StatevectorEstimator()
    vqe = VQE(estimator=estimator, ansatz=ansatz, optimizer=COBYLA(maxiter=400))
    result = vqe.compute_minimum_eigenvalue(H)
    print(f"VQE energy = {result.eigenvalue:.4f}")

if __name__ == "__main__":
    main()
