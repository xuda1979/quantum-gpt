# ISQ training COT RAG corpus: quantum_algorithms shard 74

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/2013

- task_id: `isqTrain/2013`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1171`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;
qbit q[4];
procedure main() {
    X(q[0]);
    X(q[1]);
    X(q[2]);
    Toffoli(q[0], q[1], q[3]);
    M(q[3]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes 4 qubits, applies X gates to q[0], q[1], and q[2], followed by a Toffoli gate on q[0], q[1] (controls) and q[3] (target).
2. Initial state is |0000>. After the three X gates, the state becomes |1110>.
3. The Toffoli gate flips the target q[3] because both controls q[0] and q[1] are in the |1> state.
4. The state evolves to |1111>. Measuring q[3] yields |1> with certainty.

Predicted probability distribution: {'1': 1.0}

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Multiplier LSB of 1*3: product_bit0=1 with P=1.0.'}

## isqTrain/4327

- task_id: `isqTrain/4327`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`, `superposition`
- source: `isq_train_cot`
- dataset_index: `847`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit q[4];

procedure main() {
    // Put input a in superposition, set b=1
    H(q[0]);
    X(q[1]);
    // Half adder: sum = a XOR b
    CNOT(q[0], q[2]);
    CNOT(q[1], q[2]);
    // Carry = a AND b
    Toffoli(q[0], q[1], q[3]);
    // Measure sum and carry
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[2]);
    M(q[3]);
}

