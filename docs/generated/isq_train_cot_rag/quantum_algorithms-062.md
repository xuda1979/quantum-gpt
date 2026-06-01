# ISQ training COT RAG corpus: quantum_algorithms shard 62

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/703

- task_id: `isqTrain/703`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `boolean_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3500`

### Prompt

Create an isQ quantum circuit that implements a variant of the integer_comparator pattern using q[3] -> q[5]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
**Goal**: Implement an integer comparator checking if a ≥ 2 using an expanded 5-qubit register, encoding a = 3 and storing the comparison result.

**Qubits**: 5 total (q[0]–q[4]); measuring q[2], q[3], q[4] (3 qubits, q[2] is MSB of output).

**State evolution**:
1. Initial: |00000⟩
2. X(q[0]): |10000⟩
3. X(q[1]): |11000⟩ — encodes a = 3 (binary 11 in q[0], q[1])
4. CNOT(q[1], q[2]): q[1]=|1⟩, so flip q[2] → |11100⟩ — MSB of a is set, so a ≥ 2 is TRUE
5. q[3], q[4] remain |0⟩ (ground state, unused)

**Expected probabilities**: Measuring q[2]=1, q[3]=0, q[4]=0 gives bitstring |100⟩ with probability 1.0, consistent with state |11100⟩.

## isqQA/quantum_algorithms/89_comparison

- task_id: `isqQA/quantum_algorithms/89_comparison`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `comparison`, `algorithm`, `DJ算法与经典查询复杂度对比`
- source: `qa_pipeline`
- dataset_index: `5608`

### Prompt

请对比分析Deutsch-Jozsa算法与经典确定性算法在解决函数性质判定问题时的查询复杂度差异，并深入探讨其在实际应用中的优缺点与适用场景。最后，请使用isQ语言编写一个判断2量子比特Deutsch-Jozsa问题的完整代码示例。

### Reference answer

<thinking>
1. 数学推导：
对于输入为 n 个比特的函数 f: {0,1}^n → {0,1}}，承诺其为常函数或平衡函数。
经典确定性算法：最坏情况下需要查询 2^(n-1) + 1 次才能确定。
量子Deutsch-Jozsa算法：
初始化状态为 |0⟩^⊗n|1⟩。
经过Hadamard门后状态为 ∑_x (1/√(2^n))|x⟩ (1/√2)(|0⟩ - |1⟩)。
经过Oracle U_f 作用后，状态变为 ∑_x ((-1)^f(x)/√(2^n))|x⟩ (1/√2)(|0⟩ - |1⟩)。
再次对前 n 个比特应用Hadamard门，利用公式 H^⊗n|x⟩ = (1/√(2^n)) ∑_z (-1)^{x·z}|z⟩，最终状态前n个比特的振幅为 ∑_z [ (1/2^n) ∑_x (-1)^{f(x) + x·z} ] |z⟩。
当测量前 n 个比特时，如果 f(x) 是常函数，幅度集中在 |0⟩^⊗n 上（即测量全为0）；如果是平衡函数，|0⟩^⊗n 态的幅度相互抵消为0。因此，仅需1次量子查询即可得出确定结论。

2. 代码逻辑：
设量子比特数组大小为 3，其中 q[0], q[1] 为输入，q[2] 为辅助比特。
- 初始化：X(q[2])。
- 叠加态：对所有比特施加 H 门。
- 模拟 Oracle：假设函数为 f(x) = x0 ⊕ x1，这是一个平衡函数。可以通过 CNOT(q[0], q[2]) 和 CNOT(q[1], q[2]) 实现。
- 干涉：对输入比特 q[0], q[1] 施加 H 门。
- 测量：测量 q[0], q[1]。因为 f 是平衡函数，干涉后测量结果必定不全为0（例如会得到 11）。
</thinking>

在量子计算领域，Deutsch-Jozsa（DJ）算法是展示量子并行性和量子干涉带来指数级加速的经典案例。

**1. 查询复杂度对比分析**
对于判定一个 n 比特函数 f:{0,1}^n→{0,1} 是常函数（所有输入映射到同一输出）还是平衡函数（一半输入映射到0，另一半映射到1）：
- **经典确定性算法**：最坏情况下必须进行 2^(n-1) + 1 次查询。因为直到检查了一半以上的输入并发现结果完全一致之前，无法确定性地区分这两种情况，其复杂度为 O(2^n)。
- **经典概率算法**：若允许极小的错误率，随机抽样 k 次，未发现矛盾的概率为 1/2^(k-1)，虽然能将查询降到常数级，但这并非绝对可靠的确定性解答。
- **量子Deutsch-Jozsa算法**：仅需 **1次** 对Oracle的查询，即可达到100%的确定性判定。从 O(2^n) 到 O(1) 的飞跃，完美展示了量子算法在特定黑盒问题上的指数级加速潜力。

