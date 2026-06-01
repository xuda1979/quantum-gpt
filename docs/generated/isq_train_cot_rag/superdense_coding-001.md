# ISQ training COT RAG corpus: superdense_coding shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3253

- task_id: `isqTrain/3253`
- task_type: `code_generation`
- category: `superdense_coding`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `1689`

### Prompt

Implement a quantum circuit in isQ: an isQ program: superdense coding using |Psi+> resource state to send message '11'.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Implement superdense coding to transmit the classical message '11' using a |Ψ+⟩ Bell state as the shared resource.

**Qubits:** 2 global qubits `q[2]`, both measured (`M(q[0]); M(q[1])`).

**State evolution:**
1. **|00⟩** — initial state
2. **H(q[0])** → (|00⟩ + |10⟩)/√2
3. **CNOT(q[0],q[1])** → (|00⟩ + |11⟩)/√2 = |Φ+⟩
4. **X(q[1])** → (|01⟩ + |10⟩)/√2 = |Ψ+⟩ (desired resource state)
5. **X(q[0])** (Alice encodes) → (|11⟩ + |00⟩)/√2
6. **Z(q[0])** → (−|11⟩ + |00⟩)/√2
7. **CNOT(q[0],q[1])** (Bob decodes) → (−|10⟩ + |00⟩)/√2
8. **H(q[0

## isqTrain/3252

- task_id: `isqTrain/3252`
- task_type: `code_generation`
- category: `superdense_coding`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `2833`

### Prompt

请用isQ语言编写一个量子电路：an isQ program: superdense coding using |Psi+> resource state to send message '01'.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement superdense coding to send classical message '01' using the |Ψ+⟩ Bell state as the shared resource.
2. **Qubits**: 2 qubits (q[0] is sender/Alice, q[1] is receiver/Bob); both are measured.
3. **State evolution**:
   - Start: |00⟩
   - H(q[0]): |+0⟩ = (|00⟩ + |10⟩)/√2
   - CNOT(q[0], q[1]): (|00⟩ + |11⟩)/√2 = |Φ+⟩
   - X(q[1]): (|01⟩ + |10⟩)/√2 = |Ψ+⟩ (resource state created)
   - X(q[0]) encoding '01': (|11⟩ + |00⟩)/√2 = |Φ+⟩
   - CNOT(q[0], q[1]) decode: (|00⟩ + |10⟩)/√2 = |+0⟩
   - H(q[0]) decode: |00⟩
4. **Expected probabilities**: Final state is |00⟩, yielding measurement outcome |00⟩ with probability 1.0.
