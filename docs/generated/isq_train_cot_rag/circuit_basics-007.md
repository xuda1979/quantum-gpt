# ISQ training COT RAG corpus: circuit_basics shard 7

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/2470

- task_id: `isqTrain/2470`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `global_phase`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `1508`

### Prompt

Are these two quantum circuits equivalent in terms of measurement output?

Circuit 1:
```isq
import std;
qbit q[3];
procedure main() {
    M(q[0]); M(q[1]); M(q[2]);
}

```

Circuit 2:
```isq
import std;
qbit q[3];
procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis

1. **Program A**: Declares three qubits and immediately measures them. Since no gates are applied, all qubits remain in their initial state |0⟩, yielding |000⟩ with probability 1.

2. **Program B**: Same as Program A, but inserts `GPhase(0.0)` before measurement. This applies a global phase factor of e^(i·0) = 1, which is mathematically trivial.

3. **Key difference**: Program B adds `GPhase(0.0)`, which has no physical effect since a phase of zero changes nothing.

4. **Measurement probabilities**: Identical. Both programs produce |000⟩ with probability 1, and all other outcomes with probability 0. Global phases do not affect measurement distributions.

5. **Verdict: Equivalent: Yes**

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/1587

- task_id: `isqTrain/1587`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3313`

### Prompt

实现以下量子计算任务（使用isQ）：On 4 qubits, set q[3]=|1> and apply CNOT with control=q[3], target=q[2]. Measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Initialize q[3] to |1> and use it as a control to flip q[2] using a CNOT gate, then measure all qubits.
2. **Qubits**: Requires 4 qubits (`q[0]` to `q[3]`), all of which are measured.
3. **State Evolution**:
   - Start in the ground state |0000> (ordered as `q[0]q[1]q[2]q[3]`).
   - Apply `X(q[3])` to flip the 4th qubit: |0000> → |0001>.
   - Apply `CNOT(q[3], q[2])`, which flips target `q[2]` because control `q[3]` is |1>: |0001> → |0011>.
4. **Probabilities**: The final state is deterministically |0011>, so the measurement yields the bitstring `0011` with probability 1.0.

## isqTrain/1620

- task_id: `isqTrain/1620`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `1814`

### Prompt

Implement a quantum circuit in isQ: Apply SWAP(q[1],q[2]) twice (identity) on 3 qubits with q[1]=|1>. Measure all.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply swap (three-CNOT decomposition) twice (identity) on qubits q[1] and q[2] with q[1] initialized to |1⟩, then measure all.
Three qubits q[0], q[1], q[2] are used, all measured at the end.
Initial state: |000⟩ → after X(q[1]): |010⟩
After first swap (three-CNOT decomposition)(q[1],q[2]): |001⟩ (swaps q[1] and q[2])
After second swap (three-CNOT decomposition)(q[1],q[2]): |010⟩ (identity restored)
Final state is |010⟩ with certainty, so measurement yields |010⟩ with probability 1.0.

## isqTrain/1748

