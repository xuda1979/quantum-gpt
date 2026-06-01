# ISQ training COT RAG corpus: state_preparation shard 39

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1372

- task_id: `isqTrain/1372`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `242`

### Prompt

I need an isQ program to Prepare a GHZ state on 6 qubits, then apply a Z gate to the first qubit to create a relative phase. Measure all qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a 6-qubit GHZ state with a relative Z phase, then measure all qubits.

2. **Qubits**: 6 qubits declared (`q[0]` to `q[5]`), all measured.

3. **State evolution**:
   - Initial state: |000000⟩
   - H(q[0]): (|000000⟩ + |100000⟩)/√2
   - CNOT(q[0], q[1]): (|000000⟩ + |110000⟩)/√2
   - CNOT(q[0], q[2]): (|000000⟩ + |111000⟩)/√2
   - CNOT(q[0], q[3]): (|000000⟩ + |111100⟩)/√2
   - CNOT(q[0], q[4]): (|000000⟩ + |111110⟩)/√2
   - CNOT(q[0], q[5]): (|000000⟩ + |111111⟩)/√2 — GHZ state
   - Z(q[0]): (|000000⟩ - |111111⟩)/√2 — applies -1 phase to |1⟩ on q[0]

4. **Expected probabilities**: The Z gate introduces a relative phase of -1, but measurement probabilities are unchanged: {|000000⟩: 0.5, |111111⟩: 0.5}, since |(1/√2)|² = |(-1/√2)|² = 0.5.

## isqTrain/3129

- task_id: `isqTrain/3129`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `3740`

### Prompt

帮我写一个isQ程序：an isQ program: use a for loop to apply H to each of 3 qubits, then measure all with a for loop.

### Chain-of-thought reasoning

## Reasoning
Goal: Prepare three qubits in |+> state via Hadamard gates and measure them, yielding a uniform distribution over all 3-bit strings.

Three qubits are declared globally; all are measured.

