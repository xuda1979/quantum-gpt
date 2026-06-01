# ISQ training COT RAG corpus: quantum_algorithms shard 108

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4599

- task_id: `isqTrain/4599`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `ancilla_usage`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3499`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;

qbit q[4];

procedure main() {
    
    X(q[3]);
    H(q[3]);
    
    H(q[0]);
    H(q[1]);
    H(q[2]);
    
    CNOT(q[0], q[3]);
    CNOT(q[2], q[3]);
    
    H(q[0]);
    H(q[1]);
    H(q[2]);
    
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the circuit:**
    -   4 qubits: q[0], q[1], q[2], q[3]. Initial state $|0000\rangle$.
    -   `X(q[3])`: $|0001\rangle$
    -   `H(q[3])`: $|000-\rangle$
    -   `H(q[0]), H(q[1]), H(q[2])`: $|++-\rangle_{0,1,2,3} = \frac{1}{\sqrt{8}}(|000\rangle + |001\rangle + \dots + |111\rangle)(|0\rangle - |1\rangle)$
    -   `CNOT(q[0], q[3])`: Flips q[3] when q[0] is 1. Since q[3] is in $|-\rangle$, a CNOT with q[0] as control and q[3] as target entangles them and applies a Z gate to the control (phase kickback). Wait, let's trace carefully:
        -   CNOT(c, t) where t is $|-\rangle$: $|0\rangle_c |-\rangle_t \to |0\rangle_c |-\rangle_t$
        -   $|1\rangle_c |-\rangle_t \to |1\rangle_c X|-\rangle_t = -|1\rangle_c |-\rangle_t$.
        -   So CNOT on $\frac{1}{\sqrt{2}}(|0\rangle+|1\rangle)(|-\rangle)$ yields $\frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) \otimes |-\rangle$.
        -   Wait, the state before CNOT is $\frac{1}{\sqrt{2}}(|0\rangle_0 + |1\rangle_0) \frac{1}{\sqrt{2}}(|0\rangle_2 + |1\rangle_2) |+\rangle_1 |-\rangle_3$.
        -   Apply CNOT(0, 3): $\frac{1}{\sqrt{2}}(|0\rangle_0 - |1\rangle_0) \frac{1}{\sqrt{2}}(|0\rangle_2 + |1\rangle_2) |+\rangle_1 |-\rangle_3$.
        -   This is equivalent to applying a Z gate to q[0].
    -   `CNOT(q[2], q[3])`: Same logic. Since q[3] is still $|-\rangle$ (it's an eigenstate of X), CNOT(2, 3) applies a Z gate to q[2].
        -   State after CNOT(2,3): $\frac{1}{\sqrt{2}}(|0\rangle_0 - |1\rangle_0) \frac{1}{\sqrt{2}}(|0\rangle_2 - |1\rangle_2) |+\rangle_1 |-\rangle_3$.
        -   This equals $|-\rangle_0 |-\rangle_2 |+\rangle_1 |-\rangle_3$. Wait, $\frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$ is not $|-\rangle$, it's $H Z |0\rangle$. $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$. Yes!
        -   Let's re-verify: $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$. $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
        -   So the state is $|-\rangle_0 |+\rangle_1 |-\rangle_2 |-\rangle_3$.
    -   `H(q[0])`: $HZ|0\rangle = X|0\rangle = |1\rangle_0$. (Wait: $|-\rangle = H|1\rangle$, so $H|-\rangle = |1\rangle$).
    -   `H(q[1])`: $H|+\rangle = |0\rangle_1$.
    -   `H(q[2])`: $H|-\rangle = |1\rangle_2$.
    -   State is now $|1\rangle_0 |0\rangle_1 |1\rangle_2 |-\rangle_3$.
    -   `H(q[0])`: $H|1\rangle = |-\rangle_0$.
    -   `Z(q[0])`: $Z|-\rangle = |+\rangle_0

### Reference answer

{'predicted_probs': {'0001': 1.0}, 'explanation': 'This isQ program operates on 4 qubit(s). The measurement probability distribution is: P(|0001>) = 1.0000.'}

## isqTrain/3442

- task_id: `isqTrain/3442`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `hamiltonian_simulation`
- source: `isq_train_cot`
- dataset_index: `1147`

### Prompt

Implement a quantum circuit in isQ: a single-layer QAOA circuit for MaxCut on a 2-node graph with one edge in isQ.

QAOA circuit:
1. Initialize: H on all qubits
2. Problem unitary (gamma layer): for each edge (i,j), apply    CNOT(i,j), Rz(gamma, j), CNOT(i,j)
3. Mixer unitary (beta layer): Rx(2*beta) on each qubit

Use gamma=pi/4, beta=pi/8.
Declare 2 qubits, measure both.

### Chain-of-thought reasoning

Let me trace through the QAOA circuit step by step.

1. **Initial state**: |00⟩

2. **After H on both qubits**: H|0⟩ ⊗ H|0⟩ = |+⟩|+⟩ = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2

3. **Problem unitary (gamma = π/4)**: Apply CNOT(0,1), Rz(π/4, 1), CNOT(0,1)
   - This implements exp(-iγZ₀Z₁/2) effectively (ZZ interaction)
   - The state |00⟩ gets phase e^{-iπ/4/2} = e^{-iπ/8}? Wait, let me think more carefully.
   
   Actually, CNOT-Rz-CNOT on the target qubit implements a controlled-Z rotation. Let me trace it:
   
   CNOT(0,1): |00⟩→|00⟩, |01⟩→|01⟩, |10⟩→|11⟩, |11⟩→|10⟩
   
   So after first CNOT:
   (|00⟩ + |01⟩ + |11⟩ + |10⟩)/2
   
   After Rz(π/4, q[1]):
   |00⟩ → |00⟩ (no phase, since |0⟩)
   |01⟩ → e^{-iπ/8}|01⟩
   |11⟩ → e^{-iπ/8}|11⟩... wait no. Rz(θ)|0⟩ = e^{-iθ/2}|0⟩, Rz(θ)|1⟩ = e^{iθ/2}|1⟩
   
   Actually Rz(θ) = [[e^{-iθ/2}, 0], [0, e^{iθ/2}]]
   
   So on qubit 1:
   |00⟩ → e^{-iπ/8}|00⟩
   |01⟩ → e^{iπ/8}|01⟩
   |11⟩ → e^{iπ/8}|11⟩
   |10⟩ → e^{-iπ/8}|10⟩
   
   After second CNOT:
   |00⟩ → e^{-iπ/8}|00⟩
   |01⟩ → e^{iπ/8}|01⟩
   |10⟩ → e^{iπ/8}|10⟩ (|11⟩→|10⟩)
   |11⟩ → e^{-iπ/8}|11⟩ (|10⟩→|11⟩)
   
   So the state after problem unitary:
   e^{-iπ/8}(|00⟩ + |11⟩)/2 + e^{iπ/8}(|01⟩ + |10⟩)/2

4. **Mixer unitary (Rx(2β) = Rx(π/4))**:
   Rx(θ) = [[cos(θ/2), -i·sin(θ/2)], [-i·sin(θ/2), cos(θ/2)]]
   Rx(π/4): cos(π/8) ≈ 0.9239, sin(π/8) ≈ 0.3827
   
   Applying to each qubit independently. The final state will be a superposition of all four basis states.

The resulting probabilities should be {|00⟩: 0.426777, |01⟩: 0.073223, |10⟩: 0.073223, |11⟩: 0.426777}.

Let me verify: The symmetric structure means |00⟩ and |11⟩ have equal probability, and |01⟩ and |10⟩ have equal probability.

Let me compute more carefully. After the problem unitary, the state is:
|ψ⟩ = e^{-iπ/8}(|00⟩ + |11⟩)/2 + e^{iπ/8}(|01⟩ + |10⟩)/2

This can be written as:
|ψ⟩ = cos(π/8)(|00⟩ + |01⟩ + |10⟩ + |11⟩)/2 - i·sin(π/8)(|00⟩ - |01⟩ - |10⟩ + |11⟩)/2

Now applying Rx(π/4) to each qubit. Since both qubits get the same gate:

Actually, let me think of it differently. The initial state was |++⟩. The problem unitary applies exp(-iγZZ/2) which gives:
exp(-iπ/4·ZZ/2)|++⟩ = cos(π/8)|++⟩ + i·sin(π/8)|--⟩

Wait, that's not quite right either. Let me be more careful.

ZZ|++⟩ = ZZ(|00⟩+|01⟩+|10⟩+

## isqTrain/1192

- task_id: `isqTrain/1192`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_classical_vars`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_inv`, `isq_syntax_multi_register`, `phase_manipulation`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `2476`

### Prompt

Write isQ code for the following quantum task: implements a variant of the phase_estimation pattern using target[1] -> target[3]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

Looking at this task, I need to write a reasoning section for a phase estimation circuit that:
1. Uses target[1] through target[3] instead of just target[0]
2. Has an expanded qubit register with additional qubits left in ground state

Wait, let me re-read the prompt. It says "implements a variant of the phase estimation pattern using target[1] -> target[3]". This means the controlled operations should be applied to target[1], target[2], and target[3] instead of just target[0].

The circuit should:
- anc[3] for phase readout
- target[3] for target qubits
- Only uses target[0]

For the variant, I need to:
1. Use target[1], target[2], target[3] for the controlled operations
2. Have additional qubits that remain in |0⟩ state

Let me trace through the circuit:

1. X(target[1]) - prepares target[1] in |1⟩
2. H(anc[0]), H(anc[1]), H(anc[2]) - creates superposition on ancilla
3. ctrl T(anc[0], target[1]) - controlled-T on target[1]
4. ctrl S(anc[1], target[1]) - controlled-S on target[1]
5. ctrl Z(anc[2], target[1]) - controlled-Z on target[1]
6. qft_inv_3(anc) - inverse QFT on ancilla
7. Measurements on anc[0], anc[1], anc[2]

The T gate has eigenvalues 1 and e^(iπ/4). The |1⟩ state is an eigenstate with eigenvalue e^(iπ/4).

For phase estimation with 3 qubits estimating the phase θ = π/4:
- After controlled-T^(2^k) operations, the ancilla state encodes the phase
- The inverse QFT extracts the phase bits

The phase π/4 in binary (with 3 bits) is:
π/4 = 0.001 in binary (i.e., 1/8)

So the measurement should give |100⟩ = 4 in decimal, which corresponds to binary 100.

Wait, let me reconsider. The phase θ satisfies e^(2πiθ) = e^(iπ/4), so θ = 1/8 = 0.001 in binary.

In 3-bit representation: θ = 0.001₂

After inverse QFT, the result should be the binary representation of θ: 001 in reverse order, which would be 100.

Actually, I need to be more careful about the bit ordering. The predicted output |100⟩ = probability 1.0, which means anc[0]=1, anc[1]=0, anc[2]=0.

So the measurement bitstring is 100, which in decimal is 4. But wait, the problem says "earlier measured qubit = higher bit", so anc[0] is the highest bit, anc[2] is the lowest bit.

So |100⟩ means anc[0]=1, anc[1]=0, anc[2]=0.

For the variant using target[1] instead of target[0], the logic is the same - we're just applying the gates to a different qubit index. The additional qubits (target[0], target[2], target[3] if they're not used, or just leaving them in |0⟩) don't affect the computation.

Let me write the reasoning:

## Reasoning

1. **Goal**: Implement phase estimation of the T gate using target[1] as the eigenstate qubit with an expanded register.

2. **Qubits and measurements**: Uses anc[3] for phase readout (measured), target[4] register where target[1] holds the eigenstate, others stay in |0⟩.

3. **State evolution**:
   - Initialize: target[1] prepared as |1⟩ (eigenstate of T with eigenvalue e^(iπ/4))
   - After H on ancilla: |+⟩|+⟩|+⟩ ⊗ |1⟩
   - After controlled-T^(2^k): Phase θ=1/8 encoded in ancilla as |ψ⟩ = (|0⟩ + e^(iπ/4)|1⟩)(|0⟩ + e^(iπ/2)|1⟩)(|0⟩ + e^(iπ)|1⟩)/2√2 ⊗ |1⟩
   - After inverse QFT: Extracts phase bits → ancilla in |100⟩

4. **Expected result**: Phase θ = 1/8 = 0.001₂, inverse QFT gives |100⟩ with probability 1.0.

Hmm, let me reconsider the state

## isqTrain/816

- task_id: `isqTrain/816`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `multi_controlled_logic`, `reversible_computing`, `superposition`
- source: `isq_train_cot`
- dataset_index: `737`

### Prompt

请用isQ语言编写一个量子电路：implements a variant of the quadratic_form pattern using q[3] -> q[4]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

We are given a circuit implementation for an isQ program implementing a "variant of the quadratic_form pattern using q[3] -> q[4]". The circuit should q[4] global array of 4 qubits. It then applies H on q[0] and q[1], then Toffoli on q[0], q[1], q[2], then measures q[2] and q[3]. Expected measurement probabilities: {|00>: 0.75, |10>: 0.25}. So the measured qubits are q[2] and q[3]. But the reference only has 4 qubits, and q[3] is not used in any operation; it's just measured. Since q[3] is initially |0>, it will remain |0> unless acted upon. So the measurement outcomes: q[2] is the result of AND of q[0] and q[1] (post-Toffoli, but note Toffoli flips target when both controls are 1, so if both are 1, q[2] becomes 1; else remains 0). But after Toffoli, we measure q[2] and q[3]. q[3] is always 0. So we would expect probabilities: For the two measured bits, q[2] as higher bit? The output says {|00>: 0.75, |10>: 0.25}. So that means the outcome 00 has probability 0.75, 10 has probability 0.25. That means the higher bit is q[2]? Or earlier measured qubit = higher bit. According to --probs output: array indexed by measurement bitstring (earlier measured qubit = higher bit). So if we measure q[2] first then q[3], then the bitstring would be (q[2] q[3]), with q[2] as higher bit. So outcome 00 means q[2]=0, q[3]=0; outcome 10 means q[2]=1, q[3]=0. That matches: q[2] can be 1 only when both q[0] and q[1] are 1. The probability that both are 1 is 0.25 (since each is in uniform superposition). So probability of q[2]=1 is 0.25, thus outcome 10 = 0.25, and outcome 00 = 0.75 (when q[2]=0). So that's consistent.

Now we are asked to generate a reasoning section for this code. The reasoning should explain:

1. Goal of the circuit: Implement a variant of quadratic form pattern using q[3] -> q[4] (maybe meaning that the expanded register uses q[3] and q[4]? Actually "using q[3] -> q[4]" might indicate that the circuit should use qubits q[3] and q[4] as measured? Or it might be a misinterpretation; The circuit should q[2] and q[3] measured, but it says "using q[3] -> q[4]" meaning that the pattern originally used q[0], q[1], q[2] but now we extend to q[3] and q[4]? Actually The circuit should q[3] measured but not used. Possibly the task is to write a variant that uses more qubits, but The implementation is exactly that: uses 4 qubits and measures q[2] and q[3]. The description: "Write an isQ program that implements a variant of the quadratic_form pattern using q[3] -> q[4]." So perhaps the variant uses q[3] and q[4] as the output qubits? But the reference uses q[2] and q[3]. Maybe it's a mistake. The reference measures q[2] and q[3]; perhaps the intended measurement was q[2] and q[3] but they wrote q[3] -> q[4] meaning q[3] and q[4]? Could be ambiguous. But we have to produce reasoning for the given circuit implementation. The expected measurement probabilities match the reference, so we'll base reasoning on that.

Goal: The circuit implements a quadratic form evaluation: f(x0,x1) = x0 AND x1. It uses two input qubits in superposition, computes the AND via a Toffoli onto a target qubit, and measures the target and an unused qubit.

Now we need to produce step-by-step state evolution.

- Initially: |0>^4 (4 qubits all zero). After H on q[0] and q[1] (assuming H applied sequentially): state = 1/2 (|00> + |01> + |10> + |11>) ⊗ |00>_{q2,q3

## isqTrain/4005

- task_id: `isqTrain/4005`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `809`

### Prompt

This isQ program compiles but produces incorrect probabilities. Find and correct the mistake.

```
import std;
// QPE with 3-bit precision for phase 2*pi/4
qbit q[4];

