import numpy as np
from qiskit.quantum_info import Statevector, partial_trace, DensityMatrix

def trace_out_first():
    """Tracing qubit 0 of |10> leaves qubit 1 in |1>."""
    sv = Statevector.from_label("10")
    dm = partial_trace(sv, [0])
    return np.asarray(dm)
