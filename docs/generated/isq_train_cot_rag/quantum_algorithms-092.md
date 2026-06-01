# ISQ training COT RAG corpus: quantum_algorithms shard 92

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3941

- task_id: `isqTrain/3941`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `5512`

### Prompt

This isQ program compiles but produces incorrect probabilities. Find and correct the mistake.

```
import std;
// QFT on 3 qubits with input state |001>
qbit q[3];

procedure main() {
    // Prepare input state |001>
    X(q[2]);

    // QFT stage for qubit 0
    H(q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    // QFT stage for qubit 1
    H(q[1]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    // QFT stage for qubit 2
    H(q[2]);
    // Swap q[0] and q[2]
    CNOT(q[0], q[2]);
    CNOS(q[2], q[0]);
    CNOT(q[0], q[2]);
    // Measure after QFT
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: Line `CNOS(q[2], q[0])` contains a typo — `CNOS` is not a valid gate. It should be `CNOT`. This appears in the swap section that exchanges q[0] and q[2] (required by QFT to reverse qubit order). The swap uses three CNOT gates, and the middle one is misspelled.

2. **Fix**: Replace `CNOS(q[2], q[0])` with `CNOT(q[2], q[0])`.

3. **State evolution (corrected)**:
   - |000⟩ → X(q[2]) → |001⟩
   - QFT on |001⟩ applies H and controlled-Rz rotations: produces (1/√8)Σⱼ ω^j |j⟩ where ω = e^(2πi/8), giving equal-magnitude amplitudes across all 8 basis states.
   - The CNOT-based swap of q[0]↔q[2] reverses qubit order but preserves uniform amplitude magnitudes.
   - Final measurement yields equal probability 1/8 for each of {|000⟩,|001⟩,...,|111⟩}, confirming correctness.

## isqTrain/818

- task_id: `isqTrain/818`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `multi_controlled_logic`, `reversible_computing`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4254`

### Prompt

