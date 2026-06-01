# ISQ training COT RAG corpus: logic_gates shard 2

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1733

- task_id: `isqTrain/1733`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `4079`

### Prompt

I need an isQ program to Compute NOR of a=0, b=1 using quantum gates (De Morgan: AND of negated inputs). Store result in q[2].

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Compute NOR(0, 1) using De Morgan's law: NOR(a, b) = NOT(a) AND NOT(b).
2. **Qubits**: 3 qubits (`q[0]`=a, `q[1]`=b, `q[2]`=target). All are measured.
3. **State Evolution**:
   - Initialize to |000⟩. Apply `X(q[1])` to set `b=1`, yielding |010⟩.
   - Apply `X(q[0])` and `X(q[1])` to temporarily negate inputs for the AND operation, resulting in |101⟩.
   - Apply `ctrl ctrl X(q[0], q[1], q[2])` (Toffoli). Since `q[1]` is |0⟩, the target `q[2]` is not flipped, leaving the state |101⟩.
   - Apply `X(q[0])` and `X(q[1])` again to restore the original inputs, returning the state to |010⟩.
4. **Probabilities**: The final state is exactly |010⟩, meaning q[2] correctly holds the NOR result (0). Measuring yields the bitstring '010' (q[0]=0, q[1]=1, q[2]=0) with 100% probability.

## isqTrain/1530

- task_id: `isqTrain/1530`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `2516`

### Prompt

Create an isQ quantum circuit that Compute the inner product mod 2 of a=101 and b=011 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Compute the bitwise inner product mod 2 of a=101 and b=011 using Toffoli gates, storing the result in an ancilla qubit.

2. **Qubits**: 6 data qubits q[0..5] (q[0..2]=a, q[3..5]=b) and 1 ancilla anc[0]. Only anc[0] is measured.

3. **State evolution**:
   - Initialize: |000000⟩|0⟩ → X(q[0],q[2]) sets a=101, X(q[4],q[5]) sets b=011 → |101011⟩|0⟩
   - Toffoli(q[0],q[3],anc): q[0]=1, q[3]=0 → no flip → |101011⟩|0

## isqTrain/1516

- task_id: `isqTrain/1516`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `5278`

### Prompt

Create an isQ quantum circuit that Compute the inner product mod 2 of a=011 and b=011 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning
Goal: Compute the inner product mod 2 of a=011 and b=011 using Toffoli gates, storing the result in an ancilla qubit.

Qubits: 7 total (q[0-5] for a and b, anc[0] for result); only anc[0] is measured.

State evolution:
1. Initial: |0000000⟩ (q[0-5], anc[0])
2. X(q[1]), X(q[2]) encodes a=011: |0110000⟩
3. X(q[4]), X(q[5]) encodes b=011: |0110110⟩
4. Toffoli(q[0], q[3], anc[0]): controls q[0]=|0⟩, q[3]=|0⟩ → no flip → |0110110⟩
5. Toffoli(q[1], q[4], anc[0]): controls q[1]=|1⟩, q[4]=|1⟩ → flips anc → |0110111⟩
6. Toffoli(q[2], q[5], anc[0]): controls q[2]=|1⟩, q[5]=|1⟩ → flips anc back → |0110110⟩

## isqTrain/1538

- task_id: `isqTrain/1538`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `2617`

### Prompt

Write an isQ program that Compute the inner product mod 2 of a=110 and b=100 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Compute the bitwise inner product mod 2 of $a=110$ and $b=100$ using Toffoli gates and store the result in an ancilla qubit.
2. **Qubits:** 6 data qubits ($q[0..2]$ for $a$, $q[3..5]$ for $b$) and 1 ancilla ($anc[0]$), which is measured.
3. **State Evolution:**
   - Initialize to $|0\rangle^{\otimes 7}$.
   - Apply $X$ to $q[0], q[1]$ (for $a=110$) and $q[3]$ (for $b=100$), evolving state to $|1101000\rangle$.
   - Toffoli on $q[0], q[3], anc[0]$: both controls are $|1\rangle$, so $anc[0]$ flips to $|1\rangle$.
   - Toffoli on $q[1], q[4], anc[0]$: $q[4]$ is $|0\rangle$, so $anc[0]$ remains $|1\rangle$.
   - Toffoli on $q[2], q[5], anc[0]$: $q[2], q[5]$ are $|0\rangle$, so $anc[0]$ remains $|1\rangle$.
   - Final state is $|1101001\rangle$.
