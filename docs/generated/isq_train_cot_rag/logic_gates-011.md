# ISQ training COT RAG corpus: logic_gates shard 11

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1509

- task_id: `isqTrain/1509`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `4601`

### Prompt

用isQ实现Compute the inner product mod 2 of a=010 and b=011 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Compute the bitwise inner product mod 2 of a=010 and b=011, storing the result in an ancilla.
2. Qubits: 6 data qubits (q[0..5]) for the two 3-bit strings, 1 ancilla (anc[0]) measured.
3. State evolution:
   - Initialize |000000, 0>
   - X(q[1]) (sets a[1]=1): |010000, 0>
   - X(q[4]), X(q[5]) (sets b[1]=1, b[2]=1): |010011, 0>
   - Toffoli(q[0], q[3], anc[0]): controls 0,0 → no flip: |010011, 0>
   - Toffoli(q[1], q[4], anc[0]): controls 1,1 → flip anc: |010011, 1>
   - Toffoli(q[2], q[5], anc[0]): controls 0,1 → no flip: |010011, 1>
4. The ancilla is deterministically |1>, yielding measurement probability {|1>: 1.0}.

## isqTrain/1511

- task_id: `isqTrain/1511`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `3600`

### Prompt

Write an isQ program that Compute the inner product mod 2 of a=010 and b=101 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning
Goal: Compute the inner product mod 2 of binary vectors a=010 and b=101 using Toffoli gates, storing the result in an ancilla qubit.
Seven qubits are used (q[0..5] for the inputs, anc[0] for the result), and only anc[0] is measured.
1. Initialize 6 data qubits to |0> and ancilla to |0>. State: |000000>|0>
2. Apply X to q[1] (for a=010), and X to q[3], q[5] (for b=101). State becomes |010101>|0>.
3. Apply Toffoli gates to AND the corresponding bits of a and b into anc[0]. Since no pairs of corresponding bits are both 1 (0*1=0, 1*0=0, 0*1=0), the target ancilla is never flipped. State remains |010101>|0>.
4. The inner product mod 2 is 0, so the ancilla is in state |0>. Measuring anc[0] yields |0> with 100% probability.

## isqTrain/384

