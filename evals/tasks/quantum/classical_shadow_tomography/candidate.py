import random


def clifford_shadow_snapshot(outcome: int, n_qubits: int, clifford_id: int) -> list[list[complex]]:
    """Construct a single classical-shadow density-matrix snapshot for a
    computational-basis `outcome` of a random Clifford measurement on
    `n_qubits`.

    The standard median-of-means classical shadow estimator uses
        rho_hat = (d + 1) * U^dagger |b><b| U - I

    where d = 2^n, U is the Clifford unitary (here we use the identity for
    simplicity so that the snapshot lives in the computational basis), and
    |b> is the measured basis state.

    Returns a d x d complex matrix.
    """
    if n_qubits < 1:
        raise ValueError("n_qubits must be >= 1")
    d = 1 << n_qubits
    if not 0 <= outcome < d:
        raise ValueError("outcome must be in [0, 2^n)")
    # Build |b><b| in computational basis
    projector = [[0j] * d for _ in range(d)]
    projector[outcome][outcome] = 1.0 + 0j
    # rho_hat = (d + 1) |b><b| - I
    snapshot = [
        [(d + 1) * projector[i][j] - (1.0 + 0j if i == j else 0j) for j in range(d)]
        for i in range(d)
    ]
    return snapshot


def shadow_estimate_expectation(
    snapshots: list[list[list[complex]]], observable: list[list[complex]]
) -> float:
    """Estimate Tr(O * rho) by averaging per-snapshot estimates

    Tr(O * rho_hat_i)  over all snapshots i.
    """
    if not snapshots:
        raise ValueError("snapshots must be non-empty")
    d = len(observable)
    total = 0.0
    for snap in snapshots:
        # Compute Tr(O @ snap) = sum_{i,j} O[i][j] * snap[j][i]
        acc = 0.0 + 0j
        for i in range(d):
            for j in range(d):
                acc += observable[i][j] * snap[j][i]
        total += acc.real
    return total / len(snapshots)


def sample_shadow_snapshots(
    n_snapshots: int, n_qubits: int, seed: int = 0
) -> list[list[list[complex]]]:
    """Sample `n_snapshots` classical-shadow snapshots from a uniform
    random computational-basis distribution (toy estimator)."""
    if n_snapshots < 1:
        raise ValueError("n_snapshots must be >= 1")
    rng = random.Random(seed)
    d = 1 << n_qubits
    snaps = []
    for _ in range(n_snapshots):
        b = rng.randrange(d)
        snaps.append(clifford_shadow_snapshot(b, n_qubits, 0))
    return snaps
