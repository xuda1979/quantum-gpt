# ISQ training COT RAG corpus: quantum_algorithms shard 143

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqQA/quantum_algorithms/120_application_scenario

- task_id: `isqQA/quantum_algorithms/120_application_scenario`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `application_scenario`, `algorithm`, `量子计数算法`
- source: `qa_pipeline`
- dataset_index: `3334`

### Prompt

量子计数算法在解决复杂问题中扮演着什么角色？请详细探讨它在优化量子搜索、密码学分析及组合数学等领域的应用场景与未来前景，并使用isQ语言编写一段核心代码，展示如何利用量子相位估计提取无结构数据库中目标解的数量。

### Reference answer

<thought>
量子计数算法本质上是量子相位估计（QPE）与Grover算子的结合。Grover算子的本征相位与无结构数据库中解的数量直接相关（\(\sin^2(\theta/2) = M/N\)）。通过估计这个相位，我们就能推导出解的个数。在实际应用中，这具有极高的战略价值：首先，它是自适应Grover搜索的先决条件，因为Grover算法的迭代次数依赖于解的个数；其次，在组合数学中，它能以指数级加速估算满足特定约束的解空间大小（如NP问题中的解数量）；再者，在密码学中，它被用于评估哈希函数的抗碰撞强度或分析加密系统的弱点。下面我将组织这些思路，并编写符合要求的isQ代码。
</thought>

量子计数算法是量子计算领域中极为核心的中间件算法，它巧妙地将Grover旋转算子与量子相位估计（QPE）结合，通过分析Grover算子的本征相位来估算无结构数据库中目标解的数量。其在实际应用场景与未来前景方面具有不可替代的价值，主要体现在以下几个维度：

1. **自适应量子搜索的预处理**：Grover算法虽然能提供二次方级的加速，但其最优迭代次数严格要求依赖于目标解的个数。如果盲目迭代，极易导致概率震荡（过度旋转）。量子计数算法在此作为完美的预处理步骤，首先以高精度估算解的数量，从而指导后续Grover算法动态调整迭代周期，实现真正意义上的最优量子搜索。

2. **组合数学与NP问题解空间估算**：在经典的组合数学或#P问题（如计算满足特定布尔公式的赋值数量、图中独立集或匹配的数量）中，精确计数是极其困难的。量子计数允许我们在容许一定误差范围（\(\epsilon\)）的情况下，以远低于经典随机抽样的查询复杂度（\(O(1/\epsilon)\)级别）给出解数量的近似估计，为决策问题提供极其重要的概率参考。

3. **密码学分析与安全评估**：在对称密码学和哈希函数的安全性分析中，评估碰撞的概率或特定输出空间的覆盖密度是关键。量子计数算法可被用于估算密钥空间中满足某种弱特性的子集大小，帮助量化评估古典密码在量子环境下的抗攻击能力（如评估量子碰撞攻击的实际威胁）。

4. **量子化学与基态简并度计算**：在量子化学模拟中，寻找哈密顿量基态能量附近的简并度至关重要。量子计数可以扩展到化学基态空间，用于估计特定能量本征值对应的特征态数量。

**前景展望**：随着容错量子计算机的推进，量子计数将广泛应用于更复杂的量子机器学习（如评估数据聚类大小）和量子优化启发式算法中。它将成为连接底层量子硬件与高层组合优化应用的关键桥梁。

以下是使用isQ语言实现的量子计数核心代码片段。该代码演示了如何将Grover迭代转化为受控操作，并利用逆量子傅里叶变换提取解数量的相位信息：

