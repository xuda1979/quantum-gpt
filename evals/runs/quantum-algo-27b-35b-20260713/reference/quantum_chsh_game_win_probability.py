import numpy as np

def measure_in_basis(state, basis_angle):
    """Measure a 1-qubit state in the basis rotated by `basis_angle` (radians)
    around the Bloch XY plane: |0_b> = cos(theta/2)|0> + sin(theta/2)|1>,
    |1_b> = -sin(theta/2)|0> + cos(theta/2)|1>."""
    theta = basis_angle
    # Measurement projectors
    P0 = np.array([[np.cos(theta/2)**2, np.cos(theta/2)*np.sin(theta/2)],
                   [np.cos(theta/2)*np.sin(theta/2), np.sin(theta/2)**2]])
    P1 = np.eye(2) - P0
    return P0, P1

def chsh_quantum_win_prob():
    # Alice: a=0 -> A0 = Z, a=1 -> A1 = X (angle 0 and pi/2 in XY plane basis choice)
    # Bob: b=0 -> B0 = (Z+X)/sqrt2, b=1 -> B1 = (Z-X)/sqrt2
    # Optimal angles in the X-Z plane
    # A0 = Z (measurement angle 0), A1 = X (measurement angle pi/2)
    # B0 measured at angle pi/4, B1 at angle -pi/4
    # Singlet state |Phi-> = (|01> - |10>)/sqrt2
    psi = np.array([0, 1, -1, 0], dtype=complex) / np.sqrt(2)
    # Observables
    Z = np.array([[1, 0], [0, -1]], dtype=complex)
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    A0 = Z; A1 = X
    B0 = (Z + X) / np.sqrt(2)
    B1 = (Z - X) / np.sqrt(2)
    def correlation(A, B):
        # <psi| A x B |psi>
        AB = np.kron(A, B)
        return float(np.real(psi.conj() @ AB @ psi))
    # CHSH game: Alice and Bob win if a XOR b = x AND y
    # where x, y in {0, 1} are the referee's bits.
    # Win prob = (1 + E(a,b))/2 for the matching condition.
    E00 = correlation(A0, B0)  # x=0,y=0 -> a xor b = 0
    E01 = correlation(A0, B1)  # x=0,y=1 -> a xor b = 1
    E10 = correlation(A1, B0)  # x=1,y=0 -> a xor b = 1
    E11 = correlation(A1, B1)  # x=1,y=1 -> a xor b = 0
    # Win probability averaged over the 4 equally-likely (x,y) inputs
    win = 0.25 * (
        (1 + E00) / 2 +  # x=0,y=0
        (1 - E01) / 2 +  # x=0,y=1 (need a != b)
        (1 - E10) / 2 +  # x=1,y=0 (need a != b)
        (1 + E11) / 2    # x=1,y=1 (need a == b)
    )
    return win, (E00 - E01 + E10 + E11)

def main():
    win, S = chsh_quantum_win_prob()
    classical_best = 0.75
    tsirelson = 2 * np.sqrt(2)
    print(f"CHSH quantum win prob = {win:.4f}")
    print(f"Classical best = {classical_best:.4f}")
    print(f"Tsirelson S = {S:.4f}")
    print(f"Tsirelson bound = {tsirelson:.4f}")
    print(f"Saturates Tsirelson: {abs(S - tsirelson) < 1e-6}")
    print(f"Beats classical: {win > classical_best + 1e-6}")

if __name__ == "__main__":
    main()
