# ISQ training COT RAG corpus: quantum_algorithms shard 160

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4260

- task_id: `isqTrain/4260`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3597`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;

// Triangle (K3) graph state
qbit q[3];

procedure main() {
    // Hadamard on all qubits: create |+>|+>|+>
    H(q[0]); H(q[1]); H(q[2]);
    // CZ for all edges in the triangle
    // Edge (0,1)
    CZ(q[0], q[1]);
    // Edge (1,2)
    CZ(q[1], q[2]);
    // Edge (0,2) completes the triangle
    CZ(q[0], q[2]);
    // Measure in computational (Z) basis
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Input isQ program: Creates a K3 graph state (triangle) with CZ gates, then applies an X gate to q[0], and measures all qubits.
    *   Output required: "## Circuit Analysis" section, 3-15 lines of concise reasoning using Dirac notation, step-by-step state evolution, and the predicted probability distribution.
    *   Specific constraints: Output ONLY the analysis section, no code blocks, end with the probabilities.

2.  **Step-by-Step Quantum State Evolution:**
    *   Initial state: $|000\rangle$
    *   Apply $H$ on all qubits: $|+\rangle|+\rangle|+\rangle = \frac{1}{\sqrt{8}} \sum_{x \in \{0,1\}^3} |x\rangle$
    *   Apply $CZ_{01}$: Phase shifts amplitudes where $q_0=1, q_1=1$.
    *   Apply $CZ_{12}$: Phase shifts amplitudes where $q_1=1, q_2=1$.
    *   Apply $CZ_{02}$: Phase shifts amplitudes where $q_0=1, q_2=1$.
    *   Let's evaluate the phase for each basis state in the K3 graph state (|G>):
        *   $|000\rangle$: (+1) -> $|000\rangle$
        *   $|001\rangle$: (+1) -> $|001\rangle$
        *   $|010\rangle$: (+1) -> $|010\rangle$
        *   $|011\rangle$: $CZ_{12}$ applies (-1) -> $-|011\rangle$
        *   $|100\rangle$: (+1) -> $|100\rangle$
        *   $|101\rangle$: $CZ_{02}$ applies (-1) -> $-|101\rangle$
        *   $|110\rangle$: $CZ_{01}$ applies (-1) -> $-|110\rangle$
        *   $|111\rangle$: $CZ_{01}$ (-1), $CZ_{12}$ (-1), $CZ_{02}$ (-1) -> $(-1)^3 = -|111\rangle$
        Wait, is it? Let's check 111:
        Edges: (0,1), (1,2), (0,2). Number of edges with both endpoints 1 is 3. (-1)^3 = -1.
        So the graph state is $|G\rangle = \frac{1}{\sqrt{8}} (|000\rangle + |001\rangle + |010\rangle - |011\rangle + |100\rangle - |101\rangle - |110\rangle - |111\rangle)$.
    *   Apply $X(q[0])$:
        *   Flips the first qubit (swaps 0 and 1).
        *   $|000\rangle \leftrightarrow |100\rangle$
        *   $|001\rangle \leftrightarrow |101\rangle$
        *   $|010\rangle \leftrightarrow |110\rangle$
        *   $|011\rangle \leftrightarrow |111\rangle$
        *   Wait, in the previous state, what were the amplitudes?
        *   $|000\rangle$ (+1), $|100\rangle$ (+1). After X, they swap, so both are still +1.
        *   $|001\rangle$ (+1), $|101\rangle$ (-1). After X, $|001\rangle$ becomes -1, $|101\rangle$ becomes +1.
        *   $|010\rangle$ (+1), $|110\rangle$ (-1). After X, $|010\rangle$ becomes -1, $|110\rangle$ becomes +1.
        *   $|011\rangle$ (-1), $|111\rangle$ (-1). After X, both swap, so both are -1.
        Let's re-evaluate: $X_0 |G\rangle = \frac{1}{\sqrt{8}} (|100\rangle + |101\rangle - |110\rangle - |111\rangle + |000\rangle - |001\rangle - |010\rangle - |011\rangle)$? No, wait.
        If $|G\rangle = A|000\rangle + B|001\rangle + C|010\rangle - D|011\rangle + E|100\rangle - F|101\rangle - G|110\rangle - H|111\rangle$ (all coeffs $\pm

### Reference answer

{'predicted_probs': {'000': 0.125, '001': 0.125, '010': 0.125, '011': 0.125, '100': 0.125, '101': 0.125, '110': 0.125, '111': 0.125}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|000>) = 0.1250, P(|001>) = 0.1250, P(|010>) = 0.1250, P(|011>) = 0.1250, P(|100>) = 0.1250, P(|101>) = 0.1250, P(|110>) = 0.1250, P(|111>) = 0.1250.'}

## isqTrain/3494

- task_id: `isqTrain/3494`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `basis_change`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5420`

