import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.quantum_info import Statevector
from scipy.optimize import minimize

def maxcut_objective(counts, graph):
    val = 0.0
    for bitstr, prob in counts.items():
        for i, j in graph:
            if bitstr[::-1][i] != bitstr[::-1][j]:
                val += prob
    return val

def build_qaoa_circuit(graph, gamma, beta, p=1, n=4):
    qc = QuantumCircuit(n)
    qc.h(range(n))
    for layer in range(p):
        for i, j in graph:
            qc.cx(i, j); qc.rz(2 * gamma[layer], j); qc.cx(i, j)
        for q in range(n):
            qc.rx(2 * beta[layer], q)
    return qc

def expectation(params, graph, n):
    p = len(params) // 2
    gamma = params[:p]; beta = params[p:]
    qc = build_qaoa_circuit(graph, gamma, beta, p=p, n=n)
    sv = Statevector.from_instruction(qc)
    probs = {format(i, f"0{n}b"): abs(sv.data[i]) ** 2 for i in range(2 ** n)}
    return -maxcut_objective(probs, graph)

def main():
    n = 4
    graph = [(0, 1), (1, 2), (2, 3), (3, 0)]  # 4-cycle
    p = 1
    x0 = np.array([0.5, 0.5])
    res = minimize(expectation, x0, args=(graph, n), method="COBYLA",
                   options={"maxiter": 200, "tol": 1e-6})
    # Evaluate final
    qc = build_qaoa_circuit(graph, res.x[:p], res.x[p:], p=p, n=n)
    sv = Statevector.from_instruction(qc)
    probs = {format(i, f"0{n}b"): abs(sv.data[i]) ** 2 for i in range(2 ** n)}
    cut = maxcut_objective(probs, graph)
    # Classical optimum: 4 (alternating bits)
    print(f"QAOA max-cut value = {cut:.3f}")
    print(f"Optimal max-cut = 4")
    print(f"Approx ratio = {cut / 4.0:.3f}")
    print(f"Converged: {cut / 4.0 > 0.75}")

if __name__ == "__main__":
    main()
