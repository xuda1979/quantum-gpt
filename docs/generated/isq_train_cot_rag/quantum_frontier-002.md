# ISQ training COT RAG corpus: quantum_frontier shard 2

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/front/72

- task_id: `isqExpand/front/72`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `BB84`, `QKD`, `quantum_cryptography`, `basis_selection`
- source: `qa_pipeline`
- dataset_index: `376`

### Prompt

请详细解释BB84量子密钥分发协议的工作原理。包括：Alice如何选择基底和编码比特，Bob如何随机选择测量基底，基底对比后如何筛选密钥，以及该协议如何检测窃听者Eve的存在。用isQ代码展示Alice在Z基底下编码bit=0和在X基底下编码bit=1的电路。

### Chain-of-thought reasoning

## 推理
目标：全面解释BB84协议的四个阶段。

Alice在两组共轭基底（Z和X）中编码随机比特。Bob随机选基底测量。基底匹配时结果确定，不匹配时结果随机——这是协议筛选密钥的基础。

窃听检测利用量子力学的测量坍缩：Eve的截获-测量-重发策略在基底不匹配时引入约25%错误率。不可克隆定理保证Eve没有更好的策略。

### Reference answer

## BB84量子密钥分发协议

### 协议概述
BB84是1984年由Bennett和Brassard提出的第一个量子密钥分发协议，利用量子力学的不可克隆定理和测量坍缩特性来实现安全的密钥分发。

### 工作流程

**第一步：量子态准备（Alice）**
Alice随机选择：
- 一个随机比特值（0或1）
- 一个随机基底（Z基底或X基底）

编码规则：
| 比特值 | Z基底 | X基底 |
|--------|-------|-------|
|   0    | |0⟩   | |+⟩ = H|0⟩ |
|   1    | |1⟩   | |−⟩ = H|1⟩ |

**第二步：量子态测量（Bob）**
Bob随机选择Z或X基底测量收到的量子态：
- 若基底匹配：测量结果确定性地等于Alice发送的比特
- 若基底不匹配：测量结果完全随机（50%概率得到0或1）

**第三步：基底对比（经典信道）**
Alice和Bob通过公开信道对比各自选择的基底（不公开比特值），丢弃基底不匹配的比特，保留基底匹配的比特作为原始密钥。

**第四步：窃听检测**
随机选取部分密钥比特通过公开信道对比：
- 如果错误率为0%：无窃听，剩余比特作为安全密钥
- 如果错误率约25%：存在窃听者Eve

### 窃听检测原理
Eve必须选择一个基底来测量截获的量子态。由于不可克隆定理，她无法复制未知量子态。当她选错基底（概率50%）时，测量会破坏量子态，然后她重新制备的态将在Alice和Bob基底匹配时引入约25%的错误率。

### isQ实现示例
```isq
import std;
qbit q[2];

procedure main() {
    // q[0]: bit=0, Z基底 -> 不做任何操作，保持|0⟩
    // q[1]: bit=1, X基底 -> X(q[1])然后H(q[1])得到|−⟩
    X(q[1]);
    H(q[1]);
    M(q[0]); M(q[1]);
}
```

### 安全性基础
1. **量子不可克隆定理**：Eve无法完美复制未知量子态
2. **测量坍缩**：错误基底的测量不可逆地改变量子态
3. **信息论安全**：安全性基于物理定律而非计算复杂度假设

## isqExpand/front/35

- task_id: `isqExpand/front/35`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `hamiltonian_simulation`, `feynman`, `quantum_advantage`
- source: `isq_expansion_qa`
- dataset_index: `2889`

### Prompt

解释哈密顿量模拟（Hamiltonian simulation）在量子计算中的重要性。为什么Feynman认为量子系统应该用量子计算机来模拟？

### Chain-of-thought reasoning

