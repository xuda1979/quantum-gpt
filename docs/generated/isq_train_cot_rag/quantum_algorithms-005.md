# ISQ training COT RAG corpus: quantum_algorithms shard 5

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3804

- task_id: `isqTrain/3804`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `interference`, `isq_syntax_oracle`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `5233`

### Prompt

请用isQ语言编写一个量子电路：4-bit Bernstein-Vazirani to find secret s=1001. Use oracle keyword, for loops for Hadamard. Measure all 5 qubits.

### Chain-of-thought reasoning

## Reasoning
1.  **Goal:** Implement the Bernstein-Vazirani algorithm to find the 4-bit secret string $s=1001$.
2.  **Qubits:** Uses 5 qubits (4 input qubits $q[0..3]$ and 1 ancilla $q[4]$); all 5 are measured.
3.  **Initialization:** The ancilla $q[4]$ is flipped to $|1\rangle$ and put into the $|-\rangle$ state by $X$ and $H$ gates, while the input qubits $q[0..3]$ start in $|0\rangle$.
4.  **Superposition:** Applying $H$ to $q[0..3]$ puts them into an equal superposition of all 4-bit states, yielding the global state $\frac{1}{4} \sum_{x=0}^{15} |x\rangle |-\rangle$.
5.  **Oracle Application:** The oracle $f(x) = x \cdot s \pmod 2$ applies a phase kickback of $(-1)^{f(x)}$ to the input qubits because the ancilla is in $|-\rangle$, resulting in the state $\frac{1}{4} \sum_{x} (-1)^{x \cdot 1001} |x\rangle |-\rangle$.
6.  **Interference:** Applying $H$ gates to $q[0..3]$ cancels out the superposition, uniquely revealing the secret string in the input qubits: $|1001\rangle |-\rangle$.
7.  **Measurement:** The final measurement yields the bitstring $|10010\rangle$ with probability 0.5 (if $q[4]$ collapses to $|0\rangle$) or $|10011\rangle$ with probability 0.5 (if $q[4]$ collapses to $|1\rangle$).

## isqExpand/qa/42

- task_id: `isqExpand/qa/42`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `Grover算法`, `自适应搜索`, `迭代次数`, `量子优化`, `未知解数量`, `量子 oracle`
- source: `qa_pipeline`
- dataset_index: `61`

### Prompt

什么是Grover自适应搜索（adaptive Grover search）？当解的数量未知时如何确定迭代次数？

### Chain-of-thought reasoning

## 推理
1. 分析题目意图：题目要求解释什么是Grover自适应搜索，并阐述在解的数量未知时，该算法是如何确定迭代次数的。
2. 概念解析：传统Grover算法依赖于精确的迭代次数 $\pi/4 \sqrt{N/M}$，解的数量 $M$ 未知容易导致过度或不足迭代。Grover自适应搜索（特别是Boyer等人的变体）是为了克服这一问题。
3. 组织答案：先定义Grover自适应搜索的背景和目的；接着详述未知解数量时的迭代策略（如随机选取结合指数级增加上界）；然后补充该算法在优化问题中的应用逻辑；最后通过isQ代码展示动态改变迭代次数的量子电路结构。
4. 编写isQ代码：编写一个包含两量子比特的简单Grover迭代模块，使用经典for循环模拟自适应搜索中迭代次数成倍增加的过程。

### Reference answer

Grover自适应搜索是为了解决传统Grover算法在实际应用中面临的一个核心痛点而提出的改进算法。传统Grover算法要求预先知道目标解的数量 $M$，以便精确计算出最佳的酉算子迭代次数 $k^* \approx \frac{\pi}{4} \sqrt{N/M}$（其中 $N$ 为搜索空间大小）。如果解的数量未知，迭代次数偏离最佳值会导致测量得到正确解的概率大幅下降，甚至出现“过度旋转”使得概率归零。Grover自适应搜索通过动态调整迭代策略，使得在 $M$ 未知的情况下依然能够高效地找到目标解。

