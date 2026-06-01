# ISQ training COT RAG corpus: isq_language shard 3

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/isqd/49

- task_id: `isqExpand/isqd/49`
- task_type: `output_prediction`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_procedures`, `entanglement`, `basis_change`, `isq_syntax_arrays`
- source: `isq_expansion`
- dataset_index: `700`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
qbit q[2];

procedure rotate_and_entangle(qbit reg[2], double theta) {
    Ry(theta, reg[0]);
    CNOT(reg[0], reg[1]);
}

procedure main() {
    rotate_and_entangle(q, 1.5707963);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. rotate_and_entangle(q, pi/2) called.
2. Ry(pi/2, q[0]): |0> -> (|0>+|1>)/sqrt(2)
   State: ((|0>+|1>)/sqrt(2)) x |0> = (|00>+|10>)/sqrt(2)
3. CNOT(q[0], q[1]):
   |00> -> |00>, |10> -> |11>
   State: (|00>+|11>)/sqrt(2)
4. Measurement: P(|00>)=0.5, P(|11>)=0.5.
   Index 0: P=0.5, Index 3: P=0.5.

### Reference answer

{'predicted_probs': {'00': 0.5, '01': 0.0, '10': 0.0, '11': 0.5}, 'explanation': 'Step-by-step:\n1. Ry(pi/2, q[0]): |0> -> cos(pi/4)|0> + sin(pi/4)|1> = (|0>+|1>)/sqrt(2)\n2. CNOT(q[0], q[1]): |0>|0> -> |00>, |1>|0> -> |11>\n   Combined: (|00>+|11>)/sqrt(2) -- a Bell state\n3. P(|00>) = 0.5 at index 0, P(|11>) = 0.5 at index 3.\nDistribution: [0.5, 0.0, 0.0, 0.5].'}

## isqExpand/isqd/162

- task_id: `isqExpand/isqd/162`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `h_gate`, `for_loop`, `superposition`, `measurement`, `uniform_distribution`
- source: `isq_expansion`
- dataset_index: `5015`

### Prompt

Implement the following in isQ: applies H to all 3 qubits using a for loop, then measures all.

### Chain-of-thought reasoning

We have 3 qubits initialized to |000⟩. Applying H to each qubit creates an equal superposition over all 8 computational basis states. H|0⟩ = (|0⟩+|1⟩)/√2, so H⊗H⊗H|000⟩ = (1/√8)(|000⟩+|001⟩+|010⟩+|011⟩+|100⟩+|101⟩+|110⟩+|111⟩). Each of the 8 basis states has equal probability |1/√8|² = 1/8 = 0.125. The for loop iterates from 0 to 3 exclusive (i.e., 0,1,2), applying H to q[0], q[1], q[2].

## isqExpand/isqd/166

- task_id: `isqExpand/isqd/166`
- task_type: `output_prediction`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `hadamard_gate`, `self_inverse_property`, `identity`, `measurement_probabilities`
- source: `isq_expansion`
- dataset_index: `1109`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    H(q[0]);
    H(q[0]);
    H(q[0]);
    H(q[0]);
    H(q[0]);
}
```

### Chain-of-thought reasoning

Step 1: Identify the initial state. In isQ, qubits are initialized to |0⟩. So q[0] starts in state |0⟩.

Step 2: Understand the Hadamard gate property. The Hadamard gate H is self-inverse, meaning H² = I (the identity matrix). This can be verified: H = (1/√2)[[1,1],[1,-1]], and H×H = [[1,0],[0,1]] = I.

Step 3: Count the number of H gates applied. There are 6 consecutive H(q[0]) operations.

Step 4: Simplify using the self-inverse property. H^6 = (H²)³ = I³ = I. An even number of Hadamard gates always results in the identity operation.

Step 5: Determine the final state. Since the net operation is identity and the initial state is |0⟩, the final state is |0⟩.

Step 6: Calculate measurement probabilities. The probability of measuring |0⟩ is |⟨0|0⟩|² = 1.0, and the probability of measuring |1⟩ is |⟨1|0⟩|² = 0.0.

Conclusion: The probability distribution is P('0') = 1.0, P('1') = 0.0.

### Reference answer

{'predicted_probs': {'0': 1.0, '1': 0.0}, 'explanation': "The Hadamard gate H is its own inverse: H×H = I (identity). Applying H six times is equivalent to (H×H)×(H×H)×(H×H) = I×I×I = I. Since the qubit starts in |0⟩ and the net effect is the identity, the state remains |0⟩, yielding probability 1.0 for outcome '0' and 0.0 for outcome '1'."}

## isqExpand/isqd/177

