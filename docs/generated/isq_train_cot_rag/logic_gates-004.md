# ISQ training COT RAG corpus: logic_gates shard 4

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/387

- task_id: `isqTrain/387`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_multi_register`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `1944`

### Prompt

用isQ实现implements a variant of the arithmetic_circuit pattern using B[1] -> B[3]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a 1-bit half adder (A + B → Sum, Carry) using an expanded 3-qubit B register, computing 1+1=2 (binary: Sum=0, Carry=1).

2. **Qubits**: 6 total — A[0], B[0], B[1], B[2], Sum[0], Carry[0]; all are measured.

3. **State evolution**:
   - Initial: |000000⟩ (A[0], B[0], B[1], B[2], Sum[0], Carry[0])
   - X(A[0]): |100000⟩
   - X(B[0]): |110000⟩ (inputs set to 1+1)
   - Toffoli(A[0], B[0], Carry[0]): |110001⟩ (Carry = A AND B = 1)
   - CNOT(A[0], Sum[0]): |110101⟩ (Sum flips to 1)
   - CNOT(B[0], Sum[0]): |110001⟩ (Sum flips back to 0: A XOR B = 0)

4. **Expected probabilities**: Final state |110001⟩ corresponds to measurement bitstring where A=1, B[0]=1, B[1]=0, B[2]=0, Sum=0, Carry=1. The additional B[1] and B[2] remain in |0⟩ (ground state), contributing zeros to the bitstring. Probability of |110001⟩ is 1.0.

## isqTrain/2578

- task_id: `isqTrain/2578`
- task_type: `code_equivalence`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `global_phase`, `isq_syntax_procedures`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1405`

### Prompt

Compare these two isQ programs. Do they give the same probability distribution?

First program:
```isq
import std;

qbit q[3];

procedure XOR_gate() {
    // A XOR B => store in ancilla Q[2]
    CNOT(q[0], q[2]);
    CNOT(q[1], q[2]);
}

procedure main() {
    X(q[0]); // A=1
    X(q[1]); // B=1
    
    XOR_gate();
    
    M(q[0]); M(q[1]); M(q[2]); // should be 110
}

```

Second program:
```isq
import std;

qbit q[3];

procedure XOR_gate() {
    // A XOR B => store in ancilla Q[2]
    CNOT(q[0], q[2]);
    CNOT(q[1], q[2]);
}

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    X(q[0]); // A=1
    X(q[1]); // B=1
    
    XOR_gate();
    
    M(q[0]); M(q[1]); M(q[2]); // should be 110
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. Program A initializes the state to |000⟩, applies X gates to q[0] and q[1] to yield |110⟩, and uses two CNOTs to compute q[2] = q[0] ⊕ q[1], leaving the final state as |110⟩.
2. Program B performs the exact same operations, initializing |000⟩, applying X gates to reach |110⟩, and calculating the XOR into q[2] to end up in |110⟩.
3. The only difference is that Program B includes a `GPhase(0.0)` at the start of `main()`.
4. The `GPhase(0.0)` gate applies a global phase of $e^{i0} = 1$, which is mathematically the identity operation. Global phases do not affect the measurement probability distribution.
5. Both programs output the state |110⟩ with 100% probability.
Verdict: Yes

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/391

- task_id: `isqTrain/391`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_multi_register`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `2250`

### Prompt

