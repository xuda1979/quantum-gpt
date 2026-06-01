# ISQ training COT RAG corpus: state_preparation shard 32

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1546

- task_id: `isqTrain/1546`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `4268`

### Prompt

Create an isQ quantum circuit that Apply X gate to each of 5 qubits and measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply an X gate to each of 5 qubits and measure all, flipping every qubit from |0⟩ to |1⟩.
2. **Qubits**: 5 qubits (q[0]–q[4]), all measured.
3. **Evolution**:
   - Start in |00000⟩.
   - X(q[0]) through X(q[4]) each flip |0⟩→|1⟩, yielding |11111⟩.
4. **Measurement**: The final state |11111⟩ gives outcome 11111 (decimal 31) with probability 1.0.

## isqTrain/3215

- task_id: `isqTrain/3215`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5773`

### Prompt

实现以下量子计算任务（使用isQ）：an isQ program: apply Rx(1*pi/4) then Ry(1*pi/4) to a qubit and measure.

### Chain-of-thought reasoning

The user wants a reasoning section for an isQ quantum program.
The program applies $R_x(1*\pi/4)$ followed by $R_y(1*\pi/4)$ to a single qubit and measures it.
Let's trace the state evolution:
1. Start in $|0\rangle$
2. Apply $R_x(\pi/4)$: The state becomes $\cos(\pi/8)|0\rangle - i\sin(\pi/8)|1\rangle$
3. Apply $R_y(\pi/4)$: $R_y(\theta) = \cos(\theta/2)I - i\sin(\theta/2)Y$.
So $R_y(\pi/4)|\psi\rangle = \cos(\pi/8)|\psi\rangle - i\sin(\pi/8)Y|\psi\rangle$
$= \cos(\pi/8)(\cos(\pi/8)|0\rangle - i\sin(\pi/8)|1\rangle) - i\sin(\pi/8)(i\cos(\pi/8)|1\rangle + \sin(\pi/8)|0\rangle)$
$= (\cos^2(\pi/8) - i\sin^2(\pi/8))|0\rangle + (-i\cos(\pi/8)\sin(\pi/8) + \cos(\pi/8)\sin(\pi/8))|1\rangle$? Wait, let's be more precise.
$R_y(\theta) = \begin{pmatrix} \cos(\theta/2) & -\sin(\theta/2) \\ \sin(\theta/2) & \cos(\theta/2) \end{pmatrix}$.
Initial state $|0\rangle = \begin{pmatrix} 1 \\ 0 \end{pmatrix}$.
After $R_x(\pi/4)$:
$R_x(\theta) = \begin{pmatrix} \cos(\theta/2) & -i\sin(\theta/2) \\ -i\sin(\theta/2) & \cos(\theta/2) \end{pmatrix}$.
State is $\begin{pmatrix} \cos(\pi/8) \\ -i\sin(\pi/8) \end{pmatrix}$.

Apply $R_y(\pi/4)$:
$\begin{pmatrix} \cos(\pi/8) & -\sin(\pi/8) \\ \sin(\pi/8) & \cos(\pi/8) \end{pmatrix} \begin{pmatrix} \cos(\pi/8) \\ -i\sin(\pi/8) \end{pmatrix}$
$= \begin{pmatrix} \cos^2(\pi/8) + i\sin^2(\pi/8) \\ \sin(\pi/8)\cos(\pi/8) - i\cos(\pi/8)\sin(\pi/8) \end{pmatrix}$
$= \begin{pmatrix} \frac{1+\cos(\pi/4)}{2} + i\frac{1-\cos(\pi/4)}{2} \\ \frac{\sin(\pi/4)}{2} (1 - i) \end{pmatrix}$
$= \begin{pmatrix} \frac{1}{2} + \frac{1}{2\sqrt{2}} + i(\frac{1}{2} - \frac{1}{2\sqrt{2}}) \\ \frac{1}{2\sqrt{2}}(1 - i) \end{pmatrix}$

Probability of $|0\rangle$:
$|\frac{1}{2} + \frac{\sqrt{2}}{4} + i(\frac{1}{2} - \frac{\sqrt{2}}{4})|^2 = (\frac{1}{2} + \frac{\sqrt{2}}{4})^2 + (\frac{1}{2} - \frac{\sqrt{2}}{4})^2 = \frac{1}{4} + \frac{2}{16} + \frac{1}{4} + \frac{2}{16} = \frac{1}{2} + \frac{1}{4} = 0.75$.

Wait! $R_x(\theta) |0\rangle = \cos(\theta/2)|0\rangle - i\sin(\theta/2)|1\rangle$.
Wait, let me double check The implementation expected probabilities: {|0>: 0.75, |1>: 0.25}. Yes, exactly!
Let's write out the reasoning steps.
- Goal: Apply Rx(pi/4) then Ry(pi/4) to a qubit and measure.
- Needs

## isqTrain/424

- task_id: `isqTrain/424`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `5485`

### Prompt

请用isQ语言编写一个量子电路：implements the state_preparation pattern with modified rotation parameters (pi4_to_pi6). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare a single-qubit state via Ry rotation with angle π/6, producing cos(π/12)|0⟩ + sin(π/12)|1⟩.
2. **Qubits**: 1 qubit (q[0]), which is measured.
3. **State evolution**: |0⟩ → Ry(π/6) → cos(π/12)|0⟩ + sin(π/12)|1⟩.
4. **Probabilities**: P(|0⟩) = cos²(π/12) ≈ 0.9330, P(|1⟩) = sin²(π/12) ≈ 0.0670, matching the predicted output.

## isqTrain/4211

- task_id: `isqTrain/4211`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3394`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[5];

