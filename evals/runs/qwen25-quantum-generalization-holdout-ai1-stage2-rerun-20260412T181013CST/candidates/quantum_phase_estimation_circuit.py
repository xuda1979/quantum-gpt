# Reference implementation
import math


class PhaseEstimator:
    def __init__(self, qubits: int):
        self.qubits = qubits

    def phase_estimation(self, phase: float, n_bits: int) -> int:
        """Return integer measurement from nth bit of log base 2."""
        return int(math.floor(phase * 2**self.qubits))

    @classmethod
    def phase_from_measurement(cls, measurement: int, n_bits: int) -> float:
        """Convert integer measurement back to floating point phase."""
        return measurement / 2**n_bits
