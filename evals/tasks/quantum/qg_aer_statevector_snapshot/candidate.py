from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector

def ghz_save_statevector():
    """GHZ via save_statevector on Aer."""
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(0, 2)
    qc.save_statevector()
    sim = AerSimulator(method="statevector")
    res = sim.run(qc).result()
    return res.data(0)["statevector"]
