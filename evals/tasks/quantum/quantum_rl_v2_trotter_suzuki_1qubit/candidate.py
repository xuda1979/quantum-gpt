"""One-qubit Hamiltonian H = a*X + b*Z: exact expm evolution, first-order
Lie-Trotter, and symmetric second-order Suzuki evolution to time t with
n_steps. Frobenius errors, state fidelities from |0>, unitarity checks, and
second-order-error < first-order-error verification for H = 0.9X + 0.9Z,
t = 1.1, n = 8."""

import numpy as np
from scipy.linalg import expm

X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
I2 = np.eye(2, dtype=complex)
ZERO = np.array([[1.0], [0.0]], dtype=complex)


def hamiltonian(a, b):
    return a * X + b * Z


def exact_unitary(a, b, t):
    """U_exact = expm(-i (aX + bZ) t)."""
    return np.asarray(expm(-1j * (a * X + b * Z) * t), dtype=complex)


def first_order_trotter(a, b, t, n_steps):
    """(expm(-i aX dt) expm(-i bZ dt))^n with dt = t/n_steps."""
    dt = t / n_steps
    ux = np.asarray(expm(-1j * a * X * dt), dtype=complex)
    uz = np.asarray(expm(-1j * b * Z * dt), dtype=complex)
    step = ux @ uz
    out = np.eye(2, dtype=complex)
    for _ in range(n_steps):
        out = out @ step
    return out


def second_order_suzuki(a, b, t, n_steps):
    """(expm(-i bZ dt/2) expm(-i aX dt) expm(-i bZ dt/2))^n, symmetric."""
    dt = t / n_steps
    ux = np.asarray(expm(-1j * a * X * dt), dtype=complex)
    uz2 = np.asarray(expm(-1j * b * Z * dt / 2.0), dtype=complex)
    step = uz2 @ ux @ uz2
    out = np.eye(2, dtype=complex)
    for _ in range(n_steps):
        out = out @ step
    return out


def frobenius_error(u, v):
    """||U - V||_F / 2 (normalized by sqrt(4) = 2)."""
    return float(np.linalg.norm(np.asarray(u) - np.asarray(v)) / 2.0)


def fidelity_from_zero(u):
    """| <0|U|0> |^2."""
    u = np.asarray(u, dtype=complex)
    return float(abs(u[0, 0]) ** 2)


def is_unitary(u, tol=1e-9):
    u = np.asarray(u, dtype=complex)
    return bool(np.allclose(u.conj().T @ u, I2, atol=tol))


def main():
    a, b, t, n = 0.9, 0.9, 1.1, 8
    ue = exact_unitary(a, b, t)
    u1 = first_order_trotter(a, b, t, n)
    u2 = second_order_suzuki(a, b, t, n)
    for name, u in (("exact", ue), ("first", u1), ("second", u2)):
        assert is_unitary(u), f"{name} not unitary"
    e1 = frobenius_error(u1, ue)
    e2 = frobenius_error(u2, ue)
    f1 = fidelity_from_zero(u1)
    f2 = fidelity_from_zero(u2)
    assert e2 < e1, f"second-order error {e2} not smaller than {e1}"
    print("frobenius_err_1st =", e1)
    print("frobenius_err_2nd =", e2)
    print("fidelity_1st =", f1)
    print("fidelity_2nd =", f2)


if __name__ == "__main__":
    main()
