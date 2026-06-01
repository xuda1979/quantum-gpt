# ISQ training COT RAG corpus: isq_deriving shard 3

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4634

- task_id: `isqTrain/4634`
- task_type: `output_prediction`
- category: `isq_deriving`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `3199`

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
    H(q[2]); // superposition on last qubit
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict probability distribution and explain reasoning for an isQ program.
    *   Format constraint: 3-8 lines for simple, up to 15 for complex. This is a 3-qubit circuit, fairly simple, but needs precise state tracking.
    *   Constraint: Output ONLY the analysis starting with "## Circuit Analysis". End with the predicted probability distribution.
    *   No code blocks.

2.  **Analyze the isQ code:**
    *   `import std;`
    *   `procedure entangle(qbit a, qbit b) { H(a); CNOT(a, b); } deriving gate`
        *   This defines a custom gate. Let's call it $E_{ab}$. $E = CNOT \cdot (H \otimes I)$. Maps $|00\rangle \to |++\rangle$.
    *   `qbit q[3];`
        *   Initial state: $|000\rangle$.
    *   `X(q[0]);`
        *   State becomes $|100\rangle$.
    *   `ctrl entangle(q[0], q[1], q[2]);`
        *   Wait, the gate `entangle` takes 2 parameters (`a` and `b`), but the call passes 3 qubits: `ctrl entangle(q[0], q[1], q[2])`.
        *   Let's parse `ctrl entangle(q[0], q[1], q[2])`. In isQ, `ctrl` can be applied to a gate.
        *   If `entangle(a, b)` takes 2 arguments, passing 3 to its `ctrl` version implies the first one is the control, and the next two are passed to the gate? Or does `ctrl` make the *first* argument a control? No, typically `ctrl` uses `@` to specify controls if multiple, or it just adds a control. Wait, `ctrl Gate(q1, q2)` usually means the *entire* operation is controlled.
        *   Let's look at the syntax: `ctrl entangle(q[0], q[1], q[2])`. Wait, `entangle` signature is `entangle(qbit a, qbit b)`. It only takes 2 qubits!
        *   Ah! The syntax reference says: "Control modifier: `ctrl @[c1, c2] Gate(target);`" but here it's `ctrl entangle(q[0], q[1], q[2])`. If the gate takes 2 arguments, passing 3 means the first is the control, and `q[1], q[2]` are the gate arguments. Let's verify isQ semantics. Yes, if a gate takes $k$ arguments, `ctrl` adds 1 argument before them.
        *   So `ctrl entangle(ctrl, a, b)` means: if `ctrl` is $|1\rangle$, apply `entangle(a, b)`.
        *   Let's check the state before this: $|100\rangle$.
        *   So `q[0]` is $|1\rangle$. Thus, the controlled gate *is* triggered.
        *   It applies `entangle(q[1], q[2])`.
        *   `entangle` applies `H(q[1])` then `CNOT(q[1], q[2])`.
        *   Initial for q[1], q[2] is $|00\rangle$.
        *   After $H(q[1])$: $|+0\rangle = \frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$.
        *   After $CNOT(q[1], q[2])$: $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$.
        *   Overall state is $|1\rangle \otimes \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle) = \frac{1}{\sqrt{2}}(|100\rangle + |111\rangle)$.
    *   `H(q[2]); // superposition on last qubit`
        *   Apply H to q[2].
        *   $H$ on $|0\rangle$ is $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
        *   $H$ on $|1\rangle$ is $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
        *   State becomes $\frac{1}{\sqrt{2}}(|10\rangle \otimes |+\rangle

### Reference answer

{'predicted_probs': {'100': 0.25, '101': 0.25, '110': 0.25, '111': 0.25}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|100>) = 0.2500, P(|101>) = 0.2500, P(|110>) = 0.2500, P(|111>) = 0.2500.'}

## isqTrain/1643

- task_id: `isqTrain/1643`
- task_type: `code_generation`
- category: `isq_deriving`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_deriving_gate`, `isq_syntax_inv`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `2195`

### Prompt

Create an isQ quantum circuit that Define a custom S gate using `deriving gate`, apply it then apply its inverse using `inv`. Measure. The result should be identity.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Demonstrate that applying a custom S gate followed by its inverse (`inv`) yields the identity operation, leaving the qubit in its original state.
2. **Qubits**: 1 qubit (`q[0]`) is used and measured.
3. **State evolution**:
   - Initial state: |0⟩
   - After `my_s(q[0])` (applies S gate): S|0⟩ = |0⟩ (S = [[1,0],[0,i]] leaves |0⟩ unchanged)
   - After `inv my_s(q[0])` (applies S† = [[1,0],[0,-i]]): S†|0⟩ = |0⟩
   - Final state: |0⟩
4. **Expected probabilities**: Since S†·S = I, the state returns to |0⟩ with probability 1.0.

## isqTrain/4632

- task_id: `isqTrain/4632`
- task_type: `output_prediction`
- category: `isq_deriving`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `11`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

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
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict probability distribution of an isQ quantum program.
    *   Input: isQ program using `ctrl entangle`, `X`, `H`, `Z`.
    *   Output format: "## Circuit Analysis", 3-15 lines, Dirac notation, concise step-by-step reasoning, no code blocks, end with probability distribution.

2.  **Analyze the isQ Program:**
    *   Initialization: `qbit q[3]` initialized to $|000\rangle$.
    *   `X(q[0])`: Apply X gate to q[0]. State becomes $|100\rangle$.
    *   `ctrl entangle(q[0], q[1], q[2])`:
        *   `entangle` is defined as `H(a); CNOT(a, b);`.
        *   With `ctrl`, it means "control on some other qubit". Wait, in isQ, `ctrl @[c] Gate(t)` applies a controlled-Gate.
        *   Wait, the syntax is `ctrl entangle(q[0], q[1], q[2])`. Where are the control qubits?
        *   Let's re-read the isQ syntax reference: "Control modifier: `ctrl @[c1, c2] Gate(target);`".
        *   Wait, the prompt's code is `ctrl entangle(q[0], q[1], q[2])`. But `entangle` takes two parameters: `procedure entangle(qbit a, qbit b)`. The call has 3 parameters? No, wait! Look at the prompt:
            `ctrl entangle(q[0], q[1], q[2]);` - Wait, `entangle` takes `qbit a, qbit b`.
            Wait, in isQ `ctrl` applies to the *first* argument implicitly if `@` is not provided, or maybe it's `ctrl entangle(q[1], q[2])` but `q[0]` is the control?
            Let me look at the code again: `ctrl entangle(q[0], q[1], q[2]);`. This is a syntax error in standard isQ unless `entangle` takes 3 arguments. Wait, no!
            Wait, if `entangle(a, b)` takes 2 arguments, `ctrl entangle(q[0], q[1], q[2])` has 3. Is this a typo in the prompt's provided code, or does isQ allow `ctrl @[q0] entangle(q1, q2)` implicitly by passing it as a first argument?
            Actually, in isQ, `ctrl` can be a modifier: `ctrl @[q[0]] entangle(q[1], q[2]);` is standard.
            But the prompt says `ctrl entangle(q[0], q[1], q[2])`. If `entangle(a, b)` has 2 parameters, passing 3 to it makes the first one the control qubit!
            Yes, in isQ, `ctrl Gate(controls, targets)` is a shorthand where the control qubits are passed as the first $N$ arguments to the gate, and the rest are targets.
            So `ctrl entangle(q[0], q[1], q[2])` means control on `q[0]`, target on `q[1], q[2]`. Wait, `entangle` takes `a` and `b`. If `q[0]` is control, the targets are `q[1]` and `q[2]`. But `entangle` only takes 2 targets! So `q[1]` is `a` and `q[2]` is `b`.
            Let's verify this interpretation. If `q[0]` is control, `q[1]` is `a`, `q[2]` is `b`.
            So `ctrl entangle(q[1], q[2])` controlled by `q[0]`.
            If `q[0]` is $|1\rangle$, apply `H(q[1])` then `CNOT(q[1], q[2])`.
            State starts as $|100\rangle$.
            Control `q[0]` is $|1\rangle$, so `H` is applied to `q[1]`, `CNOT(q[1], q[2])` is applied.
            $|100\rangle \xrightarrow{cH[1]} |1\rangle \otimes (H|0\rangle) \otimes |0\rangle = |1\rangle \otimes |+\rangle \otimes |0\rangle = \frac{1}{\sqrt{2}}(|

### Reference answer

{'predicted_probs': {'000': 0.5, '011': 0.5}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|000>) = 0.5000, P(|011>) = 0.5000.'}

## isqTrain/225

- task_id: `isqTrain/225`
- task_type: `code_generation`
- category: `isq_deriving`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `5520`

### Prompt

I need an isQ program to implements the gate_decomposition pattern but with a different initial state preparation (flip q[[0]] -> q[2]).

### Chain-of-thought reasoning

Let me analyze this isQ quantum program step by step.

The program has:
1. A procedure `entangle(a, b)` that applies H(a) then CNOT(a, b)
2. 3 qubits: q[0], q[1], q[2]
3. Main circuit:
   - X(q[2]) - flips qubit 2
   - ctrl entangle(q[0], q[1], q[2]) - controlled version of entangle with q[2] as control
   - Measures all three qubits

Let me trace the state evolution:

Initial state: |000⟩

After X(q[2]): |001⟩

Now, `ctrl entangle(q[0], q[1], q[2])` means we apply the entangle gate controlled by q[2].

The `ctrl` modifier with 3 qubits passed means q[2] is the control qubit, and the entangle operation applies to q[0] and q[1] only when q[2] is |1⟩.

Since q[2] is in state |1⟩, the entangle gate WILL be applied to q[0] and q[1].

entangle does:
1. H(q[0]): transforms |0⟩ to |+⟩ = (|0⟩ + |1⟩)/√2
2. CNOT(q[0], q[1]): creates Bell state

So after H(q[0]): (|0⟩ + |1⟩)/√2 ⊗ |0⟩ ⊗ |1⟩ = (|001⟩ + |101⟩)/√2

After CNOT(q[0], q[1]): (|001⟩ + |111⟩)/√2

Wait, but the expected measurement probability is {|001⟩: 1.0}

Hmm, let me reconsider. The predicted output {|001⟩: 1.0} meaning we should always measure |001⟩.

Let me re-read the code. The `ctrl` modifier... In isQ, when we have `ctrl entangle(q[0], q[1], q[2])`, the last qubit mentioned becomes the control.

Actually, looking at isQ syntax: `ctrl @[c1, c2] Gate(target);` - the control qubits are specified with @.

But in the code: `ctrl entangle(q[0], q[1], q[2]);`

This syntax might mean q[2] is the control and q[0], q[1] are the targets of the entangle procedure.

So the entangle procedure applies H(a) then CNOT(a, b) where a=q[0] and b=q[1], but only when q[2]=|1⟩.

After X(q[2]): |001⟩

Since q[2]=|1⟩, entangle is applied:
- H(q[0]): |001⟩ → (|001⟩ + |101⟩)/√2
- CNOT(q[0], q[1]): (|001⟩ + |111⟩)/√2

This gives a Bell-like state, not |001⟩ with probability 1.

But The predicted output {|001⟩: 1.0}... Let me reconsider.

Wait, maybe I'm misreading the control syntax. Perhaps the first parameter becomes the control?

Or maybe the syntax `ctrl entangle(q[0], q[1], q[2])` means:
- The entangle procedure takes 2 qubits
- When using ctrl, the first one becomes the control for the whole procedure
- So q[0] is the control, q[1] and q[2] are the targets

Hmm, but entangle only takes 2 parameters, so this interpretation doesn't work directly.

Actually, looking more carefully at isQ syntax: `ctrl @[c1, c2] Gate(target);`

The code doesn't use @ syntax. Let me think about this differently.

When you call `ctrl entangle(q[0], q[1], q[2])`, maybe q[2] is added as an additional control qubit, and q[0], q[1] are passed to the entangle procedure.

So it's a Toffoli-like control where the entangle operation on (q[0], q[1]) is controlled by q[2].

Given q[2] starts in |1⟩ after X(q[2]), the entangle operation should be applied.

Unless... the control is on q[0] and the entangle applies to q[1] and q[2]?

Let me reconsider the state evolution more carefully.

Actually wait - if The predicted output |001⟩ with probability 1, that means nothing happens to the state after X(q[2]).

Oh! Maybe the control is that q[0] controls the entangle operation on (q[1], q[2])

## isqTrain/222

- task_id: `isqTrain/222`
- task_type: `output_prediction`
- category: `isq_deriving`
- difficulty: `basic`
- concept_tags: `entanglement`, `isq_syntax_deriving_gate`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `1001`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;

procedure my_circuit(qbit a, qbit b) {
    H(a);
    CNOT(a, b);
} deriving gate

qbit q[2];

procedure main() {
    my_circuit(q[0], q[1]);
    inv my_circuit(q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The initial state of the 2-qubit system is |00>. The circuit applies a custom gate `my_circuit` followed immediately by its inverse, `inv my_circuit`.
2. `my_circuit` applies an H gate to `q[0]`, evolving the state to (|00> + |10>)/√2, followed by a CNOT with `q[0]` as control and `q[1]` as target, creating the Bell state (|00> + |11>)/√2.
3. The `inv` modifier executes the exact reverse of the gate sequence (applying CNOT then H), perfectly undoing the transformations.
4. The system returns to its initial state |00> just before measurement.
Predicted probability distribution: {|00>: 1.0}

### Reference answer

{'predicted_probs': {'0': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/77. Dimension: predict probabilities for reference circuit.'}

## isqTrain/1640

- task_id: `isqTrain/1640`
- task_type: `code_generation`
- category: `isq_deriving`
- difficulty: `basic`
- concept_tags: `isq_syntax_deriving_gate`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `441`

### Prompt

I need an isQ program to Define a custom gate equivalent to H using `deriving gate`, apply to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
The goal is to define a custom Hadamard gate using `deriving gate`, apply it to an initial |0> state, and measure the outcome.
One qubit is needed, and it is measured at the end of the circuit.
Starting in state |0>, applying the `custom_h` gate evolves the state to H|0> = |+> = (1/√2)|0> + (1/√2)|1>.
The squared amplitudes of the final superposition yield equal measurement probabilities, resulting in P(|0>) = 0.5 and P(|1>) = 0.5.

## isqTrain/2539

- task_id: `isqTrain/2539`
- task_type: `code_equivalence`
- category: `isq_deriving`
- difficulty: `basic`
- concept_tags: `entanglement`, `global_phase`, `isq_syntax_deriving_gate`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `4304`

### Prompt

Will these two quantum programs produce identical measurement outcomes?

```isq
import std;

procedure my_circuit(qbit a, qbit b) {
    H(a);
    CNOT(a, b);
} deriving gate

qbit q[2];

procedure main() {
    my_circuit(q[0], q[1]);
    inv my_circuit(q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

vs.

```isq
import std;

procedure my_circuit(qbit a, qbit b) {
    H(a);
    CNOT(a, b);
} deriving gate

qbit q[2];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    my_circuit(q[0], q[1]);
    inv my_circuit(q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** applies a unitary operation (`my_circuit`) to the initial state |00>, transforming it into a Bell state, and then immediately applies its inverse (`inv my_circuit`), returning the state exactly to |00>.
2. **Program B** applies the exact same sequence of operations as Program A, but prefixes it with the `GPhase(0.0)` gate.
3. The key difference between the two is the inclusion of `GPhase(0.0)` in Program B, which mathematically multiplies the state by $e^{i \cdot 0} = 1$.
4. The measurement probabilities are identical because a global phase of 0.0 is mathematically trivial and leaves the quantum state entirely unchanged. Both programs guarantee a final state of |00>.
5. Equivalent: True

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/229

- task_id: `isqTrain/229`
- task_type: `code_generation`
- category: `isq_deriving`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `3408`

### Prompt

帮我写一个isQ程序：implements a variant of the gate_decomposition pattern using q[4] -> q[5]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Implement a multi-controlled Z gate variant across an expanded 5-qubit register.

**Qubits & Measurement:** 5 qubits (q[0]-q[4]) declared globally; all 5 are measured.

**State Evolution:**
1. Initialize to |00000⟩
2. X(q[0]), X(q[1]), X(q[2]) → flips first three qubits → |11100⟩
3. `ctrl<3> my_z(q[0], q[1], q[2], q[3])` applies Z to q[3] when all three controls (q[0],q[1],q[2]) are |1⟩; since q[3]=|0⟩, Z|0⟩=|0⟩, so state remains |11100⟩
4. q[4] is untouched, staying at |0⟩

**Expected Probabilities:** Final state |11100⟩ is a computational basis state, so measurement yields |11100⟩ with probability 1.0.