```

### Chain-of-thought reasoning

Step 1: Initial state is |0000>.
Step 2: H(q[0]) puts q[0] in superposition -> |+000> = (1/sqrt2)(|0000> + |1000>).
Step 3: X(q[1]) flips q[1] -> (1/sqrt2)(|0100> + |1100>).
Step 4: CNOT(q[0], q[2]) computes a XOR 0 into q[2] -> (1/sqrt2)(|0100> + |1110>).
Step 5: CNOT(q[1], q[2]) computes a XOR b into q[2]. Since q[1] is always 1, it flips q[2] -> (1/sqrt2)(|0110> + |1100>).
Step 6: Toffoli(q[0], q[1], q[3]) computes a AND b into q[3] -> (1/sqrt2)(|0110> + |1101>).
Step 7: HZH on q[0] applies X(q[0]) -> (1/sqrt2)(|1110> + |0101>).
Step 8: Measurements M(q[2]) and M(q[3]) are applied, but we look at the full state probabilities.
The probability distribution over the full 4 qubits is:
|0110> (binary 6, so q[3]q[2]q[1]q[0] = 0110, which is q[0]=0, q[1]=1, q[2]=1, q[3]=0) -> |0110>: 0.5
|0101> (binary 5, so q[3]q[2]q[1]q[0] = 0101, which is q[0]=1, q[1]=0, q[2]=1, q[3]=0) -> |0101>: 0.5

Wait, let's recheck the isQ bitstring indexing for --probs output:
"earlier measured qubit = higher bit"
Wait, isQ docs say q[0] is the right-most bit in the ket notation? Usually q[0] is the 0th bit. Let's assume standard q[3]q[2]q[1]q[0].
State 1: |0110>. q[3]=0, q[2]=1, q[1]=1, q[0]=0.
State 2: |0101>. q[3]=0, q[2]=1, q[1]=0, q[0]=1.
Expected probabilities: {|0110>: 0.5, |0101>: 0.5}.

Let's double check step 6:
State was (1/sqrt2)(|0110> + |1100>)
Wait, q[0] is right-most bit.
|0110> -> q[3]=0, q[2]=1, q[1]=1, q[0]=0. So a=0, b=1, sum = 0 XOR 1 = 1 (q[2]=1), carry = 0 AND 1 = 0 (q[3]=0).
|1100> -> q[3]=1, q[2]=1, q[1]=1, q[0]=0? NO.
Let's trace bitstrings properly:
Initial: |q[3] q[2] q[1] q[0]> = |0 0 0 0>
H(q[0]): 1/sqrt(2) * (|0 0 0 0> + |0 0 0 1>)
X(q[1]): 1/sqrt(2) * (|0 0 1 0> + |0 0 1 1>)
CNOT(q[0], q[2]):
If q[0]=0 (|0010>), q[2] remains 0 -> |0010>
If q[0]=1 (|0011>), q[2] becomes 1 -> |0111>
State: 1/sqrt(2) * (|0 0 1 0> + |0 1 1 1>)
CNOT(q[1], q[2]):
Since q[1] is always 1, q[2] is flipped.
If q[2]=0, becomes 1 -> |0110>
If q[2]=1, becomes 0 -> |0101>
State: 1/sqrt(2) * (|0 1 1 0> + |0 1 0 1>)

### Reference answer

{'predicted_probs': {'0001': 0.5, '0010': 0.5}, 'explanation': 'This isQ program operates on 4 qubit(s). The measurement probability distribution is: P(|0001>) = 0.5000, P(|0010>) = 0.5000.'}

## isqTrain/3719

- task_id: `isqTrain/3719`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `814`

### Prompt

Write an isQ program that QAOA (p=1) for the MaxCut problem on a 3-node star graph with edges [(0, 1), (0, 2)]. Use parameters gamma=1.000 and beta=0.500. The circuit:
1. Initialize all qubits in superposition
2. Apply cost unitary: for each edge, use CNOT-Rz-CNOT
3. Apply mixer: Rx(2*beta) on each qubit
4. Measure all 3 qubits

### Chain-of-thought reasoning

Let me trace through this QAOA circuit for MaxCut on a 3-node star graph with edges [(0,1), (0,2)].

**Goal**: Implement QAOA p=1 for MaxCut on a 3-node star graph to find optimal bipartition.

**Qubits**: 3 qubits (q[0], q[1], q[2]), all measured.

**Step-by-step evolution**:

1. **Initial state**: |000⟩

2. **Hadamard on all**: H⊗3 |000⟩ = |+++⟩ = (1/√8) Σ_{x∈{0,1}³} |x⟩

3. **Cost unitary for edge (0,1)**: CNOT(0,1) Rz(2γ, 1) CNOT(0,1)
   - This applies exp(-iγ Z₀Z₁) when qubits 0 and 1 are in different computational basis states, the phase is -γ; when same, phase is +γ.
   - Actually, let me be more precise: CNOT-Rz(2γ)-CNOT applies exp(-iγ Z₀Z₁) to the state.
   
4. **Cost unitary for edge (0,2)**: Similarly applies exp(-iγ Z₀Z₂)

5. **Mixer**: Rx(2β) on each qubit with β=0.5, so Rx(1.0) on each.

Let me compute the predicted output more carefully.

After Hadamards: state is |+++⟩ = (1/2√2)(|000⟩ + |001⟩ + |010⟩ + |011⟩ + |100⟩ + |101⟩ + |110⟩ + |111⟩)

For the cost unitary with γ=1:
The phase for each basis state depends on the cut value. For edge (0,1) and (0,2):
- |000⟩: same partition for (0,1) and (0,2) → phase exp(i·1·(1+1)) = exp(2i)
- |001⟩: different for (0,2), same for (0,1) → exp(i·(1-1)) = exp(0) = 1
- Wait, let me reconsider.

The ZZ operator: Z₀Z₁ has eigenvalue +1 when both same, -1 when different.

For exp(-iγ Z₀Z₁):
- Same (both 0 or both 1): eigenvalue +1, phase exp(-iγ)
- Different: eigenvalue -1, phase exp(iγ)

With γ=1:

Edge (0,1):
- |000⟩, |001⟩: q0=0, q1=0 → same → exp(-i)
- |010⟩, |011⟩: q0=0, q1=1 → different → exp(i)
- |100⟩, |101⟩: q0=1, q1=0 → different → exp(i)
- |110⟩, |111⟩: q0=1, q1=1 → same → exp(-i)

Edge (0,2):
- |000⟩, |010⟩: q0=0, q2=0 → same → exp(-i)
- |001⟩, |011⟩: q0=0, q2=1 → different → exp(i)
- |100⟩, |110⟩: q0=1, q2=0 → different → exp(i)
- |101⟩, |111⟩: q0=1, q2=1 → same → exp(-i)

Combined cost phase for each basis state:
- |000⟩: exp(-i)·exp(-i) = exp(-2i)
- |001⟩: exp(-i)·exp(i) = 1
- |010⟩: exp(i)·exp(-i) = 1
- |011⟩: exp(i)·exp(i) = exp(2i)
- |100⟩: exp(i)·exp(i) = exp(2i)
- |101⟩: exp(i)·exp(-i) = 1
- |110⟩: exp(-i)·exp(i) = 1
- |111⟩: exp(-i)·exp(-i) = exp(-2i)

After cost unitary, the state is:
(1/2√2)[exp(-2i)|000⟩ + |001⟩ + |010⟩ + exp(2i)|011⟩ + exp(2i)|100⟩ + |101⟩ + |110⟩ + exp(-2i)|111⟩]

Now apply Rx(1.0) on each qubit. Rx(θ) = exp(-iθX/2), so Rx(1.0) = exp(-

## isqQA/quantum_algorithms/135_comparison

- task_id: `isqQA/quantum_algorithms/135_comparison`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `comparison`, `algorithm`, `Swap测试`
- source: `qa_pipeline`
- dataset_index: `4082`

### Prompt

在量子机器学习与量子算法设计中，Swap测试和Hadamard测试都常被用于提取量子态之间的内积或重叠度信息。请从数学原理、资源开销以及适用场景等方面深入对比这两种算法的优缺点，并探讨Swap测试在处理高维未知量子态时的局限性。最后，请使用isQ语言编写一段代码，实现一个针对两个单量子比特态的Swap测试（共三个量子比特），要求不直接使用SWAP关键字，而是利用CNOT和Toffoli门等效构造受控SWAP（CSWAP）操作。

### Reference answer

<thought>
1. 数学原理与逻辑推导：
Swap测试的核心在于引入一个辅助比特，通过控制两个寄存器之间的交换操作来提取保幅。假设待测态为 $|\psi\rangle$ 和 $|\phi\rangle$，初始态为 $|0\rangle|\psi\rangle|\phi\rangle$。对辅助比特作用Hadamard门后，系统处于 $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)|\psi\rangle|\phi\rangle$。执行受控SWAP（CSWAP）后，状态变为 $\frac{1}{\sqrt{2}}(|0\rangle|\psi\rangle|\phi\rangle + |1\rangle|\phi\rangle|\psi\rangle)$。再次对辅助比特作用H门，得到 $\frac{1}{2}|0\rangle(|\psi\rangle|\phi\rangle + |\phi\rangle|\psi\rangle) + \frac{1}{2}|1\rangle(|\psi\rangle|\phi\rangle - |\phi\rangle|\psi\rangle)$。测量辅助比特得到0的概率为 $P(0) = \frac{1}{2}(1 + |\langle\psi|\phi\rangle|^2)$。
相比之下，Hadamard测试旨在估计某一酉算符期望值或态的相位。它利用辅助比特控制酉操作 $U$，最终测量辅助比特在X和Y基上的期望来获取 $\langle\psi|U|\psi\rangle$ 的实部与虚部。

2. 算法对比与局限性分析：
- 适用场景与优势：Swap测试的最大优势在于它是“黑盒”比较。只要给定两个量子态的物理制备线路，无需知道它们的具体数学描述或全局相位，即可直接在量子硬件上估计它们的保幅。这在量子指纹识别、量子聚类分析中极为关键。而Hadamard测试适用的是已知酉操作的场景，用于提取如哈密顿量期望值等特征。
- 缺点与局限性：首先，Swap测试只能获取内积的绝对值平方 $|\langle\psi|\phi\rangle|^2$，丢失了极其重要的相位信息。其次，在面对高维或多量子比特态时，CSWAP门的深度和数量会线性增加，线路极深，极大地放大了NISQ时代的硬件噪声。最后，如果 $|\psi\rangle$ 和 $|\phi\rangle$ 极其相似（保幅接近1），则 $P(0)$ 趋近于1，需要极高的采样复杂度 $O(1/\epsilon^2)$ 才能以足够的精度分辨两者差异，容易陷入采样瓶颈。

3. isQ代码构造逻辑：
为规避直接使用SWAP门，采用标准分解：CSWAP(c, t1, t2) 可分解为 CNOT(t1, t2); Toffoli(c, t2, t1); CNOT(t1, t2); 
验证逻辑：当c=0时，Toffoli无效，连续两次CNOT(t1, t2)抵消；当c=1时，CNOT(t1, t2)后Toffoli反转t1，再CNOT恢复t2，等效于t1与t2互换。
在isQ中，全局声明3个量子比特：q[0]为辅助比特，q[1]和q[2]为两个待测试的量子比特态。为了作为演示，我们将两个态初始化为相同的 $|+\rangle$ 态，预期测量辅助比特得到0的概率为1.0。
</thought>

在量子算法设计中，Swap测试与Hadamard测试是提取量子态特征的两个核心子程序，它们在数学原理和应用场景上有着本质的区别。

**一、 算法原理与优缺点对比**
1. **数学原理差异**：
Swap测试的目标是估计两个给定状态之间的保幅。通过引入辅助比特、Hadamard门和受控SWAP（CSWAP）操作，辅助比特最终处于 $|0\rangle$ 的概率与保幅直接相关，即 $P(0) = \frac{1 + |\langle\psi|\phi\rangle|^2}{2}$。而Hadamard测试的原理是通过控制酉操作 $U$ 作用于目标态，通过测量辅助比特的X和Y方向的期望值，分别提取出 $\langle\phi|U|\psi\rangle$ 的实部和虚部。

2. **适用场景与优势**：
- **Swap测试的优势**在于其“状态比较”能力。它不需要用户提供任何已知的酉演化算符，只要硬件上物理实现了两个态的制备，就可以盲测它们的相似度。此外，Swap测试对全局相位不敏感，能够准确反映物理态的等效性，这是经典内积计算难以直接映射的。
- **Hadamard测试的优势**在于能够提取复杂的相位信息（复数内积），且如果 $U$ 具有特定的稀疏或局域结构（如变分量子本征求解器中的哈密顿量项），其线路深度通常比Swap测试浅得多。

3. **Swap测试的局限性**：
- **信息丢失**：Swap测试只能测量绝对值平方，丢失了相对相位信息。
- **高维扩展性差**：对于由多个量子比特组成的高维态，SWAP操作需要逐位执行CSWAP。在NISQ（含噪声中等规模量子）设备上，多控门会引入巨大的量子门深度和极高的错误率。
- **采样复杂度瓶颈**：当两个量子态高度相似时（即 $|\langle\psi|\phi\rangle|^2 \approx 1$），测量结果的方差极小，需要呈指数级增加的测量次数才能将其区分开来，这限制了其在某些量子机器学习模型（如量子核方法评估相似性）中的收敛速度。

**二、 isQ代码实现：三量子比特Swap测试**
以下代码演示了如何测试两个单量子比特态的重叠度。我们通过引入辅助比特，并利用CNOT与Toffoli门组合来等效实现受控SWAP操作。

```isQ
import std;

