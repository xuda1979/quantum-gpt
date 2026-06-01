# ISQ training COT RAG corpus: quantum_algorithms shard 174

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/algo/202

- task_id: `isqExpand/algo/202`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `superdense_coding`, `bell_pair`, `entanglement`, `quantum_communication`
- source: `isq_expansion`
- dataset_index: `76`

### Prompt

Write an isQ program that an isQ superdense coding circuit that encodes the classical message '10' into one qubit of a Bell pair. The circuit should: (1) Create a Bell pair between q[0] and q[1] using H and CNOT, (2) Apply the Z gate to q[0] to encode the message '10', (3) Decode by applying CNOT(q[0],q[1]) then H(q[0]), and (4) Measure both qubits. The measurement outcome should deterministically be '10'.

### Chain-of-thought reasoning

Superdense coding encodes 2 classical bits into 1 qubit using shared entanglement. Step 1: Create Bell pair |Phi+> = (|00>+|11>)/sqrt(2) via H(q[0]) then CNOT(q[0],q[1]). Step 2: For message '10', Alice applies Z to her qubit q[0]. This transforms |Phi+> to |Phi-> = (|00>-|11>)/sqrt(2). Step 3: Bob decodes by reversing the Bell preparation: CNOT(q[0],q[1]) then H(q[0]). After CNOT on |Phi->: (|00>-|10>)/sqrt(2) = ((|0>-|1>)/sqrt(2))|0>. After H on q[0]: |1>|0> = |10>. So the result is deterministic |10>, giving probability 1.0 for outcome 2 (binary 10) and 0 for all others.

## isqQA/quantum_algorithms/124_comparison

- task_id: `isqQA/quantum_algorithms/124_comparison`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `comparison`, `algorithm`, `量子随机数生成`
- source: `qa_pipeline`
- dataset_index: `1203`

### Prompt

请对比经典伪随机数生成器（PRNG）与基于量子测量的量子随机数生成器（QRNG）的工作原理、优缺点及适用场景，并使用isQ语言编写一段生成8位量子随机二进制序列的基础代码。

### Reference answer

经典伪随机数生成器（PRNG）与量子随机数生成器（QRNG）在核心原理和安全性上有着本质的区别。

首先，从工作原理来看：
1. 经典伪随机数生成器（PRNG）：它依赖于确定性的数学算法（如线性同余发生器、梅森旋转算法等），通过一个初始值（种子）来计算出一长串看似随机的数列。由于其本质是确定性的函数映射，只要知道算法和初始种子，就可以完美预测未来生成的每一个随机数。
2. 量子随机数生成器（QRNG）：它利用了量子力学中内在的随机性。例如，将一个量子比特置于 $|+\rangle$ 态（即 $\frac{1}{\sqrt{2}}|0\rangle + \frac{1}{\sqrt{2}}|1\rangle$ 的叠加态），然后对其进行测量。根据量子力学公理，测量结果坍缩到 $|0\rangle$ 和 $|1\rangle$ 的概率各为50%，这种坍缩是完全客观和不可预测的，不依赖于任何计算复杂度的假设。

其次，从优缺点进行对比分析：
1. PRNG的优点是计算速度极快，生成效率极高，且可以在任何经典计算机上轻松实现，不需要特殊的硬件支持。缺点是其随机性是“伪”的，存在周期性，且在密码学应用中，如果攻击者获取了内部状态或种子，整个系统的安全性就会崩溃。
2. QRNG的优点是能够提供“真随机性”，它基于量子物理定律，生成的随机数没有周期性，且不可被预测或回溯，提供了信息论级别的最高安全性。其缺点在于生成速度通常受限于量子态的制备、测量设备的带宽以及后处理算法的效率，且需要专门的量子硬件设备，成本较高。

最后，两者的适用场景如下：
1. PRNG适用于对随机性绝对不可预测性要求不高的场景，例如计算机图形渲染中的随机采样、日常软件测试、数值模拟（如蒙特卡洛方法）以及普通的电子游戏逻辑等。
2. QRNG则专门适用于对安全性要求极高的领域。例如，在量子密钥分发（QKD）中用于生成绝对安全的密钥，高安全级别的密码学协议通信，以及需要严格无偏采样的高精度科学研究、金融高频交易的安全令牌生成等。

