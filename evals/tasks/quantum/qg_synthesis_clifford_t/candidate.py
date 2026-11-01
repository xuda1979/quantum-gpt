import numpy as np
from qiskit.quantum_info import random_clifford, Operator
from qiskit.synthesis import synth_clifford_full

def clifford_synth_2q():
    """Synthesize a seeded Clifford and check operator equality."""
    cliff = random_clifford(2, seed=13)
    qc = synth_clifford_full(cliff)
    return bool(np.allclose(Operator(qc).data, cliff.to_matrix(),
                            atol=1e-9))
