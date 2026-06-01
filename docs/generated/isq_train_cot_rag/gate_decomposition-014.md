# ISQ training COT RAG corpus: gate_decomposition shard 14

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3356

- task_id: `isqTrain/3356`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `3329`

### Prompt

Write isQ code for the following quantum task: an isQ program: prepare |01>, apply CNOT-H0, measure both qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Prepare |01>, apply CNOT then H on qubit 0, and measure both qubits.
Two qubits q[0], q[1] are needed; both are measured.

State evolution:
1. Start: |00⟩
2. X(q[1]): |01⟩
3. CNOT(q[0], q[1]): control q[0]=|0⟩ → no flip → |01⟩
4. H(q[0]): |0⟩→(|0⟩+|1⟩)/√2 on q[0], q[1] unchanged → (|01⟩+|11⟩)/√2

Final state (|01⟩+|11⟩)/√2 yields equal probability 0.5 for |01⟩ and |11⟩ upon measurement.

## isqTrain/3346

- task_id: `isqTrain/3346`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `1509`

### Prompt

Write an isQ program that an isQ program: apply 2-qubit gate chain CNOT-CZ to |00> and measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply a CNOT-CZ gate chain to the |00> state and measure both qubits.
2. **Qubits**: 2 qubits required (q[0], q[1]), both are measured.
3. **State evolution**:
   - Initial state: |00>
   - CNOT(q[0], q[1]): Control q[0] is |0>, so target q[1] is unchanged → |00>
   - CZ(q[0], q[1]): Control q[0] is |0>, so no Z applied to q[1] → |00>
4. **Expected probabilities**: Both gates only act when the control is |1>. Since q[0] remains |0>, the state is unchanged. Measurement yields |00> with probability 1.0.

## isqTrain/3291

- task_id: `isqTrain/3291`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4284`

### Prompt

Write isQ code for the following quantum task: an isQ program: apply H, Rz(1*pi/6), Rz(-1*pi/6), H. Since Rz cancels, net is H*H=I.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Demonstrate Rz(π/6) and Rz(-π/6) cancellation sandwiched between H gates, yielding identity.
2. One qubit `q[0]` is used and measured.
3. State evolution: |0⟩ →H (|0⟩+|1⟩)/√2 →Rz(π/6) (e^{-iπ/12}|0⟩+e^{iπ/12}|1⟩)/√2 →Rz(-π/6) (|0⟩+|1⟩)/√2 = |+⟩ →H |0⟩. The two Rz rotations cancel exactly since their angles sum to zero.
4. Final state is |0⟩, so measurement yields |0⟩ with probability 1.0.

## isqTrain/3255

- task_id: `isqTrain/3255`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1092`

### Prompt

Write isQ code for the following quantum task: an isQ program: apply X twice to each of 2 qubits (X*X=I), then measure. All qubits should remain |0>.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply X twice to each of 2 qubits (X²=I), verifying all qubits return to |0⟩.
2. Qubits: 2 (q[0], q[1]), both measured.
3. Evolution:
   - Start: |00⟩
   - X(q[0]): |10⟩
   - X(q[0]): |00⟩ (X²=I restores q[0])
   - X(q[1]): |01⟩
   - X(q[1]): |00⟩ (X²=I restores q[1])
4. Final state |00⟩ yields measurement probability P(|00⟩)=1.0.

## isqTrain/3343

- task_id: `isqTrain/3343`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2495`

### Prompt

I need an isQ program to an isQ program: apply gate chain H-T-S-X to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply the gate sequence H-T-S-X to a single qubit initialized to |0⟩, then measure.
One qubit is needed (q[0]) and measured.

State evolution:
1. Initial: |0⟩
2. H: |0⟩ → |+⟩ = (|0⟩+|1⟩)/√2
3. T: → (|0⟩ + e^(iπ/4)|1⟩)/√2
4. S: → (|0⟩ + e^(i3π/4)|1⟩)/√2
5. X: → (e^(i3π/4)|0⟩ + |1⟩)/√2

The measurement probabilities are {|0⟩: 0.5, |1⟩: 0.5} since both coefficients have magnitude 1/√2.

## isqTrain/4405

- task_id: `isqTrain/4405`
- task_type: `output_prediction`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `global_phase`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4085`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[2];

procedure crz_gate(double theta, qbit c, qbit t) {
    Rz(theta/2.0, t);
    CNOT(c, t);
    Rz(-theta/2.0, t);
    CNOT(c, t);
}

