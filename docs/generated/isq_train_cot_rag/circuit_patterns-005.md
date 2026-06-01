# ISQ training COT RAG corpus: circuit_patterns shard 5

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3851

- task_id: `isqTrain/3851`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `difficult`
- concept_tags: `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `2968`

### Prompt

Create an isQ quantum circuit that Apply ctrl<2> X (equivalent to Toffoli) to input |011>. The target q[2] flips only when both q[0] and q[1] are |1>. Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Apply a doubly-controlled X gate (Toffoli) to the state |011> and measure all qubits.
2. **Qubits:** 3 qubits are required, and all 3 are measured.
3. **State Evolution:**
   - Initialize to |000>.
   - Apply X to q[1] and q[2] to prepare the input state |011>.
   - The ctrl<2> X gate targets q[2] and uses q[0] and q[1] as controls.
   - For a Toffoli gate to flip the target, both controls must be in the |1> state.
   - Here, q[0] is |0> and q[1] is |1>. Because q[0] is not |1>, the condition is not met.
   - The gate does nothing, leaving the quantum state unchanged at |011>.
4. **Measurement Probabilities:** The final state is exactly |011>, so measuring the qubits yields the bitstring '011' with a probability of 1.0.

## isqTrain/3858

- task_id: `isqTrain/3858`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `expert`
- concept_tags: `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `3522`

### Prompt

Implement a quantum circuit in isQ: Apply ctrl<3> X to input |1110>. Target q[3] flips only when q[0], q[1], q[2] are all |1>. Measure all 4 qubits.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply a triple-controlled X gate (ctrl<3> X) to input |1110>, flipping the target qubit only when all three controls are |1⟩.
2. Qubits: 4 qubits q[0..3]; all are measured.
3. State evolution:
   - Initialize to |0000⟩.
   - X(q[0]), X(q[1]), X(q[2]) → |1110⟩.
   - ctrl<3> X(q[0], q[1], q[2], q[3]): Since q[0]=|1⟩, q[1]=|1⟩, q[2]=|1⟩, the target q[3] flips: |1110⟩ → |1111⟩.
4. Expected probabilities: {|1111⟩: 1.0}, since the final state is |1111⟩ with certainty.

## isqTrain/3849

