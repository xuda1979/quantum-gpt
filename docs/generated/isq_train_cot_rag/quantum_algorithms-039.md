# ISQ training COT RAG corpus: quantum_algorithms shard 39

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/873

- task_id: `isqTrain/873`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `704`

### Prompt

实现以下量子计算任务（使用isQ）：implements the inner_product_mod2 pattern but with a different initial state preparation (flip q[[0, 2, 3]] -> q[4]).

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Compute the mod-2 inner product of two 2-bit vectors, starting with q[4] initialized to |1⟩ via X gate.

2. **Qubits**: 5 qubits (q[0..4]); only q[4] is measured.

3. **State evolution**:
   - |00000⟩ → X(q[4]) → |00001⟩
   - Toffoli(q[0], q[2], q[4]): controls q[0]=|0⟩, q[2]=|0⟩ → no flip → |00001⟩
   - Toffoli(q[1], q[3], q[4]): controls q[1]=|0⟩, q[3]=|0⟩ → no flip → |00001⟩

4. **Result**: Since input qubits q[0..3] remain |0⟩, both Toffoli gates are inactive; q[4] stays |1⟩. Measurement yields {|1⟩: 1.0}.

## isqTrain/2570

- task_id: `isqTrain/2570`
- task_type: `code_equivalence`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `global_phase`, `isq_syntax_deriving_gate`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `14`

### Prompt

Do these two isQ programs produce the same measurement results?

Program A:
```isq
import std;

qbit c[1];
qbit p[2];

procedure DEC(qbit p0, qbit p1) { 
    X(p0);
    CNOT(p0, p1);
} deriving gate

procedure INC(qbit p0, qbit p1) { 
    CNOT(p0, p1);
    X(p0);
} deriving gate

procedure main() {    
    H(c[0]);
    
    ctrl INC(c[0], p[0], p[1]);
    nctrl DEC(c[0], p[0], p[1]);
    
    M(p[0]); M(p[1]);
}

```

