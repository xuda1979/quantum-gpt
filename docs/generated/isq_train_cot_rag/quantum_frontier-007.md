# ISQ training COT RAG corpus: quantum_frontier shard 7

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/front/109

- task_id: `isqExpand/front/109`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `expert`
- concept_tags: `approximate_counting`, `grover_operator`, `phase_estimation`, `quadratic_speedup`
- source: `qa_pipeline`
- dataset_index: `2782`

### Prompt

量子近似计数（Quantum Approximate Counting）是Grover搜索算法的一个重要推广。请解释量子近似计数的原理：如何利用量子相位估计（QPE）结合Grover算子来估计搜索空间中满足条件的解的数量M，并分析其相对于经典穷举计数的复杂度优势。

### Chain-of-thought reasoning

## 推理
目标：解释量子近似计数算法。

核心链条：
1. Grover算子G有特征值e^{±2iθ}，其中sin²(θ)=M/N
2. 用QPE估计θ，从而推出M=N·sin²(θ)
3. QPE用t个辅助qubit估计相位到2^{-t}精度

复杂度分析：
- QPE需要O(2^t)次受控G操作
- 每次G操作需O(1)次oracle查询
- 要达到ε相对精度需2^t ~ √(N/M)/ε
- 总查询复杂度O(√(N/M)/ε)，比经典O(N/M/ε²)快二次

### Reference answer

## 量子近似计数

### 问题描述
给定一个N元素的搜索空间和一个布尔函数f(x)，其中恰好有M个解满足f(x)=1。经典计算需要O(N)次查询才能精确计数。量子近似计数可以用O(√(N/M))次查询估计M。

### 核心原理

量子近似计数将量子相位估计（QPE）应用于Grover迭代算子G：

G = (2|ψ⟩⟨ψ| - I) · O_f

其中|ψ⟩是均匀叠加态，O_f是oracle。

### Grover算子的特征值

Grover算子G在由解态|α⟩和非解态|β⟩张成的二维子空间中的特征值为：

e^{±2iθ}, 其中 sin²(θ) = M/N

因此：θ = arcsin(√(M/N))

### 算法步骤

1. **初始化**：准备均匀叠加态|ψ⟩ = H^⊗n|0⟩
2. **QPE应用**：对Grover算子G执行相位估计，获得相位θ的近似值θ̃
3. **计算M**：从估计的相位反推 M̃ = N·sin²(θ̃)

### 精度分析

使用t个辅助qubit的QPE可以估计θ到2^{-t}精度。
对M的相对误差约为 ΔM/M ~ 1/√M · 2^{-t}

### 复杂度比较

| 方法 | 查询复杂度 | 精度 |
|------|----------|------|
| 经典穷举 | O(N) | 精确 |
| 经典采样估计 | O(N/M · 1/ε²) | ε相对误差 |
| 量子近似计数 | O(√(N/M) · 1/ε) | ε相对误差 |

量子近似计数实现了相对于经典方法的**二次加速**。

### 应用场景

- 数据库中满足条件的记录计数
- 组合优化中解空间大小估计
- 密码分析中的密钥空间估计
- 作为自适应Grover搜索的子程序（不知道M时先估计M）

## isqExpand/front/96

- task_id: `isqExpand/front/96`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `qaoa`, `max_cut`, `superposition`, `phase_manipulation`
- source: `isq_expansion`
- dataset_index: `860`

### Prompt

实现以下量子计算任务（使用isQ）：implementing a 1-layer QAOA circuit for the Max-Cut problem on a 2-node graph with a single edge. Use gamma = pi/3 for the cost layer and beta = pi/6 for the mixer layer.

The QAOA circuit structure is:
1. Initialize all qubits in the |+> state using Hadamard gates.
2. Cost layer: Apply the ZZ interaction e^{-i*gamma*Z_0*Z_1} decomposed as CNOT(q[0],q[1]) -> Rz(2*gamma, q[1]) -> CNOT(q[0],q[1]).
3. Mixer layer: Apply Rx(2*beta) to each qubit.
4. Measure all qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: 1-layer QAOA for Max-Cut on edge (0,1).

