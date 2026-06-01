# ISQ training COT RAG corpus: state_preparation shard 31

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1441

- task_id: `isqTrain/1441`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `2367`

### Prompt

I need an isQ program to Prepare the computational basis state |010> on 3 qubits by applying X gates to the appropriate qubits, then measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare the 3-qubit computational basis state |010> by selectively flipping qubits initialized to |0>, then measure all.
2. **Qubits**: 3 qubits are required, and all 3 are measured.
3. **State evolution**:
   - Start in the ground state |000>.
   - Apply an X gate to `q[1]` to flip it, evolving the state to |010>.
4. **Measurement probabilities**: The circuit deterministically prepares the pure state |010>, so measuring all qubits yields the bitstring '010' with a probability of 1.0.

## isqTrain/4805

- task_id: `isqTrain/4805`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_switch`, `isq_syntax_classical_vars`, `mid_circuit_measurement`
- source: `isq_train_cot`
- dataset_index: `3940`

### Prompt

Write isQ code for the following quantum task: uses switch-case for error correction. Declare 3 global qubits. Set q[0] to |1>, set q[1] to |1>. Measure q[0] into variable s. Use switch(s): case 0 applies nothing (identity), case 1 applies X(q[2]) to flip q[2]. Since q[0]=|1>, case 1 executes. Measure all qubits. Expected: |111>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Demonstrate switch-case conditional error correction using a measured syndrome qubit to apply a correction gate.
2. **Qubits**: 3 global qubits (q[0], q[1], q[2]); all three are measured.
3. **State evolution**:
   - Initialize: |000⟩
   - X(q[0]): |100⟩
   - X(q[1]): |110⟩
   - Measure q[0] → s=1 (deterministic since q[0] is |1⟩)
   - Switch case 1 executes: X(q[2])
   - After X(q[2]): |111⟩
4. **Expected result**: Final state is |111⟩, so measurement yields |111⟩ with probability 1.0. The switch-case correctly routes to case 1 based on the classical measurement outcome.

## isqTrain/3739

- task_id: `isqTrain/3739`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `296`

### Prompt

Create an isQ quantum circuit that Prepare the 3-qubit W-state: (|001> + |010> + |100>) / sqrt(3).
Use Ry rotations and CNOT gates to distribute amplitude equally among the three single-excitation basis states. Measure all 3 qubits.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for the W-state preparation circuit. Let me analyze the circuit step by step.

The goal is to prepare the 3-qubit W-state: (|001⟩ + |010⟩ + |100⟩)/√3

Let me trace through the circuit:

1. Initial state: |000⟩

2. Ry(2*arccos(1/√3), q[0]):
   - arccos(1/√3) ≈ 0.9553 rad
   - Ry(2*0.9553166) ≈ Ry(1.9106)
   - This rotates q[0] so that cos(θ/2) = 1/√3 and sin(θ/2) = √(2/3)
   - State becomes: (1/√3)|000⟩ + √(2/3)|100⟩

3. nctrl Ry(π/2, q[0], q[1]):
   - This applies Ry(π/2) to q[1] when q[0] is |0⟩ (negative control)
   - When q[0] = |0⟩: Ry(π/2) rotates |0⟩ to |+⟩ = (|0⟩ + |1⟩)/√2
   - So: (1/√3)|000⟩ → (1/√3)(|000⟩ + |010⟩)/√2 = (1/√6)(|000⟩ + |010⟩)
   - State becomes: (1/√6)|000⟩ + (1/√6)|010⟩ + √(2/3)|100⟩

4. CNOT(q[1], q[2]):
   - Flips q[2] when q[1] = |1⟩
   - |010⟩ → |011⟩
   - State: (1/√6)|000⟩ + (1/√6)|011⟩ + √(2/3)|100⟩

5. CNOT(q[0], q[1]):
   - Flips q[1] when q[0] = |1⟩
   - |100⟩ → |110⟩
   - State: (1/√6)|000⟩ + (1/√6)|011⟩ + √(2/3)|110⟩

6. CNOT(q[0], q[2]): |110⟩ → |111⟩, |000⟩ unchanged, |011⟩ unchanged
   - State: (1/√6)|000⟩ + (1/√6)|011⟩ + √(2/3)|111⟩

Wait, this doesn't seem right. Let me re-check the predicted output: {|000>: 0.166667, |011>: 0.666667, |110>: 0.166667}

Hmm, The resulting probabilities should be |000⟩: 1/6, |011⟩: 2/3, |110⟩: 1/6. That's (1/√6)², (√(2/3))², (1/√6)².

So the final state before measurement should be:
(1/√6)|000⟩ + √(2/3)|011⟩ + (1/√6)|110⟩

Wait, let me re-trace:

After step 5 (CNOT(q[0], q[1])):
State: (1/√6)|000⟩ + (1/√6)|011⟩ + √(2/3)|110⟩

This matches the expected! So steps 6-8 (the swap) aren't in my trace... Let me re-read the code.

Looking at the code again:

So after CNOT(q[0], q[1]), the state is:
(1/√6)|000⟩ + (1/√6)|011⟩ + √(2/3)|110⟩

Then we have a swap (three-CNOT decomposition) between q[0] and q[2]:
- CNOT(q[0], q[2]): |011⟩ → |111⟩, |110⟩ → |111⟩... wait no
  - |000⟩ → |000⟩ (q[0]=0, so no flip)
  - |011⟩ → |011⟩ (q[0]=0)
  - |110⟩ → |111⟩ (q[0]=1, flip q[2])
  State: (1/√6)|

## isqTrain/3731

- task_id: `isqTrain/3731`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `675`

### Prompt

帮我写一个isQ程序：Prepare the 3-qubit GHZ state with phase pi/2:
|GHZ> = (|000> + e^{i*pi/2}|111>) / sqrt(2)
Use Hadamard on first qubit, Rz for phase, then CNOT chain. Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Prepare a 3-qubit GHZ state with relative phase π/2: (|000⟩ + e^{iπ/2}|111⟩)/√2.

**Qubits:** 3 qubits (q[0], q[1], q[2]), all measured.

**State evolution:**
1. Start: |000⟩
2. H(q[0]): → (|000⟩ + |100⟩)/√2
3. Rz(π/2, q[0]): applies e^{-iπ/4} to |0⟩ and e^{iπ/4} to |1⟩ → (e^{-iπ/4}|000⟩ + e^{iπ/4}|100⟩)/√2
4. CNOT(q[0], q[1]): → (e^{-iπ/4}|000⟩ + e^{iπ/4}|110⟩)/√2
5. CNOT(q[1], q[2]): → (e^{-iπ/4}|000⟩ + e^{iπ/4}|111⟩)/√2

The relative phase is e^{iπ/4}/e^{-iπ/4} = e^{iπ/2} = i, yielding the target state up to global phase e^{-iπ/4}.

**Probabilities:** Each amplitude has magnitude 1/√2, so P(|000⟩) = P(|111⟩) = 0.5, with all other outcomes having zero probability.

## isqTrain/1848

- task_id: `isqTrain/1848`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `5471`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[3];
procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes 3 qubits to |000> and applies a Hadamard gate to q[0], followed by two CNOT gates.
2. H(q[0]) evolves the state to 1/√2(|000> + |100>).
3. CNOT(q[0], q[1]) flips the target q[1] when q[0] is |1>, changing the state to 1/√2(|000> + |110>).
4. CNOT(q[1], q[2]) flips q[2

### Reference answer

{'predicted_probs': {'000': 0.5, '111': 0.5}, 'explanation': 'GHZ state. P(|000⟩) = 0.5 at index 0, P(|111⟩) = 0.5 at index 7.'}

## isqTrain/1378

- task_id: `isqTrain/1378`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `1859`

### Prompt

Implement the following in isQ: Prepare the state |11>, apply a SWAP gate, and measure both qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Prepare |11> state on two qubits, apply swap (three-CNOT decomposition), and measure both.
Two qubits q[0] and q[1] are needed; both are measured.

State evolution:
1. Initial: |00>
2. X(q[0]): |10>
3. X(q[1]): |11>
4. swap (three-CNOT decomposition)(q[0], q[1]): |11> (swapping identical qubit states yields the same state)

Expected probabilities: {|11>: 1.0} — swap (three-CNOT decomposition) exchanges qubit values, but since both are |1>, the state remains |11> with certainty.

## isqTrain/1781

- task_id: `isqTrain/1781`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4896`