- task_id: `isqTrain/1748`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3098`

### Prompt

Code this in isQ: Apply CZ to |11>. Measure both qubits. (CZ only adds phase to |11>, invisible in Z-basis.)

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Apply a CZ gate to the two-qubit state |11> and measure the outcome, demonstrating that the Z-phase is invisible in the computational basis.
2. **Qubits:** 2 qubits are required, and both are measured.
3. **State Evolution:**
   - Initialize the system to the ground state: |00>.
   - Apply X gates to both qubits (X⊗X) to prepare the state |11>.
   - Apply the CZ gate, which adds a global phase of -1 exclusively to the |11> state, yielding -|11>.
4. **Probabilities:** The final state is -|11>. Since a global phase has no effect on measurement probabilities, a measurement in the Z-basis deterministically yields the outcome |11> with probability 1.0.

## isqTrain/1568

- task_id: `isqTrain/1568`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `241`

### Prompt

Write an isQ program that Apply the gate sequence T-T-H to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply the sequence T-T-H to an initial |0> state and measure the result.
2. Qubits: 1 qubit is required and measured.
3. State evolution:
   - Initial state is |0>.
   - Apply T gate: |0> remains |0> (T only applies a phase to |1>).
   - Apply T gate: |0> remains |0>.
   - Apply H gate: |0> becomes |+> = (1/√2)|0> + (1/√2)|1>.
4. Probabilities: The final state |+> is an equal superposition of |0> and |1>, resulting in a 50% probability for both outcomes: P(|0>) = 0.5 and P(|1>) = 0.5.

## isqTrain/1486

- task_id: `isqTrain/1486`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `data_encoding_qml`
- source: `isq_train_cot`
- dataset_index: `5786`

### Prompt

帮我写一个isQ程序：Encode the classical value 13/16 into a qubit using angle encoding (Ry rotation with angle pi*13/16). Measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Encode the classical value 13/16 into a qubit using angle encoding via Ry rotation with angle π×13/16, then measure.
2. **Qubits**: 1 qubit (`q[0]`) is used and measured.
3. **State evolution**:
   - Initial state: |0⟩
   - After `Ry(π×13/16, q[0])`: The Ry(θ) gate transforms |0⟩ → cos(θ/2)|0⟩ + sin(θ/2)|1⟩, yielding cos(13π/32)|0⟩ + sin(13π/32)|1⟩
4. **Measurement probabilities**: P(|0⟩) = cos²(13π/32) ≈ 0.0843, P(|1⟩) = sin²(13π/32) ≈ 0.9157, matching the predicted output.

## isqTrain/1761

- task_id: `isqTrain/1761`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2466`

### Prompt

帮我写一个isQ程序：Apply Ry(2pi/3) to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. The goal is to apply the rotation gate Ry(2π/3) to the initial state |0⟩ and measure the resulting state.
2. This requires a single qubit (`q[0]`) which is measured at the end.
3. The initial state |0⟩ evolves under Ry(2π/3) to cos(π/3)|0⟩ + sin(π/3)|1⟩ = (1/2)|0⟩ + (√3/2)|1⟩.
4. The measurement probabilities follow from taking the squared amplitudes: P(|0⟩) = |1/2|² = 0.25 and P(|1⟩) = |√3/2|² = 0.75.

## isqTrain/1808

- task_id: `isqTrain/1808`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4894`

### Prompt

Implement the following in isQ: Apply Rx(pi*10/6) to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply Rx(5π/3) to |0⟩ and measure the resulting state.
2. **Qubits**: 1 qubit (q[0]), which is measured.
3. **State evolution**:
   - Initial: |ψ⟩ = |0⟩
   - After Rx(5π/3): Rx(θ)|0⟩ = cos(θ/2)|0⟩ - i·sin(θ/2)|1⟩ with θ=5π/3, so θ/2=5π/6
   - cos(5π/6) = -√3/2, sin(5π/6) = 1/2
   - |ψ⟩ = -√3/2·|0⟩ - i/2·|1⟩
4. **Probabilities**: P(|0⟩) = |-√3/2|² = 3/4 = 0.75, P(|1⟩) = |-i/2|² = 1/4 = 0.25

## isqTrain/4708

- task_id: `isqTrain/4708`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3956`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    Rz(pi/2.0, q[0]);
    H(q[0]);
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the isQ code:**
    *   `H(q[0]);` -> Apply Hadamard to qubit 0. State goes from $|0\rangle$ to $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
    *   `Rz(pi/2.0, q[0]);` -> Apply Rz($\pi/2$), which is equivalent to the S gate (up to global phase). $|0\rangle \to |0\rangle$, $|1\rangle \to i|1\rangle$. State becomes $\frac{1}{\sqrt{2}}(|0\rangle + i|1\rangle) = |i+\rangle$ (or just apply to the coefficients).
    *   `H(q[0]);` -> Apply Hadamard.
        *   $H(|0\rangle) = |+\rangle$
        *   $H(|1\rangle) = |-\rangle$
        *   Resulting state: $\frac{1}{\sqrt{2}}(|+\rangle + i|-\rangle) = \frac{1}{\sqrt{2}}(\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) + \frac{i}{\sqrt{2}}(|0\rangle - |1\rangle)) = \frac{1}{2}((1+i)|0\rangle + (1-i)|1\rangle)$.
    *   `X(q[0]);` -> Apply Pauli-X (bit flip).
        *   State becomes $\frac{1}{2}((1+i)|1\rangle + (1-i)|0\rangle) = \frac{1}{2}((1-i)|0\rangle + (1+i)|1\rangle)$.
    *   `M(q[0]);` -> Measure.
        *   Probability of $|0\rangle$: $| \frac{1-i}{2} |^2 = \frac{1^2 + (-1)^2}{4} = \frac{2}{4} = 0.5$.
        *   Probability of $|1\rangle$: $| \frac{1+i}{2} |^2 = \frac{1^2 + 1^2}{4} = \frac{2}{4} = 0.5$.

