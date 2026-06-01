# ISQ training COT RAG corpus: quantum_algorithms shard 192

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/690

- task_id: `isqTrain/690`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5116`

### Prompt

用isQ实现implements a variant of the half_full_adder pattern using q[5] -> q[6]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

Looking at the task, I need to reason about the given isQ program that implements a half/full adder variant.

Let me analyze the circuit:

1. **Qubits**: 6 qubits (q[0] to q[5])
2. **Inputs**: q[0]=1, q[1]=1, q[2]=1 (via X gates)
3. **Operations**:
   - CNOT(q[0], q[3]): XOR a into sum
   - CNOT(q[1], q[3]): XOR b into sum
   - CNOT(q[2], q[3]): XOR carry_in into sum
   - Toffoli(q[0], q[1], q[4]): majority vote
   - Toffoli(q[0], q[2], q[4]): majority vote
   - Toffoli(q[1], q[2], q[4]): majority vote
4. **Measured**: q[3], q[4], q[5]

Let me trace through:
- Initial: |000000>
- After X(q[0]), X(q[1], X(q[2]): |111000>
- After CNOT(q[0], q[3]): q[3] = q[0] ⊕ q[3] = 1 ⊕ 0 = 1 → |111100>
- After CNOT(q[1], q[3]): q[3] = q[1] ⊕ q[3] = 1 ⊕ 1 = 0 → |111000>
- After CNOT(q[2], q[3]): q[3] = q[2] ⊕ q[3] = 1 ⊕ 0 = 1 → |111100>
- After Toffoli(q[0], q[1], q[4]): q[4] = q[0]·q[1] ⊕ q[4] = 1·1 ⊕ 0 = 1 → |111110>
- After Toffoli(q[0], q[2], q[4]): q[4] = q[0]·q[2] ⊕ q[4] = 1·1 ⊕ 1 = 0 → |111100>
- After Toffoli(q[1], q[2], q[4]): q[4] = q[1]·q[2] ⊕ q[4] = 1·1 ⊕ 0 = 1 → |111110>

Wait, let me recalculate. The Toffoli gate flips the target if both controls are |1>. So:
- Toffoli(q[0], q[1], q[4]): controls are q[0]=1, q[1]=1, so flip q[4]. q[4] was 0, now 1.
- Toffoli(q[0], q[2], q[4]): controls are q[0]=1, q[2]=1, so flip q[4]. q[4] was 1, now 0.
- Toffoli(q[1], q[2], q[4]): controls are q[1]=1, q[2]=1, so flip q[4]. q[4] was 0, now 1.

So final state: |111110> (q[5] stays 0)

Measured qubits: q[3], q[4], q[5]
- q[3] = 1
- q[4] = 1
- q[5] = 0

In bitstring notation with earlier measured qubit as higher bit:
- q[3] is the highest bit
- q[4] is the middle bit
- q[5] is the lowest bit

So the bitstring is: q[3]q[4]q[5] = 110 = |110>

Expected measurement: {|110>: 1.0}

This matches!

Now for the reasoning:

1. Goal: Implement a full adder variant computing sum (a⊕b⊕cin) on q[3] and carry-out (majority of a,b,cin) on q[4]
2. Qubits: 6 qubits (q[0]-q[5]), measuring q[3], q[4], q[5]
3. State evolution:
   - |000000> → |111000> (set inputs to 1,1,1)
   - After 3 CNOTs: q[3] = 1⊕1⊕1 = 1 → |111100>
   - After 3 Toffolis: q[4] flips 3 times (all controls are 1) → ends as 1 → |111110>
4. Final state |111110> measured on q[3],q

## isqTrain/3029

- task_id: `isqTrain/3029`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_multi_register`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `147`

### Prompt

这个isQ程序有问题，请找出错误并给出正确代码：

