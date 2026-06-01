# ISQ training COT RAG corpus: isq_control_flow shard 5

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1707

- task_id: `isqTrain/1707`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `617`

### Prompt

请用isQ语言编写一个量子电路：Prepare a 4-qubit GHZ state using a for loop for the CNOT gates.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a maximally entangled 4-qubit GHZ (Greenberger–Horne–Zeilinger) state.
2. **Qubits**: Requires 4 qubits, all of which are measured at the end.
3. **State Evolution**:
   - Initial state is |0000>.
   - H on q[0] yields (|0000> + |1000>) / sqrt(2).
   - A `for` loop applies CNOT(q[0], q[i]) for i from 1 to 3.
   - Each CNOT flips the target qubit if q[0] is |1>, resulting in the final state (|0000> + |1111>) / sqrt(2).
4. **Probabilities**: The final state is an equal superposition of |0000> and |1111>, so measurements yield a 0.5 probability for each bitstring.

## isqTrain/1690

- task_id: `isqTrain/1690`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_for_loop`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `831`

### Prompt

Write an isQ program that Use a for loop to apply a CNOT chain on 4 qubits starting from |1000>. Each qubit controls the next.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply a CNOT chain to propagate the |1⟩ state from q[0] to all qubits.
2. **Qubits**: 4 qubits (q[0]–q[3]), all measured.
3. **State evolution**:
   - Start: |0000⟩ → X(q[0]) → |1000⟩
   - CNOT(q[0], q[1]): control=|1⟩ flips target → |1100⟩
   - CNOT(q[1], q[2]): control=|1⟩ flips target → |1110⟩
   - CNOT(q[2], q[3]): control=|1⟩ flips target → |1111⟩
4. **Result**: Final state is |1111⟩ with probability 1.0.

## isqTrain/2546

- task_id: `isqTrain/2546`
- task_type: `code_equivalence`
- category: `isq_control_flow`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `global_phase`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `1141`

### Prompt

Compare these two isQ programs. Do they give the same probability distribution?

First program:
```isq
import std;

qbit q[4];

