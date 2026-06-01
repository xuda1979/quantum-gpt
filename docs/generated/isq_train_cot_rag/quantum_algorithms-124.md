# ISQ training COT RAG corpus: quantum_algorithms shard 124

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/2070

- task_id: `isqTrain/2070`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4739`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
qbit q[2];
procedure main() {
    H(q[0]); H(q[1]);
    T(q[0]);
    S(q[1]);
    H(q[0]); H(q[1]);
    S(q[0]);
    T(q[1]);
    H(q[0]); H(q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

The user wants to analyze an isQ quantum program and predict the probability distribution of the measurement outcomes.
The circuit operates on 2 qubits, q[0] and q[1].
Initial state: |00>
Gates applied:
1. H(q[0]); H(q[1]) -> Both qubits in |+> state.
   State: 1/2 (|00> + |01> + |10> + |11>)
2. T(q[0]); S(q[1]) -> Apply T to q[0], S to q[1].
   T|0> = |0>, T|1> = e^{i\pi/4}|1>
   S|0> = |0>, S|1> = e^{i\pi/2}|1> = i|1>
   State: 1/2 (|00> + i|01> + e^{i\pi/4}|10> + i e^{i\pi/4}|11>)
3. H(q[0]); H(q[1]) -> Apply H to both.
   H(T)H corresponds to a rotation. Wait, let's keep track of the amplitudes directly.
   Amplitudes before this H,H:
   a00 = 1/2
   a01 = i/2
   a10 = e^{i\pi/4}/2
   a11 = i e^{i\pi/4}/2
   
   Wait, let's treat each qubit.
   State of q[0]: 1/sqrt(2) (|0> + e^{i\pi/4}|1>)
   State of q[1]: 1/sqrt(2) (|0> + i|1>)
   Apply H to q[0] and H to q[1].
   H(a|0> + b|1>) = ((a+b)|0> + (a-b)|1>)/sqrt(2)
   q[0] state: 1/sqrt(2) [ (1 + e^{i\pi/4})/sqrt(2) |0> + (1 - e^{i\pi/4})/sqrt(2) |1> ] = 1/2( (1+e^{i\pi/4})|0> + (1-e^{i\pi/4})|1> )
   q[1] state: 1/sqrt(2) [ (1 + i)/sqrt(2) |0> + (1 - i)/sqrt(2) |1> ] = 1/2( (1+i)|0> + (1-i)|1> )
   
4. S(q[0]); T(q[1])
   Apply S to q[0], T to q[1].
   q[0] state: 1/2( (1+e^{i\pi/4})|0> + i(1-e^{i\pi/4})|1> )
   q[1] state: 1/2( (1+i)|0> + e^{i\pi/4}(1-i)|1> )
   
5. H(q[0]); H(q[1])
   Apply H to q[0] and H to q[1].
   q[0] state: 1/(2\sqrt{2}) [ (1+e^{i\pi/4} + i - i e^{i\pi/4})|0> + (1+e^{i\pi/4} - i + i e^{i\pi/4})|1> ]
   Simplify:
   1+e^{i\pi/4} + i - i e^{i\pi/4} = (1+i) + (1-i)e^{i\pi/4} = (1+i)(1 + e^{-i\pi/4} e^{i\pi/2}) = wait...
   Let's just use angles.
   e^{i\pi/4} = (1+i)/sqrt(2)
   1 - e^{i\pi/4} = 1 - (1+i)/sqrt(2)
   i(1 - e^{i\pi/4}) = i + (1-i)/sqrt(2) = i + e^{-i\pi/4}
   
   Let's use a matrix or python to be sure, but I don't have python. I will do it by hand.
   Let the state of q[0] before the second H be: \alpha|0> + \beta|1>
   \alpha = 1/2 (1 + e^{i\pi/4})
   \beta = 1/2 i (1 - e^{i\pi/4})
   After H:
   |0'> = (\alpha

### Reference answer

{'predicted_probs': {'00': 0.7286, '01': 0.125, '10': 0.125, '11': 0.0214}, 'explanation': 'Forrelation circuit with T/S phase oracles on 2 qubits.'}

## isqExpand/algo/74

- task_id: `isqExpand/algo/74`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `vqe`, `bug_fix`, `missing_gate`, `multi_layer_ansatz`
- source: `isq_expansion`
- dataset_index: `5632`

### Prompt

修复以下isQ程序中的错误：

```isq
import std;
qbit q[2];

