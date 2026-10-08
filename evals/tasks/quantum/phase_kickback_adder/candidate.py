def controlled_phase_angle(k: int, n: int) -> float:
    """Return the phase angle 2*pi / 2^k applied by a controlled-phase
    rotation CP(2*pi/2^k) used in quantum adder circuits.

    Here k >= 1 indexes the rotation strength; for k=1 the rotation is
    a controlled-Z (pi phase) up to convention; we use 2*pi/2^k.
    """
    if k < 1 or k > n:
        raise ValueError("k must be in 1..n")
    if n < 1:
        raise ValueError("n must be positive")
    import math

    return 2.0 * math.pi / (1 << k)


def qft_adder_phase_schedule(n: int) -> list[list[float]]:
    """Return the n x n lower-triangular phase schedule for a QFT-based adder.

    schedule[i][j] (for j <= i) is the phase applied between control qubit i
    and target qubit j; schedule[i][j] = 0 for j > i. The diagonal entries
    represent single-qubit phase rotations; off-diagonal entries are
    controlled-phase angles.
    """
    if n < 1:
        raise ValueError("n must be positive")
    import math

    schedule = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            # Distance k = i - j + 1 (rotation strength)
            k = i - j + 1
            schedule[i][j] = 2.0 * math.pi / (1 << k)
    return schedule


def phase_kickback_sum(a: int, b: int, n: int) -> int:
    """Classically emulate the QFT-based modular adder on n qubits.

    Given two n-bit integers a and b in [0, 2^n), return (a + b) mod 2^n,
    which is what the quantum adder computes on the QFT-encoded target
    register after the phase-kickback controlled rotations.
    """
    if n < 1:
        raise ValueError("n must be positive")
    if not (0 <= a < (1 << n)) or not (0 <= b < (1 << n)):
        raise ValueError("a and b must be in [0, 2^n)")
    return (a + b) % (1 << n)
