# ISQ training COT RAG corpus: circuit_basics shard 21

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1807

- task_id: `isqTrain/1807`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3533`

### Prompt

实现以下量子计算任务（使用isQ）：Apply Rx(pi*9/6) to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
The goal is to apply an Rx rotation of 9π/6 to the ground state |0> and measure the resulting state.
This requires 1 global qubit, which is initialized to |0> and measured.
The initial state |0> is rotated by

## isqTrain/1557

- task_id: `isqTrain/1557`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2150`

### Prompt

Write isQ code for the following quantum task: Apply H then Z to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Initialize a qubit to |0>, apply the H (Hadamard) gate followed by the Z gate, and measure the result.
2. Qubits: The circuit requires exactly 1 qubit, which is measured at the end.
3. State evolution:
   - Start in the initial state: |0>
   - Apply H: |0> transforms to the superposition (|0> + |1>) / √2 = |+>
   - Apply Z: |+> transforms to (|0> - |1>) / √2 = |->
4. Probabilities: Measuring the |-> state in the computational (Z) basis collapses it to |0> or |1> with equal probabilities of 0.5 each.

## isqTrain/4733

- task_id: `isqTrain/4733`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3310`

### Prompt

比较这两个量子电路，它们的输出概率分布一样吗？

```isq
import std;
qbit q[1];

procedure main() {
    Rx(pi/3.0, q[0]);
    X(q[0]); // additional bit flip
    M(q[0]);
}

```

```isq
import std;
qbit q[1];

