# ISQ training COT RAG corpus: circuit_basics shard 2

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1597

- task_id: `isqTrain/1597`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5343`

### Prompt

Write an isQ program that Prepare |1> then apply Rx(pi). Measure.

### Chain-of-thought reasoning

## Reasoning
Goal: Prepare |1>, apply Rx(π), and measure to verify the output state.
Qubits: 1 qubit (q[0]), which is measured.
Evolution: |0⟩ →[X]→ |1⟩ →[Rx(π)]→ -i|0⟩ (global phase -i is unobservable).
Result: Final state is |0⟩, so measurement yields {|0⟩: 1.0}.

## isqTrain/1804

- task_id: `isqTrain/1804`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `119`

### Prompt

用isQ实现Apply Rx(pi*6/6) to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. The goal of the circuit is to apply an Rx(π) rotation (since 6/6 = 1) to an initial |0> state and measure the result.
2. The circuit requires 1 qubit, which is prepared in the default |0> state and measured at the end.
3. The initial state |0> evolves under the Rx(π) gate according to the formula Rx(θ)|0> = cos(θ/2)|0> - i*sin(θ/2)|1>.
4. Substituting θ = π gives the final state cos(π/2)|0> - i*sin(π/2)|1> = -i|1>.
5. Ignoring the global phase (-i), the final quantum state is exactly |1>, guaranteeing a 100% probability of measuring the |1> state.

## isqTrain/1824

- task_id: `isqTrain/1824`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3009`

### Prompt

用isQ实现Apply Ry(pi*2/4) to q[0], then CNOT(q[0], q[1]). Measure both.

### Chain-of-thought reasoning

## Reasoning
Goal: Create a Bell state by applying Ry(π/2) to q[0] followed by CNOT(q[0], q[1]).
Two qubits needed (q[0], q[1]), both measured.

State evolution:
- Initial: |00⟩
- After Ry(π/2) on q[0]: Ry(π/2)|0⟩ = (|0⟩ + |1⟩)/√2, giving (|00⟩ + |10⟩)/√2
- After CNOT(q[0], q[1]): Control q[0]=|1⟩ flips target q[1], yielding (|00⟩ + |11⟩)/√2

Expected probabilities: P(00) = 0.5, P(11) = 0.5 (equal superposition of |00⟩ and |11⟩).

## isqTrain/1607

- task_id: `isqTrain/1607`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `data_encoding_qml`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1100`

### Prompt

Implement a quantum circuit in isQ: Apply Ry(pi*5/8) to each of 2 qubits and measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply Ry(5π/8) rotation to each of 2 qubits, then measure both.
2. **Qubits**: 2 qubits (q[0], q[1]), both measured.
3. **State evolution**:
   - Start: |00⟩
   - After Ry(5π

## isqTrain/1480

- task_id: `isqTrain/1480`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `data_encoding_qml`
- source: `isq_train_cot`
- dataset_index: `1384`

### Prompt

Implement a quantum circuit in isQ: Encode the classical value 7/16 into a qubit using angle encoding (Ry rotation with angle pi*7/16). Measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Angle encode the classical value 7/16 into a single qubit's Y-rotation and measure.
2. **Qubits**: 1 qubit (`q[0]`), which is measured.
3. **Evolution**:
   - Start in |0>.
   - Apply Ry(7π/16, q[0]): Rotates around Y-axis by θ = 7π/16.
   - State becomes cos(θ/2)|0> + sin(θ/2)|1> = cos(7π/32)|0> + sin(7π/32)|1>.
4. **Probabilities**: Measuring gives |0> with probability cos²(7π/32) ≈ 0.5975 and |1> with probability sin²(7π/32) ≈ 0.4025.

## isqTrain/1829

- task_id: `isqTrain/1829`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `5035`

### Prompt

Create an isQ quantum circuit that Apply Hadamard gate 6 times to |0> and measure. H^6 = I.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply H gate six times to |0> and measure the result.
Uses 1 qubit (q[0]), which is measured at the end.
Initial state: |0>. Applying H once gives |+>, applying H again returns |0> (since H²=I). Repeating this cycle three times (6 H gates total) leaves the state as |0>.
Expected probabilities: {|0>: 1.0}, because H⁶ = (H²)³ = I³ = I, so the final state is |0> with certainty.

## isqTrain/4730

- task_id: `isqTrain/4730`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3103`

### Prompt

Will these two quantum programs produce identical measurement outcomes?

