# ISQ training COT RAG corpus: quantum_algorithms shard 116

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/algo/129

- task_id: `isqExpand/algo/129`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `basis_change`, `multi_controlled_logic`
- source: `isq_expansion`
- dataset_index: `2535`

### Prompt

Fix the bug in this quantum program:

```isq
import std;
qbit q[3];
procedure main() {
    X(q[2]);
    H(q[0]); H(q[1]);
    ctrl S(q[1], q[2]);
    CZ(q[0], q[2]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Bug Analysis
The IQFT is completely missing. Without it, phase information stays as relative phases, giving uniform [0.25,0.25,0.25,0.25].

Fix: Add 2-qubit IQFT + SWAP after the controlled operations.

S|1> = i|1> = e^{i*pi/2}|1>, phase = 1/4 -> k=1 -> |01>.
Expected: [0,1,0,0]

## isqTrain/2480

- task_id: `isqTrain/2480`
- task_type: `code_equivalence`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `global_phase`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3913`

### Prompt

比较这两个量子电路，它们的输出概率分布一样吗？

```isq
import std;
qbit q[2];

procedure main() {
    // target in |->
    X(q[1]); H(q[1]);
    // control in |+>
    H(q[0]);
    // CNOT
    CNOT(q[0], q[1]);
    // H on control
    H(q[0]);
    // Measure
    M(q[0]); M(q[1]);
}

```

```isq
import std;
qbit q[2];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    // target in |->
    X(q[1]); H(q[1]);
    // control in |+>
    H(q[0]);
    // CNOT
    CNOT(q[0], q[1]);
    // H on control
    H(q[0]);
    // Measure
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** prepares the control qubit in |+> and target in |->, applies a CNOT, and finally applies an H gate to the control before measuring both.
2. **Program B** performs the exact same sequence of operations but explicitly applies a `GPhase(0.0)` gate at the beginning.
3. The only difference is the `GPhase(0.0)` gate, which applies a global phase factor of $e^{i \cdot 0} = 1$. 
4. Because a global phase of 1 is mathematically equivalent to the identity operation, the overall quantum state remains completely unchanged.
5. Therefore, the measurement probability distributions for both programs are identical.
Verdict: Yes

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/3983

- task_id: `isqTrain/3983`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `2509`

### Prompt

Something is wrong with this isQ circuit. Identify the error and provide the corrected code.

```
import std;
// QAOA MaxCut p=1 on 3-node triangle graph
// gamma=0.785, beta=0.393
qbit q[3];

procedure main() {
    // Initial superposition
    H(q[0]); H(q[1]); H(q[2]);
    // Cost unitary U_C(gamma)
    // Edge (0,1): exp(-i*gamma*Z_i*Z_j)
    CNOT(q[0], q[1]);
    Rz(2.0 * 2.0 * 0.785, q[1]);
    CNOT(q[0], q[1]);
    // Edge (1,2): exp(-i*gamma*Z_i*Z_j)
    CNOT(q[1], q[2]);
    Rz(2.0 * 0.785, q[2]);
    CNOT(q[1], q[2]);
    // Edge (0,2): exp(-i*gamma*Z_i*Z_j)
    CNOT(q[0], q[2]);
    Rz(2.0 * 0.785, q[2]);
    CNOT(q[0], q[2]);
    // Mixer unitary U_M(beta)
    Rx(2.0 * 0.393, q[0]);
    Rx(2.0 * 0.393, q[1]);
    Rx(2.0 * 0.393, q[2]);
    // Measure
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: wrong parameter)

### Chain-of-thought reasoning

## Bug Analysis

1. **The bug** is in Edge (0,1)'s cost unitary: `Rz(2.0 * 2.0 * 0.785, q[1])` contains an extra multiplication by `2.0`, yielding angle `4γ` instead of `2γ`. The standard decomposition of exp(−iγ Z_i Z_j) is `CNOT; Rz(2γ); CNOT`. The other two edges correctly use `2.0 * 0.785`.

