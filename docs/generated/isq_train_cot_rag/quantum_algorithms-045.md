# ISQ training COT RAG corpus: quantum_algorithms shard 45

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3038

- task_id: `isqTrain/3038`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `measurement_order`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3530`

### Prompt

用isQ实现applies nctrl X with X init. The nctrl modifier means the gate is applied when the control qubit is |0>.

Requirements:
- Declare `qbit q[2];` at global scope.
- Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply an X gate to q[0] (initializing it to |1⟩), then conditionally apply X to q[1] only when q[0] is |0⟩ (nctrl modifier).
2. **Qubits**: 2 qubits declared globally; both measured.
3. **State evolution**:
   - Initial state: |00⟩
   - After `X(q[0])`: |10⟩
   - After `nctrl X(q[0], q[1])`: Control q[0] is |1⟩, so the negative control condition (control = |0⟩) is not met; no operation on q[1]. State remains |10⟩.
4. **Expected result**: Measurement yields |10⟩ with probability 1.0, since q[0] = |1⟩ and q[1] = |0⟩.

## isqTrain/977

- task_id: `isqTrain/977`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `basis_change`, `entanglement`, `hamiltonian_simulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1988`

### Prompt

I need an isQ program to implements the lie_trotter pattern with modified rotation parameters (num_pi2_to_pi4). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

The user is asking me to generate the reasoning section for this isQ quantum program. I need to analyze the circuit and explain it step by step.

Analyzing the code:
- This is a Lie-Trotter decomposition of the Heisenberg Hamiltonian H = XX + YY + ZZ
- Time t = π/16 ≈ 0.196349540849362
- The evolution is e^(-i*t*H) = e^(-i*t*(XX + YY + ZZ)) ≈ e^(-i*t*ZZ) * e^(-i*t*XX) * e^(-i*t*YY)
- Initial state is |10⟩

Let me trace through:

1. Start with |00⟩, apply X(q[0]) → |10⟩

2. Term 1: e^(-i*t*ZZ) - uses CNOT-Rz(2t)-CNOT
   - CNOT(q[0], q[1]): |10⟩ → |11⟩
   - Rz(2t) on q[1]: |11⟩ → e^(-it)|11⟩
   - CNOT(q[0], q[1]): e^(-it)|11⟩ → e^(-it)|10⟩

3. Term 2: e^(-i*t*XX) - uses H-CNOT-Rz(2t)-CNOT-H
   - H(q[0])H(q[1]): e^(-it)|10⟩ → e^(-it)|-+⟩ (need to be more careful here)
   
Actually let me be more careful. |10⟩ with H on both:
   H|1⟩ = |−⟩
   H|0⟩ = |+⟩
   So |10⟩ → |−+⟩

Then CNOT(q[0], q[1]):
   |−+⟩ = 1/2(|00⟩ - |10⟩ + |01⟩ - |11⟩)
   CNOT: |00⟩ → |00⟩, |10⟩ → |11⟩, |01⟩ → |01⟩, |11⟩ → |10⟩
   So CNOT|−+⟩ = 1/2(|00⟩ - |11⟩ + |01⟩ - |10⟩) = 1/2(|0⟩(|0⟩+|1⟩) - |1⟩(|1⟩+|0⟩)) = -|−+⟩... wait let me redo this.

Actually |−+⟩ = (1/2)(|0⟩-|1⟩)(|0⟩+|1⟩) = (1/2)(|00⟩+|01⟩-|10⟩-|11⟩)

CNOT(q[0], q[1]) on this:
|00⟩ → |00⟩
|01⟩ → |01⟩  
|10⟩ → |11⟩
|11⟩ → |10⟩

So CNOT|−+⟩ = (1/2)(|00⟩+|01⟩-|11⟩-|10⟩) = (1/2)(|00⟩+|01⟩-|10⟩-|11⟩) = |−+⟩ (it's an eigenstate of the XX-like interaction after the basis change)

Hmm, actually this is getting complex. Let me think about this differently.

The overall circuit implements U = e^(-it*ZZ) * e^(-it*XX) * e^(-it*YY) applied to |10⟩.

For the Trotter decomposition of the Heisenberg model, each term:
- e^(-it*ZZ): CNOT-Rz(2t)-CNOT
- e^(-it*XX): H-CNOT-Rz(2t)-CNOT-H
- e^(-it*YY): Rx(π/2)-CNOT-Rz(2t)-CNOT-Rx(-π/2)

the predicted output probabilities are:
|00⟩: 0.009515058436089139
|01⟩: 0.08273836313945242
|10⟩: 0.8982315199883694
|11⟩: 0.00951505843608916

The dominant state is |10⟩ with about 89.8% probability.

Let me write a concise reasoning:

1. Goal: Implement Lie-Trotter decomposition for Heisenberg Hamiltonian H=XX+YY+ZZ with t=π/16 on initial state |10⟩

2. 2 qubits, both measured

3. State evolution:
   - Start: |00⟩ → X(q[0]) → |10⟩
   - Term ZZ: CNOT-Rz(2t)-CNOT applies e^(-it*ZZ)
   - Term XX

## isqQA/quantum_algorithms/130_hardware_limitations

- task_id: `isqQA/quantum_algorithms/130_hardware_limitations`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `hardware_limitations`, `algorithm`, `门隐形传态`
- source: `qa_pipeline`
- dataset_index: `5060`

### Prompt

在NISQ（含噪中等规模量子）设备上执行分布式量子算法时，物理量子比特的有限连通性和退相干效应是主要瓶颈。请详细分析如何通过“门隐形传态”（Gate Teleportation，如远程CNOT门）策略来克服硬件拓扑连通性限制，并阐述T1弛豫与T2相位退相干对该过程纠缠分发及保真度的影响。此外，请使用isQ语言编写一个示例代码，展示如何利用预共享的纠缠对和经典前馈控制来实现无需直接物理耦合的远程受控量子门，并尽量优化线路深度以抵抗退相干。

### Reference answer

在当前的NISQ（含噪中等规模量子）时代，量子处理器的物理架构面临着严重的拓扑连通性限制（如超导量子计算中的最近邻耦合限制）和极短的相干时间。如果要在两个物理上不相邻的量子比特之间执行多量子比特门，传统方法是通过一连串的SWAP操作将量子态搬运到相邻位置。然而，每个SWAP门通常需要分解为3个CNOT门，这不仅极大地增加了线路深度，还使得错误率呈指数级累积。\n\n为了克服这一硬件局限，我们可以引入“门隐形传态”机制，特别是构建远程CNOT门。这种技术不再依赖物理上的直接接触，而是利用预先分发好的贝尔态（Bell State）作为量子信道，结合局域操作和经典通信（LOCC）来实现非局域的量子门。\n\n**退相干（T1弛豫与T2相位退相干）的影响分析：**\n在门隐形传态的过程中，最大的挑战在于纠缠对的准备与保持。量子比特在空闲或等待经典信号时，极易受到噪声干扰。T1弛豫（能量弛豫）会导致激发态衰减为基态，直接破坏纠缠态的量子叠加性；而T2相位退相干则会使量子态的相对相位发生随机漂移。如果从纠缠分发到执行门操作之间的延迟过长，纠缠质量将严重下降，导致最终隐形传态的保真度暴跌。因此，在NISQ设备上实现门隐形传态，必须最大程度地压缩线路深度，并利用极低的经典通信延迟完成前馈控制。\n\n以下是基于isQ语言实现的抗退相干优化的远程CNOT门（门隐形传态）代码。假设控制比特 `q[0]` 与目标比特 `q[3]` 物理上不相邻，我们利用 `q[1]` 和 `q[2]` 作为中继纠缠对：\n\n```isq\nimport std;\n\nqbit q[4]; // q[0]: 控制比特, q[1]与q[2]: 共享纠缠对, q[3]: 目标比特\n\nprocedure main() {\n    // 1. 纠缠分发：在 q[1] 和 q[2] 之间建立贝尔态\n    H(q[1]);\n    CNOT(q[1], q[2]);\n\n    // 2. 控制端本地操作：将 q[0] 与纠缠对的一部分交互\n    CNOT(q[0], q[1]);\n    H(q[0]);\n\n    // 3. 测量获取Pauli帧\n    // 为了抵抗退相干，测量应尽可能快地执行以切断与环境的纠缠\n    int m0 = M(q[0]);\n    int m1 = M(q[1]);\n\n    // 4. 经典前馈控制：根据测量结果对目标系统进行Pauli修正\n    // 通过快速经典信号触发微波脉冲，实现低延迟的动态解耦\n    if (m1 == 1) {\n        X(q[2]);\n    }\n    if (m0 == 1) {\n        Z(q[2]);\n    }\n\n    // 5. 目标端完成非局域相互作用\n    CNOT(q[2], q[3]);\n}\n```\n\n**代码与硬件优化策略解析：**\n在上述代码中，我们避免了在 `q[0]` 和 `q[3]` 之间引入漫长的SWAP网络，而是用一层纠缠分发（深度为2）和一层本地操作（深度为2）替代。这种安排极大地缩短了活动量子门的通过时间，从而削弱了T1和T2退相干的负面效应。此外，中间量子比特 `q[0]` 和 `q[1]` 在测量后即被解构，阻断了进一步向环境泄露量子信息的途径。在实际NISQ硬件部署时，还需配合底层的动态解耦（Dynamical Decoupling）脉冲序列填充空闲期，确保最终的远程门保真度达到算法可容忍的阈值。

