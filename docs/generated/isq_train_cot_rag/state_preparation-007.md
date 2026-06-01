# ISQ training COT RAG corpus: state_preparation shard 7

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/2514

- task_id: `isqTrain/2514`
- task_type: `code_equivalence`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `global_phase`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3919`

### Prompt

Compare these two isQ programs. Do they give the same probability distribution?

First program:
```isq
import std;
qbit q[1];

procedure main() {
    Rx(pi/3.0, q[0]);
    M(q[0]);
}

```

Second program:
```isq
import std;
qbit q[1];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    Rx(pi/3.0, q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** initializes qubit q[0] in the |0> state and applies an Rx rotation of π/3.
2. **Program B** performs the exact same operations but includes an additional GPhase(0.0) gate.
3. The key difference is the GPhase(0.0) gate in Program B, which applies a global phase factor of $e^{i(0)} = 1$.
4. Since a global phase of 0 does not change the quantum state vector, both programs yield the identical state: $\cos(\pi/6)|0\rangle - i\sin(\pi/6)|1\rangle$.
5. Thus, the measurement probability distributions are exactly the same ($P(0) = 3/4$, $P(1) = 1/4$).

Equivalent: Yes

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/4050

- task_id: `isqTrain/4050`
- task_type: `bug_fix`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `5172`

### Prompt

This isQ program compiles but produces incorrect probabilities. Find and correct the mistake.

```
import std;
// 2-qubit state via Ry rotations: Ry(0.0) ⊗ Ry(0.5)
qbit q[2];

procedure main() {
    // Apply rotations to create product state
    // BUG: missing gate here
    Ry(0.5, q[1]);
    // Measure
    M(q[0]); M(q[1]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: The `Ry(0.0, q[0])` gate is missing, leaving q[0] without its intended rotation. The task specifies creating the product state Ry(0.0) ⊗ Ry(0.5), but only q[1] receives its rotation.

2. **Fix**: Add `Ry(0.0, q[0])` before the existing `Ry(0.5, q[1])` line. This applies the identity-equivalent rotation to q[0], keeping it in |0⟩.

3. **State evolution**:
   - Initial: |00⟩
   - After Ry(0.0, q[0]): |0⟩ ⊗ |0⟩ = |00⟩ (no change)
   - After Ry(0.5, q[1]): |0⟩ ⊗ (cos(0.25)|0⟩ + sin(0.25)|1⟩)
   - Final: cos(0.25)|00⟩ + sin(0.25)|01⟩
   - Probabilities: P(|00⟩) = cos²(0.25) ≈ 0.9388, P(|01⟩) = sin²(0.25) ≈ 0.0612 ✓

## isqTrain/4256

- task_id: `isqTrain/4256`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `4474`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;

qbit q[1];

procedure main() {
    // |+> state
    H(q[0]);
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); // prob 0.5, 0.5
}

```

### Chain-of-thought reasoning

1.  **Analyze the isQ program**:
    *   Initializes 1 qubit `q[0]` in state `|0>`.
    *   Applies Hadamard gate `H(q[0])`.
    *   Applies Pauli-X gate `X(q[0])`.
    *   Measures `q[0]`.

2.  **Step-by-step state evolution**:
    *   Initial state: `|0>`
    *   After `H(q[0])`: `H|0> = |+> = (1/sqrt(2))|0> + (1/sqrt(2))|1>`
    *   After `X(q[0])`: `X|+> = 1/sqrt(2) X|0> + 1/sqrt(2) X|1> = 1/sqrt(2)|1> + 1/sqrt(2)|0> = |+>`
    *   Alternatively: `X|+> = X (H|0>) = H (X|0>) = H|1> = |->` (Wait, let's be precise. X H = H X. So X(H|0>) = H(X|0>) = H|1> = `|->`. Let's recompute).
    *   Let's do the math carefully:
        *   `H|0> = (|0> + |1>) / sqrt(2)`
        *   `X(|0> + |1>) / sqrt(2) = (X|0> + X|1>) / sqrt(2) = (|1> + |0>) / sqrt(2) = (|0> + |1>) / sqrt(2) = |+>`.
        *   Oh, wait. `X` swaps `|0>` and `|1>`.
        *   So `X|+> = X( (|0> + |1>)/sqrt(2) ) = (|1> + |0>)/sqrt(2) = |+>`.
        *   Let's double check $H X = X H$.
        *   $H X |0> = H |1> = |-> = (|0> - |1>)/\sqrt{2}$.
        *   $X H |0> = X (|0> + |1>)/\sqrt{2} = (|1> + |0>)/\sqrt{2} = |+>$.
        *   Ah! $X$ and $H$ do NOT commute! $HX = \begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix} \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix} = \begin{pmatrix} 1 & 1 \\ -1 & 1 \end{pmatrix}$. $XH = \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix} \begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix} = \begin{pmatrix} 1 & -1 \\ 1 & 1 \end{pmatrix}$.
        *   Wait, $H X |0> = H |1> = |->$.
        *   $X H |0> = X |+> = X \frac{1}{\sqrt{2}}(|0> + |1>) = \frac{1}{\sqrt{2}}(|1> + |0>) = |+>$.
        *   Yes, $X|+> = |+>$.
        *   Let's re-verify $X|+>$.
        *   $|+> = \frac{1}{\sqrt{2}} \begin{pmatrix} 1 \\ 1 \end{pmatrix}$.
        *   $X|+> = \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix} \frac{1}{\sqrt{2}} \begin{pmatrix} 1 \\ 1 \end{pmatrix} = \frac{1}{\sqrt{2}} \begin{pmatrix} 1 \\ 1 \end{pmatrix} = |+>$.
        *   Yes! $X|+> = |+>$.
        *   So the state after X is still $|+>$.

