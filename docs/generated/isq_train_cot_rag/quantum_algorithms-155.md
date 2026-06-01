# ISQ training COT RAG corpus: quantum_algorithms shard 155

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqQA/quantum_algorithms/124_isq_implementation

- task_id: `isqQA/quantum_algorithms/124_isq_implementation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_implementation`, `algorithm`, `量子随机数生成`
- source: `qa_pipeline`
- dataset_index: `4569`

### Prompt

请解释量子随机数生成的基本原理，并提供一段完整的isQ代码，用于生成一个真正的随机比特（0或1），同时请对代码的每一行进行详细注释。

### Reference answer

<think>
首先，明确问题的核心需求：一是从物理学角度阐释量子随机数的生成原理，二是提供符合语法的isQ代码并逐行注释。

其次，在原理分析阶段，需要对比经典伪随机数，突出量子真随机的优势。核心推导逻辑是将量子比特的初始态|0⟩经过阿达马门（H门）作用，转化为等概率的叠加态，此时测量坍缩得到0或1的概率各为50%，从而保证结果的不可预测性。

接着，在代码实现阶段，需按照isQ语言的语法结构进行设计。第一步是引入标准库以使用内置量子门；第二步声明一个量子比特；第三步应用H门创造叠加态；第四步执行测量操作将量子态转化为经典比特；最后处理并输出结果。

最后，组织解答结构，确保将量子力学概念（叠加与测量）与代码指令（H门与测量操作）严密对应，并为生成的每一行代码构思清晰、易懂的中文注释，以完成最终的回答。
</think>

量子随机数生成是量子计算最基础且最直接的应用之一。它的基本原理建立在量子力学的两个核心概念上：量子叠加和测量坍缩。在经典计算机中，随机数通常是由确定性算法生成的伪随机数，其本质上是可预测的。而在量子系统中，当一个量子比特被制备在等概率的叠加态时，对其进行测量得到的结果是真正不可预测的。

具体而言，量子比特初始状态通常为 |0⟩。当我们对其应用阿达马门（Hadamard Gate, H门）时，其状态会变为：
|ψ⟩ = H|0⟩ = (1/√2)|0⟩ + (1/√2)|1⟩
在这个叠加态中，测量得到 |0⟩（对应经典比特 0）的概率是 |1/√2|² = 0.5，测量得到 |1⟩（对应经典比特 1）的概率也是 0.5。这种由量子力学基本原理保证的 50% 概率分布，为我们提供了真随机性。

以下是使用 isQ 语言实现单比特量子随机数生成器的完整代码及逐行详细注释：

import std;
// 【引入标准库】：isQ 语言的第一行必须是 import std;，它包含了程序运行所需的基本操作、门定义（如 H 门）以及输入输出等标准功能。

qbit q[1];
// 【全局声明量子比特】：在全局范围内声明一个名为 q 的量子寄存器，大小为 1。这意味着我们分配了一个量子比特用于后续的操作。在 isQ 中，量子比特的声明通常放在全局作用域。

procedure main() {
// 【定义主函数】：procedure main() 是 isQ 程序的执行入口点。程序的执行总是从这里开始。

    H(q[0]);
    // 【创建叠加态】：对量子寄存器 q 中的第一个（也是唯一一个）量子比特 q[0] 施加 H 门（阿达马门）。
    // 初始状态下，q[0] 默认处于 |0⟩ 态。H 门的作用是将其转化为等概率的叠加态 (|0⟩ + |1⟩)/√2。
    // 这一步是实现量子随机性的核心步骤，使得该量子比特同时处于 0 和 1 的状态。

    int r = M(q[0]);
    // 【测量与坍缩】：使用测量操作符 M() 对量子比特 q[0] 进行测量。
    // 测量会导致量子态发生坍缩。由于之前处于等概率叠加态，此时有 50% 的概率坍缩到 |0⟩，50% 的概率坍缩到 |1⟩。
    // 测量的结果会被转换为经典整数值（0 或 1），并将其赋值给经典变量 r。
    // 这一步正式提取了量子世界的内秉随机性，生成了一个经典的真随机比特。

    print "Generated random bit: ";
    // 【打印提示信息】：使用 print 语句向控制台输出一段提示文本，告诉用户接下来显示的是生成的随机比特。

    print r;
    // 【输出生成的随机比特】：将存储在经典变量 r 中的测量结果（0 或 1）打印到控制台。
    // 每次运行这段程序，由于量子测量的随机性，这里输出的结果都将是不可预测的 0 或 1。
}
// 【主函数结束】：标志着 main 过程和整个量子程序的结束。

## isqTrain/4095

- task_id: `isqTrain/4095`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `4772`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[4];

unit grover_oracle(qbit q[4]) {
    X(q[2]);
    ctrl<2> CZ(q[0], q[1], q[2], q[3]);
    X(q[2]);
} deriving gate

