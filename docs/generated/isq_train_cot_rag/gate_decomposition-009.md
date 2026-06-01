# ISQ training COT RAG corpus: gate_decomposition shard 9

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3266

- task_id: `isqTrain/3266`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1246`

### Prompt

Code this in isQ: an isQ program: apply CNOT twice on |00>. Since CNOT*CNOT=I, the state should return to |00>.

### Chain-of-thought reasoning

## Reasoning
Goal: Demonstrate that applying CNOT twice is equivalent to the identity operation, returning the state to |00>.
Two qubits are needed (q[0], q[1]), both measured at the end.
Initial state: |00>. First CNOT(q[0], q[1]): control is |0>, target unchanged → |00>. Second CNOT(q[0], q[1]): same → |00>.
Since CNOT² = I, the final state is |00>, yielding measurement probability {|00>: 1.0}.

## isqTrain/3277

- task_id: `isqTrain/3277`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2897`

### Prompt

Write isQ code for the following quantum task: an isQ program: apply Ry(1*pi/6) then Ry(-1*pi/6) to cancel. Measure: should get |0>.

### Chain-of-thought reasoning

## Reasoning
Goal: Demonstrate perfect state cancellation by applying two inverse Ry rotations to a single qubit.
We need 1 qubit, `q[0]`, which is measured.
Starting in the initial state |0>, the first gate Ry(pi/6) rotates it to cos(pi/12)|0> + sin(pi/12)|1>.
The second gate Ry(-pi/6) exactly reverses this rotation, returning the qubit to the |0> state.
Because the final state is purely |0>, measurement yields |0> with a probability of 1.0.

## isqTrain/3263

- task_id: `isqTrain/3263`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `reversible_computing`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `1218`

### Prompt

Implement the following in isQ: an isQ program: apply H twice to each of 5 qubits (H*H=I), then measure. All should be |0>.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply H twice to each of 5 qubits (H² = I) and measure; all qubits return to |0⟩.
Qubits: 5 qubits q[0]–q[4], all measured.
State evolution for each qubit: |0⟩ →(H)→ |+⟩ = (|0⟩+|1⟩)/√2 →(H)→ |0⟩, since H² = I.
After both H gates, the full state is |00000⟩ with probability 1.
Measurement yields |00000⟩ with certainty: {|00000⟩: 1.0}.

## isqTrain/3375

- task_id: `isqTrain/3375`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `4367`

### Prompt

请用isQ语言编写一个量子电路：an isQ program: apply H to control q[0], then ctrl Ry(pi/6) from q[0] to q[1], then measure both.

### Chain-of-thought reasoning

## Reasoning
Goal: Create superposition on q[0], conditionally rotate q[1] via controlled-Ry, and measure both.
We need 2 qubits, q[0] and q[1], both measured.
Initial state is |00>. Applying H to q[0] yields: 1/√2 |00> + 1/√2 |10>.
Applying controlled-Ry(π/6) (with q[0] as control, q[1] as target) rotates the target only when q[0] is |1>.
State evolves to: 1/√2 |00> + cos(π/12)/√2 |10> + sin(π/12)/√2 |11>.
Measurement probabilities follow from the squared amplitudes: P(|00⟩) = 0.5, P(|10⟩) = cos²(π/12)/2 ≈ 0.4665, and P(|11⟩) = sin²(π/12)/2 ≈ 0.0335.

## isqTrain/3278

- task_id: `isqTrain/3278`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1148`

### Prompt

Implement the following in isQ: an isQ program: apply Ry(1*pi/8) then Ry(-1*pi/8) to cancel. Measure: should get |0>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Demonstrate the cancellation of two opposite Y-rotations on a single qubit.
2. **Qubits**: 1 qubit (`q[0]`) is used and measured.
3. **State Evolution**:
   - Initialize to |0⟩.
   - Apply `Ry(π/8)`: State becomes `cos(π/16)|0⟩ + sin(π/16)|1⟩`.
   - Apply `Ry(-π/8)`: Rotations are additive (`Ry(θ2) * Ry(θ1) = Ry(θ1 + θ2)`), resulting in a net zero rotation. State returns to |0⟩.
4. **Probabilities**: The final state is exactly |0⟩, yielding a 100% probability of measuring 0.

## isqTrain/3415

- task_id: `isqTrain/3415`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `5807`

### Prompt

Create an isQ quantum circuit that an isQ program: H, Rz(6*pi/7), H on a qubit. This is equivalent to Rx(6*pi/7).

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply the sequence H, Rz(6π/7), H to a single qubit, demonstrating the identity H·Rz(θ)·H = Rx(θ).
2. **Qubits**: One qubit `q[0]`, which is measured.
3. **State evolution**:
   - Initial: |0⟩
   - H → |+⟩ = (|0⟩ + |1⟩)/√2
   - Rz(6π/7) → (e^{-i3π/7}|0⟩ + e^{i3π/7}|1⟩)/√2
   - H → cos(3π/7)|0⟩ - i·sin(3π/7)|1⟩ (equivalent to Rx(6π/7)|0⟩)
4. **Probabilities**: P(|0⟩) = cos²(3π/7) ≈ 0.0495, P(|1⟩) = sin²(3π/7) ≈ 0.9505, matching the predicted output.

## isqTrain/3281

- task_id: `isqTrain/3281`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4657`

