# ISQ training COT RAG corpus: state_preparation shard 40

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/636

- task_id: `isqTrain/636`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3206`

### Prompt

Code this in isQ: implements the state_preparation pattern but with a different initial state preparation (flip q[[0]] -> q[2]).

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Write reasoning for an isQ program generating specific probabilities.
    *   Goal: Explain the circuit's purpose, qubit count/measured, step-by-step state evolution (Dirac notation), and probability justification.
    *   Constraint: "flip q[[0]] -> q[2]" compared to reference.
    *   Reference Code:
        *   `Ry(1.910633236, q[0]);` -> Roughly `2 * asin(1/sqrt(3))` or `arccos(1/3)` related rotation. Let's check: `cos(1.9106/2) ~ sin(1.9106/2) ~ 0.816 -> 1/sqrt(3)? No, sin(1.9106/2) ~ sin(0.955) ~ 0.816`. `0.816^2 = 0.666`. Wait. `cos(pi/4) = sin(pi/4) = 0.707`. `1.910633236` rad is ~109.47 degrees. `cos(109.47/2) = cos(54.7) ~ 0.577 = 1/sqrt(3)`.
        *   Wait, `Ry(theta)|0> = cos(theta/2)|0> + sin(theta/2)|1>`.
        *   If `theta = 1.910633236`, `theta/2 = 0.955316618`.
        *   `cos(0.955316618)^2 = 0.33333`, `sin(0.955316618)^2 = 0.66666`.
        *   So `Ry(1.910633236, q[0])` prepares `(1/sqrt(3))|0> + sqrt(2/3)|1>`. Let's verify expected probs: |001>, |100>, |111> all have 1/3.
    *   Circuit Transformation:
        *   `ctrl H(q[0], q[1]);`
        *   `CNOT(q[1], q[2]);`
        *   `CNOT(q[0], q[1]);`
        *   `X(q[2]);`
    *   The prompt asks to "flip q[[0]] -> q[2]". This means change `X(q[2])` to `X(q[0])`? Or maybe the prompt implies the *new* code will have `X(q[0])` instead of `X(q[2])`.
    *   Let's trace the state evolution with `X(q[0])` at the end to see if it matches expected probabilities, or I just write the reasoning for the reference circuit and adapt the final X gate. The prompt says: "Write an isQ program that implements the state_preparation pattern but with a different initial state preparation (flip q[[0]] -> q[2])."
    *   Wait! Look at the prompt: "Write an isQ program..." then "Generate a reasoning section...". I am ONLY generating the reasoning section for the `isQ` program.
    *   Actually, the prompt says "circuit implementation (isQ code):" and provides the code WITH `X(q[2])`.
    *   Let's read the prompt carefully: "Write an isQ program that implements the state_preparation pattern but with a different initial state preparation (flip q[[0]] -> q[2]). circuit implementation... Expected measurement probabilities: {|001>: 0.333..., |100>: 0.333..., |111>: 0.333...}".
    *   Wait, the probabilities are for `|001>`, `|100>`, `|111>`.
    *   Let's trace the reference code EXACTLY to see if it produces these probs:
        1. `|000>`
        2. `Ry` on q[0]: `(1/sqrt(3))|000> + sqrt(2/3)|100>`
        3. `ctrl H(q[0], q[1])`: `(1/sqrt(3))|000> + sqrt(2/3) |1+0>` = `(1/sqrt(3))|000> + sqrt(2/3)*1/sqrt(2)*(|100> + |110>)` = `(1/sqrt(3))|000> + (1/sqrt(3))|100> + (1/sqrt(3))|110>`.
        4. `CNOT(q[1], q[2])`: `(1/sqrt(3))|000> + (1/sqrt(3))

## isqTrain/3751

