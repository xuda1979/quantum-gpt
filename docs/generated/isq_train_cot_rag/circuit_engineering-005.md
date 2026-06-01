# ISQ training COT RAG corpus: circuit_engineering shard 5

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1041

- task_id: `isqTrain/1041`
- task_type: `output_prediction`
- category: `circuit_engineering`
- difficulty: `basic`
- concept_tags: `circuit_optimization`, `global_phase`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3540`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[2];

// Optimized: removed S, Rz, Z before measurement
procedure main() {
    // Set both qubits to |1>
    X(q[0]);
    X(q[1]);
    // Removed: S(q[0]), Rz(q[1]), Z(q[0])
    // All are diagonal gates (phase-only), no effect on probs
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations:** The circuit initializes two qubits in |00> and applies the X gate to both `q[0]` and `q[1]`.
2. **Evolution:** The state transitions from |00> to |10> after X(q[0]), and then to |11> after X(q[1]).
3. **Final state:** The system is deterministically in the state |11>.
4. **Distribution:** Measurement yields '11' with certainty.

Predicted probability distribution: {|11>: 1.0}

### Reference answer

{'predicted_probs': {'3': 1.0}, 'explanation': 'Parametric variant of isqEval/319. Dimension: predict probabilities for reference circuit.'}

## isqTrain/1013

- task_id: `isqTrain/1013`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `circuit_optimization`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3227`

### Prompt

Code this in isQ: implements a variant of the gate_consolidation pattern using q[1] -> q[3]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Implement gate consolidation on qubits q[1]-q[3] with an expanded register where extra qubits remain in |0⟩.
2. Need larger register (e.g., q[8]); measure q[1], q[2], q[3] (3 qubits).
3. State evolution:
   - Initial state: |00000000⟩
   - X(q[1]): |01000000⟩ — flips qubit 1 to |1⟩
   - Consolidated Rz(π/2, q[1]): applies phase e^(iπ/2) = i to the |1⟩ component → i|01000000⟩
   - Rz adds only a global phase to computational basis states, leaving measurement outcomes unchanged
4. Expected probabilities: P(|100⟩) = 1.0 for q[1]=1, q[2]=0, q[3]=0; remaining qubits stay |0⟩ unmeasured.

## isqTrain/1043

