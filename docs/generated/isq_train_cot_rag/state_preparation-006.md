# ISQ training COT RAG corpus: state_preparation shard 6

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1950

- task_id: `isqTrain/1950`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `entanglement`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `579`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
qbit q[4];
procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initial State**: The system starts in the ground state $|0000\rangle$.
2. **H(q[0])**: Applies a Hadamard gate to q0, putting it into a superposition $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$. The state is now $\frac{1}{\sqrt{2}}(|0000\rangle + |1000\rangle)$.
3. **CNOT(q[0], q[1])**: Flips q1 conditioned on q0. The state becomes $\frac{1}{\sqrt{2}}(|0000\rangle + |1100\rangle)$.
4. **CNOT(q[1], q[2])**: Flips q2 conditioned on q1. The state becomes $\frac{1}{\sqrt{2}}(|0000\rangle + |1110\rangle)$.
5. **CNOT(q[2], q[3])**: Flips q3 conditioned on q2. The state becomes $\frac{1}{\sqrt{2}}(|0000\rangle + |1111\rangle)$.
6. **Measurements**: Measuring all qubits collapses the maximally entangled GHZ state. 

Predicted probability distribution: {'0000': 0.5, '1111': 0.5}

### Reference answer

{'predicted_probs': {'0000': 0.5, '1111': 0.5}, 'explanation': '4-qubit GHZ'}

## isqTrain/3186

- task_id: `isqTrain/3186`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `488`

### Prompt

Write isQ code for the following quantum task: an isQ program: apply Ry(1*pi/9) to one qubit, then CNOT to a second qubit, creating partial entanglement.

### Chain-of-thought reasoning

## Reasoning
Goal: Create a partially entangled two-qubit state using an Ry rotation followed by a CNOT gate.
Two qubits are required, both measured at the end to observe the entangled state probabilities.
1. Initial state is |00>.
2. Apply Ry(pi/9) to q[0], evolving the state to cos(pi/18)|0> + sin(pi/18)|1> for the first qubit, making the global state cos(pi/18)|00> + sin(pi/18)|10>.
3. Apply CNOT(q[0], q[1]), which flips the target q[1] when the control q[0] is |1>, yielding the final entangled state cos(pi/18)|00> + sin(pi/18)|11>.
4. The expected measurement probabilities are determined by the squared amplitudes of this final state: P(|00>) = cos^2(pi/18) ≈ 0.9698 and P(|11>) = sin^2(pi/18) ≈ 0.0302.

## isqTrain/3364

