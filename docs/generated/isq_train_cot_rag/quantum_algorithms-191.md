# ISQ training COT RAG corpus: quantum_algorithms shard 191

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqQA/quantum_algorithms/112_optimization_variant

- task_id: `isqQA/quantum_algorithms/112_optimization_variant`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `optimization_variant`, `algorithm`, `逆QFT电路`
- source: `qa_pipeline`
- dataset_index: `1115`

### Prompt

在实现量子算法（如Shor算法的相位估计）时，逆量子傅里叶变换是不可或缺的环节。然而，标准的逆QFT电路包含了大量的多控相位旋转门和SWAP门，导致电路深度过深且量子门数量庞大。请问在硬件受限的NISQ（含噪声中等规模量子）时代，逆QFT电路有哪些重要的优化变体？能否详细解释“无SWAP逆QFT变体”与“近似逆QFT变体”的核心原理，并使用isQ语言编写一个结合这两种优化策略的四量子位近似无SWAP逆QFT代码示例？

### Reference answer

标准逆量子傅里叶变换电路在理论上非常优美，但在真实的物理硬件上却面临着极大的部署挑战。随着量子比特数量的增加，受控相位旋转门的连线复杂度呈二次增长，且远距离量子比特间的SWAP操作会带来极高的串扰和退相干误差。为了在NISQ时代高效运行需要逆QFT的算法，研究者们提出了两个极其重要的优化变体：

1. 无SWAP的逆QFT变体
在标准的QFT电路中，由于量子态的顺序在变换过程中会被反转，因此电路末端需要加入O(N)个SWAP门来恢复比特顺序。同理，在标准逆QFT电路的开头，也需要先进行SWAP操作。然而，SWAP门通常需要分解为3个CNOT门，开销极大。无SWAP变体的核心思想是直接省略掉这些SWAP门。在物理层面，这相当于让量子态保持倒序；在测量阶段，我们只需在经典计算机上将读取到的第i个经典比特映射为结果的第N-1-i位即可。这种做法完全消除了SWAP门的物理开销，大幅降低了电路深度。

2. 近似逆QFT变体
逆QFT中包含大量的受控相位旋转门（如CRk，角度为π/2^{k-1}）。当k较大时，旋转角度极小。由于任何物理量子门都存在固有误差，且在容错量子计算中，较小角度的门需要极深的Clifford+T门分解，因此实施这些微小角度旋转不仅资源消耗大，且引入的物理误差往往超过了门本身的数学贡献。近似变体通过设定一个截断阈值m，直接移除所有k>m的受控旋转门。研究表明，当m=log2(N)+常数时，近似逆QFT带来的保真度损耗在可控范围内，同时将电路的连线复杂度从O(N^2)降低至O(N log N)。

下面使用isQ语言，结合上述两种思想，编写一个截断阈值m=2（即只保留CR2和CR3，丢弃CR4及以上）、包含4个量子比特的无SWAP近似逆QFT电路。注意代码直接从高位比特开始逆变换，且无需任何SWAP门。

import std;

qbit q[4];

procedure main() {
    // 假设q处于某种已应用了QFT的任意状态，为了测试我们这里简单初始化一个叠加态
    for i in 0:4 {
        H(q[i]);
    }

    // 无SWAP的近似逆QFT电路实现
    // 原本需要从 i = 3 递减到 0。此处使用等价展开写法，避免isQ不支持的逆向循环。

    // 第1步：处理最高位 i=3
    H(q[3]);
    // 近似截断处理：只保留距离在m以内的受控旋转（此处m=2，即保留距离1和距离2的控制位）
    // 对应原相位 k=2 (距离1)，旋转角度为 -pi/2
    ctrl @[q[2]] Rz(-1.5707963, q[3]);
    // 对应原相位 k=3 (距离2)，旋转角度为 -pi/4
    ctrl @[q[1]] Rz(-0.7853981, q[3]);
    // 对应原相位 k=4 (距离3)，因为截断阈值 m=2 直接丢弃，不执行 ctrl @[q[0]] Rz

    // 第2步：处理次高位 i=2
    H(q[2]);
    ctrl @[q[1]] Rz(-1.5707963, q[2]);
    ctrl @[q[0]] Rz(-0.7853981, q[2]);

    // 第3步：处理位 i=1
    H(q[1]);
    ctrl @[q[0]] Rz(-1.5707963, q[1]);

    // 第4步：处理最低位 i=0
    H(q[0]);

    // 无需SWAP操作，直接测量。
    // 注意：由于省略了SWAP门，如果原算法最后需要提取整数结果，
    // 需要在经典后处理时将输出的比特数组进行逆序翻转。
    for i in 0:4 {
        M(q[i]);
    }
}

