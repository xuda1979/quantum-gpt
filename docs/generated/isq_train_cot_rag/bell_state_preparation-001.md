# ISQ training COT RAG corpus: bell_state_preparation shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3151

- task_id: `isqTrain/3151`
- task_type: `code_generation`
- category: `bell_state_preparation`
- difficulty: `basic`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4176`

### Prompt

实现以下量子计算任务（使用isQ）：an isQ program: create entangled pair between q[0] and q[2] in a 3-qubit register. Other qubits stay |0>.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Create a Bell state between q[0] and q[2], leaving q[1] in |0⟩.
2. Qubits: 3-qubit register (q[0], q[1], q[2]), all measured.
3. State evolution:
   - Initial state: |000⟩
   - H(q[0]): (|000⟩ + |100⟩)/√2
   - CNOT(q[0], q[2]): (|000⟩ + |101⟩)/√2
4. Measurement probabilities: The final state is an equal superposition of |000⟩ and |101⟩, so measuring yields |000⟩ with 50% probability and |101⟩ with 50% probability.

## isqTrain/3154

- task_id: `isqTrain/3154`
- task_type: `code_generation`
- category: `bell_state_preparation`
- difficulty: `basic`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2187`

### Prompt

Create an isQ quantum circuit that an isQ program: create entangled pair between q[0] and q[1] in a 5-qubit register. Other qubits stay |0>.

### Chain-of-thought reasoning

## Reasoning
Goal: Create a Bell state entangling q[0] and q[1] in a 5-qubit register, leaving q[2]–q[4] in |0⟩.

State evolution:
1. Initialize: |ψ⟩ = |00000⟩
2. H(q[0]): |ψ⟩ = (|0⟩ + |1⟩)/√2 ⊗ |0000⟩ = (|00000⟩ + |10000⟩)/√2
3. CNOT(q[0], q[1]): Control q[0] flips target q[1] when |1⟩ → |ψ⟩ = (|00000⟩ + |11000⟩)/√2

All 5 qubits are measured. The final state is an equal superposition of |00000⟩ and |11000⟩, yielding expected probabilities: P(|00000⟩) = 0.5, P(|11000⟩) = 0.5.

## isqTrain/3169

- task_id: `isqTrain/3169`
- task_type: `code_generation`
- category: `bell_state_preparation`
- difficulty: `basic`
- concept_tags: `entanglement`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `1337`

### Prompt

帮我写一个isQ程序：with a procedure `apply_bell(qbit a, qbit b)` that creates a Bell pair. Call it from main and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a Bell pair (maximally entangled two-qubit state) using a Hadamard and CNOT.
2. **Qubits**: 2 global qubits `q[2]`, both measured.
3. **State evolution**:
   - Start: |00⟩
   - H(a): (|0⟩+|1⟩)/√2 ⊗ |0⟩ = (|00⟩+|10⟩)/√2
   - CNOT(a,b): (|00⟩+|11⟩)/√2  (Bell state |Φ⁺⟩)
4. **Probabilities**: |00⟩ and |11⟩ each have amplitude 1/√2, giving probability 0.5 each.

## isqTrain/3153

- task_id: `isqTrain/3153`
- task_type: `code_generation`
- category: `bell_state_preparation`
- difficulty: `basic`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4559`

### Prompt

请用isQ语言编写一个量子电路：an isQ program: create entangled pair between q[0] and q[3] in a 4-qubit register. Other qubits stay |0>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a Bell-like entangled pair between q[0] and q[3] in a 4-qubit register, leaving q[1] and q[2] in |0⟩.
2. **Qubits**: 4-qubit register q[4]; all four qubits are measured.
3. **State evolution**:
   - Initial state: |0000⟩
   - H(q[0]): transforms |0⟩₀ → |+⟩ = (|0⟩ + |1⟩)/√2, yielding (|0000⟩ + |1000⟩)/√2
   - CNOT(q[0], q[3]): flips q[3] when q[0] is |1⟩, producing (|0000⟩ + |1001⟩)/√2
4. **Expected probabilities**: The final state is an equal superposition of |0000⟩ and |1001⟩, so measurement yields {|0000⟩: 0.5, |1001⟩: 0.5}.

## isqTrain/3152

- task_id: `isqTrain/3152`
- task_type: `code_generation`
- category: `bell_state_preparation`
- difficulty: `basic`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3437`

### Prompt

