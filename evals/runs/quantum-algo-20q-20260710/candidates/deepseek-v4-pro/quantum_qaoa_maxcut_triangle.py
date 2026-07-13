import numpy as np
from qiskit.primitives import StatevectorSampler
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA as COBYLAOptimizer
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_optimization.applications import Maxcut


def main():
    # 1. Build triangle graph
    graph = np.array([[0, 1, 1],
                      [1, 0, 1],
                      [1, 1, 0]])

    # 2. Build QUBO via Maxcut application
    maxcut = Maxcut(graph)
    qubo = maxcut.to_quadratic_program()

    # Set up QAOA with StatevectorSampler and COBYLA
    sampler = StatevectorSampler()
    optimizer = COBYLAOptimizer(maxiter=300)
    qaoa = QAOA(sampler=sampler, optimizer=optimizer, reps=2)

    # Solve with MinimumEigenOptimizer
    min_eigen_optimizer = MinimumEigenOptimizer(qaoa)
    result = min_eigen_optimizer.solve(qubo)

    # 3. Extract and print results
    binary_solution = result.x
    binary_str = ''.join(str(int(bit)) for bit in binary_solution)

    set_a = [i for i, bit in enumerate(binary_solution) if bit == 0]
    set_b = [i for i, bit in enumerate(binary_solution) if bit == 1]

    maxcut_value = int(result.fval)

    print(f"Binary solution: {binary_str}")
    print(f"Set A: {set_a}")
    print(f"Set B: {set_b}")
    print(f"Max-cut value: {maxcut_value}")

if __name__ == "__main__":
    main()
