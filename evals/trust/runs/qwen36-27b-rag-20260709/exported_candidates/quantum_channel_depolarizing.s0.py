import math


def _mat_mul(a, b):
    """Multiply two 2x2 matrices."""
    return [
        [a[0][0] * b[0][0] + a[0][1] * b[1][0], a[0][0] * b[0][1] + a[0][1] * b[1][1]],
        [a[1][0] * b[0][0] + a[1][1] * b[1][0], a[1][0] * b[0][1] + a[1][1] * b[1][1]],
    ]


def _mat_add(a, b):
    return [[a[i][j] + b[i][j] for j in range(2)] for i in range(2)]


def _mat_scale(s, m):
    return [[s * m[i][j] for j in range(2)] for i in range(2)]


def _adjoint(m):
    return [[m[j][i] for j in range(2)] for i in range(2)]


def _kraus_apply(kraus_ops, rho):
    """Apply a quantum channel: rho' = sum_k K_k rho K_k^dag."""
    result = [[0.0, 0.0], [0.0, 0.0]]
    for k in kraus_ops:
        kd = _adjoint(k)
        term = _mat_mul(_mat_mul(k, rho), kd)
        result = _mat_add(result, term)
    return result


def depolarizing_channel(rho, p):
    """
    Apply the depolarizing channel with probability p:
    rho' = (1 - p) * rho + p * (I / 2)

    p=0: no noise (identity channel)
    p=1: fully depolarizing (output is maximally mixed)
    """
    identity_half = [[0.5, 0.0], [0.0, 0.5]]
    return _mat_add(_mat_scale(1 - p, rho), _mat_scale(p, identity_half))


def amplitude_damping_channel(rho, gamma):
    """
    Apply the amplitude damping channel with damping rate gamma.
    K0 = [[1, 0], [0, sqrt(1-gamma)]]
    K1 = [[0, sqrt(gamma)], [0, 0]]
    """
    sg = math.sqrt(gamma)
    s1g = math.sqrt(1 - gamma)
    K0 = [[1, 0], [0, s1g]]
    K1 = [[0, sg], [0, 0]]
    return _kraus_apply([K0, K1], rho)


def channel_fidelity(rho, sigma):
    """
    Compute the quantum state fidelity F(rho, sigma) for 2x2 density matrices.
    Uses the 2x2 closed-form:
    F = Tr(rho sigma) + 2*sqrt(det(rho)*det(sigma))
    """
    tr_prod = sum(rho[i][j] * sigma[j][i] for i in range(2) for j in range(2))
    det_rho = rho[0][0] * rho[1][1] - rho[0][1] * rho[1][0]
    det_sigma = sigma[0][0] * sigma[1][1] - sigma[0][1] * sigma[1][0]
    f = tr_prod + 2 * math.sqrt(max(det_rho * det_sigma, 0.0))
    return f
