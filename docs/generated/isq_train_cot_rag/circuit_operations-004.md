# ISQ training COT RAG corpus: circuit_operations shard 4

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1319

- task_id: `isqTrain/1319`
- task_type: `output_prediction`
- category: `circuit_operations`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4538`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[2];

procedure main() {
    Y(q[0]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations**: The circuit initializes 2 qubits in the state $|00\rangle$, applies a Pauli Y gate to `q[0]`, and then measures both `q[0]` and `q[1]`.
2. **State Evolution**:
   - Initial state: $|00\rangle$
   - Apply $Y(q[0])$: The Pauli Y gate maps $|0\rangle$ to $i|1\rangle$. The system state becomes $i|10\rangle$.
3

### Reference answer

{'predicted_probs': {'2': 1.0}, 'explanation': 'Parametric variant of isqEval/473. Dimension: qubit_variant: q[1] -> q[2].'}

## isqTrain/1860

- task_id: `isqTrain/1860`
- task_type: `output_prediction`
- category: `circuit_operations`
- difficulty: `basic`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `1786`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[2];
procedure main() {
    X(q[0]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. Operations applied: `X` gate on q[0], followed by `CNOT` with q[0] as control and q[1] as target.
2. Initial state is |00>. 
3. The `X` gate flips q[0], evolving the state to |10>.
4. The `CNOT` gate flips the target q[1] because the control q[0] is in the |1> state, resulting in the final state |11>.
5. The measurement will deterministically yield the state where both qubits are 1.

Predicted probability distribution: {'11': 1.0}

### Reference answer

{'predicted_probs': {'11': 1.0}, 'explanation': 'CNOT with control |1⟩ flips target. P(|11⟩) = 1.0 at index 3.'}

## isqTrain/1872

- task_id: `isqTrain/1872`
- task_type: `output_prediction`
- category: `circuit_operations`
- difficulty: `basic`
- concept_tags: `isq_syntax_deriving_gate`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5052`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
qbit q[1];
procedure main() {
    H(q[0]);
    inv T(q[0]);
    H(q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes 1 qubit and applies the following sequence: Hadamard (H), inverse T ($T^\dagger$), and another Hadamard (H).
2. Initial state: $|0\rangle$.
3. After H: $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
4. After $T^\dagger$: $\frac{1}{\sqrt{2}}(|0\rangle + e^{-i\pi/4}|1\rangle)$.
5. After the final H, the state is $\frac{1}{2}(1 + e^{-i\pi/4})|0\rangle + \frac{1}{2}(1 - e^{-i\pi/4})|1\rangle$.
6. Squaring the amplitudes gives the probabilities.

Probability of measurement outcomes:
- **0: 0.8536**
- **1: 0.1464**

### Reference answer

{'predicted_probs': {'0': 0.8536, '1': 0.1464}, 'explanation': 'Expected probabilities: [0.8535533905932737, 0.14644660940672627]'}

## isqTrain/173

- task_id: `isqTrain/173`
- task_type: `output_prediction`
- category: `circuit_operations`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_deriving_gate`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `1895`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[2];

procedure my_ry(double th, qbit t) {
    Ry(th, t);
} deriving gate

procedure main() {
    X(q[0]);
    ctrl my_ry(pi/4.0, q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a concise, precise step-by-step circuit analysis of the given isQ program, predicting the probability distribution of measurement outcomes.
2.  **Analyze the Code:**
    *   `qbit q[2];` -> 2 qubits, initial state |00>
    *   `X(q[0]);` -> Apply X gate to q[0]. State becomes |10>
    *   `ctrl my_ry(pi/4.0, q[0], q[1]);` -> Apply a controlled-Ry gate with `q[0]` as control and `q[1]` as target, rotation angle $\pi/4$. Wait, the syntax is `ctrl my_ry(pi/4.0, q[0], q[1]);`. In isQ, `ctrl @[control] Gate(target)` is standard, but here `ctrl` is applied to a procedure `my_ry(theta, target)`. The arguments are `pi/4.0` (theta) and `q[1]` (target). Wait, the arguments to `ctrl my_ry` are `(pi/4.0, q[0], q[1])`? Ah, in isQ, if you do `ctrl my_ry(pi/4.0, q[0], q[1])`, `q[0]` is the control, and `q[1]` is the target. Let me double check the isQ syntax for controlled custom gates.
    *   Standard isQ control syntax: `ctrl Gate(params, target)` with control qubit passed? Wait, usually it's `ctrl @[control] Gate(params, target)`. However, the code says `ctrl my_ry(pi/4.0, q[0], q[1]);`. Wait, maybe `q[0]` and `q[1]` are the arguments? If `my_ry` takes `(double th, qbit t)`, then it only needs 1 qubit. But `ctrl my_ry(pi/4.0, q[0], q[1]);` has `q[0]` and `q[1]`. This means `q[0]` is the control, and `q[1]` is the target. Let's trace state evolution with this assumption: Control is q[0], Target is q[1].
    *   Initial state: |00>
    *   After X(q[0]): |10>
    *   After C-Ry(pi/4, q[0], q[1]) where q[0] is control, q[1] is target: Ry(pi/4) is applied to q[1] since q[0] is |1>.
    *   Ry(pi/4) = [[cos(pi/8), -sin(pi/8)], [sin(pi/8), cos(pi/8)]].
    *   Wait, Ry(theta) = [[cos(theta/2), -sin(theta/2)], [sin(theta/2), cos(theta/2)]].
    *   So Ry(pi/4) = [[cos(pi/8), -sin(pi/8)], [sin(pi/8), cos(pi/8)]].
    *   Apply to |0>: cos(pi/8)|0> + sin(pi/8)|1>.
    *   Since initial state of q[1] is |0>, new state is cos(pi/8)|10> + sin(pi/8)|11>.
    *   Probabilities: P(|10>) = cos^2(pi/8) = (1 + cos(pi/4))/2 = (1 + 1/sqrt(2))/2 ≈ (1 + 0.70710678)/2 = 0.85355339.
    *   P(|11>) = sin^2(pi/8) = (1 - cos(pi/4))/2 = (1 - 1/sqrt(2))/2 ≈ (1 - 0.70710678)/2 = 0.1464466.
    *   The reference probabilities given are: {|10>: 0.8535533905932737, |11>: 0.1464466094067262}.
    *   This perfectly matches my calculation.
3.  **Draft the Analysis:**
    *   **Step 1:** Initialize 2 qubits to |00>.
    *   **Step 2:** Apply X gate to q[0]. State becomes |10>.
    *   **Step 3:** Apply controlled-Ry(pi/4) to q[1], controlled by q[0] (`ctrl my_ry` takes `q[0]` as control and `q[1]` as target).
    *   **

### Reference answer

{'predicted_probs': {'2': 0.8535533905932737, '3': 0.1464466094067262}, 'explanation': 'Parametric variant of isqHumanEval/59. Dimension: predict probabilities for reference circuit.'}

## isqTrain/4508

- task_id: `isqTrain/4508`
- task_type: `output_prediction`
- category: `circuit_operations`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `3102`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
qbit q[1];

procedure main() {
    Ry(pi/4.0, q[0]);
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Gates applied:** `Ry(pi/4, q[0])`, `X(q[0])`
2. **State evolution:**
   - Initial state: |0>
   - After `Ry(pi/4, q[0])`: cos(π/8)|0> + sin(π/8)|1>
   - After `X(q[0])`: sin(π/8)|0> + cos(π/8)|1>
3. **Final state before measurement:** sin(π/8)|0> + cos(π/8)|1>
4. **Predicted probabilities:** 
   - P(|0>) = sin^2(π/8) = (2 - √2)/4 ≈ 0.1464
   - P(|1>) = cos^2(π/8) = (2 + √2)/4 ≈ 0.8536
   - The X gate swaps the amplitudes of |0> and |1>, thereby swapping the measurement probabilities from the state immediately preceding it.

**Probability Distribution:** {|0>: 0.14644660940672624, |1>: 0.8535533905932737}

### Reference answer

{'predicted_probs': {'0': 0.146447, '1': 0.853553}, 'explanation': 'This isQ program operates on 1 qubit(s). The measurement probability distribution is: P(|0>) = 0.1464, P(|1>) = 0.8536.'}

## isqTrain/2499

- task_id: `isqTrain/2499`
- task_type: `code_equivalence`
- category: `circuit_operations`
- difficulty: `basic`
- concept_tags: `global_phase`, `isq_syntax_deriving_gate`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3717`

### Prompt

Are these two quantum circuits equivalent in terms of measurement output?

Circuit 1:
```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    inv S(q[0]);
    H(q[0]);
    M(q[0]);
}

```

Circuit 2:
```isq
import std;
qbit q[1];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    H(q[0]);
    inv S(q[0]);
    H(q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** initializes |0> and applies a sequence of H, inv S, and H gates before measuring.
2. **Program B** applies the exact same sequence of gates (H, inv S, H) to the initial |0> state before measuring.
3. The only difference is the addition of `GPhase(0.0)` in Program B before the quantum gates. 
4. `GPhase(0.0)` multiplies the quantum state by $e^{i \cdot 0} = 1$, acting as an identity operation with no effect on the state or measurement probabilities.
5. The resulting measurement probabilities are exactly the same.

Equivalent: True

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/2615

- task_id: `isqTrain/2615`
- task_type: `code_equivalence`
- category: `circuit_operations`
- difficulty: `basic`
- concept_tags: `entanglement`, `global_phase`
- source: `isq_train_cot`
- dataset_index: `3177`

### Prompt

比较这两个量子电路，它们的输出概率分布一样吗？

```isq
import std;
qbit q[3];

procedure main() {
    X(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

```isq
import std;
qbit q[3];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    X(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A**: Transforms the initial state |000> by applying an X gate to q[0] to get |100>, followed by CNOTs from q[0] to q[1] and q[2], resulting in the entangled GHZ state |111>.
2. **Program B**: Performs the exact same gate sequence as Program A, but prepends it with a `GPhase(0.0)` operation.
3. **Key difference**: Program B introduces a global phase gate with an angle of 0.0.
4. **Probability equivalence**: A global phase of 0.0 corresponds to a complex multiplier of $e^{i \cdot 0} = 1$, which acts as an identity operation. Therefore, both programs yield the exact same final state |111> and have identical measurement probabilities (100% chance of measuring 111).
5. **Verdict**: Equivalent: True

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/1786

- task_id: `isqTrain/1786`
- task_type: `code_generation`
- category: `circuit_operations`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3688`

### Prompt

Write isQ code for the following quantum task: Reverse the qubit order of 4 qubits using SWAP gates. Start with |1000>.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Reverse the order of 4 qubits using swap (three-CNOT decomposition) gates, transforming |1000⟩ to |0001⟩.

2. **Qubits**: 4 qubits (q[0] to q[3]), all measured at the end.

3. **State evolution**:
   - Initial: |0000⟩
   - After X(q[0]): |1000⟩
   - After swap (three-CNOT decomposition)(q[0], q[3]): q[0]↔q[3] swaps, moving the |1⟩ to q[3] → |0001⟩
   - After swap (three-CNOT decomposition)(q[1], q[2]): q[1]↔q[2] swaps |0⟩ with |0⟩ → |0001⟩ (unchanged)

4. **Expected probabilities**: Final state is |0001⟩ with certainty, giving measurement probability P(|0001⟩) = 1.0. The swap (three-CNOT decomposition) network successfully reverses qubit order: q[0]→q[3], q[3]→q[0], q[1]→q[2], q[2]→q[1].

## isqTrain/2501

- task_id: `isqTrain/2501`
- task_type: `code_equivalence`
- category: `circuit_operations`
- difficulty: `basic`
- concept_tags: `global_phase`, `isq_syntax_deriving_gate`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1161`

### Prompt

这两个isQ程序是等价的吗？

程序A：
```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    inv T(q[0]);
    H(q[0]);
    M(q[0]);
}

```

程序B：
```isq
import std;
qbit q[1];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    H(q[0]);
    inv T(q[0]);
    H(q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A**: Initializes |0>, applies H, T-dagger (inv T), and H again before measuring.
2. **Program B**: Applies exactly the same quantum gates as Program A, but precedes them with a `GPhase(0.0)`. 
3. **Key Difference**: Program B includes a global phase gate with an angle of 0.
4. **Measurement Probabilities**: Since $e^{i \cdot 0} = 1$, `GPhase(0.0)` multiplies the quantum state by 1, leaving the statevector and all measurement probabilities completely unchanged.
5. **Verdict**: Equivalent: Yes

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/1765

- task_id: `isqTrain/1765`
- task_type: `code_generation`
- category: `circuit_operations`
- difficulty: `difficult`
- concept_tags: `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `4857`

### Prompt

Implement the following in isQ: Apply a 4-controlled X gate (ctrl ctrl ctrl ctrl X) where all 4 control qubits are |1>. The target should flip.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply a 4-controlled X gate where all 4 control qubits are |1⟩ to verify the target flips.
2. **Qubits**: 5 qubits (q[0]–q[4]), all measured; q[0]–q[3] are controls, q[4] is the target.
3. **State evolution**:
   - Initial state: |00000⟩
   - After X(q[0]), X(q[1]), X(q[2]), X(q[3]): |11110⟩
   - After ctrl ctrl ctrl ctrl X(q[0], q[1], q[2], q[3], q[4]): Since all 4 controls are |1⟩, the target q[4] flips: |11111⟩
4. **Expected probabilities**: The final state is |11111⟩, so measurement yields |11111⟩ with probability 1.0.
