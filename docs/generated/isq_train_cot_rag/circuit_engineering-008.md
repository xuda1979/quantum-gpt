# ISQ training COT RAG corpus: circuit_engineering shard 8

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1039

- task_id: `isqTrain/1039`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `basic`
- concept_tags: `circuit_optimization`, `global_phase`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3160`

### Prompt

帮我写一个isQ程序：implements the pre_measurement_opt pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare |11⟩ state using X gates on both qubits, then measure in reversed order (q[1] first, q[0] second).
2. **Qubits**: 2 qubits (q[0], q[1]), both measured.
3. **State evolution**:
   - Initial: |00⟩
   - After X(q[0]): |10⟩
   - After X(q[1]): |11⟩
   - Diagonal gates (S, Rz, Z) are optimized out as they only add phases, not affecting measurement probabilities.
4. **Measurement ordering**: M(q[1]) is measured first (becomes higher bit), M(q[0]) second (becomes lower bit). With state |11⟩, q[1]=1 (bit 1) and q[0]=1 (bit 0), yielding bitstring |11⟩.
5. **Expected result**: {|11⟩: 1.0} since the state is deterministically |11⟩.

## isqTrain/4371

- task_id: `isqTrain/4371`
- task_type: `output_prediction`
- category: `circuit_engineering`
- difficulty: `difficult`
- concept_tags: `basis_change`, `circuit_optimization`, `global_phase`
- source: `isq_train_cot`
- dataset_index: `2994`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;
qbit q[1];

// Optimized: H*X*H = Z (conjugation identity)
procedure main() {
    // Set qubit to |1>
    X(q[0]);
    // Replace H-X-H pattern with Z gate
    Z(q[0]);
    // Z|1> = -|1>, global phase is unobservable
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations applied**: The circuit applies a sequence of three gates to a single qubit: X, Z, and X, followed by a measurement.
2. **State evolution**:
   - Initial state: |0>
   - After X gate: |1>
   - After Z gate: -|1> (global phase applied, state effectively remains |1>)
   - After second X gate: |0>
3. **Final state before measurement**: |0>
4. **Predicted probabilities**: The measurement outcome is deterministically 0 because the final state is exactly |0>.

Predicted probability distribution: {|0>: 1.0}

### Reference answer

{'predicted_probs': {'0': 1.0}, 'explanation': 'This isQ program operates on 1 qubit(s). The measurement probability distribution is: P(|0>) = 1.0000.'}

## isqTrain/2048

- task_id: `isqTrain/2048`
- task_type: `output_prediction`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `circuit_optimization`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5545`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[2];
procedure main() {
    X(q[0]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initial state**: The 2-qubit system starts in the ground state |00>.
2. **Operations**: 
   - `X(q[0])`: Applies the Pauli-X gate (bit-flip) to the first qubit.
3. **State evolution**: 
   - Initial: |00>
   - After `X(q[0])`: |10>
4. **Final state**: The quantum state is deterministically prepared in |10>. Measuring both qubits yields '10' with certainty.

Predicted probability distribution: {'10': 1.0}

### Reference answer

{'predicted_probs': {'10': 1.0}, 'explanation': 'CNOT-CNOT and X-X-X cancellation. State |10>, index 2, P=1.0.'}
