# ISQ training COT RAG corpus: quantum_algorithms shard 76

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/952

- task_id: `isqTrain/952`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `hamiltonian_simulation`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5235`

### Prompt

帮我写一个isQ程序：implements the pauli_evolution pattern with modified rotation parameters (num_pi2_to_pi4). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

We need to generate a reasoning section for the given isQ code. The code implements a simple circuit: H, Rz(theta), H, M. The theta is given as 0.78539816339745 which is pi/4 (approximately 0.785398). Actually pi/4 = 0.7853981633974483. So it's Rz(pi/4). But the comment says "Rz(pi/2)"? Wait: "Rz(0.78539816339745, q[0]); // Pauli-Z evolution: e^(-i*pi/4*Z) = Rz(pi/2)". That comment is contradictory: e^(-i*pi/4*Z) = Rz(pi/4)? Actually Rz(theta) = e^{-i theta/2 Z} up to global phase? Standard definition: Rz(θ) = exp(-iθ/2 Z) = diag(e^{-iθ/2}, e^{iθ/2}). So if we want e^{-i*pi/4*Z} = diag(e^{-i*pi/4}, e^{i*pi/4}), then we need Rz(pi/2) because Rz(pi/2) = diag(e^{-i*pi/4}, e^{i*pi/4}). Indeed, Rz(pi/2) gives e^{-i pi/4} on |0> and e^{i pi/4} on |1>. So the comment says Rz(pi/2) but the value is 0.785398... which is pi/4, not pi/2. Something off: pi/2 ≈ 1.5708, pi/4 ≈ 0.7854. So the provided angle is pi/4, which would correspond to Rz(pi/4) = diag(e^{-i pi/8}, e^{i pi/8}). That would not produce the given expected probabilities? Let's compute the predicted output: P(|0>) = 0.853553, P(|1>) = 0.146447. This is cos^2(pi/8) ≈ 0.853553, sin^2(pi/8) ≈ 0.146447. Indeed, cos^2(pi/8) = (1+cos(pi/4))/2 = (1+√2/2)/2 ≈ (1+0.7071)/2 = 0.85355. So the circuit: start |0>, H -> |+>, then Rz(θ), then H -> measurement probabilities? Let's compute: |+> = (|0>+|1>)/√2. Apply Rz(θ) (with the standard definition Rz(θ) = e^{-iθ/2 Z}? We need to be careful about the definition in isQ. According to the syntax reference: "Rz(theta, q)" is listed as a basic gate. Typically, Rz(θ) = diag(1, e^{iθ})? Actually in many quantum computing frameworks, Rz(θ) = exp(-iθ/2 Z) up to global phase? But sometimes it's defined as Rz(θ) = diag(1, e^{iθ}). The isQ documentation is not given, but we can infer from expected outcomes. Let's compute both possibilities.

We have circuit: H, Rz(θ), H. Starting from |0>, apply H => (|0>+|1>)/√2. Then apply Rz(θ) with some definition. Then apply H => measure.

If Rz(θ) = diag(1, e^{iθ}) (i.e., phase shift on |1> only, no factor on |0>), then state after Rz: (|0> + e^{iθ}|1>)/√2. Then apply H: H|0> = (|0>+|1>)/√2, H|1> = (|0>-|1>)/√2. So final state = 1/√2 [ (|0>+|1>)/√2 + e^{iθ} (|0>-|1>)/√2 ] = 1/2 [ (1+e^{iθ})|0> + (1 - e^{iθ})|1> ]. Probability of |0> = |(1+e^{iθ})/2|^2 = (1/4)(1+e^{iθ})(1+e^{-iθ}) = (1/4)(2+2cosθ) = (1+cosθ)/2. Probability of |1> = (1-cosθ)/2. So if we want P(|0>) = cos^2(pi/8) = (1+

## isqQA/quantum_algorithms/125_math_derivation

- task_id: `isqQA/quantum_algorithms/125_math_derivation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `math_derivation`, `algorithm`, `相位回踢机制`
- source: `qa_pipeline`
- dataset_index: `3748`

### Prompt

在量子算法中，相位回踢是一个核心机制。请以受控-Z门和目标量子比特的特征态为例，严密推导并解释量子态的演化过程，说明特征态的相位是如何被“踢回”并转移到控制比特上的，并提供相应的isQ代码演示该过程。

### Reference answer

<think>
首先，明确相位回踢发生的前提：目标比特必须处于控制门（此处为受控-Z门）对应算符（Z算符）的特征态。我们选择目标比特处于特征态 $|-\rangle$（对应特征值为-1），控制比特初态设为 $|0\rangle$。

其次，推导量子态的演化过程：
1. 对控制比特施加H门，使其从 $|0\rangle$ 变为叠加态 $|+\rangle$。
2. 施加CZ门，这是推导的核心。由于目标比特处于Z的特征态，CZ门作用时目标比特状态不变，但其特征值（-1）作为全局相位因子，被“踢回”并附加到了控制比特对应的状态分量上。
3. 这导致控制比特的相对相位发生变化，状态从 $|+\rangle$ 翻转为 $|-\rangle$，从而将目标比特的相位信息成功转移到了控制比特上。

