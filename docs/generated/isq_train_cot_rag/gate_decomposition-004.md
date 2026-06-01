# ISQ training COT RAG corpus: gate_decomposition shard 4

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3157

- task_id: `isqTrain/3157`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `2550`

### Prompt

I need an isQ program to an isQ program: apply H, Rz(2*pi/4), H to a qubit and measure. This implements Rx(2*pi/4) via conjugation.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Implement an Rx(π/2) rotation on a single qubit using H and Rz(π/2) conjugation, then measure it.
2. **Qubits:** 1 qubit (`q[0]`) is allocated and measured.
3. **State Evolution:**
   - Initial state is |0⟩.
   - Apply H: transforms the state to |+⟩ = (|0⟩ + |1⟩)/√2.
   - Apply Rz(2π/4) = Rz(π/2): applies a phase factor to |1⟩, yielding (|0⟩ + i|1⟩)/√2.
   - Apply H: maps the state to (1/√2)|0⟩ - (i/√2)|1⟩, which exactly equals Rx(π/2)|0⟩.
4. **Probabilities:** The magnitude squared of both amplitudes is |1/√2|² = 0.5, giving expected measurement probabilities of 50% for |0⟩ and 50% for |1⟩.

## isqTrain/3279

- task_id: `isqTrain/3279`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `265`

### Prompt

I need an isQ program to an isQ program: apply Ry(2*pi/3) then Ry(-2*pi/3) to cancel. Measure: should get |0>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Verify that Ry(2π/3) followed by Ry(-2π/3) acts as identity, returning to |0⟩.
2. **Qubits**: 1 qubit q[0], which is measured.
3. **State evolution**:
   - Start: |ψ⟩ = |0⟩
   - After Ry(2π/3, q[0]): |ψ⟩ = cos(π/3)|0⟩ + sin(π/3)|1⟩ = 0.5|0⟩ + (√3/2)|1⟩
   - After Ry(-2π/3, q[0]): Ry(-θ) = Ry(θ)†, so Ry(-2π/3)Ry(2π/3) = I, giving |ψ⟩ = |0⟩
4. **Expected probabilities**: Since the two rotations cancel exactly, P(|0⟩) = 1.0.

## isqTrain/3332

- task_id: `isqTrain/3332`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `333`

### Prompt

Write isQ code for the following quantum task: an isQ program: apply gate chain H-Z-X to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply the gate chain H-Z-X to a single qubit initialized to |0> and measure the result.
2. **Qubits**: 1 qubit is needed and measured.
3. **State evolution**:
    - Start in |0>.
    - Apply H: transforms |0> to |+> = 1/sqrt(2)(|0> + |1>).
    - Apply Z: transforms |+> to |-> = 1/sqrt(2)(|0> - |1>).
    - Apply X: flips the basis states, transforming |-> to 1/sqrt(2)(|1> - |0>) = -|-> (global phase -1).
4. **Probabilities**: The final state -|-> has amplitudes of magnitude 1/sqrt(2) for both |0> and |1>. Thus, the measurement probabilities are P(|0>) = 0.5 and P(|1>) = 0.5.

## isqTrain/3404

- task_id: `isqTrain/3404`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `4157`

### Prompt

请用isQ语言编写一个量子电路：an isQ program: H, Rz(2*pi/5), H on a qubit. This is equivalent to Rx(2*pi/5).

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply H*Rz(2π/5)*H to a single qubit, equivalent to Rx(2π/5).
2. **Qubits**: 1 qubit (`q[0]`), measured at the end.
3. **State evolution**:
   - |0⟩ → H → |+⟩ = (|0⟩+|1⟩)/√2
   - → Rz(2π/5) → (|0⟩ + e^(i2π/5)|1⟩)/√2
   - → H → (1+e^(i2π/5))/2|0⟩ + (1-e^(i2π/5))/2|1⟩
4. **Probabilities**: P(|0⟩) = |(1+e^(i2π/5))/2|² = (1+cos(2π/5))/2 ≈ 0.6545; P(|1⟩) ≈ 0.3455.

## isqTrain/3305

