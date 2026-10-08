"""Algorithm builders for VQC (variational classifier), QPE (phase estimation),
and Grover search. Each embedded script self-validates and prints RESULT_JSON."""

from __future__ import annotations

# ---------------------------------------------------------------------------
# VQC: variational quantum classifier on a linearly separable 2D toy dataset.
# ---------------------------------------------------------------------------
VQC_CODE = '''\
# {title}: variational quantum classifier (Qiskit >= 1.2 Primitives).
import json
import numpy as np
from scipy.optimize import minimize
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.circuit.library import RealAmplitudes
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator

N_QUBITS = {n}
REPS = {reps}
rng = np.random.default_rng({seed})


def make_data(n_per=12):
    """Two well-separated N-dim Gaussian blobs; labels in {{-1,+1}}."""
    center = np.full(N_QUBITS, 0.7)
    a = rng.normal(center, 0.18, size=(n_per, N_QUBITS))
    b = rng.normal(-center, 0.18, size=(n_per, N_QUBITS))
    X = np.vstack([a, b])
    y = np.array([1.0] * n_per + [-1.0] * n_per)
    return X, y


def build_circuit():
    # Angle-encoding feature map (RY) + RealAmplitudes variational block.
    x = ParameterVector("x", N_QUBITS)
    fm = QuantumCircuit(N_QUBITS)
    for i in range(N_QUBITS):
        fm.ry(x[i], i)
    va = RealAmplitudes(N_QUBITS, reps=REPS)
    qc = QuantumCircuit(N_QUBITS)
    qc.compose(fm, inplace=True)
    qc.compose(va, inplace=True)
    return qc.decompose(), list(x), list(va.parameters)


def main():
    X, y = make_data()
    circ, x_params, w_params = build_circuit()
    obs = SparsePauliOp.from_list([("Z" + "I" * (N_QUBITS - 1), 1.0)])
    estimator = StatevectorEstimator()

    # Pre-bind the (constant) feature values into one circuit per sample, leaving
    # only the trainable weights symbolic. This avoids rebuilding circuits every
    # optimization step.
    data_circuits = []
    for xi in X:
        mp = {{p: float(v) for p, v in zip(x_params, xi)}}
        data_circuits.append(circ.assign_parameters(mp))

    def predict_raw(weights):
        pubs = [(c, obs, weights) for c in data_circuits]
        res = estimator.run(pubs).result()
        return np.array([float(r.data.evs) for r in res])

    def loss(weights):
        preds = predict_raw(weights)
        return float(np.mean((preds - y) ** 2))

    best = None
    for _ in range({restarts}):
        w0 = rng.random(len(w_params)) * 2 * np.pi
        res = minimize(loss, w0, method="COBYLA", options={{"maxiter": {maxiter}}})
        if best is None or res.fun < best.fun:
            best = res
    preds = np.sign(predict_raw(best.x))
    acc = float(np.mean(preds == y))

    print("=== {title} ===")
    print("num_qubits:", circ.num_qubits)
    print("circuit.depth():", circ.depth())
    print("num parameters (trainable):", len(w_params))
    print("final loss:", round(best.fun, 6))
    print("train accuracy:", acc)
    print("RESULT_JSON " + json.dumps({{
        "num_qubits": circ.num_qubits,
        "depth": circ.depth(),
        "num_params": len(w_params),
        "num_terms": len(obs),
        "objective": round(best.fun, 6),
        "accuracy": acc,
    }}))


if __name__ == "__main__":
    main()
'''


def build_vqc_code(title, n, reps, maxiter, seed, restarts=4):
    return VQC_CODE.format(
        title=title, n=n, reps=reps, maxiter=maxiter, seed=seed, restarts=restarts
    )


