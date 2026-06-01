# ISQ training COT RAG corpus: quantum_algorithms shard 163

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/2073

- task_id: `isqTrain/2073`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2974`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
qbit c[1];
qbit p[2];
procedure main() {
    H(c[0]);
    ctrl CNOT(c[0], p[0], p[1]);
    ctrl X(c[0], p[0]);
    nctrl X(c[0], p[0]);
    nctrl CNOT(c[0], p[0], p[1]);
    M(p[0]); M(p[1]);
}
```

### Chain-of-thought reasoning

Step 1: Analyze the circuit structure.
- Qubits: `c[0]` (control), `p[0]`, `p[1]` (target).
- Initial state: |0>_c |00>_p = |000>

Step 2: Step-by-step quantum state evolution.
1. `H(c[0])`: Apply Hadamard to c[0].
   State: (|0> + |1>) / sqrt(2) |00> = (|000> + |100>) / sqrt(2)
2. `ctrl CNOT(c[0], p[0], p[1])`: CNOT(p[0], p[1]) controlled by c[0].
   This means if c[0] is |1>, apply CNOT with p[0] as control and p[1] as target.
   Wait, let me double check the isQ syntax for multi-control.
   `ctrl CNOT(c[0], p[0], p[1])` -> Controls c[0]. Gate is CNOT(p[0], p[1]). Toffoli gate.
   If c=1, p[0]=1, flip p[1].
   Current state: (|000> + |100>) / sqrt(2). The p qubits are |00>, so CNOT does nothing.
   State remains: (|000> + |100>) / sqrt(2)
3. `ctrl X(c[0], p[0])`: Toffoli-like? No, `ctrl X` with c[0] as control, target p[0].
   Wait, `ctrl X(c[0], p[0])` means control c[0], target p[0].
   State: (|000> + |110>) / sqrt(2)
4. `nctrl X(c[0], p[0])`: Negative control on c[0], target p[0].
   If c[0] is |0>, flip p[0].
   State: (|010> + |110>) / sqrt(2)
5. `nctrl CNOT(c[0], p[0], p[1])`: Negative control c[0], CNOT(p[0], p[1]).
   If c[0] is |0>, apply CNOT(p[0], p[1]).
   State: (|011> + |110>) / sqrt(2)

Wait, let's re-read the state.
State before nctrl CNOT: (|0>|10> + |1>|10>)/sqrt(2)
nctrl CNOT: if c=0, CNOT(p[0], p[1]).
c=0 -> p=|10>. CNOT flips p[1]. p becomes |11>.
c=1 -> p=|10>. CNOT does nothing.
Result state: (|0>|11> + |1>|10>)/sqrt(2).

Step 3: Measurement.
`M(p[0]); M(p[1]);`
The measurement only measures `p[0]` and `p[1]`. `c[0]` is not measured.
States of `p[0]p[1]`:
For |0>|11> -> p is |11>
For |1>|10> -> p is |10>
So the outcomes are |10> and |11>.
Probabilities:
P('10') = |1/sqrt(2)|^2 = 0.5
P('11') = |1/sqrt(2)|^2 = 0.5
Wait, what are the measurement bitstring rules in isQ?
`M(p[0]); M(p[1]);`
Earlier measured qubit = higher bit.
First measured: `p[0]`, so it is the higher bit.
Second measured: `p[1]`, lower bit.
Let's check my mapping:
If p is |10>, p[0]=1, p[1]=0. Bitstring = '10'.
If p is |11>, p[0]=1, p[1]=1. Bitstring = '11'.
So probabilities are 0.5 for '10' and 0.5 for '11'.
Let's double check the state evolution.
Initial: |000>
H(c[0]): 1/sqrt(2) (|000> + |100>)
ctrl CNOT(c,p0,p1): c=1 -> CNOT(p0,p1). p is 00, so p1 not flipped. State: 1/sqrt(2) (|000> + |100>)
ctrl X(c,p0): c=1 -> X(p0). State: 1/sqrt(2) (|000> + |110>)
nctrl X(c,p0): c=0 -> X(p0). State: 1

### Reference answer

{'predicted_probs': {'10': 0.5, '11': 0.5}, 'explanation': 'Quantum walk 1 step from position 0 on 4-cycle.'}

## isqQA/quantum_algorithms/112_comparison

- task_id: `isqQA/quantum_algorithms/112_comparison`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `comparison`, `algorithm`, `逆QFT电路`
- source: `qa_pipeline`
- dataset_index: `4320`

### Prompt

