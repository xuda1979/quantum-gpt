import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.quantum_info import Statevector

def bound_rx_angle():
    """RX(pi/2)|0> = (|0> - i|1>)/sqrt(2)."""
    theta = Parameter("theta")
    qc = QuantumCircuit(1)
    qc.rx(theta, 0)
    bound = qc.assign_parameters({theta: np.pi / 2})
    return np.asarray(Statevector(bound))
