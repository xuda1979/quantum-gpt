# ISQ training COT RAG corpus: state_preparation shard 14

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/2476

- task_id: `isqTrain/2476`
- task_type: `code_equivalence`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `entanglement`, `global_phase`
- source: `isq_train_cot`
- dataset_index: `4225`

### Prompt

判断以下两段isQ代码是否产生相同的测量结果：

代码1：
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

代码2：
```isq
import std;
qbit q[3];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    H(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A**: Applies H to q[0], then CNOT(q[0], q[1]), then CNOT(q[1], q[2]), creating the GHZ state (|000⟩ + |111⟩)/√2.
2. **Program B**: Applies GPhase(0.0), which is the identity (a trivial global phase of 0), then the same H and CNOT sequence, producing the identical state.
3. **Key difference**: Program B adds GPhase(0.0), which has no effect.
4. **Measurement probabilities**: Identical, since GPhase(0.0) = I introduces no change.
Verdict: Yes

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/556

- task_id: `isqTrain/556`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `4830`

### Prompt

Write isQ code for the following quantum task: implements a variant of the state_preparation pattern using q[5] -> q[6]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare the computational basis state |000101⟩ on a 6-qubit register using X gates.
2. **Qubits**: 6 qubits (q[0]–q[5]), all measured at the end.
3. **State evolution**:
   - Initial state: |000000⟩
   - After `X(q[0])`: |000001⟩ (flips qubit 0 to |1⟩)
   - After `X(q[2])`: |000101⟩ (flips qubit 2 to |1⟩)
4. **Expected probabilities**: The final state is |000101⟩ with probability 1.0, as no superposition is created—only deterministic bit flips on qubits 0 and 2.

## isqTrain/4787

- task_id: `isqTrain/4787`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `superposition`, `isq_syntax_while_loop`, `isq_syntax_if_else`
- source: `isq_train_cot`
- dataset_index: `3711`

### Prompt

用isQ实现implements: while-loop with classical vars variant 3. Declare a global qbit array q of 2 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement a while-loop that applies H twice per iteration (identity operation) for 4 iterations, then a final H to q[0], demonstrating classical variable tracking in a quantum program.

2. **Qubits**: 2 qubits (q[0], q[1]), both measured.

3. **State evolution**:
   - Initial state: |00⟩
   - Each loop iteration applies H(q[0]) twice; since H² = I, state remains |00⟩ after all 4 iterations
   - Final H(q[0]) transforms |00⟩ → (1/√2)(|00⟩ + |10⟩) = |+0⟩
   - q[1] is never operated on, stays |0⟩

4. **Expected probabilities**: The final state (1/√2)(|00⟩ + |10⟩) yields P(|00⟩) = 0.5 and P(|10⟩) = 0.5, since measuring q[0] gives 0 or 1 with equal probability while q[1] is always 0.

## isqTrain/3896

- task_id: `isqTrain/3896`
- task_type: `bug_fix`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `2095`

### Prompt

这段isQ代码有bug，帮我找出并修复：

```
import std;
// 2-qubit state via Ry rotations: Ry(2.0 * 0.5) ⊗ Ry(1.0)
qbit q[2];

procedure main() {
    // Apply rotations to create product state
    Ry(0.5, q[0]);
    Ry(1.0, q[1]);
    // Measure
    M(q[0]); M(q[1]);
}

