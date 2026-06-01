# ISQ training COT RAG corpus: quantum_algorithms shard 168

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/973

- task_id: `isqTrain/973`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `entanglement`, `hamiltonian_simulation`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `215`

### Prompt

Code this in isQ: implements the lie_trotter pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

The goal is to implement a Lie-Trotter evolution $e^{-itH}$ where $H = ZZ + XX$ with $t = \pi/8$, starting from $|10\rangle$, and with reversed measurement order.

**Initial state:** $|10\rangle$

**Step 1: $e^{-it \cdot ZZ}$ decomposition**

1. CNOT(q[0], q[1]): $|10\rangle \to |11\rangle$
2. Rz(2t, q[1]) with $2t = \pi/4$: This applies $e^{-i\pi/4 \cdot Z/2} = e^{-i\pi Z/8}$ to q[1]
   - $|11\rangle \to e^{-i\pi/8}|11\rangle$ (since Z on $|1\rangle$ gives $-|1\rangle$, so phase is $e^{i\pi/8}$... wait, let me be more careful)
   - Rz(θ) = $e^{-i\theta/2} \begin{pmatrix} 1 & 0 \\ 0 & e^{i\theta} \end{pmatrix}$
   - Actually, Rz(θ) = $\begin{pmatrix} e^{-i\theta/2} & 0 \\ 0 & e^{i\theta/2} \end{pmatrix}$
   - On $|1\rangle$: applies $e^{i\theta/2}$ where $\theta = \pi/4$, so $e^{i\pi/8}$
   - $|11\rangle \to e^{i\pi/8}|11\rangle$
3. CNOT(q[0], q[1]): $e^{i\pi/8}|11\rangle \to e^{i\pi/8}|10\rangle$

After Step 1: $e^{i\pi/8}|10\rangle$

**Step 2: $e^{-it \cdot XX}$ decomposition**

1. H(q[0]); H(q[1]):
   - $|10\rangle \to |-\rangle|+\rangle = \frac{1}{2}(|0\rangle - |1\rangle)(|0\rangle + |1\rangle)$
   
   Let me compute more carefully. After Step 1 we have $e^{i\pi/8}|10\rangle$ (global phase, ignore).
   
   H on q[0] ($|1\rangle$): $|1\rangle \to |-\rangle$
   H on q[1] ($|0\rangle$): $|0\rangle \to |+\rangle$
   
   State: $|-\rangle|+\rangle$

2. CNOT(q[0], q[1]): 
   $|-\rangle|+\rangle = \frac{1}{2}(|00\rangle + |01\rangle - |10\rangle - |11\rangle)$
   
   CNOT flips q[1] when q[0]=1:
   $\frac{1}{2}(|00\rangle + |01\rangle - |11\rangle - |10\rangle) = \frac{1}{2}(|00\rangle + |01\rangle - |10\rangle - |11\rangle)$
   
   Wait, that's the same... Let me redo. CNOT with q[0] control, q[1] target:
   - $|00\rangle \to |00\rangle$
   - $|01\rangle \to |01\rangle$
   - $|10\rangle \to |11\rangle$
   - $|11\rangle \to |10\rangle$
   
   So: $\frac{1}{2}(|00\rangle + |01\rangle - |11\rangle - |10\rangle)$

3. Rz($\pi/4$, q[1]):
   Applied to q[1], phase $e^{i\pi/8}$ for $|1\rangle$ component of q[1].
   
   $\frac{1}{2}(|00\rangle + |01\rangle - e^{i\pi/8}|11\rangle - e^{i\pi/8}|10\rangle)$
   
   $= \frac{1}{2}(|00\rangle + |01\rangle - e^{i\pi/8}(|10\rangle + |11\rangle))$

4. CNOT(q[0], q[1]):
   $\frac{1}{2}(|00\rangle + |01\rangle - e^{i\pi/8}(|11\rangle + |10\rangle))$
   
   Same swap for the |10⟩,|11⟩ pair:

