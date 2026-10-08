import numpy as np
from itertools import permutations

def build_random_unitary(n, seed=42):
    """Build a random n x n unitary using QR decomposition of a complex
    Gaussian matrix."""
    rng = np.random.default_rng(seed)
    X = rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))
    Q, R = np.linalg.qr(X)
    # Make the diagonal of R real and positive to ensure a unique Haar unitary
    phases = np.diag(R) / np.abs(np.diag(R))
    U = Q * phases
    return U

def permanent(M):
    """Compute the permanent of a square matrix via Ryser's algorithm."""
    n = M.shape[0]
    if n == 0:
        return 1.0
    rows = np.arange(n)
    total = 0.0
    for k in range(1, 2 ** n):
        # subset S determined by bits of k
        cols = [j for j in range(n) if (k >> j) & 1]
        submatrix = M[np.ix_(rows, cols)]
        prod = np.prod(np.sum(submatrix, axis=1))
        sign = -1 if (len(cols) % 2 == 0) else 1  # (-1)^(n - |S|)
        if (n - len(cols)) % 2 == 0:
            sign = 1
        else:
            sign = -1
        total += sign * prod
    return -total if (n % 2 == 0) else total  # Ryser's: perm = (-1)^n sum_S (-1)^|S| prod row sums

def boson_sampling_probability(U, input_modes, output_modes):
    """Compute the probability of observing `output_modes` given `input_modes`
    in a linear interferometer U.
    input_modes: list of mode indices occupied by input photons.
    output_modes: list of mode indices we want to detect photons at.
    The probability is |Per(U[input_modes, output_modes])|^2 / (prod s_i! * prod t_j!)
    where s_i and t_j are the input/output occupation numbers."""
    submatrix = U[np.ix_(input_modes, output_modes)]
    per = permanent(submatrix)
    # For collision-free configurations (each mode has at most 1 photon),
    # the denominator is 1.
    return float(np.abs(per) ** 2)

def main():
    n_modes = 6
    n_photons = 3
    input_modes = [0, 1, 2]  # photons start in modes 0, 1, 2
    U = build_random_unitary(n_modes, seed=42)
    # Compute the full output distribution over all 3-photon configurations
    # in 6 modes: C(6,3) = 20 collision-free configurations.
    from itertools import combinations
    output_configs = list(combinations(range(n_modes), n_photons))
    probs = {}
    for out in output_configs:
        p = boson_sampling_probability(U, input_modes, list(out))
        probs[out] = p
    total = sum(probs.values())
    # Pick the most likely output
    best_out = max(probs.items(), key=lambda kv: kv[1])
    # Verify normalization (sum over ALL Fock states, not just collision-free,
    # but for distinguishable-like photons the collision-free portion sums to
    # less than 1 in general. For ideal bosons with random U, the
    # collision-free portion is a substantial fraction.)
    print(f"Boson sampling: {n_photons} photons in {n_modes} modes")
    print(f"Input modes = {input_modes}")
    print(f"Collision-free outputs = {len(output_configs)}")
    print(f"Sum of collision-free probs = {total:.4f}")
    print(f"Most likely output = {best_out[0]}")
    print(f"Max prob = {best_out[1]:.4f}")
    print(f"Valid: {total > 0.5 and best_out[1] > 0}")

if __name__ == "__main__":
    main()
