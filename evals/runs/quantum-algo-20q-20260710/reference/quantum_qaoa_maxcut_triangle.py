import networkx as nx
from qiskit.primitives import StatevectorSampler
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_optimization.applications import Maxcut


def main():
    edges = [(0,1), (1,2), (2,0)]
    G = nx.Graph()
    G.add_edges_from(edges)
    n = G.number_of_nodes()
    mc = Maxcut(G)
    qp = mc.to_quadratic_program()
    sampler = StatevectorSampler()
    qaoa = QAOA(sampler=sampler, optimizer=COBYLA(maxiter=300), reps=2)
    meo = MinimumEigenOptimizer(qaoa)
    result = meo.solve(qp)
    bs = "".join(str(int(result.x[i])) for i in range(n))
    setA = [i for i in range(n) if bs[i] == "0"]
    setB = [i for i in range(n) if bs[i] == "1"]
    cut = sum(1 for u, v in edges if bs[u] != bs[v])
    print(f"Binary solution: {bs}")
    print(f"Set A: {setA}")
    print(f"Set B: {setB}")
    print(f"Max-cut value: {cut}")

if __name__ == "__main__":
    main()
