# ISQ training COT RAG corpus: quantum_algorithms shard 83

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqQA/quantum_algorithms/105_comparison

- task_id: `isqQA/quantum_algorithms/105_comparison`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `comparison`, `algorithm`, `Shor算法中的模幂运算`
- source: `qa_pipeline`
- dataset_index: `3418`

### Prompt

在Shor算法的量子电路实现中，模幂运算是决定整个算法资源开销的核心子程序。请对比分析在实现模幂运算时，基于量子傅里叶变换（QFT）的算术方法与基于进位传播的算术方法（如CDKM或VBE加法器架构）在性能优缺点及适用场景上的差异。并请在isQ代码中展示如何利用可控模乘法模块，通过重复平方-乘的算法逻辑，构建出模幂运算的顶层控制结构。

### Reference answer

<thinking>
在Shor算法中，模幂运算的目标是实现酉变换：$U_{a,N}|x\rangle|0\rangle = |x\rangle|a^x \bmod N\rangle$。
这一变换在量子计算机上无法直接实现，必须将其分解为基本的量子门序列。最常用的方法是利用经典计算中的“平方-乘”算法。对于 $n$ 位的输入 $x = x_{n-1}...x_1x_0$，有：
$$a^x \equiv a^{\sum_{i=0}^{n-1} x_i 2^i} \equiv \prod_{i=0}^{n-1} a^{x_i 2^i} \pmod N$$
因此，电路可以通过遍历 $x$ 的每一位来构建：如果 $x_i = 1$，则在结果寄存器上执行受控的模乘操作 $\times a^{2^i} \pmod N$。每次操作后，基础数 $a$ 的模平方由经典预计算或独立的量子模平方模块完成。

在底层算术逻辑的实现上，存在两大主流流派对比：
1. **基于QFT的算术**：利用相位编码数字，加法通过条件相位旋转完成（如Draper加法器）。
   - 优点：无需处理位线间的级联进位，某些情况下可以通过并行旋转大幅降低电路深度。
   - 缺点：包含大量非Clifford门（任意角度的 $R_z$ 旋转），在容错量子计算中，这些门的合成需要极高的T门数量或极其昂贵的相位梯度状态准备，常数因子极大。
2. **基于进位的算术**（如CDKM、VBE架构）：使用Toffoli、CNOT等标准门模拟经典进位传播。
   - 优点：仅使用基础的Clifford+T门集，容错阈值极高，且在现有NISQ（含噪声中等规模量子）设备的拓扑结构上更容易进行映射和布线优化。
   - 缺点：存在不可避免的进位传播延迟，使得模加法和模乘法的电路深度显著增加，且往往需要大量的辅助比特来暂存进位。

isQ代码设计：
我们定义两个量子寄存器 `x` 和 `y`。`x` 寄存器存储控制指数（通过经典测量或量子控制），`y` 寄存器存储累加的模幂结果（初始为1）。我们将定义受控模乘的占位门，通过 for 循环演示“重复平方-乘”的受控结构。
</thinking>

在Shor算法中，模幂运算的核心在于实现变换 $|x\rangle|0\rangle \rightarrow |x\rangle|a^x \bmod N\rangle$。为了在量子线路上执行该操作，通常利用二进制展开将模幂分解为连续的受控模乘法。设 $x$ 为 $n$ 位量子寄存器，则 $a^x \pmod N$ 可展开为：
$$a^x \equiv a^{\sum_{i=0}^{n-1} x_i 2^i} \equiv \prod_{i=0}^{n-1} a^{x_i 2^i} \pmod N$$
这要求我们在量子线路中，根据 $x_i$ 的状态，条件性地对目标寄存器执行 $\times (a^{2^i} \bmod N)$ 的模乘操作。

在实现上述模乘操作所依赖的底层量子算术逻辑时，学术界主要有两种主流架构：**基于量子傅里叶变换（QFT）的算术架构**与**基于进位传播的算术架构**（如CDKM、VBE加法器）。两者的对比分析如下：

