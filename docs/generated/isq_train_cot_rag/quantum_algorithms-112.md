# ISQ training COT RAG corpus: quantum_algorithms shard 112

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/algo/28

- task_id: `isqExpand/algo/28`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `qpe`, `hhl`, `phase_estimation`, `inverse_qft`
- source: `isq_expansion`
- dataset_index: `574`

### Prompt

Write isQ code for the following quantum task: implementing 2-qubit Quantum Phase Estimation (QPE) as used in HHL. The target unitary is the S gate (phase gate), with eigenvalue e^{i*pi/2} for eigenstate |1>. Prepare the input qubit in the |1> state, run QPE with 2 clock qubits, and measure the clock qubits. The phase is theta=1/4, so with 2 bits the measurement result should encode the value 1 (representing 1/4 = 0.01 in binary), giving probability 1.0 at index 1 of the output distribution.

### Chain-of-thought reasoning

## Reasoning
Goal: QPE on S gate with input |1>.

S|1> = i|1> = e^{i*pi/2}|1>. Phase: e^{2*pi*i*theta} = e^{i*pi/2}, so theta = 1/4.

With 2 clock qubits, theta = 0.01 in binary, so measurement should give decimal 1.

QPE steps:
1. X(input[0]): prepare |1> eigenstate
2. H on both clock qubits: create superposition
3. Controlled unitaries:
   - clock[0] controls S^(2^0) = S: adds phase e^{i*pi/2} on |1> component
     clock[0] becomes (|0> + i|1>)/sqrt(2)
   - clock[1] controls S^(2^1) = S^2 = Z: adds phase -1
     clock[1] becomes (|0> - |1>)/sqrt(2)
4. Inverse QFT:
   a. H(clock[1]): |-> -> |1>. State: |1>_c1 * (|0>+i|1>)/sqrt(2)_c0
   b. ctrl@[c0] S_dag(c1): when c0=1, S_dag on c1. S_dag|1>=-i|1>.
      State: |1>_c1 * (|0>+|1>)/sqrt(2)_c0
   c. H(c0): |+> -> |0>. Final: c0=0, c1=1

Measurement: clock[0]=0, clock[1]=1 -> index 01 = 1.
Probs: [0, 1.0, 0, 0]

## isqQA/quantum_algorithms/98_step_by_step

- task_id: `isqQA/quantum_algorithms/98_step_by_step`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `step_by_step`, `algorithm`, `Grover算法的几何解释`
- source: `qa_pipeline`
- dataset_index: `3288`

### Prompt

请问如何从几何角度一步步拆解并追踪Grover量子搜索算法的工作过程？能否以2量子比特系统寻找目标态|11⟩为例，给出详细的几何状态演化解析，并用isQ语言编写对应的完整代码来验证这一过程？

### Reference answer

<think>
解答此问题需从高维空间降维和几何操作等效替换两个核心逻辑出发：

首先，进行空间降维与基底构建。将4维的2量子比特系统投影到由目标态（|11⟩）和其正交补空间（非目标叠加态）构成的二维平面内。通过内积计算初始均匀叠加态与正交基的夹角（30度），从而明确演化起点在二维平面中的确切坐标。

其次，拆解Grover迭代的几何本质。将复杂的酉算子转化为直观的几何反射：Oracle操作等效于状态向量关于目标态轴的对称翻转；随后的扩散算子则等效于关于初始均匀叠加态轴的再次翻转。这两次反射叠加，在几何上等价于向目标态方向旋转了2倍于初始夹角的角度（60度）。

最后，将几何旋转映射回物理量子门。根据反射的数学定义，反推实现翻转所需的相位置反及Hadamard门组合，并利用isQ语言的语法将上述理论演化步骤转化为具体的量子线路代码，通过比对测量结果的概率分布来验证几何推导的正确性。
</think>

Grover算法的精髓在于它在由“目标态”和“非目标态叠加态”张成的二维平面内进行巧妙的旋转。为了让你彻底弄懂，我们将通过3个清晰的步骤，手动追踪2比特系统寻找|11⟩的几何演化过程。

