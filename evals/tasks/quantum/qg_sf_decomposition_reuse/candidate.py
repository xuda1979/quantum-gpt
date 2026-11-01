import numpy as np
from qiskit.quantum_info import Statevector, schmidt_decomposition

def schmidt_equal_split():
    """|01> has exactly one nonzero Schmidt coefficient across the 0|1 cut."""
    sv = Statevector.from_label("01")
    terms = schmidt_decomposition(sv, [0])
    return int(sum(1 for coeff, _, _ in terms if abs(coeff) > 1e-10))
