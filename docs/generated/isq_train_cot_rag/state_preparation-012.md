# ISQ training COT RAG corpus: state_preparation shard 12

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1953

- task_id: `isqTrain/1953`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `4204`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[2];
procedure main() {
    H(q[0]);
    X(q[1]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants a step-by-step analysis of an isQ quantum program to predict the measurement probabilities. The output must be concise (3-15 lines), use Dirac notation, and end with the predicted probability distribution.

2.  **Analyze the isQ program**:
    *   `qbit q[2];` -> Initial state is $|00\rangle$.
    *   `H(q[0]);` -> Apply Hadamard to qubit 0. State becomes $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$.
    *   `X(q[1]);` -> Apply X to qubit 1. State becomes $\frac{1}{\sqrt{2}}(|01\rangle + |11\rangle)$.
    *   `CNOT(q[0], q[1]);` -> Apply CNOT with q[0] as control, q[1] as target. This flips q[1] when q[0] is $|1\rangle$.
        *   $|01\rangle \to |01\rangle$
        *   $|11\rangle \to |10\rangle$
        *   New state: $\frac{1}{\sqrt{2}}(|01\rangle + |10\rangle)$.
    *   `M(q[0]); M(q[1]);` -> Measure both qubits.

3.  **Determine Probabilities**:
    *   State is $\frac{1}{\sqrt{2}}(|01\rangle + |10\rangle)$.
    *   Probability of measuring $|01\rangle$ is $|1/\sqrt{2}|^2 = 0.5$.
    *   Probability of measuring $|10\rangle$ is $|1/\sqrt{2}|^2 = 0.5$.
    *   Other states ($|00\rangle, |11\rangle$) have probability 0.
    *   Wait, what is the bitstring ordering for `M(q[0]); M(q[1]);`? The prompt says "earlier measured qubit = higher bit" in the --probs output section.
    *   `M(q[0])` happens first. So q[0] is the higher bit.
    *   `M(q[1])` happens second. So q[1] is the lower bit.
    *   For state $|01\rangle$ (where q[0]=0, q[1]=1): bitstring is `01`.
    *   For state $|10\rangle$ (where q[0]=1, q[1]=0): bitstring is `10`.
    *   predicted output matches the reference: {'01': 0.5, '10': 0.5}.

4.  **Draft the response** (following rules: concise, Dirac notation, starting with "## Circuit Analysis", no isq blocks, ending with probabilities):
    *   *Initial state*: $|00\rangle$
    *   *H(q[0]) and X(q[1])*: $H$ on q[0] yields $(|0\rangle + |1\rangle)/\sqrt{2} \otimes |0\rangle = (|00\rangle + |10\rangle)/\sqrt{2}$. Then $X$ on q[1] yields $(|01\rangle + |11\rangle)/\sqrt{2}$.
    *   *CNOT(q[0], q[1])*: Flips target q[1] when control q[0] is $|1\rangle$. State becomes $(|01\rangle + |10\rangle)/\sqrt{2}$.
    *   *Measurement*: The probabilities are $|\pm 1/\sqrt{2}|^2 = 0.5$.
    *   *Final formatting*: Make it strictly 3-8 lines.

5.  **Refine the draft**:
    ## Circuit Analysis
    - Initial state is $|00\rangle$.
    - Applying `H(q[0])` creates superposition: $(|00\rangle + |10\rangle)/\sqrt{2}$.
    - Applying `X(q[1])` flips the second qubit: $(|01\rangle + |11\rangle)/\sqrt{2}$.
    - The `CNOT(q[0], q[1])` gate flips `q[1]` when `q[0]` is $|1\rangle$, yielding the final Bell state: $(|01\rangle + |10\rangle)/\sqrt{2}$.
    - Measuring both qubits collapses the state to either $|01\rangle$ or $|10\rangle$.
    
    Predicted probability distribution:

### Reference answer

{'predicted_probs': {'01': 0.5, '10': 0.5}, 'explanation': 'Bell state Psi+'}

## isqTrain/1455

- task_id: `isqTrain/1455`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `4651`

### Prompt

实现以下量子计算任务（使用isQ）：Prepare the computational basis state |00001> on 5 qubits by applying X gates to the appropriate qubits, then measure all.

### Chain-of-thought reasoning

## Reasoning
Goal: Prepare the computational basis state |00001> on 5 qubits by flipping the appropriate qubit, then measure all.

We need 5 qubits (q[0] through q[4]), all of which are measured.

Step-by-step state evolution:
1. Initialize all 5 qubits to |0>, giving state |00000>.
2. Apply X gate to q[4]: this flips the 5th qubit from |0> to |1>, resulting in state |00001>.

Expected probabilities: Since the final state is exactly |00001>, measurement yields outcome 00001 with probability 1.0. In the bitstring indexing (earlier measured qubit = higher bit), q[0] is the highest bit and q[4] is the lowest, so the result is 00001 (binary) = 1 (decimal).

## isqTrain/3195

- task_id: `isqTrain/3195`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5443`

### Prompt

I need an isQ program to an isQ program: apply Ry(1*pi/12) to a qubit and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Rotate a single qubit by angle $\pi/12$ around the Y-axis and measure it.
2. **Qubits**: 1 qubit is required, and it is measured.
3. **State evolution**: Starting in $|0\rangle$, applying $R_y(\pi/12)$ yields the state $\cos(\pi/24)|0\rangle + \sin(\pi/24)|1\rangle$.
4. **Probabilities**: The probability of measuring $|0\rangle$ is $\cos^2(\pi/24) \approx 0.983$, and the probability of measuring $|1\rangle$ is $\sin^2(\pi/24) \approx 0.017$.

## isqTrain/3747

- task_id: `isqTrain/3747`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `2809`

### Prompt

Write isQ code for the following quantum task: Prepare a 2-qubit product state by applying Ry(1.0) to q[0] and Ry(1.0) to q[1]. Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Prepare a 2-qubit product state by applying Ry(1.0) to each qubit, then measure both.
2. Two qubits (q[0], q[1]) are needed; both are measured.
3. State evolution:
   - Initial: |00⟩
   - After Ry(1.0) on q[0]: cos(0.5)|0⟩⊗|0⟩ + sin(0.5)|1⟩⊗|0⟩ = 0.8776|00⟩ + 0.4794|10⟩
   - After Ry(1.0) on q[1]: 0.8776(cos(0.5)|0⟩+sin(0.5)|1⟩)⊗|0⟩ ... actually: cos²(0.5)|00⟩ + cos(0.5)sin(0.5)|01⟩ + sin(0.5)cos(0.5)|10⟩ + sin²(0.5)|11⟩
   - = 0.7702|00⟩ + 0.4207|01⟩ + 0.4207|10⟩ + 0.2298|11⟩ ... let me recalculate: cos(0.5)≈0.8776, sin(0.5)≈0.4794
   - Probabilities: P(|00⟩)=cos²(0.5)·cos²(0.5)≈0.5931, P(|01⟩)=cos²(0.5)·sin²(0.5)≈0.1770, P(|10⟩)=sin²(0.5)·cos²(0.5)≈0.1770, P(|11⟩)=sin²(0.5)·sin²(0.5)≈0.0528
4. Expected probabilities match: {|00⟩:0.593, |01⟩:0.177, |10⟩:0.177, |11⟩:0.053}

## isqTrain/4216

- task_id: `isqTrain/4216`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `2443`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;
qbit q[2];

procedure main() {
    Ry(1.0, q[0]);
    Ry(0.0, q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initial State:** The 2-qubit system starts in the basis state $|00\rangle$.
2. **Gate Operations:** 
   - `Ry(1.0, q[0])` applies a Y-rotation of $\theta=1.0$ radian to $q[0]$.
   - `Ry(0.0, q[1])` applies a Y-rotation of 0 radians to $q[1]$, acting as an identity and leaving it in $|0\rangle$.
3. **State Evolution:** After `Ry(1.0)`, $q[0]$ evolves to $\cos(0.5)|0\rangle + \sin(0.5)|1\rangle$. The total quantum state becomes $\cos(0.5)|00\rangle + \sin(0.5)|10\rangle$.
4. **Measurement:** The system is measured in the computational basis.

**Predicted probability distribution:**
- $P(00) = \cos^2(0.5) \approx 77.0\%$
- $P(10) = \sin^2(0.5) \approx 23.0\%$
- $P(01) = 0\%$
- $P(11) = 0\%$
The most likely measurement outcome is `00`.

### Reference answer

Dominant output states: |00> with probability ~0.77 each

## isqTrain/595

- task_id: `isqTrain/595`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `3062`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[7];

procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
    CNOT(q[3], q[4]);
    CNOT(q[4], q[5]);
    CNOT(q[5], q[6]);
    M(q);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Task:** Predict probability distribution of measurement outcomes for a given isQ program.
    *   **Program:** 7 qubits. H on q[0], then a chain of CNOTs (q[0]->q[1], q[1]->q[2], ..., q[5]->q[6]). Measurement of all qubits.
    *   **Output Format:** "## Circuit Analysis" section. 3-8 lines for simple, up to 15 for complex. End with the predicted probability distribution. Dirac notation.
    *   **Constraints:** no code blocks. Output ONLY the analysis starting with "## Circuit Analysis".

2.  **Circuit Analysis (Step-by-Step):**
    *   Initial state: $|0000000\rangle$
    *   `H(q[0])`: Applies Hadamard to qubit 0. State becomes $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes |000000\rangle = \frac{1}{\sqrt{2}}(|0000000\rangle + |1000000\rangle)$.
    *   `CNOT(q[0], q[1])`: Flips q[1] if q[0] is 1. State becomes $\frac{1}{\sqrt{2}}(|0000000\rangle + |1100000\rangle)$.
    *   `CNOT(q[1], q[2])`: Flips q[2] if q[1] is 1. State becomes $\frac{1}{\sqrt{2}}(|0000000\rangle + |1110000\rangle)$.
    *   `CNOT(q[2], q[3])`: Flips q[3] if q[2] is 1. State becomes $\frac{1}{\sqrt{2}}(|0000000\rangle + |1111000\rangle)$.
    *   `CNOT(q[3], q[4])`: Flips q[4] if q[3] is 1. State becomes $\frac{1}{\sqrt{2}}(|0000000\rangle + |1111100\rangle)$.
    *   `CNOT(q[4], q[5])`: Flips q[5] if q[4] is 1. State becomes $\frac{1}{\sqrt{2}}(|0000000\rangle + |1111110\rangle)$.
    *   `CNOT(q[5], q[6])`: Flips q[6] if q[5] is 1. State becomes $\frac{1}{\sqrt{2}}(|0000000\rangle + |1111111\rangle)$. This is the GHZ state.
    *   Measurement: Both $|0000000\rangle$ and $|1111111\rangle$ have an amplitude of $1/\sqrt{2}$. Probability is $|1/\sqrt{2}|^2 = 0.5$.

3.  **Drafting the Response:**
    *   *Start:* ## Circuit Analysis
    *   *Line 1:* Initial state is |0000000>. A Hadamard gate on q[0] creates an equal superposition: (1/√2)(|0000000> + |1000000>).
    *   *Line 2-3:* The sequence of CNOT gates acts as a cascade. CNOT(q[0], q[1]) entangles q[0] and q[1] to form (1/√2)(|0000000> + |1100000>).
    *   *Line 3-4:* Subsequent CNOT gates propagate this entanglement sequentially to q[2], q[3], q[4], q[5], and q[6].
    *   *Line 5:* The final quantum state before measurement is the 7-qubit GHZ state: (1/√2)(|0000000> + |1111111>).
    *   *Line 6 (Conclusion):* Predicted probability distribution: {|0000000>: 0.5, |1111111>: 0.5}

4.  **Refining and Formatting:**
    *   Check length: 7 lines. Perfect.
    *   Check notation: Dirac notation used correctly.
    *   Check constraints: No code blocks. Starts with "## Circuit Analysis".

5.  **Final Polish:**
    ## Circuit Analysis
    1. The circuit initializes 7 qubits to |0000000>. A Hadamard gate on q[0] places it in a superposition, resulting in the state (1/√2)(|0000000> + |

### Reference answer

{'predicted_probs': {'0': 0.5, '127': 0.5}, 'explanation': 'Parametric variant of isqHumanEval/197. Dimension: predict probabilities for reference circuit.'}

## isqTrain/3201

- task_id: `isqTrain/3201`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1920`

### Prompt

Write isQ code for the following quantum task: an isQ program: apply Ry(5*pi/16) to a qubit and measure.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Apply a Y-rotation of angle 5π/16 to a single qubit and measure the resulting state.

**Qubits:** 1 qubit (`q[0]`), which is measured.

**State evolution:**
- Initial state: |0⟩
- Apply Ry(5π/16): Ry(θ)|0⟩ = cos(θ/2)|0⟩ + sin(θ/2)|1⟩
- Final state: cos(5π/32)|0⟩ + sin(5π/32)|1⟩

**Measurement probabilities:** P(|0⟩) = cos²(5π/32) ≈ 0.7778, P(|1⟩) = sin²(5π/32) ≈ 0.2222. These follow directly from the squared amplitudes of the final superposition state.

## isqTrain/4808

- task_id: `isqTrain/4808`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_switch`, `isq_syntax_classical_vars`
- source: `isq_train_cot`
- dataset_index: `2978`

### Prompt

Write isQ code for the following quantum task: using switch with a classical variable. Declare 2 global qubits. Create an integer variable set to 2. Use switch on the variable: case 0 applies X(q[0]), case 1 applies H(q[0]), case 2 applies X(q[0]) then X(q[1]). Since the variable is 2, case 2 runs and both qubits flip. Measure both qubits. Expected: |11>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Demonstrate classical control flow via `switch`, selecting case 2 which applies X gates to both qubits, flipping them from |00⟩ to |11⟩.
2. **Qubits**: 2 global qubits `q[2]`, both measured.
3. **State evolution**:
   - Initialize: |00⟩
   - `sel = 2`, so `switch` executes case 2: `X(q[0])` then `X(q[1])`
   - After `X(q[0])`: |10⟩
   - After `X(q[1])`: |11⟩
4. **Expected probabilities**: The final state is |11⟩ with probability 1.0, since X gates deterministically flip computational basis states.

## isqTrain/2586

- task_id: `isqTrain/2586`
- task_type: `code_equivalence`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `global_phase`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3710`

### Prompt

Determine if these two isQ implementations are functionally equivalent:

Version A:
```isq
import std;

qbit q[1];

procedure main() {
    // |+> state
    H(q[0]);
    M(q[0]); // prob 0.5, 0.5
}

```

Version B:
```isq
import std;

qbit q[1];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    // |+> state
    H(q[0]);
    M(q[0]); // prob 0.5, 0.5
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. Program A applies H to |0⟩, producing |+⟩ = (|0⟩ + |1⟩)/√2, then measures.
2. Program B applies GPhase(0.0) then H to |0⟩, producing |+⟩, then measures.
3. GPhase(0.0) applies a trivial global phase of e^(i·0) = 1, which has no physical effect.
4. Both programs produce identical measurement probabilities: P(|0⟩) = 0.5, P(|1⟩) = 0.5.
5. Equivalent: Yes

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/3196

- task_id: `isqTrain/3196`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3582`

### Prompt

请用isQ语言编写一个量子电路：an isQ program: apply Ry(5*pi/12) to a qubit and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply an Ry rotation of $5\pi/12$ to a single qubit and measure it.
2. **Qubits**: 1 qubit is needed, and it is measured at the end.
3. **Evolution**: Starting in $|0\rangle$, applying `Ry(5*pi/12, q[0])` transforms the state to $\cos(5\pi/24)|0\rangle + \sin(5\pi/24)|1\rangle$.
4. **Probabilities**: The measurement probabilities are the squared amplitudes: $P(|0\rangle) = \cos^2(5\pi/24) \approx 0.6294$ and $P(|1\rangle) = \sin^2(5\pi/24) \approx 0.3706$.
