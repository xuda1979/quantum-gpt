# ISQ training COT RAG corpus: quantum_algorithms shard 151

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3795

- task_id: `isqTrain/3795`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `interference`, `isq_syntax_oracle`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `2565`

### Prompt

Help me write isQ code that Deutsch-Jozsa for a 3-input balanced oracle with truth table [0, 1, 1, 0, 0, 1, 1, 0]. Use for loops for Hadamard application. Measure all 4 qubits.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Deutsch-Jozsa for a 3-input balanced oracle $f$ with truth table `[0, 1, 1, 0, 0, 1, 1, 0]`.
    *   The expected outcome states: `q` array of size 4.
    *   Action required: Generate the "Reasoning" section only.
    *   Constraint: Start with "## Reasoning", 3-15 lines, use Dirac notation, no code blocks, no isQ code.

2.  **Understand the Circuit (Deutsch-Jozsa Algorithm):**
    *   **Goal:** Determine if a 3-bit function $f$ is constant or balanced using a single query.
    *   **Qubits:** 4 qubits total ($q_0, q_1, q_2$ for input, $q_3$ for output).
    *   **Initial State:** $|0000\rangle$.
    *   **Step 1 (Output prep):** X on $q_3$, then H on $q_3$.
        *   $|0000\rangle \xrightarrow{X_3} |0001\rangle \xrightarrow{H_3} |000\rangle \otimes |-\rangle$.
    *   **Step 2 (Superposition):** Hadamard on $q_0, q_1, q_2$.
        *   $|000\rangle \otimes |-\rangle \xrightarrow{H^{\otimes 3}} \frac{1}{2\sqrt{2}} \sum_{x=0}^{7} |x\rangle \otimes |-\rangle$.
    *   **Step 3 (Oracle):** The oracle $f(x)$ is balanced (specifically $f(x) = x_1 \oplus x_2$, since $f(000)=0, f(001)=1, f(010)=1, f(011)=0$, etc. wait, let me check the table: 000=0, 001=1, 010=1, 011=0, 100=0, 101=1, 110=1, 111=0. This is $f(x) = x_0 \oplus x_1$, wait no. For $x_0x_1x_2$: 000->0, 001->1, 010->1, 011->0, 100->0, 101->1... it actually doesn't matter what the exact classical form is, we just know it's balanced so the phase kickback applies $(-1)^{f(x)}$).
        *   State becomes: $\frac{1}{2\sqrt{2}} \sum_{x=0}^{7} (-1)^{f(x)} |x\rangle \otimes |-\rangle$.
    *   **Step 4 (Final Hadamard):** Apply $H^{\otimes 3}$ to $q_0, q_1, q_2$.
        *   The input register becomes $\sum_y \left( \frac{1}{2\sqrt{2}} \sum_x (-1)^{f(x)} (-1)^{x \cdot y} \right) |y\rangle \otimes |-\rangle$.
        *   For any balanced function, $y=000$ has amplitude 0.
        *   For this specific balanced function, the amplitude is concentrated on some specific states. Actually, looking at the predicted output in the prompt: `Expected measurement probabilities: {|0110>: 0.5, |0111>: 0.5}`.
        *   Wait, The predicted output $|0110\rangle$ and $|0111\rangle$?
        *   Let's re-evaluate the oracle table.
            Table: $f(0,0,0)=0, f(0,0,1)=1, f(0,1,0)=1, f(0,1,1)=0, f(1,0,0)=0, f(1,0,1)=1, f(1,1,0)=1, f(1,1,1)=0$.
            Wait, $f(x)$ only depends on $x_1$ and $x_2$!
            If it only depends on $x_1 \oplus x_2$, then $x_0$ doesn't matter.
            Since $x_0$ doesn't matter, applying $H$ on $x_0$ gives a superposition over $x_0=0$ and $x_0=1$.
            So the final state in binary is $

## isqQA/quantum_algorithms/113_principle_advantage