3.  **Final state and probabilities**:
    *   State is $|+> = (|0> + |1>) / \sqrt{2}$.
    *   Probabilities: $P(|0>) = |1/\sqrt{2}|^2 = 0.5$, $P(|

### Reference answer

{'predicted_probs': {'0': 0.5, '1': 0.5}, 'explanation': 'This isQ program operates on 1 qubit(s). The measurement probability distribution is: P(|0>) = 0.5000, P(|1>) = 0.5000.'}

## isqTrain/3148

- task_id: `isqTrain/3148`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `4045`

### Prompt

Implement a quantum circuit in isQ: an isQ program: apply X to all 4 qubits to prepare |1111>, then measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Prepare the 4-qubit state |1111⟩ from the default |0000⟩ state using X gates, then measure all qubits.
2. **Qubits:** 4 qubits declared globally, all 4 are measured.
3. **State evolution:**
   - Start: |0000⟩
   - X(q[0]): |0000⟩ → |1000⟩
   - X(q[1]): |1000⟩ → |1100⟩
   - X(q[2]): |1100⟩ → |1110⟩
   - X(q[3]): |1110⟩ → |1111⟩
4. **Probabilities:** The final state is deterministically |1111⟩, so measurement yields `1111` with probability 1.0.

## isqTrain/3928

- task_id: `isqTrain/3928`
- task_type: `bug_fix`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3972`

### Prompt

这个isQ程序有问题，请找出错误并给出正确代码：

```
import std;
// Graph state for line_3 topology
// Edges: [(0, 1), (1, 2)]
qbit q[3];

procedure main() {
    // Step 1: Hadamard on all qubits (|+>^n)
    H(q[0]);
    H(q[1]);
    X(q[2]);
    // Step 2: CZ for each edge
    CZ(q[0], q[1]);  // edge (0,1)
    CZ(q[1], q[2]);  // edge (1,2)
    // Measure all qubits
    M(q[0]);
    M(q[1]);
    M(q[2]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

## Bug Analysis
1. The bug is on line 9 where `X(q[2])` is applied instead of the Hadamard gate. This incorrectly initializes qubit 2 to the |1> state, whereas graph state preparation requires initializing all qubits to the |+> state.
2. The fix is to replace `X(q[2])` with `H(q[2])`.
3. State evolution of the corrected circuit:
   - Initial state: |000>
   - After H gates: |+>^⊗3 = (1/√8) ∑|x>
   - After CZ gates: The CZ gates apply phase shifts based on the edges, resulting in the correct line_3 graph state.
   -

## isqTrain/3386

- task_id: `isqTrain/3386`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `2600`

### Prompt

Write an isQ program that an isQ program: in a 2-qubit register, apply X then H to q[1] only. Other qubits stay |0>. Measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply X then H to q[1] in a 2-qubit register, leaving q[0] in |0⟩, then measure both qubits.
2. **Qubits**: 2-qubit register q[2]; both q[0] and q[1] are measured.
3. **State evolution**:
   - Initialize: |q₀q₁⟩ = |00⟩
   - X(q[1]): |00⟩ → |01⟩
   - H(q[1]): |01⟩ → (|00⟩ − |01⟩)/√2
4. **Measurement probabilities**: The final state is an equal superposition of |00⟩ and |01⟩, giving P(|00⟩) = 0.5 and P(|01⟩) = 0.5.

## isqTrain/4816

- task_id: `isqTrain/4816`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_switch`, `isq_syntax_classical_vars`
- source: `isq_train_cot`
- dataset_index: `1481`

### Prompt

请用isQ语言编写一个量子电路：uses switch to apply different numbers of X gates. Declare 1 global qubit. Set int count=2 (last case). Use switch(count): case 0 applies X(q[0]) three times (net X), case 1 applies X(q[0]) twice (net identity), case 2 applies X(q[0]) once. Since count=2 (last case, no fall-through), q[0] gets one X gate. Measure q[0]. Expected: |1>.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply different numbers of X gates via switch to demonstrate case-based gate control.
2. One global qubit q[0] is declared; only q[0] is measured.
3. State evolution: |0⟩ →(X gate from case 2)→ |1⟩. Since count=2, only case 2 executes, applying X(q[0]) once.
4. Measurement of |1⟩ yields outcome 1 with probability 1.0, giving expected probabilities {|1⟩: 1.0}.

## isqTrain/3180

- task_id: `isqTrain/3180`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5757`

### Prompt

Implement a quantum circuit in isQ: an isQ program: apply Ry(3*pi/5) to one qubit, then CNOT to a second qubit, creating partial entanglement.

### Chain-of-thought reasoning

## Reasoning
Goal: Create partial entanglement between two qubits using Ry rotation followed by CNOT.

Two qubits needed, both measured. Initial state: |00⟩

State evolution:
1. Ry(3π/5) on q[0]: |00⟩ → cos(3π/10)|00⟩ + sin(3π/10)|10⟩
2. CNOT(q[0], q[1]): → cos(3π/10)|00⟩ + sin(3π/10)|11⟩

Final state is a partially entangled Bell-like state. Probabilities: P(|00⟩) = cos²(3π/10) ≈ 0.3455, P(|11⟩) = sin²(3π/10) ≈ 0.6545.

## isqTrain/3881

- task_id: `isqTrain/3881`
- task_type: `bug_fix`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `1732`

### Prompt

This isQ program doesn't produce the correct output. Can you debug it?

Code:
```
import std;
// 2-qubit state via Ry rotations: Ry(0.5) ⊗ Ry(0.0)
qbit q[2];

procedure main() {
    // Apply rotations to create product state
    // BUG: missing gate here
    Ry(0.0, q[1]);
    // Measure
    M(q[0]); M(q[1]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: The gate `Ry(0.5, q[0])` is missing from the circuit. The comment "BUG: missing gate here" indicates where the gate should be. Without it, q[0] remains in |0⟩ and only the identity rotation is applied to q[1], yielding |00⟩ with probability 1 — not the intended product state.

2. **Fix**: Add `Ry(0.5, q[0]);` before the existing `Ry(0.0, q[1]);` line to apply the specified rotation to qubit q[0].

3. **State evolution of corrected circuit**:
   - Initial state: |00⟩
   - After `Ry(0.5, q[0])`: (cos(0.25)|0⟩ + sin(0.25)|1⟩) ⊗ |0⟩
   - After `Ry(0.0, q[1])`: no change (identity rotation)
   - Final: cos(0.25)|00⟩ + sin(0.25)|10⟩
   - Measurement probabilities: P(|00⟩) = cos²(0.25) ≈ 0.9388, P(|10⟩) = sin²(0.25) ≈ 0.0612 ✓

## isqTrain/4215

- task_id: `isqTrain/4215`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `929`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[2];

procedure main() {
    Ry(0.5, q[0]);
    Ry(0.0, q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes two qubits in the |00⟩ state. 
2. `Ry(0.5, q[0])` rotates q[0] around the Y-axis by 0.5 radians, evolving it to cos(0.25)|0⟩ + sin(0.25)|1⟩.
3. `Ry(0.0, q[1])` acts as an identity operation, leaving q[1] in the |0⟩ state.
4. The joint quantum state before measurement is cos(0.25)|00⟩ + sin(0.25)|10⟩.

Predict

### Reference answer

Deterministic output: state |00> with probability ~0.94