procedure main() {
    H(q[0]);
    Rz(3.14159265358979 * 1.0 / 4.0, q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
    CNOT(q[3], q[4]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]); M(q[4]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis

1. **Operations applied**:
   - H on q[0]: creates superposition
   - Rz(π/4) on q[0]: applies phase rotation
   - CNOT(q[0],q[1]) → CNOT(q[1],q[2]) → CNOT(q[2],q[3]) → CNOT(q[3],q[4]): cascade of entanglement

2. **State evolution**:
   - Initial: |00000⟩
   - After H(q[0]): (|0⟩ + |1⟩)/√2 ⊗ |0000⟩ = (|00000⟩ + |10000⟩)/√2
   - After Rz(π/4) on q[0]: (|00000⟩ + e^(iπ/4)|10000⟩)/√2
   - After CNOT cascade: (|00000⟩ + e^(iπ/4)|11111⟩)/√2

3. **Final state**: A GHZ-like state (|00000⟩ + e^(iπ/4)|11111⟩)/√2 — an equal superposition of all-zeros and all-ones with a relative phase.

4. **Predicted probability distribution**:
   - P(00000) = 50%
   - P(11111) = 50%
   
   Both outcomes are equally likely. The most likely measurement outcomes are **00000** and **11111**, each with probability 0.5.

### Reference answer

Dominant output states: |00000>, |11111> with probability ~0.50 each

## isqTrain/3950

- task_id: `isqTrain/3950`
- task_type: `bug_fix`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3320`

### Prompt

There's an error in this quantum circuit implementation. Fix it:

```
import std;
// Entangled 2-qubit state via Ry(0.785) + CNOT
qbit q[2];

procedure main() {
    // Create entangled state
    Ry(0.785, q[0]);
    // BUG: missing gate here
    // Measure
    M(q[0]); M(q[1]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis

**1. What the bug is:**
The code is missing a CNOT gate after the `Ry(0.785, q[0])` operation. The comment indicates the circuit should create an entangled state via "Ry(0.785) + CNOT", but the CNOT is absent, leaving the qubits unentangled.

**2. What the fix is:**
Add `CNOT(q[0], q[1]);` between the `Ry` rotation and the measurements to create the intended entanglement.

**3. State evolution of corrected circuit:**
- Initial: |00⟩
- After `Ry(0.785, q[0])`: cos(0.3925)|00⟩ + sin(0.3925)|10⟩ ≈ 0.9239|00⟩ + 0.3827|10⟩
- After `CNOT(q[0], q[1])`: 0.9239|00⟩ + 0.3827|11⟩ (entangled Bell-like state)
- Measurement: P(|00⟩) = 0.9239² ≈ 0.8537, P(|11⟩) = 0.3827² ≈ 0.1463 ✓

## isqTrain/423

- task_id: `isqTrain/423`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `5602`

### Prompt

Implement a quantum circuit in isQ: implements the state_preparation pattern with modified rotation parameters (pi4_to_pi3). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Prepare a single-qubit state using Ry rotation with angle π/3 (modified from π/4).

2. **Qubits**: 1 qubit (q[0]) is allocated and measured.

3. **State evolution**:
   - Initial: |0⟩
   - After Ry(π/3, q[0]): cos(π/6)|0⟩ + sin(π/6)|1⟩ = (√3/2)|0⟩ + (1/2)|1⟩

4. **Measurement probabilities**: P(|0⟩) = cos²(π/6) = 3/4 = 0.75, P(|1⟩) = sin²(π/6) = 1/4 = 0.25, matching predicted output.

## isqTrain/1790

- task_id: `isqTrain/1790`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3055`

### Prompt

I need an isQ program to a CZ ring on 4 qubits (all in |+>): apply CZ between each consecutive pair and between last and first.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Create a 4-qubit CZ ring (cycle graph) with all qubits in |+⟩, entangling each consecutive pair and wrapping around.

**Qubits:** 4 qubits q[0..3], all measured.

**State evolution:**
1. Start: |0000⟩
2. H on all qubits: |+⟩⊗⁴ = (1/4)Σ_{x∈{0,1}⁴} |x⟩
3. CZ ring applies phase (-1)^(x₀x₁+x₁x₂+x₂x₃+x₃x₀) to each |x₀x₁x₂x₃⟩
4. This creates the graph state |G⟩ = (1/4

## isqTrain/3735

- task_id: `isqTrain/3735`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4421`

### Prompt

Help me write isQ code that Prepare the 4-qubit GHZ state with phase pi:
|GHZ> = (|0000> + e^{i*pi}|1111>) / sqrt(2)
Use Hadamard on first qubit, Rz for phase, then CNOT chain. Measure all 4 qubits.

### Chain-of-thought reasoning

This is a straightforward circuit for preparing a 4-qubit GHZ state with a phase of pi.

The task requires me to generate only the reasoning section explaining the circuit.

1. Goal: Create 4-qubit GHZ state with phase π
2. Qubits: 4 qubits, all measured
3. State evolution:
   - Start: |0000⟩
   - H(q[0]): (|0⟩ + |1⟩)/√2 ⊗ |000⟩ = (|0000⟩ + |1000⟩)/√2
   - Rz(π, q[0]): Rz(π) applies phase e^{-iπ/2} to |0⟩ and e^{iπ/2} to |1⟩, but wait...

Let me reconsider Rz(π) more carefully.

Rz(θ) = [[e^{-iθ/2}, 0], [0, e^{iθ/2}]]

So Rz(π) = [[e^{-iπ/2}, 0], [0, e^{iπ/2}]] = [[-i, 0], [0, i]] = e^{-iπ/2} [[1, 0], [0, -1]] * (-1)... 

Actually, Rz(π) = [[e^{-iπ/2}, 0], [0, e^{iπ/2}]] = [[-i, 0], [0, i]]

This applies a relative phase of -1 to |1⟩ compared to |0⟩ (up to global phase).

After H(q[0]): (|0000⟩ + |1000⟩)/√2

After Rz(π, q[0]): The |0⟩ component gets multiplied by e^{-iπ/2} = -i, and |1⟩ component by e^{iπ/2} = i. So we get:
(-i|0000⟩ + i|1000⟩)/√2 = i(-|0000⟩ + |1000⟩)/√2

Hmm, that doesn't give us the right phase.

Wait, let me reconsider. The target state is (|0000⟩ + e^{iπ}|1111⟩)/√2 = (|0000⟩ - |1111⟩)/√2.

After H(q[0]): (|0000⟩ + |1000⟩)/√2
After CNOT chain: (|0000⟩ + |1111⟩)/√2

We need to add a phase of -1 to the |1111⟩ component. 

Rz(π) on q[0] gives Rz(π) = [[e^{-iπ/2}, 0], [0, e^{iπ/2}]] = [[-i, 0], [0, i]]

After H on q[0], state is (|0⟩ + |1⟩)/√2 ⊗ |000⟩

Rz(π) on q[0]: (e^{-iπ/2}|0⟩ + e^{iπ/2}|1⟩)/√2 ⊗ |000⟩ = (-i|0⟩ + i|1⟩)/√2 ⊗ |000⟩ = i(-|0⟩ + |1⟩)/√2 ⊗ |000⟩

Hmm, that gives us (−|0000⟩ + |1111⟩)/√2 after the CNOT chain (with global phase i).

But we want (|0000⟩ − |1111⟩)/√2... which is just a global phase difference of -1.

Actually (−|0000⟩ + |1111⟩)/√2 = −(|0000⟩ − |1111⟩)/√2, which is the same state up to global phase.

And (|0000⟩ − |1111⟩)/√2 = (|0000⟩ + e^{iπ}|1111⟩)/√2 ✓

So it works! The relative phase between |0000⟩ and |1111⟩ is -1 = e^{iπ}.

Wait, let me recompute more carefully.

After H(q[0]): (|0⟩ + |1⟩)/√2 on q[0], rest still |000⟩.
State: (|0000⟩ + |1000⟩)/√2

After Rz(π, q[0]):
Rz(π) = [[e^{-iπ/2}, 0], [0, e^{iπ/2}]] = [[-i, 0], [0, i]]

Applied to the first qubit:
|0000⟩ → e^{-iπ/2}|0000⟩ = -i|0000⟩
|1000⟩ → e^{iπ/2}|1000⟩ = i|1000⟩

State: (-i|0000⟩ + i|100

## isqTrain/4208

- task_id: `isqTrain/4208`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4677`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
qbit q[4];

procedure main() {
    H(q[0]);
    Rz(3.14159265358979 * 2.0 / 4.0, q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict measurement output of given isQ circuit.
    *   Format: Step-by-step reasoning using Dirac notation. Concise (3-15 lines).
    *   Start with "## Circuit Analysis", end with probability distribution.
    *   Circuit:
        

2.  **Analyze the Circuit:**
    *   Initial state: $|0000\rangle$
    *   Apply `H(q[0])`: State becomes $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes |000\rangle = \frac{1}{\sqrt{2}}(|0000\rangle + |1000\rangle)$
    *   Apply `Rz(pi/2, q[0])`: The gate $R_z(\theta) = \begin{pmatrix} 1 & 0 \\ 0 & e^{-i\theta} \end{pmatrix}$. Wait, isQ uses $R_z(\theta) = e^{-i\theta Z/2}$. Let me check standard $R_z$ matrix: $\begin{pmatrix} e^{-i\theta/2} & 0 \\ 0 & e^{i\theta/2} \end{pmatrix}$. The prompt defines standard $R_z$ behavior.
        *   If $\theta = \pi/2$, $R_z(\pi/2) = \begin{pmatrix} e^{-i\pi/4} & 0 \\ 0 & e^{i\pi/4} \end{pmatrix}$.
        *   State: $\frac{1}{\sqrt{2}}(e^{-i\pi/4}|0000\rangle + e^{i\pi/4}|1000\rangle) = \frac{e^{-i\pi/4}}{\sqrt{2}}(|0000\rangle + e^{i\pi/2}|1000\rangle)$.
        *   $e^{i\pi/2} = i$.
        *   So state is proportional to $|0000\rangle + i|1000\rangle$.
        *   Wait, this is the same as applying $S$ gate (up to global phase $e^{-i\pi/4}$). Yes, $S = R_z(\pi/2)$.
    *   Apply `CNOT(q[0], q[1])`: Flips $q_1$ if $q_0=1$. State becomes proportional to $|0000\rangle + i|1100\rangle$.
    *   Apply `CNOT(q[1], q[2])`: Flips $q_2$ if $q_1=1$. State becomes proportional to $|0000\rangle + i|1110\rangle$.
    *   Apply `CNOT(q[2], q[3])`: Flips $q_3$ if $q_2=1$. State becomes proportional to $|0000\rangle + i|1111\rangle$.
    *   Global phase $e^{-i\pi/4}$ doesn't affect measurements.

3.  **Calculate Probabilities:**
    *   State is $\frac{1}{\sqrt{2}}(|0000\rangle + i|1111\rangle)$. (GHZ state with relative phase).
    *   Probability of 0000 is $|1/\sqrt{2}|^2 = 0.5$.
    *   Probability of 1111 is $|i/\sqrt{2}|^2 = 0.5$.
    *   All other states have probability 0.

4.  **Draft the Explanation:**
    *   Start with $|0000\rangle$.
    *   $H(q_0)$ creates $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)|000\rangle$.
    *   $R_z(\pi/2)$ on $q_0$ adds phase, resulting in $\frac{1}{\sqrt{2}}(|0\rangle + i|1\rangle)|000\rangle$.
    *   CNOTs propagate the $|1\rangle$ state: CNOTs yield $\frac{1}{\sqrt{2}}(|0000\rangle

### Reference answer

Dominant output states: |0000>, |1111> with probability ~0.50 each

## isqTrain/592

- task_id: `isqTrain/592`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `17`

### Prompt

Create an isQ quantum circuit that implements a variant of the ghz_state_preparation pattern using q[7] -> q[8]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create an 8-qubit GHZ state (|00000000> + |11111111>)/√2 using sequential entanglement from q[0] through q[7].
2. **Qubits**: 8 qubits declared (q[0] to q[7]), all measured at the end.
3. **State evolution**:
   - Initial state: |00000000>
   - H(q[0]): (|0> + |1>)/√2 ⊗ |0000000> = (|00000000> + |10000000>)/√2
   - CNOT(q[0], q[1]): (|00000000> + |11000000>)/√2
   - CNOT(q[1], q[2]): (|00000000> + |11100000>)/√2
   - CNOT(q[2], q[3]): (|00000000> + |11110000>)/√2
   - CNOT(q[3], q[4]): (|00000000> + |11111000>)/√2
   - CNOT(q[4], q[5]): (|00000000> + |11111100>)/√2
   - CNOT(q[5], q[6]): (|00000000> + |11111110>)/√2
4. **Expected probabilities**: The final superposition yields P(|00000000>) = 0.5 and P(|11111111>) = 0.5, as each basis state has amplitude 1/√2.