```text
第一步：构建初始状态与几何基底
假设2比特的四个基态为|00⟩, |01⟩, |10⟩, |11⟩。目标态|w⟩ = |11⟩。
我们将所有非目标态归一化为一个等权重的叠加态：|s'⟩ = (|00⟩ + |01⟩ + |10⟩) / √3。
现在，|w⟩和|s'⟩构成了一个二维平面的两个正交基底。
算法的第一步是制备均匀叠加态|s⟩ = (|00⟩ + |01⟩ + |10⟩ + |11⟩) / 2。
在几何上，|s⟩正好处于|w⟩和|s'⟩之间，与|s'⟩的夹角设为θ/2。
由三角函数可知：sin(θ/2) = ⟨w|s⟩ = 1/2。因此 θ/2 = π/6（即30度）。
此时，状态向量与|s'⟩轴的夹角为30度。
```

```text
第二步：理解Oracle（预言机）的几何反射
Grover迭代的第一部分是应用Oracle算子：O = I - 2|w⟩⟨w|。
Oracle的作用在几何上等价于：将状态向量关于|s'⟩轴（即垂直于|w⟩的轴）进行对称反射。
初始态|s⟩与|s'⟩夹角为30度，经过反射后，新的状态向量到了|s'⟩轴的另一侧，此时它与|s'⟩的夹角变成了-30度。
```

```text
第三步：理解扩散算子的几何反射与旋转完成
Grover迭代的第二部分是应用扩散算子（均值翻转）：D = 2|s⟩⟨s| - I。
扩散算子的作用等价于：将状态向量关于初始态|s⟩的方向进行对称反射。
目前状态向量在距离|s⟩逆时针-30度的位置，我们将它关于|s⟩（即与|s'⟩夹角30度的位置）进行反射。
反射后，新的状态向量变为与|s'⟩夹角30 + 30 + 30 = 90度的位置！
因为90度恰好与|w⟩轴重合，这意味着只需1次迭代，状态向量就完全对准了目标态|w⟩，此时测量得到|11⟩的概率达到了100%。
这本质上是一个角度为2θ = 60度的旋转，经过1次旋转（30度->90度），算法完美收敛。
```

通过下面的isQ代码，你可以直接运行并观察到，仅需一次Grover迭代，测量结果将以100%的概率坍缩到目标态11。

```isQ
import std;

qbit q[2];

procedure main() {
    // 1. 制备均匀叠加态 |s>
    H(q[0]);
    H(q[1]);

    // 2. Oracle 作用：对目标态 |11> 的相位进行翻转
    // CZ门在计算基下相当于对 |11> 态乘以 -1，即实现了 I - 2|11><11|
    CZ(q[0], q[1]);

    // 3. 扩散算子 作用
    // 扩散算子结构为 H X (多控Z) X H
    // 对所有量子比特施加H门回到计算基的对称表示
    H(q[0]);
    H(q[1]);
    
    // 施加X门，将 |00> 变为 |11> 以便使用控制相位门
    X(q[0]);
    X(q[1]);
    
    // 对新的 |11> 施加相位翻转（由于此时只有两比特，直接使用CZ门即可实现多控Z的效果）
    CZ(q[0], q[1]);
    
    // 撤销X门
    X(q[0]);
    X(q[1]);
    
    // 再次施加H门完成扩散算子
    H(q[0]);
    H(q[1]);

    // 4. 测量：由于几何旋转角度为90度，此时必定测量到目标态
    M(q[0]);
    M(q[1]);
}
```

## isqExpand/algo/203

- task_id: `isqExpand/algo/203`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `superdense_coding`, `bell_pair`, `entanglement`, `quantum_communication`
- source: `isq_expansion`
- dataset_index: `4983`

### Prompt

Write isQ code for the following quantum task: an isQ superdense coding circuit that encodes the message '11' into one qubit of a Bell pair. Create the Bell pair from |00⟩, apply the encoding gates (X then Z) on Alice's qubit (q[0]), then perform Bob's decoding (CNOT then H). Use 2 qubits total.

### Chain-of-thought reasoning

