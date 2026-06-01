# ISQ training COT RAG corpus: state_preparation shard 21

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3395

- task_id: `isqTrain/3395`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `261`

### Prompt

Implement a quantum circuit in isQ: an isQ program: in a 5-qubit register, apply X then H to q[2] only. Other qubits stay |0>. Measure all.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Write an isQ program applying X then H to q[2] in a 5-qubit register, measuring all. Wait, the prompt actually says "Generate a reasoning section that explains..." for a code_generation task. It already provides The implementation. I need to output *only* the reasoning section.
    *   Goal: Apply X then H to q[2], measure all.
    *   Reasoning constraints: 3-8 lines, precise, start with "## Reasoning", NO isQ code blocks, use Dirac notation.

2.  **Analyze the Quantum Circuit:**
    *   Initial state: $|00000\rangle$
    *   Apply X to q[2]: $X|0\rangle = |1\rangle \implies |00010\rangle$ (assuming q[4]q[3]q[2]q[1]q[0] or similar standard ordering, let's stick to the qubits indexed 0 to 4, so q[2] is the third qubit. Let's write it as $|0\rangle_4|0\rangle_3|1\rangle_2|0\rangle_1|0\rangle_0$ or simply state it changes the 3rd qubit to $|1\rangle$. Wait, the prompt says measurement probabilities are $\{|00000\rangle: 0.5, |00100\rangle: 0.5\}$ for bitstring, meaning q[2] is the middle bit in the string, i.e., $q_4 q_3 q_2 q_1 q_0$. If $q_2=1$, it's 00100).
    *   Apply H to q[2]: $H|1\rangle = |-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
    *   Final state: $\frac{1}{\sqrt{2}}(|00000\rangle - |00100\rangle)$.
    *   Measurement: 50% chance for $|00000\rangle$, 50% chance for $|00100\rangle$. (Absolute square removes the phase).

3.  **Draft the Reasoning:**
    *   *Goal:* Apply X and H gates to the 3rd qubit (q[2]) of a 5-qubit register, then measure all qubits.
    *   *Qubits:* 5 qubits (q[0] to q[4]), all are measured.
    *   *Evolution:*
        1.  Initial state is $|00000\rangle$.
        2.  `X(q[2])` flips q[2] to $|1\rangle$, changing the state to $|00100\rangle$.
        3.  `H(q[2])` applies a Hadamard gate to q[2], transforming $|1\rangle$ to $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
        4.  The resulting system state is $\frac{1}{\sqrt{2}}(|00000\rangle - |00100\rangle)$.
    *   *Probabilities:* Measuring this state yields a 50% probability for $|00000\rangle$ and 50% for $|00100\rangle$, as global/relative phases do not affect measurement probabilities.

4.  **Refine and Format:**
    *   Check constraints: 3-8 lines, precise, Dirac notation, NO code blocks.
    *   Line 1: ## Reasoning
    *   Line 2: The goal is to apply an X gate followed by an H gate to the third qubit (q[2]) in a 5-qubit register, leaving all other qubits in their initial state, and then measure all qubits.
    *   Line 3: We need 5 qubits (q[0] to q[4]), and all are measured to extract the classical outcome.
    *   Line 4: Starting from the ground state $|00000\rangle$, the X gate on q[2] flips it to $|1\rangle$, evolving the state to $|00100\rangle$.
    *   Line 5: The H gate transforms q[2]'s state from $|1\rangle$ to $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$, making the full system state $\frac{1}{\sqrt{2}}(|00000\rangle - |00100\rangle)$.
    *   Line 6: Because measurement probabilities depend on the squared amplitudes

## isqTrain/1759

- task_id: `isqTrain/1759`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3697`

### Prompt

Write an isQ program that Prepare a linear cluster state on 6 qubits: apply H to all, then CZ between consecutive pairs.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Prepare a 6-qubit linear cluster state by applying Hadamard gates to all qubits followed by CZ gates between consecutive pairs.

2. Qubits needed: 6 (q[0]–q[5]), all measured at the end.

3. State evolution:
   - Initial: |000000⟩
   - After H on all 6 qubits: |++++++⟩ = (1/8)Σ_x |x⟩, an equal superposition over all 64 basis states with amplitude +1/8 each.
   - Each CZ(q[i], q[i+1]) applies a phase of -1 when both qubits are in |1⟩. The sequence CZ(q[0],q[1]), CZ(q[1],q[2]), CZ(q[2],q[3]), CZ(q[3],q[4]), CZ(q[4],q[5]) introduces entanglement with phase factors determined by consecutive bit pairs.
   - Final state: (1/8)Σ_x (-1)^(x₀x₁ + x₁x₂ + x₂x₃ + x₃x₄ +

## isqTrain/575

- task_id: `isqTrain/575`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `878`

### Prompt

Implement a quantum circuit in isQ: implements a variant of the ghz_state_preparation pattern using q[3] -> q[5]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a 3-qubit GHZ state on q[3]-q[5] using an expanded 6-qubit register, leaving q[0]-q[2] in |0⟩.
2. **Qubits**: 6 total (q[0]-q[5]), all measured; GHZ entanglement on q[3], q[4], q[5].
3. **State evolution**:
   - Initial: |000000⟩
   - H(q[3]): |000⟩⊗(|0⟩+|1⟩)/√2 ⊗|00⟩ = (|000000⟩+|000100⟩)/√2
   - CNOT(q[3],q[4]): (|000000⟩+|000110⟩)/√2
   - CNOT(q[4],q[5]): (|000000⟩+|000111⟩)/√2
4. **Expected probabilities**: Equal superposition of |000000⟩ and |000111⟩ → each with probability 0.5.

## isqTrain/570

- task_id: `isqTrain/570`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `37`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[5];

procedure main() {
    X(q[4]);
    M(q);
}
```

### Chain-of-thought reasoning

The user wants a circuit analysis for the given isQ program.
The program:
1. Declares a 5-qubit register `q`.
2. Applies `X` gate to `q[4]`.
3. Measures all qubits `q`.

State evolution:
- Initial state: $|00000\rangle$
- After `X(q[4])`: $|00001\rangle$
Wait, isQ indexing for bitstrings usually has earlier measured qubit as higher bit.
"M(q)" measures all qubits. The prompt says: "earlier measured qubit = higher bit".
So if `q` is `[q[0], q[1], q[2], q[3], q[4]]`, the bitstring is `q[0] q[1] q[2] q[3] q[4]`.
In standard quantum notation, $|q_0 q_1 q_2 q_3 q_4\rangle$ corresponds to q[0] being the highest bit (leftmost).
Wait, let me double check the expected measurement probabilities.
"Expected measurement probabilities: {|10000>: 1.0}"
Ah! The predicted output `|10000>`.
This implies `q[4]` is the *highest* bit, or wait...
If `q[0]` is highest, `X(q[4])` would give `|00001>`.
If `q[4]` is highest, `X(q[4])` would give `|10000>`.
But the prompt says: "earlier measured qubit = higher bit".
Wait, if `M(q)` is called, `q` is the array `[q[0], q[1], q[2], q[3], q[4]]`.
If earlier measured qubit is higher bit, then `q[0]` is highest, `q[4]` is lowest. So `X(q[4])` gives `|00001>`.
Why does the Expected measurement probabilities say `{|10000>: 1.0}`?
Let me re-read carefully: "Expected measurement probabilities: {|10000>: 1.0}"
Is it possible that "earlier measured qubit = higher bit" means if you measure `M(q)`, the first qubit in the array is the highest bit?
Yes. But then X(q[4]) flips the lowest bit.
Wait, if Expected is `|10000>`, maybe `X(q[4])` flips the highest bit?
Let's reconsider: is `q[4]` considered the 5th qubit, which is at index 4.
Could `10000` mean `q[4]` is the highest bit?
If `|10000>` is the predicted output, then the bit for `q[4]` is `1`.
If `q[4]` is the highest bit, it means `q[4]` is the "earlier measured qubit"?
Wait, the isQ syntax reference says: "--probs output: array indexed by measurement bitstring (earlier measured qubit = higher bit)."
Wait, let's look at the problem carefully.
"Expected measurement probabilities: {|10000>: 1.0}"
Wait, is the predicted output `10000` because `q[4]` is the 4th index?
If I have 5 qubits, index 0 to 4. If `X(q[4])` results in `|10000>`, then `q[4]` is the left-most bit.
But "earlier measured qubit = higher bit" implies `M(q)` measures `q[0]` first, so `q[0]` is the highest bit.
Let me check this discrepancy.
If `q[0]` is the highest bit, `X(q[4])` gives `00001`.
If `q[4]` is the highest bit, `X(q[4])` gives `10000`.
Let's search my knowledge base for isQ bit ordering.
In isQ, typically the qubit array is `q[0]` to `q[N-1]`.
If the predicted output is `10000`, maybe `q[0]` is the lowest bit and `q[4]` is the highest bit?
Let me check typical little-endian vs big-endian in isQ.
Actually, if `M(q)` measures all qubits, maybe the bitstring is formed by `q[4]q[3]q[2]q[1]q[0]`? No, if earlier measured qubit is higher bit, `q[0]` is the highest bit.
Wait! What if the prompt has a typo and `X(q[4])` should have been `X(q[0])`?
No, the prompt explicitly says `X(q[

### Reference answer

{'predicted_probs': {'16': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/189. Dimension: predict probabilities for reference circuit.'}

## isqTrain/4316

- task_id: `isqTrain/4316`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `4144`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
qbit q[3];

procedure main() {
    // Prepare state |101>
    X(q[0]);
    X(q[2]);
    // Measure all qubits
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. Operations: The circuit applies `X(q[0])` and `X(q[2])` to prepare a state, followed by another `X(q[0])`, and finally measures all three qubits.
2. State evolution: The system starts in the ground state |000>.
3. The first two X gates flip qubits 0 and 2, preparing the state |101>.
4. The third X gate on qubit 0 flips it back to |0>, evolving the state to |001>.
5. Since the final state is exactly |001>, measuring the qubits yields a deterministic outcome.

Predicted probability distribution: {|001>: 1.0}

### Reference answer

{'predicted_probs': {'001': 1.0}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|001>) = 1.0000.'}

## isqTrain/3900

- task_id: `isqTrain/3900`
- task_type: `bug_fix`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1767`

### Prompt

修复以下isQ程序中的错误：

```
import std;
// 5-qubit GHZ state with phase pi/4
// Target: (|00000> + e^{i*pi/4}|11111>) / sqrt(2)
qbit q[5];

procedure main() {
    // Create GHZ state
    H(q[0]);
    // Apply phase e^{i*phi} to |1> component
    Rz(3.14159265358979 * 1.0 / 4.0, q[0]);
    // Entangle all qubits
    CNOT(q[1], q[0]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
    CNOT(q[3], q[4]);
    // Measure all
    M(q[0]); M(q[1]); M(q[2]); M(q[3]); M(q[4]);
}

``` (bug type: swapped qubits)

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Task:** Bug fix for an isQ quantum program generating a 5-qubit GHZ state with phase $\pi/4$.
    *   **Buggy Code vs. Correct Code:** The only difference is `CNOT(q[1], q[0])` vs `CNOT(q[0], q[1])` in the entanglement step.
    *   **Bug Type:** `swapped_qubits` (control and target of the first CNOT are swapped).
    *   **Output format:** ONLY the analysis starting with "## Bug Analysis", no code blocks, concise (3-15 lines).

2.  **Analyze the Bug:**
    *   **Buggy code:** `CNOT(q[1], q[0]);` - Qubit 1 is control, Qubit 0 is target. But q[0] is in state $(|0\rangle + e^{i\pi/4}|1\rangle)/\sqrt{2}$, while q[1] is in $|0\rangle$. CNOTing from 1 to 0 will do nothing because q[1] is $|0\rangle$.
    *   **Correct code:** `CNOT(q[0], q[1]);` - Qubit 0 is control, Qubit 1 is target. This correctly entangles q[1] with q[0].

3.  **Trace the State Evolution (Corrected Circuit):**
    *   Initial state: $|00000\rangle$
    *   `H(q[0])`: $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)|0000\rangle$
    *   `Rz(pi/4, q[0])`: $\frac{1}{\sqrt{2}}(|0\rangle + e^{i\pi/4}|1\rangle)|0000\rangle$
    *   `CNOT(q[0], q[1])`: $\frac{1}{\sqrt{2}}(|00\rangle + e^{i\pi/4}|11\rangle)|000\rangle$
    *   `CNOT(q[1], q[2])` through `CNOT(q[3], q[4])`: Chains the entanglement.
    *   Final state: $\frac{1}{\sqrt{2}}(|00000\rangle + e^{i\pi/4}|11111\rangle)$, which matches the target and yields measurement probabilities 0.5 for $|00000\rangle$ and 0.5 for $|11111\rangle$.

