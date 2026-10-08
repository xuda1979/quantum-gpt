# Quantum circuit construction patterns

## Layered circuits
Most quantum algorithms decompose into:
1. State preparation (e.g. H^n on the input register).
2. Oracle / problem-encoding block (Grover oracle, QAOA cost unitary).
3. Diffusion / mixer / inverse-QFT block.
4. Measurement.

Keep each block as a function returning a circuit; compose them with
`+` (Cirq), `compose` (Qiskit), or operator overloading.

## Parameterised circuits
For VQE/QAOA, expose parameters as inputs:

```python
def qaoa_layer(qc, gamma, beta, edges, n):
    # Cost unitary
    for u, v, w in edges:
        qc.cx(u, v)
        qc.rz(2 * w * gamma, v)
        qc.cx(u, v)
    # Mixer unitary
    for q in range(n):
        qc.rx(2 * beta, q)
```

## Repair / minimal-edit patterns
For repair-style tasks (common in evals/tasks/quantum/...):
- Read the failing tests carefully; only change what the test exercises.
- Prefer renaming/aliasing over re-implementing.
- Add missing imports; remove dead code; canonicalise inputs.
- For "normalize gate sequence" style tasks, use a single dictionary
  lookup with `gate.strip().lower()` and raise `ValueError` for misses.

## Phase pattern checks
For tasks that verify phase patterns (QFT, QPE), test fixtures usually
use `numpy.allclose` on the phase angles modulo `2*pi`. Always reduce
phases via `np.mod(phases, 2 * np.pi)` before comparing.

## Endianness alignment
A surprising number of bugs come from mixing endianness conventions
between input bitstrings, gate matrices, and library-returned state
vectors. Pick *one* convention per task and convert at the boundaries.

## Common pitfalls
- Forgetting to `transpile` (Qiskit) before sampling - works but slow.
- Mutating shared circuit objects; copy before parameter substitution.
- Off-by-one in qubit indices: e.g. `range(n - 1)` vs `range(n)` for
  nearest-neighbour entanglers.
