# ISQ training COT RAG corpus: circuit_patterns shard 4

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3850

- task_id: `isqTrain/3850`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `difficult`
- concept_tags: `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `3207`

### Prompt

帮我写一个isQ程序：Apply ctrl<2> X (equivalent to Toffoli) to input |010>. The target q[2] flips only when both q[0] and q[1] are |1>. Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply a doubly-controlled X gate (Toffoli) to the state |010> and measure all qubits.
2. **Qubits**: 3 qubits are needed (q[0], q[1], q[2]), and all are measured.
3. **State Evolution**: 
   - Initialize to |000⟩. Apply X to q[1] to prepare |010⟩.
   - Apply ctrl<2> X with controls q[0], q[1] and target q[2]. Since q[0] is |0⟩, the control condition (both controls in |1⟩) is not met. The state remains |010⟩.
4. **Measurement**: The final state is exactly |010⟩, so the measurement probabilities are {|010⟩: 1.0}.

## isqTrain/3865

- task_id: `isqTrain/3865`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `expert`
- concept_tags: `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `930`

### Prompt

Write an isQ program that Apply `ctrl nctrl X` to |101>: q[0] is positive control, q[1] is negative control, q[2] is target. Target flips when q[0]=|1> AND q[1]=|0>. Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply a mixed-control X gate (positive control q[0], negative control q[1], target q[2]) to state |101⟩, then measure all qubits.
2. **Qubits**: 3 qubits (q[0], q[1], q[2]), all measured.
3. **State evolution**:
   - Start: |000⟩
   - X(q[0]), X(q[2]) → |101⟩ (q[0]=|1⟩, q[1]=|0⟩, q[2]=|1⟩)
   - ctrl nctrl X(q[0], q[1], q[2]): q[0]=|1⟩ ✓ (positive control satisfied), q[1]=|0⟩ ✓ (negative control satisfied) → flip q[2]
   - |101⟩ → |100⟩
4. **Expected probabilities**: {|100⟩: 1.0} — deterministic result since the control condition is met.

## isqTrain/3971

- task_id: `isqTrain/3971`
- task_type: `bug_fix`
- category: `circuit_patterns`
- difficulty: `expert`
- concept_tags: `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3895`

### Prompt

This isQ program doesn't produce the correct output. Can you debug it?

Code:
```
import std;
// Mixed control: ctrl q[0], nctrl q[1], target q[2]
qbit q[3];

procedure main() {
    // BUG: missing gate here
    // Flip q[2] when q[0]=|1> and q[1]=|0>
    ctrl nctrl X(q[0], q[1], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug identification**: The missing gate is an `X(q[0])` initialization. The task specifies the input state |100⟩, but the circuit starts with all qubits in |000⟩. Without setting q[0] to |1⟩, the control condition for the mixed-control X gate is never satisfied.

2. **Fix**: Add `X(q[0])` before the mixed-control gate to prepare the state |100⟩ from the initial |000⟩.

3. **State evolution**:
   - Initial: |000⟩
   - After X(q[0]): |100⟩
   - After ctrl nctrl X: q[0]=|1⟩ ✓, q[1]=|0⟩ ✓ → X flips q[2], resulting in |101⟩
   - Expected measurement: {|101⟩: 1.0} ✓

## isqTrain/3857

- task_id: `isqTrain/3857`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `expert`
- concept_tags: `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `5507`

### Prompt

Help me write isQ code that Apply ctrl<3> X to input |0111>. Target q[3] flips only when q[0], q[1], q[2] are all |1>. Measure all 4 qubits.

### Chain-of-thought reasoning

## Reasoning
The goal is to apply a triple-controlled X gate to the state |0111> and measure the resulting system.
Four qubits (q[0] to q[3]) are used, and all are measured at the end of the circuit.
1. Initialize qubits to |0000>.
2. Apply X gates to q[1], q[2], and q[3] to prepare the initial state |0111>.
3. Apply `ctrl<3> X(q[0], q[1], q[2], q[3])`, which flips the target q[3]

