# ISQ training COT RAG corpus: circuit_engineering shard 2

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1016

- task_id: `isqTrain/1016`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `circuit_optimization`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `762`

### Prompt

用isQ实现implements the gate_consolidation pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Demonstrate gate consolidation by merging consecutive Rz rotations and showing H-H identity cancellation before measurement.
2. **Qubits**: 1 qubit (`q[0]`), which is measured.
3. **State evolution**:
   - `|0⟩` → **X** → `|1⟩`
   - `|1⟩` → **Rz(π/2)** → `e^{iπ/4}|1⟩` (Rz only adds phase to computational basis states)
   - `e^{iπ/4}|1⟩` → **H** → `e^{iπ/4}|-⟩`
   - `e^{iπ/4}|-⟩` → **H** → `e^{iπ/4}|1⟩` (H∘H = I, so the pair cancels to identity)
   - **M** measures in computational basis, yielding `|1⟩` with certainty
4. **Expected probabilities**: `{|1⟩: 1.0}` because the H-H pair cancels to identity and Rz only adds a global phase that doesn't affect measurement outcomes.

## isqTrain/1060

- task_id: `isqTrain/1060`
- task_type: `output_prediction`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_deriving_gate`, `isq_syntax_procedures`, `qubit_mapping`
- source: `isq_train_cot`
- dataset_index: `3398`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;

// SWAP gate for routing
procedure swap_gate(qbit a, qbit b) {
    CNOT(a, b);
    CNOT(b, a);
    CNOT(a, b);
} deriving gate

qbit q[3];

// Routed: SWAP-CNOT-SWAP pattern for non-adjacent CNOT
procedure main() {
    // Set q[0] to |1>
    X(q[0]);
    // Route: swap q[0] to q[1] position
    swap_gate(q[0], q[1]);
    // Now original q[0] data is at physical q[1], adjacent to q[2]
    CNOT(q[1], q[2]);
    // Restore: swap q[0] and q[1] back
    swap_gate(q[0], q[1]);
    // Final state: q[0]=1, q[1]=0, q[2]=1 => |101>
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The initial state of the 3-qubit system is |000>. Applying `X(q[0])` flips the first qubit to |1>, evolving the state to |100>.
2. The `swap_gate(q[0], q[1])` swaps the states of q[0] and q[1

### Reference answer

{'predicted_probs': {'5': 1.0}, 'explanation': 'Parametric variant of isqEval/322. Dimension: predict probabilities for reference circuit.'}

## isqTrain/1026

- task_id: `isqTrain/1026`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `difficult`
- concept_tags: `basis_change`, `circuit_optimization`, `entanglement`
- source: `isq_train_cot`
- dataset_index: `5234`

### Prompt

Create an isQ quantum circuit that implements a variant of the clifford_optimization pattern using q[2] -> q[3]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

The task asks me to write an isQ program for a variant of clifford_optimization pattern using q[2] -> q[3]. Let me analyze this.

The circuit should 3 qubits (q[0], q[1], q[2]) and implements a CNOT direction reversal pattern. The predicted output |110> with probability 1.0.

Now I need to create a variant using q[2] -> q[3], meaning I should use an expanded qubit register. Let me think about what this means:
- The reference uses CNOT(q[1], q[0]) with X(q[1]) to prepare |1>
- A variant using q[2] -> q[3] would mean I need at least 4 qubits

The clifford optimization pattern demonstrates that H*H*CNOT*H*H = CNOT with swapped control/target.

Let me create a circuit with 4 qubits where:
1. Initialize q[2] to |1> using X gate
2. Use CNOT(q[2], q[3]) pattern
3. Measure appropriate qubits

Wait, the predicted output show |110>: 1.0 with 3 qubits measured. But if I'm using q[2] -> q[3], I might need 4 qubits.

Let me re-read the task. It says "expanded qubit register compared to the base version" - the base has 3 qubits, so expanded would be 4 qubits.

The predicted output still |110>: 1.0 with 3 qubits measured. Hmm, but if I use 4 qubits and only measure 3, the bitstring interpretation changes.

Actually wait - let me re-read. the predicted output and number of qubits measured are given as part of the task constraints. So I need to:
1. Use 4 qubits (expanded from 3)
2. Use q[2] -> q[3] pattern
3. Get |110>: 1.0 measurement outcome on 3 measured qubits

Let me think about this more carefully. If I measure q[0], q[1], q[2] but the operations are on q[2] and q[3]:
- X(q[2]) prepares q[2] = |1>
- CNOT(q[2], q[3]) with q[2] = |1> flips q[3]
- But if I'm only measuring q[0], q[1], q[2], then q[3] isn't measured

If q[0] and q[1] start in |0>, and q[2] is set to |1>:
- State after X(q[2]): |0010> (4 qubits, q[2]=1)
- After CNOT(q[2], q[3]): |0011>
- Measuring q[0], q[1], q[2]: |010> in binary for the measured bits

Wait, that's not |110>. Let me reconsider the bit ordering.

In the --probs mode, "earlier measured qubit = higher bit". So if I measure M(q[0]), M(q[1]), M(q[2]):
- q[0] is the highest bit (bit 2)
- q[1] is the middle bit (bit 1)  
- q[2] is the lowest bit (bit 0)

So |110> means q[0]=1, q[1]=1, q[2]=0.

For The implementation with X(q[1]) and CNOT(q[1], q[0]):
- Initial: |000>
- After X(q[1]): |010>
- After CNOT(q[1], q[0]): |110> (q[1]=1 controls, q[0] flips)

So for my variant with q[2] -> q[3]:
- I need to produce |110> on the measured qubits
- Using 4 qubits, measuring some subset

If I measure q[0], q[1], q[2]:
- For |110>: q[0]=1, q[1]=1, q[2]=0

So I need:
- X(q[1]) to set q[1] = 1
- CNOT(q[2], q[3]) but q[2] should be 0 initially for this pattern
- Hmm, but the task says q[2] -> q[3]

Wait, maybe the variant means I should apply the same pattern but shifted to q[2] and q[3], while still measuring all 4 qubits? Or measure q[1], q[2], q[3]?

If I measure q[1], q[2], q[3] and want |110>:
- q[1]=

## isqTrain/1038

- task_id: `isqTrain/1038`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `basic`
- concept_tags: `circuit_optimization`, `global_phase`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3023`

