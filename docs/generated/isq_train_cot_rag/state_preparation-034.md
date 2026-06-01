# ISQ training COT RAG corpus: state_preparation shard 34

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4021

- task_id: `isqTrain/4021`
- task_type: `bug_fix`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2233`

### Prompt

There's an error in this quantum circuit implementation. Fix it:

```
import std;
// 5-qubit GHZ state with phase pi
// Target: (|00000> + e^{i*pi}|11111>) / sqrt(2)
qbit q[5];

procedure main() {
    // Create GHZ state
    H(q[0]);
    // Apply phase e^{i*phi} to |1> component
    Rz(3.14159265358979 * 4.0 / 4.0, q[0]);
    // Entangle all qubits
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[3], q[2]);
    CNOT(q[3], q[4]);
    // Measure all
    M(q[0]); M(q[1]); M(q[2]); M(q[3]); M(q[4]);
}

``` (bug type: swapped qubits)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug location**: The third CNOT gate `CNOT(q[3], q[2])` has swapped control and target qubits. It uses `q[3]` (which is still in |0⟩) as control to target `q[2]`.

2. **Fix**: Change `CNOT(q[3], q[2])` to `CNOT(q[2], q[3])`, restoring the sequential chain entanglement pattern.

3. **Corrected state evolution**:
   - `H(q[0])` → (|0⟩ + |1⟩)/√2 ⊗ |0000⟩
   - `Rz(π, q[0])` → (|0⟩ + e^{iπ}|1⟩)/√2 ⊗ |0000⟩
   - `CNOT(q[0], q[1])` → (|00⟩ + e^{iπ}|11⟩)/√2 ⊗ |000⟩
   - `CNOT(q[1], q[2])` → (|000⟩ + e^{iπ}|111⟩)/√2 ⊗ |00⟩
   - `CNOT(q[2], q[3])` → (|0000⟩ + e^{iπ}|1111⟩)/√2 ⊗ |0⟩
   - `CNOT(q[3], q[4])` → (|00000⟩ + e^{iπ}|11111⟩)/√2

   This yields the target GHZ state with measurement probabilities {|00000⟩: 0.5, |11111⟩: 0.5}.

## isqTrain/3114

- task_id: `isqTrain/3114`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2129`

### Prompt

实现以下量子计算任务（使用isQ）：an isQ program: apply Rx(pi/3) to a single qubit and measure. Expected P(0)=0.7500, P(1)=0.2500.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Initialize a qubit to |0>, apply an Rx rotation of π/3, and measure.
2. **Qubits**: 1 qubit is used and measured.
3. **State evolution**: 
   - Initial state is |0>.
   - Applying Rx(π/3) transforms the state to cos(π/6)|0> - i*sin(π/6)|1> = √3/2|0> - i/2|1>.
4. **Probabilities**: The probability of measuring |0> is |√3/2|² = 0.75, and the probability of measuring |1> is |-i/2|² = 0.25.

## isqTrain/4067

- task_id: `isqTrain/4067`
- task_type: `bug_fix`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `2457`

### Prompt

Debug this isQ program — it gives unexpected measurement results.

```
import std;
// 2-qubit state via Ry rotations: Ry(2.0 * 0.0) ⊗ Ry(1.0)
qbit q[2];

procedure main() {
    // Apply rotations to create product state
    Ry(0.0, q[0]);
    Ry(1.0, q[1]);
    // Measure
    M(q[0]); M(q[1]);
}

``` (bug type: wrong parameter)

### Chain-of-thought reasoning

The task asks me to analyze the buggy isQ code and explain the bug, fix, and state evolution.

Looking at the code:
- The buggy code applies `Ry(0.0, q[0])` and `Ry(1.0, q[1])`
- The comment says "Ry(2.0 * 0.0) ⊗ Ry(1.0)" which suggests there might have been a parameter issue involving `2.0 * 0.0`
- The resulting probabilities should be {|00>: 0.770151, |01>: 0.229849}

Wait, let me re-read this. The "corrected" code looks identical to the buggy code:

Both the buggy and correct versions have the same code. This is confusing.

Let me re-read the prompt more carefully...

The original task says: "2-qubit Ry product state: (0.0, 1.0)"

The comment in buggy code says: "Ry(2.0 * 0.0) ⊗ Ry(1.0)"

The corrected comment says: "Ry(0.0) ⊗ Ry(1.0)"

Hmm, but the actual code is the same in both cases. Let me check if there's a subtle difference...

