# ISQ training COT RAG corpus: gate_decomposition shard 16

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3358

- task_id: `isqTrain/3358`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `381`

### Prompt

I need an isQ program to an isQ program: prepare |01>, apply CNOT-CNOT-rev, measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Prepare the initial state |01>, apply two CNOT gates with swapped control and target qubits, and measure both qubits.
2. **Qubits:** 2 qubits are used (`q[0]` and `q[1]`), and both are measured at the end.
3. **State Evolution:**
   - Start in |00>.
   - Apply `X(q[1])`: Flips the second qubit, yielding |01>.
   - Apply `CNOT(q[0], q[1])`: The control q0 is |0>, so the target q1 is unchanged. The state remains |01>.
   - Apply `CNOT(q[1], q[0])`: The control q1 is |1>, so the target q0 is flipped. The state becomes |11>.
4. **Probabilities:** The final quantum state is exactly |11>, meaning the measurement will deterministically yield `11` (probability 1.0).

## isqTrain/3372

- task_id: `isqTrain/3372`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `482`

### Prompt

帮我写一个isQ程序：an isQ program: apply H to control q[0], then ctrl Rx(pi/3) from q[0] to q[1], then measure both.

### Chain-of-thought reasoning

## Reasoning

Goal: Prepare superposition on q[0], then conditionally rotate q[1] via controlled-Rx(π/3), and measure both qubits.

Two qubits q[0], q[1] are used and both are measured.

State evolution:
- **Initial**: |00⟩
- **H(q[0])**: (|00⟩ + |10⟩)/√2
- **ctrl Rx(π/3)**: Rx(π/3)|0⟩ = cos(π/6)|0⟩ − i·sin(π/6)|1⟩ = (√3/2)|0⟩ − (i/2)|1⟩, applied to q[1] when q[0]=|1⟩:
  → (|00⟩ + (√3/2)|10⟩ − (i/2)|11⟩)/√2

Measurement probabilities:
- P(|00⟩) = |1/√2|² = **0.5**
- P(|10⟩) = |√3/(2√2)|² = 3/8 = **0.375**
- P(|11⟩) = |1/(2√2)|² = 1/8 = **0.125**

## isqTrain/3401

- task_id: `isqTrain/3401`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `3390`

### Prompt

用isQ实现an isQ program: H, Rz(1*pi/7), H on a qubit. This is equivalent to Rx(1*pi/7).

### Chain-of-thought reasoning

## Reasoning
The goal is to perform an X-axis rotation, Rx(π/7), by conjugating an Rz gate with Hadamard gates.
The circuit requires 1 qubit, which is measured at the end.
Starting in |0>, the first H gate creates the superposition

## isqTrain/3156

- task_id: `isqTrain/3156`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `isq_syntax_inv`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4040`

### Prompt

Implement a quantum circuit in isQ: an isQ program: apply T then inv T (Tdg) to show they cancel. Prepare |+>, apply T, inv T, H, measure. Should get |0>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Demonstrate that T and its inverse (Tdg) cancel, leaving the state unchanged before final measurement.
2. **Qubits**: 1 qubit `q[0]`, which is measured.
3. **State evolution**:
   - Start: |0⟩
   - H(q[0]): |0⟩ → |+⟩ = (|0⟩ + |1⟩)/√2
   - T(q[0]): |+⟩ → (|0⟩ + e^{iπ/4}|1⟩)/√2
   - inv T(q[0]): applies T† = [[1,0],[0,e^{-iπ/4}]], undoing T exactly → |+⟩
   - H(q[0]): |+⟩ → |0⟩
4. **Expected probabilities**: Since the final state is |0⟩, measuring yields |0⟩ with probability 1.0.

## isqTrain/3376

- task_id: `isqTrain/3376`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `3632`

### Prompt

请用isQ语言编写一个量子电路：an isQ program: apply H to control q[0], then ctrl Rx(pi/6) from q[0] to q[1], then measure both.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Apply a Hadamard gate to the control qubit, followed by a controlled-Rx(π/6) gate, then measure both qubits.
2. **Qubits:** 2 qubits are used (`q[0]`, `q[1]`) and both are measured.
3. **State Evolution:**
   - Start in the initial state |00⟩.
   - Apply H to `q[0]`: State becomes (1/√

## isqTrain/1700

- task_id: `isqTrain/1700`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `669`

### Prompt

用isQ实现Verify the gate identity XZX = -Z by applying the gate sequence to a qubit and measuring.

### Chain-of-thought reasoning

## Reasoning
The goal is to verify the gate identity XZX = -Z by applying the sequence to a single qubit.
We need 1 qubit, which is initialized to |0> and measured at the end.
1. Initial state is |0>.
2. Apply X gate: |0> becomes |1>.
3. Apply Z gate: |1> becomes -|1>.
4. Apply X gate: -|1> becomes -|0>.
Measurement probabilities are unaffected by the global phase (-1), resulting in {|0>: 1.0}.

## isqTrain/3349

- task_id: `isqTrain/3349`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `4121`

### Prompt

用isQ实现an isQ program: apply 2-qubit gate chain H1-CZ-H1 to |00> and measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply the gate sequence H-CZ-H to qubit 1 (with q[0] as CZ control) on |00>, then measure both qubits.
2. Two qubits needed, both measured.
3. State evolution: |00> →(H on q[1])→ |0>|+> = (1/√2)(|00>+|01>) →(CZ with q[0]=|0> as control, no phase flip)→ (1/√2)(|00>+|01>) →(H on q[1])→ |00>
4. Since q[0] stays |0> throughout, CZ never applies its -1 phase, so H-H = I on q[1], yielding |00> with probability 1.0.

## isqTrain/3254

- task_id: `isqTrain/3254`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5385`