procedure main() {
    // Prepare eigenstate |1>
    X(q[3]);
    // Hadamard on precision qubits
    H(q[0]); H(q[1]); H(q[2]);
    // Controlled-U^(2^k) for each precision qubit
    ctrl Rz(2.0 * 3.14159265358979 * 2.0 / 8.0 * 1.0, q[0], q[3]);
    ctrl Rz(2.0 * 3.14159265358979 * 2.0 / 8.0 * 2.0, q[1], q[3]);
    ctrl Rz(2.0 * 3.14159265358979 * 2.0 / 8.0 * 4.0, q[2], q[3]);
    // Inverse QFT on 3 precision qubits
    // Swap q[0] <-> q[2]
    CNOT(q[0], q[2]);
    CNOT(q[0], q[2]);
    CNOT(q[0], q[2]);
    // iQFT stages
    H(q[0]);
    ctrl Rz(-3.14159265358979 / 2.0, q[1], q[0]);
    ctrl Rz(-3.14159265358979 / 4.0, q[2], q[0]);
    H(q[1]);
    ctrl Rz(-3.14159265358979 / 2.0, q[2], q[1]);
    H(q[2]);
    // Measure all
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

``` (bug type: swapped qubits)

### Chain-of-thought reasoning

Let me analyze this quantum phase estimation (QPE) circuit and identify the bug.

The circuit is performing QPE with 3-bit precision for phase 2π/4 = π/2.

First, let me understand the structure:
- q[0], q[1], q[2] are the precision/estimation qubits
- q[3] is the eigenstate qubit (prepared in |1⟩)

After Hadamard gates on precision qubits, we apply controlled-Rz rotations.

The bug is in the swap operation (three-CNOT decomposition) between q[0] and q[2].

A swap operation (three-CNOT decomposition) is implemented as:
CNOT(a, b)
CNOT(b, a) 
CNOT(a, b)

The buggy code has:
CNOT(q[0], q[2])
CNOT(q[0], q[2])  ← This is wrong! Should be CNOT(q[2], q[0])
CNOT(q[0], q[2])

So the second CNOT has swapped control and target. It should be CNOT(q[2], q[0]) instead of CNOT(q[0], q[2]).

Let me verify this is indeed the bug:
- The original code does: CNOT(0,2) → CNOT(0,2) → CNOT(0,2)
  - First CNOT(0,2): XOR target with control
  - Second CNOT(0,2): XOR target with control again (undoes first for target)
  - Third CNOT(0,2): XOR target with control again
  This would NOT perform a swap (three-CNOT decomposition).

- The fixed code does: CNOT(0,2) → CNOT(2,0) → CNOT(0,2)
  This is the standard swap (three-CNOT decomposition) decomposition.

The fix: Change the second CNOT from `CNOT(q[0], q[2])` to `CNOT(q[2], q[0])`.

Now let me verify the circuit correctness:

1. Initial state: |0000⟩
2. After X(q[3]): |0001⟩
3. After H on q[0], q[1], q[2]: (|0⟩+|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2 ⊗ |1⟩
   = 1/2√2 Σ_{k=0}^{7} |k⟩|1⟩

4. Controlled Rz rotations:
   - The phase being estimated is φ = 2/8 = 1/4 (in units of 2π)
   - So the eigenvalue is e^(2πi·1/4) = e^(iπ/2) = i
   
   Wait, let me reconsider. The phase is 2π·2/8 = 2π·1/4 = π/2.
   
   Rz(θ)|1⟩ = e^(-iθ/2)|0⟩... no wait, Rz acts on the computational basis differently.

Actually, Rz(θ) = e^(-iθ/2)|0⟩⟨0| + e^(iθ/2)|1⟩⟨1|

So controlled-Rz(θ) on |1⟩ gives e^(iθ/2)|1⟩.

The controlled rotations accumulate phase on the precision qubits:
- ctrl Rz(2π·2/8·1, q[0], q[3]): adds phase 2π·2/8·1 = π/2 to q[0] when q[3]=|1⟩
- ctrl Rz(2π·2/8·2, q[1], q[3]): adds phase 2π·2/8·2 = π to q[1]
- ctrl Rz(2π·2/8·4, q[2], q[3]): adds phase 2π·2/8·4 = 2π to q[2]

Wait, but this is applying Rz to the target qubit, not the control. Let me re-examine.

In isQ, `ctrl Rz(theta, q[0], q[3])` means q[0] is the control and q[3] is the target for Rz. But wait, that doesn't make sense for QPE...

Actually, in QPE, the controlled operations apply U^2^k to the eigenstate, controlled by the precision qubits. But here we're applying Rz to q[3] (the eigenstate qubit).

Hmm, let me think about this differently. The Rz gate applies a phase to the |1⟩ state. Since q[3] is in |1⟩, applying Rz(θ) to q[3] gives:

Rz(

## isqQA/quantum_algorithms/110_math_derivation

- task_id: `isqQA/quantum_algorithms/110_math_derivation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `math_derivation`, `algorithm`, `QPE用于不同酉算子`
- source: `qa_pipeline`
- dataset_index: `1757`

### Prompt

请严密推导量子相位估计（QPE）算法中，当第二寄存器输入为酉算子U的多个特征态叠加时的完整量子态演化过程。假设目标酉算子U及其对应的特征子空间满足 U|ψ_j⟩ = e^(i2πφ_j)|ψ_j⟩，且输入的第二寄存器处于叠加态 |Ψ⟩ = Σ_j α_j |ψ_j⟩。请给出从初态制备、Hadamard变换、受控 U^(2^k) 操作，到逆量子傅里叶变换（IQFT）的每一步数学演化，并证明为何第一寄存器最终能以极高的概率将相位 φ_j 转移到计算基态的振幅上。

### Reference answer

<think>
推理过程主要基于量子态的线性叠加原理，将叠加态输入分解为多个单特征态的独立演化后再进行线性组合：

1. **初态展开与并行叠加**：首先将第二寄存器的叠加输入态按酉算子U的特征基展开，第一寄存器经过Hadamard门后形成所有计算基的均匀叠加态，两者构成直积。
2. **受控演化与相位踢回**：执行受控 $U^{2^k}$ 操作时，由于算子的线性性质，其作用等价于分别作用于各个特征态 $|\psi_j\rangle$。根据特征方程，第二寄存器保持不变，但会将特征值中的相位因子 $e^{i2\pi\phi_j}$ 作为控制条件累积，“踢回”并编码到第一寄存器的对应基矢振幅上。
3. **逆傅里叶变换与干涉放大**：此时第一寄存器纠缠了多个相位编码态。对其整体施加逆量子傅里叶变换（IQFT），利用量子干涉效应，将隐藏在振幅相对相位中的目标相位 $\phi_j$ 精确转换并映射为计算基态的概率幅分布。
4. **测量坍缩提取结果**：最后对第一寄存器进行测量，整个量子态会以 $|\alpha_j|^2$ 的概率随机坍缩到某个特定特征态对应的相位估计值上，从而以极高概率在计算基中读出相位。
</think>

量子相位估计（QPE）是量子计算中极其重要的基础算法，其核心在于利用量子并行性和干涉效应，将存储在酉算子特征值中的相位信息转换为可以通过计算基测量的概率幅。下面为您严密推导当输入态为叠加态时，QPE算法中每一步的量子态演化过程。假设第一寄存器（评估寄存器）包含 t 个量子比特，初始处于 |0⟩^(⊗t)，第二寄存器处于目标特征态的叠加态 |Ψ⟩ = Σ_j α_j |ψ_j⟩。系统的初始状态为：|Φ_0⟩ = |0⟩^(⊗t) ⊗ |Ψ⟩ = Σ_j α_j |0⟩^(⊗t) |ψ_j⟩。第一步，对第一寄存器的所有量子比特施加阿达马门。这一步的作用是创建均匀叠加态。演化后的状态为：|Φ_1⟩ = (H^(⊗t) ⊗ I) |Φ_0⟩ = 1/2^(t/2) Σ_(k=0)^(2^t-1) |k⟩ ⊗ Σ_j α_j |ψ_j⟩ = Σ_j α_j (1/2^(t/2) Σ_k |k⟩ |ψ_j⟩)。这里 k 表示从 0 到 2^t-1 的整数。第二步，依次施加受控酉门操作。具体而言，对于第一寄存器中的第 m 个量子比特，我们以其为控制位，对第二寄存器施加受控 U^(2^(t-1-m)) 门。由于操作是线性的，我们针对叠加态中的某一个分量 |k⟩ |ψ_j⟩ 进行分析。将 k 展开为二进制形式 k = k_(t-1)2^(t-1) + ... + k_0 2^0。因为受控操作只有当对应控制位为 |1⟩ 时才执行 U 的幂次，所以该操作等价于直接对 |ψ_j⟩ 施加 U^k 操作：U^k |ψ_j⟩ = (e^(i2πφ_j))^k |ψ_j⟩ = e^(i2πφ_j k) |ψ_j⟩。将这一结果代回叠加态中，演化后的状态为：|Φ_2⟩ = Σ_j α_j [ 1/2^(t/2) Σ_(k=0)^(2^t-1) e^(i2πφ_j k) |k⟩ ] ⊗ |ψ_j⟩。这一步是QPE的核心，它成功地将特征值的相位信息 e^(i2πφ_j k) 编码到了第一寄存器的计算基态振幅中。我们可以将方括号内的直积态按量子位展开。利用 e^(i2πφ_j k) = Π_(l=0)^(t-1) e^(i2πφ_j k_l 2^l)，第一寄存器的态可以重写为张量积形式：1/2^(t/2) Σ_k e^(i2πφ_j k) |k⟩ = ⊗_(l=0)^(t-1) 1/√2 (|0⟩ + e^(i2πφ_j 2^l) |1⟩)。第三步，对第一寄存器施加逆量子傅里叶变换。我们观察方括号内的张量积态，这恰好是标准量子傅里叶变换 QFT|2^t φ_j⟩ 的定义。因为 QFT|x⟩ = 1/2^(t/2) Σ_(k=0)^(2^t-1) e^(i2πxk/2^t) |k⟩。令 x = 2^t φ_j，则有 e^(i2πxk/2^t) = e^(i2πφ_j k)。因此，如果 2^t φ_j 恰好为整数，那么 IQFT 作用后，第一寄存器将完美坍缩到基态 |2^t φ_j⟩ 上。如果 2^t φ_j 不是整数，假设其最接近的整数为 a，根据 IQFT 的性质，测量结果将以至少 4/π² ≈ 0.405 的概率落在 a 上，若增加量子比特数 t，则可以指数级逼近真实相位。由于整个演化过程保持了两个寄存器之间的纠缠线性无关性，经过 IQFT 后的系统状态演化为：|Φ_3⟩ ≈ Σ_j α_j |2^t φ_j⟩ ⊗ |ψ_j⟩。至此严密证明了 QPE 能够将叠加态中各个特征态对应的相位 φ_j 独立地转移到第一寄存器中。作为补充，下面提供展示该受控相位转移结构的基础 isQ 语言代码片段：
import std;
qbit q[3];
qbit target[1];
procedure main() {
  // 初始化目标态为|1>
  X(target[0]);
  // 制备均匀叠加态
  for i in 0:3 { H(q[i]); }
  // 受控U操作，此处 U 为相位 e^(i2πθ)
  // q[0]对应2^2次幂，q[1]对应2^1次幂，q[2]对应2^0次幂
  for i in 0:4 { ctrl @[q[0]] Rz(2*pi*theta, target[0]); }
  for i in 0:2 { ctrl @[q[1]] Rz(2*pi*theta, target[0]); }
  ctrl @[q[2]] Rz(2*pi*theta, target[0]);
  // 此处后续应接入逆量子傅里叶变换 IQFT
}

## isqQA/quantum_algorithms/109_hardware_limitations

- task_id: `isqQA/quantum_algorithms/109_hardware_limitations`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `hardware_limitations`, `algorithm`, `QPE的精度与量子比特数`
- source: `qa_pipeline`
- dataset_index: `4578`

### Prompt

在NISQ（含噪声中等规模量子）设备的硬件局限下，量子相位估计（QPE）的理论精度与评估量子比特数量之间的正比关系是如何被打破的？请详细分析退相干时间（T1, T2）和双量子比特门误差对电路深度的累积影响，并结合isQ语言给出一个针对硬件限制优化过的浅层简化QPE代码示例。

### Reference answer

在理想的量子计算模型中，量子相位估计（QPE）的精度随着评估量子比特数量的增加而呈指数级提升。具体而言，使用$n$个评估量子比特可以将相位估计到$n$位的精度（误差正比于$2^{-n}$）。然而，在NISQ（含噪声中等规模量子）设备的物理硬件局限下，这种理论关系被严苛的退相干效应和门误差彻底打破。

首先，退相干时间是限制QPE电路规模的核心因素。量子比特的相干时间（通常用纵向弛豫时间$T_1$和横向退相干时间$T_2$表示）是极其有限的。在QPE算法中，最高位（第$n-1$位）的评估量子比特需要执行受控酉算符$C-U^{2^{n-1}}$。这意味着如果我们要获得$n$位的高精度，电路的深度将随着量子比特数呈指数级增长。当电路的总执行时间逼近或超过系统的$T_1$和$T_2$时，量子态的能量弛豫和相位信息丢失将导致计算结果完全被随机噪声淹没。此时，继续增加评估量子比特数量不仅无法提升精度，反而会因为电路运行时间的延长导致退相干概率急剧上升，使得最终测量结果的保真度呈断崖式下跌。

其次，NISQ设备上双量子比特门（如CNOT或CZ）的保真度通常远低于单比特门（目前顶尖硬件约为99.0%至99.9%）。QPE算法需要构建大量的受控酉操作，这涉及频繁的纠缠门。一个深度为$d$的电路，其整体成功率会随着门误差$\epsilon$按 $(1-\epsilon)^d$ 衰减。在指数级加深的QPE电路中，累积的门误差将轻易超过算法所能带来的理论精度增益。因此，在NISQ时代，我们必须在精度和电路深度之间做出妥协，通常采用截断的浅层QPE（如仅使用1到2个评估比特）或使用变分量子算法（如VQE）作为替代。

以下是在isQ语言框架下，针对硬件局限性优化的浅层QPE代码示例。该代码严格限制了评估比特数为2，以控制纠缠门的数量和电路深度，从而在退相干和门误差允许的范围内提取有效相位：

```isq
import std;

// 声明2个评估量子比特和1个目标量子比特
qbit eval[2];
qbit target[1];

procedure main() {
    // 1. 初始化目标态，假设我们将|1>态作为酉算符U的本征态
    X(target[0]);
    
    // 2. 为评估量子比特创建叠加态
    H(eval[0]);
    H(eval[1]);
    
    // 3. 受控酉操作 (浅层截断，适应NISQ设备深度)
    // 假设本征相位为pi/4 (对应T门)
    // 为了减少双量子比特门，我们限制最高受控幂次
    ctrl @[eval[1]] T(target[0]); // 执行 U^1
    ctrl @[eval[0]] S(target[0]); // 执行 U^2
    
    // 4. 逆量子傅里叶变换 (仅针对2比特系统进行轻量化处理)
    H(eval[1]);
    
    // 施加逆向的受控相位旋转 R(-pi/4)
    inv T(eval[0]);
    ctrl @[eval[1]] T(eval[0]);
    
    H(eval[0]);
    
    // 5. 测量评估寄存器
    // 在实际硬件中，这里将读出相位的二进制估计
    M(eval[0]);
    M(eval[1]);
}
```

## isqQA/quantum_algorithms/48_isq_implementation

- task_id: `isqQA/quantum_algorithms/48_isq_implementation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_implementation`, `algorithm`, `量子振幅放大`
- source: `qa_pipeline`
- dataset_index: `3654`

### Prompt

请提供一段完整的isQ量子程序代码，演示如何在一个2比特系统中实现对目标态|11⟩的量子振幅放大。要求代码带有详细的逐行注释，并解释Oracle和扩散算子在代码中的具体实现逻辑。

### Reference answer

<think>
首先，明确振幅放大算法的三个核心步骤：初始化均匀叠加态、构建Oracle（相位翻转）和构建扩散算子。对于2比特系统目标态|11⟩，Oracle可以直接使用受控Z门（CZ门）实现，因为CZ门在输入全为|1⟩时引入π相位，等效于将目标态的概率幅乘以-1。其次，扩散算子的数学本质是对均值进行反射，其标准电路转换方法是：先用H门将状态从|+⟩基转回计算基|0⟩，接着对|00⟩态进行相位翻转，然后再用H门转回原基矢。在isQ语言的具体实现中，需通过`qbit q[2]`声明量子寄存器，并使用`procedure`关键字分别封装Oracle和扩散算子逻辑。最后，在主程序中先用H门初始化叠加态，再依次调用这两个封装好的子程序，并辅以逐行注释说明门操作的物理与数学意义即可完成代码编写。
</think>

下面是使用isQ语言实现2比特系统中针对目标态|11⟩的量子振幅放大完整代码及详细的逐行注释分析。

```isQ
// 引入标准库
import std;

// 定义量子比特的数量
const int N = 2;

// 在全局作用域声明包含2个量子比特的量子寄存器
qbit q[N];

// 定义Oracle过程，用于标记目标态（这里是|11⟩）
procedure oracle() {
    // 当且仅当q[0]和q[1]都处于|1⟩状态时，对其概率幅反转（即乘以-1）
    // 受控Z门（CZ）在输入为|11⟩时引入pi的相位，等价于将概率幅变为-1
    CZ(q[0], q[1]);
}

// 定义扩散算子过程，用于放大被标记态的振幅
procedure diffusion() {
    // 扩散算子的数学本质是对均匀叠加态进行反射，即应用矩阵 2|s><s| - I
    // 构造该算子的通用方法是先将状态从|+⟩基转换回计算基|0⟩
    H(q[0]);
    H(q[1]);
    
    // 对计算基|00⟩的状态进行相位翻转
    // 先使用X门将|0⟩翻转为|1⟩
    X(q[0]);
    X(q[1]);
    
    // 此时状态为|11⟩，再次使用类似于Oracle的受控相位翻转
    // 使用H-CNOT-H组合来等效实现CZ门
    H(q[1]);
    CNOT(q[0], q[1]);
    H(q[1]);
    
    // 使用X门恢复状态
    X(q[0]);
    X(q[1]);
    
    // 再次应用H门，将计算基转换回|+⟩基，完成整个扩散操作
    H(q[0]);
    H(q[1]);
}

// 主程序入口
procedure main() {
    // 步骤1：初始化。对每一个量子比特应用Hadamard门
    // 使得系统进入等概率的均匀叠加态：1/2 * (|00⟩ + |01⟩ + |10⟩ + |11⟩)
    H(q[0]);
    H(q[1]);
    
    // 步骤2：执行振幅放大迭代
    // 对于4个元素的搜索空间，找到唯一目标态需要的最优迭代次数为1次
    // 首先调用Oracle标记坏态和好态
    oracle();
    // 然后调用扩散算子反转并放大目标态的振幅
    diffusion();
    
    // 步骤3：测量量子比特寄存器
    // 经过放大后，测量结果将以极高的概率（理论上为100%）坍缩到目标态|11⟩
    M(q[0]);
    M(q[1]);
}
```

**代码逻辑详细解析：**

1. **Oracle的实现**：在振幅放大算法中，Oracle的作用是识别“好”的量子态并给其加上一个负号（相位翻转）。在我们的代码中，目标态是|11⟩，因此使用一个双量子比特的受控Z门（CZ）即可完美实现。CZ门仅在两个控制比特均为1时对相位产生π的偏移，从而将系数变为负数。

2. **扩散算子的构造**：扩散算子旨在将刚才被Oracle翻转的负振幅“放大”并平均分配。数学上，它是关于均匀叠加态|s⟩的反射。由于在isQ中直接实现多量子比特任意酉变换较复杂，我们采用标准的门分解法：先用H门回到计算基，接着用X门将|00⟩变为|11⟩，用受控相位操作（此处利用H-CNOT-H复合门等效）翻转其相位，再原路返回（X门恢复，H门恢复）。这一套操作完美等价于公式 $2|s\rangle\langle s| - I$ 描述的酉矩阵。

3. **迭代次数与测量**：对于包含 $N=2^2=4$ 个状态的空间，寻找1个目标态的最优振幅放大迭代次数为 $\lfloor \frac{\pi}{4}\sqrt{4} \rfloor = 1$ 次。因此代码中只调用了一次`oracle()`和`diffusion()`。最终执行测量时，系统状态已经几乎完全坍缩至|11⟩，所以测得二进制字符串'11'的概率将接近100%。

## isqTrain/1082

- task_id: `isqTrain/1082`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4620`

### Prompt

Implement a quantum circuit in isQ: implements a variant of the deutsch_jozsa pattern using anc[1] -> anc[2]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning

**Goal**: Implement Deutsch-Jozsa with a balanced oracle (f(x) = x₀ ⊕ x₁) using a 2-qubit input register and 2-qubit ancilla, demonstrating single-query function classification.

**Qubits**: 4 total (q[0], q[1] as input; anc[0], anc[1] as ancilla). Only q[0] and q[1] are measured.

**State evolution**:
1. Initial: |00⟩|00⟩
2. X(anc[0]): |00⟩|10⟩
3. H(anc[0]): |00⟩(|0⟩−|1⟩)/√2 ⊗ |0⟩ = |00⟩|−⟩|0⟩
4. H(q[0]), H(q[1]): (|00⟩+|01⟩+

## isqTrain/1086

- task_id: `isqTrain/1086`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4301`

### Prompt

Create an isQ quantum circuit that implements the deutsch_jozsa pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

Let me analyze the Deutsch-Jozsa algorithm as implemented in this isQ code.

1. **Goal**: Determine if a function f is constant or balanced using a single quantum query (classically requires 2^(n-1)+1 queries for n inputs).

2. **Qubits**: 2 input qubits q[0], q[1] and 1 ancilla qubit anc[0]. Only q[0] and q[1] are measured.

3. **State evolution**:

Initial state: |000⟩ (q[0], q[1], anc[0])

After X(anc[0]): |001⟩

After H(anc[0]): |00⟩⊗(|0⟩-|1⟩)/√2

After H(q[0])H(q[1]): (|00⟩+|01⟩+|10⟩+|11⟩)/2 ⊗ (|0⟩-|1⟩)/√2

The oracle f(q, anc) applies U_f|x⟩|y⟩ = |x⟩|y⊕f(x)⟩

For the balanced function f(x) = x[0] XOR x[1]:
- f(00) = 0
- f(01) = 1
- f(10) = 1
- f(11) = 0

So after the oracle:
(−1)^f(00)|00⟩ + (−1)^f(01)|01⟩ + (−1)^f(10)|10⟩ + (−1)^f(11)|11⟩)/2 ⊗ (|0⟩-|1⟩)/√2
= (|00⟩ - |01⟩ - |10⟩ + |11⟩)/2 ⊗ (|0⟩-|1⟩)/√2

