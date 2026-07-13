from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp


def main():
    qc = QuantumCircuit(3)
    qc.h(0)              # prepare |+> on q0
    qc.h(1); qc.cx(1, 2)  # Bell pair (q1, q2)
    qc.cx(0, 1); qc.h(0)  # Alice's Bell-basis transform
    qc.cx(1, 2); qc.cz(0, 2)  # Coherent corrections
    est = StatevectorEstimator()
    obs = SparsePauliOp.from_list([("IIX", 1.0)])
    result = est.run([(qc, obs)]).result()
    val = float(result[0].data.evs.item())
    print(f"<X> on Bob = {val:.6f}")

if __name__ == "__main__":
    main()
