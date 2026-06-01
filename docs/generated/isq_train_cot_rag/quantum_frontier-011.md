# ISQ training COT RAG corpus: quantum_frontier shard 11

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/front/84

- task_id: `isqExpand/front/84`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `trotter_decomposition`, `product_formula`, `hamiltonian_simulation`, `approximation_error`
- source: `isq_expansion_qa`
- dataset_index: `4518`

### Prompt

解释Trotter-Suzuki分解的基本原理。对于两个不对易的哈密顿量A和B，为什么不能直接将 e^{i(A+B)t} 分解为 e^{iAt}·e^{iBt}？一阶Trotter公式如何近似这个指数？误差阶数是多少？请结合量子模拟的实际场景说明其重要性。

### Chain-of-thought reasoning

## 推理
目标：解释Trotter-Suzuki分解为什么需要以及如何工作。

核心逻辑链：
1. 非对易算符→指数不可直接拆分（BCH公式中的对易子项）
2. 将时间切成小段→每段误差为O(dt²)→n步总误差O(t²/n)
3. 对称化得二阶公式，误差降为O(t³/n²)
4. 量子模拟中H=ΣHⱼ，每个局部项可用少量门实现，Trotter使全局演化可行

这是量子模拟的基础性概念，连接了量子力学和量子计算。

### Reference answer

## Trotter-Suzuki分解

### 核心问题
对于两个算符A和B，只有当 [A,B]=0（即AB=BA）时，才有精确等式：
e^{A+B} = e^A · e^B

当A和B不对易时（如量子力学中的动能和势能项），上式不再成立。差异来源于Baker-Campbell-Hausdorff公式中的对易子项：
e^A e^B = e^{A+B+[A,B]/2+...}

### 一阶Trotter公式
将时间t分成n个小步，每步dt=t/n：

e^{i(A+B)t} ≈ (e^{iA·dt} · e^{iB·dt})^n

这就是一阶Trotter公式（也称Lie-Trotter乘积公式）。其误差来自被忽略的对易子项。

### 误差分析
- 单步误差：O(dt²) = O(t²/n²)，因为展开中首个被忽略的项是 [A,B]dt²/2
- 累积n步后总误差：O(t²/n)
- 因此，要达到精度ε，需要 n = O(t²/ε) 步

### 二阶Trotter（Suzuki分解）
通过对称化可将精度提升到二阶：
S₂(dt) = e^{iA·dt/2} · e^{iB·dt} · e^{iA·dt/2}

- 单步误差：O(dt³)
- 总误差：O(t³/n²)

### 量子模拟中的重要性
在量子模拟中，待模拟的哈密顿量H通常可分解为多个局部项之和：
H = H₁ + H₂ + ... + Hₖ

每个局部项 e^{iHⱼdt} 可以用少量量子门实现，但完整的 e^{iHt} 无法直接高效实现。Trotter分解将一个困难的全局演化近似为一系列简单的局部演化的乘积，使量子模拟成为可能。

