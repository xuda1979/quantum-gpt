from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp

estimator = StatevectorEstimator()
observable = SparsePauliOp("ZI")
job = estimator.run([(circuit, observable)])
result = job.result()
value = float(result[0].data.evs)
