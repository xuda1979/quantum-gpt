import numpy as np
from qiskit.quantum_info import random_unitary

def seeded_random_unitary():
    """Deterministic 4x4 unitary via seed; must be unitary."""
    u = random_unitary(4, seed=7)
    return u
