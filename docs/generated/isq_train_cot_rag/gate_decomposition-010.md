# ISQ training COT RAG corpus: gate_decomposition shard 10

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3288

- task_id: `isqTrain/3288`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1114`

### Prompt

用isQ实现an isQ program: apply Rx(3*pi/4) then Rx(-3*pi/4) to cancel. Measure: should get |0>.

### Chain-of-thought reasoning

## Reasoning
1.  **Goal**: Apply two opposite X-axis rotations to demonstrate cancellation and measure $|0\rangle$.
2.  **Qubits**: Requires 1 qubit (`q[0]`) initialized to $|0\rangle$, which is then measured.
3.  **State Evolution**:
    *   Start with initial state $|0\rangle$.
    *   Apply $R_x(3\pi/4)$, rotating the state vector on the X-axis.
    *   Apply $R_x(-3\pi/4)$, which is the inverse of the previous gate, perfectly undoing the rotation.
    *   The final state is exactly restored to $|0\rangle$ (up to a global phase).
4.  **Probabilities**: Since the final quantum state is $|0\rangle$, measuring the qubit yields the outcome 0 with a probability of 1.0.

## isqTrain/3400

- task_id: `isqTrain/3400`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `5001`

### Prompt

Write isQ code for the following quantum task: an isQ program: H, Rz(1*pi/6), H on a qubit. This is equivalent to Rx(1*pi/6).

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply H*Rz(π/6)*H to a single qubit, equivalent to Rx(π/6).
2. One qubit needed, q[0] is measured.
3. State evolution: |0⟩ → H → |+⟩ = (|0⟩+|1⟩)/√2 → Rz(π/6) → (|0⟩ + e^(iπ/6)|1⟩)/√2 → H → (cos(π/12)|0⟩ - i·sin(π/12)|1⟩).
4. Measurement probabilities: P(|0⟩) = cos²(π/12) ≈ 0.933, P(|1⟩) = sin²(π/12) ≈ 0.067.

## isqTrain/3

- task_id: `isqTrain/3`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `407`

### Prompt

请用isQ语言编写一个量子电路：implements the gate_decomposition pattern using an alternative gate decomposition (CNOT -> H CZ H). The circuit must produce the same output as the standard decomposition.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

The circuit implements a swap operation (three-CNOT decomposition) using CZ gates instead of CNOT gates, leveraging the decomposition CNOT = H(target) CZ(control, target) H(target).

Initial state: |00⟩
After X(q[1]): |01⟩ (q[1] is flipped)

Now let's trace through the swap_gate procedure:

1. H(b) where b=q[1]: |01⟩ → |0⟩⊗|+⟩ = (|00⟩ + |01⟩)/√2

2. CZ(a, b) where a=q[0], b=q[1]: CZ applies Z to target when control is |1⟩
   (|00⟩ + |01⟩)/√2 → (|00⟩ - |01⟩)/√2 = |0⟩⊗|−⟩

3. H(b): |0⟩⊗|−⟩ = (|00⟩ - |01⟩)/√2 → |01⟩ (since H|−⟩ = |1⟩)
   Wait, let me recalculate. H|+⟩ = |0⟩, H|−⟩ = |1⟩
   
   State after step 2: (|00⟩ - |01⟩)/√2 = |0⟩⊗|−⟩
   After H(b): |0⟩⊗(H|−⟩) = |0⟩⊗|1⟩ = |01⟩

So the first CNOT decomposition (with q[0] as control, q[1] as target) maps |01⟩ → |01⟩ (target flips when control is |1⟩, but here control is |0⟩).

Wait, let me re-check. The original swap (three-CNOT decomposition) using CNOTs is:
CNOT(a,b) → CNOT(b,a) → CNOT(a,b)

Let me trace through more carefully.

Starting state after X(q[1]): |01⟩

**First CNOT(a,b) decomposition: H(b), CZ(a,b), H(b)**

State: |01⟩
H(b): |0⟩⊗H|1⟩ = |0⟩⊗|−⟩ = (|00⟩ - |01⟩)/√2
CZ(a,b): Since control q[0]=|0⟩, no phase applied → (|00⟩ - |01⟩)/√2
H(b): |0⟩⊗H|−⟩ = |0⟩⊗|1⟩ = |01⟩

So after first CNOT(a,b): |01⟩

In standard CNOT(a,b), since control a=|0⟩, target b stays the same: |01⟩ → |01⟩. ✓

**Second CNOT(b,a) decomposition: H(a), CZ(b,a), H(a)**

State: |01⟩
H(a): H|0⟩⊗|1⟩ = |+⟩⊗|1⟩ = (|01⟩ + |11⟩)/√2
CZ(b,a): Control is b, target is a. When b=|1⟩, apply Z to a.
  |01⟩ → -|01⟩? No wait, let me think about this more carefully.
  
  CZ(control, target): applies Z to target when control is |1⟩
  CZ(b,a): control=b, target=a
  
  (|01⟩ + |11⟩)/√2
  - |01⟩: b=0, so no Z applied to a → |01⟩
  - |11⟩: b=1, so Z applied to a: Z|1⟩ = -|1⟩ → -|11⟩
  
  Result: (|01⟩ - |11⟩)/√2 = |1⟩⊗|−⟩

Wait, that doesn't look right. Let me re-index. q[0]=a, q[1]=b.

State: |01⟩ means q[0]=0, q[1]=1.

H(a) where a=q[0]: H on q[0]
|01⟩ → (|01⟩ + |11⟩)/√2

CZ(b,a) where b=q[1] is control, a=q[0] is target:
When q[1]=1, apply Z to q[0].

(|01⟩ + |11⟩)/√2:
- |01⟩: q[1]=1, apply Z to q[0]: Z|0⟩ = |0⟩ → |01⟩
- |11⟩: q[1]=1, apply Z to q[0]: Z|1⟩ = -|1⟩ → -|11⟩

Result: (|01⟩ - |11⟩)/√2

H(a): Apply H to q[0]
(|01⟩ - |11⟩)/√2 = (|0⟩ - |1⟩)/√2 ⊗ |1⟩ = |−⟩⊗|1⟩

H|−⟩ =

## isqTrain/3374

- task_id: `isqTrain/3374`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `3891`

### Prompt

用isQ实现an isQ program: apply H to control q[0], then ctrl Rx(pi/2) from q[0] to q[1], then measure both.

### Chain-of-thought reasoning

## Reasoning
1. The goal is to initialize q[0] in superposition, apply a controlled Rx(π/2) to entangle it with q[1], and measure both.
2. The circuit requires 2 qubits, both of which are measured at the end.
3. Starting in |00>, the H gate on q[0] creates the state (|00> + |10>) / √2.
4. The controlled Rx(π/2) gate applies Rx(π/2) to q[1] only when q[0] is |1>, evolving the state to (|00> + (|10> - i|11>)/√2) / √2 = |00>/√2 + |10>/2 - i|11>/2.
5. Measuring both qubits yields probabilities based on the squared amplitudes: P(|00>) = 0.5, P(|10>) = 0.25, and P(|11>) = 0.25.

## isqTrain/1336

- task_id: `isqTrain/1336`
- task_type: `output_prediction`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_procedures`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5164`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[3];

procedure swap_gate(qbit a, qbit b) {
    CNOT(a, b);
    CNOT(b, a);
    CNOT(a, b);
}

procedure main() {
    X(q[1]);
    swap_gate(q[0], q[1]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations:** The circuit initializes 3 qubits in |000>. An X gate is applied to q[1]. Then, a swap operation (three-CNOT decomposition) (implemented via three CNOTs) is applied between q[0] and q[1]. Finally, all three qubits are measured.
2. **State Evolution:**
    - Initial state: |000>
    - After X

### Reference answer

{'predicted_probs': {'4': 1.0}, 'explanation': 'Parametric variant of isqEval/484. Dimension: qubit_variant: q[2] -> q[3].'}

## isqTrain/3411

- task_id: `isqTrain/3411`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `2460`

### Prompt

Implement the following in isQ: an isQ program: H, Rz(4*pi/7), H on a qubit. This is equivalent to Rx(4*pi/7).

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply a sequence of H, Rz(4π/7), and H gates to a single qubit, which is mathematically equivalent to an Rx(4π/7) rotation.
2. **Qubits**: Requires 1 qubit, which is measured at the end.
3. **State Evolution**:
   - Initialize the qubit to |0⟩.
   - Apply **H**: Transforms the state to |+⟩ = (|0⟩ + |1⟩)/√2.
   - Apply **Rz(4π/7)**: Rotates the phase of |1⟩ by e^(i4π/7), changing the state to (|0⟩ + e^(i4π/7)|1⟩)/√2.
   - Apply **H**: Maps the state to 0.5(1 + e^(i4π/7))|0⟩ + 0.5(1 - e^(i4π/7))|1⟩.
4. **Probabilities**: 
   - P(|0⟩) = |0.5(1 + e^(i4π/7))|² = (1 + cos(4π/7

## isqTrain/3285

- task_id: `isqTrain/3285`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4292`