```isq
import std;

// 定义针对2量子比特系统的Grover迭代算子 (此处以单位矩阵作为概念占位)
// 实际应用中，该矩阵应包含Oracle和Diffuser的复合操作
deriving gate grover_iter = [
  [1, 0, 0, 0],
  [0, 1, 0, 0],
  [0, 0, 1, 0],
  [0, 0, 0, 1]
];

qbit target[2]; // 存储待搜索的目标状态空间
qbit count[2];  // 用于量子相位估计的计数寄存器

procedure main() {
    // 初始化目标寄存器为均匀叠加态
    H(target[0]);
    H(target[1]);

    // 初始化计数寄存器为均匀叠加态
    H(count[0]);
    H(count[1]);

    // 相位估计：执行受控Grover迭代
    // count[0] 控制执行 2^0 = 1 次迭代
    ctrl @[count[0]] grover_iter(target);
    
    // count[1] 控制执行 2^1 = 2 次迭代
    ctrl @[count[1]] grover_iter(target);
    ctrl @[count[1]] grover_iter(target);

    // 对计数寄存器执行逆量子傅里叶变换
    // 交换位序并应用受控相位门
    H(count[1]);
    inv S(count[1]);
    CNOT(count[1], count[0]);
    H(count[0]);
    CNOT(count[1], count[0]);
    S(count[0]);
    CNOT(count[1], count[0]);

    // 测量计数寄存器，提取的相位即对应目标解的数量
    int r0 = M(count[0]);
    int r1 = M(count[1]);
}
```

## isqTrain/3597

