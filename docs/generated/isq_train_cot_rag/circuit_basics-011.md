# ISQ training COT RAG corpus: circuit_basics shard 11

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1988

- task_id: `isqTrain/1988`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `entanglement`, `measurement_order`
- source: `isq_train_cot`
- dataset_index: `228`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[2];
procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    M(q[1]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a concise, precise step-by-step analysis of an isQ quantum program, predicting its measurement probability distribution. The output must start with "## Circuit Analysis", use Dirac notation, and end with the predicted probabilities.

2.  **Analyze the isQ Code:**
    *   `qbit q[2];` -> Initialize 2 qubits, `q[0]` and `q[1]`, in state |00>.
    *   `H(q[0]);` -> Apply Hadamard gate to `q[0]`.
    *   `CNOT(q[0], q[1]);` -> Apply CNOT with `q[0]` as control and `q[1]` as target.
    *   `M(q[1]);` -> Measure `q[1]`.
    *   `M(q[0]);` -> Measure `q[0]`.

3.  **Step-by-Step Quantum State Evolution:**
    *   *Initial state:* $|00\rangle$
    *   *After H(q[0]):* $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes |0\rangle = \frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$
    *   *After CNOT(q[0], q[1]):* The control is `q[0]` and target is `q[1]`. $|00\rangle \to |00\rangle$, $|10\rangle \to |11\rangle$. Final state is $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$. This is a Bell state.

4.  **Predict Measurement Outcomes:**
    *   The measurements are `M(q[1])` then `M(q[0])`.
    *   The bitstring format in `--probs` typically lists the earlier measured qubit as the higher bit or vice-versa depending on the exact simulator convention, but standard isQ `--probs` standardly uses the qubit index order (q[0] is highest or q[0] is lowest). Wait, the prompt says: "earlier measured qubit = higher bit".
    *   Let's check the prompt: "--probs output: array indexed by measurement bitstring (earlier measured qubit = higher bit)."
    *   `M(q[1])` is the *earlier* measurement. Therefore, the result of `q[1]` is the *higher bit* (leftmost bit).
    *   `M(q[0])` is the later measurement. Its result is the lower bit (rightmost bit).
    *   Wait, the final state is an equal superposition of |00> and |11>, where the left bit is q[0] and right is q[1].
    *   Let's write the state in terms of the bitstring ordering requested: "earlier measured qubit = higher bit". Earlier measured is `q[1]`. So the bitstring format is `q[1]q[0]`.
    *   State in standard notation (q[0]q[1]): $|00\rangle + |11\rangle$.
    *   Wait, if earlier measured is `q[1]`, the bitstring is $q_1 q_0$.
    *   For $|00\rangle_{q_0 q_1}$, $q_1=0, q_0=0$. Bitstring: 00.
    *   For $|11\rangle_{q_0 q_1}$, $q_1=1, q_0=1$. Bitstring: 11.
    *   So the probabilities are P(00) = 0.5, P(11) = 0.5. This perfectly matches the Expected measurement probabilities in the prompt: {'00': 0.5, '11': 0.5}.

5.  **Draft the Circuit Analysis (Concise & Precise):**
    *   Initial state: |00>
    *   Apply H(q[0]): 1/sqrt(2) * (|00> + |10>)
    *   Apply CNOT(q[0], q[1]): 1/sqrt(2) * (|00> + |11>) (Bell state)
    *   Measurements M(q[1]) then M(q[0]) collapse the state. Since earlier measured qubit (q[1]) is the higher bit, the bitstring is q[1]q[0].
    *   Both basis states |00> and |11> have equal amplitudes.
    *   Probabilities: {'00': 0.5, '

### Reference answer

{'predicted_probs': {'00': 0.5, '11': 0.5}, 'explanation': 'Expected probabilities: [0.5, 0.0, 0.0, 0.5]'}

## isqTrain/4753

- task_id: `isqTrain/4753`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `5316`

### Prompt

Determine if these two isQ implementations are functionally equivalent:

Version A:
```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    X(q[1]);
    H(q[1]);
    CNOT(q[0], q[1]);
    H(q[1]);
    M(q[0]); M(q[1]);
}

```

Version B:
```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    X(q[1]);
    CNOT(q[0], q[1]);
    H(q[0]); // add superposition
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis

**Program A:**
1. Start: |00⟩ → X(q[0]), X(q[1]) → |11⟩
2. H(q[1]) → (|10⟩ − |11⟩)/√2
3. CNOT(q[0], q[1]) → (|11⟩ − |10⟩)/√2
4. H(q[1]) → −|11⟩ ≡ |11⟩ (global phase irrelevant)

Final state: |11⟩ → P(11) = 1

**Program B:**
1. Start: |00⟩ → X(q[0]), X(q[1]) → |11⟩
2. CNOT(q[0], q[1]) → |10⟩
3. H(q[0]) → (|00⟩ − |10⟩)/√2

Final state: (|00⟩ − |10⟩)/√2 → P(00) = 1/2, P(10) = 1/2

**Key Difference:** The H gates are applied to different qubits at different positions in the circuit. In Program A, H acts on q[1] before and after the CNOT, effectively canceling its effect and returning to |11⟩. In Program B, H acts on q[0] after the CNOT, creating a superposition over q[0].

**Verdict:** The probability distributions are different (Program A: always 11; Program B: 50/50 for 00 and 10).

**Not equivalent: No**

### Reference answer

{'equivalent': False, 'explanation': 'After adding H gate to Program B, the programs produce different probability distributions.', 'probs_a': {'11': 1.0}, 'probs_b': {'00': 0.5, '10': 0.5}}

## isqTrain/4755

- task_id: `isqTrain/4755`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `559`

### Prompt

Do these two isQ programs produce the same measurement results?

Program A:
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

Program B:
```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    Rz(pi/4.0, q[0]);
    H(q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

1.  **Analyze Program A**:
    *   Initial state: $|0\rangle$
    *   Apply $H$: $H|0\rangle = |+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$
    *   Apply $R_z(\pi/2)$: $R_z(\theta)|\psi\rangle$ introduces a phase $e^{-i\theta/2}$ to $|0\rangle$ and $e^{i\theta/2}$ to $|1\rangle$. For $\theta = \pi/2$, the state becomes $\frac{1}{\sqrt{2}}(e^{-i\pi/4}|0\rangle + e^{i\pi/4}|1\rangle)$. (Ignoring global phase: $\frac{1}{\sqrt{2}}(|0\rangle + e^{i\pi/2}|1\rangle) = \frac{1}{\sqrt{2}}(|0\rangle + i|1\rangle)$. This is actually equivalent to applying an $S$ gate).
    *   Apply $H$:
        *   $H(\frac{1}{\sqrt{2}}(|0\rangle + i|1\rangle)) = \frac{1}{2}(|0\rangle + |1\rangle + i|0\rangle - i|1\rangle)$
        *   $= \frac{1+i}{2}|0\rangle + \frac{1-i}{2}|1\rangle$
    *   Probability of measuring 0: $| \frac{1+i}{2} |^2 = \frac{1 + 2i - 1}{4}$ wait. $|1+i|^2 = 1^2 + 1^2 = 2$. So $P(0) = 2/4 = 0.5$. Wait, let me recompute.
    *   Let's check the predicted output: Program A produces {'0': 0.853553, '1': 0.146447}.
    *   Let's re-evaluate: $HR_z(\pi/2)H|0\rangle$.
    *   $HR_z(\theta)H = R_x(\theta)$ in standard definition, BUT wait, $R_z(\theta) = e^{-i\theta Z/2} = e^{-i\theta/2}|0\rangle\langle0| + e^{i\theta/2}|1\rangle\langle1|$.
    *   $H R_z(\theta) H = R_x(\theta)$ in most conventions (like Qiskit). Wait, is it $R_x(\theta)$ or something else?
    *   Let's do the matrix multiplication:
        *   $H = \frac{1}{\sqrt{2}} \begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix}$
        *   $R_z(\pi/2) = e^{-i\pi/4} \begin{pmatrix} 1 & 0 \\ 0 & e^{i\pi/2} \end{pmatrix} = e^{-i\pi/4} \begin{pmatrix} 1 & 0 \\ 0 & i \end{pmatrix}$
        *   $H R_z H = \frac{1}{2} \begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix} \begin{pmatrix} 1 & 0 \\ 0 & i \end{pmatrix} \begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix} = \frac{1}{2} \begin{pmatrix} 1 & i \\ 1 & -i \end{pmatrix} \begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix} = \frac{1}{2} \begin{pmatrix} 1+i & 1-i \\ 1-i & 1+i \end{pmatrix}$
        *   Acting on $|0\rangle = \begin{pmatrix} 1 \\ 0 \end{pmatrix}$: $\frac{1}{2} \begin{pmatrix} 1+i \\ 1-i \end{pmatrix}$
        *   Prob of 0: $\frac{1^2 + 1^2}{4} = 0.5$. Wait, the prompt says "Program A produces {'0': 0.853553, '1': 0.146447}". This is $P(0) = \cos^2(\pi/8) = 0.853

