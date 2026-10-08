# Phase estimation circuit implementation
class PhaseEstimator:
    def __init__(self, qubits: int):
        self.qubits = qubits

    def phase_estimation(self, phase: float, n_bits: int) -> int:
        """Return the measured bitstring corresponding to the nth power of e^i*phase."""
        raise NotImplementedError()

    @classmethod
    def from_measurement(cls, measurement: int, n_bits: int) -> "PhaseEstimator":
        """Convert a binary string into an instance of this class."""
        raise NotImplementedError()