### Prompt

What is the measurement probability distribution of this isQ program?

```
import std;

qbit q[2];

procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    Z(q[0]);

    CNOT(q[0], q[1]);
    H(q[0]);

    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Role: Quantum computing expert.
    *   Task: Predict output probability distribution for a given isQ program.
    *   Format: Step-by-step reasoning using Dirac notation, "## Circuit Analysis" header, concise (3-15 lines), end with predicted probability distribution.
    *   Input program:
        

2.  **Analyze the Circuit (Gate by Gate):**
    *   Initial state: $|00\rangle$
    *   `H(q[0])`: $|00\rangle \to \frac{1}{\sqrt{2}}(|00\rangle + |10\rangle) = |+\rangle|0\rangle$
    *   `CNOT(q[0], q[1])`: $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$ (Bell state)
    *   `Z(q[0])`: $\frac{1}{\sqrt{2}}(|00\rangle - |11\rangle)$ (Phase flip on |1> component of q[0])
    *   `CNOT(q[0], q[1])`: $\frac{1}{\sqrt{2}}(|00\rangle - |10\rangle) = \frac{1}{\sqrt{2}}|0\rangle(|0\rangle - |1\rangle) = |0\rangle|-\rangle$
    *   `H(q[0])`: $\frac{1}{\sqrt{2}} (|0\rangle - |1\rangle) \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) = |-\rangle|-\rangle$. Wait, let me re-evaluate CNOT(q[0], q[1]) on $\frac{1}{\sqrt{2}}(|00\rangle - |11\rangle)$.
    *   Let's re-do the calculation carefully.
        *   State 0: $|00\rangle$
        *   State 1 (H on q0): $\frac{1}{\sqrt{2}}|00\rangle + \frac{1}{\sqrt{2}}|10\rangle$
        *   State 2 (CNOT on q0, q1): $\frac{1}{\sqrt{2}}|00\rangle + \frac{1}{\sqrt{2}}|11\rangle$
        *   State 3 (Z on q0): $\frac{1}{\sqrt{2}}|00\rangle - \frac{1}{\sqrt{2}}|11\rangle$
        *   State 4 (CNOT on q0, q1): $\frac{1}{\sqrt{2}}|00\rangle - \frac{1}{\sqrt{2}}|10\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) \otimes |0\rangle = |-\rangle \otimes |0\rangle$.
            Wait! Let me check the CNOT truth table.
            $|00\rangle \to |00\rangle$
            $|11\rangle \to |10\rangle$
            Yes, $\frac{1}{\sqrt{2}}|00\rangle - \frac{1}{\sqrt{2}}|10\rangle = \frac{1}{\sqrt{2}} (|0\rangle - |1\rangle) \otimes |0\rangle$.
        *   State 5 (H on q0): $H|-\rangle \otimes |0\rangle = |1\rangle \otimes |0\rangle = |10\rangle$.

3.  **Final State and Measurement:**
    *   Final state: $|10\rangle$.
    *   Probability distribution: 100% for $|10\rangle$. (q[0] = 1, q[1] = 0).
    *   Wait, isQ M() returns int. The measurement string is based on the order, earlier measured = higher bit. So M(q[0]) is MSB, M(q[1]) is LSB. State is q[0]=1, q[1]=0. So `10`.

4.  **Drafting the response:**
    *   Header: ## Circuit Analysis
    *   Step 1: Initial state is $|00\rangle$. H gate on q[0] creates $|+\rangle|0\rangle = \frac{1}{\sqrt{2}}(|00\rangle

### Reference answer

{'predicted_probs': {'10': 1.0}, 'explanation': 'The output is |10> with probability 1.0'}

## isqTrain/52

- task_id: `isqTrain/52`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_arrays`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2341`

### Prompt

Help me write isQ code that implements the oracle_boolean pattern but with a different initial state preparation (flip q[[2]] -> q[1]).

### Chain-of-thought reasoning

Let me analyze this task carefully.

The task is to write an isQ program that implements the oracle_boolean pattern but with a different initial state preparation - specifically flipping q[[2]] -> q[1], which means instead of preparing q[2] as the output qubit in |-> state, we prepare q[1].

Analyzing the circuit requirements:
- q[0], q[1] are input qubits
- q[2] is the output qubit (prepared in |-> state)
- The balanced oracle applies CNOT(q[0], q[2]) and CNOT(q[1], q[2])
- Input qubits are put in |+> state with H gates
- After oracle, H gates are applied to inputs, then measured

The task says to flip q[[2]] -> q[1], meaning:
- q[2] should now be an input qubit (put in |+> state)
- q[1] should now be the output qubit (prepared in |-> state)

So the new setup:
- q[0] and q[2] are input qubits
- q[1] is the output qubit (prepared in |-> state)

Let me trace through the circuit:

Initial state: |000>

1. X(q[1]) -> |010>

2. H(q[1]) -> |0> ⊗ |-> ⊗ |0> (q[1] is now in |-> state)

3. H(q[0]) -> |+> ⊗ |-> ⊗ |0>

4. H(q[2]) -> |+> ⊗ |-> ⊗ |+>

5. Balanced oracle with CNOT(q[0], q[1]) and CNOT(q[2], q[1]):
   - The oracle applies phase based on inputs to the output qubit
   - CNOT(q[0], q[1]): flips q[1] when q[0] is |1>
   - CNOT(q[2], q[1]): flips q[1] when q[2] is |1>

Let me trace more carefully:
State after H gates: |+>|->|+> = (1/2)(|0>+|1>) ⊗ (|0>-|1>)/√2 ⊗ (|0>+|1>)

After CNOT(q[0], q[1]):
- |0>|->|+> stays as |0>|->|+>
- |1>|->|+> becomes |1>|+>|+> (since X|-> = |+>)

Wait, let me reconsider. When q[1] is in |-> = (|0>-|1>)/√2:
- X(q[1])|-> = (|1>-|0>)/√2 = -(|0>-|1>)/√2 = -|->

So CNOT with q[1] as target:
- When control is |0>: no change
- When control is |1>: X on |-> = -|->

So CNOT(q[0], q[1]) on |+>|-> = (1/2)(|0>+|1>)|-> 
= (1/2)(|0>|-> + |1> X|->)
= (1/2)(|0>|-> - |1>|->)
= (1/2)(|0> - |1>)|-> = |->|->

Hmm, that doesn't seem right. Let me recalculate.

Actually, for phase oracle with output in |->:
- The phase is kicked back: if output qubit starts in |->, the oracle applies a phase based on whether the function outputs 1.

For balanced_oracle(q[0], q[2], q[1]):
- f(x) = x0 ⊕ x2 (XOR of inputs)
- This is a balanced function

After phase kickback:
- |00>|-> -> |00>|-> (f(00)=0)
- |01>|-> -> -|01>|-> (f(01)=1)
- |10>|-> -> -|10>|-> (f(10)=1)
- |11>|-> -> |11>|-> (f(11)=0)

So the state becomes:
(1/2)(|00> - |01> - |10> + |11>)|-> = |->|->|->

Wait, the inputs are q[0] and q[2], so the ordering is:
(1/2)(|0>|->|0> - |0>|->|1> - |1>|->|0> + |1>|->|1>)

Hmm, I need to be more careful. The state is |q[0]>|q[1]>|q[2]>.

After initial H gates:
-

## isqTrain/3437

- task_id: `isqTrain/3437`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `hamiltonian_simulation`, `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `66`