procedure main() {
    // Layer 1
    Ry(pi/4.0, q[0]);
    Ry(pi/4.0, q[1]);
    CNOT(q[0], q[1]);
    // Layer 2 (BUG: missing Ry on q[1])
    Ry(pi/3.0, q[0]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Bug Analysis
The 2-layer VQE ansatz should have Ry rotations on BOTH qubits in each layer. Layer 2 is missing Ry(pi/3) on q[1].

Buggy output: [0.4435, 0.0167, 0.2333, 0.3065] — the missing rotation on q[1] causes it to skip the intended rotation before the second CNOT.

Correct output: [0.2622, 0.1981, 0.4831, 0.0566] — with both rotations applied.

Fix: Add Ry(pi/3.0, q[1]); between Ry(pi/3.0, q[0]); and the second CNOT.

## isqQA/quantum_algorithms/103_application_scenario

- task_id: `isqQA/quantum_algorithms/103_application_scenario`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `application_scenario`, `algorithm`, `Shor算法概述与量子优势`
- source: `qa_pipeline`
- dataset_index: `4854`

### Prompt

Shor算法在现实世界中最为人熟知的应用场景是破解公钥加密系统（如RSA算法）。请详细阐述Shor算法破解RSA的数学原理，探讨其在密码学领域的实际应用前景及业界应对策略，并在isQ代码框架下展示一个用于Shor算法寻找模幂函数周期、基于量子相位估计（QPE）的核心初始化与受控操作代码示例。

### Reference answer

<tite>
Shor算法在实际应用中最为著名的场景是破解广泛使用的公钥加密系统（如RSA算法）。RSA的安全性建立在大整数质因数分解的计算复杂性上。对于一个极大的整数 $N=p \times q$，经典计算机需要亚指数级乃至指数级的时间来找到质数 $p$ 和 $q$。

**数学推导与原理：**
Shor算法巧妙地将因数分解问题转化为求函数 $f(x) = a^x \pmod N$ 的周期 $r$ 的问题，其中 $a$ 是随机选取的小于 $N$ 且与 $N$ 互质的整数。
1. 构造量子态并利用量子傅里叶变换（QFT）寻找函数 $f(x)$ 的周期 $r$。
2. 如果找到的周期 $r$ 为奇数，则重新选择 $a$ 重复过程。
3. 如果 $r$ 为偶数，我们计算 $\gcd(a^{r/2} \pm 1, N)$。
4. 根据数论推导，由于 $a^r \equiv 1 \pmod N$，我们有 $(a^{r/2} - 1)(a^{r/2} + 1) \equiv 0 \pmod N$。只要 $a^{r/2} \not\equiv -1 \pmod N$，这两个因子中必有一个与 $N$ 的最大公约数恰好是 $p$ 或 $q$。

量子计算机通过QPE在此过程中实现了指数级加速，使得理论上破解数千位的RSA密钥从宇宙年龄级别的时间缩短到几小时。

**实际应用案例与前景：**
1. **密码学安全威胁与“先存储，后破解”**：目前虽然具备数百万物理量子比特的容错量子计算机尚未完全实现，但黑客和情报机构已经开始采用“先截获并存储加密数据，等待未来量子计算机成熟后再行破解”的战略。这使得Shor算法成为悬在当今金融、国防、互联网安全头顶的达摩克利斯之剑。
2. **推动后量子密码学（PQC）与量子密钥分发（QKD）的发展**：正是因为Shor算法的威胁，全球正在加速向不依赖大整数分解困难性的抗量子密码体制（如基于格的密码学）迁移，并大力铺设量子密钥分发网络。Shor算法直接催生了整个“量子安全”产业。
3. **科学计算中的延伸应用**：Shor算法底层的QPE技术本身也是求解复杂物理、化学系统本征能级的通用算法，未来可广泛应用于新材料发现、药物分子模拟等领域。

**isQ 代码示例：**
下面展示Shor算法中寻找模幂函数周期所需的核心环节——量子相位估计（QPE）的前半部分：控制寄存器叠加态的制备与受控模幂运算。由于真实的模幂电路需根据特定的底数 $a$ 和模数 $N$ 动态综合加法器与乘法器，代码中使用自定义的受控门来简化表示这一核心过程。

```isq
import std;

qbit ctrl[4]; // 控制寄存器，用于存储最终反映周期的相位特征态
qbit tgt[4];  // 目标寄存器，初始化为模幂运算的特征态 |u>

// 假设的受控模幂运算门（U_a_N）。在Shor算法中，该门由复杂的模加法器和模乘法器组成
deriving gate cU = [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]];

procedure main() {
    // 1. 初始化目标寄存器。在Shor算法中，由于 |1> 是所有特征态的叠加，通常将目标寄存器初始化为 |1...0>
    X(tgt[0]);

    // 2. 对控制寄存器施加Hadamard门，制备等权叠加态
    for i in 0:4 {
        H(ctrl[i]);
    }

    // 3. 执行受控模幂运算（即受控-U, 受控-U^2, 受控-U^4...）
    // 连续应用受控门，将模幂函数的周期特征映射到控制比特的相对相位上
    ctrl @[ctrl[0]] cU(tgt[0]);
    ctrl @[ctrl[1]] cU(tgt[1]);
    ctrl @[ctrl[2]] cU(tgt[2]);
    ctrl @[ctrl[3]] cU(tgt[3]);

    // 4. 对控制寄存器执行逆量子傅里叶变换
    // 简化展示IQFT的核心结构，提取出相位（即周期的倒数相关信息）
    for i in 0:4 {
        for j in 0:i {
            // 实际此处需根据位置添加精确角度的受控相位旋转门
        }
        H(ctrl[i]);
    }

    // 5. 测量控制寄存器，结果经古典连分数算法处理后即可提取周期 r 
    for i in 0:4 {
        M(ctrl[i]);
    }
}
```
<tite>

## isqTrain/4573

- task_id: `isqTrain/4573`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `multi_controlled_logic`, `reversible_computing`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3190`

### Prompt

Predict the output probabilities of the following quantum circuit:

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
    
    H(q[3]); // superposition on last qubit
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

The task requires analyzing the given isQ program and predicting the probability distribution of measurement outcomes.

First, let's trace the program step-by-step.
q[0], q[1], q[2], q[3] are initialized to |0000>.
X(q[3]); H(q[3]); -> q[3] becomes |->.
H(q[0]); H(q[1]); H(q[2]); -> q[0], q[1], q[2] become |+>|+>|+>.
The state is $|\psi_0\rangle = \frac{1}{2\sqrt{2}} \sum_{x=0}^6 |x\rangle \otimes |-\rangle$. (Note: sum over 8 states, but let's represent it as $|x\rangle|-\rangle$). Wait, actually, sum over all 8 states $x \in \{0,1\}^3$.

The program has `ctrl ctrl ctrl X(q[0], q[1], q[2], q[3]);` which is a Toffoli-like gate on 3 controls and 1 target. It flips `q[3]` when `q[0]`, `q[1]`, `q[2]` are all 1. This is exactly a 3-qubit controlled-X or a 4-qubit Toffoli gate. Wait, `ctrl ctrl ctrl X` means 3 controls. Let's call this $C_3(X)$. The target is flipped if $q[0]=1, q[1]=1, q[2]=1$. Since the target is in $|-\rangle$, applying $X$ to $|-\rangle$ leaves it as $-|-\rangle$. So this acts as an oracle marking $|111\rangle$ with a phase of -1. Thus it is effectively a controlled-Z gate (or a phase oracle) on the 3-qubit space. Let's verify: the oracle is $O|x\rangle = -|x\rangle$ for $x=111$, and $O|x\rangle = |x\rangle$ otherwise. Wait, the target is $|-\rangle$, so $C_3(X)|x\rangle|-\rangle = (-1)^{x_0 x_1 x_2} |x\rangle|-\rangle$. So the state after the first oracle is:
$|\psi_1\rangle = \frac{1}{2\sqrt{2}} \sum_{x=0}^6 |x\rangle \otimes |-\rangle - \frac{1}{2\sqrt{2}} |111\rangle \otimes |-\rangle$.

Then `diffuser()` is called.
The diffuser acts on `q[0], q[1], q[2]`.
`H(q[0]); H(q[1]); H(q[2]);`
`X(q[0]); X(q[1]); X(q[2]);`
`ctrl ctrl my_z(q[0], q[1], q[2]);` - this is a controlled-Z gate (since my_z applies Z to the target). Wait! The controls are `q[0]`, `q[1]`, and the target is `q[2]`?
Let's check the syntax: `ctrl ctrl my_z(q[0], q[1], q[2]);`
`my_z` takes one qubit `a`. So `ctrl ctrl my_z(q[0], q[1], q[2])` means controls are `q[0], q[1]`, and the target of `my_z` is `q[2]`. So it's $CZ_{012}$. But wait! $CZ_{012}$ applies Z to q[2] when q[0]=1 and q[1]=1. Wait, no. Is `ctrl ctrl my_z(q[0], q[1], q[2])` a double-controlled-Z (ctrl @[c1, c2] Z(target)) gate?
Yes, `ctrl ctrl Gate(t)` means 2 controls, 1 target. If we write `ctrl ctrl my_z(q[0], q[1], q[2])`, it means controls are `q[0], q[1]` and target is `q[2]`. But wait! A double-controlled-Z (ctrl @[c1, c2] Z(target)) gate is an 8x8 diagonal matrix with a -1 at the last element.
Wait, let's look at `ctrl ctrl my_z(q[0], q[1], q[2])`. The controls are `q[0]` and `q[1]`, the target is `q[2]`. This applies Z to `q[2]` when `q[0]` and `q[1]` are 1. So it multiplies $|11x_2\rangle$ by -1 regardless of

### Reference answer

{'predicted_probs': {'0000': 0.007813, '0001': 0.007813, '0010': 0.007813, '0011': 0.007813, '0100': 0.007813, '0101': 0.007813, '0110': 0.007813, '0111': 0.945312}, 'explanation': 'This isQ program operates on 4 qubit(s). The measurement probability distribution is: P(|0000>) = 0.0078, P(|0001>) = 0.0078, P(|0010>) = 0.0078, P(|0011>) = 0.0078, P(|0100>) = 0.0078, P(|0101>) = 0.0078, P(|0110>) = 0.0078, P(|0111>) = 0.9453.'}

## isqTrain/3952

- task_id: `isqTrain/3952`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `5566`

### Prompt

This isQ program doesn't produce the correct output. Can you debug it?

Code:
```
import std;
// QAOA MaxCut p=1 on 3-node triangle graph
// gamma=1.000, beta=0.500
qbit q[3];

procedure main() {
    // Initial superposition
    H(q[0]); H(q[1]); H(q[2]);
    // Cost unitary U_C(gamma)
    // Edge (0,1): exp(-i*gamma*Z_i*Z_j)
    CNOT(q[0], q[1]);
    Rz(2.0 * 1.000, q[1]);
    CNOT(q[0], q[1]);
    // Edge (1,2): exp(-i*gamma*Z_i*Z_j)
    CNOT(q[1], q[2]);
    Rz(2.0 * 1.000, q[2]);
    CNOT(q[1], q[2]);
    // Edge (0,2): exp(-i*gamma*Z_i*Z_j)
    CNOT(q[0], q[2]);
    Rz(2.0 * 1.000, q[2]);
    CNOT(q[0], q[2]);
    // Mixer unitary U_M(beta)
    Ry(2.0 * 0.500, q[0]);
    Rx(2.0 * 0.500, q[1]);
    Rx(2.0 * 0.500, q[2]);
    // Measure
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug identification**: In the Mixer unitary `U_M(beta)` section, line `Ry(2.0 * 0.500, q[0])` uses `Ry` instead of `Rx`. The QAOA mixer applies `Rx(2β)` uniformly to all qubits, but q[0] incorrectly received an `Ry` rotation.

2. **Fix**: Change `Ry(2.0 * 0.500, q[0])` to `Rx(2.0 * 0.500, q[0])` so all three qubits receive the same X-mixer rotation.

3. **State evolution (corrected)**: After H gates: `|+++>`. Cost unitary applies `exp(-iγ Z⊗Z)` for each edge via CNOT-Rz(2γ)-CNOT on pairs (0,1), (1,2), (0,2), entangling the qubits with phase encoding. Mixer unitary then applies `Rx(1.0)` to each qubit, rotating around X by `2β = 1.0 rad`. This produces a symmetric state where `|000>` and `|111>` have elevated probability (~0.216) and the six single-spin-flip states have equal lower probability (~0.095), matching the predicted output.

## isqQA/quantum_algorithms/90_isq_implementation

- task_id: `isqQA/quantum_algorithms/90_isq_implementation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_implementation`, `algorithm`, `Bernstein-Vazirani算法原理`
- source: `qa_pipeline`
- dataset_index: `494`

### Prompt

请用isQ语言编写一个完整的Bernstein-Vazirani算法量子程序。假设隐藏的比特串为 $s=1011$，要求包含全局量子比特声明、初始化以及必要的量子门操作，并在代码中提供详尽的逐行中文注释，解释算法并行计算内积的原理。

### Reference answer

<think>
首先，明确Bernstein-Vazirani算法的核心数学映射：利用Hadamard变换的对称性和相位Kickback机制，将隐藏比特串 $s=1011$ 的内积计算转化为量子态的相位翻转，最终通过量子干涉提取出 $s$。因为 $s$ 的长度为4，推理的第一步是确定量子资源，即需要分配4个查询量子比特和1个辅助量子比特。

接着，规划isQ代码的逻辑结构。首先进行全局量子比特声明与初始化，使用X门将辅助比特置为 $|1\rangle$，并对全部5个比特施加Hadamard门，使其进入均匀叠加态与 $|-\rangle$ 态。

随后，设计最关键的Oracle量子线路。根据 $s=1011$（从右至左或定义好高低位），在辅助比特与对应位置为1的查询比特之间施加CNOT门。这一步巧妙地利用了辅助比特的 $|-\rangle$ 态，使内积结果以相位的形式并行作用于整个查询寄存器。

最后，进行干涉还原与测量。仅需对前4个查询比特再次施加Hadamard门，此时的量子干涉会将包含特定相位的叠加态直接坍缩为目标比特串 $1011$。在编写代码时，围绕这一推导顺序逐步使用isQ语法，并辅以原理解释即可完成程序。
</think>

### 算法原理
Bernstein-Vazirani算法旨在寻找一个隐藏的比特串 $s$。在经典计算中，我们需要 $n$ 次查询 oracle 才能确定 $n$ 位的 $s$。而在量子计算中，利用量子叠加和相位反转（相位 kickback 机制），只需 $1$ 次查询即可完成。

算法的核心步骤如下：
1. 初始化 $n$ 位查询寄存器为 $|0\rangle^{\otimes n}$，1位辅助寄存器为 $|1\rangle$。
2. 对所有量子比特应用 Hadamard 门，使其进入均匀叠加态。辅助比特变为 $| - \rangle$ 态。
3. 查询量子 Oracle $U_f$。由于辅助比特处于 $| - \rangle$ 态，Oracle 计算函数 $f(x) = s \cdot x \pmod 2$ 的结果会以相位 $(-1)^{f(x)}$ 的形式Kickback（反向施加）到查询寄存器的态 $|x\rangle$ 上。
4. 再次对查询寄存器应用 Hadamard 门。由于 $H^{\otimes n} \sum_x (-1)^{s\cdot x}|x\rangle = |s\rangle$，测量查询寄存器即可直接得到隐藏比特串 $s$。

### isQ 代码实现
以下是隐藏比特串为 $s=1011$ 的完整 isQ 代码实现：

```isQ
import std;

// 全局声明5个量子比特。
// q[0] 到 q[3] 用作 4 位的查询寄存器。
// q[4] 用作辅助寄存器。
qbit q[5];

procedure main() {
    // 1. 辅助比特初始化
    // 将 q[4] 初始化为 |1> 状态，以便后续转换为 |- => 状态
    X(q[4]);

    // 2. 创建叠加态
    // 对所有量子比特（包括辅助比特）应用 Hadamard 门
    for i in 0:5 {
        H(q[i]);
    }

    // 3. 构造并应用 Bernstein-Vazirani Oracle
    // 隐藏比特串 s = 1011。根据 Oracle 定义，对 s 中值为 1 的位，我们以对应的查询比特为控制位，对辅助比特应用 CNOT 门。
    // 查询寄存器的状态为 |x1 x2 x3 x4>。
    // 对应 s 的第 0 位（最左侧，值为 1），若 x1=1 则辅助比特翻转
    CNOT(q[0], q[4]);
    // 对应 s 的第 1 位（值为 0），无需操作，跳过
    // 对应 s 的第 2 位（值为 1），若 x3=1 则辅助比特翻转
    CNOT(q[2], q[4]);
    // 对应 s 的第 3 位（最右侧，值为 1），若 x4=1 则辅助比特翻转
    CNOT(q[3], q[4]);

    // 4. 干涉与还原
    // 对查询寄存器再次应用 Hadamard 门，将相位信息转化为计算基态的概率幅
    for i in 0:4 {
        H(q[i]);
    }

    // 5. 测量
    // 对查询寄存器进行测量，由于干涉相长，结果将以 100% 的概率坍缩为隐藏字符串 1011
    for i in 0:4 {
        M(q[i]);
    }
}
```

### 代码深度解析
在这个 isQ 程序中，最精妙的地方在于 Phase Kickback（相位反向）机制。当辅助比特处于 $H|1\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}$ 状态时，它实际上是一个特征值为 $-1$ 的特征态。

当我们执行 `CNOT(q[i], q[4])` 时，这看似是在操作辅助比特，但实际上，由于量子力学的奇妙性质，如果控制比特 $q[i]$ 处于 $|1\rangle$ 状态，辅助比特会经历 $X$ 门操作，导致 $|0\rangle - |1\rangle$ 变为 $|1\rangle - |0\rangle = - (|0\rangle - |1\rangle)$。这个 $-1$ 的全局相位并没有留在辅助比特上，而是被“踢回”到了控制比特 $q[i]$ 上。

因此，对于一般态 $|x_1 x_2 x_3 x_4\rangle$，它将获得 $(-1)^{x_1 \cdot 1 + x_2 \cdot 0 + x_3 \cdot 1 + x_4 \cdot 1} = (-1)^{s \cdot x}$ 的相位。第二次施加 Hadamard 门相当于进行了一次量子傅里叶逆变换，抵消了第一次 Hadamard 门产生的均匀叠加，使得只有当查询态与隐藏态 $s=1011$ 完全相同时，所有的振幅才会相长干涉，从而使得我们在真实量子硬件或模拟器上运行此段 isQ 代码时，能够确定性地一次找出这个 4 位的隐藏密钥。

## isqTrain/24

- task_id: `isqTrain/24`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `414`

### Prompt

Code this in isQ: implements the qft_subcircuit pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

The user wants me to analyze the isQ quantum program that implements a QFT subcircuit with identity operations (X-X pair).

Let me trace through the circuit:

1. Initial state: |000>

2. X(q[2]) flips q[2]: |001>

3. QFT3 procedure is applied:
   - H(a) where a=q[0]: H on q[0] of |001> → (|001> + |101>)/√2
   - ctrl Rz(π/2, b, a) where b=q[1], a=q[0]: controlled Rz(π/2) with q[0] as target, q[1] as control
     When q[1]=|1>, apply Rz(π/2) to q[0]. But q[1] is |0> in both terms, so nothing changes.
   - ctrl Rz(π/4, c, a) where c=q[2], a=q[0]: controlled Rz(π/4) with q[0] as target, q[2] as control
     When q[2]=|1>, apply Rz(π/4) to q[0]. Both terms have q[2]=|1>, so:
     |001> → e^{-iπ/8}|001>
     |101> → e^{iπ/8}|101>
     State becomes: (e^{-iπ/8}|001> + e^{iπ/8}|101>)/√2
   
   Wait, let me re-read the QFT3. The parameters are (qbit a, qbit b, qbit c), and we call qft3(q[0], q[1], q[2]).
   
   So a=q[0], b=q[1], c=q[2].

   In isQ, `ctrl Rz(pi/2.0, b, a)` means controlled Rz with b as control and a as target? Or is it Rz(theta, target) and ctrl means the next qubit is the control?
   
   Actually, looking at the isQ syntax reference:
   - Rz(theta, q) is a single-qubit gate
   - ctrl modifier: `ctrl @[c1, c2] Gate(target);`
   
   But in the code it's written as `ctrl Rz(pi/2.0, b, a)` which seems like Rz with two qubits. This is confusing.
   
   Wait, let me look again. The syntax `ctrl Rz(pi/2.0, b, a)` - in isQ, for controlled gates, the convention might be different. Let me assume the standard QFT convention:
   
   Actually, in the reference code it says:
   
   
   This is likely a controlled-Rz gate where b is the control and a is the target, or maybe the parameter order is (angle, control, target).
   
   Let me look at the standard QFT algorithm:
   - For qubit q[k], apply H(q[k])
   - Then for each j > k, apply controlled-Rz(2π/2^{j-k+1}) with q[j] as control and q[k] as target
   
   For 3-qubit QFT on qubits q[0], q[1], q[2]:
   - H(q[0])
   - CRz(π/2) with q[1] control, q[0] target (but wait, in QFT it should be 2π/2^2 = π/2)
   - CRz(π/4) with q[2] control, q[0] target
   - H(q[1])
   - CRz(π/2) with q[2] control, q[1] target
   - H(q[2])
   - swap (three-CNOT decomposition) q[0] and q[2]
   
   This matches the code! So `ctrl Rz(pi/2.0, b, a)` means controlled-Rz with angle π/2, control b, target a.
   
   Actually wait, I need to reconsider. In standard QFT, the controlled rotation is applied to the target qubit based on the control. The rotation angle for CRk gate is 2π/2^k.
   
   For QFT on 3 qubits (a, b, c):
   - H(a)
   - CRz(2π/2^2, b→a) = CRz(π/2, b→a)
   - CRz(2π/2^3, c→a) = CRz(π/4, c→a)
   - H(b)
   - CRz(2π/2^2, c→b

## isqTrain/3964

- task_id: `isqTrain/3964`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `1674`

### Prompt

这个isQ程序有问题，请找出错误并给出正确代码：

```
import std;
// QAOA MaxCut p=1 on 3-node triangle graph
// gamma=0.500, beta=1.000
qbit q[3];

procedure main() {
    // Initial superposition
    H(q[0]); H(q[1]); H(q[2]);
    // Cost unitary U_C(gamma)
    // Edge (0,1): exp(-i*gamma*Z_i*Z_j)
    CNOT(q[0], q[1]);
    Rz(2.0 * 0.500, q[1]);
    CNOT(q[0], q[1]);
    // Edge (1,2): exp(-i*gamma*Z_i*Z_j)
    CNOT(q[1], q[2]);
    Rz(2.0 * 0.500, q[2]);
    CNOT(q[2], q[1]);
    // Edge (0,2): exp(-i*gamma*Z_i*Z_j)
    CNOT(q[0], q[2]);
    Rz(2.0 * 0.500, q[2]);
    CNOT(q[0], q[2]);
    // Mixer unitary U_M(beta)
    Rx(2.0 * 1.000, q[0]);
    Rx(2.0 * 1.000, q[1]);
    Rx(2.0 * 1.000, q[2]);
    // Measure
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: swapped qubits)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug location**: Line 19 — the second CNOT in the Edge (1,2) ZZ-interaction block has swapped qubits: `CNOT(q[2], q[1])` instead of `CNOT(q[1], q[2])`.

2. **Why it's wrong**: The ZZ-phase unitary `exp(-iγ Z₁Z₂)` is implemented via the CNOT-Rz-CNOT sandwich. The two CNOTs must have identical control/target roles so the second CNOT uncomputes the parity mapping. With swapped arguments, the second CNOT fails to restore the computational basis, leaving qubits entangled incorrectly and corrupting the cost unitary.

3. **Fix**: Change `CNOT(q[2], q[1])` → `CNOT(q[1], q[2])` so both CNOTs in the (1,2) edge block match.

4. **State evolution (corrected)**:
   - After H gates: `|+++⟩`
   - Edge (0,1) ZZ(γ): applies `exp(-iγ Z₀Z₁)` correctly via CNOT₀₁–Rz(2γ,q₁)–CNOT₀₁
   - Edge (1,2) ZZ(γ): applies `exp(-iγ Z₁Z₂)` correctly via CNOT₁₂–Rz(2γ,q₂)–CNOT₁₂
   - Edge (0,2) ZZ(γ): applies `exp(-iγ Z₀Z₂)` correctly via CNOT₀₂–Rz(2γ,q₂)–CNOT₀₂
   - Mixer U_M: Rx(2β) on each qubit rotates in X-basis, producing the expected QAOA output distribution with |000⟩ and |111⟩ having elevated probability ~0.2155, and all other states ~0.0948.

## isqExpand/qa/45

- task_id: `isqExpand/qa/45`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `HHL算法`, `线性方程组`, `量子相位估计`, `哈密顿量模拟`, `量子态制备`, `条件数`
- source: `qa_pipeline`
- dataset_index: `725`

### Prompt

HHL算法的前提条件和限制是什么？为什么不是所有线性方程组都能用HHL高效求解？

### Chain-of-thought reasoning

## 推理
首先分析HHL算法的数学原理，HHL旨在将经典向量 $b$ 转化为量子态 $|b\rangle$，利用量子相位估计求出矩阵 $A$ 的特征值，并通过受控旋转实现求倒数操作，最终得到 $|x\rangle \propto A^{-1}|b\rangle$。然后，逐步拆解影响该算法复杂度的关键因素：1) 矩阵 $A$ 的稀疏性和条件数决定相位估计的深度和旋转的精度；2) $b$ 的量子态编码（QRAM瓶颈）是输入困难点；3) 测量坍缩导致无法提取完整经典解（输出困难点）。明确了这些限制后，结合isQ的语法结构编写概念性的代码展示QPE和旋转过程，最终整理成连贯的中文解释和JSON格式。

### Reference answer

HHL算法（由Harrow, Hassidim和Lloyd提出）是量子线性系统求解算法，旨在求解线性方程组 $A\mathbf{x} = \mathbf{b}$。理论上，HHL算法对系统规模 $N$ 能够提供指数级加速，但这建立在极其严格的前提条件之上，并非所有线性方程组都能从中受益。

### 一、 HHL算法的前提条件

1. **稀疏性与良好条件数**：矩阵 $A$ 必须是稀疏矩阵，且其条件数 $\kappa = \|A\|\|A^{-1}\|$ （最大奇异值与最小奇异值之比）不能太大。算法的复杂度与 $\kappa$ 多项式相关，理想情况下要求 $\kappa = \text{poly}(\log N)$。
2. **高效的哈密顿量模拟**：必须存在某种高效的方法将矩阵 $A$ 转换为量子线路。即在时间 $t$ 内演化算符 $e^{-iAt}$ 的量子电路复杂度应为 $\text{poly}(\log N)$。
3. **高效的量子态准备**：右端项向量 $\mathbf{b}$ 必须能够通过高效的量子线路加载，即存在一个多项式时间复杂度的 Oracle 能够生成量子态 $|b\rangle = \sum_i b_i |i\rangle / \|\mathbf{b}\|$。

### 二、 为什么不是所有线性方程组都能用HHL高效求解？

HHL算法存在几个根本性的限制，导致其在实际应用中难以直接替代经典算法：

1. **数据输入瓶颈**：如果 $\mathbf{b}$ 是经典数据，将其编码到量子态 $|b\rangle$ 通常需要 $\mathcal{O}(N)$ 的时间，这直接抹杀了了算法在规模 $N$ 上的指数级加速。
2. **信息输出瓶颈（读取问题）**：HHL的输出是一个编码了解 $\mathbf{x}$ 的量子态 $|x\rangle \propto A^{-1}|b\rangle$，而非经典向量。由于海森堡测不准原理和量子态坍缩，提取 $|x\rangle$ 的全部振幅信息需要 $\mathcal{O}(N)$ 次重复测量。因此，HHL仅对提取某些全局信息（如计算内积 $\mathbf{x}^T M \mathbf{x}$ 或观测期望值）具有实际意义，不能用于求解具体的 $x_i$。
3. **条件数的限制**：当矩阵 $A$ 是病态矩阵时（即 $\kappa$ 很大），HHL中的受控旋转精度要求极高，导致电路深度呈指数级增长。
4. **哈密顿量模拟困难**：对于非稀疏的稠密矩阵，目前没有高效的通用方法实现 $e^{-iAt}$ 的模拟，因此稠密矩阵系统无法获得量子加速。

### 三、 isQ代码示例（HHL算法结构）

HHL算法包含三个主要量子步骤：量子相位估计（QPE）、受控旋转和逆量子相位估计（IQPE）。以下是在 isQ 中展示这些步骤的结构性伪代码：

```isq
import std;

qbit ancilla[1];
qbit clock[2]; // 假设特征值的相位用2个比特估计
qbit input[1]; // 用于编码 |b>

procedure main() {
    // 1. 准备输入态 |b> (此处省略具体的制备Oracle)
    // 假设 input 已被初始化为 |b>

    // 2. 对时钟寄存器应用 Hadamard 门
    H(clock[0]);
    H(clock[1]);

    // 3. 量子相位估计 (QPE)
    // 通过受控的哈密顿量模拟 e^{-iAt} 将特征值提取到时钟寄存器
    // 控制位为 clock，目标位为 input
    // ctrl @[clock[0]] HamSimA(input); 
    // ctrl @[clock[1]] HamSimA2(input);

    // 4. 受控旋转
    // 利用时钟寄存器计算出的特征值的倒数，在辅助比特上进行 Y轴旋转
    // 旋转角度 theta 与 1/lambda 成正比
    // Ry(theta, ancilla[0]);

    // 5. 逆量子相位估计 (IQPE)
    // 将时钟寄存器解纠缠，恢复为特征向量状态
    // 由于 isQ 没有直接的逆语法，使用标准的 IQPE 步骤
    // ctrl @[clock[1]] inv HamSimA2(input);
    // ctrl @[clock[0]] inv HamSimA(input);
    H(clock[1]);
    H(clock[0]);

    // 6. 测量辅助比特
    // 当测量结果为 |1> 时，input 寄存器中即为与解成正比的态 A^{-1}|b>
    M(ancilla[0]);
}
```

## isqTrain/3724

- task_id: `isqTrain/3724`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `537`

### Prompt

Code this in isQ: QAOA (p=1) for MaxCut on a 4-node complete graph with edges [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)], gamma=0.500, beta=0.500. Use CNOT-Rz-CNOT for cost unitary and Rx for mixer.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for a QAOA MaxCut circuit with p=1 on a 4-node complete graph.

Let me trace through the circuit:

1. Goal: Implement QAOA p=1 for MaxCut on K4 to find bipartitions maximizing cut edges.

2. Qubits: 4 qubits q[0]-q[3], all measured.

3. State evolution:
- Start: |0000>
- After H on all: |++++> = uniform superposition
- Cost unitary: For each edge (i,j), apply CNOT(i,j), Rz(2γ, j), CNOT(i,j). This implements controlled-Z with phase e^{-iγ} or e^{iγ} depending on whether qubits agree.
- The cost unitary for MaxCut applies phase e^{iγ} to states where connected qubits are in different partitions and e^{-iγ} when same.
- For complete graph K4 with 6 edges, each edge contributes a phase.
- States with equal bipartitions (like |0011>, |0101>, |0110>, |1001>, |1010>, |1100>) cut 4 edges.
- States with 1-3 split (like |0001>, |0010>, |0100>, |1000>, |0111>, |1011>, |1101>, |1110>) cut 3 edges.
- States |0000> and |1111> cut 0 edges.
- Mixer: Rx(2β) on all qubits, mixing |0> and |1> states.

4. With γ=β=0.5:
- the predicted output show highest values for |0000> and |1111> (~0.316), moderate for balanced bipartitions (~0.058), and very low for unbalanced single-qubit states (~0.002).

Let me verify the phases more carefully. The ZZ interaction from CNOT-Rz(2γ)-CNOT gives:
- When qubits same: e^{-iγ}
- When qubits different: e^{iγ}

For state |0000>: all 6 edges have same qubits → phase = e^{-6iγ}
For |0011>: edges (0,1)=same, (0,2)=diff, (0,3)=diff, (1,2)=diff, (1,3)=diff, (2,3)=same → 4 diff, 2 same → phase = e^{4iγ}e^{-2iγ} = e^{2iγ}
For |0001>: 3 diff, 3 same → phase = e^{0} = 1... wait, let me recalculate.

Actually, for MaxCut the cost Hamiltonian is H_C = Σ_{(i,j)} Z_i Z_j, and we apply e^{-iγH_C}. The ZZ unitary gives phase e^{-iγ} when Z_i Z_j = +1 (same partition) and e^{iγ} when Z_i Z_j = -1 (different partition).

Wait, I need to be more careful. The standard MaxCut QAOA uses:
U_C(γ) = e^{-iγ Σ_{(i,j)} (1-Z_i Z_j)/2}

Or equivalently, for each edge, we apply a phase that depends on whether the edge is cut.

Actually, the CNOT-Rz(2γ)-CNOT implements a ZZ rotation:
CNOT-Rz(2γ)-CNOT = e^{-iγ Z_c Z_t}

So when Z_c Z_t = +1 (same), phase = e^{-iγ}
When Z_c Z_t = -1 (different), phase = e^{iγ}

For state |0000>: Z_i = +1 for all, so Z_i Z_j = +1 for all 6 edges → total phase = e^{-6iγ}
For |0011>: Z_0=+1, Z_1=+1, Z_2=-1, Z_3=-1
  (0,1): Z_0 Z_1 = +1
  (0,2): Z_0 Z_2 = -1
  (0,3): Z_0 Z_3 = -1
  (1,2): Z_1 Z_2 = -1
  (1,3): Z_1 Z_3 = -1
  (2,3): Z_2 Z_3 = +1
  Sum = 1-1-1-1-1+1 = -2 → phase = e^{2iγ}

For |0001>: Z_0=+1, Z_1=+1, Z_2=+1, Z_3=-1
  (0,1): +1, (
