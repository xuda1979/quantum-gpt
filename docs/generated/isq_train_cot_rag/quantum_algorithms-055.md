# ISQ training COT RAG corpus: quantum_algorithms shard 55

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/744

- task_id: `isqTrain/744`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`, `phase_manipulation`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `1839`

### Prompt

帮我写一个isQ程序：implements the qft_adder pattern with modified rotation parameters (num_pi2s_to_pi3). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

Let me analyze this QFT adder circuit step by step.

The circuit has 2 qubits q[0] and q[1]. The input is 1 (|10⟩), and we add a constant using phase rotations in the Fourier domain.

The "modified rotation parameters (num_pi2s_to_pi3)" suggests the rotation angle for q[1] has been changed from the standard QFT adder. Normally in a QFT adder adding constant 1 to a 2-qubit register, the phase rotations would be:
- qubit 0: π (for the 2^0 bit)
- qubit 1: π/2 (for the 2^1 bit)

But here, q[1] gets Rz(1.04719755119660490) which is π/3 instead of π/2.

Let me trace the state evolution:

1. Initial state: |00⟩
2. After X(q[0]): |10⟩

3. Forward QFT on 2 qubits:
   - H(q[1]): This is applied to q[1] which is |0⟩, so → |10⟩ (no change to the overall state since q[1] is |0⟩)
   
   Wait, let me reconsider. The QFT for 2 qubits typically processes qubits in a specific order. Let me look at the circuit more carefully.

   The QFT structure here:
   - H(q[1])
   - ctrl S(q[0], q[1]) - controlled S with q[0] as control, q[1] as target
   - H(q[0])

   Starting from |10⟩ (q[0]=1, q[1]=0):

   After H(q[1]): q[1] goes from |0⟩ to |+⟩ = (|0⟩+|1⟩)/√2
   State: (|10⟩ + |11⟩)/√2 = |1⟩⊗(|0⟩+|1⟩)/√2

   After ctrl S(q[0], q[1]): When q[0]=|1⟩, apply S to q[1]. 
   S|0⟩ = |0⟩, S|1⟩ = i|1⟩
   So |1⟩⊗(|0⟩+|1⟩)/√2 → |1⟩⊗(|0⟩+i|1⟩)/√2

   After H(q[0]): H|1⟩ = (|0⟩-|1⟩)/√2
   State: (|0⟩-|1⟩)/√2 ⊗ (|0⟩+i|1⟩)/√2
   = (|00⟩+i|01⟩-|10⟩-i|11⟩)/2

   Actually, the QFT of |10⟩ (which represents the integer 1 in little-endian or 2 in big-endian... let me think about the encoding).

   Actually in QFT, if we have |x₁x₀⟩ representing x = 2x₁ + x₀ (big-endian) or x = 2x₀ + x₁ (little-endian)...

   Looking at the circuit, X(q[0]) encodes input value 1. So it seems like q[0] is the least significant bit. So |10⟩ = q[0]=1, q[1]=0 represents the integer 1.

   The QFT of |x⟩ for a 2-qubit system gives:
   QFT|x⟩ = (1/2) Σ_k e^{2πixk/4} |k⟩

   For x=1: QFT|1⟩ = (1/2)(|0⟩ + e^{iπ/2}|1⟩ + e^{iπ}|2⟩ + e^{i3π/2}|3⟩)
   = (1/2)(|0⟩ + i|1⟩ - |2⟩ - i|3⟩)

   In the basis |q[1]q[0]⟩:
   = (1/2)(|00⟩ + i|01⟩ - |10⟩ - i|11⟩)

   This matches what I calculated! Good.

4. Phase rotations (adding constant via phase):
   - Rz(π, q[0]): This applies phase e^{-iπ/2} to |0⟩ and e^{iπ/2} to |1⟩ for q[0]
   
   Wait, Rz(θ) = [[e^{-iθ/2}, 0], [0, e^{iθ/2}]]
   
   Rz(π, q[0]): phase on q[0]: |0⟩→e^{-iπ/2}|0⟩, |1⟩→e^{iπ/2}|1⟩
   
   Rz(

## isqTrain/94

- task_id: `isqTrain/94`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5090`

