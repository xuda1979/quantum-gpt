# ISQ training COT RAG corpus: circuit_patterns shard 6

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3869

- task_id: `isqTrain/3869`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `difficult`
- concept_tags: `isq_syntax_inv`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `1105`

### Prompt

实现以下量子计算任务（使用isQ）：Define a procedure with H, CNOT, S gates using `deriving gate`. Apply the procedure then `inv` of the procedure. Starting from |10>, the net effect should be identity. Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Apply a custom unitary then its inverse to verify they cancel, returning to the initial state |10>.
2. **Qubits:** 2 qubits (q[0], q[1]), both measured.
3. **State evolution:**
   - Start: |00>, then X(q[0]) → |10>
   - `my_circuit`: H(q[0]) on |10> → (1/√2)(|00> − |10>); CNOT → (1/√2)(|00> − |11>); S(q[0]) → (1/√2)(|00> − i|11>)
   - `inv my_circuit` = S†→CNOT→H: S†(q[0]) → (1/√2)(|00> − |11>); CNOT → (1/√2)(|00> − |10>); H(q[0]) → |10>
4. **Expected probabilities:** The unitary and its inverse cancel exactly, yielding |10> with probability 1.0.

## isqTrain/4066

- task_id: `isqTrain/4066`
- task_type: `bug_fix`
- category: `circuit_patterns`
- difficulty: `difficult`
- concept_tags: `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `5178`

### Prompt

This isQ program compiles but produces incorrect probabilities. Find and correct the mistake.

```
import std;
// nctrl X: flip q[1] when q[0] = |0>
qbit q[2];

