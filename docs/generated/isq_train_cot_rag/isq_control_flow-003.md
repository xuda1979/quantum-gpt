# ISQ training COT RAG corpus: isq_control_flow shard 3

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1928

- task_id: `isqTrain/1928`
- task_type: `output_prediction`
- category: `isq_control_flow`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `514`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[4];
procedure main() {
    X(q[0]);
    X(q[2]);
    int a = M(q[0]);
    int b = M(q[1]);
    int c = M(q[2]);
    int d = M(q[3]);
    print a;
    print b;
    print c;
    print d;
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The 4-qubit register is initialized to the ground state |0000>.
2. Applying the X gate to `q[0]` flips its state to |1>, evolving the system to |1000>.
3. Applying the X gate to `q[2]` flips its state to |1>, evolving the system to |1010>.
4. This is a perfectly deterministic computational basis state with no superposition.
5. Measurements of q[0], q[1], q[2], and q[3] will yield 1, 0, 1, and 0 respectively with 100% probability.

Predicted probability distribution: {'1010': 1.0}

### Reference answer

{'predicted_probs': {'1010': 1.0}, 'explanation': 'Measurements and printing.'}

## isqTrain/1710

- task_id: `isqTrain/1710`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `280`

### Prompt

Help me write isQ code that Prepare a 7-qubit GHZ state using a for loop for the CNOT gates.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare a 7-qubit GHZ state (|0000000⟩ + |1111111⟩)/√2.
2. **Qubits**: 7 qubits (q[0] to q[6]), all measured at the end.
3. **Evolution**: Starting from |0000000⟩, apply H(q[0]) to get (|0⟩ + |1⟩)|000000⟩/√2 = (|0000000⟩ + |1000000⟩)/√2. The for loop applies CNOT(q[0], q[i]) for i=1 to 6, each entangling a new qubit with q[0]. After all CNOTs, the state becomes (|0000000⟩ + |1111111⟩)/√2.
4. **Probabilities**: Measuring the GHZ state yields |0000000⟩ with probability 0.5 and |1111111⟩ with probability 0.5.

## isqTrain/2548

- task_id: `isqTrain/2548`
- task_type: `code_equivalence`
- category: `isq_control_flow`
- difficulty: `intermediate`
- concept_tags: `global_phase`, `isq_syntax_arrays`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5215`

### Prompt

Do these two isQ programs produce the same measurement results?

Program A:
```isq
import std;

qbit q[2];

procedure main() {
    H(q[0]);
    int result = M(q[0]);
    switch result {
    case 0:
        X(q[1]);
    case 1:
        H(q[1]);
    }
    M(q[1]);
}

```

Program B:
```isq
import std;

qbit q[2];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    H(q[0]);
    int result = M(q[0]);
    switch result {
    case 0:
        X(q[1]);
    case 1:
        H(q[1]);
    }
    M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A:** Applies a Hadamard gate to q[0], measures it, and then classically conditions the operation on q[1]. If the measurement is 0, X is applied to q[1]; if 1, H is applied to q[1]. Finally, q[1] is measured.
2. **Program B:** Operates identically to Program A but adds a `GPhase(0.0)` gate at the beginning of the main procedure.
3. **Key difference:** Program B introduces a global phase of 0.0 before executing the exact same circuit as Program A.
4. **Probability equivalence:** The measurement probabilities are exactly the same because a global phase of $e^{i \cdot 0} = 1$ has no effect on the quantum state vector or measurement outcomes.
5. **Verdict:** Yes

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/534

- task_id: `isqTrain/534`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `expert`
- concept_tags: `isq_syntax_classical_vars`, `isq_syntax_if_else`, `isq_syntax_oracle`, `isq_syntax_print`, `isq_syntax_procedures`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3812`

### Prompt

用isQ实现implements a variant of the oracle_parity_check pattern using q[4] -> q[6]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

Looking at this task, I need to create an isQ program that implements a variant of the oracle_parity_check pattern using q[4] -> q[6], with additional qubits in the ground state.

Let me analyze The implementation:
1. It uses recursive Fourier sampling
2. It has oracles A (4,1) and g (2,1)
3. The main qubit register is q[6] and ancilla is p[3]
4. The measurement is on p[0] and expects |1> with probability 1.0

The task says to use q[4] -> q[6], meaning I need to expand the qubit register. The additional qubits should be left in the ground state.

Analyzing the:
- q[6] is the main register
- p[3] is used for parity/results
- The recursive function uses q[0], q[1], q[2], q[3] and p[0], p[1], p[2]

For q[4] -> q[6], I need to modify this to use more qubits but leave the extras in |0>.

Actually, let me re-read the task. It says "q[4] -> q[6]" which might mean using qubits q[4] through q[6] (so q[4], q[5], q[6]), or it might mean expanding the register from 4 qubits to 6 qubits.

Given the context "significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state", I think this means:
- The base version might use fewer qubits
- We expand to use more qubits
- The extra qubits are not used (stay in |0>)

So I'll create a version with q[8] or q[7] instead of q[6], where the extra qubits are unused.

Let me think about what the circuit does:
- This is recursive Fourier sampling for a parity check oracle
- Oracle A is defined with specific truth values
- Oracle g is a 2-qubit to 1 oracle
- The recursive structure creates a Fourier sampling pattern

For the variant with expanded register:
- I'll use q[8] instead of q[6]
- Keep the same logic but have q[4], q[5], q[6], q[7] unused (in |0>)
- Still measure p[0] at the end

Wait, re-reading again: "q[4] -> q[6]" could mean:
1. Use qubits indexed 4 through 6
2. Expand register from size 4 to size 6
3. Some other meaning

Given the reference already has q[6], I think the variant should have more qubits. Let me use q[8] and leave q[4], q[5], q[6], q[7] in ground state.

Actually, looking more carefully, the task says to write an isQ program, and I need to generate reasoning, not code. The code was already provided as reference. Let me focus on the reasoning.

The reasoning should explain:
1. Goal: Implement oracle parity check with expanded register
2. Qubits: 8 qubits in main register + 3 in ancilla, measuring p[0]
3. State evolution through the recursive Fourier sampling
4. Why p[0] ends up in |1> with probability 1.0

Let me trace through the circuit:

Initial state: |00000000000000> (8 main qubits + 3 ancilla + extras)

The recursive_fourier_sampling(0) will:
1. k=0: Apply H to q[0], q[1]; X then H to p[1]; recurse to k=1
2. k=1: Apply H to q[2], q[3]; X then H to p[2]; recurse to k=2
3. k=2: Apply oracle A(q[0],q[1],q[2],q[3],p[2])
4. Return to k=1: H on q[2],q[3]; g(q[2],q[3],p[1]); H on q[2],q[3]; recurse to k=2
5. k=2 again: Apply oracle A
6. Return to k=1: H on q[2],q[3]; H on p[2]; X on p[2]
7. Return to k=0: H on q[0],q[1]; g(q[0],q[1],p[0]); H on q[0],q[1]; recurse to k=1
8. k=1: Similar structure...

This is getting complex. Let me simplify for the reasoning.

The key insight

## isqTrain/283

- task_id: `isqTrain/283`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_print`
- source: `isq_train_cot`
- dataset_index: `2841`

### Prompt

Code this in isQ: implements the gate_decomposition pattern but with a different initial state preparation (flip q[[0, 2]] -> q[1]).

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare state |0100⟩ by flipping q[1], then measure all 4 qubits.
2. **Qubits**: 4 qubits (q[0], q[1], q[2], q[3]), all measured.
3. **State evolution**: Initial state |0000⟩ → Apply X(q[1]) → |0100⟩.
4. **Measurements**: M(q[0])=0, M(q[1])=1, M(q[2])=0, M(q[3])=0, giving deterministic outcome |0100⟩ with probability 1.0.

## isqTrain/1649

- task_id: `isqTrain/1649`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `basic`
- concept_tags: `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `686`

### Prompt

Create an isQ quantum circuit that Apply Hadamard gate 6 times using a for loop. Since H^2=I, an even number of H applications yields identity.

### Chain-of-thought reasoning

## Reasoning
The goal is to apply the Hadamard gate 6 times to a qubit, demonstrating that an even number of applications acts as the identity operation ($H^2 = I$).
One qubit is required and measured.
The qubit starts in the initial state $|0\rangle$. Because $H^2 = I$, applying H six times is equivalent to applying the identity three times: $H^6 |0\rangle = (H^2)^3 |0\rangle = I^3 |0\rangle = |0\rangle$.
Therefore, the quantum state remains unchanged at $|0\rangle$, resulting in a 100% probability of measuring $|0\rangle$.

## isqTrain/1689

- task_id: `isqTrain/1689`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_for_loop`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `2325`

### Prompt

实现以下量子计算任务（使用isQ）：Use a for loop for CNOT fan-out: q[0] controls all others on 3 qubits from |100>.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply CNOT fan-out from q[0] to q[1] and q[2], starting in |100⟩.
Three qubits are used, all measured at the end.
1. Initial state |000⟩ → X(q[0]) → |100⟩
2. CNOT(q[0], q[1]) flips q[1] since control q[0]=|1⟩: |100⟩ → |110⟩
3. CNOT(q[0], q[2]) flips q[2] since control q[0]=|1⟩: |110⟩ → |111⟩
Final state |111⟩ is a computational basis state, yielding measurement probability {|111⟩: 1.0}.

## isqTrain/1625

- task_id: `isqTrain/1625`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `basic`
- concept_tags: `isq_syntax_for_loop`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5140`

### Prompt

实现以下量子计算任务（使用isQ）：Apply Hadamard to each of 2 qubits using a for loop. Measure all qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a uniform superposition over 2 qubits using Hadamard gates and measure the result.
2. **Qubits**: 2 qubits (q[0], q[1]), both measured.
3. **State evolution**:
   - Initial: |00>
   - After H(q[0]): (|0> + |1>)/√2 ⊗ |0> = (|00> + |10>)/√2
   - After H(q[1]): (|00> + |01> + |10> + |11>)/2 = |++>
4. **Probabilities**: The final state |++> has equal amplitude 1/2 for each computational basis state, giving uniform measurement probabilities: P(|00>) = P(|01>) = P(|10>) = P(|11>) = 0.25.

## isqTrain/1628

- task_id: `isqTrain/1628`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `basic`
- concept_tags: `isq_syntax_for_loop`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4798`

### Prompt

Code this in isQ: Apply Hadamard to each of 6 qubits using a for loop. Measure all qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Create a uniform superposition over all 2^6 basis states by applying Hadamard to each of 6 qubits, then measure all qubits.
Qubits: 6 qubits declared (q[0]–q[5]), all measured via M(q[i]).

State evolution:
1. Initial state: |000000⟩
2. For each qubit i from 0 to 5, H(q[i]) transforms |0⟩ → |+⟩ = (|0⟩ + |1⟩)/√2
3. After all 6 H gates: (|0⟩+|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2 ⊗ ... (6 times) = (1/√2)^6 × Σ|x⟩ for all x∈{0,1}^6

Each of the 64 basis states |x⟩ has amplitude 1/8, giving probability |1/8|² = 1/64 = 0.015625 for every outcome.

## isqTrain/253

- task_id: `isqTrain/253`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_while_loop`
- source: `isq_train_cot`
- dataset_index: `413`

### Prompt

Write isQ code for the following quantum task: implements the arithmetic_circuit pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Apply a cumulative X-rotation of π/2 to q[0] via a loop, then measure both qubits in reversed order.

2. **Qubits**: 2 qubits (q[0], q[1]); both are measured: q[1] first, q[0] second.

3. **State evolution**:
   - Initial state: |0⟩⊗|0⟩ = |00⟩
   - Loop applies Rx(π/6) to q[0] three times, totaling Rx(π/2):
     Rx(π/2)|0⟩ = cos(π/4)|0⟩ - i·sin(π/4)|1⟩ = (1/√2)|0⟩ - i
