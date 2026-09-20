import numpy as np

def grover_coin_5():
    # 5x5 Grover coin: 2/5 * J - I
    J = np.ones((5, 5))
    return 2.0 / 5.0 * J - np.eye(5)

def build_full_coin():
    # 8x8 coin: 5x5 Grover on the first 5 states, identity on |5>,|6>,|7>.
    C = np.eye(8, dtype=complex)
    C[:5, :5] = grover_coin_5()
    return C

def build_shift():
    # Position register: 3 qubits -> 8 vertices, only 0..4 valid.
    # Coin states 0..4: even -> move -1, odd -> move +1; coin >=5 -> no move.
    S = np.zeros((8 * 8, 8 * 8), dtype=complex)
    for c in range(8):
        for p in range(8):
            if c < 5 and p < 5:
                dp = 1 if (c % 2 == 1) else -1
                p2 = (p + dp) % 5
            else:
                p2 = p
            S[(c * 8 + p2), (c * 8 + p)] = 1.0
    return S

def main():
    C = build_full_coin()
    S = build_shift()
    # Combined step: S * (C tensor I_pos). State vector is indexed by (c, p).
    step = S @ np.kron(C, np.eye(8))
    state = np.zeros(64, dtype=complex)
    state[0] = 1.0  # |coin=0>|pos=0>
    for _ in range(4):
        state = step @ state
    probs = np.abs(state) ** 2
    p_vertex = np.zeros(8)
    for c in range(8):
        for p in range(8):
            p_vertex[p] += probs[c * 8 + p]
    print(f"Steps = 4")
    print(f"P(0) = {p_vertex[0]:.4f}")
    print(f"P(1) = {p_vertex[1]:.4f}")
    print(f"P(2) = {p_vertex[2]:.4f}")
    print(f"Total prob = {sum(p_vertex[:5]):.4f}")

if __name__ == "__main__":
    main()