## 推理
经典模拟量子系统面临指数级内存和时间瓶颈。Feynman洞察到量子计算机可以自然地表示量子态，用多项式资源模拟量子演化。这是量子计算的核心动机之一。

### Reference answer

哈密顿量模拟是指使用量子计算机来模拟量子系统随时间的演化，即实现时间演化算符e^{-iHt}，其中H是系统的哈密顿量。

**Feynman的洞察（1982年）：**
Feynman指出，模拟n个量子粒子的系统需要跟踪2^n个复数振幅——这对经典计算机来说是指数级增长的资源需求。例如，50个量子比特的系统需要约2^50 ≈ 10^15个复数来描述其态矢量。而量子计算机可以直接用n个量子比特来自然地表示和演化该系统。

**重要性：**
1. 材料科学：模拟新材料的电子结构和性质（如高温超导体）。
2. 药物设计：模拟分子间相互作用，加速药物发现。
3. 化学反应：预测化学反应路径和速率。
4. 基础物理：研究量子多体物理中的相变、拓扑序等现象。

**主要方法：**
1. Trotter-Suzuki分解：将e^{-iHt}分解为局部项的乘积。
2. 线性组合方法（LCU）：将哈密顿量表示为酉操作的线性组合。
3. 量子信号处理（QSP）：通过多项式变换实现最优模拟。
4. 变分方法：用参数化电路近似时间演化。

哈密顿量模拟被认为是量子计算最有前景的应用之一，可能在化学和材料科学中率先展示实用量子优势。

## isqExpand/front/131

- task_id: `isqExpand/front/131`
- task_type: `bug_fix`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `qml`, `angle_encoding`, `rotation_gates`, `amplitude_encoding`, `phase_error`
- source: `isq_expansion`
- dataset_index: `3423`

### Prompt

The following QML angle encoding circuit produces incorrect measurement probabilities. In quantum machine learning, Ry rotation is the standard choice for angle encoding because it maps real-valued features to real-valued amplitudes without introducing complex phases. The circuit encodes an angle of π/2 on qubit 0, applies a Hadamard gate, then entangles with qubit 1 via CNOT. The expected result should leave the system in state |00⟩ with certainty. Fix the encoding rotation gate to produce the correct amplitude distribution.

### Chain-of-thought reasoning

Step 1: Identify the bug. The circuit uses Rx(π/2) for angle encoding, but Ry is the standard QML encoding gate because it produces real amplitudes. Step 2: Trace the buggy circuit. Rx(π/2)|0⟩ = cos(π/4)|0⟩ - i·sin(π/4)|1⟩ = (1/√2)|0⟩ - i(1/√2)|1⟩. This introduces a complex phase -i on the |1⟩ component. Step 3: After H on q0: H maps |0⟩→(|0⟩+|1⟩)/√2 and |1⟩→(|0⟩-|1⟩)/√2, so the state becomes (1/2)(1-i)|00⟩ + (1/2)(1+i)|10⟩. After CNOT(0,1): (1/2)(1-i)|00⟩ + (1/2)(1+i)|11⟩. Probabilities: P(00)=|1-i|²/4=2/4=0.5, P(11)=|1+i|²/4=2/4=0.5. Step 4: With Ry(π/2)|0⟩ = (1/√2)|0⟩ + (1/√2)|1⟩ (purely real amplitudes). After H: the orthogonal components cancel on |1⟩ leaving pure |0⟩ on q0. After CNOT: state is |00⟩ with probability 1.0. Step 5: The fix is replacing Rx with Ry, eliminating the spurious complex phase that disrupts the constructive/destructive interference pattern.

## isqExpand/front/22

- task_id: `isqExpand/front/22`
- task_type: `output_prediction`
- category: `quantum_frontier`
- difficulty: `difficult`
- concept_tags: `output_prediction`, `variational_classifier`, `pqc`, `quantum_ml`
- source: `isq_expansion`
- dataset_index: `3719`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[2];