``` (bug type: wrong parameter)

### Chain-of-thought reasoning

The buggy code has:

The comment says `Ry(2.0 * 0.5) ⊗ Ry(1.0)`, which is `Ry(1.0) ⊗ Ry(1.0)`. But looking at the expected measurement probabilities and the corrected version, the fix keeps `Ry(0.5, q[0])` and `Ry(1.0, q[1])`.

Wait, let me look more carefully. The comment in the buggy code says `Ry(2.0 * 0.5) ⊗ Ry(1.0)`, meaning it should be `Ry(1.0)` on q[0] and `Ry(1.0)` on q[1]. But the corrected version keeps `Ry(0.5, q[0])` and `Ry(1.0, q[1])`.

Hmm, let me reconsider. The original task says "2-qubit Ry product state: (0.5, 1.0)". So the parameters should be 0.5 and 1.0.

The buggy code has `Ry(0.5, q[0])` and `Ry(1.0, q[1])` - which matches the original task description.

Wait, but the comment says `Ry(2.0 * 0.5)` which equals `Ry(1.0)`. So maybe the bug is in the comment? Or maybe the first parameter should be 1.0 instead of 0.5?

Let me verify the probabilities. 

For Ry(0.5) on q[0]:
- cos²(0.25) = cos²(0.25) ≈ (0.9689)² ≈ 0.9388
- sin²(0.25) = sin²(0.25) ≈ (0.2474)² ≈ 0.0612

Wait, Ry(θ)|0⟩ = cos(θ/2)|0⟩ + sin(θ/2)|1⟩

For Ry(0.5): cos(0.25) ≈ 0.9689, sin(0.25) ≈ 0.2474
- P(|0⟩) = 0.9388, P(|1⟩) = 0.0612

For Ry(1.0): cos(0.5) ≈ 0.8776, sin(0.5) ≈ 0.4794
- P(|0⟩) = 0.7702, P(|1⟩) = 0.2298

Expected:
- |00⟩: 0.723011 → 0.9388 × 0.7702 ≈ 0.7231 ✓
- |01⟩: 0.21578 → 0.9388 × 0.2298 ≈ 0.2158 ✓
- |10⟩: 0.04714 → 0.0612 × 0.7702 ≈ 0.0471 ✓
- |11⟩: 0.014069 → 0.0612 × 0.2298 ≈ 0.0141 ✓

So the predicted output match Ry(0.5) ⊗ Ry(1.0). The code already has this. But the task says there's a bug...

Hmm, looking again at the buggy code and the "correct" code - they look identical! The only difference is the comment changed from `Ry(2.0 * 0.5) ⊗ Ry(1.0)` to `Ry(0.5) ⊗ Ry(1.0)`.

Wait, maybe the bug is that the comment incorrectly suggests `Ry(2.0 * 0.5)` = `Ry(1.0)`, implying the first gate should be `Ry(1.0)` not `Ry(0.5)`. But the corrected version keeps `Ry(0.5)`.

Actually, I think the bug is in the comment, not the code itself. The comment says `Ry(2.0 * 0.5)` which equals `Ry(1.0)`, but the actual code uses `Ry(0.5)`. The fix is correcting the comment to match the intended behavior from the task description.

Actually wait - looking more carefully, the buggy code and correct code differ only in the comment. But the task says "wrong parameter" bug type. 

Let me re-read...

## isqTrain/565

- task_id: `isqTrain/565`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `5405`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[5];

procedure main() {
    X(q[0]);
    X(q[1]);
    X(q[3]);
    M(q);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes a 5-qubit register `q[5]` to the state |00000>.
2. An X gate is applied to `q[0]`, `q[1]`, and `q[3]`, flipping their states from |0> to |1>.
3. Qubits `q[2]` and `q[4]` are left unchanged, remaining in the |0> state.
4. The final quantum state before measurement is |01011> (where `q[4]` is the most significant bit and `q[0]` is the least significant bit).
5. Measurement deterministically yields this exact classical bitstring.

Predicted probability distribution: {|01011>: 1.0}

### Reference answer

{'predicted_probs': {'11': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/184. Dimension: predict probabilities for reference circuit.'}

## isqTrain/1548

- task_id: `isqTrain/1548`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `6`

### Prompt

用isQ实现Apply H gate to each of 3 qubits and measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply an H gate to each of 3 qubits and measure them to create an equal superposition of all possible 3-bit states.
2. **Qubits**: 3 qubits (`q[0]`, `q[1]`, `q[2]`), all of which are measured.
3. **State Evolution**:
   - Initialize to $|000\rangle$.
   - Apply H to `q[0]`: evolves to $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)|00\rangle = |+\rangle|00\rangle$.
   - Apply H to `q[1]`: evolves to $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)|0\rangle = |+\rangle|+\rangle|0\rangle$.
   - Apply H to `q[2]`: evolves to $\frac{1}{\sqrt{8}}\sum_{x=0}^{7}|x\rangle = |+\rangle|+\rangle|+\rangle$.
4. **Probabilities**: The final state is an equal superposition of all 8 basis states ($|000\rangle$ to $|111\rangle$). Measuring this state yields any of the 8 possible outcomes with an identical probability of $|1/\sqrt{8}|^2 = 0.125$.

## isqTrain/1550

- task_id: `isqTrain/1550`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `4133`

### Prompt

帮我写一个isQ程序：Apply H gate to each of 5 qubits and measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply Hadamard to 5 qubits, creating an equal superposition over all 32 basis states, then measure.
2. **Qubits**: 5 qubits q[0..4], all measured.
3. **State evolution**:
   - Initial: |ψ₀⟩ = |00000⟩
   - After H on each: |ψ⟩ = (|0⟩+|1⟩)/√2 ⊗ ... ⊗ (|0⟩+|1⟩)/√2 = (1/√32) Σ_{x∈{0,1}⁵} |x⟩
4. **Probabilities**: Each basis state has |1/√32|² = 1/32 = 0.03125 probability.

## isqTrain/637

- task_id: `isqTrain/637`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3798`