当解的数量 $M$ 未知时，确定迭代次数的核心思想是“指数级增加搜索步数并结合随机性”。最著名的策略由Boyer等人提出，其具体步骤如下：
1. 设定一个初始的最大迭代次数上界，通常取较小的值，如 $m = 1$。
2. 从区间 $[0, m]$ 中均匀随机选择一个整数 $k$ 作为当前Grover算法的迭代次数。
3. 执行进行了 $k$ 次迭代的Grover算子 $G^k$，并对系统的量子态进行测量。
4. 检验测量结果是否满足目标条件（即是否为寻找的解）。
5. 如果测量结果满足条件，说明已经找到目标，算法结束；如果未找到目标，则将最大迭代上界扩大，通常设为 $m = \lambda m$（其中 $\lambda$ 是一个大于1的常数，常取 $\lambda = 2$），然后返回第2步继续执行。

通过这种启发式方法，算法能够以极高的概率在对数级别的时间内逼近最优迭代次数。这种方法不仅保留了对经典遍历算法的二次加速优势，其期望时间复杂度依然保持在 $O(\sqrt{N/M})$ 量级。

在实际的量子组合优化问题（如寻找极值）中，Grover自适应搜索常用于动态优化阈值：每次找到更优解后，将此解作为新的判定阈值更新Oracle，不断缩小目标解空间，直到无法找到更优的解为止。

以下是一个使用isQ代码实现Grover自适应搜索框架的示例。代码展示了一个在未知解数量时，通过经典控制循环不断翻倍最大迭代次数，并在量子电路上动态执行相应次数的Grover迭代的过程：

import std;
qbit q[2];

// 定义一个Oracle，假设搜索目标态为|11>
procedure oracle() {
    CZ(q[0], q[1]);
}

// 定义Diffusion算子（振幅放大）
procedure diffusion() {
    H(q[0]);
    H(q[1]);
    X(q[0]);
    X(q[1]);
    H(q[1]);
    CNOT(q[0], q[1]);
    H(q[1]);
    X(q[0]);
    X(q[1]);
    H(q[0]);
    H(q[1]);
}

// 封装单次Grover迭代
procedure grover_iter() {
    oracle();
    diffusion();
}

procedure main() {
    int max_iters = 1;
    
    // 模拟自适应迭代过程（最多尝试4个Phase）
    for (int phase = 0; phase < 4; phase = phase + 1) {
        // 每次重新初始化为均匀叠加态
        H(q[0]);
        H(q[1]);

        // 动态执行 max_iters 次 Grover 迭代
        for (int i = 0; i < max_iters; i = i + 1) {
            grover_iter();
        }

        // 测量量子比特
        int res0 = M(q[0]);
        int res1 = M(q[1]);

        // 在真实自适应搜索中，这里会验证结果是否为解
        // 若是解，则跳出循环；若不是，则增加迭代次数并重试
        // 这里省略具体的量子态重置与条件判断逻辑
        
        // 若未找到解，指数级增加迭代次数上界
        max_iters = max_iters * 2;
    }
}

## isqQA/quantum_algorithms/105_optimization_variant

- task_id: `isqQA/quantum_algorithms/105_optimization_variant`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `optimization_variant`, `algorithm`, `Shor算法中的模幂运算`
- source: `qa_pipeline`
- dataset_index: `2779`

### Prompt

在Shor算法中，模幂运算（$a^x \bmod N$）的量子线路实现是整个算法资源消耗的核心瓶颈。近年来，针对该运算有哪些重要的优化变体？请深入探讨基于量子傅里叶变换（QFT）算术的模乘优化策略（如Beauregard方案），并使用isQ语言展示一个基于QFT的受控相位加法器核心代码片段，以此解释其优化原理。

### Reference answer

<thought>
在Shor算法中，模幂运算的经典实现需要大量的辅助比特和深度的加法器网络。Beauregard等人的优化变体巧妙地利用了量子傅里叶变换（QFT）的对数加法特性。在傅里叶基下，两个量子寄存器的加法可以被分解为一系列单比特的受控相位旋转，这极大地减少了量子线路中昂贵的多控Toffoli门数量，使得模幂运算的深度和辅助比特需求显著降低。