qbit q[3]; // q[0]: 辅助比特, q[1]: 态 |psi>, q[2]: 态 |phi>

procedure main() {
    // 初始化：为了展示最大重叠度，我们将两个态都制备为 |+> 态
    // 预期最终内积为 1.0，即测量辅助比特 q[0] 得到 0 的概率为 100%
    H(q[1]);
    H(q[2]);

    // 步骤1：对辅助比特施加Hadamard门，创建叠加态
    H(q[0]);

    // 步骤2：实现受控SWAP（CSWAP），不使用SWAP关键字
    // CSWAP逻辑等价于以下三步操作的组合
    CNOT(q[1], q[2]);
    Toffoli(q[0], q[2], q[1]);
    CNOT(q[1], q[2]);

    // 步骤3：再次对辅助比特施加Hadamard门产生干涉
    H(q[0]);

    // 步骤4：测量辅助比特
    // 量子态坍缩，统计0出现的频率即可估算保幅
    M(q[0]);
}
```

## isqQA/quantum_algorithms/48_math_derivation

- task_id: `isqQA/quantum_algorithms/48_math_derivation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `math_derivation`, `algorithm`, `量子振幅放大`
- source: `qa_pipeline`
- dataset_index: `2392`

### Prompt

请严密推导量子振幅放大算法的核心数学原理。详细说明算子Q的定义，推导量子态在由"好"态和"坏"态张成的二维子空间中的演化过程，并最终计算出经过k次迭代后的测量成功概率。

### Reference answer

<think>
推导量子振幅放大算法的核心思路是“空间降维”与“几何变换”。首先，利用投影算子将复杂的系统状态空间划分为“好”态和“坏”态两个正交子空间，从而将多维量子态问题简化为二维子空间内的参数化表示，引入角度变量$\theta$来表征初始成功概率。

