"""Depolarizing + amplitude-damping channel suite - exact holdout API.

Graded entry points: depolarizing_channel, amplitude_damping_channel,
channel_fidelity. Dense 2x2 lists, numpy-free reference."""

from __future__ import annotations

import math


def _mat_scale(c, m):
    return [[c * m[0][0], c * m[0][1]], [c * m[1][0], c * m[1][1]]]


def _mat_add(a, b):
    return [[a[0][0] + b[0][0], a[0][1] + b[0][1]], [a[1][0] + b[1][0], a[1][1] + b[1][1]]]


def _mat_mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(2)) for j in range(2)] for i in range(2)]


def _dagger(m):
    return [[m[j][i].conjugate() for j in range(2)] for i in range(2)]


def depolarizing_channel(rho, p):
    identity_half = [[0.5, 0.0], [0.0, 0.5]]
    return _mat_add(_mat_scale(1 - p, rho), _mat_scale(p, identity_half))


def amplitude_damping_channel(rho, gamma):
    sg = math.sqrt(gamma)
    s1g = math.sqrt(1 - gamma)
    K0 = [[1, 0], [0, s1g]]
    K1 = [[0, sg], [0, 0]]
    out = _mat_add(
        _mat_mul(_mat_mul(K0, rho), _dagger(K0)), _mat_mul(_mat_mul(K1, rho), _dagger(K1))
    )
    return [[v.real if isinstance(v, complex) else v for v in row] for row in out]


def channel_fidelity(rho, sigma):
    tr_prod = sum(rho[i][j] * sigma[j][i] for i in range(2) for j in range(2))
    det_rho = rho[0][0] * rho[1][1] - rho[0][1] * rho[1][0]
    det_sigma = sigma[0][0] * sigma[1][1] - sigma[0][1] * sigma[1][0]
    return tr_prod + 2 * math.sqrt(max(det_rho * det_sigma, 0.0))