## isqTrain/3862

- task_id: `isqTrain/3862`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `expert`
- concept_tags: `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3122`

### Prompt

帮我写一个isQ程序：Apply `ctrl nctrl X` to |010>: q[0] is positive control, q[1] is negative control, q[2] is target. Target flips when q[0]=|1> AND q[1]=|0>. Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
The goal is to apply a mixed-control X gate (positive control on q[0], negative on q[1]) to a 3-qubit system and measure all qubits.
We need 3 qubits, all of which are measured.
The initial state |000> is transformed to |010> by applying an X gate to q[1].
The `ctrl nctrl X` gate flips the target q[2] only if q[0] is |1> and q[1] is |0>.
Since the current state is |010> (where q[0]=|0> and q[1]=|1>), the control condition is not met and the target remains unchanged.
The final state remains |010>, leading to a 100% probability of measuring the bitstring |010>.

## isqTrain/3853

- task_id: `isqTrain/3853`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `difficult`
- concept_tags: `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `5354`

### Prompt

请用isQ语言编写一个量子电路：Apply ctrl<2> X (equivalent to Toffoli) to input |101>. The target q[2] flips only when both q[0] and q[1] are |1>. Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
The circuit applies a doubly-controlled X (Toffoli) gate to input |101>, where the target qubit flips only if both control qubits are |1>.

Three qubits (q[0], q[1], q[2]) are used and all are measured.

State evolution: |000⟩ →X(q[0]), X(q[2])→ |101⟩. The Toffoli gate ctrl<2⟩ X(q[0], q[1], q[2]) checks if q[0]=|1⟩ AND q[1]=|1⟩; since q[1]=|0⟩, the condition fails and q[2] is not flipped, leaving the state as |101⟩.

Expected measurement probabilities: {|101⟩: 1.0}, since the final state is |101⟩ with certainty.

## isqTrain/3958

- task_id: `isqTrain/3958`
- task_type: `bug_fix`
- category: `circuit_patterns`
- difficulty: `difficult`
- concept_tags: `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `425`

### Prompt

There's an error in this quantum circuit implementation. Fix it:

```
import std;
// ctrl<2> X (Toffoli) on input |001>
qbit q[3];

procedure main() {
    // Prepare input |001>
    // BUG: missing gate here
    // Apply doubly-controlled X
    ctrl<2> X(q[0], q[1], q[2]);
    // Measure
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis
1. **The bug** is a missing state preparation gate. The code is intended to evaluate a Toffoli (ctrl<2> X) gate on the input state |001>, but the qubits are initialized to |000>. Without any preparation gates, the circuit evaluates the Toffoli gate on |000>.
2. **The fix** is to add an `X(q[2])` gate before the Toffoli gate to prepare the required |001> input state by flipping the third qubit. 
3. **State evolution**: 
   - Initial state: |000>
   - Apply `X(q[2])`: State becomes |001>
   - Apply `ctrl<2> X(q[0], q[1], q[2])`: The target q[2] flips only if controls q[0] and q[1] are |1>. Since they are |0>, the state remains |001>.

## isqTrain/3913

- task_id: `isqTrain/3913`
- task_type: `bug_fix`
- category: `circuit_patterns`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_for_loop`, `isq_syntax_classical_vars`
- source: `isq_train_cot`
- dataset_index: `507`

### Prompt

修复以下isQ程序中的错误：

```
import std;
// Rotation sweep: apply Rz(i*pi/3) to q[i] for i=0..2
qbit q[3];

procedure main() {
    // Put all qubits in superposition first
    for i in 0:3 {
        H(q[i]);
    }
    // Apply parametric rotation sweep
    for i in 0:3 {
        // Rz angle increases with qubit index
        double angle = i * 3.14159265358979 / 3.0;
    // BUG: missing gate here
    }
    // Measure all qubits
    for i in 0:3 {
        M(q[i]);
    }
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: In the rotation sweep loop, the `double angle` is computed but the `Rz` gate is never actually applied to the qubit. The comment `// BUG: missing gate here` marks where the gate call should be.

