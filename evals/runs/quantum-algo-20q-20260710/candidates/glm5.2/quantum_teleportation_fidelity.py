from qiskit.circuit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp

estimator = StatevectorEstimator()
circuit = QuantumCircuit(2)
circuit.h(0)
circuit.cx(0, 1)
observable = SparsePauliOp.from_list([("XX", 1), ("YY", -1)])
job = estimator.run([(circuit, observable)])
result = job.result()
print(result[0].data.evs)
