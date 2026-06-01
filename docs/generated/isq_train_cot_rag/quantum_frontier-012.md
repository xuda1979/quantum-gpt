# ISQ training COT RAG corpus: quantum_frontier shard 12

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/front/20

- task_id: `isqExpand/front/20`
- task_type: `bug_fix`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `vqe`, `bug_fix`, `cnot_direction`, `quantum_chemistry`
- source: `isq_expansion`
- dataset_index: `4759`

### Prompt

I'm getting wrong output from this isQ code. What's the bug and how do I fix it?

```isq
import std;
qbit q[2];

procedure main() {
    // Hartree-Fock state |01>
    X(q[1]);
    // Variational ansatz
    Ry(pi/3.0, q[0]);
    // BUG: CNOT direction reversed
    CNOT(q[1], q[0]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Bug Analysis
The CNOT(q[1], q[0]) uses q[1] as control and q[0] as target.

Buggy circuit:
1. X(q[1]): |01>
2. Ry(pi/3, q[0]): cos(pi/6)|01> + sin(pi/6)|11>
3. CNOT(q[1], q[0]): q[1]=1 in both terms, so flips q[0] in both:
   cos(pi/6)|11> + sin(pi/6)|01> -> wrong state, gives P(|01>)=0.25, P(|11>)=0.75

Correct circuit:
1. X(q[1]): |01>
2. Ry(pi/3, q[0]): cos(pi/6)|01> + sin(pi/6)|11>
3. CNOT(q[0], q[1]): q[0]=0 no flip, q[0]=1 flip q[1]:
   cos(pi/6)|01> + sin(pi/6)|10> -> correct excitation state

Fix: Change CNOT(q[1], q[0]) to CNOT(q[0], q[1]).

## isqExpand/front/54

- task_id: `isqExpand/front/54`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `expert`
- concept_tags: `quantum_chemistry`, `qpe`, `eigenvalue`
- source: `isq_expansion_qa`
- dataset_index: `5411`

### Prompt

什么是量子相位估计（Quantum Phase Estimation, QPE）算法？它在量子化学中如何用于求解基态能量？

### Chain-of-thought reasoning

## 推理
QPE通过控制酉操作和逆QFT提取酉算符的本征相位。在化学中，U=e^{-iHt}的本征相位直接给出能量。QPE精度高但需要深电路，适合容错量子计算机。

### Reference answer

量子相位估计是一种量子算法，用于估计酉算符U的本征值e^{2πiφ}中的相位φ。它是量子计算中最重要的子程序之一。

**算法步骤：**
1. 准备辅助寄存器（t个量子比特）在均匀叠加态：H^⊗t|0⟩^t。
2. 控制酉操作：对每个辅助比特j，施加控制U^{2^j}操作。
3. 逆QFT：对辅助寄存器施加逆量子傅里叶变换。
4. 测量辅助寄存器，得到相位φ的t位二进制近似。

精度：使用t个辅助比特可以估计相位到2^{-t}的精度，成功概率大于1-1/(2(2^t-1))。

**在量子化学中的应用：**
将分子哈密顿量H的时间演化算符U = e^{-iHt}作为QPE的输入。如果能准备一个与基态有非零重叠的初始态|ψ₀⟩：

1. QPE会以|⟨ψ₀|E₀⟩|²的概率输出基态能量E₀对应的相位。
2. 精度由辅助比特数t和时间演化的精度决定。

**优势与挑战：**
- 优势：可以达到指数级精度（多项式资源），无需变分优化。
- 挑战：需要深电路（长时间的受控时间演化），对噪声敏感，需要容错量子计算机。初始态准备也是难题。

QPE被认为是容错时代量子化学计算的首选方法，而VQE是NISQ时代的替代方案。

## isqExpand/front/32

- task_id: `isqExpand/front/32`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `expert`
- concept_tags: `quantum_ml`, `quantum_advantage`, `dequantization`
- source: `isq_expansion_qa`
- dataset_index: `3801`

### Prompt

解释量子机器学习中的量子优势问题。在什么条件下量子机器学习可能优于经典机器学习？

### Chain-of-thought reasoning

## 推理
量子ML的优势取决于问题类型。对量子数据有天然优势，对经典数据的优势受输入瓶颈和去量子化结果的限制。当前没有对一般经典数据的严格量子加速证明。

### Reference answer

量子机器学习的量子优势问题是该领域最核心的开放问题。关于何时量子方法可能优于经典方法，目前的理解如下：

**可能存在优势的情况：**
1. 量子数据：当输入数据本身来自量子系统（如量子态层析、量子过程鉴定），量子处理有天然优势，因为经典方法需要指数级资源描述量子态。
2. 特定问题结构：对于具有隐含量子结构的分类问题，量子核方法可能提供更好的分类边界。
3. 生成模型：玻恩机（Born machine）等量子生成模型可以自然地采样自量子概率分布，这对经典采样器可能是困难的。

**当前限制：**
1. 输入瓶颈：将经典数据加载到量子计算机的成本（振幅编码需要O(2^n)门）可能抵消后续的量子加速。
2. 去量子化：Tang等人的一系列工作表明，某些之前声称有量子优势的算法（如量子推荐系统）可以被经典方法高效近似。
3. 有限的理论保证：对于一般经典数据集，目前没有严格证明量子机器学习有超多项式加速。
4. NISQ限制：当前设备的噪声和量子比特数量限制了实际应用。

总结：量子优势最可能出现在量子数据处理和特定结构化问题上，对一般经典ML问题的优势仍需更多研究。

## isqExpand/front/57

- task_id: `isqExpand/front/57`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `difficult`
- concept_tags: `hamiltonian_simulation`, `xx_interaction`, `basis_change`
- source: `isq_expansion`
- dataset_index: `2599`

### Prompt

实现以下量子计算任务（使用isQ）：implements the XX interaction gate e^{-i*theta*X⊗X} for Hamiltonian simulation.

The decomposition is:
H(q[0]), H(q[1]) -> CNOT(q[0],q[1]) -> Rz(2*theta, q[1]) -> CNOT(q[0],q[1]) -> H(q[0]), H(q[1]).

This works because H*Z*H = X, so HH*ZZ*HH = XX.

Use theta = pi/4 on initial state |00⟩.

Requirements:
- Declare global `qbit q[2];`
- Implement the XX gate.
- Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. |00⟩ is eigenstate of ZZ with eigenvalue +1.
2. Conjugating ZZ by H⊗H gives XX interaction.
3. For XX(pi/4) on |00⟩: |00⟩ = (|++⟩+|+-⟩+|-+⟩+|--⟩)/2 in X basis. But more directly: e^{-i*(pi/4)*XX}|00⟩ = cos(pi/4)|00⟩-i*sin(pi/4)|11⟩ = (|00⟩-i|11⟩)/sqrt(2).
4. P(|00⟩)=0.5, P(|11⟩)=0.5.

## isqExpand/front/127

- task_id: `isqExpand/front/127`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `quantum_machine_learning`, `basis_encoding`, `data_encoding`, `quantum_state_preparation`
- source: `isq_expansion_qa`
- dataset_index: `1904`

### Prompt

详细解释量子机器学习中的basis编码方法。它的优缺点和适用场景是什么？

### Chain-of-thought reasoning

首先分析题目要求，需要详细解释量子机器学习中basis编码的概念、优缺点和适用场景。第一步回顾basis编码的基本定义：将经典二进制数据直接映射到量子计算基态上，例如经典值5映射为|101⟩。第二步详细说明其实现方式，即在|0⟩态基础上对需要翻转的位施加X门。第三步系统梳理优点：直观、可区分、测量友好、电路简单。第四步分析缺点：编码效率低（每qubit仅1bit）、仅限离散数据、不利用量子叠加特性。第五步列举适用场景：离散分类、Grover搜索、组合优化、QRAM、布尔函数评估。第六步提供与其他编码方式（振幅编码、角度编码）的对比表格以增强理解深度。最后确保所有内容用中文表达且技术准确。

### Reference answer

## Basis编码（基编码）详解

### 基本原理

Basis编码（也称基编码或计算基编码）是量子机器学习中最直观的数据编码方式。其核心思想是将经典二进制数据直接映射到量子比特的计算基态上。

对于一个n位二进制字符串 $x = b_1 b_2 \cdots b_n$（其中 $b_i \in \{0, 1\}$），basis编码将其映射为：

$$|x\rangle = |b_1 b_2 \cdots b_n\rangle$$

例如，经典数据 $x = 5$（二进制101）编码为3个量子比特的态 $|101\rangle$。

### 编码实现

Basis编码的实现相对简单。对于每一个量子比特，如果对应的经典比特为1，则对该量子比特施加X门（NOT门）操作：

1. 初始化所有量子比特为 $|0\rangle^{\otimes n}$
2. 对经典比特为1的位置施加X门

在isQ中的示例：
```
import std;
qbit q[3];
procedure main() {
    // 编码 x = 5 (二进制101)
    X(q[0]);  // 最低位为1
    // q[1]为0，不操作
    X(q[2]);  // 最高位为1
}
```

### 优点

1. **直观简洁**：编码方式直接明了，经典数据与量子态之间是一一对应的映射关系
2. **量子态可区分**：每个经典数据点对应一个正交的计算基态，量子态之间完全可区分
3. **测量友好**：在计算基下测量即可直接读取编码的经典数据
4. **量子算法兼容性好**：与Grover搜索、Deutsch-Jozsa等基于计算基态的标准量子算法天然兼容
5. **无需复数量子门**：通常只需要X门即可完成编码，电路深度浅

### 缺点

1. **编码效率低**：n位经典数据需要n个量子比特，编码密度仅为每量子比特1比特信息
2. **仅适用于离散数据**：无法直接处理连续值数据，需要先进行二进制离散化
3. **缺乏量子优势**：直接的数据加载方式本身不利用量子叠加和干涉特性
4. **数据表示范围有限**：对于大规模数据集，所需量子比特数量线性增长
5. **不利于相似性度量**：编码后的态彼此正交，无法自然反映数据间的相似性关系

### 适用场景

1. **离散数据分类**：当输入数据本身就是二进制或可自然离散化时（如数字图像像素的黑白二值化）
2. **量子数据库搜索**：配合Grover算法在编码的数据中进行搜索
3. **组合优化问题**：将问题的解编码为基态，结合量子优化算法求解
4. **量子随机存取存储器（QRAM）构建**：作为QRAM中地址和数据的编码方式
5. **布尔函数评估**：利用Deutsch-Jozsa或Bernstein-Vazirani算法评估编码的布尔函数

### 与其他编码方式的比较

| 特性 | Basis编码 | 振幅编码 | 角度编码 |
|------|-----------|----------|----------|
| 编码密度 | 低(1 bit/qubit) | 高(O(2^n)/qubit) | 中等(n params/qubit) |
| 数据类型 | 离散 | 连续/离散 | 连续 |
| 态可区分性 | 完全可区分 | 不可完全区分 | 部分可区分 |
| 电路复杂度 | 低 | 高 | 中等 |

总之，Basis编码适合于数据规模较小、数据本身为离散二值类型的场景，尤其在需要精确保持数据值、后续进行基于计算基态的量子算法处理时最为适用。

## isqExpand/front/4

- task_id: `isqExpand/front/4`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `error_correction`, `bit_flip_code`, `syndrome_extraction`
- source: `isq_expansion`
- dataset_index: `1661`

### Prompt

用isQ实现implements syndrome extraction for a 3-qubit bit-flip code.

After encoding |1⟩ as |111⟩ and simulating a bit-flip error on q[1] (making it |101⟩), use two ancilla qubits to extract the error syndrome.

Requirements:
- Declare global `qbit q[5];` (q[0..2] = data, q[3..4] = syndrome ancilla).
- Encode |1⟩: apply X(q[0]), CNOT(q[0],q[1]), CNOT(q[0],q[2]).
- Simulate error: X(q[1]) to flip q[1].
- Syndrome extraction: CNOT(q[0],q[3]), CNOT(q[1],q[3]) to get parity of q[0]⊕q[1] in q[3]. CNOT(q[1],q[4]), CNOT(q[2],q[4]) to get parity of q[1]⊕q[2] in q[4].
- Measure q[3] and q[4].
- Expected syndrome: q[3]=1, q[4]=1 (indicating q[1] error).

### Chain-of-thought reasoning

## Reasoning
1. Start |00000⟩. X(q[0]) -> |10000⟩.
2. CNOT(q[0],q[1]): |11000⟩. CNOT(q[0],q[2]): |11100⟩.
3. X(q[1]): |10100⟩ (error on q[1]).
4. Syndrome: CNOT(q[0],q[3]): q[0]=1 flips q[3] -> |10110⟩. CNOT(q[1],q[3]): q[1]=0, no flip -> |10110⟩. CNOT(q[1],q[4]): q[1]=0, no flip -> |10110⟩. CNOT(q[2],q[4]): q[2]=1 flips q[4] -> |10111⟩.
5. State |10111⟩ = index 1*16+0+1*4+1*2+1 = 23. Syndrome q[3]=1, q[4]=1 indicates q[1] error.
