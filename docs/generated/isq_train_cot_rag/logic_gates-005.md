# ISQ training COT RAG corpus: logic_gates shard 5

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1519

- task_id: `isqTrain/1519`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `2265`

### Prompt

实现以下量子计算任务（使用isQ）：Compute the inner product mod 2 of a=011 and b=110 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning
The circuit computes the bitwise inner product mod 2 of two 3-bit strings a=011 and b=110 using a multi-qubit ancilla register.
Seven qubits are used (6 for inputs, 1 ancilla), and only the ancilla qubit is measured.
Input states are prepared using X gates: q[1] and q[2] are set to |1> for a=011; q[3] and q[4] are set to |1> for b=110.
The bitwise inner product is computed via three Toffoli gates evaluating a_i AND b_i, with results XORed into the ancilla.
Toffoli(q[0], q[3], anc) does nothing since q[0]=|0>; Toffoli(q[1], q[4], anc) flips anc to |1> since both are |1>.
Toffoli(q[2], q[5], anc) does nothing since q[5]=|0>, leaving the ancilla in the |1> state.
Measurement of the ancilla thus yields an expected probability of {|1>: 1.0}.

## isqTrain/1526

- task_id: `isqTrain/1526`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `3491`

### Prompt

用isQ实现Compute the inner product mod 2 of a=100 and b=110 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Compute the bitwise inner product mod 2 of a=100 and b=110, storing the result in an ancilla qubit.
2. **Qubits**: 7 qubits total (q[0..5] for a and b, anc[0] for result); only anc[0] is measured.
3. **State evolution**:
   - Initial state: |0000000⟩
   - X(q[0]), X(q[3]), X(q[4]): |1001100⟩ — encodes a=100 (q[0..2]) and b=110 (q[3..5])
   - Toffoli(q[0], q[3], anc[0]): both controls |1⟩ → flips anc[0] → |1001101⟩
   - Toffoli(q[1], q[4], anc[0]): q[1]=|0⟩ → no action → |1001101⟩
   - Toffoli(q[2], q[5], anc[0]): q[2]=|0⟩ → no action → |1001101⟩
4. **Measurement**: anc[0] = |1⟩ deterministically, giving probability {|1⟩: 1.0}, since (1·1) ⊕ (0·1) ⊕ (0·0) = 1.

## isqTrain/1986