## isqTrain/2072

- task_id: `isqTrain/2072`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3173`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[2];
procedure main() {
    H(q[0]); H(q[1]);
    CNOT(q[0], q[1]);
    Rz(-0.78539816339745, q[1]);
    CNOT(q[0], q[1]);
    Rx(0.78539816339745, q[0]);
    Rx(0.78539816339745, q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants a step-by-step analysis of a 2-qubit isQ quantum circuit, ending with the predicted probability distribution of measurement outcomes. the predicted output format is strictly defined (starts with "## Circuit Analysis", specific line limits, Dirac notation).

2.  **Analyze the Circuit**:
    *   Initialization: $|00\rangle$
    *   `H(q[0]); H(q[1]);` -> $H \otimes H |00\rangle = |++\rangle = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$
    *   `CNOT(q[0], q[1]);` -> CNOT(0,1) $|++\rangle = \frac{1}{2}(|00\rangle + |11\rangle + |10\rangle + |01\rangle) = |++\rangle$ (Wait, CNOT on $|++\rangle$ is actually $|++\rangle$. Let's check: $CNOT \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) = \frac{1}{2}(|00\rangle + |01\rangle + |11\rangle + |10\rangle) = |++\rangle$. Yes, CNOT leaves $|++\rangle$ unchanged).
    *   `Rz(-0.78539816339745, q[1]);` -> $-\pi/4$ on q[1]. $R_z(\theta) = e^{-i\theta/2}|0\rangle\langle 0| + e^{i\theta/2}|1\rangle\langle 1|$.
        State before: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
        State after Rz on q[1]: $\frac{1}{2}(|00\rangle + e^{i\pi/8}|01\rangle + |10\rangle + e^{i\pi/8}|11\rangle) = \frac{1}{2}(|0\rangle + |1\rangle) \otimes (|0\rangle + e^{i\pi/8}|1\rangle)$? No, wait.
        Let's recalculate carefully. $-0.785398...$ is $-\pi/4$.
        So $R_z(-\pi/4) |0\rangle = e^{i\pi/8}|0\rangle$, $R_z(-\pi/4) |1\rangle = e^{-i\pi/8}|1\rangle$.
        Actually, let's factor out global phase. Applying Rz to q[1]:
        $\frac{1}{2} (e^{i\pi/8}|00\rangle + e^{-i\pi/8}|01\rangle + e^{i\pi/8}|10\rangle + e^{-i\pi/8}|11\rangle)$
        $= \frac{1}{2} e^{i\pi/8} (|00\rangle + |10\rangle + e^{-i\pi/4}|01\rangle + e^{-i\pi/4}|11\rangle)$
        $= \frac{1}{2} e^{i\pi/8} (|0\rangle + |1\rangle)_0 \otimes (|0\rangle + e^{-i\pi/4}|1\rangle)_1$
    *   `CNOT(q[0], q[1]);` -> Apply CNOT to this state.
        Since q[1] is $|0\rangle + e^{-i\pi/4}|1\rangle$ and q[0] is $|+\rangle$, let's apply CNOT(0,1):
        CNOT($|0\rangle(|0\rangle+e^{-i\pi/4}|1\rangle)$) = $|0\rangle(|0\rangle+e^{-i\pi/4}|1\rangle)$
        CNOT($|1\rangle(|0\rangle+e^{-i\pi/4}|1\rangle)$) = $|1\rangle(e^{-i\pi/4}|0\rangle+|1\rangle)$
        Wait, no. Target is q[1]. Control is q[0].
        So it acts on q[1].
        State is $\frac{1}{2} e^{i\pi/8} [ |0\rangle_0 (|0\rangle_1 + e^{-i\pi/4}|1

### Reference answer

{'predicted_probs': {'00': 0.0732, '01': 0.4268, '10': 0.4268, '11': 0.0732}, 'explanation': 'QAOA p=1 for MaxCut on 2-node graph with gamma=pi/4, beta=pi/8.'}

## isqQA/quantum_algorithms/117_step_by_step

- task_id: `isqQA/quantum_algorithms/117_step_by_step`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `step_by_step`, `algorithm`, `振幅放大原理`
- source: `qa_pipeline`
- dataset_index: `5044`

### Prompt

请以两量子比特系统寻找目标态 |11⟩ 为例，分步讲解振幅放大（Amplitude Amplification）的核心原理。要求从最初始的量子态开始，一步步手动追踪并展示量子态的概率幅是如何通过“相位反转”和“关于均值的反转”发生变化的。最后，请使用isQ语言编写完整的代码来验证这个两量子比特的振幅放大过程。

### Reference answer

<think>
该问题的推理思路主要分为数学状态追踪与代码逻辑映射两部分。

首先，在数学推导上：系统从全0态出发，通过阿达马门生成四个基态均分概率幅（均为1/2）的均匀叠加态。接着，引入Oracle对目标态|11⟩执行“相位反转”，将其幅值变为-1/2，非目标态不变。随后，计算当前幅值的算术平均值（此例中恰好为0），并应用扩散算子进行“关于均值的反转”。利用公式计算可知，反转后非目标态幅值变为-1/2，而目标态幅值恢复为1/2。这体现了量子振幅放大的几何旋转特性。

其次，在代码映射上：将理论步骤转化为基础量子门组合。利用H门构建初始叠加，通过控制Z门（CZ）等效实现目标态的相位翻转。扩散算子则利用H门和X门将“关于均值反转”转化为关于|00⟩的相位反转操作，最后添加测量语句以验证输出概率。
</think>

<thought>让我们一步步拆解振幅放大的数学过程，然后再映射到 isQ 代码实现中。

1. **初始态准备**：
   初始态为 |00⟩。对两个量子比特应用 Hadamard 门，使其进入均匀叠加态。
   |ψ⟩ = H|0⟩ ⊗ H|0⟩ = (|00⟩ + |01⟩ + |10⟩ + |11⟩) / 2
   此时各基态的振幅均为 1/2。
   振幅向量：[1/2, 1/2, 1/2, 1/2]

2. **Oracle 作用（相位反转）**：
   假设我们的目标态是 |11⟩。Oracle $U_f$ 的作用是识别目标态并将其相位翻转（乘以 -1），非目标态保持不变。
   在两比特系统中，作用于 |11⟩ 的相位反转门等效于控制相位门 CZ。
   新的振幅向量：[1/2, 1/2, 1/2, -1/2]

3. **扩散算子作用（关于均值的反转）**：
   扩散算子 $D = 2|ψ⟩⟨ψ| - I$ 的作用是将各个态的振幅关于所有振幅的平均值进行反转。
   首先计算当前振幅的平均值 (μ)：
   μ = (1/2 + 1/2 + 1/2 - 1/2) / 4 = 1/4
   然后对每个振幅 $A_i$ 进行反转操作，新的振幅 $A_i' = 2μ - A_i$：
   - |00⟩ 的振幅：2(1/4) - 1/2 = 0
   - |01⟩ 的振幅：2(1/4) - 1/2 = 0
   - |10⟩ 的振幅：2(1/4) - 1/2 = 0
   - |11⟩ 的振幅：2(1/4) - (-1/2) = 1/2 + 1/2 = 1
   经过一次完整的 Grover 迭代，目标态 |11⟩ 的概率幅被放大到了 1（即 100% 概率），非目标态振幅变为 0。

4. **isQ 代码构建**：
   - 引入标准库 `import std;`
   - 声明两个全局量子比特 `qbit q[2];`
   - 初始化叠加态：`H(q[0]); H(q[1]);`
   - Oracle：`CZ(q[0], q[1]);`
   - 扩散算子：根据公式 $H^{⊗n} (2|0⟩⟨0| - I) H^{⊗n}$。在两量子比特下，$2|00⟩⟨00| - I$ 等效于对 |00⟩ 翻转相位，可以通过 X门、CZ门 和 X门 组合实现。
   所以扩散算子步骤为：H门 -> X门 -> CZ(q[0], q[1]) -> X门 -> H门。
   - 最后测量。</thought>

要深刻理解振幅放大原理，最直观的方法就是通过两量子比特系统进行手动追踪。我们将目标设为寻找并放大 |11⟩ 态的概率幅。整个算法过程可以拆解为三个核心步骤：

**第一步：初始化均匀叠加态**
我们从初始态 |00⟩ 开始。为了探索所有可能的状态，我们对两个量子比特分别应用 Hadamard (H) 门。H 门会将 |0⟩ 变为 (|0⟩ + |1⟩)/√2。因此，两量子比特的系统状态变为：
|ψ⟩ = (|00⟩ + |01⟩ + |10⟩ + |11⟩) / 2
此时，我们记录下四个基态的概率幅（振幅）均为 1/2。
振幅向量 = [1/2, 1/2, 1/2, 1/2]

**第二步：Oracle 相位反转**
接下来，我们需要“标记”目标态 |11⟩。量子 Oracle 通过将目标态的相位翻转 180 度（即乘以 -1）来实现标记，而其他非目标态保持不变。这就像是在人群中给目标戴上了一顶特殊的帽子。
经过 Oracle 后，系统的振幅向量变为：
[1/2, 1/2, 1/2, -1/2]
注意，此时虽然 |11⟩ 的振幅变成了负数，但它的概率（振幅的平方）仍然是 1/4，似乎没有变化。

**第三步：扩散算子（关于均值的反转）**
这是振幅放大的魔法所在。扩散算子的几何意义是将所有量子态的振幅关于它们的平均值进行反转。
首先计算当前振幅的平均值 μ：
μ = (1/2 + 1/2 + 1/2 - 1/4) / 4 = 1/4
然后，对每一个振幅 $A_i$ 执行 $A_{new} = 2μ - A_i$ 的操作：
- |00⟩ 的新振幅：2×(1/4) - 1/2 = 0
- |01⟩ 的新振幅：2×(1/4) - 1/2 = 0
- |10⟩ 的新振幅：2×(1/4) - 1/2 = 0
- |11⟩ 的新振幅：2×(1/4) - (-1/2) = 1
可以看到，非目标态的振幅全部缩小到了 0，而目标态 |11⟩ 的振幅被完美放大到了 1（即概率达到了 100%）。

**isQ 代码实现**
我们可以使用 isQ 语言编写代码来验证上述过程。在两比特系统中，标记 |11⟩ 的 Oracle 等效于 CZ 门；而扩散算子可以通过 H 门、X 门和 CZ 门的组合来实现（其原理是利用 H门将计算基转换，然后用控制相位门等效实现条件相位翻转）。

```isQ
import std;

