# ISQ training COT RAG corpus: circuit_engineering shard 6

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1005

- task_id: `isqTrain/1005`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `circuit_optimization`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5041`

### Prompt

Write an isQ program that implements a variant of the gate_cancellation pattern using q[2] -> q[3]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement a gate cancellation pattern on 4 qubits where CNOT pairs self-cancel and triple X gates reduce to a single X.

2. **Qubits**: 4-qubit register q[0..3], all measured; cancellation occurs on q[2]→q[3].

3. **State evolution**:
   - |0000⟩ — initial state
   - X(q[0]) → |1000⟩
   - CNOT(q[2], q[3]) → |1000⟩ (control q[2]=0, no flip)
   - CNOT(q[2], q[3]) → |1000⟩ (cancels previous CNOT)
   - X(q[2]); X(q[2]); X(q[2]) — net effect is single X(q[2]) → |1010⟩
   - Final state: |1010⟩

4. **Expected probabilities**: {|1010⟩: 1.0} since all operations are deterministic unitaries starting from |0000⟩, and the triple-X reduces to one X on q[2].

## isqTrain/1680

- task_id: `isqTrain/1680`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `3942`

### Prompt

请用isQ语言编写一个量子电路：a quantum half adder for inputs a=0, b=0. Use q[0]=a, q[1]=b, q[2]=sum, q[3]=carry. Compute sum = a XOR b and carry = a AND b.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Implement a quantum half adder for a=0, b=0, computing sum = a XOR b and carry = a AND b.

**Qubits:** 4 qubits used (q[0]=a, q[1]=b, q[2]=sum, q[3]=carry). All 4 are measured.

**State evolution:**
1. Initial state: |0000⟩ (all qubits in |0⟩)
2. CNOT(q[0], q[2]): Control q[0]=|0⟩, target q[2] unchanged → |0000⟩
3. CNOT(q[1], q[2]): Control q[1]=|0⟩, target q[2] unchanged → |0000⟩
4. Toffoli(q[0], q[1], q[3]): Controls q[0], q[1] both |0⟩, target q[3] unchanged → |0000⟩

**Result:** Since both inputs are |0⟩, no gates activate. The final state |0000⟩ yields measurement probability P(|0000⟩)=1.0, confirming sum=0 and carry=0.

## isqTrain/1065

- task_id: `isqTrain/1065`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `qubit_mapping`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4034`

### Prompt

Implement the following in isQ: implements the vf2_mapping pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement a VF2-mapped CNOT circuit with H-H identity pair demonstrating gate cancellation.

2. **Qubits**: 3 qubits (q[0], q[1], q[2]); all measured via M(q[0]), M(q[1]), M(q[2]).

3. **State evolution**:
   - Initial: |000⟩
   - X(q[0]): |100⟩ (flip q[0])
   - X(q[1]): |110⟩ (flip q[1])
   - CNOT(q[0], q[2]): |111⟩ (control=1, flip q[2])
   - CNOT(q[1], q[2]): |110⟩ (control=1, flip q[2] back)
   - H(q[0]): |−⟩⊗|10⟩ = (1/√2)(|010⟩ − |110⟩)
   - H(q[0]): H†H = I on q[0], restoring |110⟩

4. **Expected probabilities**: Final state is |110⟩ with certainty, so measurement yields bitstring 110 (q[0]=MSB) with probability 1.0. The H-H pair cancels to identity, leaving the pre-Hadamard state unchanged.

## isqTrain/1682

- task_id: `isqTrain/1682`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `3706`

### Prompt

实现以下量子计算任务（使用isQ）：a quantum half adder for inputs a=1, b=0. Use q[0]=a, q[1]=b, q[2]=sum, q[3]=carry. Compute sum = a XOR b and carry = a AND b.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement a quantum half adder computing sum = a XOR b and carry = a AND b for inputs a=1, b=0.

Using 4 qubits: q[0]=a, q[1]=b, q[2]=sum, q[3]=carry, all measured.

State evolution:
- Initial: |0000⟩
- X(q[0]): |1000⟩ (sets a=1)
- CNOT(q[0], q[2]): |1010⟩ (q[2] flips since q[0]=1, computing sum bit from a)
- CNOT(q[1], q[2]): |1010⟩ (q[1]=0 so no flip; sum = 1⊕0 = 1)
- ctrl ctrl X(q[0], q[1], q[3]): |1010⟩ (Toffoli gate; carry = a∧b = 1∧0 = 0, no flip)