数学推导：
假设寄存器B处于量子态 $|\psi\rangle = \sum_j y_j |j\rangle$。对其施加QFT后，状态变为 $|\phi\rangle = \sum_k \tilde{y}_k |k\rangle$。
在傅里叶基下，加上一个常数 $c$ 的操作不改变基态 $|k\rangle$ 的概率幅分布，只引入相对相位：
$|k\rangle \rightarrow e^{2\pi i c k / 2^n} |k\rangle$
这个操作可以通过对每一个量子比特施加 $R_z$ 旋转门来实现。
若该加法受控于控制比特 $ctrl$，则在isQ中可以直接使用 `ctrl @[ctrl] Rz(...)` 语法，这使得原本复杂的进位传播网络被极度简化为不交错的相位门。

isQ代码设计：
1. 全局声明控制比特和目标寄存器。
2. 编写受控常量加法器，在QFT基下工作。
3. 通过循环和受控 $R_z$ 门实现相位累加，避开传统的进位线路。
</thought>
在Shor算法中，模幂运算（$a^x \bmod N$）的实现复杂度直接决定了算法的实用性与可扩展性。传统的基于进位传播的算术逻辑（如Vedral、Barenco等人的早期方案）需要构建庞大的模加法、模乘法和条件移位网络，不仅线路深度高达 $O(n^3)$，还需要大量的辅助量子比特用于存储中间进位。

针对这一瓶颈，最重要的优化变体之一是**基于量子傅里叶变换（QFT）的算术逻辑设计**（以Stephane Beauregard在2003年提出的方案为代表）。该变体的核心优化原理在于改变了量子态的计算基：
1. **相位的算术化**：在傅里叶基下，算术加法操作被映射为单比特的相位旋转。具体而言，若对寄存器应用QFT后，加上一个经典常数 $c$ 只需对每一位施加 $R_z(2\pi c / 2^k)$ 的旋转门，完全消除了经典不可逆计算中的进位链条（Carry Ripple）。
2. **受控操作的降维**：模幂运算需要根据指数寄存器的比特决定是否执行模乘。在传统基下，这需要构建庞大的受控模乘网络；而在QFT算术变体中，受控模乘被分解为受控相位旋转，这使得控制逻辑可以直接作用于旋转门，将 $O(n^2)$ 的Toffoli门开销降至 $O(n)$ 的受控单比特门，大幅降低了量子体积需求。

以下代码展示了Beauregard变体中的核心单元——**受控QFT加法器**。它演示了在控制比特作用下，将常数 $c$ 加到已处于傅里叶基的量子寄存器上：

```isq
import std;

// 声明全局变量
qbit ctrl[1];
qbit reg_b[4]; // 假设为4位目标寄存器，处于QFT基态

// 受控常量加法器（在QFT域中执行）
procedure c_add_constant_in_qft(int c) {
    // 在傅里叶基下，加常数 c 等价于对每一位施加相对相位旋转
    // 相位角度取决于 c 的二进制表示和当前比特的位置
    // 为演示核心逻辑，假设在此处 c 的某些位为1，进行相应的相位旋转
    for k in 0:4 {
        // 提取常数 c 的第 j 位是否为1，计算对应的相位角
        // 假设常数 c 使得第 k 位需要的旋转角度为 theta_k = 2*pi*c/2^(k+1)
        double theta = 2.0 * 3.141592653589793 * c / (1 << (k + 1));
        
        // 优化核心：直接使用控制相位门，无需任何进位辅助比特
        // 受 ctrl 控制，对 reg_b[k] 施加旋转
        ctrl @[ctrl[0]] Rz(theta, reg_b[k]);
    }
}

procedure main() {
    // 初始化寄存器状态（省略了前置的QFT变换）
    H(ctrl[0]);
    for i in 0:4 {
        H(reg_b[i]);
    }
    
    // 执行受控加法：如果 ctrl 为 |1>，则在 QFT 基下将常数 5 加到 reg_b
    c_add_constant_in_qft(5);
    
    // 随后可通过逆QFT(IQFT)将结果变回计算基进行测量
}
```

