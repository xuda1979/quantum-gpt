# ISQ training COT RAG corpus: logic_gates shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/381

- task_id: `isqTrain/381`
- task_type: `output_prediction`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `isq_syntax_procedures`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5671`

### Prompt

What does this isQ program output when measured?

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

### Chain-of-thought reasoning

## Circuit Analysis
1. The initial state of the 3-qubit system is $|000\rangle$. 
2. The X gates applied to $q_0$ and $q_1$ flip their states from $|0\rangle$ to $|1\rangle$, evolving the system to $|110\rangle$.
3. The first CNOT($q_0$, $q_2$) flips the target $q_2$ to $|1\rangle$ because the control $q_0$ is $|1\rangle$, changing the state to $|111\rangle$.
4. The second CNOT($q_1$, $q_2$) flips the target $q_2$ back to $|0\rangle$ because the control $q_1$ is also $|1\rangle$, resulting in the final state $|110\rangle$. This correctly computes the XOR of 1 and 1 (which is 0) in the ancilla qubit.
5. Measurements of all three qubits will deterministically yield this final state.

Predicted probability distribution: {|110>: 1.0}

### Reference answer

{'predicted_probs': {'6': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/116. Dimension: predict probabilities for reference circuit.'}

## isqTrain/1734

- task_id: `isqTrain/1734`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`
- source: `isq_train_cot`
- dataset_index: `5725`

### Prompt

I need an isQ program to Compute XNOR of a=1, b=0 using quantum gates. Store result in q[2].

### Chain-of-thought reasoning

## Reasoning
Compute XNOR(1, 0) = 0 using a 3-qubit circuit, setting inputs and storing the result in q[2].
Initial state is |000⟩.
Apply X(q[0]) to set input a=1: |000⟩ → |100⟩.
Apply CNOT(q[0], q[2]) for partial XOR: |100⟩ → |101⟩.
Apply CNOT(q[1], q[2]) to complete XOR(1, 0) = 1: |101⟩ → |101⟩.
Apply X(q[2]) to negate the XOR result into XNOR: |101⟩ → |100⟩.
Measuring all qubits deterministically yields the bitstring 100 with probability 1.0.

## isqTrain/1675

- task_id: `isqTrain/1675`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `2307`

### Prompt

Create an isQ quantum circuit that Compute the parity of the 4-bit input |0011> using CNOT gates into an ancilla qubit. Measure the ancilla.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Compute the parity (sum modulo 2) of the 4-qubit state |0011⟩ into an ancilla qubit.
2. **Qubits**: 5 total (q[0..3] and anc[0]); only anc[0] is measured.
3. **State evolution**:
   - Initialize to |0000⟩|0⟩, apply X to q[2] and q[3] → |0011⟩|0⟩
   - CNOT(q[0], anc[0]): control |0⟩, no flip → |0011⟩|0⟩
   - CNOT(q[1], anc[0]): control |0⟩, no flip → |0011⟩|0⟩
   - CNOT(q[2], anc[0]): control |1⟩, flips ancilla → |0011⟩|1⟩
   - CNOT(q[3], anc[0]): control |1⟩, flips ancilla back → |0011⟩|0⟩
4. **Result**: The parity of 0011 is 0 (even number of 1s), so ancilla is |0⟩ with probability 1.0.

## isqTrain/1732