### Prompt

Code this in isQ: implements the gate_decomposition pattern with modified rotation parameters (pi2_to_pi3). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Implement a QAOA-inspired circuit with modified rotation parameters (π/3 for cost, π/4 for mixing).

**Qubits:** 2 qubits (q[0], q[1]), both measured.

**State evolution:**
1. **H gates:** |00⟩ → (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩) = |++⟩
2. **CNOT-Rz(π/3)-CNOT:** This sequence applies a ZZ-interaction, adding phase e^(iπ/6) to |11⟩ and e^(-iπ/6) to |10⟩, yielding: (1/2)(|00⟩ + |01⟩ + e^(-iπ/6)|10⟩ + e^(iπ/6)|11⟩)
3. **Rx(π/4) on both:** Each qubit undergoes X-rotation by π/4, partially mixing computational basis states while preserving the correlation between qubits

**Expected probabilities:** The symmetry of identical rotations on both qubits ensures P(|00⟩) = P(|11⟩) ≈ 0.4665 and P(|01⟩) = P(|10⟩) ≈ 0.0335. The ZZ-interaction with θ=π/3 creates phase alignment favoring correlated outcomes (|00⟩, |11⟩), while Rx(π/4)

## isqTrain/871

- task_id: `isqTrain/871`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3790`

### Prompt

I need an isQ program to implements a variant of the inner_product_mod2 pattern using q[5] -> q[6]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Compute inner product mod 2 of x=[1,0] and y=[1,1], storing result in q[4], with q[5] as auxiliary measured qubit.
2. **Qubits**: 6-qubit register; q[0],q[1] encode x, q[2],q[3] encode y, q[4] accumulates result, q[5] measured as |0⟩.
3. **State evolution**: Initial |000000⟩ → X(q[0]) → |100000⟩ → X(q[2]);X(q[3]) → |101100⟩ → Toffoli(q[0],q[2],q[4]) flips q[4] since both controls are |1⟩ → |101110⟩ → Toffoli(q[1],q[3],q[4]) doesn't flip (q[1]=|0⟩) → |101110⟩.
4. **Final state**: q[4]=|1⟩ (IP = 1·1 ⊕ 0·1 = 1), q[5]=|0⟩, giving measurement bitstring |10⟩ with probability 1.0.

## isqTrain/346

- task_id: `isqTrain/346`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `4014`

### Prompt

Code this in isQ: implements a variant of the arithmetic_circuit pattern using c[1] -> c[3]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

The user wants me to analyze a variant of the arithmetic_circuit pattern and write reasoning for it.

Let me understand The implementation first:
- We have qubit registers c[3] and p[2]
- H(c[0]) puts c[0] into superposition: |0> -> |+> = (|0> + |1>)/√2
- ctrl INC(c[0], p[0], p[1]) - applies INC to p[0], p[1] controlled by c[0]
- nctrl DEC(c[0], p[0], p[1]) - applies DEC to p[0], p[1] controlled by NOT c[0]

Looking at the gates:
- INC: CNOT(p0, p1), X(p0)
- DEC: X(p0), CNOT(p0, p1)

For the variant with c[1] -> c[3]:
- We need to use c[1] through c[3] instead of c[0]
- Significantly expanded qubit register with additional qubits left in ground state

Wait, let me re-read. The prompt says "using c[1] -> c[3]" which means the circuit should use c[1] to c[3].

Actually, looking more carefully at The implementation:
- c[3] is declared but only c[0] is used
- p[2] is used

For the variant:
- We need c[1] -> c[3] meaning we use c[1], c[2], c[3]
- Expanded register with additional qubits in ground state

Let me think about what the circuit does:

Initial state: |0...0>

After H(c[0]): c[0] is in |+> state
State = (|0> + |1>)/√2 ⊗ |00>_p ⊗ |000>_{c[1],c[2],c[3]}

For the variant with c[1] -> c[3], I think the control should be on c[1] instead of c[0].

Let me trace through the original:
1. H(c[0]): State becomes (|000000> + |100000>)/√2 (where c[0] is first qubit)

2. ctrl INC(c[0], p[0], p[1]):
   - When c[0]=|1>: apply INC to p[0], p[1]
   - INC(p[0], p[1]) = CNOT(p0, p1), X(p0)
   - Starting from |00>: CNOT -> |00>, X(p0) -> |10>
   - So state becomes (|000000> + |111000>)/√2 (adjusting qubit order)

Wait, let me be more careful. Let's label qubits as: c[0], c[1], c[2], p[0], p[1]
No wait, the reference has c[3] and p[2].

Let me use the order: c[0], c[1], c[2], p[0], p[1]

Initial: |00000>

After H(c[0]): (|00000> + |10000>)/√2

ctrl INC(c[0], p[0], p[1]):
- When c[0]=1, apply INC to p[0], p[1]
- INC(p0, p1): CNOT(p0, p1) then X(p0)
- Starting p state |00>: CNOT(|00>) = |00>, then X(p0)|00> = |10>
- Result: (|00000> + |11000>)/√2

nctrl DEC(c[0], p[0], p[1]):
- When c[0]=0, apply DEC to p[0], p[1]
- DEC(p0, p1): X(p0) then CNOT(p0, p1)
- Starting p state |00>: X(p0)|00> = |10>, then CNOT|10> = |11>
- When c[0]=1, p state is |10>: X(p0)|10> = |00>, CNOT|00> = |00>
- Result: (|01100> + |11000>)/√2

Wait, I need to track this more carefully. Let me use a cleaner notation.

Let me denote state as |c0 c1 c2 p0 p1>

After H(c[0]): (|00000> + |10000>)/√2

ctrl INC(c[0], p[0], p[1]):
- For |00000>: c0=0, so no change, stays |00000>
- For |10000>: c0=1, so

## isqTrain/2058

- task_id: `isqTrain/2058`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_oracle`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4520`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;
oracle bool[1] f(bool x[2]) {
    bool res[] = [x[0] != x[1]];
    return res;
}
qbit q[2];
qbit anc[1];
procedure main() {
    X(anc[0]);
    H(anc[0]);
    H(q[0]); H(q[1]);
    f(q, anc);
    H(q[0]); H(q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants a step-by-step quantum circuit analysis for a specific isQ program implementing the Deutsch-Jozsa algorithm. The algorithm determines if a 2-bit function is constant or balanced. The predicted output a "Circuit Analysis" section ending with the probability distribution.

2.  **Analyze the isQ Code**:
    *   `oracle bool[1] f(bool x[2]) { bool res[] = [x[0] != x[1]]; return res; }`
        *   This defines a boolean function $f(x)$ where $x$ is a 2-bit string.
        *   $f(x) = x_0 \oplus x_1$ (XOR).
        *   Let's evaluate $f(x)$:
            *   $f(00) = 0 \neq 0 = 0$
            *   $f(01) = 0 \neq 1 = 1$
            *   $f(10) = 1 \neq 0 = 1$
            *   $f(11) = 1 \neq 1 = 0$
        *   Since $f(00)=0, f(11)=0$ and $f(01)=1, f(10)=1$, the function is *balanced* (two 0s, two 1s).
    *   Quantum circuit steps:
        *   `qbit q[2];` -> registers $q_0, q_1$
        *   `qbit anc[1];` -> register $a_0$
        *   `X(anc[0]);` -> $a_0$ becomes $|1\rangle$
        *   `H(anc[0]);` -> $a_0$ becomes $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$
        *   `H(q[0]); H(q[1]);` -> $q_0, q_1$ become $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$
        *   State before oracle: $\frac{1}{2} \sum_{x=0}^{3} |x\rangle \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$
        *   `f(q, anc);` -> applies $U_f |x\rangle |y\rangle = |x\rangle |y \oplus f(x)\rangle$.
        *   Effect of phase kickback: $|x\rangle \frac{1}{\sqrt{2}}(|0 \oplus f(x)\rangle - |1 \oplus f(x)\rangle) = (-1)^{f(x)} |x\rangle \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$
        *   Since $f(x)$ is balanced, the sum over $x$ picks up a phase of $-1$ for $x=01, 10$.
        *   State after oracle: $\frac{1}{2} (|00\rangle - |01\rangle - |10\rangle + |11\rangle) \otimes |-\rangle$
        *   Wait, let's look at the state $\frac{1}{2} (|00\rangle - |01\rangle - |10\rangle + |11\rangle)$. Is this $|11\rangle$ in the Hadamard basis?
        *   Let's check $H^{\otimes 2} |11\rangle$:
            *   $H|1\rangle = |-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$
            *   $|-\rangle \otimes |-\rangle = \frac{1}{2}(|0\rangle - |1\rangle) \otimes (|0\rangle - |1\rangle) = \frac{1}{2}(|00\rangle - |01\rangle - |10\rangle + |11\rangle)$.
            *   Yes, exactly!
        *   `H(q[0]); H(q[1]);` -> Applies $H^{\otimes 2}$ to the state $\frac{1}{2} (|00\rangle - |01\rangle - |10\rangle + |11\rangle)$.
        *   State becomes $|11\rangle$.
        *   `M(q[0]); M(q[1]);` -> Measures $q_0, q_1$.

3.  **Format the Output**:
    *   Start with `## Circuit Analysis`.
    *   Step-by-step evolution using

