# ISQ training COT RAG corpus: logic_gates shard 3

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/663

- task_id: `isqTrain/663`
- task_type: `output_prediction`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3912`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

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

1.  **Analyze the isQ program**:
    *   `qbit q[3];` initializes 3 qubits: $|q_0 q_1 q_2\rangle = |000\rangle$.
    *   `X(q[0]);` applies an X gate to q[0]. State becomes $|100\rangle$.
    *   `ctrl nctrl X(q[0], q[1], q[2]);` -> Wait, `nctrl` is not standard isQ syntax. Analyzing the or typical ISQ commands. Wait, the prompt says `ctrl nctrl X(...)`. Is this a typo for multi-control? Let's check `ctrl nctrl`. Ah, maybe it means "negative control"? Or is it a typo in my understanding of the prompt? Let's re-read carefully: `ctrl nctrl X(q[0], q[1], q[2])`. Actually, wait, `ctrl nctrl` might not be standard. Wait, `ctrl` means controlled. If there's no list like `@[c1, c2]`, then `ctrl X(q[0], q[1], q[2])` implies a multi-controlled X (Toffoli for 2 controls, but here 3 qubits are passed to X?). Wait, X normally takes 1 qubit. If it takes 3 qubits, `ctrl X(a, b, c)` usually means `a` and `b` are controls, `c` is target. But here it says `ctrl nctrl X(...)`. Let's assume it's a multi-controlled X. Wait, if it's `ctrl nctrl`, maybe it's a Toffoli with 1 negative control and 1 positive control? `nctrl` = negative control.
    *   Wait, let's look at standard isQ: `ctrl @[c1, c2] X(target)`. But the code has `ctrl nctrl X(q[0], q[1], q[2])`. Oh, I see. Is "nctrl" a typo for something? Or maybe it's `ctrl` with negative controls? No, it's just `ctrl nctrl`. Wait, looking closely: "nctrl" might be an artifact of a generated program, or maybe it implies negative controls. Let me think if `nctrl` is a keyword in isQ. Actually, wait! IsQ has `nctrl` or maybe it means `ctrl nctrl` is a typo for `ctrl @[q[0], q[1]] X(q[2])`? No, "nctrl" is not in the provided syntax reference. Wait! The prompt says "ctrl nctrl X(...)". This is likely a typo in the user's prompt from a dataset, or it's meant to be `ctrl X(q[0], q[1], q[2])` but with `nctrl` meaning negative control? Let's assume it's a negative control on q[0] and positive on q[1]? No, `ctrl nctrl` might just be a typo for `ctrl`. Wait, if `nctrl` means negative control, then it's a gate that applies X to q[2] if q[0] is |0> (nctrl) and q[1] is |1> (ctrl).
    *   Let's check the predicted output: `Expected measurement probabilities: {|101>: 1.0}`.
    *   If the state is |101>, then q[0]=1, q[1]=0, q[2]=1. (Assuming standard bitstring ordering |q0 q1 q2>).
    *   Let's trace:
        *   Init: |000>
        *   `X(q[0])`: |100>
        *   Now, if `ctrl nctrl X(q[0], q[1], q[2])` means: q[0] is negative control (activates if |0>), q[1] is positive control (activates if |1>), target is q[2]. But q[0] is |1> and q[1] is |0>. Neither condition is met! X would not be applied. State remains |100>. But expected is |101>.
        *   What if `ctrl nctrl` means: q[0] is negative control, q[1] is negative control? Neither met.
        *   Wait, look at `ctrl nctrl`. In some quantum computing frameworks, `nctrl` means negative control. But wait, if `q[0]` is negative control, it means "apply if 0". Since q[0] is 1, it's not applied.
        *   Wait! Is it possible that `ctrl nctrl X(q[0], q[1], q[2])` is a multi-controlled X where

### Reference answer

{'predicted_probs': {'5': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/217. Dimension: predict probabilities for reference circuit.'}

## isqTrain/1730

- task_id: `isqTrain/1730`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`
- source: `isq_train_cot`
- dataset_index: `2205`

### Prompt