Actually looking more carefully at the buggy code comment: `// 2-qubit state via Ry rotations: Ry(2.0 * 0.0) ⊗ Ry(1.0)`

And the corrected code comment: `// 2-qubit state via Ry rotations: Ry(0.0) ⊗ Ry(1.0)`

The code itself appears identical in both versions. This seems like the "bug" might just be in the comment (the `2.0 *` factor), but the code is correct.

Wait, let me look at this more carefully. Maybe the bug is that the original code should have had `Ry(2.0 * 0.0, q[0])` which would be different if the parameter was supposed to be `2.0 * 0.0` vs just `0.0`.

Actually, re-reading: the "bug" type is "wrong_parameter". But the code in both buggy and corrected versions looks the same...

Hmm, this is a bit confusing. Let me assume the task is asking me to analyze and confirm the code is correct with `Ry(0.0, q[0])` and `Ry(1.0, q[1])`.

Let me verify the probabilities:
- Ry(θ) = [[cos(θ/2), -sin(θ/2)], [sin(θ/2), cos(θ/2)]]
- Ry(0.0) = [[1, 0], [0, 1]] = Identity, so q[0] stays as |0⟩
- Ry(1.0) = [[cos(0.5), -sin(0.5)], [sin(0.5), cos(0.5)]]
  - cos(0.5) ≈ 0.87758
  - sin(0.5) ≈ 0.47943

So q[1] state = cos(0.5)|0⟩ + sin(0.5)|1⟩

Product state: |0⟩ ⊗ (cos(0.5)|0⟩ + sin(0.5)|1⟩)
= cos(0.5)|00⟩ + sin(0.5)|01⟩

P(|00⟩) = cos²(0.5) ≈ 0.77015
P(|01⟩) = sin²(0.5) ≈ 0.22985

This matches the predicted output! So the code is correct.

But wait - the task says there's a bug. Looking at the comments more closely:

Buggy comment: `// 2-qubit state via Ry rotations: Ry(2.0 * 0.0) ⊗ Ry(1.0)`

The `2.0 *` in the comment suggests that maybe the buggy version was supposed to have `Ry(2.0 * 0.0, q[0])` but that evaluates to `Ry(0.0, q[0])` anyway since 2.0 * 0.0 = 0.0.

This is a strange case. The bug seems to be in the comment only - the `2.0 *` multiplier is misleading/incorrect notation.

Actually, wait. Maybe I'm overthinking this. The task says "wrong_parameter" as the bug type. Perhaps the actual intended buggy code had a different parameter that I'm not seeing, or the example

## isqTrain/3217

- task_id: `isqTrain/3217`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3421`

### Prompt

Help me write isQ code that an isQ program: apply Rx(1*pi/6) then Ry(1*pi/3) to a qubit and measure.

### Chain-of-thought reasoning

## Reasoning
- Goal: Prepare a single-qubit state by applying sequential X and Y rotations, starting from the ground state.
- Qubits: 1 qubit is required, and 1 is measured.
- Evolution: Starting in |0>, applying Rx(π/6) yields cos(π/12)|0> - i*sin(π/12)|1>.
- Applying Ry(π/3) to this state rotates it around the Y-axis by π/3, resulting in a final state with complex amplitudes for both |0> and |1>.
- Probabilities: The probability of measuring |0> is |cos(π/12)cos(π/6) + i*sin(π/12)sin(π/6)|² ≈ 0.7165, leaving a probability of ≈ 0.2835 for measuring |1>.

## isqTrain/3110

- task_id: `isqTrain/3110`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `5729`

### Prompt

Write isQ code for the following quantum task: an isQ program: apply H to 4 qubit(s) to create uniform superposition, then measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a uniform superposition over all 16 computational basis states of 4 qubits, then measure all.
2. **Qubits**: 4 qubits q[0..3], all measured.
3. **State evolution**: Initial state |0000⟩ → Apply H to each qubit: H|0⟩ = |+⟩ = (|0⟩+|1⟩)/√2 → Final state = (1/√2)⁴ Σ|x⟩ for all x∈{0,1}⁴ = (1/4)(|0000⟩+|0001⟩+...+|1111⟩).
4. **Probabilities**: Each of the 16 basis states has amplitude 1/4, giving probability |1/4|² = 1/16 = 0.0625 each.

## isqTrain/3207

- task_id: `isqTrain/3207`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `627`

### Prompt

I need an isQ program to an isQ program: apply Rx(1*pi/12) to a qubit and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Apply an Rx rotation of π/12 to a single qubit and measure it.
2. **Qubits:** 1 qubit needed; q[0] is measured.
3. **State evolution:**
   - Initial state: |0⟩
   - After Rx(π/12): cos(π/24)|0⟩ - i·sin(π/24)|1⟩
4. **Expected probabilities:**
   - P(|0⟩) = cos²(π/24) ≈ 0.983
   - P(|1⟩) = sin²(π/24) ≈ 0.017

## isqTrain/3184

- task_id: `isqTrain/3184`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2297`

