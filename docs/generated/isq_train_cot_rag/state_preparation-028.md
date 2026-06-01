# ISQ training COT RAG corpus: state_preparation shard 28

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4806

- task_id: `isqTrain/4806`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `isq_syntax_switch`, `isq_syntax_classical_vars`, `mid_circuit_measurement`
- source: `isq_train_cot`
- dataset_index: `5108`

### Prompt

Help me write isQ code that using two sequential switch statements. Declare 3 global qubits. Set q[0] to |1> and q[1] to |0>. Measure q[0] into x, measure q[1] into y. First switch(x): case 0 does nothing, case 1 applies X(q[2]). Second switch(y): case 0 does nothing, case 1 applies Z(q[2]). Since x=1 and y=0, only X(q[2]) is applied. Measure q[2]. Expected: |101>.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

1. We have 3 qubits: q[0], q[1], q[2]
2. Initial state: |000⟩

Step 1: X(q[0]) - applies X gate to q[0]
- State becomes: |100⟩

Step 2: M(q[0]) measures q[0] - gets x = 1 (deterministic since q[0] is |1⟩)

Step 3: M(q[1]) measures q[1] - gets y = 0 (deterministic since q[1] is |0⟩)

Step 4: First switch(x) where x=1
- Case 1 applies X(q[2])
- Wait, Analyzing the code more carefully:
  - case 0: { Z(q[2]); }
  - case 1: { X(q[2]); }
- So when x=1, X(q[2]) is applied
- State becomes: |101⟩

Step 5: Second switch(y) where y=0
- Looking at reference code:
  - case 0: { Z(q[2]); }
  - case 1: { H(q[2]); }
- So when y=0, Z(q[2]) is applied
- Z on |1⟩ state gives -|1⟩
- State becomes: -|101⟩ (global phase, so effectively |101⟩)

Wait, but the prompt says:
"First switch(x): case 0 does nothing, case 1 applies X(q[2]). Second switch(y): case 0 does nothing, case 1 applies Z(q[2])."

But The circuit should:
- First switch: case 0 is Z(q[2]), case 1 is X(q[2])
- Second switch: case 0 is Z(q[2]), case 1 is H(q[2])

There's a discrepancy between the prompt description and The implementation. Let me re-read.

The prompt says:
"First switch(x): case 0 does nothing, case 1 applies X(q[2]). Second switch(y): case 0 does nothing, case 1 applies Z(q[2]). Since x=1 and y=0, only X(q[2]) is applied."

So according to the prompt:
- x=1 triggers case 1 which applies X(q[2])
- y=0 triggers case 0 which does nothing

But the reference code shows:
- First switch case 0: Z(q[2]), case 1: X(q[2])
- Second switch case 0: Z(q[2]), case 1: H(q[2])

Hmm, there's definitely a mismatch. Let me follow the prompt description which says case 0 does nothing in both cases.

Actually, looking at the expected measurement probabilities: {|100>: 0.5, |101>: 0.5}

This doesn't match |101> with 100% probability as the prompt says "Expected: |101>".

Let me reconsider. The circuit should:
- First switch case 0: Z(q[2]) - but we have x=1, so this isn't triggered
- First switch case 1: X(q[2]) - this is triggered, applies X to q[2]
- Second switch case 0: Z(q[2]) - we have y=0, so this IS triggered
- Second switch case 1: H(q[2]) - not triggered

So the operations on q[2] are: X(q[2]) then Z(q[2])

Starting state of q[2]: |0⟩
After X: |1⟩
After Z on |1⟩: -|1⟩ (global phase)

So the final state is -|101⟩ which is effectively |101⟩.

But The predicted output {|100>: 0.5, |101>: 0.5}... that doesn't make sense with what I've calculated.

Wait, maybe I'm misreading the reference code. Let me look again:

In isQ, does `switch` work like C where it falls through? If so, when x=1, it would execute case 1 AND then fall through to execute case 0 as well... but that seems unlikely for a quantum language.

Actually, in most quantum languages (like Qiskit), switch statements don't fall through. Each case is independent.

Let me recalculate assuming no fall-through:
- x=1: execute case 1 → X(q[2])
- y=0: execute case 0 → Z(q[2])