Final state |1010⟩ (a=1, b=0, sum=1, carry=0) yields measurement probability {|1010⟩: 1.0} since all operations are deterministic on computational basis states.

## isqTrain/1076

- task_id: `isqTrain/1076`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `difficult`
- concept_tags: `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `qubit_mapping`
- source: `isq_train_cot`
- dataset_index: `1861`

### Prompt

实现以下量子计算任务（使用isQ）：implements the token_swapping pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement permutation [2,0,1] via token-swapping (two SWAPs) on 3 qubits, with an H-H identity pair to demonstrate gate cancellation.

2. **Qubits**: 3 qubits (q[0], q[1], q[2]), all measured.

3. **State evolution**:
   - Initial: |000⟩
   - After X(q[0]): |100⟩
   - swap_gate(q[1], q[2]): No change (both qubits are |0⟩), state remains |100⟩
   - swap_gate(q[0], q[1]): CNOT(q[0],q[1])→|110⟩, CNOT(q[1],q[0])→|010⟩, CNOT(q[0],q[1])→|010⟩
   - After first H(q[0]): |+⟩|1⟩|0⟩ = (1/√2)(|010⟩ + |110⟩)
   - After second H(q[0]): H|+⟩ = |0⟩, returning to |010⟩ (H-H = identity, demonstrating gate cancellation)

4. **Expected probabilities**: The H-H pair cancels, leaving the final state |010⟩. With M(q[0]), M(q[1]), M(q[2]) measured in order (earlier = higher bit), the bitstring is 010, so P(|010⟩) = 1.0.

## isqTrain/1047

- task_id: `isqTrain/1047`
- task_type: `output_prediction`
- category: `circuit_engineering`
- difficulty: `expert`
- concept_tags: `circuit_optimization`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1658`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[1];

