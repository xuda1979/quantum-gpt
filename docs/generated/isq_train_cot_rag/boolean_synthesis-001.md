# ISQ training COT RAG corpus: boolean_synthesis shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3324

- task_id: `isqTrain/3324`
- task_type: `code_generation`
- category: `boolean_synthesis`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`, `boolean_logic`
- source: `isq_train_cot`
- dataset_index: `4435`

### Prompt

Implement a quantum circuit in isQ: an isQ program: quantum OR gate. OR(a,b) = NOT(AND(NOT a, NOT b)). q[0]=0, q[1]=0, q[2] stores a OR b.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement quantum OR gate via De Morgan's law: OR(a,b) = NOT(AND(NOT a, NOT b)), computing 0 OR 0 = 0.
2. **Qubits**: Three qubits q[0], q[1], q[2]; all measured, with q[2] storing the OR result.
3. **State evolution**:
   - Initial state: |000⟩
   - X(q[0]), X(q[1]) → NOT both inputs: |110⟩
   - Toffoli(q[0], q[1], q[2]) → AND of NOT'd inputs stored in q[2]: |111⟩
   - X(q[0]), X(q[1]) → restore original inputs: |001⟩
   - X(q[2]) → NOT the AND to complete OR: |000⟩
4. **Result**: Final state |000⟩ yields measurement probability {|000⟩: 1.0}, confirming 0 OR 0 = 0 stored in q[2]=0.

## isqTrain/3328

- task_id: `isqTrain/3328`
- task_type: `code_generation`
- category: `boolean_synthesis`
- difficulty: `basic`
- concept_tags: `boolean_logic`
- source: `isq_train_cot`
- dataset_index: `1803`

### Prompt

Create an isQ quantum circuit that an isQ program: quantum XOR gate. Use CNOT to compute a XOR b into q[1]. q[0]=1, q[1]=1.

### Chain-of-thought reasoning

## Reasoning
The goal is to compute the XOR of two qubits initialized to 1 using a CNOT gate.
We need 2 qubits (q[0] and q[1]), both of which are measured.
Starting in |00>, applying X gates to both yields the initial state |11>.
Applying CNOT(q[0], q[1]) uses q[0] as control and q[1] as target; since q[0] is |1>, the target q[1] is flipped from |1> to |0>.
The final quantum state is |10>.
Measuring this state guarantees the outcome |10> with a probability of 1.0.

## isqTrain/3326

- task_id: `isqTrain/3326`
- task_type: `code_generation`
- category: `boolean_synthesis`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`, `boolean_logic`
- source: `isq_train_cot`
- dataset_index: `5698`

### Prompt

用isQ实现an isQ program: quantum OR gate. OR(a,b) = NOT(AND(NOT a, NOT b)). q[0]=1, q[1]=1, q[2] stores a OR b.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Compute OR(1,1)=1 via OR(a,b) = NOT(AND(NOT a, NOT b)).
2. **Qubits**: 3 qubits q[0..2]; all measured (q[0]=a, q[1]=b, q[2]=OR result).
3. **State evolution**:
   - |000⟩ → X(q[0])X(q[1]) → |110⟩ (set a=1, b=1)
   - |110⟩ → X(q[0])X(q[1]) → |000⟩ (apply NOT to inputs for De Morgan's)
   - |000⟩ → Toffoli(q[0],q[1],q[2]) → |000⟩ (AND(NOT a, NOT b) = AND(0,0) = 0)
   - |000⟩ → X(q[0])X(q[1]) → |110⟩ (restore original inputs)
   - |110⟩ → X(q[2]) → |111⟩ (NOT the AND result gives OR = NOT(0) = 1)
4. **Final state**: |111⟩ yields probability {|111⟩: 1.0}, confirming 1 OR 1 = 1.

## isqTrain/3327

- task_id: `isqTrain/3327`
- task_type: `code_generation`
- category: `boolean_synthesis`
- difficulty: `basic`
- concept_tags: `boolean_logic`
- source: `isq_train_cot`
- dataset_index: `1618`

### Prompt

Write an isQ program that an isQ program: quantum XOR gate. Use CNOT to compute a XOR b into q[1]. q[0]=0, q[1]=1.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a quantum XOR gate using CNOT to compute `q[0]` XOR `q[1]` into `q[1]`, given inputs 0 and 1.
2. **Qubits**: 2 qubits (`q[0]` and `q[1]`), both are measured at the end.
3. **State Evolution**:
   - Initialize to |00⟩.
   - `X(q[1])` flips the second qubit, resulting in |01⟩.
   - `CNOT(q[0], q[1])` applies an XOR operation; since the control `q[0]` is |0⟩, the target `q[1]` remains unchanged, leaving the state as |01⟩.
4. **Probabilities**: The final quantum state is exactly |01⟩, which ensures a 100% probability of measuring the bitstring '01' (representing 0 XOR 1 = 1).
