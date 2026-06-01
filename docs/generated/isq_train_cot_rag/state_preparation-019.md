# ISQ training COT RAG corpus: state_preparation shard 19

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3113

- task_id: `isqTrain/3113`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2541`

### Prompt

帮我写一个isQ程序：an isQ program: apply Rx(pi/4) to a single qubit and measure. Expected P(0)=0.8536, P(1)=0.1464.

### Chain-of-thought reasoning

## Reasoning
The goal is to initialize a qubit to |0>, apply an Rx rotation of pi/4, and measure the resulting state.
One qubit is needed, and it is the only one measured.
Starting from state |0>, the Rx(pi/4) gate rotates the state vector around the X-axis by pi/4, evolving the state to cos(pi/8)|0> - i*sin(pi/8)|1>.
The probability of measuring the |0> state is given by cos^2(pi/8) ≈ 0.8536.
The probability of measuring the |1> state is sin^2(pi/8) ≈ 0.1464.

## isqTrain/3912

- task_id: `isqTrain/3912`
- task_type: `bug_fix`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4326`

### Prompt

There's an error in this quantum circuit implementation. Fix it:

```
import std;
// Entangled 2-qubit state via Ry(2.0 * 1.500) + CNOT
qbit q[2];

procedure main() {
    // Create entangled state
    Ry(1.500, q[0]);
    CNOT(q[0], q[1]);
    // Measure
    M(q[0]); M(q[1]);
}

``` (bug type: wrong parameter)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: The comment incorrectly describes the operation as `Ry(2.0 * 1.500)` (i.e., Ry(3.0)), which misrepresents the gate parameter. The actual code uses `Ry(1.500)`, which is correct for the desired entangled state.

2. **Fix**: Correct the comment from `Ry(2.0 * 1.500)` to `Ry(1.500)`. The gate call `Ry(1.500, q[0])` is already correct and unchanged.

3. **State evolution**:
   - Initialize: |00⟩
   - Ry(1.500, q[0]): cos(0.75)|0⟩ + sin(0.75)|1⟩ on q[0] → cos(0.75)|00⟩ + sin(0.75)|10⟩
   - CNOT(q[0], q[1]): cos(0.75)|00⟩ + sin(0.75)|11⟩
   - P(|00⟩) = cos²(0.75) ≈ 0.5354, P(|11⟩) = sin²(0.75) ≈ 0.4646 ✓

## isqTrain/3191

- task_id: `isqTrain/3191`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4667`

### Prompt

实现以下量子计算任务（使用isQ）：an isQ program: apply Ry(1*pi/10) to one qubit, then CNOT to a second qubit, creating partial entanglement.

### Chain-of-thought reasoning

## Reasoning
- Goal: Generate partial entanglement between two qubits by applying a small Y-rotation to the first qubit and entangling it with the second via CNOT.
- Qubits: 2 qubits (`q[0]`, `q[1]`) are allocated, and both are measured

## isqTrain/3179

- task_id: `isqTrain/3179`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4294`

### Prompt

用isQ实现an isQ program: apply Ry(2*pi/5) to one qubit, then CNOT to a second qubit, creating partial entanglement.

### Chain-of-thought reasoning

## Reasoning
Goal: Create a partially entangled two-qubit state by rotating the first qubit with Ry and then entangling it with the second via CNOT.
Two qubits `q[0]` and `q[1]` are required, and both are measured.
1. Initial state is |00>.
2. Apply `Ry(2*pi/5)` to `q[0]`. This evolves the state to `cos(pi/5)|00> + sin(pi/5)|10>`.
3. Apply `CNOT(q[0], q[1])` with `q[0]` as control and `q[1]` as target. This flips the target when the control is |1>, yielding the entangled state `cos(pi/5)|00> + sin(pi/5)|11>`.
The measurement probabilities are the squares of the amplitudes: `P(|00>) = cos^2(pi/5) ≈ 0.6545` and `P(|11>) = sin^2(pi/5) ≈ 0.3455`.

## isqTrain/3393

- task_id: `isqTrain/3393`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `1787`

### Prompt

请用isQ语言编写一个量子电路：an isQ program: in a 5-qubit register, apply X then H to q[0] only. Other qubits stay |0>. Measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply X then H to q[0] only, creating a superposition, while leaving q[1]-q[4] in |0⟩.
2. **Qubits**: 5-qubit register; all 5 qubits are measured.
3. **State evolution**:
   - Initial: |00000⟩
   - After X(q[0]): X|0⟩ = |1⟩ → |10000⟩
   - After H(q[0]): H|1⟩ = (|0⟩ - |1⟩)/√2 → (|00000⟩ - |10000⟩)/√2
4. **Expected probabilities**: Each basis state |00000⟩ and |10000⟩ has amplitude 1/√2, giving probability |1/√2|² = 0.5 each.

