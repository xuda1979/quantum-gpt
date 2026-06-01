# ISQ training COT RAG corpus: quantum_algorithms shard 194

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqQA/quantum_algorithms/100_hardware_limitations

- task_id: `isqQA/quantum_algorithms/100_hardware_limitations`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `hardware_limitations`, `algorithm`, `Grover自适应搜索`
- source: `qa_pipeline`
- dataset_index: `4717`

### Prompt

在NISQ（含噪声中等规模量子）设备上实现Grover自适应搜索（Grover Adaptive Search, GAS）时，量子系统的退相干和有限的量子门保真度如何导致算法出现“噪声谷底”现象？请从密度矩阵演化的数学角度分析这一局限性，并提供一段针对硬件局限性进行浅层线路优化的isQ代码示例。

### Reference answer

在量子计算硬件的NISQ时代，Grover自适应搜索（GAS）面临着严峻的物理局限性挑战。GAS的核心在于通过反复应用预言机 和扩散算子 来放大目标态的概率幅，并在经典外循环中动态更新搜索阈值。然而，NISQ设备上的噪声会严重破坏这一过程。

从数学推导的角度来看，在理想的无噪声封闭系统中，经过k次Grover迭代后，找到目标态的概率为 P_ideal(k) = sin^2((2k+1)θ)，其中 sin^2(θ) = M/N（M为匹配解的数量，N为搜索空间）。但在NISQ设备上，量子态会与环境发生纠缠，必须使用密度矩阵 ρ 来描述系统的演化。假设单次Grover迭代的时间为 τ，且系统主要受到消相位噪声的影响，则演化过程可由算子酉和克拉布斯算子之和来近似描述。每次迭代后，密度矩阵的非对角元（包含量子叠加和干涉所需的相位信息）会以 exp(-kτ/T2) 的速率衰减，其中 T2 是量子比特的横向弛豫时间。

随着迭代次数 k 的增加，保真度的衰减会导致概率幅放大效应失效。当 kτ 达到或超过 T2 时，系统的非对角元几乎完全衰减，状态趋于最大混合态。此时，无论再增加多少次迭代，目标态的测量概率都将退化至均匀随机分布（即 1/N），这种现象被称为“噪声谷底”。此外，GAS需要深层的多控门（如Toffoli门）来构建复杂的代价函数预言机，而当前的硬件需要将其分解为大量的单双比特门，这进一步拉长了线路深度 τ，导致在实际操作中往往只需几次迭代就会触发退相干灾难。

为了在NISQ设备上缓解这一问题，当前的主流策略是采用“浅层变分”或“少步长”的Grover搜索。即牺牲单次搜索的最大理论概率，强制限制迭代次数（如仅执行1次或2次Grover迭代），依赖经典计算机的外循环来多次更新阈值。以下是一段基于isQ语言编写的针对浅层线路优化的示例代码，该代码避免了深层的复杂迭代，并将多控门分解为硬件亲和性更高的Toffoli和基础单双比特门，从而最大限度地缩短退相干时间窗口：

import std;

qbit q[3];
qbit anc[1];

// 针对NISQ硬件优化的扩散算子
procedure diffusion() {
    for i in 0:3 {
        H(q[i]);
        X(q[i]);
    }
    // 为减少门分解开销，使用单H门结合Toffoli实现相位反演
    H(q[2]);
    Toffoli(q[0], q[1], q[2]);
    H(q[2]);
    
    for i in 0:3 {
        X(q[i]);
        H(q[i]);
    }
}

procedure main() {
    // 初始化搜索寄存器和辅助比特
    for i in 0:3 { H(q[i]); }
    X(anc[0]);
    H(anc[0]);
    
    // 针对退相干的浅层Grover迭代（强制仅执行1次迭代）
    // 假设GAS当前阈值下，我们通过经典计算得出需要标记的解（如|110>）
    // 构建轻量化的相位反转预言机
    X(q[0]);
    Toffoli(q[0], q[1], anc[0]);
    X(q[0]);
    
    // 执行单次扩散操作以避免陷入噪声谷底
    diffusion();
    
    // 测量并交由经典计算机处理，进入下一个GAS自适应循环
    // 测量指令视具体运行环境而定
}

通过上述数学分析和代码策略可以看出，在NISQ阶段，GAS算法的成功率不再单纯依赖于量子加速，而是高度仰赖于经典-量子混合架构中线路深度的严格控制和错误缓解技术的应用。

