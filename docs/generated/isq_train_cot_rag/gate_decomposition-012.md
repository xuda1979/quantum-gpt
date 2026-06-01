# ISQ training COT RAG corpus: gate_decomposition shard 12

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3160

- task_id: `isqTrain/3160`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `2412`

### Prompt

Write an isQ program that an isQ program: apply H, Rz(2*pi/32), H to a qubit and measure. This implements Rx(2*pi/32) via conjugation.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement Rx(2π/32) on a qubit using H-Rz-H conjugation, then measure.
A single qubit `q[0]` is used and measured.

State evolution:
1. |0⟩ → H → |+⟩ = (|0⟩ + |1⟩)/√2
2. |+⟩ → Rz(2π/32) → (e^{-iπ/32}|0⟩ + e^{iπ/32}|1⟩)/√2
3. → H → cos(π/32)|0⟩ - i·sin(π/32)|1⟩

This equals Rx(2π/32)|0⟩ since H·Rz(θ)·H = Rx(θ).
Probabilities: P(|0⟩) = cos²(π/32) ≈ 0.9904, P(|1⟩) = sin²(π/32) ≈ 0.0096.

## isqTrain/3344

- task_id: `isqTrain/3344`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `3978`

### Prompt

Write an isQ program that an isQ program: apply 2-qubit gate chain CNOT-H0 to |00> and measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply CNOT followed by H on qubit 0 to the initial state |00>, then measure both qubits.
2. **Qubits**: 2 qubits (q[0], q[1]), both measured.
3. **State evolution**:
   - Start: |00⟩
   - CNOT(q[0], q[1]): Control q[0] is |0⟩, target unchanged → |00⟩
   - H(q[0]): H|0⟩ = |+⟩ = (|0⟩+|1⟩)/√2 → (|00⟩+|10⟩)/√2
4. **Expected probabilities**: Equal superposition of |00⟩ and |10⟩ gives P(|00⟩)=0.5, P(|10⟩)=0.5.

## isqTrain/3260

- task_id: `isqTrain/3260`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `reversible_computing`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `3285`

### Prompt

Help me write isQ code that an isQ program: apply H twice to each of 2 qubits (H*H=I), then measure. All should be |0>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply H twice to each of 2 qubits (H²=I), then measure; all outcomes should be |0⟩.
2. **Qubits**: 2 qubits (q[0], q[1]), both measured.
3. **State evolution**: |00⟩ → H(q[0]) → |+0⟩ → H(q[0]) → |00⟩ → H(q[1]) → |0+⟩ → H(q[1]) → |00⟩
4. **Result**: Since H²=I, both qubits return to |0⟩, yielding measurement probabilities {|00⟩: 1.0}.

## isqTrain/3371

- task_id: `isqTrain/3371`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `4368`

### Prompt

用isQ实现an isQ program: apply H to control q[0], then ctrl Ry(pi/3) from q[0] to q[1], then measure both.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create superposition on q[0] with H, then conditionally rotate q[1] using controlled-Ry(π/3), and measure both qubits.

2. **Qubits**: 2 qubits (q[0], q[1]), both measured.

3. **State evolution**:
   - Initial: |00⟩
   - After H(q[0]): (|00⟩ + |10⟩)/√2
   - After ctrl Ry(π/3): q[0]=|1⟩ triggers Ry(π/3) on q[1], mapping |0⟩ → cos(π/6)|0⟩ + sin(π/6)|1⟩ = (√3/2)|0⟩ + (1/2)|1⟩
   - Final state: (1/√2)|00⟩ + (√3/(2√2))|10⟩ + (1/(2√2))|11⟩

4. **Probabilities**: P(|00⟩) = 1/2 = 0.5, P(|10⟩) = 3/8 = 0.375, P(|11⟩) = 1/8 = 0.125. These come from squaring the amplitudes of the final state.

## isqTrain/1338

