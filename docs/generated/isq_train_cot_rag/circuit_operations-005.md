# ISQ training COT RAG corpus: circuit_operations shard 5

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1332

- task_id: `isqTrain/1332`
- task_type: `output_prediction`
- category: `circuit_operations`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `985`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[2];

procedure main() {
    H(q[0]);
    Rz(pi/4.0, q[0]);
    H(q[0]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the isQ program:**
    *   2 qubits: `q[0]` and `q[1]`.
    *   Initial state: $|00\rangle$.
    *   Operations:
        *   `H(q[0])`: Apply Hadamard to q[0].
        *   `Rz(pi/4.0, q[0])`: Apply Rz($\pi/4$) to q[0].
        *   `H(q[0])`: Apply Hadamard to q[0].
        *   `M(q[0]); M(q[1]);`: Measure both.

2.  **Step-by-step quantum state evolution:**
    *   Initial: $|\psi_0\rangle = |00\rangle$
    *   After `H(q[0])`: $|\psi_1\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes |0\rangle = \frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$
    *   After `Rz(\pi/4, q[0])`: Rz($\theta$) = $\begin{pmatrix} e^{-i\theta/2} & 0 \\ 0 & e^{i\theta/2} \end{pmatrix}$. Wait, isQ's Rz definition matches standard: $R_z(\theta) = e^{-i\theta Z / 2} = \begin{pmatrix} e^{-i\theta/2} & 0 \\ 0 & e^{i\theta/2} \end{pmatrix}$.
        *   $|\psi_2\rangle = \frac{1}{\sqrt{2}}(e^{-i\pi/8}|0\rangle + e^{i\pi/8}|1\rangle) \otimes |0\rangle$
    *   After `H(q[0])`: Apply H to the first qubit.
        *   $H(e^{-i\pi/8}|0\rangle + e^{i\pi/8}|1\rangle) = \frac{1}{\sqrt{2}} [ e^{-i\pi/8}(|0\rangle + |1\rangle) + e^{i\pi/8}(|0\rangle - |1\rangle) ]$
        *   $= \frac{1}{\sqrt{2}} [ (e^{-i\pi/8} + e^{i\pi/8})|0\rangle + (e^{-i\pi/8} - e^{i\pi/8})|1\rangle ]$
        *   $= \frac{1}{\sqrt{2}} [ 2\cos(\pi/8)|0\rangle - 2i\sin(\pi/8)|1\rangle ]$
        *   $= \cos(\pi/8)|0\rangle - i\sin(\pi/8)|1\rangle$
    *   Final state:
        *   $|\psi_3\rangle = (\cos(\pi/8)|0\rangle - i\sin(\pi/8)|1\rangle) \otimes |0\rangle = \cos(\pi/8)|00\rangle - i\sin(\pi/8)|10\rangle$

3.  **Probability distribution:**
    *   $P(|00\rangle) = |\cos(\pi/8)|^2 = \cos^2(\pi/8) \approx \frac{1 + \cos(\pi/4)}{2} = \frac{1 + 1/\sqrt{2}}{2} = \frac{2 + \sqrt{2}}{4} = 0.8535533905932737$
    *   $P(|10\rangle) = |-i\sin(\pi/8)|^2 = \sin^2(\pi/8) \approx \frac{1 - \cos(\pi/4)}{2} = \frac{1 - 1/\sqrt{2}}{2} = \frac{2 - \sqrt{2}}{4} = 0.14644660940672627$
    *   Wait, the qubits are measured `M(q[0]); M(q[1]);`. Since `q[0]` is 0 implies `|0>` and 1 implies `|1>`, if `q[0]` is 0, string is `00`. If `q[0]` is 1, string is `10`.
    *   Probabilities are $P(00) = 0.85355...$, $P(10) = 0.

### Reference answer

{'predicted_probs': {'0': 0.8535533905932737, '2': 0.14644660940672627}, 'explanation': 'Parametric variant of isqEval/481. Dimension: qubit_variant: q[1] -> q[2].'}

## isqTrain/1982

- task_id: `isqTrain/1982`
- task_type: `output_prediction`
- category: `circuit_operations`
- difficulty: `basic`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `5654`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

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
1. **Initial state**: The 3-qubit system starts in the ground state |000>.
2. **X gate**: The `X(q[0])` gate flips the first qubit, evolving the state to |100>.
3. **Toffoli gate**: The `ctrl ctrl X(q[0], q[1], q[2])` operation applies an X gate to `q[2]` only if both `q[0]` and `q[1]` are in the |1> state. Since `q[1]` is |0>, the condition is not met, and the state remains |100>.
4. **Measurement**: Measuring the qubits deterministically yields the classical bitstring 100.

Predicted probability distribution: {'100': 1.0}

### Reference answer

{'predicted_probs': {'100': 1.0}, 'explanation': 'Only one control is 1 in |100>, so Toffoli is inactive and |100> remains with probability 1.0.'}

## isqTrain/1889

- task_id: `isqTrain/1889`
- task_type: `output_prediction`
- category: `circuit_operations`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3850`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;
qbit q[1];
procedure main() {
    Rz(pi/8.0, q[0]);
    Ry(pi/2.0, q[0]);
    Rz(pi/4.0, q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit applies a sequence of rotation gates $Rz(\pi/8)$, $Ry(\pi/2)$, and $Rz(\pi/4)$ to a single qubit initialized to $|0\rangle$.
2. The initial state is $|0\rangle$. The first gate $Rz(\pi/8)$ applies a phase shift, resulting in $e^{-i\pi/16}|0\rangle$.
3. Next, $Ry(\pi/2)$ rotates the state around the Y-axis, yielding $\frac{1}{\sqrt{2}}e^{-i\pi/16}(|0\rangle + |1\rangle)$.
4. Finally, $Rz(\pi/4)$ applies another phase shift, resulting in the final state $\frac{1}{\sqrt{2}}e^{-i\pi/16}(e^{-i\pi/8}|0\rangle + e^{i\pi/8}|1\rangle)$.
5. Because the final state is an equal superposition of $|0\rangle$ and $|1\rangle$ (up to global and relative phases which do not affect measurement probabilities), the probability of measuring each outcome is equal.

Predicted probability distribution: {'0': 0.5, '1': 0.5}

### Reference answer

{'predicted_probs': {'0': 0.5, '1': 0.5}, 'explanation': 'Expected probabilities: [0.5000000000000001, 0.4999999999999999]'}

## isqTrain/171

- task_id: `isqTrain/171`
- task_type: `code_generation`
- category: `circuit_operations`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `907`

### Prompt

帮我写一个isQ程序：implements the gate_decomposition pattern but with a different initial state preparation (flip q[[0]] -> q[1]).

### Chain-of-thought reasoning

## Reasoning
1. The goal is to initialize the second qubit (q[1]) to the |1> state and then apply a controlled-Ry gate.
2. The circuit requires 2 qubits, and both q[0] and q[1] are measured.
3. Starting in the |00> state, the X gate on q[1] flips the state to |01>.
4. Next, a controlled-Ry(pi/4.0) gate is applied with q[0] as the control and q[1] as the target.
5. Because the control qubit q[0] remains in the |0> state, the controlled gate is not triggered, leaving the target q[1] unchanged and the overall state as |01>.
6. Consequently, the measurement probabilities are perfectly deterministic, yielding exactly |01> with probability 1.0.

## isqTrain/2503

- task_id: `isqTrain/2503`
- task_type: `code_equivalence`
- category: `circuit_operations`
- difficulty: `intermediate`
- concept_tags: `global_phase`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5239`

### Prompt

Will these two quantum programs produce identical measurement outcomes?

```isq
import std;
qbit q[1];

procedure main() {
    Rz(pi/4.0, q[0]);
    Ry(pi/2.0, q[0]);
    Rz(pi/2.0, q[0]);
    M(q[0]);
}

```

vs.

```isq
import std;
qbit q[1];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    Rz(pi/4.0, q[0]);
    Ry(pi/2.0, q[0]);
    Rz(pi/2.0, q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. Program A applies a sequence of rotations `Rz(pi/4)`, `Ry(pi/2)`, and `Rz(pi/2)` to the initial |0> state of qubit q[0], followed by a measurement.
2. Program B applies the exact same sequence of rotational gates and measurement to q[0].
3. The only difference between the two programs is the addition of `GPhase(0.0)` in Program B before the other gates.
4. The `GPhase(0.0)` gate multiplies the overall quantum state by a phase factor of $e^{i \cdot 0} = 1$. This acts as an identity operation, leaving the state vector completely unchanged.
5. Because both programs produce identical quantum states prior to measurement, their measurement probability distributions are exactly the same.

Equivalent: True

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/152

- task_id: `isqTrain/152`
- task_type: `code_generation`
- category: `circuit_operations`
- difficulty: `basic`
- concept_tags: `isq_syntax_inv`, `superposition`
- source: `isq_train_cot`
- dataset_index: `115`

### Prompt

用isQ实现implements the gate_decomposition pattern using an alternative gate decomposition (S -> T T). The circuit must produce the same output as the standard decomposition.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement a circuit using the decomposition S = T·T, where inv T followed by T cancels, demonstrating equivalent behavior.

2. **Qubits**: 1 qubit `q[0]`, measured at the end.

3. **State evolution**:
   - Start: |0⟩
   - After Rx(π/4): cos(π/8)|0⟩ - i·sin(π/8)|1⟩
   - After inv T then T: gates cancel (T†·T = I), state unchanged
   - After H: [cos(π/8) - i·sin(π/8)]/√2 |0⟩ + [cos(π/8) + i·sin(π/8)]/√2 |1⟩

4. **Probabilities**: |cos(π/8) ∓ i·sin(π/8)|²/2 = (cos²+sin²)/2 = 1/2 each, giving P(|0⟩) = P(|1⟩) = 0.5.

## isqTrain/4630

- task_id: `isqTrain/4630`
- task_type: `output_prediction`
- category: `circuit_operations`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `2213`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[3];

procedure main() {
    X(q[2]);  // target different qubit
    X(q[1]);
    ctrl ctrl X(q[0], q[1], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Role:** Quantum computing expert.
    *   **Task:** Generate concise, precise step-by-step reasoning for an isQ quantum program.
    *   **Notation:** Dirac notation (|0>, |1>, etc.).
    *   **Length:** 3-8 lines for simple circuits.
    *   **Format:** Output ONLY the analysis, starting with "## Circuit Analysis", ending with the predicted probability distribution.
    *   **Input Program:**
        
    *   **predicted output:** Probabilities for state |011>: 1.0 (as given in the prompt's reference). Wait, let me trace it myself to be sure.

2.  **Trace the Circuit:**
    *   Initial state: |000> (qubits q[0], q[1], q[2])
    *   `X(q[2])`: q[2] becomes 1 -> state is |001>
    *   `X(q[1])`: q[1] becomes 1 -> state is |011>
    *   `ctrl ctrl X(q[0], q[1], q[2])`:
        *   This is a Toffoli-like gate (doubly-controlled X).
        *   Controls: q[0], q[1]. Target: q[2].
        *   Wait, look at the syntax `ctrl ctrl X(q[0], q[1], q[2])`. In isQ, `ctrl ctrl X(q[0], q[1], q[2])` might mean q[0] and q[1] are controls and q[2] is target, OR q[0] is control 1, q[1] is control 2 (or target?).
        *   Let's check standard isQ syntax for `ctrl ctrl X(a, b, c)`.
        *   Wait, standard X is `X(target)`. If you do `ctrl X(c, t)`, it's CNOT. If you do `ctrl ctrl X(c1, c2, t)`, it's Toffoli.
        *   So here, `q[0]` is control 1, `q[1]` is control 2, `q[2]` is target.
        *   Current state is |011> (q[0]=0, q[1]=1, q[2]=1).
        *   Control condition: q[0] must be |1>. Since q[0] is |0>, the Toffoli gate does nothing.
    *   Final state: |011>.
    *   Measurement: q[0]=0, q[1]=1, q[2]=1. Bitstring 011.
    *   Wait, the prompt says "Expected measurement probabilities: {|011>: 1.0}". This matches my trace perfectly.

3.  **Draft the Analysis:**
    *   *Line 1:* Initial state is |000>.
    *   *Line 2:* `X(q[2])` flips q[2], resulting in |001>.
    *   *Line 3:* `X(q[1])` flips q[1], resulting in |011>.
    *   *Line 4:* `ctrl ctrl X(q[0], q[1], q[2])` acts as a Toffoli gate with q[0], q[1] as controls and q[2] as target.
    *   *Line 5:* Since q[0] is in |0>, the control condition is not met, and the target q[2] remains unchanged.
    *   *Line 6:* The final state is |011>.
    *   *Line 7:* Measurements of q[0], q[1], q[2] yield 0, 1, 1 respectively.

4.  **Refine to meet length and style constraints (3-8 lines):**
    *   Start with `## Circuit Analysis`.
    *   Combine the X gates step.
    *   Conclude with probability distribution.

    *Draft:*
    ## Circuit Analysis
    1. The circuit starts in the initial state |000>.
    2. Applying `X(q[2])` and `X(q[1])` flips the respective qubits, evolving the state to |011>.
    3. The `ctrl ctrl X(q[0], q[1], q[2])` gate acts as a Toffoli gate with q[0] and q[1] as controls and q

### Reference answer

{'predicted_probs': {'011': 1.0}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|011>) = 1.0000.'}

## isqTrain/1787

- task_id: `isqTrain/1787`
- task_type: `code_generation`
- category: `circuit_operations`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3495`

### Prompt

请用isQ语言编写一个量子电路：Reverse the qubit order of 5 qubits using SWAP gates. Start with |10000>.

### Chain-of-thought reasoning

## Reasoning
1. The circuit reverses the order of 5 qubits using swap (three-CNOT decomposition) gates, starting from state |10000>.
2. It requires 5 qubits, all of which are measured at the end.
3. An X gate initializes qubit 0 to 1, yielding the state |10000>.
4. swap (three-CNOT decomposition)(q[0], q[4]) exchanges qubits 0 and 4, evolving the state to |00001>.
5. swap (three-CNOT decomposition)(q[1], q[3]) exchanges qubits 1 and 3, leaving the state unchanged at |00001>.
6. The final state is exactly |00001>, yielding a 100% measurement probability for this state.

## isqTrain/1344

- task_id: `isqTrain/1344`
- task_type: `output_prediction`
- category: `circuit_operations`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4365`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;

qbit q[4];

procedure main() {
    H(q);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes 4 qubits in the ground state |0000>.
2. The Hadamard gate `H(q)` is applied to all 4 qubits, putting each into an equal superposition |+> = (1/sqrt(2)) (|0> + |1>).
3. The resulting joint quantum state is H^⊗4 |0000> = 1/4 ∑ (from x=0 to 15) |x>, which is a uniform superposition of all 16 possible computational basis states.
4. Measuring all qubits collapses this equal superposition, yielding each of the 16 possible outcomes with identical probability.
5. The probability for any specific state is (1/2)^4 = 1/16 = 0.0625.

Predicted probability distribution: {|0000>: 0.06250000000000001, |0001>: 0.06250000000000001, |0010>: 0.06250000000000001, |0011>: 0.06250000000000001, |0100>: 0.06250000000000001, |0101>: 0.06250000000000001, |0110>: 0.06250000000000001, |0111>: 0.06250000000000001, |1000>: 0.06250000000000001, |1001>: 0.06250000000000001,

### Reference answer

{'predicted_probs': {'0': 0.06250000000000001, '1': 0.06250000000000001, '2': 0.06250000000000001, '3': 0.06250000000000001, '4': 0.06250000000000001, '5': 0.06250000000000001, '6': 0.06250000000000001, '7': 0.06250000000000001, '8': 0.06250000000000001, '9': 0.06250000000000001, '10': 0.06250000000000001, '11': 0.06250000000000001, '12': 0.06250000000000001, '13': 0.06250000000000001, '14': 0.06250000000000001, '15': 0.06250000000000001}, 'explanation': 'Parametric variant of isqEval/490. Dimension: qubit_variant: q[3] -> q[4].'}

## isqTrain/1867

- task_id: `isqTrain/1867`
- task_type: `output_prediction`
- category: `circuit_operations`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2246`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

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

1.  **Analyze the request:**
    *   Task: Analyze an isQ program, predict measurement probabilities.
    *   Program: H(q[0]); Rz(pi/2.0, q[0]); H(q[0]); M(q[0]);
    *   Output format: "## Circuit Analysis", step-by-step reasoning, Dirac notation, concise (3-15 lines), NO code blocks, end with predicted probability distribution.

2.  **Analyze the circuit:**
    *   Initial state: $|0\rangle$
    *   Apply H(q[0]): $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$
    *   Apply Rz($\pi/2$, q[0]): $R_z(\theta) = \begin{pmatrix} e^{-i\theta/2} & 0 \\ 0 & e^{i\theta/2} \end{pmatrix}$. For $\theta = \pi/2$: $\begin{pmatrix} e^{-i\pi/4} & 0 \\ 0 & e^{i\pi/4} \end{pmatrix}$.
        *   State becomes: $\frac{1}{\sqrt{2}}(e^{-i\pi/4}|0\rangle + e^{i\pi/4}|1\rangle)$
        *   Factoring out global phase $e^{-i\pi/4}$: $\frac{e^{-i\pi/4}}{\sqrt{2}}(|0\rangle + e^{i\pi/2}|1\rangle) = \frac{e^{-i\pi/4}}{\sqrt{2}}(|0\rangle + i|1\rangle)$
        *   Wait, $|0\rangle + i|1\rangle$ is the same as $S|+\rangle$ (up to global phase).
    *   Apply H(q[0]):
        *   Current state (ignoring global phase): $\frac{1}{\sqrt{2}}(|0\rangle + i|1\rangle)$
        *   $H \frac{1}{\sqrt{2}}(|0\rangle + i|1\rangle) = \frac{1}{\sqrt{2}}(H|0\rangle + iH|1\rangle)$
        *   $H|0\rangle = |+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$
        *   $H|1\rangle = |-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$
        *   Combine: $\frac{1}{2} (|0\rangle + |1\rangle + i|0\rangle - i|1\rangle) = \frac{1}{2} ((1+i)|0\rangle + (1-i)|1\rangle)$
    *   Calculate probabilities:
        *   $P(0) = |\frac{1+i}{2}|^2 = (\frac{1}{2})^2 + (\frac{1}{2})^2 = \frac{1}{4} + \frac{1}{4} = \frac{1}{2}$
        *   $P(1) = |\frac{1-i}{2}|^2 = (\frac{1}{2})^2 + (-\frac{1}{2})^2 = \frac{1}{4} + \frac{1}{4} = \frac{1}{2}$

3.  **Draft the response:**
    *   Start with `## Circuit Analysis`
    *   State initial: |0>
    *   Apply H: |+> = (|0> + |1>)/√2
    *   Apply Rz(π/2): (|0> + i|1>)/√2
    *   Apply H: ((1+i)|0> + (1-i)|1>)/2
    *   Calculate probabilities: P(0) = 0.5, P(1) = 0.5.
    *   Ensure strict adherence to rules (concise, no code blocks).

4.  **Refine reasoning for length and clarity:**
    *   1. Initial state is |0>.
    *   2. H(q[0]) creates superposition |+> = (|0> + |1>)/√2.
    *   3. Rz(π/2, q[0]) applies a phase shift, yielding (|0> + i|1>)/√2 (ignoring global phase).
    *   4. H(q[0]) maps this to ((1+i)|0>

### Reference answer

{'predicted_probs': {'0': 0.5, '1': 0.5}, 'explanation': 'Expected probabilities: [0.5, 0.4999999999999999]'}
