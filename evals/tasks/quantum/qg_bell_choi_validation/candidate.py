import numpy as np
from qiskit.quantum_info import DensityMatrix, Choi, Statevector, Kraus

def bell_choi_channel():
    """Return the DensityMatrix left after sending qubit 0 of a Bell
    pair through the fully-dephasing channel."""
    bell = (Statevector.from_label("00") + Statevector.from_label("11")) / (2 ** 0.5)
    K0 = np.sqrt(0.5) * np.eye(2, dtype=complex)
    K1 = np.sqrt(0.5) * np.array([[1, 0], [0, -1]], dtype=complex)
    chan = Choi(Kraus([K0, K1]))
    dm = DensityMatrix(bell).evolve(chan, qargs=[0])
    return dm