```isq
import std;
qbit q[4];
// GHZ-like state with X on q[2]
procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
    // X(q[2]); // BUG: missing initialization
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **The bug** is a missing `X` gate on `q[2]` (it is commented out), which prevents the state from being properly flipped.
2. **The fix** is to uncomment `X(q[2]);` so the gate is applied.
3. **State evolution**: Applying H and CNOTs yields $(|0000\rangle + |1111\rangle)/\sqrt{2}$. Applying `X(q[2])` flips the third qubit, resulting in the correct state $(|0010\rangle + |1101\rangle)/\sqrt{2}$.

## isqTrain/4199

- task_id: `isqTrain/4199`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `4041`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[4];

procedure main() {
    H(q[0]); H(q[1]); H(q[2]); H(q[3]);
    CNOT(q[0], q[1]);
    Rz(2.0 * 0.785, q[1]);
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);
    Rz(2.0 * 0.785, q[2]);
    CNOT(q[0], q[2]);
    CNOT(q[0], q[3]);
    Rz(2.0 * 0.785, q[3]);
    CNOT(q[0], q[3]);
    Rx(2.0 * 0.393, q[0]);
    Rx(2.0 * 0.393, q[1]);
    Rx(2.0 * 0.393, q[2]);
    Rx(2.0 * 0.393, q[3]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants a circuit analysis for an isQ quantum program. The analysis must explain the operations, state evolution, final state, and predicted probability distribution, following specific formatting and length constraints.

2.  **Analyze the isQ Circuit**:
    *   4 qubits: `q[0]`, `q[1]`, `q[2]`, `q[3]`. Initial state $|0000\rangle$.
    *   `H(q[0]); H(q[1]); H(q[2]); H(q[3]);`: Apply Hadamard to all qubits. State becomes $|++++\rangle$, which is an equal superposition of all $2^4=16$ basis states.
    *   `CNOT(q[0], q[1]); Rz(pi/4*2, q[1]); CNOT(q[0], q[1]);` -> Wait, the angle is `2.0 * 0.785`. $2 \times 0.785 = 1.57 \approx \pi/2$.
        Let's check the sequence: `CNOT(0,1), Rz(pi/2, 1), CNOT(0,1)`.
        This is equivalent to a controlled-Rz. Wait, `CNOT` - `Rz` - `CNOT`. If control is $|0\rangle$, $Rz$ is not applied (or applied to $|0\rangle$, no phase change). If control is $|1\rangle$, target flips to $|1\rangle$, gets $Rz$, flips back to $|0\rangle$. Wait, target was originally $|+\rangle$.
        Actually, let's trace carefully.
        Initial: $|0000\rangle$. H on all: $\frac{1}{4} \sum_{x \in \{0,1\}^4} |x\rangle$.
        Since `q[0]` is the control for `q[1]`, `q[2]`, `q[3]`, the operations only introduce phases if `q[0]` is 1.
        Let's see the action of `CNOT(q[0], q[i]) Rz(\pi/2, q[i]) CNOT(q[0], q[i])`.
        If `q[0]` = 0: `CNOT` does nothing. `Rz` applies to `q[i]`. Since `q[i]` is entangled with `q[0]`, wait, no. If `q[0]` is 0, `q[i]` is still in superposition but independent?
        Wait, the state is an equal superposition.
        Let $q_0$ be the control.
        State before CNOTs: $|+\rangle \otimes |+\rangle \otimes |+\rangle \otimes |+\rangle$.
        Write as $\frac{1}{\sqrt{2}}(|0\rangle_{q0} + |1\rangle_{q0}) \otimes |\psi_{123}\rangle$.
        When we apply `CNOT(0,1), Rz(pi/2, 1), CNOT(0,1)`:
        On $|0\rangle_{q0}$ branch: CNOT does nothing. Rz(pi/2) is applied to q1. Since q1 is $|+\rangle$, Rz(pi/2) changes it to $|\circlearrowright\rangle$ (or something similar). But wait, CNOT(0,1) on $|0\rangle|+\rangle$ is $|0\rangle|+\rangle$. Rz(pi/2) makes it $|0\rangle(Rz(\pi/2)|+\rangle)$. Then CNOT(0,1) does nothing again.
        On $|1\rangle_{q0}$ branch: CNOT(0,1) on $|1\rangle|+\rangle$ gives $\frac{1}{\sqrt{2}}(|11\rangle + |10\rangle)$. Rz(pi/2) applies phase to $|1\rangle_{q1}$, giving $\frac{1}{\sqrt{2}}(|11\rangle e^{-i\pi/4} + |10\rangle e^{i\pi/4})$. Then CNOT(0,1) flips q1 back, giving $|1\rangle \frac{1}{\sqrt{2}}(e^{-i\pi/4}|1\rangle + e^{i\pi/4}|0\rangle) = |1\rangle (Rz(\pi/2)|+\rangle)$.
        So overall, the sequence `CNOT, Rz, CNOT` on $

### Reference answer

Uniform distribution across 10 states

## isqTrain/3509

- task_id: `isqTrain/3509`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `5606`

### Prompt

What is the measurement probability distribution of this isQ program?

```
import std;

