from qiskit.circuit.library import TwoLocal
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp
from qiskit_algorithms.minimum_eigensolvers import VQE
from qiskit_algorithms.optimizers import COBYLA


def main():
    # 1. Define the 2-qubit H2 Hamiltonian
    hamiltonian = SparsePauliOp.from_list([
        ("II", -1.052373),
        ("ZI",  0.397937),
        ("IZ", -0.397937),
        ("ZZ", -0.011280),
        ("XX",  0.180931)
    ])

    # 2. Ansatz: 2-layer Ry+CX (6 parameters)
    ansatz = TwoLocal(2, "ry", "cx", reps=2, entanglement="linear")

    # 3. VQE with StatevectorEstimator and COBYLA
    estimator = StatevectorEstimator()
    optimizer = COBYLA(maxiter=400)
    vqe = VQE(estimator, ansatz, optimizer)
    result = vqe.compute_minimum_eigenvalue(hamiltonian)

    # Print result rounded to 4 decimals
    energy = round(result.eigenvalue.real, 4)
    print(f"VQE energy = {energy}")

if __name__ == "__main__":
    main()
