# ISQ training COT RAG corpus: gate_decomposition shard 13

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3345

- task_id: `isqTrain/3345`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `2854`

### Prompt

Help me write isQ code that an isQ program: apply 2-qubit gate chain CZ-H0-H1 to |00> and measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply CZ followed by Hadamard on both qubits to |00>, then measure both.
2. **Qubits**: 2 qubits (q[0], q[1]), both measured.
3. **State evolution**:
   - Start: |00⟩
   - CZ(q[0], q[1]): Control is |0⟩, so no phase flip → state remains |00⟩
   - H(q[0]): |00⟩ → (|00⟩ + |10⟩)/√2
   - H(q[1]): (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2
4. **Probabilities**: The final state is an equal superposition of all four basis states, each with amplitude 1/2, giving probability |1/2|² = 0.25 for each outcome: {|00⟩: 0.25, |01⟩: 0.25, |10⟩: 0.25, |11⟩: 0.25}.

## isqTrain/3407

- task_id: `isqTrain/3407`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `1762`

### Prompt

Write isQ code for the following quantum task: an isQ program: H, Rz(3*pi/5), H on a qubit. This is equivalent to Rx(3*pi/5).

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement an Rx(3π/5) rotation on a single qubit using the decomposition H·Rz(3π/5)·H.
2. **Qubits**: 1 qubit is needed, and q[0] is measured.
3. **State evolution**:
   - Initial: |0⟩
   - After H: |+⟩ = (|0⟩ + |1⟩)/√2
   - After Rz(3π/5): (e^{-i3π/10}|0⟩ + e^{i3π/10}|1⟩)/√2
   - After final H: cos(3π/10)|0⟩ - i·sin(3π/10)|1⟩ = Rx(3π/5)|0⟩
4. **Probabilities**: P(|0⟩) = cos²(3π/10) ≈ 0.3455, P(|1⟩) = sin²(3π/10) ≈ 0.6545, consistent with an X-rotation by 3π/5.

## isqTrain/3412

- task_id: `isqTrain/3412`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `2145`

### Prompt

帮我写一个isQ程序：an isQ program: H, Rz(5*pi/6), H on a qubit. This is equivalent to Rx(5*pi/6).

### Chain-of-thought reasoning

## Reasoning
The circuit applies a sequence of H, Rz(5*pi/6), and H gates to a single qubit, which is mathematically equivalent to an Rx(5*pi/6) rotation.
One qubit is

## isqTrain/3289

- task_id: `isqTrain/3289`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2497`

### Prompt

I need an isQ program to an isQ program: apply H, Rz(1*pi/4), Rz(-1*pi/4), H. Since Rz cancels, net is H*H=I.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply H, Rz(π/4), Rz(-π/4), H to show Rz cancellation yields H² = I, leaving |0⟩.
2. **Qubits**: 1 qubit `q[0]`, which is measured.
3. **State evolution**:
   - Start: |0⟩
   - After H: |+⟩ = (|0⟩ + |1⟩)/√2
   - After Rz(π/4): (e^{-iπ/8}|0⟩ + e^{iπ/8}|1⟩)/√2
   - After Rz(-π/4): phases cancel → (|0⟩ + |1⟩)/√2 = |+⟩
   - After H: |0⟩
4. **Expected probabilities**: Final state is |0⟩, so measurement yields {|0⟩: 1.0}.

## isqTrain/3333

- task_id: `isqTrain/3333`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `883`

### Prompt

Implement a quantum circuit in isQ: an isQ program: apply gate chain X-Z-H to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Apply the gate sequence X, Z, and H to an initial |0> state and measure the result.
2. **Qubits:** 1 qubit is required and measured.
3. **State evolution:**
   - Start in |0>.
   - Apply X gate: |0> evolves to |1>.
   - Apply Z gate: |1> acquires a phase, evolving to -|1>.
   - Apply H gate: -|1> evolves to -1/√2|0> + 1/√2|1>.
4. **Probabilities:** The final state is an equal superposition of |0> and |1>, meaning both states have a 0.5 probability of being measured.

## isqTrain/3334

- task_id: `isqTrain/3334`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4721`

### Prompt

Write isQ code for the following quantum task: an isQ program: apply gate chain S-T-H to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply S, T, H gates sequentially to |0⟩ and measure the result.

Single qubit q[0] is used and measured.

State evolution:
- Initial: |0⟩
- After S: S|0⟩ = |0⟩ (S only phases |1⟩ by i)
- After T: T|0⟩ = |0⟩ (T only phases |1⟩ by e^(iπ/4))
- After H: H|0⟩ = |+⟩ = (1/√2)(|0⟩ + |1⟩)

Measurement probabilities: P(|0⟩) = |1/√2|² = 0.5, P(|1⟩) = |1/√2|² = 0.5, since the final state |+⟩ has equal amplitudes.

## isqTrain/3287

- task_id: `isqTrain/3287`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `143`

### Prompt

Implement the following in isQ: an isQ program: apply Rx(2*pi/3) then Rx(-2*pi/3) to cancel. Measure: should get |0>.

### Chain-of-thought reasoning

## Reasoning
- Goal: Demonstrate Rx gate cancellation by applying Rx(2π/3) followed by its inverse Rx(-2π/3).
- Qubits: 1 qubit (q[0]), which is measured.
- State evolution:
  1. Start in |0⟩.
  2. Apply Rx(2π/3): rotates around X-axis by 2π/3, giving cos(π/3)|0⟩ - i·sin(π/3)|1⟩ = 0.5|0⟩ - i·(√3/2)|1⟩.
  3. Apply Rx(-2π/3): exactly undoes the previous rotation since Rx(θ)Rx(-θ) = I.
  4. Final state returns to |0⟩.
- Expected probabilities: {|0⟩: 1.0}, since the two rotations cancel perfectly.

## isqTrain/3128

- task_id: `isqTrain/3128`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1478`

### Prompt

I need an isQ program to an isQ program: apply ctrl Z (=CZ) on initial state |11> and measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply a controlled-Z (CZ) gate to the |11⟩ state and measure both qubits.
2. **Qubits**: 2 qubits are required; both are measured.
3. **State evolution**:
   - Start in |00⟩. Apply X to each: |00⟩ → |10⟩ → |11⟩.
   - Apply CZ: since the control (q[0]) is |1⟩, Z acts on q[1]. Z|1⟩ = −|1⟩, so the state becomes −|11⟩ (global phase only).
4. **Expected probabilities**: The global phase has no physical effect on measurements, so the outcome is |11⟩ with probability 1.0.

## isqTrain/3402

- task_id: `isqTrain/3402`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `5228`

### Prompt

Create an isQ quantum circuit that an isQ program: H, Rz(1*pi/8), H on a qubit. This is equivalent to Rx(1*pi/8).

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply H-Rz(π/8)-H to a single qubit, equivalent to Rx(π/8).
2. **Qubits**: 1 qubit needed, 1 measured.
3. **State evolution**:
   - Initial: |0⟩
   - After H: |+⟩ = (|0⟩ + |1⟩)/√2
   - After Rz(π/8): (|0⟩ + e^(iπ/8)|1⟩)/√2
   - After H: cos(π/16)|0⟩ - i·sin(π/16)|1⟩ = Rx(π/8)|0⟩
4. **Probabilities**: |⟨0|ψ⟩|² = cos²(π/16) ≈ 0.9619, |⟨1|ψ⟩|² = sin²(π/16) ≈ 0.0381.

## isqTrain/1426

- task_id: `isqTrain/1426`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `2906`

### Prompt

Create an isQ quantum circuit that Apply CNOT decomposition (CNOT from H+CZ+H) to the initial state |10> and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply an H+CZ+H decomposition of the CNOT gate to the initial state |10> to flip the target qubit, then measure.
2. **Qubits**: 2 qubits are used (`q[0]` as control, `q[1]` as target), and both are measured.
3. **State Evolution**:
   - **Initial**: The system starts in the ground state |00>.
   - **X(q[0])**: Flips the control qubit to initialize the state to |10>.
   - **H(q[1])**: Applies a Hadamard to the target, evolving the state to 1/√2 (|10> + |11>) = |1>|+>.
   - **CZ(q[0], q[1])**: Applies a phase flip to |11>, resulting in 1/√2 (|10> - |11>) = |1>|->.
   - **H(q[1])**: Applies a second Hadamard to the target, mapping |-> back to |1>, leaving the final state |11>.
4. **Measurement Probabilities**: The system is deterministically in the |11> state prior to measurement, yielding a 100% probability of measuring the bitstring |11> (decimal 3).
