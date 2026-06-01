# ISQ training COT RAG corpus: circuit_basics shard 3

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1606

- task_id: `isqTrain/1606`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `data_encoding_qml`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4530`

### Prompt

I need an isQ program to Apply Ry(pi*4/8) to each of 2 qubits and measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply Ry(π/2) to each of 2 qubits and measure both.
2. **Qubits**: 2 qubits (q[0], q[1]), both measured.
3. **State evolution**:
   - Initial state: |00⟩
   - Ry(π/2)|0⟩ = cos(π/4)|0⟩ + sin(π/4)|1⟩ = (|0⟩ + |1⟩)/√2 = |+⟩
   - After Ry(π/2) on q[0]: |+0⟩ = (|0⟩ + |1⟩)/√2 ⊗ |0⟩
   - After Ry(π/2) on q[1]: |+⟩⊗|+⟩ = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2
4. **Expected probabilities**: Each basis state has equal probability 1/4 since both qubits are in the equal superposition |+⟩ state, giving P(00)=P(01)=P(10)=P(11)=0.25.

## isqTrain/2622

- task_id: `isqTrain/2622`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `entanglement`, `global_phase`, `measurement_order`
- source: `isq_train_cot`
- dataset_index: `1647`

### Prompt

这两个isQ程序是等价的吗？

程序A：
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

程序B：
```isq
import std;