# ---------------------------------------------------------------------------
# QPE: estimate the phase of a controlled-phase eigenvalue.
# ---------------------------------------------------------------------------
QPE_CODE = """\
# {title}: Quantum Phase Estimation (Qiskit >= 1.2 Primitives).
import json
import math
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT
from qiskit.primitives import StatevectorSampler

N_COUNT = {n_count}
TRUE_PHASE = {phase}   # exact phase phi in [0,1)


def build_qpe():
    qc = QuantumCircuit(N_COUNT + 1, N_COUNT)
    qc.x(N_COUNT)  # |1> is eigenstate of phase gate with eigenvalue e^{{2 pi i phi}}
    for q in range(N_COUNT):
        qc.h(q)
    for j in range(N_COUNT):
        for _ in range(2 ** j):
            qc.cp(2 * math.pi * TRUE_PHASE, j, N_COUNT)
    qc.compose(QFT(N_COUNT, inverse=True), qubits=range(N_COUNT), inplace=True)
    qc.measure(range(N_COUNT), range(N_COUNT))
    return qc


def main():
    qc = build_qpe()
    counts = StatevectorSampler().run([(qc,)], shots={shots}).result()[0].data.c.get_counts()
    best = max(counts, key=counts.get)
    est_phase = int(best, 2) / 2 ** N_COUNT
    err = abs(est_phase - TRUE_PHASE)

    print("=== {title} ===")
    print("num_qubits:", qc.num_qubits)
    print("circuit.depth():", qc.decompose().depth())
    print("estimated phase:", est_phase, "true phase:", TRUE_PHASE)
    print("absolute error:", err)
    print("RESULT_JSON " + json.dumps({{
        "num_qubits": qc.num_qubits,
        "depth": qc.decompose().depth(),
        "num_params": 0,
        "num_terms": 1,
        "objective": est_phase,
        "abs_error": err,
    }}))


if __name__ == "__main__":
    main()
"""


def build_qpe_code(title, n_count, phase, shots):
    return QPE_CODE.format(title=title, n_count=n_count, phase=phase, shots=shots)


# ---------------------------------------------------------------------------
# Grover: amplitude amplification to find marked basis state(s).
# ---------------------------------------------------------------------------
GROVER_CODE = """\
# {title}: Grover search via amplitude amplification (Qiskit >= 1.2 Primitives).
import json
import math
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import GroverOperator
from qiskit.primitives import StatevectorSampler

N = {n}
MARKED = "{marked}"  # target bitstring (length N, qubit-0 first)


def phase_oracle():
    qc = QuantumCircuit(N)
    # flip qubits that should be 0 in the marked state, multi-controlled Z, flip back
    zeros = [i for i, b in enumerate(MARKED) if b == "0"]
    for i in zeros:
        qc.x(i)
    if N == 1:
        qc.z(0)
    else:
        qc.h(N - 1)
        qc.mcx(list(range(N - 1)), N - 1)
        qc.h(N - 1)
    for i in zeros:
        qc.x(i)
    return qc


def main():
    oracle = phase_oracle()
    grover_op = GroverOperator(oracle)
    iters = max(1, int(np.floor((math.pi / 4) * math.sqrt(2 ** N))))

    qc = QuantumCircuit(N, N)
    qc.h(range(N))
    for _ in range(iters):
        qc.compose(grover_op, inplace=True)
    qc.measure(range(N), range(N))

    counts = StatevectorSampler().run([(qc,)], shots={shots}).result()[0].data.c.get_counts()
    best = max(counts, key=counts.get)
    best_q0 = best[::-1]  # convert little-endian to qubit-0-first
    prob = counts[best] / sum(counts.values())
    success = (best_q0 == MARKED)

    print("=== {title} ===")
    print("num_qubits:", qc.num_qubits)
    print("circuit.depth():", qc.decompose().depth())
    print("grover iterations:", iters)
    print("found:", best_q0, "target:", MARKED, "prob:", round(prob, 4))
    print("RESULT_JSON " + json.dumps({{
        "num_qubits": qc.num_qubits,
        "depth": qc.decompose().depth(),
        "num_params": 0,
        "num_terms": 1,
        "objective": round(prob, 4),
        "found": best_q0,
        "success": bool(success),
    }}))


if __name__ == "__main__":
    main()
"""


def build_grover_code(title, n, marked, shots):
    return GROVER_CODE.format(title=title, n=n, marked=marked, shots=shots)
