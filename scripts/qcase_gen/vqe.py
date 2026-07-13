"""VQE case builders: chemistry (small tapered molecules) and condensed-matter
spin models (transverse-field Ising, Heisenberg). Embedded code solves with
TwoLocal/RealAmplitudes + StatevectorEstimator and validates against exact
diagonalization, printing RESULT_JSON."""

from __future__ import annotations

VQE_CODE = """\
# {title}: ground-state energy via VQE on Qiskit >= 1.2 Primitives.
import json
import numpy as np
from scipy.optimize import minimize
from qiskit.circuit.library import {ansatz_cls}
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator

PAULI_TERMS = {terms}
REPS = {reps}


def build_hamiltonian():
    return SparsePauliOp.from_list(PAULI_TERMS)


def main():
    H = build_hamiltonian()
    nq = H.num_qubits
    ansatz = {ansatz_ctor}.decompose()
    estimator = StatevectorEstimator()

    def energy(theta):
        r = estimator.run([(ansatz, H, theta)]).result()
        return float(r[0].data.evs)

    rng = np.random.default_rng({seed})
    best = None
    for _ in range({restarts}):
        x0 = rng.random(ansatz.num_parameters) * 2 * np.pi
        res = minimize(energy, x0, method="{optimizer}",
                       options={{"maxiter": {maxiter}}})
        if best is None or res.fun < best.fun:
            best = res

    ref = float(np.min(np.linalg.eigvalsh(H.to_matrix())))
    err = abs(best.fun - ref)

    print("=== {title} (VQE) ===")
    print("num_qubits:", ansatz.num_qubits)
    print("circuit.depth():", ansatz.depth())
    print("num Pauli terms:", len(H))
    print("num parameters:", ansatz.num_parameters)
    print("VQE energy:", round(best.fun, 6))
    print("exact reference:", round(ref, 6))
    print("absolute error:", err)
    print("RESULT_JSON " + json.dumps({{
        "num_qubits": ansatz.num_qubits,
        "depth": ansatz.depth(),
        "num_params": ansatz.num_parameters,
        "num_terms": len(H),
        "objective": round(best.fun, 6),
        "reference": round(ref, 6),
        "abs_error": err,
    }}))


if __name__ == "__main__":
    main()
"""


def _ansatz(kind, nq, reps):
    if kind == "TwoLocal":
        ctor = (
            f'TwoLocal({nq}, rotation_blocks="ry", '
            f'entanglement_blocks="cz", entanglement="linear", reps={reps})'
        )
        return "TwoLocal", ctor
    if kind == "RealAmplitudes":
        ctor = f"RealAmplitudes({nq}, reps={reps})"
        return "RealAmplitudes", ctor
    if kind == "EfficientSU2":
        ctor = f"EfficientSU2({nq}, reps={reps})"
        return "EfficientSU2", ctor
    raise ValueError(kind)


def build_vqe_code(title, terms, ansatz_kind, nq, reps, optimizer, maxiter, restarts, seed):
    cls, ctor = _ansatz(ansatz_kind, nq, reps)
    return VQE_CODE.format(
        title=title,
        terms=terms,
        ansatz_cls=cls,
        ansatz_ctor=ctor,
        reps=reps,
        optimizer=optimizer,
        maxiter=maxiter,
        restarts=restarts,
        seed=seed,
    )


# ----- molecular Hamiltonians (tapered, literature coefficients) -----
H2_TERMS = [
    ("II", -1.0523732),
    ("IZ", 0.3979374),
    ("ZI", -0.3979374),
    ("ZZ", -0.0112801),
    ("XX", 0.1809312),
]
# HeH+ (2-qubit reduced, illustrative STO-3G-style coefficients)
HEHP_TERMS = [
    ("II", -3.8505),
    ("IZ", 0.2288),
    ("ZI", -0.2288),
    ("ZZ", 0.1763),
    ("XX", 0.1206),
]


def tfim_terms(n, J=1.0, h=1.0):
    """Transverse-field Ising: H = -J sum Z_i Z_{i+1} - h sum X_i (open chain)."""
    terms = []
    for i in range(n - 1):
        lab = ["I"] * n
        lab[n - 1 - i] = "Z"
        lab[n - 1 - (i + 1)] = "Z"
        terms.append(("".join(lab), -J))
    for i in range(n):
        lab = ["I"] * n
        lab[n - 1 - i] = "X"
        terms.append(("".join(lab), -h))
    return terms


def heisenberg_terms(n, Jx=1.0, Jy=1.0, Jz=1.0):
    """Anisotropic Heisenberg XXZ chain (open)."""
    terms = []
    for i in range(n - 1):
        for P, J in (("X", Jx), ("Y", Jy), ("Z", Jz)):
            lab = ["I"] * n
            lab[n - 1 - i] = P
            lab[n - 1 - (i + 1)] = P
            terms.append(("".join(lab), J))
    return terms