```isq
import std;
qbit q[3];

procedure main() {
    X(q[0]);
    X(q[1]);
    ctrl ctrl X(q[0], q[1], q[2]);
    X(q[0]); // additional bit flip
    M(q[0]); M(q[1]); M(q[2]);
}

```

vs.

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

## Equivalence Analysis

1. **Program A** applies: X on q[0], X on q[1], a Toffoli (ctrl ctrl X) with q[0],q[1] as controls and q[2] as target, then an additional X on q[0]. Starting from |000⟩: X(q[0]) and X(q[1]) produce |110⟩. The Toffoli fires (both controls are |1⟩), yielding |111⟩. The final X(q[0]) produces |011⟩.

2. **Program B** applies: X on q[0], then a Toffoli with q[0],q[1] controlling q[2]. Starting from |000⟩: X(q[0]) produces |100⟩. The Toffoli does not fire (q[1]=|0⟩), so the state remains |100⟩.

3. **Key difference:** Program A initializes q[1] to |1⟩ (enabling the Toffoli) and then flips q[0] back to |0⟩ at the end. Program B leaves q[1] at |0⟩, so the Toffoli never activates, and has no final X on q[0].

4. **Measurement probabilities:** Program A deterministically yields |011⟩ (bitstring 011), while Program B deterministically yields |100⟩ (bitstring 100). These are completely different distributions.

5. **Verdict:** Not equivalent

### Reference answer

{'equivalent': False, 'explanation': 'After adding X gate to Program A, the programs produce different probability distributions.', 'probs_a': {'011': 1.0}, 'probs_b': {'100': 1.0}}

## isqTrain/1823

- task_id: `isqTrain/1823`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3714`

### Prompt

用isQ实现Apply Ry(pi*1/4) to q[0], then CNOT(q[0], q[1]). Measure both.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a partially entangled two-qubit state using a Y-rotation followed by CNOT.
2. **Qubits**: 2 qubits (`q[0]`, `q[1]`), both measured.
3. **State evolution**:
   - Initial: `|00⟩`
   - After `Ry(π/4, q[0])`: `cos(π/8)|00⟩ - sin(π/8)|10⟩` (rotates q[0] around Y by π/4)
   - After `CNOT(q[0], q[1])`: `cos(π/8)|00⟩ - sin(π/8)|11⟩` (entangles the two qubits)
4. **Probabilities**: P(00) = cos²(π/8) ≈ 0.854, P(11) = sin²(π/8) ≈ 0.146, P(01) = P(10) = 0. The CNOT correlates the qubits perfectly, so only `|00⟩` and `|11⟩` outcomes are possible.

## isqTrain/4695

- task_id: `isqTrain/4695`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `5524`

### Prompt

这两个isQ程序是等价的吗？

程序A：
```isq
import std;
qbit q[2];

procedure main() {
    H(q[0]);
    H(q[1]);
    M(q[0]); M(q[1]);
}

```

程序B：
```isq
import std;
qbit q[2];

procedure main() {
    H(q[1]);
    H(q[0]);
    H(q[0]); // add superposition
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** applies an H gate to both q[0] and q[1]. This evolves the initial state |00> to |+>|+> = 1/2(|00> + |01> + |10> + |11>). The measurement probabilities are 25% for all four possible outcomes.
2. **Program B** applies an H gate to q[1], and two successive H gates to q[0]. Since H is self-inverse (H*H = I), the two H gates on q[0] cancel out, leaving it in its initial state |0>. 
3. The final state for Program B is |0>|+> = 1/sqrt(2)(|00> + |01>). The measurement probabilities are 50% for |00> and 50% for |01>.
4. The key difference is the double application of H on q[0] in Program B, which collapses its superposition back to the basis state, whereas Program A maintains the superposition.
5. Verdict: Not equivalent.

### Reference answer

{'equivalent': False, 'explanation': 'After adding H gate to Program B, the programs produce different probability distributions.', 'probs_a': {'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25}, 'probs_b': {'00': 0.5, '01': 0.5}}

## isqTrain/1800

- task_id: `isqTrain/1800`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4593`

### Prompt

帮我写一个isQ程序：Apply Rx(pi*2/6) to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply Rx(π/3) gate to |0⟩ and compute measurement probabilities.
Qubits: 1 qubit declared, 1 measured.
State evolution: |0⟩ → Rx(π/3)|0⟩ = cos(π/6)|0⟩ - i·sin(π/6)|1⟩ = (√3/2)|0⟩ - (i/2)|1⟩.
Probabilities: P(|0⟩) = |√3/2|² = 0.75, P(|1⟩) = |-i/2|² = 0.25.
