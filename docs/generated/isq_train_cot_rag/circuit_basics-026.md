# ISQ training COT RAG corpus: circuit_basics shard 26

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1585

- task_id: `isqTrain/1585`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `4868`

### Prompt

Write an isQ program that On 4 qubits, set q[3]=|1> and apply CNOT with control=q[3], target=q[0]. Measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare a CNOT entangled state with q[3] as control and q[0] as target, then measure all qubits.
2. **Qubits**: 4 qubits are used (q[0], q[1], q[2], q[3]), and all are measured.
3. **Evolution**:
   - Initialize to |0000>.
   - Apply X to q[3]: state becomes |0001>.
   - Apply CNOT(q[3], q[0]): since the control q[3] is |1>, the target q[0] is flipped from |0> to |1>, resulting in |1001>.
4. **Probabilities**: The final state |1001> yields a deterministic measurement outcome corresponding to |1001> (probability 1.0).

## isqTrain/4717

- task_id: `isqTrain/4717`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `superposition`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4093`

### Prompt

Are these two quantum circuits equivalent in terms of measurement output?

Circuit 1:
```isq
import std;
qbit q[1];

procedure main() {
    Ry(pi/4.0, q[0]);
    X(q[0]); // additional bit flip
    M(q[0]);
}

```

Circuit 2:
```isq
import std;
qbit q[1];

