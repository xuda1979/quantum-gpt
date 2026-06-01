# ISQ training COT RAG corpus: quantum_algorithms shard 46

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/algo/104

- task_id: `isqExpand/algo/104`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `reversible_computing`, `multi_controlled_logic`, `ancilla_usage`
- source: `isq_expansion_qa`
- dataset_index: `4724`

### Prompt

什么是量子比较器（Quantum Comparator）？如何用量子门实现两个量子比特值的大小比较？请解释基本原理和单比特比较器的电路设计。

### Chain-of-thought reasoning

## 推理
目标：解释量子比较器。

关键：
1. a > b 等价于 a AND (NOT b)
2. 用X(b) + Toffoli + X(b)实现
3. 多比特需逐位级联 + 辅助比特
4. 所有操作可逆

### Reference answer

## 量子比较器（Quantum Comparator）

### 基本概念
量子比较器是一种量子电路，用于比较两个量子寄存器所编码数值的大小关系，并将结果存储在辅助比特中。

### 单比特量子比较器
比较两个比特 a 和 b：a > b 当且仅当 a=1 且 b=0。

这等价于计算 a AND (NOT b)，电路实现：
1. X(b)：翻转b，得到NOT b
2. Toffoli(a, b, result)：当 a=1 且 (NOT b)=1 时，翻转result
3. X(b)：恢复b的原始值

### 真值表
| a | b | a>b |
|---|---|-----|
| 0 | 0 |  0  |
| 0 | 1 |  0  |
| 1 | 0 |  1  |
| 1 | 1 |  0  |

### 多比特扩展
从最高位到最低位逐位比较，需要辅助比特记录当前是否相等。若最高位不同则直接确定，否则继续比较下一位。

### isQ示例
```isq
import std;
qbit q[3];  // q[0]=a, q[1]=b, q[2]=result(a>b)
procedure main() {
    X(q[0]);  // a=1, b=0
    X(q[1]);
    Toffoli(q[0], q[1], q[2]);
    X(q[1]);
    M(q[0]); M(q[1]); M(q[2]);
}
```
结果：q[2]=1，表示 a > b。

### 应用
- Grover搜索中的阈值Oracle
- 量子排序网络
- 约束满足问题中的大小约束

## isqQA/quantum_algorithms/118_comparison

- task_id: `isqQA/quantum_algorithms/118_comparison`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `comparison`, `algorithm`, `量子振幅估计`
- source: `qa_pipeline`
- dataset_index: `4566`

### Prompt

请对比量子振幅估计（QAE）与经典蒙特卡洛方法在误差收敛速度上的差异，并进一步深入对比标准量子振幅估计（基于量子相位估计，QPE）与无相位估计的量子振幅估计算法（如最大似然振幅估计 MLAE）在电路深度、抗噪性能及适用场景上的优缺点。最后，请使用isQ代码演示如何构造振幅放大步骤中的核心Grover算符 $G$，并展示其在 $2$ 个量子比特系统中的具体应用。

### Reference answer

<think)
1. 误差收敛率对比：经典蒙特卡洛的误差收敛率为O(1/√M)，而量子振幅估计利用量子态的相长和相消干涉，可将收敛率提升至O(1/M)，实现二次加速。
2. 标准QAE与无相位QAE对比：标准QAE依赖量子相位估计（QPE），需要大量辅助比特、受控Grover算符以及逆量子傅里叶变换（IQFT），导致电路深度极深，对NISQ设备的噪声极为敏感；MLAE等变体无需QPE，通过在不同幂次下运行Grover算符并进行经典的最大似然估计来推断振幅，电路深度大幅降低，无需辅助比特，在NISQ时代更具可行性，但需要一定的经典后处理开销。
3. isQ代码实现：构造一个2比特系统。状态准备算子A使用H门制备均匀叠加态。假设目标态为|11⟩，则相位算子S_χ为CZ门。条件相移算子S_0翻转|00⟩的相位（通过H门和X门转化为|11⟩后使用CZ门，再加X和H恢复）。组合A S_0 A† S_χ即为Grover算符G。
</think)

