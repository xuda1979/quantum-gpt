# ISQ training COT RAG corpus: circuit_basics shard 5

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4694

- task_id: `isqTrain/4694`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `863`

### Prompt

判断以下两段isQ代码是否产生相同的测量结果：

代码1：
```isq
import std;
qbit q[2];

procedure main() {
    H(q[0]);
    H(q[1]);
    X(q[0]); // additional bit flip
    M(q[0]); M(q[1]);
}

```

代码2：
```isq
import std;
qbit q[2];

procedure main() {
    H(q[1]);
    H(q[0]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis

1. **Program A operations**: Applies a Hadamard gate to both q[0] and q[1], initializing them in a superposition, followed by an X (bit-flip) gate applied to q[0]. 
2. **Program B operations**: Applies a Hadamard gate to both q[1] and q[0], putting both into superposition.
3. **Key difference**: Program A applies an extra X gate to q[0] after the Hadamard gate, which Program B lacks.
4. **Probability equivalence**: The Hadamard gate transforms the initial |0> state into the |+> state, which is an equal superposition of |0> and |1>. Applying an X gate to |+> swaps the amplitudes of |0> and |1>, but since they are equal, the state remains exactly |+>. Thus, both programs result in the identical final state |+>|+>, yielding a uniform 25% probability for each of the 00, 01, 10, and 11 measurement outcomes.
5. **Verdict**: Yes

### Reference answer

{'equivalent': True, 'explanation': 'After adding X gate to Program A, the programs produce the same probability distributions.', 'probs_a': {'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25}, 'probs_b': {'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25}}

## isqTrain/4756

- task_id: `isqTrain/4756`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `168`

### Prompt

这两个isQ程序是等价的吗？

程序A：
```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    Rz(pi/4.0, q[0]);
    H(q[0]);
    X(q[0]); // additional bit flip
    M(q[0]);
}

