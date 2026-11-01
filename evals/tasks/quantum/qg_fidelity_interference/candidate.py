import numpy as np
from qiskit.quantum_info import Statevector, DensityMatrix, state_fidelity

def plus_state_fidelity():
    """Fidelity between |+> as a Statevector and as a DensityMatrix."""
    plus = Statevector.from_label("+")
    dm = DensityMatrix(plus)
    return float(state_fidelity(plus, dm))