### Reference answer

{'predicted_probs': {'11': 1.0}, 'explanation': 'Deutsch-Jozsa for balanced f(x)=x0 XOR x1: P(|11>)=1.0.'}

## isqTrain/3602

- task_id: `isqTrain/3602`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `entanglement`, `ancilla_usage`, `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `2468`

### Prompt

Fix the bug in the following isQ program.

Bug description: Wrong CNOT direction

The program should 3-qubit bit-flip code: error on q[0], correction.

### Chain-of-thought reasoning

Let me analyze the bug in this isQ program.

The program is supposed to implement a 3-qubit bit-flip code that:
1. Encodes |0> → |000>
2. Injects an X error on q[0]
3. Extracts the error syndrome
4. Corrects the error

Let me trace through the buggy code:

**Buggy encoding:**
- `CNOT(q[1], q[0])` - CNOT with q[1] as control, q[0] as target
- `CNOT(q[0], q[2])` - CNOT with q[0] as control, q[2] as target

Starting state: |000>

After first CNOT(q[1], q[0]):
- q[1] is control (|0>), q[0] is target
- Since control is |0>, target is unchanged
- State remains |000>

After second CNOT(q[0], q[2]):
- q[0] is control (|0>), q[2] is target
- Since control is |0>, target is unchanged
- State remains |000>

Wait, actually the encoding should transform |0>|0>|0> → |000>. But let's think about what the correct encoding should be:

For a 3-qubit bit-flip code encoding |ψ⟩ = α|0⟩ + β|1⟩:
- The encoding maps |0⟩ → |000⟩ and |1⟩ → |111⟩

Starting from |000⟩ (all qubits in |0⟩):
- We want the state to remain |000⟩

The correct encoding uses:
- `CNOT(q[0], q[1])` - copies q[0] to q[1]
- `CNOT(q[0], q[2])` - copies q[0] to q[2]

This works because if q[0] is |0⟩, then q[1] and q[2] stay |0⟩.
If q[0] is |1⟩, then q[1] and q[2] become |1⟩.

So the correct encoding starting from |ψ⟩|0⟩|0⟩ would give |ψ⟩⊗|ψ⟩⊗|ψ⟩ when measured in the computational basis.

**The bug:**
The buggy code has `CNOT(q[1], q[0])` instead of `CNOT(q[0], q[1])`.

This is the wrong CNOT direction. The first CNOT should have q[0] as control and q[1] as target, but the buggy code has it reversed.

**Effect of the bug:**
With the buggy code:
- CNOT(q[1], q[0]): q[1]=|0⟩ is control, so nothing happens, q[0] stays |0⟩
- CNOT(q[0], q[2]): q[0]=|0⟩ is control, so nothing happens, q[2] stays |0⟩
- State after encoding: |000⟩

Then X(q[0]) flips q[0]: |100⟩

Syndrome extraction:
- CNOT(q[0], anc[0]): q[0]=|1⟩, so anc[0] flips to |1⟩
- CNOT(q[1], anc[0]): q[1]=|0⟩, so anc[0] stays |1⟩
- CNOT(q[0], anc[1]): q[0]=|1⟩, so anc[1] flips to |1⟩  
- CNOT(q[2], anc[1]): q[2]=|0⟩, so anc[1] stays |1⟩

Syndrome: anc[0]=1, anc[1]=1 (syndrome 11)

Correction: ctrl ctrl X(anc[0], anc[1], q[0]) - This flips q[0] when both anc[0]=1 and anc[1]=1

After correction: q[0] flips back to |0⟩, state is |000⟩

Hmm, actually with the buggy code starting from |000⟩, the encoding doesn't really do anything different since all qubits are |0⟩. Let me think about this more carefully...

Actually, the issue is that the encoding is supposed to create entanglement. If we started with a general state α|0⟩ + β|1⟩ on q[0], then:

**Correct encoding:**
- Start: (α|0⟩ + β|1⟩)|0⟩|0⟩
- CNOT(q[0], q[1]): (α|00⟩ + β|11⟩)|0⟩
- CNOT(q[0], q[2]): α|000⟩ + β|111⟩ ✓

**Buggy encoding:**
- Start: (α

## isqTrain/4189

- task_id: `isqTrain/4189`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `5366`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
qbit q[3];

procedure main() {
    H(q[0]); H(q[1]); H(q[2]);
    CNOT(q[0], q[1]);
    Rz(2.0 * 0.785, q[1]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    Rz(2.0 * 0.785, q[2]);
    CNOT(q[1], q[2]);
    Rx(2.0 * 0.393, q[0]);
    Rx(2.0 * 0.393, q[1]);
    Rx(2.0 * 0.393, q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis

1. **Operations**: H on all qubits → CNOT(0,1) → Rz(π/2,1) → CNOT(0,1) → CNOT(1,2) → Rz(π/2,2) → CNOT(1,2) → Rx(π/5,0) → Rx(π/5,1) → Rx(π/5,2)

2. **State evolution**:
- |000⟩ → H⊗3 → |+++⟩ = (1/2√2)(|000⟩+|001⟩+|010⟩+|011⟩+|100⟩+|101⟩+|110⟩+|111⟩)
- The CNOT-Rz-CNOT sequences on (0,1) and (1,2) apply CPHASE(π/2): adding phase e^(iπ/2)=i when both qubits are |1⟩. This entangles qubits (0,1) and (1,2) with relative phases.
- The resulting entangled state before Rx rotations has complex amplitudes with specific phase relationships between basis states involving odd numbers of 1s.

3. **Final state**: The small Rx(π/5) ≈ Rx(36°) rotations slightly tilt each qubit's state in the X-direction, perturbing the entangled superposition. The state remains a complex superposition of all 8 basis states with non-uniform amplitudes.

4. **Predicted probability distribution**:
The distribution is approximately uniform with slight deviations due to the small Rx rotations. The most likely outcomes are **|000⟩** and **|111⟩** (around ~13.5% each), while other states (|001⟩, |010⟩, |011⟩, |100⟩, |101⟩, |110⟩) have probabilities around ~12.2-12.5%. The CPHASE interactions create constructive interference for the |000⟩ and |111⟩ components. Expected distribution: roughly (0.135, 0.122, 0.122, 0.125, 0.122, 0.125, 0.125, 0.135) indexed from |000⟩ to |111⟩.

### Reference answer

Uniform distribution across 8 states

## isqQA/quantum_algorithms/113_optimization_variant

- task_id: `isqQA/quantum_algorithms/113_optimization_variant`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `optimization_variant`, `algorithm`, `QFT与经典FFT的对比`
- source: `qa_pipeline`
- dataset_index: `2990`

### Prompt

能否介绍量子傅里叶变换（QFT）针对近期量子硬件限制所提出的重要优化变体，特别是近似量子傅里叶变换（AQFT）？请详细解释其核心原理、与经典FFT在优化思路上的异同，并用isQ代码实现一个忽略远距离控制相位操作的4比特AQFT电路。

### Reference answer

量子傅里叶变换（QFT）是Shor算法等核心量子算法的基石。虽然标准QFT在数学上只需要 O(N^2) 个量子门，但在当前含噪声中等规模量子（NISQ）时代，深电路极易受到退相干影响。为此，研究人员提出了一系列QFT的优化变体，其中最具代表性的是近似量子傅里叶变换（Approximate Quantum Fourier Transform, AQFT）。

AQFT的核心原理在于：在 N 比特的标准QFT中，控制相位旋转的角度为 π/2^k，当控制距离 k 较大时，旋转角度极其微小。在物理硬件上，执行这些极小角度门的开销大且容易被系统噪声完全掩盖，对最终的计算结果贡献微乎其微。AQFT通过引入一个截断距离 m（m < N），直接忽略所有控制距离大于 m 的相位门，只保留距离较近的比特间的纠缠操作。这一改进将电路的深度和两比特门数量从 O(N^2) 降低到了 O(N m)，在牺牲极小精度的情况下大幅提升了算法在物理硬件上的运行成功率。

将AQFT与经典快速傅里叶变换（FFT）的优化进行对比是非常有趣的。经典FFT（如Cooley-Tukey算法）的优化核心在于代数结构的分治与因式分解，旨在消除离散傅里叶变换中的冗余乘法，将计算复杂度从 O(N^2) 降至 O(N log N)。相比之下，量子QFT本身的复杂度已经是 O(N^2)，实现了相对经典计算的指数级加速（尽管提取完整信息受限于量子测量导致的态坍缩）。AQFT的优化并非为了减少纯数学计算量，而是针对底层物理硬件连通性和门保真度的“物理近似”，是通过主动丢弃物理上难以实现且影响微弱的量子干涉细节来换取整体电路保真度的策略。

除了AQFT，QFT的其他重要变体还包括基于测量的QFT和针对特定拓扑网络优化的QFT。近期研究中，利用动态量子电路（含中间测量与经典前馈）的QFT变体也备受关注，这种变体通过在测量后重置并复用量子比特，显著减少了长寿命纠缠的需求。

以下是用isQ语言实现的4比特近似量子傅里叶变换（AQFT）示例代码。该代码将截断距离设为2，即忽略控制距离大于2的相位操作，并使用CNOT组合代替被禁止的SWAP门以完成最终比特顺序的反转：

import std;

const int N = 4;
const int m = 2;

qbit q[N];

procedure main() {
    // 执行AQFT，从高位比特到低位比特
    for i in 0:N {
        int target = N - 1 - i;
        H(q[target]);
        
        // 仅在截断距离 m 内施加控制相位门
        for j in 1:m {
            int control_idx = target - j;
            if (control_idx >= 0) {
                // 计算旋转角度 π / 2^j
                double angle = 3.1415926535 / pow(2.0, j + 0.0);
                // 施加受控相位门
                ctrl @[control_idx] Rz(angle, q[target]);
            }
        }
    }
    
    // 使用3个CNOT模拟SWAP门以反转比特顺序
    // 常规AQFT需要交换 q[0]<->q[3] 和 q[1]<->q[2]
    for i in 0:2 {
        int a = i;
        int b = N - 1 - i;
        if (a < b) {
            CNOT(q[a], q[b]);
            CNOT(q[b], q[a]);
            CNOT(q[a], q[b]);
        }
    }
}

## isqExpand/algo/26

- task_id: `isqExpand/algo/26`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `amplitude_estimation`, `grover`, `qpe`, `quantum_counting`
- source: `isq_expansion_qa`
- dataset_index: `2370`

### Prompt

量子振幅估计（Quantum Amplitude Estimation）算法是什么？它与Grover搜索和量子相位估计有什么关系？

### Chain-of-thought reasoning

## 推理
目标：解释QAE算法及其与Grover和QPE的关系。

推导链：
1. QAE的核心问题：给定算子A，估计 A|0> 在目标子空间的振幅
2. Grover算子 G 在 {good, bad} 二维子空间中是旋转 2θ_a
3. G 的特征值 e^{±2iθ_a} 编码了振幅信息
4. 对 G 做 QPE 就能提取 θ_a
5. Grover搜索是 QAE 的特殊应用——不需要知道精确 θ_a，只需放大概率
6. QAE 提供二次加速：O(1/ε) vs 经典的 O(1/ε²)

### Reference answer

## 量子振幅估计

### 基本定义
量子振幅估计（QAE）用于估计某个量子算子 A 作用于初始态后，目标态的振幅 a = sin²(θ_a)。
设 A|0> = sin(θ_a)|good> + cos(θ_a)|bad>，QAE 的目标是精确估计 θ_a（从而得到概率 a）。

### 与Grover搜索的关系
Grover算子 G = A·S_0·A†·S_χ 是 QAE 的核心组件：
- S_χ：对目标态加负号（Oracle）
- S_0：对 |0> 态加负号（扩散算子）
- G 在 {|good>, |bad>} 子空间中是旋转角度 2θ_a 的旋转
- G 的特征值为 e^{±2iθ_a}

Grover搜索反复应用 G 来放大 |good> 的概率，但不需要知道 θ_a 的精确值。QAE则通过 QPE 精确估计 θ_a。

### 与QPE的关系
QAE 的标准实现就是对 Grover 算子 G 执行 QPE：
1. 准备态 A|0> = sin(θ_a)|good> + cos(θ_a)|bad>
2. 对 G 执行 QPE，测量得到 θ̃_a ≈ θ_a
3. 计算 ã = sin²(θ̃_a)

### 精度
使用 m 个额外量子比特（计数寄存器），QAE 可以达到精度 O(1/2^m)，查询复杂度为 O(2^m)，相比经典蒙特卡洛的 O(1/ε²) 有二次加速。

### 应用场景
- **量子计数**：估计 Grover 搜索中解的数量
- **量子金融**：期权定价、风险分析
- **量子机器学习**：内积估计
- **HHL后处理**：估计 |x> 中特定分量的概率

## isqQA/quantum_algorithms/132_step_by_step

- task_id: `isqQA/quantum_algorithms/132_step_by_step`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `step_by_step`, `algorithm`, `量子全加器`
- source: `qa_pipeline`
- dataset_index: `2784`

### Prompt

如何一步步手动追踪一个量子全加器电路的演化过程？

### Reference answer

<think>
追踪量子全加器演化的核心在于将布尔逻辑映射到量子态的幺正变换，其推理思路如下：

首先，明确物理架构，将逻辑变量（加数、进位输入、输出辅助比特）映射到具体的量子比特，构建多比特系统的希尔伯特空间。

其次，编码初始状态。根据预设的加法输入，利用X门将对应的目标比特翻转，确定系统的初始计算基态。

接着，进行逐门状态追踪。全加器通常由Toffoli和CNOT门构成，追踪时需重点关注控制比特的状态：先分析进位路径（Toffoli门），当控制位均满足条件时翻转目标辅助比特；再分析求和路径（CNOT门级联），完成输入与进位的异或计算。每作用一个量子门，都需要依据受控逻辑更新系统的全局状态向量。

最后，在电路末端观察态向量分布，从中提取出最终的求和位与进位位，完成整个逻辑闭环的验证。
</think>

量子全加器是将经典二进制加法推广到量子域的核心算法，其目标是计算两个量子比特 $a$ 和 $b$ 的和以及进位。一个典型的基于 Toffoli 和 CNOT 门的全加器包含三个主要输入量子比特：$a$、$b$ 和一个进位输入 $c_{in}$，以及两个输出：和位 $s$ 与进位输出 $c_{out}$。由于可用的辅助比特数量不同，全加器的实现方式有多种。这里我们以一个包含专门辅助比特的简化全加器为例进行追踪。假设我们有四个量子比特：$q[0]$ 代表 $a$，$q[1]$ 代表 $b$，$q[2]$ 代表 $c_{in}$，$q[3]$ 为初始为 $0$ 的辅助比特，用于存储进位输出 $c_{out}$。

步骤 1：初始化状态
假设我们想要计算 $1 + 1 + 0$，即 $a=1, b=1, c_{in}=0$。我们首先通过 $X$ 门准备初始状态。对 $q[0]$ 和 $q[1]$ 应用 $X$ 门，系统的状态演化为 $|a
angle|b
angle|c_{in}
angle|c_{out}
angle = |1100
angle$。

步骤 2：计算进位输出
为了计算进位输出 $c_{out} = (a \cdot b) \oplus (c_{in} \cdot (a \oplus b))$，我们首先关注 $a \cdot b$ 这一项。我们对 $q[0]$（控制位 $a$）、$q[1]$（控制位 $b$）和 $q[3]$（目标位 $c_{out}$）应用 Toffoli 门。在状态 $|1100\rangle$ 下，两个控制位均为 1，因此目标位 $q[3]$ 翻转。系统状态变为 $|1101\rangle$。

步骤 3：计算半加和
接下来我们需要计算 $a \oplus b$。我们对 $q[0]$（控制位）和 $q[1]$（目标位）应用 CNOT 门。此时 $q[0]$ 为 1，因此目标位 $q[1]$ 翻转（从 1 变为 0）。系统状态演化为 $|1001\rangle$。此时 $q[1]$ 中存储了 $a \oplus b$ 的结果，即 $1 \oplus 1 = 0$。

步骤 4：计算第二部分进位
根据 $c_{out}$ 的计算公式，我们还需要加上 $c_{in} \cdot (a \oplus b)$ 的贡献。注意此时 $q[1]$ 存储的是 $a \oplus b$，$q[2]$ 存储的是 $c_{in}$。我们对 $q[2]$（控制位）和 $q[1]$（目标位，控制条件）以及 $q[3]$（目标位）应用 Toffoli 门。但在当前状态 $|1001\rangle$ 下，$q[2]=0$，控制条件不满足，因此 $q[3]$ 不翻转。状态保持为 $|1001\rangle$。这意味着进位输出 $c_{out}$ 为 1。

步骤 5：计算最终和位
最终的和位 $s$ 的计算公式为 $(a \oplus b) \oplus c_{in}$。由于 $q[1]$ 当前存储了 $a \oplus b$ 的半加和，而 $q[2]$ 存储了 $c_{in}$，我们对 $q[2]$（控制位）和 $q[1]$（目标位）应用 CNOT 门。在当前状态 $|1001\rangle$ 下，控制位 $q[2]$ 为 0，因此 $q[1]$ 不发生翻转。系统状态依然为 $|1001\rangle$。

步骤 6：恢复输入状态并读取结果
此时 $q[1]$ 中存储的就是最终的和位 $s=0$，而 $q[3]$ 中存储的是进位输出 $c_{out}=1$。但是请注意，步骤 3 中的 CNOT 门破坏了原本的 $b$ 状态（被替换为了 $a \oplus b$）。如果我们希望在计算后保留原始输入 $b$ 的值，我们需要对 $q[0]$ 和 $q[1]$ 再次应用 CNOT 门（即逆操作）。此时 $q[0]$ 仍为 1，所以 $q[1]$ 再次翻转，从 0 变回 1。最终系统的状态演化为 $|1101\rangle$。这表明我们成功恢复了输入 $a=1, b=1, c_{in}=0$，并得到了正确的进位输出 $c_{out}=1$。通过将这种状态制备替换为处于叠加态的输入，该电路即可并行处理所有可能的输入组合，体现量子并行计算的优势。

下面是使用 isQ 语言实现上述无恢复步骤（1至5步）的量子全加器电路代码：
```isq
import std;

qbit q[4];

procedure main() {
    // 准备初始状态 a=1, b=1, c_in=0
    // q[0]为a, q[1]为b, q[2]为c_in, q[3]为c_out辅助比特
    X(q[0]);
    X(q[1]);
    
    // 步骤 2: 计算进位输出 a AND b -> q[3]
    Toffoli(q[0], q[1], q[3]);
    
    // 步骤 3: 计算半加和 a XOR b -> q[1]
    CNOT(q[0], q[1]);
    
    // 步骤 4: 计算进位 c_in AND (a XOR b) -> q[3]
    Toffoli(q[2], q[1], q[3]);
    
    // 步骤 5: 计算最终和位 (a XOR b) XOR c_in -> q[1]
    CNOT(q[2], q[1]);
    
    // 此时量子态应为 |1001>
    // q[1]=0 (和位), q[3]=1 (进位输出)
}
```
上述代码严格对应我们手动追踪的数学演化过程，展示了如何利用基础的量子逻辑门构建复杂的算术运算。
