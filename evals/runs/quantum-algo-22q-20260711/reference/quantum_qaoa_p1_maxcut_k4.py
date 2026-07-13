import numpy as np
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator, StatevectorSampler
from qiskit.quantum_info import SparsePauliOp, Statevector
from scipy.optimize import minimize

EDGES = [(0, 1), (1, 2), (2, 0), (2, 3)]
N = 4

def build_cost():
    terms = [("I" * N, 0.0)]
    for (i, j) in EDGES:
        s = ["I"] * N
        s[N - 1 - i] = "Z"
        s[N - 1 - j] = "Z"
        terms.append(("".join(s), -0.5))
        terms[0] = ("I" * N, terms[0][1] + 0.5)
    return SparsePauliOp.from_list(terms)

def build_qaoa_circuit(gamma, beta, n=N):
    qc = QuantumCircuit(n)
    for q in range(n):
        qc.h(q)
    # Cost e^{-i gamma H_C}: for each edge (i,j), apply ZZ(gamma) = e^{i gamma/2 ZiZj}
    # The standard QAOA cost unitary is exp(-i gamma * (1 - ZiZj)/2) = exp(i gamma/2 ZiZj) * exp(-i gamma/2)
    # Global phase can be dropped. So apply exp(i gamma/2 * ZiZj) per edge.
    for (i, j) in EDGES:
        qc.rzz(2 * gamma, i, j)  # RZZ(theta) = exp(-i theta/2 ZiZj); we want exp(i gamma/2 ZiZj) -> theta = -gamma
        # Actually rzz(2*gamma) = exp(-i gamma ZiZj). We want exp(i gamma/2 ZiZj) -> use rzz(-gamma).
    # Redo with correct angle
    return None

def build_qaoa_circuit_v2(gamma, beta, n=N):
    qc = QuantumCircuit(n)
    for q in range(n):
        qc.h(q)
    # Cost unitary: exp(-i gamma H_C) where H_C = sum (1 - ZiZj)/2
    # exp(-i gamma (1 - ZiZj)/2) = exp(-i gamma/2) * exp(i gamma/2 ZiZj)
    # Drop global phase exp(-i gamma/2). Apply exp(i gamma/2 ZiZj) per edge.
    # Qiskit rzz(theta) = exp(-i theta/2 Z⊗Z). We want exp(i gamma/2 ZiZj), so theta = -gamma.
    for (i, j) in EDGES:
        qc.rzz(-gamma, i, j)
    # Mixer unitary: exp(-i beta sum X_i) = RX(2*beta) on each qubit
    for q in range(n):
        qc.rx(2 * beta, q)
    return qc

def main():
    H_C = build_cost()
    estimator = StatevectorEstimator()
    sampler = StatevectorSampler()

    def cost(params):
        g, b = params
        qc = build_qaoa_circuit_v2(g, b)
        sv = Statevector.from_instruction(qc)
        # Estimate <H_C>
        result = estimator.run([(qc, H_C)]).result()
        return result[0].data.evs

    best = None
    best_val = float("inf")
    rng = np.random.default_rng(42)
    for _ in range(5):
        x0 = rng.uniform(-np.pi, np.pi, size=2)
        res = minimize(cost, x0, method="Nelder-Mead", options={"maxiter": 60})
        if res.fun < best_val:
            best_val = res.fun
            best = res.x
    # Sample
    qc = build_qaoa_circuit_v2(*best)
    qc_meas = QuantumCircuit(N, N)
    qc_meas.compose(qc, inplace=True)
    qc_meas.measure(range(N), range(N))
    counts = sampler.run([qc_meas], shots=4000).result()[0].data.c.get_counts()
    # Compute cut value for each bitstring
    def cut_value(bs):
        # bs is q3 q2 q1 q0 (big-endian). bit i (from right) corresponds to qubit i.
        bits = [int(bs[N - 1 - i]) for i in range(N)]
        return sum(1 for (i, j) in EDGES if bits[i] != bits[j])
    best_cut = max(cut_value(b) for b in counts)
    print(f"cut_value = {best_cut}")
    print(f"optimal: {'True' if best_cut == 4 else 'False'}")

if __name__ == "__main__":
    main()
