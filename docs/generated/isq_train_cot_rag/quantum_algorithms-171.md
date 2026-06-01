# ISQ training COT RAG corpus: quantum_algorithms shard 171

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1186

- task_id: `isqTrain/1186`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `interference`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1071`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;

// Hidden Linear Function on 3-qubit linear graph
// Adjacency matrix A has edges (0,1) and (1,2)
qbit q[3];

procedure main() {
    // Hadamard layer: uniform superposition
    H(q[0]); H(q[1]); H(q[2]);
    // Apply CZ for each edge in the graph
    // Edge (0,1): encodes quadratic term x0*x1
    CZ(q[0], q[1]);
    // Edge (1,2): encodes quadratic term x1*x2
    CZ(q[1], q[2]);
    // Final Hadamard layer: decode hidden function
    H(q[0]); H(q[1]); H(q[2]);
    // Measure to obtain solutions to A*z = b (mod 2)
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a concise, precise step-by-step analysis of an isQ quantum program, predicting the probability distribution. The output must start with "## Circuit Analysis", use Dirac notation, and end with the predicted probability distribution.

2.  **Analyze the isQ Code:**
    *   3 qubits: `q[0], q[1], q[2]`
    *   Initialization: `|000>`
    *   Step 1: `H(q[0]); H(q[1]); H(q[2]);` -> Creates uniform superposition `1/sqrt(8) * sum_{x=0}^{7} |x>`
    *   Step 2: `CZ(q[0], q[1]); CZ(q[1], q[2]);`
        *   CZ applies a phase of $-1$ if both are 1.
        *   The state becomes $\frac{1}{2\sqrt{2}} \sum_{x} (-1)^{x_0 x_1 + x_1 x_2} |x\rangle$.
        *   Specifically, states with even number of adjacent 1s (in the linear graph) keep +1, odd get -1. Wait, $x_0x_1 + x_1x_2$ evaluates to 1 for $|011\rangle$ ($x_0=0, x_1=1, x_2=1 \implies 0+1=1$), $|110\rangle$ ($x_0=1, x_1=1, x_2=0 \implies 1+0=1$), $|111\rangle$ ($1+1=2 \implies 0$).
        *   Let's list the signs for each basis state (order $x_0 x_1 x_2$):
            *   000 (0) -> +
            *   001 (1) -> +
            *   010 (2) -> +
            *   011 (3) -> -
            *   100 (4) -> +
            *   101 (5) -> +
            *   110 (6) -> -
            *   111 (7) -> +
    *   Step 3: `H(q[0]); H(q[1]); H(q[2]);` -> Hadamard on all qubits.
        *   $H^{\otimes 3} \frac{1}{2\sqrt{2}} \sum_x (-1)^{x_0 x_1 + x_1 x_2} |x\rangle$.
        *   Using $H^{\otimes n} \sum_x f(x) |x\rangle = \sum_z \left( \frac{1}{2^n} \sum_x (-1)^{x \cdot z} f(x) \right) |z\rangle$.
        *   We need the amplitude for each $|z\rangle = |z_0 z_1 z_2\rangle$:
            $A(z) = \frac{1}{8} \sum_{x} (-1)^{x_0 x_1 + x_1 x_2 + x_0 z_0 + x_1 z_1 + x_2 z_2}$.
        *   Let's calculate for each $z = z_0 z_1 z_2$:
            *   z = 000: $\sum (-1)^{x_0x_1 + x_1x_2}$. Sum of signs: +1 +1 +1 -1 +1 +1 -1 +1 = 4. Amplitude = 4/8 = 1/2. Prob = 1/4.
            *   z = 001: $\sum (-1)^{x_0x_1 + x_1x_2 + x_2}$. Let's check x=000..111.
                000: +
                001: -
                010: +
                011: - * - = +
                100: +
                101: -
                110: - * - = +
                111: + * - = -
                Sum: +1 -1 +1 +1 +1 -1 +1 -1 = 2. Amplitude = 2/8 = 1/4. Prob = 1/16.
                Wait, let me re-evaluate the predicted output.
                The prompt says: Expected measurement probabilities: {|000>: 0.25, |010>: 0.25, |101>: 0.25, |111>: 0.25}.
                Let me recalculate carefully.

3.  **Recalculate CZ matrix / operation:**

### Reference answer

{'predicted_probs': {'0': 0.25, '2': 0.25, '5': 0.25, '7': 0.25}, 'explanation': 'Parametric variant of isqEval/446. Dimension: predict probabilities for reference circuit.'}

## isqTrain/3825

- task_id: `isqTrain/3825`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `326`

### Prompt

Write isQ code for the following quantum task: a 1D quantum walk on 4 positions using 3 step(s). Use q[0] as the coin qubit and q[1..2] as the position register. Each step: Hadamard coin flip followed by controlled shifts.

### Chain-of-thought reasoning

Let me trace through this quantum walk carefully.

We have 3 qubits: q[0] is the coin, q[1..2] is the position register (2 bits for 4 positions).

Initial state: |000⟩ (coin=0, position=0)

The controlled shift operation: when coin is |1⟩, we increment the position. The position register q[1..2] represents positions 0,1,2,3 as |00⟩, |01⟩, |10⟩, |11⟩.

Looking at the code:
- ctrl X(q[0], q[1]) - when q[0]=|1⟩, flip q[1]
- ctrl X(q[0], q[2]) - when q[0]=|1⟩, flip q[2]

Wait, this doesn't implement an increment. If we do ctrl X on both q[1] and q[2] when coin is |1⟩, we flip both bits. So:
- |00⟩ → |11⟩
- |01⟩ → |10⟩
- |10⟩ → |01⟩
- |11⟩ → |00⟩

This is actually flipping both bits, which is position XOR 3 (or position = 3 - position, i.e., reflection).

Let me trace step by step:

**Step 1:**
- H on q[0]: |000⟩ → (1/√2)(|000⟩ + |100⟩)
- ctrl X(q[0], q[1]): (1/√2)(|000⟩ + |110⟩)
- ctrl X(q[0], q[2]): (1/√2)(|000⟩ + |111⟩)

**Step 2:**
- H on q[0]: Need to apply H to q[0] for both terms
  - |000⟩ → (1/√2)(|000⟩ + |100⟩)
  - |111⟩ → (1/√2)(|011⟩ + |111⟩) wait no... H on q[0] of |111⟩ = (1/√2)(|011⟩ + |111⟩)? No.
  
  Wait, let me be more careful. The state is |q[0], q[1], q[2]⟩.
  
  H on q[0]: |0⟩ → (1/√2)(|0⟩ + |1⟩), |1⟩ → (1/√2)(|0⟩ - |1⟩)
  
  So (1/√2)(|000⟩ + |111⟩) → (1/√2)[(1/√2)(|000⟩ + |100⟩) + (1/√2)(|011⟩ - |111⟩)]
  = (1/2)(|000⟩ + |100⟩ + |011⟩ - |111⟩)

- ctrl X(q[0], q[1]): flip q[1] when q[0]=1
  = (1/2)(|000⟩ + |110⟩ + |011⟩ - |101⟩)

- ctrl X(q[0], q[2]): flip q[2] when q[0]=1
  = (1/2)(|000⟩ + |111⟩ + |011⟩ - |100⟩)
  = (1/2)(|000⟩ - |100⟩ + |011⟩ + |111⟩)

**Step 3:**
- H on q[0]: Apply H to each term's q[0]:
  - |000⟩ → (1/√2)(|000⟩ + |100⟩)
  - |100⟩ → (1/√2)(|000⟩ - |100⟩)
  - |011⟩ → (1/√2)(|011⟩ + |111⟩)
  - |111⟩ → (1/√2)(|011⟩ - |111⟩)
  
  So: (1/2)[(1/√2)(|000⟩ + |100⟩) - (1/√2)(|000⟩ - |100⟩) + (1/√2)(|011⟩ + |111⟩) + (1/√2)(|011⟩ - |111⟩)]
  = (1/(2√2))[(|000⟩ + |100⟩ - |000⟩ + |100⟩) + (|011⟩ + |111⟩ + |011⟩ - |111⟩)]
  = (1/(2√2))[2|100⟩ + 2|011⟩]
  = (1/√2)(|100⟩ + |011⟩)
  = (1/√2)(|011⟩ + |100⟩)

- ctrl X(q[0], q[1]): flip q[1] when q[0]=1

## isqQA/quantum_algorithms/89_optimization_variant

- task_id: `isqQA/quantum_algorithms/89_optimization_variant`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `optimization_variant`, `algorithm`, `DJ算法与经典查询复杂度对比`
- source: `qa_pipeline`
- dataset_index: `3749`

### Prompt

Deutsch-Jozsa算法在理论上展示了量子计算的指数级加速，但其原始假设（承诺函数必定是严格常数或严格平衡）在实际应用中过于苛刻。为了提升其实用性和泛化能力，研究者们提出了哪些重要的改进版本或变体？请详细说明至少一种变体的数学原理，并给出其在isQ量子编程语言中的代码实现。

### Reference answer

Deutsch-Jozsa (DJ) 算法是量子计算早期的重要里程碑，但其“绝对常数或绝对平衡”的严格承诺在实际中很少遇到。为了突破这一限制并扩展其应用场景，学术界提出了几种关键的变体和改进版本。最著名的改进是**Bernstein-Vazirani (BV) 算法**，它将DJ算法中的“平衡函数”替换为“内积函数”。另一个重要的理论扩展是**概率型Deutsch-Jozsa算法**，它放宽了确定性求解的要求，以高概率区分常数和平衡函数，甚至可以处理几乎平衡的函数，这更贴近实际应用中的容错需求。此外，**广义Deutsch-Jozsa算法**被提出用于处理 $k$ 等分的函数集合。下面我们深入探讨Bernstein-Vazirani (BV) 算法及其在isQ中的实现。

**1. Bernstein-Vazirani 算法的数学原理**

在BV问题中，我们给定一个黑盒函数 $f: \{0,1\}^n \rightarrow \{0,1\}$，且承诺该函数具有特定形式：
$f(x) = s \cdot x \pmod 2$
其中 $s \in \{0,1\}^n$ 是一个未知的秘密字符串，“$\cdot$”表示按位内积（即 $s \cdot x = s_1x_1 \oplus s_2x_2 \oplus \dots \oplus s_nx_n$）。

经典算法需要查询该黑盒 $n$ 次才能确定秘密字符串 $s$（例如依次输入 $x = 2^0, 2^1, \dots, 2^{n-1}$ 的状态）。然而，BV算法通过巧妙的量子叠加和相位干涉，仅需**1次查询**即可提取出完整的 $s$。其量子线路的演化过程如下：

初始态为 $|0\rangle^{\otimes n}|1\rangle$。对所有的量子比特应用Hadamard门：
$|\psi_1\rangle = H^{\otimes n}|0\rangle^{\otimes n} \otimes H|1\rangle = \frac{1}{\sqrt{2^n}} \sum_{x=0}^{2^n-1} |x\rangle \otimes \frac{|0\rangle - |1\rangle}{\sqrt{2}}$

接着应用受控的Oracle $U_f$（其作用为 $|x\rangle|y\rangle \rightarrow |x\rangle|y \oplus f(x)\rangle$）。由于目标比特处于 $\frac{|0\rangle - |1\rangle}{\sqrt{2}}$ 状态（即特征值-1的本征态），这触发了著名的**相位反冲**：
$|\psi_2\rangle = \frac{1}{\sqrt{2^n}} \sum_{x=0}^{2^n-1} (-1)^{s \cdot x} |x\rangle \otimes \frac{|0\rangle - |1\rangle}{\sqrt{2}}$

此时，前 $n$ 个比特的状态正好是对应特征值为 $(-1)^{s \cdot x}$ 的Hadamard变换的本征向量。为了提取这个隐藏在相位中的 $s$，我们对前 $n$ 个比特再次应用Hadamard变换。由于 $H^{\otimes n} \left( \frac{1}{\sqrt{2^n}} \sum_{x=0}^{2^n-1} (-1)^{s \cdot x} |x\rangle \right) = |s\rangle$，此时系统的状态变为：
$|\psi_3\rangle = |s\rangle \otimes \frac{|0\rangle - |1\rangle}{\sqrt{2}}$

最后，对前 $n$ 个比特进行测量，就可以直接得到秘密字符串 $s$。

**2. isQ 代码实现**

假设我们寻找的秘密字符串为 $s=1011$（即十进制的11），对应的 $n=4$。由于 $f(x) = s \cdot x$ 等价于受 $s_i=1$ 控制的多位Toffoli门（此处用一系列CNOT等效），Oracle的作用可直接通过量子门映射。以下是BV算法在isQ语言中的完整实现：

```isQ
import std;