- task_id: `isqExpand/isqd/177`
- task_type: `output_prediction`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `negative_control`, `nctrl`, `X_gate`, `state_prediction`, `two_qubit`
- source: `isq_expansion`
- dataset_index: `1`

### Prompt

Predict the output probabilities when nctrl @[q[0]] X(q[1]) is applied to the initial state |00>. Since q[0] is |0>, the negatively-controlled X gate fires on q[1].

### Chain-of-thought reasoning

1. Initial state: |00>, meaning q[0]=|0> and q[1]=|0>. 2. nctrl @[q[0]] X(q[1]) is a negatively-controlled X gate: it applies X to q[1] when q[0] is |0>. 3. Since q[0] is in state |0>, the negative control condition is satisfied. 4. X gate is applied to q[1], flipping |0> to |1>. 5. Final state is |01> with probability 1.0.

### Reference answer

{'predicted_probs': {'00': 0.0, '01': 1.0, '10': 0.0, '11': 0.0}, 'explanation': 'The initial state is |00>. The nctrl (negative control) gate fires when the control qubit q[0] is |0>. Since q[0] is |0>, the X gate is applied to q[1], flipping it from |0> to |1>. The final state is |01> with probability 1.0.'}

## isqExpand/isqd/59

- task_id: `isqExpand/isqd/59`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `wrong_gate`, `s_gate`, `t_gate`, `phase_gate`, `ctrl_modifier`
- source: `isq_expansion`
- dataset_index: `3402`

### Prompt

This isQ program compiles but produces incorrect probabilities. Find and correct the mistake.

```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    H(q[1]);
    ctrl S(q[0], q[1]);  // Bug: should be T, not S
    H(q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Bug Analysis
S gate adds phase pi/2, T gate adds phase pi/4. The programmer used S instead of T.

Correct circuit trace:
1. X(q[0]): q[0]=|1>
2. H(q[1]): q[1]=(|0>+|1>)/sqrt(2)
3. ctrl @[q[0]] T(q[1]): q[0]=|1>, so T acts on q[1]:
   (|0>+e^{i*pi/4}|1>)/sqrt(2)
4. H(q[1]):
   H(|0>) = (|0>+|1>)/sqrt(2)
   H(e^{i*pi/4}|1>) = e^{i*pi/4}(|0>-|1>)/sqrt(2)
   Combined: ((1+e^{i*pi/4})|0> + (1-e^{i*pi/4})|1>)/2
   P(q[1]=0) = |1+e^{i*pi/4}|^2/4 = (2+sqrt(2))/4 = cos^2(pi/8) ~ 0.8536
   P(q[1]=1) = |1-e^{i*pi/4}|^2/4 = (2-sqrt(2))/4 = sin^2(pi/8) ~ 0.1464

Fix: Replace S with T in the ctrl line.

## isqExpand/isqd/14

- task_id: `isqExpand/isqd/14`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `for_loop`, `hadamard`, `uniform_superposition`
- source: `isq_expansion`
- dataset_index: `3644`

### Prompt

Create an isQ quantum circuit that uses a for loop to apply Hadamard gates to all 3 qubits, then measures all of them.

Requirements:
- Declare a global qbit q[3].
- In main(), use `for i in 0:3 { H(q[i]); }` to put all qubits in superposition.
- Measure all qubits using a second for loop: `for i in 0:3 { M(q[i]); }`

Since all 3 qubits are in equal superposition, each of the 8 basis states should have probability 1/8 = 0.125.

### Chain-of-thought reasoning

## Reasoning
Goal: Use a for loop to apply H to 3 qubits.

1. for i in 0:3 applies H(q[0]), H(q[1]), H(q[2])
2. Each qubit goes to (|0>+|1>)/sqrt(2)
3. Combined state: tensor product of 3 |+> states
4. Each of 2^3=8 basis states has amplitude 1/sqrt(8)
5. Probability = 1/8 = 0.125 for each state

## isqExpand/isqd/101

- task_id: `isqExpand/isqd/101`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `for_loop`, `half_open_range`, `off_by_one`, `range_error`
- source: `isq_expansion`
- dataset_index: `4446`

### Prompt

Debug this isQ program — it gives unexpected measurement results.

```isq
import std;
qbit q[3];

