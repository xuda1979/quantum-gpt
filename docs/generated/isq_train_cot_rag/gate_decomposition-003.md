# ISQ training COT RAG corpus: gate_decomposition shard 3

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/610

- task_id: `isqTrain/610`
- task_type: `output_prediction`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `5539`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;
qbit q[8];

procedure main() {
    X(q[0]);
    SWAP(q[0], q[7]);
    SWAP(q[1], q[6]);
    SWAP(q[2], q[5]);
    SWAP(q[3], q[4]);
    M(q);
}
```

### Chain-of-thought reasoning

The user wants to analyze an isQ program and predict its measurement probability distribution.
Program:
1. Initialize 8 qubits q[0] to q[7] in state |00000000>.
2. Apply X to q[0]. State becomes |10000000>.
3. Apply swap (three-CNOT decomposition)(q[0], q[7]). State becomes |00000001>.
4. Apply swap (three-CNOT decomposition)(q[1], q[6]). State remains |00000001> (since q[1] and q[6] are both |0>).
5. Apply swap (three-CNOT decomposition)(q[2], q[5]). State remains |00000001>.
6. Apply swap (three-CNOT decomposition)(q[3], q[4]). State remains |00000001>.
Wait, is the expected bitstring reversed in the prompt?
Expected measurement probabilities: {|10000000>: 1.0}
Let's re-read the predicted output. "Expected measurement probabilities: {|10000000>: 1.0}"
Ah! Why is it |10000000>?
Wait, if q[0] is the highest bit or lowest bit?
Wait, The implementation says: Expected measurement probabilities: {|10000000>: 1.0}.
Wait! But if swap (three-CNOT decomposition)(q[0], q[7]) swaps q[0] and q[7], the |1> moves to q[7].
If the bitstring is q[0]q[1]...q[7], it would be |00000001>.
Wait, let's look at the SWAPs:
swap (three-CNOT decomposition)(q[0], q[7])
swap (three-CNOT decomposition)(q[1], q[6])
swap (three-CNOT decomposition)(q[2], q[5])
swap (three-CNOT decomposition)(q[3], q[4])
This reverses the array of qubits!
Initially: q = |10000000> (q[0] is 1, q[1..7] are 0).
After the swaps, the array is reversed.
So q[0] gets q[7]'s value (0).
q[7] gets q[0]'s value (1).
So the state is |00000001> if the string is q[0]...q[7].
Wait, why does the reference say {|10000000>: 1.0}?
Wait! If The implementation says `Expected measurement probabilities: {|10000000>: 1.0}`, it might be because the reference actually computes `q[7]...q[0]` or there's something I missed?
Ah, maybe The implementation provided in the prompt has `{|00000001>: 1.0}` and I misread it?
Let me read carefully: `Expected measurement probabilities: {|10000000>: 1.0}`
Wait! The reference text provided is:

Wait, if I apply SWAPs to |10000000> to reverse the array, the state becomes 00000001.
Why does the reference say {|10000000>: 1.0}?
Could it be that X(q[0]) and then swap (three-CNOT decomposition)(q[0], q[7]) reverses it?
Wait, if q = |10000000>, and we reverse it, we get |00000001>.
Unless... the `M(q)` instruction measures and outputs the bitstring with q[0] as the lowest bit (LSB)?
Yes! `--probs output: array indexed by measurement bitstring (earlier measured qubit = higher bit).`
If earlier measured qubit is higher bit, then `M(q)` outputs `q[0] q[1] ... q[7]`.
Wait, if `q[0]` is the highest bit, then `|10000000>` means `q[0]=1`.
If the state after swaps is `q[7]=1`, then the bitstring is `00000001`.
Then why does the reference say `{|10000000>: 1.0}`?
Let's re-read the swaps:
swap (three-CNOT decomposition)(q[0], q[7]);
swap (three-CNOT decomposition)(q[1], q[6]);
swap (three-CNOT decomposition)(q[2], q[5]);
swap (three-CNOT decomposition)(q[3], q[4]);
If the initial state was |10000000>, q[0]=1.
After swap (three-CNOT decomposition)(q[0], q[7]), q[7]=1, q[0]=0. The string is 00000001.
Why would the reference say {|10000000>: 1.0}?
Is there a typo in the prompt's circuit implementation? "Expected measurement probabilities: {|10000000>: 1.0}"
Wait, if it's a typo in the prompt's reference, I should probably output what logically follows from the circuit, which is |00000001>: 1.0, or I should just follow The implementation.
Wait! Is

### Reference answer

{'predicted_probs': {'128': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/207. Dimension: predict probabilities for reference circuit.'}

## isqTrain/2467

- task_id: `isqTrain/2467`
- task_type: `code_equivalence`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `global_phase`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `382`

### Prompt

这两个isQ程序是等价的吗？

程序A：
```isq
import std;
qbit q[2];