- task_id: `isqTrain/3751`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4747`

### Prompt

Implement the following in isQ: an entangled 2-qubit state by applying Ry(1.000) to q[0] followed by CNOT(q[0], q[1]). This creates cos(θ/2)|00> + sin(θ/2)|11>. Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Create an entangled 2-qubit state via Ry rotation and CNOT, producing cos(θ/2)|00> + sin(θ/2)|11>, then measure both qubits.

**Qubits:** 2 qubits (q[0], q[1]), both measured.

**State evolution:**
1. Initial: |00>
2. Ry(1.000, q[0]): rotates |0> → cos(0.5)|0> + sin(0.5)|1>, giving cos(0.5)|00> + sin(0.5)|10>
3. CNOT(q[0], q[1]): flips q[1] when q[0]=|1>, yielding cos(0.5)|00> + sin(0.5)|11>

**Probabilities:** P(|00>) = cos²(0.5) ≈ 0.770151, P(|11>) = sin²(0.5) ≈ 0.229849. No |01> or |10> components remain—perfect correlation between qubits.

## isqTrain/566

- task_id: `isqTrain/566`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `4119`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
qbit q[5];

procedure main() {
    X(q[2]);
    X(q[3]);
    M(q);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes 5 qubits in the ground state: |00000>.
2. The `X(q[2])` gate flips the 3rd qubit (index 2) from |0> to |1>, changing the state to |00100>.
3. The `X(q[3])` gate flips the 4th qubit (index 3) from |0> to |1>, changing the state to |01100>.
4. The `M(q)` instruction measures all qubits in the computational basis. Since the system is in a pure computational basis state, it will be measured with absolute certainty.

Predicted probability distribution: {|01100>: 1.0}

### Reference answer

{'predicted_probs': {'12': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/185. Dimension: predict probabilities for reference circuit.'}

## isqTrain/4804

- task_id: `isqTrain/4804`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_switch`, `isq_syntax_classical_vars`, `mid_circuit_measurement`
- source: `isq_train_cot`
- dataset_index: `2551`

### Prompt

Write isQ code for the following quantum task: demonstrating switch-case fall-through in isQ. Declare 2 global qubits. Measure q[0] (initially |0>) into x. Use switch(x): case 0 applies X(q[1]), case 1 applies H(q[1]). Due to fall-through from case 0 to case 1, both X and H are applied. X|0>=|1>, then H|1>=(|0>-|1>)/sqrt(2). Measure both qubits. Expected: q[0]=0, q[1] in superposition with equal probabilities.

### Chain-of-thought reasoning

## Reasoning
Goal: Demonstrate isQ's switch-case fall-through by applying both X and H to q[1] when q[0] measures as 0.
Two qubits used (q[0], q[1]), both measured.
State evolution: Initial state |00>. Measuring q[0] yields x=0 (deterministic since q[0]=|0>). 
Switch fall-through: case 0 applies X(q[1]) → |0>→|1>, then case 1 applies H(q[1]) → |1>→(|0>-|1>)/√2.
Final state: |0>⊗(|0>-|1>)/√2.
Expected probabilities: P(00)=|1/√2|²=0.5, P(01)=|-1/√2|²=0.5.

## isqTrain/1446

- task_id: `isqTrain/1446`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `1459`

### Prompt

I need an isQ program to Prepare the computational basis state |0100> on 4 qubits by applying X gates to the appropriate qubits, then measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare the 4-qubit computational basis state |0100> from the initial |0000> state.
2. **Qubits**: 4 qubits (q[0], q[1], q[2], q[3]), all measured at the end.
3. **State evolution**:
   - Initial state: |0000>
   - Apply X(q[1]): flips q[1] from |0> to |1>, resulting in |0100>
4. **Measurement outcome**: The final state |0100> is a computational basis state, so measurement yields bitstring 0100 with probability 1.0.

## isqTrain/4220

- task_id: `isqTrain/4220`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `1364`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
qbit q[2];

