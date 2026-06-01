# ISQ training COT RAG corpus: state_preparation shard 10

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3745

- task_id: `isqTrain/3745`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `3526`

### Prompt

I need an isQ program to Prepare a 2-qubit product state by applying Ry(0.0) to q[0] and Ry(1.5) to q[1]. Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Create a 2-qubit product state using specific $R_y$ rotations and measure both qubits.
2. Qubits: 2 qubits ($q[0]$ and $q[1]$), both are measured.
3. Step-by-step state evolution:
   - Initial state is $|00\rangle$.
   - Apply $R_y(0.0)$ to $q[0]$, which acts as an identity, leaving it in $|0\rangle$.
   - Apply $R_y(1.5)$ to $q[1]$, evolving its state to $\cos(0.75)|0\rangle + \sin(0.75)|1\rangle$.
   - The joint 2-qubit state becomes $|0\rangle \otimes (\cos(0.75)|0\rangle + \sin(0.75)|1\rangle)$.
4. Probabilities: Measuring this state yields $P

## isqTrain/4814

- task_id: `isqTrain/4814`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_switch`, `mid_circuit_measurement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3066`

### Prompt

Implement the following in isQ: uses switch for conditional phase correction. Declare 2 global qubits. Set q[0] to |1>. Measure q[0] into x. Use switch(x): case 0 applies S(q[1]), case 1 applies H(q[1]) followed by X(q[1]). Since x=1, H(q[1]) and X(q[1]) execute. H|0>=(|0>+|1>)/sqrt(2), then X swaps to (|1>+|0>)/sqrt(2). q[1] is in equal superposition. Measure q[1]. Expected: q[0]=1, q[1]=50/50.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Demonstrate conditional phase correction using a classical `switch` on a measured qubit.
2. **Qubits**: 2 global qubits `q[0], q[1]`, both measured.
3. **State evolution**:
   - Start: |00⟩
   - X(q[0]): |10⟩
   - M(q[0]) → x=1 (deterministic, since q[0]=|1⟩)
   - switch(x=1): H(q[1]) → |1⟩⊗(|0⟩+|1⟩)/√2 = (|10⟩+|11⟩)/√2
   - X(q[1]): X swaps |0⟩↔|1⟩ → (|11⟩+|10⟩)/√2
4. **Final state**: Equal superposition of |10⟩ and |11⟩, giving probabilities {|10⟩: 0.5, |11⟩: 0.5}.

## isqTrain/4783

- task_id: `isqTrain/4783`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_for_loop`, `isq_syntax_if_else`
- source: `isq_train_cot`
- dataset_index: `3379`

### Prompt

Code this in isQ: implements: HZH = X on 7 qubits via for-loops. Declare a global qbit array q of 7 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Demonstrate the identity HZH = X on 7 qubits by applying H-Z-H sequences, transforming |0⟩ to |1⟩ on each qubit.
2. **Qubits**: 7 qubits (q[0]–q[6]), all measured at the end.
3. **State evolution**:
   - Initial state: |0000000⟩
   - After H on all qubits: |+++++++⟩ (where |+⟩ = (|0⟩+|1⟩)/√2)
   - After Z on all qubits: |-------⟩ (since Z|+⟩ = |−⟩, where |−⟩ = (|0⟩−|1⟩)/√2)
   - After H on all qubits: |1111111⟩ (since H|−⟩ = |1⟩)
4. **Expected result**: All qubits are in |1⟩, so measurement yields |1111111⟩ with probability 1.0.

## isqTrain/4471

- task_id: `isqTrain/4471`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `1882`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;

qbit q[3];

