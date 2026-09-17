"""PennyLane default.mixed: Bell state |Phi+> with
qml.DepolarizingChannel(0.03) applied to qubit 0. Full density matrix,
trace, eigenvalues, purity, fidelity with |Phi+>, and <ZZ> via independent
NumPy formulas; plus a finite-shot (20000, seeded) <ZZ> estimate that must
agree with the analytic mixed-state value within 0.04.

Analytic values for this instance (p = 0.03):
  eigenvalues  {0.97, 0.01, 0.01, 0.01}, purity 0.9412,
  fidelity with |Phi+> 0.97, <ZZ> = 1 - 4p/3 = 0.96."""

import numpy as np
import pennylane as qml


def bell_depolarizing_density(p=0.03):
    """Full 4x4 density matrix of Bell |Phi+> with DepolarizingChannel(p)
    on qubit 0, via a default.mixed QNode."""
    dev = qml.device("default.mixed", wires=2)

    @qml.qnode(dev)
    def circuit():
        qml.Hadamard(0)
        qml.CNOT(wires=[0, 1])
        qml.DepolarizingChannel(p, wires=0)
        return qml.density_matrix(wires=[0, 1])

    return np.asarray(circuit(), dtype=complex)


def trace(rho):
    return float(np.real(np.trace(np.asarray(rho, dtype=complex))))


def eigenvalues(rho):
    return np.linalg.eigvalsh(np.asarray(rho, dtype=complex))


def purity(rho):
    rho = np.asarray(rho, dtype=complex)
    return float(np.real(np.trace(rho @ rho)))


def fidelity_phi_plus(rho):
    """Fidelity with |Phi+> = (|00>+|11>)/sqrt(2) via the stable formula
    F = (Tr sqrt(sqrt(rho) sigma sqrt(rho)))^2 for the squared fidelity."""
    rho = np.asarray(rho, dtype=complex)
    phi_plus = (
        np.outer(
            np.array([1.0, 0.0, 0.0, 1.0], dtype=complex),
            np.array([1.0, 0.0, 0.0, 1.0], dtype=complex).conj(),
        )
        / 2.0
    )
    w, v = np.linalg.eigh(rho)
    w = np.clip(w, 0.0, None)
    sqrt_rho = (v * np.sqrt(w)) @ v.conj().T
    inner = sqrt_rho @ phi_plus @ sqrt_rho
    w2, v2 = np.linalg.eigh(inner)
    w2 = np.clip(w2, 0.0, None)
    sqrt_inner = (v2 * np.sqrt(w2)) @ v2.conj().T
    return float(np.real(np.trace(sqrt_inner)) ** 2)


def zz_expectation(rho):
    """<ZZ> = Tr(rho (Z otimes Z)) computed with independent NumPy."""
    Z = np.diag([1.0, -1.0]).astype(complex)
    zz = np.kron(Z, Z)
    return float(np.real(np.trace(np.asarray(rho, dtype=complex) @ zz)))


def zz_expectation_shots(p=0.03, shots=20000, seed=1234):
    """Finite-shot seeded <ZZ> estimate on a separate finite-shot QNode.

    default.mixed samples from the global NumPy RNG, so the seed is fixed
    by seeding the global RNG before device creation (deterministic run).
    """
    np.random.seed(seed)
    dev = qml.device("default.mixed", wires=2, shots=shots)

    @qml.qnode(dev)
    def circuit():
        qml.Hadamard(0)
        qml.CNOT(wires=[0, 1])
        qml.DepolarizingChannel(p, wires=0)
        return qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))

    return float(circuit())


def main():
    p = 0.03
    rho = bell_depolarizing_density(p)
    tr = trace(rho)
    evals = eigenvalues(rho)
    pur = purity(rho)
    fid = fidelity_phi_plus(rho)
    zz = zz_expectation(rho)
    zz_shots = zz_expectation_shots(p=p, shots=20000, seed=1234)
    assert abs(tr - 1.0) < 1e-12, f"trace={tr}"
    assert np.min(evals) >= -1e-12, "not PSD"
    assert abs(pur - 0.9412) < 1e-6, f"purity={pur}"
    assert abs(fid - 0.97) < 1e-6, f"fidelity={fid}"
    assert abs(zz - 0.96) < 1e-6, f"<ZZ>={zz}"
    assert abs(zz_shots - zz) < 0.04, f"shots <ZZ>={zz_shots} vs analytic {zz}"
    print("trace =", tr)
    print("eigenvalues =", sorted(evals.tolist(), reverse=True))
    print("purity =", pur)
    print("fidelity_phi_plus =", fid)
    print("zz =", zz)
    print("zz_shots =", zz_shots)


if __name__ == "__main__":
    main()
