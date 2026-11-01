from qiskit import QuantumCircuit
from qiskit.quantum_info import CNOTDihedral

def cnotdihedral_phase_poly():
    """X0 then CX(0,1) then Z1: the phase polynomial gains x1 terms."""
    qc = QuantumCircuit(2)
    qc.x(0)
    qc.cx(0, 1)
    qc.z(1)
    elem = CNOTDihedral(qc)
    return str(elem.poly)