qbit q[2];

procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);

    X(q[0]);

    CNOT(q[0], q[1]);
    H(q[0]);

    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Initial State**: |q[0], q[1]> = |00>

2.  **Apply H(q[0])**:
    State of q[0] becomes (|0> + |1>)/sqrt(2).
    Combined state: 1/sqrt(2) (|00> + |10>).

3.  **Apply CNOT(q[0], q[1])**:
    Control is q[0], target is q[1].
    State becomes 1/sqrt(2) (|00> + |11>). (Bell state)

4.  **Apply X(q[0])**:
    Flips q[0]: |0> becomes |1>, |1> becomes |0>.
    State becomes 1/sqrt(2) (|10> + |01>).

5.  **Apply CNOT(q[0], q[1])**:
    Control is q[0], target is q[1].
    |10> -> |11>
    |01> -> |01>
    State becomes 1/sqrt(2) (|11> + |01>) = 1/sqrt(2) (|01> + |11>).
    Or factored as |1>(|0> + |1>)/sqrt(2).

6.  **Apply H(q[0])**:
    q[0] is currently |1>. Applying H to |1> yields |-> = (|0> - |1>)/sqrt(2).
    Wait, let's re-evaluate:
    H(|1>) = (|0> - |1>)/sqrt(2).
    So state is (|1>)(1/sqrt(2)) * (|0> - |1>)/sqrt(2)
    = 1/2 (|10> - |11>).
    Wait, let me re-read the state:
    State was |1>(|0> + |1>)/sqrt(2).
    Apply H to q[0]:
    q[0] is in |1>, so H |1> = (|0> - |1>)/sqrt(2).
    q[1] is in (|0> + |1>)/sqrt(2).
    Tensor product: (|0> - |1>)/sqrt(2) * (|0> + |1>)/sqrt(2) = 1/2 (|00> + |01> - |10> - |11>).

7.  **Measurement**:
    Probability of each basis state is |1/2|^2 = 1/4.
    Basis states with non-zero probability: |00>, |01>, |10>, |11>.

Let's double check.
Initial: |00>
H(0): (|0>+|1>)/sqrt(2) |0> = (|00>+|10>)/sqrt(2)
CX(0,1): (|00>+|11>)/sqrt(2)
X(0): (|10>+|01>)/sqrt(2)
CX(0,1): (|11>+|01>)/sqrt(2) = |1> (|0>+|1>)/sqrt(2)
H(0): (|0>-|1>)/2 (|0>+|1>) = 1/2(|00> + |01> - |10> - |11>).

Probabilities:
P(00) = 1/4
P(01) = 1/4
P(10) = 1/4
P(11) = 1/4

Wait, let me review step 4 to 5:
State: (|10> + |01>)/sqrt(2)
CX(0,1) on |10> -> |11>
CX(0,1) on |01> -> |01>
Result: (|11> + |01>)/sqrt(2) = |1>_0 * (|0>_1 + |1>_1)/sqrt(2).
H(0) on |1> -> (|0> - |1>)/sqrt(2).
State: 1/sqrt(2) (|0> - |1>) * 1/sqrt(2) (|0> + |1>) = 1/2 (|00> + |01> - |10> - |11>).
Probability of all states |00>, |01>, |10>, |11> is 1/4.

Is the qubit order in the output correct?
`M(q[0]); M(q[1]);`
"isQ Syntax Reference... --probs output: array indexed by measurement bitstring (earlier measured qubit = higher bit)."
So M(q[0]) is the higher bit, M(q[1]) is

### Reference answer

{'predicted_probs': {'01': 1.0}, 'explanation': 'The output is |01> with probability 1.0'}

## isqTrain/1092

- task_id: `isqTrain/1092`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_oracle`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2656`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;

// Oracle for constant function f(x) = 1 (always true)
oracle bool[1] f(bool x[2]) {
    // Constant function: output is always true
    bool res[] = [true];
    return res;
}

// Input register for 2-qubit Deutsch-Jozsa
qbit q[2];
// Ancilla for phase kickback mechanism
qbit anc[1];

