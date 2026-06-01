# ISQ training COT RAG corpus: quantum_frontier shard 9

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/front/29

- task_id: `isqExpand/front/29`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `difficult`
- concept_tags: `quantum_ml`, `quantum_kernel`, `svm`, `feature_map`
- source: `qa_pipeline`
- dataset_index: `963`

### Prompt

解释量子核方法（quantum kernel method）的原理。它与经典核方法（如SVM中的RBF核）有什么区别？

### Chain-of-thought reasoning

## 推理
量子核方法用量子电路构建特征映射，将数据嵌入希尔伯特空间后计算态之间的内积作为核函数。与经典核的关键区别在于量子特征映射可以利用纠缠和量子干涉，可能提供经典无法高效模拟的核函数。

### Reference answer

量子核方法利用量子电路将数据映射到量子希尔伯特空间，然后在该空间中定义核函数来衡量数据点之间的相似性。

**基本原理：**
1. 特征映射：使用量子电路U(x)将经典数据x映射为量子态|φ(x)⟩ = U(x)|0⟩^n。
2. 核函数计算：量子核定义为两个量子态的内积的模方：k(x,y) = |⟨φ(x)|φ(y)⟩|² = |⟨0|U†(x)U(y)|0⟩|²。
3. 经典后处理：将量子核矩阵输入经典SVM或其他核方法进行分类/回归。

**与经典核方法的区别：**

1. 特征空间维度：量子核在2^n维希尔伯特空间中操作，经典RBF核在无穷维再生核希尔伯特空间中操作。但量子特征映射的结构不同于经典映射。

2. 核函数可达性：量子核可以利用纠缠和干涉效应创建经典计算机无法高效计算的核函数。

3. 计算复杂度：量子核的单次计算需要O(多项式)量子门，但核矩阵的构建仍需O(N²)次量子电路执行（N为数据集大小）。

4. 表达能力：量子核可能在特定问题上提供更好的分类边界，特别是对具有量子结构的数据。但对一般数据，量子优势尚不明确。

关键挑战包括：核矩阵的经典估计需要大量量子电路执行，核的选择依赖于问题结构，以及量子核在大数据集上的扩展性问题。

## isqExpand/front/53

- task_id: `isqExpand/front/53`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `basic`
- concept_tags: `quantum_chemistry`, `expectation_value`, `pauli_measurement`
- source: `isq_expansion`
- dataset_index: `3994`

### Prompt

请用isQ语言编写一个量子电路：measures the energy expectation value of the Pauli Z operator on a single qubit in a superposition state.

In VQE, energy measurement involves measuring Pauli operators. For H = Z, we measure the qubit directly.

Requirements:
- Declare global `qbit q[1];`
- Prepare state Ry(pi/3.0, q[0]) to create a known superposition.
- Measure q[0].
- The probability of |0⟩ gives ⟨Z⟩ = P(0) - P(1) = cos²(pi/6) - sin²(pi/6) = 3/4 - 1/4 = 1/2.

### Chain-of-thought reasoning

## Reasoning
1. Ry(pi/3)|0⟩ = cos(pi/6)|0⟩ + sin(pi/6)|1⟩ = (sqrt(3)/2)|0⟩ + (1/2)|1⟩.
2. P(|0⟩) = 3/4 = 0.75.
3. P(|1⟩) = 1/4 = 0.25.
4. ⟨Z⟩ = P(0) - P(1) = 0.5.

## isqExpand/front/50

- task_id: `isqExpand/front/50`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `expert`
- concept_tags: `quantum_chemistry`, `double_excitation`, `vqe_ansatz`
- source: `isq_expansion`
- dataset_index: `650`

### Prompt

实现以下量子计算任务（使用isQ）：implements a double excitation circuit for VQE.

A double excitation moves two electrons from orbitals (i,j) to (a,b). For a minimal 4-qubit system, this excites from |1100⟩ to |0011⟩.

A simplified double excitation circuit:
1. Start from |1100⟩.
2. Apply CNOT chain and parameterized rotations.

Implement using: CNOT(q[2],q[3]), CNOT(q[1],q[2]), CNOT(q[0],q[1]), Ry(pi/4.0, q[0]), then reverse the CNOTs.

