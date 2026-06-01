# ISQ training COT RAG corpus: circuit_patterns shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3847

- task_id: `isqTrain/3847`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `difficult`
- concept_tags: `multi_controlled_logic`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `4052`

### Prompt

实现以下量子计算任务（使用isQ）：Define a Toffoli gate using `defgate perm` syntax with permutation [0,1,2,3,4,5,7,6]. Apply to |110> (both controls 1) and verify target flips to give |111>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Define a Toffoli gate via permutation `[0,1,2,3,4,5,7,6]` and verify it flips the target qubit when both controls are |1>.
2. **Qubits**: 3 (q[0], q[1] as controls, q[2] as target); all measured.
3. **State evolution**:
   - |000⟩ → X(q[0]) → |100⟩
   - |100⟩ → X(q[1]) → |110⟩
   - |110⟩ → MyTof → |111⟩ (permutation swaps basis indices 6↔7, flipping the target when both controls are 1)
4. **Expected result**: Final state |111⟩ yields measurement probability {|111⟩: 1.0}.

## isqTrain/4045

- task_id: `isqTrain/4045`
- task_type: `bug_fix`
- category: `circuit_patterns`
- difficulty: `expert`
- concept_tags: `superposition`, `entanglement`, `isq_syntax_for_loop`, `data_encoding_qml`
- source: `isq_train_cot`
- dataset_index: `5143`

### Prompt

This isQ program compiles but produces incorrect probabilities. Find and correct the mistake.

```
import std;
// 4-qubit parameterized ansatz, depth 1
qbit q[4];

procedure main() {
    // Layer 0: rotation + entanglement
    for i in 0:4 {
        Ry(0.500, q[i]);
    }
    for i in 0:3 {
        CZ(q[i], q[i + 1]);
    }
    // Measure all qubits
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: The entanglement layer uses `CZ(q[i], q[i + 1])` instead of `CNOT(q[i], q[i + 1])`. CZ applies a phase flip (Z) to the target when control is |1⟩, while CNOT flips the target (X) when control is |1⟩. These produce different entangled states and thus different measurement probabilities.

2. **Fix**: Replace `CZ(q[i], q[i + 1])` with `CNOT(q[i], q[i + 1])` in the entanglement loop (lines 10-12).

3. **State evolution (corrected)**:
   - Initial: |0000⟩
   - After Ry(0.5) on all qubits: (cos(0.25)|0⟩ + sin(0.25)|1⟩)⊗⁴ ≈ (0.9689|0⟩ + 0.2474|1⟩)⊗⁴
   - Product state has nonzero amplitudes for all 16 basis states, dominated by |0000⟩
   - CNOT(q[0],q[1]) flips q[1] conditioned on q[0]=|1⟩, redistributing amplitude between |x0..⟩ and |x1..⟩ patterns
   - Sequential CNOTs chain entanglement through q[0]→q[1]→q[2]→q[3]
   - Final probabilities match predicted output, with |0000⟩ ≈ 0.777 and odd-parity/alternating states suppressed due to CNOT correlations

## isqTrain/3981

- task_id: `isqTrain/3981`
- task_type: `bug_fix`
- category: `circuit_patterns`
- difficulty: `expert`
- concept_tags: `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `4968`

### Prompt

Something is wrong with this isQ circuit. Identify the error and provide the corrected code.

```
import std;
// Mixed control: ctrl q[0], nctrl q[1], target q[2]
qbit q[3];

procedure main() {
    // BUG: missing gate here
    X(q[2]);
    // Flip q[2] when q[0]=|1> and q[1]=|0>
    ctrl nctrl X(q[0], q[1], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug identification**: The code is missing `X(q[1])` before `X(q[2])`. The task requires preparing state |011>, but the buggy code only initializes q[2]=|1>, leaving q[0]=|0> and q[1]=|0>.

2. **Fix**: Add `X(q[1])` to set q[1] to |1>, completing the preparation of |011>:
   - `X(q[1])` — sets q[1] to |1>
   - `X(q[2])` — sets q[2] to |1>

3. **State evolution of corrected circuit**:
   - Start: |000>
   - After X(q[1]): |010>
   - After X(q[2]): |011>
   - Apply ctrl nctrl X(q[0], q[1], q[2]): Flips q[2] when q[0]=|1> AND q[1]=|0>. Here q[0]=|0>, so condition fails → no flip
   - Final state: |011> ✓

The measurement probabilities confirm correctness: {|011>: 1.0}.

## isqTrain/3890

- task_id: `isqTrain/3890`
- task_type: `bug_fix`
- category: `circuit_patterns`
- difficulty: `difficult`
- concept_tags: `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `5551`

