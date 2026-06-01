# ISQ training COT RAG corpus: state_preparation shard 3

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4014

- task_id: `isqTrain/4014`
- task_type: `bug_fix`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `1254`

### Prompt

Debug this isQ program — it gives unexpected measurement results.

```
import std;
// 5-qubit GHZ state via for loop
qbit q[5];

procedure main() {
    // Superposition on first qubit
    H(q[0]);
    // Entangle all via CNOT chain
    for i in 0:4 {
    // BUG: missing gate here
    }
    // Measure all
    for i in 0:5 {
        M(q[i]);
    }
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis
1. **What the bug is:** The `for i in 0:4` loop in the entanglement phase is empty. Because no operations are applied, the system remains in a separable state |+>|0>|0>|0>|0> instead of forming the desired 5-qubit GHZ state.
2. **What the fix is:** Add the missing two-qubit gate `CNOT(q[i], q[i +

## isqTrain/3109

- task_id: `isqTrain/3109`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `2597`

### Prompt

Write isQ code for the following quantum task: an isQ program: apply H to 3 qubit(s) to create uniform superposition, then measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a uniform superposition over 3 qubits using Hadamard gates and measure them to observe equal probabilities.
2. **Qubits**: 3 qubits (`q[0]`, `q[1]`, `q[2]`) are used, and all are measured.
3. **State Evolution**: 
   - Initialize to |000⟩.
   - Apply H to each qubit: H|0⟩ = |+⟩ = (|0⟩ + |1⟩)/√2.
   - The state becomes |+⟩|+⟩|+⟩ = (1/√8)(|000⟩ + |001⟩ + ... + |111⟩).
4. **Probabilities**: Measuring this state collapses it into one of the 8 possible computational basis states, each with a probability of |1/√8|² = 0.125.

## isqTrain/3840

- task_id: `isqTrain/3840`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3420`

### Prompt

帮我写一个isQ程序：Prepare the graph state for a ring 4 graph with 4 nodes and edges [(0, 1), (1, 2), (2, 3), (0, 3)]. Apply Hadamard to all qubits, then CZ for each edge. Measure all 4 qubits.

### Chain-of-thought reasoning

## Reasoning
1.  **Goal**: Prepare a 4-qubit graph state for a ring graph with edges [(0,1), (1,2), (2,3), (0,3)] and measure it.
2.  **Qubits**: 4 qubits ($q[0]$ to $q[3]$) are initialized in $|0\rangle$ and all are measured.
3.  **Evolution**:
    *   Initial state is $|0000\rangle$.
    *   Applying Hadamard to all qubits creates an equal superposition: $|+\rangle^{\otimes 4} = \frac{1}{4} \sum_{x \in \{0,1\}^4} |x\rangle$.
    *   Applying CZ gates for the edges introduces phases: $|\psi\rangle = \frac{1}{4} \sum_{x} (-1)^{x_0 x_1 + x_1 x_2 + x_2 x_3 + x_0 x_3} |x\rangle$.
4.  **Probabilities**: The amplitudes of the final state all have magnitude $\frac{1}{4}$, meaning every measurement outcome has probability $|\frac{1}{4}|^2 = 0.0625$.

## isqTrain/4213

- task_id: `isqTrain/4213`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5361`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[5];

procedure main() {
    H(q[0]);
    Rz(3.14159265358979 * 4.0 / 4.0, q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
    CNOT(q[3], q[4]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]); M(q[4]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initial state**: The 5-qubit system starts in the ground state $|0\rangle^{\otimes 5} = |00000\rangle$.
2. **Hadamard gate**: Applying `H(q[0])` puts the first qubit into an equal superposition, evolving the state to $|+\rangle|0000\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)|0000\rangle$.
3. **Rz gate**: `

### Reference answer

Dominant output states: |00000>, |11111> with probability ~0.50 each

## isqTrain/3178

- task_id: `isqTrain/3178`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `758`

### Prompt

帮我写一个isQ程序：an isQ program: apply Ry(1*pi/5) to one qubit, then CNOT to a second qubit, creating partial entanglement.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Create a partially entangled two-qubit state using an Ry rotation followed by CNOT.

**Qubits:** 2 qubits (q[0], q[1]), both measured.

**State evolution:**
1. Initial: |00⟩
2. Ry(π/5) on q[0]: cos(π/10)|00⟩ + sin(π/10)|10⟩
3. CNOT(q[0], q[1]): cos(π/10)|00⟩ + sin(π/10)|11⟩ — a partially entangled Bell-like state

**Probabilities:** P(|00⟩) = cos²(π/10) ≈ 0.9045, P(|11⟩) = sin²(π/10) ≈ 0.0955, matching predicted output.

## isqTrain/3732

- task_id: `isqTrain/3732`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2117`

### Prompt

Create an isQ quantum circuit that Prepare the 3-qubit GHZ state with phase pi:
|GHZ> = (|000> + e^{i*pi}|111>) / sqrt(2)
Use Hadamard on first qubit, Rz for phase, then CNOT chain. Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Prepare the 3-qubit GHZ state with phase π: (|000⟩ + e^{iπ}|111⟩)/√2 = (|000⟩ - |111⟩)/√2.

**Qubits:** 3 qubits (q[0], q[1], q[2]), all measured.

**State evolution:**
1. **Initial:** |000⟩
2. **H(q[0]):** (|000⟩ + |100⟩)/√2 — creates superposition on first qubit
3. **Rz(π, q[0]):** Rz applies e^{iθ/2} phase to |1⟩ component (plus global phase). After H+Rz(π), q[0] is in state (|0⟩ - |1⟩)/√2, so overall: (|000⟩ - |100⟩)/√2
4. **CNOT(q[0], q[1]):** (|000⟩ - |110⟩)/√2 — entangles q[0] and q[1]
5. **CNOT(q[1], q[2]):** (|000⟩ - |111⟩)/√2 — entangles all three qubits

**Expected probabilities:** The final state is an equal superposition of |000⟩ and |111⟩ (with a relative phase of -1). Each basis state has amplitude 1/√2, giving measurement probabilities P(|000⟩) = 0.5 and P(|111⟩) = 0.5.

## isqTrain/4663

- task_id: `isqTrain/4663`
- task_type: `code_equivalence`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `987`

### Prompt

Do these two isQ programs produce the same measurement results?

Program A:
```isq
import std;
qbit q[3];

procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    X(q[0]); // additional bit flip
    M(q[0]); M(q[1]); M(q[2]);
}

```

Program B:
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

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** creates a 3-qubit GHZ state, $\frac{1}{\sqrt{2}}(|000\rangle + |111\rangle)$, using a chain of CNOTs. It then applies an X gate to $q[0]$, shifting the state to $\frac{1}{\sqrt{2}}(|100\rangle + |011\rangle)$.
2. **Program B** creates a similar GHZ state, $\frac{1}{\sqrt{2}}(|000\rangle + |111\rangle)$, but uses $q[0]$ as the control for both CNOTs. It omits the final X gate.
3. The key difference is the `X(q[0])` gate in Program A, which flips the first qubit.
4. The measurement probabilities are different: Program A yields a 50/50 distribution between $|100\rangle$ and $|011\rangle$, while Program B yields a 50/50 distribution between $|000\rangle$ and $|111\rangle$.
Verdict: Not equivalent

### Reference answer

{'equivalent': False, 'explanation': 'After adding X gate to Program A, the programs produce different probability distributions.', 'probs_a': {'011': 0.5, '100': 0.5}, 'probs_b': {'000': 0.5, '111': 0.5}}

## isqTrain/3956

- task_id: `isqTrain/3956`
- task_type: `bug_fix`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1430`

### Prompt

这个isQ程序有问题，请找出错误并给出正确代码：

```
import std;
// 4-qubit GHZ state with phase pi
// Target: (|0000> + e^{i*pi}|1111>) / sqrt(2)
qbit q[4];

procedure main() {
    // Create GHZ state
    H(q[0]);
    // Apply phase e^{i*phi} to |1> component
    Rz(3.14159265358979 * 4.0 / 4.0, q[0]);
    // Entangle all qubits
    CNOT(q[0], q[1]);
    CNOT(q[2], q[1]);
    CNOT(q[2], q[3]);
    // Measure all
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

``` (bug type: swapped qubits)

### Chain-of-thought reasoning

## Bug Analysis

**Bug:** The second CNOT gate `CNOT(q[2], q[1])` has swapped control and target qubits. At this point, q[2] is still |0⟩ (never modified), so this CNOT does nothing, breaking the entanglement chain.

**Fix:** Change `CNOT(q[2], q[1])` to `CNOT(q[1], q[2])`, using q[1] (which is entangled with q[0]) as the control to propagate entanglement to q[2].

**State evolution (corrected):**
1. H(q[0]) → (|0000⟩ + |1000⟩)/√2
2. Rz(π, q[0]) → (|0000⟩ − |100

## isqTrain/147

- task_id: `isqTrain/147`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `178`

### Prompt

实现以下量子计算任务（使用isQ）：implements the state_preparation pattern with modified rotation parameters (pi3_to_pi6). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare a single-qubit state by applying an Rx rotation with angle π/6.
2. **Qubits**: 1 qubit (q[0]), which is measured.
3. **State evolution**:
   - Initial state: |ψ⟩ = |0⟩
   - After Rx(π/6, q[0]): |ψ⟩ = cos(π/12)|0⟩ - i·sin(π/12)|1⟩
4. **Expected probabilities**: P(|0⟩) = cos²(π/12) ≈ 0.9330, P(|1⟩) = sin²(π/12) ≈ 0.0670, which matches the specification.

## isqTrain/3873

- task_id: `isqTrain/3873`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `1793`

### Prompt

Implement a quantum circuit in isQ: Prepare a 2-qubit state using amplitude array assignment `q = [1, 0, 0, 1]`. isQ normalizes the amplitudes automatically. Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Prepare a 2-qubit Bell state using amplitude array assignment and measure both qubits.
**Qubits:** 2 qubits `q[0]` and `q[1]`, both measured.
**State evolution:**
- Initial: `q = [1, 0, 0, 1]` assigns amplitudes to basis states |00⟩, |01⟩, |10⟩, |11⟩
- After normalization: |ψ⟩ = (1/√2)|00⟩ + (1/√2)|11⟩ — a maximally entangled Bell state
**Probabilities:** Measuring yields |00⟩ or |11⟩ each with probability |1/√2|² = 0.5.