**2. 优缺点及适用场景对比**
- **优点**：DJ算法是量子并行性与干涉效应的极佳教学范例。它证明了对量子态的精心操控可以在极少的查询内提取出全局函数性质。它的设计理念（相位反转 + Hadamard变换提取相位差）是后续诸多高级量子算法（如Bernstein-Vazirani算法、Simon算法乃至Shor算法）的核心基石。
- **缺点**：在实际工业应用中，DJ算法的意义非常有限。首先，现实世界中极少存在严格的“常函数或平衡函数”这种人为设定的极端黑盒问题；其次，算法要求理想的、无噪声的量子硬件来保证单次测量的绝对正确，而在当今的NISQ（含噪声中等规模量子）设备上，单次测量的可靠性容易受到硬件误差的干扰。
- **适用场景**：目前DJ算法主要用作量子计算理论研究的“Hello World”以及量子硬件基准测试的验证程序，用来直观检验量子门的保真度和量子相干性，而不作为解决实际复杂业务问题的工具。

**3. isQ语言代码示例**
下面提供一段使用isQ语言判定2量子比特DJ问题的代码。这里我们将Oracle设定为 f(x) = x_0 ⊕ x_1（即平衡函数），通过运行该量子程序，测量结果将排除 00，证明该函数是平衡函数。

```isq
import std;

// 声明3个量子比特，q[0]和q[1]为查询输入，q[2]为辅助比特
qbit q[3];

procedure main() {
    // 1. 初始化辅助比特为 |1>，以便后续产生相位反转
    X(q[2]);
    
    // 2. 将所有量子比特转化为叠加态
    H(q[0]);
    H(q[1]);
    H(q[2]);
    
    // 3. 执行Oracle查询：此处实现平衡函数 f(x0, x1) = x0 XOR x1
    // 如果作为常函数测试，可以注释掉下面的CNOT门
    CNOT(q[0], q[2]);
    CNOT(q[1], q[2]);
    
    // 4. 再次对输入比特施加Hadamard门，引发量子干涉
    H(q[0]);
    H(q[1]);
    
    // 5. 测量输入比特
    // 如果是常函数，结果必为 00；如果是平衡函数，结果必定包含 1（例如 11）
    int r0 = M(q[0]);
    int r1 = M(q[1]);
}
```

## isqQA/quantum_algorithms/129_math_derivation