Requirements:
- Declare global `qbit q[4];`
- Prepare |1100⟩.
- Apply the double excitation circuit.
- Measure all qubits.

### Chain-of-thought reasoning

## Reasoning
The double excitation circuit uses a ladder of CNOTs to propagate excitation information across orbitals, with a parameterized Ry rotation controlling the mixing amplitude. The CNOT ladder is then reversed. This creates a superposition between the Hartree-Fock state and excited configurations.

## isqExpand/front/117

- task_id: `isqExpand/front/117`
- task_type: `bug_fix`
- category: `quantum_frontier`
- difficulty: `expert`
- concept_tags: `xy_model`, `trotter_decomposition`, `wrong_angle`, `hamiltonian_simulation`
- source: `isq_expansion`
- dataset_index: `4500`

### Prompt

这段isQ代码有bug，帮我找出并修复：

```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    // XX interaction: exp(-i*Jt*XX)
    H(q[0]); H(q[1]);
    CNOT(q[0], q[1]);
    Rz(pi/6.0, q[1]);  // BUG: should be pi/3.0
    CNOT(q[0], q[1]);
    H(q[0]); H(q[1]);
    // YY interaction: exp(-i*Jt*YY)
    Rx(-pi/2.0, q[0]); Rx(-pi/2.0, q[1]);
    CNOT(q[0], q[1]);
    Rz(pi/6.0, q[1]);  // BUG: should be pi/3.0
    CNOT(q[0], q[1]);
    Rx(pi/2.0, q[0]); Rx(pi/2.0, q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Bug Analysis
The XX and YY interaction decompositions require Rz(2*Jt) as the rotation angle.
With Jt = pi/6, the correct angle is 2*pi/6 = pi/3.

Buggy: Rz(pi/6) -- uses Jt directly instead of 2*Jt.
- Buggy result: P(|01⟩)=0.25, P(|10⟩)=0.75 (excitation barely hops)
- Correct result: P(|01⟩)=0.75, P(|10⟩)=0.25 (excitation mostly hops)

The factor of 2 in the Rz angle comes from: exp(-iθ·ZZ) = CNOT · (I⊗Rz(2θ)) · CNOT

Fix: Change both Rz(pi/6.0, q[1]) to Rz(pi/3.0, q[1]).

## isqExpand/front/148

- task_id: `isqExpand/front/148`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `expert`
- concept_tags: `quantum_signal_processing`, `polynomial_transformation`, `quantum_algorithm_design`, `QSVT`, `Hamiltonian_simulation`
- source: `qa_pipeline`
- dataset_index: `1356`

### Prompt

什么是量子信号处理（QSP）？它如何通过交替使用信号算子和信号处理算子实现多项式变换？

### Chain-of-thought reasoning

首先分析量子信号处理（QSP）的定义：QSP 是一种通过交替序列实现多项式变换的量子算法框架。核心构造是信号算子 W(x)（编码输入参数）和信号处理算子 R(φ)（相位旋转）的交替序列。关键定理是：对于任意满足约束的目标多项式 P(x)，存在对应的 QSP 角度序列 {φₖ} 使得序列的矩阵元等于 P(x)。工作机制上，每次交替使多项式阶数增加，类似于经典 FIR 滤波器。QSP 是 QSVT（量子奇异值变换）的基础，后者统一了哈密顿量模拟、相位估计、线性系统等量子算法。回答需要涵盖数学表述、物理直觉以及与量子算法的联系。

### Reference answer

量子信号处理（Quantum Signal Processing, QSP）是一种强大的量子算法设计框架，其核心思想是通过交替作用信号算子（Signal Operator）和信号处理算子（Signal Processing Operator）的序列，对输入信号参数实现任意多项式变换。

## 基本框架

QSP 的基本构造单元是一个长度为 d 的交替序列：

$$U_{\text{QSP}} = e^{i\phi_0 Z} \cdot W(x) \cdot e^{i\phi_1 Z} \cdot W(x) \cdots W(x) \cdot e^{i\phi_d Z}$$

其中：
- **信号算子** $W(x)$：通常取 $W(x) = e^{i \arccos(x) Z}$ 或更一般地是一个依赖于信号参数 $x \in [-1,1]$ 的酉矩阵。在量子计算语境中，$W(x)$ 编码了我们要处理的输入信号（如哈密顿量的本征值）。
- **信号处理算子** $R(\phi_k) = e^{i\phi_k Z}$：这是绕 Z 轴的单参数旋转门，角度 $\phi_k$ 是我们可以自由选择的处理参数。
- $\{\phi_0, \phi_1, \ldots, \phi_d\}$ 是 QSP 角度序列，共 $d+1$ 个角度。

## 多项式变换的数学原理

QSP 的核心定理（QSP Theorem）表明：对于给定的目标多项式 $P(x) \in \mathbb{C}[x]$（满足一定约束条件，如 $\deg P \leq d$ 且 $|P(x)| \leq 1$ for $x \in [-1,1]$），存在一组 QSP 角度 $\{\phi_k\}_{k=0}^d$，使得：

$$\langle 0 | U_{\text{QSP}} | 0 \rangle = P(x)$$

即整个序列的左上矩阵元恰好是目标多项式 $P(x)$。

更一般地，$U_{\text{QSP}}$ 的完整矩阵可以写成：

$$U_{\text{QSP}} = \begin{pmatrix} P(x) & iQ(x) \\ iQ^*(x) & P^*(x) \end{pmatrix}$$

其中 $P(x)$ 和 $Q(x)$ 满足 $|P(x)|^2 + |Q(x)|^2 = 1$，形成互补多项式对。

## 交替序列的工作机制

每一对信号算子和处理算子的交替作用，相当于对多项式进行一次递推：

1. **初始化**：矩阵从单位矩阵或 $e^{i\phi_0 Z}$ 开始。
2. **信号注入**：$W(x)$ 引入一个新的 $x$ 依赖项，增加多项式阶数。
3. **旋转处理**：$e^{i\phi_k Z}$ 通过相位旋转调整多项式的系数。
4. **重复**：经过 $d$ 次交替，最终得到最高 $d$ 阶的多项式。

这种结构类似于经典信号处理中的有限脉冲响应（FIR）滤波器，其中 QSP 角度扮演滤波器系数的角色。

## 与量子算法的联系

QSP 是许多重要量子算法的理论基础：

1. **哈密顿量模拟**：通过 QSP 将 $e^{-iHt}$ 的近似实现为多项式变换。
2. **量子相位估计的改进**：利用 QSP 构造更高效的相位估计协议。
3. **量子线性系统算法**：将矩阵求逆问题转化为多项式变换问题。
4. **量子奇异值变换（QSVT）**：QSP 的多量子位推广，统一了几乎所有的量子算法框架。

## QSP 角度的计算

给定目标多项式，QSP 角度可以通过以下方法计算：
- **解析方法**：利用切比雪夫多项式的递推关系。
- **数值优化**：通过梯度下降等方法直接搜索角度。
- **因子分解方法**：将多项式分解为基本因子的乘积，逐步构造角度。

QSP 的优雅之处在于它将量子算法的设计问题转化为经典的多项式逼近问题，使得算法的构造和分析更加系统化。

## isqExpand/front/136

- task_id: `isqExpand/front/136`
- task_type: `bug_fix`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `vqe`, `hartree_fock`, `ansatz`, `molecular_hamiltonian`, `hydrogen_molecule`
- source: `isq_expansion`
- dataset_index: `4414`

### Prompt

The following isQ code implements a simplified H2 VQE ansatz circuit with 2 qubits and a fixed variational parameter theta=PI/4. The Hartree-Fock reference state for H2 in this encoding is |01>, meaning qubit q[1] should be initialized to |1>. However, the Hartree-Fock state preparation is missing. Fix the code by adding the missing X gate on q[1] before the variational layer. The circuit should: (1) Prepare the HF state via X(q[1]), (2) Apply Ry(PI/4, q[0]), (3) Apply CNOT(q[0], q[1]).

### Chain-of-thought reasoning

Step 1: Identify the bug. The buggy code starts from |00> and applies Ry(PI/4, q[0]) followed by CNOT(q[0], q[1]), but it never prepares the Hartree-Fock reference state |01> for H2. Step 2: The fix is to add X(q[1]) at the beginning. Step 3: Verify the corrected circuit. Starting from |00>, X(q[1]) gives |01>. Then Ry(PI/4, q[0]) transforms |01> into cos(PI/8)|01> + sin(PI/8)|11>. Then CNOT(q[0], q[1]) maps this to cos(PI/8)|01> + sin(PI/8)|10> (since q[0]=1 in the |11> component flips q[1] to give |10>). Step 4: Compute probabilities. cos^2(PI/8) = (1 + cos(PI/4))/2 = (1 + sqrt(2)/2)/2 = 0.8536. sin^2(PI/8) = (1 - cos(PI/4))/2 = (1 - sqrt(2)/2)/2 = 0.1464. So P(|00>)=0.0, P(|01>)=0.8536, P(|10>)=0.1464, P(|11>)=0.0.

## isqExpand/front/56

- task_id: `isqExpand/front/56`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `difficult`
- concept_tags: `quantum_chemistry`, `active_space`, `cas`, `resource_reduction`
- source: `isq_expansion_qa`
- dataset_index: `2039`

### Prompt

解释量子化学模拟中的活性空间（active space）概念。CAS方法如何帮助减少量子计算所需的资源？

### Chain-of-thought reasoning

## 推理
活性空间将轨道分为冻结/活性/虚拟三类，只对化学关键的活性轨道做精确量子模拟。这大幅减少所需量子比特数，使当前和近期量子设备能处理有意义的化学问题。

### Reference answer

活性空间是量子化学中用于减少计算复杂度的核心概念。其思想是将分子轨道分为三类：

1. 冻结轨道（frozen core）：深层内壳轨道，始终被占据，不参与化学键合。这些轨道的关联效应用经典方法（如平均场）处理。

2. 活性轨道（active orbitals）：参与化学键合和电子关联的轨道（如前线轨道HOMO、LUMO附近的轨道）。这些轨道中的电子关联需要精确处理。

3. 虚轨道（virtual orbitals）：高能轨道，始终为空。

**CAS方法（Complete Active Space）：**
在活性空间内进行完全构型相互作用（Full CI）计算，即考虑活性电子在活性轨道中的所有可能分布。

表示为CAS(m,n)：m个活性电子在n个活性轨道中。

**对量子计算的影响：**
- 无活性空间：模拟整个分子需要N_orb个量子比特（可能数百个）。
- 使用CAS(m,n)：只需2n个量子比特（考虑自旋轨道），通常n=5-20。

例如，Fe₂分子：
- 完整基组可能需要>100个量子比特。
- CAS(12,12)只需24个量子比特，但仍能捕获主要的多参考特征。

活性空间选择的挑战在于：选择不当可能遗漏重要关联效应。自动活性空间选择（如AVAS、AutoCAS）是活跃的研究方向。

## isqExpand/front/125

- task_id: `isqExpand/front/125`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `angle_encoding`, `quantum_machine_learning`, `data_encoding`, `variational_quantum_circuits`, `feature_map`
- source: `qa_pipeline`
- dataset_index: `2711`

### Prompt

详细解释量子机器学习中的angle编码方法。它的优缺点和适用场景是什么？

### Chain-of-thought reasoning

第一步：分析题目要求——需要详细解释角度编码方法，包括基本原理、实现方式、优缺点和适用场景。

第二步：组织回答结构——从基本原理出发，先说明角度编码是什么，然后给出具体实现方式，再分别列出优缺点，最后说明适用场景并与其他编码方法比较。

第三步：详细阐述基本原理——角度编码是将经典数据值作为旋转门的角度参数，通过Rx、Ry、Rz门将数据编码到量子态的幅角中。这是最直观的编码方式。

第四步：列出实现方式的变体——包括单旋转编码、密集编码和重复编码等不同策略。

第五步：系统分析优点——实现简单、硬件友好、可微分、可解释性强、适合变分算法。

第六步：系统分析缺点——编码容量有限、线性表达能力有限、需要归一化、量子比特利用率不高、特征间关联不足。

第七步：明确适用场景——小规模数据、NISQ设备、变分量子分类器、量子核方法、快速原型验证等。

第八步：补充与其他编码方法的比较，帮助理解角度编码在整体数据编码方法中的定位。

### Reference answer

角度编码（Angle Encoding）是量子机器学习中最基本、最直观的数据编码方法之一，其核心思想是将经典数据映射为量子态的旋转角度。

## 基本原理

角度编码通过将经典数据值x_i作为参数化量子门的旋转角度，将数据编码到量子态中。具体来说，对于一个N维经典数据向量(x_1, x_2, ..., x_N)，我们可以使用N个量子比特，对第i个量子比特施加R_x(x_i)、R_y(x_i)或R_z(x_i)旋转门，将数据编码为：

|ψ⟩ = ⊗_{i=1}^{N} R_p(x_i)|0⟩

其中p ∈ {x, y, z}表示选择的旋转轴。更一般地，可以使用多层旋转门（例如同时使用R_y和R_z）来增加表达能力。

## 具体实现方式

1. **单旋转编码**：对每个量子比特施加一个旋转门，如R_y(x_i)，每个量子比特编码一个特征值。

2. **密集编码**：在每个量子比特上依次施加多个旋转门（如R_y(x_i)和R_z(x_{i+N})），使单个量子比特能编码多个特征。

3. **重复编码**：将同一数据多次编码到不同层的旋转门中，增强数据的表示能力。

## 优点

1. **实现简单**：只需使用基本的旋转门，在当前的量子硬件上易于实现。

2. **硬件效率高**：电路深度浅，量子门数量少，适合NISQ（含噪声中等规模量子）设备。

3. **可微分性好**：旋转角度可以直接作为可训练参数，便于与参数移位法则等梯度计算方法结合。

4. **可解释性强**：数据与量子态之间的映射关系清晰直观。

5. **对变分量子算法友好**：可以自然地嵌入到变分量子电路（VQC）中作为特征映射层。

## 缺点

1. **编码容量有限**：单旋转编码只能将数据映射到Bloch球面上的一个点，无法表示一般量子态的全部自由度。

2. **线性表达能力有限**：简单的角度编码只能捕获数据的线性特征，对于复杂的非线性特征需要额外的纠缠层。

3. **归一化约束**：数据需要预先归一化到合适的范围（如[0, 2π]），这可能导致信息损失。

4. **量子比特利用率不高**：基本的角度编码方案中，N个特征需要N个量子比特，与振幅编码的O(log N)相比不占优势。

5. **特征间关联不足**：单量子比特旋转本身不引入特征间的量子关联（纠缠），限制了模型的表达能力。

## 适用场景

1. **小规模数据集**：当特征维度较低、样本量不大时，角度编码最为合适。

2. **NISQ设备**：由于电路深度浅，适合在当前噪声较大的量子硬件上运行。

3. **变分量子分类器**：作为量子神经网络的输入层，与后续的可训练变分层配合使用。

4. **量子核方法**：在量子支持向量机等核方法中，角度编码可用于构建量子特征映射。

5. **快速原型验证**：在算法开发初期，作为基准编码方案快速验证思路。

## 与其他编码方法的比较

相比于振幅编码（Amplitude Encoding）可以实现O(log N)的编码效率，角度编码需要O(N)个量子比特，但实现更简单、电路更浅。相比于基态编码（Basis Encoding），角度编码更灵活，不限于二进制数据。在实际应用中，常常在角度编码后添加纠缠层（如CNOT门组成的硬件高效拟设），以增强量子态的表达能力。

## isqExpand/front/100

- task_id: `isqExpand/front/100`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `qaoa`, `max_cut`, `superposition`, `phase_manipulation`
- source: `isq_expansion`
- dataset_index: `430`

### Prompt

Implement a quantum circuit in isQ: implementing a 1-layer QAOA circuit for a simple 2-job scheduling problem modeled as Max-Cut on a single edge. Two conflicting jobs must be assigned to different time slots (encoded as |0> or |1>). Use gamma = pi/3 and beta = pi/3.

The QAOA circuit:
1. Initialize both qubits with H gates.
2. Cost layer: ZZ interaction via CNOT(q[0],q[1]) -> Rz(2*gamma, q[1]) -> CNOT(q[0],q[1]).
3. Mixer layer: Rx(2*beta) on each qubit.
4. Measure both qubits.

The optimal scheduling (anti-aligned assignments |01> or |10>) should have the highest probabilities.

### Chain-of-thought reasoning

## Reasoning
Goal: QAOA for scheduling = Max-Cut on edge (0,1), with gamma=pi/3, beta=pi/3.

The cost Hamiltonian H_C = Z_0Z_1 penalizes same-assignment states.

With gamma=pi/3 and beta=pi/3 (stronger mixer than task 96):
1. H|00> -> uniform superposition.
2. ZZ(pi/3) cost layer: applies e^{-i*pi/3} to |00>,|11> and e^{+i*pi/3} to |01>,|10>.
3. Rx(2*pi/3) mixer: strong mixer rotation tilts amplitude toward anti-aligned states.

Result: P(|01>)=P(|10>)=0.4375 (optimal schedules), P(|00>)=P(|11>)=0.0625.
These parameters successfully amplify the Max-Cut solutions (anti-aligned qubits).

## isqExpand/front/74

- task_id: `isqExpand/front/74`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `difficult`
- concept_tags: `no_cloning`, `QKD_security`, `quantum_cryptography`, `BB84`
- source: `isq_expansion_qa`
- dataset_index: `1072`

### Prompt

量子不可克隆定理（No-Cloning Theorem）是量子密钥分发安全性的基石。请证明为什么任意未知量子态不能被完美复制，并解释这如何保证QKD协议（如BB84）的安全性。如果不可克隆定理不成立，QKD协议会面临什么攻击？

### Chain-of-thought reasoning

## 推理
目标：证明不可克隆定理并连接到QKD安全性。

证明逻辑：假设存在通用克隆算符U -> 利用酉性保内积 -> 推出矛盾（⟨psi|phi⟩ = ⟨psi|phi⟩^2只在0或1时成立）。

安全性连接：BB84中的四态两两非正交 -> 不可克隆 -> Eve无法无损复制 -> 必须测量 -> 测量引入错误 -> 可检测。

假设反面：克隆可行 -> 截获-克隆-转发攻击零错误率 -> QKD完全不安全。

### Reference answer

## 量子不可克隆定理与QKD安全性

### 不可克隆定理的证明

**假设**存在一个克隆酉变换U，使得对任意量子态|psi⟩：
U(|psi⟩ tensor |0⟩) = |psi⟩ tensor |psi⟩

**考虑两个不同的态** |psi⟩ 和 |phi⟩：
U(|psi⟩ tensor |0⟩) = |psi⟩ tensor |psi⟩
U(|phi⟩ tensor |0⟩) = |phi⟩ tensor |phi⟩

**取内积**（利用U的酉性保持内积）：
⟨psi|phi⟩ * ⟨0|0⟩ = ⟨psi|phi⟩ * ⟨psi|phi⟩
⟨psi|phi⟩ = ⟨psi|phi⟩^2

这意味着 ⟨psi|phi⟩(1 - ⟨psi|phi⟩) = 0，所以 ⟨psi|phi⟩ = 0 或 1。

**结论**：克隆操作只对正交态或相同态有效，不能克隆任意未知量子态。

### 对QKD安全性的保障

**BB84场景中的作用**：
1. Alice发送的量子态在两组非正交基底中编码（Z基底的{|0⟩,|1⟩}和X基底的{|+⟩,|−⟩}）
2. |0⟩和|+⟩不正交（⟨0|+⟩ = 1/sqrt(2)），因此不可克隆定理直接适用
3. Eve无法复制截获的量子态来保留一份并转发原始态

**Eve的困境**：
- 不测量直接转发：获取不到信息
- 测量后重新制备：选错基底（概率50%）时会引入错误
- 尝试克隆：物理定律禁止
- 部分克隆/纠缠攻击：获取的信息量受Holevo界限制，且会引入可检测的干扰

### 如果不可克隆定理不成立

Eve可以执行**完美截获-克隆-转发攻击**：
1. 截获Alice发送的每个量子态
2. 完美克隆，保留副本
3. 将原始态转发给Bob
4. 等Alice和Bob公开基底选择后，用正确基底测量自己的副本
5. 获得与Alice和Bob完全相同的密钥，且零错误率——完全不可检测

这将使所有QKD协议（BB84、E91、B92等）都失去安全性保障。

### 量化安全性
不可克隆定理的定量形式给出了克隆保真度的上界：对于均匀分布的qubit态，最优克隆保真度为5/6约等于83.3%，远低于完美克隆。这个不完美性正是QKD安全证明中隐私放大步骤的理论基础。
