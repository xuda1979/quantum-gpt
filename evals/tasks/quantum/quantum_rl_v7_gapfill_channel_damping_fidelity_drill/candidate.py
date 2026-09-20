"""Reference completion: depolarizing + amplitude-damping + channel fidelity.

Mined by C-0007 for holdout task quantum_channel_depolarizing, whose grader
locks _REQUIRED_FUNCTIONS = (depolarizing_channel, amplitude_damping_channel,
channel_fidelity). Enforced semantics, tolerance 1e-6:
  depolarizing_channel(rho, p) = (1-p) rho + p I/2
  amplitude_damping_channel(rho, gamma) = K0 rho K0^T + K1 rho K1^T with
    K0 = [[1, 0], [0, sqrt(1-gamma)]], K1 = [[0, sqrt(gamma)], [0, 0]]
  channel_fidelity(rho, sigma) = Tr(rho sigma) + 2 sqrt(det(rho) det(sigma))
Dense 2x2 nested row lists in and out; standard library only.
"""

from __future__ import annotations

import math


def _scale(c, m):
    return [[c * m[0][0], c * m[0][1]], [c * m[1][0], c * m[1][1]]]


def _add(a, b):
    return [
        [a[0][0] + b[0][0], a[0][1] + b[0][1]],
        [a[1][0] + b[1][0], a[1][1] + b[1][1]],
    ]


def _mul(a, b):
    return [[a[i][0] * b[0][j] + a[i][1] * b[1][j] for j in range(2)] for i in range(2)]


def _transpose(m):
    return [[m[j][i] for j in range(2)] for i in range(2)]


def depolarizing_channel(rho, p):
    """Enforced grader form: (1-p) rho + p I/2 (not the Pauli comment form)."""
    identity_half = [[0.5, 0.0], [0.0, 0.5]]
    return _add(_scale(1.0 - p, rho), _scale(p, identity_half))


def amplitude_damping_channel(rho, gamma):
    """Grader Kraus pair: K0 = [[1, 0], [0, sqrt(1-gamma)]], K1 = [[0, sqrt(gamma)], [0, 0]]."""
    k0 = [[1.0, 0.0], [0.0, math.sqrt(1.0 - gamma)]]
    k1 = [[0.0, math.sqrt(gamma)], [0.0, 0.0]]
    return _add(
        _mul(_mul(k0, rho), _transpose(k0)),
        _mul(_mul(k1, rho), _transpose(k1)),
    )


def channel_fidelity(rho, sigma):
    """2x2 Uhlmann fidelity: F = Tr(rho sigma) + 2 sqrt(det(rho) det(sigma))."""
    tr = (
        rho[0][0] * sigma[0][0]
        + rho[0][1] * sigma[1][0]
        + rho[1][0] * sigma[0][1]
        + rho[1][1] * sigma[1][1]
    )
    det_rho = rho[0][0] * rho[1][1] - rho[0][1] * rho[1][0]
    det_sigma = sigma[0][0] * sigma[1][1] - sigma[0][1] * sigma[1][0]
    return tr + 2.0 * math.sqrt(max(det_rho * det_sigma, 0.0))


if __name__ == "__main__":
    rho0 = [[1.0, 0.0], [0.0, 0.0]]
    assert depolarizing_channel(rho0, 0.0) == rho0
    assert channel_fidelity(rho0, rho0) == 1.0
    assert channel_fidelity(rho0, [[0.0, 0.0], [0.0, 1.0]]) == 0.0
    assert abs(channel_fidelity(rho0, [[0.5, 0.0], [0.0, 0.5]]) - 0.5) <= 1e-6