除了Beauregard的QFT变体，另一个重要的改进方向是**近似量子傅里叶变换（AQFT）**的应用。由于模幂运算的线路中，随着旋转角度指数级减小（如 $R_z(2\pi/2^k)$ 当 $k$ 较大时），对应的物理门极容易受到噪声干扰且对最终概率幅的贡献极小。通过截断这些微小的旋转角，可以在仅引入极小误差的情况下，将Shor算法的资源开销进一步压缩至 $O(n \log n)$ 级别，这是通向容错量子计算的关键优化路径。

## isqTrain/3535

- task_id: `isqTrain/3535`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `5718`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```
import std;

qbit q[2];

procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);

    Z(q[0]);
    X(q[0]);

    CNOT(q[0], q[1]);
    H(q[0]);

    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the isQ program:**
    *   `qbit q[2];`: 2-qubit register, initial state $|00\rangle$.
    *   `H(q[0]);`: Apply H to q[0]. State becomes $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$.
    *   `CNOT(q[0], q[1]);`: Apply CNOT with q[0] as control, q[1] as target. State becomes $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$ (Bell state).
    *   `Z(q[0]);`: Apply Z to q[0]. $Z|0\rangle = |0\rangle$, $Z|1\rangle = -|1\rangle$. State becomes $\frac{1}{\sqrt{2}}(|00\rangle - |11\rangle)$.
    *   `X(q[0]);`: Apply X to q[0]. $X|0\rangle = |1\rangle$, $X|1\rangle = |0\rangle$. State becomes $\frac{1}{\sqrt{2}}(|10\rangle - |01\rangle)$.
    *   `CNOT(q[0], q[1]);`: Apply CNOT(q[0], q[1]). $|10\rangle \to |11\rangle$, $|01\rangle \to |01\rangle$. State becomes $\frac{1}{\sqrt{2}}(|11\rangle - |01\rangle)$.
    *   `H(q[0]);`: Apply H to q[0].
        *   $H|11\rangle = \frac{1}{\sqrt{2}}(|01\rangle - |11\rangle)$
        *   $H|01\rangle = \frac{1}{\sqrt{2}}(|01\rangle + |11\rangle)$
        *   Total state: $\frac{1}{\sqrt{2}} \left( \frac{1}{\sqrt{2}}(|01\rangle - |11\rangle) - \frac{1}{\sqrt{2}}(|01\rangle + |11\rangle) \right) = \frac{1}{2} (|01\rangle - |11\rangle - |01\rangle - |11\rangle) = \frac{1}{2} (-2|11\rangle) = -|11\rangle$.
    *   Wait, let me double check the H application on q[0].
        *   Current state: $\frac{1}{\sqrt{2}}(|1\rangle - |0\rangle) \otimes |1\rangle$ (qubit order q[0], q[1]).
        *   Let's re-evaluate:
        *   $H|0\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$
        *   $H|1\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$
        *   State is $\frac{1}{\sqrt{2}}(|11\rangle - |01\rangle)$. Here q[0] is the first bit, q[1] is the second bit. No, wait.
        *   If $q[0]q[1]$ is $|11\rangle$, $q[0]=1, q[1]=1$.
        *   So the state is $\frac{1}{\sqrt{2}}(|1\rangle \otimes |1\rangle - |0\rangle \otimes |1\rangle)$.
        *   Apply H to q[0]:
        *   $|1\rangle \otimes |1\rangle \to H|1\rangle \otimes |1\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) \otimes |1\rangle$.
        *   $|0\rangle \otimes |1\rangle \to H|0\rangle \otimes |1\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes |1\rangle$.
        *   Total state: $\frac{1}{2} ((|0\rangle - |1\rangle) - (|0\rangle + |1\rangle)) \otimes |1\rangle = \frac{1}{2} (-2|1\rangle) \otimes |1\rangle = -|11\rangle$.
        *   Yes, the state is exactly $-|11\rangle$ (global phase ignored is just $|11\rangle$).
    *

### Reference answer

{'predicted_probs': {'11': 1.0}, 'explanation': 'The output is |11> with probability 1.0'}

## isqTrain/3714

- task_id: `isqTrain/3714`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `2047`

### Prompt

请用isQ语言编写一个量子电路：QAOA (p=1) for the MaxCut problem on a 3-node path graph with edges [(0, 1), (1, 2)]. Use parameters gamma=0.500 and beta=0.500. The circuit:
1. Initialize all qubits in superposition
2. Apply cost unitary: for each edge, use CNOT-Rz-CNOT
3. Apply mixer: Rx(2*beta) on each qubit
4. Measure all 3 qubits

### Chain-of-thought reasoning

## Reasoning
**Goal:** Implement QAOA p=1 for MaxCut on a 3-node path graph to find bipartitions maximizing cut edges.

**Qubits:** 3 qubits (q[0], q[1], q[2]), all measured.

**State evolution:**
1. **Init:** |000⟩
2. **Hadamards:** |+++⟩ = (1/√8)Σₓ |x⟩ (equal superposition over all 8 basis states)
3. **Cost edge (0,1):** CNOT-Rz(1.0)-CNOT → applies phase e^(-iγZ₀Z₁) with γ=0.5. States where q₀⊕q₁=1 get relative phase e^(-i).
4. **Cost edge (1,2):** CNOT-Rz(1.0)-CNOT → applies phase e^(-iγZ₁Z₂). States where q₁⊕q₂=1 get additional phase e^(-i).
5. **Mixer Rx(1.0):** Rotates each qubit around X-axis, mixing |0⟩↔|1⟩ amplitudes on each qubit.
6. **Final state:** Interference from cost+mixer favors |000⟩ and |111⟩ (~0.335 each), while MaxCut-optimal states |010⟩, |101⟩ get

## isqTrain/886

- task_id: `isqTrain/886`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4771`

