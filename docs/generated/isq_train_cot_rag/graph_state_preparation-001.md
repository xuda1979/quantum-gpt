# ISQ training COT RAG corpus: graph_state_preparation shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3098

- task_id: `isqTrain/3098`
- task_type: `code_generation`
- category: `graph_state_preparation`
- difficulty: `intermediate`
- concept_tags: `superposition`, `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1736`

### Prompt

用isQ实现preparing a 5-qubit linear graph state. Apply H to all qubits, then CZ on adjacent pairs, then measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare a 5-qubit linear graph state by initializing all qubits to |+⟩, entangling adjacent pairs with CZ, then measuring.
2. **Qubits**: 5 qubits (q[0]-q[4]), all measured.
3. **State evolution**:
   - Initial: |00000⟩
   - After H on all: |+⟩⁵ = (1/4√2)Σᵢ|xᵢ⟩ for all 32 basis states
   - CZ(q[0],q[1]): Applies phase (-1)^(x₀·x₁), yielding (1/4√2)Σ(-1)^(x₀x₁)|x⟩
   - CZ(q[1],q[2]): Adds phase (-1)^(x₁·x₂)
   - CZ(q[2],q[3]): Adds phase (-1)^(x₂·x₃)
   - CZ(q[3],q[4]): Adds phase (-1)^(x₃·x₄)
   - Final state: (1/4√2)Σ(-1)^(x₀x₁+x₁x₂+x₂x₃+x₃x₄)|x₀x₁x₂x₃x₄⟩
4. **Probabilities**: Each amplitude has magnitude 1/(4√2), so all 32 outcomes have probability (1/4√2)² = 1/32 = 0.03125.

## isqTrain/3097

- task_id: `isqTrain/3097`
- task_type: `code_generation`
- category: `graph_state_preparation`
- difficulty: `intermediate`
- concept_tags: `superposition`, `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1734`

### Prompt

Implement a quantum circuit in isQ: preparing a 4-qubit linear graph state. Apply H to all qubits, then CZ on adjacent pairs, then measure.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Prepare a 4-qubit linear graph state and measure all qubits.
2. Qubits: 4 (q[0]–q[3]), all measured.
3. Evolution: |0000⟩ →H⊗4 → |++++⟩ = ¼∑_{x∈{0,1}⁴}|x⟩. CZ(q[0],q[1]) adds a -1 phase when both q[0]=|1⟩ and q[1]=|1⟩; similarly for CZ(q[1],q[2]) and CZ(q[2],q[3]). The resulting state is ¼∑_{x}|x⟩·(-1)^{x₀x₁+x₁x₂+x₂x₃}, a linear cluster state.
4. Measurement probabilities: Since all amplitudes have magnitude ¼, each of the 16 basis states occurs with probability (¼)² = 1/16 = 0.0625.

## isqTrain/3247

- task_id: `isqTrain/3247`
- task_type: `code_generation`
- category: `graph_state_preparation`
- difficulty: `intermediate`
- concept_tags: `superposition`, `entanglement`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `3783`

### Prompt

Code this in isQ: an isQ program: create 4-qubit linear graph state, then measure all in X-basis (apply H before measurement).

### Chain-of-thought reasoning

Let me trace through this circuit step by step.

1. Goal: Create a 4-qubit linear graph state and measure all qubits in the X-basis.

2. We need 4 qubits (q[0], q[1], q[2], q[3]), all measured.

3. State evolution:
- Initial state: |0000⟩
- After H on all: (|0⟩+|1⟩)/√2 ⊗ 4 = 1/4(|0⟩+|1⟩)⊗4 = superposition of all 16 basis states, each with amplitude 1/4
- After CZ(q[0], q[1]): applies Z to q[1] when q[0]=|1⟩, so |1x⟩ terms get their neighbor flipped in sign
- After CZ(q[1], q[2]): applies Z to q[2] when q[1]=|1⟩
- After CZ(q[2], q[3]): applies Z to q[3] when q[2]=|1⟩
- This creates the linear graph state

4. Then applying H to all and measuring in computational basis is equivalent to X-basis measurement.

For the graph state: |G⟩ = ∏_{(i,j)∈E} CZ_{ij} H⊗4 |0000⟩

The graph state is an entangled state. When we measure all in X-basis (apply H then measure), we get outcomes that satisfy certain parity constraints.

