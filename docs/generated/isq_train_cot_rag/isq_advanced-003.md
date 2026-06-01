# ISQ training COT RAG corpus: isq_advanced shard 3

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1696

- task_id: `isqTrain/1696`
- task_type: `code_generation`
- category: `isq_advanced`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_classical_vars`, `isq_syntax_for_loop`, `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `2934`

### Prompt

Help me write isQ code that Define a procedure that applies X gate n times, call it with n=1. Measure the result.

### Chain-of-thought reasoning

## Reasoning
1. The goal is to apply the X gate to a single qubit and measure the resulting state.
2. One qubit is required, and it is the only qubit measured at the end of the circuit.
3. The qubit initializes in the ground state: |0>.
4. The procedure applies the X gate exactly once (n=1), which flips the state: X|0> = |1>.
5. The final quantum state is exactly |1>, so a measurement yields a 100% probability of observing |1>.

## isqTrain/1711

- task_id: `isqTrain/1711`
- task_type: `code_generation`
- category: `isq_advanced`
- difficulty: `difficult`
- concept_tags: `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `2910`

### Prompt

请用isQ语言编写一个量子电路：Apply double-negative-controlled X (nctrl nctrl X) to |000>. Target flips only when both controls are |0>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply a double-negative-controlled X gate to |000>, flipping the target qubit only when both control qubits are in |0⟩.
2. **Qubits**: 3 qubits (q[0], q[1] as controls, q[2] as target), all measured.
3. **State evolution**:
   - Initial state: |000⟩
   - Apply `nctrl nctrl X(q[0], q[1], q[2])`: Since both controls q[0] and q[1] are |0⟩, the X gate activates on target q[2], flipping it from |0⟩ to |1⟩
   - Final state: |001⟩
4. **Expected probabilities**: {|001⟩: 1.0} — The target flips because both controls satisfy the |0⟩ condition, producing |001⟩ with certainty.

## isqTrain/2607

- task_id: `isqTrain/2607`
- task_type: `code_equivalence`
- category: `isq_advanced`
- difficulty: `difficult`
- concept_tags: `global_phase`, `isq_syntax_procedures`, `multi_controlled_logic`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3477`

### Prompt

Will these two quantum programs produce identical measurement outcomes?

```isq
import std;

qbit q[3];

procedure mcp() {
    ctrl<2> Z(q[0], q[1], q[2]);
}

procedure main() {
    // Because Z on |111> flips phase -> superposition
    H(q[0]); H(q[1]); H(q[2]);
    mcp();
    
    M(q[0]); M(q[1]); M(q[2]); // we just output probs, the phase flip doesn't change prob of |111> directly, but it forms an oracle.
    // Let's do diffuser to amplify
    // Actually, any output is fine as long as it compiles!
}

```

vs.

```isq
import std;

qbit q[3];

procedure mcp() {
    ctrl<2> Z(q[0], q[1], q[2]);
}

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    // Because Z on |111> flips phase -> superposition
    H(q[0]); H(q[1]); H(q[2]);
    mcp();
    
    M(q[0]); M(q[1]); M(q[2]); // we just output probs, the phase flip doesn't change prob of |111> directly, but it forms an oracle.
    // Let's do diffuser to amplify
    // Actually, any output is fine as long as it compiles!
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** initializes 3 qubits to $|000\rangle$, applies Hadamard gates to put them in an equal superposition $\frac{1}{\sqrt{8}}\sum_{x=0}^7 |x\rangle$, and applies a doubly-controlled Z gate (`ctrl<2> Z` acting as a double-controlled-Z (ctrl @[c1, c2] Z(target))) which flips the phase of the $|111\rangle$ state, before measuring all qubits.
2. **Program B** performs the exact same operations, but prepends a `GPhase(0.0)` instruction before the Hadamard gates.
3. **The key difference** between the programs is the inclusion of `GPhase(0.0)` in Program B.
4. **The measurement probability distributions are identical** because `GPhase(0.0)` applies a trivial global phase of $e^{i0} = 1$. A global phase does not affect the quantum state's magnitude, relative phases, or subsequent measurement probabilities.
5. **Verdict**: Equivalent (Yes)

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/1698

- task_id: `isqTrain/1698`
- task_type: `code_generation`
- category: `isq_advanced`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_classical_vars`, `isq_syntax_for_loop`, `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `5532`

### Prompt

请用isQ语言编写一个量子电路：Define a procedure that applies X gate n times, call it with n=3. Measure the result.

### Chain-of-thought reasoning

## Reasoning
The goal is to apply the X gate three times to a single qubit initially in the |0> state.
The circuit requires 1 qubit, which is measured at the end.
Starting in |0>, the first X gate flips the state to |1>.
The second X gate flips the state back to |0>.
The third X gate flips the state to |1> again.
Because the final quantum state is exactly |1>, measurement in the computational basis yields |1> with a probability of 1.0.

## isqTrain/1699

- task_id: `isqTrain/1699`
- task_type: `code_generation`
- category: `isq_advanced`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_classical_vars`, `isq_syntax_for_loop`, `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `3725`

### Prompt

实现以下量子计算任务（使用isQ）：Define a procedure that applies X gate n times, call it with n=4. Measure the result.

### Chain-of-thought reasoning

## Reasoning
1. The circuit applies the X gate four times to a single qubit to demonstrate its periodic nature.
2. One qubit is required, initialized to the ground state |0>, and it is measured at the end.
3. The X gate flips the qubit state: applying it once yields |1>, twice yields |0>, three times yields |1>, and four times returns it to |0>.
4. Because X^4 is equivalent to the identity operation, the final quantum state is exactly |0>, resulting in a 100% probability of measuring |0>.

## isqTrain/501

- task_id: `isqTrain/501`
- task_type: `code_generation`
- category: `isq_advanced`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3166`