### isQ中的一阶Trotter示例
对于2-qubit Ising模型 H = Z₀Z₁ + X₀ + X₁：
```isq
import std;
qbit q[2];
procedure main() {
    // 一阶Trotter单步，t=pi/4
    // e^{-iXt}: Rx(2t) on each qubit
    Rx(pi/2.0, q[0]);
    Rx(pi/2.0, q[1]);
    // e^{-iZZt}: CNOT-Rz-CNOT
    CNOT(q[0], q[1]);
    Rz(pi/2.0, q[1]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

## isqExpand/front/25

- task_id: `isqExpand/front/25`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `quantum_ml`, `quantum_kernel`, `feature_map`
- source: `isq_expansion`
- dataset_index: `3385`

### Prompt

Implement the following in isQ: implements a 2-qubit quantum kernel feature map.

A quantum kernel feature map transforms classical data into a quantum state using rotations and entanglement. The feature map is:
1. Apply Ry(x_0) and Ry(x_1) for data encoding.
2. Apply CNOT(q[0], q[1]) for entanglement.
3. Apply Rz(x_0 * x_1) to capture feature interaction.

Use x_0 = pi/3 and x_1 = pi/4.

Requirements:
- Declare global `qbit q[2];`
- Apply the feature map as described.
- Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. Ry(pi/3)|0⟩ = cos(pi/6)|0⟩+sin(pi/6)|1⟩ = (sqrt(3)/2)|0⟩+(1/2)|1⟩.
2. Ry(pi/4)|0⟩ = cos(pi/8)|0⟩+sin(pi/8)|1⟩.
3. After CNOT and Rz interaction, the state becomes entangled with feature-dependent phases. The Rz gate applies a z-rotation with angle pi^2/12 to capture the product interaction between features.

## isqExpand/front/90

- task_id: `isqExpand/front/90`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `difficult`
- concept_tags: `heisenberg_model`, `trotter_decomposition`, `zz_interaction`, `xx_interaction`
- source: `isq_expansion`
- dataset_index: `4319`

### Prompt

Write an isQ program that implements a first-order Trotter step for a partial 2-qubit Heisenberg model H = Z0*Z1 + X0*X1 with time t = pi/8.

The Trotter decomposition is: e^{-iHt} ≈ e^{-i(Z0Z1)t} * e^{-i(X0X1)t}

Circuit:
1. ZZ term: CNOT(q[0],q[1]), Rz(pi/4.0, q[1]), CNOT(q[0],q[1]).
2. XX term: H(q[0]), H(q[1]), CNOT(q[0],q[1]), Rz(pi/4.0, q[1]), CNOT(q[0],q[1]), H(q[0]), H(q[1]).

Requirements:
- Declare global `qbit q[2];`
- Prepare |01> by applying X(q[1]).
- Apply the ZZ interaction circuit.
- Apply the XX interaction circuit.
- Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Trotter decompose e^{-i(ZZ+XX)t}|01>, t=pi/8.

Step 1 - ZZ on |01>: ZZ eigenvalue for |01> is (+1)(-1) = -1.
e^{-i(-1)t}|01> = e^{it}|01>. This is just a global phase — no probability change.

Step 2 - XX on e^{it}|01>: Same as XX on |01> (global phase doesn't affect XX).
e^{-i(XX)t}|01> = cos(t)|01> - i sin(t)|10>.
P(|01>) = cos^2(pi/8) ≈ 0.8536, P(|10>) = sin^2(pi/8) ≈ 0.1464.

The ZZ term adds phases that become important with different initial states or additional Trotter steps, but for single-step |01> the probabilities match the XX-only case.

## isqExpand/front/153

- task_id: `isqExpand/front/153`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `expert`
- concept_tags: `quantum_internet`, `protocol_stack`, `entanglement_distribution`, `link_layer`, `network_layer`, `quantum_repeaters`, `entanglement_swapping`, `quantum_communication`
- source: `qa_pipeline`
- dataset_index: `4044`

### Prompt

量子互联网的分层架构是什么？从链路层到应用层各负责什么功能？

### Chain-of-thought reasoning

首先回顾量子互联网研究中的经典分层架构模型，主要参考 Stephanie Wehner、David Elkouss 和 Ronald Hanson 等人在 2018 年发表的综述性论文「Quantum internet: A vision for the road ahead」以及后续的量子网络协议栈研究。该架构仿照经典网络分层思想，将量子互联网功能划分为物理层、链路层、网络层、传输层和应用层。然后逐层分析各层职责：物理层负责量子信号的物理传输与处理；链路层负责相邻节点间预示式纠缠对的生成与管理，提供可靠的链路段纠缠；网络层通过纠缠交换和路由实现长距离端到端纠缠建立；传输层负责可靠的量子态传输和 teleportation 全流程管理；应用层则承载 QKD、分布式量子计算、量子传感等终端应用。最后阐述各层之间的协作关系，强调分层解耦设计的优势。整篇回答需涵盖每层的核心功能、关键技术和典型协议，体现 expert 级别的深入理解。

### Reference answer

量子互联网的分层架构借鉴了经典互联网协议栈的思想，但针对量子通信的独特需求（如不可克隆定理、纠缠资源管理等）进行了专门设计。该架构主要由以下五个层次组成：

**1. 物理层（Physical Layer）**
- 负责实际的量子比特（量子信号）在物理信道中的传输与操作。
- 涉及单光子源、纠缠光子对产生、量子存储器、光学器件（如电光调制器、波分复用器）以及量子中继器节点之间的物理连接。
- 核心挑战包括光子损耗、退相干和探测器噪声。

**2. 链路层（Link Layer）**
- 负责在两个直接相连（相邻）的量子节点之间建立可靠的纠缠链路。
- 提供"预示式"（heralded）的纠缠生成：即双方能够确认纠缠是否成功建立。
- 管理纠缠对的保真度、生成速率，并在需要时进行纠缠纯化（purification）以提升链路质量。
- 典型协议如 MHP（Midpoint Heralding Protocol），通过中间站 heralding 确认纠缠成功。
- 链路层向上层提供"即用型"（ready-to-use）的纠缠对作为抽象服务。

**3. 网络层（Network Layer）**
- 负责跨多个中间节点建立端到端的远距离纠缠连接。
- 核心功能包括纠缠交换（entanglement swapping）：将相邻链路段的短距离纠缠连接成长距离纠缠。
- 执行路由选择（routing），决定纠缠路径以优化传输效率。
- 管理量子中继器之间的资源调度和多路复用。
- 网络层使得不相邻的节点也能共享纠缠资源。

**4. 传输层（Transport Layer）**
- 负责端到端的可靠量子数据传输和量子态传输（quantum state transfer）。
- 管理 quantum teleportation 的完整流程：包括贝尔态测量结果的经典通信、量子态重构等。
- 提供服务质量（QoS）保障，如保证传输的量子态保真度满足应用需求。
- 可通过多轮纠缠纯化和量子纠错确保端到端传输的可靠性。

**5. 应用层（Application Layer）**
- 面向最终用户和上层量子应用，利用底层提供的纠缠资源完成具体任务。
- 典型应用包括：
  - 量子密钥分发（QKD）：实现无条件安全通信；
  - 分布式量子计算：连接多个量子处理器协同运算；
  - 量子传感（quantum sensing）：利用纠缠提升测量精度，如量子时钟同步、量子成像；
  - 盲量子计算（blind quantum computation）：在保护隐私的前提下委托量子计算；
  - 量子投票、量子秘密共享等安全多方计算协议。
- 应用层只需调用下层提供的纠缠或量子传输接口，无需关心底层物理实现细节。

**各层之间的协作关系：**
物理层提供原始量子信号传输能力 → 链路层将其封装为相邻节点间的可靠纠缠对 → 网络层通过纠缠交换将纠缠扩展至远距离 → 传输层确保端到端的量子态可靠传送 → 应用层基于这些能力实现各类量子信息处理任务。这种分层解耦设计使得每一层可以独立优化，同时为上层的量子应用开发提供了清晰的抽象接口。

## isqExpand/front/3

- task_id: `isqExpand/front/3`
- task_type: `output_prediction`
- category: `quantum_frontier`
- difficulty: `basic`
- concept_tags: `error_correction`, `bit_flip_code`, `error_simulation`
- source: `isq_expansion`
- dataset_index: `1050`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;
qbit q[3];

procedure main() {
    // Encode |0> in bit-flip code
    // (no X gate, so q[0] stays |0>)
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);
    // Simulate a bit-flip error on q[1]
    X(q[1]);
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Reasoning
1. Initial state: |000⟩.
2. CNOT(q[0],q[1]): q[0]=0, no flip. State: |000⟩.
3. CNOT(q[0],q[2]): q[0]=0, no flip. State: |000⟩.
4. X(q[1]): flips q[1]. State: |010⟩.
5. |010⟩ is index 0*4+1*2+0*1 = 2.
6. P(|010⟩) = 1.0.

### Reference answer

{'predicted_probs': {'2': 1.0}, 'explanation': 'Starting from |000>, CNOT gates have no effect (control is 0). Then X(q[1]) flips q[1] to |1>. Final state is |010>, which is index 2.'}

## isqExpand/front/140

- task_id: `isqExpand/front/140`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `difficult`
- concept_tags: `Trotter-Suzuki分解`, `BCH公式`, `哈密顿量模拟`, `误差分析`, `时间反演对称性`
- source: `qa_pipeline`
- dataset_index: `727`

### Prompt

比较一阶Trotter分解与二阶Suzuki分解（Strang分裂）的误差阶。为什么二阶方法更精确？请从Baker-Campbell-Hausdorff (BCH) 公式和时间反演对称性的角度进行分析。

### Chain-of-thought reasoning

第一步：明确问题的核心——比较Lie-Trotter（一阶）和Strang分裂（二阶）两种Trotter化方法的近似误差阶。

第二步：回顾一阶Trotter公式。对于 $H=\sum H_j$，一阶近似为 $S_1(\Delta t) = \prod e^{-iH_j \Delta t}$。利用BCH公式，$e^A e^B = e^{A+B+\frac{1}{2}[A,B]+...}$，展开后误差首项为 $O(\Delta t^2)$ 来自对易子，累计 $n$ 步后总误差 $O(n \Delta t^2) = O(t^2/n)$。

第三步：分析二阶Strang分裂 $S_2(\Delta t) = \prod_{j=1}^L e^{-iH_j \Delta t/2} \prod_{j=L}^1 e^{-iH_j \Delta t/2}$。关键性质：这是对称分裂，满足 $S_2(-\Delta t) \cdot S_2(\Delta t) = I + O(\Delta t^3)$。

第四步：从时间反演对称性论证。$S_2(\Delta t) = e^{-i\tilde{H}\Delta t}$，其中 $\tilde{H}$ 的展开中，对称性要求奇数阶项为零，因此误差首项为 $O(\Delta t^3)$，总误差 $O(n\Delta t^3) = O(t^3/n^2)$。

第五步：从BCH角度直接验证。前后两个半步的BCH展开中，$O(\Delta t^2)$ 的对易子项因正负抵消而消失，剩余误差从 $O(\Delta t^3)$ 起始。

第六步：总结结论——二阶方法因对称结构消除了低阶误差项，从 $O(t^2/n)$ 提升到 $O(t^3/n^2)$，在实用中显著降低门复杂度。

### Reference answer

一阶Trotter分解（Lie-Trotter）与二阶Suzuki分解（Strang分裂）的误差阶比较：

**一阶Trotter分解（Lie-Trotter）：**
对于哈密顿量 $H = \sum_{j=1}^{L} H_j$，一阶Trotter公式为：
$$S_1(\Delta t) = \prod_{j=1}^{L} e^{-i H_j \Delta t}$$
其中 $\Delta t = t/n$。利用BCH公式展开，误差项的首阶贡献为：
$$\left\| e^{-iHt} - \left(S_1(t/n)\right)^n \right\| = O\left(\frac{L^2 \max\|H_j\|^2 \cdot t^2}{n}\right)$$
即总误差为 $O(t^2/n)$，关于步长 $\Delta t = t/n$ 是一阶的。

**二阶Suzuki分解（Strang分裂）：**
$$S_2(\Delta t) = \prod_{j=1}^{L} e^{-i H_j \Delta t/2} \cdot \prod_{j=L}^{1} e^{-i H_j \Delta t/2}$$
总误差为：
$$\left\| e^{-iHt} - \left(S_2(t/n)\right)^n \right\| = O\left(\frac{L^3 \max\|H_j\|^3 \cdot t^3}{n^2}\right)$$
即误差为 $O(t^3/n^2)$，关于步长是二阶的。

**为什么二阶更精确？**

1. **时间反演对称性**：二阶Suzuki分解是对称的，即 $S_2(-\Delta t) \cdot S_2(\Delta t) = I + O(\Delta t^3)$。这种对称性意味着 $S_2(\Delta t)$ 可以被视为某个等效哈密顿量 $\tilde{H}$ 的精确演化算符。根据对称性，$\tilde{H}$ 的展开式中所有奇数阶修正项必须为零（因为奇函数在对称区间上积分为零）。因此，第一个非零误差项出现在 $O(\Delta t^2)$ 级别，对应总误差 $O(\Delta t^2) = O(t^3/n^2)$。

2. **BCH公式分析**：将 $S_1(\Delta t)$ 用BCH公式展开为 $\exp\left(-iH\Delta t - \frac{\Delta t^2}{2}\sum_{j<k}[H_j,H_k] + O(\Delta t^3)\right)$，可见一阶误差来自对易子项 $-\frac{\Delta t^2}{2}[H_j,H_k]$。对于 $S_2(\Delta t)$，BCH展开中 $\Delta t^2$ 的对易子项因为前后半步的对称结构而精确抵消，第一个非零误差项出现在 $O(\Delta t^3)$，对应三体对易子如 $[H_j,[H_k,H_l]]$ 等。

**实用意义**：对于 $n$ 步模拟，达到精度 $\epsilon$ 所需的门数分别为：一阶需要 $O(L^2 t^2 / \epsilon)$，二阶需要 $O(L^{3/2} t^{3/2} / \sqrt{\epsilon})$。二阶方法在门复杂度上有显著优势。

## isqExpand/front/144

- task_id: `isqExpand/front/144`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `basic`
- concept_tags: `bb84`, `hadamard`, `x_basis_measurement`, `quantum_key_distribution`
- source: `isq_expansion`
- dataset_index: `1756`

### Prompt

帮我写一个isQ程序：an isQ BB84 circuit: Alice prepares |+> in X basis, Bob measures in X basis. Expected: deterministic |0> after H.

### Chain-of-thought reasoning

Step 1: In BB84, Alice prepares a qubit in the X basis. The |+> state is H|0> = (|0> + |1>)/sqrt(2). Step 2: Alice applies H to q[0] starting from |0> to create |+>. Step 3: Bob measures in the X basis, which means applying H before computational basis measurement. Step 4: Since H is self-inverse (H^2 = I), applying H twice returns |0> to |0>. Step 5: The probability of measuring |0> is 1.0 and |1> is 0.0, giving expected_probs = [1.0, 0.0].

## isqExpand/front/92

- task_id: `isqExpand/front/92`
- task_type: `output_prediction`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `xx_interaction`, `output_prediction`, `excitation_conservation`, `time_evolution`
- source: `isq_expansion`
- dataset_index: `5380`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;
qbit q[2];

procedure main() {
    // Prepare |10>
    X(q[0]);
    // XX evolution: HH-CNOT-Rz(2t)-CNOT-HH with t=pi/4
    H(q[0]); H(q[1]);
    CNOT(q[0], q[1]);
    Rz(pi/2.0, q[1]);
    CNOT(q[0], q[1]);
    H(q[0]); H(q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
Starting from |00>:
1. X(q[0]): |10>
2. H(q[0]) H(q[1]): transforms to ZZ basis
   |10> -> H|1> x H|0> = (|0>-|1>)/sqrt(2) x (|0>+|1>)/sqrt(2)
   = (1/2)(|00> + |01> - |10> - |11>)
3. CNOT(q[0],q[1]): |00>->|00>, |01>->|01>, |10>->|11>, |11>->|10>
   = (1/2)(|00> + |01> - |11> - |10>)
4. Rz(pi/2, q[1]): Rz|0>=e^{-ipi/4}|0>, Rz|1>=e^{ipi/4}|1>
   = (1/2)(e^{-ipi/4}|00> + e^{ipi/4}|01> - e^{ipi/4}|11> - e^{-ipi/4}|10>)
5. CNOT(q[0],q[1]): undo entanglement
6. H(q[0]) H(q[1]): back to computational basis

The XX interaction on |10> at t=pi/4 gives equal superposition of |01> and |10>.
e^{-i(XX)pi/4}|10> = cos(pi/4)|10> - i sin(pi/4)|01> = (|10> - i|01>)/sqrt(2)
P(|01>) = P(|10>) = 0.5

### Reference answer

{'predicted_probs': {'01': 0.5, '10': 0.5}, 'explanation': 'The XX interaction conserves total excitation number. Starting from |10> (one excitation), the evolution is:\n\ne^{-i(XX)t}|10> = cos(t)|10> - i sin(t)|01>\n\nWith t = pi/4:\n- cos(pi/4) = 1/sqrt(2), so P(|10>) = cos^2(pi/4) = 0.5\n- sin(pi/4) = 1/sqrt(2), so P(|01>) = sin^2(pi/4) = 0.5\n\nAt t = pi/4, the excitation is equally shared between the two qubits. The states |00> and |11> have zero probability because the XX interaction preserves the single-excitation subspace.\n\nExpected: {|01>: 0.5, |10>: 0.5}'}

## isqExpand/front/86

- task_id: `isqExpand/front/86`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `expert`
- concept_tags: `trotter_error`, `bch_formula`, `suzuki_formula`, `simulation_complexity`
- source: `qa_pipeline`
- dataset_index: `2442`

### Prompt

详细分析Trotter分解的误差来源和误差上界。对于一阶和二阶Trotter公式，分别推导单步误差和总误差的阶数。在实际量子模拟中，如何选择Trotter步数n来平衡精度与电路深度？

### Chain-of-thought reasoning

## 推理
目标：推导Trotter误差的数学分析。

关键推导：
1. BCH公式给出误差来源：被忽略的对易子项
2. 一阶：单步O(dt²)，n步总O(t²/n)→n=O(t²/ε)
3. 二阶：对称化消除O(dt²)项→单步O(dt³)→总O(t³/n²)→n=O(t^{3/2}/√ε)
4. 实际中二阶Trotter是精度-深度的甜点

这是理论性较强的概念，需要严谨的数学推导。

### Reference answer

## Trotter误差分析

### 误差来源
Trotter分解的误差来自Baker-Campbell-Hausdorff（BCH）公式。对于两个算符A和B：

e^{A}e^{B} = e^{A+B+[A,B]/2+([A,[A,B]]+[B,[B,A]])/12+...}

被忽略的对易子项构成了近似误差。

### 一阶Trotter误差

**单步误差**：
Δ₁ = ||e^{i(A+B)dt} - e^{iAdt}e^{iBdt}|| = O(||[A,B]||·dt²)

具体地：
e^{iAdt}e^{iBdt} = e^{i(A+B)dt - [A,B]dt²/2 + O(dt³)}

所以单步误差为 ||[A,B]||·dt²/2。

**总误差**（n步）：
Δ_total = n · O(dt²) = n · O(t²/n²) = O(t²||[A,B]||/n)

要达到精度ε：n ≥ t²||[A,B]||/(2ε)，即 n = O(t²/ε)。

### 二阶Trotter（Suzuki）误差

S₂(dt) = e^{iAdt/2}e^{iBdt}e^{iAdt/2}

**单步误差**：
S₂(dt) = e^{i(A+B)dt + O(dt³)}

对称化消除了dt²项（对易子[A,B]项恰好被抵消），首个误差项为：
O(([A,[B,A]]+[B,[A,B]])·dt³/12)

**总误差**：n · O(dt³) = O(t³/n²)

要达到精度ε：n = O(t^{3/2}/√ε)。

### 高阶Suzuki递推
k阶Suzuki公式通过递推构造：
S_{2k}(dt) = [S_{2k-2}(p_k·dt)]² · S_{2k-2}((1-4p_k)·dt) · [S_{2k-2}(p_k·dt)]²
其中 p_k = 1/(4-4^{1/(2k-1)})

总误差为 O(t^{2k+1}/n^{2k})，但电路深度指数增长。

### 实际选择策略

1. **精度-深度权衡**：
   - 高阶Trotter减少步数n，但每步门数增加
   - 实际中二阶Trotter往往是最佳平衡点

2. **经验法则**：
   - NISQ设备：n = O(10-100)，一阶或二阶
   - 容错设备：可用高阶公式

3. **对易子估计**：
   - 如果||[A,B]||较小（近似对易），即使少量步数也能达到高精度
   - Ising模型等局部哈密顿量的对易子范数通常可控

4. **总门数优化**：
   - 一阶：总门数 ∝ n ∝ t²/ε
   - 二阶：总门数 ∝ 5n/2 ∝ t^{3/2}/√ε（虽然每步更多门，但步数更少）

## isqExpand/front/45

- task_id: `isqExpand/front/45`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `difficult`
- concept_tags: `quantum_chemistry`, `jordan_wigner`, `fermion_mapping`
- source: `qa_pipeline`
- dataset_index: `1669`

### Prompt

解释Jordan-Wigner变换在量子化学模拟中的作用。为什么需要将费米子哈密顿量映射到量子比特上？

### Chain-of-thought reasoning

## 推理
JW变换将费米子的产生/湮灭算符映射为Pauli算符加Z串，Z串保证费米子反对易性。映射后的哈密顿量变为Pauli串的线性组合，可以在量子比特上直接实现。缺点是Z串导致非局部性。

### Reference answer

Jordan-Wigner（JW）变换是将费米子系统映射到量子比特系统的标准方法，是量子化学模拟的关键步骤。

**为什么需要映射：**
量子计算机原生操作的是量子比特（qubit），但化学系统由电子（费米子）组成。费米子满足反对易关系{a†ᵢ, aⱼ} = δᵢⱼ，而量子比特满足对易关系。因此需要一个将费米子代数映射到Pauli代数的变换。

**JW变换规则：**
将每个费米轨道对应一个量子比特（|0⟩=空轨道，|1⟩=占据轨道）。产生算符映射为：

a†ⱼ → (Xⱼ - iYⱼ)/2 ⊗ Z_{j-1} ⊗ Z_{j-2} ⊗ ... ⊗ Z₀

长Z-串（Jordan-Wigner string）用于保持费米子的反对易性。当交换两个费米子时，多出的负号通过Z串中的相位体现。

**映射后的哈密顿量：**
分子的二次量子化哈密顿量H = Σ h_pq a†_p a_q + Σ h_pqrs a†_p a†_q a_r a_s 映射后变为Pauli算符的加权和：H = Σ cᵢ Pᵢ，其中Pᵢ是Pauli串（如XZZY, IIXX等）。

**特点：**
- 优点：映射直观，保持粒子数守恒。
- 缺点：Z串使得非局部相互作用需要O(n)个量子门，n为轨道数。
- 替代方案：Bravyi-Kitaev变换可以将操作的局部性从O(n)改善到O(log n)。
