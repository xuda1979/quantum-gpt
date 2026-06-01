# ISQ training COT RAG corpus: quantum_algorithms shard 91

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqQA/quantum_algorithms/51_math_derivation

- task_id: `isqQA/quantum_algorithms/51_math_derivation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `math_derivation`, `algorithm`, `隐藏子群问题`
- source: `qa_pipeline`
- dataset_index: `5218`

### Prompt

请详细推导有限阿贝尔群上隐藏子群问题的标准量子算法。要求包含从初态到测量后的量子态演化过程，特别是引入量子傅里叶变换后的严密数学推导，并解释为什么这种概率分布能够成功提取出隐藏子群的信息。

### Reference answer

<think>
隐藏子群问题（HSP）的推导逻辑主要分为三个阶段：态制备与坍缩、傅里叶变换映射、以及对偶空间抽样。

首先，均匀叠加态经过黑箱函数演化后，测量第二寄存器。由于函数 $f$ 的等价关系，第一寄存器会坍缩至某个随机陪集 $g_0H$ 的均匀叠加态。

推导的核心在于对第一寄存器应用群 $G$ 上的量子傅里叶变换（QFT）。利用阿贝尔群的性质，QFT将群元素映射为特征标（Character）。在数学上，将QFT作用于陪集态时，会在特征标空间产生强烈的干涉现象：所有在隐藏子群 $H$ 上求和相位不为常数的特征标会发生完全的相消干涉（振幅为零），而满足在 $H$ 上恒为1的特征标（即属于正交群 $\hat{H}^\perp$ 的元素）则会发生相长干涉。

此时测量第一寄存器，得到的态必定严格落在 $\hat{H}^\perp$ 内，且呈现均匀分布。每次测量等价于获得一个关于子群 $H$ 结构的线性约束方程，多次运行算法收集足够多线性无关的约束后，即可通过经典线性代数求解还原出隐藏子群 $H$ 的生成元。
</think>

隐藏子群问题是量子计算中最核心的框架之一，能够涵盖Shor算法和Simon算法。假设存在一个有限阿贝尔群 $G$，其隐藏子群为 $H \le G$。给定一个黑箱函数 $f: G \to X$，满足性质：对于任意 $g_1, g_2 \in G$，$f(g_1) = f(g_2)$ 当且仅当 $g_1$ 和 $g_2$ 属于同一个陪集，即 $g_1 H = g_2 H$。我们的目标是找出 $H$ 的生成元。

量子算法的第一步是初始化两个寄存器，第一寄存器维度为 $|G|$，第二寄存器足以容纳函数值 $f(g)$，初始态为 $|0\rangle|0\rangle$。
对第一寄存器进行量子傅里叶变换的逆变换或Hadamard变换，使其处于均匀叠加态：
$$|\psi_0\rangle = \frac{1}{\sqrt{|G|}} \sum_{g \in G} |g\rangle |0\rangle$$

接着，调用量子黑箱 $U_f$ 计算函数 $f$。由于 $U_f|g\rangle|0\rangle = |g\rangle|f(g)\rangle$，系统演化为：
$$|\psi_1\rangle = \frac{1}{\sqrt{|G|}} \sum_{g \in G} |g\rangle |f(g)\rangle$$

由于函数 $f$ 在陪集上是常数，我们可以将求和重新按陪集 $cH$ 进行分组。任意 $g \in cH$ 都可以写成 $g = ch$ ($h \in H$)。选取特定陪集 $cH$ 并展开，此时状态可以改写为：
$$|\psi_1\rangle = \frac{1}{\sqrt{|G|}} \sum_{cH} \sum_{h \in H} |ch\rangle |f(ch)\rangle$$
因为 $|cH| = |H|$，这表现为各个陪集对应函数值的纠缠态。

第二步，我们测量第二个寄存器，假设测得的结果为 $y = f(c_0 H)$。由于各个陪集正交且概率均等，测量的概率为 $|H|/|G|$。测量后，第一寄存器的波函数坍缩到对应的陪集叠加态（忽略全局相位）：
$$|\psi_2\rangle = \frac{1}{\sqrt{|H|}} \sum_{h \in H} |c_0 + h\rangle$$
此时我们得到了一个关于隐藏子群 $H$ 均匀平移的叠加态。

第三步，对第一寄存器应用群 $G$ 上的量子傅里叶变换 (QFT)。QFT 的作用定义为：$\text{QFT}|x\rangle = \frac{1}{\sqrt{|G|}} \sum_{\xi \in \hat{G}} e^{2\pi i x \cdot \xi / |G|} |\xi\rangle$，其中 $\hat{G}$ 是 $G$ 的对偶群（特征标群）。将此作用于 $|\psi_2\rangle$，态演化为：
$$|\psi_3\rangle = \frac{1}{\sqrt{|H|}} \sum_{h \in H} \left( \frac{1}{\sqrt{|G|}} \sum_{\xi \in \hat{G}} e^{2\pi i (c_0+h) \cdot \xi} |\xi\rangle \right) = \frac{1}{\sqrt{|H||G|}} \sum_{\xi \in \hat{G}} e^{2\pi i c_0 \cdot \xi} \left( \sum_{h \in H} e^{2\pi i h \cdot \xi} \right) |\xi\rangle$$

最后，计算测量第一寄存器得到状态 $|\xi\rangle$ 的概率 $P(\xi)$。概率幅完全由括号内的内积决定：
$$P(\xi) = \left| \frac{1}{\sqrt{|H||G|}} \sum_{h \in H} e^{2\pi i h \cdot \xi} \right|^2 = \frac{1}{|H||G|} \left| \sum_{h \in H} e^{2\pi i h \cdot \xi} \right|^2$$
现在需要分析求和项 $\sum_{h \in H} e^{2\pi i h \cdot \xi}$。定义 $H$ 的零化特征标子群（正交子群）为 $H^{\perp} = \{\xi \in \hat{G} \mid \forall h \in H, e^{2\pi i h \cdot \xi} = 1\}$。
1. 如果 $\xi \in H^{\perp}$，则对任意 $h \in H$，相位因子 $e^{2\pi i h \cdot \xi} = 1$。因此，求和项等于 $|H|$。此时概率为：$P(\xi) = \frac{1}{|H||G|} |H|^2 = \frac{|H|}{|G|}$。
2. 如果 $\xi \notin H^{\perp}$，则必然存在某个 $h_0 \in H$，使得 $e^{2\pi i h_0 \cdot \xi} \neq 1$。根据群的封闭性，集合 $\{h \mid h \in H\}$ 和集合 $\{h+h_0 \mid h \in H\}$ 完全等价。因此，求和项可以写为：$S = \sum_{h \in H} e^{2\pi i h \cdot \xi} = \sum_{h \in H} e^{2\pi i (h+h_0) \cdot \xi} = e^{2\pi i h_0 \cdot \xi} \sum_{h \in H} e^{2\pi i h \cdot \xi} = e^{2\pi i h_0 \cdot \xi} S$。
由于 $e^{2\pi i h_0 \cdot \xi} \neq 1$，方程 $S = e^{2\pi i h_0 \cdot \xi} S$ 只有两个解：要么 $S=0$，要么不成立。因此必定有 $S = 0$。此时概率 $P(\xi) = 0$。

推导结论：经过QFT后，非 $H^{\perp}$ 元素的测量概率严格为0，系统以 100% 的概率坍缩到 $\xi \in H^{\perp}$ 的态上，且每个符合条件的态概率均等，为 $\frac{|H|}{|G|}$。因为 $|H^{\perp}| = \frac{|G|}{|H|}$，所有概率之和正好为1。
通过多次重复该量子线路，我们能够获得足够多的 $H^{\perp}$ 中的特征标样本，随后利用经典的后处理（如求解线性方程组或求高斯核），即可由 $H^{\perp}$ 反推得到隐藏子群 $H$。这正是量子算法解决HSP及大数质因数分解问题的核心加速机制所在。

## isqTrain/745

- task_id: `isqTrain/745`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`, `phase_manipulation`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `5790`

