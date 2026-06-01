# ISQ training COT RAG corpus: gate_decomposition shard 7

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3262

- task_id: `isqTrain/3262`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `reversible_computing`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `3537`

### Prompt

请用isQ语言编写一个量子电路：an isQ program: apply H twice to each of 4 qubits (H*H=I), then measure. All should be |0>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply H gate twice to each of 4 qubits and measure—since H²=I, all qubits return to |0>.
2. **Qubits**: 4 qubits (q[0]–q[3]), all measured.
3. **State evolution**:
   - Start: |0000⟩
   - After first H on each qubit: |++++⟩ (H|0⟩=|+⟩)
   - After second H on each qubit: |0000⟩ (H|+⟩=|0⟩)
4. **Expected result**: Since H²=I restores each qubit to |0⟩, measurement yields |0000⟩ with probability 1.0.

## isqTrain/1685

- task_id: `isqTrain/1685`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3750`

### Prompt

帮我写一个isQ程序：Apply SWAP then CZ on |10>. CZ adds phase to |11> but state is |01>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply swap (three-CNOT decomposition) then CZ to |10⟩, showing CZ has no effect when the state becomes |01⟩.
2. **Qubits**: 2 qubits (q[0], q[1]), both measured.
3. **State evolution**:
   - Initialize: |00⟩
   - X(q[0]): |10⟩
   - swap (three-CNOT decomposition)(q[0], q[1]): |01⟩ (swaps qubit values)
   - CZ(q[0], q[1]): CZ adds phase -1 to |11⟩ only; |01⟩ is unaffected → |01⟩
4. **Expected probabilities**: {|01⟩: 1.0} — CZ only phases |11⟩, so |01⟩ remains unchanged with probability 1.

## isqTrain/1427

- task_id: `isqTrain/1427`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `852`

### Prompt

用isQ实现Apply H, X, H (equivalent to Z) to |1> and measure. Verify the gate identity HXH = Z.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Verify the gate identity HXH = Z by applying the sequence to |1⟩ and checking the output matches Z|1⟩ = -|1⟩.
2. **Qubits**: 1 qubit (q[0]), which is measured.
3. **State evolution**:
   - Initialize |0⟩, apply X → |1⟩
   - Apply H → |−⟩ = (|0⟩ − |1⟩)/√2
   - Apply X → −|−⟩ = (|1⟩ − |0⟩)/√2
   - Apply H → −|1⟩
4. **Result**: Final state is −|1⟩ (equivalent to |1⟩ up to global phase). Since Z|1⟩ = −|1⟩, this confirms HXH = Z. Measurement yields |1⟩ with probability 1.0.

## isqTrain/1980

- task_id: `isqTrain/1980`
- task_type: `output_prediction`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `375`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;
qbit q[2];
procedure main() {
    X(q[1]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[0]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initial State:** The 2-qubit system starts in the ground state |00⟩.
2. **X(q[1]):** Flips the second qubit, changing the state to |01⟩.
3. **CNOT(q[0], q[1]):** Applies a CNOT with q[0] as control and q[1] as target. Since q[0] is |0⟩, the target is unchanged. The state remains |01⟩.
4. **CNOT(q[1], q[0]):** Applies a CNOT with q[1] as control and q[0] as target. Since q[1] is |1⟩, the target q[0] is flipped. The state transitions to |11⟩.
5. **CNOT(q[0], q[1]):** Applies a CNOT with q[0] as control and q[1] as target. Since q[0] is |1⟩, the target q[1] is flipped. The state transitions to |10

### Reference answer

{'predicted_probs': {'10': 1.0}, 'explanation': 'Three-CNOT SWAP maps |01> to |10>, so index 2 has probability 1.0.'}

## isqTrain/3294

- task_id: `isqTrain/3294`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3006`

### Prompt

