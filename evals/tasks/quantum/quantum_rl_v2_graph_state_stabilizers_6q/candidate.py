"""6-qubit graph state stabilizer verification with Qiskit.

The graph state for edges [(0,1),(0,2),(1,3),(2,4),(3,5),(4,5)] is
built by applying H to every qubit and CZ on every edge. For each
vertex v the stabilizer K_v = X_v times Z on its neighbors is
constructed with SparsePauliOp.from_sparse_list so the qubit indexing
is unambiguous, all six expectations are evaluated with
StatevectorEstimator, and every expectation is asserted to be +1
within 1e-12."""

from __future__ import annotations

from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp

EDGES = [(0, 1), (0, 2), (1, 3), (2, 4), (3, 5), (4, 5)]
N_QUBITS = 6


def graph_edges() -> list[tuple[int, int]]:
    """The six graph edges (deterministic fixture)."""
    return list(EDGES)


def graph_state_circuit() -> QuantumCircuit:
    """H on every qubit, CZ on every edge."""
    qc = QuantumCircuit(N_QUBITS)
    qc.h(range(N_QUBITS))
    for a, b in EDGES:
        qc.cz(a, b)
    return qc


def stabilizers() -> list[SparsePauliOp]:
    """K_v = X_v * Z on the neighbors of v as one product Pauli built
    with from_sparse_list: the multi-character label is paired positionally
    with the explicit qubit list [v] + sorted(neighbors), so the qubit
    indexing is unambiguous."""
    neighbors = {v: set() for v in range(N_QUBITS)}
    for a, b in EDGES:
        neighbors[a].add(b)
        neighbors[b].add(a)
    ops = []
    for v in range(N_QUBITS):
        qubits = [v] + sorted(neighbors[v])
        label = "X" + "Z" * (len(qubits) - 1)
        ops.append(SparsePauliOp.from_sparse_list([(label, qubits, 1.0)], num_qubits=N_QUBITS))
    return ops


def expectations() -> dict[str, float]:
    """K_v expectations via StatevectorEstimator (exact, no shots)."""
    circuit = graph_state_circuit()
    ops = stabilizers()
    estimator = StatevectorEstimator()
    result = estimator.run([(circuit, ops)]).result()
    evs = result[0].data.evs
    labels = [op.to_list()[0][0] for op in ops]
    return {label: float(evs[i]) for i, label in enumerate(labels)}


def run_checks() -> dict:
    """All stabilizer expectations plus the minimum (worst) value."""
    exp = expectations()
    return {
        "expectations": exp,
        "min_expectation": min(exp.values()),
        "max_deviation": max(abs(v - 1.0) for v in exp.values()),
    }


def main():
    result = run_checks()
    print("expectations =", result["expectations"])
    print("min_expectation =", result["min_expectation"])
    assert (
        result["min_expectation"] > 1.0 - 1e-12
    ), "every stabilizer expectation must be +1 within 1e-12"


if __name__ == "__main__":
    main()
