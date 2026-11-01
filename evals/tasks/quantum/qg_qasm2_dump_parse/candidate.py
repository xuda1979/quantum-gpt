from qiskit import QuantumCircuit
from qiskit import qasm2

def qasm2_roundtrip_qubits():
    """QASM2 text roundtrip must preserve qubit count."""
    qc = QuantumCircuit(3)
    qc.x(2)
    text = qasm2.dumps(qc)
    loaded = qasm2.loads(text)
    return loaded.num_qubits