- task_id: `isqTrain/3305`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `difficult`
- concept_tags: `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `3958`

### Prompt

Implement the following in isQ: an isQ program: apply 2-controlled Z gate with all controls set to |1>.

### Chain-of-thought reasoning

## Reasoning
- Goal: Execute a 2-controlled Z gate (double-controlled-Z (ctrl @[c1, c2] Z(target))) with both control qubits initialized to |1>.
- Qubits: 3 qubits (q[0], q[1], q[2]), all measured.
- Evolution: Initial state |000> transitions to |110> after applying X gates to q[0] and q[1].
- Apply double-controlled-Z (ctrl @[c1, c2] Z(target)) gate: Since controls q[0] and q[1] are in the |1> state, the Z gate is applied to target q[2].
- State change: Z|0> = |0>, so the final quantum state remains |110>.
- Result: The final measurement yields the bitstring |110> with a 100% probability.

## isqTrain/3286

- task_id: `isqTrain/3286`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2001`

### Prompt

Implement a quantum circuit in isQ: an isQ program: apply Rx(1*pi/8) then Rx(-1*pi/8) to cancel. Measure: should get |0>.

### Chain-of-thought reasoning

## Reasoning
1. The goal is to demonstrate that applying Rx(π/8) and then Rx(-π/8) cancels out, leaving the state unchanged.
2. One qubit, q[0], is needed and measured.
3. Step-by-step state evolution:
   - Initial state: |0>
   - After Rx(π/8): Rotated around X-axis by π/8
   - After Rx(-π/8): Rx is additive, so Rx(-π/8)Rx(π/8) = Rx(0) = I, returning to |0>
4. Since the final state is |0>, the measurement probability is P(|0>) = 1.0.

## isqTrain/3410

- task_id: `isqTrain/3410`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `5306`

### Prompt

Code this in isQ: an isQ program: H, Rz(4*pi/5), H on a qubit. This is equivalent to Rx(4*pi/5).

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply H, Rz(4π/5), H to a single qubit, demonstrating the identity H·Rz(θ)·H = Rx(θ).
2. **Qubits**: 1 qubit needed, q[0] is measured.
3. **State evolution**:
   - |0⟩ → H → |+⟩ = (|0⟩+|1⟩)/√2
   - |+⟩ → Rz(4π/5) → (e^(-i2π/5)|0⟩ + e^(i2π/5)|1⟩)/√2
   - → H → cos(2π/5)|0⟩ - i·sin(2π/5)|1⟩ = Rx(4π/5)|0⟩
4. **Probabilities**: P(|0⟩) = cos²(2π/5) ≈ 0.0955, P(|1⟩) = sin²(2π/5) ≈ 0.9045, matching Rx(4π/5).

## isqTrain/3173

- task_id: `isqTrain/3173`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `3259`

### Prompt

实现以下量子计算任务（使用isQ）：an isQ program: apply nctrl X (negative-controlled NOT) with q[0] as control and q[1] as target on state |11>. nctrl X flips target when control is |0>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply a negative-controlled NOT gate with q[0] as control and q[1] as target, starting from state |11⟩.
2. **Qubits**: 2 qubits (q[0], q[1]), both measured.
3. **State evolution**:
   - Initial: |00⟩
   - X(q[0]): |10⟩
   - X(q[1]): |11⟩
   - nctrl X(q[0], q[1]): Since q[0] = |1⟩, the negative control condition (control = |0⟩) is NOT met, so q[1] is not flipped → state remains |11⟩
4. **Expected result**: The nctrl X only activates when the control is |0⟩; since it's |1⟩, the target is unchanged. Final state |11⟩ gives measurement probability P(|11⟩) = 1.0.

## isqTrain/1348

