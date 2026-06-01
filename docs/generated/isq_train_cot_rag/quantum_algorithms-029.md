# ISQ training COT RAG corpus: quantum_algorithms shard 29

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4013

- task_id: `isqTrain/4013`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `856`

### Prompt

This isQ program compiles but produces incorrect probabilities. Find and correct the mistake.

```
import std;
// QPE with 3-bit precision for phase 4*pi/4
qbit q[4];

procedure main() {
    // Prepare eigenstate |1>
    X(q[3]);
    // Hadamard on precision qubits
    H(q[0]); H(q[1]); H(q[2]);
    // Controlled-U^(2^k) for each precision qubit
    ctrl Rx(2.0 * 3.14159265358979 * 4.0 / 8.0 * 1.0, q[0], q[3]);
    ctrl Rz(2.0 * 3.14159265358979 * 4.0 / 8.0 * 2.0, q[1], q[3]);
    ctrl Rz(2.0 * 3.14159265358979 * 4.0 / 8.0 * 4.0, q[2], q[3]);
    // Inverse QFT on 3 precision qubits
    // Swap q[0] <-> q[2]
    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    // iQFT stages
    H(q[0]);
    ctrl Rz(-3.14159265358979 / 2.0, q[1], q[0]);
    ctrl Rz(-3.14159265358979 / 4.0, q[2], q[0]);
    H(q[1]);
    ctrl Rz(-3.14159265358979 / 2.0, q[2], q[1]);
    H(q[2]);
    // Measure all
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

Let me analyze the buggy code carefully.

The task is QPE with 3-bit precision for phase 4π/4 = π.

In QPE, we're estimating the phase φ of a unitary U where U|ψ⟩ = e^(2πiφ)|ψ⟩.

If φ = 4/8 = 1/2, then the phase is 4π/4 = π, and the eigenvalue is e^(2πi × 1/2) = e^(πi) = -1.

Wait, let me re-read. Phase 4π/4 = π. So 2πφ = π, meaning φ = 1/2.

With 3-bit precision, we should get the binary representation of φ = 0.100₂ = 4/8. So the measurement of the precision qubits should give |100⟩ = 4 in binary.

But the expected measurement probabilities are {|0001⟩: 0.005574, |0011⟩: 0.140873, |0101⟩: 0.590097, |0111⟩: 0.263456}.

Hmm wait, the phase 4π/4 = π. With the unitary being Rz, we have Rz(θ)|1⟩ = e^(-iθ/2)|1⟩. So the eigenvalue is e^(-iθ/2).

For the controlled operations, the phase accumulated is:
- For U = Rz(2π × 4/8 × 1) = Rz(π): phase = -π/2
- For U² = Rz(2π × 4/8 × 2) = Rz(2π): phase = -π
- For U⁴ = Rz(2π × 4/8 × 4) = Rz(4π): phase = -2π

Hmm, this doesn't seem right for a clean QPE.

Actually wait, let me reconsider. The comment says "phase 4*pi/4". Let me look at this differently.

Actually, looking at the predicted output more carefully: {|0001⟩: 0.005574, |0011⟩: 0.140873, |0101⟩: 0.590097, |0111⟩: 0.263456}

The precision qubits are q[0], q[1], q[2], and q[3] is the eigenstate. In the measurement bitstring, earlier measured qubit = higher bit. So M(q[0]) is the highest bit, M(q[3]) is the lowest bit.

For |0101⟩: q[0]=0, q[1]=1, q[2]=0, q[3]=1. Precision bits = 010 = 2. This has probability 0.59.
For |0111⟩: q[0]=0, q[1]=1, q[2]=1, q[3]=1. Precision bits = 011 = 3. This has probability 0.26.

Hmm, but if phase = 4π/4 = π, the predicted output should be... Let me think about what gate U is.

The code uses Rz gates for the controlled operations. Rz(θ) on |1⟩ gives eigenvalue e^(-iθ/2).

For the eigenstate |1⟩, Rz(θ)|1⟩ = e^(-iθ/2)|1⟩.

So the phase φ satisfies 2πφ = -θ/2, i.e., φ = -θ/(4π).

Wait no. Let me be more careful. 

Rz(θ) = diag(e^{-iθ/2}, e^{iθ/2})

So Rz(θ)|1⟩ = e^{iθ/2}|1⟩

The eigenvalue is e^{iθ/2}. So 2πφ = θ/2, φ = θ/(4π).

For the controlled-Rz with k-th precision qubit, θ_k = 2π × 4/8 × 2^k = π × 2^k.

So the total phase from the k-th qubit contributes e^{iθ_k/2} = e^{iπ × 2^{k-1}}.

For k=0 (q[0]): e^{iπ/2} (controlled-Rz with power 1)
Wait, θ_0 = 2π × 4/8 × 1 = π. So eigenvalue contribution = e^{iπ/2}.
For k=1 (q[1]): θ_1 = 2π × 4/8 × 2 = 2π. Eigenvalue = e^{iπ}.
For k=2 (q

## isqTrain/313

- task_id: `isqTrain/313`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_arrays`, `isq_syntax_multi_register`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3551`

### Prompt

I need an isQ program to implements the oracle_boolean pattern. Include explicit identity operations in the circuit (X-X pair before M(x[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement a Deutsch oracle for constant function f(x)=1, demonstrating X-X gate cancellation before measurement.

2. **Qubits**: 2 qubits (x[0] input, y[0] ancilla); only x[0] is measured.

3. **State evolution**:
   - |00⟩ → X(y[0]) → |01⟩
   - H(x[0]); H(y[0]) → |+⟩⊗|−⟩ = (|0⟩+|1⟩)/√2 ⊗ (|0⟩−|1⟩)/√2
   - X(y[0]) applies constant-1 oracle: flips y[0], yielding −|+⟩⊗|−⟩ (global phase irrelevant)
   - H(x[0]) → |0⟩⊗|−⟩ (H|+⟩=|0⟩, confirming constant function)
   - X(x[0]) → |1⟩⊗|−⟩
   - X(x[0]) → |0⟩⊗|−⟩ (identity pair cancels, demonstrating gate cancellation)

4. **Measurement**: x[0] is in |0⟩, yielding probability {|0⟩: 1.0}.

## isqTrain/4003

- task_id: `isqTrain/4003`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `isq_syntax_oracle`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4589`