Actually, let me think about this more carefully. The graph state has the property that measuring all qubits in X-basis gives outcomes that satisfy: for each vertex, the product of outcomes of neighbors equals the outcome of that vertex... wait, no.

Actually, the graph state |G⟩ satisfies: for each vertex i, X_i ⊗_{j∈N(i)} Z_j |G⟩ = |G⟩

So if we measure all in X-basis, the outcomes x_i satisfy: for each i, x_i = ⊗_{j∈N(i)} x_j... no wait.

Measuring X_i on the graph state, the stabilizer X_i ⊗_{j∈N(i)} Z_j means that the eigenvalue is +1. If we measure X on all qubits, the outcomes must be consistent with these stabilizer relations.

For a linear graph 0-1-2-3:
- X_0 Z_1 = I → x_0 * z_1 eigenvalue = +1... but we're measuring X on all, not Z.

Hmm, let me think differently. After H on all qubits of the graph state, we get a state where measuring in computational basis gives equal probability 1/16 for all outcomes? That seems to be what The predicted output.

Actually, the graph state is a stabilizer state. Applying H⊗4 to it transforms it. The H gate conjugates X to Z and Z to X. So the stabilizers X_i ⊗_{j∈N(i)} Z_j become Z_i ⊗_{j∈N(i)} X_j.

So after H⊗4, the stabilizers are:
- Z_0 X_1
- X_0 Z_1 X_2
- X_1 Z_2 X_3
- X_2 Z_3

Measuring in Z-basis (computational), the outcomes must be eigenstates of these stabilizers with eigenvalue +1. But wait, these stabilizers involve both X and Z, so they don't commute with Z-measurement...

Actually, let me reconsider. When we measure all qubits in Z-basis, we collapse to a computational basis state. The stabilizers Z_i X_{N(i)} don't commute with Z-measurements on all qubits.

The measurement outcomes should still be random with equal probability? Let me check.

For a simpler case: 2-qubit graph state. H(q[0]); H(q[1]); CZ(q[0],q[1]) creates the state (|0+⟩ + |1-⟩)/√2 = (|00⟩ + |01⟩ + |10⟩ - |11⟩)/2.

Then H(q[0]); H(q[1]) gives... let me compute. H⊗2 applied to (|00⟩ + |01⟩ + |10⟩ - |11⟩)/2:

H|0⟩ = |+⟩, H|1⟩ = |-⟩