以下为使用isQ语言编写的生成8位量子随机二进制序列的代码。其核心逻辑是对8个初始为 $|0\rangle$ 的量子比特分别应用Hadamard门（H门）使其进入叠加态，然后进行测量，从而得到真正的随机数：

import std;

qbit q[8];

procedure main() {
    // 遍历所有8个量子比特
    for i in 0:8 {
        // 对每个量子比特施加Hadamard门，使其进入 |+⟩ 叠加态
        H(q[i]);
    }
    
    for i in 0:8 {
        // 测量量子比特，结果将以0或1随机坍缩
        M(q[i]);
    }
}

## isqTrain/2715

- task_id: `isqTrain/2715`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_procedures`, `measurement_order`
- source: `isq_train_cot`
- dataset_index: `2424`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
qbit q[4];
procedure main() {
    H (q[0]);
    for i in 1:4 {

        CNOT (q[i-1], q[i]);
    }
    for i in 0:4{
        M(q[i]);
    }
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1.  **Initial State**: All qubits start in $|0\rangle$. The initial state is $|0000\rangle$.
2.  **H(q[0])**: Applies a Hadamard gate to q[0], creating a superposition: $\frac{1}{\sqrt{2}}(|0000\rangle + |1000\rangle)$.
3.  **CNOT(q[0], q[1])**: Entangles q[0] and q[1], copying the state: $\frac{1}{\sqrt{2}}(|0000\rangle + |1100\rangle)$.
4.  **CNOT(q[1], q[2])**: Entangles q[1] and q[2], copying the state: $\frac{1}{\sqrt{2}}(|0000\rangle + |1110\rangle)$.
5.  **CNOT(q[2], q[3])**: Entangles q[2] and q[3], copying the state: $\frac{1}{\sqrt{2}}(|0000\rangle + |1111\rangle)$.
6.  **Measurement**: Measuring all qubits collapses the superposition. The probability of observing $|0000\rangle$ is 0.5, and the probability of observing $|1111\rangle$ is 0.5.

**Predicted probability distribution**:

### Reference answer

{'predicted_probs': {'0000': 0.5, '1111': 0.5}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/1380

- task_id: `isqTrain/1380`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_multi_register`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5590`

### Prompt

Write an isQ program that the Deutsch algorithm for the constant function f(x)=1 (flip ancilla). Prepare ancilla in |-> state, put input in superposition, apply oracle, then Hadamard and measure.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement Deutsch algorithm for constant function f(x)=1, verifying the input qubit always measures |0⟩.
Qubits: 2 (q[0] input, anc[0] ancilla); only q[0] is measured.
State evolution: |00⟩ →X(anc) |01⟩ →H(anc) |0⟩|−⟩ →H(q) (|0⟩+|1⟩)/√2 ⊗ |−⟩.
Oracle f(x)=1: X(anc) flips |−⟩→ −|−⟩, giving a global phase: state stays (|0⟩+|1⟩)/√2 ⊗ |−⟩ (phase cancels for constant f).
→H(q) |0⟩⊗|−⟩.
Measuring q[0] yields |0⟩ with probability 1.0, confirming f is constant.

## isqTrain/732

- task_id: `isqTrain/732`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `phase_manipulation`, `qft_based_arithmetic`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4845`

### Prompt

Implement a quantum circuit in isQ: implements a variant of the qft_adder pattern using q[2] -> q[3]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

Looking at this problem, I need to understand what the task is asking for:
1. A variant of QFT adder pattern using q[2] -> q[3]
2. An expanded qubit register compared to the base version
3. The expected measurement probabilities show equal superposition of |000>, |010>, |100>, |110>

Wait, Analyzing the circuit requirements, it seems like the task description says "q[2] -> q[3]" but the reference uses q[3] array (q[0], q[1], q[2]).

Let me analyze The implementation:
- 3 qubits: q[0], q[1], q[2]
- Initialize q[0] and q[1] to |1> (creating |11> = 3 on those two qubits)
- Apply 2-qubit QFT on q[0] and q[1]
- Measure all 3 qubits

The resulting probabilities should be {|000>: 0.25, |010>: 0.25, |100>: 0.25, |110>: 0.25}

This means after the circuit, we have an equal superposition of 4 states. Let me trace through:

Initial state: |000>
After X(q[0]) and X(q[1]): |110>

Now applying QFT on q[1] and q[0]:
1. H(q[1]): |110> -> |1> ⊗ H|1> ⊗ |0> = |1> ⊗ |-> ⊗ |0> = (|100> - |110>)/√2

2. ctrl S(q[0], q[1]): S applies phase i to |1>
   - |100> stays |100>
   - |110> -> i|110>
   So we get (|100> - i|110>)/√2

3. H(q[0]): 
   - |100> -> (|00> + |10>)/√2 ⊗ |0> = (|000> + |100>)/√2
   - i|110> -> i(|010> + |110>)/√2
   So we get (|000> + |100> - i|010> - i|110>)/2

Wait, that doesn't give equal probabilities. Let me reconsider.

Actually, the probabilities are equal, so the magnitudes squared must all be 0.25. Let me recalculate.

After the QFT part, we have some state. The bit-reversal swaps q[0] and q[1].

Let me trace more carefully:

Start: |000>
X(q[0]), X(q[1]): |110>

H(q[1]): 
|110> = |1>|1>|0>
H on q[1]: |1>(H|1>)|0> = |1>|->|0> = (|100> - |110>)/√2

ctrl S(q[0], q[1]):
S|0> = |0>, S|1> = i|1>
Controlled S with q[0] controlling q[1]:
- |100> -> |100> (q[1] = 0, no effect)
- |110> -> i|110> (q[1] = 1, S applies i phase)
Result: (|100> - i|110>)/√2

H(q[0]):
|100> = |1>|0>|0> -> (|0> + |1>)|0>|0>/√2 = (|000> + |100>)/√2
-i|110> = -i|1>|1>|0> -> -i(|0> + |1>)|1>|0>/√2 = -i(|010> + |110>)/√2

So: (|000> + |100> - i|010> - i|110>)/2

Now bit-reversal swap (swap q[0] and q[1]):
CNOT(q[0], q[1]), CNOT(q[1], q[0]), CNOT(q[0], q[1])

This swaps the first two qubits:
|000> -> |000>
|100> -> |010>
|010> -> |100>
|110> -> |110>

So we get: (|000> + |010> - i|100> - i|110>)/2

The probabilities:
- |000>: |1/2|² = 0.25
- |010>: |1/2|² = 0.25
- |100>: |-i/2|² = 0.25
- |110>: |-i/2|² = 0.25

This matches the predicted output.

Now the task

## isqTrain/3515

- task_id: `isqTrain/3515`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3298`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```
import std;

qbit q[2];