在量子相位估计（QPE）等核心算法中，通常在最后阶段应用逆量子傅里叶变换而不是正向QFT。请从计算原理和酉演化的角度，对比分析为什么在提取相位信息时需要使用逆QFT而不是正向QFT。进一步探讨逆QFT在电路结构上与正向QFT（尤其是相位旋转门的方向和作用顺序）的区别，并结合经典快速傅里叶逆变换（IFFT）分析其复杂度优势。最后，请提供一个使用isQ语言编写的3量子比特逆QFT电路实现代码。

### Reference answer

iề首先从数学推导和计算原理上进行对比分析。正向量子傅里叶变换（QFT）的酉算子作用是将计算基态映射到傅里叶基态：
$QFT|j
angle = \frac{1}{\sqrt{N}} \sum_{k=0}^{N-1} e^{2\pi i jk/N}|k\rangle$
而逆量子傅里叶变换是其埃尔米特共轭，数学表达式为：
$QFT^\dagger|k\rangle = \frac{1}{\sqrt{N}} \sum_{j=0}^{N-1} e^{-2\pi i jk/N}|j\rangle$
在量子相位估计（QPE）算法中，经过受控酉门序列演化后，辅助寄存器所处的量子态实际上是目标相位的傅里叶基态叠加（包含了 $e^{2\pi i \theta k}$ 的相位因子）。由于量子测量只能在计算基矢下进行，为了将隐藏在相对相位中的信息转化为可直接测量的概率幅（即本征态的概率分布），我们必须使用逆QFT将系统从傅里叶基还原到计算基。这就是对比之下，QPE等提取特征值的算法必须使用逆QFT的核心物理原因。

在电路结构上，逆QFT与正向QFT的主要区别体现在：
1. **相位旋转方向相反**：正向QFT使用的是正向相位旋转门（如 $R_k = \begin{pmatrix} 1 & 0 \\ 0 & e^{2\pi i / 2^k} \end{pmatrix}$），而逆QFT中需要使用它们的逆门 $R_k^\dagger$，即旋转角度取相反数（如 $-\pi/2, -\pi/4$ 等）。
2. **作用顺序反转**：如果正向QFT从低位量子比特（LSB）开始作用Hadamard门和受控旋转，逆QFT则是从高位量子比特（MSB）开始执行逆旋转和Hadamard门，并且受控关系通常是反向的。在实际操作中，逆QFT相当于将正向QFT的电路反向逆推。

从与经典IFFT对比的角度来看，经典IFFT的时间复杂度为 $O(N \log N)$（其中 $N=2^n$ 为数据总量），需要串行或并行地处理海量经典数据；而逆QFT利用量子叠加态，仅需 $O(n^2)$ 甚至 $O(n \log n)$ 个量子门操作即可并行处理 $2^n$ 个分量的逆变换，实现了指数级的加速。但需要注意的是，这种加速的代价是只有当结果可以转化为经典信息（如QPE中提取最高概率的计算基态）时才有实际意义。

以下是使用isQ语言编写的3量子比特逆QFT电路代码。为了优化硬件执行并遵守不使用SWAP门的原则，本代码直接按照逆变换的逻辑顺序操作量子比特，测量时在经典端处理位反转即可：

```isq
import std;

qbit q[3];

procedure main() {
    // 假设输入状态为经过QPE演化后的傅里叶基态
    // 3量子比特逆QFT实现（省略输出端的SWAP操作，在读取概率结果时反转比特位序即可）

    // 第一步：处理最高位量子比特 q[2]
    H(q[2]);
    // 应用逆向的受控相位旋转 R2_dag, R3_dag
    ctrl @[q[1]] Rz(-pi/2, q[2]);
    ctrl @[q[0]] Rz(-pi/4, q[2]);

    // 第二步：处理次高位量子比特 q[1]
    H(q[1]);
    // 应用逆向的受控相位旋转 R2_dag
    ctrl @[q[0]] Rz(-pi/2, q[1]);

    // 第三步：处理最低位量子比特 q[0]
    H(q[0]);
}
```

在此代码中，`Rz(-pi/2, target)` 和 `Rz(-pi/4, target)` 精确对应了 $R_2^\dagger$ 和 $R_3^\dagger$ 的逆向相位要求，`ctrl @[control]` 语法完美地实现了受控旋转结构的对比翻转，展现出逆QFT在量子算法中简洁而高效的应用。

## isqQA/quantum_algorithms/91_isq_implementation

- task_id: `isqQA/quantum_algorithms/91_isq_implementation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_implementation`, `algorithm`, `BV算法的不同隐藏字符串实现`
- source: `qa_pipeline`
- dataset_index: `2543`

### Prompt

在量子计算中，Bernstein-Vazirani（BV）算法用于寻找黑盒函数中隐藏的比特串。假设我们需要寻找长度为4的特定隐藏字符串 $s=1011$，应该如何使用 isQ 语言编写完整的量子程序来实现这一目标？请提供带有逐行注释的完整代码，并详细说明如果要寻找不同的隐藏字符串，应该如何调整代码。

