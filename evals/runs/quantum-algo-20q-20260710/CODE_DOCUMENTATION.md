# 20 Quantum Algorithm Coding Problems — Complete Code Documentation

**Run dir:** `evals/runs/quantum-algo-20q-20260710/`
**Date:** 2026-07-10

This file documents **all 60 candidate programs** (20 problems × 3 models) generated in this session,
alongside the reference solution for each problem. Each program is a complete Python script with
a `def main()` that calculates and prints a deterministic numerical / structural result.

## Models

| short name | role | backend |
|---|---|---|
| `glm5.2` | frontier base (teacher) | local proxy `http://127.0.0.1:18105/v1/responses` (OpenAI Responses API) |
| `deepseek-v4-pro` | frontier base (teacher) | Huanxin `qdlake` chat completions |
| `qwen3.6-27b-rag` | **27B Qwen3.6 + RAG adapter** (quantum-intelligence MCP backend) | Huanxin `kunlun` chat completions |

## Problem list (20)

| # | id | title |
|---|---|---|
| 1 | `quantum_bell_state_probability` | Bell-state measurement probabilities |
| 2 | `quantum_qft_3qubit_phase` | 3-qubit QFT phase pattern |
| 3 | `quantum_grover_2qubit_marked11` | Grover's algorithm finds |11> on 2 qubits |
| 4 | `quantum_maxcut_bruteforce_4vertices` | Brute-force MaxCut on a 4-vertex graph |
| 5 | `quantum_qaoa_maxcut_triangle` | QAOA Max-Cut on a triangle graph |
| 6 | `quantum_deutsch_jozsa_balanced` | Deutsch-Jozsa on a balanced function |
| 7 | `quantum_bernstein_vazirani_hidden` | Bernstein-Vazirani hidden string s=101 |
| 8 | `quantum_swap_test_overlap` | SWAP test overlap of |0> and |+> |
| 9 | `quantum_teleportation_fidelity` | Quantum teleportation of |+> state (coherent) |
| 10 | `quantum_density_matrix_pure_state` | Density matrix purity of a Bell state |
| 11 | `quantum_partial_trace_bipartite` | Partial trace of a bipartite pure state |
| 12 | `quantum_pauli_expectation_x` | <X> expectation value for |+> |
| 13 | `quantum_ising_ground_state_energy` | Transverse-field Ising ground energy on 2 qubits |
| 14 | `quantum_vqe_h2_energy` | VQE on H2 (2-qubit) with 2-layer Ry ansatz + COBYLA |
| 15 | `quantum_grover_3qubit_marked101` | Grover 3-qubit finds |101> |
| 16 | `quantum_phase_estimation_pi4` | QPE estimates phase 1/4 for unitary S |
| 17 | `quantum_bit_flip_code_recovery` | 3-qubit bit-flip code with X error on qubit 1 |
| 18 | `quantum_superdense_coding_11` | Superdense coding sends 2 bits '11' via 1 qubit |
| 19 | `quantum_ghz_state_5qubit` | 5-qubit GHZ state measurement |
| 20 | `quantum_trotterized_xxz` | Trotterized XXZ Heisenberg on 2 qubits: <Z on q0> at t=1.0 |

## 1. Bell-state measurement probabilities (`quantum_bell_state_probability`)

### Prompt

```
Write a complete, runnable Python program using Qiskit that:
1. Builds a 2-qubit Bell state |Phi+> = (|00> + |11>)/sqrt(2) (apply H on q0, then CX q0->q1).
2. Uses StatevectorSampler to sample 2000 shots.
3. In `def main()`, compute and print the empirical probability of measuring "00" and "11" (each should be approximately 0.5).
Output exactly two lines:
  P(00) = <value rounded to 3 decimals>
  P(11) = <value rounded to 3 decimals>
The script must call main() under `if __name__ == "__main__":`.
```

### Expected key output substrings

- `P(00) = 0.`
- `P(11) = 0.`

### Reference solution

```python
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

def main():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    sampler = StatevectorSampler()
    result = sampler.run([qc], shots=2000).result()
    counts = result[0].data.meas.get_counts()
    total = sum(counts.values())
    p00 = counts.get("00", 0) / total
    p11 = counts.get("11", 0) / total
    print(f"P(00) = {p00:.3f}")
    print(f"P(11) = {p11:.3f}")

if __name__ == "__main__":
    main()
```

### Candidate — `glm5.2`

**Status:** `PASS` (2.6s)

```python
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

def main():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()

    sampler = StatevectorSampler()
    job = sampler.run([qc], shots=2000)
    result = job.result()

    counts = result[0].data.meas.get_counts()
    total = sum(counts.values())

    p00 = counts.get("00", 0) / total
    p11 = counts.get("11", 0) / total

    print(f"P(00) = {p00:.3f}")
    print(f"P(11) = {p11:.3f}")

if __name__ == "__main__":
    main()
```

### Candidate — `deepseek-v4-pro`

**Status:** `PASS` (0.4s)

```python
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
import numpy as np

def main():
    # Build 2-qubit Bell state |Phi+>
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()

    # Sample 2000 shots
    sampler = StatevectorSampler(seed=42)
    job = sampler.run([qc], shots=2000)
    result = job.result()[0]

    # Get counts
    counts = result.data.meas.get_counts()

    # Compute empirical probabilities
    total_shots = sum(counts.values())
    p00 = counts.get("00", 0) / total_shots
    p11 = counts.get("11", 0) / total_shots

    print(f"P(00) = {p00:.3f}")
    print(f"P(11) = {p11:.3f}")

if __name__ == "__main__":
    main()
```

### Candidate — `qwen3.6-27b-rag`

**Status:** `MISSING` (0.0s)

**Missing substrings:** ['P(00) = 0.', 'P(11) = 0.']

```
# generation error: HTTP 503: no healthy upstream
```

## 2. 3-qubit QFT phase pattern (`quantum_qft_3qubit_phase`)

### Prompt

```
Write a complete, runnable Python program using Qiskit that:
1. Builds the state |5> = |101> on 3 qubits (X on q0 and q2).
2. Applies the 3-qubit Quantum Fourier Transform.
3. In `def main()`, simulates with StatevectorSampler (2000 shots) and prints the two most-probable measurement bitstrings and their counts.
Output exactly two lines:
  Top: <bitstring> count=<count>
  2nd: <bitstring> count=<count>
Call main() under `if __name__ == "__main__":`.
```

### Expected key output substrings

- `Top: `
- `2nd: `

### Reference solution

```python
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

def QFT3():
    qc = QuantumCircuit(3, name="qft3")
    qc.h(2)
    qc.cp(3.141592653589793/2, 1, 2)
    qc.cp(3.141592653589793/4, 0, 2)
    qc.h(1)
    qc.cp(3.141592653589793/2, 0, 1)
    qc.h(0)
    qc.swap(0, 2)
    return qc

def main():
    qc = QuantumCircuit(3)
    qc.x(0)
    qc.x(2)
    qc.compose(QFT3(), inplace=True)
    qc.measure_all()
    sampler = StatevectorSampler()
    counts = sampler.run([qc], shots=2000).result()[0].data.meas.get_counts()
    top = sorted(counts.items(), key=lambda kv: -kv[1])[:2]
    print(f"Top: {top[0][0]} count={top[0][1]}")
    print(f"2nd: {top[1][0]} count={top[1][1]}")

if __name__ == "__main__":
    main()
```

### Candidate — `glm5.2`

**Status:** `EXIT` (0.0s)

**Stderr:** `File "/Users/daxu/software/quantum-gpt/evals/runs/quantum-algo-20q-20260710/candidates/glm5.2/quantum_qft_3qubit_phase.py", line 1 |     """QFT on the first n qubits in circuit""" | IndentationError: unexpected indent |`

```python
    """QFT on the first n qubits in circuit"""
    for j in range(n):
        circuit.h(j)
        for k in range(j+1,n):
            np_angle = np.pi/float(2**(k-j))
            circuit.cp(np_angle, k, j)
    swap_registers(circuit, n)
```

### Candidate — `deepseek-v4-pro`

**Status:** `PASS` (0.4s)

```python
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
from qiskit.visualization import plot_histogram

def main():
    # 1. Build |5> = |101> on 3 qubits
    qc = QuantumCircuit(3)
    qc.x(0)
    qc.x(2)
    qc.barrier()
    
    # 2. Apply 3-qubit QFT
    # QFT on 3 qubits
    qc.h(2)
    qc.cp(3.141592653589793/2, 1, 2)  # pi/2
    qc.cp(3.141592653589793/4, 0, 2)  # pi/4
    qc.h(1)
    qc.cp(3.141592653589793/2, 0, 1)  # pi/2
    qc.h(0)
    # Swap qubits to get standard QFT ordering
    qc.swap(0, 2)
    
    qc.measure_all()
    
    # 3. Simulate with StatevectorSampler
    sampler = StatevectorSampler(seed=42)
    job = sampler.run([qc], shots=2000)
    result = job.result()
    
    # Get counts from the first (and only) circuit result
    counts = result[0].data.meas.get_counts()
    
    # Sort by count descending, get top two
    sorted_counts = sorted(counts.items(), key=lambda item: item[1], reverse=True)
    top1 = sorted_counts[0]
    top2 = sorted_counts[1] if len(sorted_counts) > 1 else ("N/A", 0)
    
    print(f"Top: {top1[0]} count={top1[1]}")
    print(f"2nd: {top2[0]} count={top2[1]}")

if __name__ == "__main__":
    main()
```

### Candidate — `qwen3.6-27b-rag`

**Status:** `MISSING` (0.0s)

**Missing substrings:** ['Top: ', '2nd: ']

```
# generation error: HTTP 503: no healthy upstream
```

## 3. Grover's algorithm finds |11> on 2 qubits (`quantum_grover_2qubit_marked11`)

### Prompt

```
Write a complete, runnable Python program using Qiskit that:
1. Implements Grover's algorithm for 2 qubits with the marked state |11>.
2. Uses exactly 1 Grover iteration (optimal for N=4).
3. In `def main()`, uses StatevectorSampler with 1000 shots and prints the most-measured bitstring and its probability.
Output exactly:
  Most likely: <bitstring>
  Probability: <value rounded to 3 decimals>
Call main() under `if __name__ == "__main__":`.
```

### Expected key output substrings

- `Most likely: 11`
- `Probability:`

### Reference solution

```python
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

def main():
    qc = QuantumCircuit(2)
    qc.h([0, 1])
    qc.cz(0, 1)
    qc.h([0, 1])
    qc.z([0, 1])
    qc.cz(0, 1)
    qc.h([0, 1])
    qc.measure_all()
    sampler = StatevectorSampler()
    counts = sampler.run([qc], shots=1000).result()[0].data.meas.get_counts()
    top_bs, top_n = max(counts.items(), key=lambda kv: kv[1])
    total = sum(counts.values())
    print(f"Most likely: {top_bs}")
    print(f"Probability: {top_n/total:.3f}")

if __name__ == "__main__":
    main()
```

### Candidate — `glm5.2`

**Status:** `EXIT` (0.0s)

**Stderr:** `Traceback (most recent call last): |   File "/Users/daxu/software/quantum-gpt/evals/runs/quantum-algo-20q-20260710/candidates/glm5.2/quantum_grover_2qubit_marked11.py", line 1, in <module> |     qc.h([0,1]) | NameError: name 'qc' is not defined |`

```python
qc.h([0,1])
qc.z([0,1])
qc.cz(0,1)
qc.h([0,1])
```

### Candidate — `deepseek-v4-pro`

**Status:** `PASS` (0.7s)

```python
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit_aer.primitives import Sampler
from qiskit.primitives import StatevectorSampler
import numpy as np

def grover_2qubit():
    qc = QuantumCircuit(2)
    # Step 1: Initialize superposition
    qc.h([0, 1])
    # Step 2: Oracle for |11>
    qc.cz(0, 1)
    # Step 3: Diffusion operator
    qc.h([0, 1])
    qc.x([0, 1])
    qc.cz(0, 1)
    qc.x([0, 1])
    qc.h([0, 1])
    qc.measure_all()
    return qc

def main():
    qc = grover_2qubit()
    sampler = StatevectorSampler(seed=42)
    job = sampler.run([qc], shots=1000)
    result = job.result()
    counts = result[0].data.meas.get_counts()
    most_likely = max(counts, key=counts.get)
    prob = counts[most_likely] / 1000
    print(f"Most likely: {most_likely}")
    print(f"Probability: {prob:.3f}")

if __name__ == "__main__":
    main()
```

### Candidate — `qwen3.6-27b-rag`

**Status:** `EXIT` (0.0s)

**Stderr:** `File "/Users/daxu/software/quantum-gpt/evals/runs/quantum-algo-20q-20260710/candidates/qwen3.6-27b-rag/quantum_grover_2qubit_marked11.py", line 2 |     <html lang="zh-CN"> |     ^ | SyntaxError: invalid syntax |`

```
# generation error: HTTP 503: <!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 - 页面未找到 | 焕新</title>
    <style>
```

## 4. Brute-force MaxCut on a 4-vertex graph (`quantum_maxcut_bruteforce_4vertices`)

### Prompt