最后，根据上述物理过程设计isQ代码逻辑：声明量子比特数组，利用X和H门初始化目标比特为 $|-\rangle$，按序对控制比特施加H、CZ、H门，并通过测量验证控制比特状态的改变。
</think>

<think
> 1. 明确问题核心：解释量子算法中的相位回踢机制，要求包含严密的数学推导、量子态演化分析以及isQ代码。
> 2. 数学推导步骤设定：
>    - 选择特征态：Z门的特征态为 |+⟩ 和 |-⟩，对应的特征值分别为 +1 和 -1。
>    - 初始态设定：控制比特为 |0⟩，目标比特为 |-⟩。
>    - 施加Hadamard门：控制比特变为 |+⟩。
>    - 施加受控Z门（CZ）：利用特征态性质展开推导，观察相位转移。
>    - 再次施加Hadamard门：验证控制比特测量结果的翻转。
> 3. 代码编写：
>    - 声明包含2个量子比特的数组。
>    - 初始化目标比特为 |-⟩ 态（先X后H）。
>    - 控制比特执行H门、CZ门、H门操作。
>    - 观察最终状态。
> 4. 审查约束：数学推导严密，代码使用isQ语法且禁止使用SWAP和CCX。</think
> 
相位回踢机制是量子计算中极为重要的一种物理现象，它允许我们将目标量子比特所携带的相位信息转移到控制量子比特的概率幅上，这是Shor算法、Grover算法以及量子相位估计等高级算法的基石。

下面我们以受控-Z（CZ）门和目标量子比特处于Z门特征态的情况为例，进行严密的数学推导。

假设我们有一个两比特系统，高位为控制比特，低位为目标比特。Z门的特征向量满足 $Z|u\rangle = \lambda|u\rangle$。已知Z门的两个正交特征态分别是 $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$ 和 $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$，对应的特征值分别为 $+1$ 和 $-1$。

我们选择目标比特处于 $|-\rangle$ 态（特征值 $\lambda = -1$），初始态控制比特处于 $|0\rangle$，因此系统整体的初始量子态为：
$$|\psi_0\rangle = |0\rangle \otimes |-\rangle$$

**步骤 1：对控制比特施加Hadamard门**
控制比特进入叠加态，系统状态演化为：
$$|\psi_1\rangle = (H \otimes I)|\psi_0\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes |-\rangle = \frac{1}{\sqrt{2}}(|0\rangle|-\rangle + |1\rangle|-\rangle)$$

**步骤 2：施加受控-Z门（CZ）**
根据量子力学原理，如果控制比特处于 $|1\rangle$ 态，则对目标比特施加Z门。利用目标比特是Z门特征态的性质 $Z|-\rangle = -|-\rangle$，我们有：
$$|\psi_2\rangle = CZ|\psi_1\rangle = \frac{1}{\sqrt{2}}(|0\rangle|-\rangle + |1\rangle(Z|-\rangle))$$
$$|\psi_2\rangle = \frac{1}{\sqrt{2}}(|0\rangle|-\rangle - |1\rangle|-\rangle) = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) \otimes |-\rangle$$

**核心分析：相位回踢**
在步骤2中，我们可以清晰地观察到：目标比特 $|-\rangle$ 作为Z门的特征态，本身并没有发生任何改变。然而，其对应的特征值 $-1$ 却作为全局相对相位，被“踢回”并附加到了控制比特上，使得控制比特的量子态从 $|+\rangle$ 翻转成了 $|-\rangle$。

**步骤 3：对控制比特再次施加Hadamard门**
为了在计算基下观测到这个相位回踢的结果，我们对控制比特再次应用H门：
$$|\psi_3\rangle = (H \otimes I)|\psi_2\rangle = (H\frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)) \otimes |-\rangle = |1\rangle \otimes |-\rangle$$

经过上述演化，目标态 $|-\rangle$ 的相位信息完全转移到了控制比特上，使其确定性地坍缩到 $|1\rangle$ 态。

以下是使用isQ语言模拟上述相位回踢过程的代码实现：

```isq
import std;

qbit q[2];

procedure main() {
    // 准备目标比特 (q[1]) 为 |-\rangle 态
    // |-\rangle = X|1\rangle 或者是 H|1\rangle
    X(q[1]);
    H(q[1]);

    // 准备控制比特 (q[0]) 为 |+\rangle 态
    H(q[0]);

    // 执行受控-Z门，发生相位回踢
    CZ(q[0], q[1]);

    // 再次对控制比特施加Hadamard门
    H(q[0]);

    // 此时测量控制比特 q[0]，由于相位回踢机制，
    // 理论上将以 100% 的概率得到结果 1。
    // (如果目标比特初始处于 |+\rangle 态，则测量结果将为 0)
    int r = M(q[0]);
    
    // 如果需要还原初始基态以备后续计算，可以加入经典控制
    if (r == 1) {
        X(q[0]);
    }
}
```