4.  **Draft the Response:**
    *   *Heading*: ## Bug Analysis
    *   *1. What the bug is*: The first CNOT gate in the buggy code is `CNOT(q[1], q[0])`. The control and target qubits are swapped. Since `q[1]` is in the $|0\rangle$ state at this point, this CNOT does nothing, failing to create the entangled GHZ state.
    *   *2. What the fix is*: Change `CNOT(q[1], q[0])` to `CNOT(q[0], q[1])` so that `q[0]` (which is in superposition) correctly controls `q[1]`.
    *   *3. State evolution*: 
        *   Start: $|00000\rangle$
        *   After `H(q[0])` and `Rz`: $\frac{1}{\sqrt{2}}(|0\rangle + e^{i\pi/4}|1\rangle)|0000\rangle$
        *   After `CNOT(q[0], q[1])`: $\frac{1}{\sqrt{2}}(|00\rangle + e^{i\pi/4}|11\rangle)|000\rangle$
        *   After subsequent CNOTs: $\frac{1}{\sqrt{2}}(|00000\rangle + e^{i\pi/4}|11111\rangle)$.

5.  **Refine for Conciseness:** Keep it strictly to 3-8 lines, check all rules.
    "## Bug Analysis
    1. The bug is a swapped control and target in the first entangling gate, `CNOT(q[1], q[0])`. Because q[1] is in the |0> state, this CNOT does nothing, failing to entangle the qubits.
    2. The fix is changing the gate to `CNOT(q[0], q[1])` so the superposition on q[0] controls the state of q[1].
    3. Starting from |00000>, `H(q[0])

## isqTrain/3387

- task_id: `isqTrain/3387`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `5107`

### Prompt

Write isQ code for the following quantum task: an isQ program: in a 3-qubit register, apply X then H to q[0] only. Other qubits stay |0>. Measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply X then H to q[0] in a 3-qubit register, measure all qubits.
2. **Qubits**: 3 qubits declared (q[0], q[1], q[2]), all measured.
3. **State evolution**:
   - Initial: |000⟩
   - X(q[0]): X|0⟩ = |1⟩ → |100⟩
   - H(q[0]): H|1⟩ = (|0⟩ − |1⟩)/√2 → (|000⟩ − |100⟩)/√2
4. **Probabilities**: The superposition (|000⟩ − |100⟩)/√2 yields equal probabilities: P(|000⟩) = 0.5, P(|100⟩) = 0.5. Qubits q[1] and q[2] remain |0⟩ throughout.

## isqTrain/4721

- task_id: `isqTrain/4721`
- task_type: `code_equivalence`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4248`