2.  **Format the output:**
    *   Follow instructions: "Output ONLY the analysis, starting with '## Circuit Analysis'".
    *   Use Dirac notation.
    *   Be concise (3-8 lines).
    *   End with the predicted probability distribution.

3.  **Drafting the text:**
    ## Circuit Analysis
    1. **Initial state:** The qubit starts in $|0\rangle$.
    2. **First H:** Applies a Hadamard gate, changing the state to $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
    3. **Rz($\pi/2$):** Rotates the phase, transforming the state to $\frac{1}{\sqrt{2}}(|0\rangle + i|1\rangle)$.
    4. **Second H:** Applies another Hadamard gate. $H|0\rangle \to |+\rangle$ and $H|1\rangle \to |-\rangle$, yielding $\frac{1}{2}((1+i)|0\rangle + (1-i)|1\rangle)$.
    5. **X gate:** Flips the basis states, resulting in the final state $\frac{1}{2}((1-i)|0\rangle + (1+i)|1\rangle)$.
    6. **Measurement:** The probabilities are $P(|0\rangle) = |(1-i)/2|^2 = 0.5$ and $P(|1\rangle) = |(1+i)/2|^2 = 0.5$.
    
    Predicted probability distribution: {|0>: 0.5, |1>: 0.5}

4.  **Refining to exact predicted output format:**
    *   Ensure lines are concise.
    *   "Predicted probability distribution: {|0>: 0.5, |1>: 0.5}"
    
    Let's check the Rz($\pi/2$) gate definition. It's exactly `[[1, 0], [0, exp(i * pi/2)]]` = `[[1, 0], [0, i]]`. Yes, so it's exactly S.
    So `H` then `S` then `H` is actually the adjoint of `S`, or `S\dagger`. Wait.
    `

### Reference answer

{'predicted_probs': {'0': 0.5, '1': 0.5}, 'explanation': 'This isQ program operates on 1 qubit(s). The measurement probability distribution is: P(|0>) = 0.5000, P(|1>) = 0.5000.'}

## isqTrain/1805

- task_id: `isqTrain/1805`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1534`

### Prompt

Code this in isQ: Apply Rx(pi*7/6) to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply an Rx rotation of 7π/6 to |0⟩ and measure the resulting state.

We need 1 qubit (q[0]), which is measured.

State evolution:
1. Initialize: |ψ⟩ = |0⟩
2. Apply Rx(7π/6): Rx(θ)|0⟩ = cos(θ/2)|0⟩ - i·sin(θ/2)|1⟩
   - θ/2 = 7π/12, so |ψ⟩ = cos(7π/12)|0⟩ - i·sin(7π/12)|1⟩

Measurement probabilities:
- P(|0⟩) = cos²(7π/12) = (2 - √3)/4 ≈ 0.067
- P(|1⟩) = sin²(7π/12) =
