"""QAOA Max-Cut on a 5-vertex undirected cycle graph using Qiskit."""

from qiskit.primitives import StatevectorSampler
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_optimization.applications import Maxcut


def main():
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
    n = 5

    # Build the Maxcut problem from the edge list.
    maxcut = Maxcut(edges)
    qp = maxcut.to_quadratic_program()

    # QAOA with the StatevectorSampler primitive and COBYLA optimizer.
    sampler = StatevectorSampler()
    optimizer = COBYLA()
    qaoa = QAOA(sampler=sampler, optimizer=optimizer, reps=1)
    meo = MinimumEigenOptimizer(qaoa)

    result = meo.solve(qp)

    # Variable order in the QuadraticProgram is x_0..x_{n-1}.
    binary_solution = "".join(str(int(result.x[i])) for i in range(n))

    set0 = [i for i in range(n) if binary_solution[i] == "0"]
    set1 = [i for i in range(n) if binary_solution[i] == "1"]

    cut_value = sum(1 for u, v in edges if binary_solution[u] != binary_solution[v])

    print(f"Binary solution: {binary_solution}")
    print(f"Set A: {set0}")
    print(f"Set B: {set1}")
    print(f"Max-cut value: {cut_value}")


if __name__ == "__main__":
    main()
