# ISQ training COT RAG corpus: quantum_error_correction shard 14

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqQA/quantum_error_correction/73_trap_analysis

- task_id: `isqQA/quantum_error_correction/73_trap_analysis`
- task_type: `qa_concept`
- category: `quantum_error_correction`
- difficulty: `expert`
- concept_tags: `trap_analysis`, `concept`, `魔法态蒸馏`
- source: `qa_pipeline`
- dataset_index: `5475`

### Prompt

我听说魔法态蒸馏可以显著提高量子态的保真度并实现容错量子计算。既然如此，我们能否直接利用魔法态蒸馏技术，对物理量子比特上任意待处理的未知量子态进行去噪和提纯？甚至，只要有了魔法态蒸馏，我们是不是就可以完全抛弃表面码等复杂的量子纠错编码过程，直接在含噪的物理设备上运行通用量子算法？

### Reference answer

<think>
首先，需要识别问题中的核心逻辑陷阱：将“魔法态蒸馏（MSD）”泛化为一种通用的量子态去噪和纠错工具。

第一步是概念界定。从原理出发，魔法态并非“任意未知量子态”，而是专门为实现非克利福德门（如T门）而精心设计的特定资源态。因此，它无法用于提纯承载计算数据的任意量子态。

第二步是机制剖析。深入分析MSD的执行过程，发现它依赖于执行高保真度的多比特Clifford操作和稳定子测量。如果在充满噪声的裸物理设备上直接运行，这些复杂的操作本身会引入巨大的物理噪声，导致蒸馏协议直接崩溃。

第三步是理清架构层级。正是由于MSD过程需要极高的操作保真度，它不仅不能替代表面码等量子纠错码（QEC），反而必须严格建立在QEC提供的逻辑级保护之上。因此，推理结论是：MSD与QEC是互补依存关系，绝不能抛开QEC单独使用。
</think>

<thought>
1. **识别请求**：主题是“魔法态蒸馏”，要求是“陷阱辨析维度”，难度为“expert”。需要设计一个常见误解作为陷阱。
2. **设计陷阱**：最常见的误解是将“魔法态蒸馏”视为一种通用的量子纠错机制。初学者往往认为，既然它可以“提纯”量子态，那么我们就可以用它来纠正任何量子计算过程中的错误，甚至认为只要有了魔法态蒸馏，就不需要复杂的底层量子纠错码（如表面码）了。
3. **详细纠正逻辑**：
   - **概念限制**：魔法态并不是任意的量子态，而是专门为了实现非克利福德门（如T门）而制备的特定非稳定子资源态。
   - **互补而非替代**：魔法态蒸馏（MSD）绝对不能替代量子纠错码（QEC）。相反，MSD 必须建立在 QEC 的基础之上。
   - **原理剖析**：MSD 的核心是利用多个带噪的魔法态，通过执行 Clifford 群操作和稳定子测量，丢弃出错的分支。如果没有底层的 QEC 保护，MSD 过程本身的 Clifford 操作和多比特测量就会引入巨大的物理噪声，导致蒸馏协议在物理层面直接崩溃。
   - **架构层次**：容错量子计算的正确架构是自下而上的：物理层 -> 纠错码层（如表面码）-> 魔法态蒸馏工厂 -> 逻辑算法层。
4. **融入isQ代码**：为满足系统约束并增强专业性，我将在解释中展示一段 isQ 代码，演示魔法态是如何作为“耗材”注入到电路中以实现非Clifford逻辑的，从而反证它只是高层资源而非底层纠错网。
</thought>

**错误观点**：
魔法态蒸馏是一种通用的量子态提纯和纠错技术，可以直接用于任意未知的物理量子态去噪；只要掌握了魔法态蒸馏技术，我们就可以完全绕过底层的表面码等量子纠错编码，直接在含噪中等规模量子（NISQ）设备上实现容错的通用量子计算。

**详细纠正与原理解析**：
这是一个极其危险且根本性的认知陷阱。要澄清这个误解，必须明确魔法态蒸馏在容错量子计算架构中的准确定位——它是量子纠错码的“高层消费者”，而不是底层物理错误的“清道夫”。

1. **魔法态不是通用态，提纯目标极其狭窄**：
魔法态并不是指任意含有量子信息的量子态。在容错量子计算中，由于 Eastin-Knill 定理限制了任何量子纠错码都不能拥有通用的横向逻辑门集，我们通常只能横向实现 Clifford 门。为了实现通用计算，必须引入非 Clifford 门（最典型的是 T 门）。魔法态（如 $|T\rangle = (|0\rangle + e^{i\pi/4}|1\rangle)/\sqrt{2}$）就是为了通过“门注入”和“门隐形传态”来间接实现这些非 Clifford 门而专门制备的特定资源态。MSD 仅仅只能提纯这类极其特殊的固定状态的资源，它完全无法处理一个正在运行算法的、处于任意叠加态的“数据量子比特”。

2. **MSD 不能替代底层 QEC，反而严重依赖于它**：
如果你直接在未经纠错保护的物理量子比特上运行魔法态蒸馏协议，注定会惨败。MSD 的核心机制（如 15-to-1 的 Bravyi-Kitaev 协议）需要执行大量复杂的 Clifford 操作（如 CNOT 门级联）并进行多体稳定子测量。在物理层面，这些操作本身就会引入严重错误。如果你的系统没有底层的表面码等机制来持续纠错，MSD 过程中用来筛选好坏魔法态的“测量标志位”本身就会被噪声淹没，导致你根本无法区分哪个态是被提纯的，哪个态是被污染的。因此，魔法态蒸馏不仅不能替代表面码，它反而是由无数个已经被表面码纠错保护好的“逻辑量子比特”所构成的高级别宏观操作。在实际的容错架构中，物理量子比特先被编入表面码，然后成千上万个这样的逻辑量子比特被投入到一个“魔法态工厂”中，消耗大量低保真度的逻辑魔法态，才能周期性地榨取出极少部分极高保真度的逻辑魔法态。