- task_id: `isqQA/quantum_algorithms/113_principle_advantage`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `principle_advantage`, `algorithm`, `QFT与经典FFT的对比`
- source: `qa_pipeline`
- dataset_index: `1680`

### Prompt

请深入对比经典快速傅里叶变换（FFT）与量子傅里叶变换（QFT）在宏观原理和计算复杂度上的根本差异。量子计算是如何在这个变换过程中实现指数级加速的？其背后的核心物理机制（量子态叠加与演化）是如何发挥作用的？请详细解析其优势来源，并使用isQ语言编写一个3量子比特的QFT完整线路代码。

### Reference answer

<thinking>
1. 分析宏观原理：经典FFT是对N个显式复数数据点的序列进行操作，而QFT是对n个量子比特构成的2^n个概率幅进行操作。
2. 分析时间复杂度：经典FFT处理N=2^n个点需要O(N log N)步。QFT只需要O(n^2)个量子门，因为n=log2(N)，所以QFT相对于数据规模N的时间复杂度为O((log N)^2)，实现了指数级加速。
3. 量子加速来源：量子并行性。一个作用于n个量子比特系统的酉变换可以同时作用于2^n个振幅，这种指数级的维度扩张是经典计算机无法企及的。
4. 编写isQ代码：实现3量子比特QFT。需要H门和受控相位门（S门相当于R2，T门相当于R3）。最后需要通过3个CNOT门实现等效的SWAP操作来反转比特顺序。
</thinking>

经典快速傅里叶变换（FFT）与量子傅里叶变换（QFT）在底层数学逻辑上具有一致性，但在物理原理、信息载体和计算复杂度上存在根本差异。

1. 宏观原理对比：
经典FFT是对一个包含N个复数的显式向量进行离散傅里叶变换，将信号从时域（或空域）转换到频域。它利用旋转因子的对称性和周期性，将长序列的DFT分解为短序列的DFT。在经典计算中，数据是可见且独立存储的。相比之下，QFT并不是提取显式的信号频率，而是对一个包含n个量子比特的量子态进行酉变换。这个量子态隐式地包含N=2^n个基态的概率幅，QFT直接对这些概率幅进行变换，完成干涉与重组。

2. 时间复杂度对比：
经典FFT处理N=2^n个数据点的时间复杂度为O(N log N)。而对于量子傅里叶变换，处理同样维度的2^n个隐含状态振幅，所需的量子门数量仅为O(n^2)。因为n = log2(N)，所以QFT的时间复杂度可以表示为O((log N)^2)。相较于经典FFT，QFT在状态空间规模N上实现了从多项式级到对数级的跨越，展现出了指数级别的计算加速。

3. 量子加速来源与核心物理机制：
QFT指数级加速的根本来源是“量子态叠加与演化带来的天然并行性”。在经典系统中，处理N个数据点必须依赖足够大的内存和时序电路。但在量子系统中，对处于叠加态的单个量子比特执行一个单比特量子门，由于张量积的数学结构，实际上是对该系统所有2^n个振幅同时进行了线性变换。这种指数级的状态空间膨胀并不消耗额外的物理操作时间，从而实现了指数加速。
但必须强调的是，这种加速不能直接用来“快速处理庞大的经典信号数据”，因为量子态的概率幅无法被全部直接读取（测量会导致波函数坍缩）。QFT的优势必须嵌入在更广泛的量子算法中（如Shor算法、量子相位估计），通过巧妙的干涉放大特定概率幅，来提取全局的结构特征（如周期性）。

以下是使用isQ语言编写的3量子比特QFT完整线路代码：