## isqTrain/21

- task_id: `isqTrain/21`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1201`

### Prompt

请用isQ语言编写一个量子电路：implements the qft_subcircuit pattern but with a different initial state preparation (flip q[[2]] -> q[0]).

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

The circuit has 3 qubits, initialized with X(q[0]) to prepare |100>, then applies QFT to q[0], q[1], q[2].

Wait, let me re-read the prompt. The task says "with a different initial state preparation (flip q[[2]] -> q[0])". This seems to mean that In the implementation, q[2] is flipped (X(q[2])), but we need to change it to q[0] being flipped instead (X(q[0])).

Analyzing the circuit requirements, it already has X(q[0]). So the task is asking me to generate reasoning for the given circuit implementation.

Let me trace through the circuit:

1. Initial state: |000>
2. After X(q[0]): |100>

Now apply QFT3(q[0], q[1], q[2]):

The QFT on 3 qubits transforms |100> (which is the computational basis state representing integer 4 in binary... wait, no. Let me think about the bit ordering.

Actually, let me think about this more carefully. In QFT, typically q[0] is the least significant bit. But let me trace through the gates directly.

State: |100>

H(a) where a = q[0]:
|100> → (1/√2)(|000> + |100>)

Wait, H on qubit 0 (the first qubit in |q[0]q[1]q[2]>):
|100> = |1>|0>|0>
H on first qubit: (1/√2)(|0> + |1>)|0>|0> = (1/√2)(|000> + |100>)

ctrl Rz(π/2, b, a) where b = q[1], a = q[0]:
This applies Rz(π/2) to q[0] controlled by q[1].
Since q[1] is |0>, this does nothing.
State remains: (1/√2)(|000> + |100>)

ctrl Rz(π/4, c, a) where c = q[2], a = q[0]:
This applies Rz(π/4) to q[0] controlled by q[2].
Since q[2] is |0>, this does nothing.
State remains: (1/√2)(|000> + |100>)

H(b) where b = q[1]:
State: (1/√2)(|000> + |100>) → (1/√2)(|0>(1/√2)(|0>+|1>)|0> + |1>(1/√2)(|0>+|1>)|0>)
= (1/2)(|000> + |010> + |100> + |110>)

ctrl Rz(π/2, c, b) where c = q[2], b = q[1]:
This applies Rz(π/2) to q[1] controlled by q[2].
Since q[2] is |0> in all terms, this does nothing.
State remains: (1/2)(|000> + |010> + |100> + |110>)

H(c) where c = q[2]:
State: (1/2)(|000> + |010> + |100> + |110>) where each |q0q1q2> has q2=0
After H on q2: each |q0q1>|0> → |q0q1>(1/√2)(|0>+|1>)
= (1/(2√2))(|000> + |001> + |010> + |011> + |100> + |101> + |110> + |111>)

swap (three-CNOT decomposition) a and c (q[0] and q[2]):
CNOT(q[0], q[2]), CNOT(q[2], q[0]), CNOT(q[0], q[2])

Starting state: (1/(2√2))(|000> + |001> + |010> + |011> + |100> + |101> + |110> + |111>)

Let me apply the swap operation (three-CNOT decomposition) by gate:

First CNOT(q[0], q[2]):
|000> → |000>
|001> → |001>
|010> → |010>
|011> → |011>
|100> → |101>
|101> → |100>
|110> → |111>
|111> → |110>

State: (1/(2√2))(|000> + |001> + |010> + |011> + |101> + |100> +

## isqQA/quantum_algorithms/38_math_derivation

- task_id: `isqQA/quantum_algorithms/38_math_derivation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `math_derivation`, `algorithm`, `Deutsch-Jozsa算法`
- source: `qa_pipeline`
- dataset_index: `5533`

### Prompt

请详细推导Deutsch-Jozsa算法的核心数学过程。假设黑盒函数的输入规模为$n$个比特，给定量子预言机$U_f$，请严密写出从初始量子态到最终测量前的量子态演化公式，并通过概率计算证明为何该算法能够以100%的概率区分常数函数和平衡函数。

### Reference answer

<think>
推导Deutsch-Jozsa算法的逻辑链路可严密分解为四个核心阶段：
1. **初态与叠加**：设定系统初态为$n$个工作位全$|0\rangle$和1个辅助位$|1\rangle$。通过全局Hadamard变换，将工作位转为均匀叠加态，辅助位转为$|-\rangle$态，为后续相位提取奠定基础。
2. **Oracle相位 kickback**：分析预言机作用。由于辅助比特处于特殊的叠加态，$U_f$的作用等效于将函数值$f(x)$转化为工作位叠加态的相对相位因子$(-1)^{f(x)}$，同时辅助位状态解耦保持不变。
3. **二次Hadamard干涉**：对$n$个工作位再次施加Hadamard变换。利用Hadamard矩阵的性质与二进制内积展开公式，将前一步隐藏的相位信息重新分配并转化为各个计算基态的振幅。
4. **概率计算与分类**：提取最终量子态中$|0\rangle^{\otimes n}$分量的振幅，其值正比于所有相位因子之和$\sum (-1)^{f(x)}$。若$f$为常数函数，各项相位一致发生相长干涉，测量得到全零态的概率为1；若为平衡函数，正负相位各半相互抵消发生相消干涉，全零态振幅为0。通过这一干涉特性即可实现100%区分。
</think>

