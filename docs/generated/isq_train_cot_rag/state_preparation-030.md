# ISQ training COT RAG corpus: state_preparation shard 30

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1434

- task_id: `isqTrain/1434`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1816`

### Prompt

Write isQ code for the following quantum task: Prepare the state |Phi-> Bell state and measure all qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Prepare the $|\Phi^-\rangle$ Bell state and measure both qubits.
Qubits: 2 qubits are needed (q[0], q[1]), and both are measured.
Evolution:
- Start with the initial state $|00\rangle$.
- Apply H(q[0]) to create superposition: $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$.
- Apply CNOT(q[0], q[1]) to entangle the qubits: $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$.
- Apply Z(q[0]) to flip the phase of the $|1\rangle$ component: $\frac{1}{\sqrt{2}}(|00\rangle - |11\rangle)$.
Prob

## isqTrain/3202

- task_id: `isqTrain/3202`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `828`

### Prompt

Implement a quantum circuit in isQ: an isQ program: apply Ry(7*pi/16) to a qubit and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply an Ry rotation of 7*pi/16 to a single qubit and measure its resulting state.
2. **Qubits**: 1 qubit is required, and it is measured.
3. **State Evolution**: Starting in the initial state |0>, applying the Ry(7*pi/16) gate rotates the state around the Y-axis of the Bloch sphere, resulting in the superposition cos(7*pi/32)|0> + sin(7*pi/32)|1>.
4. **Probabilities**: The final measurement yields |0> with probability cos²(7*pi/32) ≈ 0.5975, and |1> with probability sin²(7*pi/32) ≈ 0.4025.

## isqTrain/571

- task_id: `isqTrain/571`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `687`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;
qbit q[5];

procedure main() {
    X(q[0]);
    X(q[4]);
    M(q);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes a 5-qubit register `q` in the state |00000>, then applies an X gate to `q[0]` and `q[4]`, and finally measures all qubits.
2. The initial state is |00000>. 
3. Applying the X gate to `q[0]` flips its state from |0> to |1>, changing the system state to |00001>.
4. Applying the X gate to `q[4]` flips its state from |0> to |1>, changing the system state to |10001>.
5. Since the final state is a definite computational basis state, measurement will yield this exact outcome with certainty.

Predicted probability distribution: {|10001>: 1.0}

### Reference answer

{'predicted_probs': {'17': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/190. Dimension: predict probabilities for reference circuit.'}

## isqTrain/1553

- task_id: `isqTrain/1553`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3751`

### Prompt

Write an isQ program that Apply Y gate to each of 3 qubits and measure all.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply Y gate to each of 3 qubits starting in |000⟩ and measure all qubits.
Qubits: 3 qubits q[0], q[1], q[2], all measured.
State evolution: |000⟩ → Y⊗I⊗I → i|100⟩ → I⊗Y⊗I → i²|110⟩ = -|110⟩ → I⊗I⊗Y → -i|111⟩.
The Y gate maps |0⟩ → i|1⟩, so applying Y to each qubit transforms |000⟩ → i³|111⟩ = -i|111⟩.
Since -i|111⟩ differs from |111⟩ only by a global phase, measurement yields |111⟩ with probability 1.

## isqTrain/4812

- task_id: `isqTrain/4812`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_switch`, `isq_syntax_classical_vars`
- source: `isq_train_cot`
- dataset_index: `5326`

### Prompt

Implement the following in isQ: uses switch with value 3 where no case matches. Declare 2 global qubits. Set int val=3. Use switch(val): case 0 applies X(q[0]), case 1 applies X(q[1]), case 2 applies H(q[0]). Since val=3, no case matches and no gates are applied. Both qubits remain |0>. Measure both. Expected: |00>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Demonstrate that a switch statement with no matching case leaves all qubits unchanged.
2. **Qubits**: 2 global qubits q[0] and q[1], both measured.
3. **State evolution**: Initial state is |00⟩. Since val=3 doesn't match cases 0, 1, or 2, no gates (X, H) are applied. The state remains |00⟩ throughout.
4. **Expected result**: Measurement yields {|00⟩: 1.0} with certainty, as both qubits stay in |0⟩.

## isqTrain/3212

- task_id: `isqTrain/3212`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1121`

### Prompt

Write an isQ program that an isQ program: apply Rx(3*pi/16) to a qubit and measure.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply an Rx(3π/16) rotation to a single qubit and measure the resulting state.
2. One qubit (q[0]) is required and measured.
3. Starting from |0⟩, the Rx(3π/16) gate transforms the state to cos(3π/32)|0⟩ − i·sin(3π/32)|1⟩.
4. Measurement probabilities: P(|0⟩) = cos²(3π/32) ≈ 0.9157, P(|1⟩) = sin²(3π/32) ≈ 0.0843.

## isqTrain/403