- task_id: `isqTrain/3364`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3862`

### Prompt

Help me write isQ code that an isQ program: apply H to even-indexed qubits only in a 5-qubit register. Odd qubits stay |0>.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Goal:** Write a reasoning section for an isQ program that applies H to even-indexed qubits (0, 2, 4) of a 5-qubit register.
    *   **Constraints:** 3-8 lines (since it's a simple circuit), use Dirac notation, output ONLY reasoning starting with "## Reasoning", NO code blocks, NO isQ code.
    *   **Input:** The problem description and The implementation.

2.  **Break Down the Circuit:**
    *   **Goal:** Apply H gate to qubits 0, 2, and 4 in a 5-qubit system, leaving 1 and 3 in |0>.
    *   **Qubits:** 5 qubits (q[0] to q[4]).
    *   **Initial State:** $|00000\rangle$
    *   **Step 1:** Apply H to q[0]. State becomes $\frac{1}{\sqrt{2}}(|00000\rangle + |10000\rangle)$ (assuming qubit 0 is the highest bit or just standard notation. Wait, let's look at the bitstring output expectation: {|00000>: 0.125, |00001>: 0.125, |00100>: 0.125, |00101>: 0.125, |10000>: 0.125, |10001>: 0.125, |10100>: 0.125, |10101>: 0.125}. Bitstring is `q[0]q[1]q[2]q[3]q[4]`? Wait, the predicted output have non-zero states: 00000, 00001, 00100, 00101, 10000, 10001, 10100, 10101. In 5 bits (q0 q1 q2 q3 q4), this means q0 and q2 and q4 are superposition. So q0=1 -> 10000. q2=1 -> 00100. q4=1 -> 00001. This confirms q0 is highest bit, q4 is lowest bit.
    *   **Step 2:** Apply H to q[2]. State becomes $\frac{1}{2}(|00000\rangle + |00100\rangle + |10000\rangle + |10100\rangle)$.
    *   **Step 3:** Apply H to q[4]. State becomes $\frac{1}{2\sqrt{2}}(|00000\rangle + |00001\rangle + |00100\rangle + |00101\rangle + |10000\rangle + |10001\rangle + |10100\rangle + |10101\rangle)$.
    *   **Measurement:** Measurement of this state yields equal probabilities for the 8 basis states: $P = (1/(2\sqrt{2}))^2 = 1/8 = 0.125$.

3.  **Draft the Reasoning:**
    *   *Goal:* Apply H to even-indexed qubits (0, 2, 4) of a 5-qubit register.
    *   *State evolution:* Start with $|00000\rangle$. Apply H to q[0], q[2], q[4].
    *   *Evolution detail:* State evolves to $|+\rangle_0|0\rangle_1|+\rangle_2|0\rangle_3|+\rangle_4 = \frac{1}{2\sqrt{2}} \sum_{x \in \{0,1\}^3} |x_0 0 x_2 0 x_4\rangle$.
    *   *Probabilities:* Measurement yields 8 equally likely outcomes (states where odd qubits are 0), each with probability $1/8 = 0.125$.

4.  **Refine and Format:**
    *   Must be 3-8 lines. Start with "## Reasoning".
    *   Line 1: Goal of the circuit: Apply Hadamard gates to the even-indexed qubits (0, 2, 4) of a 5-qubit register.
    *   Line 2: 5 qubits are needed, and all 5 are measured.
    *   Line 3: Initial state is |00000⟩.
    *   Line 4: Applying H to q[0], q[2], and q[4] transforms the state to |+⟩|0⟩|+⟩|0⟩|+⟩.
    *   Line 5: Expanded, this is an equal superposition of the 8 states where odd qubits are |0⟩: (|00000⟩ + |00001⟩

## isqTrain/3394

- task_id: `isqTrain/3394`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `584`

### Prompt

Help me write isQ code that an isQ program: in a 5-qubit register, apply X then H to q[1] only. Other qubits stay |0>. Measure all.

### Chain-of-thought reasoning

## Reasoning
Goal: Prepare qubit q[1] in the |-> state using X and H gates in a 5-qubit register, while others remain |0>, then measure all.
Qubits: 5 qubits, all measured.
Evolution:
- Start: |00000>
- X(q[1]): Flips q[1] to |1>, resulting in |01000>.
- H(q[1]): Puts q[1] into an equal superposition (|0> - |1>)/√2, so the global state becomes (|00000> - |01000>)/√2.
Probabilities: The final state is an equal superposition of |00000> and |01000>, yielding a 50% chance for each outcome.

## isqTrain/4767

- task_id: `isqTrain/4767`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `1243`

### Prompt

Write isQ code for the following quantum task: implements: H on first 6, X on rest of 8 qubits. Declare a global qbit array q of 8 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Task:** Write a reasoning section for a specific isQ quantum program.
    *   **Circuit:** 8 qubits. Hadamard (H) on first 6. X on last 2.
    *   **Output format:** Start with "## Reasoning". No isQ code blocks. Concise (3-15 lines). Dirac notation.
    *   **Key elements to include:** Goal, number of qubits, state evolution, explanation of probabilities.

2.  **Analyze the Circuit:**
    *   **Initial State:** $|0\rangle^{\otimes 8}$
    *   **Qubits:** $q_0$ to $q_5$ (6 qubits), $q_6, q_7$ (2 qubits).
    *   **Operation 1:** $H(q_0)$ to $H(q_5)$.
        *   State becomes $\frac{1}{\sqrt{2^6}} \sum_{x=0}^{63} |x\rangle \otimes |00\rangle_{6,7} = \frac{1}{8} \sum_{x=0}^{63} |x\rangle |00\rangle$
    *   **Operation 2:** $X(q_6)$ and $X(q_7)$.
        *   State becomes $\frac{1}{8} \sum_{x=0}^{63} |x\rangle |11\rangle$
    *   **Measurements:** Measure all 8 qubits.
    *   **Probabilities:** Each of the $2^6 = 64$ combinations of the first 6 qubits has an equal probability of $1/64 = 0.015625$. The last 2 qubits are always $|11\rangle$.
    *   **Bitstrings:** The bitstrings in the predicted output are 8 bits (e.g., `|00000011>`), matching the indices. Let's check the indexing convention: `q[0]` is usually the highest bit in standard string representation (e.g., $q_0 q_1 q_2 q_3 q_4 q_5 q_6 q_7$). The predicted output `xxxxxx11`. Yes, the last two are 1s.

3.  **Draft the Reasoning (Iterative refinement for conciseness and precision):**
    *   *Draft 1:*
        ## Reasoning
        The goal is to prepare a uniform superposition on the first 6 qubits and flip the remaining 2 qubits to the $|1\rangle$ state.
        We use an 8-qubit array, starting in $|0\rangle^{\otimes 8}$, and measure all 8.
        Applying H gates to $q[0]$ through $q[5]$ transforms the first 6 qubits to $|+\rangle^{\otimes 6} = \frac{1}{8} \sum_{x=0}^{63} |x\rangle$.
        The state is now $\frac{1}{8} \sum_{x=0}^{63} |x\rangle |00\rangle$ (for $q[6], q[7]$).
        Applying X gates to $q[6]$ and $q[7]$ flips them to $|1\rangle$, yielding the final state $\frac{1}{8} \sum_{x=0}^{63} |x\rangle |11\rangle$.
        Measuring this state collapses the first 6 qubits to one of 64 possible basis states, each with probability $1/64 \approx 0.0156$, while the last 2 qubits deterministically yield $|1\rangle$.
    *   *Review against constraints:* Start with "## Reasoning"? Yes. No isQ code? Yes. Concise? 5-6 lines. Dirac notation? Yes. State evolution clear? Yes. Probability explained? Yes.

4.  **Final Polish:** Make it slightly punchier.
    ## Reasoning
    The goal is to prepare an 8-qubit state where the first 6 qubits are in a uniform superposition and the last 2 qubits are deterministically in the $|1\rangle$ state.
    We use an 8-qubit register initialized to $|0\rangle^{\otimes 8}$ and measure all 8 qubits.
    Applying H to the first 6 qubits transforms them into $|+\rangle^{\otimes 6} = \frac{1}{8} \sum_{x=0}^{63} |x\rangle$.
    Applying X to $q_6$ and $q_7$ flips them from

## isqTrain/1788

- task_id: `isqTrain/1788`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3836`