### Prompt

请用isQ语言编写一个量子电路：implements the qft_adder pattern but with a different initial state preparation (flip q[[0]] -> q[1]).

### Chain-of-thought reasoning

Let me analyze this QFT adder circuit step by step.

**Goal**: The circuit implements a QFT-based adder that adds constant 1 to the input, with the input being prepared by flipping q[1] (instead of q[0]).

**Qubits**: 2 qubits, both measured.

**Initial state preparation**:
- Start: |00>
- X(q[1]): |10> (flips q[1], not q[0] as in the reference)

**Forward QFT on 2 qubits**:
The QFT swaps the order and applies Hadamard and controlled phase gates. Let me trace through:

1. Start: |10> (q[0]=1, q[1]=0)

2. H(q[1]): |1> ⊗ H|0> = |1> ⊗ |+> = (1/√2)(|10> + |11>)

3. ctrl S(q[0], q[1]): When q[0]=1, apply S to q[1]
   - |10> stays |10> (q[0]=1, S applied to |0> = |0>)
   - |11> stays |11> (q[0]=1, S applied to |1> = i|1>)
   Wait, let me reconsider. S|0> = |0>, S|1> = i|1>
   So: (1/√2)(|10> + i|11>)

4. H(q[0]): Apply H to q[0]
   - H|1> = |->
   So: (1/√2)((1/√2)(|00> - |10>) + i(1/√2)(|01> - |11>))
   = (1/2)(|00> - |10> + i|01> - i|11>)