- task_id: `isqTrain/3597`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `hamiltonian_simulation`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2576`

### Prompt

Fix the bug in the following isQ program.

Bug description: Wrong CNOT direction

The program should 3-qubit Ising, J=1.5 h=0.8, 2 steps from |010>.

### Chain-of-thought reasoning

## Bug Analysis

**What the bug is:** In Step 1, the first CNOT implementing the ZZ(0,1) interaction has reversed control/target: `CNOT(q[1], q[0])` instead of `CNOT(q[0], q[1])`. The ZZ gate template is `CNOT(c,t) → Rz(θ,t) → CNOT(c,t)`, so both CNOTs must share the same control and target. The buggy code pairs `CNOT(q[1],q[0])` with `CNOT(q[0],q[1])`, which does not implement ZZ.

**What the fix is:** Change the first line of Step 1 from `CNOT(q[1], q[0])` to `CNOT(q[0], q[1])`, matching Step 2 and the ZZ template.

**State evolution (corrected):**
1. Start |000⟩ → X(q[1]) → |010⟩
2. CNOT(q[0],q[1]): q[0]=0, no flip → |010⟩; Rz(0.6,q[1]) → phase on |010⟩; CNOT(q[0],q[1]) → |010⟩ ✓ ZZ(0,1) correct
3. CNOT(q[1],q[2]): q[1]=1, flips q[2] → |011⟩; Rz(0.6,q[2]) → phase; CNOT(q[1],q[2]) → |010⟩ ✓ ZZ(1,2) correct
4. Rx(0.32) on all qubits creates superposition from |010⟩
5. Step 2 repeats same operations, producing expected probabilities {|010⟩: 0.774, |011⟩: 0.075, |000⟩: 0.053, …}

## isqExpand/algo/100

- task_id: `isqExpand/algo/100`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `ancilla_usage`, `multi_controlled_logic`
- source: `isq_expansion_qa`
- dataset_index: `778`

### Prompt

什么是SWAP测试（Swap Test）？它如何用来比较两个量子态的相似度？请给出电路结构、数学推导，并说明为什么不需要完整的量子态层析就能估计内积。

### Chain-of-thought reasoning

## 推理
目标：解释SWAP测试的数学原理和应用。

关键：
1. P(0) = (1+|<psi|phi>|^2)/2 是核心公式
2. 电路：H -> CSWAP -> H -> Measure
3. 不需要层析，复杂度远低于完整重建
4. isQ中用CNOT+Toffoli分解Fredkin门

### Reference answer

## SWAP测试（Swap Test）

### 基本概念
SWAP测试是一种量子算法，用于估计两个量子态 |psi> 和 |phi> 之间的内积 |<psi|phi>|^2，而不需要对量子态进行完全层析。

### 电路结构
1. 一个辅助比特（ancilla）初始化为 |0>
2. n 个比特存储 |psi>，n 个比特存储 |phi>
3. 电路步骤：H(ancilla) -> 受控SWAP -> H(ancilla) -> 测量ancilla

### 数学推导
初始态：|0>|psi>|phi>
1. H on ancilla：(|0>+|1>)/sqrt(2) * |psi>|phi>
2. 受控SWAP：(|0>|psi>|phi> + |1>|phi>|psi>)/sqrt(2)
3. H on ancilla：|0>*(|psi>|phi>+|phi>|psi>)/2 + |1>*(|psi>|phi>-|phi>|psi>)/2
4. P(ancilla=0) = (1 + |<psi|phi>|^2) / 2

### 特殊情况
- |psi> = |phi>（完全相同）：P(0) = 1
- |psi> 正交 |phi>：P(0) = 1/2

### 为什么不需要层析
量子态层析需要 O(4^n) 次测量来重建完整密度矩阵，而SWAP测试只需 O(1/epsilon^2) 次来估计内积到精度 epsilon。它直接给出态之间的相似度度量。

### isQ实现注意
在isQ中，受控SWAP（Fredkin门）可以用 CNOT + Toffoli 分解：
```isq
// Controlled-SWAP(ancilla; a, b):
CNOT(b, a);
Toffoli(ancilla, a, b);
CNOT(b, a);
```

### 应用
- 量子机器学习中的核函数估计
- 量子指纹识别（通信复杂度的指数压缩）
- 变分算法中的态保真度检测

## isqTrain/4112

- task_id: `isqTrain/4112`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `400`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
qbit q[4];

procedure main() {
    X(q[0]);
    X(q[1]);
    X(q[2]);
    X(q[3]);

    H(q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 16.0, q[3], q[0]);
    H(q[1]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[3], q[1]);
    H(q[2]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[3], q[2]);
    H(q[3]);
    CNOT(q[0], q[3]);
    CNOT(q[3], q[0]);
    CNOT(q[0], q[3]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[1]);
    CNOT(q[1], q[2]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict measurement output of an isQ quantum circuit.
    *   Input: An isQ program with 4 qubits, X gates, H gates, controlled-Rz gates, and CNOTs (specifically swap-like sequences).
    *   Output: Circuit Analysis section starting with "## Circuit Analysis", explaining operations, step-by-step state evolution, final state, and predicted probability distribution.
    *   Constraint: ONLY the analysis, no code blocks, 3-8 lines for simple, up to 15 lines for complex. Concise and precise using Dirac notation.

2.  **Analyze the Circuit:**
    *   Initial state: |0000>
    *   `X(q[0..3])` -> State is |1111>.
    *   First block (QFT-like structure):
        *   `H(q[0])`: Applies to q[0].
        *   `ctrl Rz(pi/2, q[1], q[0])`
        *   `ctrl Rz(pi/4, q[2], q[0])`
        *   `ctrl Rz(pi/8, q[3], q[0])`
        *   `H(q[1])`: Applies to q[1].
        *   `ctrl Rz(pi/2, q[2], q[1])`
        *   `ctrl Rz(pi/4, q[3], q[1])`
        *   `H(q[2])`: Applies to q[2].
        *   `ctrl Rz(pi/2, q[3], q[2])`
        *   `H(q[3])`: Applies to q[3].
        This is exactly the Quantum Fourier Transform (QFT) on |1111> (which represents the integer 15).
        Wait, let's verify the QFT order and angles.
        Standard QFT for x:
        |x> -> (1/sqrt(N)) sum_y e^{2 pi i x y / N} |y>
        The QFT of |1111> (x=15) will be a specific state.
        Let's check the angles:
        `Rz(pi/2)` is phase shift pi/2.
        `Rz(pi/4)` is phase shift pi/4.
        Let's evaluate QFT|1111> without Swaps first.
        Actually, the gates apply rotations *conditional* on higher index qubits acting as controls?
        `ctrl Rz(..., q[1], q[0])`: q[1] is control, q[0] is target. This means if q[1] is |1>, q[0] gets a phase.
        Let's re-read carefully:
        
        This is exactly the QFT matrix! The target is the first qubit `q[0]`.
        Wait, in QFT, the first Hadamard is on `q[0]`. Then `q[1]` controls a rotation on `q[0]`.
        Let's check the standard QFT(q0, q1, q2, q3) structure.
        Usually: `H(q0)`, `CPhase(pi/2, q1->q0)`, `CPhase(pi/4, q2->q0)`, `CPhase(pi/8, q3->q0)`. This matches!
        Next: `H(q[1])`, `ctrl Rz(pi/2, q[2], q[1])`, `ctrl Rz(pi/4, q[3], q[1])`. Matches!
        Next: `H(q[2])`, `ctrl Rz(pi/2, q[3], q[2])`. Matches!
        Next: `H(q[3])`. Matches!
        So the first part of the circuit is exactly QFT(15).
        Since 15 = 1111 in binary, the QFT of |15> is a superposition with specific phases.
        Wait, QFT|15> = 1/4 * sum_{y=0}^{15} e^{i 2 pi 15 y / 16} |y>.
        Notice that 15/16 is close to 1.
        e^{i 2 pi 15 y / 16} = e

### Reference answer

Uniform distribution across 16 states

## isqTrain/4274

- task_id: `isqTrain/4274`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `270`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;
qbit q[3];

procedure my_z(qbit a) {
    Z(a);
} deriving gate

procedure main() {
    // Target eigenstate |1>
    X(q[2]);
    // Count registers
    H(q[0]); H(q[1]);
    
    // CU
    ctrl my_z(q[1], q[2]);
    
    // Inverse QFT on 2 qubits
    CNOT(q[0], q[1]); CNOT(q[1], q[0]); CNOT(q[0], q[1]); // SWAP
    
    H(q[1]);
    ctrl Rz(-pi/2.0, q[0], q[1]);
    H(q[0]);
    
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the request:**
    *   Task: output_prediction for an isQ program.
    *   Input: An isQ program applying QPE (Quantum Phase Estimation) for the $Z$ gate on the eigenstate $|1\rangle$, followed by an $X$ gate on `q[0]`.
    *   Constraint: Output ONLY the analysis starting with "## Circuit Analysis", no code blocks, strict conciseness (3-15 lines), end with the predicted probability distribution.
    *   Wait, the prompt says "Expected measurement probabilities: {|000>: 0.8535533905932738, |010>: 0.1464466094067261}". Let's check the number of qubits. The circuit has 3 qubits, but only `q[0]` and `q[1]` are measured (`M(q[0]); M(q[1]);`).
    *   Let's trace carefully:
        *   `q[2]` starts as $|0\rangle$, then `X(q[2])` makes it $|1\rangle$.
        *   `q[0]` and `q[1]` start as $|00\rangle$.
        *   `H(q[0]); H(q[1]);` -> $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)_{q0,q1} \otimes |1\rangle_{q2}$.
        *   `ctrl my_z(q[1], q[2])`: Wait, the syntax is `ctrl my_z(q[1], q[2])`. Wait, `my_z(a)` takes one qubit. `ctrl my_z(q[1], q[2])` means `q[1]` is control, `q[2]` is target. Wait, isQ `ctrl Gate(ctrl, target)` or `ctrl @[ctrl] Gate(target)`? Let's assume `ctrl my_z(q[1], q[2])` means `q[1]` controls `my_z` on `q[2]`.
        *   Since it's only one controlled operation (not a power of 2), wait. Usually QPE for $Z$ would apply $CZ^{2^0}$ and $CZ^{2^1}$. But here, it's ONLY `ctrl my_z(q[1], q[2])`. Wait, where is the control on `q[0]`?
        *   Let's re-read the code:
            
            There is NO controlled operation on `q[0]`.
        *   So the phase is kicked back only to `q[1]`.
        *   Initial: $|00\rangle_{q0,q1} |1\rangle_{q2}$
        *   After Hadamards: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle) |1\rangle$
        *   After `ctrl my_z(q[1], q[2])`:
            $|0\rangle_{q1}$ does nothing. $|1\rangle_{q1}$ applies $Z$ to $|1\rangle_{q2}$, which gives $-|1\rangle_{q2}$.
            State: $\frac{1}{2}(|00\rangle + |10\rangle) |1\rangle + \frac{1}{2}(-|01\rangle - |11\rangle) |1\rangle$
            = $\frac{1}{2}(|00\rangle - |01\rangle + |10\rangle - |11\rangle) |1\rangle$
            = $\frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)_{q1} \otimes \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)_{q0} \otimes |1\rangle_{q2}$
        *   Inverse QFT on 2 qubits:
            swap (three-CNOT decomposition)(q[0], q[1]) -> state is $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)_{q1} \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)_{q0}$
            $H(q[1])$ -> $|0\rangle_{q1}$
            $ctrl Rz(-\pi/2, q[0], q[1])$ -> applies $Rz(-\pi/2)$ to `q[1]

