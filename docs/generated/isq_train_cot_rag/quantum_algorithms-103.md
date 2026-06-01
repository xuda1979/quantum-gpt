# ISQ training COT RAG corpus: quantum_algorithms shard 103

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/2851

- task_id: `isqTrain/2851`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2404`

### Prompt

请用isQ语言编写一个量子电路：creates a CNOT sandwich with Hadamard. Use the appropriate sequence of gates on 2 qubits and measure both.

Requirements:
- Declare `qbit q[2];` at global scope.
- Use `procedure main()` as entry point.
- Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a CNOT sandwiched by Hadamards (with an initial X to avoid trivial all-equal superposition).
2. **Qubits**: 2 qubits `q[0]` and `q[1]`, both measured.
3. **State evolution**:
   - |00⟩ → X(q[0]) → |10⟩
   - → H(q[0]) → (|0⟩−|1⟩)/√2 ⊗ |0⟩ = (|00⟩−|10⟩)/√2
   - → CNOT(q[0],q[1]) → (|00⟩−|11⟩)/√2
   - → H(q[0]) → (|00⟩+|10⟩−|01⟩+|11⟩)/2
4. **Probabilities**: Each basis state has amplitude 1/2, giving probability |1/2|² = 1/4 = 0.25 for each of |00⟩, |01⟩, |10⟩, |11⟩.

## isqQA/quantum_algorithms/43_principle_advantage

- task_id: `isqQA/quantum_algorithms/43_principle_advantage`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `principle_advantage`, `algorithm`, `量子计数算法`
- source: `qa_pipeline`
- dataset_index: `1015`

### Prompt

请深入解析量子计数算法的核心原理，并说明其相比于经典计数方法在时间复杂度上的优势，以及这种量子加速的根本来源是什么。

### Reference answer

量子计数算法是量子相位估计和Grover搜索算法的巧妙结合，主要用于估计无结构数据库中目标解的数量（通常记为M）。

**宏观原理：**
在Grover搜索算法中，我们构造了一个Grover算子 G = (2|ψ⟩⟨ψ| - I)O，其中O是预言机，|ψ⟩是均匀叠加态。Grover算子在由目标解子空间和非目标解子空间张成的二维平面内表现为一个旋转操作。如果我们把G作用于这个平面内的本征态，其对应的本征值具有 e^{i2πω} 的形式。数学推导表明，相位ω与目标解的数量M满足紧密的数学关系：sin²(πω) = M / N（其中N是数据库总状态数）。
量子计数算法正是利用了这一性质。它以量子相位估计算法（QPE）为核心框架，将均匀叠加态作为输入态，而将Grover算子G作为QPE中需要进行受控幂次操作的酉算子。通过执行量子相位估计线路，测量并提取出相位估计值ω̃。在获得ω̃后，只需利用简单的代数关系 M̃ = N sin²(πω̃) 即可计算出目标解数量的高精度估计值。

**时间复杂度对比：**
在经典计算中，要估计一个大小为N的无结构数据库中满足特定条件的元素数量M，没有任何比遍历或随机采样更好的通用方法。为了得到一个误差在合理范围内的估计值，经典概率算法的时间复杂度为 O(N)。
相比之下，量子计数算法展现出了极大的优势。其查询预言机O的次数仅需 O(√N) 即可完成计数任务。更精确地说，如果要求相对误差为ε，那么量子计数所需的查询复杂度为 O((1/ε)√(N/M))。这证明量子计数在解决此类问题时，相对于经典最优算法实现了平方级的显著加速。

**量子加速来源：**
这种平方级加速的根本来源在于**量子态的相干叠加与干涉特性**，以及**Grover迭代在希尔伯特空间中的几何旋转性质**。
经典算法只能串行地逐个检验元素，每次获取的信息极其局域化。而量子算法通过将初态制备为包含所有可能状态的均匀叠加，使得每一次对预言机的查询实际上都同时作用于所有 2ⁿ 个基底状态。更关键的是，Grover算子通过相位反转和关于均值的反转操作，在全局状态空间中引发了精妙的量子干涉。这种干涉导致非目标态的概率幅向目标态转移，且转移的速度（即振荡频率）直接由比例 M/N 决定。
量子相位估计算法随后利用量子傅里叶逆变换的强大能力，以极高的效率提取出隐藏在Grover动力学演化中的全局相位信息（即振荡频率ω）。因此，量子计数算法之所以能实现 O(√N) 的加速，是因为它避开了经典的逐个枚举，转而利用量子的全局干涉模式来感知整体统计信息。

## isqTrain/4080

- task_id: `isqTrain/4080`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `129`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit q[3];

unit grover_oracle(qbit q[3]) {
    X(q[0]);
    ctrl CZ(q[0], q[1], q[2]);
    X(q[0]);
} deriving gate

unit grover_diffusion(qbit q[3]) {
    H(q[0]);
    H(q[1]);
    H(q[2]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    ctrl CZ(q[0], q[1], q[2]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    H(q[0]);
    H(q[1]);
    H(q[2]);
} deriving gate

procedure main() {
    H(q[0]); H(q[1]); H(q[2]);
    grover_oracle(q);
    grover_diffusion(q);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

This is a Grover's algorithm for 3 qubits. Let me trace through the circuit step by step.

Initial state: |000⟩

After H on all qubits: |+++⟩ = (1/2√2) Σ_{x=0}^{7} |x⟩

This is an equal superposition over all 8 basis states.

**Grover Oracle:**
The oracle does:
1. X(q[0]) - flips qubit 0
2. ctrl CZ(q[0], q[1], q[2]) - this is a controlled-controlled-Z, which applies Z to q[2] when both q[0] and q[1] are |1⟩. So this is essentially a double-controlled-Z (ctrl @[c1, c2] Z(target)) gate.
3. X(q[0]) - flips qubit 0 back

So the oracle marks states where q[0]=0, q[1]=1, q[2]=1? Let me think more carefully.

After X(q[0]), the state |xyz⟩ becomes |(x⊕1)yz⟩ = |x̄yz⟩.

Then double-controlled-Z (ctrl @[c1, c2] Z(target)) applies a phase of -1 when q[0]=1, q[1]=1, q[2]=1, i.e., to state |111⟩.

But we've flipped q[0], so the original state that gets the -1 phase is when x̄=1, y=1, z=1, meaning x=0, y=1, z=1, i.e., |011⟩.

So the oracle marks |011⟩ with a -1 phase.

**Grover Diffusion:**
The diffusion operator does H⊗3, then X⊗3, then double-controlled-Z (ctrl @[c1, c2] Z(target)), then X⊗3, then H⊗3.

This is the standard Grover diffusion operator which reflects about the mean.

After the oracle, the state is:
(1/2√2)(|000⟩ + |001⟩ + |010⟩ - |011⟩ + |100⟩ + |101⟩ + |110⟩ + |111⟩)

The amplitude of |011⟩ is -1/2√2 and all others are +1/2√2.

Now applying the diffusion operator:
- The mean amplitude is: (7 × 1/2√2 - 1/2√2)/8 = 6/(8 × 2√2) = 6/(16√2) = 3/(8√2)

The diffusion operator reflects each amplitude about the mean:
- For |011⟩: new amplitude = 2 × mean - old = 2 × 3/(8√2) - (-1/2√2) = 3/(4√2) + 1/(2√2) = 3/(4√2) + 2/(4√2) = 5/(4√2)

Wait, let me recalculate. The amplitudes after oracle:
Each state has amplitude 1/(2√2) except |011⟩ which has -1/(2√2).

Mean = (7 × 1/(2√2) - 1/(2√2))/8 = 6/(16√2) = 3/(8√2)

For the non-marked states:
new = 2 × 3/(8√2) - 1/(2√2) = 3/(4√2) - 1/(2√2) = 3/(4√2) - 2/(4√2) = 1/(4√2)

For |011⟩:
new = 2 × 3/(8√2) - (-1/(2√2)) = 3/(4√2) + 1/(2√2) = 3/(4√2) + 2/(4√2) = 5/(4√2)

Let me verify normalization:
7 × (1/(4√2))² + (5/(4√2))² = 7/(32) + 25/(32) = 32/32 = 1 ✓

So the probability of measuring |011⟩ is (5/(4√2))² = 25/32 ≈ 0.78125

And each other state has probability (1/(4√2))² = 1/32 ≈ 0.03125

So the most likely measurement outcome is 011.

Wait, let me double-check the oracle. The ctrl CZ with q[0], q[1] as controls and q[2] as target... Actually in isQ syntax, `ctrl CZ(q[0], q[1], q[2])` means q[0] and q[1] are controls, and q[2] is the target of CZ. But CZ is a two-qubit gate (control and target). With `ctrl` modifier adding one more control, this becomes a

### Reference answer

Dominant output states: |011> with probability ~0.78 each

## isqTrain/1395

- task_id: `isqTrain/1395`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `isq_syntax_multi_register`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1483`

