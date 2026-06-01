# ISQ training COT RAG corpus: quantum_algorithms shard 67

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/2992

- task_id: `isqTrain/2992`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `measurement_order`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4590`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;
qbit q[2];
procedure main() {
    X(q[0]);
    X(q[1]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[0]);
    CNOT(q[0], q[1]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. Initial state is |00>.
2. X gates on both qubits flips them to |11>.
3. CNOT(q[0], q[1]) flips q[1] since q[0] is |1>, changing state to |10>.
4. CNOT(q[1], q[0]) does nothing since q[1] is |0>, state remains |10>.
5. CNOT(q[0], q[1]) flips q[1] back to |1> since q[0] is |1>, resulting in |11>.
6. Final state before measurement is |11>.

Predicted measurement probabilities:
[0.0, 0.0, 0.0, 1.0]

### Reference answer

{'predicted_probs': {'11': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/4074

- task_id: `isqTrain/4074`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_deriving_gate`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `689`

### Prompt

I'm getting wrong output from this isQ code. What's the bug and how do I fix it?

```
import std;
// Swap test: compare |1> vs |+>
// q[0] = ancilla, q[1] = state A, q[2] = state B
qbit q[3];

// Controlled-SWAP (Fredkin gate)
unit cswap(qbit q[3]) {
    CNOT(q[2], q[1]);
    Toffoli(q[0], q[1], q[2]);
    CNOS(q[2], q[1]);
} deriving gate

procedure main() {
    // Prepare state A on q[1]
    X(q[1]);
    // Prepare state B on q[2]
    H(q[2]);
    // Swap test circuit
    H(q[0]);
    cswap(q);
    H(q[0]);
    // Measure ancilla and state qubits
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

Let me analyze the bug in this isQ code.

The buggy code has a typo in the `cswap` function:

This should be:

The bug is on the third line of the `cswap` function. "CNOS" is not a valid gate - it's a typo for "CNOT". The Controlled-swap (three-CNOT decomposition) (controlled-swap operation (three-CNOT decomposition)) decomposition uses three CNOT gates and one Toffoli gate. The standard decomposition is:
1. CNOT(q[2], q[1])
2. Toffoli(q[0], q[1], q[2])
3. CNOT(q[2], q[1])

The typo "CNOS" instead of "CNOT" on line 3 breaks the circuit.

Now let me verify the state evolution of the corrected circuit:

Initial state: |000⟩

After X(q[1]): |010⟩

After H(q[2]): |01+⟩ = |01⟩(|0⟩+|1⟩)/√2 = (|010⟩+|011⟩)/√2

After H(q[0]): |+1+⟩ = (|010⟩+|011⟩+|110⟩+|111⟩)/2

Now applying Cswap (three-CNOT decomposition) (controlled by q[0]):
- When q[0]=0: no swap
- When q[0]=1: swap q[1] and q[2]

When q[0]=1:
- |110⟩ → swap q[1]=1, q[2]=0 → |101⟩
- |111⟩ → swap q[1]=1, q[2]=1 → |111⟩

So after Cswap (three-CNOT decomposition): (|010⟩+|011⟩+|101⟩+|111⟩)/2

After H(q[0]):
(|010⟩+|011⟩+|101⟩+|111⟩ + |010⟩+|011⟩-|101⟩-|111⟩)/2√2
= (2|010⟩+2|011⟩)/2√2
= (|010⟩+|011⟩)/√2

Wait, that doesn't match the predicted output which has 5 different basis states.

Let me redo this more carefully.

State after preparation:
q[0]=|0⟩, q[1]=|1⟩, q[2]=|+⟩

|ψ⟩ = |0⟩₁|1⟩₂|+⟩₃ = |0⟩(|0⟩+|1⟩)/√2 for qubits (q[0], q[1], q[2])

In computational basis (q[0]q[1]q[2]):
|ψ⟩ = (|010⟩ + |011⟩)/√2

After H(q[0]):
|ψ⟩ = (|010⟩ + |011⟩ + |110⟩ + |011⟩)/(√2·√2) 

Wait, let me be more careful.

H on q[0]: |0⟩ → |+⟩ = (|0⟩+|1⟩)/√2

|ψ⟩ = (|0⟩+|1⟩)/√2 ⊗ |1⟩ ⊗ (|0⟩+|1⟩)/√2

= (|0⟩+|1⟩)/√2 ⊗ (|10⟩+|11⟩)/√2

= (|010⟩+|011⟩+|110⟩+|111⟩)/2

Now Cswap (three-CNOT decomposition) (controlled by q[0], swaps q[1] and q[2]):
- |010⟩ → q[0]=0, no swap → |010⟩
- |011⟩ → q[0]=0, no swap → |011⟩
- |110⟩ → q[0]=1, swap q[1]=1,q[2]=0 → |101⟩
- |111⟩ → q[0]=1, swap q[1]=1,q[2]=1 → |111⟩

After Cswap (three-CNOT decomposition): (|010⟩+|011⟩+|101⟩+|111⟩)/2

After H(q[0]):
|010⟩ → (|010⟩+|110⟩)/√2
|011⟩ → (|011⟩+|111⟩)/√2
|101⟩ → (|101⟩-|001⟩)/√2  

Wait, H|1⟩ = (|0⟩-|1⟩)/√2 = |-⟩

|101⟩ → (|101⟩-|001⟩)/√2
|111⟩ → (|111⟩-|011⟩)/√2

So:
|ψ⟩ = 1/2 * [(|010⟩+|110⟩)/

## isqExpand/algo/196

- task_id: `isqExpand/algo/196`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `bernstein_vazirani`, `oracle`, `hadamard_transform`, `hidden_string`
- source: `isq_expansion`
- dataset_index: `3897`

### Prompt

请用isQ语言编写一个量子电路：implementing the Bernstein-Vazirani algorithm to find the hidden string s=11 (2-bit string). Use 3 qubits: 2 for the input register and 1 for the output qubit. The oracle computes f(x) = s·x mod 2. Apply X to the output qubit, Hadamard on all qubits, then the oracle (CNOT from each input qubit where s_i=1 to the output), then Hadamard on the input qubits, and measure the input qubits. The result should deterministically yield s=11.

### Chain-of-thought reasoning

The Bernstein-Vazirani algorithm finds a hidden string s by querying an oracle f(x) = s·x mod 2. For s=11 (binary), we need 2 input qubits (q[0], q[1]) and 1 output qubit (q[2]). Step 1: Initialize the output qubit to |1> using X(q[2]). Step 2: Apply H to all 3 qubits, putting the input register in equal superposition and the output in |->. Step 3: Apply the oracle — since s=11, both s0=1 and s1=1, so we apply CNOT(q[0],q[2]) and CNOT(q[1],q[2]). This encodes f(x) into the phase. Step 4: Apply H to the input qubits. The Hadamard transform converts the phase-encoded string into a computational basis state. Step 5: Measure q[0] and q[1]. The BV algorithm guarantees the measurement yields s=11 with probability 1. The expected probabilities for 2 measured qubits are: |00>=0, |01>=0, |10>=0, |11>=1.0.

## isqTrain/549

- task_id: `isqTrain/549`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `entanglement`, `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_if_else`, `isq_syntax_multi_register`, `isq_syntax_print`, `mid_circuit_measurement`
- source: `isq_train_cot`
- dataset_index: `4902`

### Prompt

Create an isQ quantum circuit that implements a compact variant of the bell_state_preparation pattern using pool[3] -> pool[2]. The circuit should use a reduced qubit register.

### Chain-of-thought reasoning

Looking at this task, I need to understand what the circuit does and trace through the quantum state evolution.

The circuit uses:
- `pool[2]` - declared but not used in main logic
- `q[3]` - 3 qubits used in the circuit
- Classical bits `m1, m2` for measurement results

Let me trace through the circuit:

1. Initial state: |000⟩ (for q[0], q[1], q[2])

2. `X(q[0])`: |100⟩

3. `H(q[1])`: q[1] goes into superposition
   |1⟩ ⊗ |+⟩ ⊗ |0⟩ = |1+0⟩
   = (1/√2)(|100⟩ + |110⟩)

4. `CNOT(q[1], q[2])`: Control q[1], target q[2]
   - |100⟩ → |100⟩ (control is 0)
   - |110⟩ → |111⟩ (control is 1, flip target)
   Result: (1/√2)(|100⟩ + |111⟩)

5. `CNOT(q[0], q[1])`: Control q[0], target q[1]
   - |100⟩ → |110⟩ (control is 1, flip target)
   - |111⟩ → |101⟩ (control is 1, flip target)
   Result: (1/√2)(|110⟩ + |101⟩)

6. `H(q[0])`: Apply H to q[0]
   - |110⟩ = |1⟩|1⟩|0⟩ → (1/√2)(|0⟩ - |1⟩)|1⟩|0⟩ = (1/√2)(|010⟩ - |110⟩)
   - |101⟩ = |1⟩|0⟩|1⟩ → (1/√2)(|0⟩ - |1⟩)|0⟩|1⟩ = (1/√2)(|001⟩ - |101⟩)
   
   Result: (1/√2)[(1/√2)(|010⟩ - |110⟩) + (1/√2)(|001⟩ - |101⟩)]
   = (1/2)(|010⟩ - |110⟩ + |001⟩ - |101⟩)
   = (1/2)(|001⟩ + |010⟩ - |101⟩ - |110⟩)

Wait, let me recalculate this more carefully.

State after step 5: (1/√2)(|110⟩ + |101⟩)

This is |1⟩₁ ⊗ (1/√2)(|10⟩ + |01⟩)₂₃ for qubits q[0], q[1], q[2]

Hmm, wait let me be more careful. The ordering is q[0], q[1], q[2].

After step 5: (1/√2)(|110⟩ + |101⟩)

Apply H(q[0]):
H|0⟩ = |+⟩ = (1/√2)(|0⟩ + |1⟩)
H|1⟩ = |−⟩ = (1/√2)(|0⟩ - |1⟩)

So:
|110⟩ → H on first qubit: (1/√2)(|0⟩ - |1⟩)|10⟩ = (1/√2)(|010⟩ - |110⟩)
|101⟩ → H on first qubit: (1/√2)(|0⟩ - |1⟩)|01⟩ = (1/√2)(|001⟩ - |101⟩)

Total: (1/√2)[(1/√2)(|010⟩ - |110⟩) + (1/√2)(|001⟩ - |101⟩)]
= (1/2)(|010⟩ - |110⟩ + |001⟩ - |101⟩)
= (1/2)(|001⟩ + |010⟩ - |101⟩ - |110⟩)

7. `m1 = M(q[0])`: Measure q[0]
   - If m1 = 0: state collapses to (1/√2)(|001⟩ + |010⟩), probability 1/2
   - If m1 = 1: state collapses to -(1/√2)(|101⟩ + |110⟩), probability 1/2

8. `m2 = M(q[1])`: Measure q[1]
   - For m1=0 branch:
     - If m2 = 0: |001⟩, probability 1/4
     - If m2 = 1: |010⟩, probability 1/4
   - For m1=1 branch:
     - If m2 = 0: |101⟩, probability 1/4

## isqTrain/1107

- task_id: `isqTrain/1107`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `interference`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1113`