Code this in isQ: an isQ program: apply H, Rz(3*pi/4), Rz(-3*pi/4), H. Since Rz cancels, net is H*H=I.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Apply a sequence of H, Rz(3*pi/4), Rz(-3*pi/4), and H to a single qubit to demonstrate that consecutive inverse rotations cancel out, leaving the identity.
2. **Qubits:** Requires 1 qubit (`q[0]`), which is measured at the end.
3. **State evolution:**
   - Start in the initial state |0>.
   - Apply H: maps |0> to |+>.
   - Apply Rz(3*pi/4): adds a relative phase, changing |+> to e^(-i3*pi/8)|0> + e^(i3*pi/8)|1>.
   - Apply Rz(-3*pi/4): exactly cancels the previous phase shift, returning the state to |+>.
   - Apply H: maps |+> back to |0>.
4. **Expected probabilities:** Because the sequence simplifies to the Identity (H * Rz * Rz^-1 * H = I), the final state is purely |0>. Thus, the measurement probabilities are {|0>: 1.0}.

## isqTrain/3408

- task_id: `isqTrain/3408`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `4189`

### Prompt

Help me write isQ code that an isQ program: H, Rz(3*pi/7), H on a qubit. This is equivalent to Rx(3*pi/7).

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Apply the sequence H, Rz(3*pi/7), and H to a single qubit, which is mathematically equivalent to an Rx(3*pi/7) rotation.
2. **Qubits:** 1 qubit is required and measured.
3. **Evolution:**
   - Initialize to |0>.
   - Apply H: state becomes |+> = (1/√2)(|0> + |1>).
   - Apply Rz(3*pi/7): state becomes (1/√2)(|0> + e^{-i3π/7}|1>).
   - Apply H: state becomes (1/2)[(1+e^{-i3π/7})|0> + (1-e^{-i3π/7})|1>] = cos(3π/14)|0> - i*sin(3π/14)|1>.
4. **Probabilities:** Measuring gives P(|0>) = cos²(3π/14) ≈ 0.6113 and P(|1>) = sin²(3π/14) ≈ 0.3887.

## isqTrain/3162

- task_id: `isqTrain/3162`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `2904`

### Prompt

Implement a quantum circuit in isQ: an isQ program: apply H, Rz(2*pi/128), H to a qubit and measure. This implements Rx(2*pi/128) via conjugation.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement an Rx(2π/128) rotation on a single qubit using H-Rz-H conjugation and measure the result.
Qubits: 1 qubit (q[0]), which is measured.
Evolution:
1. Start in |0>.
2. Apply H: state becomes |+> = (1/√2)(|0> + |1>).
3. Apply Rz(2π/128): state becomes (1/√2)(|0> + e^(-iπ/128)|1>).
4. Apply H: state becomes cos(π/128)|0> - i sin(π/128)|1>, which matches Rx(2π/128)|0>.
Probabilities:
P(|0>) = cos²(π/128) ≈ 0.9994
P(|1>) = sin²(π/128) ≈ 0.0006

## isqTrain/3351

- task_id: `isqTrain/3351`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `3443`

### Prompt

实现以下量子计算任务（使用isQ）：an isQ program: apply 2-qubit gate chain CNOT-X1 to |00> and measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply CNOT followed by X on qubit 1 to initial state |00>, then measure both qubits.
2. **Qubits**: 2 qubits (q[0], q[1]), both measured.
3. **State evolution**:
   - Start: |00⟩
   - After CNOT(q[0], q[1]): control q[0]=|0⟩, so target q[1] unchanged → |00⟩
   - After X(q[1]): flips q[1] from |0⟩ to |1⟩ → |01⟩
4. **Result**: Final state is |01⟩, so measurement yields |01⟩ with probability 1.0.

## isqTrain/3265

- task_id: `isqTrain/3265`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `2484`

### Prompt

Create an isQ quantum circuit that an isQ program: demonstrate S = T*T identity. Apply H, T, T, inv S, H to a qubit. Since T*T = S, and S * inv S = I, the net effect is H*H = I.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Verify the identity S = T*T by cancelling T*T with inv S, leaving H*H = I.
2. **Qubits:** 1 qubit `q[0]` is used and measured.
3. **State evolution:**
   - Start in |0>, apply H to get |+> = (|0> + |1>)/√2.
   - Apply T twice: |ψ> = (|0> + e^(iπ/2)|1>)/√2 = (|0> + i|1>)/√2. Since T*T = S, this is S|+>.
   - Apply inv S: S*inv S = I, so the state returns to |+>.
   - Apply H: H|+> = |0>.
