# ISQ training COT RAG corpus: circuit_basics shard 17

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1474

- task_id: `isqTrain/1474`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `data_encoding_qml`
- source: `isq_train_cot`
- dataset_index: `3308`

### Prompt

I need an isQ program to Encode the classical value 1/16 into a qubit using angle encoding (Ry rotation with angle pi*1/16). Measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Encode classical value 1/16 via Ry rotation with angle π/16 and measure the qubit.
2. **Qubits**: 1 qubit q[0], which is measured.
3. **State evolution**:
   - Initial state: |0⟩
   - Apply Ry(π/16, q[0]): Ry(θ)|0⟩ = cos(θ/2)|0⟩ + sin(θ/2)|1⟩, yielding cos(π/32)|0⟩ + sin(π/32)|1⟩
4. **Probabilities**: P(|0⟩) = cos²(π/32) ≈ 0.9904, P(|1⟩) = sin²(π/32) ≈ 0.0096, matching predicted output.

## isqTrain/4714

- task_id: `isqTrain/4714`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `773`

### Prompt

Compare these two isQ programs. Do they give the same probability distribution?

First program:
```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

Second program:
```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    CNOT(q[1], q[0]);
    H(q[0]); // add superposition
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis

1. **Program A** applies X to q[0] (|00⟩ → |10⟩), then CNOT(q[0], q[1]) (|10⟩ → |11⟩). Both qubits are deterministically |1⟩, yielding bitstring "11" with probability 1.

2. **Program B** applies X to q[0] (|00⟩ → |10⟩), then CNOT(q[1], q[0]). Since q[1]=|0⟩, the CNOT does nothing (|10⟩ unchanged). Then H(q[0]) transforms |1⟩⊗|0⟩ to |−⟩⊗|0⟩ = (1/√2)(|10⟩ − |00⟩).

3. **Key difference**: Program B applies an H gate to q[0] (and its CNOT has reversed control/target, which happens to be inactive). This creates superposition, whereas Program A remains in a definite |11⟩ state.

4. **Measurement probabilities**: Program A gives "11" with probability 1. Program B gives "10" with probability 1/2 and "00" with probability 1/2. These distributions are clearly different.

5. **Verdict: Not equivalent** (No)

### Reference answer

{'equivalent': False, 'explanation': 'After adding H gate to Program B, the programs produce different probability distributions.', 'probs_a': {'11': 1.0}, 'probs_b': {'00': 0.5, '10': 0.5}}

## isqTrain/1995

- task_id: `isqTrain/1995`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `global_phase`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3496`

### Prompt

预测以下isQ代码的输出概率：

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

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes 1 qubit to |0>.
2. The first H gate puts the qubit into an equal superposition: |+> = 1/sqrt(2)(|0> + |1>).
3. The GPhase(pi/2) gate applies a global phase of e^(i*pi/2) = i. The state becomes i|+>.
4. The second H gate maps |+> back to |0>. The state becomes i|0>.
5. Since global phases do not affect measurement probabilities, the qubit is deterministically in the |0> state.

Predicted probability distribution: {'0': 1.0}

### Reference answer

{'predicted_probs': {'0': 1.0}, 'explanation': 'Expected probabilities: [1.0, 0.0]'}

## isqTrain/1653

- task_id: `isqTrain/1653`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1196`

### Prompt

Implement a quantum circuit in isQ: Apply Rz(pi) to a qubit in state |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply an Rz rotation of angle pi to a single qubit initialized to the |0> state.
2. Qubits: 1 qubit is required and measured.
3. Evolution: The initial state is |0>. The Rz(pi) gate applies a relative phase only to the |1> state, leaving |0> unchanged up to a global phase ($e^{-i\pi/2}|0\rangle$).
4. Probabilities: Because the final quantum state is exactly |0> (ignoring the unobservable global phase), measuring the qubit yields |0> with a probability of 1.0.

## isqTrain/1777