```

程序B：
```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    Rz(pi/2.0, q[0]);
    H(q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A**: Initializes |0>, applies H, Rz(pi/4), H, and an X gate before measurement.
2. **Program B**: Initializes |0>, applies H, Rz(pi/2), and H before measurement.
3. **Key difference**: Program A uses a different rotation angle (pi/4 vs pi/2) and includes an additional X gate at the end.
4. **Probability comparison**: Program B results in an exact superposition with probabilities P(|0>) = 0.5 and P(|1>) = 0.5. Program A results in P(|0>) ≈ 0.293 and P(|1>) ≈ 0.707.
5. **Verdict**: No

### Reference answer

{'equivalent': False, 'explanation': 'After adding X gate to Program A, the programs produce different probability distributions.', 'probs_a': {'0': 0.146447, '1': 0.853553}, 'probs_b': {'0': 0.5, '1': 0.5}}

## isqTrain/1661

- task_id: `isqTrain/1661`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `measurement_order`
- source: `isq_train_cot`
- dataset_index: `5026`

### Prompt

实现以下量子计算任务（使用isQ）：Put 3 qubits in superposition and measure in reverse order (N-1,...,0).

### Chain-of-thought reasoning

## Reasoning
1. The goal is to create an equal superposition over 3 qubits and measure them in reverse index order.
2. The circuit uses 3 qubits (`q[0], q[1], q[2]`), all of which are initialized to `|0>` and measured.
3. Applying a Hadamard gate to each qubit transforms the initial state `|000>` into `|+>|+>|+> = (1/√8)(|000> + |001> + |010> ... + |111>)`.
4. Measuring in the reverse order `q[2], q[1], q[0]` assigns the measurement outcome of `q[2]` to the highest bit and `q[0]

## isqTrain/1715

- task_id: `isqTrain/1715`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4897`

### Prompt

Implement a quantum circuit in isQ: Apply Rx(pi/2) then Ry(pi/2) to |0>. Measure.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply Rx(π/2) followed by Ry(π/2) to |0⟩ and measure the resulting state.
2. One qubit is needed, and it is measured.
3. State evolution: |0⟩ → Rx(π/2)|0⟩ = (|0⟩ − i|1⟩)/√2 → Ry(π/2)(|0⟩ − i|1⟩)/√2 = ((1+i)|0⟩ + (1−i)|1⟩)/2.
4. Measurement probabilities: P(0) = |(1+i)/2|² = 1/2, P(1) = |(1−i)/2|² = 1/2.

## isqTrain/1775

- task_id: `isqTrain/1775`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `219`

### Prompt

Implement a quantum circuit in isQ: Apply X gate 7 times to |0> and measure. (X^7 = X.)

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply X gate 7 times to a qubit initially in |0> and measure the result.
2. **Qubits**: 1 qubit required, 1 measured.
3. **State evolution**:
   - Initial state: |0>
   - Apply X gate 7 times: X^7 = X since X^2 = I (X flips the state each time).
   - Applying X an odd number of times to |0> results in |1>.
   - Final state: |1>
4. **Probabilities**: The final state is |1>, so the measurement yields |1> with 100% probability.

## isqTrain/1558

- task_id: `isqTrain/1558`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1629`

### Prompt

Implement a quantum circuit in isQ: Apply H then S to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
The goal is to apply a Hadamard (H) gate followed by a Phase (S) gate to a single qubit initialized to |0>, then measure it.
1. Start with the initial state |0>.
2. Applying the H gate puts the qubit into an equal superposition: H|0> = (|0

## isqTrain/4700

- task_id: `isqTrain/4700`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2537`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[1];

procedure main() {
    X(q[0]);
    S(q[0]);
    S(q[0]);
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
- Initial state is |0>. The first X gate flips the state to |1>.
- The sequence of two S gates applies a phase of $i^2 = -1$ to the |1> state, evolving it to $-|1\rangle$.
- The final X gate flips the state back to $-|0\rangle$.
- Since a global phase does not affect measurement probabilities, the state is physically equivalent to |0>.
- Predicted probability distribution: {|0>: 1.0}

### Reference answer

{'predicted_probs': {'0': 1.0}, 'explanation': 'This isQ program operates on 1 qubit(s). The measurement probability distribution is: P(|0>) = 1.0000.'}

## isqTrain/4677

- task_id: `isqTrain/4677`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1985`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
qbit q[1];

procedure main() {
    X(q[0]);
    X(q[0]);
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit starts with one qubit in the initial state |0>.
2. The first X gate flips the state from |0> to |1>.
3. The second X gate flips the state from |1> back to |0>.
4. The third X gate flips the state from |0> to |1> again.
5. The final quantum state before measurement is exactly |1>.

Probability distribution: {|1>: 1.0}

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'This isQ program operates on 1 qubit(s). The measurement probability distribution is: P(|1>) = 1.0000.'}

## isqTrain/1616

- task_id: `isqTrain/1616`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `data_encoding_qml`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `317`

### Prompt

帮我写一个isQ程序：Apply Ry(pi*6/8) to each of 3 qubits and measure all.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Independently rotate each of three qubits around the Y-axis by angle 3π/4 and measure them.
2. Qubits: 3 qubits are used, and all are measured.
3. State Evolution: The circuit starts in the initial state |000>. Applying Ry(3π/4) individually to each qubit maps |0> to cos(3π/8)|0> + sin(3π/8)|1>. The final quantum state is the tensor product (cos(3π/8)|0> + sin(3π/8)|1>)^⊗3.
4. Probabilities: Because the qubits remain unentangled, the probability of measuring any specific bitstring with k zeros and (3-k) ones is exactly cos²(3π/8)^k * sin²(3π/8)^(3-k).

## isqTrain/1571

- task_id: `isqTrain/1571`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3833`

### Prompt

Implement a quantum circuit in isQ: Apply the gate sequence S-H-S to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply S-H-S gate sequence to |0> and measure the resulting state.
2. One qubit is needed (q[0]), which is measured.
3. State evolution:
   - |0> → S|0> = |0> (S leaves |0> unchanged)
   - |0> → H|0> = |+> = (1/√2)(|0> + |1>)
   - |+> → S|+> = (1/√2)(|0> + i|1>) = |i+>
4. Measurement probabilities: P(|0>) = |1/√2|² = 0.5, P(|1>) = |i/√2|² = 0.5. The S gate after H adds a relative phase of i to |1>, but since probabilities depend on squared magnitudes, both outcomes remain equally likely.