- task_id: `isqTrain/1043`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `expert`
- concept_tags: `circuit_optimization`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2571`

### Prompt

帮我写一个isQ程序：implements a variant of the solovay_kitaev pattern using q[1] -> q[3]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a Solovay-Kitaev variant decomposing Z into T^4 on q[1], using an expanded 4-qubit register with q[0] idle.
2. **Qubits**: 4 qubits (q[0]-q[3]); measuring q[1], q[2], q[3].
3. **State evolution**: |0000⟩ → X(q[1]) → |0100⟩ → T(q[1])×4 → e^{iπ}|0100⟩ (T^4 = Z applies π phase to |1⟩).
4. **Final measurement**: Z phase is unobservable; q[1]=1, q[2]=0, q[3]=0 → P(|100⟩) = 1.0.

## isqTrain/2052

- task_id: `isqTrain/2052`
- task_type: `output_prediction`
- category: `circuit_engineering`
- difficulty: `difficult`
- concept_tags: `basis_change`, `circuit_optimization`, `entanglement`
- source: `isq_train_cot`
- dataset_index: `2649`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit q[2];
procedure main() {
    X(q[1]);
    CNOT(q[1], q[0]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Analyze the given isQ program and predict the probability distribution.
    *   Output format: "## Circuit Analysis" followed by step-by-step reasoning (3-15 lines), ending with the predicted probability distribution.
    *   Constraint: Concise, use Dirac notation, no code blocks, specific structure.

2.  **Analyze the isQ Code:**
    *   `qbit q[2];`: Initializes 2 qubits, `q[0]` and `q[1]`, both in state `|0>`. Combined state is `|00>`.
    *   `X(q[1]);`: Applies Pauli-X gate to `q[1]`.
        *   Initial state: `|00>` (where the rightmost bit is usually the last index or depending on tensor product order. In isQ, usually standard q[0], q[1] -> `|q[1]q[0]>` or `|q[0]q[1]>`). Let's use `|q[1]> \otimes |q[0]>`.
        *   `X(q[1])` changes `q[1]` from `|0>` to `|1>`. State becomes `|10>` (i.e., `|1> \otimes |0>`).
    *   `CNOT(q[1], q[0]);`: CNOT with `q[1]` as control and `q[0]` as target.
        *   Current state: `|10>`. Control `q[1]` is `|1>`, so target `q[0]` is flipped.
        *   `q[0]` goes from `|0>` to `|1>`.
        *   State becomes `|11>`.
    *   `M(q[0]); M(q[1]);`: Measures both qubits.
        *   Result will deterministically be `11` (since state is `|11>`).
        *   Wait, let's double check bitstring indexing for the predicted output. "earlier measured qubit = higher bit". So `M(q[0])` is the higher bit, `M(q[1])` is the lower bit.
        *   If `q[0] = 1` and `q[1] = 1`, bitstring is `11` (q[0]=1, q[1]=1).

3.  **Draft the Step-by-Step Reasoning:**
    *   Initial state: `|00>` (q[0]=0, q[1]=0).
    *   `X(q[1])`: Flips `q[1]` to `|1>`. State becomes `|10>` (in terms of `q[1]q[0]`), or generally `|0>_q0 |1>_q1`.
    *   `CNOT(q[1], q[0])`: Control is `q[1]` (which is `|1>`), target is `q[0]`. Flips `q[0]` to `|1>`. State becomes `|1>_q0 |1>_q1`.
    *   Measurements `M(q[0])` and `M(q[1])` collapse the state `|11>`.
    *   The bitstring is formed with `q[0]` as the higher bit and `q[1]` as the lower bit, yielding "11" with probability 1.0.

4.  **Refine the Output:**
    *   Keep it concise (3-8 lines).
    *   Ensure correct notation.
    *   End with exact probability distribution format: `Predicted probability distribution: {'11': 1.0}` (matching the expected).

5.  **Final Review of the Output Text:**
    ## Circuit Analysis
    1. The circuit initializes two qubits, q[0] and q[1], in the state |00>.
    2. The `X(q[1])` gate flips q[1] from |0> to |1>, changing the state to |0>⊗|1>.
    3. The `CNOT(q[1], q[0])` gate uses q[1] as the control and q[0] as the target. Since q[1] is |1>, it flips q[0] from |0> to |1>.
    4. The system is now in the entangled state |1>⊗|1>.
    5. Measuring both qubits yields the state |1> for each, corresponding to the bitstring '11' with certainty.

    Predicted probabilities: {'11': 1.0}
    (Wait, expected

### Reference answer

{'predicted_probs': {'11': 1.0}, 'explanation': 'CNOT reversal identity. State |11>, index 3, P=1.0.'}

## isqTrain/1006

- task_id: `isqTrain/1006`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `circuit_optimization`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2845`

### Prompt

Implement the following in isQ: implements a variant of the gate_cancellation pattern using q[2] -> q[4]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a gate_cancellation variant on an expanded 4-qubit register, where net operations reduce to a single X gate on q[0].
2. **Qubits**: 4 qubits (q[0]-q[3]), all measured; predicted output state |1000⟩.
3. **State evolution**:
   - Initial: |0000⟩
   - X(q[0]): flips q[0] from |0⟩ to |1⟩ → |1000⟩
   - No other gates applied (CNOT-CNOT pair cancelled, triple X reduced to single X)
4. **Expected probabilities**: {|1000⟩: 1.0} — single X gate produces deterministic |1000⟩ state.

## isqTrain/1022