### Reference answer

{'equivalent': False, 'explanation': "Different Rz angles in H-Rz-H pattern give different measurement probs Program A produces {'0': 0.853553, '1': 0.146447} while Program B produces {'0': 0.5, '1': 0.5}.", 'probs_a': {'0': 0.5, '1': 0.5}, 'probs_b': {'0': 0.853553, '1': 0.146447}}

## isqTrain/1484

- task_id: `isqTrain/1484`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `data_encoding_qml`
- source: `isq_train_cot`
- dataset_index: `2328`

### Prompt

请用isQ语言编写一个量子电路：Encode the classical value 11/16 into a qubit using angle encoding (Ry rotation with angle pi*11/16). Measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Encode the classical value 11/16 into a qubit via angle encoding using a Y-rotation.
2. **Qubits**: 1 qubit is required, and it is measured.
3. **State evolution**:
   - Initialize to |0⟩.
   - Apply Ry(θ) with θ = π·11/16, evolving the state to cos(θ/2)|0⟩ + sin(θ/2)|1⟩, where θ/2 = 11π/32.
4. **Probabilities**: 
   - P(|0⟩) = cos²(11π/32) ≈ 0.2222
   - P(|1⟩) = sin²(11π/32) ≈ 0.7778

## isqTrain/1581