### Prompt

Write isQ code for the following quantum task: a CZ ring on 2 qubits (all in |+>): apply CZ between each consecutive pair and between last and first.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a CZ ring on 2 qubits initialized to |+>, applying CZ between consecutive pairs (q[0],q[1]) and wrap-around (q[1],q[0]).
2. **Qubits**: 2 qubits (q[0], q[1]), both measured.
3

## isqTrain/1436

- task_id: `isqTrain/1436`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `355`

### Prompt

I need an isQ program to Put 3 qubits in |+> state, then create a CZ entanglement chain (CZ between consecutive pairs). Measure all qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Prepare 3 qubits in |+⟩ superposition, entangle via a CZ chain, then measure all qubits.

State evolution:
- |000⟩ → H(q[0]) → (|000⟩+|100⟩)/√2
- → H(q[1]) → (|000⟩+|010⟩+|100⟩+|110⟩)/2
- → H(q[2]) → (|000⟩+|001⟩+|010⟩+|011⟩+|100⟩+|101⟩+|110⟩+|111⟩)/2√2
- → CZ(q[0],q[1]) → flips sign when q[0]=q[1]=|1⟩: (|000⟩+|001⟩+|010⟩+|011⟩+|100⟩+|101⟩−|110⟩−|111⟩)/2√2
- → CZ(q[1],q[2]) → flips sign when q[1]=q[2]=|1⟩: (|000⟩+|001⟩+|010⟩−|011⟩+|100⟩+|101⟩−|110⟩+|111⟩)/2√2

