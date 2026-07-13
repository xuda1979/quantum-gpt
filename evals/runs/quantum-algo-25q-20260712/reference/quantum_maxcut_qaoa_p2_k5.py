"""QAOA p=1 for Max-Cut on a triangle + pendant graph.

Graph: 4 vertices with edges (0,1), (1,2), (0,2), (2,3).
This is a triangle (0,1,2) plus a pendant edge (2,3).
Max-Cut = 3 (e.g., partition {0,3} vs {1,2} cuts all 3 edges:
  (0,1): cut
  (1,2): not cut
  (0,2): cut
  (2,3): cut
  Total = 3).
Or partition {0,2} vs {1,3}:
  (0,1): cut, (1,2): cut, (0,2): not cut, (2,3): cut -> 3 cuts.
So Max-Cut = 3.
QAOA with p=1 should find this.
"""
import numpy as np
from qiskit.circuit.library import QAOAAnsatz
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp
from scipy.optimize import differential_evolution, minimize


def main():
    n = 4
    edges = [(0, 1), (1, 2), (0, 2), (2, 3)]
    pauli_list = []
    for i, j in edges:
        labels = ["I"] * n
        labels[i] = "Z"
        labels[j] = "Z"
        pauli_str = "".join(labels)
        pauli_list.append((pauli_str, 0.5))
    H_C = SparsePauliOp.from_list(pauli_list)
    H_cost = -H_C
    ansatz = QAOAAnsatz(cost_operator=H_cost, reps=1)
    est = StatevectorEstimator()
    def cost(params):
        qc = ansatz.assign_parameters(list(params))
        result = est.run([(qc, H_cost)]).result()
        return float(result[0].data.evs)
    bounds = [(0, 2 * np.pi)] * 2
    result = differential_evolution(cost, bounds, seed=42, maxiter=200, tol=1e-8, popsize=30)
    res = minimize(cost, result.x, method="Nelder-Mead",
                   options={"xatol": 1e-8, "fatol": 1e-8, "maxiter": 5000})
    cut_value = -res.fun
    # Brute-force Max-Cut
    best_cut = 0
    for k in range(2 ** n):
        partition = [(k >> i) & 1 for i in range(n)]
        cut = sum(1 for i, j in edges if partition[i] != partition[j])
        if cut > best_cut:
            best_cut = cut
    print(f"QAOA cut value = {cut_value:.3f}")
    print(f"optimal cut = {best_cut}")
    print(f"optimal: {cut_value >= best_cut - 0.1}")


if __name__ == "__main__":
    main()
