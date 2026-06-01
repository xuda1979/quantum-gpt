# ISQ training COT RAG corpus: circuit_basics shard 6

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1778

- task_id: `isqTrain/1778`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `4592`

### Prompt

Help me write isQ code that Apply X gate 10 times to |0> and measure. (X^10 = I.)

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Apply the X gate 10 times to a qubit initialized to |0> and measure the result.
2. **Qubits:** 1 qubit is required and measured.
3. **State Evolution:**
   - Initial state is |0>.
   - Each X gate acts as a bit-flip: |0> $\leftrightarrow$ |1>.
   - Applying X 10 times flips the state an even number of times (since $X^2 = I$, $X^{10} = (X^2)^5 = I^5 = I$).
   - The final quantum state returns to |0>.
4. **Expected Probabilities:** Because the final state is exactly |0>, measurement will yield |0> (or classical 0) with a probability of 1.0.

## isqTrain/1466

- task_id: `isqTrain/1466`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `2724`

### Prompt

Code this in isQ: Apply the gate sequence CNOT+H to 2 qubits starting from |00>. Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Apply X, CNOT, then H to two qubits starting from |00>, and measure both.
**Qubits:** 2 qubits (q[0], q[1]), both measured.

**State evolution:**
1. Initial: |00⟩
2. After X(q[0]): |10⟩
3. After CNOT(q[0], q[1]): |11⟩ (control q[0]=|1⟩ flips target q[1])
4. After H(q[0]): (1/√2)(|01⟩ − |11⟩)

**Probabilities:** Both |01⟩ and |11⟩ have amplitude magnitude 1/√2, giving P(|01⟩) = 0.5 and P(|11⟩) = 0.5.

## isqTrain/1753

- task_id: `isqTrain/1753`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `46`

### Prompt

Write isQ code for the following quantum task: Start with |10000> on 5 qubits and apply a CNOT chain (q[0]->q[1], q[1]->q[2], ...). All qubits should end up as |1>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Propagate a single |1> through a 5-qubit CNOT chain to create |11111>.
2. **Qubits**: 5 qubits (q[0] to q[4]), all measured at the end.
3. **State evolution**:
   - Start with |00000>, apply X(q[0]) → |10000⟩
   - CNOT(q[0], q[1]): control=1, flips target → |11000⟩
   - CNOT(q[1], q[2]): control=1, flips target → |11100⟩
   - CNOT(q[2], q[3]): control=1, flips target → |11110⟩
   - CNOT(q[3], q[4]): control=1, flips target → |11111⟩
4. **Result**: Final state is |11111⟩ with probability 1.0, as the initial |1> cascades through the chain.

## isqTrain/1488

- task_id: `isqTrain/1488`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `data_encoding_qml`
- source: `isq_train_cot`
- dataset_index: `5793`

### Prompt

Write isQ code for the following quantum task: Encode the classical value 15/16 into a qubit using angle encoding (Ry rotation with angle pi*15/16). Measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Encode the classical value 15/16 into a qubit via Ry rotation with angle π·15/16, then measure the resulting quantum state.

2. **Qubits**: 1 qubit (`q[0]`), initialized to |0⟩; measured at the end.

3. **State evolution**:
   - Initial state: |ψ₀⟩ = |0⟩
   - Apply Ry(θ) with θ = 15π/16:
     - Ry(θ)|0⟩ = cos(θ/2)|0⟩ + sin(θ/2)|1⟩
     - θ/2 = 15π/32
     - |ψ₁⟩ = cos(15π/32)|0⟩ + sin(15π/32)|1⟩

4. **Measurement probabilities**:
   - P(|0⟩) = cos²(15π/32) ≈ 0.00961
   - P(|1⟩) = sin²(15π/32) ≈ 0.99039
   - Since 15π/32 ≈ 1.473 is close to π/2, the state is heavily tilted toward |1⟩, giving ~99% probability of measuring |1⟩.

## isqTrain/4676

- task_id: `isqTrain/4676`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4961`

### Prompt

Determine if these two isQ implementations are functionally equivalent:

Version A:
```isq
import std;
qbit q[1];

