"""One-qubit phase-flip channel with Kraus operators (NumPy/SciPy only).

E(rho) = (1-p) rho + p Z rho Z, parameterized by the Kraus pair
K0 = sqrt(1-p) I, K1 = sqrt(p) Z. The channel is applied to |+><+| and
to a seeded random mixed state; purity, trace distance and squared
Uhlmann fidelity are computed with stable Hermitian eigendecompositions
(scipy.linalg.eigh). Outputs must be Hermitian positive semidefinite
with unit trace and the fidelity must stay in [0, 1]."""

from __future__ import annotations

import math

import numpy as np
from scipy.linalg import eigh

I2 = np.eye(2, dtype=complex)
Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)


def kraus_operators(p: float) -> list[np.ndarray]:
    """[sqrt(1-p) I, sqrt(p) Z] implementing E(rho) = (1-p)rho + p Z rho Z."""
    return [math.sqrt(1.0 - p) * I2, math.sqrt(p) * Z]


def completeness_deviation(ks: list[np.ndarray]) -> float:
    """max |sum_k K_k^dagger K_k - I| over all entries."""
    total = np.zeros((2, 2), dtype=complex)
    for k in ks:
        total += k.conj().T @ k
    return float(np.max(np.abs(total - I2)))


def apply_channel(rho: np.ndarray, ks: list[np.ndarray]) -> np.ndarray:
    """E(rho) = sum_k K_k rho K_k^dagger."""
    out = np.zeros((2, 2), dtype=complex)
    for k in ks:
        out += k @ rho @ k.conj().T
    return out


def purity(rho: np.ndarray) -> float:
    """tr(rho^2) computed from eigenvalues (Hermitian-stable)."""
    eigvals = eigh((rho + rho.conj().T) / 2.0, eigvals_only=True)
    return float(np.sum(eigvals**2))


def trace_distance(rho: np.ndarray, sigma: np.ndarray) -> float:
    """(1/2) tr |rho - sigma| = (1/2) sum |eigenvalues of difference|."""
    diff = (rho - sigma + (rho - sigma).conj().T) / 2.0
    eigvals = eigh(diff, eigvals_only=True)
    return float(0.5 * np.sum(np.abs(eigvals)))


def _sqrtm_psd(mat: np.ndarray) -> np.ndarray:
    """Principal matrix square root of a Hermitian PSD matrix."""
    vals, vecs = eigh(mat)
    vals = np.clip(vals, 0.0, None)
    return (vecs * np.sqrt(vals)) @ vecs.conj().T


def fidelity_sq(rho: np.ndarray, sigma: np.ndarray) -> float:
    """Squared Uhlmann fidelity (tr sqrt(sqrt(rho) sigma sqrt(rho)))^2."""
    rho = (rho + rho.conj().T) / 2.0
    sigma = (sigma + sigma.conj().T) / 2.0
    sqrt_rho = _sqrtm_psd(rho)
    inner = _sqrtm_psd(sqrt_rho @ sigma @ sqrt_rho)
    f = np.trace(inner).real
    return float(np.clip(f * f, 0.0, 1.0))


def plus_state() -> np.ndarray:
    """|+><+| = (|0> + |1>)(<0| + <1|) / 2."""
    return np.array([[0.5, 0.5], [0.5, 0.5]], dtype=complex)


def random_mixed_state(seed: int = 1) -> np.ndarray:
    """Seeded random mixed state via a Bloch vector with r <= 1."""
    rng = np.random.RandomState(seed)
    vec = rng.uniform(-1.0, 1.0, size=3)
    r = math.sqrt(float(np.sum(vec * vec)))
    if r > 1.0:
        vec = vec / r
    x, y, z = vec
    return 0.5 * (I2 + x * X + y * (1j * np.array([[0, -1], [1, 0]], dtype=complex)) + z * Z)


def run_checks(p: float = 0.18, seed: int = 1) -> dict:
    """All channel quantities for the harness."""
    ks = kraus_operators(p)
    rho_plus = plus_state()
    out_plus = apply_channel(rho_plus, ks)
    rho_rand = random_mixed_state(seed)
    out_rand = apply_channel(rho_rand, ks)
    eig_plus = eigh((out_plus + out_plus.conj().T) / 2.0, eigvals_only=True)
    return {
        "completeness_dev": completeness_deviation(ks),
        "rho_plus_01": float(np.real(out_plus[0, 1])),
        "rho_plus_trace": float(np.trace(out_plus).real),
        "purity_plus": purity(out_plus),
        "psd_plus": bool(np.min(eig_plus) >= -1e-12),
        "fidelity_plus": fidelity_sq(rho_plus, out_plus),
        "purity_rand_before": purity(rho_rand),
        "purity_rand_after": purity(out_rand),
        "trace_rand": float(np.trace(out_rand).real),
        "trace_distance_same": trace_distance(out_plus, out_plus),
        "fidelity_rand": fidelity_sq(rho_rand, out_rand),
    }


def main():
    p = 0.18
    result = run_checks(p=p, seed=1)
    for key, value in result.items():
        print(key, "=", value)
    assert result["completeness_dev"] < 1e-12, "sum K^dagger K must equal I"
    assert abs(result["rho_plus_trace"] - 1.0) < 1e-12, "channel output must have unit trace"
    assert result["psd_plus"], "channel output must be positive semidefinite"
    assert abs(result["rho_plus_01"] - (1.0 - 2 * p) / 2.0) < 1e-12
    assert 0.0 <= result["fidelity_plus"] <= 1.0, "fidelity must stay in [0, 1]"
    assert 0.0 <= result["fidelity_rand"] <= 1.0, "fidelity must stay in [0, 1]"


if __name__ == "__main__":
    main()