其次，构造核心迭代算子$Q$。$Q$实质上由关于“好”态子空间的相位翻转（反射）和关于初始态的反射复合而成。根据线性代数中的几何性质，在同一平面内连续执行两次反射操作，等效于一次角度为$2\theta$的旋转。

最后，分析量子态的演化轨迹。将初始态代入该二维旋转模型，经过$k$次$Q$算子迭代后，系统状态与“好”态基矢的夹角被线性放大为$(2k+1)\theta$。直接计算该末态在目标子空间上的投影幅度的模平方，即可严密得出测量成功的概率表达式，并由此推导出达到最高成功率所需的最优迭代次数。
</think>

量子振幅放大是Grover算法的数学推广，其核心在于通过反复将量子态向目标子空间"反射"来线性放大成功概率。以下是完整的数学推导过程：

**1. 初始设置与空间划分**
设 $A$ 是作用在 $n$ 量子比特初态 $|0\rangle^{\otimes n}$ 上的任意酉算子，系统状态为 $|\psi\rangle = A|0\rangle$。
定义投影算子 $\Pi_{Good}$ 和 $\Pi_{Bad}$ 将空间划分为两个正交子空间：
- "好"态（目标态）：$|\psi_{Good}\rangle = \frac{\Pi_{Good}|\psi\rangle}{\sqrt{p_{good}}}$，概率 $p_{good} = \langle\psi|\Pi_{Good}|\psi\rangle$
- "坏"态（非目标态）：$|\psi_{Bad}\rangle = \frac{\Pi_{Bad}|\psi\rangle}{\sqrt{1-p_{good}}}$

**2. 振幅放大算子Q的构造**
核心算子 $Q$ 定义为：$Q = -A S_0 A^\dagger S_{\chi}$
其中：
- $S_{\chi} = I - 2\Pi_{Good}$ 是关于目标态的反射（Oracle）
- $S_0 = I - 2|0\rangle\langle0|$ 是关于初态的反射

**3. 约化至二维子空间的矩阵推导**
引入 $\sin\theta = \sqrt{p_{good}}$，初始态可写为：$|\psi\rangle = \sin\theta|\psi_{Good}\rangle + \cos\theta|\psi_{Bad}\rangle$
我们分析 $Q$ 算子在 $\{|\psi_{Good}\rangle, |\psi_{Bad}\rangle\}$ 张成的二维子空间中的行为：
- $S_{\chi}|\psi\rangle = -\sin\theta|\psi_{Good}\rangle + \cos\theta|\psi_{Bad}\rangle$
- 令 $|\psi^{\perp}\rangle = A|0\rangle^{\perp}$，经过代数化简可知 $A S_0 A^\dagger$ 作用等效于对 $|\psi\rangle$ 做反射。最终 $Q$ 的约化矩阵表示为：
$$ Q = \begin{pmatrix} \cos(2\theta) & -\sin(2\theta) \\ \sin(2\theta) & \cos(2\theta) \end{pmatrix} $$
这是一个旋转矩阵，每次作用将态矢量在二维空间中向"好"态方向旋转 $2\theta$。

**4. k次迭代的概率计算**
应用 $k$ 次 $Q$ 算子后，量子态演化为：
$$ Q^k |\psi\rangle = \sin((2k+1)\theta)|\psi_{Good}\rangle + \cos((2k+1)\theta)|\psi_{Bad}\rangle $$
此时，测量得到"好"态的概率精确为：
$$ P_{success}(k) = \sin^2((2k+1)\theta) $$
为了使概率逼近1，需选择最优迭代次数 $k \approx \frac{\pi}{4\arcsin(\sqrt{p_{good}})} - \frac{1}{2}$。当 $p_{good} \ll 1$ 时，$k \approx \frac{\pi}{4\sqrt{p_{good}}}$，实现了相对经典蒙特卡洛采样 $O(1/p_{good})$ 的二次加速。

## isqQA/quantum_algorithms/103_math_derivation