qbit q[5]; // 前4位为输入，最后1位为目标比特

procedure main() {
    // 初始化目标比特为 |1>，以便产生相位反冲
    X(q[4]);

    // 应用Hadamard门，创建叠加态
    for i in 0:5 {
        H(q[i]);
    }

    // 构建并应用 Bernstein-Vazirani Oracle
    // 秘密字符串 s = 1011，对应 q[3], q[1], q[0] 为 1
    // 当且仅当这些位为1时，翻转目标比特，引入相位 (-1)^(s.x)
    CNOT(q[0], q[4]);
    CNOT(q[1], q[4]);
    CNOT(q[3], q[4]);

    // 对前4个输入比特再次应用Hadamard门，进行逆变换提取相位
    for i in 0:4 {
        H(q[i]);
    }

    // 测量前4个比特，结果应为二进制 1011
    for i in 0:4 {
        M(q[i]);
    }
}
```

在这段代码中，我们巧妙利用了Hadam门将计算基转换为傅里叶基，使得隐藏的字符串 $s$ 从频域（相位）被还原到了空间域（概率幅），完美展现了BV变体相对经典算法在查询复杂度上的巨大优势。

## isqTrain/4455

- task_id: `isqTrain/4455`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `entanglement`, `interference`, `isq_syntax_arrays`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `43`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;

qbit q[3];
qbit a[1];

procedure my_oracle() {
    CNOT(q[0], a[0]);
    CNOT(q[1], a[0]);
}

procedure main() {
    // Prepare ancilla in |-> state
    X(a[0]); H(a[0]);
    // Apply Hadamard to query qubits
    H(q[0]); H(q[1]); H(q[2]);
    // Apply oracle
    my_oracle();
    // Second Hadamard layer
    H(q[0]); H(q[1]); H(q[2]);
    // Measure query qubits
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a concise, precise step-by-step reasoning for the provided isQ quantum program, predicting the probability distribution. The output must be exactly as specified, ending with the distribution.

2.  **Analyze the isQ Code:**
    *   `qbit q[3]; qbit a[1];` -> 4 qubits total: $q_0, q_1, q_2, a_0$. Initial state $|0000\rangle$ (order doesn't strictly matter, but let's track entanglement). Let's say $q_2 q_1 q_0 a_0$.
    *   **Ancilla preparation:** `X(a[0]); H(a[0]);` -> State $|0\rangle \xrightarrow{X} |1\rangle \xrightarrow{H} |-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$. Phase kickback is set up.
    *   **Query qubits preparation:** `H(q[0]); H(q[1]); H(q[2]);` -> Apply H to $q_0, q_1, q_2$. State becomes $\frac{1}{\sqrt{8}} \sum_{x \in \{0,1\}^3} |x\rangle \otimes (|0\rangle - |1\rangle)$.
    *   **Oracle application:** `my_oracle()` contains `CNOT(q[0], a[0]); CNOT(q[1], a[0]);`.
        *   The function computes $f(x) = x_0 \oplus x_1$ into $a_0$.
        *   Due to phase kickback, the oracle applies a phase of $(-1)^{f(x)}$ to the query qubits.
        *   $f(x) = 1$ when $x_0 \neq x_1$. $f(x) = 0$ when $x_0 = x_1$.
        *   So, $(-1)^{x_0 \oplus x_1} |x\rangle$.
        *   This is equivalent to applying a CZ gate between $q_0$ and $q_1$, with a possible global phase (it's exactly $Z_{q_0} Z_{q_1} CZ_{q_0, q_1}$ or just a phase shift based on parity). Let's trace it exactly:
            *   $|x_0 x_1 x_2\rangle (|0\rangle - |1\rangle) \to (-1)^{x_0 \oplus x_1} |x_0 x_1 x_2\rangle (|0\rangle - |1\rangle)$.
    *   **Second Hadamard layer:** `H(q[0]); H(q[1]); H(q[2]);` -> Applies $H^{\otimes 3}$ to the query qubits.
        *   This performs the inverse Fourier transform (Hadamard transform) over $Z_2^3$.
        *   The state of $q_0, q_1, q_2$ becomes $\frac{1}{\sqrt{8}} \sum_{y} \left( \frac{1}{\sqrt{8}} \sum_{x} (-1)^{x_0 \oplus x_1} (-1)^{x \cdot y} \right) |y\rangle$.
        *   Alternatively, note that $(-1)^{x_0 \oplus x_1} = (-1)^{x_0} (-1)^{x_1}$.
        *   Wait, $x_0 \oplus x_1 = x_0 + x_1 \pmod 2$.
        *   Let's look at the gate sequence. $H \to \text{Phase}(x_0 \oplus x_1) \to H$.
        *   This is $H \cdot U_f \cdot H$. Since $U_f$ acts as $(-1)^{x_0+x_1}$, $H U_f H$ acts as $X$ on $q_0$ and $q_1$ (Wait, no. A phase $(-1)^{x_i}$ becomes an $X$ gate. A phase $(-1)^{x_0 x_1}$ becomes a CZ. Here we have $(-1)^{x_0+x_1}$).
        *   Let's verify: $H_{0} H_{1} \left[ (-1)^{x_0+x_1} |x_0 x_1\rangle \right]$.
        *   For $

### Reference answer

{'predicted_probs': {'010': 1.0}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|010>) = 1.0000.'}

## isqTrain/747

- task_id: `isqTrain/747`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5091`

