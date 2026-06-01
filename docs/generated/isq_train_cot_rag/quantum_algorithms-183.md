# ISQ training COT RAG corpus: quantum_algorithms shard 183

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3420

- task_id: `isqTrain/3420`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `entanglement`, `basis_change`, `ancilla_usage`, `isq_syntax_arrays`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `3777`

### Prompt

Create an isQ quantum circuit that the encoding circuit for the Shor 9-qubit error correction code in isQ, encoding the logical |0> state.

The Shor code combines the 3-qubit phase-flip and bit-flip codes:
  |0_L> = (|000>+|111>)(|000>+|111>)(|000>+|111>) / 2*sqrt(2)

Encoding circuit:
1. Start with q[0] in |0>
2. CNOT(q[0], q[3]) and CNOT(q[0], q[6]) (phase-flip encoding)
3. H on q[0], q[3], q[6]
4. CNOT(q[0], q[1]), CNOT(q[0], q[2]) (bit-flip block 1)
5. CNOT(q[3], q[4]), CNOT(q[3], q[5]) (bit-flip block 2)
6. CNOT(q[6], q[7]), CNOT(q[6], q[8]) (bit-flip block 3)

To verify encoding, decode and measure. Decoding reverses all steps.
Expected after decode: |000000000> with probability 1.0.

Note: Only measure the first 8 qubits to keep probability array at 256 entries. The 9th qubit is always |0> after correct decode.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for the Shor 9-qubit error correction code encoding circuit in isQ.

Let me trace through the circuit:

1. Start with |000000000> (9 qubits, but we split into q[8] and r[1])

2. CNOT(q[0], q[3]) and CNOT(q[0], q[6]):
   - |000000000> → |000000000> (since q[0]=|0>, CNOT does nothing)
   - Wait, that's not right. If q[0] is |0>, CNOT doesn't flip target. So state remains |000000000>.

Hmm, but that doesn't make sense for encoding. Let me re-read the problem.

Actually, the circuit starts with q[0] in |0>, and all others in |0>. The phase-flip encoding with CNOT from |0> doesn't do anything. Then Hadamard on q[0], q[3], q[6] would give:
|+0+0+00> = (|0>+|1>)/√2 ⊗ |0> ⊗ (|0>+|1>)/√2 ⊗ |0> ⊗ (|0>+|1>)/√2 ⊗ |00>

Wait, that doesn't produce the Shor code either.

Let me reconsider. The Shor code encoding for |0_L>:
|0_L> = (|000>+|111>)⊗(|000>+|111>)⊗(|000>+|111>) / (2√2)

This is indeed the product of three GHZ-like states each in the |+> basis.

To encode starting from |0>|0>...|0>:

Actually, wait. Analyzing the circuit requirements more carefully:

1. Start: |000000000>
2. CNOT(q[0], q[3]): still |000000000> (control is |0>)
3. CNOT(q[0], q[6]): still |000000000>

So after phase-flip encoding, nothing changed. Then:
4. H(q[0]): (|0>+|1>)|0000000>/√2
5. H(q[3]): (|0>+|1>)|0>(|0>+|1>)|00000>/(2)... wait let me be more careful.

Wait, the phase-flip encoding is supposed to start with a different initial state, or there's a different approach.

Let me re-read the problem statement more carefully:

"Encoding circuit:
1. Start with q[0] in |0>
2. CNOT(q[0], q[3]) and CNOT(q[0], q[6]) (phase-flip encoding)
3. H on q[0], q[3], q[6]"

Hmm, if we start with |0>, the CNOTs don't do anything. Then the Hadamards create |+++000000> effectively (well, on positions 0, 3, 6). Then the bit-flip CNOTs spread each + state.

Let me trace:
After step 2: |000000000> (no change since control is |0>)
After H on q[0], q[3], q[6]: 
|+⟩|0⟩|0⟩|+⟩|0⟩|0⟩|+⟩|0⟩|0⟩ / (2√2)
= (|0⟩+|1⟩)|0⟩|0⟩(|0⟩+|1⟩)|0⟩|0⟩(|0⟩+|1⟩)|0⟩|0⟩ / (2√2)

Now bit-flip encoding:
CNOT(q[0], q[1]), CNOT(q[0], q[2]):
This copies the state of q[0] to q[1] and q[2].
When q[0]=|0⟩: q[1],q[2] stay |0⟩
When q[0]=|1⟩: q[1],q[2] become |1⟩

So (|000⟩+|111⟩)|0⟩|0⟩(|0⟩+|1⟩)|0⟩|0⟩(|0⟩+|1⟩)|0⟩|0⟩ / (2√2)