- task_id: `isqTrain/1581`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `1427`

### Prompt

帮我写一个isQ程序：On 4 qubits, set q[1]=|1> and apply CNOT with control=q[1], target=q[3]. Measure all.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Generate a reasoning section for a specific isQ quantum program.
    *   Program details: 4 qubits. Set q[1]=|1>. CNOT(q[1], q[3]). Measure all.
    *   Goal: Explain circuit, qubit count/measurement, state evolution, and expected probabilities.
    *   Constraints: Concise (3-8 lines), precise Dirac notation, ONLY reasoning (no code block, no isQ code), start with "## Reasoning".

2.  **Circuit Analysis:**
    *   Initial state: |0000> (4 qubits, q[0..3])
    *   Step 1: X(q[1]) -> flips q[1] from |0> to |1>. State becomes |0010> (or |10>_q1).
    *   Step 2: CNOT(q[1], q[3]) -> control is q[1] (which is |1>), target is q[3]. Flips q[3] from |0> to |1>. State becomes |1010>. Wait, let me check bit ordering.
        *   Standard ordering: q[0] is the rightmost bit, or leftmost? In Dirac notation, let's use standard right-to-left: qubit 0 is bit 0, qubit 1 is bit 1.
        *   |q[3] q[2] q[1] q[0]>
        *   Initial: |0000>
        *   X(q[1]): q[1] becomes 1 -> |0010>
        *   CNOT(q[1], q[3]): control is q[1] (1), target is q[3]. q[3] becomes 1 -> |1010>
    *   predicted output probability: The prompt says `{|0101>: 1.0}`. Wait, let me re-evaluate the bitstring output for `--probs` mode in isQ.
    *   The prompt says: `Expected measurement probabilities: {|0101>: 1.0}`.
    *   Wait, if q[1]=1 and q[3]=1, then the array of measured bits is `[M(q[0]), M(q[1]), M(q[2]), M(q[3])]`.
    *   In isQ (and many SDKs), if we measure `M(q[0]), M(q[1]), M(q[2]), M(q[3])` in this order, `--probs` output is typically an integer where the first measured qubit is the highest bit or lowest bit.
    *   "earlier measured qubit = higher bit" -> This means `M(q[0])` is the highest bit (bit 3) and `M(q[3])` is the lowest bit (bit 0).
    *   Let's check: `q[0]=0`, `q[1]=1`, `q[2]=0`, `q[3]=1`.
    *   Highest bit (bit 3) = `M(q[0])` = 0
    *   Bit 2 = `M(q[1])` = 1
    *   Bit 1 = `M(q[2])` = 0
    *   Lowest bit (bit 0) = `M(q[3])` = 1
    *   So the integer is `0101` in binary. This exactly matches the predicted output `{|0101>: 1.0}`.