```
Write a complete, runnable Python program (no Qiskit needed) that:
1. Defines a 4-vertex undirected graph with edges: (0,1), (1,2), (2,3), (3,0), (0,2).
2. In `def main()`, brute-forces all 2^4 = 16 bitstring assignments, computes the MaxCut value for each, and prints the maximum cut value and one optimal bitstring.
Output exactly:
  Max cut value: <int>
  Optimal bitstring: <4-char 0/1 string>
Call main() under `if __name__ == "__main__":`.
```

### Expected key output substrings

- `Max cut value: 4`
- `Optimal bitstring: `

### Reference solution

```python
def main():
    edges = [(0,1), (1,2), (2,3), (3,0), (0,2)]
    n = 4
    best_cut = -1
    best_bs = None
    for i in range(1 << n):
        bs = format(i, f"0{n}b")
        cut = sum(1 for u, v in edges if bs[u] != bs[v])
        if cut > best_cut:
            best_cut = cut
            best_bs = bs
    print(f"Max cut value: {best_cut}")
    print(f"Optimal bitstring: {best_bs}")

if __name__ == "__main__":
    main()
```

### Candidate — `glm5.2`

**Status:** `PASS` (0.0s)

```python
def main():
    edges = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)]
    max_cut = -1
    best_bits = "0000"

    for n in range(16):
        bits = format(n, "04b")
        cut = 0
        for u, v in edges:
            if bits[u] != bits[v]:
                cut += 1
        if cut > max_cut:
            max_cut = cut
            best_bits = bits

    print(f"Max cut value: {max_cut}")
    print(f"Optimal bitstring: {best_bits}")


if __name__ == "__main__":
    main()
```

### Candidate — `deepseek-v4-pro`

**Status:** `PASS` (0.0s)

```python
# graph_cut.py

def main():
    # Define edges
    edges = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)]
    n = 4  # number of vertices

    max_cut = -1
    best_assignment = None

    # Brute-force all 2^4 = 16 assignments
    for i in range(16):
        # Convert integer to 4-bit binary string
        assignment = format(i, '04b')
        cut_value = 0
        for u, v in edges:
            if assignment[u] != assignment[v]:
                cut_value += 1
        if cut_value > max_cut:
            max_cut = cut_value
            best_assignment = assignment

    print(f"Max cut value: {max_cut}")
    print(f"Optimal bitstring: {best_assignment}")

if __name__ == "__main__":
    main()
```

### Candidate — `qwen3.6-27b-rag`

**Status:** `MISSING` (0.0s)

**Missing substrings:** ['Max cut value: 4', 'Optimal bitstring: ']

```
# generation error: HTTP 503: no healthy upstream
```

## 5. QAOA Max-Cut on a triangle graph (`quantum_qaoa_maxcut_triangle`)

### Prompt

```
Write a complete, runnable Python program using Qiskit + qiskit_optimization that:
1. Builds a triangle graph with 3 vertices and edges (0,1), (1,2), (2,0).
2. Uses qiskit_optimization.applications.Maxcut to build the QUBO, then solves it with QAOA using StatevectorSampler, COBYLA(maxiter=300), reps=2, and MinimumEigenOptimizer.
3. In `def main()`, prints the binary solution, the two vertex sets, and the max-cut value.
Output exactly:
  Binary solution: <3-char 0/1 string>
  Set A: <list of ints>
  Set B: <list of ints>
  Max-cut value: <int>
Call main() under `if __name__ == "__main__":`.
```

### Expected key output substrings

- `Binary solution: `
- `Max-cut value: 2`

### Reference solution

```python
from qiskit.primitives import StatevectorSampler
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_optimization.applications import Maxcut
import networkx as nx

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
```

### Candidate — `glm5.2`

**Status:** `EXIT` (8.5s)

**Stderr:** `/Users/daxu/software/quantum-gpt/evals/runs/quantum-algo-20q-20260710/candidates/glm5.2/quantum_qaoa_maxcut_triangle.py:1: DeprecationWarning: Using Qiskit with Python 3.9 is deprecated as of the 2.1.0 release. Support for running Qiskit with Python 3.9 will be removed in the 2.3.0 release, which co`

```python
from qiskit.primitives import StatevectorSampler
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit_optimization.applications import Maxcut
from qiskit_optimization.algorithms import MinimumEigenOptimizer
import networkx as nx


def main():
    # Build triangle graph
    graph = nx.Graph()
    graph.add_nodes_from([0, 1, 2])
    graph.add_edges_from([(0, 1), (1, 2), (2, 0)])

    # Build QUBO using Maxcut
    maxcut = Maxcut(graph)
    qp = maxcut.to_quadratic_program()
    qubo = qp.to_ising()  # or qp.to_qubo()
    
    # Setup QAOA
    sampler = StatevectorSampler()
    optimizer = COBYLA(maxiter=300)
    qaoa = QAOA(sampler=sampler, optimizer=optimizer, reps=2)
    
    # Solve with MinimumEigenOptimizer
    meo = MinimumEigenOptimizer(qaoa)
    result = meo.solve(qp)
    
    # Get the solution
    x = result.x
    binary_solution = ''.join(str(int(b)) for b in x)
    
    set_a = [i for i, b in enumerate(x) if b == 1]
    set_b = [i for i, b in enumerate(x) if b == 0]
    
    # Max-cut value
    maxcut_value = maxcut.max_cut_value(x)  # or compute manually
    
    print(f"Binary solution: {binary_solution}")
    print(f"Set A: {set_a}")
    print(f"Set B: {set_b}")
    print(f"Max-cut value: {maxcut_value}")


if __name__ == "__main__":
    main()
```

### Candidate — `deepseek-v4-pro`

**Status:** `EXIT` (1.6s)

**Stderr:** `Traceback (most recent call last): |   File "/Users/daxu/software/quantum-gpt/evals/runs/quantum-algo-20q-20260710/candidates/deepseek-v4-pro/quantum_qaoa_maxcut_triangle.py", line 2, in <module> |     from qiskit_algorithms import QAOA, COBYLA | ImportError: cannot import name 'COBYLA' from 'qiskit`

```python
import numpy as np
from qiskit_algorithms import QAOA, COBYLA
from qiskit_algorithms.optimizers import COBYLA as COBYLAOptimizer
from qiskit.primitives import StatevectorSampler
from qiskit_optimization.applications import Maxcut
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_optimization import QuadraticProgram

def main():
    # 1. Build triangle graph
    graph = np.array([[0, 1, 1],
                      [1, 0, 1],
                      [1, 1, 0]])
    
    # 2. Build QUBO via Maxcut application
    maxcut = Maxcut(graph)
    qubo = maxcut.to_quadratic_program()
    
    # Set up QAOA with StatevectorSampler and COBYLA
    sampler = StatevectorSampler()
    optimizer = COBYLAOptimizer(maxiter=300)
    qaoa = QAOA(sampler=sampler, optimizer=optimizer, reps=2)
    
    # Solve with MinimumEigenOptimizer
    min_eigen_optimizer = MinimumEigenOptimizer(qaoa)
    result = min_eigen_optimizer.solve(qubo)
    
    # 3. Extract and print results
    binary_solution = result.x
    binary_str = ''.join(str(int(bit)) for bit in binary_solution)
    
    set_a = [i for i, bit in enumerate(binary_solution) if bit == 0]
    set_b = [i for i, bit in enumerate(binary_solution) if bit == 1]
    
    maxcut_value = int(result.fval)
    
    print(f"Binary solution: {binary_str}")
    print(f"Set A: {set_a}")
    print(f"Set B: {set_b}")
    print(f"Max-cut value: {maxcut_value}")

if __name__ == "__main__":
    main()
```

### Candidate — `qwen3.6-27b-rag`

**Status:** `MISSING` (0.0s)

**Missing substrings:** ['Binary solution: ', 'Max-cut value: 2']

```
# generation error: HTTP 503: no healthy upstream
```

## 6. Deutsch-Jozsa on a balanced function (`quantum_deutsch_jozsa_balanced`)

### Prompt

```
Write a complete, runnable Python program using Qiskit that:
1. Implements the Deutsch-Jozsa algorithm for a 2-input-bit balanced function f(x0, x1) = x0 (i.e. f is 0 when x0=0, 1 when x0=1).
2. Uses 2 query qubits + 1 ancilla, applies H to all, oracle (CX from q0 to ancilla), H on query qubits, measures.
3. In `def main()`, uses StatevectorSampler (1000 shots) and prints the measured query-bitstring and the classification ("constant" if 00, "balanced" otherwise).
Output exactly:
  Measurement: <2-char bitstring>
  Function is: <constant|balanced>
Call main() under `if __name__ == "__main__":`.
```

### Expected key output substrings

- `Measurement: `
- `Function is: balanced`

### Reference solution

```python
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

def main():
    qc = QuantumCircuit(3, 2)
    qc.x(2)
    qc.h([0, 1, 2])
    qc.cx(0, 2)
    qc.h([0, 1])
    qc.measure([0, 1], [0, 1])
    sampler = StatevectorSampler()
    counts = sampler.run([qc], shots=1000).result()[0].data.c.get_counts()
    top = max(counts.items(), key=lambda kv: kv[1])[0]
    classification = "constant" if top == "00" else "balanced"
    print(f"Measurement: {top}")
    print(f"Function is: {classification}")

if __name__ == "__main__":
    main()
```

### Candidate — `glm5.2`

**Status:** `EXIT` (0.3s)

**Stderr:** `/Users/daxu/software/quantum-gpt/evals/runs/quantum-algo-20q-20260710/candidates/glm5.2/quantum_deutsch_jozsa_balanced.py:1: DeprecationWarning: Using Qiskit with Python 3.9 is deprecated as of the 2.1.0 release. Support for running Qiskit with Python 3.9 will be removed in the 2.3.0 release, which `

```python
from qiskit.primitives import StatevectorSampler
sampler = StatevectorSampler()
job = sampler.run([circuit], shots=1000)
result = job.result()
counts = result[0].data.meas.get_counts()
```

### Candidate — `deepseek-v4-pro`

**Status:** `PASS` (0.6s)

```python
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector

def deutsch_jozsa_balanced():
    # 2 query qubits + 1 ancilla
    qc = QuantumCircuit(3, 2)
    
    # Initialize ancilla to |1> (X gate) then H on all
    qc.x(2)
    qc.h([0, 1, 2])
    
    # Oracle for f(x0,x1) = x0: CX from q0 to ancilla
    qc.cx(0, 2)
    
    # H on query qubits
    qc.h([0, 1])
    
    # Measure query qubits
    qc.measure([0, 1], [0, 1])
    
    return qc

def main():
    qc = deutsch_jozsa_balanced()
    
    # Use StatevectorSampler (AerSimulator with statevector method)
    simulator = AerSimulator(method='statevector')
    job = simulator.run(qc, shots=1000)
    result = job.result()
    counts = result.get_counts()
    
    # Get the most frequent measurement result
    measured = max(counts, key=counts.get)
    
    # Classification
    classification = "constant" if measured == "00" else "balanced"
    
    print(f"Measurement: {measured}")
    print(f"Function is: {classification}")

if __name__ == "__main__":
    main()
```

### Candidate — `qwen3.6-27b-rag`

**Status:** `EXIT` (0.0s)

**Stderr:** `File "/Users/daxu/software/quantum-gpt/evals/runs/quantum-algo-20q-20260710/candidates/qwen3.6-27b-rag/quantum_deutsch_jozsa_balanced.py", line 2 |     <html lang="zh-CN"> |     ^ | SyntaxError: invalid syntax |`

```
# generation error: HTTP 503: <!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 - 页面未找到 | 焕新</title>
    <style>
```

## 7. Bernstein-Vazirani hidden string s=101 (`quantum_bernstein_vazirani_hidden`)

### Prompt

```
Write a complete, runnable Python program using Qiskit that:
1. Implements the Bernstein-Vazirani algorithm to find a hidden bitstring s = "101" (3 bits).
2. Oracle: f(x) = s . x mod 2 (i.e. f = x0 XOR x2).
3. In `def main()`, uses StatevectorSampler (1000 shots) and prints the recovered hidden bitstring (in natural order, so it should read "101").
Output exactly:
  Hidden string: <3-char bitstring>
Call main() under `if __name__ == "__main__":`.
```

### Expected key output substrings

- `Hidden string: 101`

### Reference solution

```python
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

def main():
    s = "101"
    n = len(s)
    qc = QuantumCircuit(n + 1, n)
    qc.x(n)
    qc.h(range(n + 1))
    for i, bit in enumerate(s):
        if bit == "1":
            qc.cx(i, n)
    qc.h(range(n))
    qc.measure(range(n), range(n))
    sampler = StatevectorSampler()
    counts = sampler.run([qc], shots=1000).result()[0].data.c.get_counts()
    top = max(counts.items(), key=lambda kv: kv[1])[0]
    recovered = top[::-1]
    print(f"Hidden string: {recovered}")

if __name__ == "__main__":
    main()
```

### Candidate — `glm5.2`

**Status:** `PASS` (0.3s)