So H⊗2 (|00⟩) = |++⟩ = (|00⟩+|01⟩+|10⟩+|11⟩)/2
H⊗2 (|01⟩) = |+−⟩ = (|00⟩-|01⟩+|10⟩-|11⟩)/2
H⊗2 (|10⟩) = |-+⟩ = (|00⟩+|01⟩-|10

## isqTrain/3102

- task_id: `isqTrain/3102`
- task_type: `code_generation`
- category: `graph_state_preparation`
- difficulty: `intermediate`
- concept_tags: `superposition`, `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5544`

### Prompt

Implement the following in isQ: preparing a 5-qubit ring (cycle) graph state. Apply H to all, CZ on ring edges, measure.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Prepare a 5-qubit ring (cycle) graph state by applying Hadamard gates followed by CZ gates on edges (0,1), (1,2), (2,3), (3,4), (4,0), then measure all qubits.

2. **Qubits**: 5 qubits q[0]–q[4], all measured, yielding 5-bit output bitstrings.

3. **State evolution**:
   - Start: |00000⟩
   - After H on all: |+⟩⁵ = (1/√32) Σ_{x∈{0,1}⁵} |x⟩ (uniform superposition over all 32 basis states)
   - Each CZ(q[i],q[j]) multiplies basis state |x⟩ by (-1)^{x_i·x_j}, adding a phase when both qubits are |1⟩.
   - After all 5 CZ gates (ring edges): |G_ring⟩ = (1/√32) Σ_x (-1)^{x₀x₁ + x₁x₂ + x₂x₃ + x₃x₄ + x₄x₀} |x⟩

4. **Probabilities**: Every amplitude has magnitude 1/√32 (phases are ±1 only), so |⟨x|G_ring⟩|² = 1/32 = 0.03125 for all 32 basis states. This gives uniform measurement probabilities across all outcomes, consistent with the predicted output.

## isqTrain/3101

- task_id: `isqTrain/3101`
- task_type: `code_generation`
- category: `graph_state_preparation`
- difficulty: `intermediate`
- concept_tags: `superposition`, `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2221`

### Prompt

Implement the following in isQ: preparing a 3-qubit ring (cycle) graph state. Apply H to all, CZ on ring edges, measure.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for a 3-qubit ring graph state preparation circuit.

Let me trace through the circuit:
1. Start with |000>
2. Apply H to all: (1/√8)(|0>+|1>)⊗(|0>+|1>)⊗(|0>+|1>) = (1/√8)(|000>+|001>+|010>+|011>+|100>+|101>+|110>+|111>)
3. Apply CZ(q[0], q[1]): This applies Z to q[1] when q[0] is |1>. So states where q[0]=1 and q[1]=1 get a -1 phase.
4. Apply CZ(q[1], q[2]): applies Z to q[2] when q[1] is |1>. States where q[1]=1 and q[2]=1 get a -1 phase.
5. Apply CZ(q[2], q[0]): applies Z to q[0] when q[2] is |1>. States where q[2]=1 and q[0]=1 get a -1 phase.

Let me track the signs for each computational basis state:
- |000>: no sign changes → +1
- |001>: q[0]=0, no CZ triggers with q[0] as control; q[1]=0, no CZ triggers with q[1] as control; q[2]=1, q[0]=0 so CZ(q[2],q[0]) doesn't flip → +1
- |010>: q[0]=0; q[1]=1, q[2]=0 so CZ(q[1],q[2]) no flip; q[2]=0 → +1
- |011>: q[0]=0; q[1]=1, q[2]=1 → CZ(q[1],q[2]) flips → -1; q[2]=1, q[0]=0 → no flip. So -1
- |100>: q[0]=1, q[1]=0 → CZ(q[0],q[1]) no flip; q[1]=0; q[2]=0 → +1
- |101>: q[0]=1, q[1]=0 → no flip; q[1]=0; q[2]=1, q[0]=1 → CZ(q[2],q[0]) flips → -1. So -1
- |110>: q[0]=1, q[1]=1 → CZ(q[0],q[1]) flips → -1; q[1]=1, q[2]=0 → no flip; q[2]=0 → net -1
- |111>: q[0]=1, q[1]=1 → -1; q[1]=1, q[2]=1 → -1 (×-1 = +1); q[2]=1, q[0]=1 → -1 (×+1 = -1). So -1.

Wait, let me redo this more carefully. Each CZ is independent and adds a -1 for each time a state matches the control AND target being |1>.

- |000>: none of the CZs apply → +1
- |001>: CZ(q[2],q[0]): q[2]=1 but q[0]=0 → no → +1
- |010>: CZ(q[1],q[2]): q[1]=1 but q[2]=0 → no → +1
- |011>: CZ(q[1],q[2]): q[1]=1 AND q[2]=1 → -1. Others don't match → total -1
- |100>: CZ(q[0],q[1]): q[0]=1 but q[1]=0 → no → +1
- |101>: CZ(q[0],q[1]): q[0]=1 but q[1]=0 → no. CZ(q[2],q[0]): q[2]=1 AND q[0]=1 → -1. Total: -1
- |110>: CZ(q[0],q[1]): q[0]=1 AND q[1]=1 → -1. CZ(q[1],q[2]): q[1]=1 but q[2]=0 → no. Total: -1
- |111>: CZ(q[0],q[1]): both 1 → -1. CZ(q[1],q[2]): both 1 → -1 (so ×-1 = +1... wait, no, they accumulate). Let me just count: three CZs, how many apply to |111>?
  - CZ(q[0],q[1]): q[0]=1, q[1

## isqTrain/3100

- task_id: `isqTrain/3100`
- task_type: `code_generation`
- category: `graph_state_preparation`
- difficulty: `intermediate`
- concept_tags: `superposition`, `entanglement`
- source: `isq_train_cot`
- dataset_index: `243`

### Prompt

实现以下量子计算任务（使用isQ）：preparing a 5-qubit star graph state with q[0] as center. Apply H to all, CZ from center to leaves, measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare a 5-qubit star graph state with q[0] as center, then measure all qubits.
2. **Qubits**: 5 qubits (q[0]–q[4]), all measured.
3. **State evolution**:
   - Initial: |00000⟩
   - After H on all: |+++++⟩ = (1/√32) Σ_{x∈{0,1}⁵} |x⟩
   - CZ(q[0],q[i]) for i=1–4 applies phase (-1)^(x₀·xᵢ), yielding: (1/√32) Σ_x (-1)^(x₀(x₁+x₂+x₃+x₄)) |x⟩
4. **Measurement probabilities**: Each amplitude has magnitude 1/√32, so all 32 basis states have equal probability 1/32 = 0.03125. The phases create entanglement but don't affect measurement outcomes.

## isqTrain/3381

- task_id: `isqTrain/3381`
- task_type: `code_generation`
- category: `graph_state_preparation`
- difficulty: `intermediate`
- concept_tags: `superposition`, `entanglement`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `1868`

### Prompt

请用isQ语言编写一个量子电路：an isQ program: H on all 4 qubits, then use a for loop to apply CZ between each adjacent pair. Measure all.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Prepare an equal superposition over 4 qubits, then apply CZ gates between adjacent pairs to create phase entanglement, and measure all.

2. **Qubits**: 4 qubits (q[0]–q[3]), all measured.

3. **State evolution**:
   - **Initial**: |ψ₀⟩ = |0000⟩
   - **After H⊗4**: |ψ₁⟩ = (1/4) Σ_{x∈{0,1}⁴} |x⟩ — uniform superposition of all 16 basis states
   - **After CZ(q[0

## isqTrain/3096

- task_id: `isqTrain/3096`
- task_type: `code_generation`
- category: `graph_state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`, `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3560`

### Prompt

Write an isQ program that preparing a 2-qubit linear graph state. Apply H to all qubits, then CZ on adjacent pairs, then measure.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Prepare a 2-qubit linear graph state via H on all qubits followed by CZ on the adjacent pair, then measure.

2. **Qubits**: 2 qubits (q[0], q[1]); both are measured.

3. **State evolution**:
   - Start in |00⟩.
   - H on both: |00⟩ → |+⟩|+⟩ = (|00⟩+|01⟩+|10⟩+|11⟩)/2.
   - CZ(q[0],q[1]) applies Z to q[1] when q[0]=|1⟩: flips sign of |11⟩ only → (|00⟩+|01⟩+|10⟩−|11⟩)/2, the graph state.

4. **Probabilities**: Each computational basis state has amplitude ±1/2, so each has probability (1/2)² = 0.25.

## isqTrain/3380

- task_id: `isqTrain/3380`
- task_type: `code_generation`
- category: `graph_state_preparation`
- difficulty: `intermediate`
- concept_tags: `superposition`, `entanglement`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `5683`

### Prompt

Code this in isQ: an isQ program: H on all 3 qubits, then use a for loop to apply CZ between each adjacent pair. Measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Create an equal superposition over 3 qubits, apply controlled-phase (CZ) gates between adjacent pairs, and measure all qubits.
2. **Qubits:** 3 qubits are used (`q[0]`, `q[1]`, `q[2]`), and all are measured.
3. **State evolution:**
   - Initial state is $|000\rangle$.
   - Applying H to all qubits creates the uniform superposition $\frac{1}{\sqrt{8}} \sum_{x \in \{0,1\}^3} |x\rangle$.
   - The `CZ(q[0], q[1])` gate flips the phase to $-1$ for basis states where the first two qubits are both 1 (yielding $-|110\rangle$ and $-|111\rangle$).
   - The `CZ(q[1

## isqTrain/3382

- task_id: `isqTrain/3382`
- task_type: `code_generation`
- category: `graph_state_preparation`
- difficulty: `intermediate`
- concept_tags: `superposition`, `entanglement`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `5387`

### Prompt

Implement the following in isQ: an isQ program: H on all 5 qubits, then use a for loop to apply CZ between each adjacent pair. Measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply Hadamard to all 5 qubits creating superposition, then entangle adjacent pairs with CZ gates, and measure all qubits.

2. **Qubits**: 5 qubits (q[0]–q[4]), all measured.

3. **State evolution**:
   - Initial: |00000⟩
   - After H on all: |+++++⟩ = (1/√32) Σ|x⟩ for all x ∈ {0,1}⁵ (equal superposition of all 32 states)
   - CZ(q[0],q[1]): applies -1 phase to states where q[0]=q[1]=1 (e.g., |11xxx⟩ → -|11xxx⟩)
   - CZ(q[1],q[2]): applies -1 phase to states where q[1