- task_id: `isqTrain/1732`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`
- source: `isq_train_cot`
- dataset_index: `2104`

### Prompt

帮我写一个isQ程序：Compute XNOR of a=0, b=1 using quantum gates. Store result in q[2].

### Chain-of-thought reasoning

## Reasoning
Goal: Compute XNOR(0,1) by initializing inputs a=0 and b=1, computing XOR, then negating to get XNOR, stored in q[2].

Three qubits q[0], q[1], q[2] are used; all are measured.

State evolution:
1. |000⟩ — initial state
2. X(q[1]) → |010⟩ — sets b=1
3. CNOT(q[0], q[2]) → |010⟩ — q[0]=|0⟩, target unchanged (XOR partial: q[2]⊕=0)
4. CNOT(q[1], q[2]) → |011⟩ — q[1]=|1⟩, flips q[2] (XOR complete: q[2]=1)
5. X(q[2]) → |010⟩ — negates XOR result to get XNOR=0

Final state |010⟩ is a computational basis state, so measurement yields |010⟩ with probability 1.0.

## isqTrain/1507

- task_id: `isqTrain/1507`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `752`

### Prompt

I need an isQ program to Compute the inner product mod 2 of a=010 and b=001 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning
The circuit computes the bitwise inner product modulo 2 between a=010 and b=001 using three Toffoli gates.
It requires 7 qubits (6 for inputs, 1 ancilla); only the ancilla is measured.
X gates initialize the inputs to $|a\rangle|b\rangle|anc\rangle =

## isqTrain/1949

- task_id: `isqTrain/1949`
- task_type: `output_prediction`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `739`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit A[1]; qbit B[1]; qbit Cin[1];
qbit Sum[1]; qbit Cout[1];
qbit anc[1];

procedure main() {
    X(A[0]); X(B[0]); X(Cin[0]);
    CNOT(A[0], Sum[0]);
    CNOT(B[0], Sum[0]);
    CNOT(Cin[0], Sum[0]);
    Toffoli(A[0], B[0], Cout[0]);

    CNOT(A[0], anc[0]); CNOT(B[0], anc[0]);
    Toffoli(Cin[0], anc[0], Cout[0]);
    M(A[0]); M(B[0]); M(Cin[0]); M(Sum[0]); M(Cout[0]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Analyze an isQ program and predict the probability distribution.
    *   Output format: Concise step-by-step reasoning starting with "## Circuit Analysis", ending with the probability distribution.
    *   Specific constraints: Use Dirac notation, 3-15 lines, NO code blocks, output ONLY the analysis.

2.  **Analyze the isQ Program:**
    *   Variables: `A[1]`, `B[1]`, `Cin[1]`, `Sum[1]`, `Cout[1]`, `anc[1]`.
    *   Initial state: |000000> (6 qubits).
    *   `X(A[0]); X(B[0]); X(Cin[0]);` -> State becomes |111000> (A=1, B=1, Cin=1).
    *   `CNOT(A[0], Sum[0]); CNOT(B[0], Sum[0]); CNOT(Cin[0], Sum[0]);`
        *   Sum[0] is initially 0.
        *   Flipped by A: 1
        *   Flipped by B: 0
        *   Flipped by Cin: 1
        *   State becomes |111100> (Sum=1).
    *   `Toffoli(A[0], B[0], Cout[0]);`
        *   Both A and B are 1, so Cout[0] is flipped.
        *   State becomes |111110> (Cout=1).
    *   `CNOT(A[0], anc[0]); CNOT(B[0], anc[0]);`
        *   anc[0] is initially 0.
        *   Flipped by A: 1
        *   Flipped by B: 0
        *   State remains |111110> for measured qubits (anc=0).
    *   `Toffoli(Cin[0], anc[0], Cout[0]);`
        *   Cin is 1, but anc is 0. Toffoli doesn't flip.
        *   State remains |111110>.
    *   `M(A[0]); M(B[0]); M(Cin[0]); M(Sum[0]); M(Cout[0]);`
        *   Measured qubits: A, B, Cin, Sum, Cout.
        *   Values: 1, 1, 1, 1, 1.
        *   Bitstring: '11111'.

3.  **Check logic:**
    *   It's a full-adder circuit. 1 + 1 + 1 = 3 = 11 in binary. Sum = 1, Cout = 1. Correct.
    *   Bitstring is formed by measurements in order: M(A)=1, M(B)=1, M(Cin)=1, M(Sum)=1, M(Cout)=1.
    *   Order of measurement maps to bitstring: Earlier measured = higher bit. So A=16, B=8, Cin=4, Sum=2, Cout=1. String: 11111.

4.  **Draft the response:**
    *   Start with "## Circuit Analysis"
    *   Explain gates: initializes A, B, Cin to |1>, leaves Sum, Cout, anc at |0>.
    *   State evolution: |000000> -> X gates -> |111000>.
    *   CNOTs on Sum: Sum becomes 1^1^1 = 1. State -> |111100>.
    *   Toffoli(A, B, Cout): Both controls 1, Cout becomes 1. State -> |111110>.
    *   CNOTs on anc: anc becomes 1^1 = 0. State -> |111110>.
    *   Toffoli(Cin, anc, Cout): anc is 0, no flip. Final state |111110>.
    *   Measurements yield A, B, Cin, Sum, Cout = 1.
    *   Probabilities: {'11111': 1.0}.

5.  **Refine for conciseness (3-8 lines ideally):**
    ## Circuit Analysis
    1. The circuit implements a full-adder. It initializes qubits A, B, and Cin to |1> using X gates, starting from |000000>.
    2. Three CNOTs target Sum: since A, B, and Cin are |1>, Sum is flipped three times (0 -> 1 -> 0 -> 1), resulting in state |111100>.
    3. A Toffoli gate on Cout with controls A and B flips Cout to |1> (state |111110>).
    4. Two CNOT

### Reference answer

{'predicted_probs': {'11111': 1.0}, 'explanation': '1-bit Full Adder'}

## isqTrain/398

- task_id: `isqTrain/398`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `isq_syntax_multi_register`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `2995`

### Prompt

Implement the following in isQ: implements a variant of the arithmetic_circuit pattern using anc[1] -> anc[3]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a 1-bit full adder computing Sum = A ⊕ B ⊕ Cin and Cout = (A ∧ B) ⊕ (Cin ∧ (A ⊕ B)), with ancilla registers anc[0]-anc[2] for intermediate calculations.

2. **Qubits**: 8 total (A[1], B[1], Cin[1], Sum[1], Cout[1], anc[3]); 5 measured (A[0], B[0], Cin[0], Sum[0], Cout[0]).

3. **State evolution** (test case A=B=Cin=1):
   - Initial: |00000000⟩
   - After X gates on A[0], B[0], Cin[0]: |11100000⟩
   - CNOT(A[0], Sum[0]): |11110000⟩ (Sum=1)
   - CNOT(B[0], Sum[0]): |11100000⟩ (Sum=0)
   - CNOT(Cin[0], Sum[0]): |11110000⟩ (Sum=1)
   - Toffoli(A[0], B[0], Cout[0]): |11111000⟩ (Cout=A∧B=1)
   - CNOT(A[0], anc[0]): |11111010⟩ (anc[0]=1)
   - CNOT(B[0], anc[0]): |11111000⟩ (anc[0]=A⊕B=0)
   - Toffoli(Cin[0], anc[0], Cout[0]): |11111000⟩ (Cout stays 1 since Cin∧(A⊕B)=0)

4. **Result**: Final measured qubits A[0]=1, B[0]=1, Cin[0]=1, Sum[0]=1, Cout[0]=1 yield |11111⟩ with probability 1.0.

## isqTrain/1499

- task_id: `isqTrain/1499`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `2170`

### Prompt

Implement a quantum circuit in isQ: Compute the inner product mod 2 of a=11 and b=11 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Compute the inner product mod 2 of two 2-bit values a=11 (binary) and b=11 (binary), storing the result in an ancilla qubit.
2. **Qubits**: 4 data qubits (q[0],q[1] for a; q[2],q[3] for b) and 1 ancilla (anc[0]). Only anc[0] is measured.
3. **Initialization**: X gates on q[0], q[1], q[2], q[3] prepare state |1111⟩|0⟩ (a=11, b=11, ancilla=0).
4. **First Toffoli** (q[0], q[2], anc[0]): Both controls are |1⟩, so ancilla flips → |1111⟩|1⟩ (accumulates a₀∧b₀ = 1).
5. **Second Toffoli**

## isqTrain/1672

- task_id: `isqTrain/1672`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `5699`

### Prompt

Implement the following in isQ: Compute the parity of the 3-bit input |111> using CNOT gates into an ancilla qubit. Measure the ancilla.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Compute the parity of a 3-qubit input state (specifically |111>) into an ancilla qubit and measure the result.
2. **Qubits**: 4 qubits total (q[0], q[1], q[2], anc[0]). Only anc[0] is measured.
3. **State evolution**:
   - Initial state: |0000> (3 inputs + 1 ancilla).
   - X gates on q[0], q[1], q[2]: Prepares the input |1110>.
   - CNOT(q[0], anc[0]): Control is |1>, so target flips. State becomes |1111>.
   - CNOT(q[1], anc[0]): Control is |1>, target flips back. State becomes |1110>.
   - CNOT(q[2], anc[0]): Control is |1>, target flips. State becomes |1111>.
4. **Probabilities**: The ancilla qubit is in state |1>, representing the parity of 3 ones (1+1+1 = 3 mod 2 = 1). Measurement yields |1> with probability 1.0.

## isqTrain/1527

- task_id: `isqTrain/1527`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `1031`

### Prompt

实现以下量子计算任务（使用isQ）：Compute the inner product mod 2 of a=100 and b=111 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Compute the inner product mod 2 of the binary strings a=100 and b=111 using Toffoli gates, storing the result in an ancilla qubit.
2. **Qubits:** 6 data qubits (q[0]-q[5]) and 1 ancilla (anc[0]) which is measured.
3. **Initialization:** Apply X gates to q[0], q[3], q[4], and q[5] to represent a=100 and b=111, evolving the state from |000000⟩|0⟩ to |100111⟩|0⟩.
4. **First Toffoli:** `ctrl ctrl X(q[0], q[3], anc[0])` flips the ancilla because both controls are |1⟩, changing the state to |100111⟩|1⟩.
5. **Second Toffoli:** `ctrl ctrl X(q[1], q[4], anc[0])` does nothing because q[1] is |0⟩.
6. **Third Toffoli:** `ctrl ctrl X(q[2], q[5], anc[0])` does nothing because q[2] is