```isq
import std;

qbit q[3];

procedure main() {
    // 对第一个量子比特 q[0] 进行操作
    H(q[0]);
    ctrl @[q[1]] S(q[0]); // 受控S门 (相位 pi/2)
    ctrl @[q[2]] T(q[0]); // 受控T门 (相位 pi/4)

    // 对第二个量子比特 q[1] 进行操作
    H(q[1]);
    ctrl @[q[2]] S(q[1]); // 受控S门

    // 对第三个量子比特 q[2] 进行操作
    H(q[2]);

    // 量子傅里叶变换最后需要反转量子比特的顺序
    // 使用CNOT门组合来代替SWAP门，交换 q[0] 和 q[2]
    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
}
```

## isqTrain/98

- task_id: `isqTrain/98`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `5425`

### Prompt

帮我写一个isQ程序：implements a variant of the bell_state_preparation pattern using q[3] -> q[4]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

Let me analyze the given isQ program step by step.

The program has 4 qubits: q[0], q[1], q[2], q[3]

Step 1: X(q[0]) - Initialize q[0] to |1>
State: |1000>

Step 2: H(q[1]) - Apply Hadamard to q[1]
State: (1/√2)(|1000> + |1010>)

Step 3: CNOT(q[1], q[2]) - Create EPR pair between q[1] and q[2]
State: (1/√2)(|1000> + |1011>)

Wait, let me reconsider. CNOT with q[1] as control and q[2] as target:
When q[1] is |0>, q[2] stays |0>
When q[1] is |1>, q[2] flips from |0> to |1>

State: (1/√2)(|1000> + |1110>)

Wait, I need to be more careful about the ordering. Let me use the convention where the leftmost bit is q[0].

Initial state: |0000>

After X(q[0]): |1000>

After H(q[1]): (1/√2)(|1000> + |1100>)

After CNOT(q[1], q[2]): (1/√2)(|1000> + |1110>)

Step 4: CNOT(q[0], q[1]) - Alice's operation
When q[0] is |1>, flip q[1]
State: (1/√2)(|0100> + |0010>)

Wait, let me redo this more carefully.

After X(q[0]): |1000⟩

After H(q[1]): (1/√2)(|1000⟩ + |1100⟩)

After CNOT(q[1], q[2]): 
- |1000⟩: q[1]=0, so q[2] stays 0 → |1000⟩
- |1110⟩: q[1]=1, so q[2] flips 0→1 → |1110⟩

Wait, that's not right either. Let me be more careful about the bit ordering.

Let me write |q[0]q[1]q[2]q[3]⟩

Initial: |0000⟩

X(q[0]): |1000⟩

H(q[1]): (1/√2)(|1000⟩ + |1100⟩)

CNOT(q[1], q[2]): 
- |1000⟩: q[1]=0, q[2] stays 0 → |1000⟩
- |1100⟩: q[1]=1, q[2] flips to 1 → |1110⟩

State: (1/√2)(|1000⟩ + |1110⟩)

CNOT(q[0], q[1]):
- |1000⟩: q[0]=1, q[1] flips 0→1 → |1100⟩
- |1110⟩: q[0]=1, q[1] flips 1→0 → |1010⟩

State: (1/√2)(|1100⟩ + |1010⟩)

H(q[0]):
H|1⟩ = |−⟩ = (1/√2)(|0⟩ − |1⟩)

State: (1/2)(|0100⟩ + |1100⟩ − |0010⟩ + |1010⟩)

Wait, I need to apply H to q[0] only.

(1/√2)(|1100⟩ + |1010⟩)

H on q[0]:
|1⟩ → (1/√2)(|0⟩ − |1⟩)

So:
(1/√2) × (1/√2)(|0100⟩ − |1100⟩ + |0010⟩ − |1010⟩)

Wait, let me be more careful:

State = (1/√2)(|1⟩⊗|1⟩⊗|0⟩⊗|0⟩ + |1⟩⊗|0⟩⊗|1⟩⊗|0⟩)

After H on q[0]:
= (1/√2)((1/√2)(|0⟩−|1⟩)⊗|1⟩⊗|0⟩⊗|0⟩ + (1/√2)(|0⟩−|1⟩)⊗|0⟩⊗|1⟩⊗|0⟩)