- task_id: `isqQA/quantum_algorithms/129_math_derivation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `math_derivation`, `algorithm`, `纠缠交换`
- source: `qa_pipeline`
- dataset_index: `3732`

### Prompt

请提供量子纠缠交换协议的完整数学推导，解释两对独立纠缠态的量子比特是如何通过贝尔测量使另外两个无直接相互作用的量子比特建立纠缠的，并使用isQ代码编写相应的量子电路来演示此演化过程。

### Reference answer

<think>
要推导纠缠交换并完成电路演示，思考过程分为数学理论推导和量子电路构建两部分。

首先，明确初始状态为两对独立的贝尔态（量子比特A与B、C与D）的直积。将整体波函数在计算基下展开后，关键的数学推导步骤是对中间两个粒子（B和C）的基矢空间进行基底变换，将其由计算基替换为贝尔态基矢进行线性重组。将重组后的表达式代回原方程并重新提取公因式，整体状态即可被巧妙地改写为“A与D的贝尔态”和“B与C的贝尔态”的直积形式。由此得出核心物理结论：对B和C执行联合贝尔测量使其坍缩，A和D必然会随之坍缩至对应的贝尔态，从而建立起纠缠。

在电路构建与代码实现上，逻辑与数学过程一一对应：第一步，利用Hadamard门和CNOT门分别作用于A-B和C-D，制备两个初始纠缠对；第二步，在B和C之间构建贝尔测量电路（即依次应用CNOT门和Hadamard门）；第三步，对B和C进行测量，并可根据测量结果对A和D施加相应的泡利门（Pauli gates）修正，从而用代码完整复现这一非定域的量子演化过程。
</think>

纠缠交换是量子信息论中极其重要的现象，它允许两个原本没有任何直接相互作用的量子比特通过与其他纠缠比特进行联合测量而建立起量子纠缠。下面我将为你进行严密的数学推导，并提供对应的代码实现。

假设我们有两对独立的贝尔态（Bell State），即最大纠缠态 |Φ+> = (|00> + |11>) / √2。我们共有四个量子比特，分别记为 A, B, C, D。初始时，A 和 B 构成一对纠缠态，C 和 D 构成另一对纠缠态。系统的整体初始量子态可以表示为这两个贝尔态的张量积：
|Ψ_0> = |Φ+>_{AB} ⊗ |Φ+>_{CD} 
= 1/2 (|00>_{AB} + |11>_{AB}) ⊗ (|00>_{CD} + |11>_{CD}) 
= 1/2 (|0_A 0_B 0_C 0_D> + |0_A 0_B 1_C 1_D> + |1_A 1_B 0_C 0_D> + |1_A 1_B 1_C 1_D>)

我们将上式中的 B 和 C 组合在一起，将它们的计算基态 |00>, |01>, |10>, |11> 用 B 和 C 的四个贝尔态重新线性表示。四个贝尔态的定义为：
|Φ+>_{BC} = (|00> + |11>) / √2
|Φ->_{BC} = (|00> - |11>) / √2
|Ψ+>_{BC} = (|01> + |10>) / √2
|Ψ->_{BC} = (|01> - |10>) / √2

从中反解出计算基态并代入 |Ψ_0> 中，我们着重合并关于远端粒子 A 和 D 的项：
|Ψ_0> = 1/2 [ 1/√2(|Φ+>_{BC} + |Φ->_{BC})|0_A 0_D> + 1/√2(|Ψ+>_{BC} + |Ψ->_{BC})|0_A 1_D> + 1/√2(|Ψ+>_{BC} - |Ψ->_{BC})|1_A 0_D> + 1/√2(|Φ+>_{BC} - |Φ->_{BC})|1_A 1_D> ]

提取并合并同类项，按 B 和 C 的各个贝尔态进行分类整理：
|Ψ_0> = 1/2 [ 1/√2 |Φ+>_{BC} (|0_A 0_D> + |1_A 1_D>) + 1/√2 |Φ->_{BC} (|0_A 0_D> - |1_A 1_D>) + 1/√2 |Ψ+>_{BC} (|0_A 1_D> + |1_A 0_D>) + 1/√2 |Ψ->_{BC} (|0_A 1_D> - |1_A 0_D>) ]

括号中的项恰好也是远端量子比特 A 和 D 的贝尔态。因此，系统的状态可以极其优雅地重写为：
|Ψ_0> = 1/2 ( |Φ+>_{BC}|Φ+>_{AD} + |Φ->_{BC}|Φ->_{AD} + |Ψ+>_{BC}|Ψ+>_{AD} + |Ψ->_{BC}|Ψ->_{AD} )

从上述数学演化结果可以看出，如果此时对中间的量子比特 B 和 C 进行贝尔基联合测量，测量结果将会等概率（各25%）坍缩到四种贝尔态之一。而随着 B 和 C 态的坍缩，远端毫无关联的 A 和 D 也会瞬间坍缩到与 B、C 测量结果完全相同的贝尔态上，这就是纠缠交换的数学本质。

在量子电路中，通常我们将 B 和 C 执行 CNOT 门操作后再对 B 执行 H 门，最后测量这两个比特来完成贝尔测量。根据测量结果，我们只需对远端的 D 比特施加经典的酉操作（X门和Z门），就能将 A 和 D 主动恢复为标准的 |Φ+> 态。以下是基于 isQ 语言的完整电路演示代码：

import std;

qbit q[4]; // 全局声明量子比特，依次为 A, B, C, D

procedure main() {
    // 1. 准备第一对纠缠态：A 和 B
    H(q[0]);
    CNOT(q[0], q[1]);

    // 2. 准备第二对纠缠态：C 和 D
    H(q[2]);
    CNOT(q[2], q[3]);

    // 3. 对中间的 B (q[1]) 和 C (q[2]) 执行 Bell 测量前向演化
    CNOT(q[1], q[2]);
    H(q[1]);

    // 4. 测量 B 和 C
    int r1 = M(q[1]); // B 测量结果
    int r2 = M(q[2]); // C 测量结果

    // 5. 根据经典测量结果，对远端 D 进行局域酉变换恢复纠缠态
    if (r2 == 1) {
        X(q[3]); // 恢复奇偶性
    }
    if (r1 == 1) {
        Z(q[3]); // 恢复相对相位
    }
}

## isqTrain/96

- task_id: `isqTrain/96`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3988`

### Prompt