procedure main() {
    X(q[0]);

    CNOT(q[0], q[1]);
    CNOT(q[1], q[0]);
    CNOT(q[0], q[1]);

    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The initial state of the 2-qubit system is |00>. The `X(q[0])` gate flips the first qubit, changing the state to |10>.
2. The `CNOT(q[0], q[1])` gate flips the target q[1] because the control q[0]

### Reference answer

{'predicted_probs': {'01': 1.0}, 'explanation': 'The output is |01> with probability 1.0'}

## isqQA/quantum_algorithms/98_principle_advantage

- task_id: `isqQA/quantum_algorithms/98_principle_advantage`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `principle_advantage`, `algorithm`, `Grover算法的几何解释`
- source: `qa_pipeline`
- dataset_index: `2351`

### Prompt

请详细阐述Grover算法在希尔伯特空间中的几何解释，并基于此说明为什么它能够将无结构数据库的搜索时间复杂度从经典的O(N)降低到量子的O(√N)？这种量子加速的根本来源是什么？请附上isQ代码演示在4个元素中搜索目标态的过程。

### Reference answer

Grover算法的几何解释为我们提供了一个直观理解量子加速的宏观视角。

在希尔伯特空间中，系统的状态可以被限制在一个由两个正交基矢张成的二维子空间内。这两个基矢分别是：目标态|w⟩（我们要寻找的解），以及所有非目标态的均匀叠加态|s'⟩。算法的初始状态是所有计算基态的均匀叠加态|s⟩，它与目标态|w⟩之间存在一个极小的夹角θ，满足sin(θ) = 1/√N。

Grover迭代的核心算子G由两部分组成：预言机Oracle和扩散算子。在几何上，Oracle的作用是保持|s'⟩不变，而将|w⟩的相位翻转，这等效于将状态向量关于|s'⟩轴做一次反射；紧接着，扩散算子将状态向量关于初始叠加态|s⟩做第二次反射。在二维平面中，连续进行两次反射，其净效果等价于将状态向量朝着目标态|w⟩旋转了2θ的角度。

这种旋转机制直接解释了时间复杂度的对比：
经典计算机在无结构数据库中寻找目标，只能逐一检查，最坏和平均情况下都需要检查O(N)次。而在Grover算法中，初始态与目标态的夹角θ极小（约等于1/√N），每次Grover迭代能稳定地将状态向量向|w⟩靠近2θ。要从初始位置旋转到极其接近目标态|w⟩的位置（即夹角趋近于0），大约需要旋转(π/2) / (2θ) ≈ (π/4)√N次。因此，量子搜索的时间复杂度被降低到了O(√N)。

这种量子加速的根本来源在于**量子相干性与干涉（振幅放大）**。经典概率算法中，错误答案的概率会相互叠加，无法像量子算法那样发生相消干涉。Grover算法巧妙地利用了量子态的叠加性质，Oracle首先给目标态打上了相位标记，随后扩散算子作为一种“相长干涉”机制，将非目标态的概率幅转移到目标态上。通过O(√N)次的相长干涉操作，目标态的概率幅被成功放大到接近1，从而实现了相对经典算法的二次加速。

下面是使用isQ语言编写的2量子比特Grover算法代码，演示在4个元素（N=4）中搜索目标态|11⟩的过程：

```isQ
import std;

qbit q[2];

procedure main() {
    // 步骤1：初始化，生成所有状态的均匀叠加态 |s⟩
    H(q[0]);
    H(q[1]);

    // 步骤2：Oracle，标记目标态 |11⟩
    // CZ门使得当且仅当控制位和目标位都为|1⟩时引入-1的相位
    CZ(q[0], q[1]);

    // 步骤3：扩散算子
    // 在数学上等价于关于初始态 |s⟩ 的反射
    H(q[0]);
    H(q[1]);
    X(q[0]);
    X(q[1]);
    CZ(q[0], q[1]);
    X(q[0]);
    X(q[1]);
    H(q[0]);
    H(q[1]);

    // 步骤4：测量
    // 对于N=4的情况，仅需1次迭代即可以100%概率测量到目标态
    M(q[0]);
    M(q[1]);
}
```

## isqExpand/algo/29

- task_id: `isqExpand/algo/29`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `hhl`, `controlled_rotation`, `eigenvalue_inversion`, `ry_gate`
- source: `isq_expansion`
- dataset_index: `2356`

### Prompt

Code this in isQ: demonstrates the controlled rotation step from the HHL algorithm. Use 2 clock qubits and 1 ancilla qubit. Prepare the clock register in the state |01> (clock[0]=0, clock[1]=1) by applying X to clock[1]. Then apply a controlled Ry rotation: when the clock reads |01> (representing eigenvalue lambda=1 with c=1), rotate the ancilla by Ry(pi) (since 2*arcsin(1/1) = pi), which maps |0> to |1>. Measure only the ancilla qubit.

### Chain-of-thought reasoning

## Reasoning
Goal: Demonstrate the HHL controlled rotation step in isolation.

Setup:
- clock[0]=0, clock[1]=1 -> clock state |01> representing eigenvalue lambda=1
- For lambda=1, c=1: theta = 2*arcsin(c/lambda) = 2*arcsin(1) = pi
- Ry(pi)|0> = sin(pi/2)|1> = |1>

Implementation:
- X(clock[1]) prepares clock = |01> (clock[0]=0, clock[1]=1)
- Need controlled rotation: when clock = |01>, apply Ry(pi) to ancilla
- In isQ: nctrl @[clock[0]] ctrl @[clock[1]] Ry(pi, anc[0])
  - nctrl: activates when clock[0] = 0
  - ctrl: activates when clock[1] = 1
  - Together: activates when clock = |01>
- Ry(pi)|0> = |1>

Ancilla = |1> with probability 1.0. Probs: [0.0, 1.0]

## isqQA/quantum_algorithms/117_isq_implementation

- task_id: `isqQA/quantum_algorithms/117_isq_implementation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_implementation`, `algorithm`, `振幅放大原理`
- source: `qa_pipeline`
- dataset_index: `4423`

### Prompt

请详细解释量子振幅放大算法的核心原理，并以在3量子比特系统中搜索目标态|111⟩为例，提供一段完整的isQ代码实现。请在代码中加入逐行详细注释，说明Oracle和Diffuser（扩散算子）的具体构建方式。

### Reference answer

<think>
首先梳理振幅放大算法（Grover搜索）的理论脉络，明确核心在于交替执行“Oracle相位反转”和“Diffuser均值反转”。针对3量子比特系统寻找目标态|111⟩（状态空间N=8），可推导出最优迭代次数约为2次。

接着构建具体的量子线路逻辑：初始阶段对3个量子比特施加Hadamard门生成均匀叠加态；设计Oracle时，针对目标态|111⟩，可通过Hadamard门结合多控Z门（如CCZ门）实现目标态的相位翻转；构建Diffuser时，根据其数学表达式，其逻辑等价于对全部量子比特施加H门、对|000⟩态进行相位反转（利用X门与CCZ门组合实现）、再施加H门。

最后，将此逻辑转化为isQ代码实现。根据isQ语法声明3个量子比特，分别编写Oracle和Diffuser的子程序或内联操作，在主程序中进行两次Grover迭代，最后测量输出。在此过程中同步规划详细的逐行中文注释，解释量子门与物理操作的对应关系。
</think>

量子振幅放大算法是Grover搜索算法的核心广义化，其基本原理是通过反复执行“相位反转”和“关于均值反转”操作，来增加测量到目标量子态的概率幅，同时抑制非目标态的概率幅。

数学原理上，假设系统初始处于均匀叠加态$|s\rangle = \frac{1}{\sqrt{N}}\sum_x|x\rangle$。首先，Oracle算子$U_\omega$作用于目标态$|\omega\rangle$，将其相位翻转，即$U_\omega|\omega\rangle = -|\omega\rangle$，而其他态保持不变。这会导致平均概率幅发生偏移。接着，应用扩散算子$U_s = 2|s\rangle\langle s| - I$，它将所有态的概率幅关于平均值进行翻转。由于目标态的相位已经被翻转，它距离平均值更远，经过翻转后其概率幅会显著增加。每次这样的Grover迭代会使目标态的概率幅呈二次级加速增长，经过$O(\sqrt{N})$次迭代后，测量得到目标态的概率接近1。

以下是在isQ语言中实现的完整代码，该代码在3量子比特系统中寻找目标态|111⟩：

```isq
import std; // 引入标准库

qbit q[3]; // 全局声明3个量子比特，用于构成8维希尔伯特空间

// 定义Oracle过程，作用是翻转目标态|111>的相位
procedure oracle() {
    // 使用Hadamard门将第3个量子比特的Z基转为X基
    // 这样可以把多控Z门转化为多控X门（Toffoli门）
    H(q[2]); 
    // 使用Toffoli门实现双控X门，当q[0]和q[1]均为|1>时，翻转q[2]
    // 结合前后的H门，等效于当q[0],q[1],q[2]全为|1>时执行Z门（即相位翻转）
    Toffoli(q[0], q[1], q[2]); 
    // 恢复第3个量子比特的基
    H(q[2]); 
}

// 定义Diffuser过程，即关于均值的反转操作
procedure diffuser() {
    // 第一步：对所有的量子比特应用Hadamard门，将叠加态转换回计算基
    for i in 0:3 {
        H(q[i]);
    }
    // 第二步：对所有的量子比特应用X门，将|000>状态映射为|111>，以便后续施加多控Z门
    for i in 0:3 {
        X(q[i]);
    }
    // 第三步：应用Hadamard门和Toffoli门组合实现多控Z门
    // 这一步的目的是仅对|111>（即原来的|000>）进行相位翻转
    H(q[2]);
    Toffoli(q[0], q[1], q[2]);
    H(q[2]);
    // 第四步：再次对所有量子比特应用X门，恢复之前的翻转
    for i in 0:3 {
        X(q[i]);
    }
    // 第五步：再次对所有量子比特应用Hadamard门，回到原来的叠加基
    for i in 0:3 {
        H(q[i]);
    }
}

// 主程序入口
procedure main() {
    // 初始化：对每个量子比特应用H门，创建均匀叠加态
    for i in 0:3 {
        H(q[i]);
    }
    
    // 振幅放大迭代
    // 对于3量子比特(N=8)，最优迭代次数为 floor(pi/4 * sqrt(8)) = 2
    for iter in 0:2 {
        oracle();   // 调用Oracle标记目标态
        diffuser(); // 调用Diffuser放大目标态概率幅
    }
    
    // 测量所有量子比特
    // 经过两次迭代后，测量结果有极高概率为111（即目标态）
    for i in 0:3 {
        M(q[i]);
    }
}
```

## isqTrain/17

- task_id: `isqTrain/17`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3276`

### Prompt

实现以下量子计算任务（使用isQ）：implements the qft_subcircuit pattern with modified rotation parameters (pi2_to_pi3). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

Analyzing the circuit requirements, I need to understand what the qft_subcircuit pattern with modified rotation parameters (pi2_to_pi3) means.

The circuit should a QFT-like circuit on 3 qubits with specific rotation angles:
- Rz(pi/3.0) instead of typical Rz(pi/2) for the first controlled rotation
- Rz(pi/4.0) instead of typical Rz(pi/4) for the second controlled rotation
- Then Rz(pi/3.0) again instead of Rz(pi/2)

So the pattern "pi2_to_pi3" means replacing pi/2 rotations with pi/3 in the QFT structure.

Let me trace through the circuit:

Initial state: |000>
After X(q[2]): |100> (qubit q[2] is flipped)

Now qft3(q[0], q[1], q[2]) is called:

Step 1: H(a) where a=q[0]
State becomes: (|000> + |100>)/√2

Step 2: ctrl Rz(pi/3.0, b, a) where b=q[1], a=q[0]
This applies Rz(pi/3) on q[1] controlled by q[0]
When q[0] is |1>, apply phase rotation on q[1]
State: (|000> + e^(i*pi/3)|100>)/√2

Step 3: ctrl Rz(pi/4.0, c, a) where c=q[2], a=q[0]
State: (|000> + e^(i*pi/3)*e^(i*pi/4)|100>)/√2 = (|000> + e^(i*7*pi/12)|100>)/√2

Step 4: H(b) where b=q[1]
State: (|000> + |010> + e^(i*7*pi/12)|100> + e^(i*7*pi/12)|110>)/2

Step 5: ctrl Rz(pi/3.0, c, b) where c=q[2], b=q[1]
When q[1] is |1>, apply Rz(pi/3) on q[2]
State: (|000> + e^(i*pi/3)|010> + e^(i*7*pi/12)|100> + e^(i*7*pi/12)*e^(i*pi/3)|110>)/2
= (|000> + e^(i*pi/3)|010> + e^(i*7*pi/12)|100> + e^(i*11*pi/12)|110>)/2

Step 6: H(c) where c=q[2]
|000> -> (|000> + |001>)/√2
|010> -> (|010> + |011>)/√2
|100> -> (|100> + |101>)/√2
|110> -> (|110> + |111>)/√2

State: (|000> + |001> + e^(i*pi/3)|010> + e^(i*pi/3)|011> + e^(i*7*pi/12)|100> + e^(i*7*pi/12)|101> + e^(i*11*pi/12)|110> + e^(i*11*pi/12)|111>)/(2√2)

Step 7: swap (three-CNOT decomposition) a and c (q[0] and q[2])
This swaps the first and third qubits:
|000> -> |000>
|001> -> |100>
|010> -> |010>
|011> -> |110>
|100> -> |001>
|101> -> |101>
|110> -> |011>
|111> -> |111>

State: (|000> + |100> + e^(i*pi/3)|010> + e^(i*pi/3)|110> + e^(i*7*pi/12)|001> + e^(i*7*pi/12)|101> + e^(i*11*pi/12)|011> + e^(i*11*pi/12)|111>)/(2√2)

Now for measurement probabilities:
|000>: |1/(2√2)|² = 1/8 = 0.125
|001>: |e^(i*7*pi/12)/(2√2)|² = 1/8 = 0.125
|010>: |e^(i*pi/3)/(2√2)|² = 1/8 = 0.125
|011>: |e^(i*11*pi/12)/(2√2)|² = 1/8 = 0.125
|100>: |1/(2