procedure main() {
    H(q[0]);
    for i in 0:3 {
        CNOT(q[i], q[i+1]);
    }
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

Second program:
```isq
import std;

qbit q[4];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    H(q[0]);
    for i in 0:3 {
        CNOT(q[i], q[i+1]);
    }
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** prepares a 4-qubit GHZ state by applying an H gate to `q[0]`, creating $|+\rangle|000\rangle$, followed by a cascade of CNOT gates to entangle the qubits, resulting in $\frac{1}{\sqrt{2}}(|0000\rangle + |1111\rangle)$.
2. **Program B** applies the exact same sequence of gates (H gate followed by three CNOTs) to prepare the identical GHZ state.
3. The only difference is that Program B includes a `GPhase(0.0)` operation before the H gate.
4. `GPhase(0.0)` introduces a global phase of $e^{i \cdot 0} = 1$, which acts as an identity operation. Since global phases do not affect the physical state, the measurement probabilities remain exactly the same (50% for 0000, 50% for 1111).
5. Verdict: Yes, they are equivalent.

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/1693

- task_id: `isqTrain/1693`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_for_loop`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `2415`

### Prompt

Help me write isQ code that Use a for loop for CNOT fan-out: q[0] controls all others on 5 qubits from |10000>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a CNOT fan-out where q[0] controls q[1]–q[4], starting from |10000⟩.
2. **Qubits**: 5 qubits (q[0]–q[4]), all measured at the end.
3. **State evolution**:
   - Initial: |00000⟩
   - After X(q[0]): |10000⟩
   - After CNOT(q[0], q[1]): |11000⟩ (control q[0]=|1⟩ flips target)
   - After CNOT(q[0], q[2]): |11100⟩
   - After CNOT(q[0], q[3]): |11110⟩
   - After CNOT(q[0], q[4]): |11111⟩
4. **Expected probabilities**: Final state is |11111⟩ with probability 1.0, since each CNOT propagates the |1⟩ from q[0] to all targets.

## isqTrain/246

- task_id: `isqTrain/246`
- task_type: `output_prediction`
- category: `isq_control_flow`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `4021`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;

qbit q[4];

procedure main() {
    H(q[0]);
    for i in 0:3 {
        CNOT(q[i], q[i+1]);
    }
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initialization:** The circuit starts with 4 qubits in the state $|0000\rangle$.
2. **Hadamard Gate:** Applying `H(q[0])` puts the first qubit into a superposition, changing the state to $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes |000\rangle = \frac{1}{\sqrt{2}}(|0000\rangle + |1000\rangle)$.
3. **CNOT Cascade:** The `for` loop applies three consecutive CNOT gates: `CNOT(q[0], q[1])`, `CNOT(q[1], q[2])`, and `CNOT(q[2], q[3])`. 
4. **State Evolution:** 
   - First CNOT flips `q[1]` when `q[0]` is $|1\rangle$, resulting in $\frac{1}{\sqrt{2}}(|0000\rangle + |1100\rangle)$.
   - Second CNOT flips `q[2]` when `q[1]` is $|1\rangle$, resulting in $\frac{1}{\sqrt{2}}(|0000\rangle + |1110\rangle)$.
   - Third CNOT flips `q[3]` when `q[2]` is $|1\rangle$, resulting in the final 4-qubit GHZ state: $|\psi\rangle = \frac{1}{\sqrt{2}}(|0000\rangle + |1111\rangle)$.
5. **Measurement:** Measuring all qubits collapses the superposition, yielding either all 0s or all 1s with equal probability.

Predicted probability distribution: {|0000>: 0.5, |1111>: 0.5}

### Reference answer

{'predicted_probs': {'0': 0.5, '15': 0.5}, 'explanation': 'Parametric variant of isqHumanEval/84. Dimension: predict probabilities for reference circuit.'}

## isqTrain/241

- task_id: `isqTrain/241`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `2379`

### Prompt

Write isQ code for the following quantum task: implements the ghz_state_preparation pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare a 4-qubit GHZ entangled state and include a canceling X-X pair to demonstrate gate cancellation awareness.
2. **Qubits**: 4 qubits (q[0] to q[3]), all measured at the end.
3. **State evolution**:
   - Initialize |0000⟩
   - H(q[0]) → (|0⟩ + |1⟩)/√2 ⊗ |000⟩ = (|0000⟩ + |1000⟩)/√2
   - CNOT(q[0], q[1]) → (|0000⟩ + |1100⟩)/√2
   - CNOT(q[1], q[2]) → (|0000⟩ + |1110⟩)/√2
   - CNOT(q[2], q[3]) → (|0000⟩ + |1111⟩)/√2
   - X(q[0]) → (|1000⟩ + |0111⟩)/√2
   - X(q[0]) → (|0000⟩ + |1111⟩)/√2 (X-X pair cancels, identity operation)
4. **Expected probabilities**: The final GHZ state (|0000⟩ + |1111⟩)/√2 yields P(|0000⟩) = 0.5 and P(|1111⟩) = 0.5, with all other basis states having zero probability.

## isqTrain/240

- task_id: `isqTrain/240`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `4802`

### Prompt

Implement a quantum circuit in isQ: implements a variant of the ghz_state_preparation pattern using q[4] -> q[6]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

The user wants to prepare a variant of the GHZ state preparation circuit using q[4] -> q[6].

Let's analyze The implementation:
It prepares a GHZ state on q[0], q[1], q[2], q[3], q[4] using H(q[0]) and CNOTs (q[i], q[i+1]).
Wait, the reference has `q[4] -> q[6]` logic? No, the prompt says "implements a variant of the ghz_state_preparation pattern using q[4] -> q[6]."
Wait, The circuit should `q[4] -> q[6]`? No, `qbit q[6];`. It applies H to q[0], and CNOT to q[i], q[i+1] for i from 0 to 3.
So it applies CNOT(q[0], q[1]), CNOT(q[1], q[2]), CNOT(q[2], q[3]), CNOT(q[3], q[4]).
Wait, the predicted output for The implementation are `{|000000>: 0.5, |111100>: 0.5}`.
If it applies CNOT to q[4], then q[0..4] are entangled in GHZ state: `(|00000> + |11111>) / sqrt(2)`. But wait, q[5] is never touched.
So the state is `(|000000> + |111110>) / sqrt(2)`. But the prompt says `{|000000>: 0.5, |111100>: 0.5}`.
Ah! The prompt says "using q[4] -> q[6]". Wait, does it mean apply gates from q[4] to q[6]? Or apply GHZ to q[0] through q[3] (so CNOT stops at q[3])? Wait, if it stops at q[3], it would be `(|000000> + |111100>) / sqrt(2)`, which matches `{|000000>: 0.5, |111100>: 0.5}`!
Wait, "using q[4] -> q[6]"? Wait, maybe "q[4] -> q[6]" means the circuit should prepare a GHZ state, and the register size is 6? But wait, if the register size is 6, and the probabilities are `{|000000>: 0.5, |111100>: 0.5}`, the GHZ state is only on the first 4 qubits (q[0] to q[3]).
Let me re-read carefully: "Write an isQ program that implements a variant of the ghz_state_preparation pattern using q[4] -> q[6]."
Wait! If it is "using q[4] -> q[6]", maybe it means GHZ on q[4], q[5]? But the probabilities are for 6 qubits, ending in 00.
If GHZ is on q[0..3], the state is `(|000000> + |111100>) / sqrt(2)`.
If the prompt says "using q[4] -> q[6]", maybe it meant `q[0] -> q[3]`? Or maybe it means the index in some list?
Let's look at The implementation:

Wait, if `i` goes `0:3`, `i` takes 0, 1, 2.
So `CNOT(q[0], q[1])`, `CNOT(q[1], q[2])`, `CNOT(q[2], q[3])`.
This means q[4] and q[5] are untouched.
This results in `(|0000> + |1111>) \otimes |00>` for the 6 qubits.
Which gives `(|000000> + |111100>) / sqrt(2)`.
Ah, `for i in 0:3` in Python means `0, 1, 2`. But wait, in isQ, what does `0:3` mean? Does it mean 0, 1, 2?
Yes, standard range syntax `a:b` means `[a, a+1, ..., b-1]`.
Wait, so `0:3` means `i = 0, 1, 2`. Thus `CNOT(q[0], q[1])`, `CNOT(q[1], q[2])`, `CNOT(q[2], q[3])`.
This perfectly matches the target probabilities `{|000000>: 0.5, |111100

## isqTrain/1739

- task_id: `isqTrain/1739`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `basic`
- concept_tags: `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `2058`

### Prompt

Write an isQ program that Use a for loop from 0 to 3 (exclusive) applying X each iteration. 3 iterations means X^3.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply the X gate three times to a single qubit and measure the result.
2. **Qubits**: 1 qubit (`q[0]`) is used and measured.
3. **State evolution**:
   - Initial: `|0⟩`
   - After 1st X: `X|0⟩ = |1⟩`
   - After 2nd X: `X|1⟩ = |0⟩` (since X² = I)
   - After 3rd X: `X|0⟩ = |1⟩`
4. **Result**: The final state is `|1⟩`, yielding measurement probability `{`|1⟩: 1.0`}` because X³ = X, and X|0⟩ = |1⟩.

## isqTrain/1920

- task_id: `isqTrain/1920`
- task_type: `output_prediction`
- category: `isq_control_flow`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `5078`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[4];
procedure main() {
    for i in 0:4 {
        Ry(pi/4.0, q[i]);
    }
    for i in 0:3 {
        CNOT(q[i], q[i+1]);
    }
    for i in 0:4 {
        Rz(pi/3.0, q[i]);
    }
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a concise, step-by-step analysis of an isQ quantum program, predicting the probability distribution of the measurement outcomes. I need to follow the specified format ("## Circuit Analysis"), use Dirac notation, and limit the length (3-15 lines).

2.  **Analyze the Circuit:**
    *   4 qubits initialized to $|0\rangle$.
    *   Apply $R_y(\pi/4)$ to each qubit: transforms $|0\rangle$ to $\cos(\pi/8)|0\rangle + \sin(\pi/8)|1\rangle$.
        *   $\cos(\pi/8) \approx 0.9239$
        *   $\sin(\pi/8) \approx 0.3827$
        *   State after $R_y$: $(\cos(\pi/8)|0\rangle + \sin(\pi/8)|1\rangle)^{\otimes 4}$
    *   Apply CNOT chain: $CNOT(q[0], q[1])$, $CNOT(q[1], q[2])$, $CNOT(q[2], q[3])$.
        *   This creates an entangled state.
        *   Since the input state is a product state of the form $a|0\rangle + b|1\rangle$ for each qubit, the CNOT chain creates the GHZ-like state: $a^4|0000\rangle + a^3b|0001\rangle + a^2b^2|0011\rangle + ab^3|0111\rangle + b^4|1111\rangle + b^3a|1110\rangle + b^2a^2|1100\rangle + ba^3|1000\rangle$... wait, no.
        *   Let's trace carefully:
            Initial: $(a|0\rangle + b|1\rangle)(a|0\rangle + b|1\rangle)(a|0\rangle + b|1\rangle)(a|0\rangle + b|1\rangle)$
            Apply CNOTs: CNOT maps $\alpha|00\rangle + \beta|01\rangle + \gamma|10\rangle + \delta|11\rangle$ to $\alpha|00\rangle + \beta|01\rangle + \gamma|11\rangle + \delta|10\rangle$.
            Actually, the state $(a|0\rangle + b|1\rangle)|0\rangle$ becomes $a|00\rangle + b|11\rangle$.
            So the cascade of CNOTs turns $\sum c_{x_0 x_1 x_2 x_3} |x_0 x_1 x_2 x_3\rangle$ into:
            The state is $a|0\rangle(a|0\rangle+b|1\rangle)(a|0\rangle+b|1\rangle)(a|0\rangle+b|1\rangle) + b|1\rangle(a|1\rangle+b|0\rangle)(a|1\rangle+b|0\rangle)(a|1\rangle+b|0\rangle)$?
            No, CNOT(0,1) on $(a|0\rangle+b|1\rangle)(a|0\rangle+b|1\rangle)$ yields $a^2|00\rangle + ab|01\rangle + ba|11\rangle + b^2|10\rangle$.
            Let's use $a=\cos(\pi/8)$, $b=\sin(\pi/8)$.
            CNOT chain effect:
            Let $|\psi\rangle = \sum_{x \in \{0,1\}^4} a^{4-w(x)} b^{w(x)} |x\rangle$.
            After CNOTs, the state is $\sum_{x} a^{4-w(x)} b^{w(x)} |x_0, x_0 \oplus x_1, x_1 \oplus x_2, x_2 \oplus x_3\rangle$.
            Let's list the non-zero amplitudes after CNOTs.
            If $x = (x_0, x_1, x_2, x_3)$:
            The target $y$ is $y_0=x_0, y_1=x_0 \oplus x_1, y_2=x_1 \oplus x_2, y_3=x_2 \oplus x_3$.
            Wait, the CNOTs are:
            $q_1 \leftarrow q_0 \oplus q_1$
            $q_2 \leftarrow q_1 \oplus q

### Reference answer

{'predicted_probs': {'0000': 0.5308, '0001': 0.0911, '0010': 0.0156, '0011': 0.0911, '0100': 0.0156, '0101': 0.0027, '0110': 0.0156, '0111': 0.0911, '1000': 0.0156, '1001': 0.0027, '1011': 0.0027, '1100': 0.0156, '1101': 0.0027, '1110': 0.0156, '1111': 0.0911}, 'explanation': 'nested/multiple for loops.'}

## isqTrain/250

- task_id: `isqTrain/250`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_while_loop`
- source: `isq_train_cot`
- dataset_index: `2487`

### Prompt

实现以下量子计算任务（使用isQ）：implements the arithmetic_circuit pattern with modified rotation parameters (pi6_to_pi4). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

## Reasoning
1. The circuit applies three successive Rx(π/4) rotations to q[0] in a while loop while q[1] remains idle, then measures both qubits.
2. Two qubits are used (q[2]); both q[0] and q[1] are measured.
3. Initial state |00⟩ → after 3×Rx(π/4) on q[0] (total Rx(3π/4)): cos(3π/8)|00⟩ − i·sin(3π/8)|10⟩
4. P(|00⟩) = cos²(3π/8) ≈ 0.1464, P(|10⟩) = sin²(3π/8) ≈ 0.8536, matching predicted output.