procedure main() {
    
    q = [0.0, 0.5773502691896257, 0.5773502691896257, 0.0, 0.5773502691896257, 0.0, 0.0, 0.0];
    
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Input Program:**
    *   3 qubits: `q[3]`.
    *   Initial state given as a statevector: `q = [0.0, 0.5773502691896257, 0.5773502691896257, 0.0, 0.5773502691896257, 0.0, 0.0, 0.0]`.
    *   The statevector is of size 8 ($2^3$). The amplitudes are:
        *   $|000\rangle = 0.0$
        *   $|001\rangle \approx 0.57735 = 1/\sqrt{3}$
        *   $|010\rangle \approx 0.57735 = 1/\sqrt{3}$
        *   $|011\rangle = 0.0$
        *   $|100\rangle \approx 0.57735 = 1/\sqrt{3}$
        *   $|101\rangle = 0.0$
        *   $|110\rangle = 0.0$
        *   $|111\rangle = 0.0$
    *   The state is $\frac{1}{\sqrt{3}}(|001\rangle + |010\rangle + |100\rangle)$.
    *   Gates applied: `X(q[0])` flips qubit 0 (the right-most bit in standard qubit indexing $q_2 q_1 q_0$, assuming standard isQ mapping where $q_0$ corresponds to bit 0 of the index). Let's double check standard indexing. In statevector `[q000, q001, q010, q011, q100, q101, q110, q111]`, applying `X(q[0])` swaps amplitudes of indices differing only in bit 0.
        *   $|000\rangle \leftrightarrow |001\rangle$ (0.0 and 1/$\sqrt{3}$) -> $|001\rangle=0$, $|000\rangle=1/\sqrt{3}$
        *   $|010\rangle \leftrightarrow |011\rangle$ (1/$\sqrt{3}$ and 0) -> $|011\rangle=1/\sqrt{3}$, $|010\rangle=0$
        *   $|100\rangle \leftrightarrow |101\rangle$ (1/$\sqrt{3}$ and 0) -> $|101\rangle=1/\sqrt{3}$, $|100\rangle=0$
    *   Resulting state: $\frac{1}{\sqrt{3}}(|000\rangle + |011\rangle + |101\rangle)$.
    *   Wait, let's look at the bitstrings: `q[0]` flips the 0th bit.
    *   Let's re-verify isQ bit convention. If $q[0]$ is measured first: `M(q[0]); M(q[1]); M(q[2]);`. "earlier measured qubit = higher bit". So $q_0$ is the *most significant* bit (bit 2), $q_1$ is bit 1, $q_2$ is bit 0.
    *   Let's check the statevector array. Does `[0.0, 0.577..., 0.577..., 0.0, 0.577..., 0.0, 0.0, 0.0]` correspond to $q_2 q_1 q_0$ or $q_0 q_1 q_2$?
    *   Usually, `q[0]` is the lowest bit in statevector indexing. i.e., index 1 is `001` (meaning $q_0=1, q_1=0, q_2=0$).
    *   Let's assume standard Qiskit/isQ mapping: `q[0]` is bit 0.
    *   Initial state: $\frac{1}{\sqrt{3}}(|001\rangle_{q_2 q_1 q_0} + |010\rangle_{q_2 q_1 q_0} + |100\rangle_{q_2 q_1 q_0})$.
    *   Apply `X(q[0])`. This flips bit 0.
    *   $|001\rangle \to |000\rangle$
    *   $|010\rangle \to |011\rangle$
    *   $|100\rangle \to |101\rangle$
    *   The resulting statevector is $\frac{1}{\sqrt{

### Reference answer

{'predicted_probs': {'000': 0.333333, '101': 0.333333, '110': 0.333333}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|000>) = 0.3333, P(|101>) = 0.3333, P(|110>) = 0.3333.'}

## isqTrain/4226

- task_id: `isqTrain/4226`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2100`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;
qbit q[2];

procedure main() {
    Ry(1.000, q[0]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations**: The circuit initializes two qubits in |00>. It applies a rotation gate Ry(1.000) to q[0], followed by a CNOT with q[0] as control and q[1] as target. Finally, it measures both qubits.
2. **State Evolution**:
   - Initial state: |00>
   - After `Ry(1.000, q[0])`: `Ry` rotates q[0] around the Y-axis by 1.000 radians. The state becomes `cos(0.5)|00> + sin(0.5)|10>`.
   - After `CNOT(q[0], q[1])`: The CNOT gate entangles the two qubits, flipping q[1] when q[0] is |1>. The state becomes `cos(0.5)|00> + sin(0.5)|11>`.
3. **Final State**: `cos(0

### Reference answer

Dominant output states: |00> with probability ~0.77 each

## isqTrain/1556

- task_id: `isqTrain/1556`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `4756`

### Prompt

Implement the following in isQ: Apply Y gate to each of 6 qubits and measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply a Y gate to each of 6 qubits, then measure all qubits.
2. **Qubits**: 6 qubits (q[0]–q[5]), all measured.
3. **State evolution**: Each qubit starts in |0⟩. The Y gate maps |0⟩ → i|1⟩. After applying Y to all 6 qubits, the state is (i|1⟩)^⊗6 = i⁶|111111⟩ = (-1)|111111⟩.
4. **Expected probabilities**: The global phase (-1) is irrelevant to measurement, so the only possible outcome is |111111⟩ with probability 1.0.

## isqTrain/4020

- task_id: `isqTrain/4020`
- task_type: `bug_fix`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5647`

### Prompt

There's an error in this quantum circuit implementation. Fix it:

```
import std;
// Graph state for complete_4 topology
// Edges: [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
qbit q[4];

procedure main() {
    // Step 1: Hadamard on all qubits (|+>^n)
    H(q[0]);
    H(q[1]);
    H(q[2]);
    H(q[3]);
    // Step 2: CZ for each edge
    CZ(q[0], q[1]);  // edge (0,1)
    CZ(q[0], q[2]);  // edge (0,2)
    CZ(q[3], q[0]);  // edge (0,3)
    CZ(q[1], q[2]);  // edge (1,2)
    CZ(q[1], q[3]);  // edge (1,3)
    CZ(q[2], q[3]);  // edge (2,3)
    // Measure all qubits
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
}

``` (bug type: swapped qubits)

### Chain-of-thought reasoning

## Bug Analysis
1. **Bug**: In the buggy code, edge (0,3) is implemented as `CZ(q[3], q[0])` with swapped qubits. While CZ is symmetric (CZ(a,b) = CZ(b,a)), the original intent was to apply the gate for edge (0,3) in a consistent qubit ordering.

2. **Fix**: Change `CZ(q[3], q[0])` to `CZ(q[0], q[3])` on the line corresponding to edge (0,3).

3. **State evolution (corrected)**:
   - Initialize 4 qubits: |0000⟩
   - H on all qubits: |++++⟩ = H^⊗4|0000⟩
   - CZ on all 6 edges {(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)}: produces the complete K₄ graph state
   - The graph state has equal superposition over all 16 basis states with complex phases from CZ gates
   - Measurement probabilities: each of the 16 outcomes (|0000⟩ to |1111⟩) has probability 1/16 = 0.0625

## isqTrain/3188

- task_id: `isqTrain/3188`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `361`

### Prompt

Write an isQ program that an isQ program: apply Ry(4*pi/9) to one qubit, then CNOT to a second qubit, creating partial entanglement.

### Chain-of-thought reasoning

## Reasoning
Goal: Create partial entanglement by rotating one qubit then entangling it with a second via CNOT.

Two qubits (q[0], q[1]) are used and both are measured.

State evolution:
1. Initial: |00⟩
2. Ry(4π/9) on q[0]: cos(2π/9)|00⟩ + sin(2π/9)|10⟩
3. CNOT(q[0], q[1]): cos(2π/9)|00⟩ + sin(2π/9)|11⟩

Probabilities: P(|00⟩) = cos²(2π/9) ≈ 0.5868, P(|11⟩) = sin²(2π/9) ≈ 0.4132. Since the rotation angle is not π/2, we get unequal superposition—partial rather than maximal entanglement.

## isqTrain/4815

- task_id: `isqTrain/4815`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `isq_syntax_switch`, `isq_syntax_if_else`, `isq_syntax_classical_vars`, `superposition`
- source: `isq_train_cot`
- dataset_index: `360`

### Prompt

Write isQ code for the following quantum task: combining switch with if-else. Declare 2 global qubits. Set int a=1 and int b=1. Compute int c = a * b (c=1). Use switch(c): case 0 applies X(q[0]), case 1 checks if a==b with if-else. If a==b, apply H(q[0]) and H(q[1]); otherwise apply X(q[1]). Since c=1 and a==b, both qubits get H. Measure both. Expected: uniform distribution over all 4 states.

### Chain-of-thought reasoning

## Reasoning
Goal: Demonstrate a nested `switch` and `if-else` control flow to conditionally prepare a 2-qubit state.
Qubits: 2 global qubits `q[2]`, both initialized to |00> and measured.
Evolution:
- Variables are set a=1, b=1, computing c=1. The switch enters case 1.
- Since a==b (1==1), H gates are applied to both q[0] and q[1].
- H(q[0]) transforms |00> into an equal superposition: (|00> + |10>)/√2.
- H(q[1]) entangles the second qubit, yielding the final state |++> = (|00> + |01> + |10> + |11>)/2.
Probabilities: Measuring the final state |++> in the computational basis results in a perfectly uniform distribution of 0.25 across all four basis states.

## isqTrain/4782

- task_id: `isqTrain/4782`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_for_loop`, `isq_syntax_if_else`
- source: `isq_train_cot`
- dataset_index: `2177`

### Prompt

Create an isQ quantum circuit that implements: for-loop X on 7 qubits -> all |1>. Declare a global qbit array q of 7 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare all 7 qubits in the |1⟩ state by applying X gates in a loop.
2. **Qubits**: 7 global qubits `q[0..6]`, all measured at the end.
3. **State evolution**: Initial state is |0⟩^⊗7 = |0000000⟩. The for-loop applies X to each qubit j from 0 to 6, flipping |0⟩ → |1⟩. After each X(q[j]), qubit j transitions from |0⟩ to |1⟩. Final state is |1111111⟩.
4. **Expected probabilities**: Since the final state is exactly |1111111⟩ with no superposition, measurement yields |1111111⟩ with probability 1.0.