<reasoning>
Deutsch-Jozsa算法的数学推导展示了量子态在Hadamard变换和Oracle作用下的精美相位演化。设输入规模为$n$位比特，我们需要判断黑盒函数 $f: \{0,1\}^n \rightarrow \{0,1\}$ 是常数函数（所有输入映射到同一输出）还是平衡函数（一半输入映射到0，另一半映射到1）。

推导过程分为以下几个核心步骤：

**1. 初始态准备**
系统由 $n$ 个工作量子比特和 1 个辅助量子比特构成。初始态设定为：
$$|\psi_0\rangle = |0\rangle^{\otimes n} |1\rangle$$

**2. 第一步Hadamard变换**
对所有的量子比特施加Hadamard门。对于前 $n$ 个比特，由于 $H|0\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$，叠加后可得均匀叠加态；辅助比特经过 $H|1\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$。整体量子态演化为：
$$|\psi_1\rangle = \frac{1}{\sqrt{2^n}} \sum_{x=0}^{2^n-1} |x\rangle \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$$

**3. 预言机 $U_f$ 的作用**
量子Oracle $U_f$ 的定义为 $U_f|x\rangle|y\rangle = |x\rangle|y \oplus f(x)\rangle$。当辅助比特处于 $\frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$ 这种特殊状态时，它相当于一个相位存储器：
$$U_f \left( |x\rangle \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) \right) = (-1)^{f(x)} |x\rangle \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$$
这意味着函数值 $f(x)$ 被编码到了工作比特的相对相位上。由于辅助比特不再与工作比特发生纠缠，我们可以忽略它，此时前 $n$ 个工作比特的态变为：
$$|\psi_2\rangle = \frac{1}{\sqrt{2^n}} \sum_{x=0}^{2^n-1} (-1)^{f(x)} |x\rangle$$

**4. 第二步Hadamard变换**
再次对前 $n$ 个工作比特施加Hadamard门。已知对任意计算基态 $|x\rangle$ 作用 $H^{\otimes n}$ 的公式为：
$$H^{\otimes n}|x\rangle = \frac{1}{\sqrt{2^n}} \sum_{z=0}^{2^n-1} (-1)^{x \cdot z} |z\rangle$$
其中 $x \cdot z = x_0z_0 \oplus x_1z_1 \oplus \dots \oplus x_{n-1}z_{n-1}$ 是按位与的内积。将此公式代入 $|\psi_2\rangle$，得到演化后的最终态：
$$|\psi_3\rangle = \frac{1}{2^n} \sum_{z=0}^{2^n-1} \left[ \sum_{x=0}^{2^n-1} (-1)^{f(x)} (-1)^{x \cdot z} \right] |z\rangle$$

**5. 概率计算与判定证明**
最后，我们测量前 $n$ 个工作比特。测量得到状态 $|z\rangle$ 的概率振幅为 $A(z) = \frac{1}{2^n} \sum_{x=0}^{2^n-1} (-1)^{f(x) + x \cdot z}$。

特别地，我们关注测量结果为 $|0\rangle^{\otimes n}$ （即 $z=0$）的概率。此时振幅 $A(0)$ 为：
$$A(0) = \frac{1}{2^n} \sum_{x=0}^{2^n-1} (-1)^{f(x)}$$
测量得到全0态的概率为 $P(0) = |A(0)|^2$。

- **情形一：若 $f(x)$ 为常数函数**
若 $f(x) = 0$，则 $(-1)^{f(x)} = 1$，求和项为 $2^n$；若 $f(x) = 1$，则 $(-1)^{f(x)} = -1$，求和项为 $-2^n$。无论哪种情况，振幅 $A(0) = \pm 1$。
因此概率 $P(0) = |\pm 1|^2 = 1$。测量结果必定是 $|00\dots 0\rangle$。

- **情形二：若 $f(x)$ 为平衡函数**
$f(x)=0$ 的情况占一半，提供 $+1$；$f(x)=1$ 的情况占一半，提供 $-1$。正负项在求和时完全相互抵消，即 $\sum (-1)^{f(x)} = 0$。
因此振幅 $A(0) = 0$，概率 $P(0) = 0$。这意味着测量结果绝对不可能出现全0态，必然会测得至少包含一个1的其他基底状态。

**结论**
通过上述推导可知，只需在量子计算机上运行一次该电路，如果测量结果全为0，则确信 $f(x)$ 是常数函数；如果测量结果包含1，则确信 $f(x)$ 是平衡函数。这实现了100%的成功率，且查询复杂度仅为 $O(1)$，相比经典算法所需的 $O(2^{n-1}+1)$ 次查询，呈现出了指数级的量子加速。
</reasoning>

