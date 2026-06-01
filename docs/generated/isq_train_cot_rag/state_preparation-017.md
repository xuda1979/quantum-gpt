# ISQ training COT RAG corpus: state_preparation shard 17

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1369

- task_id: `isqTrain/1369`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2180`

### Prompt

实现以下量子计算任务（使用isQ）：Prepare a GHZ state on 5 qubits, then apply a Z gate to the first qubit to create a relative phase. Measure all qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a 5-qubit GHZ state with a relative phase by applying Z to the first qubit, then measure all.
2. **Qubits**: 5 qubits (q[0]–q[4]), all measured.
3. **State evolution**:
   - Start: |00000⟩
   - H(q[0]): (|0⟩ + |1⟩)/√2 ⊗ |0000⟩ = (|00000⟩ + |10000⟩)/√2
   - CNOT(q[0], q[1]): (|00000⟩ + |11000⟩)/√2
   - CNOT(q[0], q[2]): (|00000⟩ + |11100⟩)/√2
   - CNOT(q[0], q[3]): (|00000⟩ + |11110⟩)/√2
   - CNOT(q[0], q[4]): (|00000⟩ + |11111⟩)/√2 — GHZ state
   - Z(q[0]): (|00000⟩ - |11111⟩)/√2
4. **Expected probabilities**: Both |00000⟩ and |11111⟩ have amplitude ±1/√2, giving probability 0.5 each. The Z gate introduces a relative phase but doesn't change measurement outcomes.

## isqTrain/4720

- task_id: `isqTrain/4720`
- task_type: `code_equivalence`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5449`

### Prompt

Determine if these two isQ implementations are functionally equivalent:

Version A:
```isq
import std;
qbit q[2];

procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    X(q[0]); // additional bit flip
    M(q[0]); M(q[1]);
}

```

Version B:
```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    X(q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** applies an H gate to q[0], followed by a CNOT between q[0] and q[1], and finally an X gate to q[0]. This evolves the initial |00> state to the entangled state (1/√2)(|01> + |10>).
2. **Program B** simply applies an X gate to both q[0] and q[1]. This transforms the initial |00> state to the classical basis state |11>.
3. **The key difference** is that Program A generates a superposition of |01> and |10>, whereas Program B deterministically prepares the state |11>.
4. The measurement probabilities are different: Program A yields a 50% chance of measuring '01' and a 50% chance of measuring '10'. Program B yields a 100% chance of measuring '11'.
5. **Verdict**: No (Not Equivalent)

### Reference answer

{'equivalent': False, 'explanation': 'After adding X gate to Program A, the programs produce different probability distributions.', 'probs_a': {'01': 0.5, '10': 0.5}, 'probs_b': {'11': 1.0}}

## isqTrain/1451

- task_id: `isqTrain/1451`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `5304`

### Prompt

Implement a quantum circuit in isQ: Prepare the computational basis state |1010> on 4 qubits by applying X gates to the appropriate qubits, then measure all.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Prepare the 4-qubit computational basis state |1010> using X gates, then measure all qubits.
2. Qubits: 4 qubits (q[0] to q[3]), all measured (with earlier measured qubits forming higher bits of the output string).
3. State evolution:
   - Initial state: |0000> (all qubits in |0>)
   - Apply X(q[0]): flips q[0] to |1> → state is |1000> in measurement bitstring order
   - Apply X(q[2]): flips q[2] to |1> → state is |1010>
4. Probabilities: The final state is exactly |1010>, so measuring yields |1010> with probability 1.0.

## isqTrain/1444

- task_id: `isqTrain/1444`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `2932`

### Prompt

Code this in isQ: Prepare the computational basis state |0010> on 4 qubits by applying X gates to the appropriate qubits, then measure all.

### Chain-of-thought reasoning

## Reasoning
Goal: Prepare the 4-qubit state |0010> by flipping the appropriate qubit, then measure all.
Qubits: 4 qubits required, all measured.
State evolution:
1. Initial state: |0000>
2. X(q[2]) flips the third qubit: |0000> -> |0010>
Result: Measurement yields the classical bitstring 0010 with probability 1.0.

## isqTrain/3839

- task_id: `isqTrain/3839`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1956`

