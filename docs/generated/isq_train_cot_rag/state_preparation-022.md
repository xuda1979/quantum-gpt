# ISQ training COT RAG corpus: state_preparation shard 22

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3204

- task_id: `isqTrain/3204`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3975`

### Prompt

Code this in isQ: an isQ program: apply Ry(2*pi/5) to a qubit and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply an Ry rotation of angle 2π/5 to a single qubit and measure the result.
2. **Qubits**: 1 qubit (`q[0]`) is used and measured.
3. **State evolution**:
   - Initial state: |0⟩
   - After `Ry(2π/5, q[0])`: The Ry gate rotates the state around the Y-axis, yielding cos(π/5)|0⟩ + sin(π/5)|1⟩.
4. **Expected probabilities**: By the Born rule, P(|0⟩) = cos²(π/5) ≈ 0.6545 and P(|1⟩) = sin²(π/5) ≈ 0.3455, matching the reference values.

## isqTrain/3734

- task_id: `isqTrain/3734`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `103`

### Prompt

Create an isQ quantum circuit that Prepare the 4-qubit GHZ state with phase pi/2:
|GHZ> = (|0000> + e^{i*pi/2}|1111>) / sqrt(2)
Use Hadamard on first qubit, Rz for phase, then CNOT chain. Measure all 4 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare the 4-qubit phase-π/2 GHZ state (|0000⟩ + i|1111⟩)/√2 via H, Rz, and CNOT chain.
2. **Qubits**: 4 qubits q[0..3], all measured.
3. **State evolution**:
   - Start: |0000⟩
   - H(q[0]): (|0000⟩ + |1000⟩)/√2
   - Rz(π/2, q[0]): applies e^{iπ/2}=i phase to |1⟩ component → (|0000⟩ + i|1000⟩)/√2 (up to irrelevant global phase)
   - CNOT(q[0],q[1]): (|0000⟩ + i|1100⟩)/√2
   - CNOT(q[1],q[2]): (|0000⟩ + i|1110⟩)/√2
   - CNOT(q[2],q[3]): (|0000⟩ + i|1111⟩)/√2 ✓
4. **Probabilities**: The final state has equal magnitude amplitudes for |0000⟩ and |1111⟩, so P(|0000⟩) = P(|1111⟩) = |1/√2|² = 0.5.

## isqTrain/1782

- task_id: `isqTrain/1782`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `26`

### Prompt

Implement the following in isQ: Apply H then Z to each of 3 qubits. Measure all. Z phase is invisible in Z-basis measurement.

### Chain-of-thought reasoning

## Reasoning
1.  **Goal**: Apply an H gate followed by a Z gate to each of 3 qubits, then measure them in the computational basis.
2.  **Qubits**: 3 qubits (`q[0]`, `q[1]`, `q[2]`), all measured.
3.  **State Evolution**:
    *   Initialize 3 qubits to $|000\rangle$.
    *   Apply H to all: transforms to an equal superposition over all 8 basis states, $\frac{1}{\sqrt{8}} \sum_{x=0}^{7} |x\rangle$, or equivalently $|+++\rangle$.
    *   Apply Z to all: $Z|+\rangle = |-\rangle$, resulting in $|---\rangle = \frac{1}{\sqrt{8}}(|0\rangle - |1\rangle)^{\otimes 3}$. This introduces relative minus signs for basis states with an odd number of 1s.
4.  **Probabilities**: Measuring in the Z-basis squares the amplitudes. Since $|(\pm 1/\sqrt{8})^2| = 1/8 = 0.125$, the Z phase is invisible, yielding a uniform 12.5% probability for each of the 8 possible outcomes.

## isqTrain/1464

- task_id: `isqTrain/1464`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3366`

### Prompt

Implement the following in isQ: Prepare the computational basis state |01010> on 5 qubits by applying X gates to the appropriate qubits, then measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Prepare the 5-qubit state |01010> and measure it.
2. **Qubits:** 5 qubits are used, and all 5 are measured.
3. **State Evolution:**
   - Initialize 5 qubits to |00000>.
   - Apply X gate to q[1]: flips it to |1>, state becomes |00010>.
   - Apply X gate to q[3]: flips it to |1>, state becomes |01010>.