Cost Hamiltonian: H_C = Z_0 Z_1. The Max-Cut objective for a single edge is C = (1 - Z_0 Z_1)/2, which is maximized by anti-aligned states |01> and |10>.

Circuit:
1. H on both qubits: |+> = (|0>+|1>)/sqrt(2) each => uniform superposition |00>+|01>+|10>+|11> (all amplitude 1/2).
2. Cost unitary e^{-i*gamma*Z0Z1}: CNOT(0,1) maps Z0Z1 to Z1 in the CNOT basis. Then Rz(2*gamma, q[1]) applies e^{-i*gamma*Z1}. Second CNOT undoes the basis change.
3. Mixer unitary e^{-i*beta*sum(Xi)}: Rx(2*beta) on each qubit.

With gamma=pi/3, beta=pi/6:
- The ZZ interaction creates phase differences between same-parity (|00>,|11>) and opposite-parity (|01>,|10>) states.
- The Rx mixer then converts some phase information to amplitude.
- Result: P(|00>)=P(|11>)=0.4375, P(|01>)=P(|10>)=0.0625.

## isqExpand/front/146

- task_id: `isqExpand/front/146`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `BB84协议`, `量子密钥分发`, `拦截重发攻击`, `量子比特误码率`, `不可克隆定理`
- source: `qa_pipeline`
- dataset_index: `5148`

### Prompt

BB84协议中，如果Eve使用拦截-重发攻击，Alice和Bob如何通过误码率检测窃听？

### Chain-of-thought reasoning

首先分析BB84协议的基本流程：Alice在Z基和X基中随机选择制备量子比特发送给Bob，Bob随机选择测量基进行测量。然后分析Eve的拦截-重发策略：Eve拦截每个量子比特，随机选基测量后再发送给Bob。关键在于计算Eve引入的误码率——当Eve选错基（50%概率）时，量子态被错误坍缩，即使Bob后来选对了与Alice相同的基，也有50%概率得到错误结果，因此总体误码率约为25%。最后说明Alice和Bob通过公开比对部分筛选密钥来统计误码率，若超过阈值则判定有窃听。这体现了量子测量对态的不可逆干扰，是量子密钥分发安全性的核心基础。

### Reference answer

在BB84协议中，Alice和Bob通过以下步骤利用误码率（QBER）检测Eve的拦截-重发攻击：

**1. 拦截-重发攻击的原理：**
Eve对传输中的每一个量子比特进行拦截，随机选择一组测量基（Z基或X基）进行测量，然后根据测量结果向Bob发送一个新的量子比特。

**2. 误码产生的机制：**
- Eve有50%的概率选择了与Alice相同的制备基，此时测量不引入干扰，Bob正确接收。
- Eve有50%的概率选择了与Alice不同的基，此时Eve的测量会使量子态坍缩到错误的基上。在Bob正确选择与Alice相同基的情况下（即筛选密钥中），Bob的测量结果有50%的概率与Alice不同。
- 因此，在筛选密钥中，Eve引入的误码率为：50%（Eve选错基）× 50%（Bob结果错误）= 25%。

**3. 检测步骤：**
- Alice和Bob先通过公开信道比对各自使用的测量基，丢弃基不一致的比特，得到筛选密钥（sifted key）。
- 他们随机选取筛选密钥的一部分进行公开比对，计算误码率。
- 如果误码率显著高于预期（如超过约11%的安全阈值，理论阈值因协议变体而异），则判定存在窃听，丢弃本次密钥并重新开始。
- 如果误码率在可接受范围内，则对剩余比特进行纠错和隐私放大，得到最终安全密钥。

**4. 核心物理原理：**
这一检测机制基于量子力学的不可克隆定理和测量塌缩特性。Eve的任何测量行为都会不可避免地干扰量子态，从而在Alice和Bob的密钥比对中留下痕迹。即使Eve只拦截部分量子比特，也会以相应比例提高误码率，使窃听可被检测。