4. **Measurement:** The ancilla qubit is deterministically in the $|1\rangle$ state, yielding an expected probability of $P(|1\rangle) = 1.0$.

## isqTrain/395

- task_id: `isqTrain/395`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `isq_syntax_multi_register`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `126`

### Prompt

Code this in isQ: implements a variant of the arithmetic_circuit pattern using anc[1] -> anc[2]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement a 1-bit full adder computing Sum = A⊕B⊕Cin and Cout = (A∧B)∨(Cin∧(A⊕B)) using ancilla for intermediate XOR.

2. **Qubits**: 7 total (A, B, Cin, Sum, Cout, anc[0], anc[1]); 5 measured (A[0], B[0], Cin[0], Sum[0], Cout[0]).

3. **State evolution** (test case A=B=Cin=1):
   - After X gates: |111⟩|0000⟩ (initializing inputs to |1⟩)
   - CNOT(A→Sum), CNOT(B→Sum), CNOT(Cin→Sum): Sum = 1⊕1⊕1 = 1, state |111⟩|1000⟩
   - Toffoli(A,B→Cout): Cout = A∧B = 1, state |111⟩|1100⟩
   - CNOT(A→anc[0]), CNOT(B→anc[0]): anc[0] = A⊕B = 0, state |111⟩|110_0⟩
   - Toffoli(Cin,anc[0]→Cout): Cout = 1⊕(1∧0) = 1, final state |11111⟩|00⟩

4. **Expected result**: Final measured state is |11111⟩ with probability 1.0, confirming Sum=1, Cout=1 for inputs 1+1+1=3 (binary: Sum=1, Cout=1).

## isqTrain/2579

- task_id: `isqTrain/2579`
- task_type: `code_equivalence`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `global_phase`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `5079`

### Prompt

Will these two quantum programs produce identical measurement outcomes?

```isq
import std;

qbit A[1]; qbit B[1]; qbit Sum[1]; qbit Carry[1];

procedure main() {
    // 1-bit half adder
    // Test case: 1 + 1 -> Sum=0, Carry=1
    X(A[0]);
    X(B[0]);
    
    // Carry = A AND B
    Toffoli(A[0], B[0], Carry[0]);
    
    // Sum = A XOR B
    CNOT(A[0], Sum[0]);
    CNOT(B[0], Sum[0]);
    
    M(A[0]); M(B[0]); M(Sum[0]); M(Carry[0]); // A,B,Sum,Carry
}

```

vs.