**1. 基于量子傅里叶变换（QFT）的算术架构**
这种架构（如Draper加法器）不直接在计算基上进行布尔逻辑运算，而是先将量子态通过QFT变换到傅里叶基，通过施加一系列受控的相位旋转门 $R_z$ 完成算术运算，再通过逆QFT转回计算基。
*   **优点**：由于无需像经典计算机那样处理相邻比特间的进位传播延迟，QFT加法器在某些情况下可以实现 $O(\log N)$ 的极浅电路深度。对于不受连接拓扑约束的理想量子硬件，它具有极高的理论并行度。
*   **缺点**：QFT算术依赖大量不同角度的连续相位旋转门。在容错量子计算体系（如表面码）中，这些非Clifford操作（任意角度旋转）无法直接执行，必须将其分解为大量的T门或使用庞大的可编程态注入。这导致其底层实现的真实资源开销极其庞大，容错开销的常数因子远大于进位架构。

**2. 基于进位传播的算术架构**
这种架构直接映射经典的数字电路逻辑（如行波进位加法器或超前进位加法器）到量子门序列，主要由Toffoli、CNOT和X门构成。
*   **优点**：完全基于标准的Clifford+T门集。在容错量子计算中，Toffoli门的编译机制非常成熟且开销确定。同时，这种架构与现有NISQ设备的硬件直连拓扑兼容性更好，便于进行硬件感知的布线优化，从而减少SWAP操作的开销。
*   **缺点**：由于进位信号必须在O(n)个量子比特间依次传播，其串行特质使得电路深度至少随比特数呈线性增长，导致较长的退相干时间要求。此外，执行模乘运算通常需要大量的辅助比特来暂存进位，空间开销较大。

**适用场景总结**：
在目前的NISQ时代及早期容错量子计算阶段，由于受限于硬件的连通性和纠错码的极高代价，**基于进位传播的算术架构**是Shor算法模幂运算更可行、更主流的实现方案；而**基于QFT的算术架构**更多停留在理论探讨阶段，通常只在极高连接度且能容忍相位近似误差的专用架构中考虑。

以下是在isQ语言中展示如何利用受控模乘法模块构建Shor算法中模幂运算顶层逻辑的代码示例。代码通过循环控制结构，利用指数寄存器 `q_x` 的每一个量子位，条件性地对目标寄存器 `q_y` 执行模乘法操作：

```isq
import std;

// 声明全局量子寄存器
// q_x: 存储指数 x 的 n 位寄存器
// q_y: 存储模幂结果的工作寄存器，初始化为 |1>
qbit q_x[4];
qbit q_y[4];

// 声明抽象的受控模乘法操作门
// 在实际底层实现中，此处将被替换为基于进位传播或QFT的加法/乘法网络
// 参数 i 代表当前正在处理第 i 位，底数常数 a 和模数 N 隐藏在门的黑盒实现中
deriving gate CModMult_i = [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]; // 占位单位阵

procedure main() {
    // 初始化工作寄存器 q_y 为 |1> (即 |0001>)
    X(q_y[0]);

    // 遍历指数寄存器的每一位
    // 根据公式，若 x_i 为 1，则 q_y 累乘 a^{2^i} mod N
    for i in 0:4 {
        // 利用 isQ 的控制语法，以 q_x[i] 为控制位执行模乘
        // 如果 q_x[i] 处于 |1> 态，则对 q_y 执行受控模乘法
        ctrl @[q_x[i]] CModMult_i(q_y);
    }
}
```
在上述代码结构中，受控模乘门 `CModMult_i` 充当核心组件，其实际的物理硬件映射即可根据设备的容错能力在 QFT算术架构 或 进位传播算术架构 中灵活切换。

## isqTrain/60

- task_id: `isqTrain/60`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `63`