### Prompt

Help me write isQ code that an isQ program: apply Rx(1*pi/6) then Rx(-1*pi/6) to cancel. Measure: should get |0>.

### Chain-of-thought reasoning

## Reasoning
The goal is to demonstrate Rx gate cancellation by applying two inverse rotations to a single qubit.
We need one qubit (`q[0]`) initialized to $|0\rangle$, which will be measured at the end.
Applying $R_x(\pi/6)$ rotates the state around the X-axis, but the following $R_x(-\pi/6)$ exactly reverses this transformation.
Because $R_x(-\pi/6) R_x(\pi/6) = I$, the net effect is the identity, leaving the system perfectly in the initial state $|0\rangle$.
Therefore, the measurement probabilities are exactly $\{|0\rangle: 1.0\}$.

## isqTrain/3280

- task_id: `isqTrain/3280`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2193`

### Prompt

Code this in isQ: an isQ program: apply Ry(3*pi/4) then Ry(-3*pi/4) to cancel. Measure: should get |0>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Apply two inverse rotation gates to demonstrate their cancellation, resulting in the initial quantum state.
2. **Qubits:** 1 qubit (`q[0]`) is required and measured.
3. **State evolution:** 
   - Initialize to `|0>`.
   - Apply `Ry(3*pi/4)`: rotates the state around the Y-axis by `3*pi/4`.
   - Apply `Ry(-3*pi/4)`: applies the exact inverse rotation, perfectly undoing the previous gate.
4. **Probabilities:** The two rotations combine to an identity operation, returning the state to `|0>`. Thus, measurement yields `|0>` with 100% probability.

## isqTrain/3336

- task_id: `isqTrain/3336`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2217`

