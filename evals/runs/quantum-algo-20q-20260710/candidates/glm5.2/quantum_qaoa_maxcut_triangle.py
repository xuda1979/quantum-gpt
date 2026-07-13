import networkx as nx
from qiskit.primitives import StatevectorSampler
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_optimization.applications import Maxcut


def main():
    # Build triangle graph
    graph = nx.Graph()
    graph.add_nodes_from([0, 1, 2])
    graph.add_edges_from([(0, 1), (1, 2), (2, 0)])

    # Build QUBO using Maxcut
    maxcut = Maxcut(graph)
    qp = maxcut.to_quadratic_program()
    qubo = qp.to_ising()  # or qp.to_qubo()

    # Setup QAOA
    sampler = StatevectorSampler()
    optimizer = COBYLA(maxiter=300)
    qaoa = QAOA(sampler=sampler, optimizer=optimizer, reps=2)

    # Solve with MinimumEigenOptimizer
    meo = MinimumEigenOptimizer(qaoa)
    result = meo.solve(qp)

    # Get the solution
    x = result.x
    binary_solution = ''.join(str(int(b)) for b in x)

    set_a = [i for i, b in enumerate(x) if b == 1]
    set_b = [i for i, b in enumerate(x) if b == 0]

    # Max-cut value
    maxcut_value = maxcut.max_cut_value(x)  # or compute manually

    print(f"Binary solution: {binary_solution}")
    print(f"Set A: {set_a}")
    print(f"Set B: {set_b}")
    print(f"Max-cut value: {maxcut_value}")


if __name__ == "__main__":
    main()