After X(q[2]): q[2] goes from |0⟩ to |1

## isqTrain/3150

- task_id: `isqTrain/3150`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `2528`

### Prompt

请用isQ语言编写一个量子电路：an isQ program: apply X to all 6 qubits to prepare |111111>, then measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare the 6-qubit state |111111⟩ from |000000⟩ by flipping each qubit with an X gate, then measure all qubits.
2. **Qubits**: 6 qubits allocated (q[0]–q[5]), all are measured.
3. **State evolution**:
   - Start: |000000⟩
   - After X on each qubit sequentially: |000000⟩ → |100000⟩ → |110000⟩ → |111000⟩ → |111100⟩ → |111110⟩ → |111111⟩
   - Each X gate flips |0⟩ to |1⟩ on its respective qubit.
4. **Expected probabilities**: The final state is exactly |111111⟩, so measurement yields outcome 111111 with probability 1.0.

## isqTrain/405

- task_id: `isqTrain/405`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `419`

### Prompt

Write isQ code for the following quantum task: implements a variant of the state_preparation pattern using q[3] -> q[5]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Generate reasoning for an isQ quantum program implementing a variant of the `state_preparation` pattern using `q[3] -> q[5]`.
    *   Target state: The circuit prepares a 3-qubit W state (|00100> + |01000> + |10000>) using a 5-qubit register. Wait, the prompt says "q[3] -> q[5]" which means going from 3 qubits to 5 qubits.
    *   circuit implementation: Prepares state via state vector initialization `q = [...]` and measures all 5 qubits.
    *   Expected probabilities: |00100>: 1/3, |01000>: 1/3, |10000>: 1/3.
    *   Output format: ONLY the reasoning section, starting with "## Reasoning", using Dirac notation, concise.