### Prompt

实现以下量子计算任务（使用isQ）：an isQ program: apply Ry(3*pi/7) to one qubit, then CNOT to a second qubit, creating partial entanglement.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Apply an Ry rotation to a qubit and entangle it with a second qubit via CNOT, creating partial entanglement.
2. **Qubits:** 2 qubits (`q[0]`, `q[1]`), both measured.
3. **Evolution:** 
   - Start in |00>.
   - Apply `Ry(3*pi/7)` to `q[0]`: evolves to `cos(3*pi/14)|00> + sin(3*pi/14)|10>`.
   - Apply `CNOT(q[0], q[1])`: evolves to `cos(3*pi/14)|00> + sin(3*pi/14)|11>`.
4. **Probabilities:** Measurement yields `|00>` with probability `cos^2(3*pi/14) ≈ 0.6113` and `|11>` with probability `sin^2(3*pi/14) ≈ 0.3887`.

## isqTrain/4772

- task_id: `isqTrain/4772`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_classical_vars`
- source: `isq_train_cot`
- dataset_index: `5518`

### Prompt

实现以下量子计算任务（使用isQ）：implements: classical var variant 2. Declare a global qbit array q of 1 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Conditionally apply an X gate based on a classical integer variable and measure the qubit.
2. **Qubits**: 1 global qubit (`q[0]`), which is measured.
3. **Evolution**: `q[0]` initializes to |0>. Since the classical variable `val = 3` is greater than 2, the `if` condition evaluates to true.
4. The `X` gate is applied to `q[0]`, flipping its state from |0> to |1>.
5. **Probabilities**: The final quantum state is deterministically |1>, yielding a 100% probability of measuring |1>.

## isqTrain/3996

- task_id: `isqTrain/3996`
- task_type: `bug_fix`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5552`

### Prompt

This isQ program compiles but produces incorrect probabilities. Find and correct the mistake.

```
import std;
// Graph state for ring_4 topology
// Edges: [(0, 1), (1, 2), (2, 3), (0, 3)]
qbit q[4];

procedure main() {
    // Step 1: Hadamard on all qubits (|+>^n)
    H(q[0]);
    H(q[1]);
    H(q[2]);
    // BUG: missing gate here
    // Step 2: CZ for each edge
    CZ(q[0], q[1]);  // edge (0,1)
    CZ(q[1], q[2]);  // edge (1,2)
    CZ(q[2], q[3]);  // edge (2,3)
    CZ(q[0], q[3]);  // edge (0,3)
    // Measure all qubits
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis
1. **The Bug:** The code is missing the `H(q[3])` gate. Consequently, only the first three qubits are initialized to |+>, while the fourth qubit erroneously remains in the |0> state, preventing the correct 4-qubit graph state from being formed.
2.

## isqTrain/568

- task_id: `isqTrain/568`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `4`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[5];

procedure main() {
    X(q[1]);
    X(q[2]);
    X(q[3]);
    M(q);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations:** The circuit initializes a 5-qubit register in the $|00000\rangle$ state. It then applies the Pauli-X gate to qubits `q[1]`, `q[2]`, and `q[3]`.
2. **State Evolution:** 
   - Initial state: $|00000\rangle$
   - `X(q[1])` flips the second qubit to $|1\rangle$: $|00010\rangle$
   - `X(q[2])` flips the third qubit to $|1\rangle$: $|00110\rangle$
   - `X(q[3])` flips the fourth qubit to $|1\rangle$: $|01110\rangle$
3. **Final state:** The system is in a definite computational basis state: $|01110\rangle$.
4. **Probabilities:** Because the final state is exactly $|01110\rangle$, measurement will yield this bitstring with 100% probability (where `q[0]` is the highest-order bit).

Predicted probability distribution: {|01110>: 1.0}

### Reference answer

{'predicted_probs': {'14': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/187. Dimension: predict probabilities for reference circuit.'}