- task_id: `isqTrain/1777`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `3327`

### Prompt

实现以下量子计算任务（使用isQ）：Apply X gate 9 times to |0> and measure. (X^9 = X.)

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply an X gate 9 times to an initial |0> state and measure the result.
2. Qubits: 1 qubit is used and measured.
3. State evolution: The initial state is |0>. The X gate acts as a bit-flip, mapping |0> to |1> and |1> to |0>. Since X^2 = I, applying X 9 times is equivalent to applying X once (X^9 = X). Thus, the state transitions from |0> to |1> after the first gate and remains |1> after all 9 applications (X^9 |0> = X|0> = |1>).
4. Probabilities: The final state is exactly |1>, so the expected measurement outcome is |1> with a probability of 1.0.

## isqTrain/1746

- task_id: `isqTrain/1746`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5451`

### Prompt

Help me write isQ code that Apply CZ to |01>. Measure both qubits. (CZ only adds phase to |11>, invisible in Z-basis.)

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply CZ to |01⟩ and measure both qubits.
2. Two qubits are needed (q[0], q[1]), both measured.
3. Step-by-step:
   - Start in |00⟩
   - X(q[1]) → |01⟩
   - CZ(q[0], q[1]): CZ adds phase only to |11⟩, leaving |01⟩ unchanged → |01⟩
   - M(q[0]), M(q[1])
4. Final state is |01⟩ with probability 1.0, yielding measurement result 01 (q[0]=0, q[1]=1).

## isqTrain/4587

- task_id: `isqTrain/4587`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4744`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;
qbit q[2];

