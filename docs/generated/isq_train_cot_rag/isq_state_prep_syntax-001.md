# ISQ training COT RAG corpus: isq_state_prep_syntax shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/277

- task_id: `isqTrain/277`
- task_type: `code_generation`
- category: `isq_state_prep_syntax`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `2132`

### Prompt

Code this in isQ: implements a variant of the state_preparation pattern using q[2] -> q[4]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create an equal superposition of |0000⟩ and |1100⟩ across a 4-qubit register, with qubits 2 and 3 remaining in ground state.
2. **Qubits**: 4 qubits (q[0]-q[3]), all measured to produce 4-bit outcomes.
3. **State evolution**:
   - Initialize: |0000⟩
   - H(q[0]): (|0000⟩ + |1000⟩)/√2
   - CNOT(q[0], q[1]): (|0000⟩ + |1100⟩)/√2
4. **Probabilities**: Each basis state has amplitude 1/√2, giving probability |1/√2|² = 0.5 for both |0000⟩ and |1100⟩.

## isqTrain/1926

- task_id: `isqTrain/1926`
- task_type: `output_prediction`
- category: `isq_state_prep_syntax`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `1097`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;
qbit q[2];
procedure main() {
    q = |0> - |3>;
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **State Initialization**: The 2-qubit register `q` is initialized to $|0\rangle - |3\rangle$. In a 2-qubit system, $|0\rangle$ represents $|00\rangle$ and $|3\rangle$ represents $|11\rangle$. The normalized initial state is $\frac{1}{\sqrt{2}}(|00\rangle - |11\rangle)$.
2. **Operations**: No quantum gates are applied. The state remains $\frac{1}{\sqrt{2}}(|00\rangle - |11\rangle)$.
3. **Measurements**: Both qubits are measured. The squared magnitudes of the coefficients for $|00\rangle$ and $|11\rangle$ are both $|\frac{1}{\sqrt{2}}|^2 = 0.5$.

Predicted probability distribution: {'00': 0.5, '11': 0.5}

### Reference answer

{'predicted_probs': {'00': 0.5, '11': 0.5}, 'explanation': 'State preparation via ket expression.'}

## isqTrain/278

- task_id: `isqTrain/278`
- task_type: `code_generation`
- category: `isq_state_prep_syntax`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `632`

### Prompt

Implement the following in isQ: implements the state_preparation pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Prepare the entangled state (|00⟩ - |11⟩)/√2 and measure qubits in reversed order (q[1] before q[0]).

2. **Qubits**: 2 qubits (q[0], q[1]), both measured with M(q[1]) then M(q[0]).

3. **State evolution**:
   - Initial: |00⟩
   - After `q = |0> - |3>`: (|00⟩ - |11⟩)/√2 — an equal superposition of basis states 0 and 3

4. **Expected probabilities**: The state has equal amplitude on |00⟩ and |11⟩, giving |00⟩: 0.5 and |11⟩: 0.5. Since q[1] is measured first, it becomes the higher bit in the bitstring, but since both qubits are identical in each basis state (both 0 or both 1), the reversed order doesn't change the outcome distribution.

## isqTrain/275

- task_id: `isqTrain/275`
- task_type: `output_prediction`
- category: `isq_state_prep_syntax`
- difficulty: `basic`
- concept_tags: `entanglement`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `1334`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;

qbit q[2];

procedure main() {
    q = [1, 0, 0, -1];
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis

1. **Operations**: The program initializes a 2-qubit register with statevector [1, 0, 0, -1], then measures both qubits.

2. **State Evolution**:
   - Initial state: |ψ⟩ = (1/√2)(|00⟩ - |11⟩) (normalized from the given amplitude vector)
   - This is a Bell state - a maximally entangled state
   - No gates are applied between initialization and measurement

3. **Final State**: |ψ⟩ = (1/√2)|00⟩ - (1/√2)|11⟩

4. **Measurement Probabilities**: The probability amplitudes are |1/√2|² = 0.5 for both |00⟩ and |11⟩. The |01⟩ and |10⟩ components have zero amplitude. This gives equal probability of measuring both qubits as |0⟩ or both as |1⟩.

**Predicted probability distribution**: {|00⟩: 0.5, |11⟩: 0.5}

### Reference answer

{'predicted_probs': {'0': 0.5, '3': 0.5000000000000001}, 'explanation': 'Parametric variant of isqHumanEval/92. Dimension: predict probabilities for reference circuit.'}

## isqTrain/1925

- task_id: `isqTrain/1925`
- task_type: `output_prediction`
- category: `isq_state_prep_syntax`
- difficulty: `basic`
- concept_tags: `entanglement`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `1733`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;
qbit q[2];
procedure main() {
    q = [1, 0, 0, -1];
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The program initializes a 2-qubit system with the complex vector `[1, 0, 0, -1]`.
2. This corresponds to the normalized state $|\psi\rangle = \frac{1}{\sqrt{2}}|00\rangle - \frac{1}{\sqrt{2}}|11\rangle$, representing an entangled Bell state.
3. Both qubits `q[0]` and `q[1]` are measured in the computational basis.
4. The probability of outcome '00' is $|1/\sqrt{2}|^2 = 0.5$.
5. The probability of outcome '11' is $|-1/\sqrt{2}|^2 = 0.5$.

Predicted probability distribution: {'00': 0.5, '11': 0.5}

### Reference answer

{'predicted_probs': {'00': 0.5, '11': 0.5}, 'explanation': 'State preparation via array assignment.'}

## isqTrain/280

- task_id: `isqTrain/280`
- task_type: `output_prediction`
- category: `isq_state_prep_syntax`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3081`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;

qbit q[2];

procedure main() {
    q = |0> - |3>;
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initialization**: Two qubits `q[0]` and `q[1]` are allocated, implicitly starting in the $|00\rangle$ state.
2. **State Preparation**: The assignment `q = |0> - |3>;` initializes the 2-qubit register into an unnormalized superposition of the 0th ($|00\rangle$) and 3rd ($|11\rangle$

### Reference answer

{'predicted_probs': {'0': 0.5, '3': 0.5000000000000001}, 'explanation': 'Parametric variant of isqHumanEval/93. Dimension: predict probabilities for reference circuit.'}

## isqTrain/276

- task_id: `isqTrain/276`
- task_type: `code_generation`
- category: `isq_state_prep_syntax`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `1035`

### Prompt

Write an isQ program that implements a variant of the state_preparation pattern using q[2] -> q[3]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a Bell-like superposition (|000⟩ + |110⟩)/√2 on qubits q[0], q[1], q[2] using an expanded 4-qubit register.

2. **Qubits**: 4 qubits declared (q[0] to q[3]); only q[0], q[1], q[2] are measured to match predicted output.

3. **State evolution**:
   - Initialize: |0000⟩
   - H(q[0]): (|0⟩ + |1⟩)/√2 ⊗ |000⟩ = (|0000⟩ + |1000⟩)/√2
   - CNOT(q[0], q[1]): (|0000⟩ + |1100⟩)/√2
   - CNOT(q[2
