# ISQ training COT RAG corpus: circuit_basics shard 15

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4652

- task_id: `isqTrain/4652`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `superposition`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `21`

### Prompt

Compare these two isQ programs. Do they give the same probability distribution?

First program:
```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    Z(q[0]);
    H(q[0]);
    M(q[0]);
}

```

Second program:
```isq
import std;
qbit q[1];

procedure main() {
    X(q[0]);
    H(q[0]); // add superposition
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis

1. **Program A**: Applies H → Z → H to |0⟩. This sequence equals HZH = X, so the final state is X|0⟩ = |1⟩, yielding P(1) = 1.

2. **Program B**: Applies X → H to |0⟩. First X|0⟩ = |1⟩, then H|1⟩ = |−⟩ = (|0⟩ − |1⟩)/√2, yielding P(0) = 0.5, P(1) = 0.5.

3. **Key difference**: Program A collapses to a deterministic |1⟩ outcome, while Program B produces an equal superposition |−⟩ with 50/50 measurement probabilities.

4. **Measurement probabilities differ**: Program A gives P(1)=1; Program B gives P(0)=0.5, P(1)=0.5.

**Verdict: Not equivalent (No)**

### Reference answer

{'equivalent': False, 'explanation': 'After adding H gate to Program B, the programs produce different probability distributions.', 'probs_a': {'1': 1.0}, 'probs_b': {'0': 0.5, '1': 0.5}}

## isqTrain/1619

- task_id: `isqTrain/1619`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3125`

### Prompt

Help me write isQ code that Apply SWAP(q[0],q[1]) twice (identity) on 3 qubits with q[0]=|1>. Measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Initialize qubit 0 to |1> and apply a double swap (three-CNOT decomposition) (which acts as an identity) to qubits 0 and 1, then measure all.
2. **Qubits**: 3 qubits are used, and all are measured.
3. **State Evolution**:
   - **Initial state**: |000⟩
   - **X(q[0])**: Flips the first qubit to |1⟩, resulting in |100⟩.
   - **swap (three-CNOT decomposition)(q[0], q[1])**: Exchanges the states of q[0] and q[1], changing the state to |010⟩.
   - **swap (three-CNOT decomposition)(q[0], q[1])**: Exchanges them back, returning the system to the state |100⟩.
4. **Expected Probabilities**: Since the double swap (three-CNOT decomposition) acts as an identity and leaves the |100⟩ state unchanged, measurement yields the bitstring '100' with a probability of 1.0.

## isqTrain/673

- task_id: `isqTrain/673`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `global_phase`, `superposition`
- source: `isq_train_cot`
- dataset_index: `401`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;

qbit q[1];