procedure main() {
    // Layer 1: data encoding + entanglement
    Ry(pi/4.0, q[0]);
    Ry(pi/3.0, q[1]);
    CNOT(q[0], q[1]);
    // Layer 2: variational parameters + entanglement
    Ry(pi/6.0, q[0]);
    Ry(pi/2.0, q[1]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. Initial state: |00>
2. Ry(pi/4, q[0]): cos(pi/8)|0> + sin(pi/8)|1> on q[0]
3. Ry(pi/3, q[1]): cos(pi/6)|0> + sin(pi/6)|1> on q[1]
4. CNOT(q[0],q[1]): entangles, flipping q[1] when q[0]=1
5. Ry(pi/6, q[0]): additional rotation on q[0]
6. Ry(pi/2, q[1]): large rotation on q[1]
7. CNOT(q[0],q[1]): second entanglement

The exact computation requires tracking complex amplitudes through two entangling layers. Numerical simulation yields:
P(|00>) = 0.066, P(|01>) = 0.587, P(|10>) = 0.346, P(|11>) = 0.001.

The circuit strongly favors |01> because the combination of rotation angles and entanglement funnels amplitude into this state.

### Reference answer

{'predicted_probs': {'0': 0.0658, '1': 0.5872, '2': 0.3458, '3': 0.0011}, 'explanation': 'This is a 2-layer parameterized quantum circuit (PQC). Layer 1: Ry(pi/4) on q[0] and Ry(pi/3) on q[1] encode data, then CNOT entangles. Layer 2: Ry(pi/6) and Ry(pi/2) add variational parameters, then another CNOT. The two layers of rotation+entanglement create a complex state where most probability concentrates on |01> (0.587) and |10> (0.346), with very little on |00> (0.066) and |11> (0.001). The dominant |01> outcome reflects the combined effect of the rotation angles pushing amplitude toward this basis state.'}

## isqExpand/front/143

- task_id: `isqExpand/front/143`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `basic`
- concept_tags: `bb84`, `quantum_key_distribution`, `z_basis_measurement`, `basis_matching`, `deterministic_state`
- source: `isq_expansion`
- dataset_index: `647`

### Prompt

I need an isQ program to implementing a simplified BB84 scenario: Alice prepares a qubit in the |0> state using the Z basis (no Hadamard applied), and Bob measures it in the Z basis as well. Since both parties use the same basis, the measurement outcome should be deterministic — always |0>. Use a single qubit and provide the circuit with no additional gates needed.

### Chain-of-thought reasoning

In the BB84 protocol, Alice encodes a classical bit into a qubit using one of two bases: Z (computational) or X (Hadamard). Bob measures the qubit using his randomly chosen basis. In this simplified scenario, Alice encodes bit 0 in the Z basis, meaning she prepares the state |0> (the default state after initialization). Since Bob also measures in the Z basis (the bases match), the Born rule tells us that the probability of measuring |0> is |<0|0>|^2 = 1.0, and the probability of measuring |1> is |<1|0>|^2 = 0.0. Therefore, no quantum gates are needed — the qubit starts in |0> and remains in |0>. The expected probability distribution is [1.0, 0.0] for the basis states {|0>, |1>}.

## isqExpand/front/120

- task_id: `isqExpand/front/120`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `difficult`
- concept_tags: `quantum_error_correction`, `repetition_code`, `bit_flip_error`, `syndrome_measurement`, `encoding_circuit`, `quantum_error_correcting_codes`
- source: `qa_pipeline`
- dataset_index: `993`

### Prompt

详细解释3-qubit repetition码如何检测和纠正bit-flip错误。给出编码电路和纠错流程。

### Chain-of-thought reasoning

首先分析3-qubit repetition码的核心思想：通过将一个逻辑比特编码到三个物理比特中实现冗余。逻辑|0⟩编码为|000⟩，逻辑|1⟩编码为|111⟩。编码电路需要两个CNOT门，将数据比特q[0]的信息复制到q[1]和q[2]。然后分析bit-flip错误的影响：单比特X错误会将|000⟩变为|100⟩、|010⟩或|001⟩。为了检测哪个比特出错，需要测量两对奇偶校验子：s0=q[0]⊕q[1]和s1=q[0]⊕q[2]。通过比较三个比特之间的奇偶性，可以唯一确定错误位置。syndrome测量使用两个辅助比特，通过CNOT门实现，不直接测量数据比特从而保护量子叠加态。最后根据校验子结果施加条件X门进行纠错。整个过程需要确保不破坏编码的量子信息。

### Reference answer

3-qubit repetition码是最简单的量子纠错码之一，专门用于检测和纠正单比特bit-flip（X）错误。

## 一、编码方案

逻辑态定义：
- |0⟩_L = |000⟩
- |1⟩_L = |111⟩

对于一般量子态 α|0⟩ + β|1⟩，编码后变为 α|000⟩ + β|111⟩。

## 二、编码电路

使用3个量子比特 q[0]、q[1]、q[2]，其中 q[0] 为数据比特，q[1]、q[2] 初始为 |0⟩：

```
import std;

qbit q[3];

procedure main() {
    // 假设 q[0] 已制备为待编码态 α|0⟩+β|1⟩
    // q[1], q[2] 初始为 |0⟩
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);
    // 编码完成：α|000⟩ + β|111⟩
}
```

编码后的态是 GHZ 态 α|000⟩ + β|111⟩，三个比特携带相同的信息。

## 三、错误模型

Bit-flip 错误意味着某一位可能被翻转（X门作用）：
- 无错误：α|000⟩ + β|111⟩
- q[0] 翻转：α|100⟩ + β|011⟩
- q[1] 翻转：α|010⟩ + β|101⟩
- q[2] 翻转：α|001⟩ + β|110⟩

## 四、纠错电路（syndrome测量 + 条件修正）

引入两个辅助比特 a[0]、a[1] 来测量校验子（syndrome）：

```
import std;

qbit q[3];
qbit a[2];

procedure main() {
    // ===== 编码阶段 =====
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);

    // ===== 错误发生（此处模拟 X 错误） =====
    // X(q[1]); // 例如 q[1] 发生 bit-flip

    // ===== Syndrome 测量 =====
    // a[0] 测量 q[0]⊕q[1] 的奇偶性
    CNOT(q[0], a[0]);
    CNOT(q[1], a[0]);
    // a[1] 测量 q[0]⊕q[2] 的奇偶性
    CNOT(q[0], a[1]);
    CNOT(q[2], a[1]);

    // 测量辅助比特
    int s0 = M(a[0]);
    int s1 = M(a[1]);

    // ===== 根据校验子纠错 =====
    // (s0,s1)=(0,0): 无错误
    // (s0,s1)=(1,1): q[0] 翻转
    // (s0,s1)=(1,0): q[1] 翻转
    // (s0,s1)=(0,1): q[2] 翻转
    if (s0 == 1 && s1 == 1) { X(q[0]); }
    if (s0 == 1 && s1 == 0) { X(q[1]); }
    if (s0 == 0 && s1 == 1) { X(q[2]); }
}
```

## 五、校验子真值表

| 错误位置 | 编码态 (以|0⟩_L为例) | s0=q0⊕q1 | s1=q0⊕q2 | 纠错操作 |
|---------|---------------------|-----------|-----------|----------|
| 无错误  | 000                 | 0         | 0         | 无       |
| q[0]    | 100                 | 1         | 1         | X(q[0])  |
| q[1]    | 010                 | 1         | 0         | X(q[1])  |
| q[2]    | 001                 | 0         | 1         | X(q[2])  |

## 六、关键性质

1. **不破坏量子态**：syndrome测量只提取错误信息（奇偶性），不测量数据比特本身，因此不会坍缩量子叠加态 α|0⟩_L + β|1⟩_L。

2. **纠错能力**：3-qubit repetition码只能纠正单比特X错误。如果两个或三个比特同时出错，则无法正确纠正。

3. **与相位翻转码的关系**：对3-qubit repetition码的每个物理比特做 Hadamard 变换（H基变换），可以得到一个检测相位翻转（Z错误）的码，这是因为 HXH = Z。

## isqExpand/front/6

- task_id: `isqExpand/front/6`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `difficult`
- concept_tags: `error_correction`, `steane_code`, `css_code`
- source: `qa_pipeline`
- dataset_index: `4222`

### Prompt

解释Steane码（[[7,1,3]]码）的基本结构和工作原理。它相比三量子比特码有什么优势？

### Chain-of-thought reasoning

## 推理
Steane码是基于经典Hamming码的CSS码构造。它用7个物理比特编码1个逻辑比特，6个稳定子生成元分为X型和Z型各3个。X型稳定子检测Z错误，Z型稳定子检测X错误。距离d=3意味着可以纠正任意单比特错误（包括X、Y、Z），远优于只能纠正单一类型错误的三比特码。

### Reference answer

Steane码是一种[[7,1,3]]CSS量子纠错码，使用7个物理量子比特编码1个逻辑量子比特，最小距离为3，可纠正任意单量子比特错误。

它基于经典[7,4,3] Hamming码构造。逻辑态为：
|0⟩_L = (1/√8)Σ_{c∈C}|c⟩，其中C是[7,4,3]码的偶校验子码
|1⟩_L = (1/√8)Σ_{c∈C}|c⊕1111111⟩

Steane码有6个稳定子生成元（3个X型，3个Z型），分别检测Z错误和X错误。这是CSS码的特点——X型和Z型稳定子互相独立。

相比三量子比特码的优势：
1. 三量子比特码只能纠正比特翻转(X)或相位翻转(Z)中的一种，Steane码可同时纠正X、Y、Z任意单比特错误。
2. Steane码支持横向(transversal)逻辑门操作，使容错量子计算更容易实现。
3. 作为CSS码，其syndrome解码结构简洁，X和Z错误可独立处理。

## isqExpand/front/89

- task_id: `isqExpand/front/89`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `difficult`
- concept_tags: `xx_interaction`, `hamiltonian_simulation`, `basis_change`, `excitation_transfer`
- source: `isq_expansion`
- dataset_index: `1727`

### Prompt

Code this in isQ: implements the time evolution under the XX interaction Hamiltonian: H = X0*X1, with time t = pi/8.

The circuit for e^{-i(X0X1)t} uses the identity that conjugating ZZ by Hadamard gates on both qubits gives XX:
e^{-i(X0X1)t} = (H⊗H) e^{-i(Z0Z1)t} (H⊗H)

And e^{-i(Z0Z1)t} = CNOT(q[0],q[1]) Rz(2t, q[1]) CNOT(q[0],q[1]).

So the full circuit is: H(q[0]), H(q[1]), CNOT(q[0],q[1]), Rz(pi/4.0, q[1]), CNOT(q[0],q[1]), H(q[0]), H(q[1]).

Requirements:
- Declare global `qbit q[2];`
- Prepare the initial state |01> by applying X(q[1]).
- Apply the XX evolution circuit as described above.
- Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Simulate e^{-i(XX)t}|01> with t=pi/8.

The XX interaction preserves total excitation number. Starting from |01> (one excitation), it can evolve to a superposition of |01> and |10>.

Circuit: HH-CNOT-Rz(2t)-CNOT-HH implements e^{-i(XX)t} because H converts X basis to Z basis.

For |01>:
- e^{-i(XX)t}|01> = cos(t)|01> - i sin(t)|10>
- P(|01>) = cos^2(pi/8) ≈ 0.8536
- P(|10>) = sin^2(pi/8) ≈ 0.1464
- P(|00>) = P(|11>) = 0 (excitation number conservation)

The XX interaction is fundamental in spin chain models and quantum state transfer.

## isqExpand/front/87

- task_id: `isqExpand/front/87`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `trotter_decomposition`, `ising_model`, `time_evolution`, `zz_interaction`
- source: `isq_expansion`
- dataset_index: `1152`

### Prompt

Create an isQ quantum circuit that implements a single first-order Trotter step for the 2-qubit Ising Hamiltonian H = Z0*Z1 + X0 + X1 with time parameter t = pi/6.

The first-order Trotter approximation decomposes e^{-iHt} as:
e^{-i(X0)t} * e^{-i(X1)t} * e^{-i(Z0Z1)t}

Circuit implementation:
- e^{-iXt} is implemented as Rx(2t, q) for each qubit.
- e^{-i(Z0Z1)t} is implemented as CNOT(q[0],q[1]), Rz(2t, q[1]), CNOT(q[0],q[1]).

Requirements:
- Declare global `qbit q[2];`
- First prepare q[0] in the |+> state using H(q[0]).
- Apply the X rotation terms: Rx(pi/3.0, q[0]) and Rx(pi/3.0, q[1]).
- Apply the ZZ interaction: CNOT(q[0],q[1]), Rz(pi/3.0, q[1]), CNOT(q[0],q[1]).
- Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement one first-order Trotter step for H = ZZ + X0 + X1.

Decomposition at t = pi/6:
1. e^{-iXt} on q[0]: Rx(2t=pi/3)
2. e^{-iXt} on q[1]: Rx(2t=pi/3)
3. e^{-iZZt}: CNOT(0,1) Rz(2t=pi/3, q[1]) CNOT(0,1)

Starting from |+0> = H(q[0])|00>:
- After Rx gates and ZZ decomposition, the final state has probabilities:
  |00>: 0.375, |01>: 0.125, |10>: 0.375, |11>: 0.125

The ZZ interaction on |+0> is non-trivial because |+0> is not a ZZ eigenstate. The CNOT-Rz-CNOT decomposition implements exp(-iZZt) by mapping ZZ to local Rz via entangling gates.

## isqExpand/front/19

- task_id: `isqExpand/front/19`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `vqe`, `h2_molecule`, `uccsd`, `quantum_chemistry`
- source: `isq_expansion`
- dataset_index: `1369`

### Prompt

Write an isQ program that implements a minimal VQE (Variational Quantum Eigensolver) ansatz for simulating the H2 molecule.

In the minimal basis (STO-3G), H2 has 2 molecular orbitals mapped to 2 qubits via the Jordan-Wigner transformation. The Hartree-Fock initial state is |01⟩ (one electron in orbital 1). A single-parameter UCCSD-inspired ansatz applies a Ry rotation followed by CNOT to create the trial state.

Requirements:
- Declare global `qbit q[2];`
- Prepare the Hartree-Fock state |01⟩ by applying X(q[1]).
- Apply the variational rotation Ry(pi/3.0, q[0]) as the excitation parameter.
- Apply CNOT(q[0], q[1]) to entangle (single excitation operator).
- Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Minimal VQE ansatz for H2 molecule simulation.

1. X(q[1]): |00> -> |01> (Hartree-Fock state, 1 electron in orbital 1).
2. Ry(pi/3, q[0]): q[0] becomes cos(pi/6)|0> + sin(pi/6)|1>.
   State: cos(pi/6)|01> + sin(pi/6)|11>.
3. CNOT(q[0],q[1]): flips q[1] when q[0]=1.
   cos(pi/6)|01> + sin(pi/6)|10>.

This creates a superposition of |01> (both electrons in orbital 1) and |10> (both in orbital 0), which is the form of a single excitation operator in UCCSD.

P(|01>) = cos^2(pi/6) = 3/4 = 0.75
P(|10>) = sin^2(pi/6) = 1/4 = 0.25
