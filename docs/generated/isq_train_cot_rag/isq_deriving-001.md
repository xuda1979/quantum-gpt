# ISQ training COT RAG corpus: isq_deriving shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1644

- task_id: `isqTrain/1644`
- task_type: `code_generation`
- category: `isq_deriving`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `5477`

### Prompt

Code this in isQ: Define a custom X gate using `deriving gate`, then use it as a controlled gate (ctrl my_x) to entangle two qubits. Prepare |10> and apply ctrl my_x.

### Chain-of-thought reasoning

## Reasoning
Goal: Prepare |10⟩ and entangle using a controlled custom X gate, yielding |11⟩.

Qubits: 2 (q[0], q[1]), both measured.

State evolution:
- Initial: |00⟩
- X(q[0]): |10⟩ (flips q[0] to |1⟩)
- ctrl my_x(q[0], q[1]): Since q[0]=|1⟩, the custom X gate activates on q[1], flipping |0⟩→|1⟩, giving |11⟩

Expected probabilities: Final state is |11⟩ with certainty, so P(|11⟩) = 1.0.

## isqTrain/224

- task_id: `isqTrain/224`
- task_type: `output_prediction`
- category: `isq_deriving`
- difficulty: `intermediate`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `893`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;

qbit q[2];

procedure main() {
    X(q[1]);
    nctrl X(q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the isQ program:**
    -   `X(q[1])`: Apply an X gate to qubit 1. Initial state $|00\rangle$ becomes $|01\rangle$ (assuming standard notation where q[0] is the higher bit or vice versa, let's trace carefully: usually q[0] is bit 0, q[1] is bit 1. If initial is $|q_1 q_0\rangle = |00\rangle$, X(q[1]) makes it $|10\rangle$. Let's stick to the standard Dirac where the left-most bit is the highest index, or explicitly write $q_0, q_1$. Wait, $|q_1 q_0\rangle = |0\rangle_{q_1} \otimes |0\rangle_{q_0}$. Applying X to $q_1$ gives $|1\rangle_{q_1} \otimes |0\rangle_{q_0} = |10\rangle$). Let's use $|q_1 q_0\rangle$ for clarity, but actually it's easier to just write $|q[0], q[1]\rangle = |0, 0\rangle$. After `X(q[1])`, it becomes $|0, 1\rangle$.
    -   `nctrl X(q[0], q[1])`: `nctrl` means negative control. "Apply X to q[0] if q[1] is |0>". Currently, q[1] is in $|1\rangle$. Since the control is negative (0-triggered), and q[1] is 1, the X gate on q[0] is *not* applied.
    -   Wait, let's double check isQ syntax: `nctrl X(target, control)`. Wait, standard syntax for isQ is `ctrl @[control] Gate(target)` or something. But the program has `nctrl X(q[0], q[1])`. Wait, looking at the provided reference `nctrl X(q[0], q[1])`. If it's `nctrl Gate(target, control)`, then `q[1]` is the control, `q[0]` is the target.
    -   Let's re-read the syntax: "Control modifier: `ctrl @[c1, c2] Gate(target);`". But here it's `nctrl X(q[0], q[1])`. Is it a built-in custom gate or isQ syntax? Actually, isQ often uses `ctrl` as a prefix, but wait! Maybe `nctrl X(q[0], q[1])` is an alternative? Or maybe `X(q[0], q[1])` is a CX gate? No, standard X gate is single qubit. What if `nctrl` is a built-in syntax modifier? "nctrl" = negative control.
    -   Let's assume `q[0]` is target, `q[1]` is control. Negative control means X is applied to `q[0]` if `q[1]` is in state $|0\rangle$.
    -   Since `q[1]` is in $|1\rangle$, X is NOT applied.
    -   Wait, is `q[1]` the control or target in `nctrl X(q[0], q[1])`? Usually in isQ, `ctrl X(q[0], q[1])` means `q[1]` is control, `q[0]` is target.
    -   Let's verify the predicted output: `{|00>: 1.0}`. Wait! The expected measurement is `{|00>: 1.0}`. But `X(q[1])` sets `q[1]` to 1. How can it be `|00>`?
    -   Let's rethink. If initial is $|q[0]q[1]\rangle = |00\rangle$. `X(q[1])` makes it $|01\rangle$.
    -   If `nctrl X(q[0], q[1])` applies X to `q[0]` if `q[1]` is 0... it doesn't.
    -   Wait, if `nctrl X(q[0], q[1])` means "apply X to q[1] if q[0] is 0"?
    -   If `X(q[0], q[1])` in isQ means CNOT with `q[0]` as control and `q[1]` as target? Then `nctrl` means it applies if `q[0]` is 0. If `q[0]` is

### Reference answer

{'predicted_probs': {'0': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/78. Dimension: predict probabilities for reference circuit.'}

## isqTrain/230

- task_id: `isqTrain/230`
- task_type: `code_generation`
- category: `isq_deriving`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `2827`

### Prompt

I need an isQ program to implements a variant of the gate_decomposition pattern using q[4] -> q[6]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a triple-controlled Z gate variant with qubits q[4] and q[5] as unused ancillas in the ground state.
2. **Qubits**: 6 qubits (q[0]-q[5]), all measured.
3. **State evolution**:
   - Initial: |000000⟩
   - After X(q[0]), X(q[1]), X(q[2]): |111000⟩
   - After ctrl<3> my_z(q[0], q[1], q[2], q[3]): Z is applied to q[3] when q[0]=q[1]=q[2]=|1⟩. Since q[3]=|0⟩ and Z|0⟩=|0⟩, state remains |111000⟩
4. **Expected probabilities**: Since q[4] and q[5] are never operated on, they remain |0⟩. The triple-controlled Z has no effect because Z|0⟩=|0⟩, so the final state is |111000⟩ with probability 1.0.

## isqTrain/1913

- task_id: `isqTrain/1913`
- task_type: `output_prediction`
- category: `isq_deriving`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_deriving_gate`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `1853`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
procedure my_z(qbit a) {
    Z(a);
} deriving gate
qbit q[4];
procedure main() {
    X(q[0]);
    X(q[1]);
    X(q[2]);
    ctrl<3> my_z(q[0], q[1], q[2], q[3]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit starts in the initial state $|0000\rangle$.
2. Applying X gates to q[0], q[1], and q[2] flips them to $|1\rangle$, changing the state to $|1110\rangle$.
3. The `ctrl<3> my_z` operation applies a Z gate to q[3] conditioned on q[0], q[1], and q[2] being $|1\rangle$. Since the target q[3] is in the $|0\rangle$ state, the Z gate acts as the identity ($Z|0\rangle = |0\rangle$), leaving the overall state unchanged at $|1110\rangle$.
4. Measuring all qubits deterministically yields the outcome where the first three qubits are 1 and the fourth is 0.

Predicted probability distribution: {'1110': 1.0}

### Reference answer

{'predicted_probs': {'1110': 1.0}, 'explanation': 'ctrl<N> syntax.'}

## isqTrain/2544

- task_id: `isqTrain/2544`
- task_type: `code_equivalence`
- category: `isq_deriving`
- difficulty: `intermediate`
- concept_tags: `global_phase`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `999`

### Prompt

Are these two quantum circuits equivalent in terms of measurement output?

Circuit 1:
```isq
import std;

qbit q[2];

procedure main() {
    X(q[0]);
    H(q[1]);
    ctrl S(q[0], q[1]);
    H(q[1]);
    M(q[0]); M(q[1]);
}

```

Circuit 2:
```isq
import std;

qbit q[2];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    X(q[0]);
    H(q[1]);
    ctrl S(q[0], q[1]);
    H(q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis

1. **Program A**: Initializes |00⟩, applies X to q[0] yielding |10⟩, applies H to q[1] creating (|10⟩+|11⟩)/√2, applies controlled-S (q[0] controls q[1]) giving (|10⟩+i|11⟩)/√2, then applies H to q[1] again producing ((1+i)|10⟩+(1-i)|11⟩)/2, followed by measurements.

2. **Program B**: Identical sequence of operations to Program A, with the addition of `GPhase(0.0)` at the start.

3. **Key difference**: Program B includes `GPhase(0.0)`, which applies a global phase factor of e^(i·0) = 1 — effectively a no-op that leaves the quantum state unchanged.

4. **Measurement probabilities**: Both programs produce identical quantum states before measurement. The global phase of 0 is physically meaningless and does not affect measurement outcomes. Both yield P(10) = 1/2 and P(11) = 1/2.

5. **Verdict**: Equivalent — Yes

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/233

- task_id: `isqTrain/233`
- task_type: `output_prediction`
- category: `isq_deriving`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_deriving_gate`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `5266`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;

procedure my_z(qbit a) {
    Z(a);
} deriving gate

qbit q[4];

procedure main() {
    X(q[0]);
    X(q[1]);
    X(q[2]);
    ctrl<3> my_z(q[0], q[1], q[2], q[3]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initialization & X Gates:** The circuit starts with 4 qubits in |0000>. X gates are applied to q[0], q[1], and q[2], flipping them to |1> and evolving the state to |1110>.
2. **Controlled Z Gate:** The `ctrl<3> my_z` gate acts as a triple-controlled Z gate, applying a Z gate to the target q[3] only if control qubits q[0], q[1], and q[2] are all in the |1> state.
3. **State Evolution:** Since the control condition is met, Z is applied to q[3]. Because Z|0> = |0>, the target qubit remains unchanged in the |0> state.
4. **Final State:** The overall quantum state remains |1110> just before measurement.

Predicted probability distribution: {|1110>: 1.0}

### Reference answer

{'predicted_probs': {'14': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/80. Dimension: predict probabilities for reference circuit.'}

## isqTrain/4631

- task_id: `isqTrain/4631`
- task_type: `output_prediction`
- category: `isq_deriving`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `2610`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;

procedure entangle(qbit a, qbit b) {
    H(a);
    CNOT(a, b);
} deriving gate

qbit q[3];

procedure main() {
    X(q[0]);
    ctrl entangle(q[0], q[1], q[2]);
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants a circuit analysis for an isQ program. The program defines a custom gate `entangle`, applies it to `q[1]` and `q[2]` controlled by `q[0]`, with `q[0]` initially flipped to `|1>` and then flipped back to `|0>` before measurement. The predicted output a concise step-by-step reasoning using Dirac notation, starting with "## Circuit Analysis" and ending with the predicted probabilities.

2.  **Analyze the isQ Program**:
    *   `qbit q[3]`: Initial state is $|000\rangle$.
    *   `X(q[0])`: Flips $q_0$ to $|1\rangle$. State becomes $|100\rangle$.
    *   `entangle(a, b)` is defined as `H(a); CNOT(a, b)`. This creates a Bell state $(|00\rangle + |11\rangle)/\sqrt{2}$.
    *   `ctrl entangle(q[0], q[1], q[2])`: Since `q[0]` is $|1\rangle$, the controlled gate applies `entangle(q[1], q[2])`. So $q_1$ gets H, then CNOT($q_1$, $q_2$).
        *   Before: $|1\rangle_{q_0} \otimes |00\rangle_{q_1, q_2}$
        *   After H($q_1$): $|1\rangle \otimes (|0\rangle + |1\rangle)/\sqrt{2} \otimes |0\rangle = (|100\rangle + |110\rangle)/\sqrt{2}$
        *   After CNOT($q_1$, $q_2$): $(|100\rangle + |111\rangle)/\sqrt{2}$
    *   `X(q[0])`: Flips $q_0$ back to $|0\rangle$. State becomes $(|000\rangle + |011\rangle)/\sqrt{2}$.
    *   Measurement: `M(q[0]); M(q[1]); M(q[2])`.
        *   Outcomes: $|000\rangle$ with probability $0.5$, and $|011\rangle$ with probability $0.5$.

3.  **Draft the Explanation** (following constraints: 3-8 lines for simple, up to 15 for complex, Dirac notation):
    *   Initial state $|000\rangle$.
    *   Apply `X(q[0])` $\to |100\rangle$.
    *   `ctrl entangle(q[0], q[1], q[2])` applies $H(q_1)$ and $CNOT(q_1, q_2)$ because $q_0$ is $|1\rangle$.
    *   $H(q_1)$ changes state to $\frac{1}{\sqrt{2}}(|100\rangle + |110\rangle)$.
    *   $CNOT(q_1, q_2)$ changes state to $\frac{1}{\sqrt{2}}(|100\rangle + |111\rangle)$.
    *   Apply `X(q[0])` $\to \frac{1}{\sqrt{2}}(|000\rangle + |011\rangle)$.
    *   Measurement probabilities: $|000\rangle$ (50%) and $|011\rangle$ (50%).

4.  **Refine to match style constraints**:
    "## Circuit Analysis
    1. Initial state is |000>.
    2. X(q[0]) flips the first qubit, changing the state to |100>.
    3. `ctrl entangle(q[0], q[1], q[2])` activates since q[0] is |1>, applying H(q[1]) and CNOT(q[1], q[2]).
    4. H(q[1]) puts the second qubit in superposition: (|100> + |110>)/sqrt(2).
    5. CNOT(q[1], q[2]) entangles the second and third qubits: (|100> + |111>)/sqrt(2).
    6. X(q[0]) flips the first qubit back to |0>, resulting in the final state (|000> + |011>)/sqrt(2).
    7. Measuring all qubits yields |000> and |011> with equal probabilities."

5.  **Final Review against rules**:
    *   Starts with "## Circuit Analysis"? Yes.
    *   Dirac notation?

### Reference answer

{'predicted_probs': {'000': 0.5, '011': 0.5}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|000>) = 0.5000, P(|011>) = 0.5000.'}

## isqTrain/1641

- task_id: `isqTrain/1641`
- task_type: `code_generation`
- category: `isq_deriving`
- difficulty: `basic`
- concept_tags: `isq_syntax_deriving_gate`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `1473`

### Prompt

用isQ实现Define a custom gate that applies X twice using `deriving gate`, apply to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Define a custom gate applying X twice via `deriving gate`, apply it to |0⟩, and measure.
2. Qubits: 1 qubit (q[0]), which is measured.
3. State evolution:
   - Initial state: |0⟩
   - After first X: |1⟩
   - After second X: |0⟩
4. Since X² = I, the state returns to |0⟩, yielding measurement probabilities {|0⟩: 1.0}.

## isqTrain/2543

- task_id: `isqTrain/2543`
- task_type: `code_equivalence`
- category: `isq_deriving`
- difficulty: `difficult`
- concept_tags: `global_phase`, `isq_syntax_deriving_gate`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `1002`

### Prompt

判断以下两段isQ代码是否产生相同的测量结果：

代码1：
```isq
import std;

procedure my_h(qbit a) {
    H(a);
} deriving gate

qbit q[2];

procedure main() {
    X(q[0]);
    X(q[1]);
    nctrl inv my_h(q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

代码2：
```isq
import std;

procedure my_h(qbit a) {
    H(a);
} deriving gate

qbit q[2];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    X(q[0]);
    X(q[1]);
    nctrl inv my_h(q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A**: Initializes two qubits to |0>. Applies X to both, changing the state to |11>. Executes `nctrl inv my_h(q[0], q[1])`, which applies H to `q[1]` only if `q[0]` is |0>. Since `q[0]` is |1>, the condition fails and no gate is applied. The state remains |11>, yielding a 100% probability of measuring 11.
2. **Program B**: Initializes two qubits to |0>. Applies `GPhase(0.0)` (a global phase of 0 radians). Applies X to both qubits, changing the state to |11>. Executes the same `nctrl inv my_h(q[0], q[1])`, which again does nothing. The state remains |11>, yielding a 100% probability of measuring 11.
3. **Key difference**: Program B explicitly applies a `GPhase(0.0)` gate at the start, which Program A lacks.
4. **Probability equivalence**: The `GPhase(0.0)` gate applies a global phase factor of $e^{i \cdot 0} = 1$. This is mathematically equivalent to the identity operation and has no effect on the physical state or measurement outcomes.
5. **Verdict**: Yes, the programs are equivalent.

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/1642

- task_id: `isqTrain/1642`
- task_type: `code_generation`
- category: `isq_deriving`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_deriving_gate`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `2106`

### Prompt

Code this in isQ: Define a custom CNOT gate using `deriving gate`, apply to |10> and measure.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Define a custom CNOT gate, apply it to a 2-qubit state |10>, and measure the outcome.
2. Qubits: 2 qubits (`q[0]`, `q[1]`) are required, both of which are measured.
3. Evolution:
   - Initial state is |00>.
   - `X(q[0])` flips the first qubit, preparing the state |10>.
   - `my_cnot(q[0], q[1])` applies CNOT with `q[0]` as control and `q[1]` as target.
   - Because the control qubit is in the |1> state, the target qubit is flipped from |0> to |1>, resulting in the final state |11>.
4. Probabilities: The final state is determin