Wait, that's not quite right. Let me be more careful.

After H on q[0], q[3], q[6]:
1/(2√2) * (|0⟩+|1⟩)_0 |00⟩_{1,2} (|0⟩+|1⟩)_3 |00⟩_{4,5} (|0⟩+|1⟩)_6 |00⟩_{7,8}

After CNOT(q[0], q[1]) and CNOT(q[0], q[2]):
When

## isqQA/quantum_algorithms/101_hardware_limitations

- task_id: `isqQA/quantum_algorithms/101_hardware_limitations`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `hardware_limitations`, `algorithm`, `Grover搜索的最优性证明`
- source: `qa_pipeline`
- dataset_index: `918`

### Prompt

Grover搜索算法在理论上被证明是最优的，其查询复杂度为O(√N)（即在包含N个元素的未排序数据库中找到目标，理论上只需迭代约π/4√N次Oracle查询）。然而，在当前的NISQ（含噪声中等规模量子）设备上，这种理论最优性却受到硬件局限性（特别是退相干效应和有限的门保真度）的严重制约。请详细推导并分析退相干效应如何改变Grover算法理论上的“最优迭代次数”，并给出在噪声环境下寻找实际最优迭代策略的数学基础。进而，请使用isQ语言编写一个针对3量子比特（N=8）且目标态为|111⟩的Grover搜索示例代码，并在代码结构中体现适应NISQ硬件特性的浅层电路策略。

### Reference answer

<think_this>首先，分析无噪声情况下的Grover搜索理论最优性：设搜索空间大小为N=2^n，目标态数量为M=1。初始均匀叠加态与目标态的夹角定义为θ/2，其中 sin(θ/2) = 1/√N。每次Grover迭代（包含Oracle和扩散算子）将系统状态向目标态旋转θ。经过k次迭代后，测量得到目标态的概率为 P(k) = sin^2((2k+1)θ/2)。当k接近 π/(4θ) - 1/2 ≈ π√N/4 时，P(k)达到最大值（接近1）。接下来，引入NISQ硬件的退相干影响：在当前硬件中，量子态会随时间指数级衰减，且每层门的操作都会累积错误。假设单个Grover迭代电路（包含大量双量子比特门）造成整体保真度衰减率为 e^{-λ}（λ取决于T1、T2及门错误率）。经过k次迭代后，有效保真度衰减为 e^{-λk}。因此，考虑退相干后的实际测量成功概率变为：P_noise(k) ≈ sin^2((2k+1)θ/2) * e^{-λk}。为了在NISQ设备上找到实际的最优迭代次数 k_opt，需要对 P_noise(k) 求导并令其等于0：d/dk [ sin^2((2k+1)θ/2) * e^{-λk} ] = 0。化简后得到近似条件：tan((2k+1)θ/2) ≈ θ/(2λ)。这意味着在存在显著退相干（λ较大）的硬件中，实际最优迭代次数 k_opt 通常会显著小于理论上的 π√N/4。过度追求理论上的最高概率反而会因为电路深度过长导致极低的保真度。因此，NISQ策略往往是截断迭代次数（例如仅迭代1次），牺牲单次运行的理论最高概率，转而通过多次采样来弥补，以避免因深度过长导致的“反向旋转且伴随退相干”的双重惩罚。在isQ代码实现中，针对3比特（N=8），理论上需迭代2次，但考虑NISQ退相干限制，我们选择仅迭代1次。此外，为了降低扩散算子的门深度，避免使用深层的辅助比特，我们将扩散算子等效替换为作用在计算基态上的控制相位门结构。</think_this>Grover搜索算法在理论上被证明是最优的，其查询复杂度为O(√N)。在理想的无噪声量子计算机中，设搜索空间大小为 N=2^n，目标态数量 M=1。初始均匀叠加态与目标态的夹角满足 sin(θ/2) = 1/√N。每次Grover迭代将系统状态向目标态旋转角度 θ，经过 k 次迭代后，测量得到目标态的概率为：P(k) = sin^2((2k+1)θ/2)。理论上，最优迭代次数为 k_ideal ≈ π√N / 4。然而，在当前的NISQ（含噪声中等规模量子）设备上，这种理论最优性受到严重制约。硬件的局限性主要体现在退相干效应（受限于T1和T2时间）以及不完美的量子门保真度（特别是多量子比特门）。在Grover算法中，扩散算子和Oracle需要大量的CNOT门级联，这使得单次Grover迭代的电路深度极大。假设单次Grover迭代由于门错误和环境退相干带来的有效振幅保留率为 e^{-λ}（λ为与硬件相关的退相干系数）。经过 k 次迭代后，整个量子态保真度衰减至 e^{-λk}。因此，在NISQ设备上实际获得目标态的概率变为：P_NISQ(k) = sin^2((2k+1)θ/2) * e^{-λk}。为了寻找在噪声环境下的实际最优迭代次数 k_opt，我们求导并令其为零：d/dk [ sin^2((2k+1)θ/2) * e^{-λk} ] = 0。利用乘积求导法则，可得到近似关系式：tan((2k+1)θ/2) ≈ θ/(2λ)。这揭示了一个重要的物理结论：当硬件退相干效应显著（λ较大）时，由于 tan 值被限制在一个较小的范围内，实际的 k_opt 会大幅减小。如果继续按照理论的 k_ideal 进行迭代，不仅会由于“过度旋转”导致理论上成功概率下降，更会因为 e^{-λk} 的指数衰减导致实际结果几乎全是噪声。因此，针对NISQ硬件的实用策略是“浅层化”：接受较大的单次误差，通过严格控制迭代次数 k（例如对于 N=8，理论上 k=2.2，实际设备上往往 k=1 的整体效果最好），以此来规避中后期的深度退相干陷阱。以下提供使用isQ语言编写的3比特Grover算法示例代码。在代码设计中，考虑到NISQ硬件的局限性，我们刻意将迭代次数限制为1次；同时，在扩散算子（Diffusion Operator）的实现中，不引入额外的辅助比特，而是利用Toffoli门和单比特门来等效构建多控相位翻转，以最大程度降低双比特门的数量和整体电路深度：

