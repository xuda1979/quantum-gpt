# ISQ training COT RAG corpus: state_discrimination shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3245

- task_id: `isqTrain/3245`
- task_type: `code_generation`
- category: `state_discrimination`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1979`

### Prompt

Create an isQ quantum circuit that an isQ program: prepare state by applying Ry(3*pi/8), then discriminate by applying Ry(-3*pi/8) (inverse), then measure. Should return to |0>.

### Chain-of-thought reasoning

## Reasoning
1. The goal is to prepare a quantum state and perfectly reverse it using an inverse rotation, returning it to the initial state.
2. 1 qubit is needed (`q[0]`) and it is measured at the end.
3. Step-by-step evolution:
   - Start with the initial state |0>.
   - Apply Ry(3*pi/8): rotates the state around the Y-axis by 3*pi/8 radians.
   - Apply Ry(-3*pi/8): applies the exact inverse rotation, undoing the previous operation and returning the state to |0>.
4. Because the two rotations cancel each other out, the final state is exactly |0>, yielding a 100% probability of measuring 0.

## isqTrain/3243

- task_id: `isqTrain/3243`
- task_type: `code_generation`
- category: `state_discrimination`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2320`

### Prompt

用isQ实现an isQ program: prepare state by applying Ry(pi/6), then discriminate by applying Ry(-pi/6) (inverse), then measure. Should return to |0>.

### Chain-of-thought reasoning

## Reasoning
1. The circuit demonstrates state discrimination by applying a Y-rotation followed immediately by its inverse to restore the original state.
2. One qubit is required, which is initialized to |0>, manipulated, and then measured.
3. Applying `Ry(pi/6)` to |0> rotates the state vector to $\cos(\pi/12)|0\rangle + \sin(\pi/12)|1\rangle$.
4. Applying the inverse gate `Ry(-pi/6)` perfectly cancels the first rotation ($Ry(-\pi/6) \cdot Ry(\pi/6) = I$), mapping the state back to |0>.
5. Because the final quantum state is exactly |0>, measurement yields the outcome |0> with a probability of 1.0.

## isqTrain/3242

- task_id: `isqTrain/3242`
- task_type: `code_generation`
- category: `state_discrimination`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3059`

### Prompt

实现以下量子计算任务（使用isQ）：an isQ program: prepare state by applying Ry(pi/8), then discriminate by applying Ry(-pi/8) (inverse), then measure. Should return to |0>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Demonstrate state discrimination by applying a rotation then its inverse to return to the initial state.
2. **Qubits**: 1 qubit needed (`q[0]`), which is measured.
3. **State evolution**:
   - Initialize: |0⟩
   - After `Ry(π/8, q[0])`: cos(π/16)|0⟩ + sin(π/16)|1⟩
   - After `Ry(-π/8, q[0])`: The inverse rotation exactly undoes the first rotation, returning to |0⟩
4. **Expected probabilities**: Since the final state is |0⟩, measurement yields P(|0⟩) = 1.0, P(|1⟩) = 0.0.

## isqTrain/3091

- task_id: `isqTrain/3091`
- task_type: `code_generation`
- category: `state_discrimination`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `basis_change`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4889`

### Prompt

Write isQ code for the following quantum task: an isQ program: create Bell state |Psi+> using H+CNOT and X(q[1]), then apply Bell measurement (CNOT+H) to decode, and measure both qubits.

### Chain-of-thought reasoning

Step 1: Understand the goal.
The user wants to generate a reasoning section for a specific quantum circuit written in isQ.
The circuit prepares the Bell state |Psi+>, applies Bell measurement (decoding), and measures the qubits.
Goal: Explain the preparation of |Psi+>, its decoding via Bell measurement, and the predicted output probabilities.

Step 2: Analyze the quantum circuit.
1. Initial state: |00>
2. H(q[0]): 1/sqrt(2) (|00> + |10>)
3. CNOT(q[0], q[1]): 1/sqrt(2) (|00> + |11>) -> |Phi+>
4. X(q[1]): 1/sqrt(2) (|01> + |10>) -> |Psi+>
5. CNOT(q[0], q[1]): 1/sqrt(2) (|01> + |10>) -> CNOT flips q[1] if q[0]=1. So |01> (q0=0, q1=1 -> stays |01>) and |10> (q0=1, q1=0 -> becomes |11>). State is 1/sqrt(2) (|01> + |11>)
6. H(q[0]): H applied to q[0].
   |01> -> H(0)|0> x |1> = 1/sqrt(2)(|0> + |1>) x |1> = 1/sqrt(2) (|01> + |11>)
   |11> -> H(0)|1> x |1> = 1/sqrt(2)(|0> - |1>) x |1> = 1/sqrt(2) (|01> - |11>)
   Total state = 1/2 (|01> + |11> + |01> - |11>) = 1/2 (2|01>) = |01>
7. Measure q[0], q[1]: Result is always 01.

Step 3: Draft the reasoning section based on the required format.
- Goal: Prepare |Psi+> via H+CNOT+X, decode via Bell measurement (CNOT+H), and measure.
- Qubits: 2 qubits, both measured.
- State evolution: |00> -> 1/sqrt(2)(|00>+|10>) -> 1/sqrt(2)(|00>+|11>) [Bell |Phi+>] -> 1/sqrt(2)(|01>+|10>) [Bell |Psi+>].
- Decoding: CNOT gives 1/sqrt(2)(|01>+|11>), then H on q[0] gives |01>.
- Probabilities: Output is deterministic |01>, so P(|01>) = 1.0.