procedure swap_gate(qbit a, qbit b) {
    CNOT(a, b);
    CNOT(b, a);
    CNOT(a, b);
}

procedure main() {
    X(q[1]);
    swap_gate(q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

程序B：
```isq
import std;
qbit q[2];

procedure swap_gate(qbit a, qbit b) {
    CNOT(a, b);
    CNOT(b, a);
    CNOT(a, b);
}

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    X(q[1]);
    swap_gate(q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A**: Initializes qubits to |00>, applies an X gate to q[1] to yield |10>, and then applies a swap gate using three CNOTs, resulting in the final state |01>.
2. **Program B**: Initializes qubits to |00>, applies a `GPhase(0.0)` operation, and then performs the exact same X gate and swap sequence as Program A, resulting in the final state |01>.
3. **Key difference**: Program B includes the `GPhase(0.0)` gate, which is absent in Program A.
4. **Probability distributions**: The measurement probabilities are identical. The `GPhase(0.0)` operation merely multiplies the quantum state by $e^{i0} = 1$, which acts as an identity operation and has no effect on the physical state or measurement outcomes.
5. **Verdict**: Equivalent: True

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/1702

- task_id: `isqTrain/1702`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5196`

### Prompt

I need an isQ program to Verify the gate identity HXH = Z on |+> by applying the gate sequence to a qubit and measuring.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Task:** Verify the gate identity $HXH = Z$ on $|+\rangle$ by applying the gate sequence to a qubit and measuring.
    *   **circuit implementation:** Provides an isQ code snippet that initializes a qubit (implicitly to $|0\rangle$), applies $H$, then $H$, then $X$, then $H$, then measures. *Wait, let me look at the reference code closely.*
        *   `H(q[0]);` -> state becomes $|+\rangle$
        *   `H(q[0]);` -> state becomes $|0\rangle$
        *   `X(q[0]);` -> state becomes $|1\rangle$
        *   `H(q[0]);` -> state becomes $|-\rangle$
        *   Measurement -> 50% $|0\rangle$, 50% $|1\rangle$.
    *   *Self-Correction/Refinement on reference:* The prompt says "Verify the gate identity HXH = Z on |+>". The reference code applies `H, H, X, H` to $|0\rangle$, which effectively applies $HHXH|0\rangle = XH|0\rangle = X|+\rangle = |-\rangle$.
    *   Wait, the prompt states "Verify the gate identity HXH = Z on |+>". If it's on $|+\rangle$, applying $Z$ to $|+\rangle$ yields $|-\rangle$. So the final state should indeed be $|-\rangle$. The reference code does exactly this by starting at $|0\rangle$, applying $H$ to get $|+\rangle$, then applying $H, X, H$ which equals $Z$. Thus, it applies $Z$ to $|+\rangle$.
    *   Let's trace the reference code accurately: Initial state is $|0\rangle$.
        1. `H(q[0])` $\to |+\rangle$
        2. `H(q[0])` $\to |0\rangle$
        3. `X(q[0])` $\to |1\rangle$
        4. `H(q[0])` $\to |-\rangle$
    *   Wait, the reference code says:
        `H(q[0]);`
        `H(q[0]);`
        `X(q[0]);`
        `H(q[0]);`
        This sequence is exactly $HXH$ applied to $|+\rangle$ (which is the state after the first $H$). The result is $Z|+\rangle = |-\rangle$.
    *   Expected probabilities: $\{|0\rangle: 0.5, |1\rangle: 0.5\}$.
    *   Goal of circuit: Verify $HXH = Z$ on $|+\rangle$ by preparing $|+\rangle$, applying $HXH$, and measuring.
    *   Qubits needed: 1 qubit (`q[0]`).
    *   Evolution:
        *   Start: $|0\rangle$
        *   `H`: $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$
        *   `H`: $|0\rangle$
        *   `X`: $|1\rangle$
        *   `H`: $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$
    *   Expected probabilities: The final state $|-\rangle$ has $50\%$ probability of being measured as $|0\rangle$ and $50\%$ as $|1\rangle$.

2.  **Format Requirements:**
    *   Start with "## Reasoning"
    *   3-8 lines (simple circuit).
    *   Use Dirac notation.
    *   NO isQ code blocks.
    *   Concise and precise.

3.  **Drafting the Reasoning:**
    ## Reasoning
    Goal: Verify the identity $HXH = Z$ by applying $HXH$ to $|+\rangle$, which should equal $Z|+\rangle = |-\rangle$.
    Qubits: 1 qubit (`q[0]`).
    State evolution starting from $|0\rangle$:
    1. `H(q[0])`: Transforms $|0\rangle$ to $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
    2. `H(q[0])`: Transforms $|+\rangle$ to $|0\rangle$.
    3. `X(q[0])`: Transforms $|0

## isqTrain/3399

- task_id: `isqTrain/3399`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `4698`

### Prompt

Write isQ code for the following quantum task: an isQ program: H, Rz(1*pi/5), H on a qubit. This is equivalent to Rx(1*pi/5).

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply H·Rz(π/5)·H to a single qubit, equivalent to Rx(π/5).
2. One qubit is used and measured.
3. State evolution: |0> →H |+> →Rz(π/5) (e^{-iπ/10}|0> + e^{iπ/10}|1>)/√2 →H cos(π/10)|0> − i·sin(π/10)|1>, which is Rx(π/5)|0>.
4. Probabilities: P(|0>) = cos²(π/10) ≈ 0.9045, P(|1>) = sin²(π/10) ≈ 0.0955.

## isqTrain/3342

- task_id: `isqTrain/3342`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2119`

### Prompt

I need an isQ program to an isQ program: apply gate chain X-S-T-H to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply the gate sequence X-S-T-H to a single qubit initialized to |0⟩, then measure.
2. **Qubits**: 1 qubit is needed and measured.
3. **State evolution**:
   - Initial: |0⟩
   - X: |0⟩ → |1⟩
   - S: |1⟩ → i|1⟩
   - T: i|1⟩ → ie^{iπ/4}|1⟩ = e^{i3π/4}|1⟩
   - H: e^{i3π/4}|1⟩ → e^{i3π/4}(|0⟩ − |1⟩)/√2
4. **Probabilities**: The global phase e^{i3π/4} drops out, leaving equal amplitudes for |0⟩ and |1⟩, so P(|0⟩) = P(|1⟩) = 0.5.

## isqTrain/3347

- task_id: `isqTrain/3347`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `3067`

### Prompt

Code this in isQ: an isQ program: apply 2-qubit gate chain CZ-CNOT to |00> and measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply a CZ-CNOT gate chain to the |00> state, then measure both qubits.
2. **Qubits**: 2 qubits (q[0], q[1]), both measured.
3. **State evolution**:
   - Initial state: |00>
   - After CZ(q[0], q[1]): CZ applies Z to q[1] when q[0]=|1>. Since q[0]=|0>, no change → |00>
   - After CNOT(q[0], q[1]): CNOT flips q[1] when q[0]=|1>. Since q[0]=|0>, no change → |00>
4. **Measurement**: The final state is |00> with probability 1.0, yielding outcome |00> with certainty.

## isqTrain/541

- task_id: `isqTrain/541`
- task_type: `output_prediction`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `4330`

### Prompt

预测以下isQ代码的输出概率：

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

1.  **Analyze the Request:**
    *   **Role:** Quantum computing expert.
    *   **Task:** Analyze an isQ program and predict the probability distribution.
    *   **Format Constraints:** Concise (3-15 lines), step-by-step reasoning using Dirac notation, output ONLY the analysis starting with "## Circuit Analysis", end with the predicted probability distribution, NO `isq` code blocks.
    *   **Input Program:**
        

2.  **Trace Quantum State Evolution:**
    *   **Initial state:** |q[1] q[0]> = |00>
    *   **Step 1: `X(q[1])`** -> Flips q[1] to |1>. State becomes |10>.
    *   **Step 2: `CNOT(q[0], q[1])`** -> Control: q[0], Target: q[1]. Since q[0] is 0, target is unchanged. State remains |10>.
    *   **Step 3: `CNOT(q[1], q[0])`** -> Control: q[1], Target: q[0]. Since q[1] is 1, q[0] is flipped (0 -> 1). State becomes |11>.
    *   **Step 4: `CNOT(q[0], q[1])`** -> Control: q[0], Target: q[1]. Since q[0] is 1, q[1] is flipped (1 -> 0). State becomes |01>.
    *   *Wait, let's re-verify Step 3 and 4.*
        *   Initial: |00>
        *   `X(q[1])`: |10>  (q[1]=1, q[0]=0)
        *   `CNOT(q[0], q[1])`: Control is q[0]=0, Target is q[1]. Target not flipped. State = |10>.
        *   `CNOT(q[1], q[0])`: Control is q[1]=1, Target is q[0]. Target flipped (0->1). State = |11>.
        *   `CNOT(q[0], q[1])`: Control is q[0]=1, Target is q[1]. Target flipped (1->0). State = |01>.
    *   Let me double-check the "Expected measurement probabilities" in the prompt. The prompt says `Expected measurement probabilities: {|10>: 1.0}`.
    *   Let me re-read the standard definitions. Often standard tensor products are $q_1 \otimes q_0$ or $q_0 \otimes q_1$.
    *   If standard Dirac is $|q_1 q_0\rangle$:
        *   `X(q[1])` on $|00\rangle \to |10\rangle$
        *   `CNOT(q[0], q[1])` -> $CX_{01}$. Control $q_0=0$, so target $q_1$ is unchanged. State remains $|10\rangle$.
        *   `CNOT(q[1], q[0])` -> $CX_{10}$. Control $q_1=1$, so target $q_0$ is flipped ($0 \to 1$). State becomes $|11\rangle$.
        *   `CNOT(q[0], q[1])` -> $CX_{01}$. Control $q_0=1$, so target $q_1$ is flipped ($1 \to 0$). State becomes $|01\rangle$.
        *   Wait, is this a swap (three-CNOT decomposition) network?
        *   Let's check CNOT gates: $CX_{01} CX_{10} CX_{01}$ is exactly a swap operation (three-CNOT decomposition).
        *   $CX_{01} CX_{10} CX_{01} |10\rangle = \text{swap (three-CNOT decomposition)} |10\rangle = |01\rangle$.
        *   But the prompt says: `Expected measurement probabilities: {|10>: 1.0}`.
        *   Why would it be `|10>: 1.0`?
        *   Ah! Is the bitstring representation in the prompt `|q[0] q[1]>`?
        *   In the prompt rules: "--probs output: array indexed by measurement bitstring (earlier measured qubit = higher bit)."
        *   Measurements: `M(q[0]);

### Reference answer

{'predicted_probs': {'2': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/165. Dimension: predict probabilities for reference circuit.'}

## isqTrain/3134

- task_id: `isqTrain/3134`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2434`

### Prompt

Write an isQ program that an isQ program: apply gate chain ZX to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply gate sequence ZX to |0> and measure.
2. Qubits needed: 1; measured: q[0].
3. State evolution:
   - Initial: |0>
   - After Z: Z|0> = |0>
   - After X: X|0> = |1>
4. Measurement yields |1> with probability 1.0.

## isqTrain/4406

- task_id: `isqTrain/4406`
- task_type: `output_prediction`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `global_phase`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5222`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[2];

procedure crz_gate(double theta, qbit c, qbit t) {
    Rz(theta/2.0, t);
    CNOT(c, t);
    Rz(-theta/2.0, t);
    CNOT(c, t);
}

procedure main() {
    // Prepare |11> state
    X(q[0]);
    X(q[1]);
    // Apply controlled-Rz(pi) gate
    crz_gate(pi, q[0], q[1]);
    // Measure both qubits
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

Let me analyze this isQ program step by step.

1. Initial state: |00>

2. After X(q[0]) and X(q[1]): |11>

3. Now we apply crz_gate(pi, q[0], q[1]):
   - crz_gate applies a controlled-Rz gate. Let me trace through:
   - Rz(pi/2, q[1]) on |11>: Rz(θ)|1⟩ = e^{-iθ/2}|1⟩, so |11⟩ → e^{-iπ/4}|11⟩
   - CNOT(q[0], q[1]): control is q[0]=1, target is q[1]=1, so q[1] flips to 0 → e^{-iπ/4}|10⟩
   - Rz(-pi/2, q[1]) on |10⟩: Rz(-π/2)|0⟩ = e^{iπ/4}|0⟩, so → e^{-iπ/4}·e^{iπ/4}|10⟩ = |10⟩
   - CNOT(q[0], q[1]): control is q[0]=1, target is q[1]=0, so q[1] flips to 1 → |11⟩

   Wait, let me reconsider. The CRZ gate applies Rz(θ) to the target when the control is |1⟩. Let me think about what the decomposition actually does.

   Actually, let me reconsider the standard decomposition of CRz. The CRz(θ) gate has the matrix:
   diag(1, 1, 1, e^{iθ})
   
   Wait no. CRz(θ) applies Rz(θ) to the target when control is |1⟩. So:
   
   CRz(θ)|00⟩ = |00⟩
   CRz(θ)|01⟩ = |01⟩
   CRz(θ)|10⟩ = Rz(θ)|0⟩ ⊗ |1⟩_c ... 
   
   Wait, I need to be careful about which qubit is which. q[0] is control, q[1] is target.

   Actually, the standard CRz matrix with control as first qubit and target as second:
   
   |00⟩ → |00⟩
   |01⟩ → |01⟩
   |10⟩ → Rz(θ)|0⟩ = |0⟩ ... wait
   
   Hmm, let me think more carefully. The Rz gate applies a phase to |1⟩: Rz(θ)|0⟩ = e^{-iθ/2}|0⟩, Rz(θ)|1⟩ = e^{iθ/2}|1⟩.

   So CRz(θ) = |0⟩⟨0|_c ⊗ I_t + |1⟩⟨1|_c ⊗ Rz(θ)_t
   
   This gives:
   |00⟩ → e^{-iθ/2} |00⟩
   |01⟩ → e^{iθ/2} |01⟩  
   |10⟩ → |10⟩
   |11⟩ → e^{iθ/2} |11⟩

   Wait, that's not right either. Let me be more careful.

   CRz(θ)|00⟩ = |0⟩⟨0| ⊗ I |00⟩ + |1⟩⟨1| ⊗ Rz(θ) |00⟩
   = |0⟩ ⊗ |0⟩ + 0 = |00⟩

   Hmm, but Rz(θ) = diag(e^{-iθ/2}, e^{iθ/2}).

   CRz(θ)|00⟩ = |00⟩  (no phase from Rz since control is |0⟩)
   CRz(θ)|01⟩ = |01⟩  (no phase from Rz since control is |0⟩)
   CRz(θ)|10⟩ = |1⟩ ⊗ Rz(θ)|0⟩ = e^{-iθ/2}|10⟩
   CRz(θ)|11⟩ = |1⟩ ⊗ Rz(θ)|1⟩ = e^{iθ/2}|11⟩

   Now let's trace through the decomposition for the |11⟩ state with θ = π:

   Step 1: Rz(π/2, q[1]) on |11⟩
   Rz(π/2)|1⟩ = e^{iπ/4}|1⟩
   State: e^{iπ/4}|11⟩

   Step 2: CNOT(q[0], q[1]) on e^{iπ/4}|11⟩
   CNOT flips q[1] since q[0] = 1: |11⟩ → |10⟩
   State: e^{iπ/

### Reference answer

{'predicted_probs': {'01': 1.0}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|01>) = 1.0000.'}

## isqTrain/3259

- task_id: `isqTrain/3259`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `reversible_computing`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `2394`

### Prompt

I need an isQ program to an isQ program: apply H twice to each of 1 qubits (H*H=I), then measure. All should be |0>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Demonstrate that applying the Hadamard gate twice acts as the identity (H² = I), returning the qubit to its initial state.
2. **Qubits**: 1 qubit (`q[0]`), which is measured.
3. **State evolution**:
   - Initial state: `|0⟩`
   - After first H: `H|0⟩ = |+⟩ = (1/√2)(|0⟩ + |1⟩)`
   - After second H: `H|+⟩ = |0⟩` (since H² = I)
4. **Measurement**: The final state is `|0⟩`, so measuring yields `|0⟩` with probability 1.0.