3.  **Drafting the Reasoning:**
    *   **Goal:** Apply an X gate to set q[1] to |1>, then use it to control a CNOT gate targeting q[3].
    *   **Qubits:** 4 qubits are used, and all are measured.
    *   **Evolution:**
        *   Start with |0000> (assuming standard q[3]q[2]q[1]q[0] notation, though keeping it conceptual is safer: |0>_0 |0>_1 |0>_2 |0>_3).
        *   X(q[1]) changes the state to |0>_0 |1>_1 |0>_2 |0>_3.
        *   CNOT(q[1], q[3]) flips q[3] because q[1] is |1>, resulting in |0>_0 |1>_1 |0>_2 |1>_3.
    *   **Probabilities:** Measuring all qubits yields q[0]=0, q[1]=1, q[2]=0, q[3]=1. With the first measured qubit as the highest bit, this gives the binary string 0101 with 100

## isqTrain/1720

- task_id: `isqTrain/1720`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1463`

### Prompt

Write isQ code for the following quantum task: Apply Ry(pi/4) then H to |0>. Measure.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply Ry(π/4) followed by H to |0⟩, then measure the result.
One qubit is needed and measured.

State evolution:
- |ψ₀⟩ = |0⟩
- After Ry(π/4): |ψ₁⟩ = cos(π/8)|0⟩ + sin(π/8)|1⟩ ≈ 0.924|0⟩ + 0.383|1⟩
- After H: |ψ₂⟩ = ½[(cos(π/8)+sin(π/8))|0⟩ + (cos(π/8)-sin(π/8))|1⟩] (normalized by 1/√2)

Measurement probabilities:
- P(0) = cos²(π/8) ≈ 85.4%
- P(1) = sin²(π/8) ≈ 14.6%

## isqTrain/4743

- task_id: `isqTrain/4743`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `5345`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit q[3];

procedure main() {
    X(q[0]);
    X(q[1]);
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
- The circuit initializes three qubits to the state |000>.
- `X(q[0])` flips the first qubit, transitioning the state to |100>.
- `X(q[1])` flips the second qubit, transitioning the state to |110>.
- `X(q[0])` flips the first qubit again, returning the system to the state |010>.
- The final state |010> is deterministic upon measurement.
- Predicted measurement probabilities: {|010>: 1.0}

### Reference answer

{'predicted_probs': {'010': 1.0}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|010>) = 1.0000.'}

## isqTrain/1774

- task_id: `isqTrain/1774`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `3257`

### Prompt

Code this in isQ: Apply X gate 6 times to |0> and measure. (X^6 = I.)

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Apply the X gate 6 times to the initial state |0> and measure the result.
2. **Qubits:** 1 qubit (`q[0]`) is used and measured.
3. **State Evolution:** 
   - Start in the initial state |0>.
   - Apply the X gate 6 times. Since X is a bit-flip gate, it toggles the state between |0> and |1>: |0> → |1> → |0> → |1> → |0> → |1> → |0>.
   - Because X^2 = I (Identity), applying it 6 times (an even number) is equivalent to the identity operation (X^6 = I). The final state remains |0>.
4. **Probabilities:** The measurement of the final state |0> yields the classical outcome 0 with absolute certainty. Thus, the expected measurement probability is {|0>: 1.0}.

## isqTrain/1475

- task_id: `isqTrain/1475`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `data_encoding_qml`
- source: `isq_train_cot`
- dataset_index: `2822`

### Prompt

Implement the following in isQ: Encode the classical value 2/16 into a qubit using angle encoding (Ry rotation with angle pi*2/16). Measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Encode classical value 2/16 into a qubit via Ry rotation with angle π·2/16 = π/8, then measure.
2. **Qubits**: 1 qubit (`q[0]`), which is measured.
3. **State evolution**:
   - Initial: |0⟩
   - After Ry(π/8, q[0]): cos(π/16)|0⟩ + sin(π/16)|1⟩
4. **Probabilities**: P(|0⟩) = cos²(π/16) ≈ 0.9619, P(|1⟩) = sin²(π/16) ≈ 0.0381.

## isqTrain/4723

- task_id: `isqTrain/4723`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `3131`

### Prompt

这两个isQ程序是等价的吗？

程序A：
```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    X(q[0]); // additional bit flip
    M(q[0]);
}

