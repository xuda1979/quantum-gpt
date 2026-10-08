"""QAOA of depth p=2 from elementary Qiskit gates for MaxCut on 4 vertices
with edges [(0,1),(0,2),(0,3),(1,2),(2,3)]. Exact expected cut from
Statevector probabilities, deterministic multi-start scipy optimization,
brute-force classical optimum, approximation ratio, and seeded sampling of
the optimized circuit.

Bit order convention (declared once, used everywhere): bitstring integer b
has vertex i in partition A iff ((b >> i) & 1) == 1."""

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator
from scipy.optimize import minimize

EDGES = [(0, 1), (0, 2), (0, 3), (1, 2), (2, 3)]
N_VERTICES = 4
P = 2


def bitstring_cut(bits, edges=EDGES):
    """Number of edges crossing the partition induced by `bits` (vertex i
    in set A iff bit i is set)."""
    cut = 0
    for u, v in edges:
        if ((bits >> u) & 1) != ((bits >> v) & 1):
            cut += 1
    return cut


def qaoa_circuit(gamma, beta, edges=EDGES, n_vertices=N_VERTICES):
    """Build the p=2 QAOA circuit from elementary gates: H layer, then two
    (cost, mixer) layers built from CNOT/RZ (cost) and RX (mixer)."""
    qc = QuantumCircuit(n_vertices)
    qc.h(range(n_vertices))
    for layer in range(P):
        g = gamma[layer]
        for u, v in edges:
            qc.cx(u, v)
            qc.rz(-2.0 * g, v)
            qc.cx(u, v)
        for i in range(n_vertices):
            qc.rx(2.0 * beta[layer], i)
    return qc


def expected_cut(gamma, beta, edges=EDGES):
    """Exact expected cut = sum_b p(b) * cut(b) from Statevector
    probabilities; every cut uses the single declared bit-order function."""
    qc = qaoa_circuit(gamma, beta, edges)
    probs = Statevector(qc).probabilities_dict(decimals=15)
    total = 0.0
    for bitstring, prob in probs.items():
        total += prob * bitstring_cut(int(bitstring, 2), edges)
    return float(total)


def classical_optimum(edges=EDGES, n_vertices=N_VERTICES):
    """Brute-force enumeration of the classical MaxCut optimum."""
    best_value = 0
    best_bits = []
    for b in range(1 << n_vertices):
        v = bitstring_cut(b, edges)
        if v > best_value:
            best_value = v
            best_bits = [b]
        elif v == best_value:
            best_bits.append(b)
    return best_value, best_bits


def optimize_parameters(edges=EDGES, n_starts=12, seed=0):
    """Deterministic multi-start scipy optimization of (gamma, beta)."""
    optimum, _ = classical_optimum(edges)

    def objective(params):
        gamma = params[:P]
        beta = params[P:]
        return -expected_cut(gamma, beta, edges)

    best = None
    best_val = -np.inf
    rng = np.random.default_rng(seed)
    for s in range(n_starts):
        start = np.concatenate(
            [rng.uniform(0.0, 2.0 * np.pi, size=P), rng.uniform(0.0, np.pi, size=P)]
        )
        res = minimize(
            objective,
            start,
            method="Nelder-Mead",
            options={"maxiter": 800, "xatol": 1e-6, "fatol": 1e-8},
        )
        val = -float(res.fun)
        if val > best_val:
            best_val = val
            best = res.x
    gamma = best[:P].tolist()
    beta = best[P:].tolist()
    ratio = best_val / float(optimum)
    return gamma, beta, best_val, ratio


def sample_optimized(gamma, beta, shots=4096, seed=42, edges=EDGES):
    """Seed-sampled counts from the optimized circuit."""
    qc = qaoa_circuit(gamma, beta, edges)
    creg = ClassicalRegister(N_VERTICES, "c")
    qc.add_register(creg)
    qc.measure(range(N_VERTICES), creg)
    sim = AerSimulator(seed_simulator=seed)
    counts = sim.run(qc, shots=shots).result().get_counts()
    return counts


def main():
    gamma, beta, value, ratio = optimize_parameters()
    optimum, _ = classical_optimum()
    counts = sample_optimized(gamma, beta)
    # consistency: expectation from probabilities equals the sampled mean cut
    probs = Statevector(qaoa_circuit(gamma, beta)).probabilities_dict(decimals=15)
    assert abs(sum(probs.values()) - 1.0) < 1e-12, "probabilities do not sum to 1"
    mean_sampled = sum(bitstring_cut(int(b, 2)) * c for b, c in counts.items()) / sum(
        counts.values()
    )
    assert abs(mean_sampled - value) < 0.05, "sampled mean cut inconsistent"
    print("classical_optimum =", optimum)
    print("qaoa_expected_cut =", value)
    print("approximation_ratio =", ratio)
    print("gamma =", gamma)
    print("beta =", beta)


if __name__ == "__main__":
    main()
