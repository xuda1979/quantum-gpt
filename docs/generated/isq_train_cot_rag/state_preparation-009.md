# ISQ training COT RAG corpus: state_preparation shard 9

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3230

- task_id: `isqTrain/3230`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `278`

### Prompt

Help me write isQ code that an isQ program: apply Ry(1*pi/4) to q[0] and Ry(1*pi/2) to q[1], then measure both (no entanglement).

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply independent Ry rotations to two qubits and measure both—no entanglement is introduced.
2. **Qubits**: 2 qubits (q[0], q[1]), both measured.
3. **State evolution**:
   - Initial: |00⟩
   - After Ry(π/4) on q[0]: (cos(π/8)|0⟩ + sin(π/8)|1⟩) ⊗ |0⟩
   - After Ry(π/2) on q[1]: (cos(π/8)|0⟩ + sin(π/8)|1⟩) ⊗ (cos(π/4)|0⟩ + sin(π/4)|1⟩)
   - Final: product state with amplitudes determined by cos/sin of π/8 and π/4.
4. **Probabilities**: P(|00⟩) = cos²(π/8)·cos²(π/4) ≈ 0.4268; P(|01⟩) = cos²(π/8)·sin²(π/4) ≈ 0.4268; P(|10⟩) = sin²(π/8)·cos²(π/4) ≈ 0.0732; P(|11⟩) = sin²(π/8)·sin²(π/4) ≈ 0.0732. Since Ry(π/2) gives equal |0⟩/|1⟩ weighting, probabilities split 50/50 between q[1] outcomes, modulated by q[0]'s rotation.

## isqTrain/3298

- task_id: `isqTrain/3298`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_for_loop`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `982`

### Prompt

实现以下量子计算任务（使用isQ）：an isQ program: use a for loop to apply X to all 5 qubits, preparing |11111>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply the X gate to all 5 qubits to prepare the |11111> state.
2. **Qubits**: 5 qubits (`q[0]` to `q[4]`) are allocated, and all 5 are measured.
3. **Evolution**: 
   - Initial state is |00000>.
   - The for loop applies X to each qubit, flipping |0> to |1>.
   - Final state is |11111>.
4. **Probabilities**: Measuring |11111> yields the bitstring 11111 with probability 1.0.

## isqTrain/3779

- task_id: `isqTrain/3779`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `3624`

### Prompt

请用isQ语言编写一个量子电路：the 6-qubit GHZ state (|000000> + |111111>)/√2 using a for loop for the CNOT chain. Measure all 6 qubits.

### Chain-of-thought reasoning

## Reasoning
The goal is to prepare a 6-qubit GHZ state, creating an equal superposition of all qubits in |0> and all in |1>.
Six qubits are used, and all six are measured at the end of the circuit.
Starting from the initial state |000000>, applying a Hadamard gate to q[0] creates the state (|0> + |1>)/√2 ⊗ |00000>.
Applying the CNOT chain iteratively entangles each subsequent qubit to the first, sequentially propagating the superposition to evolve the state into (|000000> + |111111>)/√2.
Because the final state is an exact equal superposition of only the |000000> and |111111> basis states, measurement collapses it to either |000000> or |111111>, each with a probability of 0.5.

## isqTrain/1454

- task_id: `isqTrain/1454`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `4534`

### Prompt

Code this in isQ: Prepare the computational basis state |1110> on 4 qubits by applying X gates to the appropriate qubits, then measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Prepare the 4-qubit computational basis state |1110> and measure all qubits.
2. **Qubits:** 4 qubits (q[0], q[

## isqTrain/3211

- task_id: `isqTrain/3211`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4942`

### Prompt

