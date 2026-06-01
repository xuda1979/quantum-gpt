# ISQ training COT RAG corpus: hamiltonian_simulation shard 7

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4041

- task_id: `isqTrain/4041`
- task_type: `bug_fix`
- category: `hamiltonian_simulation`
- difficulty: `expert`
- concept_tags: `hamiltonian_simulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `2710`

### Prompt

I'm getting wrong output from this isQ code. What's the bug and how do I fix it?

```
import std;
// First-order Trotter: exp(-i*t*(XX + ZZ)) ≈ exp(-i*t*XX)*exp(-i*t*ZZ)
qbit q[2];

procedure main() {
    // exp(-i*t*XX) block
    H(q[0]); H(q[1]);
    CNOT(q[0], q[1]);
    Rz(2.0 * 2.0 * 0.5, q[1]);
    CNOT(q[0], q[1]);
    H(q[0]); H(q[1]);
    // exp(-i*t*ZZ) block
    CNOT(q[0], q[1]);
    Rz(2.0 * 0.5, q[1]);
    CNOT(q[0], q[1]);
    // Measure
    M(q[0]); M(q[1]);
}

``` (bug type: wrong parameter)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: In the `exp(-i*t*XX)` block, the Rz gate has parameter `2.0 * 2.0 * 0.5 = 2.0`, which contains a spurious extra factor of 2.0. This doubles the intended rotation angle for the XX term.

2. **Fix**: Change `Rz(2.0 * 2.0 * 0.5, q[1])` to `Rz(2.0 * 0.5, q[1])` in the XX block. Both the XX and ZZ blocks should use `Rz(2t)` with t=0.5, giving angle 1.0.

3. **State evolution (corrected)**: Starting from |00⟩:
   - H⊗H: → |++⟩ = (|00⟩+|01⟩+|10⟩+|11⟩)/2
   - CNOT-Rz(1.0)-CNOT: applies exp(-i·0.5·XX) → rotates XX term correctly
   - H⊗H: returns to computational basis
   - CNOT-Rz(1.0)-CNOT: applies exp(-i·0.5·ZZ) → rotates ZZ term correctly
   - Final state yields measurement probabilities {|00⟩: 0.770151, |11⟩: 0.229849}, confirming the corrected Trotter step.

## isqTrain/3669

- task_id: `isqTrain/3669`
- task_type: `code_generation`
- category: `hamiltonian_simulation`
- difficulty: `difficult`
- concept_tags: `hamiltonian_simulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `3483`

### Prompt

Code this in isQ: a Trotter simulation of the XX interaction Hamiltonian H = X⊗X with time t=0.8. Decompose exp(-i*t*X⊗X) using Hadamard gates, CNOT, and Rz rotation. Start from |00> and measure both qubits.

### Chain-of-thought reasoning