### Prompt

帮我写一个isQ程序：the Bernstein-Vazirani algorithm to find the secret string s = 0001 (MSB first). Use 4 input qubits and 1 ancilla.

### Chain-of-thought reasoning

## Reasoning
1.  **Goal:** Implement the Bernstein-Vazirani algorithm to identify the secret binary string $s = 0001$.
2.  **Qubits:** 5 qubits total (4 input $q[0..3]$, 1 ancilla $anc[0]$); only the 4 input qubits are measured.
3.  **State Evolution:**
    *   Initialize inputs to $|0\rangle^{\otimes 4}$ and flip ancilla to $|1\rangle$.
    *   Apply $H^{\otimes 4}$ to inputs and $H$ to ancilla, yielding $\frac{1}{4}\sum_{x=0}^{15} |x\rangle \otimes |-\rangle$.
    *   Apply the oracle via `CNOT(q[3], anc[0])`. Since $s=0001$, the LSB is 1, so this imparts a phase $(-1)^{x_0}$, mapping the state to $\frac{1}{4}\sum_{x=0}^{15} (-1)^{x_0}|x\rangle \otimes |-\rangle$.
    *   Apply $H^{\otimes 4}$ to the input register. This interferes the phases to exactly reconstruct the secret string.
4.  **Measurement:** The final state of the input register is exactly $|0001\rangle$. Measuring all 4 input qubits yields the classical string `0001` with probability 1.0.

