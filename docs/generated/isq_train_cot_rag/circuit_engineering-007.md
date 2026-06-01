# ISQ training COT RAG corpus: circuit_engineering shard 7

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1027

- task_id: `isqTrain/1027`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `difficult`
- concept_tags: `basis_change`, `circuit_optimization`, `entanglement`
- source: `isq_train_cot`
- dataset_index: `530`

### Prompt

Write an isQ program that implements a variant of the clifford_optimization pattern using q[2] -> q[4]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for an isQ program that implements a variant of the clifford_optimization pattern using q[2] -> q[4]. Analyzing the circuit requirements, I need to understand what's happening:

1. The reference uses q[4] (4 qubits)
2. It applies X(q[1]) to set q[1] to |1>
3. It applies CNOT(q[1], q[0]) - which reverses the original CNOT direction through H-CNOT-H optimization
4. The predicted output |1100> with probability 1.0

Now the task says "using q[2] -> q[4]" and "significantly expanded qubit register compared to the base version, with additional qubits left in the ground state."

Wait, let me re-read. The task says "q[2] -> q[4]" - this might mean using qubits q[2] through q[4], or it might mean a register size of some kind.

Analyzing the, it uses q[4] (4 qubits, indices 0-3), and The predicted output |1100> meaning q[0]=1, q[1]=1, q[2]=0, q[3]=0.

If the variant should use q[2] -> q[4], perhaps I need to interpret this as using qubits 2, 3, 4 (indices) which would mean I need at least 5 qubits (q[0] to q[4]).

Actually, re-reading more carefully: "using q[2] -> q[4]" might mean using a register from size 2 to size 4, or it could mean using qubits at indices 2 through 4.

The reference uses 4 qubits. If I need to use q[2] to q[4], that's 3 qubits at indices 2, 3, 4. But the reference expects |1100> on 4 qubits.

Let me think about this differently. The implementation:
- Uses q[4] (4 qubits)
- Sets q[1] to |1>
- Does CNOT(q[1], q[0])
- Measures all 4 qubits
- Expected: |1100>

For a variant using q[2] -> q[4], I might need to:
- Use a larger register (say 5 qubits: q[0] to q[4])
- Perform the same pattern but on qubits 2 through 4
- Leave additional qubits (0, 1) in ground state

So I'd need at least 5 qubits. Let me design:
- q[5] register
- Use q[2], q[3], q[4] for the Clifford optimization pattern
- X(q[3]) to set q[3] to |1>
- CNOT(q[3], q[2]) to flip q[2]
- Result on q[2], q[3]: |11>
- q[4], q[0], q[1] remain |0>

predicted output bitstring: If I measure all 5 qubits in order M(q[0]), M(q[1]), M(q[2]), M(q[3]), M(q[4]):
- q[0] = 0, q[1] = 0, q[2] = 1, q[3] = 1, q[4] = 0
- Bitstring with earlier measured = higher bit: |00110> = decimal 6

But wait, the reference predicted output was |1100> for 4 qubits measured as M(q[0]), M(q[1]), M(q[2]), M(q[3]) where q[0]=1 is the highest bit.

Hmm, let me re-check the reference:
- X(q[1]) sets q[1] to |1>
- CNOT(q[1], q[0]) with q[1] as control, q[0] as target
- Initial state: |00> -> X(q[1]) -> |01> -> CNOT(q[1], q[0]) -> q[1] is 1, so flip q[0] -> |11>
- q[2], q[3] remain |0>
- Measure all: q[0]=1, q[1]=1, q[2]=0, q[3]=0
- Bitstring |1100> ✓