实现以下量子计算任务（使用isQ）：an isQ program: apply Rx(1*pi/16) to a qubit and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Apply an Rx rotation of $\pi/16$ to a single qubit and measure the resulting state.
2. **Qubits:** 1 qubit (`q[0]`) is allocated and measured.
3. **Evolution:** The qubit starts in the initial state $|0\rangle$. Applying the $R_x(\pi/16)$ gate rotates the state around the X-axis by $\pi/16$, evolving it to $\cos(\pi/32)|0\rangle - i\sin(\pi/32)|1\rangle$.
4. **Probabilities:** Measuring this state in the computational basis yields probabilities $P(|0\rangle) = \cos^2(\pi/32) \approx 0.9904$ and $P(|1\rangle) = \sin^2(\pi/32) \approx 0.0096$.

## isqTrain/4203

- task_id: `isqTrain/4203`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3539`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;
qbit q[3];

procedure main() {
    H(q[0]);
    Rz(3.14159265358979 * 1.0 / 4.0, q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Circuit:**
        
    *   **Task:** Output prediction of measurement output, step-by-step reasoning using Dirac notation, strictly following the requested format.
    *   **Format Rules:** "## Circuit Analysis" section, NO  blocks, 3-8 lines for simple (this is simple), end with probability distribution.

2.  **Circuit Breakdown:**
    *   Initial state: $|000\rangle$
    *   $H(q[0])$: Applies Hadamard to q0 -> $(|0\rangle + |1\rangle)/\sqrt{2} \otimes |00\rangle = (|000\rangle + |100\rangle)/\sqrt{2}$
    *   $Rz(\pi/4, q[0])$: Applies phase shift $e^{-i\pi/8}|0\rangle\langle0| + e^{i\pi/8}|1\rangle\langle1|$ to q0.
        *   State becomes: $(e^{-i\pi/8}|000\rangle + e^{i\pi/8}|100\rangle)/\sqrt{2}$. Note: Often we ignore global phase, but let's be precise or just apply $T$ effectively (since $T = R_z(\pi/4) \cdot GPhase(\pi/8)$, but isQ $R_z$ applies $e^{-i\theta/2}|0\rangle + e^{i\theta/2}|1\rangle$). Let's just state the exact $R_z(\pi/4)$ action: $(|0\rangle + e^{i\pi/4}|1\rangle)/\sqrt{2} \otimes |00\rangle$ (ignoring the $e^{-i\pi/8}$ global phase). Let's call the phase $e^{i\pi/4} = e^{i\pi/4}$.
        *   Wait, $R_z(\theta)|0\rangle = e^{-i\theta/2}|0\rangle$, $R_z(\theta)|1\rangle = e^{i\theta/2}|1\rangle$.
        *   So $R_z(\pi/4)(|0\rangle + |1\rangle)/\sqrt{2} = (e^{-i\pi/8}|0\rangle + e^{i\pi/8}|1\rangle)/\sqrt{2} = e^{-i\pi/8}(|0\rangle + e^{i\pi/4}|1\rangle)/\sqrt{2}$. Yes.
    *   $CNOT(q[0], q[1])$: Flips q1 if q0 is 1. State: $(|000\rangle + e^{i\pi/4}|110\rangle)/\sqrt{2}$ (dropping global phase).
    *   $CNOT(q[1], q[2])$: Flips q2 if q1 is 1. State: $(|000\rangle + e^{i\pi/4}|111\rangle)/\sqrt{2}$ (dropping global phase).
    *   This is the GHZ state with a relative phase on $|111\rangle$.

3.  **Measurement Probabilities:**
    *   The final state is an equal superposition of $|000\rangle$ and $|111\rangle$.
    *   Probabilities: $P(000) = |1/\sqrt{2}|^2 = 0.5$, $P(111) = |e^{i\pi/4}/\sqrt{2}|^2 = 0.5$. All other outcomes are 0.
    *   Since M(q[0]) is first, then M(q[1]), then M(q[2]), the measurement bitstring for $|000\rangle$ is 000, for $|111\rangle$ is 111.
    *   Output states are correlated (entangled). Either all 0s or all 1s.

4.  **Drafting the response (Concise, 3-8 lines):**
    *   Start: ## Circuit Analysis
    *   Apply H to q[0]: $(|0\rangle + |1\rangle)/\sqrt{2} \otimes |00\rangle$.

### Reference answer

Dominant output states: |000>, |111> with probability ~0.50 each

## isqTrain/3957

- task_id: `isqTrain/3957`
- task_type: `bug_fix`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3050`

