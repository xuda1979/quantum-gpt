# ISQ training COT RAG corpus: circuit_basics shard 8

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4660

- task_id: `isqTrain/4660`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `superposition`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `569`

### Prompt

这两个isQ程序是等价的吗？

程序A：
```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    M(q[0]);
}

```

程序B：
```isq
import std;
qbit q[1];

procedure main() {
    Rz(pi, q[0]);
    Ry(pi/2.0, q[0]);
    H(q[0]); // add superposition
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** initializes qubit to |0> and applies a Hadamard (H) gate, transitioning the state to |+> (an equal superposition of |0> and |1>).
2. **Program B** starts by applying Rz(pi) to |0>, which only adds a global phase (-i|0>). It then applies Ry(pi/2.0), rotating the state to |+>. Finally, it applies the H gate, which maps |+> back to |0>.
3. **The key difference** is that Program B applies additional rotations before the H gate, effectively acting as H * Ry(pi/2) * Rz(pi) instead of just H.
4. **Measurement probabilities**: Program A yields a 50% probability for both |0> and |1>, whereas Program B yields a 100% probability of measuring |0> and 0% for |1>.
5. **Verdict**: No

### Reference answer

{'equivalent': False, 'explanation': 'After adding H gate to Program B, the programs produce different probability distributions.', 'probs_a': {'0': 0.5, '1': 0.5}, 'probs_b': {'0': 1.0}}

## isqTrain/1799

- task_id: `isqTrain/1799`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5386`

### Prompt

Implement a quantum circuit in isQ: Apply Rx(pi*1/6) to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply an Rx rotation by π/6 to |0⟩ and compute measurement probabilities.
2. One qubit is required and measured.
3. Initial state |0⟩ evolves under Rx(π/6): |0⟩ → cos(π/12)|0⟩ − i·sin(π/12)|1⟩.
4. Measurement probabilities are P(|0⟩) = cos²(π/12) ≈ 0.9330 and P(|1⟩) = sin²(π/12) ≈ 0.0670.

## isqTrain/4699

- task_id: `isqTrain/4699`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5777`

### Prompt

Do these two isQ programs produce the same measurement results?

Program A:
```isq
import std;
qbit q[1];

procedure main() {
    X(q[0]);
    S(q[0]);
    S(q[0]);
    M(q[0]);
}

```

Program B:
```isq
import std;
qbit q[1];

