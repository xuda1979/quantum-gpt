# ISQ training COT RAG corpus: quantum_algorithms shard 34

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/48

- task_id: `isqTrain/48`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_arrays`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3192`

### Prompt

请用isQ语言编写一个量子电路：implements a variant of the oracle_boolean pattern using q[3] -> q[5]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a balanced oracle on qubits q[0]-q[2] within an expanded 5-qubit register, leaving q[3]-q[4] untouched in the ground state.
2. **Qubits**: 5 qubits declared (q[0] to q[4]); all are measured.
3. **State evolution**:
   - Initial state: |00000⟩ (all qubits in |0⟩)
   - CNOT(q[0], q[2]): control q[0] is |0⟩, so target q[2] unchanged → |00000⟩
   - CNOT(q[1], q[2]): control q[1] is |0⟩, so target q[2] unchanged → |00000⟩
   - Qubits q[3] and q[4] remain in |0⟩ throughout (no operations applied)
4. **Expected probabilities**: Since all controls are |0⟩, no CNOT activates; the state remains |00000⟩ with probability 1.0.

## isqTrain/773

- task_id: `isqTrain/773`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4697`

### Prompt

Implement the following in isQ: implements the weighted_adder pattern. Include explicit identity operations in the circuit (X-X pair before M(q[3])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning

**Goal**: Implement a 3-input weighted adder summing q[0]+q[1]+q[2] into a 2-bit result (q[3]=sum, q[4]=carry), with an explicit X-X identity pair demonstrating gate cancellation.

**Qubits**: 5 (q[0]-q[4]); q[3] and q[4] are measured.

**State evolution**:

## isqTrain/4351

- task_id: `isqTrain/4351`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `338`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;

// Oracle for balanced function f(x) = x[0] XOR x[1]
oracle bool[1] f(bool x[2]) {
    // XOR of two input bits yields a balanced function
    bool res[] = [x[0] != x[1]];
    return res;
}

// Input register: 2 qubits
qbit q[2];
// Ancilla qubit for phase kickback
qbit anc[1];

procedure main() {
    // Prepare ancilla in |-> state for phase kickback
    X(anc[0]);
    H(anc[0]);
    // Create uniform superposition on input register
    H(q[0]); H(q[1]);
    // Single oracle query -- the key quantum speedup
    f(q, anc);
    // Interfere to extract function type
    H(q[0]); H(q[1]);
    // Measure input register only
    // Balanced function guarantees non-zero outcome
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants an analysis of an isQ program implementing the Deutsch-Jozsa algorithm for a balanced function $f(x_0, x_1) = x_0 \oplus x_1$. I need to output a step-by-step reasoning using Dirac notation, explaining the state evolution and predicting the final probability distribution.

2.  **Analyze the isQ Code:**
    *   **Qubits:** `q[2]` (input register), `anc[1]` (ancilla for phase kickback).
    *   **Initialization:** `|q[0]q[1]anc[0]\rangle = |000\rangle`.
    *   **Ancilla Prep:** `X(anc[0]); H(anc[0]);` transforms `|0\rangle \to |1\rangle \to |-\rangle`.
        *   State: `|00\rangle \otimes |-\rangle`.
    *   **Input Prep:** `H(q[0]); H(q[1]);` transforms `|00\rangle \to |++\rangle = \frac{1}{2} \sum_{x \in \{0,1\}^2} |x\rangle`.
        *   State: $\frac{1}{2} \sum_{x} |x\rangle \otimes |-\rangle$.
    *   **Oracle `f(q, anc)`:** Computes $f(x) = x_0 \oplus x_1$. The oracle applies $CZ$ or phase flip equivalent. Wait, an oracle in isQ typically computes $f(x)$ and XORs it to the ancilla. Since ancilla is in $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$, the phase kickback applies a phase $(-1)^{f(x)}$ to the input register.
        *   $f(x) = x_0 \oplus x_1$ is 1 for 01 and 10, and 0 for 00 and 11.
        *   State: $\frac{1}{2} (|00\rangle - |01\rangle - |10\rangle + |11\rangle) \otimes |-\rangle$.
    *   **Interference:** `H(q[0]); H(q[1]);` applied to the input register.
        *   Recall $H^{\otimes n} \sum_x (-1)^{f(x)}|x\rangle = \sum_z \left(\frac{1}{2^n} \sum_x (-1)^{f(x)+x\cdot z}\right) |z\rangle$.
        *   Specifically for Deutsch-Jozsa, a balanced function results in an amplitude of 0 for $|00\rangle$.
        *   Let's do it manually:
            *   $H|0\rangle = |+\rangle$, $H|1\rangle = |-\rangle$.
            *   $H(|00\rangle) = |++\rangle = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$
            *   $H(|01\rangle) = |+-\rangle = \frac{1}{2}(|00\rangle - |01\rangle + |10\rangle - |11\rangle)$
            *   $H(|10\rangle) = |-+\rangle = \frac{1}{2}(|00\rangle + |01\rangle - |10\rangle - |11\rangle)$
            *   $H(|11\rangle) = |--\rangle = \frac{1}{2}(|00\rangle - |01\rangle - |10\rangle + |11\rangle)$
        *   Wait, I need $H$ applied to the state: $|00\rangle - |01\rangle - |10\rangle + |11\rangle$.
        *   State after $H^{\otimes 2}$:
            $\frac{1}{2} [ H(|00\rangle) - H(|01\rangle) - H(|10\rangle) + H(|11\rangle) ]$
            $= \frac{1}{4} [ (|00\rangle+|01\rangle+|10\rangle+|11\rangle) - (|00\rangle-|01\rangle+|10\rangle-|11\rangle) - (|00\rangle+|01\rangle-|10\rangle-|11\rangle) + (|00\rangle-|01\rangle-|10\rangle+|11\rangle) ]$
            $= \frac{1}{4} [ |11\rangle(1 - (-1) - (-

### Reference answer

{'predicted_probs': {'01': 1.0}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|01>) = 1.0000.'}

## isqTrain/877

- task_id: `isqTrain/877`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `740`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;
qbit q[5];

procedure main() {
    // Encode x = [1, 0]
    X(q[0]);
    // Encode y = [1, 1]
    X(q[2]); X(q[3]);
    // Compute x[0]*y[0] and XOR into result q[4]
    ctrl ctrl X(q[0], q[2], q[4]);
    // Compute x[1]*y[1] and XOR into result q[4]
    ctrl ctrl X(q[1], q[3], q[4]);
    // IP = (1*1) XOR (0*1) = 1
    M(q[4]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Goal:** Generate a concise, step-by-step reasoning for an isQ quantum program.
    *   **Program:** A 5-qubit circuit computing the inner product of two classical bit vectors $x = [1, 0]$ and $y = [1, 1]$ using a Toffoli gate implementation (inner product in $GF(2)$).
    *   **Format:** Start with "## Circuit Analysis", do NOT include code blocks, use Dirac notation, end with the predicted probability distribution.
    *   **Constraint:** 3-8 lines for simple circuits, up to 15 for complex ones. Be concise.

2.  **Analyze the isQ Program:**
    *   Initialization: 5 qubits `q[0]` to `q[4]` in $|0\rangle$. Initial state: $|00000\rangle$.
    *   `X(q[0]);`: Flips $q[0]$ to 1. State becomes $|10000\rangle$.
    *   `X(q[2]); X(q[3]);`: Flips $q[2]$ and $q[3]$ to 1. State becomes $|10110\rangle$. (x=[1,0] is in q[0],q[1]; y=[1,1] is in q[2],q[3]).
    *   `ctrl ctrl X(q[0], q[2], q[4]);`: Toffoli gate with controls q[0]=1, q[2]=1, target q[4]. Since both controls are 1, it flips q[4] to 1. State becomes $|10111\rangle$. (Calculates x[0]*y[0] = 1*1 = 1).
    *   `ctrl ctrl X(q[1], q[3], q[4]);`: Toffoli gate with controls q[1]=0, q[3]=1, target q[4]. Control q[1] is 0, so no flip. State remains $|10111\rangle$. (Calculates x[1]*y[1] = 0*1 = 0, XORed into q[4] -> 1^0 = 1).
    *   `M(q[4]);`: Measures $q[4]$ in the computational basis. Result is 1 with probability 1.0.

3.  **Draft the Reasoning (incorporating constraints):**
    *   *Step 1:* Initial state is $|00000\rangle$. X gates on $q_0, q_2, q_3$ set the state to $|10110\rangle$.
    *   *Step 2:* The first Toffoli gate `ctrl ctrl X(q[0], q[2], q[4])` evaluates $q_0 \land q_2$. Since both are 1, $q_4$ flips to 1. State becomes $|10111\rangle$.
    *   *Step 3:* The second Toffoli gate `ctrl ctrl X(q[1], q[3], q[4])` evaluates $q_1 \land q_3$. Since $q_1=0$, it does not flip $q_4$.
    *   *Step 4:* The state remains $|10111\rangle$. Measuring $q_4$ yields 1 with certainty, representing the inner product $1 \oplus 0 = 1$.
    *   *Final Prediction:* Predicted probabilities: {|1>: 1.0}

4.  **Refine and Condense:**
    *   "## Circuit Analysis" (Header)
    *   1. Operations: X gates on q[0], q[2], q[3]; Two Toffoli (Toffoli) gates targeting q[4] with respective controls (q[0], q[2]) and (q[1], q[3]); Measurement of q[4].
    *   2. State evolution: Starts at $|00000\rangle$. X gates encode inputs yielding $|10110\rangle$. The first Toffoli flips $q_4$ since $q_0=1, q_2=1$, transitioning state to $|10111\rangle$.
    *   3. The second Toffoli does nothing since $q_1=0$, leaving the state at $|10111\rangle$.
    *   4. Measuring q[4] deterministically yields 1, computing the bitwise inner product $(1\cdot1) \oplus (0\cdot1) = 1$.
    *   Predicted probabilities: {|1>: 1.0}

5.

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Parametric variant of isqEval/254. Dimension: predict probabilities for reference circuit.'}

## isqQA/quantum_algorithms/121_principle_advantage

- task_id: `isqQA/quantum_algorithms/121_principle_advantage`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `principle_advantage`, `algorithm`, `量子行走算法`
- source: `qa_pipeline`
- dataset_index: `1609`

### Prompt

请深入解析离散时间量子行走算法的核心原理。相比于经典的马尔可夫链随机行走，量子行走在数学和物理本质上有哪些根本不同？这种机制如何导致算法时间复杂度上的量子加速？请从干涉和相干性的角度详细阐述加速的来源，并使用isQ语言编写一段演示2节点图上量子行走的代码，展示硬币算符与条件移位演化的过程。

### Reference answer

要深入理解离散时间量子行走，我们必须对比经典的随机行走过程。在经典随机行走中，粒子的状态由其在图各个节点上的概率分布描述，演化过程是一个马尔可夫链，每一步的转移依赖于概率。而量子行走则完全不同，它的演化是由量子力学法则主导的，状态由希尔伯特空间中的态矢量（概率幅）描述，且演化必须是幺正的。<粒子状态> 为了在图上构建合法的幺正演化，离散时间量子行走必须引入一个额外的希尔伯特空间——硬币空间。粒子的状态被表示为位置空间和硬币空间的张量积：$|\psi\rangle = \sum_{x} \sum_{c} \alpha_{x,c} |c\rangle \otimes |x\rangle$，其中 $|x\rangle$ 是位置态，$|c\rangle$ 是硬币态（例如在 $d$-正则图中，硬币空间维度为 $d$）。每一步的量子行走由两个算符的乘积构成：首先是硬币算符 $C$（通常为Hadamard门、Grover扩散门或离散傅里叶变换），它只作用在硬币空间上，使粒子进入位置的叠加态；随后是条件移位算符 $S$，它根据硬币态将粒子移动到相邻的节点。整体演化即为 $U = S \cdot (C \otimes I_{position})$。</粒子状态>
<加速来源> 量子行走之所以能带来算法上的加速，其物理本质在于量子相干性导致的干涉效应。在经典随机行走中，走多条路径的粒子只能以一定的概率选择其中一条，各个路径的贡献是概率相加的；其位置方差随时间 $t$ 呈线性增长 $\sigma^2 \propto t$。但在量子行走中，粒子同时走所有的路径，不同路径的概率幅之间会发生复杂的相长干涉和相消干涉。这种干涉使得概率幅在空间中的分布呈现出高度非均匀的弹道式传播特征，其方差随时间呈二次方增长 $\sigma^2 \propto t^2$。在解决图搜索问题时（如Grover搜索的图论推广），我们可以设计特定的硬币算符，使得非目标节点的概率幅发生相消干涉而相互抵消，同时目标节点的概率幅发生相长干涉而迅速积累。正是这种“过滤”机制，使得量子行走能够在极少的步数内定位到目标。</加速来源>
<时间复杂度对比> 基于上述原理，量子行走提供了强有力的时间复杂度加速。例如在经典的无结构数据库搜索或图遍历中，随机行走达到稳态或找到目标需要的时间复杂度为 $O(N)$。而基于量子行走的搜索算法可以将时间复杂度降至 $O(\sqrt{N})$，实现平方级加速。在某些特定结构的图（如二维网格上的相遇问题或具有特殊对称性的图）和黑盒问题（如元素区分问题）中，量子行走甚至能够实现指数级加速（$O(1)$ vs $O(\sqrt{N})$）。这种无需依赖底层复杂数据结构的通用加速手段，使得量子行走成为了量子算法设计的通用工具。</时间复杂度对比>
<代码演示> 下面使用isQ语言实现一个2节点图（即一条边连接节点0和节点1）上的量子行走。在这个模型中，位置由1个量子比特表示，硬币也由1个量子比特表示。通过施加Hadamard硬币操作和受控非门（CNOT）进行条件移位，展示纠缠和演化过程。</代码演示>

```isQ
import std;