- task_id: `isqTrain/3849`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `difficult`
- concept_tags: `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `2021`

### Prompt

用isQ实现Apply ctrl<2> X (equivalent to Toffoli) to input |001>. The target q[2] flips only when both q[0] and q[1] are |1>. Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
The goal is to apply a doubly-controlled X gate (Toffoli) to the input state |001> and measure the resulting quantum state.
Three qubits (q[0], q[1], q[2]) are used, and all three are measured at the end of the circuit.
The circuit initializes the state to |000>, and an X gate is applied to q[2] to prepare the |001> input state.
Applying the Toffoli gate with q[0] and q[1] as controls and q[2] as the target checks if both controls are |1>. 
Since q[0] and q[1] are in the |0> state, the condition is not met, and the target q[2] remains unchanged.
Therefore, the final quantum state remains |001>, resulting in a 100% probability of measuring the bitstring |001>.

## isqTrain/3782

- task_id: `isqTrain/3782`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `expert`
- concept_tags: `superposition`, `entanglement`, `isq_syntax_for_loop`, `data_encoding_qml`
- source: `isq_train_cot`
- dataset_index: `709`

### Prompt

Help me write isQ code that a 4-qubit parameterized quantum ansatz with 1 layer(s). Each layer applies Ry rotations to all qubits followed by a CNOT entangling chain. Use for loops. Measure all 4 qubits.

### Chain-of-thought reasoning

Let me analyze this 4-qubit parameterized ansatz circuit.

1. Goal: Implement a 4-qubit parameterized ansatz with 1 layer of Ry(0.5) rotations followed by CNOT entangling chain, measuring all qubits.

2. Qubits: 4 qubits (q[0], q[1], q[2], q[3]), all measured.

3. Step-by-step evolution:
- Initial state: |0000>
- After Ry(0.5) on each qubit: Each qubit becomes cos(0.25)|0> + sin(0.25)|1>
  - cos(0.25) ≈ 0.9689, sin(0.25) ≈ 0.2474
- Product state: (cos(0.25)|0> + sin(0.25)|1>)^4
- After CNOT(q[0], q[1]): Entangles q[0] and q[1]
- After CNOT(q[1], q[2]): Entangles q[1] and q[2]
- After CNOT(q[2], q[3]): Entangles q[2] and q[3]

Let me compute more carefully:
c = cos(0.25) ≈ 0.9689
s = sin(0.25) ≈ 0.2474

After rotations: (c|0> + s|1>)^4 = c^4|0000> + c^3*s|0001> + c^3*s|0010> + c^2*s^2|0011> + c^3*s|0100> + c^2*s^2|0101> + c^2*s^2|0110> + c*s^3|0111> + c^3*s|1000> + c^2*s^2|1001> + c^2*s^2|1010> + c*s^3|1011> + c^2*s^2|1100> + c*s^3|1101> + c*s^3|1110> + s^4|1111>

After CNOT chain (q[0]→q[1]→q[2]→q[3]):
- CNOT flips target when control is |1>
- The CNOT chain creates entanglement by propagating control through the chain.

Let me trace through:
Initial product state coefficients for |q3 q2 q1 q0>:
- |0000>: c^4
- |0001>: c^3*s (q[0]=1)
- |0010>: c^3*s (q[1]=1)
- |0011>: c^2*s^2 (q[0]=1, q[1]=1)
- |0100>: c^3*s (q[2]=1)
- |0101>: c^2*s^2
- |0110>: c^2*s^2
- |0111>: c*s^3
- |1000>: c^3*s (q[3]=1)
- |1001>: c^2*s^2
- |1010>: c^2*s^2
- |1011>: c*s^3
- |1100>: c^2*s^2
- |1101>: c*s^3
- |1110>: c*s^3
- |1111>: s^4

CNOT(q[0], q[1]): When q[0]=1, flip q[1]
- |0000> → |0000>
- |0001> (q1=0,q0=1) → |0011> (q1 flipped to 1)
- |0010> (q1=1,q0=0) → |0010>
- |0011> (q1=1,q0=1) → |0001> (q1 flipped to 0)
- |0100> → |0100>
- |0101> → |0111>
- |0110> → |0110>
- |0111> → |0101>
- |1000> → |1000>
- |1001> → |1011>
- |1010> → |1010>
- |1011> → |1001>
- |1100> → |1100>
- |1101> → |1111>
- |1110> → |1110>
- |1111> → |1101>

After CNOT(q[0],q[1]):
|0000>: c^4
|0001>: c^2*s^2 (was |0011>)
|0010>: c^3*s

## isqTrain/3863

- task_id: `isqTrain/3863`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `expert`
- concept_tags: `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3649`

### Prompt

Implement a quantum circuit in isQ: Apply `ctrl nctrl X` to |011>: q[0] is positive control, q[1] is negative control, q[2] is target. Target flips when q[0]=|1> AND q[1]=|0>. Measure all 3 qubits.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Generate a reasoning section for a specific isQ quantum circuit.
    *   Circuit description: Apply `ctrl nctrl X` to |011>. `q[0]` is positive control, `q[1]` is negative control, `q[2]` is target. Target flips when `q[0]=|1>` AND `q[1]=|0>`. Initial state is implicitly |000>, but we need it to start as |011>.
    *   Wait, The circuit should:
        *   `q[0]` starts as |0>
        *   `X(q[1])` -> `q[1]` is |1>
        *   `X(q[2])` -> `q[2]` is |1>
        *   Initial state for the Toffoli-like gate is |011>.
        *   The gate is `ctrl nctrl X(q[0], q[1], q[2])`. It flips `q[2]` if `q[0]=1` and `q[1]=0`. Here, `q[0]=0` and `q[1]=1`. Thus, the condition is NOT met.
        *   Therefore, `q[2]` does NOT flip.
        *   Final state remains |011>.
    *   Output format: ONLY the reasoning section starting with "## Reasoning".
    *   Constraints: Concise (3-8 lines), Dirac notation, precise state evolution.

2.  **Drafting the Reasoning:**
    *   *Goal:* Prepare the state |011> and apply a mixed-control X gate, then measure all qubits.
    *   *Qubits:* 3 qubits (`q[0]`, `q[1]`, `q[2]`), all measured.
    *   *State Evolution:*
        *   Initialize `q` to |000>.
        *   Apply X to `q[1]` and `q[2]`: state becomes |011>.
        *   Apply `ctrl nctrl X(q[0], q[1], q[2])`: checks if `q[0]`=|1> and `q[1]`=|0>. Since `q[0]`=|0> and `q[1]`=|1>, the condition fails.
        *   State remains |011>.
    *   *Probabilities:* The final state is |011> with 100% probability. Measured bitstring depends on mapping (usually q[0] is highest bit -> `q[0]q[1]q[2]` = 011).

3.  **Refining the Text (incorporating into 3-8 lines):**
    ## Reasoning
    * Goal: Initialize the state |011> and apply a mixed-control X gate where q[0] is the positive control, q[1] is the negative control, and q[2] is the target.
    * We need 3 qubits, and all 3 are measured at the end.
    * Evolution: Start in |000>. Apply X to q[1] and q[2] to transition to |011>.
    * The `ctrl nctrl X` gate flips the target (q[2]) only if q[0] is |1> and q[1] is |0>. Currently, q[0] is |0> and q[1] is |1>, so the condition is not met.
    * The quantum state remains unchanged at |011>.
    * Since the state is a computational basis state, the expected measurement probability is exactly 100% for the outcome |011>.

4.  **Final Polish:** Match the concise tone and strict formatting.
    *   Goal: Initialize state |011> and apply a mixed-control X gate (positive ctrl q[0], negative ctrl q[1], target q[2]), then measure.
    *   Qubits: 3 qubits used, all 3 are measured.
    *   State Evolution: Start at |000>. Apply X(q[1]) and X(q[2]) to create |011>.
    *   Gate action: `ctrl nctrl X` flips q[2] only if q[0]=|1> and q[1]=|0>. Since q[0]=|0> and q[1]=|1>, the condition fails, leaving the state at |011>.
    *   Probabilities: The system is in the exact basis state |011>, yielding a 100% probability of measuring 011.

5.  **Sanity Check:**
    *   Dirac notation used? Yes (|000>, |011>, |0>, |1

## isqTrain/3771

- task_id: `isqTrain/3771`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_for_loop`, `isq_syntax_classical_vars`
- source: `isq_train_cot`
- dataset_index: `2623`