- task_id: `isqTrain/1348`
- task_type: `output_prediction`
- category: `gate_decomposition`
- difficulty: `difficult`
- concept_tags: `isq_syntax_deriving_gate`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2718`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;

defgate SQSWAP = [
    1, 0, 0, 0;
    0, 0.5+0.5j, 0.5-0.5j, 0;
    0, 0.5-0.5j, 0.5+0.5j, 0;
    0, 0, 0, 1
];

qbit q[3];

procedure main() {
    X(q[0]);
    SQSWAP(q[0], q[1]);
    SQSWAP(q[0], q[1]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The objective is to analyze the given isQ quantum program and provide a step-by-step reasoning of its execution, ultimately predicting the probability distribution of measurement outcomes.

2.  **Analyze the isQ Program**:
    *   **Initial state**: 3 qubits `q[0]`, `q[1]`, `q[2]` initialized to $|0\rangle$. State is $|000\rangle$.
    *   **Gate 1**: `X(q[0])` flips `q[0]` to $|1\rangle$. State is $|100\rangle$.
    *   **Gate 2**: `SQswap (three-CNOT decomposition)(q[0], q[1])`. The SQswap (three-CNOT decomposition) gate matrix is given.
    *   **Gate 3**: `SQswap (three-CNOT decomposition)(q[0], q[1])` again.
    *   **Measurements**: `M(q[0])`, `M(q[1])`, `M(q[2])`.

3.  **Analyze SQswap (three-CNOT decomposition) Gate**:
    *   Matrix:
        $$
        \begin{bmatrix}
        1 & 0 & 0 & 0 \\
        0 & \frac{1+i}{2} & \frac{1-i}{2} & 0 \\
        0 & \frac{1-i}{2} & \frac{1+i}{2} & 0 \\
        0 & 0 & 0 & 1
        \end{bmatrix}
        $$
    *   Effect on basis states:
        *   $|00\rangle \to |00\rangle$
        *   $|01\rangle \to \frac{1+i}{2}|01\rangle + \frac{1-i}{2}|10\rangle$
        *   $|10\rangle \to \frac{1-i}{2}|01\rangle + \frac{1+i}{2}|10\rangle$
        *   $|11\rangle \to |11\rangle$
    *   Since SQswap (three-CNOT decomposition) is applied twice, we can calculate $SQswap (three-CNOT decomposition)^2$ or just trace the state. Actually, a square root of swap (three-CNOT decomposition) applied twice *should* be the swap operation (three-CNOT decomposition), possibly with a global phase. Let's verify.
        *   Applying SQswap (three-CNOT decomposition) to $|10\rangle$:
            $\frac{1-i}{2}|01\rangle + \frac{1+i}{2}|10\rangle$
        *   Applying SQswap (three-CNOT decomposition) again to this state:
            For the $|01\rangle$ component: $\frac{1+i}{2}|01\rangle + \frac{1-i}{2}|10\rangle$
            For the $|10\rangle$ component: $\frac{1-i}{2}|01\rangle + \frac{1+i}{2}|10\rangle$
            Total state:
            $|01\rangle [ (\frac{1-i}{2})(\frac{1+i}{2}) + (\frac{1+i}{2})(\frac{1-i}{2}) ] + |10\rangle [ (\frac{1-i}{2})(\frac{1-i}{2}) + (\frac{1+i}{2})(\frac{1+i}{2}) ]$
            Wait, let me re-evaluate the matrix multiplication.
            Let $S$ be the SQswap (three-CNOT decomposition) matrix.
            $S = \begin{bmatrix} 1 & 0 & 0 & 0 \\ 0 & a & b & 0 \\ 0 & b & a & 0 \\ 0 & 0 & 0 & 1 \end{bmatrix}$ where $a = \frac{1+i}{2}$ and $b = \frac{1-i}{2}$.
            $S^2 = \begin{bmatrix} 1 & 0 & 0 & 0 \\ 0 & a^2+b^2 & 2ab & 0 \\ 0 & 2ab & a^2+b^2 & 0 \\ 0 & 0 & 0 & 1 \end{bmatrix}$.
            $a^2 = (\frac{1+i}{2})^2 = \frac{1 + 2i - 1}{4} = \frac{2i}{4} = \frac{i}{2}$.
            $b^2 = (\frac{1-i}{2})^2 = \frac{1 - 2i - 1}{4} = \frac{-2i}{4} = -\frac{i}{2}$.
            So $a^2+b^2 = 0$.
            $2ab = 2(\frac{1+i}{2})(\frac{1-i}{2}) = 2(\frac{

### Reference answer

{'predicted_probs': {'2': 1.0}, 'explanation': 'Parametric variant of isqEval/494. Dimension: qubit_variant: q[2] -> q[3].'}

## isqTrain/3290

- task_id: `isqTrain/3290`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `10`

### Prompt

I need an isQ program to an isQ program: apply H, Rz(1*pi/3), Rz(-1*pi/3), H. Since Rz cancels, net is H*H=I.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Demonstrate that inverse Rz rotations cancel each other out when sandwiched between Hadamard gates, resulting in the identity operation.
2. **Qubits:** 1 qubit (`q[0]`) is used and measured.
3. **State Evolution:**
   - Start in the initial state $|0\rangle$.
   - Apply $H$: transforms the state to $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
   - Apply $R_z(\pi/3)$ followed by $R_z(-\pi/3)$: the rotations cancel perfectly ($