## isqTrain/3916

- task_id: `isqTrain/3916`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `367`

### Prompt

这个isQ程序有问题，请找出错误并给出正确代码：

```
import std;
// QFT on 4 qubits with input state |0111>
qbit q[4];

procedure main() {
    // Prepare input state |0111>
    Y(q[1]);
    X(q[2]);
    X(q[3]);

    // QFT stage for qubit 0
    H(q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 16.0, q[3], q[0]);
    // QFT stage for qubit 1
    H(q[1]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[3], q[1]);
    // QFT stage for qubit 2
    H(q[2]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[3], q[2]);
    // QFT stage for qubit 3
    H(q[3]);
    // Swap q[0] and q[3]
    CNOT(q[0], q[3]);
    CNOT(q[3], q[0]);
    CNOT(q[0], q[3]);
    // Swap q[1] and q[2]
    CNOT(q[1], q[2]);
    CNOT(q[2], q[1]);
    CNOT(q[1], q[2]);
    // Measure after QFT
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **The bug**: In the input state preparation, `Y(q[1])` was used instead of `X(q[1])`. The Y gate applies Y|0⟩ = i|1⟩, which introduces an unwanted phase factor (i), whereas X|0⟩ = |1⟩ cleanly prepares the |1⟩ state.

2. **The fix**: Replace `Y(q[1])` with `X(q[1])` to correctly prepare the input state |0111⟩ without phase errors.

3. **State evolution of corrected circuit**:
   - Initial state: |0000⟩
   - After X(q[1]), X(q[2]), X(q[3]): |0111⟩ (decimal 7)
   - QFT|7⟩ produces: (1/4) Σ_{k=0}^{15} e^{2πi·7k/16} |k⟩
   - Each basis state has magnitude |1/4| = 1/4, so probability = 1/16 = 0.0625 for all 16 outcomes
   - After swap operations, the output order matches the standard bit ordering
   - Measurement yields uniform distribution: {|0000⟩: 0.0625, |0001⟩: 0.0625, ..., |1111⟩: 0.0625} ✓

## isqTrain/1413

- task_id: `isqTrain/1413`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_ctrl_nctrl`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5588`

### Prompt

请用isQ语言编写一个量子电路：Apply the 2-qubit Quantum Fourier Transform to the input state |00> and measure all qubits.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Task:** Create a "Reasoning" section for an isQ quantum program.
    *   **Circuit:** 2-qubit Quantum Fourier Transform (QFT) applied to $|00\rangle$, followed by measurement.
    *   **Role:** Quantum computing expert.
    *   **Constraints:** Use Dirac notation. Concise (3-15 lines). ONLY output the reasoning section, starting with "## Reasoning". NO code blocks.

2.  **Analyze the Circuit:**
    *   **Input State:** $|q_1 q_0\rangle = |00\rangle$. (Wait, standard Qiskit/isQ indexing usually has $q_0$ as lowest index, but let's trace the reference code).
    *   *Reference code trace:*
        *   `qbit q[2];` -> Initial state $|00\rangle$ (q[0], q[1]). Let's write it as $|0\rangle_0 \otimes |0\rangle_1$.
        *   `H(q[1]);` -> $|0\rangle_0 \otimes |+\rangle_1 = \frac{1}{\sqrt{2}}(|00\rangle + |01\rangle)$.
        *   `ctrl S(q[0], q[1]);` -> controlled-S gate. q[0] is control, q[1] is target.
            *   For $|00\rangle$: no change.
            *   For $|01\rangle$: S on q[1] gives $i|1\rangle$. So $\frac{1}{\sqrt{2}}(|00\rangle + i|01\rangle)$.
        *   `H(q[0]);` -> H on q[0].
            *   $H_0 |0\rangle_0 = |+\rangle_0$.
            *   State becomes $\frac{1}{2}(|00\rangle + |10\rangle + i|01\rangle + i|11\rangle)$.
            *   *Wait, let's check the standard 2-qubit QFT formula.*
            *   QFT on $|00\rangle$ should yield $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
            *   Let's re-evaluate the reference code's swap (three-CNOT decomposition): `swap (three-CNOT decomposition)(q[0], q[1])`.
            *   Before swap (three-CNOT decomposition): $\frac{1}{2}(|00\rangle + |10\rangle + i|01\rangle + i|11\rangle)$. (Assuming q[1] is left bit, q[0] is right bit, $|q_1 q_0\rangle$).
            *   Let's use the state vector where q[0] is the least significant bit (LSB) or most significant bit (MSB)? In isQ/probabilities, earlier measured qubit = higher bit (MSB). Let's write states as $|q_0 q_1\rangle$ or $|q_1 q_0\rangle$ carefully. Standard tensor product: $|q_0\rangle \otimes |q_1\rangle$. Let's just use standard QFT formulation.
            *   QFT of $|00\rangle$ is $|++\rangle = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
            *   Let's re-trace reference:
                *   Init: $|00\rangle$ (q[0]=0, q[1]=0)
                *   `H(q[1])`: $|0\rangle_0 \otimes |+\rangle_1$
                *   `ctrl S(q[0], q[1])`: S applied to q[1] if q[0] is 1. Since q[0] is 0, this does nothing. State is still $|0\rangle_0 \otimes |+\rangle_1$.
                *   `H(q[0])`: $|+\rangle_0 \otimes |+\rangle_1$.
                *   `swap (three-CNOT decomposition)(q[0], q[1])`: SWAPs the qubits, but since both are $|+\rangle$, the state remains $|+\rangle_0 \otimes |+\rangle_1 = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
            *   Measurement: Equal 25% probability for each basis state.

3.  **Drafting the Reasoning Steps:**
    *   **Goal:** Apply the 2-qubit Quantum Fourier

## isqTrain/3985

- task_id: `isqTrain/3985`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `527`

### Prompt

这个isQ程序有问题，请找出错误并给出正确代码：

```
import std;
// Inverse QFT on 3 qubits with input |011>
qbit q[3];