procedure main() {
    Ry(pi/2.0, q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** initializes the state to $|0\rangle$, applies an $R_y(\pi/4)$ rotation, and then applies an $X$ gate before measurement.
2. **Program B** initializes the state to $|0\rangle$ and applies an $R_y(\pi/2)$ rotation before measurement.
3. **Key Difference**: The $X$ gate in Program A swaps the amplitudes of the $|0\rangle$ and $|1\rangle$ states, effectively mapping $R_y(\pi/4)|0\rangle$ to $\sin(\pi/8)|0\rangle + \cos(\pi/8)|1\rangle$, whereas Program B results in the equal superposition $\frac{1}{\sqrt{2}}|0\rangle + \frac{1}{\sqrt{2}}|1\rangle$.
4. **Probabilities**: Program A yields measurement probabilities $P(0) = \sin^2(\pi/8) \approx 14.6\%$ and $P(1) = \cos^2(\pi/8) \approx 85.4\%$. Program B yields $P(0) = 50\%$ and $P(1) = 50\%$.
5. **Verdict**: The probability distributions are different because $X R_y(\pi/4) \neq R

### Reference answer

{'equivalent': False, 'explanation': 'After adding X gate to Program A, the programs produce different probability distributions.', 'probs_a': {'0': 0.146447, '1': 0.853553}, 'probs_b': {'0': 0.5, '1': 0.5}}

## isqTrain/1834

- task_id: `isqTrain/1834`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4049`

### Prompt

用isQ实现Apply the gate sequence HXHZ on |0> and measure.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply the gate sequence H-X-H-Z on a single qubit initialized to |0⟩, then measure.

Quantum state evolution:
1. Start: |0⟩
2. H: |0⟩ → |+⟩ = (|0⟩ + |1⟩)/√2
3. X: |+⟩ → X(|+⟩) = (|1⟩ + |0⟩)/√2 = |+⟩
4. H: |+⟩ → |0⟩
5. Z: |0⟩ → |0⟩

Final state is |0⟩, so measurement yields 0 with 100% probability.

## isqTrain/1757

- task_id: `isqTrain/1757`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `difficult`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `4519`

### Prompt

实现以下量子计算任务（使用isQ）：Start with |100000> and use CNOT fan-out (q[0] controls all others) on 6 qubits. All should become |1>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Initialize qubits to |100000⟩ and use CNOT fan-out to propagate the |1⟩ state from q[0] to all other qubits, resulting in |111111⟩.
2. **Qubits**: 6 qubits are used, and all are measured.
3. **State Evolution**:
   - Initial state is |000000⟩. X(q[0]) changes it to |100000⟩.
   - CNOT(q[0], q[1]) flips q[1], updating state to |110000⟩.
   - CNOT(q[0], q[2]) flips q[2], updating state to |111000⟩.
   - CNOT(q[0], q[3]) flips q[3], updating state to |111100⟩.
   - CNOT(q[0], q[4]) flips q[4], updating state to |111110⟩.
   - CNOT(q[0], q[5]) flips q[5], resulting in final state |111111⟩.
4. **Probabilities**: The final state is purely |111111⟩, so measurement yields a 100% probability for the outcome `111111`.

## isqTrain/1813

- task_id: `isqTrain/1813`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `942`

### Prompt

Help me write isQ code that Apply Ry(pi*3/6) to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
The goal is to initialize a qubit in the |0> state, apply a Y-rotation of angle pi/2 (equivalent to pi*3/6), and measure the result.
One qubit is needed, and it is the one measured.
Starting in the initial state |0>, the Ry(pi/2) gate transforms the state into cos(pi/4)|0> + sin(pi/4)|1>, which equals (1/sqrt(2))|0> + (1/sqrt(2))|1>.
Because the final state is in an equal superposition, the probability of measuring |0> is |1/sqrt(2)|^2 = 0.5 and the probability of measuring |1> is |1/sqrt(2)|^2 = 0.5.

## isqTrain/4739

- task_id: `isqTrain/4739`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `5322`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    S(q[0]);
    H(q[0]);
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations applied:** H, S, H, X on a single qubit `q[0]`.
2. **Initial state:** The qubit starts in the ground state |0>.
3. **State evolution:**
   - `H(q[0])`: Transitions to |+> = (1/√2)|0> + (1/√2)|1>.
   - `S(q[0])`: Applies a phase of `i` to |1>, yielding (1/√2)|0> + (i/√2)|1>.
   - `H(q[0])`: Transforms to (1/2)(|0> + |1>) + (i/2)(|0> - |1>) = (1+i)/2 |0> + (1-i)/2 |1>.
   - `X(q[0])`: Flips the basis states, resulting in (1-i)/2 |0> + (1+i)/2 |1>.
4. **Final state:** The state before measurement has amplitudes `(1-i)/2` for |0> and `(1+i)/2` for |1>.
5. **Measurement probabilities:** The probability of measuring |0> is |(1-i)/2|²

### Reference answer

{'predicted_probs': {'0': 0.5, '1': 0.5}, 'explanation': 'This isQ program operates on 1 qubit(s). The measurement probability distribution is: P(|0>) = 0.5000, P(|1>) = 0.5000.'}

## isqTrain/4710

- task_id: `isqTrain/4710`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `399`

### Prompt

Determine if these two isQ implementations are functionally equivalent:

Version A:
```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    X(q[0]); // additional bit flip
    M(q[0]);
}

```

Version B:
```isq
import std;
qbit q[1];

procedure main() {
    X(q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A**: Applies an H gate to $|0\rangle$ to create $|+\rangle$, followed by an X gate. Since $X|+\rangle = |+\rangle$, the final state remains in an equal superposition.
2. **Program B**: Applies only an X gate to $|0\rangle$, flipping the state to $|1\rangle$.
3. **Key difference**: Program A includes an H gate that creates a superposition, whereas Program B remains in a definite computational basis state.
4. **Probabilities**: Program A measures $|0\rangle$ and $|1\rangle$ with 50% probability each. Program B measures $|1\rangle$ with 100% probability. 
5. **Verdict**: Not equivalent.

### Reference answer

{'equivalent': False, 'explanation': 'After adding X gate to Program A, the programs produce different probability distributions.', 'probs_a': {'0': 0.5, '1': 0.5}, 'probs_b': {'1': 1.0}}

## isqTrain/1814

- task_id: `isqTrain/1814`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5487`

### Prompt

实现以下量子计算任务（使用isQ）：Apply Ry(pi*4/6) to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. The goal is to apply a Y-rotation of angle $2\pi/3$ ($4\pi/6$) to a qubit initialized to the ground state and measure it.
2. The circuit requires exactly 1 qubit, which is measured

## isqTrain/1472

- task_id: `isqTrain/1472`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2754`

### Prompt

请用isQ语言编写一个量子电路：Rotate a qubit from |0> by Ry(pi/6) and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Rotate a single qubit initialized to |0> by an angle of pi/6 around the Y-axis and measure the resulting state.
2. **Qubits**: The circuit uses 1 qubit, which is measured.
3. **State Evolution**:
   - Initialize the qubit to the ground state: $|0\rangle$.
   - Apply the $R_y(\pi/6)$ rotation. The $R_y(\theta)$ gate maps $|0\rangle \to \cos(\theta/2)|0\rangle + \sin(\theta/2)|1\rangle$. Thus, the state becomes

## isqTrain/1578

- task_id: `isqTrain/1578`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `4910`

### Prompt

帮我写一个isQ程序：On 4 qubits, set q[0]=|1> and apply CNOT with control=q[0], target=q[2]. Measure all.

### Chain-of-thought reasoning

## Reasoning
The goal is to initialize 4 qubits, set q[0] to |1>, apply a CNOT gate with q[0] as the control and q[2] as the target, and measure all qubits.
All 4 qubits (q[0] to q[3]) are used and subsequently measured.
State evolution:
1. The system begins in the initialized state |0000>.
2. Applying the X gate to q[0] flips its state from |0> to |1>, evolving the system to |1000>.
3. Applying the CNOT gate with control q[0] and target q[2] flips q[2] from |0> to |1> because the control is in the |1> state. This yields the final entangled state |1010>.
Since the final state is deterministically |1010>, measuring the qubits will yield exactly the bitstring 1010 with a probability of 1.0.