3. **isQ 语言下的魔法态注入示例**：
为了更直观地理解，我们可以看一段使用 isQ 语言编写的代码。在这个示例中，我们不是在进行魔法态蒸馏，而是在算法中“消耗”已经蒸馏好的魔法态来实现高精度的 T 门。

```isq
import std;

// 声明用于存放普通数据的逻辑比特 q，以及准备用于注入的高保真度魔法态资源 magic_q
qbit q[2];
qbit magic_q[1]; 

procedure main() {
    // 在实际的容错架构中，q[0] 和 q[1] 是受表面码保护的逻辑数据
    H(q[0]);
    H(q[1]);
    
    // 假设 magic_q[0] 初始化为通过魔法态蒸馏工厂刚刚提纯出的高保真度 |T> 态
    // 此处省略了蒸馏工厂本身极其复杂的稳定子测量代码
    // 我们直接使用它来辅助执行非 Clifford 逻辑（T 门注入的简化表示）
    
    CNOT(q[0], magic_q[0]); // 将数据比特与魔法态纠缠
    
    // 测量魔法态，获取经典信息
    int res = M(magic_q[0]);
    
    // 根据测量结果，对原始数据执行相应的 Clifford 修正操作
    if (res == 1) {
        S(q[0]); // S 门属于 Clifford 门，可以直接横向执行，无需消耗魔法态
    }
    
    // 至此，逻辑上的 T 门操作就被安全地施加在了 q[0] 上
}
```

总结来说，认为“魔法态蒸馏可以通用地提纯任意态并取代底层纠错码”的误区，混淆了“计算资源”与“保护机制”的界限。魔法态蒸馏是构筑在坚不可摧的量子纠错码（如表面码）地基之上的炼金术，它将普通的稳定子态转化为能够实现通用计算的“魔法”（非 Clifford 门），但它绝不是一块可以随便盖在物理噪声之上遮风挡雨的万能抹布。

## isqQA/quantum_error_correction/163_trap_analysis

- task_id: `isqQA/quantum_error_correction/163_trap_analysis`
- task_type: `qa_concept`
- category: `quantum_error_correction`
- difficulty: `difficult`
- concept_tags: `trap_analysis`, `concept`, `CSS码的构造`
- source: `qa_pipeline`
- dataset_index: `5030`

### Prompt

在学习CSS（Calderbank-Shor-Steane）码的构造时，我经常看到一种说法：“只要选取两个满足对偶包含条件的经典线性码 C1 和 C2（即 C2 ⊂ C1），我们就可以直接将它们作为生成矩阵来构造CSS码，具体来说就是用 C1 的生成矩阵 G1 进行比特翻转的编码，用 C2 的生成矩阵 G2 进行相位翻转的编码。” 这种理解是否完全准确？这其中存在什么常见的陷阱？

### Reference answer

<think>
要判断该说法的准确性，我们需要从CSS码结合两个经典线性码的数学本质进行逆向推导：

首先，分析CSS码纠正比特翻转（X错误）的机制。在量子态中，Z稳定子负责探测X错误。要利用经典码C1来纠正这些错误，Z稳定子必须由C1的校验矩阵（即H1）构成，而非直接使用生成矩阵G1。

其次，分析纠正相位翻转（Z错误）的机制。X稳定子用于探测Z错误。根据量子力学原理，经过哈达玛基变换后，Z错误在X基下等价于X错误。因此，要利用经典码C2的纠错能力，X稳定子实际上应对应C2的对偶码，即由C2的校验矩阵H2（或对偶码的生成矩阵）来生成。

最后，比对原说法。原说法声称直接用C2的生成矩阵G2进行相位翻转编码，这忽略了量子基变换所引入的对偶关系。这种混淆经典码本身与其对偶码在X/Z基下映射关系的错误，正是该说法中的核心陷阱。
</think>

这种说法存在一个非常经典的陷阱：混淆了经典码与纠正相位翻转对应的“对偶码”之间的关系。

**错误剖析：**
该说法的错误在于认为“用 C2 的生成矩阵 G2 进行相位翻转的编码”。实际上，相位翻转在经过哈达玛门基变换后等价于比特翻转。因此，如果我们要利用经典码 C2 的纠错能力来纠正相位翻转，我们在计算基下实际使用的并不是 C2 本身，而是它的对偶码 C2⊥（或者说是 C2 的校验矩阵 H2）。

**正确的构造原理：**
构造CSS码需要两个经典线性码 C1 和 C2，通常要求它们满足对偶包含条件 C2 ⊂ C1。假设 C1 是参数为 [n, k1] 的码，C2 是参数为 [n, k2] 的码。

