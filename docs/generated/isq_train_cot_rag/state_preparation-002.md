# ISQ training COT RAG corpus: state_preparation shard 2

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4798

- task_id: `isqTrain/4798`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_if_else`, `isq_syntax_classical_vars`
- source: `isq_train_cot`
- dataset_index: `2149`

### Prompt

Implement a quantum circuit in isQ: implements: classical if-else gate choice variant 0. Declare a global qbit array q of 2 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning
The circuit initializes 2 qubits and uses a classical flag variable to conditionally apply quantum gates, finally measuring both qubits.
Two qubits, `q[0]` and `q[1]`, are used and both are measured at the end of the circuit.
Initial state is |00⟩. Since `flag == 0` evaluates to true, the `if` block executes two X gates: X(q[0]) and X(q[1]).
This flips both qubits from |0⟩ to |1⟩, yielding the final state |11⟩.
Consequently, measuring the system results in the state |11⟩ with a probability of 1.0.

## isqTrain/1432

- task_id: `isqTrain/1432`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1300`

### Prompt

Write an isQ program that Prepare the state |Psi+> Bell state and measure all qubits.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Prepare the |Ψ+⟩ Bell state (|01⟩ + |10⟩)/√2 and measure both qubits.
2. Two qubits are used, both measured.
3. Initial state |00⟩ → X(q[1]) gives |01⟩ → H(q[0]) gives (|01⟩ + |11⟩)/√2 → CNOT(q[0], q[1]) gives (|01⟩ + |10⟩)/√2 = |Ψ+⟩.
4. Measurement yields |01⟩ with probability 0.5 and |10⟩ with probability 0.5.

## isqTrain/3147

- task_id: `isqTrain/3147`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `5476`

### Prompt

Implement a quantum circuit in isQ: an isQ program: apply X to all 3 qubits to prepare |111>, then measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Initialize 3 qubits to the state |111⟩ and measure them.
2. **Qubits:** 3 qubits are used, and all 3 are measured.
3. **Evolution:** Starting from the ground state |000⟩, applying the Pauli-X gate to each qubit independently flips their state from |0⟩ to |1⟩, evolving the system to the final state |111⟩.
4. **Probabilities:** The final state is deterministically |111⟩, so measuring the quantum register yields the bitstring '111' with a probability of 1.0.

## isqTrain/3368

- task_id: `isqTrain/3368`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `2919`

### Prompt

Help me write isQ code that an isQ program: apply H to odd-indexed qubits only in a 5-qubit register.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Apply Hadamard gates exclusively to odd-indexed qubits (q[1], q[3]) in a 5-qubit register, leaving even-indexed qubits (q[0], q[2], q[4]) in |0⟩.
2. **Qubits:** 5 qubits declared globally; all 5 are measured.
3. **State evolution:**
   - Initial state: |00000⟩
   - After H(q[1]): |0⟩|+⟩|0⟩|0⟩|0⟩ = (1/√2)(|00000⟩ + |00010⟩)
   - After H(q[3]): |0⟩|+⟩|0⟩|+⟩|0⟩ = (1/2)(|00000⟩ + |00010⟩ + |01000⟩ + |01010⟩)
4. **Expected probabilities:** The final state is an equal superposition of four computational basis states, each with amplitude 1/2 and probability |1/2|² = 0.25, yielding {|00000⟩: 0.25, |00010⟩: 0.25, |01000⟩: 0.25, |01010⟩: 0.25}.

## isqTrain/3362

- task_id: `isqTrain/3362`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `2560`

### Prompt

Help me write isQ code that an isQ program: apply H to even-indexed qubits only in a 3-qubit register. Odd qubits stay |0>.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Apply H gates to even-indexed qubits (q[0], q[2]) only, leaving odd qubit q[1] in |0⟩.

**Qubits:** 3-qubit register, all measured.

**State evolution:**
1. Initial: |000⟩
2. H(q[0]): (1/√2)(|000⟩ + |100⟩)
3. H(q[2]): (1/2)(|000⟩ + |001⟩ + |100⟩ + |101⟩)

**Probabilities:** Each of the 4 basis states has amplitude 1/2, giving |1/2|² = 0.25 probability each. The middle qubit remains |0⟩, so bitstrings with q[1]=1 have zero probability.

## isqTrain/1859

