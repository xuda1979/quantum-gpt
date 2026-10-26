import numpy as np


def qaoa_maxcut_cost_function(graph: list, gamma: float, beta: float) -> float:
    """
    Compute the expected value of the MaxCut cost function for a QAOA circuit
    with given parameters gamma and beta, using classical simulation.

    Parameters:
    -----------
    graph : list of tuples
        List of edges in the graph. Each edge is a tuple (i, j) representing
        an edge between node i and node j.
    gamma : float
        QAOA mixing parameter for the cost Hamiltonian.
    beta : float
        QAOA mixing parameter for the mixer Hamiltonian.

    Returns:
    --------
    float
        Expected value of the MaxCut cost function.
    """
    if not graph:
        return 0.0

    # Determine number of nodes
    nodes = set()
    for i, j in graph:
        nodes.add(i)
        nodes.add(j)
    n = max(nodes) + 1 if nodes else 0

    if n == 0:
        return 0.0

    # Build adjacency matrix
    adj = np.zeros((n, n), dtype=float)
    for i, j in graph:
        adj[i, j] = 1
        adj[j, i] = 1

    # Define the cost Hamiltonian H_C = sum_{(i,j) in E} (1 - Z_i Z_j) / 2
    # and the mixer Hamiltonian H_B = sum_i X_i

    # For classical simulation, we simulate the QAOA circuit on all 2^n basis states
    # The initial state is |+>^n = (1/sqrt(2^n)) * sum_x |x>

    # We'll compute the probability distribution after applying the QAOA circuit
    # and then compute the expected MaxCut value.

    # For small n, we can do full statevector simulation
    if n > 12:
        # For larger n, use a different approach or raise an error
        # Here we'll use a simplified approach
        raise ValueError("Number of nodes too large for full statevector simulation")

    # Statevector simulation
    # Initial state: |+>^n
    dim = 2**n
    state = np.ones(dim, dtype=complex) / np.sqrt(dim)

    # Apply cost unitary: U_C = exp(-i * gamma * H_C)
    # H_C = sum_{(i,j) in E} (1 - Z_i Z_j) / 2
    # Since (1 - Z_i Z_j)/2 is diagonal, U_C is diagonal
    # U_C = prod_{(i,j) in E} exp(-i * gamma * (1 - Z_i Z_j) / 2)

    # For each basis state |x>, the eigenvalue of H_C is:
    # sum_{(i,j) in E} (1 - (-1)^{x_i + x_j}) / 2
    # = sum_{(i,j) in E} (1 - (-1)^{x_i + x_j}) / 2

    # Let's compute the phase for each basis state
    phases = np.zeros(dim, dtype=float)
    for idx in range(dim):
        # Get the bitstring
        bits = [(idx >> k) & 1 for k in range(n)]
        cost_val = 0.0
        for i, j in graph:
            # Z_i Z_j eigenvalue is (-1)^{bits[i] + bits[j]}
            zz = (-1) ** (bits[i] + bits[j])
            cost_val += (1 - zz) / 2.0
        phases[idx] = -gamma * cost_val

    # Apply cost unitary
    state = state * np.exp(1j * phases)

    # Apply mixer unitary: U_B = exp(-i * beta * H_B)
    # H_B = sum_i X_i
    # This is not diagonal, so we need to apply it properly.
    # For small n, we can construct the full unitary matrix.

    # Construct H_B matrix
    H_B = np.zeros((dim, dim), dtype=complex)
    for idx in range(dim):
        bits = [(idx >> k) & 1 for k in range(n)]
        for i in range(n):
            # X_i flips bit i
            new_bits = bits[:]
            new_bits[i] = 1 - new_bits[i]
            new_idx = 0
            for k in range(n):
                new_idx |= new_bits[k] << k
            H_B[idx, new_idx] = 1.0

    # Compute exp(-i * beta * H_B) using matrix exponential
    # For small dimensions, we can use scipy or implement our own
    # Let's use a simple approach: diagonalize H_B

    # H_B is Hermitian, so we can diagonalize it
    eigenvalues, eigenvectors = np.linalg.eigh(H_B)

    # U_B = V * diag(exp(-i * beta * eigenvalues)) * V^dagger
    exp_eig = np.exp(-1j * beta * eigenvalues)
    U_B = (eigenvectors * exp_eig) @ eigenvectors.conj().T

    # Apply U_B to state
    state = U_B @ state

    # Compute expected MaxCut value
    # <H_C> = sum_x |<x|psi>|^2 * cost(x)
    expected_cost = 0.0
    for idx in range(dim):
        prob = np.abs(state[idx]) ** 2
        bits = [(idx >> k) & 1 for k in range(n)]
        cost_val = 0.0
        for i, j in graph:
            zz = (-1) ** (bits[i] + bits[j])
            cost_val += (1 - zz) / 2.0
        expected_cost += prob * cost_val

    return float(np.real(expected_cost))


def simulate_qaoa_maxcut(graph: list, gamma: float, beta: float) -> float:
    """
    Alias for qaoa_maxcut_cost_function.
    """
    return qaoa_maxcut_cost_function(graph, gamma, beta)
