import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter

def w_state_3():
    """W state via Ry + negative-control CH + negative-control Toffoli."""
    import numpy as np
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(3)
    # P(q0=1) = 1/3
    qc.ry(2 * np.arcsin(1 / np.sqrt(3)), 0)
    # on the q0=0 branch (prob 2/3): H on q1 via X-sandwich
    qc.x(0)
    qc.ch(0, 1)
    # negative-control Toffoli: flip q2 iff q0=0 AND q1=0
    qc.x(1)
    qc.ccx(0, 1, 2)
    qc.x(1)
    qc.x(0)
    return qc
