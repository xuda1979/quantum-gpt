import networkx as nx
from qiskit.primitives import StatevectorSampler
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizer

G = nx.Graph()
G.add_edges_from([(0,1),(1,2),(2,3),(3,4),(4,0)])

qp = QuadraticProgram("maxcut")
for i in range(5):
    qp.binary_var(name=f"x{i}")

linear = {}
quadratic = {}
for i, j in G.edges():
    linear[f"x{i}"] = linear.get(f"x{i}", 0) + 1
    linear[f"x{j}"] = linear.get(f"x{j}", 0) + 1
    quadratic[(f"x{i}", f"x{j}")] = quadratic.get((f"x{i}", f"x{j}"), 0) - 2

linear = {k: -v for k, v in linear.items()}
quadratic = {k: -v for k, v in quadratic.items()}
qp.minimize(linear=linear, quadratic=quadratic)

sampler = StatevectorSampler()
optimizer = COBYLA(maxiter=200)
qaoa = QAOA(sampler=sampler, optimizer=optimizer, reps=2)
meo = MinimumEigenOptimizer(qaoa)
result = meo.solve(qp)

x = [int(result.x[i]) for i in range(5)]
set0 = [i for i in range(5) if x[i] == 0]
set1 = [i for i in range(5) if x[i] == 1]

cut = sum(1 for i, j in G.edges() if x[i] != x[j])

print("Binary solution:", x)
print("Vertex set 0:", set0)
print("Vertex set 1:", set1)
print("Max cut value:", cut)
