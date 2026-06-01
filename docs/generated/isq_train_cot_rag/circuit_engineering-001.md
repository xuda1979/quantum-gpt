# ISQ training COT RAG corpus: circuit_engineering shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1015

- task_id: `isqTrain/1015`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `circuit_optimization`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2726`

### Prompt

Code this in isQ: implements the gate_consolidation pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Demonstrate gate consolidation by merging rotations and showing X-X cancellation before measurement.
2. **Qubits**: 1 qubit `q[0]` is used and measured.
3. **State evolution**:
   - Start: |0⟩
   - X(q[0]): |0⟩ → |1⟩
   - Rz(π/2, q[0]): |1⟩ → e^(-iπ/4)|1⟩ (phase shift, but measurement probabilities unchanged)
   - X(q[0]): e^(-iπ/4)|1⟩ → e^(-iπ/4)|0⟩
   - X(q[0]): e^(-iπ/4)|0⟩ → e^(-iπ/4)|1⟩ (X-X pair cancels to identity)
4. **Final state**: e^(-iπ/4)|1⟩ — global phase doesn't affect measurement.
5. **Expected probabilities**: {|1⟩: 1.0} since measurement collapses to |1⟩ with certainty.

## isqTrain/1051

- task_id: `isqTrain/1051`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `qubit_mapping`
- source: `isq_train_cot`
- dataset_index: `100`

### Prompt

帮我写一个isQ程序：implements a variant of the sabre_routing pattern using q[3] -> q[4]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement a SABRE routing variant performing CNOT from q[3] to q[4] using an expanded 5-qubit register.

2. **Qubits**: 5 qubits (q[0]-q[4]), all measured at the end.

3. **State evolution**:
   - Initial state: |00000⟩
   - X(q[3]): flips q[3] → |00010⟩
   - CNOT(q[3], q[4]): control q[3]=|1⟩ flips target q[4] → |00011⟩

4. **Expected probabilities**: Final state |00011⟩ yields measurement bitstring |00011⟩ with probability 1.0, since q[3] and q[4] are both |1⟩ and all others are |0⟩.

## isqTrain/1028

- task_id: `isqTrain/1028`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `difficult`
- concept_tags: `basis_change`, `circuit_optimization`, `entanglement`
- source: `isq_train_cot`
- dataset_index: `1349`

### Prompt

Write isQ code for the following quantum task: implements the clifford_optimization pattern but with a different initial state preparation (flip q[[1]] -> q[0]).

### Chain-of-thought reasoning

## Reasoning
Goal: Prepare |10⟩ via X on q[0], then apply CNOT(1,0) which leaves the state unchanged.

Qubits: 2 (q[0], q[1]), both measured.

State evolution:
1. |00⟩ — initial state
2. X(q[0]) → |10⟩
3. CNOT(q[1], q[0]): control q[1]=|0⟩, so no flip → |10⟩
4. Measurement yields q[0]=1, q[1]=0

Expected probabilities: Since the state is deterministically |10⟩, measuring gives |10⟩ with probability 1.0.

## isqTrain/2057

- task_id: `isqTrain/2057`
- task_type: `output_prediction`
- category: `circuit_engineering`
- difficulty: `difficult`
- concept_tags: `isq_syntax_deriving_gate`, `isq_syntax_procedures`, `qubit_mapping`
- source: `isq_train_cot`
- dataset_index: `5305`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

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
    swap_gate(q[1], q[2]);
    swap_gate(q[0], q[1]);
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants a step-by-step analysis of an isQ quantum program, predicting the probability distribution of its measurement outcomes.

2.  **Analyze the isQ Code**:
    *   3 qubits: `q[0]`, `q[1]`, `q[2]`. Initial state: `|000>`.
    *   `X(q[0])`: Flips `q[0]` to `|1>`. State is `|100>`.
    *   `swap_gate(q[1], q[2])`: Swaps `q[1]` and `q[2]`. Since both are `|0>`, state remains `|100>`.
    *   `swap_gate(q[0], q[1])`: Swaps `q[0]` and `q[1]`. `q[0]` was `|1>` and `q[1]` was `|0>`. After swap, `q[0]` is `|0>` and `q[1]` is `|1>`. State becomes `|010>`.
    *   Measurements: `M(q[0])`, `M(q[1])`, `M(q[2])`.

3.  **Step-by-Step State Evolution**:
    *   Initial state: `|000>`
    *   After `X(q[0])`: `X|0> = |1>` for `q[0]`. State is `|100>`.
    *   After `swap(q[1], q[2])`: Swap `|0>` and `|0>`. State remains `|100>`.
    *   After `swap(q[0], q[1])`: Swap `|1>` and `|0>`. State becomes `|010>`.
    *   Final state: `|010>`.

4.  **Determine Probabilities**:
    *   Measurement of `|010>` yields `q[0]=0`, `q[1]=1`, `q[2]=0`.
    *   the predicted output format is a JSON-like string or dictionary for probabilities. The prompt asks for "{'010': 1.0}" (as seen In the implementation, although I must just provide the analysis and end with the predicted probability distribution). Wait, the prompt explicitly says "End with the predicted probability distribution" and "Output ONLY the analysis...". Let's format the last line clearly.
    *   Wait, is `010` correct for `q[0]=0, q[1]=1, q[2]=0`? Let's check bit ordering. "earlier measured qubit = higher bit".
        *   Measured `q[0]` -> highest bit.
        *   Measured `q[1]` -> middle bit.
        *   Measured `q[2]` -> lowest bit.
        *   `q[0]=0, q[1]=1, q[2]=0` translates to binary string `010`.
    *   Probability is 1.0 for `010` and 0.0 for all others.

5.  **Format the Output**:
    *   Start with "## Circuit Analysis".
    *   1. Operations: X on q[0], Swap(q[1], q[2]), Swap(q[0], q[1]).
    *   2. Evolution: |000> -> X(q[0]) -> |100> -> Swap(q[1], q[2]) -> |100> -> Swap(q[0], q[1]) -> |010>.
    *   3. Final state: |010>.
    *   4. Distribution: P(010) = 1.0.

6.  **Refine Text**: Keep it concise, precise, and within the length limits (3-8 lines).
    *   ## Circuit Analysis
    *   1. **Operations**: The circuit initializes 3 qubits to |000>. It applies an X gate to q[0], followed by a swap between q[1] and q[2], and finally a swap between q[0] and q[1].
    *   2. **State Evolution**:
        *   Initial state: |000>
        *   X(q[0]) flips q[0] to |1>: |100>
        *   swap(q[1], q[2]) swaps two |0> states: |100>
        *   swap(q[0], q[1]) swaps q[0] (|1>) and q[1] (|0>): |010>
    *   3. **Final State**: The system is deterministically in the state |010>.
    *   4. **Probability Distribution**: Measuring the qubits will yield '010

### Reference answer

{'predicted_probs': {'010': 1.0}, 'explanation': 'Token swapping: permutation [2,0,1]. State |010>, index 2, P=1.0.'}

## isqTrain/1054

- task_id: `isqTrain/1054`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `qubit_mapping`
- source: `isq_train_cot`
- dataset_index: `3438`

### Prompt

用isQ实现implements the sabre_routing pattern but with a different initial state preparation (flip q[[0]] -> q[2]).

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement SABRE routing pattern with CNOT(q[1], q[2]) using swap (three-CNOT decomposition) gates, but initialize q[2] to |1⟩ instead of q[0].

2. **Qubits**: 3 qubits (q[0], q[1], q[2]), all measured at the end.

3. **State evolution**:
   - Initial: |000⟩
   - X(q[2]): |001⟩ (q[2] flipped to |1⟩)
   - swap (three-CNOT decomposition)(q[0], q[1]): |001⟩ (no effect—both are |0⟩)
   - CNOT(q[1], q[2]): |001⟩ (control q[1]=|0⟩, so target unchanged)
   - swap (three-CNOT decomposition)(q[0], q[1]): |001⟩ (no effect—both are |0⟩)

4. **Expected probabilities**: Final state is |001⟩ with probability 1.0 because the CNOT control q[1] remains |0⟩ throughout, so the |1⟩ on q[2] is never flipped.

## isqTrain/1030

- task_id: `isqTrain/1030`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `difficult`
- concept_tags: `basis_change`, `circuit_optimization`, `entanglement`
- source: `isq_train_cot`
- dataset_index: `5731`

### Prompt

Implement the following in isQ: implements the clifford_optimization pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a Clifford-optimized circuit with explicit identity (X-X pair) to demonstrate gate cancellation awareness, producing |11⟩.
2. **Qubits**: 2 qubits (q[0], q[1]), both measured.
3. **State evolution**:
   - |00⟩ — initial state
   - X(q[1]) → |01⟩
   - CNOT(q[1], q[0]) → |11⟩ (control q[1]=1 flips target q[0])
   - X(q[0]) → |01⟩
   - X(q[0]) → |11⟩ (X-X pair = I, cancels out)
4. **Expected probabilities**: The X-X pair forms identity (X²=I), leaving state |11⟩. Measurement yields {|11⟩: 1.0}.

## isqTrain/1066

- task_id: `isqTrain/1066`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `qubit_mapping`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4930`

