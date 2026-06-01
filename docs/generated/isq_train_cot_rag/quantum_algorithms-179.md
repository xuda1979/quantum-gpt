# ISQ training COT RAG corpus: quantum_algorithms shard 179

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/2949

- task_id: `isqTrain/2949`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `basis_change`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `962`

### Prompt

实现以下量子计算任务（使用isQ）：prepares 3 qubit(s) in the |-> state (X then H) and measures in the computational basis.

Requirements:
- Declare `qbit q[3];` at global scope.
- Apply X followed by H to each qubit.
- Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare 3 qubits in the |−⟩ state (via X then H) and measure in the computational basis.
2. **Qubits**: 3 qubits declared globally; all 3 are measured.
3. **State evolution**: Start with |000⟩. Apply X to each: X|0⟩=|1⟩, giving |111⟩. Apply H to each: H|1⟩=(|0⟩−|1⟩)/√2=|−⟩, so the final state is |−⟩⊗|−⟩⊗|−⟩ = (1/2√2)(|000⟩−|001⟩−|010⟩+|011⟩−|100⟩+|101⟩+|110⟩−|111⟩).
4. **Probabilities**: Each computational basis state has amplitude ±1/(2√2), giving equal probability |1/(2√2)|²=1/8=0.125 for all 8 outcomes.

## isqTrain/948

- task_id: `isqTrain/948`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `boolean_logic`, `isq_syntax_deriving_gate`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4227`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;

// SWAP gate for Fredkin construction
procedure swap_gate(qbit a, qbit b) {
    CNOT(a, b);
    CNOT(b, a);
    CNOT(a, b);
} deriving gate

qbit q[3];

procedure main() {
    // Control = |0> (default), target q[1] = |1>
    X(q[1]);
    // Fredkin with control=0: no swap should occur
    ctrl swap_gate(q[0], q[1], q[2]);
    // Targets unchanged: q[1]=1, q[2]=0
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict measurement probability distribution for an isQ program.
    *   Input: isQ code implementing a controlled-swap (three-CNOT decomposition) (controlled-swap (three-CNOT decomposition)) gate. Control is `q[0]`, targets are `q[1]` and `q[2]`. `q[1]` is set to $|1\rangle$ initially. Control `q[0]` remains $|0\rangle$.
    *   Output format: "## Circuit Analysis", step-by-step reasoning (Dirac notation), predicted probability distribution.
    *   Constraints: Concise (3-8 lines for simple), precise, no code blocks, specific ending.

2.  **Analyze the isQ Code:**
    *   `qbit q[3];` -> Initial state $|q[0]\rangle \otimes |q[1]\rangle \otimes |q[2]\rangle = |0\rangle \otimes |0\rangle \otimes |0\rangle = |000\rangle$.
    *   `X(q[1]);` -> Flips $q[1]$ to $|1\rangle$. State becomes $|010\rangle$.
    *   `ctrl swap_gate(q[0], q[1], q[2]);` -> This is equivalent to a Toffoli-like control, but the `ctrl` modifier in isQ without `@[...]` applies to the *first* argument of the procedure being called. Wait, let me check the syntax: `ctrl swap_gate(q[0], q[1], q[2])` -> Wait, `swap_gate` takes `(qbit a, qbit b)`. If called with 3 qubits, the first is the control, the next 2 are the targets. So `q[0]` is the control for the swap operation (three-CNOT decomposition) acting on `q[1]` and `q[2]`. Since `q[0]` is $|0\rangle$, the controlled-swap (three-CNOT decomposition) does nothing.
    *   State remains $|010\rangle$.
    *   Measurements: `M(q[0]); M(q[1]); M(q[2]);`.

3.  **Step-by-Step State Evolution:**
    *   Start: $|000\rangle$
    *   After `X(q[1])`: $|010\rangle$
    *   After `ctrl swap_gate`: State is $|010\rangle$ because control $q[0]$ is $|0\rangle$, so swap (three-CNOT decomposition) is not activated.
    *   Measurement: Always yields '010' (binary 2).

4.  **Format the Output:**
    *   Start with `## Circuit Analysis`
    *   Explain operations: Initial state $|000\rangle$, X gate on $q[1]$, controlled-swap (three-CNOT decomposition) on $q[1], q[2]$ controlled by $q[0]$.
    *   State evolution: $|000\rangle \xrightarrow{X(q[1])} |010\rangle \xrightarrow{ctrl \text{ swap (three-CNOT decomposition)}} |010\rangle$.
    *   Final state: $|010\rangle$.
    *   Predicted probabilities: `{|010>: 1.0}` (or equivalent depending on exact string format, but "Expected measurement probabilities: {|010>: 1.0}" is standard).