### Prompt

Write isQ code for the following quantum task: implements a variant of the modular_adder pattern using q[3] -> q[5]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for an isQ quantum program. Let me analyze The implementation:

1. 5 qubits are declared: q[0] through q[4]
2. The circuit implements a modular adder pattern

Let me trace through the circuit:

1. Initial state: |00000> (all 5 qubits in ground state)

2. X(q[1]): Flips q[1], encoding a=2 (binary 10)
   State: |00010>

3. X(q[0]): Flips q[0], adding constant 1
   State: |00011> (value is now 3)

4. Toffoli(q[0], q[1], q[2]): Sets q[2] = 1 if q[0] AND q[1] are both 1 (overflow detection when value >= 3)
   Since q[0]=1 and q[1]=1, q[2] becomes 1
   State: |00111>

5. CNOT(q[2], q[0]): Flips q[0] if q[2] is 1
   Since q[2]=1, q[0] flips from 1 to 0
   State: |00110>

6. CNOT(q[2], q[1]): Flips q[1] if q[2] is 1
   Since q[2]=1, q[1] flips from 1 to 0
   State: |00100>

7. Measurements:
   - M(q[0]) = 0
   - M(q[1]) = 0
   - M(q[3]) = 0
   - M(q[4]) = 0

The result is 0000 (4 bits measured).

