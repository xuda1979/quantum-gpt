import numpy as np
from qiskit.quantum_info import Clifford
from qiskit.circuit.library import HGate

def clifford_double_h():
    """Compose H.H on one qubit; return the Clifford (identity)."""
    h = Clifford(HGate())
    return h.compose(h)