### Prompt

Implement a quantum circuit in isQ: implements the state_preparation pattern using an alternative gate decomposition (CNOT -> H CZ H). The circuit must produce the same output as the standard decomposition.

### Chain-of-thought reasoning

Looking at this task, I need to analyze the circuit and generate reasoning for it. But wait - the task says to write an isQ program implementing state_preparation with CNOT -> H CZ H decomposition. But then it gives a circuit implementation already.

Let me re-read... The task is code_generation type, and it provides a circuit implementation. The predicted output just the reasoning section.

Let me analyze the circuit:

1. Start with |000⟩
2. Ry(1.910633236, q[0]) - This rotates q[0] around Y axis
3. ctrl H(q[0], q[1]) - Controlled-Hadamard, controlled by q[0], target q[1]
4. H(q[2]) - Hadamard on q[2]
5. CZ(q[1], q[2])
6. H(q[2])
7. H(q[1])
8. CZ(q[0], q[1])
9. H(q[1])
10. X(q[0])

The CNOT decomposition H CZ H is used:
- CNOT(c, t) = H(t) CZ(c, t) H(t)

So CZ(q[1], q[2]) between H gates on q[2] is effectively CNOT(q[1], q[2])
And CZ(q[0], q[1]) between H gates on q[1] is effectively CNOT(q[0], q[1])

Expected probabilities: {|001⟩: 1/3, |010⟩: 1/3, |100⟩: 1/3}

So the final state (before measurement) should give equal 1/3 probability for these three states.

Let me trace through:

1. Initial: |000⟩
2. Ry(1.910633236, q[0]): Ry(1.910633236) ≈ Ry(1.910633236)
   - cos(1.910633236/2) ≈ cos(0.9553) ≈ 0.5774 ≈ 1/√3
   - sin(1.910633236/2) ≈ sin(0.9553) ≈ 0.8165 ≈ √(2/3)
   - So state becomes: (1/√3)|000⟩ + (√(2/3))|100⟩ = (1/√3)|0⟩ + (√(2/3))|1⟩ on q[0]
   
3. ctrl H(q[0], q[1]): When q[0] is |1⟩, apply H to q[1]
   - (1/√3)|000⟩ + (√(2/3)) H on q[1]|100⟩
   - = (1/√3)|000⟩ + (√(2/3))(1/√2)(|100⟩ + |110⟩)
   - = (1/√3)|000⟩ + (1/√3)|100⟩ + (1/√3)|110⟩

4. H(q[2]): Apply Hadamard to q[2]
   - (1/√3)(|000⟩ + |001⟩)/√2 + (1/√3)(|100⟩ + |101⟩)/√2 + (1/√3)(|110⟩ + |111⟩)/√2
   - Hmm, this is getting complicated. Let me think about this differently.

Actually, looking at the CNOT -> H CZ H decomposition:
- The H-CZ-H on q[2] around CZ(q[1], q[2]) effectively implements CNOT(q[1], q[2])
- The H-CZ-H on q[1] around CZ(q[0], q[1]) effectively implements CNOT(q[0], q[1])

So the circuit with standard CNOTs would be:
1. Ry(1.910633236, q[0])
2. CNOT(q[0], q[1]) - but wait, it's ctrl H, not CNOT

