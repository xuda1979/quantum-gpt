# ISQ training COT RAG corpus: state_preparation shard 27

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3365

- task_id: `isqTrain/3365`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `427`

### Prompt

Write isQ code for the following quantum task: an isQ program: apply H to odd-indexed qubits only in a 2-qubit register.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply the Hadamard (H) gate to the odd-indexed qubit (q[1]) in a 2-qubit register, leaving the even-indexed qubit untouched.
Qubits: 2 qubits (`q[0]`, `q[1]`), both are measured.
Evolution: Starting in the initial state |00>, applying H to q[1] transforms it from |0> to |+>, resulting in the final state |0>⊗|+> = (1/√2)(|00> + |01>).
Probabilities: The squared amplitudes of the final state yield measurement probabilities of 0.5 for |00> and 0.5 for |01>, while |10> and |11> have zero probability.

## isqTrain/3738

- task_id: `isqTrain/3738`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3155`

### Prompt

帮我写一个isQ程序：Prepare the 5-qubit GHZ state with phase pi:
|GHZ> = (|00000> + e^{i*pi}|11111>) / sqrt(2)
Use Hadamard on first qubit, Rz for phase, then CNOT chain. Measure all 5 qubits.

### Chain-of-thought reasoning

Let me analyze the task of creating a 5-qubit GHZ state with phase π.

Goal: Create the state |GHZ⟩ = (|00000⟩ + e^(iπ)|11111⟩) / √2 = (|00000⟩ - |11111⟩) / √2

Steps:
1. Start with |00000⟩
2. H(q[0]): |0⟩ → |+⟩ = (|0⟩ + |1⟩)/√2, so state is (|00000⟩ + |10000⟩)/√2
3. Rz(π, q[0]): This applies a phase rotation. Rz(θ) = e^(-iθ/2)|0⟩⟨0| + e^(iθ/2)|1⟩⟨1|
   - With θ = π: Rz(π)|0⟩ = e^(-iπ/2)|0⟩ = -i|0⟩, Rz(π)|1⟩ = e^(iπ/2)|1⟩ = i|1⟩
   - But wait, Analyzing the circuit requirements, they use Rz(3.14159265358979 * 4.0 / 4.0) = Rz(π)
   - Actually, the convention for Rz might be different. Let me check.
   
   Standard Rz(θ) = [[e^(-iθ/2), 0], [0, e^(iθ/2)]]
   
   So Rz(π) gives e^(-iπ/2)|0⟩⟨0| + e^(iπ/2)|1⟩⟨1| = -i|0⟩⟨0| + i|1⟩⟨1|
   
   Applying to |+⟩ = (|0⟩ + |1⟩)/√2:
   Rz(π)|+⟩ = (-i|0⟩ + i|1⟩)/√2 = -i(|0⟩ - |1⟩)/√2 = -i|−⟩
   
   Hmm, that's not quite right for what we want. We want e^(iπ)|11111⟩ term.
   
   Actually, looking more carefully at the problem. The reference uses Rz(π * 4/4) = Rz(π).
   
   Let me think about this differently. We want:
   |GHZ⟩ = (|00000⟩ + e^(iπ)|11111⟩)/√2 = (|00000⟩ - |11111⟩)/√2

   After H on q[0]: (|00000⟩ + |10000⟩)/√2
   
   We need to get a phase of e^(iπ) = -1 on the |11111⟩ component.
   
   If we use Rz(π) on q[0], in the standard convention:
   Rz(π) = e^(-iπ/2)|0⟩⟨0| + e^(iπ/2)|1⟩⟨1| = -i|0⟩⟨0| + i|1⟩⟨1|
   
   So state becomes: (-i|00000⟩ + i|10000⟩)/√2 = i(-|00000⟩ + |10000⟩)/√2
   
   After CNOT chain (all controlled by previous qubit):
   i(-|00000⟩ + |11111⟩)/√2
   
   This is equivalent to (|00000⟩ - |11111⟩)/√2 up to global phase i.
   
   Actually wait, let me reconsider. The implementation explicitly has:
   Rz(3.14159265358979 * 4.0 / 4.0, q[0])
   
   This is Rz(π). With the standard convention, this gives:
   After H: (|0⟩ + |1⟩)/√2
   After Rz(π): (-i|0⟩ + i|1⟩)/√2 = i(|1⟩ - |0⟩)/√2
   
   Hmm, but that would give (|11111⟩ - |00000⟩)/√2 after CNOT chain, which equals (-(|00000⟩ - |11111⟩))/√2 = (|11111⟩ - |00000⟩)/√2.
   
   Actually, measurement probabilities don't care about the sign, so both |00000⟩ and |11111⟩ have 0.5 probability.

Let me trace through more carefully:

1. Initial: |00000⟩
2. H(q[0]): (|0⟩ + |1⟩)/√2 ⊗ |0000⟩ = (|00000⟩ + |10000⟩)/√2
3. Rz(π, q[0]): Using Rz(θ) = [[e

## isqTrain/4206

- task_id: `isqTrain/4206`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`, `entanglement`
- source: `isq_train_cot`
- dataset_index: `4073`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[4];

procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. Initial state is |0000>.
2. H(q[0]) puts q[0] into superposition: (|0000> + |1000>)/√2.
3. CNOT(q[0], q[1]) entangles q[1]: (|0000> + |1100>)/√2.
4. CNOT(q[1], q[2]) propagates entanglement: (|0000> + |1110>)/√2.
5. C

### Reference answer

Dominant output states: |0000>, |1111> with probability ~0.50 each

## isqTrain/3111

- task_id: `isqTrain/3111`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `1919`

### Prompt

Code this in isQ: an isQ program: apply H to 6 qubit(s) to create uniform superposition, then measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a uniform superposition over all 2^6 = 64 computational basis states of 6 qubits, then measure all.
2. **Qubits**: 6 qubits declared globally (`q[6]`), all measured at the end.
3. **State evolution**:
   - Initial state: |000000⟩
   - After H(q[0]): (|0⟩+|1⟩)/√2 ⊗ |00000⟩ = (|000000⟩+|000001⟩)/√2
   - After H on all 6 qubits: (1/√2)⁶ Σ_{x∈{0,1}⁶} |x⟩ = (1/8) Σ|x⟩
4. **Expected probabilities**: Each of the 64 basis states has amplitude 1/8, so probability = |1/8|² = 1/64 = 0.015625 for all outcomes.

## isqTrain/4773

