# ISQ training COT RAG corpus: gate_decomposition shard 11

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3409

- task_id: `isqTrain/3409`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `3985`

### Prompt

请用isQ语言编写一个量子电路：an isQ program: H, Rz(3*pi/8), H on a qubit. This is equivalent to Rx(3*pi/8).

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply H, Rz(3π/8), H to a single qubit, exploiting the identity H·Rz(θ)·H = Rx(θ) to implement Rx(3π/8).

2. **Qubits**: 1 qubit is allocated and measured.

3. **State evolution**:
   - Initialize: |ψ₀⟩ = |0⟩
   - H gate: |ψ₁⟩ = |+⟩ = (|0⟩ + |1⟩)/√2
   - Rz(3π/8) applies phase e^(-iθ/2) to |0⟩ and e^(iθ/2) to |1⟩: |ψ₂⟩ = (e^(-i3π/16)|0⟩ + e^(i3π/16)|1⟩)/√2
   - H gate: Transforms back, equivalent to Rx(3π/8)|0⟩ = cos(3π/16)|0⟩ - i·sin(3π/16)|1⟩

4. **Probabilities**: P(|0⟩) = cos²(3π/16) ≈ 0.8536... ≈ 0.6913, P(|1⟩) = sin²(3π/16) ≈ 0.3087

## isqTrain/3163

- task_id: `isqTrain/3163`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `2700`

### Prompt

Write isQ code for the following quantum task: an isQ program: apply H, Rz(2*pi/256), H to a qubit and measure. This implements Rx(2*pi/256) via conjugation.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Implement Rx(2π/256) via H-Rz-H conjugation on one qubit, then measure.

**State evolution:**
- |0⟩ → H → |+⟩ = (|0⟩ + |1⟩)/√2
- Rz(2π/256) applies phase e^(i2π/256) to |1⟩: → (|0⟩ + e^(i2π/256)|1⟩)/√2
- H maps back: H·Rz(2π/256)·H = Rx(2π/256), so final state = cos(π/256)|0⟩ − i·sin(π/256)|1⟩

**Probabilities:** P(|0⟩) = cos²(π/256) ≈ 0.9998, P(|1⟩) = sin²(π/256) ≈ 0.0002.

## isqTrain/3171

- task_id: `isqTrain/3171`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_deriving_gate`, `isq_syntax_inv`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `1155`

### Prompt

I need an isQ program to using `deriving gate` to make a procedure invertible. Define a procedure my_rot that applies H then T, with `} deriving gate` after the body. In main, apply my_rot then inv my_rot. Measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Demonstrate `deriving gate` enables automatic inversion of a composite procedure; applying `my_rot` then `inv my_rot` yields the identity.
2. **Qubits**: One qubit `q[0]` is used and measured.
3. **State evolution**:
   - Start: |0⟩
   - `my_rot(q[0])` applies H then T: |0⟩ → |+⟩ → (|0⟩ + e^{iπ/4}|1⟩)/√2
   - `inv my_rot(q[0])` applies T† then H (reverse order, inverse gates): (|0⟩ + e^{iπ/4}|1⟩)/√2 → |+⟩ → |0⟩
4. **Result**: The inverse perfectly undoes the forward operation, returning to |0⟩ with probability 1.0.

## isqTrain/6

- task_id: `isqTrain/6`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `39`

### Prompt

Implement the following in isQ: implements the gate_decomposition pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement a swap gate decomposition with reversed measurement order to demonstrate how measurement sequence affects bitstring indexing.

2. **Qubits**: 2 qubits (q[0], q[1]), both measured in reversed order M(q[1]), M(q[0]).

3. **State evolution**:
   - Initial: |00⟩
   - After X(q[1]): |10⟩
   - CNOT(q[0], q[1]) with control=1: |10⟩ → |11⟩
   - CNOT(q[1], q[0]) with control=1: |11⟩ → |01⟩
   - CNOT(q[0], q[1]) with control=0: |01⟩ → |01⟩
   - Final state: |01⟩

4. **Expected probabilities**: M(q[1]) measured first = higher bit, M(q[0]) measured second = lower bit. State |01⟩ has q[1]=0, q[0]=1, giving bitstring "01" with probability 1.0.

## isqTrain/3271

- task_id: `isqTrain/3271`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `reversible_computing`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1306`

### Prompt

Write isQ code for the following quantum task: an isQ program: apply CZ twice on |10>. Since CZ*CZ=I, the state returns to |10>.

### Chain-of-thought reasoning

## Reasoning
Goal: Demonstrate that the CZ gate is self-inverse (CZ * CZ = I) by applying it twice to the state |10⟩.
Qubits: 2 qubits (q[0], q[1]) are used, initialized to |00⟩, and both are measured.
Evolution: Starting at |00⟩, an X gate on q[0] flips the state to |10⟩. The first CZ gate leaves the |10⟩ state unchanged (as CZ only applies a -1 phase to |11⟩). Applying the second CZ gate yields the exact same state, |10⟩, confirming CZ * CZ = I.
Probabilities: Because the final quantum state is purely |10⟩, measuring the two qubits yields the bitstring '10' with a probability of 1.0.