## isqExpand/front/37

- task_id: `isqExpand/front/37`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `difficult`
- concept_tags: `hamiltonian_simulation`, `trotter_decomposition`, `ising_model`
- source: `isq_expansion`
- dataset_index: `4607`

### Prompt

请用isQ语言编写一个量子电路：implements a single first-order Trotter step for a 2-qubit Ising model.

The Ising Hamiltonian is H = J*Z₀Z₁ + h*(X₀ + X₁). A single Trotter step approximates e^{-iHt} as e^{-iJZ₀Z₁t} * e^{-ihX₀t} * e^{-ihX₁t}.

- e^{-iJZZt} is implemented as: CNOT(q[0],q[1]), Rz(2*J*t, q[1]), CNOT(q[0],q[1]).
- e^{-ihXt} = Rx(2*h*t, q).

Use J=1, h=0.5, t=pi/4.

Requirements:
- Declare global `qbit q[2];`
- Start from |00⟩.
- Apply one Trotter step.
- Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. The ZZ interaction is decomposed as CNOT-Rz-CNOT with angle 2*J*t = 2*1*pi/4 = pi/2.
2. The X field terms become Rx(2*h*t) = Rx(2*0.5*pi/4) = Rx(pi/4) on each qubit.
3. Starting from |00⟩, the ZZ term applies a phase (Rz(pi/2) on q[1] in the CNOT basis), then Rx rotations create superpositions.

## isqExpand/front/88

- task_id: `isqExpand/front/88`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `trotter_decomposition`, `suzuki_formula`, `second_order`, `ising_model`
- source: `isq_expansion`
- dataset_index: `790`

### Prompt

Implement a quantum circuit in isQ: implements a second-order (symmetric) Trotter step for the 2-qubit Ising Hamiltonian H = Z0*Z1 + X0 + X1 with time t = pi/4.

The second-order Suzuki formula is:
S2(t) = e^{-i(X0+X1)t/2} * e^{-i(Z0Z1)t} * e^{-i(X0+X1)t/2}

This symmetric decomposition achieves O(t^3) single-step error instead of O(t^2) for first-order.

Circuit implementation:
- Half-step X rotations: Rx(pi/4.0, q[0]), Rx(pi/4.0, q[1]).
- Full-step ZZ interaction: CNOT(q[0],q[1]), Rz(pi/2.0, q[1]), CNOT(q[0],q[1]).
- Half-step X rotations again: Rx(pi/4.0, q[0]), Rx(pi/4.0, q[1]).

Requirements:
- Declare global `qbit q[2];`
- Start from |00>.
- Apply the symmetric Trotter step as described.
- Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement second-order Trotter for H = ZZ + X0 + X1, t = pi/4.

S2(t) = e^{-i(X)t/2} e^{-i(ZZ)t} e^{-i(X)t/2}

From |00>:
1. First half-step: Rx(pi/4) on each qubit (half the full rotation angle).
2. Full ZZ step: CNOT-Rz(pi/2)-CNOT.
3. Second half-step: Rx(pi/4) on each qubit.

The symmetric structure cancels the leading-order error term (the [A,B] commutator), achieving O(dt^3) accuracy per step instead of O(dt^2).

Computed probabilities: |00>: 0.625, |01>: 0.125, |10>: 0.125, |11>: 0.125.

## isqExpand/front/36

- task_id: `isqExpand/front/36`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `difficult`
- concept_tags: `hamiltonian_simulation`, `trotter_decomposition`, `product_formula`
- source: `qa_pipeline`
- dataset_index: `3395`

### Prompt

详细解释Trotter-Suzuki分解在哈密顿量模拟中的原理和应用。一阶和二阶Trotter公式有什么区别？

### Chain-of-thought reasoning

## 推理
Trotter分解将非对易哈密顿量的指数分解为对易部分的乘积序列。一阶公式简单但误差大，二阶通过对称化降低误差阶。在实际量子电路中，每个小步被翻译为一组旋转门和纠缠门。