Implement a quantum circuit in isQ: implements the gate_decomposition pattern with modified rotation parameters (pi4_to_pi3). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Implement a gate decomposition circuit with modified rotation angles (π/4 → π/3) that produces correlated measurement outcomes.

**Qubits:** 2 qubits (q[0], q[1]), both measured.

**State evolution:**
1. **Hadamards:** |00⟩ → |++⟩ = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2
2. **CNOT(q[0],q[1]):** → (|00⟩ + |01⟩ + |11⟩ + |10⟩)/2
3. **Rz(π/2, q[1]):** → (e^{-iπ/4}|00⟩ + e^{-iπ/4}|01⟩ + e^{iπ/4}|10⟩ + e^{iπ/4}|11⟩)/2
4. **CNOT(q[0],q[1]):** → e^{-iπ/4}(|00⟩+|01⟩) + e^{iπ/4}(|10⟩+|11⟩))/2 — this is the cost unitary applying ZZ-phase
5. **Rx(π/3) on both:** Each qubit rotates around X by π/3, mixing computational basis states; cos(π/6)≈0.866, sin(π/6)=0.5

**Probabilities:** The symmetric structure (H on both, same Rx on both) with the ZZ entangling operation creates correlation: |00⟩ and |11⟩ have equal high probability ≈0.467, while |01⟩ and |10⟩ have equal low probability ≈0.033. The π/3 Rx rotation preserves more amplitude in the correlated states compared to π/4.

## isqTrain/51

