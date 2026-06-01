# ISQ training COT RAG corpus: quantum_algorithms shard 165

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4086

- task_id: `isqTrain/4086`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `706`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;
qbit q[3];

unit grover_oracle(qbit q[3]) {
    X(q[0]);
    ctrl CZ(q[0], q[1], q[2]);
    X(q[0]);
} deriving gate

unit grover_diffusion(qbit q[3]) {
    H(q[0]);
    H(q[1]);
    H(q[2]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    ctrl CZ(q[0], q[1], q[2]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    H(q[0]);
    H(q[1]);
    H(q[2]);
} deriving gate

procedure main() {
    H(q[0]); H(q[1]); H(q[2]);
    grover_oracle(q);
    grover_diffusion(q);
    grover_oracle(q);
    grover_diffusion(q);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

This is a Grover's algorithm circuit with 3 qubits. Let me analyze it step by step.

**Understanding the oracle:**

The `ctrl CZ(q[0], q[1], q[2])` applies CZ on q[2] controlled by q[0] and q[1]. This applies a Z gate (phase flip) when both q[0] and q[1] are |1⟩.

With X gates around q[0], the oracle marks the state where q[0] = 0 and q[1] = 1 (since X flips q[0], making it |1⟩ when it was |0⟩).

So the oracle applies a phase of -1 to the state |010⟩ (q[0]=0, q[1]=1, q[2]=0).

Wait, let me reconsider. The state |010⟩ means q[0]=0, q[1]=1, q[2]=0.

After X(q[0]), the state |010⟩ becomes |110⟩.
Then ctrl CZ(q[0], q[1], q[2]) applies Z to q[2] when q[0]=1 and q[1]=1. So |110⟩ gets a phase flip, becoming -|110⟩.
After X(q[0]), this becomes -|010⟩.

So the oracle marks |010⟩.

**The diffusion operator:**
This is the standard Grover diffusion operator that reflects about the uniform superposition.

**Initial state:**
After H on all 3 qubits: |+++⟩ = (1/√8) Σ|x⟩ for all x in {0,1}³

**Number of marked items:**
Only one item: |010⟩.

**Number of iterations:**
The circuit applies `grover_oracle` and `grover_diffusion` twice, so 2 Grover iterations.

**Optimal number of iterations for 3 qubits with 1 marked item:**
With N=8 items and M=1 marked item, the optimal number of iterations is approximately π/4 × √(N/M) = π/4 × √8 ≈ 2.22.

So 2 iterations is close to optimal but not exactly optimal. The probability won't be exactly 1.

Let me compute this more carefully.

The initial amplitude for each state is 1/√8.

Let's denote the marked state as |w⟩ = |010⟩.

After the initial superposition:
- Amplitude of marked state: a = 1/√8
- Average amplitude of unmarked states: b = 1/√8

After each Grover iteration:
- The marked state amplitude: a' = (2(N-1)/N - 1)a + 2(N-1)/N × b... 

Actually, let me use the standard Grover analysis.

Let me define:
- a_k = amplitude of the marked state after k iterations
- b_k = amplitude of each unmarked state after k iterations

Initially: a_0 = 1/√8, b_0 = 1/√8

The Grover iteration transforms:
- a_{k+1} = (2/N - 1)a_k + 2(N-1)/N × b_k... 

Hmm, let me think about this differently using the rotation angle.

The Grover iteration rotates the state vector by angle 2θ in a 2D plane, where sin(θ) = 1/√N = 1/√8.

So θ = arcsin(1/√8).

After k iterations, the amplitude of the marked state is:
a_k = sin((2k+1)θ)

For k=2:
a_2 = sin(5θ) = sin(5 × arcsin(1/√8))

Let me compute: θ = arcsin(1/√8) ≈ arcsin(0.3536) ≈ 0.3614 radians

5θ ≈ 1.807 radians ≈ 103.5°

sin(5θ) ≈ sin(1.807) ≈ 0.9723

So the probability of measuring |010⟩ is approximately 0.9723² ≈ 0.9454, about 94.5%.

Wait, but I should double-check the oracle more carefully.

Let me reconsider the ctrl CZ gate. The syntax is `ctrl CZ(q[0], q[1], q[2])`. In isQ, this means CZ is applied to q[2] with controls q[0] and q[1]. CZ on q[2] means applying

### Reference answer

Deterministic output: state |011> with probability ~0.95

## isqTrain/3500

- task_id: `isqTrain/3500`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `data_encoding_qml`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4829`

### Prompt

What is the measurement probability distribution of this isQ program?

```
import std;

qbit q[2];

procedure main() {
    H(q[0]);
    H(q[1]);

    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initial State**: The 2-qubit system starts in the ground state $|00\rangle$.
2. **Hadamard on q[0]**: Applying H puts q[0] into an equal superposition, evolving the state to $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$.
3. **Hadamard on q[1]**: Applying H to q[1] creates an independent equal superposition, resulting

### Reference answer

Probability distribution: |00>: 0.25, |01>: 0.25, |10>: 0.25, |11>: 0.25

## isqTrain/1935

- task_id: `isqTrain/1935`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `entanglement`, `interference`, `isq_syntax_arrays`, `isq_syntax_procedures`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1372`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit q[3];
qbit a[1];
procedure my_oracle() {
    CNOT(q[0], a[0]);
    CNOT(q[1], a[0]);
}
procedure main() {
    X(a[0]); H(a[0]);
    H(q[0]); H(q[1]); H(q[2]);
    my_oracle();
    H(q[0]); H(q[1]); H(q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations**: The circuit initializes a 3-qubit register `q` and an ancilla `a`. It prepares `a` in the state |-> by applying X and H. It puts `q` into a uniform superposition using H gates. The oracle applies CNOTs from `q[0]` and `q[1]` to `a`, kicking back a phase of -1 when `q[0]` XOR `q[1]` is 1. Finally, H gates are applied to `q` before measurement.
2. **State Evolution**:
   - Initial state: |000>|1>.
   - After X(a[0]) and all H gates: (1/√8) ∑_{x∈{0,1}³} |x>|->.
   - After `my_oracle()`: The CNOTs apply a phase (-1) to basis states where `q[0]` XOR `q[1]` = 1, yielding (1/√8) ∑ (-1)^{q[0]⊕q[1]} |q[0]q[1]q[2]>|->.
   - After the final H gates on `q`: The Hadamard transform exactly cancels the phase to isolate the state |110>|->. The balanced phase function $f(x_0,x_1) = x_0 \oplus

### Reference answer

{'predicted_probs': {'110': 1.0}, 'explanation': 'BV secret 110'}

## isqQA/quantum_algorithms/89_isq_implementation

- task_id: `isqQA/quantum_algorithms/89_isq_implementation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_implementation`, `algorithm`, `DJ算法与经典查询复杂度对比`
- source: `qa_pipeline`
- dataset_index: `664`

### Prompt

请详细解释Deutsch-Jozsa算法的核心思想及其相对于经典查询复杂度的量子优势，并使用isQ语言编写一个3量子比特的Deutsch-Jozsa算法完整代码，要求包含详细逐行注释说明。

### Reference answer

<think>
首先，明确解答逻辑应分为理论机制剖析与具体代码实现两部分。在理论层面，需准确定位DJ算法的应用场景，即判断黑盒函数是恒常还是平衡。通过推导经典算法在最坏情况下的查询次数，对比量子算法利用态叠加实现一次性全局查询，并借助量子干涉效应消除特定概率幅，从而清晰展示出从指数级到常数级的查询加速优势。在代码层面，针对3比特系统（2个输入比特，1个辅助比特），算法流程需按严格步骤映射：首先初始化量子态并将辅助比特置为|1>；接着对所有比特应用Hadamard门构造全局叠加态与相位；然后构建代表恒常或平衡特性的Oracle矩阵；执行Oracle后，对输入寄存器再次施加Hadamard门进行逆傅里叶变换；最后，通过测量输入比特的概率分布即可得出确定性结论。整体思考过程紧密围绕物理原理到程序语法的精确转换。
</think>

## 量子计算教授的专业解析

您好！Deutsch-Jozsa（DJ）算法是量子计算中展示量子并行性和量子加速的标志性算法。在回答您的代码实现请求之前，我先简要梳理DJ算法与经典查询复杂度的对比。

### 1. 算法核心与经典对比分析

假设我们有一个黑盒函数 $f: \{0,1\}^n \rightarrow \{0,1\}$。已知该函数是**恒常函数**（Constant，对所有输入均输出0或均输出1）或者**平衡函数**（Balanced，对一半输入输出0，另一半输入输出1）。目标是判断 $f$ 具体属于哪一类。

- **经典查询复杂度**：在最坏情况下，经典确定性算法必须查询黑盒 $2^{n-1} + 1$ 次，才能以100%的确定性得出结论。
- **量子查询复杂度（DJ算法）**：利用量子叠加态和量子干涉效应，DJ算法仅需对黑盒进行**1次查询**，即可得出具有100%确定性的结果。复杂度从指数级骤降为常数级 $O(1)$。

算法的核心原理是：将输入寄存器置于叠加态，通过黑盒 $U_f$ 引入函数的相位信息，最后通过Hadamard变换将相位差转化为可测量的概率幅差异。如果函数是恒常的，干涉会使状态坍缩为 $|0\rangle^{\otimes n}$；如果是平衡的，则一定会测量到非零状态。

### 2. 3量子比特DJ算法的isQ代码实现

下面我们以 $n=2$ 为例（即2个输入位，1个辅助位，共3个量子比特），模拟验证一个**平衡函数** $f(x_1, x_2) = x_1 \oplus x_2$（即对应CNOT门逻辑）。以下是完整的isQ代码实现及逐行注释：

```isQ
// 引入标准量子计算库
import std;

// 全局声明3个量子比特
// q[0]和q[1]作为输入寄存器，q[2]作为辅助寄存器
qbit q[3];

// 主程序入口
procedure main() {
    // 第一步：初始化。将所有输入寄存器置于|0>态，辅助寄存器置于|1>态
    // 初始状态为 |00>|1>
    X(q[2]);

    // 第二步：施加Hadamard门，构造叠加态
    // 对输入寄存器作用H门，进入等概率叠加态
    H(q[0]);
    H(q[1]);
    // 对辅助位作用H门，使其进入 |-> = (|0>-|1>)/sqrt(2) 态
    // 这样Uf的作用会转化为输入寄存器的相位翻转
    H(q[2]);

    // 第三步：执行黑盒函数 Uf
    // 这里我们选择测试 f(x) = x0 XOR x1 的平衡函数
    // 通过两个CNOT门实现：第一个CNOT翻转q[2]；第二个CNOT再次翻转q[2]，
    // 最终等效于根据q[0], q[1]的奇偶性改变了振幅相位。
    // 黑盒总共只调用了一次Uf（此处为物理结构的组合调用）
    CNOT(q[0], q[2]);
    CNOT(q[1], q[2]);

    // 第四步：对输入寄存器再次施加Hadamard门
    // Hadamard变换将量子态的相位干涉转化为计算基态上的概率分布。
    // 若f是恒常的，干涉会全部聚集在|00>态；若f是平衡的，|00>态的振幅将抵消为0。
    H(q[0]);
    H(q[1]);

    // 第五步：测量输入寄存器
    // 因为量子态已经被破坏性干涉转移到非|00>的状态，测量必定得到非零结果。
    int r0 = M(q[0]);
    int r1 = M(q[1]);

    // 为了在控制台清晰观察结果，我们将测量的量子态恢复并进行校验（可选操作）
    // 如果测得的结果不全为0，即可确认函数为平衡函数。
    // 打印或逻辑判断（在标准测试中只需关注概率分布）
    // 注意：在isQ的--probs模式下，可以直接运行并观测q[0]和q[1]的联合概率分布
    if (r0 != 0 || r1 != 0) {
        // 确认为平衡函数的标志
        X(q[0]); 
    }
}
```

### 3. 实验预期结果与复杂度总结

在上述代码中，黑盒逻辑（两个 `CNOT` 门）作为整体仅被过一遍。如果我们运行此isQ代码并观察 `q[0]` 和 `q[1]` 的联合概率，会发现 $P(|00\rangle) = 0$，而 $P(|01\rangle) = 0.5$ 且 $P(|10\rangle) = 0.5$。

测量结果一定会包含至少一个 `1`（例如 `01` 或 `10`），这向我们在无需多次查询的情况下，明确宣告黑盒函数是一个**平衡函数**。如果黑盒是恒常的（例如 $U_f = I$），代码运行后测量结果将是100%的 `00`。这就是量子算法以 $O(1)$ 量子查询复杂度击败 $O(2^{n-1}+1)$ 经典查询复杂度的完美体现。

## isqExpand/algo/86

- task_id: `isqExpand/algo/86`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `grover`, `amplitude_amplification`, `interference`
- source: `qa_pipeline`
- dataset_index: `753`

### Prompt

Grover搜索算法中，如何确定最优迭代次数？请推导N个状态中搜索M个目标态时的最优迭代公式，并说明为什么迭代过多会导致成功概率下降。

### Chain-of-thought reasoning

## 推理
本题要求推导Grover最优迭代公式。

从Grover迭代的几何解释出发：每次迭代在|target>和|non-target>构成的二维子空间中旋转2*theta角。

关键公式：P(k) = sin^2((2k+1)*theta)
最优条件：(2k+1)*theta = pi/2
得：k_opt = floor(pi/(4*theta) - 1/2)

必须强调过度旋转的概念——超过最优次数后概率下降。用N=8的例子说明。

### Reference answer

## Grover算法最优迭代次数

### 基本参数
设搜索空间大小为N，目标态数量为M，定义Grover角：

theta = arcsin(sqrt(M/N))

### 迭代演化
初始状态|s> = (1/sqrt(N)) * sum|x>是所有计算基态的等幅叠加。

经过k次Grover迭代后，测量到目标态的概率为：

P(k) = sin^2((2k+1)*theta)

### 最优迭代次数
当(2k+1)*theta ≈ pi/2时，P(k)最大。因此最优k为：

k_opt = floor(pi/(4*theta) - 1/2)

对于M << N的常见情况，theta ≈ sqrt(M/N)，所以：

k_opt ≈ (pi/4) * sqrt(N/M)

这就是Grover算法O(sqrt(N/M))复杂度的来源。

### 具体例子
- N=8, M=1: theta ≈ 0.3614, k_opt = 1
  - 1次迭代: P = 0.78125
  - 2次迭代: P = 0.9453125
  - 3次迭代: P = 0.3301（急剧下降！）

- N=8, M=2: theta = pi/6, k_opt = 1
  - 1次迭代: P = sin^2(pi/2) = 1.0（完美！）
  - 2次迭代: P = sin^2(5*pi/6) = 0.25（灾难性下降）

### 过度旋转
Grover迭代本质上是在二维子空间中的旋转。每次迭代将态矢量旋转2*theta角。当旋转超过pi/2时，态矢量开始远离目标子空间，导致成功概率下降。这种现象称为"过度旋转"（overshooting）。

### 实际意义
1. 迭代次数不是越多越好
2. 已知M时可精确计算最优次数
3. 未知M时需要量子计数算法先估计M
4. M > N/4时Grover加速消失（经典搜索更优）

## isqTrain/741

- task_id: `isqTrain/741`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `qft_based_arithmetic`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2611`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[2];

procedure main() {
    // Prepare input state |11> = 3
    X(q[0]);
    X(q[1]);
    // 2-qubit QFT: H on MSB, controlled rotation, H on LSB
    H(q[1]);
    ctrl S(q[0], q[1]);
    H(q[0]);
    // Bit-reversal swap using three CNOTs
    CNOT(q[0], q[1]);
    CNOT(q[1], q[0]);
    CNOT(q[0], q[1]);
    // Measure both qubits
    M(q[0]);
    M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the input:**
    *   Input state: |00> initially.
    *   Operations:
        *   `X(q[0]); X(q[1]);` -> prepares |11>
        *   `H(q[1]);` -> H on q[1] (LSB in binary representation of numbers, wait, q[0] is usually index 0, so LSB if we read |q1 q0>).
        *   Let's track the state carefully.
        *   Wait, QFT usually acts as MSB first or LSB first. Let's look at the standard 2-qubit QFT matrix.
        *   Wait, the comment says "H on MSB, controlled rotation, H on LSB". `q[1]` is treated as MSB.
        *   Let's trace state `|q[1] q[0]>`
        *   Initial: `|00>`
        *   `X(q[0]), X(q[1])` -> `|11>`
        *   `H(q[1])` -> `H \otimes I |11>` = `1/\sqrt{2} (|0> - |1>) \otimes |1>` = `1/\sqrt{2} (|01> - |11>)`
        *   `ctrl S(q[0], q[1])` -> control is `q[0]`, target is `q[1]`. If `q[0]` is 1, apply S to `q[1]`.
            *   Wait, standard QFT applies controlled rotations from MSB to LSB. If `q[1]` is MSB and `q[0]` is LSB:
            *   QFT formula: $\frac{1}{2} (|0> + e^{2\pi i x/4}|1>) \otimes (|0> + e^{2\pi i x/2}|1>)$ where $x = x_1 x_0$.
            *   Wait, no, the output of QFT is bit-reversed. Let's just do matrix math.
        *   State before `ctrl S(q[0], q[1])`: `1/\sqrt{2} (|01> - |11>)`
            *   In `|01>`, `q[0]` is 1. So S applied to `q[1]`. `S|0> = |0>`.
            *   In `|11>`, `q[0]` is 1. So S applied to `q[1]`. `S|1> = i|1>`.
            *   State after `ctrl S`: `1/\sqrt{2} (|01> - i|11>)`
        *   `H(q[0])` -> `I \otimes H`
            *   `|01>` becomes `1/\sqrt{2} |0>(|0>-|1>) = 1/\sqrt{2} (|00> - |01>)`
            *   `-i|11>` becomes `-i/\sqrt{2} |1>(|0>-|1>) = -i/\sqrt{2} (|10> - |11>)`
            *   State after `H(q[0])`: `1/2 (|00> - |01> - i|10> + i|11>)`
        *   Bit-reversal swap: `CNOT(q[0], q[1]); CNOT(q[1], q[0]); CNOT(q[0], q[1]);` -> Swaps `q[0]` and `q[1]`.
            *   `|00>` -> `|00>`
            *   `|01>` -> `|10>`
            *   `|10>` -> `|01>`
            *   `|11>` -> `|11>`
            *   State after swap: `1/2 (|00> - |10> - i|01> + i|11>) = 1/2 (|00> - i|01> - |10> + i|11>)`
    *   Measurement probabilities: Square of amplitudes.
        *   P(|00>) = $|1/2|^2 = 0.25$
        *   P(|01>) = $|-i/2|^2 = 0.25$
        *   P(|10>) = $|-1/2|^2 = 0.25$
        *   P(|11>) = $|i/2|^2 = 0.25$
    *   Matches predicted output perfectly!

2.  **Format the output:**
    *   "## Circuit Analysis"
    *   State the initial state and operations.
    *   Step-by-step evolution using

### Reference answer

{'predicted_probs': {'0': 0.24999999999999994, '1': 0.25000000000000006, '2': 0.24999999999999992, '3': 0.25}, 'explanation': 'Parametric variant of isqEval/278. Dimension: predict probabilities for reference circuit.'}

## isqTrain/339

- task_id: `isqTrain/339`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `726`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;

qbit q[3];

procedure main() {
    X(q[1]);
    
    // QFT
    H(q[2]);
    ctrl S(q[1], q[2]);
    ctrl T(q[0], q[2]);
    
    H(q[1]);
    ctrl S(q[0], q[1]);
    
    H(q[0]);
    
    // SWAP
    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants an analysis of an isQ quantum program that performs the Quantum Fourier Transform (QFT) on the state $|q_2 q_1 q_0\rangle = |010\rangle$ (wait, indexing: `X(q[1])` makes it $|1\rangle$ at $q_1$, so $|010\rangle$ or $q_2=0, q_1=1, q_0=0$). Then there's a swap (three-CNOT decomposition), and finally measurements. The output must be a concise step-by-step reasoning in Dirac notation, ending with the probability distribution, following the exact format.

2.  **Analyze the Circuit**:
    *   Initial state: $|000\rangle$
    *   `X(q[1])`: State becomes $|010\rangle$ (where $q_1=1$). Let's use the basis $|q_2 q_1 q_0\rangle$.
    *   "QFT" block on `q[2], q[1], q[0]`:
        *   `H(q[2])`: Acts on $q_2$. State is $|0\rangle_2 |1\rangle_1 |0\rangle_0$. $H|0\rangle = |+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$. So state is $\frac{1}{\sqrt{2}}(|010\rangle + |110\rangle)$.
        *   `ctrl S(q[1], q[2])`: Control is $q_1$, target is $q_2$. If $q_1=1$, apply $S$ to $q_2$. $S|0\rangle = |0\rangle$, $S|1\rangle = i|1\rangle$. State becomes $\frac{1}{\sqrt{2}}(|010\rangle + i|110\rangle)$.
        *   `ctrl T(q[0], q[2])`: Control is $q_0$, target is $q_2$. Since $q_0$ is always 0, this does nothing. State remains $\frac{1}{\sqrt{2}}(|010\rangle + i|110\rangle)$.
        *   `H(q[1])`: Acts on $q_1$. $H|0\rangle = |+\rangle$, $H|1\rangle = |-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
            State becomes $\frac{1}{\sqrt{2}} [ \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)_1 |0\rangle_0 |0\rangle_2 + i \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)_1 |0\rangle_0 |1\rangle_2 ]$
            $= \frac{1}{2} (|010\rangle + |110\rangle + i|011\rangle - i|111\rangle)$. Wait, let me keep the order $|q_2 q_1 q_0\rangle$.
            $|010\rangle \to |0\rangle_2 \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)_1 |0\rangle_0 = \frac{1}{\sqrt{2}}(|000\rangle - |010\rangle)$. (Wait, $|010\rangle$ means $q_2=0, q_1=1, q_0=0$. So applying H to $q_1$ gives $\frac{1}{\sqrt{2}}(|000\rangle - |010\rangle)$.
            Wait, let's trace carefully:
            Initial: $|000\rangle$
            X(q[1]): $|010\rangle$
            H(q[2]): $\frac{1}{\sqrt{2}}(|010\rangle + |110\rangle)$
            ctrl S(q[1], q[2]): $q_1$ is control. In $|010\rangle$, $q_1=1$, so $S$ acts on $q_2$. $q_2$ is 0, so it stays 0. In $|110\rangle$, $q_1=1$, so $S$ acts on $q_2$. $q_2$ is 1, so $|1\rangle \to i|1\rangle$. State: $\frac{1}{\sqrt{2}}(|010\rangle + i|110\rangle)$.
            ctrl T(q[0], q[2]): $q_0$ is

### Reference answer

{'predicted_probs': {'0': 0.125, '1': 0.12500000000000003, '2': 0.12500000000000003, '3': 0.12500000000000003, '4': 0.12500000000000003, '5': 0.12499999999999999, '6': 0.12500000000000006, '7': 0.12500000000000003}, 'explanation': 'Parametric variant of isqHumanEval/106. Dimension: predict probabilities for reference circuit.'}

## isqTrain/22

- task_id: `isqTrain/22`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2546`

### Prompt

用isQ实现implements the qft_subcircuit pattern but with a different initial state preparation (flip q[[2]] -> q[1]).

### Chain-of-thought reasoning

Let me analyze this quantum circuit step by step.

The goal is to implement a QFT subcircuit with a different initial state preparation - specifically flipping q[1] instead of q[2].

The circuit uses 3 qubits: q[0], q[1], q[2]

Initial state preparation:
- X(q[1]) flips q[1] from |0> to |1>
- Initial state: |010> (q[2]q[1]q[0] ordering)

Wait, let me be careful about the ordering. In isQ, q[0], q[1], q[2] are the qubits. The state is typically written as |q[2]q[1]q[0]>.

After X(q[1]):
State = |010> (in q[2]q[1]q[0] notation)

Now let's trace through the QFT3 procedure:

qft3(q[0], q[1], q[2]) means a=q[0], b=q[1], c=q[2]

Starting state: |010> (q[2]=0, q[1]=1, q[0]=0)

Step 1: H(a) = H(q[0])
|010> → (|010> + |011>)/√2

Step 2: ctrl Rz(pi/2.0, b, a) = CRz(π/2) with control=q[1], target=q[0]
When b=q[1]=1, we apply Rz(π/2) to a=q[0].
The state is (|010> + |011>)/√2
For |010>: q[1]=1, so apply Rz(π/2) to q[0]=0, giving phase 1
For |011>: q[1]=1, so apply Rz(π/2) to q[0]=1, giving phase e^(iπ/2) = i

Result: (|010> + i|011>)/√2

Step 3: ctrl Rz(pi/4.0, c, a) = CRz(π/4) with control=q[2], target=q[0]
When c=q[2]=0, nothing happens.

State remains: (|010> + i|011>)/√2

Step 4: H(b) = H(q[1])
Apply H to q[1] in (|010> + i|011>)/√2
|010> → (|000> + |010>)/√2
|011> → (|001> + |011>)/√2

Result: ((|000> + |010>) + i(|001> + |011>))/2

Step 5: ctrl Rz(pi/2.0, c, b) = CRz(π/2) with control=q[2], target=q[1]
When c=q[2]=0, nothing happens.

State remains: ((|000> + |010>) + i(|001> + |011>))/2

Step 6: H(c) = H(q[2])
Apply H to q[2]:
|000> → (|000> + |100>)/√2
|010> → (|010> + |110>)/√2
|001> → (|001> + |101>)/√2
|011> → (|011> + |111>)/√2

Result: ((|000> + |100> + |010> + |110>) + i(|001> + |101> + |011> + |111>))/(2√2)

Step 7: swap (three-CNOT decomposition) a and c (q[0] and q[2])
This swaps the positions of q[0] and q[2] in our state representation.

Actually wait, let me reconsider. In the standard computational basis, |q[2]q[1]q[0]>, a swap (three-CNOT decomposition) between q[0] and q[2] swaps the first and third bits.

So |000> → |000>
|100> → |001>
|010> → |010>
|110> → |011>
|001> → |100>
|101> → |101>
|011> → |110>
|111> → |111>

After swap (three-CNOT decomposition):
((|000> + |001> + |010> + |011>) + i(|100> + |101> + |110> + |111>))/(2√2)

Let me verify the magnitude squared:
For each basis state, the amplitude is either 1/(2√2) or i/(2√2).
|1/(2√2)|² = 1/

## isqTrain/702

- task_id: `isqTrain/702`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `boolean_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4362`

### Prompt

Implement a quantum circuit in isQ: implements a variant of the integer_comparator pattern using q[3] -> q[4]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a simple integer comparator that checks if value a (encoded in q[0],q[1]) is >= 2, storing the result flag in q[2].
2. **Qubits**: 4-qubit register (q[0] through q[3]); q[2] and q[3] are measured.
3. **State evolution**:
   - Start: |0000⟩
   - After X(q[0]): |0001⟩ (encode bit 0 of a=3)
   - After X(q[1]): |0011⟩ (encode bit 1 of a=3, now a=3 in binary)
   - After CNOT(q[1], q[2]): |0111⟩ (q[1]=1 flips q[2], flagging a≥2)
4. **Measurement**: M(q[2])=1 (result flag), M(q[3])=0 (unchanged). Per convention (earlier measured qubit = higher bit), this yields bitstring |10⟩ with probability 1.0.

## isqTrain/4524

- task_id: `isqTrain/4524`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `interference`, `multi_controlled_logic`, `ancilla_usage`, `isq_syntax_oracle`
- source: `isq_train_cot`
- dataset_index: `2959`

### Prompt

What does this isQ program output when measured?

```isq
import std;

oracle Uf(3,1) = [0,0,0,0,0,0,1,0];

defgate U0 = [
    1, 0, 0, 0, 0, 0, 0, 0;
    0, -1, 0, 0, 0, 0, 0, 0;
    0, 0, -1, 0, 0, 0, 0, 0;
    0, 0, 0, -1, 0, 0, 0, 0;
    0, 0, 0, 0, -1, 0, 0, 0;
    0, 0, 0, 0, 0, -1, 0, 0;
    0, 0, 0, 0, 0, 0, -1, 0;
    0, 0, 0, 0, 0, 0, 0, -1
];

qbit q[3];
qbit anc;

procedure main() {
    
    H(q[2]); H(q[1]); H(q[2]);  // target different qubit
    
    X(anc);
    H(anc);
    
    Uf(q[2], q[1], q[0], anc);
    H(q[0]); H(q[1]); H(q[2]);
    U0(q[2], q[1], q[0]);
    H(q[0]); H(q[1]); H(q[2]);
    
    Uf(q[2], q[1], q[0], anc);
    H(q[0]); H(q[1]); H(q[2]);
    U0(q[2], q[1], q[0]);
    H(q[0]); H(q[1]); H(q[2]);
    
    H(anc); X(anc);
    
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

Let me analyze this isQ program step by step.

The program has 3 qubits q[0], q[1], q[2] and one ancilla qubit.

Let me trace through the circuit:

Initial state: |0000⟩ (q[2], q[1], q[0], anc)

1. H(q[2]); H(q[1]); H(q[2]) - This applies H to q[2], then H to q[1], then H to q[2] again.
   - After H(q[2]): (|0⟩+|1⟩)/√2 ⊗ |000⟩ = (|0000⟩+|1000⟩)/√2
   - After H(q[1]): (|0000⟩+|0100⟩+|1000⟩+|1100⟩)/2
   - After H(q[2]): The H(q[2]) applied again cancels the first H(q[2]) since H²=I.
   Wait, let me reconsider. H(q[2]) twice gives identity on q[2]. So after H(q[2]);H(q[1]);H(q[2]):
   - q[2] goes through H twice = I
   - q[1] goes through H once
   
   State: |0⟩⊗(|0⟩+|1⟩)/√2⊗|0⟩⊗|0⟩ = (|0000⟩+|0100⟩)/√2

2. X(anc); H(anc):
   - X(anc): (|0001⟩+|0101⟩)/√2
   - H(anc): (|0000⟩-|0001⟩+|0100⟩-|0101⟩)/2 ... wait let me be more careful.
   
   After X(anc): anc is |1⟩
   State: (|0⟩_q2 ⊗ (|0⟩+|1⟩)/√2_q1 ⊗ |0⟩_q0 ⊗ |1⟩_anc)
   
   After H(anc): anc becomes (|0⟩-|1⟩)/√2
   State: (|0⟩_q2 ⊗ (|0⟩+|1⟩)/√2_q1 ⊗ |0⟩_q0) ⊗ (|0⟩-|1⟩)/√2_anc
   
   In computational basis for (q[2],q[1],q[0],anc):
   = 1/2 (|0000⟩ - |0001⟩ + |0100⟩ - |0101⟩)

3. Now Uf is applied. The oracle Uf(3,1) = [0,0,0,0,0,0,1,0] with inputs (q[2], q[1], q[0], anc).

Uf acts as: |x⟩|y⟩ → |x⟩|y ⊕ f(x)⟩ where x is 3 bits and y is 1 bit.

The oracle matrix is [0,0,0,0,0,0,1,0]. This means:
- For input |000⟩|0⟩ → |000⟩|0⟩
- For input |000⟩|1⟩ → |000⟩|1⟩
- For input |001⟩|0⟩ → |001⟩|0⟩
- For input |001⟩|1⟩ → |001⟩|1⟩
...

Wait, the oracle is 16x16 or 8x8? Uf(3,1) means 3 input qubits and 1 output qubit. The matrix has 8 entries... but it should be 16x16. 

Actually looking at the isQ syntax, `oracle Uf(3,1) = [0,0,0,0,0,0,1,0]` - the 8 entries probably represent f(x) values for x=0..7. So f(6)=1, all others f(x)=0.

So Uf: |x⟩|y⟩ → |x⟩|y ⊕ f(x)⟩

f(0)=0, f(1)=0, f(2)=0, f(3)=0, f(4)=0, f(5)=0, f(6)=1, f(7)=0

So f(x) = 1 only when x = 6 = |110⟩.

Now, the inputs are (q[2], q[1], q[0], anc), so x is formed from (q[2], q[1], q[0]).

The state before Uf: 1/2 (|0000⟩ - |0001⟩ + |0100⟩ - |0101⟩)
where the bits are (q[2], q[1], q[0

### Reference answer

{'predicted_probs': {'000': 0.28125, '001': 0.03125, '010': 0.28125, '011': 0.28125, '100': 0.03125, '101': 0.03125, '110': 0.03125, '111': 0.03125}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|000>) = 0.2812, P(|001>) = 0.0312, P(|010>) = 0.2812, P(|011>) = 0.2812, P(|100>) = 0.0312, P(|101>) = 0.0312, P(|110>) = 0.0312, P(|111>) = 0.0312.'}