## isqQA/quantum_algorithms/131_isq_implementation

- task_id: `isqQA/quantum_algorithms/131_isq_implementation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_implementation`, `algorithm`, `量子半加器`
- source: `qa_pipeline`
- dataset_index: `2219`

### Prompt

如何使用isQ量子编程语言实现一个量子半加器？请提供完整的代码实现，并逐行注释解释其工作原理和量子门的物理意义。

### Reference answer

<think>
要实现量子半加器，首先需要将经典逻辑转化为量子可逆线路。半加器的核心逻辑为：和位对应异或操作（XOR），进位位对应与操作（AND）。在量子计算中，异或操作可以直接通过受控非门（CNOT）实现，而与操作则需要通过多控的Toffoli门（CCX门）实现。

其次，由于量子操作必须是可逆的，不能直接覆盖输入态，因此线路设计需要引入额外的辅助量子比特。我们需要分配四个量子比特：两个作为输入态，两个初始化为|0>的辅助比特分别用于存储Sum和Carry的输出结果。

最后，基于上述逻辑映射和比特分配，即可构建isQ代码结构。声明量子比特数组后，通过X门对输入比特进行初始化（如置为|1>以验证逻辑），然后依次应用CNOT门和Toffoli门，将输入比特作为控制位，对应的输出辅助比特作为目标位，从而完成半加器的逻辑验证。
</think>

在量子计算中，半加器是构建复杂量子算术电路的基础组件。半加器的功能是将两个单比特量子态（通常表示为输入A和B）相加，并输出两个结果：和位（Sum）与进位位（Carry）。在经典逻辑中，和位对应于异或操作（XOR），即 $Sum = A \oplus B$；进位位对应于与操作（AND），即 $Carry = A \wedge B$。在量子线路中，异或操作可以通过受控非门（CNOT）来实现，而与操作则需要使用三比特的Toffoli门（或称CCX门）来实现。为了在量子体系下无损且可逆地执行这一过程，我们需要使用四个量子比特：两个用于存储输入数据，两个用于存储输出数据（初始均置为 $|0\rangle$）。

以下是使用isQ量子编程语言实现量子半加器的完整代码。在此示例中，为了验证半加器的功能，我们将输入A和B通过X门初始化为 $|1\rangle$ 状态，预期的计算结果应为 $Sum=0$ 且 $Carry=1$。

```isq
import std;

// 全局声明4个量子比特：q[0]为输入A，q[1]为输入B，q[2]为输出Sum，q[3]为输出Carry
qbit q[4];

procedure main() {
    // 初始化输入A为|1>。X门的作用是将|0>翻转为|1>
    X(q[0]);
    
    // 初始化输入B为|1>。
    X(q[1]);
    
    // 计算Sum位 (A XOR B)
    // 第一个CNOT门：如果q[0]为|1>，则翻转q[2]。此时q[2]的状态等于A
    CNOT(q[0], q[2]);
    // 第二个CNOT门：如果q[1]为|1>，则翻转q[2]。此时q[2]被翻转两次(1^1=0)或一次(1^0=1)，完成异或操作
    CNOT(q[1], q[2]);
    
    // 计算Carry位 (A AND B)
    // Toffoli门：只有当控制位q[0]和q[1]同时为|1>时，才会翻转目标位q[3]
    // 这完美等价于经典逻辑中的与门(AND)
    Toffoli(q[0], q[1], q[3]);
    
    // 测量所有量子比特，将量子态坍缩到经典寄存器中
    // 在isQ中，M()函数返回测量的经典值(0或1)
    int r0 = M(q[0]);
    int r1 = M(q[1]);
    int r2 = M(q[2]); // 预期结果为0
    int r3 = M(q[3]); // 预期结果为1
}
```

**代码原理解析**：
1. `X` 门操作：在代码开头对 `q[0]` 和 `q[1]` 执行 `X` 门，将默认的 $|0\rangle$ 态翻转为 $|1\rangle$ 态。这模拟了输入值 $A=1, B=1$ 的情况。
2. 异或求和（Sum）：通过串联两个 `CNOT` 门实现。第一个 `CNOT` 将输入A的值复制到Sum位（因为Sum位初始为0，A⊕0=A）；第二个 `CNOT` 作用后，Sum位变为A⊕B，这就是半加器中和位的计算原理。
3. 进位计算（Carry）：使用 `Toffoli` 门。Toffoli门包含两个控制位和一个目标位。由于初始Carry位为0，只有当A和B均为1时，目标位才会被翻转成1。这符合布尔代数中的与逻辑，即向高位进位。
4. 测量操作：最后对4个比特进行测量。对于输入 $|11\rangle$，计算结果必定是Sum位 $|0\rangle$ 和Carry位 $|1\rangle$。

## isqTrain/2919