### Prompt

Implement a quantum circuit in isQ: a 4-qubit circuit that applies a rotation sweep: Rz(i*π/4) to qubit q[i] for i=0..3. First apply Hadamard to all qubits using a for loop, then the rotation sweep, then measure all qubits using a for loop.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Create a 4-qubit circuit applying Hadamard to all qubits, then Rz(i·π/4) rotation to qubit q[i], then measure all.

**Qubits:** 4 qubits (q[0]–q[3]), all measured.

**State evolution:**
1. Initial: |0000>
2. After H on all: |++++> = (1/4)Σ_{x∈{0,1}⁴} |x⟩, equal superposition over 16 states
3. Rz(i·π/4) on q[i] applies phase e^{-iθ/2}|0⟩ + e^{iθ/2}|1⟩ to each qubit. For computational basis state |x₃x₂x₁x₀⟩, this accumulates phase exp(i·Σᵢ xᵢ·(−1)⁰·θᵢ/2) where θᵢ = i·π/4
4. Each |x⟩ gets a different phase, but |amplitude|² = (1/16) for all states

**Probabilities:** Rz only adds phases (diagonal operation), so measurement probabilities remain uniform: P(|x⟩) = 1/16 = 0.0625 for all 16 basis states.

## isqTrain/3852

- task_id: `isqTrain/3852`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `difficult`
- concept_tags: `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `4710`

### Prompt

请用isQ语言编写一个量子电路：Apply ctrl<2> X (equivalent to Toffoli) to input |100>. The target q[2] flips only when both q[0] and q[1] are |1>. Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
The goal is to prepare the state |100> and apply a doubly-controlled X (Toffoli) gate to it.
Three qubits (q[0], q[1], q[2]) are required, and all are measured at the end.
Starting from the ground state |000>, an X gate applied to q[0] prepares the input state |100>.
The Toffoli gate flips the target qubit q[2] only if both controls (q[0] and q[1]) are |1>. 
Since q[1] is in the |0> state, the control condition is not met, leaving the quantum state unchanged at |100>.
Consequently, the final state deterministically yields the measurement bitstring '100' with a probability of 1.0.

## isqTrain/3854

- task_id: `isqTrain/3854`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `difficult`
- concept_tags: `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1296`

### Prompt

I need an isQ program to Apply ctrl<2> X (equivalent to Toffoli) to input |110>. The target q[2] flips only when both q[0] and q[1] are |1>. Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
The goal is to apply a doubly-controlled X gate (Toffoli) to a 3-qubit system initialized to |110> and measure the result.
Three qubits (q[0], q[1], q[2]) are required, and all three are measured at the end of the circuit.
Starting from |000>, applying X gates to q[0] and q[1] prepares the input state |110>.
The `ctrl<2> X` gate flips the target q[2] from |0> to |1> because both controls (q[0] and q[1]) are in the |1> state, evolving the system to |111>.
Because the final quantum state is exactly |111>, the expected measurement outcome is deterministically |111> with a probability of 1.0.

## isqTrain/3995

- task_id: `isqTrain/3995`
- task_type: `bug_fix`
- category: `circuit_patterns`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_for_loop`, `isq_syntax_classical_vars`
- source: `isq_train_cot`
- dataset_index: `836`