Hmm, wait. The state before H(q[0]) is:
(1/√2)(|1100⟩ + |1010⟩)

When we apply H to q[0]:
|1100⟩ → H on first q

## isqQA/quantum_algorithms/91_math_derivation

- task_id: `isqQA/quantum_algorithms/91_math_derivation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `math_derivation`, `algorithm`, `BV算法的不同隐藏字符串实现`
- source: `qa_pipeline`
- dataset_index: `78`

### Prompt

请以长度为3的隐藏字符串 s=101 为例，详细推导Bernstein-Vazirani (BV) 算法在量子线路中各个阶段的量子态演化过程，并使用isQ语言编写实现该特定隐藏字符串预言机的完整量子程序。

### Reference answer

<think>
Bernstein-Vazirani (BV) 算法的核心在于利用量子叠加与相位反冲效应，将经典需要 $n$ 次查询的问题转化为仅需 1 次。对于给定的隐藏字符串 $s=101$，推导与编程思路分为四个关键步骤：

首先，初始化系统，将3个输入比特置为 $|0\rangle$，辅助比特置为 $|1\rangle$。接着，对所有比特施加 Hadamard 门，使输入比特进入均匀叠加态，辅助比特变为 $|-\rangle$ 态。这一步为相位反冲创造了条件。

随后，构建预言机。由于 $s=101$（即 $s_0=1, s_1=0, s_2=1$），函数 $f(x)$ 实际上是比特 $x_0$ 与 $x_2$ 的异或。当辅助比特处于 $|-\rangle$ 态时，这种异或计算会转化为输入态上的相位因子 $(-1)^{x_0 \oplus x_2}$，从而将隐藏字符串的信息编码进量子态的相位中。

最后，对输入比特再次施加 Hadamard 门。由于 $H$ 门的干涉效应，非目标态的相位会相互抵消，状态会精确坍缩为 $|101\rangle$。在 isQ 编程实现时，逻辑同样清晰：只需根据 $s=101$ 的非零位，在量子程序中对第0、第2个输入比特与辅助比特之间添加受控非（CNOT）门即可完成预言机构建。
</think>

<LM>
Bernstein-Vazirani (BV) 算法旨在寻找一个隐藏字符串 $s \in \{0,1\}^n$。对于预言机 $U_f$，其作用为 $f_s(x) = x \cdot s \pmod 2$。下面我们以 $n=3$ 且隐藏字符串 $s=101$ 为例，严密推导各阶段的量子态演化。

1. **初始态**：
系统包含3个输入量子比特和1个辅助比特，初始态为：
$$|\psi_0\rangle = |000\rangle \otimes |1\rangle$$

2. **Hadamard变换**：
对所有量子比特施加Hadamard门。辅助比特 $|1\rangle$ 变为 $|-\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}$。前三个比特形成均匀叠加态：
$$|\psi_1\rangle = \frac{1}{\sqrt{2^3}} \sum_{x=0}^{7} |x\rangle \otimes \frac{|0\rangle - |1\rangle}{\sqrt{2}}$$

3. **预言机 $U_f$ 作用**：
预言机将态映射为 $|x\rangle|y\rangle \mapsto |x\rangle|y \oplus f_s(x)\rangle$。由于辅助比特处于 $|0\rangle - |1\rangle$ 的叠加态，这会导致相位反跳：
$$|\psi_2\rangle = \frac{1}{\sqrt{2^3}} \sum_{x=0}^{7} (-1)^{x \cdot s} |x\rangle \otimes \frac{|0\rangle - |1\rangle}{\sqrt{2}}$$
对于 $s=101$，如果输入 $x=101$，则 $x \cdot s = 1 \cdot 1 + 0 \cdot 0 + 1 \cdot 1 = 2 \equiv 0 \pmod 2$，相位为 $+1$；若 $x=001$，则 $x \cdot s = 1$，相位为 $-1$。

4. **二次Hadamard变换**：
抛开辅助比特，对前3个量子比特再次施加 $H^{\otimes 3}$。已知 $H^{\otimes n}|x\rangle = \frac{1}{\sqrt{2^n}} \sum_{z} (-1)^{x \cdot z} |z\rangle$，代入得：
$$|\psi_3\rangle = \frac{1}{8} \sum_{x=0}^{7} \sum_{z=0}^{7} (-1)^{x \cdot s} (-1)^{x \cdot z} |z\rangle = \sum_{z=0}^{7} \left( \frac{1}{8} \sum_{x=0}^{7} (-1)^{x \cdot (s \oplus z)} \right) |z\rangle$$
根据正交性，内层求和当且仅当 $z = s$ 时为1，否则为0。因此系统坍缩为：
$$|\psi_3\rangle = |s\rangle = |101\rangle$$

5. **测量**：
此时对前3个量子比特进行测量，将以100%的概率得到隐藏字符串 `101`。

以下是使用isQ语言实现上述过程的代码，通过受控非门(CNOT)构造 $s=101$ 的预言机：

```isq
import std;

