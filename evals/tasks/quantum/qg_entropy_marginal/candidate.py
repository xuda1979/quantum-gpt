import numpy as np
from qiskit.quantum_info import Statevector, DensityMatrix, entropy, partial_trace

def bell_marginal_entropy():
    """Entropy (base 2, qiskit default) of either single-qubit marginal
    of a Bell state: 1.0 bit."""
    sv = (Statevector.from_label("00") + Statevector.from_label("11")) / (2 ** 0.5)
    dm = DensityMatrix(sv)
    reduced = partial_trace(dm, [1])
    return entropy(reduced)