### Reference answer

Trotter-Suzuki分解是将复杂哈密顿量的时间演化算符分解为简单项的乘积的方法。

**基本问题：**
给定H = H₁ + H₂ + ... + H_L，我们需要实现e^{-iHt}。由于[H_j, H_k] ≠ 0（哈密顿量的各项一般不对易），e^{-i(H₁+H₂)t} ≠ e^{-iH₁t}e^{-iH₂t}。

**一阶Trotter公式：**
e^{-iHt} ≈ (e^{-iH₁t/n} e^{-iH₂t/n} ... e^{-iH_Lt/n})^n

将时间t分为n个小步，在每个步长内近似各项可以独立演化。误差为O(t²L²/n)，即O(1/n)。

**二阶Trotter公式（Suzuki公式）：**
e^{-iHt} ≈ (e^{-iH₁t/2n} e^{-iH₂t/2n} ... e^{-iH_Lt/n} ... e^{-iH₂t/2n} e^{-iH₁t/2n})^n

通过对称排列消除一阶误差项，误差降为O(t³L³/n²)，即O(1/n²)。

**对比：**
- 一阶：每步需L个酉变换，误差O(1/n)。
- 二阶：每步需2L-1个酉变换，误差O(1/n²)。
- 总门数：要达到误差ε，一阶需O(L²t²/ε)步，二阶需O(L^{3/2}t^{3/2}/ε^{1/2})步。

**实践意义：**
Trotter分解直观且易于实现，是NISQ设备上哈密顿量模拟的首选方法。对于局部哈密顿量（如自旋链），每个e^{-iH_jt/n}只涉及少数量子比特，可以高效地用基本量子门实现。

## isqExpand/front/28

- task_id: `isqExpand/front/28`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `quantum_ml`, `quantum_classifier`, `variational`
- source: `isq_expansion`
- dataset_index: `4279`

### Prompt

Implement the following in isQ: implements a quantum classifier circuit for a simple 2-class problem.

The circuit uses:
1. Data encoding: Rx rotations to encode 2 features.
2. Variational layer: Ry rotations as trainable parameters.
3. Entangling: CNOT gate.
4. Measurement of q[0] determines the class.

Use feature values x0=pi/2, x1=pi and trained parameters theta0=pi/4, theta1=pi/3.

Requirements:
- Declare global `qbit q[2];`
- Apply Rx(pi/2.0, q[0]), Rx(pi, q[1]) for encoding.
- Apply Ry(pi/4.0, q[0]), Ry(pi/3.0, q[1]) for variational layer.
- Apply CNOT(q[0], q[1]).
- Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
The circuit encodes classical data using Rx rotations, applies trainable Ry rotations, and entangles with CNOT. The measurement of q[0] serves as the classification output. The probability of measuring |0⟩ on q[0] corresponds to class 0, and |1⟩ to class 1. The exact probabilities depend on the interplay of all rotations and the entanglement.

## isqExpand/front/9

- task_id: `isqExpand/front/9`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `difficult`
- concept_tags: `error_correction`, `surface_code`, `topological_code`
- source: `isq_expansion_qa`
- dataset_index: `2877`

### Prompt

解释表面码（surface code）的基本概念。为什么它被认为是最有前景的量子纠错方案之一？

### Chain-of-thought reasoning

## 推理
表面码在二维网格上定义，使用两种稳定子——面算符(X型)和顶点算符(Z型)——分别检测不同类型的错误。其优势在于：约1%的高容错阈值、仅需最近邻相互作用的物理可实现性、以及成熟的解码算法。这些特点使它成为超导量子计算平台上最实际的纠错方案。

### Reference answer

表面码是一种拓扑量子纠错码，其物理量子比特排列在二维网格上。它有两种类型的稳定子算符：

