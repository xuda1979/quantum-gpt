# ISQ training COT RAG corpus: quantum_algorithms shard 71

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4505

- task_id: `isqTrain/4505`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4132`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;

qbit q[2];

procedure main() {
    
    X(q[0]); H(q[1]);  // replaced H with X
    
    
    CZ(q[0], q[1]);
    
    
    H(q[0]); H(q[1]);
    
    X(q[0]); X(q[1]);
    CZ(q[0], q[1]);
    X(q[0]); X(q[1]);
    
    H(q[0]); H(q[1]);
    
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

Step 1: Initial state |00>
Step 2: X(q[0]) -> |10>
Step 3: H(q[1]) -> |1+> = 1/sqrt(2)(|10> + |11>)
Step 4: CZ(q[0], q[1]) -> 1/sqrt(2)(|10> - |11>) = |1->. The control q[0] is |1>, so Z is applied to q[1].
Step 5: H(q[0]), H(q[1]) -> H|1> H|-> = |-> |0> = 1/sqrt(2)(|00> - |10>)
Wait: H|1> = |->. H|-> = |1>. So H|1> H|-> = |-> |1>. Let's re-evaluate.
H on |1> is |->.
H on |-> is |1>.
So H(q[0])H(q[1]) on 1/sqrt(2)(|10> - |11>) is |-> |1> = 1/sqrt(2)(|01> - |11>).
Wait, q[0] is |-> and q[1] is |1>.
Let's trace carefully:
After X(q[0]): |10>
After H(q[1]): |1>(|0>+|1>)/sqrt(2) = (|10> + |11>)/sqrt(2)
After CZ(q[0], q[1]): (|10> - |11>)/sqrt(2). (Z applied to q[1] when q[0] is 1)
After H(q[0])H(q[1]):
H(q[0]) on |1> = (|0>-|1>)/sqrt(2)
H(q[1]) on (|0>-|1>)/sqrt(2) = |1>
So state is |-> |1> = (|01> - |11>)/sqrt(2).

Now, X(q[0]) X(q[1]):
(|10> - |00>)/sqrt(2).

CZ(q[0], q[1]):
|-0> is invariant under CZ. So CZ on (|10> - |00>)/sqrt(2) leaves it as (|10> - |00>)/sqrt(2).

X(q[0]) X(q[1]):
(|01> - |11>)/sqrt(2).

H(q[0]) H(q[1]):
q[0] was in (|0>-|1>)/sqrt(2), which is H|1>. H applied gives |1>.
q[1] was in (|0>-|1>)/sqrt(2) wait.
Let's apply H to qubits.
State is (|01> - |11>)/sqrt(2) = (|0> - |1>)/sqrt(2) |1>.
H on (|0>-|1>)/sqrt(2) is |1>.
H on |1> is |->.
So state is |1> |-> = (|10> - |11>)/sqrt(2).

Measurement:
q[0] is |1> with probability 1.
q[1] is |-> = (|0>-|1>)/sqrt(2), so measured as 0 with prob 0.5, and 1 with prob 0.5.
So overall states are |10> with prob 0.5, |11> with prob 0.5.
Let me double check the CZ(|-0>).
CZ applies Z to q[1] if q[0]=|1>.
|-0> = (|0> - |1>) |0> / sqrt(2) = (|00> - |10>)/sqrt(2).
Apply CZ: |00> remains |00>, |10> becomes -|11> wait.
CZ applies Z to q[1] (the target) if q[0] is |1>.
Wait, in isQ CZ(q[0], q[1]) applies Z to q[1] when q[0] is |1>.
So CZ(|10>) = -|11>? No, CZ(q[0], q[1]) applies Z to q[1]. Z|0> = |0>. So |10> remains |10>.
Ah! CZ applies Z to q[1] when control q[0] is |1>. If q[1] is |0>, it remains |0>.
Let's re-evaluate Step 4:
State: (|10> + |11>)/sqrt(2).
Apply CZ(q[0], q[1]). q[0] is the control.
|10> -> |10> (since q[1]=

### Reference answer

{'predicted_probs': {'10': 0.5, '11': 0.5}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|10>) = 0.5000, P(|11>) = 0.5000.'}

## isqQA/quantum_algorithms/49_principle_advantage

- task_id: `isqQA/quantum_algorithms/49_principle_advantage`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `principle_advantage`, `algorithm`, `量子行走算法`
- source: `qa_pipeline`
- dataset_index: `548`

### Prompt

请深入解析量子行走算法的核心原理及其相较于经典随机行走的优势。详细说明其物理与数学的宏观原理，对比在图遍历或搜索问题中与经典随机行走的时间复杂度差异，并深刻剖析带来这种量子加速的根本物理来源（如干涉效应、相干性等）。

### Reference answer

量子行走是经典随机行走 在量子力学框架下的推广，是众多量子算法（如量子搜索、图同构算法）的核心底层算子。其宏观原理、复杂度优势及加速来源可从以下三个维度深入剖析：

1. **物理与数学宏观原理**：
量子行走主要分为连续时间量子行走（CTQW）和离散时间量子行走（DTQW）。以DTQW为例，系统的状态空间不仅包含表示位置的节点空间，还包含表示方向的“硬币”空间。整个系统的量子态表示为位置态和硬币态的张量积。每一次量子行走操作由两步构成：首先是“掷硬币”操作，即对硬币态作用一个酉算子（如Hadamard门），使其进入不同方向的叠加态；其次是“条件移位”操作，即根据硬币态的不同取值，将位置态向相应的相邻节点演化。由于量子态的演化是线性和幺正的，行走者实际上同时探索了所有可能的路径，形成了一棵深度呈指数级增长的计算树。

2. **时间复杂度对比**：
在经典计算中，随机行走表现出扩散过程的特点。例如，在长度为$N$的直线图上，经典行走者从原点出发，需要$O(N^2)$步才能以常数概率到达边界；而在图搜索问题（如寻找$N$个节点中的特定标记节点）中，经典随机行走的命中时间复杂度为$O(N)$。
对比之下，量子行走展现出“弹道式”运动特征。在同样的直线图上，量子行走仅需$O(N)$步即可到达边界，实现了平方级加速。在基于图的搜索问题中（如连续时间量子行走搜索算法），寻找单个标记节点的时间复杂度可优化至$O(\sqrt{N})$，这与Grover算法的最优复杂度一致。更令人惊叹的是，在特定的图结构（如粘合树图 Glued Trees）中，量子行走从入口到达出口的时间复杂度仅为多项式级甚至是对数级，而经典随机行走由于容易陷入死胡同，需要指数级时间$O(2^N)$，这展现了量子行走在特定场景下的指数级加速优势。

3. **量子加速的根本来源**：
量子行走之所以能实现超越经典行走的加速，其根本物理来源在于**量子相干性与量子干涉效应**。
在经典随机游走中，概率是正实数的简单相加，不同路径的发生是互斥且耗散的，会导致概率分布随时间趋于均匀平坦。而在量子行走中，系统状态是由复数概率幅描述的。当行走的多个演化路径在交汇节点相遇时，概率幅之间会发生量子干涉：通向错误节点的路径相位相反，发生相消干涉从而概率幅相互抵消；而通向正确目标节点的路径相位一致，发生相长干涉使得概率幅迅速放大。这种基于波的干涉特性的负概率幅现象，使得量子行走能够以极其迅速且定向的方式穿过庞大且复杂的图结构，从而规避了经典过程必须经历的扩散耗散过程，实现了计算复杂度的本质飞跃。

## isqQA/quantum_algorithms/123_isq_implementation

- task_id: `isqQA/quantum_algorithms/123_isq_implementation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_implementation`, `algorithm`, `连续时间量子行走`
- source: `qa_pipeline`
- dataset_index: `2069`

### Prompt

如何在一个包含4个节点的环形图上实现连续时间量子行走，并利用isQ量子编程语言演示行走者从初始节点0演化至均匀叠加态（即实现完美的状态扩散）的过程？请提供包含完整数学原理推导及逐行注释的isQ代码。

### Reference answer

<think>
解决该问题的推理过程主要分为四个步骤：

首先，进行物理模型映射。将4节点环形图的状态空间映射到2个量子比特系统上，其中初始节点0对应量子态 $|00\rangle$。

其次，构建系统的哈密顿量与演化算符。根据图的邻接关系，推导出哈密顿量 $H = X \otimes I + I \otimes X$。由于这两项相互对易，时间演化算符 $U(t) = e^{-iHt}$ 可以完美分解为两个独立单比特演化的张量积。

接着，推导实现完美扩散所需的参数。将单比特演化 $e^{-iXt}$ 映射为标准的 $R_x$ 旋转门。为了让行走者达到均匀叠加态（即各节点概率幅绝对值相等），单比特状态需从 $|0\rangle$ 演化为 $(|0\rangle - i|1\rangle)/\sqrt{2}$，由此计算出旋转角度为 $\pi/2$，并反推出所需的最佳演化时间 $t = \pi/4$。

最后，进行代码逻辑转换。基于上述数学结论，在isQ代码中声明两个量子比特，并分别对其施加参数为 $\pi/2$ 的 $R_x$ 门，即可完成从初始态到均匀叠加态的量子行走演化过程的演示。
</think>

连续时间量子行走是经典随机游走在量子领域的对应，它不依赖硬币算符，而是直接基于图的哈密顿量进行连续的酉演化。在4节点环（即2维超立方体或周期性边界条件的环）上，节点可以用2个量子比特表示：|00>代表节点0，|01>代表节点1，|10>代表节点2，|11>代表节点3。该图的邻接矩阵哈密顿量可映射为泡利-X算符的张量积组合：H = X ⊗ I + I ⊗ X。由于这两部分是对易的，系统的时间演化算符U(t) = exp(-iHt)可以完美分解为张量积形式：
U(t) = exp(-i(X ⊗ I)t) · exp(-i(I ⊗ X)t) = exp(-iXt) ⊗ exp(-iXt)。
在标准量子门集中，exp(-iXt)等价于绕X轴旋转门 Rx(2t)。如果我们设定演化时间 t = π/4，那么旋转角度 θ = 2t = π/2。初始状态设定为行走者位于节点0，即 |00>。演化后状态将为 Rx(π/2)|0> ⊗ Rx(π/2)|0>。由于 Rx(π/2)|0> = (|0> - i|1>)/√2，最终系统状态将变为 (|00> - i|01> - i|10> - |11>)/2，此时测量得到4个节点的概率均等，均为25%，展现了量子行走在特定时间步的完美扩散特性。

以下是实现该连续时间量子行走的完整isQ代码及逐行注释：

import std;

// 声明包含2个量子比特的全局数组
// 2个量子比特恰好能编码4个节点的环形拓扑结构
qbit q[2];

procedure main() {
    // 行走者初始位于节点0，即二进制状态|00>
    // isQ默认全局声明量子比特初态为|0>，因此无需进行额外初始化操作

    // 设定连续时间量子行走的演化时间参数 t = PI / 4
    // 完美扩散在哈密顿量 H = X(x)I + I(x)X 下发生在 t = π/4 时刻
    real t = 3.1415926535 / 4.0;

    // 计算对应的量子门旋转角度 theta = 2 * t = π / 2
    // 这是因为演化算符 exp(-iHt) 展开后，单比特演化为 exp(-iXt) = Rx(2t)
    real theta = 2.0 * t;

    // ----------------- 执行连续时间量子行走 -----------------
    // 哈密顿量 H = X ⊗ I + I ⊗ X 意味着我们需要在各个子系统上独立作用 Rx 门
    // 对第一个量子比特作用 Rx(theta) 门，等效于执行 exp(-i X t) ⊗ I
    Rx(theta, q[0]);
    
    // 对第二个量子比特作用 Rx(theta) 门，等效于执行 I ⊗ exp(-i X t)
    Rx(theta, q[1]);

    // ----------------- 测量与输出 -----------------
    // 测量两个量子比特，观察行走者的最终位置分布
    // 预期结果将以均匀的概率 (25%) 塌缩到 00, 01, 10, 11 中的任意一个
    int r0 = M(q[0]);
    int r1 = M(q[1]);
    
    // 经典控制：如果需要确保将带有负相位的状态恢复为标准的基态，可在此应用Z门修正
    // 但对于概率测量而言，全局相位和相对相位不影响绝对概率的分布
    if (r0 == 1) {
        // 可选的相位恢复操作，这里省略以观察原始演化结果
    }
}

## isqTrain/950

- task_id: `isqTrain/950`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `hamiltonian_simulation`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `81`

### Prompt

Implement a quantum circuit in isQ: implements a variant of the pauli_evolution pattern using q[1] -> q[3]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

The user wants me to generate reasoning for a quantum circuit that implements a variant of the pauli_evolution pattern using q[1] -> q[3]. Let me analyze The implementation:

1. The circuit uses 3 qubits (q[0], q[1], q[2])
2. Only q[0] is actively used in the computation
3. q[1] and q[2] remain in |0⟩ state (ground state)
4. The circuit implements:
   - H(q[0]): Creates |+⟩ = (|0⟩ + |1⟩)/√2
   - Rz(π/2, q[0]): Pauli-Z evolution e^(-i*π/4*Z), adds phase to components
   - H(q[0]): Converts phase back to amplitude
   - M(q[0]), M(q[1]), M(q[2]): Measure all qubits

Let me trace the state evolution:

Initial: |000⟩

After H(q[0]): (|0⟩ + |1⟩)/√2 ⊗ |00⟩ = (|000⟩ + |100⟩)/√2

After Rz(π/2, q[0]): The Rz gate applies:
- |0⟩ → e^(-i*π/4)|0⟩
- |1⟩ → e^(i*π/4)|1⟩

So: (e^(-i*π/4)|000⟩ + e^(i*π/4)|100⟩)/√2

After H(q[0]):
H applied to the first qubit:
- e^(-i*π/4)|0⟩ → e^(-i*π/4)(|0⟩ + |1⟩)/√2
- e^(i*π/4)|1⟩ → e^(i*π/4)(|0⟩ - |1⟩)/√2

Combined: (e^(-i*π/4) + e^(i*π/4))|0⟩/2 + (e^(-i*π/4) - e^(i*π/4))|1⟩/2

Using Euler's formula:
- e^(-i*π/4) + e^(i*π/4) = 2cos(π/4) = √2
- e^(-i*π/4) - e^(i*π/4) = -2i*sin(π/4) = -i√2

So the state becomes: √2/2 |0⟩ + (-i√2/2)|1⟩ = (|0⟩ - i|1⟩)/√2 ⊗ |00⟩

The probabilities are:
- |000⟩: |1/√2|² = 0.5
- |100⟩: |−i/√2|² = 0.5

This matches the predicted output.

Now I need to write the reasoning section. The task mentions "q[1] -> q[3]" which suggests expanding the register. Analyzing the, it uses q[0] as the active qubit, and the variant should use q[1] instead.

Wait, let me re-read the prompt. It says "using q[1] -> q[3]". This could mean:
1. Use qubits q[1], q[2], q[3] (4 qubits total)
2. Or the arrow notation means something else

Analyzing the circuit requirements which has 3 qubits and measures all of them, and The predicted output 3 qubits measured, I think the variant should:
- Use q[1] instead of q[0] for the active computation
- Keep the expanded register with qubits in ground state

But wait, the predicted output show |000⟩ and |100⟩ with 3 qubits measured. If q[1] is the active qubit, the measurement would show |000⟩ and |010⟩ (q[1] = higher significance bit in the 3-bit string... actually I need to check the bit ordering).

Let me think about this more carefully. The prompt says "q[1] -> q[3]" - this might mean using q[1] through q[3], which would be 4 qubits total. But the reference uses 3 qubits.

Actually, looking more carefully at The implementation and predicted output, the reference already uses q[0] as the active qubit. The task says to implement a "variant" using q[1] -> q[3].

Hmm, but The predicted output the same probabilities as if q[0] is active. Let me re-read...

The predicted output: {|000>: 0.5, |100>: 0.5}

This means q[0] is in a superposition, and q[1], q[

## isqTrain/2810

- task_id: `isqTrain/2810`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_procedures`, `measurement_order`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4417`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit w[5];
procedure main() {
    X(w[0]); 
    for i in 0:3{
        X2P(w[i]);
        Y2P(w[i+1]);
        CNOT(w[i], w[i+1]);
    }
    for i in 0:3{
        for j in 0:3{
            for k in 0:3{
                H(w[(i+j+k) % 5]);
            }
        }
    }
    for i in 0:5{
        M(w[i]);
    }
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a concise, step-by-step quantum state analysis of a given isQ program. The final output must contain the reasoning and the probability distribution of the measured states.

2.  **Analyze the isQ code:**
    *   `qbit w[5];` - 5 qubits, initialized to $|0\rangle^{\otimes 5}$.
    *   `X(w[0]);` - Applies X to $w_0$. State becomes $|10000\rangle$.
    *   `for i in 0:3 { X2P(w[i]); Y2P(w[i+1]); CNOT(w[i], w[i+1]); }` - Repeats for $i=0,1,2,3$.
        *   $X2P$ is $R_x(\pi/2)$. Matrix: $\frac{1}{\sqrt{2}} \begin{pmatrix} 1 & -i \\ -i & 1 \end{pmatrix}$.
        *   $Y2P$ is $R_y(\pi/2)$. Matrix: $\frac{1}{\sqrt{2}} \begin{pmatrix} 1 & -1 \\ 1 & 1 \end{pmatrix}$.
        *   Let's trace carefully.
        *   Wait, let's look at the actual loop behavior. This creates entanglement.
        *   Is there a simpler way? Let's trace step by step.
        *   Initial: $|10000\rangle$.
        *   i=0:
            *   $X2P(w[0])$ on $|1\rangle$: $\frac{1}{\sqrt{2}}(|0\rangle - i|1\rangle)$.
            *   $Y2P(w[1])$ on $|0\rangle$: $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
            *   CNOT(0,1): Control is $w[0]$, target is $w[1]$.
                *   If $w[0]=0$, $w[1]$ is unchanged.
                *   If $w[0]=1$, $w[1]$ is flipped.
                *   State: $\frac{1}{2} [ |0\rangle(|0\rangle+|1\rangle) - i|1\rangle(|1\rangle+|0\rangle) ] = \frac{1-i}{2} |00\rangle + \frac{1-i}{2} |11\rangle$?
                *   Wait.
                *   Let's do it exactly:
                *   $w_0 = \frac{1}{\sqrt{2}}|0\rangle - \frac{i}{\sqrt{2}}|1\rangle$
                *   $w_1 = \frac{1}{\sqrt{2}}|0\rangle + \frac{1}{\sqrt{2}}|1\rangle$
                *   Product state: $\frac{1}{2}|00\rangle + \frac{1}{2}|01\rangle - \frac{i}{2}|10\rangle - \frac{i}{2}|11\rangle$.
                *   Apply CNOT(0,1): (control=0, target=1)
                *   $|00\rangle \to |00\rangle$
                *   $|01\rangle \to |01\rangle$
                *   $|10\rangle \to |11\rangle$
                *   $|11\rangle \to |10\rangle$
                *   State becomes: $\frac{1}{2}|00\rangle + \frac{1}{2}|01\rangle - \frac{i}{2}|11\rangle - \frac{i}{2}|10\rangle = \frac{1}{2}(|0\rangle + i|1\rangle)(|0\rangle + i|1\rangle)$?
                *   Let's check: $(|0\rangle+i|1\rangle)(|0\rangle+i|1\rangle) = |00\rangle + i|01\rangle + i|10\rangle - |11\rangle$. No.
                *   Let's re-group: $\frac{1}{2}|0\rangle(|0\rangle+|1\rangle) - \frac{i}{2}|1\rangle(|1\rangle+|0\rangle) = \frac{1-i}{2}(|00\rangle + |11\rangle)$. Ah, yes.
                *   So after i=0, $w_0, w_1$ are in the state $\frac{1-i}{2}(|00\rangle + |11\rangle)$.
        *

### Reference answer

{'predicted_probs': {'00000': 0.12499999999999994, '00100': 0.12500000000000006, '01000': 0.12499999999999994, '01100': 0.12499999999999997, '10000': 0.12500000000000003, '10100': 0.1250000000000001, '11000': 0.12499999999999986, '11100': 0.12500000000000003}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/683

- task_id: `isqTrain/683`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `ancilla_usage`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1474`