procedure main() {
    // Prepare ancilla in |-> for phase kickback
    X(anc[0]);
    H(anc[0]);
    // Superposition on input register
    H(q[0]); H(q[1]);
    // Query oracle once
    f(q, anc);
    // Hadamard to decode function type
    H(q[0]); H(q[1]);
    // Constant function always yields |00>
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict measurement outcomes for an isQ program.
    *   Algorithm: Deutsch-Jozsa algorithm with a constant function $f(x) = 1$.
    *   Format: Specific output format ("## Circuit Analysis"), no code blocks, step-by-step reasoning, Dirac notation.
    *   Constraints: 3-8 lines for simple, up to 15 for complex. Concise, precise.

2.  **Analyze the isQ Code:**
    *   Qubits: `q[2]` (input), `anc[1]` (target/ancilla). Initial state $|000\rangle$.
    *   Gates on `anc[0]`: `X(anc[0])`, `H(anc[0])`. State becomes $|1\rangle \to |-\rangle$.
    *   Gates on `q[0], q[1]`: `H(q[0])`, `H(q[1])`. State becomes $|++\rangle = \frac{1}{2}\sum_{x=0}^{3} |x\rangle$.
    *   Total state after initialization: $|++\rangle \otimes |-\rangle$.
    *   Oracle `f(q, anc)`: $f(x) = 1$. The oracle performs $|x\rangle|y\rangle \to |x\rangle|y \oplus f(x)\rangle$. Because `anc` is in $|-\rangle$, phase kickback occurs. For $f(x)=1$, it applies a phase of $-1$ to all states $|x\rangle$. Wait, actually for constant 1, $|y \oplus 1\rangle$ applied to $|-\rangle$ gives $|1 \oplus y\rangle$, which is $-|-\rangle$. So the global phase is -1? Let's trace carefully.
        $|x\rangle(|0\rangle - |1\rangle)/\sqrt{2} \to |x\rangle(|0 \oplus f(x)\rangle - |1 \oplus f(x)\rangle)/\sqrt{2}$.
        If $f(x) = 1$, this is $|x\rangle(|1\rangle - |0\rangle)/\sqrt{2} = -|x\rangle(|0\rangle - |1\rangle)/\sqrt{2}$.
        So the input register gets a factor of $-1$ for all $x$. Since this applies to *all* $x$, it's just a global phase. $|++\rangle \to -|++\rangle$.
    *   Alternatively, as a phase oracle, $U_f: |x\rangle \to (-1)^{f(x)}|x\rangle$. Since $f(x)=1$, all $x$ get a phase of $-1$, which is a global phase.
    *   Next gates: `H(q[0])`, `H(q[1])`. Applying H to $|+\rangle|+\rangle$ gives $|00\rangle$. (The global phase $-1$ is irrelevant).
    *   Measurements: `M(q[0])`, `M(q[1])`. Both will be 0.

3.  **Draft the Reasoning:**
    *   Initial state is $|00\rangle|0\rangle$.
    *   X and H on ancilla prepare it in $|-\rangle$.
    *   H on input register prepares it in an equal superposition: $|+\rangle|+\rangle|-\rangle$.
    *   The oracle applies a phase $(-1)^{f(x)}$ to each basis state $|x\rangle$. For constant $f(x)=1$, all states get a phase of $-1$.
    *   This $-1$ is a global phase and can be ignored. The input state remains $\frac{1}{2}\sum |x\rangle$.
    *   The final Hadamard gates on the input register reverse the initial superposition, bringing the state back to $|0\rangle|0\rangle$ (and the ancilla remains in $|-\rangle$).
    *   Measuring the input register yields $|00\rangle$ with 100% probability.

4.  **Refine to Meet Constraints:**
    *   Must be concise, 3-8 lines.
    *   Include step-by-step evolution.
    *   End with predicted distribution.

    *Drafting:*
    ## Circuit Analysis
    1. The circuit applies a 2-qubit Deutsch-Jozsa algorithm to classify a constant function.
    2. Initialization: Input register `q` starts in $|00\rangle$ and ancilla `anc` in $|

### Reference answer

{'predicted_probs': {'0': 1.0}, 'explanation': 'Parametric variant of isqEval/432. Dimension: predict probabilities for reference circuit.'}

## isqTrain/2971

- task_id: `isqTrain/2971`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2776`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;
qbit q[4];
procedure main() {
    H(q[0]);
    H(q[1]);
    H(q[2]);
    H(q[3]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
    CNOT(q[3], q[0]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants to know the output probability distribution of an isQ quantum circuit. I need to generate a concise, step-by-step reasoning in Dirac notation, listing each gate's effect, and ending with the predicted probability distribution.

2.  **Analyze the Circuit:**
    *   4 qubits: $q[0], q[1], q[2], q[3]$. Initial state $|0000\rangle$.
    *   Gates applied:
        *   `H(q[0])`
        *   `H(q[1])`
        *   `H(q[2])`
        *   `H(q[3])`
        *   `CNOT(q[0], q[1])`
        *   `CNOT(q[1], q[2])`
        *   `CNOT(q[2], q[3])`
        *   `CNOT(q[3], q[0])`
    *   Measurements: M(q[0]), M(q[1]), M(q[2]), M(q[3]).

3.  **Step-by-Step State Evolution:**
    *   Initial: $|0000\rangle$.
    *   After `H(q[0])` to `H(q[3])`: $\frac{1}{4} \sum_{x \in \{0,1\}^4} |x\rangle$.
        Specifically: $\frac{1}{4} (|0000\rangle + |0001\rangle + |0010\rangle + \dots + |1111\rangle)$.
        Actually, let's trace the basis states.
    *   Let's see the effect of the CNOTs.
        *   `CNOT(q[0], q[1])`: $x_0 \oplus x_1$ in place of $x_1$.
        *   `CNOT(q[1], q[2])`: new $x_1 \oplus x_2$ in place of $x_2$.
        *   `CNOT(q[2], q[3])`: new $x_2 \oplus x_3$ in place of $x_3$.
        *   `CNOT(q[3], q[0])`: new $x_3 \oplus x_0$ in place of $x_0$.
    *   Let's track basis state $|x_0 x_1 x_2 x_3\rangle$:
        *   Start: $|x_0, x_1, x_2, x_3\rangle$
        *   After CNOT(0,1): $|x_0, x_0 \oplus x_1, x_2, x_3\rangle$
        *   After CNOT(1,2): $|x_0, x_0 \oplus x_1, x_0 \oplus x_1 \oplus x_2, x_3\rangle$
        *   After CNOT(2,3): $|x_0, x_0 \oplus x_1, x_0 \oplus x_1 \oplus x_2, x_0 \oplus x_1 \oplus x_2 \oplus x_3\rangle$
        *   After CNOT(3,0): $|x_0 \oplus (x_0 \oplus x_1 \oplus x_2 \oplus x_3), x_0 \oplus x_1, x_0 \oplus x_1 \oplus x_2, x_0 \oplus x_1 \oplus x_2 \oplus x_3\rangle$
        *   Simplify $x_0 \oplus (x_0 \oplus x_1 \oplus x_2 \oplus x_3)$: this is $x_1 \oplus x_2 \oplus x_3$.
        *   Wait, is this mapping bijective?
        *   Let's check the matrix:
            $y_0 = x_1 \oplus x_2 \oplus x_3$
            $y_1 = x_0 \oplus x_1$
            $y_2 = x_0 \oplus x_1 \oplus x_2$
            $y_3 = x_0 \oplus x_1 \oplus x_2 \oplus x_3$
        *   Since CNOTs are reversible, it is a permutation of the $2^4 = 16$ basis states.
        *   Since we started with a uniform superposition over all 16 basis states (each has amplitude $1/4

### Reference answer

{'predicted_probs': {'0000': 0.06250000000000001, '0001': 0.06250000000000001, '0010': 0.06250000000000001, '0011': 0.06250000000000001, '0100': 0.06250000000000001, '0101': 0.06250000000000001, '0110': 0.06250000000000001, '0111': 0.06250000000000001, '1000': 0.06250000000000001, '1001': 0.06250000000000001, '1010': 0.06250000000000001, '1011': 0.06250000000000001, '1100': 0.06250000000000001, '1101': 0.06250000000000001, '1110': 0.06250000000000001, '1111': 0.06250000000000001}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/2936

- task_id: `isqTrain/2936`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2094`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;
qbit q[4];
procedure main() {
    for i in 0:4 {
        H(q[i]);
    }
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations applied:** The circuit initializes a 4-qubit register in the state |0000⟩. It then applies a Hadamard gate (H) independently to each of the 4 qubits. Finally, it measures all 4 qubits.
2. **State evolution:** 
   - Initial state: |0000⟩
   - Applying H to each qubit transforms |0⟩ into the superposition |+⟩ = (1/√2)(|0⟩ + |1⟩). 
   - The joint 4-qubit state becomes the tensor product of these individual superpositions: (1/√2)(|0⟩ + |1⟩) ⊗ (1/√2)(|0⟩ + |1⟩) ⊗ (1/√2)(|0⟩ + |1⟩) ⊗ (1/√2)(|0⟩ + |1⟩).
3. **Final state before measurement:** The system is in a uniform superposition of all 16 possible 4-qubit basis states: (1/4) * Σ|x⟩ for x from 0000 to 1111.
4. **Predicted probability distribution:** Because the amplitude of each basis state is 1/4, the probability of measuring any specific state is exactly |1/4|² = 1/16 = 0.0625. The distribution is perfectly uniform across all states.

Predicted probabilities: 
|0000⟩: 0.0625, |0001⟩: 0.0625, |0010⟩: 0.0625, |0011⟩: 0.0625, |0100⟩: 0.0625, |0101⟩: 0.0625, |0110⟩: 0.0625, |0111⟩: 0.0625, |1000⟩: 0.0625, |1001⟩: 0.0625, |1010⟩: 0.0625, |1011⟩: 0.0625, |1100⟩: 0.0625, |1101⟩: 0.0625, |1110⟩: 0.0625, |1111⟩: 0.0625

### Reference answer

{'predicted_probs': {'0000': 0.06250000000000001, '0001': 0.06250000000000001, '0010': 0.06250000000000001, '0011': 0.06250000000000001, '0100': 0.06250000000000001, '0101': 0.06250000000000001, '0110': 0.06250000000000001, '0111': 0.06250000000000001, '1000': 0.06250000000000001, '1001': 0.06250000000000001, '1010': 0.06250000000000001, '1011': 0.06250000000000001, '1100': 0.06250000000000001, '1101': 0.06250000000000001, '1110': 0.06250000000000001, '1111': 0.06250000000000001}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/4032

- task_id: `isqTrain/4032`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `5028`

### Prompt

这段isQ代码有bug，帮我找出并修复：

```
import std;
// Inverse QFT on 3 qubits with input |101>
qbit q[3];

procedure main() {
    // Prepare input
    X(q[0]);
    X(q[2]);

    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    H(q[2]);
    ctrl Rz(2.0 * -2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    H(q[1]);
    ctrl Rz(-2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    ctrl Rz(-2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    H(q[0]);
    // Measure after inverse QFT
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: wrong parameter)

### Chain-of-thought reasoning

Let me analyze this bug fix task.

The task is about a 3-qubit inverse QFT with input |101>.

First, let me understand what inverse QFT does. The QFT (Quantum Fourier Transform) maps a computational basis state to a Fourier basis state. The inverse QFT does the reverse.

For a 3-qubit system, the QFT of |101⟩ would be:
- |101⟩ in binary is 5
- QFT|5⟩ = (1/√8) Σ_{k=0}^{7} e^{2πi·5k/8} |k⟩

The inverse QFT should map this back to |101⟩.

But wait, the problem says the input is |101⟩ and we're applying inverse QFT. Let me re-read...

"3-qubit inverse QFT with input |101>"

So we start with |101⟩ and apply inverse QFT. 

The inverse QFT of |101⟩ would be:
- |101⟩ = |5⟩
- IQFT|5⟩ = (1/√8) Σ_{k=0}^{7} e^{-2πi·5k/8} |k⟩

This would give an equal superposition with different phases, and when measured, each outcome would have equal probability 1/8.

Now let's look at the expected measurement probabilities:
{|000>: 0.125, |001>: 0.125, |010>: 0.125, |011>: 0.125, |100>: 0.125, |101>: 0.125, |110>: 0.125, |111>: 0.125}

This confirms that the output should be an equal superposition of all 8 states, each with probability 1/8.

Now let's look at the buggy code:

The code prepares |101⟩ by applying X to q[0] and q[2].

Then it applies what should be the inverse QFT circuit.

The inverse QFT for 3 qubits typically works as follows:
1. Start with qubit 2 (highest bit)
2. Apply H to qubit 2
3. Apply controlled Rz rotations from qubit 1 to qubit 2, and qubit 0 to qubit 2
4. Apply H to qubit 1
5. Apply controlled Rz rotation from qubit 0 to qubit 1
6. Apply H to qubit 0
7. Swap qubits 0 and 2

Wait, let me reconsider the qubit ordering. In the code, q[0] is the least significant bit (LSB) and q[2] is the most significant bit (MSB) for |101⟩:
- q[0] = 1 (LSB)
- q[1] = 0
- q[2] = 1 (MSB)

Looking at the code:

This is a swap operation (three-CNOT decomposition) between q[0] and q[2].

After the swap (three-CNOT decomposition):
- q[0] = 1 (was q[2])
- q[1] = 0
- q[2] = 1 (was q[0])

Then the inverse QFT operations follow.

The bug is in this line:

The fixed version has:

So the bug is `2.0 * -2.0` instead of just `-2.0`. This means the angle was multiplied by 2 incorrectly, giving `-4π/4 = -π` instead of `-2π/4 = -π/2`.

Let me verify the inverse QFT circuit structure:

For QFT, the circuit applies:
- H on qubit k
- Controlled R_k (rotation by 2π/2^k) from qubits k+1, k+2, ... to qubit k

For inverse QFT, we apply the inverse operations in reverse order.

The standard QFT circuit for 3 qubits (q[0] = MSB, q[2] = LSB) would be:
1. H(q[0])
2. CR_2(q[1], q[0]) - controlled rotation by 2π/4
3. CR_3(q[2], q[0]) - controlled rotation by 2π/8
4. H(q[1])
5.

## isqTrain/2946

- task_id: `isqTrain/2946`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `basis_change`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2515`

### Prompt

用isQ实现prepares 2 qubit(s) in the |-> state (X then H) and measures in the computational basis.

Requirements:
- Declare `qbit q[2];` at global scope.
- Apply X followed by H to each qubit.
- Measure all 2 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare 2 qubits in the |-> state (by applying X then H) and measure in the computational basis.
2. **Qubits**: 2 qubits declared globally (`q[2]`), both measured.
3. **State evolution**:
   - Start: |00⟩
   - After X(q[0]), X(q[1]): |11⟩ (X flips |0⟩ to |1⟩)
   - After H(q[0]), H(q[1]): |−⟩|−⟩ = (1/2)(|00⟩ − |01⟩ − |10⟩ + |11⟩), since H|1⟩ = |−⟩ = (|0⟩−|1⟩)/√2
4. **Expected probabilities**: Each basis state has amplitude ±1/2, so |amplitude|² = 1/4 for each: P(|00⟩)=0.25, P(|01⟩)=0.25, P(|10⟩)=0.25, P(|11⟩)=0.25.

## isqTrain/3560

- task_id: `isqTrain/3560`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `ancilla_usage`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3086`

### Prompt

Fix the bug in the following isQ program.

Bug description: Wrong CNOT direction

The program should 5-qubit repetition code encoding |0_L>=|00000>.

### Chain-of-thought reasoning

## Bug Analysis

**Bug:** The first CNOT gate `CNOT(q[1], q[0])` has reversed arguments — q[1] is used as control instead of q[0]. This breaks the fan-out encoding pattern where q[0] should be the single control broadcasting its state to all other qubits.

**Fix:** Change `CNOT(q[1], q[0])` to `CNOT(q[0], q[1])`, making q[0] the control in all four CNOTs.

**State evolution (corrected circuit):**
1. Initial state: |00000⟩
2. `CNOT(q[0], q[1])`: control q[0]=|0⟩ → no flip → |00000⟩
3. `CNOT(q[0], q[2])`: control q[0]=|0⟩ → no flip → |00000⟩
4. `CNOT(q[0], q[3])`: control q[0]=|0⟩ → no flip → |00000⟩
5. `CNOT(q[0], q[4])`: control q[0]=|0⟩ → no flip → |00000⟩
6. Final state: |00000⟩ ✓

While the bug is masked for |0_L⟩ (since CNOT with |0⟩ control is identity regardless of direction), it would cause incorrect encoding for |1_L⟩: the buggy `CNOT(q[1], q[0])` would clear q[0]'s |1⟩ back to |0⟩ instead of copying it to q[1].
