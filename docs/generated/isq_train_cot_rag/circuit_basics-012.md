# ISQ training COT RAG corpus: circuit_basics shard 12

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1655

- task_id: `isqTrain/1655`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2280`

### Prompt

实现以下量子计算任务（使用isQ）：Apply Ry(pi/2) to a qubit in state |0> and measure.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply Ry(π/2) rotation to |0⟩ and measure, creating an equal superposition.
One qubit is needed (q[0]) and is measured.
Initial state: |0⟩. Ry(π/2)|0⟩ = cos(π/4)|0⟩ + sin(π/4)|1⟩ = (|0⟩ + |1⟩)/√2 = |+⟩.
Measuring |+⟩ gives P(|0⟩) = |1/√2|² = 0.5 and P(|1⟩) = |1/√2|² = 0.5.

## isqTrain/4396

- task_id: `isqTrain/4396`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `5748`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[1];

procedure main() {
    // Two Hadamards cancel out: HH = I
    H(q[0]);
    H(q[0]);
    // Measure (returns |0> deterministically)
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit starts with a single qubit initialized to |0>.
2. The first two gates are Hadamards (H). Since HH = I (Identity), they cancel out, leaving the state unchanged at |0>.
3. The next sequence is H, followed by Z, followed by H. It is a known identity that HZH = X (Pauli-X gate).
4. Applying the equivalent X gate to |0> flips the state to |1>.
5. The final measurement measures the qubit in the |1> state with certainty.

Predicted probability distribution: {|1>: 1.0}

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'This isQ program operates on 1 qubit(s). The measurement probability distribution is: P(|1>) = 1.0000.'}

## isqTrain/1489

- task_id: `isqTrain/1489`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `data_encoding_qml`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `458`

### Prompt

请用isQ语言编写一个量子电路：Encode the integer 7 (binary 111) into 3 qubits using basis encoding. Measure all qubits.

### Chain-of-thought reasoning

## Reasoning
The goal is to basis encode the integer 7 (binary 111) into a 3-qubit register and measure the result.
We need 3 qubits (q[0], q[1], q[2]), and all 3 will be measured at the end.
Starting in the initial state |000>, applying an X gate to each qubit flips its state from |0> to |1>.
The state evolution is: |000> -> |001> -> |011> -> |111>.
Since the final quantum state is exactly |111>, measuring all qubits deterministically yields the bitstring '111' with a probability of 1.0.

## isqTrain/1611

- task_id: `isqTrain/1611`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `data_encoding_qml`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1373`

### Prompt

实现以下量子计算任务（使用isQ）：Apply Ry(pi*1/8) to each of 3 qubits and measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Apply the $R_y(\pi/8)$ rotation independently to 3 qubits and measure them.
2. **Qubits:** 3 qubits are needed, and all 3 are measured.
3. **State Evolution:** Starting from $|000\rangle$, applying $R_y(\pi/8)$ to each qubit rotates it around the Y-axis by $\pi/8$, putting each qubit into the state $\cos(\pi/16)|0\rangle + \sin(\pi/16)|1\rangle$. The joint final state is $(\cos(\pi/16)|0\rangle + \sin(\pi/16)|1\rangle)^{\otimes 3}$.
4. **Probabilities:** The probability of measuring a bitstring with $k$ ones is $\cos^{2(3-k)}(\pi/16) \sin^{2k}(\pi/16)$, as the qubits are unentangled.

## isqTrain/1478

- task_id: `isqTrain/1478`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `data_encoding_qml`
- source: `isq_train_cot`
- dataset_index: `4611`

### Prompt

I need an isQ program to Encode the classical value 5/16 into a qubit using angle encoding (Ry rotation with angle pi*5/16). Measure.

### Chain-of-thought reasoning