### Prompt

实现以下量子计算任务（使用isQ）：implements a variant of the phase_oracle pattern using q[2] -> q[3]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a phase oracle using controlled-Z to flip phase of |11⟩ on q[0],q[1], with q[2] as an expanded register qubit.
2. **Qubits**: 3 qubits (q[0], q[1], q[2]); all measured at the end.
3. **State evolution**:
   - Start: |000⟩
   - H(q[0]): (|000⟩ + |100⟩)/√2
   - H(q[1]): (|000⟩ + |010⟩ + |100⟩ + |110⟩)/2
   - CZ(q[0]→q[1]): (|000⟩ + |010⟩ + |100⟩ - |110⟩)/2
4. **Probabilities**: Phase on |110⟩ is invisible to measurement; all four basis states have |amplitude|² = 1/4, yielding uniform distribution {000: 0.25, 010: 0.25, 100: 0.25, 110: 0.25}.

## isqQA/quantum_algorithms/95_application_scenario

- task_id: `isqQA/quantum_algorithms/95_application_scenario`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `application_scenario`, `algorithm`, `Grover算法的Oracle设计`
- source: `qa_pipeline`
- dataset_index: `5511`

### Prompt

Grover算法因其能够在无序数据库中实现二次加速而闻名，但其真正的应用前景往往体现在解决组合优化或密码分析等实际复杂问题中。在这些实际应用场景下，Grover算法的核心难点在于如何将具体的业务逻辑转化为量子Oracle。请详细阐述Grover算法Oracle在实际应用中的设计理念及其对应用前景的影响，并使用isQ语言编写代码，演示如何为一个简单的布尔满足性问题（例如在一个包含4个元素的系统中寻找使得状态满足 x1=1, x2=0 的目标项）构建相位反转Oracle，并完成单次Grover迭代与测量。

### Reference answer

