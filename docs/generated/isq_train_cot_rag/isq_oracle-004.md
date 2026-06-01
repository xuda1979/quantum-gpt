# ISQ training COT RAG corpus: isq_oracle shard 4

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/209

- task_id: `isqTrain/209`
- task_type: `code_generation`
- category: `isq_oracle`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1135`

### Prompt

Write isQ code for the following quantum task: implements the oracle_boolean pattern but with a different initial state preparation (flip q[[0]] -> q[1]).

### Chain-of-thought reasoning

## Reasoning
1. Goal: Implement an XOR oracle with initial state preparation that flips q[1] to |1⟩.
2. Qubits: 3 total (q[0], q[1] for inputs, anc[0] for oracle output). All 3 are measured.
3. State evolution:
   - Initial: |000⟩
   - After X(q[1]): |010⟩ (q[1] flipped to |1⟩)
   - After xor_oracle: Computes q[0] XOR q[1] = 0 XOR 1 = 1, storing in anc[0]
   - Final: |011⟩
4. Since the final state is deterministically |011⟩, measurement yields {|011⟩: 1.0}.

## isqTrain/220

- task_id: `isqTrain/220`
- task_type: `output_prediction`
- category: `isq_oracle`
- difficulty: `difficult`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_deriving_gate`, `isq_syntax_procedures`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `612`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;

oracle bool[1] grover_oracle(bool x[2]) {
    bool res[] = [x[0] && x[1]];
    return res;
}

qbit q[2];
qbit anc[1];

procedure my_z(qbit a) {
    Z(a);
} deriving gate

procedure main() {
    X(anc[0]);
    H(anc[0]);
    H(q[0]); H(q[1]);
    grover_oracle(q, anc);
    H(q[0]); H(q[1]);
    X(q[0]); X(q[1]);
    ctrl my_z(q[0], q[1]);
    X(q[0]); X(q[1]);
    H(q[0]); H(q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

Let me analyze this isQ program step by step.

The program implements a single iteration of Grover's algorithm for a 2-qubit search space.

1. **Oracle**: `grover_oracle` marks the state |11⟩ (when x[0] AND x[1] are both true)

2. **Quantum state evolution**:

**Initial state**: |00⟩|0⟩ (q[0], q[1], anc[0])

**After X(anc[0])**: |00⟩|1⟩

**After H(anc[0])**: |00⟩(|0⟩ - |1⟩)/√2

**After H(q[0]), H(q[1])**: (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2 ⊗ (|0⟩ - |1⟩)/√2

**After grover_oracle**: The oracle applies a phase flip to |11⟩ because the oracle returns true when x[0] && x[1]. So it flips the ancilla when the state is |11⟩:
(|00⟩ + |01⟩ + |10⟩ - |11⟩)/2 ⊗ (|0⟩ - |1⟩)/√2

Now we can ignore the ancilla since it's not entangled with the main qubits in a problematic way.

The state of q[0], q[1] is: (|00⟩ + |01⟩ + |10⟩ - |11⟩)/2

**After H(q[0]), H(q[1])**:
Let me compute this transformation.

H⊗2 (|00⟩ + |01⟩ + |10⟩ - |11⟩)/2

H|0⟩ = (|0⟩ + |1⟩)/√2
H|1⟩ = (|0⟩ - |1⟩)/√2

H⊗2|00⟩ = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2
H⊗2|01⟩ = (|00⟩ - |01⟩ + |10⟩ - |11⟩)/2
H⊗2|10⟩ = (|00⟩ + |01⟩ - |10⟩ - |11⟩)/2
H⊗2|11⟩ = (|00⟩ - |01⟩ - |10⟩ + |11⟩)/2

Sum: (|00⟩ + |01⟩ + |10⟩ + |11⟩ + |00⟩ - |01⟩ + |10⟩ - |11⟩ + |00⟩ + |01⟩ - |10⟩ - |11⟩ - |00⟩ + |01⟩ + |10⟩ - |11⟩)/2

= (|00⟩ + |01⟩ + |10⟩ + |11⟩ + |00⟩ - |01⟩ + |10⟩ - |11⟩ + |00⟩ + |01⟩ - |10⟩ - |11⟩ - |00⟩ + |01⟩ + |10⟩ - |11⟩)/2

Let me redo this more carefully:
Coefficients:
|00⟩: 1 + 1 + 1 - 1 = 2
|01⟩: 1 - 1 + 1 + 1 = 2
|10⟩: 1 + 1 - 1 + 1 = 2
|11⟩: 1 - 1 - 1 - 1 = -2

Wait, let me redo:

For the state (|00⟩ + |01⟩ + |10⟩ - |11⟩)/2:

Applying H⊗2:
Each basis state gets transformed:
|00⟩ → (|0⟩+|1⟩)(|0⟩+|1⟩)/2
|01⟩ → (|0⟩+|1⟩)(|0⟩-|1⟩)/2
|10⟩ → (|0⟩-|1⟩)(|0⟩+|1⟩)/2
|11⟩ → (|0⟩-|1⟩)(|0⟩-|1⟩)/2

So H⊗2[(|00⟩ + |01⟩ + |10⟩ - |11⟩)/2] =

(|0⟩+|1⟩)(|0⟩+|1⟩)/4 + (|0⟩+|1⟩)(|0⟩-|1⟩)/4 + (|0⟩-|1⟩)(|0⟩+|1⟩)/4 - (|0⟩-|1⟩)(|0⟩-|1⟩)/4

Let me expand each term:
First term: (|00⟩+|01⟩+|10⟩+|11⟩)/4
Second term: (|00⟩-|01⟩+|10⟩-|11⟩)/4
Third term: (|00⟩+|01⟩-|10⟩-|11⟩)/4
Fourth term: -( |00⟩-

### Reference answer

{'predicted_probs': {'3': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/76. Dimension: predict probabilities for reference circuit.'}