- task_id: `isqTrain/51`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_arrays`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `786`

### Prompt

用isQ实现implements the oracle_boolean pattern but with a different initial state preparation (flip q[[2]] -> q[0]).

### Chain-of-thought reasoning

Looking at the task, I need to reason about the given isQ program. Let me trace through the circuit.

The program implements the Deutsch-Jozsa algorithm for 2 input qubits with a balanced oracle.

Qubits: q[0], q[1], q[2]

The task says "flip q[[2]] -> q[0]" which means the output qubit should be q[0] instead of q[2], and the initial state preparation changes accordingly.

Let me trace the original circuit implementation:

Initial state: |000>

1. X(q[0]): |000> → |100>
2. H(q[2]): |100> → |100> (no change to q[2])
3. H(q[0]): |100> → (1/√2)(|000> - |100>) (wait, H|1> = |-> = (|0> - |1>)/√2)
   Actually |100> → H on q[0] gives (1/√2)(|000> - |100>) ... wait let me be more careful.

Wait, The circuit should:
- X(q[0]) - flips q[0] to |1>
- H(q[2]) - puts q[2] in superposition
- H(q[0]), H(q[1]) - puts q[0], q[1] in |+> state

But this is confusing. Let me re-read.

Actually wait - The implementation puts q[0] in |1> first with X, then applies H to get |->. Then H(q[2]) is applied... but then H(q[0]) is applied again? That would take |-> back to |1>?

No wait, the order is:
1. X(q[0]) → q[0] = |1>
2. H(q[2]) → q[2] = |+>
3. H(q[0]) → q[0] = |-> (since H|1> = |->)
4. H(q[1]) → q[1] = |+>

So after initialization: q[0] = |->, q[1] = |+>, q[2] = |+>

Then balanced_oracle(q[0], q[1], q[2]):
- CNOT(q[0], q[2])
- CNOT(q[1], q[2])

This applies phase kickback. Since q[2] starts in |+>:
CNOT(q[0], q[2]) with q[0] in |-> and q[2] in |+>:
When q[0]=|0>: q[2] unchanged
When q[0]=|1>: q[2] gets X applied

Actually let me think about this more carefully. The state before oracle is:
|ψ⟩ = |−⟩₀ ⊗ |+⟩₁ ⊗ |+⟩₂

= (|0⟩-|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2

Let me expand:
= 1/(2√2) Σ_{x∈{0,1}²} (-1)^{x₁} |x₁⟩|x₂⟩(|0⟩+|1⟩)

Wait, let me index properly. q[0] is the first qubit.

|ψ⟩ = (|0⟩₀ - |1⟩₀)/√2 ⊗ (|0⟩₁ + |1⟩₁)/√2 ⊗ (|0⟩₂ + |1⟩₂)/√2

For the balanced oracle f(x₁, x₂) = x₁ ⊕ x₂:
CNOT(q[0], q[2]) followed by CNOT(q[1], q[2])

This computes f on q[2]. Since q[2] is in |+⟩, by phase kickback:
|−⟩₀|+⟩₁|+⟩₂ → (−1)^{f(x)} factors get kicked back

Actually, the standard Deutsch-Jozsa: if the oracle qubit is in |−⟩, then the phase kickback gives (-1)^f(x) to the input state. But here q[0] is in |−⟩ and it's also an input to the oracle...

Hmm, let me reconsider. The balanced_oracle takes (q[0], q[1], q[2]) where q[2] is the target. The CNOT gates flip q[2] based on q[0] and q[1].

The state is |−⟩₀|+⟩₁|+⟩₂. Let me write it out:

|ψ⟩ = 1/(2√2) Σ_{a,b ∈ {0,1}} (-1)^a |a⟩₀|

## isqQA/quantum_algorithms/109_step_by_step

- task_id: `isqQA/quantum_algorithms/109_step_by_step`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `step_by_step`, `algorithm`, `QPE的精度与量子比特数`
- source: `qa_pipeline`
- dataset_index: `4941`

### Prompt

量子相位估计（QPE）算法中，精度与量子比特数究竟是如何对应的？请以估计酉算符 S 门（作用于 |1⟩ 态产生相位 π/2）为例，使用 2 个计数比特，一步步教我手动追踪整个算法过程的数学状态演化，并解释为什么增加比特能提高精度。最后，请用 isQ 语言写出对应的量子线路代码。

### Reference answer

<think>
要解答这个问题，首先需明确QPE的核心机制：通过受控酉操作实现相位回退，将特征态的相位提取到振幅中，再由逆量子傅里叶变换（IQFT）将相位信息转化为二进制概率分布。计数比特数$t$将相位区间$[0,1)$均匀划分为$2^t$份，精度即由比特数直接决定。

针对S门案例，已知其作用于$|1\rangle$的相位为$\pi/2$，对应十进制相位值$0.25$（即二进制$0.01_2$）。在追踪2比特演化时，逻辑步骤如下：首先对计数比特施加H门构建叠加态；接着施加受控$S^{2^k}$门，相位会按2的幂次累加，使计数寄存器演化为带有周期性相位的态；然后施加IQFT，因为0.25刚好能用2位二进制小数精确表示，相位信息会被完美映射为确切的计算基矢态，测量即得结果。

在解释为何增加比特能提高精度时，核心在于二进制离散化误差。若真实相位无法用有限位精确表示，测量概率峰会分散在真实值两侧。增加比特数相当于提供了更细的离散化网格，从而降低截断误差，使概率分布更集中于真实相位。最后，基于上述演化逻辑（初始化、H门、受控S门、IQFT及测量），即可顺理成章地将其映射为isQ量子编程语言的具体代码。
</think>

在量子相位估计（QPE）算法中，我们核心目标是通过施加受控酉操作，将隐藏在特征态中的相位转移到计数寄存器的基矢振幅上，再通过逆量子傅里叶变换（IQFT）将其转化为可测量的二进制位串。计数寄存器的比特数 $t$ 直接决定了相位的分辨率，步长为 $1/2^t$。下面我们分步骤为你手动追踪使用 2 个计数比特估计 $S$ 门相位（$\phi = 1/4 = 0.25$）的过程。\n\n**第一步：系统初始化**\n我们使用 2 个计数比特 $q_0, q_1$（初始化为 $|0\rangle$）和 1 个目标比特 $q_2$（初始化为特征态 $|1\rangle$）。系统的初始状态为：\n$|\psi_0\rangle = |00\rangle \otimes |1\rangle$\n\n**第二步：对计数比特施加 Hadamard 门**\n对 $q_0, q_1$ 施加 H 门，产生均匀叠加态：\n$|\psi_1\rangle = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle) \otimes |1\rangle$\n\n**第三步：施加受控酉操作（相位反冲）**\n目标相位 $\phi = 0.25$（对应 $S$ 门产生的相位 $\pi/2$）。根据 QPE 原理，第 $j$ 个计数比特控制 $U^{2^j}$ 操作。\n- $q_0$ 控制 $S^1$ 操作：对 $|1\rangle$ 态产生相位 $e^{i2\pi \cdot 0.25 \cdot 1} = e^{i\pi/2} = i$。\n- $q_1$ 控制 $S^2$ 操作（相当于 Z 门）：对 $|1\rangle$ 态产生相位 $e^{i2\pi \cdot 0.25 \cdot 2} = e^{i\pi} = -1$。\n状态演化为：\n$|\psi_2\rangle = \frac{1}{2}(|00\rangle + i|01\rangle - |10\rangle - i|11\rangle) \otimes |1\rangle$\n此时，目标特征态的相位已经被“打”到了计数寄存器的相对相位上。\n\n**第四步：施加逆量子傅里叶变换（IQFT）**\n由于 $\phi = 0.25 = \frac{1}{4}$，可以用二进制精确表示为 $0.01_2$。当前的状态其实就是频率 $k=1$ 的傅里叶基矢。执行 $QFT^\dagger$ 会将其映射回计算基矢 $|01\rangle$。\n$|\psi_3\rangle = QFT^\dagger |\psi_2\rangle = |01\rangle \otimes |1\rangle$\n\n**第五步：测量与精度分析**\n测量计数寄存器，我们将 100% 得到字符串 `01`。读取结果为 $0 \times 2^{-1} + 1 \times 2^{-2} = 0.25$，与真实相位完全一致。\n为什么增加比特能提高精度？因为 2 个比特只能将 $[0, 1)$ 区间划分为 $2^2 = 4$ 份（只能完美表示 $0, 0.25, 0.5, 0.75$）。如果相位是 $0.3$，2 比特无法精确表示，测量结果会塌缩到最近的值，产生最高 $0.125$ 的误差；若使用 $t$ 个比特，则区间被划分为 $2^t$ 份，分辨率达到 $2^{-t}$，从而实现极高精度的相位估计。\n\n**isQ 代码实现**\n以下是展示上述 2 比特 QPE 过程的 isQ 代码：\n```isQ\nimport std;\n\nqbit q[3]; // q[0], q[1] 为计数比特，q[2] 为目标比特\n\nprocedure main() {\n    // 初始化目标特征态 |1>\n    X(q[2]);\n\n    // 对计数比特施加 Hadamard 门\n    H(q[0]);\n    H(q[1]);\n\n    // 受控酉操作：相位反冲\n    // q[0] 控制 S 门 (U^1)\n    ctrl @[q[0]] S(q[2]);\n\n    // q[1] 控制 S^2 门 (即 Z 门)\n    ctrl @[q[1]] Z(q[2]);\n\n    // 施加逆量子傅里叶变换 (IQFT)\n    // 第一步：交换 q[0] 和 q[1] (使用非SWAP方式：3个CNOT)\n    CNOT(q[0], q[1]);\n    CNOT(q[1], q[0]);\n    CNOT(q[0], q[1]);\n\n    // 第二步：q[1] 位的逆处理 (H门)\n    H(q[1]);\n\n    // 第三步：q[0] 位的逆处理 (Rz^-pi/2 加 H门)\n    // 修正相对相位\n    Rz(-1.5707963268, q[0]); // -pi/2\n    CNOT(q[1], q[0]);\n    Rz(1.5707963268, q[0]);  // pi/2\n    CNOT(q[1], q[0]);\n    H(q[0]);\n\n    // 测量计数比特\n    M(q[0]);\n    M(q[1]);\n}\n```

