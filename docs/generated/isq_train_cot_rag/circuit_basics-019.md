# ISQ training COT RAG corpus: circuit_basics shard 19

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1609

- task_id: `isqTrain/1609`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `data_encoding_qml`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2317`

### Prompt

Code this in isQ: Apply Ry(pi*7/8) to each of 2 qubits and measure all.

### Chain-of-thought reasoning

## Reasoning
1. The circuit applies an $R_y(7\pi/8)$ rotation to two independent qubits initialized to $|0\rangle$ and measures them.
2. Two qubits are required, and both are measured.
3. The initial state $|00\rangle$ transitions to $(\cos(7\pi/

## isqTrain/4742

- task_id: `isqTrain/4742`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `5488`

### Prompt

Do these two isQ programs produce the same measurement results?

Program A:
```isq
import std;
qbit q[3];

procedure main() {
    X(q[0]);
    X(q[1]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

Program B:
```isq
import std;
qbit q[3];

procedure main() {
    X(q[0]);
    X(q[2]);
    H(q[0]); // add superposition
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** initializes 3 qubits to |000>, applies X gates to q[0] and q[1], changing the state to |110>, and then measures the qubits.
2. **Program B** initializes 3 qubits to |000>, applies an X gate to q[0] and q[2] (resulting in |101>), and then applies an H gate to q[0], resulting in the superposition (|001> - |101>) / √2.
3. **Key Difference**: Program A deterministically prepares |110>, whereas Program B prepares a superposition of |001> and |101>.
4. **Probabilities**: Measurement of Program A yields bitstring 110 with 100% probability. Measurement of Program B yields bitstrings 001 and 101, each with 50% probability. The distributions are strictly disjoint.
5. **Verdict**: Equivalent: False

### Reference answer

{'equivalent': False, 'explanation': 'After adding H gate to Program B, the programs produce different probability distributions.', 'probs_a': {'110': 1.0}, 'probs_b': {'001': 0.5, '101': 0.5}}

## isqTrain/1479

- task_id: `isqTrain/1479`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `data_encoding_qml`
- source: `isq_train_cot`
- dataset_index: `1321`

### Prompt

Code this in isQ: Encode the classical value 6/16 into a qubit using angle encoding (Ry rotation with angle pi*6/16). Measure.

### Chain-of-thought reasoning

## Reasoning
1. The goal is to encode the classical value 6/16 into a single qubit using an Ry rotation.
2. One qubit is needed, and it is measured at the end of the circuit.
3. Starting in the initial state |0>, the Ry(3π/8) gate rotates the state around the Y-axis of the Bloch sphere, evolving it to cos(3π/16)|0> + sin(3π/16)|1>.
4. Measuring this state yields the predicted output: P(|0>) = cos²(3π/16) ≈ 0.6913 and P(|1>) = sin²(3π/16) ≈ 0.3087.

## isqTrain/1817

- task_id: `isqTrain/1817`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4705`

### Prompt

Implement the following in isQ: Apply Ry(pi*7/6) to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply rotation Ry(7π/6) to |0⟩ and measure the resulting state.
One qubit is needed (q[0]), and it is measured.

State evolution:
- Initial: |ψ⟩ = |0⟩
- After Ry(7π/6): |ψ⟩ = cos(7π/12)|0⟩ + sin(7π/12)|1⟩

The Ry(θ) gate maps |0⟩ → cos(θ/2)|0⟩ + sin(θ/2)|1⟩. With θ = 7π/6, we get θ/2 = 7π/12 = 105°. Thus cos(7π/12) ≈ -0.2588 and sin(7π/12) ≈ 0.9659. The measurement probabilities are P(|0⟩) = cos²(7π/12) ≈ 0.06699 and P(|1⟩) = sin²(7π/12) ≈ 0.93301.

## isqTrain/1481

- task_id: `isqTrain/1481`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `data_encoding_qml`
- source: `isq_train_cot`
- dataset_index: `1545`

### Prompt

Write isQ code for the following quantum task: Encode the classical value 8/16 into a qubit using angle encoding (Ry rotation with angle pi*8/16). Measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Encode classical value 8/16 into a qubit using angle encoding with Ry rotation, then measure.
2. **Qubits**: 1 qubit (q[0]), which is measured.
3. **State evolution**:
   - Initial state: |0>
   - Apply Ry(π × 8/16, q[0]) = Ry(π/2, q[0])
   - Ry(θ) = cos(θ/2)|0> + sin(θ/2)|1>, so for θ = π/2: cos(π/4)|0> + sin(π/4)|1> = |+>
4. **Expected probabilities**: The |+> state yields P(|0>) = |1/√2|² = 0.5 and P(|1>) = |1/√2|² = 0.5.

## isqTrain/4758

- task_id: `isqTrain/4758`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `1654`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    Rz(pi/4.0, q[0]);
    H(q[0]);
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the request:**
    *   Task: output_prediction for an isQ program.
    *   Program: `H(q[0]); Rz(pi/4, q[0]); H(q[0]); X(q[0]); M(q[0]);`
    *   Constraints: Generate concise, precise step-by-step reasoning using Dirac notation. Length 3-15 lines. Output format: ONLY the analysis starting with "## Circuit Analysis", ending with the predicted probability distribution.

2.  **Analyze the circuit:**
    *   Initial state: $|0\rangle$
    *   `H(q[0])`: State becomes $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$
    *   `Rz(pi/4.0, q[0])`:
        $Rz(\theta) = e^{-i\theta/2}|0\rangle\langle0| + e^{i\theta/2}|1\rangle\langle1|$ (up to global phase). Let's use the standard matrix:
        $Rz(\pi/4) = \begin{pmatrix} e^{-i\pi/8} & 0 \\ 0 & e^{i\pi/8} \end{pmatrix}$
        State becomes $\frac{1}{\sqrt{2}}(e^{-i\pi/8}|0\rangle + e^{i\pi/8}|1\rangle)$
    *   `H(q[0])`:
        $H \frac{1}{\sqrt{2}}(e^{-i\pi/8}|0\rangle + e^{i\pi/8}|1\rangle)$
        $= \frac{1}{2} ((e^{-i\pi/8} + e^{i\pi/8})|0\rangle + (e^{-i\pi/8} - e^{i\pi/8})|1\rangle)$
        Using Euler's formula: $e^{ix} + e^{-ix} = 2\cos(x)$, $e^{ix} - e^{-ix} = 2i\sin(x)$.
        $= \cos(\pi/8)|0\rangle - i\sin(\pi/8)|1\rangle$
    *   `X(q[0])`:
        $X(\cos(\pi/8)|0\rangle - i\sin(\pi/8)|1\rangle) = -i\sin(\pi/8)|0\rangle + \cos(\pi/8)|1\rangle$

3.  **Calculate probabilities:**
    *   $P(|0\rangle) = |-i\sin(\pi/8)|^2 = \sin^2(\pi/8) = \frac{1 - \cos(\pi/4)}{2} = \frac{1 - 1/\sqrt{2}}{2} \approx \frac{1 - 0.70710678}{2} = 0.1464466$
    *   $P(|1\rangle) = |\cos(\pi/8)|^2 = \cos^2(\pi/8) = \frac{1 + \cos(\pi/4)}{2} = \frac{1 + 1/\sqrt{2}}{2} \approx \frac{1 + 0.70710678}{2} = 0.8535534$

4.  **Format the output:**
    *   Start with "## Circuit Analysis"
    *   Keep it concise (3-15 lines).
    *   Use Dirac notation.
    *   End with the probability distribution.

5.  **Drafting the response:**
    ## Circuit Analysis
    1. **Initial state**: $|0\rangle$
    2. **H gate**: Transforms state to $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
    3. **$R_z(\pi/4)$ gate**: Applies a phase rotation, resulting in $\frac{1}{\sqrt{2}}(e^{-i\pi/8}|0\rangle + e^{i\pi/8}|1\rangle)$.
    4. **H gate**: Interferes the amplitudes. The state becomes $\cos(\pi/8)|0\rangle - i\sin(\pi/8)|1\rangle$.
    5. **X gate**: Flips the computational basis states, yielding the final state $-i\sin(\pi/8)|0\rangle + \cos(\pi/8)|1\rangle$.
    6. **Measurement**: Probabilities are determined by the squared magnitudes of the amplitudes.

### Reference answer

{'predicted_probs': {'0': 0.146447, '1': 0.853553}, 'explanation': 'This isQ program operates on 1 qubit(s). The measurement probability distribution is: P(|0>) = 0.1464, P(|1>) = 0.8536.'}

## isqTrain/4656

- task_id: `isqTrain/4656`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2518`

### Prompt

Compare these two isQ programs. Do they give the same probability distribution?

First program:
```isq
import std;
qbit q[1];

procedure main() {
    X(q[0]);
    M(q[0]);
}

```

Second program:
```isq
import std;
qbit q[1];

procedure main() {
    Rx(pi, q[0]);
    H(q[0]); // add superposition
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** applies the X gate to qubit q[0], evolving the initial state |0> to |1>.
2. **Program B** applies Rx(pi) to |0>, resulting in -i|1>. It then applies the H gate, yielding the superposition (-i/sqrt(2))|0> + (i/sqrt(2))|1>.
3. The key difference is the application of the H gate in Program B, which introduces superposition.
4. The measurement probabilities are different. Program A measures |1> with 100% probability. Program B measures |0> and |1> each with 50% probability.
5. Verdict: Not equivalent

### Reference answer

{'equivalent': False, 'explanation': 'After adding H gate to Program B, the programs produce different probability distributions.', 'probs_a': {'1': 1.0}, 'probs_b': {'0': 0.5, '1': 0.5}}

## isqTrain/2509

- task_id: `isqTrain/2509`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `entanglement`, `global_phase`, `isq_syntax_arrays`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3389`

### Prompt

比较这两个量子电路，它们的输出概率分布一样吗？

```isq
import std;
qbit q[2];

procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    Rx(pi/4.0, q[0]);
    M(q[0]); M(q[1]);
}

```

```isq
import std;
qbit q[2];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    H(q[0]);
    CNOT(q[0], q[1]);
    Rx(pi/4.0, q[0]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis

1. **Program A operations**: Initializes two qubits in |00>, applies a Hadamard (H) to q[0], a CNOT from q[0] to q[1], an Rx rotation of pi/4 on q[0], and measures both.
2. **Program B operations**: Executes the exact same sequence of gates as Program A, but precedes them with a GPhase(0.0) operation.
3. **Key difference**: Program B introduces a global phase of 0 radians using GPhase(0.0) before executing the circuit.
4. **Measurement probabilities**: The GPhase(0.0) gate multiplies the quantum state by $e^{i \cdot 0} = 1$. This results in an identical state vector throughout the circuit's execution. Because global phase does not affect measurement probabilities, both programs yield the same distribution.
5. **Verdict**: Equivalent: True

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/1806

- task_id: `isqTrain/1806`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2128`

### Prompt

实现以下量子计算任务（使用isQ）：Apply Rx(pi*8/6) to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply Rx(4π/3) to |0⟩ and compute measurement probabilities.
One qubit is needed and measured.

State evolution:
- Initial: |ψ⟩ = |0⟩
- Rx(θ)|0⟩ = cos(θ/2)|0⟩ - i·sin(θ/2)|1⟩
- With θ = 4π/3: cos(2π/3) = -1/2, sin(2π/3) = √3/2
- Final: |ψ⟩ = -1/2|0⟩ - i·(√3/2)|1⟩

Probabilities: P(|0⟩) = |−1/2|² = 0.25, P(|1⟩) = |−i·√3/2|² = 3/4 = 0.75

## isqTrain/1467

- task_id: `isqTrain/1467`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `3620`

### Prompt

Help me write isQ code that Apply the gate sequence H+H to 2 qubits starting from |00>. Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
The goal is to initialize a uniform superposition across two independent qubits starting in the ground state.
The circuit requires 2 qubits (`q[0]`, `q[1]`), and both are measured at the end.
Initial state is |00>.
Applying H(q[0]) transforms the state to (|00> + |10>) / sqrt(2).
Applying H(q[1]) creates the final state (|00> + |01> + |10> + |11>) / 2.
Since the final state is an equal superposition of all four 2-qubit basis states, the probability of measuring each state (|00>, |01>, |10>, |11>) is |1/2|^2 = 0.25.