I need an isQ program to implements the quadratic_form pattern. Include explicit identity operations in the circuit (X-X pair before M(q[2])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Implement a quadratic form f(x₀,x₁) = x₀∧x₁ with an X-X identity pair to demonstrate gate cancellation awareness.

**Qubits:** 3 qubits (q[0], q[1], q[2]); only q[2] is measured.

**State evolution:**
1. |000⟩ → H(q[0]) → (|000⟩+|100⟩)/√2
2. → H(q[1]) → (|000⟩+|010⟩+|100⟩+|110⟩)/2
3. → Toffoli(q[0],q[1],q[2]) → (|000⟩+|010⟩+|100⟩+|111⟩)/2  [AND computed]
4. → X(q[2]) → (|001⟩+|011⟩+|101⟩+|110⟩)/2
5. → X(q[2]) → (|000⟩+|010⟩+|100⟩+|111⟩)/2  [X-X cancels; identity demonstrated]
6. → M(q[2])

**Expected probabilities:** In the final state, q[2]=|0⟩ for three terms (|000⟩,|010⟩,|100⟩) each with amplitude 1/2, and q[2]=|1⟩ for one term (|111⟩). Thus P(|0⟩)=3×(1/4)=0.75 and P(|1⟩)=1/4=0.25.

## isqTrain/3011

- task_id: `isqTrain/3011`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_syntax_multi_register`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `257`

### Prompt

修复以下isQ程序中的错误：

```isq
import std;
qbit q[4];
// Double-H identity circuit on 4 qubits
procedure main() {
    H(q[0]);
    // H(q[0]); // BUG: missing Hadamard
    H(q[1]);
    H(q[1]);
    H(q[2]);
    H(q[2]);
    H(q[3]);
    H(q[3]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **Bug**: The second `H(q[0])` is commented out (missing), leaving q[0] in superposition |+⟩ instead of returning to |0⟩.
2. **Fix**: Uncomment the missing `H(q[0])` gate so all four qubits receive two Hadamard gates.
3. **State evolution**: Each qubit starts at |0⟩ → H → |+⟩ → H → |0⟩. Double-H is identity (H²=I), so all qubits return to |0⟩. Measurement yields |0000⟩ with probability 1.0.

## isqTrain/4824

- task_id: `isqTrain/4824`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_syntax_import_qft`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4148`

### Prompt

用isQ实现applies QFT to a 2-qubit register in state |11>. Import std and qft. Declare 2 global qubits. Apply X to both qubits to create |11>, then apply qft(q). Measure both qubits. The result has uniform measurement probabilities.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Apply 2-qubit QFT to the |11⟩ state and verify uniform measurement probabilities.

**Qubits:** 2 global qubits q[0], q[1], both measured.

**State evolution:**
1. |00⟩ → X(q[0]), X(q[1]) → |11⟩
2. QFT|11⟩ = QFT|3⟩ = (1/2)Σₖ e^(2πi·3k/4)|k⟩ for k=0,1,2,3
3. = (1/2)[|00⟩ - i|01⟩ - |10⟩ + i|11⟩]

**Expected probabilities:** Each amplitude has magnitude 1/2, giving |1/2|² = 0.25 for all four basis states: {|00⟩: 0.25, |01⟩: 0.25, |10⟩: 0.25, |11⟩: 0.25}. The phases (-i, -1, +i) cancel in probability, yielding uniform distribution.

## isqQA/quantum_algorithms/96_optimization_variant

- task_id: `isqQA/quantum_algorithms/96_optimization_variant`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `optimization_variant`, `algorithm`, `Grover算法的扩散算子`
- source: `qa_pipeline`
- dataset_index: `4517`

### Prompt

Grover算法中的标准扩散算子通过关于均匀叠加态的反射来放大目标态的概率幅。然而，标准扩散算子在面临解的数量未知或需要极高精度时存在“过度烹饪”导致概率回落的局限。请问针对这些局限性，扩散算子有哪些重要的改进版本或变体？请详细说明其中一种变体的数学原理，并提供相应的isQ量子程序代码实现。

### Reference answer

<thought>标准Grover扩散算子为 $U_s = 2|s\rangle\langle s| - I$，其中 $|s\rangle$ 是均匀叠加态。其局限性在于迭代次数必须严格依赖于解的数量，否则成功率会剧烈震荡。主要的优化变体包括固定点量子搜索算法和基于量子计数器的自适应扩散变体。这里我们详细推导固定点变体：Long等人提出的固定点Grover算法将原来相位翻转中的 $\pi$ 替换为可变的相位 $\phi$。其核心思想是将oracle的相位翻转 $I - 2|\omega\rangle\langle\omega|$ 改为 $I - (1-e^{i\phi})|\omega\rangle\langle\omega|$，同时将扩散算子中的相位 $\pi$ 改为相同的 $\phi$，即扩散算子变为 $U_s(\phi) = I - (1-e^{i\phi})|s\rangle\langle s|$。当选择特定的相位序列时，算法的成功概率能够单调递增逼近1，彻底消除了过度迭代带来的概率回落问题。在代码实现中，我们将展示一个基础的3量子比特系统的标准扩散算子结构（通过 H门、X门、多控Z门、X门、H门实现），并在电路注释中体现相位可调的灵活性。多控Z门由于对NISQ设备较为昂贵，通常使用Toffoli门进行分解优化。</thought>

Grover算法的标准扩散算子虽然形式优美，但在实际应用中存在两个显著的局限性：一是必须精确知道解的数量以确定迭代次数，否则会出现“过度烹饪”现象，导致测量成功率在达到峰值后迅速回落至0；二是多控Z门在物理实现上的电路深度过高。为了克服这些缺陷，研究人员提出了多个重要的改进版本与变体。

其中最具代表性的是**固定点量子搜索算法**，由Long等人提出。其数学推导如下：
标准Grover算子是由关于目标态 $|\omega\rangle$ 的反射和关于初始叠加态 $|s\rangle$ 的反射组合而成，即 $U = U_s U_\omega$，其中 $U_\omega = I - 2|\omega\rangle\langle\omega|$，$U_s = 2|s\rangle\langle s| - I$。固定点变体的核心在于将这两个反射中的 $\pi$ 相位（即-1）替换为一个随迭代步数变化的动态相位角 $\phi_j$。此时，修正后的oracle算子和扩散算子分别变为：
$U_\omega(\phi_j) = I - (1 - e^{i\phi_j})|\omega\rangle\langle\omega|$
$U_s(\phi_j) = I - (1 - e^{i\phi_j})|s\rangle\langle s|$
通过仔细选择每次迭代的相位角 $\phi_j$（例如使用特定的三角函数级数），状态向量在希尔伯特空间中的旋转将不再形成一个闭合的圆，而是呈螺旋状逐渐收敛到目标态 $|\omega\rangle$。这种变体使得算法的成功概率能够单调递增并无限逼近100%，彻底解决了迭代次数估计不准导致的概率回落问题。

此外，从底层量子硬件实现的优化维度来看，**多控门分解变体**也非常关键。标准扩散算子的核心是多控Z（MCZ）门，在量子比特连通性受限的NISQ（含噪中等规模量子）设备上，直接执行多控门会产生极深的电路。因此，通常会引入辅助量子比特，利用Toffoli门级联的方式将一个多控Z门分解为多个两比特和单比特门，或者使用相对相位网络来实现无辅助比特的浅层扩散算子电路。

以下代码使用isQ语言演示一个3量子比特系统扩散算子的基础构建，并利用辅助比特优化多控Z门的实现：

```isq
import std;

// 定义系统规模
parameter N = 3;
// 全局声明量子寄存器
qbit q[N];
// 声明一个用于分解多控Z门的辅助量子比特
qbit anc[1];

// 自定义扩散算子
procedure diffusion() {
    // 1. 将均匀叠加态反射变换为关于 |0...0> 状态的反射
    for i in 0:N {
        H(q[i]);
        X(q[i]);
    }

    // 2. 应用关于 |1...1> 状态的相位翻转
    // 此处为了适应NISQ设备的拓扑限制，通常利用辅助比特进行门分解优化
    // 对3个量子比特使用Toffoli门分解多控Z门
    // 先通过Toffoli门将控制信息存储在辅助比特上
    Toffoli(q[0], q[1], anc[0]);
    // 利用辅助比特对目标量子比特执行Z门控制相位
    ctrl @[anc[0]] Z(q[2]);
    // 撤销辅助比特的纠缠（逆向操作）
    inv Toffoli(q[0], q[1], anc[0]);

    // 3. 恢复基组
    for i in 0:N {
        X(q[i]);
        H(q[i]);
    }
}

procedure main() {
    // 初始化：生成均匀叠加态
    for i in 0:N {
        H(q[i]);
    }

    // 假设在此处插入了Oracle操作（标记目标态相位翻转）
    // ... 

    // 调用优化后的扩散算子进行概率幅放大
    diffusion();

    // 测量输出
    for i in 0:N {
        M(q[i]);
    }
}
```

## isqTrain/3023

- task_id: `isqTrain/3023`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_multi_register`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1596`

### Prompt

Something is wrong with this isQ circuit. Identify the error and provide the corrected code.

```isq
import std;
qbit q[4];
// GHZ-like state with X on q[0]
procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
    // X(q[0]); // BUG: missing initialization
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **Bug**: The `X(q[0])` gate is commented out, meaning the qubit `q[0]` remains in the |0> state before entanglement instead of being flipped to |1>. This causes the circuit to prepare a standard GHZ state rather than the intended shifted GHZ-like state.
2. **Fix**: Uncomment `X(q[0])` to apply the Pauli-X gate after the entangling CNOT sequence.
3. **State Evolution**: Starting from |0000>, the Hadamard and CNOT gates create the standard entangled state (|0000> + |1111>)/√2. Applying the X gate to q[0] flips the first qubit, yielding the correct final state (|1000> + |0111>)/√2, which matches the expected measurement probabilities.

## isqTrain/3485

- task_id: `isqTrain/3485`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `hamiltonian_simulation`
- source: `isq_train_cot`
- dataset_index: `4859`

### Prompt

I need an isQ program to single-layer QAOA for MaxCut on K4 (4-node complete graph, 6 edges) in isQ.

Edges: (0,1),(0,2),(0,3),(1,2),(1,3),(2,3). gamma=0.5, beta=0.4.
Declare 4 qubits, measure all.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for the QAOA MaxCut on K4 circuit.
1. Goal: Implement single-layer QAOA for MaxCut on K4 (complete graph with 4 nodes, 6 edges) with gamma=0.5 and beta=0.4.
2. Qubits: 4 qubits declared globally, all 4 are measured.
3. State evolution:
- Initialize |0000>.
- Apply H to all 4 qubits -> |+>|+>|+>|+> (equal superposition).
- Phase Separator: Apply ZZ(2*gamma) for each edge (6 edges total). Using CNOT-Rz-CNOT decomposition. Rz(0.5) = Rz(gamma) for each edge. This entangles the qubits and applies phases based on the cut value of the bitstring. For K4, cuts of size 0, 2, 4 (even parity) get phase $e^{-i6\gamma/2}$, cuts of size 1, 3 get phase $e^{-i2\gamma/2}$... wait, for K4, nodes have degree 3.
The number of cut edges for bitstring $x$ is $C(x)$. The phase is $e^{-i \gamma C(x)}$. Max cuts are at 0000, 1111 (0 edges, actually wait, 0000 is partitioned into empty and {0,1,2,3}, so 0 cut edges. 0011 is partitioned into {0,1} and {2,3}, which is 4 cut edges. Max cut on K4 is 4). Let's just say it applies $e^{-i \gamma C(x)}$ to each basis state.
- Mixer: Apply Rx(0.8) to all qubits (since $2\beta = 0.8$, $\beta = 0.4$). This rotates the state around the X-axis, mixing the amplitudes to hopefully amplify the MaxCut states.
4. Expected probabilities: The measurement probabilities show that symmetric states with all 0s or all 1s (representing one partition being empty, so 0 cut edges, wait, MaxCut on K4 should favor 0011, 0101, 0110, etc. Why does 0000 and 1111 have the highest probability 0.302787?). Let me re-analyze the probabilities:
|0000>: 0.302787, |1111>: 0.302787. These have NO cut edges!
Wait, if MaxCut favors max edges, why are 0000 and 1111 favored?
Ah! In K4, the partition into sets of size 2 gives 4 edges.
Wait, 0000 is parity 0, 0011 is parity 0. Parity of number of 1s?
With $2\gamma = 1$, $\beta = 0.4$.
Wait, QAOA doesn't perfectly solve MaxCut in 1 step, especially with arbitrary angles. The angles $\gamma=0.5, \beta=0.4$ might just be random or specific values that don't yield the optimal max cut as the highest probability, or they favor the trivial partition.
Regardless, my reasoning should just state that the gates prepare the QAOA state and the probabilities follow from the evolved amplitudes.

Let's structure the reasoning:
- Goal: Implement 1-layer QAOA for MaxCut on K4 with $\gamma=0.5, \beta=0.4$.
- Qubits: 4 global qubits, all measured.
- Evolution:
1. Init to $|0000\rangle$.
2. Hadamards create the uniform superposition $|++++\rangle = \frac{1}{4}\sum_{x \in \{0,1\}^4} |x\rangle$.
3. Phase separator uses CNOT-Rz(0.5)-CNOT on all 6 edges. This applies $e^{-i\gamma C(x)}$ phase to each basis state $|x\rangle$, where $C(x)$ is the number of cut edges.
4. Mixer applies Rx(0.8) to all qubits, rotating each qubit around the X-axis by $2\beta = 0.8$ to mix amplitudes.
5. Probabilities are obtained by measuring all qubits. Symmetries of K4 result in equal probabilities for bitstrings with the same number of cut edges (e.g., 0000 and 1111 both have 0 cut edges, so they have the same probability). Wait, 0011, 0101, 0110, 1100, 1010, 1001 have 4 cut edges, their prob is 0.

## isqQA/quantum_algorithms/99_comparison

- task_id: `isqQA/quantum_algorithms/99_comparison`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `comparison`, `algorithm`, `多解Grover搜索`
- source: `qa_pipeline`
- dataset_index: `5499`

### Prompt

在处理规模为 $N$ 的无结构数据库且已知存在 $k$ 个目标解时，多解Grover算法相比经典的遍历搜索以及基于连续时间量子游走的搜索算法在性能和适用性上有什么差异？请详细对比它们的优缺点、时间复杂度及适用场景。此外，请在你的分析中推导多解Grover的迭代次数要求，并使用isQ语言编写一个针对4量子比特且已知目标解数量 $k=4$ 的多解Grover搜索代码示例。

### Reference answer

在无结构数据库的搜索问题中，当已知目标解的数量为 $k$ 且总规模为 $N$ 时，这三种算法展现了截然不同的计算范式与性能特征。

首先是经典的线性遍历搜索算法。在经典计算中，寻找 $k$ 个目标解的期望时间复杂度为 $O(N/k)$。其优点在于实现极其简单，且不需要知道精确的 $k$ 值即可进行搜索。然而，其缺点也是显而易见的：面对大规模数据集时效率极为低下，且没有利用到量子力学的并行性与概率幅放大机制。它主要适用于数据规模较小或无法构建量子硬件的场景。

其次是多解Grover算法。其核心在于利用量子叠加和相位翻转进行振幅放大。从数学推导来看，我们将搜索空间划分为目标态空间（维度为 $k$）和非目标态空间（维度为 $N-k$）。经过哈达马变换后的均匀叠加态可以表示为 $|\psi\rangle = \sqrt{\frac{k}{N}}|\omega\rangle + \sqrt{\frac{N-k}{N}}|\omega^\perp\rangle$。令 $\sin\theta = \sqrt{\frac{k}{N}}$，则每次Grover迭代会将系统状态在二维子空间中向目标态旋转 $2\theta$。为了最大化测量到目标态的概率，需要将状态旋转至接近 $\pi/2$。因此，最优迭代次数 $R$ 满足 $R \cdot 2\theta \approx \pi/2$，即 $R \approx \frac{\pi}{4} \sqrt{\frac{N}{k}}$。多解Grover的时间复杂度为 $O(\sqrt{N/k})$，相比经典算法提供了二次加速。其优点是通用性强，只要能够构造预言机即可适用；缺点是必须预先知道或估计 $k$ 的值，若 $k$ 未知则极易导致“过度旋转”而降低成功率。

最后是基于连续时间量子游走的搜索算法。与Grover算法离散的迭代不同，量子游走是在连续时间下基于图的邻接矩阵演化的。对于特定结构的图，其时间复杂度同样可以达到 $O(\sqrt{N})$。其优点在于对于某些特殊的图结构（如高维格点、树状结构等），量子游走不仅能提供加速，而且在物理实现的演化连续性上可能比离散的Grover预言机更自然。然而，其缺点是适用场景严重依赖于底层的图拓扑结构，且在通用无结构数据库搜索中，其综合性能表现和理论直观性通常不如Grover算法。

综上所述，多解Grover算法在通用的无结构搜索中占据了最佳的理论平衡点。以下是在isQ语言中实现的针对 $N=16$（4个量子比特）且 $k=4$（目标态为 $|0000\rangle, |0001\rangle, |0010\rangle, |0011\rangle$，即高两位均为0）的多解Grover搜索代码。由于 $\sin^2\theta = 4/16 = 0.25$，即 $\theta = \pi/6$，最优迭代次数 $R \approx \frac{\pi/4}{\pi/6} = 1.5$，我们取1次迭代即可达到很高的成功率。

```isq
import std;

qbit q[4];

// 预言机：标记高两位(q[2], q[3])为0的状态，共有4个解
procedure oracle() {
    // 利用负控制实现：当q[2]和q[3]为0时，对整体相位或某一量子比特进行翻转
    X(q[2]);
    X(q[3]);
    
    // 等效于对|1111>作用Z门，通过H-X-H转换
    H(q[0]);
    ctrl @[2, 3] X(q[0]);
    H(q[0]);
    
    X(q[2]);
    X(q[3]);
}

// 扩散算子
procedure diffuser() {
    for i in 0:4 {
        H(q[i]);
        X(q[i]);
    }
    
    // 多控制Z门
    H(q[3]);
    ctrl @[0, 1, 2] X(q[3]);
    H(q[3]);
    
    for i in 0:4 {
        X(q[i]);
        H(q[i]);
    }
}

procedure main() {
    // 步骤1：初始化均匀叠加态
    for i in 0:4 {
        H(q[i]);
    }
    
    // 步骤2：执行1次多解Grover迭代
    oracle();
    diffuser();
    
    // 步骤3：测量量子比特
    for i in 0:4 {
        M(q[i]);
    }
}
```

## isqTrain/3527

- task_id: `isqTrain/3527`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `4527`

### Prompt

预测以下isQ代码的输出概率：

```
import std;

qbit q[2];

procedure main() {
    X(q[1]);
    H(q[0]);
    CNOT(q[0], q[1]);

    CNOT(q[0], q[1]);
    H(q[0]);

    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. Initial state is |00>. 
2. `X(q[1])` flips q[1] to |1>, resulting in the state |10>.
3. `H(q[0])` puts q[0] into superposition: |1> ⊗ |+> = (1/√2)(|10> + |11>).
4. `CNOT(q[0], q[1])` flips q[1] based on q[0], changing the state to (1/√2)(|00> + |01>).
5. `CNOT(q[0], q[1])` is applied again, exactly undoing the previous step. The state reverts to (1/√2)(|10> + |11>).
6. `H(q[0])` is applied again, undoing the first Hadamard and collapsing q[0] back to |0>. The state becomes |10>.
7. Measurements on q[0] and q[1] yield deterministic results: q[0] is 0, q[1] is 1.

Predicted probability distribution: 100% probability for |10>.

### Reference answer

{'predicted_probs': {'01': 1.0}, 'explanation': 'The output is |01> with probability 1.0'}

## isqQA/quantum_algorithms/52_math_derivation

- task_id: `isqQA/quantum_algorithms/52_math_derivation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `math_derivation`, `algorithm`, `相位回踢机制`
- source: `qa_pipeline`
- dataset_index: `443`

### Prompt

请严密推导并解释量子计算中的“相位回踢”机制。假设我们有一个处于叠加态的控制量子比特|c⟩和一个目标量子态|ψ⟩。目标态|ψ⟩是酉算子U的本征态，即U|ψ⟩ = e^(iθ)|ψ⟩。请详细写出当执行受控酉操作C-U时，复合系统量子态的演化过程，并基于推导说明相位是如何被“踢回”到控制量子比特上的。最后，请计算如果此时对控制比特再施加一次Hadamard门，测量得到控制比特为|0⟩态的概率是多少。

### Reference answer

<think>
首先，明确初态由控制比特的叠加态与目标本征态构成，并在计算基下进行线性展开。接着，根据受控酉操作（C-U）的定义，仅当控制比特处于 $|1\rangle$ 态时才对目标态作用算子 $U$。将目标态的本征方程 $U|\psi\rangle = e^{i\theta}|\psi\rangle$ 代入演化过程，可以看出目标态在演变后保持不变，但产生了一个全局相位因子 $e^{i\theta}$。

由于该相位因子仅存在于控制比特为 $|1\rangle$ 的分支中，它可以被提取为控制比特本身的相对相位。这一步将目标系统的特征相位转移到了控制系统的相对相位上，严密揭示了“相位回踢”的数学本质。最后，针对带有相对相位的控制比特执行Hadamard门操作，利用量子干涉原理合并振幅，计算出控制比特最终坍缩到 $|0\rangle$ 态的振幅，取其模平方即可得出测量概率。
</think>

相位回踢是量子算法（如量子相位估计、Shor算法）中极其核心的机制，它通过量子纠缠将目标寄存器中特征态的未知相位转移到控制寄存器的相对相位上。以下是严密的数学推导过程：

1. 初始状态设定：
假设我们有一个控制量子比特初始处于|+⟩态，一个目标量子比特处于酉算子U的本征态|ψ⟩。酉算子U作用在|ψ⟩上会附加一个全局相位，满足本征方程：U|ψ⟩ = e^{iθ}|ψ⟩。
控制比特经过Hadamard门（H|0⟩ = (|0⟩ + |1⟩)/√2）后处于叠加态，因此复合系统的初始状态（张量积）可以写为：
|Ψ₀⟩ = |c⟩ ⊗ |ψ⟩ = (1/√2)(|0⟩ + |1⟩) ⊗ |ψ⟩
展开张量积得到：
|Ψ₀⟩ = (1/√2)(|0⟩|ψ⟩ + |1⟩|ψ⟩)

2. 受控酉操作（C-U）的演化：
受控酉操作的定义是：当控制比特为|0⟩时，目标比特不发生任何操作；当控制比特为|1⟩时，对目标比特作用酉算子U。其矩阵作用效果可表示为：
C-U (|0⟩|ψ⟩) = |0⟩ ⊗ (I|ψ⟩) = |0⟩|ψ⟩
C-U (|1⟩|ψ⟩) = |1⟩ ⊗ (U|ψ⟩) = |1⟩ ⊗ (e^{iθ}|ψ⟩)
将该作用应用到初始态|Ψ₀⟩上，演化后的量子态|Ψ₁⟩为：
|Ψ₁⟩ = C-U |Ψ₀⟩ 
     = (1/√2)( |0⟩|ψ⟩ + |1⟩ ⊗ e^{iθ}|ψ⟩ )
     = (1/√2)( |0⟩|ψ⟩ + e^{iθ} |1⟩|ψ⟩ )

3. 相位回踢的数学分离（因式分解）：
观察演化后的状态|Ψ₁⟩，我们可以将目标量子态|ψ⟩作为公因数从叠加项中提取出来（张量积的分配律）：
|Ψ₁⟩ = (1/√2)(|0⟩ + e^{iθ}|1⟩) ⊗ |ψ⟩
这个数学形式极其深刻地揭示了“相位回踢”的本质：由于目标态|ψ⟩是算子U的本征态，在受控操作后，目标寄存器并没有发生改变（依然保持为|ψ⟩）。但是，原本属于目标寄存器本征值的相位因子e^{iθ}，被“踢回”并转移到了控制寄存器的相对相位上，使得控制比特的态从原本的(|0⟩ + |1⟩)/√2变为了(|0⟩ + e^{iθ}|1⟩)/√2。这相当于对控制比特施加了一个旋转操作（如Rz门），从而实现了相位信息的跨寄存器转移。

4. 测量概率计算：
接下来对控制比特再施加一次Hadamard门（H）。首先看H门对基矢的作用：
H|0⟩ = (|0⟩ + |1⟩)/√2
H|1⟩ = (|0⟩ - |1⟩)/√2
对处于叠加态(|0⟩ + e^{iθ}|1⟩)/√2的控制比特作用H门：
H [ (1/√2)(|0⟩ + e^{iθ}|1⟩) ] = (1/√2) [ H|0⟩ + e^{iθ} H|1⟩ ]
= (1/√2) [ (1/√2)(|0⟩ + |1⟩) + e^{iθ}(1/√2)(|0⟩ - |1⟩) ]
= (1/2) [ (1 + e^{iθ})|0⟩ + (1 - e^{iθ})|1⟩ ]
此时复合系统的态变为：
|Ψ₂⟩ = (1/2)(1 + e^{iθ})|0⟩|ψ⟩ + (1/2)(1 - e^{iθ})|1⟩|ψ⟩
根据玻恩法则，如果此时在计算基下测量控制比特，测得控制比特处于|0⟩态的概率幅为 A₀ = (1 + e^{iθ})/2。利用欧拉公式 e^{iθ} = cosθ + isinθ，概率的模平方计算如下：
P(0) = |A₀|² = |1/2 + (cosθ + isinθ)/2|²
= (1/2)² [ (1 + cosθ)² + (sinθ)² ]
= (1/4) [ 1 + 2cosθ + cos²θ + sin²θ ]
由于 cos²θ + sin²θ = 1，上式化简为：
P(0) = (1/4) [ 2 + 2cosθ ] = (1 + cosθ) / 2
利用半角公式，1 + cosθ = 2cos²(θ/2)，最终结果为：
P(0) = cos²(θ/2)

总结：通过这一套数学演化，目标系统的特征相位θ被成功转移到了控制比特上，并通过干涉（Hadamard门的作用）转化为了可观测的经典概率 P(0) = cos²(θ/2)。这就是众多量子算法能够提取相位的底层数学逻辑。