- task_id: `isqTrain/1859`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1717`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
qbit q[1];
procedure main() {
    X(q[0]);
    H(q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The qubit is initialized to the ground state |0>.
2. The X gate flips the qubit to the excited state |1>.
3. The H (Hadamard) gate transforms the state into an equal superposition: |-> = (1/sqrt(2))(|0> - |1>).
4. Measuring in the computational basis collapses the superposition, yielding equal probabilities for both states.

Predicted probability distribution: {'0': 0.5, '1': 0.5}

### Reference answer

{'predicted_probs': {'0': 0.5, '1': 0.5}, 'explanation': '|-⟩ state yields uniform distribution.'}

## isqTrain/3838

- task_id: `isqTrain/3838`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1413`

### Prompt

I need an isQ program to Prepare the graph state for a ring 3 graph with 3 nodes and edges [(0, 1), (1, 2), (0, 2)]. Apply Hadamard to all qubits, then CZ for each edge. Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare a 3-qubit ring (triangle) graph state and measure all qubits.
2. **Qubits**: 3 qubits are used (q[0], q[1], q[2]), and all are measured at the end.
3. **Evolution**: Starting from |000>, applying Hadamard gates to all qubits creates an equal superposition |+++> = (1/√8) ∑ |x> for all 3-bit strings x.
4. **Entanglement**: Applying CZ gates for the edges (0,1), (1,2), and (0,2) applies a phase of -1 to any basis state where the connected qubits are both |1>, creating the graph state.
5. **Probabilities**: Because the CZ gates only modify the relative phases (e.g., mapping |011>, |101>, |110>, |111> to their negative counterparts), the measurement probabilities remain uniformly distributed as 0.125 for all 8 possible outcomes.

## isqTrain/3872

- task_id: `isqTrain/3872`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3821`

### Prompt

帮我写一个isQ程序：Prepare 3-qubit GHZ state (|000>+|111>)/√2 using ket assignment `q = |0> + |7>`. Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Prepare a 3-qubit GHZ state (|000> + |111>)/√2 and measure all qubits.
2. Qubits needed: 3 (q[0], q[1], q[2]), all measured.
3. State evolution:
   - Initial: |000>
   - After `q = |0> + |7>`: (|000> + |111>)/√2 — the GHZ state. In little-endian, |0> = |000> and |7> = |111>.
4. Measurements yield |000> or |111> each with probability 0.5.

## isqTrain/4217

- task_id: `isqTrain/4217`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `4676`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
qbit q[2];

procedure main() {
    Ry(1.5, q[0]);
    Ry(0.0, q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. Initial state is $|00\rangle$. The circuit applies an $R_y(1.5)$ rotation to $q[0]$ and $R_y(0.0)$ (identity) to $q[1]$.
2. State evolves from $|00\rangle$ to $(\cos(0.75)|0\rangle + \sin(0.75)|1\rangle) \otimes |0\rangle = \cos(0.75)|00\rangle + \sin(0.75)|10\rangle$.
3. Because $q[1]$ remains unaffected, measuring the system yields either $|00\rangle$ or $|10\rangle$.
4. The probability distribution is $P(00) = \cos^2(0.75) \approx 53.5\%$ and $P(10) = \sin^2(0.75) \approx 46.5\%$.

### Reference answer

Dominant output states: |00> with probability ~0.54 each

## isqTrain/3360

- task_id: `isqTrain/3360`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1999`

### Prompt

帮我写一个isQ程序：an isQ program: H(q[0]) then cascade CNOT through 6 qubits. This creates a cascading entanglement pattern.

### Chain-of-thought reasoning

## Reasoning
The goal is to create a 6-qubit GHZ state by placing the first qubit into an equal superposition and then entangling it with the remaining qubits.
6 qubits are required, and all 6 are measured at the end.
1. Initialize to $|000000\rangle$.
2. Apply $H(q[0])$, yielding $\frac{1}{\sqrt{2}}(|000000\rangle + |100000\rangle)$.
3. Apply $CNOT(q[0], q[1])$, propagating the entanglement to get $\frac{1}{\sqrt{2}}(|000000\rangle + |110000\rangle)$.
4. Continue the CNOT cascade through $q[5]$, turning $|1\rangle$ in the control to $|1\rangle$ in the target, resulting in the final state $\frac{1}{\sqrt{2}}(|000000\rangle + |111111\rangle)$.
Since the final state is an exact superposition of $|000000\rangle$ and $|111111\rangle$, measurements will strictly yield these two outcomes with equal probabilities of 0.5.