2. **Fix**: Add `Rz(angle, q[i]);` on the line marked as the bug, so the computed angle is used to rotate each qubit.

3. **State evolution of corrected circuit**:
   - Initial state: |000⟩
   - After H on all qubits: |+++⟩ = 1/√8 ∑|b₂b₁b₀⟩ (equal superposition over all 8 basis states)
   - After Rz(i·π/3) on q[i]: q[0] gets Rz(0) (identity, no effect), q[1] gets Rz(π/3), q[2] gets Rz(2π/3). Each Rz only adds a relative phase: |+⟩ → (|0⟩ + e^{iθ}|1⟩)/√2. The magnitudes of all amplitudes remain 1/√8.
   - Measurement yields equal probabilities of 0.125 for all 8 outcomes, matching the predicted output.

## isqTrain/3783

- task_id: `isqTrain/3783`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `expert`
- concept_tags: `superposition`, `entanglement`, `isq_syntax_for_loop`, `data_encoding_qml`
- source: `isq_train_cot`
- dataset_index: `3487`

### Prompt

Help me write isQ code that a 4-qubit parameterized quantum ansatz with 2 layer(s). Each layer applies Ry rotations to all qubits followed by a CNOT entangling chain. Use for loops. Measure all 4 qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Build a 4-qubit parameterized ansatz with 2 layers of Ry rotations and CNOT entanglement for variational state preparation.

4 qubits (q[0]-q[3]) are used and all are measured at the end.

**State evolution:**
- Initial: |ψ⟩ = |0000⟩
- Layer 0 rotations: Each Ry(0.5) creates superposition cos(0.25)|0⟩ + sin(0.25)|1⟩ on each qubit, yielding a product state with amplitude ~0.9689 for |0⟩ and ~0.2474 for |1⟩ per qubit.
- Layer 0 CNOT chain: Sequential CNOT(q[i], q[i+1]) entangles qubits, correlating the bit-flip patterns. States like |1010⟩ gain amplitude due to alternating CNOT structure.
- Layer 1 rotations: Ry(0.8) further rotates each qubit (cos(0.4)≈0.9211, sin(0.4)≈0.3894), adding phase interference between basis states.
- Layer 1 CNOT chain: Additional entanglement creates complex superposition across all 16 basis states.

Final state is a fully entangled superposition. Measurement probabilities show non-uniform distribution (e.g., |0000⟩≈0.302 is dominant due to initial |0⟩ bias, while |1001⟩≈0.000025 is suppressed by destructive interference). The two-layer structure with different angles (0.5, 0.8) creates rich correlation patterns visible in the probability spread.

## isqTrain/4006

- task_id: `isqTrain/4006`
- task_type: `bug_fix`
- category: `circuit_patterns`
- difficulty: `difficult`
- concept_tags: `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `4374`

### Prompt

This isQ program compiles but produces incorrect probabilities. Find and correct the mistake.

```
import std;
// T followed by T† = identity
qbit q[1];

procedure main() {
    H(q[0]);
    T(q[0]);
    inv T(q[0]);
    // BUG: missing gate here
    // H then identity then H = identity, so |0>
    M(q[0]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis
1. **The Bug**: The code is missing a closing Hadamard gate (`H(q[0])`). The first `H(q[0])` puts the qubit into the |+> state. The subsequent `T` and `inv T` gates cancel each other out, leaving the qubit in the |+> state. Without a final `H` gate, measuring the qubit would yield |0> and |1> with equal probability.
2. **The Fix**: Insert `H(q[0]);` immediately after `inv T(q[0]);` to complete the identity sequence (H - I - H) and return the qubit to |0>.
3. **State Evolution**: 
   - Initial: |0>
   - `H(q[0])`: |+>
   - `T(q[0])`: T|+>
   - `inv T(q[0])`: |+> (T and T† cancel)
   - `H(q[0])`: |0> (H is self-inverse)
   - Measurement yields P(|0>) = 1.0.
