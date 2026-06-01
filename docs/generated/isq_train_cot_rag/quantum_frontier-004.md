# ISQ training COT RAG corpus: quantum_frontier shard 4

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/front/115

- task_id: `isqExpand/front/115`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `data_reuploading`, `quantum_classifier`, `variational_circuit`, `expressibility`
- source: `isq_expansion`
- dataset_index: `2043`

### Prompt

Write isQ code for the following quantum task: implementing a data re-uploading quantum classifier on 2 qubits.

Data re-uploading interleaves data encoding layers with trainable parameter layers. The same classical data is encoded multiple times (re-uploaded) to increase the model's expressivity.

Requirements:
- Declare global `qbit q[2];`
- Data value: x = pi/3.0. Trainable parameters: w1 = pi/6.0, w2 = pi/4.0.
- Layer 1: Ry(pi/3.0, q[0]), Ry(pi/3.0, q[1]), CNOT(q[0], q[1]), Rz(pi/6.0, q[0]), Rz(pi/6.0, q[1]).
- Layer 2 (re-upload): Ry(pi/3.0, q[0]), Ry(pi/3.0, q[1]), CNOT(q[0], q[1]), Rz(pi/4.0, q[0]), Rz(pi/4.0, q[1]).
- Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement data re-uploading classifier with 2 encoding layers.

Data re-uploading encodes classical data multiple times:
- Each layer: Ry(x) for data + Rz(w) for trainable params + CNOT for entanglement
- Re-uploading same x with different w increases the Fourier frequencies the model can represent

Numerical simulation yields: P(|00⟩)=0.133, P(|01⟩)=0.211, P(|10⟩)=0.551, P(|11⟩)=0.105.

## isqExpand/front/43

- task_id: `isqExpand/front/43`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `difficult`
- concept_tags: `quantum_chemistry`, `vqe`, `variational_principle`
- source: `qa_pipeline`
- dataset_index: `5711`

### Prompt

解释量子化学中变分量子本征求解器（Variational Quantum Eigensolver, VQE）的基本原理和工作流程。

### Chain-of-thought reasoning

## 推理
VQE利用变分原理，通过参数化量子电路准备试探态，在量子计算机上测量能量期望值，再由经典优化器调参。这种混合方案适合NISQ设备，是量子化学计算的代表性应用。

### Reference answer

VQE是一种混合量子-经典算法，用于寻找量子系统哈密顿量的基态能量。它是NISQ时代最重要的量子化学算法之一。

**基本原理——变分原理：**
对于任意试探态|ψ(θ)⟩，其能量期望值总是大于等于基态能量E₀：
⟨ψ(θ)|H|ψ(θ)⟩ ≥ E₀

因此，通过最小化能量期望值，可以逼近基态。

**工作流程：**
1. 哈密顿量映射：将分子的费米子哈密顿量（通过Jordan-Wigner或Bravyi-Kitaev变换）映射为量子比特上的Pauli算符之和：H = Σᵢ cᵢ Pᵢ。

2. 参数化试探态准备：选择一个ansatz电路U(θ)，在量子计算机上准备|ψ(θ)⟩ = U(θ)|0⟩。常用ansatz包括UCCSD（酉耦合簇）和硬件高效ansatz。

3. 能量测量：通过多次测量不同Pauli项Pᵢ的期望值，计算总能量E(θ) = Σᵢ cᵢ⟨Pᵢ⟩。

4. 经典优化：经典优化器（如COBYLA、L-BFGS-B、SPSA）根据测量结果更新参数θ。

5. 迭代：重复步骤2-4直到能量收敛。

**优势：**
- 电路深度较浅，适合NISQ设备。
- 对噪声有一定的鲁棒性（变分优化可以部分补偿系统误差）。

**挑战：**
- 贫瘠高原可能导致优化困难。
- 测量次数随Pauli项数量增长。
- ansatz选择对结果影响很大。

## isqExpand/front/5

- task_id: `isqExpand/front/5`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `difficult`
- concept_tags: `error_correction`, `stabilizer_formalism`, `pauli_group`
- source: `qa_pipeline`
- dataset_index: `1229`

### Prompt

