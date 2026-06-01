# ISQ training COT RAG corpus: gate_decomposition shard 5

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3261

- task_id: `isqTrain/3261`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `reversible_computing`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `2950`

### Prompt

Write isQ code for the following quantum task: an isQ program: apply H twice to each of 3 qubits (H*H=I), then measure. All should be |0>.

### Chain-of-thought reasoning

## Reasoning
Goal: Demonstrate that H⊗H = I by applying two Hadamard gates to each of three qubits, leaving all qubits in |0⟩.

Qubits: 3 qubits (q[0], q[1], q[2]), all measured.

State evolution:
- Initial: |000⟩
- H(q[0]): |+00⟩ = (|000⟩+|100⟩)/√2
- H(q[0]): |000⟩ (H² = I returns q[0] to |0⟩)
- H(q[1]); H(q[1]): |000⟩ (same logic)
- H(q[2]); H(q[2]): |000⟩ (same logic)

Since H is self-inverse (H·H = I), each qubit returns to |0⟩, so the final state is |000⟩ with probability 1.0.

## isqTrain/3268

- task_id: `isqTrain/3268`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `341`

### Prompt

帮我写一个isQ程序：an isQ program: apply CNOT twice on |11>. Since CNOT*CNOT=I, the state should return to |11>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Demonstrate that applying CNOT twice acts as identity (CNOT²=I), returning |11> to itself.
2. **Qubits**: 2 qubits required; both `q[0]` and `q[1]` are measured.
3. **State evolution**: |00> →(X⊗X)→ |11> →(CNOT)→ |10> →(CNOT)→ |11>
   - First CNOT: control `q[0]`=1 flips target `q[1]` from 1→0, giving |10>
   - Second CNOT: control `q[0]`=1 flips target `q[1]` from 0→1, giving |11>
4. **Expected probabilities**: {|11>: 1.0}, since the final state is exactly |11> with unit probability.

## isqTrain/1430

- task_id: `isqTrain/1430`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `isq_syntax_inv`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `703`

### Prompt

Implement a quantum circuit in isQ: Apply T then T-dagger (identity) to |+> and measure. Verify the gate identity TdagT = I.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Verify the gate identity T-dagger * T = I by applying it to the |+> state.
2. **Qubits**: 1 qubit is required and measured.
3. **State Evolution**:
   - Start in |0>, apply H to create |+> = (|0> + |1>) / sqrt(2).
   - Apply T: state becomes (|0> + exp(i*pi/4)|1>) / sqrt(2).
   - Apply T-dagger (`inv T`): cancels the relative phase shift, returning the state exactly to |+>.
4. **Probabilities**: Measuring |+> yields a 50/50 distribution {|0>: 0.5, |1>: 0.5}, confirming the identity.

## isqTrain/3159

- task_id: `isqTrain/3159`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `1146`

### Prompt

实现以下量子计算任务（使用isQ）：an isQ program: apply H, Rz(2*pi/16), H to a qubit and measure. This implements Rx(2*pi/16) via conjugation.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement $R_x(2\pi/16)$ using H-Rz-H conjugation on a single qubit and measure.
2. **Qubits**: 1 qubit needed; q[0] is measured.
3. **State evolution**:
   - Initial: $|0\rangle$
   - After H: $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$
   - After Rz($\pi/8$): $\frac{1}{\sqrt{2}}(e^{-i\pi/16}|0\rangle + e^{i\pi/16}|1\rangle)$
   - After H: $\cos(\pi/16)|0\rangle - i\sin(\pi/16)|1\rangle$
4. **Probabilities**: $P(|0\rangle) = \cos^2(\pi/16) \approx 0.9619$, $P(|1\rangle) = \sin^2(\pi/16) \approx 0.0381$.

## isqTrain/3258

