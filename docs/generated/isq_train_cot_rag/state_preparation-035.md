# ISQ training COT RAG corpus: state_preparation shard 35

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1367

- task_id: `isqTrain/1367`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `entanglement`
- source: `isq_train_cot`
- dataset_index: `2336`

### Prompt

请用isQ语言编写一个量子电路：Prepare a GHZ state on 4 qubits and measure all qubits in the X basis (apply H before measurement).

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare a 4-qubit GHZ state (|0000⟩+|1111⟩)/√2 and measure all qubits in the X-basis.
2. **Qubits**: 4 qubits (q[0]–q[3]), all measured after basis rotation.
3. **State evolution**:
   - Initial: |0000⟩
   - H(q[0]): (|0000⟩+|1000⟩)/√2
   - C

## isqTrain/3876

- task_id: `isqTrain/3876`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `1268`

### Prompt

Implement a quantum circuit in isQ: Prepare a 3-qubit uniform superposition using ket sum assignment. Sum all computational basis states. Measure all.

### Chain-of-thought reasoning

## Reasoning
Goal: Prepare a 3-qubit uniform superposition using direct ket sum assignment of all computational basis states.
Three qubits (q[0], q[1], q[2]) are used and all are measured.
The ket sum `q = |0> + |1> + ... + |7>` assigns the unnormalized state |000>+|001>+|010>+|011>+|100>+|101>+|110>+|111>, which isQ automatically normalizes to (1/√8)(|0⟩+|1⟩+|2⟩+|3⟩+|4⟩+|5⟩+|6⟩+|7⟩) in the 3-qubit space.
Each of the 8 computational basis states has equal amplitude 1/√8, giving probability |1/√8|² = 1/8 = 0.125 for each outcome.
Measurement of all three qubits yields outcomes |000⟩ through |111⟩ each with probability 0.125.

## isqTrain/1433

- task_id: `isqTrain/1433`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5082`

### Prompt

实现以下量子计算任务（使用isQ）：Prepare the state |Psi-> Bell state and measure all qubits.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Prepare the state $|\Psi^-\rangle$ Bell state and measure all qubits.
    *   Role: Quantum computing expert generating reasoning for an isQ quantum program.
    *   Format: Concise step-by-step reasoning, 3-8 lines, starting with "## Reasoning".
    *   Language: Dirac notation (|0>, |1>, etc.).
    *   Constraint: Do NOT include isQ code or code blocks.

2.  **Understand the Target State ($|\Psi^-\rangle$):**
    *   Bell states are maximally entangled states of two qubits.
    *   $|\Psi^-\rangle = \frac{1}{\sqrt{2}}(|01\rangle - |10\rangle)$.

3.  **Determine the Circuit/Steps to achieve $|\Psi^-\rangle$:**
    *   Start with $|00\rangle$.
    *   Apply X to q[1]: $|01\rangle$.
    *   Apply H to q[0]: $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes |1\rangle = \frac{1}{\sqrt{2}}(|01\rangle + |11\rangle)$.
    *   Apply CNOT(q[0], q[1]): If q[0] is |1>, flip q[1].
        *   $|01\rangle \to |01\rangle$
        *   $|11\rangle \to |10\rangle$
        *   Result: $\frac{1}{\sqrt{2}}(|01\rangle + |10\rangle) = |\Psi^+\rangle$.
    *   To get $|\Psi^-\rangle$, we need a relative phase of -1.
        *   Apply Z to q[0]: $\frac{1}{\sqrt{2}}(|01\rangle - |10\rangle)$.
    *   Wait, The implementation says:
        *   `X(q[1])` -> |01>
        *   `H(q[0])` -> (|0> + |1>)|1> = |01> + |11>
        *   `CNOT(q[0], q[1])` -> |01> + |10> ($|\Psi^+\rangle$)
        *   `Z(q[0])` -> |01> - |10> ($|\Psi^-\rangle$)
        *   Yes, this matches perfectly. Alternatively, we could do `X(q[1])` then standard Bell prep, but wait, standard Bell prep is H on q[0], CNOT(q[0], q[1]), then Z(q[0]) gives $|\Psi^-\rangle$? Let's check:
            *   |00> -> X(q[1]) -> |01>
            *   H(q[0]) -> (|0> + |1>)|1> / sqrt(2) = (|01> + |11>) / sqrt(2)
            *   CNOT -> (|01> + |10>) / sqrt(2)
            *   Z(q[0]) -> (|01> - |10>) / sqrt(2) = $|\Psi^-\rangle$.
            *   Perfect.

4.  **Draft the Reasoning Section:**
    *   Goal: Prepare the Bell state $|\Psi^-\rangle = \frac{1}{\sqrt{2}}(|01\rangle - |10\rangle)$ and measure both qubits.
    *   Qubits: 2 qubits (q[0], q[1]), both measured.
    *   Evolution:
        *   Initial state: $|00\rangle$
        *   `X(q[1])`: Flips q[1] to yield $|01\rangle$.
        *   `H(q[0])`: Creates superposition $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)|1\rangle = \frac{1}{\sqrt{2}}(|01\rangle + |11\rangle)$.
        *   `CNOT(q[0], q[1])`: Entangles qubits, resulting in $\frac{1}{\sqrt{2}}(|01\rangle + |10\rangle) = |\Psi^+\rangle$.
        *   `Z(q[0])`: Applies a -1 phase to the |1> state of q[0], changing $|\Psi^+\rangle$ to $\frac{1}{\sqrt{2}}(|01\rangle - |10\rangle) = |\Psi^-\rangle$.
    *   Measurement: The final state has equal probability amplitudes for $|01\rangle$

## isqTrain/145

- task_id: `isqTrain/145`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `1293`

### Prompt

实现以下量子计算任务（使用isQ）：implements a variant of the state_preparation pattern using q[1] -> q[3]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Prepare a single-qubit superposition on q[0] via Rx(π/3), leaving q[1] and q[2] in |0⟩.

2. **Qubits**: 3-qubit register (q[0], q[1], q[2]), all measured.

3. **State evolution**:
   - Initial: |000⟩
   - After Rx(π/3) on q[0]: cos(π/6)|000⟩ − i·sin(π/6)|100⟩ = (√3/2)|000⟩ − (i/2)|100⟩

4. **Probabilities**:
   - P(|000⟩) = |√3/2|² = 3/4 = 0.75
   - P(|100⟩) = |−i/2|² = 1/4 = 0.25

## isqTrain/4207

- task_id: `isqTrain/4207`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `845`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[4];

procedure main() {
    H(q[0]);
    Rz(3.14159265358979 * 1.0 / 4.0, q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis

**Gate sequence:**
1. H(q[0]) — Hadamard on q[0]
2. Rz(π/4, q[0]) — Phase rotation of π/4 on q[0]
3. CNOT(q[0], q[1]) — Entangles q[0] and q[1]
4. CNOT(q[1], q[2]) — Propagates entanglement to q[2]
5. CNOT(q[2], q[3]) — Propagates entanglement to q[3]

**State evolution:**
- Initial: |0000⟩
- After H(q[0]): (|0000⟩ + |1000⟩)/√2
- After Rz(π/4, q[0]): (|0000⟩ + e^(iπ/4)|1000⟩)/√2
- After CNOT(q[0], q[1]): (|0000⟩ + e^(iπ/4)|1100⟩)/√2
- After CNOT(q[1], q[2]): (|0000⟩ + e^(iπ/4)|1110⟩)/√2
- After CNOT(q[2], q[3]): (|0000⟩ + e^(iπ/4)|1111⟩)/√2

**Final state:** (|0000⟩ + e^(iπ/4)|1111⟩)/√2 — a GHZ-like state with relative phase e^(iπ/4).

**Predicted probability distribution:**
- P(0000) = 0.5 (50%)
- P(1111) = 0.5 (50%)
- All other outcomes: 0

Both |0000⟩ and |1111⟩ are equally likely. The Rz(π/4) phase does not affect measurement probabilities.

### Reference answer

Dominant output states: |0000>, |1111> with probability ~0.50 each

## isqTrain/3388

- task_id: `isqTrain/3388`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `5146`

### Prompt

I need an isQ program to an isQ program: in a 3-qubit register, apply X then H to q[1] only. Other qubits stay |0>. Measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare q[1] in the |−⟩ state via X then H, keeping q[0] and q[2] at |0⟩.
2. **Qubits**: 3-qubit register, all measured at the end.
3. **State evolution**:
   - Start: |000⟩
   - X(q[1]): |010⟩ — flips q[1] from |0⟩ to |1⟩
   - H(q[1]): |0⟩⊗H|1⟩⊗|0⟩ = |0⟩⊗|−⟩⊗|0⟩ = (|000⟩ − |010⟩)/√2
4. **Probabilities**: Measuring yields |000⟩ with probability 0.5 and |010⟩ with probability 0.5, since each amplitude has magnitude 1/√2.

## isqTrain/3299

- task_id: `isqTrain/3299`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_for_loop`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `1400`

### Prompt

Write isQ code for the following quantum task: an isQ program: use a for loop to apply X to all 6 qubits, preparing |111111>.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Prepare the 6-qubit state |111111⟩ by applying X gates to all qubits initialized to |0⟩.

**Qubits:** 6 qubits q[0]–q[5], all measured.

**State evolution:**
- Initial state: |000000⟩
- For i=0: X(q[0]) → |100000⟩
- For i=1: X(q[1]) → |110000⟩
- For i=2: X(q[2]) → |111000⟩
- For i=3: X(q[3]) → |111100⟩
- For i=4: X(q[4]) → |111110⟩
- For i=5: X(q[5]) → |111111⟩

**Expected probabilities:** Since the final state is exactly |111111⟩, measurement yields bitstring 111111 with probability 1.0.

## isqTrain/1784

- task_id: `isqTrain/1784`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `353`

### Prompt

Help me write isQ code that Apply H then Z to each of 5 qubits. Measure all. Z phase is invisible in Z-basis measurement.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Apply H then Z to each of 5 qubits and measure; Z is invisible in Z-basis measurement.

**Qubits:** 5 qubits declared globally, all 5 measured.

**State evolution (all qubits follow identical transformation):**
- Initial state: |00000⟩
- After H on all: |+++++⟩, where each qubit is |+⟩ = (|0⟩+|1⟩)/√2
- After Z on all: |-----⟩, where Z|+⟩ = (|0⟩-|1⟩)/√2 = |-⟩

**Why uniform distribution:** Measuring |-⟩ in Z-basis gives P(0)=|1/√2|²=0.5 and P(1)=|-1/√2|²=0.5, identical to measuring |+⟩. The Z-induced phase is invisible in Z-basis. All 32 outcomes have equal probability 1/32 = 0.03125.

## isqTrain/1885

- task_id: `isqTrain/1885`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `4647`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
qbit q[1];
procedure main() {
    Rx(pi/3.0, q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1.  **Initial state**: The single qubit `q[0]` starts in the ground state $|0\rangle$.
2.  **Rx Gate**: Applies an $R_x(\pi/3)$ rotation around the x-axis.
3.  **State Evolution**: The $R_x(\theta)$ gate transforms the state to $\cos(\theta/2)|0\rangle - i\sin(\theta/2)|1\rangle$. Substituting $\theta = \pi/3$, the resulting state is $\frac{\sqrt{3}}{2}|0\rangle - \frac{i}{2}|1\rangle$.
4.  **Measurement**: The probability of measuring $|0\rangle$ is $|\frac{\sqrt{3}}{2}|^2 = 0.75$, and the probability of measuring $|1\rangle$ is $|-i/2|^2 = 0.25$.

Predicted probability distribution: {'0': 0.75, '1': 0.25}

### Reference answer

{'predicted_probs': {'0': 0.75, '1': 0.25}, 'explanation': 'Expected probabilities: [0.7500000000000001, 0.24999999999999994]'}

## isqTrain/3366

- task_id: `isqTrain/3366`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `480`

### Prompt

请用isQ语言编写一个量子电路：an isQ program: apply H to odd-indexed qubits only in a 3-qubit register.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply H gate to odd-indexed qubit(s) only in a 3-qubit register, leaving even-indexed qubits untouched.
We need 3 qubits (q[0], q[1], q[2]); all are measured to produce a 3-bit outcome.
Initial state: |000⟩. Only q[1] (index 1, the odd-indexed qubit) receives H, transforming it: |0⟩ → |+⟩ = (|0⟩+|1⟩)/√2.
Final state: |0⟩⊗|+⟩⊗|0⟩ = (|000⟩+|010⟩)/√2, so measuring all qubits yields |000⟩ or |010⟩ each with probability 0.5.
