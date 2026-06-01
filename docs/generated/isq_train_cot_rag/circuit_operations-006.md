# ISQ training COT RAG corpus: circuit_operations shard 6

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1836

- task_id: `isqTrain/1836`
- task_type: `code_generation`
- category: `circuit_operations`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `2577`

### Prompt

Help me write isQ code that 2 layer(s) of CNOT entanglement on 3 qubits starting from |100>.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply 2 layers of CNOT entanglement on 3 qubits starting from |100>.
2. 3 qubits needed (q[0], q[1], q[2]), all measured at the end.
3. State evolution: |000> → X(q[0]) → |100> → CNOT(q[0],q[1]) → |110> → CNOT(q[1],q[2]) → |111> (Layer 1)
4. Layer 2: CNOT(q[0],q[1]) → |101> → CNOT(q[1],q[2]) → |101> (no flip, q[1]=|0>)
5. Final state |101> gives deterministic measurement: 100% probability of outcome 5 (binary 101).

## isqTrain/1875

- task_id: `isqTrain/1875`
- task_type: `output_prediction`
- category: `circuit_operations`
- difficulty: `intermediate`
- concept_tags: `global_phase`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2745`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[1];
procedure main() {
    Rz(0.0, q[0]);
    Ry(pi, q[0]);
    Rz(pi, q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Output prediction (probability distribution) for an isQ program.
    *   Input program:
        
    *   predicted output format: "## Circuit Analysis" followed by a 3-8 line step-by-step reasoning, concluding with the predicted probability distribution.

2.  **Analyze the Circuit:**
    *   Initial state: $|0\rangle$
    *   Gate 1: `Rz(0.0, q[0])`. Since $\theta = 0$, $R_z(0) = I$ (identity, up to global phase). State remains $|0\rangle$.
    *   Gate 2: `Ry(pi, q[0])`. $R_y(\pi) = \begin{pmatrix} \cos(\pi/2) & -\sin(\pi/2) \\ \sin(\pi/2) & \cos(\pi/2) \end{pmatrix} = \begin{pmatrix} 0 & -1 \\ 1 & 0 \end{pmatrix}$. This maps $|0\rangle$ to $-|1\rangle$ or equivalently, applies $-iY$. Wait, $R_y(\pi) |0\rangle = |1\rangle$ (up to global phase $i$).
        *   Let's check: $R_y(\pi) = e^{-i \frac{\pi}{2} Y} = \cos(\pi/2)I - i\sin(\pi/2)Y = -iY$.
        *   $Y |0\rangle = i|1\rangle$. So $-i(i|1\rangle) = |1\rangle$.
        *   So after `Ry(pi, q[0])`, the state is $|1\rangle$.
    *   Gate 3: `Rz(pi, q[0])`. $R_z(\pi) |1\rangle = e^{-i \pi/2} e^{-i \pi Z/2} |1\rangle$. Since $Z|1\rangle = -|1\rangle$, $R_z(\pi) |1\rangle = e^{-i \pi Z/2} |1\rangle = e^{-i\pi/2} |1\rangle$. This is a global phase (or relative phase if not, but here it's $|1\rangle$). Wait, $R_z(\theta) = e^{-i\theta Z/2}$. For $\theta=\pi$, $R_z(\pi) |1\rangle = e^{i\pi/2} |1\rangle = i|1\rangle$. The state is $i|1\rangle$.
    *   Measurement: $|1\rangle$ probability is $|i|^2 = 1$.

3.  **Formulate the Output:**
    *   **Step-by-step evolution**:
        *   Start: $|0\rangle$
        *   `Rz(0.0)`: No change, state is $|0\rangle$.
        *   `Ry(pi)`: Rotates $\pi$ around Y-axis, mapping $|0\rangle$ to $|1\rangle$ (up to global phase).
        *   `Rz(pi)`: Rotates $\pi$ around Z-axis, applying a global phase of $i$ to $|1\rangle$, resulting in $i|1\rangle$.
        *   `M(q[0])`: Measurement in the computational basis yields $|1\rangle$ with certainty.
    *   **Probability distribution**:
        *   Prob('0') = 0.0
        *   Prob('1') = 1.0
    *   Constrain to the requested format.

4.  **Refine the Output:**
    *   "## Circuit Analysis"
    *   1. The circuit applies an identity $R_z(0)$, followed by a $\pi$ rotation around the Y-axis ($R_y(\pi)$), and a $\pi$ rotation around the Z-axis ($R_z(\pi)$) on a single qubit.
    *   2. The qubit starts in the $|0\rangle$ state. `Rz(0.0)` leaves the state unchanged at $|0\rangle$.
    *   3. `Ry(pi)` applies $-iY$, mapping the state to $|1\rangle$.
    *   4. `Rz(pi)` applies a phase of $i$ to the $|1

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Expected probabilities: [0.0, 1.0]'}

## isqTrain/1310

- task_id: `isqTrain/1310`
- task_type: `code_generation`
- category: `circuit_operations`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3906`