## isqTrain/3478

- task_id: `isqTrain/3478`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `phase_manipulation`, `ancilla_usage`, `boolean_logic`
- source: `isq_train_cot`
- dataset_index: `3095`

### Prompt

Write an isQ program that Deutsch-Jozsa for 3 qubits with balanced function f(x) = x[0] XOR x[1] XOR x[2] in isQ.
Oracle: CNOT from each input to ancilla.
Expected: |111> (non-zero).

### Chain-of-thought reasoning

## Reasoning

**Goal:** Implement Deutsch-Jozsa for 3 qubits to classify f(x)=x₀⊕x₁⊕x₂ as balanced, producing |111⟩.

**Qubits:** 3 input qubits q[0..2] (measured) + 1 ancilla q[1] (not measured).

**State evolution:**
1. **Init + X,H on ancilla:** |000⟩(√2⁻¹(|0⟩−|1⟩))
2. **H on inputs:** (1/√8)Σₓ|x⟩(√2

## isqQA/quantum_algorithms/87_comparison

- task_id: `isqQA/quantum_algorithms/87_comparison`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `comparison`, `algorithm`, `Deutsch-Jozsa算法`
- source: `qa_pipeline`
- dataset_index: `5298`

### Prompt

请对比分析Deutsch-Jozsa算法与经典算法在解决函数恒定与平衡判定问题上的性能差异。并进一步将其与同属早期量子算法的Bernstein-Vazirani（BV）算法在适用场景和核心机制上进行比较。最后，请使用isQ语言实现一个针对3比特输入的Deutsch-Jozsa算法电路，其中黑盒函数设定为平衡函数$f(x) = x_0 \oplus x_1$。

### Reference answer

<thinking>
1. **经典与量子对比分析：**
   - **经典算法：** 对于输入长度为$n$的函数，判定其是恒定还是平衡的，经典确定性算法在最坏情况下需要查询黑盒$2^{n-1} + 1$次。如果采用概率算法，查询$k$次出错的概率为$2^{-k}$，要保证零错误仍需指数级查询。
   - **量子算法（Deutsch-Jozsa）：** 仅需对量子黑盒进行**1次**查询即可达到100%的确定性。在查询复杂度上，量子算法相对经典确定性算法实现了指数级加速。

2. **Deutsch-Jozsa与Bernstein-Vazirani对比：**
   - **电路结构相似性：** 两者的核心电路结构完全相同，均为先施加Hadamard门，然后调用Oracle（$U_f$），再对输入位施加Hadamard门，最后测量。
   - **适用场景与问题定义：** DJ算法用于验证一个函数的“全局属性”（是所有输入输出相同，还是恰好一半输出0一半输出1）；而BV算法用于“提取隐含信息”，即寻找一个隐藏的比特串$a$，使得$f(x) = a \cdot x \pmod 2$。
   - **测量结果机制：** 在DJ算法中，若测量结果为全0态（$|000\dots 0\rangle$），则函数恒定；若为其他态，则函数平衡。在BV算法中，测量结果直接坍缩为隐藏字符串$|a\rangle$。可以说BV算法是DJ算法在更严格Oracle条件下的一个特例应用。

3. **isQ代码实现：**
   - 需要3个输入量子比特（q[0..2]）和1个辅助量子比特（anc[0]）。
   - 辅助比特初始化为$|1\rangle$并应用H门，进入$| - \rangle$态以实现相位反冲。
   - Oracle实现$f(x) = x_0 \oplus x_1$：由于这是模2加法，可通过两个CNOT门实现，控制位分别为q[0]和q[1]，目标位为anc[0]。
   - 最后对输入比特应用H门并测量。由于该函数平衡，测量结果必不为000。
</thinking>

Deutsch-Jozsa（DJ）算法与经典算法及其他量子算法的对比分析非常具有教学意义。

**1. 与经典算法的性能对比**
在经典计算模型中，如果我们有一个黑盒函数$f: \{0,1\}^n \rightarrow \{0,1\}$，且已知它要么是“恒定的”（对所有输入输出相同），要么是“平衡的”（对恰好一半的输入输出0，另一半输出1）。经典确定性算法在最坏情况下必须查询该函数$2^{n-1} + 1$次才能完全确定其属性。如果使用经典概率算法，查询$k$次得到相同结果的错误概率为$2^{-k}$，虽然能提供概率性加速，但依然没有从根本上摆脱指数级别的限制。
相比之下，Deutsch-Jozsa量子算法**仅需1次查询**就能以100%的概率给出绝对正确的答案。在查询复杂度这一维度上，DJ算法相对经典确定性算法实现了指数级的加速（$O(2^n)$ vs $O(1)$）。但其局限性在于，实际工程中极少遇到这种绝对非黑即白且需严格零错误的问题，因此它更多地是作为展示量子并行性和干涉机制的“概念验证”算法。

**2. 与Bernstein-Vazirani（BV）算法的对比**
DJ算法与BV算法在电路结构上具有高度的相似性，核心过程均为：Hadamard变换 $\rightarrow$ Oracle $\rightarrow$ Hadamard变换。但它们的适用场景和数学核心大不相同：
- **适用场景**：DJ算法用于判断全局的宏观属性（恒定或平衡）；BV算法则用于精确提取隐藏的局部信息（隐藏字符串$a$）。
- **Oracle限制**：DJ算法的Oracle没有任何代数结构限制，只要是平衡或恒定即可；BV算法的Oracle则被严格限定为线性函数结构（$f(x) = a \cdot x \pmod 2$）。
- **核心机制**：在DJ算法中，恒定函数会使所有态发生相同的相移，干涉后概率集中在全零态；而平衡函数会使一半态发生$\pi$的相移，干涉后全零态概率严格为0。在BV算法中，Oracle的线性结构直接等效于对态矢量施加了一个傅里叶基变换，这使得最终的Hadamard门刚好能将其逆变换回计算基态，从而直接测量出隐藏字符串。

**3. isQ代码实现**
以下是使用isQ语言实现的针对3比特输入的DJ算法。这里设计黑盒函数$U_f$为平衡函数$f(x) = x_0 \oplus x_1$（即只异或前两比特，忽略第三比特，满足一半输出0，一半输出1）。实现该函数只需对辅助比特执行两次CNOT门。

```isq
import std;

qbit q[3];
qbit anc[1];

procedure main() {
    // 1. 初始化辅助比特为 |1>
    X(anc[0]);
    
    // 2. 对所有量子比特施加Hadamard门
    // 输入比特进入均匀叠加态，辅助比特进入 |-> 态
    for i in 0:3 {
        H(q[i]);
    }
    H(anc[0]);
    
    // 3. 实现Oracle Uf，代表平衡函数 f(x) = x0 XOR x1
    // 作用辅助比特，引发相位反冲
    CNOT(q[0], anc[0]);
    CNOT(q[1], anc[0]);
    
    // 4. 再次对输入比特施加Hadamard门进行干涉
    for i in 0:3 {
        H(q[i]);
    }
    
    // 5. 测量输入比特
    // 由于函数是平衡的，测量结果绝对不会是 000
    // （在此具体函数下，测量结果将坍缩为 110）
    for i in 0:3 {
        M(q[i]);
    }
}
```

## isqTrain/4131

- task_id: `isqTrain/4131`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `4635`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[4];

procedure main() {
    X(q[3]);
    H(q[0]); H(q[1]); H(q[2]);
    ctrl Rz(2.0 * 3.14159265358979 * 2.0 / 8.0 * 1.0, q[0], q[3]);
    ctrl Rz(2.0 * 3.14159265358979 * 2.0 / 8.0 * 2.0, q[1], q[3]);
    ctrl Rz(2.0 * 3.14159265358979 * 2.0 / 8.0 * 4.0, q[2], q[3]);
    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    H(q[0]);
    ctrl Rz(-3.14159265358979 / 2.0, q[1], q[0]);
    ctrl Rz(-3.14159265358979 / 4.0, q[2], q[0]);
    H(q[1]);
    ctrl Rz(-3.14159265358979 / 2.0, q[2], q[1]);
    H(q[2]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants to predict the measurement output of a given isQ quantum circuit. The output must start with "## Circuit Analysis" and end with the predicted probability distribution. The reasoning must be in Dirac notation and concise.

2.  **Analyze the Circuit:**
    *   **Qubits:** `q[0], q[1], q[2], q[3]` (4 qubits). Initial state: $|0000\rangle$.
    *   **Initialization:**
        *   `X(q[3])` -> $|0001\rangle$.
        *   `H(q[0]), H(q[1]), H(q[2])` -> Creates an equal superposition on the first 3 qubits.
            State: $\frac{1}{2\sqrt{2}} \sum_{x=0}^{7} |x\rangle |1\rangle$.
    *   **Controlled-Rz (Phase Kickback / QFT part 1):**
        *   The operations are `ctrl Rz(2pi * 2/8 * 2^k, q[k], q[3])` for k=0, 1, 2.
        *   Wait, the angle for $Rz(\theta)$ is usually $e^{-i\theta/2}$. Let's look at the standard QFT definition.
        *   In QFT, the controlled phase shift for distance $k$ is $R_k = \begin{pmatrix} 1 & 0 \\ 0 & e^{2\pi i / 2^k} \end{pmatrix}$.
        *   The circuit has `ctrl Rz(2.0 * PI * 2.0 / 8.0 * 1.0, q[0], q[3])`.
            Angle = $2 \pi / 4 = \pi / 2$.
        *   `ctrl Rz(2.0 * PI * 2.0 / 8.0 * 2.0, q[1], q[3])`.
            Angle = $2 \pi / 2 = \pi$.
        *   `ctrl Rz(2.0 * PI * 2.0 / 8.0 * 4.0, q[2], q[3])`.
            Angle = $2 \pi$.
        *   Wait, standard $R_z(\theta)$ in isQ is $U1(\theta) = \begin{pmatrix} 1 & 0 \\ 0 & e^{i\theta} \end{pmatrix}$ or $Rz(\theta) = e^{-i\theta Z/2}$? Usually isQ's Rz is $e^{-i\theta Z/2}$, so $U1(\theta)$ is `GPhase(theta) Rz(2*theta)` or something.
        *   Let's check the definition. The angle `2.0 * PI * 2.0 / 8.0 * ...` looks exactly like the exponent in QFT. $e^{2\pi i j k / 2^n}$.
        *   Let's assume `ctrl Rz` applies the phase $e^{i\theta}$ or $e^{-i\theta}$ to the $|11\rangle$ component.
        *   Actually, if it's applied to $|x\rangle|1\rangle$, it transforms $|x\rangle|1\rangle \to e^{i\phi}|x\rangle|1\rangle$. The phase is kicked back to the control.
        *   Let $N = 8$. The states are $|x\rangle|1\rangle$.
        *   After these gates, state is $\frac{1}{\sqrt{8}} \sum_{x=0}^{7} e^{2\pi i x / 8} |x\rangle |1\rangle$? Let's trace carefully.
        *   Wait, $R_z$ in standard libs is usually $R_z(\theta) = \begin{pmatrix} e^{-i\theta/2} & 0 \\ 0 & e^{i\theta/2} \end{pmatrix}$.
        *   If controlled, the target is $|1\rangle$. The control is $|x\rangle$. If $x_k=1$, target gets $R_z$. For target=1, $|1\rangle \to e^{i\theta/2}|1\rangle$.
        *   Wait, the gates are `ctrl Rz(angle, q[k], q[3])`. The control is `q[k]`, target is `q[3]`.
        *   So if `q[k]=1` and `q[3]=1

### Reference answer

Dominant output states: |1001> with probability ~0.59 each

## isqTrain/1407

- task_id: `isqTrain/1407`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `isq_syntax_multi_register`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2868`

### Prompt

请用isQ语言编写一个量子电路：the Bernstein-Vazirani algorithm to find the secret string s = 11111 (MSB first). Use 5 input qubits and 1 ancilla.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Find the secret string s=11111 using the Bernstein-Vazirani algorithm with a single oracle query.

**Qubits:** 5 input qubits q[0]-q[4] (measured) and 1 ancilla anc[0] (unmeasured).

**State evolution:**
1. Initialize ancilla to |->: X then H on anc[0] gives |00000>|->.
2. Hadamard on input register: H⊗5 creates (1/√32)Σ|x⟩|−⟩ over all x ∈ {0,1}⁵.
3. Oracle f(x) = s·x mod 2: Each CNOT(q[i], anc[0]) phases by (-1)^(s·x), yielding (1/√32)Σ|x⟩(-1)^(s·x)|−⟩.
4. Final Hadamard H⊗5: Since H⊗5 is self-inverse and H⊗5|s⟩ = (1/√32)Σ|x⟩(-1)^(s·x)|x⟩, applying H⊗5 to the phase-encoded state recovers exactly |s⟩ = |11111⟩|−⟩.

**Expected probabilities:** The input register collapses to |11111⟩ with probability 1.0.

## isqTrain/3477

- task_id: `isqTrain/3477`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `phase_manipulation`, `ancilla_usage`
- source: `isq_train_cot`
- dataset_index: `4943`

### Prompt

Code this in isQ: Deutsch-Jozsa for 2 qubits with balanced function f(x) = x[1] in isQ.
Oracle: CNOT(q[1], anc).
Expected: |01> (non-zero confirms balanced).

### Chain-of-thought reasoning

## Reasoning

Goal: Implement Deutsch-Jozsa for 2 qubits to classify the balanced function f(x) = x[1].

Qubits: 3 total (q[0], q[1], anc); only q[0], q[1] are measured.

State evolution:
1. Initialize |q₀q₁anc⟩ = |000⟩; apply X(anc), H(anc): → |00⟩(|0⟩−|1⟩)/√2 = |00⟩|−⟩
2. Apply H(q[0]), H(q[1]): → (|00⟩+|01⟩+|10⟩+|11⟩)/2 ⊗ |−⟩
3. Apply Oracle CNOT(q[1], anc): phase kickback applies (−1)^f(x) = (−1)^(x₁), yielding (|00⟩−|01⟩+|10⟩−|11⟩)/2 ⊗ |−⟩ = |+⟩|−⟩ ⊗ |−⟩
4. Apply H(q[0]), H(q[1]): H|+⟩ = |0⟩, H|−⟩ = |1⟩ → |01⟩|−⟩

Expected measurement probabilities: {|01⟩: 1.0}. Since the result is non-zero (not |00⟩), this confirms the function is balanced.

## isqTrain/3652

- task_id: `isqTrain/3652`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `2013`

### Prompt

Write isQ code for the following quantum task: the 4-qubit inverse QFT on input |1111>. Apply bit-reversal, then inverse controlled-Rz rotations and Hadamard gates in reverse order. Measure all qubits.

### Chain-of-thought reasoning

## Reasoning
The circuit implements a 4-qubit inverse Quantum Fourier Transform (QFT†) on input |1111>, producing a uniform superposition over all 16 basis states.

**Qubits:** 4 qubits (q[0] to q[3]), all measured.

**State evolution:**
1. Initialize |0000⟩, apply X to all qubits → |1111⟩
2. Bit-reversal via swap (three-CNOT decomposition)(q[0],q[3]) and swap (three-CNOT decomposition)(q[1],q[2]) → |1111⟩ (unchanged since all bits are 1)
3. Apply inverse QFT in reverse order:
   - H(q[3]): |1111⟩ → (1/√2)(|0111⟩ + |1111⟩)
   - Controlled Rz(-π/2) on q[2] with control q[3]: introduces phase
   - H(q[2]): entangles q[2]
   - Controlled Rz(-π/4) and Rz(-π/2) on q[1] with controls q[3], q[2]
   - H(q[1]): further entangles q[1]
   - Controlled Rz(-π/8), Rz(-π/4), Rz(-π/2) on q[0] with controls q[3], q[2], q[1]
   - H(q[0]): completes the uniform superposition

**Final