### Prompt

I need an isQ program to an isQ program: apply gate chain T-S-H to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply the gate sequence T, then S, then H to a single qubit initialized to |0⟩, then measure it.
2. **Qubits**: 1 qubit is needed and is measured.
3. **State evolution**:
   - Start: |0⟩
   - T|0⟩ = |0⟩ (T is diagonal; eigenvalue for |0⟩ is 1)
   - S|0⟩ = |0⟩ (S is diagonal; eigenvalue for |0⟩ is 1)
   - H|0⟩ = (|0⟩ + |1⟩)/√2 = |+⟩
4. **Expected probabilities**: The final state |+⟩ has equal amplitude on |0⟩ and |1⟩, giving P(|0⟩) = 0.5 and P(|1⟩) = 0.5.

## isqTrain/3264

- task_id: `isqTrain/3264`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2397`

### Prompt

Write an isQ program that an isQ program: demonstrate Z = S*S identity. Apply H, then S, then S, then H to a qubit. H*Z*H = X, so result should be |1>.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Demonstrate the Z = S*S identity by applying H, S, S, H to transform |0> into |1>.
2. One qubit is needed, and it is measured.
3. State evolution: 
   - Initial state is |0>.
   - Apply H: state becomes |+>.
   - Apply S twice: since S*S = Z, the state becomes Z|+> = |->.
   - Apply H: state becomes H|-> = |1>.
4. Expected measurement probabilities: The final state is exactly |1>, so measuring the qubit yields |1> with probability 1.0.