procedure main() {
    // Prepare |11> state
    X(q[0]);
    X(q[1]);
    // Apply controlled-Rz(pi) gate
    crz_gate(pi, q[0], q[1]);
    // Measure both qubits
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The objective is to provide a step-by-step quantum state analysis of the given isQ program and predict the final measurement probability distribution.

2.  **Analyze the isQ Code**:
    *   Initialize `q[2]` to `|00>`.
    *   `X(q[0]); X(q[1]);` -> State becomes `|11>`.
    *   Apply `crz_gate(pi, q[0], q[1]);`
        *   Wait, the prompt has a bug in my normal expectation or I should just trace it exactly. Let's trace `crz_gate(pi, q[0], q[1])`.
        *   Rz(pi/2.0, q[1]) -> `|1>` gets phase `e^{i*pi/2} = i`. State: `i|11>`
        *   CNOT(q[0], q[1]) -> Target q[1] is 1, control q[0] is 1. Target flips to 0. State: `i|10>`
        *   Rz(-pi/2.0, q[1]) -> `|0>` gets phase `1` (since Rz acts on |1>). Wait, target is now `|0>`. Rz(-pi/2) on `|0>` doesn't change it? Let's check Rz matrix: `diag(1, e^{-i\theta/2})` (Wait, standard Rz is `diag(e^{-i\theta/2}, e^{i\theta/2})`. Actually, let's just use standard phase shifts). If Rz adds a phase to |1>, and q[1] is |0>, it does nothing. State remains `i|10>`.
        *   CNOT(q[0], q[1]) -> Target q[1] is 0, control is 1. Target flips to 1. State: `i|11>`.
        *   Wait! Is `crz_gate` implemented correctly for a controlled-Rz? Let's trace carefully.
        *   Standard CRz:
            *   |00> -> |00>
            *   |01> -> |01>
            *   |10> -> |10>
            *   |11> -> e^{i\theta} |11>
        *   Let's check the code's implementation:
            *   `Rz(theta/2, t)` -> |11> -> e^{i*pi/2} |11> = i|11>
            *   `CNOT(c, t)` -> |11> -> |10>
            *   `Rz(-theta/2, t)` -> |10> -> |10> (since t is |0>)
            *   `CNOT(c, t)` -> |10> -> |11>
        *   So it adds `e^{i*pi/2} = i` phase to |11>. This is exactly CRz(pi). State is `i|11>`. Global phase `i`.
    *   `X(q[0]);` -> State becomes `i|01>`.
    *   Measurement: `M(q[0])` and `M(q[1])` are applied to `i|01>`. Measurement probabilities are independent of the global phase `i`.
    *   Result: 100% probability of `|01>`.

3.  **Step-by-Step Dirac Notation**:
    *   Initial state: |00>
    *   After X gates: |11>
    *   Apply crz_gate(pi, q[0], q[1]):
        *   Rz(pi/2, q[1]) -> i|11>
        *   CNOT(q[0], q[1]) -> i|10>
        *   Rz(-pi/2, q[1]) -> i|10> (since q[1] is |0>)
        *   CNOT(q[0], q[1]) -> i|11>
    *   Apply X(q[0]): i|01>
    *   Measurement: 100% |01>

4.  **Format Requirements**:
    *   Use Dirac notation.
    *   Start with "## Circuit Analysis".
    *   End with predicted probability distribution.
    *   3-8 lines.
    *   no code blocks.

5.  **Drafting the Output**:
    ## Circuit Analysis
    - Initial state: |00>
    - Apply X gates to both qubits: |11>
    - Apply `crz_gate(pi, q[0], q[1])`: Rz(pi/2) on q[1] gives i|11>. CNOT flips q[1] to |0> (i|10>). Rz(-pi/2

### Reference answer

{'predicted_probs': {'01': 1.0}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|01>) = 1.0000.'}

## isqTrain/3135

- task_id: `isqTrain/3135`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4131`

### Prompt

Implement the following in isQ: an isQ program: apply gate chain HXH to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply gate chain HXH to a single |0⟩ qubit and measure.
2. **Qubits**: 1 qubit needed, measured at end.
3. **State evolution**:
   - |0⟩ → H → |+⟩ = (|0⟩ + |1⟩)/√2
   - |+⟩ → X → |+⟩ (X swaps |0⟩↔|1⟩, leaving |+⟩ invariant)
   - |+⟩ → H → |0⟩ (H is self-inverse: H|+⟩ = HH|0⟩ = |0⟩)
4. **Result**: Final state is |0⟩, so measurement yields |0⟩ with probability 1.0.

## isqTrain/0

- task_id: `isqTrain/0`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `1996`

### Prompt

Write an isQ program that implements a variant of the gate_decomposition pattern using q[2] -> q[3]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

The user wants me to write a reasoning section for an isQ program that implements a variant of the gate_decomposition pattern using q[2] -> q[3]. The circuit should use an expanded qubit register.

Analyzing the circuit requirements, it uses 3 qubits, applies an X gate to q[1], then applies a swap gate between q[0] and q[1], and measures all three qubits.

The expected measurement probabilities are {|100>: 1.0}, meaning we should get state |100> with certainty.

Let me trace through:
1. Initial state: |000>
2. X(q[1]): |010>
3. swap_gate(q[0], q[1]):
   - CNOT(q[0], q[1]): |010> → |010> (control q[0] is 0, target unchanged)
   - CNOT(q[1], q[0]): |010> → |110> (control q[1] is 1, flips q[0])
   - CNOT(q[0], q[1]): |110> → |100> (control q[0] is 1, flips q[1])
4. Final state: |100>

Wait, but the task says "using q[2] -> q[3]" which suggests a swap between q[2] and q[3]. This means we need at least 4 qubits.

Let me re-read the task. It says "implements a variant of the gate_decomposition pattern using q[2] -> q[3]". So we need to adapt The implementation to use qubits 2 and 3 instead of 0 and 1.

For the expanded qubit register, I'll use 4 qubits. The variant would:
- Apply X to one of the qubits (let's say q[3])
- Apply swap_gate between q[2] and q[3]
- Measure all qubits

Let me trace this:
1. Initial state: |0000>
2. X(q[3]): |0001>
3. swap_gate(q[2], q[3]):
   - CNOT(q[2], q[3]): |0001> → |0001> (control q[2] is 0, target unchanged)
   - CNOT(q[3], q[2]): |0001> → |0011> (control q[3] is 1, flips q[2])
   - CNOT(q[2], q[3]): |0011> → |0010> (control q[2] is 1, flips q[3])
4. Final state: |0010>

Wait, I need to be careful about the bit ordering. In isQ, the bitstring representation typically has the first measured qubit as the highest bit.

If we measure M(q[0]); M(q[1]); M(q[2]); M(q[3]);, the output would be indexed by the bitstring where q[0] is the highest bit.

So if the final state is |0010> in the computational basis (q[3]q[2]q[1]q[0] order), the measurement bitstring would be...

Actually, I need to think about this more carefully. In quantum computing, the standard convention is:
- |q[0]q[1]q[2]q[3]>
- So |0001> means q[3]=1 and all others are 0

Let me re-trace:
1. Initial state: |0000> (all qubits in |0>)
2. X(q[3]): |0001> (q[3] is now |1>)
3. swap_gate(q[2], q[3]):
   - CNOT(q[2], q[3]): control q[2]=0, target q[3]=1, so no change: |0001>
   - CNOT(q[3], q[2]): control q[3]=1, target q[2]=0, so flip q[2]: |0011>
   - CNOT(q[2], q[3]): control q[2]=1, target q[3]=1, so flip q[3]: |0010>
4. Final state: |0010>

For the measurement bitstring in --probs mode, "earlier measured qubit = higher bit", so if we measure M(q[0]); M(q[1]); M(q[2]); M(q[3]);, the bitstring would be:
- q[0] = 0 (bit 3)
- q[1] = 0 (bit 2)
- q[2] = 1 (bit 1)
- q[3] = 0 (bit 0)

So the bitstring is 0010 in binary = 2 in decimal.

Wait

## isqTrain/3339

- task_id: `isqTrain/3339`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3264`

### Prompt

用isQ实现an isQ program: apply gate chain H-S-X to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply H-S-X gate chain to |0⟩ and measure the result.
One qubit is needed and measured.
Evolution: |0⟩ → H → |+⟩ = (|0⟩+|1⟩)/√2 → S → (|0⟩+i|1⟩)/√2 → X → (|1⟩+i|0⟩)/√2 = (i|0⟩+|1⟩)/√2.
Probabilities: P(0) = |i/√2|² = 0.5, P(1) = |1/√2|² = 0.5.

## isqTrain/675

- task_id: `isqTrain/675`
- task_type: `output_prediction`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2507`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;

qbit q[1];

procedure main() {
    Z(q[0]);
    Y(q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes a single qubit, q[0], in the state |0>.
2. The Z gate is applied to the qubit, leaving the state unchanged: Z|0> = |0>.
3. The Y gate is then applied to the qubit: Y|0> = -i|1>.
4. Since global phases do not affect measurement outcomes, the final quantum state is equivalent to |1>.
5. Therefore, a measurement of the qubit will deterministically yield the state |1>.

Predicted probability distribution: {|1>: 1.0}

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/221. Dimension: predict probabilities for reference circuit.'}