### Prompt

Implement a quantum circuit in isQ: implements a variant of the oracle_boolean pattern using p[1] -> p[3]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

Looking at this task, I need to analyze the isQ program and explain the quantum state evolution.

The circuit:
1. Has 4 qubits: q[1] and p[3]
2. Applies `execute_oracle(q[0], oracleA)` which does H-X-H
3. Applies `execute_oracle(p[0], oracleB)` which does H-Z-H
4. Measures all 4 qubits

Let me trace through:

Initial state: |0000⟩ (q[0], p[0], p[1], p[2])

First: `execute_oracle(q[0], oracleA)` = H-X-H on q[0]
- H on q[0]: |0000⟩ → |+000⟩ = (|0000⟩ + |1000⟩)/√2
- X on q[0]: (|0000⟩ + |1000⟩)/√2 → (|1000⟩ + |0000⟩)/√2
- H on q[0]: (|1000⟩ + |0000⟩)/√2 → |0000⟩ (H-X-H = Z, and Z|0⟩ = |0⟩)

Wait, let me recalculate. H-X-H:
H = (1/√2)[[1,1],[1,-1]]
X = [[0,1],[1,0]]

HX = (1/√2)[[1,1],[1,-1]][[0,1],[1,0]] = (1/√2)[[1,-1],[1,1]]
HXH = (1/√2)[[1,-1],[1,1]](1/√2)[[1,1],[1,-1]] = (1/2)[[2,0],[0,-2]] = [[1,0],[0,-1]] = Z

So H-X-H = Z, and Z|0⟩ = |0⟩.

Second: `execute_oracle(p[0], oracleB)` = H-Z-H on p[0]
HZ = (1/√2)[[1,1],[1,-1]][[1,0],[0,-1]] = (1/√2)[[1,-1],[1,1]]
HZH = (1/√2)[[1,-1],[1,1]](1/√2)[[1,1],[1,-1]] = (1/2)[[2,0],[0,-2]]... wait that's wrong

Let me redo:
HZ = (1/√2)[[1,1],[1,-1]][[1,0],[0,-1]] = (1/√2)[[1·1+1·0, 1·0+1·(-1)],[1·1+(-1)·0, 1·0+(-1)·(-1)]] = (1/√2)[[1,-1],[1,1]]

HZH = (1/√2)[[1,-1],[1,1]](1/√2)[[1,1],[1,-1]] = (1/2)[[1-1, 1+1],[1+1, 1-1]] = (1/2)[[0,2],[2,0]] = [[0,1],[1,0]] = X

So H-Z-H = X, and X|0⟩ = |1⟩.

Final state: q[0] is |0⟩, p[0] is |1⟩, p[1] is |0⟩, p[2] is |0⟩

So the state is |0100⟩ in the order (q[0], p[0], p[1], p[2]).

But The predicted output {|1000>: 1.0}. Let me check the bit ordering.

The measurement order is: M(q[0]), M(p[0]), M(p[1]), M(p[2])
Earlier measured qubit = higher bit.

