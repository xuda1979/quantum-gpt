# ISQ training COT RAG corpus: gate_decomposition shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3283

- task_id: `isqTrain/3283`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3757`

### Prompt

实现以下量子计算任务（使用isQ）：an isQ program: apply Rx(1*pi/4) then Rx(-1*pi/4) to cancel. Measure: should get |0>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Demonstrate that two opposite Rx rotations cancel, returning the qubit to |0⟩.
2. **Qubits**: 1 qubit (`q[0]`), which is measured.
3. **State evolution**:
   - Start: |0⟩
   - After Rx(π/4): cos(π/8)|0⟩ − i·sin(π/8)|1⟩
   - After Rx(−π/4): Rx(−π/4)·Rx(π/4)|0⟩ = I|0⟩ = |0⟩
4. **Probabilities**: Since the two Rx rotations are inverses, the final state is exactly |0⟩, giving P(|0⟩) = 1.0, P(|1⟩) = 0.0.

## isqTrain/3293

- task_id: `isqTrain/3293`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4658`

### Prompt

Write isQ code for the following quantum task: an isQ program: apply H, Rz(2*pi/3), Rz(-2*pi/3), H. Since Rz cancels, net is H*H=I.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Demonstrate that H-H sandwich with cancelling Rz rotations yields identity.
2. **Qubits**: 1 qubit `q[0]`, measured at the end.
3. **State evolution**:
   - Start: |0⟩
   - H → |+⟩ = (|0⟩+|1⟩)/√2
   - Rz(2π/3) → (e^{-iπ/3}|0⟩ + e^{iπ/3}|1⟩)/√2 (Z-axis phase rotation)
   - Rz(-2π/3) → phases cancel: (|0⟩+|1⟩)/√2 = |+⟩ (since Rz(θ)·Rz(-θ)=I)
   - H → |0⟩ (since H|+⟩=|0⟩)
4. **Expected probabilities**: {|0⟩: 1.0} because the net circuit is H·Rz(2π/3)·Rz(-2π/3)·H = H·I·H = I.

## isqTrain/3133

- task_id: `isqTrain/3133`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `4106`

### Prompt

Help me write isQ code that an isQ program: apply Toffoli (ctrl ctrl X) on initial state |111> where q[0]=1, q[1]=1, q[2]=1 (target).

### Chain-of-thought reasoning

## Reasoning
Goal: Apply a Toffoli gate to |111⟩ with q[0], q[1] as controls and q[2] as target.

Three qubits q[0], q[1], q[2] are declared globally; all three are measured.

State evolution:
1. Initial: |000⟩
2. X(q[0]), X(q[1]), X(q[2]) → |111⟩
3. Toffoli: both controls (q[0], q[1]) are |1⟩, so target q[2] flips: |111⟩ → |110⟩

Final state |110⟩ yields measurement probability {|110⟩: 1.0}.

## isqTrain/3348

- task_id: `isqTrain/3348`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `211`

### Prompt

Help me write isQ code that an isQ program: apply 2-qubit gate chain H0-CZ-H0 to |00> and measure both qubits.

### Chain-of-thought reasoning

## Reasoning
- Goal: Apply H0-CZ-H0 to |00⟩ and measure both qubits, showing the circuit acts as identity here.
- Qubits: 2 (q[0], q[1]), both measured.
- Evolution: |00⟩ → H₀ → (|00⟩+|10⟩)/√2 → CZ → (|00⟩+|10⟩)/√2 (CZ only phases |11⟩, not present) → H₀ → |00⟩.
- Since q[1] stays |0⟩ throughout, CZ never applies its -1 phase, and H₀-H₀ = I on q[0].
- Result: {|00⟩: 1.0}.

## isqTrain/3172