1. X-plaquette稳定子：作用于每个面（plaquette）的四个边上的量子比特，用XXXX算符检测Z错误。
2. Z-star稳定子：作用于每个顶点（vertex）周围的四个量子比特，用ZZZZ算符检测X错误。

表面码被认为最有前景的原因包括：

1. 高容错阈值：错误阈值约为1%，这是所有已知量子纠错码中最高的之一。当物理错误率低于此阈值时，增加码距可指数级降低逻辑错误率。

2. 局部操作：所有稳定子测量只涉及相邻量子比特，适合二维芯片布局，与超导量子比特等硬件平台高度兼容。

3. 可扩展性：码距d的表面码需要O(d²)个物理量子比特，通过增大d即可提高保护能力。

4. 成熟的解码算法：最小权重完美匹配（MWPM）等高效解码算法已被广泛研究。

主要挑战在于：逻辑门操作（特别是非Clifford门如T门）需要复杂的魔法态蒸馏技术，增加了资源开销。

## isqExpand/front/95

- task_id: `isqExpand/front/95`
- task_type: `bug_fix`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `zz_decomposition`, `missing_gate`, `bug_fix`, `entanglement`
- source: `isq_expansion`
- dataset_index: `5687`

### Prompt

这段isQ代码有bug，帮我找出并修复：

```isq
import std;
qbit q[2];

procedure main() {
    // Prepare |++>
    H(q[0]); H(q[1]);
    // ZZ evolution (BUG: missing second CNOT)
    CNOT(q[0], q[1]);
    Rz(pi/2.0, q[1]);
    // Decode
    H(q[0]); H(q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Bug Analysis
The ZZ decomposition requires two CNOTs sandwiching an Rz: CNOT-Rz-CNOT.

The first CNOT maps the computational basis parity onto q[1]: |ab> -> |a, a XOR b>.
The Rz then applies a phase depending on a XOR b (which encodes the ZZ eigenvalue).
The second CNOT is essential to uncompute the XOR and restore the original basis.

Without the second CNOT:
- The state remains entangled in a way that does not correspond to ZZ evolution.
- |++> -> after CNOT becomes (|00>+|11>)/sqrt(2) (Bell state), Rz adds phases, then HH decoding gives wrong probabilities.
- Buggy: [0.5, 0.5, 0.0, 0.0]
- Correct: [0.5, 0.0, 0.0, 0.5]

The correlated phase from ZZ should give |00> and |11> after HH decoding, but the bug breaks this correlation.

Fix: Add CNOT(q[0], q[1]) after the Rz and before the H gates.

## isqExpand/front/105

- task_id: `isqExpand/front/105`
- task_type: `bug_fix`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `qaoa`, `phase_manipulation`, `entanglement`
- source: `isq_expansion`
- dataset_index: `5514`

### Prompt

The following isQ code has a bug. Find and fix it.

Buggy code:
```isq
import std;
qbit q[2];

procedure main() {
    H(q[0]); H(q[1]);
    // Cost layer: ZZ interaction
    CNOT(q[0], q[1]);
    Rz(2.0*pi/3.0, q[0]);  // BUG: should be q[1]
    CNOT(q[0], q[1]);
    // Mixer layer
    Rx(2.0*pi/3.0, q[0]);
    Rx(2.0*pi/3.0, q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Bug Analysis
In the CNOT-Rz-CNOT decomposition of e^{-i*gamma*Z0Z1}:
- CNOT(0,1) maps the parity information into q[1]
- Rz must act on q[1] (the target qubit that carries the parity)
- Applying Rz to q[0] (the control) instead produces a different unitary

With Rz on q[0]:
CNOT * (Rz(q0) ⊗ I) * CNOT = e^{-i*gamma*Z0} (single-qubit Z rotation, not ZZ)
This loses the two-body interaction entirely.

Buggy output: [0.4375, 0.4375, 0.0625, 0.0625]
Correct output: [0.0625, 0.4375, 0.4375, 0.0625]

Fix: Change Rz(2.0*pi/3.0, q[0]) to Rz(2.0*pi/3.0, q[1]).
