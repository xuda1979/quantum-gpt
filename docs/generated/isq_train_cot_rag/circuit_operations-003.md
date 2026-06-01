# ISQ training COT RAG corpus: circuit_operations shard 3

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4410

- task_id: `isqTrain/4410`
- task_type: `output_prediction`
- category: `circuit_operations`
- difficulty: `basic`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `5363`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[3];

procedure main() {
    // Flip first qubit to |1>
    X(q[0]);
    // Propagate via CNOT to create |111>
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);
    // Measure all qubits
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initial State:** The 3-qubit system begins in the ground state |000⟩.
2. **Gate X(q[0]):** Flips the first qubit from |0⟩ to |1⟩. The state becomes |100⟩.

### Reference answer

{'predicted_probs': {'011': 1.0}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|011>) = 1.0000.'}

## isqTrain/2486

- task_id: `isqTrain/2486`
- task_type: `code_equivalence`
- category: `circuit_operations`
- difficulty: `basic`
- concept_tags: `global_phase`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1655`

### Prompt

Compare these two isQ programs. Do they give the same probability distribution?

First program:
```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    M(q[0]);
}

```

Second program:
```isq
import std;
qbit q[1];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    H(q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** initializes q[0] to |0> and applies a Hadamard (H) gate, transforming the state to |+> = (|0> + |1>)/√2.
2. **Program B** also initializes to |0>, applies GPhase(0.0) (which multiplies the state by $e^{i0}=1$), and then applies the H gate to reach the exact same |+> state.
3. The key difference is the addition of `GPhase(0.0)` in Program B, which is a trivial identity operation (a global phase of 0).
4. The measurement probabilities are exactly the same (50% for |0> and 50% for |1>) because global phase differences do not affect measurement outcomes, and here the phase is identically zero anyway.
5. Equivalent: True

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/1994

- task_id: `isqTrain/1994`
- task_type: `output_prediction`
- category: `circuit_operations`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1287`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[2];
procedure main() {
    Y(q[0]);
    H(q[1]);
    CZ(q[0], q[1]);
    H(q[1]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initial State:** |00>
2. **Y(q[0]):** Transforms |0

### Reference answer

{'predicted_probs': {'11': 1.0}, 'explanation': 'Expected probabilities: [0.0, 0.0, 0.0, 1.0]'}

## isqTrain/1785

- task_id: `isqTrain/1785`
- task_type: `code_generation`
- category: `circuit_operations`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `1279`

### Prompt

Help me write isQ code that Reverse the qubit order of 3 qubits using SWAP gates. Start with |100>.

### Chain-of-thought reasoning

## Reasoning
Goal: Reverse the order of 3 qubits starting in |100> using a swap operation (three-CNOT decomposition) to exchange the first and last qubits.

Three qubits q[0], q[1], q[2] are used, and all are measured.

State evolution:
1. Initial state: |000>
2. After X(q[0]): |100>
3. After swap (three-CNOT decomposition)(q[0], q[2]): exchanges q[0] and q[2], yielding |001>

The final state is |001>, so measurement yields {|001>: 1.0}.

## isqTrain/1861

- task_id: `isqTrain/1861`
- task_type: `output_prediction`
- category: `circuit_operations`
- difficulty: `basic`
- concept_tags: `basis_change`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `2584`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[1];
procedure main() {
    Ry(pi/4.0, q[0]);
    H(q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the isQ program:**
    *   `qbit q[1];` -> one qubit, initialized to $|0\rangle$.
    *   `Ry(pi/4.0, q[0]);` -> apply $R_y(\pi/4)$ to $q_0$.
    *   `H(q[0]);` -> apply Hadamard to $q_0$.
    *   `M(q[0]);` -> measure $q_0$.

2.  **Step-by-step state evolution:**
    *   Initial state: $|\psi_0\rangle = |0\rangle = \begin{bmatrix} 1 \\ 0 \end{bmatrix}$.
    *   Apply $R_y(\pi/4)$:
        *   $R_y(\theta) = \begin{bmatrix} \cos(\theta/2) & -\sin(\theta/2) \\ \sin(\theta/2) & \cos(\theta/2) \end{bmatrix}$.
        *   For $\theta = \pi/4$, $\cos(\pi/8) = c$, $\sin(\pi/8) = s$.
        *   $|\psi_1\rangle = R_y(\pi/4) |0\rangle = \cos(\pi/8)|0\rangle + \sin(\pi/8)|1\rangle$.
    *   Apply $H$:
        *   $H = \frac{1}{\sqrt{2}} \begin{bmatrix} 1 & 1 \\ 1 & -1 \end{bmatrix}$.
        *   $|\psi_2\rangle = H |\psi_1\rangle = \frac{1}{\sqrt{2}} \begin{bmatrix} 1 & 1 \\ 1 & -1 \end{bmatrix} \begin{bmatrix} \cos(\pi/8) \\ \sin(\pi/8) \end{bmatrix}$
        *   $|\psi_2\rangle = \frac{1}{\sqrt{2}} (\cos(\pi/8) + \sin(\pi/8)) |0\rangle + \frac{1}{\sqrt{2}} (\cos(\pi/8) - \sin(\pi/8)) |1\rangle$.
    *   Let's simplify the amplitudes:
        *   $\cos(\pi/8) = \cos(22.5^\circ)$
        *   $\sin(\pi/8) = \sin(22.5^\circ)$
        *   Amp of $|0\rangle$: $\frac{1}{\sqrt{2}} (\cos(22.5^\circ) + \sin(22.5^\circ)) = \cos(45^\circ - 22.5^\circ) = \cos(22.5^\circ) = \cos(\pi/8)$.
            *   Wait, let's verify: $\cos(A-B) = \cos A \cos B + \sin A \sin B$. Not quite. $\cos(A-B)$ doesn't match $\frac{1}{\sqrt{2}}(\cos B + \sin B)$.
            *   Actually, $\sin(45^\circ + B) = \sin(45^\circ)\cos(B) + \cos(45^\circ)\sin(B) = \frac{1}{\sqrt{2}}(\cos B + \sin B)$.
            *   So Amp of $|0\rangle = \sin(\pi/4 + \pi/8) = \sin(3\pi/8) = \cos(\pi/2 - 3\pi/8) = \cos(\pi/8)$.
        *   Amp of $|1\rangle$: $\frac{1}{\sqrt{2}} (\cos(\pi/8) - \sin(\pi/8)) = \sin(\pi/4 - \pi/8) = \sin(\pi/8)$.
            *   Wait, $\sin(45^\circ - B) = \sin(45^\circ)\cos B - \cos(45^\circ)\sin B = \frac{1}{\sqrt{2}}(\cos B - \sin B)$.
            *   Yes, Amp of $|1\rangle = \sin(\pi/8)$.

    *   Wait, is it $\cos(\pi/8)$ and $\sin(\pi/8)$? Let's check the values.
        *   $P(0) = \cos^2(\pi/8) = \frac{1 + \cos(\pi/4)}{2} = \frac{1 + \sqrt{2}/2}{2} = \frac{2 + \

### Reference answer

{'predicted_probs': {'0': 0.8536, '1': 0.1464}, 'explanation': 'Measuring Ry(pi/4)|0> in X basis. State is cos(pi/8)|0> + sin(pi/8)|1> in Z, which becomes H(state) in X basis.'}

## isqTrain/1743

- task_id: `isqTrain/1743`
- task_type: `code_generation`
- category: `circuit_operations`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `superposition`
- source: `isq_train_cot`
- dataset_index: `581`

### Prompt

Code this in isQ: Apply controlled-H with control qubit in |0>. Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply a controlled-H gate with control qubit in |0⟩ state, then measure both qubits.
2. Two qubits needed (q[0] as control, q[1] as target), both measured.
3. Initial state: |00⟩. The controlled-H applies H to q[1] only when q[0]=|1⟩. Since q[0]=|0⟩, no action occurs, state remains |00⟩.
4. Measuring both qubits yields |00⟩ with probability 1.0.

## isqTrain/1541

- task_id: `isqTrain/1541`
- task_type: `code_generation`
- category: `circuit_operations`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4207`

### Prompt

用isQ实现Apply controlled-Ry(pi) with control qubit in |0>. Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply a controlled-Ry(π) gate with control qubit in |0⟩, then measure both qubits.

**Qubits:** 2 qubits (q[0] as control, q[1] as target), both measured.

**State evolution:**
1. Initial state: |00⟩
2. Apply `ctrl Ry(π)` with q[0] as control, q[1] as target
   - Controlled gates activate only when control is |1⟩
   - Since q[0] = |0⟩, Ry(π) is NOT applied to q[1]
   - State remains |00⟩

**Expected probabilities:** {|00⟩: 1.0}

The control qubit is in |0⟩, so the controlled operation is never triggered and the target qubit remains unchanged in |0⟩.

## isqTrain/4488

- task_id: `isqTrain/4488`
- task_type: `output_prediction`
- category: `circuit_operations`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4482`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    T(q[0]);
    H(q[0]);
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:** The user wants a circuit analysis for an isQ program. The analysis needs to be concise (3-15 lines), use Dirac notation, explain operations, step-by-step state evolution, final state, and probability distribution. Must end with the predicted probabilities.

2.  **Analyze the isQ program:**
    *   `qbit q[1];` (Starts in |0>)
    *   `H(q[0]);` (State: |+> = 1/sqrt(2)|0> + 1/sqrt(2)|1>)
    *   `T(q[0]);` (State: 1/sqrt(2)|0> + e^(i*pi/4)/sqrt(2)|1>)
    *   `H(q[0]); H(q[0]); Z(q[0]); H(q[0]);`
        *   Wait, the comment says `HZH = X`.
        *   Let's trace it: `H` then `H` is `I`. So the sequence `H H Z H` is `I Z H = Z H`.
        *   Let's re-read the code: `H(q[0]); H(q[0]); Z(q[0]); H(q[0]);`
        *   Wait, the code literally says `H(q[0]); H(q[0]); Z(q[0]); H(q[0]);`.
        *   $H H = I$. So $H H Z H = Z H$.
        *   Comment says `HZH = X on qubit 0`. But the code has FOUR gates: `H, H, Z, H`. Is it a typo in the code, or is it evaluated as written?
        *   Let's look at the predicted output: `{|0>: 0.14644660940672616, |1>: 0.8535533905932738}`.
        *   Let's calculate both scenarios.
        *   **Scenario A (HZH = X):** State after T is 1/sqrt(2)|0> + e^{i\pi/4}/sqrt(2)|1>. Apply X: e^{i\pi/4}/sqrt(2)|0> + 1/sqrt(2)|1>. Prob of |0> is 1/2. Prob of |1> is 1/2. Not a match.
        *   **Scenario B (HHZH = ZH):** State after T is 1/sqrt(2)|0> + e^{i\pi/4}/sqrt(2)|1>. Apply Z: 1/sqrt(2)|0> - e^{i\pi/4}/sqrt(2)|1>. Apply H: 1/2(1-e^{i\pi/4})|0> + 1/2(1+e^{i\pi/4})|1>.
            *   Prob of |0>: |1/2(1 - (1+i)/sqrt(2))|^2 = 1/4 * |1 - 1/sqrt(2) - i/sqrt(2)|^2 = 1/4 * ((1 - 1/sqrt(2))^2 + 1/2) = 1/4 * (1 - sqrt(2) + 1/2 + 1/2) = 1/4 * (2 - sqrt(2)) = 1/2 - sqrt(2)/4 ≈ 0.5 - 0.35355 = 0.1464466094. MATCH!
        *   So the code executes exactly as written: `H`, `H`, `Z`, `H`, which equates to `I Z H = Z H`.

3.  **Step-by-step State Evolution:**
    *   Initial: |0>
    *   `H(q[0])`: 1/√2 |0> + 1/√2 |1>
    *   `T(q[0])`: 1/√2 |0> + e^(iπ/4)/√2 |1>
    *   `H(q[0]); H(q[0]); Z(q[0]); H(q[0]);`: As HH=I, this is equivalent to applying Z then H.
    *   Apply Z: 1/√2 |0> - e^(iπ/4)/√2 |1>
    *   Apply H: 1/2(1 - e^(iπ/4))|0> + 1/2(1 + e^(iπ/4))|1>
    *   Since e^(iπ/4) = (1+i)/√2:
        *   Prob(|0>) = |1/

### Reference answer

{'predicted_probs': {'0': 0.146447, '1': 0.853553}, 'explanation': 'This isQ program operates on 1 qubit(s). The measurement probability distribution is: P(|0>) = 0.1464, P(|1>) = 0.8536.'}

## isqTrain/1324

- task_id: `isqTrain/1324`
- task_type: `output_prediction`
- category: `circuit_operations`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `3202`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;
qbit q[2];

procedure main() {
    Ry(pi/2.0, q[0]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes a 2-qubit register in the state |00>.
2. A Ry(pi/2) gate is applied to qubit q[0]. This rotates q[0] from |0> to cos(pi/4)|0> + sin(pi/4)|1> = (1/sqrt(2))|0> + (1/sqrt(2))|1>.
3. Qubit q[1] remains unchanged in the |0> state.
4. The combined state before measurement is (1/sqrt(2))|00> + (1/sqrt(2))|10>.
5. Measuring both qubits collapses the superposition, yielding either |00> or |10> with equal probability.

Predicted probability distribution: {|00>: 0.5, |10>: 0.5}

### Reference answer

{'predicted_probs': {'0': 0.5000000000000001, '2': 0.4999999999999999}, 'explanation': 'Parametric variant of isqEval/476. Dimension: qubit_variant: q[1] -> q[2].'}

## isqTrain/1321

- task_id: `isqTrain/1321`
- task_type: `output_prediction`
- category: `circuit_operations`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `1213`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit q[1];

procedure main() {
    Rx(pi/4.0, q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes a single qubit in the state |0> and applies an Rx rotation gate with an angle of π/4.
2. The Rx(π/4) gate rotates the state around the X-axis of the Bloch sphere, evolving the initial state to cos(π/8)|0> - i*sin(π/8)|1>.
3. The measurement probabilities are determined by taking the square of the amplitudes of the final state.
4. This yields a probability of cos²(π/8) ≈ 0.8536 for the |0> state and sin²(π/8) ≈ 0.1464 for the |1> state.

Predicted probability distribution: {|0>: 0.8535533905932737, |1>: 0.14644660940672624}

### Reference answer

{'predicted_probs': {'0': 0.8535533905932737, '1': 0.14644660940672624}, 'explanation': 'Parametric variant of isqEval/475. Dimension: param_variant: pi2_to_pi4.'}