5.  **Refine the Output:**
    *   Make it 3-8 lines.
    *   Check control modifier syntax: `ctrl swap_gate(q[0], q[1], q[2])` implies `q[0]` is the control, `q[1]` and `q[2]` are passed to `swap_gate(a, b)`. Correct.
    *   No code blocks.

    Draft:
    ## Circuit Analysis
    1. The circuit initializes 3 qubits to $|000\rangle$, applies an X gate to $q[1]$ to set it to $|1\rangle$, and then applies a controlled-swap (three-CNOT decomposition) (controlled-swap (three-CNOT decomposition)) gate with $q[0]$ as the control and $q[1], q[2]$ as the targets.
    2. Initial state: $|000\rangle$.
    3. After `X(q[1])`, the state transitions to $|010\rangle$.
    4. The `ctrl swap_gate(q[0], q[1], q[2])` applies the swap operation (three-CNOT decomposition) to targets only if the control $q[0]$ is $|1\rangle$. Since $q[0]$ is $|0\rangle$, the swap (three-CNOT decomposition) is not triggered, leaving the state unchanged as $|010\rangle$.
    5. The final state before measurement is $|010\rangle

### Reference answer

{'predicted_probs': {'2': 1.0}, 'explanation': 'Parametric variant of isqEval/267. Dimension: predict probabilities for reference circuit.'}

## isqTrain/3035

- task_id: `isqTrain/3035`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `measurement_order`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `1621`

### Prompt

Code this in isQ: applies nctrl H. The nctrl modifier means the gate is applied when the control qubit is |0>.

Requirements:
- Declare `qbit q[2];` at global scope.
- Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply a negative-controlled Hadamard gate (nctrl H), which applies H to q[1] when control q[0] is |0⟩.

2. **Qubits**: 2 qubits (q[0] = control, q[1] = target), both measured.

3. **State evolution**:
   - Initial state: |00⟩
   - Apply nctrl H(q[0], q[1]): Since q[0] is |0⟩, H is applied to q[1]
   - Result: |0⟩ ⊗ H|0⟩ = |0⟩ ⊗ (|0⟩ + |1⟩)/√2 = (|00⟩ + |01⟩)/√2

4. **Expected probabilities**: Both |00⟩ and |01⟩ have amplitude 1/√2, so P(|00⟩) = P(|01⟩) = 0.5, consistent with the predicted output.

## isqTrain/4007

- task_id: `isqTrain/4007`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `interference`, `isq_syntax_oracle`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `2448`

### Prompt

I'm getting wrong output from this isQ code. What's the bug and how do I fix it?