Program B:
```isq
import std;

qbit c[1];
qbit p[2];

procedure DEC(qbit p0, qbit p1) { 
    X(p0);
    CNOT(p0, p1);
} deriving gate

procedure INC(qbit p0, qbit p1) { 
    CNOT(p0, p1);
    X(p0);
} deriving gate

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);    
    H(c[0]);
    
    ctrl INC(c[0], p[0], p[1]);
    nctrl DEC(c[0], p[0], p[1]);
    
    M(p[0]); M(p[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis

1. **Program A** prepares `c[0]` in |+⟩ via H, then applies a controlled INC gate (on `c[0]` = |1⟩, INC = CNOT then X on p0) and a negative-controlled DEC gate (on `c[0]` = |0⟩, DEC = X on p0 then CNOT). Finally, it measures `p[0]` and `p[1]`.

2. **Program B** performs the exact same sequence but inserts `GPhase(0.0)` before the Hadamard gate.

3. **Key difference:** Program B contains the additional instruction `GPhase(0.0)`, which applies a global phase of $e^{i \cdot 0} = 1$ — the identity operation.

4. Since `GPhase(0.0)` is mathematically trivial, both programs produce identical quantum states before measurement, yielding identical measurement probability distributions.

Verdict: Yes

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqQA/quantum_algorithms/133_optimization_variant

- task_id: `isqQA/quantum_algorithms/133_optimization_variant`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `optimization_variant`, `algorithm`, `量子比较器`
- source: `qa_pipeline`
- dataset_index: `800`

### Prompt

在量子算法设计中，量子比较器是构建条件分支、搜索和排序算法的核心组件。然而，基础的量子比较器（如基于进位传播的线性结构）往往具有较深的电路深度和较高的T门消耗。为了适应NISQ时代或容错量子计算的需求，该算法有哪些重要的改进版本或变体？请从电路深度和辅助比特开销等维度详细分析这些优化变体的核心机制，并使用isQ语言展示一种利用并行结构及负控制逻辑实现的2-qubit量子比较器的优化代码示例。

### Reference answer

量子比较器的基础实现通常依赖于量子减法器，通过计算最高有效位（MSB）的借位状态来判断两个量子寄存器的大小关系。然而，这种串行进位结构会导致电路深度随量子比特数呈线性增长（O(n)），并且需要大量的辅助比特和TC0T0ffoli门，这在容错量子计算中会带来极高的魔法状态蒸馏开销。为了解决这些瓶颈，研究人员提出了多种重要的优化变体：

1. 对数深度并行比较器
基于经典计算中超前进位加法器（Carry-Lookahead Adder）的思想，该变体将借位生成和传播过程并行化。通过构建前缀树结构，进位计算的时间复杂度从线性降至对数级（O(log n)）。虽然这种变体可能略微增加量子门的绝对数量，但大幅降低了电路深度，极大地缩短了量子态的相干时间要求，非常适合深度敏感的量子硬件。

2. 零辅助比特比较器
此类变体通过相对相位Tarfalgar效应或巧妙利用量子门的可逆性，在不引入额外辅助量子比特的情况下完成比较。它通常基于多控制非门和相位逻辑的直接综合，减少了量子资源的占用宽度，为物理比特数受限的NISQ设备提供了可行的方案。

3. 基于量子傅里叶变换（QFT）的比较器
该变体不直接计算算术减法，而是利用QFT将整数映射到相位空间。通过对两个目标寄存器施加不同方向的相位旋转，将其差值转化为可测量的相对相位。这种结构与其他基于QFT的算术模块（如量子乘法器）高度契合，能够有效减少模块间状态转换的退相干风险。

下面是一个使用isQ语言编写的2-qubit量子比较器优化示例。该代码摒弃了传统的复杂减法器结构，直接通过多控制门和负控制逻辑并行判断高低位的大小关系，并且采用了延迟测量和逆计算技术清理辅助比特，体现了深度与宽度的平衡优化：

import std;

qbit a[2];
qbit b[2];
qbit anc[1];
qbit out[1];

procedure main() {
    // 假设对a和b进行了某种状态准备，例如叠加态或特定二进制态
    // 初始化测试输入 a = 2 (二进制10), b = 1 (二进制01)
    X(a[1]);
    X(b[0]);

    // 第一步：处理最高位(MSB) a[1] 和 b[1] 的比较
    // 如果 a[1]=1 且 b[1]=0，则直接可以确定 a > b，翻转输出比特
    nctrl @[b[1]] ctrl @[a[1]] X(out[0]);

    // 第二步：判断最高位是否相等 (a[1] == b[1])
    // 利用辅助比特 anc[0] 存储 XOR 结果，若相等则为0，反之为1
    CNOT(a[1], anc[0]);
    CNOT(b[1], anc[0]);
    // 为了便于控制，我们取反使得相等时 anc[0]=1
    X(anc[0]);

    // 第三步：在最高位相等的控制下，比较最低位 a[0] 和 b[0]
    // 如果 anc[0]=1 (高位相等)，且 a[0]=1, b[0]=0，翻转输出比特
    nctrl @[b[0]] ctrl @[a[0]] ctrl @[anc[0]] X(out[0]);

    // 此时 out[0] 即存储了 a > b 的布尔结果
    // 可以在此处进行基于比较结果的后续量子操作
    // ...

    // 第四步：逆计算 擦除辅助比特的纠缠，恢复为 |0⟩
    X(anc[0]);
    CNOT(b[1], anc[0]);
    CNOT(a[1], anc[0]);
    
    // 逆操作测试输入，恢复计算基底
    X(b[0]);
    X(a[1]);
}

## isqTrain/3626

- task_id: `isqTrain/3626`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1458`

### Prompt

Create an isQ quantum circuit that the 3-qubit Quantum Fourier Transform (QFT) applied to the input state |001>. The circuit should:
1. Prepare the input state by applying X gates where needed
2. Apply the QFT using Hadamard and controlled-Rz gates
3. Include the final bit-reversal swaps
4. Measure all 3 qubits

### Chain-of-thought reasoning

The user wants a reasoning section for a 3-qubit QFT applied to |001>.

Let me trace through the circuit:

1. Initialize |000>, apply X(q[2]) to get |001>