```isq
import std;

qbit q[3];
cbit c[3];

// 针对|111>目标的Oracle，标记目标态相位
procedure oracle() {
    // 使用Hadamard将控制相位转为控制X
    H(q[2]);
    Toffoli(q[0], q[1], q[2]);
    H(q[2]);
}

// 针对NISQ硬件优化的扩散算子
procedure diffusion() {
    // 步骤1: 应用Hadamard门
    for i in 0:3 {
        H(q[i]);
    }
    // 步骤2: 应用X门
    for i in 0:3 {
        X(q[i]);
    }
    // 步骤3: 实现条件相位翻转(等价于控制Z结构)
    H(q[2]);
    Toffoli(q[0], q[1], q[2]);
    H(q[2]);
    // 步骤4: 恢复X门
    for i in 0:3 {
        X(q[i]);
    }
    // 步骤5: 恢复Hadamard门
    for i in 0:3 {
        H(q[i]);
    }
}

procedure main() {
    // 初始化：构造均匀叠加态
    for i in 0:3 {
        H(q[i]);
    }

    // NISQ适应策略：考虑退相干影响，不使用理论上的2次迭代，而是截断为1次迭代
    oracle();
    diffusion();

    // 测量并输出结果
    for i in 0:3 {
        c[i] = M(q[i]);
    }
}
```

## isqQA/quantum_algorithms/117_optimization_variant

- task_id: `isqQA/quantum_algorithms/117_optimization_variant`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `optimization_variant`, `algorithm`, `振幅放大原理`
- source: `qa_pipeline`
- dataset_index: `4211`

### Prompt

量子振幅放大算法是量子计算中实现搜索加速的核心原理，但标准的Grover迭代要求我们必须精确知道目标解的比例，否则很容易出现“过度旋转”导致成功率大幅下降。请问为了克服这一缺陷以及适应更复杂的场景，振幅放大算法有哪些重要的优化改进版本或变体？

### Reference answer

<thought>
数学推导：
1. 标准振幅放大的局限性：假设初态为 $|\psi\rangle$，目标态为 $|\psi_{good}\rangle$。通过算子 $Q = -A S_0 A^\dagger S_\chi$ 进行迭代，成功概率为 $P(k) = \sin^2((2k+1)\theta)$。如果迭代次数 $k$ 选得不合适，概率会发生震荡。
2. 定点振幅放大：核心在于改变相位。将原本固定为 $\pi$ 的相位翻转算子 $S_\chi$ 和 $S_0$ 替换为可变角度的旋转 $R_\chi(\beta_k)$ 和 $R_0(\alpha_k)$。通过选择递减的序列，使得幅度收敛。
3. 无关振幅放大：在不知道具体子空间投影的情况下，利用 $Q = -U V^{-1} U V$ 进行放大，常用于哈密顿量模拟。