2. **The fix** changes `Rz(2.0 * 2.0 * 0.785, q[1])` to `Rz(2.0 * 0.785, q[1])`, making the rotation angle consistent with all other edges.

3. **State evolution (corrected):**
   - After H on all qubits: |+++⟩, an equal superposition over all 8 basis states.
   - **U_C(γ):** Each edge (0,1), (1,2), (0,2) applies `CNOT–Rz(2γ=1.57)–CNOT`, implementing exp(−iγZ_iZ_j). On the triangle graph, this phases basis states by −γ times the number of "cut" edges (disagreeing bit pairs). States |000⟩, |111⟩ (0 cuts) get no phase; single-bit-flip states (1 cut) get −γ; two-bit-flip states (2 cuts) get −2γ.
   - **U_M(β):** Rx(2β=0.786) on each qubit rotates around X, mixing computational basis states.
   - **Result:** Constructive interference favors |000⟩ and |111⟩ (each ~0.313), while the six single/two-bit-flip states each get ~0.062, matching the predicted output.

## isqTrain/2868

- task_id: `isqTrain/2868`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `isq_syntax_multi_register`, `measurement_order`, `multi_controlled_logic`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3742`

### Prompt

这段isQ代码有bug，帮我找出并修复：

```isq
import std;
qbit q[3];
// CZ gate with Hadamard
procedure main() {
    H(q[0]);
    H(q[1]);
    CZ(q[0], q[1]);
    H(q[2]);
    M(q[0]);
    M(q[0]);
    M(q[2]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **The Bug**: The second measurement operation `M(q[0])` is incorrectly measuring qubit 0 again, leaving qubit 1 unmeasured. 
2. **The Fix**: Change the second `M(q[0])` to `M(q[1])` so that all three distinct qubits (q[0], q[1], and q[2]) are measured exactly once.
3. **State Evolution**: Initially $|000\rangle$. The `H` gates put $q_0, q_1, q_2$ into superpositions, forming $(|00\rangle + |01\rangle + |10\rangle + |11\rangle) \otimes (|0\rangle + |1\rangle)/\sqrt{8}$. The `CZ(q[0], q[1])` phase-shifts the $|11\rangle$ component of the first two qubits, resulting in a state $(|00\rangle + |01\rangle + |10\rangle - |11\rangle) \otimes (|0\rangle + |1\rangle)/\sqrt{8}$. When expanded, this yields an equal probability of $0.125$ for all 3-qubit basis states.

## isqTrain/111

- task_id: `isqTrain/111`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `276`

### Prompt

Implement the following in isQ: implements the qft_subcircuit pattern but with a different initial state preparation (flip q[[1]] -> q[0]).

### Chain-of-thought reasoning

The user wants to understand the provided isQ code that implements a QFT subcircuit pattern.

**Goal:** Implement a qft_subcircuit pattern, prepare an initial state by flipping q[0] instead of q[1], and explain the circuit's state evolution.

**Circuit breakdown:**
1. Initial state: |00>
2. `X(q[0])`: Flips q[0]. State becomes |10>
3. `H(q[0])`: Hadamard on q[0]. State becomes (|00> - |10>)/sqrt(2) or (|0> - |1>)_0 ⊗ |0>_1 / sqrt(2)
4. `ctrl my_z(q[0], q[1])`: Controlled-Z gate. Z is applied to q[1] if q[0] is |1>. Wait, the code says `ctrl my_z(q[0], q[1])`. In isQ, `ctrl Gate(control, target)` or `ctrl @[c] Gate(target)`? The syntax provided in the prompt says: `ctrl @[c1, c2] Gate(target);`. But the code says `ctrl my_z(q[0], q[1])`. Wait, the code has `ctrl my_z(q[0], q[1])`. If `my_z` takes one argument, `ctrl my_z(q[0], q[1])` implies q[0] is control and q[1] is target.
Let's trace `ctrl my_z(q[0], q[1])`:
State before: (|00> - |10>)/sqrt(2)
Apply CZ(0,1): |00> remains |00>, |10> becomes -|10> because Z applies to q[1] when q[0] is 1. Wait, Z(q[1]) on |0> is |0>. Wait, Z on |0> is |0>. Z on |1> is -|1>.
Ah, Z on |0> is +|0>.
So |00> -> |00>
|10> -> |10> (since q[1] is |0>, Z doesn't add a minus sign).
Wait, Z|0> = |0>, Z|1> = -|1>.
Since q[1] is |0>, applying Z to it does nothing.
So state remains (|00> - |10>)/sqrt(2).
Wait! The predicted output {|1>: 1.0}.
Let me re-evaluate.
Wait, if predicted output is |1> with probability 1.0, the state before H must be |10>.
Let's check `ctrl my_z`.
If `ctrl` makes it a controlled gate, `my_z` takes one qubit.
State before: (|00> - |10>)/sqrt(2) = (|0> - |1>)⊗|0>/sqrt(2).
Apply CZ(0,1). CZ applies Z to q[1] if q[0] is |1>. But q[1] is |0>. So CZ does nothing.
Wait, let's look at standard QPE.
If U = Z. Eigenstate of Z is |0> or |1>. Here q[1] is |0>. Eigenvalue is +1.
So phase is 0. QPE on phase 0 gives |0>.
Why is expected measurement probability {|1>: 1.0}?
Wait, in isQ, if I have `procedure my_z(qbit a) { Z(a); }`, and I call `ctrl my_z(q[0], q[1])`.
Does this mean q[0] is the target and q[1] is the control?
No, standard isQ `ctrl` syntax for custom gates:
`ctrl my_z(q[0], q[1])` means q[0] is the control, q[1] is the target of `my_z`.
Wait, let's read isQ documentation or infer from the prompt.
"Two-qubit gates: CNOT(control, target)"
If `my_z` has parameter `a`, then `ctrl my_z(c, a)` -> `c` is control, `a` is target.
So `ctrl my_z(q[0], q[1])` -> q[0] is control, q[1] is target.
But Z on |0> does nothing!
Let me check The implementation again.

    X(q[0]); // state: |10>
    H(q[0]); // state: |00> + |10> ? No, X|0> = |1>, H|1> = |0> - |1>. So state is |10> - |00> ? Wait.
    // |10> -> (|0> - |1>) ⊗

## isqTrain/4854

- task_id: `isqTrain/4854`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `boolean_logic`
- source: `isq_train_cot`
- dataset_index: `2338`

### Prompt

Write an isQ program that for HLF on 3 qubits with star graph (edges 0-1, 0-2). Measure.

### Chain-of-thought reasoning

tep-by-step reasoning for the HLF (Hadamard Layer Function) on 3 qubits with star graph.

Let me trace through the circuit:

1. Initial state: |000>

2. First Hadamard layer: H on all 3 qubits
   |000> → H⊗3 → |+++> = (|000> + |001> + |010> + |011> + |100> + |101> + |110> + |111>)/2√2

3. Star graph CZ gates: CZ(q[0], q[1]) and CZ(q[0], q[2])
   This applies a phase of -1 when both qubits are |1>
   
   CZ(0,1) applies -1 phase when q[0]=1 AND q[1]=1
   CZ(0,2) applies -1 phase when q[0]=1 AND q[2]=1
   
   So states that get a phase flip:
   - |110>: q[0]=1, q[1]=1 → -1 from CZ(0,1)
   - |101>: q[0]=1, q[2]=1 → -1 from CZ(0,2)
   - |111>: q[0]=1, q[1]=1, q[2]=1 → -1 from both, so phase = (-1)×(-1) = +1
   
   After CZ gates:
   (|000> + |001> + |010> + |011> + |100> - |101> - |110> + |111>)/2√2

4. Second Hadamard layer: H on all 3 qubits
   
   Let me compute this carefully. H⊗3 applied to each basis state:
   
   H⊗3|000> = |+++> = (|0>+|1>)(|0>+|1>)(|0>+|1>)/2√2
   H⊗3|001> = (|0>+|1>)(|0>+|1>)(|0>-|1>)/2√2
   H⊗3|010> = (|0>+|1>)(|0>-|1>)(|0>+|1>)/2√2
   H⊗3|011> = (|0>+|1>)(|0>-|1>)(|0>-|1>)/2√2
   H⊗3|100> = (|0>-|1>)(|0>+|1>)(|0>+|1>)/2√2
   H⊗3|101> = (|0>-|1>)(|0>+|1>)(|0>-|1>)/2√2
   H⊗3|110> = (|0>-|1>)(|0>-|1>)(|0>+|1>)/2√2
   H⊗3|111> = (|0>-|1>)(|0>-|1>)(|0>-|1>)/2√2

   Combining:
   State = (1/2√2)[|000>+|001>+|010>+|011>+|100>+|101>+|110>+|111>
                   +|000>-|001>+|010>-|011>+|100>-|101>+|110>-|111>
                   +|000>+|001>-|010>-|011>+|100>+|101>-|110>-|111>
                   +|000>-|001>-|010>+|011>+|100>-|101>-|110>+|111>
                   +|000>+|001>+|010>+|011>-|100>-|101>-|110>-|111>
                   -(|000>-|001>+|010>-|011>-|100>+|101>-|110>+|111>)
                   -(|000>+|001>-|010>-|011>-|100>-|101>+|110>+|111>)
                   +(|000>-|001>-|010>+|011>-|100>+|101>+|110>-|111>)]

   Let me collect coefficients for each basis state:
   
   Coefficient of |000>: 1+1+1+1+1-1-1+1 = 4
   Coefficient of |001>: 1-1+1-1+1+1-1-1 = 0
   Coefficient of |010>: 1+1-1-1+1-1-1+1 = 0
   Coefficient of |011>: 1-1-1+1+1+1+1-1 = 2
   Coefficient of |100>: 1+1+1+1-1+1+1

## isqQA/quantum_algorithms/124_optimization_variant

- task_id: `isqQA/quantum_algorithms/124_optimization_variant`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `optimization_variant`, `algorithm`, `量子随机数生成`
- source: `qa_pipeline`
- dataset_index: `5571`

### Prompt

量子随机数生成（QRNG）的基础实现通常是对处于叠加态的量子比特进行测量。为了提升随机数生成的速率、效率以及安全性，该算法有哪些重要的改进版本或变体？请解释这些变体的原理，并使用isQ语言展示一个并行生成多比特随机数的量子线路代码。

### Reference answer

<...>量子随机数生成（QRNG）的基础算法是利用Hadamard门将量子比特从初始态|0>转化为均匀叠加态 (|0> + |1>)/√2，随后进行测量，以50%的概率坍缩至|0>或|1>，从而生成1个比特的真随机数。随着量子信息技术的发展，为了提升随机数生成的速率、效率以及对抗黑客攻击的安全性，研究者们提出了多种重要的改进版本与变体：

1. **设备无关量子随机数生成**：
基础QRNG的安全性高度依赖于对物理设备的精确建模和信任。DI-QRNG变体打破了这一限制，它不依赖于设备的内部工作原理。该变体通过在两个空间分离的量子设备之间进行贝尔测试，只要测试结果违背了贝尔不等式，就能从原理上保证随机性的真实性，有效抵御侧信道攻击和设备后门。

2. **连续变量量子随机数生成**：
基础离散变量QRNG每次测量只能提取单个比特，生成速率受限。CV-QRNG变体利用相干态等连续变量的量子态进行操作，通过平衡零拍探测器测量光场正交分量的量子真空涨落。由于连续变量包含更丰富的状态信息，这种变体能够以极高的带宽实现随机数提取，极大提升了随机数生成的比特率，是当前高速量子密钥分发系统的核心组件。

3. **基于量子随机游走的QRNG**：
相较于单比特的简单测量，量子随机游走利用粒子的相干性和干涉效应，在特定的拓扑结构或图上进行演化。通过优化初始态和转移算子，演化后的概率分布可以呈现出高度复杂的均匀或混沌分布。这种变体能够在一次测量中提取多个随机比特，显著提高了量子态资源的利用率。

在实际应用中，为了提升基础QRNG的吞吐量，最直接的算法优化变体是**多通道并行扩展**，即同时操作多个量子比特生成随机序列。下面是使用isQ语言编写的并行8比特量子随机数生成代码：

```isq
import std;

// 全局声明8个量子比特用于并行随机数生成
qbit q[8];

procedure main() {
    // 对每个量子比特施加Hadamard门，使其进入均匀叠加态
    for i in 0:8 {
        H(q[i]);
    }
    
    // 测量所有量子比特以提取随机数
    // 测量结果将坍缩为随机的0或1，从而一次性产生8位随机比特串
    for i in 0:8 {
        M(q[i]);
    }
}
```
上述代码展示了如何通过简单的循环并行化生成多位随机数。在真实的硬件体系中，这类并行生成结果通常会配合经典后处理算法（如Toeplitz矩阵哈希提取），以消除实际硬件噪声带来的微小偏置，输出高质量的标准随机数序列。</...>

## isqExpand/algo/115

- task_id: `isqExpand/algo/115`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `reversible_computing`, `multi_controlled_logic`, `ancilla_usage`
- source: `isq_expansion`
- dataset_index: `1367`

### Prompt

Create an isQ quantum circuit that implementing a 2-bit quantum ripple-carry adder. Compute A + B where A=11 (binary, i.e. 3) and B=01 (binary, i.e. 1). Use q[0]=A0, q[1]=A1, q[2]=B0, q[3]=B1 (sum computed in-place), q[4]=internal carry, q[5]=Cout (final carry-out). Initialize: X(q[0]), X(q[1]), X(q[2]) for A=11, B=01. Bit 0 stage: Toffoli(q[0],q[2],q[4]) first (carry BEFORE sum), then CNOT(q[0],q[2]) for S0. Bit 1 stage: three Toffolis for carry-out, then two CNOTs for S1. Measure all 6 qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: 2-bit ripple-carry adder for A=11(3) + B=01(1) = 100(4).

Bit 0: carry first, then sum.
  Toffoli(A0,B0,carry): q[4] = 1 AND 1 = 1
  CNOT(A0,B0): q[2] = 1 XOR 1 = 0 (S0=0)

Bit 1: three Toffolis for Cout, two CNOTs for S1.
  Result: S1=0, Cout=1

Final: q=[1,1,0,0,1,1], index = 32+16+0+0+2+1 = 51.

## isqTrain/2511

- task_id: `isqTrain/2511`
- task_type: `code_equivalence`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `global_phase`, `isq_syntax_deriving_gate`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `4706`

### Prompt

Compare these two isQ programs. Do they give the same probability distribution?

First program:
```isq
import std;
qbit q[3];
procedure my_z(qbit a) {
    Z(a);
} deriving gate
procedure main() {
    X(q[0]); H(q[0]); // State = |->
    
    H(q[1]); CNOT(q[1], q[2]); // EPR
    
    CNOT(q[0], q[1]); H(q[0]); // Alice
    
    CNOT(q[1], q[2]); ctrl my_z(q[0], q[2]); // Bob
    
    H(q[2]); // Bob verifies by changing |-> to |1>
    M(q[0]); M(q[1]); M(q[2]);
}

```

Second program:
```isq
import std;
qbit q[3];
procedure my_z(qbit a) {
    Z(a);
} deriving gate
procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    X(q[0]); H(q[0]); // State = |->
    
    H(q[1]); CNOT(q[1], q[2]); // EPR
    
    CNOT(q[0], q[1]); H(q[0]); // Alice
    
    CNOT(q[1], q[2]); ctrl my_z(q[0], q[2]); // Bob
    
    H(q[2]); // Bob verifies by changing |-> to |1>
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** applies a series of gates that perform quantum teleportation of the state |-> from qubit q[0] to q[2], followed by measurements of all three qubits.
2. **Program B** applies the exact same sequence of gates and operations for the quantum teleportation protocol.
3. The only difference between the two programs is the addition of the `GPhase(0.0)` gate at the beginning of Program B.
4. `GPhase(0.0)` applies a global phase factor of $e^{i0} = 1$, which is mathematically trivial and does not alter the quantum state vector or the resulting measurement probability distribution.
5. **Verdict**: Equivalent: True

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/3660

- task_id: `isqTrain/3660`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `1544`

### Prompt

Write isQ code for the following quantum task: 3-bit quantum phase estimation for phase angle 3*pi/4 (in multiples of 2π/8). Use 3 precision qubits, controlled-Rz rotations, and a 3-qubit inverse QFT. Measure all 4 qubits (3 precision + 1 eigenstate).

### Chain-of-thought reasoning

Let me analyze this quantum phase estimation circuit step by step.

Goal: Implement 3-bit QPE for phase angle 3π/4 (in multiples of 2π/8).

Qubits: 4 total - q[0], q[1], q[2] are precision qubits, q[3] is the eigenstate qubit.

Step-by-step:

1. **Initial state**: |0000⟩

2. **X(q[3])**: Prepare eigenstate |1⟩ on q[3]
   State: |0001⟩

3. **H(q[0]), H(q[1]), H(q[2])**: Hadamard on precision qubits
   State: |+++1⟩ = (1/2√2)(|0⟩+|1⟩)⊗(|0⟩+|1⟩)⊗(|0⟩+|1⟩)⊗|1⟩

4. **Controlled-Rz rotations**:
   - ctrl Rz(2π × 3/8 × 1, q[0], q[3]): applies phase e^(iπ×3/8) when q[0]=|1⟩
   - ctrl Rz(2π × 3/8 × 2, q[1], q[3]): applies phase e^(iπ×6/8) = e^(i3π/4) when q[1]=|1⟩
   - ctrl Rz(2π × 3/8 × 4, q[2], q[3]): applies phase e^(iπ×12/8) = e^(i3π/2) when q[2]=|1⟩

   After these operations, the state becomes:
   (1/2√2) Σ_{k=0}^{7} e^(2πi × 3k/8) |k⟩|1⟩
   
   where k is the 3-bit integer formed by q[2]q[1]q[0].
   
   Actually, let me be more careful. The phase for each computational basis state |k₂k₁k₀⟩ is:
   - If k₀=1: phase *= e^(i×3π/4)
   - If k₁=1: phase *= e^(i×3π/2)
   - If k₂=1: phase *= e^(i×3π) = e^(iπ) = -1
   
   Wait, let me recalculate. The Rz gate is Rz(θ) = exp(-iθZ/2). But in the context of controlled-Rz, when the control is |1⟩, it applies the rotation to the target.
   
   For an eigenstate |1⟩ of Z with eigenvalue -1:
   Rz(θ)|1⟩ = e^(-iθ/2)|1⟩ × (-1) → actually Rz(θ) = e^(-iθ/2)|0⟩⟨0| + e^(iθ/2)|1⟩⟨1|
   
   So Rz(θ)|1⟩ = e^(iθ/2)|1⟩

   For controlled-Rz(θ, control, target):
   When control is |1⟩ and target is |1⟩: phase = e^(iθ/2)
   
   For q[0]: θ = 2π × 3/8 = 3π/4, so phase when q[0]=|1⟩, q[3]=|1⟩: e^(i×3π/8)
   For q[1]: θ = 2π × 3/8 × 2 = 3π/2, so phase when q[1]=|1⟩, q[3]=|1⟩: e^(i×3π/4)
   For q[2]: θ = 2π × 3/8 × 4 = 3π, so phase when q[2]=|1⟩, q[3]=|1⟩: e^(i×3π/2)
   
   Total phase for |k₂k₁k₀⟩|1⟩: e^(i×3π/8×k₀) × e^(i×3π/4×k₁) × e^(i×3π/2×k₂)
   = e^(i×3π/8×(k₀ + 2k₁ + 4k₂))
   = e^(i×3π/8×k)
   where k = k₀ + 2k₁ + 4k₂ is the integer with k₀ as LSB.
   
   Wait, I need to be careful about the bit ordering. In the QPE circuit:
   - q[0] gets the least significant bit (2^0 power)
   - q[1] gets 2^1 power
