# ISQ training COT RAG corpus: state_preparation shard 38

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3146

- task_id: `isqTrain/3146`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3279`

### Prompt

Create an isQ quantum circuit that an isQ program: apply X to all 2 qubits to prepare |11>, then measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare the 2-qubit state |11⟩ from |00⟩ by flipping both qubits, then measure.
2. **Qubits**: 2 qubits are allocated; both are measured.
3. **State evolution**: |00⟩ → X(q[0]) → |10⟩ → X(q[1]) → |11⟩.
4. **Probabilities**: The final state is |11⟩ with certainty, so measurement yields bitstring 11 with probability 1.0.

## isqTrain/3209

- task_id: `isqTrain/3209`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1870`

### Prompt

Help me write isQ code that an isQ program: apply Rx(7*pi/12) to a qubit and measure.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply an Rx rotation of 7π/12 to a single qubit and measure the result.
2. One qubit is needed (q[0]) and is the only qubit measured.
3. Initial state: |0⟩. After Rx(7π/12): |ψ⟩ = cos(7π/24)|0⟩ - i·sin(7π/24)|1⟩, where 7π/24 ≈ 52.5°.
4. Expected probabilities: P(|0⟩) = cos²(7π/24) ≈ 0.3706, P(|1⟩) = sin²(7π/24) ≈ 0.6294.

## isqTrain/3777

- task_id: `isqTrain/3777`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `4149`

### Prompt

I need an isQ program to the 4-qubit GHZ state (|0000> + |1111>)/√2 using a for loop for the CNOT chain. Measure all 4 qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Create a 4-qubit GHZ state, (|0000> + |1111>)/√2, and measure all qubits.
Qubits: 4 qubits are used and all are measured.
1. Start in |0000>. H(q[0]) creates superposition on the first qubit: (|0000> + |1000>)/√2.
2. A for loop applies CNOT(q[i], q[i+1]) for i=0, 1, 2.
3. CNOT(q[0], q[1]) flips q[1] when q[0] is |1>, resulting in (|0000> + |1100>)/√2.
4. CNOT(q[1], q[2]) flips q[2] when q[1] is |1>, resulting in (|0000> + |1110>)/√2.
5. CNOT(q[2], q[3]) flips q[3] when q[2] is |1>, yielding the final GHZ state (|0000> + |1111>)/√2.
6. Measuring all qubits collapses the superposition, giving 50% probability for |0000> and 50% for |1111>.

## isqTrain/1456

- task_id: `isqTrain/1456`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `1026`

### Prompt

Implement the following in isQ: Prepare the computational basis state |00010> on 5 qubits by applying X gates to the appropriate qubits, then measure all.

### Chain-of-thought reasoning

## Reasoning
The goal is to prepare the 5-qubit computational basis state |00010> and measure all qubits.
We use a 5-qubit register initialized to |00000>. Applying an X gate to qubit 3 flips it from |0> to |1>.
The quantum state transitions from |00000> to |00010>.
Measuring all 5 qubits collapses the state, yielding the bitstring '00010' with a probability of 1.0.

## isqTrain/4778

- task_id: `isqTrain/4778`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_for_loop`, `isq_syntax_if_else`
- source: `isq_train_cot`
- dataset_index: `2640`

### Prompt

Help me write isQ code that implements: for-loop X on 3 qubits -> all |1>. Declare a global qbit array q of 3 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Flip all 3 qubits from |0⟩ to |1⟩ using X gates applied via a for-loop.
Qubits: 3 global qubits (q[0], q[1], q[2]), all measured.
State evolution:
- Initial: |000⟩
- After X(q[0]): |100⟩
- After X(q[1]): |110⟩
- After X(q[2]): |111⟩
Final state |111⟩ yields measurement outcome 111 with probability 1.0.

## isqTrain/3871

- task_id: `isqTrain/3871`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4355`

### Prompt