procedure main() {
    // All |0>
    // Negative-controlled X: active when control is |0>
    // BUG: missing gate here
    M(q[0]); M(q[1]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis
1. **Bug**: The `nctrl X(q[0], q[1]);` gate is entirely missing from the code.
2. **Fix**: Add `nctrl X(q[0], q[1]);` before the measurements.
3. **State evolution**:
   - Initial state: $|00\rangle$
   - Apply `nctrl X(q[0], q[1])`: Because $q[0] = |0\rangle$, the X gate activates on $q[1]$. State $\rightarrow |01\rangle$.
   - Measure: yields $|01\rangle$ with probability 1.0.

## isqTrain/4027

- task_id: `isqTrain/4027`
- task_type: `bug_fix`
- category: `circuit_patterns`
- difficulty: `expert`
- concept_tags: `superposition`, `entanglement`, `isq_syntax_for_loop`, `data_encoding_qml`
- source: `isq_train_cot`
- dataset_index: `4386`

### Prompt

这个isQ程序有问题，请找出错误并给出正确代码：

```
import std;
// 3-qubit parameterized ansatz, depth 2
qbit q[3];

procedure main() {
    // Layer 0: rotation + entanglement
    for i in 0:3 {
    // BUG: missing gate here
    }
    for i in 0:2 {
        CNOT(q[i], q[i + 1]);
    }
    // Layer 1: rotation + entanglement
    for i in 0:3 {
        Ry(0.800, q[i]);
    }
    for i in 0:2 {
        CNOT(q[i], q[i + 1]);
    }
    // Measure all qubits
    M(q[0]);
    M(q[1]);
    M(q[2]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **What the bug is**: In Layer 0's rotation loop (`for i in 0:3`), the body is empty — the `Ry` rotation gate is missing. Layer 0 is supposed to apply a parameterized rotation to each qubit before entanglement, mirroring the structure of Layer 1, but the loop does nothing.

2. **What the fix is**: Add `Ry(0.500, q[i]);` inside the Layer 0 loop. This matches the ansatz pattern where each layer consists of single-qubit `Ry` rotations followed by a CNOT entangling chain.

3. **State evolution of the corrected circuit**:
   - **Init**: All qubits in |000⟩
   - **Layer 0 rotations**: Ry(0.500) on each qubit rotates |0⟩ → cos(0.25)|0⟩ + sin(0.25)|1⟩, producing a product state with amplitudes proportional to (cos(0.25), sin(0.25)) on each qubit
   - **Layer 0 entanglement**: CNOT(q[0],q[1]) then CNOT(q[1],q[2]) creates correlations between neighboring qubits
   - **Layer 1 rotations**: Ry(0.800) further rotates each qubit, mixing the amplitudes
   - **Layer 1 entanglement**: Second CNOT chain adds additional correlations
   - **Measurement**: Yields the expected distribution with |000⟩ dominant at ~0.389 and |001⟩ at ~0.176, confirming the corrected two-layer ansatz

## isqTrain/3775

- task_id: `isqTrain/3775`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `expert`
- concept_tags: `entanglement`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `4454`

### Prompt

Write an isQ program that a 5-qubit CNOT chain: set q[0] to |1>, then use a for loop to apply CNOT(q[i], q[i+1]) for i=0..3. This should propagate the |1> to all qubits. Measure all 5 qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Propagate a |1> state across a 5-qubit chain via CNOT gates to create an all-|1> state.
Qubits: 5 qubits are used (q[0] to q[4]), and all 5 are measured at the end.
Step 1: X(q[0]) flips the first qubit, evolving the initial |00000> state to |10000>.
Step 2-5: A sequence of CNOT gates propagates the |1> state rightwards:
- CNOT(q[0], q[1]) results in |11000>
- CNOT(q[1], q[2]) results in |11100>
- CNOT(q[2], q[3]) results in |11110>
- CNOT(q[3], q[4]) results in |11111>
Probabilities: The final quantum state is deterministically |11111>, yielding a 100% probability of measuring the bitstring 11111.

## isqTrain/3930

- task_id: `isqTrain/3930`
- task_type: `bug_fix`
- category: `circuit_patterns`
- difficulty: `expert`
- concept_tags: `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `1425`

### Prompt

Fix the bug in this quantum program:

```
import std;
// Mixed control: ctrl q[0], nctrl q[1], target q[2]
qbit q[3];

procedure main() {
    // BUG: missing gate here
    X(q[1]);
    // Flip q[2] when q[0]=|1> and q[1]=|0>
    ctrl nctrl X(q[0], q[1], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis
1. **Bug**: The missing gate is `X(q[0])`. The task requires operating on the initial state |110>, which means both q[0] and q[1] must be flipped to |1>. The buggy code only flips q[1], resulting in the state |010>.
2. **Fix**: Add `X(q[0])` before the mixed-control gate. This correctly initializes the state to |110>.
3. **State Evolution**: 
   - Start in |000>. Apply X(q[0]) and X(q[1]) to prepare |110>.
   - Apply `ctrl nctrl X(q[0], q[1], q[2])`. The condition requires q[0]=|1> and q[1]=|0>.
   - Since q[1] is |1>, the `nctrl` condition fails, so the X gate is not applied to q[2].
   - The state remains |110>, matching the expected measurement probabilities.

## isqTrain/3879

- task_id: `isqTrain/3879`
- task_type: `bug_fix`
- category: `circuit_patterns`
- difficulty: `difficult`
- concept_tags: `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `4441`

### Prompt

There's an error in this quantum circuit implementation. Fix it:

```
import std;
// ctrl<2> X (Toffoli) on input |110>
qbit q[3];

procedure main() {
    // Prepare input |110>
    X(q[0]);
    Y(q[1]);
    // Apply doubly-controlled X
    ctrl<2> X(q[0], q[1], q[2]);
    // Measure
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: Line `Y(q[1]);` uses the Y gate instead of X to prepare q[1]. The Y gate maps |0⟩ → i|1⟩, introducing an unwanted phase factor of i, rather than cleanly preparing |1⟩.

2. **Fix**: Replace `Y(q[1]);` with `X(q[1]);`. The X gate correctly maps |0⟩ → |1⟩ without phase.

3. **State evolution of corrected circuit**:
   - Initial: |000⟩
   - After X(q[0]): |100⟩
   - After X(q[1]): |110⟩
   - After ctrl<2> X (Toffoli): Both controls (q[0]=1, q[1]=1) satisfy the condition, so target q[2] flips → |111⟩
   - Measurement outcome: |111⟩ with probability 1.0 ✓

## isqTrain/3776

- task_id: `isqTrain/3776`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `expert`
- concept_tags: `entanglement`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `4835`

### Prompt

Code this in isQ: a 6-qubit CNOT chain: set q[0] to |1>, then use a for loop to apply CNOT(q[i], q[i+1]) for i=0..4. This should propagate the |1> to all qubits. Measure all 6 qubits.

### Chain-of-thought reasoning

Sponsor
1.  **Analyze the Request:**
    *   **Task:** Generate reasoning for an isQ quantum program (based on the provided code).
    *   **Circuit:** 6-qubit CNOT chain. `q[0]` starts as |1>, `CNOT(q[i], q[i+1])` for `i` in `0..4`.
    *   **Goal:** Propagate |1> to all qubits, measure all 6.
    *   **Format:** "## Reasoning" section, concise (3-8 lines), precise Dirac notation, NO isQ code blocks.
    *   **Language:** English.

2.  **Deconstruct the Circuit & State Evolution:**
    *   Initial state: `q` is array of 6 qubits. All in |0>. `|000000>`
    *   Step 1: `X(q[0])`. Flips `q[0]` to |1>. State is `|100000>`.
    *   Step 2: `CNOT(q[0], q[1])`. Control `q[0]` is |1>, so `q[1]` flips to |1>. State is `|110000>`.
    *   Step 3: `CNOT(q[1], q[2])`. Control `q[1]` is |1>, so `q[2]` flips to |1>. State is `|111000>`.
    *   Step 4: `CNOT(q[2], q[3])`. Control `q[2]` is |1>, so `q[3]` flips to |1>. State is `|111100>`.
    *   Step 5: `CNOT(q[3], q[4])`. Control `q[3]` is |1>, so `q[4]` flips to |1>. State is `|111110>`.
    *   Step 6: `CNOT(q[4], q[5])`. Control `q[4]` is |1>, so `q[5]` flips to |1>. State is `|111111>`.
    *   Final State: `|111111>`.
    *   Measurement: Measure all 6 qubits. Outcome is deterministically `111111`.

3.  **Draft the Reasoning (incorporating constraints):**
    *   *Constraint Checklist & Confidence Score:*
        1. Goal? Yes.
        2. Qubits & measured? Yes.
        3. Step-by-step Dirac? Yes.
        4. Why expected probs? Yes.
        *Confidence Score: 5/5*

    *   *Drafting:*
        ## Reasoning
        The circuit aims to initialize a single qubit to |1> and propagate this state sequentially through a 6-qubit chain using CNOT gates, utilizing 6 qubits (all measured).
        1. Initialize 6 qubits: |ψ₀⟩ = |000000⟩.
        2. Apply X(q[0]): |ψ₁⟩ = |100000⟩.
        3. CNOT chain (i=0 to 4): Each CNOT flips the next target qubit because the control is |1⟩. State evolves as: |100000⟩ → |110000⟩ → |111000⟩ → |111100⟩ → |111110⟩ → |ψ_f⟩ = |111111⟩.
        4. Since the final quantum state is exactly |111111⟩ with amplitude 1, measuring all 6 qubits yields the bitstring '111111' with 100% probability.

4.  **Refine and Format:**
    *   Check length: ~6 lines. Perfect.
    *   Check tone: Concise, precise.
    *   Check syntax constraints: No code blocks, starts with "## Reasoning".

5.  **Final Polish:** (Self-Correction during drafting)
    Make sure the bit order matches standard notation if specified, but standard Dirac implies q[0] is leftmost. The `--probs` note says earlier measured is higher bit. In state |111111>, it doesn't matter, but good to keep notation consistent.

    ## Reasoning
    This circuit propagates an initial |1> state across a linear chain of 6 qubits using cascading CNOT gates, with all 6 qubits measured.
    - Initial state: |000000⟩.
    - Apply X(q[0]) to set the first qubit to |1⟩: |ψ⟩ = |100000⟩.
    - The for loop applies CNOT(q[i], q[i+1]) for i=0 to 4. Since each control qubit is in the |1> state, each successive target qubit is

## isqTrain/3855

- task_id: `isqTrain/3855`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `difficult`
- concept_tags: `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1695`

### Prompt

Create an isQ quantum circuit that Apply ctrl<2> X (equivalent to Toffoli) to input |111>. The target q[2] flips only when both q[0] and q[1] are |1>. Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply a doubly-controlled X gate (Toffoli) to the input state |111> and measure all qubits.
2. **Qubits**: 3 qubits are required (q[0], q[1], q[2]), and all are measured.
3. **State evolution**:
   - Initialize to |000>.
   - Apply X gates to all qubits: |000> → |111>.
   - Apply `ctrl<2> X(q[0], q[1], q[2])`: Since controls q[0] and q[1] are both |1>, the target q[2] flips: |111> → |110>.
4. **Expected probabilities**: The final state is exactly |110>, so measurement yields "110" with probability 1.0.

## isqTrain/4070

- task_id: `isqTrain/4070`
- task_type: `bug_fix`
- category: `circuit_patterns`
- difficulty: `difficult`
- concept_tags: `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `2578`

### Prompt

This isQ program doesn't produce the correct output. Can you debug it?

Code:
```
import std;
// ctrl<2> X (Toffoli) on input |010>
qbit q[3];

procedure main() {
    // Prepare input |010>
    X(q[1]);
    // Apply doubly-controlled X
    // BUG: missing gate here
    // Measure
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis
1. **The bug**: The code prepares the initial state |010> by applying an X gate to `q[1]`, but entirely omits the requested doubly-controlled X (Toffoli) gate before measurement.
2. **The fix**: Insert the command `ctrl<2> X(q[0], q[1], q[2]);` where the bug is indicated, applying the Toffoli gate with `q[0]` and `q[1]` as controls and `q[2]` as the target.
3. **State evolution**: The circuit starts in |000>, and `X(q[1])` changes the state to |010>. The Toffoli gate evaluates whether both controls (`q[0]` and `q[1]`) are in the |1> state. Since `q[0]` is |0>, the condition fails, and the target `q[2]` remains unchanged. The final state is |010>, which correctly yields a 100% measurement probability for |010>.

## isqTrain/3866

- task_id: `isqTrain/3866`
- task_type: `code_generation`
- category: `circuit_patterns`
- difficulty: `expert`
- concept_tags: `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `5181`

### Prompt

Code this in isQ: Apply `ctrl nctrl X` to |110>: q[0] is positive control, q[1] is negative control, q[2] is target. Target flips when q[0]=|1> AND q[1]=|0>. Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Prepare the state |110> and apply a mixed-control X gate with q[0] as positive and q[1] as negative control.
Qubits: 3 qubits are used, initialized to |000>, and all are measured.
Evolution:
1. `X(q[0])` and `X(q[1])` prepare the initial state |110>.
2. The `ctrl nctrl X(q[0], q[1], q[2])` gate applies an X gate to q[2] only if q[0] is |1> and q[1] is |0>.
3. Since q[1] is currently in state |1>, the negative control condition is not met, and the target q[2] is not flipped.
Final state: |110>.
Probabilities: The final state is deterministically |110>, so measurement yields the bitstring 110 with a probability of 1.0.