2. QFT stage for qubit 0:
   - H(q[0]): |001> → (|001> + |101>)/√2
   - ctrl Rz(π/2, q[1], q[0]): Since q[1]=0, no phase applied → (|001> + |101>)/√2
   - ctrl Rz(π/4, q[2], q[0]): When q[2]=1 and q[0]=1, apply phase e^(iπ/4). |101> gets phase → (|001> + e^(iπ/4)|101>)/√2

Wait, let me reconsider the QFT circuit structure. In QFT, the stages work as follows:

For a 3-qubit QFT on qubits q[0], q[1], q[2]:

Stage for qubit 0 (least significant):
- H on q[0]
- CRz(π/2) from q[1] to q[0] (controlled rotation Rz(2π/2²) = Rz(π/2))
- CRz(π/4) from q[2] to q[0] (controlled rotation Rz(2π/2³) = Rz(π/4))

Stage for qubit 1:
- H on q[1]
- CRz(π/2) from q[2] to q[1]

Stage for qubit 2:
- H on q[2]

Then swap q[0] and q[2].

Starting state: |001> = |q[2]q[1]q[0]> = |1,0,0>

Wait, I need to be careful about qubit ordering. In the code, q[0] is the least significant bit, q[2] is the most significant.

So |001> means q[0]=1, q[1]=0, q[2]=0.

Let me trace through:

Initial: |0,0,1> (q[2], q[1], q[0])

X(q[2]) → |1,0,1>? No wait...

The comment says "Prepare input state |001>". If we interpret |001> as q[2]=0, q[1]=0, q[0]=1, then we apply X(q[0]). But the code applies X(q[2]).

Hmm, let me reconsider. In the code:
- X(q[2]) is applied to prepare |001>

This suggests that in the convention used, |001> might mean q[2]=0, q[1]=0, q[0]=1. But applying X(q[2]) would give q[2]=1, making it |101> in that convention.

OR the convention might be that |001> means the binary number 1, where q[2] is the least significant bit. In that case, q[2]=1, q[1]=0, q[0]=0, and X(q[2]) makes sense.

Actually, looking at the predicted output: equal probabilities across all 8 basis states. This is consistent with QFT of |1> on 3 qubits, which should give a uniform superposition with phases.