- task_id: `isqTrain/2919`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_classical_vars`, `isq_syntax_if_else`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `measurement_order`
- source: `isq_train_cot`
- dataset_index: `307`

### Prompt

Something is wrong with this isQ circuit. Identify the error and provide the corrected code.

```isq
import std;
bool m1, m2;
qbit q_1, q_2, q_3;
// Teleport |0> state
procedure Teleport(qbit qsrc, qbit qanc, qbit qdest) {
    H(qanc);
    CNOT(qanc, qdest);
    CNOT(qsrc, qanc);
    // H(qsrc); // BUG: missing Hadamard
    m1 = M(qsrc);
    m2 = M(qanc);
    if (m2) { X(qdest); }
    if (m1) { Z(qdest); }
}
procedure main() {
    Teleport(q_1, q_2, q_3);
    M(q_3);
}

```

### Chain-of-thought reasoning

The buggy code has a missing Hadamard gate on `qsrc` before measurement. The line `// H(qsrc);` is commented out. This breaks the teleportation protocol because the Bell measurement requires applying H to the source qubit before measurement.

Let me trace through the corrected circuit:

1. Initial state: |000⟩ (q_1, q_2, q_3)
2. H(qanc) = H(q_2): |0⟩⟨0| → |+⟩, so state is |0+0⟩ = |000⟩ + |010⟩ / √2
3. CNOT(qanc, qdest) = CNOT(q_2, q_3): creates Bell pair between q_2 and q_3: state is |0⟩(|00⟩ + |11⟩)/√2
4. CNOT(qsrc, qanc) = CNOT(q_1, q_2): state is (|000⟩ + |011⟩)/√2
5. H(qsrc) = H(q_1): state is (|+00⟩ + |011⟩)/√2 = (|000⟩ + |100⟩ + |011⟩ + |111⟩)/2

Now measuring q_1 and q_2:
- |000⟩: m1=0, m2=0 → no corrections, q_3 = |0⟩
- |100⟩: m1=1, m2=0 → Z correction, q_3 = |0⟩
- |011⟩: m1=0, m2=1 → X correction, q_3 = |0⟩
- |111⟩: m1=1, m2=1 → X then Z, q_3 = |0⟩

After corrections, q_3 is always |0⟩.

The measurement probabilities with q_1 measured first (higher bit), then q_2, then q_3:
- |000⟩: 0.25
- |100⟩: 0.25
- |011⟩: 0.25
- |111⟩: 0.25

Wait, but The predicted output {|001>: 0.25, |010>: 0.25, |101>: 0.25, |110>: 0.25}. Let me reconsider the measurement ordering.

In the --probs output: "earlier measured qubit = higher bit". So m1 = M(qsrc) is measured first → higher bit, m2 = M(qanc) is measured second → middle bit, M(q_3) is measured third → lowest bit.

Wait, but M(q_3) happens after the corrections. So let me think again...

After corrections, q_3 should be |0⟩. So the final bit should be 0. But The predicted output bit 0 being 1 sometimes... Let me re-read.

Expected: {|001>: 0.25, |010>: 0.25, |101>: 0.25, |110>: 0.25}

Hmm, so q_3 ends up as |1⟩ sometimes? That doesn't match teleporting |0⟩.

Wait, let me re-read the measurement ordering. "earlier measured qubit = higher bit". 

m1 = M(qsrc) → measured first → bit 2 (highest)
m2 = M(qanc) → measured second → bit 1 (middle)
M(q_3) → measured third → bit 0 (lowest)

After teleportation with corrections, q_3 should be in the state that was originally in q_1, which is |0⟩. So M(q_3) should always be 0.

But The predicted output the last bit being 1 half the time... 

Hmm, wait. Let me re-examine. Maybe the corrections are wrong in some way?

Actually wait - let me look at the correction order. In standard teleportation:
- if m1 (Bell measurement on source): apply Z
- if m2 (Bell measurement on ancilla): apply X

Let me re-examine. Standard teleportation: After the Bell measurement, if the measurement results are (m1, m2):
- (0,0): no correction
- (0,1): X correction  
- (1,0): Z correction
- (1,1): ZX correction

This matches the code: `if (m2) { X(qdest); }` then `if (m1) { Z(qdest); }`

After proper corrections, q_3 should be |0⟩. So M(q_3) = 0 always.

Expected: |001>: 0.25, |010>: 0.25, |101>: 0.25, |110>: 0.25

Hmm, that would mean q_3 ends up as |

## isqTrain/734

- task_id: `isqTrain/734`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `phase_manipulation`, `qft_based_arithmetic`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3966`

### Prompt

Code this in isQ: implements the qft_adder pattern using an alternative gate decomposition (CNOT -> H CZ H). The circuit must produce the same output as the standard decomposition.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a 2-qubit QFT adder using CNOT→(H-CZ-H) decomposition for bit-reversal swap, producing equal superposition output.
2. **Qubits**: 2 qubits (q[0], q[1]), both measured.
3. **State evolution**: |00⟩ →X,X→ |11⟩ →QFT(H,ctrl S,H)→ (1/2)(|00⟩ + i|01⟩ - |10⟩ - i|11⟩) →3×CNOT swap(decomposed as H-CZ-H)→ equal superposition state with |amplitude|² = 1/4 each.
4. **Expected probabilities**: All basis states have equal probability 0.25 because QFT of |11⟩ produces equal-magnitude amplitudes, preserved through the swap decomposition.

## isqTrain/4331

- task_id: `isqTrain/4331`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4120`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;
qbit q[2];