### Prompt

Create an isQ quantum circuit that implements the pre_measurement_opt pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Demonstrate pre-measurement optimization by showing that phase-only gates (S, Z, Rz) before measurement don't affect probabilities, and that X-X pairs cancel to identity.
2. **Qubits**: 2 qubits (q[0], q[1]), both measured.
3. **State evolution**:
   - Initial: |00⟩
   - After X(q[0]): |10⟩
   - After X(q[1]): |11⟩
   - S(q[0]), Rz(q[1]), Z(q[0]) removed — these are diagonal gates adding only phases (e.g., Z|1⟩ = -|1⟩), which don't change measurement probabilities
   - X(q[0]) then X(q[0]): X² = I, so state remains |11⟩
4. **Expected probabilities**: {|11⟩: 1.0} — the circuit prepares |11⟩ with certainty since all phase operations and the X-X identity pair have no measurable effect.

## isqTrain/2051

- task_id: `isqTrain/2051`
- task_type: `output_prediction`
- category: `circuit_engineering`
- difficulty: `difficult`
- concept_tags: `basis_change`, `circuit_optimization`, `global_phase`
- source: `isq_train_cot`
- dataset_index: `1552`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[1];
procedure main() {
    X(q[0]);
    Z(q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations**: Applies an X gate followed by a Z gate to qubit q[0].
2. **Initial state**: The qubit starts in the |0> state.
3. **State evolution**: 
   - Applying the X gate flips the state: X|0> = |1>.
   - Applying the Z gate adds a global phase: Z|1> = -|1>.
4. **Final state**: The state before measurement is -|1>.
5. **Measurement probabilities**: Since the state is proportional to |1>, measuring in the computational basis yields outcome '1' with certainty.

**Predicted probabilities:** {'1': 1.0}

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Template H*X*H = Z applied to |1>. State |1>, P=1.0.'}

## isqTrain/1050

- task_id: `isqTrain/1050`
- task_type: `output_prediction`
- category: `circuit_engineering`
- difficulty: `basic`
- concept_tags: `qubit_mapping`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3343`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[2];

// Remapped: logical 0 -> physical 1, logical 1 -> physical 0
procedure main() {
    // X on logical q[0] -> physical q[1]
    X(q[1]);
    // CNOT(logical 0, logical 1) -> CNOT(physical 1, physical 0)
    CNOT(q[1], q[0]);
    // Measure both physical qubits
    // Both carry value 1 after the mapping
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit starts with two qubits initialized to |00⟩.
2. The X gate is applied to q[1], changing the state from |00⟩ to |10⟩.
3. A CNOT gate is executed with q[1] as the control and q[0] as the target.
4. Since the control q[1] is in the |1⟩ state, the target q[0] is flipped from |0⟩ to |1⟩.
5. The quantum state of the system becomes |11⟩.
6. Both qubits are measured, yielding a deterministic result.

Predicted probability distribution: {|11>: 1.0}

### Reference answer

{'predicted_probs': {'3': 1.0}, 'explanation': 'Parametric variant of isqEval/321. Dimension: predict probabilities for reference circuit.'}

## isqTrain/2055

- task_id: `isqTrain/2055`
- task_type: `output_prediction`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_deriving_gate`, `isq_syntax_procedures`, `qubit_mapping`
- source: `isq_train_cot`
- dataset_index: `1212`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
procedure swap_gate(qbit a, qbit b) {
    CNOT(a, b);
    CNOT(b, a);
    CNOT(a, b);
} deriving gate
qbit q[3];
procedure main() {
    X(q[0]);
    swap_gate(q[0], q[1]);
    CNOT(q[1], q[2]);
    swap_gate(q[0], q[1]);
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request**:
    *   Task: Analyze an isQ quantum program and predict the probability distribution of measurement outcomes.
    *   Format: "## Circuit Analysis" section, up to 15 lines (concise).
    *   Input circuit:
        *   Initialize `q[0], q[1], q[2]` to `|0>|0>|0>`
        *   `X(q[0])` -> `|1>|0>|0>`
        *   `swap(q[0], q[1])` -> `|0>|1>|0>`
        *   `CNOT(q[1], q[2])` -> `|0>|1>|1>`
        *   `swap(q[0], q[1])` -> `|1>|0>|1>`
    *   Output requirement: Predicted probability distribution {'101': 1.0} at the end.

2.  **Step-by-Step State Evolution**:
    *   Initial state: `|q[0], q[1], q[2]> = |000>`
    *   `X(q[0])`: Flips `q[0]` to `|1>`. State becomes `|100>`.
    *   `swap_gate(q[0], q[1])`: Swaps `q[0]` and `q[1]`. State becomes `|010>`.
    *   `CNOT(q[1], q[2])`: Control `q[1]`, Target `q[2]`. Since `q[1]` is `|1>`, `q[2]` flips to `|1>`. State becomes `|011>`.
    *   `swap_gate(q[0], q[1])`: Swaps `q[0]` and `q[1]` again. State becomes `|101>`.
    *   Measurements: `M(q[0]), M(q[1]), M(q[2])` correspond to bitstring `101` (if `q[0]` is the highest bit). Wait, the prompt says "(earlier measured qubit = higher bit)". The isQ code measures `M(q[0]); M(q[1]); M(q[2]);`. So `q[0]` is the highest bit, `q[2]` is the lowest bit. The state is `|q[0]=1, q[1]=0, q[2]=1>`, which means bitstring `101`.
    *   Probability: `101` with 100% probability.

3.  **Drafting the response**:
    *   Line 1: Initial state `|q[0]q[1]q[2]> = |000>`.
    *   Line 2: `X(q[0])` flips the first qubit to `|1>`, resulting in `|100>`.
    *   Line 3: `swap_gate(q[0], q[1])` exchanges qubits 0 and 1, state becomes `|010>`.
    *   Line 4: `CNOT(q[1], q[2])` flips qubit 2 since qubit 1 is `|1>`, state becomes `|011>`.
    *   Line 5: `swap_gate(q[0], q[1])` swaps qubits 0 and 1 again, state becomes `|101>`.
    *   Line 6: Measurements on `q[0], q[1], q[2]` will deterministically yield `101` (where `q[0]` is the highest bit).
    *   Line 7: Predicted probabilities: {'101': 1.0}

4.  **Refining constraints**:
    *   Concise, precise step-by-step reasoning.
    *   Use Dirac notation.
    *   Only the analysis starting with "## Circuit Analysis".
    *   End with the predicted probability distribution.

5.  **Final Polish**:
    ## Circuit Analysis
    1. Initial state is `|q[0]q[1]q[2]> = |000>`.
    2. `X(q[0])` flips qubit 0, evolving the state to `|100>`.
    3. `swap_gate(q[0], q[1])` swaps qubits 0 and 1, resulting in state `|010>`.
    4. `CNOT(q[1], q[2])` flips qubit 2 because qubit 1 is `|1>`, changing the state to `|011>`.
    5. `swap_gate(q[0], q[1])` swaps qubits 0 and 1 again, resulting in the final state `|101>`.

### Reference answer

{'predicted_probs': {'101': 1.0}, 'explanation': 'SABRE routing: SWAP-CNOT-SWAP for non-adjacent CNOT. |101>, index 5, P=1.0.'}

## isqTrain/1069

- task_id: `isqTrain/1069`
- task_type: `output_prediction`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `qubit_mapping`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5121`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[3];

// VF2 mapping: a->q[0], b->q[1], c->q[2]
// All CNOT pairs have direct connectivity, zero SWAPs needed
procedure main() {
    // Set logical inputs a=1, b=1
    X(q[0]);
    X(q[1]);
    // CNOT(a, c) -> CNOT(q[0], q[2]): flips q[2] to 1
    CNOT(q[0], q[2]);
    // CNOT(b, c) -> CNOT(q[1], q[2]): flips q[2] back to 0
    CNOT(q[1], q[2]);
    // Result: q[0]=1, q[1]=1, q[2]=0
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. Operations: X gates on q[0] and q[1], followed by CNOT(q[0], q[2]) and CNOT(q[1], q[2]).
2. State evolution:
   - Initial state: |000>
   - `X(q[0])`, `X(q[1])`: Flips the first two qubits to |1>, evolving the state to |110>.
   - `CNOT(q[0], q[2])`: Control q[0] is |1>, so target q[2] is flipped from |0> to |1>. State becomes |111>.
   - `CNOT(q[1], q[2])`: Control q[1] is |1>, so target q[2] is flipped back from |1> to |0>. State becomes |110>.
3. Final state: |110>
4. Predicted probabilities: {|110>: 1.0}

### Reference answer

{'predicted_probs': {'6': 1.0}, 'explanation': 'Parametric variant of isqEval/323. Dimension: predict probabilities for reference circuit.'}

## isqTrain/1009

- task_id: `isqTrain/1009`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `circuit_optimization`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2229`

### Prompt

Write an isQ program that implements the gate_cancellation pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Implement a gate-cancellation pattern with reversed measurement order to demonstrate how measurement sequence affects bitstring indexing.
2. Two qubits (q[0], q[1]) are used, both measured in reversed order: M(q[1]) first, then M(q[0]).
3. State evolution:
   - Initial state: |00⟩
   - After X(q[0]): |10⟩ (q[0] flips to |1⟩, q[1] remains |0⟩)
   - The CNOT-CNOT pair cancels (CNOT is self-inverse), and three X gates reduce to one X gate.
4. Measurement produces probability {|01⟩: 1.0} because:
   - M(q[1]) measured first → bit 1 (higher) = 0
   - M(q[0]) measured second → bit 0 (lower) = 1
   - Bitstring "01" corresponds to q[1]=0, q[0]=1, matching |10⟩ quantum state.

## isqTrain/1070

- task_id: `isqTrain/1070`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `difficult`
- concept_tags: `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `qubit_mapping`
- source: `isq_train_cot`
- dataset_index: `2583`

### Prompt

实现以下量子计算任务（使用isQ）：implements a variant of the token_swapping pattern using q[3] -> q[4]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a 3-cycle permutation using swap (three-CNOT decomposition) gates, moving a |1⟩ token from q[0] to q[1] via the permutation [2,0,1].
2. **Qubits**: 4 qubits declared (q[0]-q[3]), all measured at the end.
3. **State evolution**:
   - Initial: |0000⟩
   - X(q[0]): |1000⟩
   - swap_gate(q[1], q[2]): |1000⟩ (swapping two |0⟩ states leaves them unchanged)
   - swap_gate(q[0], q[1]): |0100⟩ (the |1⟩ moves from q[0] to q[1])
4. **Final state**: |0100⟩ with probability 1.0, as the circuit performs classical permutation using reversible swap (three-CNOT decomposition) operations.
