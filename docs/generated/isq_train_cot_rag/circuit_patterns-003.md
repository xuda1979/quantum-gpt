# ISQ training COT RAG corpus: circuit_patterns shard 3

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3877

- task_id: `isqTrain/3877`
- task_type: `bug_fix`
- category: `circuit_patterns`
- difficulty: `difficult`
- concept_tags: `isq_syntax_inv`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `1170`

### Prompt

This isQ program doesn't produce the correct output. Can you debug it?

Code:
```
import std;
// Inverse of a custom procedure
qbit q[2];

unit my_circuit(qbit q[2]) {
    H(q[0]);
    CNOT(q[0], q[1]);
    S(q[0]);
} deriving gate

procedure main() {
    // Apply circuit then its inverse: net = identity
    // BUG: missing gate here
    my_circuit(q);
    inv my_circuit(q);
    // Should still be |10>
    M(q[0]); M(q[1]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis
1. **Bug**: A missing `X(q[0])` gate before `my_circuit(q)`. The code applies `my_circuit` then its inverse (`inv my_circuit`), which nets to identity. Starting from |00⟩, the result would be |00⟩, but The predicted output |10⟩.

2. **Fix**: Add `X(q[0])` before `my_circuit(q)` to prepare the initial state as |10⟩. Since `my_circuit` followed by `inv my_circuit` is the identity, the state |10⟩ is preserved.

3. **State evolution**:
   - |00⟩ — initial state
   - X(q[0]) → |10⟩
   - my_circuit(q) → some entangled state (H, CNOT, S applied)
   - inv my_circuit(q) → |10⟩ (inverse cancels exactly)
   - Measure: |10⟩ with probability 1.0

## isqTrain/4076

- task_id: `isqTrain/4076`
- task_type: `bug_fix`
- category: `circuit_patterns`
- difficulty: `expert`
- concept_tags: `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `1055`

### Prompt

The following isQ code has a bug. Find and fix it.

Buggy code:
```
import std;
// Mixed control: ctrl q[0], nctrl q[1], target q[2]
qbit q[3];

procedure main() {
    X(q[0]);
    X(q[1]);
    // BUG: missing gate here
    // Flip q[2] when q[0]=|1> and q[1]=|0>
    ctrl nctrl X(q[0], q[1], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis
1. **Bug**: Missing `X(q[2])` gate. The code initializes only q[0] and q[1] to |1>, leaving q[2] in |0>, so the initial state is |110⟩ instead of the required |111⟩.

2. **Fix**: Add `X(q[2])` before the mixed-control gate to prepare the state |111⟩.

3. **State evolution** (corrected):
   - |000⟩ → X(q[0]), X(q[1]), X(q[2]) → |111⟩
   - ctrl nctrl X(q[0], q[1], q[2]): condition is q[0]=|1⟩ AND q[1]=|0⟩; since q[1]=|1⟩, the gate does NOT fire
   - Final state: |111⟩ → measurement yields |111⟩ with probability 1.0

## isqTrain/4026

- task_id: `isqTrain/4026`
- task_type: `bug_fix`
- category: `circuit_patterns`
- difficulty: `expert`
- concept_tags: `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `3268`

### Prompt

这个isQ程序有问题，请找出错误并给出正确代码：

```
import std;
// ctrl<3> X on input |0000>
qbit q[4];

procedure main() {
    // Prepare |0000>
    // All qubits |0>
    // Triple-controlled X
    ctrl<3> Y(q[0], q[1], q[2], q[3]);
    // Measure
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

## Bug Analysis
1. **Bug**: Line `ctrl<3> Y(q[0], q[1], q[2], q[3])` uses a triple-controlled **Y** gate instead of the required triple-controlled **X** gate.
2. **Fix**: Replace `ctrl<3> Y` with `ctrl<3> X`.
3. **State evolution (corrected)**: Initial state is |0000⟩. The `ctrl<3> X` gate flips q[3] only when controls q[0], q[1], q[2] are all |1⟩. Since they are all |0⟩, the gate does not trigger and the state remains |0000⟩. Measurements yield |0000⟩ with probability 1.0.

## isqTrain/4063

- task_id: `isqTrain/4063`
- task_type: `bug_fix`
- category: `circuit_patterns`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `1750`

### Prompt

The following isQ code has a bug. Find and fix it.

Buggy code:
```
import std;
// CNOT chain: propagate |1> through 4 qubits
qbit q[4];

