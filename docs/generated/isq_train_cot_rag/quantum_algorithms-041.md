# ISQ training COT RAG corpus: quantum_algorithms shard 41

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/961

- task_id: `isqTrain/961`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `hamiltonian_simulation`, `isq_syntax_ctrl_nctrl`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3962`

### Prompt

Write isQ code for the following quantum task: implements a variant of the pauli_evolution pattern using q[2] -> q[4]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

The user wants me to write a reasoning section for an isQ quantum program that implements a variant of the pauli_evolution pattern using q[2] -> q[4].

Let me analyze The implementation:
- It uses 4 qubits (q[0] to q[3])
- Prepares eigenstate |01> of ZZ by applying X to q[1]
- Implements e^(-i*theta*ZZ) with theta = pi/4 using the standard decomposition:
  1. CNOT(q[0], q[1]) - compute parity
  2. Rz(pi/2) on q[1] - apply rotation
  3. CNOT(q[0], q[1]) - undo parity
- The final expected state is |0100> with probability 1.0

Now the task asks for "q[2] -> q[4]" which means I should use qubits q[2] and q[4] for the Pauli evolution, with additional qubits in the ground state.

Let me trace the state evolution:
1. Initial state: |0000>
2. After X(q[1]): |0100>
3. After CNOT(q[0], q[1]): |0100> (since q[0] is |0>, target unchanged)
4. After Rz(pi/2, q[1]): e^(-i*pi/4)|0100> (just a phase on the |1> component)
5. After CNOT(q[0], q[1]): e^(-i*pi/4)|0100>
6. Measurement: |0100> with probability 1.0

Wait, the task says "q[2] -> q[4]" - this likely means the Pauli evolution should be applied to qubits q[2] and q[4], not q[0] and q[1].

So I need to adjust the reasoning to use q[2] and q[4] as the qubits involved in the Pauli ZZ evolution.

For the variant using q[2] -> q[4]:
- We need at least 5 qubits (q[0] to q[4])
- Apply X to q[3] to prepare an eigenstate
- Apply CNOT(q[2], q[3])
- Apply Rz(pi/2) on q[3]
- Apply CNOT(q[2], q[3])
- Measure all 5 qubits

Wait, let me re-read: "q[2] -> q[4]" - this notation is a bit unclear. It could mean:
1. Apply evolution to q[2] and q[4] (skipping q[3])
2. Apply evolution to q[2] through q[4] (meaning q[2], q[3], q[4])

Given the reference uses q[0] and q[1] for a 2-qubit ZZ evolution, I think "q[2] -> q[4]" means we should expand the register and apply the evolution to specific qubits, perhaps q[2] and q[4] as the main ones, with others in ground state.

Actually, Analyzing the more carefully, it's a 2-qubit evolution on q[0] and q[1]. The "variant" with "q[2] -> q[4]" might mean we're shifting the operation to different qubits in a larger register.

Let me reconsider: The task says "significantly expanded qubit register" - so we need more qubits than the base 4. And "q[2] -> q[4]" likely means the evolution is applied to q[2] and q[4] specifically.

For a ZZ evolution on q[2] and q[4] with an eigenstate:
- Need at least 5 qubits
- Prepare eigenstate by applying X to one of them (say q[3] or q[4])
- Apply CNOT(q[2], q[4])
- Apply Rz(pi/2) on q[4]
- Apply CNOT(q[2], q[4])

Hmm, but "q[2] -> q[4]" with the arrow notation in the reference code uses CNOT(q[0], q[1]) - so q[0] -> q[1]. This suggests the evolution involves q[2] and q[4] as the two qubits.

Let me write the reasoning for this variant:

1. Goal: Implement Pauli ZZ evolution e^(-i*pi/4*ZZ) on q[2] and q[4] with expanded register
2. Qubits: Need 5 qubits (q[0] to q[4]), all measured
3. State evolution:
   - |00000> initial
   - X(q[3]): |00010> (prepare eigen

## isqTrain/1844

- task_id: `isqTrain/1844`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_arrays`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `93`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;
qbit q[4];
procedure main() {
    H(q[0]); H(q[1]);
    CNOT(q[0], q[2]);
    CNOT(q[1], q[3]);
    CNOT(q[0], q[2]);
    CNOT(q[0], q[3]);
    H(q[0]); H(q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a concise step-by-step analysis of an isQ quantum program, calculating the probability distribution of its measurement outcomes. The output must follow specific formatting rules (starting with "## Circuit Analysis", no code blocks, ending with the predicted distribution) and be 3-15 lines long.

2.  **Analyze the Circuit:**
    *   Initial state: $|0000\rangle$ for `q[0], q[1], q[2], q[3]`.
    *   `H(q[0]); H(q[1]);`: Apply Hadamard to q0, q1. State becomes $|++00\rangle = \frac{1}{2}(|0000\rangle + |0100\rangle + |1000\rangle + |1100\rangle)$.
    *   `CNOT(q[0], q[2]);`: Flips q2 if q0 is 1. State becomes $\frac{1}{2}(|0000\rangle + |0100\rangle + |1010\rangle + |1110\rangle)$.
    *   `CNOT(q[1], q[3]);`: Flips q3 if q1 is 1. State becomes $\frac{1}{2}(|0000\rangle + |0101\rangle + |1010\rangle + |1111\rangle)$.
    *   `CNOT(q[0], q[2]);`: Flips q2 if q0 is 1. State becomes $\frac{1}{2}(|0000\rangle + |0101\rangle + |1000\rangle + |1101\rangle)$. Wait, $|1010\rangle \xrightarrow{CNOT_{02}} |1000\rangle$. $|1111\rangle \xrightarrow{CNOT_{02}} |1101\rangle$.
    *   `CNOT(q[0], q[3]);`: Flips q3 if q0 is 1. State becomes $\frac{1}{2}(|0000\rangle + |0101\rangle + |1001\rangle + |1100\rangle)$. Let me re-check this.
        *   Initial basis: 0000, 0100, 1000, 1100
        *   After CNOT02: 0000, 0100, 1010, 1110
        *   After CNOT13: 0000, 0101, 1010, 1111
        *   After CNOT02 again: 0000, 0101, 1000, 1101
        *   After CNOT03: 0000, 0101, 1001, 1100
        *   Now apply H on q0 and q1.
        *   Let's analyze the effect of H-CNOT-H.
        *   Actually, H applied to a CNOT control swaps CNOT into a CZ or another CNOT, etc.
        *   Notice $H_{q0} CNOT_{q0,q2} H_{q0} = CZ_{q0,q2}$.
        *   Here, CNOT(q[0], q[2]) is applied, then later H(q[0]) and H(q[1]) are applied. Wait, the code has:
            H(q[0]), H(q[1])
            CNOT(q[0], q[2])
            CNOT(q[1], q[3])
            CNOT(q[0], q[2])
            CNOT(q[0], q[3])
            H(q[0]), H(q[1])
        *   Let's trace state $|0000\rangle$:
            *   H0 H1 -> $|++00\rangle$
            *   CNOT02 -> $\frac{1}{2}(|0000\rangle + |0100\rangle + |1010\rangle + |1110\rangle)$
            *   CNOT13 -> $\frac{1}{2}(|0000\rangle + |0101\rangle + |1010\rangle + |1111\rangle)$
            *   CNOT02 -> $\frac{1}{2}(|0000\rangle + |0101\rangle + |1000\rangle + |1101\rangle)$
            *   CNOT03 -> $\frac{1}{2}(|0000\rangle + |0101\rangle + |1001\rangle + |1100\rangle)$
            *   Apply H0 H1.
            *   $|00\rangle_{01} \rightarrow |00\rangle + |01\rangle + |10\rangle + |11\rangle$
            *   $|01\rangle_{01} \rightarrow |00\rangle - |

### Reference answer

{'predicted_probs': {'00': 0.5, '11': 0.5}, 'explanation': 'Simon\'s with s="11": y·s=0 ⟹ y ∈ {00, 11}. P(|00⟩) ≈ P(|11⟩) ≈ 0.5.'}

## isqTrain/3567

- task_id: `isqTrain/3567`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `hamiltonian_simulation`, `basis_change`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3584`

### Prompt

Fix the bug in the following isQ program.

Bug description: Wrong CNOT direction

The program should XX evolution operator, theta=pi/4.

### Chain-of-thought reasoning

The user wants an analysis of a bug fix in an isQ quantum program.
The bug description says: Wrong CNOT direction.
The program should implement an XX evolution operator with theta=pi/4.
The buggy code has:

The corrected version:

In the buggy code, the first CNOT has q[1] as control and q[0] as target. Then Rz is applied to q[1]. Then the second CNOT has q[0] as control and q[1] as target. This sequence doesn't properly implement the controlled-Z rotation (which should be CNOT(c,t), Rz(t), CNOT(c,t) or equivalent).
To apply a ZZ evolution (after the Hadamards), we need a standard ZZ rotation sequence. A standard ZZ rotation is CNOT(q[0], q[1]) -> Rz(q[1]) -> CNOT(q[0], q[1]).

Let's trace the corrected circuit:
Initial state: |00>
H(q[0]); H(q[1]) -> |++>
CNOT(q[0], q[1]) -> (|00> + |11>)/sqrt(2)
Rz(pi/2, q[1]) -> exp(-i * pi/4 * Z) on q[1] -> (e^{-i\pi/4} |00> + e^{i\pi/4} |11>)/sqrt(2) -> e^{-i\pi/4} (|00> + i|11>)/sqrt(2) (up to global phase). Wait, Rz(theta) adds phase e^{-i*theta/2} to |0> and e^{i*theta/2} to |1>.
So Rz(pi/2) adds e^{-i\pi/4} to |0> and e^{i\pi/4} to |1>.
State after Rz: e^{-i\pi/4} |00> + e^{i\pi/4} |11>.
CNOT(q[0], q[1]) -> e^{-i\pi/4} |00> + e^{i\pi/4} |10> -> e^{-i\pi/4} (|00> + e^{i\pi/2} |10>) = e^{-i\pi/4} (|0> + i|1>) |0> / sqrt(2) * sqrt(2)? No.
Let's recalculate |++> in computational basis: (|0>+|1>)(|0>+|1>)/2 = (|00>+|01>+|10>+|11>)/2.
CNOT(c=0, t=1) maps |00>->|00>, |01>->|01>, |10>->|11>, |11>->|10>.
So (|00>+|01>+|11>+|10>)/2 = (|0>+|1>)(|0>+|1>)/2 = |++>. Wait, CNOT(|++>) = |++>.
But wait, XX evolution is H_q0 H_q1 CZ H_q0 H_q1.
Wait, exp(-i theta/2 X_0 X_1) = H_0 H_1 exp(-i theta/2 Z_0 Z_1) H_0 H_1.
exp(-i theta/2 Z_0 Z_1) = CNOT_{01} Rz(theta)_1 CNOT_{01} ?
Let's check the matrix of CNOT_{01} Rz(theta) CNOT_{01}.
If control is |0>, target is unchanged by CNOT, gets Rz, unchanged by CNOT. So Rz is applied.
If control is |1>, target is flipped to |1> by first CNOT, gets Rz (which adds opposite phase), flipped back by second CNOT. So Rz dagger is applied.
Wait, Z_0 Z_1 means same phase for |00>, opposite for |01>, opposite for |10>, same for |11>.
Wait, Z_0 Z_1 |00> = |00>, Z_0 Z_1 |01> = -|01>, Z_0 Z_1 |10> = -|10>, Z_0 Z_1 |11> = |11>.
If we use CNOT(0,1) Rz(1) CNOT(

## isqTrain/4110

- task_id: `isqTrain/4110`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `5433`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[4];

procedure main() {
    X(q[0]);
    X(q[2]);

    H(q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 16.0, q[3], q[0]);
    H(q[1]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[3], q[1]);
    H(q[2]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[3], q[2]);
    H(q[3]);
    CNOT(q[0], q[3]);
    CNOT(q[3], q[0]);
    CNOT(q[0], q[3]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[1]);
    CNOT(q[1], q[2]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

Initial state: |0000⟩

After X(q[0]) and X(q[2]): |0101⟩

Now we apply QFT-like operations (H followed by controlled Rz gates):

For q[0]:
- H(q[0]): The state of q[0] is |1⟩, so H|1⟩ = |−⟩ = (|0⟩ - |1⟩)/√2
- State becomes: (|0101⟩ - |1101⟩)/√2

Wait, let me be more careful with the ordering. q[0] is the least significant bit typically, but in isQ, let me just track the state.

State: |q[3], q[2], q[1], q[0]⟩ = |0,1,0,1⟩

H(q[0]): q[0] goes from |1⟩ to |−⟩
State: (|0101⟩ - |0100⟩)/√2

ctrl Rz(π/2, q[1], q[0]): when q[1]=1, apply Rz(π/2) to q[0]
In (|0101⟩ - |0100⟩)/√2, q[1]=0 in both terms, so no phase applied.
State unchanged.

ctrl Rz(π/4, q[2], q[0]): when q[2]=1, apply Rz(π/4) to q[0]
q[2]=1 in both terms. Rz(π/4)|0⟩ = |0⟩, Rz(π/4)|1⟩ = e^{iπ/4}|1⟩
State: (e^{iπ/4}|0101⟩ - |0100⟩)/√2

ctrl Rz(π/8, q[3], q[0]): when q[3]=1, apply Rz(π/8) to q[0]
q[3]=0 in both terms, no change.

H(q[1]): q[1] goes from |0⟩ to |+⟩
State: (e^{iπ/4}(|0101⟩ + |1101⟩) - (|0100⟩ + |1100⟩))/(2)

Wait, let me be more careful.

State before H(q[1]): (e^{iπ/4}|0101⟩ - |0100⟩)/√2

H acts on q[1] which is |0⟩ in both terms. H|0⟩ = |+⟩ = (|0⟩ + |1⟩)/√2

State: (e^{iπ/4}( |0001⟩ + |0101⟩) - (|0000⟩ + |0100⟩))/(2)

Wait, I'm getting confused with qubit ordering. Let me use |q[3]q[2]q[1]q[0]⟩ notation consistently.

Initial: |0000⟩
After X(q[0]): |0001⟩
After X(q[2]): |0101⟩

Now q[0]=1, q[1]=0, q[2]=1, q[3]=0.

H(q[0]): H acts on q[0] which is |1⟩ → |−⟩
State: (|0101⟩ - |0100⟩)/√2

ctrl Rz(π/2, q[1], q[0]): controlled on q[1]. Both terms have q[1]=0, so nothing happens.

ctrl Rz(π/4, q[2], q[0]): controlled on q[2]. Both terms have q[2]=1.
Rz(π/4) applied to q[0]:
- For |0101⟩: q[0]=|1⟩, gets phase e^{iπ/8} (since Rz(π/4)|1⟩ = e^{-iπ/8}|1⟩... wait)

Let me recall: Rz(θ) = [[e^{-iθ/2}, 0], [0, e^{iθ/2}]]

So Rz(π/4)|0⟩ = e^{-iπ/8}|0⟩ and Rz(π/4)|1⟩ = e^{iπ/8}|1⟩

ctrl Rz(π/4, q[2], q[0]): when q[2]=1, apply Rz(π/4) to q[0].
Both terms have q[2]=1.
- |0101⟩: q[0]=|1⟩ → e^{iπ/8}|1⟩, so → e^{iπ/8}|0101⟩
- |0100⟩: q[0]=|0⟩ → e^{-iπ/8}|0⟩, so →

### Reference answer

Uniform distribution across 16 states

## isqTrain/3558

- task_id: `isqTrain/3558`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `interference`, `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `5481`

### Prompt

Fix the bug in the following isQ program.

Bug description: Missing Hadamard gate

The program should SWAP test: orthogonal states |0> vs |1>.

### Chain-of-thought reasoning

## Bug Analysis

**1. Bug identification:** The initial Hadamard gate `H(q[0])` is missing from the beginning of `main()`. The comment `// Control in superposition` indicates where it should go, but no gate follows it. Without this, the control qubit remains |0⟩, the controlled-swap (three-CNOT decomposition) never activates, and the test is non-functional.

**2. Fix:** Add `H(q[0]);` immediately after the `// Control in superposition` comment, before the state preparation section.

**3. State evolution of corrected circuit:**
- Initial: |000⟩
- **H(q[0])** → (1/√2)(|000⟩ + |100⟩)
- X(q[2]) → (1/√2)(|001⟩ + |101⟩)
- ctrl CNOT(q[0], q[2], q[1]) → (1/√2)(|001⟩ + |111⟩)
- ctrl CNOT(q[0], q[1], q[2]) → (1/√2)(|001⟩ + |110⟩)
- ctrl CNOT(q[0], q[2], q[1]) → (1/√2)(|001⟩ + |110⟩)
- H(q[0]) → (1/2)(|001⟩ + |101⟩ + |010⟩ − |110⟩)
- Measure q[0]: P(|0⟩) = P(|1⟩) = 0.5 ✓

The 50/50 outcome confirms orthogonal states — the swap (three-CNOT decomposition) test correctly distinguishes |0⟩ and |1⟩ as having zero overlap.

## isqTrain/3030

- task_id: `isqTrain/3030`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5419`

### Prompt

Code this in isQ: creates a 4-qubit GHZ state and then applies an X gate to qubit 3.

Requirements:
- Declare `qbit q[4];` at global scope.
- Measure all 4 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a 4-qubit GHZ state then apply X to qubit 3.
2. **Qubits**: 4 qubits declared globally (`qbit q[4]`), all measured.
3. **State evolution**:
   - Start: |0000⟩
   - H(q[0]): (|0000⟩ + |1000⟩)/√2
   - CNOT(q[0],q[1]): (|0000⟩ + |1100⟩)/√2
   - CNOT(q[1],q[2]): (|0000⟩ + |1110⟩)/√2
   - CNOT(q[2],q[3]): (|0000⟩ + |1111⟩)/√2 — standard GHZ state
   - X(q[3]): flips qubit 3, giving (|0001⟩ + |1110⟩)/√2
4. **Probabilities**: Each basis state has amplitude 1/√2, so probability 0.5 each.

## isqTrain/2852

- task_id: `isqTrain/2852`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1446`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
qbit q[2];
procedure main() {
    X(q[0]);
    H(q[0]);
    CNOT(q[0], q[1]);
    H(q[0]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **X on q[0]**: $\left|00\right\rangle \rightarrow \left|10\right\rangle$
2.  **H on q[0]**: $\left|10\right\rangle \rightarrow \frac{1}{\sqrt{2}}(\left|00\right\rangle + \left|10\right\rangle) = \left|+0\right\rangle$
3.  **CNOT(q[0], q[1])**: $\left|+0\right\rangle \rightarrow \frac{1}{\sqrt{2}}(\left|00\right\rangle + \left|11\right\rangle) = \left|\Phi^+\right\rangle$
4.  **H on q[0]**: $H \otimes I \left|\Phi^+\right\rangle = \frac{1}{\sqrt{2}} \left(\left|+0\right\rangle + \left|-1\right\rangle\right) = \frac{1}{2}\left(\left|00\right\rangle + \left|10\right\rangle - \left|01\right\rangle + \left|11\right\rangle\right)$ wait. Let's do it carefully.
    $H |0\rangle = |+\rangle$, $H |1\rangle = |-\rangle$.
    State is $\frac{1}{\sqrt{2}}(\left|00\right\rangle + \left|11\right\rangle)$.
    Apply $H$ to q[0]:
    $H_0 (\left|00\right\rangle + \left|11\right\rangle)/\sqrt{2} = (\left|+0\right\rangle + \left|-1\right\rangle)/\sqrt{2}$
    $= \frac{1}{\sqrt{2}} \left[ \frac{1}{\sqrt{2}}(\left|0\right\rangle + \left|1\right\rangle)\left|0\right\rangle + \frac{1}{\sqrt{2}}(\left|0\right\rangle - \left|1\right\rangle)\left|1\right\rangle \right]$
    $= \frac{1}{2} (\left|00\right\rangle + \left|10\right\rangle + \left|01\right\rangle - \left|11\right\rangle)$.
5.  **Measurements**: Probability of each basis state is $\left|\frac{1}{2}\right|^2 = 0.25$.

Let me double check the state evolution:
- Initial: |00>
- X(q[0]): |10>
- H(q[0]): 1/sqrt(2) (|00> - |10>) wait. H|1> = |-> = 1/sqrt(2)(|0> - |1>). So H on |10> gives 1/sqrt(2)(|00> - |10>). Wait! H(q[0]) on |10>.
Let's re-read X and H.
H|0> = |+>
H|1> = |->
So:
|00> --X(0)--> |10>
|10> --H(0)--> (|00> - |10>) / sqrt(2)
(|00> - |10>) / sqrt(2) --CNOT(0,1)--> (|00> - |11>) / sqrt(2)
(|00> - |11>) / sqrt(2) --H(0)--> (|+0> - |-1>) / sqrt(2) = ( (|0>+|1>)|0> - (|0>-|1>)|1> ) / 2 = (|00> + |10> - |01> + |11>) / 2.
Probabilities: 1/4 for all.

Let me re-read X and H.
H = 1/sqrt(2) [[1, 1], [1, -1]]
X = [[0, 1], [1, 0]]
X|0> = |1>.
H|1> = 1/sqrt(2) (|0> - |1>).
So:
1. `X(q[0])`: |00> -> |10>
2. `H(q[0])`: |10> -> (|00> - |10>) / sqrt(2)
3. `CNOT(q[0], q[1])`: (|00> - |10>) / sqrt(2) -> (|00> - |11>) / sqrt(2)
4. `H(q[0])`: (|00> - |11>) / sqrt(2) -> (

### Reference answer

{'predicted_probs': {'00': 0.25000000000000006, '01': 0.24999999999999994, '10': 0.25000000000000006, '11': 0.24999999999999994}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/2785

- task_id: `isqTrain/2785`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `measurement_order`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4751`

### Prompt

There's an error in this quantum circuit implementation. Fix it:

```isq
import std;

qbit q[2];

procedure main(){
    H(q[0]);
    CNOT(q[0],q[1]);
    X(q[0]); // BUG: spurious X before measurement

    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

## Bug Analysis

**What the bug is:**
The line `X(q[0]);` is a spurious X gate applied to q[0] after the CNOT entangling operation. This bit-flip rotates the state out of the intended Bell basis before measurement.

**What the fix is:**
Remove the `X(q[0]);` line entirely, leaving only `H(q[0])` and `CNOT(q[0],q[1])` as the Bell state preparation, followed directly by measurements.

**State evolution of the corrected circuit:**
1. Initial state: |00⟩
2. H(q[0]): (|0⟩ + |1⟩)/√2 ⊗ |0⟩ = (|00⟩ + |10⟩)/√2
3. CNOT(q[0],q[1]): (|00⟩ + |11⟩)/√2 — this is the Bell state Φ⁺
4. Measurements yield |00⟩ with probability 0.5 and |11⟩ with probability 0.5, matching the predicted output.

## isqQA/quantum_algorithms/126_hardware_limitations

- task_id: `isqQA/quantum_algorithms/126_hardware_limitations`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `hardware_limitations`, `algorithm`, `隐藏子群问题`
- source: `qa_pipeline`
- dataset_index: `1683`

### Prompt

隐藏子群问题（HSP）是量子计算中一类核心的理论框架，Shor算法和Simon算法都可以看作它的特例。然而，在理论上有指数级加速优势的HSP通用量子算法，在当前的含噪中型量子（NISQ）设备上却极难真正有效运行，特别是当底群为非阿贝尔群（如对称群 $S_n$）时更是如此。请从NISQ设备的硬件局限性、量子比特连通性以及退相干影响的角度，深度分析将通用HSP量子算法（特别是其中的量子傅里叶变换部分）部署到物理量子芯片上时面临的核心物理阻碍，并结合底层硬件效率进行探讨。

### Reference answer

<think...
隐藏子群问题（HSP）的量子算法核心在于利用量子傅里叶变换（QFT）提取隐藏子群的共轭类信息。对于非阿贝尔群，这要求我们能够在量子硬件上实现群代数上的QFT。我需要详细阐述NISQ设备的噪声、退相干和拓扑连通性是如何摧毁这一干涉过程的。超导量子计算机通常具有有限的连通性（如重六边形或网格拓扑），而实现非阿贝尔QFT需要高度非局部的多量子比特纠缠操作，这将导致大量的SWAP开销，进而急剧增加线路深度，使得量子态在完成计算前就发生退相干。结合这些点组织回答。
</think...
隐藏子群问题（HSP）是量子计算理论中的一颗明珠，其通用量子算法的核心机制是通过酉变换制备函数叠加态，随后在底群上执行量子傅里叶变换（QFT），利用量子干涉来提取隐藏子群的特征频率。尽管在理论上具有极其重要的地位，但在当前的含噪中型量子（NISQ）时代，将其部署到超导或离子阱等物理硬件上面临着难以逾越的鸿沟，特别是对于解决图同构等涉及非阿贝尔群（如对称群 $S_n$）的复杂情况。从NISQ硬件的局限性和退相干角度来看，核心阻碍主要体现在以下几个深层方面：

1. 量子态退相干时间与线路深度的极度不对称
HSP算法的有效性高度依赖于计算过程中量子态相位信息的完美保持。然而，非阿贝尔群上的QFT极其复杂。例如，在对称群 $S_n$ 上实现QFT需要 $O(n^2 \log n)$ 数量级的量子门操作。在超导量子平台中，尽管双比特门（如CZ或CNOT）操作速度较快（约几十纳秒），但目前的退相干时间（$T_1$ 和 $T_2$）普遍在 $100\mu s$ 左右。这意味着，随着问题规模 $n$ 的增加，执行完整的非阿贝尔QFT所需的线路深度将迅速突破物理系统的相干时间极限。在相位信息完全退相干之前，量子计算机根本无法完成足够长的干涉计算，导致测量结果退化为随机噪声，算法的指数级加速优势彻底丧失。

2. 物理拓扑限制引发的巨大SWAP开销
硬件效率不仅取决于门的保真度，还高度受限于芯片的物理拓扑连通性。HSP中的群QFT往往需要高阶的多比特纠缠甚至远程量子比特间的受控操作。当前的NISQ超导芯片大多受限于平面拓扑结构（如网格或重六边形架构），并非全连通。在非全连通的拓扑中实现远程多比特门，必须引入大量的SWAP操作来移动量子态。每增加一层SWAP网络，就会增加极其可观的线路深度和门错误率累积。这种因为硬件连通性局限而被迫增加的底层调度开销，对于对相位极度敏感的HSP算法是致命的。

3. 多控制门在NISQ时代的保真度瓶颈
在非阿贝尔HSP的电路实现中，不可避免地涉及大量的多控制高阶门操作（例如受控循环移位和受控对换）。在物理层面，这些高阶门需要分解为基本单比特门和双比特门组合。在当前硬件的双比特门保真度尚停留在99%~99.5%左右的阶段，这种深层分解会引发严重的误差累积。由于NISQ设备缺乏完全实用的量子纠错码（QEC）来主动修正这些错误，任何微小的门误差或环境噪声引起的退相干，都会破坏HSP算法依赖的量子干涉振幅。

总结而言，通用HSP量子算法（特别是非阿贝尔情况）本质上要求深层、高保真且高度非局部的量子计算资源，这与当前NISQ设备受限的连通性、极短的退相干时间以及缺乏容错机制的物理现实形成了强烈的冲突。

## isqTrain/4821

- task_id: `isqTrain/4821`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_import_qft`, `superposition`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `5203`

### Prompt

I need an isQ program to applies inverse QFT to a uniform superposition. Import std and qft. Declare 2 global qubits. Apply H to both qubits to create uniform superposition, then apply qft_inv(q). The inverse QFT of a uniform superposition on 2 qubits produces |00>. Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply inverse QFT to a uniform superposition of 2 qubits, which should yield |00⟩.
Two global qubits q[0] and q[1] are used, and both are measured.
State evolution: |00⟩ →H(q[0])→ (|00⟩+|10⟩)/√2 →H(q[1])→ (|00⟩+|01⟩+|10⟩+|11⟩)/2 = |+⟩|+⟩.
The inverse QFT (qft_inv) maps the uniform superposition back to |00⟩, since QFT|0⟩^⊗n produces a uniform superposition.
Expected measurement probabilities: {|00⟩: 1.0}, as the final state is exactly |00⟩.