Now in Fourier domain, we add constant 1:

5. Rz(π, q[0]): Phase rotation on q[0]
   Rz(π)|0> = -i|0>, Rz(π)|1> = i|1>
   
   Wait, let me be more careful. Rz(θ) = [[1,0],[0,e^(iθ)]]
   So Rz(π)|0> = |0>, Rz(π)|1> = -|1>
   
   Applying to q[0]:
   = (1/2)(|00> - |10> + i|01> - i|11>) with q[0] getting phase e^(iπ) = -1 when |1>
   = (1/2)(|00> + |10> + i|01> + i|11>)
   
   Wait, let me reconsider. Rz(θ) = diag(1, e^(iθ))
   So Rz(π) = diag(1, -1)
   
   On q[0]: terms where q[0]=1 get multiplied by -1:
   (1/2)(|00> - (-1)|10> + i|01> - i(-1)|11>)
   = (1/2)(|00> + |10> + i|01> + i|11>)

6. Rz(π/2, q[1]): Phase rotation on q[1]
   Rz(π/2) = diag(1, i)
   
   On q[1]: terms where q[1]=1 get multiplied by i:
   = (1/2)(|00> + |10> + i·i|01> + i·i|11>)
   = (1/2)(|00> + |10> - |01> - |11>)

Now inverse QFT:

7. H(q[0]): Apply H to q[0]
   = (1/2)(H(|0>+|1>)⊗|0> + H(-|0>-|1>)⊗|1>)
   Wait, let me be more careful:
   
   |00> + |10> = (|0>+|1>)⊗|0>, and -|01> - |11> = -(|0>+|1>)⊗|1>
   So = (1/2)((|0>+|1>)⊗|0> - (|0>+|1>)⊗|1>)
   
   H(|0>+|1>) = √2|0> + 0 = √2|0>
   
   So after H(q[0]):
   = (1/2)(√2|00> - √2|01>)
   = (1/√2)(|00> - |01>)
   = (1/√2)|0>(|0>-|1>)
   = |0>⊗|->

## isqTrain/47

- task_id: `isqTrain/47`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_arrays`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2939`

### Prompt

I need an isQ program to implements a variant of the oracle_boolean pattern using q[3] -> q[4]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning
* **Goal**: Implement a balanced oracle variant using a 4-qubit register and measure all qubits.
* **Qubits**: Uses 4 qubits (`q[0]` to `q[3]`), all of which are measured to yield a 4-bit classical string.
*

## isqTrain/3482

- task_id: `isqTrain/3482`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1804`

### Prompt

Code this in isQ: the controlled-S gate using CNOT and T gates in isQ.

CS = ctrl S decomposed as:
  T(q[0]); T(q[1]); CNOT(q[0],q[1]); Rz(-pi/4, q[1]); CNOT(q[0],q[1]);

Test: q[0]=|1>, q[1]=|1>. Then apply H(q[1]) and measure.
The S on |1> gives phase i; this affects the H measurement result.

Declare 2 qubits, measure both.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement controlled-S gate via CNOT+T decomposition on |11>, then probe the acquired phase i with H and measurement.

2 qubits needed (q[0]=control, q[1]=target), both measured.

State evolution:
- |00⟩ → X,X → |11⟩
- T(q[0]): e^(iπ/4)|11⟩; T(q

## isqTrain/3885

- task_id: `isqTrain/3885`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `677`

### Prompt

Fix the bug in this quantum program:

```
import std;
// QAOA MaxCut p=1 on 4-node star graph
// gamma=0.500, beta=0.500
qbit q[4];

