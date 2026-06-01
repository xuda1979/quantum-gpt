# ISQ training COT RAG corpus: circuit_patterns shard 7

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3867

- task_id: `isqTrain/3867`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `expert`
- concept_tags: `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `5640`

### Prompt

Implement a quantum circuit in isQ: Apply `ctrl nctrl X` to |111>: q[0] is positive control, q[1] is negative control, q[2] is target. Target flips when q[0]=|1> AND q[1]=|0>. Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Apply a mixed-control X gate to a 3-qubit system initialized to |111>, where q[0] is positive control, q[1] is negative control, and q[2] is the target.
2. **Qubits:** 3 qubits are used (q[0], q[1], q[2]) and all are measured.
3. **State evolution:** The initial state is |111>. The gate flips the target qubit only if q[0]=|1> and q[1]=|0>. Since q[1] is |1>, the condition is not met and the state remains |111>.
4. **Measurement:** The final state is |111>, yielding a 100% probability of measuring the bitstring 111.
