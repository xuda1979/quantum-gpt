# ISQ training COT RAG corpus: gate_decomposition shard 6

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3132

- task_id: `isqTrain/3132`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `4363`

### Prompt

Implement the following in isQ: an isQ program: apply Toffoli (ctrl ctrl X) on initial state |000> where q[0]=0, q[1]=0, q[2]=0 (target).

### Chain-of-thought reasoning

## Reasoning
The goal is to apply a Toffoli (double-controlled X) gate to a 3-qubit system initialized in the |000> state.
Three qubits are required, representing the two controls (q[0], q[1]) and one target (q[2]), and all three are measured.
The system begins in the |000> state, where both control qubits are |0>.
The Toffoli gate flips the target qubit only when both control qubits are in the |1> state.
Since neither control qubit is |1>, the gate acts as the identity, leaving the quantum state unchanged as |000>.
Therefore, a measurement of all three qubits yields the state |000> with a probability of 1.0.

## isqTrain/1792

- task_id: `isqTrain/1792`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `basis_change`
- source: `isq_train_cot`
- dataset_index: `3278`

### Prompt

Write isQ code for the following quantum task: Apply H, then Y, then H to |0>. Measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Apply the sequence H-Y-H to the initial state |0> and measure the resulting state.
2. **Qubits:** 1 qubit is required, and it is measured at the end.
3. **State evolution:** 
   - Start with |0⟩.
   - Apply H: state becomes |+⟩ = (1/√2)(|0⟩ + |1⟩).
   - Apply Y: state becomes (1/√2)(i|1⟩ - i|0⟩) = -i(1/√2)(|0⟩ - |1⟩) = -i|-⟩.
   - Apply H: state becomes -i|1⟩.
4. **Probabilities:** The final state is exactly -i|1⟩. The global phase (-i) does not affect measurement, so the probability of measuring |1⟩ is 1.0.

## isqTrain/1703

- task_id: `isqTrain/1703`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3213`

### Prompt

用isQ实现Verify the gate identity TT = S by applying the gate sequence to a qubit and measuring.

### Chain-of-thought reasoning

## Reasoning
Goal: Verify the identity TT = S by applying two T gates to a qubit and measuring.
One qubit (q[0]) is used and measured.
State evolution: |0⟩ → T|0⟩ = |0⟩ (T only phases |1⟩) → T|0⟩ = |0⟩.
Since TT = diag(1, e^(iπ/2)) = S, and the qubit stays in |0⟩ throughout, measurement yields |0⟩ with probability 1.0.

## isqTrain/1704

- task_id: `isqTrain/1704`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5018`

### Prompt

请用isQ语言编写一个量子电路：Verify the gate identity TTTT = Z by applying the gate sequence to a qubit and measuring.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Verify the gate identity T⁴ = Z by applying the gate sequence to a single qubit.
2. Qubits: Uses 1 qubit, which is measured at the end.
3. State evolution: The initial state is |0>. Since T⁴ = Z, applying four T gates transforms the state as T⁴|0> = Z|0> = |0>.
4. Expected probabilities: The final quantum state is exactly |0>, so the measurement outcome is deterministic with P(|0>) = 1.0.

## isqTrain/3274

- task_id: `isqTrain/3274`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `251`

### Prompt

Code this in isQ: an isQ program: prepare |11> and apply SWAP using 3 CNOT gates. Verify the qubits are swapped.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Code generation for isQ (prepare |11>, swap (three-CNOT decomposition) using 3 CNOTs, verify).
    *   Output required: "Reasoning" section ONLY. No isQ code block. 3-8 lines for simple, up to 15 for complex.
    *   Specific constraints: Start with "## Reasoning". Trace state evolution with Dirac notation. Expected probabilities.