代码思路：
使用isQ语言构建一个带可变相位的振幅放大迭代。以寻找 $|11\rangle$ 为例。
常规的相位翻转使用 CZ 门（等效于控制-Z）。在变体中，我们需要受控-$R_z(\theta)$ 门。
受控-$R_z$ 可以分解为：CNOT, $R_z$, CNOT。
我们将展示一个含参的自定义振幅放大过程。
</thought>

量子振幅放大算法虽然强大，但标准版本在实际应用中存在明显的局限性。标准Grover算子 $Q = -A S_0 A^\dagger S_\chi$ 的每次迭代会将状态向量在二维子空间中旋转 $2\theta$ 的角度。如果不知道目标态的精确比例，我们很难确定最佳的迭代次数 $k$。一旦 $k$ 超过最优值，成功概率反而会像钟摆一样回落，这被称为“过度旋转”问题。为了解决这一问题并适应更广泛的量子算法需求，学术界提出了几种极其重要的变体：

1. **定点振幅放大**：
这是解决过度旋转最经典的方案（例如Yoder、Low和Chuang在2014年提出的方法）。在标准版本中，$S_\chi$ 和 $S_0$ 的相位翻转固定为 $\pi$。而在定点变体中，算法在第 $k$ 次迭代时使用动态的相位 $\phi_k$ 和 $\varphi_k$。通过精心设计的相位序列，可以使状态向量的振幅单调递增，最终成功概率被严格限制在一个非常接近100%的下界之上，无论迭代次数如何增加都不会下降。这种变体在容错量子计算中极为重要。

2. **无关振幅放大**：
在某些高级量子算法（如量子线性系统算法或哈密顿量模拟）中，我们无法显式构造出标准的预言机。OAA允许我们在不知道精确目标子空间的情况下进行振幅放大。它通常利用子空间的等距映射性质，直接对酉算子进行类似Grover的反射操作，从而实现算法步骤的平方级加速。

3. **自适应振幅放大**：
该变体通过量子计数等辅助手段，动态估计当前的成功概率，并自适应地决定何时停止迭代，或者在不同阶段采用不同的放大策略。

为了更直观地理解相位变体的实现原理，下面使用isQ语言展示一个带有自定义相位旋转的振幅放大迭代。我们将原本硬性的 $\pi$ 相位翻转（如CZ门）替换为带参数的受控旋转，这是构建定点放大算法的基础逻辑：

```isq
import std;

qbit q[2];
real theta = 3.14159/4; // 示例：使用 pi/4 而非标准 pi 的相位旋转

// 自定义受控相位旋转门
procedure ctrl_Rz(real angle, qbit c, qbit t) {
    CNOT(c, t);
    Rz(angle, t);
    CNOT(c, t);
}

procedure main() {
    // Step 1: 初始化叠加态
    H(q[0]);
    H(q[1]);
    
    // Step 2: 应用于自定义相位的 Oracle (替代标准的 S_chi)
    // 标准 S_chi 对应于 theta = pi 的 CZ 门
    // 这里使用变体角度
    ctrl_Rz(theta, q[0], q[1]);

    // Step 3: 扩散算子 (S_0 的变体)
    H(q[0]);
    H(q[1]);
    X(q[0]);
    X(q[1]);
    
    // 替换标准的 CZ 中心操作为受控相位旋转
    ctrl_Rz(theta, q[0], q[1]);
    
    X(q[0]);
    X(q[1]);
    H(q[0]);
    H(q[1]);
    
    // 测量查看状态
    M(q[0]);
    M(q[1]);
}
```
在这段isQ代码中，核心在于将相位翻转转化为了角度可调的受控 $R_z$ 门。在实际的定点算法中，外层会有一个循环控制变量 `theta` 不断变化（例如从大到小），从而使得搜索过程能够稳定收敛。这些优化变体极大拓宽了振幅放大在现代量子算法框架中的适用范围。

## isqTrain/2839

- task_id: `isqTrain/2839`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_syntax_multi_register`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4078`

### Prompt

There's an error in this quantum circuit implementation. Fix it:

```isq
import std;
qbit q[1];
// Prepare (|0> + e^(i*pi/4)|1>)/sqrt(2) state
procedure main() {
    // H(q[0]); // BUG: missing Hadamard
    T(q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **What the bug is:** The Hadamard gate `H(q[0])` is commented out on line 6. Without it, the qubit remains in the initial `|0>` state, and the subsequent `T` gate only applies a global phase, failing to create the required superposition state.
2. **What the fix is:** Uncomment the `H(q[0]);` line so that the Hadamard gate is applied to the qubit before the `T` gate.
3. **Brief state evolution:**
   - Initial state: `|0>`
   - Apply `H`: Transitions to the `|+>` state, `( |0> + |1> ) / sqrt(2)`
   - Apply `T`: Applies a `pi/4` phase shift to the `|1>` component, resulting in `( |0> + e^(i*pi/4)|1> ) / sqrt(2)`

## isqTrain/2039

- task_id: `isqTrain/2039`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `basis_change`, `entanglement`, `hamiltonian_simulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1116`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;
qbit q[2];
procedure main() {
    X(q[0]);
    H(q[0]); H(q[1]);
    CNOT(q[0], q[1]);
    Rz(1.57079632679490, q[1]);
    CNOT(q[0], q[1]);
    H(q[0]); H(q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a step-by-step analysis of a specific isQ quantum program, ending with the predicted measurement probability distribution.

2.  **Analyze the Circuit:**
    *   Initial state: $|00\rangle$
    *   `X(q[0])`: $|10\rangle$
    *   `H(q[0]); H(q[1])`: $H|1\rangle \otimes H|0\rangle = |-\rangle \otimes |+\rangle = \frac{1}{2}(|0\rangle - |1\rangle) \otimes (|0\rangle + |1\rangle) = \frac{1}{2}(|00\rangle + |01\rangle - |10\rangle - |11\rangle)$.
    *   `CNOT(q[0], q[1])`: CNOT with control $q_0$, target $q_1$.
        Wait, let's look at the standard basis. The state is an equal superposition. Let's track it in the Z basis.
        Actually, $|+\rangle |+\rangle$ transformed by CNOT is $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle) \otimes |+\rangle$? No.
        Let's just compute it directly:
        $CNOT(|-\rangle|+\rangle)$. Let $c=q_0, t=q_1$.
        $|00\rangle \to |00\rangle$
        $|01\rangle \to |01\rangle$
        $|10\rangle \to |11\rangle$
        $|11\rangle \to |10\rangle$
        So: $\frac{1}{2}(|00\rangle + |01\rangle - |11\rangle - |10\rangle) = \frac{1}{2}(|00\rangle + |01\rangle - |10\rangle - |11\rangle)$.
        Wait, the state is actually $|-\rangle \otimes |-\rangle$! Let's check: $|-\rangle|-\rangle = \frac{1}{2}(|0\rangle - |1\rangle)(|0\rangle - |1\rangle) = \frac{1}{2}(|00\rangle - |01\rangle - |10\rangle + |11\rangle)$.
        Ah. Let me re-evaluate $|-\rangle|+\rangle$ with CNOT:
        $|-\rangle|+\rangle = \frac{1}{2}(|00\rangle + |01\rangle - |10\rangle - |11\rangle)$.
        Apply CNOT(0,1):
        $|00\rangle \to |00\rangle$
        $|01\rangle \to |01\rangle$
        $|10\rangle \to |11\rangle$
        $|11\rangle \to |10\rangle$
        So it becomes $\frac{1}{2}(|00\rangle + |01\rangle - |11\rangle - |10\rangle) = -\frac{1}{2}(|10\rangle + |11\rangle - |00\rangle - |01\rangle)$.
        Wait, this is $- |-\rangle|-\rangle$.
        Let's check CNOT in the X basis. CNOT applies $X$ on target if control is $|1\rangle$.
        Control in $|+\rangle$, target in $|+\rangle$ -> CNOT -> $|+\rangle|+\rangle$.
        Control in $|+\rangle$, target in $|-\rangle$ -> CNOT -> $|-\rangle|-\rangle$.
        Control in $|-\rangle$, target in $|+\rangle$ -> CNOT -> $|-\rangle|+\rangle$.
        Control in $|-\rangle$, target in $|-\rangle$ -> CNOT -> $|+\rangle|-\rangle$.
        So $CNOT(|-\rangle|+\rangle) = |-\rangle|+\rangle$.
        Let's re-verify my manual expansion.
        $CNOT(c,t) = |0\rangle\langle0| \otimes I + |1\rangle\langle1| \otimes X$.
        State is $|-\rangle|+\rangle = \frac{1}{2}(|00\rangle + |01\rangle - |10\rangle - |11\rangle)$.
        Apply CNOT:
        $|0\rangle\langle0| \otimes I (|00\rangle + |01\rangle) = |00\rangle + |01\rangle$
        $|1\rangle\langle1| \otimes X (-|10\rangle - |11\rangle) = -|11\rangle - |10\rangle

### Reference answer

{'predicted_probs': {'01': 0.5, '10': 0.5}, 'explanation': 'XX evolution on |10>: generates P(|01>)=0.5, P(|10>)=0.5.'}

## isqTrain/4367

- task_id: `isqTrain/4367`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1548`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;

