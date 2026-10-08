--- BEGIN REFERENCE CANDIDATE ---
from typing import List

def phase_to_register_bits(phase: float, n_qubits: int) -> List[int]:
    """
    Map a fractional phase [0, 1) into a fixed-length register bit vector.
    """
    if n_qubits <= 0:
        raise ValueError("n_qubits must be positive")
    if not (0.0 <= phase < 1.0):
        raise ValueError("phase must be in [0, 1)")

    scale = 1 << n_qubits
    integer_rep = int(phase * scale)
    bits: List[int] = []
    for shift in range(n_qubits - 1, -:: ,生素ὗ',
譡@endsection"
, their有关
...",
–%\-
