# ISQ training COT RAG corpus: circuit_basics shard 13

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4689

- task_id: `isqTrain/4689`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5061`

### Prompt

判断以下两段isQ代码是否产生相同的测量结果：

代码1：
```isq
import std;
qbit q[1];

procedure main() {
    M(q[0]);
}

```

代码2：
```isq
import std;
qbit q[1];

procedure main() {
    Z(q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A:** Initializes qubit `q[0]` in the default state |0> and immediately measures it.
2. **Program B:** Initializes qubit `q[0]` in the state |0>, applies a Z gate, and then measures it.
3. **Key difference:** Program B applies a Z gate before measurement, whereas Program A acts as the identity.
4. **Probability comparison:** The Z gate leaves the |0> state unchanged because Z|0> = |0>. Therefore, both programs measure the exact same quantum state.
5. **Verdict:** Yes

### Reference answer

{'equivalent': True, 'explanation': "Z on |0> gives |0>, same as identity Both programs produce the same probability distribution: {'0': 1.0}.", 'probs_a': {'0': 1.0}, 'probs_b': {'0': 1.0}}

## isqTrain/1831

- task_id: `isqTrain/1831`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `1318`

### Prompt

Help me write isQ code that Apply Hadamard gate 8 times to |0> and measure. H^8 = I.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply Hadamard gate 8 times to |0⟩ to show H⁸ = I, then measure.
2. Qubits: 1 qubit `q[0]`, which is measured.
3. State evolution:
   - Initial: |0⟩
   - H⁸|0⟩ = (H²)⁴|0⟩ = I⁴|0⟩ = |0⟩ (since H² = I)
4. Measurement probabilities: {|0⟩: 1.0}, since the final state is |0⟩.

## isqTrain/1594

- task_id: `isqTrain/1594`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1574`

### Prompt

帮我写一个isQ程序：Put 4 qubits in superposition, measure only q[1].

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create superposition on 4 qubits, measure only q[1].
2. **Qubits**: 4 qubits (q[0]-q[3]), only q[1] measured.
3. **State evolution**:
   - Initial: |0000⟩
   - After H on all 4 qubits: (1/4) Σ_{x∈{0,1}^4} |x⟩ (equal superposition of all 16 states)
4. **Measurement probabilities**: Since all qubits are independently in equal superposition, q[1] has probability 0.5 for |0⟩ and 0.5 for |1⟩, regardless of the other unmeasured qubits.

## isqTrain/4704

- task_id: `isqTrain/4704`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `107`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    T(q[0]);
    T(q[0]);
    H(q[0]);
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The qubit is initialized in the state |0>.
2. `H(q[0])` creates an equal superposition: (1/sqrt(2))|0> + (1/sqrt(2))|1>.
3. Two sequential `T(q[0])` gates apply a

### Reference answer

{'predicted_probs': {'0': 0.5, '1': 0.5}, 'explanation': 'This isQ program operates on 1 qubit(s). The measurement probability distribution is: P(|0>) = 0.5000, P(|1>) = 0.5000.'}

## isqTrain/1801

- task_id: `isqTrain/1801`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3716`

### Prompt

Implement a quantum circuit in isQ: Apply Rx(pi*3/6) to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply Rx(π/2) to |0⟩ and measure, producing an equal superposition.
2. **Qubits**: 1 qubit (q[0]) is allocated and measured.
3. **State evolution**: Initial state |ψ⟩ = |0⟩. After Rx(π/2): |ψ⟩ = cos(π/4)|0⟩ − i·sin(π/4)|1⟩ = (|0⟩ − i|1⟩)/√2.
4. **Expected probabilities**: P(|0⟩) = |1/√2|² = 0.5, P(|1⟩) = |−i/√2|² = 0.5, giving an equal 50/50 split.

## isqTrain/1574

- task_id: `isqTrain/1574`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `4463`

### Prompt

用isQ实现On 3 qubits, set q[1]=|1> and apply CNOT with control=q[1], target=q[2]. Measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare q[1]=|1⟩, then use it to flip q[2] via CNOT, and measure all.
2. **Qubits**: 3 qubits q[0], q[1], q[2]; all are measured.
3. **State evolution**:
   - Initial state: |000⟩
   - After X(q[1]): |010⟩ (q[1] flipped to |1⟩)
   - After CNOT(q[1], q[2]): |011⟩ (control q[1]=|1⟩, so target q[2] flips to |1⟩)
4. **Expected measurement**: The circuit is deterministic — state |011⟩ is measured with probability 1.0. Bitstring 011 (q[0]=0, q[1]=1, q[2]=1).

## isqTrain/1660

- task_id: `isqTrain/1660`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `measurement_order`
- source: `isq_train_cot`
- dataset_index: `5283`

### Prompt

请用isQ语言编写一个量子电路：Put 2 qubits in superposition and measure in reverse order (N-1,...,0).

### Chain-of-thought reasoning

## Reasoning
1. The goal is to initialize two qubits into an equal superposition and measure them in reverse index order.
2. The circuit requires 2 qubits, both of which are measured.
3. Starting in the initial state |00>, applying an H gate to q[0] evolves the state to (1/√2)(|00> + |10>).
4. Applying an H gate to q[1] further evolves the state to an equal superposition of all basis states: (1/2)(|00> + |01> + |10> + |11>).
5. Because the final state is a uniform superposition, measuring q[1] (MSB) and then q[0] (LSB) yields an exact 25% probability for each of the four possible outcomes: |00>, |01>, |10>, and |11>.

## isqTrain/4741

- task_id: `isqTrain/4741`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `5236`

### Prompt

Determine if these two isQ implementations are functionally equivalent:

Version A:
```isq
import std;
qbit q[3];

procedure main() {
    X(q[0]);
    X(q[1]);
    X(q[0]); // additional bit flip
    M(q[0]); M(q[1]); M(q[2]);
}

```

Version B:
```isq
import std;
qbit q[3];

procedure main() {
    X(q[0]);
    X(q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** initializes qubits q[0], q[1], and q[2] to |0>. It applies an X gate to q[0] and q[1], flipping them to |1>. It then applies another X gate to q[0], flipping it back to |0>. 
2. **Program B** initializes qubits q[0], q[1], and q[2] to |0>. It applies an X gate to q[0] and q[2], flipping them to |1>, while q[1] remains in the |0> state.
3. The key difference is the state of the qubits before measurement. Program A results in the quantum state |0>|1>|0>, while Program B results in the quantum state |1>|0>|1>.
4. The measurement probability distributions are different. Program A will yield a 100% probability of measuring the bitstring 010 (assuming q[0] is the highest bit). Program B will yield a 100% probability of measuring the bitstring 101.
5. Verdict: No

### Reference answer

{'equivalent': False, 'explanation': 'After adding X gate to Program A, the programs produce different probability distributions.', 'probs_a': {'010': 1.0}, 'probs_b': {'101': 1.0}}

## isqTrain/1833

- task_id: `isqTrain/1833`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4576`

### Prompt

帮我写一个isQ程序：Apply the gate sequence ZYX on |0> and measure.

### Chain-of-thought reasoning

## Reasoning
- Goal: Apply Z, Y, X gates in sequence to |0⟩, then measure.
- 1 qubit needed (q[0]), measured at the end.
- State evolution:
  1. |0⟩
  2. Z|0⟩ = |0⟩
  3. Y|0⟩ = i|1⟩
  4. X(i|1⟩) = i|0⟩
- Final state: i|0⟩ (global phase irrelevant). Measurement yields 0 with probability 1.

## isqTrain/4718

- task_id: `isqTrain/4718`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `superposition`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2605`

### Prompt

Do these two isQ programs produce the same measurement results?

Program A:
```isq
import std;
qbit q[1];

procedure main() {
    Ry(pi/4.0, q[0]);
    M(q[0]);
}

```

Program B:
```isq
import std;
qbit q[1];

procedure main() {
    Ry(pi/2.0, q[0]);
    H(q[0]); // add superposition
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. Program A applies an $R_y(\pi/4)$ rotation to |0⟩, yielding the state $\cos(\pi/8)|0\rangle + \sin(\pi/8)|1\rangle$.
2. Program B applies $R_y(\pi/2)$ followed by H. The $R_y(\pi/2)$ gate rotates |0⟩ to |+⟩, and applying the H gate to |+⟩ returns it to the |0⟩ state.
3. The key difference is that Program B uses a larger rotation angle and an additional H gate, which constructively interferes to return the qubit to a basis state.
4. Measurement probabilities differ: Program A has a $\sin^2(\

### Reference answer

{'equivalent': False, 'explanation': 'After adding H gate to Program B, the programs produce different probability distributions.', 'probs_a': {'0': 0.853553, '1': 0.146447}, 'probs_b': {'0': 1.0}}