1. **X稳定子（纠正相位翻转）：** 它们对应的是 C2 的元素。在态的构造中，这意味着我们在X基下的叠加包含了 C2 的码字。实际上，X稳定子的生成元对应的是 C2⊥ 的生成矩阵 H2 所代表的X算符。
2. **Z稳定子（纠正比特翻转）：** 它们对应的是 C1⊥ 的元素。Z稳定子的生成元对应的是 C1 的校验矩阵 H1 所代表的Z算符。
3. **逻辑量子比特：** 有效的逻辑态存在于商空间 C1 / C2 中，其逻辑维度（逻辑量子比特数）为 k = k1 - k2。

**纠正后的结论：**
正确的CSS码构造应当是：利用 C1 的校验矩阵 H1 构造Z稳定子来检测比特翻转（利用 C1⊥ 的纠错能力），同时利用 C2 的校验矩阵 H2 构造X稳定子来检测相位翻转（利用 C2⊥ 的纠错能力）。误将 G2 直接用于相位编码会导致稳定子群的结构完全错误，因为 G2 的行向量将无法与 H1 的行向量对易，从而无法构成一个合法的量子稳定子码。

为了更直观地理解这个纠正过程，我们可以使用isQ语言编写一个基于 C1=[[7,4,3]] 汉明码和 C2=[[7,1,3]] 重复码（注意此时满足 C2 ⊂ C1）的简化版Steane码稳定子测量电路的代码示例：

```isQ
import std;

qbit q[7];
qbit anc[3];

procedure main() {
    // 将数据比特制备为叠加态以模拟编码空间
    for i in 0:7 {
        H(q[i]);
    }
    
    // Z稳定子测量（基于C1的校验矩阵H1）
    // Steane码的Z稳定子生成元对应H1的行：1111000, 1100110, 1010101 等
    // 此处简化演示第一个Z稳定子 1111000
    for i in 0:4 {
        CNOT(q[i], anc[0]);
    }
    // 测量辅助比特
    int r = M(anc[0]);
    
    // 重置辅助比特以供后续使用
    if (r == 1) {
        X(anc[0]);
    }

    // X稳定子测量（基于C2的校验矩阵H2）
    // C2是重复码，校验矩阵H2对应逻辑为 1100000, 0011000, 0000110 等
    // 此处简化演示第一个X稳定子 1100000
    // 测量X稳定子需要将数据比特变到X基，然后执行CNOT
    H(anc[1]);
    for i in 0:2 {
        CNOT(anc[1], q[i]);
    }
    H(anc[1]);
    // 测量辅助比特
    int s = M(anc[1]);
}
```

## isqTrain/1878