// 声明量子比特：coin[1]作为硬币空间，pos[1]作为位置空间
qbit coin[1];
qbit pos[1];

procedure main() {
    // 初始化状态为 |0>_coin |0>_pos
    // 第一步：抛硬币操作，使用Hadamard门将硬币置于叠加态
    H(coin[0]);
    
    // 第二步：条件移位操作
    // 如果硬币为|0>，位置不变；如果硬币为|1>，位置翻转（从节点0走到节点1）
    // 使用CNOT门完美实现这一逻辑
    CNOT(coin[0], pos[0]);
    
    // 我们可以再进行一步量子行走以观察干涉现象
    // 再次抛硬币
    H(coin[0]);
    
    // 再次条件移位
    CNOT(coin[0], pos[0]);
    
    // 此时如果不测量，系统将处于位置和硬币的纠缠态
    // 为了提取经典信息，对硬币和位置进行测量
    // 在isQ的--probs模式下，也可以省略M()以直接查看状态向量的振幅分布
    M(coin[0]);
    M(pos[0]);
}
```

## isqTrain/3999

- task_id: `isqTrain/3999`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `5448`

### Prompt

This isQ program doesn't produce the correct output. Can you debug it?

Code:
```
import std;
// Inverse QFT on 3 qubits with input |000>
qbit q[3];

