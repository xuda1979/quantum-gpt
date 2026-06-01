# ISQ training COT RAG corpus: isq_array_ops shard 2

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/265

- task_id: `isqTrain/265`
- task_type: `code_generation`
- category: `isq_array_ops`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `1716`

### Prompt

Create an isQ quantum circuit that implements a compact variant of the gate_decomposition pattern using p[3] -> p[2]. The circuit should use a reduced qubit register.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement a compact gate decomposition pattern using a reduced 2-qubit register p instead of 3, with CNOT entangling p and q registers.

2. **Qubits**: 5 total — p[0], p[1] (control register), q[0], q[1], q[2] (target register); all measured.

3. **State evolution**:
   - Initial: |00000⟩ (p[0], p[1], q[0], q[1], q[2])
   - After `X(p)`: |11000⟩ — both p qubits flipped to |1⟩
   - After `CNOT(p, q)`: The CNOT with array arguments applies pairwise control (p[0]→q[0], p[1]→q[1]), flipping q[0] and q[1] since their controls are

## isqTrain/264

- task_id: `isqTrain/264`
- task_type: `code_generation`
- category: `isq_array_ops`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `47`

### Prompt

Implement a quantum circuit in isQ: implements a variant of the gate_decomposition pattern using p[3] -> p[4]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Prepare a 7-qubit entangled state where all qubits are in |1⟩ by applying X gates and CNOT correlations between two registers.

**Qubits:** 7 total (p[0-3], q[0-2]); all are measured, yielding a 7-bit outcome.

**State evolution:**
1. **Initial:** |0⟩⁷ = |0000000⟩
2. **X(p):** Flips all 4 p-qubits → |1111⟩⊗|000⟩ = |1111000⟩
3. **CNOT(p, q):** Each p[i] (i=0,1,2) controls q[i]; since all controls are |1⟩, all three targets flip → |1111111⟩

**Result:** The final state is |1111111⟩, so measurement yields bitstring 1111111 with probability 1.0.

## isqTrain/259

- task_id: `isqTrain/259`
- task_type: `code_generation`
- category: `isq_array_ops`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `1547`

### Prompt

Implement a quantum circuit in isQ: implements the gate_decomposition pattern but with a different initial state preparation (flip q[[2, 3]] -> q[0]).

### Chain-of-thought reasoning

## Reasoning
1. Goal: Create an equal superposition on q[0] and q[1], then apply X gate to flip q[0] as the modified initial state preparation.
2. Qubits: 4 qubits (q[0]-q[3]) declared, all 4 measured at the end.
3. State evolution:
   - Initial: |0000⟩
   - After H(q[0]): (|0000⟩ + |1000⟩)/√2
   - After H(q[1]): (|0000⟩ + |0100⟩ + |1000⟩ + |1100⟩)/2
   - After X(q[0]): (|1000⟩ + |1100⟩ + |0000⟩ + |0100⟩)/2
4. The final state is an equal superposition of |0000⟩, |0100⟩, |1000⟩, and |1100⟩, each with amplitude 1/2, giving probability 0.25 for each basis state.

## isqTrain/266

- task_id: `isqTrain/266`
- task_type: `code_generation`
- category: `isq_array_ops`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `5066`

### Prompt

I need an isQ program to implements a compact variant of the gate_decomposition pattern using q[3] -> q[2]. The circuit should use a reduced qubit register.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Create a 5-qubit state where all qubits are |1⟩ using X gates on one register and CNOT gate to propagate to a second register.

2. **Qubits**: 5 total — p[0], p[1], p[2] and q[0], q[1] — all measured.

3. **State evolution**:
   - Initial: |000⟩_p ⊗ |00⟩_q = |00000⟩
   - After `X(p)`: Applies X to each qubit in p → |111⟩_p ⊗ |00⟩_q = |11100⟩
   - After `CNOT(p, q)`: Element-wise CNOTs (CNOT(p[0],q[0]), CNOT(p[1],q[1])) flip q bits since p[0]=|1⟩, p[1]=|1⟩ → |111⟩_p ⊗ |11⟩_q = |11111⟩

4. **Final state** |11111⟩ yields measurement probability 1.0 for outcome |11111⟩ (bitstring 11111).

## isqTrain/2552

- task_id: `isqTrain/2552`
- task_type: `code_equivalence`
- category: `isq_array_ops`
- difficulty: `intermediate`
- concept_tags: `global_phase`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3546`

### Prompt

Determine if these two isQ implementations are functionally equivalent:

Version A:
```isq
import std;

qbit p[3];
qbit q[3];

procedure main() {
    X(p);
    CNOT(p, q);
    M(p[0]); M(p[1]); M(p[2]); M(q[0]); M(q[1]); M(q[2]);
}

```

Version B:
```isq
import std;

qbit p[3];
qbit q[3];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    X(p);
    CNOT(p, q);
    M(p[0]); M(p[1]); M(p[2]); M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A**: Applies the X gate to all qubits in array `p`, changing their state from |000> to |111>. Then applies CNOT with `p` as the control and `q` as the target, flipping all qubits in `q` to |111>. The final combined state is |111111>.
2. **Program B**: Applies a global phase `GPhase(0.0)` to the initial |000000> state (which multiplies the state vector by $e^{i0} = 1$, effectively doing nothing). It then applies the exact same X and CNOT gates as Program A, resulting in the identical final state |111111>.
3. **Key Difference**: Program B contains the operation `GPhase(0.0)` which is absent in Program A.
4. **Measurement Probabilities**: The measurement probability distributions are exactly the same. A global phase of 0.0 is a trivial identity transformation, leaving the quantum state mathematically and physically unchanged.
5. **Verdict**: Yes

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/1923

- task_id: `isqTrain/1923`
- task_type: `output_prediction`
- category: `isq_array_ops`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3478`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit p[3];
qbit q[3];
procedure main() {
    X(p);
    CNOT(p, q);
    M(p[0]); M(p[1]); M(p[2]); M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The 6-qubit system starts in the initial state $|000000\rangle$.
2. `X(p)` applies

### Reference answer

{'predicted_probs': {'111111': 1.0}, 'explanation': 'Two-array broadcasting.'}
