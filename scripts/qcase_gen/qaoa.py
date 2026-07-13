"""QAOA / QUBO case builders. Each problem type has a correct QUBO (or Ising)
formulation; the embedded code rebuilds the same coefficients and solves with
QAOA on Qiskit>=1.2 Primitives, printing a standardized RESULT_JSON line."""

from __future__ import annotations

import itertools
import random

QAOA_CODE = '''\
# {title} solved with QAOA on Qiskit >= 1.2 (modern qiskit.quantum_info API).
# The QUBO cost Hamiltonian is diagonal in the computational basis, so the
# expectation <psi|H_C|psi> is evaluated exactly and cheaply from the statevector
# probabilities dotted with the precomputed classical cost values.
import json
import numpy as np
from scipy.optimize import minimize
from qiskit.circuit.library import QAOAAnsatz
from qiskit.quantum_info import SparsePauliOp, Statevector

N = {n}
LINEAR = {linear}
QUAD = {quad}
CONST = {const}
REPS = {reps}


def qubo_to_ising(linear, quad, const, n):
    """Map x_i=(1-z_i)/2 QUBO into an Ising SparsePauliOp (little-endian labels)."""
    ident = const
    z = np.zeros(n)
    zz = {{}}
    for i, h in linear.items():
        ident += h / 2.0
        z[i] += -h / 2.0
    for (i, j), w in quad.items():
        ident += w / 4.0
        z[i] += -w / 4.0
        z[j] += -w / 4.0
        zz[(i, j)] = zz.get((i, j), 0.0) + w / 4.0
    terms = [("I" * n, ident)]
    for i in range(n):
        lab = ["I"] * n
        lab[n - 1 - i] = "Z"
        terms.append(("".join(lab), z[i]))
    for (i, j), w in zz.items():
        lab = ["I"] * n
        lab[n - 1 - i] = "Z"
        lab[n - 1 - j] = "Z"
        terms.append(("".join(lab), w))
    terms = [(p, c) for p, c in terms if abs(c) > 1e-12]
    return SparsePauliOp.from_list(terms)


def qubo_value(bits, linear, quad, const):
    val = const
    for i, h in linear.items():
        val += h * bits[i]
    for (i, j), w in quad.items():
        val += w * bits[i] * bits[j]
    return val


def cost_diagonal(linear, quad, const, n):
    """Precompute classical QUBO cost for every basis state (qiskit little-endian)."""
    diag = np.empty(2 ** n)
    for idx in range(2 ** n):
        bits = [(idx >> j) & 1 for j in range(n)]
        diag[idx] = qubo_value(bits, linear, quad, const)
    return diag


def main():
    linear = {{int(k): v for k, v in LINEAR.items()}}
    quad = {{tuple(map(int, k.split("_"))): v for k, v in QUAD.items()}}
    cost_op = qubo_to_ising(linear, quad, CONST, N)
    diag = cost_diagonal(linear, quad, CONST, N)
    ansatz = QAOAAnsatz(cost_operator=cost_op, reps=REPS).decompose()

    def cost(params):
        probs = Statevector(ansatz.assign_parameters(params)).probabilities()
        return float(probs @ diag)

    rng = np.random.default_rng(7)
    best_res = None
    for _ in range({restarts}):
        x0 = rng.random(ansatz.num_parameters) * np.pi
        res = minimize(cost, x0, method="COBYLA", options={{"maxiter": {maxiter}}})
        if best_res is None or res.fun < best_res.fun:
            best_res = res
    res = best_res

    probs = Statevector(ansatz.assign_parameters(res.x)).probabilities()
    best_idx = int(np.argmax(probs))
    bits = [(best_idx >> j) & 1 for j in range(N)]
    best = "".join(str(b) for b in bits[::-1])  # big-endian string for display
    obj = qubo_value(bits, linear, quad, CONST)

    opt_val, opt_bits = brute_optimum(linear, quad, CONST, N)
    is_optimal = abs(obj - opt_val) < 1e-6
    # Approximation ratio vs the worst (max) objective, robust to sign/zero:
    # ratio = (worst - obj) / (worst - opt) in [0,1], 1.0 means global optimum.
    worst_val = brute_worst(linear, quad, CONST, N)
    span = worst_val - opt_val
    approx_ratio = 1.0 if span < 1e-12 else (worst_val - obj) / span

    print("=== {title} (QAOA) ===")
    print("num_qubits:", ansatz.num_qubits)
    print("circuit.depth():", ansatz.depth())
    print("num Pauli terms:", len(cost_op))
    print("num parameters:", ansatz.num_parameters)
    print("best bitstring:", best, "-> selected:", [i for i, b in enumerate(bits) if b == 1])
    print("QUBO objective value:", round(obj, 6))
    print("brute-force optimum:", round(opt_val, 6), "optimal_hit:", is_optimal)
    print("approximation ratio:", round(approx_ratio, 4))
    print("RESULT_JSON " + json.dumps({{
        "num_qubits": ansatz.num_qubits,
        "depth": ansatz.depth(),
        "num_params": ansatz.num_parameters,
        "num_terms": len(cost_op),
        "objective": round(obj, 6),
        "optimum": round(opt_val, 6),
        "optimal_hit": bool(is_optimal),
        "approx_ratio": round(approx_ratio, 4),
        "bitstring": best,
        "selected": [i for i, b in enumerate(bits) if b == 1],
    }}))


def brute_optimum(linear, quad, const, n):
    import itertools
    best, bb = None, None
    for combo in itertools.product([0, 1], repeat=n):
        v = qubo_value(list(combo), linear, quad, const)
        if best is None or v < best:
            best, bb = v, combo
    return best, list(bb)


def brute_worst(linear, quad, const, n):
    import itertools
    worst = None
    for combo in itertools.product([0, 1], repeat=n):
        v = qubo_value(list(combo), linear, quad, const)
        if worst is None or v > worst:
            worst = v
    return worst


if __name__ == "__main__":
    main()
'''


def _fmt_quad(quad):
    # JSON keys must be strings: use "i_j"
    return {f"{i}_{j}": round(w, 6) for (i, j), w in quad.items()}


def _fmt_linear(linear):
    return {str(i): round(w, 6) for i, w in linear.items()}


def build_qaoa_code(title, n, linear, quad, const, reps, maxiter, shots, restarts=5):
    return QAOA_CODE.format(
        title=title,
        n=n,
        linear=_fmt_linear(linear),
        quad=_fmt_quad(quad),
        const=round(const, 6),
        reps=reps,
        maxiter=maxiter,
        shots=shots,
        restarts=restarts,
    )


def rand_graph(n, p, seed):
    rng = random.Random(seed)
    edges = []
    for i, j in itertools.combinations(range(n), 2):
        if rng.random() < p:
            edges.append((i, j, round(rng.uniform(0.5, 2.0), 2)))
    if not edges:  # ensure connected-ish
        edges.append((0, 1, 1.0))
    return edges