### Prompt

修复以下isQ程序中的错误：

```
import std;
// Deutsch-Jozsa for 2-input balanced oracle [0, 0, 1, 1]
oracle f(2, 1) = [0, 0, 1, 1];
qbit q[3];  // 2 input + 1 output

procedure main() {
    // Initialize output qubit to |->
    X(q[2]);
    H(q[2]);
    // Hadamard on input qubits
    X(q[0]); H(q[1]);
    // Apply oracle
    f(q[0], q[1], q[2]);
    // Hadamard on inputs
    H(q[0]); H(q[1]);
    // Measure input qubits (non-zero = balanced)
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: Line `X(q[0]); H(q[1]);` contains `X(q[0])` instead of `H(q[0])`. The Deutsch-Jozsa algorithm requires Hadamard gates on **all** input qubits to create a uniform superposition, not an X gate.

2. **Fix**: Replace `X(q[0]); H(q[1]);` with `H(q[0]); H(q[1]);`.

3. **State evolution (corrected)**:
   - Start: |000⟩
   - After X(q[2]), H(q[2]): |00⟩⊗|−⟩
   - After H(q[0]), H(q[1]): (½)(|00⟩+|01⟩+|10⟩+|11⟩)⊗|−⟩
   - Oracle f=[0,0,1,1] phase kickback:

## isqTrain/1267

- task_id: `isqTrain/1267`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `data_encoding_qml`, `entanglement`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3339`

### Prompt

帮我写一个isQ程序：implements the data_encoding pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

Let me analyze this isQ program step by step.

The circuit implements a ZZ feature map for data encoding with entanglement on 2 qubits.

Step-by-step state evolution:

1. Initial state: |00⟩

2. H(q[0]); H(q[1]) → |++⟩ = (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩)

