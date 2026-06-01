# ISQ training COT RAG corpus: key_distribution shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3237

- task_id: `isqTrain/3237`
- task_type: `code_generation`
- category: `key_distribution`
- difficulty: `basic`
- concept_tags: `basis_change`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1396`

### Prompt

Write an isQ program that an isQ program: 4-qubit BB84 with all X-basis matching. Prepare all qubits with H (X-basis), measure in X-basis (H then M). Since H*H=I, all qubits measure |0>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Simulate BB84 protocol with 4 qubits where Alice prepares in X-basis and Bob measures in X-basis (matching).
2. **Qubits**: 4 qubits q[0..3], all measured.
3. **State evolution**:
   - Start: |0000⟩
   - Alice's H gates: |0000⟩ → |++++⟩ (each |0⟩ → |+⟩ = (|0⟩+|1⟩)/√2)
   - Bob's H gates: |++++⟩ → |0000⟩ (H² = I on each qubit, H|+⟩ = |0⟩)
4. **Expected result**: Final state |0000⟩, so measurement yields 0000 with probability 1.0.

## isqTrain/3236

- task_id: `isqTrain/3236`
- task_type: `code_generation`
- category: `key_distribution`
- difficulty: `basic`
- concept_tags: `basis_change`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5198`

### Prompt

Help me write isQ code that an isQ program: 3-qubit BB84 with all X-basis matching. Prepare all qubits with H (X-basis), measure in X-basis (H then M). Since H*H=I, all qubits measure |0>.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Simulate 3-qubit BB84 where Alice prepares and Bob measures in matching X-basis, yielding deterministic outcomes.
2. Qubits: 3 (q[0], q[1], q[2]), all measured.
3. State evolution:
   - Initial: |000⟩
   - Alice's H gates: |000⟩ → H⊗3|000⟩ = |+++⟩
   - Bob's H gates: |+++⟩ → H⊗3|+++⟩ = |000⟩ (since H² = I)
4. Expected: Since H is self-inverse, H|+⟩ = H(H|0⟩) = |0⟩, so all qubits return to |0⟩, yielding P(|000⟩) = 1.0.
