# ISQ training COT RAG corpus: swap_test shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3330

- task_id: `isqTrain/3330`
- task_type: `code_generation`
- category: `swap_test`
- difficulty: `difficult`
- concept_tags: `entanglement`, `multi_controlled_logic`, `interference`
- source: `isq_train_cot`
- dataset_index: `3332`

### Prompt

用isQ实现an isQ program: SWAP test between |1> and |1>. q[0]=ancilla, q[1]=state A, q[2]=state B. H on ancilla, controlled-SWAP, H on ancilla, measure ancilla.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Perform a swap (three-CNOT decomposition) test between two identical |1⟩ states; identical states should yield ancilla measurement |0⟩ with certainty.
2. **Qubits**: 3 qubits (q[0]=ancilla, q[1]=state A, q[2]=state B); all 3 measured.
3. **State evolution**:
   - Initialize: X(q[1]), X(q[2]) → |011⟩
   - H(q[0]): 1/√2(|0⟩+|1⟩)⊗|11⟩ = 1/√2(|011⟩+|111⟩)
   - Controlled-swap (three-CNOT decomposition): swapping |11⟩→|11⟩ (no change since both qubits identical) → 1/√2(|011⟩+|111⟩)
   - H(q[0]): 1/2(|011⟩+|111⟩+|011⟩-|111⟩) = |011⟩
4. **Result**: Final state is exactly |011⟩, so measurement yields |011⟩ with probability 1.0. The ancilla (q[0]) is |0⟩, confirming the two states are identical (overlap = 1).

## isqTrain/3329

- task_id: `isqTrain/3329`
- task_type: `code_generation`
- category: `swap_test`
- difficulty: `difficult`
- concept_tags: `entanglement`, `multi_controlled_logic`, `interference`
- source: `isq_train_cot`
- dataset_index: `3986`

### Prompt

请用isQ语言编写一个量子电路：an isQ program: SWAP test between |0> and |0>. q[0]=ancilla, q[1]=state A, q[2]=state B. H on ancilla, controlled-SWAP, H on ancilla, measure ancilla.

### Chain-of-thought reasoning

## Reasoning
The circuit performs a swap (three-CNOT decomposition) test to calculate the overlap between two identical states, |0> and |0>.
It requires 3 qubits: q[0] as the ancilla, and q[1], q[2] as the two input states, all of which are measured.
The initial state is |000>. Applying an H gate to the ancilla yields (1/√2)(|000> + |100>).
The controlled-swap operation (three-CNOT decomposition) exchanges q[1] and q[2] only when q[0] is |1>. Since both q[1] and q[2] are in the |0> state, swapping them leaves the quantum state unchanged.
Applying a second H gate to the ancilla constructively interferes the ancilla states: (1/2)[(|0>+|1>) + (|0>-|1>)]|00> = |000>.
Since the exact final state is |000>, measuring the system yields the bitstring '000'