4. **Probabilities:** The final state is exactly |01010>. Since it is a computational basis state, measurement yields the bitstring "01010" with probability 1.0.

## isqTrain/3778

- task_id: `isqTrain/3778`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `4165`

### Prompt

Write isQ code for the following quantum task: the 5-qubit GHZ state (|00000> + |11111>)/√2 using a for loop for the CNOT chain. Measure all 5 qubits.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Create a 5-qubit GHZ state (|00000⟩ + |11111⟩)/√2 and measure all qubits.
2. Use 5 qubits (q[0]–q[4]), all measured at the end.
3. State evolution:
   - Initialize: |00000⟩
   - H(q[0]): (|0⟩+|1⟩)/√2 ⊗ |0000⟩ = (|00000⟩+|10000⟩)/√2
   - CNOT(q[0],q[1]): (|00000⟩+|11000⟩)/√2
   - CNOT(q[1],q[2]): (|00000⟩+|11100⟩)/√2
   - CNOT(q[2],q[3]): (|00000⟩+|11110⟩)/√2
   - CNOT(q[3],q[4]): (|00000⟩+|11111⟩)/√2
4. The final state has equal amplitude on |00000⟩ and |11111⟩, yielding measurement probabilities P(|00000⟩) = 0.5 and P(|11111⟩) = 0.5.

## isqTrain/3112

- task_id: `isqTrain/3112`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `252`

### Prompt

Implement a quantum circuit in isQ: an isQ program: apply Rx(pi/6) to a single qubit and measure. Expected P(0)=0.9330, P(1)=0.0670.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply an $Rx(\pi/6)$ rotation to a single qubit initialized to $|0\rangle$ and measure its state.
2. **Qubits**: Requires 1 qubit (`q[0]`), which is the only one measured.
3. **State Evolution**: 
   - Start in the initial state $|\psi_0\rangle = |0\rangle$.
   - Apply the $Rx(\pi/6)$ gate, which evolves the state to $|\psi_1\rangle = \cos(\pi/12)|0\rangle - i\sin(\pi/12)|1\rangle$.
4. **Probabilities**: Measuring the final state yields $P(0) = \cos^2(\pi/12) \approx 0.9330$ and $P(1) = \sin^2(\pi/12) \approx 0.0670$.

## isqTrain/3733

- task_id: `isqTrain/3733`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2260`

### Prompt

Help me write isQ code that Prepare the 4-qubit GHZ state with phase pi/4:
|GHZ> = (|0000> + e^{i*pi/4}|1111>) / sqrt(2)
Use Hadamard on first qubit, Rz for phase, then CNOT chain. Measure all 4 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Prepare the 4-qubit GHZ state with phase π/4: |GHZ> = (|0000> + e^{iπ/4}|1111>) / √2 and measure all qubits.
2. **Qubits:** 4 qubits (q[0] to q[3]) are used, all measured.
3. **State Evolution:**
   - Initial state: |ψ₀> = |0000>.
   - H(q[0]): |ψ₁> = (|0> + |1>)/√₂ ⊗ |000> = (|0000> + |1000>) / √2.
   - Rz(π/4, q[0]): Applies a relative phase e^{iπ

## isqTrain/3183

- task_id: `isqTrain/3183`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4092`

### Prompt

Code this in isQ: an isQ program: apply Ry(2*pi/7) to one qubit, then CNOT to a second qubit, creating partial entanglement.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a partially entangled two-qubit state using a Y-rotation followed by CNOT.
2. **Qubits**: 2 qubits (`q[0]`, `q[1]`), both measured.
3. **State evolution**:
   - Start: |00⟩
   - After Ry(2π/7) on q[0]: cos(π/7)|0⟩⊗|0⟩ + sin(π/7)|1⟩⊗|0⟩ = cos(π/7)|00⟩ + sin(π/7)|10⟩
   - After CNOT(q[0], q[1]): cos(π/7)|00⟩ + sin(π/7)|11⟩ (CNOT flips |10⟩ to |11⟩)
4. **Measurement probabilities**: P(|00⟩) = cos²(π/7) ≈ 0.8117, P(|11⟩) = sin²(π/7) ≈ 0.1883. The non-zero angle creates partial (not maximal) entanglement.

## isqTrain/1449