So the modular adder takes value 3 (which is >= modulus 3), detects the overflow, and subtracts 3 to get 0.

Wait, let me re-check the qubit ordering. The prompt says "q[3] -> q[5]" which seems to indicate using qubits 3 through 5, but the reference uses q[0] through q[4]. Let me re-read...

Actually, looking at the code more carefully, it seems like the circuit uses q[0], q[1], q[2] for the main computation, and q[3], q[4] are left in the ground state. The measurements are on q[0], q[1], q[3], q[4].

Let me trace again more carefully:

1. |00000> initial state
2. X(q[1]): |00100> (q[1] = 1, encoding a=2 in binary where q[0] is LSB, q[1] is next bit)

Wait, I need to be careful about the bit ordering. In the comment it says "binary 10" for a=2. If q[0] is LSB:
- a=2 in binary is "10" which means q[1]=1, q[0]=0
So after X(q[1]): q[1]=1, others=0

Actually let me think about this differently. The state is typically written as |q[4]q[3]q[2]q[1]q[0]> from left to right (highest to lowest bit).

So |00000> means all qubits are 0.

After X(q[1]): The second qubit from the right (q[1]) is flipped.
State: |00010> which in my notation is |q[4]=0, q[3]=0, q[2]=0, q[1]=1, q[0]=0>

