# ISQ training COT RAG corpus: hamiltonian_simulation shard 5

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3677

- task_id: `isqTrain/3677`
- task_type: `code_generation`
- category: `hamiltonian_simulation`
- difficulty: `expert`
- concept_tags: `hamiltonian_simulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `2419`

### Prompt

Implement a quantum circuit in isQ: first-order Trotter simulation of the Ising Hamiltonian H = X⊗X + Z⊗Z with time t=0.1. Decompose as:
exp(-i*t*H) ≈ exp(-i*t*XX) * exp(-i*t*ZZ)
Use separate XX and ZZ blocks with `deriving gate`. Start from |00> and measure both qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement first-order Trotter simulation of H=X⊗X+Z⊗Z for time t=0.1 using separate XX and ZZ rotation blocks.
Qubits: 2 qubits (q[0], q[1]), both are measured.
Evolution:
1. Initial state is |00>.
2. The exp(-i*t*XX) block applies H to both qubits, CNOT, Rz(0.2), and CNOT, then H again. This acts as exp(-i*t*XX)|00> = cos(0.1)|00> - i

## isqTrain/4153

- task_id: `isqTrain/4153`
- task_type: `output_prediction`
- category: `hamiltonian_simulation`
- difficulty: `expert`
- concept_tags: `hamiltonian_simulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `2181`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;
qbit q[2];

