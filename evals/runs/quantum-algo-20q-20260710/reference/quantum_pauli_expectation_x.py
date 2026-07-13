from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp


def main():
    qc = QuantumCircuit(1)
    qc.h(0)
    est = StatevectorEstimator()
    obs = SparsePauliOp.from_list([("X", 1.0)])
    result = est.run([(qc, obs)]).result()
    val = float(result[0].data.evs.item())
    print(f"<X> = {val:.6f}")

if __name__ == "__main__":
    main()