Implement a quantum circuit in isQ: an isQ program: create entangled pair between q[0] and q[1] in a 4-qubit register. Other qubits stay |0>.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Generate a reasoning section for a specific isQ quantum program.
    *   Goal: Explain the creation of an entangled pair (Bell state) between q[0] and q[1] in a 4-qubit register.
    *   Circuit Details: H on q[0], CNOT(q[0], q[1]), measure all 4 qubits.
    *   predicted output: `|0000>: 0.5, |1100>: 0.5`.
    *   Constraints: Concise (3-8 lines), start with "## Reasoning", NO code blocks, use Dirac notation.

2.  **Deconstruct the Circuit & State Evolution:**
    *   Initial state: 4 qubits, all in |0>. $|q_3 q_2 q_1 q_0\rangle = |0000\rangle$.
    *   Step 1: `H(q[0])`. Transforms $|0\rangle$ to $(|0\rangle + |1\rangle)/\sqrt{2}$. State becomes $\frac{1}{\sqrt{2}}(|0000\rangle + |0001\rangle)$. (Assuming bit ordering or just standard tensor product, let's write it as $|00\rangle_{q[3]q[2]} \otimes |00\rangle_{q[1]q[0]} \rightarrow |00\rangle \otimes \frac{1}{\sqrt{2}}(|0\rangle+|1\rangle) \otimes |0\rangle$ -> Let's stick to simpler notation: $|0000\rangle + |0001\rangle$ where the rightmost bit is q[0]).
    *   Step 2: `CNOT(q[0], q[1])`. Control is q[0], target is q[1]. If q[0] is |1>, flip q[1].
        *   $|0000\rangle$ -> $|0000\rangle$
        *   $|0001\rangle$ -> $|0011\rangle$ (flipping the second bit from right, i.e., q[1]).
        *   Overall state: $\frac{1}{\sqrt{2}}(|0000\rangle + |0011\rangle)$.
        *   *Wait, The predicted output `|1100>: 0.5`.* Let's look at the bitstring mapping in `--probs`. "indexed by measurement bitstring (earlier measured qubit = higher bit)".
        *   Measurements: `M(q[0])` (highest bit in index), `M(q[1])` (next), `M(q[2])`, `M(q[3])` (lowest bit).
        *   So the index is `M(q[0]) M(q[1]) M(q[2]) M(q[3])`.
        *   State 1: q[0]=0, q[1]=0, q[2]=0, q[3]=0. Index: 0000.
        *   State 2: q[0]=1, q[1]=1, q[2]=0, q[3]=0. Index: 1100.
        *   This perfectly matches the Dirac notation logic if we map the measurement bitstrings to the values.

3.  **Draft the Reasoning (incorporating constraints):**
    *   *Goal:* Create a Bell state (maximally entangled pair) between q[0] and q[1] while keeping q[2] and q[3] in |0>.
    *   *Qubits:* 4 qubits total, all measured.
    *   *Evolution:*
        *   Initial: $|0000\rangle$.
        *   H(q[0]): Transforms q[0] to $|+\rangle$, yielding $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes |0\rangle \otimes |00\rangle = \frac{1}{\sqrt{2}}(|0000\rangle + |1000\rangle)$ (in q[0]-q[3] order). Let's use the exact bitstrings from the prompt.
        *   Let's just write: `H(q[0])` creates $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)_{q0} \otimes |000\rangle_{q1,q2,q3}$.
        *   `CNOT(q[0], q[1])` entangles them: $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)_{q0,q1} \

## isqTrain/3155

- task_id: `isqTrain/3155`
- task_type: `code_generation`
- category: `bell_state_preparation`
- difficulty: `basic`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2696`

### Prompt

I need an isQ program to an isQ program: create entangled pair between q[0] and q[4] in a 5-qubit register. Other qubits stay |0>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a Bell (maximally entangled) pair between q[0] and q[4] in a 5-qubit register, leaving q[1], q[2], q[3] in |0⟩.
2. **Qubits**: 5 qubits declared (q[0]–q[4]); all 5 are measured.
3. **State evolution**:
   - Initialize: |ψ₀⟩ = |00000⟩
   - H(q[0]): |ψ₁⟩ = (|0⟩ + |1⟩)/√2 ⊗ |0000⟩ = (|00000⟩ + |10000⟩)/√2
   - CNOT(q[0], q[4]): |ψ₂⟩ = (|00000⟩ + |10001⟩)/√2 — the control q[0] being |1⟩ flips target q[4]
4. **Expected probabilities**: The final state is an equal superposition of two computational basis states. Measurement yields |00000⟩ with probability |1/√2|² = 0.5 and |10001⟩ with probability 0.5.