- task_id: `isqTrain/1022`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `difficult`
- concept_tags: `basis_change`, `circuit_optimization`, `global_phase`
- source: `isq_train_cot`
- dataset_index: `5678`

### Prompt

帮我写一个isQ程序：implements the template_matching_opt pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a template-matching optimization pattern demonstrating H*X*H → Z substitution and X-X gate cancellation.
2. **Qubits**: 1 qubit (q[0]) is measured.
3. **State evolution**:
   - |0⟩ → X → |1⟩ (initialize to |1⟩)
   - |1⟩ → Z → -|1⟩ (Z on |1⟩ adds global phase; replaces H*X*H)
   - -|1⟩ → X → -|0⟩ (bit flip)
   - -|0⟩ → X → -|1⟩ (second X cancels the first: X*X = I)
4. **Final state**: -|1⟩ ≡ |1⟩ (global phase is unobservable).
5. **Expected probabilities**: P(|1⟩) = 1.0, since measurement yields |1⟩ with certainty.

## isqTrain/1055

- task_id: `isqTrain/1055`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `qubit_mapping`
- source: `isq_train_cot`
- dataset_index: `3745`

### Prompt

帮我写一个isQ程序：implements the sabre_routing pattern using an alternative gate decomposition (CNOT -> H CZ H). The circuit must produce the same output as the standard decomposition.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for a quantum circuit that implements a "sabre_routing pattern" using an alternative gate decomposition (CNOT -> H CZ H).

Let me analyze the circuit:

1. **Goal**: Implement a CNOT between non-adjacent qubits using swap (three-CNOT decomposition) gates for routing, with CNOT decomposed as H-CZ-H on the target.

2. **Qubits**: 3 qubits (q[0], q[1], q[2]), all measured.

3. **State evolution**:
   - Initial state: |000>
   - X(q[0]): |100>
   - swap (three-CNOT decomposition)(q[0], q[1]): |010> (using H-CZ-H decomposition for each CNOT in swap (three-CNOT decomposition))
   - The swap operation (three-CNOT decomposition) is decomposed as 3 CNOTs, each further decomposed as H-CZ-H
   - H(q[2]): |01> ⊗ (|0> + |1>)/√2 = (|010> + |011>)/√2
   - CZ(q[1], q[2]): Since q[1] is |1>, this applies Z to q[2], flipping |+> to |->
     - (|010> - |011>)/√2
   - H(q[2]): Converts |-> back to |1>
     - |011>
   - swap (three-CNOT decomposition)(q[0], q[1]): |101>
   - Final state: |101>

Wait, let me trace through more carefully.

Initial: |000>
X(q[0]): |100>

swap (three-CNOT decomposition)(q[0], q[1]):
The swap (three-CNOT decomposition) is implemented with H-CZ-H decomposition for CNOTs.
swap (three-CNOT decomposition) = CNOT(a,b) CNOT(b,a) CNOT(a,b)

For the first CNOT(a,b) where a=q[0], b=q[1]:
- H(b): |100> → |1> ⊗ H|0> ⊗ |0> = |1> ⊗ (|0>+|1>)/√2 ⊗ |0> = (|100>+|110>)/√2
- CZ(a,b): control is q[0]=|1>, so applies Z to q[1]
  - Z(|0>+|1>)/√2 = (|0>-|1>)/√2
  - State: (|100>-|110>)/√2
- H(b): H(|0>-|1>)/√2 = |1>
  - State: |110>

For the second CNOT(b,a) where b=q[1], a=q[0]:
- H(a): |110> → H|1> ⊗ |1> ⊗ |0> = (|0>-|1>)/√2 ⊗ |1> ⊗ |0> = (|010>-|110>)/√2
- CZ(b,a): control is q[1]=|1>, so applies Z to q[0]
  - Z(|0>-|1>)/√2 = (|0>+|1>)/√2 = |+>
  - State: (|010>+|110>)/√2
- H(a): H(|0>+|1>)/√2 = H|+> = |0>
  - State: |010>