### Prompt

Debug this isQ program — it gives unexpected measurement results.

```
import std;
// Rotation sweep: apply Rz(i*pi/5) to q[i] for i=0..4
qbit q[5];

procedure main() {
    // Put all qubits in superposition first
    for i in 0:5 {
        X(q[i]);
    }
    // Apply parametric rotation sweep
    for i in 0:5 {
        // Rz angle increases with qubit index
        double angle = i * 3.14159265358979 / 5.0;
        Rz(angle, q[i]);
    }
    // Measure all qubits
    for i in 0:5 {
        M(q[i]);
    }
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

## Bug Analysis
1. **The bug** is in the first loop where `X(q[i])` is applied. The X gate flips the qubit state from |0> to |1>, whereas the comment states the intent is to put the qubits into a superposition.
2. **The fix** is to replace `X(q[i])` with `H(q[i])`. The Hadamard gate transforms the |0> state into the |+> superposition state.
3. **State evolution**: Starting in |0>, the H gate creates an equal superposition |+> = (|0> + |1>)/√2. The subsequent `Rz` rotation applies a relative phase, resulting in the state (|0> + exp(iθ)|1>)/√2. Because `Rz` only changes the phase and not the amplitudes, measuring the qubits yields an equal 50% probability for |0> and |1> on each qubit, meaning all 32 possible 5-qubit computational basis states will be measured with a uniform probability of 1/32 (0.03125).

## isqTrain/3926

- task_id: `isqTrain/3926`
- task_type: `bug_fix`
- category: `circuit_patterns`
- difficulty: `difficult`
- concept_tags: `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `4901`

### Prompt

Fix the bug in this quantum program:

```
import std;
// ctrl<2> X (Toffoli) on input |101>
qbit q[3];

procedure main() {
    // Prepare input |101>
    X(q[0]);
    Y(q[2]);
    // Apply doubly-controlled X
    ctrl<2> X(q[0], q[1], q[2]);
    // Measure
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

## Bug Analysis
1. **The bug** is on line 9: `Y(q[2])` is used instead of `X(q[2])` to prepare the input state |101>. The Y gate applies a phase to |1>, resulting in i|1> instead of |1>.
2. **The fix** is to replace `Y(q[2])` with `X(q[2])`.
3. **State evolution of the corrected circuit**:
- Initialize |000>
- Apply X(q[0]) -> |100>
- Apply X(q[2]) -> |101>
- Apply ctrl<2> X(q[0], q[1], q[2]) -> Control q[1] is |0>, so the Toffoli gate is not triggered and state remains |101>
- Final state: |101>
