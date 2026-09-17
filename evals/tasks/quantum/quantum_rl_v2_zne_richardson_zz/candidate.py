"""Zero-noise extrapolation by hand for <ZZ> on the Bell state, with a
two-qubit CX depolarizing error of probability p = 0.04.

The ideal state is |Phi+> = (|00>+|11>)/sqrt(2) with <ZZ> = 1. Locally
folded circuits replace CX by 1, 3, and 5 consecutive CX gates; every CX
is followed by the two-qubit depolarizing channel
Lambda_p(rho) = (1-p) rho + p I/4 (qiskit_aer depolarizing_error
convention), so <ZZ>_1 = 1 - p exactly and odd-fold expectations decay
geometrically. Exact density-matrix expectations are obtained by direct
superoperator-free matrix evolution in NumPy (CX conjugation plus the
channel applied gate by gate) -- exact, deterministic, version-safe.

The quadratic Richardson intercept with weights 15/8, -5/4, 3/8 at
scales (1, 3, 5) is closer to the noiseless value 1 than the scale-1
exact noisy value. Shot-based parity estimates (50000 seeded shots per
scale) report linear and quadratic intercepts with a binomial bootstrap
uncertainty; no brittle per-draw improvement assertion is made.
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

P = 0.04
S2 = np.sqrt(2.0)


def bell_zz_circuit(scale):
    """H(0), then 2*scale-1 consecutive CX(0,1) gates, no measurements."""
    n_cx = 2 * scale - 1
    qc = QuantumCircuit(2)
    qc.h(0)
    for _ in range(n_cx):
        qc.cx(0, 1)
    return qc


def _cx_matrix():
    """CX(0,1) with control q0 (LSB of the 2-qubit index) and target q1."""
    cx = np.zeros((4, 4), dtype=complex)
    for b in range(4):
        q0, q1 = b & 1, (b >> 1) & 1
        cx[((q1 ^ q0) << 1) | q0, b] = 1.0
    return cx


def _depolarize(rho, p):
    """Two-qubit depolarizing channel Lambda_p(rho) = (1-p) rho + p I/4."""
    return (1.0 - p) * rho + (p / 4.0) * np.eye(4, dtype=complex)


def exact_zz(scale, p=P):
    """<ZZ> after 2*scale-1 noisy CX gates, exact density-matrix evolution.

    Start from |+0> = (|00> + |10>)/sqrt(2) (H on qubit 0), then for each
    CX gate apply the unitary conjugation followed by the depolarizing
    channel, and finally take <ZZ> = Tr(rho (Z otimes Z)).
    """
    cx = _cx_matrix()
    rho = (
        np.outer(
            np.array([1.0, 1.0, 0.0, 0.0], dtype=complex),
            np.array([1.0, 1.0, 0.0, 0.0], dtype=complex).conj(),
        )
        / 2.0
    )
    zz = np.kron(np.diag([1.0, -1.0]), np.diag([1.0, -1.0])).astype(complex)
    for _ in range(2 * scale - 1):
        rho = cx @ rho @ cx.conj().T
        rho = _depolarize(rho, p)
    return float(np.real(np.trace(rho @ zz)))


def quadratic_richardson(e1, e3, e5):
    """Quadratic Richardson intercept with weights 15/8, -5/4, 3/8."""
    return (15.0 / 8.0) * e1 - (5.0 / 4.0) * e3 + (3.0 / 8.0) * e5


def linear_richardson(e1, e3):
    """Linear Richardson intercept through scales 1 and 3."""
    return 1.5 * e1 - 0.5 * e3


def shot_zz(scale, shots=50000, seed=1234):
    """Parity estimate of <ZZ> from seeded noisy Aer shots."""
    qc = bell_zz_circuit(scale)
    qc.measure_all()
    nm = NoiseModel()
    nm.add_all_qubit_quantum_error(depolarizing_error(P, 2), ["cx"])
    sim = AerSimulator(noise_model=nm)
    counts = sim.run(qc, shots=shots, seed_simulator=seed).result().get_counts()
    n = float(sum(counts.values()))
    par = sum(v for k, v in counts.items() if k.count("1") % 2 == 0)
    return 2.0 * par / n - 1.0


def zne_exact(p=P):
    """Exact density-matrix expectations + Richardson intercepts."""
    e1, e3, e5 = exact_zz(1, p), exact_zz(2, p), exact_zz(3, p)
    return {
        "e1": e1,
        "e3": e3,
        "e5": e5,
        "quadratic_intercept": quadratic_richardson(e1, e3, e5),
        "linear_intercept": linear_richardson(e1, e3),
        "noiseless": 1.0,
    }


def zne_shots(shots=50000, seed=1234, n_boot=100):
    """Shot-based intercepts with a binomial bootstrap uncertainty."""
    e1 = shot_zz(1, shots, seed)
    e3 = shot_zz(2, shots, seed)
    e5 = shot_zz(3, shots, seed)
    quad = quadratic_richardson(e1, e3, e5)
    lin = linear_richardson(e1, e3)

    rng = np.random.default_rng(seed)
    boot_quad = []
    boot_lin = []
    for _ in range(n_boot):
        b1 = 2.0 * rng.binomial(shots, (e1 + 1.0) / 2.0) / shots - 1.0
        b3 = 2.0 * rng.binomial(shots, (e3 + 1.0) / 2.0) / shots - 1.0
        b5 = 2.0 * rng.binomial(shots, (e5 + 1.0) / 2.0) / shots - 1.0
        boot_quad.append(quadratic_richardson(b1, b3, b5))
        boot_lin.append(linear_richardson(b1, b3))
    return {
        "e1": e1,
        "e3": e3,
        "e5": e5,
        "quadratic_intercept": quad,
        "linear_intercept": lin,
        "quadratic_bootstrap_std": float(np.std(boot_quad)),
        "linear_bootstrap_std": float(np.std(boot_lin)),
    }


def main():
    ex = zne_exact()
    print("exact:", ex)
    assert abs(ex["e1"] - (1.0 - P)) < 1e-12
    assert ex["e1"] > ex["e3"] > ex["e5"]
    assert abs(ex["quadratic_intercept"] - 1.0) < 5e-4
    assert abs(ex["quadratic_intercept"] - 1.0) < abs(ex["e1"] - 1.0)
    st = zne_shots()
    print("shots:", st)
    assert abs(st["quadratic_intercept"] - 1.0) < 0.05
    assert st["quadratic_bootstrap_std"] > 0.0
    print("ZNE OK")


if __name__ == "__main__":
    main()