<thought>
梳理Grover算法的实际应用维度与Oracle设计逻辑。
1. 场景与前景分析：Grover算法的实际应用远不止于字面上的“数据库搜索”。在真实的业务场景中，它被广泛视为解决无结构搜索问题的通用框架，特别是在组合优化（如SAT问题、最大割问题）和密码学分析（如哈希碰撞查找、对称密钥暴力破解）中具有巨大潜力。其能够将复杂度从经典的 O(N) 降低至 O(√N)，在后量子密码时代，这是评估密钥安全强度的重要基准。
2. Oracle设计理念：在实际应用中，业务规则往往被抽象为一个判定函数 f(x)。如果状态 x 满足业务条件（如满足特定的布尔子句），则 f(x)=1。量子Oracle的任务就是识别这些目标态并引入相对相位翻转，实现 (-1)^(f(x))|x⟩。这通常需要将经典逻辑电路转化为可逆量子电路，利用辅助量子比特进行计算，施加相位反转，然后进行“解计算”以恢复辅助比特状态。
3. 代码逻辑推导：
- 问题设定：寻找目标状态 |10⟩（即 x1=1, x2=0）。
- 初始化：使用2个量子比特，施加H门进入均匀叠加态。
- 设计Oracle：针对目标 |10⟩。我们可以先对第二个量子比特施加X门，使状态 |10⟩ 临时变为 |11⟩。接着对这两个量子比特施加CZ门（受控Z门），此时 |11⟩ 的相位会被翻转。最后再次对第二个量子比特施加X门恢复原状。这样只有 |10⟩ 状态的相位被反转，其余状态不受影响。
- 设计扩散算子：实现关于均值反转的相位翻转。电路结构为 H -> X -> CZ -> X -> H。
- 迭代：对于 N=4 且目标数 M=1 的情况，只需进行 1 次Grover迭代即可达到最大概率。
</thought>

Grover算法的实际应用前景广阔，其核心价值在于为无结构空间的搜索提供通用的平方级加速。在现实场景中，它常被应用于解决复杂的组合优化问题（如旅行商问题、布尔可满足性问题SAT）以及密码学中的穷举攻击（如寻找AES的密钥或发现哈希函数的碰撞）。这些问题在经典计算机上通常需要指数级的时间，而Grover算法通过量子叠加与干涉原理，显著缩小了搜索空间。然而，算法的效用高度依赖于Oracle的设计。Oracle相当于一个“黑盒”验证器，它必须能够识别正确答案并引发相位反转。在实际应用中，将复杂的业务逻辑转化为量子电路是工程实现的主要瓶颈，其电路深度往往受限于当前含噪声中等规模量子（NISQ）设备的硬件资源与相干时间。

以下是一个在isQ语言中实现的完整示例。假设我们需要在一个包含4个元素的状态空间中，寻找满足条件 $x_1=1, x_2=0$ 的特定配置。我们将构建对应的Oracle并进行Grover迭代：

```isQ
import std;

qbit q[2];

procedure main() {
    // 步骤 1：初始化，对所有量子比特施加Hadamard门，生成均匀叠加态
    H(q[0]);
    H(q[1]);

    // --- 开始 Grover 迭代 ---

    // 步骤 2：构建Oracle，标记目标状态 |10⟩ (即 q[0]=1, q[1]=0)
    // 对 q[1] 施加 X 门，将 |10⟩ 映射为 |11⟩
    X(q[1]);
    // 使用 CZ 门翻转 |11⟩ 的相位
    CZ(q[0], q[1]);
    // 再次对 q[1] 施加 X 门，恢复 |11⟩ 为 |10⟩，此时只有 |10⟩ 的相位被翻转
    X(q[1]);

    // 步骤 3：构建扩散算子
    H(q[0]);
    H(q[1]);
    X(q[0]);
    X(q[1]);
    CZ(q[0], q[1]);
    X(q[0]);
    X(q[1]);
    H(q[0]);
    H(q[1]);

    // --- 结束 Grover 迭代 ---

    // 步骤 4：测量，理论上将以 100% 的概率坍缩到目标状态 |10⟩
    M(q[0]);
    M(q[1]);
}
```

## isqTrain/3536

- task_id: `isqTrain/3536`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `phase_manipulation`, `ancilla_usage`
- source: `isq_train_cot`
- dataset_index: `4797`

### Prompt

帮我分析一下这个量子程序的输出：