qbit q[2];

procedure main() {
    // 第一步：初始化均匀叠加态
    H(q[0]);
    H(q[1]);
    
    // 第二步：Oracle 相位反转
    // CZ门在控制比特和目标比特均为1时翻转相位，恰好对应目标态 |11>
    CZ(q[0], q[1]);
    
    // 第三步：应用扩散算子
    // 1. 再次应用H门，将态矢量转换回易于操作的计算基
    H(q[0]);
    H(q[1]);
    
    // 2. 应用X门
    X(q[0]);
    X(q[1]);
    
    // 3. 条件相位翻转 (等效于在 |00> 态上翻转相位)
    CZ(q[0], q[1]);
    
    // 4. 恢复X门
    X(q[0]);
    X(q[1]);
    
    // 5. 最后再次应用H门完成扩散变换
    H(q[0]);
    H(q[1]);
    
    // 测量验证结果，理论上将以 100% 的概率测得 11 (即十进制的 3)
    M(q[0]);
    M(q[1]);
}
```

通过这段代码和数学推导，初学者可以清晰地看到振幅放大算法如何巧妙地利用量子叠加和干涉效应，将目标解的概率从茫茫的均等分布中一步步凸显出来。

## isqTrain/3496

- task_id: `isqTrain/3496`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `2643`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```
import std;