## isqQA/quantum_algorithms/115_principle_advantage

- task_id: `isqQA/quantum_algorithms/115_principle_advantage`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `principle_advantage`, `algorithm`, `HHL中的受控旋转步骤`
- source: `qa_pipeline`
- dataset_index: `2693`

### Prompt

在HHL量子算法中，受控旋转步骤承担了将特征值倒数信息编码到振幅中的重任。请详细阐述受控旋转的宏观原理，探讨实现该操作的时间复杂度，并分析这一步骤为何能成为HHL算法相较于经典算法产生指数级加速的关键来源之一？

### Reference answer

在HHL量子算法中，受控旋转步骤是连接量子相位估计与最终求解的桥梁，其核心目的在于将寄存器中编码的特征值信息非线性地映射为振幅，从而提取出特征值的倒数。以下是该步骤的原理剖析与复杂度分析。

**宏观原理：**
假设我们求解线性方程组 $Ax = b$。经过量子相位估计后，系统演化至状态 $\sum_j \beta_j |u_j\rangle |\lambda_j\rangle$，其中 $|u_j\rangle$ 是 $A$ 的特征向量，$\lambda_j$ 是对应的特征值，$\beta_j$ 是初始状态 $|b\rangle$ 在特征基下的展开系数。此时，特征值 $\lambda_j$ 被编码在辅助寄存器中。
受控旋转步骤引入一个附加的辅助量子比特。根据 $\lambda_j$ 的值，对该辅助比特执行条件旋转 $R_y(\theta_j)$，其中旋转角度 $\theta_j$ 满足 $\sin(\theta_j) = C/\lambda_j$（$C$ 为归一化常数）。在量子线路中，这通常通过计算 $\arcsin(C/\lambda_j)$ 并将其转化为控制旋转角来实现。执行该旋转后，系统的状态演变为：
$$ \sum_j \beta_j |u_j\rangle |\lambda_j\rangle \left( \frac{C}{\lambda_j}|1\rangle + \sqrt{1 - \frac{C^2}{\lambda_j^2}}|0\rangle \right) $$
如果我们在最后测量这个辅助比特并测得结果为 $1$，系统的状态将坍缩并归一化为 $\sum_j \beta_j \frac{C}{\lambda_j} |u_j\rangle |\lambda_j\rangle$。随后通过逆相位估计解除寄存器 $|\lambda_j\rangle$ 的纠缠，即可得到 $\sum_j \beta_j \lambda_j^{-1} |u_j\rangle$，这正是解向量 $x = A^{-1}b$ 的量子态编码。