```isq
import std;

qbit A[1]; qbit B[1]; qbit Sum[1]; qbit Carry[1];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    // 1-bit half adder
    // Test case: 1 + 1 -> Sum=0, Carry=1
    X(A[0]);
    X(B[0]);
    
    // Carry = A AND B
    Toffoli(A[0], B[0], Carry[0]);
    
    // Sum = A XOR B
    CNOT(A[0], Sum[0]);
    CNOT(B[0], Sum[0]);
    
    M(A[0]); M(B[0]); M(Sum[0]); M(Carry[0]); // A,B,Sum,Carry
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** initializes four qubits (A, B, Sum, Carry) to |0>. It applies X gates to A and B, setting them to |1>. A Toffoli gate computes the Carry (A AND B) resulting in |1>. Two CNOT gates compute the Sum (A XOR B) resulting in |0>.
2. **Program B** performs the exact same sequence of operations: initialization, X gates on A and B, the Toffoli gate, and the two CNOT gates. 
3. The only difference between the programs is the addition of `GPhase(0.0)` in Program B before the main logic.
4. `GPhase(0.0)` applies a global phase factor of $e^{i0} = 1$, which is an identity operation on the quantum state. Thus, the final quantum states and measurement probability distributions of both programs are identical (yielding 100% probability for A=1, B=1, Sum=0, Carry=1).
5. Verdict: Equivalent: True

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/1512

- task_id: `isqTrain/1512`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `2804`

### Prompt

Implement a quantum circuit in isQ: Compute the inner product mod 2 of a=010 and b=110 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Compute the inner product mod 2 of a=010 and b=110 using Toffoli gates, storing the result in an ancilla qubit.

**Qubits:** 6 data qubits (q[0-2] for a, q[3-5] for b) and 1 ancilla (anc[0]); only anc[0] is measured.

**State evolution:**
1. Initial: |000000⟩|0⟩
2. After X(q[1]), X(q[3]), X(q[4]): |010110⟩|0⟩ (encodes a=010, b=110)
3. Toffoli(q[0], q[3], anc): q[0]=0, no flip → |010110⟩|0⟩
4. Toffoli(q[1], q[4], anc): q[1]=1, q[4]=1, flip → |010110⟩|1⟩
5. Toffoli(q[2], q[5], anc): q[2]=0, no flip → |010110⟩|1⟩

**Result:** The inner product mod 2 is 0⊕1⊕0 = 1. The ancilla is in state |1⟩, so measurement yields |1⟩ with probability 1.0.

## isqTrain/1522

- task_id: `isqTrain/1522`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `1800`

### Prompt

帮我写一个isQ程序：Compute the inner product mod 2 of a=100 and b=010 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Compute a·b mod 2 where a=100, b=010 using Toffoli gates, storing result in ancilla.
2. **Qubits**: 7 total (q[0..5] for inputs, anc[0] for result); only anc[0] is measured.
3. **State evolution**:
   - Initial: |000000⟩|0⟩
   - After X(q[0]), X(q[4]): |100100⟩|0⟩ (a=100 in q[0:3], b=010 in q[3:6])
   - Toffoli(q[0],q[3],anc): controls (1,0) → no flip → |100100⟩|0⟩
   - Toffoli(q[1],q[4],anc): controls (0,1) → no flip → |100100⟩|0⟩
   - Toffoli(q[2],q[5],anc): controls (0,0) → no flip → |100100⟩|0⟩
4. **Result**: a·b = (1·0)⊕(0·1)⊕(0·0) = 0, so ancilla remains |0⟩. Expected probabilities: {|0⟩: 1.0}.

## isqTrain/1501

- task_id: `isqTrain/1501`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `1850`

### Prompt

Create an isQ quantum circuit that Compute the inner product mod 2 of a=001 and b=010 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Compute the bitwise inner product mod 2 of a=001 and b=010 using Toffoli gates, storing the result in an ancilla qubit.
2. **Qubits**: 7 qubits total (q[0...5] for the two bitstrings, anc[0] for the result). Only anc[0] is measured.
3. **State Evolution**:
   - Initialize all qubits to |0>: |0000000>.
   - Encode a=001 and b=010: Apply X to q[2] and q[4], yielding |0010100>.
   - Apply Toffoli(q[0], q

## isqTrain/1510

- task_id: `isqTrain/1510`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `5077`

### Prompt

Write isQ code for the following quantum task: Compute the inner product mod 2 of a=010 and b=100 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Compute the bitwise inner product mod 2 of a=010 and b=100, storing the result in an ancilla qubit.
2. **Qubits**: 7 total (6 inputs, 1 ancilla); only the ancilla (`anc[0]`) is measured.
3. **Initialization**: Apply X gates to `q[1]` (for a's second bit) and `q[3]` (for b's first bit), yielding the state |0101000>.
4. **Evolution**: The Toffoli gates compute the AND of corresponding bit pairs (q[0]&q[3], q[1]&q[4], q[2]&q[5]) and XOR them into the ancilla. Since none of the bit pairs are both '1', the ancilla is never flipped.
5. **Outcome**: The final state is |0101000>, so measuring the ancilla yields |0> with 100% probability, correctly reflecting the inner product mod 2 of 0.