```

程序B：
```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    H(q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

1.  **Analyze Program A**:
    *   Initial state: |0>
    *   Apply H(q[0]): State becomes |+> = (1/√2)|0> + (1/√2)|1>
    *   Apply X(q[0]): State becomes (1/√2)|1> + (1/√2)|0> = |+> (Wait, X just swaps |0> and |1>, so |+> remains |+>).
    *   Let's re-read the predicted output carefully: "After adding X gate to Program A, the programs produce different probability distributions."
    *   Wait, X|+> = X ( (|0> + |1>)/√2 ) = (|1> + |0>)/√2 = |+>.
    *   Let me re-read Program B.
    *   H(q[0]); H(q[0]); = Identity. State is |0>. Prob(0) = 1.0.
    *   Wait, if Program A is |+>, Prob(0) = 0.5, Prob(1) = 0.5.
    *   If Program B is H * H |0> = I |0> = |0>, Prob(0) = 1.0.
    *   So yes, they produce different probability distributions.
    *   Wait, my previous thought "State becomes (1/√2)|1> + (1/√2)|0> = |+>" is correct. Program A gives 50/50, Program B gives 100/0.
    *   Let's double check. H|0> = |+>. X|+> = |+>. So A is H, X -> 50% |0>, 50% |1>.
    *   B is H, H -> I -> 100% |0>.

2.  **Draft the explanation**:
    *   Program A applies H, then X to q[0]. Initial state |0> becomes |+>, and X acts on |+> leaving it as |+>. The final state is |+>, resulting in a 50% probability for both |0> and |1>.
    *   Program B applies H, then another H to q[0]. Two Hadamards cancel out (H^2 = I), so the state remains |0>. The measurement probability is 100% for |0> and 0% for |1>.
    *   The key difference is that A results in the |+> state while B results in the |0> state.
    *   The measurement probabilities are different (50/50 vs 100/0).

3.  **Format the output**:
    *   Start with "## Equivalence Analysis"
    *   Keep it concise (3-8 lines).
    *   End with a clear "Yes/No" verdict line (e.g., "Equivalent: No" or just "No"). Let's use "Verdict: Not equivalent" or "Equivalent: False". The instructions say "End with a clear 'Yes/No' verdict line" and the predicted output uses "Equivalent: False". Wait, "clear 'Yes/No' verdict line". Let's just say "Verdict: No" or "Equivalent: No". I'll write "Equivalent: No".

4.  **Refine lines**:
    1. Program A applies an H gate followed by an X gate to the initial state |0>.
    2. The H gate maps |0> to |+>, and the X gate leaves |+> unchanged, so Program A measures |0> and |1> with 50% probability each.
    3. Program B applies two consecutive H gates to |0>, which cancel out (H^2 = I), leaving the qubit in the |0> state.
    4. Program B measures |0> with 100% probability.
    5. The key difference is the net unitary applied (X*H vs I), leading to different final states (|+> vs |0>).
    6. Equivalent: No

    Let's check the constraint: "3-8 lines for simple circuits".
    Line 1: Program A applies H and then X to |0>, resulting in the state |+> (since X|+> = |+>), yielding 50% probability for both |0> and |1>.
    Line 2: Program B applies H twice to |0>, which acts as the identity (H^2 = I), leaving the state as |0> with 100% measurement probability.
    Line 3: The key difference is that A results in the superposition |+> state, while B remains in the basis state |0>.
    Line 4: The measurement probabilities are clearly different (50/

### Reference answer

{'equivalent': False, 'explanation': 'After adding X gate to Program A, the programs produce different probability distributions.', 'probs_a': {'0': 0.5, '1': 0.5}, 'probs_b': {'0': 1.0}}
