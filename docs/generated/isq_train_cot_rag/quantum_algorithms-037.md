# ISQ training COT RAG corpus: quantum_algorithms shard 37

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4261

- task_id: `isqTrain/4261`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4264`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;

// Triangle (K3) graph state
qbit q[3];

procedure main() {
    // Hadamard on all qubits: create |+>|+>|+>
    H(q[0]); H(q[1]); H(q[2]);
    // CZ for all edges in the triangle
    // Edge (0,1)
    CZ(q[0], q[1]);
    // Edge (1,2)
    CZ(q[1], q[2]);
    // Edge (0,2) completes the triangle
    CZ(q[0], q[2]);
    // Measure in computational (Z) basis
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the isQ program:**
    *   Initialization: 3 qubits, all at |000>.
    *   `H(q[0]); H(q[1]); H(q[2]);` -> Transforms |000> to |+>|+>|+> = 1/sqrt(8) sum over all 3-bit strings.
    *   `CZ(q[0], q[1]); CZ(q[1], q[2]); CZ(q[0], q[2]);` -> Applies CZ gates to form a triangle (K3) graph state. The state is $\frac{1}{\sqrt{8}} \sum_{x \in \{0,1\}^3} (-1)^{x_0 x_1 + x_1 x_2 + x_0 x_2} |x\rangle$.
    *   `H(q[0]); Z(q[0]); H(q[0]);` -> This sequence is HZH. Since $HZH = X$, this applies an $X$ gate to qubit 0.
    *   `M(q[0]); M(q[1]); M(q[2]);` -> Measurement in the Z basis.

2.  **Trace the state evolution:**
    *   Initial: $|000\rangle$
    *   After H's: $|+++\rangle = \frac{1}{\sqrt{2}}(|0\rangle+|1\rangle)^{\otimes 3} = \frac{1}{\sqrt{8}}(|000\rangle + |001\rangle + |010\rangle + \dots + |111\rangle)$
    *   After CZ(0,1), CZ(1,2), CZ(0,2): Graph state. Let's evaluate the amplitudes:
        *   000 -> +
        *   001 -> +
        *   010 -> +
        *   011 -> - (1 interaction: 1,2)
        *   100 -> +
        *   101 -> - (1 interaction: 0,2)
        *   110 -> - (1 interaction: 0,1)
        *   111 -> - (3 interactions: 01, 02, 12 -> odd parity)
        So state is $\frac{1}{\sqrt{8}}(|000\rangle + |001\rangle + |010\rangle - |011\rangle + |100\rangle - |101\rangle - |110\rangle - |111\rangle)$.
    *   Apply X to qubit 0: Flips the value of qubit 0 (0<->1).
        *   |000> -> |100>
        *   |001> -> |101>
        *   |010> -> |110>
        *   |011> -> |111>
        *   |100> -> |000>
        *   |101> -> |001>
        *   |110> -> |010>
        *   |111> -> |011>
        Wait, let's just rewrite the superposition after X on qubit 0:
        $\frac{1}{\sqrt{8}}(|100\rangle + |101\rangle + |110\rangle - |111\rangle + |000\rangle - |001\rangle - |010\rangle - |011\rangle)$
        Notice this is just a permutation of the basis states with a uniform amplitude magnitude of $1/\sqrt{8}$.
    *   Measurement: Since all 8 basis states have an amplitude magnitude of $1/\sqrt{8}$, their probabilities of being measured are all $|1/\sqrt{8}|^2 = 1/8 = 0.125$.

3.  **Draft the response:**
    *   Start with "## Circuit Analysis".
    *   Step 1: H gates create $|+++\rangle$.
    *   Step 2: CZ gates create the K3 graph state.
    *   Step 3: `H(q[0]); Z(q[0]); H(q[0]);` applies an X gate to qubit 0. This permutes the basis states (flips qubit 0).
    *   Step 4: Measurement yields equal probability for all 8 states.

4.  **Refine to be concise and precise:**
    *   1. Initial state $|000\rangle$ transformed to $|+++\rangle$ by H gates.
    *   2. CZ gates add a phase of $-1$ to basis states where an odd number of connected pairs are $|1\rangle$.
    *   3. `H; Z; H` on q[0] is equivalent to `X` on q[0], which swaps the amplit

### Reference answer

{'predicted_probs': {'000': 0.125, '001': 0.125, '010': 0.125, '011': 0.125, '100': 0.125, '101': 0.125, '110': 0.125, '111': 0.125}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|000>) = 0.1250, P(|001>) = 0.1250, P(|010>) = 0.1250, P(|011>) = 0.1250, P(|100>) = 0.1250, P(|101>) = 0.1250, P(|110>) = 0.1250, P(|111>) = 0.1250.'}

## isqTrain/718

- task_id: `isqTrain/718`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2632`