2.  **Analyze the Circuit & State Evolution:**
    *   Goal: Prepare |11> and apply a swap operation (three-CNOT decomposition) decomposed into 3 CNOT gates, then measure.
    *   Qubits: 2 (`q[0]`, `q[1]`), both measured.
    *   Initial state: |00>
    *   Apply `X(q[0])` and `X(q[1])`: state becomes |11>.
    *   Apply `CNOT(q[0], q[1])`: control=q[0], target=q[1]. |11> -> q[0] is 1, so flip q[1] (1->0). State becomes |10>.
    *   Apply `CNOT(q[1], q[0])`: control=q[1], target=q[0]. |10> -> q[1] is 0, so don't flip q[0]. State remains |10>. Wait, standard swap (three-CNOT decomposition) is CNOT(0,1), CNOT(1,0), CNOT(0,1)? Let's check.
        *   Start with |10>: CNOT(0,1) -> |11>; CNOT(1,0) -> |01>; CNOT(0,1) -> |01>. Correct.
        *   Start with |11>: CNOT(0,1) -> |10>; CNOT(1,0) -> |01>; CNOT(0,1) -> |01>.
        *   Wait, The implementation in the prompt has `M(q[0]); M(q[1]);`.
        *   Let's trace The implementation exactly:
            1. `X(q[0])`, `X(q[1])` -> |11>
            2. `CNOT(q[0], q[1])` -> |10>
            3. `CNOT(q[1], q[0])` -> |01> (Wait, |10> means q[0]=1, q[1]=0. `CNOT(q[1], q[0])` flips q[0] because q[1]=0? No, CNOT(control, target) flips target if control is 1. Control is q[1]=0, so target q[0] is NOT flipped. State remains |10>).
            Wait! Let me re-read standard swap (three-CNOT decomposition).
            swap(A, B) via three CNOTs = CNOT(A, B); CNOT(B, A); CNOT(A, B).
            If state is |11>:
            1. CNOT(0, 1) -> |10>
            2. CNOT(1, 0) -> |10> (Control q[1] is 0, so no flip on q[0])
            3. CNOT(0, 1) -> |11> (Control q[0] is 1, so flip q[1] from 0 to 1)
            Result is |11>.
            Let me check the prompt's expected measurement probabilities: `Expected measurement probabilities: {|11>: 1.0}`.
            Yes! The final state is indeed |11> because swap (three-CNOT decomposition)(|11>) = |11>.
    *   Let me re-verify the state steps carefully.
        *   Start: |00>
        *   X(q[0]), X(q[1]): |11>
        *   CNOT(q[0], q[1]): target q[1] flips. |11> -> |10>
        *   CNOT(q[1], q[0]): target q[0] flips if q[1]==1. q[1] is 0, so no flip. |10>
        *   CNOT(q[0], q[1]): target q[1] flips if q[0]==1. q[0] is 1, so q[1] flips (0->1). |10> -> |11>
        *   Final state: |11>
    *   Measurement: `M(q[0])` and `M(q[1])`. State is |11>. Probability of 11 is 1.0.

3.  **Draft the Reasoning Section:**
    *   Goal: Prepare |11>, swap qubits using CNOT decomposition, and verify the output remains |11>.
    *   Qubits: 2 qubits

## isqTrain/3354

- task_id: `isqTrain/3354`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `1281`

### Prompt

Write an isQ program that an isQ program: prepare |10>, apply H1-CNOT, measure both qubits.

### Chain-of-thought reasoning

The user wants to prepare the state |10>, apply H on qubit 1, then CNOT, and measure both qubits.

Let me trace through the circuit:

1. Start with |00>
2. Apply X to q[0]: |10>
3. Apply H to q[1] (which is q[0] in the initial state... wait, let me re-read)

Wait, the prompt says "prepare |10>, apply H1-CNOT". Let me interpret this:
- "H1-CNOT" means apply H to qubit 1, then CNOT
- "prepare |10>" means q[0]=1, q[1]=0

So the initial state is |10> (q[0]=|1>, q[1]=|0>).

But In the implementation:
- X(q[0]) makes q[0] = |1>
- H(q[1]) is applied... wait, but q[1] is in |0>

Hmm, let me re-read The implementation:

Wait, that's odd. If we want to prepare |10>, we only need X(q[0]). But then H(q[1]) is applied to q[1] which is in |0>, making it |+>.

But then CNOT(q[0], q[1]) with q[0] as control:
- |10> → |10>
- |11> → |11>

Wait, let me reconsider. The state after X(q[0]) is |10>. Then H(q[1]) applies H to q[1]:
|10> → |1⟩⊗H|0⟩ = |1⟩⊗|+⟩ = |1⟩⊗(1/√2)(|0⟩+|1⟩) = (1/√2)(|10⟩+|11⟩)

Then CNOT(q[0], q[1]):
- CNOT with q[0] as control, q[1] as target
- |10⟩ → |11⟩ (target flips because control is |1⟩)
- |11⟩ → |10⟩ (target flips because control is |1⟩)

So (1/√2)(|10⟩+|11⟩) → (1/√2)(|11⟩+|10⟩) = (1/√2)(|10⟩+|11⟩)

That's the same state! So the final state is (1/√2)(|10⟩+|11⟩), which gives probabilities {|10⟩: 0.5, |11⟩: 0.5}.

This makes sense with the predicted output.

Let me write the reasoning:

1. Goal: Prepare |10⟩, apply H to qubit 1 then CNOT, and measure both qubits.
2. Need 2 qubits, both measured.
3. State evolution:
   - Start: |00⟩
   - After X(q[0]): |10⟩
   - After H(q[1]): |1⟩⊗|+⟩ = (1/√2)(|10⟩+|11⟩)
   - After CNOT(q[0], q[1]): CNOT flips target when control=|1⟩, so |10⟩→|11⟩ and |11⟩→|10⟩, giving (1/√2)(|11⟩+|10⟩) = (1/√2)(|10⟩+|11⟩)
