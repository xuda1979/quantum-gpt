import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import RZZGate

def rzz_in_toffoli_basis():
    """RZZ(pi/4) decomposes to exactly 2 CX gates in the cx/rz/h basis."""
    qc = QuantumCircuit(2)
    qc.append(RZZGate(np.pi / 4), [0, 1])
    out = transpile(qc, basis_gates=["cx", "rz", "h"],
                    optimization_level=0)
    return sum(1 for inst in out.data if inst.operation.name == "cx")