## Reasoning
Goal: Encode the classical value 5/16 into a single qubit via angle encoding using a Y-rotation.
Qubits: 1 qubit is required and measured.
Evolution: The qubit begins in the initial state |0>.
Rotation: Applying the Ry(5*π/16) gate rotates the state around the Y-axis by the specified angle.
Final State: The quantum state becomes cos(5π/32)|0> + sin(5π/32)|1>.
Probabilities: Measurement yields |0> with probability cos²(5π/32) ≈ 0.7778 and |1> with probability sin²(5π/32) ≈ 0.2222.

## isqTrain/4658

- task_id: `isqTrain/4658`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `superposition`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2289`

### Prompt

Will these two quantum programs produce identical measurement outcomes?

```isq
import std;
qbit q[1];

procedure main() {
    Rz(pi, q[0]);
    Ry(pi/2.0, q[0]);
    M(q[0]);
}

```

vs.

```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

1.  **Analyze Program A:**
    *   Initial state: $|0\rangle$
    *   Gate 1: `Rz(pi, q[0])`. Matrix: $\begin{pmatrix} e^{-i\pi/2} & 0 \\ 0 & e^{i\pi/2} \end{pmatrix} = \begin{pmatrix} -i & 0 \\ 0 & i \end{pmatrix}$. Wait, Rz definition in standard quantum computing is usually $e^{-iZ\theta/2}$. So Rz($\pi$) is $e^{-iZ\pi/2} = \begin{pmatrix} e^{-i\pi/2} & 0 \\ 0 & e^{i\pi/2} \end{pmatrix} = \begin{pmatrix} -i & 0 \\ 0 & i \end{pmatrix}$. Applied to $|0\rangle$, state becomes $-i|0\rangle$.
    *   Gate 2: `Ry(pi/2.0, q[0])`. Matrix: $\begin{pmatrix} \cos(\pi/4) & -\sin(\pi/4) \\ \sin(\pi/4) & \cos(\pi/4) \end{pmatrix} = \frac{1}{\sqrt{2}} \begin{pmatrix} 1 & -1 \\ 1 & 1 \end{pmatrix}$.
    *   Combined operation: $Ry(\pi/2) \cdot Rz(\pi)$.
        $Ry(\pi/2) \cdot Rz(\pi) |0\rangle = \frac{1}{\sqrt{2}} \begin{pmatrix} 1 & -1 \\ 1 & 1 \end{pmatrix} \begin{pmatrix} -i & 0 \\ 0 & i \end{pmatrix} \begin{pmatrix} 1 \\ 0 \end{pmatrix} = \frac{1}{\sqrt{2}} \begin{pmatrix} 1 & -1 \\ 1 & 1 \end{pmatrix} \begin{pmatrix} -i \\ 0 \end{pmatrix} = \frac{-i}{\sqrt{2}} \begin{pmatrix} 1 \\ 1 \end{pmatrix}$.
        This is $|+\rangle$ up to a global phase. The probability of measuring 0 is $|-i/\sqrt{2}|^2 = 1/2$, and measuring 1 is $|-i/\sqrt{2}|^2 = 1/2$.
    *   Wait, is $Rz(\pi) R_y(\pi/2)$? No, the program has `Rz(pi, q[0]); Ry(pi/2.0, q[0]);`. This applies $Rz$ first, then $Ry$. So $Ry(\pi/2) Rz(\pi)$.
    *   Does $Ry(\pi/2) Rz(\pi)$ equal $H$?
        $H = \frac{1}{\sqrt{2}} \begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix}$.
        $Ry(\pi/2) Rz(\pi) = \frac{1}{\sqrt{2}} \begin{pmatrix} 1 & -1 \\ 1 & 1 \end{pmatrix} \begin{pmatrix} -i & 0 \\ 0 & i \end{pmatrix} = \frac{1}{\sqrt{2}} \begin{pmatrix} -i & -i \\ -i & i \end{pmatrix} = \frac{-i}{\sqrt{2}} \begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix} = -i H$.
        Since $-i H$ is $H$ with a global phase of $-i$, the measurement probabilities are identical.

