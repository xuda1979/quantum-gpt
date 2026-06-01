# ISQ training COT RAG corpus: circuit_basics shard 27

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1815

- task_id: `isqTrain/1815`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `829`

### Prompt

请用isQ语言编写一个量子电路：Apply Ry(pi*5/6) to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply rotation Ry(5π/6) to |0⟩ and measure the resulting state.
2. **Qubits**: 1 qubit needed, measured at the end.
3. **State evolution**:
   - Initial state: |ψ₀⟩ = |0⟩
   - Apply Ry(5π/6): |ψ₁⟩ = cos(5π/12)|0⟩ + sin(5π/12)|1⟩
4. **Measurement probabilities**:
   - P(|0⟩) = cos²(5π/12) = cos²(75°) ≈ 0.0669872981
   - P(|1⟩) = sin²(5π/12) = sin²(75°) ≈ 0.9330127019

## isqTrain/4731

- task_id: `isqTrain/4731`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `5746`

### Prompt

Determine if these two isQ implementations are functionally equivalent:

Version A:
```isq
import std;
qbit q[3];

procedure main() {
    X(q[0]);
    X(q[1]);
    ctrl ctrl X(q[0], q[1], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

Version B:
```isq
import std;
qbit q[3];

procedure main() {
    X(q[0]);
    ctrl ctrl X(q[0], q[1], q[2]);
    H(q[0]); // add superposition
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis

1. **Program A** prepares state |110>, then applies a Toffoli (ctrl ctrl X) with both controls in |1>, flipping q[2] to yield |111>. Measurement always yields bitstring 111.

2. **Program B** prepares state |100>, then applies a Toffoli where q[0]=|1> but q[1]=|0>, so q[2] is NOT flipped, leaving |100>. Then H(q[0]) creates (|000> + |100>)/√2. Measurement yields bitstrings 000 or 100, each with 50% probability.

3. **Key difference**: Program A initializes both controls to |1> (triggering the Toffoli), while Program B only initializes one control to |1> (Toffoli does nothing), then adds a Hadamard creating superposition. The resulting states are completely different: |111> vs (|000>+|100>)/√2.

4. The measurement probability distributions differ: Program A gives {111: 1.0}, while Program B gives {000: 0.5, 100: 0.5}.

5. **Verdict: Not equivalent**

### Reference answer

{'equivalent': False, 'explanation': 'After adding H gate to Program B, the programs produce different probability distributions.', 'probs_a': {'111': 1.0}, 'probs_b': {'000': 0.5, '100': 0.5}}

## isqTrain/641

- task_id: `isqTrain/641`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `entanglement`, `measurement_order`
- source: `isq_train_cot`
- dataset_index: `5484`

### Prompt

Implement a quantum circuit in isQ: implements a variant of the measurement_order_test pattern using q[2] -> q[3]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a Bell pair between q[0] and q[1] with an extra ancilla q[2], demonstrating measurement order with a 3-qubit register.
2. **Qubits**: 3 qubits (q[0], q[1], q[2]), all measured; q[2] remains idle in |0⟩.
3. **State evolution**:
   - Initialize: |000⟩
   - H(q[0]): (|000⟩ + |100⟩)/√2
   - CNOT(q[0], q[1]): (|000⟩ + |110⟩)/√2 (entangled Bell state on q[0],q[1]; q[2] untouched)
4. **Measurement**: M(q[1]) first (high bit), then M(q[0]) (middle), M(q[2]) (low bit).
   - With probability 0.5: measure q[1]=0, q[0]=0, q[2]=0 → bitstring 000
   - With probability 0.5: measure q[1]=1, q[0]=1, q[2]=0 → bitstring 110
5. **Result**: {|000⟩: 0.5, |110⟩: 0.5} — the Bell pair collapses correlatively, and the idle qubit always yields 0.

## isqTrain/4686

- task_id: `isqTrain/4686`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5006`

### Prompt

这两个isQ程序是等价的吗？

程序A：
```isq
import std;
qbit q[1];

procedure main() {
    Y(q[0]);
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
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A operations**: Applies a Y gate followed by an X gate to q[0]. The state evolves as |0> -> i|1> -> i|0>.
2. **Program B operations**: Applies an X gate to q[0]. The state evolves as |0> -> |1>.
3. **Key difference**: Program A results in a final state of i|0> (a global phase applied to |0>), whereas Program B results in a final state of |1>.
4. **Probability distributions**: Program A measures q[0] as 0 with 100% probability, while Program B measures q[0] as 1 with 100% probability.
5. **Verdict**: No

### Reference answer

{'equivalent': False, 'explanation': 'After adding X gate to Program A, the programs produce different probability distributions.', 'probs_a': {'0': 1.0}, 'probs_b': {'1': 1.0}}

## isqTrain/1818

- task_id: `isqTrain/1818`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1813`

### Prompt

Write isQ code for the following quantum task: Apply Ry(pi*8/6) to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply rotation Ry(4π/3) to |0⟩ and measure the resulting state.
2. **Qubits**: 1 qubit, which is measured.
3. **State evolution**:
   - Start: |ψ₀⟩ = |0⟩
   - Apply Ry(4π/3): |ψ₁⟩ = cos(2π/3)|0⟩ + sin(2π/3)|1⟩ = (-1/2)|0⟩ + (√3/2)|1⟩
4. **Probabilities**: P(|0⟩) = |-1/2|² = 0.25, P(|1⟩) = |√3/2|² = 0.75.

## isqTrain/1810

- task_id: `isqTrain/1810`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3861`

### Prompt

Implement a quantum circuit in isQ: Apply Rx(pi*12/6) to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply Rx(2π) to |0⟩ and measure the resulting state.
2. **Qubits**: 1 qubit needed, 1 measured.
3. **State evolution**: 
   - Initial: |ψ⟩ = |0⟩
   - Rx(2π) = [[cos(π), -i·sin(π)], [-i·sin(π), cos(π)]] = [[-1, 0], [0, -1]] = -I
   - After Rx(2π): |ψ⟩ = -|0⟩ (global phase only, same measurement statistics)
4. **Expected probabilities**: {|0⟩: 1.0, |1⟩: 0.0} — the global phase (-1) doesn't affect measurement, so |0⟩ is observed with certainty.

## isqTrain/4737

- task_id: `isqTrain/4737`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `1578`

### Prompt

Do these two isQ programs produce the same measurement results?

Program A:
```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    S(q[0]);
    H(q[0]);
    X(q[0]); // additional bit flip
    M(q[0]);
}

```

Program B:
```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    T(q[0]);
    H(q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Compare two isQ programs for measurement probability distribution equivalence.
    *   Program A: H -> S -> H -> X -> M
    *   Program B: H -> T -> H -> M
    *   Output Format: "## Equivalence Analysis", concise (3-15 lines), specific structure (1-5 points), No code blocks, Yes/No verdict line.

2.  **Analyze Program A:**
    *   Initial state: $|0\rangle$
    *   Apply $H$: $(|0\rangle + |1\rangle)/\sqrt{2} = |+\rangle$
    *   Apply $S$: $(|0\rangle + i|1\rangle)/\sqrt{2}$
    *   Apply $H$: $\frac{1}{\sqrt{2}} ( \frac{|0\rangle + |1\rangle}{\sqrt{2}} + i \frac{|0\rangle - |1\rangle}{\sqrt{2}} ) = \frac{1+i}{2}|0\rangle + \frac{1-i}{2}|1\rangle$.
        *   Wait, an easier way: $H S H$ is a basis transformation. $H S H |0\rangle$.
        *   $H Z H = X$, $H S H = R_x(\pi/2)$ or $R_y$? Let's check:
        *   $S = P(\pi/2)$. $H P(\pi/2) H = R_x(-\pi/2) = X2M$. Wait. $H \begin{pmatrix} 1&0\\0&i\end{pmatrix} H = \frac{1}{2} \begin{pmatrix} 1&1\\1&-1\end{pmatrix} \begin{pmatrix} 1&0\\0&i\end{pmatrix} \begin{pmatrix} 1&1\\1&-1\end{pmatrix} = \frac{1}{2} \begin{pmatrix} 1&i\\1&-i\end{pmatrix} \begin{pmatrix} 1&1\\1&-1\end{pmatrix} = \frac{1}{2} \begin{pmatrix} 1+i & 1-i \\ 1-i & 1+i \end{pmatrix}$.
        *   Let's check $R_y(\pi/2)$: $\frac{1}{\sqrt{2}} \begin{pmatrix} 1 & -1 \\ 1 & 1 \end{pmatrix}$. Not this.
        *   Let's re-evaluate $H S H |0\rangle$:
        *   $H |0\rangle = |+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$
        *   $S |+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + i|1\rangle)$
        *   $H (\frac{1}{\sqrt{2}}(|0\rangle + i|1\rangle)) = \frac{1}{2}(|0\rangle + |1\rangle + i|0\rangle - i|1\rangle) = \frac{1+i}{2}|0\rangle + \frac{1-i}{2}|1\rangle$.
        *   Probabilities: $P(0) = |\frac{1+i}{2}|^2 = 1/2$. $P(1) = 1/2$.
    *   Apply $X$: $X \left( \frac{1+i}{2}|0\rangle + \frac{1-i}{2}|1\rangle \right) = \frac{1+i}{2}|1\rangle + \frac{1-i}{2}|0\rangle = \frac{1-i}{2}|0\rangle + \frac{1+i}{2}|1\rangle$.
    *   Probabilities before measurement: $P(0) = 1/2, P(1) = 1/2$. Wait, if both have $P(0)=1/2$ and $P(1)=1/2$, they ARE equivalent in measurement distribution! Let me re-read the prompt. "predicted output: Equivalent: False. Explanation: After adding X gate to Program A, the programs produce different probability distributions."
    *   Wait, does $H T H$ also have 1/2, 1/2? Yes.
    *   Let me re-read the *exact* matrices.
    *   $H = \frac{1}{\sqrt{2}} \begin{pmatrix

### Reference answer

{'equivalent': False, 'explanation': 'After adding X gate to Program A, the programs produce different probability distributions.', 'probs_a': {'0': 0.5, '1': 0.5}, 'probs_b': {'0': 0.853553, '1': 0.146447}}

## isqTrain/4688

- task_id: `isqTrain/4688`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `516`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[1];

procedure main() {
    Y(q[0]);
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The initial state of qubit q[0] is |0>.
2. The `Y` gate transforms the state: Y|0> = i|1>.
3. The `X` gate transforms the state: X(i|1>) = i|0>.
4. The global phase factor `i` does not affect measurement probabilities, so the state is effectively |0>.
5. Measurement will deterministically yield the |0> state.

Expected measurement probabilities: {|0>: 1.0}

### Reference answer

{'predicted_probs': {'0': 1.0}, 'explanation': 'This isQ program operates on 1 qubit(s). The measurement probability distribution is: P(|0>) = 1.0000.'}

## isqTrain/1822

- task_id: `isqTrain/1822`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `732`

### Prompt

Help me write isQ code that Apply Ry(pi*12/6) to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. The goal is to apply an $R_y(2\pi)$ rotation to the $|0\rangle$ state and measure it.
2. The circuit requires 1 qubit, which is measured.
3. Starting in $|0\rangle$, applying $R_y(\pi \cdot 12/6) = R_y(2\pi)$ yields $-|0\rangle$ (a $2\pi$ rotation introduces a global phase of -1).
4. Since global phases do not affect measurement probabilities, the final state is functionally equivalent to $|0\rangle$, resulting in a 100% chance of measuring $|0\rangle$.

## isqTrain/1809

- task_id: `isqTrain/1809`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2423`

### Prompt

Help me write isQ code that Apply Rx(pi*11/6) to |0> and measure.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Task:** Code generation task. Apply $R_x(11\pi/6)$ to $|0\rangle$ and measure.
    *   **Goal:** Generate a *reasoning section* explaining the circuit, NOT the code itself.
    *   **Format constraints:** Start with "## Reasoning". Use Dirac notation. Concise (3-8 lines). No code blocks.

2.  **Analyze the Circuit/Physics:**
    *   Initial state: $|0\rangle$
    *   Gate: $R_x(\theta) = e^{-i\theta X/2} = \cos(\theta/2)I - i\sin(\theta/2)X$.
    *   Angle: $\theta = 11\pi/6$.
    *   Angle / 2: $\theta/2 = 11\pi/12$.
    *   Resulting state: $\cos(11\pi/12)|0\rangle - i\sin(11\pi/12)|1\rangle$.
    *   Probabilities:
        *   $P(0) = \cos^2(11\pi/12)$
        *   $P(1) = \sin^2(11\pi/12)$
    *   Trig values:
        *   $\cos(11\pi/12) = -\cos(\pi/12) = -\frac{\sqrt{6}+\sqrt{2}}{4}$
        *   $\sin(11\pi/12) = \sin(\pi/12) = \frac{\sqrt{6}-\sqrt{2}}{4}$
        *   Wait, is $\cos^2(11\pi/12) \approx 0.933$? Yes, $\cos^2(\pi/12) = \frac{2 + \sqrt{3}}{4} = 0.9330127...$
        *   $\sin^2(11\pi/12) = \sin^2(\pi/12) = \frac{2 - \sqrt{3}}{4} = 0.066987...$

3.  **Draft the Reasoning Steps:**
    *   *Goal:* Apply $R_x(11\pi/6)$ to $|0\rangle$ and measure the single qubit.
    *   *State Evolution:*
        1. Start with $|0\rangle$.
        2. Apply $R_x(11\pi/6)$, which rotates around the X-axis by $11\pi/6$.
        3. State becomes $\cos(11\pi/12)|0\rangle - i\sin(11\pi/12)|1\rangle$.
    *   *Probabilities:* Probability of measuring $|0\rangle$ is $\cos^2(11\pi/12) \approx 0.933$, and $|1\rangle$ is $\sin^2(11\pi/12) \approx 0.067$.

4.  **Refine and Format (applying constraints):**
    *   Keep it concise. 3-8 lines.
    *   Start with "## Reasoning".

    *Draft:*
    ## Reasoning
    - The goal is to initialize a single qubit in the $|0\rangle$ state, apply the rotation gate $R_x(11\pi/6)$, and measure it.
    - The quantum state begins as $|\psi_0\rangle = |0\rangle$.
    - Applying $R_x(\theta)$ transforms the state to $|\psi_1\rangle = \cos(\theta/2)|0\rangle - i\sin(\theta/2)|1\rangle$, where $\theta/2 = 11\pi/12$.
    - The final state is $|\psi_f\rangle = \cos(11\pi/12)|0\rangle - i\sin(11\pi/12)|1\rangle$.
    - The measurement probability of $|0\rangle$ is $\cos^2(11\pi/12) = \frac{2+\sqrt{3}}{4} \approx 0.933$, and for $|1\rangle$ it is $\sin^2(11\pi/12) = \frac{2-\sqrt{3}}{4} \approx 0.067$.

5.  **Final Review against constraints:**
    *   Starts with "## Reasoning"? Yes.
    *   No code blocks? Yes.
    *   Dirac notation used? Yes.
    *   Concise? Yes, 5 lines.
    *   Correct probabilities? Yes.

6.
