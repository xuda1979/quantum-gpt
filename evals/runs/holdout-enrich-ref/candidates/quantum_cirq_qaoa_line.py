"""QAOA p=1 for the MaxCut of a 4-node line graph using Cirq.

Line graph edges: (0,1), (1,2), (2,3). Optimal cut value is 3 (alternating
bit assignment 0101 / 1010).
"""

import cirq
import numpy as np


def maxcut_line_edges() -> list[tuple[int, int]]:
    return [(0, 1), (1, 2), (2, 3)]


def qaoa_line_circuit(gamma: float, beta: float) -> cirq.Circuit:
    """Build the p=1 QAOA circuit for the 4-node line MaxCut."""
    qubits = cirq.LineQubit.range(4)
    circuit = cirq.Circuit()

    # Initial superposition
    circuit.append(cirq.H.on_each(*qubits))

    # Cost unitary: exp(-i gamma/2 * (I - Z_u)(I - Z_v)) per edge -> ZZ rotation
    for u, v in maxcut_line_edges():
        circuit.append(cirq.ZZPowGate(exponent=2 * gamma / np.pi)(qubits[u], qubits[v]))

    # Mixer unitary: exp(-i beta X) on each qubit
    for q in qubits:
        circuit.append(cirq.XPowGate(exponent=2 * beta / np.pi)(q))

    return circuit


def measure_bitstrings(gamma: float, beta: float, repetitions: int = 1000, seed: int = 0) -> dict:
    """Sample bitstrings from the QAOA circuit and return a histogram."""
    circuit = qaoa_line_circuit(gamma, beta)
    qubits = cirq.LineQubit.range(4)
    circuit.append(cirq.measure(*qubits, key="m"))
    simulator = cirq.Simulator(seed=seed)
    result = simulator.run(circuit, repetitions=repetitions)
    arr = result.measurements["m"]
    hist: dict[str, int] = {}
    for row in arr:
        bs = "".join(str(int(b)) for b in row)
        hist[bs] = hist.get(bs, 0) + 1
    return hist


def maxcut_value(bitstring: str, edges: list[tuple[int, int]]) -> int:
    return sum(1 for u, v in edges if bitstring[u] != bitstring[v])


def best_maxcut_value(edges: list[tuple[int, int]], n: int) -> int:
    best = 0
    for i in range(1 << n):
        bs = format(i, f"0{n}b")
        best = max(best, maxcut_value(bs, edges))
    return best


if __name__ == "__main__":
    edges = maxcut_line_edges()
    print("optimal MaxCut value:", best_maxcut_value(edges, 4))
    # A reasonable p=1 point for the line graph
    hist = measure_bitstrings(gamma=0.5, beta=0.3, repetitions=500)
    top = sorted(hist.items(), key=lambda kv: -kv[1])[:5]
    for bs, c in top:
        print(f"  {bs}  count={c}  cut={maxcut_value(bs, edges)}")
