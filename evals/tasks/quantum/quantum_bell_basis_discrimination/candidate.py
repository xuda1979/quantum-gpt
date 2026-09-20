import math

S2 = 1.0 / math.sqrt(2)


def bell_statevector(k: int) -> list[float]:
    """
    Return the k-th Bell state as a 4-vector over |00>, |01>, |10>, |11>:

      k=0: |Phi+>  = (|00> + |11>)/sqrt(2)
      k=1: |Phi->  = (|00> - |11>)/sqrt(2)
      k=2: |Psi+>  = (|01> + |10>)/sqrt(2)
      k=3: |Psi->  = (|01> - |10>)/sqrt(2)
    """
    if k == 0:
        return [S2, 0.0, 0.0, S2]
    if k == 1:
        return [S2, 0.0, 0.0, -S2]
    if k == 2:
        return [0.0, S2, S2, 0.0]
    return [0.0, S2, -S2, 0.0]


def bell_basis_unitary() -> list[list[complex]]:
    """4x4 matrix whose columns are the four Bell states (change of basis)."""
    return [[complex(bell_statevector(k)[i]) for k in range(4)] for i in range(4)]


def classify_bell(state: list[complex]) -> int:
    """
    Discriminate a 2-qubit state by measuring it in the Bell basis.

    Rotating with the adjoint of the Bell-basis unitary maps Bell state k to
    the computational state |k>; the identified index is argmax |<bell_k|s>|^2
    (equivalently the argmax of the rotated amplitudes squared).
    """
    import numpy as np

    U = np.asarray(bell_basis_unitary(), dtype=complex)
    v = np.asarray(state, dtype=complex)
    probs = np.abs(U.conj().T @ v) ** 2
    return int(np.argmax(probs))


def entanglement_concurrence(state: list[complex]) -> float:
    """
    Concurrence of a pure 2-qubit state [a, b, c, d]^T:

        C = 2 |a d - b c|

    1.0 for Bell states, 0.0 for product states.
    """
    a, b, c, d = state
    return 2.0 * abs(complex(a) * complex(d) - complex(b) * complex(c))