procedure main() {
    H(q[1]);  // target different qubit
    CNOT(q[0], q[1]);
    Rx(pi/4.0, q[0]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a concise, precise step-by-step analysis of an isQ quantum program. The output must predict the measurement probability distribution using Dirac notation, follow specific formatting rules (start with "## Circuit Analysis", no code blocks, end with predicted distribution), and match the reference probabilities: {|00>: 0.4267766952966369, |01>: 0.4267766952966369, |10>: 0.07322330470336312, |11>: 0.07322330470336312}.

2.  **Analyze the Circuit:**
    *   Initial state: $|00\rangle$
    *   Gate 1: `H(q[1])`. The state becomes $|0\rangle \otimes \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) = \frac{1}{\sqrt{2}}(|00\rangle + |01\rangle)$.
    *   Gate 2: `CNOT(q[0], q[1])`. Control=q[0], Target=q[1].
        *   For $|00\rangle$, target q[1] is 0, control q[0] is 0 -> stays $|00\rangle$.
        *   For $|01\rangle$, target q[1] is 1, control q[0] is 0 -> stays $|01\rangle$.
        *   Wait, $q[0]$ is the control. In $|00\rangle$, $q[0]$ (left) is 0. In $|01\rangle$, $q[0]$ (left) is 0.
        *   State remains $\frac{1}{\sqrt{2}}(|00\rangle + |01\rangle)$. The CNOT does nothing because the control $q[0]$ is $|0\rangle$.
    *   Gate 3: `Rx(pi/4.0, q[0])`.
        *   $q[0]$ is currently $|0\rangle$.
        *   $R_x(\theta) |0\rangle = \cos(\theta/2) |0\rangle - i \sin(\theta/2) |1\rangle$.
        *   Here $\theta = \pi/4$.
        *   $q[0]$ state becomes $\cos(\pi/8) |0\rangle - i \sin(\pi/8) |1\rangle$.
    *   Total state: $\left(\cos(\pi/8) |0\rangle - i \sin(\pi/8) |1\rangle\right) \otimes \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$
    *   $= \frac{1}{\sqrt{2}} \cos(\pi/8) |00\rangle + \frac{1}{\sqrt{2}} \cos(\pi/8) |01\rangle - \frac{i}{\sqrt{2}} \sin(\pi/8) |10\rangle - \frac{i}{\sqrt{2}} \sin(\pi/8) |11\rangle$.

3.  **Calculate Probabilities:**
    *   $P(00) = |\frac{1}{\sqrt{2}} \cos(\pi/8)|^2 = 0.5 \times \cos^2(\pi/8)$.
    *   $P(01) = |\frac{1}{\sqrt{2}} \cos(\pi/8)|^2 = 0.5 \times \cos^2(\pi/8)$.
    *   $P(10) = |-\frac{i}{\sqrt{2}} \sin(\pi/8)|^2 = 0.5 \times \sin^2(\pi/8)$.
    *   $P(11) = |-\frac{i}{\sqrt{2}} \sin(\pi/8)|^2 = 0.5 \times \sin^2(\pi/8)$.
    *   $\cos^2(\pi/8) = \frac{1 + \cos(\pi/4)}{2} = \frac{1 + 1/\sqrt{2}}{2} \approx \frac{1 + 0.7071067}{2} = 0.853553$.
    *   $0.5 \times 0.853553 = 0.426776695...$ (Matches reference).
    *   $\sin^2(\pi/8) = \frac{1 - \cos(\pi/4)}{

### Reference answer

{'predicted_probs': {'00': 0.426777, '01': 0.426777, '10': 0.073223, '11': 0.073223}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|00>) = 0.4268, P(|01>) = 0.4268, P(|10>) = 0.0732, P(|11>) = 0.0732.'}

## isqTrain/4746

- task_id: `isqTrain/4746`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `superposition`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `3300`

### Prompt

比较这两个量子电路，它们的输出概率分布一样吗？

```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    X(q[0]);
    H(q[0]);
    M(q[0]);
}

```

```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    H(q[0]); // add superposition
    M(q[0]);
}

```

### Chain-of-thought reasoning

1.  **Analyze Program A:**
    *   Initial state: |0>
    *   H(q[0]): state becomes |+> = 1/sqrt(2)|0> + 1/sqrt(2)|1>
    *   X(q[0]): X|+> = |- > = 1/sqrt(2)|0> - 1/sqrt(2)|1>
    *   H(q[0]): H|- > = |1>
    *   Measurement: measures |1> with 100% probability.

2.  **Analyze Program B:**
    *   Initial state: |0>
    *   H(q[0]): state becomes |+>
    *   H(q[0]): H|+> = |0>
    *   Measurement: measures |0> with 100% probability.

3.  **Wait, let me re-evaluate.**
    *   Let's check Program A:
        *   H -> X -> H
        *   H X H = Z (up to global phase).
        *   Applying Z to |0> gives |0>.
        *   Wait, H|0> = |+>. X|+> = |- >. H|- > = |1>.
        *   Ah. HXH = Z. Z|0> = |0>.
        *   Let me re-evaluate X|+>.
        *   |+> = (|0> + |1>)/sqrt(2)
        *   X|+> = (X|0> + X|1>)/sqrt(2) = (|1> + |0>)/sqrt(2) = |+>.
        *   Wait, X acts as identity on |+> ! X|+> = |+>.
        *   So Program A: H -> X -> H.
        *   H|0> = |+>.
        *   X|+> = |+>.
        *   H|+> = |0>.
        *   Measurement gives |0> with 100% probability.
    *   Let's check Program B:
        *   H -> H
        *   H|0> = |+>
        *   H|+> = |0>
        *   Measurement gives |0> with 100% probability.
    *   Wait! Is my manual calculation correct?
        *   X matrix: [[0,1],[1,0]]. H matrix: 1/sqrt(2)[[1,1],[1,-1]].
        *   H|0> = 1/sqrt(2)(|0> + |1>) = |+>.
        *   X|+> = 1/sqrt(2)(X|0> + X|1>) = 1/sqrt(2)(|1> + |0>) = |+>.
        *   H|+> = 1/sqrt(2)(H|0> + H|1>) = 1/sqrt(2)(|+> + |->) = 1/sqrt(2)[1/sqrt(2)(|0>+|1>) + 1/sqrt(2)(|0>-|1>)] = 1/2(2|0>) = |0>.
        *   Yes! Program A gives |0>.
        *   Program B gives |0>.
        *   So both give 100% probability of |0>.

4.  **Draft the Analysis:**
    *   Program A applies H, X, and H gates to q[0]. It evolves |0> -> |+> -> |+> -> |0>.
    *   Program B applies two H gates to q[0]. It evolves |0> -> |+> -> |0>.
    *   The key difference is the presence of the X gate in Program A.
    *   However, the X gate acts as the identity on the |+> state because X|+> = |+>. Thus, it has no effect on the quantum state.
    *   Both programs leave q[0] in the |0> state, resulting in a 100% probability of measuring 0.
    *   Verdict: Yes.

5.  **Refine to constraints:** 3-8 lines. Dirac notation. Start with "## Equivalence Analysis". End with "Yes/No" verdict line.

    ## Equivalence Analysis
    1. Program A applies an H gate, followed by an X gate, and then another H gate to |0>, evolving the state to |+> -> |+> -> |0>.
    2. Program B applies two consecutive H gates to |0>, evolving the state to |+> -> |0>.
    3. The key difference is the intermediate X gate in Program A, which acts as an identity on

### Reference answer

{'equivalent': True, 'explanation': 'After adding H gate to Program B, the programs produce the same probability distributions.', 'probs_a': {'0': 1.0}, 'probs_b': {'0': 1.0}}

## isqTrain/4760

- task_id: `isqTrain/4760`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `2708`

### Prompt

比较这两个量子电路，它们的输出概率分布一样吗？

```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    CNOT(q[0], q[1]);
    X(q[0]); // additional bit flip
    M(q[0]); M(q[1]);
}

```

```isq
import std;
qbit q[2];

procedure main() {
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
* **Program A:** Applies an X gate to q[0] ($|00\rangle \to |10\rangle$), a CNOT ($|10\rangle \to |11\rangle$), and another X gate to q[0] ($|11\rangle \to |01\rangle$).
* **Program B:** Applies a CNOT gate, which acts on the initial state $|00\rangle$ and leaves it unchanged as $|00\rangle$.
* **Key Difference:** Program A alters the control qubit before the CNOT gate, activating the target flip, and then flips the control back, ultimately swapping the bits from the initial state.
* **Probability Comparison:** Program A yields a 100% probability of measuring $|01\rangle$, whereas Program

### Reference answer

{'equivalent': False, 'explanation': 'After adding X gate to Program A, the programs produce different probability distributions.', 'probs_a': {'01': 1.0}, 'probs_b': {'00': 1.0}}

## isqTrain/1604

- task_id: `isqTrain/1604`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `data_encoding_qml`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `643`

### Prompt

Create an isQ quantum circuit that Apply Ry(pi*2/8) to each of 2 qubits and measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply an $R_y(\pi/4)$ rotation independently to two qubits and measure them.
2. **Qubits**: 2 qubits are used, and both are measured.
3. **State evolution**:
   - Initialize the 2-qubit system to the ground state $|00\rangle$.
   - Apply $R_y(\pi/4)$ to $q[0]$, evolving the state to $(\cos(\pi/8)|0\rangle + \sin(\pi/8)|1\rangle) \otimes |0\rangle$.
   - Apply $R_y(\pi/4)$ to $q[1]$, evolving the state to $(\cos(\pi/8)|0\rangle + \sin(\pi/8)|1\rangle) \otimes (\cos(\pi/8)|0\rangle + \sin(\pi/8)|1\rangle)$.
   - Expanding the tensor product gives the final state: $\cos^2(\pi/8)|00\rangle + \sin(\pi/8)\cos(\pi/8)|01\rangle + \sin(\pi/8)\cos(\pi/8)|10
