# ISQ training COT RAG corpus: logic_gates shard 12

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1497

- task_id: `isqTrain/1497`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `1388`

### Prompt

I need an isQ program to Compute the inner product mod 2 of a=11 and b=01 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants a reasoning section explaining the inner product mod 2 circuit for vectors a=11 (q[0], q[1]) and b=01 (q[2], q[3]) using an ancilla qubit. The predicted output the reasoning only, strictly following the constraints (3-8 lines, Dirac notation, step-by-step evolution).

2.  **Analyze the Circuit**:
    *   Initial state: $|00000\rangle$ (q[0..3], anc[0])
    *   X gates on q[0], q[1], q[3]: State becomes $|1101\rangle \otimes |0\rangle$
    *   Note: The vectors are:
        *   $a = a_0 a_1 \rightarrow$ q[0]=1, q[1]=1
        *   $b = b_0 b_1 \rightarrow$ q[2]=0, q[3]=1
    *   Toffoli on q[0], q[2], anc[0]: anc[0] += $a_0 b_0$. $a_0=1, b_0=0 \implies$ anc flips by $1 \cdot 0 = 0$. State is still $|1101\rangle|0\rangle$.
    *   Toffoli on q[1], q[3], anc[0]: anc[0] += $a_1 b_1$. $a_1=1, b_1=1 \implies$ anc flips by $1 \cdot 1 = 1$. State becomes $|1101\rangle|1\rangle$.
    *   Measurement of anc[0] yields $|1\rangle$ with probability 1.0.

3.  **Draft the Reasoning**:
    *   Goal: Compute the inner product mod 2 of binary vectors a=11 and b=01 using an ancilla qubit.
    *   Qubits: 4 qubits for inputs, 1 ancilla qubit for the result; only the ancilla is measured.
    *   Evolution:
        1. Initialize to $|0000\rangle|0\rangle$.
        2. Apply X gates to q[0], q[1], and q[3] to encode $a=11$ and $b=01$, evolving state to $|1101\rangle|0\rangle$.
        3. Apply Toffoli(q[0], q[2], anc[0]): adds $a_0 \cdot b_0 = 1 \cdot 0 = 0$ to ancilla; state remains $|1101\rangle|0\rangle$.
        4. Apply Toffoli(q[1], q[3], anc[0]): adds $a_1 \cdot b_1 = 1 \cdot 1 = 1$ to ancilla; state becomes $|1101\rangle|1\rangle$.
    *   Probabilities: The final state has the ancilla in $|1\rangle$, yielding a 100% probability of measuring $|1\rangle$.

4.  **Refine and Format**:
    *   Check line count: ~7 lines.
    *   Check notation: $|1101\rangle \otimes |0\rangle$.
    *   Ensure NO code block and starts with "## Reasoning".

5.  **Final Polish**:
    ## Reasoning
    Goal: Compute the mod 2 inner product of binary vectors a=11 and b=01, storing the result in an ancilla qubit.
    Qubits: 5 qubits total (4 for inputs, 1 ancilla); only the ancilla qubit is measured.
    Evolution:
    1. Initialize all qubits to $|0\rangle$, starting in state $|0000\rangle \otimes |0\rangle$.
    2. Apply X gates to q[0], q[1], and q[3] to set a=11 and b=01, yielding state $|1101\rangle \otimes |0\rangle$.
    3. Apply Toffoli(q[0], q[2], anc[0]) to compute $a_0 \cdot b_0$; since q[2] is $|0\rangle$, the ancilla remains unchanged.
    4. Apply Toffoli(q[1], q[3], anc[0]) to compute $a_1 \cdot b_1$; since q[1] and q[3] are $|1\rangle$, it flips the ancilla to $|1\rangle$.
    Probabilities: The final state $|1101\rangle \

## isqTrain/386

- task_id: `isqTrain/386`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_multi_register`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `287`

### Prompt

Help me write isQ code that implements a variant of the arithmetic_circuit pattern using A[1] -> A[3]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a 1-bit half adder (A + B) with expanded register A[3], computing Sum and Carry.
2. **Qubits**: 6 total — A[0], A[1], A[2], B[0], Sum[0], Carry[0]; all are measured.
3. **State evolution** (initial |000000⟩ → final):
   - X(A[0]): |000000⟩ → |100000⟩ (set A[0]=1)
   - X(B[0]): |100000⟩ → |100100⟩ (set B[0]=1)
   - Toffoli(A[0], B[0], Carry[0]): |100100⟩ → |100101⟩ (Carry = A AND B = 1)
   - CNOT(A[0], Sum[0]): |100101⟩ → |100111⟩ (flip Sum since A=1)
   - CNOT(B[0], Sum[0]): |100111⟩ → |100101⟩ (flip Sum since B=1; Sum = 1⊕1 = 0)
4. **Result**: Final state |100101⟩ has probability 1.0, encoding A[0]=1, A[1]=0, A[2]=0, B[0]=1, Sum=0, Carry=1. Extra qubits A[1], A[2] remain in |0⟩ as required.

## isqTrain/1532

- task_id: `isqTrain/1532`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `4239`

### Prompt

I need an isQ program to Compute the inner product mod 2 of a=101 and b=101 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning
Goal: Compute inner product mod 2 of binary strings a=101 and b=101 using Toffoli gates, storing result in ancilla.

Qubits: q[0..5] encode the two 3-bit strings (q[0..2]=a, q[3..5]=b), anc[0] holds the result; only anc[0] is measured.

State evolution:
1. Initialize all 7 qubits to |0⟩: |000000⟩|0⟩
2. X(q[0]), X(q[2]) set a=101: |101000⟩|0⟩
3. X(q[3]), X(q[5]) set b=101: |101101⟩|0⟩
4. Toffoli(q[0], q[3], anc[0]): both |1⟩ → flip anc → |101101⟩|1⟩
5. Toffoli(q[1], q[4], anc[0]): q[1]=|0⟩ → no flip → |101101⟩|1⟩
6. Toffoli(q[2], q[5], anc[0]): both |1⟩ → flip anc → |101101⟩|0⟩

Result: Inner product mod 2 = (1·1 + 0·0 + 1·1) mod 2 = 2 mod 2 = 0, so anc[0]=|0⟩ with probability 1.0.
