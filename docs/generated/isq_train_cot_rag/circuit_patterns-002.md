# ISQ training COT RAG corpus: circuit_patterns shard 2

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4043

- task_id: `isqTrain/4043`
- task_type: `bug_fix`
- category: `circuit_patterns`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_for_loop`, `isq_syntax_classical_vars`
- source: `isq_train_cot`
- dataset_index: `3628`

### Prompt

这个isQ程序有问题，请找出错误并给出正确代码：

```
import std;
// Rotation sweep: apply Rz(i*pi/4) to q[i] for i=0..3
qbit q[4];

procedure main() {
    // Put all qubits in superposition first
    for i in 0:4 {
        H(q[i]);
    }
    // Apply parametric rotation sweep
    for i in 0:4 {
        // Rz angle increases with qubit index
        double angle = i * 3.14159265358979 / 4.0;
        Rx(angle, q[i]);
    }
    // Measure all qubits
    for i in 0:4 {
        M(q[i]);
    }
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

## Bug Analysis
1. **The Bug:** The code incorrectly uses an X-axis rotation gate (`Rx`) instead of the Z-axis rotation gate (`Rz`) in the parametric sweep loop, contradicting the task description and inline comments.
2. **The Fix:** Replace `Rx(angle, q[i])` with `Rz(angle, q[i])` to correctly apply the phase rotation.
3. **State Evolution:**
   - Initialize all qubits to the ground state $|0000\rangle$.
   - Apply Hadam

## isqTrain/3772

- task_id: `isqTrain/3772`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_for_loop`, `isq_syntax_classical_vars`
- source: `isq_train_cot`
- dataset_index: `5538`

### Prompt

I need an isQ program to a 5-qubit circuit that applies a rotation sweep: Rz(i*π/5) to qubit q[i] for i=0..4. First apply Hadamard to all qubits using a for loop, then the rotation sweep, then measure all qubits using a for loop.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a 5-qubit circuit that applies a Hadamard and a parameterized Z-rotation to each qubit, then measures them.
2. **Qubits**: 5 qubits are used, and all are measured simultaneously.
3. **Evolution**: The qubits start in the joint state |00000>. Applying a Hadamard to each puts them into an equal superposition: (1/√32) Σ |x₄x₃x₂x₁x₀>.
4. **Rotations**: The `Rz(i*π/5)` gate applies a phase shift to the |1> component of qubit i. This transforms the state to (1/√32) Σ exp(i * π/5 * Σ(xⱼ * j / 2)) |x₄...x₀>.
5. **Probabilities**: Since the Rz gates only alter the relative phases of the basis states and do not change their amplitudes, the measurement probability for each of the 32 possible states remains uniformly 1/32 = 0.03125.

## isqTrain/3861

- task_id: `isqTrain/3861`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `expert`
- concept_tags: `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3889`

### Prompt

Create an isQ quantum circuit that Apply `ctrl nctrl X` to |001>: q[0] is positive control, q[1] is negative control, q[2] is target. Target flips when q[0]=|1> AND q[1]=|0>. Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply a mixed-control X gate (positive control on q[0], negative control on q[1], target q[2]) to state |001>, then measure all qubits.
2. **Qubits**: 3 qubits (q[0], q[1], q[2]), all measured.
3. **State evolution**:
   - Initialize: |000⟩
   - X(q[2]): |000⟩ → |001⟩ (flips q[2])
   - ctrl nctrl X(q[0], q[1], q[2]): Condition requires q[0]=|1⟩ AND q[1]=|0⟩. Since q[0]=|0⟩, condition fails → no flip → state remains |001⟩
4. **Expected result**: Since q[0]=|0⟩, the control condition fails, so the target is unchanged. Final state |001⟩ gives measurement probability {|001⟩: 1.0}.

## isqTrain/3781

- task_id: `isqTrain/3781`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `expert`
- concept_tags: `superposition`, `entanglement`, `isq_syntax_for_loop`, `data_encoding_qml`
- source: `isq_train_cot`
- dataset_index: `4544`

### Prompt

Write an isQ program that a 3-qubit parameterized quantum ansatz with 2 layer(s). Each layer applies Ry rotations to all qubits followed by a CNOT entangling chain. Use for loops. Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Build a 3-qubit parameterized ansatz (depth 2) for variational algorithms using alternating Ry rotations and CNOT entanglement, then measure all qubits.

State evolution (3 qubits, all measured):
1. Initial state: |000⟩
2. Layer 0 - Ry(0.5) on all qubits: (cos(0.25)|0⟩ + sin(0.25)|1⟩)⊗³ ≈ (0.9689|0⟩ + 0.2474|1⟩)⊗³
3. Layer 0 - CNOT chain q[0]→q[1], q[1]→q[2]: entangles adjacent qubits, creating superposition over correlated bitstrings
4. Layer 1 - Ry(0.8) on all qubits: applies additional rotations cos(0.4)|0⟩ + sin(0.4)|1⟩ ≈ 0.9211|0⟩ + 0.3894|1⟩ to each qubit in the entangled basis
5. Layer 1 - CNOT chain: further entangles qubits, mixing amplitudes across computational basis states
6. Final state is a complex entangled superposition; measurement probabilities reflect the cumulative rotation-entanglement structure: highest in |000⟩ (0.389) where both rotation angles favor |0⟩, with asymmetric distribution from the two-layer depth creating non-trivial correlations (e.g., |101⟩ at 0.149 vs |100⟩ at 0.008, showing entanglement effects).

## isqTrain/3901

- task_id: `isqTrain/3901`
- task_type: `bug_fix`
- category: `circuit_patterns`
- difficulty: `expert`
- concept_tags: `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `65`

### Prompt

修复以下isQ程序中的错误：

```
import std;
// ctrl<3> X on input |1111>
qbit q[4];

procedure main() {
    // Prepare |1111>
    X(q[0]);
    X(q[1]);
    X(q[2]);
    X(q[3]);
    // Triple-controlled X
    ctrl<3> Y(q[0], q[1], q[2], q[3]);
    // Measure
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

## Bug Analysis
1. **Bug**: Line `ctrl<3> Y(q[0], q[1], q[2], q[3]);` uses a controlled-Y gate instead of the required controlled-X gate. The task specifies a triple-controlled X, which should flip the target qubit when all controls are |1>.

2. **Fix**: Replace `ctrl<3> Y` with `ctrl<3> X`. The Y gate introduces both a bit-flip and phase-flip, whereas X only performs the required bit-flip.

3. **State evolution (corrected)**:
   - Initial: |0000⟩
   - After X on all qubits: |1111⟩
   - ctrl<3> X with controls q[0],q[1],q[2] on target q[3]: all controls are |1⟩, so X flips q[3] from |1⟩ → |0⟩
   - Result: |1110⟩, matching predicted output probability {|1110⟩: 1.0}

## isqTrain/3936

- task_id: `isqTrain/3936`
- task_type: `bug_fix`
- category: `circuit_patterns`
- difficulty: `difficult`
- concept_tags: `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1406`

### Prompt

Something is wrong with this isQ circuit. Identify the error and provide the corrected code.

```
import std;
// ctrl<2> X (Toffoli) on input |100>
qbit q[3];

procedure main() {
    // Prepare input |100>
    X(q[0]);
    // Apply doubly-controlled X
    ctrl<2> Y(q[0], q[1], q[2]);
    // Measure
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

## Bug Analysis
1. **Bug**: Line `ctrl<2> Y(q[0], q[1], q[2]);` uses the wrong gate (Y instead of X). The task requires a Toffoli (doubly-controlled X) gate.
2. **Fix**: Replace `Y` with `X` so the line becomes `ctrl<2> X(q[0], q[1], q[2]);`.
3. **State evolution**: |000> →(X on q[0])→ |100> →(ctrl<2> X: both controls q[0],q[1] are not |1>, so no flip)→ |100>. Measurement yields |100⟩ with probability 1.0.

## isqTrain/3864

- task_id: `isqTrain/3864`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `expert`
- concept_tags: `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `69`

### Prompt

Implement the following in isQ: Apply `ctrl nctrl X` to |100>: q[0] is positive control, q[1] is negative control, q[2] is target. Target flips when q[0]=|1> AND q[1]=|0>. Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Apply a mixed-control X gate to flip the target qubit when the positive control is |1> and the negative control is |0>.
2. **Qubits:** 3 qubits are initialized, and all 3 are measured.
3. **Evolution:** Initial state is |000>. `X(q[0])` transforms it to |100>. The `ctrl nctrl X` gate evaluates the condition q[0]=|1> and q[1]=|0>. Since the state is |100>, the condition is satisfied, flipping the target q[2] from |0> to |1>.
4. **Probabilities:** The final state is exactly |101>. Measuring all qubits yields the bitstring '101' with a probability of 1.0.

## isqTrain/4023

- task_id: `isqTrain/4023`
- task_type: `bug_fix`
- category: `circuit_patterns`
- difficulty: `difficult`
- concept_tags: `multi_controlled_logic`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `3556`

### Prompt

这个isQ程序有问题，请找出错误并给出正确代码：

```
import std;
// Toffoli gate via defgate perm
defgate MyTof(3) = perm [0, 1, 2, 3, 4, 5, 7, 6];
qbit q[3];

procedure main() {
    // Set both controls to |1>: should flip target
    Y(q[0]);
    X(q[1]);
    MyTof(q[0], q[1], q[2]);
    // Expected: |111>
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

Let me analyze this buggy isQ code.

The code is trying to implement a Toffoli gate using a permutation-based defgate and then test it.

1. The Toffoli gate defined by `defgate MyTof(3) = perm [0, 1, 2, 3, 4, 5, 7, 6]` maps basis states:
   - |000> → |000>
   - |001> → |001>
   - |010> → |010>
   - |011> → |011>
   - |100> → |100>
   - |101> → |101>
   - |110> → |111> (swap 6 and 7)
   - |111> → |110> (swap 6 and 7)
   
   Wait, let me re-read. The permutation [0, 1, 2, 3, 4, 5, 7, 6] means:
   - Index 0 → 0: |000> stays
   - Index 1 → 1: |001> stays
   - Index 2 → 2: |010> stays
   - Index 3 → 3: |011> stays
   - Index 4 → 4: |100> stays
   - Index 5 → 5: |101> stays
   - Index 6 → 7: |110> → |111>
   - Index 7 → 6: |111> → |110>
   
   This is indeed a Toffoli gate - it flips the target (third qubit) when both controls are |1>.

2. The main procedure sets up the initial state:
   - Y(q[0]) puts q[0] in some state
   - X(q[1]) puts q[1] in |1>
   
   For the Toffoli to flip the target, both controls need to be |1>. So q[0] and q[1] should both be |1>.

3. Y gate: Y = [[0,-i],[i,0]], so Y|0⟩ = i|1⟩. This puts q[0] in state i|1⟩, which has a global phase but is effectively |1⟩ in terms of measurement.
   
   Wait, actually Y|0⟩ = [[0,-i],[i,0]][[1],[0]] = [[0],[i]] = i|1⟩.
   
   Hmm, so Y(q[0]) does put q[0] in a state that measures as |1⟩ with probability 1. But the global phase i matters when we consider the full state.
   
   Actually, let me reconsider. Y|0⟩ = i|1⟩. So after Y(q[0]) and X(q[1]), the state is i|110⟩ (since q[2] starts in |0⟩).
   
   Then the Toffoli gate acts on |110⟩ → |111⟩.
   
   So the result should be i|111⟩, which measures as |111⟩ with probability 1.

Wait, that should work then? Let me re-examine...

Actually, wait. The bug type is "wrong_gate". The comment says "Set both controls to |1>: should flip target" and The predicted output |111⟩.

Let me think about what Y does again:
- Y|0⟩ = i|1⟩
- Y|1⟩ = -i|0⟩

So Y(q[0]) on |0⟩ gives i|1⟩. This is effectively |1⟩ up to global phase. The measurement probability should still be 1 for |111⟩.

Hmm, but maybe there's an issue with how Y is defined or the expected behavior?

Actually, let me reconsider. Maybe the bug is that Y is the wrong gate choice here, even though it technically produces the right measurement result. The intent is clearly to set q[0] to |1⟩, and X is the natural gate to use for that. While Y|0⟩ = i|1⟩ gives the same measurement statistics, the comment says "Set both controls to |1⟩" which implies using X gates.

But wait, the expected measurement probabilities say {|111⟩: 1.0}. If Y(q[0]) produces i|1⟩, then the state after all operations would be i|111⟩, which measures as |111⟩ with probability 1. So technically it should work...

Unless the perm gate doesn't handle the phase correctly? Or maybe Y has a different definition in isQ?

Let me look at the X gate: X|0⟩ = |1⟩. This is straightforward.

The fix is to change Y(q[0]) to X(q[0]). This makes both controls |1⟩ without any phase factor, which is cleaner and what the comments indicate was intended

## isqTrain/3773

- task_id: `isqTrain/3773`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_for_loop`, `isq_syntax_classical_vars`
- source: `isq_train_cot`
- dataset_index: `2072`

### Prompt

Create an isQ quantum circuit that a 6-qubit circuit that applies a rotation sweep: Rz(i*π/6) to qubit q[i] for i=0..5. First apply Hadamard to all qubits using a for loop, then the rotation sweep, then measure all qubits using a for loop.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply Hadamard to all 6 qubits, then a rotation sweep Rz(i·π/6) to each qubit q[i], and measure all qubits.

Six qubits are needed (q[0]–q[5]), all measured.

State evolution:
1. Initial state: |000000⟩
2. After H on all qubits: |++++++⟩ = (1/√64) Σ|x⟩ over all 6-bit strings x
3. After Rz(i·π/6) on q[i]: each qubit becomes (|0⟩ + e^(i·iπ/6)|1⟩)/√2, giving state ⊗ᵢ₌₀⁵ (|0ᵢ⟩ + e^(i²π/6)|1ᵢ⟩)/√2

The Rz gates add relative phases but don't change measurement probabilities since they only modify the phase of |1⟩ components. Each computational basis state |x⟩ has |amplitude|² = |1/8|² = 1/64 = 0.015625, yielding uniform distribution over all 64 outcomes.

## isqTrain/3846

- task_id: `isqTrain/3846`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `difficult`
- concept_tags: `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `5`

### Prompt

实现以下量子计算任务（使用isQ）：Define sqrt(X) gate using `defgate` with matrix [[0.5+0.5i, 0.5-0.5i], [0.5-0.5i, 0.5+0.5i]]. Apply it twice to |0> (equivalent to X gate) and verify the result is |1>.

### Chain-of-thought reasoning

## Reasoning
* The goal is to apply a custom $\sqrt{X}$ gate twice to $|0\rangle$, verifying that its square acts identically to the standard Pauli-X gate.
* The circuit requires 1 qubit (`q[0]`), which is initialized to $|0\rangle$ and measured at the end.
* Initial state: $|0\rangle$.
* After 1st SQRTX: state evolves to $\frac{1+i}{2}|0\rangle + \frac{1-i}{2}|1\rangle$.
* After 2nd SQRTX: applying the gate again computes $(\sqrt{X})^2 |0\rangle = X|0\rangle = |1\rangle$.
* Measuring the final state $|1\rangle$ yields the classical outcome 1 with a probability of 1.0.