什么是量子纠错中的稳定子形式（stabilizer formalism）？它如何用于描述量子纠错码？

### Chain-of-thought reasoning

## 推理
稳定子形式的核心思想是用一组Pauli算符的本征空间来定义码空间。n-k个独立稳定子生成元将2^n维Hilbert空间划分为2^k维的码子空间。错误检测等价于测量稳定子——如果错误与某稳定子反对易，对应测量结果翻转为-1。syndrome的模式唯一标识错误类型，从而实现纠错。

### Reference answer

稳定子形式是描述量子纠错码的数学框架。一个n量子比特的稳定子码由一组相互对易的Pauli算符（稳定子生成元）定义，这些算符的共同+1本征态空间构成码空间。

具体来说，对于[[n,k,d]]码，有n-k个独立的稳定子生成元S₁,...,S_{n-k}，它们是n量子比特Pauli群的元素。码空间是所有满足Sᵢ|ψ⟩=|ψ⟩的态|ψ⟩的集合，可编码k个逻辑量子比特。

错误检测通过测量稳定子实现：如果错误E反对易某个稳定子Sᵢ（即ESᵢ=-SᵢE），则测量Sᵢ会给出-1结果，暴露错误的存在。所有稳定子测量结果的组合称为错误syndrome，用于定位和纠正错误。

经典例子包括：Steane[[7,1,3]]码的稳定子由6个生成元定义，表面码的稳定子由X-plaquette和Z-star算符定义。

## isqExpand/front/83

- task_id: `isqExpand/front/83`
- task_type: `output_prediction`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `output_prediction`, `E91`, `Bell_state`, `mixed_basis_measurement`
- source: `isq_expansion`
- dataset_index: `720`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[2];