### Reference answer

<think>
首先，明确Bernstein-Vazirani算法的核心物理原理是利用量子叠加和干涉效应，将相位编码转化为计算基矢的测量结果。算法的标准量子线路逻辑为：对初态施加Hadamard门产生叠加态，经过目标Oracle进行相位 kickback，最后再次施加Hadamard门进行逆傅里叶变换并测量。

其次，针对特定隐藏字符串 $s=1011$，关键在于构建相应的量子Oracle。在量子线路中，函数 $f(x) = s \cdot x$ 的等效实现是借助辅助比特，在输入寄存器与辅助比特之间施加CNOT门。具体映射规则是：仅当字符串对应位置的值为1时，才添加一个以该位为控制、辅助比特为目标的CNOT门。

接着，在编写isQ代码时，程序的执行流需严格对应上述逻辑：定义5个量子比特（4个输入，1个辅助），初始化辅助比特为 $|1\rangle$ 状态，对所有比特施加H门，执行基于 $s=1011$ 的CNOT序列，再次对输入比特施加H门，最后测量输入寄存器。

最后，为了适应寻找不同字符串的需求，推理得出只需修改Oracle部分的逻辑即可：通过参数化隐藏字符串，动态遍历其每一个比特位，按条件增删CNOT门，即可实现通用的BV算法程序。
</think>

Bernstein-Vazirani（BV）算法是展示量子并行性和查询加速的经典量子算法。

在经典计算中，寻找 $n$ 位的隐藏字符串需要 $O(n)$ 次查询，而BV算法仅需 $O(1)$ 次（即1次）量子查询即可确定隐藏字符串。算法的核心数学推导和流程如下：
1. 初始化 $n$ 位的输入寄存器为 $|0\rangle^{\otimes n}$，以及1位的辅助寄存器为 $|1\rangle$。
2. 对所有量子比特施加 Hadamard 门，使输入寄存器处于均匀叠加态，辅助比特进入 $| -\rangle$ 态。
3. 执行实现隐藏字符串的 Oracle 门 $U_f$。对于目标字符串 $s$，该门实际上是一系列由输入寄存器控制辅助比特的 CNOT 门。
4. 对输入寄存器再次施加 Hadamard 门，通过量子干涉消除其他基态的概率幅，放大目标态的概率幅。
5. 测量输入寄存器，测量结果即为目标隐藏字符串 $s$。

针对隐藏字符串 $s=1011$（长度为4），以下提供了完整的 isQ 语言实现代码，并包含了逐行详细注释：

```isQ
// 引入 isQ 标准库
import std;

// 全局声明量子比特。q为长度为4的输入寄存器，a为1位的辅助寄存器
qbit q[4];
qbit a[1];

// 主程序入口
procedure main() {
    // 1. 初始化辅助比特为 |1> 状态
    // 因为默认状态是 |0>，施加 X 门即可翻转为 |1>
    X(a[0]);
    
    // 2. 对所有量子比特施加 Hadamard 门，进入叠加态
    // 输入寄存器变为 1/sqrt(2^n) * sum(|x>)
    for i in 0:4 {
        H(q[i]);
    }
    // 辅助比特变为 (|0> - |1>) / sqrt(2) 即 |-> 态
    H(a[0]);
    
    // 3. 构造并应用 Oracle 门 U_f
    // 对于隐藏字符串 s=1011，其二进制位第0、1、3位为 1
    // Oracle 的作用是当且仅当 s[i]=1 时，在输入比特 q[i] 和辅助比特 a[0] 之间建立纠缠
    // CNOT(c, t) 表示控制比特为 c，目标比特为 t
    CNOT(q[0], a[0]); // s[0] = 1，施加 CNOT
    CNOT(q[1], a[0]); // s[1] = 1，施加 CNOT
    // s[2] = 0，不需要施加 CNOT，直接跳过
    CNOT(q[3], a[0]); // s[3] = 1，施加 CNOT
    
    // 4. 对输入寄存器再次施加 Hadamard 门
    // 这一步将量子态从傅里叶基转换回计算基，使得隐藏字符串的信息转化为确定的概率分布
    for i in 0:4 {
        H(q[i]);
    }
    
    // 5. 对输入寄存器进行测量
    // 此时的理论测量结果将以 100% 的概率坍缩为二进制字符串 1011
    for i in 0:4 {
        M(q[i]);
    }
}
```