For the third CNOT(a,b) where a=q[0], b=q[1]:
- H(b): |010> → |0> ⊗ (|0>+|1>)/√2 ⊗ |0> = (|000>+|010>)/√2... wait that's wrong.

Let me redo this. |010> = |0>₀ ⊗ |1>₁ ⊗ |0>₂

H(q[1]): |0>₀ ⊗ (|0>+|1>)/√2 ⊗ |0>₂ = (|000>+|010>)/√2

Hmm wait, I'm confusing myself. Let me be more careful with the qubit ordering.

State |q[0], q[1], q[2]>

Initial: |000>
X(q[0]): |100>

Now swap (three-CNOT decomposition)(q[0], q[1]) with the H-CZ-H decomposition:

The code shows:

H(b);      // H(q[1])
CZ(a, b);  // CZ(q[0], q[1])
H(b);      // H(q[1])
H(a);      // H(q[0])
CZ(b, a);  // CZ(q[1], q[0])
H(a);      // H(q[0])
H(b);      // H(q[1])
CZ(a, b);  // CZ(q[0], q[1])
H(b);      // H(q[1])
``

## isqTrain/1008

- task_id: `isqTrain/1008`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `circuit_optimization`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4375`

### Prompt

Implement the following in isQ: implements the gate_cancellation pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
Goal: Demonstrate gate cancellation awareness by showing that three consecutive X gates reduce to a single X (since X² = I, thus X³ = X), producing state |10⟩ from |00⟩.

Two qubits q[0] and q[1] are used; both are measured.

State evolution: |00⟩ →X(q[0])→ |10⟩ →X(q[0])→ |00⟩ →X(q[0])→ |10⟩. The three X gates on q[0] net to one X (X·X·X = X). Qubit q[1] remains unaltered in |0⟩.

Final state |10⟩ yields measurement probabilities {|10⟩: 1.0}, as confirmed by measuring both qubits.

## isqTrain/1037

- task_id: `isqTrain/1037`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `basic`
- concept_tags: `circuit_optimization`, `global_phase`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4259`

### Prompt

帮我写一个isQ程序：implements a variant of the pre_measurement_opt pattern using q[2] -> q[4]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement a pre_measurement_opt variant with an expanded 4-qubit register, optimizing by removing diagonal phase gates before measurement.

2. **Qubits**: 4 qubits (q[0]-q[3]), all measured; q[2] and q[3] remain in ground state |0⟩.

3. **State evolution**:
   - Initial: |0000⟩
   - X(q[0]): |1000⟩
   - X(q[1]): |1100⟩
   - q[2], q[3] untouched: remain |0⟩
   - Final state: |1100⟩

4. **Expected probabilities**: {|1100⟩: 1.0} — diagonal gates (S, Rz, Z) only add global/relative phases, which don't affect measurement probabilities, so they can be safely removed.

## isqTrain/1064

- task_id: `isqTrain/1064`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `qubit_mapping`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2175`

### Prompt

帮我写一个isQ程序：implements the vf2_mapping pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a VF2-mapped circuit with an explicit X-X identity pair to demonstrate gate cancellation awareness.
2. **Qubits**: 3 qubits (q[0], q[1], q[2]), all measured; VF2 mapping assigns logical a→q[0], b→q[1], c→q[2] with zero SWAPs due to direct connectivity.
3. **State evolution**:
   - Initialize: |000⟩
   - X(q[0]): |100⟩
   - X(q[1]): |110⟩
   - CNOT(q[0], q[2]) (control=1, flips q[2]): |111⟩
   - CNOT(q[1], q[2]) (control=1, flips q[2] back): |110⟩
   - X(q[0]): |010⟩
   - X(q[0]) (identity pair cancels): |110⟩
4. **Final state**: |110⟩ — the X-X pair is identity (X²=I), so it has no net effect.
5. **Measurement**: Probabilities {|110⟩: 1.0} since the final state is a computational basis state.