procedure main() {
    // Superposition
    H(q[0]); H(q[1]); H(q[2]); H(q[3]);
    // Cost unitary
    // Edge (0,1)
    CZ(q[0], q[1]);
    Rz(2.0 * 0.500, q[1]);
    CNOT(q[0], q[1]);
    // Edge (0,2)
    CNOT(q[0], q[2]);
    Rz(2.0 * 0.500, q[2]);
    CNOT(q[0], q[2]);
    // Edge (0,3)
    CNOT(q[0], q[3]);
    Rz(2.0 * 0.500, q[3]);
    CNOT(q[0], q[3]);
    // Mixer
    Rx(2.0 * 0.500, q[0]);
    Rx(2.0 * 0.500, q[1]);
    Rx(2.0 * 0.500, q[2]);
    Rx(2.0 * 0.500, q[3]);
    // Measure
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **What the bug is**: In the Edge (0,1) cost unitary section, the first gate is `CZ(q[0], q[1])` instead of `CNOT(q[0], q[1])`. The standard decomposition of the ZZ interaction $e^{-i\gamma Z_i Z_j}$ uses CNOT–Rz–CNOT, not CZ–Rz–CNOT.

2. **What the fix is**: Replace `CZ(q[0], q[1])` with `CNOT(q[0], q[1])` on line 11. This ensures all three edges use the same correct CNOT–Rz(2γ)–CNOT pattern.

3. **State evolution (corrected circuit)**:
   - After H on all qubits: |++++⟩ (equal superposition)
   - Edge (0,1) cost: CNOT(0,1)·Rz(2γ,1)·CNOT(0,1) applies $e^{-i\gamma Z_0 Z_1}$, entangling q0|q1 with phase
   - Edge (0,2) cost: same pattern applies $e^{-i\gamma Z_0 Z_2}$
   - Edge (0,3) cost: same pattern applies $e^{-i\gamma Z_0 Z_3}$
   - After full cost unitary: qubit 0 accumulates opposite phase to qubits 1,2,3 (star graph structure)
   - Mixer Rx(2β) on all qubits: rotates each qubit, with β=0.500 creating constructive/destructive interference
   - Resulting probabilities favor |0000⟩ and |1111⟩ (~0.256 each) — the poor cuts — while balanced cuts like |0111⟩ and |1000⟩ (~0.057) reflect the QAOA state with γ=β=0.5

## isqTrain/2062

- task_id: `isqTrain/2062`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `interference`, `isq_syntax_oracle`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1819`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
oracle bool[2] f(bool x[2]) {
    bool x0_xor_x1 = x[0] != x[1];
    bool res[] = [false, x0_xor_x1];
    return res;
}
qbit q[2];
qbit out[2];
procedure main() {
    H(q[0]); H(q[1]);
    f(q, out);
    H(q[0]); H(q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants a step-by-step analysis of an isQ quantum program that uses a Deutsch-Jozsa-like structure with an oracle, specifically analyzing the state evolution and predicting the measurement probabilities. The output must strictly follow the given format rules.

2.  **Analyze the isQ Code**:
    *   **Qubits**: `q[2]`, `out[2]`.
    *   **Oracle `f`**:
        *   Input: `bool x[2]`.
        *   Logic: `x0_xor_x1 = x[0] != x[1]`. `res = [false, x0_xor_x1]`.
        *   Meaning: If $x = (0,0)$ or $x = (1,1)$, $res = (0,0)$. If $x = (0,1)$ or $x = (1,0)$, $res = (0,1)$.
        *   In the context of isQ, an oracle `f(q, out)` essentially applies a unitary $U_f$ such that $U_f |x\rangle |y\rangle = |x\rangle |y \oplus f(x)\rangle$. Here $f(x)$ is a 2-bit output. Wait, isQ oracle returns a `bool[2]`. So $f(x_0, x_1) = (0, x_0 \oplus x_1)$.
        *   Wait, the oracle flips `out[1]` if $x_0 \oplus x_1 = 1$, and `out[0]` is always 0. But `out` is initialized to $|0\rangle$. If we aren't initializing `out` to $|+\rangle$, applying $U_f |x\rangle|00\rangle = |x\rangle|f(x)\rangle$. Wait, this isn't phase kickback!
        *   Wait, standard Deutsch-Jozsa requires the output qubit to be in $|1\rangle$ or $|-\rangle$ to get phase kickback. But here `out` is $|00\rangle$.
        *   Let's check the exact effect of `f(q, out)`. It calculates $y_{new} = y \oplus f(x)$. So $|x\rangle|00\rangle \to |x\rangle|f(x)\rangle$.
        *   Then $H(q[0]); H(q[1])$ is applied to `q[0], q[1]`.
        *   Let's trace it carefully.

3.  **Step-by-Step State Evolution**:
    *   Initial state: $|00\rangle_q |00\rangle_{out} = |0000\rangle$
    *   After `H(q[0]); H(q[1])`:
        $|+\rangle|+\rangle|00\rangle = \frac{1}{2} \sum_{x \in \{0,1\}^2} |x\rangle |00\rangle$
    *   Oracle `f(q, out)` is called. It maps $|x\rangle |y\rangle \to |x\rangle |y \oplus f(x)\rangle$.
        *   $f(00) = 00$
        *   $f(01) = 01$
        *   $f(10) = 01$
        *   $f(11) = 00$
        *   The state becomes: $\frac{1}{2} (|00\rangle|00\rangle + |01\rangle|01\rangle + |10\rangle|01\rangle + |11\rangle|00\rangle)$.
    *   Then `H(q[0]); H(q[1])` is applied to `q[0], q[1]`.
        *   $H^{\otimes 2}$ on `q` transforms $\sum_x (-1)^{?} |x\rangle$. But there's no $(-1)$ phase! The phase is not kicked back because $y=0$.
        *   Wait! In isQ, does `f(q, out)` map $|x\rangle |y\rangle \to |x\rangle |y \oplus f(x)\rangle$? Yes, that's standard for quantum oracles defined classically.
        *   Wait, the `res` is `[false, x0_xor_x1]`. Does the oracle apply a phase if the first output bit is false? No, it outputs boolean array, and isQ synthesizes a reversible circuit $y_i \oplus f_i(x)$.
        *   Actually, let's look at the standard Deutsch-Jozsa algorithm. If we don't initialize the output to $|1\r

### Reference answer

{'predicted_probs': {'00': 0.5, '11': 0.5}, 'explanation': "Simon's algorithm for s=11: P(|00>)=0.5, P(|11>)=0.5."}

## isqTrain/2793

- task_id: `isqTrain/2793`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4252`

### Prompt

这段isQ代码有bug，帮我找出并修复：

```isq
import std;

oracle bool[1] constant(bool a[4]) {
    bool res[] = [true];
    return res;
}

qbit q[4], anc[1];

procedure main()
{
    // X(anc[0]); // BUG: missing initialization
    H(q);
    H(anc[0]);
    constant(q, anc);
    H(q);
    print M(q);
}
```

### Chain-of-thought reasoning

The bug is clear: the `X(anc[0])` gate is commented out. In the Deutsch-Jozsa algorithm, the ancilla qubit needs to be initialized to |1> before applying the Hadamard gate to it, so that it becomes |-> (minus state). This is crucial for the phase kickback mechanism to work properly.

Let me trace through the corrected circuit:

1. Initial state: |0000>|0>
2. After X(anc[0]): |0000>|1>
3. After H(q) on all 4 qubits: (1/4) Σ|x>|1> where x ranges from 0000 to 1111
4. After H(anc[0]): (1/4) Σ|x]>|-> = (1/4) Σ|x>(|0>-|1>)/√2