4. Final state (1/√2)(|10⟩+|11⟩) yields P(|10⟩) = 0.5, P(|11⟩) = 0.5.

Wait, I need to double-check the H(q[1]) part. The reference applies H to q[1], not q[0]. But the prompt says "H1-CNOT". This could mean "H on qubit 1, then CNOT" which is what the reference does.

Actually, re-reading the reference: it applies H(q[1]) which is the second qubit. That's qubit index 1. So "H1" means H on qubit 1 (q[1]).

Hmm wait, let me reconsider. The circuit should:

But to prepare |10>, we need q[0]=1 and q[1]=0. X(q[0]) sets q[0]=1. Then H(q[1]) is applied to q[1] which is still |0>, turning it into |+>.

But actually, I wonder if "H1-CNOT" means the H is applied to q[0] (qubit 1 in 1-indexed notation). Let me check: in the reference, H(q[1])

## isqTrain/2

- task_id: `isqTrain/2`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `3234`

### Prompt

Help me write isQ code that implements the gate_decomposition pattern but with a different initial state preparation (flip q[[1]] -> q[0]).

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a swap gate decomposition with X(q[0]) initialization to prepare |01>.
2. **Qubits**: 2 qubits (q[0], q[1]), both measured.
3. **State evolution**:
   - |00> → X(q[0]) → |10>
   - CNOT(q[0], q[1]) → |11>
   - CNOT(q[1], q[0]) → |01>
   - CNOT(q[0], q[1]) → |01> (swap complete)
4. **Result**: Final state |01⟩ yields measurement probability P(|01⟩) = 1.0.

## isqTrain/1841

- task_id: `isqTrain/1841`
- task_type: `output_prediction`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `global_phase`, `isq_syntax_arrays`, `isq_syntax_deriving_gate`, `isq_syntax_procedures`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1521`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
qbit q[2];
procedure cy_gate(qbit c, qbit t) {
    inv S(t);
    CNOT(c, t);
    S(t);
}
procedure main() {
    X(q[0]);
    X(q[1]);
    cy_gate(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations**: The circuit initializes 2 qubits in |00>, applies X to both, and then applies a custom `cy_gate` (which decomposes to `inv S`, `CNOT`, `S`) with `q[0]` as control and `q[1]` as target.
2. **State Evolution**:
   - Initial state: |00>
   - After X gates: |11>
   - `inv S` on target |1> phase: $e^{-i\pi/2}|11\rangle = -i|11\rangle$
   - `CNOT` flips the target qubit: $-i|10\rangle$
   - `S` acts on target |0>, leaving it unchanged: $-i|10\rangle$
3. **Final state**: $-i|10\rangle$ (equivalent to |10> up to a global phase).
4. **Probabilities**: Measuring the state yields exactly |10>.

Predicted probability distribution: {'10': 1.0}

### Reference answer

{'predicted_probs': {'10': 1.0}, 'explanation': 'CY|11⟩ = i|10⟩. Global phase unobservable, P(|10⟩) = 1.0 at index 2.'}

## isqTrain/3397

- task_id: `isqTrain/3397`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `5792`

### Prompt

用isQ实现an isQ program: H, Rz(1*pi/3), H on a qubit. This is equivalent to Rx(1*pi/3).

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply H, Rz(π/3), H to a single qubit, equivalent to Rx(π/3).
2. **Qubits**: 1 qubit (q[0]), measured at the end.
3. **State evolution**:
   - |0⟩ → H → |+⟩ = (|0⟩ + |1⟩)/√2
   - → Rz(π/3) → (e^{-iπ/6}|0⟩ + e^{iπ/6}|1⟩)/√2
   - → H → cos(π/6)|0⟩ - i·sin(π/6)|1⟩ = (√3/2)|0⟩ - i(1/2)|1⟩
4. **Probabilities**: |⟨0|ψ⟩|² = 3/4 = 0.75, |⟨1|ψ⟩|² = 1/4 = 0.25, consistent with Rx(π/3).

## isqTrain/3270

- task_id: `isqTrain/3270`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `reversible_computing`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1522`

### Prompt

I need an isQ program to an isQ program: apply CZ twice on |01>. Since CZ*CZ=I, the state returns to |01>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply two CZ gates to the state |01> to demonstrate that CZ squared is the identity.
2. **Qubits**: 2 qubits, `q[0]` and `q[1]`, both of which are measured at the end.
3. **State Evolution**:
   - Initialize to |00>.
   - Apply X to `q[1]`, flipping it to create the state |01>.
   - Apply CZ(q[0], q[1]): Since the control `q[0]` is |0>, the target is unaltered, leaving the state as |01>.
   - Apply CZ(q[0], q[1]) again: The state remains |01> (verifying CZ*CZ=I).
4. **Probabilities**: The final state is deterministically |01>, yielding a 100% probability of measuring the bitstring "01" (where `q[0]`=0, `q[1]`=1).