Implement a quantum circuit in isQ: Prepare the Bell state |Φ+> = (|00> + |11>)/√2 using isQ state assignment syntax `q = |0> + |3>`. Note: isQ uses little-endian encoding. Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare the Bell state |Φ+⟩ = (|00⟩ + |11⟩)/√2 and measure both qubits.
2. **Qubits**: 2 qubits (`q[0]`, `q[1]`), both measured.
3. **State evolution**:
   - Initial state: |00⟩
   - Using ket expression `q = |0> + |3>`: In little-endian encoding, |0⟩ = |00⟩ and |3⟩ = |11⟩. The expression directly assigns the superposition (|00⟩ + |11⟩)/√2 (auto-normalized).
4. **Measurement probabilities**: The final state is an equal superposition of |00⟩ and |11⟩, so measurement yields |00⟩ with probability 0.5 and |11⟩ with probability 0.5.

## isqTrain/3740

- task_id: `isqTrain/3740`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `3076`

### Prompt

实现以下量子计算任务（使用isQ）：Prepare a 2-qubit product state by applying Ry(0.5) to q[0] and Ry(0.0) to q[1]. Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
- Goal: Prepare a 2-qubit product state by applying Ry rotations and measure both qubits.
- Initial state is |00>. Applying Ry(0.0) to q[1] leaves it unchanged in |0>.
- Applying Ry(0.5) to q[0] rotates it around the Y-axis, yielding the state cos(0.25)|0> + sin(0.25)|1>.
- The combined 2-qubit state is cos(0.25)|00> + sin(0.25)|10>.
- Measurement probabilities follow from the amplitudes: P(|00>) = cos²(0.25) ≈ 0.9388 and P(|10>) = sin²(0.25) ≈ 0.0612.

## isqTrain/1459

- task_id: `isqTrain/1459`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `1940`

### Prompt

I need an isQ program to Prepare the computational basis state |00101> on 5 qubits by applying X gates to the appropriate qubits, then measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare the computational basis state |00101> on a 5-qubit register and measure it.
2. **Qubits**: 5 qubits (`q[0]` to `q[4]`) are required, and all are measured.
3. **Evolution**: 
   - The qubits are initialized to the ground state |00000>.
   - An X gate is applied to `q[2]`, flipping its state from |0> to |1>, evolving the state to |00100>.
   - An X gate is applied to `q[4]`, flipping its state from |0> to |1>, evolving the state to the target |00101>.
4. **Probabilities**: Because the system is deterministically prepared in the exact basis state |00101> (where `q[0]` maps to the highest bit), measuring all qubits yields the bitstring '00101' with a 1.0 probability.

## isqTrain/148

- task_id: `isqTrain/148`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `755`

### Prompt

Create an isQ quantum circuit that implements the state_preparation pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Prepare a quantum state via Rx rotation and demonstrate gate cancellation with an X-X identity pair.

**Qubits:** 1 qubit (q[0]), which is measured.

**State evolution:**
1. Start: |0⟩
2. Rx(π/3, q[0]): cos(π/6)|0⟩ − i·sin(π/6)|1⟩ = (√3/2)|0⟩ − (i/2)|1⟩
3. X(q[0]): swaps amplitudes → (−i/2)|0⟩ + (√3/2)|1⟩
4. X(q[0]): swaps back → (√3/2)|0⟩ − (i/2)|1⟩ (X-X = I, cancellation restores state from step 2)
5. M(q[0]): measurement in computational basis

**Expected probabilities:** P(|0⟩) = |√3/2|² = 0.75, P(|1⟩) = |−i/2|² = 0.25. The X-X pair acts as identity, so the result equals applying only Rx(π/3).

## isqTrain/4766

- task_id: `isqTrain/4766`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `1832`

### Prompt

Implement the following in isQ: implements: X on 6-qubit array, flip back q[0]. Declare a global qbit array q of 6 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply X to all 6 qubits then flip q[0] back, demonstrating array slicing and individual qubit addressing.
2. **Qubits**: 6 global qubits q[0..5], all measured.
3. **State evolution**:
   - Initial: |000000⟩
   - After X(q[0:6]): |111111⟩ — all qubits flipped to |1⟩
   - After X(q[0]): |011111⟩ — q[0] flipped back to |0⟩
4. **Expected result**: Deterministic state |011111⟩ with probability 1.0, where q[0]=0 (most significant bit) and q[1..5]=1.