Wait, let me redo this more carefully.

Initial state: |0000>|0>

After X(anc[0]): |0000>|1>

After H(q) on all 4 qubits: (1/4)(|0>+|1>)^4 ⊗ |1> = (1/4) Σ|x>|1>

After H(anc[0]): (1/4) Σ|x> ⊗ H|1> = (1/4) Σ|x> ⊗ (|0>-|1>)/√2 = (1/4) Σ|x> |->

The constant oracle with res=[true] applies a phase. For a constant-1 function, the oracle applies f(x) = 1 for all x, which means it phase-flips the ancilla for all inputs. Since anc is in |-> state, the phase kickback means every |x> gets a -1 phase: becomes (-1) Σ|x> |->

Wait, actually let me think about this more carefully. The oracle `constant` returns `true` for all inputs. How does this oracle work in isQ?

In the Deutsch-Jozsa algorithm, the oracle typically computes f(x) into the ancilla: |x>|b> → |x>|b ⊕ f(x)>

If ancilla is in |-> = (|0>-|1>)/√2, then:
- If f(x) = 0: |x>|-> → |x>|-> (no phase change)
- If f(x) = 1: |x>|-> → -|x>|-> (phase flip)

So for constant-1 function, every term gets a -1 phase:
State after oracle: (-1)(1/4) Σ|x> |->