unit grover_diffusion(qbit q[4]) {
    H(q[0]);
    H(q[1]);
    H(q[2]);
    H(q[3]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    X(q[3]);
    ctrl<2> CZ(q[0], q[1], q[2], q[3]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    X(q[3]);
    H(q[0]);
    H(q[1]);
    H(q[2]);
    H(q[3]);
} deriving gate

procedure main() {
    H(q[0]); H(q[1]); H(q[2]); H(q[3]);
    for i in 0:3 {
        grover_oracle(q);
        grover_diffusion(q);
    }
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

Let me analyze this isQ circuit step by step.

First, let me understand the circuit structure:
1. 4 qubits initialized to |0000>
2. Hadamard gates on all 4 qubits (creates uniform superposition)
3. 4 iterations of Grover's algorithm (oracle + diffusion)
4. Measurement of all qubits

Let me analyze the oracle:

The `ctrl<2> CZ(q[0], q[1], q[2], q[3])` applies a controlled-Z with 2 controls. Looking at the syntax, this seems to be a multi-controlled gate where q[0] and q[1] are controls, and the CZ acts on q[2] and q[3]. But wait, CZ is a two-qubit gate, so this is applying CZ(q[2], q[3]) controlled by q[0] and q[1].

Actually, let me reconsider. The `ctrl<2>` modifier adds 2 control qubits. The CZ gate acts on q[2] and q[3]. So this is a Toffoli-like controlled CZ where q[0] and q[1] are controls, and the CZ is applied to q[2] and q[3] when both controls are |1>.

Wait, CZ applies Z to the target when control is |1>. So CZ(q[2], q[3]) would apply Z to q[3] when q[2] is |1>. With the additional controls from ctrl<2>, this means: apply Z to q[3] when q[0]=1, q[1]=1, AND q[2]=1.

So the oracle marks states where q[0]=1, q[1]=1, q[2]=1 (i.e., |1110> and |1111>). But the X(q[2]) gates before and after flip q[2], so effectively it marks states where q[0]=1, q[1]=1, q[2]=0 (before the X).

Wait, let me trace through more carefully:
- X(q[2]) flips q[2], so |0> -> |1> and |1> -> |0>
- ctrl<2> CZ(q[0], q[1], q[2], q[3]) applies CZ to (q[2], q[3]) when q[0]=1 and q[1]=1
  - This applies Z to q[3] when q[0]=1, q[1]=1, q[2]=1
- X(q[2]) flips q[2] back

So for the original state, the oracle applies a phase flip (-1) to states where:
- q[0]=1, q[1]=1
- After X(q[2]), q[2] becomes |1>, meaning originally q[2] was |0>
- q[3] can be anything (CZ applies Z to q[3] when q[2]=1, but the phase affects the whole state)

Wait, let me think about this more carefully. The ctrl<2> CZ(q[0], q[1], q[2], q[3]) is a controlled-controlled-CZ gate. It applies CZ(q[2], q[3]) when q[0]=1 and q[1]=1. The CZ gate applies a phase of -1 when both q[2]=1 and q[3]=1.

So the marked states are those where q[0]=1, q[1]=1, and after X(q[2]), q[2]=1 and q[3]=1. Since X(q[2]) was applied, originally q[2]=0 and q[3]=1.

So the oracle marks the state |1101> (q[0]=1, q[1]=1, q[2]=0, q[3]=1).

Hmm, let me reconsider the CZ operation. CZ applies Z to the target when the control is |1>. So CZ(q[2], q[3]) applies Z to q[3] when q[2]=|1>. Z gives a phase of -1 when q[3]=|1>.

So the overall effect is:
- Apply phase -1 when q[0]=1, q[1]=1, q[2]=1 (after X on q[2]), q[3]=1
- After X(q[2]), q[2]=1 means originally q[2

### Reference answer

Deterministic output: state |1101> with probability ~0.96

## isqTrain/1279

- task_id: `isqTrain/1279`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1811`

### Prompt

What does this isQ program output when measured?

```isq
import std;

// Triangle (K3) graph state
qbit q[3];

procedure main() {
    // Hadamard on all qubits: create |+>|+>|+>
    H(q[0]); H(q[1]); H(q[2]);
    // CZ for all edges in the triangle
    // Edge (0,1)
    CZ(q[0], q[1]);
    // Edge (1,2)
    CZ(q[1], q[2]);
    // Edge (0,2) completes the triangle
    CZ(q[0], q[2]);
    // Measure in computational (Z) basis
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: `output_prediction` for an isQ quantum program.
    *   Input program: Creates a 3-qubit triangle graph state using H gates on all, then CZ gates on pairs (0,1), (1,2), (0,2), then measures all.
    *   Format: "## Circuit Analysis" section, step-by-step reasoning, Dirac notation, concise (3-15 lines), predicted probability distribution at the end.
    *   Constraints: NO code blocks, start with "## Circuit Analysis", end with predicted probability distribution.

2.  **Analyze the Circuit:**
    *   Initial state: $|000\rangle$
    *   $H(q[0]), H(q[1]), H(q[2]) \rightarrow |+++\rangle = \frac{1}{2\sqrt{2}} \sum_{x \in \{0,1\}^3} |x\rangle$
    *   $CZ(q[0], q[1]) \rightarrow$ applies $(-1)^{q_0 q_1}$ phase. State becomes $\frac{1}{2\sqrt{2}} \sum_{x} (-1)^{q_0 q_1} |x\rangle$.
    *   $CZ(q[1], q[2]) \rightarrow$ applies $(-1)^{q_1 q_2}$ phase. State becomes $\frac{1}{2\sqrt{2}} \sum_{x} (-1)^{q_0 q_1 + q_1 q_2} |x\rangle$.
    *   $CZ(q[0], q[2]) \rightarrow$ applies $(-1)^{q_0 q_2}$ phase. State becomes $\frac{1}{2\sqrt{2}} \sum_{x} (-1)^{q_0 q_1 + q_1 q_2 + q_0 q_2} |x\rangle$.
    *   Look at the amplitudes:
        *   $|000\rangle$: $(-1)^0 = 1$
        *   $|001\rangle$: $(-1)^0 = 1$
        *   $|010\rangle$: $(-1)^0 = 1$
        *   $|011\rangle$: $(-1)^1 = -1$
        *   $|100\rangle$: $(-1)^0 = 1$
        *   $|101\rangle$: $(-1)^1 = -1$
        *   $|110\rangle$: $(-1)^1 = -1$
        *   $|111\rangle$: $(-1)^{1+1+1} = (-1)^3 = -1$
    *   Since every computational basis state has an amplitude of either $1$ or $-1$ (which have magnitude squared $1$), the probability of measuring any specific basis state is $| \pm 1 / (2\sqrt{2}) |^2 = 1/8 = 0.125$.
    *   All 8 outcomes are equally likely.

3.  **Draft the Explanation:**
    *   Start with "## Circuit Analysis".
    *   Step 1: Initialization and H gates transform $|000\rangle$ into $|+++\rangle = \frac{1}{2\sqrt{2}}(|000\rangle + |001\rangle + \dots + |111\rangle)$.
    *   Step 2: The three CZ gates apply a phase of $(-1)$ for each pair of adjacent 1s. The exponent sum is $q_0 q_1 + q_1 q_2 + q_0 q_2$.
    *   Step 3: The final state is an equal superposition of all 8 basis states with amplitudes $\pm 1/2\sqrt{2}$. Specifically: $\frac{1}{2\sqrt{2}}(|000\rangle + |001\rangle + |010\rangle - |011\rangle + |100\rangle - |101\rangle - |110\rangle - |111\rangle)$.
    *   Step 4: Measurement in the Z-basis finds each state with probability $| \pm 1/2\sqrt{2} |^2 = 0.125$.

4.  **Refine and Format:**
    *   Ensure strict compliance with rules: Concise (3-15 lines), correct start/end, no code blocks, Dirac notation.

    *Drafting the actual text:*
    ## Circuit Analysis
    1. The circuit initializes 3 qubits in $|000\rangle$.
    2. Applying Hadamard to all qubits creates an equal

### Reference answer

{'predicted_probs': {'0': 0.12500000000000003, '1': 0.12500000000000003, '2': 0.12500000000000003, '3': 0.12500000000000003, '4': 0.12500000000000003, '5': 0.12500000000000003, '6': 0.12500000000000003, '7': 0.12500000000000003}, 'explanation': 'Parametric variant of isqEval/463. Dimension: predict probabilities for reference circuit.'}

## isqExpand/algo/190

- task_id: `isqExpand/algo/190`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `VQE`, `barren_plateau`, `variational_quantum_algorithms`, `gradient_vanishing`, `optimization`, `quantum_machine_learning`
- source: `isq_expansion_qa`
- dataset_index: `1719`

### Prompt

VQE中的barren plateau问题是什么？它对训练有什么影响？有哪些缓解策略？

### Chain-of-thought reasoning

首先分析问题的三个层面：barren plateau的定义、对训练的影响、缓解策略。Barren plateau是McClean等人在2018年提出的重要概念，指变分量子电路中梯度随量子比特数指数衰减的现象。核心数学描述是Var[∂C/∂θᵢ] ∈ O(1/2ⁿ)。产生原因涉及电路深度、代价函数全局性、纠缠度过高和过参数化。对训练的影响主要体现为梯度消失、优化器失效、可扩展性受限。缓解策略需要从多个角度综述：局部代价函数（Cerezo等2021）、结构化初始化（identity block等）、浅层电路设计、ADAPT-VQE、对称性嵌入、分治策略等。回答需要确保技术准确性和全面性，同时涵盖最新的研究方向。

### Reference answer

Barren Plateau（贫瘠高原）问题是指在变分量子算法（如VQE）中，随着量子电路深度和量子比特数量的增加，损失函数关于变分参数的梯度值呈指数级衰减，导致梯度接近于零的现象。

**核心定义：**
对于一个参数化量子电路 U(θ)，代价函数 C(θ) = ⟨ψ(θ)|H|ψ(θ)⟩ 的偏导数 ∂C/∂θᵢ 的方差随量子比特数 n 指数衰减：
Var[∂C/∂θᵢ] ∈ O(1/2ⁿ)
这意味着在参数空间的大部分区域，梯度几乎为零，形成平坦的"高原"。

**产生原因：**
1. 电路深度过大：随机初始化的深层电路使输出趋于全局酉群上的均匀分布（Haar测度），导致梯度消失。
2. 代价函数的全局性：全局可观测量（如全局哈密顿量）比局部可观测量更容易引发贫瘠高原。
3. 表达能力过强：参数过多时，参数空间中可同时存在指数级数量的"好"解和"坏"解，但绝大多数区域梯度为零。
4. 量子纠缠：过高的纠缠度与贫瘠高原密切相关。

**对训练的影响：**
1. 梯度消失：优化器无法获得有效的梯度信号，参数更新方向随机化。
2. 训练时间指数增长：需要在指数级大的参数空间中搜索非零梯度区域。
3. 经典优化器失效：基于梯度的优化器（如Adam、L-BFGS）失效，无梯度方法也面临采样复杂度指数增长。
4. 可扩展性受限：限制了VQE在中大规模量子比特系统上的实际应用。
5. 随机搜索无异：在贫瘠高原区域，随机搜索与任何优化策略效果相当。

**缓解策略：**

1. **局部代价函数**：使用局部哈密顿量代替全局哈密顿量。研究表明，当代价函数为局部可观测量时，梯度的方差下降速度可从指数级降低到多项式级。

2. **结构化初始参数**：采用特定的参数初始化策略，如 identity block initialization（将初始电路设计为近似恒等操作），使初始状态远离贫瘠高原区域。例如量子自然梯度、layer-wise training。

3. **浅层电路**：限制变分电路的深度，使用较浅的ansatz（如 hardware-efficient ansatz 的浅层版本或问题启发式ansatz如UCCSD），避免过参数化。

4. **参数关联与层间结构**：使用具有物理先验的ansatz结构，如 ADAPT-VQE 逐层构建电路，只添加对梯度贡献最大的算符。

5. **梯度缩放与元学习**：利用量子自然梯度等二阶优化方法，或通过经典预处理识别有希望的参数区域。

6. **利用对称性**：将问题的对称性约束嵌入到电路结构中，减小有效搜索空间。如粒子数守恒、自旋对称性等。

7. **局域性策略**：将大问题分解为小问题分别求解（如分治VQE），每个子问题的量子比特数较少，避开贫瘠高原。

8. **噪声辅助**：在某些情况下，适度的量子噪声反而可以帮助逃离贫瘠高原（虽然有争议），因为噪声可能破坏导致梯度消失的对称性。

9. **量子上采样与方差减少技术**：通过测量策略优化减少梯度估计的方差。

总结来说，贫瘠高原是变分量子算法走向大规模应用的核心障碍之一。目前最有前景的缓解方向包括使用问题启发式浅层ansatz、局部代价函数设计、以及巧妙的参数初始化策略。在实际VQE应用中，通常需要组合多种策略来有效应对这一问题。

## isqTrain/2942

- task_id: `isqTrain/2942`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3358`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
qbit q[6];
procedure main() {
    for i in 0:6 {
        H(q[i]);
    }
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
    M(q[4]);
    M(q[5]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Provide a step-by-step reasoning for a given isQ quantum program.
    *   Output format: Concise, precise, 3-8 lines (for simple circuits), up to 15 lines (for complex). Starts with "## Circuit Analysis". Ends with the predicted probability distribution. Uses Dirac notation.
    *   Input program: A 6-qubit circuit with Hadamard gates on all qubits, followed by measurements on all qubits.

2.  **Analyze the Circuit:**
    *   Qubits: `q[0]` to `q[5]` (6 qubits).
    *   Initialization: `|000000>`
    *   Operations:
        *   Loop `i` from 0 to 5: `H(q[i])`.
    *   State evolution:
        *   Initial state: $|0\rangle^{\otimes 6} = |000000\rangle$
        *   After $H^{\otimes 6}$: The state is an equal superposition of all $2^6 = 64$ computational basis states.
        *   $\frac{1}{\sqrt{2^6}} \sum_{x=0}^{63} |x\rangle = \frac{1}{8} \sum_{x=0}^{63} |x\rangle$
    *   Measurement: Probability of each basis state is $(1/8)^2 = 1/64 = 0.015625$.

3.  **Draft the Explanation:**
    *   Initial state is $|000000\rangle$.
    *   A Hadamard gate $H$ is applied to each of the 6 qubits.
    *   $H|0\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) = |+\rangle$.
    *   The joint state becomes $|+\rangle^{\otimes 6} = \frac{1}{\sqrt{64}} \sum_{x=0}^{63} |x\rangle$.
    *   Measurement probabilities are calculated as the squared magnitude of the amplitude for each state.
    *   Since all 64 basis states have amplitude $1/\sqrt{64} = 1/8$, each has probability $|1/8|^2 = 1/64 \approx 0.015625$.

4.  **Format the Output:**
    *   Start with "## Circuit Analysis".
    *   Ensure it's 3-8 lines.
    *   End with the distribution.

    *Drafting text:*
    ## Circuit Analysis
    1. The circuit initializes 6 qubits in the state |000000>.
    2. A Hadamard (H) gate is applied to each qubit, transforming each |0> to |+> = (|0> + |1>)/√2.
    3. The joint quantum state evolves into an equal superposition of all 64 computational basis states: |ψ> = (1/√64) * Σ|x>.
    4. Since the amplitude for each of the 64 states is 1/8, the probability of measuring any specific basis state is (1/8)² = 1/64.
    5. The measurement probabilities are uniformly distributed across all possible 6-bit strings.

    Predicted probability distribution:
    {'000000': 0.015625, '000001': 0.015625, ... , '111111': 0.015625} (all 64 states have equal probability).

    *Refining according to prompt requirements:* Let's list the exact distribution matching The implementation format, or a representative form. The prompt says "list of probabilities" or "predicted probability distribution". I will just provide a compact representation as it's 64 items, or output the full dict as expected in the reference. Actually, the prompt implies providing exactly the distribution. I will write the compact notation "all 64 computational basis states from |000000> to |111111> have a probability of 0.015625." Let's see if the exact dict format is strictly needed. The "Expected measurement probabilities" in the prompt is a huge dict. I'll output a readable form and note they are all equal to 0.015625.

    Wait, the prompt says "Express your answer as a list of probabilities." and the circuit implementation has the exact dictionary. Let me format the final line as requested.
    Let me write the full dictionary just to be safe, or just state "Each of the 64 states (000000 to 111111) has a probability of 0.015625." The prompt requires ending with "the predicted probability distribution".

### Reference answer

{'predicted_probs': {'000000': 0.015625000000000003, '000001': 0.015625000000000003, '000010': 0.015625000000000003, '000011': 0.015625000000000003, '000100': 0.015625000000000003, '000101': 0.015625000000000003, '000110': 0.015625000000000003, '000111': 0.015625000000000003, '001000': 0.015625000000000003, '001001': 0.015625000000000003, '001010': 0.015625000000000003, '001011': 0.015625000000000003, '001100': 0.015625000000000003, '001101': 0.015625000000000003, '001110': 0.015625000000000003, '001111': 0.015625000000000003, '010000': 0.015625000000000003, '010001': 0.015625000000000003, '010010': 0.015625000000000003, '010011': 0.015625000000000003, '010100': 0.015625000000000003, '010101': 0.015625000000000003, '010110': 0.015625000000000003, '010111': 0.015625000000000003, '011000': 0.015625000000000003, '011001': 0.015625000000000003, '011010': 0.015625000000000003, '011011': 0.015625000000000003, '011100': 0.015625000000000003, '011101': 0.015625000000000003, '011110': 0.015625000000000003, '011111': 0.015625000000000003, '100000': 0.015625000000000003, '100001': 0.015625000000000003, '100010': 0.015625000000000003, '100011': 0.015625000000000003, '100100': 0.015625000000000003, '100101': 0.015625000000000003, '100110': 0.015625000000000003, '100111': 0.015625000000000003, '101000': 0.015625000000000003, '101001': 0.015625000000000003, '101010': 0.015625000000000003, '101011': 0.015625000000000003, '101100': 0.015625000000000003, '101101': 0.015625000000000003, '101110': 0.015625000000000003, '101111': 0.015625000000000003, '110000': 0.015625000000000003, '110001': 0.015625000000000003, '110010': 0.015625000000000003, '110011': 0.015625000000000003, '110100': 0.015625000000000003, '110101': 0.015625000000000003, '110110': 0.015625000000000003, '110111': 0.015625000000000003, '111000': 0.015625000000000003, '111001': 0.015625000000000003, '111010': 0.015625000000000003, '111011': 0.015625000000000003, '111100': 0.015625000000000003, '111101': 0.015625000000000003, '111110': 0.015625000000000003, '111111': 0.015625000000000003}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/3036

- task_id: `isqTrain/3036`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `measurement_order`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3670`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
qbit q[2];
procedure main() {
    nctrl H(q[0], q[1]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

The user wants a circuit analysis for a given isQ quantum program.
The program is:

Wait, `nctrl`? Or is it `ctrl`? Oh, the isQ syntax has `ctrl @[c1, c2] Gate(target);`.
Actually, wait, `nctrl H(q[0], q[1])` might mean "No control" or "negative control"?
Wait, `nctrl` in isQ might mean "negated control"?
Let me recheck standard isQ syntax. I haven't seen `nctrl` but it might be equivalent to applying H on q[0] and q[1] independently?
Ah, wait, `H(q[0], q[1])` is valid in some languages, meaning applying H to multiple qubits. Wait, if it's `H(q[0], q[1])` it means applying H to q[0] and H to q[1]. But `nctrl` is weird.
Let's look at the predicted output: `{'00': 0.4999999999999999, '01': 0.5000000000000001}`
Wait! the predicted output is exactly {'00': 0.5, '01': 0.5}.
If H is applied to q[0] and q[1], the state would be |++> = 0.5|00> + 0.5|01> + 0.5|10> + 0.5|11>, which means probabilities are 0.25 for all.
Why is it {'00': 0.5, '01': 0.5}?
Wait, if H is applied to q[1], and q[0] is |0>, then we have |0> x |+> = 0.707|00> + 0.707|01>. The probabilities would be 0.5 for |00> and 0.5 for |01>.
How does `nctrl H(q[0], q[1])` result in this?
Wait, in isQ, `ctrl` means control. So `nctrl` might be negative control, but `H` takes 1 qubit. If you pass `q[0], q[1]` to `H`, maybe `q[0]` is the control and `q[1]` is the target?
Wait, if `H` takes two qubits, `ctrl` and `nctrl` might be applied implicitly, but here `nctrl H(q[0], q[1])` might mean "apply H to q[1], negatively controlled by q[0]"?
Since q[0] is |0>, a negative control (active when control is |0>) would apply H to q[1].
If q[0] is the control and q[1] is the target, then `nctrl H(q[0], q[1])` applies H to q[1] if q[0] is |0>.
Since q[0] is |0>, H is applied to q[1]. q[0] remains |0>.
The state becomes |0>|+> = 1/sqrt(2) |00> + 1/sqrt(2) |01>.
Measurement probabilities: P(00) = 0.5, P(01) = 0.5.

Let me double check the `nctrl` syntax in isQ.
`nctrl H(q[0], q[1])` means negative control. The first qubit `q[0]` is the control, and `q[1]` is the target. Since the control is |0>, the gate H is applied to `q[1]`.
State evolution:
Initial state: |00>
Gate `nctrl H(q[0], q[1])`: Apply H to `q[1]` because `q[0]` is |0>.
State becomes: |0+> = (|00> + |01>) / sqrt(2).
Measurement probabilities:
|00>: 0.5
|01>: 0.5
|10>: 0
|11>: 0

This perfectly matches the expected measurement probabilities {'00': 0.5, '01': 0.5}.

Let's write down the steps clearly:
1. Initial state is |00> for q[0] and q[1].
2. The `nctrl H(q[0], q[1])` gate applies the H gate to the target qubit (q[1]), controlled by q[0] on the |0> state (negative control).
3. Since q[0] is initially in |0>, the H gate is applied to q[1].
4

### Reference answer

{'predicted_probs': {'00': 0.4999999999999999, '01': 0.5000000000000001}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/3516

- task_id: `isqTrain/3516`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `basis_change`, `interference`
- source: `isq_train_cot`
- dataset_index: `508`

### Prompt

What does this isQ program output when measured?

```
import std;

qbit q[2];

procedure main() {
    X(q[1]);
    H(q[1]);

    H(q[0]);

    CNOT(q[0], q[1]);

    H(q[0]);
    H(q[1]);

    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

Step 1: Initial state is |00>.
Step 2: X(q[1]) transforms state to |01>.
Step 3: H(q[1]) transforms state to (|00> - |10>) / sqrt(2).
Step 4: H(q[0]) transforms state to (|00> + |01> - |10> - |11>) / 2.
Step 5: CNOT(q[0], q[1]) flips q[1] if q[0] is |1>. State becomes (|00> + |01> - |11> - |10>) / 2 = (|00> + |01> - |10> - |11>) / 2. CNOT does nothing because H H on control is basis change, but let's trace carefully.
Wait, let's re-evaluate.
State |00> + |01> - |10> - |11>.
CNOT(q[0], q[1]) applies to this. Let's write state as:
1/sqrt(2) * (|0>_0 (|0>_1 + |1>_1)/sqrt(2) - |1>_0 (|0>_1 + |1>_1)/sqrt(2))
This is 1/sqrt(2) * (|0> - |1>)_0 * |+>_1.
CNOT(q[0], q[1]) flips the target (q[1]) if control (q[0]) is |1>.
Resulting state: 1/sqrt(2) * (|0>_0 |+>_1 - |1>_0 |->_1).
Let's expand:
|+> = |0> + |1>, |-> = |0> - |1>.
State: 1/sqrt(2) * (|00> + |01> - |10> + |11>).
Step 6: H(q[0]) applies H to q[0].
H|0> = |+>, H|1> = |->
State: 1/2 * ((|0> + |1>)|+> - (|0> - |1>)|->)
= 1/2 * (|0>|+> + |1>|+> - |0>|-> + |1>|->)
= 1/2 * (|0>(|+> - |->) + |1>(|+> + |->))
Since |+> + |-> = |0>, and |+> - |-> = |1>.
Wait, (|0>+|1>) + (|0>-|1>) = 2|0>.
So State = 1/2 * (|0>|1> + |1>|0>) = (|01> + |10>) / 2.
Step 7: H(q[1]) applies H to q[1].
State = 1/2 * (|0> H|1> + |1> H|0>)
= 1/2 * (|0> |-> + |1> |+>)
= 1/2 * (|0>(|0>-|1>) + |1>(|0>+|1>))
= 1/2 * (|00> - |01> + |10> + |11>).

Let me double check the calculation.
1. |00>
2. X(q[1]) -> |01>
3. H(q[1]) -> |0>(|0>-|1>)/sqrt(2) = |0>|-> = (|00> - |01>)/sqrt(2).
Ah! I made a mistake in step 3.
Let's restart.
Initial: |00>
X(q[1]) -> |01>
H(q[1]) -> |0>(|0>-|1>)/sqrt(2) = (|00> - |01>)/sqrt(2).
H(q[0]) -> (|0>+|1>)/sqrt(2) * (|0>-|1>)/sqrt(2) = (|00> - |01> + |10> - |11>) / 2.
CNOT(q[0], q[1]) -> (|00> - |01> + |11> - |10>) / 2.
= (|00> - |01> - |10> + |11>) / 2.
= (|0>-|1>)/sqrt(2) \otimes (|0>-|1>)/sqrt(2).
= |->|->.
H(q[0]) -> Z|-> = -|1> ? Wait, H|-> = |1>.
H(q[1]) -> H|-> = |1>.
So state becomes |1>|1> = |11>.
Let's re-verify H|

### Reference answer

{'predicted_probs': {'11': 1.0}, 'explanation': 'The output is |11> with probability 1.0'}

## isqTrain/69

- task_id: `isqTrain/69`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `379`

### Prompt

用isQ实现implements a variant of the bell_state_preparation pattern using q[2] -> q[4]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for a quantum circuit written in isQ. Let me analyze The implementation.

Looking at the circuit:
1. We have `qbit q[4];` - a 4-qubit register
2. The circuit creates an EPR pair between q[0] and q[1], then encodes "11", then decodes.

Let me trace through the state evolution:

Initial state: |0000>

After H(q[0]): (|0> + |1>)/√2 ⊗ |000> = (|0000> + |1000>)/√2

After CNOT(q[0], q[1]): (|0000> + |1100>)/√2

After Z(q[0]): (|0000> - |1100>)/√2

After X(q[0]): (|1000> - |0100>)/√2

Wait, let me recalculate. X flips the qubit:
- |0> -> |1>
- |1> -> |0>

So after X(q[0]) on (|0000> - |1100>)/√2:
= (|1000> - |0100>)/√2

Hmm, that doesn't seem right for getting |1100> at the end.

Let me re-trace more carefully:

Initial: |0000>

H(q[0]): (|0> + |1>)/√2 ⊗ |000> = (|0000> + |1000>)/√2

CNOT(q[0], q[1]): (|0000> + |1100>)/√2

This is the Bell state |Φ+>

Z(q[0]): (|0000> - |1100>)/√2

This is |Φ->

X(q[0]): (X on q[0])
X|0> = |1>
X|1> = |0>

So (|0000> - |1100>)/√2 becomes (|1000> - |0100>)/√2

This is |Ψ-> (negated) for qubits 0 and 1.

CNOT(q[0], q[1]):
When q[0]=1, flip q[1]:
|1000> -> |1100>
When q[0]=0, don't flip:
|0100> -> |0100>

Wait, I need to be careful about which qubit is which.

Let me label: |q3 q2 q1 q0>

Initial: |0000>

H(q[0]): q0 becomes (|0>+|1>)/√2
State: (|0000> + |0001>)/√2

CNOT(q[0], q[1]): control=q[0], target=q[1]
When q[0]=1, flip q[1]:
(|0000> + |0110>)/√2

Hmm, this doesn't match typical Bell state notation. Let me use |q0 q1 q2 q3> ordering (q[0] is leftmost).

Initial: |0000>

H(q[0]): (1/√2)(|0000> + |1000>)

CNOT(q[0], q[1]): (1/√2)(|0000> + |1100>)

Z(q[0]): (1/√2)(|0000> - |1100>)

X(q[0]): (1/√2)(|1000> - |0100>)

CNOT(q[0], q[1]): 
When q[0]=1, flip q[1]: |1000> -> |1100>
When q[0]=0, don't flip: |0100> stays |0100>

(1/√2)(|1100> - |0100>)

H(q[0]):
H on q[0]:
H|1> = (|0> - |1>)/√2
H|0> = (|0> + |1>)/√2

(1/√2)((|0100> - |1100>)/√2 - (|0100> + |1100>)/√2)

Wait, let me redo this. The state before H(q[0]) is:
(1/√2)(|1100> - |0100>)

Applying H to q[0]:
|1100> -> (|0> - |1>)/√2 ⊗ |100> = (|0100> - |1100>)/√2
|0100> -> (|0> + |1>)/√2 ⊗ |100> = (|0100> + |1100>)/√2

So the final state:
(1

## isqTrain/681

- task_id: `isqTrain/681`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `ancilla_usage`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2411`

### Prompt

Code this in isQ: implements the half_full_adder pattern. Include explicit identity operations in the circuit (X-X pair before M(q[2])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Implement a half/full adder computing sum (XOR) and carry (AND) for inputs a=1, b=1, with explicit X-X identity pair demonstrating gate cancellation awareness.
2. **Qubits:** 4 qubits—q[0], q[1] as inputs, q[2] for sum, q[3] for carry. Measuring q[2] and q[3].
3. **State evolution:**
   - |0000⟩ → X(q[0]), X(q[1]) → |1100⟩ (inputs set to |1⟩,|1⟩)
   - CNOT(q[0], q[2]) → |1110⟩ (control=1 flips target)
   - CNOT(q[1], q[2]) → |1000⟩ (second XOR flips sum back to |0⟩)
   - Toffoli(q[0], q[1], q[3]) → |1001⟩ (both controls=1 sets carry=1)
   - X(q[2]) → |1101⟩, then X(q[2]) → |1001⟩ (X-X pair cancels to identity)
4. **Final state:** |1001⟩ → measuring q[2]=0 (sum), q[3]=1 (carry) yields |01⟩ with probability 1.0.

## isqTrain/318

- task_id: `isqTrain/318`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `entanglement`, `interference`, `isq_syntax_arrays`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1387`

### Prompt

帮我写一个isQ程序：implements a variant of the oracle_boolean pattern using a[1] -> a[2]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

Analyzing the given isQ program:

**Goal**: This implements a Deutsch-Jozsa-like oracle circuit that encodes a constant function into an expanded 3-qubit register system.

**Qubits**: 5 total qubits: `q[0]`, `q[1]`, `q[2]` (measured), and `a[0]`, `a[1]` (ancilla, not measured).

**Step-by-step state evolution**:

1. **Initial state**: |00000⟩ (all qubits in |0⟩)

2. **X(a[0])**: Flips ancilla a[0] to |1⟩
   State: |00001⟩ (where ordering is q[2], q[1], q[0], a[1], a[0] → but let me be careful with ordering)

3. **H(a[0])**: Puts ancilla in superposition
   State for a[0]: (|0⟩ - |1⟩)/√2
   Full state: |000⟩ ⊗ |0⟩ ⊗ (|0⟩ - |1⟩)/√2

4. **H(q[0]), H(q[1]), H(q[2])**: Hadamard on all three q-register qubits
   Each goes to |+⟩ = (|0⟩ + |1⟩)/√2
   State: |+++⟩ ⊗ |0⟩ ⊗ (|0⟩ - |1⟩)/√2

5. **my_oracle()**: 
   - CNOT(q[0], a[0]): Controlled on q[0], flips a[0]
   - CNOT(q[1], a[0]): Controlled on q[1], flips a[0]
   
   Since a[0] is in (|0⟩ - |1⟩)/√2, flipping it changes sign: (|0⟩ - |1⟩)/√2 → (|1⟩ - |0⟩)/√2 = -(|0⟩ - |1⟩)/√2
   
   Two CNOTs with controls q[0] and q[1]:
   - When q[0] = |1⟩ and q[1] = |0⟩: one flip → phase of -1
   - When q[0] = |0⟩ and q[1] = |1⟩: one flip → phase of -1
   - When q[0] = |1⟩ and q[1] = |1⟩: two flips → phase of +1
   - When q[0] = |0⟩ and q[1] = |0⟩: no flips → phase of +1
   
   This is phase kickback. The oracle computes f(q[0], q[1]) = q[0] ⊕ q[1], applying a phase of (-1)^f.

6. **H(q[0]), H(q[1]), H(q[2])**: Hadamard on all three q-register qubits again

   After the oracle, the state of q[0], q[1] is:
   (1/2)[|00⟩ + |01⟩(-1) + |10⟩(-1) + |11⟩(+1)] ⊗ |+⟩ ⊗ |a⟩
   
   = (1/2)[|00⟩ - |01⟩ - |10⟩ + |11⟩] ⊗ |+⟩ ⊗ |a⟩

   Applying H⊗H to q[0], q[1]:
   H⊗H |00⟩ = |++⟩
   H⊗H |01⟩ = |+-⟩
   H⊗H |10⟩ = |-+⟩
   H⊗H |11⟩ = |--⟩

   So: (1/2)[|++⟩ - |+-⟩ - |-+⟩ + |--⟩]
   
   Let me compute this more carefully:
   
   |++⟩ = (|00⟩+|01⟩+|10⟩+|11⟩)/2
   |+-⟩ = (|00⟩-|01⟩+|10⟩-|11⟩)/2
   |-+⟩ = (|00⟩+|01⟩-|10⟩-|11⟩)/2
   |--⟩ = (|00⟩-|01⟩-|10⟩+|11⟩)/2

   (1/2)[|++⟩ - |+-⟩ - |-+⟩ + |--⟩]
   = (1/4)[(|00⟩+|01⟩+|10⟩+|11⟩) - (|00⟩-|01⟩+|10⟩-|11⟩) - (|00⟩+|01⟩-|10⟩-|11⟩) + (|00⟩-|01⟩-|10⟩+|11⟩)]
   
   q[0] coefficient for |
