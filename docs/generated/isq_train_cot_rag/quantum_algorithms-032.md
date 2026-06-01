# ISQ training COT RAG corpus: quantum_algorithms shard 32

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/2892

- task_id: `isqTrain/2892`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_syntax_multi_register`, `measurement_order`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `394`

### Prompt

Fix the bug in this quantum program:

```isq
import std;
qbit q[1];
// Single qubit with Ry(pi/2)
procedure main() {
    Ry(1.5707963, q[0]);
    X(q[0]); // BUG: spurious X before measurement

    M(q[0]);
}

```

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: The line `X(q[0]);` on line 7 is a spurious X gate inserted between the state preparation (`Ry(pi/2)`) and measurement. It flips the qubit, altering the state before measurement.

2. **Fix**: Remove the `X(q[0]);` line. The circuit should only apply `Ry(pi/2)` and then measure.

3. **State evolution (corrected)**:
   - Initial: |0⟩
   - After `Ry(π/2, q[0])`: cos(π/4)|0⟩ + sin(π/4)|1⟩ = (|0⟩ + |1⟩)/√2 = |+⟩
   - Measurement yields |0⟩ with probability 0.5 and |1⟩ with probability 0.5, matching predicted output.

## isqTrain/984

- task_id: `isqTrain/984`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `basis_change`, `entanglement`, `hamiltonian_simulation`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4674`

### Prompt

Code this in isQ: implements the suzuki_trotter pattern but with a different initial state preparation (flip q[[0]] -> q[1]).

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

1. **Goal**: Implement a second-order Suzuki-Trotter decomposition with initial state |10⟩ instead of |00⟩.

2. **Qubits**: 2 qubits (q[0], q[1]), both measured.