### Prompt

Write isQ code for the following quantum task: implements the phase_kickback pattern using an alternative gate decomposition (CNOT -> H CZ H). The circuit must produce the same output as the standard decomposition.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement phase kickback using CNOT = H·CZ·H decomposition, producing the same output as a standard CNOT-based phase kickback circuit.

2. **Qubits**: 2 qubits (q[0] = control, q[1] = target); both measured.

3. **State evolution**:
   - **|00⟩** → X(q[1]) → **|01⟩** → H(q[1]) → **|0⟩|−⟩** → H(q[0]) → **|+⟩|−⟩** = ½(|00⟩−|01⟩+|10⟩

## isqTrain/2679

- task_id: `isqTrain/2679`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_oracle`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2498`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;
oracle bool[1] constant(bool a[4]) {
    bool res[] = [true];
    return res;
}
qbit q[4], anc[1];

procedure main()
{
    X(anc[0]);
    H(q);
    H(anc[0]);
    constant(q, anc);
    H(q);
    print M(q);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Role:** Quantum computing expert.
    *   **Task:** Analyze an isQ program and predict its measurement probability distribution.
    *   **Input Program:** Deutsch-Jozsa algorithm for a constant oracle.
    *   **Output format:** "## Circuit Analysis" followed by a concise, precise step-by-step reasoning (3-8 lines), ending with the predicted probability distribution as a JSON array of floats.
    *   **Constraints:** Use Dirac notation, be concise, do not include code blocks, output ONLY the analysis.

2.  **Analyze the isQ Program:**
    *   **Qubits:** `q[4]` (input register), `anc[1]` (ancilla).
    *   **Initial state:** |00000> (q0, q1, q2, q3, anc)
    *   **Gate sequence:**
        *   `X(anc[0])`: Flips ancilla to |1>. State: |0000>_q ⊗ |1>_anc.
        *   `H(q)`: Hadamard on all 4 input qubits. State: |++++>_q ⊗ |1>_anc.
        *   `H(anc[0])`: Hadamard on ancilla. State: |++++>_q ⊗ |->_anc.
        *   `constant(q, anc)`: Oracle application. The oracle returns `[true]` regardless of input `a[4]`. This corresponds to a phase kickback of (-1)^1 = -1 to the ancilla state, or applying a phase of -1 to the whole state for any input. Actually, let's trace exactly: Oracle maps |x>|y> -> |x>|y XOR f(x)>. Since f(x) = 1 for all x, it maps |x>|0> -> |x>|1> and |x>|1> -> |x>|0>.
            *   Initial ancilla state: |-> = 1/sqrt(2) (|0> - |1>).
            *   Applying X to ancilla: X|-> = 1/sqrt(2) (|1> - |0>) = - |->.
            *   Thus, the state becomes -|++++>_q ⊗ |->_anc (global phase of -1).
        *   `H(q)`: Hadamard on all 4 input qubits.
            *   H|+> = |0>.
            *   So, H^{\otimes 4}|++++> = |0000>.
            *   Total state: -|0000>_q ⊗ |->_anc.
        *   `M(q)`: Measure only the input qubits `q[0..3]`.
    *   **Measurement Probabilities:**
        *   The input register is exactly in the state |0000>.
        *   Probability of measuring 0000 is 1.0 (100%).

3.  **Draft the Step-by-Step Reasoning:**
    *   Step 1: Initialization. |0000>|1> after `X(anc[0])`.
    *   Step 2: Superposition. Apply `H(q)` and `H(anc)`. The state becomes |++++>|-> = H^{\otimes 4}|0000> ⊗ |->.
    *   Step 3: Oracle. `constant(q, anc)` always flips the ancilla. Since ancilla is in |->, it acquires a phase of -1. State becomes -|++++>|->.
    *   Step 4: Interference. Apply `H(q)`. State becomes -|0000>|->.
    *   Step 5: Measurement. Measure `q`. The state is deterministically |0000>.

4.  **Format the Output:**
    *   Follow the JSON array requirement. The prompt specifically asks for a JSON array of floats representing the probabilities, but also "Output ONLY the analysis, starting with "## Circuit Analysis" ... End with the predicted probability distribution". Wait, the prompt says "Return the probability vector as a JSON array of floats" in the prompt description, but the Rules say "End with the predicted probability distribution". Let's provide the text analysis and end with the probability distribution formatted clearly, perhaps as the JSON array.
    *   Let's keep the analysis 3-8 lines.
    *   "End with the predicted probability distribution". Example format: `[1.0, 0.0, 0.0, ...]` for a 4-qubit system is length 16.
    *   Wait, The implementation says: `Expected measurement probabilities: {'0000': 1.0}`. I should ensure I list the full array or a clear representation. A 16-element array is `[1.0

### Reference answer

{'predicted_probs': {'0000': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/918

- task_id: `isqTrain/918`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `boolean_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2630`

### Prompt

实现以下量子计算任务（使用isQ）：implements a variant of the boolean_synthesis pattern using q[3] -> q[5]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement boolean XNOR synthesis with inputs a=1, b=1 using a 5-qubit register, where q[3] and q[4] remain in the ground state.

2. **Qubits**: 5 qubits (q[0] to q[4]), all measured. Inputs encoded in q[0] and q[1], result computed into q[2], and q[3]-q[4] are idle ancillas.

3. **State evolution**:
   - Start: |00000⟩
   - X(q[0]), X(q[1]): |11000⟩ (encode inputs a=1, b=1)
   - CNOT(q[0], q[2]): |11100⟩ (q[2] = 0 ⊕ 1 = 1)
   - CNOT(q[1], q[2]): |11000⟩ (q[2] = 1 ⊕ 1 = 0, computing XOR)
   - X(q[2]): |11100⟩ (negate to get XNOR = NOT(0) = 1)

4. **Expected probabilities**: The final state is |11100⟩ with certainty, so measurement yields {|11100⟩: 1.0}. The two ancilla qubits remain |00⟩ throughout since no gates act on them.

## isqTrain/2947

- task_id: `isqTrain/2947`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `basis_change`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3159`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;
qbit q[2];
procedure main() {
    X(q[0]);
    X(q[1]);
    H(q[0]);
    H(q[1]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the isQ program**:
    *   `qbit q[2];` initializes a 2-qubit system in state |00>.
    *   `X(q[0]);` applies X to q0. State becomes |10>.
    *   `X(q[1]);` applies X to q1. State becomes |11>.
    *   `H(q[0]);` applies H to q0. State becomes (1/sqrt(2))(|01> - |11>).
    *   `H(q[1]);` applies H to q1. State becomes 1/2 (|00> - |01> - |10> + |11>). Wait, let's trace carefully.

2.  **Trace State Evolution**:
    *   Initial: $|00\rangle$
    *   After `X(q[0])`: $|10\rangle$
    *   After `X(q[1])`: $|11\rangle$
    *   After `H(q[0])`: $H|1\rangle \otimes |1\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) \otimes |1\rangle = \frac{1}{\sqrt{2}}(|01\rangle - |11\rangle)$. Wait, the standard is to write q[0] as the first qubit, so $|q_0\rangle \otimes |q_1\rangle$. Or is it $|q_1\rangle \otimes |q_0\rangle$? Let's stick to $q_0$ being the first index.
    *   Let's use $q_0 q_1$. Initial: $|00\rangle$.
    *   `X(q[0])`: $|10\rangle$
    *   `X(q[1])`: $|11\rangle$
    *   `H(q[0])`: $\frac{1}{\sqrt{2}}(|01\rangle - |11\rangle)$. Wait. $H|1\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$. So if it was $|11\rangle$, it becomes $\frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) \otimes |1\rangle = \frac{1}{\sqrt{2}} (|01\rangle - |11\rangle)$. Wait, no. If $|11\rangle = |1_0\rangle |1_1\rangle$. Then applying H to $q_0$ yields $\frac{1}{\sqrt{2}}(|0_0\rangle - |1_0\rangle) |1_1\rangle = \frac{1}{\sqrt{2}}(|01\rangle - |11\rangle)$. Yes.
    *   `H(q[1])`: Apply H to $q_1$. We have $\frac{1}{\sqrt{2}} (|0_0\rangle |1_1\rangle - |1_0\rangle |1_1\rangle)$.
        Apply H to $q_1$: $\frac{1}{\sqrt{2}} (|0_0\rangle \frac{1}{\sqrt{2}}(|0_1\rangle - |1_1\rangle) - |1_0\rangle \frac{1}{\sqrt{2}}(|0_1\rangle - |1_1\rangle))$
        $= \frac{1}{2} (|00\rangle - |01\rangle - |10\rangle + |11\rangle)$.
    *   Squared amplitudes are all $(1/2)^2 = 1/4$.
    *   Probabilities are all 0.25.

3.  **Draft the Explanation**:
    *   *Step 1*: Initial state $|00\rangle$.
    *   *Step 2*: `X(q[0])` and `X(q[1])` flip both qubits to $|11\rangle$.
    *   *Step 3*: `H(q[0])` puts $q_0$ into $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$. State becomes $\frac{1}{\sqrt{2}}(|01\rangle - |11\rangle)$.
    *   *Step 4*: `H(q[1])` puts $q_1$ into $|-\rangle$. The tensor product $|-\rangle \otimes |-\rangle$ yields $\frac{1}{2}(|00\rangle - |01\rangle - |10\rangle + |11

### Reference answer

{'predicted_probs': {'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/345

- task_id: `isqTrain/345`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `2609`

### Prompt

I need an isQ program to implements a variant of the arithmetic_circuit pattern using p[2] -> p[3]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

Looking at this problem, I need to generate an isQ program that implements a variant of the arithmetic_circuit pattern with p[2] -> p[3], using an expanded qubit register.

Let me analyze The implementation:
- It has qbit c[1] (control qubit) and qbit p[3] (3 qubits for the register)
- DEC procedure: X(p0), then CNOT(p0, p1)
- INC procedure: CNOT(p0, p1), then X(p0)
- Main circuit:
  1. H(c[0]) - puts control in superposition
  2. ctrl INC(c[0], p[0], p[1]) - apply INC controlled by c[0]
  3. nctrl DEC(c[0], p[0], p[1]) - apply DEC when c[0] is |0>
  4. M(p[0]), M(p[1]), M(p[2]) - measure 3 qubits

Let me trace the state evolution:

Initial state: |0>_c ⊗ |000>_p

After H(c[0]):
(1/√2)(|0> + |1>)_c ⊗ |000>_p = (1/√2)(|0000> + |1000>)

Now let's understand INC and DEC:
- DEC(q0, q1): X(q0), CNOT(q0, q1)
  - |00> → |10> → |11>
  - |01> → |11> → |10>
  - |10> → |00> → |00>
  - |11> → |01> → |01>
  
- INC(q0, q1): CNOT(q0, q1), X(q0)
  - |00> → |00> → |10>
  - |01> → |01> → |11>
  - |10> → |11> → |01>
  - |11> → |10> → |00>

Wait, let me reconsider. Looking at p[2] -> p[3], this might mean using p[0], p[1], p[2] and some operation involves p[2] -> p[3] but we only have p[3]? Let me re-read.

Actually, looking at "p[2] -> p[3]" - the reference has p[3] declared (3 qubits: p[0], p[1], p[2]). The pattern might mean the expanded register uses indices p[2] to p[3] which would be... hmm, that doesn't quite make sense.

Let me just trace through the given circuit implementation:

Initial: |0>_c |000>_p = |0000>

After H(c[0]):
1/√2 (|0> + |1>)_c |000>_p = 1/√2 (|0000> + |1000>)

ctrl INC(c[0], p[0], p[1]):
- When c[0] = |0>, nothing happens
- When c[0] = |1>, apply INC(p[0], p[1])

INC(p[0], p[1]) on |00>: CNOT(p0,p1) gives |00>, then X(p0) gives |10>
So |1000> → |1110> (where last bit is p[0]=1, second to last is p[1]=1... wait let me be more careful)

Let me order as c, p[0], p[1], p[2]:
- |0>_c |0>_{p0} |0>_{p1} |0>_{p2}

After H(c[0]): 1/√2(|0000> + |1000>) where order is c, p0, p1, p2

ctrl INC(c[0], p[0], p[1]):
- |0000> stays |0000> (control is 0)
- |1000>: INC on p0,p1 which are |00>. CNOT(p0,p1) → |00>, X(p0) → |10>. So p0=1, p1=0.
  Result: |1010>

State: 1/√2(|0000> + |1010>)

nctrl DEC(c[0], p[0], p[1]):
- When c[0] = |0>, apply DEC
- When c[0] = |1>, nothing

DEC(p[0], p[1]) on |00>: X(p0) → |10>, CNOT(p0,p1) → |11>
So |0000> → |0110>

State: 1/√2(|0110> + |1010>

## isqTrain/3726

- task_id: `isqTrain/3726`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `5201`

### Prompt

用isQ实现QAOA (p=1) for MaxCut on a 4-node star graph with edges [(0, 1), (0, 2), (0, 3)], gamma=0.500, beta=0.500. Use CNOT-Rz-CNOT for cost unitary and Rx for mixer.

### Chain-of-thought reasoning

## Reasoning
1.  **Goal:** Implement a single-layer QAOA (p=1) circuit to find the maximum cut of a 4-node star graph.
2.  **Qubits:** 4 qubits are used (q[0] to q[3]), and all are measured to output a 4-bit string representing the partition.
3.  **State Evolution:**
    *   Initialize in the ground state $|0000\rangle$.
    *   Apply Hadamard gates to all qubits, creating a uniform superposition: $|+\rangle^{\otimes 4} = \frac{1}{4}\sum_{x \in \{0,1\}^4} |x\rangle$.
    *   Apply the cost unitary for each edge $(0,1), (0,2), (0,3)$ using CNOT-Rz(1.0)-CNOT sequences. This entangles the qubits and applies phase shifts $e^{-0.5i(-1)^{x_0 \oplus x_k}}$ to each basis state $|x_0x_1x_2x_3\rangle$ based on the number of cut edges.
    *   Apply the mixer unitary $Rx(1.0)$ to all qubits, which rotates the state around the X-axis, interfering the phases to amplify the amplitudes of states with large cut sizes.
4.  **Expected Probabilities:** The final state probabilities reflect the interference pattern optimized for MaxCut. States like $|0111\rangle$ and $|1000\rangle$ (which partition the nodes to maximize cut edges) and $|0000\rangle$ and $|1111\rangle$ (due to symmetric phase properties) have the highest probabilities, while balanced partitions like $|0011

## isqTrain/2823

- task_id: `isqTrain/2823`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_for_loop`, `isq_syntax_multi_register`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2437`

### Prompt

This isQ program compiles but produces incorrect probabilities. Find and correct the mistake.

```isq
import std;
qbit q[3];
// Create a 3-qubit GHZ state
procedure main() {
    H(q[0]);
    for i in 1:3 {
        // CNOT(q[i-1], q[i]); // BUG: missing CNOT
    }
    for i in 0:3 {
        M(q[i]);
    }
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **Bug**: The `CNOT(q[i-1], q[i])` line is commented out with `//`, so the entangling loop executes no gates. After `H(q[0])`, the state is `(|000⟩ + |100⟩)/√2` — qubits 1 and 2 remain unentangled, yielding measurement probabilities {|000⟩: 0.25, |100⟩: 0.25, |010⟩: 0.0, ...} instead of the GHZ state.

2. **Fix**: Uncomment the CNOT line: `CNOT(q[i-1], q[i]);` so that in the `for i in 1:3` loop, both iterations (i=1 and i=2) apply a CNOT, entangling all qubits.

3. **Corrected state evolution**: `|000⟩` → H(q[0]) → `(|000⟩ + |100⟩)/√2` → CNOT(q[0],q[1]) → `(|000⟩ + |110⟩)/√2` → CNOT(q[1],q[2]) → `(|000⟩ + |111⟩)/√2`, confirming the 3-qubit GHZ state with expected measurement probabilities {|000⟩: 0.5, |111⟩: 0.5}.

## isqTrain/3041

- task_id: `isqTrain/3041`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `217`

### Prompt

帮我写一个isQ程序：defines a `bellpair` procedure using the `deriving gate` syntax. The procedure creates a Bell pair from two qubits. Use it to create two independent Bell pairs and measure all 4 qubits.

Requirements:
- Use `deriving gate` on the bellpair procedure.
- Declare `qbit q[4];` at global scope.
- Measure all 4 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create two independent Bell pairs (q[0]-q[1] and q[2]-q[3]) and measure all qubits.
2. **Qubits**: 4 qubits declared globally, all measured.
3. **State evolution**:
   - Initial: |0000⟩
   - H(q[0]): (|0⟩+|1⟩)/√2 ⊗ |0⟩ ⊗ |00⟩ = (|0000⟩+|1000⟩)/√2
   - CNOT(q[0],q[1]): (|0000⟩+|1100⟩)/√2 — first Bell pair
   - H(q[2]): (|0000⟩+|0010⟩+|1100⟩+|1110⟩)/2
   - CNOT(q[2],q[3]): (|0000⟩+|0011⟩+|1100⟩+|1111⟩)/2 — second Bell pair
4. **Expected probabilities**: The final state is an equal superposition of |0000⟩, |0011⟩, |1100⟩, |1111⟩, each with amplitude 1/2, giving probability 0.25 each. Qubits within each pair are perfectly correlated, but the two pairs are independent.

## isqTrain/692

- task_id: `isqTrain/692`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1792`

### Prompt

实现以下量子计算任务（使用isQ）：implements the half_full_adder pattern but with a different initial state preparation (flip q[[0, 1, 2]] -> q[3]).

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement a full adder circuit where q[3] is initialized to |1⟩ (instead of q[0], q[1], q[2]) to compute sum and carry_out with inputs a=0, b=0, carry_in=0.

2. **Qubits**: 5 qubits (q[0]-q[4]); q[3] (sum) and q[4] (carry_out) are measured.

3. **State evolution**:
   - Initial: |00000⟩
   - X(q[3]): |00010⟩ — q[3] set to 1
   - CNOT(q[0], q[3]): No change (q[0]=0) → |00010⟩
   - CNOT(q[1], q[3]): No change (q[1]=0) → |00010⟩
   - CNOT(q[2], q[3]): No change (q[2]=0) → |00010⟩
   - Toffoli(q[0], q[1], q[4]): No change (q[0]=q[1]=0) → |00010⟩
   - Toffoli(q[0], q[2], q[4]): No change (q[0]=q[2]=0) → |00010⟩
   - Toffoli(q[1], q[2], q[4]): No change (q[1]=q[2]=0) → |00010⟩

4. **Final state**: |00010⟩, so M(q[3])=1, M(q[4])=0. With q[3] as the higher bit, the measurement bitstring is |10⟩ with probability 1.0, since no gates activate due to all inputs being 0 while q[3] remains in its initialized |1⟩ state.