procedure my_z(qbit a) {
    Z(a);
} deriving gate

procedure main() {
    // Prepare eigenstate |1>
    X(q[1]);
    // Prepare counting register
    H(q[0]);
    // Apply controlled-U
    ctrl my_z(q[0], q[1]);
    // Inverse QFT (for 1 qubit it's just H)
    H(q[0]);
    // Measure
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]);
}

```

### Chain-of-thought reasoning

The user wants to analyze an isQ quantum program and predict the probability distribution of measurement outcomes.
The program uses 2 qubits, `q[0]` and `q[1]`.
Let's trace the state step by step:
1. Initial state: |00>
2. `X(q[1])`: applies X to q[1]. State becomes |01>
3. `H(q[0])`: applies H to q[0]. State becomes 1/sqrt(2)(|00> + |10>) * 1 for q[1] => 1/sqrt(2)(|00> + |10>) wait, |00> + |10> with q[1]=1 is |01> + |11>. So state is 1/sqrt(2) (|01> + |11>).
4. `ctrl my_z(q[0], q[1])`: controlled-Z on q[1], controlled by q[0]. `my_z` applies Z to `a`. So it's CZ(q[0], q[1]).
State becomes 1/sqrt(2) (|01> - |11>).
Wait, eigenstate of Z is |1>, which has eigenvalue -1.
Let's re-evaluate 1/sqrt(2) (|0> + |1>) |1>.
Applying CZ: |0>|1> -> |0>|1>. |1>|1> -> -|1>|1>.
State is 1/sqrt(2) (|01> - |11>).
5. `H(q[0])`: applies H to q[0].
|01> -> 1/sqrt(2)(|01> + |11>)
-|11> -> -1/sqrt(2)(|01> - |11>)
Sum: 1/2 (|01> + |11> - |01> + |11>) = |11>.
Wait, if we measure at this point, we get eigenvalue +1 (which maps to phase 0) because |1> is -1 eigenstate of Z, wait!
Ah! Let's check eigenvalues of Z.
Z|0> = |0> (eigenvalue 1)
Z|1> = -|1> (eigenvalue -1)
Phase estimation for Z on |1> gives eigenvalue -1, which is e^{i*pi}.
The phase is pi, which is 1 in binary (1/2).
So the QPE output should be |1>.
Indeed, my calculation gave |11>.
6. `X(q[0])`: flips q[0].
State becomes |01>.
7. `M(q[0])`: measures q[0]. It will be 0 with probability 1.
Wait, the prompt asks for probability distribution of measurement outcomes.
the predicted output format from the reference:
"Expected measurement probabilities: {|00>: 1.0}
Number of qubits measured: 2"
Wait, `M(q[0])` measures only q[0] in the code, but standard `--probs` mode might track the whole register if asked for the probability distribution of all qubits, or maybe just the measured ones?
Ah, The implementation says `Expected measurement probabilities: {|00>: 1.0} Number of qubits measured: 2`.
But `q[1]` is not measured. If `M(q[0])` is the only measurement, then it collapses to |0> for q[0]. The whole state is |01>, so the bitstring is `00` (wait, if earlier measured qubit = higher bit, q[0] is bit 1, q[1] is bit 0. No, if `q[0]` is measured, its outcome is `0`. If it represents `q[0]q[1]` then `q[0]` is the higher bit? "earlier measured qubit = higher bit". So if only `q[0]` is measured, maybe it's just 0, but it says {|00>: 1.0}? Wait, if `q[0]` is the only measured qubit, then maybe it prints `{|0>: 1.0}`. But the reference says `{|00>: 1.0}`. Let me just write the analysis and then the final probability distribution.
Let's trace again carefully.
Initial: |00>
X(q[1]) -> |01>
H(q[0]) -> 1/sqrt(2)(|01> + |11>)
ctrl my_z (CZ): -> 1/sqrt(2)(|01> - |11>)
H(q[0]) -> 1/2(|01> + |11> - |01> + |11>) = |11>
X(q[0]) -> |01>

### Reference answer

{'predicted_probs': {'00': 1.0}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|00>) = 1.0000.'}

## isqTrain/3976

- task_id: `isqTrain/3976`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `532`

### Prompt

Fix the bug in this quantum program:

```
import std;
// QFT on 4 qubits with input state |0001>
qbit q[4];

