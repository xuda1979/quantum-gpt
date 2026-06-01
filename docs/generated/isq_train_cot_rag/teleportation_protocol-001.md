# ISQ training COT RAG corpus: teleportation_protocol shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3118

- task_id: `isqTrain/3118`
- task_type: `code_generation`
- category: `teleportation_protocol`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `5465`

### Prompt

Write an isQ program that an isQ program: teleport state |0> from q[0] to q[2] using q[1] as entanglement partner. Simplified: just create Bell pair between q[1] and q[2], then CNOT(q[0],q[1]) and H(q[0]), measure all 3.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Teleport state |0⟩ from q[0] to q[2] using standard teleportation protocol with q[1] as entanglement partner.

**Qubits:** 3 qubits (q[0], q[1], q[2]), all measured.

**State evolution:**
1. **Initial:** |000⟩
2. **H(q[1]):** |0⟩⊗(|0⟩+|1⟩)/√2⊗|0⟩ = (|000⟩+|010⟩)/√2
3. **CNOT(q[1],q[2]):** (|000⟩+|011⟩)/√2 — Bell pair (Φ⁺) created between q[1] and q[2]
4. **CNOT(q[0],q[1]):** State unchanged since q[0]=|0⟩; remains (|000⟩+|011⟩)/√2
5. **H(q[0]):** → (|000⟩+|100⟩+|011⟩+|111⟩)/2

**Probabilities:** The final state is an equal superposition of four computational basis states (|000⟩, |100⟩, |011⟩, |111⟩), each with amplitude 1/2, yielding probability 0.25 for each outcome.

## isqTrain/3396

- task_id: `isqTrain/3396`
- task_type: `code_generation`
- category: `teleportation_protocol`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `2188`

### Prompt

Implement a quantum circuit in isQ: an isQ program: quantum teleportation circuit for |+>. q[0]=state to teleport, q[1]-q[2]=Bell pair. Create Bell pair, do Bell measurement (CNOT+H), measure all 3.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Teleport the |+> state from q[0] to q[2] using a Bell pair on q[1]-q[2], then measure all qubits.

**Qubits:** 3 (q[0], q[1], q[2]), all measured.

**State evolution:**
1. **Initial:** |000⟩
2. **H(q[0]):** |+00⟩ = (1/√2)(|000⟩ + |100⟩)
3. **H(q[1]):** (1/2)(|000⟩ + |010⟩ + |100⟩ + |110⟩)
4. **CNOT(q[1],q[2]):** (1/2)(|000⟩ + |011⟩ + |100⟩ + |111⟩) — Bell pair entangles q[1]-q[2]
5. **CNOT(q[0],q[1]):** (1/2)(|000⟩ + |011⟩ + |110⟩ + |101⟩)
6. **H(q[0]):** (1/2√2)(|000⟩+|001⟩+|010⟩+|011⟩+|100⟩+|101⟩+|110⟩+|111⟩) — all eight basis states with equal amplitude

**Probabilities:** Each of the 8 computational basis states has amplitude 1/(2√2), giving equal probability (1/8 = 0.125) for each outcome, consistent with the expected uniform distribution.