- task_id: `isqTrain/403`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `entanglement`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3926`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;

qbit q[4];

procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
    
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initial State**: The 4-qubit system begins in the ground state |0000>.
2. **Hadamard Gate (H(q[0]))**: Puts the first qubit into an equal superposition, changing the state to (1/√2)(|0000> + |1000>).
3. **CNOT Gate (CNOT(q[0], q[1]))**: Entangles q[0] and q[1]. Since q[0] is the control, the state becomes (1/√2)(|0000> + |1100>).
4. **CNOT Gate (CNOT(q[1], q[2]))**: Entangles q[1] and q[2], flipping q[2] when q[1] is |1>. The state updates to (1/√2)(|0000> + |1110>).
5. **CNOT Gate (CNOT(q[2], q[3]))**: Entangles q[2] and q[3], flipping q[3] when q[2] is |1>. The final state

### Reference answer

{'predicted_probs': {'0': 0.5, '15': 0.5}, 'explanation': 'Parametric variant of isqHumanEval/119. Dimension: predict probabilities for reference circuit.'}

## isqTrain/3149

- task_id: `isqTrain/3149`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `2365`

### Prompt

帮我写一个isQ程序：an isQ program: apply X to all 5 qubits to prepare |11111>, then measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare the 5-qubit state |11111⟩ by flipping all qubits from their ground state, then measure.
2. **Qubits**: 5 qubits (q[0]–q[4]) are allocated and all are measured.
3. **State evolution**: The system starts in |00000⟩. Each X gate acts as a bit-flip (|0⟩→|1⟩) on its respective qubit. Applying X to all five qubits transforms |00000⟩ → |11111⟩.
4. **Expected probabilities**: Since the final state is exactly |11111⟩ with unit amplitude, measurement yields the bitstring 11111 with probability 1.0.

## isqTrain/4000

- task_id: `isqTrain/4000`
- task_type: `bug_fix`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2684`

### Prompt

This isQ program compiles but produces incorrect probabilities. Find and correct the mistake.

```
import std;
// Graph state for star_4 topology
// Edges: [(0, 1), (0, 2), (0, 3)]
qbit q[4];

procedure main() {
    // Step 1: Hadamard on all qubits (|+>^n)
    H(q[0]);
    H(q[1]);
    H(q[2]);
    H(q[3]);
    // Step 2: CZ for each edge
    CZ(q[0], q[1]);  // edge (0,1)
    CZ(q[2], q[0]);  // edge (0,2)
    CZ(q[0], q[3]);  // edge (0,3)
    // Measure all qubits
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
}

``` (bug type: swapped qubits)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: In line `CZ(q[2], q[0]);  // edge (0,2)`, the qubit arguments are swapped. The edge is (0, 2), meaning q[0] should be the first argument and q[2] the second, but they are reversed as `CZ(q[2], q[0])`.

2. **Fix**: Change `CZ(q[2], q[0])` to `CZ(q[0], q[2])` so the qubit order matches the intended edge (0, 2). This aligns all three CZ calls with their respective edges: (0,1), (0,2), and (0,3).

3. **State evolution (corrected)**:
   - Initial: |0000⟩
   - After H on all 4 qubits: |+⟩⊗4 = (1/4)∑|x⟩ over all x ∈ {0,1}⁴
   - CZ(q[0],q[1]): applies phase (-1)^(x₀·x₁) for each basis state
   - CZ(q[0],q[2]): applies phase (-1)^(x₀·x₂)
   - CZ(q[0],q[3]): applies phase (-1)^(x₀·x₃)
   - This is the star_4 graph state: each computational basis state |x⟩ has phase (-1)^(x₀·x₁ + x₀·x₂ + x₀·x₃)
   - Measurement probabilities: all 16 basis states equally likely at 1/16 = 0.0625, since |amplitude|² = (1/16)² × 16 = 1/16 for each. ✓

## isqTrain/3216

- task_id: `isqTrain/3216`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1937`

### Prompt

I need an isQ program to an isQ program: apply Rx(1*pi/3) then Ry(1*pi/6) to a qubit and measure.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Apply Rx(π/3) then Ry(π/6) to a single qubit and measure.
2. **Qubits**: 1 qubit, measured at the end.
3. **State evolution**:
   - Initial: |0⟩
   - After Rx(π/3): cos(π/6)|0⟩ − i·sin(π/6)|1⟩ = (√3/2)|0⟩ − (i/2)|1⟩
   - After Ry(π/6): Ry acts as cos(π/12)I − i·sin(π/12)Y, giving state [cos(π/6)cos(π/12) + i·sin(π/6)sin(π/12)]|0⟩ + [cos(π/6)sin(π/12) − i·sin(π/6)cos(π/12)]|1⟩
4. **Probabilities**: P(|0⟩) = cos²(π/6)cos²(π/12) + sin²(π/6)sin²(π/12) ≈ 0.7165; P(|1⟩) ≈ 0.2835.