qbit q[4]; // q[0..2]为输入比特，q[3]为辅助比特

procedure main() {
    // 初始化辅助比特为 |-> 态
    X(q[3]);
    H(q[3]);

    // 对输入比特施加Hadamard门
    for i in 0:3 {
        H(q[i]);
    }

    // 构建 s = 101 的预言机 U_f
    // s[0]=1, s[1]=0, s[2]=1
    CNOT(q[0], q[3]);
    // s[1]=0，无需操作
    CNOT(q[2], q[3]);

    // 对输入比特再次施加Hadamard门
    for i in 0:3 {
        H(q[i]);
    }

    // 测量前三个比特以获取隐藏字符串
    for i in 0:3 {
        int r = M(q[i]);
    }
}
```
</LM>

## isqTrain/2683

- task_id: `isqTrain/2683`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_oracle`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4880`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
oracle bool[4] g(bool a[4]) {
    bool res[] = [a[0], a[1], a[2], false];
    return res;
}
qbit q[4], res[4];

procedure main(){
    H(q);
    g(q, res);
    H(q); 
    print M(q);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Input:** An isQ program containing 4 qubits `q`, 4 qubits `res`, an oracle `g` that computes `res = [a[0], a[1], a[2], false]`, applied via `g(q, res);`, and measurements on `q` after `H(q); g(...); H(q);`.
    *   **Format:** Concise reasoning (3-15 lines), starting with "## Circuit Analysis".
    *   **Content:** Steps of operations, state evolution, final state, and probability distribution (JSON array of floats).
    *   **Syntax Reference:** Provided.
    *   **predicted output:** A JSON array representing the probability distribution based on the given reference: {'0000': 0.125, ..., '0111': 0.125}.

2.  **Analyze the Circuit:**
    *   Initial state: $|0\rangle^{\otimes 4}_q \otimes |0\rangle^{\otimes 4}_{res}$
    *   `H(q)`: Applies Hadamard to each of the 4 `q` qubits. State: $\frac{1}{4} \sum_{x=0}^{15} |x\rangle_q |0\rangle_{res}$
    *   `g(q, res)`: Computes the oracle function. For a state $|x\rangle|0\rangle$, it maps to $|x\rangle|g(x)\rangle$. Specifically, the last qubit of `res` gets $0 \oplus 0 = 0$ (since the oracle's last output is always `false`). The first three get $x_0, x_1, x_2$. State becomes $\frac{1}{4} \sum_{x=0}^{15} |x\rangle_q |x_0, x_1, x_2, 0\rangle_{res}$.
    *   `H(q)`: Applies Hadamard to the 4 `q` qubits.
    *   We need the state of `q` before measurement. Notice that the oracle `g` does *not* change `q`, it only writes to `res`. Wait, is it phase oracle or state oracle?
        *   Standard isQ `oracle` computes boolean arrays to boolean arrays. `g(q, res)` means evaluating the oracle function. Actually, in isQ, if it modifies `res` based on `q`, it's a standard reversible computation. But usually, if it acts as a unitary, `|x\rangle|y\rangle \to |x\rangle|y \oplus g(x)\rangle`.
        *   Wait, is `res` entangled with `q`? Yes.
        *   The Hadamard transform on `q` acts on the joint state: $\frac{1}{4} \sum_{x} |x\rangle |x_0, x_1, x_2, 0\rangle$.
        *   Applying $H^{\otimes 4}$ to the `q` register: $\frac{1}{4} \sum_{x} \left( \frac{1}{4} \sum_{z} (-1)^{x \cdot z} |z\rangle \right) |x_0, x_1, x_2, 0\rangle$.
        *   The measurement is *only* on `q`. So we trace out `res`, or simply look at the reduced density matrix of `q` after the second `H(q)`.
        *   Let's trace out `res`: $\rho_q = \text{Tr}_{res} |\psi\rangle\langle\psi|$. Since $g$ is a bijective function for the first 3 bits (actually, $g(x) = (x_0, x_1, x_2, 0)$), the `res` states for different $x$ are perfectly distinguishable (orthogonal).
        *   Wait, $x$ has 4 bits, $x = x_0 x_1 x_2 x_3$. The function is $g(x) = (x_0, x_1, x_2, 0)$. Notice that $x_3$ is ignored in the output!
        *   So for $x$ and $x'$, if they differ only in $x_3$, they produce the *same* `res` state.
        *   Let's write $x = (y, x_3)$ where $y \in \{0,1\}^3$ and $x_3 \in \{0,1\}$. $g(x) = (y, 0)$.
        *

### Reference answer

{'predicted_probs': {'0000': 0.12500000000000003, '0001': 0.12500000000000003, '0010': 0.12500000000000003, '0011': 0.12500000000000003, '0100': 0.12500000000000003, '0101': 0.12500000000000003, '0110': 0.12500000000000003, '0111': 0.12500000000000003}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqQA/quantum_algorithms/135_principle_advantage

- task_id: `isqQA/quantum_algorithms/135_principle_advantage`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `principle_advantage`, `algorithm`, `Swap测试`
- source: `qa_pipeline`
- dataset_index: `698`

### Prompt

在量子机器学习和量子算法设计中，Swap测试是一种极其重要的基础子程序，常用于比较两个量子态的相似度。请详细阐述Swap测试的宏观原理，并将其与经典的内积估计进行时间复杂度对比，深入分析其背后的量子加速来源。此外，请使用isQ语言编写一个通用的Swap测试代码，要求能够处理N个量子比特的状态比较。

### Reference answer

Swap测试是量子计算中用于估计两个量子态重叠度（即内积绝对值的平方）的核心子程序。

宏观原理：该算法引入一个初始化为|0⟩的辅助量子比特。首先，对辅助比特施加Hadamard门，使其进入叠加态。接着，以辅助比特为控制位，对两个目标量子态寄存器执行受控交换操作。然后再对辅助比特施加一次Hadamard门并测量。根据量子干涉效应，辅助比特的最终状态包含了目标量子态之间的重叠信息。具体而言，测量辅助比特得到0的概率为 P(0) = (1 + |⟨ψ|φ⟩|²) / 2。通过多次重复执行该电路并统计0出现的频率，我们可以估算出这两个量子态的保真度。

时间复杂度对比与量子加速来源：在经典计算中，若要比较两个n-量子比特系统的状态向量，我们需要完全读取或重构这两个系统的波函数。由于状态空间的维度呈指数增长（2^n），经典读取和内积计算的时间复杂度为 O(2^n)。而在量子Swap测试中，我们无需读取整个状态空间。对于n-量子比特系统，我们仅需执行n个受控交换操作，其物理线路的深度复杂度仅为 O(n)。虽然为了达到给定的误差精度 ε 需要进行 O(1/ε²) 次重复测量，但这部分开销独立于系统的规模 n。

这种从指数级 O(2^n) 到线性级 O(n) 的显著加速，其根本来源是量子态的叠加性和干涉特性。受控交换操作直接作用并干涉了处于高维希尔伯特空间中的概率幅，将高维内积的相位信息高效地转移到了单比特的观测概率上，成功规避了经典计算中不可避免的“维数灾难”。

以下是使用isQ语言实现的N-qubit量子态的Swap测试代码。由于语法约束禁止直接使用SWAP门，我们通过CNOT和Toffoli门构建了标准的Fredkin（受控交换）门来实现等效逻辑：

import std;

int N = 3;
qbit ancilla[1];
qbit psi[N];
qbit phi[N];

procedure main() {
    // 1. 假设态已由前置子程序制备完毕

    // 2. Swap测试：辅助比特施加H门
    H(ancilla[0]);

    // 3. 以辅助比特为控制，对两寄存器执行受控SWAP
    for i in 0:N {
        // 使用CNOT和Toffoli合成受控SWAP（Fredkin门）
        CNOT(phi[i], psi[i]);
        Toffoli(ancilla[0], psi[i], phi[i]);
        CNOT(phi[i], psi[i]);
    }

    // 4. 辅助比特再次施加H门
    H(ancilla[0]);

    // 5. 测量辅助比特
    M(ancilla[0]);
}

## isqExpand/algo/192

- task_id: `isqExpand/algo/192`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `VQE`, `ansatz`, `CNOT`, `entanglement`, `two_qubit_gate`
- source: `isq_expansion`
- dataset_index: `4994`

### Prompt

The following isQ code implements a simple VQE ansatz for a 2-qubit system. It applies Ry(π/3) on both qubits followed by a CNOT entangling gate. However, the CNOT direction is reversed: the control and target are swapped (q[1]→q[0] instead of the intended q[0]→q[1]). Fix the CNOT direction so the circuit produces the correct ansatz state. Report the expected measurement probabilities for the corrected circuit.

### Chain-of-thought reasoning

Step 1: After Ry(π/3, q[0]) and Ry(π/3, q[1]), each qubit is in state cos(π/6)|0⟩ + sin(π/6)|1⟩. Since cos(π/6)=√3/2 and sin(π/6)=1/2, the joint state is (3/4)|00⟩ + (√3/4)|01⟩ + (√3/4)|10⟩ + (1/4)|11⟩. Step 2: With correct CNOT(q[0],q[1]) where q[0] is control and q[1] is target: |00⟩→|00⟩, |01⟩→|01⟩, |10⟩→|11⟩, |11⟩→|10⟩. Result: (3/4)|00⟩ + (√3/4)|01⟩ + (1/4)|10⟩ + (√3/4)|11⟩. Step 3: Probabilities: P(00)=(3/4)²=9/16=0.5625, P(01)=(√3/4)²=3/16=0.1875, P(10)=(1/4)²=1/16=0.0625, P(11)=(√3/4)²=3/16=0.1875. Step 4: The buggy CNOT(q[1],q[0]) would give different probabilities: P(00)=0.5625, P(01)=0.0625, P(10)=0.1875, P(11)=0.1875, which swaps P(01) and P(10). Step 5: The fix changes CNOT(q[1],q[0]) to CNOT(q[0],q[1]).

## isqExpand/algo/43

- task_id: `isqExpand/algo/43`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `qpe`, `z_gate`, `inverse_qft`, `phase_estimation`
- source: `isq_expansion`
- dataset_index: `1098`

### Prompt

Create an isQ quantum circuit that implements Quantum Phase Estimation (QPE) to estimate the phase of the Z gate acting on its eigenstate |1>. Use 2 phase qubits (q[0] as MSB, q[1] as LSB) and 1 eigenstate qubit (q[2]). The Z gate has eigenvalue -1 for |1>, corresponding to phase 1/2. Implement the inverse QFT on the phase register and SWAP the phase qubits using 3 CNOT gates. Only measure the phase register qubits q[0] and q[1].

### Chain-of-thought reasoning

## Reasoning
Goal: QPE to estimate phase of Z gate on eigenstate |1>.

Z|1> = -|1> = e^{i*pi}|1>, so phase phi = pi/(2*pi) = 1/2.

With 2 phase qubits, the result encodes phi * 2^2 = 2 = binary |10>.

Circuit design:
1. H(q[0]), H(q[1]): phase qubits in superposition
2. X(q[2]): prepare eigenstate |1>
3. Controlled-U operations (q[0]=MSB, q[1]=LSB):
   - q[0] controls U^{2^1} = Z^2 = I (skip, identity)
   - q[1] controls U^{2^0} = Z^1 = Z: ctrl @[q[1]] Z(q[2])
4. Inverse QFT on 2 qubits:
   - H(q[0])
   - ctrl inv S(q[1], q[0]) — q[1] controls S^dag on q[0]
   - H(q[1])
   - SWAP(q[0], q[1]) via 3 CNOTs
5. Measure q[0], q[1]

After ctrl Z from q[1], q[1] picks up the phase. The inverse QFT and SWAP produce |10> with probability 1.

## isqTrain/2702

- task_id: `isqTrain/2702`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_procedures`, `measurement_order`
- source: `isq_train_cot`
- dataset_index: `4584`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

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