procedure main() {
    // Prepare input
    X(q[1]);
    X(q[2]);

    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[2], q[0]);
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

The task is to analyze the bug in the given isQ code for a 3-qubit inverse QFT with input |011>.

Let me first understand the task:
- We have a 3-qubit inverse QFT circuit
- Input state is |011> (q[0]=0, q[1]=1, q[2]=1)
- The bug is "swapped_qubits"

Let me look at the buggy code:

Fixed code:

So the bug is in the third CNOT of the swap operation (three-CNOT decomposition). The buggy code has `CNOT(q[2], q[0])` but should be `CNOT(q[0], q[2])`.

The three CNOTs should form a swap operation (three-CNOT decomposition) between q[0] and q[2]:
- CNOT(q[0], q[2]) - control q[0], target q[2]
- CNOT(q[2], q[0]) - control q[2], target q[0]
- CNOT(q[0], q[2]) - control q[0], target q[2]

But the buggy code has:
- CNOT(q[0], q[2])
- CNOT(q[2], q[0])
- CNOT(q[2], q[0])  <- wrong

This third CNOT should have q[0] as control and q[2] as target, not the other way around.

Now let me verify the state evolution with the corrected circuit:

Initial state: |000>

After X(q[1]) and X(q[2]): |011>

Now the swap (three-CNOT decomposition) between q[0] and q[2]:
- Before swap (three-CNOT decomposition): |011> = |0⟩|1⟩|1⟩
- After swap (three-CNOT decomposition): |110> = |1⟩|1⟩|0⟩

Wait, let me think about the qubit ordering. In isQ, typically q[0] is the least significant bit, so |011> means q[2]=0, q[1]=1, q[0]=1.

Actually, let me reconsider. The comment says "input |011>". In the context of the problem:
- q[0] corresponds to the rightmost bit
- q[1] corresponds to the middle bit
- q[2] corresponds to the leftmost bit

So |011> means:
- q[2] = 0
- q[1] = 1
- q[0] = 1

But the code prepares with X(q[1]) and X(q[2]), which gives:
- q[0] = 0 (no X applied)
- q[1] = 1 (X applied)
- q[2] = 1 (X applied)

So the state is |110> in the standard notation (q[2]q[1]q[0]).

Wait, this is confusing. Let me think about the standard convention.

In quantum computing, |abc⟩ typically means qubit 2 is a, qubit 1 is b, qubit 0 is c.

But the comment says input |011> and prepares with X(q[1]) and X(q[2]). This gives:
- q[0] = 0
- q[1] = 1
- q[2] = 1

