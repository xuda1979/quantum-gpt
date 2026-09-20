import math


def shor_codeword(logical: int) -> list[float]:
    """
    One Shor-code codeword as a length-512 amplitude list (qubit 0 = MSB).

    |0_L> = (|000>+|111>)(|000>+|111>)(|000>+|111>) / (2 sqrt(2))
    |1_L> = (|000>-|111>)(|000>-|111>)(|000>-|111>) / (2 sqrt(2))
    """
    s2 = 1.0 / math.sqrt(2)
    block = [0.0] * 8
    block[0] = s2
    block[7] = s2 if logical == 0 else -s2
    out = [1.0]
    for _ in range(3):
        out = [a * c for a in out for c in block]
    return out


def shor_stabilizer_generators() -> list[str]:
    """
    The 8 Shor-code stabilizer generators as length-9 Pauli strings
    (qubit 0 left to right): six Z-pair checks (bit-flip correction) and
    two X-block checks (phase-flip correction).
    """
    return [
        "ZZIIIIIII",  # Z0 Z1
        "IZZIIIIII",  # Z1 Z2
        "IIIZZIIII",  # Z3 Z4
        "IIIIZZIII",  # Z4 Z5
        "IIIIIIZZI",  # Z6 Z7
        "IIIIIIIZZ",  # Z7 Z8
        "XXXXXXIII",  # X0..X5
        "IIIXXXXXX",  # X3..X8
    ]


def _pauli_masks(pauli: str) -> tuple[int, int]:
    """Return (xmask, zmask) over 9 qubits; qubit q sits at bit (8-q)."""
    xmask = 0
    zmask = 0
    for q, ch in enumerate(pauli):
        bit = 1 << (8 - q)
        if ch in ("X", "Y"):
            xmask |= bit
        if ch in ("Z", "Y"):
            zmask |= bit
    return xmask, zmask


def pauli_eigenvalue(pauli: str, state: list[float]) -> complex:
    """
    <state| P |state> for a Pauli string P on 9 qubits.

    P acts as phase(i) |i XOR xmask> with phase(i) = (-1)^(popcount(i & zmask)).
    For codewords the result is exactly +/-1.
    """
    xmask, zmask = _pauli_masks(pauli)
    n = len(state)
    out = [0.0] * n
    for i, a in enumerate(state):
        phase = (-1.0) ** bin(i & zmask).count("1")
        out[i ^ xmask] += phase * a
    return sum(complex(a) * complex(b) for a, b in zip(state, out))


def pauli_commute(a: str, b: str) -> bool:
    """
    Two Pauli strings commute iff their symplectic inner products vanish
    (an even number of anticommuting qubit pairs).
    """
    ax, az = _pauli_masks(a)
    bx, bz = _pauli_masks(b)
    return bin(ax & bz).count("1") % 2 == bin(bx & az).count("1") % 2