All 8 basis states have equal amplitude magnitude 1/(2√2), so each has probability |1/(2√2)|² = 1/8 = 0.125.

## isqTrain/3234

- task_id: `isqTrain/3234`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3117`

### Prompt

Implement the following in isQ: an isQ program: apply Ry(1*pi/3) to q[0] and Ry(1*pi/3) to q[1], then measure both (no entanglement).

### Chain-of-thought reasoning

## Reasoning
The goal is to apply independent Ry rotations of π/3 to two separate qubits and measure them.
Two qubits (q[0] and q[1]) are required, and both are measured.
Starting in the initial state |00⟩, the Ry(π/3) gate rotates each qubit from |0⟩ to cos(π/6)|0⟩ + sin(π/6)|1⟩ = (√3/2)|0⟩ + (1/2)|1⟩.
Since there is no entanglement, the combined state is the tensor product of the individual states: (3/4)|00⟩ + (√3/4)|01⟩ + (√3/4)|10⟩ + (1/4)|11⟩.
The expected measurement probabilities are the squares of the amplitudes: P(00) = (3/4)² = 0.5625, P(01) = P(10) = (√3/4)² = 0.1875,

## isqTrain/3213

- task_id: `isqTrain/3213`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2176`

### Prompt

Write isQ code for the following quantum task: an isQ program: apply Rx(5*pi/16) to a qubit and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply an Rx(5π/16) rotation to a single qubit and measure the resulting state.
2. **Qubits**: 1 qubit (`q[0]`), which is measured.
3. **State evolution**:
   - Initial state: |ψ⟩ = |0⟩
   - After Rx(5π/16): |ψ⟩ = cos(5π/32)|0⟩ - i·sin(5π/32)|1⟩
   - The Rx(θ) gate rotates around the X-axis: Rx(θ)|0⟩ = cos(θ/2)|0⟩ - i·sin(θ/2)|1⟩
4. **Measurement probabilities**:
   - P(|0⟩) = cos²(5π/32) ≈ 0.7778
   - P(|1⟩) = sin²(5π/32) ≈ 0.2222

## isqTrain/3748

- task_id: `isqTrain/3748`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `743`

### Prompt

帮我写一个isQ程序：Prepare a 2-qubit product state by applying Ry(0.5) to q[0] and Ry(1.0) to q[1]. Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare a 2-qubit product state via independent Ry rotations and measure both qubits.
2. **Qubits**: 2 qubits (q[0], q[1]), both measured.
3. **State evolution**:
   - Start: |00⟩
   - After Ry(0.5) on q[0]: (cos(0.25)|0⟩ + sin(0.25)|1⟩) ⊗ |0⟩
   - After Ry(1.0) on q[1]: (cos(0.25)|0⟩ + sin(0.25)|1⟩) ⊗ (cos(0.5)|0⟩ + sin(0.5)|1⟩)
4. **Probabilities** from product state:
   - P(|00⟩) = cos²(0.25)cos²(0.5) ≈ 0.7230
   - P(|01⟩) = cos²(0.25)sin²(0.5) ≈ 0.2158
   - P(|10⟩) = sin²(0.25)cos²(0.5) ≈ 0.0471
   - P(|11⟩) = sin²(0.25)sin²(0.5) ≈ 0.0141