Implement a quantum circuit in isQ: Compute XNOR of a=0, b=0 using quantum gates. Store result in q[2].

### Chain-of-thought reasoning

## Reasoning
Goal: Compute XNOR(0, 0) using a quantum circuit, storing the result in q[2].
Qubits: 3 qubits (q[0]=a=0, q[1]=b=0, q[2]=result), all measured.
Step-by-step evolution:
1. Initial state: |000⟩ (q[0]=|0⟩, q[1]=|0⟩, q[2]=|0⟩)
2. CNOT(q[0], q[2]): control q[0] is |0⟩, target q[2] unchanged → |000⟩
3. CNOT(q[1], q[2]): control q[1] is |0⟩, target q[2] unchanged → |000⟩
4. X(q[2]): flips q[2] from |0⟩ to |1⟩ → |001⟩
Expected probabilities: {|001⟩: 1.0} because XNOR(0,0) = 1, and measurements deterministically yield q[2]=|1⟩.

## isqTrain/1520

- task_id: `isqTrain/1520`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `4070`

### Prompt

Write an isQ program that Compute the inner product mod 2 of a=011 and b=111 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

Let me analyze this problem step by step.

Goal: Compute the inner product mod 2 of a=011 and b=111 using Toffoli gates, storing result in ancilla.

The inner product mod 2 is: a·b = a[0]*b[0] ⊕ a[1]*b[1] ⊕ a[2]*b[2]
where ⊕ is XOR.

a = 011, b = 111
a·b = 0*1 ⊕ 1*1 ⊕ 1*1 = 0 ⊕ 1 ⊕ 1 = 0

So the result should be 0.

Let me trace through the circuit:

1. We have q[6] and anc[1], all initialized to |0⟩.

2. Initialize a = 011:
   - q[0] = 0 (no X gate)
   - q[1] = 1 (X gate applied)
   - q[2] = 1 (X gate applied)

3. Initialize b = 111:
   - q[3] = 1 (X gate applied)
   - q[4] = 1 (X gate applied)
   - q[5] = 1 (no X gate shown in code, but let me re-read)

Wait, let me re-read the code:
- X(q[1]); X(q[2]); X(q[3]); - this sets q[1]=1, q[2]=1, q[3]=1
- X(q[4]); X(q[5]); - this sets q[4]=1, q[5]=1

Hmm, this is a bit confusing. Let me think about the structure:
- q[0], q[1], q[2] should represent a=011
- q[3], q[4], q[5] should represent b=111

For a=011:
- q[0] = 0 (no X)
- q[1] = 1 (X applied)
- q[2] = 1 (X applied)

For b=111:
- q[3] = 1 (X applied)
- q[4] = 1 (X applied)
- q[5] = 1 (X applied)

So the initialization in the code is:
- X(q[1]); X(q[2]); for a
- X(q[3]); X(q[4]); X(q[5]); for b

But wait, the code shows X(q[3]) in the first block and X(q[4]), X(q[5]) in the second block. That's 5 X gates total which gives:
- q[1]=1, q[2]=1, q[3]=1, q[4]=1, q[5]=1

Hmm, but then a would be q[0]=0, q[1]=1, q[2]=1 → 011 ✓
And b would be q[3]=1, q[4]=1, q[5]=1 → 111 ✓

Wait, I need to re-count the X gates in the code:

That's X on q[1], q[2], q[3], q[4], q[5]. So:
- q[0]=0, q[1]=1, q[2]=1 → a = 011 ✓
- q[3]=1, q[4]=1, q[5]=1 → b = 111 ✓

Now the Toffoli gates:
1. ctrl ctrl X(q[0], q[3], anc[0]); - flips anc[0] if q[0]=1 AND q[3]=1
   - q[0]=0, so no flip
2. ctrl ctrl X(q[1], q[4], anc[0]); - flips anc[0] if q[1]=1 AND q[4]=1
   - q[1]=1, q[4]=1, so anc[0] flips to 1