### Prompt

The following isQ code has a bug. Find and fix it.

Buggy code:
```
import std;
// ctrl<2> X (Toffoli) on input |011>
qbit q[3];

procedure main() {
    // Prepare input |011>
    X(q[1]);
    // BUG: missing gate here
    // Apply doubly-controlled X
    ctrl<2> X(q[0], q[1], q[2]);
    // Measure
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis
1. **The bug** is a missing `X(q[2])` gate. The task specifies the input state should be |011>, meaning `q[0]`=|0>, `q[1]`=|1>, and `q[2]`=|1>. However, the buggy code only applies `X(q[1])`, which prepares the state |010>.
2. **The fix** is to add `X(q[2])` to correctly prepare the required input state |011>.
3. **State evolution** of the corrected circuit:
- Initial state is |000>.
- `X(q[1])` flips the second qubit to yield |010>.
- `X(q[2])` flips the third qubit to yield |011>.
- `ctrl<2> X(q[0], q[1], q[2])` (Toffoli gate) targets `q[2]` with controls on `q[0]` and `q[1]`. Since `q[0]` is |0>, the control condition is not met, leaving the state unchanged as |011>.

## isqTrain/3859

- task_id: `isqTrain/3859`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `expert`
- concept_tags: `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `3619`

### Prompt

请用isQ语言编写一个量子电路：Apply ctrl<3> X to input |1111>. Target q[3] flips only when q[0], q[1], q[2] are all |1>. Measure all 4 qubits.

### Chain-of-thought reasoning

## Reasoning
The goal is to apply a triple-controlled X gate to a 4-qubit register initialized to |1111>.
Four qubits are used (q[0] to q[3]), and all are measured.
1. Initialize the quantum state to |0000>.
2. Apply X gates to all four qubits to prepare the initial state |1111>.
3. Apply `ctrl<3> X(q[0], q[1], q[2], q[3])`. Since the control qubits q[0], q[1], and q[2] are all in the |1> state, the target qubit q[3] flips from |1> to |0>.
4. The quantum state evolves to |1110>.
Measurement of this final state yields the bitstring 1110 with a probability of 1.0.

## isqTrain/3848

- task_id: `isqTrain/3848`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `difficult`
- concept_tags: `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `4522`

### Prompt

Write isQ code for the following quantum task: Apply ctrl<2> X (equivalent to Toffoli) to input |000>. The target q[2] flips only when both q[0] and q[1] are |1>. Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply a Toffoli (ctrl<2> X) gate to the initial state |000> and measure the qubits.
Qubits: 3 qubits (q[0], q[1], q[2]) are used, and all are measured.
Evolution: The system initializes to |000>. The ctrl<2> X gate targets q[2], conditioned on both q[0] and q[1] being |1>. Since the control qubits are in the |0> state, the target is not flipped, leaving the state unchanged as |000>.
Probabilities: Because the final quantum state is exactly |000>, measuring the system yields the bitstring 000 with a probability of 1.0.

## isqTrain/3770

- task_id: `isqTrain/3770`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_for_loop`, `isq_syntax_classical_vars`
- source: `isq_train_cot`
- dataset_index: `2917`

### Prompt

Write isQ code for the following quantum task: a 3-qubit circuit that applies a rotation sweep: Rz(i*π/3) to qubit q[i] for i=0..2. First apply Hadamard to all qubits using a for loop, then the rotation sweep, then measure all qubits using a for loop.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Apply Hadamard to 3 qubits, then Rz(i·π/3) to q[i], creating a rotation sweep with increasing angles.

2. **Qubits**: 3 qubits (q[0], q[1], q[2]), all measured.

