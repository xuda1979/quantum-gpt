import cirq
import networkx as nx
import numpy as np
from cirq import H, LineQubit, measure, optimizers, qaoa


def build_line_graph(n_nodes: int = 4) -> nx.Graph:
    """Build a line graph with n_nodes nodes."""
    G = nx.Graph()
    G.add_nodes_from(range(n_nodes))
    for i in range(n_nodes - 1):
        G.add_edge(i, i + 1)
    return G


def get_maxcut_edges(G: nx.Graph):
    """Get the list of edges for MaxCut."""
    return list(G.edges())


def run_qaoa_maxcut(n_nodes: int = 4, n_layers: int = 2, n_repetitions: int = 1000, seed: int = 42):
    """
    Run QAOA on a 4-node line graph for MaxCut.

    Returns:
        best_cut: The best cut found (list of node assignments)
        best_value: The best MaxCut value found
        best_params: The best parameters (betas, gammas)
    """
    G = build_line_graph(n_nodes)
    edges = get_maxcut_edges(G)

    # Create qubits
    qubits = [LineQubit(i) for i in range(n_nodes)]

    # Build the QAOA circuit
    # MaxCut cost function: for each edge (i,j), cost = (1 - Z_i * Z_j) / 2
    # The QAOA ansatz alternates between cost and mixer unitaries

    def make_qaoa_circuit(betas, gammas):
        circuit = cirq.Circuit()

        # Initial state: apply H to all qubits
        for q in qubits:
            circuit.append(H(q))

        for layer in range(n_layers):
            # Cost unitary: for each edge, apply exp(-i * gamma * (1 - Z_i Z_j)/2)
            # This is equivalent to exp(-i * gamma/2) * exp(i * gamma/2 * Z_i Z_j)
            # The global phase doesn't matter, so we apply exp(i * gamma/2 * Z_i Z_j)
            # which is a controlled-Z rotation
            for i, j in edges:
                # exp(i * gamma/2 * Z_i Z_j) can be implemented as:
                # CNOT(i, j), RZ(gamma) on j, CNOT(i, j)
                # Actually, let's use the standard QAOA cost unitary
                # U_C = prod_edges exp(-i * gamma * (1 - Z_i Z_j)/2)
                # = prod_edges exp(-i * gamma/2) * exp(i * gamma/2 * Z_i Z_j)
                # The global phase exp(-i * gamma/2 * |E|) can be ignored
                # So we apply exp(i * gamma/2 * Z_i Z_j) for each edge
                # exp(i * theta * Z_i Z_j) = CNOT(i,j) * RZ(2*theta) on j * CNOT(i,j)
                # Wait, let me think more carefully.
                # Z_i Z_j is diagonal. exp(i * theta * Z_i Z_j) is also diagonal.
                # In the computational basis, Z_i Z_j has eigenvalue +1 if bits are same, -1 if different.
                # So exp(i * theta * Z_i Z_j) applies phase i*theta if same, -i*theta if different.
                # This can be implemented as:
                # CNOT(i, j), RZ(2*theta) on j, CNOT(i, j)
                # Let's verify: CNOT flips j if i=1.
                # Actually, a simpler way: use cirq's built-in or implement directly.

                # Use the standard decomposition:
                # exp(i * theta * Z_i Z_j) = CNOT(i,j) * RZ(2*theta) on j * CNOT(i,j)
                # But RZ(2*theta) on j after CNOT... let me just use cirq's approach.

                # Actually, let's use a cleaner approach with cirq's QAOA utilities
                pass

            # Mixer unitary: exp(-i * beta * sum X_i)
            # This is just applying RX(2*beta) to each qubit
            for q in qubits:
                circuit.append(cirq.rx(2 * betas[layer]).on(q))

        return circuit

    # Let's use cirq's built-in QAOA for MaxCut
    # cirq.qaoa has a MaxCut problem class

    # Define the MaxCut problem
    maxcut_problem = qaoa.MaxCutProblem(edges=edges)

    # Create the QAOA ansatz
    ansatz = qaoa.QAOAAnsatz(problem=maxcut_problem, n_layers=n_layers, qubits=qubits)

    # Define the cost function for optimization
    def cost_function(params):
        betas = params[:n_layers]
        gammas = params[n_layers:]
        circuit = ansatz(betas=betas, gammas=gammas)

        # Simulate and compute expected MaxCut value
        simulator = cirq.Simulator(seed=seed)
        result = simulator.run(circuit, repetitions=n_repetitions)

        # Get the measurement results
        # The ansatz should have measurements at the end
        # Let's add measurements
        circuit_with_measure = circuit.copy()
        for i, q in enumerate(qubits):
            circuit_with_measure.append(measure(q, key=f"q{i}"))

        result = simulator.run(circuit_with_measure, repetitions=n_repetitions)

        # Compute MaxCut value
        total_cut = 0
        for i, j in edges:
            bits_i = result.measurements[f"q{i}"]
            bits_j = result.measurements[f"q{j}"]
            # Count how many times the bits differ
            diff_count = np.sum(bits_i[:, 0] != bits_j[:, 0])
            total_cut += diff_count

        # The cost function should return the negative of the MaxCut value (since we minimize)
        return -total_cut / n_repetitions

    # Optimize parameters
    initial_params = np.random.RandomState(seed).uniform(0, np.pi, size=2 * n_layers)
    optimizer = optimizers.GridSearch(
        params=initial_params, ranges=[(0, np.pi)] * (2 * n_layers), resolution=0.1
    )

    # Actually, let's use a simpler approach with scipy or just grid search
    from scipy.optimize import minimize

    def cost_function_scipy(params):
        betas = params[:n_layers]
        gammas = params[n_layers:]
        circuit = ansatz(betas=betas, gammas=gammas)

        circuit_with_measure = circuit.copy()
        for i, q in enumerate(qubits):
            circuit_with_measure.append(measure(q, key=f"q{i}"))

        simulator = cirq.Simulator(seed=seed)
        result = simulator.run(circuit_with_measure, repetitions=n_repetitions)

        total_cut = 0
        for i, j in edges:
            bits_i = result.measurements[f"q{i}"]
            bits_j = result.measurements[f"q{j}"]
            diff_count = np.sum(bits_i[:, 0] != bits_j[:, 0])
            total_cut += diff_count

        return -total_cut / n_repetitions

    # Use Nelder-Mead optimization
    result_opt = minimize(
        cost_function_scipy,
        initial_params,
        method="Nelder-Mead",
        options={"maxiter": 100, "xatol": 0.01, "fatol": 0.01},
    )

    best_params = result_opt.x
    best_betas = best_params[:n_layers]
    best_gammas = best_params[n_layers:]

    # Run with best parameters to get the best cut
    circuit = ansatz(betas=best_betas, gammas=best_gammas)
    circuit_with_measure = circuit.copy()
    for i, q in enumerate(qubits):
        circuit_with_measure.append(measure(q, key=f"q{i}"))

    simulator = cirq.Simulator(seed=seed)
    result = simulator.run(circuit_with_measure, repetitions=n_repetitions)

    # Find the best cut among all measurements
    best_cut_value = -1
    best_cut = None
    for rep in range(n_repetitions):
        cut_value = 0
        for i, j in edges:
            bit_i = result.measurements[f"q{i}"][rep, 0]
            bit_j = result.measurements[f"q{j}"][rep, 0]
            if bit_i != bit_j:
                cut_value += 1
        if cut_value > best_cut_value:
            best_cut_value = cut_value
            best_cut = [result.measurements[f"q{i}"][rep, 0] for i in range(n_nodes)]

    return best_cut, best_cut_value, best_params


if __name__ == "__main__":
    best_cut, best_value, best_params = run_qaoa_maxcut(n_nodes=4, n_layers=2, n_repetitions=1000)
    print(f"Best cut: {best_cut}")
    print(f"Best MaxCut value: {best_value}")
    print(f"Best parameters: {best_params}")