- task_id: `isqTrain/1878`
- task_type: `output_prediction`
- category: `quantum_error_correction`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2359`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[9];
procedure main() {
    H(q[0]);
    CNOT(q[0], q[3]);
    CNOT(q[0], q[6]);
    H(q[0]); H(q[3]); H(q[6]);
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);
    CNOT(q[3], q[4]);
    CNOT(q[3], q[5]);
    CNOT(q[6], q[7]);
    CNOT(q[6], q[8]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]); M(q[4]); M(q[5]); M(q[6]); M(q[7]); M(q[8]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Analyze an isQ quantum program and predict the probability distribution of measurement outcomes.
    *   Input code: A 9-qubit circuit.
    *   Constraint: Concise (3-15 lines), output only the analysis starting with "## Circuit Analysis", NO code blocks, end with the predicted probability distribution.
    *   Target probabilities: {'000000000': 0.25, '000111111': 0.25, '111000111': 0.25, '111111000': 0.25}

2.  **Analyze the Circuit:**
    *   Initial state: $|0\rangle^{\otimes 9}$
    *   H(q[0]): $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)_0 \otimes |0\rangle_{1..8}$
    *   CNOT(0,3), CNOT(0,6): GHZ state on 0,3,6 -> $\frac{1}{\sqrt{2}}(|000\rangle + |111\rangle)_{0,3,6} \otimes |0\rangle^{\otimes 6}$
    *   H(0), H(3), H(6): Apply H to each of the entangled qubits.
        *   $H|0\rangle = |+\rangle$, $H|1\rangle = |-\rangle$
        *   $|000\rangle \to |+++\rangle$
        *   $|111\rangle \to |---\rangle$
        *   State is $\frac{1}{\sqrt{2}}(|+++\rangle + |---\rangle)$.
        *   Since $|+\rangle = \frac{|0\rangle+|1\rangle}{\sqrt{2}}$ and $|-\rangle = \frac{|0\rangle-|1\rangle}{\sqrt{2}}$.
        *   This state can be rewritten as $\frac{1}{2}(|000\rangle + |011\rangle + |101\rangle + |110\rangle)_{0,3,6}$. Let me re-evaluate.
        *   Wait, $|+++\rangle + |---\rangle = \frac{1}{2\sqrt{2}} [ (|0\rangle+|1\rangle)(|0\rangle+|1\rangle)(|0\rangle+|1\rangle) + (|0\rangle-|1\rangle)(|0\rangle-|1\rangle)(|0\rangle-|1\rangle) ]$.
        *   Expanding this gives: $|000\rangle + |011\rangle + |101\rangle + |110\rangle$. Yes, the even parity states of 3 qubits.
        *   So, $\frac{1}{2}(|000\rangle + |011\rangle + |101\rangle + |110\rangle)_{0,3,6} \otimes |0\rangle_{rest}$.
    *   CNOT(0,1), CNOT(0,2): Copies q[0] to q[1] and q[2].
        *   If 0 is 1, q[1,2] become 1.
        *   State: $\frac{1}{2}(|000\rangle_{0,1,2} + |111\rangle_{0,1,2}) \otimes |00\rangle_{3,6} + ...$
    *   CNOT(3,4), CNOT(3,5): Copies q[3] to q[4] and q[5].
    *   CNOT(6,7), CNOT(6,8): Copies q[6] to q[7] and q[8].
    *   Effectively, the state $\frac{1}{2}(|000\rangle + |011\rangle + |101\rangle + |110\rangle)_{0,3,6}$ becomes $\frac{1}{2}(|000000000\rangle + |000111111\rangle + |111000111\rangle + |111111000\rangle)$.
    *   Measurements yield these four strings with equal probability 1/4 = 0.25.

3.  **Draft the step-by-step reasoning:**
    *   Start with `## Circuit Analysis`
    *   Step 1: Initial state $|0\rangle^{\otimes 9}$.
    *   Step 2: `H(q[0])` creates $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)_0$.
    *   Step 3: `CNOT(0

### Reference answer

{'predicted_probs': {'000000000': 0.25, '000111111': 0.25, '111000111': 0.25, '111111000': 0.25}, 'explanation': 'Expected probabilities: [0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]'}

## isqTrain/288

- task_id: `isqTrain/288`
- task_type: `code_generation`
- category: `quantum_error_correction`
- difficulty: `intermediate`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `5054`

### Prompt

实现以下量子计算任务（使用isQ）：implements the error_correction_syndrome pattern but with a different initial state preparation (flip q[[0]] -> q[1]).

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a 3-qubit bit-flip encoding circuit but with the initial state prepared on q[1] instead of q[0].

2. **Qubits**: 3 qubits (q[0], q[1], q[2]), all measured at the end.

3. **State evolution**:
   - **Initial**: |000⟩
   - **X(q[1])**: Flips q[1] → |010⟩
   - **CNOT(q[0], q[1])**: Control q[0]=0, so no action → |010⟩
   - **CNOT(q[0], q[2])**: Control q[0]=0, so no action → |010⟩

4. **Expected probabilities**: The final state is |010⟩ with certainty. Since q[0]=0 (measured first = highest bit), q[1]=1, q[2]=0, the measurement bitstring is |010⟩ with probability 1.0. Unlike the standard encoding (which would produce |111⟩ from X(q[0])), here the X gate is on a non-control qubit, so the CNOTs never activate.

## isqQA/quantum_error_correction/74_popular_explanation

- task_id: `isqQA/quantum_error_correction/74_popular_explanation`
- task_type: `qa_concept`
- category: `quantum_error_correction`
- difficulty: `expert`
- concept_tags: `popular_explanation`, `concept`, `qLDPC码`
- source: `qa_pipeline`
- dataset_index: `13`

### Prompt

听说量子低密度奇偶校验码（qLDPC码）是目前量子纠错领域的前沿技术，被认为是未来实现大规模量子计算机的关键。但我没有任何数学和物理基础，你能用一个日常生活的例子，给我讲讲它到底是怎么回事吗？它为什么那么厉害？

### Reference answer

想象一下，你是一个超级博物馆的馆长，馆里珍藏着许多极其罕见、一见光就会瞬间消失的魔法玻璃雕像（这就像是极其脆弱的“量子比特”）。为了让雕像不消失，你绝对不能直接进入房间去看它们有没有损坏。但是，这些雕像又特别娇贵，时不时地会因为空气流动而出现微小的裂纹（这叫做“量子噪声”）。既然不能直接看，我们该怎么保护它们呢？

你决定雇佣大量的“巡逻保安”。保安不能开门看雕像，但他们可以站在走廊里，通过检查相邻几个房间的门窗震动情况，来判断是否有异常。这种“检查周围几个房间状态是否一致”的动作，在量子计算里就叫做“奇偶校验”。

在早期的保护方案中（比如传统的表面码），你可能需要雇佣上万个保安，死死围住一个雕像。虽然很安全，但这太浪费空间和人力了，导致我们永远造不出能装下足够多雕像的博物馆。

这就是“量子低密度奇偶校验码”出场的时候了。这个名词听起来吓人，但拆解开来看非常直观：

首先是“低密度”。这意味着每个保安不需要检查几百个房间，他们只需要拿着对讲机，核对两三个相邻房间的震动情况（每个校验只涉及少量量子比特）。同时，每个雕像房间也只由两三个保安负责监视（每个量子比特只参与少量校验）。因为每个人的任务都很轻（密度很低），所以他们的工作速度极快，不会因为互相干扰而犯错。

其次是“量子”和“奇偶”的结合。因为魔法雕像有一种奇特的“分身术”（量子叠加态），保安在用对讲机交流时必须非常小心，绝不能泄露雕像的具体形态，只能交流“这几个房间的震动规律是否矛盾”。这种巧妙的交流密码，就是所谓的“量子”校验。

那么，qLDPC到底厉害在哪里？过去的保护方案就像是把雕像平铺在一个巨大的二维网格平房里，保护一个雕像需要占用一大片土地。而qLDPC就像是给保安们配备了“魔法电梯”和“立体通道”。虽然每个保安依然只检查几个房间，但因为有了四通八达的立体通道，他们可以跨越楼层，建立起极其严密的交叉监控网。这样一来，你就可以把博物馆建造成高耸入云的摩天大楼，而不是占用无限大的土地。在有限的物理空间内，它能保护的魔法雕像数量呈指数级增长，这也就是为什么科学家们认为，qLDPC码是未来建造拥有数百万甚至上亿量子比特的超级量子计算机的终极钥匙。

## isqExpand/qa/59

- task_id: `isqExpand/qa/59`
- task_type: `qa_concept`
- category: `quantum_error_correction`
- difficulty: `difficult`
- concept_tags: `quantum_error_correction`, `stabilizer_formalism`, `pauli_group`, `code_space`, `syndrome_measurement`
- source: `qa_pipeline`
- dataset_index: `5246`

### Prompt

什么是量子纠错码的稳定子形式？如何用稳定子组描述一个量子码？

### Chain-of-thought reasoning

## 推理
1. **明确问题**：用户询问两个核心概念：一是量子纠错码的稳定子形式的定义，二是如何使用稳定子组来描述一个具体的量子码。
2. **解构“稳定子形式”**：需要从基础的保利群出发，解释什么是子群，以及算符如何通过特征值为+1来“稳定”一个或一组量子态。必须强调阿贝尔群和不含 $-I$ 的条件。
3. **解构“描述量子码”**：解释生成元的概念，说明 $[[n, k]]$ 码需要 $n-k$ 个生成元。进一步解释纠错原理，即通过测量生成元得到错误伴随式（Syndrome），利用对易和反对易关系区分不同的错误。
4. **引入实例**：抽象概念需要具体例子支撑。选择最经典的3-qubit位翻转码。计算它的稳定子生成元 $Z_1 Z_2$ 和 $Z_1 Z_3$，并分析发生错误（如 $X_1$）时伴随式如何变化。
5. **结合isQ编程**：为了让回答更加完整和契合提示要求，设计一个isQ代码片段，展示如何用辅助比特和CZ门测量这些稳定子（在计算基下，通过前后包裹H门将CZ变为CX作用以测量Z，或者直接利用相位反作用力）。
6. **内容组织**：引言 -> 核心数学定义 -> 描述方法与纠错原理 -> 具体算例分析 -> isQ代码示例 -> 总结。确保逻辑连贯，数学公式符合LaTeX规范，且不使用Markdown代码块包裹整个输出。

### Reference answer

稳定子形式是量子纠错理论中极其重要的一种数学框架，由Daniel Gottesman提出。它利用群论的方法，极大地简化了量子态空间和量子纠错码的构造与分析。理解稳定子形式，是掌握如表面码、Shor码、Steane码等现代量子纠错码的基础。

### 1. 什么是稳定子形式？

在量子力学中，我们研究的状态通常是希尔伯特空间中的向量。而稳定子形式改变了我们的视角：它通过一组作用于希尔伯特空间的算符（操作）来定义和描述一个量子状态空间。

假设系统有 $n$ 个量子比特，其希尔伯特空间为 $\mathcal{H}_2^{\otimes n}$。我们首先定义 $n$ 阶保利群 $\mathcal{P}_n$（Pauli Group），它由所有形如 $i^k P_1 \otimes P_2 \otimes \dots \otimes P_n$ 的张量积组成，其中 $k \in \{0,1,2,3\}$，且 $P_j \in \{I, X, Y, Z\}$。

**稳定子**是指保利群 $\mathcal{P}_n$ 中的一个子群 $\mathcal{S}$。对于一个给定的子群 $\mathcal{S}$，我们可以找到所有满足以下条件的量子态 $|\psi\rangle$：
$$ P |\psi\rangle = |\psi\rangle, \quad \forall P \in \mathcal{S} $$
这意味着子群 $\mathcal{S}$ 中的所有算符都保持状态 $|\psi\rangle$ 不变（即特征值为 $+1$ 的特征向量）。所有满足这一条件的量子态张成的线性空间，就称为稳定子群 $\mathcal{S}$ 的**码空间**。

为了保证码空间是非平凡的（即存在这样的态），稳定子群 $\mathcal{S}$ 必须满足以下两个条件：
1. **阿贝尔群（可交换）**：群内的任意两个元素必须相互对易，即 $[P_i, P_j] = 0$。
2. **不包含负单位阵**：群内不能包含算符 $-I$，否则将要求 $-|\psi\rangle = |\psi\rangle$，这会导致 $|\psi\rangle = 0$。

### 2. 如何用稳定子组描述一个量子码？

在实际构造量子码时，我们不需要列出稳定子群 $\mathcal{S}$ 中的所有 $2^{n-k}$ 个元素，而是可以通过一组数量较少的**生成元**来完整描述该群。

假设我们要构造一个将 $k$ 个逻辑量子比特编码到 $n$ 个物理量子比特中的量子码（记为 $[[n, k]]$ 码）。由于 $n$ 个物理比特对应的保利群维度关系，我们需要 $n-k$ 个独立的、相互对易的保利算符 $g_1, g_2, \dots, g_{n-k}$ 作为生成元。这组生成元完全刻画了稳定子群 $\mathcal{S} = \langle g_1, g_2, \dots, g_{n-k} \rangle$，同时也唯一确定了该量子码的码空间。

**纠错原理与错误检测**：
稳定子代码之所以能纠错，是因为我们可以通过反复测量这 $n-k$ 个生成元来获取系统的**错误伴随式**。
- 如果没有错误发生，系统状态处于码空间内，所有生成元的测量结果都将是 $+1$。
- 如果系统发生了某种错误 $E \in \mathcal{P}_n$，状态变成了 $E|\psi\rangle$。当我们测量生成元 $g_i$ 时，结果取决于 $g_i$ 与 $E$ 的对易关系：
  - 如果 $[g_i, E] = 0$，测量结果仍为 $+1$。
  - 如果 $\{g_i, E\} = 0$（反对易），测量结果将翻转为 $-1$。
通过记录哪些生成元返回了 $-1$，我们可以得到一个二进制伴随式向量，从而定位并识别发生的错误。

### 3. 示例说明：3量子比特位翻转码

以最简单的 $[[3, 1, 3]]$ 位翻转码为例。我们将1个逻辑比特编码到3个物理比特中，逻辑态定义为：
$$ |\bar{0}\rangle = |000\rangle, \quad |\bar{1}\rangle = |111\rangle $$
显然，这个码空间可以由以下两个相互对易的保利算符生成：
$$ g_1 = Z \otimes Z \otimes I = Z_1 Z_2 $$
$$ g_2 = Z \otimes I \otimes Z = Z_1 Z_3 $$
稳定子群为 $\mathcal{S} = \langle Z_1 Z_2, Z_1 Z_3 \rangle$。

如果第一个量子比特发生了位翻转（即错误 $E = X \otimes I \otimes I = X_1$）：
因为 $X_1$ 与 $Z_1$ 反对易，所以 $X_1$ 会与 $g_1$ 和 $g_2$ 均反对易。当我们测量 $g_1$ 和 $g_2$ 时，都会得到 $-1$。对应的伴随式为 $(-1, -1)$。由于只有当第一个比特发生翻转时才会出现这个伴随式，我们就能断定是第一个比特出错了，只需对其施加 $X$ 门即可恢复。

**isQ代码示例**：
以下展示了如何在isQ中模拟3比特位翻转码的稳定子测量电路。通过引入两个辅助比特来无损地测量生成元 $Z_1 Z_2$ 和 $Z_1 Z_3$。

```isq
import std;