// Solovay-Kitaev decomposition: Z = T^4
// T = Rz(pi/4), so T^4 = Rz(pi) = Z
procedure main() {
    // Set qubit to |1>
    X(q[0]);
    // Decompose Z into four T gates
    // T^2 = S (pi/2 phase), T^4 = S^2 = Z (pi phase)
    T(q[0]);
    T(q[0]);
    T(q[0]);
    T(q[0]);
    // Phase on |1> does not affect measurement probability
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initial State:** The qubit `q[0]` starts in the ground state |0>.
2. **X Gate:** The `X(q[0])` gate flips the qubit to the excited state |1>.
3. **T Gates:** Four successive `T(q[0])` gates are applied. The T gate applies a $\pi/4$ phase to |1>. Applying it four times applies a $\pi$ phase ($4 \times \pi/4 = \pi$), which is functionally equivalent to a Z gate ($T^4 = Z$).
4. **Final State:** The quantum state becomes $e^{i\pi}|1\rangle = -|1\rangle$. Since global phase does not affect measurement probabilities, the state is effectively |1>.
5. **Measurement:** Measuring the state yields |1> with certainty.

Predicted probability distribution: {|1>: 1.0}

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Parametric variant of isqEval/320. Dimension: predict probabilities for reference circuit.'}

## isqTrain/2056

- task_id: `isqTrain/2056`
- task_type: `output_prediction`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `qubit_mapping`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3930`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[3];
procedure main() {
    X(q[0]);
    X(q[1]);
    CNOT(q[0], q[2]);
    CNOT(q[1], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations**: The circuit initializes 3 qubits in $|000\rangle$. It applies X gates to `q[0]` and `q[1]`, followed by two CNOT gates targeting `q[2]`.
2. **State Evolution**:
   - Initial state: $|000\rangle$
   - After `X(q[0])` and `X(q[1])`: The state becomes $|110\rangle$.
   - After `CNOT(q[0], q[2])`: The control `q[0]` is $|1\rangle$, flipping the target `q[2]` to $|1\rangle$, resulting in $|111\rangle$.
   - After `CNOT(q[1], q[2])`: The control `q[1]` is $|1\rangle$, flipping the target `q[2]` back to $|0\rangle$, returning the state to $|110\rangle$.
3. **Final State**: The quantum state before measurement is exactly $|110\rangle$.
4. **Measurement**: Me

### Reference answer

{'predicted_probs': {'110': 1.0}, 'explanation': 'VF2 mapping on triangle. State |110>, index 6, P=1.0.'}

## isqTrain/1042

- task_id: `isqTrain/1042`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `expert`
- concept_tags: `circuit_optimization`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `589`

### Prompt

Implement a quantum circuit in isQ: implements a variant of the solovay_kitaev pattern using q[1] -> q[2]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement a Solovay-Kitaev style decomposition where T^4 = Z, applied to demonstrate phase accumulation on a multi-qubit register.

2. **Qubits**: Uses 2-qubit register q[2]; both q[0] and q[1] are measured.

3. **State evolution**:
   - Initial state: |00⟩
   - X(q[0]): |00⟩ → |10⟩
   - T(q[0]) #1: |10⟩ → e^(iπ/4)|10⟩ (T applies phase e^(iπ/4) to |1⟩ component)
   - T(q[0]) #2: → e^(iπ/2)|10⟩ = i|10⟩ (equivalent to S gate)
   - T(q[0]) #3: → e^(i3π/4)|10⟩
   - T(q[0]) #4: → e^(iπ)|10⟩ = -|10⟩ (equivalent to Z gate; global phase unobservable)

4. **Expected probabilities**: The final state is -|10⟩, which is physically equivalent to |10⟩ up to global phase. Measuring both qubits yields |10⟩ with probability 1.0, as confirmed by the predicted output {|10>: 1.0}.

## isqTrain/1044

- task_id: `isqTrain/1044`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `expert`
- concept_tags: `circuit_optimization`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4720`

### Prompt

Write isQ code for the following quantum task: implements the solovay_kitaev pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Demonstrate Solovay-Kitaev decomposition (Z = T⁴) with an explicit X-X identity pair for gate cancellation awareness.
2. **Qubits**: 1 qubit (`q[0]`), measured at the end.
3. **State evolution**:
   - `X(q[0])`: |0⟩ → |1⟩
   - `T(q[0])` × 4: |1⟩ → e^(iπ)|1⟩ = −|1⟩ (T⁴ = Z, applies π phase to |1⟩)
   - `X(q[0])`: −|1⟩ → −|0⟩
   - `X(q[0])`: −|0⟩ → −|1⟩ (X-X pair is identity; state returns to −|1⟩)
4. **Measurement**: The final state −|1⟩ differs from |1⟩ only by a global phase, so measurement yields |1⟩ with probability 1.0.

## isqTrain/1080

- task_id: `isqTrain/1080`
- task_type: `output_prediction`
- category: `circuit_engineering`
- difficulty: `difficult`
- concept_tags: `isq_syntax_deriving_gate`, `isq_syntax_procedures`, `qubit_mapping`
- source: `isq_train_cot`
- dataset_index: `1501`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;

// SWAP gate for token swapping
procedure swap_gate(qbit a, qbit b) {
    CNOT(a, b);
    CNOT(b, a);
    CNOT(a, b);
} deriving gate

qbit q[3];

// Permutation [2,0,1]: a 3-cycle decomposed into two SWAPs
procedure main() {
    // Initialize: q[0]=1, q[1]=0, q[2]=0
    X(q[0]);
    // Decompose permutation [2,0,1] into transpositions:
    // [2,0,1] = SWAP(1,2) followed by SWAP(0,1)
    // Step 1: SWAP q[1] and q[2] (both 0, no visible change)
    swap_gate(q[1], q[2]);
    // Step 2: SWAP q[0] and q[1] (moves the 1 from q[0] to q[1])
    swap_gate(q[0], q[1]);
    // Result: q[0]=0, q[1]=1, q[2]=0
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis

1. **Operations applied:**
   - `X(q[0])` — flips q[0] from |0⟩ to |1⟩
   - `swap_gate(q[1], q[2])` — swap (three-CNOT decomposition) between q[1] and q[2]
   - `swap_gate(q[0], q[1])` — swap (three-CNOT decomposition) between q[0] and q[1]

2. **State evolution:**
   - Initial state: |000⟩
   - After `X(q[0])`: |100⟩
   - After `swap (three-CNOT decomposition)(q[1], q[2])`: |100⟩ (both q[1], q[2] are |0⟩, so swap (three-CNOT decomposition) has no effect)
   - After `swap (three-CNOT decomposition)(q[0], q[1])`: |010⟩ (the |1⟩ moves from q[0] to q[1])

3. **Final state before measurement:** |010⟩

4. **Probability distribution:**
   The system is in a definite computational basis state |010⟩, so measurement yields this outcome with certainty. This implements the permutation [2,0,1] applied to the initial one-hot token at position 0, moving it to position 1.

**Predicted probability distribution:** {|010⟩: 1.0}

### Reference answer

{'predicted_probs': {'2': 1.0}, 'explanation': 'Parametric variant of isqEval/324. Dimension: predict probabilities for reference circuit.'}