### Prompt

Write isQ code for the following quantum task: implements the ripple_carry_adder pattern using an alternative gate decomposition (CNOT -> H CZ H). The circuit must produce the same output as the standard decomposition.

### Chain-of-thought reasoning

Let me analyze this ripple carry adder circuit step by step.

The circuit has 5 qubits: q[0], q[1], q[2], q[3], q[4]

Initial state: |00000⟩

1. X(q[0]): q[0] → |1⟩, state = |10000⟩
2. X(q[2]): q[2] → |1⟩, state = |10100⟩

So we're encoding a = q[0]q[1] = 01 (a0=1, a1=0) and b = q[2]q[3] = 01 (b0=1, b1=0).

3. Toffoli(q[0], q[2], q[4]): When q[0]=1 AND q[2]=1, flip q[4]. Both are 1, so q[4] flips to 1.
   State = |10101⟩

4. CNOT decomposition for q[0] → q[2]:
   H(q[2]): |1⟩ → |−⟩ (Hadamard on |1⟩ gives (|0⟩ - |1⟩)/√2 = |−⟩)
   But wait, we need to track the full state.
   
   Let me be more careful. After Toffoli: |10101⟩ = |1⟩⊗|0⟩⊗|1⟩⊗|0⟩⊗|1⟩

   H(q[2]): H on |1⟩ = |−⟩
   State = |1⟩⊗|0⟩⊗|−⟩⊗|0⟩⊗|1⟩ = |10−01⟩

   CZ(q[0], q[2]): CZ applies Z to target when control is |1⟩
   Z|−⟩ = Z(|0⟩ - |1⟩)/√2 = (|0⟩ + |1⟩)/√2 = |+⟩
   
   Since q[0] is |1⟩, CZ applies Z to q[2], turning |−⟩ to |+⟩
   State = |1⟩⊗|0⟩⊗|+⟩⊗|0⟩⊗|1⟩ = |10+01⟩

   H(q[2]): H|+⟩ = |0⟩
   State = |10001⟩

   So this CNOT (H-CZ-H) flips q[2] from 1 to 0. That's CNOT with control q[0]=1, target q[2]: XOR operation. 1 XOR 1 = 0. Correct!

5. Now for q[1] → q[3] CNOT decomposition:
   State = |10001⟩
   
   H(q[3]): H on |0⟩ = |+⟩
   State = |100+1⟩ = |1⟩⊗|0⟩⊗|0⟩⊗|+⟩⊗|1⟩
   
   CZ(q[1], q[3]): q[1] = |0⟩, so no Z applied to q[3]
   State = |100+1⟩
   
   H(q[3]): H|+⟩ = |0⟩
   State = |10001⟩

   So q[3] stays 0. CNOT with control=0 doesn't flip. Correct!

6. Now for q[4] → q[3] CNOT decomposition:
   State = |10001⟩
   
   H(q[3]): H on |0⟩ = |+⟩
   State = |100+1⟩
   
   CZ(q[4], q[3]): q[4] = |1⟩, so Z applied to q[3]
   Z|+⟩ = |−⟩
   State = |100−1⟩
   
   H(q[3]): H|−⟩ = |1⟩
   State = |10011⟩

   So q[3] becomes 1. CNOT with control=1 flips target. 0 XOR 1 = 1. Correct!

Final state: |10011⟩

Measured qubits: q[2] = 0, q[3] = 1

The measurement bitstring: q[2] is measured first (higher bit), q[3] is measured second (lower bit).
So bitstring = q[2]q[3] = 01