Superdense coding allows sending 2 classical bits via 1 qubit using a shared Bell pair. Step 1: Create Bell pair |Phi+⟩ = (|00⟩+|11⟩)/√2 using H(q[0]) then CNOT(q[0],q[1]). Step 2: Encode '11' on Alice's qubit q[0]. The standard encoding is: '00'→nothing, '01'→X, '10'→Z, '11'→X then Z. Applying X to q[0] on |Phi+⟩ gives (|10⟩+|01⟩)/√2. Then Z on q[0] gives (-|10⟩+|01⟩)/√2. Step 3: Bob decodes with CNOT(q[0],q[1]) then H(q[0]). After CNOT: (-|11⟩+|01⟩)/√2. After H on q[0]: (1/2)(-(|0⟩-|1⟩)|1⟩ + (|0⟩+|1⟩)|1⟩) = (1/2)(2|1⟩|1⟩) = |11⟩. So the final state is |11⟩ with probability 1.0, giving expected_probs = [0.0, 0.0, 0.0, 1.0].

## isqTrain/706

- task_id: `isqTrain/706`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `boolean_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4487`

### Prompt

请用isQ语言编写一个量子电路：implements the integer_comparator pattern. Include explicit identity operations in the circuit (X-X pair before M(q[2])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a simple integer comparator that checks if a 2-bit integer a ≥ 2 by using the MSB (most significant bit) as a control, with explicit X-X identity pair to demonstrate gate cancellation.
2. **Qubits**: 3 qubits (q[0], q[1] for input a, q[2] for result flag); only q[2] is measured.
3. **State evolution**:
   - Start: |000⟩
   - X(q[0]): |100⟩ (sets LSB)
   - X(q[1]): |110⟩ (sets MSB, encoding a=3)
   - CNOT(q[1], q[2]): |111⟩ (MSB=1 flips ancilla, flagging a≥2)
   - X(q[2]): |110⟩
   - X(q[2]): |111⟩ (X-X pair cancels, net identity—demonstrates gate cancellation awareness)
4. **Result**: q[2] is in state |1⟩ with certainty, so measurement yields P(|1⟩) = 1.0.

## isqQA/quantum_algorithms/98_math_derivation

- task_id: `isqQA/quantum_algorithms/98_math_derivation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `math_derivation`, `algorithm`, `Grover算法的几何解释`
- source: `qa_pipeline`
- dataset_index: `1531`

### Prompt

请从数学推导的角度，严密阐述Grover算法中量子态的几何演化过程，详细论证为什么Grover迭代算子能够被视为在二维子空间中的旋转，并给出使用isQ语言实现的、能够清晰体现这一演化过程的Grover算法核心代码。

### Reference answer

<think>
第一步，构建二维子空间。将初始均匀叠加态向目标态及其正交补态投影，将N维希尔伯特空间的演化严格限制在这两个正交基张成的二维平面内。

第二步，拆解Grover迭代算子。数学分析表明，Oracle算子翻转目标态相位，几何上等效为关于正交补态的反射；而扩散算子 $2|s\rangle\langle s|-I$ 则等效为关于初始叠加态的反射。

第三步，论证旋转等效性。根据解析几何原理，同一平面内连续两次反射的复合等效于一次旋转。由于两反射轴夹角为 $\theta/2$（其中 $\sin(\theta/2)=1/\sqrt{N}$），故每次迭代必定使量子态向目标态精确旋转 $\theta$ 角度。

第四步，映射isQ代码实现。基于上述数学推导，代码结构需先定义Oracle门实现首次反射，再构建扩散算子实现二次反射，最后在主程序中通过循环精确控制旋转次数，从而复现状态向量逼近目标态的几何演化过程。
</think>

Grover算法的几何解释建立在一个极其优美的数学基础之上，其核心在于将高维希尔伯特空间中的复杂量子态演化，降维到一个由目标态和初始叠加态张成的二维子空间中进行严密分析。

首先，我们定义两个至关重要的正交基向量。假设算法的目标是搜索被标记的态 $|\omega\rangle$。我们构造另一个均匀叠加态 $|s'\rangle$，它包含了除 $|\omega\rangle$ 之外的所有其他计算基态，且满足归一化条件：
$|s'\rangle = \frac{1}{\sqrt{N-1}} \sum_{x \neq \omega} |x\rangle$

算法的初始态是包含所有计算基态的均匀叠加态 $|s\rangle = \frac{1}{\sqrt{N}} \sum_{x=0}^{N-1} |x\rangle$。我们可以将 $|s\rangle$ 分解到 $|\omega\rangle$ 和 $|s'\rangle$ 这两个正交基上：
$|s\rangle = \sqrt{\frac{N-1}{N}} |s'\rangle + \sqrt{\frac{1}{N}} |\omega\rangle$

为了在几何上直观表达，我们定义角度 $\theta/2$，使得 $\sin(\theta/2) = \frac{1}{\sqrt{N}}$，因此 $\cos(\theta/2) = \sqrt{\frac{N-1}{N}}$。此时，初始态可以重写为：
$|s\rangle = \cos(\frac{\theta}{2}) |s'\rangle + \sin(\frac{\theta}{2}) |\omega\rangle$

这意味着初始态 $|s\rangle$ 位于由 $|s'\rangle$ 和 $|\omega\rangle$ 张成的二维平面内，且与 $|s'\rangle$ 轴的夹角为 $\theta/2$。

Grover迭代算子由两部分组成：$G = (2|s\rangle\langle s| - I) O$。

1. **Oracle算子 $O$ 的作用**：其数学定义为 $O = I - 2|\omega\rangle\langle\omega|$。当它作用于该二维子空间内的任意态 $|\psi\rangle = a|s'\rangle + b|\omega\rangle$ 时，有 $O|\psi\rangle = a|s'\rangle - b|\omega\rangle$。在几何上，这等价于将量子态矢量关于 $|s'\rangle$ 轴进行反射。

2. **扩散算子 $D = 2|s\rangle\langle s| - I$ 的作用**：该算子将任意态关于 $|s\rangle$ 轴进行反射。

连续应用这两个反射操作构成了Grover迭代 $G$。根据线性代数和几何学的基本定理，在同一平面内连续执行两次反射，等价于在该平面内做了一次角度为两倍反射夹角的旋转。因为 $|s\rangle$ 与 $|s'\rangle$ 的夹角为 $\theta/2$，所以第一次关于 $|s'\rangle$ 反射，再关于 $|s\rangle$ 反射，总的效果就是将量子态向 $|\omega\rangle$ 轴旋转了 $\theta$ 角度。

因此，经过 $k$ 次Grover迭代后，量子态演化为：
$|\psi_k\rangle = \cos((2k+1)\frac{\theta}{2}) |s'\rangle + \sin((2k+1)\frac{\theta}{2}) |\omega\rangle$

经过大约 $\frac{\pi}{4}\sqrt{N}$ 次迭代后，系数接近 $\sin(\pi/2) = 1$，此时测量将以极高的概率坍缩到目标态 $|\omega\rangle$。

以下是使用isQ语言实现的Grover算法代码，以2量子比特（搜索空间 $N=4$，寻找目标态 $|11\rangle$）为例，体现上述演化：

import std;
qbit q[2];

procedure main() {
    // 制备初始态 |s>
    for i in 0:2 {
        H(q[i]);
    }
    
    // N=4时仅需1次迭代即可达到最优
    // 1. Oracle算子 O：对目标态 |11> 的相位进行翻转
    CZ(q[0], q[1]);
    
    // 2. 扩散算子 D：关于 |s> 的反射
    for i in 0:2 {
        H(q[i]);
        X(q[i]);
    }
    CZ(q[0], q[1]);
    for i in 0:2 {
        X(q[i]);
        H(q[i]);
    }
    
    // 测量观察演化结果
    for i in 0:2 {
        M(q[i]);
    }
}

## isqTrain/4069

- task_id: `isqTrain/4069`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `3027`

### Prompt

This isQ program doesn't produce the correct output. Can you debug it?

Code:
```
import std;
// 4-qubit Grover search targeting |0011>
qbit q[4];

// Oracle: mark target state |0011>
unit grover_oracle(qbit q[4]) {
    X(q[0]);
    X(q[1]);
    ctrl<2> CZ(q[0], q[1], q[2], q[3]);
    // BUG: missing gate here
    X(q[0]);
} deriving gate

// Diffusion operator for 4 qubits
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

// Main: apply Grover iteration and measure
procedure main() {
    // Superposition on all 4 qubits
    H(q[0]); H(q[1]); H(q[2]); H(q[3]);
    // Grover iterations (3 iterations optimal for N=4)
    for i in 0:3 {
        grover_oracle(q);
        grover_diffusion(q);
    }
    // Measure all qubits
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug location**: In `grover_oracle`, the uncomputation step after the multi-controlled CZ gate is incomplete. The oracle applies `X(q[0])` and `X(q[1])` before the CZ to convert the target state |0011⟩ → |1111⟩, but only undoes `X(q[0])` afterward. The `X(q[1])` gate is missing.

2. **Fix**: Add `X(q[1])` between the CZ gate and the final `X(q[0])` in the oracle, so both X gates are properly uncomputed:
   - Before: `... ctrl<2> CZ(...); // BUG; X(q[0]);`
   - After: `... ctrl<2> CZ(...); X(q[1]); X(q[0]);`

3. **State evolution (corrected)**:
   - **Superposition**: H on all 4 qubits creates uniform superposition Σ|x⟩/4
   - **Oracle**: X(q[0]),X(q[1]) map |0011⟩→|1111⟩; `ctrl<2> CZ` flips phase of |1111⟩; X(q[1]),X(q[0]) restore, yielding -|0011⟩ phase marking
   - **Diffusion**: H→X→`ctrl<2> CZ`→X→H amplifies the marked state's amplitude
   - **3 iterations**: Each iteration rotates state toward |0011⟩; after 3 (optimal for N=16), |0011⟩ reaches ~96.3% probability, matching predicted output

## isqQA/quantum_algorithms/128_comparison

- task_id: `isqQA/quantum_algorithms/128_comparison`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `comparison`, `algorithm`, `超密编码`
- source: `qa_pipeline`
- dataset_index: `4473`

### Prompt

请对比分析超密编码与经典通信以及量子隐形传态在资源消耗、通信目的和适用场景上的异同。并请提供一段使用isQ语言实现超密编码的示例代码，说明Alice如何通过一个量子比特向Bob传递两个经典比特的信息。

### Reference answer

超密编码、经典通信以及量子隐形传态是量子信息领域三个经常被放在一起比较的通信协议。它们在通信目的、信道需求和物理资源消耗上有着本质的区别与深刻的内在联系。

首先，**与经典通信的对比**：
在经典通信中，若要传输$n$个比特的信息，发送方必须通过经典信道物理性地传输$n$个经典比特。超密编码的突出优点在于它突破了经典信道容量的极限——发送方仅需通过量子信道传输**1个量子比特**，即可成功向接收方传递**2个经典比特**的信息。这使得通信的信道容量密度翻倍。然而，超密编码的缺点和局限性在于其严苛的前提条件：通信双方必须预先共享一对最大纠缠态（如贝尔态），并且收发双方之间必须存在能够传输该量子比特的完整量子信道。在当前物理系统中，维持长距离的量子纠缠和建立无噪声量子信道的成本极高。因此，经典通信适用于日常宏观的高速数据传输，而超密编码目前主要适用于未来量子网络节点间的高效数据包传输、量子密钥分发加速等特定场景。

其次，**与量子隐形传态的对比**：
超密编码和量子隐形传态在数学机制和量子线路上具有高度的对称性和互逆性。
1. **通信目的**：超密编码是利用量子信道来传输**经典信息**（将经典比特编码进纠缠态中）；而隐形传态是利用经典信道来传输**量子信息**（将未知的量子态转移至远方）。
2. **资源消耗**：超密编码需要预先共享1对纠缠态（消耗2个量子比特的纠缠资源），并在正向传输中发送1个量子比特；隐形传态同样需要预先共享1对纠缠态，但在正向传输中需要发送2个经典比特。
3. **适用场景**：超密编码适用于量子计算节点间需要压缩经典数据传输量的场景（如分布式量子数据库查询）；隐形传态则是构建大规模量子计算集群和量子中继通信网的核心基石。

<thinking>
超密编码的物理与数学推导基于贝尔态基矢的正交完备性。
假设Alice和Bob预先共享的纠缠态为：
|Φ⁺⟩ = (1/√2)(|00⟩ + |11⟩)
在这个态中，左侧比特属于Alice，右侧比特属于Bob。
Alice根据想要发送的2比特经典信息（00, 01, 10, 11），对自己手中的量子比特施加相应的泡利门操作：
- 若发送 00：施加 I 门，全局态保持 |Φ⁺⟩
- 若发送 01：施加 X 门，全局态塌缩为 |Ψ⁺⟩ = (1/√2)(|10⟩ + |01⟩)
- 若发送 10：施加 Z 门，全局态塌缩为 |Φ⁻⟩ = (1/√2)(|00⟩ - |11⟩)
- 若发送 11：施加 iY 门（即先施加X门再施加Z门），全局态塌缩为 |Ψ⁻⟩ = (1/√2)(|10⟩ - |01⟩)
因为上述四个贝尔态彼此完全正交，Alice将操作后的量子比特通过量子信道发送给Bob。Bob此时拥有完整的两个量子比特，他只需对这两个比特执行逆贝尔基变换（先执行CNOT门，再对控制比特执行Hadamard门），就可以在计算基下确定性地测量出Alice到底施加了哪个门，从而解读出原来的2位经典比特。

以下是基于isQ语言实现的超密编码完整示例代码。为了演示，代码中假设Alice固定发送经典比特串 "11"：

import std;

qbit q[2];

procedure main() {
    // 1. 准备阶段：分发纠缠对
    // 在此处我们通过H门和CNOT门生成贝尔态 |Φ⁺⟩
    // 此时默认 q[0] 分配给 Alice，q[1] 分配给 Bob
    H(q[0]);
    CNOT(q[0], q[1]);

    // 2. 编码阶段：Alice根据经典比特进行操作
    // 假设 Alice 要发送的经典比特是 c1=1, c0=1 (即二进制的 11)
    // c0 = 1，施加 X 门
    X(q[0]);
    // c1 = 1，施加 Z 门
    Z(q[0]);

    // 3. 传输与解码阶段：Alice将 q[0] 发送给 Bob
    // Bob 现在拥有完整的 (q[0], q[1])，执行贝尔基的逆变换进行解码
    CNOT(q[0], q[1]);
    H(q[0]);

    // 4. 测量阶段：Bob测量两个量子比特以读取经典信息
    // 此时测量结果 r0, r1 将会是 1, 1
    M(q[0]);
    M(q[1]);
}
</thinking>

通过上述isQ代码的执行，量子系统将自动完成从经典信息的编码到量子解码的全过程。在理想的量子硬件上，程序结束时测量得到的概率分布将100%集中在状态 |11⟩ 上。超密编码极为巧妙地利用了量子纠缠的非局域关联特性，是展现量子力学在信息论中强大应用潜力的标志性算法。

## isqTrain/3053

- task_id: `isqTrain/3053`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `measurement_order`
- source: `isq_train_cot`
- dataset_index: `4359`

### Prompt

Write isQ code for the following quantum task: initializes 3 qubits to the state |010> using X gates and measures all.

Requirements:
- Declare `qbit q[3];` at global scope.
- Apply X to qubits that should be |1>.
- Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Initialize a 3-qubit register to the specific basis state |010> and measure it.
2. **Qubits**: 3 qubits (`q[0]`, `q[1]`, `q[2]`) are used, and all 3 are measured.
3. **State Evolution**:
   - Start in the initial state: |000>.
   - Apply `X(q[1])`: The X gate flips the second qubit, changing the state to |010>.
4. **Probabilities**: Measuring the final state |010> deterministically yields the bitstring '010' (decimal 2), resulting in the probability distribution {|010>: 1.0}.

## isqTrain/3998

- task_id: `isqTrain/3998`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `4543`

### Prompt

Fix the bug in this quantum program:

```
import std;
// QFT on 4 qubits with input state |1111>
qbit q[4];

procedure main() {
    // Prepare input state |1111>
    X(q[0]);
    X(q[1]);
    // BUG: missing gate here
    X(q[3]);

    // QFT stage for qubit 0
    H(q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 16.0, q[3], q[0]);
    // QFT stage for qubit 1
    H(q[1]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[3], q[1]);
    // QFT stage for qubit 2
    H(q[2]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[3], q[2]);
    // QFT stage for qubit 3
    H(q[3]);
    // Swap q[0] and q[3]
    CNOT(q[0], q[3]);
    CNOT(q[3], q[0]);
    CNOT(q[0], q[3]);
    // Swap q[1] and q[2]
    CNOT(q[1], q[2]);
    CNOT(q[2], q[1]);
    CNOT(q[1], q[2]);
    // Measure after QFT
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **What the bug is**: The state preparation section is missing `X(q[2])` to flip qubit 2. The code only applies X to q[0], q[1], and q[3], preparing |1101> instead of the intended |1111>.

2. **What the fix is**: Add `X(q[2])` between the X(q[1]) and X(q[3]) lines to complete the preparation of |1111>.

3. **Brief state evolution of corrected circuit**:
   - Initialize |0000>
   - Apply X to all 4 qubits → |1111>
   - QFT transforms |1111> (computational basis state |15>) into an equal superposition: 1/4 Σ|k⟩ for k=0..15 with appropriate phases
   - Final swaps reorder qubits
   - Measurement yields uniform distribution: each of the 16 basis states has probability 1/16 = 0.0625

## isqTrain/73

- task_id: `isqTrain/73`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `3028`

### Prompt

实现以下量子计算任务（使用isQ）：implements the bell_state_preparation pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

Starting state: |00>

1. H(q[0]): Creates superposition on qubit 0
   → (|0⟩ + |1⟩)/√2 ⊗ |0⟩ = (|00⟩ + |10⟩)/√2

2. CNOT(q[0], q[1]): Bell state (EPR pair)
   → (|00⟩ + |11⟩)/√2

3. Z(q[0]): Apply Z to Alice's qubit
   → (|00⟩ - |11⟩)/√2

4. X(q[0]): Apply X to Alice's qubit
   → (|10⟩ - |01⟩)/√2

5. CNOT(q[0], q[1]): 
   → |11⟩ - |01⟩)/√2 = (|11⟩ - |01⟩)/√2
   
   Wait, let me redo this. CNOT flips target when control is |1⟩.
   
   |10⟩ → |11⟩ (control is |1⟩, flip target)
   |01⟩ → |01⟩ (control is |0⟩, no flip)
   
   So: (|11⟩ - |01⟩)/√2

6. H(q[0]):
   Apply H to qubit 0:
   |11⟩ → H on first qubit: (|01⟩ - |11⟩)/√2
   |01⟩ → H on first qubit: (|01⟩ + |11⟩)/√2
   
   So: ((|01⟩ - |11⟩) - (|01⟩ + |11⟩))/2 = -2|11⟩/2 = -|11⟩
   
   So after first H: -|11⟩

7. H(q[0]): Apply H again
   |11⟩ → (|01⟩ - |11⟩)/√2
   
   Wait, H|0⟩ = (|0⟩ + |1⟩)/√2, H|1⟩ = (|0⟩ - |1⟩)/√2
   
   So H on qubit 0 of |11⟩:
   |1⟩₁ → (|0⟩ - |1⟩)/√2
   Result: (|01⟩ - |11⟩)/√2

8. H(q[0]): Apply H again (the third one, which cancels the second)
   This H-H pair should cancel:
   
   H(q[0]) then H(q[0]) is identity on qubit 0.
   
   So after the H-H pair, we're back to -|11⟩

9. M(q[0]) and M(q[1]):
   Measure both qubits. State is -|11⟩
   
   Probability of |11⟩ = |⟨11|(-|11⟩)|² = 1.0

Wait, let me recount the H gates:

Looking at the code:

So after CNOT decode (step 5), we have: -|11⟩

Then:
- First H(q[0]): H on qubit 0 of -|11⟩
  |1⟩ → (|0⟩ - |1⟩)/√2
  Result: -( |01⟩ - |11⟩)/√2 = (-|01⟩ + |11⟩)/√2

Hmm, let me be more careful.

After step 5 (CNOT):
State = (|11⟩ - |01⟩)/√2

Wait, I need to be careful about qubit ordering. Let me use |q[0]q[1]⟩ notation.

After H(q[0]): (|00⟩ + |10⟩)/√2

After CNOT(q[0], q[1]): 
When q[0]=|1⟩, flip q[1]
|00⟩ → |00⟩
|10⟩ → |11⟩
Result: (|00⟩ + |11⟩)/√2

After Z(q[0]):
Z|0⟩ = |0⟩, Z|1⟩ = -|1⟩
|00⟩ → |00⟩
|11⟩ → -|11⟩
Result: (|00⟩ - |11⟩)/√2

After X(q[0]):
X|0⟩ = |1⟩, X|1⟩ = |0⟩
|00⟩ → |10⟩
|11⟩ → |01⟩
Result: (|10⟩ - |01⟩)/√2

After CNOT(q[0], q[1]):
|10⟩ → |11⟩ (q[0]=1, flip q[