### Prompt

There's an error in this quantum circuit implementation. Fix it:

```
import std;
// 4-qubit GHZ state with phase pi/2
// Target: (|0000> + e^{i*pi/2}|1111>) / sqrt(2)
qbit q[4];

procedure main() {
    // Create GHZ state
    H(q[0]);
    // Apply phase e^{i*phi} to |1> component
    Rz(3.14159265358979 * 2.0 / 4.0, q[0]);
    // Entangle all qubits
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[3], q[2]);
    // Measure all
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

``` (bug type: swapped qubits)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: The last CNOT on line 16 is `CNOT(q[3], q[2])` — the control and target qubits are swapped. The q[3] qubit has never been acted on and is still in |0⟩, so using it as a control does nothing. The state remains (|0000⟩ + e^{iπ/2}|1110⟩)/√2, never reaching q[3].

2. **Fix**: Change `CNOT(q[3], q[2])` to `CNOT(q[2], q[3])`. This makes q[2] the control and q[3] the target, correctly propagating entanglement to the fourth qubit.

3. **Corrected state evolution**:
   - |0000⟩ → H(q[0]) → (|0000⟩ + |1000⟩)/√2
   - Rz(π/2, q[0]) → (|0000⟩ + e^{iπ/2}|1000⟩)/√2
   - CNOT(q[0],q[1]) → (|0000⟩ + e^{iπ/2}|1100⟩)/√2
   - CNOT(q[1],q[2]) → (|0000⟩ + e^{iπ/2}|1110⟩)/√2
   - CNOT(q[2],q[3]) → (|0000⟩ + e^{iπ

## isqTrain/3754

- task_id: `isqTrain/3754`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1989`

### Prompt

用isQ实现an entangled 2-qubit state by applying Ry(0.785) to q[0] followed by CNOT(q[0], q[1]). This creates cos(θ/2)|00> + sin(θ/2)|11>. Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a partially-entangled 2-qubit state via Ry rotation and CNOT, then measure.
2. **Qubits**: 2 qubits (q[0], q[1]), both measured.
3. **State evolution**:
   - Start: |00⟩
   - After Ry(0.785, q[0]): cos(0.785/2)|00⟩ + sin(0.785/2)|10⟩ ≈ 0.9239|00⟩ + 0.3827|10⟩
   - After CNOT(q[0], q[1]): cos(0.785/2)|00⟩ + sin(0.785/2)|11⟩ ≈ 0.9239|00⟩ + 0.3827|11⟩
4. **Probabilities**: P(|00⟩) = cos²(0.3925) ≈ 0.8537; P(|11⟩) = sin²(0.3925) ≈ 0.1463

## isqTrain/3177

- task_id: `isqTrain/3177`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4531`

### Prompt

请用isQ语言编写一个量子电路：an isQ program: apply Ry(1*pi/8) to one qubit, then CNOT to a second qubit, creating partial entanglement.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Create a partially entangled Bell-like state by rotating one qubit and entangling it with another via CNOT.
2. **Qubits:** 2 qubits, `q[0]` and `q[1]`, both are measured.
3. **State Evolution:** 
   - Initial state: $|00\rangle$
   - After $R_y(\pi/8)$ on `q[0]`: $\cos(\pi/16)|00\rangle + \sin(\pi/16)|10\rangle$
   - After CNOT(0, 1): $\cos(\pi/16)|00\rangle + \sin(\pi/16)|11\rangle$
4. **Probabilities:** Measurement yields $|00\rangle$ with probability $\cos^2(\pi/16) \approx 0.9619$ and $|11\rangle$ with probability $\sin^2(\pi/16) \approx 0.0381$.

## isqTrain/3737

- task_id: `isqTrain/3737`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3295`

### Prompt

Implement a quantum circuit in isQ: Prepare the 5-qubit GHZ state with phase pi/2:
|GHZ> = (|00000> + e^{i*pi/2}|11111>) / sqrt(2)
Use Hadamard on first qubit, Rz for phase, then CNOT chain. Measure all 5 qubits.

### Chain-of-thought reasoning

Step 1: Analyze the user's request.
- Task: Generate a reasoning section for a specific quantum circuit (isQ code generation task, but I only output the reasoning).
- Circuit: 5-qubit GHZ state with phase pi/2, $|GHZ\rangle = (|00000\rangle + e^{i\pi/2}|11111\rangle)/\sqrt{2}$.
- Implementation: H on q[0], Rz(pi/2, q[0]), CNOT chain q[0] -> q[4], Measure all.
- predicted output: A "## Reasoning" section explaining the goal, qubits, state evolution, and probabilities.
- Constraints: 3-8 lines (simple), max 15 lines. No code blocks. Dirac notation. Precise, concise.

Step 2: Draft the reasoning steps.
1. Goal: Prepare a 5-qubit phase-shifted GHZ state.
2. Qubits: 5 qubits (q[0] to q[4]), all measured.
3. Evolution:
   - Start with |00000>.
   - H(q[0]) -> (|0> + |1>)/sqrt(2) ⊗ |0000> = (|00000> + |10000>)/sqrt(2).
   - Rz(pi/2, q[0]) applies phase e^{-i*pi/4} to |0> and e^{i*pi/4} to |1>. Wait, the isQ code uses Rz(3.14159265358979 * 2.0 / 4.0, q[0]) which is Rz(pi/2). Up to global phase, Rz(pi/2)|0> = |0>, Rz(pi/2)|1> = e^{i*pi/2}|1>.
   - State becomes (|00000> + e^{i*pi/2}|10000>)/sqrt(2).
   - CNOT(q[0], q[1]) -> (|00000> + e^{i*pi/2}|11000>)/sqrt(2).
   - CNOT(q[1], q[2]) -> (|00000> + e^{i*pi/2}|11100>)/sqrt(2).
   - CNOT(q[2], q[3]) -> (|00000> + e^{i*pi/2}|11110>)/sqrt(2).
   - CNOT(q[3], q[4]) -> (|00000> + e^{i*pi/2}|11111>)/sqrt(2).
4. Probabilities: Measuring all 5 qubits gives 0.5 probability for |00000> and 0.5 for |11111>.

Step 3: Refine and format the reasoning section.
- Check line count constraints.
- "## Reasoning" header.
- Concise phrasing.

Draft:
## Reasoning
- Goal: Prepare a 5-qubit GHZ state with a $\pi/2$ phase shift on the $|11111\rangle$ component.
- Qubits: 5 qubits are used, and all are measured.
- State Evolution:
  1. Start in $|00000\rangle$.
  2. Apply H to q[0]: $|00000\rangle \to \frac{1}{\sqrt{2}}(|00000\rangle + |10000\rangle)$.
  3. Apply Rz($\pi/2$) to q[0]: State becomes $\frac{1}{\sqrt{2}}(|00000\rangle + e^{i\pi/2}|10000\rangle)$.
  4. Apply CNOT(q[0], q[1]): Propagates the state to $\frac{1}{\sqrt{2}}(|00000\rangle + e^{i\pi/2}|11000\rangle)$.
  5. Apply CNOT(q[1], q[2]), CNOT(q[2], q[3]), CNOT(q[3], q[4]): The CNOT chain copies the control state, resulting in $\frac{1}{\sqrt{2}}(|00000\rangle + e^{i\pi/2}|11111\rangle)$.
- Probabilities: The final state is an equal superposition of two orthogonal basis states, yielding a 50% chance of measuring $|00000\rangle$ and a 50% chance of measuring $|11111\rangle$.

Check length: 11 lines. Perfect.

Wait, Rz definition in isQ:
Rz(theta) = [[e^{-i theta/2}, 0], [0, e^{i theta/2}]]
So Rz(pi/2)|0> = e^{-i pi/4}|0>
Rz