- task_id: `isqTrain/1338`
- task_type: `output_prediction`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_procedures`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `891`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;
qbit q[3];

procedure crz_gate(double theta, qbit c, qbit t) {
    Rz(theta/2.0, t);
    CNOT(c, t);
    Rz(-theta/2.0, t);
    CNOT(c, t);
}

procedure main() {
    X(q[0]);
    X(q[1]);
    crz_gate(pi, q[0], q[1]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants a concise, step-by-step circuit analysis of the given isQ program, predicting the probability distribution of the measurement outcomes. The output must follow specific formatting rules.

2.  **Analyze the isQ Code**:
    *   `import std;`
    *   `qbit q[3];` -> Initial state is |000>.
    *   `procedure crz_gate(double theta, qbit c, qubit t)`:
        *   `Rz(theta/2.0, t);`
        *   `CNOT(c, t);`
        *   `Rz(-theta/2.0, t);`
        *   `CNOT(c, t);`
        *   *Note*: This is a standard decomposition of a controlled-Rz (CRz) gate. For $|11\rangle$ it applies $e^{-i\theta/2}$ to the state due to the relative phases, but actually let's trace it exactly.
    *   `main()`:
        *   `X(q[0]);` -> state becomes |100>.
        *   `X(q[1]);` -> state becomes |110>.
        *   `crz_gate(pi, q[0], q[1]);`
            *   Applies CRz(pi) with control q[0] and target q[1].
            *   $R_z(\pi/2)$ on q[1]: State |110> becomes $e^{-i \pi/4} |110\rangle$.
            *   `CNOT(q[0], q[1])`: |110> -> |100> (since q[1] flips). State is $e^{-i \pi/4} |100\rangle$.
            *   $R_z(-\pi/2)$ on q[1]: State is $e^{-i \pi/4} e^{i \pi/4} |100\rangle = |100\rangle$.
            *   `CNOT(q[0], q[1])`: |100> -> |110> (since q[1] flips back). State is $|110\rangle$.
            *   Wait, let's re-evaluate the $R_z$ action.
            *   $R_z(\lambda) = \begin{pmatrix} e^{-i\lambda/2} & 0 \\ 0 & e^{i\lambda/2} \end{pmatrix}$.
            *   On |0>, $R_z$ applies $e^{-i\lambda/2}$. On |1>, $R_z$ applies $e^{i\lambda/2}$.
            *   Start: $|110\rangle$.
            *   $R_z(\pi/2)$ on q[1]: q[1] is |1>. Phase $e^{i(\pi/2)/2} = e^{i\pi/4}$. Wait, the standard definition of $R_z$ might vary, but let's use $R_z(\theta) = Z^{theta/\pi}$ or $diag(e^{-i\theta/2}, e^{i\theta/2})$.
            *   Let's trace carefully: $|1\rangle \xrightarrow{R_z(\theta)} e^{i\theta/2} |1\rangle$.
            *   $|110\rangle \xrightarrow{R_z(\pi/2, q_1)} e^{i\pi/4} |110\rangle$.
            *   $CNOT(q_0, q_1)$: $|110\rangle \to |100\rangle$. The phase applies to the whole state: $e^{i\pi/4} |100\rangle$.
            *   $R_z(-\pi/2, q_1)$: q[1] is now |0>. Phase is $e^{-i(-\pi/2)/2} = e^{i\pi/4}$. State becomes $e^{i\pi/4} e^{i\pi/4} |100\rangle = e^{i\pi/2} |100\rangle$.
            *   $CNOT(q_0, q_1)$: $|100\rangle \to |110\rangle$. State is $e^{i\pi/2} |110\rangle$.
            *   Since $e^{i\pi/2}$ is a global phase, the physical state is exactly $|110\rangle$.
        *   Wait, let me double check standard CRz decomposition.
        *   $CRz(\theta) = \begin{pmatrix} 1 & 0 & 0 & 0 \\ 0 & 1 & 0 & 0 \\ 0 & 0 & e^{-i\theta/2

### Reference answer

{'predicted_probs': {'6': 1.0}, 'explanation': 'Parametric variant of isqEval/486. Dimension: qubit_variant: q[2] -> q[3].'}

## isqTrain/3125

- task_id: `isqTrain/3125`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `3991`

### Prompt

Code this in isQ: an isQ program: apply ctrl X (=CNOT) on initial state |11> and measure both qubits.

### Chain-of-thought reasoning

## Reasoning
*   The goal is to apply a CNOT gate to the |11> state and measure the resulting state of both qubits.
*   Two qubits, `q[0]` and `q[1]`, are required, and both are measured.
*   Initialize the state to |11> by applying X gates to both qubits: $X \otimes X |00\rangle = |11\rangle$.
*   Apply the CNOT gate with `q[0]` as the control and `q[1]` as the target. Since the control qubit is in the |1> state, the target qubit flips: $CNOT |11\rangle = |10\rangle$.
*   Because the final quantum state is deterministically |10>, the expected measurement outcome is |10> with a probability of 1.0.

## isqTrain/3369

- task_id: `isqTrain/3369`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1064`