### Prompt

Create an isQ quantum circuit that an isQ program: apply X twice to each of 1 qubits (X*X=I), then measure. All qubits should remain |0>.

### Chain-of-thought reasoning

## Reasoning
1. The goal is to demonstrate that applying the Pauli-X gate twice to a single qubit acts as an identity operation (X*X = I).
2. The circuit requires 1 qubit initialized to its default state |0>, which is measured at the end.
3. The first X gate flips the initial state from |0> to |1>.
4. The second X gate flips the state back from |1> to |0>.
5. Because the final quantum state is exactly |0>, measurement yields the outcome |0> with a probability of 1.0.

## isqTrain/4

- task_id: `isqTrain/4`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `3203`

### Prompt

I need an isQ program to implements the gate_decomposition pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement a swap-based circuit with an explicit identity X-X pair to demonstrate gate cancellation awareness, yielding deterministic output.

Two qubits q[0], q[1] are used and both are measured.

State evolution:
1. Initial: |00⟩
2. X(q[1]): |01⟩
3. swap_gate(q[0], q[1]) via three CNOTs: |01⟩ → |01⟩ → |11⟩ → |10⟩ (swaps qubit values)
4. X(q[0]): |10⟩ → |00⟩
5. X(q[0]): |00⟩ → |10⟩ (X-X pair = identity, net effect returns to |10⟩)

Final state is |10⟩ with probability 1.0, as the X-X pair cancels exactly and the swap correctly exchanges the initial |1⟩ from q[1] into q[0].

## isqTrain/609

- task_id: `isqTrain/609`
- task_type: `output_prediction`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `4777`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
qbit q[7];

procedure main() {
    X(q[0]);
    SWAP(q[0], q[6]);
    SWAP(q[1], q[5]);
    SWAP(q[2], q[4]);
    M(q);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Role: Quantum computing expert.
    *   Task: Generate a concise, precise step-by-step reasoning for an isQ quantum program.
    *   Format: "## Circuit Analysis" followed by 3-15 lines of reasoning. No code blocks. End with the probability distribution.
    *   Program:
        
    *   Initial state: 7 qubits, all |0>. State: |0000000>.
    *   Number of qubits measured: 7.

2.  **Step-by-Step State Evolution:**
    *   **Initial:** $|0000000\rangle$
    *   **Apply X(q[0]):** Flips q[0] to |1>. State becomes $|1000000\rangle$.
    *   **Apply swap (three-CNOT decomposition)(q[0], q[6]):** Swaps the state of q[0] (which is |1>) and q[6] (which is |0>). State becomes $|0000001\rangle$.
    *   **Apply swap (three-CNOT decomposition)(q[1], q[5]):** Swaps q[1] (|0>) and q[5] (|0>). State remains $|0000001\rangle$.
    *   **Apply swap (three-CNOT decomposition)(q[2], q[4]):** Swaps q[2] (|0>) and q[4] (|0>). State remains $|0000001\rangle$.
    *   **Apply M(q):** Measure all 7 qubits.
    *   Wait, let's look at The implementation. Expected measurement probabilities: {|1000000>: 1.0}.
    *   Let me re-read the array indexing convention in the prompt. "array indexed by measurement bitstring (earlier measured qubit = higher bit)".
    *   Ah! The prompt says `M(q)` measures `q[0]` to `q[6]`. "earlier measured qubit = higher bit". This means `q[0]` is the *highest bit* (leftmost in the bitstring), and `q[6]` is the lowest bit (rightmost).
    *   Let's re-evaluate:
        *   Initial: q[0]=0, q[1]=0, q[2]=0, q[3]=0, q[4]=0, q[5]=0, q[6]=0. Bitstring: 0000000.
        *   `X(q[0])`: q[0]=1. Bitstring: 1000000.
        *   `swap (three-CNOT decomposition)(q[0], q[6])`: q[0] becomes 0, q[6] becomes 1. Bitstring: 0000001.
        *   Wait, why does The implementation say `{|1000000>: 1.0}`?
        *   Let's check standard isQ bit ordering. `M(q)` usually measures in array order `q[0]` down to `q[6]`.
        *   Wait, maybe isQ bitstring indexing is opposite? If earlier measured qubit = higher bit, `q[0]` is the highest bit. So bitstring is `q[0] q[1] q[2] q[3] q[4] q[5] q[6]`.
        *   If `X(q[0])` makes q[0]=1. Then `swap (three-CNOT decomposition)(q[0], q[6])` makes q[0]=0 and q[6]=1. Bitstring should be 0000001.
        *   Why is it 1000000? Is there a difference in `swap (three-CNOT decomposition)`? No.
        *   Wait, look at The implementation again: `Expected measurement probabilities: {|1000000>: 1.0}`. Is this a typo In the implementation or did I misunderstand `swap (three-CNOT decomposition)(q[0], q[6])`?
        *   Let's reread the prompt. Is it possible `swap (three-CNOT decomposition)` does nothing? No.
        *   Wait! Look at The implementation... `Expected measurement probabilities: {|1000000>: 1.0}`. Could The implementation be wrong, or did I misread the bitstring?
        *   Let's think if `swap (three-CNOT decomposition)(q[0], q[6])` actually swaps the bits. Yes.
        *   Wait... if The implementation says {|1000000>: 1.0}, then either The implementation is wrong, OR `M(q)` measures q[6] first

### Reference answer

{'predicted_probs': {'64': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/206. Dimension: predict probabilities for reference circuit.'}
