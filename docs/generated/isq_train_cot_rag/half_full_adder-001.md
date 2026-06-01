# ISQ training COT RAG corpus: half_full_adder shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3320

- task_id: `isqTrain/3320`
- task_type: `code_generation`
- category: `half_full_adder`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5513`

### Prompt

实现以下量子计算任务（使用isQ）：an isQ program: half adder for 1+1. q[0]=a=1, q[1]=b=1, q[2]=carry (ancilla). Sum: CNOT(q[0],q[1]). Carry: Toffoli(q[0],q[1],q[2]) applied BEFORE the CNOT.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement a half adder for 1+1 (binary addition) computing sum and carry outputs.
Qubits: 3 qubits (q[0]=a=1, q[1]=b=1, q[2]=carry ancilla); all measured.

State evolution:
- |000⟩ → X(q[0]), X(q[1]) → |110⟩ (initialize a=1, b=1)
- |110⟩ → Toffoli(q[0],q[1],q[2]) → |111⟩ (carry=1 since both inputs are 1)
- |111⟩ → CNOT(q[0],q[1]) → |101⟩ (sum=1⊕1=0 stored in q[1])

Final state |101⟩ means q[2]=1 (carry), q[1]=0 (sum), q[0]=1 (a), giving probability {|101⟩: 1.0} — correct result since 1+1=10 in binary (sum 0, carry 1).

## isqTrain/3318

- task_id: `isqTrain/3318`
- task_type: `code_generation`
- category: `half_full_adder`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1959`

### Prompt

用isQ实现an isQ program: half adder for 0+1. q[0]=a=0, q[1]=b=1, q[2]=carry (ancilla). Sum: CNOT(q[0],q[1]). Carry: Toffoli(q[0],q[1],q[2]) applied BEFORE the CNOT.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Implement a half adder for 0+1, computing sum and carry outputs.
**Qubits:** 3 qubits (q[0]=a=0, q[1]=b=1, q[2]=carry ancilla); all measured.

**State evolution:**
1. Initialize |000⟩; apply X(q[1]) → |010⟩ (sets b=1)
2. Apply Toffoli(q[0], q[1], q[2]): requires both controls |1⟩ to flip target; q[0]=0, so no change → |010⟩
3. Apply CNOT(q[0], q[1]): flips q[1] when q[0]=|1⟩; q[0]=0, so no change → |010⟩

**Final state:** |010⟩, meaning sum (q[1])=1, carry (q[2])=0.
**Expected probability:** {|010⟩: 1.0} — correct result for 0+1=01 (no carry, sum=1).

## isqTrain/3319

- task_id: `isqTrain/3319`
- task_type: `code_generation`
- category: `half_full_adder`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2907`

### Prompt

Implement a quantum circuit in isQ: an isQ program: half adder for 1+0. q[0]=a=1, q[1]=b=0, q[2]=carry (ancilla). Sum: CNOT(q[0],q[1]). Carry: Toffoli(q[0],q[1],q[2]) applied BEFORE the CNOT.

### Chain-of-thought reasoning

## Reasoning
The goal is to implement a quantum half adder for 1+0, computing the sum and carry bits.
Three qubits are used: q[0] (input a), q[1] (input b), and q[2] (carry ancilla), and all three are measured.
The circuit starts in the initial state |000⟩.
An X gate is applied to q[0], changing the state to |100⟩ to set a=1 and b=0.
The Toffoli gate (carry) is applied first, but since q[1] is |0⟩, the target q[2] is not flipped, leaving the state as |100⟩.
The CNOT gate (sum) applies to q[0] and q[1]; since the control q[0] is |1⟩, the target q[1] is flipped to |1⟩, resulting in the final state |110⟩.
This final state directly yields the measurement probabilities {|110⟩: 1.0}, as the system is in a deterministic basis state.

## isqTrain/3317

- task_id: `isqTrain/3317`
- task_type: `code_generation`
- category: `half_full_adder`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4568`

### Prompt

Create an isQ quantum circuit that an isQ program: half adder for 0+0. q[0]=a=0, q[1]=b=0, q[2]=carry (ancilla). Sum: CNOT(q[0],q[1]). Carry: Toffoli(q[0],q[1],q[2]) applied BEFORE the CNOT.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Implement a half adder for 0+0, computing sum and carry outputs.
2. Three qubits (q[0]=a=0, q[1]=b=0, q[2]=carry ancilla), all measured.
3. Initial state: |000⟩
4. Toffoli(q[0], q[1], q[2]): Flips q[2] only if both q[0]=|1⟩ AND q[1]=|1⟩; since both are |0⟩, state remains |000⟩
5. CNOT(q[0], q[1]): Flips q[1] only if q[0]=|1⟩; since q[0]=|0⟩, state remains |000⟩
6. Final state: |000⟩ with probability 1.0
7. Expected measurement: {|000⟩: 1.0} — sum=0 (q[1]), carry=0 (q[2])
