# ISQ training COT RAG corpus: logic_gates shard 9

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/385

- task_id: `isqTrain/385`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_multi_register`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `5151`

### Prompt

实现以下量子计算任务（使用isQ）：implements a variant of the arithmetic_circuit pattern using Carry[1] -> Carry[2]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a 1-bit half adder (A XOR B → Sum, A AND B → Carry) with inputs A=1, B=1 using an expanded Carry register.
2. **Qubits**: 5 total (A[1], B[1], Sum[1], Carry[2]); all are measured, yielding 5-bit output.
3. **State evolution**: |00000⟩ → X(A[0]) → |10000⟩ → X(B[0]) → |11000⟩ → Toffoli(A[0],B[0],Carry[0]) flips Carry[0] since both controls are |1⟩ → |11010⟩ → CNOT(A[0],Sum[0]) flips Sum[0] → |11110⟩ → CNOT(B[0],Sum[0]) flips Sum[0] back → |11010⟩. Carry[1] remains |0⟩ throughout (unused).
4. **predicted output**: Final state |11010⟩ occurs with probability 1.0, corresponding to Sum=0, Carry[0]=1 (since 1+1=0 with carry 1).

## isqTrain/1676

- task_id: `isqTrain/1676`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `4819`

### Prompt

用isQ实现Compute the parity of the 4-bit input |0100> using CNOT gates into an ancilla qubit. Measure the ancilla.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Task:** Compute parity of `|0100>` using CNOTs into an ancilla, then measure ancilla.
    *   **Input state:** `|0100>` (which means q[0]=|0>, q[1]=|1>, q[2]=|0>, q[3]=|0>). Plus ancilla in `|0>`. Total initial state: `|01000>` (q[0..3], anc[0]).
    *   **Circuit:**
        *   Initialize qubits: 5 qubits total (4 data, 1 ancilla).
        *   Apply X to q[1] to prepare `|0100>`.
        *   Apply CNOT(q[0], anc[0])
        *   Apply CNOT(q[1], anc[0])
        *   Apply CNOT(q[2], anc[0])
        *   Apply CNOT(q[3], anc[0])
        *   Measure anc[0].
    *   **Parity of 0100:** Number of 1s is 1 (odd), so parity is 1.
    *   **Output:** ONLY the reasoning section. Concise. Use Dirac notation.

2.  **Drafting the Reasoning:**
    *   *Goal:* Compute the parity (sum mod 2) of the 4-bit state |0100> into an ancilla qubit and measure it.
    *   *Qubits:* 5 qubits (4 data qubits initialized to |0>, 1 ancilla initialized to |0>). Only the ancilla is measured.
    *   *Step-by-step:*
        *   Init: |00000> -> Apply X to q[1]: |01000>
        *   CNOT(q[0], anc[0]): Control is 0, target unchanged -> |01000>
        *   CNOT(q[1], anc[0]): Control is 1, target flips to 1 -> |01001>
        *   CNOT(q[2], anc[0]): Control is 0, target unchanged -> |01001>
        *   CNOT(q[3], anc[0]): Control is 0, target unchanged -> |01001>
    *   *Conclusion:* The final state is |01001>. Measuring the ancilla yields |1> with 100% probability, confirming the odd parity of |0100>.

3.  **Refining and Formatting (applying constraints):**
    *   Constraint: 3-8 lines.
    *   Constraint: ONLY output "## Reasoning" followed by the text.
    *   Constraint: Use Dirac notation.

    *Draft 2:*
    ## Reasoning
    1. Goal: Compute and measure the parity of the 4-qubit state |0100> into an ancilla qubit.
    2. Setup: 5 total qubits (4 data, 1 ancilla). X(q[1]) prepares |01000>.
    3. Evolution:
       - CNOT(q[0], anc[0]) does nothing (control=|0>): State remains |01000>.
       - CNOT(q[1], anc[0]) flips ancilla (control=|1>): State becomes |01001>.
       - CNOT(q[2], anc[0]) and CNOT(q[3], anc[0]) do nothing (control=|0>): State remains |01001>.
    4. Result: The ancilla qubit ends in the state |1>, so measurement yields 1 (odd parity) with 100% probability.

    Wait, the ancilla is the last bit in the ket. Let's make it clear. Let's say `|q_3 q_2 q_1 q_0, anc>`.
    Initial: |0000, 0> -> X on q_1 -> |0100, 0>.
    CNOT(q_0, anc) -> |0100, 0>.
    CNOT(q_1, anc) -> |0100, 1>.
    CNOT(q_2, anc) -> |0100, 1>.
    CNOT(q_3, anc) -> |0100, 1>.
    Perfect.

    Let's compress to fit the 3-8 lines limit tightly.

    ## Reasoning
    - **Goal**: Compute the parity of |0100> by XOR-ing the data qubits into an ancilla and measuring it.
    - **Initial State**: 5 qubits (4 data, 1 ancilla). X(q[1]) prepares the state |0100>|0>.
    - **State Evolution**: CNOTs from q[0] and q[2..3] do nothing (controls are |0>). CNOT(q[

## isqTrain/1667

- task_id: `isqTrain/1667`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `5231`

### Prompt

Implement the following in isQ: Compute the parity of the 3-bit input |010> using CNOT gates into an ancilla qubit. Measure the ancilla.

### Chain-of-thought reasoning

## Reasoning
Goal: Compute the parity (XOR) of |010⟩ into an ancilla qubit and measure it.
Qubits: 3 data qubits (q[0..2]) + 1 ancilla (anc[0]); only ancilla is measured.
State evolution: |000⟩|0⟩ →(X on q[1])→ |010⟩|0⟩ →(CNOT q[0]→anc, control=0)→ |010⟩|0⟩ →(CNOT q[1]→anc, control=1)→ |010⟩|1⟩ →(CNOT q[2]→anc, control=0)→ |010⟩|1⟩.
Parity of 010 is 0⊕1⊕0 = 1 (odd), so the ancilla holds |1⟩.
Measuring ancilla yields |1⟩ with probability 1.0.

## isqTrain/1517

- task_id: `isqTrain/1517`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `5187`

### Prompt

Create an isQ quantum circuit that Compute the inner product mod 2 of a=011 and b=100 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Compute the binary inner product a·b mod 2 where a=011 and b=100, storing the result in an ancilla qubit.
2. **Qubits**: 6 data qubits q[0..5] (first 3 for a, last 3 for b) and 1 ancilla; only anc[0] is measured.
3. **State evolution**:
   - Initialize: |000000⟩|0⟩
   - After X(q[1]), X(q[2]): encodes a=011 → |011000⟩|0⟩
   - After X(q[3]): encodes b=100 → |011100⟩|0⟩
   - Toffoli(q[0], q[3], anc): controls are |0⟩,|1⟩ → no flip, state unchanged
   - Toffoli(q[1], q[4], anc): controls are |1⟩,|0⟩ → no flip, state unchanged
   - Toffoli(q[2], q[5], anc): controls are |1⟩,|0⟩ → no flip, state unchanged
4. **Result**: Inner product = (0·1)⊕(1·0)⊕(1·0) = 0, so ancilla remains |0⟩ with probability 1.0.

## isqTrain/1670

- task_id: `isqTrain/1670`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `3469`

### Prompt

Create an isQ quantum circuit that Compute the parity of the 3-bit input |101> using CNOT gates into an ancilla qubit. Measure the ancilla.

### Chain-of-thought reasoning

## Reasoning
Goal: Compute the parity (mod 2 sum) of the 3-bit state |101> into an ancilla qubit and measure it.
Qubits: 4 total (q[3] for data, anc[1] for parity result); measure anc[0] only.
State evolution: |0000> → X(q[0])|1000> → X(q[2])|1010>.
CNOT(q[0],anc[0]): anc flips (q[0]=1) → |1011>.
CNOT(q[1],anc[0]): anc unchanged (q[1]=0) → |1011>.
CNOT(q[2],anc[0]): anc flips (q[2]=1) → |1010>.
Parity of 101 is 1+0+1=2 (even), so ancilla = |0>. Measurement yields P(|0>) = 1.0.

## isqTrain/383

- task_id: `isqTrain/383`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_multi_register`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `637`