## isqTrain/3579

- task_id: `isqTrain/3579`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `entanglement`, `ancilla_usage`, `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1980`

### Prompt

Fix the bug in the following isQ program.

Bug description: Wrong CNOT direction

The program should 3-qubit bit-flip code: error on q[2], correction.

### Chain-of-thought reasoning

The buggy code has:

The corrected version:

The bug is in the first CNOT gate during encoding. The direction is wrong: `CNOT(q[1], q[0])` should be `CNOT(q[0], q[1])`.

Let me trace through the corrected circuit:

1. Initial state: |000>|00> (q[0], q[1], q[2], anc[0], anc[1])

2. CNOT(q[0], q[1]): control=q[0], target=q[1]. Since q[0] is |0>, no flip. State: |000>|00>

Wait, but the comment says "Encode |0> -> |000>". If we start with |0>|0>|0>, then CNOT(q[0], q[1]) does nothing since control is |0>. Same for CNOT(q[0], q[2]). So the encoding step does nothing when starting from |000>.

Then X(q[2]) flips q[2]: |001>|00>

Syndrome measurement:
- CNOT(q[0], anc[0]): control=q[0]=|0>, no flip. State: |001>|00>
- CNOT(q[1], anc[0]): control=q[1]=|0>, no flip. State: |001>|00>
- CNOT(q[1], anc[1]): control=q[1]=|0>, no flip. State: |001>|00>
- CNOT(q[2], anc[1]): control=q[2]=|1>, flips anc[1]. State: |001>|01>

So syndrome is anc[0]=0, anc[1]=1, i.e., syndrome is 01.

Then `nctrl ctrl X(anc[0], anc[1], q[2])`: This applies X to q[2] when anc[0]=0 (negated) and anc[1]=1. So with anc[0]=0 and anc[1]=1, the condition is met. X is applied to q[2], flipping it back. State: |000>|01>

Final measurement: |000> with probability 1. ✓

Now with the buggy code:
CNOT(q[1], q[0]) with q[1]=|0>: no flip. State: |000>
CNOT(q[0], q[2]) with q[0]=|0>: no flip. State: |000>

Hmm, in this specific case starting from |000>, both versions produce the same result because both CNOTs have control in |0> state.

Wait, but the buggy version's first CNOT is CNOT(q[1], q[0]) - control is q[1] which is |0>, target is q[0]. Since control is |0>, nothing happens. Same as CNOT(q[0], q[1]) when control q[0] is |0>.

So actually for the |000> input, both versions give the same result. The bug would manifest with different initial states.

Actually, let me re-read the problem. The comment says "Encode |0> -> |000>". The 3-qubit bit-flip code encodes a logical qubit into 3 physical qubits. If the data qubit is q[0], starting in state |0>:
- CNOT(q[0], q[1]): copies q[0] to q[1]. |000>
- CNOT(q[0], q[2]): copies q[0] to q[2]. |000>

If instead we have CNOT(q[1], q[0]):
- CNOT(q[1], q[0]): control=q[1]=|0>, no flip. Still |000>
- CNOT(q[0], q[2]): still |000>

For |0> input, it still works. But for |1> input:
- Correct: CNOT(q[0], q[1]) → |110>, CNOT(q[0], q[2]) → |111>
- Buggy: CNOT(q[1], q[0]) → |110>, CNOT(q[0], q[2]) → |111>

Wait, both give the same result for |1> too because after the first CNOT, q[0] and q[1] are the same.

Hmm, actually for input |+>|0>|0> = (|0>+|1>)/√2 |0>|0>:
- Correct: CNOT(q[0], q[1]) → (|00>+|11>)/√2 |0>, CNOT