### Prompt

请用isQ语言编写一个量子电路：implements the vf2_mapping pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare a computational basis state using X gates and CNOTs, then measure in reversed order.
2. **Qubits**: 3 qubits (q[0], q[1], q[2]), all measured.
3. **State evolution**:
   - Initial: |000⟩
   - X(q[0]): |100⟩
   - X(q[1]): |110⟩
   - CNOT(q[0], q[2]): |111⟩ (q[2] flipped by q[0]=1)
   - CNOT(q[1], q[2]): |110⟩ (q[2] flipped back by q[1]=1)
4. **Measurement order**: M(q[2]) → M(q[1]) → M(q[0]) means q[2] is the highest bit, q[0] is the lowest.
5. **Result**: Final state q[0]=1, q[1]=1, q[2]=0 maps to bitstring |011⟩ with probability 1.0.

## isqTrain/1018

- task_id: `isqTrain/1018`
- task_type: `output_prediction`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `circuit_optimization`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4711`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[1];

// Optimized: merged two Rz(pi/4) into one Rz(pi/2)
procedure main() {
    // Set qubit to |1>
    X(q[0]);
    // Consolidated rotation: Rz(pi/4) + Rz(pi/4) = Rz(pi/2)
    // pi/2 = 1.5707963267949
    Rz(1.5707963267949, q[0]);
    // Rz only adds phase to computational basis states
    // Measurement outcome is unchanged
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations**: The circuit initializes a single qubit `q[0]`, applies an X gate, followed by an Rz rotation of $\pi/2$ (1.570796... radians), and measures the qubit.
2. **State Evolution**:
   - Initial state: $|0\rangle$
   - After X gate: $X|0\rangle = |1\rangle$
   - After Rz($\pi/2$) gate: $Rz(\pi/2)|1\rangle = e^{i\pi/4}|1\rangle$ (up to global phase convention, applying a phase to the $|1\rangle$ state).
3. **Final State**: The final state is $e^{i\pi/4}|1\rangle$. The Rz gate only alters the phase of the computational basis states, which does not affect measurement probabilities.
4. **Probabilities**: Because the qubit is entirely in the $|1\rangle$ state (up to an unmeasurable global phase), it will be measured as 1 with 100% probability

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Parametric variant of isqEval/312. Dimension: predict probabilities for reference circuit.'}

## isqTrain/1035

- task_id: `isqTrain/1035`
- task_type: `output_prediction`
- category: `circuit_engineering`
- difficulty: `difficult`
- concept_tags: `basis_change`, `circuit_optimization`, `entanglement`
- source: `isq_train_cot`
- dataset_index: `5115`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[2];

// Optimized: H*H*CNOT(0,1)*H*H = CNOT(1,0)
procedure main() {
    // Set q[1] to |1>
    X(q[1]);
    // CNOT direction reversal: the H-CNOT-H sandwich
    // swaps control and target, giving CNOT(q[1], q[0])
    CNOT(q[1], q[0]);
    // q[1]=1 controls, q[0] flips: |01> -> |11>
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Gates applied**: `X(q[1])`, `CNOT(q[1], q[0])`
2. **State evolution**:
   - Initial state: |00>
   - `X(q[1])`: Flips q[1], resulting in |01>
   - `CNOT(q[1], q[0])`: q[1] is the control and is in |1>, so target q[0] is flipped from |0> to |1>, resulting in |11>
3. **Final state**: |11>
4. **Prediction**: The state is deterministically |11>, so measuring both qubits will always yield 1.

Predicted probabilities: {|11>: 1.0}

### Reference answer

{'predicted_probs': {'3': 1.0}, 'explanation': 'Parametric variant of isqEval/317. Dimension: predict probabilities for reference circuit.'}

## isqTrain/1025

- task_id: `isqTrain/1025`
- task_type: `output_prediction`
- category: `circuit_engineering`
- difficulty: `difficult`
- concept_tags: `basis_change`, `circuit_optimization`, `global_phase`
- source: `isq_train_cot`
- dataset_index: `1822`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

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
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations:** X gate followed by Z gate on qubit q[0].
2. **State evolution:**
   - Initial: |0>
   - After X: |1>
   - After Z: -|1> (global phase -1)
3. **Final state:** -|1>, which is physically equivalent to |1>.
4. **Prediction:** Measurement yields |1> with certainty since the global phase has no observable effect.

**Predicted probability distribution:** {|1>: 1.0}

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Parametric variant of isqEval/315. Dimension: predict probabilities for reference circuit.'}