### Prompt

Write an isQ program that implements a variant of the arithmetic_circuit pattern using B[1] -> B[2]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement a 1-bit half adder computing Sum = A XOR B and Carry = A AND B, with an expanded B[2] register, testing the case 1+1.

2. **Qubits**: 5 qubits (A[0], B[0], B[1], Sum[0], Carry[0]), all measured. B[1] is unused/idle.

3. **State evolution**:
   - **Initial**: |00000⟩ across (A[0], B[0], B[1], Sum[0], Carry[0])
   - **X(A[0])**: |10000⟩ — sets input A=1
   - **X(B[0])**: |11000⟩ — sets input B=1
   - **Toffoli(A[0], B[0], Carry[0])**: Both controls |1⟩ → flips Carry[0] → |11001⟩ (Carry = A AND B = 1)
   - **CNOT(A[0], Sum[0])**: Control |1⟩ → flips Sum[0] → |11011⟩
   - **CNOT(B[0], Sum[0])**: Control |1⟩ → flips Sum[0] back → |11001⟩ (Sum = A XOR B = 0)

4. **Expected measurement**: Final state |11001⟩ has probability 1.0, encoding A=1, B=1 (with B[1]=0), Sum=0, Carry=1 — the correct result for 1+1=10₂ (Sum 0, Carry 1).

## isqTrain/1492

