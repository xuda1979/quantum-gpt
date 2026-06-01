# ISQ training COT RAG corpus: circuit_engineering shard 4

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1061

- task_id: `isqTrain/1061`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `qubit_mapping`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4038`

### Prompt

Implement the following in isQ: implements a variant of the vf2_mapping pattern using q[3] -> q[4]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement a VF2-inspired mapping circuit on an expanded 4-qubit register, demonstrating direct CNOT connectivity with no swap (three-CNOT decomposition) overhead.

2. **Qubits**: 4 qubits (q[0]-q[3]); all measured, with q[3] serving as the expanded register element.

3. **State evolution**:
   - Initial: |0000⟩
   - X(q[0]): |1000⟩
   - X(q[1]): |1100⟩
   - CNOT(q[0], q[2]): |1110⟩ (control q[0]=1 flips q[2])
   - CNOT(q[1], q[2]): |1100⟩ (control q[1]=1 flips q[2] back)

4. **Final measurement**: Deterministic |1100⟩ (probability 1.0) — q[3] remains |0⟩ throughout, showing the expanded register is idle but included in readout.

## isqTrain/1007

- task_id: `isqTrain/1007`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `circuit_optimization`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5469`

### Prompt

Create an isQ quantum circuit that implements the gate_cancellation pattern but with a different initial state preparation (flip q[[0]] -> q[1]).

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement gate cancellation pattern with X on q[1] instead of q[0].
2. **Qubits**: 2 qubits (q[0], q[1]), both measured.
3. **State evolution**:
   - Initial: |00⟩
   - After X(q[1]): |01⟩
   - CNOT-CNOT pair cancels (CNOT is self-inverse)
   - Final: |01⟩
4. **Expected probabilities**: {|01⟩: 1.0} — single X on q[1] flips it to |1⟩, and cancelled CNOTs leave state unchanged.

## isqTrain/1056

- task_id: `isqTrain/1056`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `qubit_mapping`
- source: `isq_train_cot`
- dataset_index: `3411`

### Prompt

Help me write isQ code that implements the sabre_routing pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a swap (three-CNOT decomposition)-based routing pattern for a non-adjacent CNOT, with an X-X identity pair demonstrating gate cancellation awareness.
2. **Qubits**: 3 qubits (q[0], q[1], q[2]), all measured.
3. **State evolution**:
   - Initialize to |000⟩
   - X(q[0]) → |100⟩
   - swap (three-CNOT decomposition)(q[0], q[1]) routes data to adjacent position → |010⟩
   - CNOT(q[1], q[2]) with control=1 flips target → |011⟩
   - swap (three-CNOT decomposition)(q[0], q[1]) restores positions → |101⟩
   - X(q[0]) flips q[0] to 0 → |001⟩
   - X(q[0]) flips q[0] back to 1 (identity pair: X·X = I) → |101⟩
4. **Expected probabilities**: The final state |101⟩ is deterministic, yielding {|101⟩: 1.0}.

## isqTrain/1053

- task_id: `isqTrain/1053`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `qubit_mapping`
- source: `isq_train_cot`
- dataset_index: `274`

### Prompt

Implement the following in isQ: implements the sabre_routing pattern but with a different initial state preparation (flip q[[0]] -> q[1]).

### Chain-of-thought reasoning

## Reasoning
1. Goal: Implement SABRE routing (swap (three-CNOT decomposition)-CNOT-swap (three-CNOT decomposition) pattern) with q[1] initialized to |1⟩.
2. Qubits: 3 qubits (q[0], q[1], q[2]), all measured at the end.
3. State evolution:
   - |000⟩ → X(q[1]) → |010⟩
   - swap (three-CNOT decomposition)(q[0], q[1]): |010⟩ → |100⟩
   - CNOT(q[1], q[2]): |100⟩ → |100⟩ (control q[1]=0, no flip on q[2])
   - swap (three-CNOT decomposition)(q[0], q[1]): |100⟩ → |010⟩
4. Final state |010⟩ gives measurement probability {|010⟩: 1.0}.

## isqTrain/1052

- task_id: `isqTrain/1052`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `qubit_mapping`
- source: `isq_train_cot`
- dataset_index: `3616`

