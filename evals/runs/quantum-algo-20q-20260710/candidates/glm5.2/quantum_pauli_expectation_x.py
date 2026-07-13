from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp

qc = QuantumCircuit(2)
...
estimator = StatevectorEstimator()
observables = SparsePauliOp.from_list([("II", 1), ("IZ", 2), ...])
job = estimator.run([(qc, observables)])
result = job.result()
print(result[0].data.evs)