- task_id: `isqTrain/1986`
- task_type: `output_prediction`
- category: `logic_gates`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `956`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;
qbit q[4];
procedure main() {
    X(q[0]);
    X(q[1]);
    X(q[2]);
    ctrl ctrl ctrl X(q[0], q[1], q[2], q[3]);
    M(q[3]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes 4 qubits in the state |0000⟩.
2. X gates are applied to q[0], q[1], and q[2], changing the state to |1110⟩.
3. A triple-controlled X gate (ctrl ctrl ctrl X) is applied with q[0], q[1], and q[2] as controls and q[3] as the target.
4. Since all control qubits are in the |1⟩ state, the target qubit q[3] is flipped from |0⟩ to |1⟩, evolving the state to |1111⟩.
5. Measuring q[3] yields the outcome '1' with absolute certainty.

Predicted probability distribution: {'1': 1.0}

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Expected probabilities: [0.0, 1.0]'}

## isqTrain/1669

- task_id: `isqTrain/1669`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `5556`

### Prompt

用isQ实现Compute the parity of the 3-bit input |100> using CNOT gates into an ancilla qubit. Measure the ancilla.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Compute the parity (XOR sum) of a 3-qubit register initialized to |100⟩ and store the result in an ancilla qubit.
2. **Qubits**: 4 total — `q[3]` for the input register, `anc[1]` to hold the parity result; only `anc[0]` is measured.
3. **State evolution**:
   - Initialize all qubits to |0⟩: |000⟩|0⟩
   - Apply X(q[0]) to prepare |100⟩: |100⟩|0⟩
   - CNOT(q[0], anc[0]) flips ancilla (control is |1⟩): |100⟩|1⟩
   - CNOT(q[1], anc[0]) leaves ancilla unchanged (control is |0⟩): |100⟩|1⟩
   - CNOT(q[2], anc[0]) leaves ancilla unchanged (control is |0⟩): |100⟩|1⟩
4. **Measurement**: The ancilla qubit is in state |1⟩ with certainty, yielding probability distribution {|1⟩: 1.0}. This correctly reflects the odd parity (one `1` in `100`).

## isqTrain/1664

- task_id: `isqTrain/1664`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `basic`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `2113`

### Prompt

实现以下量子计算任务（使用isQ）：Compute the parity of the 2-bit input |10> using CNOT gates into an ancilla qubit. Measure the ancilla.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Compute parity (XOR) of input |10⟩ into ancilla qubit and measure it.
2. Qubits: q[0], q[1] for input, anc[0] for parity result. Only anc[0] is measured.
3. State evolution:
   - Initialize |000⟩ → X(q[0]) → |100⟩
   - CNOT(q[0], anc[0]): control q[0]=|1⟩ flips anc[0] → |101⟩
   - CNOT(q[1], anc[0]): control q[1]=|0⟩ leaves anc[0] unchanged → |101⟩
4. Parity of |10⟩ is 1⊕0=1, so ancilla ends in |1⟩ with certainty: P(|1⟩)=1.0.

## isqTrain/1533

- task_id: `isqTrain/1533`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `2436`

### Prompt

I need an isQ program to Compute the inner product mod 2 of a=101 and b=110 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Compute the bitwise inner product mod 2 of a=101 and b=110 using Toffoli gates, storing the result in an ancilla qubit.

**Setup:** 7 qubits: q[0..5] encode the two bitstrings (q[0..2]=a, q[3..5]=b), anc[0] stores the result. Only anc[0] is measured.

**State evolution:**
1. Initialize: |0000000⟩ (all zeros)
2. X(q[0]), X(q[2]): sets a=101 → |1010000⟩
3. X(q[3]), X(q[4]): sets b=110 → |1011100⟩
4. Toffoli(q[0], q[3], anc): both q[0]=1, q[3]=1 → flip anc → |1011101⟩
5. Toffoli(q[1], q[4], anc): q[1]=0 → no flip → |1011101⟩
6. Toffoli(q[2], q[5], anc): q[5]=0 → no flip → |1011101⟩

**Result:** The inner product is a₀b₀⊕a₁b₁⊕a₂b₂ = 1⊕0⊕0 = 1, so anc[0] = |1⟩ with probability 1.0.

## isqTrain/1498

- task_id: `isqTrain/1498`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `4925`

### Prompt

Write isQ code for the following quantum task: Compute the inner product mod 2 of a=11 and b=10 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Compute the mod-2 inner product of binary strings a=11 and b=10 using Toffoli gates.

**Qubits:** 4 data qubits q[0..3] (a in q[0,1], b in q[2,3]) and 1 ancilla anc[0]; only anc[0] is measured.

**State evolution:**
- Initial: |0000⟩|0⟩
- After X(q[0]), X(q[1]), X(q[2]): |1110⟩|0⟩ (a[0]=1, a[1]=1, b[0]=1, b[1]=0)
- Toffoli(q[0], q[2], anc[0]): both controls are |1⟩, so anc flips → |1110⟩|1⟩
- Toffoli(q[1], q[3], anc[0]): q[3]=|0⟩ so no flip → |1110⟩|1⟩

**Result:** anc[0] = (a₀·b₀) ⊕ (a₁·b₁) = 1·1 ⊕ 1·0 = 1, so measurement yields |1⟩ with probability 1.0.

## isqTrain/1666

- task_id: `isqTrain/1666`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `945`

### Prompt

Implement a quantum circuit in isQ: Compute the parity of the 3-bit input |001> using CNOT gates into an ancilla qubit. Measure the ancilla.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Compute the parity (XOR sum) of |001> into an ancilla qubit and measure it.
2. **Qubits**: 3 data qubits (q[0..2]) + 1 ancilla (anc[0]); only anc[0] is measured.
3. **State evolution** (ordering: q[0], q[1], q[2], anc[0]):
   - Initial: |0000⟩
   - X(q[2]): |0010⟩
   - CNOT(q[0], anc[0]): control is |0⟩, no flip → |0010⟩
   - CNOT(q[1], anc[0]): control is |0⟩, no flip → |0010⟩
   - CNOT(q[2], anc[0]): control is |1⟩, flips ancilla → |0011⟩
4. **Measurement**: anc[0] is |1⟩, so P(|1⟩) = 1.0, matching parity 0⊕0⊕1 = 1.

## isqTrain/1678

- task_id: `isqTrain/1678`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `240`

### Prompt

用isQ实现Compute the parity of the 4-bit input |0110> using CNOT gates into an ancilla qubit. Measure the ancilla.

### Chain-of-thought reasoning

## Reasoning
1.  **Goal**: Calculate the parity of the 4-qubit input state |0110> by storing the result in an ancilla qubit and measuring it.
2.  **Qubits**: Define a 4-qubit register `q` for the input and a 1-qubit register `anc` for the result; only `anc[0]` is measured.
3.  **Evolution**:
    *   Initialize the 5-qubit system to |00000>.
    *   Apply X gates to `q[1]` and `q[2]` to prepare the input, evolving the state to |01100> (where the last qubit is the ancilla).
    *   Apply CNOT(q[0], anc[0]): `q[0]` is |0>, ancilla remains |0>. State is |01100>.
    *   Apply CNOT(q[1], anc[0]): `q[1]` is |1>, ancilla flips to |1>. State is |01101>.
    *   Apply CNOT(q[2], anc[0]): `q[2]` is |1>, ancilla flips to |0>. State is |01100>.
    *   Apply CNOT(q[3], anc[0]): `q[3]` is |0>, ancilla remains |0>. State is |01100>.
4.  **Probabilities**: The final state of the ancilla qubit is deterministically |0>. Thus, measurement yields the bitstring "0" (index 0) with probability 1.0, reflecting the even parity (sum of bits mod 2 is 0) of |0110>.

## isqTrain/1513

- task_id: `isqTrain/1513`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `3017`

### Prompt

I need an isQ program to Compute the inner product mod 2 of a=010 and b=111 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Compute the inner product mod 2 of bitstrings a=010 and b=111, storing the result in an ancilla qubit.
2. **Qubits:** 7 qubits total (q[0..2] for a, q[3..5] for b, anc[0] for the result). Only anc[0] is measured.
3. **State Evolution:**
   - Initialize state to |0>⁷. Apply X to q[1] to set a=|010>, and X to q[3], q[4], q[5] to set b=|111>. Ancilla is |0>.
   - Apply Toffoli(q[0], q[3], anc): evaluates $0 \cdot