procedure main() {
    // Set first qubit to |1>
    Y(q[0]);
    // Propagate via CNOT chain
    for i in 0:3 {
        CNOT(q[i], q[i + 1]);
    }
    // All qubits should now be |1>
    for i in 0:4 {
        M(q[i]);
    }
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

The user wants a bug analysis for the given isQ quantum code.
The buggy code uses the `Y` gate instead of the `X` gate to set the first qubit to |1>.

1.  **Identify the bug**: The buggy code uses `Y(q[0])` to set the first qubit to |1>. Wait, the comment says "Set first qubit to |1>". The `Y` gate on |0> gives `i|1>`. The `X` gate on |0> gives |1>. Both have a probability of 1 of measuring |1>. However, if The predicted output `{|1111>: 1.0}`, the global phase `i` per qubit won't affect measurement probabilities. Let's re-read carefully.
Ah, wait. `Y` gate applied to |0> results in `i|1>`.
Wait, no! `Y = [[0, -i], [i, 0]]`.
Applying Y to |0>:
`Y |0> = [[0, -i], [i, 0]] [1, 0]^T = [0, i]^T = i|1>`.
So `Y` *does* produce the |1> state (up to a global phase).
Wait, if Y sets it to |1>, why is it the wrong gate?
Let me check the exact matrices.
X = [[0,1],[1,0]] -> X|0> = |1>
Y = [[0,-i],[i,0]] -> Y|0> = i|1>

Wait, is there a difference in what the prompt says?
"Buggy code: Y(q[0]);"
"Correct (fixed) code: X(q[0]);"

Why is Y the wrong gate? Because Y introduces a relative phase? No, on |0> it introduces a global phase. But wait, maybe the standard way to flip |0> to |1> is X?
Or maybe the prompt implies that setting to |1> is best done by X?
Let me double check the prompt: "Bug type: wrong_gate".
Wait, let's look at the output of `Y(q[0])`.
If the first qubit is `i|1>`, then `CNOT(i|1>, |0>)` produces `i|11>`.
Then the final state is `i^1 |1111>` (actually `i|1111>`), which has probability 1 to measure |1111>. So `Y(q[0])` actually gives `{|1111>: 1.0}`!
But the bug fix task explicitly says: "Fix the code so it produces the correct output." and "Buggy code: Y(q[0]);" "Correct (fixed) code: X(q[0]);".

If Y gives the exact same measurement probabilities, why is it considered a bug?
Perhaps because the comment says "Set first qubit to |1>", and X maps |0> to exactly |1> without a global phase, whereas Y maps |0> to i|1>.
Or perhaps `Y` was supposed to be `X` because X is the standard bit-flip gate. The prompt states "Bug type: wrong_gate". I will just explain that X maps |0> to |1>, while Y maps |0> to i|1>. The task requires X.
Let's write down the state evolution for the corrected circuit:
1. All qubits start in |0>. State is |0000>.
2. Apply X to q[0]. State becomes |1000>.
3. CNOT(q[0], q[1]) flips q[1] because q[0] is |1>. State becomes |1100>.
4. CNOT(q[1], q[2]) flips q[2]. State becomes |1110>.
5. CNOT(q[2], q[3]) flips q[3]. State becomes |1111>.
6. All qubits are measured, probability of |1111> is 1.0.

Let's double check the bug analysis requirements:
1. What the bug is (which gate/line is wrong and why)
2. What the fix is (what needs to change)
3. Brief state evolution of the corrected circuit to confirm correctness

Is there any error in the loop?
`for i in 0:3 { CNOT(q[i], q[i + 1]); }`
In 0:3 means i = 0, 1, 2. Length 3.
i=0: CNOT(q[0], q[1])
i=1: CNOT(q[1], q[2])
i=2: CNOT(q[2], q[3])
This covers all 3 CNOTs needed for 4 qubits.
And `for i in 0:4` means i=0,

## isqTrain/3860

- task_id: `isqTrain/3860`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `expert`
- concept_tags: `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `902`

### Prompt

Create an isQ quantum circuit that Apply `ctrl nctrl X` to |000>: q[0] is positive control, q[1] is negative control, q[2] is target. Target flips when q[0]=|1> AND q[1]=|0>. Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply a mixed-control X gate (positive control on q[0], negative control on q[1], target on q[2]) to |000⟩ and measure all qubits.
2. **Qubits**: 3 qubits (q[0], q[1], q[2]), all measured.
3. **State evolution**:
   - Initial state: |000⟩
   - The `ctrl nctrl X` gate flips q[2] only when q[0]=|1⟩ AND q[1]=|0⟩
   - For |000⟩: q[0]=|0⟩ (fails positive control), so the condition is not met
   - No flip occurs; final state remains |000⟩
4. **Probabilities**: {|000⟩: 1.0} — the control condition fails, so the target is never flipped.

## isqTrain/4059

- task_id: `isqTrain/4059`
- task_type: `bug_fix`
- category: `circuit_patterns`
- difficulty: `expert`
- concept_tags: `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1958`

### Prompt

This isQ program doesn't produce the correct output. Can you debug it?

Code:
```
import std;
// ctrl<3> X on input |0111>
qbit q[4];

procedure main() {
    // Prepare |0111>
    X(q[1]);
    Y(q[2]);
    X(q[3]);
    // Triple-controlled X
    ctrl<3> X(q[0], q[1], q[2], q[3]);
    // Measure
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

Analyzing the buggy code for `ctrl<3> X on |0111>`:

1. What the bug is:
The bug is on line `Y(q[2]);` which should be `X(q[2]);`. The task requires preparing the state |0111>, meaning q[0]=|0⟩, q[1]=|1⟩, q[2]=|1⟩, q[3]=|1⟩. The Y gate, while it does flip |0⟩ to |1⟩ (up to a global phase), introduces a phase factor of i, potentially affecting the state. However, more critically for the preparation, Y(q[2]) actually does flip |0⟩ to |1⟩ (Y|0⟩ = i|1⟩). 

Actually, let me reconsider. The Y gate matrix is [[0,-i],[i,0]], so Y|0⟩ = i|1⟩ and Y|1⟩ = -i|0⟩. So Y does flip |0⟩ to |1⟩ but with a phase of i.

The issue is that the code should use X gates to prepare |0111⟩ cleanly without extra phases. Using Y instead of X introduces an unwanted global phase factor. While for measurement probabilities this might not matter, the "correct" preparation should use X gates consistently.

Wait, but The predicted output {|0111>: 1.0}, and with Y(q[2]), the state before the ctrl<3> X would be i|0111⟩, which after the triple-controlled X would become i|1111⟩. So the measurement result would be |1111⟩ with probability 1.0, not |0111⟩.

Wait, let me reconsider. The ctrl<3> X flips q[0] when q[1], q[2], q[3] are all |1⟩. So starting from |0111⟩, all three controls (q[1], q[2], q[3]) are |1⟩, so q[0] (which is |0⟩) gets flipped to |1⟩, giving |1111⟩.

But the expected measurement probabilities are {|0111>: 1.0}. That seems contradictory...

Hmm, let me re-read the task. "ctrl<3> X on input |0111>". The predicted output {|0111>: 1.0}. 

Wait, maybe the ctrl<3> X syntax in isQ has a specific order. Let me look at the syntax: `ctrl<3> X(q[0], q[1], q[2], q[3])`. This means q[0] is the target and q[1], q[2], q[3] are controls? Or is q[3] the target?

In isQ, `ctrl<3> X(q[0], q[1], q[2], q[3])` - typically the last qubit is the target in the ctrl modifier syntax. So q[3] would be the target, and q[0], q[1], q[2] are controls.

With input |0111⟩: q[0]=|0⟩, q[1]=|1⟩, q[2]=|1⟩, q[3]=|1⟩.
Controls are q[0], q[1], q[2]. q[0]=|0⟩, so not all controls are |1⟩. The ctrl<3> X does NOT fire. The state remains |0111⟩.

So the predicted output |0111⟩ with probability 1.0 makes sense!

Now, with the buggy code using Y(q[2]) instead of X(q[2]):
- Y|0⟩ = i|1⟩
- So the state becomes: |0⟩ ⊗ |1⟩ ⊗ i|1⟩ ⊗ |1⟩ = i|0111⟩
- ctrl<3> X: controls q[0]=|0⟩, q[1]=|1⟩, q[2]=|1⟩ → q[0] is not |1⟩, so gate doesn't fire
- State remains i|0111⟩ → measurement gives |0111⟩ with probability 1.0

Hmm, so actually the Y gate would give the same measurement result because the global phase i doesn't affect measurements. So the bug might be more subtle.

Wait, but the task says the bug type is "wrong_gate" and the fix changes Y to X. Maybe the bug is just that Y is the wrong gate to use for preparing |1⟩ state, even though it gives the same measurement outcome due to global phase. The "correct" way to prepare |0111⟩ is with X gates.

Actually, Analyzing theed code, the only change is Y(q[2]) → X(q[2]). The fix

## isqTrain/3780

- task_id: `isqTrain/3780`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `difficult`
- concept_tags: `superposition`, `entanglement`, `isq_syntax_for_loop`, `data_encoding_qml`
- source: `isq_train_cot`
- dataset_index: `4537`

### Prompt

Write an isQ program that a 3-qubit parameterized quantum ansatz with 1 layer(s). Each layer applies Ry rotations to all qubits followed by a CNOT entangling chain. Use for loops. Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Build a 3-qubit parameterized ansatz (depth 1) with Ry(0.5) rotations on all qubits followed by a CNOT entangling chain, then measure.

2. **Qubits**: 3 qubits (q[0], q[1], q[2]), all measured.

3. **State evolution**:
   - **Initial**: |000⟩
   - **After Ry(0.5) on all qubits**: Product state (c|0⟩ + s|1⟩)⊗

## isqTrain/3899

- task_id: `isqTrain/3899`
- task_type: `bug_fix`
- category: `circuit_patterns`
- difficulty: `difficult`
- concept_tags: `superposition`, `entanglement`, `isq_syntax_for_loop`, `data_encoding_qml`
- source: `isq_train_cot`
- dataset_index: `5295`

### Prompt

Something is wrong with this isQ circuit. Identify the error and provide the corrected code.

```
import std;
// 3-qubit parameterized ansatz, depth 1
qbit q[3];

procedure main() {
    // Layer 0: rotation + entanglement
    for i in 0:3 {
        Rz(0.500, q[i]);
    }
    for i in 0:2 {
        CNOT(q[i], q[i + 1]);
    }
    // Measure all qubits
    M(q[0]);
    M(q[1]);
    M(q[2]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

## Bug Analysis
1. **Bug**: The rotation layer uses `Rz(0.500, q[i])` instead of `Ry(0.500, q[i])`. Since Rz only applies a phase to |0> (Rz(θ)|0> = e^{-iθ/2}|0>), it doesn't change measurement probabilities. Starting from |000>, Rz on all qubits followed by CNOTs yields |000> with probability 1, contradicting the expected diverse distribution.

2. **Fix**: Replace `Rz` with `Ry` in the rotation loop. Ry(θ)|0> = cos(θ/2)|0> + sin(θ/2)|1>, creating genuine superposition amplitudes that propagate through the CNOT entangling layer.

3. **State evolution (corrected)**:
   - Initial: |000>
   - After Ry(0.5) on all qubits: (cos(0.25)|0> + sin(0.25)|1>)⊗³ ≈ 0.910|000> + 0.233|001> + ... (8 terms)
   - CNOT(q[0],q[1]): flips q[1] when q[0]=|1>, creating entanglement
   - CNOT(q[1],q[2]): flips q[2] when q[1]=|1>, further entangling
   - Resulting non-trivial measurement distribution matches expected: {|000>: 0.827, |001>: 0.054, |010>: 0.004, ...}

## isqTrain/3774

- task_id: `isqTrain/3774`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `3925`

### Prompt

实现以下量子计算任务（使用isQ）：a 4-qubit CNOT chain: set q[0] to |1>, then use a for loop to apply CNOT(q[i], q[i+1]) for i=0..2. This should propagate the |1> to all qubits. Measure all 4 qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Propagate a |1⟩ state through a 4-qubit CNOT chain to demonstrate entanglement propagation.
Four qubits are used, and all four are measured at the end.
State evolution: |0000⟩ →(X on q[0])→ |1000⟩ →(CNOT q[0]→q[1])→ |1100⟩ →(CNOT q[1]→q[2])→ |1110⟩ →(CNOT q[2]→q[3])→ |1111⟩.
Each CNOT copies the |1⟩ from control to target (since X flips |0⟩→|1⟩ when control is |1⟩).
Final state |1111⟩ yields measurement outcome 1111 with probability 1.0.

## isqTrain/3992

- task_id: `isqTrain/3992`
- task_type: `bug_fix`
- category: `circuit_patterns`
- difficulty: `expert`
- concept_tags: `entanglement`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `3855`

### Prompt

There's an error in this quantum circuit implementation. Fix it:

```
import std;
// CNOT chain: propagate |1> through 5 qubits
qbit q[5];

procedure main() {
    // Set first qubit to |1>
    X(q[0]);
    // Propagate via CNOT chain
    for i in 0:4 {
    // BUG: missing gate here
    }
    // All qubits should now be |1>
    for i in 0:5 {
        M(q[i]);
    }
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: The loop body is empty — the CNOT gate that should propagate the |1⟩ state from q[i] to q[i+1] is missing. Without it, only q[0] becomes |1⟩; qubits q[1]–q[4] remain |0⟩.

2. **Fix**: Add `CNOT(q[i], q[i + 1]);` inside the for loop to chain each qubit to the next, copying the |1⟩ state forward.

3. **State evolution (corrected)**:
   - |00000⟩ → X(q[0]) → |10000⟩
   - CNOT(q[0],q[1]) → |11000⟩
   - CNOT(q[1],q[2]) → |11100⟩
   - CNOT(q[2],q[3]) → |11110⟩
   - CNOT(q[3],q[4]) → |11111⟩
   - Final measurement yields {|11111⟩: 1.0}, confirming all qubits are |1⟩.