qbit q[3]; // 数据量子比特（存储逻辑态）
qbit a[2]; // 辅助量子比特（用于测量稳定子）

procedure main() {
    // 准备逻辑0态：|000>
    for(int i=0; i<3; i++){
        H(q[i]);
        // 这里简化演示，实际应为 |000>
    }
    // 假设在此处注入错误，例如在q[0]作用X门
    X(q[0]); 

    // 稳定子测量：测量 g1 = Z1 Z2, 结果存于 a[0]
    H(a[0]);
    CZ(q[0], a[0]); // Z1 作用
    CZ(q[1], a[0]); // Z2 作用
    H(a[0]);
    // 测量 a[0] 获得 g1 的特征值

    // 稳定子测量：测量 g2 = Z1 Z3, 结果存于 a[1]
    H(a[1]);
    CZ(q[0], a[1]); // Z1 作用
    CZ(q[2], a[1]); // Z3 作用
    H(a[1]);
    // 测量 a[1] 获得 g2 的特征值
    
    // 根据测量结果 (伴随式) 执行恢复操作 (略)
}
```
通过上述框架，稳定子形式将复杂的量子态空间分析转化为了群论中生成元的代数运算与测量电路的设计，是目前容错量子计算的核心基石。

## isqQA/quantum_error_correction/163_isq_demonstration

- task_id: `isqQA/quantum_error_correction/163_isq_demonstration`
- task_type: `qa_concept`
- category: `quantum_error_correction`
- difficulty: `difficult`
- concept_tags: `isq_demonstration`, `concept`, `CSS码的构造`
- source: `qa_pipeline`
- dataset_index: `3663`

### Prompt

请解释量子纠错中CSS（Calderbank-Shor-Steane）码的核心构造原理，并使用isQ语言编写一个程序来演示一个最简单的CSS码（例如基于4个物理量子比特的[[4,2,2]]错误检测码）的编码电路，以及它如何分离并独立测量X和Z类型的稳定子。

### Reference answer

CSS码是量子纠错码中极其重要的一类，它的核心构造思想是利用两个经典的线性分组码来分别独立处理量子比特的位翻转（X错误）和相位翻转（Z错误）。

在数学构造上，假设我们有两个经典线性码：码 $C_1$（参数为 $[n, k_1]$）和码 $C_2$（参数为 $[n, k_2]$），并且它们满足对偶包含条件，即 $C_2^\perp \subset C_1$。基于此，我们可以构造出一个参数为 $[[n, k_1 - k_2, d]]$ 的量子CSS码。具体来说：
1. **Z稳定子（用于检测X错误）**：对应于经典码 $C_2$ 的生成矩阵，作用于量子态上表现为一系列 $Z$ 操作的张量积。这相当于检查量子态是否属于特定的经典码字空间。
2. **X稳定子（用于检测Z错误）**：对应于经典码 $C_1$ 的对偶码 $C_1^\perp$ 的生成矩阵，表现为一系列 $X$ 操作的张量积。
因为 $C_2^\perp \subset C_1$，这就保证了所有的 X 稳定子和 Z 稳定子是相互对易的，从而可以进行联合测量。CSS码的最大优势在于其稳定子测量网络可以通过经典码的奇偶校验矩阵直接映射，极大地简化了容错量子计算的实现。

为了直观演示这一概念，我们以最简单的 $[[4, 2, 2]]$ 错误检测码为例。它可以看作是一个CSS码，其 X 稳定子为 $X_0 X_1 X_2 X_3$，Z 稳定子为 $Z_0 Z_1 Z_2 Z_3$。在下方的isQ程序中，我们将编码一个逻辑态 $\frac{1}{\sqrt{2}}(|0000\rangle + |1111\rangle)$，主动注入一个Z错误，并演示如何分别提取Z稳定子和X稳定子的错误伴随式（Syndrome）：

```isq
import std;

