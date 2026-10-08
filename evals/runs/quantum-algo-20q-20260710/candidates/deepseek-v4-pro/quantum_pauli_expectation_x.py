from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator


def main():
    # 1. Prepare |+> = H|0> on 1 qubit
    qc = QuantumCircuit(1)
    qc.h(0)

    # 2. Use StatevectorEstimator to compute <psi|X|psi>
    estimator = StatevectorEstimator()
    job = estimator.run([(qc, "X", [0])])
    result = job.result()
    exp_val = result[0].data.evs

    # 3. Print expectation value rounded to 6 decimals
    print(f"<X> = {exp_val:.6f}")

if __name__ == "__main__":
    main()
