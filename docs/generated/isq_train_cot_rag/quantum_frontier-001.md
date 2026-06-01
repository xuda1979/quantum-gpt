# ISQ training COT RAG corpus: quantum_frontier shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/front/34

- task_id: `isqExpand/front/34`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `difficult`
- concept_tags: `quantum_ml`, `expressibility`, `entangling_capability`, `ansatz`
- source: `qa_pipeline`
- dataset_index: `688`

### Prompt

解释量子机器学习中的表达能力（expressibility）和纠缠能力（entangling capability）的概念。为什么这两个度量对评估参数化量子电路很重要？

### Chain-of-thought reasoning

## 推理
表达能力衡量PQC在态空间中的覆盖范围，纠缠能力衡量其产生多体关联的能力。两者共同决定了PQC作为ML模型的适用性。需要平衡——过高表达能力导致贫瘠高原，过低则欠拟合。

### Reference answer

表达能力和纠缠能力是评估参数化量子电路（PQC）质量的两个关键度量：

**表达能力（Expressibility）：**
衡量PQC生成的量子态在希尔伯特空间中的覆盖程度。具体定义为PQC生成的态分布与Haar随机态分布之间的差异。

计算方法：随机采样参数θ和φ，计算保真度F = |⟨ψ(θ)|ψ(φ)⟩|²的分布，并与Haar随机分布比较（用KL散度或类似度量）。

表达能力越高，PQC可以表示的量子态越多样，但过高的表达能力可能导致贫瘠高原。

**纠缠能力（Entangling Capability）：**
衡量PQC生成纠缠态的能力。通常用Scott纠缠度量或Meyer-Wallach纠缠度量来评估。

高纠缠能力意味着电路可以创建强相关的多体量子态，这对于捕获数据中的非线性关系可能很重要。

**为什么重要：**
1. 选择ansatz：不同的电路结构（ansatz）有不同的表达-纠缠特性，需要根据问题需求选择。
2. 避免过拟合/欠拟合：表达能力太低无法学习复杂函数，太高容易过拟合和遇到贫瘠高原。
3. 资源效率：在相同门数量下，不同结构的表达和纠缠效率差异很大。
4. 理论分析：这些度量为比较不同PQC提供了定量的框架。

## isqExpand/front/142

