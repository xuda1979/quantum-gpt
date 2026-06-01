# ISQ training COT RAG corpus: gate_decomposition shard 8

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1684

- task_id: `isqTrain/1684`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `1308`

### Prompt

Help me write isQ code that CZ using the decomposition H-CNOT-H on |11>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement CZ on |11⟩ using the decomposition CZ = (I⊗H)·CNOT·(I⊗H).
2. **

## isqTrain/3353

- task_id: `isqTrain/3353`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `1194`

### Prompt

Create an isQ quantum circuit that an isQ program: apply 2-qubit gate chain H1-CNOT-H1 to |00> and measure both qubits.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Apply the gate chain H-CNOT-H to qubit q[1] (with q[0] as CNOT control) on initial state |00>.

**Qubits:** 2 qubits (q[0], q[1]), both measured.

**State evolution:**
1. Initial: |00⟩
2. H(q[1]): |0⟩⊗(1/√2)(|0⟩+|1⟩) = 1/√2(|00⟩+|01⟩)
3. CNOT(q[0],q[1]): Control q[0]=|0⟩, so target unchanged → 1/√2(|00⟩+|01⟩)
4. H(q[1]): H|+⟩ = |0⟩, so 1/√2·|0⟩⊗(1/√2(|0⟩+|1⟩+|0⟩−|1⟩)) = |00⟩

**Result:** Final state is |00⟩, so P(|00⟩)=1.0.

## isqTrain/14

