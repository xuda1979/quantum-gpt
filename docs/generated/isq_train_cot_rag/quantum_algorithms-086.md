# ISQ training COT RAG corpus: quantum_algorithms shard 86

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/2730

- task_id: `isqTrain/2730`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3608`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[3];

procedure main(){
    H(q[0]);
    X2P(q[1]);
    CZ(q[0], q[2]);
    Y2M(q[0]);
    CZ(q[2], q[1]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict the final state and probability distribution for an isQ quantum circuit.
    *   Circuit gates: `H(q[0])`, `X2P(q[1])`, `CZ(q[0], q[2])`, `Y2M(q[0])`, `CZ(q[2], q[1])`.
    *   Qubits: `q[0], q[1], q[2]`.
    *   Output format: "## Circuit Analysis" section, 3-15 lines, Dirac notation, ending with predicted probability distribution.

2.  **Analyze the Circuit & Gates:**
    *   Initial state: $|000\rangle$
    *   `H(q[0])`: $|0\rangle \to |+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$. State becomes $\frac{1}{\sqrt{2}}(|000\rangle + |100\rangle)$.
    *   `X2P(q[1])`: This is $R_x(\pi/2)$. On $|0\rangle$, $R_x(\pi/2)|0\rangle = \frac{1}{\sqrt{2}}(|0\rangle - i|1\rangle)$. Let's verify: $R_x(\theta) = \cos(\theta/2)I - i\sin(\theta/2)X$. $R_x(\pi/2) = \frac{1}{\sqrt{2}}(I - iX)$. $R_x(\pi/2)|0\rangle = \frac{1}{\sqrt{2}}(|0\rangle - i|1\rangle)$. State is now $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)_0 \otimes \frac{1}{\sqrt{2}}(|0\rangle - i|1\rangle)_1 \otimes |0\rangle_2$.
    *   `CZ(q[0], q[2])`: Control q[0], Target q[2].
        State is $\frac{1}{2}(|00\rangle + |10\rangle)_{0,2} \otimes (|0\rangle - i|1\rangle)_1$. Wait, order is $q_0 q_1 q_2$.
        Current state: $\frac{1}{2}(|000\rangle - i|010\rangle + |100\rangle - i|110\rangle)$.
        Apply $CZ(q[0], q[2])$: Flips sign when $q_0=1, q_2=1$, but $q_2$ is currently 0. So $CZ$ does nothing.
        State remains $\frac{1}{2}(|000\rangle - i|010\rangle + |100\rangle - i|110\rangle)$.
    *   `Y2M(q[0])`: This is $R_y(-\pi/2)$. $R_y(\theta) = \cos(\theta/2)I - i\sin(\theta/2)Y$.
        $R_y(-\pi/2) = \frac{1}{\sqrt{2}}(I + iY) = \frac{1}{\sqrt{2}}\begin{pmatrix} 1 & 1 \\ -1 & 1 \end{pmatrix}$.
        Let's apply to $q_0$:
        $|0\rangle \to \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$
        $|1\rangle \to \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$
        Apply to state $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)_0$:
        $\frac{1}{\sqrt{2}} \left( \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) + \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \right) = \frac{1}{\sqrt{2}} ( \frac{2}{\sqrt{2}} |0\rangle ) = |0\rangle$.
        Wait, let me double check this.
        $R_y(-\pi/2) |+\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) + \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) = |0\rangle$. Correct!
        Wait, $CZ(q[0], q[2])$

### Reference answer

{'predicted_probs': {'000': 0.5000000000000002, '010': 0.4999999999999999}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/1261

- task_id: `isqTrain/1261`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `boolean_logic`, `interference`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3120`

### Prompt

Help me write isQ code that implements a variant of the deutsch_jozsa pattern using q[3] -> q[5]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

Let me analyze the Deutsch-Jozsa variant described In the implementation.

1. **Goal**: Implement a Deutsch-Jozsa circuit with a 5-qubit register (using q[0]-q[4]), where only q[0]-q[2] participate in the algorithm, and q[3]-q[4] remain in |0⟩.

2. **Qubits**: 5 input qubits (q[0]-q[4]) + 1 ancilla (anc[0]). All 5 input qubits are measured.

3. **Oracle**: f(x) = (x[0] AND x[1]) XOR x[2], which is balanced (outputs 0 for 4 inputs, 1 for 4 inputs).

4. **State evolution**:

Initial state: |00000⟩|1⟩ (after X on ancilla)

