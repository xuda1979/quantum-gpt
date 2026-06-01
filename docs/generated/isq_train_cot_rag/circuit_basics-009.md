# ISQ training COT RAG corpus: circuit_basics shard 9

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4675

- task_id: `isqTrain/4675`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2005`

### Prompt

Compare these two isQ programs. Do they give the same probability distribution?

First program:
```isq
import std;
qbit q[1];

procedure main() {
    X(q[0]);
    X(q[0]);
    X(q[0]); // additional bit flip
    M(q[0]);
}

```

Second program:
```isq
import std;
qbit q[1];

procedure main() {
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. Program A initializes a qubit to |0> and applies the X gate three times, resulting in the final state |1> before measurement.
2. Program B initializes a qubit to |0> and applies no gates, leaving it in the state |0> before measurement.
3. The key difference is the odd number of X gates in Program A, which flips the initial state from |0> to |1>.
4. The measurement probability distributions are different: Program A yields 100% probability of measuring 1, while Program B yields 100% probability of measuring 0.
5. Verdict: No

### Reference answer

{'equivalent': False, 'explanation': 'After adding X gate to Program A, the programs produce different probability distributions.', 'probs_a': {'1': 1.0}, 'probs_b': {'0': 1.0}}

## isqTrain/4727

- task_id: `isqTrain/4727`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `4373`

### Prompt

这两个isQ程序是等价的吗？

程序A：
```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    M(q[0]); M(q[1]);
}

```

程序B：
```isq
import std;
qbit q[2];

procedure main() {
    X(q[1]);
    H(q[0]); // add superposition
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. Program A applies an X gate to $q[0]$, preparing the state $|10\rangle$. Measurement yields $|10\rangle$ with 100% probability.
2. Program B applies an X gate to $q[1]$ and an H gate to $q[0]$, preparing the state $\frac{1}{\sqrt{2}}(|01\rangle + |11\rangle)$. Measurement yields $|01\rangle$ and $|11\rangle$, each with 50% probability.
3. The key difference is that Program A acts on $q[0]$ with an X gate, while Program B acts on $q[1]$ with X and adds superposition on $q[0]$ via the H gate.
4. The measurement probability distributions are completely different: deterministic $|10\rangle$ for A versus an equal mixture of $|01\rangle$ and $|11\rangle$ for B.
5. Verdict: Not equivalent

### Reference answer

{'equivalent': False, 'explanation': 'After adding H gate to Program B, the programs produce different probability distributions.', 'probs_a': {'10': 1.0}, 'probs_b': {'01': 0.5, '11': 0.5}}

## isqTrain/1615

- task_id: `isqTrain/1615`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `data_encoding_qml`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1069`

### Prompt

实现以下量子计算任务（使用isQ）：Apply Ry(pi*5/8) to each of 3 qubits and measure all.

### Chain-of-thought reasoning

## Reasoning
The goal is to apply an $R_y$ rotation of $5\pi/8$ to three independent qubits and measure them.
This requires 3 qubits ($q[0], q[1], q[2]$), all initialized to $|0\rangle$ and subsequently measured.
Each $R_y(5\pi/8)$ gate rotates a qubit around the Y-axis, evolving its state from $|0

## isqTrain/4690

- task_id: `isqTrain/4690`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1650`

### Prompt

Compare these two isQ programs. Do they give the same probability distribution?

First program:
```isq
import std;
qbit q[1];

procedure main() {
    Z(q[0]);
    X(q[0]); // additional bit flip
    M(q[0]);
}

```

Second program:
```isq
import std;
qbit q[1];

procedure main() {
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A operations**: Applies a Z gate to q[0], leaving the |0> state unchanged. Then applies an X gate, flipping the state to |1>. Finally, it measures the qubit.
2. **Program B operations**: Measures the initial |0> state of q[0] directly without applying any gates.
3. **Key difference**: Program A includes an X gate (bit-flip) before measurement, changing the state from |0> to |1>, whereas Program B does not.
4. **Measurement probabilities**: Program A will always measure the state as |1> (100% probability), while Program B will always measure the state as |0> (100% probability). The probability distributions are completely inverted.
5. **Verdict**: No

### Reference answer

{'equivalent': False, 'explanation': 'After adding X gate to Program A, the programs produce different probability distributions.', 'probs_a': {'1': 1.0}, 'probs_b': {'0': 1.0}}

## isqTrain/1717

- task_id: `isqTrain/1717`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5327`

### Prompt

Code this in isQ: Apply Rx(pi/2) then Rz(pi/2) to |0>. Measure.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Generate a step-by-step reasoning section for an isQ quantum program.
    *   Input Prompt: Apply Rx(pi/2) then Rz(pi/2) to |0>. Measure.
    *   Constraint: Output ONLY the "## Reasoning" section. Concise (3-8 lines). Use Dirac notation.
    *   No code blocks.

2.  **Trace the Quantum State Evolution:**
    *   Initial state: $|0\rangle$
    *   Apply $R_x(\pi/2)$: $R_x(\theta) = \cos(\theta/2)I - i\sin(\theta/2)X$.
        *   $R_x(\pi/2) |0\rangle = \frac{1}{\sqrt{2}}(|0\rangle - i|1\rangle) = \frac{1}{\sqrt{2}}(|0\rangle - i|1\rangle)$ or $\frac{1}{2}(1-i)|0\rangle + ...$ wait. Let's use standard matrix multiplication.
        *   $R_x(\pi/2) = \frac{1}{\sqrt{2}} \begin{pmatrix} 1 & -i \\ -i & 1 \end{pmatrix}$.
        *   $R_x(\pi/2) |0\rangle = \frac{1}{\sqrt{2}} |0\rangle - \frac{i}{\sqrt{2}} |1\rangle$.
    *   Apply $R_z(\pi/2)$: $R_z(\theta) = e^{-i\theta/2}|0\rangle\langle 0| + e^{i\theta/2}|1\rangle\langle 1|$.
        *   $R_z(\pi/2) \left( \frac{1}{\sqrt{2}} |0\rangle - \frac{i}{\sqrt{2}} |1\rangle \right) = \frac{1}{\sqrt{2}} e^{-i\pi/4} |0\rangle - \frac{i}{\sqrt{2}} e^{i\pi/4} |1\rangle$.
    *   Measurement probabilities: The probability of measuring $|0\rangle$ is $|\frac{1}{\sqrt{2}} e^{-i\pi/4}|^2 = 1/2$. The probability of measuring $|1\rangle$ is $|-\frac{i}{\sqrt{2}} e^{i\pi/4}|^2 = |-i|^2 |e^{i\pi/4}|^2 / 2 = 1/2$.
    *   Both states have equal probability of 50%.

3.  **Draft the Reasoning Section:**
    *   Goal: Apply a sequence of Rx and Rz rotations to the $|0\rangle$ state and measure the result.
    *   Qubits: 1 qubit is needed, which is measured.
    *   Evolution:
        *   Start: $|0\rangle$
        *   $R_x(\pi/2)$: Transitions state to $\frac{1}{\sqrt{2}}|0\rangle - \frac{i}{\sqrt{2}}|1\rangle$.
        *   $R_z(\pi/2)$: Applies phase shifts, resulting in $\frac{1}{\sqrt{2}}e^{-i\pi/4}|0\rangle - \frac{i}{\sqrt{2}}e^{i\pi/4}|1\rangle$.
    *   Probabilities: The final state has amplitudes with magnitudes $\frac{1}{\sqrt{2}}$ for both $|0\rangle$ and $|1\rangle$, giving an exact 50% probability for each outcome.

4.  **Refine and Format:**
    *   Keep it concise (3-8 lines).
    *   Check rules: Output ONLY the reasoning section starting with "## Reasoning".

    ## Reasoning
    Goal: Apply $R_x(\pi/2)$ and $R_z(\pi/2)$ rotations to an initial $|0\rangle$ state and measure it.
    Qubits: 1 qubit is required, which is measured.
    State Evolution:
    1. Start in the $|0\rangle$ state.
    2. Apply $R_x(\pi/2)$ to get $\frac{1}{\sqrt{2}}|0\rangle - \frac{i}{\sqrt{2}}|1\rangle$.
    3. Apply $R_z(\pi/2)$ to apply relative phases, yielding $\frac{1}{\sqrt{2}}e^{-i\pi/4}|0\rangle - \

## isqTrain/642

- task_id: `isqTrain/642`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `entanglement`, `measurement_order`
- source: `isq_train_cot`
- dataset_index: `313`

### Prompt

Implement the following in isQ: implements a variant of the measurement_order_test pattern using q[2] -> q[4]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

The task asks me to write a reasoning section for a variant of the measurement_order_test pattern using q[2] -> q[4], with an expanded qubit register.

Let me analyze:
1. The base pattern uses H(q[0]) and CNOT(q[0], q[1]) to create a Bell state
2. The variant uses q[2] -> q[4] instead
3. The register should be significantly expanded (more qubits than base)
4. Additional qubits should be left in ground state

Analyzing the circuit requirements, it uses 4 qubits with H on q[0] and CNOT(q[0], q[1]).
The variant should use q[2] and q[4] as the active qubits, so we need at least 5 qubits.

The circuit:
1. Apply H(q[2]) to put q[2] in superposition: |0> -> |+> = (|0> + |1>)/√2
2. Apply CNOT(q[2], q[4]) to create Bell pair: (|00> + |11>)/√2 on q[2],q[4]
3. Other qubits (q[0], q[1], q[3], and any others) remain in |0>
4. Measure all qubits

Expected probabilities: For 5 qubits with q[2] and q[4] entangled:
- |00000>: 0.5 (both q[2] and q[4] are 0)
- |00101>: 0.5 (q[2] is 1, q[4] is 1, others 0)

Wait, let me reconsider the measurement order. The problem says "earlier measured qubit = higher bit" for the output.

If we measure q[2] then q[4] (as per the pattern q[2] -> q[4]), the bitstring would be:
- If q[2]=0, q[4]=0: |00000> -> q[2] is bit 2, q[4] is bit 4... this gets confusing.

Let me think about this more carefully. The measurement bitstring has "earlier measured qubit = higher bit". So if we measure in order q[0], q[1], q[2], q[3], q[4]:
- q[0] is measured first -> highest bit
- q[4] is measured last -> lowest bit

For a 5-qubit system with the Bell state on q[2] and q[4]:
|ψ> = (|00000> + |10100>)/√2

When measured:
- q[2]=0, q[4]=0 -> |00000>
- q[2]=1, q[4]=1 -> |10100> (binary: q[4]=0, q[3]=0, q[2]=1, q[1]=0, q[0]=1)

Hmm, the bitstring encoding depends on the measurement order.

Actually, let me re-read: "measurement bitstring (earlier measured qubit = higher bit)"

So if M(q[0]), M(q[1]), M(q[2]), M(q[3]), M(q[4]) in that order:
- Result of M(q[0]) goes to bit 4 (highest)
- Result of M(q[1]) goes to bit 3
- Result of M(q[2]) goes to bit 2
- Result of M(q[3]) goes to bit 1
- Result of M(q[4]) goes to bit 0 (lowest)

So if q[2]=0, q[4]=0, all others 0 -> |00000>
If q[2]=1, q[4]=1, all others 0 -> q[0]=0(bit4), q[1]=0(bit3), q[2]=1(bit2), q[3]=0(bit1), q[4]=1(bit0) -> |00101> = 5

Wait, I need to check the measurement order in the problem. It says "measurement_order_test pattern using q[2] -> q[4]". The arrow might indicate the order or just indicate q[2] to q[4].

Analyzing the circuit requirements more carefully:

So q[1] is measured first (highest bit), then q[0], q[2], q[3].

For the variant with q[2] -> q[4], we should have something similar where q[2] is measured before q[4].

Let me create a reasonable variant:
- Use 6 or 7 qubits (significantly expanded)
-

## isqTrain/1773

- task_id: `isqTrain/1773`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `2663`

### Prompt

实现以下量子计算任务（使用isQ）：Apply X gate 5 times to |0> and measure. (X^5 = X.)

### Chain-of-thought reasoning

## Reasoning
Goal: Apply the X gate 5 times to |0> and measure, exploiting X^5 = X.
Qubits: 1 qubit (q[0]), measured at the end.
State evolution: |0> →X |1> →X |0> →X |1> →X |0> →X |1>.
Since 5 is odd, X^5 = X, so the net effect is a single X, flipping |0> to |1>.
Probability: {|1>: 1.0}, as the final state is exactly |1>.

## isqTrain/4732

- task_id: `isqTrain/4732`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2679`

### Prompt

Are these two quantum circuits equivalent in terms of measurement output?

Circuit 1:
```isq
import std;
qbit q[1];

procedure main() {
    Rx(pi/6.0, q[0]);
    M(q[0]);
}

```

Circuit 2:
```isq
import std;
qbit q[1];

procedure main() {
    Rx(pi/3.0, q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

1.  **Analyze Program A**:
    *   Starts with $|0\rangle$.
    *   Applies $R_x(\pi/6, q[0])$.
    *   Rotation matrix for $R_x(\theta) = e^{-i\theta X/2} = \cos(\theta/2)I - i\sin(\theta/2)X$.
    *   State becomes $\cos(\pi/12)|0\rangle - i\sin(\pi/12)|1\rangle$.
    *   Probability of 0: $P(0) = \cos^2(\pi/12)$.
    *   $\cos(\pi/12) = \cos(15^\circ) = \frac{\sqrt{6}+\sqrt{2}}{4}$.
    *   $\cos^2(15^\circ) = \frac{6 + 2 + 2\sqrt{12}}{16} = \frac{8 + 4\sqrt{3}}{16} = \frac{2+\sqrt{3}}{4} \approx \frac{2+1.732}{4} = 0.9330125$.
    *   Probability of 1: $P(1) = \sin^2(\pi/12) \approx 0.066987$.

2.  **Analyze Program B**:
    *   Starts with $|0\rangle$.
    *   Applies $R_x(\pi/3, q[0])$.
    *   State becomes $\cos(\pi/6)|0\rangle - i\sin(\pi/6)|1\rangle$.
    *   Probability of 0: $P(0) = \cos^2(\pi/6) = (\sqrt{3}/2)^2 = 3/4 = 0.75$.
    *   Probability of 1: $P(1) = \sin^2(\pi/6) = (1/2)^2 = 1/4 = 0.25$.

3.  **Wait, looking at the predicted output**:
    *   "Program A produces {'0': 0.75, '1': 0.25}"
    *   "Program B produces {'0': 0.933013, '1': 0.066987}"
    *   Let me re-calculate. $R_x(\theta) = e^{-i \theta X / 2}$.
    *   If A uses $\theta = \pi/6$, the angle of rotation on the Bloch sphere is $\pi/6$. The probabilities are $\cos^2(\pi/12)$ and $\sin^2(\pi/12)$.
    *   Wait! The prompt's predicted output says: Program A produces {'0': 0.75, '1': 0.25}.
    *   If A has $\pi/6$ rotation, and $P(0) = 0.75$, this implies $\cos^2(\theta/2) = 0.75 \implies \cos(\theta/2) = \sqrt{3}/2 \implies \theta/2 = \pi/6 \implies \theta = \pi/3$.
    *   Ah! Standard $R_x$ matrix in some libraries (like isQ or Qiskit) might be $R_x(\theta) = \begin{pmatrix} \cos(\theta/2) & -i\sin(\theta/2) \\ -i\sin(\theta/2) & \cos(\theta/2) \end{pmatrix}$.
    *   Let me check the isQ docs or standard convention. In standard Qiskit, $R_x(\pi/3)$ gives $P(0) = \cos^2(\pi/6) = 0.75$.
    *   Let's re-read the predicted output: Program A (pi/6) -> {'0': 0.75, '1': 0.25}? Wait, if A is $\pi/6$, $P(0) = \cos^2(\pi/12) = 0.933$. B is $\pi/3$, $P(0) = \cos^2(\pi/6) = 0.75$. So the predicted output text might have swapped them or it's using a different convention (like $R_x(\theta) = e^{-i \theta X}$ without the /2).
    *   Wait, if $R_x(\theta)$ in isQ is exactly $\begin{pmatrix} \cos(\theta/2) & -i\sin(\theta/2) \\ -i\sin(\theta/2) & \cos(\theta/2) \

### Reference answer

{'equivalent': False, 'explanation': "Different rotation angles produce different measurement distributions Program A produces {'0': 0.75, '1': 0.25} while Program B produces {'0': 0.933013, '1': 0.066987}.", 'probs_a': {'0': 0.933013, '1': 0.066987}, 'probs_b': {'0': 0.75, '1': 0.25}}

## isqTrain/1320

- task_id: `isqTrain/1320`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `649`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[2];

procedure main() {
    H(q[0]);
    H(q[0]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes two qubits to the state |00>.
2. A Hadamard gate (H) is applied to q[0], changing the state to 1/√2(|00> + |10>).
3. A second H gate is applied to q[0]. Since the Hadamard gate is its own inverse (H^2 = I), the state returns exactly to |00>.
4. Both qubits are measured in the computational basis. Because the final state is exactly |00>, this outcome is certain.

Predicted probability distribution: {|00>: 1.0}

### Reference answer

{'predicted_probs': {'0': 1.0}, 'explanation': 'Parametric variant of isqEval/474. Dimension: qubit_variant: q[1] -> q[2].'}

## isqTrain/4679

- task_id: `isqTrain/4679`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `2357`

### Prompt

Will these two quantum programs produce identical measurement outcomes?

```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    X(q[1]);
    CNOT(q[0], q[1]);
    X(q[0]); // additional bit flip
    M(q[0]); M(q[1]);
}

```

vs.

```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A operations**: Applies X to both qubits, changing the state from $|00\rangle$ to $|11\rangle$. A CNOT gate then flips the target qubit $q_1$, resulting in $|10\rangle$. Finally, an X gate is applied to $q_0$, resulting in the final state $|00\rangle$.
2. **Program B operations**: Applies a single X gate to $q_0$, changing the state from $|00\rangle$ to $|10\rangle$.
3. **Key difference**: Program A ultimately leaves the system in the ground state $|00\rangle$, whereas Program B leaves the system in the excited state $|10\rangle$. 
4. **Measurement probabilities**: Program A yields a 100% probability of measuring the bitstring `00`. Program B yields a 100% probability of measuring the bitstring `10`.
5. **Verdict**: No

### Reference answer

{'equivalent': False, 'explanation': 'After adding X gate to Program A, the programs produce different probability distributions.', 'probs_a': {'00': 1.0}, 'probs_b': {'10': 1.0}}