### Prompt

Code this in isQ: one Trotter step of the 2-qubit Heisenberg XXX model in isQ.

H = J*(X_0*X_1 + Y_0*Y_1 + Z_0*Z_1)

Trotter decomposition:
1. XX interaction: H-CNOT-Rz-CNOT-H (on both qubits)
2. YY interaction: Rx(pi/2)-CNOT-Rz-CNOT-Rx(-pi/2)
3. ZZ interaction: CNOT-Rz-CNOT

Use J=1.0, dt=0.3. Start from |10>.
Declare 2 qubits, measure both.

### Chain-of-thought reasoning

Let me analyze this problem step by step.

**Goal:** Implement one Trotter step of the 2-qubit Heisenberg XXX model H = J*(X₀X₁ + Y₀Y₁ + Z₀Z₁) with J=1.0, dt=0.3, starting from |10⟩.

**Qubits:** 2 qubits (q[0], q[1]), both measured.

**State evolution:**

1. **Initial state:** |00⟩
2. **After X(q[0]):** |10⟩

3. **XX interaction (exp(-i·J·dt·X₀X₁)):**
   - H(q[0]) H(q[1]) on |10⟩ → H|1⟩⊗H|0⟩ = |−⟩⊗|+⟩
   - CNOT(q[0], q[1]) on |−⟩|+⟩ = 1/2(|00⟩ - |01⟩ + |10⟩ - |11⟩) → The CNOT maps |0⟩|±⟩ → |0⟩|±⟩ and |1⟩|±⟩ → |1⟩|∓⟩, so we get 1/2(|00⟩ - |01⟩ + |10⟩ + |11⟩)... let me recalculate.