Expected probabilities: {|01⟩: 1.0}

Let me verify the addition:
- a = 01 (binary) = 1
- b = 01 (binary) = 1  
- a + b = 2 = 10 (binary)
- sum bits: q[2] = sum0, q[3] = sum1
- Result: 01 → this represents sum = 01... wait

Actually, let me reconsider. The output is q[

## isqTrain/2016

- task_id: `isqTrain/2016`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `multi_controlled_logic`, `reversible_computing`, `superposition`
- source: `isq_train_cot`
- dataset_index: `682`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[3];
procedure main() {
    H(q[0]);
    H(q[1]);
    Toffoli(q[0], q[1], q[2]);
    M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit starts in the initial state |000>.
2. Applying H to q[0] and q[1] creates an equal superposition: 0.5(|000> + |010> + |100> + |110>) (with q[2] remaining |0>).
3. The Toffoli gate flips the target q[2] only when both controls q

### Reference answer

{'predicted_probs': {'0': 0.75, '1': 0.25}, 'explanation': 'Bilinear form x0*x1 in superposition: P(0)=0.75, P(1)=0.25.'}

## isqTrain/1191

- task_id: `isqTrain/1191`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_classical_vars`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_inv`, `isq_syntax_multi_register`, `phase_manipulation`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `86`

### Prompt

Help me write isQ code that implements a variant of the phase_estimation pattern using anc[3] -> anc[5]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

Let me analyze this phase estimation circuit carefully.

1. The goal is to implement a variant of quantum phase estimation using a 5-qubit ancilla register but only using 3 of them (anc[0], anc[1], anc[2]) for actual computation, with anc[3] and anc[4] left in |0⟩.

2. Qubits: anc[0..4] (5 ancilla) and target[0] (1 target). All 5 ancilla are measured, but only anc[0..2] participate in computation.

3. Step-by-step evolution:

Initial state: |00000⟩|0⟩

After X(target[0]): |00000⟩|1⟩

After H(anc[0]), H(anc[1]), H(anc[2]):
1/2√2 (|0⟩+|1⟩)(|0⟩+|1⟩)(|0⟩+|1⟩)|00⟩|1⟩
= 1/2√2 Σ_{k=0}^{7} |k⟩_3 |00⟩ |1⟩

The T gate has eigenstate |1⟩ with eigenvalue e^(iπ/4). So T|1⟩ = e^(iπ/4)|1⟩, T² = S with eigenvalue e^(iπ/2) = i, T⁴ = Z with eigenvalue e^(iπ) = -1.

After controlled-T on anc[0]: phase e^(iπ/4) when anc[0]=|1⟩
After controlled-S on anc[1]: phase e^(iπ/2) when anc[1]=|1⟩  
After controlled-Z on anc[2]: phase e^(iπ) when anc[2]=|1⟩

State becomes:
1/2√2 Σ_{k=0}^{7} e^(iπk/8) |k⟩_3 |00⟩ |1⟩

Wait, let me be more careful. The phase accumulated is:
- anc[0] contributes e^(iπ/4) when = 1
- anc[1] contributes e^(i2π/4) when = 1  
- anc[2] contributes e^(i4π/4) when = 1

So for computational basis state |b₂b₁b₀⟩, the phase is e^(iπ(b₀/4 + b₁/2 + b₂·1)) = e^(iπ·(4b₂ + 2b₁ + b₀)/4) = e^(iπk/4) where k = 4b₂ + 2b₁ + b₀.

Actually let me reconsider. The phase from T is π/4. So:
- anc[0] controls T: phase = π/4 when anc[0]=1
- anc[1] controls T²=S: phase = 2π/4 = π/2 when anc[1]=1
- anc[2] controls T⁴=Z: phase = 4π/4 = π when anc[2]=1

For |b₂b₁b₀⟩: total phase = b₀·π/4 + b₁·π/2 + b₂·π

We need to find which basis state the inverse QFT extracts.

In standard phase estimation, after the controlled unitaries we have:
1/2√2 Σ_k e^(2πiφk) |k⟩

where φ = 1/8 (since T has eigenvalue e^(iπ/4) = e^(2πi/8)).

So the state is:
1/2√2 Σ_{k=0}^{7} e^(2πik/8) |k⟩₃ |00⟩ |1⟩

= 1/2√2 Σ_{k=0}^{7} e^(2πik·φ) |k⟩₃ |00⟩ |1⟩ where φ = 1/8

With 3 bits, this is exactly represented: φ = 0.001 in binary.

The inverse QFT maps |k⟩₃ e^(2πiφk) → |φ·2³⟩₃ = |1⟩₃ = |001⟩₃.

Wait, but the QFT_inv_3 procedure swaps q[0] and q[2] at the beginning. Let me trace through the qubit ordering.

The ancilla register is anc[0], anc[1], anc[2]. The procedure qft_inv_3 takes q[0]=anc[0], q[1]=anc[1], q[2]=anc[2].

Standard QFT on qubits q[0] (LSB) to q[n-1] (MSB):
QFT|k⟩ = 1/√N Σ_j e^(2π

## isqTrain/3932

- task_id: `isqTrain/3932`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `1046`

### Prompt

Something is wrong with this isQ circuit. Identify the error and provide the corrected code.

```
import std;
// QAOA MaxCut p=1 on 4-node complete graph
// gamma=0.785, beta=0.393
qbit q[4];

procedure main() {
    // Superposition
    H(q[0]); H(q[1]); H(q[2]); H(q[3]);
    // Cost unitary
    // Edge (0,1)
    CNOT(q[0], q[1]);
    Rz(2.0 * 0.785, q[1]);
    CNOT(q[0], q[1]);
    // Edge (0,2)
    CNOT(q[0], q[2]);
    Rz(2.0 * 0.785, q[2]);
    CNOT(q[0], q[2]);
    // Edge (0,3)
    CNOT(q[0], q[3]);
    Rz(2.0 * 0.785, q[3]);
    CNOT(q[0], q[3]);
    // Edge (1,2)
    CNOT(q[1], q[2]);
    Rz(2.0 * 0.785, q[2]);
    CNOT(q[1], q[2]);
    // Edge (1,3)
    CNOT(q[1], q[3]);
    Rz(2.0 * 0.785, q[3]);
    CNOT(q[1], q[3]);
    // Edge (2,3)
    CNOT(q[3], q[2]);
    Rz(2.0 * 0.785, q[3]);
    CNOT(q[2], q[3]);
    // Mixer
    Rx(2.0 * 0.393, q[0]);
    Rx(2.0 * 0.393, q[1]);
    Rx(2.0 * 0.393, q[2]);
    Rx(2.0 * 0.393, q[3]);
    // Measure
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

``` (bug type: swapped qubits)

### Chain-of-thought reasoning

## Bug Analysis

1. **The bug**: In the Edge (2,3) cost unitary section, the first `CNOT(q[3], q[2])` has swapped arguments compared to the second `CNOT(q[2], q[3])`. The CNOT control/target pair must be consistent before and after the Rz gate. The first CNOT incorrectly uses q[3] as control and q[2] as target, while the second correctly uses q[2] as control and q[3] as target.

2. **The fix**: Change `CNOT(q[3], q[2])` to `CNOT(q[2], q[3])` so both CNOTs share the same control (q[2]) and target (q[3]).

3. **State evolution**: After H gates, all qubits are in |+⟩, giving |++++⟩. The cost unitary applies $e^{-i\gamma Z_i Z_j}$ per edge via the CNOT-Rz-CNOT pattern, which computes the parity into the target's phase. With consistent CNOT(q[2],q[3]), the ZZ interaction for edge (2,3) is correctly applied as $e^{-i\gamma Z_2 Z_3}$. The broken version applied a different, incorrect unitary due to mismatched control/target qubits. After all six cost unitaries and the Rx mixer rotations, the specific γ=π/4, β≈0.393 values yield a uniform superposition with equal probability 0.0625 for all 16 basis states.

## isqTrain/2642

- task_id: `isqTrain/2642`
- task_type: `code_equivalence`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `global_phase`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `953`

### Prompt

Will these two quantum programs produce identical measurement outcomes?

```isq
import std;
qbit q[3];

procedure main() {
    // Encode a = 2 (binary 10)
    X(q[1]);
    // Add constant 1: flip the LSB
    X(q[0]);
    // Now register = 3 (binary 11)
    // Overflow detection: set flag if both bits are 1 (value >= 3)
    Toffoli(q[0], q[1], q[2]);
    // Modular correction: subtract 3 by flipping both bits
    CNOT(q[2], q[0]);
    CNOT(q[2], q[1]);
    // Measure the 2-bit result: should be 0
    M(q[0]);
    M(q[1]);
}

```

vs.

```isq
import std;
qbit q[3];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    // Encode a = 2 (binary 10)
    X(q[1]);
    // Add constant 1: flip the LSB
    X(q[0]);
    // Now register = 3 (binary 11)
    // Overflow detection: set flag if both bits are 1 (value >= 3)
    Toffoli(q[0], q[1], q[2]);
    // Modular correction: subtract 3 by flipping both bits
    CNOT(q[2], q[0]);
    CNOT(q[2], q[1]);
    // Measure the 2-bit result: should be 0
    M(q[0]);
    M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** initializes the 3-qubit register to |000>. It applies X gates to q[1] and q[0] to encode the state |011>. It then computes the overflow using a Toffoli gate, resulting in |111>. Finally, it applies CNOTs from q[2] to q[0] and q[1] to subtract 3, yielding the final state |100>. Measurements on q[0] and q[1] will deterministically output 0.
2. **Program B** applies the exact same gate sequence as Program A, but includes an initial `GPhase(0.0)` operation.
3. The only difference between the programs is the `GPhase(0.0)` gate in Program B. This gate applies a global phase factor of $e^{i \cdot 0} = 1$, which acts as an identity operation.
4. Because a global phase of 0 does not change the quantum state, both programs result in the exact same final state |100> and produce identical measurement probability distributions (100% chance of measuring 0).
5. Verdict: Equivalent: True

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqExpand/algo/91

- task_id: `isqExpand/algo/91`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `grover`, `multi_solution`, `amplitude_amplification`, `bug_fix`
- source: `isq_expansion`
- dataset_index: `721`

### Prompt

下面的量子程序运行结果不对，请帮我debug：

```isq
import std;
qbit q[3];

procedure oracle() {
    X(q[0]); X(q[2]);
    ctrl ctrl Z(q[0], q[1], q[2]);
    X(q[0]); X(q[2]);
    X(q[1]);
    ctrl ctrl Z(q[0], q[1], q[2]);
    X(q[1]);
}

procedure diffusion() {
    H(q[0]); H(q[1]); H(q[2]);
    X(q[0]); X(q[1]); X(q[2]);
    ctrl ctrl Z(q[0], q[1], q[2]);
    X(q[0]); X(q[1]); X(q[2]);
    H(q[0]); H(q[1]); H(q[2]);
}

procedure main() {
    H(q[0]); H(q[1]); H(q[2]);
    oracle();
    diffusion();
    oracle();
    diffusion();
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Bug分析

### 问题
对于N=8, M=2的Grover搜索，Grover角为theta = arcsin(sqrt(2/8)) = pi/6。

最优迭代次数k使得(2k+1)*theta = pi/2：
(2k+1) * pi/6 = pi/2 -> 2k+1 = 3 -> k = 1

1次迭代后：P_total = sin^2(pi/2) = 1.0（完美！）
2次迭代后：P_total = sin^2(5*pi/6) = sin^2(150°) = 0.25

### Bug效果
Buggy代码执行了2次迭代，导致过度旋转。2次迭代后分布变为均匀（每个态概率0.125）。

### 修复
删除main()中的第二次 oracle(); diffusion(); 调用。

修复后：|010>(index 2) = 0.5, |101>(index 5) = 0.5, 其余 = 0.0

## isqQA/quantum_algorithms/86_hardware_limitations

- task_id: `isqQA/quantum_algorithms/86_hardware_limitations`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `hardware_limitations`, `algorithm`, `Deutsch算法原理`
- source: `qa_pipeline`
- dataset_index: `5673`

### Prompt

请解释Deutsch算法的基本原理，并分析在当前NISQ（含噪声中等规模量子）设备上运行该算法时，退相干现象是如何影响其计算结果准确性的？请提供一段使用isQ语言实现的Deutsch算法代码示例。

### Reference answer

Deutsch算法是量子计算中最基础的算法之一，旨在判断一个黑盒布尔函数 $f: \{0,1\} \to \{0,1\}$ 是常数函数（即 $f(0)=f(1)$）还是平衡函数（即 $f(0) \neq f(1)$）。在经典计算中，我们需要查询该黑盒两次才能得出结论，而借助量子叠加与干涉特性，Deutsch算法仅需查询一次。

其基本原理如下：算法初始化两个量子比特至 $|0\rangle |1\rangle$ 状态，随后对两者应用Hadamard门，使系统进入叠加态 $\frac{1}{2}(|0\rangle + |1\rangle)(|0\rangle - |1\rangle)$。接着，将黑盒函数 $U_f$ 作用于该叠加态。在量子线路中，$U_f$ 会根据 $f(x)$ 的值对目标比特施加相位反转，使得第一个量子比特的状态变为 $\pm \frac{1}{\sqrt{2}}(|0\rangle + (-1)^{f(0) \oplus f(1)}|1\rangle)$。最后，对第一个量子比特再次应用Hadamard门。如果 $f(0) \oplus f(1) = 0$（常数函数），干涉结果为 $|0\rangle$；如果 $f(0) \oplus f(1) = 1$（平衡函数），干涉结果为 $|1\rangle$。

然而，在当前的NISQ（Noisy Intermediate-Scale Quantum）设备上运行该算法时，硬件局限性尤其是退相干（Decoherence）现象会严重影响结果的准确性。量子比特非常脆弱，极易与周围环境发生耦合，导致能量弛豫（T1过程）和相位丢失（T2过程）。如果执行量子门操作和测量的总电路深度时间接近甚至超过量子比特的相干时间，原本完美的量子干涉图样就会被破坏，系统状态会坍缩或退化为经典的概率混合。这意味着在理论上应100%测得 $|1\rangle$ 的平衡函数场景下，NISQ设备上往往只能测得大约80%甚至更低的概率，导致计算出现误差。

以下是使用isQ语言编写的Deutsch算法代码示例，我们以平衡函数 $f(x) = x$ （对应CNOT门）作为黑盒：

```isQ
import std;

qbit q[2];

procedure main() {
    // 初始化状态，将第二个量子比特翻转为 |1>
    X(q[1]);

    // 对所有量子比特应用Hadamard门，创建叠加态
    H(q[0]);
    H(q[1]);

    // 模拟黑盒函数 U_f
    // 此处以平衡函数 f(x) = x 为例，等价于应用 CNOT 门
    // 控制比特为 q[0]，目标比特为 q[1]
    CNOT(q[0], q[1]);

    // 对第一个量子比特再次应用Hadamard门以产生干涉
    H(q[0]);

    // 测量第一个量子比特
    // 若为 1，则为平衡函数；若为 0，则为常数函数
    int result = M(q[0]);
    print(result);
}
```

## isqTrain/1420

- task_id: `isqTrain/1420`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `isq_syntax_ctrl_nctrl`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2878`

### Prompt

帮我写一个isQ程序：Apply the 3-qubit Quantum Fourier Transform to the input state |011> and measure all qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Apply 3-qubit QFT to input state |011⟩ (representing the integer 3).

2. **Qubits:** 3 qubits required (q[0], q[1], q[2]), all measured at the end.

3. **State Evolution:**
   - Initialize |000⟩, apply X to q[1] and q[2] → |011⟩
   - QFT circuit: H(q[2]) → (|010⟩ + |011⟩)/√2
   - ctrl S(q[1], q[2]) → (|010⟩ + i|011⟩)/√2
   - ctrl T(q[0], q[2]) → (|010⟩ + i|011⟩)/√2 (no phase since q[0]=|0⟩)
   - H(q[1]) → superposition spreading across 4 states
   - ctrl S(q[0], q[1]) → phases applied based on q[0]
   - H(q[0]) → creates full superposition
   - swap (three-CNOT decomposition)(q[0], q[2]) → reverses qubit order
   
   The final state is (1/√8)Σ_k exp(2πi·3k/8)|k⟩ for k=0,...,7

4. **Probabilities:** Since |ψ⟩ = (1/√8)Σ_k exp(2πi·3k/8)|k⟩, all amplitudes have magnitude 1/√8, giving equal probability 0.125 for each basis state |000⟩ through |111⟩.

## isqTrain/350

- task_id: `isqTrain/350`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `301`

### Prompt

I need an isQ program to implements the arithmetic_circuit pattern. Include explicit identity operations in the circuit (H-H pair before M(p[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

Let me analyze this isQ program step by step.

The program has:
- 1 control qubit `c[0]`
- 2 data qubits `p[0]`, `p[1]`

Let me trace through the circuit:

1. Initial state: |000⟩ (c[0], p[0], p[1])

2. H(c[0]): Creates superposition on control qubit
   State: (|000⟩ + |100⟩)/√2

3. ctrl INC(c[0], p[0], p[1]): Apply INC controlled by c[0]
   INC does: CNOT(p[0], p[1]), then X(p[0])
   So controlled INC means: if c[0]=|1⟩, apply INC to p[0], p[1]
   
   When c[0]=|0⟩: nothing happens to p qubits
   When c[0]=|1⟩: apply INC(p[0], p[1])
   
   INC(p[0], p[1]):
   - CNOT(p[0], p[1]): flips p[1] if p[0]=|1⟩ - but p[0]=|0⟩, so no change
   - X(p[0]): flips p[0] to |1⟩
   
   So for the |100⟩ component, INC gives |110⟩ (since p[0] was 0, CNOT does nothing, then X flips p[0])
   
   Wait, let me be more careful. The state before ctrl INC is:
   (|000⟩ + |100⟩)/√2
   
   ctrl INC with c[0] as control:
   - |000⟩ stays |000⟩ (control is 0)
   - |100⟩ becomes |110⟩ after INC (CNOT(0,0)→(0,0), then X(0)→1)
   
   State: (|000⟩ + |110⟩)/√2

4. nctrl DEC(c[0], p[0], p[1]): Apply DEC with negative control on c[0]
   Negative control means apply when c[0]=|0⟩
   
   DEC does: X(p[0]), then CNOT(p[0], p[1])
   
   For |000⟩ (c[0]=0, so nctrl activates):
   - X(p[0]): |010⟩
   - CNOT(p[0], p[1]): flips p[1] since p[0]=1 → |011⟩
   
   For |110⟩ (c[0]=1, so nctrl does NOT activate):
   - Stays |110⟩
   
   State: (|011⟩ + |110⟩)/√2

5. H(p[0]):
   For |011⟩: H on p[0] (which is 1) → (|011⟩ - |111⟩)/√2
   For |110⟩: H on p[0] (which is 1) → (|110⟩ - |010⟩)/√2
   
   State: (|011⟩ - |111⟩ + |110⟩ - |010⟩)/2

6. H(p[0]) again:
   For |011⟩: p[0]=1, H|1⟩ = (|0⟩-|1⟩)/√2 → (|011⟩ - |111⟩)/√2
   For |111⟩: p[0]=1, H|1⟩ = (|0⟩-|1⟩)/√2 → (|111⟩ - |011⟩)/√2
   For |110⟩: p[0]=1, H|1⟩ = (|0⟩-|1⟩)/√2 → (|110⟩ - |010⟩)/√2
   For |010⟩: p[0]=1, H|1⟩ = (|0⟩-|1⟩)/√2 → (|010⟩ - |110⟩)/√2
   
   Wait, this is H applied twice on the same qubit, so H-H = I (identity). This demonstrates gate cancellation!
   
   So the state after two H(p[0]) is the same as after step 4:
   (|011⟩ + |110⟩)/√2

7. Measurement of p[0] and p[1]:
   State is (|011⟩ + |110⟩)/√2
   
   In terms of measurement outcomes for p[0], p[1]:
   - |011⟩: c[0]=0, p[0]=1, p[1]=1 → measure p[0]=1, p[1]=1 → |11⟩
   - |110⟩: c[0]=1, p[0]=1, p[1