After H on ancilla: |00000⟩(|0⟩ - |1⟩)/√2

After H on q[0], q[1], q[2]:
(|0⟩+|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2 ⊗ |00⟩ ⊗ (|0⟩-|1⟩)/√2

= 1/√8 Σ_{x∈{0,1}^3} |x,00⟩(|0⟩-|1⟩)/√2

After oracle f (phase kickback):
1/√8 Σ_x (-1)^{f(x)} |x,00⟩(|0⟩-|1⟩)/√2

Since f(x) = (x[0] AND x[1]) XOR x[2] is balanced:
- f(000)=0, f(001)=1, f(010)=0, f(011)=1
- f(100)=0, f(101)=1, f(110)=1, f(111)=0

After H on q[0], q[1], q[2]:
The Hadamard transform of the phase pattern gives:
H^⊗3 applied to (-1)^{f(x)} pattern

For the balanced function f(x) = (x[0] AND x[1]) XOR x[2]:

The phase pattern is: +,-,+,-,+,-,-,+

The result after H^⊗3 on the first 3 qubits:
The states |0⟩^⊗3 will have zero amplitude (since f is balanced).

The output states in q[0:3] are |001⟩, |011⟩, |101⟩, |111⟩ with equal amplitudes of 1/2 (in magnitude).

With q[3], q[4] in |00⟩:

Final state: 1/2(|00100⟩ + |01100⟩ + |10100⟩ + |11100⟩)

Wait, but these could have phases. Let me recalculate more carefully.

H^⊗3 applied to the oracle state:

Let me define the phase pattern: φ(x) = (-1)^{f(x)}
f(000)=0 → φ=+1
f(001)=1 → φ=-1
f(010)=0 → φ=+1
f(011)=1 → φ=-1
f(100)=0 → φ=+1
f(101)=1 → φ=-1
f(110)=1 → φ=-1
f(111)=0 → φ=+1

So φ = [+1, -1, +1, -1, +1, -1, -1, +1]

H^⊗3 transformation: The amplitude for output |y⟩ is:
(1/√8) Σ_x (-1)^{x·y} φ(x)

For y=000 (i.e., |000⟩):
(1/√8)(+1-1+1-1+1-1-1+1) = (1/√8)(0) = 0 ✓ (balanced function)

For y=001:
(1/√8)(+1·1 + (-1)·(-1) + (+1)·1 + (-1)·(-1) + (+1)·1 + (-1)·(-1) + (-1)·1 + (+1)·1)
= (1/√8)(1+1+1+1+1+1-1+1) = 6/√8

For y=010:
(1/√8)(+1·1 + (-1)·1 + (+1)·(-1) + (-1)·(-1) + (+1)·1 + (-1)·1 + (-1)·(-1) + (+1)·(-1))
= (1/√8)(1-1-1+1

## isqTrain/3013

- task_id: `isqTrain/3013`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `319`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[3];
procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    X(q[0]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Explain the isQ quantum program step-by-step and predict the output probabilities.
    *   Input: A 3-qubit isQ circuit: `H(q[0])`, `CNOT(q[0], q[1])`, `CNOT(q[1], q[2])`, `X(q[0])`.
    *   Format: "## Circuit Analysis" followed by the explanation and predicted probabilities.
    *   Constraints: Concise (3-15 lines), Dirac notation, no code blocks, output ONLY the analysis.

2.  **Analyze the Circuit:**
    *   Initial state: $|q[0]q[1]q[2]\rangle = |000\rangle$.
    *   Gate 1: `H(q[0])` -> State becomes $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes |00\rangle = \frac{1}{\sqrt{2}}(|000\rangle + |100\rangle)$.
    *   Gate 2: `CNOT(q[0], q[1])` -> Control=q[0], Target=q[1]. Flips q[1] when q[0] is 1.
        *   State becomes $\frac{1}{\sqrt{2}}(|000\rangle + |110\rangle)$. This is a Bell-like entangled state (specifically, a GHZ state in the making).
    *   Gate 3: `CNOT(q[1], q[2])` -> Control=q[1], Target=q[2]. Flips q[2] when q[1] is 1.
        *   State becomes $\frac{1}{\sqrt{2}}(|000\rangle + |111\rangle)$. This is the standard 3-qubit GHZ state.
    *   Gate 4: `X(q[0])` -> Applies X gate to q[0]. Flips q[0] (0->1, 1->0).
        *   State becomes $\frac{1}{\sqrt{2}}(|100\rangle + |011\rangle)$.

3.  **Determine Probabilities:**
    *   Final state before measurement: $\frac{1}{\sqrt{2}}(|100\rangle + |011\rangle)$.
    *   Measurement is applied to all qubits: `M(q[0])`, `M(q[1])`, `M(q[2])`.
    *   Probabilities: $P(100) = |1/\sqrt{2}|^2 = 0.5$, $P(011) = |1/\sqrt{2}|^2 = 0.5$.
    *   Note on bit order in isQ: The prompt says "(earlier measured qubit = higher bit)". The measurements are M(q[0]), M(q[1]), M(q[2]).
        *   Wait, standard notation usually puts q[0] as the highest bit or lowest bit? Let's check The implementation expected probabilities: `{'011': 0.5, '100': 0.5}`.
        *   If state is $|100\rangle$ (meaning q[0]=1, q[1]=0, q[2]=0) and measurement string is '100', then q[0] is the highest bit.
        *   Let's map the Dirac notation to the bit strings directly. $|100\rangle \rightarrow$ q[0]=1, q[1]=0, q[2]=0 $\rightarrow$ '100'. Matches perfectly.

4.  **Draft the Explanation:**
    *   Start with `## Circuit Analysis`
    *   Step 1: Initialize to $|000\rangle$. Apply `H` to q[0] to get $\frac{1}{\sqrt{2}}(|000\rangle + |100\rangle)$.
    *   Step 2: Apply `CNOT(q[0], q[1])` to entangle q[0] and q[1], resulting in $\frac{1}{\sqrt{2}}(|000\rangle + |110\rangle)$.
    *   Step 3: Apply `CNOT(q[1], q[2])` to entangle q[1] and q[2], resulting in the GHZ state $\frac{1}{\sqrt{2}}(|000\rangle + |111\rangle)$.
    *   Step 4: Apply `X(q[0])` to flip the first qubit, changing the state to $\frac{1}{\sqrt{2}}(|100\rangle + |011\rangle)$.
    *   Final state & Probabilities: The state

### Reference answer

{'predicted_probs': {'011': 0.5, '100': 0.5}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/1113

- task_id: `isqTrain/1113`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `interference`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1039`

### Prompt

Implement the following in isQ: implements the simon_algorithm pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

The user wants me to generate reasoning for a Simon's algorithm implementation with reversed measurement order.

Let me analyze the circuit:

1. Goal: Implement Simon's algorithm to find the period s = 11 (binary) of a 2-to-1 function
2. Qubits: q[2] (input register, measured), out[2] (output register, not measured)
3. The measurement order is reversed: M(q[1]) first, then M(q[0])

Let me trace the state evolution:

Initial state: |0000⟩ (q[0], q[1], out[0], out[1])

After H(q[0]), H(q[1]):
1/2 (|00⟩ + |01⟩ + |10⟩ + |11⟩) ⊗ |00⟩

Oracle f:
- f(00) = 00
- f(01) = 01
- f(10) = 01
- f(11) = 00

The oracle creates:
1/2 (|00⟩|00⟩ + |01⟩|01⟩ + |10⟩|01⟩ + |11⟩|00⟩)

Since out register is not measured, we can trace it out. The key insight is that the oracle entangles the input and output registers, and due to the symmetry of the function (f(x) = f(x⊕s) where s=11), certain interference patterns emerge.

After applying H on q[0] and q[1] again:

Let me compute more carefully. The state after oracle is:
|ψ⟩ = 1/2 (|00⟩|00⟩ + |01⟩|01⟩ + |10⟩|01⟩ + |11⟩|00⟩)

The input register state (tracing out output) has correlations, but for Simon's algorithm, the key is the interference.

Actually, let me be more careful. The function is:
- f(00) = 00
- f(01) = 01
- f(10) = 01
- f(11) = 00

So f(x) depends on x[0] XOR x[1]:
- x = 00: x[0] XOR x[1] = 0, so f = 00
- x = 01: x[0] XOR x[1] = 1, so f = 01
- x = 10: x[0] XOR x[1] = 1, so f = 01
- x = 11: x[0] XOR x[1] = 0, so f = 00

So f(00) = f(11) = 00 and f(01) = f(10) = 01. This is a 2-to-1 function with period s = 11.

After oracle, the state is:
1/2 (|00⟩|00⟩ + |01⟩|01⟩ + |10⟩|01⟩ + |11⟩|00⟩)

Now applying Hadamard on the input register q:

The Hadamard transform on a basis state |x⟩ gives:
H|0⟩ = (|0⟩ + |1⟩)/√2
H|1⟩ = (|0⟩ - |1⟩)/√2

So H⊗2 |x₁x₂⟩ = 1/2 Σ_y (-1)^(x·y) |y₁y₂⟩

where x·y = x₁y₁ + x₂y₂ mod 2.

The state after H⊗2 on input:
|ψ_final⟩ = 1/2 [1/2 Σ_y (-1)^(00·y) |y⟩|00⟩ + 1/2 Σ_y (-1)^(01·y) |y⟩|01⟩ + 1/2 Σ_y (-1)^(10·y) |y⟩|01⟩ + 1/2 Σ_y (-1)^(11·y) |y⟩|00⟩]

= 1/4 Σ_y [(-1)^(0·y) + (-1)^(11·y)] |y⟩|00⟩ + 1/4 Σ_y [(-1)^(01·y) + (-1)^(10·y)] |y⟩|01⟩

Now, (-1)^(0·y) + (-1)^(11·y):
- y = 00: 1 + 1 = 2
- y = 01: 1 + (-1) = 0
- y = 10: 1 + (-1) = 0
- y = 11: 1 + 1 = 2

And (-1)^(01·y) + (-1)^(10·y):
- y = 00: 1 + 1 = 2
- y =

## isqTrain/2972

- task_id: `isqTrain/2972`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `isq_syntax_multi_register`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2364`

### Prompt

The following isQ code has a bug. Find and fix it.

Buggy code:
```isq
import std;
qbit q[4];
// 1-layer H+CNOT circuit on 4 qubits
procedure main() {
    H(q[0]);
    // H(q[1]); // BUG: missing Hadamard
    H(q[2]);
    H(q[3]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
    CNOT(q[3], q[0]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **Bug**: `H(q[1])` is commented out, leaving q[1] in |0⟩ while q[0], q[2], q[3] are placed in |+⟩. This breaks the intended uniform superposition across all 4 qubits.

2. **Fix**: Uncomment `H(q[1])` so all four qubits receive a Hadamard gate before entanglement.

3. **State evolution (corrected)**:
   - Initial: |0000⟩
   - After H on all 4 qubits: |+⟩⊗⁴ = (1/4)∑_{x∈{0,1}⁴}|x⟩
   - CNOT ring (0→1→2→3→0): Since |+⟩⊗⁴ is a +1 eigenstate of each CNOT's stabilizer (X₁X₀, X₂X₁, X₃X₂, X₀X₃), the uniform superposition is preserved.
   - Measurement yields equal probability 1/16 for all 16 outcomes {|0000⟩…|1111⟩}, matching the expected uniform distribution.

## isqTrain/3975

- task_id: `isqTrain/3975`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `isq_syntax_oracle`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3755`

### Prompt

This isQ program compiles but produces incorrect probabilities. Find and correct the mistake.

```
import std;
// Deutsch-Jozsa for 2-input balanced oracle [0, 1, 1, 0]
oracle f(2, 1) = [0, 1, 1, 0];
qbit q[3];  // 2 input + 1 output

procedure main() {
    // Initialize output qubit to |->
    X(q[2]);
    H(q[2]);
    // Hadamard on input qubits
    H(q[0]); H(q[1]);
    // Apply oracle
    f(q[0], q[1], q[2]);
    // Hadamard on inputs
    // BUG: missing gate here
    // Measure input qubits (non-zero = balanced)
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: The code is missing Hadamard gates on the input qubits after the oracle application. The comment `// BUG: missing gate here` indicates where the gates should be. In the Deutsch-Jozsa algorithm, the input qubits must be transformed back from the Hadamard basis via H gates before measurement.

2. **Fix**: Add `H(q[0]); H(q[1]);` after the oracle call and before measurement. This restores the input qubits to the computational basis, allowing the algorithm to distinguish constant from balanced oracles.

3. **State evolution (corrected)**:
   - After initialization: |00⟩|−⟩
   - After H on inputs: (1/2)(|00⟩+|01⟩+|10⟩+|11⟩)|−⟩
   - After oracle f=[0,1,1,0] (balanced, phase kickback): (1/2)(|00⟩−|01⟩−|10⟩+|11⟩)|−⟩
   - After H on inputs: |11⟩|−⟩
   - Measurement yields |110⟩ or |111⟩ each with prob 0.5 (non-zero on inputs confirms balanced).

## isqTrain/2727

- task_id: `isqTrain/2727`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_procedures`, `measurement_order`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4346`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
qbit q[2];

procedure main(){
    H(q[0]);
    CNOT(q[0],q[1]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations**: The circuit initializes two qubits to |00>, applies a Hadamard gate (H) to q[0], and then applies a CNOT gate with q[0] as the control and q[1] as the target.
2. **State evolution**: Starting from |00>, applying H to q[0] creates the superposition (|00> + |10>)/√2.
3. **Entanglement**: The CNOT gate flips q[1] when q[0] is |1>, resulting in the maximally entangled Bell state (|00> + |11>)/√2.
4. **Probabilities**: The squared amplitudes of this final state are both (1/√2)² = 0.5 for |00> and |11>, while the probabilities for |01> and |10> are 0.

Predicted measurement probabilities: {'00': 0.5, '11': 0.5}

### Reference answer

{'predicted_probs': {'00': 0.5, '11': 0.5}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqExpand/algo/8

- task_id: `isqExpand/algo/8`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `qft`, `phase_rotation`, `fourier_transform`
- source: `isq_expansion`
- dataset_index: `4532`

### Prompt

Implement the following in isQ: implements a simple 2-qubit Quantum Fourier Transform (QFT). Apply QFT to the state |10> (q[0]=1, q[1]=0) and measure.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply 2-qubit QFT to |10>.

QFT circuit for 2 qubits:
1. H(q[0])
2. Controlled-S: ctrl @[q[1]] S(q[0]) — applies S (phase pi/2) to q[0] when q[1]=1
3. H(q[1])

Starting state: |10> (X on q[0])
1. H(q[0]): |10> -> (|0>-|1>)/sqrt(2) ⊗ |0> = (|00>-|10>)/sqrt(2)
2. ctrl @[q[1]] S(q[0]): q[1]=0, so no effect -> (|00>-|10>)/sqrt(2)
3. H(q[1]): (|00>-|10>)/sqrt(2) -> each term splits:
   |00> -> |0>(|0>+|1>)/sqrt(2), |10> -> |1>(|0>+|1>)/sqrt(2)
   Result: (|00>+|01>-|10>-|11>)/2

All 4 outcomes have |amplitude|^2 = 1/4 = 0.25.
Expected: uniform {|00>: 0.25, |01>: 0.25, |10>: 0.25, |11>: 0.25}

## isqQA/quantum_algorithms/134_principle_advantage

- task_id: `isqQA/quantum_algorithms/134_principle_advantage`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `principle_advantage`, `algorithm`, `量子递增/递减电路`
- source: `qa_pipeline`
- dataset_index: `1815`

### Prompt

在量子算法设计中，我们经常需要对寄存器中的数值进行加1操作（即量子递增电路，Quantum Incrementer）。请阐述量子递增电路的宏观工作原理。相比于经典计算机中处理大规模数据集的递增操作，量子递增电路在理论上能够提供什么样的加速？这种量子加速的根本来源是什么？最后，请在回答中包含一段使用 isQ 语言实现的 3 比特量子递增电路代码示例。

### Reference answer

量子递增电路是量子算术运算中的基础组件，主要用于实现状态值加一并取模的操作，即完成变换 $|x\rangle \to |(x+1) \pmod{2^n}\rangle$。

从宏观原理来看，与经典数字电路中的进位加法器类似，量子递增电路需要处理低位向高位的进位。在没有辅助比特的情况下，一种巧妙的实现方式是逆向传播控制信号：从最高位开始，逐级向下判断是否所有低位均为 1。如果所有低位都是 1，则触发当前位的翻转。这种自顶向下的多控门结构（如 Toffoli 门）能够确保在执行低位翻转之前，高位的进位条件已经被正确计算和传递，从而避免了因低位状态过早改变而导致的进位信息丢失。

在时间复杂度与量子加速方面，量子电路展现出颠覆性的优势。在经典计算中，如果我们需要对 $N = 2^n$ 个不同的独立数据分别执行加 1 操作，采用串行处理的时间复杂度为 $O(n \cdot 2^n)$；即便是采用理想的经典并行架构，也需要消耗大量的硬件资源。而在量子计算中，由于 $n$ 个量子比特可以处于包含 $2^n$ 个基态的均匀叠加态上，我们只需将量子递增电路作用于这个处于叠加态的量子寄存器一次，就可以利用酉变换的线性性质，同时完成对这 $2^n$ 个数据的加 1 操作。此时，量子操作的时间复杂度仅为 $O(n)$（即量子线路的深度）。

这种惊人加速的根本来源是“量子并行性”。量子态处于希尔伯特空间中的叠加态，量子门对状态的作用是么正变换，天然地对所有基态分量同时进行演化。因此，单次量子硬件操作即可完成经典计算中需要极大算力支持的批量数据处理任务。

以下是使用 isQ 语言编写的 3 比特量子递增电路代码（低位为 q[0]，高位为 q[2]）：

```isQ
import std;

qbit q[3];

procedure main() {
    // 假设初始状态为叠加态以体现并行性
    for i in 0:3 {
        H(q[i]);
    }

    // 3比特量子递增操作 (+1 模 8)
    // 判断 q[0] 和 q[1] 是否均为 1，若是则最高位 q[2] 翻转
    Toffoli(q[0], q[1], q[2]);
    
    // 判断 q[0] 是否为 1，若是则次高位 q[1] 翻转
    CNOT(q[0], q[1]);
    
    // 最低位 q[0] 无条件翻转
    X(q[0]);

    // 测量观察结果
    for i in 0:3 {
        M(q[i]);
    }
}
```

## isqTrain/4097

- task_id: `isqTrain/4097`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1527`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[3];

procedure main() {

    H(q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    H(q[1]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    H(q[2]);
    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

The circuit has 3 qubits q[0], q[1], q[2].

Initial state: |000>

Let me trace through each gate:

1. H(q[0]): Apply Hadamard to q[0]
   State: (|000> + |100>)/√2

2. ctrl Rz(π/2, q[1], q[0]): Controlled-Rz with q[1] as control, q[0] as target. Wait, let me check the isQ syntax. `ctrl Rz(theta, q[1], q[0])` - I need to understand the syntax. In isQ, `ctrl Rz(theta, control, target)` or `ctrl Rz(theta, target)` with `@[control]`?

Looking at the syntax reference: `ctrl @[c1, c2] Gate(target);`

But the code uses `ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[1], q[0]);`

This seems like the old syntax where `ctrl Rz(theta, control, target)` means control is q[1], and Rz is applied to q[0] when q[1] is |1>.

Wait, let me re-read. `ctrl Rz(theta, q[1], q[0])` - I think in isQ, the first qubit argument after theta is the control, and the second is the target. So q[1] is the control and q[0] is the target for Rz.

Actually, looking more carefully at isQ syntax, `ctrl Rz(theta, q[1], q[0])` might mean: control q[1], apply Rz(theta) to q[0] when q[1]=|1>.

Let me trace through:

1. H(q[0]): |000> → (|000> + |100>)/√2

2. ctrl Rz(π/2, q[1], q[0]): When q[1]=|1>, apply Rz(π/2) to q[0].
   - |000> component: q[1]=0, no action → |000>
   - |100> component: q[1]=0, no action → |100>
   State: (|000> + |100>)/√2 (unchanged since q[1]=0 in both terms)

3. ctrl Rz(π/4, q[2], q[0]): When q[2]=|1>, apply Rz(π/4) to q[0].
   - Both components have q[2]=0, so no change.
   State: (|000> + |100>)/√2

4. H(q[1]): Apply Hadamard to q[1]
   State: (|000> + |010> + |100> + |110>)/2

5. ctrl Rz(π/2, q[2], q[1]): When q[2]=|1>, apply Rz(π/2) to q[1].
   - |000>: q[2]=0, no change → |000>
   - |010>: q[2]=0, no change → |010>
   - |100>: q[2]=0, no change → |100>
   - |110>: q[2]=1, apply Rz(π/2) to q[1]. q[1] is in |1>, so Rz(π/2)|1> = e^{-iπ/4}|1>
   So |110> → e^{-iπ/4}|110>
   State: (|000> + |010> + |100> + e^{-iπ/4}|110>)/2

6. H(q[2]): Apply Hadamard to q[2]
   |000> → (|000> + |001>)/√2
   |010> → (|010> + |011>)/√2
   |100> → (|100> + |101>)/√2
   |110> → (|110> + |111>)/√2
   State: (|000> + |001> + |010> + |011> + |100> + |101> + e^{-iπ/4}(|110> + |111>))/2√2

7-9. CNOT(q[0], q[2]); CNOT(q[2], q[0]); CNOT(q[0], q[2]): This is a swap (three-CNOT decomposition) between q[0] and q[2].

Wait, actually three CNOTs with alternating control/target is a swap (three-CNOT decomposition). Let me verify:
- CNOT(q[0],

### Reference answer

Uniform distribution across 8 states