- task_id: `isqQA/quantum_algorithms/103_math_derivation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `math_derivation`, `algorithm`, `Shor算法概述与量子优势`
- source: `qa_pipeline`
- dataset_index: `588`

### Prompt

在Shor算法中，量子相位估计和量子傅里叶变换是实现指数级加速的核心。请严密推导在Shor算法的量子阶寻找部分中，经过模幂运算和逆量子傅里叶变换（IQFT）后，测量前系统的量子态演化过程。假设我们有一个黑盒酉算子 $U_{y,N}|x
angle|0
angle = |x
angle|y^x mod N
angle$，请给出详细的数学推导，并探讨为什么测量该态能以极大概率提取出阶 $r$ 的信息，从而体现指数级量子优势。进一步地，请使用isQ语言实现该量子态准备和逆量子傅里叶变换的核心代码片段。

### Reference answer

<think>
首先，对第一寄存器施加Hadamard变换生成均匀叠加态，随后通过黑盒算子执行模幂运算，使两个寄存器产生量子纠缠。由于模幂运算具有周期$r$，若以第二寄存器为条件，第一寄存器的态将坍缩为一系列等间距（间隔为$r$）的态的线性叠加。

接着，对第一寄存器应用逆量子傅里叶变换（IQFT）。在数学推导上，这一步是将时域上的周期性求和转换为频域上的概率幅干涉。经过严密的复数求和与相位化简，原先离散的周期性态会转化为概率幅高度集中在特定整数上的量子态，这些峰值正比于 $cQ/r$ 的最近整数。

最后，通过测量该量子态，我们能够以极高概率获得包含 $c/r$ 信息的相位估计值。结合经典连分数算法即可提取出阶 $r$。量子优势的核心在于，量子傅里叶变换能在多项式时间内处理规模呈指数级增长的量子态叠加，从而打破了经典算法在因式分解上的指数级时间壁垒。
</think>

<verify>
为了推导Shor算法中阶寻找部分的量子态演化，我们假设第一寄存器有 $n$ 个量子比特，大小为 $Q = 2^n$，第二寄存器用于存储模幂结果。
1. **初始化与叠加态**：
初始态为 $|\psi_0\rangle = |0\rangle^{\otimes n}|0\rangle^{\otimes m}$。
对第一寄存器应用Hadamard门，得到：
$|\psi_1\rangle = \frac{1}{\sqrt{Q}} \sum_{x=0}^{Q-1} |x\rangle|0\rangle$。

2. **模幂运算**：
应用酉算子 $U_{y,N}$，演化过程为：
$|\psi_2\rangle = \frac{1}{\sqrt{Q}} \sum_{x=0}^{Q-1} |x\rangle|y^x \bmod N\rangle$。
设函数 $f(x) = y^x \bmod N$ 的周期为 $r$。对于第二寄存器的某个确定测量值 $z_0 = y^{x_0} \bmod N$，满足此条件的 $x$ 的集合为 $x = x_0 + kr$ （其中 $k$ 为整数）。若假设 $Q$ 远大于 $r$ 且 $r$ 整除 $Q$，则可近似认为每组有 $K = Q/r$ 个解。此时，第一寄存器的态坍缩（或剥离出）为周期态：
$|\psi_{periodic}\rangle = \frac{1}{\sqrt{K}} \sum_{k=0}^{K-1} |x_0 + kr\rangle$。

3. **逆量子傅里叶变换 (IQFT)**：
IQFT的作用是将基态从 $|x\rangle$ 变为 $\frac{1}{\sqrt{Q}} \sum_{c=0}^{Q-1} e^{-2\pi i x c / Q} |c\rangle$。
将周期态代入IQFT的定义中，得到最终的演化态：
$|\psi_3\rangle = \frac{1}{\sqrt{K}} \sum_{k=0}^{K-1} \left( \frac{1}{\sqrt{Q}} \sum_{c=0}^{Q-1} e^{-2\pi i (x_0 + kr) c / Q} |c\rangle \right)$
整理求和项：
$|\psi_3\rangle = \frac{1}{\sqrt{r}} \sum_{c=0}^{Q-1} \left( \frac{1}{K} \sum_{k=0}^{K-1} e^{-2\pi i k r c / Q} \right) e^{-2\pi i x_0 c / Q} |c\rangle$
括号内的等比数列求和当且仅当 $\frac{rc}{Q}$ 接近某个整数 $d$ 时，即 $c \approx \frac{d Q}{r}$ 时，各项的相位趋于一致，发生相长干涉，使得振幅最大。测量第一寄存器将以极高概率得到满足此条件的整数 $c$。

4. **量子优势分析**：
由于 $Q \ge N^2$，根据数论中的连分数算法，我们可以从分数 $c/Q$ 唯一且精确地提取出分母 $r$。这表明量子态干涉一次性提取了周期特征，将经典计算机需要 $O(N)$ 甚至次指数级时间的阶寻找问题，降维到了多项式级的量子门操作 $O((\log N)^3)$。

5. **isQ代码实现**：
下面展示核心的叠加态初始化和逆QFT代码。为了避免使用SWAP门，我们在经典后处理中逆序读取比特。
```isQ
import std;

const int N = 4; // 寄存器比特数
qbit q1[N]; // 第一寄存器
qbit q2[N]; // 第二寄存器

// 假设存在模幂运算的黑盒或分解实现，此处省略其内部具体实现
// procedure modular_exponentiation(int power, qbit target) { ... }

