# ISQ training COT RAG corpus: quantum_algorithms shard 25

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4081

- task_id: `isqTrain/4081`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `3549`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;
qbit q[3];

unit grover_oracle(qbit q[3]) {
    X(q[1]);
    X(q[2]);
    ctrl CZ(q[0], q[1], q[2]);
    X(q[2]);
    X(q[1]);
} deriving gate

unit grover_diffusion(qbit q[3]) {
    H(q[0]);
    H(q[1]);
    H(q[2]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    ctrl CZ(q[0], q[1], q[2]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    H(q[0]);
    H(q[1]);
    H(q[2]);
} deriving gate

procedure main() {
    H(q[0]); H(q[1]); H(q[2]);
    grover_oracle(q);
    grover_diffusion(q);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The objective is to predict the measurement outcome of a 3-qubit isQ circuit, which represents a Grover's search algorithm. I need to provide a step-by-step analysis using Dirac notation, keeping it concise (3-15 lines) and outputting only the "## Circuit Analysis" section, ending with the probability distribution.

2.  **Analyze the Circuit**:
    *   **Initialization**: 3 qubits initialized to $|000\rangle$.
    *   **Superposition**: Hadamard on all qubits $H^{\otimes 3}$, state becomes $|+\rangle^{\otimes 3} = \frac{1}{\sqrt{8}} \sum_{x=0}^{7} |x\rangle$.
    *   **Oracle**: `grover_oracle` applies X to q[1], q[2], then a controlled-Z (CZ with 2 controls, i.e., Toffoli equivalent with Z), then X to q[1], q[2]. This targets the basis state where q[1]=0 and q[2]=0, which is $|100\rangle$. The oracle flips the phase of $|100\rangle$ to $-|100\rangle$.
    *   **Diffusion**: `grover_diffusion` applies $H^{\otimes 3}$, $X^{\otimes 3}$, CZ (controlled on q[0], q[1] acting on q[2]), $X^{\otimes 3}$, $H^{\otimes 3}$. Wait, let's look at `ctrl CZ(q[0], q[1], q[2])`. This means CZ is applied to q[2] conditioned on q[0] and q[1] being |1>. So it's a controlled-controlled-Z (double-controlled-Z (ctrl @[c1, c2] Z(target))) gate. This is the standard Grover diffusion operator on 3 qubits.
    *   **Amplitude Amplification**: The oracle marks $|100\rangle$. The diffusion operator amplifies this state. One iteration of Grover's algorithm perfectly flips the state from the uniform superposition to the target state.
    *   **Final state**: $|100\rangle$.

3.  **Verify the Oracle State**:
    *   $|q_0 q_1 q_2\rangle$
    *   Oracle applies X to $q_1, q_2$.
    *   Then applies CZ(q[0], q[1], q[2]). This means apply Z to q[2] if $q_0=1, q_1=1$.
    *   Wait, $Z |0\rangle = |0\rangle$ and $Z |1\rangle = -|1\rangle$. So if q[2] was 1, it becomes -1.
    *   The control is q[0], q[1]. So if $q_0=1, q_1=1$, and $q_2=1$, phase flips.
    *   The state being targeted before X gates is $q_0=1, q_1=1, q_2=1 \implies |111\rangle$.
    *   Since X gates are applied to $q_1, q_2$ *before* and *after*, it actually targets $q_1=0, q_2=0$.
    *   Let's trace: $|q_0, 0, 0\rangle \xrightarrow{X} |q_0, 1, 1\rangle \xrightarrow{double-controlled-Z (ctrl @[c1, c2] Z(target))} -|1, 1, 1\rangle$ (if $q_0=1$) $\xrightarrow{X} -|1, 0, 0\rangle$.
    *   So the marked state is indeed $|100\rangle$. (Assuming q[0] is the left-most bit, or whichever bitstring representation is standard, usually $q_0 q_1 q_2$).

4.  **Verify Grover Iteration Mathematically**:
    *   Initial: $|s\rangle = \frac{1}{\sqrt{8}} \sum |x\rangle$.
    *   $|w\rangle = |100\rangle$.
    *   Oracle: $U_w |s\rangle = |s\rangle - 2|w\rangle \langle w|s\rangle = |s\rangle - 2 \frac{1}{\sqrt{8}} |100\rangle$.
    *   Diffusion: $U_s = 2|s\rangle \langle s| - I$.
    *   $U_s U_w |s\rangle = (2|s\rangle \

### Reference answer

Dominant output states: |100> with probability ~0.78 each

## isqTrain/3891

- task_id: `isqTrain/3891`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `isq_syntax_oracle`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `2038`

### Prompt

There's an error in this quantum circuit implementation. Fix it:

```
import std;
// Bernstein-Vazirani: find secret string s = 101
oracle f(3, 1) = [0, 1, 0, 1, 1, 0, 1, 0];
qbit q[4];  // 3 input + 1 output

procedure main() {
    // Prepare |->  on output qubit
    X(q[3]);
    X(q[3]);
    // Hadamard on input qubits
    for i in 0:3 {
        H(q[i]);
    }
    // Apply BV oracle
    f(q[0], q[1], q[2], q[3]);
    // Final Hadamard on inputs
    for i in 0:3 {
        H(q[i]);
    }
    // Measure inputs to reveal secret string
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: The preparation of the output qubit `q[3]` has two consecutive `X(q[3])` gates, which cancel each other out (X·X = I), leaving `q[3]` in |0⟩ instead of the required |−⟩ state.

2. **Fix**: Replace the second `X(q[3])` with `H(q[3])`, so the output qubit preparation becomes `X(q[3]); H(q[3]);`, which correctly produces |−⟩ = (|0⟩ − |1⟩)/√2.

3. **State evolution (corrected)**:
   - `q[3]`: |0⟩ →X→ |1⟩ →H→ |−⟩
   - `q[0..2]`: |000⟩ →H⊗3→ |+⟩⊗³ (equal superposition)
   - Oracle `f` (encoding s=101): phase kickback flips the sign for basis states |x⟩ where x·s mod 2 = 1, applying I⊗I⊗Z controlled on the input register to `q[3]`. This effectively encodes s into the input qubits' relative phases.
   - Final H⊗3 on `q[0..2]`: converts phase encoding back to computational basis, yielding |101⟩ on inputs.
   - `q[3]` returns to |−⟩, so measuring it gives 0 or 1 with equal probability.
   - Result: {|1010⟩: 0.5, |1011⟩: 0.5}, correctly revealing s = 101.

## isqTrain/4547

- task_id: `isqTrain/4547`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `reversible_computing`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2376`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
qbit q[3];

procedure main() {
    
    H(q[0]);
    H(q[1]);
    
    CNOT(q[1], q[2]);
    
    H(q[2]); // superposition on last qubit
    M(q[2]);
}
```

### Chain-of-thought reasoning

Step 1: Initial state |q[0], q[1], q[2]> = |000>.
Step 2: H(q[0]) -> |+00> = (|000> + |100>)/sqrt(2).
Step 3: H(q[1]) -> (|000> + |010> + |100> + |110>)/2.
Step 4: CNOT(q[1], q[2]) -> (|000> + |011> + |100> + |111>)/2.
Step 5: H(q[2]) applies to the last qubit. Let's trace out q[2].
|0>_2 -> |+>_2
|1>_2 -> |->_2
The state becomes (1/2) (|00>|+> + |01>|-> + |10>|+> + |11>|->)
= (1/(2*sqrt(2))) (|000> + |001> + |010> - |011> + |100> + |101> + |110> - |111>)
Step 6: Measurement is performed on all qubits implicitly (due to --probs mode). The prompt specifies measurement probabilities: {|000>: 0.5, |001>: 0.5}. Wait, let me double check this. If I have 3 qubits and the amplitudes for |000>, |001>, |010>, |011>, |100>, |101>, |110>, |111> are all 1/(2*sqrt(2)), the probabilities should be 1/8 for each state.
Ah, wait. Let's re-read the predicted output: `Expected measurement probabilities: {|000>: 0.5, |001>: 0.5}`. But this contradicts my state calculation.
Wait, if q[0] is |+>, q[1] is |+>, the CNOT(q[1], q[2]) entangles q[1] and q[2].
Wait, CNOT(|+>|0>) = (|00> + |11>)/sqrt(2).
Then H(q[2]) acts on the second qubit of this Bell state.
Let's check: (I \otimes H) (1/sqrt(2) (|00> + |11>)).
|0>|+> + |1>|-> = (|00> + |01> + |10> - |11>)/2.
So q[1] and q[2] are in the state (|0+> + |1->)/sqrt(2).
Since q[0] is |+>, the total state is |+> \otimes (|0+> + |1->)/sqrt(2).
The amplitudes for all 8 states (|000>, |001>, |010>, |011>, |100>, |101>, |110>, |111>) are non-zero.
Wait, why does the prompt say `Expected measurement probabilities: {|000>: 0.5, |001>: 0.5}`? Let me check the code again.

Is it possible that `M(q[2])` only measures q[2], collapsing the state, and the question implies `--probs` records only the measured qubits?
Ah, `--probs` records the *measured* qubits. The implementation says `Number of qubits measured: 3` but then `Expected measurement probabilities: {|000>: 0.5, |001>: 0.5}`?
Wait! If only q[2] is measured, the probability of q[2]=0 is 0.5, q[2]=1 is 0.5. But it uses bitstrings like `|000>`.
Wait, in `--probs` mode, does it measure *all* qubits or only the ones with `M`? "Number of qubits measured: 3" implies all are measured. But if all are measured, probability of 000 is 1/8.
Let's re-read: Expected measurement probabilities: {|000>: 0.5, |001>: 0.5}.
How could the probabilities be 0.5 for 000 and 001, and 0 for the rest?
If q[1] and q[2] collapse to 00 or 01, then q[0] is still |+>, which means 000, 001, 100, 101 all have probability 1/8.
If The predicted output `{|000>: 0.5, |001>: 0.5}`, this means q[0

### Reference answer

{'predicted_probs': {'000': 0.5, '001': 0.5}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|000>) = 0.5000, P(|001>) = 0.5000.'}

## isqTrain/1226

- task_id: `isqTrain/1226`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4357`

### Prompt

Implement the following in isQ: implements a variant of the shor_subroutine pattern using w[2] -> w[4]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Implement a Shor subroutine for modular exponentiation 2^x mod 3 with an expanded 4-qubit work register (only 2 actively used).

**Qubits:** 5 total — x[0] (exponent) and w[0..3] (work register, 4 qubits). All 5 are measured.

**State evolution:**
1. Initial: |0⟩⊗|0000⟩ = |00000⟩
2. X(w[0]): |0⟩⊗|0001⟩ — initializes work to decimal 1
3. H(x[0]): (1/√2)(|0⟩+|1⟩)⊗|0001⟩ = (1/√2)(|00001⟩+|10001⟩)
4. ctrl swap (three-CNOT decomposition)(x[0], w[0], w[1]): swaps w[0]↔w[1] when x=1
   - x=0 branch: work stays |0001⟩ (decimal 1, i.e., 2^0 mod 3)
   - x=1 branch: work becomes |0010⟩ (decimal 2, i.e., 2^1 mod 3)
5. Final: (1/√2)(|01000⟩ + |10100⟩)

**Probabilities:** Equal superposition of two orthogonal states gives P(|01000⟩) = 0.5 and P(|10100⟩) = 0.5, matching predicted output. Qubits w[2], w[3] remain in |0⟩ throughout (unused workspace).

## isqTrain/3522

- task_id: `isqTrain/3522`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `multi_controlled_logic`, `reversible_computing`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `4562`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```
import std;

qbit q[3];

procedure main() {
    X(q[0]); X(q[1]);

    CNOT(q[2], q[1]);
    ctrl ctrl X(q[0], q[1], q[2]);
    CNOT(q[2], q[1]);

    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis

1. **Initial state:** |000⟩
2. **X(q[0]); X(q[1]):** Flip q[0] and q[1] → |110⟩
3. **CNOT(q[2], q[1]):** Control=q[2]=0, so no change → |110⟩
4. **ctrl ctrl X(q[0], q[1], q[2]):** Toffoli gate; both controls (q[0]=1, q[1]=1) are |1⟩, so flip target q[2] → |111⟩
5. **CNOT(q[2], q[1]):** Control=q[2]=1, so flip target q[1] → |101⟩

**Final state:** |101⟩ (deterministic)

**Predicted distribution:** |101⟩ with probability 1.

### Reference answer

{'predicted_probs': {'101': 1.0}, 'explanation': 'The output is |101> with probability 1.0'}

## isqTrain/4022

- task_id: `isqTrain/4022`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `2130`

### Prompt

There's an error in this quantum circuit implementation. Fix it:

```
import std;
// Inverse QFT on 3 qubits with input |111>
qbit q[3];

// Entry point
procedure main() {
    // Prepare input
    X(q[0]);
    X(q[1]);
    X(q[2]);

    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CZ(q[0], q[2]);
    H(q[2]);
    ctrl Rz(-2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    H(q[1]);
    ctrl Rz(-2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    ctrl Rz(-2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    H(q[0]);
    // Measure after inverse QFT
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **The bug**: The third line of the swap operation (three-CNOT decomposition) between `q[0]` and `q[2]` uses `CZ(q[0], q[2])` instead of `CNOT(q[0], q[2])`. A proper swap (three-CNOT decomposition) requires three CNOTs; substituting a CZ breaks the swap, leaving the qubits entangled incorrectly.

2. **The fix**: Replace `CZ(q[0], q[2])` with `CNOT(q[0], q[2])`, completing the standard swap (three-CNOT decomposition) decomposition: CNOT(q[0],q[2]) → CNOT(q[2],q[0]) → CNOT(q[0],q[2]).

3. **State evolution (corrected circuit)**:
   - Prepare |111⟩ via X gates
   - swap (three-CNOT decomposition)(q[0], q[2]): state remains |111⟩ (symmetric under swap)
   - H(q[2]), then controlled Rz gates and H(q[1]), H(q[0]) apply inverse QFT rotations
   - invQFT|111⟩ produces (1/√8)Σⱼ e

## isqTrain/2071

- task_id: `isqTrain/2071`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_inv`, `phase_manipulation`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `2750`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
procedure R(int k, qbit q) {
    double phase = 3.14159265358979 / 2 ** (k - 1);
    ctrl GPhase(phase, q);
} deriving gate
procedure qft_inv_3(qbit q[3]) {
    SWAP(q[0], q[2]);
    H(q[0]);
    ctrl inv R(2, q[0], q[1]);
    H(q[1]);
    ctrl inv R(3, q[0], q[2]);
    ctrl inv R(2, q[1], q[2]);
    H(q[2]);
} deriving gate
qbit anc[3];
qbit target[1];
procedure main() {
    X(target[0]);
    H(anc[0]); H(anc[1]); H(anc[2]);
    ctrl T(anc[0], target[0]);
    ctrl S(anc[1], target[0]);
    ctrl Z(anc[2], target[0]);
    qft_inv_3(anc);
    M(anc[0]); M(anc[1]); M(anc[2]);
}
```

### Chain-of-thought reasoning

Let me analyze this isQ program step by step.

The program implements quantum phase estimation (QPE) for a unitary that applies X to the target qubit.

Let me trace through:

1. Initial state: |anc[0], anc[1], anc[2]⟩ ⊗ |target[0]⟩ = |000⟩ ⊗ |0⟩

2. X(target[0]): |000⟩ ⊗ |1⟩

3. H on all ancilla: (1/√8)(|000⟩ + |001⟩ + |010⟩ + |011⟩ + |100⟩ + |101⟩ + |110⟩ + |111⟩) ⊗ |1⟩

4. ctrl T(anc[0], target[0]): This applies T to target when anc[0] is |1⟩
   T|1⟩ = e^(iπ/4)|1⟩
   So anc[0]=1 terms get phase e^(iπ/4)

5. ctrl S(anc[1], target[0]): S|1⟩ = i|1⟩ = e^(iπ/2)|1⟩
   So anc[1]=1 terms get phase e^(iπ/2)

6. ctrl Z(anc[2], target[0]): Z|1⟩ = -|1⟩ = e^(iπ)|1⟩
   So anc[2]=1 terms get phase e^(iπ)

After these controlled operations, the ancilla state picks up phases:
For basis state |anc[2], anc[1], anc[0]⟩ (note: anc[0] is bit 0, least significant for the phase), the total phase is:
phase = anc[0] × π/4 + anc[1] × π/2 + anc[2] × π

This is like the phase φ = π/4 encoded as φ = (1 × π/4) = π/4 in the phase, with the three ancilla qubits representing bits of φ/(2π) or something similar.

Wait, let me reconsider. The phase accumulation is:
- anc[0] contributes π/4 per unit
- anc[1] contributes π/2 per unit  
- anc[2] contributes π per unit

So the total phase for state |b2 b1 b0⟩ (where b0 = anc[0], b1 = anc[1], b2 = anc[2]) is:
φ = b0·π/4 + b1·π/2 + b2·π

This means φ = π/4 × (b0 + 2b1 + 4b2)

In terms of the binary representation, if we think of k = b2 b1 b0 as a 3-bit binary number (k = 4b2 + 2b1 + b0), then:
φ = π/4 × (4b2 + 2b1 + b0) = (π × k)/4

But for QPE, the phase is 2π × j/2^n where j is the integer representation.

The phase φ = π/4 corresponds to the eigenvalue e^(iπ/4) of T applied to |1⟩.

Actually, wait. The unitary being estimated is X (since X(target[0]) prepares |1⟩, then we apply controlled-T, controlled-S, controlled-Z). But actually, the program applies X to target first, then uses it as |1⟩, and the controlled gates are applied to the target.

Hmm, let me reconsider what "ctrl T(anc[0], target[0])" does. In isQ, this applies T gate to target[0] controlled by anc[0]. But T is a single-qubit gate, so when controlled, it becomes a controlled-T gate.

So the sequence is:
- Prepare target in |1⟩
- Apply controlled-T with anc[0] as control
- Apply controlled-S with anc[1] as control  
- Apply controlled-Z with anc[2] as control

Since T|1⟩ = e^(iπ/4)|1⟩, S|1⟩ = e^(iπ/2)|1⟩, Z|1⟩ = e^(iπ)|1⟩

These are all diagonal in the computational basis, so |1⟩ is an eigenvector. The phases accumulated are exactly as I described.

The ancilla state after phase kickback is:
(1/√8) Σ_{k=0}^{7} e^(i·φ_k) |k⟩

where φ_k = (π/4)·k for k expressed in binary as b2b1b0 = anc[2]anc[1]anc[0].

Wait, k = 4·b2 + 2·b1 + b0, so φ_k = (π/4)·

### Reference answer

{'predicted_probs': {'100': 1.0}, 'explanation': '3-bit QPE for T gate: phase=1/8, deterministic output.'}

## isqTrain/31

- task_id: `isqTrain/31`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `interference`, `isq_syntax_arrays`, `isq_syntax_oracle`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4229`

### Prompt

用isQ实现implements the oracle_boolean pattern using an alternative gate decomposition (CNOT -> H CZ H). The circuit must produce the same output as the standard decomposition.

### Chain-of-thought reasoning

## Reasoning

**Goal**: Implement the Bernstein-Vazirani algorithm to find hidden string s="1111" using CZ-based oracle decomposition (CNOT ≡ H-CZ-H).

**Qubits**: 5 total (q[0]-q[3] input, q[4] ancilla); measure q[0]-q[3].

**State evolution**:
1. Initial: |00000⟩
2. X(q[4]) then H on all: |+⟩|+⟩|+⟩|+⟩|−⟩ = ½² Σ_x |x⟩|−⟩
3. For each bit of s="1111", apply H(q[4])-CZ(q[i],q[4])-H(q[4]) ≡ CNOT(q[i],q[4])
4. Oracle phase kickback: ½² Σ_x (-1)^(x·1111) |x⟩|−⟩
5. H on q[0]-q[3]: |1111⟩|−⟩

**Expected probabilities**: Hadamard transform on phase-encoded state yields |1111⟩ with probability 1.0.

## isqQA/quantum_algorithms/91_comparison

- task_id: `isqQA/quantum_algorithms/91_comparison`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `comparison`, `algorithm`, `BV算法的不同隐藏字符串实现`
- source: `qa_pipeline`
- dataset_index: `4886`

### Prompt

请从计算复杂度、算法目标和底层量子傅里叶变换的联系等维度，深入对比分析Bernstein-Vazirani（BV）算法与经典暴力搜索、Deutsch-Jozsa（DJ）算法以及Simon算法的异同。此外，假设我们需要寻找的隐藏字符串为 a = 1011（长度为4），请提供一段完整的isQ语言代码来展示BV算法的具体量子线路实现，并简述其测量结果的意义。

### Reference answer

≲ Bernstein-Vazirani (BV) 算法是量子计算中展示量子并行性和查询复杂度优势的经典算法之一。为了深入理解它的价值，我们可以将其与经典算法及其他量子算法进行多维度对比：

1. **与经典暴力搜索的对比**： 
 在经典计算中，对于一个布尔函数 $f(x) = a \cdot x \pmod 2$（其中 $a$ 是隐藏的n比特字符串，$x$ 是输入），要确定未知字符串 $a$，我们需要进行 $n$ 次查询。例如，依次输入 $x = 1000, 0100, 0010, 0001$ 来分别提取 $a$ 的每一位。而BV算法利用量子叠加态和干涉效应，仅需对黑盒进行 **1次查询** 即可确定整个字符串 $a$，实现了从 $O(n)$ 到 $O(1)$ 的指数级查询加速。

2. **与Deutsch-Jozsa (DJ) 算法的对比**：
 BV算法实际上可以看作是DJ算法的一个特例或扩展应用。DJ算法的目标是判断一个函数是常数（对所有输入输出相同）还是平衡（对一半输入输出0，另一半输出1）；而BV算法面对的函数必定是平衡函数（除非 $a=0$），其目标不仅是识别出它是平衡的，而是要精确提取出这个平衡函数的具体结构参数（即隐藏字符串 $a$）。两者在量子线路上高度相似，都采用“Hadamard变换 -> 酉算子黑盒 -> Hadamard变换”的结构，本质都是利用Hadamard变换在计算基和傅里叶基（即X基和Z基）之间的转换来提取相位信息。

3. **与Simon算法的对比**：
 Simon算法解决的是寻找函数隐藏周期的问题，它通常被看作是Shor算法的前身。BV算法其实可以被广义地理解为Simon算法在阿贝尔群上的一个特殊形式，其中隐藏的子群仅包含字符串 $a$ 本身。Simon算法处理的是双射映射中的异或掩码，而BV算法处理的则是内积运算。

以下是为寻找隐藏字符串 $a = 1011$ （长度为4）编写的isQ量子程序代码实现：

```isQ
import std;

qbit q[5]; // 全局声明5个量子比特，前4个(q[0]-q[3])为输入寄存器，q[4]为输出比特

procedure main() {
    // 1. 初始化输入寄存器为叠加态
    for i in 0:4 {
        H(q[i]);
    }
    
    // 2. 初始化输出比特为 |-> 态，用于提取相位
    X(q[4]);
    H(q[4]);
    
    // 3. 实现黑盒函数 U_f 对应的酉变换
    // 隐藏字符串 a = 1011，对应 q[3]=1, q[2]=0, q[1]=1, q[0]=1
    // 当且仅当 a[i]=1 时，对对应的输入比特和输出比特执行 CNOT 门
    CNOT(q[0], q[4]);
    CNOT(q[1], q[4]);
    CNOT(q[3], q[4]);
    
    // 4. 再次对输入寄存器执行Hadamard变换（逆傅里叶变换）
    for i in 0:4 {
        H(q[i]);
    }
    
    // 5. 测量输入寄存器
    // 由于输出比特q[4]处于解缠结状态，仅需测量前4个比特即可获得结果
    for i in 0:4 {
        M(q[i]);
    }
}
```

**测量结果分析**：
在该isQ代码中，经过第一次Hadamard变换后，输入寄存器处于均匀叠加态。黑盒 $U_f$ 执行后，根据目标比特的 $|\rangle$ 态设定，隐藏字符串 $a$ 的信息被编码到输入寄存器的相对相位中（即 $(-1)^{a \cdot x}$）。最后一次Hadamard变换相当于对系统进行了一次量子傅里叶逆变换，将这些相位信息转换为了振幅信息。因此，在 `--probs` 模式下运行上述代码，对前四个量子比特进行测量的概率分布将 100% 塌缩到二进制字符串 `1011`（由于末尾比特 `q[4]` 的干扰消除，这一结果将确切反映出隐藏的字符串 $a$），这完美展示了BV算法仅用单次测量就能提取全局信息的绝佳特性。≁

## isqQA/quantum_algorithms/92_principle_advantage

- task_id: `isqQA/quantum_algorithms/92_principle_advantage`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `principle_advantage`, `algorithm`, `Simon算法原理`
- source: `qa_pipeline`
- dataset_index: `3232`

### Prompt

请深入解析Simon算法的宏观原理，并对比其在经典计算与量子计算环境下的时间复杂度。进一步阐述该算法实现指数级量子加速的根本物理与数学来源是什么？最后，请使用isQ语言编写一个针对2比特输入（n=2）、隐藏周期（秘密字符串）为s=11的Simon算法核心量子线路。

### Reference answer

Simon算法的宏观原理基于量子并行性和干涉效应，旨在解决黑盒寻隐问题：给定一个布尔函数 $f: \{0,1\}^n \to \{0,1\}^n$，承诺存在非零隐藏字符串 $s$ 使得 $f(x) = f(x \oplus s)$，目标是找到 $s$。其量子线路首先对输入寄存器应用Hadamard门制备所有可能输入的等幅叠加态，随后通过量子预言机 $U_f$ 计算函数值并将结果纠缠存入输出寄存器。此时，若测量输出寄存器，输入寄存器将坍缩为与输出结果对应的两个互补输入态的叠加态：$\frac{1}{\sqrt{2}}(|x\rangle + |x \oplus s\rangle)$。紧接着对输入寄存器再次应用Hadamard变换，由于量子干涉作用，最终测量得到的态 $|y\rangle$ 必定满足 $y \cdot s = 0 \pmod 2$。通过多次重复该线路收集足够的线性无关的 $y$ 向量，再借助经典高斯消元法即可解出秘密字符串 $s$。

在时间复杂度对比上，经典算法面临巨大的挑战。根据生日悖论，经典计算机必须进行 $\Omega(2^{n/2})$ 次查询才有可能找到一对碰撞 $f(x)=f(y)$ 进而推导出 $s$，其时间复杂度呈指数级。而Simon算法在量子设备上仅需执行 $O(n)$ 次量子查询，结合 $O(n^3)$ 的经典线性代数后处理，总时间复杂度骤降至多项式级别 $O(n^3)$，相对经典计算机实现了真正的指数级加速。

这种指数级量子加速的根本来源是**量子干涉（Quantum Interference）**与**相位信息的全局提取**。经典概率系统只能处理非负的概率叠加，而量子态不仅具有幅度还拥有相位。在Simon算法中，Hadamard变换不仅用于产生叠加，更关键的是它在计算隐藏周期时的作用：它将态矢空间中与隐藏字符串 $s$ 正交的向量聚拢相长干涉，而将非正交向量的概率幅通过相消干涉完全抵消为零。这种将隐藏的周期结构转化为可观测正交约束的能力，是经典随机算法无法企及的。

以下是使用isQ语言实现n=2且隐藏周期 $s=11$ 的Simon算法核心量子线路。在该设计中，预言机 $U_f$ 满足 $f(00)=f(11)=00$, $f(01)=f(10)=11$：

```isq
import std;

qbit q[4]; // q[0], q[1] 为输入寄存器，q[2], q[3] 为输出寄存器

procedure main() {
    // 1. 对输入寄存器施加 Hadamard 门，制备叠加态
    H(q[0]);
    H(q[1]);

    // 2. 构造特定的预言机 U_f
    // 此处函数设计使得当输入 x0 XOR x1 = 0 时输出 00，反之为 11
    // 满足 f(x) = f(x XOR 11)
    CNOT(q[0], q[2]);
    CNOT(q[1], q[2]);
    CNOT(q[0], q[3]);
    CNOT(q[1], q[3]);

    // 3. 测量输出寄存器，使输入寄存器坍缩为 |x> + |x XOR s> 的叠加
    int r2 = M(q[2]);
    int r3 = M(q[3]);

    // 4. 对输入寄存器再次施加 Hadamard 变换以引发量子干涉
    H(q[0]);
    H(q[1]);

    // 5. 测量输入寄存器，结果必定满足 y.s = 0 mod 2
    // 多次运行可测得 00 或 11，籍此解出 s = 11
    int y0 = M(q[0]);
    int y1 = M(q[1]);
}
```