```python
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

def build_oracle(n, s):
    oracle = QuantumCircuit(n + 1)
    for i in range(n):
        if s[i] == '1':
            oracle.cx(i, n)
    return oracle

def main():
    n = 3
    s = "101"
    
    qc = QuantumCircuit(n + 1, n)
    
    # Initialize ancilla to |-> state
    qc.x(n)
    qc.h(n)
    
    # Apply Hadamard to input qubits
    qc.h(range(n))
    
    # Apply oracle
    oracle = build_oracle(n, s)
    qc.compose(oracle, inplace=True)
    
    # Apply Hadamard to input qubits
    qc.h(range(n))
    
    # Measure
    qc.measure(range(n), range(n))
    
    # Run with StatevectorSampler
    sampler = StatevectorSampler()
    job = sampler.run([qc], shots=1000)
    result = job.result()
    
    # Get counts
    counts = result[0].data.c.get_counts()
    
    # Find most common result
    most_common = max(counts, key=counts.get)
    
    # Reverse to get natural order (s[0] s[1] s[2])
    recovered = most_common[::-1]
    
    print(f"Hidden string: {recovered}")

if __name__ == "__main__":
    main()
```

### Candidate — `deepseek-v4-pro`

**Status:** `PASS` (0.3s)

```python
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
import numpy as np

def bernstein_vazirani_oracle(s: str) -> QuantumCircuit:
    n = len(s)
    oracle = QuantumCircuit(n + 1)
    for i, bit in enumerate(s):
        if bit == '1':
            oracle.cx(i, n)
    return oracle

def main():
    s = "101"
    n = len(s)
    
    # Create circuit with n+1 qubits and n classical bits
    qc = QuantumCircuit(n + 1, n)
    
    # Initialize last qubit to |1>
    qc.x(n)
    
    # Apply Hadamard to all qubits
    qc.h(range(n + 1))
    
    # Apply oracle
    oracle = bernstein_vazirani_oracle(s)
    qc.compose(oracle, inplace=True)
    
    # Apply Hadamard to first n qubits
    qc.h(range(n))
    
    # Measure first n qubits
    qc.measure(range(n), range(n))
    
    # Run with StatevectorSampler
    sampler = StatevectorSampler(seed=42)
    job = sampler.run([qc], shots=1000)
    result = job.result()
    
    # Get the most frequent result
    counts = result[0].data.c.get_counts()
    max_count = max(counts.values())
    measured = next(k for k, v in counts.items() if v == max_count)
    
    # The measured string is in little-endian order (q0 is rightmost), reverse to get natural order
    recovered = measured[::-1]
    
    print(f"Hidden string: {recovered}")

if __name__ == "__main__":
    main()
```

### Candidate — `qwen3.6-27b-rag`

**Status:** `MISSING` (0.0s)

**Missing substrings:** ['Hidden string: 101']

```
# generation error: HTTP 503: no healthy upstream
```

## 8. SWAP test overlap of |0> and |+> (`quantum_swap_test_overlap`)

### Prompt

```
Write a complete, runnable Python program using Qiskit that:
1. Builds a SWAP-test circuit: ancilla q0, state A = |0> on q1, state B = |+> = H|0> on q2.
2. Applies H on ancilla, CSWAPs (controlled by ancilla) between q1 and q2, H on ancilla, measure ancilla.
3. In `def main()`, uses StatevectorSampler (4000 shots), computes P(ancilla=0), and prints |<A|B>|^2 = 2*P(0) - 1.
Output exactly:
  P(0) = <value rounded to 3 decimals>
  |<A|B>|^2 = <value rounded to 3 decimals>
Call main() under `if __name__ == "__main__":`.
```

### Expected key output substrings

- `P(0) = 0.7`
- `|<A|B>|^2 = 0.`

### Reference solution

```python
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

def main():
    qc = QuantumCircuit(3, 1)
    qc.h(2)
    qc.h(0)
    qc.cswap(0, 1, 2)
    qc.h(0)
    qc.measure(0, 0)
    sampler = StatevectorSampler()
    counts = sampler.run([qc], shots=4000).result()[0].data.c.get_counts()
    total = sum(counts.values())
    p0 = counts.get("0", 0) / total
    overlap_sq = 2 * p0 - 1
    print(f"P(0) = {p0:.3f}")
    print(f"|<A|B>|^2 = {overlap_sq:.3f}")

if __name__ == "__main__":
    main()
```

### Candidate — `glm5.2`

**Status:** `MISSING` (0.4s)

**Missing substrings:** ['P(0) = 0.7', '|<A|B>|^2 = 0.']

```python
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

qc = QuantumCircuit(1)
qc.h(0)
qc.measure_all()

sampler = StatevectorSampler()
job = sampler.run([qc], shots=1000)
result = job.result()
```

### Candidate — `deepseek-v4-pro`

**Status:** `MISSING` (0.4s)

**Missing substrings:** ['P(0) = 0.7', '|<A|B>|^2 = 0.']

```python
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
import numpy as np

def main():
    # Build SWAP-test circuit
    qc = QuantumCircuit(3, 1)
    # Prepare state B = |+> on q2
    qc.h(2)
    # SWAP test: H on ancilla, CSWAPs, H on ancilla
    qc.h(0)
    qc.cswap(0, 1, 2)
    qc.h(0)
    # Measure ancilla
    qc.measure(0, 0)

    # Run with StatevectorSampler
    sampler = StatevectorSampler(seed=42)
    job = sampler.run([qc], shots=4000)
    result = job.result()[0]
    counts = result.data.c.get_counts()

    # Compute P(0)
    shots = 4000
    count0 = counts.get(0, 0)
    p0 = count0 / shots

    # Compute |<A|B>|^2 = 2*P(0) - 1
    overlap = 2 * p0 - 1

    print(f"P(0) = {p0:.3f}")
    print(f"|<A|B>|^2 = {overlap:.3f}")

if __name__ == "__main__":
    main()
```

### Candidate — `qwen3.6-27b-rag`

**Status:** `MISSING` (0.0s)

**Missing substrings:** ['P(0) = 0.7', '|<A|B>|^2 = 0.']

```
# generation error: HTTP 503: no healthy upstream
```

## 9. Quantum teleportation of |+> state (coherent) (`quantum_teleportation_fidelity`)

### Prompt

```
Write a complete, runnable Python program using Qiskit that:
1. Teleports the state |+> from Alice (q0) to Bob (q2) using a Bell pair (q1, q2) and coherent (no mid-circuit measurement) classical corrections.
   Steps: prepare |+> on q0; create Bell pair on (q1, q2); apply CX q0->q1 then H q0; apply CX q1->q2 and CZ q0->q2 (coherent corrections).
2. In `def main()`, uses qiskit.primitives.StatevectorEstimator to compute the expectation value <X> on qubit q2 (the teleported state, which should be |+>).
Output exactly:
  <X> on Bob = <value rounded to 6 decimals>
Call main() under `if __name__ == "__main__":`.
```

### Expected key output substrings

- `<X> on Bob = 1.000000`

### Reference solution

```python
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator

def main():
    qc = QuantumCircuit(3)
    qc.h(0)              # prepare |+> on q0
    qc.h(1); qc.cx(1, 2)  # Bell pair (q1, q2)
    qc.cx(0, 1); qc.h(0)  # Alice's Bell-basis transform
    qc.cx(1, 2); qc.cz(0, 2)  # Coherent corrections
    est = StatevectorEstimator()
    obs = SparsePauliOp.from_list([("IIX", 1.0)])
    result = est.run([(qc, obs)]).result()
    val = float(result[0].data.evs.item())
    print(f"<X> on Bob = {val:.6f}")

if __name__ == "__main__":
    main()
```

### Candidate — `glm5.2`

**Status:** `MISSING` (0.4s)

**Missing substrings:** ['<X> on Bob = 1.000000']

```python
from qiskit.circuit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp

estimator = StatevectorEstimator()
circuit = QuantumCircuit(2)
circuit.h(0)
circuit.cx(0, 1)
observable = SparsePauliOp.from_list([("XX", 1), ("YY", -1)])
job = estimator.run([(circuit, observable)])
result = job.result()
print(result[0].data.evs)
```

### Candidate — `deepseek-v4-pro`

**Status:** `EXIT` (0.4s)

**Stderr:** `/Users/daxu/software/quantum-gpt/evals/runs/quantum-algo-20q-20260710/candidates/deepseek-v4-pro/quantum_teleportation_fidelity.py:1: DeprecationWarning: Using Qiskit with Python 3.9 is deprecated as of the 2.1.0 release. Support for running Qiskit with Python 3.9 will be removed in the 2.3.0 releas`

```python
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator
import numpy as np

def main():
    # Create circuit with 3 qubits and 0 classical bits
    qc = QuantumCircuit(3, 0)
    
    # Step 1: Prepare |+> on q0
    qc.h(0)
    
    # Step 2: Create Bell pair on (q1, q2)
    qc.h(1)
    qc.cx(1, 2)
    
    # Step 3: Apply CX q0->q1 then H q0
    qc.cx(0, 1)
    qc.h(0)
    
    # Step 4: Coherent corrections: CX q1->q2 and CZ q0->q2
    qc.cx(1, 2)
    qc.cz(0, 2)
    
    # Compute expectation value <X> on qubit q2
    estimator = StatevectorEstimator()
    job = estimator.run([(qc, [('X', [2])])])
    result = job.result()
    exp_val = result[0].data.evs[0]
    
    print(f"<X> on Bob = {exp_val:.6f}")

if __name__ == "__main__":
    main()
```

### Candidate — `qwen3.6-27b-rag`

**Status:** `MISSING` (0.0s)

**Missing substrings:** ['<X> on Bob = 1.000000']

```
# generation error: HTTP 503: no healthy upstream
```

## 10. Density matrix purity of a Bell state (`quantum_density_matrix_pure_state`)

### Prompt

```
Write a complete, runnable Python program using Qiskit that:
1. Builds the Bell state |Phi+> = (|00> + |11>)/sqrt(2).
2. Uses qiskit.quantum_info.DensityMatrix to compute the density matrix rho = |Phi+><Phi+|.
3. In `def main()`, computes Tr(rho^2) (purity) and the von-Neumann entropy S(rho) = -Tr(rho log2 rho), and prints both.
Output exactly:
  Purity = <value rounded to 6 decimals>
  Entropy = <value rounded to 6 decimals>
Call main() under `if __name__ == "__main__":`.
```

### Expected key output substrings

- `Purity = 1.000000`
- `Entropy = 0.000000`

### Reference solution

```python
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix
import numpy as np

def main():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    rho = DensityMatrix(qc)
    mat = rho.data
    purity = float(np.real(np.trace(mat @ mat)))
    eigvals = np.linalg.eigvalsh(mat)
    eigvals = np.clip(eigvals, 0, None)
    entropy = float(-np.sum(eigvals * np.log2(eigvals + 1e-30)))
    print(f"Purity = {purity:.6f}")
    print(f"Entropy = {entropy:.6f}")

if __name__ == "__main__":
    main()
```

### Candidate — `glm5.2`

**Status:** `PASS` (0.4s)

```python
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix

def main():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    
    rho = DensityMatrix(qc)
    data = rho.data
    
    purity = float(np.trace(data @ data).real)
    
    eigvals = np.linalg.eigvalsh(data)
    eigvals = np.maximum(eigvals, 0.0)
    mask = eigvals > 1e-12
    entropy = float(-np.sum(eigvals[mask] * np.log2(eigvals[mask])))
    
    print(f"Purity = {purity:.6f}")
    print(f"Entropy = {entropy:.6f}")

if __name__ == "__main__":
    main()
```

### Candidate — `deepseek-v4-pro`

**Status:** `PASS` (0.3s)

```python
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix
import numpy as np

def main():
    # 1. Build Bell state |Phi+>
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    
    # 2. Compute density matrix
    rho = DensityMatrix.from_instruction(qc)
    
    # 3. Compute purity Tr(rho^2)
    purity = np.real(np.trace(rho.data @ rho.data))
    
    # Compute von-Neumann entropy S(rho) = -Tr(rho log2 rho)
    eigenvalues = np.linalg.eigvalsh(rho.data)
    # Filter out zero eigenvalues to avoid log(0)
    nonzero_ev = eigenvalues[eigenvalues > 1e-12]
    entropy = -np.sum(nonzero_ev * np.log2(nonzero_ev))
    
    print(f"Purity = {purity:.6f}")
    print(f"Entropy = {entropy:.6f}")

if __name__ == "__main__":
    main()
```

### Candidate — `qwen3.6-27b-rag`

**Status:** `EXIT` (0.0s)

**Stderr:** `File "/Users/daxu/software/quantum-gpt/evals/runs/quantum-algo-20q-20260710/candidates/qwen3.6-27b-rag/quantum_density_matrix_pure_state.py", line 2 |     <html lang="zh-CN"> |     ^ | SyntaxError: invalid syntax |`

```
# generation error: HTTP 503: <!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 - 页面未找到 | 焕新</title>
    <style>
```

## 11. Partial trace of a bipartite pure state (`quantum_partial_trace_bipartite`)

### Prompt

```
Write a complete, runnable Python program using Qiskit that:
1. Builds a 3-qubit GHZ state |000> + |111> (apply H on q0, then CX q0->q1, CX q1->q2).
2. Uses qiskit.quantum_info.DensityMatrix and partial_trace over qubits [1, 2] to get the reduced density matrix rho_A on qubit 0.
3. In `def main()`, prints the 2x2 reduced density matrix (real parts, 4 decimals) and its purity Tr(rho_A^2).
Output exactly:
  Reduced density matrix:
    [[<a>, <b>], [<c>, <d>]]
  Purity = <value rounded to 6 decimals>
Call main() under `if __name__ == "__main__":`.
```