- task_id: `isqExpand/front/142`
- task_type: `output_prediction`
- category: `quantum_frontier`
- difficulty: `difficult`
- concept_tags: `trotterization`, `ising_model`, `zz_interaction`, `cnot_decomposition`, `eigenstate_evolution`
- source: `isq_expansion`
- dataset_index: `4051`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    CNOT(q[0], q[1]);
    Rz(1.5707963267948966, q[1]);
    CNOT(q[0], q[1]);
}
```

### Chain-of-thought reasoning

Step 1: Initial state after X(q[0]) is |10⟩.
Step 2: First CNOT(q[0], q[1]) with control q[0]=1 flips q[1]: |10⟩ → |11⟩.
Step 3: Rz(π/2, q[1]) applies rotation e^(-iπ/4) to |0⟩ and e^(+iπ/4) to |1⟩ on q[1]. Since q[1] is in |1⟩, we get: e^(iπ/4)|11⟩.
Step 4: Second CNOT(q[0], q[1]) with control q[0]=1 flips q[1] back: e^(iπ/4)|11⟩ → e^(iπ/4)|10⟩.
Step 5: Final state is e^(iπ/4)|10⟩, which differs from |10⟩ only by a global phase.
Step 6: Global phase has no observable effect, so measurement probabilities are P(10)=1.0 and all others 0.
Step 7: Verification: |10⟩ is an eigenstate of Z⊗Z with eigenvalue (1)×(-1)=-1, so U|10⟩=e^(iπ/4)|10⟩, confirming only a global phase change.

### Reference answer

{'predicted_probs': {'00': 0.0, '01': 0.0, '10': 1.0, '11': 0.0}, 'explanation': 'The initial state is |10⟩. The CNOT-Rz(π/2)-CNOT sequence implements exp(-i·(π/4)·Z⊗Z). Since |10⟩ is an eigenstate of Z⊗Z with eigenvalue -1, the evolution only adds a global phase factor e^(iπ/4), leaving measurement probabilities unchanged.'}

## isqExpand/front/113

- task_id: `isqExpand/front/113`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `expert`
- concept_tags: `xy_model`, `trotter_decomposition`, `hamiltonian_simulation`, `spin_exchange`
- source: `isq_expansion`
- dataset_index: `4778`

### Prompt

Implement the following in isQ: implements a first-order Trotter step for simulating the XY model Hamiltonian on 2 qubits.

The XY model: H_XY = J(X₁X₂ + Y₁Y₂) describes spin-spin exchange interaction. A Trotter step decomposes e^{-iHt} into e^{-iJt·XX} · e^{-iJt·YY}.

The XX interaction is decomposed as: H-CNOT-Rz(2Jt)-CNOT-H (on both qubits).
The YY interaction is decomposed as: Rx(-pi/2.0)-CNOT-Rz(2Jt)-CNOT-Rx(pi/2.0) (on both qubits).

Requirements:
- Declare global `qbit q[2];`
- Start with |10⟩ (one excitation on q[0]): X(q[0]).
- Apply one Trotter step with Jt = pi/6.0.
- For XX: H(q[0]), H(q[1]), CNOT(q[0],q[1]), Rz(pi/3.0, q[1]), CNOT(q[0],q[1]), H(q[0]), H(q[1]).
- For YY: Rx(-pi/2.0, q[0]), Rx(-pi/2.0, q[1]), CNOT(q[0],q[1]), Rz(pi/3.0, q[1]), CNOT(q[0],q[1]), Rx(pi/2.0, q[0]), Rx(pi/2.0, q[1]).
- Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Simulate XY model H = J(XX+YY) for 2 qubits using first-order Trotter.

1. Start with |10⟩ (one spin excitation on q[0]).
2. XX decomposition: H⊗H · CNOT · Rz(2Jt) · CNOT · H⊗H implements exp(-iJt·XX)
3. YY decomposition: Rx(-π/2)⊗Rx(-π/2) · CNOT · Rz(2Jt) · CNOT · Rx(π/2)⊗Rx(π/2)
4. With Jt = π/6, the Rz angle is 2·π/6 = π/3.
5. Analytical: P(|10⟩) = sin²(π/6) = 0.25, P(|01⟩) = cos²(π/6) = 0.75
6. States |00⟩ and |11⟩ have zero probability (excitation number conservation).

## isqExpand/front/52

- task_id: `isqExpand/front/52`
- task_type: `bug_fix`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `hamiltonian_simulation`, `zz_interaction`, `angle_error`
- source: `isq_expansion`
- dataset_index: `4516`

### Prompt

这个isQ程序有问题，请找出错误并给出正确代码：

```isq
import std;
qbit q[2];