**时间复杂度与量子加速来源：**
受控旋转是通过量子算术线路来实现的。如果 $\lambda_j$ 以 $n$ 个比特进行精度为 $\epsilon$ 的编码，那么实现受控旋转的时间复杂度通常为 $O(\text{poly}(n))$ 或 $O(\text{poly}(\log(1/\epsilon)))$。相比于经典算法求解线性方程组所需的 $O(N)$ 甚至 $O(N^{\omega})$（$\omega$ 为矩阵乘法指数）的复杂度，这里的加速来源主要体现在两个方面：
1. **量子态叠加与非线性并行映射**：受控旋转操作通过控制酉算子，同时作用于所有基态 $|\lambda_j\rangle$。它相当于在一次酉演化操作中，对所有特征值并行完成了求倒数的非线性变换。这种指数级的并行处理是量子计算的核心优势。
2. **振幅编码与概率查询**：经典算法必须显式计算出 $O(N)$ 个解的分量。而量子算法巧妙地利用受控旋转，将 $1/\lambda_j$ 存储在单个辅助比特的概率振幅中。只要后续的应用（如计算内积或期望值）不需要完整读出所有态矢量信息，这种将宏观维度信息压缩至对数级 Hilbert 空间振幅的机制，就能保持 $O(\log N)$ 的位宽操作。

