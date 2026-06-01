# ISQ training COT RAG corpus: quantum_random_walk shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3307

- task_id: `isqTrain/3307`
- task_type: `code_generation`
- category: `quantum_random_walk`
- difficulty: `intermediate`
- concept_tags: `superposition`, `entanglement`
- source: `isq_train_cot`
- dataset_index: `1549`

### Prompt

Write an isQ program that an isQ program: 1-step quantum walk with Y coin. Use 2 qubits: q[0]=coin, q[1]=position. Apply Y to coin, then CNOT(coin, position) for conditional shift.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a 1-step quantum walk using a Y coin operator on q[0] (coin) with a conditional shift (CNOT) on q[1] (position), measuring both qubits.

2. **Qubits**: 2 qubits total — q[0] = coin, q[1] = position; both are measured.

3. **State evolution**:
   - Initialize: |00⟩
   - Apply Y to q[0]: Y|0⟩ = i|1⟩, so state → i|10⟩
   - Apply CNOT(q[0], q[1]): control q[0]=|1⟩ flips position q[1], so state → i|11⟩

4. **Final state**: i|11⟩ (global phase i is irrelevant to measurement).

5. **Expected probabilities**: Since the final state is |11⟩ up to a global phase, measurement yields |11⟩ with probability 1.0.

## isqTrain/3309

- task_id: `isqTrain/3309`
- task_type: `code_generation`
- category: `quantum_random_walk`
- difficulty: `intermediate`
- concept_tags: `superposition`, `entanglement`, `interference`
- source: `isq_train_cot`
- dataset_index: `185`

### Prompt

Create an isQ quantum circuit that an isQ program: 3-step quantum walk with H coin. Apply H+CNOT 3 times.

### Chain-of-thought reasoning

The goal is to create a 3-step quantum walk with H coin, applying H+CNOT 3 times.
Let's trace the quantum state evolution.
Initial state: |00>
Step 1:
H on q[0]: (|0> + |1>) |0> / sqrt(2)
CNOT(q[0], q[1]): (|00> + |11>) / sqrt(2)
Step 2:
H on q[0]: (|00> + |10> + |10> - |11>) / 2 = (|00> + 2|10> - |11>) / 2
Wait, let's expand properly.
(|0> + |1>) |0> / 2 + (|0> - |1>) |1> / 2 = |00>/2 + |10>/2 + |01>/2 - |11>/2
CNOT(q[0], q[1]): |00>/2 + |11>/2 + |01>/2 - |10>/2
Step 3:
H on q[0]: (|0>+|1>)|0>/2sqrt2 + (|0>-|1>)|1>/2sqrt2 + (|0>+|1>)|1>/2sqrt2 - (|0>-|1>)|0>/2sqrt2
= |00>/2sqrt2 + |10>/2sqrt2 - |01>/2sqrt2 + |11>/2sqrt2 + |01>/2sqrt2 + |11>/2sqrt2 - |00>/2sqrt2 + |10>/2sqrt2
= 2|10>/2sqrt2 + 2|11>/2sqrt2 = (|10> + |11>) / sqrt(2)
Wait, |10> means q[0] is 1, q[1] is 0.
So q[0] is 1 with probability 1. q[1] is 0 or 1 with equal probability.
Therefore, the probabilities are P(10) = 0.5, P(11) = 0.5.
Let's double check step 3.
State after Step 2 CNOT: (|00> - |10> + |01> + |11>)/2
Wait!
|00>/2 + |11>/2 + |01>/2 - |10>/2
Apply H on q[0]:
|00> -> |00>+|10>
|11> -> |01>-|11>
|01> -> |01>+|11>
|10> -> |00>-|10>
Sum: |00>+|10> + |01>-|11> + |01>+|11> - |00>+|10> = 2|10> + 2|01>
Wait! My previous manual expansion gave 2|11> + 2|10>. Let's recompute carefully.
State before H: (|00> - |10> + |01> + |11>)/2
Let q[0] be control, q[1] be target.
H(q[0]):
|00> -> (|0>+|1>)|0> = |00>+|10>
-|10> -> -(|0>-|1>)|0> = -|00>+|10>
|01> -> (|0>+|1>)|1> = |01>+|11>
|11> -> (|0>-|1>)|1> = |01>-|11>
Sum of all: (|00>+|10> - |00>+|10> + |01>+|11> + |01>-|11>) / 2 = (2|10> + 2|01>) / 2 = |10> + |01>
Apply CNOT(q[0], q[1]):
|10> -> |11>
|01> -> |01>
Result: |01> + |11> (up to global phase)
Probabilities of measuring q[0] (first bit) and q[1] (second bit):
Wait, in isQ, `M(q[0]); M(q[1]);` means bitstring is q[0] q[1].
If state is |01> + |11>, q[0] is 0 for |01> and 1 for |11>.
So bitstring is 01 and 11.
Probabilities: P(01) = 0.5, P(11) = 0.5.
Wait, if the prompt says Expected measurement probabilities: {|01>: 0.5, |11>: 0.5}.
Matches perfectly.

Wait, step 2 check:
State before step 2: (|00>+|11>)/sqrt(2)
H on q[0]: |0>(|0>+|

## isqTrain/3308

- task_id: `isqTrain/3308`
- task_type: `code_generation`
- category: `quantum_random_walk`
- difficulty: `intermediate`
- concept_tags: `superposition`, `entanglement`, `interference`
- source: `isq_train_cot`
- dataset_index: `2042`

### Prompt

Help me write isQ code that an isQ program: 2-step quantum walk with H coin. Apply H+CNOT 2 times.

### Chain-of-thought reasoning

## Reasoning

**Goal**: Implement a 2-step quantum walk with H as the coin operator and CNOT as the conditional shift operator.

**Qubits**: 2 qubits — q[0] (coin), q[1] (walker position); both measured.

**State evolution**:

1. **Initial**: |00⟩

2. **Step 1 — H(q[0])**: |00⟩ → (|00⟩ + |10⟩)/√2

3. **Step 1 — CNOT(q[0], q[1])**: (|00⟩ + |10⟩)/√2 → (|00⟩ + |11⟩)/√2

4. **Step 2 — H(q[0])**: (|00⟩ + |11⟩)/√2 → (|00⟩ + |10⟩ + |01⟩ − |11⟩)/2

5. **Step 2 — CNOT(q[0], q[1])**: (|00⟩ + |10⟩ + |01⟩ − |11⟩)/2 → (|00⟩ + |11⟩ + |01⟩ − |10⟩)/2

**Probabilities**: Each basis state {|00⟩, |01⟩, |10⟩, |11⟩} has amplitude ±1/2, giving probability |±1/2|² = 0.25 each. The H coin spreads the walker uniformly over 2 steps, with interference yielding equal probabilities across all outcomes.
