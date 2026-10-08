import cmath
import math


def pauli_matrix(name: str) -> list[list[complex]]:
    """Return the 2x2 Pauli matrix for 'I', 'X', 'Y', or 'Z'."""
    if name == "I":
        return [[1, 0], [0, 1]]
    if name == "X":
        return [[0, 1], [1, 0]]
    if name == "Y":
        return [[0, -1j], [1j, 0]]
    if name == "Z":
        return [[1, 0], [0, -1]]
    raise ValueError(f"Unknown Pauli: {name}")


def matrix_exp_hermitian(h: list[list[complex]], theta: float) -> list[list[complex]]:
    """
    Compute exp(-i * theta * H) for a 2x2 Hermitian matrix H.

    Uses eigendecomposition: H = U diag(e1,e2) U^dag
    exp(-i*theta*H) = U diag(e^{-i*theta*e1}, e^{-i*theta*e2}) U^dag
    """
    a = complex(h[0][0])
    b = complex(h[0][1])
    d = complex(h[1][1])

    # Eigenvalues of 2x2 Hermitian: (a+d)/2 +/- sqrt(((a-d)/2)^2 + |b|^2)
    half_trace = (a + d) / 2
    disc = math.sqrt(((a - d).real / 2) ** 2 + abs(b) ** 2)

    e1 = half_trace.real + disc
    e2 = half_trace.real - disc

    phase1 = cmath.exp(-1j * theta * e1)
    phase2 = cmath.exp(-1j * theta * e2)

    if disc < 1e-15:
        # Proportional to identity
        return [[phase1, 0], [0, phase1]]

    # Eigenvectors
    cos_a = disc
    # |v1> = [b, e1-a], normalized
    v1 = [b, e1 - a.real]
    n1 = math.sqrt(abs(v1[0]) ** 2 + abs(v1[1]) ** 2)
    if n1 < 1e-15:
        v1 = [1, 0]
        n1 = 1
    v1 = [v1[0] / n1, v1[1] / n1]

    v2 = [-v1[1].conjugate(), v1[0].conjugate()]

    # exp = phase1 * |v1><v1| + phase2 * |v2><v2|
    result = [[0j, 0j], [0j, 0j]]
    for i in range(2):
        for j in range(2):
            result[i][j] = phase1 * v1[i] * v1[j].conjugate() + phase2 * v2[i] * v2[j].conjugate()
    return result


def _mat_vec(m, v):
    n = len(v)
    return [sum(m[i][j] * v[j] for j in range(n)) for i in range(n)]


def trotter_evolve(
    state: list[complex],
    hamiltonian_terms: list[tuple[float, str]],
    t: float,
    steps: int,
) -> list[complex]:
    """
    Evolve a 1-qubit state under H = sum_k coeff_k * Pauli_k using
    first-order Trotterization with the given number of steps.

    exp(-i*H*t) ~ (prod_k exp(-i*coeff_k*Pauli_k*dt))^steps
    """
    dt = t / steps
    current = list(state)
    for _ in range(steps):
        for coeff, pauli_name in hamiltonian_terms:
            mat = pauli_matrix(pauli_name)
            u = matrix_exp_hermitian(mat, coeff * dt)
            current = _mat_vec(u, current)
    return current