### Prompt

Do these two isQ programs produce the same measurement results?

Program A:
```isq
import std;
qbit q[2];

procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

Program B:
```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    X(q[1]);
    H(q[0]); // add superposition
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis

**Program A** applies H to q[0] creating |+⟩|0⟩, then CNOT(q[0], q[1]) producing the Bell state (|00⟩ + |11⟩)/√2.

**Program B** applies X to both qubits yielding |11⟩, then H(q[0]) transforms it to (|0⟩ - |1⟩)/√2 ⊗ |1⟩ = (|01⟩ - |11⟩)/√2.

**Key difference:** Program A produces perfect correlation (both qubits always agree), while Program B produces anti-correlated superposition (q[1] is always |1⟩, q[0] is in superposition).

**Measurement probabilities:**
- Program A: 50% |00⟩, 50% |11⟩
- Program B: 50% |01⟩, 50% |11⟩

These are clearly different distributions. The programs are **not equivalent**.

**Verdict: No**

### Reference answer

{'equivalent': False, 'explanation': 'After adding H gate to Program B, the programs produce different probability distributions.', 'probs_a': {'00': 0.5, '11': 0.5}, 'probs_b': {'01': 0.5, '11': 0.5}}

## isqTrain/1461

- task_id: `isqTrain/1461`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3735`

### Prompt

Create an isQ quantum circuit that Prepare the computational basis state |00111> on 5 qubits by applying X gates to the appropriate qubits, then measure all.

### Chain-of-thought reasoning

## Reasoning
- The goal is to prepare the computational basis state |00111> on 5 qubits.
- All 5 qubits are used and measured.
- Starting from |00000>, X gates on q[2], q[3], and q[4] flip those qubits: |00000> → |00111>.
- Since the final state is a single computational basis state, measurement yields |00111> with probability 1.0.

## isqTrain/3233

- task_id: `isqTrain/3233`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `91`

### Prompt

I need an isQ program to an isQ program: apply Ry(1*pi/2) to q[0] and Ry(1*pi/2) to q[1], then measure both (no entanglement).

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Apply independent Ry(π/2) rotations to two qubits and measure them to demonstrate an equal superposition across all basis states.
2. **Qubits:** 2 qubits are used (`q[0]`, `q[1]`), and both are measured at the end of the circuit.
3. **State evolution:**
   - Initialize to the ground state: |00⟩
   - Apply Ry(π/2) to q[0]: Ry(π/2)|0⟩ = (|0⟩ + |1⟩)/√2. State becomes (|00⟩ + |10⟩)/√2
   - Apply Ry(π/2) to q[1]: State becomes (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2
4. **Probabilities:** The final state is an equal superposition of the four 2-qubit basis states. Squaring the amplitudes gives a uniform 25% probability for each outcome: {|00⟩: 0.25, |01⟩: 0.25, |10⟩: 0.25, |11⟩: 0.25}.