State evolution:
- Initial: |000⟩.
- After H on qubit 0: (|0⟩+|1⟩)/√2 ⊗ |00⟩ = (|0⟩+|1⟩)/√2 ⊗ |00⟩.
- After H on qubit 1: (|0⟩+|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2 ⊗ |0⟩.
- After H on qubit 2: (|0⟩+|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2 = |+++⟩ = (1/√8) ∑_{x∈{0,1}³} |x⟩.

Measurement of all qubits yields each basis state |x⟩ with probability |1/√8|² = 1/8 = 0.125, giving uniform probabilities for |000⟩ to |111⟩.

## isqTrain/1796

- task_id: `isqTrain/1796`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `1063`

### Prompt

Implement a quantum circuit in isQ: Apply H to even-indexed qubits and X to odd-indexed qubits on 3 qubits. Measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply H to even-indexed qubits (0,2) and X to odd-indexed qubit (1) on 3 qubits, then measure all.
2. **Qubits**: 3 qubits (q[0], q[1], q[2]), all measured.
3. **State evolution**:
   - Initial: |000⟩
   - H(q[0]): (|000⟩ + |100⟩)/√2
   - X(q[1]): (|010⟩ + |110⟩)/√2
   - H(q[2]): (|010⟩ + |011⟩ + |110⟩ +

## isqTrain/4205

- task_id: `isqTrain/4205`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5319`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[3];

procedure main() {
    H(q[0]);
    Rz(3.14159265358979 * 4.0 / 4.0, q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. Initial state is $|000\rangle$. The Hadamard gate $H(q[0])$ creates the superposition $\frac{1}{\sqrt{2}}(|000\rangle + |100\rangle)$.
2. The $Rz(\pi, q[0])$ gate applies a phase flip equivalent to the Z gate, changing the state to $\frac{1}{\sqrt{2}}(|000\rangle - |100\rangle)$.
3. $CNOT(q[0], q[1])$ entangles $q[1]$ with $q[0]$, evolving the state to $\frac{1}{\sqrt{2}}(|000\rangle - |110\rangle)$.
4. $CNOT(q[

### Reference answer

Dominant output states: |000>, |111> with probability ~0.50 each

## isqTrain/559

- task_id: `isqTrain/559`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `1189`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;
qbit q[5];

procedure main() {
    X(q[0]);
    X(q[2]);
    M(q);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes a 5-qubit register to the ground state |00000>.
2. An X gate is applied to `q[0]`, flipping its state to |1>. The system state becomes |00001>.
3. An X gate is applied to `q[2]`, flipping its state to |1>. The system state becomes |00101>.
4. No other operations are applied, and measuring the qubits collapses the system deterministically into this final basis state.

Predicted probability distribution: {|00101>: 1.0}

### Reference answer

{'predicted_probs': {'5': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/178. Dimension: predict probabilities for reference circuit.'}

## isqTrain/4813

- task_id: `isqTrain/4813`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_switch`, `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5567`

### Prompt

Write an isQ program that uses switch to select an entanglement pattern. Declare 3 global qubits. Set int mode=2 (last case, no fall-through). Use switch(mode): case 0 entangles q[0]-q[1] (H, CNOT), case 1 entangles q[1]-q[2] (H, CNOT), case 2 creates a GHZ state (H on q[0], CNOT to q[1], CNOT to q[2]). Since mode=2, create GHZ=(|000>+|111>)/sqrt(2). Measure all. Expected: 50% |000> + 50% |111>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a GHZ state (|000⟩ + |111⟩)/√2 using a switch statement with mode=2.
2. **Qubits**: 3 global qubits q[0], q[1], q[2]; all measured at the end.
3. **State evolution** (mode=2 case):
   - |000⟩ → H(q[0]) → (|000⟩ + |100⟩)/√2
   - CNOT(q[0], q[1]) → (|000⟩ + |110⟩)/√2
   - CNOT(q[0], q[2]) → (|000⟩ + |111⟩)/√2
4. **Expected probabilities**: Equal superposition of |000⟩ and |111⟩ gives 50% each.

## isqTrain/3874

- task_id: `isqTrain/3874`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4315`

### Prompt

Create an isQ quantum circuit that Prepare the 3-qubit W-state using amplitude array assignment. Set amplitudes for |001>, |010>, |100> (indices 1, 2, 4 in little-endian). Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare the 3-qubit W-state, $|W\rangle = \frac{1}{\sqrt{3}}(|001\rangle + |010\rangle + |100\rangle)$, using an amplitude array assignment, and measure all qubits.
2. **Qubits**: 3 qubits are required (`q[3]`), and all 3 are measured.
3. **State Evolution**: The system begins in $|000\rangle$. By assigning `q = [0, 1, 1, 0, 1, 0, 0, 0]`, the state is directly initialized to an equal superposition across the basis states corresponding to indices 1, 2, and 4. In little-endian order, these indices represent $|001\rangle$, $|010\rangle$, and $|100\rangle$.
4. **Probabilities**: The final state is an exact uniform superposition of three basis states. Thus, measurement yields $|001\rangle$, $|010\rangle$, and $|100\rangle$, each with a probability of $1/3 \approx 0.3333$.

## isqTrain/4204

- task_id: `isqTrain/4204`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `716`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
qbit q[3];

procedure main() {
    H(q[0]);
    Rz(3.14159265358979 * 2.0 / 4.0, q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations applied:**
   - `H(q[0])`: Applies a Hadamard gate to qubit 0.
   - `Rz(3.14159265358979 *

### Reference answer

Dominant output states: |000>, |111> with probability ~0.50 each

## isqTrain/3837

- task_id: `isqTrain/3837`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `52`

### Prompt

I need an isQ program to Prepare the graph state for a line 3 graph with 3 nodes and edges [(0, 1), (1, 2)]. Apply Hadamard to all qubits, then CZ for each edge. Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare a 3-qubit line graph state and measure all qubits.
2. **Qubits**: 3 qubits (q[0], q[1], q[2]), all measured.
3. **State evolution**:
   - Initial: |000⟩
   - After H on all: |+++⟩ = (1/√8)∑_{x,y,z}|xyz⟩
   - CZ(q[0],q[1]): applies phase (-1)^(x·y) → (1/√8)∑(-1)^(xy)|xyz⟩
   - CZ(q[1],q[2]): applies phase (-1)^(y·z) → (1/√8)∑(-1)^(xy+yz)|xyz⟩
4. **Final state**: |G⟩ = (1/√8)(|000⟩+|001⟩+|010⟩-|011⟩+|100⟩+|101⟩-|110⟩+|111⟩)
5. **Probabilities**: Each computational basis state has amplitude ±1/√8, giving probability |±1/√8|² = 1/8 = 0.125 for all 8 outcomes.

## isqTrain/4212

- task_id: `isqTrain/4212`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2235`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
qbit q[5];

procedure main() {
    H(q[0]);
    Rz(3.14159265358979 * 2.0 / 4.0, q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
    CNOT(q[3], q[4]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]); M(q[4]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Task:** Predict the measurement output of an isQ circuit.
    *   **Input:** isQ code with a Hadamard (H), a Z-rotation (Rz), and a chain of CNOTs on 5 qubits.
    *   **Format Constraints:** Output ONLY the analysis starting with "## Circuit Analysis". Do NOT include isQ code blocks. Concise (3-15 lines). End with the predicted probability distribution. Use Dirac notation.

2.  **Analyze the Circuit:**
    *   Initial state: $|0\rangle^{\otimes 5} = |00000\rangle$
    *   `H(q[0])`: Puts $q_0$ into $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$. State is $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes |0000\rangle = \frac{1}{\sqrt{2}}(|00000\rangle + |10000\rangle)$.
    *   `Rz(3.14159265358979 * 2.0 / 4.0, q[0])`:
        *   $3.14159265358979 \approx \pi$.
        *   Angle $\theta = \pi \times \frac{2.0}{4.0} = \frac{\pi}{2}$.
        *   Gate $R_z(\pi/2)$ acts on $|0\rangle$ as $e^{-i\pi/4}|0\rangle$ and on $|1\rangle$ as $e^{i\pi/4}|1\rangle$.
        *   $R_z(\pi/2) |+\rangle = R_z(\pi/2) \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) = \frac{1}{\sqrt{2}}(e^{-i\pi/4}|0\rangle + e^{i\pi/4}|1\rangle) = e^{-i\pi/4} \frac{1}{\sqrt{2}}(|0\rangle + e^{i\pi/2}|1\rangle) = e^{-i\pi/4} \frac{1}{\sqrt{2}}(|0\rangle + i|1\rangle) = e^{-i\pi/4} |i+\rangle$ (where $|i+\rangle$ is the $|R\rangle$ eigenstate of the Y gate).
        *   Since global phase is irrelevant in measurement, we can consider the state as $\frac{1}{\sqrt{2}}(|0\rangle + i|1\rangle) \otimes |0000\rangle = \frac{1}{\sqrt{2}}(|00000\rangle + i|10000\rangle)$.
    *   `CNOT(q[0], q[1])`: Entangles $q_0$ and $q_1$. State becomes $\frac{1}{\sqrt{2}}(|00000\rangle + i|11000\rangle)$.
    *   `CNOT(q[1], q[2])`: Entangles $q_1$ and $q_2$. State becomes $\frac{1}{\sqrt{2}}(|00000\rangle + i|11100\rangle)$.
    *   `CNOT(q[2], q[3])`: Entangles $q_2$ and $q_3$. State becomes $\frac{1}{\sqrt{2}}(|00000\rangle + i|11110\rangle)$.
    *   `CNOT(q[3], q[4])`: Entangles $q_3$ and $q_4$. State becomes $\frac{1}{\sqrt{2}}(|00000\rangle + i|11111\rangle)$.
    *   Notice that the relative phase $i$ (or $e^{i\pi/2}$) does not affect the measurement probabilities in the computational basis.

3.  **Determine Probabilities:**
    *   Final state: $\frac{1}{\sqrt{2}}(|00000\rangle + i|11111\rangle)$.
    *   Probability of measuring $|00000\rangle$ is $|\frac{1}{\sqrt{2}}|^2 = 0.5$.
    *   Probability of measuring $|11111\rangle$ is $|i\frac{1}{\sqrt{2}}|^2 = 0.5$.
    *   Bitstring notation: earlier measured qubit = higher bit. The measurement order is q[0], q[1],

### Reference answer

Dominant output states: |00000>, |11111> with probability ~0.50 each