- task_id: `isqTrain/384`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_multi_register`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `60`

### Prompt

Implement a quantum circuit in isQ: implements a variant of the arithmetic_circuit pattern using Sum[1] -> Sum[2]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning
1. The circuit implements a 1-bit half adder computing 1+1, using 5 qubits (A, B, Sum[0], Sum[1], Carry) which are all measured.
2. Initial state is |00000>. X gates on A[0] and B[0] set inputs to |1>, yielding |11000>.
3. Toffoli(A[0], B[0], Carry[0]) computes the carry bit (1 AND 1 = 1), evolving the state to |11001>.
4. CNOT(A[0], Sum[0]) and CNOT(B[0], Sum[0]) compute the sum bit (1 XOR 1 = 0), flipping Sum[0] to |1> then back to |0>, resulting in the final state |11001>.
5. The final state deterministically collapses to |11001> upon measurement, representing A=1, B=1, Sum=0, and Carry=1.

## isqTrain/1494

- task_id: `isqTrain/1494`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `12`

### Prompt

Write isQ code for the following quantum task: Compute the inner product mod 2 of a=10 and b=01 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Goal: Generate a concise reasoning section for an isQ quantum program computing the inner product mod 2.
    *   Input values: a = 10, b = 01.
    *   Code provided uses `q[0]`, `q[1]` for 'a' bits (wait, standard a=10 means a[0]=0, a[1]=1? Let's check the code: `X(q[0])` and `X(q[3])`. If `q[0]` is a[0] and `q[1]` is a[1], then `q[2]` is b[0], `q[3]` is b[1]. `X(q[0])` sets a[0]=1. `X(q[3])` sets b[1]=1. Thus a=10 (in bits a[1]a[0] = 10? No, if a[0]=1 and a[1]=0, a is 01. If a is indexed a[0]=1, a[1]=0, and b[0]=0, b[1]=1, then `ctrl ctrl X(q[0], q[2], anc[0])` is `ctrl ctrl X(1, 0, anc)` -> nothing. `ctrl ctrl X(q[1], q[3], anc[0])` is `ctrl ctrl X(0, 1, anc)` -> nothing. Inner product is 0. Code expects |0>: 1.0. So this matches.
    *   Actually, let's trace carefully:
        *   `q[0]` = a_0 -> X(q[0]) sets it to 1.
        *   `q[1]` = a_1 -> stays 0.
        *   `q[2]` = b_0 -> stays 0.
        *   `q[3]` = b_1 -> X(q[3]) sets it to 1.
        *   Inner product mod 2 = a_0*b_0 + a_1*b_1 mod 2 = 1*0 + 0*1 mod 2 = 0.
        *   `anc[0]` starts at 0.
        *   `ctrl ctrl X(q[0], q[2], anc[0])` -> controls are |1> and |0> -> anc stays |0>.
        *   `ctrl ctrl X(q[1], q[3], anc[0])` -> controls are |0> and |1> -> anc stays |0>.
        *   Measurement yields |0> with probability 1.0.
    *   Wait, what if `q[0]` and `q[1]` are the bits of 'a' and `q[2]` and `q[3]` are the bits of 'b'?
        *   a = 10 -> a[0] = 0, a[1] = 1? If `X(q[0])` sets `q[0]`=1, then `a` in binary is `q[1]q[0]` = `10` (which is 2 in decimal).
        *   b = 01 -> `X(q[3])` sets `q[3]`=1, so `q[3]q[2]` = `01` (which is 1 in decimal).
        *   If `q[0]`=1, `q[1]`=0, `q[2]`=0, `q[3]`=1.
        *   `ctrl ctrl X(q[0], q[2], anc[0])` -> 1 and 0 -> anc stays |0>.
        *   `ctrl ctrl X(q[1], q[3], anc[0])` -> 0 and 1 -> anc stays |0>.
        *   Result is |0>.
    *   Alternatively, the task description says "a=10, b=01". Usually "10" and "01" are just strings of bits.
    *   Regardless of indexing, in the provided code, q[0]=1, q[1]=0, q[2]=0, q[3]=1.
    *   Inner product mod 2 is `q[0]*q[2] + q[1]*q[3]` = 1*0 + 0*1 = 0.
    *   The task is just to output the *Reasoning section* based on the prompt and circuit implementation.

2.  **Drafting the Reasoning:**
    *   Goal: Compute inner product mod 2 of a=10 and b=01 using Toffoli

## isqTrain/2577

- task_id: `isqTrain/2577`
- task_type: `code_equivalence`
- category: `logic_gates`
- difficulty: `basic`
- concept_tags: `global_phase`, `isq_syntax_procedures`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5743`

### Prompt

Compare these two isQ programs. Do they give the same probability distribution?

First program:
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

Second program:
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
    // Equivalent implementation with global phase
    GPhase(0.0);
    X(q[0]); // A=1
    // B=0
    
    OR_gate();
    
    M(q[0]); M(q[1]); M(q[2]); // should be 101
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. Program A initializes 3 qubits to |000>, applies X to q[0] to get |100>, and uses a custom OR gate to compute A OR B. The OR gate inverts inputs and the output qubit, applies a Toffoli, and inverts the inputs back, leaving the system in the |101> state.
2. Program B performs the exact same initialization and logical operations, but introduces a `GPhase(0.0)` gate at the beginning of the main procedure.
3. The only difference between the two programs is this added global phase gate.
4. `GPhase(0.0)` applies a global phase factor of $e^{i \cdot 0} = 1$, which has no effect on the quantum state vector or measurement probabilities.
5. Both programs deterministically measure the final state |101>, yielding the exact same probability distribution.
Equivalent: Yes

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/1528

- task_id: `isqTrain/1528`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `5399`

### Prompt

Implement a quantum circuit in isQ: Compute the inner product mod 2 of a=101 and b=001 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Generate a concise reasoning section for a specific isQ quantum program.
    *   Problem: Compute the inner product mod 2 of a=101 and b=001 using Toffoli gates, storing result in ancilla.
    *   Reference code provided for context.
    *   Output format: Markdown starting with "## Reasoning".
    *   Constraints: 3-8 lines for simple, up to 15 for complex. Precise state evolution (Dirac notation). NO isQ code block.