3. Rz(1.04719755119660, q[0]) = Rz(π/3, q[0])
4. Rz(0.52359877559830, q[1]) = Rz(π/6, q[1])

After these rotations, the state becomes:
(1/2)(e^(-i(π/6+π/12))|00⟩ + e^(-i(π/6-π/12))|01⟩ + e^(-i(-π/6+π/12))|10⟩ + e^(-i(-π/6-π/12))|11⟩)

Wait, let me be more careful. Rz(θ) applies e^(-iθ/2) to |0⟩ and e^(iθ/2) to |1⟩.

After H-H: |++⟩ = (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩)

After Rz(π/3, q[0]):
- |0⟩ → e^(-iπ/6)|0⟩
- |1⟩ → e^(iπ/6)|1⟩

After Rz(π/6, q[1]):
- |0⟩ → e^(-iπ/12)|0⟩
- |1⟩ → e^(iπ/12)|1⟩

State after both Rz:
(1/2)(e^(-iπ/6-iπ/12)|00⟩ + e^(-iπ/6+iπ/12)|01⟩ + e^(iπ/6-iπ/12)|10⟩ + e^(iπ/6+iπ/12)|11⟩)
= (1/2)(e^(-iπ/4)|00⟩ + e^(-iπ/12)|01⟩ + e^(iπ/12)|10⟩ + e^(iπ/4)|11⟩)

5. CNOT(q[0], q[1])
|00⟩ → |00⟩, |01⟩ → |01⟩, |10⟩ → |11⟩, |11⟩ → |10⟩

State becomes:
(1/2)(e^(-iπ/4)|00⟩ + e^(-iπ/12)|01⟩ + e^(iπ/4)|10⟩ + e^(iπ/12)|11⟩)

Wait, let me redo this. CNOT(q[0], q[1]) means q[0] is control, q[1] is target.
- |00⟩ → |00⟩
- |01⟩ → |01⟩
- |10⟩ → |11⟩
- |11⟩ → |10⟩

So:
(1/2)(e^(-iπ/4)|00⟩ + e^(-iπ/12)|01⟩ + e^(iπ/12)|11⟩ + e^(iπ/4)|10⟩)

Wait, I need to be more careful:
Before CNOT: (1/2)(e^(-iπ/4)|00⟩ + e^(-iπ/12)|01⟩ + e^(iπ/12)|10⟩ + e^(iπ/4)|11⟩)

After CNOT (control=q[0], target=q[1]):
- |00⟩ stays |00⟩
- |01⟩ stays |01⟩
- |10⟩ becomes |11⟩
- |11⟩ becomes |10⟩

So the state becomes:
(1/2)(e^(-iπ/4)|00⟩ + e^(-iπ/12)|01⟩ + e^(iπ/4)|10⟩ + e^(iπ/12)|11⟩)

6. Rz(0.54831135561608, q[1]) on q[1]

This applies Rz(θ) on q[1]:
- For |0⟩ on q[1]: multiply by e^(-iθ/2)
- For |1⟩ on q[1]: multiply by e^(iθ/2)

θ = 0.54831135561608

