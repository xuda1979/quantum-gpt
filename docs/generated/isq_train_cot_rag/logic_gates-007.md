# ISQ training COT RAG corpus: logic_gates shard 7

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/393

- task_id: `isqTrain/393`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `isq_syntax_multi_register`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `1426`

### Prompt

实现以下量子计算任务（使用isQ）：implements a variant of the arithmetic_circuit pattern using Cin[1] -> Cin[2]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

Top of Form

## Reasoning

1.  **Goal**: Implement a 1-bit full adder (A, B, Cin -> Sum, Cout) where A=1, B=1, Cin=1, using an expanded carry register `Cin[2]`, and measure the result.
2.  **Qubits**: 7 total (`A[1], B[1], Cin[2], Sum[1], Cout[1], anc[1]`). 6 qubits are measured (`A[0], B[0], Cin[0], Cin[1], Sum[0], Cout[0]`).
3.  **Initialization**: `X` gates set A[0], B[0], Cin[0] to |1>.
    *   State: |1>_A |1>_B |1,0>_{Cin} |0>_Sum |0>_Cout |0>_anc -> |1101000> (order A, B, Cin[0], Cin[1], Sum, Cout, anc)
4.  **Sum logic**: `CNOT(A, Sum)`, `CNOT(B, Sum)`, `CNOT(Cin[0], Sum)` compute XOR in Sum.
    *   A=1 flips Sum (0->1). B=1 flips Sum (1->0). Cin[0]=1 flips Sum (0->1).
    *   Sum is 1.
    *   State: |1101100> (Sum is now 1).
5.  **Carry logic Part 1**: `Toffoli(A, B, Cout)` computes AND in Cout.
    *   A=1, B=1 flips Cout (0->1).
    *   State: |1101101> (Cout is now 1).
6.  **Carry logic Part 2**: `CNOT(A, anc)`, `CNOT(B, anc)` compute A XOR B in anc.
    *   A=1 flips anc (0->1). B=1 flips anc (1->0).
    *   anc is 0.
    *   State: |1101100> (anc is now 0).
7.  **Carry logic Part 3**: `Toffoli(Cin[0], anc, Cout)` adds Cin*(A^B) to Cout.
    *   Since anc=0, this Toffoli does nothing.
    *   State: |1101100> (Cout remains 1).
8.  **Final State**: The measured bits are A(1), B(1), Cin[0](1), Cin[1](0), Sum(1), Cout(1).
    *   The bitstring is 111011 (A is highest bit, Cout is lowest bit as per standard `M` ordering in description, though need to be careful about bit reversal).
    *   Standard output mapping: earliest measured = highest bit index.
    *   A=1 (bit 5), B=1 (bit 4), Cin[0]=1 (bit 3), Cin[1]=0 (bit 2), Sum=1 (bit 1), Cout=1 (bit 0).
    *   Decimal value: 1*32 + 1*16 + 1*8 + 0*4 + 1*2 + 1*1 = 59.
    *   However, the prompt says "expected measurement probabilities: {|111011>: 1.0}". This implies the string itself is `111011`.
