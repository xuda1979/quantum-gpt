import numpy as np
from qiskit.quantum_info import Statevector, Pauli

def zz_chain_expectation():
    """<GHZ| Z0Z1 |GHZ> = 1 (perfect pair correlation on a Bell-like cut)."""
    ghz = (Statevector.from_label("000") + Statevector.from_label("111")) / (2 ** 0.5)
    op = Pauli("ZZI")
    evolved = ghz.evolve(op)
    return float(np.real(evolved.expectation_value(op)))
