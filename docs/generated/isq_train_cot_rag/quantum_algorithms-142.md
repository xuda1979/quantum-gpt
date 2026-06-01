# ISQ training COT RAG corpus: quantum_algorithms shard 142

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3493

- task_id: `isqTrain/3493`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `multi_controlled_logic`, `boolean_logic`, `reversible_computing`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `4738`

### Prompt

预测以下isQ代码的输出概率：

```
import std;

qbit q[5];

procedure main() {
    X(q[0]); X(q[1]); X(q[2]);

    ctrl ctrl X(q[0], q[2], q[4]);
    ctrl ctrl X(q[1], q[3], q[4]);

    M(q[0]); M(q[1]); M(q[2]); M(q[3]); M(q[4]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis

1. **Operations applied:**
   - X(q[0]), X(q[1]), X(q[2]): Initialize first three qubits to |1⟩
   - ctrl ctrl X(q[0], q[2], q[4]): Toffoli gate flipping q[4] when q[0]=q[2]=|1⟩
   - ctrl ctrl X(q[1], q[3], q[4]): Toffoli gate flipping q[4] when q[1]=q[3]=|1⟩

2. **State evolution:**
   - Initial: |00000⟩
   - After X gates: |11100⟩
   - After first Toffoli (q[0]=1, q[2]=1): q[4] flips → |11101⟩
   - After second Toffoli (q[1]=1, q[3]=0): condition not met → state unchanged |11101⟩

3. **Final state:** |11101⟩

4. **Predicted distribution:** Only one basis state with probability 1.

**Non-zero probability states:** |11101⟩ (probability 1.0)

### Reference answer

{'predicted_probs': {'11101': 1.0}, 'explanation': 'The output is |11101> with probability 1.0'}

## isqTrain/3635

- task_id: `isqTrain/3635`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `5088`

### Prompt

用isQ实现the 4-qubit QFT applied to input state |0011>. The circuit should use Hadamard gates, controlled-Rz rotations with angles 2π/2^k, and final bit-reversal swaps. Measure all 4 qubits.

### Chain-of-thought reasoning

Let me analyze this 4-qubit QFT circuit applied to |0011>.

1. Goal: Implement QFT on 4 qubits starting from state |0011>

2. Qubits: 4 qubits (q[0] to q[3]), all measured

3. State evolution:
- Initial: |0000>
- After X(q[2]), X(q[3]): |0011>
- QFT stage for qubit 0:
  - H(q[0]): Creates superposition on q[0]
  - Since q[1]=0, q[2]=1, q[3]=1, the controlled rotations that activate are:
    - ctrl Rz(π/2, q[2], q[0]) - phase rotation by π/2
    - ctrl Rz(π/4, q[3], q[0]) - phase rotation by π/4

Actually, let me think more carefully about the QFT structure.

For QFT, we process each qubit from q[0] to q[n-1], and for each qubit j:
1. Apply H(q[j])
2. For each qubit k > j, apply controlled Rz(2π/2^(k-j+1)) with q[k] as control and q[j] as target

Wait, let me check the reference code:
- For q[0]: H(q[0]), then ctrl Rz with q[1] (angle π/2), q[2] (angle π/4), q[3] (angle π/8)
- For q[1]: H(q[1]), then ctrl Rz with q[2] (angle π/2), q[3] (angle π/4)
- For q[2]: H(q[2]), then ctrl Rz with q[3] (angle π/2)
- For q[3]: H(q[3])

Then swap q[0]↔q[3] and q[1]↔q[2].

Let me trace through the state:

Initial: |0000>
After X(q[2]), X(q[3]): |0011> (in computational basis: q[0]=0, q[1]=0, q[2]=1, q[3]=1)

Now for QFT:
The QFT of |0011> where 0011 in binary is 3.

QFT|x> = (1/√16) Σ_y e^(2πixy/16) |y>

So QFT|3> = (1/4) Σ_{y=0}^{15} e^(2πi·3·y/16) |y>

Let me compute the phases:
- y=0: e^0 = 1
- y=1: e^(6πi/16) = e^(3πi/8)
- y=2: e^(12πi/16) = e^(3πi/4)
- y=3: e^(18πi/16) = e^(9πi/8)
- etc.

All 16 basis states have equal magnitude 1/4, so equal probability 1/16 = 0.0625.

This explains the predicted output: all 16 basis states have probability 0.0625.

Let me trace the circuit more carefully:

State: |0011>

Stage for q[0]:
- H(q[0]): (|0> + |1>)/√2 ⊗ |011> = (|0011> + |1011>)/√2

- ctrl Rz(π/2, q[1], q[0]): q[1]=0, so no rotation applied
- ctrl Rz(π/4, q[2], q[0]): q[2]=1, so rotate |1> on q[0] by π/4
  (|0011> + e^(iπ/4)|1011>)/√2
- ctrl Rz(π/8, q[3], q[0]): q[3]=1, so rotate |1> on q[0] by π/8
  (|0011> + e^(iπ/4 + iπ/8)|1011>)/√2 = (|0011> + e^(3iπ/8)|1011>)/√2

Stage for q[1]:
- H(q[1]): 
  The state is (|0011> + e^(3iπ/8)|1011>)/√2
  Apply H to q[1] (second qubit):
  |0> → (|0>+|1>)/√2
  So: (1/2)(|011> + |111>)(|0>+|1>)_

## isqTrain/3832

- task_id: `isqTrain/3832`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `3709`

### Prompt

Help me write isQ code that Demonstrate phase kickback with controlled-Rz(pi/4). Control qubit starts in |+>, target in |1>. After controlled-Rz and Hadamard, measure to observe the kicked-back phase.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Demonstrate phase kickback where controlled-Rz(π/4) imparts a phase to the control qubit instead of the target.

**Qubits:** 2 qubits (q[0]=control, q[1]=target), both measured.

**State evolution:**
1. Initial: |00⟩
2. H(q[0]): |+⟩|0⟩ = (|00⟩ + |10⟩)/√2
3. X(q[1]): (|01⟩ + |11⟩)/√2 — target in |1⟩ eigenstate of Rz
4. ctrl Rz(π/4): (|01⟩ + e^{iπ/8}|11⟩)/√2 — phase kicks back to control (since Rz only adds phase to |1⟩, which target already is)
5. H(q[0]): [(1+e^{iπ/8})|01⟩ + (1-e^{iπ/8})|11⟩]/2

**Probabilities:** P(|01⟩) = |1+e^{iπ/8}|²/4 = (1+cos(π/8))/2 ≈ 0.9619; P(|11⟩) = (1-cos(π/8))/2 ≈ 0.

## isqTrain/737

- task_id: `isqTrain/737`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `phase_manipulation`, `qft_based_arithmetic`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1924`