- task_id: `isqTrain/1449`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `4811`

### Prompt

Code this in isQ: Prepare the computational basis state |0111> on 4 qubits by applying X gates to the appropriate qubits, then measure all.

### Chain-of-thought reasoning

## Reasoning
Goal: Prepare the computational basis state |0111> on 4 qubits by flipping qubits 1, 2, and 3.
All 4 qubits are measured after state preparation.
State evolution:
- Initial: |0000>
- After X(q[1]): |0010>
- After X(q[2]): |0110>
- After X(q[3]): |0111>
Measurement yields |0111> with probability 1.0, since the state is a single computational basis state.

## isqTrain/587

- task_id: `isqTrain/587`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `3921`

### Prompt

实现以下量子计算任务（使用isQ）：implements a variant of the ghz_state_preparation pattern using q[6] -> q[7]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

The user wants me to generate reasoning for a GHZ state preparation circuit using qubits q[6] -> q[7]. Wait, that notation is a bit confusing - "q[6] -> q[7]" might mean using 8 qubits (q[0] through q[7]) or it might mean something else.

Analyzing the circuit requirements, it uses 7 qubits (q[0] through q[6]) with a register declaration of `qbit q[7]`. The predicted output measurement probabilities for |0000000> and |0111111>, which are 7-bit states.

But wait, the task says "q[6] -> q[7]" and "expanded qubit register compared to the base version". The circuit should 7 qubits. So maybe the predicted output should actually be 8 qubits?

Let me re-read: "implements a variant of the ghz_state_preparation pattern using q[6] -> q[7]"

Hmm, this is ambiguous. Let me look at the expected measurement probabilities: {|0000000>: 0.5, |0111111>: 0.5}

|0000000> has 7 zeros, and |0111111> has a 0 followed by 6 ones. So this is a 7-qubit GHZ state.

The implementation already shows 7 qubits. The pattern is:
1. Apply H to q[0]
2. Apply CNOT(q[0], q[1])
3. Apply CNOT(q[1], q[2])
4. Apply CNOT(q[2], q[3])
5. Apply CNOT(q[3], q[4])
6. Apply CNOT(q[4], q[5])
7. Measure all qubits

But wait, this only creates entanglement between q[0] and q[1] through q[5]. q[6] is never touched! So the final state would be:
- q[0] through q[5] in (|000000> + |011111>)/√2
- q[6] in |0>

So the measurement probabilities should actually be:
{|0000000>: 0.5, |0111110>: 0.5}

But The predicted output {|0000000>: 0.5, |0111111>: 0.5}. This suggests there should be a CNOT(q[5], q[6]) as well!

Let me re-check The implementation... It has:
- CNOT(q[4], q[5])
- Then M(q)

There's no CNOT(q[5], q[6]). So either:
1. The implementation is incomplete/incorrect
2. The resulting probabilities should be wrong
3. I'm misunderstanding something

Given the task says "using q[6] -> q[7]", maybe the circuit should actually have 8 qubits and include CNOT(q[5], q[6]) and CNOT(q[6], q[7])?

Wait, "q[6] -> q[7]" might mean the CNOT chain goes from q[6] to q[7], implying we need at least 8 qubits.

Let me think about this differently. The circuit should 7 qubits but only creates a 6-qubit GHZ state (q[0] to q[5]). To make a proper 7-qubit GHZ state with all 7 qubits entangled, we need CNOT(q[5], q[6]).

Actually, looking more carefully at the predicted output: {|0000000>: 0.5, |0111111>: 0.5} - this is 7 bits, and the state |0111111> has 6 ones, which means all qubits except the first are in the |1> state when the first is |0>. Wait no, that's not right either.

In a GHZ state, we have (|00...0> + |11...1>)/√2. So for 7 qubits: (|0000000> + |1111111>)/√2.

But The predicted output (|0000000> + |0111111>)/√2. This is strange - it's not a standard GHZ state!

Oh wait, I think I'm misreading the measurement bitstring ordering. the predicted output mentions: "earlier measured qubit = higher bit". So if we measure q[0], q[1], q[2], q[3], q[4], q[5], q[6] in that order with M(q), then:
- q[0] is the highest bit (most significant)
- q[6] is the lowest bit (least significant)

So |0000000> means all qubits are
