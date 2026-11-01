from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator

def estimator_zz_expectation():
    """<ZZ> on |11> is +1; circuit X(0)+CX(0,1) prepares |11>."""
    qc = QuantumCircuit(2)
    qc.x(0)
    qc.cx(0, 1)
    op = SparsePauliOp("ZZ")
    est = StatevectorEstimator(seed=9)
    res = est.run([(qc, op)]).result()
    return float(res[0].data.evs)