Step 4: Refine to meet constraints (3-8 lines, precise, Dirac notation).
## Reasoning
Goal: Prepare the Bell state |Psi+> and decode it using a Bell measurement to verify deterministic output.
Qubits: 2 qubits `q[2]`, both measured.
Evolution: Start with |00>. H(q[0]) gives (|00> + |10>)/√2. CNOT(q[0], q[1]) creates |Phi+> = (|00> + |11>)/√2. X(q[1]) converts this to |Psi+> = (|01> + |10>)/√2.
Measurement decoding: CNOT(q[0], q[1]) transforms |Psi+> to (|01> + |11>)/√2. H(q[0]) then maps (|0> + |1>)/√2 ⊗ |1> and (|0> - |1>)/√2 ⊗ |1> to cancel out the |11> component, resulting in |01>.
Probabilities: The final state before measurement is exactly |01>, yielding a 100% probability of measuring `01`.

Check line count: 6 lines. Meets criteria.
Check content: "earlier measured qubit = higher bit", so M(q[0]) M(q[1]) on state |01> gives bitstring "01" (q0=0, q1=1).
Wait, higher bit for earlier measured qubit means q[0] is the higher bit.
Let's verify: state |01> means q[0] = |0>, q[1] = |1>. The bitstring is 0*2^1 + 1*2^0 = 1. Which corresponds to `01` in binary.
Yes. Output string `01` has probability 1.0.
The text says "deterministic output", "yielding a 100% probability of measuring `01`

## isqTrain/3089

- task_id: `isqTrain/3089`
- task_type: `code_generation`
- category: `state_discrimination`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `phase_manipulation`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `5436`

### Prompt

Write isQ code for the following quantum task: an isQ program: prepare |i+> (Y-basis eigenstate), then rotate to computational basis using inv(S) then H, and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare the Y-basis eigenstate |i+⟩ = (|0⟩ + i|1⟩)/√2, rotate it back to the computational basis, and measure.
2. **Qubits**: 1 qubit (`q[0]`) is allocated and measured.
3. **State evolution**:
   - Initial: |0⟩
   - `H(q[0])`: |0⟩ → |+⟩ = (|0⟩ + |1⟩)/√2
   - `S(q[0])`: |+⟩ → |i+⟩ = (|0⟩ + i|1⟩)/√2
   - `inv S(q[0])`: |i+⟩ → |+⟩ = (|0⟩ + |1⟩)/√2 (S† undoes S)
   - `H(q[0])`: |+⟩ → |0⟩
4. **Expected probabilities**: The final state is |0⟩, so measurement yields |0⟩ with probability 1.0.

## isqTrain/3092

- task_id: `isqTrain/3092`
- task_type: `code_generation`
- category: `state_discrimination`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `basis_change`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4813`

### Prompt

Help me write isQ code that an isQ program: create Bell state |Psi-> using H+CNOT and X(q[1]),Z(q[0]), then apply Bell measurement (CNOT+H) to decode, and measure both qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Prepare Bell state |Ψ⁻⟩ and perform Bell measurement to decode it into a deterministic outcome.

**State evolution:**
1. |00⟩ → H(q[0]) → (|00⟩ + |10⟩)/√2
2. → CNOT(q[0], q[1]) → (|00⟩ + |11⟩)/√2 = |Φ⁺⟩
3. → X(q[1]) → (|01⟩ + |10⟩)/√2 = |Ψ⁺⟩
4. → Z(q[0]) → (|01⟩ − |10⟩)/√2 = |Ψ⁻⟩

**Bell measurement:**
5. → CNOT(q[0], q[1]) → (|01⟩ − |11⟩)/√2
6. → H(q[0]) → |11⟩

**Result:** Measurement yields |11⟩ with probability 1.0, as the Bell measurement decodes |Ψ⁻⟩ to a unique computational basis state.

## isqTrain/3090

- task_id: `isqTrain/3090`
- task_type: `code_generation`
- category: `state_discrimination`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `phase_manipulation`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `2494`

### Prompt

Implement a quantum circuit in isQ: an isQ program: prepare |i-> (Y-basis eigenstate), then rotate to computational basis using inv(S) then H, and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare the Y-basis eigenstate |i-> and rotate it to the computational basis for measurement.
2. **Qubits**: 1 qubit (`q[0]`), which is measured.
3. **State evolution**:
   - Start: |0>
   - H(q[0]): |0> → |+> = (|0> + |1>)/√2
   - S(q[0]): |+> → (|0> + i|1>)/√2 = |i+>
   - Z(q[0]): |i+> → (|0> - i|1>)/√2 = |i->
   - inv S(q[0]): S† maps |i-> → (|0> - (-i)i|1>)/√2 = (|0> - |1>)/√2 = |->
   - H(q[0]): |-> → |1>
4. **Expected result**: Final state is |1>, so measurement yields outcome 1 with probability 1.0.

## isqTrain/3244

- task_id: `isqTrain/3244`
- task_type: `code_generation`
- category: `state_discrimination`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5022`

### Prompt

I need an isQ program to an isQ program: prepare state by applying Ry(pi/3), then discriminate by applying Ry(-pi/3) (inverse), then measure. Should return to |0>.

### Chain-of-thought reasoning

## Reasoning
- Goal: Prepare a state via Ry(π/3), then undo it via Ry(-π/3) to recover |0⟩ and measure.
- Qubits: 1 global qubit `q[1]` is used and measured.
- Evolution: Start in |0⟩; apply Ry(π/3)|0⟩ = cos(π/6)|0⟩ + sin(π/6)|1⟩; then apply Ry(-π/3), which is the inverse rotation, returning the state exactly to |0⟩.
- Probabilities: The final state is |0⟩, so measurement yields |0⟩ with probability 1.0.