### Expected key output substrings

- `Reduced density matrix:`
- `Purity = 0.500000`

### Reference solution

```python
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix, partial_trace
import numpy as np

def main():
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    rho = DensityMatrix(qc)
    rho_A = partial_trace(rho, [1, 2])
    m = rho_A.data
    a = float(np.real(m[0, 0]))
    b = float(np.real(m[0, 1]))
    c = float(np.real(m[1, 0]))
    d = float(np.real(m[1, 1]))
    purity = float(np.real(np.trace(m @ m)))
    print("Reduced density matrix:")
    print(f"  [[{a:.4f}, {b:.4f}], [{c:.4f}, {d:.4f}]]")
    print(f"Purity = {purity:.6f}")

if __name__ == "__main__":
    main()
```

### Candidate — `glm5.2`

**Status:** `EXIT` (0.0s)

**Stderr:** `File "/Users/daxu/software/quantum-gpt/evals/runs/quantum-algo-20q-20260710/candidates/glm5.2/quantum_partial_trace_bipartite.py", line 1 |     Output exactly: |            ^ | SyntaxError: invalid syntax |`

```python
Output exactly:
  Reduced density matrix:
    [[<a>, <b>], [<c>, <d>]]
  Purity = <value rounded to 6 decimals>
```

### Candidate — `deepseek-v4-pro`

**Status:** `EXIT` (0.3s)

**Stderr:** `/Users/daxu/software/quantum-gpt/evals/runs/quantum-algo-20q-20260710/candidates/deepseek-v4-pro/quantum_partial_trace_bipartite.py:1: DeprecationWarning: Using Qiskit with Python 3.9 is deprecated as of the 2.1.0 release. Support for running Qiskit with Python 3.9 will be removed in the 2.3.0 relea`

```python
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix, partial_trace
import numpy as np

def main():
    # Build 3-qubit GHZ state
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    
    # Get density matrix of the full state
    rho = DensityMatrix.from_instruction(qc)
    
    # Partial trace over qubits [1, 2] to get reduced density matrix on qubit 0
    rho_A = partial_trace(rho, [1, 2])
    
    # Convert to numpy array
    rho_A_array = rho_A.data
    
    # Extract real parts and round to 4 decimals
    a = round(rho_A_array[0, 0].real, 4)
    b = round(rho_A_array[0, 1].real, 4)
    c = round(rho_A_array[1, 0].real, 4)
    d = round(rho_A_array[1, 1].real, 4)
    
    # Compute purity = Tr(rho_A^2)
    rho_A_sq = rho_A @ rho_A
    purity = np.trace(rho_A_sq.data).real
    purity_rounded = round(purity, 6)
    
    print("Reduced density matrix:")
    print(f"  [[{a}, {b}], [{c}, {d}]]")
    print(f"Purity = {purity_rounded}")

if __name__ == "__main__":
    main()
```

### Candidate — `qwen3.6-27b-rag`

**Status:** `EXIT` (0.0s)

**Stderr:** `File "/Users/daxu/software/quantum-gpt/evals/runs/quantum-algo-20q-20260710/candidates/qwen3.6-27b-rag/quantum_partial_trace_bipartite.py", line 2 |     <html lang="zh-CN"> |     ^ | SyntaxError: invalid syntax |`

```
# generation error: HTTP 503: <!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 - 页面未找到 | 焕新</title>
    <style>
```

## 12. <X> expectation value for |+> (`quantum_pauli_expectation_x`)

### Prompt

```
Write a complete, runnable Python program using Qiskit that:
1. Prepares |+> = H|0> on 1 qubit.
2. Uses qiskit.primitives.StatevectorEstimator to compute <psi|X|psi>.
3. In `def main()`, prints the expectation value rounded to 6 decimals.
Output exactly:
  <X> = <value>
Call main() under `if __name__ == "__main__":`.
```

### Expected key output substrings

- `<X> = 1.000000`

### Reference solution

```python
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator

def main():
    qc = QuantumCircuit(1)
    qc.h(0)
    est = StatevectorEstimator()
    obs = SparsePauliOp.from_list([("X", 1.0)])
    result = est.run([(qc, obs)]).result()
    val = float(result[0].data.evs.item())
    print(f"<X> = {val:.6f}")

if __name__ == "__main__":
    main()
```

### Candidate — `glm5.2`

**Status:** `EXIT` (0.3s)

**Stderr:** `/Users/daxu/software/quantum-gpt/evals/runs/quantum-algo-20q-20260710/candidates/glm5.2/quantum_pauli_expectation_x.py:1: DeprecationWarning: Using Qiskit with Python 3.9 is deprecated as of the 2.1.0 release. Support for running Qiskit with Python 3.9 will be removed in the 2.3.0 release, which coi`

```python
from qiskit.primitives import StatevectorEstimator
from qiskit.circuit.library import RealAmplitudes
from qiskit.quantum_info import SparsePauliOp

qc = QuantumCircuit(2)
...
estimator = StatevectorEstimator()
observables = SparsePauliOp.from_list([("II", 1), ("IZ", 2), ...])
job = estimator.run([(qc, observables)])
result = job.result()
print(result[0].data.evs)
```

### Candidate — `deepseek-v4-pro`

**Status:** `EXIT` (0.3s)

**Stderr:** `/Users/daxu/software/quantum-gpt/evals/runs/quantum-algo-20q-20260710/candidates/deepseek-v4-pro/quantum_pauli_expectation_x.py:1: DeprecationWarning: Using Qiskit with Python 3.9 is deprecated as of the 2.1.0 release. Support for running Qiskit with Python 3.9 will be removed in the 2.3.0 release, `

```python
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator
import numpy as np

def main():
    # 1. Prepare |+> = H|0> on 1 qubit
    qc = QuantumCircuit(1)
    qc.h(0)
    
    # 2. Use StatevectorEstimator to compute <psi|X|psi>
    estimator = StatevectorEstimator()
    job = estimator.run([(qc, "X", [0])])
    result = job.result()
    exp_val = result[0].data.evs
    
    # 3. Print expectation value rounded to 6 decimals
    print(f"<X> = {exp_val:.6f}")

if __name__ == "__main__":
    main()
```

### Candidate — `qwen3.6-27b-rag`

**Status:** `EXIT` (0.0s)

**Stderr:** `File "/Users/daxu/software/quantum-gpt/evals/runs/quantum-algo-20q-20260710/candidates/qwen3.6-27b-rag/quantum_pauli_expectation_x.py", line 2 |     <html lang="zh-CN"> |     ^ | SyntaxError: invalid syntax |`

```
# generation error: HTTP 503: <!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 - 页面未找到 | 焕新</title>
    <style>
```

## 13. Transverse-field Ising ground energy on 2 qubits (`quantum_ising_ground_state_energy`)

### Prompt

```
Write a complete, runnable Python program using numpy that:
1. Constructs the Hamiltonian H = -Z (x) Z - 0.5*(X (x) I + I (x) X) for 2 qubits (where (x) is the Kronecker product).
2. Computes the ground-state energy E0 = min(eigenvalues of H) using numpy.linalg.eigvalsh.
3. In `def main()`, prints E0 rounded to 6 decimals.
Output exactly:
  Ground state energy = <value>
Call main() under `if __name__ == "__main__":`.
```

### Expected key output substrings

- `Ground state energy = -1.414214`

### Reference solution

```python
import numpy as np

def main():
    I = np.array([[1, 0], [0, 1]], dtype=complex)
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Z = np.array([[1, 0], [0, -1]], dtype=complex)
    H = -np.kron(Z, Z) - 0.5 * (np.kron(X, I) + np.kron(I, X))
    E0 = float(np.min(np.linalg.eigvalsh(H)))
    print(f"Ground state energy = {E0:.6f}")

if __name__ == "__main__":
    main()
```

### Candidate — `glm5.2`

**Status:** `PASS` (0.1s)

```python
import numpy as np

def build_hamiltonian():
    Z = np.array([[1, 0], [0, -1]], dtype=float)
    X = np.array([[0, 1], [1, 0]], dtype=float)
    I = np.eye(2, dtype=float)
    return -np.kron(Z, Z) - 0.5 * (np.kron(X, I) + np.kron(I, X))

def main():
    H = build_hamiltonian()
    E0 = np.min(np.linalg.eigvalsh(H))
    print(f"Ground state energy = {E0:.6f}")

if __name__ == "__main__":
    main()
```

### Candidate — `deepseek-v4-pro`

**Status:** `PASS` (0.1s)

```python
import numpy as np

def main():
    # Pauli matrices
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Z = np.array([[1, 0], [0, -1]], dtype=complex)
    I = np.eye(2, dtype=complex)

    # Kronecker products
    Z_Z = np.kron(Z, Z)
    X_I = np.kron(X, I)
    I_X = np.kron(I, X)

    # Hamiltonian
    H = -Z_Z - 0.5 * (X_I + I_X)

    # Ground-state energy
    eigenvalues = np.linalg.eigvalsh(H)
    E0 = np.min(eigenvalues).real

    print(f"  Ground state energy = {E0:.6f}")

if __name__ == "__main__":
    main()
```

### Candidate — `qwen3.6-27b-rag`

**Status:** `MISSING` (0.0s)

**Missing substrings:** ['Ground state energy = -1.414214']

```
# generation error: HTTP 503: no healthy upstream
```

## 14. VQE on H2 (2-qubit) with 2-layer Ry ansatz + COBYLA (`quantum_vqe_h2_energy`)

### Prompt

```
Write a complete, runnable Python program using Qiskit + qiskit_algorithms that:
1. Defines the 2-qubit H2 Hamiltonian: H = -1.052373*II + 0.397937*ZI - 0.397937*IZ - 0.011280*ZZ + 0.180931*XX (Pauli strings read left-to-right as qubit-1, qubit-0).
2. Uses VQE from qiskit_algorithms.minimum_eigensolvers with StatevectorEstimator, a 2-layer Ry+CX ansatz on 2 qubits (6 parameters), and COBYLA(maxiter=400).
3. In `def main()`, prints the VQE optimum energy rounded to 4 decimals.
Output exactly:
  VQE energy = <value>
Call main() under `if __name__ == "__main__":`.
```

### Expected key output substrings

- `VQE energy = -1.85`

### Reference solution

```python
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator
from qiskit_algorithms.minimum_eigensolvers import VQE
from qiskit_algorithms.optimizers import COBYLA

def main():
    H = SparsePauliOp.from_list([
        ("II", -1.052373),
        ("ZI", 0.397937),
        ("IZ", -0.397937),
        ("ZZ", -0.011280),
        ("XX", 0.180931),
    ])
    p = ParameterVector("p", 6)
    ansatz = QuantumCircuit(2)
    ansatz.ry(p[0], 0); ansatz.ry(p[1], 1)
    ansatz.cx(0, 1)
    ansatz.ry(p[2], 0); ansatz.ry(p[3], 1)
    ansatz.cx(0, 1)
    ansatz.ry(p[4], 0); ansatz.ry(p[5], 1)
    estimator = StatevectorEstimator()
    vqe = VQE(estimator=estimator, ansatz=ansatz, optimizer=COBYLA(maxiter=400))
    result = vqe.compute_minimum_eigenvalue(H)
    print(f"VQE energy = {result.eigenvalue:.4f}")

if __name__ == "__main__":
    main()
```

### Candidate — `glm5.2`

**Status:** `EXIT` (1.3s)

**Stderr:** `Traceback (most recent call last): |   File "/Users/daxu/software/quantum-gpt/evals/runs/quantum-algo-20q-20260710/candidates/glm5.2/quantum_vqe_h2_energy.py", line 4, in <module> |     from qiskit.primitives import Estimator | ImportError: cannot import name 'Estimator' from 'qiskit.primitives' (/U`

```python
from qiskit_algorithms import VQE
from qiskit_algorithms.optimizers import COBYLA
from qiskit.circuit.library import TwoLocal
from qiskit.primitives import Estimator

estimator = Estimator()
ansatz = TwoLocal(...)
optimizer = COBYLA()
vqe = VQE(estimator, ansatz, optimizer)
result = vqe.compute_minimum_eigenvalue(operator)
```

### Candidate — `deepseek-v4-pro`

**Status:** `PASS` (0.9s)

```python
from qiskit.quantum_info import SparsePauliOp
from qiskit.circuit.library import TwoLocal
from qiskit_algorithms.minimum_eigensolvers import VQE
from qiskit_algorithms.optimizers import COBYLA
from qiskit.primitives import StatevectorEstimator
import numpy as np

def main():
    # 1. Define the 2-qubit H2 Hamiltonian
    hamiltonian = SparsePauliOp.from_list([
        ("II", -1.052373),
        ("ZI",  0.397937),
        ("IZ", -0.397937),
        ("ZZ", -0.011280),
        ("XX",  0.180931)
    ])

    # 2. Ansatz: 2-layer Ry+CX (6 parameters)
    ansatz = TwoLocal(2, "ry", "cx", reps=2, entanglement="linear")

    # 3. VQE with StatevectorEstimator and COBYLA
    estimator = StatevectorEstimator()
    optimizer = COBYLA(maxiter=400)
    vqe = VQE(estimator, ansatz, optimizer)
    result = vqe.compute_minimum_eigenvalue(hamiltonian)

    # Print result rounded to 4 decimals
    energy = round(result.eigenvalue.real, 4)
    print(f"VQE energy = {energy}")

if __name__ == "__main__":
    main()
```