### Prompt

用isQ实现implements the qft_adder pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement a 2-qubit QFT adder on input |11⟩ with reversed measurement ordering (q[1] measured first).

**State evolution:**
1. Initialize |00⟩; apply X(q[0]), X(q[1]) → |11⟩
2. H(q[1]) → (|10⟩ - |11⟩)/√2
3. ctrl S(q[0], q[1]) → (|10⟩ - i|11⟩)/√2
4

## isqTrain/2472

- task_id: `isqTrain/2472`
- task_type: `code_equivalence`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `global_phase`, `interference`, `isq_syntax_arrays`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `674`

### Prompt

Compare these two isQ programs. Do they give the same probability distribution?

First program:
```isq
import std;
qbit q[4];

procedure main() {
    H(q[0]); H(q[1]);
    // Copy
    CNOT(q[0], q[2]);
    CNOT(q[1], q[3]);
    // Oracle for s="11"
    CNOT(q[0], q[2]);
    CNOT(q[0], q[3]);
    // H on inputs
    H(q[0]); H(q[1]);
    // Measure inputs
    M(q[0]); M(q[1]);
}

```

Second program:
```isq
import std;
qbit q[4];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    H(q[0]); H(q[1]);
    // Copy
    CNOT(q[0], q[2]);
    CNOT(q[1], q[3]);
    // Oracle for s="11"
    CNOT(q[0], q[2]);
    CNOT(q[0], q[3]);
    // H on inputs
    H(q[0]); H(q[1]);
    // Measure inputs
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** initializes 4 qubits in |0>, applies H to q[0] and q[1] creating |+>|+>|0>|0>, uses CNOTs to copy states, applies a Bernstein-Vazirani oracle for s="11" using CNOTs, applies H to the inputs again, and measures q[0] and q[1].
2. **Program B** performs the exact same circuit operations as Program A, but adds the `GPhase(0.0)` instruction at the beginning of the main procedure.
3. The key difference between the programs is the presence of the `GPhase(0.0)` gate in Program B.
4. The `GPhase(0.0)` gate applies a global phase of $e^{i \cdot 0} = 1$. Multiplying a quantum state by 1 leaves the state perfectly unchanged.
5. Because the global phase is trivial, the quantum states in both programs are mathematically identical at every step, resulting in the exact same measurement probability distribution.

Verdict: Yes

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/2028

- task_id: `isqTrain/2028`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `boolean_logic`, `interference`, `isq_syntax_deriving_gate`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3999`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[2];
procedure my_z(qbit a) {
    Z(a);
} deriving gate
procedure main() {
    H(q[0]); H(q[1]);
    X(q[0]);
    ctrl my_z(q[0], q[1]);
    X(q[0]);
    H(q[0]); H(q[1]);
    X(q[0]); X(q[1]);
    ctrl my_z(q[0], q[1]);
    X(q[0]); X(q[1]);
    H(q[0]); H(q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Analyze an isQ program and predict measurement probabilities.
    *   Format: Start with "## Circuit Analysis", concise step-by-step reasoning using Dirac notation, end with the predicted probability distribution.
    *   Input Program: 2-qubit circuit with H, X, and `ctrl my_z` (which is CZ). Let's trace the state.

2.  **Analyze the Circuit:**
    *   Qubits: `q[0], q[1]` initialized to `|00>`.
    *   `my_z(a)` is a gate that applies `Z(a)`.
    *   `ctrl my_z(q[0], q[1])` is effectively `CZ(q[0], q[1])`.
    *   Let's trace step by step.
        *   Initial: `|00>`
        *   `H(q[0]); H(q[1])`: `1/2 (|00> + |01> + |10> + |11>)`
        *   `X(q[0])`: `1/2 (|10> + |11> + |00> + |01>)`
        *   `ctrl my_z(q[0], q[1])` (CZ on 0->1): applies Z to `q[1]` if `q[0]` is 1.
            *   `1/2 (|10> - |11> + |00> + |01>)`
        *   `X(q[0])`: `1/2 (|00> - |01> + |10> + |11>)`
        *   `H(q[0]); H(q[1])`: Let's expand H on q[0] and q[1].
            *   Current state: `1/2 |00> - 1/2 |01> + 1/2 |10> + 1/2 |11>`
            *   Apply H to q[0]:
                *   `1/2 * 1/sqrt(2) (|0> + |1>)|0> - 1/2 * 1/sqrt(2) (|0> + |1>)|1> + 1/2 * 1/sqrt(2) (|0> - |1>)|0> + 1/2 * 1/sqrt(2) (|0> - |1>)|1>`
                *   Wait, let's just group by `|0>` and `|1>` for q[0].
                *   q[0] part: `1/sqrt(2) [ (1/2|0> + 1/2|1>)|0> - (1/2|0> + 1/2|1>)|1> + (1/2|0> - 1/2|1>)|0> + (1/2|0> - 1/2|1>)|1> ]`
                *   Let's be systematic. State before H,H is `1/2 (|00> - |01> + |10> + |11>)`.
                *   Let `|psi>` = `|0> (1/2|0> - 1/2|1>) + |1> (1/2|0> + 1/2|1>)`.
                *   `H_0 |psi>` = `1/sqrt(2) (|0>+|1>) (1/2|0> - 1/2|1>) + 1/sqrt(2) (|0>-|1>) (1/2|0> + 1/2|1>)`
                *   `= 1/sqrt(2) [ |0>(1/2|0> - 1/2|1> + 1/2|0> + 1/2|1>) + |1>(1/2|0> - 1/2|1> - 1/2|0> - 1/2|1>) ]`
                *   `= 1/sqrt(2) [ |0>|0> + |1>(-|1>) ]` = `1/sqrt(2) (|00> - |11>)`.
                *   Now apply `H_1` to `1/sqrt(2) (|00> - |11>)`:
                *   `= 1/sqrt(2) [ |0>(|0> + |1>)/sqrt(2) - |1>(|0> - |1>)/sqrt(2) ]`
                *   Wait, `H|0> = (|0> + |1>)/sqrt(2

### Reference answer

{'predicted_probs': {'01': 1.0}, 'explanation': 'Grover search for |01>: P(|01>)=1.0 after one iteration.'}

## isqTrain/937

- task_id: `isqTrain/937`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5070`

### Prompt

Create an isQ quantum circuit that implements a variant of the reversible_logic pattern using q[3] -> q[5]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement a reversible controlled-swap (three-CNOT decomposition) (controlled-swap (three-CNOT decomposition)) gate on a 5-qubit register, where extra qubits remain idle in |0⟩.

2. **Qubits & Measurement**: 5 qubits (q[0]–q[4]) declared; all measured at the end.

3. **State evolution**:
   - |00000⟩ — initial state
   - X(q[0]) → |10000⟩
   - X(q[1]) → |11000⟩
   - ctrl swap_gate(q[0], q[1], q[2]): Since control q[0]=|1⟩, swap (three-CNOT decomposition)(q[1], q[2]) activates, swapping |10⟩ → |01⟩ on q[1],q[2] → |10100⟩
   - q[3], q[4] untouched, remain |0⟩

4. **Expected probabilities**: Final state is |10100⟩ with probability 1.0, yielding bitstring `10100` (q[0]=MSB).

## isqTrain/3529

- task_id: `isqTrain/3529`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `4378`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```
import std;

qbit q[2];

procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);

    CNOT(q[0], q[1]);
    H(q[0]);

    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Role:** Quantum computing expert.
    *   **Task:** Predict the output probability distribution of an isQ program.
    *   **Format:** Concise (3-15 lines), step-by-step reasoning, use Dirac notation.
    *   **Content:** Circuit analysis, state evolution, final state, predicted probability distribution.
    *   **Constraint:** Output ONLY the analysis, starting with "## Circuit Analysis", NO isQ code blocks, end with the predicted probability distribution.

2.  **Analyze the isQ Code:**
    

3.  **Step-by-Step State Evolution:**
    *   **Initial state:** $|00\rangle$
    *   **Gate 1:** `H(q[0])` -> State becomes $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$
    *   **Gate 2:** `CNOT(q[0], q[1])` -> Control is $q_0$, target is $q_1$. State becomes $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$ (Bell state).
    *   **Gate 3:** `CNOT(q[0], q[1])` -> Since CNOT is its own inverse ($CNOT^2 = I$), this unentangles the qubits. State returns to $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$.
    *   **Gate 4:** `H(q[0])` -> Since $H^2 = I$, this reverses the first Hadamard. State returns to $|00\rangle$.
    *   **Measurement:** `M(q[0])`, `M(q[1])` -> The state is $|00\rangle$. It will measure $q_0=0, q_1=0$ with certainty.

4.  **Format the Output:**
    *   Start with "## Circuit Analysis"
    *   Keep it concise (3-8 lines).
    *   Use Dirac notation.
    *   List non-zero probability states clearly.

5.  **Drafting the response:**
    ## Circuit Analysis
    1. Initial state is $|00\rangle$.
    2. `H(q[0])` creates superposition: $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$.
    3. First `CNOT(q[0], q[1])` entangles qubits into Bell state: $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$.
    4. Second `CNOT(q[0], q[1])` unentangles the state since CNOT is self-inverse: $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$.
    5. Final `H(q[0])` reverts $q_0$ to $|0\rangle$ since H is also self-inverse, resulting in final state $|00\rangle$.
    6. Predicted output probability distribution: 100% probability for $|00\rangle$.

6.  **Review against constraints:**
    *   Starts with "## Circuit Analysis"? Yes.
    *   No isQ code blocks? Yes.
    *   Ends with predicted probability distribution? Yes.
    *   Concise? Yes (6 lines).

    Wait, the prompt mentions: "List all basis states with non-zero probability." Let me ensure the end explicitly lists this.
    "Predicted probability distribution: 100% |00⟩." or "|00⟩: 100%".
    Let's refine the ending.
    "Predicted output probability distribution: |00⟩ (100%)."

    Let's check the qubit order in isQ measurement mapping. The prompt says "earlier measured qubit = higher bit" for --probs mode.
    `M(q[0]); M(q[1]);`
    So q[0] is higher bit, q[1] is lower bit. Thus state |q0=0, q1=0> corresponds to bitstring 00 (value 0).
    This matches perfectly.

    Final polish of the text to ensure maximum precision and conciseness.
    ## Circuit Analysis
    - Initial state is $|00\rangle$.
    - `H(q[0])` creates an equal superposition: $\frac{1}{\sqrt

### Reference answer

{'predicted_probs': {'00': 1.0}, 'explanation': 'The output is |00> with probability 1.0'}

## isqExpand/algo/216

- task_id: `isqExpand/algo/216`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `ghz_state`, `superposition`, `cnot_chain`, `entanglement`, `hadamard`
- source: `isq_expansion`
- dataset_index: `842`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```
import std;

qbit q[4];

procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
}
```

### Chain-of-thought reasoning

Step 1: The circuit starts with 4 qubits in state |0000⟩.
Step 2: Apply H(q[0]). This puts qubit 0 into superposition: (|0⟩ + |1⟩)/√2. The full state becomes (|0000⟩ + |1000⟩)/√2.
Step 3: Apply CNOT(q[0], q[1]). This entangles qubits 0 and 1. When control (q[0]) is |0⟩, target (q[1]) stays |0⟩. When control is |1⟩, target flips to |1⟩. State becomes (|0000⟩ + |1100⟩)/√2.
Step 4: Apply CNOT(q[1], q[2]). Similarly, this entangles qubit 2 with the chain. State becomes (|0000⟩ + |1110⟩)/√2.
Step 5: Apply CNOT(q[2], q[3]). This entangles qubit 3. State becomes (|0000⟩ + |1111⟩)/√2.
Step 6: The measurement probabilities are |⟨0000|ψ⟩|² = 0.5 and |⟨1111|ψ⟩|² = 0.5. All other basis states have zero amplitude, hence zero probability.
Step 7: The 16-element probability array is [0.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.5].

### Reference answer

{'predicted_probs': {'0000': 0.5, '0001': 0.0, '0010': 0.0, '0011': 0.0, '0100': 0.0, '0101': 0.0, '0110': 0.0, '0111': 0.0, '1000': 0.0, '1001': 0.0, '1010': 0.0, '1011': 0.0, '1100': 0.0, '1101': 0.0, '1110': 0.0, '1111': 0.5}, 'explanation': 'The circuit creates a 4-qubit GHZ state, which is an equal superposition of |0000⟩ and |1111⟩, each with probability 0.5. All other basis states have zero probability.'}

## isqTrain/4612

- task_id: `isqTrain/4612`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3273`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[1];

procedure main() {
    
    X(q[0]);
    H(q[0]);
    
    
    H(q[0]);
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The qubit `q[0]` is initialized to the ground state |0>.
2. `X(q[0])` flips the state to |1>.
3. `H(q[0])` puts the state into the superposition |-> = (|0> - |1>) / sqrt(2).
4. The second `H(q[0])` reverses the previous superposition, transforming |-> back to |1>.
5. `X(q[0])` flips the state |1> to |0>.
6. The measurement operator will deterministically yield the outcome corresponding to |0>.

Predicted probability distribution: {|0>: 1.0}

### Reference answer

{'predicted_probs': {'0': 1.0}, 'explanation': 'This isQ program operates on 1 qubit(s). The measurement probability distribution is: P(|0>) = 1.0000.'}