- task_id: `isqTrain/3258`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1047`

### Prompt

Help me write isQ code that an isQ program: apply X twice to each of 5 qubits (X*X=I), then measure. All qubits should remain |0>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply the X gate twice to each of 5 qubits to demonstrate the identity $X \cdot X = I$, ensuring all qubits return to their initial state.
2. **Qubits**: 5 qubits are used (`q[0]` to `q[4]`), and all are measured.
3. **State evolution**: 
   - Initial state: $|00000\rangle$
   - First X gate on each qubit flips the state to $|11111\rangle$ (since $X|0\rangle = |1\rangle$).
   - Second X gate on each qubit flips the state back to $|00000\rangle$ (since $X|1\rangle = |0\rangle$).
4. **Expected probabilities**: As the final quantum state is exactly $|00000\rangle$, measurement yields the bitstring '00000' with a probability of 1.0.

## isqTrain/3370

- task_id: `isqTrain/3370`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `4026`

### Prompt

Implement a quantum circuit in isQ: an isQ program: apply H to control q[0], then ctrl Rx(pi/4) from q[0] to q[1], then measure both.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Create a superposition on q[0], then conditionally rotate q[1] via Rx(π/4), and measure both qubits.

**Qubits:** 2 (q[0], q[1]), both measured.

**State evolution:**
- **Initial:** |00⟩
- **After H(q[0]):** (|0⟩ + |1⟩)/√2 ⊗ |0⟩ = (|00⟩ + |10⟩)/√2
- **After ctrl Rx(π/4) (q[0]→q[1]):** q[1] is rotated only when q[0]=|1⟩. Rx(π/4)|0⟩ = cos(π/8)|0⟩ - i·sin(π/8)|1⟩, giving:
  (1/√2)|00⟩ + (cos(π/8)/√2)|10⟩ - i·(sin(π/8)/√2)|11⟩

**Probabilities:**
- P(|00⟩) = 1/2 = **0.5**
- P(|10⟩) = cos²(π/8)/2 ≈ **0.4268**
- P(|11⟩) = sin²(π/8)/2 ≈ **0.0732**

These sum to 1, confirming consistency.

## isqTrain/3398

- task_id: `isqTrain/3398`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `5426`

### Prompt

Code this in isQ: an isQ program: H, Rz(1*pi/4), H on a qubit. This is equivalent to Rx(1*pi/4).

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Generate a reasoning section for an isQ program applying H, Rz(1*pi/4), H to a qubit.
    *   Role: Quantum computing expert.
    *   Format Requirements: Start with "## Reasoning", use Dirac notation, NO isQ code, NO markdown code blocks for isQ, concise (3-8 lines).

2.  **Analyze the Circuit:**
    *   Initial state: $|0\rangle$
    *   Apply $H$: State becomes $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$
    *   Apply $R_z(\pi/4)$: $R_z(\theta) = e^{-i\theta/2}|0\rangle\langle0| + e^{i\theta/2}|1\rangle\langle1|$. State becomes $\frac{1}{\sqrt{2}}(e^{-i\pi/8}|0\rangle + e^{i\pi/8}|1\rangle)$.
    *   Apply $H$: State becomes $\frac{1}{2}(e^{-i\pi/8}(|0\rangle + |1\rangle) + e^{i\pi/8}(|0\rangle - |1\rangle)) = \frac{1}{2}((e^{-i\pi/8} + e^{i\pi/8})|0\rangle + (e^{-i\pi/8} - e^{i\pi/8})|1\rangle)$.
    *   Simplify using Euler's formulas: $e^{ix} + e^{-ix} = 2\cos(x)$, $e^{ix} - e^{-ix} = 2i\sin(x)$.
    *   State: $\cos(\pi/8)|0\rangle - i\sin(\pi/8)|1\rangle$. Wait, $R_x(\pi/4)$ is $\cos(\pi/8)I - i\sin(\pi/8)X$. So applying $R_x(\pi/4)$ to $|0\rangle$ gives $\cos(\pi/8)|0\rangle - i\sin(\pi/8)|1\rangle$. This matches perfectly!
    *   Probabilities: $P(|0\rangle) = |\cos(\pi/8)|^2 \approx 0.85355$. $P(|1\rangle) = |-\sin(\pi/8)|^2 \approx 0.14645$.

3.  **Draft the Reasoning (incorporating all rules):**
    *   *Goal*: Apply H, Rz(pi/4), and H gates to a single qubit, which is mathematically equivalent to an Rx(pi/4) rotation.
    *   *Qubits*: Requires 1 qubit, which is measured.
    *   *Evolution*:
        *   Start in |0>.
        *   H gate changes state to |+> = (1/sqrt(2))(|0> + |1>).
        *   Rz(pi/4) rotates phase: (1/sqrt(2))(e^{-i*pi/8}|0> + e^{i*pi/8}|1>).
        *   H gate transforms this to cos(pi/8)|0> - i*sin(pi/8)|1>, equivalent to applying Rx(pi/4).
    *   *Probabilities*: Measurement yields |0> with probability cos^2(pi/8) ≈ 0.8536, and |1> with probability sin^2(pi/8) ≈ 0.1464.

4.  **Refine and Format:**
    *   Ensure it's 3-8 lines.
    *   Check for strict compliance (NO code blocks, starts with "## Reasoning").

    ## Reasoning
    1. The goal is to apply a sequence of H, Rz(pi/4), and H gates to a single qubit, which is mathematically equivalent to an Rx(pi/4) rotation.
    2. The circuit requires 1 qubit, which is measured at the end.
    3. Starting in |0>, the first H gate puts the qubit in |+> = (1/sqrt(2))(|0> + |1>).
    4. The Rz(pi/4) gate applies a relative phase, yielding (1/sqrt(2))(e^{-i*pi/8}|0> + e^{i*pi/8}|1>).
    5. The final H gate maps this to cos(pi/8)|0> - i*sin(pi/8)|1>, exactly matching the Rx(pi/4) matrix applied to |0>.
    6

## isqTrain/3292

- task_id: `isqTrain/3292`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2088`