## isqExpand/algo/66

- task_id: `isqExpand/algo/66`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `qaoa`, `maxcut`, `zz_interaction`, `cost_layer`, `mixer_layer`
- source: `isq_expansion`
- dataset_index: `1697`

### Prompt

实现以下量子计算任务（使用isQ）：implements one round of QAOA for a 2-qubit MaxCut problem on a single edge. The circuit should:
1. Initialize both qubits in |+> using Hadamard gates
2. Apply the ZZ cost layer with gamma=pi/6, decomposed as CNOT(q[0],q[1]) - Rz(pi/3, q[1]) - CNOT(q[0],q[1])
3. Apply the mixer layer: Rx(2*pi/3, q[0]) and Rx(2*pi/3, q[1])
4. Measure both qubits

### Chain-of-thought reasoning

## Reasoning
Goal: One QAOA round for 2-qubit MaxCut.

QAOA structure:
1. H on both: |+>|+> = (1/2)(|00>+|01>+|10>+|11>)
2. Cost layer exp(-i*gamma*Z_0*Z_1) with gamma=pi/6:
   Decomposition: CNOT(0,1) - Rz(2*gamma=pi/3, q[1]) - CNOT(0,1)
   This applies phase e^{-i*gamma} to same-parity states and e^{+i*gamma} to different-parity states
3. Mixer layer exp(-i*beta*X_j) with beta=pi/3:
   Rx(2*beta=2pi/3) on each qubit

The ZZ interaction adds phase e^{-i*pi/6} to |00>,|11> and e^{+i*pi/6} to |01>,|10>.
After the Rx mixer, interference favors cut states |01> and |10>.

Numerical result: P(00)=P(11)=0.0625, P(01)=P(10)=0.4375.
This demonstrates QAOA concentrating probability on the optimal MaxCut solution.

## isqTrain/694