**如何修改代码以寻找不同的隐藏字符串：**
如果要寻找其他不同的隐藏字符串，算法的初始化、Hadamard 变换和测量逻辑完全保持不变，核心修改点仅在于**第3步的 Oracle 构造部分**。因为 Hadamard 变换和相位反转的数学性质，目标字符串的二进制位直接决定了哪些控制比特会与辅助比特产生纠缠。

- 如果目标字符串的第 $i$ 位为 1，则在代码中保留或添加 `CNOT(q[i], a[0]);`。
- 如果目标字符串的第 $i$ 位为 0，则在代码中删除或注释掉对应的 `CNOT(q[i], a[0]);`。

例如，如果新的目标隐藏字符串变为 $s=0101$，你只需要在 Oracle 部分写下如下代码：
```isQ
    // Oracle for s=0101
    // CNOT(q[0], a[0]); // s[0] = 0，不需要
    CNOT(q[1], a[0]); // s[1] = 1
    // CNOT(q[2], a[0]); // s[2] = 0，不需要
    CNOT(q[3], a[0]); // s[3] = 1
```
这种高度模块化的特性使得 BV 算法在探索不同隐藏字符串时非常直观且易于实现。

## isqTrain/4570

- task_id: `isqTrain/4570`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `multi_controlled_logic`, `reversible_computing`, `superposition`
- source: `isq_train_cot`
- dataset_index: `18`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit q[4];

procedure my_z(qbit a) {
    Z(a);
} deriving gate

procedure diffuser() {
    H(q[0]); H(q[1]); H(q[2]);
    X(q[0]); X(q[1]); X(q[2]);
    ctrl ctrl my_z(q[0], q[1], q[2]);
    
    X(q[0]); X(q[1]); X(q[2]);
    H(q[0]); H(q[1]); H(q[2]);
}