### Candidate — `qwen3.6-27b-rag`

**Status:** `MISSING` (0.0s)

**Missing substrings:** ['VQE energy = -1.85']

```
# generation error: HTTP 503: no healthy upstream
```

## 15. Grover 3-qubit finds |101> (`quantum_grover_3qubit_marked101`)

### Prompt

```
Write a complete, runnable Python program using Qiskit that:
1. Implements Grover's algorithm on 3 qubits to find the marked state |101>.
2. Uses 2 Grover iterations. Oracle: X on q1 (the bit that is 0 in |101>), then CCZ on all 3 qubits (implemented as H on q2, MCX with controls [q0, q1] targeting q2, H on q2), then X on q1 to uncompute.
   Diffusion: H on all, X on all, CCZ on all (same construction), X on all, H on all.
3. In `def main()`, uses StatevectorSampler (1000 shots) and prints the most-likely bitstring and its probability.
Output exactly:
  Most likely: <3-char bitstring>
  Probability: <value rounded to 3 decimals>
Call main() under `if __name__ == "__main__":`.
```

### Expected key output substrings

- `Most likely: 101`
- `Probability: 0.`

### Reference solution

```python
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

def ccz(qc: QuantumCircuit):
    qc.h(2)
    qc.mcx([0, 1], 2)
    qc.h(2)

def main():
    n = 3
    qc = QuantumCircuit(n)
    qc.h(range(n))
    for _ in range(2):
        # Oracle for |101>: q0=1, q1=0, q2=1
        qc.x(1)
        ccz(qc)
        qc.x(1)
        # Diffusion
        qc.h(range(n))
        qc.x(range(n))
        ccz(qc)
        qc.x(range(n))
        qc.h(range(n))
    qc.measure_all()
    sampler = StatevectorSampler()
    counts = sampler.run([qc], shots=1000).result()[0].data.meas.get_counts()
    top_bs, top_n = max(counts.items(), key=lambda kv: kv[1])
    total = sum(counts.values())
    print(f"Most likely: {top_bs}")
    print(f"Probability: {top_n/total:.3f}")

if __name__ == "__main__":
    main()
```

### Candidate — `glm5.2`

**Status:** `EXIT` (0.0s)

**Stderr:** `File "/Users/daxu/software/quantum-gpt/evals/runs/quantum-algo-20q-20260710/candidates/glm5.2/quantum_grover_3qubit_marked101.py", line 9 |     Actually in V2, the result contains PubResult objects. result[0].data.<register>.get_counts(). If the circuit has a classical register named "meas", then re`

```python
from qiskit import QuantumCircuit, transpile
from qiskit.primitives import StatevectorSampler

sampler = StatevectorSampler()
job = sampler.run(qc, shots=1000)
result = job.result()
counts = result[0].data.meas.get_counts()

Actually in V2, the result contains PubResult objects. result[0].data.<register>.get_counts(). If the circuit has a classical register named "meas", then result[0].data.meas.get_counts(). If no name, maybe result[0].data.cr.get_counts()? Let's inspect memory.

Example from Qiskit docs for SamplerV2:

from qiskit.primitives import StatevectorSampler
from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0,1)
qc.measure_all()
sampler = StatevectorSampler()
job = sampler.run([qc], shots=1000)
result = job.result()
counts = result[0].data.meas.get_counts()
print(counts)

Actually measure_all() adds a classical register named "meas". So result[0].data.meas.get_counts() works.

But maybe result[0].data["meas"].get_counts(). Let's check. In V2, PubResult.data is a DataBin object. You can access by attribute: data.meas.get_counts(). Or data["meas"].get_counts(). Both should work.

We can use measure_all() and then get counts via result[0].data.meas.get_counts().

Alternatively, if we use QuantumCircuit(3,3) and measure(q, c), the classical register default name is "c"? In QuantumCircuit(3,3), classical register name is "c" maybe? Actually QuantumCircuit(3,3) creates ClassicalRegister(3, 'c'). Then result[0].data.c.get_counts(). But to be safe, use measure_all() and attribute 'meas'.

Need to print most likely bitstring and probability. The counts are bitstrings with keys like '101'. Need to find max count, probability = max_count/1000 rounded to 3 decimals.

But note: Qiskit bitstrings are printed with the classical bits in order of the classical register. If we measure qubits [0,1,2] into classical bits [0,1,2] using measure_all(), the bitstring order: Qiskit uses little-endian? Let's recall. In Qiskit, the statevector order is little-endian: qubit 0 is the least significant bit (rightmost) in the bitstring. When measuring, counts keys are bitstrings where the leftmost bit corresponds to classical bit with highest index? Actually standard: counts string is ordered as c_{n-1}...c_0, where c_0 is the least significant bit (from qubit 0). So if we measure qubit 0 to classical bit 0, the bitstring's rightmost char is qubit 0. For state |101> in Dirac notation |q2 q1 q0>? Wait, in Qiskit, |101> usually means qubit 2 is 1, qubit 1 is 0, qubit 0 is 1? Let's be careful.

The problem says "find the marked state |101>" and oracle: X on q1 (the bit that is 0 in |101>). So in |101>, the middle bit (q1) is 0. That suggests the bitstring is ordered as q2 q1 q0? Actually |101> written as three bits: first bit is q0? In many textbooks, |101> means qubit 0 = 1, qubit 1 = 0, qubit 2 = 1, with q0 leftmost? Wait, standard Dirac notation for multi-qubit states: |b_{n-1} ... b_0> where b_0 is the state of qubit 0? In Qiskit, the label |101> corresponds to qubit 2=1, qubit 1=0, qubit 0=1 because Qiskit uses little-endian indexing. But the prompt says "X on q1 (the bit that is 0 in |101>)". If |101> bits are read left-to-right as q0 q1 q2? Then q0=1, q1=0, q2=1. So q1 is indeed the bit that is 0. That suggests they are using the convention that the bitstring's leftmost char is q0, next is q1, rightmost is q2. But Qiskit's counts may output in the opposite order. Need to be careful to get the printed most-likely bitstring correct.

The oracle description: "X on q1 (the bit that is 0 in |101>), then CCZ on all 3 qubits (implemented as H on q2, MCX with controls [q0, q1] targeting q2, H on q2), then X on q1 to uncompute."

This oracle marks state |101>. Let's analyze. The oracle should flip phase of |101>. They propose: X on q1 (so |101> becomes |111>), then CCZ on all 3 qubits flips phase of |111>, then X on q1 uncomputes. So indeed the marked state is the one where after X on q1, all qubits are 1. That means original state has q0=1, q1=0, q2=1. So the bitstring |101> corresponds to q0=1, q1=0, q2=1 (left-to-right = q0 q1 q2). This is the textbook convention (qubit 0 is leftmost). Qiskit's internal statevector ordering is little-endian, but the circuit drawing and gate labels use q0 as the top wire. The counts bitstrings from Qiskit are typically printed with the most significant bit corresponding to the highest-index classical bit, which is often q2 if measuring q0->c0, q1->c1, q2->c2. Let's verify.

In Qiskit, if you do:

qc = QuantumCircuit(3)
qc.x(0)
qc.x(2)
qc.measure_all()
sampler.run...
counts: {'101': 1000}? Or {'110': 1000}? Let's recall from experience. If you initialize a state with x on q0 and x on q2, the statevector is |101> in Qiskit's convention? Actually the statevector index for q0=1, q1=0, q2=1 is binary 101 (q2 q1 q0 = 1 0 1) = decimal 5. The counts key for that state should be '101' because Qiskit prints the bitstring as the binary representation with qubit 0 as the least significant bit (rightmost). So counts key '101' corresponds to q2=1, q1=0, q0=1. That matches the state where q0=1, q1=0, q2=1. So the counts key '101' is exactly what we want, even though it's displayed as q2 q1 q0. Wait, the string '101' has leftmost char = q2, middle = q1, rightmost = q0. But the marked state |101> in the problem has q0=1, q1=0, q2=1. In Qiskit's counts, that is also '101' because q2=1, q1=0, q0=1. So the string is the same! The only difference is interpretation of which char corresponds to which qubit, but the string '101' is identical. So if the algorithm works, the most likely bitstring in counts should be '101'. Good.

But let's double-check. If we apply X on q1 (the middle qubit) in the oracle, that is X(1). The CCZ on all 3 qubits implemented as H on q2, MCX controls [q0,q1] target q2. This is a standard decomposition of CCZ with q2 as target. It flips phase of |111>. After X on q1, the state |101> (q0=1,q1=0,q2=1) becomes |111>. So oracle marks it. Good.

Now diffusion: H on all, X on all, CCZ on all (same construction), X on all, H on all. That's the standard Grover diffusion operator using CCZ. It should work.

We need 2 Grover iterations. For 3 qubits, optimal number is about pi/4 * sqrt(N/M) = pi/4 * sqrt(8) ≈ 2.22. So 2 iterations is fine. The marked state should have high probability. Let's compute expected probability after 2 iterations. For M=1, N=8, after k iterations amplitude ~ sin((2k+1)θ), where sin θ = sqrt(M/N)=1/sqrt(8). θ = arcsin(0.35355)=0.361367 rad. After k=2: (5θ)=1.8068 rad, sin=0.972. So probability ~0.945? Actually amplitude = sin(5θ) ≈ sin(1.8068) ≈ 0.972. Probability ~0.945. With 1000 shots, probability printed should be around 0.945. But due to StatevectorSampler (ideal) with 1000 shots, counts will be random; probability could be e.g., 0.95. But they might want deterministic? StatevectorSampler with shots returns random samples. The most likely should be '101' with high probability. The exact rounded probability will vary per run. The prompt says "prints the most-likely bitstring and its probability." So it's okay to be stochastic. But maybe they expect the exact probability from statevector? Wait, they explicitly say StatevectorSampler (1000 shots). So it's sampling. The output will vary. But the problem likely checks that the program is correct, not the exact output. However, they say "Output exactly: Most likely: ... Probability: ...". In an evaluation, they might run the program and compare output? If it's random, they can't compare exact probability. Maybe they just check format. Or maybe they expect to use the sampler's result and compute probability as count/1000, which will be random but close. Alternatively, maybe they expect to use StatevectorSampler to get quasi-probabilities? Let's think.

StatevectorSampler in Qiskit can also return counts. It samples. With 1000 shots, the most likely bitstring will almost certainly be '101'. Probability will be around 0.94. Rounding to 3 decimals will vary. The evaluation might not require exact probability. But the instruction "Output exactly:" might be a template. We'll follow it.

Need to ensure we import correct modules. Qiskit version might be 1.0+. Let's write code that works with Qiskit 1.0.

Potential issues:
- MCX gate: In Qiskit, we can use qc.mcx([0,1], 2) or qc.ccx(0,1,2) since it's 2 controls. The prompt says MCX with controls [q0, q1] targeting q2. So use qc.mcx([0,1], 2).
- CCZ implementation: H on q2, MCX controls [0,1] target 2, H on q2.
- Grover iterations: 2 times.
- Diffusion: H on all, X on all, CCZ on all, X on all, H on all. The CCZ same construction: H on q2, MCX [0,1] target 2, H on q2. Note: After H on all and X on all, the diffusion operator should be a reflection about |s>. The standard diffusion is H^n (2|0><0| - I) H^n. And (2|0><0| - I) is implemented as X^n (2|1><1| - I) X^n? Actually the standard is: apply X to all, then multi-controlled Z (which flips phase of |11...1>), then X to all. Then H. So yes, the described diffusion is correct.
- Need to apply H to all at start of Grover to create uniform superposition. The prompt doesn't explicitly mention initial H, but Grover's algorithm requires it. The description of diffusion includes H on all, but we need initial Hadamards. Should we include them? The problem says "Implements Grover's algorithm... Uses 2 Grover iterations." Grover's algorithm includes initial Hadamard on all qubits. We must include it. The diffusion operator also starts and ends with H. So the circuit is: H on all; [oracle; diffusion] repeated 2 times; measure.

Let's verify the oracle and diffusion with initial H.

Circuit:
q = QuantumRegister(3)
qc = QuantumCircuit(q)
qc.h([0,1,2])
for _ in range(2):
    # Oracle
    qc.x(1)
    # CCZ
    qc.h(2)
    qc.mcx([0,1], 2)
    qc.h(2)
    qc.x(1)
    # Diffusion
    qc.h([0,1,2])
    qc.x([0,1,2])
    # CCZ
    qc.h(2)
    qc.mcx([0,1], 2)
    qc.h(2)
    qc.x([0,1,2])
    qc.h([0,1,2])
qc.measure_all()

Wait, the diffusion: "H on all, X on all, CCZ on all (same construction), X on all, H on all." The CCZ on all is the same as oracle's CCZ. So yes.

But note: In the diffusion, the CCZ is on all 3 qubits. The construction uses H on q2, MCX controls [q0,q1] target q2. That's a CCZ with q2 as target. It works.

Now, after 2 iterations, measure.

Let's test mentally if the circuit indeed amplifies |101>. We can simulate the statevector to ensure. Let's do a quick analytical or semi-analytical check.

Initial state: |s> = (1/√8) Σ_x |x>.
Oracle: flips phase of |101> (q0=1,q1=0,q2=1). In Qiskit's ordering, that's basis index 5 (binary 101). So after oracle: |ψ1> = |s> - 2/√8 |101>.
Diffusion: reflects about |s>. After one iteration, amplitude of |101> increases.

After 2 iterations, should be high.

But there is a subtlety: The oracle uses X on q1. In Qiskit, q1 is the middle qubit. The marked state |101> in Qiskit counts is index 5 (binary 101 where q2 is MSB). The q1 bit is 0. So X on q1 flips it to 1. The state becomes |111> (index 7). CCZ flips phase of |111>. Then X on q1 returns to |101>. So oracle marks index 5. Good.

The diffusion operator: H, X, CCZ, X, H. The CCZ flips phase of |111>. After X on all, the state |000> becomes |111>. So the operator (X⊗X⊗X) CCZ (X⊗X⊗X) = CZ? Actually it implements -I on |000> and identity on others? Let's see: CCZ flips phase of |111>. X on all maps |000>↔|111>. So the combined operator is a diagonal phase flip on |000> (since |000> -> X -> |111> -> CCZ flips -> |111> -> X -> |000> with phase -1). For any other state, it's not all ones after X, so no phase flip. So the operator is 2|000><000| - I (phase flip on |000>). Then H on both sides gives the diffusion operator. So it's correct.

Now, the code. Need to be careful with imports for State
```