3. **State evolution**:
   - Initial: |000⟩
   - After H⊗3: |+⟩|+⟩|+⟩ = (1/√8)Σ_{b₂b₁b₀∈{0,1}}|b₂b₁b₀⟩
   - After Rz(0) on q[0]: No change (angle=0)
   - After Rz(π/3) on q[1]: Phase e^(iπ/3) applied to |1⟩ component of q[1]
   - After Rz(2π/3) on q[2]: Phase e^(i2π/3) applied to |1⟩ component of q[2]
   - Final: (1/√8)Σ_{b₂b₁b₀} e^(ib₂·2π/3)·

## isqTrain/4029

- task_id: `isqTrain/4029`
- task_type: `bug_fix`
- category: `circuit_patterns`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_for_loop`, `isq_syntax_classical_vars`
- source: `isq_train_cot`
- dataset_index: `1516`

### Prompt

下面的量子程序运行结果不对，请帮我debug：

```
import std;
// Rotation sweep: apply Rz(i*pi/6) to q[i] for i=0..5
qbit q[6];

procedure main() {
    // Put all qubits in superposition first
    for i in 0:6 {
        H(q[i]);
    }
    // Apply parametric rotation sweep
    for i in 0:6 {
        // Rz angle increases with qubit index
        double angle = i * 3.14159265358979 / 6.0;
    // BUG: missing gate here
    }
    // Measure all qubits
    for i in 0:6 {
        M(q[i]);
    }
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis
1. **What the bug is**: The `angle` variable is computed in the second `for` loop, but no parametric rotation gate is actually applied to the qubits. The code is missing the `Rz` gate execution.
2. **What the fix is**: Insert `Rz(angle, q[i]);` inside the second loop body where the `// BUG` comment is located.
3. **Brief state evolution of the corrected circuit**: 
   - Initialize to $|000000\rangle$.
   - Apply $H$ to all qubits, resulting in the superposition $|+\rangle^{\otimes 6} = \frac{1}{\sqrt{64}} \sum_{x=0}^{63} |x\rangle$.
   - Apply the computed $Rz$ rotations. Since $Rz$ only imparts relative phases to the $|0\rangle$ and $|1\rangle$ states, the computational basis measurement probabilities remain completely unchanged.
   - Measure all qubits in the $Z$-basis, producing a uniform probability distribution of $0.015625$ ($1/64$) for all 64 possible basis states.

## isqTrain/3868

- task_id: `isqTrain/3868`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `difficult`
- concept_tags: `isq_syntax_inv`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2185`

### Prompt

Implement a quantum circuit in isQ: Apply S gate followed by inv S (S†) to qubit in |1> state. Verify the inverse cancels the gate, leaving |1>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply the S gate followed by its inverse (S†) to a |1⟩ state to verify they perfectly cancel each other out.
2. **Qubits**: Requires 1 qubit (`q[0]`), which is measured at the end.
3. **State Evolution**:
   - Start in the ground state |0⟩, then apply the X gate to initialize to |1⟩.
   - Apply the S gate, which adds a relative phase of $i$, changing the state to $i|1\rangle$.
   - Apply `inv S` (S†), which applies a phase of $-i$, returning the state to exactly $|1\rangle$.
4. **Probabilities**: Because the final quantum state is exactly |1⟩, the measurement yields |1⟩ with a probability of 1.0.

## isqTrain/3856

- task_id: `isqTrain/3856`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `expert`
- concept_tags: `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `4926`

### Prompt

帮我写一个isQ程序：Apply ctrl<3> X to input |0000>. Target q[3] flips only when q[0], q[1], q[2] are all |1>. Measure all 4 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Apply a triple-controlled X gate to a 4-qubit zero state and measure the outcome.
2. **Qubits:** 4 qubits (`q[0]`, `q[1]`, `q[2]`, `q[3]`) are used, and all are measured.
3. **Evolution:** The initial state is `|0000>`. Applying `ctrl<3> X(q[0], q[1], q[2], q[3])` attempts to flip target `q[3]` only if controls `q[0]`, `q[1]`, and `q[2]` are all `|1>`. 
4. Since the control qubits are `|0>`, the condition is not met, the target is not flipped, and the state remains exactly `|0000>`.
5. **Probabilities:** Because the
