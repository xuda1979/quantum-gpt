from qiskit import QuantumCircuit

def three_sat_mark():
    """Phase oracle marking |111> via H-MCZ-H sandwich on target bit."""
    qc = QuantumCircuit(3)
    qc.h(2)
    qc.mcx([0, 1], 2)
    qc.h(2)
    return qc