Actually, let me be more careful. |10⟩ means q[0]=1, q[1]=0.

H|1⟩ = |−⟩ = (|0⟩ - |1⟩)/√2
H|0⟩ = |+⟩ = (|0⟩ + |1⟩)/√2

So after H on both: |−⟩⊗|+⟩ = 1/2(|00⟩ + |01⟩ - |10⟩ - |11⟩)

CNOT(q[0], q[1]): control=q[0], target=q[1]
- |00⟩ → |00⟩
- |01⟩ → |01⟩
- |10⟩ → |11⟩
- |11⟩ → |10⟩

So 1/2(|00⟩ + |01⟩ - |11⟩ - |10⟩) = 1/2(|00⟩ + |01⟩ - |10⟩ - |11⟩)

After Rz(0.6, q[1]): applies Rz(θ) = diag(e^{-iθ/2}, e^{iθ/2}) on q[1]
- |0⟩ → e^{-iθ/2}|0⟩
- |1⟩ → e^{iθ/2}|1⟩

With θ = 0.6:
1/2(e^{-0.3i}|00⟩ + e^{0.3i}|01⟩ - e^{-0.3i}|10⟩ - e^{0.3i}|11⟩)

After CNOT(q[0], q[1]):
1/2(e^{-0.3i}|00⟩ + e^{0.3i}|01⟩ - e^{0.3i}|10⟩ - e^{-0.3i}|11⟩)

After H(q[0]) H(q[1]):
This gets complicated. Let me think about this differently.

Actually, the circuit H-CNOT-Rz-CNOT-H implements exp(-iθ/2·Z₀Z₁) which in the X basis corresponds to exp(-iθ/2·X₀X₁). Wait, no. Let me think again.

The standard identity: H⊗H maps X⊗X to Z⊗Z. So H⊗H · exp(-iθ/2·Z⊗Z) · H⊗H = exp(-iθ/2·X⊗X).

And exp(-iθ/2·Z⊗Z) = CNOT · (I⊗Rz(θ)) · CNOT.

So the XX block implements exp(-i·0.3·X₀X₁).

Similarly:
- Rx(π/2)⊗Rx(π/2) maps Y⊗Y to Z⊗Z, so the YY block implements exp(-i·0.3·Y₀Y₁)
- The ZZ block directly implements exp(-i·0.3·Z₀Z₁)

The full Trotter step approximates exp(-i·dt·H) = exp(-i·0.3·(X₀X₁ + Y₀Y₁ + Z₀Z₁)).

Let me trace the state numerically. Starting from |10⟩.