### Reference answer

{'predicted_probs': {'000': 0.853553, '010': 0.146447}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|000>) = 0.8536, P(|010>) = 0.1464.'}

## isqTrain/928

- task_id: `isqTrain/928`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5696`

### Prompt

Code this in isQ: implements the boolean_synthesis pattern but with a different initial state preparation (flip q[[0, 1]] -> q[5]).

### Chain-of-thought reasoning

Let me analyze this circuit carefully.

The goal is to implement a boolean_synthesis pattern that computes a majority function or similar boolean expression, with the initial state preparation changed to flip q[5] instead of q[0] and q[1].

Let me trace through the circuit:

**Initial State:** |000000⟩

**After X(q[5]):**
State becomes |000001⟩ (q[5] = 1)

Now let me trace the boolean logic gates:

**q[3] = a AND b = q[0] AND q[1]:**
ctrl ctrl X(q[0], q[1], q[3])
Since q[0] = 0 and q[1] = 0, this doesn't flip q[3].
State: |000001⟩

**q[4] = a AND c = q[0] AND q[2]:**
ctrl ctrl X(q[0], q[2], q[4])
Since q[0] = 0, this doesn't flip q[4].
State: |000001⟩

**CNOT(q[3], q[5]):**
q[3] = 0, so q[5] stays as is.
State: |000001⟩

**CNOT(q[4], q[5]):**
q[4] = 0, so q[5] stays as is.
State: |000001⟩

**ctrl ctrl X(q[1], q[2], q[5]):**
q[1] = 0, q[2] = 0, so this doesn't flip q[5].
State: |000001⟩

Wait, so q[5] = 1, and we measure q[5]. The result should be |1⟩ with probability 1.0.

Hmm, but the comment says "MAJ(1,1,0) = 1" which suggests the original inputs were a=1, b=1, c=0. But here with the flipped initial state (q[5] flipped instead of q[0] and q[1]), we have a=0, b=0, c=0, and q[5] starts at 1.

Let me re-examine:
- q[0] = a = 0
- q[1] = b = 0  
- q[2] = c = 0
- q[3] = scratch for a AND b
- q[4] = scratch for a AND c
- q[5] = initialized to 1 (the flip)

The computation:
- q[3] = a AND b = 0 AND 0 = 0
- q[4] = a AND c = 0 AND 0 = 0
- CNOT(q[3], q[5]): q[5] = q[5] XOR q[3] = 1 XOR 0 = 1
- CNOT(q[4], q[5]): q[5] = q[5] XOR q[4] = 1 XOR 0 = 1
- ctrl ctrl X(q[1], q[2], q[5]): q[5] = q[5] XOR (b AND c) = 1 XOR 0 = 1

So q[5] = 1 at the end.

But wait, the XOR approach for OR isn't exactly correct unless inclusion-exclusion is handled. The expression being computed is:
q[5]_final = q[5]_init XOR (a AND b) XOR (a AND c) XOR (b AND c)

With q[5]_init = 1, a=0, b=0, c=0:
q[5]_final = 1 XOR 0 XOR 0 XOR 0 = 1

The measurement of q[5] gives |1⟩ with probability 1.0. ✓

Actually wait - I need to think about this more carefully. The Toffoli gate (ctrl ctrl X) doesn't XOR - it flips the target when both controls are |1⟩. So:

Starting state: |000001⟩

After ctrl ctrl X(q[0], q[1], q[3]): controls q[0]=0, q[1]=0, so no flip. State: |000001⟩
After ctrl ctrl X(q[0], q[2], q[4]): controls q[0]=0, q[2]=0, so no flip. State: |000001⟩
After CNOT(q[3], q[5]): control q[3]=0, so no flip. State: |000001⟩
After CNOT(q[4], q[5]): control q[4]=0, so no flip. State: |000001⟩
After ctrl ctrl X(q[1], q[2], q

## isqTrain/3831

- task_id: `isqTrain/3831`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1560`

