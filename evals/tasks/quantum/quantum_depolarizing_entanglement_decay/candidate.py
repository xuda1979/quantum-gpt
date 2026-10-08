def bell_density_matrix() -> list[list[float]]:
    """Density matrix of the Bell state |Phi+> = (|00> + |11>)/sqrt(2)."""
    return [
        [0.5, 0.0, 0.0, 0.5],
        [0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0],
        [0.5, 0.0, 0.0, 0.5],
    ]


def two_qubit_depolarizing(rho: list[list[float]], p: float) -> list[list[float]]:
    """
    Two-qubit depolarizing channel:

        rho -> (1 - p) rho + (p / 4) I_4

    With probability p the state is replaced by the maximally mixed state
    I_4/4 of the 4-dimensional two-qubit space (dimension 4, so the
    white-noise weight is p/4).
    """
    n = len(rho)
    out = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            out[i][j] = (1.0 - p) * rho[i][j] + (p / 4.0) * (1.0 if i == j else 0.0)
    return out


def werner_state(p: float) -> list[list[float]]:
    """
    Werner state: (1 - p)|Phi+><Phi+| + p I_4 / 4.

    Identical to applying the two-qubit depolarizing channel with the same
    noise parameter to the Bell state.
    """
    return two_qubit_depolarizing(bell_density_matrix(), p)


def fidelity_to_bell(rho: list[list[float]]) -> float:
    """Fidelity <Phi+| rho |Phi+> = (rho00 + rho33)/2 + Re(rho03)."""
    return 0.5 * (rho[0][0] + rho[3][3]) + rho[0][3]