After exp(-i·0.3·X₀X₁):
X₀X₁|10⟩ = X|1⟩⊗X|0⟩ = |0⟩⊗|1⟩ = |01⟩
So X₀X₁ has eigenvalues: for |00⟩→|11⟩, |11⟩→|00⟩, |01⟩→|10⟩, |10⟩→|01⟩.
The symmetric subspace {|01⟩+|

## isqTrain/1402

- task_id: `isqTrain/1402`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `isq_syntax_multi_register`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5338`

### Prompt

实现以下量子计算任务（使用isQ）：the Bernstein-Vazirani algorithm to find the secret string s = 1111 (MSB first). Use 4 input qubits and 1 ancilla.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Task:** Generate a concise, step-by-step reasoning for the provided isQ code (Bernstein-Vazirani algorithm for s=1111).
    *   **Format:** "## Reasoning" section, strictly 3-8 lines (up to 15 for complex).
    *   **Content:** Goal, qubits/measured, state evolution (Dirac notation), expected probabilities justification.
    *   **Constraints:** NO code, NO isq code blocks.

2.  **Analyze the Circuit:**
    *   **Qubits:** 4 input (`q[0..3]`), 1 ancilla (`anc[0]`). Measured: `q[0..3]`.
    *   **Goal:** Identify the secret string $s = 1111$ using the Bernstein-Vazirani algorithm.
    *   **State evolution:**
        *   Initial: $|0000\rangle_q |0\rangle_a$
        *   Prepare ancilla: $X(H|0\rangle) = |-\rangle_a$. State: $|0000\rangle_q |-\rangle_a$
        *   Hadamard inputs: $H^{\otimes 4}|0000\rangle = |+++\rangle_q$. State: $|+++\rangle_q |-\rangle_a$
        *   Oracle (CNOT from each q to anc): The phase kickback applies a phase $(-1)^{s \cdot x}$ to the input register. For $s=1111$, it flips the phase of all states $x$ where $x \cdot 1111 \bmod 2 = 1$. State: $\frac{1}{4} \sum_{x \in \{0,1\}^4} (-1)^{1111 \cdot x} |x\rangle_q |-\rangle_a$
        *   Hadamard inputs: Interference transforms the state back from the Fourier basis to the computational basis, isolating the secret string. $H^{\otimes 4} \left( \frac{1}{4} \sum (-1)^{s \cdot x} |x\rangle \right) = |s\rangle = |1111\rangle_q$.
        *   Final State (measured part): $|1111\rangle_q$.
    *   **Expected Probabilities:** Measurement of input register yields $|1111\rangle$ with probability 1.0.

3.  **Draft the Reasoning:**
    *   Line 1: Goal.
    *   Line 2: Qubits/measured.
    *   Lines 3-6: State evolution.
    *   Line 7: Probabilities.

    *Drafting lines:*
    ## Reasoning
    Goal: Identify the secret binary string $s=1111$ using the Bernstein-Vazirani algorithm.
    Qubits: 4 input qubits ($q[0..3]$) and 1 ancilla ($anc[0]$). Only $q[0..3]$ are measured.
    Evolution:
    1. Initialize ancilla to $|-\rangle$ and apply $H^{\otimes 4}$ to inputs: $|0000\rangle |0\rangle \to |+\rangle^{\otimes 4} |-\rangle$.
    2. The CNOT oracle encodes $s=1111$ via phase kickback: $|x\rangle |-\rangle \to (-1)^{s \cdot x}|x\rangle |-\rangle$.
    3. Applying $H^{\otimes 4}$ to the input register cancels out the superposition, yielding $|s\rangle |-\rangle = |1111\rangle |-\rangle$.
    Outcome: The final state of the input register is precisely $|1111\rangle$, so measuring yields $|1111\rangle$ with 100% probability.

4.  **Refine to Constraints:**
    Length is 7 lines, well within the 3-8 (or 15) line constraint. Uses Dirac notation. No code blocks.

5.  **Final Polish:**
    Ensure exact string representation in Dirac notation.
    $|+\rangle^{\otimes 4}$ is cleaner. Let's write $|+++\rangle$ as $|+\rangle^{\otimes 4}$. Wait, 4 qubits. $|++++\rangle$. Let's use $|+\rangle^{\otimes 4}$ or $\frac{1}{4}\sum |x\rangle$.
    "Prepare ancilla in |-> and inputs in |+>^4."
    "Oracle applies phase (-1)^(s.x) to inputs."
    "Final H^4 maps phase-encoded state to |1111

## isqTrain/695

- task_id: `isqTrain/695`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `114`

### Prompt

帮我写一个isQ程序：implements the half_full_adder pattern. Include explicit identity operations in the circuit (H-H pair before M(q[3])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a full adder with inputs a=1, b=1, carry_in=1, computing sum and carry_out.
2. **Qubits**: 5 qubits (q[0-4]); inputs q[0-2], sum in q[3], carry_out in q[4]; measuring q[3], q[4].
3. **State evolution**:
   - Start: |00000⟩
   - After X(q[0]), X(q[1]), X(q[2]): |11100⟩ (inputs set)
   - After CNOT(q[0], q[3]): |11110⟩; CNOT(q[1], q[3]): |11100⟩; CNOT(q[2], q[3]): |11110⟩ (sum = 1⊕1⊕1 = 1)
   - After Toffoli(q[0], q[1], q[4]): |11111⟩; Toffoli(q[0], q[2], q[4]): |11110⟩; Toffoli(q[1], q[2], q[4]): |11111⟩ (carry_out = majority(1,1,1) = 1)
   - After H(q[3]): |11⟩⊗|+⟩⊗|1⟩ on measured qubits; after H(q[3]): H-H = I, returns to |11111⟩
4. **Result**: Measurement yields |11⟩ (q[3]=1, q[4]=1) with probability 1.0, since H-H cancels and both output qubits remain |1⟩.

## isqTrain/3063

- task_id: `isqTrain/3063`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `measurement_order`
- source: `isq_train_cot`
- dataset_index: `913`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit q[3];
procedure main() {
    X(q[0]);
    X(q[1]);
    X(q[2]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1.  **Gate operations**: The circuit initializes a 3-qubit register `q[3]` in the |000> state. It then sequentially applies the Pauli-X gate to `q[0]`, `q[1]`, and `q[2]`.
2.  **State evolution**:
    *   Initial state: |000>
    *   After `X(q[0])`: Flips the 0th qubit, resulting in |100>.
    *   After `X(q[1])`: Flips the 1st qubit, resulting in |110>.
    *   After `X(q[2])`: Flips the 2nd qubit, resulting in |111>.
3.  **Final state**: The quantum state prior to measurement is deterministically |111>.
4.  **Predicted probability distribution**: Since the state is exactly |111>, a measurement in the computational basis will yield the outcome '111' with

### Reference answer

{'predicted_probs': {'111': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/1422

- task_id: `isqTrain/1422`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `isq_syntax_ctrl_nctrl`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4205`

### Prompt

Write an isQ program that Apply the 3-qubit Quantum Fourier Transform to the input state |101> and measure all qubits.

### Chain-of-thought reasoning

Let me trace through this 3-qubit QFT circuit applied to |101>.

Initial state: |000>
After X(q[0]) and X(q[2]): |101>

Now applying QFT on 3 qubits. The QFT maps |k⟩ → (1/√N) Σ_j e^{2πijk/N} |j⟩

For |101⟩ = |5⟩:
QFT|5⟩ = (1/√8) Σ_{j=0}^{7} e^{2πi·5·j/8} |j⟩

The phases are:
j=0: e^0 = 1
j=1: e^{10πi/8} = e^{5πi/4} = e^{-3πi/4}
j=2: e^{20πi/8} = e^{5πi/2} = e^{πi/2} = i
j=3: e^{30πi/8} = e^{15πi/4} = e^{-πi/4}
j=4: e^{40πi/8} = e^{5πi} = -1
j=5: e^{50πi/8} = e^{25πi/4} = e^{πi/4}
j=6: e^{60πi/8} = e^{15πi/2} = e^{-πi/2} = -i
j=7: e^{70πi/8} = e^{35πi/4} = e^{3πi/4}

So QFT|5⟩ = (1/√8)(|0⟩ + e^{-3πi/4}|1⟩ + i|2⟩ + e^{-πi/4}|3⟩ - |4⟩ + e^{πi/4}|5⟩ - i|6⟩ + e^{3πi/4}|7⟩)

The magnitude squared of each coefficient is 1/8 = 0.125, so all measurement outcomes have equal probability 0.125.

Let me verify the circuit implements QFT correctly.

The standard 3-qubit QFT circuit:
1. H on qubit 2 (MSB), then controlled-S from qubit 1 to qubit 2, controlled-T from qubit 0 to qubit 2
2. H on qubit 1, then controlled-S from qubit 0 to qubit 1
3. H on qubit 0
4. swap (three-CNOT decomposition) qubits 0 and 2

Note: In this code, q[0] is the least significant bit and q[2] is the most significant bit based on the ordering.

Let me trace:
Initial: |000⟩
X(q[0]), X(q[2]): |101⟩ (q[0]=1, q[1]=0, q[2]=1, representing |5⟩)

H(q[2]):
|10⟩ ⊗ H|1⟩ = |10⟩ ⊗ (|0⟩-|1⟩)/√2 = (|100⟩-|101⟩)/√2

Wait, I need to be careful with the qubit ordering. Let me use |q[2]q[1]q[0]⟩ notation.

Initial: |000⟩
X(q[0]): |001⟩
X(q[2]): |101⟩ (this is |q[2]=1, q[1]=0, q[0]=1⟩, which is 5 in decimal with q[0] as LSB)

H(q[2]):
H|1⟩ = (|0⟩-|1⟩)/√2
State: (|001⟩-|101⟩)/√2

ctrl S(q[1], q[2]): Apply S to q[2] if q[1]=1
Since q[1]=0 in both terms, nothing happens.
State: (|001⟩-|101⟩)/√2

ctrl T(q[0], q[2]): Apply T to q[2] if q[0]=1
For |001⟩: q[0]=1, so apply T to q[2]: T|0⟩ = |0⟩, T|1⟩ = e^{iπ/4}|1⟩
For |001⟩: q[2]=0, T|0⟩=|0⟩ → |001⟩
For |101⟩: q[0]=1, q[2]=1, T|1⟩ = e^{iπ/4}|1⟩ → e^{iπ/4}|101⟩

State: (|001⟩- e^{iπ/4}|101⟩)/√2

H(q[1]):
H on q[1] for both terms:
|001⟩ = |0⟩₁⊗

## isqTrain/3564

- task_id: `isqTrain/3564`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `hamiltonian_simulation`, `basis_change`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3350`

### Prompt

Fix the bug in the following isQ program.

Bug description: Wrong CNOT direction

The program should YY evolution operator, theta=pi/6 on |01>.

### Chain-of-thought reasoning

Let me analyze this bug.

The program is trying to implement the YY evolution operator $e^{-i\pi/6 Y_0 Y_1}$ on |01>.

The standard decomposition for $e^{-i\theta Y \otimes Y}$ uses the identity:
$$Y = R_x(\pi/2)^\dagger Z R_x(\pi/2)$$

So $Y \otimes Y = (R_x(\pi/2)^\dagger \otimes R_x(\pi/2)^\dagger) (Z \otimes Z) (R_x(\pi/2) \otimes R_x(\pi/2))$

The ZZ evolution can be decomposed using CNOTs:
$$e^{-i\theta Z \otimes Z} = \text{CNOT}_{0 \to 1} \cdot (I \otimes R_z(2\theta)) \cdot \text{CNOT}_{0 \to 1}$$

So the correct circuit should be:
1. Prepare |01⟩ by X(q[1])
2. Basis change: Rx(π/2) on both qubits
3. CNOT(q[0], q[1])
4. Rz(2θ) on q[1]
5. CNOT(q[0], q[1])
6. Undo basis change: Rx(-π/2) on both qubits

The buggy code has:

The first CNOT has q[1] as control and q[0] as target, and the second CNOT has q[0] as control and q[1] as target. These are inconsistent - both should be CNOT(q[0], q[1]).

The fixed code correctly uses:

This implements the ZZ interaction correctly with consistent CNOT directions.

Let me verify the output state. Starting with |01⟩:
- After Rx(π/2) on both qubits: We transform |01⟩ using the basis change.

Actually, let me compute more carefully. The state |01⟩ with Y⊗Y evolution.

$Y|0⟩ = i|1⟩$, $Y|1⟩ = -i|0⟩$

So $Y \otimes Y |01⟩ = (Y|0⟩) \otimes (Y|1⟩) = i|1⟩ \otimes (-i|0⟩) = |10⟩$

So |01⟩ and |10⟩ are eigenstates of Y⊗Y with eigenvalue -1? Let me check:
$Y \otimes Y |10⟩ = (Y|1⟩) \otimes (Y|0⟩) = (-i|0⟩) \otimes (i|1⟩) = |01⟩$

So Y⊗Y interchanges |01⟩ and |10⟩. The eigenstates are |01⟩ ± |10⟩ with eigenvalues ±1.

Therefore:
$e^{-i\theta Y \otimes Y} |01⟩ = e^{-i\theta Y \otimes Y} \frac{1}{2}[(|01⟩ + |10⟩) + (|01⟩ - |10⟩)]$
$= \frac{1}{2}[e^{-i\theta}(|01⟩ + |10⟩) + e^{i\theta}(|01⟩ - |10⟩)]$
$= \cos(\theta)|01⟩ - i\sin(\theta)|10⟩$

With θ = π/6:
$= \cos(\pi/6)|01⟩ - i\sin(\pi/6)|10⟩ = \frac{\sqrt{3}}{2}|01⟩ - \frac{i}{2}|10⟩$

Measurement probabilities:
- P(|01⟩) = (√3/2)² = 3/4 = 0.75
- P(|10⟩) = (1/2)² = 1/4 = 0.25

This matches the predicted output. Good.

Now let me trace through the corrected circuit:

Initial: |00⟩
After X(q[1]): |01⟩

Basis change Rx(π/2) on both:
$R_x(\pi/2) = \frac{1}{\sqrt{2}}\begin{pmatrix} 1 & -i \\ -i & 1 \end{pmatrix}$

$R_x(\pi/2)|0⟩ = \frac{1}{\sqrt{2}}(|0⟩ -

## isqTrain/1087

- task_id: `isqTrain/1087`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2714`

### Prompt

I need an isQ program to implements the deutsch_jozsa pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

Let me analyze this Deutsch-Jozsa circuit step by step.

**Goal**: Implement Deutsch-Jozsa algorithm with a balanced oracle (f(x) = x[0] XOR x[1]) and reversed measurement order.

**Qubits**: 2 input qubits q[0], q[1] and 1 ancilla anc[0]. Only q[0] and q[1] are measured.

**State evolution**:

1. **Initial state**: |q[1]q[0]⟩|anc⟩ = |00⟩|0⟩

2. **After X(anc[0])**: |00⟩|1⟩

3. **After H(anc[0])**: |00⟩(|0⟩ - |1⟩)/√2 = |00⟩|−⟩

4. **After H(q[0]) and H(q[1])**: (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2 ⊗ |−⟩

5. **Oracle application**: f(q, anc) with f(x) = x[0] XOR x[1]
   - This applies phase kickback: |x⟩|−⟩ → (−1)^f(x)|x⟩|−⟩
   - f(00) = 0, f(01) = 1, f(10) = 1, f(11) = 0
   - State becomes: (|00⟩ − |01⟩ − |10⟩ + |11⟩)/2 ⊗ |−⟩

6. **After H(q[0]) and H(q[1])**: 
   The Hadamard transform on n qubits: H^⊗n|x⟩ = (1/√2^n) Σ_z (−1)^(x·z)|z⟩
   
   Let me compute this explicitly. The state before H is:
   (1/2)(|00⟩ − |01⟩ − |10⟩ + |11⟩)
   
   Applying H⊗H:
   For each basis state |ab⟩, H⊗H|ab⟩ = Σ_z (−1)^(a·z1 + b·z2)|z1z2⟩/2
   
   H⊗H(|00⟩ − |01⟩ − |10⟩ + |11⟩)/2
   
   = (1/2)[H⊗H|00⟩ − H⊗H|01⟩ − H⊗H|10⟩ + H⊗H|11⟩]
   
   H⊗H|00⟩ = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2
   H⊗H|01⟩ = (|00⟩ − |01⟩ + |10⟩ − |11⟩)/2
   H⊗H|10⟩ = (|00⟩ + |01⟩ − |10⟩ − |11⟩)/2
   H⊗H|11⟩ = (|00⟩ − |01⟩ − |10⟩ + |11⟩)/2
   
   Result = (1/2)[(1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩) 
            − (1/2)(|00⟩ − |01⟩ + |10⟩ − |11⟩)
            − (1/2)(|00⟩ + |01⟩ − |10⟩ − |11⟩)
            + (1/2)(|00⟩ − |01⟩ − |10⟩ + |11⟩)]
   
   Coefficient of |00⟩: (1/4)(1 − 1 − 1 + 1) = 0
   Coefficient of |01⟩: (1/4)(1 + 1 − 1 − 1) = 0
   Coefficient of |10⟩: (1/4)(1 − 1 + 1 − 1) = 0
   Coefficient of |11⟩: (1/4)(1 + 1 + 1 + 1) = 1
   
   So the state becomes |11⟩ ⊗ |−⟩

7. **Measurement order**: M(q[1]) first, then M(q[0])
   - q[1] measured first → higher bit
   - q[0] measured second → lower bit
   - So the bitstring is q[1]q[0] = 11
   
   Wait, let me re-read the rule: "earlier measured qubit = higher bit"
   
   So if M(q[1]) is first, q[1] is the higher bit, and M(q[0]) is second, q[0] is the lower bit.
   
   The state is |q[0]=1, q[1]=1⟩ which in bitstring notation with q[1] as higher bit and q[0] as lower bit is |11⟩.

   So we get {|