### Prompt

用isQ实现implements the state_preparation pattern with modified rotation parameters (pi2_to_pi3). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Prepare a quantum state via H-Rz(π/3)-H sequence, implementing an effective X-rotation with modified angle.

2. **Qubits**: 1 qubit (q[0]) is used and measured.

3. **State evolution**:
   - Start: |0⟩
   - After H: |+⟩ = (1/√2)(|0⟩ + |1⟩)
   - After Rz(π/3): (1/√2)(e^(-iπ/6)|0⟩ + e^(iπ/6)||1⟩)
   - After H: cos(π/6)|0⟩ - i·sin(π/6)|1⟩

4. **Probabilities**: Since cos(π/6) = √3/2 and sin(π/6) = 1/2, we get P(|0⟩) = cos²(π/6) = 3/4 = 0.75 and P(|1⟩) = sin²(π/6) = 1/4 = 0.25, matching the predicted output.

## isqTrain/2488

- task_id: `isqTrain/2488`
- task_type: `code_equivalence`
- category: `circuit_operations`
- difficulty: `basic`
- concept_tags: `entanglement`, `global_phase`
- source: `isq_train_cot`
- dataset_index: `4922`

### Prompt

这两个isQ程序是等价的吗？

程序A：
```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

程序B：
```isq
import std;
qbit q[2];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    X(q[0]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** applies an X gate to q[0], changing the state from |00> to |10>. It then applies a CNOT with q[0] as control and q[1] as target, entangling them into the |11> state.
2. **Program B** applies a GPhase(0.0) global phase gate, followed by the exact same sequence as Program A (X on q[0], then CNOT on q[0], q[1]). 
3. **The key difference** is the addition of `GPhase(0.0)` at the beginning of Program B, which multiplies the quantum state by $e^{i \cdot 0} = 1$.
4. **The measurement probabilities are exactly the same**. A global phase of 0.0 acts as an identity operation and does not alter the quantum state or measurement outcomes. Both programs yield a 100% probability of measuring the |11> state.
5. **Verdict**: Yes

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/1891

- task_id: `isqTrain/1891`
- task_type: `output_prediction`
- category: `circuit_operations`
- difficulty: `intermediate`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `4404`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[2];
procedure main() {
    H(q[0]); H(q[1]);
    CNOT(q[0], q[1]);
    Rz(pi/4.0, q[1]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants an analysis of the provided isQ quantum program to predict its measurement probability distribution. The output must be a "Circuit Analysis" section, concisely explaining the state evolution in Dirac notation, and ending with the predicted probabilities.

2.  **Analyze the Circuit:**
    *   Initial state: $|00\rangle$
    *   `H(q[0]); H(q[1]);` -> Apply Hadamard to both qubits: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$
    *   `CNOT(q[0], q[1]);` -> Control is $q_0$, target is $q_1$.
        *   $|00\rangle \to |00\rangle$
        *   $|01\rangle \to |01\rangle$
        *   $|10\rangle \to |11\rangle$
        *   $|11\rangle \to |10\rangle$
        State becomes $\frac{1}{2}(|00\rangle + |01\rangle + |11\rangle + |10\rangle) = \frac{1}{2}(|0\rangle(|0\rangle+|1\rangle) + |1\rangle(|1\rangle+|0\rangle)) = \frac{1}{2}(|0\rangle + |1\rangle) \otimes (|0\rangle + |1\rangle)$. Wait, let's look at the terms: $|00\rangle + |01\rangle + |11\rangle + |10\rangle$. This is exactly the same superposition as before, just reordered!
    *   `Rz(pi/4.0, q[1]);` -> Applies a phase to $|1\rangle$ of $q_1$.
        *   $|00\rangle \to |00\rangle$
        *   $|01\rangle \to e^{i\pi/4}|01\rangle$
        *   $|11\rangle \to e^{i\pi/4}|11\rangle$
        *   $|10\rangle \to |10\rangle$
        State: $\frac{1}{2}(|00\rangle + e^{i\pi/4}|01\rangle + |10\rangle + e^{i\pi/4}|11\rangle) = \frac{1}{2}(|0\rangle + |1\rangle) \otimes (|0\rangle + e^{i\pi/4}|1\rangle)$
    *   `CNOT(q[0], q[1]);` -> Same as before.
        *   $|00\rangle \to |00\rangle$
        *   $e^{i\pi/4}|01\rangle \to e^{i\pi/4}|01\rangle$
        *   $|10\rangle \to |11\rangle$
        *   $e^{i\pi/4}|11\rangle \to e^{i\pi/4}|10\rangle$
        State: $\frac{1}{2}(|00\rangle + e^{i\pi/4}|01\rangle + e^{i\pi/4}|10\rangle + |11\rangle)$.
    *   Measurement: Probabilities are the squared magnitudes of the amplitudes.
        *   P(00) = $(1/2)^2 = 1/4 = 0.25$
        *   P(01) = $(1/2)^2 = 1/4 = 0.25$
        *   P(10) = $(1/2)^2 = 1/4 = 0.25$
        *   P(11) = $(1/2)^2 = 1/4 = 0.25$

3.  **Format the Output:**
    *   Start with "## Circuit Analysis"
    *   Keep it 3-8 lines (this is simple).
    *   Use Dirac notation.
    *   End with the predicted probability distribution.

4.  **Drafting the text:**
    ## Circuit Analysis
    1. **Initialization & Superposition:** The circuit starts in $|00\rangle$. Applying `H` to both yields $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
    2. **First CNOT:** `CNOT(q[0], q[1])` swaps $|10\rangle \leftrightarrow |11\rangle$, but the state vector remains an equal superposition of all 4 states: $\frac{1}{2}(|00\rangle + |01\rangle + |11\rangle

### Reference answer

{'predicted_probs': {'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25}, 'explanation': 'Expected probabilities: [0.25, 0.25, 0.25, 0.25]'}

## isqTrain/600

- task_id: `isqTrain/600`
- task_type: `code_generation`
- category: `circuit_operations`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3466`

### Prompt

I need an isQ program to implements a variant of the gate_decomposition pattern using q[5] -> q[7]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

Let me analyze this task carefully.

The task asks me to write an isQ program that implements a variant of the gate_decomposition pattern using q[5] -> q[7]. The circuit should use a significantly expanded qubit register compared to the base version, with additional qubits left in the ground state.

Analyzing the circuit requirements:
- It has 7 qubits
- It applies Ry(π) rotations to q[0] through q[4]
- It measures all qubits

The expected measurement probability is {|0011111>: 1.0}

Wait, this is interesting. The predicted output |0011111> with probability 1.0, which means:
- q[0] = 0
- q[1] = 0
- q[2] = 1
- q[3] = 1
- q[4] = 1
- q[5] = 1
- q[6] = 1

But In the implementation, Ry(π) is applied to q[0] through q[4], and q[5] and q[6] are left alone (in |0>).

Wait, let me think about what Ry(π) does:
Ry(θ) = [[cos(θ/2), -sin(θ/2)], [sin(θ/2), cos(θ/2)]]

Ry(π) = [[cos(π/2), -sin(π/2)], [sin(π/2), cos(π/2)]]
      = [[0, -1], [1, 0]]

So Ry(π)|0> = |1>
And Ry(π)|1> = -|0>

So applying Ry(π) to |0> gives |1>.

So after the rotations:
- q[0] through q[4] should be in |1> state
- q[5] and q[6] should be in |0> state

So the expected state should be |1111100>, not |0011111>.

Hmm, but The predicted output |0011111>. Let me think about the bit ordering in isQ.

In the --probs output, "earlier measured qubit = higher bit". So if we measure q[0], q[1], ..., q[6], then q[0] is the highest bit.

So |0011111> means:
- Bit 6 (highest) = q[0] = 0
- Bit 5 = q[1] = 0
- Bit 4 = q[2] = 1
- Bit 3 = q[3] = 1
- Bit 2 = q[4] = 1
- Bit 1 = q[5] = 1
- Bit 0 (lowest) = q[6] = 1

Wait, that doesn't match either. Let me re-read.

Actually, |0011111> as a bitstring:
- Position 0 (leftmost): 0
- Position 1: 0
- Position 2: 1
- Position 3: 1
- Position 4: 1
- Position 5: 1
- Position 6: 1

If "earlier measured qubit = higher bit", and we measure q in order, then:
- q[0] is the highest bit (bit 6)
- q[6] is the lowest bit (bit 0)

So |0011111> = 0*64 + 0*32 + 1*16 + 1*8 + 1*4 + 1*2 + 1*1 = 31

Wait, let me reconsider. The bitstring "0011111" for 7 qubits:
- The leftmost '0' corresponds to the highest bit position
- The rightmost '1' corresponds to the lowest bit position

So if q[0] is the highest bit:
- q[0] = 0
- q[1] = 0
- q[2] = 1
- q[3] = 1
- q[4] = 1
- q[5] = 1
- q[6] = 1

But the reference applies Ry(π) to q[0] through q[4], which would put them in |1> state. And q[5], q[6] are untouched, so they're in |0> state.

This doesn't match! Let me re-check...

Actually wait, the task says "using q[5] -> q[7]". Maybe the task is asking for a different circuit than The implementation?

Let me re-read the task:
- "Write an isQ program that implements a variant of the gate_decomposition pattern using q

## isqTrain/1896

- task_id: `isqTrain/1896`
- task_type: `output_prediction`
- category: `circuit_operations`
- difficulty: `basic`
- concept_tags: `isq_syntax_deriving_gate`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5728`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[1];
procedure main() {
    H(q[0]);
    inv S(q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. Operations: Hadamard (H) gate followed by the inverse S gate ($S^\dagger$).
2. State evolution: Starts at $|0\rangle$. After H, it is in the superposition $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
3. The $S^\dagger$ gate applies a $-\pi/2$ phase to the $|1\rangle$ state, evolving the state to $\frac{1}{\sqrt{2}}(|0\rangle - i|1\rangle)$.
4. Measurement probabilities are determined by the squared magnitudes of the amplitudes, which are both $\left|1/\sqrt{2}\right|^2 = 0.5$.

Predicted probability distribution: {'0': 0.5, '1': 0.5}

### Reference answer

{'predicted_probs': {'0': 0.5, '1': 0.5}, 'explanation': 'Expected probabilities: [0.5, 0.5]'}

## isqTrain/1328

- task_id: `isqTrain/1328`
- task_type: `output_prediction`
- category: `circuit_operations`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1221`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[1];

procedure main() {
    Ry(pi/6.0, q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The qubit `q[0]` is initialized to the state |0>.
2. The circuit applies an `Ry` rotation gate with an angle of $\pi/6$ to `q[0]`.
3. This gate evolves the state from |0> to $\cos(\pi/12)|0\rangle + \sin(\pi/12)|1\rangle$.
4. Before measurement, the quantum state is approximately $0.9659|0\rangle + 0.2588|1\rangle$.
5. The probability of measuring the outcome 0 (state |0>) is $\cos^2(\pi/12) \approx 0.9330$.
6. The probability of measuring the outcome 1 (state |1>) is $\sin^2(\pi/12) \approx 0.0670$.

Predicted probability distribution: {|0>: 0.9330127018922194, |1>: 0.06698729810778066}

### Reference answer

{'predicted_probs': {'0': 0.9330127018922194, '1': 0.06698729810778066}, 'explanation': 'Parametric variant of isqEval/480. Dimension: param_variant: pi4_to_pi6.'}

## isqTrain/547

- task_id: `isqTrain/547`
- task_type: `output_prediction`
- category: `circuit_operations`
- difficulty: `basic`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `2803`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;
qbit q[3];

procedure main() {
    X(q[0]);
    ctrl ctrl X(q[0], q[1], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Gates applied**: `X(q[0])`, `ctrl ctrl X(q[0], q[1], q[2])` (Toffoli)
2. **State evolution**:
   - Initial state: |000>
   - `X(q[0])`: Flips q[0] to |1>, state becomes |100>
   - `ctrl ctrl X(q[0], q[1], q[2])`: Checks if q[0] and q[1] are both |1>. Since q[1] is |0>, the target q[2] is not flipped.
3. **Final state**: |100>
4. **Predicted probability distribution**: {|100>: 1.0}

### Reference answer

{'predicted_probs': {'4': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/168. Dimension: predict probabilities for reference circuit.'}

## isqTrain/1331

- task_id: `isqTrain/1331`
- task_type: `output_prediction`
- category: `circuit_operations`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1007`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    Rz(pi/6.0, q[0]);
    H(q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict measurement outcomes for a given isQ program.
    *   Output: "## Circuit Analysis" followed by step-by-step reasoning (3-15 lines), ending with the predicted probability distribution.
    *   Constraint: Use Dirac notation, no code blocks, concise.

2.  **Analyze the isQ Program:**
    

3.  **State Evolution:**
    *   Initial state: $|0\rangle$
    *   After `H(q[0])`: $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$
    *   After `Rz(pi/6.0, q[0])` (applies a phase of $e^{-i\pi/12}$ to $|0\rangle$ and $e^{i\pi/12}$ to $|1\rangle$ - actually, standard Rz matrix is $[[e^{-i\theta/2}, 0], [0, e^{i\theta/2}]]$. So phase diff is $\theta = \pi/6$):
        $e^{-i\pi/12}|0\rangle + e^{i\pi/12}|1\rangle$. (Up to global phase $e^{i\pi/12}$, this is $|0\rangle + e^{i\pi/6}|1\rangle$)
    *   Let's use the global phase to simplify: $e^{i\pi/12} (e^{-i\pi/6}|0\rangle + |1\rangle)$.
        Or simply $| \psi \rangle = \frac{1}{\sqrt{2}} (e^{-i\pi/12}|0\rangle + e^{i\pi/12}|1\rangle)$.
    *   After `H(q[0])`:
        $H = \frac{1}{\sqrt{2}} \begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix}$
        $H |\psi\rangle = \frac{1}{2} \begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix} \begin{pmatrix} e^{-i\pi/12} \\ e^{i\pi/12} \end{pmatrix} = \frac{1}{2} \begin{pmatrix} e^{-i\pi/12} + e^{i\pi/12} \\ e^{-i\pi/12} - e^{i\pi/12} \end{pmatrix}$
        $= \begin{pmatrix} \cos(\pi/12) \\ -i \sin(\pi/12) \end{pmatrix}$
    *   Probabilities:
        $P(0) = \cos^2(\pi/12) = \frac{1 + \cos(\pi/6)}{2} = \frac{1 + \sqrt{3}/2}{2} = \frac{2 + \sqrt{3}}{4} \approx 0.93301$
        $P(1) = \sin^2(\pi/12) = \frac{1 - \cos(\pi/6)}{2} = \frac{1 - \sqrt{3}/2}{2} = \frac{2 - \sqrt{3}}{4} \approx 0.06699$

4.  **Draft the Explanation (concise, 3-8 lines):**
    *   Start with "## Circuit Analysis"
    *   Initial state is $|0\rangle$.
    *   Hadamard $H$ changes state to $|+\rangle = \frac{1}{\sqrt{2}}|0\rangle + \frac{1}{\sqrt{2}}|1\rangle$.
    *   $R_z(\pi/6)$ applies phase $e^{-i\pi/12}$ to $|0\rangle$ and $e^{i\pi/12}$ to $|1\rangle$.
    *   Applying $H$ again yields $\cos(\pi/12)|0\rangle - i\sin(\pi/12)|1\rangle$.
    *   Measurement probabilities are $|\cos(\pi/12)|^2$ for $|0\rangle$ and $|\sin(\pi/12)|^2$ for $|1\rangle$.
    *   State final probabilities.

5.  **Refine to constraints:**
    *   Check predicted output values: 0.9

### Reference answer

{'predicted_probs': {'0': 0.9330127018922194, '1': 0.06698729810778067}, 'explanation': 'Parametric variant of isqEval/481. Dimension: param_variant: pi4_to_pi6.'}