1. **Operations applied:**
   - H on q[0], creating superposition
   - CNOT(q[0], q[1]) for i=1
   - CNOT(q[1], q[2]) for i=2
   - CNOT(q[2], q[3]) for i=3
   - Measurements on all 4 qubits

2. **State evolution:**
   - Initial: |0000⟩
   - After H(q[0]): (|0000⟩ + |1000⟩)/√2
   - After CNOT(q[0], q[1]): (|0000⟩ + |1100⟩)/√2
   - After CNOT(q[1], q[2]): (|0000⟩ + |1110⟩)/√2
   - After CNOT(q[2], q[3]): (|0000⟩ + |1111⟩)/√2

3. **Final state:** (|0000⟩ + |1111⟩)/√2 — a 4-qubit GHZ state.

4. **Predicted probability distribution:** The equal superposition of |0000⟩ and |1111⟩ gives:
   - P(0000) = 0.5
   - P(0001) = 0
   - P(0010) = 0
   - P(0011) = 0
   - P(0100) = 0
   - P(0101) = 0
   - P(0110) = 0
   - P(0111) = 0
   - P(1000) = 0
   - P(1001) = 0
   - P(1010) = 0
   - P(1011) = 0
   - P(1100) = 0
   - P(1101) = 0
   - P(1110) = 0
   - P(1111) = 0.5

### Reference answer

{'predicted_probs': {'0000': 0.5, '1111': 0.5}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/857

- task_id: `isqTrain/857`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `boolean_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4642`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
qbit q[2];

procedure main() {
    // Set input x = 1
    X(q[0]);
    // Reciprocal: 1/1 = 1
    // Set output to 1 when input is 1
    CNOT(q[0], q[1]);
    // Measure the reciprocal output
    M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes two qubits, `q[0]` and `q[1]`, to the state |00>.
2. `X(q[0])` flips the first qubit, evolving the state to |10>.
3. `CNOT(q[0], q[1])` applies an X gate to `q[1]` because `q[0]` is in the state |1>, changing the state to |11>.
4. Finally, `M(q[1])` measures the target qubit `q[1]`.

Predicted probability distribution: {|1>: 1.0}

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Parametric variant of isqEval/294. Dimension: predict probabilities for reference circuit.'}
