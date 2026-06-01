# ISQ training COT RAG corpus: isq_defgate shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/199

- task_id: `isqTrain/199`
- task_type: `output_prediction`
- category: `isq_defgate`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1976`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;

defgate CRP = [
    1, 0, 0, 0;
    0, 1, 0, 0;
    0, 0, 1, 0;
    0, 0, 0, 0+1j
];

qbit q[2];

procedure main() {
    H(q[0]);
    CRP(q[0], q[1]);
    H(q[1]);
    CRP(q[0], q[1]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[0]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a concise, step-by-step analysis of an isQ quantum program, predicting the probability distribution of measurement outcomes.
2.  **Analyze the isQ Program:**
    *   Qubits: 2 (`q[0]`, `q[1]`)
    *   Initial state: $|00\rangle$
    *   Gate 1: `H(q[0])` -> State: $(|0\rangle + |1\rangle)/\sqrt{2} \otimes |0\rangle = (|00\rangle + |10\rangle)/\sqrt{2}$
    *   Gate 2: `CRP(q[0], q[1])` -> This is a controlled phase gate. Matrix is diag(1, 1, 1, i). So if state is $|11\rangle$, it gets a phase of $i$.
        *   State: $(|00\rangle + |10\rangle)/\sqrt{2}$. No $|11\rangle$ component. State is unchanged: $(|00\rangle + |10\rangle)/\sqrt{2}$.
    *   Gate 3: `H(q[1])` -> Applies H to $q[1]$.
        *   State: $\frac{1}{\sqrt{2}}(|0\rangle(|0\rangle+|1\rangle) + |1\rangle(|0\rangle+|1\rangle))/\sqrt{2} = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
    *   Gate 4: `CRP(q[0], q[1])` -> Controlled phase $i$ on $|11\rangle$.
        *   State: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + i|11\rangle)$.
    *   Gate 5: `CNOT(q[0], q[1])` -> Flips $q[1]$ when $q[0]$ is 1.
        *   State: $\frac{1}{2}(|00\rangle + |01\rangle + |11\rangle + i|10\rangle) = \frac{1}{2}(|00\rangle + |01\rangle + i|10\rangle + |11\rangle)$.
    *   Gate 6: `CNOT(q[1], q[0])` -> Flips $q[0]$ when $q[1]$ is 1.
        *   State: $\frac{1}{2}(|00\rangle + |11\rangle + i|11\rangle + |10\rangle) = \frac{1}{2}(|00\rangle + |10\rangle + (1+i)|11\rangle)$.
    *   Gate 7: `CNOT(q[0], q[1])` -> Flips $q[1]$ when $q[0]$ is 1.
        *   State: $\frac{1}{2}(|00\rangle + |11\rangle + (1+i)|10\rangle) = \frac{1}{2}(|00\rangle + (1+i)|10\rangle + |11\rangle)$.
    *   Wait, let's carefully re-evaluate Gate 5, 6, 7 (swap (three-CNOT decomposition)?).
    *   Let's trace again.
    *   Initial: $|00\rangle$
    *   $H_0$: $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$
    *   $CRP_{01}$: $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$
    *   $H_1$: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$
    *   $CRP_{01}$: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + i|11\rangle)$
    *   $CNOT_{01}$:
        *   $|00\rangle \to |00\rangle$
        *   $|01\rangle \to |01\rangle$
        *   $|10\rangle \to |11\rangle$
        *   $|11\rangle \to |10\rangle$
        *   State: $\frac{1}{2}(|00\rangle + |01\rangle + |11\rangle + i|10\rangle) = \frac{1}{2}(|00\rangle + i|10\rangle + |01\rangle + |11\rangle)$.
    *   $

### Reference answer

{'predicted_probs': {'0': 0.25, '1': 0.24999999999999994, '2': 0.25, '3': 0.25}, 'explanation': 'Parametric variant of isqHumanEval/69. Dimension: predict probabilities for reference circuit.'}

## isqTrain/529

- task_id: `isqTrain/529`
- task_type: `code_generation`
- category: `isq_defgate`
- difficulty: `expert`
- concept_tags: `ancilla_usage`, `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_for_loop`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `isq_syntax_print`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4335`

### Prompt

Write an isQ program that implements a variant of the amplitude_amplification pattern using q[3] -> q[4]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

This problem asks me to generate a concise reasoning explaining a variant of the amplitude amplification pattern (specifically a Grover search variant).

Let me analyze the circuit:
- 5 qubits total: q[0], q[1], q[2], q[3] and anc
- 4 qubits measured: q[0], q[1], q[2], q[3]
- Wait, looking more carefully - there are 4 qubits in q[4] array, plus anc
- But the oracle only uses q[0], q[1], q[2] and anc
- q[3] is never used in any operations
- So q[3] stays in whatever state it was initialized

Let me trace through:
1. Initialize q[0:3] with H gates → equal superposition over 8 states (for q[0:2])
   q[3] also gets H → |+>
   So state is (1/4) * Σ|x>|+> for x from 0 to 7

2. anc gets X then H → |->

3. Oracle U_omega marks state |001> (q[2]=0, q[1]=0, q[0]=1) - it's an oracle with [0,1,0,0,0,0,0,0], meaning it flips the phase of the |001> state

4. Grover iteration: oracle, then H(q), U0 (diffusion), H(q) - applied 3 times

Wait, let me re-read. The oracle is `oracle U_omega(3,1) = [0,1,0,0,0,0,0,0]`. The (3,1) parameter... I think this means it acts on 3 qubits and marks 1 state. The vector [0,1,0,0,0,0,0,0] marks |001>.

So this is a Grover search on 3 qubits looking for |001>, with q[3] as an extra qubit that's just in superposition but not involved in the search.

After 3 iterations of Grover on 3 qubits:
- For 3 qubits (N=8), optimal iterations ≈ π√(N/4)/4 ≈ π√2/4 ≈ 1.1, so 1 iteration would be optimal
- 3 iterations is more than optimal, so we get oscillation

The predicted output probabilities:
- |0001>: 0.47265625
- |1001>: 0.47265625
- All others: ~0.0039 (1/256)

So the marked state |001> has high probability when combined with q[3]=0 or q[3]=1.

Actually wait, looking at the oracle call: `U_omega(q[2], q[1], q[0], anc)` - it uses q[2], q[1], q[0], and anc. The anc is in |-> state for phase kickback.

The diffusion operator U0 acts on q[2], q[1], q[0] (3 qubits).

q[3] is completely uninvolved in the algorithm, just stays in |+> state.

So effectively:
- Grover search on 3 qubits for |001>
- 3 iterations
- q[3] is in |+> = (|0> + |1>)/√2

the predicted output show that states ending in |001> (with q[3]=0 or 1) have about 47.3% probability each, totaling ~94.5%.

Let me write the reasoning:

## Reasoning
1. Goal: Implement Grover's amplitude amplification on 3 qubits (q[0]-q[2]) searching for |001⟩, with an extra qubit q[3] in superposition.

2. Qubits: 5 total (q[0]-q[3] plus anc); 4 measured (q[0]-q[3]).

3. State evolution:
   - H(q) puts all 4 qubits in equal superposition: (1/4)Σ|x₀x₁x₂⟩ ⊗ |+⟩₃
   - X(anc); H(anc) prepares anc in |−⟩ for phase kickback
   - Oracle U_ω flips phase of |001⟩ component using anc qubit
   - Three Grover iterations (H → U₀ diffusion on 3 qubits → H) amplify |001⟩
   - q[3] remains in |+⟩ throughout, factorizing from the search space

4. Expected probabilities: For 3-qubit Grover with N=8 and ~3 iterations, the marked state |001⟩ is amplified