在误差收敛速度方面，经典蒙特卡洛方法需要通过大量随机采样来逼近期望值，其误差收敛率服从 $O(1/\sqrt{M})$，其中 $M$ 为采样次数；而量子振幅估计（QAE）利用量子态的相长与相消干涉特性，能够将误差收敛率提升至 $O(1/M)$，这被称为海森伯极限，提供了相对于经典方法的二次加速。这种加速在金融衍生品定价、风险分析和组合优化等需要海量采样的场景中具有革命性意义。

在算法变体的优缺点和适用场景上，标准量子振幅估计基于量子相位估计（QPE）实现。它的优点是理论极为优雅，能严格达到最优的加速比。但缺点是它需要引入大量辅助量子比特，执行深层的多控受控Grover算符操作，以及逆量子傅里叶变换（IQFT）。这导致其电路深度极高，对当前处于NISQ（含噪声中等规模量子）时代的硬件极不友好，噪声极易掩盖甚至逆转其量子优势。

为了克服这一瓶颈，研究人员提出了无相位估计的量子振幅估计变体，例如最大似然振幅估计（MLAE）。MLAE摒弃了QPE和辅助比特，直接在不同深度 $m_k$ 下制备并运行Grover迭代 $G^{m_k}$，然后对末态进行物理测量，最后在经典计算机上利用最大似然估计（MLE）从测量结果中推断出振幅。MLAE的优点是电路深度显著降低，所需量子资源大幅减少，抗噪能力强，非常适合当前的NISQ设备；其缺点是需要一定量的经典后处理计算，且实验序列的设计策略会直接影响收敛的常数因子。

以下展示如何使用isQ语言构造Grover算符 $G = A S_0 A^\dagger S_\chi$ 并在2比特系统中应用：

```isq
import std;

qbit q[2];

// 状态准备算子 A：此处简单使用H门制备等概率叠加态
procedure applyA() {
    H(q[0]);
    H(q[1]);
}

// 标记好态的相位算子 S_chi：假设目标态为 |11>，将其相位翻转
procedure applySchi() {
    CZ(q[0], q[1]);
}

// 条件相移算子 S_0：翻转 |00> 的相位
// 通过 H 和 X 门将 |00> 映射为 |11>，执行 CZ，再映射回去
procedure applyS0() {
    H(q[0]);
    H(q[1]);
    X(q[0]);
    X(q[1]);
    CZ(q[0], q[1]);
    X(q[0]);
    X(q[1]);
    H(q[0]);
    H(q[1]);
}

// 构造完整的 Grover 算符 G
procedure applyG() {
    applySchi();
    inv applyA();
    applyS0();
    applyA();
}

procedure main() {
    // 1. 初始化状态准备
    applyA();
    
    // 2. 施加一次 Grover 算符放大目标振幅
    applyG();
    
    // 3. 测量得到结果（理论上测得 |11> 的概率会从 1/4 提升到更接近 1）
    M(q[0]);
    M(q[1]);
}
```

## isqTrain/2794

- task_id: `isqTrain/2794`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2293`

### Prompt

This isQ program doesn't produce the correct output. Can you debug it?

Code:
```isq
import std;

oracle bool[1] constant(bool a[4]) {
    bool res[] = [true];
    return res;
}

qbit q[4], anc[1];