procedure main() {
    X(q[0]);
    Z(q[0]);
    H(q[0]); // add superposition
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. Program A applies an X gate to initialize the qubit to |1>. The subsequent two S gates act as a Z gate, resulting in the final state -|1> (a global phase shift). Measurement yields |1> with 100% probability.
2. Program B applies X and Z gates to reach -|1>, but then applies an H gate, transforming the state to (-|0> + |1>)/√2.
3. The key difference is the H gate in Program B, which introduces superposition.
4. Program A's measurement results in P(1) = 100%, whereas Program B's measurement results in P(0) = 50% and P(1) = 50%.
5. Verdict: No

### Reference answer

{'equivalent': False, 'explanation': 'After adding H gate to Program B, the programs produce different probability distributions.', 'probs_a': {'1': 1.0}, 'probs_b': {'0': 0.5, '1': 0.5}}

## isqTrain/644

- task_id: `isqTrain/644`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `entanglement`, `measurement_order`
- source: `isq_train_cot`
- dataset_index: `196`

### Prompt

Create an isQ quantum circuit that implements the measurement_order_test pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a Bell state, measure one qubit, then demonstrate gate cancellation with an X-X identity pair before measuring the second qubit.

2. **Qubits**: 2 qubits (q[0], q[1]), both measured.

3. **State evolution**:
   - Initial: |00>
   - H(q[0]): (|0> + |1>)/√2 ⊗ |0> = (|00> + |10>)/√2
   - CNOT(q[0], q[1]): (|00> + |11>)/√2 (Bell state)
   - M(q[1]): Collapses to |00> (prob 0.5) or |11> (prob 0.5)
   - X(q[0]); X(q[0]): X² = I, net identity — no state change
   - M(q[0]): Measures correlated value matching q[1]

4. **Probabilities**: The Bell state correlations ensure both qubits always match. With X-X cancelling to identity, measurements yield |00> or |11> each with 50% probability: {|00>: 0.5, |11>: 0.5}.

## isqTrain/1560

- task_id: `isqTrain/1560`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1776`

### Prompt

实现以下量子计算任务（使用isQ）：Apply X then Y to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
The circuit applies the Pauli-X gate followed by the Pauli-Y gate to a single qubit initialized in the |0> state, then measures it.
The system requires 1 qubit which is measured at the end.
Initial state is |0>.
Applying the X gate flips the state to |1>.
Applying the Y gate to |1> yields the state i|0>.
Because measurement probabilities are unaffected by the global phase factor i, the final state is effectively |0>, resulting in a measurement probability of {|0>: 1.0}.

## isqTrain/1575

- task_id: `isqTrain/1575`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `867`

### Prompt

请用isQ语言编写一个量子电路：On 3 qubits, set q[2]=|1> and apply CNOT with control=q[2], target=q[0]. Measure all.

### Chain-of-thought reasoning

## Reasoning
1. The goal is to prepare q[2] in the |1> state and conditionally flip q[0] using a CNOT gate.
2. The circuit uses 3 qubits (q[0], q[1], q[2]), and all are measured at the end.
3. Starting in the initial state |000>, applying the X gate to q[2] flips it to |1>, evolving the state to |100>.
4. Applying CNOT with control=q[2] and target=q[0] flips q[0] from |0> to |1> because the control q[2

## isqTrain/1469

- task_id: `isqTrain/1469`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `4597`

### Prompt

Implement the following in isQ: Apply the gate sequence H+X to 2 qubits starting from |00>. Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply an H gate to the first qubit and an X gate to the second, starting from |00>, then measure both.
2. Qubits: 2 qubits are needed, and both are measured.
3. Evolution:
   - Start in the initial state |00>.
   - H(q[0]) puts the first qubit into an equal superposition, yielding (|00> + |10>)/√2.
   - X(q[1]) flips the second qubit, resulting in the final state (|01> + |11>)/√2.
4. Probabilities: The final state is an equal superposition of |01> and |11>. Consequently, measurement yields |01> with probability 0.5 and |11> with probability 0.5.

## isqTrain/1621

- task_id: `isqTrain/1621`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `4690`

### Prompt

Write isQ code for the following quantum task: Apply SWAP(q[0],q[2]) twice (identity) on 3 qubits with q[0]=|1>. Measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply swap (three-CNOT decomposition)(q[0], q[2]) twice on 3 qubits with q[0]=|1>, then measure all.
2. **Qubits**: 3 qubits q[0], q[1], q[2]; all measured.
3. **State evolution**:
   - |000> → X(q[0]) → |100>
   - |100> → swap (three-CNOT decomposition)(q[0], q[2]) → |001>
   - |001> → swap (three-CNOT decomposition)(q[0], q[2]) → |100>
4. **Final state**: |100>, so measurement yields |100> with probability 1.0. The two SWAPs compose to identity.

## isqTrain/4735

- task_id: `isqTrain/4735`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5593`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
qbit q[1];

procedure main() {
    Rx(pi/3.0, q[0]);
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The qubit q[0] starts in the initial state |0>.
2. Applying `Rx(pi/3.0)` rotates the state around the X-axis by $\pi/3$, evolving the state to $\cos(\pi/6)|0\rangle - i\sin(\pi/6)|1\rangle = \frac{\sqrt{3}}{2}|0\rangle - \frac{i}{2}|1\rangle$.
3. Applying the Pauli-X gate `X(q[0])` flips the basis states, resulting in the final pre-measurement state: $-\frac{i}{2}|0\rangle + \frac{\sqrt{3}}{2}|1\rangle$.
4. Calculating the absolute squares of the amplitudes gives the probability of |0> as $|-i/2|^2 = 0.25$ and the probability of |1> as $|\sqrt{3}/2|^2 = 0.75$.

Predicted probability distribution: {|0>: 0.25, |1>: 0.75}

### Reference answer

{'predicted_probs': {'0': 0.25, '1': 0.75}, 'explanation': 'This isQ program operates on 1 qubit(s). The measurement probability distribution is: P(|0>) = 0.2500, P(|1>) = 0.7500.'}

## isqTrain/2629

- task_id: `isqTrain/2629`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `global_phase`, `superposition`
- source: `isq_train_cot`
- dataset_index: `775`

### Prompt

Are these two quantum circuits equivalent in terms of measurement output?

Circuit 1:
```isq
import std;

qbit q[1];

procedure main() {
    H(q[0]);
    GPhase(1.57079632679);
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
    GPhase(1.57079632679);
    H(q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A**: Applies a Hadamard gate (H), followed by a global phase of $\pi/2$ (`GPhase(1.57079632679)`), another Hadamard gate (H), and finally measures the qubit.
2. **Program B**: Applies a trivial global phase of 0 (`GPhase(0.0)`), then exactly matches Program A with an H gate, a `GPhase(1.57079632679)`, another H gate, and measurement.
3. **Key difference**: Program B includes an additional `GPhase(0.0)` operation at the very beginning of the circuit.
4. **Probability equivalence**: The `GPhase(0.0)` gate applies a phase factor of $e^{i \cdot 0} = 1$, which acts as an identity operation. Both programs map the initial $|0\rangle$ state to the exact same final state ($i|0\rangle$) before measurement. Therefore, the measurement probability distributions are exactly the same.
5. **Verdict**: Yes

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}