- task_id: `isqTrain/694`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3146`

### Prompt

I need an isQ program to implements the half_full_adder pattern. Include explicit identity operations in the circuit (X-X pair before M(q[3])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a full adder computing sum = a ⊕ b ⊕ c_in and carry_out = majority(a, b, c_in) with inputs a=1, b=1, c_in=1.
2. **Qubits**: 5 qubits (q[0..4]); q[3] (sum) and q[4] (carry_out) are measured, yielding 2-bit output.
3. **Initialization**: X(q[0]), X(q[1]), X(q[2]) set inputs to |111⟩ → state |11100⟩.
4. **Sum via CNOTs**: Three CNOTs with q[3] as target compute XOR: CNOT(q[0],q[3]) → |11110⟩, CNOT(q[1],q[3]) → |11100⟩, CNOT(q[2],q[3]) → |11110⟩. Sum q[3] = 1⊕1⊕1 = 1.
5. **Carry via Toffoli**: Three Toffoli gates on q[4] count pairs: Toffoli(q[0],q[1],q[4]) → |11111⟩, Toffoli(q[0],q[2],q[4]) → |11110⟩, Toffoli(q[1],q[2],q[4]) → |11111⟩. Odd number of majority terms → carry_out q[4] = 1.
6. **Identity X-X pair**: X(q[3]) followed by X(q[3]) is a no-op (XX = I), leaving |11111⟩ unchanged—demonstrating gate cancellation awareness.
7. **Measurement**: M(q[3])=1, M(q[4])=1 → bitstring |11⟩ with probability 1.0.

## isqExpand/algo/25

- task_id: `isqExpand/algo/25`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `hhl`, `linear_systems`, `qpe`, `eigenvalue_inversion`
- source: `qa_pipeline`
- dataset_index: `1261`

### Prompt

HHL算法的基本原理是什么？它如何利用量子计算来求解线性方程组 Ax=b？请详细说明算法的主要步骤。

### Chain-of-thought reasoning

## 推理
目标：从原理层面解释HHL算法的完整流程。

分析路线：
1. 明确问题：求解 Ax=b，A 是厄米矩阵
2. 核心洞察：利用谱分解，|x> = Σ (b_j/λ_j)|u_j>，需要将 1/λ 编码到振幅
3. 四步流程：QPE提取特征值 → 受控旋转将 c/λ 编码到辅助qubit振幅 → 逆QPE解纠缠时钟寄存器 → 后选择测量得到 |x>
4. 复杂度优势来自 QPE 只需 O(log N) 个 qubit 表示特征值
5. 限制条件：矩阵需稀疏、条件数不能太大

### Reference answer

## HHL算法原理

### 问题背景
HHL（Harrow-Hassidim-Lloyd）算法用于求解线性方程组 A|x>=|b>，其中 A 是 N×N 的厄米矩阵。经典方法（如共轭梯度法）的复杂度为 O(N)，而 HHL 在满足特定条件时可实现指数级加速，复杂度为 O(poly(log N))。

### 核心思路
设 A 的谱分解为 A = Σ λ_j |u_j><u_j|，将 |b> 分解到特征基上：|b> = Σ b_j |u_j>。
那么 |x> = A^{-1}|b> = Σ (b_j / λ_j) |u_j>。
关键在于将 1/λ_j 编码到量子态的振幅中。

### 四个主要步骤

**步骤1：量子相位估计（QPE）**
利用酉算子 U = e^{iAt}，通过 QPE 将特征值 λ_j 的近似值写入时钟寄存器：
|b>|0> → Σ b_j |u_j>|λ̃_j>

**步骤2：受控旋转**
在辅助量子比特上执行受控 Ry 旋转，角度为 θ = 2·arcsin(c/λ̃_j)：
|λ̃_j>|0> → |λ̃_j>(√(1-c²/λ̃_j²)|0> + c/λ̃_j |1>)

**步骤3：逆QPE**
对时钟寄存器执行 QPE 的逆操作，将其恢复为 |0>：
Σ b_j |u_j>|0>(√(1-c²/λ_j²)|0> + c/λ_j |1>)

**步骤4：后选择测量**
测量辅助比特，若得到 |1>，则输出寄存器坍缩为：
Σ (c·b_j/λ_j) |u_j> ∝ |x>

### 复杂度
算法的复杂度为 O(log(N)·s²·κ²/ε)，其中 s 是稀疏度，κ 是条件数，ε 是精度。条件数 κ 越大，所需资源越多。

### isQ中的实现框架
```isq
import std;
import qft;
// 1. 制备 |b> 态
// 2. QPE: H(clock), ctrl-U^(2^k), QFT_inv
// 3. 受控旋转: 根据 clock 值执行 Ry
// 4. 逆QPE
// 5. 测量辅助比特
```

## isqTrain/2850

- task_id: `isqTrain/2850`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `isq_syntax_multi_register`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `500`

### Prompt

Fix the bug in this quantum program:

```isq
import std;
qbit q[2];
// two-qubit state using H+CZ
procedure main() {
    // H(q[0]); // BUG: missing Hadamard
    H(q[1]);
    CZ(q[0], q[1]);
    M(q[0]);
    M(q[1]);
}

```

### Chain-of-thought reasoning

## Bug Analysis

**Bug:** `H(q[0])` is commented out, leaving q[0] in |0⟩ instead of creating superposition.

**Effect:** Without H(q[0]), the state after H(q[1]) is |0⟩⊗|+⟩ = (|00⟩+|01⟩)/√2. CZ does nothing (q[0]=|0⟩), yielding only |00⟩ and |01⟩ at 50% each — not the expected uniform distribution.

**Fix:** Uncomment `H(q[0])` to restore superposition on both qubits.

**Corrected state evolution:**
1. |00⟩ → H(q[0]) → (|00⟩+|10⟩)/√2
2. → H(q[1]) → (|00⟩+|01⟩+|10⟩+|11⟩)/2
3. → CZ(q[0],q[1]) → (|00⟩+|01⟩+|10⟩−|11⟩)/2
4. Measurement: each of {|00⟩,|01⟩,|10⟩,|11⟩} has probability 0.25 ✓

(The CZ phase on |11⟩ doesn't affect computational-basis probabilities, so all four outcomes remain equally likely.)

## isqTrain/3028

- task_id: `isqTrain/3028`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `663`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
qbit q[4];
procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
    X(q[2]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Gate sequence**: H(q[0]), CNOT(q[0], q[1]), CNOT(q[1], q[2]), CNOT(q[2], q[3]), X(q[2]).
2. **State evolution**:
   - Start with |0000>.
   - H(q[0]) creates an equal superposition: (|0000> + |1000>)/√2.
   - CNOT(q[0], q[1]) propagates the entanglement: (|0000> + |1100>)/√2.
   - CNOT(q[1], q[2]) extends it: (|0000> + |1110>)/√2.
   - CNOT(q[2], q[3]) forms a 4-qubit GHZ state: (|0000> + |1111>)/√2.
   - X(q[2]) flips the 3rd qubit, yielding the final state: (|0010> + |1101>)/√2.
3. **Final state**: (|0010> + |1101>)/√2.
4. **Predicted probability distribution**: Measuring this state yields either |0010> or |1101>, each with a probability of 0.5. All other outcomes have 0 probability.

### Reference answer

{'predicted_probs': {'0010': 0.5, '1101': 0.5}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/758

- task_id: `isqTrain/758`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2025`