// Superdense coding: transmit message '11'
qbit q[2];

procedure main() {
    // Create Bell pair between Alice and Bob
    H(q[0]);
    CNOT(q[0], q[1]);
    // Alice encodes '11': apply Z then X
    // Z flips the phase, X flips the bit
    Z(q[0]);
    X(q[0]);
    // Bob decodes by reversing Bell circuit
    CNOT(q[0], q[1]);
    H(q[0]);
    // Measurement yields the transmitted bits
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants an analysis of the provided isQ program, predicting the measurement outcome probability distribution. The output must follow specific formatting constraints (start with "## Circuit Analysis", max 15 lines, use Dirac notation, output ONLY the analysis, end with the probability distribution).

2.  **Analyze the Code:**
    *   Initialization: `q[0]` = |0>, `q[1]` = |0>. Initial state: |00>.
    *   `H(q[0])`: Apply Hadamard to q[0]. State becomes (|00> + |10>) / sqrt(2).
    *   `CNOT(q[0], q[1])`: Control q[0], target q[1]. State becomes (|00> + |11>) / sqrt(2) = |Phi+>.
    *   `Z(q[0])`: Apply Z to q[0]. State becomes (|00> - |11>) / sqrt(2) = |Phi->.
    *   `X(q[0])`: Apply X to q[0]. State becomes (|10> - |01>) / sqrt(2) = |Psi->.
    *   `CNOT(q[0], q[1])`: State becomes |11> - |00> ... wait, let's trace carefully.
        *   State before CNOT: (|10> - |01>) / sqrt(2).
        *   CNOT(0, 1): |10> -> |11>, |01> -> |01>. State becomes (|11> - |01>) / sqrt(2) = (|1> - |0>)|1> / sqrt(2) = (-|0> + |1>)|1> / sqrt(2).
        *   Actually, let's trace it mathematically:
            CNOT |10> = |11>
            CNOT |01> = |01>
            So CNOT (|10> - |01>) / sqrt(2) = (|11> - |01>) / sqrt(2).
    *   `H(q[0])`: Apply H to q[0].
        *   H|0> = |+>, H|1> = |->
        *   State becomes (|->|1> - |+>|1>) ... wait.
        *   Let's apply H to (-|0> + |1>)/sqrt(2). This is exactly H X |0> ... wait, X|0> = |1>. Z X|0> = Z|1> = -|1>. H Z X|0> = H|-1> wait.
        *   Let's do standard superdense coding decode:
            Message '11': Apply ZX. Z is applied first in code? "Z(q[0]); X(q[0]);" Yes.
            Bell state creation: H CNOT -> |00>+|11>.
            Apply Z: |00> - |11>.
            Apply X: |10> - |01>. (This is |Psi->).
            Decode: CNOT.
            (|10> - |01>) -> CNOT(0,1) -> |11> - |01>.
            Apply H: H(-|0> + |1>) = -|+> + |-> = (-1/sqrt(2))(|0>+|1>) + (1/sqrt(2))(|0>-|1>) = (-2/sqrt(2))|1> = -sqrt(2)|1>.
            So q[0] becomes |1>, q[1] remains |1>. State is -|11>.
            This should decode to '11'.
    *   **Wait, there's extra gates in the code:**
        *   `H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0`
        *   Let's see: state is -|11>.
        *   Apply H(q[0]): -|1> -> |-> = (|0>-|1>)/sqrt(2). State is -|1>|1> -> (-1/sqrt(2))(|0> - |1>)|1> = (-|01> + |11>)/sqrt(2).
        *   Apply Z(q[0]): (-|01> - |11>)/sqrt(2).
        *   Apply H(q[0]): (-1/sqrt(2)) ( (|0>+|1>)|1> + (|0>-|1>)|1> ) = (-1/sqrt(2)) ( 2|0>|1> ) = -sqrt(2)|01>.
        *   So the state becomes |01> (up to global phase).
    *   Let's re-

### Reference answer

{'predicted_probs': {'01': 1.0}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|01>) = 1.0000.'}

## isqTrain/2846

- task_id: `isqTrain/2846`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5736`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
qbit q[2];
procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    X(q[1]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations applied:** Hadamard on q[0] (H), CNOT with control q[0] and target q[1], and Pauli-X on q[1] (X).
2. **State evolution:**
   - Initialize to |00>.
   - `H(q[0])` creates superposition: (1/√2)(|00> + |10>).
   - `CNOT(q[0], q[1])` entangles the qubits: (1/√2)(|00> + |11>).
   - `X(q[1])` flips the second qubit: (1/√2)(|01> + |10>).
3. **Final state before measurement:** (1/√2)(|01> + |10>). 
4. **Probability distribution:** The squared amplitudes for the |01> and |10> states are both |1/√2|² = 0.5. The |00> and

### Reference answer

{'predicted_probs': {'01': 0.5, '10': 0.5}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/3456

- task_id: `isqTrain/3456`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `interference`, `ancilla_usage`
- source: `isq_train_cot`
- dataset_index: `3612`

### Prompt

Write an isQ program that the Bernstein-Vazirani algorithm in isQ to find the secret string s=101 (3 bits).

The algorithm finds s in f(x) = s.x mod 2 with a single query.

Circuit:
1. Prepare ancilla in |->: X, H
2. H on all input qubits
3. Oracle: CNOT from q[i] to ancilla for each bit i where s[i]=1
4. H on all input qubits
5. Measure input qubits to reveal s

Declare 3 input qubits and 1 ancilla. Measure input qubits.
Expected: |101>.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Find secret string s=101 using Bernstein-Vazirani with a single oracle query.

**Qubits:** 3 input qubits q[0], q[1], q[2] and 1 ancilla anc[0]. Measure q[0..2].

**State evolution:**
- **Initialize:** |0000⟩
- **X, H on ancilla:** |000⟩(|0⟩-|1⟩)/√2 = |000⟩|−⟩
- **H on inputs:** (1/√8)Σₓ|x⟩|−⟩ where x ∈ {000,...,111}
- **Oracle (CNOT q[0], q[2] → anc):** Phase kickback applies (−1)^(s·x): (1/√8)Σₓ(−1)^(s·x)|x⟩|−⟩ where s=101
- **H on inputs:** |101⟩|−⟩ (Hadamard transforms phase encoding to computational basis)

**Measurement:** Input register is |101⟩ with certainty, revealing the secret string s=101.

## isqTrain/3019

- task_id: `isqTrain/3019`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3493`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
qbit q[3];
procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    X(q[2]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Task:** Explain the step-by-step evolution of an isQ quantum circuit, determine the final state before measurement, and output the probability distribution.
    *   **Input Program:** A simple 3-qubit circuit: `H(q[0])`, `CNOT(q[0], q[1])`, `CNOT(q[1], q[2])`, `X(q[2])`.
    *   **Constraints:** Use Dirac notation, be concise (3-15 lines), output ONLY the analysis starting with "## Circuit Analysis", end with the predicted probability distribution.
    *   **predicted output:** Probability distribution {'001': 0.5, '110': 0.5}.

2.  **Trace the Circuit:**
    *   Initial state: $|000\rangle$
    *   `H(q[0])`: $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes |00\rangle = \frac{1}{\sqrt{2}}(|000\rangle + |100\rangle)$
    *   `CNOT(q[0], q[1])`: Control q[0], target q[1]. Flips q[1] when q[0] is 1. State becomes $\frac{1}{\sqrt{2}}(|000\rangle + |110\rangle)$
    *   `CNOT(q[1], q[2])`: Control q[1], target q[2]. Flips q[2] when q[1] is 1. State becomes $\frac{1}{\sqrt{2}}(|000\rangle + |111\rangle)$
    *   `X(q[2])`: Flips q[2]. $|0\rangle \rightarrow |1\rangle$ and $|1\rangle \rightarrow |0\rangle$. State becomes $\frac{1}{\sqrt{2}}(|001\rangle + |110\rangle)$

3.  **Calculate Probabilities:**
    *   State: $\frac{1}{\sqrt{2}}(|001\rangle + |110\rangle)$
    *   $P(001) = |\frac{1}{\sqrt{2}}|^2 = 0.5$
    *   $P(110) = |\frac{1}{\sqrt{2}}|^2 = 0.5$

4.  **Draft the Analysis:**
    *   Start with `## Circuit Analysis`
    *   List gates: H(0), CNOT(0,1), CNOT(1,2), X(2).
    *   State evolution:
        *   Initial: $|000\rangle$
        *   After H(0): $\frac{1}{\sqrt{2}}(|000\rangle + |100\rangle)$
        *   After CNOT(0,1): $\frac{1}{\sqrt{2}}(|000\rangle + |110\rangle)$ (entanglement between q0, q1)
        *   After CNOT(1,2): $\frac{1}{\sqrt{2}}(|000\rangle + |111\rangle)$ (GHZ state)
        *   After X(2): $\frac{1}{\sqrt{2}}(|001\rangle + |110\rangle)$
    *   Probabilities: 50% for 001, 50% for 110.

5.  **Refine to meet conciseness and formatting:**
    ## Circuit Analysis
    1. Operations: H(q[0]), CNOT(q[0], q[1]), CNOT(q[1], q[2]), X(q[2]).
    2. State Evolution (initial |000>):
       - H(q[0]) creates superposition: (1/√2)(|000> + |100>)
       - CNOT(q[0], q[1]) entangles q0, q1: (1/√2)(|000> + |110>)
       - CNOT(q[1], q[2]) propagates to q2 (GHZ state): (1/√2)(|000> + |111>)
       - X(q[2]) flips the last qubit: (1/√2)(|001> + |110>)
    3. Final State: (1/√2)(|001> + |110>)
    4. Probabilities: Measuring yields equal probability for states |001> and |110>.
    Predicted probability distribution: {'001': 0.5, '110': 0.5}

6.  **Final check against rules:**
    *   Only analysis starting with `## Circuit Analysis`? Yes.
    *   no code blocks? Yes.
    *

### Reference answer

{'predicted_probs': {'001': 0.5, '110': 0.5}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/864

- task_id: `isqTrain/864`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `808`

### Prompt

Implement a quantum circuit in isQ: implements a variant of the quantum_logic_gate pattern using q[3] -> q[4]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

Alright, let me understand the problem:

1. I need to implement a variant of the quantum_logic_gate pattern using q[3] -> q[4]
2. The circuit should use an expanded qubit register compared to the base version

Let me analyze The implementation:
- It uses 4 qubits: q[0], q[1], q[2], q[3]
- q[0] is initialized to |1> (via X gate), q[1] to |0>
- It implements De Morgan's law: OR(a,b) = NOT(NOT(a) AND NOT(b))
- Steps:
  1. Negate inputs: X(q[0]), X(q[1])
  2. Toffoli computes AND of negated inputs: ctrl ctrl X(q[0], q[1], q[2])
  3. Restore original inputs: X(q[0]), X(q[1])
  4. Negate the AND result to get OR: X(q[2])
- All qubits are measured

The expected measurement is |1010> with probability 1.0:
- q[0] measured first -> highest bit -> 1
- q[1] measured second -> 1
- q[2] measured third -> 0
- q[3] measured fourth -> lowest bit -> 0

Wait, let me trace through:
- Initial: |0000>
- After X(q[0]): |1000>
- After X(q[0]): |0000> (negates back to 0)
- After X(q[1]): |0100>
- After Toffoli(q[0], q[1], q[2]): |0100> (controls are 0 and 1, not both 1, so target unchanged)
- After X(q[0]): |1100>
- After X(q[1]): |1000>
- After X(q[2]): |1010>

Hmm, that doesn't match. Let me re-analyze the output.

Expected: {|1010>: 1.0}

In bitstring format with 4 qubits, |1010> means:
- qubit 3 (or highest index) = 0
- qubit 2 = 1
- qubit 1 = 0
- qubit 0 (or lowest index) = 1

But wait, the problem says "earlier measured qubit = higher bit". So if we measure q[0], q[1], q[2], q[3] in that order:
- q[0] = bit 3 (highest)
- q[1] = bit 2
- q[2] = bit 1
- q[3] = bit 0 (lowest)

So |1010> means:
- q[0] = 1
- q[1] = 0
- q[2] = 1
- q[3] = 0

Let me trace again:
- Initial: |0000>
- X(q[0]): |1000> (q[0]=1)
- X(q[0]): |0000> (q[0]=0)
- X(q[1]): |0100> (q[1]=1)
- Toffoli(q[0], q[1], q[2]): Since q[0]=0, q[1]=1, not both 1, so target unchanged
  State: |0100>
- X(q[0]): |1100> (q[0]=1)
- X(q[1]): |1000> (q[1]=0)
- X(q[2]): |1010> (q[2]=1)

Final state: q[0]=1, q[1]=0, q[2]=1, q[3]=0

In bitstring with q[0] as highest bit: |1010>

That matches! Now the task says "using q[3] -> q[4]". I think this means I should adapt the circuit to use qubits q[3] and q[4] (and maybe more) instead of q[0] and q[1].

Actually, re-reading: "The circuit should use an expanded qubit register compared to the base version."

The base version uses 4 qubits. I should expand this. Perhaps use 5 qubits and shift the operations to use q[3] and q[4]?

Let me think about this differently. The task says "using q[3] -> q[4]". This might mean:
- Use q[3] and q[4] as the input qubits (instead of q[0] and q[1])
- Need at least 5 qubits total

So I'll modify the circuit:
- 5 qubits: q[0]