```
import std;
// Bernstein-Vazirani: find secret s = 1101
oracle f(4, 1) = [0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1];
qbit q[5];

procedure main() {
    // Output in |->
    X(q[4]);
    H(q[4]);
    // Hadamard on inputs
    for i in 0:4 {
    // BUG: missing gate here
    }
    // Oracle
    f(q[0], q[1], q[2], q[3], q[4]);
    // Hadamard
    for i in 0:4 {
        H(q[i]);
    }
    // Measure
    M(q[0]); M(q[1]); M(q[2]); M(q[3]); M(q[4]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis
1. **The Bug:** The first `for i in 0:4` loop, which is supposed to apply Hadamard gates to the input qubits to create an equal superposition, is missing the `H(q[i]);` statement inside its body. Without this, the input qubits remain in the $|0\rangle$ state instead of the required $|+\rangle$ state.
2. **The Fix:** Add the Hadamard gate `H(q[i]);` inside the first `for` loop block.
3. **State Evolution:** 
   - Initializing to $|00000\rangle$, the target qubit `q[4]` is flipped to $|1\rangle$ and put into the $|-\rangle$ state via `X` and `H`.
   - With the fix, the input qubits `q[0:4]` undergo `H` gates, creating the state $\frac{1}{4} \sum_{x \in \{0,1\}^4} |x\rangle |-\rangle$.
   - The phase oracle `f` encodes the secret string $s=1101$ by mapping $|x\rangle \to (-1)^{x \cdot s}|x\rangle$.
   - The final Hadamard transform on `q[0:4]` interferes the phases to yield exactly $|1101\rangle$ on the input qubits, leaving `q[4]` in $|-\rangle$. Measuring all 5 qubits yields $|11010\rangle$ or $|11011\rangle$ with 50% probability each.

## isqExpand/algo/90

- task_id: `isqExpand/algo/90`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `qft`, `inverse_qft`, `bug_fix`, `phase_manipulation`
- source: `isq_expansion`
- dataset_index: `3992`

### Prompt

Debug this isQ program — it gives unexpected measurement results.

```isq
import std;
qbit q[3];

procedure qft() {
    H(q[0]);
    ctrl S(q[1], q[0]);
    ctrl T(q[2], q[0]);
    H(q[1]);
    ctrl S(q[2], q[1]);
    H(q[2]);
}

procedure iqft() {
    H(q[2]);
    ctrl S(q[2], q[1]);
    H(q[1]);
    ctrl T(q[2], q[0]);
    ctrl S(q[1], q[0]);
    H(q[0]);
}