### Prompt

Write an isQ program that implements a variant of the sabre_routing pattern using q[3] -> q[5]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

Step 1: Understand the Goal
The user wants an isQ program that implements a "sabre_routing" pattern with q[3] -> q[5]. This means I need to perform a CNOT where the control is q[3] and the target is q[5], using swap (three-CNOT decomposition) gates to route the information through adjacent qubits (since in many hardware topologies, only adjacent qubits can interact directly).

Step 2: Analyze the Requirements
- "variant of the sabre_routing pattern using q[3] -> q[5]": I need to route a CNOT from q[3] (control) to q[5] (target).
- "significantly expanded qubit register compared to the base version": The base version used 3 qubits (q[0], q[1], q[2]) to do a routing from 0->2. The user wants a routing from 3->5. To accommodate this, I need at least 6 qubits (q[0] to q[5]). The requirement "significantly expanded" might mean even more, like 8 or 10, but 6 is the minimum to have q[5]. Let's use a register of size 6 or more. Let's stick to 6 qubits to be safe, or maybe 8. Let's use `qbit q[8];`.
- "additional qubits left in the ground state": This means q[0], q[1], q[2], q[6], q[7] should remain |0>.
- The circuit should the pattern:
  1. Initialize q[0] to |1>.
  2. swap (three-CNOT decomposition)(q[0], q[1]) -> brings control closer.
  3. CNOT(q[1], q[2]).
  4. swap (three-CNOT decomposition)(q[0], q[1]) -> restores original positions.
  
  Wait, in the reference, the final state is |101>. The original q[0] was |1>. After swap(0, 1) via three CNOTs, the state is at physical q[1]. CNOT(1,2) entangles it with q[2]. So original data of 0 is at 1, 1 is at 0, 2 is 1. Then swap(0, 1) via three CNOTs again restores the data: 0 has its original data (which was q[1]'s |0>), 1 has its original data (which was q[0]'s |1>), and 2 is the target which got flipped. Wait, in the reference, final state is |101>, so q[0]=1, q[1]=0, q[2]=1.
  Let's trace reference:
  Init: q[0]=1. |100>
  swap(0, 1) via three CNOTs: |010>
  CNOT(1,2): control is 1 (which is 1), target is 2 (which is 0). Target flips to 1. State: |011>
  swap(0, 1) via three CNOTs: swaps 0 and 1. 0 becomes 1, 1 becomes 0. State: |101>.
  Measured: 101.
  