qbit q[4]; // 4个数据量子比特
qbit a[2]; // 2个辅助量子比特，用于测量稳定子

procedure main() {
    // 1. CSS编码过程：构造叠加态 (|0000> + |1111>) / sqrt(2)
    // 这实际上构造了逻辑 |00> 态的子空间
    H(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);
    CNOT(q[0], q[3]);

    // 2. 模拟信道传输：在 q[1] 上注入一个 Z 错误 (相位翻转)
    Z(q[1]);

    // 3. 测量 Z 稳定子 (Z_0 Z_1 Z_2 Z_3) 以检测 X错误
    // 利用辅助比特 a[0]，通过受控非门级联测量奇偶性
    H(a[0]);
    CNOT(q[0], a[0]);
    CNOT(q[1], a[0]);
    CNOT(q[2], a[0]);
    CNOT(q[3], a[0]);
    H(a[0]);
    int z_syndrome = M(a[0]);

    // 4. 测量 X 稳定子 (X_0 X_1 X_2 X_3) 以检测 Z错误
    // CSS码的特征：将数据比特通过 H 门转换到 X 基，即可使用与Z稳定子相同的测量网络
    for i in 0:4 {
        H(q[i]);
    }
    H(a[1]);
    CNOT(q[0], a[1]);
    CNOT(q[1], a[1]);
    CNOT(q[2], a[1]);
    CNOT(q[3], a[1]);
    H(a[1]);
    int x_syndrome = M(a[1]);

    // 输出错误伴随式
    // 预期结果：z_syndrome = 0（无X错误），x_syndrome = 1（检测到Z错误）
    print x_syndrome;
    print z_syndrome;
}
```

## isqQA/quantum_error_correction/175_popular_explanation

- task_id: `isqQA/quantum_error_correction/175_popular_explanation`
- task_type: `qa_concept`
- category: `quantum_error_correction`
- difficulty: `expert`
- concept_tags: `popular_explanation`, `concept`, `transversal gate`
- source: `qa_pipeline`
- dataset_index: `2814`

### Prompt

我是一名没有任何物理背景的初学者，最近看科普文章时经常看到量子计算机里有一个词叫“Transversal Gate（横向门）”，据说它对防止量子计算错误非常重要。你能不使用任何复杂的数学公式，仅用日常生活的通俗类比，向我解释一下到底什么是Transversal Gate吗？为什么它被称为量子纠错的“保护伞”？

### Reference answer

要理解这个极其核心的量子纠错概念，我们可以先用一个合唱团的日常例子来打个比方。假设你是一个大型合唱团的指挥，你要让合唱团完成一次复杂的和声转换（这就好比量子计算机要执行一个计算操作）。在普通的合唱团里，歌手们站在一起，如果某个人感冒咳嗽（这就好比量子计算机里发生的“错误”），病菌很容易传染给旁边的歌手，导致整个合唱团的演出崩溃（这就是量子错误蔓延）。为了防止这种传染，你发明了一个绝妙的办法：把合唱团的每位歌手分别关在一个个绝对隔音的透明玻璃房间里。当你挥动指挥棒时，每个人都按照指令独立改变自己的音调，彼此之间没有任何物理接触。即使某个人生病了，因为隔离玻璃的存在，错误也绝对不会传染给其他人。这种“将一个整体操作拆分成对每个独立个体同时进行、且互不干涉的操作”的模式，就是“Transversal Gate（横向门）”的核心本质。在量子纠错中，为了保护脆弱的量子信息，科学家把一个“逻辑量子比特”（相当于整体合唱团）拆分成好几个“物理量子比特”（相当于每位歌手）的组合。当我们需要对这个逻辑量子比特进行运算时，如果让这些物理量子比特直接互相碰撞着运算，一旦其中一个出错，错误就会像多米诺骨牌一样感染所有人。而“横向门”的做法是：它对由多个物理量子比特组成的逻辑量子比特进行操作时，是“一一对应、平行推进”的。比如逻辑量子比特由物理量子比特A、B、C组成。横向门操作就像是有三只独立的机械手，同时且分别地对A、B、C执行完全相同的动作，而且A、B、C之间绝对不会发生任何交互（即不产生量子纠缠）。这种操作方式天生就切断了错误蔓延的路径，因此它是实现“容错量子计算”的基石。为了让你有更直观的感受，我们可以用isQ量子编程语言来看一下最简单的横向操作逻辑。假设我们用3个物理量子比特来编码1个逻辑量子比特，当我们对它施加一个横向的X门（逻辑翻转）时，其代码逻辑就是单独且均匀地施加操作：

import std;
qbit q[3];
procedure main() {
    // 对3个独立的物理量子比特分别同时施加X门，互不干涉，这就是横向门的基本形态
    for i in 0:3 {
        X(q[i]);
    }
}

正如你在代码中所见，这种“物理隔离”加上“同步同构”的操作，保证了任何一个物理量子比特发生的错误，在经过横向门之后，依然只是单个物理层面上的错误，而不会像病毒一样扩散成无法挽回的灾难。这就是为什么量子物理学家们如此钟爱横向门的原因。

## isqQA/quantum_error_correction/179_isq_demonstration

- task_id: `isqQA/quantum_error_correction/179_isq_demonstration`
- task_type: `qa_concept`
- category: `quantum_error_correction`
- difficulty: `difficult`
- concept_tags: `isq_demonstration`, `concept`, `实时纠错与syndrome解码`
- source: `qa_pipeline`
- dataset_index: `2401`

### Prompt

如何使用isQ语言编写一个量子程序，演示基于三比特位翻转码的实时纠错与Syndrome（伴随式）解码过程？请展示包括逻辑态编码、模拟物理比特翻转错误、通过辅助比特提取Syndrome，以及基于经典测量结果的实时反馈纠错的完整电路代码。

### Reference answer

量子计算在实际运行中极易受到环境噪声的干扰而发生错误。实时量子纠错（QEC）是容错量子计算的核心，其基本思想是引入冗余的物理量子比特来编码逻辑量子比特，并通过测量所谓的伴随式来诊断发生的错误，最后基于经典的实时反馈控制来纠正错误，且在此过程中不破坏编码的逻辑量子态。

三比特位翻转码是最简单的量子纠错码。它将一个逻辑量子比特 $|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$ 编码为三个物理比特的纠缠态 $\alpha|000\rangle + \beta|111\rangle$。如果其中某一个物理比特发生了位翻转错误（X错误），我们可以引入两个辅助比特，分别测量第一、二个物理比特之间的奇偶性（即 $Z_1 Z_2$）以及第二、三个物理比特之间的奇偶性（即 $Z_2 Z_3$）。这两个奇偶校验结果构成了伴随式。如果测量结果为 11，说明第二个物理比特发生翻转；若为 10，说明第一个翻转；若为 01，说明第三个翻转；若为 00，则说明没有错误。得到伴随式后，系统将实时执行相应的X门操作以恢复初始状态。

以下是使用isQ语言实现的完整演示程序：

```isQ
import std;