Wait, but if all measurement probabilities are equal (0.125 each), that makes sense because after QFT of any computational basis state, the magnitudes of all amplitudes are equal (they're all 1/√8 in magnitude, giving probability 1/8 each).

Let me verify: QFT|j⟩ = (1/√N) Σ_k e^{2πijk/N} |k⟩

For N=8 and j=1:
QFT|1⟩ = (1/√8) Σ_{k=0}^{7} e^{2πik/8} |k⟩

All amplitudes have magnitude 1/√8, so probabilities are all 1/8 = 0.125. ✓

Now let me trace through the circuit more carefully:

Convention: |q[2], q[1], q[0]>

X(q[2]) transforms |000> → |100> = |4⟩ in decimal

Wait, that would be j=4, not j=1.

Hmm, let me think about this differently. In the bit ordering for isQ:

If we think of the state as |q[0], q[1], q[2]⟩ and X(q[2]) flips q[2], then:
|000⟩ → |001⟩ (where the rightmost bit is q[2])

This

## isqTrain/85

- task_id: `isqTrain/85`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `reversible_computing`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2214`

### Prompt

请用isQ语言编写一个量子电路：implements a variant of the amplitude_amplification pattern using q[2] -> q[4]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Implement amplitude amplification on a 4-qubit register to find the |11⟩ marked state on q[0]-q[1], leaving q[2]-q[3] in |0⟩.
2. Uses 4 qubits (q[0]-q[3]), all measured; q[2]-q[3] are never operated on and remain |0⟩.
3. Initial H gates on q[0], q[1] create the uniform superposition |ψ⟩ = (|00⟩+|01⟩+|10⟩+|11⟩)/2 ⊗ |00⟩.
4. The oracle `my_cz(q[0],q[1])` applies CZ (via H-CNOT-H), flipping the phase of |11⟩: state becomes (|00⟩+|01⟩+|10⟩-|11⟩)/2 ⊗ |00⟩.
5. The diffuser (H-X-my_cz-X-H on both q[0],q[1]) performs reflection about the mean: H returns to computational basis, X-my_cz-X applies a conditional phase on |00⟩, H returns to Hadamard basis.
6. After the diffuser, destructive interference cancels |00⟩,|01⟩,|10⟩ amplitudes while constructive interference amplifies |11⟩.
7. Final state is -|1100⟩ (global phase -1 irrelevant to measurement).
8. Expected probabilities: {|1100⟩: 1.0} since

## isqTrain/779

- task_id: `isqTrain/779`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `finite_field_arithmetic`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2532`

### Prompt

Implement the following in isQ: implements a variant of the gf2_multiplication pattern using q[3] -> q[5]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Implement GF(2) multiplication (AND) of two classical bits using a Toffoli gate, with an expanded 5-qubit register where extra qubits remain in |0>.

2. **Qubits:** 5 qubits (q[0]-q[4]); measuring q[2], q[3], q[4] (3 qubits measured).

3. **State evolution:**
   - Initial: |00000⟩
   - After X(q[0]): |10000⟩
   - After X(q[1]): |11000⟩
   - After Toffoli(q[0], q[1], q[2]): |11100⟩ (both controls are |1⟩, so target q[2] flips to |1⟩)

4. **Expected probabilities:** The Toffoli computes AND(1,1) = 1, placing q[2] in |1⟩. Qubits q[3] and q[4] are untouched and remain |0⟩. Measuring q[2] (MSB), q[3], q[4] yields bitstring |100⟩ with probability 1.0, since all states are computational basis states with no superposition.

## isqExpand/algo/122

- task_id: `isqExpand/algo/122`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `entanglement`
- source: `isq_expansion`
- dataset_index: `5457`

### Prompt

请用isQ语言编写一个量子电路：implementing one round of QAOA for a weighted 3-qubit MaxCut problem. The graph is a triangle with edge weights: w(q0,q1)=1, w(q0,q2)=2, w(q1,q2)=1. Use gamma=pi/3 and beta=pi/6. Start with H on all qubits. Cost layer: for each edge (i,j) with weight w, apply CNOT(qi,qj), Rz(2*gamma*w, qj), CNOT(qi,qj). Edge (0,1): Rz(2*pi/3, q[1]). Edge (0,2): Rz(4*pi/3, q[2]). Edge (1,2): Rz(2*pi/3, q[2]). Mixer layer: Rx(2*beta, q[i]) = Rx(pi/3, q[i]) on each qubit. Note: isQ uses Rz(angle, qubit) syntax. Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: QAOA for weighted MaxCut on a triangle.

Cost layer: CNOT-Rz-CNOT for each edge, Rz angle = 2*gamma*weight.
  (0,1,w=1): Rz(2*pi/3 ~ 2.0944)
  (0,2,w=2): Rz(4*pi/3 ~ 4.1888)
  (1,2,w=1): Rz(2*pi/3 ~ 2.0944)

Mixer: Rx(pi/3 ~ 1.0472) on each.

The optimal MaxCut separates vertex 0 from {1,2} (cut value = 3).
QAOA concentrates on |010> and |101>: P ~ 0.477 each.

## isqTrain/3573

- task_id: `isqTrain/3573`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `entanglement`, `basis_change`, `ancilla_usage`, `isq_syntax_arrays`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `5219`

### Prompt

Fix the bug in the following isQ program.

Bug description: Wrong CNOT direction

The program should Shor 9-qubit code encode+decode |1_L>.

### Chain-of-thought reasoning

## Bug Analysis

1. **What the bug is:** In the bit-flip encoding for block 1, the line `CNOT(q[1], q[0])` has the control and target reversed. The block leader q[0] (holding |1>) should control q[1] (in |0>), not vice versa.

2. **What the fix is:** Change `CNOT(q[1], q[0])` to `CNOT(q[0], q[1])`. The fixed code correctly uses q[0] as control to propagate the bit-flip encoding to q[1].

3. **State evolution (corrected):**
   - `X(q[0])`: |0>^9 → |1>|0>^8
   - Phase-flip CNOTs: |111>|0>^6
   - Hadamards on leaders: (|+>|+>|+>)|0>^6
   - Bit-flip CNOTs (block 1): `CNOT(q[0],q[1])` copies |+> to q[1], then `CNOT(q[0],q[2])` copies to q[2], yielding |+++>|+++>|+++>
   - Blocks 2,3 similarly encode to complete |1_L>
   - Decoding is the exact inverse of encoding, recovering |1>|0>^8
   - Measurement confirms: |10000000> with probability 1.0

## isqTrain/788

- task_id: `isqTrain/788`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `finite_field_arithmetic`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2019`

### Prompt

Implement the following in isQ: implements the gf2_multiplication pattern but with a different initial state preparation (flip q[[0, 1, 2]] -> q[4]).

### Chain-of-thought reasoning

The user wants to implement a gf2_multiplication pattern but with a different initial state preparation.
The implementation prepares the initial state by applying X to q[4].
The prompt asks to "flip q[[0, 1, 2]] -> q[4]". Wait, The implementation says `X(q[4]);` corresponds to setting a(x) = 1+x. If I change the initial state preparation to `q[[0, 1, 2]] -> q[4]`, it means the prompt might have meant something like applying X to q[0], q[1], q[2]. Let's look at the instruction: "Write an isQ program that implements the gf2_multiplication pattern but with a different initial state preparation (flip q[[0, 1, 2]] -> q[4])."
Wait, does it mean "flip q[0], q[1], q[2] instead of q[4]"?
Let's see The implementation:

If I change it to `X(q[0]); X(q[1]); X(q[2]);`, then:
- a(x) = 1+x (since X(q[0]), X(q[1]) means a0=1, a1=1)
- b(x) = 1 (since X(q[2]) means b0=1)
Wait, The implementation had `X(q[4])` but the comment says `Set polynomial a(x) = 1+x: a0=1, a1=1`. The implementation looks buggy or maybe the comment meant `a0=1, a1=1` but actually `X(q[4])` flips the output qubit directly? No, `X(q[4])` sets q[4] to 1. The circuit should:

If q[4] was initially |1>, then Toffoli(q[1], q[2], q[4]) would flip it to |0> because q[1] and q[2] are |0>.
Wait, if the prompt says "flip q[[0, 1, 2]] -> q[4]", maybe it meant "flip q[0], q[1], q[2]"?
"but with a different initial state preparation (flip q[[0, 1, 2]] -> q[4])" -> this notation `q[[0, 1, 2]] -> q[4]` might mean "flip q[0], q[1], q[2] instead of q[4]".
Let's assume the initial state is `|11100>` for q[0..4].
Then:
Toffoli(q[0], q[2], q[3]) -> q[0]=1, q[2]=1, so q[3] flips to 1. State is `|11110>`.
Toffoli(q[1], q[2], q[4]) -> q[1]=1, q[2]=1, so q[4] flips to 1. State is `|11111>`.
Measurement is M(q[3]), M(q[4]). Probabilities: {|11>: 1.0}.
Let me re-read the prompt.
Prompt: Write an isQ program that implements the gf2_multiplication pattern but with a different initial state preparation (flip q[[0, 1, 2]] -> q[4]).
Expected measurement probabilities: {|01>: 1.0}. Wait, the prompt says Expected measurement probabilities: {|01>: 1.0}. Wait, no it doesn't!
Ah! The prompt says:
circuit implementation (isQ code):
...
Expected measurement probabilities: {|01>: 1.0}
Wait, this expected measurement probability is for The implementation!
Wait, The circuit should:

And then `Toffoli(q[1], q[2], q[4])`. Since q[1] and q[2] are 0, Toffoli does nothing. So q[4] remains 1.
q[3] is 0. Toffoli(q[0], q[2], q[3]) does nothing. So q[3] remains 0.
Measurement: q[3]=0, q[4]=1. So {|01>: 1.0}.
This perfectly matches The implementation.
So the prompt is asking me to write a program for the *circuit implementation* and generate the reasoning for it!
Oh, "

## isqQA/quantum_algorithms/86_isq_implementation

- task_id: `isqQA/quantum_algorithms/86_isq_implementation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_implementation`, `algorithm`, `Deutsch算法原理`
- source: `qa_pipeline`
- dataset_index: `880`

### Prompt

请简述Deutsch算法的核心原理，并使用isQ语言编写一个完整的量子程序来实现该算法，以判断一个未知的黑盒函数是常数函数还是平衡函数，要求对代码进行逐行注释。

### Reference answer

<think>
首先，明确问题要求包含理论简述和isQ代码实现两个部分。

在理论推导上，从经典与量子的查询复杂度对比切入，突出量子并行性的优势。接着按量子线路的时间顺序梳理核心原理：第一步，初始化系统为 $|0\rangle|1\rangle$ 状态；第二步，对两个量子比特施加Hadamard门，使其进入等概率叠加态；第三步，引入黑盒酉算子 $U_f$，利用量子干涉与相位反冲效应，将函数特征转移到第一个量子比特的相对相位上；最后，对第一比特再次施加Hadamard门，消除叠加并放大相位差异。测量结果为0代表常数函数，为1代表平衡函数。

在代码实现上，根据isQ语言的语法规范进行映射。规划代码结构：声明量子比特、初始化、调用内置H门、通过矩阵或基本量子门模拟黑盒 $U_f$ 的两种情况、最后执行测量操作。同时规划逐行注释的位置，确保代码逻辑与上述理论步骤一一对应。
</think>

Deutsch算法是量子计算中用于展示量子并行性和干涉现象的基础算法。它的核心目标是判断一个黑盒函数 $f: \{0, 1\} \to \{0, 1\}$ 是常数函数（即 $f(0)=f(1)$）还是平衡函数（即 $f(0) \neq f(1)$）。在经典计算中，我们必须分别求值 $f(0)$ 和 $f(1)$，需要两次查询；而利用Deutsch算法，仅需一次量子查询即可得出结果，实现了指数级的加速。

该算法的原理如下：系统初始化为 $|0\rangle |1\rangle$。经过Hadamard门后，两个量子比特进入叠加态 $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$。接着，将其输入代表黑盒函数的酉算符 $U_f$。根据相位反冲效应，$U_f$ 的作用会将函数值转移到第一个量子比特的相对相位上，状态变为 $\pm \frac{1}{\sqrt{2}}(|0\rangle + (-1)^{f(0) \oplus f(1)}|1\rangle) \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$。最后，对第一个量子比特再次应用Hadamard门。如果 $f(0) \oplus f(1) = 0$（常数函数），干涉使得状态变为 $|0\rangle$；如果 $f(0) \oplus f(1) = 1$（平衡函数），干涉使得状态变为 $|1\rangle$。测量第一个比特即可直接得到结论。

在下面的isQ代码实现中，我们以 $f(x) = x$ （平衡函数）为例，此时 $U_f$ 等价于一个CNOT门。

import std;

qbit q[2]; // 全局声明两个量子比特，q[0]为输入比特，q[1]为辅助比特

procedure main() {
    // 第一步：初始化辅助比特
    // 系统默认初态为|00>，我们需要将辅助比特q[1]翻转为|1>，使得整体初态为|01>
    X(q[1]);

    // 第二步：施加Hadamard门，进入叠加态
    // 对q[0]作用H门，状态变为 (|0> + |1>)/sqrt(2)
    H(q[0]);
    // 对q[1]作用H门，状态变为 (|0> - |1>)/sqrt(2)，这是相位反冲的关键
    H(q[1]);

    // 第三步：执行黑盒操作
    // 这里假设黑盒函数为 f(x) = x，这是一个平衡函数。
    // 平衡函数f(x)=x对应的酉算符U_f在电路中即为CNOT门。
    // 控制端为q[0]，目标端为q[1]。
    CNOT(q[0], q[1]);

    // 第四步：对输入比特施加Hadamard门，引发量子干涉
    // 如果是常数函数，此步操作后q[0]将相长干涉为|0>；
    // 在本例（平衡函数）中，将相长干涉为|1>。
    H(q[0]);

    // 第五步：测量第一个量子比特
    // 测量结果存储在经典变量r中
    int r = M(q[0]);

    // 第六步：输出结果
    // 若r=0，代表黑盒为常数函数；若r=1，代表黑盒为平衡函数。
    // 对于本代码中的CNOT黑盒，预期打印结果为1。
    print r;
}
