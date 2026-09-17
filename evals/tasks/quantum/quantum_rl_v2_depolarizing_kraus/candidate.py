"""One-qubit depolarizing channel (numpy/scipy only).

Kraus convention: E(rho) = (1-p) rho + p/3 (X rho X + Y rho Y + Z rho Z).
Kraus operators: sqrt(1-p) I, sqrt(p/3) X, sqrt(p/3) Y, sqrt(p/3) Z.
Applies the channel to |+><+| and to a seeded random mixed state; provides
purity, trace distance, and squared Uhlmann fidelity via stable Hermitian
eigendecompositions, with PSD / unit-trace / fidelity-in-[0,1] assertions."""

import numpy as np

I2 = np.eye(2, dtype=complex)
X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
Y = np.array([[0.0, -1j], [1j, 0.0]], dtype=complex)
Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)

PLUS = 0.5 * np.ones((2, 2), dtype=complex)  # |+><+| = [[.5, .5], [.5, .5]]


def depolarizing_kraus(p):
    """Four Kraus operators for the depolarizing channel at strength p."""
    return [
        np.sqrt(1.0 - p) * I2,
        np.sqrt(p / 3.0) * X,
        np.sqrt(p / 3.0) * Y,
        np.sqrt(p / 3.0) * Z,
    ]


def kraus_completeness(kraus):
    """sum_k K_k^dagger K_k; should equal identity."""
    total = np.zeros((2, 2), dtype=complex)
    for k in kraus:
        total = total + k.conj().T @ k
    return total


def apply_channel(kraus, rho):
    """Apply the CP map sum_k K_k rho K_k^dagger."""
    out = np.zeros_like(np.asarray(rho, dtype=complex))
    for k in kraus:
        out = out + k @ rho @ k.conj().T
    return out


def random_mixed_state(seed=0):
    """Seeded random valid density matrix via a Ginibre-style ensemble."""
    rng = np.random.default_rng(seed)
    g = rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2))
    rho = g @ g.conj().T
    return rho / np.trace(rho)


def purity(rho):
    return float(np.real(np.trace(rho @ rho)))


def trace_distance(rho, sigma):
    """(1/2) Tr |rho - sigma| = (1/2) sum |eigenvalues| of the difference."""
    diff = np.asarray(rho, dtype=complex) - np.asarray(sigma, dtype=complex)
    return float(0.5 * np.sum(np.abs(np.linalg.eigvalsh(diff))))


def uhlmann_fidelity_sq(rho, sigma):
    """Squared Uhlmann fidelity F^2 = (Tr sqrt(sqrt(rho) sigma sqrt(rho)))^2.

    Uses stable Hermitian eigendecompositions (scipy sqrtm with the PSD
    square root of rho taken via eigendecomposition).
    """
    rho = np.asarray(rho, dtype=complex)
    sigma = np.asarray(sigma, dtype=complex)
    # stable PSD square root of rho via Hermitian eigendecomposition
    w, v = np.linalg.eigh(rho)
    w = np.clip(w, 0.0, None)
    sqrt_rho = (v * np.sqrt(w)) @ v.conj().T
    inner = sqrt_rho @ sigma @ sqrt_rho
    w2, v2 = np.linalg.eigh(inner)
    w2 = np.clip(w2, 0.0, None)
    sqrt_inner = (v2 * np.sqrt(w2)) @ v2.conj().T
    return float(np.real(np.trace(sqrt_inner)) ** 2)


def main():
    p = 0.25
    kraus = depolarizing_kraus(p)
    comp = kraus_completeness(kraus)
    assert np.allclose(comp, I2, atol=1e-12), f"sum K^dag K != I: {comp}"
    rho_plus = apply_channel(kraus, PLUS)
    rho_rand = apply_channel(kraus, random_mixed_state(seed=7))
    for name, rho in (("E(|+><+|)", rho_plus), ("E(rho_rand)", rho_rand)):
        assert np.allclose(rho, rho.conj().T, atol=1e-12), f"{name} not Hermitian"
        evals = np.linalg.eigvalsh(rho)
        assert np.min(evals) >= -1e-12, f"{name} not PSD"
        assert abs(np.trace(rho) - 1.0) < 1e-12, f"{name} trace != 1"
    f = uhlmann_fidelity_sq(rho_plus, rho_rand)
    assert 0.0 <= f <= 1.0 + 1e-12, f"fidelity {f} outside [0, 1]"
    print("purity(E(|+><+|)) =", purity(rho_plus))
    print("trace_distance(E(|+><+|), |0><0|) =", trace_distance(rho_plus, np.diag([1.0, 0.0])))
    print("fidelity_sq =", f)


if __name__ == "__main__":
    main()