2.  **Analyze the circuit implementation:**
    *   `qbit q[5];`
    *   State vector `q = [...]` represents a 3-qubit W state mapped onto the first 3 qubits, with the last 2 qubits being |00>.
    *   Let's verify the state vector indexing:
        *   |00000> = index 0  -> 0.0
        *   |00001> = index 1  -> 0.577... (1/sqrt(3))
        *   |00010> = index 2  -> 0.577...
        *   |00011> = index 3  -> 0.0
        *   |00100> = index 4  -> 0.577...
        *   |00101> = index 5  -> 0.0
        *   etc.
    *   Wait, the isQ vector is 8 elements long. `q = [...]` on `q[5]`? Ah, if `q = [...]` is given an 8-element vector for a 5-qubit register (32-dimensional), it will likely zero-pad or fail. But wait, let me look at the exact expected bitstrings: `|00100>` (index 4), `|01000>` (index 8?? no, |01000> is 8), `|10000>` (index 16).
    *   Wait! The circuit should EXACTLY 8 elements: `[0.0, 0.5773502691896257, 0.5773502691896257, 0.0, 0.5773502691896257, 0.0, 0.0, 0.0]`.
    *   Indices: 0, 1, 2, 3, 4, 5, 6, 7.
    *   Index 1: |001> -> mapped to qubits?
    *   If it's mapped to a 5-qubit register, maybe isQ interprets it as q[0..2]? No, The resulting probabilities should be `|00100>: 1/3, |01000>: 1/3, |10000>: 1/3`.
    *   Wait! `|00100>` has the 1 at index 2 (0-indexed from right: 2^2 = 4).
    *   `|01000>` has the 1 at index 3 (2^3 = 8).
    *   `|10000>` has the 1 at index 4 (2^4 = 16).
    *   If the vector is 8 elements, it corresponds to indices 0..7.
    *   If The resulting probabilities should be at 4, 8, 16, how can an 8-element vector produce them?
    *   Ah! Let's re-read the reference vector.
        *   `q = [0.0, 0.577, 0.577, 0.0, 0.577, 0.0, 0.0, 0.0];`
        *   Wait, 8 elements.
        *   Is it possible isQ zero-pads the *end* of the vector? No, if it zero pads, index 1, 2, 4 are non-zero. Which is |001>, |010>, |100> for a 3-qubit system. But the system is 5 qubits. If `q = [...]` sets the state of the *first* 3 qubits, and the remaining are |0>, then:
        *   Non-zero indices in 5-qubit basis:
            *   |00100> is index 4. (Wait, q[2]=1

## isqTrain/3379

- task_id: `isqTrain/3379`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `superposition`, `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5114`

### Prompt

用isQ实现an isQ program: 3-layer circuit with H and CZ on 4 qubits. Each layer: H on all, then CZ between adjacent.

### Chain-of-thought reasoning

Let me trace through this 3-layer H+CZ circuit on 4 qubits.

Initial state: |0000>

**Layer 1:**
- H on all 4 qubits: |0000⟩ → |++++⟩ = H⊗4|0000⟩
- CZ(0,1): applies Z to q1 when q0=|1⟩
- CZ(1,2): applies Z to q2 when q1=|1⟩
- CZ(2,3): applies Z to q3 when q2=|1⟩

The H+CZ layer creates a GHZ-like entangled state. Let me think more carefully.

After H on all: |++++⟩ = (1/4)(|0000⟩ + |0001⟩ + |0010⟩ + ... + |1111⟩) = uniform superposition over all 16 states.

CZ(0,1): flips sign of states where both q0=1 AND q1=1. So states |1100⟩, |1101⟩, |1110⟩, |1111⟩ get a -1 phase.

CZ(1,2): flips sign when q1=1 AND q2=1. States: |0110⟩, |0111⟩, |1110⟩, |1111⟩ get -1.

CZ(2,3): flips sign when q2=1 AND q3=1. States: |0011⟩, |0111⟩, |1011⟩, |1111⟩ get -1.

After all three CZ gates, let me track the phase of each computational basis state:

|0000⟩: no CZ applies → +1
|0001⟩: CZ(2,3) applies → -1
|0010⟩: no CZ → +1
|0011⟩: CZ(2,3) → -1
|0100⟩: no CZ → +1
|0101⟩: no CZ → +1
|0110⟩: CZ(1,2) → -1
|0111⟩: CZ(1,2) and CZ(2,3) → +1
|1000⟩: no CZ → +1
|1001⟩: no CZ → +1
|1010⟩: no CZ → +1
|1011⟩: CZ(2,3) → -1
|1100⟩: CZ(0,1) → -1
|1101⟩: CZ(0,1) → -1
|1110⟩: CZ(0,1) and CZ(1,2) → +1
|1111⟩: CZ(0,1) and CZ(1,2) and CZ(2,3) → -1

Wait, let me be more careful.

CZ(0,1): phase flip when q0=1 AND q1=1
CZ(1,2): phase flip when q1=1 AND q2=1
CZ(2,3): phase flip when q2=1 AND q3=1

Let me list each state and count how many CZ gates apply:

|0000⟩: 0 → +1
|0001⟩: 0 → +1
|0010⟩: 0 → +1
|0011⟩: CZ(2,3) → -1
|0100⟩: 0 → +1
|0101⟩: 0 → +1
|0110⟩: CZ(1,2) → -1
|0111⟩: CZ(1,2), CZ(2,3) → +1
|1000⟩: 0 → +1
|1001⟩: 0 → +1
|1010⟩: 0 → +1
|1011⟩: CZ(2,3) → -1
|1100⟩: CZ(0,1) → -1
|1101⟩: CZ(0,1) → -1
|1110⟩: CZ(0,1), CZ(1,2) → +1
|1111⟩: CZ(0,1), CZ(1,2), CZ(2,3) → -1

So after Layer 1:
(1/4)(|0000⟩ + |0001⟩ + |0010⟩ - |0011⟩ + |0100⟩ + |0101⟩ - |0110⟩ + |0111⟩ + |1000⟩ + |1001⟩ + |1010⟩ - |1011⟩ - |1100⟩ - |1101⟩ + |1110⟩ - |1111⟩)

This is getting complex. The key observation is that 3 layers of H+CZ on 4 qubits... Let me think about what the

## isqTrain/1793

- task_id: `isqTrain/1793`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `996`

### Prompt

Help me write isQ code that Bell pairs on 3 qubits (pair q[0]-q[1], q[2]-q[3], etc.) and measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a Bell pair between q[0] and q[1] (q[2] remains unentangled), then measure all three qubits.
2. **Qubits**: 3 qubits declared; all three are measured.
3. **State evolution**:
   - Initial state: |000⟩
   - After H(q[0]): (|0⟩ + |1⟩)/√2 ⊗ |0⟩ ⊗ |0⟩ = (|000⟩ + |100⟩)/√2
   - After CNOT(q[0], q[1]): (|000⟩ + |110⟩)/√2 — q[0] and q[1] are now maximally entangled (Bell state Φ⁺), q[2] stays |0⟩
4. **Expected probabilities**: Measurement yields |000⟩ with 50% and |110⟩ with 50%. In bitstring indexing (earlier measured qubit = higher bit), this corresponds to `probs[0b000] = 0.5` and `probs[0b110] = 0.5`.

## isqTrain/3755

- task_id: `isqTrain/3755`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5008`

### Prompt

实现以下量子计算任务（使用isQ）：an entangled 2-qubit state by applying Ry(1.571) to q[0] followed by CNOT(q[0], q[1]). This creates cos(θ/2)|00> + sin(θ/2)|11>. Measure both qubits.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Create a maximally entangled 2-qubit Bell-like state using Ry(π/2) + CNOT, then measure both qubits.

**Qubits:** 2 qubits (q[0], q[1]), both measured.

**State evolution:**
1. Initial state: |00⟩
2. After Ry(1.571, q[0]): cos(1.571/2)|00⟩ + sin(1.571/2)|10⟩ ≈ 0.7070|00⟩ + 0.7071|10⟩
   - (1.571 ≈ π/2, so θ/2 ≈ π/4)
3. After CNOT(q[0], q[1]): 0.7070|00⟩ + 0.7071|11⟩ (flips q[1] when q[0]=|1⟩)

**Expected probabilities:**
- P(|00⟩) = cos²(π/4) ≈ 0.499898
- P(|11⟩) = sin²(π/4) ≈ 0.500102
- Note: θ = 1.571 ≈ π/2 but not exact, so probabilities are not exactly 50/50.

## isqTrain/1460

- task_id: `isqTrain/1460`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3814`

### Prompt

I need an isQ program to Prepare the computational basis state |00110> on 5 qubits by applying X gates to the appropriate qubits, then measure all.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Prepare the 5-qubit computational basis state |00110> and measure all qubits.
2. Qubits: 5 qubits q[0..4], all measured.
3. State evolution: Start in |00000>. Apply X(q[2]) → |00100>. Apply X(q[3]) → |00110>. All other qubits remain in |0>.
4. Measurement outcome: Measuring the final state |00110> yields the bitstring "00110" with probability 1.0.

## isqTrain/1798

- task_id: `isqTrain/1798`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `2096`

### Prompt

实现以下量子计算任务（使用isQ）：Apply H to even-indexed qubits and X to odd-indexed qubits on 5 qubits. Measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply H to even-indexed qubits (0,2,4) and X to odd-indexed qubits (1,3) on 5 qubits, then measure all.
2. **Qubits**: 5 qubits q[0..4], all measured.
3. **State evolution** from |00000⟩:
   - H(q[0]) → (|00000⟩ + |10000⟩)/√2
   - X(q[1]) → (|01000⟩ + |11000⟩)/√2
   - H(q[2]) → (|01000⟩ + |01100⟩ + |11000⟩ + |11100⟩)/2
   - X(q[3]) → (|01010⟩ + |01110⟩ + |11010⟩ + |11110⟩)/2
   - H(q[4]) → (|01010⟩ + |01011⟩ + |01110⟩ + |01111⟩ + |11010⟩ + |11011⟩ + |11110⟩ + |11111⟩)/(2√2)
4. **Probabilities**: All 8 outcomes with q[1]=1 and q[3]=1 have equal probability 1/8. Qubits q[0], q[2], q

## isqTrain/1555

- task_id: `isqTrain/1555`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `2405`

### Prompt

Help me write isQ code that Apply Y gate to each of 5 qubits and measure all.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Apply the Y gate to each of 5 qubits and measure all, producing a deterministic |11111⟩ state.

**Qubits:** 5 qubits allocated (q[0]–q[4]), all measured.

**State Evolution:**
1. Initial state: |00000⟩
2. Y|0⟩ = i|1⟩, so applying Y to each qubit transforms |00000⟩ → i⁵|11111⟩ = i|11111⟩ (global phase is irrelevant for measurement)
3. All qubits measured in the computational basis

**Expected Probabilities:** {|11111⟩: 1.0} — The Y gate deterministically maps |0⟩ → i|1⟩, so measuring all qubits yields 11111 with certainty.

## isqTrain/4202

- task_id: `isqTrain/4202`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`, `entanglement`
- source: `isq_train_cot`
- dataset_index: `804`

### Prompt

What measurement results should I expect from this quantum program?

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

1.  **Analyze the Request:**
    *   **Input:** An isQ quantum circuit:
        
    *   **Goal:** Predict the measurement output, explain step-by-step state evolution using Dirac notation, and provide the probability distribution.
    *   **Constraints:** Concise (3-15 lines), output ONLY the analysis starting with "## Circuit Analysis", no code blocks, end with the probability distribution, use Dirac notation.

2.  **Circuit Breakdown & State Evolution:**
    *   **Initial state:** $|q_0 q_1 q_2\rangle = |000\rangle$
    *   **Gate 1:** `H(q[0])` applies Hadamard to $q_0$.
        *   State becomes $\frac{1}{\sqrt{2}}(|000\rangle + |100\rangle) = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes |00\rangle$. Wait, standard notation for 3 qubits is usually $|q_2 q_1 q_0\rangle$ or $|q_0 q_1 q_2\rangle$. Let's use $|q_0, q_1, q_2\rangle$.
        *   State: $\frac{1}{\sqrt{2}}(|000\rangle + |100\rangle)$
    *   **Gate 2:** `CNOT(q[0], q[1])` flips $q_1$ if $q_0$ is $|1\rangle$.
        *   State: $\frac{1}{\sqrt{2}}(|000\rangle + |110\rangle)$
    *   **Gate 3:** `CNOT(q[1], q[2])` flips $q_2$ if $q_1$ is $|1\rangle$.
        *   State: $\frac{1}{\sqrt{2}}(|000\rangle + |111\rangle)$
    *   This is the GHZ state.

3.  **Measurement Output:**
    *   The state is a superposition of $|000\rangle$ and $|111\rangle$.
    *   Probability of 000 is $|1/\sqrt{2}|^2 = 0.5$.
    *   Probability of 111 is $|1/\sqrt{2}|^2 = 0.5$.
    *   All other states have probability 0.

4.  **Drafting the Response:**
    *   *Rule check:* Start with "## Circuit Analysis".
    *   *Rule check:* End with the probability distribution.
    *   *Rule check:* Concise, Dirac notation.

    *Drafting lines:*
    ## Circuit Analysis
    1. Initial state is $|000\rangle$.
    2. `H(q[0])` puts $q_0$ into superposition: $\frac{1}{\sqrt{2}}(|000\rangle + |100\rangle)$.
    3. `CNOT(q[0], q[1])` entangles $q_0$ and $q_1$: $\frac{1}{\sqrt{2}}(|000\rangle + |110\rangle)$.
    4. `CNOT(q[1], q[2])` entangles $q_1$ and $q_2$: $\frac{1}{\sqrt{2}}(|000\rangle + |111\rangle)$ (GHZ state).
    5. The final state is an equal superposition of all qubits being 0 or all being 1.
    6. Probability distribution: 50% for 000, 50% for 111.

5.  **Refining and Formatting:**
    Make sure it strictly adheres to "End with the predicted probability distribution".

    ## Circuit Analysis
    1. The circuit starts with the initial state |000>.
    2. `H(q[0])` puts the first qubit into superposition, resulting in (1/√2)(|000> + |100>).
    3. `CNOT(q[0], q[1])` flips the second qubit, creating entanglement: (1/√2)(|000> + |110>).
    4. `CNOT(q[1], q[2])` flips the third qubit based on the second, yielding the 3-qubit GHZ state: (1/√2)(|000> + |111>).

### Reference answer

Dominant output states: |000>, |111> with probability ~0.50 each