Hmm, but typically in quantum computing, we write |q[n-1]...q[1]q[0]> where q[0] is the rightmost bit. So |00010> means q[1]=1, all others 0.

OK so:
1. |00000> - initial
2. X(q[1]) → |00010> (q[1]=1)
3. X(q[0]) → |00011> (q[0]=1, q[1]=1, value=3)
4. Toffoli(q[0], q[1], q[2]) → |00111> (q[2]=1 because q[0]=1 and q[1]=1)
5. CNOT(q[2], q[0]) → |00110> (q[0] flips from 1 to 0)
6. CNOT(q[2], q[1]) → |00100> (q[1] flips from 1 to 0)

Wait, that's not right. After step 5, q[0] should be

## isqTrain/3569

- task_id: `isqTrain/3569`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `entanglement`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1724`

### Prompt

Fix the bug in the following isQ program.

Bug description: Missing X gate for state preparation

The program should 4-qubit W state preparation.

### Chain-of-thought reasoning

The buggy code is missing the X gate on q[0] to prepare the initial state |1000>.

The comment says "Start with |1000>" but no X gate is applied. Without the X gate, the initial state is |0000>, and the subsequent Ry gate and other operations won't produce the correct W state.

The fix is to add `X(q[0]);` right after the comment about starting with |1000>.

Let me trace through the corrected circuit:

1. Initial state: |0000>
2. After X(q[0]): |1000>
3. After Ry(2*pi/3, q[0]): This rotates q[0] so that amplitude is split: 1/4 stays in q[0], 3/4 goes to |0> on q[0] with the excitation needing to go elsewhere. Actually, Ry(2*arccos(sqrt(1/4))) on |1> gives cos(arccos(0.5))|1> + sin(arccos(0.5))|0> = 0.5|1> + sqrt(3)/2|0>. Wait, let me recalculate.

Ry(θ)|1⟩ = cos(θ/2)|1⟩ + sin(θ/2)|0⟩

θ = 2*arccos(0.5) = 2*(π/3) = 2π/3

cos(π/3) = 0.5, sin(π/3) = sqrt(3)/2

So Ry(2π/3)|1⟩ = 0.5|1⟩ + sqrt(3)/2|0⟩

State: (1/2)|1000⟩ + (√3/2)|0000⟩... wait, that doesn't seem right for W state preparation.

Hmm, let me reconsider. Actually, Ry(θ)|0⟩ = cos(θ/2)|0⟩ + sin(θ/2)|1⟩ and Ry(θ)|1⟩ = -sin(θ/2)|0⟩ + cos(θ/2)|1⟩.

So after X(q[0]), state is |1000⟩.

Ry(2*arccos(sqrt(1/4))) applied to q[0]:
θ/2 = arccos(0.5) = π/3
sin(π/3) = √3/2, cos(π/3) = 1/2

Ry|1⟩ = -sin(π/3)|0⟩ + cos(π/3)|1⟩ = -(√3/2)|0⟩ + (1/2)|1⟩

So state becomes: (1/2)|1000⟩ - (√3/2)|0000⟩

The global phase doesn't matter. So we have amplitude 1/2 on |1000⟩ and √3/2 on |0000⟩.

Then nctrl X(q[0], q[1]) means X is applied to q[1] when q[0] is |0⟩. So the |0000⟩ component becomes |0100⟩ (q[1] flips).

Wait, but the predicted output say |0100⟩: 0.5 which is way more than 1/4. Hmm, let me re-examine the predicted output.

Expected: {|0001>: 0.125, |0010>: 0.125, |0100>: 0.5, |1000>: 0.25}

Hmm, these don't sum to a W state. |0100> has 0.5 probability? That's not a W state which should have equal amplitudes. But maybe The predicted output just what the buggy/corrected circuit produces, not necessarily a perfect W state. Actually wait, looking more carefully - a 4-qubit W state is (|0001⟩+|0010⟩+|0100⟩+|1000⟩)/2, each with probability 1/4 = 0.25.

But The predicted output |0100>: 0.5, which is wrong for a W state. Maybe The predicted output what the *buggy* circuit produces? No, it says "Expected measurement probabilities" for the corrected code.

Hmm, actually, I wonder if the predicted output in the prompt is just illustrative and possibly wrong, and I should focus on the bug fix itself.

The bug is clear: missing `X(q[0])` to initialize the state to |1000⟩ before the Ry rotation. The comment says "Start with |1000>" but the X gate is absent.

Let me not worry too much about the exact expected probabilities and just explain the bug and fix.

Actually, wait. Let me re-analyze the probabilities. Maybe the output format uses a different bit ordering. "earlier

## isqTrain/63

- task_id: `isqTrain/63`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `533`

### Prompt

Write isQ code for the following quantum task: implements the phase_kickback pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

Let me analyze the phase kickback circuit with reversed measurement order.

## Circuit Analysis

**Goal**: Implement phase kickback with reversed measurement order to demonstrate how measurement ordering affects bitstring indexing.

**Qubits**: 2 qubits (q[0] and q[1]), both measured.

**State Evolution**:

1. Initial state: |00>

2. Apply X(q[1]), H(q[1]): 
   - q[1] goes to |1>, then H|1> = |->
   - State: |0>⊗|-> = (|00> - |01>)/√2

3. Apply H(q[0]):
   - q[0] goes to |+>
   - State: |+>⊗|-> = (|0>+|1>)/√2 ⊗ (|0>-|1>)/√2
   - = (|00> - |01> + |10> - |11>)/2

4. Apply CNOT(q[0], q[1]):
   - CNOT with q[0] as control, q[1] as target
   - |00> → |00>, |01> → |01>, |10> → |11>, |11> → |10>
   - State: (|00> - |01> + |11> - |10>)/2
   - = (|00> - |01> - |10> + |11>)/2
   - = (|0>-|1>)/√2 ⊗ (|0>-|1>)/√2 = |->⊗|->

   Wait, let me recalculate:
   - Before CNOT: (|00> - |01> + |10> - |11>)/2
   - After CNOT: (|00> - |01> + |11> - |10>)/2
   
   Actually CNOT(q[0], q[1]) means q[0] is control, q[1] is target:
   - |00> → |00>
   - |01> → |01>
   - |10> → |11>
   - |11> → |10>
   
   So: (|00> - |01> + |11> - |10>)/2 = (|00> - |01> - |10> + |11>)/2
   
   This can be factored as: (|0>-|1>)/√2 ⊗ (|0>-|1>)/√2 = |->⊗|->

   Hmm, but in standard phase kickback, the control should end up in |1> after the H gate. Let me reconsider.

   The phase kickback effect: when the target is in |->, CNOT applies a phase of -1 when the control is |1>. This effectively applies Z to the control qubit.

   Let me trace again more carefully:
   
   Before CNOT: |+>|-> = (|0>+|1>)/√2 ⊗ (|0>-|1>)/√2
   
   Expanding: (|0>(|0>-|1>) + |1>(|0>-|1>))/2
   = (|00>-|01>+|10>-|11>)/2
   
   After CNOT (control=q[0], target=q[1]):
   |00> → |00>, |01> → |01>, |10> → |11>, |11> → |10>
   
   State: (|00>-|01>+|11>-|10>)/2
   = (|00>-|01>-|10>+|11>)/2
   = |0>(|0>-|1>)/2 + |1>(|1>-|0>)/2
   = (|0>-|1>)/2 ⊗ (|0>-|1>) 
   
   Wait, that's not right. Let me be more careful:
   
   = (|00>-|01>-|10>+|11>)/2
   = |0>(|0>-|1>)/2 + |1>(-|0>+|1>)/2
   = |0>(|0>-|1>)/2 - |1>(|0>-|1>)/2
   = (|0>-|1>)(|0>-|1>)/2
   = |->⊗|->

5. Apply H(q[0]):
   - H|-> = |1>
   - State: |1>⊗|-> = |1>(|0>-|1>)/√2 = (|10>-|11>)/√2

6. Measure M(q[1]), M(q[0]):
   - The state is (|10>-|11>)/√2
   - This

## isqTrain/3588

- task_id: `isqTrain/3588`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `qft_based_arithmetic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `164`