procedure main() {
    Rx(pi/6.0, q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

1.  **Analyze Program A:**
    *   Applies $R_x(\pi/3)$ to $|0\rangle$.
    *   Applies $X$ gate.
    *   Measures the qubit.
    *   $R_x(\theta) = \cos(\theta/2)I - i\sin(\theta/2)X$.
    *   Initial state: $|0\rangle$.
    *   After $R_x(\pi/3)$: $\cos(\pi/6)|0\rangle - i\sin(\pi/6)|1\rangle = \frac{\sqrt{3}}{2}|0\rangle - \frac{i}{2}|1\rangle$.
    *   After $X$: $\frac{\sqrt{3}}{2}|1\rangle - \frac{i}{2}|0\rangle$.
    *   Probability of $|0\rangle$ is $|-i/2|^2 = 1/4$.
    *   Probability of $|1\rangle$ is $|\sqrt{3}/2|^2 = 3/4$.

2.  **Analyze Program B:**
    *   Applies $R_x(\pi/6)$ to $|0\rangle$.
    *   Measures the qubit.
    *   After $R_x(\pi/6)$: $\cos(\pi/12)|0\rangle - i\sin(\pi/12)|1\rangle$.
    *   Probability of $|0\rangle$ is $\cos^2(\pi/12) = \frac{2+\sqrt{3}}{4} \approx 0.933$.
    *   Probability of $|1\rangle$ is $\sin^2(\pi/12) = \frac{2-\sqrt{3}}{4} \approx 0.067$.

3.  **Compare Programs:**
    *   Program A applies $X \cdot R_x(\pi/3)$.
    *   Program B applies $R_x(\pi/6)$.
    *   $X \cdot R_x(\pi/3) = X (\cos(\pi/6)I - i\sin(\pi/6)X) = \cos(\pi/6)X - i\sin(\pi/6)I$.
    *   This matrix is $-i \cdot \begin{pmatrix} \sin(\pi/6) & 0 \\ 0 & \sin(\pi/6) \end{pmatrix} + \begin{pmatrix} 0 & \cos(\pi/6) \\ \cos(\pi/6) & 0 \end{pmatrix} = \begin{pmatrix} -i\sin(\pi/6) & \cos(\pi/6) \\ \cos(\pi/6) & -i\sin(\pi/6) \end{pmatrix}$.
    *   This is essentially a global phase times a specific unitary, but NOT $R_x(\pi/6)$.
    *   Alternatively, $R_x(\theta)$ rotates around the X-axis. The $X$ gate reflects around the X-axis in the Bloch sphere, so $X R_x(\pi/3) X = R_x(\pi/3)$. But $X R_x(\pi/3) = R_x(\pi/3) X$. Wait, $X$ and $R_x$ commute!
    *   Therefore, $X R_x(\pi/3) |0\rangle = X (\cos(\pi/6)|0\rangle - i\sin(\pi/6)|1\rangle) = \cos(\pi/6)|1\rangle - i\sin(\pi/6)|0\rangle$.
    *   $R_x(\pi/6) |0\rangle = \cos(\pi/12)|0\rangle - i\sin(\pi/12)|1\rangle$.
    *   The states are different, and their measurement probabilities are different.

4.  **Draft the explanation:**
    *   Program A applies $R_x(\pi/3)$ followed by an $X$ gate to $|0\rangle$. The resulting state is $\frac{\sqrt{3}}{2}|1\rangle - \frac{i}{2}|0\rangle$. The probabilities are $P(0) = 1/4$ and $P(1) = 3/4$.
    *   Program B applies $R_x(\pi/6)$ to $|0\rangle$. The resulting state is $\cos(\pi/12)|0\rangle - i\sin(\pi/12)|1\rangle$. The probabilities are $P(0) = \cos^2(\pi/12) \approx 0.933$ and $

### Reference answer

{'equivalent': False, 'explanation': 'After adding X gate to Program A, the programs produce different probability distributions.', 'probs_a': {'0': 0.25, '1': 0.75}, 'probs_b': {'0': 0.933013, '1': 0.066987}}

## isqTrain/1659

- task_id: `isqTrain/1659`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `4853`

### Prompt

Help me write isQ code that Apply reverse CNOT chain: q[2]->q[1]->q[0] from |001>.

### Chain-of-thought reasoning

## Reasoning
1. The goal is to prepare the state |001> and propagate the |1> through a reverse CNOT chain (q[2] -> q[1] -> q[0]).
2. The circuit requires 3 qubits (q[0], q[1], q[2]), all of which are measured.
3. Applying X(q[2]) to the initial |000> state yields |001>.
4. The first CNOT(q[2], q[1]) flips q[1] because q[2] is |1>, updating the state to |011>.
5. The second CNOT(q[1], q[0]) flips q[0] because q[1] is |1>, updating the state to |111>.
6. The final state is deterministically |111>,

## isqTrain/1835

- task_id: `isqTrain/1835`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3255`

### Prompt

请用isQ语言编写一个量子电路：Apply the gate sequence ZHXH on |0> and measure.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply the gate sequence ZHXH on initial state |0> and measure the result.

One qubit is needed, and q[0] is measured.

State evolution:
1. Start: |0>
2. Z|0> = |0> (Z leaves |0> unchanged)
3. H|0> = |+> = (|0> + |1>)/√2
4. X|+> = (|1> + |0>)/√2 = |+> (X swaps |0> and |1>, leaving |+> invariant)
5. H|+> = |0> (H is self-inverse, so H|+> returns to |0>)

The final state is |0>, so measurement yields 0 with probability 1.

## isqTrain/645

- task_id: `isqTrain/645`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `entanglement`, `measurement_order`
- source: `isq_train_cot`
- dataset_index: `2092`

### Prompt

帮我写一个isQ程序：implements the measurement_order_test pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Create a Bell pair, measure one qubit, then demonstrate that an H-H identity pair before the final measurement has no effect on outcomes.

**Qubits:** 2 qubits (q[2]), both measured.

**State evolution:**
1. Initial: |00⟩
2. H(q[0]): (|0⟩ + |1⟩)/√2 ⊗ |0⟩ = (|00⟩ + |10⟩)/√2
3. CNOT(q[0], q[1]): (|00⟩ + |11⟩)/√2 (Bell state)
4. M(q[1]): collapses to |00⟩ (prob 0.5) or |11⟩ (prob 0.5); q[0] remains in |0⟩ or |1⟩ respectively
5. H(q[0]) then H(q[0]): H² = I, so q[0] state is unchanged (identity pair demonstrates gate cancellation)
6. M(q[0]): measures the unchanged computational basis state

**Result:** Since H-H = I, the measurement outcomes are perfectly correlated: {|00⟩: 0.5, |11⟩: 0.5}. The H-H pair cancels, leaving q[0] in its post-CNOT state determined by the first measurement.

## isqTrain/1825

- task_id: `isqTrain/1825`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `415`

### Prompt

请用isQ语言编写一个量子电路：Apply Ry(pi*3/4) to q[0], then CNOT(q[0], q[1]). Measure both.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Create an entangled state via Ry rotation on q[0] followed by CNOT entanglement with q[1].

**Qubits:** 2 qubits (q[0], q[1]), both measured.

**State evolution:**
1. Initial: |00⟩
2. Ry(3π/4, q[0]): Rotates q[0] to cos(3π/8)|0⟩ + sin(3π/8)|1⟩, giving cos(3π/8)|00⟩ + sin(3π/8)|10⟩
3. CNOT(q[0], q[1]): Flips q[1] when q[0]=|1⟩, producing cos(3π/8)|00⟩ + sin(3π/8)|11⟩

**Expected probabilities:** P(00) = cos²(3π/8) ≈ 14.6%, P(11) = sin²(3π/8) ≈ 85.4%, P(01) = P(10) = 0. The final state is an entangled Bell-like superposition with no |01⟩ or |10⟩ components.

## isqTrain/1561

- task_id: `isqTrain/1561`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4215`

### Prompt

帮我写一个isQ程序：Apply Y then X to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Apply Y followed by X to an initial |0> state and measure the result.
2. **Qubits:** 1 qubit is required, which is measured at the end.
3. **State evolution:**
   - Initial state: |0>
   - Apply Y: Y|0> = i|1>
   - Apply X: X(i|1>) = i(X|1>) = i|0>
4. **Probabilities:** The final state is i|0>, which yields a measurement probability of 1.0 for |0> (the global phase i is unobservable).

## isqTrain/4678

- task_id: `isqTrain/4678`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `520`

### Prompt

Will these two quantum programs produce identical measurement outcomes?

```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    M(q[0]); M(q[1]);
}

```

vs.

```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    X(q[1]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis

**Program A:** Applies X to q[0], taking |00⟩ to |10⟩. Measures both qubits.

**Program B:** Applies X to q[0] → |10⟩, then X to q[1] → |11⟩, then CNOT(q[0], q[1]) which flips the target q[1] (since control q[0]=1) → |10⟩. Measures both qubits.

**Key difference:** Program B applies X to q[1] followed by CNOT, which effectively undoes the X on q[1] when q[0] is in |1⟩.

**Measurement probabilities:** Both programs deterministically produce the state |10⟩, yielding measurement outcome '10' with probability 1.0.

**Verdict:** Equivalent — Yes

### Reference answer

{'equivalent': True, 'explanation': "CNOT on |11> flips target back to |0>, same as just |10> Both programs produce the same probability distribution: {'10': 1.0}.", 'probs_a': {'10': 1.0}, 'probs_b': {'10': 1.0}}

## isqTrain/1476

- task_id: `isqTrain/1476`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `data_encoding_qml`
- source: `isq_train_cot`
- dataset_index: `900`

### Prompt

Implement a quantum circuit in isQ: Encode the classical value 3/16 into a qubit using angle encoding (Ry rotation with angle pi*3/16). Measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Encode classical value 3/16 into a qubit via angle encoding using Ry rotation with angle 3π/16, then measure.
2. **Qubits**: 1 qubit (`q[0]`), which is measured.
3. **State evolution**:
   - Initial state: |0⟩
   - After Ry(3π/16, q[0]): cos(3π/32)|0⟩ + sin(3π/32)|1⟩, since Ry(θ)|0⟩ = cos(θ/2)|0⟩ + sin(θ/2)|1⟩
4. **Expected probabilities**:
   - P(|0⟩) = cos²(3π/32) ≈ 0.9157
   - P(|1⟩) = sin²(3π/32) ≈ 0.0843
   - These follow directly from measuring the final state in the computational basis.