Hmm, let me re-read. The ctrl H(q[0], q[1]) is a controlled-Hadamard, not a CNOT.

Let me trace more carefully:

After Ry on q[0]: (1/√3)|000⟩ + √(2/3)|100⟩

After ctrl H: This is a controlled-Hadamard with control q[0] and target q[1]
- When control is |0⟩, nothing happens
- When control is |1⟩, H is applied to target
- Result: (1/√3)|000⟩ + √(2/3) * (1/√2)(|100⟩ + |110⟩)
-

## isqTrain/420

- task_id: `isqTrain/420`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `390`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;

qbit q[2];

procedure main() {
    // |Ψ-> = (|01> - |10>)/sqrt(2)
    X(q[0]); X(q[1]);
    H(q[0]);
    CNOT(q[0], q[1]);
    
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Output prediction for a given isQ program.
    *   Input Program:
        
    *   Expected format: "## Circuit Analysis" section, 3-15 lines, using Dirac notation, no code blocks, ending with predicted probability distribution.
    *   Expected outcome: As given in the prompt, it should be close to `|01>` and `|10>` with 50% probability each. Wait, let's trace it.

2.  **Trace the State:**
    *   Initial state: $|00\rangle$
    *   After `X(q[0]); X(q[1]);`: $|11\rangle$
    *   After `H(q[0]);`: $\frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) \otimes |1\rangle = \frac{1}{\sqrt{2}}(|01\rangle - |11\rangle)$
    *   After `CNOT(q[0], q[1]);` (control=q[0], target=q[1]):
        $|01\rangle \to |01\rangle$ (Wait, q[0] is 0, q[1] is 1, so it stays $|01\rangle$. Let's check: $|0\rangle_{ctrl}|1\rangle_{tgt} \to |0\rangle_{ctrl}|1\rangle_{tgt}$)
        $|11\rangle \to |10\rangle$ (q[0] is 1, q[1] is 1, so it flips to $|10\rangle$)
    *   Final state: $\frac{1}{\sqrt{2}}(|01\rangle - |10\rangle)$. This is the $|\Psi^-\rangle$ Bell state.

3.  **Format the Output:**
    *   Start with "## Circuit Analysis".
    *   Briefly state the operations: X on both, H on q[0], CNOT(q[0], q[1]).
    *   Step-by-step state:
        *   Start: $|00\rangle$
        *   $X(q[0]), X(q[1])$: $|11\rangle$
        *   $H(q[0])$: $\frac{1}{\sqrt{2}}(|01\rangle - |11\rangle)$ (Remember $H|1\rangle = |-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$)
        *   $CNOT(q[0], q[1])$: $\frac{1}{\sqrt{2}}(|01\rangle - |10\rangle)$
    *   Final state is the singlet state $|\Psi^-\rangle$.
    *   Predicted probabilities: $P(|01\rangle) = 0.5$, $P(|10\rangle) = 0.5$.

4.  **Refine Text (concise, 3-8 lines usually, up to 15):**
    ## Circuit Analysis
    1. **Operations**: The circuit initializes two qubits, applies an X gate to both, an H gate to q[0], and a CNOT with q[0] as control and q[1] as target.
    2. **State Evolution**:
       - Initial state: $|00\rangle$
       - After X gates: $|11\rangle$
       - After H gate: $\frac{1}{\sqrt{2}}(|01\rangle - |11\rangle)$
       - After CNOT: $\frac{1}{\sqrt{2}}(|01\rangle - |10\rangle)$
    3. **Final State**: The system is in the Bell state $|\Psi^-\rangle$.
    4. **Probabilities**: Measuring yields $|01\rangle$ and $|10\rangle$ with equal probability.
    Predicted probability distribution: {|01>: 0.5, |10>: 0.5}

5.  **Check Constraints:**
    *   Starts with "## Circuit Analysis".
    *   Uses Dirac notation.
    *   3-15 lines.
    *   No code blocks.
    *   Ends with predicted probability distribution.
    *   Measured qubits: q[0] and q[1]. In isQ `--probs` output, if both measured, format is typically big-endian (q[0] is higher bit). The keys `01` and `10` match my manual derivation. Note

### Reference answer

{'predicted_probs': {'1': 0.5000000000000001, '2': 0.4999999999999999}, 'explanation': 'Parametric variant of isqHumanEval/123. Dimension: predict probabilities for reference circuit.'}

## isqTrain/412

- task_id: `isqTrain/412`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `1960`

### Prompt

Write an isQ program that implements the bell_state_preparation pattern but with a different initial state preparation (flip q[[1]] -> q[0]).

### Chain-of-thought reasoning

Let me analyze this task carefully.

The task asks me to implement a bell_state_preparation pattern but with a different initial state preparation: flip q[[1]] -> q[0].

Analyzing the circuit requirements:
1. It starts with |00⟩
2. Applies H(q[0]) → (|0⟩ + |1⟩)/√2 ⊗ |0⟩ = (|00⟩ + |10⟩)/√2
3. Applies X(q[0]) → flips q[0], so (|10⟩ + |00⟩)/√2 = (|00⟩ + |10⟩)/√2

Wait, let me recalculate:
- Initial: |00⟩
- H(q[0]): (|0⟩ + |1⟩)/√2 ⊗ |0⟩ = (|00⟩ + |10⟩)/√2
- X(q[0]): (|1⟩ + |0⟩)/√2 ⊗ |0⟩ = (|10⟩ + |00⟩)/√2 = (|00⟩ + |10⟩)/√2

Hmm, that's the same state. Let me think again...

Actually wait, H followed by X:
- H|0⟩ = |+⟩ = (|0⟩ + |1⟩)/√2
- X|+⟩ = X(|0⟩ + |1⟩)/√2 = (|1⟩ + |0⟩)/√2 = |+⟩

So after H then X on q[0], we have |+⟩|0⟩ = (|00⟩ + |10⟩)/√2

Then CNOT(q[0], q[1]):
- |00⟩ → |00⟩
- |10⟩ → |11⟩

Final state: (|00⟩ + |11⟩)/√2

This is the standard Bell state Φ+.

The expected measurement probabilities are {|00⟩: 0.5, |11⟩: 0.5}, which confirms this.

Now the task says "flip q[[1]] -> q[0]". This is a bit confusing. Let me re-read it.

"Write an isQ program that implements the bell_state_preparation pattern but with a different initial state preparation (flip q[[1]] -> q[0])."

I think the original pattern might have been to prepare q[1] in some state, but now we flip to use q[0] instead. Or maybe the original had X(q[1]) and now we use X(q[0])?

Analyzing the circuit requirements, it has X(q[0]) which seems to be the "different" preparation. The standard Bell state preparation is usually:
1. H(q[0])
2. CNOT(q[0], q[1])

This gives (|00⟩ + |11⟩)/√2.

To get Ψ+ = (|01⟩ + |10⟩)/√2, you'd typically:
1. H(q[0])
2. X(q[1]) to flip the second qubit
3. CNOT(q[0], q[1])

Or:
1. X(q[0]) to start with |10⟩
2. H(q[0])
3. CNOT(q[0], q[1])

Let me verify: Starting from |10⟩:
- H(q[0]): (|0⟩ - |1⟩)/√2 ⊗ |0⟩ = (|00⟩ - |10⟩)/√2

Wait that's |−⟩|0⟩, not right for Ψ+.

Actually The circuit should a comment saying it creates |Ψ+⟩ = (|01⟩ + |10⟩)/√2, but let me trace through:

1. Start: |00⟩
2. H(q[0]): (|00⟩ + |10⟩)/√2
3. X(q[0]): (|10⟩ + |00⟩)/√2 = (|00⟩ + |10⟩)/√2

Hmm, X applied to (|0⟩ + |1⟩)/√2 gives (|1⟩ + |0⟩)/√2 which is the same state.

4. CNOT(q[0], q[1]): (|00⟩ + |11⟩)/√2

So the final state is |Φ+⟩ = (|00⟩ + |11⟩)/√2, not |Ψ+⟩.

the predicted output confirm this: {|00⟩: 0.5, |11⟩: 0.5}.

So the comment In the implementation is wrong about which Bell state it creates.

Anyway, my task is to generate the reasoning, not the code. Let me write the reasoning for this circuit:

1. Goal: Prepare a Bell state using H and X gates on q[0], then CNOT with q[1]
2. 2 qubits needed, both measured
3. State evolution:
