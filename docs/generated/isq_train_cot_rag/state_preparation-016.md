# ISQ training COT RAG corpus: state_preparation shard 16

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4665

- task_id: `isqTrain/4665`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `877`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
qbit q[3];

procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initialization:** The 3-qubit system starts in the fundamental basis state |000⟩.
2. **Superposition:** The H gate on q[0] creates an equal superposition, evolving the state to (1/√2)(|000⟩ + |100⟩).
3. **Entanglement:** A CNOT(q[0], q[1]) flips q[1] when q[0] is |1⟩, resulting in (1/√2)(|000⟩ + |110⟩). 
4. **GHZ State:** A subsequent CNOT(q[1], q[

### Reference answer

{'predicted_probs': {'011': 0.5, '100': 0.5}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|011>) = 0.5000, P(|100>) = 0.5000.'}

## isqTrain/3108

- task_id: `isqTrain/3108`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `3701`

### Prompt

Write an isQ program that an isQ program: apply H to 2 qubit(s) to create uniform superposition, then measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Create a uniform superposition over 2 qubits using Hadamard gates and measure the resulting state.
2. **Qubits:** 2 qubits are allocated, and both are measured.
3. **State evolution:**
   - Initial state: |00>
   - Apply H to both qubits: H⊗H |00> = (1/√2)(|0> + |1>) ⊗ (1/√2)(|0> + |1>) = (1/2)(|00> + |01> + |10> + |11>)
4. **Probabilities:** Measuring this equal superposition yields all 4 possible outcomes (|00>, |01>, |10>, |11>) with identical probability (1/2)² = 0.25.

## isqTrain/3197

- task_id: `isqTrain/3197`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1884`

### Prompt

Code this in isQ: an isQ program: apply Ry(7*pi/12) to a qubit and measure.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Task:** Generate a step-by-step reasoning for the given isQ quantum program.
    *   **Input:** A prompt asking to write an isQ program applying `Ry(7*pi/12)` to a qubit and measure. circuit implementation and expected probabilities provided.
    *   **Role:** Quantum computing expert.
    *   **Output Format:** "## Reasoning" section ONLY, no isQ code, concise (3-8 lines for simple circuits), using Dirac notation.

2.  **Analyze the Quantum Circuit:**
    *   **Goal:** Apply an $R_y(7\pi/12)$ rotation to a single qubit initially in state $|0\rangle$ and measure it.
    *   **Qubits:** 1 qubit ($q_0$).
    *   **Initial State:** $|\psi_0\rangle = |0\rangle$.
    *   **Gate Operation:** $R_y(\theta) = \cos(\theta/2)|0\rangle\langle0| - \sin(\theta/2)|1\rangle\langle0| + \sin(\theta/2)|0\rangle\langle1| + \cos(\theta/2)|1\rangle\langle1|$.
        Wait, standard definition: $R_y(\theta) = e^{-i\theta Y/2}$.
        Applied to $|0\rangle$: $\cos(\theta/2)|0\rangle + \sin(\theta/2)|1\rangle$.
        Here $\theta = 7\pi/12$.
        $\theta/2 = 7\pi/24$.
        $|\psi_1\rangle = \cos(7\pi/24)|0\rangle + \sin(7\pi/24)|1\rangle$.
    *   **Probabilities:**
        $P(0) = \cos^2(7\pi/24) \approx \cos^2(91.875^\circ)$? No, $7\pi/24 \approx 0.2916\pi \approx 52.5^\circ$.
        Wait, $7\pi/12 = 105^\circ$.
        $\theta/2 = 52.5^\circ$.
        $\cos(52.5^\circ) \approx 0.6087$. $P(0) = \cos^2(52.5^\circ) \approx 0.3706$.
        $\sin(52.5^\circ) \approx 0.7933$. $P(1) = \sin^2(52.5^\circ) \approx 0.6294$.
        Matches expected.

3.  **Draft the Reasoning (Iterative refinement for conciseness):**
    *   *Line 1 (Goal):* The circuit applies a Y-rotation of $7\pi/12$ to a single qubit and measures it.
    *   *Line 2 (Qubits):* It requires one qubit, initially in state $|0\rangle$.
    *   *Line 3 (Evolution):* Applying $R_y(7\pi/12)$ rotates the state around the Y-axis by $7\pi/12$ radians, evolving the state to $\cos(7\pi/24)|0\rangle + \sin(7\pi/24)|1\rangle$.
    *   *Line 4 (Probabilities):* Measuring this state yields probability $\cos^2(7\pi/24) \approx 0.3706$ for outcome $|0\rangle$ and $\sin^2(7\pi/24) \approx 0.6294$ for outcome $|1\rangle$.

4.  **Check Constraints:**
    *   Starts with "## Reasoning"? Yes.
    *   No isQ code? Yes.
    *   no code blocks? Yes.
    *   Dirac notation used? Yes ($|0\rangle$, $|1\rangle$).
    *   Concise (3-8 lines)? Yes (4 lines).
    *   Precise? Yes.

5.  **Final Polish:**
    ## Reasoning
    The goal is to rotate a single qubit around the Y-axis by an angle of $7\pi/12$ and measure its state.
    We need one qubit, $q[0]$, which starts in the initial state $|0\rangle$.
    The $R_y(7\pi/12)$ gate transforms the state to $\cos(7\pi/24)|0\rangle + \sin(7\pi/24)|1\rangle$.
    The final measurement probabilities are $P(|0\r

## isqTrain/581

- task_id: `isqTrain/581`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `350`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[4];

procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
    M(q);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Gates applied**: H(q[0]), CNOT(q[0], q[1]), CNOT(q[1], q[2]), CNOT(q[2], q[3]).
2. **State evolution**:
   - Initial state is |0000>.
   - H(q[0]) puts q[0] in superposition: (|0000> + |1000>)/√2.
   - CNOT(q[0], q[1]) entangles q[1] with q[0]: (|0000> + |1100>)/√2.
   - CNOT(q[1], q[2]) entangles q[2] with q[1]: (|0000> + |1110>)/√2.
   - CNOT(q[2], q[3]) entangles q[3] with q[2]: (|0000> + |1111>)/√2.
3. **Final state**: The 4-qubit GHZ state (|0000> + |1111>)/√2.
4. **Measurement probabilities**: {|0000>: 0.5, |1111>: 0.5}

### Reference answer

{'predicted_probs': {'0': 0.5, '15': 0.5}, 'explanation': 'Parametric variant of isqHumanEval/194. Dimension: predict probabilities for reference circuit.'}

## isqTrain/3746

- task_id: `isqTrain/3746`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `2118`

### Prompt

用isQ实现Prepare a 2-qubit product state by applying Ry(0.5) to q[0] and Ry(0.5) to q[1]. Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare a 2-qubit product state by applying Ry(0.5) to each qubit, then measure both.

2. **Qubits**: 2 qubits q[0] and q[1], both measured.

3. **State evolution**:
   - Initial: |00⟩
   - Ry(0.5) on q[0]: [cos(0.25)|0⟩ + sin(0.25)|1⟩] ⊗ |0⟩ ≈ 0.969|0⟩ + 0.247|1⟩ on q[0]
   - Ry(0.5) on q[1]: [cos(0.25)|0⟩ + sin(0.25)|1⟩] ⊗ [cos(0.25)|0⟩ + sin(0.25)|1⟩]
   - Final product state: cos²(0.25)|00⟩ + cos(0.25)sin(0.25)|01⟩ + sin(0.25)cos(0.25)|10⟩ + sin²(0.25)|11⟩

4. **Probabilities**: P(|00⟩)=cos⁴(0.25)≈0.881, P(|01⟩)=P(|10⟩)=cos²(0.25)sin²(0.25)≈0.057, P(|11⟩)=sin⁴(0.25)≈0.004, matching expected values.

## isqTrain/4774

- task_id: `isqTrain/4774`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_classical_vars`
- source: `isq_train_cot`
- dataset_index: `497`

### Prompt

I need an isQ program to implements: classical var variant 4. Declare a global qbit array q of 1 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Implement a circuit using a classical variable to conditionally apply an X gate to a single qubit.
2. **Qubits:** 1 global qubit `q[0]`, which is measured.
3. **State evolution:** 
   - Initial state is |0>.
   - Classical variable `val` is 5, satisfying `val > 4`.
   - The X gate is applied to `q[0]`, changing the state from |0> to X|0> = |1>.
4. **Expected probabilities:** The final state is exactly |1>, so measurement yields `1` with probability 1.0, giving `{|1>: 1.0}`.

## isqTrain/3185

- task_id: `isqTrain/3185`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2141`

### Prompt

Write isQ code for the following quantum task: an isQ program: apply Ry(5*pi/7) to one qubit, then CNOT to a second qubit, creating partial entanglement.

### Chain-of-thought reasoning

## Reasoning
Goal: Create a partially entangled two-qubit state using Ry rotation followed by CNOT.

Two qubits are used (q[0], q[1]), both measured at the end.

State evolution:
1. Initial: |00⟩
2. Ry(5π/7) on q[0]: cos(5π/14)|0⟩ + sin(5π/14)|1⟩ ≈ 0.4339|0⟩ + 0.9010|1⟩, yielding state 0.4339|00⟩ + 0.9010|10⟩
3. CNOT(q[0], q[1]) flips q[1] when q[0]=|1⟩: |00⟩→|00⟩, |10⟩→|11⟩, giving 0.4339|00⟩ + 0.9010|11⟩

Probabilities: P(|00⟩) = cos²(5π/14) ≈ 0.1883, P(|11⟩) = sin²(5π/14) ≈ 0.8117, confirming partial (non-maximal) entanglement.

## isqTrain/1447

- task_id: `isqTrain/1447`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3945`

### Prompt

Implement a quantum circuit in isQ: Prepare the computational basis state |0101> on 4 qubits by applying X gates to the appropriate qubits, then measure all.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Goal: Generate a concise, step-by-step reasoning section for a quantum program in isQ that prepares state |0101> on 4 qubits and measures all.
    *   Format Requirements: Start with "## Reasoning", use Dirac notation, concise (3-8 lines), NO isQ code blocks, NO code generation.
    *   Problem Specifics:
        *   Qubits: 4 (`q[0]`, `q[1]`, `q[2]`, `q[3]`)
        *   Initial state: `|0000>`
        *   Operations: `X(q[1])`, `X(q[3])`
        *   Measurement: All 4 qubits.
        *   Target state: `|0101>`
        *   Probabilities: 100% for `|0101>` (binary string 0101).

2.  **Drafting the Reasoning:**
    *   *Goal:* Prepare the computational basis state $|0101\rangle$ on a 4-qubit register and measure it.
    *   *Qubits:* Requires 4 qubits (q[0] to q[3]), all of which are measured.
    *   *Evolution:*
        *   Start in $|0000\rangle$.
        *   Apply X gate to q[1] and q[3] (which flips $|0\rangle$ to $|1\rangle$).
        *   State transitions from $|0000\rangle$ to $|0101\rangle$.
    *   *Probabilities:* The final state is deterministically $|0101\rangle$, so measuring all qubits yields the bitstring 0101 with 100% probability.

3.  **Refining and Formatting:**
    *   Keep it within the 3-8 line limit.
    *   Ensure Dirac notation is used correctly ($|0000\rangle$, $|0101\rangle$).
    *   Check rule: Output ONLY the reasoning section, starting with "## Reasoning".

    *Draft:*
    ## Reasoning
    The goal is to prepare the specific computational basis state $|0101\rangle$ on 4 qubits and measure it.
    We initialize 4 qubits ($q_0, q_1, q_2, q_3$) in the ground state $|0000\rangle$.
    Applying the X gate to $q_1$ flips it to $|1\rangle$, evolving the state to $|0010\rangle$ (considering index order $q_3 q_2 q_1 q_0$). Wait, isQ uses little-endian or big-endian? Typically, q[0] is the least significant bit (rightmost). So flipping q[1] makes it $|0010\rangle$? Wait. Let's trace carefully.
    Initial: `|0 q[3]> |0 q[2]> |0 q[1]> |0 q[0]>` -> `|0000>`.
    X(q[1]) -> `|0> |0> |1> |0>` -> `|0010>`.
    X(q[3]) -> `|1> |0> |1> |0>` -> `|1010>`.
    Wait! If the prompt says "Prepare the computational basis state |0101> on 4 qubits by applying X gates to the appropriate qubits", q[0] is rightmost. So $|0101>$ means q[0]=1, q[1]=0, q[2]=1, q[3]=0.
    Let's check The implementation:
    
    If q[1] and q[3] are flipped, the bitstring is:
    q[3]=1, q[2]=0, q[1]=1, q[0]=0.
    Represented as `q[3]q[2]q[1]q[0]`, this is `1010`.
    Why does the prompt say `Prepare the computational basis state |0101>` and then flip q[1] and q[3]?
    Ah. If q[0] is the *leftmost* bit (big-endian, standard in some notations), then `|0101>` means q[0]=0, q[1]=1, q[2]=0, q[3]=1.
    Flipping q[1] and q[3] makes it `|0101>`.
    Let's write the reasoning matching The implementation without getting bogged down in standard vs isQ endianness, just describe the flip. "Applying X gates to q[

## isqTrain/4785

- task_id: `isqTrain/4785`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `superposition`, `isq_syntax_while_loop`, `isq_syntax_if_else`
- source: `isq_train_cot`
- dataset_index: `1010`

### Prompt

帮我写一个isQ程序：implements: while-loop with classical vars variant 1. Declare a global qbit array q of 2 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement a while-loop with classical variable counting, applying H gates in a repeated pattern to demonstrate classical-quantum interplay.
Qubits: 2-qubit array q[2]; both qubits measured at the end.

State evolution:
- Initial: |00>
- Loop iteration 1 (steps=0): H(q[0])|00> = |+0>, then H(q[0])|+0> = |00> (H is self-inverse: H² = I)
- Loop iteration 2 (steps=1): Same pattern, H twice returns |00> again
- After loop: State is |00>
- Final H(q[0]): |00> → |+0> = (|00> + |10>)/√2

Expected probabilities: The final state (|00>+|10>)/√2 yields |00> with probability 0.5 and |10> with probability 0.5, since q[1] remains |0> throughout and q[0] is in equal superposition.

## isqTrain/4662

- task_id: `isqTrain/4662`
- task_type: `code_equivalence`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2163`

### Prompt

比较这两个量子电路，它们的输出概率分布一样吗？

```isq
import std;
qbit q[3];

procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

```isq
import std;
qbit q[3];

procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A**: Applies a Hadamard gate to q[0], then entangles q[1] and q[2] directly with q[0] using CNOT(q[0], q[1]) and CNOT(q[0], q[2]).
2. **Program B**: Applies a Hadamard gate to q[0], then uses a chain of CNOTs: CNOT(q[0], q[1]) followed by CNOT(q[1], q[2]).
3. **Key difference**: Program A uses q[0] as the control for both CNOTs, whereas Program B uses q[1] as the control for the second CNOT.
4. **Measurement probabilities**: Both programs generate the exact same 3-qubit GHZ state, $1/\sqrt{2}(|000\rangle + |111\rangle)$. Thus, they yield identical probability distributions: 50% for '000' and 50% for '111'.
5. **Verdict**: Yes

### Reference answer

{'equivalent': True, 'explanation': "Two ways to create 3-qubit GHZ state Both programs produce the same probability distribution: {'000': 0.5, '111': 0.5}.", 'probs_a': {'000': 0.5, '111': 0.5}, 'probs_b': {'000': 0.5, '111': 0.5}}