## isqTrain/190

- task_id: `isqTrain/190`
- task_type: `output_prediction`
- category: `isq_defgate`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `2738`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;

defgate ISWAP = [
    1, 0, 0, 0;
    0, 0, 0+1j, 0;
    0, 0+1j, 0, 0;
    0, 0, 0, 1
];

qbit q[2];

procedure main() {
    X(q[0]);
    ISWAP(q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations**: The circuit initializes a 2-qubit system to |00>, applies an X gate to q[0], applies a custom ISWAP gate to (q[0], q[1]), and measures both qubits.
2. **State Evolution**:
   - Initial state: |00>
   - `X(q[0])`: Flips the first qubit, changing the state to |10>.
   - `ISWAP(q[0], q[1])`: According to the provided matrix, this gate swaps the |10> and |01> basis states and applies a complex phase of `i`. Applying it to |10> yields the state `i|01>`.
3. **Final State**: The system is in the state `i|01>`.
4. **Probabilities**: Global phases do not affect measurement outcomes. The probability of measuring |01> is |i|^2 = 1.

Predicted probability distribution: {|01>: 1.0}

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/67. Dimension: predict probabilities for reference circuit.'}

## isqTrain/192

- task_id: `isqTrain/192`
- task_type: `code_generation`
- category: `isq_defgate`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `1795`

### Prompt

Implement the following in isQ: implements a variant of the gate_decomposition pattern using q[3] -> q[5]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

Let me analyze this task carefully.

The task asks me to write a variant of the gate_decomposition pattern using q[3] -> q[5]. This means I need to apply gates to qubits q[3] through q[5] (or similar), but using a 5-qubit register where additional qubits are left in the ground state.

Analyzing the circuit requirements:
- It uses a 5-qubit register q[5]
- It applies X to q[0] and q[1]
- Then applies controlled-swap (three-CNOT decomposition)(q[0], q[1], q[2]) - which is a Cswap (three-CNOT decomposition) gate
- Measures all 5 qubits
- predicted output: |10100> with probability 1.0

The controlled-swap operation (three-CNOT decomposition) (Cswap (three-CNOT decomposition)) swaps q[1] and q[2] when q[0] is |1>.

Let me trace the state evolution:
1. Initial: |00000>
2. After X(q[0]): |10000>
3. After X(q[1]): |11000>
4. After controlled-swap (three-CNOT decomposition)(q[0], q[1], q[2]): Since q[0]=|1>, swap q[1] and q[2]. q[1]=|1>, q[2]=|0>. After swap: q[1]=|0>, q[2]=|1>. So state becomes |10100>
5. Measurements: q[0]=1, q[1]=0, q[2]=1, q[3]=0, q[4]=0 → |10100>

This matches the predicted output.

Now, the task says "using q[3] -> q[5]" which might mean applying the operations to qubits q[3], q[4], q[5] instead of q[0], q[1], q[2]. But since we only have 5 qubits (q[0]-q[4]), q[5] doesn't exist. 

Wait, I think "q[3] -> q[5]" might mean the register size is from 3 to 5 qubits, or it might mean something else. Let me re-read...

"using q[3] -> q[5]" - this could mean:
1. Use a register of size that goes from 3 to 5 qubits (but that's ambiguous)
2. Use qubits indexed from 3 to 5 (but q[5] doesn't exist in a 5-qubit register)
3. The circuit is a variant that involves qubits q[3], q[4], q[5]

Actually, Analyzing the circuit requirements again, it uses q[0], q[1], q[2] for the controlled-swap operation (three-CNOT decomposition). The task says to use q[3] -> q[5], which could mean use q[3], q[4], q[5] instead. But that doesn't exist in a 5-qubit register.

Wait, maybe the task is asking me to generate the same pattern but with a different interpretation. Let me think about this differently.

Actually, I think "q[3] -> q[5]" might refer to the qubit register expansion. The base version might have had 3 qubits, and now we expand to 5 qubits. The circuit should this - it has 5 qubits but only uses the first 3 for operations, leaving q[3] and q[4] in the ground state.

So the task is: create a circuit that follows the gate_decomposition pattern but uses a 5-qubit register, where the pattern operates on some subset of qubits and the rest stay in |0>.

Analyzing the circuit requirements, it seems correct for this task. Let me verify:

1. Register: q[5] - 5 qubits (expanded from base 3)
2. Operations: X(q[0]), X(q[1]), controlled-swap (three-CNOT decomposition)(q[0], q[1], q[2]) - these are on q[0], q[1], q[2]
3. q[3] and q[4] are untouched (remain in ground state |0>)
4. Measurement: All 5 qubits

the predicted output |10100> means:
- q[0] = 1
- q[1] = 0
- q[2] = 1
- q[3] = 0
- q[4] = 0

This matches the controlled-swap operation (three-CNOT decomposition) where:
- After X(q[0]): q[0] = 1
- After X(q[1]): q[1] = 1
- controlled-swap (three-CNOT decomposition) swaps q[1] and q[2] when q[0]=1: q[1] becomes 0, q[2] becomes 1

So the final state is |10100> as expected.

## isqTrain/4501

- task_id: `isqTrain/4501`
- task_type: `output_prediction`
- category: `isq_defgate`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `2236`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;

defgate MyToffoli(3) = perm [0, 1, 2, 3, 4, 5, 7, 6];

qbit q[3];

procedure main() {
    X(q[0]);
    X(q[1]);
    MyToffoli(q[0], q[1], q[2]);
    H(q[2]); // superposition on last qubit
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations**: Initialize to |000>, apply X to q[0] and q[1], apply `MyToffoli`, and apply H to q[2].
2. **Evolution**:
   - Initial state: |000>
   - After X gates: |110>
   - `MyToffoli` is defined by permutation `[0, 1, 2, 3, 4, 5, 7, 6]`, which swaps |110> and |111>. Thus, it acts as a standard Toffoli gate, flipping the target q[2] to |1> because the controls q[0] and q[1] are |1>. The state becomes |111>.
   - Applying H to q[2] puts it into an equal superposition: |11> ⊗ ((|0> - |1>)/√2) = (|110> - |111>) / √2.
3. **Probabilities**: Measuring the system yields equal probabilities for the states |110> and |111>.

Predicted probability distribution: {|110>: 0.5, |111>: 0.5}

### Reference answer

{'predicted_probs': {'110': 0.5, '111': 0.5}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|110>) = 0.5000, P(|111>) = 0.5000.'}

## isqTrain/530

- task_id: `isqTrain/530`
- task_type: `code_generation`
- category: `isq_defgate`
- difficulty: `expert`
- concept_tags: `ancilla_usage`, `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_for_loop`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `isq_syntax_print`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3088`

### Prompt

Implement the following in isQ: implements a variant of the amplitude_amplification pattern using q[3] -> q[5]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
The circuit implements Grover's amplitude amplification on a 3-qubit subspace (q[0:3]) searching for marked state |001⟩, with q[3:5] serving as inactive extra qubits that remain in uniform superposition throughout.

**Qubits:** 5 main qubits (q[0:5]) plus 1 ancilla; all 5 main qubits are measured.

**State evolution:**
1. **Initialization:** H(q) creates uniform superposition on all 5 qubits: |+⟩⊗⁵|0⟩; X(anc),H(anc) prepares ancilla as |-⟩
2. **Oracle U_ω:** Marks |001⟩ on q[0:3] by applying controlled phase flip via ancilla: |001⟩|−⟩ → −|001⟩|−⟩
3. **Diffusion (H-U₀-H):** Inverts amplitudes about mean on q[0:3] subspace; U₀ flips all basis states except |000⟩
4.

## isqTrain/195

- task_id: `isqTrain/195`
- task_type: `output_prediction`
- category: `isq_defgate`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3672`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;

defgate Fredkin(3) = perm [0, 1, 2, 3, 4, 6, 5, 7];

qbit q[3];

procedure main() {
    X(q[0]);
    X(q[1]);
    Fredkin(q[0], q[1], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Input: An isQ program defining a 3-qubit circuit with an `X` gate, another `X` gate, and a custom `controlled-swap (three-CNOT decomposition)` gate (`perm [0, 1, 2, 3, 4, 6, 5, 7]`).
    *   Task: Explain step-by-step state evolution using Dirac notation and output the predicted probability distribution.
    *   Constraints: 3-8 lines for simple circuits. Start with "## Circuit Analysis". No code blocks. End with the predicted probability distribution.

2.  **Analyze the isQ Program:**
    *   `qbit q[3];`: Initial state is $|q_2 q_1 q_0\rangle = |000\rangle$.
    *   `X(q[0]);`: Flips $q_0$ to 1. State becomes $|001\rangle$.
    *   `X(q[1]);`: Flips $q_1$ to 1. State becomes $|011\rangle$.
    *   `defgate controlled-swap (three-CNOT decomposition)(3) = perm [0, 1, 2, 3, 4, 6, 5, 7];`:
        *   This permutation swaps the basis states corresponding to the indices.
        *   Index 5 (binary 101) is swapped with index 6 (binary 110).
        *   Let's check the qubit order in isQ. Usually, in isQ arrays, $q[0]$ is the least significant bit (LSB).
        *   Wait, the permutation indices are for the standard computational basis: 0 is $|000\rangle$, 1 is $|001\rangle$, 2 is $|010\rangle$, 3 is $|011\rangle$, 4 is $|100\rangle$, 5 is $|101\rangle$, 6 is $|110\rangle$, 7 is $|111\rangle$.
        *   State before controlled-swap (three-CNOT decomposition) is $|011\rangle$ (index 3).
        *   Since index 3 maps to 3 in the permutation $[0, 1, 2, 3, 4, 6, 5, 7]$, the state $|011\rangle$ remains unchanged!
        *   Let's double check. If the controlled-swap operation (three-CNOT decomposition) swaps q[1] and q[2] controlled by q[0]:
            *   Control is $q[0]$, targets are $q[1], q[2]$.
            *   Wait, standard controlled-swap (three-CNOT decomposition) is Cswap (three-CNOT decomposition). It swaps the other two qubits if the control (first qubit) is 1.
            *   Let's map indices. If `controlled-swap (three-CNOT decomposition)(a, b, c)` has control `a`:
            *   Indices where `a` (LSB) is 1 are 1, 3, 5, 7.
            *   For 1 (001), it becomes 1.
            *   For 3 (011), it becomes 3.
            *   For 5 (101 -> swap middle and MSB -> 110 -> 6), so 5 maps to 6.
            *   For 6 (110 -> swap middle and MSB -> 101 -> 5), so 6 maps to 5.
            *   This exactly matches `perm [0, 1, 2, 3, 4, 6, 5, 7]`.
            *   So `controlled-swap (three-CNOT decomposition)(q[0], q[1], q[2])` is a Cswap (three-CNOT decomposition) where `q[0]` is the control, and `q[1]`, `q[2]` are the targets.
    *   Current state before controlled-swap (three-CNOT decomposition): $q[0]=1, q[1]=1, q[2]=0$. This is $|011\rangle$ (binary $0q_2 q_1 q_0 = 011$).
    *   Since $q[0]=1$ (control is active), `controlled-swap (three-CNOT decomposition)` swaps $q[1]$ and $q[2]$.
    *   So $q[1]$ becomes 0, and $q[2]$ becomes 1.
    *   New state: $q[0]=1, q[1]=0, q[2]=1$. This is $|101\rangle$.
    *   Let's check the index of $|011\rangle$ is 3. If controlled-swap (three-CNOT decomposition) is $[0, 1, 2, 3, 4, 6, 5, 7]$, index 3 maps to 3.
    *   Wait

### Reference answer

{'predicted_probs': {'5': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/68. Dimension: predict probabilities for reference circuit.'}

## isqTrain/1902

- task_id: `isqTrain/1902`
- task_type: `output_prediction`
- category: `isq_defgate`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5265`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
defgate CRP = [
    1, 0, 0, 0;
    0, 1, 0, 0;
    0, 0, 1, 0;
    0, 0, 0, 0+1j
];
qbit q[2];
procedure main() {
    H(q[0]);
    CRP(q[0], q[1]);
    H(q[1]);
    CRP(q[0], q[1]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[0]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **H(q[0])**: Applies Hadamard to $q_0$. Initial state $|00\rangle \rightarrow \frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$.
2.  **CRP(q[0], q[1])**: CRP is controlled-phase (applies $e^{i\pi/2} = i$ if $q_0=1, q_1=1$). Since $q_1$ is $|0\rangle$, state remains $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$.
3.  **H(q[1])**: Applies Hadamard to $q_1$. State $\rightarrow \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
4.  **CRP(q[0], q[1])**: Applies $i$ phase to $|11\rangle$. State $\rightarrow \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + i|11\rangle)$.
5.  **CNOT(q[0], q[1])**: Flips $q_1$ if $q_0=1$. State $\rightarrow \frac{1}{2}(|00\rangle + |01\rangle + |11\rangle + i|10\rangle)$.
6.  **CNOT(q[1], q[0])**: Flips $q_0$ if $q_1=1$. State $\rightarrow \frac{1}{2}(|00\rangle + |11\rangle + |01\rangle + i|00\rangle) = \frac{1+i}{2}|00\rangle + \frac{1}{2}|01\rangle + \frac{1}{2}|11\rangle$.
7.  **CNOT(q[0], q[1])**: Flips $q_1$ if $q_0=1$. State $\rightarrow \frac{1+i}{2}|00\rangle + \frac{1}{2}|00\rangle + \frac{1}{2}|10\rangle = (\frac{1+i}{2} + \frac{1}{2})|00\rangle + \frac{1}{2}|10\rangle = \frac{2+i}{2}|00\rangle + \frac{1}{2}|10\rangle$. Wait, let's re-evaluate step 6.
    *   Step 5 state: $\frac{1}{2}(|00\rangle + |01\rangle + i|10\rangle + |11\rangle)$.
    *   Step 6 (CNOT $q_1 \to q_0$):
        *   $|00\rangle \to |00\rangle$
        *   $|01\rangle \to |11\rangle$
        *   $i|10\rangle \to i|10\rangle$
        *   $|11\rangle \to |01\rangle$
        *   Result: $\frac{1}{2}(|00\rangle + |11\rangle + i|10\rangle + |01\rangle)$.
    *   Step 7 (CNOT $q_0 \to q_1$):
        *   $|00\rangle \to |00\rangle$
        *   $|11\rangle \to |10\rangle$
        *   $i|10\rangle \to i|11\rangle$
        *   $|01\rangle \to |01\rangle$
        *   Result: $\frac{1}{2}(|00\rangle + |10\rangle + i|11\rangle + |01\rangle) = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + i|11\rangle)$.
8.  **Probabilities**:
    *   Amplitude of $|00\rangle$ is $1/2$. Prob = 1/4.
    *   Amplitude of $|01\rangle$ is $1/2$. Prob = 1/4.
    *   Amplitude of $|10\rangle$ is $1/2$. Prob = 1/4.
    *   Amplitude of $|11\rangle$ is $i/2$. Prob = 1/4.
    *   Total probability = 1. All four states are equiprobable.

Wait, step 5 to 7 evaluates to the exact same state!
Let's double check.
State 4: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + i|11\rangle)$.
The three CNOTs (swap operation (three-CNOT decomposition) sequence

### Reference answer

{'predicted_probs': {'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25}, 'explanation': 'Custom complex defgate in a 2-qubit circuit.'}

## isqTrain/4499

- task_id: `isqTrain/4499`
- task_type: `output_prediction`
- category: `isq_defgate`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `462`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;

defgate MyToffoli(3) = perm [0, 1, 2, 3, 4, 5, 7, 6];

qbit q[3];

procedure main() {
    X(q[0]);
    X(q[1]);
    MyToffoli(q[0], q[1], q[2]);
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a step-by-step analysis of an isQ quantum program to predict its measurement probability distribution. The response must follow specific formatting and length rules, using Dirac notation.

2.  **Analyze the isQ code:**
    *   `import std;`
    *   `defgate MyToffoli(3) = perm [0, 1, 2, 3, 4, 5, 7, 6];` -> This defines a Toffoli gate (permutation of states 6 and 7, which are |110> and |111>). Wait, standard Toffoli is permutation [0, 1, 2, 3, 4, 5, 7, 6] because it flips the target when both controls are 1. State |110> (6) goes to |111> (7) and vice versa. Yes, standard Toffoli.
    *   `qbit q[3];` -> 3 qubits, initialized to |000>.
    *   `X(q[0]);` -> Flips q[0] to |1>. State is |001>.
    *   `X(q[1]);` -> Flips q[1] to |1>. State is |011>.
    *   `MyToffoli(q[0], q[1], q[2]);` -> Toffoli gate. Controls: q[0], q[1]. Target: q[2]. Since both q[0] and q[1] are |1>, q[2] is flipped. State becomes |111>. Wait, wait.
        Let's check the qubit order carefully. `q[0]` is the first qubit, usually the right-most in binary representation (or left-most depending on convention, but typically q[0] is bit 0, so value 1. q[1] is bit 1, value 2. q[2] is bit 2, value 4).
        Initial: |000>
        X(q[0]) -> |001>
        X(q[1]) -> |011>
        MyToffoli(q[0], q[1], q[2]). Both controls (q[0], q[1]) are 1. Target (q[2]) is flipped from 0 to 1.
        State becomes |111>.
    *   `X(q[0]);` -> Flips q[0] from |1> to |0>. State becomes |110>.

    Wait! Let me re-read bit-string to state mapping in standard isQ/quantum conventions.
    If `q[0]` is measured first, is it the highest bit or lowest bit? The prompt says "earlier measured qubit = higher bit". So `q[0]` is the highest bit? No, the prompt says: "array indexed by measurement bitstring (earlier measured qubit = higher bit)."
    If M(q[0]), M(q[1]), M(q[2]).
    Bitstring = M(q[0]) M(q[1]) M(q[2]).
    So `q[0]` is the left-most bit, `q[2]` is the right-most bit.
    Let's represent the state as |q[0], q[1], q[2]>.
    Initial: |000>
    X(q[0]) -> |100>
    X(q[1]) -> |110>
    MyToffoli(q[0], q[1], q[2]). Since q[0]=1 and q[1]=1, q[2] is flipped. |110> -> |111>.
    X(q[0]) -> q[0] flipped. |111> -> |011>.
    So state is |011>.

3.  **Refine the steps:**
    *   Initial state: |000> (qubits q[0], q[1], q[2] in |0>)
    *   `X(q[0])`: State becomes |100>
    *   `X(q[1])`: State becomes |110>
    *   `MyToffoli(q[0], q[1], q[2])`: Flips target q[2] since controls q[0] and q[1] are |1>. State becomes |111>.
    *   `X(q[0])`: Flips q[0] from |1> to |0>. State becomes |011>.
    *   Measurement: Probabilities are 100% for |011>.

4.  **Format the Output:**
    *   Start with "## Circuit Analysis"
    *   List gates.
    *   State evolution.
    *   Final state.
    *   Predicted probabilities.
    *   Keep

### Reference answer

{'predicted_probs': {'011': 1.0}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|011>) = 1.0000.'}

## isqTrain/4502

- task_id: `isqTrain/4502`
- task_type: `output_prediction`
- category: `isq_defgate`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `751`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;

defgate MyToffoli(3) = perm [0, 1, 2, 3, 4, 5, 7, 6];

qbit q[3];

procedure main() {
    X(q[2]);  // target different qubit
    X(q[1]);
    MyToffoli(q[0], q[1], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Analyze an isQ program and predict the probability distribution.
    *   Program: Applies `X(q[2])`, `X(q[1])`, and a custom permutation gate `MyToffoli` acting on `q[0], q[1], q[2]`.
    *   Custom Gate: `defgate MyToffoli(3) = perm [0, 1, 2, 3, 4, 5, 7, 6];` - This swaps basis states |110> and |111>. Note that the bitstring order in isQ standard perm matrices usually maps `int` to the qubits in order. |6> is |110> (q[2]=0, q[1]=1, q[0]=1). |7> is |111>. Wait, standard permutation matrix `perm [0, 1, 2, 3, 4, 5, 7, 6]` maps column `i` to row `P[i]`. So it maps |6> to |7> and |7> to |6>. |6> is |110>. But what is the qubit order? The gate takes `(q[0], q[1], q[2])`. In isQ, the first qubit is the most significant bit (MSB). So `q[0]` is bit 2, `q[1]` is bit 1, `q[2]` is bit 0.
    *   Let's verify isQ qubit order for `perm`:
        *   State index `i` = `q[0]*4 + q[1]*2 + q[2]`.
        *   `|6>` is `q[0]=1, q[1]=1, q[2]=0`.
        *   `|7>` is `q[0]=1, q[1]=1, q[2]=1`.
        *   The `perm [0, 1, 2, 3, 4, 5, 7, 6]` swaps |110> and |111>. This means if `q[0]=1` and `q[1]=1`, it flips `q[2]`. This is exactly a standard Toffoli gate!

2.  **Step-by-step State Evolution:**
    *   Initial state: |000> (q[0]=0, q[1]=0, q[2]=0)
    *   `X(q[2])`: Flips q[2] to 1. State becomes |001> (index 1).
    *   `X(q[1])`: Flips q[1] to 1. State becomes |011> (index 3).
    *   `MyToffoli(q[0], q[1], q[2])`:
        *   Current state is |011>, which is index 3.
        *   The permutation gate `perm [0, 1, 2, 3, 4, 5, 7, 6]` applies the mapping: |0> -> |0>, |1> -> |1>, |2> -> |2>, |3> -> |3>, |4> -> |4>, |5> -> |5>, |6> -> |7>, |7> -> |6>.
        *   Since the current state is |3>, it maps to |3>.
        *   The state remains |011>.
    *   Wait, let me double-check the MSB/LSB convention in isQ.
        *   Standard: `q[0]` is the highest bit (value 4).
        *   Initial: |000>
        *   `X(q[2])`: flips bit 0 (value 1). State: |001>
        *   `X(q[1])`: flips bit 1 (value 2). State: |011>
        *   `MyToffoli`: maps |011> to |011>.
        *   Measurement: `M(q[0])` = 0, `M(q[1])` = 1, `M(q[2])` = 1. Bitstring = 011.

    Let's re-read the `MyToffoli` definition:
    `defgate MyToffoli(3) = perm [0, 1, 2, 3, 4, 5, 7, 6];`
    If it's `ctrl @[q[0], q[1]] X(q[2])`, it would be a Toffoli gate.
    For state |110> (q[0]=1, q[1]=1, q

### Reference answer

{'predicted_probs': {'011': 1.0}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|011>) = 1.0000.'}