2.  **Analyze the Circuit/Problem:**
    *   Goal: Compute the bitwise inner product mod 2 (binary dot product) of $a=101$ and $b=001$, saving the result to an ancilla qubit.
    *   Inputs: $a_0=1, a_1=0, a_2=1$ (stored in $q[0..2]$), $b_0=0, b_1=0, b_2=1$ (stored in $q[3..5]$).
    *   Initialization: $|0\rangle^{\otimes 7}$
    *   State prep: $X(q[0])$, $X(q[2])$, $X(q[5])$ sets $q_0=1, q_2=1, q_5=1$.
    *   Initial computational state: $|1,0,1, 0,0,1\rangle_q \otimes |0\rangle_{anc}$
    *   Toffoli 1: `ctrl ctrl X(q[0], q[3], anc[0])` -> $q_0=1, q_3=0$, so ancilla remains 0.
    *   Toffoli 2: `ctrl ctrl X(q[1], q[4], anc[0])` -> $q_1=0, q_4=0$, so ancilla remains 0.
    *   Toffoli 3: `ctrl ctrl X(q[2], q[5], anc[0])` -> $q_2=1, q_5=1$, so ancilla flips to 1.
    *   Final state: $|1,0,1, 0,0,1\rangle_q \otimes |1\rangle_{anc}$.
    *   Measurement on `anc[0]`: Expect 100% probability of $|1\rangle$.

3.  **Draft the Reasoning:**
    *   *Goal:* Compute the bitwise inner product mod 2 of a=101 and b=001 using Toffoli gates into an ancilla qubit.
    *   *Qubits & Measurement:* Uses 7 qubits (6 inputs + 1 ancilla). Only the ancilla (`anc[0]`) is measured.
    *   *Step 1:* Initialize to $|0\rangle^{\otimes 7}$, then apply X gates to $q[0], q[2], q[5]$ setting their states to $|1\rangle$, resulting in $|1010010\rangle$.
    *   *Step 2:* The first Toffoli checks $q[0] \cdot q[3]$ ($1 \cdot 0 = 0$), leaving the ancilla as $|0\rangle$.
    *   *Step 3:* The second Toffoli checks $q[1] \cdot q[4]$ ($0 \cdot 0 = 0$), leaving the ancilla as $|0\rangle$.
    *   *Step 4:* The third Toffoli checks $q[2] \cdot q[5]$ ($1 \cdot 1 = 1$), flipping the ancilla to $|1\rangle$.
    *   *Conclusion:* The final state of the ancilla is $|1\rangle$, so measurement yields $|1\rangle$ with probability 1.0.

4.  **Refine and Condense (Targeting 3-8 lines):**
    *   Line 1: The goal is to compute the bitwise inner product mod 2 of a=101 and b=001.
    *   Line 2: The circuit uses 7 qubits (6 for inputs, 1 ancilla), measuring only the ancilla.
    *   Line 3: X gates initialize the state to $|1\rangle_0|0\rangle_1|1\rangle_2|0\rangle_3|0\rangle_4|1\rangle_5|0\rangle_{anc}$.
    *   Line 4: Three Toffoli gates act as classical AND gates, flipping the ancilla if both controls are $|1\rangle

## isqTrain/1508

- task_id: `isqTrain/1508`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `4932`

### Prompt

用isQ实现Compute the inner product mod 2 of a=010 and b=010 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning
**Goal**: Compute the inner product mod 2 of a=010 and b=010 using Toffoli gates, storing result in an ancilla qubit.

**Qubits**: 7 total (6 data: q[0-2] for a, q[3-5] for b; 1 ancilla). Only anc[0] is measured.

**State evolution**:
1. Initial: |0000000⟩ (all 7 qubits in |0⟩)
2. X(q[1]): Sets a[1]=1 → |0100000⟩
3. X(q[4]): Sets b[1]=1 → |0100100⟩
4. Toffoli(q[0], q[3], anc[0]): Controls (0,0) not both |1⟩ → no flip, state unchanged
5. Toffoli(q[1], q[4], anc[0]): Controls (1,1) both |1⟩ → flips anc[0] → |0100101⟩
6. Toffoli(q[2], q[5], anc[0]): Controls (0,0) not both |1⟩ → no flip, state unchanged