## isqTrain/4225

- task_id: `isqTrain/4225`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2004`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;
qbit q[2];

procedure main() {
    Ry(0.500, q[0]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes two qubits to |00> and applies a rotation `Ry(0.500)` to the first qubit, followed by a `CNOT` gate.
2. Initial state: |00>
3. After `Ry(0.500, q[0])`: cos(0.25)|0> + sin(0.25)|1> on q[0]. State is (cos(0.25)|0> + sin(0.25)|1>) ⊗ |0>.
4. After `CNOT(q[0], q[1])`: Entangled state cos(0.25)|00> + sin(0.25)|11>.
5. Probabilities: P(00) = cos²(0.25) ≈ 93.88%, P(11) = sin²(0.25) ≈ 6.12%.
6. The most likely measurement outcome is 00.

### Reference answer

Deterministic output: state |00> with probability ~0.94

## isqTrain/1326

- task_id: `isqTrain/1326`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `947`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
qbit q[4];

procedure main() {
    X(q[0]);
    X(q[2]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes 4 qubits in the state |0000>, applies an X gate to q[0] and q[2], and then measures all 4 qubits.
2. Initial state: |0000>.
3. After applying X(q[0]), the state flips to |1000>.
4. After applying X(q[2]), the state flips to |1010>.
5. The final state before measurement is exactly |1010>.
6. Because the state is a definitive computational basis state, measuring the qubits yields '1010' with certainty.

Predicted probability distribution: {|1010>: 1.0}

### Reference answer

{'predicted_probs': {'10': 1.0}, 'explanation': 'Parametric variant of isqEval/478. Dimension: qubit_variant: q[3] -> q[4].'}

## isqTrain/1373

- task_id: `isqTrain/1373`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `entanglement`
- source: `isq_train_cot`
- dataset_index: `4316`

### Prompt

Write an isQ program that Prepare a GHZ state on 6 qubits and measure all qubits in the X basis (apply H before measurement).

### Chain-of-thought reasoning

## Reasoning

**Goal**: Prepare a 6-qubit GHZ state and measure all qubits in the X basis.

**Qubits**: 6 qubits (q[0]–q[5]), all measured.

**State evolution**:
1. Initial state: |000000⟩
2. H(q[0]) → (|000000⟩ + |100000⟩)/√2
3. CNOT(q[0], q[1..5]) sequentially → GH

## isqTrain/4802

- task_id: `isqTrain/4802`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_if_else`, `isq_syntax_classical_vars`
- source: `isq_train_cot`
- dataset_index: `2079`

### Prompt

Implement the following in isQ: implements: OR-condition if-else variant 5. Declare a global qbit array q of 3 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement an OR-condition if-else that applies X gates to all three qubits when `x==1 || y==1` is true.
2. **Qubits**: 3 global qubits `q[0]`, `q[1]`, `q[2]`, all measured.
3. **State evolution**:
   - Initial state: |000⟩
   - Condition `(x==1 || y==1)` with x=1, y=0 evaluates to true, so the if-block executes.
   - X(q[0]): |000⟩ → |100⟩
   - X(q[1]): |100⟩ → |110⟩
   - X(q[2]): |110⟩ → |111⟩
   - M(q[0]), M(q[1]), M(q[2]): measurement collapses |111⟩ with certainty.
4. **Expected probabilities**: {|111⟩: 1.0}, since all three qubits are flipped to |1⟩ by the X gates.

## isqTrain/1371

- task_id: `isqTrain/1371`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3401`

### Prompt

Help me write isQ code that Prepare a GHZ state on 6 qubits: (|000000> + |111111>) / sqrt(2). Measure all qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare a 6-qubit GHZ state (|000000> + |111111>) / sqrt(2) and measure all qubits.
2. **Qubits**: 6 qubits are used, and all 6 are measured.
3. **State Evolution**:
   - Start in the ground state |000000>.
   - Apply H(q[0]) to put the first qubit into an equal superposition: (|0> + |1>)|00000> / sqrt(2).
   - Apply CNOT(q[0], q[1]) to entangle q[1] with q[0]: (|00> + |11>)|0000> / sqrt(2).
   - Apply CNOT(q[0], q[2]) to entangle q[2]: (|000> + |111>)|000> / sqrt(2).
   - Apply CNOT(q[0], q[3]) to entangle q[3]: (|0000> + |1111>)|00> / sqrt(2).
   - Apply CNOT(q[0], q[4]) to entangle q[4]: (|00000> + |11111>)|0> / sqrt(2).
   - Apply CNOT(q[0], q[5]) to entangle q[5]: (|000000> + |111111>) / sqrt(2).
4. **Probabilities**: Measurement collapses the entire state simultaneously, yielding |000000> with probability 0.5 and |111111> with probability 0.5.