### Prompt

用isQ实现an isQ program: apply Ry(5*pi/6) then Ry(-5*pi/6) to cancel. Measure: should get |0>.

### Chain-of-thought reasoning

## Reasoning
* **Goal:** Apply an $R_y$ rotation and its exact inverse to verify that they cancel out, leaving the initial state unchanged.
* **Qubits:** 1 qubit (`q[0]`), initialized to $|0\rangle$ and measured at the end.
* **State Evolution:**
  1. The qubit begins in the initial state $|0\rangle$.
  2. Apply $R_y(5\pi/6)$, rotating the state around the Y-axis of the Bloch sphere to $\cos(5\pi/12)|0\rangle + \sin(5\pi/12)|1\rangle$.
  3. Apply $R_y(-5\pi/6)$, which exactly reverses the previous rotation. Mathematically, $R_y(-5\pi/6) R_y(5\pi/6) = I$ (Identity).
  4.

## isqTrain/1429

- task_id: `isqTrain/1429`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `87`

### Prompt

Create an isQ quantum circuit that Apply S twice (equivalent to Z) to |+> state and measure. Verify the gate identity ZSS = I on |+>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply S twice to |+⟩ and measure to verify Z = S² identity (since ZSS = I implies SS = Z⁻¹ = Z on |+⟩).
2. **Qubits**: 1 qubit, measured at the end.
3. **State evolution**:
   - Initialize |0⟩; apply H → |+⟩ = (1/√2)(|0⟩ + |1⟩)
   - Apply S: |+⟩ → (1/√2)(|0⟩ + i|1⟩)
   - Apply S again: → (1/√2)(|0⟩ + i²|1⟩) = (1/√2)(|0⟩ - |1⟩) = |-⟩ = Z|+⟩
   - Measure: |⟨0|−⟩|² = 0.5, |⟨1|−⟩|² = 0.5
4. **Expected probabilities**: {|0⟩: 0.5, |1⟩: 0.5} — since |-⟩ is an equal superposition, measurement yields uniform distribution, confirming S² = Z transforms |+⟩ to |-⟩.

## isqTrain/3373

- task_id: `isqTrain/3373`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `2183`

### Prompt

Create an isQ quantum circuit that an isQ program: apply H to control q[0], then ctrl Ry(pi/2) from q[0] to q[1], then measure both.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: The circuit prepares a superposition on q[0], then applies a controlled-Ry rotation from q[0] to q[1], and measures both.
2. **Qubits**: 2 qubits, q[0] and q[1], both measured.
3. **State evolution**:
   - Initial state: $|00\rangle$
   - `H(q[0])`: $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$
   - `ctrl Ry(pi/2, q[0], q[1])`: Applies $R_y(\pi/2)$ to q[1] if q[0] is $|1\rangle$. Since $R_y(\pi/2)|0\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$, the state becomes $\frac{1}{\sqrt{2}}|00\rangle + \frac{1}{2}|10\rangle + \frac{1}{2}|11\rangle$.
4. **Probabilities**: Measuring gives $|00\rangle$ with probability $|\frac{1}{\sqrt{2}}|^2 = 0.5$, $|10\rangle$ with probability $|\frac{1}{2}|^2 = 0.25$, and $|11\rangle$ with probability $0.25$.

## isqTrain/1

- task_id: `isqTrain/1`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `73`

### Prompt

Code this in isQ: implements a variant of the gate_decomposition pattern using q[2] -> q[4]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a swap gate on qubits 0 and 1 using three CNOT gates, with an expanded 4-qubit register where q[2] and q[3] remain untouched in the ground state.

2. **Qubits**: 4 qubits (q[0] through q[3]), all measured at the end.

3. **State evolution**:
   - Initial: |0000⟩
   - X(q[1]): |0100⟩ (qubit 1 flipped to |1⟩)
   - CNOT(q[0], q[1]): |0100⟩ (control q[0]=0, no change)
   - CNOT(q[1], q[0]): |1100⟩ (control q[1]=1, flips q[0])
   - CNOT(q[0], q[1]): |1000⟩ (control q[0]=1, flips q[1] back)
   - Final state: |1000⟩

4. **Expected probabilities**: The swap gate exchanges |0⟩↔|1⟩ between q[0] and q[1]. Starting from |01⟩, after swap we get |10⟩. Qubits q[2] and q[3] remain |00⟩ throughout since no gates act on them. Hence |1000⟩ has probability 1.0.