### Prompt

Fix the bug in the following isQ program.

Bug description: Wrong rotation angle (doubled)

The program should Draper QFT adder: 2+1=3.

### Chain-of-thought reasoning

Let me analyze this bug carefully.

The program implements a Draper QFT adder to compute 2+1=3.

Let me understand the setup:
- `q[0]` = a[0] (LSB of a)
- `q[1]` = a[1] (MSB of a)
- `q[2]` = b[0] (LSB of b)
- `q[3]` = b[1] (MSB of b)

Initial state: a=10 (binary), so a[0]=0, a[1]=1. b=01 (binary), so b[0]=1, b[1]=0.
So X(q[1]) sets a[1]=1, X(q[2]) sets b[0]=1.

The QFT on the b register (q[2], q[3]) involves:
1. H on q[2]
2. Controlled Rz from q[3] to q[2]
3. H on q[3]
4. Then some swap (CNOT swap)

The buggy code has:

This is π, but the correct angle should be π/2 (1.5707963267949).

In QFT, the controlled rotation between qubit j and qubit k (where they are k-j apart) uses angle 2π/2^(k-j+1). For q[2] and q[3], they are 1 apart, so the angle should be 2π/2^2 = 2π/4 = π/2.

The buggy code uses π (which is doubled), and the fix changes it to π/2.