**Expected probabilities**: Inner product mod 2 = a[0]·b[0] ⊕ a[1]·b[1] ⊕ a[2]·b[2] = 0·0 ⊕ 1·1 ⊕ 0·0 = 1. Final state of anc[0] is |1⟩, so measurement yields {|1⟩: 1.0}.

## isqTrain/2248

- task_id: `isqTrain/2248`
- task_type: `bug_fix`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `isq_syntax_multi_register`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `4912`

### Prompt

I'm getting wrong output from this isQ code. What's the bug and how do I fix it?

```isq
import std;

qbit A[1]; qbit B[1]; qbit Cin[1]; 
qbit Sum[1]; qbit Cout[1];

qbit anc[1];

procedure main() {
    // 1-bit full adder
    // Test case: 1 + 1 + 1 -> Sum=1, Cout=1
    X(A[0]); X(B[0]); X(Cin[0]);
    
    // Sum = A ^ B ^ Cin
    CNOT(A[0], Sum[0]);
    CNOT(B[0], Sum[0]);
    // BUG: removed CNOT(Cin[0], Sum[0]);
    
    // Cout = (A & B) | (Cin & (A ^ B))
    // We can use an ancilla or compute in place if possible
    // Let's use Cout directly
    Toffoli(A[0], B[0], Cout[0]); 
    // Now Cout has A&B. 
    // We need to add Cin & (A^B) to it. Since both terms cannot be 1 at the same time,
    // XOR is the same as OR here.

    CNOT(A[0], anc[0]); CNOT(B[0], anc[0]); // anc = A^B
    Toffoli(Cin[0], anc[0], Cout[0]); // Cout ^= Cin & (A^B)
    
    M(A[0]); M(B[0]); M(Cin[0]); M(Sum[0]); M(Cout[0]);
}

``` (bug type: a gate is missing)

### Chain-of-thought reasoning

## Bug Analysis

**The bug:** The CNOT gate `CNOT(Cin[0], Sum[0])` is missing from the Sum computation. The comment explicitly marks it as removed.

**The fix:** Add `CNOT(Cin[0], Sum[0])` after the first two CNOTs so that Sum correctly computes A ⊕ B ⊕ Cin.

**State evolution (A=B=Cin=1):**
1. Initial: |00000⟩ → X on A,B,Cin → |11100⟩
2. CNOT(A,Sum): Sum ⊕= A=1 → |11110⟩
3. CNOT(B,Sum): Sum ⊕= B=1 → |11100⟩
4. **CNOT(Cin,Sum)**: Sum ⊕= Cin=1 → |11110⟩ (this was missing, without it Sum=0 incorrectly)
5. Toffoli(A,B,Cout): Cout = A&B = 1 → |11111⟩
6. CNOT(A,anc); CNOT(B,anc): anc = A⊕B = 0
7. Toffoli(Cin,anc,Cout): Cout ⊕= Cin&anc = 0 → Cout stays 1 → |11111⟩ ✓

## isqTrain/1731

- task_id: `isqTrain/1731`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `563`

### Prompt

Write isQ code for the following quantum task: Compute NOR of a=0, b=0 using quantum gates (De Morgan: AND of negated inputs). Store result in q[2].

### Chain-of-thought reasoning

The user wants me to generate reasoning for a NOR gate computation using quantum gates, specifically computing NOR(0,0) using De Morgan's theorem.

Let me trace through the circuit:

1. Initialize 3 qubits: q[0]=|0⟩, q[1]=|0⟩, q[2]=|0⟩
   State: |000⟩

2. Apply X to q[0] and X to q[1]:
   q[0] flips to |1⟩, q[1] flips to |1⟩
   State: |110⟩

3. Apply Toffoli (ctrl ctrl X) with controls q[0], q[1] and target q[2]:
   Since both controls are |1⟩, the target q[2] flips to |1⟩
   State: |111⟩

4. Apply X to q[0] and X to q[1] again:
   q[0] flips back to |0⟩, q[1] flips back to |0⟩
   State: |011⟩

