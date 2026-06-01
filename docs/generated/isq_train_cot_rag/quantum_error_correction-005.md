# ISQ training COT RAG corpus: quantum_error_correction shard 5

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1343

- task_id: `isqTrain/1343`
- task_type: `output_prediction`
- category: `quantum_error_correction`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5252`

### Prompt

What does this isQ program output when measured?

```isq
import std;

qbit q[4];

procedure main() {

    X(q[0]);

    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. Initial state is |0000>.
2. `X(q[0])` flips q[0] to |1>, changing the state to |1000>.
3. `CNOT(q[0], q[1])` entangles q[1] with q[0]. Since q[0] is |1>, q[1] flips to |1>, yielding |1100>.
4. `CNOT(q[0], q[2])` flips q[2] because q[0

### Reference answer

{'predicted_probs': {'14': 1.0}, 'explanation': 'Parametric variant of isqEval/489. Dimension: qubit_variant: q[3] -> q[4].'}

## isqQA/quantum_error_correction/179_depth_progression

- task_id: `isqQA/quantum_error_correction/179_depth_progression`
- task_type: `qa_concept`
- category: `quantum_error_correction`
- difficulty: `difficult`
- concept_tags: `depth_progression`, `concept`, `实时纠错与syndrome解码`
- source: `qa_pipeline`
- dataset_index: `4722`

### Prompt

在表面码的量子纠错中，当我们同时考虑数据量子比特发生的物理错误以及辅助比特测量过程中的读出错误时，综合征的解码将面临什么核心挑战？应如何构建三维时空匹配图来解决这一问题？此外，请用isQ代码展示一个包含两轮测量的简单三比特重复码综合征提取过程，并在其中一轮人为引入测量错误，以说明累积多次测量的必要性。

### Reference answer

在表面码等拓扑量子纠错方案中，数据量子比特的物理退相干和辅助比特的测量错误是叠加在一起发生的。核心挑战在于：如果解码器仅仅依赖单次测量的综合征结果，它将无法区分某个“违规”是由真实的数据错误引起的，还是由一次随机的测量读出错误引起的。如果因为测量错误而错误地施加了物理纠正操作，反而会在系统中引入原本不存在的逻辑错误。

为了解决这一问题，我们需要将二维的空间晶格扩展为三维的时空匹配图。在这个三维图中，X轴和Y轴代表量子比特在芯片上的物理位置（空间维度），而Z轴代表时间维度（即连续的纠错周期）。每一层对应一个纠错周期的稳定子测量结果。在这个三维图中，边被分为两类：一类是同一时间切片内的“空间边”，代表相邻稳定子之间可能发生的数据错误；另一类是连接两个相邻时间切片中同一稳定子的“时间边”，代表该稳定子在连续两次测量中可能发生的测量错误。

通过比较连续多个周期的测量结果，如果某个稳定子的结果在某一时刻发生了翻转，但在下一个时刻立刻又翻转回来，解码器会倾向于认为这是一次测量错误，并在三维图中通过沿时间轴的短距离匹配来消除它。相反，如果错误持续存在，则会被视为真实的数据错误并沿空间轴进行匹配。这种时空映射使得像最小权重完美匹配（MWPM）这样的算法能够准确推断出底层物理错误的演化轨迹。然而，这也给实时解码器带来了巨大的计算压力，因为三维图的节点数随时间线性增长，这就是为什么当前工业界迫切需要研究具有近线性时间复杂度的实时解码算法（如Union-Find解码器）。

为了更直观地理解累积测量如何对抗测量错误，我们可以通过一个三比特重复码的例子来说明。以下isQ代码模拟了连续两轮的综合征提取，并在第一轮提取后人为引入了一个测量错误：

```isQ
import std;

const int N = 3;
qbit data[N]; // 数据比特
qbit anc[2]; // 用于两轮提取的辅助比特

procedure main() {
    // 初始化逻辑|1>状态：即|111>
    for i in 0:N {
        X(data[i]);
    }

    // === 第一轮综合征提取 ===
    // 将data[0]和data[1]的奇偶性纠缠到辅助比特anc[0]上
    CNOT(data[0], anc[0]);
    CNOT(data[1], anc[0]);
    
    // 人为模拟测量错误：在测量前对辅助比特施加X门
    // 这将导致第一轮的经典读数 r0 翻转
    X(anc[0]);
    
    int r0 = M(anc[0]); // 假设此时发生错误，读数为1

    // === 第二轮综合征提取 ===
    // 使用新的辅助比特anc[1]进行同样的奇偶性测量
    CNOT(data[0], anc[1]);
    CNOT(data[1], anc[1]);
    
    // 第二轮不施加任何错误
    int r1 = M(anc[1]); // 因为数据未发生错误，正确测量应为0

    // 实时解码器的逻辑判断：
    // r0 = 1 (异常), r1 = 0 (恢复正常)
    // 时空匹配图发现异常只存在于一轮切片中，判定为测量错误。
    // 因此，尽管第一轮综合征报错，解码器决定不执行任何纠正操作。
    if (r0 == 1) {
        // 若缺乏时序信息，单轮解码器可能会错误地执行 X(data[0])，
        // 但基于时空图的双轮解码器将放弃在此处操作。
    }
}
```
通过上述机制，实时纠错系统能够在充斥着量子噪声与经典测量噪声的复杂环境中，鲁棒地守护量子信息的完整性。

## isqExpand/qa/63

- task_id: `isqExpand/qa/63`
- task_type: `qa_concept`
- category: `quantum_error_correction`
- difficulty: `difficult`
- concept_tags: `fault_tolerance`, `transversal_gate`, `error_propagation`, `quantum_error_correction`, `eastin_knill_theorem`
- source: `qa_pipeline`
- dataset_index: `4903`

### Prompt

什么是容错量子计算？transversal gate（横向门/跨越门）为什么对容错量子计算非常重要？

### Chain-of-thought reasoning

## 推理
1. **拆解提示词**：用户询问两个核心概念，一是“容错量子计算”的定义，二是“transversal gate”为什么对容错很重要。这属于概念解释题型。
2. **概念解析 - 容错量子计算**：需要明确仅仅有量子纠错码（QEC）是不够的，如果在操作时出错并扩散，纠错码也会失效。因此，容错架构的核心是防止错误在计算过程中不受控地扩散和放大。
3. **概念解析 - Transversal Gate**：首先给出其数学或物理定义，即操作仅发生在对应编号的物理比特之间，呈张量积形式。用数学公式表达即 $U_L = \bigotimes_{i=1}^n U_i$。
4. **建立因果联系（为什么重要）**：这是回答的重点。错误扩散是破坏码距的元凶。由于横向门没有块内交叉操作，单个组件的物理错误只能停留在局部或一对一传到下一个块的对应位置，这就把错误数量限制在纠错码的处理能力之内（即不降低码距），从而保证了容错性。
5. **举例与代码结合**：使用最直观的3比特翻转码作为背景。通过 isQ 代码展示 `q1[3]` 和 `q2[3]` 之间的逐位 CNOT 操作，这完美诠释了横向门“不交叉”的特点。
6. **拓展深度**：为了展现专家水平，应当提及 Eastin-Knill 定理。指出虽然横向门非常好，但没有任何一种纠错码可以仅靠横向门实现通用量子计算，顺带引出魔法态提纯等现实方案。这使答案更加严谨和完整。
7. **规范检查**：公式使用标准 LaTeX；isQ 代码符合规范且无 `SWAP` 等禁用指令；输出结构为不带 markdown 格式的 JSON。

### Reference answer

容错量子计算（Fault-Tolerant Quantum Computing, FTQC）是量子计算领域为了克服量子比特易受噪声干扰、容易发生退相干和操作错误而提出的一种架构设计理念。由于物理量子比特的错误率通常远高于经典计算机，如果我们直接在物理比特上运行长量子的算法（如Shor算法），计算结果会被噪声完全淹没。量子纠错码（QEC）通过将一个逻辑量子比特编码到多个物理量子比特中（例如 $|0_L\rangle$ 和 $|1_L\rangle$）来保护量子信息。然而，仅仅有编码是不够的，因为在进行量子门操作时，如果操作本身引发了错误，且该错误在纠错码块内部扩散，就会超出码的纠错能力。容错量子计算的核心目标就是设计一套规则和电路，使得即使在量子门、测量、或者制备过程中存在物理错误，这些错误也没有机会在系统内不受控地大量扩散和放大，从而确保逻辑计算层面的正确性。

Transversal gate（横向门）是实现容错量子计算的关键机制之一。对于一个将 $k$ 个逻辑量子比特编码到 $n$ 个物理量子比特的纠错码，如果一个逻辑门被实现为多个独立的物理量子门的张量积，且这些物理门仅分别作用于各自对应的物理比特，那么这个逻辑门就被称为 transversal gate。

例如，对于两个逻辑比特之间的 transversal CNOT 门，其对应的物理操作是第一个逻辑块中的第 $i$ 个物理比特控制第二个逻辑块中的第 $i$ 个物理比特，且没有任何其他的交叉作用。其数学表达式可以写为：
$$ \text{CNOT}_L = \bigotimes_{i=1}^n \text{CNOT}_{c_i \to t_i} $$

Transversal gate 对容错量子计算至关重要，主要原因在于其完美的**错误抑制与隔离特性**：
1. **防止错误扩散（Error Propagation）**：由于 transversal gate 在物理比特之间没有任何内部的交叉连接，一个物理比特上发生的错误（如 $X$ 错误或 $Z$ 错误）绝不会传播到同一个纠错码块内的其他物理比特上。对于两比特门，控制比特的错误虽然会传播到目标比特，但也仅限于目标块中对应位置的物理比特（即从 $c_i$ 传到 $t_i$），不会造成码块内部的连锁反应。
2. **保留距离**：量子纠错码的纠错能力取决于它的码距 $d$（最多可以纠正 $\lfloor (d-1)/2 \rfloor$ 个错误）。如果一次门操作导致一个物理错误变成了两个或更多物理错误，码距就会迅速被耗尽。Transversal 操作确保了单个故障点只会导致少量的错误（通常在每一块中至多产生一个错误），这使得纠错码在下一次纠错周期中能够轻易地将其捕获并纠正。

为了更直观地理解，我们可以用 isQ 代码来演示如何在一个基于3比特比特翻转码的容错架构中实现 Transversal CNOT 门。这种实现方式确保了控制寄存器和目标寄存器之间是对位独立作用的：

```isq
import std;

// 声明控制逻辑比特q1和目标逻辑比特q2，各包含3个物理比特
qbit q1[3];
qbit q2[3];

procedure main() {
    // 假设 q1 已经被编码为逻辑态 |1_L> = |111>
    X(q1[0]);
    X(q1[1]);
    X(q1[2]);
    
    // 假设 q2 初始被编码为逻辑态 |0_L> = |000>
    // 在真实的容错电路中，状态通常是通过容错状态制备生成的

    // 执行 Transversal CNOT 门
    // 只有对应下标的物理比特发生相互作用
    CNOT(q1[0], q2[0]);
    CNOT(q1[1], q2[1]);
    CNOT(q1[2], q2[2]);
    
    // 此时 q2 应该被翻转为 |111>，即逻辑 |1_L>
    // 如果在执行 CNOT(q1[1], q2[1]) 时发生了一个物理错误
    // 该错误只会停留在 q1[1] 和 q2[1] 上，绝不会污染 q1[0] 或 q2[2]
}
```

值得注意的是，Eastin-Knill 定理指出，对于任何一种具有通用纠错能力的量子纠错码，不可能所有的逻辑门都能用 transversal 的方式实现。因此，在现实的容错量子计算方案（如表面码）中，通常大部分门（如 Clifford 门）使用横向门实现，而少数非横向的逻辑门（如 T 门）则必须通过引入“魔法态提纯”等特殊的容错协议来安全实现。

## isqQA/quantum_error_correction/158_depth_progression

- task_id: `isqQA/quantum_error_correction/158_depth_progression`
- task_type: `qa_concept`
- category: `quantum_error_correction`
- difficulty: `intermediate`
- concept_tags: `depth_progression`, `concept`, `量子纠错为什么比经典纠错难`
- source: `qa_pipeline`
- dataset_index: `1085`

### Prompt

在经典纠错中，我们只需复制比特并检查是否一致。而在量子纠错中，既然连续的微小旋转错误（如 $R_x(\theta)$）在物理上是连续且不可预测的，且受不可克隆定理限制我们无法复制未知量子态，那么量子纠错码（如Shor码或表面码）究竟是如何在不引起波函数坍缩的前提下，将这种连续错误离散化并提取出离散的错误伴随式（syndrome）的？请从数学原理和量子测量的本质进行深入剖析，并用isQ代码展示一个简单的错误投影过程。

### Reference answer

<thought>这个问题触及了量子纠错的核心理论基石——错误离散化。我需要首先解释量子态的线性叠加性质如何将连续的错误转化为离散子空间的叠加，然后解释投影测量（提取伴随式）如何将连续参数转化为概率分布并最终迫使系统坍缩到离散错误态上。接着澄清保距测量如何在不获取量子态信息的情况下获取错误信息。最后使用isQ代码展示一个3比特位翻转码中施加连续旋转并准备进行离散投影的基础结构。</thought>

这是一个非常深刻的追问。量子纠错之所以能够克服看似无法逾越的“不可克隆定理”和“连续错误”两大障碍，其核心物理和数学基石在于**错误离散化**与**量子态的线性叠加原理**。以下是具体的机制剖析：

1. **连续错误的离散化（数学原理）**
假设我们使用一个简单的3量子比特位翻转码来保护逻辑态 $|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$。编码后系统状态为 $\alpha|000\rangle + \beta|111\rangle$。
如果在第一个量子比特上发生了一个微小的连续旋转错误 $R_x(\theta)$，这在数学上可以展开为：
$R_x(\theta)|0\rangle \approx \cos(\frac{\theta}{2})|0\rangle - i\sin(\frac{\theta}{2})|1\rangle$
$R_x(\theta)|1\rangle \approx \cos(\frac{\theta}{2})|1\rangle - i\sin(\frac{\theta}{2})|0\rangle$
当这个错误作用在编码态上时，根据量子力学的线性性质，系统的整体状态变为：
$|\Psi_{err}\rangle = \cos(\frac{\theta}{2})(\alpha|000\rangle + \beta|111\rangle) - i\sin(\frac{\theta}{2})(\alpha|100\rangle + \beta|011\rangle)$
注意这里的奇妙之处：连续的参数 $\theta$ 并没有产生无穷多种不同的量子态，而是变成了两个正交子空间的线性组合：一个是“没有错误”的子空间（$I$ 作用），另一个是“发生位翻转”的子空间（$X_1$ 作用）。

2. **投影测量与伴随式提取（测量本质）**
为了纠正错误，我们需要测量系统的伴随式。在量子纠错中，我们测量的不是量子比特本身的值（这会破坏 $\alpha$ 和 $\beta$ 导致波函数坍缩），而是测量一组特定的厄米算符（稳定子生成元）。
上述例子中，我们会测量 $Z_1 Z_2$ 和 $Z_2 Z_3$。由于“无错误”态和“第一位翻转”态是这两个算符的本征态，且对应不同的本征值，量子力学的**投影公设**在这里发挥了作用：
当我们进行这种多维度的保距测量时，量子态会以 $\cos^2(\frac{\theta}{2})$ 的概率坍缩到无错误子空间，或以 $\sin^2(\frac{\theta}{2})$ 的概率坍缩到 $X_1$ 错误子空间。
一旦测量完成，连续的角度 $\theta$ 就被彻底“抹去”了，系统明确地告诉测量仪器：“我要么没发生错误，要么发生了一个完整的位翻转错误”。这就像将一把连续的尺子变成了离散的开关。

3. **不泄露逻辑信息的保护机制**
因为稳定子测量 $Z_i Z_j$ 只能分辨出两个量子比特是否相同，它们完全无法区分 $|000\rangle$ 和 $|111\rangle$（这两者在没有错误时给出相同的伴随式）。因此，我们提取出的仅仅是“错误发生的位置”这一经典伴随式信息，而关于 $\alpha$ 和 $\beta$ 的量子叠加信息被完好无损地封锁在了正交的编码子空间中。

下面是使用isQ语言展示的一个简单3比特位翻转码的编码与连续错误施加的物理过程。该代码演示了如何将逻辑信息编码进更大的纠缠空间中，以备后续提取离散的伴随式信息：

```isQ
import std;

qbit q[3];

procedure main() {
    // 假设我们要保护一个叠加态 |psi> = alpha|0> + beta|1>
    // 为了演示，我们这里以 |+> 态为例准备初始逻辑态
    H(q[0]);
    
    // 步骤1：将逻辑态编码到3个物理比特中 (|000> + |111>) / sqrt(2)
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);
    
    // 步骤2：模拟环境引入了一个连续的微小旋转错误
    // 假设在第0个比特上发生了角度为 0.3 的 X 轴连续旋转
    Rx(0.3, q[0]);
    
    // 此时量子态变为无错误空间与 X_0 错误空间的连续叠加
    // 在真实的量子纠错电路中，接下来会引入辅助比特
    // 并进行受控测量提取伴随式，迫使连续状态坍缩为离散错误。
    // （由于isQ标准测量是对单个比特投影，此处省略完整伴随式提取步骤，
    // 仅演示连续错误在离散化前的核心物理结构）
}
```
总结而言，量子纠错之所以比经典纠错更深奥，是因为它利用了希尔伯特空间的几何结构，将连续的物理演化和离散的逻辑表征统一起来，通过线性代数和量子测量公设的巧妙结合，实现了不违背不可克隆定理的“隐式”查错与纠错。

## isqQA/quantum_error_correction/166_isq_demonstration

- task_id: `isqQA/quantum_error_correction/166_isq_demonstration`
- task_type: `qa_concept`
- category: `quantum_error_correction`
- difficulty: `intermediate`
- concept_tags: `isq_demonstration`, `concept`, `码距与纠错能力`
- source: `qa_pipeline`
- dataset_index: `978`

### Prompt

请解释量子纠错中“码距”的概念及其与量子态纠错能力之间的数学关系，并使用isQ量子编程语言编写一个展示三位重复码的量子电路程序。该程序需能够编码一个逻辑量子比特，人为引入一个单比特翻转错误，随后通过测量错误伴随式进行错误检测和纠正。

### Reference answer

<think 
1. **概念解析与关系**：
   - **码距**：在量子纠错码中，码距$d$是指将一个合法的码字变成另一个合法码字所需改变的最少物理量子比特数目。在数学上，它对应于稳定子生成元的最小权重（即参与作用的非恒等算符的最小数量）。
   - **纠错能力**：根据经典和量子纠错理论，如果一个量子纠错码的码距为$d$，那么它可以检测出最多$d-1$个任意位置的量子比特错误，并且能够纠正最多$t = \lfloor(d-1)/2\rfloor$个错误。
   - **三位重复码**：它是一种码距$d=3$的简单量子纠错码。由于$d=3$，它可以纠正$t = \lfloor(3-1)/2\rfloor = 1$个比特翻转(X)错误。其逻辑态编码为：$|0\rangle_L = |000\rangle$, $|1\rangle_L = |111\rangle$。

2. **isQ代码构建逻辑**：
   - **初始化与编码**：声明3个数据量子比特`q[3]`和2个用于测量的辅助量子比特`a[2]`。通过将第一个量子比特的状态通过两个CNOT门复制到第二和第三个量子比特上来实现编码。
   - **模拟错误**：在任意一个物理量子比特（如`q[1]`）上人为施加一个X门，模拟单比特翻转错误。
   - **伴随式测量**：利用辅助比特检测哪一位发生了翻转。通过`CNOT(q[0], a[0])`和`CNOT(q[1], a[0])`比较`q[0]`和`q[1]`的奇偶性；通过`CNOT(q[1], a[1])`和`CNOT(q[2], a[1])`比较`q[1]`和`q[2]`的奇偶性。
   - **错误纠正**：测量辅助比特`a[0]`和`a[1]`，根据测量结果（伴随式）精确判定错误位置并施加对应的X门进行恢复。
</think

在量子计算中，**码距**是衡量量子纠错码鲁棒性的核心指标。它被定义为将一个合法的量子码字转变为另一个合法码字所需改变的最少物理量子比特数。在量子错误信道中，码距$d$直接决定了码的**纠错能力**：一个码距为$d$的量子纠错码，最多可以检测出$d-1$个错误，并最多可以纠正$t = \lfloor (d-1)/2 \rfloor$个任意位置的物理比特错误。

以最简单的**三位比特翻转码**为例，其逻辑零态和逻辑一态分别被编码为 $|0\rangle_L = |000\rangle$ 和 $|1\rangle_L = |111\rangle$。在这个系统中，任意改变1个比特（例如从$|000\rangle$变为$|010\rangle$）都不会使其变成另一个合法的逻辑状态。要使$|000\rangle$完全变为$|111\rangle$，至少需要改变3个物理比特，因此该码的码距为$d=3$。根据公式，$t = \lfloor(3-1)/2\rfloor = 1$，这意味着它具备纠正任意1个物理比特发生翻转错误的能力。

以下是用 isQ 量子编程语言实现该编码、单比特错误模拟及纠正电路的完整代码：

```isq
import std;

// 声明3个物理数据比特和2个用于伴随式测量的辅助比特
qbit q[3];
qbit a[2];

procedure main() {
    // 1. 编码阶段
    // 假设我们需要编码逻辑态 |1>_L = |111>
    // 初始化物理比特0为|1>，其余默认为|0>
    X(q[0]);
    // 通过CNOT门生成纠缠态，完成三位重复码编码
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);

    // 2. 模拟噪声环境中的单比特翻转错误
    // 假设第2个物理比特(索引为1)发生了翻转错误
    X(q[1]);

    // 3. 错误检测阶段 (伴随式提取)
    // 辅助比特 a[0] 检测 q[0] 和 q[1] 之间的奇偶性差异
    CNOT(q[0], a[0]);
    CNOT(q[1], a[0]);
    
    // 辅助比特 a[1] 检测 q[1] 和 q[2] 之间的奇偶性差异
    CNOT(q[1], a[1]);
    CNOT(q[2], a[1]);

    // 4. 错误诊断与纠正阶段
    // 测量辅助比特以获取错误伴随式
    int r0 = M(a[0]);
    int r1 = M(a[1]);

    // 根据测量结果定位并纠正错误
    // r0=1, r1=0: 说明 q[0] 和 q[1] 不同，但 q[1] 和 q[2] 相同 -> q[0] 错误
    if (r0 == 1) {
        if (r1 == 0) {
            X(q[0]); // 纠正 q[0]
        } 
        // r0=1, r1=1: 说明 q[0] 和 q[1] 不同，且 q[1] 和 q[2] 不同 -> q[1] 错误
        else {
            X(q[1]); // 纠正 q[1]
        }
    } else {
        // r0=0, r1=1: 说明 q[0] 和 q[1] 相同，但 q[1] 和 q[2] 不同 -> q[2] 错误
        if (r1 == 1) {
            X(q[2]); // 纠正 q[2]
        }
        // r0=0, r1=0: 无错误发生
    }
}
```

上述代码完美展示了码距与纠错能力的对应关系：由于三位重复码的码距为3，程序能够通过2个辅助量子比特提取出的4种可能的伴随式状态（00、10、11、01），精准定位到具体哪一个物理比特发生了翻转，并成功执行纠正操作，使其恢复到正确的逻辑量子态。

## isqTrain/301

- task_id: `isqTrain/301`
- task_type: `code_generation`
- category: `quantum_error_correction`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `isq_syntax_arrays`, `superposition`
- source: `isq_train_cot`
- dataset_index: `282`

### Prompt

I need an isQ program to implements a variant of the error_correction_syndrome pattern using q[7] -> q[8]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

Looking at this task, I need to generate a reasoning section for the given isQ program that implements a variant of the Steane 7-qubit code.

Let me trace through the circuit:

1. Start with 8 qubits all in |0⟩ state: |00000000⟩

2. Apply H to q[0], q[1], q[2]:
   - This creates a superposition on the first 3 qubits
   - State: (1/√8) Σ_{x2,x1,x0 ∈ {0,1}} |x2 x1 x0 00000⟩

3. CNOT gates for Steane code encoding:
   - CNOT(q[0], q[3]), CNOT(q[1], q[3]): q[3] = q[0] ⊕ q[1]
   - CNOT(q[0], q[4]), CNOT(q[2], q[4]): q[4] = q[0] ⊕ q[2]
   - CNOT(q[1], q[5]), CNOT(q[2], q[5]): q[5] = q[1] ⊕ q[2]
   - CNOT(q[0], q[6]), CNOT(q[1], q[6]), CNOT(q[2], q[6]): q[6] = q[0] ⊕ q[1] ⊕ q[2]

This is the Steane code encoding. The Steane code encodes 1 logical qubit into 7 physical qubits. The logical |0⟩_L state is an equal superposition of all even-weight codewords of the [7,4,3] Hamming code.

The classical Hamming code has codewords:
0000000
0010111
0101011
0111100
1001101
1011010
1100110
1110011

But we need to trace through more carefully. The 8th qubit q[7] stays as |0⟩ throughout.

Let me trace for each basis state |x2 x1 x0 0 0 0 0 0⟩:

For |000 00000⟩:
- q[3] = 0⊕0 = 0
- q[4] = 0⊕0 = 0
- q[5] = 0⊕0 = 0
- q[6] = 0⊕0⊕0 = 0
Result: |00000000⟩

For |001 00000⟩:
- q[3] = 1⊕0 = 1
- q[4] = 1⊕0 = 1
- q[5] = 0⊕0 = 0
- q[6] = 1⊕0⊕0 = 1
Result: |00111010⟩

Wait, let me be more careful. The qubits are q[0], q[1], q[2], q[3], q[4], q[5], q[6], q[7].

Starting state: |x0 x1 x2 0 0 0 0 0⟩

After CNOT(q[0], q[3]): q[3] = x0
After CNOT(q[1], q[3]): q[3] = x0 ⊕ x1
After CNOT(q[0], q[4]): q[4] = x0
After CNOT(q[2], q[4]): q[4] = x0 ⊕ x2
After CNOT(q[1], q[5]): q[5] = x1
After CNOT(q[2], q[5]): q[5] = x1 ⊕ x2
After CNOT(q[0], q[6]): q[6] = x0
After CNOT(q[1], q[6]): q[6] = x0 ⊕ x1
After CNOT(q[2], q[6]): q[6] = x0 ⊕ x1 ⊕ x2

For |00000000⟩ (x0=0, x1=0, x2=0):
q[3]=0, q[4]=0, q[5]=0, q[6]=0
Result: |00000000⟩

For |10000000⟩ (x0=1, x1=0, x2=0):
q[3]=1, q[4]=1, q[5]=0, q[6]=1
Result: |10011010⟩

For |01000000⟩ (x0=0, x1=1, x2=0):
q[3]=1, q[4]=0, q[5]=1, q[6]=1
Result:

## isqQA/quantum_error_correction/181_isq_demonstration

- task_id: `isqQA/quantum_error_correction/181_isq_demonstration`
- task_type: `qa_concept`
- category: `quantum_error_correction`
- difficulty: `difficult`
- concept_tags: `isq_demonstration`, `concept`, `量子纠错开销`
- source: `qa_pipeline`
- dataset_index: `5506`

### Prompt

量子纠错是实现大规模容错量子计算的基石，但引入纠错机制会带来显著的“量子纠错开销”。能否请你深入讲解量子纠错开销的具体含义，并使用isQ量子编程语言编写一个示例程序，通过具体的量子电路（如最简单的3比特位翻转码）来直观展示我们在物理层面付出了哪些资源开销？

### Reference answer

量子纠错开销是指在物理层面实现一个无错的“逻辑量子比特”及其逻辑操作时，所需消耗的额外物理量子比特数量、量子门操作数量以及电路深度的增加。在量子计算中，由于量子态极易受到环境噪声的干扰而发生退相干或门操作错误，我们必须引入量子纠错码（QEC）。然而，为了纠正错误，系统必须付出巨大的开销：空间开销上，一个逻辑比特往往需要成百上千个物理比特来编码（如表面码）；时间开销上，需要不断进行错误症状测量并执行前馈控制纠错，这极大地增加了电路深度和控制的复杂性。为了直观展示这一概念，我们可以通过经典的3比特位翻转码来进行演示。在这个例子中，为了保护1个逻辑量子比特，我们需要将其编码到3个物理量子比特中，并引入2个辅助量子比特用于错误症状提取，物理资源直接从1扩展到了5，同时增加了大量的CNOT门和条件逻辑门。

以下是用isQ语言编写的3比特位翻转码演示程序：

```isq
import std;

// 声明3个物理数据量子比特和2个辅助测量比特
qbit q[3];
qbit anc[2];
// 声明用于存储测量结果的经典寄存器
creg c[2];

procedure main() {
    // === 1. 逻辑态初始化与编码 ===
    // 准备逻辑态 |1>_L，原本对1个物理比特的简单操作，现在需要施加X门并使用2个CNOT门进行纠缠编码
    X(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);

    // === 2. 模拟环境噪声 ===
    // 假设第2个物理量子比特发生了位翻转错误
    X(q[1]);

    // === 3. 错误症状测量 ===
    // 为了诊断错误，引入辅助比特，这构成了重大的物理资源开销
    // 测量Z_1 Z_2的奇偶性到anc[0]
    CNOT(q[0], anc[0]);
    CNOT(q[1], anc[0]);
    // 测量Z_2 Z_3的奇偶性到anc[1]
    CNOT(q[1], anc[1]);
    CNOT(q[2], anc[1]);

    // 读取症状
    c[0] = M(anc[0]);
    c[1] = M(anc[1]);

    // === 4. 前馈纠错操作 ===
    // 根据测量出的经典症状，施加恢复操作
    // 如果anc[0]=1, anc[1]=1，说明q[1]翻转
    if (c[0] == 1) {
        if (c[1] == 1) {
            X(q[1]);
        } else {
            // 如果anc[0]=1, anc[1]=0，说明q[0]翻转
            X(q[0]);
        }
    } else {
        if (c[1] == 1) {
            // 如果anc[0]=0, anc[1]=1，说明q[2]翻转
            X(q[2]);
        }
        // 若均为0，说明无错误发生
    }
}
```

通过上述isQ代码，我们可以清晰地核算出量子纠错的开销：为了保护1个量子比特，我们将量子比特数扩大了5倍（q[0], q[1], q[2], anc[0], anc[1]）；执行的操作包含高达6个CNOT门、多次测量和经典条件控制反馈。在实际的容错量子计算中，为了对抗连续的噪声并纠正多比特错误，这种开销将呈指数级增长，这也是当前量子硬件发展的主要挑战之一。

## isqQA/quantum_error_correction/68_math_formalization

- task_id: `isqQA/quantum_error_correction/68_math_formalization`
- task_type: `qa_concept`
- category: `quantum_error_correction`
- difficulty: `difficult`
- concept_tags: `math_formalization`, `concept`, `量子纠错阈值定理`
- source: `qa_pipeline`
- dataset_index: `5517`

### Prompt

在量子纠错理论中，阈值定理是证明容错量子计算可行性的基石。请你严格从数学形式化的角度，推导并阐述量子纠错阈值定理。要求从描述物理噪声信道的CPTP映射和Dirac符号出发，给出级联编码下逻辑错误率的递推关系，并最终证明当物理错误率低于特定阈值时，逻辑错误率随编码级联层数呈双指数级递减的完整数学结论。

### Reference answer

<think>
首先，利用完全正定保迹（CPTP）映射和Dirac符号形式化描述物理噪声，将量子信道作用在密度矩阵上的过程通过Kraus算符展开，从而定义单量子比特的物理错误率$p$。其次，引入级联编码机制，分析纠错过程的失效概率。对于能纠正$t$个错误的编码，产生不可纠正逻辑错误的概率是$p$的$t+1$阶多项式。由此，可构建第$L$级逻辑错误率$p_L$与第$L-1$级错误率之间的非线性递推关系（如$p_L = c \cdot (p_{L-1})^{t+1}$）。最后，通过求解并分析该递推数列的动力学行为，寻找其不动点。确定当初始物理错误率$p$低于特定临界阈值（不动点解）时，该数列收敛，进而从数学上推导出逻辑错误率随编码级联层数$L$呈双指数递减的核心结论。
</think>

<thought>
为了形式化地表述量子纠错阈值定理，我需要先构建单物理量子比特的噪声模型。通常我们使用完全正定保迹（CPTP）映射来描述，结合密度矩阵和Kraus算符（或泡利矩阵展开）。接着，我需要引入级联编码的框架，设物理错误率为p。在独立随机错误模型下，第一级编码发生不可纠正错误的概率与p的多项式成正比（具体为发生超过t个错误的概率，t为码距决定的纠正能力）。通过递推公式，可以得出第L级逻辑错误率的表达式。当p小于某个临界常数（即阈值）时，递推关系将收敛，最终表达为双指数衰减形式。
</thought>
量子纠错阈值定理的严格数学形式化需要借助量子操作的算符和表示以及密度矩阵来进行推导。以下是完整的数学表述与推导过程：

首先，在量子力学和量子信息论中，一个物理量子比特上的任意噪声过程都可以严格表示为一个完全正定保迹（CPTP）映射 \(\mathcal{E}\)。对于一个给定的密度矩阵 \(\rho = \sum_i p_i |\psi_i\rangle \langle\psi_i|\)，噪声信道 \(\mathcal{E}\) 可以通过Kraus算符 \(\{E_k\}\) 表示为：
\[ \mathcal{E}(\rho) = \sum_k E_k \rho E_k^\dagger \]
假设噪声主要为随机泡利错误，该信道可以展开为：
\[ \mathcal{E}(\rho) = (1-p)\rho + p_X X\rho X + p_Y Y\rho Y + p_Z Z\rho Z \]
其中 \(p = p_X + p_Y + p_Z\) 定义为单物理量子比特发生错误的总体物理错误率。

为了进行量子纠错，我们引入一个参数为 \(\llbracket n, k, d \rrbracket\) 的量子纠错码，它将 \(k\) 个逻辑量子比特编码到 \(n\) 个物理量子比特中，码距为 \(d\)。该编码过程可用一个等距映射（Isometry） \(U_{\text{enc}}\) 表示，它将 \(k\) 个物理比特的希尔伯特空间 \(\mathcal{H}_2^{\otimes k}\) 映射到 \(n\) 个物理比特的纠缠空间 \(\mathcal{H}_2^{\otimes n}\)：
\[ U_{\text{enc}} : \mathcal{H}_2^{\otimes k} \to \mathcal{H}_2^{\otimes n} \]
逻辑态 \(\rho_L\) 被编码为 \(\bar{\rho} = U_{\text{enc}} \rho_L U_{\text{enc}}^\dagger\)。

在经过噪声信道 \(\mathcal{E}^{\otimes n}\) 并施加纠错电路 \(\mathcal{R}\) 后，逻辑错误率 \(p^{(1)}\) 取决于码距 \(d\)。根据独立错误模型，只有当物理错误数量超过 \(t = \lfloor \frac{d-1}{2} \rfloor\) 时，才会发生无法纠正的逻辑错误。此时，第一级逻辑错误率 \(p^{(1)}\) 可近似为最低阶的失败概率：
\[ p^{(1)} \approx \binom{n}{t+1} p^{t+1} + O(p^{t+2}) = c p^{t+1} \]
其中 \(c\) 是由具体编码结构决定的多项式系数。

为了达到任意高的精度，我们采用级联编码策略。设 \(p^{(L)}\) 为经过 \(L\) 级级联编码后的逻辑错误率，那么递推关系式可以写为：
\[ p^{(L)} = c \left( p^{(L-1)} \right)^{t+1} \]
为简化起见，我们考虑最常用的能纠正1个错误的码 \(t=1\)，例如 Steane \(\llbracket 7, 1, 3 \rrbracket\) 码，此时递推公式简化为：
\[ p^{(L)} = c \left( p^{(L-1)} \right)^2 \]
这是一个二次递推关系。如果我们对等式两边取对数，可以得到：
\[ \log p^{(L)} = \log c + 2 \log p^{(L-1)} \]
通过不断展开这个递推式，我们得到关于初始物理错误率 \(p = p^{(0)}\) 的显式表达式：
\[ p^{(L)} = \frac{(c p)^{2^L}}{c} \]

这就是阈值定理的核心数学结论。从这个公式可以看出，只要满足条件 \(c p < 1\)，即初始物理错误率低于某个特定的阈值 \(p_{th} = \frac{1}{c}\)，那么分子项 \((c p)^{2^L}\) 将随着级联层数 \(L\) 呈现**双指数衰减**。

完整的阈值定理表述如下：给定一个相互作用多边形结构的容错量子计算架构，存在一个正的常数阈值 \(p_{th} > 0\)（通常取决于具体的纠错码和噪声模型）。如果初始物理量子比特的错误率满足 \(p < p_{th}\)，那么对于任意给定的计算精度要求 \(\epsilon > 0\)（即最终逻辑错误率 \(p_L \le \epsilon\)），我们可以通过使用大小为 \(L = O(\log \log (1/\epsilon))\) 的级联编码来实现。

其资源开销的数学代价为：所需的物理量子比特总数 \(N_{\text{physical}}\) 与逻辑量子比特数 \(N_{\text{logical}}\) 的关系满足多项式增长：
\[ N_{\text{physical}} = \text{Poly}\left(\log \left(\frac{1}{\epsilon}\right)\right) N_{\text{logical}} \]
并且量子门操作的时间复杂度开销也是多项式级别的。这一数学证明表明，只要有足够多且质量达到阈值要求的物理量子比特，我们就能以有限的物理资源开销，构筑出任意高保真度的逻辑量子计算机。

## isqQA/quantum_error_correction/171_math_formalization

- task_id: `isqQA/quantum_error_correction/171_math_formalization`
- task_type: `qa_concept`
- category: `quantum_error_correction`
- difficulty: `expert`
- concept_tags: `math_formalization`, `concept`, `拓扑量子纠错码`
- source: `qa_pipeline`
- dataset_index: `3489`

### Prompt

请详细阐述拓扑量子纠错码中最具代表性的环面码的数学形式化表述。要求使用LaTeX公式与Dirac符号，给出其局部稳定子算符的具体构造、系统哈密顿量、基态的纠缠态形式，并从代数拓扑的角度说明任意子激发的逻辑态作用。此外，请提供一段符合语法规范的isQ代码，演示如何通过量子线路模拟一个基本稳定子（如星型算符）的测量与纠错过程。

### Reference answer

<think>
为了推导环面码的数学表述，首先需确立几何架构，将量子比特映射到二维正方晶格的边并施加周期性边界条件（环面）。基于晶格结构，自然可构造出作用于顶点的星型算符（Pauli-X）和作用于面的斑块算符（Pauli-Z），并证明它们相互对易。由此可构建系统的拓扑哈密顿量，其基态即表现为所有稳定子本征值为+1的高度纠缠态。

在代数拓扑层面，环面的一阶同调群决定了系统存在由全局性质引起的基态简并。违反局部稳定子条件会产生任意子激发，而逻辑量子比特的操作则对应于任意子在非平庸闭合环路上的产生、移动与湮灭过程。最后，将拓扑模型映射到离散的量子线路中，利用辅助比特与数据比特的受控纠缠及测量提取错误特征，即可设计出用isQ语言实现稳定子校验与纠错的代码逻辑。
</think>

环面码是拓扑量子纠错码中最经典的模型，由A. Kitaev提出。它将量子比特映射到一个尺寸为 $L \times L$ 的二维正方晶格的边上，并在周期性边界条件下（即环面 $T^2$ 上）定义物理量子比特。我们使用Dirac符号与算符代数对其进行严谨的数学形式化。\n\n首先，定义晶格的基本结构。对于每一个顶点 $s$（site），我们定义一个包含4个量子比特的集合为该顶点周围的四条边；对于每一个斑块 $p$（plaquette），我们定义一个包含4个量子比特的集合为围绕该方格的四条边。基于此，我们可以构建两组相互对易的局部稳定子算符：\n1. 星型算符（顶点稳定子），定义为顶点 $s$ 周围四个量子比特上的泡利 $X$ 算符的张量积：\n\[ A_s = \bigotimes_{j \in star(s)} \sigma_x^{(j)} \]\n2. 面算符（斑块稳定子），定义为方格 $p$ 边界上四个量子比特上的泡利 $Z$ 算符的张量积：\n\[ B_p = \bigotimes_{j \in boundary(p)} \sigma_z^{(j)} \]\n\n由于每个 $A_s$ 与 $B_p$ 在非重叠区域包含不同的泡利矩阵，在共享区域（两条边）包含反对易的泡利矩阵，因此它们整体是相互对易的，即 $[A_s, B_p] = 0$。在周期性边界条件下，稳定子集合存在四个全局约束（乘积恒等式）：$\prod_s A_s = I$ 以及 $\prod_p B_p = I$。因此，独立稳定子的数量为 $L^2 - 1 + L^2 - 1 = 2L^2 - 2$。\n\n系统的拓扑纠错哈密顿量可写为这些稳定子算符之和：\n\[ H = -\sum_{s} A_s - \sum_{p} B_p \]\n该哈密顿量的基态空间（码空间）是所有稳定子算符本征值为 $+1$ 的共同本征态空间。基态 $|\xi\rangle$ 满足：\n\[ A_s |\xi\rangle = |\xi\rangle, \quad B_p |\xi\rangle = |\xi\rangle, \quad \forall s, p \]\n基态具有四重简并度，对应于环面的第一贝蒂数 $b_1 = 2$ 所决定的拓扑不变量。其逻辑态由非局域的弦算符（String Operators）连接。例如，在环面上围绕两个不可收缩的同调环作用弦算符，可以定义两对逻辑泡利算符 $\overline{X}_1, \overline{Z}_1$ 与 $\overline{X}_2, \overline{Z}_2$。\n\n当系统发生局域错误（如单量子比特翻转）时，会使得部分 $A_s$ 或 $B_p$ 的本征值变为 $-1$。这在物理上等价于在顶点或斑块中心生成了任意子激发。电荷载子（$e$）对应于 $A_s = -1$，而磁荷载子（$m$）对应于 $B_p = -1$。这两种任意子服从阿贝尔统计，且它们互为反平方关系。只有当错误链形成一条横跨整个环面的同调非平庸闭合环时，才会引发真实的逻辑错误。因此，环面码的距离为 $d = L$。\n\n为了在实际量子计算中保护逻辑态，我们需要通过辅助比特进行稳定子测量来探测任意子的位置（即伴随 Syndrome 测量的纠错）。下面是用 isQ 语言编写的模拟代码，展示如何通过一个辅助比特测量一个简化的4量子比特星型稳定子 $A_s = X_1 X_2 X_3 X_4$，并在探测到错误时施加条件纠正（反馈）：\n\n```isq\nimport std;\n\nqbit q[4]; // 数据量子比特，模拟顶点周围的4个边\nqbit anc[1]; // 用于Syndrome测量的辅助比特\n\nprocedure main() {\n    // 初始化数据比特为基态 |++++\rangle\n    for i in 0:4 {\n        H(q[i]);\n    }\n\n    // 引入一个人为的单比特翻转错误来测试纠错\n    Z(q[2]);\n\n    // 开始星型稳定子 A_s = X X X X 的测量\n    // 重置辅助比特\n    X(anc[0]);\n    H(anc[0]);\n\n    // 辅助比特与数据比特进行受控X操作（CNOT反向）\n    CNOT(anc[0], q[0]);\n    CNOT(anc[0], q[1]);\n    CNOT(anc[0], q[2]);\n    CNOT(anc[0], q[3]);\n\n    // 将辅助比特转换回计算基测量\n    H(anc[0]);\n    \n    // 测量辅助比特获取Syndrome\n    int syndrome = M(anc[0]);\n\n    // 如果syndrome为1，说明探测到了本征值-1（出现错误/任意子）\n    if (syndrome == 1) {\n        // 在实际拓扑码中需要复杂的译码算法(如最小权重匹配)\n        // 这里我们假设确切知道错误发生在q[2]，直接施加X恢复\n        // (注意：Z错误在X基下表现为X错误，此处用X门纠正)\n        X(q[2]);\n    }\n}\n```\n\n在上述代码中，辅助比特通过哈达马门和一系列受控非门实现了 $X_1 X_2 X_3 X_4$ 稳定子的无损测量。这种基于纠缠与相干控制的测量机制正是拓扑量子纠错能够 subspace 恢复量子信息的核心数学物理过程。

## isqQA/quantum_error_correction/164_math_formalization

- task_id: `isqQA/quantum_error_correction/164_math_formalization`
- task_type: `qa_concept`
- category: `quantum_error_correction`
- difficulty: `difficult`
- concept_tags: `math_formalization`, `concept`, `稳定子形式`
- source: `qa_pipeline`
- dataset_index: `2752`

### Prompt

如何利用稳定子形式（Stabilizer Formalism）严格定义一个 $[[n, k, d]]$ 量子纠错码的编码空间？请使用Dirac符号和LaTeX公式，详细阐述从 $n$ 比特Pauli群 $\mathcal{P}_n$ 构造稳定子群 $\mathcal{S}$ 的数学过程，并推导基于群代数的正交投影算符如何作用在 $n$ 个物理量子比特的希尔伯特空间 $\mathcal{H}_2^{\otimes n}$ 上以提取出该码字的逻辑子空间。

### Reference answer

<think>
构建该解答的推理过程分为三个核心步骤：

1. **确立基础算子代数**：首先定义作用在 $n$ 个物理量子比特上的Pauli群 $\mathcal{P}_n$，明确其元素由单比特Pauli矩阵的张量积与全局相位构成，为后续提供算子基础。
2. **构造稳定子与隐式空间定义**：从 $\mathcal{P}_n$ 中提取一个不包含 $-I$ 的Abel子群 $\mathcal{S}$ 作为稳定子群。根据对易关系，所有群元可同时对角化，进而将合法的编码空间（码字）严格定义为 $\mathcal{S}$ 中所有元素的共同 $+1$ 本征子空间。
3. **推导投影算符提取逻辑态**：基于群代数的正交性，构造正交投影算符 $P = \frac{1}{|\mathcal{S}|} \sum_{s \in \mathcal{S}} s$。论证其幂等性与厄米性，说明将 $P$ 作用于全希尔伯特空间 $\mathcal{H}_2^{\otimes n}$ 时，如何滤除非合法态，并利用群大小 $|\mathcal{S}|=2^{n-k}$ 推导出投影后的逻辑子空间维度严格为 $2^k$。
</think>

在量子纠错理论中，稳定子形式为我们提供了一套极其优雅且强大的数学框架来构造和分析量子码。对于一个参数为 $[[n, k, d]]$ 的量子纠错码，它将 $k$ 个逻辑量子比特编码到 $n$ 个物理量子比特的希尔伯特空间 $\mathcal{H}_2^{\otimes n}$ 中，其核心思想是通过定义一个被称为“稳定子”的算子集合来隐式地定义编码空间。

首先，定义 $n$ 个量子比特上的Pauli群 $\mathcal{P}_n$。该群由所有形如 $P = \omega \sigma_1 \otimes \sigma_2 \otimes \dots \otimes \sigma_n$ 的张量积算子构成，其中系数 $\omega \in \{1, -1, i, -i\}$ 为全局相位，而 $\sigma_i \in \{I, X, Y, Z\}$ 是作用在第 $i$ 个物理量子比特上的单比特Pauli矩阵。

在这个Pauli群中，我们选取一个Abel（阿贝尔）子群 $\mathcal{S} \subset \mathcal{P}_n$ 作为稳定子群。为了能够定义一个有效的、非平庸的编码子空间，稳定子群 $\mathcal{S}$ 必须满足两个关键的数学约束条件：
1. 对易性：对于任意的 $M_i, M_j \in \mathcal{S}$，它们必须相互对易，即 $[M_i, M_j] = 0$。
2. 不包含负单位阵：子群 $\mathcal{S}$ 中不能包含负单位算子，即 $-I^{\otimes n} \notin \mathcal{S}$。

稳定子码的编码子空间（或称码字空间） $\mathcal{C}$ 被严格定义为稳定子群 $\mathcal{S}$ 中所有算子的共同本征空间，且对应的本征值恰好为 $+1$。利用Dirac符号，我们可以将码字空间中的任意一个合法态 $|\psi\rangle \in \mathcal{C}$ 表示为满足以下条件的态矢量：
$$ \mathcal{C} = \left\{ |\psi\rangle \in \mathcal{H}_2^{\otimes n} \mathrel{\Big|} M |\psi\rangle = |\psi\rangle, \forall M \in \mathcal{S} \right\} $$

假设稳定子群 $\mathcal{S}$ 可以由 $n-k$ 个独立的、对易的生成元 $\{g_1, g_2, \dots, g_{n-k}\}$ 生成。由于每一个生成元 $g_i$ 都可以将希尔伯特空间一分为二（本征值为 $+1$ 和 $-1$ 的子空间），$n-k$ 个独立的生成元将会把 $2^n$ 维的希尔伯特空间划分为 $2^{n-k}$ 个正交子空间。而我们取本征值全为 $+1$ 的那个子空间作为编码空间，其维度恰好为 $\frac{2^n}{2^{n-k}} = 2^k$，这正是 $k$ 个逻辑量子比特所需要的维度。

为了在代数上显式地提取或投影出这个逻辑子空间，我们可以基于稳定子群 $\mathcal{S}$ 的群元素构造一个正交投影算符 $P_\mathcal{S}$。在群代数中，该投影算符可以通过对群 $\mathcal{S}$ 中的所有元素求平均来获得，其数学表述为：
$$ P_\mathcal{S} = \frac{1}{|\mathcal{S}|} \sum_{M \in \mathcal{S}} M $$
其中 $|\mathcal{S}| = 2^{n-k}$ 是子群 $\mathcal{S}$ 的阶。更直观地，由于 $\mathcal{S}$ 是由生成元 $\{g_1, \dots, g_{n-k}\}$ 张成的，该投影算符可以等价地写为这些生成元对应的 $+1$ 本征投影算符的乘积：
$$ P_\mathcal{S} = \prod_{i=1}^{n-k} \frac{I^{\otimes n} + g_i}{2} $$
由于所有的 $g_i$ 都相互对易，上述乘积可以无歧义地展开。当我们将这个投影算符作用于任意的 $n$ 比特物理态 $|\phi\rangle$ 时，它会消除掉所有不属于稳定子共有本征空间 $+1$ 的分量，只保留和归一化那些被所有生成元 $g_i$ 作用后保持不变的态。

可以简要验证该算符的性质：由于 $P_\mathcal{S}$ 是所有 $M \in \mathcal{S}$ 的线性组合，对于任意的群元素 $M_j \in \mathcal{S}$，其与 $P_\mathcal{S}$ 的乘积仅仅是对求和项的重排（因为群在乘法下是封闭的），因此有 $M_j P_\mathcal{S} = P_\mathcal{S}$。这意味着任何处于 $P_\mathcal{S}$ 像空间中的态 $|\psi\rangle = P_\mathcal{S}|\phi\rangle$ 都自动满足 $M_j |\psi\rangle = |\psi\rangle$。因此，投影算符 $P_\mathcal{S}$ 完美地在庞大的物理希尔伯特空间中提取出了存放量子信息的无错逻辑子空间。