procedure main() {
    CNOT(q[0], q[1]);
    Rz(2.0 * 0.1000, q[1]);
    CNOT(q[0], q[1]);
    H(q[0]); H(q[1]);
    CNOT(q[0], q[1]);
    Rz(2.0 * 0.2, q[1]);
    CNOT(q[0], q[1]);
    H(q[0]); H(q[1]);
    CNOT(q[0], q[1]);
    Rz(2.0 * 0.1000, q[1]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a step-by-step analysis of a quantum circuit written in isQ, predicting the measurement outcome and its probability distribution.

2.  **Analyze the Circuit:**
    *   **Qubits:** 2 (`q[0]`, `q[1]`), initialized to `|00>`.
    *   **Gate Sequence:**
        1.  `CNOT(q[0], q[1])`
        2.  `Rz(0.2, q[1])` (Wait, `Rz(2.0 * 0.1)` = `Rz(0.2)`)
        3.  `CNOT(q[0], q[1])`
        4.  `H(q[0]); H(q[1])`
        5.  `CNOT(q[0], q[1])`
        6.  `Rz(0.4, q[1])` (Since `2.0 * 0.2` = `0.4`)
        7.  `CNOT(q[0], q[1])`
        8.  `H(q[0]); H(q[1])`
        9.  `CNOT(q[0], q[1])`
        10. `Rz(0.2, q[1])` (`2.0 * 0.1000` = `0.2`)
        11. `CNOT(q[0], q[1])`
    *   **Measurements:** `M(q[0]); M(q[1])`

3.  **Step-by-Step State Evolution:**
    *   Initial state: $|\psi_0\rangle = |00\rangle$.
    *   `CNOT(q[0], q[1])` on `|00\rangle` -> `|00\rangle`.
    *   `Rz(0.2, q[1])` on `|00\rangle` -> `|00\rangle`. (Rz only adds a phase to `|1>`, which has 0 amplitude).
    *   `CNOT(q[0], q[1])` on `|00\rangle` -> `|00\rangle`.
    *   Wait, this whole block 1-3 is $CNOT \cdot Rz \cdot CNOT$. If the control is 0, CNOT does nothing. The target is 0. Rz adds phase to 1. So it remains `|00>`.
    *   Wait, let's trace exactly:
        *   State 0: $|00\rangle$
        *   After 1: $|00\rangle$
        *   After 2: $|00\rangle$
        *   After 3: $|00\rangle$
        *   After 4: $(H \otimes H) |00\rangle = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
        *   After 5-7: $H^{\otimes 2} \cdot CNOT \cdot Rz \cdot CNOT \cdot H^{\otimes 2}$ is a common pattern. Let's see. $CNOT \cdot Rz(\theta) \cdot CNOT$. If applied to $(a|0\rangle + b|1\rangle) \otimes |\psi\rangle$, it's just an identity if control is 0, and $Rz$ on target if control is 1. Wait, in the Hadamard basis, $CNOT$ is $CZ$? No, $H_{target} CNOT H_{target} = CZ$.
        *   Let's analyze $CNOT \cdot (I \otimes Rz(\theta)) \cdot CNOT$. This is a controlled-$Rz$ gate. It applies $Rz(\theta)$ to the target if the control is $|1\rangle$.
        *   Actually, let's track the exact amplitudes.
        *   After 4: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$
        *   Apply `CNOT(q[0], q[1])`: $\frac{1}{2}(|00\rangle + |01\rangle + |11\rangle + |10\rangle) = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$. Symmetric!
        *   Apply `Rz(0.4, q[1])`: $\frac{1}{2}(|00\rangle + e^{-i0.2}|01

### Reference answer

Deterministic output: state |00> with probability ~0.96

## isqTrain/4140

- task_id: `isqTrain/4140`
- task_type: `output_prediction`
- category: `hamiltonian_simulation`
- difficulty: `difficult`
- concept_tags: `hamiltonian_simulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `4918`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
qbit q[2];

procedure main() {
    H(q[0]);
    H(q[1]);
    CNOT(q[0], q[1]);
    Rz(2.0 * 0.5, q[1]);
    CNOT(q[0], q[1]);
    H(q[0]);
    H(q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the isQ circuit:**
    -   Initial state: $|00\rangle$
    -   `H(q[0]); H(q[1]);` -> $H \otimes H |00\rangle = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle) = |++\rangle$
    -   `CNOT(q[0], q[1]);` -> CNOT with q[0] as control, q[1] as target. In the $|+\rangle, |-\rangle$ basis (or just expanding), CNOT $|++\rangle = \frac{1}{2}(|00\rangle + |01\rangle + |11\rangle + |10\rangle) = |++\rangle$.
        Wait, let's trace it:
        $|00\rangle \to |00\rangle$
        $|01\rangle \to |01\rangle$
        $|10\rangle \to |11\rangle$
        $|11\rangle \to |10\rangle$
        So the state remains $\frac{1}{2}(|00\rangle + |01\rangle + |11\rangle + |10\rangle) = |++\rangle$.
    -   `Rz(2.0 * 0.5, q[1]);` -> $R_z(1)$ on q[1].
        Let's apply $I \otimes R_z(1)$ to $|++\rangle$.
        $R_z(1) |0\rangle = e^{-i/2} |0\rangle$.
        $R_z(1) |1\rangle = e^{i/2} |1\rangle$.
        Wait, $R_z(\theta) = e^{-i\theta/2} |0\rangle\langle0| + e^{i\theta/2} |1\rangle\langle1|$.
        State on q[1] was $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
        $R_z(1) |+\rangle = \frac{1}{\sqrt{2}}(e^{-i/2} |0\rangle + e^{i/2} |1\rangle) = e^{-i/2} \frac{1}{\sqrt{2}}(|0\rangle + e^{i} |1\rangle)$.
        Total state: $|+\rangle \otimes e^{-i/2} \frac{1}{\sqrt{2}}(|0\rangle + e^{i} |1\rangle)$.
    -   `CNOT(q[0], q[1]);` -> Since q[0] is in $|+\rangle$, it's a mixture of control=0 and control=1.
        State before CNOT: $\frac{1}{2} (|0\rangle + |1\rangle) \otimes (e^{-i/2}|0\rangle + e^{i/2}|1\rangle)$
        $= \frac{1}{2} (e^{-i/2}|00\rangle + e^{i/2}|01\rangle + e^{-i/2}|10\rangle + e^{i/2}|11\rangle)$.
        Apply CNOT:
        $|00\rangle \to |00\rangle$
        $|01\rangle \to |01\rangle$
        $|10\rangle \to |11\rangle$
        $|11\rangle \to |10\rangle$
        So CNOT gives:
        $\frac{1}{2} (e^{-i/2}|00\rangle + e^{i/2}|01\rangle + e^{-i/2}|11\rangle + e^{i/2}|10\rangle)$
        $= \frac{1}{2} (e^{-i/2}(|00\rangle + |11\rangle) + e^{i/2}(|01\rangle + |10\rangle))$.
    -   `H(q[0]); H(q[1]);` -> Apply $H \otimes H$.
        $H \otimes H |00\rangle = |++\rangle = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
        $H \otimes H |11\rangle = |--\rangle = \frac{1}{2}(|00\rangle - |01\rangle - |10\rangle + |11\rangle)$.
        $H \otimes H (|00\rangle + |11\rangle) = |++\rangle + |--\rangle = |00\rangle + |11

### Reference answer

Dominant output states: |00> with probability ~0.77 each

## isqTrain/4569

- task_id: `isqTrain/4569`
- task_type: `output_prediction`
- category: `hamiltonian_simulation`
- difficulty: `difficult`
- concept_tags: `hamiltonian_simulation`, `basis_change`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2977`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;

qbit q[2];

procedure main() {
    
    
    H(q[1]);  // target different qubit
    H(q[1]);
    
    CNOT(q[0], q[1]);
    Rz(3.14159265358979 / 2, q[1]);
    CNOT(q[0], q[1]);
    
    H(q[0]);
    H(q[1]);
    
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict the probability distribution of an isQ program.
    *   Format: Step-by-step reasoning starting with "## Circuit Analysis", concluding with the distribution.
    *   Input Program:
        
    *   Constraint: 3-8 lines for simple circuits, up to 15 for complex ones. Output only the analysis. End with the distribution.

2.  **Step-by-step Circuit Analysis:**
    *   Initial state: $|00\rangle$ (assuming standard initialization).
    *   `H(q[1])` followed by `H(q[1])` is the Identity operation ($H \cdot H = I$). State remains $|00\rangle$.
    *   The sequence `CNOT(q[0], q[1]); Rz(pi/2, q[1]); CNOT(q[0], q[1])` applies a controlled-$R_z(\pi/2)$ gate to $q[1]$ controlled by $q[0]$.
    *   Since $q[0]$ is $|0\rangle$, the target $q[1]$ is not rotated (or rather, $|0\rangle$ gets a phase, but $|1\rangle$ gets the $R_z$ rotation, which doesn't matter here since $q[1]$ is also $|0\rangle$). The state remains $|00\rangle$.
    *   Wait, let's trace carefully:
        *   $|00\rangle$
        *   After CNOTs and Rz: Still $|00\rangle$.
        *   `H(q[0]); H(q[1]);`: Creates $H|0\rangle \otimes H|0\rangle = |+\rangle \otimes |+\rangle = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
        *   Measurement probabilities: Equal superposition means 25% for each basis state.

3.  **Refine the Explanation:**
    *   State $|00\rangle$.
    *   $H(q[1])$ twice $\rightarrow I$.
    *   CNOT-Rz(pi/2)-CNOT sequence on $|00\rangle$. The CNOT doesn't flip $q[1]$ because $q[0]$ is 0. State remains $|00\rangle$. (Technically $R_z$ applies a phase to $|0\rangle$ and $e^{i\pi/2}$ to $|1\rangle$, so $|00\rangle \to |00\rangle$ up to global phase).
    *   Apply $H(q[0])$ and $H(q[1])$, yielding $|+\rangle \otimes |+\rangle = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
    *   Measurements yield uniform probabilities.

4.  **Drafting the text:**
    ## Circuit Analysis
    - Initial state is $|00\rangle$.
    - `H(q[1])` followed by `H(q[1])` acts as the identity gate, leaving the state as $|00\rangle$.
    - The sequence `CNOT(q[0], q[1])`, `Rz(pi/2, q[1])`, `CNOT(q[0], q[1])` implements a controlled-$R_z$ gate. Because $q[0]$ is in state $|0\rangle$, the $R_z$ rotation is conditionally applied, but since $q[1]$ is also $|0\rangle$, the state remains $|00\rangle$ (up to a global phase).
    - Applying `H(q[0])` and `H(q[1])` creates a uniform superposition: $(H|0\rangle) \otimes (H|0\rangle) = |+\rangle \otimes |+\rangle = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
    - Measuring both qubits in this balanced superposition yields equal probabilities for all possible outcomes.

    Predicted probability distribution: {|00

### Reference answer

{'predicted_probs': {'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|00>) = 0.2500, P(|01>) = 0.2500, P(|10>) = 0.2500, P(|11>) = 0.2500.'}

## isqTrain/3942

- task_id: `isqTrain/3942`
- task_type: `bug_fix`
- category: `hamiltonian_simulation`
- difficulty: `difficult`
- concept_tags: `hamiltonian_simulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `5382`

### Prompt

The following isQ code has a bug. Find and fix it.

Buggy code:
```
import std;
// Trotter simulation of ZZ interaction: exp(-i*0.8*Z⊗Z)
qbit q[2];

procedure main() {
    // Start from superposition to see ZZ effect
    H(q[0]);
    // Decompose exp(-i*t*ZZ) using CNOT sandwich
    CNOT(q[0], q[1]);
    Rz(2.0 * 0.8, q[1]);
    // BUG: missing gate here
    // Measure
    M(q[0]); M(q[1]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: The second `CNOT(q[0], q[1])` is missing. The decomposition of exp(-iθ Z⊗Z) requires a "CNOT sandwich": CNOT → Rz(2θ) → CNOT. The first CNOT maps Z⊗Z into Z⊗I, the Rz applies the rotation on the target, and the second CNOT maps back. Without it, the entangling structure is never undone.

2. **Fix**: Insert `CNOT(q[0], q[1]);` after the `Rz` gate to complete the CNOT sandwich.

3. **State evolution (corrected)**:
   - |00⟩
   - H(q[0]): (|00⟩ + |10⟩)/√2
   - CNOT(q[0],q[1]): (|00⟩ + |11⟩)/√2

## isqTrain/3895

- task_id: `isqTrain/3895`
- task_type: `bug_fix`
- category: `hamiltonian_simulation`
- difficulty: `difficult`
- concept_tags: `hamiltonian_simulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `5036`

### Prompt

这个isQ程序有问题，请找出错误并给出正确代码：

```
import std;
// Trotter simulation of XX interaction: exp(-i*1.0*X⊗X)
// Decomposition: H-CNOT-Rz-CNOT-H
qbit q[2];

procedure main() {
    // Decompose exp(-i*t*XX) using CNOT sandwich
    H(q[0]);
    H(q[1]);
    CNOT(q[0], q[1]);
    Rz(2.0 * 1.0, q[1]);
    CNOT(q[0], q[1]);
    // BUG: missing gate here
    H(q[1]);
    // Measure both qubits
    M(q[0]); M(q[1]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis

**The bug:** The code is missing `H(q[0])` after the second `CNOT`. The XX interaction decomposition requires an H gate on **both** qubits before and after the CNOT-Rz-CNOT sandwich (i.e., H⊗H … H⊗H). Only `H(q[1])` is present after the sandwich; `H(q[0])` is absent.

**The fix:** Add `H(q[0]);` immediately before `H(q[1]);` after the second CNOT, so both qubits are rotated back from the Z basis.

**State evolution (corrected):**
1. |00⟩ → H⊗H → |++⟩
2. |++⟩ → CNOT → CNOT|++⟩ (entangled superposition)
3. → Rz(2.0) on q[1] → phases applied: exp(-i) on |0⟩, exp(i) on |1⟩ of q[1]
4. → CNOT → uncompute parity encoding
5. → H⊗H → final state: e^{-i}|00⟩cos(1) + i·e^{-i}|11⟩sin(1) (up to global phase), yielding P(|00⟩) ≈ 0.2919, P(|11⟩) ≈ 0.7081, matching predicted output.

## isqTrain/3948

- task_id: `isqTrain/3948`
- task_type: `bug_fix`
- category: `hamiltonian_simulation`
- difficulty: `expert`
- concept_tags: `hamiltonian_simulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `921`

### Prompt

Debug this isQ program — it gives unexpected measurement results.

```
import std;
// First-order Trotter: exp(-i*t*(XX + ZZ)) ≈ exp(-i*t*XX)*exp(-i*t*ZZ)
qbit q[2];

procedure main() {
    // exp(-i*t*XX) block
    H(q[0]); H(q[1]);
    CNOT(q[0], q[1]);
    Rz(2.0 * 0.1, q[1]);
    CNOT(q[0], q[1]);
    H(q[0]); H(q[1]);
    // exp(-i*t*ZZ) block
    CNOT(q[1], q[0]);
    Rz(2.0 * 0.1, q[1]);
    CNOT(q[0], q[1]);
    // Measure
    M(q[0]); M(q[1]);
}

``` (bug type: swapped qubits)

### Chain-of-thought reasoning

## Bug Analysis

1. **The bug**: In the `exp(-i*t*ZZ)` block, the first CNOT has swapped control/target (`CNOT(q[1], q[0])` instead of `CNOT(q[0], q[1])`), and the third CNOT is also inconsistent. The standard decomposition of exp(-iθZZ) requires both CNOTs to have the same control and target direction.

2. **The fix**: Change the ZZ block to use consistent `CNOT(q[0], q[1])` for both CNOTs, with `Rz(2t, q[1])` on the target in between.

3. **State evolution** (starting from |00⟩):
   - **XX block**: H⊗H maps |00⟩→|++⟩. CNOT(0,1)+Rz(0.2,q[1])+CNOT(0,1)+H⊗H implements exp(-i·0.1·XX), yielding a state close to |00⟩ with a small |11⟩ component.
   - **ZZ block (corrected)**: CNOT(0,1)+Rz(0.2,q[1])+CNOT(0,1) implements exp(-i·0.1·ZZ). Since ZZ|00⟩=|00⟩, this applies a phase e^(-i·0.1) to |00⟩ and e^(i·0.1) to |11⟩.
   - **Final state**: ≈ 0.995|00⟩ + 0.0999|11⟩ (approximate), giving probabilities P(|00⟩)≈0.990, P(|11⟩)≈0.010, consistent with the predicted output. The swapped CNOTs would

## isqTrain/3925

- task_id: `isqTrain/3925`
- task_type: `bug_fix`
- category: `hamiltonian_simulation`
- difficulty: `expert`
- concept_tags: `hamiltonian_simulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `2954`

### Prompt

这个isQ程序有问题，请找出错误并给出正确代码：

```
import std;
// First-order Trotter: exp(-i*t*(XX + ZZ)) ≈ exp(-i*t*XX)*exp(-i*t*ZZ)
qbit q[2];

procedure main() {
    // exp(-i*t*XX) block
    H(q[0]); H(q[1]);
    CNOT(q[0], q[1]);
    Rz(2.0 * 0.2, q[1]);
    CZ(q[0], q[1]);
    H(q[0]); H(q[1]);
    // exp(-i*t*ZZ) block
    CNOT(q[0], q[1]);
    Rz(2.0 * 0.2, q[1]);
    CNOT(q[0], q[1]);
    // Measure
    M(q[0]); M(q[1]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

Let me analyze the buggy code and the corrected version.

The buggy code has:

The fixed code has:

So the bug is that `CZ(q[0], q[1])` was used instead of `CNOT(q[0], q[1])` in the exp(-i*t*XX) block.

Let me think about why this is wrong and verify the circuit.

For exp(-i*t*XX), we use the identity:
XX = H⊗H · ZZ · H⊗H

So exp(-i*t*XX) = H⊗H · exp(-i*t*ZZ) · H⊗H

And exp(-i*t*ZZ) = CNOT · Rz(2t) · CNOT (approximately, for the diagonal implementation)

So the correct circuit for exp(-i*t*XX) is:
1. H(q[0]); H(q[1]);  -- transform to ZZ basis
2. CNOT(q[0], q[1]);  -- implement ZZ
3. Rz(2*t, q[1]);     -- rotation
4. CNOT(q[0], q[1]);  -- undo CNOT
5. H(q[0]); H(q[1]);  -- transform back

The bug uses CZ instead of the second CNOT. CZ applies a phase of -1 to |11>, but CNOT flips the target based on the control. These are different operations, so using CZ instead of CNOT gives the wrong result.

Let me verify the corrected circuit step by step:

Starting from |00⟩:

1. After H⊗H: |++⟩ = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2

2. After CNOT(q[0], q[1]): (|00⟩ + |01⟩ + |11⟩ + |10⟩)/2

Wait, let me be more careful. CNOT(q[0], q[1]) flips q[1] when q[0] is |1⟩.

|00⟩ → |00⟩
|01⟩ → |01⟩
|10⟩ → |11⟩
|11⟩ → |10⟩

So after CNOT: (|00⟩ + |01⟩ + |11⟩ + |10⟩)/2

Hmm, that's the same state. Let me think again...

Actually |++⟩ = (|0⟩ + |1⟩)/√2 ⊗ (|0⟩ + |1⟩)/√2 = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2

After CNOT(q[0], q[1]):
|00⟩ → |00⟩
|01⟩ → |01⟩
|10⟩ → |11⟩
|11⟩ → |10⟩

So the state becomes (|00⟩ + |01⟩ + |11⟩ + |10⟩)/2, which is still a uniform superposition.

3. After Rz(2*0.2, q[1]):
Rz(θ) applies phase e^{-iθ/2} to |0⟩ and e^{iθ/2} to |1⟩ on the target qubit.

θ = 0.4

State: (e^{-iθ/2}|00⟩ + e^{iθ/2}|01⟩ + e^{-iθ/2}|11⟩ + e^{iθ/2}|10⟩)/2

Wait, Rz is applied to q[1], so it affects the second qubit:
- |00⟩: q[1]=0, gets phase e^{-iθ/2}
- |01⟩: q[1]=1, gets phase e^{iθ/2}
- |11⟩: q[1]=1, gets phase e^{iθ/2}
- |10⟩: q[1]=0, gets phase e^{-iθ/2}

So: e^{-iθ/2}(|00⟩ + |10⟩)/2 + e^{iθ/2}(|01⟩ + |11⟩)/2

4. After CNOT(q[0], q[1]):
|00⟩ → |00⟩, |10⟩ → |11⟩, |01⟩ → |01⟩, |11⟩ → |10⟩

## isqTrain/3681

- task_id: `isqTrain/3681`
- task_type: `code_generation`
- category: `hamiltonian_simulation`
- difficulty: `expert`
- concept_tags: `hamiltonian_simulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `3517`

### Prompt

Implement the following in isQ: second-order Suzuki-Trotter simulation of H = XX + ZZ with t=0.2. Use the symmetric decomposition:
S2(t) = exp(-i*t/2*ZZ) * exp(-i*t*XX) * exp(-i*t/2*ZZ)
Measure both qubits starting from |00>.

### Chain-of-thought reasoning

Let me analyze the Suzuki-Trotter simulation circuit step by step.

The goal is to implement a second-order Suzuki-Trotter decomposition of the Hamiltonian H = XX + ZZ with t = 0.2, starting from |00⟩ and measuring both qubits.

The decomposition is: S2(t) = exp(-i*t/2*ZZ) * exp(-i*t*XX) * exp(-i*t/2*ZZ)

Let me trace through the circuit:

**Initial state:** |00⟩

**First ZZ block (t/2 = 0.1):**
- CNOT(q[0], q[1]): |00⟩ → |00⟩ (target doesn't flip since control is |0⟩)
- Rz(2*0.1, q[1]): |00⟩ → |00⟩ (Rz on |0⟩ just adds global phase e^(-i*0.1))
- CNOT(q[0], q[1]): |00⟩ → |00⟩

So after first ZZ block, we have |00⟩ (with some global phase).

Actually, let me think more carefully. The exp(-i*θ*ZZ) on |00⟩:
ZZ|00⟩ = |00⟩, so exp(-i*θ*ZZ)|00⟩ = e^(-iθ)|00⟩

So the first ZZ block gives e^(-i*0.1)|00⟩.

**XX block (t = 0.2):**
- H(q[0]): |0⟩ → |+⟩
- H(q[1]): |0⟩ → |+⟩
State: |++⟩ = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2

- CNOT(q[0], q[1]): |++⟩ → (|00⟩ + |11⟩ + |10⟩ + |01⟩)/2 = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2
Wait, let me recalculate.

|++⟩ = (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩)

CNOT: |00⟩→|00⟩, |01⟩→|01⟩, |10⟩→|11⟩, |11⟩→|10⟩

So CNOT|++⟩ = (1/2)(|00⟩ + |01⟩ + |11⟩ + |10⟩) = |++⟩

Hmm, that doesn't change anything. Let me reconsider the XX decomposition.

The standard decomposition for exp(-i*θ*XX):
exp(-i*θ*XX) = (H⊗H) · exp(-i*θ*ZZ) · (H⊗H)

And exp(-i*θ*ZZ) = CNOT · (I⊗Rz(2θ)) · CNOT

So for the XX block with t=0.2:
- H⊗H: transforms to ZZ basis
- CNOT(q[0], q[1])
- Rz(2*0.2, q[1]) = Rz(0.4, q[1])
- CNOT(q[0], q[1])
- H⊗H: transforms back

Let me trace through from |00⟩:

After first ZZ block: e^(-i*0.1)|00⟩ (global phase)

After H⊗H: e^(-i*0.1)|++⟩

After CNOT: e^(-i*0.1)|++⟩ (since |++⟩ is symmetric under CNOT, actually let me verify)

|++⟩ = (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩)
CNOT: (1/2)(|00⟩ + |01⟩ + |11⟩ + |10⟩) = (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩) = |++⟩

So CNOT|++⟩ = |++⟩.

After Rz(0.4, q[1]):
Rz(θ)|0⟩ = e^(-iθ/2)|0⟩, Rz(θ)|1⟩ = e^(iθ/2)|1⟩

(1/2)(e^(-i*0.2)|00⟩ + e^(i*0.2)|01⟩ + e^(-i*0.2)|10⟩ + e^(i*0.2)|11⟩)

After CNOT: swap |10⟩↔|11⟩:
(1/2)(e^(-i*0.2)|00⟩ + e^(i*0.2)|01⟩ + e^(i*0.2)|11⟩ + e^(-i*0.2)|10⟩)

Hmm wait, CNOT(q[0], q[1]) with q[0] as

## isqTrain/3931

- task_id: `isqTrain/3931`
- task_type: `bug_fix`
- category: `hamiltonian_simulation`
- difficulty: `difficult`
- concept_tags: `hamiltonian_simulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `2499`

### Prompt

This isQ program doesn't produce the correct output. Can you debug it?

Code:
```
import std;
// Trotter simulation of ZZ interaction: exp(-i*0.1*Z⊗Z)
qbit q[2];

procedure main() {
    // Start from superposition to see ZZ effect
    H(q[0]);
    // Decompose exp(-i*t*ZZ) using CNOT sandwich
    CZ(q[0], q[1]);
    Rz(2.0 * 0.1, q[1]);
    CNOT(q[0], q[1]);
    // Measure
    M(q[0]); M(q[1]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **The bug**: On line 10, `CZ(q[0], q[1])` is used as the first gate in the CNOT-sandwich decomposition of exp(-i·t·Z⊗Z). The correct decomposition requires CNOT gates, not CZ. The CZ gate maps |11⟩→-|11⟩ (introducing an unwanted sign flip) instead of swapping |10⟩↔|11⟩ like CNOT does, breaking the entangling/disentangling sandwich structure.

2. **The fix**: Replace `CZ(q[0], q[1])` with `CNOT(q[0], q[1])` on line 10, so both ends of the sandwich use matching CNOT gates.

3. **State evolution (corrected)**:
   - |00⟩ → H(q[0]) → (|00⟩+|10⟩)/√2
   - → CNOT(q[0],q[1]) → (|00⟩+|11⟩)/√2
   - → Rz(0.2, q[1]) → (e^{-i·0.1}|00⟩+e^{i·0.1}|11⟩)/√2
   - → CNOT(q[0],q[1]) → (e^{-i·0.1}|00⟩+e^{i·0.1}|10⟩)/√2
   - Measurement: P(|00⟩)=0.5, P(|10⟩)=0.5 ✓
