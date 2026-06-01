# ISQ training COT RAG corpus: logic_gates shard 8

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/388

- task_id: `isqTrain/388`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_multi_register`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `4847`

### Prompt

Code this in isQ: implements a variant of the arithmetic_circuit pattern using Sum[1] -> Sum[3]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

The circuit is a 1-bit half adder that computes A + B = Sum + 2*Carry.

Initial state: |000000> (6 qubits: A[0], B[0], Sum[0], Sum[1], Sum[2], Carry[0])

Wait, let me re-read the qubit declarations:
- A[1]: 1 qubit
- B[1]: 1 qubit
- Sum[3]: 3 qubits
- Carry[1]: 1 qubit

Total: 6 qubits

Step 1: X(A[0]) and X(B[0])
After X gates on A[0] and B[0]:
|110000> (A[0]=1, B[0]=1, Sum[2:0]=000, Carry[0]=0)

Step 2: Toffoli(A[0], B[0], Carry[0])
This flips Carry[0] when both A[0]=1 and B[0]=1:
|110001> (Carry[0] becomes 1)

Step 3: CNOT(A[0], Sum[0]) then CNOT(B[0], Sum[0])
- CNOT(A[0], Sum[0]): Sum[0] = 0 XOR 1 = 1
State: |110101> (Sum[0]=1, but wait... Sum[0] is after B[0])

Wait, I need to be more careful about the qubit ordering. Let me think about which qubits are measured and in what order.

The measurements are: M(A[0]), M(B[0]), M(Sum[0]), M(Sum[1]), M(Sum[2]), M(Carry[0])

In the --probs output, "earlier measured qubit = higher bit", so:
- Bit 5 (MSB): A[0]
- Bit 4: B[0]
- Bit 3: Sum[0]
- Bit 2: Sum[1]
- Bit 1: Sum[2]
- Bit 0 (LSB): Carry[0]

Now let me trace through:

Initial: |A[0], B[0], Sum[0], Sum[1], Sum[2], Carry[0]> = |000000>

After X(A[0]), X(B[0]):
|110000>

After Toffoli(A[0], B[0], Carry[0]):
Carry[0] = 0 XOR (A[0] AND B[0]) = 0 XOR 1 = 1
|110001>

After CNOT(A[0], Sum[0]):
Sum[0] = 0 XOR A[0] = 0 XOR 1 = 1
|110101>

Wait, that doesn't match. Let me reconsider the ordering.

Actually, the qubits are declared as:
qbit A[1]; qbit B[1]; qbit Sum[3]; qbit Carry[1];

So the qubit indices would be:
- A[0] = qubit 0
- B[0] = qubit 1
- Sum[0] = qubit 2
- Sum[1] = qubit 3
- Sum[2] = qubit 4
- Carry[0] = qubit 5

But for the measurement bitstring, we need to track:
M(A[0]) - bit 5 (highest)
M(B[0]) - bit 4
M(Sum[0]) - bit 3
M(Sum[1]) - bit 2
M(Sum[2]) - bit 1
M(Carry[0]) - bit 0 (lowest)

So the state after all gates:
- A[0] = 1
- B[0] = 1
- Sum[0] = 0 XOR 1 XOR 1 = 0 (CNOT from A[0] then CNOT from B[0])
- Sum[1] = 0
- Sum[2] = 0
- Carry[0] = 1

Final state: |110001>

In binary with bit ordering:
Bit 5 (A[0]) = 1
Bit 4 (B[0]) = 1
Bit 3 (Sum[0]) = 0
Bit 2 (Sum[1]) = 0
Bit 1 (Sum[2]) = 0
Bit 0 (Carry[0]) = 1

So the bitstring is: 110001 (binary) = 49 (decimal)

This matches the predicted output: {|110001>: 1.0}

The circuit correctly implements a half adder: 1 + 1 = 0 (Sum) with

## isqTrain/1674

- task_id: `isqTrain/1674`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `5761`

### Prompt

Implement the following in isQ: Compute the parity of the 4-bit input |0010> using CNOT gates into an ancilla qubit. Measure the ancilla.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Compute the parity of the 4-qubit input state |0010> using an ancilla qubit and measure the result.
2. **Qubits:** 5 qubits total (4 input, 1 ancilla). Only the ancilla qubit is measured.
3. **Evolution:**
   - Initialize state to |0000>|0>. Apply X(q[2]) to prepare the input |0010>|0>.
   - Apply CNOT(q[0], anc[0]): Control is |0>, so ancilla remains |0>. State is |0010>|0>.
   - Apply CNOT(q[1], anc[0]): Control is |0>, so ancilla remains |0>. State is |0010>|0>.
   - Apply CNOT(q[2], anc[0]): Control is |1>, so ancilla flips to |1>. State is |0010>|1>.
   - Apply CNOT(q[3], anc[0]): Control is |0>, so ancilla remains |1>. State is |0010>|1>.
4. **Probabilities:** The final state of the ancilla is exactly |1>. Measuring the ancilla yields the bitstring "1" (value 1) with probability 1.0.

## isqTrain/1737

- task_id: `isqTrain/1737`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `1019`

### Prompt

请用isQ语言编写一个量子电路：Compute NOR of a=1, b=1 using quantum gates (De Morgan: AND of negated inputs). Store result in q[2].

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Compute NOR(1,1) using De Morgan's law: NOR(a,b) = AND(NOT a, NOT b), storing the result in q[2].
2. **Qubits**: 3 qubits (q[0], q[1], q[2]); all are measured.
3. **State evolution**:
   - Initialize |000⟩
   - X(q[0]); X(q[1]) → |110⟩ (encode a=1, b=1)
   - X(q[0]); X(q[1]) → |000⟩ (negate both inputs)
   - Toffoli(q[0], q[1], q[2]): since both controls are |0⟩, target doesn't flip → |000⟩ (AND(0,0) = 0)
   - X(q[0]); X(q[1]) → |110⟩ (restore original inputs)
4. **Result**: q[2] = 0, which is NOR(1,1) = NOT(1 OR 1) = 0. Final state |110⟩ yields measurement probability {|110⟩: 1.0}.

## isqTrain/1992

- task_id: `isqTrain/1992`
- task_type: `output_prediction`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3682`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
qbit q[3];
procedure main() {
    X(q[0]);
    ctrl nctrl X(q[0], q[1], q[2]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a step-by-step circuit analysis for an isQ program, explaining the operations, state evolution, and final probability distribution. The output must be concise (3-15 lines), use Dirac notation, and end with the predicted probabilities.

2.  **Analyze the isQ code:**
    *   `qbit q[3];`: 3 qubits initialized to $|000\rangle$.
    *   `X(q[0]);`: Apply X gate to q[0]. State becomes $|100\rangle$.
    *   `ctrl nctrl X(q[0], q[1], q[2]);`: Wait, what does `ctrl nctrl` mean in isQ? Let me double-check the syntax.
        *   Usually, Toffoli is `ctrl @[c1, c2] X(target)`.
        *   `ctrl nctrl X(q[0], q[1], q[2]);` looks like a custom or specific syntax for multi-controlled X. Wait, "nctrl" might be a typo in my understanding, or it means "negative control"? Let me look closely at `ctrl nctrl X(...)`.
        *   Ah, the prompt has `ctrl nctrl X(q[0], q[1], q[2]);`. Wait, could `nctrl` mean "no control"? No. Is it "N-control"?
        *   Let's reconsider standard isQ or typical QC frameworks. Actually, let's check the provided Expected measurement probabilities: `{'101': 1.0}`.
        *   Wait, The predicted output `{'101': 1.0}`. Let's trace to see how we get `101`.
        *   Start: $|000\rangle$
        *   `X(q[0])` -> $|100\rangle$ (q[0] is the right-most bit if standard convention is used, but wait. "array indexed by measurement bitstring (earlier measured qubit = higher bit)". So if q[0] is measured first, it's the highest bit? Usually, M(q[0]) is bit 2, M(q[1]) is bit 1, M(q[2]) is bit 0. So q[0]=1, q[1]=0, q[2]=0 is `100`.
        *   Next, `ctrl nctrl X(q[0], q[1], q[2])`. If it results in `101`, then q[2] must flip to 1.
        *   How does it flip? If it's a multi-controlled gate, maybe `q[0]` is the target and `q[1]` is the control? No, `X` has one parameter, so `q[2]` is the target of the X gate. `q[0]` and `q[1]` are controls.
        *   Wait, standard Toffoli: if q[0]=1 and q[1]=1, flip q[2]. But q[1] is 0. So standard Toffoli wouldn't flip it.
        *   What if `ctrl nctrl` means *negative* control? If it's negative control, it triggers when the control is 0. So `nctrl` on q[1] means if q[1]=0, flip q[2]. `ctrl` on q[0] means if q[0]=1, flip q[2].
        *   Let's check: q[0]=1 (positive control condition met). q[1]=0 (negative control condition met). So q[2] flips from 0 to 1.
        *   Final state: q[0]=1, q[1]=0, q[2]=1.
        *   Bitstring: q[0] is higher bit, q[2] is lower bit -> `101`. This perfectly matches the expected `{'101': 1.0}`!
        *   Therefore, `ctrl nctrl` indicates a multi-controlled X where the first control is positive and the second is negative. Or `nctrl` is a modifier for the second control qubit. Wait, standard isQ `ctrl @[c1, c2]` vs `ctrl nctrl`. Maybe it means `ctrl` applies to `q[0]`, and `nctrl` applies to `q[1]`.

3.  **Step-by-Step Trace:**
    *   Initial state: $|000\rangle$ (assuming q[0] is the first qubit, typically high bit in bitstring if measured first).
    *   After `X(q[0])`: $|100\rangle$.
    *   Apply `ctrl nctrl X(q[0], q[1], q[2])`: This applies a Toff

### Reference answer

{'predicted_probs': {'101': 1.0}, 'explanation': 'Expected probabilities: [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0]'}

## isqTrain/1677

- task_id: `isqTrain/1677`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `3872`

### Prompt

I need an isQ program to Compute the parity of the 4-bit input |0101> using CNOT gates into an ancilla qubit. Measure the ancilla.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Generate reasoning for an isQ quantum program computing the parity of a 4-bit input |0101> into an ancilla qubit and measuring it.
    *   Output format: ONLY the "## Reasoning" section. No code blocks. No isQ code.
    *   Length: 3-8 lines (since it's a simple circuit).
    *   Content requirements: Goal (1 line), Qubits needed/measured, Step-by-step state evolution (Dirac notation), Justification of probabilities.

2.  **Analyze the Circuit:**
    *   Input state: |0000>|0> (5 qubits: 4 data, 1 ancilla).
    *   Initialization: X(q[1]), X(q[3]) changes state to |0101>|0>.
    *   Parity computation:
        *   CNOT(q[0], anc[0]): ancilla flips because q[0]=1. State becomes |0101>|1>.
        *   CNOT(q[1], anc[0]): ancilla doesn't flip (q[1]=0). State stays |0101>|1>.
        *   CNOT(q[2], anc[0]): ancilla doesn't flip (q[2]=1? Wait, q[2] is 0 because state is |0101>. q[0]=1, q[1]=0, q[2]=1? No, standard qubit ordering: q[0] is right-most or left-most? Usually in Dirac |q_3 q_2 q_1 q_0>. Let's be careful. |0101> means q[3]=0, q[2]=1, q[1]=0, q[0]=1).
        *   Let's trace explicitly: |0101> means index 0 is 1, index 1 is 0, index 2 is 1, index 3 is 0.
        *   CNOT(q[0], anc[0]): control q[0] is |1>. ancilla flips to |1>. State: |0101>|1>.
        *   CNOT(q[1], anc[0]): control q[1] is |0>. ancilla stays |1>.
        *   CNOT(q[2], anc[0]): control q[2] is |1>. ancilla flips to |0>. State: |0101>|0>.
        *   CNOT(q[3], anc[0]): control q[3] is |0>. ancilla stays |0>.
    *   Final state: |0101>|0>.
    *   Measurement: M(anc[0]) measures ancilla in state |0>. Probability of |0> is 1.0.

3.  **Draft the Reasoning:**
    *   *Goal:* Compute the parity of the 4-qubit state |0101> by XORing the bits into an ancilla qubit and measuring the result.
    *   *Qubits:* 5 qubits total (4 data qubits, 1 ancilla); only the ancilla qubit is measured.
    *   *Evolution:*
        *   Initial |0000>|0> -> Apply X(q[1]), X(q[3]) -> |0101>|0> (where q[0]=1, q[1]=0, q[2]=1, q[3]=0).
        *   CNOT(q[0], anc): flips ancilla (q[0]=1) -> |0101>|1>.
        *   CNOT(q[1], anc): no flip (q[1]=0) -> |0101>|1>.
        *   CNOT(q[2], anc): flips ancilla (q[2]=1) -> |0101>|0>.
        *   CNOT(q[3], anc): no flip (q[3]=0) -> |0101>|0>.
    *   *Probabilities:* The final state is |0101>|0>, so measuring the ancilla yields |0> with a 100% probability (parity is even: 1+0+1+0 = 2).

4.  **Refine and Format:**
    *   Keep it within the 3-8 line limit.
    *   Check Dirac notation accuracy.

    Draft 2:
    ## Reasoning
    *   Goal: Calculate the parity of a 4-qubit state |0101> using CNOT gates into an ancilla qubit and measure it.
    *   Setup: Requires 5 qubits (4 data, 1 ancilla); only the ancilla qubit is measured.
    *   Evolution: Starts as |0000>|0>, then X gates prepare the data register to |0101>|0>

## isqTrain/1505

- task_id: `isqTrain/1505`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `1622`

### Prompt

Help me write isQ code that Compute the inner product mod 2 of a=001 and b=110 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Compute inner product mod 2 of a=001 and b=110 using Toffoli gates, storing result in ancilla.
2. Use 7 qubits: q[0-2] for a=001, q[3-5] for b=110, anc[0] for result.

## isqTrain/631

- task_id: `isqTrain/631`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `2694`

### Prompt

Code this in isQ: implements the gate_decomposition pattern. Include explicit identity operations in the circuit (X-X pair before M(q[3])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a gate_decomposition pattern with a triple-controlled X (Toffoli-3), demonstrating identity cancellation via an explicit X-X pair on q[3] before measurement.
2. **Qubits**: 4 qubits (q[0]–q[3]); only q[3] is measured.
3. **State evolution**: |0000⟩ →(X on q[0],q[1],q[2])→ |1110⟩ →(Toffoli with controls q[0],q[1],q[2], target q[3])→ |1111⟩ →(X on q[3])→ |1110⟩ →(X on q[3])→ |1111⟩. The X-X pair on q[3] is an identity operation (cancels out), preserving |1⟩ on q[3].
4. **Result**: M(q[3]) yields |1⟩ with probability 1.0, as the two sequential X gates on q[3] return it to |1⟩ after the Toffoli set it.

## isqTrain/661

- task_id: `isqTrain/661`
- task_type: `output_prediction`
- category: `logic_gates`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3204`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;

qbit q[2];

procedure main() {
    nctrl X(q[0], q[1]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations**: The circuit initializes two qubits, `q[0]` and `q[1]`, to the ground state |00>. It then applies a negatively controlled X gate (`nctrl X`) with `q[0]` as the control and `q[1]` as the target. Finally, both qubits are measured.
2. **State Evolution**:
   - Initial state: |00>
   - The `nctrl X` gate applies an X gate to the target qubit

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/216. Dimension: predict probabilities for reference circuit.'}

## isqTrain/1539

- task_id: `isqTrain/1539`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `59`

### Prompt

帮我写一个isQ程序：Compute the inner product mod 2 of a=110 and b=101 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning
- The goal is to compute the bitwise inner product mod 2 of a=110 and b=101, storing the result in an ancilla qubit.
- Seven qubits are used: `q[0..2]` for `a`, `q[3..5]` for `b`, and `anc[0]` for the result; only `anc[0]` is measured.
- Initialize the 7-qubit state to |0000000>. Apply X gates to encode a=110 and b=101, evolving the state

## isqTrain/378

- task_id: `isqTrain/378`
- task_type: `output_prediction`
- category: `logic_gates`
- difficulty: `basic`
- concept_tags: `isq_syntax_procedures`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2002`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;

qbit q[3]; // A, B, Output

procedure OR_gate() {
    // A OR B = NOT (NOT A AND NOT B)
    X(q[0]); X(q[1]); X(q[2]);
    Toffoli(q[0], q[1], q[2]);
    X(q[0]); X(q[1]);
}

procedure main() {
    X(q[0]); // A=1
    // B=0
    
    OR_gate();
    
    M(q[0]); M(q[1]); M(q[2]); // should be 101
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initial state:** The 3-qubit system starts in the ground state |000> (q[0]=A, q[1]=B, q[2]=Output).
2. **Main preparation:** `X(q[0])` flips qubit A, evolving the state to |100>.
3. **OR_gate execution:**
   - `X(q[0]), X(q[1]), X(q[2])` flip all qubits, evolving the state to |011>.
   - `Toffoli(q[0], q[1], q[2])` flips the Output qubit because both q[0] and q[1] are |1>, resulting in |010>.
   - `X(q[0]), X(q[1])` restore qubits A and B to their inputs before the OR gate, resulting in |101>.
4. **Final state:** The quantum state before measurement is |101>, which correctly represents A=1, B=0, A OR B = 1.
5. **Measurement:** Measuring q[0], q[1], and q[2] deterministically yields this bitstring.

Predicted probability distribution: {|101>: 1.0}

### Reference answer

{'predicted_probs': {'5': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/115. Dimension: predict probabilities for reference circuit.'}
