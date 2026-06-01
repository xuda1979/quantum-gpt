# ISQ training COT RAG corpus: graph_state_preparation shard 2

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3099

- task_id: `isqTrain/3099`
- task_type: `code_generation`
- category: `graph_state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`, `entanglement`
- source: `isq_train_cot`
- dataset_index: `4809`

### Prompt

Code this in isQ: preparing a 3-qubit star graph state with q[0] as center. Apply H to all, CZ from center to leaves, measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Prepare a 3-qubit star graph state with q[0] as the center and leaves q[1], q[2], then measure all qubits.
2. **Qubits:** 3 qubits are allocated (q[0], q[1], q[2]), and all are measured at the end.
3. **Evolution:** 
   - Start in |000⟩. Applying H to all qubits creates an equal superposition: |+⟩|+⟩|+⟩ = 1/√8 ∑_{x∈{0,1}³} |x⟩.
   - Apply CZ(q[0], q[1]): adds a -1 phase when both q[0] and q[1] are |1⟩.
   - Apply CZ(q[0], q[2]): adds a -1 phase when both q[0] and q[2] are |1⟩.
   - The final state is the star graph state: 1/√8 (|000⟩+|001⟩+|010⟩+|011⟩+|100⟩-|101⟩-|110⟩+|111⟩).
4. **Probabilities:** Because the state is an equal superposition of all 8 computational basis states (with phases ±1), the measurement probability for every basis state is |1/√8|² = 0.125.