State becomes:
(1/2)(e^(-iπ/4)·e^(-iθ/2)|00⟩ + e^(-iπ/12)·e^(iθ/2)|01⟩ + e^(iπ/4)·e^(-

## isqQA/quantum_algorithms/123_optimization_variant

- task_id: `isqQA/quantum_algorithms/123_optimization_variant`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `optimization_variant`, `algorithm`, `连续时间量子行走`
- source: `qa_pipeline`
- dataset_index: `1011`

### Prompt

在连续时间量子行走算法的发展中，为了解决空间搜索问题并实现相较于经典算法的二次加速，研究者们提出了哪些重要的优化变体？请详细阐述其中一种基于哈密顿量修改的“空间搜索变体”的数学原理，并使用isQ语言展示如何在量子线路上实现针对特定目标节点的状态相位翻转（即引入局域势能项）。

### Reference answer

连续时间量子行走（CTQW）最初被设计用于在图结构上模拟量子态的演化，其基础形式在无结构搜索问题上并未直接展现出Grover算法那样的二次加速。为此，研究者们提出了多种重要的优化变体与改进版本，主要包括：

1. **空间搜索变体（带有标记顶点的CTQW）**：这是最著名的改进版本之一。通过在系统的哈密顿量中针对目标节点引入一个额外的局域势能（相当于对目标态施加相位翻转），使得量子行走演化为一种类似于Grover搜索的振幅放大过程。
2. **Szegedy量子行走离散化变体**：将连续时间演化转化为离散时间的量子马尔可夫链，通过谱定理将经典马尔可夫链的转移矩阵提升为酉算子，极大地扩展了CTQW在一般非正则图上的应用。
3. **带相消干涉的优化变体**：通过精心调节图中某些边的跃迁振幅或引入缺陷，利用相消干涉消除非目标态的转移概率，从而实现对目标节点概率的高效汇聚。

以**空间搜索变体**为例，其核心数学推导如下：
在标准CTQW中，系统的哈密顿量通常取图的邻接矩阵 $A$，演化算符为 $U = e^{-iAt}$。这种演化缺乏对目标顶点 $|w\rangle$ 的区分度。在优化变体中，哈密顿量被修改为：
$H = A + r |w\rangle\langle w|$
其中 $r$ 是标记强度。为了在量子计算机上模拟这种演化，我们通常采用Trotter-Suzuki分解。对于极短的时间步长 $\Delta t$，演化算符可近似为：
$e^{-iH\Delta t} \approx e^{-iA\Delta t} e^{-ir|w\rangle\langle w|\Delta t}$
这里，第一项 $e^{-iA\Delta t}$ 对应于图上的标准连续量子行走；第二项 $e^{-ir|w\rangle\langle w|\Delta t}$ 则是一个对角矩阵，它只对目标状态 $|w\rangle$ 附加相位 $e^{-ir\Delta t}$，而其他正交状态保持不变。这正是该变体打破对称性，实现搜索加速的物理本质。

以下是使用isQ语言实现该变体核心步骤的代码。假设在一个包含3个量子比特（共8个节点）的完全图中，我们将 $|000\rangle$ 设定为目标节点 $|w\rangle$。代码展示了如何通过X门和Toffoli门构造等效的多控制相位翻转，以实现 $e^{-ir|w\rangle\langle w|\Delta t}$ 这一步骤：
<displayText>
import std;
const N = 3;
qbit q[N];

procedure mark_target_vertex() {
    // 变体优化：针对目标顶点 |000> 引入哈密顿量中的势能项，即相位翻转
    // 首先翻转所有比特，将 |000> 映射为 |111>
    for i in 0:N { X(q[i]); }

    // 使用H门和Toffoli门构建多控制Z门（等效于对 |111> 态施加负相位）
    // 逻辑上对应于算符 I - 2|111><111|
    H(q[2]);
    Toffoli(q[0], q[1], q[2]);
    H(q[2]);

    // 恢复比特状态，此时只有 |000> 被施加了相位翻转
    for i in 0:N { X(q[i]); }
}

procedure main() {
    // 初始化：将系统制备为所有节点的均匀叠加态
    for i in 0:N { H(q[i]); }

    // 在实际算法循环中，这里应插入模拟 e^{-iAt} 的量子门序列（对应图结构的演化）
    // ... standard_continuous_walk_step();

    // 应用变体优化：针对目标节点引入局域势能项的相位翻转
    mark_target_vertex();

    // 再次进行量子行走演化
    // ... standard_continuous_walk_step();
}
</displayText>
通过交替执行标准的连续时间量子行走操作和上述针对目标节点的相位标记操作，量子态会在由均匀叠加态和目标态张成的二维子空间中发生拉比振荡，从而以 $O(\sqrt{N})$ 的时间复杂度极高概率地命中目标节点。

## isqTrain/3511

- task_id: `isqTrain/3511`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `interference`, `ancilla_usage`
- source: `isq_train_cot`
- dataset_index: `5637`

### Prompt

Predict the output probabilities of the following quantum circuit:

```
import std;

qbit q[5];
qbit anc[1];

procedure main() {
    X(anc[0]);
    H(anc[0]);

    H(q[0]); H(q[1]); H(q[2]); H(q[3]); H(q[4]);

    CNOT(q[0], anc[0]);
    CNOT(q[1], anc[0]);
    CNOT(q[2], anc[0]);
    CNOT(q[3], anc[0]);
    CNOT(q[4], anc[0]);

    H(q[0]); H(q[1]); H(q[2]); H(q[3]); H(q[4]);

    M(q[0]); M(q[1]); M(q[2]); M(q[3]); M(q[4]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict the output probability distribution for a given isQ quantum program.
    *   Input: isQ program involving 5 data qubits `q[5]` and 1 ancilla qubit `anc[1]`.
    *   Output format: Concise step-by-step reasoning using Dirac notation. Ends with predicted probability distribution.
    *   Constraints: "3-8 lines for simple circuits, up to 15 for complex ones." -> Need to be very concise. Start with "## Circuit Analysis". Output ONLY the analysis.

2.  **Analyze the Circuit:**
    *   `X(anc[0])`: Initialize ancilla to $|1\rangle$.
    *   `H(anc[0])`: Apply H to ancilla -> $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
    *   `H(q[0..4])`: Apply H to all data qubits -> State is $|+\rangle^{\otimes 5} \otimes |-\rangle$.
    *   `CNOT(q[i], anc[0])` for $i=0..4$: Apply phase kickback. Since ancilla is in $|-\rangle$, a CNOT between a control in $|+\rangle$ and a target in $|-\rangle$ leaves the control in $|+\rangle$ and target in $|-\rangle$. Wait, what if the controls are entangled or we consider multiple CNOTs?
        *   Wait, the control qubits are in $|+\rangle$. The state before CNOTs is $H^{\otimes 5}|0\rangle^{\otimes 5} \otimes H X|0\rangle$.
        *   Since the controls are all in superposition, let's look at the global state.
        *   The phase kickback from $|-\rangle$ target applies a $Z$ gate to the control if it is $|1\rangle$.
        *   Wait, no. CNOT with target in $|-\rangle$ applies a $Z$ gate to the *control*! Let's verify:
            $CNOT_{c,t} (|+\rangle_c |-\rangle_t) = \frac{1}{2}(|0\rangle+|1\rangle)(|0\rangle-|1\rangle) = \frac{1}{2}(|00\rangle - |01\rangle + |10\rangle - |11\rangle)$
            After CNOT: $\frac{1}{2}(|00\rangle - |01\rangle + |11\rangle - |10\rangle) = \frac{1}{2}(|0\rangle - |1\rangle)(|0\rangle - |1\rangle)$ Wait! No.
            $|00\rangle \to |00\rangle$
            $|01\rangle \to |01\rangle$
            $|10\rangle \to |11\rangle$
            $|11\rangle \to |10\rangle$
            Sum = $\frac{1}{2}(|00\rangle - |01\rangle + |11\rangle - |10\rangle) = \frac{1}{2}(|0\rangle(|0\rangle-|1\rangle) - |1\rangle(|0\rangle-|1\rangle)) = \frac{1}{2}(|0\rangle-|1\rangle)(|0\rangle-|1\rangle) = |-\rangle_c |-\rangle_t$.
            Ah! Wait. If control is $|+\rangle$ and target is $|-\rangle$, both become $|-\rangle$.
            Wait, is this true? No, $H_c CNOT H_c = CZ$. So $H_c \otimes I_t \cdot CNOT \cdot H_c \otimes I_t = CZ$. This means $CNOT (H_c \otimes I_t) = (H_c \otimes I_t) CZ$.
            Let's check: $CNOT(|+\rangle_c |-\rangle_t) = CNOT \frac{1}{2}(|0\rangle+|1\rangle)(|0\rangle-|1\rangle) = \frac{1}{2}(|0\rangle(|0\rangle-|1\rangle) + |1\rangle(|1\rangle-|0\rangle)) = \frac{1}{2}(|0\rangle - |1\rangle)(|0\rangle - |1\rangle) = |-\rangle_c |-\rangle_t$.
            Yes, applying CNOT with target in $|-\rangle$ flips the control from $|+\rangle$ to $|-\rangle$.
        *

### Reference answer

{'predicted_probs': {'11111': 1.0}, 'explanation': 'The output is |11111> with probability 1.0'}

## isqTrain/3060

- task_id: `isqTrain/3060`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `measurement_order`
- source: `isq_train_cot`
- dataset_index: `1352`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[3];
procedure main() {
    X(q[0]);
    X(q[2]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The 3-qubit system initializes to the |000> state.
2. The `X(q[0])` gate flips the first qubit, evolving the state to |100>.
3. The `X(q[2])` gate flips the third qubit, evolving the state to |101>.
4. The measurements are applied to q[0], q[1], and q[2] in that order, mapping them to bits 2, 1, and 0 respectively.
5. The system is in a definitive computational basis state, yielding |101> (which corresponds to index 5) with a 100%

### Reference answer

{'predicted_probs': {'101': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/1189

- task_id: `isqTrain/1189`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_classical_vars`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_inv`, `isq_syntax_multi_register`, `phase_manipulation`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `3960`

### Prompt

Code this in isQ: implements a variant of the phase_estimation pattern using target[1] -> target[2]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

Let me analyze this phase estimation circuit step by step.

The goal is to implement a variant of phase estimation using a 2-qubit target register (though only target[0] is used as the eigenstate) and a 3-qubit ancilla register.

Let me trace through the circuit:

1. **Initial state**: |000⟩_anc ⊗ |00⟩_target

2. **X(target[0])**: |000⟩_anc ⊗ |10⟩_target

3. **H(anc[0]), H(anc[1]), H(anc[2])**: Creates superposition on ancilla
   (|0⟩+|1⟩)(|0⟩+|1⟩)(|0⟩+|1⟩)/2√2 ⊗ |10⟩_target
   = 1/(2√2) Σ_{k=0}^{7} |k⟩_anc ⊗ |10⟩_target

4. **Controlled operations**:
   - ctrl T(anc[0], target[0]): T gate has eigenvalue e^(iπ/4) for |1⟩
   - ctrl S(anc[1], target[0]): S = T², eigenvalue e^(iπ/2) = i
   - ctrl Z(anc[2], target[0]): Z = T⁴, eigenvalue e^(iπ) = -1

   The phase accumulated is:
   - anc[0]=1 contributes e^(iπ/4)
   - anc[1]=1 contributes e^(iπ/2)
   - anc[2]=1 contributes e^(iπ)

   So state becomes: 1/(2√2) Σ_{k} e^(iφ_k) |k⟩_anc ⊗ |10⟩_target

   where φ_k depends on the binary representation of k.

   For k = k₂k₁k₀ (binary):
   φ_k = k₀·π/4 + k₁·π/2 + k₂·π

5. **Inverse QFT on ancilla**: The inverse QFT should extract the phase as a computational basis state.

   The phase encoded is θ = π/8 (since T|1⟩ = e^(iπ/4)|1⟩, and phase estimation extracts θ where U|ψ⟩ = e^(i2πθ)|ψ⟩, so 2πθ = π/4, thus θ = 1/8).

   So the 3-bit representation of 1/8 = 0.001 in binary.

   After inverse QFT, we should get |100⟩ (reading from the QFT structure).

Wait, let me reconsider. In phase estimation:
- If θ = 1/8, the binary representation is 0.001
- The QFT encodes this as |001⟩
- But there's a qubit ordering issue with the QFT

Actually, let me be more careful. The phase of T gate on |1⟩ is e^(iπ/4). In standard phase estimation, we have U|ψ⟩ = e^(i2πθ)|ψ⟩, so e^(i2πθ) = e^(iπ/4), giving θ = 1/8.

Binary: θ = 0.001₂

In the circuit:
- anc[0] controls T¹ → phase e^(iπ/4·1) when anc[0]=1
- anc[1] controls T²=S → phase e^(iπ/4·2) when anc[1]=1
- anc[2] controls T⁴=Z → phase e^(iπ/4·4) when anc[2]=1

The phase for basis state |k₂k₁k₀⟩ is:
φ = k₀·π/4 + k₁·π/2 + k₂·π = π/4(k₀ + 2k₁ + 4k₂)

So e^(iφ) = e^(iπ(k₀ + 2k₁ + 4k₂)/4)

This encodes θ = (k₀ + 2k₁ + 4k₂)/8 in the phase.

After inverse QFT, we extract θ = 1/8 = 0.001₂.

With the QFT structure used here (with the swap (three-CNOT decomposition)), the output should be |100⟩ because:
- The QFT maps |j⟩ → Σ_k e^(2πijk/2^n) |k⟩
- The inverse QFT with SWAPs reverses qubit order

So the expected measurement is |100⟩ with probability 1.

Let me structure the reasoning:

## Reasoning
1. Goal: Implement 3-qubit phase estimation of T gate eigenvalue using a 2-qubit target register.

2. Qubits: 5 total (anc[3] for

## isqTrain/349

- task_id: `isqTrain/349`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `2421`

### Prompt

Implement a quantum circuit in isQ: implements the arithmetic_circuit pattern. Include explicit identity operations in the circuit (X-X pair before M(p[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

Let me analyze this isQ quantum program step by step.

**Goal of the circuit:**
The circuit implements an arithmetic_circuit pattern with controlled operations and demonstrates gate cancellation with an X-X pair.

**Qubits:**
- `c[1]`: 1 control qubit
- `p[2]`: 2 parameter/measurement qubits
- Total: 3 qubits
- Measured: `p[0]` and `p[1]` (2 qubits)

**Step-by-step state evolution:**

Initial state: |000⟩ (c[0], p[0], p[1])

1. **H(c[0])**: Hadamard on control qubit
   - |000⟩ → (1/√2)(|000⟩ + |100⟩)

2. **ctrl INC(c[0], p[0], p[1])**: Controlled INC
   - INC(p[0], p[1]) = { CNOT(p[0], p[1]); X(p[0]); }
   - When c[0]=|1⟩, apply INC to p[0], p[1]
   - Since p[0]=|0⟩ initially: CNOT(0,0) does nothing, then X(p[0]) flips p[0]
   - State: (1/√2)(|000⟩ + |110⟩)

3. **nctrl DEC(c[0], p[0], p[1])**: Negative-controlled DEC (apply when c[0]=|0⟩)
   - DEC(p[0], p[1]) = { X(p0); CNOT(p0, p1); }
   - When c[0]=|0⟩, p[0]=|0⟩: X(p[0]) → p[0]=|1⟩, then CNOT(p[0], p[1]) → p[1]=|1⟩
   - State: (1/√2)(|011⟩ + |110⟩)

4. **X(p[0])**: First X gate on p[0]
   - |011⟩ → |111⟩, |110⟩ → |010⟩
   - State: (1/√2)(|111⟩ + |010⟩)

5. **X(p[0])**: Second X gate on p[0] (cancels with first)
   - |111⟩ → |011⟩, |010⟩ → |110⟩
   - State: (1/√2)(|011⟩ + |110⟩)

6. **M(p[0])** and **M(p[1])**: Measure p[0] and p[1]

Final state before measurement (tracing out c[0]):
(1/√2)(|011⟩ + |110⟩)

Looking at just p[0] and p[1]:
- In |011⟩: p[0]=|1⟩, p[1]=|1⟩ → |11⟩
- In |110⟩: p[0]=|1⟩, p[1]=|0⟩ → |10⟩

So measurement probabilities:
- |10⟩: 0.5
- |11⟩: 0.5

This matches the predicted output!

**Gate cancellation awareness:**
The X-X pair on p[0] demonstrates that X*X = I (identity), so these two gates cancel each other. This is important for circuit optimization.

Let me write the reasoning section:

## Reasoning

1. **Goal**: Implement an arithmetic_circuit pattern with controlled INC/DEC operations and demonstrate X-X gate cancellation.

2. **Qubits**: 3 qubits total (c[0], p[0], p[1]); measuring p[0] and p[1] (2 qubits).

3. **State evolution**:
   - Initial: |000⟩
   - H(c[0]): (1/√2)(|000⟩ + |100⟩)
   - ctrl INC: applies {CNOT(p0,p1); X(p0)} when c=|1⟩ → (1/√2)(|000⟩ + |110⟩)
   - nctrl DEC: applies {X(p0); CNOT(p0,p1)} when c=|0⟩ → (1/√2)(|011⟩ + |110⟩)
   - X(p[0]): (1/√2)(|111⟩ + |010⟩)
   - X(p[0]): (1/√2)(|011⟩ + |110⟩) [cancels previous X]

4. **Expected probabilities**: The final state has equal amplitude for |011⟩ and |110⟩. Tracing out c[0], the measurement outcomes on p[0],p[1] are |11⟩ and |10⟩, each with probability 0.5. The X

## isqTrain/1202

- task_id: `isqTrain/1202`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `300`

### Prompt

帮我写一个isQ程序：implements the qaoa pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for a QAOA circuit that implements MaxCut on a 2-node graph with p=1.

Let me trace through the circuit:

1. **Initial state**: |00>

2. **Hadamard on both qubits**: Creates uniform superposition
   H(q[0]) and H(q[1]) → |+⟩|+⟩ = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2

3. **Cost layer (ZZ interaction)**:
   - CNOT(q[0], q[1]): |00⟩→|00⟩, |01⟩→|01⟩, |10⟩→|11⟩, |11⟩→|10⟩
   - Rz(-0.78539816339745, q[1]): This is Rz(-π/4) on q[1]
   - CNOT(q[0], q[1]): Uncomputes

   The effect of CNOT-Rz(γ)-CNOT is equivalent to Rzz(-γ) = exp(iγ Z⊗Z/2)
   
   With γ = -π/4, this is exp(-iπ/4 * Z⊗Z/2) = exp(-iπ/8 * Z⊗Z)

4. **Mixer layer**: Rx(π/4) on each qubit
   Rx(0.78539816339745, q[0]) and Rx(0.78539816339745, q[1])

5. **X-X pair on q[0]**: Two X gates cancel out (identity)

6. **Measurement**: M(q[0]) and M(q[1])

Let me verify the probabilities:
- |00⟩: 0.07322330470336282
- |01⟩: 0.4267766952966372
- |10⟩: 0.4267766952966372
- |11⟩: 0.07322330470336282

These probabilities sum to 1. The symmetry suggests equal probability for |01⟩ and |10⟩ (the MaxCut solutions for a 2-node graph), which makes sense.

Note: 0.07322330470336282 ≈ (1 - 1/√2)/4 ≈ (2 - √2)/4
And 0.4267766952966372 ≈ (1 + 1/√2)/4 ≈ (2 + √2)/4

Actually let me recalculate: √2 ≈ 1.41421356
(2 - √2)/4 ≈ (2 - 1.41421356)/4 ≈ 0.58578644/4 ≈ 0.14644661... 

Hmm that's not matching. Let me try another approach.

0.07322330470336282 ≈ sin²(π/8)/2 or something like that?

sin(π/8) ≈ 0.3826834
sin²(π/8) ≈ 0.1464466

0.07322330 ≈ 0.1464466/2

So |00⟩ and |11⟩ have probability sin²(π/8)/2 each
|01⟩ and |10⟩ have probability cos²(π/8)/2 each

cos²(π/8) ≈ 0.8535534
0.8535534/2 ≈ 0.4267767 ✓

This makes sense for the QAOA with these parameters - it maximizes the probability of measuring the MaxCut solutions (|01⟩ and |10⟩).

Now let me write the reasoning:

## Reasoning

This circuit implements a QAOA algorithm (p=1) for MaxCut on a 2-node graph to find the optimal cut assignment.

Two qubits are used (q[0], q[1]) and both are measured at the end.

**State evolution:**
1. Start: |00⟩
2. After H⊗H: (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2 = |+⟩|+⟩
3. Cost layer (CNOT-Rz(-π/4)-CNOT): Applies exp(iπ/8·Z₀Z₁), entangling qubits with phase depending on ZZ parity
4. Mixer layer (Rx(π/4) on each): Rotates each qubit around X-axis by π/4
5. X-X pair on q[0]: These cancel (XX = I), having no effect on the state