3. ctrl ctrl X(q[2], q[5], anc[0]); - flips anc[0] if q[2]=1 AND q[5]=1
   - q[2]=1, q[5]=1, so anc[0] flips from 1 back to 0

Final anc[0] = 0

State evolution:
1. |0000000⟩ (7 qubits: q[0-5] and anc[0])
2. After X gates: |0111110⟩
3. After first Toffoli (no flip): |0111110⟩

## isqTrain/1665

- task_id: `isqTrain/1665`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `basic`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `1290`

### Prompt

Code this in isQ: Compute the parity of the 2-bit input |11> using CNOT gates into an ancilla qubit. Measure the ancilla.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Compute the parity (XOR) of a 2-bit input |11> into an ancilla qubit and measure it.
2. **Qubits**: 3 total (q[0], q[1], anc[0]); only anc[0] is measured.
3. **State evolution**:
   - Start: |000⟩
   - X(q[0]): |100⟩
   - X(q[1]): |110⟩
   - CNOT(q[0], anc[0]): q[0]=|1⟩ flips anc → |111⟩
   - CNOT(q[1], anc[0]): q[1]=|1⟩ flips anc again → |110⟩
4. **Result**: anc[0] = |0⟩ since parity of 1⊕1 = 0 (two flips cancel). Measurement yields {|0⟩: 1.0}.

## isqTrain/1503

- task_id: `isqTrain/1503`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `4604`

### Prompt

Write isQ code for the following quantum task: Compute the inner product mod 2 of a=001 and b=100 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Compute the bitwise inner product mod 2 of binary strings `a=001` and `b=100`, storing the result in an ancilla qubit.
2. **Qubits**: 6 data qubits (first 3 for `a`, next 3 for `b`) and 1 ancilla qubit; only the ancilla is measured.
3. **Initialization**: `X(q[2])` and `X(q[3])` set the states to represent `a=001` and `b=100`, preparing the system in `|001>|100>|0>`.
4. **Evolution**: Three Toffoli gates compute the `AND` of corresponding bits: `ctrl ctrl X(q[0], q[3], anc)`, `ctrl ctrl X(q[1], q[4], anc)`, and `ctrl ctrl X(q[2], q[5], anc)`.
5. Since no pair of corresponding bits is simultaneously `1` (i.e., `0*1=0`, `0*0=0`, `1*0=0`), no Toffoli gate triggers, leaving the ancilla unchanged.
6. **Probabilities**: The final state of the ancilla is `|0>`, meaning measurement yields `|0>` with probability 1.0.

## isqTrain/389

- task_id: `isqTrain/389`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_multi_register`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3849`

### Prompt

帮我写一个isQ程序：implements a variant of the arithmetic_circuit pattern using Carry[1] -> Carry[3]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement a 1-bit half adder (A + B = Sum, Carry) using an expanded 3-qubit Carry register, testing case 1+1=10.

Qubits: A[1], B[1], Sum[1], Carry[3] — all 6 measured (M order: A,B,Sum,Carry[0-2]).

State evolution:
1. |000000⟩ — initial state (A,B,Sum,Carry[0-2])
2. X(A[0]) → |100000⟩
3. X(B[0]) → |110000⟩
4. Toffoli(A[0],B[0],Carry[0]) → |110100⟩ (Carry[0]=1 since both controls |1⟩)
5. CNOT(A[0],Sum[0]) → |111100⟩ (Sum flips to 1)
6. CNOT(B[0],Sum[0]) → |110100⟩ (Sum flips back to 0: 1⊕1=0)

Final state |110100⟩ yields A=1, B=1, Sum=0, Carry[0]=1, Carry[1]=0, Carry[2]=0 — correct half-adder result (1+1=10 binary), with expanded register qubits remaining in |0⟩.

## isqTrain/1535

- task_id: `isqTrain/1535`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `560`

### Prompt