### Prompt

I need an isQ program to Prepare the graph state for a line 4 graph with 4 nodes and edges [(0, 1), (1, 2), (2, 3)]. Apply Hadamard to all qubits, then CZ for each edge. Measure all 4 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare a 4-qubit line graph state by initializing all qubits to |+> and entangling them with CZ gates along edges (0,1), (1,2), (2,3).
2. **Qubits**: 4 qubits declared globally; all 4 are measured.
3. **State evolution**:
   - Initial state: |0000⟩
   - After H on all: |++++⟩ = (1/4)Σ_{x∈{0,1}⁴}|x⟩
   - CZ(q[0],q[1]): phase factor (-1)^(x₀·x₁) applied → state picks up phase for edges in graph
   - CZ(q[1],q[2]): accumulates phase (-1)^(x₁·x₂)
   - CZ(q[2],q[3]): accumulates phase (-1)^(x₂·x₃)
   - Final graph state: (1/4)Σ(-1)^(x₀x₁+x₁x₂+x₂x₃)|x₀x₁x₂x₃⟩
4. **Probabilities**: Each basis state |x⟩ has amplitude 1/4 (only phase differs), so all 16 outcomes have equal probability |1/4|² = 0.0625.

## isqTrain/3989

- task_id: `isqTrain/3989`
- task_type: `bug_fix`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4151`

### Prompt

This isQ program doesn't produce the correct output. Can you debug it?

Code:
```
import std;
// 4-qubit GHZ state with phase pi/4
// Target: (|0000> + e^{i*pi/4}|1111>) / sqrt(2)
qbit q[4];