Step 1: The goal is to simulate exp(-i * 0.8 * X⊗X) on |00> and measure.
Step 2: 2 qubits are needed, both are measured.
Step 3: State evolution:
- Initial state: |00>
- H⊗H on |00> -> (|00> + |01> + |10> + |11>)/2 = (|+>|+>)
- The XX interaction can be simulated via conjugation: exp(-i*t*XX) = (H⊗I) CNOT Rz(2t) CNOT (H⊗I) acting on qubits. Wait, let's trace the given decomposition.
- Actually, let's trace: H⊗H CNOT_{0,1} Rz_{1}(1.6) CNOT_{0,1} H⊗H |00>.
- H⊗H |00> = |+>|+> = 1/2 (|00> + |01> + |10> + |11>)
- CNOT_{0,1}: 1/2 (|00> + |01> + |10> + |11>) -> 1/2 (|00> + |01> + |11> + |10>)
- Rz_{1}(1.6) on qubit 1: Adds phase e^{-i(1.6)/2} for |0> and e^{i(1.6)/2} for |1>.
Wait, Rz(theta) = exp(-i * theta * Z / 2). So Rz(1.6) = exp(-i * 0.8 * Z).
- For |0>, phase is e^{-i * 0.8}. For |1>, phase is e^{i * 0.8}.
Wait, |00> -> e^{-i 0.8}|00>, |01> -> e^{i 0.8}|01>, |11> -> e^{-i 0.8}|11>, |10> -> e^{i 0.8}|10>.
Wait, |10> becomes e^{i 0.8}|10>.
Let's write it out:
State after Rz: 1/2 (e^{-i 0.8}|00> + e^{i 0.8}|01> + e^{i 0.8}|11> + e^{-i 0.8}|10>)
Factorize by qubit 0:
= 1/2 [ |0>(e^{-i 0.8}|0> + e^{i 0.8}|1>) + |1>(e^{-i 0.8}|1> + e^{i 0.8}|0>) ]
- CNOT_{0,1}: 1/2 [ |0>(e^{-i 0.8}|0> + e^{i 0.8}|1>) + |1>(e^{i 0.8}|0> + e^{-i 0.8}|1>) ]
- H on qubit 0:
Apply H to |0> -> |+>, |1> -> |->.
1/2 [ |+>(e^{-i 0.8}|0> + e^{i 0.8}|1>) + |->(e^{i 0.8}|0> + e^{-i 0.8}|1>) ]
= 1/4 [ (|0> + |1>)(...) + (|0> - |1>)(...) ]
= 1/4 [ |0>( (e^{-i 0.8} + e^{i 0.8})|0> + (e^{i 0.8} + e^{-i 0.8})|1> ) + |1>( (e^{-i 0.8} - e^{i 0.8})|0> + (e^{i 0.8} - e^{-i 0.8})|1> ) ]
= 1/2 [ |0>(cos(0.8)|0> + cos(0.8)|1>) + |1>(-i sin(0.8)|0> + i sin(0.8)|1>) ]
- H on qubit 1:
1/2 [ |0>(cos(0.8)(|+>)) + |1>(-i sin(0.8)(|->)) ]
= 1/sqrt(2) [ cos(0.8) |0>|+> - i sin(0.8) |1>|-> ]
Wait, is that correct? Let's re-evaluate Rz.
exp(-i * 0.8 * X_0 X_1) on |00>.
|00> = 1/sqrt(2)(|0

## isqTrain/4019

- task_id: `isqTrain/4019`
- task_type: `bug_fix`
- category: `hamiltonian_simulation`
- difficulty: `difficult`
- concept_tags: `hamiltonian_simulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `3191`

### Prompt

Debug this isQ program — it gives unexpected measurement results.

```
import std;
// Trotter simulation of XX interaction: exp(-i*0.3*X⊗X)
// Decomposition: H-CNOT-Rz-CNOT-H
qbit q[2];

procedure main() {
    // Decompose exp(-i*t*XX) using CNOT sandwich
    H(q[0]);
    H(q[1]);
    CNOT(q[0], q[1]);
    Rz(2.0 * 2.0 * 0.3, q[1]);
    CNOT(q[0], q[1]);
    H(q[0]);
    H(q[1]);
    // Measure both qubits
    M(q[0]); M(q[1]);
}

``` (bug type: wrong parameter)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: The `Rz` gate parameter is `2.0 * 2.0 * 0.3 = 1.2` (double the correct value). The extra factor of 2.0 is incorrect.

2. **Fix**: Change `Rz(2.0 * 2.0 * 0.3, q[1])` to `Rz(2.0 * 0.3, q[1])`. The decomposition of exp(-i·t·X⊗X) uses the identity X⊗X = (H⊗H)(Z⊗Z)(H⊗H), and exp(-i·t·Z⊗Z) is implemented via CNOT-Rz(2t)-CNOT. With t=0.3, the Rz angle is 2×0.3 = 0.6.

3. **State evolution** (corrected):
   - |00⟩ → (H⊗H) → |++⟩ = (|00⟩+|01⟩+|10⟩+|11⟩)/2
   - CNOT(q[0],q[1]) → (|00⟩+|01⟩+|11⟩+|10⟩)/2
   - Rz(0.6, q[1]) → (|00⟩+e^{-i0.6}|01⟩+e^{-i0.6}|11⟩+|10⟩)/2
   - CNOT(q[0],q[1]) → (|00⟩+e^{-i0.6}|01⟩+|11⟩+e^{-i0.6}|10⟩)/2
   - (H⊗H) → cos(0.3)|00⟩ - i·sin(0.3)|11⟩
   - Measuring: P(|00⟩) = cos²(0.3) ≈ 0.9127, P(|11⟩) = sin²(0.3) ≈ 0.0873 ✓
