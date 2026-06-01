# ISQ training COT RAG corpus: isq_advanced shard 2

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1632

- task_id: `isqTrain/1632`
- task_type: `code_generation`
- category: `isq_advanced`
- difficulty: `basic`
- concept_tags: `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `5519`

### Prompt

Write an isQ program that SWAP as a reusable procedure, then call it from main(). Measure all qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement swap (three-CNOT decomposition) as a reusable procedure and demonstrate it swaps |10⟩ to |01⟩.
2. **Qubits**: 2 qubits q[0], q[1], both measured.
3. **State evolution**:
   - Start: |00⟩
   - X(q[0]) → |10⟩
   - CNOT(q[0], q[1]) — control q[0]=1 flips q[1]: |10⟩ → |11⟩
   - CNOT(q[1], q[0]) — control q[1]=1 flips q[0]: |11⟩ → |01⟩
   - CNOT(q[0], q[1]) — control q[0]=0, no flip: |01⟩ → |01⟩
4. **Result**: Final state is |01⟩, so measurement yields {|01⟩: 1.0}.

## isqTrain/1972

- task_id: `isqTrain/1972`
- task_type: `output_prediction`
- category: `isq_advanced`
- difficulty: `difficult`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3737`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;
qbit q[4];
defgate MY_H = [
    0.7071067811865476, 0.7071067811865476;
    0.7071067811865476, -0.7071067811865476
];
procedure main() {
    for i in 0:4 {
        MY_H(q[i]);
    }
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations**: The circuit initializes 4 qubits in the state |0000> and applies a custom unitary gate `MY_H` to each qubit. The matrix defined for `MY_H` is exactly equivalent to the standard Hadamard (H) gate.
2. **State Evolution**: Starting from |0000>, applying `MY_H` to each qubit independently puts every qubit into the equal superposition state |+> = (|0> + |1>) / sqrt(2). 
3. **Final State**: The system evolves into the tensor product of these superpositions, yielding a uniform superposition over all 16 possible basis states: |psi> = (1/4) * sum_{x=0}^{15} |x>.
4. **Probabilities**: Because each of the 16 basis states has an identical amplitude magnitude of 1/4, squaring the amplitude gives a uniform measurement probability of 1/16 (0.0625) for every possible outcome.

Predicted probability distribution: {'0000': 0.0625, '0001': 0.0625, '0010': 0.0625, '0011': 0.0625, '0100': 0.0625, '0101

### Reference answer

{'predicted_probs': {'0000': 0.0625, '0001': 0.0625, '0010': 0.0625, '0011': 0.0625, '0100': 0.0625, '0101': 0.0625, '0110': 0.0625, '0111': 0.0625, '1000': 0.0625, '1001': 0.0625, '1010': 0.0625, '1011': 0.0625, '1100': 0.0625, '1101': 0.0625, '1110': 0.0625, '1111': 0.0625}, 'explanation': 'defgate bounding over parameterized loops'}

## isqTrain/2556

- task_id: `isqTrain/2556`
- task_type: `code_equivalence`
- category: `isq_advanced`
- difficulty: `intermediate`
- concept_tags: `global_phase`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `3205`

### Prompt

Will these two quantum programs produce identical measurement outcomes?

```isq
import std;

procedure my_h(qbit a) {
    H(a);
}

procedure my_x(qbit a) {
    X(a);
}

procedure apply_gate(qbit a, unit gate_op(qbit)) {
    gate_op(a);
}

qbit q[1];

procedure main() {
    apply_gate(q[0], my_h);
    M(q[0]);
}

```

vs.

```isq
import std;

procedure my_h(qbit a) {
    H(a);
}

procedure my_x(qbit a) {
    X(a);
}

procedure apply_gate(qbit a, unit gate_op(qbit)) {
    gate_op(a);
}

qbit q[1];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    apply_gate(q[0], my_h);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis

1. **Program A**: Initializes q[0] to |0>, applies the H gate via `my_h` procedure, resulting in |+> = (|0> + |1>)/√2. Measures q[0].

2. **Program B**: Initializes q[0] to |0>, applies `GPhase(0.0)` (a trivial global phase of 0), then applies H via `my_h`, resulting in |+>. Measures q[0].

3. **Key difference**: Program B includes `GPhase(0.0)`, which multiplies the global state by e^(i*0) = 1. This is an identity operation and has no effect.

4. **Probability distributions**: Both programs produce 50% |0> and 50% |1>. The global phase does not affect measurement probabilities.

5. **Verdict**: Yes

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/4647

- task_id: `isqTrain/4647`
- task_type: `output_prediction`
- category: `isq_advanced`
- difficulty: `difficult`
- concept_tags: `interference`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `1558`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;

qbit q[2];
qbit anc[1];

procedure my_dj_oracle() {
    CNOT(q[0], anc[0]);
    nctrl X(q[1], anc[0]);
} deriving gate

procedure main() {
    
    X(q);  // replaced H with X
    X(anc[0]); 
    H(anc[0]);
    
    my_dj_oracle();
    
    
    
    
    
    H(q);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The task is to analyze an isQ program, trace the quantum state through the operations using Dirac notation, and predict the probability distribution of the measurement outcomes. The output must strictly follow the specified format, starting with "## Circuit Analysis" and ending with the predicted probabilities.

2.  **Analyze the isQ Program**:
    *   **Initialization**: `qbit q[2]` (states |00>) and `qbit anc[1]` (state |0>). Initial combined state: $|000\rangle$ (q[1]q[0]anc[0]).
    *   **Step 1**: `X(q);`
        *   Applies X to q[0] and q[1].
        *   State becomes $|110\rangle$.
    *   **Step 2**: `X(anc[0]);`
        *   Applies X to anc[0].
        *   State becomes $|111\rangle$.
    *   **Step 3**: `H(anc[0]);`
        *   Applies H to anc[0].
        *   State becomes $\frac{1}{\sqrt{2}}(|110\rangle - |111\rangle)$.
    *   **Step 4**: `my_dj_oracle();`
        *   Inside oracle: `CNOT(q[0], anc[0]);`
            *   Flips anc[0] if q[0] is 1.
            *   State: $\frac{1}{\sqrt{2}}(|111\rangle - |110\rangle) = -\frac{1}{\sqrt{2}}(|110\rangle - |111\rangle)$. Wait, $|110\rangle \rightarrow |111\rangle$ and $|111\rangle \rightarrow |110\rangle$.
            *   State is now $\frac{1}{\sqrt{2}}(|111\rangle - |110\rangle) = -\frac{1}{\sqrt{2}}(|110\rangle - |111\rangle)$.
        *   Inside oracle: `nctrl X(q[1], anc[0]);`
            *   Negative control on q[1]. Flips anc[0] if q[1] is 0. Since q[1] is currently 1, this does NOT apply.
            *   State remains $-\frac{1}{\sqrt{2}}(|110\rangle - |111\rangle)$.
        *   Actually, $-\frac{1}{\sqrt{2}}(|110\rangle - |111\rangle)$ can just be written as $-\frac{1}{\sqrt{2}}(|11\rangle \otimes (|0\rangle - |1\rangle))$.
    *   **Step 5**: `H(q);`
        *   Applies H to q[0] and q[1].
        *   Let's look at the state of q: $|11\rangle$.
        *   $H^{\otimes 2} |11\rangle = H|1\rangle \otimes H|1\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) = \frac{1}{2}(|00\rangle - |01\rangle - |10\rangle + |11\rangle)$.
        *   The anc qubit is in state $\frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$ (with a global phase of -1).
        *   Total state: $\frac{1}{2}(|00\rangle - |01\rangle - |10\rangle + |11\rangle) \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
    *   **Step 6**: `M(q[0]); M(q[1]);`
        *   Measures q[0] and q[1].
        *   Probabilities for q[1]q[0]:
            *   $|00\rangle$: $(\frac{1}{2})^2 = 0.25$
            *   $|01\rangle$: $(-\frac{1}{2})^2 = 0.25$
            *   $|10\rangle$: $(-\frac{1}{2})^2 = 0.25$
            *   $|11\rangle$: $(\frac{1}{2})^2 = 0.25$

3.  **Draft the response**:
    *   Must be 3-15 lines.
    *   Must start with `## Circuit Analysis`
    *   Must end with predicted probability distribution.

### Reference answer

{'predicted_probs': {'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|00>) = 0.2500, P(|01>) = 0.2500, P(|10>) = 0.2500, P(|11>) = 0.2500.'}

## isqTrain/1927

- task_id: `isqTrain/1927`
- task_type: `output_prediction`
- category: `isq_advanced`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `861`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
procedure my_h(qbit a) {
    H(a);
}
procedure my_x(qbit a) {
    X(a);
}
procedure apply_gate(qbit a, unit gate_op(qbit)) {
    gate_op(a);
}
qbit q[1];
procedure main() {
    apply_gate(q[0], my_h);
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initial State**: The qubit `q[0]` is initialized to the ground state |0>.
2. **Operations**: The program passes the custom procedure `my_h` to the higher-order function `apply_gate`, which applies an H (Hadamard) gate to `q[0]`.
3. **State Evolution**: 
   - Start: |0>
   - After H gate: $H|0\rangle = |+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$
4. **Measurement Probabilities**: Measuring the superposition state |+> yields an equal probability of collapsing to |0> or |1>.

Predicted probability distribution: {'0': 0.5, '1': 0.5}

### Reference answer

{'predicted_probs': {'0': 0.5, '1': 0.5}, 'explanation': 'Higher-order procedure.'}

## isqTrain/491

- task_id: `isqTrain/491`
- task_type: `code_generation`
- category: `isq_advanced`
- difficulty: `difficult`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_ctrl_nctrl`, `isq_syntax_for_loop`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2465`

### Prompt

Code this in isQ: implements the qft_subcircuit pattern but with a different initial state preparation (flip q[[0]] -> q[2]).

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for an isQ program that implements a QFT subcircuit with an initial state preparation where q[2] is flipped.

Let me analyze The implementation:
1. We have 3 qubits: q[0], q[1], q[2]
2. Initial state preparation: X(q[2]) prepares |100⟩ (q[2] is the highest bit, so flipping it gives |100⟩)
3. Then QFT is applied to all 3 qubits
4. Manual swap (three-CNOT decomposition) of q[0] and q[2] (reversing the order)
5. Measurement of all 3 qubits

The predicted output equal probabilities of 1/8 for all 8 basis states, which means the final state is a uniform superposition.

Let me trace through:
1. Initial state: |000⟩
2. After X(q[2]): |100⟩ (q[2] flipped)
3. After QFT on |100⟩:
   - QFT of |100⟩ in the standard basis would be...
   - The QFT of a computational basis state |k⟩ (for n qubits) produces a superposition
   - For |100⟩ = |4⟩ in the 3-qubit case (since q[2] is the most significant bit)
   - Actually, let me reconsider the bit ordering. In isQ, q[0] is typically the least significant bit.
   - So |100⟩ means q[0]=0, q[1]=0, q[2]=1, which is the state |4⟩ in decimal.
   
4. QFT of |4⟩ for 3 qubits:
   QFT|k⟩ = 1/√N Σ_{j=0}^{N-1} e^{2πijk/N} |j⟩
   
   For N=8 and k=4:
   QFT|4⟩ = 1/√8 Σ_{j=0}^{7} e^{2πi·4·j/8} |j⟩
          = 1/√8 Σ_{j=0}^{7} e^{πij} |j⟩
          = 1/√8 (|0⟩ - |1⟩ + |2⟩ - |3⟩ + |4⟩ - |5⟩ + |6⟩ - |7⟩)
   
   This is actually a product state! It's |−⟩⊗|−⟩⊗|−⟩ where |−⟩ = (|0⟩ - |1⟩)/√2
   
   Hmm, but then after swap (three-CNOT decomposition) of q[0] and q[2], the state would still be the same since it's a product state with all qubits in |−⟩.

5. The final state should be |−⟩⊗|−⟩⊗|−⟩ which gives equal probability 1/8 for all outcomes.

Wait, let me reconsider. The QFT implementation in the code doesn't include the bit-reversal at the end, which is why there's a manual swap (three-CNOT decomposition).

Actually, looking at the code more carefully:
- The QFT procedure applies H gates and controlled rotations
- Then there's a manual swap (three-CNOT decomposition) at the end: CNOT(q[0], q[2]); CNOT(q[2], q[0]); CNOT(q[0], q[2]);

This swap (three-CNOT decomposition) reverses the qubit order, which is needed because the QFT naturally produces the output in reversed bit order.

Let me trace more carefully:
1. |000⟩ → X(q[2]) → |100⟩ (q[0]=0, q[1]=0, q[2]=1)
2. QFT is applied. The standard QFT of |100⟩ (computational basis state 4 in big-endian) produces a uniform superposition after the bit-reversal.

Actually, The predicted output all probabilities are 1/8, which confirms the final state is a uniform superposition.

Let me verify:
- QFT|4⟩ for 3 qubits after bit reversal = 1/√8 (|0⟩ + |1⟩ + |2⟩ + |3⟩ + |4⟩ + |5⟩ + |6⟩ + |7⟩)

Yes, that gives equal probability 1/8 for each outcome.

Now for the reasoning:

## Reasoning
1. Goal: Apply QFT to the initial state |100⟩ and measure all qubits.
2. 3 qubits are needed (q[0], q[1], q[2]), all measured at the end.
3. State evolution:
   - Initial: |000⟩
   - X(q[2]): |100⟩ (computational state |4⟩)
   - QFT: The QFT of |4⟩ produces 1/√8 Σ_{j=0}^{

## isqTrain/498

- task_id: `isqTrain/498`
- task_type: `code_generation`
- category: `isq_advanced`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2614`

### Prompt

帮我写一个isQ程序：implements a variant of the oracle_boolean pattern using q[1] -> q[2]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

Looking at this problem, I need to analyze the given isQ program and explain its behavior.

Let me trace through the circuit:

1. **Qubits declared**: `q[2]` (q[0], q[1]) and `p[1]` (p[0]) - total 3 qubits

2. **Initial state**: All qubits start in |0⟩, so the state is |000⟩ (q[0]=0, q[1]=0, p[0]=0)

3. **execute_oracle(q[0], oracleA)**:
   - Apply H to q[0]: |0⟩ → |+⟩ = (|0⟩ + |1⟩)/√2
   - Apply oracleA (X gate) to q[0]: X|+⟩ = |+⟩ (since X|+⟩ = |+⟩)
   - Apply H to q[0]: |+⟩ → |0⟩
   
   So q[0] remains in |0⟩ state.

4. **execute_oracle(p[0], oracleB)**:
   - Apply H to p[0]: |0⟩ → |+⟩ = (|0⟩ + |1⟩)/√2
   - Apply oracleB (Z gate) to p[0]: Z|+⟩ = |-⟩ = (|0⟩ - |1⟩)/√2
   - Apply H to p[0]: |-⟩ → |1⟩
   
   So p[0] ends up in |1⟩ state.

5. **Final state**: |0⟩_q[0] ⊗ |0⟩_q[1] ⊗ |1⟩_p[0] = |001⟩

Wait, but the expected measurement says {|100⟩: 1.0}. Let me check the measurement order.

The measurements are: M(q[0]), M(q[1]), M(p[0])

In the --probs output, "earlier measured qubit = higher bit". So:
- q[0] is the highest bit (bit 2)
- q[1] is the middle bit (bit 1)
- p[0] is the lowest bit (bit 0)

So if q[0]=0, q[1]=0, p[0]=1, the bitstring would be:
- Bit 2 = q[0] = 0
- Bit 1 = q[1] = 0
- Bit 0 = p[0] = 1

That gives bitstring 001, not 100.

But The predicted output {|100⟩: 1.0}. Let me re-read...

Hmm, the problem says "The circuit should use an expanded qubit register compared to the base version" and "using q[1] -> q[2]". The circuit should q[2] and p[1], but maybe I need to write a different program?

Wait, the prompt says to write a program, and The implementation is given. The expected measurement is {|100⟩: 1.0} with 3 qubits measured.

Let me reconsider. If we have:
- q[0] measured = 1
- q[1] measured = 0  
- p[0] measured = 0

Then bitstring = 100 (q[0]=bit2, q[1]=bit1, p[0]=bit0)

But according to my analysis, The implementation gives q[0]=0, q[1]=0, p[0]=1 = 001.

Wait, let me re-read The implementation comment: "should be 01 (index 1)" - but there are 3 measurements, so maybe there's a different interpretation?

Actually, I think the prompt is asking me to write a NEW program (variant) that achieves the predicted output {|100⟩: 1.0}, not analyze The implementation.

Let me re-read: "Write an isQ program that implements a variant of the oracle_boolean pattern using q[1] -> q[2]. The circuit should use an expanded qubit register compared to the base version."

So I need to create a new program. But I'm only asked to generate the reasoning section...

Hmm, but the task says "Generate a reasoning section that explains" the circuit. I think I should analyze what circuit would give {|100⟩: 1.0}.

Let me think about what oracle_boolean pattern with q[1] -> q[2] means. It's probably a controlled operation where q[1] controls some operation on q[2].

For |100⟩: 
- q[0] = 1
- q[1] = 0
- q[2] = 0

Wait, but that's 3 qubits from a single register? Or maybe we have q[0], q[1],

## isqTrain/497

- task_id: `isqTrain/497`
- task_type: `output_prediction`
- category: `isq_advanced`
- difficulty: `difficult`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3085`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;

qbit q[4];

defgate MY_H = [
    0.7071067811865476, 0.7071067811865476;
    0.7071067811865476, -0.7071067811865476
];

procedure main() {
    for i in 0:4 {
        MY_H(q[i]);
    }
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Analyze an isQ program and predict measurement outcomes.
    *   Program: 4 qubits, applies `MY_H` gate to each, then measures all.
    *   `MY_H` gate matrix: `[[0.707..., 0.707...], [0.707..., -0.707...]]`. This is clearly the standard Hadamard gate $H = \frac{1}{\sqrt{2}} \begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix}$.
    *   Format: "## Circuit Analysis" followed by step-by-step reasoning using Dirac notation, ending with the probability distribution.
    *   Length: Concise (3-8 lines for simple).

2.  **Trace the Circuit:**
    *   Initial state: $|q[3]q[2]q[1]q[0]\rangle = |0000\rangle$ (Wait, isQ convention for bitstrings: "earlier measured qubit = higher bit". The measurements are M(q[0]), M(q[1]), M(q[2]), M(q[3]). Let's assume standard notation $|q_0 q_1 q_2 q_3\rangle$. The probability output is exactly uniform: $1/16$ for all states from $|0000\rangle$ to $|1111\rangle$).
    *   Gate 1: `MY_H` on $q_0$. State becomes $|0\rangle \otimes |0\rangle \otimes |0\rangle \otimes |+\rangle$.
    *   Gate 2: `MY_H` on $q_1$. State becomes $|0\rangle \otimes |0\rangle \otimes |+\rangle \otimes |+\rangle$.
    *   Gate 3: `MY_H` on $q_2$. State becomes $|0\rangle \otimes |+\rangle \otimes |+\rangle \otimes |+\rangle$.
    *   Gate 4: `MY_H` on $q_3$. State becomes $|+\rangle \otimes |+\rangle \otimes |+\rangle \otimes |+\rangle = |++++\rangle$.
    *   This state is an equal superposition of all 16 possible computational basis states.

3.  **Draft the Analysis:**
    *   Step 1: Initial state is $|0000\rangle$.
    *   Step 2: The custom gate `MY_H` is applied to each of the 4 qubits. `MY_H` is equivalent to the standard Hadamard (H) gate, mapping $|0\rangle$ to $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
    *   Step 3: The quantum state evolves to $|+\rangle^{\otimes 4} = \frac{1}{4} \sum_{x=0}^{15} |x\rangle$.
    *   Step 4: Measuring all qubits yields a uniform probability distribution over the 16 basis states, each with probability $(1/\sqrt{16})^2 = 0.0625$.

4.  **Format the Output:**
    *   Follow rules strictly: ONLY analysis, start with "## Circuit Analysis", no code blocks, end with predicted distribution.
    *   Match requested probabilities (floats can be simplified, e.g., 0.0625).

    *Drafting text:*
    ## Circuit Analysis
    1. The circuit initializes 4 qubits in the state $|0000\rangle$.
    2. It applies a custom gate `MY_H` to each qubit. This matrix is exactly the Hadamard gate, which transforms $|0\rangle \rightarrow |+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
    3. Applying this to all four qubits yields the state $|++++\rangle = \frac{1}{4}(|0000\rangle + |0001\rangle + \dots + |1111\rangle)$.
    4. This represents an equal superposition over all 16 possible computational basis states.
    5. Therefore, measurement collapses the state uniformly to any of the 16 outcomes.

    Predicted probability distribution: {|0000>: 0.0625, |0001>: 0.0625, |0010>: 0.0625, |0011>: 0.0625, |0100>: 0.0625, |0101>: 0.0625

### Reference answer

{'predicted_probs': {'0': 0.06250000000000003, '1': 0.06250000000000003, '2': 0.06250000000000003, '3': 0.0625, '4': 0.06250000000000003, '5': 0.0625, '6': 0.0625, '7': 0.06249999999999997, '8': 0.06250000000000003, '9': 0.0625, '10': 0.0625, '11': 0.06249999999999997, '12': 0.0625, '13': 0.06249999999999997, '14': 0.06249999999999997, '15': 0.06249999999999996}, 'explanation': 'Parametric variant of isqHumanEval/143. Dimension: predict probabilities for reference circuit.'}

## isqTrain/1636

- task_id: `isqTrain/1636`
- task_type: `code_generation`
- category: `isq_advanced`
- difficulty: `basic`
- concept_tags: `isq_syntax_inv`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5575`

### Prompt

Help me write isQ code that Apply H then inv H to |0>. H is self-inverse, result is |0>.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Demonstrate that applying H followed by its inverse returns a qubit to the initial state.
2. One qubit is required; it is measured at the end.
3. State evolution: initial state |0> → H|0> = |+> = (|0>+|1>)/√2 → inv H|+> = H|+> = |0> (since H is Hermitian and unitary, H²=I).
4. The final state is |0>, so measurement yields |0> with probability 1.0.

## isqTrain/507

- task_id: `isqTrain/507`
- task_type: `output_prediction`
- category: `isq_advanced`
- difficulty: `difficult`
- concept_tags: `isq_syntax_procedures`, `multi_controlled_logic`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `565`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;

qbit q[3];

procedure mcp() {
    ctrl<2> Z(q[0], q[1], q[2]);
}

procedure main() {
    // Because Z on |111> flips phase -> superposition
    H(q[0]); H(q[1]); H(q[2]);
    mcp();
    
    M(q[0]); M(q[1]); M(q[2]); // we just output probs, the phase flip doesn't change prob of |111> directly, but it forms an oracle.
    // Let's do diffuser to amplify
    // Actually, any output is fine as long as it compiles!
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: `output_prediction` for an isQ quantum program.
    *   Output: "## Circuit Analysis" section with step-by-step reasoning, state evolution (using Dirac notation), and predicted probability distribution.
    *   Constraints: Concise (3-15 lines), precise, no code blocks, start with "## Circuit Analysis", end with distribution.

2.  **Analyze the isQ Program:**
    *   Initialization: 3 qubits `q[0], q[1], q[2]` initialized to $|000\rangle$.
    *   Hadamard gates: `H(q[0]); H(q[1]); H(q[2]);` creates an equal superposition over all 8 basis states.
    *   Multi-controlled Z: `ctrl<2> Z(q[0], q[1], q[2]);` applies a Z gate to `q[2]` controlled by `q[0]` and `q[1]`. Wait, standard control syntax `ctrl<2> Z(q[0], q[1], q[2])` implies a Toffoli-like structure where the last qubit is the target. Z gate flips the phase of $|1\rangle$. So if q[0]=1, q[1]=1, Z is applied to q[2]. If q[2] is 0, Z does nothing ($Z|0\rangle = |0\rangle$). If q[2] is 1, Z flips phase ($Z|1\rangle = -|1\rangle$). Thus, this is equivalent to a double-controlled-Z (ctrl @[c1, c2] Z(target)) gate. It flips the phase of the $|111\rangle$ state.
    *   Measurements: `M(q[0]); M(q[1]); M(q[2]);` measures in the computational basis.
    *   *Crucial realization:* Phase flip (Z) doesn't affect the probability of measurement in the computational basis. $|\alpha|^2$ remains unchanged whether the state is $+\alpha|111\rangle$ or $-\alpha|111\rangle$.
    *   Therefore, all 8 states have an equal probability of $1/8 = 0.125$.

3.  **Draft the Reasoning (Step-by-Step):**
    *   *Initial state:* $|000\rangle$.
    *   *H gates:* $H^{\otimes 3}|000\rangle = \frac{1}{2\sqrt{2}} \sum_{x=0}^7 |x\rangle$.
    *   *MCP gate:* `ctrl<2> Z` acts as a double-controlled-Z (ctrl @[c1, c2] Z(target)) gate. It flips the phase of the $|111\rangle$ state. The state becomes $\frac{1}{2\sqrt{2}}(|000\rangle + |001\rangle + \dots - |111\rangle)$.
    *   *Measurement:* Since probability is the magnitude squared of the amplitudes, and $|(1/2\sqrt{2})^2| = |(-1/2\sqrt{2})^2| = 1/8$, all outcomes have equal probability.

4.  **Format the Output:**
    *   Start with `## Circuit Analysis`.
    *   Keep it concise.
    *   State the final distribution explicitly at the end.

5.  **Refine the Text (Self-Correction during drafting):**
    *   *Draft:*
        ## Circuit Analysis
        1. The circuit starts in $|000\rangle$ and applies H to all three qubits, creating the state $\frac{1}{2\sqrt{2}}\sum_{x=0}^7 |x\rangle$.
        2. The `mcp` procedure applies a doubly-controlled Z gate (double-controlled-Z (ctrl @[c1, c2] Z(target))). This flips the phase of the $|111\rangle$ state to $-|111\rangle$, yielding $\frac{1}{2\sqrt{2}}(|000\rangle + |001\rangle + \dots - |111\rangle)$.
        3. Before measurement, the absolute amplitude for every basis state is $\frac{1}{2\sqrt{2}}$.
        4. Because probabilities are the squared magnitudes of the amplitudes, and the phase flip on $|111\rangle$ does not change magnitude, all 8 basis states have equal probability.
        Predicted probability distribution: {|000>: 0.125, |001>: 0.125, |010>: 0.125, |011>: 0.125, |100>: 0.125, |101>: 0.125, |110>: 0.125, |111>: 0.125}
    *   *Check against constraints:* Concise? Yes

### Reference answer

{'predicted_probs': {'0': 0.12500000000000008, '1': 0.12500000000000008, '2': 0.12499999999999996, '3': 0.12499999999999996, '4': 0.12499999999999996, '5': 0.12499999999999997, '6': 0.125, '7': 0.12500000000000003}, 'explanation': 'Parametric variant of isqHumanEval/145. Dimension: predict probabilities for reference circuit.'}