Let me verify the output. After the Draper adder, we expect:
- a register stays the same: a[0]=0, a[1]=1 → q[0]=0, q[1]=1
- b register should show the sum: 2+1=3 → b=11 → q[2]=1, q[3]=1

So the final state should be |0110> ... wait, let me re-check the measurement bitstring.

The predicted measurement is |0100> with probability 1.0. Let me reconsider.

Hmm, let me re-read the bit ordering. The --probs output says "earlier measured qubit = higher bit".

Measurements are: M(q[0]), M(q[1]), M(q[2]), M(q[3]).

So the bitstring is q[0]q[1]q[2]q[3] where q[0] is the highest bit.

Expected: |0100> means q[0]=0, q[1]=1, q[2]=0, q[3]=0.

Wait, that would mean a=01(1) and b=00(0), giving 1+0=1, not 3. That doesn't make sense.

Actually wait, let me re-read. "Expected measurement probabilities: {|0100>: 1.0}"

Hmm, maybe I'm misunderstanding the register mapping or the predicted output. Let me re-examine...

Actually wait - maybe the "expected measurement probabilities" in the prompt is wrong or I'm misreading it. Let me just focus on the bug.

The bug is clear: in the QFT on the b register, the controlled Rz gate between q[3] and q[2] uses angle π instead of π/2. The QFT requires a rotation of 2π/2^(distance+1) = 2π/4 = π/2 for adjacent qubits.