- task_id: `isqTrain/1492`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `935`

### Prompt

Implement a quantum circuit in isQ: Compute the inner product mod 2 of a=01 and b=10 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Compute the inner product mod 2 of a=01 and b=10 using Toffoli gates.
2. **Qubits:** Uses 5 qubits: q[0..3] for inputs, anc[0] for the result. Measures anc[0].
3. **Initialization:** Initial state is |00000>. X gates on q[1] and q[2] prepare the inputs: a=01 (q[0]=0, q[1]=1) and b=10 (q[2]=1, q[3]=0). State becomes |01100>.
4. **First Toffoli:** `ctrl ctrl X(q[0], q[2], anc[0])` checks a[0] & b[0] (0 & 1 = 0). Since controls aren't both |1>, it does nothing.
5. **Second Toffoli:** `ctrl ctrl X(q[1], q[3], anc[0])` checks a[1] & b[1] (1 & 0 = 0). Since controls aren't both |1>, it does nothing.
6. **Measurement:** anc[0] remains in |0>. Expected probability is {|0>: 1.0}.

## isqTrain/1504

- task_id: `isqTrain/1504`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `1712`

### Prompt

I need an isQ program to Compute the inner product mod 2 of a=001 and b=101 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Compute inner product mod 2 of a=001 and b=101 using Toffoli gates, storing result in ancilla.
2. **Qubits**: 6 data qubits q[0..5] (q[0..2] for a, q[3..5] for b) and 1 ancilla anc[0]; only anc[0] is measured.
3. **State evolution**:
   - Initial: |000000>|0⟩
   - After X(q[2]), X(q[3]), X(q[5]): |001101>|0⟩ (encoding a₂=1, b₀=1, b₂=1)
   - Toffoli(q[0], q[3], anc[0]): q[0]=0, no flip → |001101>|0⟩
   - Toffoli(q[1], q[4], anc[0]): q[1]=0, no flip → |001101>|0⟩
   - Toffoli(q[2], q[5], anc[0]): q[2]=1 and q[5]=1, flips anc → |001101>|1⟩
4. **Result**: anc[0] = 1 since a·b mod 2 = (0∧1)⊕(0∧0)⊕(1∧1) = 0⊕0⊕1 = 1, giving measurement probability {|1⟩: 1.0}.

## isqTrain/1540

- task_id: `isqTrain/1540`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `1235`

### Prompt

Write isQ code for the following quantum task: Compute the inner product mod 2 of a=110 and b=110 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Compute inner product mod 2 of a=110 and b=110 using Toffoli gates, storing result in ancilla.
2. **Qubits**: 7 total (q[0-5] for inputs, anc[0] for result); only anc[0] is measured.
3. **State evolution**:
   - Initial: |0000000⟩
   - After X gates on q[0], q[1], q[3], q[4]: |1100110⟩ (a=110 in q[0-2], b=110 in q[3-5])
   - Toffoli(q[0], q[3], anc[0]): both |1⟩ → flips anc[0] → |1100111⟩
   - Toffoli(q[1], q[4], anc[0]): both |1⟩ → flips anc[0] → |1100110⟩
   - Toffoli(q[2], q[5], anc[0]): q[2]=|0⟩ → no flip → |1100110⟩
4. **Result**: Inner product = (1·1 + 1·1 + 0·0) mod 2 = 2 mod 2 = 0, so anc[0] = |0⟩ with probability 1.0.

## isqTrain/1327

- task_id: `isqTrain/1327`
- task_type: `output_prediction`
- category: `logic_gates`
- difficulty: `basic`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `2349`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;

qbit q[4];

procedure AND_gate() {
    Toffoli(q[0], q[1], q[2]);
}

procedure main() {
    X(q[0]);
    X(q[1]);

    AND_gate();

    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations applied:** The circuit initializes 4 qubits in the `|0000>` state. It applies an X gate to `q[0]` and `q[1]`. It then applies a Toffoli gate with `q[0]` and `q[1]` as controls and `q[2]` as the target.
2. **State evolution:** 
   - Initial state: `|0000>`
   - After `X(q[0])` and `X(q[1])`: `|1100>`
   - The Toffoli gate flips the target `q[2]` if both controls (`q[0]` and `q[1]`) are in the `|1>` state. Since both are `|1>`, the target is flipped.
   - Final state before measurement: `|1110>`
3. **Probability distribution:** The state `|1110>` is a deterministic basis state. Measuring the qubits in the order `q[0]`, `q[1]`, `q[2]`, `q[3]` yields the bitstring `1110` with certainty.

Predicted probability distribution: {|1110>: 1.0}

### Reference answer

{'predicted_probs': {'14': 1.0}, 'explanation': 'Parametric variant of isqEval/479. Dimension: qubit_variant: q[3] -> q[4].'}