procedure main()
{
    X(anc[0]);
    // H(q); // BUG: missing Hadamard
    H(anc[0]);
    constant(q, anc);
    H(q);
    print M(q);
}
```

### Chain-of-thought reasoning

## Bug Analysis

**1. Bug:** The line `H(q)` is commented out, so the input register `q[4]` remains in |0000⟩ instead of being placed into superposition. Without this, the oracle is queried on a single basis state, and the final Hadamard transform cannot produce the interference pattern that distinguishes constant from balanced functions.

**2. Fix:** Uncomment `H(q)` to apply Hadamard gates to all input qubits before the oracle call.

**3. State evolution (corrected):**
- After `X(anc[0])`: |0000⟩|1⟩
- After `H(q)` and `H(anc[0])`: (1/4)∑|x⟩ ⊗ |−⟩ where |−⟩ = (|0⟩−|1⟩)/√2
- After `constant(q, anc)`: phase kickback applies (−1)^f(x) = (−1)^1 = −1 for all x, yielding (−1/4)∑|x⟩|−⟩ (global phase irrelevant)
- After `H(q)`: |0000⟩|−⟩ — all amplitudes interfere constructively at |0000⟩ for a constant function
- Measure: |0000⟩ with probability 1.0 ✓

## isqTrain/3654

- task_id: `isqTrain/3654`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `3126`

### Prompt

用isQ实现2-bit quantum phase estimation (QPE) to estimate the phase pi/4 of a Rz rotation gate. Use:
1. Two precision qubits and one eigenstate qubit
2. Prepare eigenstate |1> on the target qubit
3. Apply controlled-Rz operations
4. Apply inverse QFT on precision register
5. Measure all qubits

### Chain-of-thought reasoning

Let me trace through this quantum phase estimation circuit carefully.

**Goal**: Estimate the phase φ = π/4 of the Rz rotation gate using 2-bit QPE.

**Qubits**: 3 qubits total - q[0] and q[1] are precision qubits, q[2] is the target/eigenstate qubit.

**Step-by-step state evolution**:

1. **Initial state**: |000⟩

2. **X(q[2])**: |001⟩
   - Target qubit is now |1⟩, which is an eigenstate of Rz(θ) with eigenvalue e^{-iθ/2}

3. **H(q[0]); H(q[1])**: (1/2)(|0⟩+|1⟩)(|0⟩+|1⟩)|1⟩ = (1/2)(|00⟩+|01⟩+|10⟩+|11⟩)|1⟩

4. **Controlled Rz(2π·(1/4)·1, q[0], q[2])** = CRz(π/2, q[0], q[2]):
   - When q[0]=|1⟩, apply Rz(π/2) to q[2]
   - Rz(π/2)|1⟩ = e^{-iπ/4}|1⟩
   - State: (1/2)(|00⟩|1⟩ + |01⟩|1⟩ + e^{-iπ/4}|10⟩|1⟩ + e^{-iπ/4}|11⟩|1⟩)

5. **Controlled Rz(2π·(1/4)·2, q[1], q[2])** = CRz(π, q[1], q[2]):
   - When q[1]=|1⟩, apply Rz(π) to q[2]
   - Rz(π)|1⟩ = e^{-iπ/2}|1⟩ = -i|1⟩
   - State: (1/2)(|00⟩|1⟩ + e^{-iπ/2}|01⟩|1⟩ + e^{-iπ/4}|10⟩|1⟩ + e^{-iπ/4-iπ/2}|11⟩|1⟩)
   - = (1/2)(1|00⟩ + e^{-iπ/2}|01⟩ + e^{-iπ/4}|10⟩ + e^{-i3π/4}|11⟩)|1⟩

So the phase being estimated is θ/2π = -1/8 (from the e^{-iπ/4} = e^{-2πi·(1/8)} per unit of precision qubit 0).

Wait, let me reconsider. The phase in QPE is encoded in the precision register as:
- The eigenvalue is e^{2πiφ} where we want to find φ
- For Rz(θ) on |1⟩, the eigenvalue is e^{-iθ/2}

Here θ = π/4, so eigenvalue = e^{-iπ/8}

Hmm, but the controlled operations apply powers of the unitary:
- q[0] controls U^1
- q[1] controls U^2

After controlled operations, the precision register should be in state:
∑_x e^{2πiφx}|x⟩ where φ is the phase.

Let me recompute. The phase from Rz(π/4) on |1⟩:
Rz(θ) = diag(1, e^{-iθ})
Rz(π/4)|1⟩ = e^{-iπ/8}|1⟩

Wait, Rz(θ) = diag(e^{-iθ/2}, e^{iθ/2}) typically, but the convention matters.

Actually in many conventions, Rz(θ) = [[1,0],[0,e^{iθ}]]. Let me check the isQ convention.

In isQ, Rz(θ) likely follows Rz(θ) = diag(1, e^{iθ}) = [[1,0],[0,e^{iθ}]].

So Rz(π/4)|1⟩ = e^{iπ/4}|1⟩

The phase is φ = 1/8 (since e^{2πi·1/8} = e^{iπ/4}).

So after controlled operations:
- CRz(2π·1/4·1) = CRz(π/2) on q[0]: applies phase e^{iπ/4} when q[0]=1
- CRz(2π·1/4·2) = CRz(π) on q[1]: applies phase e^{iπ/2} when q[1]=1

State: (1/2)(|00⟩ +

## isqQA/quantum_algorithms/132_hardware_limitations

- task_id: `isqQA/quantum_algorithms/132_hardware_limitations`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `hardware_limitations`, `algorithm`, `量子全加器`
- source: `qa_pipeline`
- dataset_index: `724`

### Prompt

在当前的含噪中等规模量子（NISQ）设备上构建量子全加器电路时，量子门的保真度和量子比特的退相干效应是如何限制算法执行的？请详细分析Toffoli门等复杂多量子比特门在物理分解时带来的电路深度问题，并提出一种在NISQ时代降低退相干影响的电路优化策略。最后，请使用isQ语言实现一个考虑了基础物理门分解深度的4量子比特全加器示例代码。

### Reference answer

在当前的NISQ（含噪中等规模量子）设备上实现量子全加器，其核心挑战在于硬件局限性，特别是退相干效应和有限的双量子比特门保真度。量子全加器的逻辑高度依赖多量子比特控制门（如Toffoli门），而在物理硬件上，量子比特通常只能实现相邻的耦合，且单量子比特门与双量子比特门（如CNOT）的保真度存在显著差异。

退相干效应包括纵向弛豫（用时间常数T1表征，导致能量丢失）和横向退相干（用T2表征，导致相位信息丢失）。标准Toffoli门无法直接在物理机上一步执行，必须被分解为多个基础的CNOT门和单量子比特门（通常需要至少6个CNOT门和8个单比特门）。如果全加器串行包含多个Toffoli门，电路深度将急剧增加。当电路的执行时间接近或超过系统的T1和T2时间时，量子态的相干性会被破坏，计算结果的概率分布将严重偏离理想值，导致全加器输出极高的错误率。

为了缓解NISQ设备的这种局限性，优化策略主要集中在“电路深度压缩”和“门数量削减”。我们通过利用量子逻辑门的等价性，采用不引入额外辅助比特的相对相位Toffoli门分解，或者利用特定的线性代数性质将标准Toffoli分解中的CNOT数量降至4个。这种优化大幅缩短了临界路径长度，降低了退相干带来的误码率，并减轻了硬件耦合拓扑带来的路由开销。

以下是使用isQ语言编写的量子全加器代码实现。该实现利用1个进位输入、2个输入操作数和1个用于存储进位输出的辅助比特，在逻辑映射上充分考虑了门分解的复杂性：

<think
import std;

// 全局声明4个量子比特
// q[0]: 进位输入 (c_in)
// q[1]: 输入操作数 a
// q[2]: 输入操作数 b
// q[3]: 进位输出 (c_out)，初始需为 |0>
qbit q[4];

procedure main() {
    // 初始化输入态，例如计算 1 + 1 + 1 = 11 (进位与和均为1)
    // 将输入置为 |1>态以测试全加器功能
    X(q[0]); // c_in = 1
    X(q[1]); // a = 1
    X(q[2]); // b = 1
    
    // 步骤 1: 计算 a AND b，结果保存在 c_out (q[3])
    // 使用 Toffoli 门
    Toffoli(q[1], q[2], q[3]);
    
    // 步骤 2: 计算 a XOR b，结果保存在 b (q[2])
    CNOT(q[1], q[2]);
    
    // 步骤 3: 计算 c_in AND (a XOR b)，并将结果异或到 c_out (q[3])
    // 此时 c_out = (a AND b) XOR (c_in AND (a XOR b))，即最终进位
    Toffoli(q[0], q[2], q[3]);
    
    // 步骤 4: 计算最终的和 Sum = c_in XOR a XOR b，结果保存在 c_in (q[0])
    CNOT(q[2], q[0]);
    
    // 测量输出
    // q[0] 为 Sum (期望为 1)
    // q[3] 为 c_out (期望为 1)
    int r0 = M(q[0]);
    int r3 = M(q[3]);
    
    // 经典条件操作，仅用于验证输出结果是否符合预期
    if (r0 == 1) {
        if (r3 == 1) {
            // 验证成功：Sum = 1, c_out = 1
            X(q[0]);
        }
    }
}
>

在上述代码中，逻辑上我们使用了两次Toffoli门和两次CNOT门。在实际投入NISQ硬件运行前，底层编译器会将高阶的Toffoli门转换为底层物理脉冲序列。由于我们通过逻辑代码清晰地规划了工作比特和辅助比特，并在算法设计层面避免了不必要的SWAP操作及额外冗余比特的引入，这使得该全加器在现有的退相干时间窗口内能够最大限度地保持量子态的相干性，从而提取出高保真的加法结果。

## isqTrain/959

- task_id: `isqTrain/959`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `hamiltonian_simulation`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4996`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
qbit q[1];

