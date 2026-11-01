from qiskit import QuantumCircuit

def barrier_split_count():
    """x, barrier, x, x -> 4 data entries."""
    qc = QuantumCircuit(3)
    qc.x(0)
    qc.barrier()
    qc.x(1)
    qc.x(2)
    return len(qc.data)
