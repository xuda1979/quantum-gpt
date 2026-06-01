# ISQ training COT RAG corpus: state_preparation shard 13

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3875

- task_id: `isqTrain/3875`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `521`

### Prompt

Help me write isQ code that Prepare a 2-qubit uniform superposition using ket sum assignment. Sum all computational basis states. Measure all.

### Chain-of-thought reasoning

## Reasoning
The goal is to prepare a 2-qubit uniform superposition using a direct ket sum assignment and measure the resulting state.
Two global qubits `q[0]` and `q[1]` are utilized, and both are measured at the end of the circuit.
The ket sum `q = |0> + |1> + |2> + |3>` directly initializes the system to the normalized state `|ψ> = (|00> + |01> + |10> + |11>) / 2`.
Because all four basis states have identical probability amplitudes of 1/2, measuring the qubits yields an equal probability of 0.25 for each outcome: |00>, |01>, |10>, and |11>.

## isqTrain/3736

- task_id: `isqTrain/3736`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4405`

### Prompt

Code this in isQ: Prepare the 5-qubit GHZ state with phase pi/4:
|GHZ> = (|00000> + e^{i*pi/4}|11111>) / sqrt(2)
Use Hadamard on first qubit, Rz for phase, then CNOT chain. Measure all 5 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare a 5-qubit phase-shifted GHZ state, $(|00000\rangle + e^{i\pi/4}|11111\rangle) / \sqrt{2}$, and measure all qubits.
2. **Initialization & Phase**: Starting from $|00000\rangle$, applying an H gate to `q[0]` creates $(|00000\rangle + |10000\rangle)/\sqrt{2}$. Applying `Rz(pi/4)` to `q[0]` imparts the relative phase, evolving the state to $(|00000\rangle + e^{i\pi/4}|10000\rangle) / \sqrt{2}$.
3. **Entanglement**: A sequential chain of CNOT gates (using `q[0]` through `q[4]` as control and target) copies the computational basis state of `q[

## isqTrain/3182

- task_id: `isqTrain/3182`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `941`

### Prompt

Create an isQ quantum circuit that an isQ program: apply Ry(1*pi/7) to one qubit, then CNOT to a second qubit, creating partial entanglement.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a partially entangled 2-qubit state by applying an $R_y$ rotation followed by a CNOT gate.
2. **Qubits**: Requires 2 qubits (`q[0]`, `q[1]`), both of which are measured at the end of the circuit.
3. **State Evolution**: 
   - Initialize to $|00\rangle$.
   - Apply $R_y(\pi/7)$ to `q[0]`: evolves to $\cos(\pi/14)|00\rangle + \sin(\pi/14)|10\rangle$.
   - Apply CNOT(`q[0]`, `q[1]`): entangles the qubits, resulting in $\cos(\pi/14)|00\rangle + \sin(\pi/14)|11\rangle$.
4. **Probabilities**: Measuring this state yields $P(|00\rangle) = \cos^2(\pi/14) \approx 0.9505$ and $P(|11\rangle) = \sin^2(\pi/14) \approx 0.0495$, matching the predicted output.

## isqTrain/4789

- task_id: `isqTrain/4789`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `superposition`, `isq_syntax_while_loop`, `isq_syntax_if_else`
- source: `isq_train_cot`
- dataset_index: `5474`

### Prompt

Write isQ code for the following quantum task: implements: while-loop with classical vars variant 5. Declare a global qbit array q of 2 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Use a while-loop to apply H twice per iteration (which is identity), then apply a single final H to q[0].
2. **Qubits**: 2 qubits (q[0], q[1]), both measured.
3. **State evolution**:
   - Start: |00⟩
   - While-loop body: H(q[0]) twice → H·H = I, so 6 iterations leave |00⟩ unchanged
   - Final H(q[0]): |00⟩ → (|00⟩ + |10⟩)/√2
   - q[1] is never touched, stays |0⟩
4. **Probabilities**: |00⟩ and |10⟩ each have amplitude 1/√2, giving P(|00⟩) = 0.5 and P(|10⟩) = 0.5.

## isqTrain/416

- task_id: `isqTrain/416`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `1646`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;

qbit q[2];

procedure main() {
    // |Ψ+> = (|01> + |10>)/sqrt(2)
    H(q[0]);
    X(q[1]);
    CNOT(q[0], q[1]);
    
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initial State**: The circuit starts with 2 qubits in the state |00>.
2. **Gate Operations**:
   - `H(q[0])`: Applies a Hadamard gate to q[0], evolving the state to `(|00> + |10>) / sqrt(2)`.
   - `X(q[1])`: Applies an X gate to q[1], flipping its state. The system evolves to `(|01> + |11>) / sqrt(2)`.
   - `CNOT(q[0], q[1])`: Applies a controlled-NOT gate with q[0] as the control and q[1] as the target. The state |01> remains unchanged (control is |0>), while |11> becomes |10> (control is |1>). The state evolves to the Bell state `(|01> + |10>) / sqrt(2)`.
3. **Final State**: The quantum state right before measurement is `(|01> + |10>) / sqrt(2)`.
4. **Measurement**: Measuring both qubits yields either |01> or |10>, each with an amplitude magnitude squared of `(1/sqrt(2))^2 = 0.5`.

Predicted probability distribution: {|01>: 0.5, |10>: 0.5}

### Reference answer

{'predicted_probs': {'1': 0.5, '2': 0.5}, 'explanation': 'Parametric variant of isqHumanEval/122. Dimension: predict probabilities for reference circuit.'}

## isqTrain/4214

- task_id: `isqTrain/4214`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `562`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[3];

procedure main() {
    Ry(2.0 * 0.9553166, q[0]);
    nctrl Ry(3.14159265358979 / 2.0, q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

Let me analyze this isQ circuit step by step.

The circuit has 3 qubits: q[0], q[1], q[2]

Initial state: |000>

Step 1: `Ry(2.0 * 0.9553166, q[0])`
This applies Ry(2 * 0.9553166) ≈ Ry(1.9106332) to q[0].

Ry(θ) rotates around Y-axis:
Ry(θ) = [[cos(θ/2), -sin(θ/2)], [sin(θ/2), cos(θ/2)]]

So Ry(2 * 0.9553166) has θ/2 = 0.9553166
cos(0.9553166) ≈ cos(0.9553) ≈ 0.5774 ≈ 1/√3
sin(0.9553166) ≈ sin(0.9553) ≈ 0.8165 ≈ √(2/3)

Wait, let me recalculate. 
0.9553166 radians...
cos(0.9553) ≈ 0.5774
sin(0.9553) ≈ 0.8165

So q[0] becomes cos(0.9553)|0> + sin(0.9553)|1> ≈ 0.5774|0> + 0.8165|1>

Actually, wait. Let me check if 0.9553166 ≈ arccos(1/√3) or something similar.

arccos(1/√3) = arccos(0.5774) ≈ 0.9553 radians. Yes!

So cos(0.9553166) ≈ 1/√3 and sin(0.9553166) ≈ √(2/3)

State after step 1: (1/√3)|0> + √(2/3)|1> ⊗ |00>
= (1/√3)|000> + √(2/3)|100>

Step 2: `nctrl Ry(3.14159265358979 / 2.0, q[0], q[1])`

Wait, what does `nctrl` mean in isQ? 

Looking at the syntax reference, it says:
- Control modifier: `ctrl @[c1, c2] Gate(target);`

But `nctrl` is used here. In isQ, `nctrl` likely means "negated control" - i.e., the gate is applied when the control qubit is in state |0>, not |1>.

So `nctrl Ry(π/2, q[0], q[1])` means: if q[0] is |0>, apply Ry(π/2) to q[1].

Ry(π/2) applied to |0> gives (|0> + |1>)/√2 = |+>

State after step 2:
When q[0] = |0>: Ry(π/2) is applied to q[1], turning |0> into (|0>+|1>)/√2
When q[0] = |1>: nothing happens to q[1]

So state becomes:
(1/√3) × (1/√2)(|000> + |010>) + √(2/3)|100>
= (1/√6)|000> + (1/√6)|010> + √(2/3)|100>

Step 3: `CNOT(q[1], q[2])`
This flips q[2] when q[1] = |1>

State after step 3:
(1/√6)|000> + (1/√6)|011> + √(2/3)|100>

Step 4: `CNOT(q[0], q[1])`
This flips q[1] when q[0] = |1>

State after step 4:
(1/√6)|000> + (1/√6)|011> + √(2/3)|110>

Step 5: `CNOT(q[0], q[2])`
This flips q[2] when q[0] = |1>

State after step 5:
(1/√6)|000> + (1/√6)|011> + √(2/3)|111>

Step 6: `CNOT(q[2], q[0])`
This flips q[0] when q[2] =

### Reference answer

Dominant output states: |011> with probability ~0.67 each

## isqTrain/1325

- task_id: `isqTrain/1325`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `590`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[3];

procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes three qubits to |000> and applies a Hadamard gate to q[0] followed by a CNOT with q[0] as control and q[1] as target.
2. The Hadamard gate puts q[0] into an equal superposition: 1/sqrt(2)(|0> + |1>) |00> = 1/sqrt(2)(|000> + |100>).
3. The CNOT gate entangles q[0] and q[1], flipping q[1] to |1> only when q[0] is |1>, yielding the final state: 1/sqrt(2)(|000> + |110>).
4. Because q[2] is never manipulated, it remains in the |0> state. Measuring the system will cause it to collapse into one of the two entangled basis states with equal probability.

Predicted probability distribution: {|000>: 0.5, |110>: 0.5}

### Reference answer

{'predicted_probs': {'0': 0.5, '6': 0.5}, 'explanation': 'Parametric variant of isqEval/477. Dimension: qubit_variant: q[2] -> q[3].'}

## isqTrain/1363

- task_id: `isqTrain/1363`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1643`

### Prompt

Code this in isQ: Prepare a GHZ state on 3 qubits, then apply a Z gate to the first qubit to create a relative phase. Measure all qubits.

### Chain-of-thought reasoning

## Reasoning
**Goal**: Create a 3-qubit GHZ state, apply a Z gate to introduce a relative phase, and measure all qubits.
**Qubits**: 3 qubits (q[0], q[1], q[2]), all measured.

**State evolution**:
1. Initial state: |000⟩
2. H(q[0]): (|0⟩ + |1⟩)/√2 ⊗ |00⟩ = (|000⟩ + |100⟩)/√2
3. CNOT(q[0], q[1]): (|000⟩ + |110⟩)/√2
4. CNOT(q[0], q[2]): (|000⟩ + |111⟩)/√2 — standard GHZ state
5. Z(q[0]): Z|0⟩ = |0⟩, Z|1⟩ = -|1⟩ → (|000⟩ - |111⟩)/√2

**Expected probabilities**: The final state is an equal superposition of |000⟩ and |111⟩ with a relative phase. Since measurement probabilities depend on squared amplitudes, the phase doesn't affect outcomes: P(|000⟩) = 0.5, P(|111⟩) = 0.5.

## isqTrain/4811

- task_id: `isqTrain/4811`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_switch`, `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2512`

### Prompt

帮我写一个isQ程序：selects a Bell state via switch. Declare 2 global qubits and an integer variable sel=0. Use switch(sel): case 0 creates |Phi+> (H then CNOT), case 1 creates |Phi-> (X, H, CNOT), case 2 creates |Psi+> (H, CNOT, X on q[1]). Since sel=0, create |Phi+> = (|00>+|11>)/sqrt(2). Note: fall-through means cases 1 and 2 also execute after case 0. To get just case 0, place it as the last case. Actually, use sel=2 so only case 2 runs (last case, no fall-through). Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Create the Bell state |Psi+> = (|01>+|10>)/√2 using switch with sel=2.
2. Two global qubits q[2]; both are measured.
3. State evolution (case 2 only):
   - |00> → H(q[0]) → (|00>+|10>)/√2
   - → CNOT(q[0],q[1]) → (|00>+|11>)/√2
   - → X(q[1]) → (|01>+|10>)/√2
4. Measurement yields |01> or |10> with equal probability 0.5 each, matching expected {|01>: 0.5, |10>: 0.5}.

## isqTrain/4855

- task_id: `isqTrain/4855`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `measurement_order`, `entanglement`
- source: `isq_train_cot`
- dataset_index: `1299`

### Prompt

Write isQ code for the following quantum task: measuring only q[0] of a Bell pair. Leave q[1] unmeasured.

### Chain-of-thought reasoning

## Reasoning
Goal: Create a Bell state and measure only q[0], leaving q[1] unmeasured.

Two qubits needed: q[0] (measured), q[1] (not measured).

State evolution:
1. Initialize: |00⟩
2. H(q[0]): (|0⟩ + |1⟩)/√2 ⊗ |0⟩ = (|00⟩ + |10⟩)/√2
3. CNOT(q[0], q[1]): (|00⟩ + |11⟩)/√2 (Bell state |Φ+⟩)

Measurement of q[0]: The reduced density matrix of q[0] gives equal probability for |0⟩ and |1⟩ since both terms in the superposition have equal amplitude. Expected: {|0⟩: 0.5, |1⟩: 0.5}.