procedure main() {
    // 1. 初始化第一寄存器为均匀叠加态
    for i in 0:N {
        H(q1[i]);
    }
    
    // 2. 模幂运算概念性调用
    // for i in 0:N {
    //    ctrl @[q1[i]] modular_exponentiation(pow(2, i), q2);
    // }

    // 3. 逆量子傅里叶变换 (IQFT)
    for i in 0:N {
        H(q1[i]);
        for j in (i+1):N {
            // 角度计算为 -pi / 2^(j-i)
            double angle = -3.1415926535 / pow(2.0, j - i);
            ctrl @[q1[j]] Rz(angle, q1[i]);
        }
    }
    
    // 测量（省略具体经典读取步骤）
}
```
上述代码严格遵循了isQ语言规范，利用受控Rz门构建了无SWAP的逆QFT电路。
</verify>

在Shor算法的量子阶寻找子程序中，其指数级加速的本质来源于量子态的相干叠加与干涉效应。我们通过严密的数学推导来分析这一量子态演化过程。

假设第一寄存器包含 $n$ 个量子比特，其状态空间维度为 $Q = 2^n$，第二寄存器用于存储模幂结果。演化步骤如下：

1. **叠加态制备**：
系统初始化为全 $|0\rangle$ 态，对第一寄存器的所有量子比特应用Hadamard门，系统进入等权叠加态：
$$|\psi_1\rangle = \frac{1}{\sqrt{Q}} \sum_{x=0}^{Q-1} |x\rangle|0\rangle$$

2. **模幂运算酉变换**：
利用黑盒酉算子 $U_{y,N}$ 执行操作 $|x\rangle|0\rangle \rightarrow |x\rangle|y^x \bmod N\rangle$。由于函数 $f(x) = y^x \bmod N$ 具有周期 $r$，这会在计算基中产生强烈的关联：
$$|\psi_2\rangle = \frac{1}{\sqrt{Q}} \sum_{x=0}^{Q-1} |x\rangle|y^x \bmod N\rangle$$
在此状态下，如果我们将第二寄存器剥离（或者测量它使其坍缩到某个本征态 $|z_0\rangle = |y^{x_0} \bmod N\rangle$），第一寄存器的态将变为一个周期为 $r$ 的周期态（设 $r$ 整除 $Q$，周期项数为 $K=Q/r$）：
$$|\psi_{periodic}\rangle = \frac{1}{\sqrt{K}} \sum_{k=0}^{K-1} |x_0 + kr\rangle$$

3. **逆量子傅里叶变换 (IQFT) 的干涉提取**：
对第一寄存器应用逆量子傅里叶变换。IQFT的作用是将基态映射为：$|x\rangle \rightarrow \frac{1}{\sqrt{Q}} \sum_{c=0}^{Q-1} e^{-2\pi i x c / Q} |c\rangle$。代入周期态得：
$$|\psi_3\rangle = \frac{1}{\sqrt{K}} \sum_{k=0}^{K-1} \left( \frac{1}{\sqrt{Q}} \sum_{c=0}^{Q-1} e^{-2\pi i (x_0 + kr) c / Q} |c\rangle \right)$$
重新排列求和顺序：
$$|\psi_3\rangle = \frac{1}{\sqrt{r}} \sum_{c=0}^{Q-1} \left( \frac{1}{K} \sum_{k=0}^{K-1} e^{-2\pi i k r c / Q} \right) e^{-2\pi i x_0 c / Q} |c\rangle$$
这里体现了量子相长干涉：括号内的等比数列求和，只有当 $\frac{rc}{Q}$ 极其接近某个整数 $d$ 时，即 $c \approx \frac{dQ}{r}$ （$0 \le d < r$）时，各项的相位差趋近于0，振幅会急剧叠加放大；否则会产生相消干涉，振幅趋于零。

4. **量子优势的体现**：
测量第一寄存器将以极高的概率得到满足 $\left| \frac{c}{Q} - \frac{d}{r} \right| \le \frac{1}{2Q}$ 的整数 $c$。由于我们设定 $Q \ge N^2$，分母 $Q$ 足够大，通过经典的连分数算法，可以从 $c/Q$ 唯一且确定性地反推出分母 $r$。这种从频率域（相位干涉）提取周期的方法，成功将大数质因数分解的时间复杂度从经典算法的亚指数级 $O(e^{(\log N)^{1/3}})$ 降低到了多项式级 $O((\log N)^3)$，这就是Shor算法展现出的绝对量子优势。

以下是使用isQ语言编写的核心部分代码，包含初态制备及无SWAP门的逆QFT实现：

```isQ
import std;

const int N = 4; // 定义第一寄存器比特数
qbit reg1[N]; // 第一寄存器
qbit reg2[N]; // 第二寄存器(模幂运算用)

procedure main() {
    // 1. 制备第一寄存器的均匀叠加态
    for i in 0:N {
        H(reg1[i]);
    }
    
    // 2. 此处应执行模幂运算，通常通过受控模加和模乘门分解
    // 伪代码示意: for i in 0:N { ctrl @[reg1[i]] U_power(1 << i, reg2); }

    // 3. 执行逆量子傅里叶变换 (IQFT)
    for i in 0:N {
        H(reg1[i]);
        // 依次与后续比特进行受控逆向旋转
        for j in (i+1):N {
            // 计算旋转角度 -π / 2^(j-i)
            double angle = -3.1415926535 / pow(2.0, j - i);
            ctrl @[reg1[j]] Rz(angle, reg1[i]);
        }
    }
    
    // 4. 测量第一寄存器以提取相位
    for i in 0:N {
        int res = M(reg1[i]);
    }
}
```
在代码中，我们通过嵌套循环和受控`Rz`门实现了`IQFT`，省略了标准`QFT`电路末端的`SWAP`操作，这种省略在物理实现上极大地降低了电路深度，只需在经典后处理阶段将读出的比特串逆序即可还原真实的十进制数值。

## isqTrain/1110

- task_id: `isqTrain/1110`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `interference`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2680`

### Prompt

Write an isQ program that implements a variant of the simon_algorithm pattern using out[2] -> out[4]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement Simon's algorithm with period s=11 using an expanded 4-qubit output register, measuring only the 2 input qubits.

Qubits: 6 total (q[2] input, out[4] output); only q[0], q[1] are measured. The extra output qubits out[2], out[3] remain in |0⟩ throughout.

State evolution:
1. **Initial**: |0000⟩_out ⊗ |00⟩_q
2. **H⊗H on q**: |0000⟩_out ⊗ (|00⟩+|01⟩+|10⟩+|11⟩)/2
3. **Oracle f**: (|0000⟩|00⟩ + |0001⟩|01⟩ + |0001⟩|10⟩ + |0000⟩|11⟩)/2 — maps to out[0:2] only; out[2:4] stay |00⟩. Since f(00)=f(11)=00 and f(01)=f(10)=01, pairs with same f-value interfere.
4. **H⊗H on q**: Applying H to input disentangles it — terms |00⟩ and |11⟩ (same f) interfere constructively to |00⟩, while |01⟩ and |10⟩ (same f) interfere to |11⟩.
5. **Final state**: (|0000⟩_out ⊗ |00⟩_q + |0001⟩_out ⊗ |11⟩_q)/√2

Measurement probabilities: Since out is unmeasured and traced out, measuring q yields |00⟩ with probability 0.5 and |11⟩ with probability 0.5, satisfying y·s = 0 mod 2 for s=11.

## isqTrain/1386

- task_id: `isqTrain/1386`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_multi_register`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2983`