Actually, hold on. Let me reconsider. The QFT rotation from qubit j to qubit i (where i < j) is Rz(2π/2^(j-i+1)). Wait, standard QFT:

For QFT on n qubits, after H on qubit i, we apply controlled Rz(2π/2^k) from qubit i+k to qubit i for k = 2, 3, ..., n-i.

So for the first qubit (q[2]), after H(q[2]):
- Controlled Rz(2π/2^2) = Rz(π/2) from q[3] to q[2]

That's π/2, not π. The bug is that the angle was doubled to π instead of π/2.

The fix: change `ctrl Rz(3.1415926535898, q[3], q[2])` to `ctrl Rz(1.5707963267949, q[3], q[2])`.

Let me verify

## isqTrain/3018

- task_id: `isqTrain/3018`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3396`

### Prompt

Implement a quantum circuit in isQ: creates a 3-qubit GHZ state and then applies an X gate to qubit 2.

Requirements:
- Declare `qbit q[3];` at global scope.
- Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Create a 3-qubit GHZ state (|000⟩ + |111⟩)/√2, then apply X to qubit 2.

**Qubits:** 3 qubits declared globally (`qbit q[3]`), all 3 measured.

**State evolution:**
1. Start: |000⟩
2. H(q[0]): (|000⟩ + |100⟩)/√2
3. CNOT(q[0], q[1]): (|000⟩ + |110⟩)/√2
4. CNOT(q[1], q[2]): (|000⟩ + |111⟩)/√2 — standard GHZ state
5. X(q[2]): (|001⟩ + |110⟩)/√2

**Expected probabilities:** Equal superposition of |001⟩ and |110⟩, each with probability 0.5. The X gate on q[2] flips the last bit, transforming |000⟩→|001⟩ and |111⟩→|110⟩.

## isqExpand/algo/120

- task_id: `isqExpand/algo/120`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `multi_controlled_logic`
- source: `isq_expansion`
- dataset_index: `2717`

### Prompt

Implement a quantum circuit in isQ: implementing one step of a coined quantum walk on a 4-node cycle graph with an oracle that marks node |10>. Use q[0] as the coin qubit and q[1],q[2] as the 2-bit position register. Start at position |00> with coin |0>. The algorithm: (1) Oracle marks position |10> (q1=1,q2=0): X(q[2]), CZ(q[1],q[2]), X(q[2]). (2) Coin flip: H(q[0]). (3) Conditional shift: coin=1 right-shift via CNOT(q[0],q[1]) controlled on q[2] and X on q[2] controlled on q[0]; coin=0 left-shift via nctrl operations. Specifically: ctrl CNOT(q[0], q[2], q[1]) then CNOT(q[0], q[2]) for right-shift; nctrl X(q[0], q[2]) then nctrl CNOT(q[0], q[2], q[1]) for left-shift. Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: One step of coined quantum walk on 4-node cycle from position |00>.

1. Oracle marks pos |10>: no effect since current pos is |00>.
2. Coin H(q[0]): creates superposition.
3. Shift: coin=1 -> right (00->01), coin=0 -> left (00->11).

Final state: (|0,11> + |1,01>)/sqrt(2)
  |011> = index 3, prob 0.5
  |101> = index 5, prob 0.5
Expected: [0,0,0,0.5,0,0.5,0,0]