- task_id: `isqTrain/3172`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_deriving_gate`, `isq_syntax_inv`, `entanglement`
- source: `isq_train_cot`
- dataset_index: `1974`

### Prompt

Code this in isQ: with a procedure `encode` that applies H(a) then CNOT(a,b), marked with `} deriving gate`. In main, apply encode to create Bell pair, then inv encode to decode, and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** The program creates a Bell pair using an `encode` procedure, then applies the inverse to decode it, demonstrating perfect state reversal.
2. **Qubits:** 2 global qubits (`q[0]`, `q[1]`), both are measured.
3. **State Evolution:**
   - Initialize as `|00>`.
   - Apply `encode` (`H` on `q[0]`, then `CNOT` on `q[1]` controlled by `q[0]`): 
     `|00>` → `(|0> + |1>)/√2 ⊗ |0>` → `(|00> + |11>)/√2`
   - Apply `inv encode` (inverse `CNOT`, then inverse `H` on `q[0]`):
     `(|00> + |11>)/√2` → `(|00> + |10>)/√2` → `|00>`
4. **Probabilities:** The final state is deterministically `|00>`, so measuring both qubits yields `00` with a probability of 1.0.

## isqTrain/1428

- task_id: `isqTrain/1428`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `isq_syntax_inv`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3461`

### Prompt

Implement the following in isQ: Apply S then S-dagger (identity) to |+> state and measure. Verify the gate identity SdagS = I.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Apply the gate sequence S then S-dagger to the |+> state to verify the identity S-dagger * S = I.
2. **Qubits:** 1 qubit (`q[0]`) is used and measured.
3. **State evolution:**
   - Initialize `q[0]` to |0>.
   - `H(q[0])`: Transforms the state to |+> = 1/sqrt(2)(|0> + |1>).
   - `S(q[0])`: Applies a pi/2 phase to |1>, resulting in 1/sqrt(2)(|0> + i|1>).
   - `inv S(q[0])`: Applies a -pi/2 phase to |1>, undoing the previous operation and returning the state to |+> = 1/sqrt(2)(|0> + |1>).
4. **Measurement probabilities:** Since the final state is exactly |+>, measuring in the computational basis yields an equal probability of |0> and |1>, giving {|0>: 0.5, |1>: 0.5}.

## isqTrain/3338