### Prompt

请用isQ语言编写一个量子电路：an isQ program: apply H to control q[0], then ctrl Ry(pi/4) from q[0] to q[1], then measure both.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Create a superposition on q[0], then conditionally rotate q[1] via controlled-Ry(π/4), and measure both qubits.

2. **Qubits**: 2 qubits (q[0], q[1]), both measured.

3. **State evolution**:
   - Initial: |00⟩
   - After H(q[0]): (|00⟩ + |10⟩)/√2
   - After ctrl Ry(π/4): (|00⟩ + cos(π/8)|10⟩ + sin(π/8)|11⟩)/√2

4. **Probabilities**: P(|00⟩) = 1/2 = 0.5, P(|10⟩) = cos²(π/8)/2 ≈ 0.8536/2 ≈ 0.4268, P(|11⟩) = sin²(π/8)/2 ≈ 0.1464/2 ≈ 0.0732, P(|01⟩) = 0.

## isqTrain/3414

- task_id: `isqTrain/3414`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `2970`

### Prompt

Code this in isQ: an isQ program: H, Rz(5*pi/8), H on a qubit. This is equivalent to Rx(5*pi/8).

### Chain-of-thought reasoning

## Reasoning
Goal: Apply H-Rz(5π/8)-H to a single qubit, equivalent to Rx(5π/8).
One qubit is used and measured.

State evolution:
- |0⟩ → H → |+⟩ = (|0⟩+|1⟩)/√2
- |+⟩ → Rz(5π/8) → (e^(-i5π/16)|0⟩ + e^(i5π/16)|1⟩)/√2
- → H → Rx(5π/8)|0⟩ = cos(5π/16)|0⟩ - i·sin(5π/16)|1⟩

Since H·Rz(θ)·H = Rx(θ), the final state has P(|0⟩) = cos²(5π/16) ≈ 0.3087 and P(|1⟩) = sin²(5π/16) ≈ 0.6913.

## isqTrain/3406

- task_id: `isqTrain/3406`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `595`

### Prompt

I need an isQ program to an isQ program: H, Rz(3*pi/4), H on a qubit. This is equivalent to Rx(3*pi/4).

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply H·Rz(3π/4)·H to a single qubit, which is equivalent to Rx(3π/4).
2. One qubit is needed (q[0]) and measured at the end.
3. State evolution: |0⟩ →H |+⟩ = (1/√2)(|0⟩ + |1⟩) →Rz(3π/4) (1/√2)(|0⟩ + e^(i3π/4)|1⟩) →H (1/2)[(1+e^(i3π/4))|0⟩ + (1-e^(i3π/4))|1⟩].
4. Probability of |0⟩: |(1+e^(i3π/4))/2|² = (2-√2)/4 ≈ 0.1464; probability of |1⟩: (2+√2)/4 ≈ 0.8536, matching expected results.

## isqTrain/3126

- task_id: `isqTrain/3126`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `4536`

### Prompt

Implement the following in isQ: an isQ program: apply ctrl Z (=CZ) on initial state |00> and measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply a controlled-Z (CZ) gate to two qubits initialized in |00⟩ and measure both.
2. **Qubits**: 2 qubits (q[0], q[1]), both measured.
3. **State evolution**:
   - Initial state: |00⟩
   - Apply CZ: The CZ gate applies Z to the target only when the control is |1⟩. Since q[0] is |0⟩, no action is taken. State remains |00⟩.
4. **Expected probabilities**: {|00⟩: 1.0} — CZ leaves |00⟩ unchanged, so measurement always yields 00.