### Candidate — `deepseek-v4-pro`

**Status:** `PASS` (0.4s)

```python
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector
import numpy as np

def grover_3qubit():
    qc = QuantumCircuit(3)
    # Initialize superposition
    qc.h([0, 1, 2])
    
    # Oracle for |101>
    qc.x(1)  # flip q1 because it's 0 in |101>
    qc.h(2)
    qc.mcx([0, 1], 2)  # multi-controlled X with controls q0,q1 target q2
    qc.h(2)
    qc.x(1)  # uncompute
    
    # Diffusion operator
    qc.h([0, 1, 2])
    qc.x([0, 1, 2])
    qc.h(2)
    qc.mcx([0, 1], 2)
    qc.h(2)
    qc.x([0, 1, 2])
    qc.h([0, 1, 2])
    
    # Second iteration
    # Oracle
    qc.x(1)
    qc.h(2)
    qc.mcx([0, 1], 2)
    qc.h(2)
    qc.x(1)
    
    # Diffusion
    qc.h([0, 1, 2])
    qc.x([0, 1, 2])
    qc.h(2)
    qc.mcx([0, 1], 2)
    qc.h(2)
    qc.x([0, 1, 2])
    qc.h([0, 1, 2])
    
    qc.measure_all()
    return qc

def main():
    qc = grover_3qubit()
    simulator = AerSimulator(method='statevector')
    result = simulator.run(qc, shots=1000).result()
    counts = result.get_counts()
    most_likely = max(counts, key=counts.get)
    prob = counts[most_likely] / 1000
    print(f"Most likely: {most_likely}")
    print(f"Probability: {prob:.3f}")

if __name__ == "__main__":
    main()
```

### Candidate — `qwen3.6-27b-rag`

**Status:** `EXIT` (0.0s)

**Stderr:** `File "/Users/daxu/software/quantum-gpt/evals/runs/quantum-algo-20q-20260710/candidates/qwen3.6-27b-rag/quantum_grover_3qubit_marked101.py", line 2 |     <html lang="zh-CN"> |     ^ | SyntaxError: invalid syntax |`

```
# generation error: HTTP 503: <!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 - 页面未找到 | 焕新</title>
    <style>
```

## 16. QPE estimates phase 1/4 for unitary S (`quantum_phase_estimation_pi4`)

### Prompt

```
Write a complete, runnable Python program using Qiskit that:
1. Implements Quantum Phase Estimation with 3 counting qubits to estimate the phase of the unitary U = S (phase gate, eigenvalue e^{i*pi/2}, phase = 1/4).
2. Uses eigenstate |1> on the target qubit (qubit 3).
3. Apply H to counting qubits 0,1,2; apply controlled-U^(2^k): cp(pi/2, q0, tgt), cp(pi, q1, tgt), (q2 needs S^4 = I, so no gate); then inverse QFT on the 3 counting qubits.
4. In `def main()`, uses StatevectorSampler (2000 shots) and prints the most-likely 3-bit measurement (Qiskit little-endian: leftmost char is q2) and the estimated phase = int(measurement) / 2^3.
Output exactly:
  Measurement: <3-bit string>
  Estimated phase: <float rounded to 4 decimals>
Call main() under `if __name__ == "__main__":`.
```

### Expected key output substrings

- `Measurement: `
- `Estimated phase: 0.2500`

### Reference solution

```python
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
import math

def main():
    n_count = 3
    tgt = n_count
    qc = QuantumCircuit(n_count + 1, n_count)
    qc.x(tgt)
    qc.h(range(n_count))
    qc.cp(math.pi/2, 0, tgt)  # CS
    qc.cp(math.pi, 1, tgt)    # CZ = S^2
    # 2^2 = S^4 = I: no gate
    # Inverse QFT on counting register
    qc.swap(0, 2)
    qc.h(0)
    qc.cp(-math.pi/2, 0, 1)
    qc.h(1)
    qc.cp(-math.pi/4, 0, 2)
    qc.cp(-math.pi/2, 1, 2)
    qc.h(2)
    qc.measure(range(n_count), range(n_count))
    sampler = StatevectorSampler()
    counts = sampler.run([qc], shots=2000).result()[0].data.c.get_counts()
    top = max(counts.items(), key=lambda kv: kv[1])[0]
    val = int(top, 2)
    phase = val / (2 ** n_count)
    print(f"Measurement: {top}")
    print(f"Estimated phase: {phase:.4f}")

if __name__ == "__main__":
    main()
```

### Candidate — `glm5.2`

**Status:** `MISSING` (0.3s)

**Missing substrings:** ['Estimated phase: 0.2500']

```python
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

def qft_inverse(qc, qubits):
    """Apply inverse QFT on the given qubits."""
    n = len(qubits)
    # Swap qubits
    for i in range(n // 2):
        qc.swap(qubits[i], qubits[n - 1 - i])
    # Inverse QFT
    for j in range(n):
        for k in range(j):
            qc.cp(-np.pi / (2 ** (j - k)), qubits[j], qubits[k])
        qc.h(qubits[j])

def main():
    # Create circuit with 4 qubits: 3 counting + 1 target
    qc = QuantumCircuit(4, 3)
    
    # Prepare eigenstate |1> on target qubit (qubit 3)
    qc.x(3)
    
    # Apply H to counting qubits
    qc.h(0)
    qc.h(1)
    qc.h(2)
    
    # Apply controlled-U^(2^k)
    # q0: controlled-S (S^1), phase = pi/2
    qc.cp(np.pi / 2, 0, 3)
    # q1: controlled-S^2 = controlled-Z, phase = pi
    qc.cp(np.pi, 1, 3)
    # q2: controlled-S^4 = controlled-I, no gate needed
    
    # Inverse QFT on counting qubits
    qft_inverse(qc, [0, 1, 2])
    
    # Measure counting qubits
    qc.measure([0, 1, 2], [0, 1, 2])
    
    # Run with StatevectorSampler
    sampler = StatevectorSampler()
    result = sampler.run([qc], shots=2000).result()
    
    # Get counts
    counts = result[0].data.c.get_counts()
    
    # Find most likely measurement
    most_likely = max(counts, key=counts.get)
    
    # Calculate estimated phase
    # In Qiskit, the bitstring is little-endian: leftmost char is q2
    # The integer value is int(most_likely, 2) if we interpret it as q2 q1 q0
    measured_int = int(most_likely, 2)
    estimated_phase = measured_int / (2 ** 3)
    
    print(f"Measurement: {most_likely}")
    print(f"Estimated phase: {round(estimated_phase, 4)}")

if __name__ == "__main__":
    import numpy as np
    main()
```

### Candidate — `deepseek-v4-pro`

**Status:** `MISSING` (0.3s)

**Missing substrings:** ['Estimated phase: 0.2500']

```python
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
import numpy as np

def main():
    # Create circuit with 3 counting qubits + 1 target qubit
    n_count = 3
    qc = QuantumCircuit(n_count + 1)
    
    # Prepare target qubit in eigenstate |1>
    qc.x(n_count)
    
    # Apply Hadamard to counting qubits
    for i in range(n_count):
        qc.h(i)
    
    # Apply controlled-U^(2^k) operations
    # U = S gate, eigenvalue e^{i*pi/2}, phase = 1/4
    # k=0: U^(2^0) = S, controlled-S = cp(pi/2)
    qc.cp(np.pi/2, 0, n_count)
    # k=1: U^(2^1) = S^2 = Z, controlled-Z = cp(pi)
    qc.cp(np.pi, 1, n_count)
    # k=2: U^(2^2) = S^4 = I, no gate needed
    
    # Inverse QFT on counting qubits
    # Swap qubits for standard QFT ordering
    qc.swap(0, 2)
    # Apply inverse QFT
    for j in range(n_count):
        qc.h(j)
        for k in range(j + 1, n_count):
            qc.cp(-np.pi / (2 ** (k - j)), k, j)
    
    # Measure counting qubits
    qc.measure_all()
    
    # Run with StatevectorSampler
    sampler = StatevectorSampler(seed=42)
    job = sampler.run([qc], shots=2000)
    result = job.result()[0]
    
    # Get counts
    counts = result.data.meas.get_counts()
    
    # Find most likely measurement
    most_likely = max(counts, key=counts.get)
    
    # Qiskit little-endian: leftmost char is q2
    # Convert to integer (binary string is q2 q1 q0)
    int_val = int(most_likely, 2)
    estimated_phase = int_val / (2 ** n_count)
    
    print(f"Measurement: {most_likely}")
    print(f"Estimated phase: {estimated_phase:.4f}")

if __name__ == "__main__":
    main()
```

### Candidate — `qwen3.6-27b-rag`

**Status:** `MISSING` (0.0s)

**Missing substrings:** ['Measurement: ', 'Estimated phase: 0.2500']

```
# generation error: HTTP 503: no healthy upstream
```

## 17. 3-qubit bit-flip code with X error on qubit 1 (`quantum_bit_flip_code_recovery`)

### Prompt

```
Write a complete, runnable Python program using Qiskit that:
1. Encodes |1> into the 3-qubit bit-flip code: |111> (apply X on each of the 3 data qubits q0, q1, q2).
2. Applies an X error on the middle qubit (qubit 1).
3. Performs syndrome measurement: parity c0 = q0 XOR q1 (CX q0->q3, CX q1->q3) and c1 = q1 XOR q2 (CX q1->q4, CX q2->q4).
4. Measures all 5 qubits (3 data + 2 syndrome).
5. In `def main()`, uses StatevectorSampler (1000 shots), decodes the 3 data qubits via majority vote, and prints P(majority = 1), which should be 1.0.
   Note: Qiskit measurement bitstring is in little-endian order (leftmost char = highest qubit index).
Output exactly:
  P(majority=1) = <value rounded to 3 decimals>
Call main() under `if __name__ == "__main__":`.
```

### Expected key output substrings

- `P(majority=1) = 1.000`

### Reference solution

```python
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

def main():
    qc = QuantumCircuit(5, 5)
    qc.x([0, 1, 2])
    qc.x(1)
    qc.cx(0, 3)
    qc.cx(1, 3)
    qc.cx(1, 4)
    qc.cx(2, 4)
    qc.measure(3, 0)
    qc.measure(4, 1)
    qc.measure(0, 2)
    qc.measure(1, 3)
    qc.measure(2, 4)
    sampler = StatevectorSampler()
    counts = sampler.run([qc], shots=1000).result()[0].data.c.get_counts()
    total = sum(counts.values())
    maj_one = 0
    for bs, c in counts.items():
        data_bits = [bs[4], bs[3], bs[2]]
        if sum(int(b) for b in data_bits) >= 2:
            maj_one += c
    print(f"P(majority=1) = {maj_one/total:.3f}")

if __name__ == "__main__":
    main()
```

### Candidate — `glm5.2`

**Status:** `MISSING` (0.3s)

**Missing substrings:** ['P(majority=1) = 1.000']

```python
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

def main():
    # Create a 5-qubit circuit (3 data + 2 syndrome)
    qc = QuantumCircuit(5, 5)
    
    # Step 1: Encode |1> into |111> by applying X on q0, q1, q2
    qc.x(0)
    qc.x(1)
    qc.x(2)
    
    # Step 2: Apply X error on middle qubit (q1)
    qc.x(1)
    
    # Step 3: Syndrome measurement
    # c0 = q0 XOR q1
    qc.cx(0, 3)
    qc.cx(1, 3)
    # c1 = q1 XOR q2
    qc.cx(1, 4)
    qc.cx(2, 4)
    
    # Step 4: Measure all 5 qubits
    qc.measure_all()
    
    # Wait, measure_all() adds classical bits. Let me use measure instead.
    # Actually, I already created the circuit with 5 classical bits.
    # Let me use qc.measure(range(5), range(5)) instead.
```