## isqTrain/605

- task_id: `isqTrain/605`
- task_type: `output_prediction`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `896`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[4];

procedure main() {
    X(q[0]);
    SWAP(q[0], q[3]);
    SWAP(q[1], q[2]);
    M(q);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit starts with 4 qubits initialized to the ground state |0000>.
2. An X gate is applied to q[0], flipping it from |0> to |1>. The state becomes |0001>.
3. A swap operation (three-CNOT decomposition) exchanges the states of q[0] and q[3]. The |1> state moves from q[0] to q[3], changing the state to |1000>.
4. A swap operation (three-CNOT decomposition) exchanges q[1] and q[2]. Since both are

### Reference answer

{'predicted_probs': {'8': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/203. Dimension: predict probabilities for reference circuit.'}

## isqTrain/3267

- task_id: `isqTrain/3267`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3019`

### Prompt

Create an isQ quantum circuit that an isQ program: apply CNOT twice on |01>. Since CNOT*CNOT=I, the state should return to |01>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Demonstrate that CNOT is self-inverse by applying it twice to |01> and verifying the state returns to |01>.
2. **Qubits**: 2 qubits (q[0], q[1]), both measured.
3. **State evolution**:
   - |00> —initial state
   - X(q[1]) → |01>
   - CNOT(q[0], q[1]) → |01> (control q[0]=|0>, target unchanged)
   - CNOT(q[0], q[1]) → |01> (control q[0]=|0>, target unchanged)
4. **Expected probabilities**: {|01>: 1.0}, since CNOT×CNOT = I and the state remains |01> throughout.

## isqTrain/3269

- task_id: `isqTrain/3269`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `reversible_computing`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3119`

### Prompt

Implement a quantum circuit in isQ: an isQ program: apply CZ twice on |00>. Since CZ*CZ=I, the state returns to |00>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Demonstrate that applying CZ twice is equivalent to the identity operation (CZ² = I) on the |00⟩ state.
2. **Qubits**: 2 qubits (q[0], q[1]) are needed; both are measured.
3. **State evolution**:
   - Initial state: |00⟩
   - After 1st CZ(q[0], q[1]): Control q[0] is |0⟩, so Z is NOT applied to q[1]. State remains |00⟩.
   - After 2nd CZ(q[0], q[1]): Same condition—control still |0⟩. State remains |00⟩.
4. **Expected probabilities**: Since CZ only acts when control is |1⟩, applying it twice on |00⟩ leaves the state unchanged at |00⟩. Measurement yields {|00⟩: 1.0}.

## isqTrain/2469

- task_id: `isqTrain/2469`
- task_type: `code_equivalence`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `global_phase`, `isq_syntax_arrays`, `isq_syntax_deriving_gate`, `isq_syntax_procedures`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `124`

### Prompt

Will these two quantum programs produce identical measurement outcomes?

```isq
import std;
qbit q[2];

procedure cy_gate(qbit c, qbit t) {
    inv S(t);
    CNOT(c, t);
    S(t);
}

procedure main() {
    X(q[0]);
    X(q[1]);
    cy_gate(q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

vs.

```isq
import std;
qbit q[2];

procedure cy_gate(qbit c, qbit t) {
    inv S(t);
    CNOT(c, t);
    S(t);
}

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    X(q[0]);
    X(q[1]);
    cy_gate(q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis

1. **Program A operations**: Initializes two qubits to |00>. Applies X gates to both qubits, preparing the state |11>. It then applies a controlled-Y (CY) gate via `inv S(t)`, `CNOT(c, t)`, and `S(t)`. This sequence transforms the state to -i|10>.
2. **Program B operations**: Executes the exact same initialization, X gates, and CY gate sequence. The only addition is a `GPhase(0.0)` operation before the X gates.
3. **Key difference**: Program B introduces a `GPhase(0.0)` gate, which applies a global phase factor of $e^{i \cdot 0} = 1$.
4. **Measurement probabilities**: The measurement probability distributions are exactly the same. `GPhase(0.0)` is mathematically an identity operation, having no effect on the quantum state or subsequent measurements. Both programs output the state |10> with 100% probability.
5. **Verdict**: Yes

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/1996

- task_id: `isqTrain/1996`
- task_type: `output_prediction`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `446`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

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
1. The circuit initializes a single qubit in the |0> state, applies a Z gate followed by a Y gate, and measures the qubit.
2. Initial state: |0>. Applying the Z gate leaves the state unchanged: Z|0> = |0>.
3. Applying the Y gate to |0> yields Y|0> = i|1>.
4. The final state before measurement is i|1>. Because the probability is the absolute square of the amplitude, the global phase 'i' does not affect the outcome.
5. Measurement collapses the state to |1> with absolute certainty.

Predicted probability distribution: {'1': 1.0}

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Expected probabilities: [0.0, 1.0]'}