- task_id: `isqTrain/14`
- task_type: `output_prediction`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `global_phase`, `isq_syntax_arrays`, `isq_syntax_deriving_gate`, `isq_syntax_procedures`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2644`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
qbit q[2];

procedure cy_gate(qbit c, qbit t) {
    inv S(t);
    CNOT(c, t);
    S(t);
}

procedure main() {
    X(q[0]);
    X(q[1]);
    cy_gate(q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a step-by-step quantum circuit analysis for an isQ program. The output must follow specific formatting rules (Dirac notation, concise 3-15 lines, start with "## Circuit Analysis", end with the probability distribution).

2.  **Analyze the isQ code:**
    *   Initialization: `qbit q[2];` -> state is $|00\rangle$.
    *   `main()`:
        *   `X(q[0]);` -> Flips q[0] to $|1\rangle$. State is $|10\rangle$.
        *   `X(q[1]);` -> Flips q[1] to $|1\rangle$. State is $|11\rangle$.
        *   `cy_gate(q[0], q[1]);` -> Applies a controlled-Y gate, defined as `inv S(target); CNOT(control, target); S(target);`.
            *   Wait, let's check the definition of CY gate:
                *   $S^\dagger$ on target
                *   CNOT(control, target)
                *   $S$ on target
            *   Since q[0] is control ($|1\rangle$) and q[1] is target ($|1\rangle$), let's trace the state:
                *   Initial state for cy: $|11\rangle$.
                *   `inv S(q[1])`: Applies $S^\dagger = \begin{pmatrix} 1 & 0 \\ 0 & -i \end{pmatrix}$ to q[1]. State becomes $1 \cdot (-i) |11\rangle = -i|11\rangle$.
                *   `CNOT(q[0], q[1])`: Control is $|1\rangle$, so target q[1] flips. $|1\rangle \to |0\rangle$. State becomes $-i|10\rangle$.
                *   `S(q[1])`: Applies $S = \begin{pmatrix} 1 & 0 \\ 0 & i \end{pmatrix}$ to q[1]. q[1] is $|0\rangle$, so $S|0\rangle = |0\rangle$. State remains $-i|10\rangle$.
        *   Alternatively, apply matrix representation of CY to $|11\rangle$:
            *   $CY = (I \otimes S) \cdot CNOT \cdot (I \otimes S^\dagger)$
            *   Wait, $(I \otimes S) \cdot CNOT \cdot (I \otimes S^\dagger) |11\rangle = (I \otimes S) \cdot CNOT |1\rangle \otimes (-i|1\rangle) = -i (I \otimes S) |10\rangle = -i |10\rangle$.
        *   Final state is $-i|10\rangle$.
        *   Measurements: `M(q[0]); M(q[1]);`
            *   Measurement result corresponds to $|10\rangle$ with probability 1.0.

3.  **Draft the response:**
    *   *Step 1:* Initial state $|00\rangle$.
    *   *Step 2:* `X(q[0])` and `X(q[1])` prepare the state $|11\rangle$.
    *   *Step 3:* `cy_gate` applies $S^\dagger(q[1])$, turning the state to $-i|11\rangle$.
    *   *Step 4:* `CNOT(q[0], q[1])` flips q[1] to $|0\rangle$, making the state $-i|10\rangle$.
    *   *Step 5:* `S(q[1])` leaves $|0\rangle$ unchanged, leaving the final state as $-i|10\rangle$.
    *   *Step 6:* Probability of measuring $|10\rangle$ is 1.0.

4.  **Refine formatting:**
    *   Ensure it starts with "## Circuit Analysis"
    *   Ensure it ends with "Expected measurement probabilities: {|10>: 1.0}"
    *   Check conciseness. The drafted steps are about 5-6 lines. Perfect.

5.  **Final Review of the generated text:**
    ## Circuit Analysis
    1. The circuit initializes two qubits to |00>.
    2. X gates on both q[0] and q[1] flip their states to |1>, resulting in the state |11>.
    3. The `cy_gate` procedure applies S^\dagger to q[1], yielding

### Reference answer

{'predicted_probs': {'2': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/2. Dimension: predict probabilities for reference circuit.'}

## isqTrain/3413

- task_id: `isqTrain/3413`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `5568`

### Prompt

Implement a quantum circuit in isQ: an isQ program: H, Rz(5*pi/7), H on a qubit. This is equivalent to Rx(5*pi/7).

### Chain-of-thought reasoning

## Reasoning
Goal: Apply H, Rz(5π/7), H to a single qubit, implementing the identity H·Rz(θ)·H = Rx(θ).

Qubits: 1 qubit (q[0]), measured at the end.

State evolution:
1. Initialize |0⟩
2. H(q[0]): |0⟩ → |+⟩ = (|0⟩ + |1⟩)/√2
3. Rz(5π/7, q[0]): |+⟩ → (|0⟩ + e^(i5π/7)|1⟩)/√2
4. H(q[0]): Applies Hadamard, yielding cos(5π/14)|0⟩ - i·sin(5π/14)|1⟩ (equivalent to Rx(5π/7)|0⟩)

Probabilities: P(|0⟩) = cos²(5π/14) ≈ 0.1883, P(|1⟩) = sin²(5π/14) ≈ 0.8117, matching predicted output.

## isqTrain/3403

- task_id: `isqTrain/3403`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `3673`

### Prompt

实现以下量子计算任务（使用isQ）：an isQ program: H, Rz(2*pi/3), H on a qubit. This is equivalent to Rx(2*pi/3).

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply H·Rz(2π/3)·H to a single qubit, demonstrating the identity H·Rz(θ)·H = Rx(θ).
2. One qubit is needed (`q[0]`), and it is measured at the end.
3. State evolution: |0⟩ →H→ |+⟩ = (|0⟩+|1⟩)/√2 →Rz(2π/3)→ (e^{-iπ/3}|0⟩ + e^{iπ/3}|1⟩)/√2 →H→ cos(π/3)|0⟩ - i·sin(π/3)|1⟩ = ½|0⟩ - i(√3/2)|1⟩
4. Measurement probabilities: P(|0⟩) = |½|² = 0.25, P(|1⟩) = |√3/2|² = 0.75, confirming equivalence to Rx(2π/3)|0⟩.

## isqTrain/3416

- task_id: `isqTrain/3416`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `4069`

### Prompt

I need an isQ program to an isQ program: H, Rz(7*pi/8), H on a qubit. This is equivalent to Rx(7*pi/8).

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply H-Rz(7π/8)-H to a single qubit, which is equivalent to Rx(7π/8).
2. **Qubits**: 1 qubit, measured at the end.
3. **State evolution**:
   - Initial: |0⟩
   - After H: |+⟩ = (|0⟩ + |1⟩)/√2
   - After Rz(7π/8): (|0⟩ + e^{i7π/8}|1⟩)/√2
   - After H: (1 + e^{i7π/8})/2|0⟩ + (1 - e^{i7π/8})/2|1⟩ ≡ Rx(7π/8)|0⟩ = cos(7π/16)|0⟩ - i·sin(7π/16)|1⟩
4. **Probabilities**: P(|0⟩) = cos²(7π/16) ≈ 0.0381, P(|1⟩) = sin²(7π/16) ≈ 0.9619, matching predicted output.

## isqTrain/3256

- task_id: `isqTrain/3256`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4312`