After H(q[0])H(q[1]) on the input register:
The input register becomes: (H⊗H)(|00⟩ - |01⟩ - |10⟩ + |11⟩)/2

Let me compute this:
H⊗H|00⟩ = (|0⟩+|1⟩)(|0⟩+|1⟩)/2 = (|00⟩+|01⟩+|10⟩+|11⟩)/2
H⊗H|01⟩ = (|0⟩+|1⟩)(|0⟩-|1⟩)/2 = (|00⟩-|01⟩+|10⟩-|11⟩)/2
H⊗H|10⟩ = (|0⟩-|1⟩)(|0⟩+|1⟩)/2 = (|00⟩+|01⟩-|10⟩-|11⟩)/2
H⊗H|11⟩ = (|0⟩-|1⟩)(|0⟩-|1⟩)/2 = (|00⟩-|01⟩-|10⟩+|11⟩)/2

So:
H⊗H(|00⟩ - |01⟩ - |10⟩ + |11⟩)/2
= [(|00⟩+|01⟩+|10⟩+|11⟩) - (|00⟩-|01⟩+|10⟩-|11⟩) - (|00⟩+|01⟩-|10⟩-|11⟩) + (|00⟩-|01⟩-|10⟩+|11⟩)]/4
= [|00⟩+|01⟩+|10⟩+|11⟩ - |00⟩+|01⟩-|10⟩+|11⟩ - |00⟩-|01⟩+|10⟩+|11⟩ + |00⟩-|01⟩-|10⟩+|11⟩]/4
= [0 + 0 + 0 + 4|11⟩]/4
= |11⟩

So after the final Hadamards on input register, we get |11⟩⊗(|0⟩-|1⟩)/√2.

Now, the code has H(q[0]) followed by H(q[0]) before measurement. These form an identity pair (H⊗H = I), so the state remains |11⟩.

Wait, let me re-read the code more carefully:

So after the second pair of H(q[0])H(q[1]) transforms |00⟩ - |01⟩ - |10⟩ + |11⟩) / 2 → |11⟩ (as I computed above).

Then H(q[0])H(q[0]) = I on q[0], so the state remains |11⟩.

The measurement of q[0] and q[1] gives