- task_id: `isqTrain/4773`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_classical_vars`
- source: `isq_train_cot`
- dataset_index: `2464`

### Prompt

Code this in isQ: implements: classical var variant 3. Declare a global qbit array q of 1 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Demonstrate classical variable usage in isQ by conditionally applying a quantum gate based on a classical integer comparison.
2. **Qubits**: 1 qubit (q[0]) is declared globally and measured.
3. **State evolution**:
   - Initial state: |0>
   - Classical variable `val = 4` satisfies `val > 3`, so H(q[0]) is applied
   - After H gate: |+> = (1/√2)(|0> + |1>)
   - Measurement collapses the superposition
4. **Expected probabilities**: The |+> state yields P(|0>) = |1/√2|² = 0.5 and P(|1>) = |1/√2|² = 0.5, giving equal probability of measuring either outcome.

## isqTrain/1551

- task_id: `isqTrain/1551`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `4321`

### Prompt

Code this in isQ: Apply H gate to each of 6 qubits and measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a uniform superposition over all 64 computational basis states of 6 qubits and measure.
2. **Qubits**: 6 qubits (q[0]–q[5]), all measured.
3. **State evolution**: Start at |000000⟩. Each H gate transforms |0⟩→|+⟩=(|0⟩+|1⟩)/√2, so after all six H gates the state is |++++++⟩ = (1/√2)⁶ Σ|x₁x₂x₃x₄x₅x₆⟩, a uniform superposition over all 2⁶=64 basis states.
4. **Probabilities**: Each of the 64 possible measurement outcomes |000000⟩ through |111111⟩ has probability |(1/√64)|² = 1/64 ≈ 0.015625.

## isqTrain/4300

- task_id: `isqTrain/4300`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `2073`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;

qbit q[2];

procedure main() {
    // |Ψ-> = (|01> - |10>)/sqrt(2)
    X(q[0]); X(q[1]);
    H(q[0]);
    CNOT(q[0], q[1]);
    
    // Measure both qubits
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a concise analysis of an isQ quantum program, predicting the measurement outcomes and explaining the step-by-step quantum state evolution. Output must strictly start with "## Circuit Analysis" and end with the predicted probability distribution. Length should be 3-15 lines.

2.  **Analyze the isQ Code:**
    *   `X(q[0]); X(q[1]);` -> Starts in $|00\rangle$, flips both to $|11\rangle$.
    *   `H(q[0]);` -> Applies Hadamard to qubit 0. State becomes $\frac{1}{\sqrt{2}}(|01\rangle + |11\rangle)$? Wait.
        *   $H|1\rangle = |-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
        *   So $|1\rangle_0 |1\rangle_1 \to \frac{1}{\sqrt{2}}(|0\rangle_0 - |1\rangle_0)|1\rangle_1 = \frac{1}{\sqrt{2}}(|01\rangle - |11\rangle)$.
    *   `CNOT(q[0], q[1]);` -> Control is q[0], target is q[1].
        *   Applies to $\frac{1}{\sqrt{2}}(|01\rangle - |11\rangle)$.
        *   $|01\rangle$ (control=0) remains $|01\rangle$.
        *   $|11\rangle$ (control=1) becomes $|10\rangle$.
        *   Result: $\frac{1}{\sqrt{2}}(|01\rangle - |10\rangle)$. This matches the comment: $|\Psi^-\rangle$.
    *   `H(q[0]); Z(q[0]); H(q[0]);` -> This is $HZH$.
        *   We know $HZH = X$. (Because $X = HZH$).
        *   So, apply $X$ to qubit 0.
    *   Apply $X$ to $|\Psi^-\rangle = \frac{1}{\sqrt{2}}(|01\rangle - |10\rangle)$.
        *   $X_0$ flips the state of qubit 0.
        *   $|01\rangle \to |11\rangle$.
        *   $|10\rangle \to |00\rangle$.
        *   Resulting state: $\frac{1}{\sqrt{2}}(|11\rangle - |00\rangle)$.
        *   Wait, is it $-|00\rangle + |11\rangle$? Yes, $X_0(|01\rangle - |10\rangle) = |11\rangle - |00\rangle$.
    *   Wait, let's re-verify the $HZH = X$ on $|\Psi^-\rangle$.
        *   $|\Psi^-\rangle = \frac{1}{\sqrt{2}}(|01\rangle - |10\rangle)$.
        *   Apply $X$ on qubit 0: $X_0 |\Psi^-\rangle = \frac{1}{\sqrt{2}}(|11\rangle - |00\rangle)$.
        *   Measurement probabilities: $|00\rangle$ has prob $1/2$, $|11\rangle$ has prob $1/2$.
        *   Let's check the predicted output in the prompt: `{|00>: 0.4999999999999999, |11>: 0.5}`. Matches perfectly.

3.  **Draft the Explanation:**
    *   *Step 1:* Initialize qubits to $|00\rangle$. Apply $X$ to both to get $|11\rangle$.
    *   *Step 2:* Apply $H$ to $q[0]$ to get $\frac{1}{\sqrt{2}}(|01\rangle - |11\rangle)$.
    *   *Step 3:* Apply $CNOT(q[0], q[1])$ to create the Bell state $|\Psi^-\rangle = \frac{1}{\sqrt{2}}(|01\rangle - |10\rangle)$.
    *   *Step 4:* Apply $H, Z, H$ to $q[0]$, which is equivalent to applying $X$ to $q[0]$.
    *   *Step 5:* The final state becomes $\frac{1}{\sqrt{2}}(-|00\rangle + |11\rangle)$.
    *   *Step 6:* Measurements yield $|00\rangle$ and $|11

### Reference answer

{'predicted_probs': {'00': 0.5, '11': 0.5}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|00>) = 0.5000, P(|11>) = 0.5000.'}

## isqTrain/3219

- task_id: `isqTrain/3219`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1602`