### Candidate — `deepseek-v4-pro`

**Status:** `PASS` (0.4s)

```python
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector
from qiskit_aer.primitives import Sampler
import numpy as np

def main():
    # Create quantum circuit with 5 qubits (3 data + 2 syndrome) and 5 classical bits
    qc = QuantumCircuit(5, 5)
    
    # Step 1: Encode |1> into |111> by applying X on each data qubit
    qc.x(0)
    qc.x(1)
    qc.x(2)
    
    # Step 2: Apply X error on middle qubit (qubit 1)
    qc.x(1)
    
    # Step 3: Syndrome measurement
    # c0 = q0 XOR q1: CX q0->q3, CX q1->q3
    qc.cx(0, 3)
    qc.cx(1, 3)
    # c1 = q1 XOR q2: CX q1->q4, CX q2->q4
    qc.cx(1, 4)
    qc.cx(2, 4)
    
    # Step 4: Measure all 5 qubits
    qc.measure([0, 1, 2, 3, 4], [0, 1, 2, 3, 4])
    
    # Step 5: Use StatevectorSampler (1000 shots)
    backend = AerSimulator()
    sampler = Sampler()
    job = sampler.run([qc], shots=1000)
    result = job.result()
    
    # Get counts from the quasi-probabilities
    counts = result.quasi_dists[0].binary_probabilities()
    
    # Decode data qubits via majority vote
    majority_one_count = 0
    total_shots = 0
    
    for bitstring, prob in counts.items():
        # bitstring is little-endian: leftmost char = highest qubit index (q4)
        # So bitstring[0] = q4, bitstring[1] = q3, bitstring[2] = q2, bitstring[3] = q1, bitstring[4] = q0
        # Extract data qubits: q0 = bitstring[4], q1 = bitstring[3], q2 = bitstring[2]
        q0_val = int(bitstring[4])
        q1_val = int(bitstring[3])
        q2_val = int(bitstring[2])
        
        # Majority vote
        sum_bits = q0_val + q1_val + q2_val
        majority = 1 if sum_bits >= 2 else 0
        
        # Convert probability to count (approximate)
        count = int(round(prob * 1000))
        total_shots += count
        if majority == 1:
            majority_one_count += count
    
    # Calculate probability
    prob_majority_one = majority_one_count / total_shots if total_shots > 0 else 0.0
    
    print(f"P(majority=1) = {prob_majority_one:.3f}")

if __name__ == "__main__":
    main()
```

### Candidate — `qwen3.6-27b-rag`

**Status:** `MISSING` (0.0s)

**Missing substrings:** ['P(majority=1) = 1.000']

```
# generation error: HTTP 503: no healthy upstream
```

## 18. Superdense coding sends 2 bits '11' via 1 qubit (`quantum_superdense_coding_11`)

### Prompt

```
Write a complete, runnable Python program using Qiskit that:
1. Creates a shared Bell pair |Phi+> between Alice (q0) and Bob (q1).
2. Alice encodes 2 bits "11" by applying Z then X to her qubit (q0).
3. Bob receives q0, applies CX q0->q1 then H q0, then measures both qubits.
4. In `def main()`, uses StatevectorSampler (1000 shots) and prints the most-likely 2-bit decoded message (natural order: c0 c1, so "11") and its probability.
Output exactly:
  Decoded bits: <2-char bitstring>
  Probability: <value rounded to 3 decimals>
Call main() under `if __name__ == "__main__":`.
```

### Expected key output substrings

- `Decoded bits: 11`
- `Probability: 1.000`

### Reference solution

```python
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

def main():
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.z(0)
    qc.x(0)
    qc.cx(0, 1)
    qc.h(0)
    qc.measure(0, 0)
    qc.measure(1, 1)
    sampler = StatevectorSampler()
    counts = sampler.run([qc], shots=1000).result()[0].data.c.get_counts()
    top_bs, top_n = max(counts.items(), key=lambda kv: kv[1])
    total = sum(counts.values())
    decoded = top_bs[::-1]
    print(f"Decoded bits: {decoded}")
    print(f"Probability: {top_n/total:.3f}")

if __name__ == "__main__":
    main()
```

### Candidate — `glm5.2`

**Status:** `EXIT` (0.0s)

**Stderr:** `File "/Users/daxu/software/quantum-gpt/evals/runs/quantum-algo-20q-20260710/candidates/glm5.2/quantum_superdense_coding_11.py", line 10 |     If we have a classical register named "meas" with 2 bits, then pub_result.data.meas.get_counts() returns a dict of bitstrings. Or if we have individual classi`

```python
from qiskit.primitives import StatevectorSampler

sampler = StatevectorSampler()
job = sampler.run([circuit], shots=1000)
result = job.result()
# result is PrimitiveResult
# result[0] is a PubResult
# pub_result.data.c0.get_counts() maybe? Actually for V2, measurements are stored in DataBin. The classical bits are accessed as attributes named after registers or bits.

If we have a classical register named "meas" with 2 bits, then pub_result.data.meas.get_counts() returns a dict of bitstrings. Or if we have individual classical bits? We need to know.

Let's recall Qiskit 1.0 V2 sampler result structure.

In Qiskit 1.0, when you add_measurements, the classical data is stored in a DataBin object. The result of sampler.run([qc], shots=1000).result() returns a PrimitiveResult with a list of PubResults. Each PubResult has .data (DataBin) and .metadata. The DataBin has attributes corresponding to the classical register names used in measure. If you used QuantumCircuit(2, 2) with a classical register automatically named "c", then data.c is a RegisterBitarray? Actually, in Qiskit 1.0, the classical bits are stored as a BitArray. You can call data.c.get_counts() to get counts. Or if you used classical register named "meas", data.meas.get_counts().

Alternatively, maybe StatevectorSampler is from qiskit_aer? No, qiskit.primitives.StatevectorSampler is in Qiskit.

Let's write code that is robust.

We can create a circuit with two qubits and two classical bits. Use qc = QuantumCircuit(2, 2). Then:

# Create Bell pair
qc.h(0)
qc.cx(0, 1)

# Alice encodes 11: apply Z then X to q0
qc.z(0)
qc.x(0)

# Bob receives q0 (it's in same circuit), applies CX q0->q1
qc.cx(0, 1)
# H q0
qc.h(0)

# Measure both
qc.measure(0, 0)
qc.measure(1, 1)

Then run StatevectorSampler.

Let's verify the expected result. Superdense coding: start with |Phi+> = (|00> + |11>)/sqrt2. Alice applies Z then X for "11". Let's compute:

|Phi+> = (|00> + |11>)/√2.
Apply Z to q0: Z|0> = |0>, Z|1> = -|1>. So state becomes (|00> - |11>)/√2 = |Phi->.
Apply X to q0: X|0> = |1>, X|1> = |0>. So state becomes (|10> - |01>)/√2? Wait:
After Z: (|00> - |11>)/√2.
Apply X on q0: X|0> = |1>, X|1> = |0>. So |00> -> |10>, |11> -> |01>. So state becomes (|10> - |01>)/√2.
That's |Psi->? Actually |Psi-> = (|01> - |10>)/√2. Our state is (|10> - |01>)/√2 = -(|01> - |10>)/√2 = -|Psi->. Global phase irrelevant. So after encoding, state is |Psi-> (up to global phase).

Bob applies CX q0->q1. CX with control q0 target q1:
On |10>: q0=1, q1=0 -> flip q1 -> |11>.
On |01>: q0=0, q1=1 -> no flip -> |01>.
So state becomes (|11> - |01>)/√2 = (|1> - |0>)|1> / √2? Let's factor: |11> - |01> = (|1> - |0>)|1>. So state = ((|1> - |0>)/√2) ⊗ |1>.
Then apply H to q0: H|1> = (|0> - |1>)/√2. H|0> = (|0> + |1>)/√2.
Wait, the q0 part is (|1> - |0>)/√2 = - (|0> - |1>)/√2 = - H|1>? Actually H|1> = (|0> - |1>)/√2. So (|1> - |0>)/√2 = - (|0> - |1>)/√2 = - H|1>. So after H on q0, the q0 state becomes -|1>. So overall state becomes -|1> ⊗ |1> = -|11>. So measurement yields 11 with certainty.

Thus the most likely decoded bits are "11" with probability 1.0. With 1000 shots, probability should be around 1.0, but due to simulation maybe exactly 1.0. StatevectorSampler might give exact probabilities? With shots, it samples, so counts will be 1000 for "11". Probability = 1000/1000 = 1.0. Rounded to 3 decimals = 1.0. But we need to compute from counts.

Output format:
  Decoded bits: <2-char bitstring>
  Probability: <value rounded to 3 decimals>

So:
  Decoded bits: 11
  Probability: 1.0

But note: "natural order: c0 c1, so '11'". In Qiskit, measurement results bitstrings are usually ordered with the leftmost bit being the highest index? Actually, in Qiskit, the bitstring in counts is ordered as c_{n-1} ... c_0? Wait, there is confusion. In Qiskit, when using get_counts(), the bitstring is printed with the most significant bit being the classical bit with the highest index? Let's recall. In Qiskit, the classical register bits are indexed from 0 to n-1. The bitstring in counts is a string of length n where the leftmost character corresponds to the classical bit with the highest index (n-1) and the rightmost corresponds to bit 0. This is because Qiskit uses little-endian ordering for qubits, but for classical bits in counts, it's often printed as q_{n-1}...q_0? Let's verify.

In Qiskit, if you measure qubit i to classical bit i, the counts bitstring '01' means classical bit 0 is 1 and classical bit 1 is 0? Or the other way? Let's recall from Qiskit textbook: For a 2-qubit circuit, measuring to classical bits, the state |01> means qubit 0 is 1 and qubit 1 is 0? Actually, Qiskit uses little-endian for qubits: |q1 q0> where q0 is the least significant qubit. The bitstring '01' means qubit 1 is 0 and qubit 0 is 1. In Qiskit's counts, the bitstring is ordered with the most significant bit being the highest-indexed classical bit. So '01' corresponds to c1=0, c0=1. Wait, is that right? Let's check.

In Qiskit, the default classical register is also little-endian? The counts dictionary keys are strings where the rightmost bit is classical bit 0. For example, if you have a 2-qubit circuit and measure q0->c0 and q1->c1, and you get counts {'01': 500, '10': 500}, then '01' means c1=0, c0=1? Actually, I think the leftmost bit is the highest index. Let's verify with a known example: Bell state circuit:

qc = QuantumCircuit(2,2)
qc.h(0)
qc.cx(0,1)
qc.measure([0,1],[0,1])

Counts will be roughly {'00': 500, '11': 500}. The Bell state is |00> + |11>. In Qiskit, |00> means q0=0, q1=0. The bitstring '00' is symmetric. If we instead create |01> + |10> (by X on q0 before Bell), the counts would be {'01': 500, '10': 500}. But which bit is which? Let's see: If we do qc.x(0) then H(0) CX(0,1), the state is |01> + |10>? Actually, start |00>, X on q0 gives |01> (q0=1, q1=0). H on q0: (|0> - |1>)/√2 on q0? Wait, X|0> = |1>. H|1> = (|0> - |1>)/√2. So state after H on q0: (|0> - |1>)/√2 ⊗ |0> = (|00> - |10>)/√2. Then CX(0,1): |00> -> |00>, |10> -> |11>. So state = (|00> - |11>)/√2. That's not |01>+|10>. Let's do a better example: X on q1? Actually, let's not get lost.

The key point: The task explicitly says "natural order: c0 c1, so '11'". That means they want the bitstring where the first character is c0 and second is c1. But Qiskit's default counts may output 'c1 c0' (big-endian). We need to be careful to output in natural order c0 c1.

If we measure q0 to c0 and q1 to c1, the resulting state is |11> (q0=1, q1=1). In Qiskit's little-endian bitstring, |11> is represented as '11' because both are 1, so it's symmetric. But for "01" or "10" it matters. Since here it's "11", it's symmetric. But we should still handle it correctly for general case.

The problem says: "prints the most-likely 2-bit decoded message (natural order: c0 c1, so '11')". This implies they want the bitstring as c0 c1. In Qiskit's counts, if we use qc.measure(0,0) and qc.measure(1,1), the counts keys might be 'c1c0' or 'c0c1' depending on version. Let's check Qiskit 1.0 behavior.

In Qiskit 1.0, with the new V2 primitives, the classical data is stored as a BitArray. When you call get_counts(), the bitstrings are ordered with the most significant bit being the last bit measured? Actually, BitArray in Qiskit follows the same convention as Qiskit: the bitstring is printed with the highest index on the left. For a register with bits 0 and 1, the string '01' means bit 1=0, bit 0=1. So the natural order c0 c1 would be the reverse of the Qiskit bitstring.

But since the answer is "11", reverse of "11" is still "11". So we don't need to worry for this specific case. However, to be safe and correct, we might want to reverse the bitstring or construct it from individual bit arrays.

Let's verify with the actual Qiskit code. In Qiskit, if you have a classical register "c" with 2 bits, and you measure qubit 0 to c[0] and qubit 1 to c[1], then the state |q1 q0> = |11> corresponds to counts '11'. For |q1 q0> = |10> (q0=0, q1=1), the counts key is '10'. So if we want c0 c1, we would read the bitstring as c0 c1? Actually, '10' in Qiskit means c1=1, c0=0. So c0 c1 would be '01'. So to get natural order, we need to reverse the string. But again, for '11' it's fine.

Given the problem explicitly says "natural order: c0 c1, so '11'", they likely know about the ordering issue and want us to output the bits in that order. Since the answer is 11, reversing doesn't change it. But we can write code that reverses the bitstring to be safe. Or we can measure in a way that the natural order matches. Actually, if we measure q0 to c1 and q1 to c0? No, the problem says "natural order: c0 c1, so '11'". That suggests c0 is the first bit (leftmost) and c1 is the second bit. In Qiskit, if we use a classical register of 2 bits, the leftmost bit is the highest index. So to have c0 as leftmost, we could measure q0 to c1 and q1 to c0? That would make the leftmost bit correspond to q0? Let's think: if we measure q0 to classical bit 1 and q1 to classical bit 0, then the state |q1 q0> = |11> still gives '11'. For a general state, the leftmost bit would be c1 (which is q0) and the rightmost would be c0 (which is q1). So the bitstring would be c1 c0 = q0 q1? Wait, if q0 maps to c1, then leftmost bit is c1 = q0. Rightmost is c0 = q1. So bitstring = q0 q1. That matches natural order c0 c1 if we rename? Actually, c0 is the first classical bit. If we want the output string to be c0 c1, we need the leftmost character to be c0. But if we map q0 to c0 and q1 to c1, Qiskit's leftmost is c1. So the string is c1 c0. If we map q0 to c1 and q1 to c0, Qiskit's leftmost is c1 = q0, rightmost is c0 = q1. The string is q0 q1. But we want c0 c1. If we call the classical bits by their index, c0 is the first bit (index 0), c1 is the second bit (index 1). The problem says "natural order: c0 c1". That means the first character is c0, second is c1. So if we map q0 to c0 and q1 to c1, the Qiskit string is c1 c0. To get c0 c1, we need to reverse the string. Or we could map q0 to c1 and q1 to c0, then the Qiskit string is c1 c0 = q0 q1. But we want c0 c1. If we map q0 to c0 and q1 to c1, then reversing the Qiskit string gives c0 c1. So the simplest is to reverse.

But since the answer is 11, it doesn't matter. However, I want to write correct code.

Let's think about the StatevectorSampler usage in Qiskit 1.0. We need to import:

from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

Then:

def main():
    qc = QuantumCircuit(2, 2)
    # Bell pair
    qc.h(0)
    qc.cx(0, 1)
    # Alice encodes 11: Z then X on q0
    qc.z(0)
    qc.x(0)
    # Bob decoding
    qc.cx(0, 1)
    qc.h(0)
    # Measure
    qc.measure(0, 0)
    qc.measure(1, 1)

    sampler = StatevectorSampler()
    job = sampler.run([qc], shots=1000)
    result = job.result()
    # Get counts
    pub_result = result[0]
    # In Qiskit 1.0, data is a DataBin. The classical register is named 'c' by default.
    counts = pub_result.data.c.get_counts()
    # counts is a dict like {'11': 1000}

    # Find most likely
    most_likely = max(counts, key=counts.get)
    # most_likely is a string in Qiskit bit order (c1 c0). Reverse to get c0 c1.
    decoded = most_likely[::-1]
    prob = counts[most_likely] / 1000.0
    print(f"  Decoded bits: {decoded}")
    print(f"  Probability: {round(prob, 3)}")

But wait, does pub_result.data.c exist? If we use QuantumCircuit(2,2), the classical register is named 'c'. The DataBin should have attribute 'c'. Let's confirm.

In Qiskit 1.0, the `measure` method adds classical data to the circuit. When using the V2 primitives, the result's `data` is a `DataBin` object. The
```