procedure main() {
    // Prepare input state |0001>
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
    CNOT(q[0], q[3]);
    CNOT(q[0], q[3]);
    // Swap q[1] and q[2]
    CNOT(q[1], q[2]);
    CNOT(q[2], q[1]);
    CNOT(q[1], q[2]);
    // Measure after QFT
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

``` (bug type: swapped qubits)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug location**: The second CNOT in the swap of q[0] and q[3] has swapped arguments: `CNOT(q[0], q[3])` appears instead of `CNOT(q[3], q[0])`.

2. **Fix**: Change the middle CNOT in the q[0]-q[3] swap from `CNOT(q[0], q[3])` to `CNOT(q[3], q[0])`, making it follow the standard CNOT-swap pattern: CNOT(a,b) → CNOT(b,a) → CNOT(a,b).

3. **State evolution** (corrected circuit):
   - Start: |0000⟩ → X(q[3]) → |0001⟩
   - QFT stages apply H and controlled-Rz rotations on each qubit, transforming |0001⟩ → (1/4)Σ_k e^{2πik/16}|k⟩ (in reverse bit order)
   - Correct swaps reverse qubit order: q[0]↔q[3] and q[1]↔q[2]
   - Final state: (1/4)Σ_{k=0}^{15} e^{2πik/16}|k⟩, giving equal probability 1/16 = 0.0625 for each of the 16 basis states

## isqTrain/4827

- task_id: `isqTrain/4827`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_import_qft`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4056`

### Prompt

用isQ实现prepares a state, applies QFT, and then inverse QFT, using intermediate X gates between them. Import std and qft. Declare 2 global qubits. Apply X(q[0]) and X(q[1]) to prepare |11>. Apply qft(q). Apply X(q[0]) to modify the state in frequency domain. Apply qft_inv(q). Measure both qubits.

### Chain-of-thought reasoning

Let me trace through this circuit step by step.

1. Start with |00>

2. Apply X(q[0]) and X(q[1]) to prepare |11>

3. Apply QFT to |11>. 

For a 2-qubit system, QFT maps:
|00> → (|00> + |01> + |10> + |11>)/2
|01> → (|00> - |01> + |10> - |11>)/2
|10> → (|00> + i|01> - |10> - i|11>)/2
|11> → (|00> - i|01> - |10> + i|11>)/2

So |11> → (|00> - i|01> - |10> + i|11>)/2

4. Apply X(q[0]) to modify state in frequency domain.

X(q[0]) flips qubit 0, so:
|00> → |01>
|01> → |00>
|10> → |11>
|11> → |10>

So the state becomes:
(|01> - i|00> - |11> + i|10>)/2
= (-i|00> + |01> + i|10> - |11>)/2

5. Apply QFT_inv.

QFT_inv is the inverse of QFT. Since QFT is unitary, QFT_inv = QFT†.

Let me think about what QFT does more carefully.

For 2 qubits, the QFT matrix is:
QFT|j⟩ = (1/√4) Σ_k e^{2πijk/4} |k⟩

So:
QFT|0⟩ = (|0⟩ + |1⟩ + |2⟩ + |3⟩)/2
QFT|1⟩ = (|0⟩ + i|1⟩ - |2⟩ - i|3⟩)/2
QFT|2⟩ = (|0⟩ - |1⟩ + |2⟩ - |3⟩)/2
QFT|3⟩ = (|0⟩ - i|1⟩ - |2⟩ + i|3⟩)/2

So |11⟩ = |3⟩ → (|0⟩ - i|1⟩ - |2⟩ + i|3⟩)/2 = (|00⟩ - i|01⟩ - |10⟩ + i|11⟩)/2

After X(q[0]):
|00⟩ → |01⟩
|01⟩ → |00⟩
|10⟩ → |11⟩
|11⟩ → |10⟩

So:
(-i|00⟩ + |01⟩ + i|10⟩ - |11⟩)/2

Now applying QFT_inv. Since QFT† = QFT_inv, we need to compute QFT† of this state.

Let me represent the state as a vector in the computational basis:
coefficients: (-i/2, 1/2, i/2, -1/2) for |00⟩, |01⟩, |10⟩, |11⟩

The QFT matrix for 2 qubits is:
F = (1/2) * [[1, 1, 1, 1],
             [1, i, -1, -i],
             [1, -1, 1, -1],
             [1, -i, -1, i]]

So F† = (1/2) * [[1, 1, 1, 1],
                  [1, -i, -1, i],
                  [1, -1, 1, -1],
                  [1, i, -1, -i]]

Applying F† to the vector (-i/2, 1/2, i/2, -1/2):

Component for |00⟩: (1/2)[1·(-i/2) + 1·(1/2) + 1·(i/2) + 1·(-1/2)] = (1/2)(-i/2 + 1/2 + i/2 - 1/2) = 0

Component for |01⟩: (1/2)[1·(-i/2) + (-i)·(1/2) + (-1)·(i/2) + i·(-1/2)]
= (1/2)(-i/2 - i/2 - i/2 - i/2) = (1/2)(-2i) = -i

Wait, let me redo this more carefully.

Component for |01⟩: (1/2)[1·(-i/2) + (-i)·(1/2) + (-1)·(i/2) + i·(-1/2
