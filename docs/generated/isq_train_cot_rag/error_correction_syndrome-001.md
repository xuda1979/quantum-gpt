# ISQ training COT RAG corpus: error_correction_syndrome shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3094

- task_id: `isqTrain/3094`
- task_type: `code_generation`
- category: `error_correction_syndrome`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `ancilla_usage`
- source: `isq_train_cot`
- dataset_index: `2286`

### Prompt

Code this in isQ: an isQ program: 5-qubit bit-flip repetition code encoding logical |0>. Use CNOT from q[0] to all others.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Encode logical $|0\rangle$ into a 5-qubit bit-flip repetition code state $|00000\rangle$ using CNOT fan-out.
2. **Qubits**: 5 qubits `q[0]` to `q[4]`, all initialized to $|0\rangle$. All are measured.
3. **State Evolution**:
   - Initial state: $|00000\rangle$
   - Since control qubit `q[0]` is $|0\rangle$, each `CNOT(q[0], q[i])` leaves target `q[i]` unchanged (flips only if control is $|1\rangle$).
   - After all CNOTs, state remains $|00000\rangle$.
4. **Probabilities**: Measurement yields $|00000\rangle$ with probability 1.0, matching the desired logical $|0\rangle$ encoding.

## isqTrain/3093

- task_id: `isqTrain/3093`
- task_type: `code_generation`
- category: `error_correction_syndrome`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `ancilla_usage`
- source: `isq_train_cot`
- dataset_index: `3900`

### Prompt

I need an isQ program to an isQ program: 4-qubit bit-flip repetition code encoding logical |0>. Use CNOT from q[0] to all others.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Encode logical |0> into a 4-qubit bit-flip repetition code, mapping |0> → |0000>.
2. **Qubits**: 4 qubits (q[0]–q[3]), all measured at the end.
3. **State evolution**:
   - Initialize: |ψ₀⟩ = |0000⟩ (all qubits in |0⟩)
   - CNOT(q[0], q[1]): control q[0]=|0⟩, so target unchanged → |0000⟩
   - CNOT(q[0], q[2]): control q[0]=|0⟩, so target unchanged → |0000⟩
   - CNOT(q[0], q[3]): control q[0]=|0⟩, so target unchanged → |0000⟩
4. **Expected probabilities**: The final state is |0000⟩, so measurement always yields `0000` with probability 1.0. The CNOT fan-out only propagates a |1⟩ on the control; since q[0] starts in |0⟩, all targets remain |0⟩, giving the trivial encoding |0⟩_L = |0000⟩.

## isqTrain/3095

- task_id: `isqTrain/3095`
- task_type: `code_generation`
- category: `error_correction_syndrome`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `basis_change`, `ancilla_usage`
- source: `isq_train_cot`
- dataset_index: `5269`

### Prompt

Create an isQ quantum circuit that an isQ program: 3-qubit phase-flip code encoding logical |->. Apply H, then CNOT fan-out, then H on all 3.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Encode logical |-> into a 3-qubit phase-flip code by applying H, CNOT fan-out, then H on all qubits.

**Qubits:** 3 qubits (q[0], q[1], q[2]), all measured.

**State evolution:**
1. |000⟩ → X(q[0]) → |100⟩
2. H(q[0]) → (|000⟩ - |100⟩)/√2 = (|0⟩ - |1⟩)₀|00⟩₁₂/√2
3. CNOT(q[0], q[1]) → (|00⟩ - |11⟩)₀₁|0⟩₂/√2
4. CNOT(q[0], q[2]) → (|000⟩ - |111⟩)/√2 (GHZ state)
5. H(q[0]), H(q[1]), H(q[2]) → (|+++⟩ - |---⟩)/√2

**Expanding:** |+++⟩ - |---⟩ = (1/√2)(|001⟩ + |010⟩ + |100⟩ + |111⟩), giving final state (1/2)(|001⟩ + |010⟩ + |100⟩ + |111⟩).

**Expected probabilities:** Each of the four basis states |001⟩, |010⟩, |100⟩, |111⟩ has amplitude 1/2, yielding probability |1/2|² = 0.25 each. These are the odd-weight bitstrings — the signature of logical |-> in the phase-flip code.
