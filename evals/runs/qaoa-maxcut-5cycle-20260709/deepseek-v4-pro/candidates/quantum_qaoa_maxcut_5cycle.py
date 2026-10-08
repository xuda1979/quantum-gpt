import numpy as np
from qiskit.primitives import StatevectorSampler
from qiskit_algorithms import QAOA, MinimumEigenOptimizer
from qiskit_algorithms.optimizers import COBYLA
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizerResult

# 构建 Max-Cut 的 QUBO
qp = QuadraticProgram()
for i in range(5):
    qp.binary_var(f"x{i}")

edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
linear = {}
quadratic = {}
for u, v in edges:
    quadratic[(f"x{u}", f"x{v}")] = 2
    linear[f"x{u}"] = linear.get(f"x{u}", 0) - 1
    linear[f"x{v}"] = linear.get(f"x{v}", 0) - 1
qp.minimize(linear=linear, quadratic=quadratic)

# 设置 QAOA
sampler = StatevectorSampler()
optimizer = COBYLA(maxiter=100)
qaoa = QAOA(sampler=sampler, optimizer=optimizer, reps=1)
meo = MinimumEigenOptimizer(qaoa)

# 求解
result: MinimumEigenOptimizerResult = meo.solve(qp)
x = np.array(result.x).astype(int)

# 输出
print("Binary solution:", x.tolist())
set0 = [i for i, v in enumerate(x) if v == 0]
set1 = [i for i, v in enumerate(x) if v == 1]
print("Set 0:", set0)
print("Set 1:", set1)
cut_value = sum(1 for u, v in edges if x[u] != x[v])
print("Max-Cut value:", cut_value)
