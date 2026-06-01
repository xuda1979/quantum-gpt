# ISQ training COT RAG corpus: gate_decomposition shard 2

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3352

- task_id: `isqTrain/3352`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `3400`

### Prompt

Implement a quantum circuit in isQ: an isQ program: apply 2-qubit gate chain H0-CNOT-H0 to |00> and measure both qubits.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Apply the gate sequence H₀–CNOT–H₀ to two qubits initialized in |00⟩, then measure both.

2. **Qubits**: 2 qubits (q[0], q[1]), both measured.

3. **State evolution**:
   - **Initial**: |00⟩
   - **H(q[0])**: (|00⟩ + |10⟩)/√2
   - **CNOT(q[0], q[1])**: (|00⟩ + |11⟩)/√2  — a Bell state
   - **H(q[0])**: Applying H to the first qubit of (|00⟩ + |11⟩)/√2 yields (|00⟩ + |01⟩ + |10⟩ − |11⟩)/2

4. **Expected probabilities**: Each computational basis state has amplitude 1/2, giving |amplitude|² = 0.25 for each of {|00⟩, |01⟩, |10⟩, |11⟩}. This is a uniform distribution over all 2-qubit states.

## isqTrain/3383

- task_id: `isqTrain/3383`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `superposition`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `245`

### Prompt

I need an isQ program to an isQ program: apply H to 2 qubits, then H again (undo), then H a third time (re-apply). Net: one H on each qubit.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply the Hadamard gate three times to two independent qubits, effectively applying it once since H^3 = H.
Qubits: 2 qubits (q[0], q[1]), both measured.
State evolution:
1. Initial state is |00>.
2. First H creates equal superposition: |++> = (1/2)(|00> + |01> + |10> + |11>).
3. Second H reverses the first, returning the state to |00>.
4. Third H recreates the equal superposition: |++>.
Final state: Both qubits are in the |+> state. Measuring this yields a 25% probability for each of the 2-qubit basis states (|00>, |01>, |10>, |11>).

## isqTrain/3124

- task_id: `isqTrain/3124`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `3562`

### Prompt

Create an isQ quantum circuit that an isQ program: apply ctrl X (=CNOT) on initial state |00> and measure both qubits.

### Chain-of-thought reasoning

## Reasoning
The goal is to apply a controlled-X (CNOT) gate to the default initial state |00> and measure both qubits.
Two qubits are required, both of which are measured at the end of the circuit.
The circuit starts in the state |00>. Since the control qubit (q[0]) is in the |0> state, the CNOT gate leaves the target qubit (q[1]) unchanged, resulting in the final state |00>.
Measuring this final state yields the bitstring 00 with a probability of 1.0.

## isqTrain/3384

- task_id: `isqTrain/3384`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `superposition`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4856`

### Prompt

Implement a quantum circuit in isQ: an isQ program: apply H to 3 qubits, then H again (undo), then H a third time (re-apply). Net: one H on each qubit.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply H three times to each of 3 qubits; since H² = I, the net effect is a single H per qubit, putting all three into equal superposition.

We need 3 qubits q[0], q[1], q[2], all measured. Initial state: |000⟩.

1. **First H on all:** |000⟩ → |+++⟩ = (1/√8)Σ|x⟩ over all 3-bit strings x.
2. **Second H on all:** H|+⟩ = |0⟩, so |+++⟩ → |000⟩ (undo the superposition).
3. **Third H on all:** |000⟩ → |+++⟩ = (1/√8)(|000⟩+|001⟩+|010⟩+|011⟩+|100⟩+|101⟩+|110⟩+|111⟩).

Measurement yields each of the 8 basis states with equal probability |1/√8|² = 1/8 = 0.125.

## isqTrain/3272

- task_id: `isqTrain/3272`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `reversible_computing`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1493`

### Prompt

Code this in isQ: an isQ program: apply CZ twice on |11>. Since CZ*CZ=I, the state returns to |11>.

### Chain-of-thought reasoning

## Reasoning
- Goal: Demonstrate that applying CZ twice acts as identity, returning |11> to itself.
- Qubits: 2 qubits (q[0], q[1]), both measured.
- State evolution:
  1. Start at |00>; apply X to both: X⊗X|00> = |11⟩
  2. First CZ on |11⟩: applies Z phase to target, yielding -|11⟩
  3. Second CZ on -|11⟩: applies another -1 phase, giving (-1)(-1)|11⟩ = |11⟩