procedure main() {
    H(q[0]);
    GPhase(1.57079632679);
    H(q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes in the state |0>.
2. The first `H(q[0])` puts the qubit into an equal superposition: |+> = (1/√2)|0> + (1/√2)|1>.
3. `GPhase

### Reference answer

{'predicted_probs': {'0': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/220. Dimension: predict probabilities for reference circuit.'}

## isqTrain/1654

- task_id: `isqTrain/1654`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `402`

### Prompt

请用isQ语言编写一个量子电路：Apply Rx(pi/2) to a qubit in state |0> and measure.

### Chain-of-thought reasoning

## Reasoning
The goal is to apply an Rx(π/2) rotation to a single qubit initially in the |0> state and measure the resulting state.
The circuit requires exactly 1 qubit, which is measured at the end.
Starting in the |0> state, applying Rx(π/2) rotates the qubit around the X-axis by π/2, evolving the state to (1/√2)|0> - (i/√2)|1>.
Because the probability amplitudes for both |0> and |1> have a magnitude of 1/√2, the expected measurement outcome probabilities are both |1/√2|² = 0.5.

## isqTrain/4757

- task_id: `isqTrain/4757`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `1565`

### Prompt

Will these two quantum programs produce identical measurement outcomes?

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

vs.

```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    Rz(pi/2.0, q[0]);
    H(q[0]);
    H(q[0]); // add superposition
    M(q[0]);
}

```

### Chain-of-thought reasoning

Let me analyze both programs.

**Program A:**
1. Start with |0>
2. H(q[0]): |+> = (|0> + |1>)/√2
3. Rz(π/4, q[0]): This applies a phase rotation. Rz(θ) = [[e^(-iθ/2), 0], [0, e^(iθ/2)]]
   After Rz(π/4): (e^(-iπ/8)|0> + e^(iπ/8)|1>)/√2
4. H(q[0]): Apply H again
   H * Rz(π/4) * H on |0>

Let me compute this more carefully.

H * Rz(θ) * H:
H = (1/√2)[[1,1],[1,-1]]
Rz(θ) = [[e^(-iθ/2),0],[0,e^(iθ/2)]]

H * Rz(θ) * H = (1/2)[[1,1],[1,-1]] * [[e^(-iθ/2),0],[0,e^(iθ/2)]] * [[1,1],[1,-1]]

First: Rz(θ) * H = (1/√2)[[e^(-iθ/2), e^(-iθ/2)],[e^(iθ/2), -e^(iθ/2)]]

Then H * (Rz(θ) * H) = (1/2)[[e^(-iθ/2)+e^(iθ/2), e^(-iθ/2)-e^(iθ/2)],[e^(-iθ/2)-e^(iθ/2), e^(-iθ/2)+e^(iθ/2)]]
= (1/2)[[2cos(θ/2), -2i·sin(θ/2)],[-2i·sin(θ/2), 2cos(θ/2)]]
= [[cos(θ/2), -i·sin(θ/2)],[-i·sin(θ/2), cos(θ/2)]]

For θ = π/4:
cos(π/8) ≈ 0.9239
sin(π/8) ≈ 0.3827

So Program A applies: [[cos(π/8), -i·sin(π/8)],[-i·sin(π/8), cos(π/8)]]

This is like Rx(π/4) but with a global phase difference. Rx(θ) = [[cos(θ/2), -i·sin(θ/2)],[-i·sin(θ/2), cos(θ/2)]]

So Program A: H * Rz(π/4) * H = Rx(π/4)

Applied to |0>: cos(π/8)|0> - i·sin(π/8)|1>

P(0) = cos²(π/8) ≈ 0.8536
P(1) = sin²(π/8) ≈ 0.1464

**Program B:**
1. H(q[0]): |+>
2. Rz(π/2, q[0])
3. H(q[0])
4. H(q[0]) = I (since H*H = I)

So Program B: H * Rz(π/2) * H * H = H * Rz(π/2) * I = H * Rz(π/2)

Wait, H * H = I, so the last H just cancels the previous H.

Program B = H * Rz(π/2) * H * H = H * Rz(π/2) * I = H * Rz(π/2)

Hmm, let me re-read. The operations are applied sequentially:
Start with |0>
After H: |+>
After Rz(π/2): (e^(-iπ/4)|0> + e^(iπ/4)|1>)/√2
After H: Apply H to the state above
After H again: Apply H again (which cancels the previous H)

So the net effect is: H * Rz(π/2) applied to |0>

Wait no. Let me be more careful.

State after step 1 (H): |+>
State after step 2 (Rz(π/2)): Rz(π/2)|+> = (e^(-iπ/4)|0> + e^(iπ/4)|1>)/√2
State after step 3 (H): H * Rz(π/2)|+>
State

### Reference answer

{'equivalent': False, 'explanation': 'After adding H gate to Program B, the programs produce different probability distributions.', 'probs_a': {'0': 0.853553, '1': 0.146447}, 'probs_b': {'0': 0.5, '1': 0.5}}

## isqTrain/1828

- task_id: `isqTrain/1828`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `1910`

### Prompt

请用isQ语言编写一个量子电路：Apply Hadamard gate 5 times to |0> and measure. H^5 = H.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply the Hadamard gate five times to a single qubit initialized in the |0> state.
2. **Qubits**: 1 qubit is required and measured.
3. **State Evolution**:
   - Start with the initial state |0>.
   - The Hadamard gate is its own inverse (H * H = I), meaning applying it twice returns the qubit to its original state.
   - Applying H five times (H^5) is equivalent to applying H four times (which is Identity) followed by H once: H^5 = I * H = H.
   - |0> ->(H)-> |+> ->(H)-> |0> ->(H)-> |+> ->(H)-> |0> ->(H)-> |+>.
   - The final quantum state is |+> = (1/√2)|0> + (1/√2)|1>.
4. **Probabilities**: Measuring the |+> state in the computational basis yields a 50% probability for |0> and a 50% probability for |1>.

## isqTrain/1610

- task_id: `isqTrain/1610`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `data_encoding_qml`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4936`

### Prompt

Write isQ code for the following quantum task: Apply Ry(pi*8/8) to each of 2 qubits and measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Apply an $R_y(\pi)$ rotation to 2 qubits initialized to $|0\rangle$ and measure them.
2. **Qubits:** 2 qubits are required, and both are measured.
3. **State Evolution:**
   - Initial state: $|00\rangle$
   - $R_y(\theta)|0\rangle = \cos(\theta/2)|0\rangle + \sin(\theta/2)|1\rangle$. For $\theta = \pi$, this becomes exactly $|1\rangle$.
   - Applying $R_y(\pi)$ to both qubits maps the state $|00\rangle \to |11\rangle$.
4. **Probabilities:** The final quantum state is exactly $|11\rangle$ (ignoring global phase), so measurement yields the bitstring 11 (index 3) with 100% probability.

## isqTrain/1411

- task_id: `isqTrain/1411`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2127`

### Prompt

Implement a quantum circuit in isQ: Demonstrate phase kickback: prepare control in |+> and target in |1>, apply CZ, then H on control to reveal the phase. Measure control.

### Chain-of-thought reasoning

## Reasoning
Goal: Demonstrate phase kickback by applying CZ to |+⟩|1⟩ and revealing the acquired phase via H on the control.
Two qubits needed (q[0] control, q[1] target); only q[0] is measured.
Step-by-step: |00⟩ →(X on q[1])→ |01⟩ →(H on q[0])→ (|0⟩+|1⟩)|1⟩/√2 = (|01⟩+|11⟩)/√2.
After CZ: CZ(|01⟩+|11⟩)/√2 = (|01⟩-|11⟩)/√2 = |−⟩|1⟩ where |−⟩=(|0⟩-|1⟩)/√2.
After H on q[0]: H|−⟩=|1⟩, so state becomes |1⟩|1⟩.
Measuring q[0] yields |1⟩ with probability 1.0, confirming the phase kickback from target to control.

## isqTrain/1826

- task_id: `isqTrain/1826`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2274`

### Prompt

Help me write isQ code that Apply Ry(pi*4/4) to q[0], then CNOT(q[0], q[1]). Measure both.

### Chain-of-thought reasoning

## Reasoning
- Goal: Apply an Ry rotation of $\pi$ to the first qubit, entangle it with the second via CNOT, and measure both.
- Qubits: 2 qubits (`q[0]`, `q[1]`), both measured.
- State evolution:
  1. Start in |00⟩.
  2. Apply Ry(π, q[0]): Rotates |0⟩ to |1⟩, yielding the state |10⟩.
  3. Apply CNOT(q[0], q[1]): Control q[0] is |1⟩, so target q[1] is flipped, resulting in the final state |11⟩.
- Probabilities: The final state is deterministically |11⟩, meaning the measurement will yield 11 with 100% probability.

## isqTrain/4672

- task_id: `isqTrain/4672`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `5689`

### Prompt

这两个isQ程序是等价的吗？

程序A：
```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    H(q[0]);
    M(q[0]);
}

```

程序B：
```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]); // add superposition
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A**: Applies a Hadamard gate (H) to qubit q[0] twice, followed by a measurement. Since H is its own inverse (H*H = I), the two H gates cancel each other out.
2. **Program B**: Applies a single Hadamard gate to qubit q[0], putting it into superposition, followed by a measurement.
3. **Key difference**: Program A leaves the qubit in its initial computational basis state |0>, whereas Program B leaves the qubit in the superposition state |+> = (1/sqrt(2))(|0> + |1>).
4. **Probability distribution**: The measurement in Program A yields |0> with 100% probability. The measurement in Program B yields |0> with 50% probability and |1> with 50% probability.
5. **Verdict**: Not equivalent

### Reference answer

{'equivalent': False, 'explanation': 'After adding H gate to Program B, the programs produce different probability distributions.', 'probs_a': {'0': 1.0}, 'probs_b': {'0': 0.5, '1': 0.5}}