### Prompt

Create an isQ quantum circuit that the Bernstein-Vazirani algorithm to find the secret string s = 10 (MSB first). Use 2 input qubits and 1 ancilla.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Bernstein-Vazirani algorithm.
    *   Secret string: $s = 10$ (MSB first, so $s_0=1, s_1=0$). Wait, isQ array notation typically implies $q[0]$ is the first one used. If $s=10$, let's say $q[0]$ is MSB, so $q[0]$ is 1, $q[1]$ is 0. The oracle applies CNOT for every bit in $s$ that is 1. Thus, only $CNOT(q[0], anc[0])$.
    *   Format: Reasoning section ONLY, starting with "## Reasoning". No code blocks.
    *   Constraints: Concise, precise step-by-step state evolution using Dirac notation. 3-8 lines (or up to 15 for complex).

2.  **Determine the Circuit Steps:**
    *   Initial state: $|00\rangle_q |0\rangle_a$.
    *   Ancilla prep: $X|0\rangle = |1\rangle$, then $H|1\rangle = |-\rangle$. State: $|00\rangle_q |-\rangle_a$.
    *   Input register prep: $H^{\otimes 2}|00\rangle = |+\rangle|+\rangle = \frac{1}{2}\sum_{x \in \{0,1\}^2} |x\rangle$. State: $\frac{1}{2}\sum |x\rangle_q |-\rangle_a$.
    *   Oracle application: CNOT(q[0], anc[0]) for $s=10$ (where $q[0]$ is the '1'). This maps $|x\rangle_q |-\rangle_a \to (-1)^{x_0}|x\rangle_q |-\rangle_a$.
    *   Final Hadamards on input: $H^{\otimes 2} \sum (-1)^{x_0}|x\rangle = |10\rangle_q$ (since $s=10$).
    *   Measurement: Measures $q[0]$ and $q[1]$, yielding $s=10$ with probability 1.0.

3.  **Draft the Reasoning Section:**
    *   *Goal:* Implement Bernstein-Vazirani to find secret string $s=10$.
    *   *Qubits:* 2 input ($q[0], q[1]$) and 1 ancilla ($anc[0]$). Measure the input qubits.
    *   *Evolution:*
        *   Start: $|00\rangle |0\rangle$
        *   Ancilla prep: $X$ then $H$ puts ancilla in $|-\rangle$. State is $|00\rangle |-\rangle$.
        *   Input prep: $H^{\otimes 2}$ on inputs creates uniform superposition $\frac{1}{2}\sum_{x\in\{0,1\}^2} |x\rangle |-\rangle$.
        *   Oracle: CNOT(q[0], anc[0]) phase-kicks back $(-1)^{x_0}$, yielding $\frac{1}{2}\sum_{x\in\{0,1\}^2} (-1)^{x_0} |x\rangle |-\rangle$.
        *   Final H gates: $H^{\otimes 2}$ uncomputes the superposition, isolating the phase as the state $|10\rangle |-\rangle$.
    *   *Probabilities:* Measuring $q[0]$ and $q[1]$ yields bitstring $10$ with certainty.

4.  **Refine and Compress (Target 3-8 lines):**
    *   Line 1: Goal is to find the secret string $s=10$ using the Bernstein-Vazirani algorithm, requiring 2 input qubits and 1 ancilla, measuring the inputs.
    *   Line 2: State evolution starts at $|00\rangle_q|0\rangle_a$.
    *   Line 3: Prepare ancilla as $|-\rangle$ and inputs with $H^{\otimes 2}$ to get $\frac{1}{2}\sum_{x \in \{0,1\}^2} |x\rangle_q |-\rangle_a$.
    *   Line 4: The oracle CNOT(q[0], anc[0]) applies a phase $(-1)^{x_0}$ via phase kickback, evolving the state to $\frac{1}{2}\sum_{x} (-1)^{x_0} |x\rangle_q |-\

## isqTrain/809