Wait, that doesn't seem right. Let me re-read the problem.

The goal is to compute NOR(0,0) = 1.

NOR via De Morgan: NOT(a) AND NOT(b) = NOR(a,b)

So the approach is:
1. Negate inputs a and b (apply X to q[0] and q[1])
2. Compute AND of the negated inputs using Toffoli
3. This gives us NOR directly

Let me trace again:
1. Initial: |000⟩
2. X(q[0]), X(q[1]): |110⟩
3. Toffoli(q[0], q[1], q[2]): |111⟩
4. X(q[0]), X(q[1]): |011⟩

So q[2] = 1, which is correct for NOR(0,0) = 1.

But wait, the expected measurement is |001⟩ with probability 1.0. The measurement bitstring has earlier measured qubit as higher bit.

So if we measure q[0], q[1], q[2] in that order:
- q[0] = 0 (highest bit)
- q[1] = 1 (middle bit)
- q[2] = 1 (lowest bit)

That gives |011⟩ in bitstring = 3, not |001⟩.

Hmm, let me reconsider. The predicted output {|001>: 1.0}. That means:
- q[0] = 0
- q[1] = 0
- q[2] = 1

But after the Toffoli, we have |111⟩, then after uncomputing q[0] and q[1], we get |011⟩.

Wait, I need to re-read The implementation more carefully. The comment says:

But wait, we applied X to q[0] and q[1] to get |1⟩|1⟩. Then Toffoli gives |1⟩|1⟩|1⟩. Then we apply X again to get |0⟩|1⟩|1⟩ = |011⟩.

Hmm, that's not |001⟩.

Let me re-read again... Actually, the problem says a=0, b=0. So the inputs are:
- q[0] = 0 (input a)
- q[1] = 0 (input b)
- q[2] = 0 (ancilla for result)

NOR(0,0) = NOT(0 OR 0) = NOT(0) = 1

Using De Morgan: NOR(a,b) = NOT(a) AND NOT(b)
- NOT(0) = 1
- NOT(0) = 1
- 1 AND 1 = 1 ✓

So the circuit should:
1. Negate inputs: X(q[0]), X(q[1]) → q[0]=1, q[1]=1
2. AND the negated inputs: Toffoli → q[2]=1
3. Uncompute the input negations: X(q[0]), X(q[1]) → q[0]=0, q[1]=0

Final state: |001⟩

Wait, that's what I calculated. Let me trace more carefully:

Initial: q[0]=|0⟩, q[1]=|0⟩, q[2]=|0⟩ → |000⟩

After X(q[0]): q[0]=|1⟩ → |100⟩
After X(q[1]): q[1]=|1⟩ → |110⟩

After Toffoli(q[0], q[1],

## isqTrain/1523

- task_id: `isqTrain/1523`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `4541`

### Prompt

Create an isQ quantum circuit that Compute the inner product mod 2 of a=100 and b=011 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning

**Goal**: Compute the inner product mod 2 of a=100 and b=011 using Toffoli gates.

**Qubit setup**: 6 data qubits (q[0..5]) encode a and b bitwise; 1 ancilla (anc[0]) accumulates the result; anc[0] is measured.

**State evolution**:
1. Initialize all qubits to |0⟩; apply X(q[0]), X(q[4]), X(q[5]) → sets a=100 (q[0]=|1⟩, q[1]=|0⟩, q[2]=|0⟩) and b=011 (q[3]=|0⟩, q[4]=|1⟩, q[5]=|1⟩), anc[0]=|0⟩
2. Toffoli(q[0], q[3], anc[0]): requires q[0]=|1⟩ AND q[3]=|1⟩ → 1·0=0, no flip → anc[0] stays |0⟩
3. Toffoli(q[1], q[4], anc[0]): requires q[1]=|1⟩ AND q[4]=|1⟩ → 0·1=0, no flip → anc[0] stays |0⟩
4. Toffoli(q[2], q[5], anc[0]): requires q[2]=|1⟩ AND q[5]=|1⟩ → 0·1=0, no flip → anc[0] stays |0⟩

**Result**: Inner product mod 2 = (1·0)⊕(0·1)⊕(0·1) = 0, so anc[0]=|0⟩ with probability 1.0.