9.  **Conclusion**: Since A, B, Cin were all 1 (1+1+1=3), Sum=1 (3 mod 2) and Cout=1 (3 // 2). The expanded `Cin[1]` qubit remains 0. The final state corresponds to |111011> with certainty.

1.  **Goal**: Implement a 1-bit full adder (A=1, B=1, Cin=1) producing Sum and Cout using an expanded Cin register, and measure the results.
2.  **Qubits**: 7 total (`A[1], B[1], Cin[2], Sum[1], Cout[1], anc[1]`). Measured: A, B, Cin[0], Cin[1], Sum, Cout (6 qubits).
3.  **Initialization**: X gates set A, B, Cin to |1>. State: |1101000> (ignoring ordering).
4.  **Sum Logic**: CNOTs compute Sum = A ^ B ^ Cin[0] = 1 ^ 1 ^ 1 = 1. Sum qubit becomes |1>.
5.  **Carry Logic**: Toffoli(A, B, Cout) sets Cout = A & B = 1 & 1 = 1.

## isqTrain/1515

- task_id: `isqTrain/1515`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `4621`

### Prompt

I need an isQ program to Compute the inner product mod 2 of a=011 and b=010 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Generate a concise, precise step-by-step reasoning for a given isQ quantum program (computing inner product mod 2).
    *   Format: Start with "## Reasoning", 3-8 lines (simple) or up to 15 (complex), use Dirac notation.
    *   Input program computes $a \cdot b \pmod 2$ for $a=011$ and $b=010$.
    *   Initial state: $|000000\rangle|0\rangle$ (6 qubits + 1 ancilla).
    *   $a=011 \implies q[0]=0, q[1]=1, q[2]=1$.
    *   $b=010 \implies q[3]=0, q[4]=1, q[5]=0$.
    *   The inner product mod 2 is $(0\cdot0) \oplus (1\cdot1) \oplus (1\cdot0) = 0 \oplus 1 \oplus 0 = 1$.
    *   Toffoli gates check $(q[0], q[3])$, $(q[1], q[4])$, $(q[2], q[5])$. If both controls are 1, they flip `anc[0]`.
    *   Only $(q[1], q[4])$ will be $1$. So `anc[0]` is flipped once, resulting in $|1\rangle$.

2.  **Draft the Reasoning:**
    *   Goal: Compute inner product mod 2 of $a=011$ and $b=010$ using Toffoli gates, storing the result in an ancilla qubit.
    *   Qubits: 7 qubits total ($q[0..5]$ for $a$ and $b$, $anc[0]$ for the result). Only $anc[0]$ is measured.
    *   State evolution:
        *   Initial: $|0000000\rangle$
        *   After X gates ($q[1], q[2], q[4]$): $|0101100\rangle$ (representing $a=011, b=010, anc=0$).
        *   1st Toffoli on $(q[0], q[3])$: controls are $0, 0$; no flip $\rightarrow |0101100\rangle$.
        *   2nd Toffoli on $(q[1], q[4])$: controls are $1, 1$; flips $anc[0] \rightarrow |0101101\rangle$.
        *   3rd Toffoli on $(q[2], q[5])$: controls are $1, 0$; no flip $\rightarrow |0101101\rangle$.
    *   Measurement: $anc[0]$ is in state $|1\rangle$, yielding 100% probability for $|1\rangle$.

3.  **Refine to meet constraints:**
    *   Constraint checklist: 3-8 lines, start with "## Reasoning", only reasoning, Dirac notation, concise.
    *   Line 1: Goal.
    *   Line 2: Qubits.
    *   Line 3-6: Evolution.
    *   Line 7: Probabilities.

    *Drafting final text:*
    ## Reasoning
    1. **Goal**: Compute the bitwise inner product mod 2 of $a=011$ and $b=010$, storing the result in an ancilla.
    2. **Qubits**: Uses 6 data qubits ($q[0..2]$ for $a$, $q[3..5]$ for $b$) and 1 ancilla ($anc[0]$). Only $anc[0]$ is measured.
    3. **Initialization**: X gates on $q[1], q[2]$ (representing $a$) and $q[4]$ (representing $b$) prepare the state $|010\rangle_a |010\rangle_b |0\rangle_{anc}$.
    4. **State Evolution**: 
       - Toffoli on $(q[0], q[3]) \rightarrow anc[0]$: Controls are $|0\rangle, |0\rangle$, so no flip occurs.
       - Toffoli on $(q[1], q[4]) \rightarrow anc[0]$: Controls are $|1\rangle, |1\rangle$, flipping $anc[0]$ to $|1\rangle$.
       - Toffoli on $(q[2], q[5]) \rightarrow anc[0]$: Controls are $|1\r

## isqTrain/1536

- task_id: `isqTrain/1536`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `207`

### Prompt

Write an isQ program that Compute the inner product mod 2 of a=110 and b=010 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

The user wants to compute the inner product mod 2 of a=110 and b=010 using Toffoli gates.
a = 110 corresponds to bits a0=1, a1=1, a2=0 (or vice versa, but let's check the reference).
Wait, The circuit should q[0], q[1], q[4] initialized to |1>.
The reference has 6 qubits: q[0..2] for a, q[3..5] for b.
Let's trace reference:
X(q[0]) -> a0 = 1
X(q[1]) -> a1 = 1
X(q[4]) -> b1 = 1
Wait, a=110 could mean a2=1, a1=1, a0=0. If so, X(q[0]), X(q[1]) means a0=1, a1=1. The string is "110", so 6 in decimal, which is 110. Bitstring 110. So a2=1, a1=1, a0=0.
Wait, if a=110, X(q[0]) makes a0=1. So q[0] is LSB?
Let's see: X(q[0]), X(q[1]) means a has bits 1 and 1 set. So a = 011 = 3. Or a = 110 depending on encoding. Let's assume q[0..2] is a.
q[3..5] is b. X(q[4]) means b has bit 4 set. So b1=1.
If a = 110 -> a2=1, a1=1, a0=0. Then a.b mod 2 = 1*0 + 1*1 + 0*0 = 1.
If a = 110 -> q[0]=0, q[1]=1, q[2]=1. Then X(q[0]) would be wrong.
Let's look at the prompt's reference:

Wait, if q[0]=1, q[1]=1, q[2]=0, this represents a=011=3.
q[3]=0, q[4]=1, q[5]=0, this represents b=010=2.
Inner product mod 2: 0*0 + 1*1 + 1*0 = 1. Result is |1>.
If the string "110" means q[0]=1, q[1]=1, q[2]=0, and "010" means q[3]=0, q[4]=1, q[5]=0, then the prompt matches.
Inner product mod 2 is the sum of a_i * b_i mod 2.
The Toffoli gates:
ctrl ctrl X(q[0], q[3], anc[0]);
ctrl ctrl X(q[1], q[4], anc[0]);
ctrl ctrl X(q[2], q[5], anc[0]);
ancilla starts at |0>.
Toffoli flips ancilla if q[i] and q[i+3] are both 1.
Since q[1]=1 and q[4]=1, the second Toffoli flips the ancilla to |1>.
First Toffoli doesn't flip (q[3]=0). Third doesn't flip (q[2]=0).
So ancilla ends up as |1>.

Goal: Compute inner product mod 2 of a and b, where a=110 (meaning q[0]=1, q[1]=1) and b=010 (meaning q[4]=1), storing the result in an ancilla.
1. Goal: Compute the mod-2 inner product of bit strings a and b using Toffoli gates.
2. Qubits: 6 data qubits (q[0]-q[5]) for a and b, 1 ancilla (anc[0]) to store the result. Only anc[0] is measured.
3. Evolution:
- Initial state is |000000>|0> for q[0..5] and anc[0].
- X gates on q[0], q[1], and q[4] set the state to |011010>|0>.
- First Toffoli on q[0], q[3] does nothing as q[3]=0.
- Second Toffoli on q[1], q[4] flips anc[0] to |1> because both are 1.
- Third Toffoli on q[2], q[5] does nothing as q[2]=0.
- Final state is |011010>|1>.
4. Measurement: The ancilla is in the state |1>,

## isqTrain/632

- task_id: `isqTrain/632`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `4489`

### Prompt

Implement the following in isQ: implements the gate_decomposition pattern. Include explicit identity operations in the circuit (H-H pair before M(q[3])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement a gate decomposition with explicit H-H identity pair to demonstrate gate cancellation awareness.

2. **Qubits**: 4 qubits (q[0..3]), only q[3] is measured.

3. **State evolution**:
   - Initial: |0000⟩
   - After X(q[0]), X(q[1]), X(q[2]): |1110⟩
   - After ctrl^3 X (triple-controlled X flips q[3] when q[0]=q[1]=q[2]=1): |1111⟩
   - After first H(q[3]): H|1⟩ = |−⟩ = (|0⟩−|1⟩)/√2 → state is |111−⟩
   - After second H(q[3]): H|−⟩ = |1⟩ → state returns to |1111⟩ (H-H = I, gate cancellation)
   - M(q[3]) measures the last qubit

4. **Expected probabilities**: Since q[3] is in state |1⟩, measurement yields {|1⟩: 1.0}. The H-H pair cancels to identity, leaving q[3] deterministic.

## isqTrain/1521

- task_id: `isqTrain/1521`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `2876`

### Prompt

Implement a quantum circuit in isQ: Compute the inner product mod 2 of a=100 and b=001 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning
Goal: Compute the bitwise inner product mod 2 of a=100 and b=001, storing the result in an ancilla qubit.

Seven qubits are used: q[0..2] for a, q[3..5] for b, and anc[0] for the result. Only anc[0] is measured.

State evolution:
1. Initial state: |000000⟩|0⟩
2. X(q[0]) sets a[0]=1: |100000⟩|0⟩
3. X(q[5]) sets b[2]=1: |100001⟩|0⟩
4. Toffoli(q[0], q[3], anc): q[3]=0, so no flip → |100001⟩|0⟩
5. Toffoli(q[1], q[4], anc): q[1]=0, so no flip → |100001⟩|0⟩
6. Toffoli(q[2], q[5], anc): q[2]=0, so no flip → |100001⟩|0⟩

The inner product is 1·0 + 0·0 + 0·1 = 0 mod 2 = 0. No Toffoli fires since no position has both a[i]=1 and b[i]=1, so anc[0] remains |0⟩, yielding measurement probability {|0⟩: 1.0}.

## isqTrain/397

- task_id: `isqTrain/397`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `isq_syntax_multi_register`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `518`

### Prompt

Create an isQ quantum circuit that implements a variant of the arithmetic_circuit pattern using Cout[1] -> Cout[3]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning

**Goal**: Implement a 1-bit full adder (A + B + Cin) with test case 1+1+1, using an expanded Cout[3] register.

**Qubits**: 8 total (A[1], B[1], Cin[1], Sum[1], Cout[3], anc[1]); 7 measured (all except anc).

**State evolution**:
1. Initialize |00000000⟩ (A,B,Cin,Sum,Cout[0-2],anc)
2. X on A[0],B[0],Cin[0] → |11100000⟩
3. CNOT(A→Sum), CNOT(B→Sum), CNOT(Cin→Sum): Sum = A⊕B⊕Cin = 1⊕1⊕1 = 1 → |11110000⟩
4. Toffoli(A,B→Cout[0]): Cout[0] = A&B = 1 → |11111000⟩
5. CNOT(A→anc), CNOT(B→anc): anc = A⊕B = 0 → |11111000⟩
6. Toffoli(Cin,anc→Cout[0]): Cout[0] ^= Cin&(A⊕B) = 1⊕0 = 1 → |11111000⟩

**Result**: Final measured state |1111100⟩ (A=1,B=1,Cin=1,Sum=1,Cout=1,Cout[1]=0,Cout[2]=0) with probability 1, confirming 1+1+1 = Sum(1), Cout(1).

## isqTrain/1531

- task_id: `isqTrain/1531`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `5272`

### Prompt

Code this in isQ: Compute the inner product mod 2 of a=101 and b=100 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning
Goal: Compute inner product mod 2 of a=101 and b=100 using Toffoli gates, storing result in ancilla.

Qubits: 7 total (q[0..5] for inputs, anc[0] for result). Only anc[0] is measured.

State evolution:
1. Initialize all to |0⟩: |0000000⟩
2. X(q[0]): |1000000⟩
3. X(q[2]): |1010000⟩
4. X(q[3]): |1011000⟩

## isqTrain/1524

- task_id: `isqTrain/1524`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `776`

### Prompt

Write an isQ program that Compute the inner product mod 2 of a=100 and b=100 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Compute the bitwise inner product mod 2 between binary strings a=100 and b=100, storing the result in an ancilla qubit.
2. **Qubits**: 6 data qubits `q[0..5]` to hold the two 3-bit strings, and 1 `anc[0]` to hold the output (only `anc[0]` is measured).
3. **State Evolution**:
   - Initialize all qubits to $|0\rangle^{\otimes 7}$.
   - Apply X to `q[0]` and `q[3]` to encode $a=100$ and $b=100$, yielding state $|1001000\rangle$.
   - Apply `ctrl ctrl X(q[0], q[3], anc[0])`: since `q[0]` and `q[3]` are both 1, the ancilla flips to 1 $\rightarrow |1001001\rangle$.
   - Apply Toffolis for the remaining pairs `(q[1], q[4])` and `(q[2], q[5])`: both pairs are in $|0\rangle$, so no flip occurs.
4. **Probabilities**: The final state is $|1001001\rangle$. Measuring `anc[0]` deterministically yields 1, giving output probabilities $\{|1\rangle: 1.0\}$.

## isqTrain/1947

- task_id: `isqTrain/1947`
- task_type: `output_prediction`
- category: `logic_gates`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `isq_syntax_procedures`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3828`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[3];
procedure XOR_gate() {
    CNOT(q[0], q[2]);
    CNOT(q[1], q[2]);
}
procedure main() {
    X(q[0]);
    X(q[1]);
    XOR_gate();
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes 3 qubits in the state |000>.
2. X gates are applied to q[0] and q[1], flipping them to |1> and transitioning the state to |110>.
3. The XOR_gate applies CNOT(q[0], q[2]). Since q[0] is |1>, q[2] flips to |1>, making the state |111>.
4. Next, CNOT(q[1], q[2]) is applied. Since q[1] is |1>, q[2] flips back to |0>, resulting in the final state |110>.
5. The measurement outcomes will deterministically yield the exact computational basis state.

Predicted probability distribution: {'110': 1.0}

### Reference answer

{'predicted_probs': {'110': 1.0}, 'explanation': 'Reversible XOR'}

## isqTrain/1514

- task_id: `isqTrain/1514`
- task_type: `code_generation`
- category: `logic_gates`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `2295`

### Prompt

Create an isQ quantum circuit that Compute the inner product mod 2 of a=011 and b=001 using Toffoli gates. Store result in ancilla.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Compute the bitwise inner product mod 2 of binary strings $a=011$ and $b=001$.
2. **Qubits:** 6 data qubits ($q[0\dots2]$ for $a$, $q[3\dots5]$ for $b$) and 1 ancilla qubit to store the result. Only `anc[0]` is measured.
3. **State Evolution:**
   - Initialize to $|0000000\rangle$.
   - Apply X gates to $q[1], q[2]$ (setting $a=011$) and $q[5]$ (setting $b=001$), yielding $|0110010\rangle$.
   - Toffoli($q[0], q[3], anc[0]$): $a_0 \cdot b_0 = 0 \cdot 0 = 0$. No flip, state remains $|0110010\rangle$.
   - Toffoli($q[1], q[4], anc[0]$): $a_1 \cdot b_1 = 1 \cdot 0 = 0$. No flip, state remains $|0110010\rangle$.
   - Toffoli($q[2], q[5], anc[0]$): $a_2 \cdot b_2 = 1 \cdot 1 = 1$. Flips `anc[0]`, resulting in $|0110011\rangle$.
4. **Probabilities:** The final state of `anc[0]` is exactly $|1\rangle$. Thus, measuring `anc[0]` yields 1 with a probability of 1.0, matching the predicted output $\{|1\rangle: 1.0\}$.