procedure main() {
    X(q[0]);
    X(q[0]);
    M(q[0]);
}

```

Version B:
```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]); // add superposition
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. Program A applies two X gates to the initial |0> state, which acts as an identity operation and leaves the state as |0>.
2. Program B applies an H gate to the initial |0> state, putting it into an equal superposition |+> = (|0> + |1>)/√2.
3. Consequently, Program A measures |0> with 100% probability, whereas Program B measures |0> and |1> each with 50% probability.
4. The two programs result in entirely different measurement probability distributions.
Verdict: No

### Reference answer

{'equivalent': False, 'explanation': 'After adding H gate to Program B, the programs produce different probability distributions.', 'probs_a': {'0': 1.0}, 'probs_b': {'0': 0.5, '1': 0.5}}

## isqTrain/1470

- task_id: `isqTrain/1470`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5688`

### Prompt

请用isQ语言编写一个量子电路：Rotate a qubit from |0> by Ry(pi/4) and measure.

### Chain-of-thought reasoning

## Reasoning
1. The goal is to apply an Ry(pi/4) rotation to a single qubit starting in the ground state |0> and measure the resulting state.
2. The circuit requires 1 qubit, which is measured at the end.
3. The initial state |0> evolves under Ry(pi/4) to cos(pi/8)|0> + sin(pi/8)|1>.
4. Measuring this state yields a probability of cos²(pi/8) = (2 + √2)/4 ≈ 0.8536 for |0>.
5. The probability for |1> is sin²(pi/8) = (2 - √2)/4 ≈ 0.1464.

## isqTrain/1471

- task_id: `isqTrain/1471`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4733`

### Prompt

Implement a quantum circuit in isQ: Rotate a qubit from |0> by Ry(3pi/4) and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Rotate a single qubit from |0⟩ by angle 3π/4 around the Y-axis, then measure.
2. **Qubits**: 1 qubit required; q[0] is measured.
3. **State evolution**:
   - Initial: |ψ⟩ = |0⟩
   - After Ry(3π/4): |ψ⟩ = cos(3π/8)|0⟩ + sin(3π/8)|1⟩
4. **Probabilities**: P(|0⟩) = cos²(3π/8) ≈ 0.1464, P(|1⟩) = sin²(3π/8) ≈ 0.8536, matching the predicted output.

## isqTrain/1583

- task_id: `isqTrain/1583`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `4412`

### Prompt

Help me write isQ code that On 4 qubits, set q[2]=|1> and apply CNOT with control=q[2], target=q[1]. Measure all.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Goal:** Generate a reasoning section for an isQ quantum program.
    *   **Circuit:** 4 qubits (`q[0]` to `q[3]`). Initialize `q[2]` to $|1\rangle$. Apply `CNOT(q[2], q[1])`. Measure all.
    *   **Constraints:** Output ONLY "## Reasoning" section, no code, concise (3-8 lines), use Dirac notation.