procedure main() {
    Ry(0.0, q[0]);
    Ry(1.5, q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes two qubits, q[0] and q[1], to the state |00⟩.
2. The gate `Ry(0.0, q[0])` applies an identity rotation, leaving q[0] in the state |0⟩.
3. The gate `Ry(1.5, q[1])` rotates q[1] by 1.5 radians around the Y-axis: Ry(θ)|0⟩ = cos(θ/2)|0⟩ + sin(θ/2)|1⟩.
4. The joint state evolves to |0⟩ ⊗ (cos(0.75)|0⟩ + sin(0.75)|1⟩) = cos(0.75)|00⟩ + sin(0.75)|01⟩.
5. Measuring both qubits will collapse the state to either |00⟩ or |01⟩ since q[0] is strictly |0⟩.

**Predicted probability distribution:**
- **00**: ~53.5% (cos²(0.75))
- **01**: ~46.5% (sin²(0.75))
- 10: 0%
- 11: 0%

### Reference answer

Dominant output states: |00> with probability ~0.54 each

## isqTrain/1797

- task_id: `isqTrain/1797`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `1964`

### Prompt

Implement a quantum circuit in isQ: Apply H to even-indexed qubits and X to odd-indexed qubits on 4 qubits. Measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply H to even-indexed qubits and X to odd-indexed qubits across 4 qubits, then measure all.
2. **Qubits**: 4 qubits (q[0] to q[3]), all measured at the end.
3. **State evolution**:
   - Initial: |0000⟩
   - H(q[0]): (|0⟩+|1⟩)/√₂ ⊗ |000⟩ = (|0000⟩+|1000⟩)/√₂
   - X(q[1]): (|0100⟩+|1100⟩)/√₂
   - H(q[2]): (|0100⟩+|0110⟩+|1100⟩+|1110⟩)/2
   - X(q[3]): (|0101⟩+|0111⟩+|1101⟩+|1111⟩)/2
4. **Probabilities**: Each of the 4 basis states {|0101⟩, |0111⟩, |1101⟩, |1111⟩} has equal probability 1/4. Odd-indexed qubits (1,3) are always |1⟩ due to X; even-indexed qubits (0,2) are in |+⟩ superposition due to H.

## isqTrain/3389

- task_id: `isqTrain/3389`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `5582`

### Prompt

实现以下量子计算任务（使用isQ）：an isQ program: in a 3-qubit register, apply X then H to q[2] only. Other qubits stay |0>. Measure all.

### Chain-of-thought reasoning

## Reasoning
Goal: Prepare the |-> state on q[2] while leaving q[0] and q[1] in the |0> state, then measure all qubits.
Qubits: A 3-qubit register is required, and all three are measured.
Evolution:
- Initial state: |000>
- Apply X to q[2]: Flips q[2] to |1>, resulting in |001>.
- Apply H to q[2]: Transforms |1> to |-> = (|0> - |1>)/√2, resulting in the state (|000> - |001>)/√2.
Probabilities: The final state has absolute amplitude squared of |1/√2|² = 0.5 for both |000> and |001>, yielding a 50% chance for each outcome.<|user|>

## isqTrain/1987

- task_id: `isqTrain/1987`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `multi_controlled_logic`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4602`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[3];
procedure main() {
    Ry(1.910633236, q[0]);
    ctrl H(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[0], q[1]);
    X(q[0]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Input: isQ program applying `Ry`, `ctrl H`, `CNOT`, `CNOT`, and `X` to 3 qubits.
    *   Task: Provide step-by-step reasoning using Dirac notation, predict probability distribution.
    *   Constraint: Concise (3-15 lines), specific format starting with "## Circuit Analysis", no code blocks, end with probabilities.
    *   predicted output format matches the given examples (probability distribution at the end).

2.  **Circuit Breakdown & State Evolution:**
    *   Initial state: $|000\rangle$
    *   `Ry(1.910633236, q[0])`:
        *   $1.910633236 \approx 1.91 \approx \pi/2 \times 1.215 \approx$ wait, let's look closer. $1.9106 \approx 1.21 \times \pi/2$. Let's calculate exact cos/sin.
        *   Wait, let's calculate $R_y(\theta) |0\rangle = \cos(\theta/2) |0\rangle + \sin(\theta/2) |1\rangle$.
        *   $\theta/2 = 1.910633236 / 2 = 0.955316618 \approx \pi/2 - 0.0155$.
        *   Actually, maybe it's $R_y(1.9106) \approx \sqrt{1/3}|0\rangle + \sqrt{2/3}|1\rangle$? Let's check: $\arccos(\sqrt{1/3}) \approx 0.9553$, so $2 \times 0.9553 = 1.9106$. Yes! $\cos(\theta/2) = \sqrt{1/3}$, $\sin(\theta/2) = \sqrt{2/3}$.
        *   State: $\sqrt{1/3}|000\rangle + \sqrt{2/3}|100\rangle$.
    *   `ctrl H(q[0], q[1])`:
        *   If $q_0=|0\rangle$, no op. If $q_0=|1\rangle$, $H$ on $q_1$.
        *   State: $\sqrt{1/3}|000\rangle + \sqrt{2/3} (|10\rangle \to \frac{1}{\sqrt{2}}(|10\rangle + |11\rangle)) = \sqrt{1/3}|000\rangle + \frac{\sqrt{2}}{\sqrt{3}}\frac{1}{\sqrt{2}}(|100\rangle + |110\rangle) = \sqrt{1/3}|000\rangle + \frac{1}{\sqrt{3}}|100\rangle + \frac{1}{\sqrt{3}}|110\rangle$.
    *   `CNOT(q[1], q[2])`:
        *   $q_2 \oplus q_1$.
        *   $|000\rangle \to |000\rangle$
        *   $|100\rangle \to |100\rangle$
        *   $|110\rangle \to |111\rangle$
        *   State: $\sqrt{1/3}|000\rangle + \frac{1}{\sqrt{3}}|100\rangle + \frac{1}{\sqrt{3}}|111\rangle$.
    *   `CNOT(q[0], q[1])`:
        *   $q_1 \oplus q_0$.
        *   $|000\rangle \to |000\rangle$
        *   $|100\rangle \to |110\rangle$
        *   $|111\rangle \to |101\rangle$
        *   State: $\sqrt{1/3}|000\rangle + \frac{1}{\sqrt{3}}|110\rangle + \frac{1}{\sqrt{3}}|101\rangle$.
    *   `X(q[0])`:
        *   Flips $q_0$.
        *   $|000\rangle \to |100\rangle$
        *   $|110\rangle \to |010\rangle$
        *   $|101\rangle \to |001\rangle$
        *   State: $\sqrt{1/3}|100\rangle + \frac{1}{\sqrt{3}}|010\rangle + \frac{1}{\sqrt{3}}|001\rangle$.
    *   Measurements: `M(q[0])`,

### Reference answer

{'predicted_probs': {'001': 0.3333, '010': 0.3333, '100': 0.3333}, 'explanation': 'Expected probabilities: [0.0, 0.33333333327463904, 0.33333333327463904, 0.0, 0.3333333334507219, 0.0, 0.0, 0.0]'}

## isqTrain/4209

- task_id: `isqTrain/4209`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5331`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[4];

procedure main() {
    H(q[0]);
    Rz(3.14159265358979 * 4.0 / 4.0, q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the circuit:**
    *   Initialization: 4 qubits, all in $|0\rangle$. State is $|0000\rangle$.
    *   Gate 1: $H(q[0])$.
        *   State of $q[0]$ becomes $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
        *   Combined state: $\frac{1}{\sqrt{2}}(|0000\rangle + |1000\rangle)$.
    *   Gate 2: $Rz(3.14159265358979 * 4.0 / 4.0, q[0])$.
        *   $3.14159265358979 \approx \pi$. $\pi * 4.0 / 4.0 = \pi$.
        *   $Rz(\pi) = Z$. (Actually, $Rz(\theta) = e^{-i\theta/2}|0\rangle\langle0| + e^{i\theta/2}|1\rangle\langle1|$).
        *   Applying $Rz(\pi)$ to $|+\rangle$: $Rz(\pi) \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) = \frac{1}{\sqrt{2}}(e^{-i\pi/2}|0\rangle + e^{i\pi/2}|1\rangle) = \frac{1}{\sqrt{2}}(-i|0\rangle + i|1\rangle) = i \frac{1}{\sqrt{2}}(|1\rangle - |0\rangle) = -i |-\rangle$ (up to global phase).
        *   Wait, is it $Rz(\theta)$ matrix or applying $e^{-i\theta Z/2}$? Yes.
        *   Let's just say $H$ then $Rz(\pi)$ is equivalent to $H$ then $Z$, which gives $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
        *   State becomes $\frac{1}{\sqrt{2}}(|0000\rangle - |1000\rangle)$.
    *   Gate 3: $CNOT(q[0], q[1])$.
        *   State becomes $\frac{1}{\sqrt{2}}(|0000\rangle - |1100\rangle)$.
    *   Gate 4: $CNOT(q[1], q[2])$.
        *   State becomes $\frac{1}{\sqrt{2}}(|0000\rangle - |1110\rangle)$.
    *   Gate 5: $CNOT(q[2], q[3])$.
        *   State becomes $\frac{1}{\sqrt{2}}(|0000\rangle - |1111\rangle) = \frac{1}{\sqrt{2}}(|0\rangle^{\otimes 4} - |1\rangle^{\otimes 4})$. This is the GHZ state.
    *   Measurements: $M(q[0])$, $M(q[1])$, $M(q[2])$, $M(q[3])$.

2.  **Evaluate Probabilities:**
    *   $|\psi\rangle = \frac{1}{\sqrt{2}}|0000\rangle - \frac{1}{\sqrt{2}}|1111\rangle$.
    *   Measuring $|0000\rangle$: $|1/\sqrt{2}|^2 = 0.5 = 50\%$.
    *   Measuring $|1111\rangle$: $|-1/\sqrt{2}|^2 = 0.5 = 50\%$.
    *   All other states have 0 probability.

3.  **Format the output:**
    *   Start with "## Circuit Analysis".
    *   List operations.
    *   Step-by-step state evolution using Dirac notation.
    *   Predicted probability distribution.

4.  **Drafting the text:**
    *   State starts at $|0000\rangle$.
    *   $H(q[0])$ creates $\frac{1}{\sqrt{2}}(|0000\rangle + |1000\rangle)$.
    *   $Rz(\pi)$ on $q[0]$ applies a phase of $-1$ to the $|1\rangle$ component (yielding $|-\rangle$ for $q[0]$), resulting in $\frac{1}{\sqrt{2}}(|0000\rangle - |1000\rangle)$.
    *

### Reference answer

Dominant output states: |0000>, |1111> with probability ~0.50 each