Step 3: Adapt to q[3] -> q[5]
The user wants a CNOT from q[3] to q[5]. Let's assume q[3] and q[5] are not directly connected, and we need to route through q[4].
Wait, in a linear topology:
q[3] --- q[4] --- q[5]
If we want CNOT(3, 5), we can do:
swap(4, 5) via three CNOTs -> brings q[5] to physical position 4, which is adjacent to 3.
CNOT(3, 4) -> performs the operation on the logical qubits (3 and 5).
swap(4, 5) via three CNOTs -> restores original positions.
Let's check this:
Assume q[3] is initialized to |1> like in the reference.
Init: |0001000> (let's say 7 qubits). q[3]=1.
swap(4, 5) via three CNOTs: swaps |0> and |0>. State is still |0001000>.
CNOT(3,4): control is 3 (value 1), target is 4 (value 0). Target flips to 1. State: |0001100>.
swap(4, 5) via three CNOTs: swaps 4 and 5. State becomes |0001010>.
Measurement would be: q[3]=1, q[4]=0, q[5]=1. So the bitstring for q[3..5] is 101.
This perfectly matches the requirement of routing from 3 to 5!
Wait, should I route the control or the target

## isqTrain/2053

- task_id: `isqTrain/2053`
- task_type: `output_prediction`
- category: `circuit_engineering`
- difficulty: `basic`
- concept_tags: `circuit_optimization`, `global_phase`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1916`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;
qbit q[2];
procedure main() {
    X(q[0]);
    X(q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The 2-qubit system is initialized in the ground state $|00\rangle$.
2. The $X(q[0])$ gate flips the first qubit ($|0\rangle \to |1\rangle$), transitioning the state to $|10\rangle$.
3. The $X(q[1])$ gate flips the second qubit ($|0\rangle \to |1\rangle$), transitioning the state to $|11\rangle$.
4. Before measurement, the exact quantum state is the product state $|11\rangle$.
5. Measuring both qubits deterministically collapses the state to $|11\rangle$.

**Predicted probability distribution:**
- '11': 1.0 (100%)

### Reference answer

{'predicted_probs': {'11': 1.0}, 'explanation': 'Pre-measurement phase gate removal. State |11>, index 3, P=1.0.'}

## isqTrain/1075

- task_id: `isqTrain/1075`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `difficult`
- concept_tags: `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `qubit_mapping`
- source: `isq_train_cot`
- dataset_index: `4789`

### Prompt

实现以下量子计算任务（使用isQ）：implements the token_swapping pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement token swapping via permutation [2,0,1] decomposed into transpositions, with an explicit X-X identity pair demonstrating gate cancellation.

2. **Qubits**: 3 qubits (q[0], q[1], q[2]), all measured at the end.

3. **State evolution**:
   - Start: |000⟩
   - X(q[0]): |100⟩
   - swap (three-CNOT decomposition)(q[1], q[2]): |100⟩ (no change, both are |0⟩)
   - swap (three-CNOT decomposition)(q[0], q[1]): |010⟩ (token "1" moves from q[0] to q[1])
   - X(q[0]): |110⟩
   - X(q[0]): |010⟩ (X-X = I, gates cancel)
   - Final state: |010⟩

4. **Expected probabilities**: The final state is |010⟩ with probability 1.0, since the X-X pair cancels and the swap (three-CNOT decomposition) sequence correctly implements the token movement.

## isqTrain/1029

- task_id: `isqTrain/1029`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `difficult`
- concept_tags: `basis_change`, `circuit_optimization`, `entanglement`
- source: `isq_train_cot`
- dataset_index: `884`

### Prompt

Code this in isQ: implements the clifford_optimization pattern using an alternative gate decomposition (CNOT -> H CZ H). The circuit must produce the same output as the standard decomposition.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

The goal is to implement a CNOT gate decomposition using H-CZ-H on the target qubit, and demonstrate it produces the same result as a standard CNOT.

Starting state: |00⟩

1. X(q[1]) → |01⟩ (flip q[1] to |1⟩)

2. H(q[0]) → (|0⟩ + |1⟩)/√2 ⊗ |1⟩ = (|01⟩ + |11⟩)/√2

3. CZ(q[1], q[0]) - This applies Z to q[0] when q[1] = |1⟩
   - CZ with q[1] as control and q[0] as target
   - When q[1] = |1⟩, apply Z to q[0]
   - Z|0⟩ = |0⟩, Z|1⟩ = -|1⟩
   - So: (|01⟩ - |11⟩)/√2

4. H(q[0]) → H on q[0]:
   - H(|01⟩ - |11⟩)/√2 = (H|0⟩⊗|1⟩ - H|1⟩⊗|1⟩)/√2
   - = ((|0⟩+|1⟩)⊗|1⟩ - (|0⟩-|1⟩)⊗|1⟩)/(2)
   - = (|01⟩+|11⟩ - |01⟩+|11⟩)/2
   - = 2|11⟩/2 = |11⟩

So the final state is |11⟩ with probability 1.0.

This is equivalent to CNOT(q[1], q[0]) acting on |01⟩, which would flip q[0] to get |11⟩.

The H-CZ-H decomposition on the target of a CNOT is a well-known identity: CNOT(c,t) = (I⊗H)·CZ(c,t)·(I⊗H), which reverses the roles effectively.

Wait, let me reconsider. The standard identity is:
- CNOT(c,t) = (I ⊗ H) · CZ · (I ⊗ H)

But here we have CZ(q[1], q[0]) with q[1] as control and q[0] as target. CZ is symmetric, so CZ(q[1], q[0]) = CZ(q[0], q[1]).

The H gates are applied to q[0]. So this implements:
- CNOT(q[0], q[1]) = H(q[0]) · CZ(q[0],q[1]) · H(q[0])

But wait, CZ(q[1], q[0]) = CZ(q[0], q[1]) since CZ is symmetric.

So we're implementing CNOT(q[0], q[1]) where q[0] is control and q[1] is target.

Starting from |01⟩:
- CNOT(q[0], q[1]) with q[0]=|0⟩ (control), q[1]=|1⟩ (target)
- Since q[0]=|0⟩, the target q[1] is NOT flipped
- So the result should be |01⟩

But The predicted output |11⟩... Let me re-trace.

Actually, wait. Let me re-read The implementation comments:

"Optimized: H*H*CNOT(0,1)*H*H = CNOT(1,0)"
"q[1]=1 controls, q[0] flips: |01> -> |11>"

So the H-CZ-H decomposition is implementing CNOT(q[1], q[0]) where q[1] is control and q[0] is target.

Let me verify: 
The identity is: CNOT(c,t) = (I_c ⊗ H_t) · CZ(c,t) · (I_c ⊗ H_t)

So if we want CNOT(q[1], q[0]):
- Control = q[1], Target = q[0]
- H on target q[0]
- CZ(q[1], q[0])
- H on target q[0]

This gives us CNOT(q[1], q[0]).

Starting state |01⟩:
- CNOT(q[1], q[0]) with q[1]=|1⟩ as control
- Since control is |1⟩, target q[0] flips from |0⟩ to |1⟩
- Result: |11⟩

Yes! This matches.

Let me verify my state evolution again:
1. |00⟩ → X(q[1]) → |01⟩
2. |01⟩ → H(q[0]) → (|01⟩ + |11⟩)/√2
3. CZ(q[1], q[0]) applies Z

## isqTrain/1032

- task_id: `isqTrain/1032`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `difficult`
- concept_tags: `basis_change`, `circuit_optimization`, `entanglement`
- source: `isq_train_cot`
- dataset_index: `4938`

### Prompt

帮我写一个isQ程序：implements the clifford_optimization pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

## Reasoning

1. Goal: Implement a Clifford-optimized circuit using the H-CNOT-H identity (reversing CNOT direction) with reversed measurement ordering to show index mapping effects.

2. Qubits: 2 qubits (q[0], q[1]), both measured with q[1] measured first (higher bit position), q[0] second (lower bit position).

3. State evolution:
   - |00⟩ → X(q[1]) → |01⟩
   - |01⟩ → CNOT(q[1], q[0]) with q[1]=|1⟩ as control, flips q[0] → |11⟩

4. Expected probabilities: The final state |11⟩ is an eigenstate. With reversed measurement order (M(q[1]) first = bit 1, M(q[0]) second = bit 0), bitstring "11" maps to |11⟩ with P(|11⟩) = 1.0.

## isqTrain/1074

- task_id: `isqTrain/1074`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `difficult`
- concept_tags: `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `qubit_mapping`
- source: `isq_train_cot`
- dataset_index: `1058`

### Prompt

实现以下量子计算任务（使用isQ）：implements the token_swapping pattern using an alternative gate decomposition (CNOT -> H CZ H). The circuit must produce the same output as the standard decomposition.

### Chain-of-thought reasoning

## Reasoning
- **Goal**: Implement a 3-cycle token swap (permutation [2,0,1]) on 3 qubits using CNOT → H-CZ-H decomposition, matching standard swap (three-CNOT decomposition) behavior.
- **Qubits**: 3 global qubits q[0], q[1], q[2], all measured at the end.
- **State evolution**:
  1. Initial state |100⟩ after X(q[0]).
  2. swap (three-CNOT decomposition)(q[1],q[2]) via H-CZ-H×3: both are |0⟩, so state remains |100⟩.
  3. swap (three-CNOT decomposition)(q[0],q[1]) via H-CZ-H×3: swaps |1⟩₀ and |0⟩₁, producing |010⟩.
- **Why expected probs**: Final state is exactly |010⟩, so measurement yields |010⟩ with probability 1.0. The H-CZ-H decomposition preserves CNOT semantics, ensuring the swap (three-CNOT decomposition) acts identically to the standard decomposition.