- task_id: `isqTrain/809`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `reversible_computing`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5242`

### Prompt

I need an isQ program to implements a variant of the quadratic_form pattern using q[2] -> q[4]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

Let me analyze this task carefully.

The goal is to write an isQ program that implements a variant of the quadratic_form pattern using q[2] -> q[4]. The circuit should use a significantly expanded qubit register compared to the base version, with additional qubits left in the ground state.

Analyzing the circuit requirements:
- It uses `qbit q[4]` (4 qubits)
- H(q[0]) puts q[0] in superposition
- CNOT(q[0], q[1]) copies q[0] to q[1]
- Measures q[1], q[2], q[3]

Expected measurement probabilities: {|000>: 0.5, |100>: 0.5}

Wait, let me think about this. The predicted output measurement probabilities are {|000>: 0.5, |100>: 0.5}.

But the measurements are: M(q[1]), M(q[2]), M(q[3])

After H(q[0]) and CNOT(q[0], q[1]):
- State is (|0000> + |1100>)/sqrt(2) (qubits q[0], q[1], q[2], q[3])

When we measure q[1], q[2], q[3]:
- For |0000>: measuring q[1]=0, q[2]=0, q[3]=0 gives "000"
- For |1100>: measuring q[1]=1, q[2]=0, q[3]=0 gives "100"

So the bitstring is formed with q[1] as the highest bit (measured first).

Wait, looking at the predicted output format: --probs output: array indexed by measurement bitstring (earlier measured qubit = higher bit).

So M(q[1]) is measured first = highest bit, M(q[2]) = middle bit, M(q[3]) = lowest bit.

State after operations:
- Initial: |0000>
- After H(q[0]): (|0000> + |1000>)/sqrt(2)
- After CNOT(q[0], q[1]): (|0000> + |1100>)/sqrt(2)

Measuring q[1], q[2], q[3]:
- If state is |0000>: q[1]=0, q[2]=0, q[3]=0 → bitstring = 000
- If state is |1100>: q[1]=1, q[2]=0, q[3]=0 → bitstring = 100

So probabilities: {|000>: 0.5, |100>: 0.5} ✓

Now the prompt says "using q[2] -> q[4]". This seems to suggest expanding the register. But wait, The circuit should q[4] which has indices q[0], q[1], q[2], q[3].

Actually, re-reading the prompt: "Write an isQ program that implements a variant of the quadratic_form pattern using q[2] -> q[4]."

Hmm, this might mean using a register of size from 2 to 4, or using qubits q[2] to q[4] somehow. But The circuit should q[4] (4 qubits total).

Actually, I think "q[2] -> q[4]" might be describing some transformation or mapping, but Analyzing the circuit requirements, it just uses 4 qubits with the same basic circuit pattern.

Wait, I need to re-read. The task says "The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state."

So the base version might have had fewer qubits (like 2), and now we expand to 4 qubits, with q[2] and q[3] left in ground state.

Let me generate the reasoning:

## Reasoning

1. **Goal**: Implement a quadratic form circuit f(x) = x² mod 2 = x with an expanded 4-qubit register, leaving q[2] and q[3] in |0⟩.

2. **Qubits and measurements**: 4 qubits total (q[0]-q[3]); q[1], q[2], q[3] are measured.

3. **State evolution**:
   - Initial: |0000⟩
   - H(q[0]): (|0000⟩ + |1000⟩)/√2 — superposition on input qubit
   - CNOT(q[0], q[1]): (|0000⟩ + |1100⟩)/√2 — entangled, result copied to q[1]

4. **Expected probabilities**: Measuring q[1]⟨q[2]⟨q[3]⟩

## isqTrain/4415

- task_id: `isqTrain/4415`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5536`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
qbit q[3];

procedure main() {
    // Uniform superposition = QFT(|000>)
    // Start with uniform superposition
    H(q[0]); H(q[1]); H(q[2]);

    // IQFT: process from q[0] to q[2] (no SWAP needed in isQ's qubit ordering)
    H(q[0]);
    ctrl Rz(-pi/2.0, q[0], q[1]);
    H(q[1]);
    ctrl Rz(-pi/4.0, q[0], q[2]);
    ctrl Rz(-pi/2.0, q[1], q[2]);
    H(q[2]);

    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the request:**
    *   Task: Analyze an isQ program, predict measurement probabilities, and provide step-by-step reasoning.
    *   Format: Output only "## Circuit Analysis" followed by the reasoning and predicted probabilities.
    *   Constraint: Concise (3-15 lines), use Dirac notation, no code blocks.
    *   Program:
        

2.  **Trace the quantum state:**
    *   Initial state: $|000\rangle$
    *   After `H(q[0]); H(q[1]); H(q[2]);`: $|+\rangle|+\rangle|+\rangle = \frac{1}{\sqrt{8}} \sum_{x=0}^{7} |x\rangle$. This represents the QFT of $|000\rangle$.
    *   Next, the inverse QFT (IQFT) is applied to this state.
    *   Since QFT followed by IQFT gives the identity operation, the state reverts to $|000\rangle$.
        *   Let's double check standard QFT/IQFT definitions. The code applies H, then controlled Rz, etc. This matches the standard structure of IQFT.
        *   Wait, standard QFT applied to $|0...0\rangle$ gives $\frac{1}{\sqrt{N}} \sum |x\rangle$.
        *   Applying IQFT to $\frac{1}{\sqrt{N}} \sum |x\rangle$ gives $|0...0\rangle$.
        *   Yes, $\text{IQFT} \cdot \text{QFT} |000\rangle = |000\rangle$.
    *   Let's verify the exact gates in the code:
        *   H(q0), H(q1), H(q2) creates $|+++\rangle$.
        *   H(q0) acts on $|+\rangle$ -> $|0\rangle$.
        *   Wait, standard IQFT starts from the *last* qubit. The code applies it from q0 to q2.
        *   Let's check QFT definition: $QFT|x\rangle = \frac{1}{\sqrt{N}} \sum_y e^{2\pi i x y / N} |y\rangle$.
        *   Code for IQFT (forward order: q0 then q1 then q2):
            *   H(q0)
            *   ctrl Rz(-pi/2) q0->q1
            *   H(q1)
            *   ctrl Rz(-pi/4) q0->q2
            *   ctrl Rz(-pi/2) q1->q2
            *   H(q2)
        *   This exactly matches standard IQFT without the final swaps, assuming isQ maps q0 to bit 0 (least significant). In isQ, $q[0]$ is typically the least significant bit in state $|q_2 q_1 q_0\rangle$.
        *   Thus, QFT|000> = $\frac{1}{\sqrt{8}}\sum |x\rangle$. IQFT($\frac{1}{\sqrt{8}}\sum |x\rangle$) = |000>.
    *   After IQFT, the state is exactly $|000\rangle$.
    *   Then `X(q[0])` is applied.
    *   State becomes $|001\rangle$.
    *   Wait, in bitstring representation for `M(q[0]) M(q[1]) M(q[2])`, `q[0]` is usually the rightmost bit.
    *   If state is $|q_2 q_1 q_0\rangle = |001\rangle$, then $q_0=1, q_1=0, q_2=0$.
    *   Measurement outcome: 100. Wait, The implementation says `{|100>: 1.0}`.
    *   Let's check standard bit ordering in isQ. If $q[0]$ is the highest bit (most significant

### Reference answer

{'predicted_probs': {'100': 1.0}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|100>) = 1.0000.'}