So if we write the state as |q[2]q[1]q[0]⟩, it's |110⟩.

But the comment says input |011>. This could mean the input in the QFT sense is the computational basis state |3⟩ = |011⟩.

Actually, I think the convention here is that |011⟩ means q[0]=1, q[1]=1, q[2]=0 (little-endian). So:
- X(q[0]) should be applied for the LSB
- X(q[1]) should be applied for the middle bit

But the code applies X(q[1]) and X(q[2]), which would correspond to |011⟩ in big-endian where q[2] is MSB.

Hmm, let me just trust the code and the predicted output.

For inverse QFT on 3 qubits:

The QFT maps computational basis states to Fourier basis states:
QFT|j⟩ = (1/√N) Σ_k e^{2πijk/N} |k⟩

where N = 2^n.

## isqExpand/algo/24

- task_id: `isqExpand/algo/24`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `teleportation`, `classical_correction`, `bug_fix`
- source: `isq_expansion`
- dataset_index: `122`

### Prompt

Debug this isQ program — it gives unexpected measurement results.

```isq
import std;
qbit q[3];

procedure main() {
    X(q[0]);
    H(q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[0], q[1]);
    H(q[0]);
    int m0 = M(q[0]);
    int m1 = M(q[1]);
    if (m0 == 1) {
        X(q[2]);
    }
    if (m1 == 1) {
        Z(q[2]);
    }
    M(q[2]);
}
```

### Chain-of-thought reasoning

## Bug Analysis

In quantum teleportation, the correction mapping is:
- m1 (measurement of q[1], the CNOT target) → X correction on q[2]
- m0 (measurement of q[0], the H qubit) → Z correction on q[2]

The bug swaps these: m0 triggers X and m1 triggers Z, which is backwards.

Fix: Swap the conditions:
- if (m1 == 1) { X(q[2]); }
- if (m0 == 1) { Z(q[2]); }

This correctly implements the teleportation corrections based on the Bell measurement outcomes.

## isqTrain/2975