3. **State evolution**:
   - Initial state: |00⟩
   - After X(q[1]): |10⟩
   
   Now we apply the Suzuki-Trotter decomposition S2(t) = e^(-i*t/2*ZZ) * e^(-i*t*XX) * e^(-i*t/2*ZZ) with t = π/8.

   **First half-step: e^(-i*t/2*ZZ)**
   - CNOT(q[0], q[1]): |10⟩ → |11⟩
   - Rz(t, q[1]) where t = π/8: |11⟩ → e^(-i*t/2)|11⟩
   - CNOT(q[0], q[1]): e^(-i*t/2)|11⟩ → e^(-i*t/2)|10⟩
   
   **Full XX step: e^(-i*t*XX)**
   - H(q[0]), H(q[1]): e^(-i*t/2)|10⟩ → e^(-i*t/2) * (|0⟩-|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2
     = e^(-i*t/2)/2 * (|00⟩ + |01⟩ - |10⟩ - |11⟩)
   
   Wait, let me recalculate:
   H|0⟩ = |+⟩ = (|0⟩+|1⟩)/√2
   H|1⟩ = |−⟩ = (|0⟩-|1⟩)/√2
   
   So H(q[0])H(q[1])|10⟩ = H(q[0])|1⟩ ⊗ H(q[1])|0⟩ = |−⟩ ⊗ |+⟩ = (|0⟩-|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2
   
   With the phase: e^(-i*t/2)/2 * (|00⟩ + |01⟩ - |10⟩ - |11⟩)
   
   - CNOT(q[0], q[1]): This flips q[1] when q[0] is |1⟩
     |00⟩ → |00⟩, |01⟩ → |01⟩, |10⟩ → |11⟩, |11⟩ → |10⟩
     Result: e^(-i*t/2)/2 * (|00⟩ + |01⟩ - |11⟩ - |10⟩)
   
   - Rz(2t, q[1]) where 2t = π/4: This applies phase e^(-it) to |1⟩ state of q[1]
     |00⟩ → |00⟩
     |01⟩ → e^(-iπ/8)|01⟩ (wait, Rz applies phase to |1⟩)
     
   Actually, Rz(θ) = e^(-iθ/2)|0⟩⟨0| + e^(iθ/2)|1⟩⟨1|... but in many conventions it's applied as a phase gate.
   
   Let me think more carefully. The Rz gate is typically:
   Rz(θ) = diag(e^(-iθ/2), e^(iθ/2))
   
   So Rz(θ)|0⟩ = e^(-iθ/2)|0⟩ and Rz(θ)|1⟩ = e^(iθ/1)|1⟩
   
   Actually, for the purpose of computing probabilities, the global phases don't matter, but relative phases do.
   
   Let me track the state more carefully. This is getting complex. Let me just verify the predicted output.

   The predicted output: {|01⟩: 0.8536, |10⟩: 0.1464}

   These sum to 1, and 0.8536 ≈ (2+√2)/4 and 0.1464 ≈ (2-√2)/4.

   Let me verify: (2+√2)/4 ≈ (2+1.414)/4 ≈ 3.414/4 ≈ 0.8535 ✓
   (2-√2)/4 ≈ (2-1.414)/4 ≈ 0.586/4 ≈ 0.1465 ✓

So the final state has amplitudes for |01⟩ and |10⟩ with probabilities proportional to these values.

Let me trace through more carefully with t = π/8.

Starting: |

## isqTrain/2862

- task_id: `isqTrain/2862`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `isq_syntax_multi_register`, `measurement_order`, `multi_controlled_logic`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2606`

### Prompt

修复以下isQ程序中的错误：

```isq
import std;
qbit q[3];
// 3-qubit GHZ state
procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    // CNOT(q[1], q[2]); // BUG: missing CNOT
    M(q[0]);
    M(q[1]);
    M(q[2]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. The bug is a missing CNOT gate, as `CNOT(q[1], q[2])` was commented out, leaving the third qubit in its initial state and failing to propagate entanglement.
2. The fix is to uncomment the

## isqTrain/901

- task_id: `isqTrain/901`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_oracle`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5290`

### Prompt

请用isQ语言编写一个量子电路：implements a variant of the bit_flip_oracle pattern using q[3] -> q[5]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a bit-flip oracle for f(x) = x[0] XOR x[1] on a 5-qubit register, computing the XOR into q[2] while leaving q[3], q[4] untouched.
2. **Qubits**: 5 qubits (q[0..4]), all measured; output bitstring is q[0]q[1]q[2]q[3]q[4].
3. **State evolution**:
   - Initial: |00000⟩
   - X(q[0]): |10000⟩ — prepares input x = |10⟩
   - CNOT(q[0], q[2]): |10100⟩ — control q[0]=1 flips q[2]
   - CNOT(q[1], q[2]): |10100⟩ — control q[1]=0 leaves q[2] unchanged
   - q[3], q[4] remain |0⟩ throughout
4. **Expected probabilities**: Final state |10100⟩ gives measurement outcome |10100⟩ with probability 1.0, since XOR(1,0) = 1 correctly appears in q[2].

## isqTrain/2941

- task_id: `isqTrain/2941`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_for_loop`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1805`

### Prompt

Code this in isQ: creates a uniform superposition over 6 qubits by applying Hadamard to each qubit.

Requirements:
- Declare `qbit q[6];` at global scope.
- Use a for loop to apply H gates.
- Measure all 6 qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Create a uniform superposition over 6 qubits by applying Hadamard gates to each qubit initialized to |0⟩.

1. **Qubits**: 6 qubits `q[0]` through `q[5]`, all measured at the end.
2. **Initial state**: |000000⟩ — all qubits in |0⟩.
3. **Step-by-step evolution**:
   - Apply `H(q[i])` for i = 0 to 5 via the for loop.
   - Each `H` transforms |0⟩ → |+⟩ = (|0⟩ + |1⟩)/√2.
   - After all 6 Hadamard gates, the joint state is |++++++⟩ = (1/√2)⁶ Σ |x⟩ for all x ∈ {0,1}⁶.
   - This is a uniform superposition over all 2⁶ = 64 computational basis states.
4. **Measurement probabilities**: Each of the 64 basis states has amplitude 1/√64, giving probability |1/√64|² = 1/64 ≈ 0.015625.

## isqQA/quantum_algorithms/87_step_by_step

- task_id: `isqQA/quantum_algorithms/87_step_by_step`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `step_by_step`, `algorithm`, `Deutsch-Jozsa算法`
- source: `qa_pipeline`
- dataset_index: `1931`

### Prompt

请以 Deutsch-Jozsa 算法处理 2 量子位输入（即 n=2）为例，一步步教学并手动追踪其量子态的演化过程。假设我们要识别的黑盒函数是一个平衡函数 $f(x_0, x_1) = x_0 \oplus x_1$（即异或运算），请详细推导每一步的量子态，并提供完整的 isQ 语言代码实现。

### Reference answer

<think>
推理过程主要分为量子态演化的数学推导和代码逻辑映射两步。首先分析理论推导：初始化3个量子比特后，通过Hadamard门使前两位进入均匀叠加态，辅助位变为 $|-\rangle$ 态。接着应用黑盒函数 $U_f$，由于辅助位的作用， $U_f$ 等价于对输入态引入相位因子 $(-1)^{f(x)}$。对于函数 $f(x_0, x_1) = x_0 \oplus x_1$，计算可知输入为00和11时相位为+1，01和10时为-1。随后再次对输入位施加Hadamard门，发生量子干涉。因为相位的对称分布特征，干涉会导致测量结果中 $|00\rangle$ 的概率幅严格为0。由此通过单次运行测量到非零结果，即可判定该函数为平衡函数。在代码实现上，思路是将上述门操作翻译为isQ语言。核心在于黑盒的线路映射：异或操作可通过两个控制位分别作用于辅助位的CNOT门实现，并在首尾辅以Hadamard门，最后加入测量语句验证干涉结果。
</think>

Deutsch-Jozsa（D-J）算法是量子计算中展示量子并行性和干涉现象的经典算法。它的核心任务是：给定一个黑盒函数 $f:\{0,1\}^n \rightarrow \{0,1\}$，已知它要么是常数函数（对所有输入输出相同），要么是平衡函数（恰好一半输入输出0，一半输出1），要求判断其属于哪一类。经典算法最坏情况下需要 $2^{n-1}+1$ 次查询，而量子算法只需 1 次查询。

我们以 $n=2$，黑盒函数 $f(x_0, x_1) = x_0 \oplus x_1$ 为例，手动追踪其演化过程：

**步骤 1：初始化**
我们需要 2 个输入量子位（设为 $q[0]$ 和 $q[1]$）和 1 个辅助量子位（设为 $q[2]$）。
初始态为：
$$|\psi_0\rangle = |00\rangle \otimes |1\rangle = |001\rangle$$

**步骤 2：应用 Hadamard 门**
对所有 3 个量子位应用 H 门。对于输入位，H 门将其变为均匀叠加态；对于辅助位，H 门将其变为 $|-
angle$ 态。
$$|\psi_1\rangle = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle) \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$$

**步骤 3：应用 Oracle $U_f$**
Oracle 的作用是 $|x\rangle|y\rangle \rightarrow |x\rangle|y \oplus f(x)\rangle$。由于辅助位处于 $|0\rangle - |1\rangle$ 的叠加态，发生相位反冲，相当于对输入位作用了 $(-1)^{f(x)}$ 的相位。
对于 $f(x_0, x_1) = x_0 \oplus x_1$，代入计算得：
- $x=00$ 时，$f(0,0)=0$，相位不变 $(+1)$
- $x=01$ 时，$f(0,1)=1$，相位反转 $(-1)$
- $x=10$ 时，$f(1,0)=1$，相位反转 $(-1)$
- $x=11$ 时，$f(1,1)=0$，相位不变 $(+1)$

忽略辅助位（它始终保持在 $|0\rangle - |1\rangle$ 态并最终被抛弃），输入位状态变为：
$$|\psi_2\rangle = \frac{1}{2}(|00\rangle - |01\rangle - |10\rangle + |11\rangle)$$

**步骤 4：再次对输入位应用 Hadamard 门**
对前两个量子位应用 $H^{\otimes 2}$。我们可以通过线性代数或逐位计算 $H|x\rangle = \frac{1}{\sqrt{2}}\sum_{z} (-1)^{x \cdot z}|z\rangle$ 来更新状态。计算每一项的贡献并相加：
$$|\psi_3\rangle = \frac{1}{4} \sum_{z} \left[ \sum_{x} (-1)^{x \cdot z + f(x)} \right] |z\rangle$$
经过代数化简或矩阵乘法，由于各项的正负干涉，所有 $z$ 的振幅均为 0，除了 $z=11$。此时振幅为 $1$。
因此，状态坍缩为：
$$|\psi_3\rangle = |11\rangle$$

**步骤 5：测量**
我们对输入位进行测量。因为当前状态精确为 $|11\rangle$，所以测量结果必定是二进制字符串 `11`（即非全 0）。
**结论**：只要测量结果不全为 0，我们就100%确定该函数是平衡函数。

以下是使用 isQ 语言实现的完整代码：

```isq
import std;

qbit q[3]; // q[0], q[1] 为输入位，q[2] 为辅助位

procedure main() {
    // 初始化辅助位为 |1>
    X(q[2]);

    // 步骤 2：对所有量子位应用 Hadamard 门
    for i in 0:3 {
        H(q[i]);
    }

    // 步骤 3：构造并应用平衡函数 Oracle f(x) = x0 XOR x1
    // 逻辑：当 x0 != x1 时，f(x)=1。利用辅助位的相位反冲，可以等效为对输入态施加相应相位。
    // 在电路上，通过 CNOT 即可实现 f(x) 的计算并传递给辅助位。
    CNOT(q[0], q[2]);
    CNOT(q[1], q[2]);

    // 步骤 4：对输入位再次应用 Hadamard 门
    for i in 0:2 {
        H(q[i]);
    }

    // 步骤 5：测量输入位
    // 如果是平衡函数，结果中必然包含 1（非 00）
    // 可以在 --probs 模式下观察概率分布，必定全在 |11> 态上
    M(q[0]);
    M(q[1]);
}
```

通过这段代码和推导，你可以直观地看到量子态是如何在并行计算后通过干涉将正确答案放大，同时消除错误答案的。这完美诠释了量子计算在特定问题上的指数级加速能力。

## isqTrain/786

- task_id: `isqTrain/786`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `finite_field_arithmetic`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3459`

### Prompt

Help me write isQ code that implements a variant of the gf2_multiplication pattern using q[5] -> q[7]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
Goal: Multiply polynomials a(x) = 1+x and b(x) = 1 in GF(2), using a 7-qubit register with q[3-4] for product and q[5-6] as idle ancillas.
Seven qubits are used; q[3], q[4], q[5], q[6] are measured to yield a 4-bit outcome.
Step 1: X(q[0]), X(q[1]), X(q[2]) prepare |a₁a₀b₀⟩ = |111⟩ on q[0-2], giving full state |111⟩|0000⟩.
Step 2: Toffoli(q[0], q[2], q[3]) computes p₀ = a₀∧b₀ = 1, flipping q[3] → state |111⟩|1000⟩.
Step 3: Toffoli(q[1], q[2], q[4]) computes p₁ = a₁∧b₀ = 1, flipping q[4] → state |111⟩|1100⟩.
Step 4: Measuring q[3,4,5,6] yields product p = 1+x in q[3-4] and 0 in q[5-6], giving outcome |1100⟩ with probability 1.0.

## isqExpand/qa/40

- task_id: `isqExpand/qa/40`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_kickback`, `quantum_circuits`, `controlled_unitary`, `eigenstate`, `linear_algebra`
- source: `qa_pipeline`
- dataset_index: `3089`

### Prompt

量子算法中的相位回踢机制是什么？请用数学推导解释它为什么有效。

### Chain-of-thought reasoning

## 推理
首先明确相位回踢的定义，指出其发生在受控酉操作中，并且要求目标量子比特处于酉算子的特征态上。接着通过具体的线性代数推导，展示全局相位是如何转化为控制量子比特的相对相位的。最后，使用一个最经典的CNOT门的例子（目标态为|-e）来具体说明，并给出isQ代码供学生动手验证。这样的结构既严谨又易于理解。

### Reference answer

在量子计算中，**相位回踢** 是一种核心的底层机制，广泛应用于Deutsch算法、Deutsch-Jozsa算法、量子相位估计（QPE）以及Grover搜索算法中。

直观地说，相位回踢发生在一个多量子比特系统中：当我们对一个处于叠加态的“控制量子比特”和一个处于特定状态的“目标量子比特”执行**受控酉操作**时，目标量子比特不仅没有发生我们预期的常规状态翻转，反而将酉算子对应的**特征值（相位）“回踢”**给了控制量子比特，从而改变了控制量子比特的相对相位。

### 数学推导
假设我们有一个受控酉门 $CU$，它的作用是：当控制量子比特处于 $|1\rangle$ 态时，对目标量子比特应用酉算子 $U$；当控制量子比特处于 $|0\rangle$ 态时，什么都不做。

设酉算子 $U$ 作用在 $n$ 维目标量子比特上，且 $|u\rangle$ 是 $U$ 的一个特征向量，对应的特征值为 $e^{i\phi}$（其中 $\phi$ 为实数），即满足：
$$ U|u\rangle = e^{i\phi}|u\rangle $$

现在，我们将控制量子比特初始化为一般叠加态 $\alpha|0\rangle + \beta|1\rangle$，并将目标量子比特初始化为该特征态 $|u\rangle$。系统的初始状态为：
$$ |\psi_{initial}\rangle = (\alpha|0\rangle + \beta|1\rangle) \otimes |u\rangle $$

对其进行受控酉操作 $CU$，系统的状态演变如下：
$$ 
\begin{aligned} 
CU |\psi_{initial}\rangle &= \alpha CU(|0\rangle \otimes |u\rangle) + \beta CU(|1\rangle \otimes |u\rangle) \\
&= \alpha |0\rangle \otimes |u\rangle + \beta |1\rangle \otimes U|u\rangle \\
&= \alpha |0\rangle \otimes |u\rangle + \beta |1\rangle \otimes (e^{i\phi}|u\rangle) \\
&= (\alpha|0\rangle + \beta e^{i\phi}|1\rangle) \otimes |u\rangle 
\end{aligned}
$$

**结论：** 目标量子比特的状态依然是 $|u\rangle$（未发生改变），但控制量子比特的 $|1\rangle$ 分支却获得了一个全局相位 $e^{i\phi}$。由于控制量子比特处于 $|0\rangle$ 和 $|1\rangle$ 的叠加态，这个全局相位变成了控制量子比特的**相对相位**。这正是相位“回踢”到控制位的数学本质。

### 直观案例：CNOT门带来的 $\pi$ 相位回踢
最简单的相位回踢发生在受控非门（CNOT）中。CNOT的本质是受控 $X$ 门。如果我们把目标量子比特放在 $X$ 算子的特征态 $|-
angle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$ 上（对应特征值 $-1 = e^{i\pi}$）：

1. 控制位状态：$|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$
2. 目标位状态：$|-
angle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$
3. 执行 CNOT 后，由于 $X|-
angle = -|-
angle$，相位回踢使得控制位 $|1\rangle$ 分支乘以 $-1$。
4. 最终状态变为 $|-
angle_{control} \otimes |-
angle_{target}$。控制位从 $|+\rangle$ 变成了 $|-
angle$，即发生了一次 $\pi$ 的相位翻转。

### isQ 代码示例
以下代码演示了上述的 CNOT 相位回踢实验：控制位初始为 $|0\rangle$，目标位初始为 $|1\rangle$。我们通过 Hadamard 门将控制位和目标位分别变为 $|+\rangle$ 和 $|-
angle$。执行 CNOT 后，我们测量控制位，会发现它变为了确定的 $|1\rangle$ 状态（因为 $H|-
angle = |1\rangle$），证明发生了相位回踢。

```isq
import std;

qbit q[2];

procedure main() {
    // 初始化目标量子比特 q[1] 为 |1>
    X(q[1]);

    // 将控制量子比特 q[0] 转换为 |+>
    // 将目标量子比特 q[1] 转换为 |->
    H(q[0]);
    H(q[1]);

    // 执行 CNOT 门，触发相位回踢
    CNOT(q[0], q[1]);

    // 此时 q[0] 的状态已经因为相位回踢从 |+> 变成了 |->
    // 再次应用 H 门，将相位差异转化为计算基态的差异：H|-> = |1>
    H(q[0]);

    // 测量 q[0]
    M(q[0]);
    print M(q[0]);
}
```
运行该程序，控制量子比特 `q[0]` 的测量结果将以 100% 的概率输出 `1`。

## isqTrain/3570

- task_id: `isqTrain/3570`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `basis_change`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2651`

### Prompt

Fix the bug in the following isQ program.

Bug description: Missing Hadamard gate

The program should Bell state Psi- creation and verification.

### Chain-of-thought reasoning

## Bug Analysis

**1. What the bug is:** The Hadamard gate `H(q[0])` is missing between `X(q[1])` and `CNOT(q[0], q[1])`. Without it, the CNOT acts on |01⟩ with control q[0]=|0⟩, leaving the state as |01⟩ — no entanglement is created, and the circuit fails to produce |Ψ⁻⟩.

**2. What the fix is:** Insert `H(q[0]);` after `X(q[1]);` and before `CNOT(q[0], q[1]);`. This creates the necessary superposition on q[0] for entanglement via CNOT.

**3. State evolution of corrected circuit:**
- |00⟩ → X(q[1]) → |01⟩
- |01⟩ → H(q[0]) → (|01⟩ + |11⟩)/√2
- → CNOT(q[0],q[1]) → (|01⟩ + |10⟩)/√2 = |Ψ⁺⟩
- → Z(q[0]) → (|01⟩ − |10⟩)/√2 = |Ψ⁻⟩ ✓
- → Bell measurement (CNOT then H): CNOT(q[0],q[1]) → (|01⟩ − |11⟩)/√2, then H(q[0]) → |11⟩
- Measurement yields |11⟩ with probability 1.0 ✓

## isqTrain/4822

- task_id: `isqTrain/4822`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_syntax_import_qft`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2573`

### Prompt

Create an isQ quantum circuit that applies QFT to a 4-qubit register initialized to |0000>. Import std and qft. Declare 4 global qubits. Apply qft(q). Measure all 4 qubits. The QFT of |0> produces a uniform superposition over all 16 basis states.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply the 4-qubit Quantum Fourier Transform (QFT) to |0000⟩, producing a uniform superposition over all 16 computational basis states.
2. **Qubits**: 4 global qubits q[0..3]; all 4 are measured.
3. **State evolution**: |0000⟩ → QFT → (1/4) Σ_{x=0}^{15} |x⟩ = (1/4)(|0000⟩+|0001⟩+...+|1111⟩). QFT on |0⟩^⊗n is equivalent to applying H to each qubit, creating an equal superposition.
4. **Probabilities**: Each basis state has amplitude 1/4, giving probability |1/4|² = 1/16 = 0.0625 for all 16 outcomes.