qbit q[3];
qbit anc[2];

procedure main() {
    // 1. 初始化状态为逻辑叠加态
    // 在 q[0] 上施加 H 门，得到 (|0> + |1>)/sqrt(2)
    H(q[0]);
    
    // 2. 编码过程：利用 CNOT 门生成纠缠态
    // 将状态编码为 (|000> + |111>)/sqrt(2)
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);
    
    // 3. 模拟环境噪声：在第二个物理比特 q[1] 上引入位翻转错误
    X(q[1]);
    
    // 4. Syndrome 提取：通过辅助比特探测错误位置
    // 测量 Z1 Z2 的奇偶性到 anc[0]
    CNOT(q[0], anc[0]);
    CNOT(q[1], anc[0]);
    
    // 测量 Z2 Z3 的奇偶性到 anc[1]
    CNOT(q[1], anc[1]);
    CNOT(q[2], anc[1]);
    
    // 5. 测量辅助比特，获得伴随式
    int s0 = M(anc[0]);
    int s1 = M(anc[1]);
    
    // 6. 经典控制与实时纠错
    // 若伴随式 s0=1, s1=1，表示 Z1Z2=-1 且 Z2Z3=-1，即 q[1] 发生错误
    if (s0 == 1 && s1 == 1) {
        X(q[1]);
    }
    // 若伴随式 s0=1, s1=0，表示 q[0] 发生错误
    if (s0 == 1 && s1 == 0) {
        X(q[0]);
    }
    // 若伴随式 s0=0, s1=1，表示 q[2] 发生错误
    if (s0 == 0 && s1 == 1) {
        X(q[2]);
    }
}
```

代码解析：
1. **量子比特声明**：我们声明了包含3个数据比特的数组 `q[3]` 和2个辅助比特的数组 `anc[2]`。
2. **逻辑编码**：在主程序开始时，首先通过H门将 `q[0]` 置于叠加态，随后使用两个 `CNOT` 门将其扩展为三比特的GHZ态，这实现了量子信息的冗余编码。
3. **模拟错误**：通过直接在 `q[1]` 上调用 `X(q[1])`，我们模拟了一次意外的位翻转错误。这使得量子态从 $\alpha|000\rangle + \beta|111\rangle$ 变成了 $\alpha|010\rangle + \beta|101\rangle$。
4. **伴随式测量**：我们将辅助比特初始化为 $|0\rangle$。第一组 `CNOT(q[0], anc[0])` 和 `CNOT(q[1], anc[0])` 把 $q[0]$ 和 $q[1]$ 的异或值（即 $Z_1 Z_2$ 的本征值）写入了 `anc[0]`。同理，第二组CNOT把 $Z_2 Z_3$ 的本征值写入了 `anc[1]`。
5. **提取结果与实时纠错**：使用 `M()` 操作测量 `anc` 数组，将坍缩后的经典结果保存在 `s0` 和 `s1` 变量中。最后使用 `if` 条件控制语句，根据不同的伴随式结果执行对应的 `X` 门操作。例如，因为错误发生于 `q[1]`，测量结果必为 `s0=1, s1=1`，程序会自动施加 `X(q[1])`，从而完美恢复了原始的纠缠态。

## isqTrain/1771

- task_id: `isqTrain/1771`
- task_type: `code_generation`
- category: `quantum_error_correction`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `3305`

### Prompt

Write isQ code for the following quantum task: 5-qubit repetition code encoding |1>. Perform syndrome measurement on 4 ancilla qubits without introducing any error.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Encode |1⟩ into a 5-qubit repetition code |11111⟩ and verify via syndrome measurement that no bit-flip errors are present.

**Qubits:** 5 data qubits (data[0..4]) encode the logical state; 4 ancilla qubits (anc[0..3]) are measured for the syndrome.

**State evolution:**
- Initial: |00000⟩|0000⟩
- After X(data[0