qbit q[1];

procedure main() {
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. Initial state: The qubit `q[0]` is initialized to the ground state |0>.
2. Operations: No quantum gates are applied to the qubit. 
3. Final state: The quantum state remains unchanged as |0> before measurement.
4. Measurement: Measuring the state |0> deterministically yields the classical outcome 0.

Predicted probability distribution:
|0>: 1.0

### Reference answer

{'predicted_probs': {'0': 1.0}, 'explanation': 'The output is |0> with probability 1.0'}

## isqTrain/4601

- task_id: `isqTrain/4601`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `ancilla_usage`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4730`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;

qbit q[4];

procedure main() {
    
    X(q[3]);
    H(q[3]);
    
    H(q[0]);
    H(q[1]);
    H(q[2]);
    
    CNOT(q[0], q[3]);
    CNOT(q[2], q[3]);
    
    H(q[0]);
    H(q[1]);
    H(q[2]);
    
    H(q[3]); // superposition on last qubit
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:** The user wants a step-by-step reasoning of an isQ quantum program that predicts the measurement probability distribution. The output must be concise (3-15 lines), use Dirac notation, start with "## Circuit Analysis", and end with the predicted probability distribution.

2.  **Analyze the isQ Program:**
    *   `qbit q[4]`: 4 qubits. Initial state: $|0000\rangle$.
    *   `X(q[3])`: Flips $q_3$. State: $|0001\rangle$.
    *   `H(q[3])`: Applies H to $q_3$. State: $|000-\rangle = \frac{1}{\sqrt{2}}(|0000\rangle - |0001\rangle)$.
    *   `H(q[0]), H(q[1]), H(q[2])`: Applies H to $q_0, q_1, q_2$. State: $\frac{1}{\sqrt{8}} \sum_{x \in \{0,1\}^3} |x\rangle \otimes (|0\rangle - |1\rangle)$.
    *   `CNOT(q[0], q[3])`: Flips $q_3$ if $q_0=1$.
    *   `CNOT(q[2], q[3])`: Flips $q_3$ if $q_2=1$.
        *   Effect on $q_3$: $q_3$ becomes $q_3 \oplus q_0 \oplus q_2$.
        *   State after CNOTs: $\frac{1}{\sqrt{8}} \sum_{x} |x_0 x_1 x_2\rangle \otimes (-1)^{x_0 \oplus x_2} (|0\rangle - |1\rangle)$.
        *   Actually, let's trace $q_3$ carefully. If $x_0 \oplus x_2 = 0$, $q_3$ is unchanged ($|-\rangle$). If $x_0 \oplus x_2 = 1$, $q_3$ is flipped ($-|-\rangle$).
        *   Wait, $X|-\rangle = -|-\rangle$.
        *   So $|x_0 x_1 x_2\rangle (|0\rangle - |1\rangle)$ becomes $|x_0 x_1 x_2\rangle (-1)^{x_0 \oplus x_2}(|0\rangle - |1\rangle)$.
    *   `H(q[0]), H(q[1]), H(q[2])`: Applies H to the first 3 qubits.
        *   $H^{\otimes 3} \sum_x (-1)^{x_0 \oplus x_2} |x_0 x_1 x_2\rangle$.
        *   Let's compute this. This is the Hadamard transform of the state $(-1)^{x_0 \oplus x_2}$.
        *   $x_0 \oplus x_2 = x \cdot 101$.
        *   By the property of Hadamard transform, $H^{\otimes n} \sum_x (-1)^{x \cdot y} |x\rangle = |y\rangle$.
        *   So the first 3 qubits become $|101\rangle$. (Which means $q_0=1, q_1=0, q_2=1$).
    *   `H(q[3])`: Applies H to $q_3$. $H|-\rangle = |1\rangle$.
    *   Final state before measurement: $|1011\rangle$.
        *   Wait, isq string order. $q_0$ is the highest bit or lowest?
        *   Usually $q_0$ is MSB in bitstrings. Let's assume $|q_0 q_1 q_2 q_3\rangle$.
        *   If $q_0=1, q_1=0, q_2=1$, the bitstring is $1011$.
        *   Let's re-verify The implementation: `Expected measurement probabilities: {|0101>: 1.0}`.
        *   Ah! The implementation says `|0101>`. Let's figure out why.
        *   Reference string: `|0101>`. Wait, number of qubits measured: 4.
        *   Let's re-read the predicted output: `{0101: 1.0}`. Wait, if the state is `101

### Reference answer

{'predicted_probs': {'0101': 1.0}, 'explanation': 'This isQ program operates on 4 qubit(s). The measurement probability distribution is: P(|0101>) = 1.0000.'}

## isqQA/quantum_algorithms/41_principle_advantage

- task_id: `isqQA/quantum_algorithms/41_principle_advantage`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `principle_advantage`, `algorithm`, `Grover搜索算法`
- source: `qa_pipeline`
- dataset_index: `2238`

### Prompt

Grover搜索算法是量子计算中最具代表性的算法之一。请详细解释Grover算法的宏观工作原理，对比它与经典搜索算法在时间复杂度上的差异，并深入分析其能够实现量子加速的根本来源是什么。

### Reference answer

Grover搜索算法（又称量子搜索算法）主要用于在无结构的数据库中寻找特定元素。它的宏观工作原理可以概括为“量子振幅放大”。算法过程主要包含以下几个核心步骤：首先，将系统的初始状态制备为所有可能状态的等概率叠加态（均匀叠加态）。接着，算法反复执行两个关键操作：一是Oracle（预言机）操作，它能够识别目标状态并将其概率幅的相位反转（即乘以-1），而保持其他状态的相位不变；二是扩散算子（Diffusion Operator）操作，它的作用是将所有状态的概率幅围绕它们的平均值进行翻转。这两个操作的组合每次都会将目标状态的概率幅稍微增大，同时减小非目标状态的概率幅。经过大约 $O(\sqrt{N})$ 次迭代后，目标状态的概率幅将趋近于1，此时进行测量，即可有极大概率得到目标结果。

在时间复杂度对比方面，经典计算在处理无结构数据库搜索时，只能逐个检查数据，因此最坏情况下的时间复杂度为 $O(N)$，平均也需要 $O(N/2)$。而Grover算法利用量子力学的特性，将搜索时间复杂度大幅降低到了 $O(\sqrt{N})$。例如，当 $N = 10^6$（即一百万个数据）时，经典算法需要一百万次操作，而Grover算法仅需大约一千次操作。这种从线性复杂度到平方根复杂度的跨越，在数据量极大时展现出极为显著的效率优势。值得一提的是，Bennett等人已经证明，对于无结构搜索问题，$O(\sqrt{N})$ 是量子算法的复杂度下限，这意味着Grover算法在该领域已经达到了最优。

Grover算法能够实现量子加速的根本来源，在于量子力学的**叠加态**与**干涉效应**。首先，由于量子比特可以处于0和1的叠加态，$n$ 个量子比特可以同时表示 $2^n$ 种状态，这赋予了量子计算机极其强大的并行处理能力，使得Oracle能够一次性评估所有可能的状态。然而，仅有叠加态是不够的，因为直接测量叠加态只会等概率地塌缩到某一个状态，这并没有比经典随机猜测更好。量子加速的核心关键在于第二步：利用概率幅的干涉。Oracle给目标状态打上了特殊的“相位标记”，随后扩散算子巧妙地利用了波的干涉原理，使得目标状态的概率幅发生相长干涉（不断叠加增大），而非目标状态的概率幅发生相消干涉（相互抵消减小）。这种通过精确设计的量子线路，引导系统状态演化到目标状态的过程，就是量子加速的本质所在。

## isqTrain/2943

- task_id: `isqTrain/2943`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_for_loop`, `isq_syntax_multi_register`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1190`

### Prompt

修复以下isQ程序中的错误：

```isq
import std;
qbit q[6];
// Apply H to all 6 qubits (uniform superposition)
procedure main() {
    for i in 0:6 {
        H(q[i]);
    }
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[0]);
    M(q[4]);
    M(q[5]);
}

```

### Chain-of-thought reasoning

## Bug Analysis

**Bug:** The fourth measurement statement measures `q[0]` instead of `q[3]`, causing qubit 3 to never be measured and qubit 0 to be measured twice.

**Fix:** Change the fourth `M(q[0])` to `M(q[3])` so all six qubits are measured exactly once.

**State evolution:**
1. Initialize 6 qubits in |000000⟩
2. Apply H to each qubit via the loop, creating uniform superposition: (1/√8) Σ|x⟩ for all x ∈ {0,1}⁶ = (|0⟩+|1⟩)⊗⁶/√64
3. Each of the 64 basis states has equal probability 1/64 ≈ 0.015625

## isqTrain/3010

- task_id: `isqTrain/3010`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3566`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;
qbit q[4];
procedure main() {
    H(q[0]);
    H(q[0]);
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

## Circuit Analysis
1. **Operations**: The circuit applies two Hadamard (H) gates to each of the four qubits: `q[0]`, `q[1]`, `q[2]`, and `q[3]`.
2. **State Evolution**: The Hadamard gate is its own inverse, meaning $H \cdot H = I$. Thus, applying two consecutive Hadamard gates to any qubit leaves its state unchanged.
3. **Final State**: Since all qubits start in the $|0\rangle$ state and the gates applied result in the identity operation, the final state of the system before measurement is $|0000\rangle$.
4. **Probabilities**: Measurement will deterministically yield the state $|0000\rangle$ with a probability of 1.0.

Probability distribution: {'0000': 1.0}

### Reference answer

{'predicted_probs': {'0000': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/3550

- task_id: `isqTrain/3550`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `hamiltonian_simulation`, `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `3822`

### Prompt

Fix the bug in the following isQ program.

Bug description: Wrong CNOT direction

The program should 2-qubit Heisenberg XXX model, 1 Trotter step from |10>.

### Chain-of-thought reasoning

## Bug Analysis

1. **The bug** is in the XX interaction section. The first CNOT has reversed arguments: `CNOT(q[1], q[0])` instead of `CNOT(q[0], q[1])`. This breaks the standard Z⊗Z simulation decomposition (CNOT-Rz-CNOT), which requires consistent control/target roles. The two CNOTs surrounding the Rz must use the same (control, target) pair to properly create the entangling phase on the |11⟩ component of the rotated basis.

2. **The fix** changes line 14 from `CNOT(q[1], q[0])` to `CNOT(q[0], q[1])`, making both CNOTs in the XX block consistent with q[0] as control and q[1] as target—matching the pattern used correctly in the YY and ZZ sections.

3. **State evolution (corrected):** Starting from |10⟩ (after X(q[0])):
   - **XX block:** H⊗H rotates to |−⟩|+⟩. CNOT(q[0],q[1]) entangles, Rz(0.6,q[1]) phases the |1⟩ target components, then CNOT+H⊗H undo, implementing exp(−i·0.3·X⊗X).

## isqTrain/78

- task_id: `isqTrain/78`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `622`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[2];
procedure main() {
    // EPR pair
    H(q[0]); CNOT(q[0], q[1]);
    // Encode "11": apply Z then X to Alice's qubit
    Z(q[0]); X(q[0]);
    // Decode
    CNOT(q[0], q[1]);
    H(q[0]);
    // Measure
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Output prediction for an isQ program representing the superdense coding protocol.
    *   Program logic: EPR pair creation -> Encode "11" with Z then X -> Decode with CNOT then H -> Measure.
    *   Output format: "## Circuit Analysis" header, concise step-by-step state evolution using Dirac notation, predicted probability distribution at the end.

2.  **Step-by-Step State Evolution:**
    *   *Initial state:* |00>
    *   *H(q[0]):* q[0] becomes |+>, state is 1/√2 (|00> + |10>)
    *   *CNOT(q[0], q[1]):* Entangled, state is 1/√2 (|00> + |11>). This is the EPR pair / Bell state $\beta_{00}$.
    *   *Z(q[0]):* Applies Z to q[0]. Z|0> = |0>, Z|1> = -|1>. State becomes 1/√2 (|00> - |11>). This is $\beta_{10}$.
    *   *X(q[0]):* Applies X to q[0]. X|0> = |1>, X|1> = |0>. State becomes 1/√2 (|10> - |01>). This is $\beta_{11}$.
    *   *CNOT(q[0], q[1]):* Decoding step. Let's trace it.
        *   Current: 1/√2 (|10> - |01>)
        *   CNOT on |10> -> |11>
        *   CNOT on |01> -> |01>
        *   New state: 1/√2 (|11> - |01>) = 1/√2 |1>_0 (|1>_1 - |0>_1)
    *   *H(q[0]):* Applied to the first qubit.
        *   Current: 1/√2 |1>_0 (|1>_1 - |0>_1)
        *   H|0> = 1/√2(|0> + |1>)
        *   H|1> = 1/√2(|0> - |1>)
        *   New state: 1/√2 * [ 1/√2(|0> - |1>) ] * (|1> - |0>)
        *   = 1/2 (|01> - |00> - |11> + |10>)
        *   Let's re-evaluate: 1/√2 (|11> - |01>) is $|1\rangle \otimes \frac{1}{\sqrt{2}}(|1\rangle - |0\rangle)$. Wait, let me write it carefully.
        *   State before H: 1/√2 (|11> - |01>) = 1/√2 |1>_0 |1>_1 - 1/√2 |0>_0 |1>_1. Wait, CNOT(1/√2(|10> - |01>)) = 1/√2 (|11> - |01>). Correct.
        *   Apply H to q[0]:
            *   H |0> = (|0> + |1>) / √2
            *   H |1> = (|0> - |1>) / √2
            *   State: 1/√2 [ (|0> - |1>)/√2 * |1> - (|0> + |1>)/√2 * |0> ] -- wait, CNOT was applied.
            *   Let's use Bell basis transformations.
            *   $\beta_{11}$ = (X $\otimes$ Z) $\beta_{00}$.
            *   Alternatively: H CNOT maps Bell basis to computational basis.
            *   $H_1 CNOT_{1,2} \beta_{00} = |00\rangle$
            *   $H_1 CNOT_{1,2} \beta_{01} = |10\rangle$
            *   $H_1 CNOT_{1,2} \beta_{10} = |01\rangle$
            *   $H_1 CNOT_{1,2} \beta_{11} = |11\rangle$
            *   Since we applied Z then X, we mapped $\beta_{00}$ to $\beta_{11}$.
            *   So $H_1 CNOT_{1,2} \beta_{11}$ yields $|11\rangle$.
    *   *Check:* Let's do the math manually.
        *   $1/\sqrt{2}(|10

### Reference answer

{'predicted_probs': {'3': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/18. Dimension: predict probabilities for reference circuit.'}