### Prompt

Implement a quantum circuit in isQ: Demonstrate phase kickback using controlled-T gate.
1. Put control qubit q[0] in |+> state
2. Prepare target q[1] in eigenstate |1>
3. Apply controlled-T
4. Apply H to control and measure both qubits.
Explanation: T|1> = e^{iπ/4}|1>, phase π/4 kicked back

### Chain-of-thought reasoning

## Reasoning
Goal: Demonstrate phase kickback where a controlled-T gate applies a relative phase to the control qubit.
Qubits: 2 (q[0] as control, q[1] as target). Both measured.
1. Initial state is |00>.
2. H(q[0]) creates |+0> = (|00> + |10>)/√2.
3. X(q[1]) changes target to |1>, yielding (|01> + |11>)/√2.
4. ctrl T(q[0], q[1]) applies T to q[1] if q[0] is |1>. Since T|1> = e^{iπ/4}|1>, the state becomes (|01> + e^{iπ/4}|11>)/√2.
5. H(q[0]) transforms the control qubit, resulting in [(1+e^{iπ/4})|01> + (1-e^{iπ/4})|11>]/2.
6. Measuring both qubits yields |01> with probability |1

## isqTrain/4103

- task_id: `isqTrain/4103`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `887`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;
qbit q[3];

procedure main() {
    X(q[0]);
    X(q[1]);

    H(q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    H(q[1]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    H(q[2]);
    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

Initial state: |000>

After X(q[0]) and X(q[1]): |110>

Now we apply the circuit. Let me think about what this circuit does.

H(q[0]): Applied to q[0] (which is |1>)
H|1⟩ = |−⟩ = (|0⟩ - |1⟩)/√2

So state becomes: (|010⟩ - |110⟩)/√2

Wait, let me be more careful. The qubits are q[0], q[1], q[2].

State after X(q[0]), X(q[1]): |110⟩ where q[0]=1, q[1]=1, q[2]=0.

Actually, let me denote the state as |q[2]q[1]q[0]⟩ or |q[0]q[1]q[2]⟩. Let me use |q[0],q[1],q[2]⟩.

After X(q[0]), X(q[1]): |1,1,0⟩

H(q[0]): |1⟩ → |−⟩ = (|0⟩ - |1⟩)/√2
State: (|0,1,0⟩ - |1,1,0⟩)/√2

ctrl Rz(π/2, q[1], q[0]): This is a controlled-Rz with q[1] as control and q[0] as target. Rz(π/2) applies phase e^{-iπ/4} to |0⟩ and e^{iπ/4} to |1⟩.

Wait, ctrl Rz(theta, control, target). Let me check the isQ syntax. Looking at the code:
`ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[1], q[0]);`

The Rz gate has theta and target. With ctrl modifier, the first qubit listed after theta becomes the control, and the Rz target becomes q[0].

Wait, actually looking at isQ syntax more carefully:
`ctrl Rz(theta, q[1], q[0])` - I think this means Rz is applied to q[0] controlled by q[1].

Actually, let me reconsider. In isQ, `ctrl Rz(theta, qubit)` would be a single-qubit Rz with a ctrl modifier. The ctrl modifier adds a control qubit. So `ctrl Rz(theta, q[1], q[0])` means: Rz(theta) on q[0] controlled by q[1].

Wait, actually that's also not clear. Let me look at the syntax reference:
"Control modifier: `ctrl @[c1, c2] Gate(target);`"

So the format might be: `ctrl Rz(theta, q[1], q[0])` where q[1] is the control (first qubit after theta) and q[0] is the target of Rz.

Hmm, but actually in the convenience form without @, the ctrl might just add one control. Let me re-read:

The function signature of Rz is `Rz(theta, q)`. With ctrl, it becomes `ctrl Rz(theta, control, target)` where control is inserted before the original arguments.

So `ctrl Rz(2.0*π/4, q[1], q[0])` means: controlled-Rz(π/2) on q[0], with q[1] as control.

OK so let me continue.

State after H(q[0]): (|0,1,0⟩ - |1,1,0⟩)/√2

ctrl Rz(π/2, q[1], q[0]): Apply Rz(π/2) to q[0] when q[1]=1.
Since q[1]=1 in both terms, this applies Rz(π/2) to q[0] in both terms.

Rz(π/2)|0⟩ = e^{-iπ/4}|0⟩
Rz(π/2)|1⟩ = e^{iπ/4}|1⟩

State: (e^{-iπ/4}|0,1,0⟩ - e^{iπ/4}|1,1,0⟩)/√2 = e^{-iπ/4}(|0,1,0⟩ - e^{iπ/2}|1,1,0⟩)/√2
= e^{-iπ/4}(|0,1,0⟩ - i|1,1,0⟩)/√2

ctrl Rz(π/4, q[2], q[0]): Apply Rz(π/4) to q[0] when q[2]=1.
Since q[

### Reference answer

Uniform distribution across 8 states

## isqExpand/algo/191

- task_id: `isqExpand/algo/191`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `QAOA`, `approximation_ratio`, `layer_depth`, `combinatorial_optimization`, `variational_quantum_algorithms`
- source: `qa_pipeline`
- dataset_index: `1353`

### Prompt

QAOA的近似比(approximation ratio)是什么概念？层数p如何影响解的质量？

### Chain-of-thought reasoning

首先分析问题的两个核心部分：近似比的定义和层数p的影响。关于近似比，它本质上是衡量量子算法输出解质量与经典最优解之间差距的度量，定义为期望成本与最优成本的比值。关于层数p的影响，需要从理论角度（p→∞时对应绝热演化，近似比趋于1）和实践角度（噪声、优化难度、线路深度限制）两方面分析。还需提及已知的理论结果，如p=1时MaxCut的0.6924近似比下界。最终综合这些要素构建完整的中文回答。

### Reference answer

近似比(approximation ratio)是衡量QAOA(Quantum Approximate Optimization Algorithm)解质量的核心指标，定义为算法所得期望目标函数值与最优解之比。具体而言，设最优解对应的目标函数值为C_max，QAOA在参数(γ,β)下测量的期望值为⟨C(γ,β)⟩，则近似比α = ⟨C(γ,β)⟩ / C_max，满足0 ≤ α ≤ 1。近似比越接近1，说明算法输出的解越接近最优解。

关于层数p对解质量的影响：

1. **表达能力递增**：QAOA的量子线路由p层组成，每层包含一个问题哈密顿量演化exp(-iγH_C)和一个混合哈密顿量演化exp(-iβH_B)。随着p增大，参数化量子线路的表达能力增强，能够覆盖更大的量子态空间，从而有可能更逼近最优解。

2. **理论保证**：Farhi等人证明，当p→∞时，QAOA可以通过连续量子演化精确逼近量子绝热演化过程，理论上能够以高概率找到最优解，即近似比趋于1。对于MaxCut问题，已有研究表明p=1时QAOA在某些图类上可达到0.6924的近似比保证。

3. **实际权衡**：虽然增大p理论上能提高解的质量，但层数增加也带来以下挑战：(a) 参数优化的难度增加，参数空间维度为2p，高维非凸优化容易陷入局部最优；(b) 量子线路深度增加，噪声影响累积，在NISQ设备上实际性能可能反而下降；(c) 线路执行时间和采样开销增大。

4. **经验观察**：在实际应用中，适度增加p（如从1到5-10）通常能显著提升近似比，但收益逐渐递减。对于特定问题实例，存在一个性价比最优的p值范围。实验表明，对于中等规模的组合优化问题，p=3到p=10通常能获得较好的近似比（如0.85以上）。

## isqTrain/805

- task_id: `isqTrain/805`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5308`

### Prompt

Create an isQ quantum circuit that implements the quantum_multiplier pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a 1×2 quantum multiplier with reversed measurement order (q[4] measured before q[3]).
2. **Qubits**: 5 qubits (q[0]=multiplier a=1, q[1]=b0=0, q[2]=b1=1, q[3]=p0, q[4]=p1); only q[4] and q[3] are measured.
3. **State evolution**:
   - Initial: |00000⟩
   - X(q[0]): |10000⟩ (a=1)
   - X(q[2]): |10100⟩ (b=10₂=2)
   - Toffoli(q[0],q[1],q[3]): |10100⟩ (p0 = 1∧0 = 0, q[3] stays |0⟩)
   - Toffoli(q[0],q[2],q[4]): |10110⟩ (p1 = 1∧1 = 1, q[4] flips to |1⟩)
4. **Measurement**: M(q[4]) first → MSB=1, M(q[3]) second → LSB=0, yielding bitstring |10⟩ with probability 1.0, since product 1×2=2=10₂.
