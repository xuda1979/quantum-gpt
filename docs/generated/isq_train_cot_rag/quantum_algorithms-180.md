# ISQ training COT RAG corpus: quantum_algorithms shard 180

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3487

- task_id: `isqTrain/3487`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `entanglement`, `ancilla_usage`, `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1562`

### Prompt

Write isQ code for the following quantum task: the 3-qubit bit-flip code with error on q[2] and correction in isQ.

Syndrome: anc[0]=q[0] XOR q[1], anc[1]=q[1] XOR q[2].
Syndrome 01 means error on q[2].
Correct: nctrl ctrl X(anc[0], anc[1], q[2]).
Declare q[3] and anc[2]. Measure q only. Expected: |000>.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Encode |0⟩ into |000⟩ via 3-qubit bit-flip code, inject X-error on q[2], detect syndrome via ancillas, and correct.

**Qubits:** 3 data (q[0–2]) + 2 ancilla (anc[0–1]); only q[0–2] measured.

**State evolution:**
1. **Encode:** Starting from |00000⟩, CNOT(q[0],q[1]) and CNOT(q[0],q[2]) leave state as |000⟩|00⟩ (encodes |0⟩ → |000⟩).
2. **Error:** X(q[2]) flips q[2]: state becomes |001⟩|00⟩.
3. **Syndrome extraction:**
   - CNOT(q[0],anc[0]), CNOT(q[1],anc[0]): anc[0] = q[0]⊕q[1] = 0⊕0 = 0
   - CNOT(q[1],anc[1]), CNOT(q[2

## isqTrain/789

- task_id: `isqTrain/789`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `finite_field_arithmetic`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3462`

### Prompt

Implement the following in isQ: implements the gf2_multiplication pattern. Include explicit identity operations in the circuit (X-X pair before M(q[3])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement GF(2) polynomial multiplication a(x)·b(x) where a(x)=1+x, b(x)=1, storing coefficients p0 and p1 in ancilla qubits, with an explicit X-X cancellation pair.

2. **Qubits**: 5 qubits total; q[0],q[1] encode a(x), q[2] encodes b(x), q[3],q[4] store the product p0,p1. Only q[3] and q[4] are measured.

3. **State evolution**:
   - |00000⟩ → X(q[0,1,2]) → |11100⟩
   - Toffoli(q[0],q[2],q[3]): both controls |1⟩, so q[3] flips → |11110⟩ (p0 = a0·b0 = 1)
   - Toffoli(q[1],q[2],q[4]): both controls |1⟩, so q[4] flips → |11111⟩ (p1 = a1·b0 = 1)
   - X(q[3]): q[3] flips to 0 → |11011⟩
   - X(q[3]): q[3] flips back to 1 → |11111⟩ (X-X cancels, demonstrating gate cancellation)

4. **Result**: Measuring q[3],q[4] yields |11⟩ with probability 1.0, confirming (1+x)·1 = 1+x in GF(2). The X-X pair is a no-op, illustrating awareness of gate cancellation in circuit optimization.

## isqTrain/2824

- task_id: `isqTrain/2824`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_for_loop`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3984`

### Prompt

Write isQ code for the following quantum task: creates a 4-qubit GHZ state. Apply H to the first qubit, then chain CNOT gates to entangle all 4 qubits. Measure all qubits.

Requirements:
- Declare `qbit q[4];` at global scope.
- Use `procedure main()` as entry point.
- Measure all 4 qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Create a 4-qubit GHZ state (|0000⟩ + |1111⟩)/√2.
Requires 4 qubits (declared globally), all measured at the end.
State evolution from initial |0000⟩:
1. H(q[0]) creates superposition: (|0000⟩ + |1000⟩)/√2
2. CNOT(q[0], q[1]) entangles q1: (|0000⟩ + |1100⟩)/√2
3. CNOT(q[1], q[2]) entangles q2: (|0000⟩ + |1110⟩)/√2
4. CNOT(q[2], q[3]) entangles q3: (|0000⟩ + |1111⟩)/√2
Measurement collapses the state to either |0000⟩ or |1111⟩, each with probability 0.5.

## isqTrain/1162

- task_id: `isqTrain/1162`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3788`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;

// Multi-controlled multi-target X gate
// 2 controls (q[0], q[1]) and 2 targets (q[2], q[3])
qbit q[4];

procedure main() {
    // Set both control qubits to |1>
    X(q[0]); X(q[1]);
    // Apply doubly-controlled X to first target
    ctrl ctrl X(q[0], q[1], q[2]);
    // Apply doubly-controlled X to second target
    ctrl ctrl X(q[0], q[1], q[3]);
    // Measure all qubits to verify the operation
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The 4-qubit system initializes to the basis state |0000>.
2. `X(q[0])` and `X(q[1])` flip the first two qubits, changing the state to |1100>.
3. `ctrl ctrl X(q[0], q[1], q[2])` acts as a Toffoli gate. Because both controls (q

### Reference answer

{'predicted_probs': {'15': 1.0}, 'explanation': 'Parametric variant of isqEval/442. Dimension: predict probabilities for reference circuit.'}

## isqTrain/1333

- task_id: `isqTrain/1333`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3082`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit q[2];

procedure main() {

    X(q[0]);
    H(q[0]);

    H(q[0]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. Operations applied: X on q[0], followed by two H gates on q[0], and measurements on q[0] and q[1].
2. Initial state is |00>. The X gate flips q[0] to |1>, evolving the state to |10>.
3. The first H gate maps q[0] from |1> to |->, resulting in the state (|0> - |1>) ⊗ |0> / √2.
4. The second H gate acts as an inverse (since H² = I), returning q[0] to the |1> state. The final state before measurement is exactly |10>.
5. Because the system is in a deterministic computational basis state, measuring q[0] and q[1] yields |10> with certainty.

Predicted probability distribution: {|10>: 1.0}

### Reference answer

{'predicted_probs': {'2': 1.0}, 'explanation': 'Parametric variant of isqEval/482. Dimension: qubit_variant: q[1] -> q[2].'}

## isqTrain/3621

- task_id: `isqTrain/3621`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `4445`

### Prompt

Implement a quantum circuit in isQ: a 4-qubit Grover search for target state |1001> using the optimal 3 iterations. The circuit should:
1. Initialize 4 qubits in uniform superposition
2. Apply 3 Grover iterations (oracle + diffusion) using a for loop
3. Measure all 4 qubits
Use `deriving gate` and `ctrl<2> CZ` for the multi-controlled phase.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement 4-qubit Grover search to find target state |1001> among 16 possible states.
2. **Qubits**: 4 qubits (q[0]-q[3]), all measured at the end.
3. **State evolution**:
   - **Initialization**: H on all qubits creates uniform superposition |ψ₀⟩ = (1/4)Σₓ|x⟩.
   - **Oracle**: X on q[1],q[2] converts |1001⟩→|1111⟩, then `ctrl<2> CZ` applies -1 phase to |1111⟩, and X gates restore. This flips the sign of |1001⟩ only.
   - **Diffusion**: H→X→`ctrl<2> CZ`→X→H on all qubits reflects the state about the mean amplitude, amplifying the marked state.
   - **3 iterations**: For N=16, optimal iterations ≈ ⌊π√16/4⌉ = 3, rotating the state vector close to |1001⟩.
4. **Expected result**: After 3 iterations, the amplitude of |1001⟩ is amplified to ≈0.981, giving probability ≈96.3%, while all other states have near-equal residual probability ≈0.25% each. The slight spread beyond 100% on |1001⟩ explains the non-zero small probabilities on other states.

## isqTrain/2706

- task_id: `isqTrain/2706`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_oracle`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `213`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
oracle g(3, 1) = [0, 0, 1, 1, 1, 1, 0, 0];
qbit q[3], anc;
procedure main(){
    for i in 0:3{
        H(q[i]);
    }
    X(anc);
    H(anc);
    g(q[0], q[1], q[2], anc);
    for i in 0:3{
        H(q[i]);
        int a = M(q[i]);
        print a;
    }
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The objective is to analyze the given isQ code, determine the step-by-step quantum state evolution, and predict the final output probability distribution.

2.  **Analyze the isQ Code:**
    *   `import std;`
    *   `oracle g(3, 1) = [0, 0, 1, 1, 1, 1, 0, 0];`: This defines an oracle. It acts on 3 qubits and 1 ancilla (total 4). The array represents the phases applied to the basis states $|x\rangle$ where ancilla is $|-\rangle$. Wait, the standard phase oracle definition in isQ (and many other quantum programming languages) is usually: `oracle g(n, m) = [...]` implies an $n$-qubit boolean function $f(x)$ that maps to the array values. Here, $n=3$, $m=1$ (meaning 1 ancilla?). The array has $2^3 = 8$ elements: $f(0)=0, f(1)=0, f(2)=1, f(3)=1, f(4)=1, f(5)=1, f(6)=0, f(7)=0$.
        Actually, the oracle $g$ takes 4 arguments: `q[0], q[1], q[2], anc`. It applies $(-1)^{f(x)}$ to $|x\rangle |-\rangle$. Let's verify this. Yes, standard oracle behavior applies a phase of $-1$ to states where $f(x)=1$.
        $f(x_1 x_2 x_3)$ evaluates to:
        $x=000 \implies f=0$
        $x=001 \implies f=0$
        $x=010 \implies f=1$
        $x=011 \implies f=1$
        $x=100 \implies f=1$
        $x=101 \implies f=1$
        $x=110 \implies f=0$
        $x=111 \implies f=0$
        Notice that $f(x) = x_1 \oplus x_2$. Wait, let's check:
        $00 \to 0$, $01 \to 1$, $10 \to 1$, $11 \to 0$. Yes! $f(x_1, x_2, x_3)$ is just XOR of the first two bits. But let's treat it as a general phase oracle. The state of the first 3 qubits gets multiplied by $(-1)^{f(x)}$.
    *   Initial state: $|0\rangle^{\otimes 3} |0\rangle$
    *   `for i in 0:3 { H(q[i]); }`: Applies H to the first 3 qubits. State becomes $\frac{1}{\sqrt{8}} \sum_{x=0}^{7} |x\rangle |0\rangle$
    *   `X(anc); H(anc);`: Puts ancilla in $|-\rangle$ state. State becomes $\frac{1}{\sqrt{8}} \sum_{x=0}^{7} |x\rangle |-\rangle$.
    *   `g(q[0], q[1], q[2], anc);`: Phase oracle applies $(-1)^{f(x)}$. State becomes $\frac{1}{\sqrt{8}} \sum_{x=0}^{7} (-1)^{f(x)} |x\rangle |-\rangle$.
    *   `for i in 0:3 { H(q[i]); int a = M(q[i]); print a; }`: Applies H to the first 3 qubits again.
    *   We need to evaluate the state of the first 3 qubits.
        $\frac{1}{\sqrt{8}} \sum_{x} (-1)^{f(x)} |x\rangle$. Apply H on all 3.
        The amplitude of $|y\rangle$ will be $\frac{1}{8} \sum_{x} (-1)^{f(x) + x \cdot y}$.
        Since $f(x) = x_1 \oplus x_2$ (where $x = x_1 x_2 x_3$, wait, 0 is MSB or LSB? isQ usually little-endian or big-endian? Let's look at the array: `[0, 0, 1, 1, 1, 1, 0, 0]`.
        Index 0 (000) -> 0
        Index 1 (001) -> 0
        Index

### Reference answer

{'predicted_probs': {'110': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/3905

- task_id: `isqTrain/3905`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1154`

### Prompt

下面的量子程序运行结果不对，请帮我debug：

```
import std;
// Phase kickback with Rz(pi/4)
qbit q[2];

procedure main() {
    // Control in superposition
    H(q[0]);
    // Target in |1> eigenstate
    Y(q[1]);
    // Controlled Rz
    ctrl Rz(3.14159265358979 * 1.0 / 4.0, q[0], q[1]);
    // Detect phase on control
    H(q[0]);
    // Measure
    M(q[0]); M(q[1]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

Let me analyze this bug fix task.

The buggy code has `Y(q[1])` to prepare the target in the |1> eigenstate, but The corrected version `X(q[1])`.

Let me think about why:

1. For phase kickback with Rz(π/4), we need the target qubit to be in an eigenstate of Z (since Rz is a rotation around the Z-axis). The eigenstates of Z are |0⟩ and |1⟩.

2. If the target is |0⟩: Rz(θ)|0⟩ = e^{-iθ/2}|0⟩ - phase kickback is -θ/2
   If the target is |1⟩: Rz(θ)|1⟩ = e^{iθ/2}|1⟩ - phase kickback is +θ/2

3. To prepare |1⟩ from |0⟩, we use X gate. Y gate would prepare i|1⟩ (with a global phase), which still works for kickback since |1⟩ is the Z eigenstate.

Wait, actually Y|0⟩ = i|1⟩, so the state is i|1⟩. Since |1⟩ is still an eigenstate of Z (and Rz), the phase kickback should still work the same way... 

Hmm, let me reconsider. The predicted output {|01>: 0.96194, |11>: 0.03806}.

Let me trace through the corrected circuit:

1. Initial: |00⟩
2. H(q[0]): (|0⟩ + |1⟩)/√2 ⊗ |0⟩ = (|00⟩ + |10⟩)/√2
3. X(q[1]): (|01⟩ + |11⟩)/√2
4. ctrl Rz(π/4, q[0], q[1]): 
   - Rz(π/4) on q[1] when q[0] is |1⟩
   - Rz(π/4)|1⟩ = e^{iπ/8}|1⟩
   - So state becomes: (|01⟩ + e^{iπ/8}|11⟩)/√2
5. H(q[0]): 
   - |01⟩ → (|01⟩ + |11⟩)/√2
   - |11⟩ → (|01⟩ - |11⟩)/√2
   - Result: (|01⟩ + |11⟩ + e^{iπ/8}(|01⟩ - |11⟩))/(2) = ((1+e^{iπ/8})|01⟩ + (1-e^{iπ/8})|11⟩)/2

Probability of |01⟩: |1+e^{iπ/8}|²/4 = (1 + 2cos(π/8) + 1)/4 = (2 + 2cos(π/8))/4 = (1+cos(π/8))/2 ≈ (1+0.9239)/2 ≈ 0.9619

Probability of |11⟩: |1-e^{iπ/8}|²/4 = (1 - 2cos(π/8) + 1)/4 = (2 - 2cos(π/8))/4 = (1-cos(π/8))/2 ≈ 0.03806

This matches! ✓

Now with Y(q[1]) instead of X(q[1]):

1. |00⟩
2. H(q[0]): (|00⟩ + |10⟩)/√2
3. Y(q[1]): Y|0⟩ = i|1⟩, so state is i(|01⟩ + |11⟩)/√2 (global phase doesn't matter)
4. ctrl Rz(π/4): same as before since |1⟩ is eigenstate
5. H(q[0]): same result

Wait, so Y should also give the same result? The only difference is a global phase of i, which doesn't affect measurements.

Hmm, but The predicted output the bug is wrong_gate (Y should be X). Let me think again...

Actually, maybe the issue is more subtle. Let me check if Y in isQ has a different definition.

Y = [[0,-i],[i,0]], so Y|0⟩ = i|1⟩

But wait - in isQ, maybe the Y gate is defined differently? Or maybe the issue is that with the phase from Y, the controlled-Rz works differently?

Actually, let me reconsider. With Y(q[1]):
- State after Y: i|1⟩ for q[1], so overall i(|01⟩ + |11⟩)/√2

After ctrl Rz(π/4):
- The control is q[0], when it's |1⟩, apply

## isqTrain/3078

- task_id: `isqTrain/3078`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `measurement_order`
- source: `isq_train_cot`
- dataset_index: `2976`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit q[4];
procedure main() {
    X(q[0]);
    X(q[1]);
    X(q[2]);
    X(q[3]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations:** The circuit applies an X gate to each of the four qubits (`q[0]` to `q[3]`).
2. **State Evolution:** The system starts in the ground state $|0000\rangle$. Applying the X gates sequentially flips each qubit from $|0\rangle$ to $|1\rangle$, transitioning the state to $|1000\rangle$, then $|1100\rangle$, then $|1110\rangle$, and finally $|1111\rangle$.
3. **Final State:** The quantum state immediately before measurement is $|1111\rangle$.
4. **Probabilities:** Because the state is definitively $|1111\rangle$, measuring the qubits will yield '1111' with absolute certainty.

Predicted probabilities: {'1111': 1.0}

### Reference answer

{'predicted_probs': {'1111': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/1145

- task_id: `isqTrain/1145`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5134`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;

// 3-qubit linear graph state: edges (0,1) and (1,2)
qbit q[3];

procedure main() {
    // Initialize all qubits in |+> state
    H(q[0]); H(q[1]); H(q[2]);
    // Apply CZ for each edge in the linear graph
    CZ(q[0], q[1]);
    CZ(q[1], q[2]);
    // Measure in X basis (H before M)
    // Graph state stabilizers determine the outcomes
    H(q[0]); H(q[1]); H(q[2]);
    // Measure all qubits
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The task is to analyze a given isQ quantum program, trace the quantum state through each operation using Dirac notation, and predict the measurement outcome probabilities. The output must match specific formatting rules (start with "## Circuit Analysis", NO isQ code blocks, concise 3-15 lines).

2.  **Analyze the isQ program**:
    *   `qbit q[3];` -> 3 qubits initialized to $|000\rangle$.
    *   `H(q[0]); H(q[1]); H(q[2]);` -> Apply H to all: state becomes $|+\rangle|+\rangle|+\rangle = \frac{1}{\sqrt{8}} \sum_{x=0}^{7} |x\rangle$.
    *   `CZ(q[0], q[1]);` -> Apply CZ to q0, q1. $|00\rangle \to |00\rangle$, $|01\rangle \to |01\rangle$, $|10\rangle \to |10\rangle$, $|11\rangle \to -|11\rangle$. State becomes $\frac{1}{2} (|00\rangle + |01\rangle + |10\rangle - |11\rangle) \otimes |+\rangle$.
    *   `CZ(q[1], q[2]);` -> Apply CZ to q1, q2. State becomes the linear graph state $|G\rangle$. Specifically, the amplitudes of basis states with odd parity of edges get $-1$. Or in Z basis: $\frac{1}{2\sqrt{2}}(|000\rangle + |001\rangle + |010\rangle - |011\rangle + |100\rangle + |101\rangle - |110\rangle + |111\rangle)$.
    *   `H(q[0]); H(q[1]); H(q[2]);` -> Apply H to all again.
        Let's transform the graph state.
        Recall that $H^{\otimes n} \prod_{(i,j) \in E} CZ_{ij} H^{\otimes n} |0\rangle^{\otimes n}$ is related to parity.
        Actually, the program directly does $H \to CZ_{01} \to CZ_{12} \to H$.
        Let's do this algebraically for each basis state:
        $H^{\otimes 3} \frac{1}{2\sqrt{2}} (|000\rangle+|001\rangle+|010\rangle-|011\rangle+|100\rangle+|101\rangle-|110\rangle+|111\rangle)$.
        Let's look at the Z-basis representation:
        $|000\rangle \xrightarrow{CZ_{12}} |000\rangle$
        $|001\rangle \xrightarrow{CZ_{12}} -|001\rangle$
        $|010\rangle \xrightarrow{CZ_{12}} -|010\rangle$
        $|011\rangle \xrightarrow{CZ_{12}} |011\rangle$
        $|100\rangle \xrightarrow{CZ_{12}} |100\rangle$
        $|101\rangle \xrightarrow{CZ_{12}} -|101\rangle$
        $|110\rangle \xrightarrow{CZ_{12}} -|110\rangle$
        $|111\rangle \xrightarrow{CZ_{12}} |111\rangle$
        Wait, CZ is applied to q1, q2.
        If q1 and q2 are both 1, we apply Z.
        Let's re-evaluate:
        $|000\rangle \to |000\rangle$
        $|001\rangle \to -|001\rangle$ (q1=0, q2=1 -> no? Wait, CZ is q1, q2. So CZ applies Z to q2 if q1=1.
        Wait, standard CZ: control is q[1], target is q[2]. If q1=1, q2 flips phase if q2=1.
        Wait, no! CZ applies Z to target when control is |1>. Actually CZ is symmetric: $|11\rangle \to -|11\rangle$, all others unchanged.
        Let's check the states:
        $|0+\rangle |+\rangle \xrightarrow{CZ_{01}} \frac{1}{2}(|00\rangle+|01\rangle+|10\rangle-|11\rangle) \otimes |+\rangle$.
        Wait, my first CZ was on q0, q1. So $|11\rangle$ in q0, q1 gets minus.
        $|000\r

### Reference answer

{'predicted_probs': {'0': 0.25, '2': 0.25, '5': 0.25, '7': 0.25}, 'explanation': 'Parametric variant of isqEval/440. Dimension: predict probabilities for reference circuit.'}