```
import std;

qbit q[2];
qbit anc[1];

procedure main() {
    X(anc[0]); H(anc[0]);
    H(q[0]); H(q[1]);

    CNOT(q[1], anc[0]);

    H(q[0]); H(q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants an analysis of an isQ quantum program to determine the output probability distribution (specifically the non-zero basis states) of the measured qubits. The analysis should be concise, use Dirac notation, and strictly follow the specified format.

2.  **Analyze the Circuit:**
    *   `qbit q[2]; qbit anc[1];` -> 3 qubits: $q_0, q_1, anc_0$. Initial state: $|000\rangle$ (order: $q_0, q_1, anc_0$).
    *   `X(anc[0])` -> Flips anc to $|1\rangle$. State: $|001\rangle$.
    *   `H(anc[0])` -> Hadamard on anc. State: $|00\rangle \otimes |-\rangle = \frac{1}{\sqrt{2}}(|000\rangle - |001\rangle)$.
    *   `H(q[0]); H(q[1])` -> Hadamard on both q. State: $|++\rangle \otimes |-\rangle = \frac{1}{\sqrt{8}} \sum_{x,y \in \{0,1\}} (-1)^z |xyz\rangle$ where z is anc.
        *   Explicitly: $\frac{1}{\sqrt{8}}(|000\rangle + |010\rangle + |100\rangle + |110\rangle - |001\rangle - |011\rangle - |101\rangle - |111\rangle)$.
        *   Wait, let's keep track of the signs carefully.
        *   Initial: $|000\rangle$
        *   X(anc[0]): $|001\rangle$
        *   H(anc[0]): $\frac{1}{\sqrt{2}}(|00\rangle|0\rangle - |00\rangle|1\rangle)$
        *   H(q[0]), H(q[1]): $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle) \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$
    *   `CNOT(q[1], anc[0])` -> Control is $q_1$, target is $anc_0$.
        *   If $q_1 = 1$, flip $anc_0$.
        *   Let's apply this to the state $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle) \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$
        *   For $|00\rangle$, anc is $|-\rangle$. CNOT does nothing (control is 0). Result: $|00\rangle |-\rangle$.
        *   For $|01\rangle$, anc is $|-\rangle$. CNOT flips anc. $X|-\rangle = -|-\rangle$. Result: $-|01\rangle |-\rangle$.
        *   For $|10\rangle$, anc is $|-\rangle$. CNOT does nothing. Result: $|10\rangle |-\rangle$.
        *   For $|11\rangle$, anc is $|-\rangle$. CNOT flips anc. $X|-\rangle = -|-\rangle$. Result: $-|11\rangle |-\rangle$.
        *   State after CNOT: $\frac{1}{2}(|00\rangle - |01\rangle + |10\rangle - |11\rangle) \otimes |-\rangle$.
        *   Let's rewrite this in the Z basis for q to make applying the next H gates easier:
        *   $|00\rangle - |01\rangle = |0\rangle \otimes (|0\rangle - |1\rangle) = \sqrt{2} |0\rangle |-\rangle$ -> actually, $|0\rangle \otimes |1\rangle$ in H basis.
        *   Wait, simply: $|00\rangle - |01\rangle = \sqrt{2} |0\rangle |1\rangle_H$? No.
        *   $|00\rangle - |01\rangle = |0\rangle \otimes (|0\rangle - |1\rangle) = \sqrt{2} |0\rangle |-\rangle$.
        *   Actually, we just need to apply $H(q_0)$ and $H(q_1)$ to $\frac{1}{2}(|00\rangle - |01\rangle + |10\rangle - |

### Reference answer

{'predicted_probs': {'01': 1.0}, 'explanation': 'The output is |01> with probability 1.0'}

## isqTrain/3593

- task_id: `isqTrain/3593`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `entanglement`, `basis_change`, `ancilla_usage`, `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1167`

### Prompt

Fix the bug in the following isQ program.

Bug description: Wrong CNOT direction

The program should 3-qubit phase-flip code with Z error on q[1] and correction.

### Chain-of-thought reasoning

Let me analyze the buggy code and the corrected version to understand the bug.

The buggy code has:

The fixed code has:

The only difference is the first CNOT: `CNOT(q[1], q[0])` vs `CNOT(q[0], q[1])`.

Let me trace through the corrected circuit to verify it produces |000>:

1. Initial state: |000⟩ for q[0], q[1], q[2]

2. CNOT(q[0], q[1]): q[0] is control, q[1] is target. Both are |0⟩, so no change. State: |000⟩

3. CNOT(q[0], q[2]): q[0] is control, q[2] is target. Both are |0⟩, so no change. State: |000⟩

4. H(q[0]); H(q[1]); H(q[2]): Apply Hadamard to all three qubits.
   State: |+⟩|+⟩|+⟩ = |+++⟩

5. Z(q[1]): Apply Z to qubit 1.
   Z|+⟩ = Z(1/√2)(|0⟩ + |1⟩) = (1/√2)(|0⟩ - |1⟩) = |-⟩
   State: |+⟩|-⟩|+⟩

6. H(q[0]); H(q[1]); H(q[2]): Apply Hadamard to all three.
   H|+⟩ = |0⟩
   H|-⟩ = |1⟩
   State: |0⟩|1⟩|0⟩ = |010⟩

   This is equivalent to the bit-flip code with an X error on q[1].

7. Syndrome extraction:
   CNOT(q[0], anc[0]): Control q[0]=|0⟩, anc[0] stays |0⟩
   CNOT(q[1], anc[0]): Control q[1]=|1⟩, anc[0] flips to |1⟩
   CNOT(q[1], anc[1]): Control q[1]=|1⟩, anc[1] flips to |1⟩
   CNOT(q[2], anc[1]): Control q[2]=|0⟩, anc[1] stays |1⟩
   
   Syndrome: anc[0]=1, anc[1]=1 (binary 11)

8. ctrl ctrl X(anc[0], anc[1], q[1]): Since anc[0]=|1⟩ and anc[1]=|1⟩, apply X to q[1].
   q[1] was |1⟩, flips to |0⟩.
   State: |000⟩

9. Measurement: |000⟩ with probability 1.0

Now let me check the buggy version:

1. Initial state: |000⟩

2. CNOT(q[1], q[0]): q[1] is control, q[0] is target. Both are |0⟩, so no change. State: |000⟩

3. CNOT(q[0], q[2]): q[0] is control, q[2] is target. Both are |0⟩, so no change. State: |000⟩

Actually wait, at this point the states are the same because all qubits start in |0⟩, so any CNOT does nothing. The encoding produces |+++⟩ in both cases.

Let me re-examine. The issue might be more subtle. The encoding of |0_L⟩ = |+++⟩ should be: start with |000⟩, apply H to all qubits to get |+++⟩. The CNOTs before the Hadamards shouldn't matter since everything is |0⟩.

Hmm, but actually the code applies CNOTs BEFORE the Hadamards. So:
- Start: |000⟩
- CNOT(q[1], q[0]) [buggy] or CNOT(q[0], q[1]) [fixed]: Both do nothing since all |0⟩
- CNOT(q[0], q[2]): Does nothing since |0⟩
- H on all: |+++⟩

So actually both versions would produce the same |+++⟩ state after encoding. This means the bug might not actually matter for this specific case since we're starting from |000⟩.

Wait, let me re-read more carefully. Actually, the encoding is supposed to create an entangled state, but with C

## isqTrain/875

- task_id: `isqTrain/875`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `2888`

### Prompt

Write an isQ program that implements the inner_product_mod2 pattern. Include explicit identity operations in the circuit (H-H pair before M(q[4])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
Goal: Compute the inner product mod 2 of x=[1,0] and y=[1,1], storing the result in q[4].

Five qubits are used; only q[4] is measured. State evolution:
1. |00000⟩ — Initial state.
2. X(q[0]); X(q[2]); X(q[3]) → |10110⟩ — Encodes x and y vectors.
3. ctrl ctrl X(q[0],q[2],q[4]) → |10111⟩ — x[0]·y[0]=1, flips q[4].
4. ctrl ctrl X(q[1],q[3],q[4]) → |10111⟩ — x[1]·y[1]=0, no flip (q[1]=0).
5. H(q[4]) → |1011⟩⊗(|0⟩−|1⟩)/√2 — Creates superposition on q[4].
6. H(q[4]) → |10111⟩ — Second H cancels the first (H²=I identity pair).
7. M(q[4]) collapses to |1⟩ with probability 1.0, since IP = (1·1)⊕(0·1) = 1.

The H-H pair demonstrates gate cancellation: two consecutive Hadamards form identity, leaving q[4] in |1⟩ deterministically.
