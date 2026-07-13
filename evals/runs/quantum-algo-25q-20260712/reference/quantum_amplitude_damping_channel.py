"""Amplitude damping channel via Kraus operators.

The amplitude damping channel with damping parameter gamma has Kraus operators:
  K0 = [[1, 0], [0, sqrt(1-gamma)]]
  K1 = [[0, sqrt(gamma)], [0, 0]]
Apply to |1> state: rho -> K0 |1><1| K0 + K1 |1><1| K1
                       = (1-gamma)|1><1| + gamma|0><0|
So P(0) = gamma, P(1) = 1-gamma.
We use gamma = 0.3 and verify the output populations.
"""
import numpy as np


def amplitude_damping_kraus(gamma: float) -> list[np.ndarray]:
    K0 = np.array([[1.0, 0.0], [0.0, np.sqrt(1 - gamma)]], dtype=complex)
    K1 = np.array([[0.0, np.sqrt(gamma)], [0.0, 0.0]], dtype=complex)
    return [K0, K1]


def apply_channel(rho: np.ndarray, kraus_ops: list[np.ndarray]) -> np.ndarray:
    out = np.zeros_like(rho)
    for K in kraus_ops:
        out += K @ rho @ K.conj().T
    return out


def main():
    gamma = 0.3
    # Initial state |1>
    psi = np.array([0.0, 1.0], dtype=complex)
    rho = np.outer(psi, psi.conj())
    K_ops = amplitude_damping_kraus(gamma)
    rho_out = apply_channel(rho, K_ops)
    p0 = rho_out[0, 0].real
    p1 = rho_out[1, 1].real
    print(f"gamma = {gamma}")
    print(f"P(0) = {p0:.3f}")
    print(f"P(1) = {p1:.3f}")
    print(f"trace_preserving: {abs(np.trace(rho_out) - 1.0) < 1e-9}")
    print(f"correct: {abs(p0 - gamma) < 0.01 and abs(p1 - (1 - gamma)) < 0.01}")


if __name__ == "__main__":
    main()
