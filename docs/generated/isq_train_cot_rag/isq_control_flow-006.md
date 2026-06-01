# ISQ training COT RAG corpus: isq_control_flow shard 6

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1648

- task_id: `isqTrain/1648`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `basic`
- concept_tags: `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `4832`

### Prompt

Implement the following in isQ: Apply Hadamard gate 4 times using a for loop. Since H^2=I, an even number of H applications yields identity.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply the Hadamard gate four times to a single qubit, exploiting H² = I to return to the initial state.
2. **Qubits**: One qubit `q[0]`, initialized to |0⟩, is measured.
3. **State evolution**:
   - Start: |0⟩
   - H(q[0]): |+⟩ = (|0⟩ + |1⟩)/√2
   - H(q[0]): |0⟩ (since H² = I)
   - H(q[0]): |+⟩
   - H(q[0]): |0⟩
4. **Result**: The final state is |0⟩, so measurement yields {|0⟩: 1.0}.

## isqTrain/2545

- task_id: `isqTrain/2545`
- task_type: `code_equivalence`
- category: `isq_control_flow`
- difficulty: `basic`
- concept_tags: `global_phase`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `2275`

### Prompt

比较这两个量子电路，它们的输出概率分布一样吗？

```isq
import std;

qbit q[4];

procedure main() {
    for i in 0:4 {
        H(q[i]);
    }
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

```isq
import std;

qbit q[4];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    for i in 0:4 {
        H(q[i]);
    }
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** initializes 4 qubits in |0>, applies a Hadamard gate (H) to each, resulting in the joint state |+>|+>|+>|+>, and measures them.
2. **Program B** performs the exact same operations but includes an additional GPhase(0.0) instruction at the beginning.
3. The key difference is the inclusion of GPhase(0.0) in Program B, which applies a global phase factor of $e^{i \cdot 0} = 1$.
4. Since a global phase of 1 is mathematically an identity operation, it leaves the quantum statevector completely unchanged. Thus, the resulting measurement probabilities are strictly identical.
5. Verdict: Yes, the programs are equivalent.

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/1691

- task_id: `isqTrain/1691`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_for_loop`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `879`

### Prompt

用isQ实现Use a for loop for CNOT fan-out: q[0] controls all others on 4 qubits from |1000>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a |1111> GHZ-like state from |0000> using X on q[0] followed by CNOT fan-out to all other qubits.
2. **Qubits**: 4 qubits (q[0] to q[3]), all measured.
3. **State evolution**:
   - |0000> →(X on q[0])→ |1000>
   - |1000> →(CNOT q[0]→q[1])→ |1100>
   - |1100> →(CNOT q[0]→q[2])→ |1110>
   - |1110> →(CNOT q[0]→q[3])→ |1111>
4. **Expected probabilities**: The final state is |1111> with certainty, so measurement yields |1111> (bitstring 15) with probability 1.0.

## isqTrain/1695

- task_id: `isqTrain/1695`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_for_loop`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `909`

### Prompt

实现以下量子计算任务（使用isQ）：Use a for loop for CNOT fan-out: q[0] controls all others on 6 qubits from |100000>.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement a CNOT fan-out where q[0] (control) entangles all other qubits, starting from |100000⟩, using 6 qubits—all measured.

1. **Initial state**: |000000⟩; after X(q[0]) → |100000⟩.
2. **CNOT fan-out loop** (i=1 to 5): Each CNOT(q[0], q[i]) flips q[i] since q[0]=|1⟩:
   - i=1: |110000⟩, i=2: |111000⟩, i=3: |111100⟩, i=4: |111110⟩, i=5: |111111⟩.
3. **Final state**: |111111⟩.
4. **Measurement**: All 6 qubits measured; P(|111111⟩)=1.0, since the state is deterministic with all qubits in |1⟩.

## isqTrain/247

- task_id: `isqTrain/247`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_while_loop`
- source: `isq_train_cot`
- dataset_index: `1672`

### Prompt

请用isQ语言编写一个量子电路：implements a variant of the arithmetic_circuit pattern using q[2] -> q[3]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement an arithmetic-style circuit using a while loop to apply repeated Rx rotations, demonstrating classical control flow integration.

2. **Qubits**: 3 qubits (q[0], q[1], q[2]) are declared and all are measured.

3. **State evolution**:
   - Initial: |000⟩
   - Loop applies Rx(π/6) three times to q[0], totaling Rx(π/2)
   - Rx(π/2)|0⟩ = cos(π/4)|0⟩ + i·sin(π/4)|1⟩ = (1/√2)|0⟩ + (i/√2)|1⟩
   - Final state: (1/√2)|000⟩ + (i/√2)|100⟩

4. **Probabilities**: P(|000⟩) = |1/√2|² = 0.5, P(|100⟩) = |i/√2|² = 0.5

## isqTrain/243

- task_id: `isqTrain/243`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `1477`

### Prompt

用isQ实现implements the ghz_state_preparation pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Prepare a 4-qubit GHZ state and measure qubits in reversed order (q[3]→q[0]).

2. **Qubits**: 4 qubits (q[0] to q[3]), all measured; earlier-measured qubit maps to higher bit in output.

3. **State evolution**:
   - Initial: |0000⟩
   - H(q[0]): (|0000⟩ + |1000⟩)/√2
   - CNOT(q[0],q[1]): (|0000⟩ + |1100⟩)/√2
   - CNOT(q[1],q[2]): (|0000⟩ + |1110⟩)/√2
   - CNOT(q[2],q[3]): (|0000⟩ + |1111⟩)/√2 (GHZ state)

4. **Probabilities**: The GHZ state has equal amplitude on |0000⟩ and |1111⟩, giving P(|0000⟩) = 0.5 and P(|1111⟩) = 0.5. The reversed measurement order maps q[3] as the highest bit and q[0] as the lowest, but since all qubits are entangled in the same computational basis state (all 0s or all 1s), the bitstring remains |0000⟩ or |1111⟩.

## isqTrain/239

- task_id: `isqTrain/239`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `4773`

### Prompt

Implement the following in isQ: implements a variant of the ghz_state_preparation pattern using q[4] -> q[5]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

The task asks me to write a reasoning section for a variant of the GHZ state preparation circuit. Looking at the prompt, the circuit should use q[4] -> q[5], which suggests 6 qubits total (q[0] through q[5]).

Wait, let me re-read. The prompt says "q[4] -> q[5]" but The circuit should q[0] through q[4] (5 qubits). The expected measurement probabilities are {|00000>: 0.5, |11110>: 0.5} for 5 qubits.

Hmm, but |11110> is interesting - it's not the standard GHZ state which would be (|00000> + |11111>)/√2.

Let me trace through The implementation:
1. Start with |00000>
2. H(q[0]) → (|00000> + |10000>)/√2
3. CNOT(q[0], q[1]) → (|00000> + |11000>)/√2
4. CNOT(q[1], q[2]) → (|00000> + |11100>)/√2
5. CNOT(q[2], q[3]) → (|00000> + |11110>)/√2
6. CNOT(q[3], q[4]) → (|00000> + |11111>)/√2

So The implementation produces (|00000> + |11111>)/√2, not (|00000> + |11110>)/√2.

The predicted output {|00000>: 0.5, |11110>: 0.5}, which means only 4 CNOTs should be applied (up to q[3] -> q[4] would give |11110>, but that's q[4] as target).

Wait, let me re-read: "q[4] -> q[5]" suggests the last CNOT is from q[4] to q[5], but the predicted output show |11110> which has a 0 in the last position.

Actually, looking more carefully at the predicted output: {|00000>: 0.5, |11110>: 0.5}. This has 5 bits, measuring 5 qubits. The state |11110> has the last qubit as 0.

So the circuit should:
1. H(q[0])
2. CNOT(q[0], q[1])
3. CNOT(q[1], q[2])
4. CNOT(q[2], q[3])
5. CNOT(q[3], q[4])
6. No CNOT from q[4] to q[5]

But the prompt says "using q[4] -> q[5]" which suggests we should use 6 qubits and the CNOT goes from q[4] to q[5].

Let me think about this differently. Maybe the "variant" means we need to modify the circuit. The prompt says "expanded qubit register compared to the base version."

Actually, I think the task is to generate reasoning, not the code. The circuit should 5 qubits with 4 CNOTs (from i=0 to i=3, applying CNOT(q[i], q[i+1])).

The final state after the reference code would be:
1. |00000> initial
2. H(q[0]) → (|0> + |1>)/√2 ⊗ |0000> = (|00000> + |10000>)/√2
3. CNOT(q[0], q[1]) → (|00000> + |11000>)/√2
4. CNOT(q[1], q[2]) → (|00000> + |11100>)/√2
5. CNOT(q[2], q[3]) → (|00000> + |11110>)/√2

So after 3 CNOTs (i from 0 to 2), we get (|00000> + |11110>)/√2.

But the loop is `for i in 0:3` which means i = 0, 1, 2, 3 (4 iterations), so 4 CNOTs total.

Wait, in isQ, what does `for i in 0:3` mean? Is it 0, 1, 2 (3 iterations) or 0, 1, 2, 3 (4 iterations)?

Looking at typical quantum computing languages, `for i in 0:3` usually means i goes from 0 to 2 (exclusive of 3), so 3 iterations.

But The predicted output {|00000>: 0.5, |11110>: 0.