procedure main() {
    X(q[1]); X(q[2]);
    qft();
    iqft();
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Bug分析

### 问题
逆QFT需要使用QFT中旋转门的共轭转置（S^dag 和 T^dag）。buggy代码的iqft()虽然正确地反转了门的顺序，但忘记对旋转门取共轭，即使用了S而非inv S，T而非inv T。

### Bug效果
数值模拟显示：buggy版本将|011>经QFT再经错误IQFT后变为|101>(index 5)。

### 修复
将iqft()中的三个受控旋转改为逆旋转：
- ctrl @[q[2]] S(q[1]) -> ctrl @[q[2]] inv S(q[1])
- ctrl @[q[2]] T(q[0]) -> ctrl @[q[2]] inv T(q[0])
- ctrl @[q[1]] S(q[0]) -> ctrl @[q[1]] inv S(q[0])

修复后：QFT→IQFT = 恒等，|011>被正确恢复。

## isqTrain/3824

- task_id: `isqTrain/3824`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `680`

### Prompt

请用isQ语言编写一个量子电路：a 1D quantum walk on 4 positions using 2 step(s). Use q[0] as the coin qubit and q[1..2] as the position register. Each step: Hadamard coin flip followed by controlled shifts.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Generate reasoning for a 1D quantum walk on 4 positions with 2 steps using isQ code.
    *   Format: Markdown starting with "## Reasoning", no isQ code blocks, 3-15 lines.
    *   Key elements to cover: Goal, qubits used/measured, step-by-step state evolution (Dirac notation), expected probabilities.

2.  **Analyze the Circuit:**
    *   Qubits: `q[0]` (coin), `q[1]` (position bit 0), `q[2]` (position bit 1). Total 3 qubits. Initial state |000>.
    *   Step 1:
        *   `H(q[0])`: Coin flip. State becomes (|000> + |100>) / sqrt(2). (Using order `q[2]q[1]q[0]` or `coin, pos1, pos2`... wait, standard notation: `q[2]q[1]q[0]` as $q_2 q_1 q_0$. Let's use $|q_2 q_1 q_0\rangle$. So |000> -> (|000> + |001>)/sqrt(2). Wait, `q[0]` is the coin, so it's the right-most bit if we write it as `q[2] q[1] q[0]`.)
        *   `ctrl X(q[0], q[1])`: If coin is |1>, flip `q[1]`. State becomes (|000> + |011>)/sqrt(2).
        *   `ctrl X(q[0], q[2])`: If coin is |1>, flip `q[2]`. State becomes (|000> + |111>)/sqrt(2).
    *   Step 2:
        *   `H(q[0])`: Coin flip. (|000> + |111>)/sqrt(2) -> (|000> + |100> + |111> - |011>) / 2.
        *   `ctrl X(q[0], q[1])`: (|000> + |110> + |111> - |001>) / 2.
        *   `ctrl X(q[0], q[2])`: (|000> + |100> + |011> - |111>) / 2.  Wait, let me re-calculate carefully.
        *   Let state be $|c, p_1, p_2\rangle$. Initial: $|0,0,0\rangle$.
        *   Step 1: H(c) -> $(|0,0,0\rangle + |1,0,0\rangle)/\sqrt{2}$.
        *   Shift (add +1 to position if c=1, meaning XOR with 1... wait, the code applies `ctrl X(q[0], q[1])` then `ctrl X(q[0], q[2])`. This XORs both position bits if coin is 1. So it adds 11 in binary, which is +3 mod 4? Or is it +1 and +2 = +3? Let's trace:
        *   If c=1, `q[1]` flips, `q[2]` flips. Position goes from 00 to 11 (which is 3).
        *   So Step 1 state: $(|0,0,0\rangle + |1,1,1\rangle)/\sqrt{2}$.
        *   Step 2: H(c) -> $(|0,0,0\rangle + |1,0,0\rangle + |1,1,1\rangle - |0,1,1\rangle)/2$.
        *   Shift again: apply `ctrl X(c, p_1)` then `ctrl X(c, p_2)`.
        *   For $|1,0,0\rangle$, it becomes $|1,1,1\rangle$.
        *   For $|1,1,1\rangle$, it becomes $|1,0,0\rangle$.
        *   So state becomes $(|0,0,0\rangle + |1,1,1\rangle + |1,0,0\rangle - |0,1,1\rangle)/2$.
        *   Wait, let me read the predicted output: {|000>: 0.25, |011>: 0.25, |100>: 0.25, |111>: 0.25}.
        *   Let's check my final state: $(|0,0,0\rangle + |1,

## isqTrain/1286

- task_id: `isqTrain/1286`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3353`

### Prompt

Write isQ code for the following quantum task: implements the iqp_circuit pattern using an alternative gate decomposition (S -> T T). The circuit must produce the same output as the standard decomposition.

### Chain-of-thought reasoning

Let me analyze this IQP circuit pattern with S -> T T decomposition.

The circuit has:
1. 2 qubits
2. Hadamard layer on both qubits
3. Diagonal layer with S gates (but decomposed as T T)
4. CZ gate
5. Hadamard layer
6. Measurements

Let me trace the state evolution:

Initial state: |00>

After H on both: (|00> + |01> + |10> + |11>)/2 = |++>

The S gate on q[0] is decomposed as T(q[0]), T(q[0])
The S gate on q[1] is decomposed as T(q[1]), T(q[1])

After T(q[0]): (|00> + e^(iπ/4)|01> + |10> + |11>)/2 - wait, T only acts on the first qubit
Actually, let me be more careful. T acts on qubit basis states where that qubit is |1>.

After H(q[0]), H(q[1]):
State = (|00> + |01> + |10> + |11>)/2

After T(q[0]): phase e^(iπ/4) on terms where q[0]=|1>
= (|00> + |01> + e^(iπ/4)|10> + e^(iπ/4)|11>)/2

After T(q[0]) again: phase e^(iπ/4) again on terms where q[0]=|1>
= (|00> + |01> + e^(iπ/2)|10> + e^(iπ/2)|11>)/2

After T(q[1]): phase e^(iπ/4) on terms where q[1]=|1>
= (|00> + e^(iπ/4)|01> + e^(iπ/2)|10> + e^(i3π/4)|11>)/2

After T(q[1]) again: phase e^(iπ/4) again on terms where q[1]=|1>
= (|00> + e^(iπ/2)|01> + e^(iπ/2)|10> + e^(iπ)|11>)/2

After CZ(q[0], q[1]): phase -1 on |11>
= (|00> + e^(iπ/2)|01> + e^(iπ/2)|10> - e^(iπ)|11>)/2
= (|00> + i|01> + i|10> + |11>)/2

Wait, let me recalculate. After the two T gates on q[0] and two T gates on q[1]:

The phases accumulated:
- |00>: no phase
- |01>: two T on q[1] = e^(iπ/2) = i
- |10>: two T on q[0] = e^(iπ/2) = i
- |11>: two T on q[0] + two T on q[1] = e^(iπ) = -1

After CZ: |11> gets another -1, so:
- |00>: 1
- |01>: i
- |10>: i
- |11>: (-1)(-1) = 1

State = (|00> + i|01> + i|10> + |11>)/2

Now apply H on both qubits:
H⊗H |00> = (|00>+|01>+|10>+|11>)/2
H⊗H |01> = (|00>-|01>+|10>-|11>)/2
H⊗H |10> = (|00>+|01>-|10>-|11>)/2
H⊗H |11> = (|00>-|01>-|10>+|11>)/2

So the final state = (1/2)[(|00>+|01>+|10>+|11>)/2 + i(|00>-|01>+|10>-|11>)/2 + i(|00>+|01>-|10>-|11>)/2 + (|00>-|01>-|10>+|11>)/2]

Let me collect coefficients:
|00>: (1 + i + i + 1)/4 = (2 + 2i)/4 = (1+i)/2
|01>: (1 - i + i - 1)/4 = 0/4 = 0
|10>: (1 + i - i - 1)/4 = 0/4 = 0
|11>: (1 - i - i + 1)/4 = (2 - 2i)/4 = (

## isqTrain/1208

- task_id: `isqTrain/1208`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4061`

### Prompt

请用isQ语言编写一个量子电路：implements a variant of the quantum_random_walk pattern using c[1] -> c[3]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Implement a discrete quantum walk on a 4-node cycle using an expanded 3-qubit coin register where only `c[1]` is active, with `c[0]` and `c[2]` idling in |0⟩.

**Qubits:** 5 total — coin register `c[3]` and position register `p[2]`; only `p[0]`, `p[1]` are measured.

**State evolution:**
1. **H(c[1]):** |000⟩_c|00⟩_p → (|000⟩+|010⟩)/√2 ⊗ |00⟩ — coin c[1] enters superposition while c[0],c[2] stay |0⟩
2. **ctrl CNOT(c[1], p[0], p[1]):** Both branches have p

## isqTrain/3470

- task_id: `isqTrain/3470`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `hamiltonian_simulation`, `basis_change`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5100`

### Prompt

实现以下量子计算任务（使用isQ）：the evolution operator exp(-i*theta*X_0*X_1) for theta=pi/4 in isQ.

Decomposition of XX interaction:
1. Basis change: H on both qubits (X -> Z)
2. ZZ evolution: CNOT(q[0],q[1]), Rz(2*theta, q[1]), CNOT(q[0],q[1])
3. Undo basis change: H on both

Apply to |00> state. Declare 2 qubits, measure both.

### Chain-of-thought reasoning

Let me analyze this step by step.

The goal is to implement exp(-i*theta*X_0*X_1) for theta = pi/4 applied to |00>.

The decomposition is:
1. H on both qubits to convert X basis to Z basis
2. ZZ evolution using CNOT, Rz, CNOT
3. H on both qubits to undo basis change

Let me trace the state evolution:

Initial state: |00>

After H⊗H: |00> → (1/√2)(|0> + |1>) ⊗ (1/√2)(|0> + |1>) = (1/2)(|00> + |01> + |10> + |11>)

Now for the ZZ evolution part with theta = pi/4, so 2*theta = pi/2.

CNOT(q[0], q[1]) applied to |+>|+> = (1/2)(|00> + |01> + |10> + |11>)
CNOT with control=q[0], target=q[1]:
|00> → |00>
|01> → |01>
|10> → |11>
|11> → |10>
Result: (1/2)(|00> + |01> + |11> + |10>) = (1/2)(|00> + |01> + |10> + |11>) - wait, that's the same state.

Hmm, let me recalculate. Actually H|0> = |+> = (|0>+|1>)/√2, so |+>|+> = (1/2)(|00> + |01> + |10> + |11>).

CNOT(q[0], q[1]) on this:
|00> → |00>
|01> → |01>
|10> → |11>
|11> → |10>

So we get (1/2)(|00> + |01> + |11> + |10>) = (1/2)(|00> + |01> + |10> + |11>) - same thing because the state is symmetric. Wait, actually let me be more careful:

(1/2)(|00> + |01> + |10> + |11>) after CNOT becomes:
(1/2)(CNOT|00> + CNOT|01> + CNOT|10> + CNOT|11>)
= (1/2)(|00> + |01> + |11> + |10>)
= (1/2)(|00> + |01> + |10> + |11>)

Same state. Now apply Rz(pi/2) on q[1]:
Rz(θ)|0> = e^{-iθ/2}|0>
Rz(θ)|1> = e^{iθ/2}|1>

For θ = pi/2:
Rz(pi/2)|0> = e^{-iπ/4}|0>
Rz(pi/2)|1> = e^{iπ/4}|1>

Applied to q[1]:
(1/2)(e^{-iπ/4}|00> + e^{iπ/4}|01> + e^{-iπ/4}|10> + e^{iπ/4}|11>)
= (e^{-iπ/4}/2)(|00> + |10>) + (e^{iπ/4}/2)(|01> + |11>)
= (1/2)(|00> + |10>) ⊗ e^{-iπ/4}|0> + (1/2)(|00> + |10>) ⊗ e^{iπ/4}|1>

Hmm, let me just track it more simply. After CNOT, we have (1/2)(|00> + |01> + |10> + |11>).

Apply Rz(pi/2) on qubit 1:
= (1/2)(e^{-iπ/4}|00> + e^{iπ/4}|01> + e^{-iπ/4}|10> + e^{iπ/4}|11>)
= (e^{-iπ/4}/2)(|00> + |10>) + (e^{iπ/4}/2)(|01> + |11>)

Now apply CNOT(q[0], q[1]) again:
= (e^{-iπ/4}/2)(|00> + |11>) + (e^{iπ/4}/2)(|01> + |10>)

Hmm wait, CNOT|00> = |00>, CNOT|10> = |11>, CNOT|01> = |01>, CNOT|11> = |10>.

So:
(e^{-iπ/4}/2)(|00

## isqTrain/1116

- task_id: `isqTrain/1116`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `interference`, `isq_syntax_oracle`, `superposition`
- source: `isq_train_cot`
- dataset_index: `139`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;

// Simon oracle with period s = 11 (binary)
// f(00) = f(11) and f(01) = f(10)
oracle bool[2] f(bool x[2]) {
    // Map: f(x) depends only on x[0] XOR x[1]
    // f(00)=00, f(01)=01, f(10)=01, f(11)=00
    bool x0_xor_x1 = x[0] != x[1];
    bool res[] = [false, x0_xor_x1];
    return res;
}

// Input register for Simon's algorithm
qbit q[2];
// Output register to hold f(x)
qbit out[2];

procedure main() {
    // Create superposition of all inputs
    H(q[0]); H(q[1]);
    // Query the oracle
    f(q, out);
    // Hadamard on input register to extract period info
    H(q[0]); H(q[1]);
    // Measure input: y satisfies y . s = 0 mod 2
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict measurement outcomes for a given isQ program (Simon's algorithm).
    *   Format: Markdown, starting with `## Circuit Analysis`, 3-15 lines.
    *   Program Details:
        *   4 qubits: `q[0]`, `q[1]` (input), `out[0]`, `out[1]` (output).
        *   Oracle `f` maps: `00->00`, `01->01`, `10->01`, `11->00`. Secret string $s = 11$.
        *   Circuit:
            *   Init state: `|0000>`
            *   Apply `H` to `q[0]`, `q[1]`: `(|00> + |01> + |10> + |11>)/2 |00>`
            *   Apply oracle `f(q, out)`: The oracle performs `|x>|0> -> |x>|f(x)>`.
                *   `f(00)=00`, `f(01)=01`, `f(10)=01`, `f(11)=00`.
                *   Because $f(x) = f(x \oplus s)$, specifically $f(00)=f(11)=00$ and $f(01)=f(10)=01$.
                *   State after oracle: `( |00>|00> + |01>|01> + |10>|01> + |11>|00> ) / 2`
                *   We can group them: `( |00>|00> + |11>|00> + |01>|01> + |10>|01> ) / 2` = `( (|00>+|11>)|00> + (|01>+|10>)|01> ) / 2`.
            *   Apply `H` to `q[0]`, `q[1]`:
                *   $H^{\otimes 2} (|00>+|11>) = H^{\otimes 2} (|00>+|11>) = |00> \cdot 2 - |01> \cdot 0 - |10> \cdot 0 + |11> \cdot 2$ -> wait, let's just use standard Simon's formula.
                *   $H^{\otimes 2} \frac{1}{\sqrt{2}} \sum_{z \in \{0,1\}^2} \frac{(-1)^{x \cdot z}}{2} |z> $.
                *   Let's trace it carefully:
                    *   First term: $|00> + |11>$. Apply $H^{\otimes 2}$:
                        *   $|00>$ -> $|++> = (|00> + |01> + |10> + |11>)/2$
                        *   $|11>$ -> $|--> = (|00> - |01> - |10> + |11>)/2$
                        *   Sum: $(2|00> + 2|11>)/2 = |00> + |11>$.
                    *   Second term: $|01> + |10>$. Apply $H^{\otimes 2}$:
                        *   $|01>$ -> $|+-)> = (|00> - |01> + |10> - |11>)/2$
                        *   $|10>$ -> $|-+)> = (|00> + |01> - |10> - |11>)/2$
                        *   Sum: $(2|00> - 2|11>)/2 = |00> - |11>$.
                    *   Wait! Let me re-calculate $|--> = H|1>H|1> = \frac{|0>-|1>}{\sqrt{2}} \otimes \frac{|0>-|1>}{\sqrt{2}} = \frac{|00> - |01> - |10> + |11>}{2}$.
                    *   $|00> + |11>$.
                    *   $H^{\otimes 2}(|00>+|11>) = \frac{1}{2}(|00>+|01>+|10>+|11>) + \frac{1}{2}(|00>-|01>-|10>+|11>) = |00> + |11>$.
                    *   Second term: $|01> + |10>$.
                    *   $H^{\otimes 2}(|01>+|10>) = \frac{1}{2}(|00>-|01>+|10>-|11>) + \frac{1}{2}(|00>+|01>-|10>-|11>) = |00> -

### Reference answer

{'predicted_probs': {'0': 0.5, '3': 0.5}, 'explanation': 'Parametric variant of isqEval/435. Dimension: predict probabilities for reference circuit.'}