### Prompt

实现以下量子计算任务（使用isQ）：an isQ program: apply Rx(1*pi/2) then Ry(1*pi/4) to a qubit and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply sequential rotations Rx(π/2) and Ry(π/4) to a single qubit, then measure it.
2. **Qubits**: 1 qubit is needed; q[0] is measured.
3. **State evolution**:
   - Start: |ψ⟩ = |0⟩
   - After Rx(π/2): |ψ⟩ = (|0⟩ - i|1⟩)/√2 (equal superposition from X/2 rotation)
   - After Ry(π/4): Ry(π/4) = [[cos(π/8), -sin(π/8)], [sin(π/8), cos(π/8)]]
     - α = [cos(π/8) + i·sin(π/8)]/√2
     - β = [sin(π/8) - i·cos(π/8)]/√2
4. **Probabilities**: P(|0⟩) = |α|² = [cos²(π/8) + sin²(π/8)]/2 = 0.5, P(|1⟩) = |β|² = [sin²(π/8) + cos²(π/8)]/2 = 0.5, since Rx(π/2) creates equal amplitudes and Ry(π/4) preserves their magnitudes.

## isqTrain/3744

- task_id: `isqTrain/3744`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `967`

### Prompt

Create an isQ quantum circuit that Prepare a 2-qubit product state by applying Ry(0.0) to q[0] and Ry(1.0) to q[1]. Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare a 2-qubit product state by applying Ry rotations to two separate qubits.
2. **Qubits**: 2 qubits are allocated (`q[0]`, `q[1]`), and both are measured.
3. **State Evolution**:
   - Initial state is |00>.
   - Applying `Ry(0.0)` to `q[0]` does nothing, leaving it in the |0> state.
   - Applying `Ry(1.0)` to `q[1]` rotates it from |0> to cos(0.5)|0> + sin(0.5)|1>.
   - The final 2-qubit state is |0> ⊗ (cos(0.5)|0> + sin(0.5)|1>) = cos(0.5)|00> + sin(0.5)|01>.
4. **Measurement Probabilities**: Measuring the final state yields probabilities P(|00>) = cos²(0.5) ≈ 0.770151 and P(|01>) = sin²(0.5) ≈ 0.229849. P(|10>) = P(|11>) = 0.

## isqTrain/3131

- task_id: `isqTrain/3131`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `2746`

### Prompt

Code this in isQ: an isQ program: use a for loop to apply H to each of 6 qubits, then measure all with a for loop.

### Chain-of-thought reasoning

## Reasoning
Goal: Create a uniform superposition over all 64 computational basis states of 6 qubits by applying H to each, then measure all.
Qubits: 6 qubits `q[0]` through `q[5]`, all measured.

State evolution:
1. Initial: |000000⟩
2. After H on q[0]: (|0⟩+|1⟩)/√2 ⊗ |00000⟩ = (|000000⟩+|100000⟩)/√2
3. After H on all 6: ((|0⟩+|1⟩)/√2)^⊗6 = (1/8) Σ|x⟩ for all x∈{0,1}^6

Each of the 64 basis states has amplitude 1/8, giving probability |1/8|² = 1/64 ≈ 0.015625 for each outcome.