### Prompt

Write isQ code for the following quantum task: implements a variant of the simon_algorithm pattern using out[2] -> out[3]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning

**Goal**: Implement Simon's algorithm with period s=11 using a 2-qubit input register and expanded 3-qubit output register.

**Qubits**: 2 input qubits q[0],q[1] (measured) + 3 output qubits out[0..2] (ancillary). Only q[0],q[1] are measured.

**State evolution**:
1. Initialize: |00⟩|000⟩
2. H⊗2 on input: (|00⟩+|01⟩+|10⟩+|11⟩)/2 ⊗ |000⟩
3

## isqTrain/3542

- task_id: `isqTrain/3542`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `entanglement`, `ancilla_usage`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `4067`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```
import std;

qbit q[3];

procedure main() {
    X(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initial state**: The 3-qubit system starts in the ground state |000⟩.
2. **X(q[0])**: Flips the first qubit, evolving the state to |100⟩.
3. **CNOT(q[0], q[1])**: Since the control q[0] is |1⟩, the target q[1] is flipped, resulting in the state |110⟩.
4. **CNOT(q[0], q[2])**: Since the control q[0] is |1

### Reference answer

{'predicted_probs': {'111': 1.0}, 'explanation': 'The output is |111> with probability 1.0'}

## isqTrain/2676

- task_id: `isqTrain/2676`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_procedures`, `measurement_order`
- source: `isq_train_cot`
- dataset_index: `4307`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
qbit q[4];
procedure main() {
    H (q[0]);
    for i in 1:4 {

        CNOT (q[i-1], q[i]);
    }
    for i in 0:4{
        M(q[i]);
    }
}
```

### Chain-of-thought reasoning

1.  **Analyze the isQ program:**
    *   `qbit q[4];`: Array of 4 qubits, indexed 0 to 3. Wait, the array is size 4, so valid indices are 0, 1, 2, 3.
    *   Let's check the loop: `for i in 1:4 { CNOT(q[i-1], q[i]); }`
        *   If `i` goes from 1 to 3 (if 4 is exclusive), or 1 to 4 (inclusive).
        *   Wait! If it's `1:4` and 4 is inclusive, `q[4]` is out of bounds for `qbit q[4]`.
        *   Looking closely at the prompt: `qbit q[4];` and `for i in 1:4 { CNOT(q[i-1], q[i]); }`
        *   If the array is size 4, the indices are 0, 1, 2, 3.
        *   Wait, The predicted output `{'0000': 0.5, '1111': 0.5}`. This implies 4 qubits.
        *   If it's 4 qubits, the loop must not access `q[4]`. Thus, `for i in 1:4` means `i = 1, 2, 3`.
        *   Let me re-read typical isQ syntax or Python-like syntax. `for i in 1:4` usually means 1, 2, 3. Wait, or maybe `qbit q[5]` was intended but written as `q[4]` in the prompt?
        *   Let's check the prompt's array declaration: `qbit q[4];` -> 4 qubits.
        *   Loop `for i in 1:4`. In python, `1:4` is 1, 2, 3.
        *   CNOTs applied:
            *   i=1: CNOT(q[0], q[1])
            *   i=2: CNOT(q[1], q[2])
            *   i=3: CNOT(q[2], q[3])
        *   This creates an entangled state across 4 qubits: GHZ state.
        *   Initial state: |0000>
        *   H(q[0]): (|0> + |1>)|000> = |0000> + |1000> (unnormalized)
        *   CNOT(q[0], q[1]): |0000> + |1100>
        *   CNOT(q[1], q[2]): |0000> + |1110>
        *   CNOT(q[2], q[3]): |0000> + |1111>
        *   Normalized: (|0000> + |1111>) / sqrt(2)
        *   This exactly matches the expected `{'0000': 0.5, '1111': 0.5}`.

2.  **Draft the step-by-step reasoning:**
    *   **Initialization**: 4 qubits `q[0..3]` initialized to |0000>.
    *   **Hadamard**: `H(q[0])` creates an equal superposition on q[0], yielding (|0000> + |1000>)/√2.
    *   **Entanglement (CNOTs)**: The loop `for i in 1:4` (iterating 1, 2, 3) applies CNOTs with control `q[i-1]` and target `q[i]`.
        *   i=1: CNOT(q[0], q[1]) -> (|0000> + |1100>)/√2
        *   i=2: CNOT(q[1], q[2]) -> (|0000> + |1110>)/√2
        *   i=3: CNOT(q[2], q[3]) -> (|0000> + |1111>)/√2
    *   **Measurement**: The final state is the 4-qubit GHZ state (|0000> + |1111>)/√2. Measurement probabilities are 0.5 for |0000> and 0.5 for |1111>.

3.  **Format the output:**
    *   Start with "## Circuit Analysis"
    *   List operations
    *   Step-by-step evolution using Dirac notation
    *   Final state and probabilities
    *   No code blocks, concise lines.

4.  **Refine constraints:**
    *   "3-8 lines for simple circuits, up to

### Reference answer

{'predicted_probs': {'0000': 0.5, '1111': 0.5}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/962

- task_id: `isqTrain/962`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `hamiltonian_simulation`, `isq_syntax_ctrl_nctrl`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2121`