procedure main() {
    // Prepare input

    CNOT(q[0], q[2]);
    CNOT(q[0], q[2]);
    CNOT(q[0], q[2]);
    H(q[2]);
    ctrl Rz(-2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    H(q[1]);
    ctrl Rz(-2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    ctrl Rz(-2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    H(q[0]);
    // Measure after inverse QFT
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: swapped qubits)

### Chain-of-thought reasoning

The buggy code has:

This is three identical CNOTs with q[0] as control and q[2] as target. Three CNOTs in succession is equivalent to one CNOT (since CNOT is self-inverse, CNOT^3 = CNOT).

The corrected version:

This is a swap operation (three-CNOT decomposition) implemented as three CNOTs. It swaps the states of q[0] and q[2].

Wait, let me check: CNOT(a, b); CNOT(b, a); CNOT(a, b) is indeed a swap operation (three-CNOT decomposition).

So the bug is that the second CNOT should have q[2] as control and q[0] as target, but in the buggy code it has q[0] as control and q[2] as target (same as the other two).

Now, let me think about what this circuit is supposed to do. It's an inverse QFT on 3 qubits with input |000>.

For inverse QFT, after applying it to |000>, we should get |000> (since QFT|000> = (1/√8)Σ|x>, and inverse QFT of that should give |000>... wait, no.

Actually, QFT|000> = (1/√8)Σ_{k=0}^{7} |k>. So inverse QFT applied to (1/√8)Σ|k> = |000>.

But the circuit starts with |000> and applies inverse QFT to it. inverse QFT|000> = |000>. That would just give |000>.

Hmm, but the expected measurement probabilities show equal probability for all 8 states. So the output is (1/√8)Σ|x>, which is the uniform superposition.

Wait, maybe the circuit is actually applying QFT (not inverse QFT) despite the comment saying "inverse QFT"? Or maybe the "prepare input" section prepares some state that when inverse QFT is applied gives the uniform superposition?

Actually, let me re-read: The predicted output equal probability for all states, which means the final state is (1/√8)Σ|x>.

If we're doing inverse QFT on |000>, the result should just be |000>. So maybe the "inverse QFT" label is misleading, or the circuit is actually doing QFT.

Actually, looking at the circuit more carefully:

The gates after the "prepare input" section look like an inverse QFT circuit. In a standard QFT, you'd have:
1. H on first qubit
2. Controlled rotations with increasing angles
3. Swap at the end

For inverse QFT, you'd reverse the order and negate the angles.

But here, the circuit has:
- Some swap (three-CNOT decomposition)-like operations at the beginning
- H(q[2]) first, then controlled Rz gates, then H(q[1]), etc.

This looks like the swap is at the beginning (part of the QFT or inverse QFT structure where swaps are typically at the end).

Let me just focus on the bug: the second CNOT in the swap (three-CNOT decomposition) sequence has the wrong control and target. It should be CNOT(q[2], q[0]) but was written as CNOT(q[0], q[2]).

With the bug (three identical CNOTs = one CNOT):
- CNOT(q[0], q[2]) flips q[2] when q[0]=1. Since both are |0>, nothing happens. State remains |000>.

With the fix (proper swap (three-CNOT decomposition)):
- swap (three-CNOT decomposition)(q[0], q[2]) on |000> = |000>. Still nothing.

Hmm, so the swap on |000> doesn't change anything either way.

Wait, but The predicted output equal superposition. So there must be something else going on. Let me look at the inverse QFT part more carefully.

H(q[2]) on |000> → (|0⟩+|1⟩)/√2 on q[2], state = (|000⟩+|001⟩)/√2 (assuming q[0] is MSB... actually depends on convention).

Actually wait, I need to be careful about bit ordering. In isQ, q[0] might be the highest bit or lowest bit.

Looking at the predicted output: {|000>: 0.125, |001>: 0.125, ..., |111>: 0.125} - equal superposition.

Let me trace through the corrected circuit:

Initial state: |000⟩ (q[2], q[1], q[0] -

## isqTrain/1155

- task_id: `isqTrain/1155`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `824`

### Prompt

Create an isQ quantum circuit that implements a variant of the mcmt_gate pattern using q[4] -> q[6]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement a multi-controlled multi-target X gate variant using q[4]→q[6] with 2 controls flipping 2 targets, leaving extra qubits in |0⟩.

2. **Qubits**: 6 total (q[0]–q[5]), all measured. Controls: q[0], q[1]; targets: q[2], q[3]; unused: q[4], q[5].

3. **State evolution**:
   - |000000⟩ → X(q[0]) → |100000⟩
   - |100000⟩ → X(q[1]) → |110000⟩
   - |110000⟩ → ctrl ctrl X(q[0],q[1],q[2]) → |111000⟩ (both controls |1⟩ flips q[2])
   - |111000⟩ → ctrl ctrl X(q[0],q[1],q[3]) → |111100⟩ (both controls |1⟩ flips q[3])
   - q[4], q[5] untouched, remain |0⟩

4. **Expected probabilities**: Final state |111100⟩ yields measurement outcome `111100` with

## isqTrain/1251

- task_id: `isqTrain/1251`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `ancilla_usage`, `entanglement`, `isq_syntax_arrays`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `4081`

### Prompt

请用isQ语言编写一个量子电路：implements a variant of the error_correction_syndrome pattern using data[3] -> data[4]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

Let me analyze this problem step by step.

The task is to implement a variant of error_correction_syndrome using data[3] -> data[4], meaning we expand the qubit register from 3 data qubits to 4 data qubits.

Analyzing the circuit requirements:
- It uses a 3-qubit bit-flip code
- Encodes logical |1> = |111>
- Introduces an error on data[1]
- Extracts syndrome via parity checks
- Measures syndrome qubits

The variant needs data[4] instead of data[3], so we have 4 data qubits.

Let me trace through the circuit in the reference:
1. Initialize: |000000> (4 data + 2 syndrome)
2. X(data[0]): |100000>
3. CNOT(data[0], data[1]): |110000>
4. CNOT(data[0], data[2]): |111000>
5. X(data[1]) error: |101000>
6. CNOT(data[0], syndrome[0]): |101100> - syndrome[0] gets data[0] XOR data[1] = 1 XOR 0 = 1
7. CNOT(data[1], syndrome[0]): |101000> - wait, let me redo this

Actually, let me be more careful:
State after encoding: |111> ⊗ |00> = |11100>

After error X(data[1]): |101> ⊗ |00> = |10100>

Now syndrome extraction:
- CNOT(data[0], syndrome[0]): data[0]=1, so syndrome[0] flips → |10110>
- CNOT(data[1], syndrome[0]): data[1]=0, so syndrome[0] doesn't flip → |10110>
- So syndrome[0] = 1 XOR 0 = 1

- CNOT(data[1], syndrome[1]): data[1]=0, so syndrome[1] doesn't flip → |10110>
- CNOT(data[2], syndrome[1]): data[2]=1, so syndrome[1] flips → |10111>

So syndrome = |11>

Wait, that's correct! The error on data[1] produces syndrome |11> because:
- syndrome[0] = data[0] XOR data[1] = 1 XOR 0 = 1
- syndrome[1] = data[1] XOR data[2] = 0 XOR 1 = 1

So The predicted output |11> with probability 1.0.

For the variant with data[4]:
- We need to adjust the encoding to use 4 data qubits
- The syndrome extraction should still work similarly

The task says "data[3] -> data[4]", meaning we expand from 3 to 4 data qubits. The reference already shows data[4] declaration but only uses data[0], data[1], data[2]. So perhaps the variant uses all 4 qubits.

Let me think about what a 4-qubit code might look like. Perhaps:
- Encode logical |1> = |1111>
- Use appropriate parity checks

But the expected measurement is still |11>, so the syndrome qubits should still give that result.

Actually, looking more carefully at the reference code, it already declares `qbit data[4]` but only uses indices 0, 1, 2. So maybe the task is just to extend the usage to include data[3] somehow while maintaining the syndrome pattern.

For a 4-qubit repetition code:
- Encode |1>_L = |1111>
- Parity checks could be:
  - syndrome[0] = data[0] XOR data[1]
  - syndrome[1] = data[2] XOR data[3]

Or we could keep the same syndrome pattern but extend the encoding:
- Encode |1>_L = |1111>
- syndrome[0] = data[0] XOR data[1]
- syndrome[1] = data[1] XOR data[2]
- (maybe another syndrome for data[2] XOR data[3])

But we only have 2 syndrome qubits, so let's keep the same structure.

With 4 data qubits encoding |1111>, if we introduce error on data[1]:
- State becomes |1011> ⊗ |00>
- syndrome[0] = data[0] XOR data[1] = 1 XOR 0 = 1
- syndrome[1] = data[1] XOR data[2] = 0 XOR 1 = 1
- Result: syndrome = |11>

This matches the predicted output!

So the circuit would be:
1. X(data[0]): Initialize first qubit to |1>
2. CNOT(data[0], data

## isqTrain/724

- task_id: `isqTrain/724`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5120`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
qbit q[5];

procedure main() {
    // Encode a=1 (binary 01) and b=1 (binary 01)
    X(q[0]);
    X(q[2]);
    // Bit 0: compute carry0 = a0 AND b0
    Toffoli(q[0], q[2], q[4]);
    // Bit 0: sum0 = a0 XOR b0 (result stored in q[2])
    CNOT(q[0], q[2]);
    // Bit 1: propagate a1 and carry into b1
    CNOT(q[1], q[3]);
    CNOT(q[4], q[3]);
    // Measure sum bits: q[2]=sum0, q[3]=sum1
    M(q[2]);
    M(q[3]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a concise, step-by-step analysis of an isQ quantum program, predicting the measurement outcomes and explaining the reasoning using Dirac notation. The final output must start with "## Circuit Analysis" and end with the probability distribution.

2.  **Analyze the Code:**
    *   Initialization: `qbit q[5];` -> |00000>
    *   `X(q[0]); X(q[2]);` -> |00101> (q[0] is the least significant bit, wait, standard Dirac is usually q[4]q[3]q[2]q[1]q[0] or similar. Let's trace carefully. q[0]=1, q[2]=1, others=0).
    *   `Toffoli(q[0], q[2], q[4]);` -> q[0] and q[2] are 1, so q[4] flips. q[4] becomes 1. State: |10101>
    *   `CNOT(q[0], q[2]);` -> q[0] is 1, so q[2] flips. q[2] becomes 0. State: |10100>
    *   `CNOT(q[1], q[3]);` -> q[1] is 0, so q[3] unchanged. State: |10100>
    *   `CNOT(q[4], q[3]);` -> q[4] is 1, so q[3] flips. q[3] becomes 1. State: |11100> (q[4]=1, q[3]=1, q[2]=0, q[1]=0, q[0]=0)
    *   Let's re-verify bit ordering. Let's just track the values.
        *   q[0] = 1, q[1] = 0, q[2] = 1, q[3] = 0, q[4] = 0 initially.
        *   `X(q[0]), X(q[2])` -> q[0]=1, q[2]=1.
        *   `Toffoli(q[0], q[2], q[4])` -> carry0 = 1 AND 1 = 1. So q[4] = 1.
        *   `CNOT(q[0], q[2])` -> sum0 = 1 XOR 1 = 0. So q[2] = 0.
        *   `CNOT(q[1], q[3])` -> q[3] = 0 XOR 0 = 0.
        *   `CNOT(q[4], q[3])` -> q[3] = 0 XOR 1 = 1.
        *   So final values: q[2]=0, q[3]=1.
    *   Measurements: `M(q[2])`, `M(q[3])`.
        *   Measured bitstring according to standard output conventions: Earlier measured qubit = higher bit.
        *   Wait, the prompt says: "--probs output: array indexed by measurement bitstring (earlier measured qubit = higher bit)."
        *   `M(q[2])` is measured first. So it's the higher bit.
        *   `M(q[3])` is measured second. So it's the lower bit.
        *   Higher bit = q[2] = 0.
        *   Lower bit = q[3] = 1.
        *   Resulting bitstring = '01' (q[2]=0, q[3]=1).
        *   Wait, is "01" corresponding to the state where q[2]=0 and q[3]=1? Yes. Let's check The implementation. Reference says Expected measurement probabilities: {|01>: 1.0}. So my deduction is correct.

3.  **Draft the Explanation:**
    *   Initial state: |00000>.
    *   After `X(q[0])` and `X(q[2])`: Sets q[0] and q[2] to |1>, resulting in |00101>.
    *   After `Toffoli(q[0], q[2], q[4])`: Since both q[0] and q[2] are |1>, q[4] flips to |1>. State is |10101>.
    *   After `CNOT(q[0], q[2])`: q[0] is |1>, so q[2] flips to |0>. State is |10100>.
    *   After `CNOT(q[1], q[3])`: q[1] is |0>, so q[

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Parametric variant of isqEval/276. Dimension: predict probabilities for reference circuit.'}

## isqTrain/97

- task_id: `isqTrain/97`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `superposition`
- source: `isq_train_cot`
- dataset_index: `815`

### Prompt

Implement a quantum circuit in isQ: implements the gate_decomposition pattern with modified rotation parameters (pi4_to_pi6). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

Step 1: Analyze the user's request.
- Goal: Create a reasoning section for an isQ quantum program.
- The program implements a `gate_decomposition` pattern with modified rotation parameters (`pi4_to_pi6`).
- The isQ code applies H gates to 2 qubits, a cost unitary using CNOT-Rz(pi/2)-CNOT, a mixing unitary using Rx(pi/6) on both qubits, and measures both.
- predicted output probabilities are given: {|00>: ~0.4665, |01>: ~0.0335, |10>: ~0.0335, |11>: ~0.4665}.
- The reasoning should explain the goal, qubits/measured qubits, step-by-step state evolution using Dirac notation, and why the probabilities match.
- Length constraint: 3-15 lines.
- Output format: ONLY the reasoning section starting with "## Reasoning". NO isQ code blocks.

Step 2: Trace the quantum state evolution.
- Qubits: 2, q[0] and q[1]. Measured: both.
- Initial state: |00>
- H(q[0]), H(q[1]) -> |00> -> (1/2)(|00> + |01> + |10> + |11>) = |++>
- CNOT(q[0], q[1]) -> (1/2)(|00> + |11> + |10> + |01>) -- wait, CNOT on |00> is |00>, on |01> is |01>, on |10> is |11>, on |11> is |10>. So CNOT(|++>) = 1/sqrt(2)(|00> + |11>) -- wait no.
Let's re-evaluate CNOT on |++>.
|++> = 1/2 (|0>(|0>+|1>) + |1>(|0>+|1>))
CNOT applies X to target if control is |1>.
So |0>(|0>+|1>) remains |0>(|0>+|1>).
|1>(|0>+|1>) becomes |1>(|1>+|0>) = |1>(|0>+|1>).
So CNOT(|++>) = |++> = (1/2)(|00> + |01> + |10> + |11>).
Wait! Let's check CNOT matrix on |++>.
|++> is an eigenstate of CNOT with eigenvalue +1.
Wait, no. CNOT(c, t) on |c>|t>.
If c=0, t unchanged. If c=1, t flipped.
|+> = 1/sqrt(2)(|0>+|1>).
|++> = 1/2 (|00> + |01> + |10> + |11>)
CNOT: |00>->|00>, |01>->|01>, |10>->|11>, |11>->|10>.
Resulting state: 1/2(|00> + |01> + |11> + |10>) = |++>.
Yes, CNOT leaves |++> unchanged!
Wait, let me double check.
|00> -> |00>
|01> -> |01>
|10> -> |11>
|11> -> |10>
So |00>+|01>+|10>+|11> -> |00>+|01>+|11>+|10> = |++>.
Correct.

- Rz(pi/2, q[1]):
State is |++>. This is equivalent to (|0>+|1>) \otimes (|0>+|1>) / 2.
Wait, Rz on q[1] affects the |0> and |1> components of q[1].
Rz(pi/2) on |0> is |0>, on |1> is exp(j*pi/2)|1> = j|1>.
So Rz(pi/2) on |+> gives (|0> + j|1>)/sqrt(2).
Let's call this state |R> or similar. Specifically, it's the right circular polarization eigenstate.
So the state after Rz is |+>|R> = 1/2 (|00> + j|01> + |10> + j|11>).

- CNOT(q[0], q[1]):
Let's apply CNOT to 1/2 (|00> + j|01> + |10> + j|11>).
|00> -> |00>
j|01> -> j|01>
|10> -> |11>
j|11> -> j|10>
So state becomes 1/2 (|00> + j|01> + |11> +