## isqTrain/1418

- task_id: `isqTrain/1418`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `isq_syntax_ctrl_nctrl`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `422`

### Prompt

Implement the following in isQ: Apply the 3-qubit Quantum Fourier Transform to the input state |001> and measure all qubits.

### Chain-of-thought reasoning

Let me trace through the QFT on 3 qubits with input |001>.

The 3-qubit QFT transforms $|x_0 x_1 x_2\rangle$ where x is the binary representation of the input number. |001> represents the number 1.

The QFT formula gives: QFT|x⟩ = (1/√8) Σ_y e^(2πixy/8) |y⟩

For x=1: QFT|1⟩ = (1/√8) Σ_{y=0}^{7} e^(2πiy/8) |y⟩ = (1/√8)(|0⟩ + e^(iπ/4)|1⟩ + e^(iπ/2)|2⟩ + e^(i3π/4)|3⟩ + e^(iπ)|4⟩ + e^(i5π/4)|5⟩ + e^(i3π/2)|6⟩ + e^(i7π/4)|7⟩)

Each computational basis state has equal magnitude 1/√8, so each has probability 1/8 = 0.125.

Let me trace through the circuit step by step:

1. Start with |000⟩
2. X(q[2]) → |001⟩ (q[2] is the least significant bit in the array indexing, but I need to check the convention)

Wait, let me reconsider the convention. In the isQ code, q[0], q[1], q[2] are declared. The input |001> - which qubit is 1?

Looking at the QFT circuit structure:
- H(q[2]) then ctrl S(q[1], q[2]) then ctrl T(q[0], q[2]) - this is the first stage targeting q[2]
- H(q[1]) then ctrl S(q[0], q[1]) - second stage targeting q[1]
- H(q[0]) - third stage targeting q[0]
- swap (three-CNOT decomposition)(q[0], q[2]) - final swap