4. **Probabilities:** The final state is exactly |0>, so measuring yields {|0>: 1.0}.

## isqTrain/608

- task_id: `isqTrain/608`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `5247`

### Prompt

Write isQ code for the following quantum task: implements a variant of the gate_decomposition pattern using q[7] -> q[8]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

Let me analyze this task. I need to write a reasoning section for an isQ program that implements a variant of the gate_decomposition pattern using q[7] -> q[8].

Analyzing the circuit requirements:
- It uses 8 qubits (q[0] to q[7])
- It applies X(q[0]) to flip qubit 0 from |0> to |1>
- Then applies swap (three-CNOT decomposition) gates: q[0]↔q[6], q[1]↔q[5], q[2]↔q[4]
- Measures all qubits
- Expected result: |01000000> with probability 1.0

Let me trace through the state evolution:
1. Initial state: |00000000>
2. After X(q[0]): |10000000>
3. After swap (three-CNOT decomposition)(q[0], q[6]): |00000010> (the |1> moves from position 0 to position 6)
4. After swap (three-CNOT decomposition)(q[1], q[5]): |00000010> (no change, both were |0>)
5. After swap (three-CNOT decomposition)(q[2], q[4]): |00000010> (no change, both were |0)
6. Final state: |00000010>

Wait, The predicted output |01000000>. Let me reconsider the bit ordering.

Actually, looking at the expected measurement probabilities: {|01000000>: 1.0}

The measurement output is a bitstring where "earlier measured qubit = higher bit". So if we measure q[0], q[1], ..., q[7], the bitstring would be q[0]q[1]q[2]q[3]q[4]q[5]q[6]q[7] from highest to lowest bit.

Let me trace again:
1. Initial: |00000000>
2. After X(q[0]): |10000000> (q[0]=1)
3. After swap (three-CNOT decomposition)(q[0], q[6]): q[0] and q[6] swap, so q[0]=0, q[6]=1 → |00000010>
4. After swap (three-CNOT decomposition)(q[1], q[5]): no change → |00000010>
5. After swap (three-CNOT decomposition)(q[2], q[4]): no change → |00000010>

Hmm, this gives |00000010> which in bitstring notation with q[0] as highest bit would be 00000010 in binary.

The predicted is |01000000>. Let me think about this more carefully.

If the bitstring is "01000000", that's 8 bits where position 0 (leftmost) is 0, position 1 is 1, etc.

So q[1]=1 and all others are 0.

But according to my trace, q[6]=1 and all others are 0.

There might be a different convention. Let me re-read the note: "earlier measured qubit = higher bit"

So if M(q) measures q[0] first, then q[0] is the highest bit. The bitstring "01000000" would mean:
- q[0] = 0 (highest bit, leftmost)
- q[1] = 1
- q[2] = 0
- q[3] = 0
- q[4] = 0
- q[5] = 0
- q[6] = 0
- q[7] = 0

But my trace gives q[6]=1, not q[1]=1.

Let me reconsider. Maybe there's an error in my understanding, or The implementation is different from what would produce |01000000>.

Actually, wait - the task says "using q[7] -> q[8]" which might mean using a 9-qubit register (indices 0-8) or just expanding from 7 to 8 qubits.

Analyzing the, it uses qbit q[8], which gives indices 0-7.

Let me re-examine. The predicted output |01000000>. If this means the state where qubit 1 is |1> and all others are |0>, then we'd need a different circuit.

Actually, maybe I should just trust The implementation and the predicted output, and produce reasoning accordingly. Perhaps there's a different swap (three-CNOT decomposition) pattern or the state interpretation is different.

Let me try another interpretation: maybe the swap (three-CNOT decomposition) gates are meant to demonstrate a pattern, and the actual predicted output comes from a different gate sequence.

Actually, looking more carefully at the task, it says to implement "a variant of the gate_decomposition pattern using q[7] -> q[8]". This suggests using 9 qubits (q[0] through q[