### Prompt

Implement the following in isQ: implements the pauli_evolution pattern but with a different initial state preparation (flip q[[1]] -> q[0]).

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement $e^{-i\theta ZZ}$ evolution with $\theta = \pi/4$ on the initial state $|10\rangle$.

2. **Qubits**: 2 qubits (`q[0]`, `q[1]`), both measured.

3. **State evolution**:
   - Start: $|00\rangle$
   - `X(q[0])`: $|10\rangle$ (prepare the flipped initial state)
   - `CNOT(q[0], q[1])`: $|10\rangle \to |11\rangle$ (computes parity into q[1])
   - `Rz(\pi/2, q[1])`: $|11\rangle \to e^{i\pi/4}|11\rangle$ (applies phase rotation)
   - `CNOT(q[0], q[1])`: $e^{i\pi/4}|11\rangle \to e^{i\pi/4}|10\rangle$ (undoes parity)

4. **Expected probabilities**: $|10\rangle$ is a $ZZ$ eigen

## isqTrain/139

- task_id: `isqTrain/139`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `1512`

### Prompt

Create an isQ quantum circuit that implements the gate_decomposition pattern with modified rotation parameters (pi3_to_pi6). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a two-qubit circuit with Ry rotations (π/6 and π/4) followed by CNOT entanglement and measurement.
2. **Qubits**: 2 qubits (q[0], q[1]), both measured.
3. **State evolution**:
   - Initial: |00⟩
   - After Ry(π/6, q[0]): cos(π/12)|0⟩ + sin(π/12)|1⟩ on q[0], state = cos(π/12)|00⟩ + sin(π/12)|10⟩
   - After Ry(π/4, q[1]): cos(π/12)cos(π/8)|00⟩ + cos(π/12)sin(π/8)|01⟩ + sin(π/12)cos(π/8)|10⟩ + sin(π/12)sin(π/

## isqTrain/3444

- task_id: `isqTrain/3444`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `hamiltonian_simulation`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `1009`

### Prompt

实现以下量子计算任务（使用isQ）：single-layer QAOA for MaxCut on a 4-node path graph (edges: 0-1, 1-2, 2-3) in isQ.

Use gamma=0.6, beta=0.3.
Declare 4 qubits, measure all.

### Chain-of-thought reasoning

## Reasoning

**Goal**: Single-layer QAOA for MaxCut on a 4-node path graph (edges 0-1, 1-2, 2-3) with γ=0.6, β=0.3.

**Qubits**: 4 qubits declared globally, all measured.

**State evolution**:
1. Initial state: |0000⟩
2. H⊗⁴: Creates uniform superposition |ψ⟩ = (1/4)Σ|x⟩ over all 16 basis states
3. Problem unitary applies ZZ(γ=0.6) on each edge via CNOT-Rz-CNOT: each basis state |x₀x₁x₂x₃⟩ ac
