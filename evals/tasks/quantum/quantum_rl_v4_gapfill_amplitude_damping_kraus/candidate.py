"""Amplitude damping channel with an exact required API.

K0 damps the excited-state amplitude by sqrt(1-gamma); K1 maps |1> to
sqrt(gamma)|0>. This task grades the entry-point contract itself: every
required function must exist under its exact name.
"""

from __future__ import annotations

import math

import numpy as np


def kraus(gamma):
    """[K0, K1] for E(rho) = K0 rho K0^dag + K1 rho K1^dag."""
    k0 = np.array([[1.0, 0.0], [0.0, math.sqrt(1.0 - gamma)]], dtype=complex)
    k1 = np.array([[0.0, math.sqrt(gamma)], [0.0, 0.0]], dtype=complex)
    return [k0, k1]


def apply(rho, ks):
    """sum_k K rho K^dagger."""
    out = np.zeros(rho.shape, dtype=complex)
    for k in ks:
        out += k @ rho @ k.conj().T
    return out


def purity(rho):
    """tr(rho^2) via Hermitian-stable eigenvalues."""
    h = (rho + rho.conj().T) / 2.0
    vals = np.linalg.eigvalsh(h)
    return float(np.sum(vals**2))


def excited_state_survival(t, gamma):
    """Probability the excited state survives time t: exp(-gamma t)."""
    return float(math.exp(-gamma * t))


def _random_mixed_state(seed=1):
    """Seeded random two-level density matrix (Bloch vector, r <= 1)."""
    rng = np.random.RandomState(seed)
    vec = rng.uniform(-1.0, 1.0, size=3)
    r = math.sqrt(float(np.sum(vec * vec)))
    if r > 1.0:
        vec = vec / r
    x, y, z = vec
    I2 = np.eye(2, dtype=complex)
    X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
    Y = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex)
    Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
    return 0.5 * (I2 + x * X + y * Y + z * Z)


def run_checks(gamma=0.12, t=1.0, seed=1):
    """All channel quantities for the harness."""
    ks = kraus(gamma)
    total = np.zeros((2, 2), dtype=complex)
    for k in ks:
        total += k.conj().T @ k
    ket1 = np.array([[0.0], [1.0]], dtype=complex)
    rho1 = ket1 @ ket1.conj().T
    out1 = apply(rho1, ks)
    rho_rand = _random_mixed_state(seed)
    pur_before = purity(rho_rand)
    pur_after = purity(apply(rho_rand, ks))
    return dict(
        ks_ok=float(np.max(np.abs(total - np.eye(2)))),
        rho1_00=float(np.real(out1[0, 0])),
        purity_before=pur_before,
        purity_after=pur_after,
    )


def main():
    gamma = 0.12
    res = run_checks(gamma=gamma, t=1.0, seed=1)
    for key, value in res.items():
        print(key, "=", value)
    assert res["ks_ok"] < 1e-12, "Kraus set must be complete"
    assert abs(res["rho1_00"] - gamma) < 1e-12, "population decay must leave gamma"
    ket1 = np.array([[0.0], [1.0]], dtype=complex)
    out1 = apply(ket1 @ ket1.conj().T, kraus(gamma))
    expected = (1.0 - gamma) ** 2 + gamma**2
    assert abs(purity(out1) - expected) < 1e-9, "purity must equal (1-g)^2 + g^2"
    assert res["purity_after"] < res["purity_before"], "purity must drop"
    print("amplitude damping OK")


if __name__ == "__main__":
    main()
