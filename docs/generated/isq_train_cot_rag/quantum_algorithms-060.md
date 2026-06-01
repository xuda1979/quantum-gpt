# ISQ training COT RAG corpus: quantum_algorithms shard 60

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3040

- task_id: `isqTrain/3040`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`, `measurement_order`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `1841`

### Prompt

I'm getting wrong output from this isQ code. What's the bug and how do I fix it?

```isq
import std;
qbit q[2];
// nctrl X with X init circuit
procedure main() {
    X(q[0]);
    nctrl X(q[0], q[1]);
    M(q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. The bug is in the final line where `M(q[0])` is called a second time instead of measuring the second qubit. 
2. The fix is to change the second measurement target from `q[0]` to `q[1]` so that the full 2-qubit state is observed.
3. State evolution of the corrected circuit:
   - Initialize the 2-qubit system to |00>.
   - `X(q[0])` flips the first qubit, evolving the state to |10>.
   - `nctrl X(q[0], q[1])` applies an X gate to `q[1]` only if

## isqTrain/4552

- task_id: `isqTrain/4552`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `basis_change`, `entanglement`, `hamiltonian_simulation`, `isq_syntax_for_loop`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3249`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[2];

procedure main() {
    
    X(q[0]);

    
    
    
    

    
    CNOT(q[0], q[1]);
    
    Rz(1.57079632679490, q[1]);
    CNOT(q[0], q[1]);

    
    H(q[0]); H(q[1]);
    CNOT(q[0], q[1]);
    
    Rz(1.57079632679490, q[1]);
    CNOT(q[0], q[1]);
    H(q[0]); H(q[1]);

    
    CNOT(q[0], q[1]);
    Rz(1.57079632679490, q[1]);
    CNOT(q[0], q[1]);

    
    H(q[0]); H(q[1]);
    CNOT(q[0], q[1]);
    Rz(1.57079632679490, q[1]);
    CNOT(q[0], q[1]);
    H(q[0]); H(q[1]);

    
    H(q[1]); // superposition on last qubit
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a step-by-step quantum circuit analysis of an isQ program, ending with the predicted probability distribution.

2.  **Analyze the isQ Code:**
    *   **Initialization:** `qbit q[2];` -> 2 qubits, initial state |00>.
    *   **Step 1:** `X(q[0]);` -> state becomes |10>.
    *   **Step 2:** `CNOT(q[0], q[1]);` -> state becomes |11>.
    *   **Step 3:** `Rz(1.57079632679490, q[1]);` -> $R_z(\pi/2) = S$ gate. Since q[1] is |1>, it gets a phase. $|11\rangle \to e^{i\pi/4} |11\rangle$ (or $i|11\rangle$ depending on global phase, let's track exact matrix: $R_z(\theta) = \begin{pmatrix} e^{-i\theta/2} & 0 \\ 0 & e^{i\theta/2} \end{pmatrix}$. With $\theta = \pi/2$, it is $e^{-i\pi/4}|0\rangle$ or $e^{i\pi/4}|1\rangle$. The state is $e^{i\pi/4}|11\rangle$).
    *   **Step 4:** `CNOT(q[0], q[1]);` -> $|11\rangle \to |10\rangle$.
    *   **Wait, let's group operations to see what they simplify to.**
        *   Gate block: `CNOT(q[0], q[1]); Rz(pi/2, q[1]); CNOT(q[0], q[1]);`
            *   This applies $R_z(\pi/2)$ controlled on q[0] being 0? No, `CNOT; Rz; CNOT` applies $R_z$ only when control is |0>. Let's check:
            *   If control is |0>, target is unchanged by 1st CNOT, gets Rz, unchanged by 2nd CNOT. -> CRz on |0>.
            *   If control is |1>, target flips to |1>, gets Rz, flips back to |0>. -> Target state didn't change phase.
            *   Actually, $CNOT_{01} (I \otimes R_z) CNOT_{01}$ applies $R_z$ to the *control*? No, it applies $R_z$ to the target controlled by the control.
            *   Let's trace:
                *   |00> -> CNOT -> |00> -> Rz -> $e^{-i\pi/4}|00\rangle$ -> CNOT -> $e^{-i\pi/4}|00\rangle$
                *   |01> -> CNOT -> |01> -> Rz -> $e^{i\pi/4}|01\rangle$ -> CNOT -> $e^{i\pi/4}|01\rangle$
                *   |10> -> CNOT -> |11> -> Rz -> $e^{i\pi/4}|11\rangle$ -> CNOT -> $e^{i\pi/4}|10\rangle$
                *   |11> -> CNOT -> |10> -> Rz -> $e^{-i\pi/4}|10\rangle$ -> CNOT -> $e^{-i\pi/4}|11\rangle$
            *   Notice that |10> gets $e^{i\pi/4}$ and |11> gets $e^{-i\pi/4}$. This means the *control* qubit (q[0]) gets a phase $R_z(\pm \pi/2)$ depending on target? Wait, the phase is applied to the state where the target was |0> originally, which became |1> then back to |0>.
            *   Let's rewrite: $CNOT (I \otimes R_z(\theta)) CNOT = |0\rangle\langle0| \otimes R_z(\theta) + |1\rangle\langle1| \otimes (X R_z(\theta) X)$.
            *   Since $X R_z(\theta) X = R_z(-\theta)$, this is $|0\rangle\langle0| \otimes R_z(\theta) + |1\rangle\langle1| \otimes R_z(-\theta)$.
            *   So it applies $+R_z(\theta)$ to q[1] if q[0] is 0, and $-R_z(\theta)$ to q[1] if q[0

### Reference answer

{'predicted_probs': {'00': 0.5, '01': 0.5}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|00>) = 0.5000, P(|01>) = 0.5000.'}

## isqTrain/3834

- task_id: `isqTrain/3834`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1431`

### Prompt

Write isQ code for the following quantum task: Demonstrate phase kickback with controlled-Rz(3pi/4). Control qubit starts in |+>, target in |1>. After controlled-Rz and Hadamard, measure to observe the kicked-back phase.

### Chain-of-thought reasoning

Let me trace through this phase kickback circuit step by step.

1. **Goal**: Demonstrate phase kickback where a controlled-Rz gate kicks back a phase onto the control qubit.

2. **Qubits**: 2 qubits (q[0] = control, q[1] = target), both measured.

3. **State evolution**:

   - Initial state: |00>
   
   - After H(q[0]): (|0> + |1>)/√2 ⊗ |0> = (|00> + |10>)/√2
   
   - After X(q[1]): (|01> + |11>)/√2
   
   - After ctrl Rz(3π/4, q[0], q[1]): 
     The controlled-Rz applies Rz(3π/4) to q[1] when q[0] is |1>.
     
     Rz(3π/4) = [[e^{-i3π/8}, 0], [0, e^{i3π/8}]]
     
     When applied to |1>: Rz(3π/4)|1> = e^{i3π/8}|1>
     
     So the state becomes: (|01> + e^{i3π/8}·e^{i3π/8}|11>)/√2 = (|01> + e^{i3π/4}|11>)/√2
     
     Wait, let me reconsider. The controlled-Rz applies Rz to the target when control is |1>. 
     
     Actually, the phase kickback works like this: when the target is in an eigenstate of Z (which |1> is, with eigenvalue -1... wait no, let me reconsider).
     
     Actually, let me think about this more carefully. The target is |1>, which is an eigenstate of Rz with eigenvalue e^{i3π/8}.
     
     So controlled-Rz when control is |0>: no change, |01> stays |01>
     When control is |1>: Rz(3π/4)|1> = e^{i3π/8}|1>, so |11> → e^{i3π/8}|11>
     
     Wait, but that's not quite right either. Let me recalculate.
     
     Actually, for phase kickback, the key insight is that when the target is in an eigenstate of the gate being controlled, the phase gets "kicked back" to the control.
     
     |1> is an eigenstate of Rz(θ) with eigenvalue e^{iθ/2}:
     Rz(θ)|1> = [[e^{-iθ/2}, 0], [0, e^{iθ/2}]]|1> = e^{iθ/2}|1>
     
     So with θ = 3π/4:
     Rz(3π/4)|1> = e^{i3π/8}|1>
     
     The controlled operation on (|0> + |1>)/√2 ⊗ |1>:
     = (|0>⊗|1> + |1>⊗Rz(3π/4)|1>)/√2
     = (|0>⊗|1> + e^{i3π/8}|1>⊗|1>)/√2
     = (|01> + e^{i3π/8}|11>)/√2
     
     This is a phase on the control qubit!
   
   - After H(q[0]):
     H(|0>) = |+> = (|0> + |1>)/√2
     H(|1>) = |-> = (|0> - |1>)/√2
     
     So: (H⊗I)((|01> + e^{i3π/8}|11>)/√2)
     = (|01> + |11>)/2 + e^{i3π/8}(|01> - |11>)/2
     = ((1 + e^{i3π/8})|01> + (1 - e^{i3π/8})|11>)/2
     
   - Probabilities:
     P(|01>) = |1 + e^{i3π/8}|²/4 = (1 + e^{i3π/8})(1 + e^{-i3π/8})/4 = (1 + 2cos(3π/8) + 1)/4 = (2 + 2cos(3π/8))/4 = (1 + cos(3π/8))/2
     
     cos(3π/8) ≈ 0.38268
     
     P(|01>) = (1 + 0.38268)/2 ≈ 0

## isqTrain/4048

- task_id: `isqTrain/4048`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_deriving_gate`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3923`

### Prompt

The following isQ code has a bug. Find and fix it.

Buggy code:
```
import std;
// Swap test: compare |+> vs |+>
// q[0] = ancilla, q[1] = state A, q[2] = state B
qbit q[3];

// Controlled-SWAP (Fredkin gate)
unit cswap(qbit q[3]) {
    CNOT(q[2], q[1]);
    Toffoli(q[0], q[1], q[2]);
    CNOT(q[1], q[2]);
} deriving gate

procedure main() {
    // Prepare state A on q[1]
    H(q[1]);
    // Prepare state B on q[2]
    H(q[2]);
    // Swap test circuit
    H(q[0]);
    cswap(q);
    H(q[0]);
    // Measure ancilla and state qubits
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: swapped qubits)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: In the `cswap` unit, the third line uses `CNOT(q[1], q[2])` instead of `CNOT(q[2], q[1])`. The correct Cswap (three-CNOT decomposition) (controlled-swap (three-CNOT decomposition)) decomposition is `CNOT(2,1) → Toffoli(0,1,2) → CNOT(2,1)`. The buggy code swaps the control/target on the final CNOT, breaking the controlled-swap operation (three-CNOT decomposition).

2. **Fix**: Change the last line from `CNOT(q[1], q[2])` to `CNOT(q[2], q[1])`.

3. **State evolution (corrected)**:
   - Start: |000⟩
   -

## isqTrain/1158

- task_id: `isqTrain/1158`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `2519`

### Prompt

Write an isQ program that implements the mcmt_gate pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Implement a multi-controlled multi-target X gate (2 controls, 2 targets) with an explicit X-X identity pair on q[0] to demonstrate gate cancellation awareness.

**Qubits:** 4 qubits (q[0..3]), all measured.

**State evolution:**
1. |0000⟩ → X(q[0]), X(q[1]) → |0011⟩ (both controls set to |1⟩)
2. → ctrl ctrl X(q[0],q[1],q[2]) → |0111⟩ (doubly-controlled X flips first target)
3. → ctrl ctrl X(q[0],q[1],q[3]) → |1111⟩ (doubly-controlled X flips second target)
4. → X(q[0]) → |1110⟩ (bit-flip on q[0])
5. → X(q[0]) → |1111⟩ (X-X pair cancels, demonstrating identity/cancellation awareness)

**Result:** Final state is |1111⟩ with probability 1.0. The X-X pair on q[0] is an explicit identity operation that a optimizing compiler would cancel, leaving the state unchanged.

## isqTrain/2882

- task_id: `isqTrain/2882`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `measurement_order`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `2041`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
qbit q[4];
procedure main() {
    X(q[0]);
    X(q[1]);
    X(q[2]);
    ctrl ctrl ctrl X(q[0], q[1], q[2], q[3]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the request:**
    *   Task: Analyze an isQ quantum program, generate step-by-step reasoning, and predict its measurement probability distribution.
    *   Input isQ code:
        
    *   Qubits: `q[0]`, `q[1]`, `q[2]`, `q[3]`. Total = 4 qubits.
    *   Output format: "## Circuit Analysis" section, step-by-step state evolution, final state, and predicted probability distribution (JSON array). Constraint: 3-8 lines for simple circuits, up to 15 for complex ones.

2.  **Analyze the circuit:**
    *   Initial state: $|0000\rangle$ (Assuming standard order $q_0 q_1 q_2 q_3$)
    *   `X(q[0])`: Flips $q_0$. State becomes $|1000\rangle$
    *   `X(q[1])`: Flips $q_1$. State becomes $|1100\rangle$
    *   `X(q[2])`: Flips $q_2$. State becomes $|1110\rangle$
    *   `ctrl ctrl ctrl X(q[0], q[1], q[2], q[3])`: This is a 3-controlled X gate (equivalent to a Toffoli-like gate, or CCCX). The target is $q_3$, and controls are $q_0, q_1, q_2$. Since $q_0, q_1, q_2$ are all in the $|1\rangle$ state, the X gate is applied to $q_3$.
    *   Applying X to $q_3$ (which is in $|0\rangle$) flips it to $|1\rangle$.
    *   State becomes $|1111\rangle$.

3.  **Formulate the step-by-step evolution:**
    *   Initial: $|0000\rangle$
    *   After `X(q[0]), X(q[1]), X(q[2])`: $|1110\rangle$
    *   After `ctrl ctrl ctrl X(q[0], q[1], q[2], q[3])`: Since $q_0, q_1, q_2$ are 1, it flips $q_3$. State $\rightarrow |1111\rangle$.

4.  **Predict the measurement probability distribution:**
    *   Final state: $|1111\rangle$
    *   Probability of 1111 is 1.0.
    *   Probability of everything else is 0.0.
    *   Bitstring length is 4. Array size is 16.
    *   Index for 1111 (binary 15) is 1.0, others are 0.0.

5.  **Draft the response:**
    *   Start with `## Circuit Analysis`.
    *   Briefly explain the X gates setting up the state.
    *   Explain the CCCX gate.
    *   Provide the final state.
    *   Provide the JSON array.

6.  **Refine to meet constraints (Concise, 3-8 lines):**
    *   "## Circuit Analysis"
    *   "1. The circuit initializes 4 qubits in $|0000\rangle$. Three X gates are applied to $q_0, q_1, q_2$, preparing the state $|1110\rangle$."
    *   "2. A triple-controlled X gate (`ctrl ctrl ctrl X`) is applied with $q_0, q_1, q_2$ as controls and $q_3$ as the target."
    *   "3. Since all control qubits are in the $|1\rangle$ state, the X gate activates, flipping $q_3$ from $|0\rangle$ to $|1\rangle$."
    *   "4. The final quantum state before measurement is $|1111\rangle$."
    *   "5. Measurement will deterministically yield the bitstring `1111`."
    *   Probability array: `[0.0, 0.0, ..., 1.0]` at index 15.

7.  **Final JSON check:**
    Index 15 (1111) is 1.0.
    `[0.0, 0.0, 0.0, 0.0,

### Reference answer

{'predicted_probs': {'1111': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/4119

- task_id: `isqTrain/4119`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `4065`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit q[3];

procedure main() {
    X(q[0]);
    X(q[1]);

    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    H(q[2]);
    ctrl Rz(-2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    H(q[1]);
    ctrl Rz(-2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    ctrl Rz(-2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    H(q[0]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

Initial state: |000⟩

1. X(q[0]): |100⟩
2. X(q[1]): |110⟩

Now we have CNOT(q[0], q[2]); CNOT(q[2], q[0]); CNOT(q[0], q[2]);

Let me track the state:
- After X(q[0]): |100⟩
- After X(q[1]): |110⟩

Now the three CNOTs:
- CNOT(q[0], q[2]): q[0]=1, so q[2] flips: |111⟩
- CNOT(q[2], q[0]): q[2]=1, so q[0] flips: |011⟩
- CNOT(q[0], q[2]): q[0]=1, so q[2] flips: |010⟩

Wait, let me be more careful. The qubits are q[0], q[1], q[2]. Let me write the state as |q[0] q[1] q[2]⟩.

Initial: |000⟩
After X(q[0]): |100⟩
After X(q[1]): |110⟩

CNOT(q[0], q[2]): control=q[0], target=q[2]
q[0]=1, so q[2] flips from 0 to 1: |111⟩

CNOT(q[2], q[0]): control=q[2], target=q[0]
q[2]=1, so q[0] flips from 1 to 0: |011⟩

CNOT(q[0], q[2]): control=q[0], target=q[2]
q[0]=1, so q[2] flips from 1 to 0: |010⟩

So after the three CNOTs: |010⟩

Hmm, wait. Let me reconsider the qubit ordering. In isQ, q[0], q[1], q[2] are just labels. The state |q[0]=1, q[1]=1, q[2]=0⟩ I'll write as |110⟩ with the convention that q[0] is the leftmost bit.

State after the three CNOTs: |010⟩

Now: H(q[2])
|010⟩ → |0⟩ ⊗ |1⟩ ⊗ H|0⟩ = |01⟩ ⊗ (|0⟩+|1⟩)/√2 = (|010⟩ + |011⟩)/√2

Wait, that's wrong. Let me re-examine.

After the three CNOTs: q[0]=0, q[1]=1, q[2]=0. So the state is |010⟩ (with q[0] as the leftmost bit).

H(q[2]) acts on q[2]:
|010⟩ → |0⟩ ⊗ |1⟩ ⊗ H|0⟩ = |0⟩ ⊗ |1⟩ ⊗ |+⟩ = (|010⟩ + |011⟩)/√2

ctrl Rz(-2π/4, q[2], q[1]): This is a controlled Rz with q[2] as control and q[1] as target.
Rz(θ) = e^{-iθZ/2}

Wait, I need to be careful about the Rz convention. In isQ, Rz(θ, q) applies the rotation Rz(θ). The angle here is -2π/4 = -π/2.

Rz(θ) = [[e^{-iθ/2}, 0], [0, e^{iθ/2}]]

So Rz(-π/2) = [[e^{iπ/4}, 0], [0, e^{-iπ/4}]]

The ctrl Rz(-π/2, q[2], q[1]) applies Rz(-π/2) to q[1] when q[2] is |1⟩.

Current state: (|010⟩ + |011⟩)/√2

When q[2]=0 (state |010⟩): no action, stays |010⟩
When q[2]=1 (state |011⟩): apply Rz(-π/2) to q[1]

For |011⟩: q[1] is |1⟩, so Rz(-π/2)|1⟩ = e^{-i(-π/2)/2}|1⟩ = e^{iπ/4}|1⟩

State: (|010⟩ + e^{iπ/4}|011⟩)/√2

H(q[1]): Apply H to q[1]
|010⟩ = |0⟩⊗|1⟩⊗(|0⟩+|1⟩)/√2

### Reference answer

Uniform distribution across 8 states

## isqTrain/3603

- task_id: `isqTrain/3603`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `hamiltonian_simulation`
- source: `isq_train_cot`
- dataset_index: `4392`

### Prompt

Fix the bug in the following isQ program.

Bug description: Wrong CNOT direction

The program should QAOA MaxCut on 2-node graph.

### Chain-of-thought reasoning

The bug is in the CNOT sequence for implementing the ZZ interaction. In the buggy code:

The CNOTs don't match - the first CNOT has q[1] as control and q[0] as target, but the second has q[0] as control and q[1] as target. For the standard ZZ gate decomposition, both CNOTs should have the same control and target:

This implements the ZZ interaction correctly as CNOT-Rz-CNOT on the same control-target pair.

Let me verify the probabilities with the corrected circuit:

1. Initial state: |00⟩
2. After H on both: |++⟩ = (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩)
3. After CNOT(q[0], q[1]): (1/2)(|00⟩ + |01⟩ + |11⟩ + |10⟩) = same as |++⟩ (actually the CNOT maps |+⟩|+⟩ to |+⟩|+⟩ since CNOT|++⟩ = |++⟩)

Wait, let me recalculate. CNOT with control q[0], target q[1]:
|00⟩ → |00⟩
|01⟩ → |01⟩
|10⟩ → |11⟩
|11⟩ → |10⟩

So (1/2)(|00⟩ + |01⟩ + |11⟩ + |10⟩) - yes same state.

4. After Rz(γ) on q[1] with γ = π/4:
|00⟩ → |00⟩ (no phase since q[1]=0, wait Rz on |0⟩ gives e^{-iγ/2}|0⟩ and |1⟩ gives e^{iγ/2}|1⟩)

Rz(θ)|0⟩ = e^{-iθ/2}|0⟩
Rz(θ)|1⟩ = e^{iθ/2}|1⟩

So Rz(γ) on q[1] with γ = π/4:
(1/2)(e^{-iπ/8}|00⟩ + e^{iπ/8}|01⟩ + e^{iπ/8}|11⟩ + e^{-iπ/8}|10⟩)

5. After CNOT(q[0], q[1]):
(1/2)(e^{-iπ/8}|00⟩ + e^{iπ/8}|01⟩ + e^{iπ/8}|10⟩ + e^{-iπ/8}|11⟩)

This is e^{-iπ/8}|00⟩⟨++| + e^{iπ/8}... Actually let me factor:
= (1/2)(e^{-iπ/8}(|00⟩ + |11⟩) + e^{iπ/8}(|01⟩ + |10⟩))

Hmm, this is equivalent to applying ZZ(γ) = e^{-iγ/2} * diag(e^{iγ}, 1, 1, e^{iγ})... actually ZZ(γ) = exp(-iγ/2 * Z⊗Z).

ZZ(γ)|++⟩ = ?

Z⊗Z has eigenvalues: +1 for |00⟩, |11⟩ and -1 for |01⟩, |10⟩.

So exp(-iγ/2 * Z⊗Z)|++⟩ = (1/2)(e^{-iγ/2}|00⟩ + e^{iγ/2}|01⟩ + e^{iγ/2}|10⟩ + e^{-iγ/2}|11⟩)

With γ = π/4:
= (1/2)(e^{-iπ/8}|00⟩ + e^{iπ/8}|01⟩ + e^{iπ/8}|10⟩ + e^{-iπ/8}|11⟩)

6. Now mixer Rx(2β) on both with 2β = π/4:
Rx(θ) = cos(θ/2)I - i sin(θ/2)X

Rx(π/4)|+⟩ = Rx(π/4)(1/√2)(|0⟩ + |1⟩)
= (1/√2)(cos(π/8)|0⟩ - i sin(π/8)|1⟩ + cos(π/8)|1⟩ - i sin(π/8)|0⟩)
= (1/√2)((cos(π/8) - i sin(π/8))|0⟩

## isqTrain/905

- task_id: `isqTrain/905`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_oracle`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2098`

### Prompt

I need an isQ program to implements the bit_flip_oracle pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement a bit-flip oracle for f(x) = x[0] XOR x[1] with input |10⟩, including an identity X-X pair to demonstrate gate cancellation awareness.

2. **Qubits**: 3 qubits (q[0], q[1] as input, q[2] as oracle output target); all 3 are measured.

3. **State evolution**:
   - |000⟩ — initial state
   - X(q[0]) → |100⟩ — prepare input x = |10⟩
   - CNOT(q[0], q[2]) → |101⟩ — q[0]=|1⟩ flips q[2] to |1⟩
   - CNOT(q[1], q[2]) → |101⟩ — q[1]=|0⟩ leaves q[2] unchanged
   - X(q[0]) → |001⟩ — first X of identity pair
   - X(q[0]) → |101⟩ — second X cancels, restoring state (gate cancellation)
   - Final state: |101⟩

4. **Expected probabilities**: The final state |101⟩ is a computational basis state, so measurement yields |101⟩ with probability 1.0, confirming XOR(1,0) = 1 is encoded in q[2].

## isqTrain/4357

- task_id: `isqTrain/4357`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_arrays`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `486`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

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
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

Let me analyze this isQ program step by step.

Initial state: |0000>

1. H(q[0]); H(q[1]);
   Apply H to q[0] and q[1]:
   |0000> → |++00> = (1/2)(|0000> + |0100> + |1000> + |1100>)

2. CNOT(q[0], q[2]);
   Copy q[0] to q[2]:
   (1/2)(|0000> + |0100> + |1010> + |1110>)

3. CNOT(q[1], q[3]);
   Copy q[1] to q[3]:
   (1/2)(|0000> + |0101> + |1010> + |1111>)

4. CNOT(q[0], q[2]);
   Oracle: XOR q[0] into q[2]:
   (1/2)(|0000> + |0101> + |0110> + |1011>)
   
   Wait, let me recalculate. After step 3, the state is:
   (1/2)(|0000> + |0101> + |1010> + |1111>)
   
   CNOT(q[0], q[2]) flips q[2] when q[0] is |1>:
   - |0000> → |0000> (q[0]=0, no flip)
   - |0101> → |0101> (q[0]=0, no flip)
   - |1010> → |1000> (q[0]=1, flip q[2])
   - |1111> → |1101> (q[0]=1, flip q[2])
   
   State: (1/2)(|0000> + |0101> + |1000> + |1101>)

5. CNOT(q[0], q[3]);
   XOR q[0] into q[3]:
   - |0000> → |0000>
   - |0101> → |0101>
   - |1000> → |1001>
   - |1101> → |1100>
   
   State: (1/2)(|0000> + |0101> + |1001> + |1100>)

6. H(q[0]); H(q[1]);
   Apply H to q[0] and q[1]:
   
   Let me compute this term by term.
   
   H|00> = |++> = (1/2)(|00> + |01> + |10> + |11>)
   H|01> = |+-> = (1/2)(|00> - |01> + |10> - |11>)
   H|10> = |-+> = (1/2)(|00> + |01> - |10> - |11>)
   H|11> = |--> = (1/2)(|00> - |01> - |10> + |11>)
   
   State before H: (1/2)(|00>|00> + |01>|01> + |10>|01> + |11>|00>)
   
   Applying H on q[0] and q[1]:
   (1/4)[(|00> + |01> + |10> + |11>)|00> + (|00> - |01> + |10> - |11>)|01> + (|00> + |01> - |10> - |11>)|01> + (|00> - |01> - |10> + |11>)|00>]
   
   = (1/4)[|00>(|00> + |01> + |00> + |00>) + |01>(|00> - |01> + |01> - |01>) + |10>(|00> + |01> - |01> - |01>) + |11>(|00> - |01> - |01> + |00>)]
   
   Wait, let me be more careful. Let me denote the state after step 5 as:
   (1/2)(|00>|00> + |01>|01> + |10>|01> + |11>|00>)
   
   Now apply H⊗H on q[0]q[1]:
   
   H⊗H |00> = (1/2)(|00> + |01> + |10> + |11>)
   H⊗H |01> = (1/2)(|00> - |01> + |10> - |11>)
   H⊗H |10> = (1/2)(|00> + |

### Reference answer

{'predicted_probs': {'0001': 0.5, '0010': 0.5}, 'explanation': 'This isQ program operates on 4 qubit(s). The measurement probability distribution is: P(|0001>) = 0.5000, P(|0010>) = 0.5000.'}