procedure main() {
    for i in 0:4 {
        H(q[i]);
    }
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Bug Analysis
Buggy: for i in 0:4 accesses q[3] out of bounds (q has 3 elements).
Fix: for i in 0:3 (half-open [0,3) = {0,1,2}).
After fix: H on 3 qubits -> uniform over 8 states, P=1/8 each.

## isqExpand/isqd/142

- task_id: `isqExpand/isqd/142`
- task_type: `output_prediction`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `increment_circuit`, `CNOT`, `X_gate`, `binary_arithmetic`, `measurement`
- source: `isq_expansion`
- dataset_index: `1067`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[2];

procedure main() {
    // Initialize to |10>
    X(q[1]);

    // 2-qubit increment circuit: increment by 1
    // If LSB (q[0]) is 1, carry to q[1]
    CNOT(q[0], q[1]);
    // Always flip LSB
    X(q[0]);

    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

Step 1: Initial state is |00⟩. After X(q[1]), the state becomes |10⟩ (q[1]=1, q[0]=0).

Step 2: Apply CNOT(q[0], q[1]). Since q[0]=0 (control is 0), the target q[1] is unchanged. State remains |10⟩.

Step 3: Apply X(q[0]). This flips q[0] from 0 to 1. State becomes |11⟩.

Step 4: Measurement probabilities are deterministic: P(|00⟩)=0, P(|01⟩)=0, P(|10⟩)=0, P(|11⟩)=1.

Verification: Incrementing binary 10 (=2) by 1 gives binary 11 (=3). Correct.

### Reference answer

{'predicted_probs': {'00': 0.0, '01': 0.0, '10': 0.0, '11': 1.0}, 'explanation': 'The circuit initializes |10⟩ (binary 2). The CNOT(q[0], q[1]) does nothing because q[0]=0. Then X(q[0]) flips q[0] from 0 to 1. The final state is |11⟩ (binary 3), which is 10 + 1 = 3. This is the correct increment result.'}

## isqExpand/isqd/150

- task_id: `isqExpand/isqd/150`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `boolean_oracle`, `ancilla_management`, `uncomputation`, `phase_kickback`, `toffoli_gate`
- source: `isq_expansion`
- dataset_index: `3953`

### Prompt

The following isQ program implements a Boolean oracle that marks the |11⟩ state of two data qubits using an ancilla qubit q[2]. The oracle should apply a phase flip to |11⟩ while leaving the ancilla in state |0⟩. However, there is a bug: the ancilla is computed but never uncomputed, leaving it entangled with the main register. Fix the code so that the ancilla is properly restored to |0⟩ after the phase flip. Verify by measuring all 3 qubits — the ancilla should always read 0.

### Chain-of-thought reasoning

Step 1: Analyze the buggy code. H(q[0]) and H(q[1]) create an equal superposition (|00>+|01>+|10>+|11>)/2 on the data qubits, with q[2]=|0>. Step 2: Toffoli(q[0],q[1],q[2]) computes the AND into the ancilla: the state becomes (|00>|0>+|01>|0>+|10>|0>+|11>|1>)/2. Step 3: Z(q[2]) flips the phase of the |1> component of the ancilla: state becomes (|00>|0>+|01>|0>+|10>|0>-|11>|1>)/2. Step 4: The bug is that the ancilla is not uncomputed. The ancilla remains |1> when data is |11>, so measuring all 3 qubits gives P(111)=0.25 and P(110)=0.0. Step 5: The fix adds Toffoli(q[0],q[1],q[2]) after Z(q[2]) to uncompute the ancilla. Since Toffoli is its own inverse, applying it again restores q[2] to |0>. The state becomes (|00>+|01>+|10>-|11>)|0>/2. Step 6: Measuring all 3 qubits in the corrected state gives P(000)=P(010)=P(100)=P(110)=0.25 and P(001)=P(011)=P(101)=P(111)=0.0. The ancilla q[2] is always 0, confirming proper disentanglement.

## isqExpand/isqd/61

- task_id: `isqExpand/isqd/61`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `inv_modifier`, `adjoint`, `s_gate`, `uncomputation`, `best_practice`
- source: `isq_expansion`
- dataset_index: `2730`

### Prompt

用isQ实现demonstrates correct use of the `inv` modifier for uncomputation. The program should:
1. Apply X(q[0]) to set q[0] to |1>
2. Apply S(q[0]) to add a pi/2 phase
3. Apply inv S(q[0]) to undo the phase (S-dagger)
4. Apply X(q[0]) to return to |0>
5. Measure q[0]

The S and inv S should cancel, so the final state is |0> with probability 1.0.

### Chain-of-thought reasoning

## Reasoning
Demonstrate the inv modifier for uncomputation.

S gate: |1> -> i|1> (phase pi/2).
S-dagger (inv S): |1> -> -i|1> (phase -pi/2).
S followed by inv S = Identity on the phase.

Circuit trace:
1. X(q[0]): |0> -> |1>
2. S(q[0]): |1> -> i|1>
3. inv S(q[0]): i|1> -> |1> (phases cancel)
4. X(q[0]): |1> -> |0>
5. P(|0>)=1.0

Key lesson: use `inv Gate(q)` to apply the adjoint (inverse) of a gate. This is essential for uncomputation patterns in quantum algorithms.