- task_id: `isqTrain/2975`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_multi_register`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `134`

### Prompt

This isQ program doesn't produce the correct output. Can you debug it?

Code:
```isq
import std;
qbit q[4];
// 2-layer H+CNOT circuit on 4 qubits
procedure main() {
    H(q[0]);
    H(q[1]);
    H(q[2]);
    H(q[3]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
    CNOT(q[3], q[0]);
    H(q[0]);
    H(q[1]);
    // H(q[2]); // BUG: missing Hadamard
    H(q[3]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
    CNOT(q[3], q[0]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **The bug** is a missing Hadamard gate on `q[2]` in the second layer of the circuit (indicated by the commented-out line `// H(q[2]);`). This breaks the intended symmetric evolution of the state vector, as `q[2]` skips the superposition step prior to the final CNOT ring.

2. **The fix** is to restore the `H(q[2])` gate, placing it exactly between the Hadamard operations on `q[1]` and `q[3]`.

3. **State evolution**: 
- All

## isqTrain/1292

- task_id: `isqTrain/1292`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `interference`, `isq_syntax_oracle`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `763`

### Prompt

请用isQ语言编写一个量子电路：implements the fourier_checking pattern using an alternative gate decomposition (CZ -> H CNOT H). The circuit must produce the same output as the standard decomposition.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a 3-qubit Fourier checking circuit where CZ gates are decomposed as H-CNOT-H, producing the same measurement distribution as the standard decomposition.

2. **Qubits**: 3 qubits (q[0], q[1], q[2]), all measured at the end.

3. **State evolution**:
   - **Initial**: |000⟩
   - **First H layer**: |000⟩ → |+++⟩ = (1/√8)Σ|x⟩ for x∈{0,1}³
   - **Oracle f (T gates)**: Applies phase e^(iπ/4) per |1⟩ in each qubit → (1/√8)Σ e^(iπ·wt(x)/4)|x⟩ where wt is Hamming weight
   - **CZ(0,1) via H-CNOT-H**: Entangles q[0],q[1] with conditional phase; H(q[1]) rotates to Z-basis, CNOT adds parity phase, H(q[1]) returns
   - **CZ(1,2) via H-CNOT-H**: Same decomposition on q[1],q[2], applying controlled-Z through the H-CNOT-H sandwich
   - **Middle H layer**: Transforms to Fourier basis for oracle g
   - **Oracle g (S gates)**: Applies phase i to |1⟩ components, creating interference with oracle f phases
   - **Final H layer**: Returns to computational basis, producing interference between f and g phase patterns

4. **Expected probabilities**: The final state amplitudes reflect the inner product ⟨ĝ|f⟩, giving non-uniform distribution: P(|010⟩)≈0.232, P(|111⟩)≈0.232 are largest; P(|011⟩)≈0.018, P(|110⟩)≈0.018 are smallest—consistent with Fourier checking where correlated f,g yield biased output.

## isqExpand/algo/186

- task_id: `isqExpand/algo/186`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `vqe`, `hardware_efficient_ansatz`, `rotation_gates`, `entanglement`, `cnot`
- source: `isq_expansion`
- dataset_index: `1984`

### Prompt

Create an isQ quantum circuit that a 2-qubit VQE hardware-efficient ansatz with Ry(1.5708) on q[0], Ry(0.3927) on q[1], followed by CNOT entangling layer and measurement.

### Chain-of-thought reasoning

Step 1: Start with |00⟩ initial state. Step 2: Apply Ry(1.5708≈π/2) to q[0], rotating |0⟩→(1/√2)|0⟩+(1/√2)|1⟩, giving state (1/√2)|00⟩+(1/√2)|10⟩. Step 3: Apply Ry(0.3927≈π/8) to q[1], giving (1/√2)[cos(π/16)|00⟩-sin(π/16)|01⟩+cos(π/16)|10⟩-sin(π/16)|11⟩]. cos(π/16)=0.9808, sin(π/16)=0.1951. Step 4: Apply CNOT(q[0],q[1]) which maps |10⟩→|11⟩ and |11⟩→|10⟩. Final state: (1/√2)cos(π/16)(|00⟩+|11⟩) - (1/√2)sin(π/16)(|01⟩+|10⟩). Probabilities: P(00)=(1/2)cos²(π/16)=0.48097, P(01)=(1/2)sin²(π/16)=0.01903, P(10)=(1/2)sin²(π/16)=0.01903, P(11)=(1/2)cos²(π/16)=0.48097. Sum=1.0 ✓

## isqTrain/913

- task_id: `isqTrain/913`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`
- source: `isq_train_cot`
- dataset_index: `3136`

### Prompt

I need an isQ program to implements a variant of the bit_flip_oracle pattern using q[2] -> q[4]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement a bit-flip oracle computing AND(x₀, x₁) on an expanded 5-qubit register, with q[2], q[3] left as ground-state spectators.

2. **Qubits**: 5 total — `q[0..3]` and `ancilla[0]`. All are measured: `M(q[0..3]); M(ancilla[0])`.

3. **State evolution**:
   - Initialize |ψ₀⟩ = |00000⟩ (q[0..3], ancilla all |0⟩)
   - `X(q[0]); X(q[1])` → |ψ₁⟩ = |11000⟩
   - `f(q, ancilla)` computes AND(1,1)=1: ancilla flips → |ψ₂⟩ = |11001⟩
   - Spectator qubits q[2], q[3] remain in |0⟩ throughout

4. **Expected probability**: With all qubits in a definite computational basis state |11001⟩, measurement yields |11001⟩ with probability 1.0.

## isqTrain/749

- task_id: `isqTrain/749`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1675`

### Prompt

请用isQ语言编写一个量子电路：implements the modular_adder pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Implement a modular adder that computes (a + 1) mod 3, demonstrating gate cancellation with an X-X identity pair.

**Qubits:** 3 qubits (q[0], q[1], q[2]); only q[0] and q[1] are measured.

**State evolution:**
1. Initial: |000⟩
2. X(q[1]): |010⟩ — encodes a=2
3. X(q[0]): |011⟩ — adds 1, now value=3
4. Toffoli(q[0],q[1],q[2]): |111⟩ — overflow flag set (both bits were 1)
5. CNOT(q[2],q[0]): |101⟩ — subtract 3 (flip q[0])
6. CNOT(q[2],q[1]): |100⟩ — subtract 3 (flip q[1])
7. X(q[0]): |000⟩
8. X(q[0]): |000⟩ — X-X pair cancels (identity), demonstrating gate cancellation awareness

**Measurement:** State |000⟩ → measuring q[0],q[1] yields |00⟩ with probability 1.0.