procedure main() {
    // Create GHZ state
    H(q[0]);
    // Apply phase e^{i*phi} to |1> component
    Rz(3.14159265358979 * 1.0 / 4.0, q[0]);
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

1. **Bug**: The final CNOT `CNOT(q[3], q[2])` has swapped control and target qubits. At this point, q[2] is entangled in the |1⟩ component while q[3] is in |0⟩, so using q[3] as control does nothing—it cannot propagate entanglement to q[3].

2. **Fix**: Change `CNOT(q[3], q[2])` to `CNOT(q[2], q[3])`, using q[2] as control to flip q[3] when q[2] is |1⟩.

3. **Corrected state evolution**:
   - H(q[0]): (|0⟩ + |1⟩)/√2 ⊗ |000⟩
   - Rz(π/4, q[0]): (|0⟩ + e^{iπ/4}|1⟩)/√2 ⊗ |000⟩
   - CNOT(q[0], q[1]): (|00⟩ + e^{iπ/4}|11⟩)/√2 ⊗ |00⟩
   - CNOT(q[1], q[2]): (|000⟩ + e^{iπ/4}|111⟩)/√2 ⊗ |0⟩
   - CNOT(q[2], q[3]): (|0000⟩ + e^{iπ/4}|1111⟩)/√2 ✓

## isqTrain/4224

- task_id: `isqTrain/4224`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `4956`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[2];

procedure main() {
    Ry(1.0, q[0]);
    Ry(0.5, q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the isQ code:**
    *   Two qubits: `q[0]`, `q[1]`.
    *   Initial state: $|00\rangle$.
    *   `Ry(1.0, q[0])`: Rotates `q[0]` around Y-axis by angle 1.0.
    *   `Ry(0.5, q[1])`: Rotates `q[1]` around Y-axis by angle 0.5.
    *   Measurements: `M(q[0])` and `M(q[1])`.

2.  **State Evolution:**
    *   Start: $|\psi_0\rangle = |0\rangle \otimes |0\rangle = |00\rangle$.
    *   Apply $R_y(1.0)$ to $q[0]$:
        $R_y(\theta) = \begin{pmatrix} \cos(\theta/2) & -\sin(\theta/2) \\ \sin(\theta/2) & \cos(\theta/2) \end{pmatrix}$.
        For $\theta = 1.0$, $q[0]$ becomes $\cos(0.5)|0\rangle + \sin(0.5)|1\rangle$.
    *   Apply $R_y(0.5)$ to $q[1]$:
        For $\theta = 0.5$, $q[1]$ becomes $\cos(0.25)|0\rangle + \sin(0.25)|1\rangle$.
    *   Combined state: $|\psi_f\rangle = (\cos(0.5)|0\rangle + \sin(0.5)|1\rangle) \otimes (\cos(0.25)|0\rangle + \sin(0.25)|1\rangle)$.

3.  **Calculate probabilities:**
    *   $P(00) = \cos^2(0.5) \cos^2(0.25) \approx (0.8776)^2 \approx 0.770$
    *   $P(01) = \cos^2(0.5) \sin^2(0.25) \approx (0.8776) \times (0.2474)^2 \approx 0.0537$
    *   $P(10) = \sin^2(0.5) \cos^2(0.25) \approx (0.4794)^2 \times (0.9689)^2 \approx 0.2155$
    *   $P(11) = \sin^2(0.5) \sin^2(0.25) \approx (0.4794)^2 \times (0.2474)^2 \approx 0.014$

    Let's refine the exact values:
    *   $P(00) = \cos^2(0.5)\cos^2(0.25) \approx 0.770$
    *   $P(01) = \cos^2(0.5)\sin^2(0.25) \approx 0.054$
    *   $P(10) = \sin^2(0.5)\cos^2(0.25) \approx 0.216$
    *   $P(11) = \sin^2(0.5)\sin^2(0.25) \approx 0.014$

    Bitstring mapping: The isQ --probs mode output usually maps `M(q[0])` to the highest bit (or it's mapped as $q_0 q_1$).
    State $q_0=0, q_1=0 \rightarrow |00\rangle \rightarrow 0$
    State $q_0=0, q_1=1 \rightarrow |01\rangle \rightarrow 1$
    State $q_0=1, q_1=0 \rightarrow |10\rangle \rightarrow 2$
    State $q_0=1, q_1=1 \rightarrow |11\rangle \rightarrow 3$
    Most likely outcome: $|00\rangle$ (or bitstring 0).

4.  **Draft the response:**
    *   Step 1: Initial state is $|00\rangle$.
    *   Step 2: `Ry(1.0, q[0])` applies $R_y(\theta)$ with $\theta=1.0$ to $q[0]$, transitioning it to $\cos(0.5)|0\rangle + \sin(0.5)|1\rangle$.
    *   Step 3: `R

### Reference answer

Dominant output states: |00> with probability ~0.72 each

## isqTrain/3175

- task_id: `isqTrain/3175`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3391`

### Prompt

帮我写一个isQ程序：an isQ program: apply Ry(pi/3) to q[0], then CNOT(q[0],q[1]) to create partial entanglement. Measure both.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a partially entangled two-qubit state using Ry(pi/3) and CNOT, then measure both qubits.
2. **Qubits**: 2 qubits (q[0], q[1]), both measured.
3. **State evolution**:
   - Initial: |00⟩
   - Ry(π/3) on q[0]: cos(π/6)|0⟩ + sin(π/6)|1⟩ → state = (√3/2)|00⟩ + (1/2)|10⟩
   - CNOT(q[0], q[1]): flips q[1] when q[0]=|1⟩ → (√3/2)|00⟩ + (1/2)|11⟩
4. **Probabilities**: P(|00⟩) = (√3/2)² = 0.75, P(|11⟩) = (1/2)² = 0.25. No |01⟩ or |10⟩ terms exist due to CNOT correlation.

## isqTrain/3377

- task_id: `isqTrain/3377`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `superposition`, `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `266`

### Prompt

实现以下量子计算任务（使用isQ）：an isQ program: 3-layer circuit with H and CZ on 2 qubits. Each layer: H on all, then CZ between adjacent.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for an isQ quantum program.

1.  **Analyze the Request:**
    *   Task: 3-layer circuit with H and CZ on 2 qubits.
    *   Structure: Each layer applies H to all, then CZ between adjacent. Finally, measurement.
    *   Output: Only the reasoning section starting with "## Reasoning".
    *   Format: 3-8 lines, concise, precise, using Dirac notation.

2.  **Analyze the Circuit:**
    *   Qubits: 2 (q[0], q[1]).
    *   Initial state: |00>.
    *   Layer 1:
        *   H(q[0]), H(q[1]) -> $(H \otimes H)|00\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle) = |++\rangle$.
        *   CZ(q[0], q[1]) -> Applies Z to q[1] if q[0] is |1>. Z(|0>+|1>) = |0>-|1>. Z(|0>-|1>) = |0>+|1>.
        *   State after Layer 1 CZ: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle - |11\rangle)$.
    *   Layer 2:
        *   H(q[0]), H(q[1]) -> Let's apply $H \otimes H$ to the current state.
        *   $H \otimes H (\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle - |11\rangle))$
        *   $H \otimes H |00\rangle = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$
        *   $H \otimes H |01\rangle = \frac{1}{2}(|00\rangle - |01\rangle + |10\rangle - |11\rangle)$
        *   $H \otimes H |10\rangle = \frac{1}{2}(|00\rangle + |01\rangle - |10\rangle - |11\rangle)$
        *   $H \otimes H |11\rangle = \frac{1}{2}(|00\rangle - |01\rangle - |10\rangle + |11\rangle)$
        *   Sum with signs (+, +, +, -):
        *   |00>: 1+1+1+1 = 4 * 1/4 = 1
        *   |01>: 1-1+1-(-1) = 0
        *   |10>: 1+1-1-(-1) = 0
        *   |11>: 1-1-1-(-1) = 0
        *   Wait, let me re-evaluate.
        *   Let's do this easier.
        *   CZ = diag(1, 1, 1, -1).
        *   $H^{\otimes 2} \cdot CZ \cdot H^{\otimes 2}$ is the operator.
        *   In the Hadamard basis, CZ acts as CNOT (with target and control swapped depending on convention, but here we can just see it).
        *   Let's trace it carefully.
        *   Initial: $|00\rangle$
        *   L1: $H^{\otimes 2} |00\rangle = |++\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes |+\rangle$.
        *   CZ applies phase -1 if both are 1: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle - |11\rangle)$.
        *   L2 Hs: Apply $H \otimes H$ to the state.
        *   $H|0\rangle = |+\rangle$, $H|1\rangle = |-\rangle$.
        *   State before L2 H: $\frac{1}{2}(|0\rangle(|0\rangle+|1\rangle) + |1\rangle(|0\rangle-|1\rangle))$.
        *   Apply H to q[1]: $\frac{1}{\sqrt{2}}(|0\rangle|+\rangle + |1\rangle

## isqTrain/3229

- task_id: `isqTrain/3229`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `331`

### Prompt

I need an isQ program to an isQ program: apply Ry(1*pi/2) to q[0] and Ry(1*pi/4) to q[1], then measure both (no entanglement).

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply independent Y-rotations of $\pi/2$ and $\pi/4$ to two qubits and measure them.
2. **Qubits**: 2 qubits (`q[0]`, `q[1]`), both measured.
3. **State Evolution**:
   - Initialize to the ground state $|00\rangle$.
   - Apply $R_y(\pi/2)$ to `q[0]`, evolving it to the $|+\rangle$ state: $\frac{1}{\sqrt