### Prompt

Code this in isQ: an isQ program: apply H, Rz(1*pi/8), Rz(-1*pi/8), H. Since Rz cancels, net is H*H=I.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Demonstrate that Rz(π/8) and Rz(-π/8) cancel, leaving H·H = I, so the qubit returns to |0⟩.
2. **Qubits**: 1 qubit (q[0]), which is measured.
3. **State evolution**:
   - Start: |0⟩
   - After H: |+⟩ = (|0⟩ + |1⟩)/√2
   - After Rz(π/8): global phase shift on superposition
   - After Rz(-π/8): rotations cancel exactly, state remains |+⟩
   - After H: H|+⟩ = |0⟩
4. **Result**: Since Rz(θ)·Rz(-θ) = I and H·H = I, the full circuit is identity. Measuring |0⟩ gives probability 1.0.

## isqTrain/3275

- task_id: `isqTrain/3275`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1700`

### Prompt

I need an isQ program to an isQ program: apply Ry(1*pi/4) then Ry(-1*pi/4) to cancel. Measure: should get |0>.

### Chain-of-thought reasoning

## Reasoning
The circuit demonstrates the cancellation of rotation gates by applying Ry(π/4) followed by its inverse Ry(-π/4).
It requires one qubit, q[0], which is initialized to |0> and subsequently measured.
Starting in state |0>, the first gate evolves the state to Ry(π/4)|0>.
The second gate applies the exact inverse rotation, Ry(-π/4), perfectly canceling the first operation and returning the state to |0>.
Consequently, the measurement will deterministically yield the outcome |0> with a probability of 1.0.

## isqTrain/3273

- task_id: `isqTrain/3273`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3596`

### Prompt

用isQ实现an isQ program: prepare |00> and apply SWAP using 3 CNOT gates. Verify the qubits are swapped.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply a 3-CNOT swap (three-CNOT decomposition) decomposition to the |00> state to verify the gate sequence leaves it unchanged.
Qubits: 2 qubits (q[0], q[1]), both measured.
State evolution:
- Initialize to |00>.
- CNOT(q[0], q[1]): Control q[0] is |0>, target q[1] unchanged. State remains |00>.
- CNOT(q[1], q[0]): Control q[1] is |0>, target q[0] unchanged. State remains |00>.
- CNOT(q[0], q[1]): Control q[0] is |0>, target q[1] unchanged. State remains |00>.
Probabilities: The final state is |00>, so measuring both qubits yields the bitstring 00 with a probability of 1.0.