- Expected probabilities: Final state is exactly |11⟩, so measurement yields |11⟩ with probability 1.0.

## isqTrain/3257

- task_id: `isqTrain/3257`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1663`

### Prompt

Implement a quantum circuit in isQ: an isQ program: apply X twice to each of 4 qubits (X*X=I), then measure. All qubits should remain |0>.

### Chain-of-thought reasoning

## Reasoning
Goal: Demonstrate that applying X twice to each qubit leaves the state unchanged (X²=I).

We need 4 qubits (q[0..3]), all measured at the end.

State evolution: All qubits start at |0000⟩. Each X gate flips |0⟩↔|1⟩, so applying X twice to any qubit restores it: X·X|0⟩ = I|0⟩ = |0⟩. After X(q[0]);X(q[0]) → |0000⟩. Same for q[1], q[2], q[3]: state remains |0000⟩.

Expected probabilities: Since the final state is |0000⟩, measurement yields |0000⟩ with probability 1.0.

## isqTrain/3282

- task_id: `isqTrain/3282`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2032`

### Prompt

用isQ实现an isQ program: apply Ry(7*pi/8) then Ry(-7*pi/8) to cancel. Measure: should get |0>.

### Chain-of-thought reasoning

## Reasoning
- Goal: Show that applying Ry(7π/8) then Ry(-7π/8) cancels, restoring |0⟩.
- Qubits: 1 qubit (q[0]), measured at the end.
- Evolution: |0⟩ → Ry(7π/8)|0⟩ (rotated on Y-axis) → Ry(-7π/8)Ry(7π/8)|0⟩ = I|0⟩ = |0⟩, since Ry(-θ) = Ry(θ)⁻¹.
- The two rotations cancel exactly, leaving the state |0⟩.
- Expected measurement outcome: |0⟩ with probability 1.0.

## isqTrain/3355

- task_id: `isqTrain/3355`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `1836`

### Prompt

Write isQ code for the following quantum task: an isQ program: prepare |10>, apply CNOT-CNOT-rev, measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare |10⟩, apply CNOT(q[0],q[1]) then CNOT(q[1],q[0]), and measure both qubits.
2. **Qubits**: 2 qubits q[0] and q[1], both measured.
3. **State evolution**:
   - Initialize |00⟩; X(q[0]) → |10⟩
   - CNOT(q[0],q[1]) with q[0]=|1⟩ flips q[1]: |10⟩ → |11⟩
   - CNOT(q[1],q[0]) with q[1]=|1⟩ flips q[0]: |11⟩ → |01⟩
4. **Final state**: |01⟩ → measurement yields |01⟩ with probability 1.0 (q[0]=0 is higher bit, q[1]=1 is lower bit in bitstring indexing).

## isqTrain/3335

- task_id: `isqTrain/3335`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2720`

### Prompt

Implement a quantum circuit in isQ: an isQ program: apply gate chain H-T-S to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply the gate sequence H, T, S to a single qubit initialized to |0⟩, then measure.
2. One qubit is needed (q[0]) and it is measured.
3. State evolution:
   - Initial: |0⟩
   - After H: |+⟩ = (1/√2)(|0⟩ + |1⟩)
   - After T: (1/√2)(|0⟩ + e^(iπ/4)|1⟩)
   - After S: (1/√2)(|0⟩ + e^(i3π/4)|1⟩)
4. Measurement probabilities: P(|0⟩) = |1/√2|² = 0.5, P(|1⟩) = |e^(i3π/4)/√2|² = 0.5. The phases accumulated by T and S do not affect probabilities, giving a uniform 50/50 distribution.

## isqTrain/1701

- task_id: `isqTrain/1701`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `496`

### Prompt

Implement the following in isQ: Verify the gate identity ZXZ = -X by applying the gate sequence to a qubit and measuring.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Verify the identity ZXZ = -X by applying this sequence to |0⟩ and showing it produces -|1⟩ ≡ |1⟩.
2. **Qubits**: 1 qubit, measured at the end.
3. **State evolution**:
   - Initial: |0⟩
   - Z(q): Z|0⟩ = |0⟩
   - X(q): X|0⟩ = |1⟩
   - Z(q): Z|1⟩ = -|1⟩
4. **Expected probabilities**: The final state -|1⟩ is physically equivalent to |1⟩ (global phase), so measurement yields {|1⟩: 1.0}.