2.  **Analyze Program B:**
    *   Initial state: $|0\rangle$
    *   Gate 1: `H(q[0])`. Matrix: $\frac{1}{\sqrt{2}} \begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix}$.
    *   State becomes $\frac{1}{\sqrt{2}} \begin{pmatrix} 1 \\ 1 \end{pmatrix} = |+\rangle$.
    *   Measurement probability: 0 with prob 0.5, 1 with prob 0.5.

3.  **Compare and Conclude:**

### Reference answer

{'equivalent': True, 'explanation': "H gate and Rz(pi)*Ry(pi/2) produce same measurement distribution Both programs produce the same probability distribution: {'0': 0.5, '1': 0.5}.", 'probs_a': {'0': 0.5, '1': 0.5}, 'probs_b': {'0': 0.5, '1': 0.5}}

## isqTrain/1477

- task_id: `isqTrain/1477`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `data_encoding_qml`
- source: `isq_train_cot`
- dataset_index: `4581`

### Prompt

Write isQ code for the following quantum task: Encode the classical value 4/16 into a qubit using angle encoding (Ry rotation with angle pi*4/16). Measure.

### Chain-of-thought reasoning

## Reasoning
Goal: Encode classical value 4/16 via angle encoding using Ry(π·4/16) rotation on a single qubit and measure it.
Qubits: 1 qubit q[0], which is measured.
State evolution: |0> → Ry(π/4)|0> = cos(π/8)|0> + sin(π/8)|1>
Measurement probabilities: P(|0>) = cos²(π/8) ≈ 0.8536, P(|1>) = sin²(π/8) ≈ 0.1464, consistent with the predicted output.

## isqTrain/646

- task_id: `isqTrain/646`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `entanglement`, `measurement_order`
- source: `isq_train_cot`
- dataset_index: `3776`

### Prompt

Create an isQ quantum circuit that implements the measurement_order_test pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Create a Bell state and measure qubits in reversed order (q[1] first, then q[0]) to demonstrate how measurement ordering affects bitstring indexing.

2. The circuit requires 2 qubits (q[0] and q[1]), both of which are measured.

3. State evolution step-by-step:
   - Initial state: |00>
   - After H(q[0]): (|0> + |1>)/√2 ⊗ |0> = (|00> + |10>)/√2
   - After CNOT(q[0], q[1]): (|00> + |11>)/√2 (Bell state with perfect correlation)

4. With reversed measurement order, q[1] is measured first (becomes higher bit) and q[0] measured second (becomes lower bit). Since the Bell state has perfect correlation (q[0] = q[1] always), both outcomes remain |00> and |11> with equal probability 0.5 each.

## isqTrain/1830

- task_id: `isqTrain/1830`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `2665`

### Prompt

帮我写一个isQ程序：Apply Hadamard gate 7 times to |0> and measure. H^7 = H.

### Chain-of-thought reasoning

## Reasoning
1. The goal is to apply the Hadamard gate seven times to an initial $|0\rangle$ state and measure the resulting qubit.
2. The circuit requires exactly 1 qubit, which is the one measured.
3. Initial state is $|0\rangle$.
4. State evolution: Since the Hadamard gate is its own inverse ($H^2 = I$), applying it 7 times is equivalent to applying it once ($H^7 = H$). Thus, $H^7|0\rangle = H|0\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) = |+\rangle$.
5. Expected probabilities: Measuring the final $|+\rangle$ state in the computational basis yields an equal probability of collapsing to $|0\rangle$ or $|1\rangle$, resulting in probabilities {|0>: 0.5, |1>: 0.5}.

## isqTrain/1563

- task_id: `isqTrain/1563`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5334`

### Prompt

Write isQ code for the following quantum task: Apply S then H to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
- Goal: Apply the S gate followed by the H gate to an initial |0> state and measure the resulting state.
- Qubits: 1 qubit is required, which is measured at the end.
- Evolution: Starting in |0>, the S gate leaves it as |0> (since S|0> = 1|0>). The H gate then transforms it to |+> = (1/√2)(|0> + |1>).
- Probabilities: Measuring the final |+> state yields equal probabilities of 0.5 for both |0> and |1>.