Now for variant using q[2] -> q[4]:
- Register size: at least 5 (indices 0-4)
- X(q[3]) sets q[3] to |1>
- CNOT(q[3], q[2]) with q[3] as control, q[

## isqTrain/1681

- task_id: `isqTrain/1681`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `3552`

### Prompt

请用isQ语言编写一个量子电路：a quantum half adder for inputs a=0, b=1. Use q[0]=a, q[1]=b, q[2]=sum, q[3]=carry. Compute sum = a XOR b and carry = a AND b.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a quantum half adder for classical inputs a=0, b=1 to calculate sum (a XOR b) and carry (a AND b).
2. **Qubits**: 4 qubits are used ($q[0]=a, q[1]=b, q[2]=sum, q[3]=carry$), and all are measured.
3. **State Evolution**:
   - Initialize to $|0000\rangle$.
   - $X(q[1])$ sets input b=1: state becomes $|0100\rangle$.
   - $CNOT(q[0], q[2])$ copies input a to sum: state remains $|0100\rangle$.
   - $CNOT(q[1], q[2])$ XORs input b into sum: state becomes $|0110\rangle$.
   - `ctrl ctrl X(q[0], q[1], q[3])` (Toffoli) computes a AND b into carry: state remains $|0110\rangle$ (since $q[0]=0$).
4. **Expected Probabilities**: The final state is deterministically $|0110\rangle$, which represents the measurement bitstring '0110' (with earlier measured qubits as higher bits), yielding a probability of 1.0.

## isqTrain/1031

- task_id: `isqTrain/1031`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `difficult`
- concept_tags: `basis_change`, `circuit_optimization`, `entanglement`
- source: `isq_train_cot`
- dataset_index: `2594`

### Prompt

用isQ实现implements the clifford_optimization pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement a Clifford circuit demonstrating H-H cancellation, resulting in a deterministic |11⟩ state.

Qubits: 2 (q[0], q[1]), both measured.

State evolution:
1. Initial: |00⟩
2. X(q[1]): |00⟩ → |01⟩
3. CNOT(q[1], q[0]): q[1]=1 is control, flips q[0]: |01⟩ → |11⟩
4. H(q[0]): |11⟩ → (|01⟩ - |11⟩)/√2
5. H(q[0]): H² = I, so state returns to |11⟩

Since the final state before measurement is |11⟩, both qubits measure as 1 with certainty, yielding probability distribution {|11⟩: 1.0}.

## isqTrain/1021

- task_id: `isqTrain/1021`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `difficult`
- concept_tags: `basis_change`, `circuit_optimization`, `global_phase`
- source: `isq_train_cot`
- dataset_index: `5508`

### Prompt

用isQ实现implements a variant of the template_matching_opt pattern using q[1] -> q[3]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a template-matching-optimized circuit on an expanded register, applying X then Z to one qubit (equivalent to H-X-H) while extra qubits stay in |0⟩.
2.

## isqTrain/1683

- task_id: `isqTrain/1683`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `4940`

### Prompt

请用isQ语言编写一个量子电路：a quantum half adder for inputs a=1, b=1. Use q[0]=a, q[1]=b, q[2]=sum, q[3]=carry. Compute sum = a XOR b and carry = a AND b.

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants a concise reasoning section (3-15 lines) explaining the provided quantum half-adder circuit, written from the perspective of a quantum computing expert. It should trace the state evolution using Dirac notation.

2.  **Analyze the Circuit**:
    *   Inputs: $a=1$ ($X(q[0])$), $b=1$ ($X(q[1])$).
    *   Initial state: $|0000\rangle$.
    *   After X gates on q[0], q[1]: $|1100\rangle$.
    *   Sum computation (CNOT(q[0], q[2]) then CNOT(q[1], q[2])):
        *   CNOT(q[0], q[2]) flips q[2] because q[0] is 1. State: $|1110\rangle$.
        *   CNOT(q[1], q[2]) flips q[2] because q[1] is 1. State: $|1100\rangle$. Wait, let me re-verify. Initial: 1100. CNOT(0,2) -> 1110. CNOT(1,2) -> 1100. But wait, q[2] was |0>, first CNOT flips to |1>, second CNOT flips to |0>. Sum is 0.
    *   Carry computation (Toffoli(q[0], q[1], q[3])):
        *   ctrl ctrl X(q[0], q[1], q[3]) is a Toffoli gate.
        *   Because q[0]=1 and q[1]=1, it flips q[3]. State: $|1101\rangle$. Carry is 1.
    *   Measurement: All 4 qubits.

3.  **Draft the Reasoning**:
    *   Goal: Implement a quantum half adder for $1+1=0$ (sum), $1$ (carry).
    *   Setup: Requires 4 qubits; all are measured.
    *   Evolution:
        *   Start at $|0000\rangle$.
        *   Apply $X$ to $q_0, q_1 \rightarrow |1100\rangle$.
        *   Apply CNOTs for sum: $q_2 \oplus q_0 = 1$, then $q_2 \oplus q_1 = 0$, state $\rightarrow |1100\rangle$.
        *   Apply Toffoli for carry: $q_3 \oplus q_0 \cdot q_1 = 1$, state $\rightarrow |1101\rangle$.
    *   Expected outcome: The final state is deterministically $|1101\rangle$, yielding a 100% measurement probability for this bitstring.

4.  **Refine and Format**:
    *   Check rules: ONLY reasoning starting with "## Reasoning", no code, precise Dirac notation, concise.
    *   Ensure bit order in Dirac notation matches standard convention (usually $q_0 q_1 q_2 q_3$ or $q_3 q_2 q_1 q_0$ depending on endianness. isQ standard typically uses little-endian in Dirac for probabilities or matches the array indices. Let's use $|q_0 q_1 q_2 q_3\rangle$).
    *   Let's trace: $|0000\rangle \xrightarrow{X_0 X_1} |1100\rangle$.
    *   CNOT$_{0,2}$: $q_0=1 \rightarrow X$ on $q_2 \rightarrow |1110\rangle$.
    *   CNOT$_{1,2}$: $q_1=1 \rightarrow X$ on $q_2 \rightarrow |1100\rangle$.
    *   Toffoli$_{0,1,3}$: $q_0=1, q_1=1 \rightarrow X$ on $q_3 \rightarrow |1101\rangle$.
    *   Wait, is $|1101\rangle$ read as $q_0 q_1 q_2 q_3$? Yes. Let's explicitly state it: $|q_0 q_1 q_2 q_3\rangle = |1101\rangle$. The expected string from prompt is `|1101>`.

5.  **Final Polish**:
    ## Reasoning
    1. **Goal:** Implement a quantum half adder for $a=1, b=1$ to compute the sum ($1 \oplus 1 = 0$) and carry ($1 \land 1 = 1$).
    2. **

## isqTrain/1045

- task_id: `isqTrain/1045`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `expert`
- concept_tags: `circuit_optimization`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3217`

### Prompt

Implement the following in isQ: implements the solovay_kitaev pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement the Solovay-Kitaev pattern where Z is decomposed into T^4, with an explicit H-H identity pair to demonstrate gate cancellation awareness.
2. **Qubits**: 1 qubit `q[0]` is used and measured.
3. **State evolution**:
   - `X(q[0])`: |0⟩ → |1⟩
   - `T(q[0])` × 4: |1⟩ → e^(iπ)|1⟩ = -|1⟩ (since T^4 = Z, and Z|1⟩ = -|1⟩)
   - `H(q[0])`: -|1⟩ → -(|0⟩ - |1⟩)/√2 = -(1/√2)|0⟩ + (1/√2)|1⟩
   - `H(q[0])` (identity pair): Back to -|1⟩ (since HH = I, global phase preserved)
4. **Expected probabilities**: The final state -|1⟩ differs from |1⟩ only by a global phase, so measuring yields |1⟩ with probability 1.0.

## isqTrain/1036

- task_id: `isqTrain/1036`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `basic`
- concept_tags: `circuit_optimization`, `global_phase`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2358`

### Prompt

Write an isQ program that implements a variant of the pre_measurement_opt pattern using q[2] -> q[3]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Implement a 3-qubit pre_measurement_opt variant where diagonal phase gates are removed before measurement.
2. Three qubits (q[0], q[1], q[2]) are used and all measured; the circuit initializes q[0] and q[1] to |1⟩.
3. State evolution: |000⟩ → X(q[0]) → |100⟩ → X(q[1]) → |110⟩; q[2] remains |0⟩ throughout.
4. Diagonal gates (S, Rz, Z) are omitted since they only add phases without changing measurement probabilities.
5. Final state |110⟩ yields measurement outcome q[0]=1, q[1]=1, q[2]=0 → bitstring |110⟩ with probability 1.0.

## isqTrain/1012

- task_id: `isqTrain/1012`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `circuit_optimization`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1677`

### Prompt

I need an isQ program to implements a variant of the gate_consolidation pattern using q[1] -> q[2]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement gate consolidation on an expanded 3-qubit register, applying X and consolidated Rz to q[1] (variant of the base pattern).
2. **Qubits**: 3 qubits (q[3]), all measured; operations target q[1].
3. **State evolution**:
   - Initial state: |000⟩
   - X(q[1]): |010⟩

## isqTrain/1057

- task_id: `isqTrain/1057`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `qubit_mapping`
- source: `isq_train_cot`
- dataset_index: `550`

### Prompt

用isQ实现implements the sabre_routing pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a SABRE-inspired routing pattern (swap (three-CNOT decomposition)-CNOT-swap (three-CNOT decomposition) for non-adjacent qubits) with identity H-H pairs demonstrating gate cancellation.
2. **Qubits**: 3 qubits (q[0], q[1], q[2]), all measured.
3. **State evolution**:
   - Start: |000⟩
   - X(q[0]): |100⟩
   - swap (three-CNOT decomposition)(q[0],q[1]): |010⟩ — routes original q[0] data adjacent to q[2]
   - CNOT(q[1],q[2]): |110⟩ — flips q[2] since q[1]=|1⟩
   - swap (three-CNOT decomposition)(q[0],q[1]): |101⟩ — restores original layout
   - H(q[0]): (|001⟩−|101⟩)/√2 — superposition on q[0]
   - H(q[0]): |101⟩ — H-H identity cancels out
4. **Expected measurement**: Final state |101⟩ yields probability {|101⟩: 1.0}, confirming H-H cancellation preserves the routed CNOT result.

## isqTrain/1014

- task_id: `isqTrain/1014`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `circuit_optimization`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2076`

### Prompt

Implement a quantum circuit in isQ: implements the gate_consolidation pattern with modified rotation parameters (num_pi2s_to_pi3). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Demonstrate gate consolidation by merging two Rz(π/4) rotations into a single Rz(π/2) while preserving measurement outcomes.
2. **Qubits**: 1 qubit (`q[0]`), which is measured.
3. **State evolution**:
   - Initial: |0⟩
   - After X: |1⟩
   - After Rz(π/2): e^{iπ/4}|1⟩ (Rz adds phase e^{iθ/2} to |1⟩; global phase is physically meaningless)
4. **Expected probabilities**: Since Rz only adds a phase to computational basis states, the measurement distribution is unchanged—P(|1⟩) = 1.0.