### Prompt

Create an isQ quantum circuit that implements a variant of the weighted_adder pattern using q[4] -> q[5]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a weighted adder variant that computes weighted sum bits from inputs using CNOT gates on an expanded 5-qubit register.

2. **Qubits**: 5 qubits total (q[0]-q[4]); q[2], q[3], q[4] are measured (3 bits).

3. **State evolution**:
   - Start: |00000⟩
   - X(q[0]), X(q[1]): |11000⟩ (set both inputs to |1⟩)
   - CNOT(q[0], q[2]): |11100⟩ (weight-1 contribution flips sum bit q[2])
   - CNOT(q[1], q[3]): |11110⟩ (weight-2 contribution flips sum bit q[3])

4. **Final state** |11110⟩: q[2]=1, q[3]=1, q[4]=0 → measurement bitstring |110⟩ with probability 1.0, since all operations are deterministic classical mappings in the computational basis.

## isqTrain/143

- task_id: `isqTrain/143`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1032`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[5];

procedure main() {
    H(q[0]); H(q[1]); H(q[2]); H(q[3]); H(q[4]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]); M(q[4]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Goal:** Generate a concise, precise step-by-step reasoning for a given isQ quantum program.
    *   **Input:** isQ program applying H gates to 5 qubits, followed by measurements.
    *   **Output Format:** "## Circuit Analysis" followed by reasoning (state evolution) and the predicted probability distribution. Must use Dirac notation.
    *   **Constraints:** Concise (3-8 lines), no code blocks, end with the predicted probability distribution.

2.  **Analyze the Circuit:**
    *   Initial state: $|00000\rangle$
    *   Operations: $H(q[0]) \otimes H(q[1]) \otimes H(q[2]) \otimes H(q[3]) \otimes H(q[4])$
    *   State evolution: Each $H|0\rangle$ becomes $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
    *   Combined state: $\frac{1}{\sqrt{2^5}} \sum_{x=0}^{31} |x\rangle = \frac{1}{4\sqrt{2}} \sum_{x=0}^{31} |x\rangle$.
    *   Probability: $|\frac{1}{4\sqrt{2}}|^2 = \frac{1}{32} = 0.03125$.
    *   Measurement outcomes: All 32 possible bitstrings from $|00000\rangle$ to $|11111\rangle$ with equal probability.

3.  **Draft the Reasoning:**
    *   *Step 1: Initial state.* The system of 5 qubits starts in the state $|00000\rangle$.
    *   *Step 2: Hadamard gates.* The circuit applies a Hadamard (H) gate to each of the 5 qubits.
    *   *Step 3: State evolution.* Each qubit transitions from $|0\rangle$ to the superposition state $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
    *   *Step 4: Final state.* The joint state of the system becomes an equal superposition of all $2^5=32$ possible basis states: $\frac{1}{\sqrt{32}} \sum_{i=0}^{31} |i\rangle$.
    *   *Step 5: Measurement.* Measuring all qubits collapses this superposition, yielding a uniform probability distribution over all 32 computational basis states.

4.  **Format the Output:**
    *   Ensure it starts with "## Circuit Analysis".
    *   Ensure it ends with the predicted probability distribution.

5.  **Refine Text:**
    ## Circuit Analysis
    1. The circuit initializes 5 qubits in the state $|00000\rangle$.
    2. A Hadamard (H) gate is applied to each qubit, transforming each $|0\rangle$ into $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
    3. The joint quantum state becomes an equal superposition of all 32 possible basis states: $\frac{1}{\sqrt{32}} \sum_{x=0}^{31} |x\rangle$.
    4. Upon measuring all qubits, the probability amplitude of each basis state is squared, yielding an equal probability for every outcome.
    
    Predicted probability distribution:
    {|00000>: 0.03125, |00001>: 0.03125, ..., |11111>: 0.03125} (all 32 states have 1/32 probability). Wait, standard format expected from the example should probably just list them or specify. The prompt says "Expected measurement probabilities: {|00000>: 0.03125...}". I will provide the full dictionary format if possible, or a summary. I will provide the full dictionary as standard for these kinds of program evaluations. Let's write out the dictionary comprehensively as The implementation implies it's standard.
    Actually, writing all 32 is long. I'll write a compact form or the full form depending on standard length. The prompt shows the full dict in the expected. Let's just output it. Wait, rule: "End with the predicted probability distribution". I will list the distribution.
    Let's keep it compact: {|00000>: 0.03125, ..., |11111>: 0.03125} or list all 32. I'll list all 32 to be strictly matching the reference style.

    Let me double check the exact dict from prompt: `{|000

### Reference answer

{'predicted_probs': {'0': 0.03125000000000001, '1': 0.03125000000000001, '2': 0.03125000000000001, '3': 0.03125000000000001, '4': 0.03125000000000001, '5': 0.03125000000000001, '6': 0.03125000000000001, '7': 0.03125000000000001, '8': 0.03125000000000001, '9': 0.03125000000000001, '10': 0.03125000000000001, '11': 0.03125000000000001, '12': 0.03125000000000001, '13': 0.03125000000000001, '14': 0.03125000000000001, '15': 0.03125000000000001, '16': 0.03125000000000001, '17': 0.03125000000000001, '18': 0.03125000000000001, '19': 0.03125000000000001, '20': 0.03125000000000001, '21': 0.03125000000000001, '22': 0.03125000000000001, '23': 0.03125000000000001, '24': 0.03125000000000001, '25': 0.03125000000000001, '26': 0.03125000000000001, '27': 0.03125000000000001, '28': 0.03125000000000001, '29': 0.03125000000000001, '30': 0.03125000000000001, '31': 0.03125000000000001}, 'explanation': 'Parametric variant of isqHumanEval/50. Dimension: predict probabilities for reference circuit.'}

## isqTrain/1257

- task_id: `isqTrain/1257`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `ancilla_usage`, `entanglement`, `isq_syntax_arrays`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `1934`

### Prompt

用isQ实现implements the error_correction_syndrome pattern with a different measurement ordering (reversed measurement order for syndrome). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement 3-qubit bit-flip code syndrome detection with reversed measurement order (syndrome[1] measured first, then syndrome[0]).

2. **Qubits**: 3 data qubits + 2 syndrome qubits; only syndrome[0] and syndrome[1] are measured.

3. **State evolution**:
   - Start: |000⟩_data|00⟩_syndrome
   - X(data[0]): |100⟩|00⟩
   - CNOT(data[0],data[1]); CNOT(data[0],data[2]): |111⟩|00⟩ (logical |1L⟩ = |111⟩)
   - X(data[1]) error: |101⟩|00⟩
   - CNOT(data[0],syndrome[0]); CNOT(data[1],syndrome[0]): syndrome[0] = 1⊕0 = 1 → |101⟩|10⟩
   - CNOT(data[1],syndrome[1]); CNOT(data[2],syndrome[1]): syndrome[1] = 0⊕1 = 1 → |101⟩|11⟩

4. **Probabilities**: Syndrome qubits are in state |11⟩. With reversed measurement M(syndrome[1]) then M(syndrome[0]), syndrome[1]=1 is the higher bit and syndrome[0]=1 is the lower bit, giving bitstring "11". Thus P(|11⟩) = 1.0.