为了更直观地展示受控旋转的核心逻辑，以下提供使用isQ语言编写的概念模拟代码片段（为了演示清晰，采用单比特控制旋转示意）：

```isq
import std;

// 受控旋转核心逻辑示意
procedure main() {
    // 声明量子比特数组
    // 假设 q[0] 为用于受控旋转的辅助比特
    // q[1] 为存储特征值信息的特征比特（简化模型）
    qbit q[2]; 

    // 模拟相位估计后的状态：特征比特 q[1] 处于叠加态或特定态
    // 这里假设通过某种手段 q[1] 编码了特征值 lambda
    H(q[1]);

    // --- 受控旋转步骤 ---
    // 在真实 HHL 算法中，我们需要根据寄存器中的 lambda 计算出 theta = arcsin(C/lambda)
    // 并应用受控的 Ry(theta) 门。这里简化为使用固定角度的受控旋转。
    real theta = 1.23; // 假设计算出的 arcsin(C/lambda) 角度参数

    // 在 isQ 中，我们可以使用控制结构实现受控旋转
    // 当特征寄存器 q[1] 为 |1> 时，对辅助比特 q[0] 执行 Ry 旋转
    ctrl @[q[1]] Ry(theta, q[0]);
    
    // 如果是多比特寄存器表示特征值，真实实现需要用量子算术线路计算角度
    // 此处演示了最基本的将特征信息转化为振幅的受控酉操作思想
}
```

总结而言，HHL算法的指数级加速并不是凭空产生的，受控旋转步骤成功避免了显式遍历并求逆矩阵的庞大计算量，将 $O(N)$ 的矩阵求逆操作巧妙转化为量子态振幅的几何旋转。这种非线性映射的量子化实现，是算法实现 $O(\text{poly}(\log N, \kappa, 1/\epsilon))$ 复杂度并超越经典极限的关键。

## isqTrain/717

