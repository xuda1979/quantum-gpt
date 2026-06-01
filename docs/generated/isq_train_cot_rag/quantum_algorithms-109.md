# ISQ training COT RAG corpus: quantum_algorithms shard 109

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/2865

- task_id: `isqTrain/2865`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `isq_syntax_multi_register`, `measurement_order`, `multi_controlled_logic`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1461`

### Prompt

The following isQ code has a bug. Find and fix it.

Buggy code:
```isq
import std;
qbit q[3];
// approximate W state preparation
procedure main() {
    X(q[0]);
    // H(q[0]); // BUG: missing Hadamard
    CNOT(q[0], q[1]);
    H(q[0]);
    CNOT(q[0], q[2]);
    CNOT(q[2], q[1]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
}

```

### Chain-of-thought reasoning

The buggy code has a commented-out Hadamard gate: `// H(q[0]);` right after the X(q[0]) gate. The bug hint says "A Hadamard gate was removed, breaking the superposition."

Let me trace through the corrected circuit:

1. Initial state: |000⟩
2. X(q[0]): |100⟩
3. H(q[0]): (|0⟩ + |1⟩)/√2 ⊗ |00⟩ = (|000⟩ + |100⟩)/√2
4. CNOT(q[0], q[1]): (|000⟩ + |110⟩)/√2
5. H(q[0]): (1/2)(|000⟩ + |100⟩ + |010⟩ - |110⟩)... wait let me redo this.

Actually let me be more careful. H on q[0] applied to (|000⟩ + |110⟩)/√2:

H|0⟩ = |+⟩, H|1⟩ = |-⟩

So applying H to q[0]:
(|+⟩|00⟩ + |-⟩|10⟩)/√2
= (1/2)(|000⟩ + |100⟩ + |010⟩ - |110⟩)

Wait, let me redo. The state after step 4 is (|000⟩ + |110⟩)/√2.

Applying H to q[0]:
H|0⟩⊗|00⟩ + H|1⟩⊗|10⟩ all over √2
= (|0⟩+|1⟩)/√2 ⊗ |00⟩ + (|0⟩-|1⟩)/√2 ⊗ |10⟩ all over √2
= (|000⟩ + |100⟩ + |010⟩ - |110⟩)/2

6. CNOT(q[0], q[2]): q[0] is control, q[2] is target
= (|000⟩ + |101⟩ + |010⟩ - |111⟩)/2

7. CNOT(q[2], q[1]): q[2] is control, q[1] is target
= (|000⟩ + |111⟩ + |011⟩ - |101⟩)/2... wait let me be more careful.

|000⟩: q[2]=0, so no flip on q[1] → |000⟩
|101⟩: q[2]=1, so flip q[1]: 0→1 → |111⟩
|010⟩: q[2]=0, so no flip → |010⟩
|111⟩: q[2]=1, so flip q[1]: 1→0 → |101⟩

So final state: (|000⟩ + |111⟩ + |010⟩ - |101⟩)/2... hmm that doesn't match the predicted output.

Wait, let me re-check. The resulting probabilities should be: {|000⟩: 0.25, |010⟩: 0.25, |101⟩: 0.25, |111⟩: 0.25}

So the final state should have equal amplitudes on |000⟩, |010⟩, |101⟩, |111⟩.

Let me redo step 7:
State before CNOT(q[2], q[1]): (|000⟩ + |101⟩ + |010⟩ - |111⟩)/2

CNOT(q[2], q[1]): control=q[2], target=q[1]
- |000⟩: q[2]=0 → |000⟩ ✓
- |101⟩: q[2]=1, flip q[1] (0→1) → |111⟩ 
- |010⟩: q[2]=0 → |010⟩ ✓
- |111⟩: q[2]=1, flip q[1] (1→0) → |101⟩

Final state: (|000⟩ + |111⟩ + |010⟩ - |101⟩)/2

Probabilities:
|000⟩: 0.25
|010⟩: 0.25
|101⟩: 0.25
|111⟩: 0.25

Yes! That matches. The phases don't matter for measurement probabilities.

Now the buggy circuit without the first H:

1. |000⟩
2. X(q[0]): |100⟩
3. (no H)
4. CNOT(q[0], q[1]): |110⟩
5. H(q[0]): (|010⟩ + |110⟩... wait no.

H on q[0] of |110⟩ = |1⟩|1⟩|0⟩
H|1⟩ = (|0⟩ - |1⟩)/√2
So state: (|010⟩ - |110⟩)/√2

6. CNOT(q[0], q[2]):

## isqTrain/2896

- task_id: `isqTrain/2896`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `measurement_order`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4370`

### Prompt

I need an isQ program to applies a Rx(pi/4) rotation to a single qubit and measures it.

Requirements:
- Declare `qbit q[1];` at global scope.
- Use `procedure main()` as entry point.
- Measure the qubit.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply an Rx(π/4) rotation to a single qubit initialized to |0⟩, then measure it.
2. **Qubits**: 1 qubit (`q[0]`) is declared and measured.
3. **State evolution**:
   - Initial state: |0⟩
   - After Rx(π/4): cos(π/8)|0⟩ − i·sin(π/8)|1⟩
4. **Probabilities**: P(|0⟩) = cos²(π/8) ≈ 0.8536, P(|1⟩) = sin²(π/8) ≈ 0.1464, matching the predicted output.

## isqTrain/845

- task_id: `isqTrain/845`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `finite_field_arithmetic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `120`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;
qbit q[6];

procedure main() {
    // Encode a = 1 in GF(3): binary 01
    X(q[0]);
    // Encode b = 2 in GF(3): binary 10
    X(q[3]);
    // GF(3) multiplication by 1 is identity
    // Copy b register to product register
    CNOT(q[2], q[4]);
    CNOT(q[3], q[5]);
    // Measure the product register
    M(q[4]);
    M(q[5]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations**: The circuit initializes 6 qubits, applies `X` gates to q[0] and q[3], and then applies `CNOT` gates with q[2] targeting q[4] and q[3] targeting q[5].
2. **State Evolution**: The initial state is $|000000\rangle$. After the `X` gates, the state becomes $|100100\rangle$.
3. **CNOTs**: The first `CNOT(q[2], q[4])` does nothing because q[2] is $|0\rangle$. The second `CNOT(q[3], q[5])` flips q[5] to $|1\rangle$ because q[3] is $|1\rangle$, resulting

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Parametric variant of isqEval/292. Dimension: predict probabilities for reference circuit.'}

## isqTrain/1360

- task_id: `isqTrain/1360`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `isq_syntax_oracle`
- source: `isq_train_cot`
- dataset_index: `4815`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;

oracle bool[1] xor_oracle(bool x[2]) {
    bool res[] = [x[0] != x[1]];
    return res;
}

qbit q[2];
qbit anc[2];

procedure main() {
    X(q[0]);
    xor_oracle(q, anc);
    M(q[0]); M(q[1]); M(anc[0]); M(anc[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis

1. **Operations applied:**
   - `X(q[0])`: Flips q[0] from |0⟩ to |1⟩
   - `xor_oracle(q, anc)`: Computes XOR (q[0] ≠ q[1]) into anc[0] via XOR; anc[1] is untouched
   - Four measurements: M(q[0]), M(q[1]), M(anc[0]), M(anc[1])

2. **State evolution:**
   - Initial: |0000⟩ (q[0], q[1], anc[0], anc[1])
   - After X(q[0]): |1000⟩
   - After xor_oracle: The oracle evaluates q[0]≠q[1]. Since q[0]=1, q[1]=0, the result is 1. This XORs anc[0] (was 0) with 1 → anc[0]=1. State becomes **|1010⟩**

3

### Reference answer

{'predicted_probs': {'10': 1.0}, 'explanation': 'Parametric variant of isqEval/500. Dimension: qubit_variant: anc[1] -> anc[2].'}

## isqTrain/785

- task_id: `isqTrain/785`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `finite_field_arithmetic`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `781`

### Prompt

Code this in isQ: implements a variant of the gf2_multiplication pattern using q[5] -> q[6]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: The circuit computes the product of polynomials a(x)=1+x and b(x)=1 in GF(2), storing the result in ancilla qubits using classical AND logic (Toffoli gates).
2. **Qubits**: 6 total (`q[0]` to `q[5]`). `q[3]`, `q[4]`, and `q[5]` are measured, with `q[3]` corresponding to the highest bit in the output bitstring.
3. **Initialization**: `X` gates set `q[0]=1`, `q[1]=1` (coefficients of a(x)), and `q[2]=1` (coefficient of b(x)), evolving the initial state from |000000> to |111000>.
4. **Multiplication**: `Toffoli(q[0], q[2], q[3])` computes p0 = a0*b0 = 1, flipping `q[3]` to yield |111100>.
5. **Multiplication**: `Toffoli(q[1], q[2], q[4])` computes p1 = a1*b0 = 1, flipping `q[4]` to yield the final state |111110>.
6. **Outcome**: The measured qubits `q[3]`, `q[4]`, and the untouched `q[5]` are in the state |110>. This strictly corresponds to the expected measurement probability of {|

## isqTrain/3651

- task_id: `isqTrain/3651`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `3118`

### Prompt

Help me write isQ code that the 4-qubit inverse QFT on input |1010>. Apply bit-reversal, then inverse controlled-Rz rotations and Hadamard gates in reverse order. Measure all qubits.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for the 4-qubit inverse QFT circuit on input |1010>.

Let me trace through this circuit:

1. Initialize |0000>
2. X(q[0]) and X(q[2]) prepare |1010> (in the q[3]q[2]q[1]q[0] ordering, this is q[0]=1, q[1]=0, q[2]=1, q[3]=0, so |0101> in standard notation where q[3] is MSB)

Wait, let me reconsider the bit ordering. The input is |1010>. In isQ, q[0] is typically the least significant bit.

So |1010> means q[3]=1, q[2]=0, q[1]=1, q[0]=0.

X(q[0]) flips q[0]: |0000> -> |0001>
X(q[2]) flips q[2]: |0001> -> |0101>

Hmm, that doesn't give |1010>. Let me reconsider.

Actually, Analyzing the circuit requirements more carefully:
- X(q[0]) flips q[0]
- X(q[2]) flips q[2]

So we get |q[3]q[2]q[1]q[0]> = |0101>

If we interpret this as the integer 5 in binary (q[3] is MSB), that's |0101>.

But the prompt says input |1010>. If q[0] is the LSB, then |1010> = 10 in decimal, which would require q[3]=1, q[2]=0, q[1]=1, q[0]=0. So we'd need X(q[1]) and X(q[3]).

There seems to be a mismatch, but I'll follow The implementation. The implementation prepares |0101> (or equivalently, depending on convention, this could be interpreted as |1010> with a different bit ordering).

Now the bit-reversal swaps:
- CNOT(q[0], q[3]); CNOT(q[3], q[0]); CNOT(q[0], q[3]) swaps q[0] and q[3]
- CNOT(q[1], q[2]); CNOT(q[2], q[1]); CNOT(q[1], q[2]) swaps q[1] and q[2]

So |0101> becomes |1010>.

Then inverse QFT is applied in reverse order starting from q[3]:

H(q[3]), then controlled Rz gates targeting q[3]...

Wait, let me re-read the code. After bit-reversal, we have |1010>.

Then:
- H(q[3])
- ctrl Rz(-2π/4, q[3], q[2]) — control q[3], target q[2]

Wait no, the syntax is `ctrl Rz(angle, q[3], q[2])` — I need to understand the isQ syntax for controlled gates.

Looking at the syntax: `ctrl @[c1, c2] Gate(target)` or `ctrl Gate(target)` with control qubit.

Actually in the code: `ctrl Rz(-2.0 * 3.14159265358979 / 4.0, q[3], q[2]);`

The Rz gate has parameters (angle, target). With `ctrl`, the preceding qubit(s) become controls. So this is controlled-Rz with control q[3] and target q[2]? Or is it Rz(angle, q[3]) controlled by q[2]?

Hmm, looking at the pattern more carefully and the inverse QFT structure:

Inverse QFT on 4 qubits works as follows:
1. Bit-reversal
2. For qubit i from n-1 down to 0:
   - Apply H to qubit i
   - For j from i-1 down to 0:
     - Apply controlled-Rz(-2π/2^(i-j+1)) with control q[j] and target q[i]

Wait, let me think about this differently. The standard QFT applies:
- H on qubit 0
- CR_k gates for increasing k
- Then move to qubit 1, etc.
- Finally bit-reverse

So inverse QFT is:
- Bit-reverse first
- Then for qubit n-1 down to 0:
  - Apply inverse CR_k gates
  - Apply H

Let me look at the code pattern:

After bit-reversal (state is |1010>):

H(q[3]);
ctrl Rz(-2π/4, q[3], q[2]);
H(q[2]);
ctrl Rz(-2

## isqTrain/4193

- task_id: `isqTrain/4193`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `616`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[3];

procedure main() {
    H(q[0]); H(q[1]); H(q[2]);
    CNOT(q[0], q[1]);
    Rz(2.0 * 0.785, q[1]);
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);
    Rz(2.0 * 0.785, q[2]);
    CNOT(q[0], q[2]);
    Rx(2.0 * 0.393, q[0]);
    Rx(2.0 * 0.393, q[1]);
    Rx(2.0 * 0.393, q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

We have 3 qubits q[0], q[1], q[2], all initialized to |000⟩.

Step 1: H(q[0]), H(q[1]), H(q[2])
After Hadamards on all three qubits:
State = |+⟩|+⟩|+⟩ = (1/2√2)(|000⟩ + |001⟩ + |010⟩ + |011⟩ + |100⟩ + |101⟩ + |110⟩ + |111⟩)

Step 2: CNOT(q[0], q[1])
This entangles q[0] and q[1]. In the computational basis:
|000⟩ → |000⟩
|001⟩ → |001⟩
|010⟩ → |010⟩
|011⟩ → |011⟩
|100⟩ → |110⟩
|101⟩ → |111⟩
|110⟩ → |100⟩
|111⟩ → |101⟩

State = (1/2√2)(|000⟩ + |001⟩ + |010⟩ + |011⟩ + |110⟩ + |111⟩ + |100⟩ + |101⟩)
= same superposition, just reordered

Step 3: Rz(2.0 * 0.785, q[1]) = Rz(π/2, q[1])
Rz(π/2) applies a phase of e^(iπ/4) to |0⟩ and e^(-iπ/4) to |1⟩ on q[1].

Let me denote this as Rz(π/2). When applied to q[1]:
- States where q[1]=|0⟩ get factor e^(iπ/4) = (1+i)/√2
- States where q[1]=|1⟩ get factor e^(-iπ/4) = (1-i)/√2

Step 4: CNOT(q[0], q[1]) - undoes the first CNOT

Step 5: CNOT(q[0], q[2])
Step 6: Rz(2.0 * 0.785, q[2]) = Rz(π/2, q[2])
Step 7: CNOT(q[0], q[2]) - undoes the CNOT

Step 8: Rx(2.0 * 0.393, q[0]) = Rx(π/4, q[0])
Step 9: Rx(2.0 * 0.393, q[1]) = Rx(π/4, q[1])
Step 10: Rx(2.0 * 0.393, q[2]) = Rx(π/4, q[2])

This is getting complex. Let me think more carefully about what's happening.

The pattern CNOT(c,t), Rz(θ,t), CNOT(c,t) is effectively applying a controlled-Rz, but only partially. Let me reconsider.

Actually, CNOT(c,t) · Rz(θ,t) · CNOT(c,t):
- When control=|0⟩: CNOT does nothing, Rz(θ,t) applies to target, CNOT does nothing. Net: Rz(θ) on target.
- When control=|1⟩: CNOT flips target, Rz(θ) applies, CNOT flips back. Net: Rz(-θ) on target.

So this is a conditional rotation. The overall effect on the two-qubit space is:
|0⟩⟨0| ⊗ Rz(θ) + |1⟩⟨1| ⊗ Rz(-θ)

Actually wait, I need to reconsider. When control=|1⟩ and target=|0⟩:
CNOT → |1,1⟩
Rz(θ) → e^(-iθ/2)|1,1⟩ (phase on |1⟩ of target)
CNOT → e^(-iθ/2)|1,0⟩

When control=|1⟩ and target=|1⟩:
CNOT → |1,0⟩
Rz(θ) → e^(iθ/2)|1,0⟩ (phase on |0⟩ of target)
CNOT → e^(iθ/2)|1,1⟩

So when control=|1⟩: the phases are swapped compared to control=|0⟩. This is indeed Rz(-θ).

So the circuit structure is:
1. Apply H to all qubits → |+++⟩
2. Apply conditional rotation on q[1] controlled by q[0]: if q[0]=0, Rz(π/2) on q[1]; if q[0]=1, Rz(-π/2) on q[1]
3. Apply conditional rotation on

### Reference answer

Uniform distribution across 8 states

## isqExpand/algo/118

- task_id: `isqExpand/algo/118`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `multi_controlled_logic`
- source: `isq_expansion`
- dataset_index: `3965`

### Prompt

实现以下量子计算任务（使用isQ）：implementing Grover's algorithm with a multi-target oracle that simultaneously marks two non-adjacent states |010> and |101> in a 3-qubit system (8-state space). Use exactly 1 Grover iteration. The oracle for |010> (q0=0,q1=1,q2=0): X(q[0]), X(q[2]), then H(q[2]), Toffoli(q[0],q[1],q[2]), H(q[2]) for 3-qubit CCZ, then X(q[0]), X(q[2]). The oracle for |101> (q0=1,q1=0,q2=1): X(q[1]), then H(q[2]), Toffoli(q[0],q[1],q[2]), H(q[2]), then X(q[1]). The diffusion operator: H all, X all, H(q[2]), Toffoli(q[0],q[1],q[2]), H(q[2]), X all, H all. Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Multi-target Grover on 3 qubits marking |010> (index 2) and |101> (index 5).

k=2 marked states, N=8. theta = arcsin(sqrt(2/8)) = pi/6.
With r=1: sin(3*pi/6) = 1. Perfect concentration after 1 iteration.

3-qubit CCZ via Toffoli: H(target), Toffoli(c1,c2,target), H(target).
This converts the X flip from Toffoli into a Z phase flip.

P(|010>) = P(|101>) = 0.5. All others = 0.
Expected: [0,0,0.5,0,0,0.5,0,0]

## isqTrain/896

- task_id: `isqTrain/896`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `boolean_logic`, `interference`, `isq_syntax_deriving_gate`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5005`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;
qbit q[2];

// Z gate wrapper for ctrl modifier
procedure my_z(qbit a) {
    Z(a);
} deriving gate

procedure main() {
    // Step 1: uniform superposition
    H(q[0]); H(q[1]);

    // Step 2: phase oracle marking |10>
    // |10> means q[0]=1, q[1]=0; negate q[1] to match ctrl
    X(q[1]);
    ctrl my_z(q[0], q[1]);
    X(q[1]);

    // Step 3: Grover diffusion operator
    H(q[0]); H(q[1]);
    X(q[0]); X(q[1]);
    // Conditional phase flip for |00> (after X -> |11>)
    ctrl my_z(q[0], q[1]);
    X(q[0]); X(q[1]);
    H(q[0]); H(q[1]);

    // Measure: |10> amplified to probability 1
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Task:** Analyze an isQ program implementing Grover's algorithm for 2 qubits.
    *   **Goal:** Predict the probability distribution of measurement outcomes and explain the reasoning.
    *   **Format:** Output ONLY the analysis starting with "## Circuit Analysis", ending with the predicted probability distribution. Concise (3-15 lines). Use Dirac notation. no code blocks.
    *   **Input program:**
        *   Step 1: `H(q[0]); H(q[1])` -> creates |+>|+> = 0.5(|00> + |01> + |10> + |11>)
        *   Step 2: Oracle for |10>. `X(q[1])`, `ctrl my_z(q[0], q[1])`, `X(q[1])`. Note that `ctrl my_z` applies CZ(q[0], q[1]). Wait, let's trace this carefully.
            *   State initially: `|10>` -> after X on q[1] becomes `|11>`.
            *   `ctrl my_z(q[0], q[1])` is a CZ gate. It applies -1 phase if both are 1. So `|11>` becomes `-|11>`.
            *   Then `X(q[1])` converts it back.
            *   Overall, it flips the phase of `|10>`.
        *   Step 3: Grover Diffusion.
            *   `H` on both.
            *   `X` on both.
            *   `ctrl my_z(q[0], q[1])` (CZ). This applies -1 phase to `|11>` (which was `|00>` before X gates).
            *   `X` on both.
            *   `H` on both.
            *   This performs the standard 2-qubit reflection about the mean.
        *   Step 4: Measure. Grover's algorithm with 1 iteration perfectly finds the target.

2.  **Step-by-Step State Evolution:**
    *   Initial: $|00\rangle$
    *   Step 1 (Hadamards): $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$
    *   Step 2 (Oracle on $|10\rangle$): $\frac{1}{2}(|00\rangle + |01\rangle - |10\rangle + |11\rangle)$
    *   Step 3 (Diffusion operator):
        *   Applies $H \otimes H$: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle - |11\rangle)$  [Wait, let's do the math: $H_2 Z_{00} H_2$ acting on $(|00\rangle+|01\rangle-|10\rangle+|11\rangle)/2$. Actually, the standard diffusion operator on $(a, b, -c, d)$ reflects around the mean. Mean of amplitudes: $(1+1-1+1)/4 = 1/2$. Reflection maps $x \to 2\mu - x$.
        *   Amplitude of $|00\rangle$: $2(1/2) - 1/2 = 1/2$.
        *   Amplitude of $|01\rangle$: $2(1/2) - 1/2 = 1/2$.
        *   Amplitude of $|10\rangle$: $2(1/2) - (-1/2) = 3/2$.
        *   Amplitude of $|11\rangle$: $2(1/2) - 1/2 = 1/2$.
        *   Let's trace the diffusion circuit exactly: $H \to X \to CZ \to X \to H$.
        *   Initial of Step 3: $|\psi\rangle = \frac{1}{2}|00\rangle + \frac{1}{2}|01\rangle - \frac{1}{2}|10\rangle + \frac{1}{2}|11\rangle$.
        *   After $H^{\otimes 2}$:
            *   $H^{\otimes 2}|00\rangle = \frac{1}{2}(|00\rangle+|01\rangle+|10\rangle+|11\rangle)$
            *   $H^{\otimes 2}|01\rangle = \frac{1}{2}(|00\rangle-|01\rangle+|10\rangle-|11\rangle)$
            *   $H^{\otimes 2}|10\r

### Reference answer

{'predicted_probs': {'2': 1.0}, 'explanation': 'Parametric variant of isqEval/258. Dimension: predict probabilities for reference circuit.'}

## isqTrain/2809

- task_id: `isqTrain/2809`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_procedures`, `measurement_order`
- source: `isq_train_cot`
- dataset_index: `1880`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[4];
procedure main() {
    X(q[0]); 
    H (q[0]);
    for i in 1:4 {

        CNOT (q[i-1], q[i]);
    }
    for i in 0:4{
        M(q[i]);
    }
}
```

### Chain-of-thought reasoning

1.  **Analyze the isQ code**:
    *   Initialization: `qbit q[4];` creates 4 qubits, all in $|0\rangle$. Initial state: $|0000\rangle$.
    *   `X(q[0])`: Flips qubit 0 to $|1\rangle$. State: $|1000\rangle$.
    *   `H(q[0])`: Applies Hadamard to qubit 0. State: $\frac{1}{\sqrt{2}}(|0000\rangle + |1000\rangle)$. Wait, the bit order. If q[0] is the most significant bit or least significant? Let's assume standard Dirac notation $|q_3 q_2 q_1 q_0\rangle$ or $|q_0 q_1 q_2 q_3\rangle$. Let's write $|q_0\rangle \otimes |q_1\rangle \otimes |q_2\rangle \otimes |q_3\rangle$. So $|1000\rangle$ means $q_0=1$. After H: $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes |0\rangle \otimes |0\rangle \otimes |0\rangle$.
    *   `for i in 1:4 { CNOT(q[i-1], q[i]) }`:
        *   i=1: `CNOT(q[0], q[1])`. Entangles $q_0$ and $q_1$. State: $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle) \otimes |00\rangle$.
        *   i=2: `CNOT(q[1], q[2])`. Entangles $q_1$ and $q_2$. State: $\frac{1}{\sqrt{2}}(|000\rangle + |111\rangle) \otimes |0\rangle$.
        *   i=3: `CNOT(q[2], q[3])`. Entangles $q_2$ and $q_3$. State: $\frac{1}{\sqrt{2}}(|0000\rangle + |1111\rangle)$.
        *   *Wait!* The loop `for i in 1:4` iterates i = 1, 2, 3. It does *not* include 4 in isQ.
        *   Let's double check isQ `for` loop semantics. Python-like ranges are `a:b` where `b` is exclusive. So i=1, 2, 3. Correct.
    *   Measurements: `for i in 0:4 { M(q[i]) }`. Measures all 4 qubits.

2.  **State Evolution**:
    *   Start: $|0000\rangle$
    *   `X(q[0])` -> $|1000\rangle$
    *   `H(q[0])` -> $\frac{1}{\sqrt{2}}(|0000\rangle + |1000\rangle)$
    *   `CNOT(q[0], q[1])` -> $\frac{1}{\sqrt{2}}(|0000\rangle + |1100\rangle)$
    *   `CNOT(q[1], q[2])` -> $\frac{1}{\sqrt{2}}(|0000\rangle + |1110\rangle)$
    *   `CNOT(q[2], q[3])` -> $\frac{1}{\sqrt{2}}(|0000\rangle + |1111\rangle)$
    *   Wait, is the bitstring order $q_0 q_1 q_2 q_3$? Usually, standard Dirac is $q_3 q_2 q_1 q_0$, so the state would be written as $\frac{1}{\sqrt{2}}(|0000\rangle + |1111\rangle)$ in either convention since all are 0 or all are 1. So this is safe.

3.  **Probabilities**:
    *   Measuring $\frac{1}{\sqrt{2}}(|0000\rangle + |1111\rangle)$.
    *   Probability of 0000 is $0.5$.
    *   Probability of 1111 is $0.5$.
    *   All other states have probability $0$.
    *   Number of qubits is 4. The array size is $2^4 = 16$.
    *   The JSON array needs to map 0000 (index 0) to 0.5, and 1111 (index

### Reference answer

{'predicted_probs': {'0000': 0.5000000000000001, '1111': 0.4999999999999999}, 'explanation': 'Probability distribution from quantum circuit simulation.'}