The global phase doesn't matter, so this is equivalent to (1/4) Σ|x> |->

After H(q): H^4 applied to (1/4) Σ|x> gives |0000>

So measurement yields |0000> with probability 1.

Now if X(anc[0]) is missing, anc starts in |0>, and after H(anc[0]) it's in |+> = (|0>+|1>)/√2.

The oracle computes f(x) into ancilla: |x>|b> → |x>|b ⊕ f(x)>

For ancilla in |+>: f(x)=1 means |+> → |1⊕0>+|1⊕1> = |1>+|0> = |+>. No phase kickback!

So the oracle wouldn't impart any phase to the computational qubits, and the algorithm wouldn't work correctly.

Actually wait - let me reconsider. The state would be:
(1/4) Σ|x> |+> → (1/4) Σ|x> |+> (since f(x)=1 for all x, b⊕1 flips, but |+> is eigenstate of X, so... hmm)

Actually, for |+> = (|0>+|1>)/√2, applying b⊕1 gives (|1>+|0>)/√2 = |+>. So no change at all.

Then H(q) applied to (1/4) Σ|x> gives |0000>.

Hmm, so actually the measurement would still give |0000>... but that's only because this specific oracle is constant-1. Let me reconsider.

Wait, actually the oracle in isQ with `constant(q, anc)` - how exactly does it work? Let me look at the oracle definition:

This returns [true] for all inputs. In the isQ framework, an oracle `bool[1] constant(bool a[4])` applied as `constant(q, anc)` would typically implement:
|x>|anc> → (-1)^{f(x)} |x>|anc> (phase oracle)

Or it could be:

## isqTrain/768

- task_id: `isqTrain/768`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `555`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[4];