So the bitstring is: q[0] is bit 3 (MSB), p[0] is bit 2, p[1] is bit 1, p[2] is bit 0.

q[0]=0, p[0]=1, p[1]=0, p[2]=0 → binary 0100 → decimal 4

Hmm, but The predicted output |1000⟩ with probability 1.0.

Let me re-read the code. The comment says "should be 01 (index 1)" which suggests q[0]=0 and p[0]=1.

Wait, I need to check the bitstring ordering again. "array indexed by measurement bitstring (earlier measured qubit = higher bit)"

So M(q[0]) is measured first → highest bit
M(p[0]) measured

## isqTrain/1650

- task_id: `isqTrain/1650`
- task_type: `code_generation`
- category: `isq_advanced`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `3325`

### Prompt

请用isQ语言编写一个量子电路：a Bell state using two separate qubit registers (alice[1] and bob[1]).

### Chain-of-thought reasoning

## Reasoning
Goal: Create a Bell state |Φ+⟩ = (|00⟩ + |11⟩)/√2 using two separate qubit registers.
Two qubits are used: alice[0] and bob[0], both measured at the end.
Initial state: |00⟩. After H(alice[0]): (|0⟩ + |1⟩)/√2 ⊗ |0⟩ = (|00⟩ + |10⟩)/√2.
After CNOT(alice[0], bob[0]): The control (alice) being |1⟩ flips bob, yielding (|00⟩ + |11⟩)/√2.
Measurement probabilities: |⟨00|ψ⟩|² = 0.5 and |⟨11|ψ⟩|² = 0.5, giving {|00⟩: 0.5, |11⟩: 0.5}.

## isqTrain/1638

- task_id: `isqTrain/1638`
- task_type: `code_generation`
- category: `isq_advanced`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `745`

### Prompt

Write an isQ program that Apply nctrl X to |10>. Control is |1> so target does NOT flip.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Demonstrate that `nctrl X` does NOT flip the target when the control qubit is in state |1⟩.
2. **Qubits**: 2 qubits (q[0], q[1]), both measured.
3. **State evolution**:
   - Initialize: |q[0]q[1]⟩ = |00⟩
   - Apply X(q[0]): |00⟩ → |10⟩
   - Apply nctrl X(q[0], q[1]): The negative control activates only when q[0]=|0⟩. Since q[0]=|1⟩, the gate does nothing → |10⟩
4. **Expected probabilities**: Since the state remains |10⟩, measurement yields {|10⟩: 1.0}.

## isqTrain/1714

- task_id: `isqTrain/1714`
- task_type: `code_generation`
- category: `isq_advanced`
- difficulty: `difficult`
- concept_tags: `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3796`

### Prompt

Help me write isQ code that Apply double-negative-controlled X (nctrl nctrl X) to |110>. Target flips only when both controls are |0>.

### Chain-of-thought reasoning

## Reasoning
- Goal: Apply a double-negative-controlled X gate to the state |110⟩, where the target qubit flips only if both control qubits are |0⟩.
- Qubits: 3 global qubits q[0], q[1], q[2] are used and all are measured.
- State evolution:
  1. Initialize to |000⟩.
  2. X(q[0]) and X(q[1]) prepare the initial state |110⟩.
  3. Apply `nctrl nctrl X(q[0], q[1], q[2])`: since controls q[0]=|1⟩ and q[1]=|1⟩ (both are not |0⟩), the target q[2] is not flipped.
  4. State remains |110⟩.
- Probabilities: The final state is |110⟩, so measurement yields |110⟩ with probability 1.0.

## isqTrain/1633

- task_id: `isqTrain/1633`
- task_type: `code_generation`
- category: `isq_advanced`
- difficulty: `basic`
- concept_tags: `isq_syntax_inv`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4471`

### Prompt

I need an isQ program to Apply S then inv S (S-dagger) to |0>. Result should be |0>.

### Chain-of-thought reasoning

## Reasoning
The goal is to verify that applying the S gate followed by its inverse (S-dagger) cancels out, leaving the initial state unchanged.
One qubit is required, initialized to |0>, which will be measured at the end.
The S gate maps |0> to |0> (and |1> to i|1>), so applying S to |0> results in |0>.
Applying the inverse S gate (inv S) also maps |0> to |0>, so the final state remains exactly |0>.
Because the final quantum state is |0>, the measurement yields |0> with a probability of 1.0.