This is the standard QFT circuit. The input |001> means q[0]=0, q[1]=0, q[2]=1 (since X is applied to q[2]).

Let me trace:

Initial: |000⟩
After X(q[2]): |001⟩ (q[2]=1)

Now QFT stage 1 (on q[2]):
H(q[2]) on |001⟩: The state is |00⟩⊗|1⟩. H|1⟩ = |−⟩ = (|0⟩−|1⟩)/√2
State: (|000⟩−|001⟩)/√2

ctrl S(q[1], q[2]): S|1⟩ = i|1⟩, controlled by q[1]. Since q[1]=0, nothing happens.
State: (|000⟩−|001⟩)/√2

ctrl T(q[0], q[2]): T|1⟩ = e^(iπ/4)|1⟩, controlled by q[0]. Since q[0]=0, nothing happens.
State: (|000⟩−|001⟩)/√2

QFT stage 2 (on q[1]):
H(q[1]) on the state: H acts on q[1] which is always |0⟩, so H|0⟩ = |+⟩ = (|0⟩+|1⟩)/√2
State: (|000⟩+|010⟩−|001⟩−|011⟩)/2

ctrl S(q[0], q[1]): S controlled by q[0]. Since q[0]=0, nothing happens.
State: (|000⟩+|010⟩−|001⟩−|011⟩)/2

QFT stage 3 (on q[0]):
H(q[0]) on the state: H acts on q[0] which is always |0⟩, so H|0⟩ = (|0⟩+|1⟩)/√2
State: (|000⟩+|100⟩+|010⟩+|110⟩−|001⟩−|101⟩−|011⟩−|111⟩)/(2√2)

swap (three-CNOT decomposition)(q[0], q[2]):
|000⟩→|000⟩, |100⟩→|001⟩, |010⟩→|010⟩, |110⟩→|011⟩, |001⟩→|100⟩, |101⟩→|101⟩, |011⟩→|110⟩, |111⟩→|111⟩

State: (|000⟩+|001⟩+|010⟩+|011⟩−|100⟩−|101⟩−|110⟩−|111⟩)/(2√2)

Wait, that gives probabilities of 1/8 for each state, but

## isqTrain/4823