procedure main() {
    // Set both input qubits to |1>
    X(q[0]);
    X(q[1]);
    // Weight 1 contribution: add x0 to sum bit 0
    CNOT(q[0], q[2]);
    // Weight 2 contribution: add x1 to sum bit 1
    CNOT(q[1], q[3]);
    // Measure the 2-bit sum output
    M(q[2]);
    M(q[3]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initialization**: The 4-qubit system starts in the ground state |0000> (for q[0], q[1], q[2], q[3]).
2. **X Gates**: The `X(q[0])` and `X(q[1])` gates flip the first two qubits, evolving the state to |1100>.
3. **First CNOT**: `CNOT(q[0], q[2])` targets q[2] controlled by q[0]. Since q[0] is |1>, q[2] is flipped to |1>, changing the state to |1110>.
4. **Second CNOT**: `CNOT(q[1], q[3])` targets q[3] controlled by q[1]. Since q[1] is |1>, q[3] is flipped to |1>, resulting in the final state |1111>.
5. **Measurement**: Measuring q[2] and q[3] deterministically yields 1 for both qubits.

Predicted probability distribution: {|11>: 1.0}

### Reference answer

{'predicted_probs': {'3': 1.0}, 'explanation': 'Parametric variant of isqEval/282. Dimension: predict probabilities for reference circuit.'}

## isqTrain/3430

- task_id: `isqTrain/3430`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `qft_based_arithmetic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1335`

### Prompt

I need an isQ program to the Draper QFT-based adder in isQ computing 10 + 01 = 11 (2 + 1 = 3 in binary).

Use the same QFT adder structure:
1. QFT on b register
2. Controlled phase additions from a register
3. IQFT on b register

q[0..1] = a = 10 (LSB first, so a0=0, a1=1), q[2..3] = b = 01 (b0=1, b1=0).
Expected: a=10 unchanged, b=11 (3).
Declare 4 qubits, measure all.

### Chain-of-thought reasoning

Let me analyze this Draper QFT-based adder circuit step by step.

The goal is to implement a quantum adder that computes 2 + 1 = 3 using the Draper QFT adder approach.

Setup:
- q[0..1] = a register (a0=q[0], a1=q[1]) = 10 in binary = 2 (LSB first: a0=0, a1=1)
- q[2..3] = b register (b0=q[2], b1=q[3]) = 01 in binary = 1 (LSB first: b0=1, b1=0)

Initial state after X gates:
- |q[0]q[1]q[2]q[3]⟩ = |0110⟩

Wait, let me re-read:
- a = 10 (2 in decimal), LSB first means a0=0, a1=1
- b = 01 (1 in decimal), LSB first means b0=1, b1=0

So q[0]=0, q[1]=1, q[2]=1, q[3]=0
State: |q[0]q[1]q[2]q[3]⟩ = |0110⟩

Wait, that's |0⟩⊗|1⟩⊗|1⟩⊗|0⟩ = |0110⟩

Step 1: QFT on b register (q[2], q[3])

The QFT for 2 qubits:
H(q[2])
ctrl Rz(π/2, q[3], q[2])
H(q[3])
Then swap (three-CNOT decomposition) q[2], q[3] (using 3 CNOTs)

Actually wait, looking at the code more carefully:

QFT on b register:
H(q[2])
ctrl Rz(π/2, q[3], q[2]) - controlled phase from q[3] to q[2]
H(q[3])
swap (three-CNOT decomposition)(q[2], q[3]) using CNOTs

Starting b state: |b0,b1⟩ = |1,0⟩ = |10⟩ (but this is q[2]=1, q[3]=0)

After H(q[2]): q[2] goes from |1⟩ to H|1⟩ = |−⟩ = (|0⟩ - |1⟩)/√2
State: (|0⟩ - |1⟩)/√2 ⊗ |0⟩ for b part

After ctrl Rz(π/2, q[3], q[2]): This adds phase to q[2] when q[3]=1. Since q[3]=0, no change.
State still: (|0⟩ - |1⟩)/√2 ⊗ |0⟩

After H(q[3]): q[3] goes from |0⟩ to |+⟩
State: (|0⟩ - |1⟩)/√2 ⊗ (|0⟩ + |1⟩)/√2

After swap (three-CNOT decomposition)(q[2], q[3]):
State: (|0⟩ + |1⟩)/√2 ⊗ (|0⟩ - |1⟩)/√2

Hmm, let me be more careful. The QFT output should encode the value 1 (binary 01, LSB first: b0=1, b1=0).

Actually, let me reconsider. The QFT takes a computational basis state and maps it to the Fourier basis. For a 2-qubit QFT:

QFT|01⟩ (which is the state with q[2]=1, q[3]=0, or in binary notation for the register, value 1)

Wait, I need to be careful about the ordering. In the circuit:
- q[2] is b0 (LSB of b)
- q[3] is b1 (MSB of b)

The value b = b0 + 2*b1 = 1 + 2*0 = 1

So initial b state is |b0=1, b1=0⟩ where b0 is q[2] and b1 is q[3].

QFT maps |j⟩ → (1/√N) Σ_k e^{2πijk/N} |k⟩

For N=4 (2 qubits) and j=1:
QFT|1⟩ = (1/2)(|0⟩ + e^{2πi·1/4}|1⟩ + e^{2πi·2/4}|2⟩ + e^{2πi·3/4}|3⟩)
= (1/2)(|0⟩ + i|1⟩ - |2⟩ - i|3⟩)
= (1/2)(|00⟩ + i|01⟩ - |10⟩ - i

## isqQA/quantum_algorithms/96_isq_implementation

- task_id: `isqQA/quantum_algorithms/96_isq_implementation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_implementation`, `algorithm`, `Grover算法的扩散算子`
- source: `qa_pipeline`
- dataset_index: `4662`

### Prompt

请以3个量子比特为例，编写实现Grover算法中扩散算子的完整isQ代码，并详细解释其背后的数学原理与每一行代码的作用。

### Reference answer

<think>
首先，从数学层面解析Grover扩散算子 $U_s = 2|s\rangle\langle s| - I$。代入均匀叠加态 $|s\rangle = H^{\otimes n}|0\rangle^{\otimes n}$，可推导出 $U_s = H^{\otimes n}(2|0\rangle\langle 0| - I)H^{\otimes n}$。这揭示了量子线路的对称结构：两端需对3个量子比特施加Hadamard门，中间核心部分则是关于全零态的条件相移操作。

接着，分析中间条件相移的实现方式。直接控制全零态 $|000\rangle$ 不方便，可利用X门将计算基态反转，将条件转化为对全壹态 $|111\rangle$ 的操作，这在量子线路上对应一个多控Z门（CCZ门）。

最后，映射到isQ代码实现。基于上述推导，针对3个量子比特设计代码流程：声明量子比特 -> 施加H门 -> 施加X门进行基态反转 -> 应用CCZ门实现相位翻转 -> 再次施加X门恢复基态 -> 再次施加H门完成振幅放大。随后再结合数学原理对每一行代码进行匹配与详细解释。
</think>

Grover算法中的扩散算子，也称为关于平均值的反转操作，其核心作用是将各个量子态的振幅关于所有振幅的平均值进行反转。在数学上，扩散算子可以表示为 $U_s = 2|s\rangle\langle s| - I$，其中 $|s\rangle = H^{\otimes n}|0\rangle^{\otimes n}$ 是均匀叠加态。\n\n推导其分解过程如下：\n$U_s = 2(H^{\otimes n}|0\rangle^{\otimes n})(\langle 0|^{\otimes n}H^{\otimes n}) - I$ \n$U_s = H^{\otimes n}(2|0\rangle\langle 0| - I)H^{\otimes n}$ \n\n观察括号内的部分 $(2|0\rangle\langle 0| - I)$，这是一个条件相移算子，它对全零态 $|000...0\rangle$ 的相位保持不变（乘以+1），而对其他所有计算基态的相位翻转180度（乘以-1）。为了在量子线路上实现它，我们通常会先用 $X$ 门将全零态映射为全壹态 $|111...1\rangle$，然后使用一个多控Z门（在目标为1时翻转相位），最后再使用 $X$ 门恢复原状。而多控Z门可以通过对目标比特添加Hadamard门，将其转化为多控X门（如Toffoli门），再转换回来实现。\n\n以下是使用isQ编程语言实现3量子比特Grover扩散算子的完整代码及逐行详细注释：\n\nimport std; // 引入标准库，提供基础量子门和测量等内置函数\n\nqbit q[3]; // 全局声明3个量子比特，用于构建Grover搜索的3比特量子寄存器\n\n// 定义扩散算子过程，接收3个量子比特作为参数\nprocedure diffusion_op(qbit q[3]) {\n    // 第一步：对所有的量子比特应用Hadamard门\n    // 对应数学公式中的 H^{\otimes 3}\n    H(q[0]);\n    H(q[1]);\n    H(q[2]);\n\n    // 第二步：对所有的量子比特应用X门\n    // 目的是将计算基态从 |000> 翻转为 |111>，以便后续利用多控门进行相位反转\n    X(q[0]);\n    X(q[1]);\n    X(q[2]);\n\n    // 第三步：实现针对 |111> 状态的条件相位翻转 \n    // 多控Z门等价于对目标比特施加H门，执行多控X门，然后再施加H门\n    H(q[2]); // 将目标比特q[2]从Z基转换到X基\n    // 执行Toffoli门（双控X门），当q[0]和q[1]均为|1>时，翻转q[2]的状态\n    // 结合前后的H门，其整体效果就是当q[0],q[1],q[2]均为|1>时，翻转整体的相对相位\n    Toffoli(q[0], q[1], q[2]); \n    H(q[2]); // 将目标比特q[2]重新转换回Z基\n\n    // 第四步：再次对所有的量子比特应用X门\n    // 恢复之前被翻转的状态，将 |111> 重新变回 |000>\n    X(q[0]);\n    X(q[1]);\n    X(q[2]);\n\n    // 第五步：再次对所有的量子比特应用Hadamard门\n    // 对应数学推导中另一侧的 H^{\otimes 3}，完成关于平均值的反转操作\n    H(q[0]);\n    H(q[1]);\n    H(q[2]);\n}\n\nprocedure main() {\n    // 初始化阶段：通过H门将所有量子比特制备为均匀叠加态 |s>\n    H(q[0]);\n    H(q[1]);\n    H(q[2]);\n\n    // 注意：实际Grover算法中，这里应该先执行Oracle操作标记目标态\n    // 例如：oracle(q); （此处省略具体的Oracle实现）\n\n    // 调用上面定义的扩散算子过程，放大目标态的概率振幅\n    diffusion_op(q);\n\n    // 对所有量子比特进行测量，坍缩到最终的计算结果\n    int r0 = M(q[0]);\n    int r1 = M(q[1]);\n    int r2 = M(q[2]);\n}