procedure main() {
    H(q[0]); H(q[1]);
    // ZZ(pi/4) interaction
    CNOT(q[0], q[1]);
    Rz(pi/4.0, q[1]);  // BUG: should be Rz(pi/2.0)
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Reasoning
The ZZ interaction e^{-i*theta*ZZ} decomposes as CNOT-Rz(2*theta)-CNOT. For theta=pi/4, the Rz angle should be 2*pi/4=pi/2. The buggy code uses Rz(pi/4) instead of Rz(pi/2), implementing only half the intended interaction strength.

## isqExpand/front/133

- task_id: `isqExpand/front/133`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `difficult`
- concept_tags: `Jordan-Wigner变换`, `费米子到量子比特映射`, `二次量子化`, `H2分子`, `量子化学模拟`, `泡利算符`, `Bravyi-Kitaev变换`
- source: `isq_expansion_qa`
- dataset_index: `2017`

### Prompt

解释Jordan-Wigner变换如何将费米子哈密顿量映射到量子比特哈密顿量。以H2分子为例，说明具体的映射过程和结果。

### Chain-of-thought reasoning

首先回顾Jordan-Wigner变换的定义：它将费米子产生/湮灭算符映射为泡利算符，核心是Z链编码宇称信息以保证反对易关系。然后推导映射公式a†_j = (X_j - iY_j)/2 ⊗ Z_{j-1}...Z_0。接着以H2分子为具体例子：STO-3G基组下4个自旋轨道→4量子比特，电子哈密顿量包含单体和双体积分项。经过JW变换得到泡利哈密顿量后，利用粒子数守恒和自旋对称性约化到2量子比特。最终得到标准形式H = g0*I + g1*Z0 + g2*Z1 + g3*Z0Z1 + g4*X0X1 + g5*Y0Y1。最后讨论JW变换的优缺点并与Bravyi-Kitaev变换对比。

### Reference answer

Jordan-Wigner变换是将费米子算符映射到量子比特（泡利）算符的核心方法。

一、基本原理

费米子与量子比特的本质区别在于：费米子满足反对易关系（泡利不相容原理），而量子比特（自旋-1/2粒子）满足对易关系。Jordan-Wigner变换通过在泡利算符中引入Z链（parity string）来编码费米子的宇称信息，从而保持反对易关系。

二、映射规则

费米子产生算符和湮灭算符的Jordan-Wigner映射为：

a†_j = 1/2 (X_j - iY_j) ⊗ Z_{j-1} ⊗ Z_{j-2} ⊗ ... ⊗ Z_0

a_j = 1/2 (X_j + iY_j) ⊗ Z_{j-1} ⊗ Z_{j-2} ⊗ ... ⊗ Z_0

其中X_j、Y_j、Z_j是作用在第j个量子比特上的泡利算符，Z链记录了第j个模式之前所有模式的粒子数宇称（奇偶性），这正是保证反对易关系的关键。

对于双算符乘积：

a†_i a_j + a†_j a_i → (X_i X_j + Y_i Y_j)/2 ⊗ Z_{i+1}...Z_{j-1}（i<j时）

a†_i a†_j + a_j a_i → (X_i Y_j - Y_i X_j)/2 ⊗ Z_{i+1}...Z_{j-1}

a†_i a_j a†_k a_l → 涉及四个泡利算符的张量积，同理包含适当的Z链。

三、H2分子实例

在STO-3G最小基组下，H2分子有2个原子轨道（每个H原子各1个1s轨道），经过分子轨道线性组合后得到2个分子自旋轨道（成键轨道σ_g和反键轨道σ_u），考虑自旋后共4个自旋轨道。因此需要4个量子比特来表示。

H2的电子结构哈密顿量（二次量子化形式）包含以下项：
- 常数项（核排斥能）
- 单体项：h_{pq} a†_p a_q
- 双体项：1/2 g_{pqrs} a†_p a†_q a_r a_s

经过Jordan-Wigner变换后，4量子比特哈密顿量包含大量泡利串项。

四、对称性约化

利用H2分子的对称性可以大幅简化：
1. 粒子数守恒：固定电子数为2
2. 自旋守恒（S_z=0）：每个自旋通道各1个电子
3. 空间对称性：成键和反键轨道的对称性约束

经过Bravyi-Kitaev或进一步约化后，可以仅用2个量子比特表示有效哈密顿量：

H = g_0 I + g_1 Z_0 + g_2 Z_1 + g_3 Z_0 Z_1 + g_4 X_0 X_1 + g_5 Y_0 Y_1

其中系数g_0到g_5依赖于核间距R。例如在平衡键长R≈0.74Å附近，典型值为：
g_0 ≈ -0.8105（常数偏移+核排斥），g_1 ≈ +0.1720，g_2 ≈ +0.1720，g_3 ≈ +0.1689，g_4 ≈ +0.0451，g_5 ≈ +0.0451（具体值随基组和键长变化）。

注意X_0 X_1和Y_0 Y_1项反映了两个量子比特间的量子关联（非对角项），正是量子计算需要处理的本质困难所在，也是经典方法难以高效处理的原因。

五、总结

Jordan-Wigner变换的优势是概念直观、实现简单，每个费米模式直接对应一个量子比特。缺点是Z链长度随系统规模增长，导致非局域的泡利串。对于大规模系统，Bravyi-Kitaev变换可以改善局部性，将Z链长度从O(N)降至O(log N)。

## isqExpand/front/101

- task_id: `isqExpand/front/101`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `qaoa`, `max_cut`, `phase_manipulation`, `superposition`
- source: `qa_pipeline`
- dataset_index: `2961`

### Prompt

解释量子近似优化算法（QAOA）的核心思想和电路结构。QAOA如何利用cost层和mixer层来求解组合优化问题？以Max-Cut问题为例说明。

### Chain-of-thought reasoning

## 推理
目标：解释QAOA的核心思想，聚焦cost层和mixer层的作用。

核心逻辑链：
1. 组合优化问题 -> 编码为对角哈密顿量H_C（Z基上的经典目标函数）
2. Cost层e^{-i*gamma*H_C}为不同目标函数值的基态添加不同相位
3. Mixer层e^{-i*beta*H_M}将相位差转化为概率差，驱动振幅向高质量解集中
4. 变分优化gamma, beta来最大化<H_C>

Max-Cut是最经典的QAOA应用：H_C = sum Z_i Z_j，ZZ用CNOT-Rz-CNOT分解。

### Reference answer

## QAOA（量子近似优化算法）

### 核心思想
QAOA 是一种变分量子算法，用于求解组合优化问题。其核心思想是：
- 将优化问题的目标函数编码为**cost哈密顿量 H_C**
- 利用参数化量子电路交替施加 cost 演化和 mixer 演化
- 通过经典优化器调节参数 (gamma, beta) 来最大化目标函数的期望值

### 电路结构（p=1层）

1. **初始化**：对所有 n 个量子比特施加 Hadamard 门，生成均匀叠加态 |+>^n

2. **Cost 层**：施加 e^{-i*gamma*H_C}
   - 对于 Max-Cut：H_C = sum_{(i,j) in edges} Z_i Z_j
   - 每条边的 ZZ 相互作用分解为：CNOT(i,j) -> Rz(2*gamma, j) -> CNOT(i,j)
   - 该层为不同 cut 值的计算基态赋予不同的相位

3. **Mixer 层**：施加 e^{-i*beta*H_M}，其中 H_M = sum_i X_i
   - 分解为每个量子比特上的 Rx(2*beta)
   - 该层在计算基态之间驱动概率转移

4. **测量**：在计算基上测量，得到候选解

### Max-Cut 示例

考虑两节点单边图：
- H_C = Z_0 Z_1
- Max-Cut 解为 |01> 和 |10>（两个节点分属不同集合）

在 isQ 中的实现：
```isq
import std;
qbit q[2];
procedure main() {
    H(q[0]); H(q[1]);
    // Cost layer: ZZ(gamma)
    CNOT(q[0], q[1]);
    Rz(2.0*gamma, q[1]);
    CNOT(q[0], q[1]);
    // Mixer layer
    Rx(2.0*beta, q[0]);
    Rx(2.0*beta, q[1]);
    M(q[0]); M(q[1]);
}
```

### 性能保证
对于 Max-Cut，p=1 层 QAOA 在最优参数下至少能达到最优解的 0.6924 近似比。增加层数 p 可以提高近似质量，p -> infinity 时趋近精确解。

## isqExpand/front/150

- task_id: `isqExpand/front/150`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `difficult`
- concept_tags: `quantum_metrology`, `Heisenberg_limit`, `standard_quantum_limit`, `quantum_entanglement`, `NOON_state`, `quantum_Fisher_information`, `parameter_estimation`
- source: `qa_pipeline`
- dataset_index: `2843`

### Prompt

什么是量子计量学中的Heisenberg极限？它如何超越经典的标准量子极限（SQL）？

### Chain-of-thought reasoning

首先，需要明确量子计量学的核心目标：利用量子力学效应提高参数估计的精度。步骤一：定义标准量子极限（SQL），说明当使用N个独立粒子时，由散粒噪声限制的不确定度按1/√N标度，来源于量子Fisher信息FQ=N。步骤二：引入Heisenberg极限，说明利用量子纠缠（如NOON态）可以将量子Fisher信息提升至FQ=N²，从而使不确定度按1/N标度改善。步骤三：从物理机制角度解释，纠缠态中所有粒子作为一个集体单元累积相位，等效相位放大N倍，这是超越SQL的核心原因。步骤四：讨论Cramér-Rao界作为精度的理论下界，以及Heisenberg极限作为量子力学基本原理所允许的最终极限。步骤五：补充实际实现中的挑战，如纠缠态对退相干的敏感性。最终综合这些要素形成完整的中文回答。

### Reference answer

在量子计量学中，测量精度受到基本物理极限的约束。

**标准量子极限（Standard Quantum Limit, SQL）**：
当使用N个独立（非纠缠）的量子粒子进行参数估计时，测量不确定度按Δθ ∝ 1/√N的规律随粒子数N减小。这是经典策略或使用非纠缠量子态所能达到的最佳精度，也称为散粒噪声极限（Shot Noise Limit）。其物理本质是每个粒子的测量结果独立随机，总噪声按√N增长，而信号按N增长，因此信噪比仅以√N改善。

**Heisenberg极限（Heisenberg Limit, HL）**：
当利用量子纠缠资源（如NOON态、GHZ态等）时，测量不确定度可以按Δθ ∝ 1/N的规律随粒子数N减小。这比SQL快了√N的因子，代表了量子计量学中理论上可达的最优精度。

**超越SQL的物理机制**：
1. **纠缠增强灵敏度**：在NOON态|N,0⟩+|0,N⟩中，N个粒子作为一个整体累积相位，等效相位累积为Nφ而非独立粒子情况下的φ。这使得干涉条纹的振荡频率提高了N倍，从而将角度估计灵敏度提高N倍。
2. **量子Fisher信息**：SQL对应的量子Fisher信息为FQ = N，而达到Heisenberg极限时FQ = N²。Cramér-Rao界给出Δθ ≥ 1/√FQ，因此FQ = N²导致Δθ ≥ 1/N。
3. **实际协议示例**：光学干涉仪中使用NOON态输入可达到Heisenberg标度；原子钟中使用纠缠原子可以提高频率估计精度。

**理论限制**：Heisenberg极限是量子力学基本原理（不确定性关系）所允许的最终极限，无法被进一步超越。实际实现中，纠缠态对退相干和粒子损耗极为敏感，因此在远离理想条件下维持Heisenberg标度是一个重大实验挑战。

## isqExpand/front/8

- task_id: `isqExpand/front/8`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `error_correction`, `phase_flip_code`, `syndrome_extraction`
- source: `isq_expansion`
- dataset_index: `1951`

### Prompt

请用isQ语言编写一个量子电路：demonstrates error detection in a 3-qubit phase-flip code.

The phase-flip code works in the Hadamard basis. A phase-flip error (Z gate) in the computational basis becomes a bit-flip error in the Hadamard basis.

Requirements:
- Declare global `qbit q[5];` (q[0..2] data, q[3..4] syndrome ancilla).
- Encode |0⟩_L: apply H to q[0], q[1], q[2].
- Simulate a phase-flip error on q[1]: apply Z(q[1]).
- Transform to Hadamard basis for syndrome extraction: apply H to q[0], q[1], q[2].
- Extract syndrome: CNOT(q[0],q[3]), CNOT(q[1],q[3]), CNOT(q[1],q[4]), CNOT(q[2],q[4]).
- Measure all 5 qubits.
- After H transform, Z error on q[1] becomes X error, so q[1] is flipped. State of data should be |010⟩, syndrome should be |11⟩.

### Chain-of-thought reasoning

## Reasoning
1. Start |00000⟩. H on data qubits: |+++00⟩.
2. Z(q[1]): |+-+00⟩ (phase flip on q[1], |−⟩ = H|1⟩).
3. H on data qubits: H|+⟩=|0⟩, H|−⟩=|1⟩, H|+⟩=|0⟩. State: |01000⟩.
4. CNOT(q[0],q[3]): q[0]=0, no flip. CNOT(q[1],q[3]): q[1]=1, flips q[3]. |01010⟩.
5. CNOT(q[1],q[4]): q[1]=1, flips q[4]. |01011⟩. CNOT(q[2],q[4]): q[2]=0, no flip.
6. Final state |01011⟩ = index 8+0+0+2+1 = 11.

## isqExpand/front/107

- task_id: `isqExpand/front/107`
- task_type: `output_prediction`
- category: `quantum_frontier`
- difficulty: `difficult`
- concept_tags: `qaoa`, `output_prediction`, `phase_manipulation`, `interference`
- source: `isq_expansion`
- dataset_index: `368`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;
qbit q[2];

procedure main() {
    // Prepare |++> state
    H(q[0]); H(q[1]);
    // ZZ interaction with theta = pi/3
    CNOT(q[0], q[1]);
    Rz(2.0*pi/3.0, q[1]);
    CNOT(q[0], q[1]);
    // Convert q[0] phase to amplitude
    H(q[0]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. H(q0), H(q1): |00> -> |++> = (|00>+|01>+|10>+|11>)/2
2. ZZ(pi/3): e^{-i*pi/3*Z0Z1}
   - Same parity (|00>,|11>): eigenvalue +1, phase e^{-i*pi/3}
   - Opposite parity (|01>,|10>): eigenvalue -1, phase e^{+i*pi/3}
3. H(q0): converts q[0] basis, mixing the phase information.

For |x,y> after ZZ, the phase is e^{-i*pi/3*(-1)^{x+y}}.
H(q0) on the q[0] register:
- Amplitude of |0,y> = (amp(|0,y>) + amp(|1,y>))/sqrt(2)
- Amplitude of |1,y> = (amp(|0,y>) - amp(|1,y>))/sqrt(2)

For y=0: A(|00>)=(e^{-ipi/3}+e^{ipi/3})/2sqrt(2) => P=cos^2(pi/3)/2=0.125
         A(|10>)=(e^{-ipi/3}-e^{ipi/3})/2sqrt(2) => P=sin^2(pi/3)/2=0.375
For y=1: symmetric => P(|01>)=0.125, P(|11>)=0.375

### Reference answer

{'predicted_probs': {'0': 0.125, '1': 0.125, '2': 0.375, '3': 0.375}, 'explanation': 'Step-by-step state evolution:\n1. |00> -> H,H -> |++> = (|00>+|01>+|10>+|11>)/2\n2. ZZ(pi/3) via CNOT-Rz(2pi/3)-CNOT:\n   Same-parity (|00>,|11>) get phase e^{-i*pi/3}, cross-parity (|01>,|10>) get e^{+i*pi/3}.\n   State: (e^{-ipi/3}|00> + e^{ipi/3}|01> + e^{ipi/3}|10> + e^{-ipi/3}|11>)/2\n3. H on q[0]: transforms |0> -> (|0>+|1>)/sqrt(2), |1> -> (|0>-|1>)/sqrt(2)\n   Regrouping by q[0] value:\n   For q[1]=0: amplitude of |00> = (e^{-ipi/3}+e^{ipi/3})/2sqrt(2) = cos(pi/3)/sqrt(2) = 0.25*sqrt(2)\n   For q[1]=0: amplitude of |10> = (e^{-ipi/3}-e^{ipi/3})/2sqrt(2) = -i*sin(pi/3)/sqrt(2)\n   For q[1]=1: amplitude of |01> = (e^{ipi/3}+e^{-ipi/3})/2sqrt(2) = cos(pi/3)/sqrt(2)\n   For q[1]=1: amplitude of |11> = (e^{ipi/3}-e^{-ipi/3})/2sqrt(2) = i*sin(pi/3)/sqrt(2)\n\n   P(|00>) = cos^2(pi/3)/2 = 0.125\n   P(|01>) = cos^2(pi/3)/2 = 0.125\n   P(|10>) = sin^2(pi/3)/2 = 0.375\n   P(|11>) = sin^2(pi/3)/2 = 0.375\n\nThe H gate on q[0] converts the ZZ phase into measurable probability, showing that |10> and |11> dominate (sin^2(pi/3) > cos^2(pi/3)).'}

## isqExpand/front/7

- task_id: `isqExpand/front/7`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `basic`
- concept_tags: `error_correction`, `phase_flip_code`, `hadamard_basis`
- source: `isq_expansion`
- dataset_index: `5014`

### Prompt

Write isQ code for the following quantum task: implements a 3-qubit phase-flip code encoder and demonstrates that it correctly encodes |+⟩.

The phase-flip code encodes in the Hadamard basis:
- |0⟩_L = |+++⟩
- |1⟩_L = |---⟩

Encoding steps for input |0⟩:
1. Apply H to all three qubits (creating |+++⟩).
2. This is already the encoded |0⟩_L.

Requirements:
- Declare global `qbit q[3];`
- Apply H to all three qubits.
- Then apply H to all (to convert back to computational basis for measurement).
- Measure all qubits. Result should be |000⟩.

### Chain-of-thought reasoning

## Reasoning
1. Start |000⟩.
2. Apply H to all: |+++⟩ = encoded |0⟩_L.
3. Apply H to all again: H*H = I, returns to |000⟩.
4. Measurement yields |000⟩ with probability 1.