procedure main() {
    // Pauli-X evolution: e^(-i*(pi/6)*X) = Rx(pi/3)
    // Rx(pi/3)|0> = cos(pi/6)|0> - i*sin(pi/6)|1>
    // cos^2(pi/6) = 0.75, sin^2(pi/6) = 0.25
    Rx(1.04719755119660, q[0]);
    // Measure the qubit to observe the probabilities
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes a single qubit `q[0]` in the ground state $|0\rangle$.
2. It applies the gate `Rx(1.04719755119660, q[0])`, which corresponds to an $R_x(\pi/3)$ rotation.
3. The $R_x(\theta)$ gate transforms the initial state as follows: $R_x(\theta)|0\rangle = \cos(\theta/2)|0\rangle - i\sin(\theta/2)|1\rangle$.
4. Substituting $\theta = \pi/3$, the resulting quantum state becomes $\cos(\pi/6)|0\rangle - i\sin(\pi/6)|1\rangle = \frac{\sqrt{3}}{2}|0\rangle - \frac{i}{2}|1\rangle$.
5. The probability of measuring the $|0\rangle$ state is $\cos^2(\pi/6) = 0.75$.
6. The probability of measuring the $|1\rangle$ state is $\sin^2(\pi/6) = 0.25$.

Predicted probability distribution: {|0>: 0.75, |1>: 0.25}

### Reference answer

{'predicted_probs': {'0': 0.749999999999999, '1': 0.250000000000001}, 'explanation': 'Parametric variant of isqEval/297. Dimension: predict probabilities for reference circuit.'}

## isqExpand/algo/105

- task_id: `isqExpand/algo/105`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `superposition`, `basis_change`
- source: `qa_pipeline`
- dataset_index: `5182`

### Prompt

量子随机数生成器（QRNG）的原理是什么？为什么量子产生的随机数是"真随机"而不是伪随机？请对比经典伪随机数生成器并给出最简单的QRNG电路设计。

### Chain-of-thought reasoning

## 推理
目标：解释QRNG与经典PRNG的本质区别。

关键：
1. Born规则导致内禀随机性
2. 不可预测、不可重复——与PRNG根本不同
3. 最简电路：H + M
4. 设备无关方案用Bell不等式认证

### Reference answer

## 量子随机数生成器（QRNG）

### 核心原理
量子随机数的真随机性源于量子力学的Born规则：测量一个处于叠加态的量子比特时，结果具有内禀不确定性。

H|0> = (|0>+|1>)/sqrt(2)，测量得0或1各50%概率。这种随机性不是因为信息不完整，而是物理定律的固有属性。

### 与经典伪随机的区别
| 特性 | QRNG | PRNG |
|------|------|------|
| 来源 | 量子力学固有 | 确定性算法 |
| 可预测性 | 不可预测 | 知道种子可预测 |
| 安全性 | 信息论安全 | 计算安全 |
| 可重复性 | 不可重复 | 可重复 |

### 最简单电路
对n个量子比特各施加H门后测量，产生n位均匀随机字符串：
```isq
import std;
qbit q[3];
procedure main() {
    H(q[0]); H(q[1]); H(q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}
```
每个3-bit输出等概率1/8。

### 安全性保证
设备无关QRNG利用Bell不等式违背来认证随机性，无需信任量子设备内部工作。

## isqTrain/2673

- task_id: `isqTrain/2673`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_procedures`, `measurement_order`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4317`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[5];

procedure main(){
    X(q[4]);
    for i in 0:5{ 
        H(q[i]);
    }
    CNOT(q[0], q[4]);
    CNOT(q[1], q[4]);
    CNOT(q[3], q[4]);
    for i in 0:5{ 
        H(q[i]); 
    }
    for i in 0:5{
        M(q[i]); 
    }
}
```

### Chain-of-thought reasoning

Step 1: Initialize 5 qubits to |00000>. Apply X to q[4], state becomes |00001>.
Step 2: Apply H to all qubits. State becomes (1/sqrt(32)) sum over x in {0,1}^5 |x> |1> for q[4]? No, X was on q4, so |00001>. H^5 on |00001> gives |+++++>? No, H on |0> is |+>, H on |1> is |->.
So H on q[0..3] gives |+> for them, H on q[4] gives |->.
State is |+ + + + ->.
Wait, let's write it explicitly: (1/sqrt(2)) sum_{x \in {0,1}^4} |x> (|0> - |1>) / sqrt(2) for q4.
Step 3: CNOTs with q[4] as target.
CNOT(q[0], q[4]) flips q4 when q0=1. This transforms |+ + + + -> into |+ + + + ->? No.
Let f(x) = x0 + x1 + x3 mod 2. Then the state becomes (1/4) sum_x (-1)^{f(x)} |x> (|0>-|1>)/sqrt(2)? No.
Actually, let's track the phase:
Initial: |00001>
H on all: (1/4) sum_{x \in {0,1}^4} |x> \otimes |-> = (1/4) sum_x |x> (|0>-|1>)/sqrt(2).
CNOTs apply Z on q[4] conditioned on q0, q1, q3.
Wait, if control is |1> and target is |->, CNOT(control, target) applies Z to target, which does nothing to |-> (since Z|-> = -|->). But wait! Z is applied if control is |1>. So it multiplies the state by -1 if control is |1> AND target is |->. No, Z on |-> is -|->, so it's -1. The total phase is (-1)^{x0 + x1 + x3}.
Wait, no. Z|-> = -|->, so if CNOT is applied with target in |->, it applies Z to target, which gives -|->.
So the state becomes (1/4) sum_{x \in {0,1}^4} (-1)^{x0+x1+x3} |x> (|0>-|1>)/sqrt(2).
Wait, let's verify.
If control is |1> and target is |0>, CNOT gives |1>|1>.
If control is |1> and target is |1>, CNOT gives |1>|0>.
If control is |1> and target is |-> = (|0>-|1>)/sqrt(2), CNOT gives (|1>|1> - |1>|0>)/sqrt(2) = |1> \otimes (|1>-|0>)/sqrt(2) = - |1> |->.
So CNOT with target in |-> applies a phase of -1 if control is |1>.
Thus, the state after the 3 CNOTs is:
(1/4) sum_{x \in {0,1}^4} (-1)^{x0 + x1 + x3} |x> |->.
Step 4: Apply H to all qubits again.
This maps |-> to |1>.
And the phase (-1)^{x0 + x1 + x3} is transformed back.
Let's see: (1/4) sum_{x} (-1)^{f(x)} |x> applied to H^{\otimes 4}.
H^{\otimes 4} maps |x> to (1/4) sum_{y} (-1)^{x \cdot y} |y>.
So the overall state for the first 4 qubits is:
(1/16) sum_{y} [ sum_{x} (-1)^{f(x) + x \cdot y} ] |y>.
For q[4], the state is |1>.
What is f(x)? f(x) = x0 + x1 + x3.
We want to find y such that f(x) + x \cdot y = 0 for all x.
This requires y = f(x) as a vector.
So y0 = 1, y1 = 1, y3 = 1. y2 = 0.
Thus y = 1101.
So the state of the first 4 qubits

### Reference answer

{'predicted_probs': {'11011': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/2657

- task_id: `isqTrain/2657`
- task_type: `code_equivalence`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `global_phase`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5177`

### Prompt

Compare these two isQ programs. Do they give the same probability distribution?

First program:
```isq
import std;
qbit q[3];

procedure main() {
    // Set control=1, a=1, b=0
    X(q[0]);
    X(q[1]);
    // Fredkin gate (controlled-SWAP) decomposition
    // Step 1: CNOT from a to b
    CNOT(q[1], q[2]);
    // Step 2: Toffoli with control and b targeting a
    Toffoli(q[0], q[2], q[1]);
    // Step 3: CNOT from a to b
    CNOT(q[1], q[2]);
    // After swap: a=0, b=1
    M(q[1]);
    M(q[2]);
}

```

Second program:
```isq
import std;
qbit q[3];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    // Set control=1, a=1, b=0
    X(q[0]);
    X(q[1]);
    // Fredkin gate (controlled-SWAP) decomposition
    // Step 1: CNOT from a to b
    CNOT(q[1], q[2]);
    // Step 2: Toffoli with control and b targeting a
    Toffoli(q[0], q[2], q[1]);
    // Step 3: CNOT from a to b
    CNOT(q[1], q[2]);
    // After swap: a=0, b=1
    M(q[1]);
    M(q[2]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis

1. **Program A** initializes q[0]=|1⟩, q[1]=|1⟩, q[2]=|0⟩ via X gates, then applies a controlled-swap (three-CNOT decomposition) (controlled-swap (three-CNOT decomposition)) decomposition: CNOT(q[1],q[2]), Toffoli(q[0],q[2],q[1]), CNOT(q[1],q[2]). Final state: |101⟩.

2. **Program B** applies the exact same sequence of gates with the same initial state preparation, yielding the same final state |101⟩.

3. **Key difference:** Program B includes `GPhase(0.0)` before the gate sequence, which applies a global phase factor of e^(i·0) = 1 — a trivial identity operation.

4. **Measurement probabilities:** GPhase(0.0) does not alter the quantum state at all. Both programs produce the identical measurement distribution: q[1]=0 with probability 1, q[2]=1 with probability 1.

5. **Verdict:** Yes — the programs are equivalent.

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/2901

- task_id: `isqTrain/2901`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_classical_vars`, `isq_syntax_for_loop`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4655`

### Prompt

这个isQ程序有问题，请找出错误并给出正确代码：

```isq
import std;
oracle bool[1] f_const(bool a[2]) {
    bool res[] = [true];
    return res;
}
qbit q[2], anc[1];
procedure main() {
    X(anc[0]);
    // H(anc[0]); // BUG: missing Hadamard
    for i in 0:2 {
        H(q[i]);
    }
    f_const(q, anc);
    for i in 0:2 {
        H(q[i]);
    }
    for i in 0:2 {
        M(q[i]);
    }
    M(anc[0]);
}

```

### Chain-of-thought reasoning

The user wants to identify and fix a bug in the provided isQ quantum program.
The bug hint says: "A Hadamard gate was removed, breaking the superposition."
Looking at the buggy code, the line `// H(anc[0]); // BUG: missing Hadamard` is commented out.
The program appears to be a Deutsch-Jozsa algorithm circuit.
State evolution in corrected circuit:
Initial: |00...0>
X(anc[0]): anc is in |1>
H(anc[0]): anc is in |->
H(q[0..1]): q is in |+>|+>
f_const(q, anc): phase oracle applies phase to |+>|+> state, or to ancilla.
Actually, `f_const` is an oracle returning `true`. In Deutsch-Jozsa, the oracle applies a phase based on f(x). Wait, `anc[0]` is |- >. The phase kickback puts a phase of -1 on the q state.
So after oracle, the state of q is -|+>|+>.
Then H(q[0..1]): H |+> |+> = |00>.
So measuring q[0..1] should give |00>.
Wait, the prompt expects: Expected measurement probabilities: {|000>: 0.5, |001>: 0.5}
Ah, if the measurements are M(q[0]), M(q[1]), M(anc[0]).
q[0] = 0, q[1] = 0. anc[0] was in |- >, which is a superposition of |0> and |1>, so measuring it gives 0 or 1 with equal probability. So the bitstrings are 000 and 001. Yes, because the first measured qubit (q[0]) corresponds to the highest bit. Wait, earlier measured qubit = higher bit. So q[0] is the highest bit. `q[0]=0, q[1]=0, anc[0]=0` gives `000`. `q[0]=0, q[1]=0, anc[0]=1` gives `001`.
This matches the predicted output: {|000>: 0.5, |001>: 0.5}.

Let's write down the bug analysis.
1. What the bug is: The line `H(anc[0])` is commented out. This gate is required to put the ancilla qubit into the |-> state, which enables phase kickback for the Deutsch-Jozsa algorithm. Without it, the oracle performs an X gate on the ancilla (since f is constant 1), leaving the input qubits in |00> but failing to demonstrate the proper phase kickback mechanics (or as per the predicted output, it breaks the superposition on the ancilla). Actually, without H(anc[0]), the ancilla is in |1>, the oracle flips it to |0>, so measuring anc gives |0> with probability 1. But the expected is {|000>: 0.5, |001>: 0.5}, meaning ancilla must be in superposition.
2. What the fix is: Uncomment the `H(anc[0])` line.
3. Brief state evolution of corrected circuit:
- X(anc[0]) puts ancilla in |1>.
- H(anc[0]) puts ancilla in |->.
- H(q[0]) and H(q[1]) put input qubits in |+>|+>.
- The oracle applies phase kickback, resulting in (-1) |+>|+> |->.
- H(q[0]) and H(q[1]) rotate input qubits back to |00>.
- Measurement of input qubits yields |00> (100% probability).
- Measurement of ancilla yields |0> or |1> (50% probability each) because it is in |-> state before measurement (since measurement is in the Z-basis).
Total state before measurement is |00>|->. So probabilities are 0.5 for |000> and 0.5 for |001>.

Let's double check if the oracle in isQ modifies the ancilla based on the returned boolean. Yes, `oracle bool[1] f_const(bool a[2])` takes `q` and `anc`. It returns `[true]`. This means it flips `anc` when `res` is `true`. Since it's constant 1, it always flips `anc`. If `anc` is in |->, flipping it (applying X) gives -|->. This introduces the phase.
Wait, if `anc` is in |1>, X(anc) gives |0>.
If `anc` is in |- >, X(anc) gives -|- >. Since the oracle is a controlled operation from the inputs... wait, no. A constant oracle that returns `true` is just
