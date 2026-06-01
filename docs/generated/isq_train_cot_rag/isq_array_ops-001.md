# ISQ training COT RAG corpus: isq_array_ops shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/273

- task_id: `isqTrain/273`
- task_type: `output_prediction`
- category: `isq_array_ops`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `2425`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;

qbit q[3];

procedure main() {
    X(q[0]);
    X(q[2]);
    int x = M(q);
    print x;
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The 3-qubit system is initialized to the ground state |000>.
2. `X(q[0])` applies a Pauli-X gate to the first qubit, flipping its state from |0> to |1>. The system state becomes |001>.
3. `X(q[2])` applies a Pauli-X gate to the third qubit, flipping its state from |0> to |1>. The system state becomes |101>.
4. The quantum state before measurement is deterministically |101>. 
5. Measuring the qubits yields this exact classical bitstring with certainty.

Predicted probability distribution: {|101>: 1.0}

### Reference answer

{'predicted_probs': {'5': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/91. Dimension: predict probabilities for reference circuit.'}

## isqTrain/262

- task_id: `isqTrain/262`
- task_type: `output_prediction`
- category: `isq_array_ops`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3631`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;

qbit q[4];

procedure main() {
    H(q[0]); H(q[1]);
    X(q[2]); X(q[3]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations:** The circuit initializes 4 qubits in |0>. It applies H to q[0] and q[1], creating equal superpositions. It then applies X to q[2] and q[3], flipping them to |1>. 
2. **Evolution:** 
   - Initial state: |0000>
   - After H(q[0]) and H(q[1]): (1/

### Reference answer

{'predicted_probs': {'3': 0.25, '7': 0.25, '11': 0.25, '15': 0.25}, 'explanation': 'Parametric variant of isqHumanEval/88. Dimension: predict probabilities for reference circuit.'}

## isqTrain/1921

- task_id: `isqTrain/1921`
- task_type: `output_prediction`
- category: `isq_array_ops`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `4336`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[4];
procedure main() {
    H(q[0]); H(q[1]);
    X(q[2]); X(q[3]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Analyze an isQ quantum program and predict the probability distribution of measurement outcomes.
    *   Input Program: 4 qubits. H on q[0], H on q[1], X on q[2], X on q[3]. Measurements on all.
    *   Format Constraints: Output ONLY the analysis, starting with "## Circuit Analysis", ending with the predicted probability distribution. Do not include code blocks.
    *   Length Constraint: 3-8 lines for simple circuits.

2.  **Circuit Analysis:**
    *   Initial state: $|0000\rangle$
    *   Apply H on q[0]: $(|0\rangle + |1\rangle)/\sqrt{2} \otimes |000\rangle = (|0000\rangle + |1000\rangle)/\sqrt{2}$
    *   Apply H on q[1]: $(|00\rangle + |01\rangle + |10\rangle + |11\rangle)/2 \otimes |00\rangle = (|0000\rangle + |0100\rangle + |1000\rangle + |1100\rangle)/2$
    *   Apply X on q[2]: $(|0010\rangle + |0110\rangle + |1010\rangle + |1110\rangle)/2$
    *   Apply X on q[3]: $(|0011\rangle + |0111\rangle + |1011\rangle + |1111\rangle)/2$
    *   Measurements: M(q[0]), M(q[1]), M(q[2]), M(q[3]).
    *   Wait, isQ `--probs` output convention: "earlier measured qubit = higher bit". M(q[0]) is highest bit (bit 3), M(q[1]) is bit 2, M(q[2]) is bit 1, M(q[3]) is bit 0.
    *   Bitstring format: $q_0 q_1 q_2 q_3$.
    *   States: $|0011\rangle, |0111\rangle, |1011\rangle, |1111\rangle$. All have equal probability 1/4 = 0.25.
    *   Matches expected: {'0011': 0.25, '0111': 0.25, '1011': 0.25, '1111': 0.25}.

3.  **Drafting the Response:**
    *   *Line 1:* ## Circuit Analysis
    *   *Line 2:* 1. **Operations:** The circuit initializes 4 qubits in |0000>, applies Hadamard (H) gates to q[0] and q[1], and Pauli-X gates to q[2] and q[3], followed by measurement.
    *   *Line 3:* 2. **State Evolution:** H gates put q[0] and q[1] into an equal superposition $|+\rangle = (|0\rangle + |1\rangle)/\sqrt{2}$.
    *   *Line 4:* X gates flip q[2] and q[3] to $|1\rangle$.
    *   *Line 5:* 3. **Final State:** The combined state is $\frac{1}{2}(|0011\rangle + |0111\rangle + |1011\rangle + |1111\rangle)$.
    *   *Line 6:* 4. **Probabilities:** The four states are equally likely, each with a 25% probability.

4.  **Refining to meet constraints:** 3-8 lines.
    *   "## Circuit Analysis"
    *   "1. Operations: Initialize 4 qubits in $|0000\rangle$. Apply H gates to q[0] and q[1], and X gates to q[2] and q[3]."
    *   "2. State Evolution: H gates create superpositions on the first two qubits ($|+\rangle$), while X gates flip the last two qubits to $|1\rangle$."
    *   "3. Final State: The quantum state before measurement is $\frac{1}{2}(|0011\rangle + |0111\rangle + |1011\rangle + |1111\rangle)$."
    *   "4. Predicted Probability Distribution:"
    *   "0011: 0.25"
    *   "0111: 0.25"
    *   "1011: 0.25"
    *   "1111: 0.25"
    *   (Total 9 lines, slightly long

### Reference answer

{'predicted_probs': {'0011': 0.25, '0111': 0.25, '1011': 0.25, '1111': 0.25}, 'explanation': 'Array slicing simulation.'}

## isqTrain/270

- task_id: `isqTrain/270`
- task_type: `code_generation`
- category: `isq_array_ops`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `1316`

### Prompt

Write isQ code for the following quantum task: implements the gate_decomposition pattern with a different measurement ordering (reversed measurement order for p). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply X to flip all p qubits, then entangle with q via CNOT, measuring in reversed order for p.
2. Qubits: 6 total (p[0-2], q[0-2]); all measured with order p[2], p[1], p[0], q[0], q[1], q[2].
3. Initial state: |000⟩ₚ ⊗ |000⟩_q. After X(p): |111⟩ₚ ⊗ |000⟩_q. After CNOT(p,q): since each p[i]=|1⟩, all q[i] flip → |111⟩ₚ ⊗ |111⟩_q.
4. Measurement bitstring: p[2] is MSB (bit 5), down to q[2] as LSB (bit 0). All qubits yield 1, giving |111111⟩ with probability 1.0.

## isqTrain/268

- task_id: `isqTrain/268`
- task_type: `code_generation`
- category: `isq_array_ops`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `4822`

### Prompt

Code this in isQ: implements the gate_decomposition pattern. Include explicit identity operations in the circuit (X-X pair before M(p[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Demonstrate gate decomposition with an identity X-X pair that cancels, leaving the state unchanged before measurement.
2. **Qubits**: 6 total (p[0-2], q[0-2]), all measured.
3. **State evolution**:
   - Start: |000000⟩
   - X(p) → |111000⟩ (flip all p qubits)
   - CNOT(p,q) → |111111⟩ (each p[i]=|1⟩ flips q[i])
   - X(p[0]) → |011111⟩
   - X(p[0]) → |111111⟩ (X-X pair = identity, gate cancellation)
4. **Result**: Final state |111111⟩ yields measurement probability {|111111⟩: 1.0}.

## isqTrain/267

- task_id: `isqTrain/267`
- task_type: `code_generation`
- category: `isq_array_ops`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `2218`

### Prompt

Implement the following in isQ: implements a variant of the gate_decomposition pattern using p[3] -> p[5]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Create an 8-qubit circuit (p[5] + q[3]) that produces |11111111> with certainty.
2. 8 qubits needed: p[0]-p[4] and q[0]-q[2]; all are measured.
3. State evolution:
   - Initial: |00000000>
   - X(p) flips all p qubits to |1>: |11111000>
   - CNOT(p[i], q[i]) for i=0,1,2 propagates control |1> to targets: |11111111>
4. Final state is |11111111> with probability 1.0 since all 8 qubits are in |1>.

## isqTrain/260

- task_id: `isqTrain/260`
- task_type: `code_generation`
- category: `isq_array_ops`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `4919`

### Prompt

I need an isQ program to implements the gate_decomposition pattern but with a different initial state preparation (flip q[[2, 3]] -> q[1]).

### Chain-of-thought reasoning

Let me analyze this task carefully.

The task is to write an isQ program that implements a gate_decomposition pattern but with a different initial state preparation. The circuit should:

1. Apply H to q[0] and q[1]
2. Apply X to q[1]
3. Measure all 4 qubits

The resulting probabilities should be:
- |0000>: 0.25
- |0100>: 0.25
- |1000>: 0.25
- |1100>: 0.25

Let me trace through The implementation:
- Initial state: |0000>
- After H(q[0]): |+>|0>|0>|0> = (1/√2)(|0000> + |1000>)
- After H(q[1]): (1/√2)(|+0>|0>|0>) = (1/2)(|0000> + |0100> + |1000> + |1100>)
- After X(q[1]): (1/2)(|0100> + |0000> + |1100> + |1000>) = (1/2)(|0000> + |0100> + |1000> + |1100>)

Wait, that gives the same result. Let me think again...

Actually, H(q[1]) followed by X(q[1]) is different from X(q[1]) followed by H(q[1]).

Let me redo:
- Initial state: |0000>
- After H(q[0]): (1/√2)(|0000> + |1000>)
- After H(q[1]): (1/2)(|0000> + |0100> + |1000> + |1100>)
- After X(q[1]): (1/2)(|0100> + |0000> + |1100> + |1000>)

Hmm, the order of X flip on q[1] just rearranges terms, but since we have all four states with equal amplitude, the probabilities are the same.

The task says to "flip q[[2, 3]] -> q[1]" which means instead of applying X to q[1], we should flip q[2] and q[3] (or some variation).

Wait, let me re-read: "implements the gate_decomposition pattern but with a different initial state preparation (flip q[[2, 3]] -> q[1])"

I think this means the original pattern had X on q[1], but now we need to flip q[2] and q[3] instead of q[1].

But looking at the predicted output:
- |0000>: 0.25
- |0100>: 0.25
- |1000>: 0.25
- |1100>: 0.25

These are the same as the reference! So the measurement probabilities are the same for q[0] and q[1], but q[2] and q[3] would be different if we flip those instead.

Wait, but if we flip q[2] instead of q[1], the state would be:
- After H(q[0]) and H(q[1]): (1/2)(|0000> + |0100> + |1000> + |1100>)
- After X(q[2]): (1/2)(|0010> + |0110> + |1010> + |1110>)

That would give probabilities for |0010>, |0110>, |1010>, |1110> - which doesn't match the predicted output.

Let me re-read the task more carefully. the predicted output match The implementation, so perhaps the task wants us to produce the same output but with a different way of achieving it?

Actually, I think I misread. Let me look again at the predicted output:
{|0000>: 0.25, |0100>: 0.25, |1000>: 0.25, |1100>: 0.25}

And The circuit should:
H(q[0]); H(q[1]); X(q[1]);

This creates a superposition where q[0] and q[1] are in an equal superposition of all combinations, and q[2], q[3] remain |0>.

The task says "flip q[[2, 3]] -> q[1]" which I interpret as: instead of flipping q[1], flip q[2] and q[3]. But that would give different measurement results...

Unless the measurement only considers certain qubits? No, it says "Number of qubits measured: 4"

I think there might be some ambiguity here. Let me assume the task wants:
- H(q[0]); H(q[1]) to create superposition on first two qubits

## isqTrain/1924

- task_id: `isqTrain/1924`
- task_type: `output_prediction`
- category: `isq_array_ops`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `4035`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[3];
procedure main() {
    X(q[0]);
    X(q[2]);
    int x = M(q);
    print x;
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initialization**: The 3-qubit register `q` is initialized to the $|000\rangle$ state.
2. **X Gate on q[0]**: The Pauli-X gate flips the state of `q[0]`, changing the state to $|100\rangle$.
3. **X Gate on q[2]**: The Pauli-X gate flips the state of `q[2]`, changing the state to $|101\rangle$.
4. **Measurement**: Measuring the qubits yields the deterministic classical state corresponding to $|101\rangle$.

**Predicted probability distribution:**
- `101`: 1.0

### Reference answer

{'predicted_probs': {'101': 1.0}, 'explanation': 'Array measurement.'}

## isqTrain/269

- task_id: `isqTrain/269`
- task_type: `code_generation`
- category: `isq_array_ops`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `1415`

### Prompt

Implement the following in isQ: implements the gate_decomposition pattern. Include explicit identity operations in the circuit (H-H pair before M(p[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a gate_decomposition pattern demonstrating identity via consecutive H gates (H∘H = I) on qubit p[0] before measurement.
2. **Qubits**: 6 total — p[3] and q[3]; all are measured with M().
3. **State evolution**:
   - Initial: |000000⟩ (order: p[0],p[1],p[2],q[0],q[1],q[2])
   - After `X(p)`: |111000⟩ — all p qubits flip to |1⟩
   - After `CNOT(p,q)`: |111111⟩ — each q[i] flips since p[i] = |1⟩
   - After first `H(p[0])`: (|011111⟩ − |111111⟩)/√2 — p[0] enters superposition
   - After second `H(p[0])`: |111111⟩ — H∘H = I restores p[0] to |1⟩
4. **Expected probabilities**: The final state is exactly |111111⟩, so measurement always yields 111111 with probability 1.0. The H-H pair cancels (demonstrating gate cancellation awareness) leaving the X+CNOT structure intact.

## isqTrain/2551

- task_id: `isqTrain/2551`
- task_type: `code_equivalence`
- category: `isq_array_ops`
- difficulty: `intermediate`
- concept_tags: `global_phase`, `isq_syntax_arrays`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3442`

### Prompt

这两个isQ程序是等价的吗？

程序A：
```isq
import std;

qbit q[3];

procedure main() {
    H(q);
    M(q[0]); M(q[1]); M(q[2]);
}

```

程序B：
```isq
import std;

qbit q[3];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    H(q);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. Program A applies H gates to all three qubits, preparing the state |+⟩|+⟩|+⟩ = (1/√8)Σ|x⟩ for all 3-bit strings x.
2. Program B applies GPhase(0.0) followed by H gates to all three qubits.
3. The key difference is the addition of GPhase(0.0) in Program B, which applies a trivial global phase factor of e^(i·0) = 1 (the identity).
4. Since GPhase(0.0) has no effect on the quantum state, both programs produce the identical state |+⟩|+⟩|+⟩, yielding equal measurement probabilities of 1/8 for each of the 8 possible outcomes.
5. Verdict: Equivalent: True

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}
