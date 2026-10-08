import math


def _iterate(amplitudes: list[float], marked: list[int]) -> list[float]:
    """One Grover iteration on real amplitudes.

    Steps:
      1. Oracle: flip the sign of marked amplitudes.
      2. Diffusion: 2*mean - amp for every amplitude.
    """
    n = len(amplitudes)
    # Oracle
    amps = [(-amplitudes[i] if i in marked else amplitudes[i]) for i in range(n)]
    # Diffusion
    mean = sum(amps) / n
    return [2 * mean - a for a in amps]


def grover_state_after_iterations(
    amplitudes: list[float], marked: list[int], iterations: int
) -> list[float]:
    """Apply `iterations` Grover iterations to the initial real amplitude vector.

    `marked` is the list of indices of the marked states. Amplitudes are
    assumed real (Grover diffusion preserves reality when starting real).
    """
    if iterations < 0:
        raise ValueError("iterations must be non-negative")
    if not amplitudes:
        raise ValueError("amplitudes must be non-empty")
    n = len(amplitudes)
    marked_set = set(marked)
    if any(m < 0 or m >= n for m in marked_set):
        raise ValueError("marked index out of range")

    amps = list(amplitudes)
    for _ in range(iterations):
        amps = _iterate(amps, sorted(marked_set))
    return amps


def uniform_initial_state(n: int) -> list[float]:
    """Return the uniform real superposition of n basis states."""
    if n <= 0:
        raise ValueError("n must be positive")
    return [1.0 / math.sqrt(n)] * n