- task_id: `isqTrain/3338`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5564`

### Prompt

Write isQ code for the following quantum task: an isQ program: apply gate chain X-S-H to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply the gate sequence X → S → H to a single qubit initialized in |0⟩, then measure it.
2. One qubit is needed and measured (q[0]).
3. State evolution:
   - Start: |0⟩
   - After X: X|0⟩ = |1⟩
   - After S: S|1⟩ = i|1⟩ (S applies phase i to |1⟩)
   - After H: H(i|1⟩) = i · (|0⟩ - |1⟩)/√2 = (i|0⟩ - i|1⟩)/√2
4. The final state has equal-amplitude superposition with |i/√2|² = 1/2 probability for each outcome, giving P(|0⟩) = 0.5 and P(|1⟩) = 0.5.

## isqTrain/3350

- task_id: `isqTrain/3350`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `1107`

### Prompt

Implement a quantum circuit in isQ: an isQ program: apply 2-qubit gate chain CNOT-X0 to |00> and measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Prepare state |10⟩ by applying CNOT then X to an initial |00⟩ state.
2. Two qubits needed (q[0], q[1]), both measured.
3. Initial state: |00⟩. CNOT(q[0], q[1]) leaves state as |00⟩ (control is |0⟩). X(q[0]) flips q[0] to |1⟩, giving |10⟩.
4. Measuring yields |10⟩ with probability 1.0, since the final state is exactly |10⟩.

## isqTrain/607

- task_id: `isqTrain/607`
- task_type: `output_prediction`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `308`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
qbit q[6];

procedure main() {
    X(q[0]);
    SWAP(q[0], q[5]);
    SWAP(q[1], q[4]);
    SWAP(q[2], q[3]);
    M(q);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a concise step-by-step analysis of the provided isQ quantum program, ending with the probability distribution of the measurement outcomes.
2.  **Analyze the isQ code:**
    *   `qbit q[6];`: Initializes a 6-qubit register in the state $|000000\rangle$.
    *   `X(q[0]);`: Applies an X gate to qubit 0. State becomes $|100000\rangle$.
    *   `swap (three-CNOT decomposition)(q[0], q[5]);`: Swaps qubit 0 and qubit 5. State becomes $|000001\rangle$.
    *   `swap (three-CNOT decomposition)(q[1], q[4]);`: Swaps qubit 1 and qubit 4. Both are $|0\rangle$, state remains $|000001\rangle$.
    *   `swap (three-CNOT decomposition)(q[2], q[3]);`: Swaps qubit 2 and qubit 3. Both are $|0\rangle$, state remains $|000001\rangle$.
    *   `M(q);`: Measures all qubits.
3.  **Check measurement ordering/endianness:**
    *   The prompt specifies: "`--probs output: array indexed by measurement bitstring (earlier measured qubit = higher bit)`."
    *   `M(q)` implicitly measures `q[0], q[1], q[2], q[3], q[4], q[5]` in that order.
    *   The state is `q[5]=|1>` and the rest `|0>`.
    *   Bitstring: `q[0]` is highest bit, `q[5]` is lowest bit.
    *   So `q[5]=|1>` corresponds to `000001`.
    *   Wait, let me double check The implementation / predicted output in the prompt!
    *   "Expected measurement probabilities: {|100000>: 1.0}".
    *   Ah! Wait. Let's re-read The implementation: `{|100000>: 1.0}`.
    *   Let me re-evaluate `swap (three-CNOT decomposition)(q[0], q[5])`. If the state was $|1\rangle$ on `q[0]` and $|0\rangle$ on `q[5]`, swap (three-CNOT decomposition) moves $|1\rangle$ to `q[5]`. So the state is `|000001>`.
    *   Why does the reference say `|100000>`?
    *   Let's re-read the bitstring rule: "earlier measured qubit = higher bit".
    *   If `M(q)` measures `q[0]` first, `q[0]` is the highest bit.
    *   If `q[5]` is $|1\rangle$, it's the lowest bit, so it should be `000001`.
    *   Let's look at the circuit implementation again: `Expected measurement probabilities: {|100000>: 1.0}`.
    *   Wait! Is it possible that the predicted output implies no swap (three-CNOT decomposition) happened, or X was applied to `q[0]` and swap (three-CNOT decomposition) failed, or `q[0]` is the *lowest* bit?
    *   Or maybe the swap (three-CNOT decomposition) reversed the register entirely?
    *   Wait, if `q[0]` is the highest bit, and `X(q[0])` was applied, the state is `100000`.
    *   If it was SWAPped to `q[5]`, it's `000001`.
    *   If the expected is `100000`, is `q[0]` the *lowest* bit? "earlier measured qubit = higher bit". `M(q)` measures `q[0]` first. So `q[0]` is highest bit. Then `q[1]`, `q[2]`, `q[3]`, `q[4]`, `q[5]`.
    *   Could The implementation in the prompt be a mistake in the prompt itself?
    *   "circuit implementation / circuit code: ... Expected measurement probabilities: {|100000>: 1.0}"
    *   Actually, if `q[5]` is 1, and `q[5]` is the lowest bit, the string is `000001`. If `q[0]` is the *lowest* bit, then `100000`. But the prompt says "earlier measured qubit = higher bit". `M(q)` measures `q[0]` first. So `q[0]` is highest bit.
    *   Let me check standard isQ behavior. Often, isQ bitstrings have `q[0]` as the lowest

### Reference answer

{'predicted_probs': {'32': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/205. Dimension: predict probabilities for reference circuit.'}

## isqTrain/1337

- task_id: `isqTrain/1337`
- task_type: `output_prediction`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_procedures`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5360`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[3];

procedure cz_gate(qbit a, qbit b) {
    H(b);
    CNOT(a, b);
    H(b);
}

procedure main() {
    X(q[0]);
    X(q[1]);
    cz_gate(q[0], q[1]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a concise step-by-step quantum circuit analysis for an isQ program, predicting the final measurement probability distribution.
2.  **Analyze the isQ Code:**
    *   `qbit q[3]`: 3 qubits initialized to $|000\rangle$.
    *   `X(q[0]); X(q[1]);`: Apply X gate to q[0] and q[1]. State becomes $|110\rangle$.
    *   `cz_gate(q[0], q[1]);`: Apply a CZ gate between q[0] (control) and q[1] (target).
        *   Wait, let's trace `cz_gate`:
            *   `H(b)`: Hadamard on q[1].
            *   `CNOT(a, b)`: CNOT with q[0] as control, q[1] as target.
            *   `H(b)`: Hadamard on q[1].
        *   This is the standard decomposition of a CZ gate.
        *   Since the initial state before `cz_gate` is $|11\rangle$ (for q[0], q[1]), the CZ gate applies a Z gate to q[1] when q[0] is $|1\rangle$. So $|11\rangle \to -|11\rangle$.
    *   Wait, is it $-|11\rangle$? Yes, CZ applies a phase of -1.
    *   Actually, let's look at the global state: $|110\rangle \to -|110\rangle$.
    *   Since global phase is unmeasurable, the measurement probabilities will be $100\%$ for $|110\rangle$.
3.  **Step-by-Step State Evolution:**
    *   Initial: $|000\rangle$
    *   X(q[0]), X(q[1]): $|110\rangle$
    *   `cz_gate`:
        *   H(q[1]): $|1\rangle \otimes (H|1\rangle) \otimes |0\rangle = \frac{1}{\sqrt{2}} (|10\rangle - |11\rangle) \otimes |0\rangle = \frac{1}{\sqrt{2}}(|100\rangle - |110\rangle)$
        *   CNOT(q[0], q[1]): flips q[1] if q[0] is 1.
            *   $|10\rangle \to |11\rangle$
            *   $|11\rangle \to |10\rangle$
            *   State: $\frac{1}{\sqrt{2}}(|110\rangle - |100\rangle)$
        *   H(q[1]):
            *   Wait, let's re-evaluate H on q[1] for $\frac{1}{\sqrt{2}}(|110\rangle - |100\rangle)$.
            *   $|100\rangle \to |1\rangle \otimes |0\rangle \otimes |0\rangle \to |1\rangle \otimes |+\rangle \otimes |0\rangle = \frac{1}{\sqrt{2}}(|100\rangle + |110\rangle)$
            *   $|110\rangle \to |1\rangle \otimes |1\rangle \otimes |0\rangle \to |1\rangle \otimes |-\rangle \otimes |0\rangle = \frac{1}{\sqrt{2}}(|100\rangle - |110\rangle)$
            *   Total state: $\frac{1}{\sqrt{2}} [ \frac{1}{\sqrt{2}}(|100\rangle - |110\rangle) - \frac{1}{\sqrt{2}}(|100\rangle + |110\rangle) ] = \frac{1}{2}( -2|110\rangle ) = -|110\rangle$.
    *   Final state is $-|110\rangle$. Measurement is not sensitive to the global phase.
4.  **Format the Output:**
    *   Start with "## Circuit Analysis".
    *   Keep it concise (3-8 lines).
    *   End with the predicted probability distribution.
5.  **Drafting the response:**
    ## Circuit Analysis
    1. The circuit initializes 3 qubits to |000>, applies an X gate to q[0] and q[1], and then applies a controlled-Z gate (via standard CNOT-H decomposition) between q[0] and q[1].
    2. Initial state is |000>. After the X gates, the state is |110>.
    3. The `cz_gate(q[0], q[1

### Reference answer

{'predicted_probs': {'6': 1.0}, 'explanation': 'Parametric variant of isqEval/485. Dimension: qubit_variant: q[2] -> q[3].'}