procedure main() {
    
    X(q[3]); H(q[3]);
    
    H(q[0]); H(q[1]); H(q[2]);
    
    
    ctrl ctrl ctrl X(q[0], q[1], q[2], q[3]); 
    diffuser();
    
    
    ctrl ctrl ctrl X(q[0], q[1], q[2], q[3]); 
    diffuser();
    
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants an analysis of an isQ program that simulates Grover's algorithm for 3 qubits searching for the state |111>, with an ancilla qubit q[3], followed by a final X gate on q[0] before measurement. the predicted output should be a "## Circuit Analysis" section with step-by-step state evolution, ending with the specific probability distribution provided in the predicted output.

2.  **Analyze the Circuit:**
    *   **Qubits:** `q[0], q[1], q[2], q[3]`
    *   **Initialization:**
        *   `X(q[3]); H(q[3])` puts q[3] into |-> (|- > = (|0> - |1>)/sqrt(2)).
        *   `H(q[0]); H(q[1]); H(q[2])` puts q[0..2] into an equal superposition: (|000> + |001> + |010> + ... + |111>)/sqrt(8).
        *   State is $|\psi_0\rangle = \frac{1}{\sqrt{8}} \sum_{x=0}^7 |x\rangle \otimes |-\rangle$.
    *   **Oracle:**
        *   `ctrl ctrl ctrl X(q[0], q[1], q[2], q[3])` flips q[3] when q[0], q[1], q[2] are all 1. Since q[3] is in |->, this applies a -1 phase to the |111> component of the search space.
        *   State: $|\psi_1\rangle = \frac{1}{\sqrt{8}} \sum_{x \neq 111} |x\rangle |-\rangle - \frac{1}{\sqrt{8}} |111\rangle |-\rangle$.
    *   **Diffuser:**
        *   Applied to q[0], q[1], q[2].
        *   `H`, `X`, `ctrl ctrl my_z` (which is double-controlled-Z (ctrl @[c1, c2] Z(target))), `X`, `H`.
        *   This reflects the state about the mean, amplifying the amplitude of |111>.
        *   For 3 qubits, one Grover iteration amplifies the amplitude of |111> from $1/\sqrt{8}$ to $3/\sqrt{8}$, and decreases the others from $1/\sqrt{8}$ to $-1/\sqrt{8}$.
        *   State after 1st iteration: $|\psi_2\rangle = (-\frac{1}{\sqrt{8}} |000> - \frac{1}{\sqrt{8}} |001> \dots + \frac{3}{\sqrt{8}} |111>) \otimes |-\rangle$.
    *   **Second Iteration:**
        *   `ctrl ctrl ctrl X(q[0], q[1], q[2], q[3])` applies oracle again.
        *   `diffuser()` applies diffuser again.
        *   Amplitude of |111> goes from $3/\sqrt{8}$ to $-5/\sqrt{8}$ (wait, let's calculate exactly).
        *   Initial amplitudes: $1/\sqrt{8} = \sqrt{1/8}$.
        *   Mean $\mu = (7 \times 1/\sqrt{8} - 1/\sqrt{8}) / 8 = 6/(8\sqrt{8})$.
        *   New amplitude for |111>: $-\mu - (-1/\sqrt{8}) = -6/(8\sqrt{8}) + 8/(8\sqrt{8}) = 2/(8\sqrt{8}) = 1/(4\sqrt{8}) = \sqrt{8}/32 = 2\sqrt{2}/32 = \sqrt{2}/16$? Wait.
        *   Let's use the standard Grover formula: $a^{(t)} = \sin((2t+1)\theta)$ where $\sin\theta = 1/\sqrt{8}$.
        *   After 2 iterations, $a^{(2)} = \sin(5\theta)$.
        *   $\cos\theta = \sqrt{7/8}$.
        *   $\sin(2\theta) = 2 \sin\theta \cos\theta = 2 \frac{\sqrt{7}}{8} = \frac{\sqrt{7}}{4}$.
        *   $\cos(2\theta) = \cos^2\theta - \sin^2\theta = 7/8 - 1/8 = 6/8 =

### Reference answer

{'predicted_probs': {'0000': 0.007813, '0001': 0.007813, '0010': 0.007813, '0011': 0.945312, '0100': 0.007813, '0101': 0.007813, '0110': 0.007813, '0111': 0.007813}, 'explanation': 'This isQ program operates on 4 qubit(s). The measurement probability distribution is: P(|0000>) = 0.0078, P(|0001>) = 0.0078, P(|0010>) = 0.0078, P(|0011>) = 0.9453, P(|0100>) = 0.0078, P(|0101>) = 0.0078, P(|0110>) = 0.0078, P(|0111>) = 0.0078.'}

## isqQA/quantum_algorithms/131_application_scenario

- task_id: `isqQA/quantum_algorithms/131_application_scenario`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `application_scenario`, `algorithm`, `量子半加器`
- source: `qa_pipeline`
- dataset_index: `2445`

### Prompt

在量子计算中，量子半加器虽然结构简单，但它是构建更复杂量子算术逻辑的基础。请问量子半加器的主要实际应用场景有哪些？它在未来的量子算法发展中扮演着怎样的关键角色？

### Reference answer

<thinking>
量子半加器是量子计算中的基础算术电路，用于计算两个量子比特的和（Sum）与进位（Carry）。其逻辑为：
- Sum = A ⊕ B
- Carry = A ∧ B
在量子电路中，通常使用一个CNOT门计算Sum，一个Toffoli门（或等效的CCX门）计算Carry。

在isQ语言中，我们可以用以下代码实现：
1. 声明3个量子比特：q[0]和q[1]作为输入，q[2]作为进位输出。
2. 使用Toffoli门计算Carry，结果存储在q[2]。
3. 使用CNOT门计算Sum，结果存储在q[1]。

代码实现：
```isq
import std;

qbit q[3];

procedure main() {
  // 假设q[0]和q[1]已初始化为输入状态
  // q[2]初始化为|0>，用于存储进位

  // 计算进位：Carry = q[0] AND q[1]
  Toffoli(q[0], q[1], q[2]);

  // 计算和：Sum = q[0] XOR q[1]
  CNOT(q[0], q[1]);
}
```

量子半加器的应用场景主要集中在量子算法的基础构建模块中，例如量子全加器、量子乘法器等。它在Shor算法、量子模拟和量子机器学习中都有重要作用。
</thinking>

量子半加器虽然是量子计算中最基础的算术单元，但它是构建复杂量子算法不可或缺的基石。它的核心作用在于实现了最基本的二进制加法逻辑，即计算两个量子比特的和与进位。其应用场景和未来前景主要体现在以下几个方面：

1. **构建更复杂的量子算术电路**：
   量子半加器是量子全加器的基本组成部分。通过将多个半加器和全加器级联，可以构建出量子多比特加法器。在此基础上，还可以进一步构建量子乘法器、量子除法器等更复杂的算术逻辑单元。这些电路是量子计算机执行复杂数学运算的基础。

2. **Shor算法的量子模指数运算**：
   Shor算法是目前最著名的量子算法之一，用于分解大整数。该算法的核心是量子模指数运算，而模指数运算需要大量的模乘法和模加法操作。量子半加器作为这些操作的基础组件，其性能和效率直接影响Shor算法的整体执行速度和资源消耗。

3. **量子模拟中的哈密顿量计算**：
   在量子模拟领域，模拟复杂量子系统的哈密顿量通常需要进行大量的数值计算。量子半加器可以用于构建量子电路，实现这些计算过程，从而加速模拟效率。例如，在模拟分子结构或材料性质时，量子算术电路用于计算电子间的相互作用能。

4. **量子机器学习中的数据处理**：
   量子机器学习算法通常涉及大量的矩阵运算和数据处理。量子半加器可以用于构建量子随机存取存储器和量子算术逻辑单元，从而实现高效的数据索引、特征提取和模型训练。它为量子机器学习提供了底层的算术支持。

从未来发展前景来看，量子半加器的研究不仅限于其基本功能实现，还包括如何优化其电路深度、减少量子比特使用以及提高容错率。随着量子硬件的不断进步，高效、低错误的量子半加器设计将成为推动量子计算机从实验走向实用化的关键因素之一。下面是一个使用isQ语言实现的量子半加器示例代码：

```isq
import std;

qbit q[3]; // 声明3个量子比特：q[0]和q[1]为输入，q[2]为进位输出

procedure main() {
  // 初始化输入状态（示例）
  // 假设输入A=1，B=1
  X(q[0]);
  X(q[1]);

  // 量子半加器逻辑
  // 计算进位：Carry = A AND B
  Toffoli(q[0], q[1], q[2]);

  // 计算和：Sum = A XOR B
  CNOT(q[0], q[1]);

  // 此时：
  // q[1] 存储和
  // q[2] 存储进位
}
```

## isqExpand/algo/33

- task_id: `isqExpand/algo/33`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `hhl`, `controlled_rotation`, `ry_gate`, `bug_fix`
- source: `isq_expansion`
- dataset_index: `980`

### Prompt

The following isQ code has a bug. Find and fix it.

Buggy code:
```isq
import std;
qbit clock[2];
qbit anc[1];

procedure main() {
    X(clock[1]);
    nctrl ctrl Ry(1.5708, clock[0], clock[1], anc[0]);
    M(anc[0]);
}
```

### Chain-of-thought reasoning

## Bug Analysis

The HHL controlled rotation requires Ry(2*arcsin(c/lambda)).
For lambda=1, c=1: theta = 2*arcsin(1) = 2*(pi/2) = pi.

The buggy code uses 1.5708 = pi/2 = arcsin(1), which is only half the correct angle.

Ry(pi/2)|0> = cos(pi/4)|0> + sin(pi/4)|1> = (|0>+|1>)/sqrt(2)
This gives P(|1>) = 0.5, not the desired 1.0.

Ry(pi)|0> = cos(pi/2)|0> + sin(pi/2)|1> = |1>
This gives P(|1>) = 1.0.

Fix: Change 1.5708 to 3.14159265 (use pi instead of pi/2).

## isqTrain/900

- task_id: `isqTrain/900`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_oracle`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3174`

### Prompt

Write isQ code for the following quantum task: implements a variant of the bit_flip_oracle pattern using q[3] -> q[4]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a bit-flip oracle computing f(x) = x[0] ⊕ x[1] on an expanded 4-qubit register, with input |10⟩.
2. **Qubits**: 4 qubits (q[0..3]); all are measured, giving 4-bit output.
3. **State evolution**:
   - Start: |0000⟩
   - X(q[0]) → |1000⟩ (prepares input x=|10⟩ on q[0],q[1])
   - CNOT(q[0],q[2]): q[0]=1 flips q[2] → |1010⟩
   - CNOT(q[1],q[2]): q[1]=0, no flip → |1010⟩
4. **Result**: XOR(1,0)=1 stored in q[2], q[3] remains |0⟩. Measurement yields |1010⟩ with probability 1.0.

## isqExpand/algo/110

- task_id: `isqExpand/algo/110`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `interference`, `phase_manipulation`, `ancilla_usage`
- source: `isq_expansion`
- dataset_index: `424`

### Prompt

这个isQ程序有问题，请找出错误并给出正确代码：

```isq
import std;
qbit q[2];

procedure main() {
    H(q[0]); H(q[1]);
    CNOT(q[0], q[1]);
    H(q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Bug Analysis
Phase kickback needs ancilla in |-> = H|1>. Without X(q[1]), ancilla starts as |0>, H gives |+>, and CNOT entangles instead of kicking back phase.

Fix: Add X(q[1]) before H(q[1]).

After fix: |0>|1> -> H -> |+>|-> -> CNOT -> (-1)^x|x>|-> -> H -> |1>.
Expected: [0.0, 1.0].

## isqTrain/44

- task_id: `isqTrain/44`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_arrays`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1108`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
qbit q[4];

procedure main() {
    H(q[0]); H(q[1]);
    // Copy
    CNOT(q[0], q[2]);
    CNOT(q[1], q[3]);
    // Oracle for s="11"
    CNOT(q[0], q[2]);
    CNOT(q[0], q[3]);
    // H on inputs
    H(q[0]); H(q[1]);
    // Measure inputs
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:** The user wants an analysis of the provided isQ program, explaining the quantum state evolution using Dirac notation and predicting the measurement probability distribution. The output must follow specific formatting rules (start with "## Circuit Analysis", no code blocks, end with predicted probabilities) and be concise (3-15 lines).

2.  **Analyze the isQ Code:**
    *   `qbit q[4];` initializes $|0\rangle^{\otimes 4}$.
    *   `H(q[0]); H(q[1]);` applies Hadamard to $q_0$ and $q_1$. State becomes $\frac{1}{\sqrt{2}}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)_{0,1} \otimes |00\rangle_{2,3} = \frac{1}{2} \sum_{x \in \{0,1\}^2} |x, 00\rangle$. Wait, more precisely: $\frac{1}{2} \sum_{x \in \{0,1\}^2} |x\rangle_{0,1} |00\rangle_{2,3}$.
    *   `CNOT(q[0], q[2]); CNOT(q[1], q[3]);` copies $q_0 \to q_2$ and $q_1 \to q_3$. State: $\frac{1}{2} \sum_{x} |x\rangle |x\rangle$.
    *   `CNOT(q[0], q[2]); CNOT(q[0], q[3]);` This is the Bernstein-Vazirani oracle for $s="11"$. It computes $x \oplus s \cdot x$? Wait, let's look at the standard BV oracle.
        The target of both CNOTs is $q_0$. Wait, no.
        The code says:
        `CNOT(q[0], q[2]);`
        `CNOT(q[0], q[3]);`
        Let's trace this carefully.
        Wait, standard BV has an oracle $U_f |x\rangle |y\rangle = |x\rangle |y \oplus f(x)\rangle$.
        But in the code, we just applied a copying step:
        State: $\frac{1}{2} (|00\rangle|00\rangle + |01\rangle|01\rangle + |10\rangle|10\rangle + |11\rangle|11\rangle)$.
        Then `CNOT(q[0], q[2])`: $q_2$ becomes $q_2 \oplus q_0$.
        Wait, $q_2$ already has $q_0$. So $q_2$ becomes $q_0 \oplus q_0 = 0$.
        And `CNOT(q[0], q[3])`: $q_3$ becomes $q_3 \oplus q_0$. $q_3$ has $q_1$. So $q_3$ becomes $q_1 \oplus q_0$.
        Let's write the full state after each step:
        Initial: $|0000\rangle$
        H on 0, 1: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)_{0,1} |00\rangle_{2,3}$
        CNOT(0,2), CNOT(1,3): $\frac{1}{2}(|0000\rangle + |0101\rangle + |1010\rangle + |1111\rangle)$
        CNOT(0,2), CNOT(0,3): (q[0] is control, q[2] is target, q[3] is target)
        Let's apply CNOT(0,2) to the state:
        $|0000\rangle \to |0000\rangle$
        $|0101\rangle \to |0101\rangle$
        $|1010\rangle \to |1000\rangle$ (q[0]=1, so q[2] flips to 0)
        $|1111\rangle \to |1101\rangle$ (q[0]=1, q[2] flips to 0)
        Now apply CNOT(0,3):
        $|0000\rangle \to |0000\rangle$
        $|0101\rangle \to |0101\rangle$
        $|1000\rangle \to |1011\rangle$ (q[0]=1, so q[3] flips to 1)
        $|110

### Reference answer

{'predicted_probs': {'0': 0.5, '3': 0.5}, 'explanation': 'Parametric variant of isqHumanEval/8. Dimension: predict probabilities for reference circuit.'}

## isqQA/quantum_algorithms/135_hardware_limitations

- task_id: `isqQA/quantum_algorithms/135_hardware_limitations`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `hardware_limitations`, `algorithm`, `Swap测试`
- source: `qa_pipeline`
- dataset_index: `3069`

### Prompt

在NISQ（含噪声中等规模量子）设备上运行多量子比特态的Swap测试时，电路深度和噪声是极大的挑战。请从硬件局限的角度分析退相干现象如何影响Swap测试的保真度？同时，假设我们需要评估两个单量子比特态的保真度，请写出对应的isQ代码实现，并通过数学推导说明为什么长电路深度的Swap测试在当前硬件上极难获得高精度的结果。

### Reference answer

<Thought>
数学推导：
Swap测试用于计算两个量子态内积的模平方。设输入态为 $|\psi\rangle$ 和 $|\phi\rangle$，辅助比特初始化为 $|0\rangle$。
1. 初始态：$|0\rangle \otimes |\psi\rangle \otimes |\phi\rangle$
2. 对辅助比特应用H门：$\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) |\psi\rangle |\phi\rangle$
3. 执行受控交换（CSWAP或Fredkin门），当辅助比特为1时交换目标态：$\frac{1}{\sqrt{2}}(|0\rangle|\psi\rangle|\phi\rangle + |1\rangle|\phi\rangle|\psi\rangle)$
4. 再次对辅助比特应用H门：$\frac{1}{2}|0\rangle(|\psi\rangle|\phi\rangle + |\phi\rangle|\psi\rangle) + \frac{1}{2}|1\rangle(|\psi\rangle|\phi\rangle - |\phi\rangle|\psi\rangle)$
5. 测量辅助比特为0的概率为：$P(0) = \frac{1 + |\langle\psi|\phi\rangle|^2}{2}$
在NISQ设备中，系统的退相干用密度矩阵描述，幅值阻尼（$T_1$）和相位阻尼（$T_2$）会导致量子态概率和相位的散失。假设设备发生退极化噪声，真实测量的概率会加入大量随机背景噪声，导致 $P(0)$ 逐渐趋近于 $0.5$，从而完全掩盖了量子态之间的重叠信息。

代码设计：
在isQ中实现单比特的Swap测试。为了避免使用被禁止的SWAP关键字，我们利用逻辑门的等效替换，将受控SWAP分解为两个CNOT和一个Toffoli门。
分解公式：CSWAP(c, t1, t2) = CNOT(t2, t1); Toffoli(c, t1, t2); CNOT(t2, t1);
</Thought>

在当前的NISQ（含噪声中等规模量子）设备上执行Swap测试算法，面临着严峻的硬件局限性挑战，尤其是退相干效应和量子门保真度不足带来的叠加影响。

首先，从数学期望与退相干机制来看，Swap测试的核心在于通过受控交换门（CSWAP）在辅助比特上产生干涉。如上推导，理想情况下辅助比特测量得到0的概率为 $P(0) = \frac{1 + |\langle\psi|\phi\rangle|^2}{2}$。然而，NISQ设备中的量子比特受限于有限的弛豫时间（$T_1$）和退相位时间（$T_2$）。当算法需要比较两个多比特量子态时，受控交换门需要被分解为大量基础的CNOT和单比特门。例如，一个标准的CSWAP门通常需要约6个CNOT门。这种深度的堆积导致电路的执行时间 $t_{exec}$ 呈指数级增长。
当 $t_{exec}$ 接近甚至超过系统的退相干时间时，幅值阻尼噪声会将激发态 $|1\rangle$ 弛豫回基态 $|0\rangle$，而相位阻尼则会破坏量子态的相对相位。此时，系统的密度矩阵 $\rho$ 会迅速演化为最大混合态 $\frac{I}{2^n}$。反映在Swap测试中，就是干涉条纹变模糊，辅助比特的测量结果 $P(0)$ 会严重偏离理论值，并向绝对无信息的均匀分布（即0.5）漂移。这使得我们几乎无法从测量统计中提取出准确的保真度 $|\langle\psi|\phi\rangle|^2$。

以下是在isQ环境下，对两个单量子比特执行标准Swap测试的代码实现：

```isq
import std;

qbit q[3]; // q[0]: 辅助比特, q[1]: 态 |psi>, q[2]: 态 |phi>

procedure main() {
    // 初始化待测试的两个态。这里假设它们已经被制备。
    // 例如制备两个相同的态，理论上保真度应为1。
    H(q[1]);
    H(q[2]);

    // 开始 Swap Test
    H(q[0]);

    // 实现受控SWAP (CSWAP) 门分解
    // 根据分解定理：CSWAP(c, t1, t2) = CNOT(t2, t1) -> Toffoli(c, t1, t2) -> CNOT(t2, t1)
    CNOT(q[2], q[1]);
    Toffoli(q[0], q[1], q[2]);
    CNOT(q[2], q[1]);

    // 辅助比特再次施加H门并测量
    H(q[0]);
    
    // 测量辅助比特以估计 |<psi|phi>|^2
    M(q[0]);
}
```

在上述代码中，即使仅仅是对两个单比特进行比较，我们也使用了1个Toffoli门和2个CNOT门。在目前的超导或离子阱硬件上，Toffoli门需要进一步分解为6个CNOT门，这意味着核心受控操作将引入极高的门错误率。如果在多比特系统上进行Swap测试，由于硬件联通性拓扑的限制，引入SWAP路由操作将进一步使CNOT数量呈指数级增长。这种由高电路深度引发的误差累积与退相干效应产生共鸣，导致输出结果的信噪比极低。

因此，在NISQ时代，直接运行深层次的Swap测试往往是不切实际的。这也是为什么学术界正在大力发展诸如破坏性Swap测试（Destructive Swap Test）或随机化测量等浅层电路替代方案，以规避由于受控操作过多带来的硬件退相干瓶颈。