Write an isQ program that implements the arithmetic_circuit pattern. Include explicit identity operations in the circuit (H-H pair before M(A[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a 1-bit half adder (1+1) and demonstrate that an identity H-H gate pair cancels out.
2. **Qubits**: 4 qubits (`A`, `B`, `Sum`, `Carry`) are measured, with `A` acting as the highest bit in the output bitstring.
3. **Evolution**:
   - Initialize to |0000⟩. `X` gates on A and B set inputs to 1: |1100⟩.
   - `Toffoli`(A, B, Carry) computes A AND B = 1: |1101⟩.
   - `CNOT`(A, Sum) flips Sum to 1: |1111⟩. `CNOT`(B, Sum) flips Sum back to 0: |1101⟩.
   - `H`(A) maps |1⟩ to |−⟩, creating superposition. The second `H`(A) maps |−⟩ back to |1⟩, restoring |1101⟩.
4. **Result**: The final state is deterministically |1101⟩, resulting in a 100% probability of measuring the bitstring `1101`.

## isqTrain/1502

- task_id: `isqTrain/1502`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `1025`

### Prompt

Write an isQ program that Compute the inner product mod 2 of a=001 and b=011 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Compute the binary inner product a·b mod 2 for a=001 and b=011 using Toffoli gates, storing the result in an ancilla qubit.

2. **Qubits**: 7 qubits total — q[0..2] encode a, q[3..5] encode b, anc[0] stores the result. Only anc[0] is measured.

3. **State evolution**:
   - Initialize: |000⟩_a|000⟩_b|0⟩_anc
   - X(q[2]): |001⟩_a|000⟩_b|0⟩_anc (sets a=001)
   - X(q[4]), X(q[5]): |001⟩_a|011⟩_b|0⟩_anc (sets b=011)
   - Toffoli(q[0], q[3], anc): q[0]=0, no flip → state unchanged
   - Toffoli(q[1], q[4], anc): q[1]=0, no flip → state unchanged
   - Toffoli(q[2], q[5], anc): q[2]=1 AND q[5]=1, flips anc → |001⟩_a|011⟩_b|1⟩_anc

4. **Result**: Since a·b = 0·0 ⊕ 0·1 ⊕ 1·1 = 1, the ancilla is |1⟩. Measurement yields {|1⟩: 1.0}.

## isqTrain/1679

- task_id: `isqTrain/1679`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `4251`

### Prompt

I need an isQ program to Compute the parity of the 4-bit input |0111> using CNOT gates into an ancilla qubit. Measure the ancilla.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Compute the parity (XOR sum) of input |0111⟩ into an ancilla qubit using CNOT gates, then measure.
2. **Qubits**: 5 total (q[0-3] for input, anc[0] for parity); only anc[0] is measured.
3. **State evolution**:
   - Initialize all to |0⟩: |0000⟩|0⟩
   - Apply X to q[1], q[2], q[3]: |0111⟩|0⟩
   - CNOT(q[0], anc[0]): control q[0]=0, no flip → |0111⟩|0⟩
   - CNOT(q[1], anc[0]): control q[1]=1, flip → |0111⟩|1⟩
   - CNOT(q[2], anc[0]): control q[2]=1, flip → |0111⟩|0⟩
   - CNOT(q[3], anc[0]): control q[3]=1, flip → |0111⟩|1⟩
4. **Result**: Parity = 0+1+1+1 = 3 (odd), ancilla is |1⟩, so measurement yields |1⟩ with probability 1.0.

## isqTrain/1671

- task_id: `isqTrain/1671`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `3365`

### Prompt

Write an isQ program that Compute the parity of the 3-bit input |110> using CNOT gates into an ancilla qubit. Measure the ancilla.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Compute the parity of the 3-qubit state |110> into an ancilla qubit.
2. **Qubits**: 3 data qubits (q[0..2]) and 1 ancilla qubit (anc[0]). Only anc[0] is measured.
3. **State evolution**:
   - Initialize to |000>|0>. Apply X to q[0] and q[1] to prepare |110>|0>.
   - Apply CNOT(q[0], anc[0]): control is |1>, flips ancilla to |110>|1>.
   - Apply CNOT(q[1], anc[0]): control is |1>, flips ancilla to |110>|0>.
   - Apply CNOT(q[2], anc[0]): control is |0>, leaves ancilla at |110>|0>.
4. **Measurement probabilities**: The parity of 110 is 1+1+0 = 2 (even parity, 0 mod 2). The ancilla is exactly |0>, so measuring it yields `0` with probability 1.0.

## isqTrain/394

- task_id: `isqTrain/394`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `isq_syntax_multi_register`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3111`

### Prompt

Write an isQ program that implements a variant of the arithmetic_circuit pattern using Cout[1] -> Cout[2]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

Looking at this task, I need to understand what the circuit does and trace through the state evolution.

The circuit implements a 1-bit full adder with:
- Inputs: A[0]=1, B[0]=1, Cin[0]=1
- Output: Sum[0], Cout[0]
- Also has Cout[1] and anc[0] as auxiliary qubits

Let me trace through the state evolution:

1. Initial state: |000000> (A[0], B[0], Cin[0], Sum[0], Cout[0], Cout[1])

Wait, the qubits are: A[1], B[1], Cin[1], Sum[1], Cout[2], anc[1]
That's 7 qubits total, but only 6 are measured (A[0], B[0], Cin[0], Sum[0], Cout[0], Cout[1])

Let me re-read the code:
- X(A[0]); X(B[0]); X(Cin[0]); prepares inputs 1+1+1
- CNOT(A[0], Sum[0]); CNOT(B[0], Sum[0]); CNOT(Cin[0], Sum[0]); computes Sum = A^B^Cin
- Toffoli(A[0], B[0], Cout[0]); computes A&B into Cout
- CNOT(A[0], anc[0]); CNOT(B[0], anc[0]); computes A^B into anc
- Toffoli(Cin[0], anc[0], Cout[0]); adds Cin&(A^B) to Cout

For inputs 1+1+1:
- Sum = 1^1^1 = 1
- Cout = (1&1) | (1&(1^1)) = 1 | 0 = 1

Let me trace the states:
1. After X gates: |1110000> (A=1, B=1, Cin=1, Sum=0, Cout[0]=0, Cout[1]=0, anc=0)

Wait, the order of qubits in the registers and measurement matters. Let me think about this more carefully.

The qubits declared are: A[1], B[1], Cin[1], Sum[1], Cout[2], anc[1]
So we have 7 qubits: A[0], B[0], Cin[0], Sum[0], Cout[0], Cout[1], anc[0]

After X(A[0]), X(B[0]), X(Cin[0]):
State: |111>|0000> (first 3 are A,B,Cin = 1,1,1; remaining are Sum,Cout[0],Cout[1],anc = 0,0,0,0)

After CNOT(A[0], Sum[0]): Sum becomes A=1
State: |111>|1000>

After CNOT(B[0], Sum[0]): Sum becomes 1^1=0
State: |111>|0000>

Hmm wait, that's not right. Let me think again.

Actually, CNOT flips the target when control is |1>.
- CNOT(A[0], Sum[0]): A=1, so Sum flips from 0 to 1
- CNOT(B[0], Sum[0]): B=1, so Sum flips from 1 to 0
- CNOT(Cin[0], Sum[0]): Cin=1, so Sum flips from 0 to 1

So Sum = 1 (correct for 1+1+1=3, sum bit is 1)

After Toffoli(A[0], B[0], Cout[0]): Both A=1 and B=1, so Cout[0] flips from 0 to 1

After CNOT(A[0], anc[0]): A=1, so anc flips from 0 to 1
After CNOT(B[0], anc[0]): B=1, so anc flips from 1 to 0 (anc = A^B = 1^1 = 0)

After Toffoli(Cin[0], anc[0], Cout[0]): Cin=1 but anc=0, so Cout[0] doesn't flip (stays 1)

Final state (before measurement):
A[0]=1, B[0]=1, Cin[0]=1, Sum[0]=1, Cout[0]=1, Cout[1]=0, anc[0]=0

Measured qubits: A[0], B[0], Cin[0], Sum[0], Cout[0], Cout[1]
That's 6 qubits, with values 1,1,1,1,1,0

The bitstring is 111110 (with earlier

## isqTrain/1736

- task_id: `isqTrain/1736`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`
- source: `isq_train_cot`
- dataset_index: `127`

### Prompt

用isQ实现Compute XNOR of a=1, b=1 using quantum gates. Store result in q[2].

### Chain-of-thought reasoning

## Reasoning
1. Goal: Compute XNOR of a=1, b=1 using XOR + NOT, storing the result in q[2].
2. Qubits used: 3 (q[0], q[1], q[2]), all measured.
3. Initial state is |000>. X gates on q[0] and q[1] set them to 1, evolving the state to |110>.
4. CNOT(q[0], q[2]) flips q[2] to 1 (since q[0] is 1), changing state to |111>.
5. CNOT(q[1], q[2]) flips q[2] back to 0 (since q[1] is 1), changing state to |110>.
6. X(q[2]) acts as the NOT to invert XOR to XNOR, flipping q[2] to 1, yielding the final state |111>.
7. Expected probabilities follow directly from the final state: {|111>: 1.0}.

## isqTrain/1496

- task_id: `isqTrain/1496`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `2989`

### Prompt

请用isQ语言编写一个量子电路：Compute the inner product mod 2 of a=10 and b=11 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Generate reasoning for an isQ quantum program that computes the inner product mod 2 of a=10 and b=11 using Toffoli gates.
    *   Input: a=10 (binary), b=11 (binary).
    *   Goal: Explain the state evolution and final measurement probabilities.
    *   Format: "## Reasoning" section, concise (3-15 lines), Dirac notation, NO code blocks.

2.  **Analyze the Circuit (from the circuit implementation):**
    *   Qubits: `q[0]`, `q[1]`, `q[2]`, `q[3]`, `anc[0]`.
    *   Initial state: $|00000\rangle$.
    *   Initialization:
        *   `X(q[0])`: `q[0]` becomes 1. Represents `a[0] = 1`.
        *   `X(q[2])`: `q[2]` becomes 1. Represents `b[0] = 1`.
        *   `X(q[3])`: `q[3]` becomes 1. Represents `b[1] = 1`.
        *   `q[1]` is 0 (represents `a[1] = 0`).
        *   State is $|1\rangle_{q[0]} |0\rangle_{q[1]} |1\rangle_{q[2]} |1\rangle_{q[3]} |0\rangle_{anc} = |10110\rangle$.
    *   Gate operations:
        *   `ctrl ctrl X(q[0], q[2], anc[0])`: Toffoli gate. If `q[0]` and `q[2]` are both 1, flip `anc[0]`. Since `q[0]=1` and `q[2]=1`, `anc[0]` flips to 1.
        *   `ctrl ctrl X(q[1], q[3], anc[0])`: Toffoli gate. If `q[1]` and `q[3]` are both 1, flip `anc[0]`. `q[1]=0` and `q[3]=1`. Target is not flipped.
    *   Final state: $|10111\rangle$.
    *   Measurement: `M(anc[0])` measures the last qubit (`anc[0]`), which is $|1\rangle$.

3.  **Draft the Reasoning:**
    *   *Goal*: Compute the bitwise inner product mod 2 of a=10 and b=11, storing the result in an ancilla qubit.
    *   *Qubits*: 5 qubits total (`q[0..3]`, `anc[0]`), measuring `anc[0]`.
    *   *State evolution*:
        *   Initial state is $|00000\rangle$.
        *   X gates initialize qubits to represent the bits of a=10 and b=11: `q[0]`=1, `q[1]`=0, `q[2]`=1, `q[3]`=1. State becomes $|1_00_1_1_10\rangle = |10110\rangle$.
        *   First Toffoli (`q[0]`, `q[2]`, `anc[0]`): Both controls are $|1\rangle$, so `anc[0]` flips to $|1\rangle$, resulting in $|10111\rangle$.
        *   Second Toffoli (`q[1]`, `q[3]`, `anc[0]`): Control `q[1]` is $|0\rangle$, so `anc[0]` remains $|1\rangle$.
    *   *Measurement*: `anc[0]` is in state $|1\rangle$, so it measures as 1 with 100% probability (inner product $1\cdot1 + 0\cdot1 = 1 \pmod 2$).

4.  **Refine to Constraints:**
    *   Only output reasoning section.
    *   Concise, precise, step-by-step.
    *   Use Dirac notation.

    *Drafting final text:*
    ## Reasoning
    The goal is to compute the bitwise inner product mod 2 of a=10 and b=11, storing the result in an ancilla qubit.
    Five qubits are used (`q[0..3]` for the bits, `anc[0]` for the result), and only `anc[0]` is measured.
    Starting in $|00000\r

## isqTrain/1668

- task_id: `isqTrain/1668`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `1066`

### Prompt

Write isQ code for the following quantum task: Compute the parity of the 3-bit input |011> using CNOT gates into an ancilla qubit. Measure the ancilla.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Compute the parity (sum mod 2) of the 3-qubit state |011⟩ into an ancilla qubit and measure it.
2. **Qubits**: 4 total (q[0], q[1], q[2], anc[0]); only anc[0] is measured.
3. **State evolution**:
   - Initialize |0000⟩ → Apply X(q[1]), X(q[2]) → |0110⟩ (data |011⟩, ancilla |0⟩)
   - CNOT(q[0], anc[0]): control is |0⟩ → no flip → |0110⟩
   - CNOT(q[1], anc[0]): control is |1⟩ → flip → |0111⟩
   - CNOT(q[2], anc[0]): control is |1⟩ → flip → |0110⟩
4. **Result**: Ancilla returns to |0⟩ because parity of |011⟩ is 0+1+1=2≡0 (mod 2).
5. **Expected measurement**: {|0⟩: 1.0} — ancilla is deterministically |0⟩.