### Prompt

Write an isQ program that implements the half_full_adder pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a half adder with inputs a=1, b=1, computing sum (a⊕b) and carry (a∧b), with reversed measurement order.
2. **Qubits**: 4 qubits — q[0]=input a, q[1]=input b, q[2]=sum, q[3]=carry; only q[3] and q[2] are measured.
3. **State evolution**: |0000⟩ →X(q[0])→ |1000⟩ →X(q[1])→ |1100⟩ →CNOT(q[0],q[2])→ |1110⟩ →CNOT(q[1],q[2])→ |1100⟩ →Toffoli(q[0],q[1],q[3])→ |1101⟩
4. **Measurement order**: M(q[3]) first (carry=1, higher bit), M(q[2]) second (sum=0, lower bit) → bitstring |10⟩.
5. **Result**: For inputs 1+1, sum=0 and carry=1, giving expected probabilities {|10⟩: 1.0}.

## isqTrain/721

- task_id: `isqTrain/721`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5263`

### Prompt

Write an isQ program that implements the ripple_carry_adder pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Implement a ripple-carry adder adding a=1 (binary 01) and b=1 (binary 01), producing sum=2 (binary 10).

2. Uses 5 qubits: q[0]=a0, q[1]=a1, q[2]=b0, q[3]=b1, q[4]=carry; measures q[3] (sum1) then q[2] (sum0).

3. State evolution (in |q[0]q[1]q[2]q[3]q[4]> order):
   - Initial: |00000⟩
   - After X(q[0]), X(q[2]): |10100⟩ (encode a=01, b=01)
   - Toffoli(q[0],q[2],q[4]): |10101⟩ (carry0 = a0 AND b0 = 1)
   - CNOT(q[0],q[2]): |10001⟩ (sum0 = a0 XOR b0 = 0)
   - CNOT(q[1],q[3]): |10001⟩ (q[1]=0, no change)
   - CNOT(q[4],q[3]): |10011⟩ (sum1 = a1 XOR b1 XOR carry0 = 1)

4. Measurement order: M(q[3]) first (higher

## isqTrain/921

- task_id: `isqTrain/921`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `boolean_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3455`

### Prompt

Implement the following in isQ: implements the boolean_synthesis pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement XNOR(1,1) using CNOT-based XOR synthesis with an explicit H-H identity pair to show gate cancellation awareness.

Qubits: 3 (q[0], q[1], q[2]); all are measured, yielding a 3-bit outcome.

State evolution:
1. Start in |000⟩; apply X to q[0], q[1] → |110⟩ (inputs a=1, b=1, ancilla=0).
2. CNOT(q[0], q[2]) flips q[2] (control q[0]=1) → |111⟩.
3. CNOT(q[1], q[2]) flips q[2] again (control q[1]=1) → |110⟩ (XOR(1,1)=0 in q[2]).
4. X(q[2]) negates q[2] → |111⟩ (XNOR(1,1)=1).
5. H(q[0]) followed by H(q[0]) is an identity pair; since H²=I, the state remains |111⟩.
6. Measure all qubits.

Expected probabilities: Since the final state is |111⟩, measurement yields outcome 111 with probability 1.0.

## isqTrain/100

- task_id: `isqTrain/100`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `3982`

### Prompt

Create an isQ quantum circuit that implements the bell_state_preparation pattern but with a different initial state preparation (flip q[[0]] -> q[2]).

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for the provided isQ code.
The code is a Bell state preparation / teleportation-like circuit with 3 qubits.
Let's analyze the circuit:
Qubits: q[0], q[1], q[2]
Initial state: |000>
X(q[2]) -> |001>
H(q[1]) -> |0+1>
CNOT(q[1], q[2]) -> |0> (|00> + |11>) ... wait, wait.
Wait, if q[1] is control and q[2] is target:
|001> -> H(q[1]) -> |001> + |011> over sqrt(2)
CNOT(q[1], q[2]) -> |001> + |110> over sqrt(2) ... wait!
Let's trace it carefully:
Initial state: |000>
X(q[2]) -> |001>
H(q[1]) -> 1/sqrt(2) (|001> + |011>)
CNOT(q[1], q[2]) -> 1/sqrt(2) (|001> + |110>)
CNOT(q[0], q[1]) -> 1/sqrt(2) (|001> + |110>)
H(q[0]) -> 1/2 (|001> + |101> + |010> - |110>) ... Wait, H on q[0] of |0> gives |0>+|1>, so:
|0> (|001>) -> 1/sqrt(2) (|001> + |101>)
|1> (|110>) -> 1/sqrt(2) (|110> - |010>)
Total state after H(q[0]): 1/2 (|001> + |101> + |110> - |010>)

Let's reorder qubits: q[2], q[1], q[0]
|001> -> q2=1, q1=0, q0=0 -> |100>
|101> -> q2=1, q1=0, q0=1 -> |101>
|110> -> q2=0, q1=1, q0=1 -> |011>
|010> -> q2=0, q1=1, q0=0 -> |010>
Actually, let's keep q[0]q[1]q[2] order.
|001> = |0>|0>|1>
|101> = |1>|0>|1>
|110> = |1>|1>|0>
|010> = |0>|1>|0>
CNOT(q[1], q[2]):
q[1] controls q[2].
For |001>, q[1]=0, q[2]=1 -> no flip -> |001>
For |101>, q[1]=0, q[2]=1 -> no flip -> |101>
For |110>, q[1]=1, q[2]=0 -> flip -> |111>
For |010>, q[1]=1, q[2]=0 -> flip -> |011>
State after CNOT(q[1], q[2]):
1/2 (|001> + |101> + |111> - |011>)
Notice that q[2] is always 1 now. Let's write it as:
|q0>|q1>|1>
Coefficients:
|00> -> 1
|10> -> 1
|11> -> 1
|01> -> -1
Wait, what is the state before ctrl my_z?
Wait, CNOT(q[1], q[2]) then ctrl my_z(q[0], q[2])
my_z is Z. ctrl my_z(q[0], q[2]) means CZ(q[0], q[2]).
Z on q[2] applies a -1 phase if q[2] is |1>.
Since q[2] is |1> in all terms, CZ(q[0], q[2]) acts like Z on q[0].
Wait! In the state after CNOT(q[1], q[2]), q[2] is 1 for all terms?
Let's recheck CNOT(q[1], q[2]) effect on 1/2 (|001> + |101> + |110> - |010>).
|001> -> q1=0, q2=1 -> |001>
|101> -> q1=0, q2=1 -> |101>
|110> -> q1=1, q2=0 -> |111>
|010> -> q1=1, q2=0 -> |011>
So yes, all terms have q2=1.
Then CZ(q0, q2) applies -1

## isqTrain/3441

- task_id: `isqTrain/3441`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `qft_based_arithmetic`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `5321`

### Prompt

Implement the following in isQ: QPE for the Rz(pi/2) rotation using 3 precision qubits in isQ.

Rz(pi/2)|1> = exp(-i*pi/4)|1>, so the phase is -pi/4.
theta = -1/8 mod 1 = 7/8.
Binary: 0.111 with 3 bits -> |111>.

Controlled operations:
- prec[k] controls Rz(pi/2)^(2^k)
- Rz(pi/2)^1 = Rz(pi/2), Rz(pi/2)^2 = Rz(pi), Rz(pi/2)^4 = Rz(2*pi) = I

Declare prec[3] and tgt[1]. Measure prec only.

### Chain-of-thought reasoning

Let me analyze this QPE circuit for Rz(π/2).

The goal is to implement QPE for Rz(π/2) on eigenstate |1⟩ with 3 precision qubits.

Key facts:
- Rz(π/2)|1⟩ = e^{-iπ/4}|1⟩, so phase φ = -π/4
- θ = -1/8 mod 1 = 7/8
- Binary representation of 7/8 = 0.111 (3 bits)

Wait, but The predicted output not |111⟩ with certainty. Let me look at the predicted output:
{|000>: 0.086418, |001>: 0.038582, |010>: 0.700824, |011>: 0.027729, |100>: 0.02063, |101>: 0.000816, |110>: 0.086418, |111>: 0.038582}

The dominant outcome is |010⟩ with probability 0.700824. That's interesting - this doesn't match |111⟩.

Let me reconsider. The issue is that Rz gates in isQ might have a different convention than expected. In many quantum computing frameworks, Rz(θ) = e^{-iθ/2}Z, not Rz(θ) = e^{-iθZ/2}.

Actually, let me reconsider the problem more carefully.

In isQ, Rz(θ, q) applies the rotation Rz(θ). The convention might be:
Rz(θ) = e^{-iθZ/2} = [[e^{-iθ/2}, 0], [0, e^{iθ/2}]]

Or it might be:
Rz(θ) = [[1, 0], [0, e^{iθ}]]

Let me check: if Rz(π/2) = [[1, 0], [0, e^{iπ/2}]] = [[1, 0], [0, i]], then:
Rz(π/2)|1⟩ = i|1⟩

The phase would be i = e^{iπ/2}, so φ = π/2.

Then θ = φ/(2π) = 1/4.

With 3 precision qubits, we'd expect to measure 1/4 in binary = 0.010, which is |010⟩.

That matches the dominant outcome!

But wait, let me reconsider. In standard QPE, the controlled operations apply U^{2^k} where U has eigenvalue e^{2πiθ}. So if U|ψ⟩ = e^{2πiθ}|ψ⟩, QPE estimates θ.

If Rz(π/2) in isQ means [[1, 0], [0, e^{iπ/2}]], then applied to |1⟩:
Rz(π/2)|1⟩ = e^{iπ/2}|1⟩ = i|1⟩

So e^{2πiθ} = e^{iπ/2}, giving θ = 1/4.

With 3 precision qubits, θ = 1/4 = 0.010 in binary. So we should measure |010⟩. ✓

Now let me trace through the circuit:

1. Initial state: |000⟩|0⟩

2. X(tgt[0]): |000⟩|1⟩

3. H(prec[0]); H(prec[1]); H(prec[2]):
   (1/2√2)(|000⟩ + |001⟩ + |010⟩ + |011⟩ + |100⟩ + |101⟩ + |110⟩ + |111⟩)|1⟩

4. Controlled operations:
   - prec[0] controls Rz(π/2)^4 = Rz(2π): This is identity in the [[1,0],[0,e^{iθ}]] convention (e^{i2π} = 1). Skip.
   - prec[1] controls Rz(π/2)^2 = Rz(π): This is [[1,0],[0,-1]] = Z.
   - prec[2] controls Rz(π/2)^1 = Rz(π/2).

Actually, wait. The problem statement says:
- prec[0] controls Rz(π/2)^4 = Rz(2π) = I: skip
- prec[1] controls Rz(π/2)^2 = Rz(π) = Z
- prec[2] controls Rz(π/2)^1 = Rz(π/2)

Hmm, but in the isQ code, the controlled Rz uses a specific call: `ctrl Rz(1.570