2.  **Deconstruct the Circuit:**
    *   Initial state: $|0000\rangle$ (assuming standard convention for `q[0..3]`). Wait, bit ordering: `q[0]` is usually the least significant or most significant. Let's trace it carefully. The prompt says "set q[2]=|1>".
    *   State after initialization: $|0000\rangle$.
    *   After $X(q[2])$: Flips `q[2]` to $|1\rangle$. State is $|0010\rangle$ (where `q[3]` is leftmost, `q[2]` is second, `q[1]` is third, `q[0]` is rightmost) or $|0100\rangle$ depending on notation. Let's use standard ordering $q_3 q_2 q_1 q_0$. So $q_3 q_2 q_1 q_0 = 0010$. Wait, if the expected measurement probability is `|0110>: 1.0`, then the bits correspond to measurements `M(q[0]), M(q[1]), M(q[2]), M(q[3])`. Let's look at the expected measurement array: "earlier measured qubit = higher bit". Wait, "expected measurement probabilities: {|0110>: 1.0}".
    *   Let's decode `|0110>`.
        *   `M(q[0])` corresponds to highest bit? No, usually `M(q[0])` is highest bit (MSB) or lowest bit (LSB). Let's assume `M(q[0])` is MSB (bit 3) for a 4-bit string, or maybe `q[3]` is MSB?
        *   If `q[0]` = 0, `q[1]` = 1, `q[2]` = 1, `q[3]` = 0. This matches `0110` where `q[0]` is MSB? No, `0` (q3), `1` (q2), `1` (q1), `0` (q0) is `0110`.
        *   Wait, `q[2]` is 1, `q[1]` is flipped from 0 to 1 by CNOT. So `q[2]=1`, `q[1]=1`. `q[0]=0`, `q[3]=0`.
        *   String `0110` perfectly matches `q[3]q[2]q[1]q[0]` = `0110`. Or if it's `q[0]q[1]q[2]q[3]` = `0110`, that means `q[0]=0, q[1]=1, q[2]=1, q[3]=0`. In either ordering, the result is 0110!
        *   Let's use $|q_3 q_2 q_1 q_0\rangle$ notation in Dirac: initial $|0000\rangle$.
        *   Apply $X(q_2)$: state becomes $|0, 1, 0, 0\rangle$.
        *   Apply $CNOT(q_2, q_1)$: control $q_2$ is 1, so target $q_1$ flips to 1. State becomes $|0, 1, 1, 0\rangle$.
        *   Measuring all gives $|0110\rangle$ with probability 1.0.

3.  **Draft the Reasoning:**
    *   **Goal:** Set q[2] to |1> and entangle/toggle q[1] using CNOT, then measure all 4 qubits.
    *   **Qubits:** 4 qubits (`q[0]` to `q[3]`), all measured.
    *   **Evolution:**
        1.  Start in $|0000\rangle$.
        2.  $X(q[2])$ flips the 3rd qubit (assuming $

## isqTrain/4698

- task_id: `isqTrain/4698`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3144`

### Prompt

这两个isQ程序是等价的吗？

程序A：
```isq
import std;
qbit q[1];

procedure main() {
    X(q[0]);
    S(q[0]);
    S(q[0]);
    X(q[0]); // additional bit flip
    M(q[0]);
}

```

程序B：
```isq
import std;
qbit q[1];

procedure main() {
    X(q[0]);
    Z(q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. Program A applies an X gate, two S gates (which combine to act as a Z gate), and an additional X gate, evolving the initial state |0> to -|0>.
2. Program B applies an X gate followed by a Z gate, evolving the initial state |0> to -|1>.
3. The key difference is the final X gate in Program A, which flips the qubit state back to the |0> state (up to a global phase of -1).
4. The measurement probabilities are different because the qubits are in orthogonal states: Program A results in a 100% probability of measuring 0, whereas Program B results in a 100% probability of measuring 1.
5. Verdict: No

### Reference answer

{'equivalent': False, 'explanation': 'After adding X gate to Program A, the programs produce different probability distributions.', 'probs_a': {'0': 1.0}, 'probs_b': {'1': 1.0}}

## isqTrain/1847

- task_id: `isqTrain/1847`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `1435`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[3];
procedure main() {
    X(q[0]); X(q[1]);
    ctrl ctrl X(q[0], q[1], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes three qubits to the state |000⟩.
2. `X(q[0])` and `X(q[1])` flip the first two qubits, changing the state to |110⟩.
3. `ctrl ctrl X(q[0], q[1], q[2])` applies a Toffoli (Toffoli) gate. Since both control qubits (q[0] and q[1]) are in the |1⟩ state, the target qubit (q[2]) is flipped from |0⟩ to |1⟩.
4. The quantum state evolves to |111⟩.
5. Measuring the qubits in the computational basis will deterministically yield the state |111⟩.

Predicted probability distribution: {'111': 1.0}

### Reference answer

{'predicted_probs': {'111': 1.0}, 'explanation': 'Toffoli on |110⟩ flips target to |111⟩. P(|111⟩) = 1.0 at index 7.'}