### Prompt

Implement a quantum circuit in isQ: Apply H then Z to each of 2 qubits. Measure all. Z phase is invisible in Z-basis measurement.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply H then Z to each of 2 qubits and measure both in the Z-basis.
2. **Qubits**: 2 qubits (q[0], q[1]), both measured.
3. **State evolution**:
   - Initialize: |00⟩
   - H on both: (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2
   - Z on q[0]: (|00⟩ + |01⟩ − |10⟩ − |11⟩)/2
   - Z on q[1]: (|00⟩ − |01⟩ − |10⟩ + |11⟩)/2
4. **Probabilities**: Each computational basis state has amplitude ±1/2, so |amplitude|² = 1/4 for all four states. The Z phase is invisible in Z-basis measurement, yielding uniform distribution: {|00⟩: 0.25, |01⟩: 0.25, |10⟩: 0.25, |11⟩: 0.25}.

## isqTrain/3198

- task_id: `isqTrain/3198`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5672`

### Prompt

Write isQ code for the following quantum task: an isQ program: apply Ry(11*pi/12) to a qubit and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Apply an Ry rotation of 11π/12 to a single qubit, then measure it.
2. **Qubits:** 1 qubit needed; q[0] is measured.
3. **State evolution:**
   - Initial state: |0⟩
   - Apply Ry(11π/12): Ry(θ)|0⟩ = cos(θ/2)|0⟩ + sin(θ/2)|1⟩
   - With θ = 11π/12, θ/2 = 11π/24 ≈ 82.5°
   - Final state: cos(11π/24)|0⟩ + sin(11π/24)|1⟩ ≈ 0.1305|0⟩ + 0.9914|1⟩
4. **Expected probabilities:** P(|0⟩) = cos²(11π/24) ≈ 0.017, P(|1⟩) = sin²(11π/24) ≈ 0.983, matching the reference values.

## isqTrain/4004

- task_id: `isqTrain/4004`
- task_type: `bug_fix`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `4191`

### Prompt

The following isQ code has a bug. Find and fix it.

Buggy code:
```
import std;
// 2-qubit state via Ry rotations: Ry(2.0 * 1.0) ⊗ Ry(1.0)
qbit q[2];

procedure main() {
    // Apply rotations to create product state
    Ry(1.0, q[0]);
    Ry(1.0, q[1]);
    // Measure
    M(q[0]); M(q[1]);
}

``` (bug type: wrong parameter)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: The comment `Ry(2.0 * 1.0) ⊗ Ry(1.0)` reveals the first qubit's rotation angle was intended to be `2.0` (i.e., `Ry(2.0, q[0])`), but the task specifies a product state with angles `(1.0, 1.0)`. The wrong parameter `2.0` was used for `q[0]`.

2. **Fix**: Change `Ry(2.0, q[0])` to `Ry(1.0

## isqTrain/1457

- task_id: `isqTrain/1457`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `4055`

### Prompt

Write an isQ program that Prepare the computational basis state |00011> on 5 qubits by applying X gates to the appropriate qubits, then measure all.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Prepare the 5-qubit computational basis state |00011⟩ and measure all qubits.

**Qubits:** 5 qubits (q[0]–q[4]), all measured.

**State evolution:**
1. Initial state: |00000⟩
2. X(q[3]) flips qubit 3 from |0⟩ to |1⟩ → |00010⟩
3. X(q[4]) flips qubit 4 from |0⟩ to |1⟩ → |00011⟩

**Measurement probabilities:** The final state is exactly |00011⟩, a single computational basis state, so measurement yields the bitstring '00011' with probability 1.0.
