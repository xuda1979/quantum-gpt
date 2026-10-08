from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp
from qiskit_algorithms.minimum_eigensolvers import VQE
from qiskit_algorithms.optimizers import COBYLA


def main():
    terms = []
    for i in range(3):
        s = ["I"] * 4
        s[3 - i] = "Z"
        s[3 - (i + 1)] = "Z"
        terms.append(("".join(s), -1.0))
    for i in range(4):
        s = ["I"] * 4
        s[3 - i] = "X"
        terms.append(("".join(s), -1.0))
    H = SparsePauliOp.from_list(terms)
    p = ParameterVector("p", 12)
    ansatz = QuantumCircuit(4)
    for layer in range(3):
        for q in range(4):
            ansatz.ry(p[layer * 4 + q], q)
        ansatz.cx(0, 1); ansatz.cx(1, 2); ansatz.cx(2, 3)
    estimator = StatevectorEstimator()
    vqe = VQE(estimator=estimator, ansatz=ansatz, optimizer=COBYLA(maxiter=800))
    result = vqe.compute_minimum_eigenvalue(H)
    print(f"VQE energy = {result.eigenvalue:.4f}")
    print("exact = -4.759")

if __name__ == "__main__":
    main()