### Prompt

I need an isQ program to an isQ program: apply X twice to each of 3 qubits (X*X=I), then measure. All qubits should remain |0>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply X*X=I (double X) to each of 3 qubits, proving identity leaves |0> unchanged.
2. **Qubits**: 3 qubits (q[0], q[1], q[2]), all measured.
3. **State evolution**: |000> → X(q[0])X(q[0])→|000> → X(q[1])X(q[1])→|000> → X(q[2])X(q[2])→|000>. Each X*X=I leaves state unchanged.
4. **Expected probabilities**: {|000>: 1.0} — final state is |000>, so all measurements yield 0.

## isqTrain/3161

- task_id: `isqTrain/3161`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `3416`

### Prompt

Create an isQ quantum circuit that an isQ program: apply H, Rz(2*pi/64), H to a qubit and measure. This implements Rx(2*pi/64) via conjugation.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement Rx(2π/64) via H-Rz-H conjugation and measure the resulting qubit.
2. **Qubits**: 1 qubit (`q[0]`), which is measured.
3. **State evolution**:
   - Start: |0⟩
   - After H: |+⟩ = (1/√2)(|0⟩ + |1⟩)
   - After Rz(2π/64): (1/√2)(e^(-iπ/64)|0⟩ + e^(iπ/64)|1⟩)
   - After H: cos(π/64)|0⟩ - i·sin(π/64)|1⟩ = Rx(2π/64)|0⟩
4. **Probabilities**: P(|0⟩) = cos²(π/64) ≈ 0.9976, P(|1⟩) = sin²(π/64) ≈ 0.0024, matching predicted output.

## isqTrain/3158

- task_id: `isqTrain/3158`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `3692`

### Prompt

Code this in isQ: an isQ program: apply H, Rz(2*pi/8), H to a qubit and measure. This implements Rx(2*pi/8) via conjugation.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Implement Rx(π/4) using the identity H·Rz(θ)·H = Rx(θ) on a single qubit starting in |0⟩, then measure.
2. **Qubits:** One qubit q[0] is used and measured.
3. **State evolution:**
   - Start: |0⟩
   - H: |0⟩ → |+⟩ = (1/√2)(|0⟩ + |1⟩)
   - Rz(π/4): |+⟩ → (1/√2)(e^{-iπ/8}|0⟩ + e^{iπ/8}|1⟩)
   - H: → cos(π/8)|0⟩ − i·sin(π/8)|1⟩
4. **Probabilities:** P(|0⟩) = cos²(π/8) ≈ 0.8536, P(|1⟩) = sin²(π/8) ≈ 0.1464, matching Rx(π/4)|0⟩.

## isqTrain/3405

- task_id: `isqTrain/3405`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `4053`

### Prompt

Write an isQ program that an isQ program: H, Rz(2*pi/7), H on a qubit. This is equivalent to Rx(2*pi/7).

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply H, Rz(2π/7), H to a single qubit, which is mathematically equivalent to Rx(2π/7).
2. **Qubits**: 1 qubit (`q[0]`), measured at the end.
3. **State evolution**:
   - Start: |0⟩
   - After H: |+⟩ = (|0⟩ + |1⟩)/√2
   - After Rz(2π/7): (e^{-iπ/7}|0⟩ + e^{iπ/7}|1⟩)/√2
   - After H: cos(π/7)|0⟩ − i·sin(π/7)|1⟩
4. **Probabilities**: P(|0⟩) = cos²(π/7) ≈ 0.8117, P(|1⟩) = sin²(π/7) ≈ 0.1883.