qbit q[2];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    H(q[0]);
    CNOT(q[0], q[1]);
    
    M(q[1]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. Program A initializes two qubits to |00>, applies an H gate to q[0] creating (|00> + |10>)/√2, and then a CNOT(q[0], q[1]) to form the Bell state (|00> + |11>)/√2. 
2. Program B applies the exact same quantum gates (H and CNOT) to the same initial state.
3. The only difference is that Program B includes `GPhase(0.0)` at the beginning of the circuit.
4. `GPhase(0.0)` applies a global phase of $e^{i0} = 1$, which is an identity operation. Thus, both programs have identical quantum states prior to measurement.
5. Both programs yield identical measurement probability distributions (50% for |00> and 50% for |11>).
Verdict: Yes

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/1567

- task_id: `isqTrain/1567`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `452`

### Prompt

Create an isQ quantum circuit that Apply the gate sequence S-S-H to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply the S-S-H gate sequence to an initial |0> state and measure the output.
2. **Qubits**: 1 qubit is needed, and it is measured.
3. **State Evolution**:
   - Initial: |0>
   - After 1st S: S|0> = |0> (S adds a phase of $i$ to |1>, so |0> is unaffected)
   - After 2nd S: S|0> = |0>
   - After H: H|0> = |+> = (1/√2)(|0> + |1>)
4. **Probabilities**: The final state |+> is an equal superposition of |0> and |1>, yielding a 50% probability for each outcome. Expected measurement probabilities: P(0) = 0.5, P(1) = 0.5.

## isqTrain/4703

- task_id: `isqTrain/4703`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3885`

### Prompt

Do these two isQ programs produce the same measurement results?

Program A:
```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    T(q[0]);
    T(q[0]);
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
    S(q[0]);
    H(q[0]);
    H(q[0]); // add superposition
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis

**Program A:** Applies H → T → T → H to |0⟩. Two T gates compose to S (since T² = S), giving the sequence H → S → H.

**Program B:** Applies H → S → H → H to |0⟩.

**Key difference:** Program B has an extra H gate at the end compared to Program A.

**Measurement probabilities:** Both programs yield 50% |0⟩ and 50% |1⟩. In Program A, H-S-H produces equal probabilities. In Program B, the additional H gate changes the state but preserves the 50/50 distribution since applying H to any equal-amplitude superposition (with phases) still yields a state with equal measurement probabilities (both outcomes have magnitude 1/2).

**Verdict: Yes** — the programs are equivalent in measurement probability distribution.

### Reference answer

{'equivalent': True, 'explanation': 'After adding H gate to Program B, the programs produce the same probability distributions.', 'probs_a': {'0': 0.5, '1': 0.5}, 'probs_b': {'0': 0.5, '1': 0.5}}

## isqTrain/1657

- task_id: `isqTrain/1657`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `global_phase`
- source: `isq_train_cot`
- dataset_index: `1909`

### Prompt

Create an isQ quantum circuit that Apply X to prepare |1>, then apply a global phase of pi using GPhase. Measure. (Global phase has no observable effect.)

### Chain-of-thought reasoning

## Reasoning
Goal: Prepare |1> and demonstrate that GPhase has no observable effect on measurement.
We need 1 qubit, which is measured.

Step-by-step state evolution:
1. Initial state: |0>
2. After X(q[0]): |1>
3. After GPhase(π): -|1> (global phase of -1 applied)
4. Measurement: global phase is unobservable, so P(|1>) = 1.0

Expected probabilities: {|1>: 1.0}, since global phase does not affect measurement outcomes.

## isqTrain/650

- task_id: `isqTrain/650`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `entanglement`, `measurement_order`
- source: `isq_train_cot`
- dataset_index: `3932`

### Prompt

What measurement results should I expect from this quantum program?

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

## Circuit Analysis
1. **Gates applied**: `H(q[0])`, `CNOT(q[0], q[1])`.
2. **State evolution**:
   - Initial: |00⟩
   - After H(q[0]): 1/√2 (|0⟩ + |1⟩) ⊗ |0⟩ = 1/√2 (|00⟩ + |10⟩)
   - After CNOT(q[0], q[1]): 1/√2 (|00⟩ + |11⟩) (Bell state)
3. **Final state**: (|00⟩ + |11⟩)/√2.
4. **Prediction**: Measuring yields |00⟩ or |11⟩ with equal probability.

Predicted probabilities: {|00>: 0.5, |11>: 0.5}

### Reference answer

{'predicted_probs': {'0': 0.5, '3': 0.5}, 'explanation': 'Parametric variant of isqHumanEval/213. Dimension: predict probabilities for reference circuit.'}

## isqTrain/4728

- task_id: `isqTrain/4728`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `899`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes two qubits, q[0] and q[1], in the ground state |00>.
2. The first X gate flips q[0] from |0> to |1>, evolving the state to |10>.
3. The second X gate flips q[0] again from |1> back to |0>, returning the state to |00>.
4. Both qubits are measured in the computational basis.

Predicted probability distribution: {|00>: 1.0}

### Reference answer

{'predicted_probs': {'00': 1.0}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|00>) = 1.0000.'}

## isqTrain/4671

- task_id: `isqTrain/4671`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `1827`

### Prompt

Are these two quantum circuits equivalent in terms of measurement output?

Circuit 1:
```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    H(q[0]);
    X(q[0]); // additional bit flip
    M(q[0]);
}

```

Circuit 2:
```isq
import std;
qbit q[1];

procedure main() {
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A**: Starts in |0>, applies H twice (returning to |0>), and then applies an X gate to flip the state to |1>.
2. **Program B**: Starts in |0>, applies no gates, and remains in the |0> state.
3. **Key difference**: Program A applies an X gate before measurement, while Program B does not.
4. **Probabilities**: Program A will measure |1> with 100% probability, whereas Program B will measure |0> with 100% probability. 
5. **Verdict**: Not equivalent.

### Reference answer

{'equivalent': False, 'explanation': 'After adding X gate to Program A, the programs produce different probability distributions.', 'probs_a': {'1': 1.0}, 'probs_b': {'0': 1.0}}

## isqTrain/1584

- task_id: `isqTrain/1584`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `2311`

### Prompt

实现以下量子计算任务（使用isQ）：On 4 qubits, set q[2]=|1> and apply CNOT with control=q[2], target=q[3]. Measure all.

### Chain-of-thought reasoning

## Reasoning
The goal is to prepare a specific 4-qubit basis state and measure it.
Four qubits (q[0] to q[3]) are used, and all are measured.
Initially, the state is |0000>. The X gate applied to q[2] flips it to |1>, changing the state to |0010>.
The CNOT gate with control q[2] and target q[3] flips q[3] to |1> because the control is |1>, evolving the state to |0011>.
Since the final state is exactly |0011>, measuring all qubits yields the bitstring '0011' with a probability of 1.0.

## isqTrain/4684

- task_id: `isqTrain/4684`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `superposition`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `810`

### Prompt

这两个isQ程序是等价的吗？

程序A：
```isq
import std;
qbit q[1];

procedure main() {
    Ry(pi/2.0, q[0]);
    M(q[0]);
}

```

程序B：
```isq
import std;
qbit q[1];

procedure main() {
    Rx(pi/2.0, q[0]);
    H(q[0]); // add superposition
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis

1. **Program A** applies `Ry(π/2)` to |0⟩, producing (1/√2)|0⟩ + (1/√2)|1⟩. Measurement yields P(0) = P(1) = 1/2.

2. **Program B** applies `Rx(π/2)` then `H` to |0⟩. First, `Rx(π/2)|0⟩ = (1/√2)|0⟩ − (i/√2)|1⟩`. Then applying `H` yields `((1−i)/2)|0⟩ + ((1+i)/2)|1⟩`.

3. **The key difference** is the gate sequence: Program A uses one rotation (Ry), while Program B uses Rx followed by H, resulting in different final quantum states with a relative phase difference.

4. **Despite different final states**, the measurement probabilities are identical: `|(1−i)/2|² = 1/2` and `|(1+i)/2|² = 1/2`. Both programs yield P(0) = P(1) = 1/2.

5. **Verdict: Yes** — the programs produce the same measurement probability distribution.

### Reference answer

{'equivalent': True, 'explanation': 'After adding H gate to Program B, the programs produce the same probability distributions.', 'probs_a': {'0': 0.5, '1': 0.5}, 'probs_b': {'0': 0.5, '1': 0.5}}