帮我写一个isQ程序：Compute the inner product mod 2 of a=110 and b=001 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Compute the bitwise inner product mod 2 of binary strings a=110 and b=001 using Toffoli gates, storing the result in an ancilla qubit.
2. **Qubits:** 7 qubits total (`q[0..2]` for `a`, `q[3..5]` for `b`, `anc[0]` for the result). Only `anc[0]` is measured.
3. **State Evolution:**
   - Initialize `a` and `b` via X gates: `X(q[0])`, `X(q[1])`, and `X(q[5])` set the state to |110> for `q[0..2]` and |001> for `q[3..5]`. The ancilla starts in |0>.
   - Apply `ctrl ctrl X(q[0], q[3], anc[0])`: Controls are |1> and |0> (product 0), so the ancilla remains |0>.
   - Apply `ctrl ctrl X(q[1], q[4], anc[0])`: Controls are |1> and |0> (product 0), so the ancilla remains |0>.
   - Apply `ctrl ctrl X(q[2], q[5], anc[0])`: Controls are |0> and |1> (product 0), so the ancilla remains |0>.
4. **Expected Probabilities:** The inner product is $1\cdot0 + 1\cdot0 + 0\cdot1 = 0$. Since the total number of flips to the ancilla is 0 (an even number), its final state is |0>. Measurement yields {|0>: 1.0}.

## isqTrain/1500

- task_id: `isqTrain/1500`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `2116`

### Prompt

用isQ实现Compute the inner product mod 2 of a=001 and b=001 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning
Goal: Compute the inner product mod 2 of a=001 and b=001 using Toffoli gates, storing result in an ancilla qubit.
Qubits: 6 data qubits (q[0-2] for a, q[3-5] for b) initialized to |0⟩, plus ancilla qubit measured at the end.
Initial state: |000000⟩|0⟩. After X(q[2]) and X(q[5]): |001001⟩|0⟩ (a[2]=1, b[2]=1).
Toffoli(q[0],q[3],anc): controls are |0⟩|0⟩ → no flip. Toffoli(q[1],q[4],anc): controls are |0⟩|0⟩ → no flip.
Toffoli(q[2],q[5],anc): controls are |1⟩|1⟩ → flips ancilla. Final state: |001001⟩|1⟩.
Measurement yields |1⟩ with probability 1.0, since inner product mod 2 = (0·0)⊕(0·0)⊕(1·1) = 1.

## isqTrain/634

- task_id: `isqTrain/634`
- task_type: `output_prediction`
- category: `logic_gates`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `5342`

### Prompt

帮我分析一下这个量子程序的输出：

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
1. The initial 4-qubit state is |0000⟩.
2. Applying X gates to q[0], q[1], and q[2] flips them to |1⟩, evolving the state to |1110⟩.
3. The `ctrl ctrl ctrl X` gate applies an X gate to the target q[3] only if the control qubits (q[0], q[1], q[2]) are in the |1⟩ state. 
4. Since all three controls are |1⟩, the target q[3] is flipped from |0⟩ to |1⟩, resulting in the final state |1111⟩.
5. Measuring q[3] deterministically yields the state |1⟩.

Predicted probability distribution: {|1⟩: 1.0}

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/211. Dimension: predict probabilities for reference circuit.'}

## isqTrain/1491

- task_id: `isqTrain/1491`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `263`

### Prompt

Implement the following in isQ: Compute the inner product mod 2 of a=01 and b=01 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Compute the inner product mod 2 of binary strings a=01 and b=01, storing the result in an ancilla qubit.

**Qubits:** 5 total — q[0..1] for a, q[2..3] for b, anc[0] for result. Only anc[0] is measured.

**State evolution:**
1. **Initial:** |00000⟩ (all qubits in |0⟩)
2. **X(q[1]):** Sets a=01 → |01000⟩
3. **X(q[3]):** Sets b=01 → |01010⟩
4. **Toffoli(q[0], q[2], anc[0]):** Controls are q[0]=|0⟩, q[2]=|0⟩ → no flip → |01010⟩
5. **Toffoli(q[1], q[3], anc[0]):** Controls are q[1]=|1⟩, q[3]=|1⟩ → flip anc → |01011⟩

**Result:** anc[0] = |1⟩ since a·b mod 2 = (0·0 + 1·1) mod 2 = 1. Measurement yields {|1⟩: 1.0}.