### Candidate — `deepseek-v4-pro`

**Status:** `EXIT` (0.3s)

**Stderr:** `/Users/daxu/software/quantum-gpt/evals/runs/quantum-algo-20q-20260710/candidates/deepseek-v4-pro/quantum_superdense_coding_11.py:1: DeprecationWarning: Using Qiskit with Python 3.9 is deprecated as of the 2.1.0 release. Support for running Qiskit with Python 3.9 will be removed in the 2.3.0 release,`

```python
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector
from qiskit_aer.primitives import SamplerV2 as Sampler
from qiskit_aer.primitives import StatevectorSampler
import numpy as np

def main():
    # 1. Create Bell pair |Phi+> = (|00> + |11>)/sqrt(2)
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    
    # 2. Alice encodes "11": Z then X on q0
    qc.z(0)  # Z gate
    qc.x(0)  # X gate
    
    # 3. Bob's operations: CX q0->q1, then H on q0, then measure
    qc.cx(0, 1)
    qc.h(0)
    qc.measure([0, 1], [0, 1])
    
    # 4. Simulate with StatevectorSampler, 1000 shots
    sampler = StatevectorSampler(seed=42)
    job = sampler.run([qc], shots=1000)
    result = job.result()
    
    # Get counts from the first (and only) circuit
    counts = result[0].data.c.get_counts()
    
    # Find most likely bitstring
    most_likely = max(counts, key=counts.get)
    prob = counts[most_likely] / 1000.0
    
    print(f"Decoded bits: {most_likely}")
    print(f"Probability: {prob:.3f}")

if __name__ == "__main__":
    main()
```

### Candidate — `qwen3.6-27b-rag`

**Status:** `MISSING` (0.0s)

**Missing substrings:** ['Decoded bits: 11', 'Probability: 1.000']

```
# generation error: HTTP 503: no healthy upstream
```

## 19. 5-qubit GHZ state measurement (`quantum_ghz_state_5qubit`)

### Prompt

```
Write a complete, runnable Python program using Qiskit that:
1. Builds the 5-qubit GHZ state: H on q0, then CX q0->q1, q1->q2, q2->q3, q3->q4.
2. In `def main()`, uses StatevectorSampler (4000 shots), computes P(measurement is all-0s or all-1s), and prints it.
Output exactly:
  P(all-0 or all-1) = <value rounded to 3 decimals>
Call main() under `if __name__ == "__main__":`.
```

### Expected key output substrings

- `P(all-0 or all-1) =`

### Reference solution

```python
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

def main():
    n = 5
    qc = QuantumCircuit(n)
    qc.h(0)
    for i in range(n - 1):
        qc.cx(i, i + 1)
    qc.measure_all()
    sampler = StatevectorSampler()
    counts = sampler.run([qc], shots=4000).result()[0].data.meas.get_counts()
    total = sum(counts.values())
    p = (counts.get("0" * n, 0) + counts.get("1" * n, 0)) / total
    print(f"P(all-0 or all-1) = {p:.3f}")

if __name__ == "__main__":
    main()
```

### Candidate — `glm5.2`

**Status:** `PASS` (0.3s)

```python
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def main():
    qc = QuantumCircuit(5)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.cx(2, 3)
    qc.cx(3, 4)
    qc.measure_all()

    sampler = StatevectorSampler()
    job = sampler.run([qc], shots=4000)
    result = job.result()
    counts = result[0].data.meas.get_counts()

    total = sum(counts.values())
    favorable = counts.get("00000", 0) + counts.get("11111", 0)
    probability = favorable / total

    print(f"P(all-0 or all-1) = {probability:.3f}")


if __name__ == "__main__":
    main()
```

### Candidate — `deepseek-v4-pro`

**Status:** `PASS` (0.4s)

```python
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
import numpy as np

def main():
    # Build 5-qubit GHZ state
    qc = QuantumCircuit(5)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.cx(2, 3)
    qc.cx(3, 4)
    qc.measure_all()

    # Use StatevectorSampler with 4000 shots
    sampler = StatevectorSampler(seed=42)
    job = sampler.run([qc], shots=4000)
    result = job.result()[0]

    # Get counts
    counts = result.data.meas.get_counts()

    # Compute probability of all-0 or all-1
    total_shots = sum(counts.values())
    all_zero = counts.get('00000', 0)
    all_one = counts.get('11111', 0)
    prob = (all_zero + all_one) / total_shots

    print(f"P(all-0 or all-1) = {prob:.3f}")

if __name__ == "__main__":
    main()
```

### Candidate — `qwen3.6-27b-rag`

**Status:** `MISSING` (0.0s)

**Missing substrings:** ['P(all-0 or all-1) =']

```
# generation error: HTTP 503: no healthy upstream
```

## 20. Trotterized XXZ Heisenberg on 2 qubits: <Z on q0> at t=1.0 (`quantum_trotterized_xxz`)

### Prompt

```
Write a complete, runnable Python program using Qiskit that:
1. Simulates the 2-qubit XXZ Heisenberg Hamiltonian H = X (x) X + Y (x) Y + 0.5 * Z (x) Z using a 4-step Trotter decomposition for total time t=1.0 (each step e^{-i dt H}, dt=0.25).
   Per-step gates (for each Trotter step):
     - e^{-i dt XX}: H on both qubits, CX q0->q1, RZ(2*dt) on q1, CX q0->q1, H on both qubits.
     - e^{-i dt YY}: RX(pi/2) on both, CX q0->q1, RZ(2*dt) on q1, CX q0->q1, RX(-pi/2) on both.
     - e^{-i dt * 0.5 ZZ}: CX q0->q1, RZ(2*0.5*dt) on q1, CX q0->q1.
2. Evolves the initial state |01> (apply X on q1).
3. In `def main()`, uses qiskit.primitives.StatevectorEstimator to compute <Z (x) I> (i.e. "ZI" Pauli string) and prints the value rounded to 4 decimals.
Output exactly:
  <Z on q0> = <value>
Call main() under `if __name__ == "__main__":`.
```

### Expected key output substrings

- `<Z on q0> = `

### Reference solution

```python
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator
import math

def main():
    t_total = 1.0
    steps = 4
    dt = t_total / steps
    qc = QuantumCircuit(2)
    qc.x(1)
    for _ in range(steps):
        # XX
        qc.h([0, 1])
        qc.cx(0, 1)
        qc.rz(2 * dt, 1)
        qc.cx(0, 1)
        qc.h([0, 1])
        # YY
        qc.rx(math.pi/2, [0, 1])
        qc.cx(0, 1)
        qc.rz(2 * dt, 1)
        qc.cx(0, 1)
        qc.rx(-math.pi/2, [0, 1])
        # ZZ (with 0.5 coefficient)
        qc.cx(0, 1)
        qc.rz(2 * 0.5 * dt, 1)
        qc.cx(0, 1)
    est = StatevectorEstimator()
    obs = SparsePauliOp.from_list([("ZI", 1.0)])
    res = est.run([(qc, obs)]).result()
    val = float(res[0].data.evs.item())
    print(f"<Z on q0> = {val:.4f}")

if __name__ == "__main__":
    main()
```

### Candidate — `glm5.2`

**Status:** `EXIT` (0.3s)

**Stderr:** `/Users/daxu/software/quantum-gpt/evals/runs/quantum-algo-20q-20260710/candidates/glm5.2/quantum_trotterized_xxz.py:1: DeprecationWarning: Using Qiskit with Python 3.9 is deprecated as of the 2.1.0 release. Support for running Qiskit with Python 3.9 will be removed in the 2.3.0 release, which coincid`

```python
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp

estimator = StatevectorEstimator()
observable = SparsePauliOp("ZI")
job = estimator.run([(circuit, observable)])
result = job.result()
value = float(result[0].data.evs)
```

### Candidate — `deepseek-v4-pro`

**Status:** `PASS` (0.3s)

```python
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator
import numpy as np

def main():
    dt = 0.25
    steps = 4
    total_time = 1.0

    # Build circuit for 4 Trotter steps
    qc = QuantumCircuit(2)
    # Initial state |01>
    qc.x(1)

    for _ in range(steps):
        # e^{-i dt XX}
        qc.h(0)
        qc.h(1)
        qc.cx(0, 1)
        qc.rz(2 * dt, 1)
        qc.cx(0, 1)
        qc.h(0)
        qc.h(1)

        # e^{-i dt YY}
        qc.rx(np.pi / 2, 0)
        qc.rx(np.pi / 2, 1)
        qc.cx(0, 1)
        qc.rz(2 * dt, 1)
        qc.cx(0, 1)
        qc.rx(-np.pi / 2, 0)
        qc.rx(-np.pi / 2, 1)

        # e^{-i dt * 0.5 ZZ}
        qc.cx(0, 1)
        qc.rz(2 * 0.5 * dt, 1)
        qc.cx(0, 1)

    # Observable ZI
    obs = SparsePauliOp.from_list([("ZI", 1.0)])

    estimator = StatevectorEstimator()
    job = estimator.run([(qc, obs)])
    result = job.result()
    value = result[0].data.evs

    print(f"<Z on q0> = {value:.4f}")

if __name__ == "__main__":
    main()
```

### Candidate — `qwen3.6-27b-rag`

**Status:** `EXIT` (0.0s)

**Stderr:** `File "/Users/daxu/software/quantum-gpt/evals/runs/quantum-algo-20q-20260710/candidates/qwen3.6-27b-rag/quantum_trotterized_xxz.py", line 2 |     <html lang="zh-CN"> |     ^ | SyntaxError: invalid syntax |`

```
# generation error: HTTP 503: <!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 - 页面未找到 | 焕新</title>
    <style>
```
