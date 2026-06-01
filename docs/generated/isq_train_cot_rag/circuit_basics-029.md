# ISQ training COT RAG corpus: circuit_basics shard 29

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1318

- task_id: `isqTrain/1318`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `1597`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
qbit q[2];

procedure main() {
    H(q[0]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes two qubits in the ground state |00> and applies a Hadamard gate to `q[0]`.
2. The Hadamard gate puts `q[0]` into an equal superposition, evolving the system state to (|00> + |10>)/√2.
3. Qubit `q[1]` remains untouched and stays in the |0> state.
4. Measuring both qubits collapses the superposition, yielding either |00> or |10> with equal likelihood.

Predicted probability distribution: {|00>: 0.5, |10>: 0.5}

### Reference answer

{'predicted_probs': {'0': 0.5, '2': 0.5}, 'explanation': 'Parametric variant of isqEval/472. Dimension: qubit_variant: q[1] -> q[2].'}

## isqTrain/1618

- task_id: `isqTrain/1618`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `data_encoding_qml`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `231`

### Prompt

I need an isQ program to Apply Ry(pi*8/8) to each of 3 qubits and measure all.

### Chain-of-thought reasoning

## Reasoning
1. The goal is to apply an $R_y(\pi)$ rotation to 3 independent qubits and measure them.
2. The circuit requires 3 qubits ($q_0, q_1, q_2$), all of which are measured.
3. All qubits start in the initial state $|000\rangle$. 
4. The gate $R_y(\pi)$ rotates the state $|0\rangle$ to $|1\rangle$ (up to an unobservable global phase of $-i$).
5. Applying $R_y(\pi)$ sequentially to $q_0, q_1,$ and $q_2$ evolves the system state from $|000\rangle \rightarrow |100\rangle \rightarrow |110\rangle \rightarrow |111\rangle$.
6. The final state is exactly $|111\rangle$, so measuring all qubits guarantees the outcome 111 with 100% probability.

## isqTrain/1651

- task_id: `isqTrain/1651`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5023`

### Prompt

Write an isQ program that Apply Rx(pi) to a qubit in state |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply an Rx rotation of π to |0> and measure the resulting state.
2. One qubit is required, and it is measured.
3. Initial state is |0>. Applying Rx(π) transforms the state to -i|1>.
4. Measuring this state yields the result |1> with probability 1.0.

## isqTrain/1812

- task_id: `isqTrain/1812`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3722`

### Prompt

Create an isQ quantum circuit that Apply Ry(pi*2/6) to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. The goal is to apply an $R_y(\pi/3)$ rotation to the initial $|0\rangle$ state and measure the resulting qubit.
2. The circuit requires 1 qubit, which is measured.
3. Starting in $|0\rangle$, applying $R_y(\pi/3)$ transforms the state to $\cos(\pi/6)|0\rangle + \sin(\pi/6)|1\rangle = \frac{\sqrt{3}}{2}|0\rangle + \frac{1}{2}|1\rangle$.
4. The measurement probabilities are the squared magnitudes of the amplitudes: $P(|0\rangle) = (\sqrt{3}/2)^2 = 0.75$ and $P(|1\rangle) = (1/2)^2 = 0.25$.

## isqTrain/1600

- task_id: `isqTrain/1600`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3893`

### Prompt

Implement the following in isQ: Prepare |1> then apply Rx(2pi/3). Measure.

### Chain-of-thought reasoning

## Reasoning
1.  **Goal**: Prepare the |1> state and apply an Rx rotation of 2π/3.
2.  **Qubits**: 1 qubit is required and measured.
3.  **Evolution**:
    *   Initialize to |0>.
    *   Apply X: |0> becomes |1>.
    *   Apply Rx(2π/3): Using Rx(θ)|1> = cos(θ/2)|1> - i·sin(θ/2)|0>, with θ/2 = π/3, the state becomes (1/2)|1> - i(√3/2)|0>.
4.  **Probabilities**: Measuring the final state yields P(|0>) = |-i√3/2|² = 0.75 and P(|1>) = |1/2|² = 0.25.

## isqTrain/1602

- task_id: `isqTrain/1602`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2733`

### Prompt

Help me write isQ code that Prepare |1> then apply Ry(pi/2). Measure.

### Chain-of-thought reasoning

## Reasoning
Goal: Initialize a qubit to |1>, apply an Ry(pi/2) rotation, and measure it.
1. The circuit requires 1 qubit, which is measured at the end.
2. Starting in the ground state |0⟩, the X gate flips the state to |1⟩.
3. Applying Ry(θ) to |1⟩ yields -sin(θ/2)|0⟩ + cos(θ/2)|1⟩. For θ = π/2, this becomes -(1/√2)|0⟩ + (1/√2)|1⟩.
4. The probabilities are determined by the squared amplitudes, resulting in a 50% chance for |0⟩ and a 50% chance for |1⟩.