- task_id: `isqTrain/717`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2909`

### Prompt

Code this in isQ: implements the ripple_carry_adder pattern but with a different initial state preparation (flip q[[0, 2]] -> q[3]).

### Chain-of-thought reasoning

Step 1: Understand the Goal
The task is to implement a `ripple_carry_adder` pattern with a specific initial state preparation: `flip q[[0, 2]] -> q[3]`. Analyzing the circuit requirements, the "flip q[[0, 2]] -> q[3]" instruction translates to applying an X gate to `q[3]`.
The implementation performs an addition-like operation using qubits `q[0], q[1], q[2], q[3], q[4]`.
Wait, let's look at The implementation closely.
It starts with `X(q[3])`. This sets `a` and `b`... wait, the reference has:

The problem statement asks to "Write an isQ program that implements the ripple_carry_adder pattern but with a different initial state preparation (flip q[[0, 2]] -> q[3])."
Wait, what does "flip q[[0, 2]] -> q[3]" mean?
If I look at The implementation, it says "Encode a=1 (binary 01) and b=1 (binary 01)" but only applies `X(q[3])`.
Wait, The implementation only flips `q[3]`. the predicted output probabilities are `{|01>: 1.0}`.
Let's trace The implementation:
Initial state: |00000>
X(q[3]) -> |00010> (qubits are q[4]q[3]q[2]q[1]q[0] = 00010)
Toffoli(q[0], q[2], q[4]) -> Toffoli on |0>, |0>, target |0> -> remains |00010>
CNOT(q[0], q[2]) -> CNOT(0, 2) -> remains |00010>
CNOT(q[1], q[3]) -> CNOT(1, 3) -> control is |0>, target is |1> -> remains |00010>
CNOT(q[4], q[3]) -> CNOT(4, 3) -> control is |0>, target is |1> -> remains |00010>
Measure q[2], q[3].
q[2] is 0, q[3] is 1.
Output bitstring is measured in order q[2], q[3].
Bitstring = q[2] * 2^1 + q[3] * 2^0? No, usually earlier measured qubit = higher bit, so q[2] is higher bit.
q[2]=0, q[3]=1 -> '01' in binary -> integer 1. So |01> has probability 1.0.

Wait, the prompt says "Write an isQ program that implements the ripple_carry_adder pattern but with a different initial state preparation (flip q[[0, 2]] -> q[3])."
Does it mean I just need to output the exact circuit implementation but analyze its reasoning?
"Generate a reasoning section that explains:"
"Output ONLY the reasoning section, starting with "## Reasoning""
"Do NOT include the isQ code"

Ah! The task type is `code_generation` but the instruction specifically asks to "Generate a reasoning section that explains" and "Output ONLY the reasoning section, starting with "## Reasoning"".
So I don't output the code. I only output the reasoning for The implementation.

Let's write the reasoning for the provided circuit implementation.
1. The goal of the circuit: Perform a 2-bit ripple-carry addition (adding a and b) starting with a specific initial state prepared by flipping q[3].
2. Qubits needed: 5 qubits (`q[0]` to `q[4]`). Measured qubits are `q[2]` and `q[3]`.
3. Step-by-step evolution:
- Initial state: |00000>.
- `X(q[3])` sets q[3] to |1>, state becomes |00010> (in q[4..0]).
- `Toffoli(q[0], q[2], q[4])` computes carry0. Since q[0]=0, q[2]=0, carry is 0, state remains |00010>.
- `CNOT(q[0], q[2])` computes sum0 (a0 XOR b0). Since q[0]=0, q[2] remains 0.
- `CNOT(q[1], q[3])`

## isqTrain/2927

- task_id: `isqTrain/2927`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `measurement_order`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2471`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[2];
procedure main() {
    H(q[0]);
    X(q[1]);
    ctrl Rz(1.178097, q[0], q[1]);
    H(q[0]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

The user wants to analyze an isQ quantum program and predict its measurement probability distribution.
The circuit is:
q[0] and q[1] initially in |00>
1. H(q[0]) -> |+0>
2. X(q[1]) -> |+1>
3. ctrl Rz(1.178097, q[0], q[1])
   Wait, Rz in isQ: if Rz(theta, q), it applies phase e^{-i\theta/2} to |0> and e^{i\theta/2} to |1>?
   Let's check the standard Rz(theta, q) matrix. Usually Rz is [[1,0],[0,e^{i\theta}]]. Or [[e^{-i\theta/2}, 0], [0, e^{i\theta/2}]].
   Let's assume standard Rz matrix: [[e^{-i\theta/2}, 0], [0, e^{i\theta/2}]].
   Wait, the angle is 1.178097. Let's see what 1.178097 is.
   1.178097 / pi ≈ 0.375.
   0.375 * pi = 3/8 * pi.
   So the angle is 3pi/8.
   Wait, in isQ, `ctrl Rz(theta, q[0], q[1])` means if q[0] is |1>, apply Rz(theta) to q[1].
   State before this gate is |+1> = 1/sqrt(2) (|01> + |11>).
   Since Rz applies to q[1], and q[1] is in |1>, applying Rz(theta) to |1> multiplies it by e^{i\theta/2}.
   Wait, if it's [[1,0],[0,e^{i\theta}]], it multiplies by e^{i\theta}.
   Let's check standard Qiskit and isQ Rz definitions. isQ uses standard Rz definition [[1,0],[0,e^{i\theta}]] or [[e^{-i\theta/2}, 0], [0, e^{i\theta/2}]].
   Let's check expected probabilities: '01': 0.9157..., '11': 0.0842...
   This implies the state is not simply |+1> anymore, the phases of |01> and |11> are different!
   Let's re-evaluate:
   Initial: |00>
   H(q[0]): |+0> = 1/sqrt(2)(|00> + |10>)
   X(q[1]): 1/sqrt(2)(|01> + |11>)
   ctrl Rz(theta, q[0], q[1]) applies Rz(theta) to q[1] controlled by q[0].
   If q[0] is |1>, it applies Rz(theta) to q[1].
   Since q[1] is |1>, the |11> state picks up a phase.
   Wait, what is the phase?
   If Rz is [[1,0],[0,e^{i\theta}]], then |11> -> e^{i\theta} |11>.
   State becomes 1/sqrt(2) (|01> + e^{i\theta} |11>).
   Then H(q[0]) is applied.
   H on q[0]:
   1/sqrt(2) [ |01>(|0>+|1>)/sqrt(2) + e^{i\theta} |11>(|0>-|1>)/sqrt(2) ]
   = 1/2 [ |01> + |11> + e^{i\theta} |11> - e^{i\theta} |01> ]
   = 1/2 [ (1 - e^{i\theta}) |01> + (1 + e^{i\theta}) |11> ]
   Prob(01) = 1/4 |1 - e^{i\theta}|^2 = 1/4 ( (1-cos(theta))^2 + sin^2(theta) ) = 1/4 (2 - 2 cos(theta)) = (1 - cos(theta))/2
   Prob(11) = 1/4 |1 + e^{i\theta}|^2 = (1 + cos(theta))/2

   Given '01': 0.9157348401933039.
   So (1 - cos(theta))/2 = 0.9157348401933039
   1 - cos(theta) = 1.8314696803866078
   cos(theta

### Reference answer

{'predicted_probs': {'01': 0.9157348401933039, '11': 0.08426515980669609}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/4828

- task_id: `isqTrain/4828`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_import_qft`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `777`

### Prompt

Help me write isQ code that applies QFT twice to a 2-qubit register. Import std and qft. Declare 2 global qubits. Apply X(q[0]) to prepare |10>. Apply qft(q) twice. QFT applied twice equals a bit-reversal permutation (on 2 qubits, it swaps the qubits). Measure both qubits.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Goal: Write a reasoning section for an isQ program applying QFT twice to a 2-qubit register prepared in |10>.
    *   Input: Code prepares |10>, applies QFT twice, measures both qubits.
    *   predicted output: Expected probabilities are {|01>: 1.0} (Wait, the prompt says `{|11>: 1.0}`, let me double check. QFT(QFT(|10>)) = bit reversal. |10> bit reversed is |01>. Why does the prompt say `{|11>: 1.0}`? Let's trace it carefully.
    *   Initial state: |00>
    *   X(q[0]) -> |10>
    *   1st QFT on |10>: QFT_2 |10> = 1/2(|00> - |10> + |01> - |11>) = 1/sqrt(2) (|0> - |1>) \otimes 1/sqrt(2) (|0> - |1>) = |->
    *   Wait, standard QFT on |10> (which means j=1 in binary j=10, no, q[0] is |1>, so j = q[1]q[0] = 01? No, q[0] is least significant. If q[0]=1, state is |01>. But X(q[0]) makes the state |10> in binary (q[1]=0, q[0]=1). Wait, |q[1]q[0]>. So |01>.
    *   Let's check standard QFT: QFT|01> = 1/sqrt(2) (|0> + e^{i pi/2}|1>) \otimes 1/sqrt(2) (|0> + e^{i pi} |1>) = 1/sqrt(2)(|0> + i|1>) \otimes 1/sqrt(2)(|0> - |1>) = 1/2 (|00> - |01> + i|10> - i|11>).
    *   2nd QFT on this: QFT^2 |01>.
    *   In general, QFT^2 |j> = |reverse(j)>. For N=2, QFT^2 |01> = |10>.
    *   If measured, q[1] is 1, q[0] is 0. So measurement bitstring is 10? Wait.
    *   Let's re-read the prompt's "Expected measurement probabilities: {|11>: 1.0}".
    *   Wait, is QFT in isQ doing something different?
    *   Let's re-read the prompt reference code:
        `X(q[0])` -> |10> ? No, if X(q[0]) is applied to |00>, the state is |01> if we write it as |q[1]q[0]>.
        But if they mean "prepare |10>" literally, they might mean q[1]=1, q[0]=0? But `X(q[0])` sets q[0] to 1.
        Ah, prompt says: "Expected measurement probabilities: {|11>: 1.0}". Wait.
        Is `qft` in isQ standard QFT? Yes.
        Let's trace: q[0]=1 -> |01>.
        QFT(|01>) = 1/2 (|0> + |1>) \otimes (|0> - |1>) ? No.
        QFT|x> = 1/sqrt(N) \sum_k e^{2\pi i x k / N} |k>.
        For N=4, x=1 (which is |01>): QFT|1> = 1/2 \sum_{k=0}^3 e^{i \pi/2 k} |k> = 1/2 (|0> + i|1> - |2> - i|3>) = 1/2 (|00> + i|01> - |10> - i|11>).
        Apply QFT again: QFT(1/2(|0> + i|1> - |2> - i|3>)).
        Wait, QFT^2 |x> = |reverse(x)>. For N=4, reverse of |01> is |10>.
        So QFT^2(|01>) = |10>.
        If final state is |10>, measurement of q[0] is 0, q[1] is 1. Measurement bitstring is 10 (decimal 2).
        Why does the prompt say `{|11>: 1.0

## isqTrain/2875

- task_id: `isqTrain/2875`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `measurement_order`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1519`

### Prompt

Write an isQ program that demonstrating phase kickback with controlled-T. Set the target qubit to |1>, apply Hadamard to the control, apply controlled-T, then Hadamard again. Measure both qubits.

Requirements:
- Declare `qbit q[2];` at global scope.
- Use `procedure main()` as entry point.
- Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Demonstrate phase kickback where a controlled-T gate imparts a phase to the control qubit instead of the target.
2. **Qubits**: 2 qubits declared globally (`q[0]` = control, `q[1]` = target); both are measured.
3. **State evolution**:
   - `X(q[1])`: |00⟩ → |01⟩
   - `H(q[0])`: |01⟩ → (1/√2)(|01⟩ + |11⟩)
   - `ctrl T(q[0], q[1])`: Target |1⟩ acquires T-phase e^(iπ/4) when control is |1⟩ → (1/√2)(|01⟩ + e^(iπ/4)|11⟩). Phase kickback: the relative phase now resides on the control qubit's |1⟩ component.
   - `H(q[0])`: Interferes the control's superposition → (1/2)[(1+e^(iπ/4))|01⟩ + (1-e^(iπ/4))|11⟩]
4. **Probabilities**: P(|01⟩) = |1+e^(iπ/4)|²/4 = (2+√2)/4 ≈ 0.8536; P(|11⟩) = |1-e^(iπ/4)|²/4 = (2-√2)/4 ≈ 0.1464. The kickback phase e^(iπ/4) shifts measurement away from equal superposition.

## isqTrain/2658

- task_id: `isqTrain/2658`
- task_type: `code_equivalence`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `global_phase`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `239`

### Prompt

Are these two quantum circuits equivalent in terms of measurement output?

Circuit 1:
```isq
import std;
qbit q[3];

procedure main() {
    // Set inputs: a=1, b=0
    X(q[0]);
    // De Morgan: OR(a,b) = NOT(NOT(a) AND NOT(b))
    // Step 1: negate inputs
    X(q[0]); X(q[1]);
    // Step 2: Toffoli computes AND of negated inputs
    ctrl ctrl X(q[0], q[1], q[2]);
    // Step 3: restore original inputs
    X(q[0]); X(q[1]);
    // Step 4: negate the AND result to get OR
    X(q[2]);
    // Measure all qubits
    M(q[0]); M(q[1]); M(q[2]);
}

```

Circuit 2:
```isq
import std;
qbit q[3];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    // Set inputs: a=1, b=0
    X(q[0]);
    // De Morgan: OR(a,b) = NOT(NOT(a) AND NOT(b))
    // Step 1: negate inputs
    X(q[0]); X(q[1]);
    // Step 2: Toffoli computes AND of negated inputs
    ctrl ctrl X(q[0], q[1], q[2]);
    // Step 3: restore original inputs
    X(q[0]); X(q[1]);
    // Step 4: negate the AND result to get OR
    X(q[2]);
    // Measure all qubits
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A**: Sets q[0] to |1>. Negates q[0] and q[1] to |0> and |1>. Applies a Toffoli gate, which does nothing as both controls are not |1>. Restores q[0] and q[1] to |1> and |0>. Negates q[2] to |1>. Final state is |101>.
2. **Program B**: Performs the exact same sequence of operations as Program A, resulting in the same final quantum state |101>.
3. **Key difference**: Program B explicitly applies a `GPhase(0.0)` gate at the beginning, which introduces a global phase factor of $e^{i0} = 1$.
4. **Probability comparison**: A global phase of 1 has no effect on the quantum state vector or measurement probabilities. Both programs will measure the exact same bitstrings with identical probabilities (100% for |101>).
5. **Verdict: Yes**

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/728

- task_id: `isqTrain/728`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `972`

### Prompt

Write isQ code for the following quantum task: implements the ripple_carry_adder pattern but with a different initial state preparation (flip q[[0, 1, 2]] -> q[5]).

### Chain-of-thought reasoning

## Reasoning

**Goal**: Implement a ripple-carry adder where only q[5] is initialized to |1⟩, computing a=0 + b=0 with an extra bit set.

**Qubits**: 6 qubits (q[0..5]); q[2], q[3], q[5] are measured as sum0, sum1, and carry_out.

**State evolution**:
1. Initial: |000000⟩ → X(q[5]) → |000001⟩ (q[5]=1, all others 0)
2. Toffoli(q[0],q[2],q[4]): controls are |0⟩, q[4] stays 0 → |000001⟩
3. CNOT(q[0],q[2]): control is |0⟩, q[2] stays 0 → |000001⟩
4. Toffoli(q[1],q[3],q[5]): controls |0⟩, q[5] unchanged → |000001⟩
5. Toffoli(q[1],q[4],q[5]): controls |0⟩, q[5] unchanged → |000001⟩
6. Toffoli(q