procedure main() {
    // Create Bell pair |Phi+> = (|00> + |11>)/sqrt(2)
    H(q[0]);
    CNOT(q[0], q[1]);
    // Alice measures Z-basis (no extra gate)
    // Bob measures X-basis
    H(q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. H(q[0]): |00> -> (|0>+|1>)/sqrt(2) x |0> = (|00>+|10>)/sqrt(2)
2. CNOT(q[0],q[1]): (|00>+|11>)/sqrt(2) = Bell state |Phi+>
3. H(q[1]): Apply H to second qubit.
   |00> -> |0>(|0>+|1>)/sqrt(2), |11> -> |1>(|0>-|1>)/sqrt(2)
   State = (|00>+|01>+|10>-|11>)/2
4. All amplitudes: +1/2, +1/2, +1/2, -1/2. All probabilities = 1/4.

In E91, mismatched-basis measurements yield uncorrelated results (uniform distribution), used for Bell inequality testing rather than key generation.

### Reference answer

{'predicted_probs': {'0': 0.25, '1': 0.25, '2': 0.25, '3': 0.25}, 'explanation': 'Bell state |Phi+> = (|00>+|11>)/sqrt(2). Bob applies H to q[1] before measurement. H on q[1]: (|0>(|0>+|1>)/sqrt(2) + |1>(|0>-|1>)/sqrt(2))/sqrt(2) = (|00>+|01>+|10>-|11>)/2. All four basis states have amplitude magnitude 1/2, giving probability 1/4 each. When Alice and Bob use different bases in E91, their results are completely uncorrelated -- each outcome is equally likely. These measurement pairs would be used for Bell inequality testing, not key generation.'}

## isqExpand/front/12

- task_id: `isqExpand/front/12`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `angle_encoding`, `amplitude_encoding`, `data_encoding`, `quantum_ml`
- source: `qa_pipeline`
- dataset_index: `1117`

### Prompt

在量子机器学习中，经典数据需要编码为量子态才能被量子电路处理。请解释角度编码（angle encoding）和振幅编码（amplitude encoding）的原理、实现方式和各自的优缺点。

### Chain-of-thought reasoning

## 推理
目标：对比角度编码和振幅编码两种QML数据编码方案。

角度编码：一个qubit一个特征，Ry(2x_i)旋转。简单但qubit需求线性增长。
振幅编码：N维向量用log2(N)个qubit，指数压缩但状态制备复杂度高。

关键权衡：qubit数量 vs 电路深度。NISQ时代角度编码更实用。

### Reference answer

## 量子数据编码

### 角度编码（Angle Encoding）

将每个经典数据特征 x_i 映射为一个量子比特上旋转门的角度参数：

|ψ⟩ = ⊗_i Ry(2x_i)|0⟩

例如，对于两维数据 (x_0, x_1)：
Ry(2x_0, q[0])  Ry(2x_1, q[1])

**优点**：
- 实现简单，每个特征对应一个qubit
- 电路深度为O(1)（单层旋转门）
- 对噪声相对鲁棒

**缺点**：
- 需要 n 个qubit编码 n 维数据，qubit数量与特征维度线性增长
- 编码的表达能力有限

### 振幅编码（Amplitude Encoding）

将 N = 2^n 维经典数据向量编码为 n 个qubit态的振幅：

|ψ⟩ = Σ_i (x_i / ||x||) |i⟩

例如，向量 (a, b, c, d) 归一化后编码为：
|ψ⟩ = a'|00⟩ + b'|01⟩ + c'|10⟩ + d'|11⟩

**优点**：
- 指数压缩：仅需 log2(N) 个qubit编码 N 维数据
- 对高维数据高效

**缺点**：
- 状态制备电路深度通常为 O(N)，抵消了qubit数量的优势
- 电路设计复杂，通用振幅编码需要多控制旋转门
- 在NISQ设备上难以高效实现

### isQ中的角度编码示例
```isq
import std;
qbit q[2];
procedure main() {
    // 编码数据 x = (pi/6, pi/4)
    Ry(pi/3.0, q[0]);   // 2 * pi/6
    Ry(pi/2.0, q[1]);   // 2 * pi/4
    M(q[0]); M(q[1]);
}
```

### 选择建议
- 特征维度低（<20）：角度编码
- 特征维度高、需要量子优势：振幅编码
- 实际NISQ应用：角度编码更实用

## isqExpand/front/97

- task_id: `isqExpand/front/97`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `qaoa`, `phase_manipulation`, `interference`, `entanglement`
- source: `isq_expansion`
- dataset_index: `5004`

### Prompt

Write isQ code for the following quantum task: demonstrates the ZZ interaction e^{-i*theta*Z_0*Z_1} using the CNOT-Rz-CNOT decomposition with theta = pi/3.

The circuit should:
1. Apply H to q[0] to create a superposition |+> on the first qubit (q[1] stays |0>).
2. Apply the ZZ interaction: CNOT(q[0],q[1]) -> Rz(2*theta, q[1]) -> CNOT(q[0],q[1]).
3. Apply H to q[0] again to convert the accumulated phase into measurable probability.
4. Measure both qubits.

This is a Ramsey-like interference experiment that reveals the ZZ phase in measurement probabilities.

### Chain-of-thought reasoning

## Reasoning
Goal: Demonstrate ZZ interaction visibility through Ramsey interference.

Step-by-step state evolution:
1. |00> -> H(q[0]) -> |+0> = (|00> + |10>)/sqrt(2)
2. CNOT(0,1): (|00> + |11>)/sqrt(2)
3. Rz(2*pi/3, q[1]): (e^{-i*pi/3}|00> + e^{i*pi/3}|11>)/sqrt(2)
4. CNOT(0,1): (e^{-i*pi/3}|00> + e^{i*pi/3}|10>)/sqrt(2)
5. H(q[0]): e^{-i*pi/3}(|0>+|1>)|0>/2 + e^{i*pi/3}(|0>-|1>)|0>/2
   = ((e^{-i*pi/3}+e^{i*pi/3})|00> + (e^{-i*pi/3}-e^{i*pi/3})|10>)/2
   = (2*cos(pi/3)|00> - 2i*sin(pi/3)|10>)/2
   = cos(pi/3)|00> - i*sin(pi/3)|10>

P(|00>) = cos^2(pi/3) = 0.25
P(|10>) = sin^2(pi/3) = 0.75
P(|01>) = P(|11>) = 0

## isqExpand/front/24

- task_id: `isqExpand/front/24`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `difficult`
- concept_tags: `quantum_ml`, `parameterized_circuit`, `quantum_neural_network`
- source: `isq_expansion_qa`
- dataset_index: `1555`

### Prompt

解释参数化量子电路（Parameterized Quantum Circuit, PQC）在量子机器学习中的作用。它与经典神经网络有什么相似和不同之处？

### Chain-of-thought reasoning

## 推理
PQC是QML的核心，用参数化旋转门和纠缠门构建可训练的量子模型。与经典神经网络类似，但操作在指数级大的希尔伯特空间中，且面临独特挑战如贫瘠高原和测量的不可逆性。

### Reference answer

参数化量子电路（PQC），也称变分量子电路或量子神经网络，是量子机器学习的核心构件。它由带可调参数的量子门组成，参数通过经典优化器迭代更新。

**与经典神经网络的相似之处：**
1. 参数化：两者都有可训练的参数（PQC的旋转角度 vs 神经网络的权重）。
2. 层级结构：PQC通常由重复的"层"组成，每层包含旋转门和纠缠门，类似于神经网络的层。
3. 优化方法：都使用梯度下降或类似方法优化损失函数。
4. 通用近似：在一定条件下，PQC可以近似任意酉变换，类似于神经网络的通用近似定理。

**关键不同：**
1. 计算空间：PQC在2^n维希尔伯特空间中操作（n为量子比特数），神经网络在实数空间中操作。
2. 可逆性：量子电路（除测量外）是酉变换，天然可逆。神经网络通常不可逆。
3. 测量限制：量子态不可复制（no-cloning），获取梯度需要特殊技术如参数移位规则（parameter shift rule）。
4. 纠缠：PQC可以利用量子纠缠创建经典系统无法高效模拟的相关性。
5. 贫瘠高原问题（barren plateau）：随机初始化的深层PQC梯度指数衰减，这是QML的独特挑战。

## isqExpand/front/23

- task_id: `isqExpand/front/23`
- task_type: `output_prediction`
- category: `quantum_frontier`
- difficulty: `difficult`
- concept_tags: `output_prediction`, `jordan_wigner`, `hopping`, `quantum_chemistry`
- source: `isq_expansion`
- dataset_index: `3804`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[2];

procedure main() {
    // Initial state: one electron in orbital 1
    X(q[1]);
    // Hopping simulation: CNOT-Ry-CNOT decomposition
    // Implements partial exchange between orbitals
    CNOT(q[0], q[1]);
    Ry(pi/4.0, q[0]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. X(q[1]): |00> -> |01> (one electron in orbital 1).
2. CNOT(q[0],q[1]): control=q[0]=0, no flip. State: |01>.
3. Ry(pi/4, q[0]): |0> -> cos(pi/8)|0> + sin(pi/8)|1>.
   State: cos(pi/8)|01> + sin(pi/8)|11>.
4. CNOT(q[0],q[1]): when q[0]=1, flip q[1].
   - |01> term: q[0]=0, no flip -> |01>
   - |11> term: q[0]=1, flip q[1]: |11> -> |10>
   State: cos(pi/8)|01> + sin(pi/8)|10>.
5. P(|01>) = cos^2(pi/8) ~ 0.8536
   P(|10>) = sin^2(pi/8) ~ 0.1464

This CNOT-Ry-CNOT pattern simulates a partial particle-hole excitation, analogous to the hopping term in a Jordan-Wigner transformed fermionic Hamiltonian.

### Reference answer

{'predicted_probs': {'1': 0.8536, '2': 0.1464}, 'explanation': 'Starting from |01> (one electron in orbital 1). First CNOT(q[0],q[1]): q[0]=0, no flip, state remains |01>. Then Ry(pi/4, q[0]): q[0] becomes cos(pi/8)|0> + sin(pi/8)|1>, giving state cos(pi/8)|01> + sin(pi/8)|11>. Second CNOT(q[0],q[1]): flips q[1] when q[0]=1, giving cos(pi/8)|01> + sin(pi/8)|10>. This represents partial electron hopping from orbital 1 to orbital 0. P(|01>) = cos^2(pi/8) = (2+sqrt(2))/4 ~ 0.854. P(|10>) = sin^2(pi/8) = (2-sqrt(2))/4 ~ 0.146. The electron has a ~14.6% probability of hopping to the other orbital.'}

## isqExpand/front/39

- task_id: `isqExpand/front/39`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `expert`
- concept_tags: `hamiltonian_simulation`, `lcu`, `quantum_signal_processing`
- source: `isq_expansion_qa`
- dataset_index: `1336`

### Prompt

解释线性组合酉操作（Linear Combination of Unitaries, LCU）方法在哈密顿量模拟中的原理。它相比Trotter分解有什么优势？

### Chain-of-thought reasoning

## 推理
LCU将哈密顿量表示为酉操作的线性组合，通过辅助量子比特和振幅放大实现精确模拟。渐近复杂度优于Trotter，但实现更复杂，需要更多辅助资源。

### Reference answer

线性组合酉操作（LCU）是一种实现哈密顿量模拟的高级方法，可以达到比Trotter分解更优的渐近复杂度。

**基本原理：**
将哈密顿量H分解为酉矩阵的线性组合：H = Σⱼ αⱼ Uⱼ，其中αⱼ是系数，Uⱼ是酉矩阵。

实现步骤：
1. Prepare辅助寄存器：用辅助量子比特准备状态 |α⟩ = (1/√λ) Σⱼ √αⱼ |j⟩，其中λ = Σⱼ|αⱼ|。
2. Select操作：根据辅助寄存器的状态选择性地应用Uⱼ。
3. Unprepare：对辅助寄存器施加prepare的逆操作。
4. 后选择：测量辅助比特，若为|0⟩则成功实现了H/λ的作用。

通过oblivious amplitude amplification可以将成功概率提升到接近1。

**相比Trotter的优势：**
1. 精度：LCU结合量子信号处理可以达到最优的复杂度O(τ + log(1/ε)/log log(1/ε))，其中τ=||H||t是演化参数。
2. 误差控制：没有Trotter误差的累积问题。
3. 灵活性：适用于更广泛的哈密顿量形式，不要求局部性。

**劣势：**
1. 需要额外的辅助量子比特。
2. 实现复杂，不太适合NISQ设备。
3. 常数因子可能较大。

LCU是容错量子计算时代哈密顿量模拟的核心技术之一。

## isqExpand/front/11

- task_id: `isqExpand/front/11`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `difficult`
- concept_tags: `error_correction`, `repetition_code`, `syndrome_correction`
- source: `isq_expansion`
- dataset_index: `894`

### Prompt

Help me write isQ code that implementing a simple repetition code with majority vote error correction.

Encode |1⟩ into 3 qubits, simulate a bit-flip error on q[2], then use syndrome measurement to detect and correct the error.

Requirements:
- Declare global `qbit q[5];` (q[0..2] data, q[3..4] syndrome).
- Encode: X(q[0]), CNOT(q[0],q[1]), CNOT(q[0],q[2]) to get |111⟩.
- Error: X(q[2]) to flip q[2], giving |110⟩.
- Syndrome: CNOT(q[0],q[3]), CNOT(q[1],q[3]), CNOT(q[1],q[4]), CNOT(q[2],q[4]).
- Correction: measure syndrome, if q[4]==1 and q[3]==0, apply X(q[2]).
- Measure all 5 qubits. After correction, data should be |111⟩.

### Chain-of-thought reasoning

## Reasoning
1. Encode: X(q[0]) -> |10000⟩. CNOT(q[0],q[1]) -> |11000⟩. CNOT(q[0],q[2]) -> |11100⟩.
2. Error X(q[2]): |11000⟩.
3. Syndrome: CNOT(q[0],q[3]): q[0]=1 flips q[3] -> |11010⟩. CNOT(q[1],q[3]): q[1]=1 flips q[3] back -> |11000⟩. CNOT(q[1],q[4]): q[1]=1 flips q[4] -> |11001⟩. CNOT(q[2],q[4]): q[2]=0, no flip -> |11001⟩.
4. Syndrome: q[3]=0, q[4]=1 -> error on q[2]. Apply X(q[2]) -> |11101⟩.
5. Final: |11101⟩ = index 16+8+4+0+1 = 29.