- task_id: `isqTrain/4823`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_import_qft`, `phase_manipulation`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `5754`

### Prompt

Write an isQ program that uses QFT for phase manipulation. Import std and qft. Declare 2 global qubits. Apply qft(q) to move to frequency domain, apply Z(q[0]) to add a phase, then apply qft_inv(q) to return to computational basis. Measure both qubits.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for an isQ quantum program that uses QFT for phase manipulation.

Let me trace through the circuit:

1. Initial state: |00⟩ (2 qubits)

2. QFT(q) on 2 qubits:
   - QFT on |00⟩ gives |00⟩/2 + |01⟩/2 + |10⟩/2 + |11⟩/2 = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2
   - Wait, let me think about this more carefully. QFT on |0⟩^n gives an equal superposition over all computational basis states.
   - For 2 qubits: QFT|00⟩ = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2

3. Z(q[0]) - applies Z gate to qubit 0
   - Z|0⟩ = |0⟩, Z|1⟩ = -|1⟩
   - So this flips the sign of states where q[0] = |1⟩
   - States with q[0] = 1: |10⟩ and |11⟩
   - After Z(q[0]): (|00⟩ + |01⟩ - |10⟩ - |11⟩)/2

4. QFT_inv(q) - inverse QFT
   - We need to compute QFT_inv of (|00⟩ + |01⟩ - |10⟩ - |11⟩)/2
   
Let me think about this using the QFT formula. For n qubits:
QFT|j⟩ = (1/√N) Σ_k e^(2πijk/N) |k⟩

For 2 qubits, N=4:
QFT|j⟩ = (1/2) Σ_k e^(2πijk/4) |k⟩

So:
- QFT|0⟩ = (1/2)(|0⟩ + |1⟩ + |2⟩ + |3⟩) = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2
- QFT|1⟩ = (1/2)(|0⟩ + i|1⟩ - |2⟩ - i|3⟩) = (|00⟩ + i|01⟩ - |10⟩ - i|11⟩)/2
- QFT|2⟩ = (1/2)(|0⟩ - |1⟩ + |2⟩ - |3⟩) = (|00⟩ - |01⟩ + |10⟩ - |11⟩)/2
- QFT|3⟩ = (1/2)(|0⟩ - i|1⟩ - |2⟩ + i|3⟩) = (|00⟩ - i|01⟩ - |10⟩ + i|11⟩)/2

After QFT on |00⟩: (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2

After Z(q[0]):
Z on qubit 0 (the higher-order qubit) flips the sign when q[0]=1
So |10⟩ and |11⟩ get a minus sign:
(|00⟩ + |01⟩ - |10⟩ - |11⟩)/2

Now applying QFT_inv:
Since QFT is unitary, QFT_inv is its conjugate transpose.

The state (|00⟩ + |01⟩ - |10⟩ - |11⟩)/2 can be written as (1/2)(QFT|0⟩ + QFT|2⟩)/2... no wait.

Actually, let me think in terms of the Fourier basis.

After QFT|00⟩, we have the state |ŝ0⟩ (the Fourier transform of |0⟩, which is the uniform superposition).

Applying Z to q[0] is like applying a phase in the frequency domain. 

Actually, let me reconsider. The state after QFT is:
(|00⟩ + |01⟩ + |10⟩ + |11⟩)/2

After Z(q[0]):
Z on q[0] means we apply Z to the first qubit. Z|0⟩ = |0⟩, Z|1⟩ = -|1⟩.
So terms where q[0]=1 (i.e., |10⟩ and |11⟩) get a phase of -1.

New state: (|00⟩ + |01⟩ - |10⟩ - |11⟩)/2

This state is actually (1/2)(|00⟩ + |01⟩ - |10⟩ - |11⟩)
= (1/2)(|0⟩(|0⟩+|1⟩) - |1⟩(|0⟩+|1⟩)) for q[0] and q[1]
Wait no, let me be more careful with ordering.

If q[0] is the first qubit and q[1] is

## isqExpand/algo/32

- task_id: `isqExpand/algo/32`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `amplitude_estimation`, `amplitude_amplification`, `grover`
- source: `isq_expansion`
- dataset_index: `3665`

### Prompt

I need an isQ program to demonstrating amplitude amplification on 3 qubits. The state preparation A creates the state (|000> + |111>)/sqrt(2) using H on q[0] followed by two CNOT gates. The 'good' outcome is defined as q[2]=1. After state preparation, the probability of q[2]=1 is 0.5 (sin^2(theta)=0.5, theta=pi/4). Since theta=pi/4, one Grover iteration rotates to 3*pi/4, giving sin^2(3*pi/4)=0.5 — the probability remains unchanged. Verify this by applying one Grover iteration and measuring q[2].

### Chain-of-thought reasoning

## Reasoning
Goal: Demonstrate amplitude amplification structure.

State preparation A:
1. H(q[0]): (|0>+|1>)/sqrt(2)
2. CNOT(q[0],q[1]): (|00>+|11>)/sqrt(2)
3. CNOT(q[1],q[2]): (|000>+|111>)/sqrt(2)

'Good' subspace: q[2]=1, probability = 0.5, so theta = pi/4.

Grover iteration G = A * S_0 * A_dag * S_chi:
- S_chi (oracle): Z(q[2]) flips phase when q[2]=1
- A_dag: inverse of A
- S_0: zero-state reflection using X gates + multi-controlled Z
- A: re-apply state preparation

After 1 iteration, angle goes from pi/4 to 3*pi/4.
P(good) = sin^2(3*pi/4) = sin^2(pi/4) = 0.5.
The probability stays the same — a known property when theta = pi/4.

Probs for q[2]: [0.5, 0.5]

## isqTrain/3003

- task_id: `isqTrain/3003`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1065`

### Prompt

Create an isQ quantum circuit that applies two Hadamard gates to each of 2 qubits (H*H = I). All qubits should end in |0>.

Requirements:
- Declare `qbit q[2];` at global scope.
- Measure all 2 qubits.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply double Hadamard (H²=I) to each of 2 qubits, demonstrating the identity property.
2. Two qubits are used (`q[0]`, `q[1]`), both measured at the end.
3. State evolution:
   - Initial: |00⟩
   - After H(q[0]): (|0⟩+|1⟩)/√2 ⊗ |0⟩ = (|00⟩+|10⟩)/√2
   - After H(q[0]) again: |00⟩ (since H·H = I)
   - After H(q[1]): |0⟩ ⊗ (|0⟩+|1⟩)/√2 = (|00⟩+|01⟩)/√2
   - After H(q[1]) again: |00⟩ (since H·H = I)
4. Final state |00⟩ yields measurement probability {|00⟩: 1.0}, confirming the double-H identity operation.
